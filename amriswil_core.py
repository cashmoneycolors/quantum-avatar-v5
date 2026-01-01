#!/usr/bin/env python3
"""
Amriswil Core - Totale Integration aller Module
"""

from quantum_avatar.inventory.barcode_scanner import BarcodeScanner
from quantum_avatar.monitoring.monitoring_module import MonitoringModule
from quantum_avatar.whatsapp.whatsapp_bot import WhatsAppBot


def main():
    payment = None
    try:
        from quantum_avatar.apis.payment_provider import PaymentProvider

        payment = PaymentProvider()
    except Exception as exc:
        print(f"Payment deaktiviert: {exc}")

    inventory = BarcodeScanner()
    monitoring = MonitoringModule()
    whatsapp = WhatsAppBot()

    print("Amriswil Core gestartet.")
    # Beispiel-Operationen
    inventory.scan_product("sucuk", 10)
    monitoring.log_action("System start")
    response = whatsapp.respond("preis sucuk")
    print(f"WhatsApp Response: {response}")

    if payment is not None:
        print("PaymentProvider bereit.")


if __name__ == "__main__":
    main()
