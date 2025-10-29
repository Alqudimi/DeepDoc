"""Status endpoint for task monitoring."""

from fastapi import APIRouter, HTTPException
from typing import Dict
import logging

from ..models.responses import StatusResponse, TaskStatus
from ..core.task_manager import task_manager

router = APIRouter(prefix="/status", tags=["status"])
logger = logging.getLogger(__name__)


@router.get("/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a documentation generation task.
    
    - **task_id**: The task identifier returned from /analyze
    """
    task = task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return StatusResponse(
        task_id=task.task_id,
        status=TaskStatus(task.status.value),
        progress=task.progress,
        current_step=task.current_step,
        message=task.message,
        started_at=task.started_at,
        completed_at=task.completed_at,
        error=task.error,
        result=task.result
    )


@router.get("", response_model=Dict[str, StatusResponse])
async def get_all_tasks():
    """
    Get the status of all tasks.
    
    Returns a dictionary mapping task_id to StatusResponse.
    """
    tasks = task_manager.get_all_tasks()
    
    return {
        task_id: StatusResponse(
            task_id=task.task_id,
            status=TaskStatus(task.status.value),
            progress=task.progress,
            current_step=task.current_step,
            message=task.message,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error=task.error,
            result=task.result
        )
        for task_id, task in tasks.items()
    }
