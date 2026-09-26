from __future__ import annotations

import hashlib

from ...config import get_settings
from ...domain import Category, Priority, TriageResult
from .rules import RuleBasedTriage


class SimulatedTriage:
    name = 'simulated'

    def __init__(self, failure_mode: str | None = None) -> None:
        self.failure_mode = failure_mode or get_settings().simulated_failure_mode
        self.rules = RuleBasedTriage()

    def triage(self, text: str, location: str) -> TriageResult:
        if self.failure_mode == 'raise':
            raise RuntimeError('simulated provider failure')
        if self.failure_mode == 'malformed':
            # Intentionally invalid at the provider boundary for resilience tests.
            return TriageResult.model_validate({'category': 'invalid', 'priority': 'normal', 'summary': 'bad', 'confidence': 0.5})
        base = self.rules.triage(text, location)
        digest = hashlib.sha256(f'{text}|{location}|civicpulse'.encode()).digest()
        categories: tuple[Category, ...] = (
            Category.WATER,
            Category.ELECTRICITY,
            Category.SANITATION,
            Category.ROADS,
            Category.STREETLIGHTS,
            Category.OTHER,
        )
        if base.category == Category.OTHER:
            base.category = categories[digest[0] % len(categories)]
        if digest[1] % 11 == 0 and base.priority == Priority.NORMAL:
            base.priority = Priority.LOW
        base.confidence = round(0.70 + (digest[2] / 255) * 0.25, 3)
        return base
