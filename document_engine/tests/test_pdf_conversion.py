"""Tests for PDF conversion utilities."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.utils.docx_to_pdf import convert_docx_to_pdf


class TestDocxToPdfConversion:
    """Unit tests for DOCX to PDF conversion."""

    def test_libreoffice_not_found(self, tmp_path: Path) -> None:
        """Should raise RuntimeError when LibreOffice is not found."""
        with patch("app.utils.docx_to_pdf.shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="LibreOffice"):
                convert_docx_to_pdf(
                    str(tmp_path / "test.docx"),
                    str(tmp_path),
                    libreoffice_path="nonexistent",
                )

    def test_successful_conversion(self, tmp_path: Path) -> None:
        """Should return PDF path after successful conversion."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("mock docx")
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("mock pdf")

        with patch("app.utils.docx_to_pdf.shutil.which", return_value="/usr/bin/libreoffice"):
            with patch(
                "app.utils.docx_to_pdf.subprocess.run",
                return_value=MagicMock(stdout="", stderr=""),
            ) as mock_run:
                result = convert_docx_to_pdf(str(docx_file), str(tmp_path))
                assert result == str(pdf_file)
                mock_run.assert_called_once()
                args = mock_run.call_args
                assert args[0][0][0] == "/usr/bin/libreoffice"

    def test_conversion_failure(self, tmp_path: Path) -> None:
        """Should raise RuntimeError when LibreOffice returns non-zero."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("mock docx")

        from subprocess import CalledProcessError

        with patch("app.utils.docx_to_pdf.shutil.which", return_value="/usr/bin/libreoffice"):
            with patch(
                "app.utils.docx_to_pdf.subprocess.run",
                side_effect=CalledProcessError(
                    returncode=1,
                    cmd=["libreoffice"],
                    stderr="Error: file not found",
                ),
            ):
                with pytest.raises(RuntimeError, match="DOCX to PDF conversion failed"):
                    convert_docx_to_pdf(str(docx_file), str(tmp_path))

    def test_conversion_timeout(self, tmp_path: Path) -> None:
        """Should raise RuntimeError on timeout."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("mock docx")

        from subprocess import TimeoutExpired

        with patch("app.utils.docx_to_pdf.shutil.which", return_value="/usr/bin/libreoffice"):
            with patch(
                "app.utils.docx_to_pdf.subprocess.run",
                side_effect=TimeoutExpired(cmd="libreoffice", timeout=60),
            ):
                with pytest.raises(RuntimeError, match="timed out"):
                    convert_docx_to_pdf(str(docx_file), str(tmp_path), timeout=60)

    def test_pdf_not_created(self, tmp_path: Path) -> None:
        """Should raise RuntimeError when PDF is missing after command."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("mock docx")

        with patch("app.utils.docx_to_pdf.shutil.which", return_value="/usr/bin/libreoffice"):
            with patch(
                "app.utils.docx_to_pdf.subprocess.run",
                return_value=MagicMock(stdout="", stderr=""),
            ):
                with pytest.raises(RuntimeError, match="PDF not found"):
                    convert_docx_to_pdf(str(docx_file), str(tmp_path))

    def test_soffice_fallback(self, tmp_path: Path) -> None:
        """Should fall back to soffice when libreoffice is not found."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("mock docx")
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("mock pdf")

        def which_side_effect(cmd: str) -> str | None:
            if cmd == "libreoffice":
                return None
            if cmd == "soffice":
                return "/usr/bin/soffice"
            return None

        with patch("app.utils.docx_to_pdf.shutil.which", side_effect=which_side_effect):
            with patch(
                "app.utils.docx_to_pdf.subprocess.run",
                return_value=MagicMock(stdout="", stderr=""),
            ) as mock_run:
                result = convert_docx_to_pdf(str(docx_file), str(tmp_path))
                assert result == str(pdf_file)
                args = mock_run.call_args[0][0]
                assert args[0] == "/usr/bin/soffice"
