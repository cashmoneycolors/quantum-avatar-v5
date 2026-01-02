class DynamicPricing:
    def __init__(self):
        self.competitor_urls = ["https://competitor.ch/prices"]

    def scrape_competitor_prices(self):
        # Mock scraping
        return {"fladenbrot": 2.50, "sucuk": 5.50}

    def adjust_price(self, product, our_price):
        competitor_prices = self.scrape_competitor_prices()
        if (
            product in competitor_prices
            and competitor_prices[product] < our_price
        ):
            return competitor_prices[product] - 0.10  # Bestpreis-Garantie
        return our_price
