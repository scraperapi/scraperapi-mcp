"""Shared tool-execution plumbing for all ScraperAPI MCP tools."""

from typing import Awaitable

import httpx
from mcp.server.fastmcp.exceptions import ToolError

from scraperapi_mcp_server.config import ApiKeyEnvVarNotSetError, settings
from scraperapi_mcp_server.sdes.base import BaseSdeParams, fetch_sde
from scraperapi_mcp_server.utils.exceptions import ScraperAPIError
from scraperapi_mcp_server.utils.rate_limiter import (
    RateLimiter,
    RateLimitExceededError,
)

# One rate limiter shared by every tool so the configured limit is global.
rate_limiter = RateLimiter(
    max_calls=settings.RATE_LIMIT_MAX_CALLS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)


def require_ready() -> None:
    """Validate preconditions common to every tool invocation.

    Raises:
        ToolError: If the API key is not configured or the rate limit is hit.
    """
    try:
        settings.validate_api_key()
    except ApiKeyEnvVarNotSetError as e:
        raise ToolError(str(e)) from e
    try:
        rate_limiter.acquire()
    except RateLimitExceededError as e:
        raise ToolError(str(e)) from e


async def run_sde(path: str, params: BaseSdeParams) -> str:
    """Run a structured-data endpoint tool end to end.

    Applies the shared guard rails, calls the endpoint, and converts any
    :class:`ScraperAPIError` into a :class:`ToolError`.

    Args:
        path: Endpoint path including the ``/structured`` prefix.
        params: A populated :class:`BaseSdeParams` subclass instance.

    Returns:
        The raw response body (JSON or CSV) as text.
    """
    require_ready()
    try:
        return await fetch_sde(path, params)
    except ScraperAPIError as e:
        raise ToolError(str(e)) from e


async def run_request(response: Awaitable[httpx.Response]) -> str:
    """Run a raw HTTP tool call end to end.

    For tools that assemble their own request (e.g. the crawler, which POSTs a
    JSON body to a different host). Applies the shared guard rails, awaits the
    already-constructed request, and converts any :class:`ScraperAPIError` into a
    :class:`ToolError`.

    Args:
        response: An un-awaited ``http.get/post/delete(...)`` coroutine.

    Returns:
        The response body as text.
    """
    require_ready()
    try:
        result = await response
        return result.text
    except ScraperAPIError as e:
        raise ToolError(str(e)) from e
