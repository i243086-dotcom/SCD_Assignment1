from __future__ import annotations

import logging
import time
import uuid

import httpx
from ..domain import TriageResult
from ..metrics import TRIAGE_CACHE, TRIAGE_FALLBACKS, TRIAGE_LATENCY
from ..providers.cache import RedisProvider
from ..providers.triage.base import TriageProvider
from ..providers.triage.rules import RuleBasedTriage
from ..schemas import ProviderOutcome

logger = logging.getLogger(__name__)


class TriageService:
    def __init__(self, provider: TriageProvider, cache: RedisProvider) -> None:
        self.provider = provider
        self.cache = cache
        self.fallback = RuleBasedTriage()

    @staticmethod
    def _retryable(exc: Exception) -> bool:
        if isinstance(exc, httpx.TimeoutException):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code == 429 or exc.response.status_code >= 500

        # OpenAI/Groq SDK is an optional runtime boundary at import time; only the hosted
        # provider requires it. If installed, classify its timeout/429/5xx exceptions exactly.
        try:
            from openai import APIStatusError, APITimeoutError, RateLimitError
        except ImportError:
            return False
        if isinstance(exc, (APITimeoutError, RateLimitError)):
            return True
        if isinstance(exc, APIStatusError):
            return exc.status_code == 429 or exc.status_code >= 500
        return False

    @staticmethod
    def _jitter_seconds(complaint_id: uuid.UUID) -> float:
        # Deterministic jitter keeps tests reproducible while avoiding synchronized retries.
        return 0.05 + ((complaint_id.int % 150) / 1000.0)

    def triage(self, complaint_id: uuid.UUID, text: str, location: str) -> tuple[TriageResult, str, int]:
        cached = self.cache.get_triage(text, location)
        if cached is not None:
            TRIAGE_CACHE.labels('hit').inc()
            result, triaged_by = cached
            self.cache.record_outcome(
                ProviderOutcome(provider=triaged_by, latency_ms=0, fallback=triaged_by == 'rules:fallback')
            )
            return result, triaged_by, 0
        TRIAGE_CACHE.labels('miss').inc()

        started = time.perf_counter()
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                raw_result = self.provider.triage(text, location)
                # Enforce the contract again at the orchestration boundary even for custom/injected providers.
                result = TriageResult.model_validate(raw_result)
                latency_ms = int((time.perf_counter() - started) * 1000)
                TRIAGE_LATENCY.labels(self.provider.name).observe(latency_ms / 1000.0)
                self.cache.set_triage(text, location, result, self.provider.name)
                self.cache.record_outcome(
                    ProviderOutcome(provider=self.provider.name, latency_ms=latency_ms, fallback=False)
                )
                return result, self.provider.name, latency_ms
            except Exception as exc:  # provider boundary: all failures become a safe fallback
                last_error = exc
                if attempt == 0 and self._retryable(exc):
                    time.sleep(self._jitter_seconds(complaint_id))
                    continue
                break

        fallback_started = time.perf_counter()
        result = self.fallback.triage(text, location)
        latency_ms = int((time.perf_counter() - started) * 1000)
        TRIAGE_LATENCY.labels(self.fallback.name).observe(time.perf_counter() - fallback_started)
        error_class = type(last_error).__name__ if last_error else 'UnknownError'
        TRIAGE_FALLBACKS.labels(self.provider.name, error_class).inc()
        logger.warning(
            'triage provider failed; rules fallback used',
            extra={
                'complaint_id': str(complaint_id),
                'provider': self.provider.name,
                'error_class': error_class,
            },
        )
        self.cache.set_triage(text, location, result, 'rules:fallback')
        self.cache.record_outcome(
            ProviderOutcome(
                provider=self.provider.name,
                latency_ms=latency_ms,
                fallback=True,
                error_class=error_class,
            )
        )
        return result, 'rules:fallback', latency_ms
