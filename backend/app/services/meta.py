from __future__ import annotations

from ..providers.cache import RedisProvider
from ..providers.triage.base import TriageProvider
from ..schemas import ProviderMetaResponse


class MetaService:
    def __init__(self, provider: TriageProvider, cache: RedisProvider) -> None:
        self.provider = provider
        self.cache = cache

    def provider_meta(self) -> ProviderMetaResponse:
        return ProviderMetaResponse(
            active_provider=self.provider.name,
            outcomes=self.cache.get_outcomes()[:20],
        )
