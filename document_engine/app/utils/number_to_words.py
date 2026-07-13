"""Convert numeric amounts to Russian words."""

from __future__ import annotations

from decimal import Decimal
from typing import Union

from num2words import num2words


# Russian currency forms for correct declension
_RUBLES_FORMS = ["рубль", "рубля", "рублей"]
_KOPECKS_FORMS = ["копейка", "копейки", "копеек"]


def _plural_form(n: int, forms: list[str]) -> str:
    """Return correct Russian plural form for a number."""
    if 10 <= n % 100 <= 20:
        return forms[2]
    mod = n % 10
    if mod == 1:
        return forms[0]
    if 2 <= mod <= 4:
        return forms[1]
    return forms[2]


def amount_to_words(amount: Union[Decimal, int, float, str]) -> str:
    """Convert a monetary amount to Russian words.

    Examples:
        23100.50 -> "Двадцать три тысячи сто рублей 50 копеек"
        1000.00 -> "Одна тысяча рублей 00 копеек"

    Args:
        amount: Monetary amount (supports Decimal for precision).

    Returns:
        Amount spelled out in Russian with currency units.
    """
    if isinstance(amount, str):
        amount = Decimal(amount.replace(" ", "").replace(",", "."))
    elif isinstance(amount, (int, float)):
        amount = Decimal(str(amount))
    elif not isinstance(amount, Decimal):
        raise TypeError(f"amount must be Decimal, int, float or str, got {type(amount)}")

    # Separate rubles and kopecks
    rubles = int(amount)
    kopecks = int((amount - rubles) * 100)

    # Handle negative amounts
    if amount < 0:
        rubles = abs(rubles)
        kopecks = abs(kopecks)
        prefix = "Минус "
    else:
        prefix = ""

    # Convert to words
    rubles_words = num2words(rubles, lang="ru")
    kopecks_words = num2words(kopecks, lang="ru")

    # Capitalize first letter and add currency forms
    rubles_words = prefix + rubles_words.capitalize()
    rubles_form = _plural_form(rubles, _RUBLES_FORMS)
    kopecks_form = _plural_form(kopecks, _KOPECKS_FORMS)

    return f"{rubles_words} {rubles_form} {kopecks_words:02d} {kopecks_form}"


def number_to_words(n: Union[int, str]) -> str:
    """Convert a plain number to Russian words (capitalized)."""
    if isinstance(n, str):
        n = int(n)
    return num2words(n, lang="ru").capitalize()
