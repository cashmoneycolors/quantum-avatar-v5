class BarcodeScanner:
    def __init__(self):
        self.inventory = {}

    def scan_product(self, barcode, quantity):
        if barcode in self.inventory:
            self.inventory[barcode] += quantity
        else:
            self.inventory[barcode] = quantity
        return f"Bestand aktualisiert: {barcode} = {self.inventory[barcode]}"

    def get_inventory(self):
        return self.inventory
