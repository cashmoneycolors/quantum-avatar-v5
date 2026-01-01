from __future__ import annotations

import os
from typing import Any, cast

try:
    import stripe  # type: ignore
except Exception:  # pragma: no cover
    stripe = None


class PaymentProvider:
    def __init__(self, api_key: str | None = None):
        if stripe is None:
            raise RuntimeError(
                "stripe ist nicht installiert. Installiere es oder mache "
                "Payment optional."
            )

        self._stripe: Any = cast(Any, stripe)

        if api_key is None:
            api_key = os.getenv("STRIPE_API_KEY")
        if not api_key:
            raise ValueError("STRIPE_API_KEY fehlt")

        stripe.api_key = api_key

    def charge_customer(self, amount_chf, customer_email):
        amount_rappen = int(amount_chf * 100)
        try:
            charge = self._stripe.Charge.create(
                amount=amount_rappen,
                currency="chf",
                source="tok_visa",
                description=f"Zahlung für {customer_email}",
            )
            return {"status": "success", "charge_id": charge["id"]}
        except self._stripe.error.StripeError as e:
            return {"status": "error", "message": str(e)}
