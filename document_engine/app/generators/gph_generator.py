"""GPH Contract (Договор подряда / ГПХ) generator."""

from __future__ import annotations

from typing import Any

from app.generators.base import BaseDocumentGenerator


class GPHGenerator(BaseDocumentGenerator):
    """Generate a civil-law contract (Договор ГПХ) from template."""

    template_name = "gph_contract"

    def validate_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Ensure required GPH contract fields are present."""
        required = [
            "company_name",
            "client_name",
            "document_number",
            "contract_date",
            "total_amount",
        ]
        for key in required:
            if key not in context:
                raise ValueError(f"Missing required field: {key}")
        return context
