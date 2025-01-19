# config/settings.py

import os
import json
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import constants
from config.constants import (
    Environment,
    LogLevel,
    MAX_TOKENS,
    DEFAULT_TIMEOUT,
    MAX_MEMORY_MB,
    ALLOWED_EXTENSIONS,
    API_RATE_LIMIT,
    MAX_FILE_SIZE,
    GC_INTERVAL,
    DEFAULT_CACHE_SIZE,
    DEFAULT_MODEL,
    ALLOWED_ORIGINS,
    MODEL_SETTINGS
)

# Custom exception class
class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass

@dataclass
class SystemSettings:
    """System-wide settings."""
    debug_mode: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value))
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    timeout: int = field(default_factory=lambda: int(os.getenv("TIMEOUT", str(DEFAULT_TIMEOUT))))
    cache_enabled: bool = field(default_factory=lambda: os.getenv("CACHE_ENABLED", "true").lower() == "true")
    cache_size: int = field(default_factory=lambda: int(os.getenv("CACHE_SIZE", str(DEFAULT_CACHE_SIZE))))
    base_url: str = field(default_factory=lambda: os.getenv("BASE_URL", "http://localhost:8000"))
    version: str = field(default_factory=lambda: os.getenv("VERSION", "1.0.0"))
    model_name: str = field(default_factory=lambda: os.getenv("MODEL_NAME", DEFAULT_MODEL))
    model_settings: Dict[str, Any] = field(default_factory=lambda: MODEL_SETTINGS)

@dataclass
class SecuritySettings:
    """Security-related settings."""
    enable_safety_filters: bool = field(default_factory=lambda: os.getenv("ENABLE_SAFETY_FILTERS", "true").lower() == "true")
    content_filtering: bool = field(default_factory=lambda: os.getenv("CONTENT_FILTERING", "true").lower() == "true")
    max_tokens: int = field(default_factory=lambda: int(os.getenv("MAX_TOKENS", str(MAX_TOKENS))))
    rate_limit: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT", str(API_RATE_LIMIT))))
    api_key_required: bool = field(default_factory=lambda: os.getenv("API_KEY_REQUIRED", "false").lower() == "true")
    allowed_origins: List[str] = field(default_factory=lambda: os.getenv("ALLOWED_ORIGINS", ",".join(ALLOWED_ORIGINS)).split(","))
    ssl_verify: bool = field(default_factory=lambda: os.getenv("SSL_VERIFY", "true").lower() == "true")
    max_request_size: int = field(default_factory=lambda: int(os.getenv("MAX_REQUEST_SIZE", str(MAX_FILE_SIZE))))

