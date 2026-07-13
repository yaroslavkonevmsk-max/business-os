"""Act (Акт выполненных работ) generator."""

from __future__ import annotations

from typing import Any

from app.generators.base import BaseDocumentGenerator


class ActGenerator(BaseDocumentGenerator):
    """Generate an act of completed work (Акт выполненных работ) from template."""

    template_name = "act"

    def validate_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Ensure required act fields are present."""
        required = [
            "company_name",
            "client_name",
            "document_number",
            "total_amount",
            "contract_number",
            "contract_date",
        ]
        for key in required:
            if key not in context:
                raise ValueError(f"Missing required field: {key}")
        return context
