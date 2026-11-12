"""
Main FastAPI Application Entry Point (`main.py`).

Provides the E-Commerce Web Trap Storefront (`/`), Search Trap Endpoint (`/search_trap`),
and Unprotected Defender SOC Command Center (`/admin/soc`).
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from data_storage.postgresql_store import forensic_logs_repository
from data_storage.redis_store import fast_alerts_stream
from shared_contracts.alert_schema import (
    AlertSeverityEnum,
    AttackCategoryEnum,
    SecurityAlertContract,
)
from soc_dashboard.attack_visualizations.telemetry_chart_view import (
    telemetry_chart_view,
)
from soc_dashboard.dashboard_server import (
    dashboard_core_router,
    report_export_router,
    soc_dashboard_lifespan,
    visualization_router,
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Create the primary application instance
app = FastAPI(
    title="Defender SOC Command Center & E-Commerce Web Trap",
    version="1.0.0",
    lifespan=soc_dashboard_lifespan,
)


@app.get("/", response_class=HTMLResponse)
async def get_ecommerce_store(request: Request):
    """Serve the E-commerce Web Trap storefront (templates/index.html)."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"message": None, "search_query": ""},
    )


@app.post("/search_trap", response_class=HTMLResponse)
async def post_search_trap(
    request: Request,
    search_query: str = Form(""),
):
    """
    E-Commerce Search Honeypot Trap:
    Captures search/SQLi payloads, logs attacker telemetry, and maintains deception.
    """
    ip = request.client.host if request.client else "127.0.0.1"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()

    print(f"[WEB TRAP] SQLi/Search attempt from IP {ip}. Payload: {search_query}")

    # Emit real-time deception alert to Redis Streams and PostgreSQL logs
    try:
        session_id = request.headers.get("X-Session-ID") or f"sess_trap_{uuid.uuid4().hex[:8]}"
        alert = SecurityAlertContract(
            alert_id=f"alt_trap_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(timezone.utc),
            severity=AlertSeverityEnum.HIGH,
            category=AttackCategoryEnum.HONEY_TOKEN_TRIGGERED,
            source_ip=ip if ip != "testclient" else "127.0.0.1",
            session_id=session_id,
            target_endpoint="/search_trap",
            http_method="POST",
            action_taken="LOGGED_AND_DECEIVED",
            summary_message=f"E-Commerce search honeypot triggered by {ip}: payload '{search_query[:120]}'",
            raw_headers_snapshot=dict(request.headers),
        )
        await fast_alerts_stream.publish_alert(alert)
        await forensic_logs_repository.save_security_alert(alert)
    except Exception as exc:
        print(f"[WEB TRAP] Warning: Failed to publish trap alert to storage: {exc}")

    fake_message = f"No results found for: {search_query}"
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "message": fake_message,
            "search_query": search_query,
        },
        status_code=status.HTTP_200_OK,
    )


@app.get("/admin/soc", response_class=HTMLResponse)
async def get_open_soc_dashboard(request: Request):
    """Unprotected, direct entry point returning the SOC dashboard template."""
    html_content = await telemetry_chart_view.render_enterprise_soc_html()
    return HTMLResponse(content=html_content, status_code=200)


# Include SOC subsystems and routers
app.include_router(dashboard_core_router)
app.include_router(visualization_router)
app.include_router(report_export_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8500, reload=True)
