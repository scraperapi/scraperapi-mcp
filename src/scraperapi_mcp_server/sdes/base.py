from scraperapi_mcp_server.config import settings
from scraperapi_mcp_server.utils.make_request import make_request

class ScraperEndpoint:
    def __init__(self, endpoint_path, context_template):
        self.endpoint_path = endpoint_path
        self.context_template = context_template

    def call(self, **params):
        payload = {'api_key': settings.API_KEY}
        payload.update(params)
        url = f"{settings.API_URL}{self.endpoint_path}"
        context = self.context_template.format(**params)
        return make_request(url=url, params=payload, context=context) 