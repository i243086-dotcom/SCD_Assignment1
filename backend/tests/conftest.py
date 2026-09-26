from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_complaint_service, get_health_service
from app.domain import Category, Priority, Status
from app.main import create_app
from app.services.complaints import ComplaintService
from app.services.triage import TriageService


class FakeCache:
    def __init__(self, limit_after: int | None = None) -> None:
        self.triage = {}
        self.stats = None
        self.outcomes = []
        self.calls = 0
        self.limit_after = limit_after
        self.invalidations = 0

    @staticmethod
    def triage_key(text, location):
        return f'{text}|{location}'

    def get_triage(self, text, location):
        return self.triage.get(self.triage_key(text, location))

    def set_triage(self, text, location, result, triaged_by):
        self.triage[self.triage_key(text, location)] = (result, triaged_by)

    def get_stats(self):
        return self.stats

    def set_stats(self, stats):
        self.stats = stats

    def invalidate_stats(self):
        self.stats = None
        self.invalidations += 1

    def allow_request(self, client_ip):
        self.calls += 1
        self.last_client_ip = client_ip
        if self.limit_after is not None and self.calls > self.limit_after:
            return False, 30
        return True, 30

    def record_outcome(self, outcome):
        self.outcomes.insert(0, outcome)
        self.outcomes = self.outcomes[:20]

    def get_outcomes(self):
        return self.outcomes[:20]

    def ping(self):
        return True

    def close(self):
        pass


@dataclass
class Row:
    id: uuid.UUID
    text: str
    location: str
    reporter_contact: str | None
    category: str
    priority: str
    status: str
    ai_summary: str | None
    triaged_by: str
    triage_latency_ms: int
    created_at: datetime
    updated_at: datetime


class FakeRepository:
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, Row] = {}

    def create(self, **kwargs):
        now = datetime.now(timezone.utc)
        row = Row(
            id=kwargs['complaint_id'],
            text=kwargs['text'],
            location=kwargs['location'],
            reporter_contact=kwargs['reporter_contact'],
            category=kwargs['category'].value,
            priority=kwargs['priority'].value,
            status=Status.OPEN.value,
            ai_summary=kwargs['ai_summary'],
            triaged_by=kwargs['triaged_by'],
            triage_latency_ms=kwargs['triage_latency_ms'],
            created_at=now,
            updated_at=now,
        )
        self.rows[row.id] = row
        return row

    def get(self, complaint_id):
        return self.rows.get(complaint_id)

    def list(self, *, category, priority, status, page, page_size):
        rows = list(self.rows.values())
        if category:
            rows = [r for r in rows if r.category == category.value]
        if priority:
            rows = [r for r in rows if r.priority == priority.value]
        if status:
            rows = [r for r in rows if r.status == status.value]
        rows.sort(key=lambda r: r.created_at, reverse=True)
        total = len(rows)
        start = (page - 1) * page_size
        return rows[start:start + page_size], total

    def update_status(self, row, new_status):
        row.status = new_status.value
        row.updated_at = datetime.now(timezone.utc)
        return row

    def stats(self):
        by_category = {c.value: 0 for c in Category}
        by_priority = {p.value: 0 for p in Priority}
        for row in self.rows.values():
            by_category[row.category] += 1
            by_priority[row.priority] += 1
        return {'by_category': by_category, 'by_priority': by_priority, 'total': len(self.rows)}


class DeterministicProvider:
    name = 'simulated'

    def triage(self, text, location):
        from app.domain import TriageResult
        return TriageResult(category=Category.WATER, priority=Priority.HIGH, summary=text[:140], confidence=0.9)


class AlwaysRaises:
    name = 'llm:groq'

    def triage(self, text, location):
        raise RuntimeError('boom')


class MalformedProvider:
    name = 'llm:groq'

    def triage(self, text, location):
        return {'category': 'not-valid'}


class FakeHealth:
    def __init__(self, ok=True, failures=None):
        self.ok = ok
        self.failures = failures or []
        self.calls = 0

    def readiness(self):
        self.calls += 1
        return self.ok, self.failures


@pytest.fixture
def cache():
    return FakeCache()


@pytest.fixture
def repository():
    return FakeRepository()


def make_service(repository, cache, provider=None):
    return ComplaintService(repository, TriageService(provider or DeterministicProvider(), cache), cache)


@pytest.fixture
def service(repository, cache):
    return make_service(repository, cache)


@pytest.fixture
def client(service, cache):
    app = create_app(rate_limit_cache=cache)
    app.dependency_overrides[get_complaint_service] = lambda: service
    app.dependency_overrides[get_health_service] = lambda: FakeHealth()
    with TestClient(app) as test_client:
        yield test_client
