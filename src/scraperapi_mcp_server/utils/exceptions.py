from typing import Dict, Any
from requests.exceptions import RequestException, HTTPError as RequestsHTTPError
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR


# Status code to error message mapping
HTTP_STATUS_DETAILS = {
    400: "Bad request - check the URL and parameters.",
    401: "Unauthorized - check your API key.",
    403: "Forbidden - you may not have access to this resource.",
    404: "URL not found - verify the URL is correct.",
    429: "Too many requests - you've exceeded your quota or rate limit.",
    500: "ScraperAPI server error - the service might be experiencing issues.",
    503: "Service unavailable - ScraperAPI might be down or overloaded.",
}


def handle_scraper_http_error(
    e: RequestsHTTPError, url: str, payload: Dict[str, Any]
) -> McpError:
    """
    Handle HTTP errors from ScraperAPI with detailed error messages.

    Args:
        e: The HTTP error exception
        url: The URL that was being scraped
        payload: The parameters used in the API call

    Returns:
        An McpError with detailed error information
    """
    status_code = e.response.status_code if hasattr(e, "response") else 500

    # Get error details from mapping or use generic message
    error_details = HTTP_STATUS_DETAILS.get(
        status_code, f"HTTP error {status_code} - please check your request."
    )

    error_message = (
        f"HTTP error {status_code} when scraping '{url}': {str(e)}. {error_details}"
    )

    # Include the parameters we tried in the error message
    param_summary = " ".join([f"{k}={v}" for k, v in payload.items() if k != "api_key"])
    error_message += f" Parameters used: {param_summary}"

    return McpError(
        ErrorData(
            code=INTERNAL_ERROR,
            message=error_message,
        )
    )


def handle_scraper_connection_error(e: RequestException, url: str) -> McpError:
    """
    Handle connection errors with detailed troubleshooting suggestions.

    Args:
        e: The connection error exception
        url: The URL that was being scraped

    Returns:
        An McpError with detailed error information
    """
    error_message = f"Connection error when scraping '{url}': {str(e)}"
    error_message += " This might be due to network issues, timeout, or the target server being unreachable."

    return McpError(
        ErrorData(
            code=INTERNAL_ERROR,
            message=error_message,
        )
    )


def handle_scraper_generic_error(e: Exception, url: str) -> McpError:
    """
    Handle generic errors during scraping.

    Args:
        e: Any exception
        url: The URL that was being scraped

    Returns:
        An McpError with error information
    """
    error_message = f"Unexpected error when scraping '{url}': {str(e)}"

    return McpError(
        ErrorData(
            code=INTERNAL_ERROR,
            message=error_message,
        )
    )
