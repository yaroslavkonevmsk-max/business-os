"""Monthly report (Отчет) generator."""

from __future__ import annotations

from typing import Any

from app.generators.base import BaseDocumentGenerator


class ReportGenerator(BaseDocumentGenerator):
    """Generate a monthly business report from template."""

    template_name = "monthly_report"

    def validate_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Ensure required report fields are present."""
        required = [
            "company_name",
            "period_start",
            "period_end",
            "total_revenue",
            "total_expenses",
            "profit",
        ]
        for key in required:
            if key not in context:
                raise ValueError(f"Missing required field: {key}")
        return context
