from typing import Annotated

from fastapi import APIRouter, Depends

from ..dependencies import get_meta_service
from ..schemas import ProviderMetaResponse
from ..services.meta import MetaService

router = APIRouter(tags=['meta'])
Service = Annotated[MetaService, Depends(get_meta_service)]


@router.get('/api/meta/providers', response_model=ProviderMetaResponse)
def provider_meta(service: Service) -> ProviderMetaResponse:
    return service.provider_meta()
