"""Content-based validation of uploaded files.

Clients control the declared Content-Type and filename extension, so neither can be
trusted. These helpers sniff the actual leading bytes ("magic numbers") to confirm a
file really is the type it claims, preventing e.g. an HTML/SVG payload from being
stored as ``.png``.
"""
from typing import Optional

IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def detect_file_type(data: bytes) -> Optional[str]:
    """Return the MIME type detected from the file's magic bytes, or None if unknown."""
    if len(data) < 12:
        return None
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[:4] == b"%PDF":
        return "application/pdf"
    if data[4:8] == b"ftyp":
        return "video/mp4"
    return None


def is_valid_image(data: bytes) -> bool:
    """True if the bytes are a recognized raster image format."""
    return detect_file_type(data) in IMAGE_MIME_TYPES
