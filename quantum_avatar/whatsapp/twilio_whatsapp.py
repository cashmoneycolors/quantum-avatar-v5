from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

try:
    from twilio.rest import Client  # type: ignore
except Exception:  # pragma: no cover
    Client = None


@dataclass(frozen=True)
class TwilioWhatsAppConfig:
    account_sid: str
    auth_token: str
    from_number: str

    @staticmethod
    def from_env() -> "TwilioWhatsAppConfig":
        account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        from_number = os.getenv("TWILIO_WHATSAPP_FROM", "").strip()

        missing: list[str] = []
        if not account_sid:
            missing.append("TWILIO_ACCOUNT_SID")
        if not auth_token:
            missing.append("TWILIO_AUTH_TOKEN")
        if not from_number:
            missing.append("TWILIO_WHATSAPP_FROM")
        if missing:
            raise ValueError(f"Missing env vars: {', '.join(missing)}")

        return TwilioWhatsAppConfig(
            account_sid=account_sid,
            auth_token=auth_token,
            from_number=from_number,
        )


class TwilioWhatsAppClient:
    def __init__(self, config: TwilioWhatsAppConfig | None = None):
        if Client is None:
            raise RuntimeError(
                "twilio ist nicht installiert. Installiere es "
                "(pip install twilio) oder nutze WhatsAppBot als Mock."
            )

        if config is None:
            config = TwilioWhatsAppConfig.from_env()

        self._config = config
        self._client: Any = Client(config.account_sid, config.auth_token)

    def send_message(self, to_number: str, body: str) -> str:
        to_number = to_number.strip()
        if not to_number:
            raise ValueError("to_number darf nicht leer sein")

        message = self._client.messages.create(
            from_=self._config.from_number,
            body=body,
            to=(
                f"whatsapp:{to_number}"
                if not to_number.startswith("whatsapp:")
                else to_number
            ),
        )
        return str(getattr(message, "sid", ""))


def send_whatsapp_order_confirmation(
    customer_number: str,
    order_details: str,
) -> str:
    client = TwilioWhatsAppClient()
    body = (
        "Bestätigung Amriswil Markt: Ihre Bestellung "
        f"{order_details} ist bereit zur Abholung. Vielen Dank!"
    )
    return client.send_message(customer_number, body)


if __name__ == "__main__":
    # Example usage (requires TWILIO_* env vars + 'twilio' installed)
    # print(send_whatsapp_order_confirmation('+4179XXXXXXX', 'Order #123'))
    pass
