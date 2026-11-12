"""
Main FastAPI Application Entry Point for the Core Web Application (`core_web_app.main`).

Initializes the Layer 2 legitimate enterprise web application (`app`) with an
asynchronous `lifespan` context manager (`init_and_seed_core_db`), mounts
`auth_router` and `legitimate_router`, and attaches standardized response headers
and exception handlers for integration with `deception_gateway` and
`honey_token_injector`.
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Callable, Dict, Optional

try:
    from fastapi import FastAPI, HTTPException, Request, Response, status
    from fastapi.responses import JSONResponse
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_handler import (  # type: ignore[attr-defined]
        HTTPException,
        status,
    )
    from core_web_app.authentication.auth_routes import Request  # type: ignore[attr-defined]

    class Response:  # type: ignore[no-redef]
        def __init__(
            self,
            content: Any = b"",
            status_code: int = 200,
            headers: Optional[Dict[str, str]] = None,
            media_type: Optional[str] = None,
        ) -> None:
            self.content = content
            self.body = (
                content.encode("utf-8") if isinstance(content, str) else content
            )
            self.status_code = status_code
            self.headers: Dict[str, str] = dict(headers or {})
            self.media_type = media_type

    class JSONResponse(Response):  # type: ignore[no-redef]
        def __init__(
            self,
            content: Any = None,
            status_code: int = 200,
            headers: Optional[Dict[str, str]] = None,
            media_type: str = "application/json",
        ) -> None:
            import json as _json

            raw = _json.dumps(content, default=str).encode("utf-8")
            super().__init__(
                content=raw,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
            )
            self.json_content = content

    class FastAPI:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            self.title = kwargs.get("title", "")
            self.description = kwargs.get("description", "")
            self.version = kwargs.get("version", "1.0.0")
            self.lifespan = kwargs.get("lifespan")
            self.routers: list[Any] = []
            self.middlewares: list[Any] = []
            self.exception_handlers: Dict[Any, Any] = {}

        def middleware(self, _type: str) -> Any:
            def decorator(fn: Any) -> Any:
                self.middlewares.append(fn)
                return fn

            return decorator

        def exception_handler(self, exc_cls: Any) -> Any:
            def decorator(fn: Any) -> Any:
                self.exception_handlers[exc_cls] = fn
                return fn

            return decorator

        def add_middleware(self, middleware_cls: Any, **kwargs: Any) -> None:
            self.middlewares.append((middleware_cls, kwargs))

        def include_router(self, router: Any, **kwargs: Any) -> None:
            self.routers.append((router, kwargs))

from core_web_app.authentication.auth_routes import auth_router
from core_web_app.database_connector.connection import core_db_engine
from core_web_app.database_connector.session_manager import init_and_seed_core_db
from core_web_app.legitimate_request_routes import health_check, legitimate_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def core_app_lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Asynchronous lifespan context manager that initializes `core_app_users` and
    `core_app_records` tables and seeds default accounts on startup.
    """
    await init_and_seed_core_db()
    yield
    if core_db_engine is not None:
        try:
            await core_db_engine.dispose()
        except Exception:
            pass


app = FastAPI(
    title="Enterprise Core Web Application (Layer 2)",
    description=(
        "Production enterprise API service for the FastAPI-Driven Deception "
        "Architecture. Serves legitimate authenticated traffic routed by "
        "`deception_gateway` and integrates with `honey_token_injector`."
    ),
    version="1.0.0",
    lifespan=core_app_lifespan,
)


@app.middleware("http")
async def attach_structured_gateway_headers(
    request: Request,
    call_next: Callable[[Request], Response],
) -> Response:
    """
    Middleware attaching standardized upstream telemetry headers so
    `deception_gateway` and `honey_token_injector` can inspect and enrich
    legitimate responses seamlessly.
    """
    start_ns = time.perf_counter_ns()
    response: Response = await call_next(request)
    elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0

    response.headers["X-Core-App-Service"] = os.getenv(
        "SERVICE_NAME", "core_web_app"
    )
    response.headers["X-Deception-Upstream-Target"] = "CORE_WEB_APP"
    response.headers["X-Request-Processing-Time-Ms"] = f"{elapsed_ms:.3f}"
    return response


@app.exception_handler(HTTPException)
async def standardized_http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Return a structured JSON error envelope for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "service": "core_web_app",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        headers=dict(exc.headers) if exc.headers else None,
    )


@app.exception_handler(Exception)
async def standardized_unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all exception handler preventing stack-trace leakage."""
    logger.exception("Unhandled exception in core_web_app on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Internal server error in Core Web Application.",
            "path": request.url.path,
            "service": "core_web_app",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


app.include_router(auth_router)
app.include_router(legitimate_router)


@app.get("/", tags=["Core Enterprise Operations"], summary="Core Web Application Root Status")
async def core_app_root() -> Dict[str, Any]:
    """Return operational status and API documentation links at the root URL (`/`)."""
    status_payload = await health_check()
    status_payload["docs_url"] = "/docs"
    status_payload["endpoints"] = [
        "/api/v1/health",
        "/api/v1/records",
        "/api/v1/system/status",
        "/api/v1/auth/login",
    ]
    return status_payload
