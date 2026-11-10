"""
SOC Attack Visualization, Live WebSocket/SSE Streaming, and SOAR Control Routes
(`soc_dashboard.attack_visualizations.visualization_routes`).

Exposes `/api/v1/soc/visualizations` endpoints for real-time alert feeds,
SSE/WebSocket streaming, MITRE ATT&CK matrices, live sandbox terminal replay,
and SOAR automated response actions (manual IP/session isolation, container
teardown & sanitization, and honey-token rotation).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

try:
    from fastapi import APIRouter, HTTPException, Query, WebSocket, status
    from fastapi.responses import HTMLResponse, StreamingResponse
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_handler import (  # type: ignore[attr-defined]
        HTTPException,
        status,
    )
    from core_web_app.authentication.auth_routes import APIRouter  # type: ignore[attr-defined]
    from core_web_app.legitimate_request_routes import Query  # type: ignore[attr-defined]
    from core_web_app.main import Response  # type: ignore[attr-defined]

    class HTMLResponse(Response):  # type: ignore[no-redef]
        def __init__(self, content: str = "", status_code: int = 200) -> None:
            super().__init__(
                content=content,
                status_code=status_code,
                media_type="text/html; charset=utf-8",
            )

    class StreamingResponse(Response):  # type: ignore[no-redef]
        def __init__(
            self, content: Any = None, status_code: int = 200, media_type: str = "text/event-stream"
        ) -> None:
            super().__init__(content=b"", status_code=status_code, media_type=media_type)
            self.body_iterator = content

    class WebSocket:  # type: ignore[no-redef]
        async def accept(self) -> None:
            pass

        async def send_json(self, data: Any) -> None:
            pass

        async def close(self) -> None:
            pass

from data_storage.postgresql_store import forensic_logs_repository
from data_storage.redis_store import fast_alerts_stream, session_state_store
from honey_token_injector import (
    fake_header_generator,
    fake_url_generator,
    honey_token_validator,
)
from isolation_sandbox.prewarmed_dynamic_sandbox import (
    prewarmed_pool_controller,
    sandbox_session_binder,
)
from shared_contracts.alert_schema import (
    AlertSeverityEnum,
    AttackCategoryEnum,
    SecurityAlertContract,
)
from shared_contracts.session_schema import (
    RoutingTargetEnum,
    SessionStateContract,
    SessionStatusEnum,
)
from soc_dashboard.attack_visualizations.telemetry_chart_view import (
    telemetry_chart_view,
)

visualization_router = APIRouter(
    prefix="/api/v1/soc/visualizations",
    tags=["SOC Visualizations & SOAR Controls"],
)


class SOARIsolateSessionRequest(BaseModel):
    """Request schema for manual SOAR isolation of a suspicious session or IP."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    session_id: Optional[str] = Field(default=None, min_length=8, max_length=128)
    client_ip: str = Field(..., description="Attacker IPv4/IPv6 address to isolate.")
    reason: str = Field(
        default="Manual SOC analyst SOAR containment directive.",
        min_length=5,
        max_length=512,
    )


