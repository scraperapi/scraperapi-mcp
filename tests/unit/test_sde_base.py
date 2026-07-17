from typing import Annotated, Optional

import pytest
from pydantic import Field, ValidationError

from scraperapi_mcp_server.sdes.base import (
    BaseSdeParams,
    SdeOutputFormat,
    fetch_sde,
)


class _ExampleParams(BaseSdeParams):
    """A stand-in family model exercising required input + an aliased field."""

    query: Annotated[str, Field(description="Search query")]
    sort_by: Annotated[
        Optional[str],
        Field(default=None, serialization_alias="s", description="Sort order"),
    ]


class TestQueryParams:
    def test_defaults_only_emit_output_format(self):
        params = _ExampleParams(query="laptops")
        assert params.query_params() == {"query": "laptops", "output_format": "json"}

    def test_enum_unwrapped_and_none_dropped(self):
        params = _ExampleParams(query="laptops", output_format=SdeOutputFormat.CSV)
        result = params.query_params()
        assert result["output_format"] == "csv"
        assert "tld" not in result
        assert "country_code" not in result

    def test_serialization_alias_applied(self):
        params = _ExampleParams(query="laptops", sort_by="price-asc")
        result = params.query_params()
        assert result["s"] == "price-asc"
        assert "sort_by" not in result

    def test_optional_common_params_included_when_set(self):
        params = _ExampleParams(query="x", tld="co.uk", country_code="gb")
        result = params.query_params()
        assert result["tld"] == "co.uk"
        assert result["country_code"] == "gb"

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError):
            _ExampleParams(query="x", bogus="y")


class TestFetchSde:
    @pytest.mark.asyncio
    async def test_builds_url_and_injects_auth(self, mocker):
        mock_response = mocker.Mock()
        mock_response.text = '{"results": []}'
        mock_get = mocker.patch(
            "scraperapi_mcp_server.sdes.base.http.get",
            new_callable=mocker.AsyncMock,
            return_value=mock_response,
        )
        mock_settings = mocker.patch("scraperapi_mcp_server.sdes.base.settings")
        mock_settings.API_KEY = "test_api_key"
        mock_settings.API_URL = "https://api.scraperapi.com"
        mock_settings.SCRAPER_SDK = "mcp-server"

        result = await fetch_sde(
            "/structured/amazon/search", _ExampleParams(query="laptops")
        )

        assert result == '{"results": []}'
        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        assert (
            mock_get.call_args.args[0]
            == "https://api.scraperapi.com/structured/amazon/search"
        )
        assert kwargs["params"] == {
            "query": "laptops",
            "output_format": "json",
            "api_key": "test_api_key",
            "scraper_sdk": "mcp-server",
        }
