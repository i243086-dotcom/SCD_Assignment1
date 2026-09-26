from __future__ import annotations

from enum import StrEnum
from pydantic import BaseModel, Field, field_validator


class Category(StrEnum):
    WATER = 'water'
    ELECTRICITY = 'electricity'
    SANITATION = 'sanitation'
    ROADS = 'roads'
    STREETLIGHTS = 'streetlights'
    OTHER = 'other'


class Priority(StrEnum):
    HIGH = 'high'
    NORMAL = 'normal'
    LOW = 'low'


class Status(StrEnum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    REJECTED = 'rejected'


class TriageResult(BaseModel):
    category: Category
    priority: Priority
    summary: str = Field(min_length=1, max_length=140)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator('summary')
    @classmethod
    def one_line_summary(cls, value: str) -> str:
        value = ' '.join(value.splitlines()).strip()
        if len(value) > 140:
            raise ValueError('summary must be at most 140 characters')
        return value


TRANSITIONS: dict[Status, tuple[Status, ...]] = {
    Status.OPEN: (Status.IN_PROGRESS, Status.REJECTED),
    Status.IN_PROGRESS: (Status.RESOLVED, Status.REJECTED),
    Status.RESOLVED: (),
    Status.REJECTED: (),
}
