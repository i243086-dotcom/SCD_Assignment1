from __future__ import annotations

from typing import Protocol

from ...domain import TriageResult


class TriageProvider(Protocol):
    name: str

    def triage(self, text: str, location: str) -> TriageResult:
        ...
