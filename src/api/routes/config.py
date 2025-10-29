"""Configuration management endpoint."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..models.requests import ConfigUpdate
from ..models.responses import ConfigResponse
from ..core.config_manager import get_config, update_config

router = APIRouter(prefix="/config", tags=["config"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ConfigResponse)
async def get_configuration():
    """
    Get the current configuration.
    
    Returns the complete configuration object including:
    - Ollama settings
    - Documentation preferences
    - Scanning options
    - Output settings
    - Advanced features
    """
    config = get_config()
    
    return ConfigResponse(
        config=config.config,
        message="Current configuration retrieved"
    )


@router.put("", response_model=ConfigResponse)
async def update_configuration(config_update: ConfigUpdate):
    """
    Update the configuration.
    
    Provide a partial or complete configuration object to update.
    Only provided fields will be updated; others remain unchanged.
    
    Example:
    ```json
    {
        "config": {
            "ollama": {
                "model": "codellama"
            },
            "documentation": {
                "style": "casual"
            }
        }
    }
    ```
    """
    try:
        updated_config = update_config(config_update.config, save=False)
        
        return ConfigResponse(
            config=updated_config.config,
            message="Configuration updated successfully"
        )
    except Exception as e:
        logger.error(f"Failed to update configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Configuration update failed: {e}")


@router.post("/reset", response_model=ConfigResponse)
async def reset_configuration():
    """
    Reset configuration to defaults.
    
    This will reset all settings to their default values.
    """
    from ...docgen.core.config import Config
    
    global _config_instance
    _config_instance = Config()
    
    return ConfigResponse(
        config=_config_instance.config,
        message="Configuration reset to defaults"
    )
