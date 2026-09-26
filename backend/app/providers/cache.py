from __future__ import annotations

import hashlib
import json
import time
from typing import Any


from ..config import get_settings
from ..domain import TriageResult
from ..schemas import ProviderOutcome


class RedisProvider:
    def __init__(self, url: str | None = None) -> None:
        self.settings = get_settings()
        self.url = url or self.settings.redis_url
        self._client: Any | None = None

    @property
    def client(self) -> Any:
        if self._client is None:
            import redis

            self._client = redis.Redis.from_url(self.url, decode_responses=True)
        return self._client

    @staticmethod
    def triage_key(text: str, location: str) -> str:
        normalized = f'{text.strip()}\n{location.strip()}'.encode('utf-8')
        return f'triage:{hashlib.sha256(normalized).hexdigest()}'

    def get_triage(self, text: str, location: str) -> tuple[TriageResult, str] | None:
        value = self.client.get(self.triage_key(text, location))
        if not value:
            return None
        payload = json.loads(value)
        return TriageResult.model_validate(payload['result']), str(payload['triaged_by'])

    def set_triage(self, text: str, location: str, result: TriageResult, triaged_by: str) -> None:
        payload = {'result': result.model_dump(mode='json'), 'triaged_by': triaged_by}
        self.client.setex(
            self.triage_key(text, location),
            self.settings.triage_cache_ttl_seconds,
            json.dumps(payload),
        )

    def get_stats(self) -> dict[str, Any] | None:
        value = self.client.get('stats:v1')
        return json.loads(value) if value else None

    def set_stats(self, stats: dict[str, Any]) -> None:
        self.client.setex('stats:v1', self.settings.stats_cache_ttl_seconds, json.dumps(stats))

    def invalidate_stats(self) -> None:
        self.client.delete('stats:v1')

    def allow_request(self, client_ip: str) -> tuple[bool, int]:
        window = self.settings.rate_limit_window_seconds
        bucket = int(time.time()) // window
        key = f'ratelimit:complaints:{client_ip}:{bucket}'
        pipe = self.client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window + 1)
        count, _ = pipe.execute()
        remaining = max(1, window - (int(time.time()) % window))
        return int(count) <= self.settings.rate_limit_requests, remaining

    def record_outcome(self, outcome: ProviderOutcome) -> None:
        key = 'triage:outcomes'
        pipe = self.client.pipeline()
        pipe.lpush(key, outcome.model_dump_json())
        pipe.ltrim(key, 0, 19)
        pipe.execute()

    def get_outcomes(self) -> list[ProviderOutcome]:
        rows = self.client.lrange('triage:outcomes', 0, 19)
        return [ProviderOutcome.model_validate_json(row) for row in rows]

    def ping(self) -> bool:
        return bool(self.client.ping())

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
