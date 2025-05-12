# src/scraperapi_mcp_server/scraping/smart_scrape.py
from mcp.shared.exceptions import McpError
from scraperapi_mcp_server.scraping.basic_scrape import basic_scrape
from scraperapi_mcp_server.utils.domain_based_suggestions import (
    apply_domain_suggestions,
)
from scraperapi_mcp_server.utils.exceptions import handle_scraper_generic_error


def smart_scrape(
    url: str, render: str, device_type: str = None, country_code: str = None
) -> str:
    """
    Implements scraping with domain-specific parameters based on historical usage data.

    Args:
        url: The URL to scrape
        render: Enable JavaScript rendering only when needed for dynamic content (default: False)
                Set to True ONLY if the content you need is missing from the initial HTML response and is loaded dynamically by JavaScript.
                For most websites, including many modern ones, the main content is available without JavaScript rendering.
        device_type: Optional device type (mobile/desktop)
        country_code: Optional country code

    Returns:
        The scraped content as a string
    """
    # Apply domain-specific parameter suggestions
    domain_params = apply_domain_suggestions(
        url,
        {
            "render": render,
            "country_code": country_code,
            "premium": None,
            "ultra_premium": None,
            "device_type": device_type,
        },
    )

    try:
        result = basic_scrape(
            url=url,
            render=domain_params["render"],
            country_code=domain_params["country_code"],
            premium=domain_params["premium"],
            ultra_premium=domain_params["ultra_premium"],
            device_type=domain_params["device_type"],
        )

        if not result or not result.strip():
            raise Exception("Received empty response from ScraperAPI")

        return result

    except McpError:
        raise
    except Exception as e:
        raise handle_scraper_generic_error(e, url)
