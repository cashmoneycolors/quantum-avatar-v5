def calculate_price(ek, mwst=0.026, marge=0.35):
    return round((ek * (1 + mwst)) / (1 - marge), 2)


if __name__ == "__main__":
    # Beispiel für 50 Produkte (gekürzt)
    products = [
        {"name": "Sucuk", "ek": 4.00, "marge": 0.35},
        {"name": "Oliven", "ek": 3.00, "marge": 0.35},
        # ... weitere 48
    ]

    for p in products[:2]:  # Beispiel
        p["vk"] = calculate_price(p["ek"], marge=p["marge"])
        print(f"{p['name']}: EK {p['ek']} CHF, VK {p['vk']} CHF")
