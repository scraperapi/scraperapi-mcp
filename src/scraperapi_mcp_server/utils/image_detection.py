"""Utilities for detecting image content from HTTP responses."""

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
_IMAGE_SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"RIFF", "image/webp"),  # WebP starts with RIFF....WEBP
    (b"BM", "image/bmp"),
    (b"II\x2a\x00", "image/tiff"),  # little-endian TIFF
    (b"MM\x00\x2a", "image/tiff"),  # big-endian TIFF
)


def _detect_by_magic_bytes(data: bytes) -> Optional[str]:
    """Detect image format from magic bytes. Returns MIME type or None."""
    for signature, mime_type in _IMAGE_SIGNATURES:
        if data[: len(signature)] == signature:
            # Extra check for WebP: bytes 8-12 must be "WEBP"
            if mime_type == "image/webp" and data[8:12] != b"WEBP":
                continue
            # Extra check for BMP: bytes 6-9 (reserved) must be zero
            if mime_type == "image/bmp" and data[6:10] != b"\x00\x00\x00\x00":
                continue
            return mime_type
    return None


def _detect_svg(data: bytes) -> bool:
    """Detect SVG content by looking for an <svg tag in the first 4 KB."""
    head = data[:4096].lstrip()
    # Strip XML declaration / doctype if present
    if head.startswith(b"<?xml"):
        idx = head.find(b"?>")
        if idx != -1:
            head = head[idx + 2 :].lstrip()
    if head.startswith(b"<!DOCTYPE") or head.startswith(b"<!doctype"):
        idx = head.find(b">")
        if idx != -1:
            head = head[idx + 1 :].lstrip()
    return head.startswith(b"<svg") or head.startswith(b"<SVG")


def detect_image_mime(content_type: str, data: bytes) -> Optional[str]:
    """Return the image MIME type if the response is an image, else None.

    Checks the Content-Type header first, then falls back to magic-byte
    detection and SVG content inspection.
    """
    if content_type in IMAGE_CONTENT_TYPES or content_type.startswith("image/"):
        return content_type

    detected = _detect_by_magic_bytes(data)
    if detected:
        return detected

    if _detect_svg(data):
        return "image/svg+xml"

    return None
