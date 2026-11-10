"""
Main FastAPI Entry Point for the Deception Gateway (`deception_gateway.main`).

Initializes Layer 1 (`deception_gateway`), configures the asynchronous `lifespan`
context manager to verify Redis session storage, initialize PostgreSQL forensic
tables, and prepare `HoneyTokenInjectorMiddleware`, and mounts `gateway_router`.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

try:
    from fastapi import FastAPI, HTTPException, Request, status
    from fastapi.responses import JSONResponse
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_handler import (  # type: ignore[attr-defined]
        HTTPException,
        status,
    )
    from core_web_app.authentication.auth_routes import Request  # type: ignore[attr-defined]
    from core_web_app.main import FastAPI, JSONResponse  # type: ignore[attr-defined]

from core_web_app.database_connector.session_manager import init_and_seed_core_db
from data_storage.postgresql_store import init_forensic_database
from data_storage.redis_store import session_state_store
from deception_gateway.gateway_router import (
    attack_detector,
    gateway_router,
    injector_enricher,
    malicious_session_router,
    redis_cache_verifier,
    traffic_classifier,
)
from honey_token_injector.injector_middleware import HoneyTokenInjectorMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def gateway_lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Asynchronous lifespan context manager initializing Redis session store,
    PostgreSQL forensic database tables, and Core Web App seed state.
    """
    await session_state_store.health_check()
    await init_forensic_database()
    await init_and_seed_core_db()
    logger.info("Deception Gateway (Layer 1) initialized and ready.")
    yield


app = FastAPI(
    title="FastAPI Deception Gateway & Reverse Proxy (Layer 1)",
    description=(
        "High-performance asynchronous deception reverse proxy that inspects incoming "
        "traffic for triggered honey tokens and exploit signatures, routes legitimate "
        "sessions to `core_web_app`, and transparently isolates attackers inside "
        "`isolation_sandbox`."
    ),
    version="1.0.0",
    lifespan=gateway_lifespan,
)

app.add_middleware(
    HoneyTokenInjectorMiddleware,
    header_generator=injector_enricher.header_generator,
    url_generator=injector_enricher.url_generator,
    token_validator=injector_enricher.token_validator,
)


@app.exception_handler(HTTPException)
async def gateway_http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Return a structured JSON error envelope for gateway HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "service": "deception_gateway",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        headers=dict(exc.headers) if exc.headers else None,
    )


@app.exception_handler(Exception)
async def gateway_unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Prevent internal stack-trace leakage at the perimeter gateway."""
    logger.exception(
        "Unhandled exception in deception_gateway on %s: %s", request.url.path, exc
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Internal gateway error.",
            "path": request.url.path,
            "service": "deception_gateway",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


app.include_router(gateway_router)

__all__ = [
    "app",
    "gateway_lifespan",
    "gateway_router",
    "redis_cache_verifier",
    "attack_detector",
    "traffic_classifier",
    "malicious_session_router",
]
