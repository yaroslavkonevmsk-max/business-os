"""Tax calculation service for Russian tax regimes."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class TaxResult:
    """Result of a tax calculation."""
    total_income: Decimal
    total_expenses: Decimal
    tax_base: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    regime: str
    remaining_amount: Decimal = Decimal("0")


class TaxService:
    """Calculate taxes for Russian tax regimes."""

    RATES = {
        "usn_income": Decimal("0.06"),          # УСН 6% Доходы
        "usn_income_expense": Decimal("0.15"),  # УСН 15% Доходы минус Расходы
        "npd": Decimal("0.04"),                # НПД 4% (default, can be 6%)
        "patent": Decimal("0.00"),             # Патент (fixed, not calculated here)
    }

    def calculate_tax(
        self,
        total_income: Decimal,
        total_expenses: Decimal = Decimal("0"),
        regime: str = "usn_income",
        npd_rate: Optional[Decimal] = None,
    ) -> TaxResult:
        """Calculate tax for a given regime."""
        if regime not in self.RATES:
            raise ValueError(f"Unknown tax regime: {regime}")

        rate = self.RATES[regime]

        if regime == "usn_income":
            # УСН 6%: tax on all income, expenses ignored for base but tracked
            tax_base = total_income
            tax_amount = (tax_base * rate).quantize(Decimal("0.01"))
        elif regime == "usn_income_expense":
            # УСН 15%: tax on (income - expenses)
            tax_base = total_income - total_expenses
            if tax_base < 0:
                tax_base = Decimal("0")
            tax_amount = (tax_base * rate).quantize(Decimal("0.01"))
        elif regime == "npd":
            # НПД: 4% for individuals, 6% for legal entities (default 4%)
            effective_rate = npd_rate if npd_rate is not None else rate
            tax_base = total_income
            tax_amount = (tax_base * effective_rate).quantize(Decimal("0.01"))
        elif regime == "patent":
            # Patent is fixed amount, not calculated from income
            tax_base = Decimal("0")
            tax_amount = Decimal("0")
        else:
            raise ValueError(f"Unsupported regime: {regime}")

        return TaxResult(
            total_income=total_income.quantize(Decimal("0.01")),
            total_expenses=total_expenses.quantize(Decimal("0.01")),
            tax_base=tax_base.quantize(Decimal("0.01")),
            tax_rate=rate,
            tax_amount=tax_amount,
            regime=regime,
        )

    def get_tax_deadline(self, period: str) -> str:
        """Return tax payment deadline for a given period (YYYY-MM)."""
        # For individual entrepreneurs on УСН:
        # Q1 → April 28
        # H1 → July 28
        # 9 months → October 28
        # Year → April 30 of next year
        # For simplicity, return standard deadlines
        year, month = period.split("-")
        quarter = (int(month) - 1) // 3 + 1
        deadlines = {
            1: f"{year}-04-28",
            2: f"{year}-07-28",
            3: f"{year}-10-28",
            4: f"{int(year) + 1}-04-30",
        }
        return deadlines.get(quarter, f"{year}-04-28")

    def recalculate_tax_for_period(
        self,
        income: Decimal,
        expenses: Decimal,
        regime: str,
        paid_amount: Decimal = Decimal("0"),
    ) -> TaxResult:
        """Recalculate tax and remaining amount."""
        result = self.calculate_tax(income, expenses, regime)
        result.remaining_amount = (result.tax_amount - paid_amount).quantize(Decimal("0.01"))
        if result.remaining_amount < 0:
            result.remaining_amount = Decimal("0")
        return result
