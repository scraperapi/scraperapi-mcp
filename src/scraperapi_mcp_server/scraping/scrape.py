from scraperapi_mcp_server.config import settings
from scraperapi_mcp_server.utils.make_request import make_request

def basic_scrape(
        url: str, 
        render: bool = None, 
        country_code: str = None, 
        premium: bool = None, 
        ultra_premium: bool = None, 
        device_type: str = None
    ) -> str:
    payload = {
        'api_key': settings.API_KEY,
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

    return make_request(
        url=settings.API_URL,
        params=payload,
        context=f"scraping '{url}'"
    )