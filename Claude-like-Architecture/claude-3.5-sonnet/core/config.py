# core/config.py
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
import logging
import os

from config.settings import Settings, ConfigError
from config.constants import (
    VERSION,
    Environment,
    LogLevel,
    MAX_TOKENS,
    DEFAULT_TIMEOUT,
    MAX_MEMORY_MB,
    ALLOWED_EXTENSIONS,
    API_RATE_LIMIT,
    MAX_FILE_SIZE,
    GC_INTERVAL,
    DEFAULT_CONFIG
)

@dataclass
class SystemConfig:
    """System configuration settings."""
    
    # System Settings
    system_name: str
    version: str
    environment: str
    debug_mode: bool = False

    # Performance Settings
    max_tokens: int = MAX_TOKENS
    response_timeout: int = DEFAULT_TIMEOUT
    max_concurrent_operations: int = 10
    memory_limit: int = MAX_MEMORY_MB * 1024 * 1024  # 1GB in bytes

    # Security Settings
    enable_safety_filters: bool = True
    content_filtering: bool = True
    max_retries: int = 3
    rate_limit: int = API_RATE_LIMIT

    # Resource Settings
    storage_path: Path = Path("storage")
    temp_path: Path = Path("temp")
    max_file_size: int = MAX_FILE_SIZE  # 10MB
    allowed_extensions: List[str] = field(default_factory=lambda: ALLOWED_EXTENSIONS['text'] + ALLOWED_EXTENSIONS['code'] + ALLOWED_EXTENSIONS['data'] + ALLOWED_EXTENSIONS['image'])
    cleanup_interval: int = GC_INTERVAL  # 1 hour
    max_storage_size: int = MAX_MEMORY_MB * 1024 * 1024  # 1GB in bytes

    # Logging Settings
    log_level: str = LogLevel.INFO.value
    log_file_path: Optional[str] = None
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    rotate_logs: bool = True
    log_max_size: int = MAX_FILE_SIZE  # 10MB
    log_backup_count: int = 5
    console_output: bool = True

    @classmethod
    def from_file(cls, config_path: Path) -> 'SystemConfig':
        """Load configuration from file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Konfigurationsfil hittades inte: {config_path}")

        try:
            if config_path.suffix == '.json':
                with open(config_path) as f:
                    config_data = json.load(f)
            elif config_path.suffix in ('.yaml', '.yml'):
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Otillåten konfigurationsformat: {config_path.suffix}")

            return cls(**config_data)

        except Exception as e:
            raise ConfigError(f"Misslyckades med att ladda konfiguration: {str(e)}")

    @classmethod
    def from_env(cls) -> 'SystemConfig':
        """Create configuration from environment variables."""
        config_data = {
            "system_name": os.getenv("SYSTEM_NAME", "Claude"),
            "version": os.getenv("VERSION", VERSION),
            "environment": os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value),
            "debug_mode": os.getenv("DEBUG_MODE", "false").lower() == "true",
            "max_tokens": int(os.getenv("MAX_TOKENS", str(MAX_TOKENS))),
            "response_timeout": int(os.getenv("TIMEOUT", str(DEFAULT_TIMEOUT))),
            "max_concurrent_operations": int(os.getenv("MAX_CONCURRENT_OPS", "10")),
            "memory_limit": int(os.getenv("MEMORY_LIMIT", str(MAX_MEMORY_MB * 1024 * 1024))),
            "enable_safety_filters": os.getenv("ENABLE_SAFETY_FILTERS", "true").lower() == "true",
            "content_filtering": os.getenv("CONTENT_FILTERING", "true").lower() == "true",
            "max_retries": int(os.getenv("MAX_RETRIES", "3")),
            "rate_limit": int(os.getenv("RATE_LIMIT", str(API_RATE_LIMIT))),
            "storage_path": Path(os.getenv("STORAGE_PATH", "storage")),
            "temp_path": Path(os.getenv("TEMP_PATH", "temp")),
            "max_file_size": int(os.getenv("MAX_FILE_SIZE", str(MAX_FILE_SIZE))),
            "allowed_extensions": os.getenv("ALLOWED_EXTENSIONS", '').split(',') if os.getenv("ALLOWED_EXTENSIONS") else ALLOWED_EXTENSIONS['text'] + ALLOWED_EXTENSIONS['code'] + ALLOWED_EXTENSIONS['data'] + ALLOWED_EXTENSIONS['image'],
            "cleanup_interval": int(os.getenv("CLEANUP_INTERVAL", str(GC_INTERVAL))),
            "max_storage_size": int(os.getenv("MAX_STORAGE_SIZE", str(MAX_MEMORY_MB * 1024 * 1024))),
            "log_level": os.getenv("LOG_LEVEL", LogLevel.INFO.value),
            "log_file_path": os.getenv("LOG_FILE"),
            "log_format": os.getenv("LOG_FORMAT", '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            "rotate_logs": os.getenv("ROTATE_LOGS", "true").lower() == "true",
            "log_max_size": int(os.getenv("LOG_MAX_SIZE", str(MAX_FILE_SIZE))),
            "log_backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5")),
            "console_output": os.getenv("LOG_CONSOLE_OUTPUT", "true").lower() == "true"
        }
        return cls(**config_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "system_name": self.system_name,
            "version": self.version,
            "environment": self.environment,
            "debug_mode": self.debug_mode,
            "max_tokens": self.max_tokens,
            "response_timeout": self.response_timeout,
            "max_concurrent_operations": self.max_concurrent_operations,
            "memory_limit": self.memory_limit,
            "enable_safety_filters": self.enable_safety_filters,
            "content_filtering": self.content_filtering,
            "max_retries": self.max_retries,
            "rate_limit": self.rate_limit,
            "storage_path": str(self.storage_path),
            "temp_path": str(self.temp_path),
            "max_file_size": self.max_file_size,
            "allowed_extensions": self.allowed_extensions,
            "cleanup_interval": self.cleanup_interval,
            "max_storage_size": self.max_storage_size,
            "log_level": self.log_level,
            "log_file_path": self.log_file_path,
            "log_format": self.log_format,
            "rotate_logs": self.rotate_logs,
            "log_max_size": self.log_max_size,
            "log_backup_count": self.log_backup_count,
            "console_output": self.console_output
        }

    def save(self, config_path: Path) -> None:
        """Save configuration to file."""
        config_data = self.to_dict()
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            if config_path.suffix == '.json':
                with open(config_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
            elif config_path.suffix in ('.yaml', '.yml'):
                with open(config_path, 'w') as f:
                    yaml.dump(config_data, f)
            else:
                raise ValueError(f"Otillåten konfigurationsformat: {config_path.suffix}")

        except Exception as e:
            raise ConfigError(f"Misslyckades med att spara konfiguration: {str(e)}")

    def validate(self) -> bool:
        """Validate configuration settings."""
        try:
            # System validation
            assert self.environment in [e.value for e in Environment], f"Ogiltig miljö: {self.environment}"
            
            # Performance validation
            assert isinstance(self.max_tokens, int) and 0 < self.max_tokens <= MAX_TOKENS, "max_tokens måste vara ett positivt heltal"
            assert isinstance(self.response_timeout, int) and self.response_timeout > 0, "response_timeout måste vara ett positivt heltal"
            assert isinstance(self.max_concurrent_operations, int) and self.max_concurrent_operations > 0, "max_concurrent_operations måste vara ett positivt heltal"
            assert isinstance(self.memory_limit, int) and 0 < self.memory_limit <= MAX_MEMORY_MB * 1024 * 1024, "memory_limit måste vara ett positivt heltal inom tillåtet intervall"
            
            # Security validation
            assert isinstance(self.max_retries, int) and self.max_retries >= 0, "max_retries måste vara ett icke-negativt heltal"
            assert isinstance(self.rate_limit, int) and self.rate_limit > 0, "rate_limit måste vara ett positivt heltal"
            
            # Resource validation
            assert isinstance(self.max_file_size, int) and self.max_file_size > 0, "max_file_size måste vara ett positivt heltal"
            assert isinstance(self.allowed_extensions, list) and all(ext.startswith('.') for ext in self.allowed_extensions), "allowed_extensions måste vara en lista av strängar som börjar med '.'"
            assert isinstance(self.cleanup_interval, int) and self.cleanup_interval > 0, "cleanup_interval måste vara ett positivt heltal"
            assert isinstance(self.max_storage_size, int) and self.max_storage_size > 0, "max_storage_size måste vara ett positivt heltal"
            
            # Logging validation
            assert self.log_level in [level.value for level in LogLevel], f"Ogiltig loggningsnivå: {self.log_level}"
            assert self.log_max_size > 0, "log_max_size måste vara positivt"
            assert self.log_backup_count >= 0, "log_backup_count måste vara icke-negativt"
            if self.log_file_path:
                log_file_path = Path(self.log_file_path)
                assert log_file_path.parent.exists() or log_file_path.parent.mkdir(parents=True), f"Sökvägen för log_file kunde inte skapas: {log_file_path.parent}"
            
            return True

        except AssertionError as e:
            logging.error(f"Konfigurationsvalidering misslyckades: {str(e)}")
            return False

    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration settings."""
        for key, value in updates.items():
            if hasattr(self, key):
                # Convert paths
                if key in ['storage_path', 'temp_path', 'log_file_path']:
                    value = Path(value)
                # Validate environment and log_level
                if key == 'environment' and value not in [e.value for e in Environment]:
                    raise ValueError(f"Ogiltig miljö: {value}")
                if key == 'log_level' and value not in [level.value for level in LogLevel]:
                    raise ValueError(f"Ogiltig loggningsnivå: {value}")
                setattr(self, key, value)

    def reset_defaults(self) -> None:
        """Reset configuration to default values."""
        default_config = DEFAULT_CONFIG
        self.system_name = default_config['system']['system_name']
        self.version = default_config['system']['version']
        self.environment = default_config['system']['environment']
        self.debug_mode = default_config['system']['debug_mode']
        self.max_tokens = default_config['system']['max_tokens']
        self.response_timeout = default_config['system']['timeout']
        self.max_concurrent_operations = 10  # Default
        self.memory_limit = MAX_MEMORY_MB * 1024 * 1024  # 1GB in bytes
        self.enable_safety_filters = default_config['security']['enable_safety']
        self.content_filtering = default_config['security']['content_filtering']
        self.max_retries = default_config['system']['max_retries']
        self.rate_limit = default_config['security']['rate_limit']
        self.storage_path = Path(default_config['resources']['storage_path'])
        self.temp_path = Path(default_config['resources']['temp_path'])
        self.max_file_size = default_config['resources']['max_file_size']
        self.allowed_extensions = default_config['resources']['allowed_extensions']
        self.cleanup_interval = default_config['resources']['cleanup_interval']
        self.max_storage_size = default_config['resources']['max_storage_size']
        self.log_level = default_config['logging']['level']
        self.log_file_path = default_config['logging']['file_path']
        self.log_format = default_config['logging']['format']
        self.rotate_logs = default_config['logging']['rotate_logs']
        self.log_max_size = default_config['logging']['max_size']
        self.log_backup_count = default_config['logging']['backup_count']
        self.console_output = default_config['logging']['console_output']
