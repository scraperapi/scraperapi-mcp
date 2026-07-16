"""Shared async HTTP transport for all ScraperAPI tool families.

This module is a thin wrapper over ``httpx`` that centralizes timeout handling
and translates transport/HTTP failures into a single :class:`ScraperAPIError`
with an actionable message.
"""

from typing import Any, Optional

import httpx
import logging

from scraperapi_mcp_server.config import settings
from scraperapi_mcp_server.utils.exceptions import ScraperAPIError


def clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Drop ``None`` and empty-string values from a query/body dict.

    ScraperAPI treats an empty param as a set-but-blank value, so unset optional
    fields must be omitted entirely rather than sent as ``""``.
    """
    return {k: v for k, v in params.items() if v is not None and v != ""}


async def request(
    method: str,
    url: str,
    *,
    params: Optional[dict[str, Any]] = None,
    json: Optional[dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> httpx.Response:
    """Perform an HTTP request and return the response, raising on failure.

    Raises:
        ScraperAPIError: On non-2xx responses, connection errors, or any other
            unexpected failure. The message includes the target URL and, for HTTP
            errors, the status code and a truncated response body.
    """
    effective_timeout = timeout if timeout is not None else settings.API_TIMEOUT_SECONDS
    try:
        logging.info(f"{method} {url}")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.request(
                method,
                url,
                params=params,
                json=json,
                timeout=effective_timeout,
            )
            response.raise_for_status()
        return response
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        body_preview = (e.response.text or "").strip()[:500]
        error_message = f"HTTP error {status_code} from {url}." + (
            f" Response: {body_preview}" if body_preview else ""
        )
        logging.exception(f"http.request: {error_message}")
        raise ScraperAPIError(error_message) from e
    except httpx.RequestError as e:
        error_message = f"Connection error contacting {url}: {e}"
        logging.exception(f"http.request: {error_message}")
        raise ScraperAPIError(error_message) from e
    except ScraperAPIError:
        raise
    except Exception as e:
        error_message = f"Unexpected error contacting {url}: {e}"
        logging.exception(f"http.request: {error_message}")
        raise ScraperAPIError(error_message) from e


async def get(
    url: str,
    *,
    params: Optional[dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> httpx.Response:
    """GET ``url`` with the given query params."""
    return await request("GET", url, params=params, timeout=timeout)


async def post(
    url: str,
    *,
    json: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> httpx.Response:
    """POST ``url`` with a JSON body."""
    return await request("POST", url, params=params, json=json, timeout=timeout)


async def delete(
    url: str,
    *,
    params: Optional[dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> httpx.Response:
    """DELETE ``url``."""
    return await request("DELETE", url, params=params, timeout=timeout)
