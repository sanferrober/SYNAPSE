"""
Utility functions for Synapse
"""

import json
import os
import hashlib
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from functools import wraps
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.debug(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result
    return wrapper


def retry_decorator(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry function execution on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            raise last_exception
        return wrapper
    return decorator


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    timestamp = str(datetime.now().timestamp())
    hash_input = f"{prefix}{timestamp}{os.urandom(8).hex()}"
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    return f"{prefix}{hash_value}" if prefix else hash_value


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        logger.error(f"Failed to parse JSON: {json_str[:100]}...")
        return default


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Safely dump object to JSON string"""
    try:
        return json.dumps(obj, ensure_ascii=False, **kwargs)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to serialize object: {str(e)}")
        return "{}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_timestamp(timestamp: Union[str, datetime, float, None] = None) -> str:
    """Format timestamp to ISO format"""
    if timestamp is None:
        return datetime.now().isoformat()
    elif isinstance(timestamp, str):
        return timestamp
    elif isinstance(timestamp, datetime):
        return timestamp.isoformat()
    elif isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp).isoformat()
    else:
        return datetime.now().isoformat()


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def validate_required_fields(data: Dict, required_fields: List[str]) -> tuple[bool, List[str]]:
    """Validate that required fields are present in data"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    return len(missing_fields) == 0, missing_fields


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def calculate_hash(data: Union[str, bytes]) -> str:
    """Calculate SHA256 hash of data"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction - can be enhanced with NLP
    words = text.lower().split()
    keywords = []
    
    for word in words:
        # Remove punctuation
        word = ''.join(c for c in word if c.isalnum())
        if len(word) >= min_length and word not in keywords:
            keywords.append(word)
    
    return keywords[:10]  # Return top 10 keywords


def create_error_response(error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    error_response = {
        "success": False,
        "error": {
            "type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        }
    }
    
    if context:
        error_response["error"]["context"] = context
    
    return error_response


def create_success_response(data: Any = None, message: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized success response"""
    response = {
        "success": True,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    return response


class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if call is allowed for given key"""
        now = time.time()
        
        # Clean old entries
        self.calls = {
            k: [t for t in times if now - t < self.time_window]
            for k, times in self.calls.items()
        }
        
        # Check rate limit
        if key not in self.calls:
            self.calls[key] = []
        
        if len(self.calls[key]) >= self.max_calls:
            return False
        
        self.calls[key].append(now)
        return True


class Cache:
    """Simple in-memory cache implementation"""
    
    def __init__(self, ttl: float = 300):  # 5 minutes default TTL
        self.ttl = ttl
        self.cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
    
    def remove(self, key: str) -> None:
        """Remove specific key from cache"""
        if key in self.cache:
            del self.cache[key]