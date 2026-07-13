"""Base document generator."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from docxtpl import DocxTemplate

from app.config import get_settings

settings = get_settings()


class BaseDocumentGenerator(ABC):
    """Abstract base class for document generators."""

    template_name: str = ""

    def __init__(self) -> None:
        if not self.template_name:
            raise ValueError("template_name must be set on subclass")
        self.template_path = settings.templates_dir / f"{self.template_name}.docx"
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

    def generate(self, document_id: int, context: dict[str, Any]) -> str:
        """Render template and save to temporary DOCX file.

        Args:
            document_id: Unique document identifier.
            context: Jinja2 template variables.

        Returns:
            Absolute path to the generated DOCX file.
        """
        doc = DocxTemplate(str(self.template_path))
        doc.render(context)

        output_path = settings.temp_dir / f"doc_{document_id}_{self.template_name}.docx"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        return str(output_path)

    @abstractmethod
    def validate_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize template context."""
        ...
