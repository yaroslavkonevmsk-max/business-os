"""DOCX to PDF conversion via LibreOffice headless."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def convert_docx_to_pdf(
    docx_path: str,
    output_dir: str,
    libreoffice_path: Optional[str] = None,
    timeout: int = 60,
) -> str:
    """Convert a DOCX file to PDF using LibreOffice headless mode.

    Args:
        docx_path: Path to the input DOCX file.
        output_dir: Directory where the PDF will be saved.
        libreoffice_path: Path to the soffice/libreoffice binary.
        timeout: Maximum seconds to wait for conversion.

    Returns:
        Absolute path to the generated PDF file.

    Raises:
        RuntimeError: If LibreOffice is not found or conversion fails.
    """
    lo_binary = libreoffice_path or "libreoffice"

    # Fallback to soffice if libreoffice is not found
    if shutil.which(lo_binary) is None:
        lo_binary = "soffice"
        if shutil.which(lo_binary) is None:
            raise RuntimeError(
                "LibreOffice (libreoffice or soffice) not found in PATH. "
                "Install LibreOffice or set LIBREOFFICE_PATH environment variable."
            )

    docx_path_abs = os.path.abspath(docx_path)
    output_dir_abs = os.path.abspath(output_dir)
    os.makedirs(output_dir_abs, exist_ok=True)

    cmd = [
        lo_binary,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_dir_abs,
        docx_path_abs,
    ]

    logger.info("Running LibreOffice conversion: %s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        logger.debug("LibreOffice stdout: %s", result.stdout)
        if result.stderr:
            logger.warning("LibreOffice stderr: %s", result.stderr)
    except subprocess.CalledProcessError as exc:
        logger.error(
            "LibreOffice conversion failed: returncode=%s stdout=%s stderr=%s",
            exc.returncode,
            exc.stdout,
            exc.stderr,
        )
        raise RuntimeError(f"DOCX to PDF conversion failed: {exc.stderr}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"DOCX to PDF conversion timed out after {timeout} seconds"
        ) from exc

    pdf_name = Path(docx_path).stem + ".pdf"
    pdf_path = os.path.join(output_dir_abs, pdf_name)

    if not os.path.exists(pdf_path):
        raise RuntimeError(f"PDF not found after conversion: {pdf_path}")

    return pdf_path
