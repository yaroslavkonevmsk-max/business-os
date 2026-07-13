"""Invoice (Счет на оплату) generator."""

from __future__ import annotations

from typing import Any

from app.generators.base import BaseDocumentGenerator


class InvoiceGenerator(BaseDocumentGenerator):
    """Generate an invoice (Счет на оплату) from template."""

    template_name = "invoice"

    def validate_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Ensure required invoice fields are present."""
        required = ["company_name", "client_name", "document_number", "total_amount"]
        for key in required:
            if key not in context:
                raise ValueError(f"Missing required field: {key}")
        return context
