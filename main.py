"""
Main FastAPI Application Entry Point (`main.py`).

Provides the Web-Level Honeypot & Decoy Login Portal (`/login`),
authenticated redirect to Defender SOC Command Center (`/admin/soc`),
and integrates with the 4-layer Deception Architecture.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from soc_dashboard.dashboard_server import app as soc_app

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Use the established SOC Dashboard application instance
app = soc_app


@app.get("/login", response_class=HTMLResponse)
async def get_honeypot_login(request: Request):
    """Serve the decoy corporate login portal to trap web crawlers/adversaries."""
    return templates.TemplateResponse(
        request=request,
        name="fake_login.html",
        context={"error": None},
    )


@app.post("/login")
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
    # Check if credentials match hardcoded admin
    if username == "sajad_admin" and password == "Soc@2026":
        return RedirectResponse(url="/admin/soc", status_code=status.HTTP_303_SEE_OTHER)

    # Attacker / Honeypot Trigger
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


@app.get("/admin/soc", response_class=HTMLResponse)
async def admin_soc_dashboard(request: Request):
    """Authenticated entry point redirecting to the Defender SOC Command Center."""
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8500, reload=True)
