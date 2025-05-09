from mcp.server.fastmcp import FastMCP
from scraperapi_mcp_server.scraping.models import Scrape
from scraperapi_mcp_server.scraping.basic_scrape import basic_scrape
from scraperapi_mcp_server.scraping.smart_scrape import smart_scrape
from scraperapi_mcp_server.utils.prompts import (
    SCRAPE_PROMPT_TEMPLATE,
    SCRAPE_ASSISTED_PROMPT_TEMPLATE,
)

mcp = FastMCP(
    name="ScraperAPI",
    instructions=f"scrape:\n{SCRAPE_PROMPT_TEMPLATE}\n\nscrape_assisted:\n{SCRAPE_ASSISTED_PROMPT_TEMPLATE}",
)


# @mcp.tool()
# def scrape(params: Scrape) -> str:
#     """
#     Execute a web scrape using ScraperAPI with the specified parameters.

#     Parameters:
#         params: Scrape model containing:
#             url: Target URL to scrape (required)
#             render: Enable JavaScript rendering only when needed for dynamic content (default: False)
#                     Set to True ONLY if the content you need is missing from the initial HTML response and is loaded dynamically by JavaScript.
#                     For most websites, including many modern ones, the main content is available without JavaScript rendering.
#             country_code: Two-letter country code for geo-specific scraping
#             premium: Use premium residential/mobile proxies for higher success rate (costs more, incompatible with ultra_premium)
#             ultra_premium: Activate advanced bypass mechanisms (costs more, incompatible with premium)
#             device_type: 'mobile' or 'desktop' for device-specific user agents

#     Returns:
#         Scraped content as a string
#     """

#     return basic_scrape(
#         url=str(params.url),
#         render=params.render,
#         country_code=params.country_code,
#         premium=params.premium,
#         ultra_premium=params.ultra_premium,
#         device_type=params.device_type,
#     )


@mcp.tool()
def scrape_assisted(params: Scrape) -> str:
    """
    Interactive scraping assistant that guides users through ScraperAPI parameter selection.

    This tool walks users through each parameter choice, explaining options and tradeoffs
    while providing feedback on selections. Designed for new users or complex scraping tasks.

    Parameters:
        params: Initial Scrape model with:
            url: Target URL to scrape (required)
            country_code: Optional two-letter country code
            device_type: Optional 'mobile' or 'desktop' setting

    Returns:
        Scraped content as a string after interactive parameter selection
    """

    return smart_scrape(
        url=str(params.url),
        device_type=params.device_type,
        country_code=params.country_code,
    )
