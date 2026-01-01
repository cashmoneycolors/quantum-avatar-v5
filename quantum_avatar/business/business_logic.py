class BusinessLogic:
    def __init__(self):
        self.users = {}  # user_id: {'points': int, 'level': str}
        try:
            from .margin_optimizer import MarginOptimizer

            self.margin_optimizer = MarginOptimizer()
        except Exception:
            self.margin_optimizer = None

    def earn_points(self, user_id, amount):
        if user_id not in self.users:
            self.users[user_id] = {"points": 0, "level": "Bronze"}
        self.users[user_id]["points"] += amount
        self.update_level(user_id)
        return self.users[user_id]

    def redeem_points(self, user_id, amount):
        if user_id in self.users and self.users[user_id]["points"] >= amount:
            self.users[user_id]["points"] -= amount
            return True
        return False

    def update_level(self, user_id):
        points = self.users[user_id]["points"]
        if points < 100:
            level = "Bronze"
        elif points < 500:
            level = "Silver"
        elif points < 1000:
            level = "Gold"
        else:
            level = "Platinum"
        self.users[user_id]["level"] = level

    def virtual_earnings(self, user_id, action):
        earnings = {"purchase": 10, "referral": 50, "review": 20}
        if action in earnings:
            return self.earn_points(user_id, earnings[action])
        return None

    def get_user_status(self, user_id):
        return self.users.get(user_id, {"points": 0, "level": "Bronze"})

    def suggest_sales_price(
        self,
        purchase_price: float,
        spoilage_rate_percent: float,
        *,
        target_margin: float | None = None,
        vat_rate: float | None = None,
    ):
        if self.margin_optimizer is None:
            return None
        return self.margin_optimizer.calculate_sales_price(
            purchase_price,
            spoilage_rate_percent,
            target_margin=target_margin,
            vat_rate=vat_rate,
        )
