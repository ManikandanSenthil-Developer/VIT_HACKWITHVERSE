import time
from collections import defaultdict
from threading import Lock
from typing import Callable, Dict, List, Optional
from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """
    Thread-safe, in-memory sliding window rate limiter suitable for single-laptop
    and local production deployments without requiring external Redis clusters.
    """

    def __init__(self):
        self._lock = Lock()
        # Key: identifier (e.g. IP, user_id, or action:IP) -> List of float timestamps
        self._records: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(
        self, key: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if request is permitted under the sliding window.
        Returns (is_allowed, retry_after_seconds).
        """
        current_time = time.time()
        window_start = current_time - window_seconds

        with self._lock:
            # Filter timestamps within current window
            timestamps = [t for t in self._records[key] if t > window_start]
            self._records[key] = timestamps

            if len(timestamps) < max_requests:
                self._records[key].append(current_time)
                return True, 0
            else:
                earliest_in_window = timestamps[0]
                retry_after = max(1, int(earliest_in_window + window_seconds - current_time))
                return False, retry_after

    def clear(self):
        """Reset all rate limiter records (useful for test suites)."""
        with self._lock:
            self._records.clear()


# Global in-memory rate limiter singleton
rate_limiter = SlidingWindowRateLimiter()


def rate_limit_dependency(
    max_requests: int,
    window_seconds: int = 60,
    by_user: bool = False,
    action: Optional[str] = None,
) -> Callable:
    """
    FastAPI dependency generator for enforcing rate limits.
    """
    async def dependency(request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        action_prefix = f"{action}:" if action else ""

        # Check if auth header provides user identity or fallback to IP
        user_key = None
        if by_user:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                user_key = f"token:{hash(auth_header)}"

        identifier = f"{action_prefix}{user_key or client_ip}"
        allowed, retry_after = rate_limiter.is_allowed(
            key=identifier,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Rate limit exceeded. Please retry in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

    return dependency
