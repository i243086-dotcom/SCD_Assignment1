from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..domain import Category, Priority, Status
from ..models import Complaint


class ComplaintRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        complaint_id: uuid.UUID,
        text: str,
        location: str,
        reporter_contact: str | None,
        category: Category,
        priority: Priority,
        ai_summary: str,
        triaged_by: str,
        triage_latency_ms: int,
    ) -> Complaint:
        row = Complaint(
            id=complaint_id,
            text=text,
            location=location,
            reporter_contact=reporter_contact,
            category=category.value,
            priority=priority.value,
            status=Status.OPEN.value,
            ai_summary=ai_summary,
            triaged_by=triaged_by,
            triage_latency_ms=triage_latency_ms,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def get(self, complaint_id: uuid.UUID) -> Complaint | None:
        return self.session.get(Complaint, complaint_id)

    def list(
        self,
        *,
        category: Category | None,
        priority: Priority | None,
        status: Status | None,
        page: int,
        page_size: int,
    ) -> tuple[Sequence[Complaint], int]:
        filters = []
        if category is not None:
            filters.append(Complaint.category == category.value)
        if priority is not None:
            filters.append(Complaint.priority == priority.value)
        if status is not None:
            filters.append(Complaint.status == status.value)

        base = select(Complaint).where(*filters)
        total = self.session.scalar(select(func.count()).select_from(base.subquery())) or 0
        rows = self.session.scalars(
            base.order_by(Complaint.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
        return rows, int(total)

    def update_status(self, row: Complaint, new_status: Status) -> Complaint:
        row.status = new_status.value
        row.updated_at = datetime.now(timezone.utc)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def stats(self) -> dict[str, object]:
        by_category = {category.value: 0 for category in Category}
        by_priority = {priority.value: 0 for priority in Priority}
        for category, count in self.session.execute(
            select(Complaint.category, func.count()).group_by(Complaint.category)
        ):
            by_category[str(category)] = int(count)
        for priority, count in self.session.execute(
            select(Complaint.priority, func.count()).group_by(Complaint.priority)
        ):
            by_priority[str(priority)] = int(count)
        total = int(self.session.scalar(select(func.count()).select_from(Complaint)) or 0)
        return {'by_category': by_category, 'by_priority': by_priority, 'total': total}

    def ensure_seed(self, rows: list[dict[str, object]]) -> int:
        inserted = 0
        for item in rows:
            complaint_id = item['id']
            if self.session.get(Complaint, complaint_id) is not None:
                continue
            self.session.add(Complaint(**item))
            inserted += 1
        self.session.commit()
        return inserted
