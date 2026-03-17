import pytest
from scraperapi_mcp_server.server import scrape
from scraperapi_mcp_server.scrape.models import Scrape
from scraperapi_mcp_server.scrape.models import ScrapeResult


class TestIntegration:
    """Integration test cases."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_scrape_flow(self, mocker):
        mock_basic_scrape = mocker.patch(
            "scraperapi_mcp_server.server.basic_scrape",
            new_callable=mocker.AsyncMock,
        )
        mock_basic_scrape.return_value = ScrapeResult(
            text="<html><body>Integration test content</body></html>"
        )

        params = Scrape(
            url="https://example.com",
            render=True,
            country_code="US",
            premium=True,
            ultra_premium=False,
            device_type="mobile",
        )

        result = await scrape(params)

        assert result == "<html><body>Integration test content</body></html>"

        mock_basic_scrape.assert_called_once()
        call_kwargs = mock_basic_scrape.call_args[1]
        assert call_kwargs["url"] == "https://example.com/"
        assert call_kwargs["render"] is True
        assert call_kwargs["country_code"] == "us"
        assert call_kwargs["premium"] is True
        assert call_kwargs["ultra_premium"] is False

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_propagation_through_layers(self, mocker):
        mock_basic_scrape = mocker.patch(
            "scraperapi_mcp_server.server.basic_scrape",
            new_callable=mocker.AsyncMock,
        )
        mock_basic_scrape.side_effect = Exception("Integration test error")

        params = Scrape(url="https://example.com")

        with pytest.raises(Exception, match="Integration test error"):
            await scrape(params)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multiple_scrape_requests(self, mocker):
        mock_basic_scrape = mocker.patch(
            "scraperapi_mcp_server.server.basic_scrape",
            new_callable=mocker.AsyncMock,
        )
        mock_basic_scrape.side_effect = [
            ScrapeResult(text="Content from first request"),
            ScrapeResult(text="Content from second request"),
            ScrapeResult(text="Content from third request"),
        ]

        params1 = Scrape(url="https://example1.com")
        params2 = Scrape(url="https://example2.com", render=True)
        params3 = Scrape(url="https://example3.com", premium=True)

        result1 = await scrape(params1)
        result2 = await scrape(params2)
        result3 = await scrape(params3)

        assert result1 == "Content from first request"
        assert result2 == "Content from second request"
        assert result3 == "Content from third request"

        assert mock_basic_scrape.call_count == 3

        calls = mock_basic_scrape.call_args_list
        assert calls[0][1]["url"] == "https://example1.com/"
        assert calls[1][1]["url"] == "https://example2.com/"
        assert calls[1][1]["render"] is True
        assert calls[2][1]["url"] == "https://example3.com/"
        assert calls[2][1]["premium"] is True
