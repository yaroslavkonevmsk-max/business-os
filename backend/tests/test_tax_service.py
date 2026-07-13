"""Tests for tax calculation service."""
import pytest
from decimal import Decimal

from app.services.tax_service import TaxService, TaxResult


class TestTaxService:
    def test_usn_income_6_percent(self):
        service = TaxService()
        result = service.calculate_tax(
            total_income=Decimal("100000"),
            total_expenses=Decimal("0"),
            regime="usn_income",
        )
        assert result.tax_amount == Decimal("6000.00")
        assert result.tax_base == Decimal("100000.00")
        assert result.tax_rate == Decimal("0.06")
        assert result.regime == "usn_income"

    def test_usn_income_expense_15_percent(self):
        service = TaxService()
        result = service.calculate_tax(
            total_income=Decimal("100000"),
            total_expenses=Decimal("30000"),
            regime="usn_income_expense",
        )
        assert result.tax_amount == Decimal("10500.00")
        assert result.tax_base == Decimal("70000.00")
        assert result.tax_rate == Decimal("0.15")

    def test_npd_4_percent(self):
        service = TaxService()
        result = service.calculate_tax(
            total_income=Decimal("50000"),
            regime="npd",
            npd_rate=Decimal("0.04"),
        )
        assert result.tax_amount == Decimal("2000.00")
        assert result.tax_base == Decimal("50000.00")

    def test_npd_default_rate(self):
        service = TaxService()
        result = service.calculate_tax(
            total_income=Decimal("100000"),
            regime="npd",
        )
        assert result.tax_amount == Decimal("4000.00")

    def test_usn_income_expense_zero_base(self):
        service = TaxService()
        result = service.calculate_tax(
            total_income=Decimal("10000"),
            total_expenses=Decimal("20000"),
            regime="usn_income_expense",
        )
        assert result.tax_base == Decimal("0.00")
        assert result.tax_amount == Decimal("0.00")

    def test_patent_returns_zero(self):
        service = TaxService()
        result = service.calculate_tax(
            total_income=Decimal("100000"),
            regime="patent",
        )
        assert result.tax_amount == Decimal("0.00")

    def test_recalculate_tax_for_period(self):
        service = TaxService()
        result = service.recalculate_tax_for_period(
            income=Decimal("100000"),
            expenses=Decimal("0"),
            regime="usn_income",
            paid_amount=Decimal("2000"),
        )
        assert result.tax_amount == Decimal("6000.00")
        assert result.remaining_amount == Decimal("4000.00")

    def test_get_tax_deadline(self):
        service = TaxService()
        assert service.get_tax_deadline("2025-01") == "2025-04-28"
        assert service.get_tax_deadline("2025-04") == "2025-07-28"
        assert service.get_tax_deadline("2025-07") == "2025-10-28"
        assert service.get_tax_deadline("2025-10") == "2026-04-30"

    def test_unknown_regime_raises(self):
        service = TaxService()
        with pytest.raises(ValueError, match="Unknown tax regime"):
            service.calculate_tax(total_income=Decimal("100000"), regime="unknown")