class SOARContainerTeardownRequest(BaseModel):
    """Request schema for SOAR container teardown or sanitization."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    session_id: str = Field(..., min_length=8, max_length=128)
    destroy_permanently: bool = Field(default=False)


class SOARRotateTokensRequest(BaseModel):
    """Request schema for SOAR rotation of active honey tokens."""

    model_config = ConfigDict(extra="forbid")

    header_tokens_count: int = Field(default=2, ge=1, le=4)
    include_decoy_cookie: bool = Field(default=True)
    include_fake_api_key: bool = Field(default=True)


@visualization_router.get(
    "/kpi",
    status_code=status.HTTP_200_OK,
    summary="Retrieve real-time SOC KPI cards and system metrics",
)
async def get_soc_kpi_summary() -> Dict[str, Any]:
    """Return real-time KPI statistics across Gateway, Sandbox, and Forensics."""
    return await telemetry_chart_view.build_live_kpi_summary()


@visualization_router.get(
    "/alerts/live",
    status_code=status.HTTP_200_OK,
    summary="Fetch recent real-time security alerts with optional severity filter",
)
async def get_live_alerts_feed(
    limit: int = Query(default=50, ge=1, le=200),
    min_severity: Optional[AlertSeverityEnum] = Query(default=None),
) -> Dict[str, Any]:
    """
    Retrieve the latest `SecurityAlertContract` items from `FastAlertsStream`
    (with automatic fallback to `ForensicLogsRepository`).
    """
    alerts = await fast_alerts_stream.get_recent_alerts(
        limit=limit, min_severity=min_severity
    )
    if not alerts:
        alerts = await forensic_logs_repository.get_alerts_history(limit=limit)

    return {
        "count": len(alerts),
        "alerts": [a.model_dump(mode="json") for a in alerts],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


async def _sse_alert_event_generator(
    max_events: int = 10,
) -> AsyncGenerator[str, None]:
    """Yield Server-Sent Events (SSE) formatted alert payloads for live SOC streaming."""
    recent = await fast_alerts_stream.get_recent_alerts(limit=max_events)
    for alert in reversed(recent):
        yield f"event: security_alert\ndata: {alert.model_dump_json()}\n\n"


@visualization_router.get(
    "/alerts/sse",
    status_code=status.HTTP_200_OK,
    summary="Server-Sent Events (SSE) real-time alert stream",
)
async def stream_alerts_sse() -> StreamingResponse:
    """Stream security alerts over Server-Sent Events (`text/event-stream`)."""
    return StreamingResponse(
        _sse_alert_event_generator(),
        media_type="text/event-stream",
    )


@visualization_router.get(
    "/mitre-matrix",
    status_code=status.HTTP_200_OK,
    summary="Retrieve aggregated MITRE ATT&CK Tactics and Techniques heatmap",
)
async def get_mitre_attack_matrix() -> Dict[str, Any]:
    """Return the MITRE ATT&CK heatmap across all trapped sessions."""
    return await telemetry_chart_view.build_mitre_attack_heatmap()


@visualization_router.get(
    "/sessions/malicious",
    status_code=status.HTTP_200_OK,
    summary="List all active trapped and isolated attacker sessions",
)
async def list_malicious_sessions() -> Dict[str, Any]:
    """
    Return all active sessions in `MALICIOUS_TRAPPED` or `ISOLATED` status along
    with their active `SandboxBindingContract` records.
    """
    sessions = await session_state_store.list_active_malicious_sessions()
    enriched: List[Dict[str, Any]] = []
    for sess in sessions:
        binding = await session_state_store.get_active_sandbox_binding(sess.session_id)
        enriched.append(
            {
                "session": sess.model_dump(mode="json"),
                "sandbox_binding": (
                    binding.model_dump(mode="json") if binding else None
                ),
            }
        )
    return {
        "active_malicious_sessions_count": len(enriched),
        "sessions": enriched,
    }


@visualization_router.get(
    "/sessions/{session_id}/terminal-replay",
    status_code=status.HTTP_200_OK,
    summary="Retrieve live sandbox terminal command replay and IOCs for a session",
)
async def get_session_terminal_replay(session_id: str) -> Dict[str, Any]:
    """Return the de-obfuscated terminal command replay, eBPF traces, and C2 callbacks."""
    return await telemetry_chart_view.build_sandbox_terminal_replay(session_id)


@visualization_router.get(
    "/sandbox/pool-status",
    status_code=status.HTTP_200_OK,
    summary="Inspect Pre-Warmed Sandbox Container Pool status and quotas",
)
async def get_sandbox_pool_status() -> Dict[str, Any]:
    """Return real-time capacity and container lifecycle state of `isolation_sandbox`."""
    return await prewarmed_pool_controller.get_pool_metrics()


@visualization_router.post(
    "/soar/isolate-session",
    status_code=status.HTTP_200_OK,
    summary="SOAR Action: Manually isolate an IP or session into the Honey Sandbox",
)
async def soar_isolate_session(
    payload: SOARIsolateSessionRequest,
) -> Dict[str, Any]:
    """
    SOAR Containment Action: Immediately escalate a target session or IP to
    `ISOLATED` (`risk_score=100.0`), bind it to a prewarmed honey container,
    and broadcast a `CRITICAL` security alert.
    """
    existing = None
    if payload.session_id:
        existing = await session_state_store.get_session(payload.session_id)
    if existing is None:
        existing = await session_state_store.get_session_by_ip(payload.client_ip)

    now_utc = datetime.now(timezone.utc)
    target_sid = (
        existing.session_id
        if existing is not None
        else (payload.session_id or str(uuid.uuid4()))
    )

    binding = await sandbox_session_binder.get_or_create_binding(
        session_id=target_sid
    )

    if existing is not None:
        isolated_session = existing.model_copy(
            update={
                "status": SessionStatusEnum.ISOLATED,
                "routing_target": RoutingTargetEnum.PREWARMED_SANDBOX,
                "risk_score": 100.0,
                "assigned_container_id": binding.container_id,
                "last_active_at": max(now_utc, existing.first_seen_at),
            }
        )
    else:
        isolated_session = SessionStateContract(
            session_id=target_sid,
            client_ip=payload.client_ip,
            user_agent="SOAR-Manual-Isolation-Target",
            status=SessionStatusEnum.ISOLATED,
            routing_target=RoutingTargetEnum.PREWARMED_SANDBOX,
            risk_score=100.0,
            triggered_token_id=None,
            assigned_container_id=binding.container_id,
            request_count=1,
            first_seen_at=now_utc,
            last_active_at=now_utc,
            ttl_seconds=3600,
        )

    await session_state_store.upsert_session(isolated_session)

    alert = SecurityAlertContract(
        alert_id=f"alt_soar_{uuid.uuid4().hex[:12]}",
        timestamp=now_utc,
        severity=AlertSeverityEnum.CRITICAL,
        category=AttackCategoryEnum.UNAUTHORIZED_PATH_ACCESS,
        source_ip=isolated_session.client_ip,
        session_id=isolated_session.session_id,
        triggered_token_id=None,
        target_endpoint="/soar/manual-isolation",
        http_method="POST",
        action_taken="SOAR_ISOLATED_TO_SANDBOX",
        summary_message=(
            f"SOAR manual containment executed against {isolated_session.client_ip} "
            f"(session {isolated_session.session_id}): {payload.reason}"
        ),
        raw_headers_snapshot={"X-SOAR-Action": "ISOLATE_SESSION"},
    )
    await fast_alerts_stream.publish_alert(alert)
    await forensic_logs_repository.save_security_alert(alert)

    return {
        "soar_action": "ISOLATE_SESSION",
        "status": "executed",
        "isolated_session": isolated_session.model_dump(mode="json"),
        "sandbox_binding": binding.model_dump(mode="json"),
        "alert_id": alert.alert_id,
    }


@visualization_router.post(
    "/soar/teardown-container",
    status_code=status.HTTP_200_OK,
    summary="SOAR Action: Teardown or sanitize an active sandbox container",
)
async def soar_teardown_container(
    payload: SOARContainerTeardownRequest,
) -> Dict[str, Any]:
    """
    SOAR Containment Action: Release a session's sandbox container binding,
    sanitize or permanently destroy the container, and replenish the warm pool.
    """
    released = await sandbox_session_binder.unbind_and_recycle_session(
        session_id=payload.session_id,
        destroy_container=payload.destroy_permanently,
    )
    pool_metrics = await prewarmed_pool_controller.get_pool_metrics()
    return {
        "soar_action": "TEARDOWN_AND_SANITIZE_CONTAINER",
        "session_id": payload.session_id,
        "destroyed_permanently": payload.destroy_permanently,
        "released": released,
        "pool_status": pool_metrics,
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }


@visualization_router.post(
    "/soar/rotate-honey-tokens",
    status_code=status.HTTP_201_CREATED,
    summary="SOAR Action: Generate and rotate fresh cryptographic Honey Tokens",
)
async def soar_rotate_honey_tokens(
    payload: SOARRotateTokensRequest,
) -> Dict[str, Any]:
    """
    SOAR Deception Action: Issue a fresh batch of HMAC-SHA256 signed header,
    cookie, decoy URL, and fake API key honey tokens and register them with
    `HoneyTokenValidator`.
    """
    issued_contracts = []
    hdr_tokens = fake_header_generator.generate_header_bundle(
        count=payload.header_tokens_count
    )
    issued_contracts.extend(hdr_tokens)

    if payload.include_decoy_cookie:
        issued_contracts.append(
            fake_header_generator.generate_decoy_cookie_token()
        )
    if payload.include_fake_api_key:
        issued_contracts.append(
            fake_url_generator.generate_fake_api_key_token()
        )
    issued_contracts.append(fake_url_generator.generate_hidden_url_token())

    for tok in issued_contracts:
        honey_token_validator.register_token(tok)

    return {
        "soar_action": "ROTATE_HONEY_TOKENS",
        "status": "executed",
        "rotated_count": len(issued_contracts),
        "tokens": [t.model_dump(mode="json") for t in issued_contracts],
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }


@visualization_router.websocket("/alerts/ws")
async def handle_alerts_websocket(websocket: WebSocket) -> None:
    """
    WebSocket handler streaming live `SecurityAlertContract` snapshots and
    subsequent real-time Pub/Sub alerts to connected SOC analysts.
    """
    await websocket.accept()
    try:
        recent = await fast_alerts_stream.get_recent_alerts(limit=10)
        for alert in reversed(recent):
            await websocket.send_json(
                json.loads(alert.model_dump_json())
            )
        async for live_alert in fast_alerts_stream.subscribe_alerts():
            await websocket.send_json(
                json.loads(live_alert.model_dump_json())
            )
    except Exception:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
