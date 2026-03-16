import pytest
import httpx
from scraperapi_mcp_server.scrape.scrape import basic_scrape, ScrapeError, ScrapeResult


def _mock_httpx_client(mocker, mock_response):
    """Helper to set up an async httpx client mock."""
    mock_client = mocker.AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mocker.patch(
        "scraperapi_mcp_server.scrape.scrape.httpx.AsyncClient",
        return_value=mock_client,
    )
    return mock_client


def _mock_settings(mocker, image_size_limit=1_000_000):
    """Helper to set up settings mock."""
    mock_settings = mocker.patch("scraperapi_mcp_server.scrape.scrape.settings")
    mock_settings.API_KEY = "test_api_key"
    mock_settings.API_URL = "https://api.scraperapi.com"
    mock_settings.API_TIMEOUT_SECONDS = 30
    mock_settings.IMAGE_SIZE_LIMIT_BYTES = image_size_limit
    return mock_settings


class TestBasicScrape:
    @pytest.mark.asyncio
    async def test_basic_scrape_success(self, mocker):
        _mock_settings(mocker)

        mock_response = mocker.Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.content = b"<html><body>Test content</body></html>"
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_response.raise_for_status.return_value = None

        mock_client = _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com")

        assert isinstance(result, ScrapeResult)
        assert not result.is_image
        assert result.text == "<html><body>Test content</body></html>"
        mock_client.get.assert_called_once_with(
            "https://api.scraperapi.com",
            params={
                "api_key": "test_api_key",
                "url": "https://example.com",
                "output_format": "markdown",
                "autoparse": "false",
                "scraper_sdk": "mcp-server",
            },
            timeout=30,
        )

    @pytest.mark.asyncio
    async def test_basic_scrape_image_response(self, mocker):
        _mock_settings(mocker)

        fake_image_bytes = b"\x89PNG\r\n\x1a\nfake-image-data"
        mock_response = mocker.Mock()
        mock_response.content = fake_image_bytes
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.raise_for_status.return_value = None

        _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com/photo.png")

        assert isinstance(result, ScrapeResult)
        assert result.is_image
        assert result.image_data == fake_image_bytes
        assert result.mime_type == "image/png"

    @pytest.mark.asyncio
    async def test_basic_scrape_jpeg_image(self, mocker):
        _mock_settings(mocker)

        fake_image_bytes = b"\xff\xd8\xff\xe0fake-jpeg-data"
        mock_response = mocker.Mock()
        mock_response.content = fake_image_bytes
        mock_response.headers = {"Content-Type": "image/jpeg; charset=binary"}
        mock_response.raise_for_status.return_value = None

        _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com/photo.jpg")

        assert result.is_image
        assert result.image_data == fake_image_bytes
        assert result.mime_type == "image/jpeg"

    @pytest.mark.asyncio
    async def test_basic_scrape_image_too_large(self, mocker):
        _mock_settings(mocker, image_size_limit=100)

        large_image_bytes = b"\x89PNG" + b"\x00" * 200
        mock_response = mocker.Mock()
        mock_response.content = large_image_bytes
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.raise_for_status.return_value = None

        _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com/large.png")

        assert not result.is_image
        assert "exceeds the" in result.text
        assert "size limit" in result.text
        assert "image/png" in result.text

    @pytest.mark.asyncio
    async def test_basic_scrape_image_within_limit(self, mocker):
        _mock_settings(mocker)

        small_image_bytes = b"\x89PNG" + b"\x00" * 50
        mock_response = mocker.Mock()
        mock_response.content = small_image_bytes
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.raise_for_status.return_value = None

        _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com/small.png")

        assert result.is_image
        assert result.image_data == small_image_bytes

    @pytest.mark.asyncio
    async def test_basic_scrape_octet_stream_large(self, mocker):
        """Large non-image binary response is returned as text (not blocked by image size limit)."""
        _mock_settings(mocker, image_size_limit=100)

        large_binary = b"\x00" * 200
        mock_response = mocker.Mock()
        mock_response.content = large_binary
        mock_response.text = large_binary.decode("latin-1")
        mock_response.headers = {"Content-Type": "application/octet-stream"}
        mock_response.raise_for_status.return_value = None

        _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com/file.bin")

        assert not result.is_image
        assert result.text == large_binary.decode("latin-1")

    @pytest.mark.asyncio
    async def test_basic_scrape_octet_stream_small(self, mocker):
        """Small binary response with application/octet-stream returns as text."""
        _mock_settings(mocker)

        mock_response = mocker.Mock()
        mock_response.content = b"small data"
        mock_response.text = "small data"
        mock_response.headers = {"Content-Type": "application/octet-stream"}
        mock_response.raise_for_status.return_value = None

        _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com/file.bin")

        assert not result.is_image
        assert result.text == "small data"

    @pytest.mark.asyncio
    async def test_basic_scrape_text_content_type_oversized(self, mocker):
        """Image binary returned with text/plain content type still triggers size guard."""
        _mock_settings(mocker, image_size_limit=100)

        large_binary = b"\xff\xd8\xff\xe0" + b"\x00" * 200
        mock_response = mocker.Mock()
        mock_response.content = large_binary
        mock_response.text = large_binary.decode("latin-1")
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.raise_for_status.return_value = None

        _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com/photo.jpg")

        assert not result.is_image
        assert "exceeds the" in result.text
        assert "size limit" in result.text
        assert "image/jpeg" in result.text

    @pytest.mark.asyncio
    async def test_basic_scrape_small_image_with_text_content_type(self, mocker):
        """Small image with text/plain content type is detected via magic bytes."""
        _mock_settings(mocker)

        # Valid JPEG magic bytes, small enough to be under the size limit
        small_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 50
        mock_response = mocker.Mock()
        mock_response.content = small_jpeg
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.raise_for_status.return_value = None

        _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com/photo.jpg")

        assert result.is_image
        assert result.image_data == small_jpeg
        assert result.mime_type == "image/jpeg"

    @pytest.mark.asyncio
    async def test_basic_scrape_small_png_with_octet_stream(self, mocker):
        """Small PNG with application/octet-stream is detected via magic bytes."""
        _mock_settings(mocker)

        small_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        mock_response = mocker.Mock()
        mock_response.content = small_png
        mock_response.headers = {"Content-Type": "application/octet-stream"}
        mock_response.raise_for_status.return_value = None

        _mock_httpx_client(mocker, mock_response)

        result = await basic_scrape("https://example.com/image.png")

        assert result.is_image
        assert result.image_data == small_png
        assert result.mime_type == "image/png"

    @pytest.mark.asyncio
    async def test_basic_scrape_error(self, mocker):
        _mock_settings(mocker)

        mock_client = mocker.AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

        mocker.patch(
            "scraperapi_mcp_server.scrape.scrape.httpx.AsyncClient",
            return_value=mock_client,
        )

        with pytest.raises(ScrapeError, match="Connection error"):
            await basic_scrape("https://example.com")
