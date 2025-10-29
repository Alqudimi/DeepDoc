"""Background task manager for async documentation generation."""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """Represents a documentation generation task."""
    
    task_id: str
    project_path: str
    config_overrides: Dict
    status: TaskStatus
    progress: int
    current_step: Optional[str]
    message: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error: Optional[str]
    result: Optional[Dict]
    
    def __init__(self, task_id: str, project_path: str, config_overrides: Optional[Dict] = None):
        self.task_id = task_id
        self.project_path = project_path
        self.config_overrides = config_overrides or {}
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.current_step = None
        self.message = "Task created"
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.result = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "result": self.result
        }


class TaskManager:
    """Manages background documentation generation tasks."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self._lock = asyncio.Lock()
    
    def create_task(self, project_path: str, config_overrides: Optional[Dict] = None) -> str:
        """Create a new task and return its ID."""
        task_id = str(uuid.uuid4())
        task = Task(task_id, project_path, config_overrides)
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id} for project: {project_path}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Task]:
        """Get all tasks."""
        return self.tasks.copy()
    
    async def update_task_status(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        current_step: Optional[str] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        result: Optional[Dict] = None
    ):
        """Update task status and metadata."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found")
                return
            
            if status:
                task.status = status
                if status == TaskStatus.RUNNING and not task.started_at:
                    task.started_at = datetime.now()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.completed_at = datetime.now()
            
            if progress is not None:
                task.progress = progress
            if current_step:
                task.current_step = current_step
            if message:
                task.message = message
            if error:
                task.error = error
            if result:
                task.result = result
            
            logger.debug(f"Task {task_id} updated: {task.status} - {task.message}")
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Deleted task {task_id}")
            return True
        return False
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove tasks older than specified hours."""
        now = datetime.now()
        to_delete = []
        
        for task_id, task in self.tasks.items():
            age = now - task.created_at
            if age.total_seconds() > max_age_hours * 3600:
                to_delete.append(task_id)
        
        for task_id in to_delete:
            self.delete_task(task_id)
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} old tasks")


task_manager = TaskManager()
