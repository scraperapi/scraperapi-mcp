import pytest
from pydantic import ValidationError

from scraperapi_mcp_server.aiparser.models import (
    AiParserCreateParams,
    AiParserUpdateParams,
)


class TestCreateParams:
    def test_body_is_json_native(self):
        # JSON body must keep real bool/int/enum-value types (not "true" strings).
        params = AiParserCreateParams(
            name="products",
            urls=["https://example.com/p/1"],
            scraper_params={"render": True, "device_type": "mobile"},
            fields=[{"name": "price", "description": "product price", "type": "number"}],
        )
        body = params.model_dump(mode="json", exclude_none=True)
        assert body["scraper_params"]["render"] is True
        assert body["scraper_params"]["device_type"] == "mobile"
        assert body["fields"][0]["type"] == "number"
        assert "api_key" not in body  # injected in the tool, not the model

    def test_requires_at_least_one_url(self):
        with pytest.raises(ValidationError):
            AiParserCreateParams(name="x", urls=[])

    def test_rejects_more_than_three_urls(self):
        # Docs cap example URLs at 1-3.
        with pytest.raises(ValidationError):
            AiParserCreateParams(
                name="x", urls=[f"https://e.com/{i}" for i in range(4)]
            )

    def test_invalid_country_code_rejected(self):
        with pytest.raises(ValidationError):
            AiParserCreateParams(
                name="x",
                urls=["https://e.com/1"],
                scraper_params={"country_code": "usa"},
            )


class TestUpdateBody:
    def test_excludes_path_params_from_body(self):
        params = AiParserUpdateParams(
            parser_id="abc",
            version=2,
            remove_fields=["price"],
        )
        body = params.model_dump(
            mode="json", exclude_none=True, exclude={"parser_id", "version"}
        )
        assert body == {"remove_fields": ["price"]}


class TestAiParserDispatch:
    @pytest.mark.asyncio
    async def test_create_posts_body_with_api_key(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.text = '{"id": "abc", "version": 0}'
        mock_post = mocker.patch(
            "scraperapi_mcp_server.aiparser.aiparser.http.post",
            new_callable=mocker.AsyncMock,
            return_value=mock_resp,
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(
            "ai_parser_create",
            {"params": {"name": "products", "urls": ["https://example.com/p/1"]}},
        )

        mock_post.assert_awaited_once()
        url = mock_post.call_args.args[0]
        body = mock_post.call_args.kwargs["json"]
        assert url.endswith("/parsers")
        assert body["api_key"] == "test_api_key"
        assert body["name"] == "products"

    @pytest.mark.asyncio
    async def test_parse_gets_with_url_and_api_key(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.text = '{"result": {}}'
        mock_get = mocker.patch(
            "scraperapi_mcp_server.aiparser.aiparser.http.get",
            new_callable=mocker.AsyncMock,
            return_value=mock_resp,
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(
            "ai_parser_parse_url",
            {"params": {"parser_id": "abc", "url": "https://example.com/p/2"}},
        )

        mock_get.assert_awaited_once()
        url = mock_get.call_args.args[0]
        query = mock_get.call_args.kwargs["params"]
        assert url.endswith("/parse/abc")
        assert query == {"api_key": "test_api_key", "url": "https://example.com/p/2"}

    @pytest.mark.asyncio
    async def test_get_uses_version_in_path(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.text = '{"status": "FINISHED"}'
        mock_get = mocker.patch(
            "scraperapi_mcp_server.aiparser.aiparser.http.get",
            new_callable=mocker.AsyncMock,
            return_value=mock_resp,
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(
            "ai_parser_get_details", {"params": {"parser_id": "abc", "version": 3}}
        )

        assert mock_get.call_args.args[0].endswith("/parsers/abc/3")

    @pytest.mark.asyncio
    async def test_update_patches_without_path_params_in_body(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.text = '{"id": "abc", "version": 1}'
        mock_patch = mocker.patch(
            "scraperapi_mcp_server.aiparser.aiparser.http.patch",
            new_callable=mocker.AsyncMock,
            return_value=mock_resp,
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(
            "ai_parser_update",
            {"params": {"parser_id": "abc", "remove_fields": ["price"]}},
        )

        mock_patch.assert_awaited_once()
        url = mock_patch.call_args.args[0]
        body = mock_patch.call_args.kwargs["json"]
        assert url.endswith("/parsers/abc")
        assert "parser_id" not in body and "version" not in body
        assert body["remove_fields"] == ["price"]
        assert body["api_key"] == "test_api_key"

    @pytest.mark.asyncio
    async def test_delete_calls_delete(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.text = ""
        mock_delete = mocker.patch(
            "scraperapi_mcp_server.aiparser.aiparser.http.delete",
            new_callable=mocker.AsyncMock,
            return_value=mock_resp,
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool("ai_parser_delete", {"params": {"parser_id": "abc"}})

        mock_delete.assert_awaited_once()
        assert mock_delete.call_args.args[0].endswith("/parsers/abc")

    @pytest.mark.asyncio
    async def test_list_gets_parsers(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.text = "[]"
        mock_get = mocker.patch(
            "scraperapi_mcp_server.aiparser.aiparser.http.get",
            new_callable=mocker.AsyncMock,
            return_value=mock_resp,
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool("ai_parser_list", {})

        mock_get.assert_awaited_once()
        assert mock_get.call_args.args[0].endswith("/parsers")
