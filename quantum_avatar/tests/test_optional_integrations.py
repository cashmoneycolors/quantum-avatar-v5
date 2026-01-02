import os
import unittest

from quantum_avatar.apis import stripe_payment_intents
from quantum_avatar.whatsapp import twilio_whatsapp


class TestOptionalIntegrations(unittest.TestCase):
    def test_stripe_payment_intent_requires_stripe_lib(self):
        # In CI we intentionally do not install the stripe SDK.
        with self.assertRaises((RuntimeError, ValueError)):
            stripe_payment_intents.create_payment_intent(10.0)

    def test_twilio_client_requires_twilio_lib(self):
        # In CI we intentionally do not install the twilio SDK.
        with self.assertRaises(RuntimeError):
            twilio_whatsapp.TwilioWhatsAppClient()

    def test_twilio_config_requires_env(self):
        # Validates clear env-var error behavior
        # without needing twilio installed.
        old = {
            "TWILIO_ACCOUNT_SID": os.environ.pop("TWILIO_ACCOUNT_SID", None),
            "TWILIO_AUTH_TOKEN": os.environ.pop("TWILIO_AUTH_TOKEN", None),
            "TWILIO_WHATSAPP_FROM": os.environ.pop(
                "TWILIO_WHATSAPP_FROM",
                None,
            ),
        }
        try:
            with self.assertRaises(ValueError):
                twilio_whatsapp.TwilioWhatsAppConfig.from_env()
        finally:
            for k, v in old.items():
                if v is not None:
                    os.environ[k] = v


if __name__ == "__main__":
    unittest.main()
