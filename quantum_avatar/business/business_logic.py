from __future__ import annotations

from typing import Any


class BusinessLogic:
    def __init__(self):
        # user_id -> {'points': int, 'level': str}
        self.users: dict[str, dict[str, Any]] = {}
        try:
            from .margin_optimizer import MarginOptimizer

            self.margin_optimizer = MarginOptimizer()
        except Exception:
            self.margin_optimizer = None

    @staticmethod
    def _normalize_user_id(user_id: Any) -> str:
        value = str(user_id).strip() if user_id is not None else ""
        return value or "default"

    @staticmethod
    def _normalize_amount(amount: Any) -> int:
        try:
            value = int(amount)
        except Exception as e:
            raise ValueError("amount muss eine ganze Zahl sein") from e
        if value < 0:
            raise ValueError("amount darf nicht negativ sein")
        return value

    def earn_points(self, user_id: Any, amount: Any) -> dict[str, Any]:
        uid = self._normalize_user_id(user_id)
        delta = self._normalize_amount(amount)

        if uid not in self.users:
            self.users[uid] = {"points": 0, "level": "Bronze"}
        current = int(self.users[uid].get("points", 0))
        self.users[uid]["points"] = current + delta
        self.update_level(uid)
        return dict(self.users[uid])

    def redeem_points(self, user_id: Any, amount: Any) -> bool:
        uid = self._normalize_user_id(user_id)
        delta = self._normalize_amount(amount)

        if uid in self.users:
            current = int(self.users[uid].get("points", 0))
            if current >= delta:
                self.users[uid]["points"] = current - delta
            self.update_level(uid)
            return True
        return False

    def update_level(self, user_id: str) -> None:
        points = int(self.users[user_id].get("points", 0))
        if points < 100:
            level = "Bronze"
        elif points < 500:
            level = "Silver"
        elif points < 1000:
            level = "Gold"
        else:
            level = "Platinum"
        self.users[user_id]["level"] = level

    def virtual_earnings(self, user_id: Any, action: Any) -> dict[str, Any]:
        earnings = {"purchase": 10, "referral": 50, "review": 20}
        key = str(action).strip().lower() if action is not None else ""

        if key in earnings:
            return self.earn_points(user_id, earnings[key])

        uid = self._normalize_user_id(user_id)
        status = self.get_user_status(uid)
        status["error"] = f"Unbekannte Aktion: {action}"
        status["supported_actions"] = sorted(list(earnings.keys()))
        return status

    def get_user_status(self, user_id: Any) -> dict[str, Any]:
        uid = self._normalize_user_id(user_id)
        data = self.users.get(uid)
        if not data:
            return {"points": 0, "level": "Bronze"}
        return {
            "points": int(data.get("points", 0)),
            "level": str(data.get("level", "Bronze")),
        }

    def suggest_sales_price(
        self,
        purchase_price: float,
        spoilage_rate_percent: float,
        *,
        target_margin: float | None = None,
        vat_rate: float | None = None,
    ) -> float | None:
        if self.margin_optimizer is None:
            return None
        return self.margin_optimizer.calculate_sales_price(
            purchase_price,
            spoilage_rate_percent,
            target_margin=target_margin,
            vat_rate=vat_rate,
        )
