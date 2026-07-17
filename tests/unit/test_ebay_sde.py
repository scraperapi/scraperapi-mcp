import pytest
from pydantic import ValidationError

from scraperapi_mcp_server.sdes.ebay import EbayProductParams, EbaySearchParams


class TestEbayParams:
    def test_search_defaults(self):
        params = EbaySearchParams(query="vintage camera")
        assert params.query_params() == {
            "query": "vintage camera",
            "output_format": "json",
        }

    def test_search_filters_snake_case_wire_names(self):
        params = EbaySearchParams(
            query="camera",
            page=2,
            items_per_page=50,
            seller_id="topseller",
            condition="new,used",
            buying_format="auction",
            show_only="sold_items",
            sort_by="price_lowest",
        )
        result = params.query_params()
        assert result["items_per_page"] == 50
        assert result["seller_id"] == "topseller"
        assert result["buying_format"] == "auction"
        assert result["show_only"] == "sold_items"
        assert result["sort_by"] == "price_lowest"

    def test_product_id_wire_name(self):
        params = EbayProductParams(product_id="123456789012")
        assert params.query_params()["product_id"] == "123456789012"

    def test_page_must_be_positive(self):
        with pytest.raises(ValidationError):
            EbaySearchParams(query="x", page=0)


class TestEbayToolDispatch:
    @pytest.mark.parametrize(
        "tool_name,arguments,expected_path",
        [
            ("ebay_search", {"query": "camera"}, "/structured/ebay/search"),
            (
                "ebay_product",
                {"product_id": "123456789012"},
                "/structured/ebay/product",
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_tool_routes_to_endpoint(
        self, mocker, tool_name, arguments, expected_path
    ):
        mock_run = mocker.patch(
            "scraperapi_mcp_server.sdes.ebay.run_sde",
            new_callable=mocker.AsyncMock,
            return_value='{"ok": true}',
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(tool_name, {"params": arguments})

        mock_run.assert_awaited_once()
        path_arg, _ = mock_run.call_args.args
        assert path_arg == expected_path
