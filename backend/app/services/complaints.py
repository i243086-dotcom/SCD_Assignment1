from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException

from ..domain import Category, Priority, Status, TRANSITIONS
from ..providers.cache import RedisProvider
from ..repositories.complaints import ComplaintRepository
from ..schemas import ComplaintCreate, ComplaintListResponse, ComplaintResponse, StatsResponse
from .triage import TriageService


class ComplaintService:
    def __init__(
        self,
        repository: ComplaintRepository,
        triage_service: TriageService,
        cache: RedisProvider,
    ) -> None:
        self.repository = repository
        self.triage_service = triage_service
        self.cache = cache

    @staticmethod
    def _response(row: Any) -> ComplaintResponse:
        status = Status(row.status)
        return ComplaintResponse.model_validate(
            {
                'id': row.id,
                'text': row.text,
                'location': row.location,
                'reporter_contact': row.reporter_contact,
                'category': row.category,
                'priority': row.priority,
                'status': row.status,
                'ai_summary': row.ai_summary,
                'triaged_by': row.triaged_by,
                'triage_latency_ms': row.triage_latency_ms,
                'created_at': row.created_at,
                'updated_at': row.updated_at,
                'allowed_transitions': list(TRANSITIONS[status]),
            }
        )

    def create(self, payload: ComplaintCreate) -> ComplaintResponse:
        complaint_id = uuid.uuid4()
        result, triaged_by, latency_ms = self.triage_service.triage(complaint_id, payload.text, payload.location)
        row = self.repository.create(
            complaint_id=complaint_id,
            text=payload.text,
            location=payload.location,
            reporter_contact=payload.reporter_contact,
            category=result.category,
            priority=result.priority,
            ai_summary=result.summary,
            triaged_by=triaged_by,
            triage_latency_ms=latency_ms,
        )
        self.cache.invalidate_stats()
        return self._response(row)

    def get(self, complaint_id: uuid.UUID) -> ComplaintResponse:
        row = self.repository.get(complaint_id)
        if row is None:
            raise HTTPException(status_code=404, detail='Complaint not found')
        return self._response(row)

    def list(
        self,
        *,
        category: Category | None,
        priority: Priority | None,
        status: Status | None,
        page: int,
        page_size: int,
    ) -> ComplaintListResponse:
        rows, total = self.repository.list(
            category=category,
            priority=priority,
            status=status,
            page=page,
            page_size=page_size,
        )
        return ComplaintListResponse(
            items=[self._response(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update_status(self, complaint_id: uuid.UUID, new_status: Status) -> ComplaintResponse:
        row = self.repository.get(complaint_id)
        if row is None:
            raise HTTPException(status_code=404, detail='Complaint not found')
        current = Status(row.status)
        if new_status not in TRANSITIONS[current]:
            raise HTTPException(
                status_code=409,
                detail=f'Invalid status transition: {current.value} -> {new_status.value}',
            )
        updated = self.repository.update_status(row, new_status)
        self.cache.invalidate_stats()
        return self._response(updated)

    def stats(self) -> tuple[StatsResponse, str]:
        cached = self.cache.get_stats()
        if cached is not None:
            return StatsResponse.model_validate(cached), 'HIT'
        stats = self.repository.stats()
        self.cache.set_stats(stats)
        return StatsResponse.model_validate(stats), 'MISS'
