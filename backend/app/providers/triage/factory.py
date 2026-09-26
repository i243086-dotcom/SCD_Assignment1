from __future__ import annotations

from ...config import get_settings
from .base import TriageProvider
from .llm import LLMTriage
from .ollama import OllamaTriage
from .rules import RuleBasedTriage
from .simulated import SimulatedTriage


def create_triage_provider(name: str | None = None) -> TriageProvider:
    selected = (name or get_settings().triage_provider).lower()
    providers = {
        'llm': LLMTriage,
        'groq': LLMTriage,
        'ollama': OllamaTriage,
        'rules': RuleBasedTriage,
        'simulated': SimulatedTriage,
    }
    try:
        return providers[selected]()
    except KeyError as exc:
        raise ValueError(f'Unknown TRIAGE_PROVIDER: {selected}') from exc
