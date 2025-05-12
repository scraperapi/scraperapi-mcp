# src/scraperapi_mcp_server/scraping/smart_scrape.py
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR
from scraperapi_mcp_server.scraping.basic_scrape import basic_scrape
from scraperapi_mcp_server.utils.domain_based_suggestions import (
    apply_domain_suggestions,
)


def smart_scrape(url: str, device_type: str = None, country_code: str = None) -> str:
    """
    Implements smart scraping logic according to company guidelines:
    1. Always start with render=False
    2. Apply domain-specific parameter suggestions
    3. If a domain is in both premium and ultra_premium, prioritize premium
    4. If no results, retry with render=True


    Args:
        url: The URL to scrape
        device_type: Optional device type (mobile/desktop)
        country_code: Optional country code

    Returns:
        The scraped content as a string
    """
    # Get domain-specific parameter suggestions
    domain_params = apply_domain_suggestions(
        url,
        {
            "render": False,  # Always start with render=False
            "country_code": country_code,
            "premium": None,  # Let domain suggestions determine this
            "ultra_premium": None,  # Let domain suggestions determine this
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

        if result and len(result.strip()) > 0:
            return result
    except McpError as e:
        first_attempt_error = e
        try:
            # If first attempt fails, retry with render=True but keep other parameters
            domain_params["render"] = True

            return basic_scrape(
                url=url,
                render=domain_params["render"],
                country_code=domain_params["country_code"],
                premium=domain_params["premium"],
                ultra_premium=domain_params["ultra_premium"],
                device_type=domain_params["device_type"],
            )
        except McpError as e:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to scrape '{url}' with both render=False and render=True: \n Without rendering: { str(first_attempt_error)} \n With rendering: {str(e)}",
                )
            )
