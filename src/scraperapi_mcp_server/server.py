import re
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import (
    ErrorData,
    INTERNAL_ERROR,
)
from scraperapi_mcp_server.scraping.models import Scrape
from scraperapi_mcp_server.utils.country_codes import COUNTRY_CODES
from scraperapi_mcp_server.scraping.scrape import basic_scrape


mcp = FastMCP("mcp-scraperapi")


@mcp.tool()
def scrape(params: Scrape) -> str:
    """
    Scrape a URL using ScraperAPI.
    
    Args:
        params: A Scrape model instance containing all scraping parameters
            - url: The URL to scrape. (required)
            - render: Set to True ONLY if the content you need is missing from the initial HTML response and is loaded dynamically by JavaScript. 
                        For most websites, including many modern ones, the main content is available without JavaScript rendering.
                        **Do not enable unless you have confirmed that the required data is not present in the HTML or accessible via API calls.**
                        Using render=True is slower, more expensive, and may not be necessary even for sites built with JavaScript frameworks. (optional)
            - country_code: Two-letter country code to scrape from. (optional)
            - premium: Whether to use premium residential proxies and mobile IPs (optional)
            - ultra_premium: Whether to activate advanced bypass mechanisms. Cannot combine with premium (optional)
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
        params: A natural language string describing what to scrape or fetch and how.
            Example: "Scrape https://example.com with JavaScript rendering enabled from a mobile device in the US"
            
            **JavaScript rendering (render=True) should only be enabled if you have confirmed that the required content is NOT present in the initial HTML or via API calls.**
            Many modern websites, including those built with JavaScript frameworks, still expose their main content in the HTML or via XHR/API endpoints.
            Enabling JavaScript rendering is slower, more expensive, and should be a last resort.
        
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