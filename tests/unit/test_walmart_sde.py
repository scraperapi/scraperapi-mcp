import pytest

from scraperapi_mcp_server.sdes.walmart import (
    WalmartCategoryParams,
    WalmartProductParams,
    WalmartReviewParams,
    WalmartSearchParams,
)


class TestWalmartParams:
    def test_search_defaults(self):
        params = WalmartSearchParams(query="kids backpack")
        assert params.query_params() == {
            "query": "kids backpack",
            "output_format": "json",
        }

    def test_product_id_wire_name_is_snake_case(self):
        params = WalmartProductParams(product_id="5029197970")
        result = params.query_params()
        assert result["product_id"] == "5029197970"

    def test_category_with_page(self):
        params = WalmartCategoryParams(category="5438", page=2)
        result = params.query_params()
        assert result["category"] == "5438"
        assert result["page"] == 2

    def test_review_filters(self):
        params = WalmartReviewParams(
            product_id="5029197970",
            page=1,
            sort="recent",
            ratings="4,5",
            verified_purchase="true",
        )
        result = params.query_params()
        assert result["product_id"] == "5029197970"
        assert result["sort"] == "recent"
        assert result["ratings"] == "4,5"
        assert result["verified_purchase"] == "true"

    def test_product_has_no_page_field(self):
        assert "page" not in WalmartProductParams.model_fields

    def test_page_must_be_positive(self):
        with pytest.raises(Exception):
            WalmartSearchParams(query="x", page=0)


class TestWalmartToolDispatch:
    @pytest.mark.parametrize(
        "tool_name,arguments,expected_path",
        [
            ("walmart_search", {"query": "backpack"}, "/structured/walmart/search"),
            (
                "walmart_product",
                {"product_id": "5029197970"},
                "/structured/walmart/product",
            ),
            ("walmart_category", {"category": "5438"}, "/structured/walmart/category"),
            (
                "walmart_review",
                {"product_id": "5029197970"},
                "/structured/walmart/review",
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_tool_routes_to_endpoint(
        self, mocker, tool_name, arguments, expected_path
    ):
        mock_run = mocker.patch(
            "scraperapi_mcp_server.sdes.walmart.run_sde",
            new_callable=mocker.AsyncMock,
            return_value='{"ok": true}',
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(tool_name, {"params": arguments})

        mock_run.assert_awaited_once()
        path_arg, _ = mock_run.call_args.args
        assert path_arg == expected_path
