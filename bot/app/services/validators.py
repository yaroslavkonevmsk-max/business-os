import re
from decimal import Decimal, InvalidOperation


def validate_amount(text: str) -> float | None:
    """Validate and parse a monetary amount. Returns float or None."""
    if not text:
        return None
    # Remove spaces, normalize comma to dot
    cleaned = text.replace(" ", "").replace("\u00a0", "").replace(",", ".")
    # Remove currency symbols if at end
    cleaned = re.sub(r'[\s₽$€]?$', '', cleaned)
    try:
        amount = float(cleaned)
        if amount <= 0:
            return None
        return amount
    except ValueError:
        return None


def validate_phone(text: str) -> bool:
    """Validate phone number (7+ digits)."""
    if not text or text == "-":
        return True  # Optional
    digits = re.sub(r'\D', '', text)
    return len(digits) >= 7


def validate_email(text: str) -> bool:
    """Validate email format."""
    if not text or text == "-":
        return True  # Optional
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(pattern.match(text))


def validate_inn(text: str) -> bool:
    """Validate Russian INN (10 or 12 digits)."""
    if not text or text == "-":
        return True  # Optional
    digits = re.sub(r'\D', '', text)
    return len(digits) in (10, 12)


def parse_date(text: str) -> str | None:
    """Parse date from DD.MM.YYYY or YYYY-MM-DD. Returns ISO date string or None."""
    if not text or text == "-":
        return None
    
    # Try DD.MM.YYYY
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', text):
        return f"{text[6:10]}-{text[3:5]}-{text[0:2]}"
    
    # Try YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', text):
        return text
    
    return None
