"""Documentation retrieval endpoint."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from ..models.responses import DocsResponse
from ..core.task_manager import task_manager, TaskStatus
from ..services.documentation_service import DocumentationService

router = APIRouter(prefix="/docs", tags=["docs"])
logger = logging.getLogger(__name__)

doc_service = DocumentationService(task_manager)


@router.get("/{task_id}", response_model=DocsResponse)
async def get_documentation(
    task_id: str,
    format: str = Query("markdown", description="Documentation format (currently only 'markdown' supported)")
):
    """
    Retrieve generated documentation for a completed task.
    
    - **task_id**: The task identifier
    - **format**: Output format (currently only 'markdown' supported)
    """
    task = task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Task {task_id} has not completed yet. Status: {task.status.value}"
        )
    
    if not task.result or 'project_path' not in task.result:
        raise HTTPException(
            status_code=500,
            detail="Task completed but no result data available"
        )
    
    project_path = task.result['project_path']
    docs = doc_service.get_documentation_files(project_path, task_id)
    
    if not docs:
        raise HTTPException(
            status_code=404,
            detail="No documentation files found for this task"
        )
    
    return DocsResponse(
        documentation=docs,
        format=format,
        task_id=task_id
    )
