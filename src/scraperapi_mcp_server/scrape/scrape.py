import httpx
from scraperapi_mcp_server.config import settings
import logging


async def basic_scrape(
    url: str,
    render: bool = None,
    country_code: str = None,
    premium: bool = None,
    ultra_premium: bool = None,
    device_type: str = None,
    output_format: str = "markdown",
    autoparse: bool = False,
) -> str:
    logging.info(f"Starting scrape for URL: {url}")
    payload = {
        "api_key": settings.API_KEY,
        "url": url,
        "scraper_sdk": "mcp-server",
    }
    optional_params = {
        "render": (render, lambda v: str(v).lower()),
        "country_code": (country_code, str),
        "premium": (premium, lambda v: str(v).lower()),
        "ultra_premium": (ultra_premium, lambda v: str(v).lower()),
        "device_type": (
            device_type,
            lambda v: v.value if hasattr(v, "value") else str(v),
        ),
        "output_format": (
            output_format,
            lambda v: v.value if hasattr(v, "value") else str(v),
        ),
        "autoparse": (autoparse, lambda v: str(v).lower()),
    }
    for key, (value, formatter) in optional_params.items():
        if value is not None:
            payload[key] = formatter(value)
            logging.debug(f"Added optional param: {key}={payload[key]}")
    try:
        logging.info(f"Sending request to {settings.API_URL}")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                settings.API_URL,
                params=payload,
                timeout=settings.API_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        logging.info(f"Scrape successful for URL: {url}")
        return response.text
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        param_summary = " ".join(
            f"{k}={v}" for k, v in payload.items() if k != "api_key"
        )
        error_message = f"HTTP error {status_code} when scraping '{url}'. Parameters used: {param_summary}"
        logging.error(f"basic_scrape: {error_message}", exc_info=True)
        raise ScrapeError(error_message) from e
    except httpx.RequestError as e:
        error_message = f"Connection error when scraping '{url}': {e}"
        logging.error(f"basic_scrape: {error_message}", exc_info=True)
        raise ScrapeError(error_message) from e
    except Exception as e:
        error_message = f"Unexpected error when scraping '{url}': {e}"
        logging.error(f"basic_scrape: {error_message}", exc_info=True)
        raise ScrapeError(error_message) from e


class ScrapeError(Exception):
    """Raised when a scrape operation fails. Carries an actionable error message."""

    pass
