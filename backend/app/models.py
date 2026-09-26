from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .domain import Status


class Base(DeclarativeBase):
    pass


class Complaint(Base):
    __tablename__ = 'complaints'
    __table_args__ = (
        CheckConstraint('char_length(text) >= 10 AND char_length(text) <= 2000', name='ck_complaints_text_len'),
        CheckConstraint('char_length(location) >= 3 AND char_length(location) <= 200', name='ck_complaints_location_len'),
        CheckConstraint("category IN ('water','electricity','sanitation','roads','streetlights','other')", name='ck_complaints_category'),
        CheckConstraint("priority IN ('high','normal','low')", name='ck_complaints_priority'),
        CheckConstraint("status IN ('open','in_progress','resolved','rejected')", name='ck_complaints_status'),
        CheckConstraint('ai_summary IS NULL OR char_length(ai_summary) <= 140', name='ck_complaints_ai_summary_len'),
        CheckConstraint("ai_summary IS NULL OR ai_summary !~ E'[\\n\\r]'", name='ck_complaints_ai_summary_one_line'),
        CheckConstraint("triaged_by IN ('llm:groq','llm:ollama','rules','rules:fallback','simulated')", name='ck_complaints_triaged_by'),
        Index('ix_complaints_status_priority', 'status', 'priority'),
        Index('ix_complaints_created_at', 'created_at'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    reporter_contact: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=Status.OPEN.value)
    ai_summary: Mapped[str | None] = mapped_column(String(140), nullable=True)
    triaged_by: Mapped[str] = mapped_column(String(32), nullable=False)
    triage_latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
