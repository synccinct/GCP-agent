"""Helper utility functions."""

import re
import json
import time
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """Generate a unique identifier."""
    
    unique_part = str(uuid.uuid4()).replace('-', '')[:length]
    timestamp_part = str(int(time.time()))[-4:]
    
    if prefix:
        return f"{prefix}_{timestamp_part}_{unique_part}"
    else:
        return f"{timestamp_part}_{unique_part}"

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    # Ensure not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized

def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown text."""
    
    code_blocks = []
    
    # Pattern for fenced code blocks
    pattern = r'``````'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        language = match[0] if match[0] else "text"
        code = match[1].strip()
        
        code_blocks.append({
            "language": language,
            "code": code
        })
    
    return code_blocks

def validate_json_schema(data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data against JSON schema (simplified)."""
    
    errors = []
    
    def validate_field(field_name: str, value: Any, field_schema: Dict[str, Any]):
        field_type = field_schema.get("type")
        required = field_schema.get("required", False)
        
        if value is None:
            if required:
                errors.append(f"Field '{field_name}' is required")
            return
        
        if field_type == "string" and not isinstance(value, str):
            errors.append(f"Field '{field_name}' must be a string")
        elif field_type == "integer" and not isinstance(value, int):
            errors.append(f"Field '{field_name}' must be an integer")
        elif field_type == "number" and not isinstance(value, (int, float)):
            errors.append(f"Field '{field_name}' must be a number")
        elif field_type == "boolean" and not isinstance(value, bool):
            errors.append(f"Field '{field_name}' must be a boolean")
        elif field_type == "array" and not isinstance(value, list):
            errors.append(f"Field '{field_name}' must be an array")
        elif field_type == "object" and not isinstance(value, dict):
            errors.append(f"Field '{field_name}' must be an object")
    
    # Validate top-level fields
    if isinstance(schema, dict) and "properties" in schema:
        for field_name, field_schema in schema["properties"].items():
            value = data.get(field_name) if isinstance(data, dict) else None
            validate_field(field_name, value, field_schema)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def hash_content(content: str, algorithm: str = "sha256") -> str:
    """Generate hash of content."""
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(content.encode('utf-8'))
    return hash_obj.hexdigest()

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string with fallback."""
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {str(e)}")
        return default

def retry_with_delay(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry function with exponential backoff."""
    
    def wrapper(*args, **kwargs):
        last_exception = None
        current_delay = delay
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries - 1:
                    time.sleep(current_delay)
                    current_delay *= backoff
                else:
                    raise last_exception
    
    return wrapper

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix."""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def parse_size_string(size_str: str) -> int:
    """Parse size string (e.g., '1GB', '500MB') to bytes."""
    
    size_str = size_str.upper().strip()
    
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }
    
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)])
                return int(number * multiplier)
            except ValueError:
                break
    
    # Try to parse as plain number (assume bytes)
    try:
        return int(size_str)
    except ValueError:
        raise ValueError(f"Invalid size format: {size_str}")

def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    
    return filename.split('.')[-1].lower() if '.' in filename else ""

def is_valid_identifier(name: str) -> bool:
    """Check if string is a valid Python identifier."""
    
    return name.isidentifier() and not name.startswith('_')

def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def snake_to_camel(name: str) -> str:
    """Convert snake_case to CamelCase."""
    
    components = name.split('_')
    return ''.join(word.capitalize() for word in components)
  
