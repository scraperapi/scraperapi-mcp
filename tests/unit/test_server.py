import pytest
from mcp.server.fastmcp.exceptions import ToolError
from scraperapi_mcp_server.server import mcp, scrape
from scraperapi_mcp_server.scrape.models import Scrape
from scraperapi_mcp_server.scrape.scrape import ScrapeError


class TestMCPServer:
    """Test cases for the MCP server."""

    def test_mcp_server_initialization(self):
        assert mcp.name == "ScraperAPI"

    @pytest.mark.asyncio
    async def test_scrape_tool_success(self, mocker):
        mock_basic_scrape = mocker.patch(
            "scraperapi_mcp_server.server.basic_scrape",
            new_callable=mocker.AsyncMock,
        )
        params = Scrape(url="https://example.com")
        mock_basic_scrape.return_value = "<html><body>Test content</body></html>"

        result = await scrape(params)

        assert result == "<html><body>Test content</body></html>"
        mock_basic_scrape.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_tool_with_all_params(self, mocker):
        mock_basic_scrape = mocker.patch(
            "scraperapi_mcp_server.server.basic_scrape",
            new_callable=mocker.AsyncMock,
        )
        params = Scrape(
            url="https://test.com",
            render=True,
            country_code="CA",
            premium=True,
            ultra_premium=False,
            device_type="mobile",
        )

        mock_basic_scrape.return_value = "Scraped content"

        result = await scrape(params)

        assert result == "Scraped content"
        mock_basic_scrape.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_error_raises_tool_error(self, mocker):
        mock_basic_scrape = mocker.patch(
            "scraperapi_mcp_server.server.basic_scrape",
            new_callable=mocker.AsyncMock,
        )
        params = Scrape(url="https://example.com")
        mock_basic_scrape.side_effect = ScrapeError(
            "HTTP error 403 when scraping 'https://example.com'"
        )

        with pytest.raises(ToolError, match="HTTP error 403"):
            await scrape(params)

    @pytest.mark.asyncio
    async def test_rate_limit_raises_tool_error(self, mocker):
        mocker.patch(
            "scraperapi_mcp_server.server.basic_scrape",
            new_callable=mocker.AsyncMock,
        )
        mocker.patch(
            "scraperapi_mcp_server.server._rate_limiter.acquire",
            side_effect=__import__(
                "scraperapi_mcp_server.utils.rate_limiter",
                fromlist=["RateLimitExceededError"],
            ).RateLimitExceededError("Rate limit exceeded"),
        )
        params = Scrape(url="https://example.com")

        with pytest.raises(ToolError, match="Rate limit exceeded"):
            await scrape(params)
