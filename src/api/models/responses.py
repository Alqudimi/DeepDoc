"""Response models for the FastAPI server."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalyzeResponse(BaseModel):
    """Response model for analysis endpoint."""
    
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Task creation timestamp")


class StatusResponse(BaseModel):
    """Response model for status endpoint."""
    
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    progress: Optional[int] = Field(None, description="Progress percentage (0-100)")
    current_step: Optional[str] = Field(None, description="Current processing step")
    message: Optional[str] = Field(None, description="Status message")
    started_at: Optional[datetime] = Field(None, description="Task start time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")
    error: Optional[str] = Field(None, description="Error message if failed")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result data")


class ConfigResponse(BaseModel):
    """Response model for config endpoint."""
    
    config: Dict[str, Any] = Field(..., description="Current configuration")
    message: str = Field(..., description="Response message")


class SummaryResponse(BaseModel):
    """Response model for summary endpoint."""
    
    summary: Optional[str] = Field(None, description="Project summary text")
    task_id: Optional[str] = Field(None, description="Associated task ID")
    project_name: Optional[str] = Field(None, description="Project name")
    languages: Optional[List[str]] = Field(None, description="Detected languages")
    frameworks: Optional[List[str]] = Field(None, description="Detected frameworks")


class DocsResponse(BaseModel):
    """Response model for docs endpoint."""
    
    documentation: Dict[str, str] = Field(
        ...,
        description="Documentation files (filename -> content)"
    )
    format: str = Field("markdown", description="Documentation format")
    task_id: Optional[str] = Field(None, description="Associated task ID")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    task_id: Optional[str] = Field(None, description="Associated task ID if applicable")
