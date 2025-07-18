import pytest
from scraperapi_mcp_server.server import scrape
from scraperapi_mcp_server.scrape.models import Scrape


class TestIntegration:
    """Integration test cases."""

    @pytest.mark.integration
    def test_full_scrape_flow(self, mocker):
        mock_basic_scrape = mocker.patch("scraperapi_mcp_server.server.basic_scrape")
        mock_basic_scrape.return_value = (
            "<html><body>Integration test content</body></html>"
        )

        params = Scrape(
            url="https://example.com",
            render=True,
            country_code="US",
            premium=True,
            ultra_premium=False,
            device_type="mobile",
        )

        result = scrape(params)

        assert result == "<html><body>Integration test content</body></html>"

        mock_basic_scrape.assert_called_once_with(
            url="https://example.com/",
            render=True,
            country_code="US",
            premium=True,
            ultra_premium=False,
            device_type="mobile",
        )

    @pytest.mark.integration
    def test_error_propagation_through_layers(self, mocker):
        mock_basic_scrape = mocker.patch("scraperapi_mcp_server.server.basic_scrape")
        mock_basic_scrape.side_effect = Exception("Integration test error")

        params = Scrape(url="https://example.com")

        with pytest.raises(Exception, match="Integration test error"):
            scrape(params)

    @pytest.mark.integration
    def test_multiple_scrape_requests(self, mocker):
        mock_basic_scrape = mocker.patch("scraperapi_mcp_server.server.basic_scrape")
        mock_basic_scrape.side_effect = [
            "Content from first request",
            "Content from second request",
            "Content from third request",
        ]

        params1 = Scrape(url="https://example1.com")
        params2 = Scrape(url="https://example2.com", render=True)
        params3 = Scrape(url="https://example3.com", premium=True)

        result1 = scrape(params1)
        result2 = scrape(params2)
        result3 = scrape(params3)

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
