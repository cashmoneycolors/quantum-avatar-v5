class StampCard:
    def __init__(self, user_id):
        self.user_id = user_id
        self.stamps = 0

    def add_stamp(self, purchase_amount):
        if purchase_amount >= 50:
            self.stamps += 1
            if self.stamps % 10 == 0:
                return "CHF 10 Gutschein erhalten!"
        return f"Stempel: {self.stamps}"

    def redeem_voucher(self):
        if self.stamps >= 10:
            self.stamps -= 10
            return "CHF 10 Gutschein eingelöst"
        return "Nicht genug Stempel"
