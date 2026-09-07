"""Parse explicit scalar quantities without treating missing text as zero."""

import re
from decimal import Decimal, InvalidOperation

NUMBER = re.compile(r"(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)")
GROUPED_NUMBER = re.compile(r"[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]+)?")
UNIT_FACTORS = {"g": Decimal(1), "gram(s)": Decimal(1), "mg": Decimal("0.001")}


def parse_amount(amount, unit):
    text = "" if amount is None else str(amount).strip()
    unit = "" if unit is None else str(unit).strip().lower()
    if not text:
        return None, "missing_amount"
    if not unit:
        return None, "missing_unit"
    if unit not in UNIT_FACTORS:
        return None, "unsupported_unit"
    if not (NUMBER.fullmatch(text) or GROUPED_NUMBER.fullmatch(text)):
        return None, "non_scalar_or_invalid"
    try:
        grams = Decimal(text.replace(",", "")) * UNIT_FACTORS[unit]
        if not grams.is_finite() or grams > Decimal("1e308"):
            return None, "non_scalar_or_invalid"
    except InvalidOperation:
        return None, "non_scalar_or_invalid"
    if grams == 0:
        return None, "zero_needs_review"
    return float(grams), "usable"
