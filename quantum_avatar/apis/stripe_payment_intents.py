from __future__ import annotations

import os
from typing import Any, Iterable, cast

try:
    import stripe  # type: ignore
except Exception:  # pragma: no cover
    stripe = None


def _get_stripe_client(api_key: str | None = None) -> Any:
    if stripe is None:
        raise RuntimeError(
            "stripe ist nicht installiert. Installiere es oder mache Payment "
            "optional."
        )

    stripe_any: Any = cast(Any, stripe)

    if api_key is None:
        api_key = os.getenv("STRIPE_API_KEY")
    if not api_key:
        raise ValueError("STRIPE_API_KEY fehlt")

    stripe_any.api_key = api_key
    return stripe_any


def create_payment_intent(
    amount_chf: float,
    currency: str = "chf",
    payment_method_types: Iterable[str] = ("card",),
    api_key: str | None = None,
) -> str:
    """Create a Stripe PaymentIntent and return the client_secret.

    Keeps Stripe optional: raises clear errors if stripe or STRIPE_API_KEY is
    missing.
    """
    stripe_client = _get_stripe_client(api_key=api_key)

    amount_rappen = int(round(float(amount_chf) * 100))
    intent = stripe_client.PaymentIntent.create(
        amount=amount_rappen,
        currency=currency,
        payment_method_types=list(payment_method_types),
        metadata={"location": "Amriswil_Markt"},
    )
    return str(intent.client_secret)
