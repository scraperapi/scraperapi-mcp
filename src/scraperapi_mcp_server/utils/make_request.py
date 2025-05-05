import requests
from scraperapi_mcp_server.config import settings
from requests.exceptions import RequestException, HTTPError as RequestsHTTPError
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR


def make_request(url: str, params: dict, context: str = "request") -> str:
    """
    Make an HTTP GET request with unified error handling.

    Args:
        url (str): The URL to request.
        params (dict): Query parameters for the request.
        context (str): Context string for error messages (e.g., 'scraping', 'fetching Ebay product').

    Returns:
        str: The response text.
    """
    try:
        response = requests.get(url, params=params, timeout=settings.API_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.text
    except RequestsHTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') else 500
        error_message = f"HTTP error {status_code} when {context}: {str(e)}"
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=error_message,
        ))
    except RequestException as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Connection error when {context}: {str(e)}",
        ))
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Unexpected error when {context}: {str(e)}",
        )) 