class PurchaseOptimizer:
    def analyze_price_fluctuations(self, product, current_price, historical_prices):
        avg_price = sum(historical_prices) / len(historical_prices)
        if current_price < avg_price * 0.9:
            return f"Optimaler Kaufzeitpunkt für {product}: Jetzt kaufen."
        return f"Preis für {product} hoch, warten."

    def calculate_inventory_value(self, inventory):
        total_value = 0
        for item, details in inventory.items():
            total_value += details["quantity"] * details["price_chf"]
        return total_value
