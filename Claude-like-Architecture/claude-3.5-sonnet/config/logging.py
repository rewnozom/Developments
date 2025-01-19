# config/logging.py
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import json
import yaml

from config.constants import LogLevel

class LogFormatter(logging.Formatter):
    """Custom formatter with additional fields."""

    def __init__(self, include_extra: bool = True):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with optional extra fields."""
        # Format basic message
        message = super().format(record)

        # Add extra fields if present and enabled
        if self.include_extra and hasattr(record, 'extra'):
            try:
                extra_data = json.dumps(record.extra, indent=2)
                message = f"{message}\nExtra Data:\n{extra_data}"
            except Exception:
                pass

        return message

class LogManager:
    """Manages logging configuration and operations."""

    def __init__(self,
                 log_level: str = LogLevel.INFO.value,
                 log_dir: Optional[Path] = None,
                 config_file: Optional[Path] = None):
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_dir = log_dir or Path("logs")
        self.handlers: Dict[str, logging.Handler] = {}
        
        # Create log directory if needed
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Load config if provided
        if config_file:
            self.load_config(config_file)

        # Initialize logging
        self.setup_logging()

    def setup_logging(self) -> None:
        """Set up logging configuration."""
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Add console handler
        console_handler = self._create_console_handler()
        root_logger.addHandler(console_handler)
        self.handlers['console'] = console_handler

        # Add file handler
        file_handler = self._create_file_handler()
        root_logger.addHandler(file_handler)
        self.handlers['file'] = file_handler

        # Add error file handler
        error_handler = self._create_error_handler()
        root_logger.addHandler(error_handler)
        self.handlers['error'] = error_handler

    def _create_console_handler(self) -> logging.Handler:
        """Create console handler."""
        handler = logging.StreamHandler()
        handler.setLevel(self.log_level)
        handler.setFormatter(LogFormatter())
        return handler

    def _create_file_handler(self) -> logging.Handler:
        """Create rotating file handler."""
        log_file = self.log_dir / "application.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        handler.setLevel(self.log_level)
        handler.setFormatter(LogFormatter(include_extra=True))
        return handler

    def _create_error_handler(self) -> logging.Handler:
        """Create error file handler."""
        error_file = self.log_dir / "error.log"
        handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        handler.setLevel(logging.ERROR)
        handler.setFormatter(LogFormatter(include_extra=True))
        return handler

    def load_config(self, config_file: Path) -> None:
        """Load logging configuration from file."""
        try:
            with open(config_file) as f:
                if config_file.suffix == '.json':
                    config = json.load(f)
                elif config_file.suffix in ('.yaml', '.yml'):
                    config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Otillåten config format: {config_file.suffix}")

            # Update settings
            self.log_level = getattr(logging, config.get('level', 'INFO').upper(),
                                      logging.INFO)
            
            if 'directory' in config:
                self.log_dir = Path(config['directory'])
                self.log_dir.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            logging.error(f"Misslyckades med att ladda loggkonfiguration: {str(e)}")

    def get_logger(self, name: str) -> logging.Logger:
        """Get logger with specified name."""
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        return logger

    def update_log_level(self, level: str) -> None:
        """Uppdatera loggningsnivå."""
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Uppdatera handlers
        for handler in self.handlers.values():
            handler.setLevel(self.log_level)

    def add_handler(self, name: str, handler: logging.Handler) -> None:
        """Lägg till en anpassad logghanterare."""
        if name in self.handlers:
            raise ValueError(f"Hanterare {name} finns redan")
            
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        self.handlers[name] = handler

    def remove_handler(self, name: str) -> None:
        """Ta bort en logghanterare."""
        if name not in self.handlers:
            return
            
        handler = self.handlers.pop(name)
        root_logger = logging.getLogger()
        root_logger.removeHandler(handler)

    def rotate_logs(self) -> None:
        """Tvinga rotation av loggfiler."""
        for handler in self.handlers.values():
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.doRollover()

    def archive_logs(self, archive_dir: Optional[Path] = None) -> None:
        """Arkivera aktuella loggfiler."""
        import shutil
        import time
        
        archive_dir = archive_dir or self.log_dir / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # Arkivera varje loggfil
        for handler in self.handlers.values():
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                log_file = Path(handler.baseFilename)
                if log_file.exists():
                    archive_name = f"{log_file.stem}-{timestamp}{log_file.suffix}"
                    shutil.copy2(log_file, archive_dir / archive_name)

    def cleanup_logs(self,
                    max_age_days: int = 30,
                    include_archive: bool = True) -> None:
        """Rensa gamla loggfiler."""
        import time
        
        now = time.time()
        max_age = max_age_days * 24 * 60 * 60
        
        def cleanup_dir(directory: Path) -> None:
            for file_path in directory.glob("*.log*"):
                if file_path.is_file():
                    age = now - file_path.stat().st_mtime
                    if age > max_age:
                        try:
                            file_path.unlink()
                        except Exception as e:
                            logging.error(f"Misslyckades med att ta bort {file_path}: {str(e)}")

        # Rensa huvudloggkatalogen
        cleanup_dir(self.log_dir)
        
        # Rensa arkiv om begärt
        if include_archive:
            archive_dir = self.log_dir / "archive"
            if archive_dir.exists():
                cleanup_dir(archive_dir)

def setup_logging(
   level: str = LogLevel.INFO.value,
   log_dir: Optional[Path] = None,
   config_file: Optional[Path] = None
) -> LogManager:
    """Initiera loggningssystemet."""
    manager = LogManager(level, log_dir, config_file)
    return manager

def get_logger(name: str) -> logging.Logger:
    """Hämta logger med angivet namn."""
    return logging.getLogger(name)
