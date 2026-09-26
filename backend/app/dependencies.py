from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from .database import SessionLocal
from .providers.cache import RedisProvider
from .providers.triage.base import TriageProvider
from .providers.triage.factory import create_triage_provider
from .repositories.complaints import ComplaintRepository
from .repositories.health import DatabaseHealthRepository
from .services.complaints import ComplaintService
from .services.health import HealthService
from .services.meta import MetaService
from .services.triage import TriageService


@lru_cache
def get_cache_provider() -> RedisProvider:
    return RedisProvider()


@lru_cache
def get_triage_provider() -> TriageProvider:
    return create_triage_provider()


def get_complaint_service() -> Generator[ComplaintService, None, None]:
    session = SessionLocal()
    cache = get_cache_provider()
    try:
        repository = ComplaintRepository(session)
        triage = TriageService(get_triage_provider(), cache)
        yield ComplaintService(repository, triage, cache)
    finally:
        session.close()


def get_health_service() -> HealthService:
    return HealthService(DatabaseHealthRepository(), get_cache_provider())


def get_meta_service() -> MetaService:
    return MetaService(get_triage_provider(), get_cache_provider())
