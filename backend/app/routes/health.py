from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from ..dependencies import get_health_service
from ..services.health import HealthService

router = APIRouter(tags=['health'])
Health = Annotated[HealthService, Depends(get_health_service)]


@router.get('/health')
def health() -> dict[str, str]:
    # Deliberately no database/Redis access: this endpoint is Kubernetes liveness.
    return {'status': 'ok'}


@router.get('/ready')
def ready(service: Health) -> Response:
    ok, failures = service.readiness()
    if ok:
        return JSONResponse({'status': 'ready'}, status_code=200)
    return JSONResponse({'status': 'not_ready', 'failed_dependencies': failures}, status_code=503)


@router.get('/metrics')
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
