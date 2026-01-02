from __future__ import annotations

from dataclasses import dataclass
from datetime import time


def _parse_hhmm(value: str) -> time:
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError("Zeitformat muss HH:MM sein")
    hour = int(parts[0])
    minute = int(parts[1])
    return time(hour=hour, minute=minute)


@dataclass(frozen=True)
class MarginOptimizer:
    target_margin: float = 0.30
    vat_rate: float = 0.026

    def calculate_sales_price(
        self,
        purchase_price: float,
        spoilage_rate_percent: float,
        *,
        target_margin: float | None = None,
        vat_rate: float | None = None,
    ) -> float:
        purchase_price = float(purchase_price)
        spoilage_rate_percent = float(spoilage_rate_percent)

        if target_margin is None:
            effective_target_margin = self.target_margin
        else:
            effective_target_margin = float(target_margin)

        if vat_rate is None:
            effective_vat_rate = self.vat_rate
        else:
            effective_vat_rate = float(vat_rate)

        if purchase_price < 0:
            raise ValueError("purchase_price darf nicht negativ sein")
        if spoilage_rate_percent < 0:
            raise ValueError("spoilage_rate_percent darf nicht negativ sein")
        if not (0.0 <= effective_target_margin < 1.0):
            raise ValueError("target_margin muss in [0, 1) liegen")
        if effective_vat_rate < 0:
            raise ValueError("vat_rate darf nicht negativ sein")

        cost = purchase_price * (1.0 + (spoilage_rate_percent / 100.0))
        sales_price_excl_vat = cost / (1.0 - effective_target_margin)
        sales_price_incl_vat = sales_price_excl_vat * (1.0 + effective_vat_rate)
        return round(sales_price_incl_vat, 2)

    def dynamic_pricing(
        self,
        original_price: float,
        current_time: str | time,
        *,
        expiry_time: str | time = "17:00",
        discount_after_expiry: float = 0.5,
    ) -> float:
        original_price = float(original_price)
        if original_price < 0:
            raise ValueError("original_price darf nicht negativ sein")
        if not (0.0 < float(discount_after_expiry) <= 1.0):
            raise ValueError("discount_after_expiry muss in (0, 1] liegen")

        if isinstance(current_time, str):
            now = _parse_hhmm(current_time)
        else:
            now = current_time

        if isinstance(expiry_time, str):
            cutoff = _parse_hhmm(expiry_time)
        else:
            cutoff = expiry_time

        if now >= cutoff:
            return round(original_price * float(discount_after_expiry), 2)
        return round(original_price, 2)
