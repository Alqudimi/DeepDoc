"""Documentation generation service that reuses CLI logic."""

import asyncio
import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
import logging

from ...docgen.core.config import Config
from ...docgen.core.scanner import ProjectScanner
from ...docgen.core.llm_client import LLMClient
from ...docgen.core.workflow import DocumentationWorkflow
from ...docgen.generators.doc_writer import DocumentationWriter
from ..core.task_manager import TaskManager, TaskStatus

logger = logging.getLogger(__name__)


class DocumentationService:
    """Service for generating documentation asynchronously."""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
    
    async def generate_documentation(
        self,
        task_id: str,
        project_path: str,
        config: Config,
        model_name: Optional[str] = None,
        overwrite: bool = False
    ):
        """Generate documentation asynchronously."""
        try:
            await self.task_manager.update_task_status(
                task_id,
                status=TaskStatus.RUNNING,
                progress=0,
                current_step="Initializing",
                message="Starting documentation generation"
            )
            
            if model_name:
                config.config['ollama']['model'] = model_name
            
            if overwrite:
                config.config['output']['overwrite_existing'] = True
            
            await self.task_manager.update_task_status(
                task_id,
                progress=10,
                current_step="Scanning project",
                message="Analyzing project structure"
            )
            
            scanner = ProjectScanner(config)
            analysis = await asyncio.to_thread(scanner.scan_project, project_path)
            
            await self.task_manager.update_task_status(
                task_id,
                progress=30,
                current_step="Initializing AI",
                message="Connecting to Ollama"
            )
            
            llm_client = LLMClient(config)
            
            await self.task_manager.update_task_status(
                task_id,
                progress=40,
                current_step="Generating documentation",
                message="Running AI workflow"
            )
            
            workflow = DocumentationWorkflow(config, llm_client, scanner)
            state = await asyncio.to_thread(workflow.run, project_path)
            
            await self.task_manager.update_task_status(
                task_id,
                progress=80,
                current_step="Writing files",
                message="Saving documentation to disk"
            )
            
            doc_writer = DocumentationWriter(config)
            written_files = doc_writer.write_documentation(project_path, state)
            
            result = {
                "project_path": project_path,
                "analysis": {
                    "name": analysis.get('name'),
                    "total_files": analysis.get('total_files'),
                    "total_lines": analysis.get('total_lines'),
                    "languages": list(analysis.get('languages', {}).keys()),
                    "frameworks": analysis.get('frameworks', [])
                },
                "written_files": written_files,
                "summary": state.get('summary')
            }
            
            await self.task_manager.update_task_status(
                task_id,
                status=TaskStatus.COMPLETED,
                progress=100,
                current_step="Completed",
                message="Documentation generated successfully",
                result=result
            )
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Task {task_id} failed: {error_msg}", exc_info=True)
            
            await self.task_manager.update_task_status(
                task_id,
                status=TaskStatus.FAILED,
                current_step="Failed",
                message="Documentation generation failed",
                error=error_msg
            )
    
    async def extract_zip(self, zip_path: str, extract_to: str) -> str:
        """Extract ZIP file and return the project directory."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            extracted_items = os.listdir(extract_to)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(extract_to, extracted_items[0])):
                return os.path.join(extract_to, extracted_items[0])
            
            return extract_to
            
        except Exception as e:
            logger.error(f"Failed to extract ZIP: {e}")
            raise ValueError(f"Invalid ZIP file: {e}")
    
    def get_documentation_files(self, project_path: str, task_id: Optional[str] = None) -> Dict[str, str]:
        """Read generated documentation files."""
        docs = {}
        project_root = Path(project_path)
        
        doc_files = [
            "README.md",
            "SUMMARY.md",
            "docs/ARCHITECTURE.md",
            "docs/API.md",
            "docs/CONTRIBUTING.md",
            "docs/DEPENDENCIES.md"
        ]
        
        for doc_file in doc_files:
            file_path = project_root / doc_file
            if file_path.exists():
                try:
                    docs[doc_file] = file_path.read_text(encoding='utf-8')
                except Exception as e:
                    logger.warning(f"Failed to read {doc_file}: {e}")
        
        return docs
    
    def get_project_summary(self, project_path: str, task_id: Optional[str] = None) -> Optional[str]:
        """Get the generated project summary."""
        summary_path = Path(project_path) / "SUMMARY.md"
        
        if summary_path.exists():
            try:
                content = summary_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        return line.strip()
                
                return content.strip()
            except Exception as e:
                logger.warning(f"Failed to read summary: {e}")
        
        return None
