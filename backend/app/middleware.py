from __future__ import annotations

import asyncio
import ipaddress
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from .logging import request_id_var
from .metrics import REQUEST_COUNT, REQUEST_LATENCY

logger = logging.getLogger(__name__)
IpNetwork = ipaddress.IPv4Network | ipaddress.IPv6Network


def client_ip_from_request(request: Request, trusted_proxy_cidrs: tuple[IpNetwork, ...]) -> str:
    """Use forwarding headers only when the TCP peer is a configured proxy."""
    peer_ip = request.client.host if request.client else 'unknown'
    try:
        peer_is_trusted = any(ipaddress.ip_address(peer_ip) in network for network in trusted_proxy_cidrs)
    except ValueError:
        peer_is_trusted = False
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if peer_is_trusted and forwarded_for:
        candidate = forwarded_for.split(',', maxsplit=1)[0].strip()
        try:
            return str(ipaddress.ip_address(candidate))
        except ValueError:
            logger.warning('ignoring invalid forwarded client IP', extra={'client_ip': candidate})
    return peer_ip


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers['X-Request-ID'] = request_id
        route = request.scope.get('route')
        path = getattr(route, 'path', request.url.path)
        duration = time.perf_counter() - start
        REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(duration)
        token = request_id_var.set(request_id)
        try:
            logger.info(
                'request completed',
                extra={
                    'method': request.method,
                    'path': path,
                    'status_code': response.status_code,
                    'duration_ms': int(duration * 1000),
                },
            )
        finally:
            request_id_var.reset(token)
        return response


class DrainState:
    def __init__(self) -> None:
        self.accepting = True
        self.inflight = 0
        self._lock = asyncio.Lock()

    async def enter(self) -> bool:
        async with self._lock:
            if not self.accepting:
                return False
            self.inflight += 1
            return True

    async def leave(self) -> None:
        async with self._lock:
            self.inflight = max(0, self.inflight - 1)

    async def begin_shutdown(self) -> None:
        async with self._lock:
            self.accepting = False

    async def wait_for_drain(self, timeout: float = 20.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            async with self._lock:
                if self.inflight == 0:
                    return
            await asyncio.sleep(0.05)


drain_state = DrainState()


class GracefulDrainMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.url.path == '/health':
            return await call_next(request)
        if not await drain_state.enter():
            return JSONResponse({'detail': 'server is shutting down'}, status_code=503)
        try:
            return await call_next(request)
        finally:
            await drain_state.leave()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, cache: Any, trusted_proxy_cidrs: str) -> None:
        super().__init__(app)
        self.cache = cache
        self.trusted_proxy_cidrs = tuple(
            ipaddress.ip_network(cidr.strip())
            for cidr in trusted_proxy_cidrs.split(',')
            if cidr.strip()
        )

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.method == 'POST' and request.url.path == '/api/complaints':
            client_ip = client_ip_from_request(request, self.trusted_proxy_cidrs)
            try:
                allowed, retry_after = self.cache.allow_request(client_ip)
            except Exception:
                # Readiness will report Redis failure; do not silently replace a distributed limiter
                # with an in-process limiter that would become incorrect after HPA scale-out.
                return JSONResponse({'detail': 'rate limiter unavailable'}, status_code=503)
            if not allowed:
                return JSONResponse(
                    {'detail': 'Rate limit exceeded'},
                    status_code=429,
                    headers={'Retry-After': str(retry_after)},
                )
        return await call_next(request)
