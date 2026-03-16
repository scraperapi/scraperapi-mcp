import httpx
from scraperapi_mcp_server.config import settings
import logging
from dataclasses import dataclass
from typing import Optional


IMAGE_CONTENT_TYPES = frozenset(
    {
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "image/bmp",
        "image/tiff",
    }
)

# Magic byte signatures for common image formats
IMAGE_SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"RIFF", "image/webp"),  # WebP starts with RIFF....WEBP
    (b"BM", "image/bmp"),
    (b"II\x2a\x00", "image/tiff"),  # little-endian TIFF
    (b"MM\x00\x2a", "image/tiff"),  # big-endian TIFF
)


def _detect_image_by_magic_bytes(data: bytes) -> Optional[str]:
    """Detect image format from magic bytes. Returns MIME type or None."""
    for signature, mime_type in IMAGE_SIGNATURES:
        if data[: len(signature)] == signature:
            # Extra check for WebP: bytes 8-12 must be "WEBP"
            if mime_type == "image/webp" and data[8:12] != b"WEBP":
                continue
            # Extra check for BMP: bytes 6-9 (reserved) must be zero
            if mime_type == "image/bmp" and data[6:10] != b"\x00\x00\x00\x00":
                continue
            return mime_type
    return None


def _format_file_size(size_bytes: int) -> str:
    """Format byte count as a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


@dataclass
class ScrapeResult:
    """Result of a scrape operation, supporting both text and image content."""

    text: Optional[str] = None
    image_data: Optional[bytes] = None
    mime_type: Optional[str] = None

    @property
    def is_image(self) -> bool:
        return self.image_data is not None


def _get_content_type(response: httpx.Response) -> str:
    """Extract the base content type from a response, without parameters."""
    content_type = response.headers.get("Content-Type", "")
    return content_type.split(";")[0].strip().lower()


async def basic_scrape(
    url: str,
    render: bool = None,
    country_code: str = None,
    premium: bool = None,
    ultra_premium: bool = None,
    device_type: str = None,
    output_format: str = "markdown",
    autoparse: bool = False,
) -> ScrapeResult:
    logging.info(f"Starting scrape for URL: {url}")
    payload = {
        "api_key": settings.API_KEY,
        "url": url,
        "scraper_sdk": "mcp-server",
    }
    optional_params = {
        "render": (render, lambda v: str(v).lower()),
        "country_code": (country_code, str),
        "premium": (premium, lambda v: str(v).lower()),
        "ultra_premium": (ultra_premium, lambda v: str(v).lower()),
        "device_type": (
            device_type,
            lambda v: v.value if hasattr(v, "value") else str(v),
        ),
        "output_format": (
            output_format,
            lambda v: v.value if hasattr(v, "value") else str(v),
        ),
        "autoparse": (autoparse, lambda v: str(v).lower()),
    }
    for key, (value, formatter) in optional_params.items():
        if value is not None:
            payload[key] = formatter(value)
            logging.debug(f"Added optional param: {key}={payload[key]}")
    try:
        logging.info(f"Sending request to {settings.API_URL}")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                settings.API_URL,
                params=payload,
                timeout=settings.API_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        logging.info(f"Scrape successful for URL: {url}")

        content_type = _get_content_type(response)
        content_size = len(response.content)
        size_limit = settings.IMAGE_SIZE_LIMIT_BYTES
        is_image = content_type in IMAGE_CONTENT_TYPES or content_type.startswith(
            "image/"
        )

        if not is_image:
            detected_mime = _detect_image_by_magic_bytes(response.content)
            if detected_mime:
                is_image = True
                content_type = detected_mime
                logging.info(
                    f"Image detected by magic bytes ({content_type}) "
                    f"despite Content-Type header"
                )

        if is_image:
            logging.info(
                f"Image response detected: {content_type}, "
                f"size: {_format_file_size(content_size)}"
            )
            if content_size > size_limit:
                logging.warning(
                    f"Image too large ({_format_file_size(content_size)}), "
                    f"limit is {_format_file_size(size_limit)}"
                )
                return ScrapeResult(
                    text=(
                        f"Image found at {url}\n"
                        f"Type: {content_type}\n"
                        f"Size: {_format_file_size(content_size)}\n\n"
                        f"The image exceeds the {_format_file_size(size_limit)} "
                        f"size limit for inline content and cannot be returned directly."
                    )
                )
            return ScrapeResult(image_data=response.content, mime_type=content_type)

        return ScrapeResult(text=response.text)
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        param_summary = " ".join(
            f"{k}={v}" for k, v in payload.items() if k != "api_key"
        )
        error_message = f"HTTP error {status_code} when scraping '{url}'. Parameters used: {param_summary}"
        logging.error(f"basic_scrape: {error_message}", exc_info=True)
        raise ScrapeError(error_message) from e
    except httpx.RequestError as e:
        error_message = f"Connection error when scraping '{url}': {e}"
        logging.error(f"basic_scrape: {error_message}", exc_info=True)
        raise ScrapeError(error_message) from e
    except Exception as e:
        error_message = f"Unexpected error when scraping '{url}': {e}"
        logging.error(f"basic_scrape: {error_message}", exc_info=True)
        raise ScrapeError(error_message) from e


class ScrapeError(Exception):
    """Raised when a scrape operation fails. Carries an actionable error message."""

    pass
