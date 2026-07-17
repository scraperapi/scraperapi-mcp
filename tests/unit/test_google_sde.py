import pytest
from pydantic import ValidationError

from scraperapi_mcp_server.sdes.base import SdeOutputFormat
from scraperapi_mcp_server.sdes.google import (
    GoogleMapsSearchParams,
    GoogleSearchParams,
    GoogleTimePeriod,
)


class TestGoogleQueryParams:
    def test_search_defaults(self):
        params = GoogleSearchParams(query="laptops")
        assert params.query_params() == {"query": "laptops", "output_format": "json"}

    def test_search_full_serialization(self):
        params = GoogleSearchParams(
            query="laptops",
            country_code="gb",
            num=20,
            start=10,
            time_period=GoogleTimePeriod.LAST_DAY,
            include_html=True,
            output_format=SdeOutputFormat.CSV,
        )
        result = params.query_params()
        assert result == {
            "query": "laptops",
            "country_code": "gb",
            "num": 20,
            "start": 10,
            "time_period": "1D",
            "include_html": "true",
            "output_format": "csv",
        }

    def test_bool_false_serialized_lowercase(self):
        params = GoogleSearchParams(query="x", include_html=False)
        assert params.query_params()["include_html"] == "false"

    def test_maps_has_no_serp_pagination_fields(self):
        # latitude/longitude/zoom belong to maps; uule/num/hl/gl/start do not.
        params = GoogleMapsSearchParams(
            query="coffee", latitude=40.71, longitude=-74.0, zoom=12
        )
        result = params.query_params()
        assert result["latitude"] == 40.71
        assert result["zoom"] == 12
        assert "num" not in GoogleMapsSearchParams.model_fields

    def test_num_must_be_positive(self):
        with pytest.raises(ValidationError):
            GoogleSearchParams(query="x", num=0)

    def test_extra_field_forbidden(self):
        with pytest.raises(ValidationError):
            GoogleSearchParams(query="x", bogus="y")


class TestGoogleToolDispatch:
    @pytest.mark.parametrize(
        "tool_name,expected_path",
        [
            ("google_search", "/structured/google/search"),
            ("google_news", "/structured/google/news"),
            ("google_jobs", "/structured/google/jobs"),
            ("google_shopping", "/structured/google/shopping"),
            ("google_maps_search", "/structured/google/mapssearch"),
        ],
    )
    @pytest.mark.asyncio
    async def test_tool_routes_to_endpoint(self, mocker, tool_name, expected_path):
        mock_run = mocker.patch(
            "scraperapi_mcp_server.sdes.google.run_sde",
            new_callable=mocker.AsyncMock,
            return_value='{"ok": true}',
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(tool_name, {"params": {"query": "laptops"}})

        mock_run.assert_awaited_once()
        path_arg, params_arg = mock_run.call_args.args
        assert path_arg == expected_path
        assert params_arg.query == "laptops"
