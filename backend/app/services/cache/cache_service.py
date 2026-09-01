from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Tuple
import threading


class CacheEntry:
    def __init__(self, value: Any, ttl_seconds: int, source: str):
        self.value = value
        self.retrieved_at = datetime.now(timezone.utc)
        self.expires_at = self.retrieved_at + timedelta(seconds=ttl_seconds)
        self.source = source

    @property
    def is_fresh(self) -> bool:
        return datetime.now(timezone.utc) < self.expires_at


class CacheService:
    """Thread-safe in-memory cache supporting TTL and degraded data retention."""

    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str, allow_stale: bool = True) -> Optional[Tuple[Any, datetime, str, bool]]:
        """
        Retrieve cached value.
        Returns tuple: (value, retrieved_at, source, is_fresh) or None if absent.
        If allow_stale is True, returns degraded/stale entry with is_fresh=False instead of None.
        """
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            
            fresh = entry.is_fresh
            if not fresh and not allow_stale:
                return None
                
            return (entry.value, entry.retrieved_at, entry.source, fresh)

    def set(self, key: str, value: Any, ttl_seconds: int, source: str = "provider") -> None:
        with self._lock:
            self._cache[key] = CacheEntry(value=value, ttl_seconds=ttl_seconds, source=source)

    def delete(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


# Global singleton instance
cache_service = CacheService()
