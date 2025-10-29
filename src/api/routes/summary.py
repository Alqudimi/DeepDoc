"""Project summary endpoint."""

from fastapi import APIRouter, HTTPException
import logging

from ..models.responses import SummaryResponse
from ..core.task_manager import task_manager, TaskStatus
from ..services.documentation_service import DocumentationService

router = APIRouter(prefix="/summary", tags=["summary"])
logger = logging.getLogger(__name__)

doc_service = DocumentationService(task_manager)


@router.get("/{task_id}", response_model=SummaryResponse)
async def get_project_summary(task_id: str):
    """
    Get the AI-generated project summary for a completed task.
    
    - **task_id**: The task identifier
    """
    task = task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Task {task_id} has not completed yet. Status: {task.status.value}"
        )
    
    if not task.result:
        raise HTTPException(
            status_code=500,
            detail="Task completed but no result data available"
        )
    
    project_path = task.result.get('project_path')
    if not project_path:
        raise HTTPException(
            status_code=500,
            detail="Task result missing project_path"
        )
    analysis = task.result.get('analysis', {})
    
    summary_text = doc_service.get_project_summary(project_path, task_id)
    
    if not summary_text:
        summary_text = task.result.get('summary', 'No summary available')
    
    return SummaryResponse(
        summary=summary_text,
        task_id=task_id,
        project_name=analysis.get('name'),
        languages=analysis.get('languages'),
        frameworks=analysis.get('frameworks')
    )
