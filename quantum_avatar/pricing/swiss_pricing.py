from __future__ import annotations


def swiss_round(amount: float) -> float:
    """Round to the nearest 0.05 CHF (Swiss 5 Rappen rounding)."""
    return round(float(amount) * 20) / 20


def calculate_shelf_price(
    ek_price: float, margin_percent: float, vat_rate: float = 0.026
) -> str:
    """Compute a shelf price string (CHF) from purchase price, margin, and VAT."""
    price_with_vat = float(ek_price) * (1 + float(vat_rate))
    target_price = price_with_vat / (1 - float(margin_percent))
    return f"CHF {swiss_round(target_price):.2f}"
