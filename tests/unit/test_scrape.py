import pytest
import requests
from scraperapi_mcp_server.scrape.scrape import basic_scrape


class TestBasicScrape:
    def test_basic_scrape_success(self, mocker):
        mock_settings = mocker.patch("scraperapi_mcp_server.scrape.scrape.settings")
        mock_get = mocker.patch("scraperapi_mcp_server.scrape.scrape.requests.get")

        mock_settings.API_KEY = "test_api_key"
        mock_settings.API_URL = "https://api.scraperapi.com"
        mock_settings.API_TIMEOUT_SECONDS = 30

        mock_response = mocker.Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = basic_scrape("https://example.com")

        assert result == "<html><body>Test content</body></html>"
        mock_get.assert_called_once_with(
            "https://api.scraperapi.com",
            params={
                "api_key": "test_api_key",
                "url": "https://example.com",
                "output_format": "markdown",
                "scraper_sdk": "mcp-server",
            },
            timeout=30,
        )

    def test_basic_scrape_error(self, mocker):
        mock_settings = mocker.patch("scraperapi_mcp_server.scrape.scrape.settings")
        mock_get = mocker.patch("scraperapi_mcp_server.scrape.scrape.requests.get")

        mock_settings.API_KEY = "test_api_key"
        mock_settings.API_URL = "https://api.scraperapi.com"
        mock_settings.API_TIMEOUT_SECONDS = 30

        mock_get.side_effect = requests.ConnectionError("Connection failed")

        with pytest.raises(Exception):
            basic_scrape("https://example.com")