@dataclass
class LoggingSettings:
    """Logging configuration."""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", LogLevel.INFO.value))
    file_path: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE", "logs/claude.log"))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    rotate_logs: bool = field(default_factory=lambda: os.getenv("ROTATE_LOGS", "true").lower() == "true")
    max_size: int = field(default_factory=lambda: int(os.getenv("LOG_MAX_SIZE", str(MAX_FILE_SIZE))))
    backup_count: int = field(default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", "5")))
    console_output: bool = field(default_factory=lambda: os.getenv("LOG_CONSOLE_OUTPUT", "true").lower() == "true")

@dataclass
class ResourceSettings:
    """Resource management settings."""
    storage_path: Path = field(default_factory=lambda: Path(os.getenv("STORAGE_PATH", "storage")))
    temp_path: Path = field(default_factory=lambda: Path(os.getenv("TEMP_PATH", "temp")))
    max_file_size: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", str(MAX_FILE_SIZE))))
    allowed_extensions: List[str] = field(default_factory=lambda: 
        os.getenv("ALLOWED_EXTENSIONS", 
                 ",".join(ALLOWED_EXTENSIONS['text'] + 
                         ALLOWED_EXTENSIONS['code'] + 
                         ALLOWED_EXTENSIONS['data'] + 
                         ALLOWED_EXTENSIONS['image'])).split(","))
    cleanup_interval: int = field(default_factory=lambda: int(os.getenv("CLEANUP_INTERVAL", str(GC_INTERVAL))))
    max_storage_size: int = field(default_factory=lambda: int(os.getenv("MAX_STORAGE_SIZE", str(MAX_MEMORY_MB * 1024 * 1024))))

class Settings:
    """Main settings configuration class."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        # Initialize subsystems
        self.system = SystemSettings()
        self.security = SecuritySettings()
        self.logging = LoggingSettings()
        self.resources = ResourceSettings()
        
        # Load configuration
        if config_path:
            self.load_config(config_path)

    @property
    def log_level(self) -> str:
        """For compatibility with older code."""
        return self.logging.level

    def load_config(self, config_path: Union[str, Path]) -> None:
        """Load configuration from file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path) as f:
                if config_path.suffix == '.json':
                    config_data = json.load(f)
                elif config_path.suffix in ('.yaml', '.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    raise ConfigError(f"Unsupported configuration format: {config_path.suffix}")

            self._update_settings(config_data)
            
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {str(e)}")

    def _update_settings(self, config_data: Dict[str, Any]) -> None:
        """Update settings from config data."""
        def update_section(section_name: str, section_data: Dict[str, Any]) -> None:
            section = getattr(self, section_name)
            for key, value in section_data.items():
                if hasattr(section, key):
                    if key.endswith('_path'):
                        value = Path(value)
                    setattr(section, key, value)

        sections = ['system', 'security', 'logging', 'resources']
        for section in sections:
            if section in config_data:
                update_section(section, config_data[section])

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'system': {k: str(v) if isinstance(v, Path) else v 
                     for k, v in self.system.__dict__.items()},
            'security': {k: v for k, v in self.security.__dict__.items()},
            'logging': {k: v for k, v in self.logging.__dict__.items()},
            'resources': {k: str(v) if isinstance(v, Path) else v 
                        for k, v in self.resources.__dict__.items()}
        }

    def save_config(self, config_path: Union[str, Path]) -> None:
        """Save current configuration to file."""
        config_data = self.to_dict()

        config_path = Path(config_path)
        try:
            if config_path.suffix == '.json':
                with open(config_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
            elif config_path.suffix in ('.yaml', '.yml'):
                with open(config_path, 'w') as f:
                    yaml.dump(config_data, f)
            else:
                raise ConfigError(f"Unsupported configuration format: {config_path.suffix}")
                
        except Exception as e:
            raise ConfigError(f"Error saving configuration: {str(e)}")

    def validate(self) -> bool:
        """Validate current configuration."""
        try:
            # System validation
            assert self.system.environment in [e.value for e in Environment], f"Invalid environment: {self.system.environment}"
            assert self.system.max_retries > 0, "max_retries must be positive"
            assert self.system.timeout > 0, "timeout must be positive"
            assert self.system.cache_size >= 0, "cache_size must be non-negative"
            assert self.system.model_name in self.system.model_settings, f"Unknown model: {self.system.model_name}"
            
            # Security validation
            assert self.security.max_tokens > 0, "max_tokens must be positive"
            assert self.security.rate_limit > 0, "rate_limit must be positive"
            assert self.security.max_request_size > 0, "max_request_size must be positive"
            
            # Logging validation
            assert self.logging.level in [level.value for level in LogLevel], f"Invalid logging level: {self.logging.level}"
            assert self.logging.max_size > 0, "log_max_size must be positive"
            assert self.logging.backup_count >= 0, "backup_count must be non-negative"
            
            # Resource validation
            assert self.resources.max_file_size > 0, "max_file_size must be positive"
            assert self.resources.cleanup_interval > 0, "cleanup_interval must be positive"
            assert self.resources.max_storage_size > 0, "max_storage_size must be positive"
            
            return True
            
        except AssertionError as e:
            logging.error(f"Configuration validation failed: {str(e)}")
            return False