"""Analyze endpoint for documentation generation."""

import os
import tempfile
import shutil
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from typing import Optional
import logging
import json

from ..models.responses import AnalyzeResponse, TaskStatus, ErrorResponse
from ..core.task_manager import task_manager
from ..core.config_manager import get_config
from ..services.documentation_service import DocumentationService

router = APIRouter(prefix="/analyze", tags=["analyze"])
logger = logging.getLogger(__name__)

doc_service = DocumentationService(task_manager)


@router.post("", response_model=AnalyzeResponse)
async def analyze_project(
    background_tasks: BackgroundTasks,
    project_path: Optional[str] = Form(None),
    zip_file: Optional[UploadFile] = File(None),
    config_overrides: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None),
    overwrite: bool = Form(False)
):
    """
    Analyze a project and generate documentation.
    
    Either provide a local project_path OR upload a zip_file, not both.
    
    - **project_path**: Local path to project directory
    - **zip_file**: ZIP file containing the project
    - **config_overrides**: JSON string of configuration overrides
    - **model_name**: Ollama model to use (e.g., 'llama3.2', 'codellama')
    - **overwrite**: Whether to overwrite existing documentation files
    """
    try:
        if not project_path and not zip_file:
            raise HTTPException(
                status_code=400,
                detail="Either project_path or zip_file must be provided"
            )
        
        if project_path and zip_file:
            raise HTTPException(
                status_code=400,
                detail="Provide either project_path or zip_file, not both"
            )
        
        config = get_config()
        
        if config_overrides:
            try:
                overrides = json.loads(config_overrides)
                for key, value in overrides.items():
                    if key in config.config:
                        config.config[key].update(value)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid config_overrides JSON")
        
        actual_project_path: str = ""
        temp_dir: Optional[str] = None
        
        if zip_file:
            upload_dir = os.getenv("UPLOAD_DIR", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            
            temp_zip = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".zip",
                dir=upload_dir
            )
            
            try:
                content = await zip_file.read()
                temp_zip.write(content)
                temp_zip.close()
                
                temp_dir = tempfile.mkdtemp(dir=upload_dir)
                actual_project_path = await doc_service.extract_zip(temp_zip.name, temp_dir)
                
                os.unlink(temp_zip.name)
                
            except Exception as e:
                if os.path.exists(temp_zip.name):
                    os.unlink(temp_zip.name)
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                raise HTTPException(status_code=400, detail=f"Failed to process ZIP file: {e}")
        else:
            if not project_path:
                raise HTTPException(status_code=400, detail="project_path is required")
            actual_project_path = project_path
            if not os.path.exists(actual_project_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Project path not found: {actual_project_path}"
                )
            if not os.path.isdir(actual_project_path):
                raise HTTPException(
                    status_code=400,
                    detail=f"Project path is not a directory: {actual_project_path}"
                )
        
        task_id = task_manager.create_task(actual_project_path, config.config)
        
        background_tasks.add_task(
            doc_service.generate_documentation,
            task_id,
            actual_project_path,
            config,
            model_name,
            overwrite
        )
        
        if temp_dir:
            background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
        
        logger.info(f"Started documentation generation task {task_id} for {actual_project_path}")
        
        return AnalyzeResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="Documentation generation started",
            created_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
