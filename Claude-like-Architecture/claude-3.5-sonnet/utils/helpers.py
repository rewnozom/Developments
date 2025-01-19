# utils/helpers.py
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from datetime import datetime
import time
import json
import re
import functools
import logging
from pathlib import Path

T = TypeVar('T')

def retry_operation(
    func: Callable[..., T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Retry an operation with exponential backoff."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        last_exception = None
        delay_time = delay

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(delay_time)
                    delay_time *= backoff_factor
                    logging.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__}")
                else:
                    break
                    
        raise OperationError(
            f"Operation failed after {max_retries} retries: {str(last_exception)}"
        )
    
    return wrapper

def safe_execute(
    func: Callable[..., T],
    default: Optional[T] = None,
    log_errors: bool = True
) -> T:
    """Safely execute a function with error handling."""
    try:
        return func()
    except Exception as e:
        if log_errors:
            logging.error(f"Error executing {func.__name__}: {str(e)}")
        return default

def calculate_token_length(text: str) -> int:
    """Estimate token length of text."""
    # Simple estimation - in production use proper tokenizer
    words = text.split()
    return sum(len(word) // 4 + 1 for word in words)

def text_to_tokens(text: str) -> List[str]:
    """Convert text to tokens."""
    # Simple tokenization - in production use proper tokenizer
    return re.findall(r'\b\w+\b', text.lower())

def load_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Safely load JSON file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {str(e)}")
        return {}

def save_json_file(data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
    """Safely save JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {str(e)}")
        return False

def chunks(lst: List[T], n: int) -> List[List[T]]:
    """Split list into chunks of size n."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """Convert timestamp to datetime."""
    return datetime.fromtimestamp(timestamp)

def datetime_to_timestamp(dt: datetime) -> float:
    """Convert datetime to timestamp."""
    return dt.timestamp()

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length while preserving words."""
    if len(text) <= max_length:
        return text
        
    truncated = text[:max_length-len(suffix)].rsplit(' ', 1)[0]
    return truncated + suffix

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.findall(url_pattern, text)

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove control characters
    text = "".join(char for char in text if char.isprintable())
    return text

def create_directory(directory: Union[str, Path]) -> bool:
    """Create directory if it doesn't exist."""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {directory}: {str(e)}")
        return False

def remove_directory(directory: Union[str, Path]) -> bool:
    """Remove directory and all contents."""
    try:
        path = Path(directory)
        if path.exists():
            for item in path.iterdir():
                if item.is_dir():
                    remove_directory(item)
                else:
                    item.unlink()
            path.rmdir()
        return True
    except Exception as e:
        logging.error(f"Error removing directory {directory}: {str(e)}")
        return False

class OperationError(Exception):
    """Raised when an operation fails."""
    pass

class RetryError(Exception):
    """Raised when retry operation fails."""
    pass