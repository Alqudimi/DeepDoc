"""Configuration management for the documentation generator."""

import os
import yaml
import copy
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the documentation generator."""
    
    DEFAULT_CONFIG = {
        "ollama": {
            "base_url": "http://localhost:11434",
            "model": "llama3.2",
            "temperature": 0.3,
            "timeout": 120
        },
        "documentation": {
            "style": "professional",
            "tone": "clear",
            "verbosity": "detailed",
            "include_emojis": True,
            "include_badges": True,
            "include_table_of_contents": True
        },
        "scanning": {
            "max_file_size_mb": 5,
            "max_depth": 10,
            "follow_symlinks": False,
            "ignore_patterns": [
                "*.log", "*.tmp", "*.cache",
                ".git/", ".svn/", "node_modules/",
                "__pycache__/", "venv/", ".venv/",
                "dist/", "build/", "target/",
                ".next/", ".nuxt/", "coverage/", ".pytest_cache/"
            ],
            "code_extensions": [
                ".py", ".js", ".ts", ".jsx", ".tsx",
                ".java", ".cpp", ".c", ".h", ".hpp",
                ".cs", ".go", ".rs", ".rb", ".php",
                ".swift", ".kt", ".scala", ".sh", ".bash", ".sql"
            ]
        },
        "output": {
            "docs_directory": "docs",
            "create_readme": True,
            "create_api_docs": True,
            "create_architecture_docs": True,
            "create_contributing": True,
            "create_changelog": False,
            "overwrite_existing": False
        },
        "languages": {
            "auto_detect": True,
            "overrides": {}
        },
        "advanced": {
            "chunk_size": 4000,
            "max_concurrent_requests": 3,
            "retry_attempts": 3,
            "enable_caching": True,
            "cache_ttl_hours": 24,
            "log_level": "INFO",
            "generate_summary": True,
            "analyze_dependencies": True,
            "analyze_code_structure": True,
            "enable_markdown_enhancements": True,
            "enable_seo_optimization": True
        },
        "notifications": {
            "enable_sound": True,
            "enable_completion_message": True
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or defaults."""
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
        elif os.path.exists("config.yaml"):
            self.load_from_file("config.yaml")
        else:
            logger.info("No config file found, using defaults")
    
    def load_from_file(self, path: str):
        """Load configuration from YAML file."""
        try:
            with open(path, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self._merge_config(user_config)
                logger.info(f"Loaded configuration from {path}")
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Merge user configuration with defaults."""
        for key, value in user_config.items():
            if key in self.config and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, *keys: str, value: Any):
        """Set configuration value using dot notation."""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
    
    def save(self, path: str = "config.yaml"):
        """Save current configuration to file."""
        try:
            with open(path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuration saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save config to {path}: {e}")
