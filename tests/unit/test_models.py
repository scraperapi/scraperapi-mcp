import pytest
from pydantic import ValidationError
from scraperapi_mcp_server.scrape.models import Scrape


class TestScrapeModel:
    """Test cases for the Scrape model."""

    def test_minimal_scrape_params(self):
        params = Scrape(url="https://example.com")

        # AnyUrl normalizes URLs by adding trailing slash
        assert str(params.url) == "https://example.com/"
        assert params.render is False  # default
        assert params.country_code is None  # default
        assert params.premium is False  # default
        assert params.ultra_premium is False  # default
        assert params.device_type is None  # default

    def test_invalid_url(self):
        with pytest.raises(ValidationError):
            Scrape(url="not-a-url")

    def test_empty_url(self):
        with pytest.raises(ValidationError):
            Scrape(url="")
