from typing import Annotated

from fastapi import APIRouter, Depends, Response

from ..dependencies import get_complaint_service
from ..schemas import StatsResponse
from ..services.complaints import ComplaintService

router = APIRouter(tags=['stats'])
Service = Annotated[ComplaintService, Depends(get_complaint_service)]


@router.get('/api/stats', response_model=StatsResponse)
def get_stats(service: Service, response: Response) -> StatsResponse:
    payload, cache_status = service.stats()
    response.headers['X-Cache'] = cache_status
    return payload
