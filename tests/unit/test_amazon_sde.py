import pytest
from pydantic import ValidationError

from scraperapi_mcp_server.sdes.amazon import (
    AmazonOffersParams,
    AmazonProductParams,
    AmazonSearchParams,
)

VALID_ASIN = "B08N5WRWNW"


class TestAmazonProductParams:
    def test_defaults(self):
        params = AmazonProductParams(asin=VALID_ASIN)
        assert params.query_params() == {"asin": VALID_ASIN, "output_format": "json"}

    def test_invalid_asin_rejected(self):
        with pytest.raises(ValidationError):
            AmazonProductParams(asin="too-short")

    def test_include_html_serialized(self):
        params = AmazonProductParams(asin=VALID_ASIN, include_html=True)
        assert params.query_params()["include_html"] == "true"


class TestAmazonSearchParams:
    def test_alias_fields_serialized_to_api_names(self):
        params = AmazonSearchParams(
            query="kids backpack",
            page=2,
            sort_by="price-asc-rank",
            department="toys-and-games",
        )
        result = params.query_params()
        # sort_by -> s, department -> i
        assert result["s"] == "price-asc-rank"
        assert result["i"] == "toys-and-games"
        assert "sort_by" not in result
        assert "department" not in result
        assert result["page"] == 2

    def test_page_must_be_positive(self):
        with pytest.raises(ValidationError):
            AmazonSearchParams(query="x", page=0)


class TestAmazonOffersParams:
    def test_condition_filters_serialized_snake_case(self):
        params = AmazonOffersParams(
            asin=VALID_ASIN,
            f_new=True,
            f_used_like_new=True,
            f_used_very_good=False,
        )
        result = params.query_params()
        assert result["f_new"] == "true"
        assert result["f_used_like_new"] == "true"
        assert result["f_used_very_good"] == "false"

    def test_condition_string_passthrough(self):
        params = AmazonOffersParams(asin=VALID_ASIN, condition="f_new,f_usedlikenew")
        assert params.query_params()["condition"] == "f_new,f_usedlikenew"


class TestAmazonToolDispatch:
    @pytest.mark.parametrize(
        "tool_name,arguments,expected_path",
        [
            ("amazon_product", {"asin": VALID_ASIN}, "/structured/amazon/product"),
            ("amazon_search", {"query": "kids backpack"}, "/structured/amazon/search"),
            ("amazon_offers", {"asin": VALID_ASIN}, "/structured/amazon/offers"),
        ],
    )
    @pytest.mark.asyncio
    async def test_tool_routes_to_endpoint(
        self, mocker, tool_name, arguments, expected_path
    ):
        mock_run = mocker.patch(
            "scraperapi_mcp_server.sdes.amazon.run_sde",
            new_callable=mocker.AsyncMock,
            return_value='{"ok": true}',
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(tool_name, {"params": arguments})

        mock_run.assert_awaited_once()
        path_arg, _ = mock_run.call_args.args
        assert path_arg == expected_path
