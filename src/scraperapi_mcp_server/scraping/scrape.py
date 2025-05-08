import requests
from requests.exceptions import RequestException, HTTPError as RequestsHTTPError
from mcp.shared.exceptions import McpError
from scraperapi_mcp_server.config import settings
from mcp.types import (
    ErrorData,
    INTERNAL_ERROR,
)

def basic_scrape(
        url: str, 
        render: bool = None, 
        country_code: str = None, 
        premium: bool = None, 
        ultra_premium: bool = None, 
        device_type: str = None
    ) -> str:
    payload = {
        'api_key': settings.API_KEY,
        'url': url,
        'output_format': 'markdown',
        'scraper_sdk': 'mcp-server'
    }

    optional_params = {
        'render': (render, lambda v: str(v).lower()),
        'country_code': (country_code, str),
        'premium': (premium, lambda v: str(v).lower()),
        'ultra_premium': (ultra_premium, lambda v: str(v).lower()),
        'device_type': (device_type, str)
    }

    for key, (value, formatter) in optional_params.items():
        if value is not None:
            payload[key] = formatter(value)

    try:
        response = requests.get(settings.API_URL, params=payload, timeout=settings.API_TIMEOUT_SECONDS)
        response.raise_for_status()
        
        return response.text
    except RequestsHTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') else 500
        error_message = f"HTTP error {status_code} when scraping '{url}': {str(e)}"
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=error_message,
        ))
    except RequestException as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Connection error when scraping '{url}': {str(e)}",
        ))
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Unexpected error when scraping '{url}': {str(e)}",
        ))