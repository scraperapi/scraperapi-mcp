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
    """
    Execute a web scrape using ScraperAPI with the specified parameters.
    Supports both text and image URLs. When the target URL points to an image,
    the image content is returned directly.

    Parameters:
        params: Scrape model containing:
            url: Target URL to scrape (required)
            render: Enable JavaScript rendering only when needed for dynamic content (default: False)
                    Set to True ONLY if the content you need is missing from the initial HTML response and is loaded dynamically by JavaScript.
                    For most websites, including many modern ones, the main content is available without JavaScript rendering.
            country_code: Two-letter country code for geo-specific scraping
            premium: Use premium residential/mobile proxies for higher success rate (costs more, incompatible with ultra_premium)
            ultra_premium: Activate advanced bypass mechanisms (costs more, incompatible with premium)
            device_type: 'mobile' or 'desktop' for device-specific user agents
            output_format: 'text', 'markdown', 'csv' or 'json' for the output format (default: 'markdown')
            autoparse: boolean to enable automatic parsing of the content for select websites (default: False).
                    Set to true if the output_format is 'csv' or 'json'. Only available for certain websites.

    Returns:
        Scraped content as text, csv or json
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
