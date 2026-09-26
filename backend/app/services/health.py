from __future__ import annotations

from ..providers.cache import RedisProvider
from ..repositories.health import DatabaseHealthRepository


class HealthService:
    def __init__(self, database: DatabaseHealthRepository, cache: RedisProvider) -> None:
        self.database = database
        self.cache = cache

    def readiness(self) -> tuple[bool, list[str]]:
        failures: list[str] = []
        if not self.database.ping():
            failures.append('postgres')
        try:
            self.cache.ping()
        except Exception:
            failures.append('redis')
        return not failures, failures
