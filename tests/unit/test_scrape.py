import pytest
import httpx
from scraperapi_mcp_server.scrape.scrape import basic_scrape, ScrapeError


class TestBasicScrape:
    @pytest.mark.asyncio
    async def test_basic_scrape_success(self, mocker):
        mock_settings = mocker.patch("scraperapi_mcp_server.scrape.scrape.settings")
        mock_settings.API_KEY = "test_api_key"
        mock_settings.API_URL = "https://api.scraperapi.com"
        mock_settings.API_TIMEOUT_SECONDS = 30

        mock_response = mocker.Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status.return_value = None

        mock_client = mocker.AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

        mocker.patch(
            "scraperapi_mcp_server.scrape.scrape.httpx.AsyncClient",
            return_value=mock_client,
        )

        result = await basic_scrape("https://example.com")

        assert result == "<html><body>Test content</body></html>"
        mock_client.get.assert_called_once_with(
            "https://api.scraperapi.com",
            params={
                "api_key": "test_api_key",
                "url": "https://example.com",
                "output_format": "markdown",
                "autoparse": "false",
                "scraper_sdk": "mcp-server",
            },
            timeout=30,
        )

    @pytest.mark.asyncio
    async def test_basic_scrape_error(self, mocker):
        mock_settings = mocker.patch("scraperapi_mcp_server.scrape.scrape.settings")
        mock_settings.API_KEY = "test_api_key"
        mock_settings.API_URL = "https://api.scraperapi.com"
        mock_settings.API_TIMEOUT_SECONDS = 30

        mock_client = mocker.AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

        mocker.patch(
            "scraperapi_mcp_server.scrape.scrape.httpx.AsyncClient",
            return_value=mock_client,
        )

        with pytest.raises(ScrapeError, match="Connection error"):
            await basic_scrape("https://example.com")
