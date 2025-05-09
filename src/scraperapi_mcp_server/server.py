from mcp.server.fastmcp import FastMCP
from scraperapi_mcp_server.scraping.models import Scrape
from scraperapi_mcp_server.scraping.basic_scrape import basic_scrape
from scraperapi_mcp_server.scraping.smart_scrape import smart_scrape


mcp = FastMCP("ScraperAPI")


@mcp.tool()
def scrape(params: Scrape) -> str:
    """
    Scrape a URL using ScraperAPI.

    Args:
        params: A Scrape model instance containing all scraping parameters
            - url: The URL to scrape. (required)
            - render: Set to True ONLY if the content you need is missing from the initial HTML response and is loaded dynamically by JavaScript. (optional)
                        For most websites, including many modern ones, the main content is available without JavaScript rendering.
                        **Do not enable unless you have confirmed that the required data is not present in the HTML or accessible via API calls.**
                        Using render=True is slower, more expensive, and may not be necessary even for sites built with JavaScript frameworks.
            - country_code: Two-letter country code to scrape from. (optional)
            - premium: Whether to use premium residential proxies and mobile IPs (optional)
                Using premium proxies costs more, and even more if used in combination with Javascript rendering (render=True)
            - ultra_premium: Whether to activate advanced bypass mechanisms. Cannot combine with premium (optional)
                Using ultra_premium costs more, and even more if used in combination with Javascript rendering (render=True)
            - device_type: Set to 'mobile' or 'desktop' to use specific user agents (optional)

    Returns:
        The scraped content or an error message as a string
    """

    return basic_scrape(
        url=str(params.url),
        render=params.render,
        country_code=params.country_code,
        premium=params.premium,
        ultra_premium=params.ultra_premium,
        device_type=params.device_type,
    )


@mcp.tool()
def scrape_assisted(params: Scrape) -> str:
    """
    Scrape a URL using ScraperAPI with intelligent parameter optimization.

    WARNING: This tool may automatically select more expensive options (such as premium or ultra_premium proxies, or enabling JavaScript rendering) based on domain-specific logic. These choices can significantly increase scraping costs.

    This function implements a smart scraping approach that:
    1. Automatically applies domain-specific optimizations based on historical success patterns
    2. Starts with JavaScript rendering disabled for faster, more efficient scraping
    3. Intelligently retries with rendering enabled if the initial attempt fails
    4. Applies the appropriate proxy type (standard/premium/ultra_premium) based on domain requirements

    Args:
        params: A Scrape model instance containing all scraping parameters
            - url: The URL to scrape. (required)
            - device_type: Set to 'mobile' or 'desktop' to use specific user agents (optional)
            - country_code: Two-letter country code to scrape from. (optional)

    Returns:
        The scraped content or an error message as a string
    """
    return smart_scrape(
        url=str(params.url),
        device_type=params.device_type,
        country_code=params.country_code,
    )
