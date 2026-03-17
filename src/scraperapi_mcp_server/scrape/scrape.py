import httpx
from scraperapi_mcp_server.config import settings
from scraperapi_mcp_server.scrape.models import ScrapeError, ScrapeResult
from scraperapi_mcp_server.utils.image_detection import detect_image_mime
import logging


def _format_file_size(size_bytes: int) -> str:
    """Format byte count as a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _get_content_type(response: httpx.Response) -> str:
    """Extract the base content type from a response, without parameters."""
    content_type = response.headers.get("Content-Type", "")
    return content_type.split(";")[0].strip().lower()


async def basic_scrape(
    url: str,
    render: bool = None,
    country_code: str = None,
    premium: bool = None,
    ultra_premium: bool = None,
    device_type: str = None,
    output_format: str = "markdown",
    autoparse: bool = False,
) -> ScrapeResult:
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

        content_type = _get_content_type(response)
        content_size = len(response.content)
        size_limit = settings.IMAGE_SIZE_LIMIT_BYTES
        image_mime = detect_image_mime(content_type, response.content)

        if image_mime:
            content_type = image_mime
            logging.info(
                f"Image response detected: {content_type}, "
                f"size: {_format_file_size(content_size)}"
            )
            if content_size > size_limit:
                logging.warning(
                    f"Image too large ({_format_file_size(content_size)}), "
                    f"limit is {_format_file_size(size_limit)}"
                )
                return ScrapeResult(
                    text=(
                        f"Image found at {url}\n"
                        f"Type: {content_type}\n"
                        f"Size: {_format_file_size(content_size)}\n\n"
                        f"The image exceeds the {_format_file_size(size_limit)} "
                        f"size limit for inline content and cannot be returned directly."
                    )
                )
            return ScrapeResult(image_data=response.content, mime_type=content_type)

        return ScrapeResult(text=response.text)
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
