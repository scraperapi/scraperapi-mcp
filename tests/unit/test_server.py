import pytest
from scraperapi_mcp_server.server import mcp, scrape
from scraperapi_mcp_server.scrape.models import Scrape


class TestMCPServer:
    """Test cases for the MCP server."""

    def test_mcp_server_initialization(self):
        assert mcp.name == "ScraperAPI"

    def test_scrape_tool_success(self, mocker):
        mock_basic_scrape = mocker.patch("scraperapi_mcp_server.server.basic_scrape")
        params = Scrape(url="https://example.com")
        mock_basic_scrape.return_value = "<html><body>Test content</body></html>"

        result = scrape(params)

        assert result == "<html><body>Test content</body></html>"
        mock_basic_scrape.assert_called_once()

    def test_scrape_tool_with_all_params(self, mocker):
        mock_basic_scrape = mocker.patch("scraperapi_mcp_server.server.basic_scrape")
        params = Scrape(
            url="https://test.com",
            render=True,
            country_code="CA",
            premium=True,
            ultra_premium=False,
            device_type="mobile",
        )

        mock_basic_scrape.return_value = "Scraped content"

        result = scrape(params)

        assert result == "Scraped content"
        mock_basic_scrape.assert_called_once()

    def test_scrape_tool_exception_handling(self, mocker):
        mock_basic_scrape = mocker.patch("scraperapi_mcp_server.server.basic_scrape")
        params = Scrape(url="https://example.com")
        mock_basic_scrape.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            scrape(params)
