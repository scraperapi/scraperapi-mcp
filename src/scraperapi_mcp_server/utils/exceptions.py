from typing import Dict, Any
from requests.exceptions import RequestException, HTTPError as RequestsHTTPError
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR
import logging


class ApiKeyEnvVarNotSetError(Exception):
    """Raised when the API key environment variable is not set."""

    pass


def handle_scraper_error(
    e: Exception, url: str, payload: Dict[str, Any] = None
) -> McpError:
    """
    Handle all scraper errors with simple error messages.

    Args:
        e: The exception that occurred
        url: The URL that was being scraped
        payload: Optional parameters used in the API call

    Returns:
        An McpError with error information
    """
    if isinstance(e, RequestsHTTPError) and hasattr(e, "response"):
        status_code = e.response.status_code
        error_message = f"HTTP error {status_code} when scraping '{url}': {str(e)}"
    elif isinstance(e, RequestException):
        error_message = f"Connection error when scraping '{url}': {str(e)}"
    else:
        error_message = f"Error when scraping '{url}': {str(e)}"

    # Include the parameters we tried in the error message if available
    if payload and isinstance(e, RequestsHTTPError):
        param_summary = " ".join(
            [f"{k}={v}" for k, v in payload.items() if k != "api_key"]
        )
        error_message += f" Parameters used: {param_summary}"

    logging.error(f"handle_scraper_error: {error_message}", exc_info=True)
    return McpError(
        ErrorData(
            code=INTERNAL_ERROR,
            message=error_message,
        )
    )
