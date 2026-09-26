from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ..dependencies import get_complaint_service
from ..domain import Category, Priority, Status
from ..schemas import ComplaintCreate, ComplaintListResponse, ComplaintResponse, StatusUpdate
from ..services.complaints import ComplaintService

router = APIRouter(prefix='/api/complaints', tags=['complaints'])
Service = Annotated[ComplaintService, Depends(get_complaint_service)]


@router.post('', response_model=ComplaintResponse, status_code=201)
def create_complaint(payload: ComplaintCreate, service: Service) -> ComplaintResponse:
    return service.create(payload)


@router.get('/{complaint_id}', response_model=ComplaintResponse)
def get_complaint(complaint_id: uuid.UUID, service: Service) -> ComplaintResponse:
    return service.get(complaint_id)


@router.get('', response_model=ComplaintListResponse)
def list_complaints(
    service: Service,
    category: Category | None = None,
    priority: Priority | None = None,
    status: Status | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ComplaintListResponse:
    return service.list(
        category=category,
        priority=priority,
        status=status,
        page=page,
        page_size=page_size,
    )


@router.patch('/{complaint_id}/status', response_model=ComplaintResponse)
def update_status(complaint_id: uuid.UUID, payload: StatusUpdate, service: Service) -> ComplaintResponse:
    return service.update_status(complaint_id, payload.status)
