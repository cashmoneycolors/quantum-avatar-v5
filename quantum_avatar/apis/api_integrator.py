from __future__ import annotations

import os

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None

try:
    import stripe  # type: ignore
except Exception:  # pragma: no cover
    stripe = None


class APIIntegrator:
    def __init__(self):
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()

        if stripe is not None:
            api_key = os.getenv("STRIPE_API_KEY", "").strip()
            if api_key:
                stripe.api_key = api_key

    def process_payment(self, amount_chf, customer_email):
        # Amount in Rappen (100 Rappen = 1 CHF)
        amount_rappen = int(amount_chf * 100)

        if stripe is None:
            return "Payment unavailable: stripe not installed"

        if not getattr(stripe, "api_key", None):
            return "Payment unavailable: STRIPE_API_KEY missing"

        try:
            charge = stripe.Charge.create(
                amount=amount_rappen,
                currency="chf",
                source="tok_visa",  # Placeholder
                description=f"Payment for {customer_email}",
            )
            return charge["id"]
        except stripe.error.StripeError as e:
            return f"Payment failed: {e}"

    def get_weather_amriswil(self):
        # Amriswil coordinates: 47.548, 9.303
        if requests is None:
            return {"error": "Weather unavailable: requests not installed"}

        if not self.weather_api_key:
            return {
                "error": "Weather unavailable: OPENWEATHER_API_KEY missing",
            }

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?lat=47.548&lon=9.303&appid={self.weather_api_key}&units=metric"
        )
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "weather": data["weather"][0]["main"].lower(),
            }
        return {"error": "Weather data not available"}

    def get_stock_data(self, product):
        # Placeholder for stock API
        # Assume a mock API
        mock_stock = {"sucuk": 50, "oliven": 30, "lamm": 20}
        return mock_stock.get(product.lower(), 0)
