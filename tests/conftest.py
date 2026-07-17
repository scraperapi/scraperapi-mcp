import os

os.environ.setdefault("API_KEY", "test_api_key")

import pytest


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Clear the shared rate limiter before each test.

    Tools share one process-wide limiter (execution.rate_limiter). Tests that
    exercise the real guard would otherwise accumulate calls across the suite and
    eventually trip the limit, causing order-dependent failures.
    """
    from scraperapi_mcp_server.execution import rate_limiter

    rate_limiter._timestamps.clear()
    yield
