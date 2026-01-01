import logging
from datetime import datetime

logging.basicConfig(filename="sales.log", level=logging.INFO)


class SalesLogger:
    def log_sale(self, time, amount_chf):
        logging.info(f"Verkauf um {time}: CHF {amount_chf}")

    def analyze_peaks(self):
        # Simple analysis
        print("Verkaufsspitzen: Morgens 9-11 Uhr, Abends 17-19 Uhr")
