"""QR code generator for payment links and document verification."""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

import qrcode
from qrcode.image.pil import PilImage

logger = logging.getLogger(__name__)


def generate_qr_code(
    data: str,
    output_path: Optional[str] = None,
    size: int = 10,
    border: int = 2,
) -> str:
    """Generate a QR code image.

    Args:
        data: The string to encode in the QR code (e.g., a payment URL).
        output_path: Optional path to save the PNG image. If None, a temporary path is used.
        size: Box size in pixels.
        border: Border width in boxes.

    Returns:
        Path to the generated PNG image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if output_path is None:
        from app.config import get_settings

        settings = get_settings()
        output_path = str(settings.temp_dir / "qr_code.png")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    logger.info("QR code saved to %s", output_path)
    return output_path


def generate_qr_code_bytes(data: str, size: int = 10, border: int = 2) -> bytes:
    """Generate a QR code and return as PNG bytes.

    Args:
        data: The string to encode.
        size: Box size in pixels.
        border: Border width in boxes.

    Returns:
        PNG image bytes.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
