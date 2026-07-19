"""
In-memory caching system with TTL support
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from logger import setup_logger

logger = setup_logger(__name__)


class TTLCache:
    """TTL Cache implementation"""
    
    def __init__(self, ttl: int = 30):
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        logger.info(f"✅ Cache initialized with {ttl}s TTL")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            if datetime.now() > entry["expires_at"]:
                del self._cache[key]
                return None
            
            return entry["value"]
    
    async def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        async with self._lock:
            self._cache[key] = {
                "value": value,
                "expires_at": datetime.now() + timedelta(seconds=self.ttl),
            }
    
    async def clear(self) -> None:
        """Clear all cache"""
        async with self._lock:
            self._cache.clear()


# Global cache instances
rate_cache = TTLCache(ttl=30)
user_request_cache = TTLCache(ttl=2)