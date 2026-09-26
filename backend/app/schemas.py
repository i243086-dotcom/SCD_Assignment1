from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .domain import Category, Priority, Status


class ComplaintCreate(BaseModel):
    text: str = Field(min_length=10, max_length=2000)
    location: str = Field(min_length=3, max_length=200)
    reporter_contact: str | None = Field(default=None, max_length=200)

    @field_validator('text', 'location')
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('must not be blank')
        return value


class StatusUpdate(BaseModel):
    status: Status


class ComplaintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    text: str
    location: str
    reporter_contact: str | None
    category: Category
    priority: Priority
    status: Status
    ai_summary: str | None
    triaged_by: str
    triage_latency_ms: int
    created_at: datetime
    updated_at: datetime
    allowed_transitions: list[Status] = []


class ComplaintListResponse(BaseModel):
    items: list[ComplaintResponse]
    total: int
    page: int
    page_size: int


class StatsResponse(BaseModel):
    by_category: dict[str, int]
    by_priority: dict[str, int]
    total: int


class ProviderOutcome(BaseModel):
    provider: str
    latency_ms: int
    fallback: bool
    error_class: str | None = None


class ProviderMetaResponse(BaseModel):
    active_provider: str
    outcomes: list[ProviderOutcome]
