import time
import threading


class RateLimiter:
    """Sliding window rate limiter for tool invocations."""

    def __init__(self, max_calls: int, window_seconds: float):
        self._max_calls = max_calls
        self._window_seconds = window_seconds
        self._timestamps: list[float] = []
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """Check rate limit. Raises RateLimitExceededError if exceeded."""
        now = time.monotonic()
        with self._lock:
            cutoff = now - self._window_seconds
            self._timestamps = [t for t in self._timestamps if t > cutoff]
            if len(self._timestamps) >= self._max_calls:
                raise RateLimitExceededError(
                    f"Rate limit exceeded: max {self._max_calls} requests per {self._window_seconds}s. Please wait before retrying."
                )
            self._timestamps.append(now)


class RateLimitExceededError(Exception):
    """Raised when the rate limit is exceeded."""

    pass
