import httpx
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations
from scraperapi_mcp_server.config import settings
from scraperapi_mcp_server.execution import require_ready
from scraperapi_mcp_server.scrape.models import Scrape, ScrapeError, ScrapeResult
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
        logging.exception(f"basic_scrape: {error_message}")
        raise ScrapeError(error_message) from e
    except httpx.RequestError as e:
        error_message = f"Connection error when scraping '{url}': {e}"
        logging.exception(f"basic_scrape: {error_message}")
        raise ScrapeError(error_message) from e
    except Exception as e:
        error_message = f"Unexpected error when scraping '{url}': {e}"
        logging.exception(f"basic_scrape: {error_message}")
        raise ScrapeError(error_message) from e


_SCRAPE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


async def scrape_tool(params: Scrape) -> str:
    """Scrape a web page or image from any URL using the ScraperAPI services, bypassing anti-bot protections.

    Use this tool to retrieve the content of a web page or download an image from a given URL. It handles CAPTCHAs, IP blocks, and rate limits automatically via ScraperAPI's proxy infrastructure.

    When to use:
    - Extracting text content from web pages (articles, product listings, search results, etc.)
    - Downloading images from URLs (returns the image directly if the URL points to an image file)
    - Scraping geo-restricted content by specifying a country code
    - Retrieving structured data (CSV/JSON) from supported websites with autoparse enabled

    When NOT to use:
    - For URLs that require authentication or login (ScraperAPI cannot access authenticated sessions)
    - For non-HTTP resources (e.g., FTP, local files)
    - When you already have the content and don't need to fetch it again (this tool is rate-limited)

    Args:
        params (Scrape): Validated input parameters containing:
            - url (AnyUrl): The full URL to scrape (e.g. 'https://example.com/page')
            - render (bool): Enable JavaScript rendering for dynamic pages (default: false)
            - country_code (Optional[str]): ISO 3166-1 alpha-2 code for geo-targeted scraping (e.g. 'us', 'gb')
            - premium (bool): Use premium proxies for difficult sites (default: false)
            - ultra_premium (bool): Use ultra-premium proxies for heavily protected sites (default: false)
            - device_type (Optional[DeviceType]): 'mobile' or 'desktop' User-Agent emulation
            - output_format (OutputFormat): Response format — 'markdown' (default), 'text', 'csv', or 'json'
            - autoparse (bool): Enable structured data extraction for supported sites (default: false)

    Returns:
        For web pages: str containing the page content in the requested output_format.
            - 'markdown': Clean, readable markdown extracted from the page HTML
            - 'text': Plain text without any formatting
            - 'csv': Comma-separated values (requires autoparse=true on supported sites)
            - 'json': JSON string (requires autoparse=true on supported sites)
        For image URLs: Image object with binary image data (JPEG, PNG, GIF, WebP, BMP, TIFF, or SVG).
            Images larger than ~700KB are rejected.

    Raises:
        ToolError: If the API key is not configured, rate limit is exceeded, or the scrape operation fails.
    """
    logging.info(f"Invoking scrape tool with params: {params}")
    require_ready()
    try:
        result = await basic_scrape(
            url=str(params.url),
            render=params.render,
            country_code=params.country_code,
            premium=params.premium,
            ultra_premium=params.ultra_premium,
            device_type=params.device_type,
            output_format=params.output_format,
            autoparse=params.autoparse,
        )
        logging.info(f"Scrape tool completed for URL: {params.url}")

        if result.is_image:
            logging.info(
                f"Returning image content ({result.mime_type}) for URL: {params.url}"
            )
            # Image() expects short format name (e.g. "jpeg"), not full MIME type
            image_format = result.mime_type.removeprefix("image/")
            return Image(data=result.image_data, format=image_format)

        return result.text
    except ScrapeError as e:
        raise ToolError(str(e)) from e


def register_scrape_tool(mcp: FastMCP) -> None:
    """Register the scrape tool on the given MCP server."""
    mcp.tool(name="scrape", annotations=_SCRAPE_ANNOTATIONS)(scrape_tool)
