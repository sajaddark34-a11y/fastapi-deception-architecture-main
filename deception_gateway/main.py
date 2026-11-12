"""
Main FastAPI Entry Point for the Deception Gateway (`deception_gateway.main`).

Initializes Layer 1 (`deception_gateway`), configures the asynchronous `lifespan`
context manager to verify Redis session storage, initialize PostgreSQL forensic
tables, and prepare `HoneyTokenInjectorMiddleware`, and mounts `gateway_router`.
"""

from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

try:
    from uvicorn.protocols.http.h11_impl import H11Protocol as _BaseHttpProtocol
except ImportError:  # pragma: no cover
    _BaseHttpProtocol = asyncio.Protocol  # type: ignore[assignment]

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

_L4_SCAN_DETECTION_ARMED: bool = False
_HTTP_METHOD_PREFIXES: tuple[bytes, ...] = (
    b"GET ",
    b"POST ",
    b"PUT ",
    b"DELETE ",
    b"HEAD ",
    b"OPTIONS ",
    b"PATCH ",
    b"TRACE ",
    b"CONNECT ",
    b"PRI * ",
)


def arm_l4_scan_detection(armed: bool = True) -> None:
    """Enable or disable L4 raw TCP port-scan telemetry after startup readiness probes complete."""
    global _L4_SCAN_DETECTION_ARMED
    _L4_SCAN_DETECTION_ARMED = armed


class TCPL4DeceptionProtocol(_BaseHttpProtocol):  # type: ignore[misc]
    """
    Transport-Layer (L4) TCP Deception Protocol Wrapper around Uvicorn's HTTP Protocol.

    Intercepts:
      1. Zero-byte TCP handshakes (`nmap -sS` via NAT / `nmap -sT` / `nc -zv` port scans)
         that close (`FIN`/`RST`) before transmitting an HTTP request.
      2. Raw non-HTTP service discovery probes (`nmap -sV` NULL/Help/GenericLines/SSL/RPC/RTSP probes)
         that would otherwise be dropped silently by the HTTP parser before reaching FastAPI.
    Forwards all captured L4 events directly to `attack_detector.inspect_tcp_l4_scan()`
    and the `ForensicExtractionEngine` (`T1046`).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._l4_client_ip: str = "127.0.0.1"
        self._l4_client_port: int = 0
        self._l4_dest_port: int = 8000
        self._l4_bytes_received: int = 0
        self._l4_probe_logged: bool = False
        self._l4_connected_at: float = 0.0

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        peername = transport.get_extra_info("peername")
        if isinstance(peername, (tuple, list)) and len(peername) >= 2:
            self._l4_client_ip = str(peername[0])
            self._l4_client_port = int(peername[1])
        sockname = transport.get_extra_info("sockname")
        if isinstance(sockname, (tuple, list)) and len(sockname) >= 2:
            self._l4_dest_port = int(sockname[1])
        self._l4_bytes_received = 0
        self._l4_probe_logged = False
        self._l4_connected_at = time.monotonic()
        super().connection_made(transport)

    def data_received(self, data: bytes) -> None:
        is_first_chunk = self._l4_bytes_received == 0
        self._l4_bytes_received += len(data)

        if is_first_chunk and data and not self._l4_probe_logged:
            upper_prefix = data[:16].upper()
            is_standard_http = any(
                upper_prefix.startswith(prefix) for prefix in _HTTP_METHOD_PREFIXES
            )
            is_nmap_rtsp_or_raw = b"RTSP/1.0" in data[:64].upper() or not is_standard_http
            if is_nmap_rtsp_or_raw:
                self._l4_probe_logged = True
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(
                        attack_detector.inspect_tcp_l4_scan(
                            client_ip=self._l4_client_ip,
                            client_port=self._l4_client_port,
                            destination_port=self._l4_dest_port,
                            raw_probe_bytes=bytes(data[:128]),
                            scan_type="NMAP_SERVICE_VERSION_PROBE",
                        )
                    )
                except RuntimeError:
                    pass

        super().data_received(data)

    def connection_lost(self, exc: Exception | None) -> None:
        super().connection_lost(exc)
        elapsed = time.monotonic() - self._l4_connected_at
        is_loopback_idle_preconnect = (
            self._l4_client_ip in ("127.0.0.1", "::1") and elapsed >= 0.20
        )
        if (
            _L4_SCAN_DETECTION_ARMED
            and self._l4_bytes_received == 0
            and not self._l4_probe_logged
            and not is_loopback_idle_preconnect
        ):
            self._l4_probe_logged = True
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(
                    attack_detector.inspect_tcp_l4_scan(
                        client_ip=self._l4_client_ip,
                        client_port=self._l4_client_port,
                        destination_port=self._l4_dest_port,
                        raw_probe_bytes=b"",
                        scan_type="TCP_L4_PORT_SCAN",
                    )
                )
            except RuntimeError:
                pass


__all__ = [
    "app",
    "gateway_lifespan",
    "gateway_router",
    "redis_cache_verifier",
    "attack_detector",
    "traffic_classifier",
    "malicious_session_router",
    "TCPL4DeceptionProtocol",
    "arm_l4_scan_detection",
]
