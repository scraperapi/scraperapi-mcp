# src/scraperapi_mcp_server/scraping/smart_scrape.py
from scraperapi_mcp_server.scraping.basic_scrape import basic_scrape
from scraperapi_mcp_server.utils.domain_based_suggestions import (
    apply_domain_suggestions,
)


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

    return basic_scrape(
        url=url,
        render=domain_params["render"],
        country_code=domain_params["country_code"],
        premium=domain_params["premium"],
        ultra_premium=domain_params["ultra_premium"],
        device_type=domain_params["device_type"],
    )
