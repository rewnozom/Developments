# utils/validators.py
from typing import Any, Dict, List, Optional, Union, Callable
import re
import json
from datetime import datetime
from pathlib import Path
import logging

def validate_input(
    data: Any,
    validation_type: str,
    **kwargs
) -> bool:
    """Validate input data based on type."""
    validators = {
        "text": validate_text,
        "number": validate_number,
        "email": validate_email,
        "url": validate_url,
        "json": validate_json,
        "path": validate_path,
        "datetime": validate_datetime
    }
    
    validator = validators.get(validation_type)
    if not validator:
        raise ValueError(f"Invalid validation type: {validation_type}")
        
    try:
        return validator(data, **kwargs)
    except Exception as e:
        logging.error(f"Validation error ({validation_type}): {str(e)}")
        return False

def validate_text(
    text: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    **kwargs
) -> bool:
    """Validate text content."""
    if not isinstance(text, str):
        return False
        
    if min_length is not None and len(text) < min_length:
        return False
        
    if max_length is not None and len(text) > max_length:
        return False
        
    if pattern is not None and not re.match(pattern, text):
        return False
        
    return True

def validate_number(
    number: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    is_integer: bool = False,
    **kwargs
) -> bool:
    """Validate numeric value."""
    if is_integer and not isinstance(number, int):
        return False
        
    if not isinstance(number, (int, float)):
        return False
        
    if min_value is not None and number < min_value:
        return False
        
    if max_value is not None and number > max_value:
        return False
        
    return True

def validate_email(
    email: str,
    allow_subdomains: bool = True,
    **kwargs
) -> bool:
    """Validate email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not allow_subdomains:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'
        
    return bool(re.match(pattern, email))

def validate_url(
    url: str,
    allowed_schemes: Optional[List[str]] = None,
    require_tld: bool = True,
    **kwargs
) -> bool:
    """Validate URL."""
    if not allowed_schemes:
        allowed_schemes = ['http', 'https']
        
    pattern = r'(?:' + '|'.join(allowed_schemes) + r')://'
    pattern += r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
    pattern += r'localhost|'
    pattern += r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    pattern += r'(?::\d+)?(?:/?|[/?]\S+)$'
    
    return bool(re.match(pattern, url, re.IGNORECASE))

def validate_json(
    data: Union[str, Dict, List],
    schema: Optional[Dict] = None,
    **kwargs
) -> bool:
    """Validate JSON data."""
    try:
        if isinstance(data, str):
            data = json.loads(data)
            
        if schema:
            return validate_schema(data, schema)
            
        return True
    except Exception:
        return False

def validate_path(
    path: Union[str, Path],
    must_exist: bool = True,
    file_type: Optional[str] = None,
    **kwargs
) -> bool:
    """Validate file or directory path."""
    try:
        path = Path(path)
        if must_exist and not path.exists():
            return False
            
        if file_type:
            if not path.is_file() or path.suffix.lower() != f".{file_type.lower()}":
                return False
                
        return True
    except Exception:
        return False

def validate_datetime(
    dt: Union[str, datetime],
    min_date: Optional[datetime] = None,
    max_date: Optional[datetime] = None,
    format_str: Optional[str] = None,
    **kwargs
) -> bool:
    """Validate datetime."""
    try:
            if isinstance(dt, str):
                if format_str:
                    dt = datetime.strptime(dt, format_str)
                else:
                    dt = datetime.fromisoformat(dt)
                    
            if min_date and dt < min_date:
                return False
                
            if max_date and dt > max_date:
                return False
                
            return True
    except Exception:
            return False



def validate_schema(
   data: Union[Dict, List],
   schema: Dict[str, Any]
) -> bool:
   """Validate data against JSON schema."""
   try:
       # Basic type validation
       if schema.get('type') == 'object' and not isinstance(data, dict):
           return False
       if schema.get('type') == 'array' and not isinstance(data, list):
           return False
           
       # Validate object properties
       if isinstance(data, dict):
           properties = schema.get('properties', {})
           required = schema.get('required', [])
           
           # Check required fields
           if not all(prop in data for prop in required):
               return False
               
           # Validate each property
           for prop, value in data.items():
               if prop in properties:
                   if not validate_value(value, properties[prop]):
                       return False
                       
       # Validate array items
       if isinstance(data, list):
           items = schema.get('items', {})
           if not all(validate_value(item, items) for item in data):
               return False
               
       return True
   except Exception:
       return False

def validate_value(
   value: Any,
   schema: Dict[str, Any]
) -> bool:
   """Validate a single value against schema definition."""
   try:
       # Check type
       type_map = {
           'string': str,
           'number': (int, float),
           'integer': int,
           'boolean': bool,
           'array': list,
           'object': dict
       }
       
       expected_type = type_map.get(schema.get('type'))
       if expected_type and not isinstance(value, expected_type):
           return False
           
       # Check enum
       if 'enum' in schema and value not in schema['enum']:
           return False
           
       # Check string constraints
       if isinstance(value, str):
           min_length = schema.get('minLength', 0)
           max_length = schema.get('maxLength')
           pattern = schema.get('pattern')
           
           if len(value) < min_length:
               return False
           if max_length and len(value) > max_length:
               return False
           if pattern and not re.match(pattern, value):
               return False
               
       # Check number constraints
       if isinstance(value, (int, float)):
           minimum = schema.get('minimum')
           maximum = schema.get('maximum')
           
           if minimum is not None and value < minimum:
               return False
           if maximum is not None and value > maximum:
               return False
               
       return True
   except Exception:
       return False

def create_validator(
   validation_type: str,
   **kwargs
) -> Callable[[Any], bool]:
   """Create a validator function with preset parameters."""
   def validator(data: Any) -> bool:
       return validate_input(data, validation_type, **kwargs)
   return validator

def validate_all(
   validators: List[Callable[[Any], bool]],
   data: Any
) -> bool:
   """Run multiple validators on data."""
   return all(validator(data) for validator in validators)

def validate_any(
   validators: List[Callable[[Any], bool]],
   data: Any
) -> bool:
   """Check if data passes any validator."""
   return any(validator(data) for validator in validators)

class ValidationError(Exception):
   """Base class for validation errors."""
   def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
       super().__init__(message)
       self.details = details or {}

class SchemaValidationError(ValidationError):
   """Raised when schema validation fails."""
   pass

class ValueError(ValidationError):
   """Raised when value validation fails."""
   pass

# Common validator instances
validate_positive_number = create_validator('number', min_value=0)
validate_percentage = create_validator('number', min_value=0, max_value=100)
validate_year = create_validator('number', min_value=1900, max_value=9999, is_integer=True)

# Email validators
validate_email_strict = create_validator('email', allow_subdomains=False)
validate_email_loose = create_validator('email', allow_subdomains=True)

# URL validators
validate_http_url = create_validator('url', allowed_schemes=['http', 'https'])
validate_file_url = create_validator('url', allowed_schemes=['file'])

# Path validators
validate_file_exists = create_validator('path', must_exist=True)
validate_directory_exists = create_validator('path', must_exist=True, file_type=None)

# JSON validators
validate_json_string = create_validator('json')

# Datetime validators
validate_iso_datetime = create_validator('datetime')
validate_future_date = create_validator(
   'datetime',
   min_date=datetime.now()
)