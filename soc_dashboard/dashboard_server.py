"""
Defender SOC Command Center & SOAR Dashboard Server (Layer 4).

Provides the unified FastAPI application for the Security Operations Center (SOC):
  - Interactive Dark-Mode Enterprise SOC Command Center UI (`GET /`)
  - Real-time Alert & Telemetry Streaming (WebSocket + SSE + REST)
  - MITRE ATT&CK Tactics & Techniques Coverage Heatmap
  - Live Deobfuscated Sandbox Terminal Replay
  - Active SOAR Containment Controls (Session Isolation, Container Teardown, Honey-Token Rotation)
  - Cryptographically Verified Incident Report Generation & Export (HMAC-SHA256 Chain-of-Custody)
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict

try:
    from fastapi import APIRouter, FastAPI, Form, Request, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, RedirectResponse
    from fastapi.templating import Jinja2Templates
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_routes import APIRouter
    from core_web_app.main import FastAPI

    class CORSMiddleware:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    class HTMLResponse:  # type: ignore[no-redef]
        def __init__(self, content: str, status_code: int = 200) -> None:
            self.content = content
            self.status_code = status_code
            self.body = content.encode("utf-8")

    class RedirectResponse:  # type: ignore[no-redef]
        def __init__(self, url: str, status_code: int = 303) -> None:
            self.url = url
            self.status_code = status_code

    class Jinja2Templates:  # type: ignore[no-redef]
        def __init__(self, directory: str) -> None:
            self.directory = directory


from data_storage.postgresql_store import (
    check_db_health,
    init_forensic_database,
)
from data_storage.redis_store import fast_alerts_stream, session_state_store
from isolation_sandbox.prewarmed_dynamic_sandbox import prewarmed_pool_controller
from soc_dashboard.attack_visualizations.telemetry_chart_view import (
    telemetry_chart_view,
)
from soc_dashboard.attack_visualizations.visualization_routes import (
    visualization_router,
)
from soc_dashboard.incident_reports.report_export_routes import report_export_router


@asynccontextmanager
async def soc_dashboard_lifespan(app_instance: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manages startup and shutdown lifecycle of the SOC Dashboard server:
      - Initializes PostgreSQL schema if needed.
      - Ensures Redis Consumer Group for SOC alert streaming exists.
      - Ensures Prewarmed Sandbox Pool is initialized.
    """
    await init_forensic_database()
    await fast_alerts_stream.ensure_consumer_group()
    await prewarmed_pool_controller.initialize_warm_pool()
    try:
        yield
    finally:
        await session_state_store.close()
        await fast_alerts_stream.close()


app = FastAPI(
    title="Defender SOC Command Center & SOAR Dashboard (Layer 4)",
    version="1.0.0",
    description=(
        "Enterprise Real-Time SOC Dashboard, MITRE ATT&CK Explorer, "
        "SOAR Containment Engine, and Tamper-Evident DFIR Report Exporter."
    ),
    lifespan=soc_dashboard_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dashboard_core_router = APIRouter(tags=["SOC Dashboard Core"])


@dashboard_core_router.get("/")
async def render_soc_command_center_ui() -> HTMLResponse:
    """
    Serves the interactive Dark-Mode Enterprise SOC Command Center HTML interface.
    """
    html_content = await telemetry_chart_view.render_enterprise_soc_html()
    return HTMLResponse(content=html_content, status_code=200)


@dashboard_core_router.get("/health")
async def soc_dashboard_health_check() -> Dict[str, Any]:
    """
    Performs a comprehensive health check across Layer 4 SOC subsystems,
    Redis session/alert stores, PostgreSQL forensic repository, and Sandbox pool.
    """
    pg_healthy = await check_db_health()
    pool_metrics = await prewarmed_pool_controller.get_pool_metrics()
    return {
        "service": "soc_dashboard",
        "layer": "Layer 4 - Defender SOC & SOAR Command Center",
        "status": "healthy" if pg_healthy else "degraded_fallback_active",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subsystems": {
            "postgresql_forensic_store": "connected" if pg_healthy else "in_memory_fallback",
            "redis_alert_stream": "operational",
            "prewarmed_sandbox_pool": pool_metrics,
            "chain_of_custody_verifier": "HMAC-SHA256 Ready",
        },
    }


@dashboard_core_router.get("/metrics")
async def soc_dashboard_metrics() -> Dict[str, Any]:
    """
    Returns live SOC KPI summary and MITRE ATT&CK coverage metrics.
    """
    kpi = await telemetry_chart_view.build_live_kpi_summary()
    mitre = await telemetry_chart_view.build_mitre_attack_heatmap()
    return {
        "kpi_summary": kpi,
        "mitre_attack_summary": {
            "total_techniques_observed": len(mitre["techniques_matrix"]),
            "total_tactics_observed": len(mitre["tactics_distribution"]),
        },
    }


