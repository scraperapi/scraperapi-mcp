import pytest
from pydantic import ValidationError
from scraperapi_mcp_server.scrape.models import Scrape, OutputFormat, DeviceType


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
        assert params.output_format == OutputFormat.MARKDOWN
        assert params.autoparse is False

    def test_invalid_url(self):
        with pytest.raises(ValidationError):
            Scrape(url="not-a-url")

    def test_empty_url(self):
        with pytest.raises(ValidationError):
            Scrape(url="")

    def test_invalid_output_format(self):
        with pytest.raises(ValidationError, match="Input should be"):
            Scrape(url="https://example.com", output_format="xml")

    def test_valid_output_formats(self):
        for fmt in ["text", "markdown", "csv", "json"]:
            params = Scrape(url="https://example.com", output_format=fmt)
            assert params.output_format.value == fmt

    def test_invalid_device_type(self):
        with pytest.raises(ValidationError, match="Input should be"):
            Scrape(url="https://example.com", device_type="tablet")

    def test_valid_device_types(self):
        for dt in ["mobile", "desktop"]:
            params = Scrape(url="https://example.com", device_type=dt)
            assert params.device_type.value == dt

    def test_premium_and_ultra_premium_mutually_exclusive(self):
        with pytest.raises(
            ValidationError, match="premium and ultra_premium cannot both be enabled"
        ):
            Scrape(url="https://example.com", premium=True, ultra_premium=True)

    def test_premium_alone_is_valid(self):
        params = Scrape(url="https://example.com", premium=True)
        assert params.premium is True
        assert params.ultra_premium is False

    def test_ultra_premium_alone_is_valid(self):
        params = Scrape(url="https://example.com", ultra_premium=True)
        assert params.ultra_premium is True
        assert params.premium is False

    def test_invalid_country_code(self):
        with pytest.raises(ValidationError, match="Invalid country_code"):
            Scrape(url="https://example.com", country_code="zz")

    def test_valid_country_code(self):
        params = Scrape(url="https://example.com", country_code="us")
        assert params.country_code == "us"

    def test_country_code_name_resolves(self):
        params = Scrape(url="https://example.com", country_code="brazil")
        assert params.country_code == "br"

    def test_country_code_case_insensitive(self):
        params = Scrape(url="https://example.com", country_code="US")
        assert params.country_code == "us"
