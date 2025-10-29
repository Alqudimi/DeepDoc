"""Configuration management for the FastAPI server."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from ...docgen.core.config import Config

logger = logging.getLogger(__name__)

_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global _config_instance
    
    if _config_instance is None:
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        if os.path.exists(config_path):
            _config_instance = Config(config_path)
            logger.info(f"Loaded configuration from {config_path}")
        else:
            _config_instance = Config()
            logger.info("Using default configuration")
    
    return _config_instance


def update_config(updates: Dict[str, Any], save: bool = False) -> Config:
    """Update configuration with new values."""
    config = get_config()
    
    def deep_update(base: dict, updates: dict):
        """Recursively update nested dictionary."""
        for key, value in updates.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                deep_update(base[key], value)
            else:
                base[key] = value
    
    deep_update(config.config, updates)
    
    if save:
        save_path = os.getenv("CONFIG_PATH", "config.yaml")
        config.save(save_path)
        logger.info(f"Configuration saved to {save_path}")
    
    return config


def get_server_config() -> Dict[str, Any]:
    """Get server-specific configuration."""
    return {
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "5000")),
        "reload": os.getenv("API_RELOAD", "true").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "info").lower(),
        "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
        "upload_dir": os.getenv("UPLOAD_DIR", "uploads"),
        "max_upload_size_mb": int(os.getenv("MAX_UPLOAD_SIZE_MB", "100")),
    }
