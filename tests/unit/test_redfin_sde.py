import pytest
from pydantic import ValidationError

from scraperapi_mcp_server.sdes.redfin import (
    RedfinAgentParams,
    RedfinForRentParams,
    RedfinForSaleParams,
    RedfinSearchParams,
)

SALE_URL = (
    "https://www.redfin.com/NY/New-York/970-Park-Ave-10028/unit-5N/home/193335918"
)


class TestRedfinParams:
    def test_defaults(self):
        params = RedfinSearchParams(url=SALE_URL)
        assert params.query_params() == {"url": SALE_URL, "output_format": "json"}

    def test_raw_serialized_bool(self):
        params = RedfinForSaleParams(url=SALE_URL, raw=True)
        assert params.query_params()["raw"] == "true"

    def test_search_and_agent_have_no_raw_field(self):
        assert "raw" not in RedfinSearchParams.model_fields
        assert "raw" not in RedfinAgentParams.model_fields
        assert "raw" in RedfinForSaleParams.model_fields
        assert "raw" in RedfinForRentParams.model_fields

    def test_url_required(self):
        with pytest.raises(ValidationError):
            RedfinForSaleParams()


class TestRedfinToolDispatch:
    @pytest.mark.parametrize(
        "tool_name,expected_path",
        [
            ("redfin_for_sale", "/structured/redfin/forsale"),
            ("redfin_for_rent", "/structured/redfin/forrent"),
            ("redfin_search", "/structured/redfin/search"),
            ("redfin_agent", "/structured/redfin/agent"),
        ],
    )
    @pytest.mark.asyncio
    async def test_tool_routes_to_endpoint(self, mocker, tool_name, expected_path):
        mock_run = mocker.patch(
            "scraperapi_mcp_server.sdes.redfin.run_sde",
            new_callable=mocker.AsyncMock,
            return_value='{"ok": true}',
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(tool_name, {"params": {"url": SALE_URL}})

        mock_run.assert_awaited_once()
        path_arg, _ = mock_run.call_args.args
        assert path_arg == expected_path
