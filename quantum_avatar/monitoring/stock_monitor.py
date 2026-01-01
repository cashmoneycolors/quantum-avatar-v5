class StockMonitor:
    def __init__(self):
        self.stock = {"sucuk": 50, "granatapfel": 100}

    def check_stock(self, product, threshold=10):
        if self.stock.get(product, 0) < threshold:
            print(f"Warnung: {product} Bestand unter {threshold}!")
        return self.stock.get(product, 0)

    def update_stock(self, product, amount):
        self.stock[product] = amount
