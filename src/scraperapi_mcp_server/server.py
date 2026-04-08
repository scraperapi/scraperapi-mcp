from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations
from scraperapi_mcp_server.scrape.models import Scrape
from scraperapi_mcp_server.scrape.scrape import basic_scrape
from scraperapi_mcp_server.scrape.models import ScrapeError
from scraperapi_mcp_server.config import settings, ApiKeyEnvVarNotSetError
from scraperapi_mcp_server.utils.rate_limiter import RateLimiter, RateLimitExceededError
import logging

mcp = FastMCP("ScraperAPI")

_rate_limiter = RateLimiter(
    max_calls=settings.RATE_LIMIT_MAX_CALLS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)


@mcp.tool(
    name="scrape",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def scrape(params: Scrape) -> str:
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
    try:
        settings.validate_api_key()
    except ApiKeyEnvVarNotSetError as e:
        raise ToolError(str(e)) from e
    try:
        _rate_limiter.acquire()
    except RateLimitExceededError as e:
        raise ToolError(str(e)) from e
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
