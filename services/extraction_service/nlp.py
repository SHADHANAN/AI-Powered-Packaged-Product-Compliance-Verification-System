import re
from typing import Optional, Tuple

# Mapping of raw unit strings to normalized canonical units
UNIT_MAPPINGS = {
    "g": "g",
    "gm": "g",
    "gms": "g",
    "gram": "g",
    "grams": "g",
    "kg": "kg",
    "kgs": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "mg": "mg",
    "milligram": "mg",
    "milligrams": "mg",
    "ml": "ml",
    "millilitre": "ml",
    "milliliter": "ml",
    "millilitres": "ml",
    "milliliters": "ml",
    "l": "l",
    "lt": "l",
    "ltr": "l",
    "ltrs": "l",
    "litre": "l",
    "liter": "l",
    "litres": "l",
    "liters": "l",
    "n": "pcs",
    "pcs": "pcs",
    "pc": "pcs",
    "piece": "pcs",
    "pieces": "pcs",
    "unit": "pcs",
    "units": "pcs",
}


def normalize_unit(raw_unit: Optional[str]) -> Optional[str]:
    """
    Normalizes diverse unit spellings to standard Legal Metrology metric units.
    """
    if not raw_unit:
        return None
    cleaned = raw_unit.strip().lower()
    return UNIT_MAPPINGS.get(cleaned, cleaned)


def clean_text(text: Optional[str]) -> Optional[str]:
    """
    Trims whitespace, collapses internal spaces, and removes leading/trailing punctuation.
    """
    if not text:
        return None
    cleaned = re.sub(r"[ \t]+", " ", text).strip()
    cleaned = re.sub(r"^[:\-,.;]+\s*", "", cleaned)
    cleaned = re.sub(r"\s*[:\-,.;]+$", "", cleaned)
    return cleaned if cleaned else None


def clean_price(price_str: Optional[str]) -> Optional[float]:
    """
    Parses a price string into a float.
    """
    if not price_str:
        return None
    # Replace comma decimal separators e.g. 20,50 -> 20.50
    normalized = price_str.replace(",", ".").strip()
    try:
        val = float(normalized)
        return round(val, 2)
    except (ValueError, TypeError):
        return None


def clean_quantity(qty_str: Optional[str]) -> Optional[float]:
    """
    Parses a quantity string into a float.
    """
    if not qty_str:
        return None
    normalized = qty_str.replace(",", ".").strip()
    try:
        val = float(normalized)
        return int(val) if val.is_integer() else round(val, 3)
    except (ValueError, TypeError):
        return None


def extract_emails_and_phones(text: str) -> Tuple[list, list]:
    """
    Extracts email addresses and phone/toll-free numbers from a customer care text block.
    """
    from services.extraction_service.regex_patterns import PHONE_PATTERN, EMAIL_PATTERN

    phones = PHONE_PATTERN.findall(text)
    emails = EMAIL_PATTERN.findall(text)
    return list(dict.fromkeys(phones)), list(dict.fromkeys(emails))
