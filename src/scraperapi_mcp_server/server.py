import re
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import (
    ErrorData,
    INTERNAL_ERROR,
)
from scraperapi_mcp_server.model import Scrape
from scraperapi_mcp_server.country_codes import COUNTRY_CODES
from scraperapi_mcp_server.scrape import basic_scrape


mcp = FastMCP("mcp-scraperapi")


@mcp.tool()
def scrape(params: Scrape) -> str:
    """
    Scrape a URL using ScraperAPI.
    
    Args:
        params: A Scrape model instance containing all scraping parameters
            - url: The URL to scrape (required)
            - render: Set to True ONLY if the page requires JavaScript to load content. 
                      Default is False, which is sufficient for most static websites.
            - country_code: Two-letter country code to scrape from (optional)
            - premium: Whether to use premium proxies (optional)
            - ultra_premium: Whether to use ultra premium proxies (optional)
            - device_type: Set to 'mobile' or 'desktop' to use specific user agents (optional)
        
    Returns:
        The scraped content as a string
    """
    return basic_scrape(
        url=str(params.url),
        render=params.render,
        country_code=params.country_code,
        premium=params.premium,
        ultra_premium=params.ultra_premium,
        device_type=params.device_type
    )


@mcp.prompt()
def scrape_prompt(params: str) -> str:
    """
    Scrape a URL using ScraperAPI based on natural language instructions.
    
    Args:
        params: A natural language string describing what to scrape and how.
                Example: "Scrape https://example.com with JavaScript rendering enabled from a mobile device in the US"
                
                To enable JavaScript rendering, explicitly mention "javascript rendering" or "render javascript".
                By default, JavaScript rendering is OFF for better performance and lower costs.
        
    Returns:
        The scraped content as a string
    """
    scrape_params = Scrape(
        url="",  # This will be set based on the prompt
        render=False,
        country_code=None,
        premium=False,
        ultra_premium=False,
        device_type=None
    )
    
    url_match = re.search(r'https?://[^\s]+', params)
    if not url_match:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message="No URL found in the prompt. Please provide a valid URL to scrape.",
        ))
    scrape_params.url = url_match.group(0)
    
    # Only enable JavaScript rendering if explicitly mentioned
    js_keywords = ["javascript rendering", "render javascript", "enable javascript", "with javascript", "using javascript"]
    if any(keyword in params.lower() for keyword in js_keywords):
        scrape_params.render = True
    
    if "mobile" in params.lower():
        scrape_params.device_type = "mobile"
    elif "desktop" in params.lower():
        scrape_params.device_type = "desktop"
    
    if "premium" in params.lower():
        if "ultra" in params.lower():
            scrape_params.ultra_premium = True
        else:
            scrape_params.premium = True
    
    # Extract country code if mentioned
    for country, code in COUNTRY_CODES.items():
        if country in params.lower():
            scrape_params.country_code = code
            break
    
    return scrape(scrape_params)