# utils/formatters.py
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import re
import json
import html

def format_response(
    content: str,
    format_type: str = "text",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Format response content based on type."""
    formatters = {
        "text": format_text,
        "code": format_code,
        "markdown": format_markdown,
        "html": format_html,
        "json": format_json
    }
    
    formatter = formatters.get(format_type, format_text)
    return formatter(content, metadata)

def format_text(
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Format plain text content."""
    # Clean and normalize text
    content = content.strip()
    content = re.sub(r'\s+', ' ', content)
    return content

def format_code(
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Format code content."""
    language = metadata.get("language", "") if metadata else ""
    
    # Add code block markers for markdown
    if language:
        return f"```{language}\n{content}\n```"
    return f"```\n{content}\n```"

def format_markdown(
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Format markdown content."""
    # Normalize headers
    content = re.sub(r'(?m)^#+\s*', lambda m: m.group().strip() + ' ', content)
    
    # Normalize lists
    content = re.sub(r'(?m)^[-*+]\s*', '- ', content)
    
    # Normalize code blocks
    content = re.sub(r'```\s*\n', '```\n', content)
    
    return content.strip()

def format_html(
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Format HTML content."""
    # Escape HTML special characters
    content = html.escape(content)
    
    # Wrap in appropriate tags
    tag = metadata.get("tag", "div") if metadata else "div"
    classes = metadata.get("classes", "") if metadata else ""
    
    return f"<{tag} class='{classes}'>{content}</{tag}>"

def format_json(
    content: Union[str, Dict[str, Any], List[Any]],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Format JSON content."""
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return content

    indent = metadata.get("indent", 2) if metadata else 2
    return json.dumps(content, indent=indent)

def format_timestamp(
    timestamp: Union[int, float, datetime],
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """Format timestamp to string."""
    if isinstance(timestamp, (int, float)):
        timestamp = datetime.fromtimestamp(timestamp)
    return timestamp.strftime(format_str)

def format_number(
    number: Union[int, float],
    decimal_places: int = 2,
    thousands_separator: str = ","
) -> str:
    """Format number with proper separators and decimal places."""
    try:
        if isinstance(number, int):
            return f"{number:,}"
        return f"{number:,.{decimal_places}f}"
    except Exception:
        return str(number)

def format_size(
    size_bytes: int,
    binary: bool = False
) -> str:
    """Format size in bytes to human readable format."""
    if binary:
        units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
        base = 1024
    else:
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        base = 1000

    for unit in units:
        if size_bytes < base:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= base
    
    return f"{size_bytes:.2f} {units[-1]}"

def format_duration(
    seconds: Union[int, float],
    include_seconds: bool = True
) -> str:
    """Format duration in seconds to human readable format."""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if include_seconds and seconds > 0:
        parts.append(f"{seconds}s")

    return " ".join(parts) if parts else "0s"

class FormatError(Exception):
    """Raised when formatting fails."""
    pass