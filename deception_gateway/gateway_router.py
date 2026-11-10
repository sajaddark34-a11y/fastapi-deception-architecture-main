"""
Deception Gateway Reverse-Proxy Router (`deception_gateway.gateway_router`).

Acts as the Layer 1 perimeter ingress router (`APIRouter`) inspecting every request
via `TrafficClassifier`:
- Legitimate sessions (`RoutingTargetEnum.CORE_WEB_APP`) are forwarded to
  `core_web_app` (via `httpx` upstream or direct in-process dispatch) and their
  responses are enriched with cryptographic lures by `HoneyTokenInjectorMiddleware`.
- Malicious or trapped sessions (`RoutingTargetEnum.PREWARMED_SANDBOX`) are
  immediately diverted to `MaliciousSessionRouter` without ever touching the
  production application or database.
Also exposes `/gateway/health` and `/gateway/metrics` for SOC monitoring.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional, Tuple

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore[assignment]

try:
    from fastapi import APIRouter, Request, status
    from fastapi.responses import JSONResponse, Response
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_handler import status  # type: ignore[attr-defined]
    from core_web_app.authentication.auth_routes import (  # type: ignore[attr-defined]
        APIRouter,
        Request,
    )
    from core_web_app.main import JSONResponse, Response  # type: ignore[attr-defined]

from core_web_app.authentication.auth_handler import HTTPAuthorizationCredentials
from core_web_app.authentication.auth_routes import (
    LoginRequestSchema,
    RegisterRequestSchema,
    TokenVerifyRequestSchema,
    get_authenticated_profile,
    login_user,
    register_user,
    verify_jwt_token,
)
from core_web_app.database_connector.session_manager import init_and_seed_core_db
from core_web_app.legitimate_request_routes import (
    EnterpriseRecordCreateSchema,
    create_enterprise_record,
    get_enterprise_record_by_id,
    get_system_status,
    health_check as core_app_health_check,
    list_enterprise_records,
)
from data_storage.postgresql_store import (
    check_db_health,
    forensic_logs_repository,
)
from data_storage.redis_store import (
    fast_alerts_stream,
    session_state_store,
)
from deception_gateway.attack_detector import AttackDetector
from deception_gateway.malicious_session_router import MaliciousSessionRouter
from deception_gateway.redis_cache_verifier import RedisCacheVerifier
from deception_gateway.traffic_classifier import (
    TrafficClassificationDecision,
    TrafficClassifier,
)
from honey_token_injector import (
    HoneyTokenInjectorMiddleware,
    honey_token_injector_middleware,
    honey_token_validator,
)
from shared_contracts.session_schema import RoutingTargetEnum

logger = logging.getLogger(__name__)

CORE_WEB_APP_URL: str = os.getenv(
    "CORE_WEB_APP_URL", "http://core_web_app:8001"
).rstrip("/")

redis_cache_verifier = RedisCacheVerifier(store=session_state_store)
attack_detector = AttackDetector(
    validator=honey_token_validator,
    alerts_stream=fast_alerts_stream,
    logs_repo=forensic_logs_repository,
)
traffic_classifier = TrafficClassifier(
    cache_verifier=redis_cache_verifier,
    attack_detector=attack_detector,
)
malicious_session_router = MaliciousSessionRouter(
    state_store=session_state_store,
    alerts_stream=fast_alerts_stream,
    logs_repo=forensic_logs_repository,
)
injector_enricher: HoneyTokenInjectorMiddleware = honey_token_injector_middleware

gateway_router = APIRouter(tags=["Deception Gateway Reverse Proxy"])


async def _dispatch_to_core_app_inprocess(
    method: str,
    path: str,
    headers: Mapping[str, str],
    query_params: Mapping[str, str],
    body_bytes: bytes,
    request_obj: Request,
) -> Tuple[int, Dict[str, Any]]:
    """
    In-process fallback dispatcher invoking `core_web_app` handlers directly when
    running in unified local/test mode without a separate `core_web_app` container.
    """
    await init_and_seed_core_db()
    clean_path = path.split("?")[0].rstrip("/") or "/"
    upper_method = method.upper()

    auth_header = headers.get("Authorization") or headers.get("authorization") or ""
    creds: Optional[HTTPAuthorizationCredentials] = None
    if auth_header.lower().startswith("bearer "):
        creds = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=auth_header.split(" ", 1)[1].strip(),
        )

    body_dict: Dict[str, Any] = {}
    if body_bytes:
        try:
            parsed = json.loads(body_bytes.decode("utf-8"))
            if isinstance(parsed, dict):
                body_dict = parsed
        except Exception:
            body_dict = {}

    if clean_path in ("/", "/api/v1/health") and upper_method == "GET":
        return 200, await core_app_health_check()

    if clean_path == "/api/v1/system/status" and upper_method == "GET":
        return 200, await get_system_status()

    if clean_path == "/api/v1/records" and upper_method == "GET":
        res = await list_enterprise_records(
            department=query_params.get("department"),
            classification_level=query_params.get("classification_level"),
            limit=int(query_params.get("limit", "50")),
            db=None,
        )
        return 200, res.model_dump(mode="json")

    if clean_path == "/api/v1/records" and upper_method == "POST":
        create_schema = EnterpriseRecordCreateSchema.model_validate(body_dict)
        res = await create_enterprise_record(
            payload=create_schema,
            credentials=creds,
            db=None,
        )
        return 201, res.model_dump(mode="json")

    if clean_path.startswith("/api/v1/records/") and upper_method == "GET":
        rec_id = clean_path.split("/api/v1/records/", 1)[1]
        res = await get_enterprise_record_by_id(record_id=rec_id, db=None)
        return 200, res.model_dump(mode="json")

    if clean_path == "/api/v1/auth/login" and upper_method == "POST":
        login_schema = LoginRequestSchema.model_validate(body_dict)
        res = await login_user(payload=login_schema, request=request_obj, db=None)
        return 200, res.model_dump(mode="json")

    if clean_path == "/api/v1/auth/register" and upper_method == "POST":
        reg_schema = RegisterRequestSchema.model_validate(body_dict)
        res = await register_user(payload=reg_schema, db=None)
        return 201, res.model_dump(mode="json")

    if clean_path == "/api/v1/auth/verify" and upper_method == "POST":
        ver_schema = TokenVerifyRequestSchema.model_validate(body_dict)
        res = await verify_jwt_token(payload=ver_schema)
        return 200, res.model_dump(mode="json")

    if clean_path == "/api/v1/auth/me" and upper_method == "GET":
        from core_web_app.authentication.auth_handler import (
            get_current_authenticated_user,
        )

        user = await get_current_authenticated_user(credentials=creds, db=None)
        res = await get_authenticated_profile(current_user=user)
        return 200, res.model_dump(mode="json")

    return 404, {
        "error": True,
        "status_code": 404,
        "detail": f"Endpoint '{clean_path}' not found on Core Web Application.",
    }


async def forward_legitimate_request(
    method: str,
    path: str,
    headers: Mapping[str, str],
    query_params: Mapping[str, str],
    body_bytes: bytes,
    session_id: str,
    request_obj: Request,
) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
    """
    Forward a verified legitimate request to `core_web_app` (via `httpx.AsyncClient`
    or in-process fallback) and enrich the response with Honey Tokens via
    `HoneyTokenInjectorMiddleware`.
    """
    norm_path = path if path.startswith("/") else f"/{path}"
    target_url = f"{CORE_WEB_APP_URL}{norm_path}"

    status_code: int = 200
    response_payload: Dict[str, Any] = {}
    upstream_headers: Dict[str, str] = {
        "X-Deception-Upstream-Target": RoutingTargetEnum.CORE_WEB_APP.value,
        "X-Session-ID": session_id,
    }

    proxied_remotely = False
    if httpx is not None and os.getenv("DISABLE_EXTERNAL_CORE_PROXY", "false").lower() != "true":
        fwd_headers = {
            str(k): str(v)
            for k, v in headers.items()
            if str(k).lower() not in {"host", "content-length"}
        }
        fwd_headers["X-Session-ID"] = session_id
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                resp = await client.request(
                    method=method.upper(),
                    url=target_url,
                    params=dict(query_params),
                    headers=fwd_headers,
                    content=body_bytes,
                )
                status_code = resp.status_code
                response_payload = resp.json()
                proxied_remotely = True
        except Exception as exc:
            logger.debug(
                "Upstream core_web_app at %s not reachable over network (%s); using in-process Core App dispatcher.",
                target_url,
                exc,
            )

    if not proxied_remotely:
        try:
            status_code, response_payload = await _dispatch_to_core_app_inprocess(
                method=method,
                path=norm_path,
                headers=headers,
                query_params=query_params,
                body_bytes=body_bytes,
                request_obj=request_obj,
            )
        except Exception as exc:
            sc = getattr(exc, "status_code", 500)
            detail = getattr(exc, "detail", str(exc))
            status_code = int(sc)
            response_payload = {
                "error": True,
                "status_code": status_code,
                "detail": detail,
            }

    # Enrich outgoing legitimate response with Honey Tokens (headers + JSON lures)
    injector_enricher.inject_headers_into_mapping(upstream_headers)
    if status_code < 400 and isinstance(response_payload, dict):
        enriched_payload, _ = injector_enricher.enrich_json_payload(response_payload)
        response_payload = enriched_payload

    return status_code, response_payload, upstream_headers


@gateway_router.get(
    "/gateway/health",
    status_code=status.HTTP_200_OK,
    summary="Deception Gateway perimeter health and readiness check",
)
async def gateway_health_check() -> Dict[str, Any]:
    """
    Verify operational readiness of the Deception Gateway, Redis session store,
    PostgreSQL forensic database, and Honey Token Injector.
    """
    redis_ok = await session_state_store.health_check()
    postgres_ok = await check_db_health()
    malicious_sessions = await session_state_store.list_active_malicious_sessions()

    return {
        "status": "healthy",
        "service": os.getenv("SERVICE_NAME", "deception_gateway"),
        "layer": "Layer 1 - Ingress Deception Gateway",
        "redis_session_store_ready": redis_ok,
        "postgres_forensic_db_connected": postgres_ok,
        "active_trapped_sessions_count": len(malicious_sessions),
        "monitored_decoy_paths_count": len(
            injector_enricher.url_generator.get_registered_decoy_paths()
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@gateway_router.get(
    "/gateway/metrics",
    status_code=status.HTTP_200_OK,
    summary="Real-time Deception Gateway threat classification and containment metrics",
)
async def gateway_metrics() -> Dict[str, Any]:
    """
    Aggregate real-time threat metrics across active malicious sessions in Redis,
    recent security alerts, and forensic database timelines.
    """
    malicious_sessions = await session_state_store.list_active_malicious_sessions()
    recent_alerts = await fast_alerts_stream.get_recent_alerts(limit=25)
    timeline_metrics = await forensic_logs_repository.get_attack_timeline_metrics()

    return {
        "gateway_service": "deception_gateway",
        "active_malicious_sessions": [
            s.model_dump(mode="json") for s in malicious_sessions
        ],
        "recent_alerts_count": len(recent_alerts),
        "issued_header_tokens_count": len(
            injector_enricher.header_generator.get_issued_tokens()
        ),
        "issued_url_tokens_count": len(
            injector_enricher.url_generator.get_issued_tokens()
        ),
        "forensic_timeline_metrics": timeline_metrics,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def process_gateway_request(
    request: Request,
    full_path: str = "/",
) -> Response:
    """
    Core reverse-proxy handler evaluating `request` through `TrafficClassifier`
    and routing either to `core_web_app` (with honey-token injection) or to
    `MaliciousSessionRouter` (isolated sandbox containment).
    """
    norm_path = full_path if full_path.startswith("/") else f"/{full_path}"
    method = getattr(request, "method", "GET")
    headers = dict(getattr(request, "headers", {}) or {})
    query_params = dict(getattr(request, "query_params", {}) or {})
    cookies = dict(getattr(request, "cookies", {}) or {})

    client_obj = getattr(request, "client", None)
    direct_ip = (getattr(client_obj, "host", None) if client_obj else None) or "127.0.0.1"
    trust_proxy = os.getenv("TRUST_PROXY_HEADERS", "true").lower() == "true"
    forwarded_ip = (
        headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or headers.get("X-Real-IP", "").strip()
    ) if trust_proxy else ""
    client_ip = forwarded_ip or direct_ip
    session_id = (
        headers.get("X-Session-ID")
        or headers.get("x-session-id")
        or cookies.get("deception_session_id")
    )

    body_bytes = b""
    if hasattr(request, "body") and callable(request.body):
        try:
            body_bytes = await request.body()
        except Exception:
            body_bytes = b""

    body_text = body_bytes.decode("utf-8", errors="replace") if body_bytes else ""

    decision: TrafficClassificationDecision = (
        await traffic_classifier.classify_request(
            session_id=session_id,
            client_ip=client_ip,
            request_path=norm_path,
            request_method=method,
            headers=headers,
            query_params=query_params,
            cookies=cookies,
            body_text=body_text,
        )
    )

    if decision.routing_target == RoutingTargetEnum.PREWARMED_SANDBOX:
        sbx_status, sbx_payload, sbx_headers = (
            await malicious_session_router.route_to_sandbox(
                session=decision.session,
                request_method=method,
                request_path=norm_path,
                headers=headers,
                query_params=query_params,
                body_bytes=body_bytes,
            )
        )
        return JSONResponse(
            content=sbx_payload,
            status_code=sbx_status,
            headers=sbx_headers,
        )

    core_status, core_payload, core_headers = await forward_legitimate_request(
        method=method,
        path=norm_path,
        headers=headers,
        query_params=query_params,
        body_bytes=body_bytes,
        session_id=decision.session.session_id,
        request_obj=request,
    )
    return JSONResponse(
        content=core_payload,
        status_code=core_status,
        headers=core_headers,
    )


@gateway_router.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    summary="Unified Deception Reverse-Proxy Catch-All Route",
)
async def gateway_catch_all_proxy(
    request: Request,
    full_path: str,
) -> Response:
    """
    Catch-all reverse-proxy endpoint inspecting every incoming HTTP request and
    transparently routing between `CORE_WEB_APP` and `PREWARMED_SANDBOX`.
    """
    return await process_gateway_request(request=request, full_path=f"/{full_path}")
