from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class TriggerRule:
    condition: dict[str, Any] | Callable[[dict[str, Any]], bool]
    action: str


class AutonomousExecutor:
    def __init__(self):
        # Keep insertion order deterministic; avoid dict keys for conditions.
        self.triggers: list[TriggerRule] = []

    def add_trigger(
        self,
        condition: dict[str, Any] | Callable[[dict[str, Any]], bool],
        action: str,
    ) -> None:
        rule = TriggerRule(condition=condition, action=str(action))
        self.triggers.append(rule)

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
        if day_expected is not None:
            day_actual = self._norm_str(state.get("day"))
            if day_actual != self._norm_str(day_expected):
                return False

        weather_expected = condition.get("weather")
        if weather_expected is not None:
            weather_actual = self._norm_str(state.get("weather"))
            if weather_actual != self._norm_str(weather_expected):
                return False

        location_expected = condition.get("location")
        if location_expected is not None:
            location_actual = self._norm_str(state.get("location"))
            if location_actual != self._norm_str(location_expected):
                return False

        if "stock_level_below" in condition:
            try:
                threshold_raw = condition.get("stock_level_below")
                if threshold_raw is None:
                    return False
                threshold = float(threshold_raw)

                stock_level_raw = state.get("stock_level", 1.0)
                if stock_level_raw is None:
                    return False
                stock_level = float(stock_level_raw)
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
        is_saturday = self._norm_str(s.get("day")) == "saturday"
        is_sunny = self._norm_str(s.get("weather")) == "sunny"
        if is_saturday and is_sunny:
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
