# core/constants.py
from enum import Enum
from pathlib import Path

# System Constants
VERSION = "1.0.0"
DEFAULT_ENCODING = "utf-8"
TEMP_DIR = Path("./temp")
CACHE_DIR = Path("./cache")

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

# Token Constants
MAX_TOKENS = 100000
TOKEN_PADDING = 50
RESPONSE_BUFFER = 1000

# Time Constants
DEFAULT_TIMEOUT = 30
MAX_RETRY_DELAY = 60
RETRY_BACKOFF_FACTOR = 2

# Memory Constants
MAX_MEMORY_MB = 1024
CLEANUP_THRESHOLD = 0.9
GC_INTERVAL = 3600

# File Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    'text': ['.txt', '.md', '.rst'],
    'code': ['.py', '.js', '.java', '.cpp', '.h'],
    'data': ['.json', '.yaml', '.yml', '.csv'],
    'image': ['.svg']
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
API_VERSION = "v1"
API_BASE_URL = "https://api.anthropic.com"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": f"claude-sonnet/{VERSION}"
}

# Security Constants
ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000'
]
API_RATE_LIMIT = 60  # requests per minute
TOKEN_EXPIRY = 3600  # 1 hour
MIN_PASSWORD_LENGTH = 12

# Cache Settings
DEFAULT_CACHE_SIZE = 1000
CACHE_TTL = 3600  # 1 hour
CACHE_CLEANUP_INTERVAL = 300  # 5 minutes

# Model Settings
DEFAULT_MODEL = "claude-3-5-sonnet"
MODEL_SETTINGS = {
    "claude-3-5-sonnet": {
        "max_tokens": 100000,
        "temperature": 0.7,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
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
        'debug_mode': False,
        'environment': Environment.DEVELOPMENT.value,
        'max_retries': 3,
        'timeout': DEFAULT_TIMEOUT
    },
    'security': {
        'enable_safety_filters': True,
        'content_filtering': True,
        'max_tokens': MAX_TOKENS,
        'rate_limit': API_RATE_LIMIT
    },
    'resources': {
        'max_file_size': MAX_FILE_SIZE,
        'allowed_extensions': ALLOWED_EXTENSIONS,
        'auto_cleanup': True
    },
    'logging': {
        'level': LogLevel.INFO.value,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }
}