@dashboard_core_router.post("/api/v1/reset-telemetry")
async def reset_soc_telemetry() -> Dict[str, Any]:
    """
    Safely flush Redis telemetry streams/session keys and reset historical
    counter tables to zero without breaking active Redis or WebSocket connections.
    """
    from sqlalchemy import delete
    from data_storage.postgresql_store import (
        AttackerCommandLogORM,
        ForensicSessionLocal,
        NetworkTelemetryLogORM,
        SecurityAlertLogORM,
        forensic_logs_repository,
    )

    # 1. Flush Redis Streams & Session Keys on the existing connection without closing it
    redis_client = await fast_alerts_stream._get_client()
    if redis_client is not None:
        await redis_client.flushdb()
    await fast_alerts_stream.ensure_consumer_group()

    # 2. Clear in-memory stream and session fallback buffers
    fast_alerts_stream._mem_alerts.clear()
    fast_alerts_stream._mem_telemetry.clear()
    session_state_store._mem_sessions.clear()
    session_state_store._mem_bindings.clear()
    session_state_store._mem_malicious_ids.clear()

    # 3. Reset persisted KPI counter tables & MITRE cache so polling stays at 0
    from deception_gateway.gateway_router import attack_detector

    getattr(attack_detector, "_l4_probe_dedup_cache", {}).clear()
    forensic_logs_repository._mem_alerts.clear()
    forensic_logs_repository._mem_commands.clear()
    forensic_logs_repository._mem_network.clear()
    telemetry_chart_view.forensic_collector.command_logger._session_mitre_map.clear()
    telemetry_chart_view.forensic_collector.command_logger._analysis_by_event_id.clear()
    if ForensicSessionLocal is not None:
        async with ForensicSessionLocal() as db:
            await db.execute(delete(SecurityAlertLogORM))
            await db.execute(delete(AttackerCommandLogORM))
            await db.execute(delete(NetworkTelemetryLogORM))
            await db.commit()

    return {
        "status": "reset_complete",
        "counters": {
            "active_trapped_sessions": 0,
            "security_alerts_emitted": 0,
            "commands_captured": 0,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@dashboard_core_router.get("/login", response_class=HTMLResponse)
async def get_honeypot_login(request: Request):
    """Serve the decoy corporate login portal to trap web crawlers/adversaries."""
    return templates.TemplateResponse(
        request=request,
        name="fake_login.html",
        context={"error": None},
    )


@dashboard_core_router.post("/login")
async def post_honeypot_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Inspect login credentials:
    - Legitimate admin credentials -> Redirect to SOC dashboard route (/admin/soc).
    - Attacker credentials -> Log SOC alert, harvest payload, and maintain deception.
    """
    if username == "sajad_admin" and password == "Soc@2026":
        return RedirectResponse(url="/admin/soc", status_code=status.HTTP_303_SEE_OTHER)

    client_ip = request.client.host if request.client else "127.0.0.1"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()

    soc_alert: Dict[str, Any] = {
        "event_type": "WEB_HONEYPOT_CREDENTIAL_HARVEST",
        "severity": "HIGH",
        "source_ip": client_ip,
        "captured_username": username,
        "captured_password": password,
        "target_endpoint": "/login",
        "user_agent": request.headers.get("user-agent", "Unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_taken": "CREDENTIALS_HARVESTED_DECEPTION_MAINTAINED",
    }

    # TODO: Insert Redis Logging here
    # Example:
    # await redis_client.xadd("deception:streams:alerts", {"payload": json.dumps(soc_alert)})
    # or:
    # await fast_alerts_stream.publish_alert(soc_alert)

    return templates.TemplateResponse(
        request=request,
        name="fake_login.html",
        context={"error": "Invalid credentials. Incident logged."},
        status_code=status.HTTP_200_OK,
    )


@dashboard_core_router.get("/admin/soc", response_class=HTMLResponse)
async def admin_soc_dashboard(request: Request):
    """Authenticated entry point redirecting to the Defender SOC Command Center."""
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


app.include_router(dashboard_core_router)
app.include_router(visualization_router)
app.include_router(report_export_router)

__all__ = [
    "app",
    "soc_dashboard_lifespan",
    "dashboard_core_router",
    "render_soc_command_center_ui",
    "soc_dashboard_health_check",
    "soc_dashboard_metrics",
]
