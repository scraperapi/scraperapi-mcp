import httpx
import pytest

from scraperapi_mcp_server.utils import http
from scraperapi_mcp_server.utils.exceptions import ScraperAPIError


def _mock_httpx_client(mocker, mock_response=None, request_side_effect=None):
    """Set up an async httpx client mock for scraperapi_mcp_server.utils.http."""
    mock_client = mocker.AsyncMock()
    if request_side_effect is not None:
        mock_client.request.side_effect = request_side_effect
    else:
        mock_client.request.return_value = mock_response
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mocker.patch(
        "scraperapi_mcp_server.utils.http.httpx.AsyncClient",
        return_value=mock_client,
    )
    return mock_client


class TestCleanParams:
    def test_drops_none_and_empty_string(self):
        result = http.clean_params({"a": 1, "b": None, "c": "", "d": "x", "e": False})
        assert result == {"a": 1, "d": "x", "e": False}


class TestRequest:
    @pytest.mark.asyncio
    async def test_get_success(self, mocker):
        mock_response = mocker.Mock()
        mock_response.text = '{"ok": true}'
        mock_response.raise_for_status.return_value = None
        mock_client = _mock_httpx_client(mocker, mock_response)

        response = await http.get(
            "https://api.scraperapi.com/structured/amazon/product",
            params={"asin": "B0000000001"},
        )

        assert response.text == '{"ok": true}'
        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert args[0] == "GET"
        assert args[1] == "https://api.scraperapi.com/structured/amazon/product"
        assert kwargs["params"] == {"asin": "B0000000001"}

    @pytest.mark.asyncio
    async def test_post_sends_json_body(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_client = _mock_httpx_client(mocker, mock_response)

        await http.post(
            "https://crawler.scraperapi.com/job", json={"start_url": "https://x.com"}
        )

        _, kwargs = mock_client.request.call_args
        assert kwargs["json"] == {"start_url": "https://x.com"}

    @pytest.mark.asyncio
    async def test_http_status_error_raises_scraperapi_error(self, mocker):
        error_response = mocker.Mock()
        error_response.status_code = 403
        error_response.text = "Forbidden"
        status_error = httpx.HTTPStatusError(
            "boom", request=mocker.Mock(), response=error_response
        )
        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = status_error
        _mock_httpx_client(mocker, mock_response)

        with pytest.raises(ScraperAPIError, match="HTTP error 403"):
            await http.get("https://api.scraperapi.com/structured/amazon/product")

    @pytest.mark.asyncio
    async def test_request_error_raises_scraperapi_error(self, mocker):
        _mock_httpx_client(mocker, request_side_effect=httpx.ConnectError("no route"))

        with pytest.raises(ScraperAPIError, match="Connection error"):
            await http.get("https://api.scraperapi.com/structured/amazon/product")
