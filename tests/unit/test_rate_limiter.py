import time
import pytest
from scraperapi_mcp_server.utils.rate_limiter import RateLimiter, RateLimitExceededError


class TestRateLimiter:
    def test_allows_calls_within_limit(self):
        limiter = RateLimiter(max_calls=3, window_seconds=60)
        for _ in range(3):
            limiter.acquire()

    def test_blocks_calls_over_limit(self):
        limiter = RateLimiter(max_calls=2, window_seconds=60)
        limiter.acquire()
        limiter.acquire()
        with pytest.raises(RateLimitExceededError, match="Rate limit exceeded"):
            limiter.acquire()

    def test_allows_calls_after_window_expires(self):
        limiter = RateLimiter(max_calls=1, window_seconds=0.1)
        limiter.acquire()
        with pytest.raises(RateLimitExceededError):
            limiter.acquire()
        time.sleep(0.15)
        limiter.acquire()

    def test_sliding_window_evicts_old_entries(self):
        limiter = RateLimiter(max_calls=2, window_seconds=0.2)
        limiter.acquire()
        time.sleep(0.15)
        limiter.acquire()
        time.sleep(0.1)
        # First call should have expired, so this should succeed
        limiter.acquire()
