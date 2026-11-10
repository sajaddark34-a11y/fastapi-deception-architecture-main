"""
Unified Multi-Layer Launcher for FastAPI-Driven Deception Architecture (`run_all.py`).

Starts all four architectural layers concurrently inside a single asynchronous
event loop for seamless local execution and live demonstration:
  - Layer 1: Deception Gateway (`http://127.0.0.1:8000`)
  - Layer 2: Core Web Application (`http://127.0.0.1:8001`)
  - Layer 3: Isolation Sandbox & Forensic Extraction Hook (`http://127.0.0.1:8080`)
  - Layer 4: Defender SOC Dashboard (`http://127.0.0.1:8500`)
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("CORE_WEB_APP_URL", "http://127.0.0.1:8001")
os.environ.setdefault("SANDBOX_POOL_URL", "http://127.0.0.1:8080")
os.environ.setdefault(
    "FORENSICS_VAULT_PATH", str(PROJECT_ROOT / "artifacts_vault")
)

import uvicorn  # noqa: E402
from core_web_app.main import app as core_app  # noqa: E402
from deception_gateway.main import app as gateway_app  # noqa: E402
from forensic_extraction_engine.engine_service import (  # noqa: E402
    forensic_engine_service,
)
from isolation_sandbox.isolated_honey_containers.decoy_service_app import (  # noqa: E402
    app as sandbox_app,
)
from soc_dashboard.dashboard_server import app as soc_app  # noqa: E402


async def run_all_layers() -> None:
    """Attach forensic telemetry hooks and serve all four layers concurrently."""
    forensic_engine_service.attach_sandbox_telemetry_hook()

    host = os.getenv("BIND_HOST", "127.0.0.1")
    gateway_port = int(os.getenv("GATEWAY_PORT", "8000"))
    core_port = int(os.getenv("CORE_APP_PORT", "8001"))
    sandbox_port = int(os.getenv("DECOY_SERVICE_PORT", "8080"))
    soc_port = int(os.getenv("SOC_DASHBOARD_PORT", "8500"))

    servers = [
        uvicorn.Server(
            uvicorn.Config(gateway_app, host=host, port=gateway_port, log_level="info")
        ),
        uvicorn.Server(
            uvicorn.Config(core_app, host=host, port=core_port, log_level="info")
        ),
        uvicorn.Server(
            uvicorn.Config(sandbox_app, host=host, port=sandbox_port, log_level="info")
        ),
        uvicorn.Server(
            uvicorn.Config(soc_app, host=host, port=soc_port, log_level="info")
        ),
    ]
    await asyncio.gather(*(s.serve() for s in servers))


if __name__ == "__main__":
    asyncio.run(run_all_layers())
