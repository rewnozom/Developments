# config/constants.py
from enum import Enum
from pathlib import Path
from typing import Dict, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# System Constants
VERSION = os.getenv("VERSION", "1.0.0")
DEFAULT_ENCODING = os.getenv("DEFAULT_ENCODING", "utf-8")
TEMP_DIR = Path(os.getenv("TEMP_PATH", "./temp"))
CACHE_DIR = Path(os.getenv("CACHE_DIR", "./cache"))

class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class SystemStatus(Enum):
    """System status enumeration."""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class OperationType(Enum):
    """Operation type enumeration."""
    CONVERSATION = "conversation"
    GENERATION = "generation"
    PROCESSING = "processing"
    ANALYSIS = "analysis"

class ContentType(Enum):
    """Content type enumeration."""
    TEXT = "text"
    CODE = "code"
    MARKDOWN = "markdown"
    HTML = "html"
    SVG = "svg"
    MERMAID = "mermaid"

class SecurityLevel(Enum):
    """Security level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    STRICT = "strict"

# Token Constants
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "100000"))
TOKEN_PADDING = int(os.getenv("TOKEN_PADDING", "50"))
RESPONSE_BUFFER = int(os.getenv("RESPONSE_BUFFER", "1000"))

# Time Constants
DEFAULT_TIMEOUT = int(os.getenv("TIMEOUT", "30"))
MAX_RETRY_DELAY = int(os.getenv("MAX_RETRY_DELAY", "60"))
RETRY_BACKOFF_FACTOR = int(os.getenv("RETRY_BACKOFF_FACTOR", "2"))

# Memory Constants
MAX_MEMORY_MB = int(os.getenv("MEMORY_LIMIT", "1024"))
CLEANUP_THRESHOLD = float(os.getenv("CLEANUP_THRESHOLD", "0.9"))
GC_INTERVAL = int(os.getenv("CLEANUP_INTERVAL", "3600"))  # 1 hour

# File Constants
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB default
ALLOWED_EXTENSIONS: Dict[str, List[str]] = {
    'text': os.getenv("ALLOWED_TEXT_EXTENSIONS", ".txt,.md,.rst").split(","),
    'code': os.getenv("ALLOWED_CODE_EXTENSIONS", ".py,.js,.java,.cpp,.h").split(","),
    'data': os.getenv("ALLOWED_DATA_EXTENSIONS", ".json,.yaml,.yml,.csv").split(","),
    'image': os.getenv("ALLOWED_IMAGE_EXTENSIONS", ".svg").split(",")
}

# Content Types
MIME_TYPES = {
    'code': 'application/vnd.ant.code',
    'markdown': 'text/markdown',
    'html': 'text/html',
    'svg': 'image/svg+xml',
    'mermaid': 'application/vnd.ant.mermaid',
    'react': 'application/vnd.ant.react'
}

# API Constants
API_VERSION = os.getenv("API_VERSION", "v1")
API_BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": f"claude-sonnet/{VERSION}"
}

# Security Constants
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
API_RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))  # requests per minute
TOKEN_EXPIRY = int(os.getenv("TOKEN_EXPIRY", "3600"))  # 1 hour
MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "12"))

# Cache Settings
DEFAULT_CACHE_SIZE = int(os.getenv("CACHE_SIZE", "1000"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
CACHE_CLEANUP_INTERVAL = int(os.getenv("CACHE_CLEANUP_INTERVAL", "300"))  # 5 minutes

# Model Settings
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "lm-studio-local")

# Model-specific settings for different providers
MODEL_SETTINGS = {
    "claude-3-haiku": {
        "model_name": os.getenv("CLAUDE_HAIKU_MODEL", "claude-3-haiku-20240307"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "100000")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "top_p": float(os.getenv("TOP_P", "0.9"))
    },
    "claude-3-sonnet": {
        "model_name": os.getenv("CLAUDE_SONNET_MODEL", "claude-3-sonnet-20240229"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "100000")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "top_p": float(os.getenv("TOP_P", "0.9"))
    },
    "claude-3-opus": {
        "model_name": os.getenv("CLAUDE_OPUS_MODEL", "claude-3-opus-20240229"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "100000")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "top_p": float(os.getenv("TOP_P", "0.9"))
    },
    "gpt-4": {
        "model_name": os.getenv("GPT4_MODEL", "gpt-4"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "100000")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "top_p": float(os.getenv("TOP_P", "0.9"))
    },
    "gpt-3.5-turbo": {
        "model_name": os.getenv("GPT35_MODEL", "gpt-3.5-turbo"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "100000")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "top_p": float(os.getenv("TOP_P", "0.9"))
    },
    "lm-studio-local": {
        "model_name": os.getenv("LM_STUDIO_MODEL", "model-identifier"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "100000")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "top_p": float(os.getenv("TOP_P", "0.9")),
        "api_base": os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    }
}

# Error Messages
ERROR_MESSAGES = {
    'validation': 'Validation failed: {details}',
    'not_found': 'Resource not found: {resource}',
    'permission': 'Permission denied: {reason}',
    'rate_limit': 'Rate limit exceeded. Try again in {seconds} seconds.',
    'timeout': 'Operation timed out after {seconds} seconds.',
    'memory': 'Memory limit exceeded. Current usage: {usage}MB',
    'token': 'Token limit exceeded. Required: {required}, Available: {available}'
}

# Success Messages
SUCCESS_MESSAGES = {
    'created': 'Resource created successfully: {resource}',
    'updated': 'Resource updated successfully: {resource}',
    'deleted': 'Resource deleted successfully: {resource}'
}

# Response Templates
RESPONSE_TEMPLATES = {
    'error': {
        'status': 'error',
        'message': '{message}',
        'code': '{code}',
        'details': '{details}'
    },
    'success': {
        'status': 'success',
        'data': '{data}',
        'metadata': '{metadata}'
    }
}

# Validation Patterns
PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'url': r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',
    'version': r'^\d+\.\d+\.\d+$',
    'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
}

# Default Configuration
DEFAULT_CONFIG = {
    'system': {
        'debug_mode': os.getenv("DEBUG", "false").lower() == "true",
        'environment': os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value),
        'max_retries': int(os.getenv("MAX_RETRIES", "3")),
        'timeout': DEFAULT_TIMEOUT,
        'cache_enabled': os.getenv("CACHE_ENABLED", "true").lower() == "true",
        'cache_size': DEFAULT_CACHE_SIZE,
        'base_url': API_BASE_URL,
        'version': VERSION,
        'model_name': DEFAULT_MODEL
    },
    'security': {
        'enable_safety': os.getenv("ENABLE_SAFETY_FILTERS", "true").lower() == "true",
        'content_filtering': os.getenv("CONTENT_FILTERING", "true").lower() == "true",
        'max_tokens': MAX_TOKENS,
        'rate_limit': API_RATE_LIMIT,
        'api_key_required': os.getenv("API_KEY_REQUIRED", "false").lower() == "true",
        'allowed_origins': ALLOWED_ORIGINS,
        'ssl_verify': os.getenv("SSL_VERIFY", "true").lower() == "true",
        'max_request_size': MAX_FILE_SIZE
    },
    'resources': {
        'storage_path': os.getenv("STORAGE_PATH", "storage"),
        'temp_path': os.getenv("TEMP_PATH", "temp"),
        'max_file_size': MAX_FILE_SIZE,
        'allowed_extensions': ALLOWED_EXTENSIONS,
        'cleanup_interval': GC_INTERVAL,
        'max_storage_size': MAX_MEMORY_MB * 1024 * 1024  # 1GB in bytes
    },
    'logging': {
        'level': os.getenv("LOG_LEVEL", LogLevel.INFO.value),
        'file_path': os.getenv("LOG_FILE", None),
        'format': os.getenv("LOG_FORMAT", '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        'rotate_logs': os.getenv("ROTATE_LOGS", "true").lower() == "true",
        'max_size': MAX_FILE_SIZE,
        'backup_count': int(os.getenv("LOG_BACKUP_COUNT", "5")),
        'console_output': os.getenv("LOG_CONSOLE_OUTPUT", "true").lower() == "true"
    }
}