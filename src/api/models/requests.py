"""Request models for the FastAPI server."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request model for project analysis."""
    
    project_path: Optional[str] = Field(
        None,
        description="Local path to project directory. Required if not uploading a ZIP file."
    )
    config_overrides: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration overrides for this analysis"
    )
    model_name: Optional[str] = Field(
        None,
        description="Ollama model to use (overrides config)"
    )
    overwrite: bool = Field(
        False,
        description="Overwrite existing documentation files"
    )


class ConfigUpdate(BaseModel):
    """Request model for configuration updates."""
    
    config: Dict[str, Any] = Field(
        ...,
        description="Configuration data to update"
    )
