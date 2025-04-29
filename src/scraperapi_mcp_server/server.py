import requests
from mcp.server.fastmcp import FastMCP
from scraperapi_mcp_server.model import Scrape

def basic_scrape(
        api_key: str,
        url: str, 
        render: bool = None, 
        country_code: str = None, 
        premium: bool = None, 
        ultra_premium: bool = None, 
        device_type: str = None
    ) -> str:
    payload = {
        'api_key': api_key,
        'url': url,
        'output_format': 'markdown'
    }

    optional_params = {
        'render': (render, lambda v: str(v).lower()),
        'country_code': (country_code, str),
        'premium': (premium, lambda v: str(v).lower()),
        'ultra_premium': (ultra_premium, lambda v: str(v).lower()),
        'device_type': (device_type, str)
    }

    for key, (value, formatter) in optional_params.items():
        if value is not None:
            payload[key] = formatter(value)

    try:
        response = requests.get('https://api.scraperapi.com', params=payload)
        return response.text
    except Exception as e:
        return str(e)

mcp = FastMCP("mcp-scraperapi")

@mcp.tool()
def scrape(params: Scrape) -> str:
    """
    Scrape a URL using ScraperAPI.
    
    Args:
        params: A Scrape model instance containing all scraping parameters
        
    Returns:
        The scraped content as a string
    """
    return basic_scrape(
        api_key=params.api_key,
        url=str(params.url),
        render=params.render,
        country_code=params.country_code,
        premium=params.premium,
        ultra_premium=params.ultra_premium,
        device_type=params.device_type
    )