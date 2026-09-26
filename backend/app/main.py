from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .database import dispose_engine
from .dependencies import get_cache_provider
from .logging import configure_logging
from .middleware import GracefulDrainMiddleware, RateLimitMiddleware, RequestContextMiddleware, drain_state
from .routes import complaints, health, meta, stats

settings = get_settings()
configure_logging(settings.log_level)


def create_app(rate_limit_cache: Any | None = None, trusted_proxy_cidrs: str | None = None) -> FastAPI:
    cache = rate_limit_cache or get_cache_provider()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        drain_state.accepting = True
        drain_state.inflight = 0
        yield
        await drain_state.begin_shutdown()
        await drain_state.wait_for_drain(timeout=20.0)
        if hasattr(cache, 'close'):
            cache.close()
        dispose_engine()

    application = FastAPI(title='CivicPulse API', version='1.0.0', lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
        allow_credentials=False,
        allow_methods=['GET', 'POST', 'PATCH', 'OPTIONS'],
        allow_headers=['*'],
    )
    application.add_middleware(
        RateLimitMiddleware,
        cache=cache,
        trusted_proxy_cidrs=trusted_proxy_cidrs or settings.trusted_proxy_cidrs,
    )
    application.add_middleware(GracefulDrainMiddleware)
    application.add_middleware(RequestContextMiddleware)

    application.include_router(complaints.router)
    application.include_router(stats.router)
    application.include_router(meta.router)
    application.include_router(health.router)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [
            {
                'field': '.'.join(str(part) for part in error['loc'] if part != 'body'),
                'message': error['msg'],
                'type': error['type'],
            }
            for error in exc.errors()
        ]
        return JSONResponse(status_code=400, content={'detail': 'Validation failed', 'errors': errors})

    return application


app = create_app()
