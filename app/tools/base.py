"""
Base tool infrastructure for YoshkaFlow.
Provides core functionality for tool execution, caching, and status tracking.
"""
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
import json
import hashlib
from datetime import datetime, timedelta

from app.core.config import get_settings
import redis

class ToolException(Exception):
    """Base exception for tool-related errors"""
    pass

class ValidationError(ToolException):
    """Raised when tool input validation fails"""
    pass

class ExecutionError(ToolException):
    """Raised when tool execution fails"""
    pass

class BaseTool(ABC):
    """
    Base class for all tools in YoshkaFlow.
    Provides common functionality for caching, validation, and execution.
    """
    def __init__(self):
        self.settings = get_settings()
        self.redis = redis.Redis.from_url(self.settings.REDIS_URL)
        
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool's main functionality.
        Must be implemented by all tool classes.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            Dict containing the tool's execution results
            
        Raises:
            ExecutionError: If tool execution fails
        """
        raise NotImplementedError
    
    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """
        Validate the tool's input parameters.
        Must be implemented by all tool classes.
        
        Args:
            **kwargs: Tool-specific arguments to validate
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """
        raise NotImplementedError
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """
        Generate a cache key for the given tool and parameters.
        
        Args:
            prefix: Tool-specific prefix for the cache key
            **kwargs: Parameters to include in the cache key
            
        Returns:
            str: Cache key
        """
        # Sort kwargs by key to ensure consistent cache keys
        sorted_items = sorted(kwargs.items())
        key_str = f"{prefix}:" + ":".join(f"{k}={v}" for k, v in sorted_items)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def cache_result(self, key: str, result: Dict[str, Any], expire: int = 3600) -> None:
        """
        Cache tool results in Redis.
        
        Args:
            key: Cache key
            result: Result data to cache
            expire: Cache expiration time in seconds (default: 1 hour)
        """
        cache_data = {
            "result": result,
            "cached_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=expire)).isoformat()
        }
        self.redis.set(f"tool_result:{key}", json.dumps(cache_data), ex=expire)
    
    def get_cached_result(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached tool results from Redis.
        
        Args:
            key: Cache key
            
        Returns:
            Optional[Dict]: Cached result data if found and valid, None otherwise
        """
        value = self.redis.get(f"tool_result:{key}")
        if not value:
            return None
            
        try:
            cache_data = json.loads(value)
            # Return just the result part of the cached data
            return cache_data.get("result")
        except json.JSONDecodeError:
            return None
    
    async def run(self, use_cache: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Main entry point for running a tool. Handles validation, caching, and execution.
        
        Args:
            use_cache: Whether to use cached results if available
            **kwargs: Tool-specific arguments
            
        Returns:
            Dict containing the tool's results
            
        Raises:
            ValidationError: If input validation fails
            ExecutionError: If tool execution fails
        """
        # Validate input
        if not self.validate_input(**kwargs):
            raise ValidationError("Tool input validation failed")
            
        # Generate cache key
        cache_key = self._generate_cache_key(self.__class__.__name__, **kwargs)
        
        # Check cache if enabled
        if use_cache:
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
        
        try:
            # Execute tool
            result = await self.execute(**kwargs)
            
            # Cache successful result
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            raise ExecutionError(f"Tool execution failed: {str(e)}")
