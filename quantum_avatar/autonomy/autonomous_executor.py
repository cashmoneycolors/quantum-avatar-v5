from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class TriggerRule:
    condition: dict[str, Any] | Callable[[dict[str, Any]], bool]
    action: str


class AutonomousExecutor:
    def __init__(self):
        # Keep insertion order deterministic; do NOT use dict keys for conditions.
        self.triggers: list[TriggerRule] = []

    def add_trigger(self, condition: dict[str, Any] | Callable[[dict[str, Any]], bool], action: str) -> None:
        self.triggers.append(TriggerRule(condition=condition, action=str(action)))

    def execute(self, current_state: dict[str, Any] | None) -> str:
        state = dict(current_state or {})
        for rule in self.triggers:
            if self.check_condition(rule.condition, state):
                return self.perform_action(rule.action)
        return "Keine Aktion"

    @staticmethod
    def _norm_str(value: Any) -> str:
        return str(value).strip().lower()

    def check_condition(
        self,
        condition: dict[str, Any] | Callable[[dict[str, Any]], bool],
        state: dict[str, Any],
    ) -> bool:
        if callable(condition):
            try:
                return bool(condition(state))
            except Exception:
                return False

        # Dict-based matching (simple and robust)
        # Supported keys: day, weather, location, stock_level_below
        day_expected = condition.get("day")
        if day_expected is not None and self._norm_str(state.get("day")) != self._norm_str(day_expected):
            return False

        weather_expected = condition.get("weather")
        if weather_expected is not None and self._norm_str(state.get("weather")) != self._norm_str(weather_expected):
            return False

        location_expected = condition.get("location")
        if location_expected is not None and self._norm_str(state.get("location")) != self._norm_str(location_expected):
            return False

        if "stock_level_below" in condition:
            try:
                threshold = float(condition.get("stock_level_below"))
                stock_level = float(state.get("stock_level", 1.0))
                if not (stock_level < threshold):
                    return False
            except Exception:
                return False

        return True

    def perform_action(self, action: str) -> str:
        key = self._norm_str(action)
        if key in {"send_whatsapp", "whatsapp"}:
            return "WhatsApp-Einladung gesendet"
        if key in {"generate_post", "facebook_post", "post"}:
            return "Facebook-Post generiert"
        if key in {"book_radio", "radio"}:
            return "Radio-Werbung gebucht"
        return "Aktion ausgeführt"

    def autonomous_decision(self, state: dict[str, Any] | None) -> str:
        # Prefer explicit triggers if any were registered.
        if self.triggers:
            return self.execute(state)

        s = dict(state or {})

        # Example: Samstag + Sonne (+ optional Location) -> WhatsApp Einladung
        if self._norm_str(s.get("day")) == "saturday" and self._norm_str(s.get("weather")) == "sunny":
            return self.perform_action("send_whatsapp")

        # Low stock -> scarcity post
        try:
            if float(s.get("stock_level", 1.0)) < 0.2:
                return self.perform_action("generate_post")
        except Exception:
            pass

        # Market day -> radio
        if self._norm_str(s.get("day")) == "thursday":
            return self.perform_action("book_radio")

        return "Keine Aktion"
