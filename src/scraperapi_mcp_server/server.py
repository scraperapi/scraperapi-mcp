from mcp.server.fastmcp import FastMCP
from scraperapi_mcp_server.scrape.models import Scrape
from scraperapi_mcp_server.scrape.scrape import basic_scrape
import logging

mcp = FastMCP("ScraperAPI")


@mcp.tool()
def scrape(params: Scrape) -> str:
    """
    Execute a web scrape using ScraperAPI with the specified parameters.

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

    Returns:
        Scraped content as a string
    """

    logging.info(f"Invoking scrape tool with params: {params}")
    try:
        result = basic_scrape(
            url=str(params.url),
            render=params.render,
            country_code=params.country_code,
            premium=params.premium,
            ultra_premium=params.ultra_premium,
            device_type=params.device_type,
        )
        logging.info(f"Scrape tool completed for URL: {params.url}")
        return result
    except Exception as e:
        logging.error(
            f"Scrape tool failed for URL: {params.url}. Error: {e}", exc_info=True
        )
        raise
