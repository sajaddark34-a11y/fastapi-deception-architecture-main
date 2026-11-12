"""
Unified Multi-Layer Orchestrator for FastAPI-Driven Deception Architecture (`run_all.py`).

Starts all five FastAPI microservices across the four architectural layers concurrently
inside a single asynchronous event loop for seamless execution and live demonstration:
  - Layer 1: Deception Gateway Reverse Proxy (`http://127.0.0.1:8000`)
  - Layer 2: Core Web Application & Honey Token Injector (`http://127.0.0.1:8001`)
  - Layer 3A: Isolation Sandbox Decoy Service (`http://127.0.0.1:8080`)
  - Layer 3B: Forensic Extraction Engine (`http://127.0.0.1:8090`)
  - Layer 4: Defender SOC Command Center Dashboard (`http://127.0.0.1:8500`)
"""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_dotenv_file(env_path: Path) -> None:
    """Load key=value pairs from `.env` if present without external dependencies."""
    if not env_path.is_file():
        return
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'").strip('"')
            if key and key not in os.environ:
                os.environ[key] = val
    except Exception:
        pass


_load_dotenv_file(PROJECT_ROOT / ".env")

os.environ.setdefault("CORE_WEB_APP_URL", "http://127.0.0.1:8001")
os.environ.setdefault("SANDBOX_POOL_URL", "http://127.0.0.1:8080")
os.environ.setdefault(
    "FORENSICS_VAULT_PATH", str(PROJECT_ROOT / "artifacts_vault")
)


def _is_port_in_use(host: str, port: int) -> bool:
    """Return True if a TCP port is currently bound on `host`."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


def _ensure_ports_free(_host: str, ports: Iterable[int]) -> None:
    """
    Detect and release stale local processes holding any of the required project ports
    so repeated single-click launches never fail with `Address already in use`.
    """
    my_pid = os.getpid()
    port_set = {int(p) for p in ports}
    if sys.platform.startswith("win"):
        try:
            out = subprocess.check_output(
                ["netstat", "-ano", "-p", "TCP"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            killed_pids: set[int] = set()
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 5 and parts[0].upper() == "TCP":
                    local_addr = parts[1]
                    state = parts[3].upper()
                    pid_str = parts[4]
                    if state == "LISTENING" and pid_str.isdigit():
                        pid = int(pid_str)
                        if (
                            pid != my_pid
                            and pid > 0
                            and pid not in killed_pids
                            and any(local_addr.endswith(f":{p}") for p in port_set)
                        ):
                            killed_pids.add(pid)
                            subprocess.run(
                                ["taskkill", "/PID", str(pid), "/T", "/F"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                check=False,
                            )
        except Exception:
            pass


import uvicorn  # noqa: E402
from core_web_app.database_connector.session_manager import (  # noqa: E402
    init_and_seed_core_db,
)
from core_web_app.main import app as core_app  # noqa: E402
from data_storage.postgresql_store import init_forensic_database  # noqa: E402
from data_storage.redis_store import (  # noqa: E402
    fast_alerts_stream,
    session_state_store,
)
from deception_gateway.main import (  # noqa: E402
    TCPL4DeceptionProtocol,
     app as gateway_app,
    arm_l4_scan_detection,
)
from forensic_extraction_engine.engine_service import (  # noqa: E402
    app as forensic_app,
    forensic_engine_service,
)
from isolation_sandbox.isolated_honey_containers.decoy_service_app import (  # noqa: E402
    app as sandbox_app,
)
from isolation_sandbox.prewarmed_dynamic_sandbox import (  # noqa: E402
    prewarmed_pool_controller,
)
from soc_dashboard.dashboard_server import app as soc_app  # noqa: E402


def _get_lan_ip() -> str:
    """Detect the primary non-loopback IPv4 address for VM/LAN access."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def _print_startup_banner(
    host: str,
    gateway_port: int,
    core_port: int,
    sandbox_port: int,
    forensic_port: int,
    soc_port: int,
) -> None:
    """Display structured startup information, URLs, and test credentials."""
    display_host = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    lan_ip = _get_lan_ip()
    banner = f"""
================================================================================
  FASTAPI-DRIVEN DECEPTION ARCHITECTURE - ALL 4 LAYERS ONLINE
================================================================================
  [Layer 1] Deception Gateway (Local)    : http://{display_host}:{gateway_port}
            Deception Gateway (LAN / VM) : http://{lan_ip}:{gateway_port}
            Gateway Swagger UI           : http://{display_host}:{gateway_port}/docs
            Gateway Health Check         : http://{display_host}:{gateway_port}/gateway/health

  [Layer 2] Core Web Application         : http://{display_host}:{core_port}
            Core App Swagger UI          : http://{display_host}:{core_port}/docs
            Legitimate Records (via GW)  : http://{display_host}:{gateway_port}/api/v1/records

  [Layer 3] Isolation Honey Sandbox      : http://{display_host}:{sandbox_port}/docs
            Forensic Extraction Engine   : http://{display_host}:{forensic_port}/docs

  [Layer 4] Defender SOC Command Center  : http://{display_host}:{soc_port}
            SOC Dashboard Swagger UI     : http://{display_host}:{soc_port}/docs
            SOC Health Check             : http://{display_host}:{soc_port}/health
--------------------------------------------------------------------------------
  DEFAULT CREDENTIALS (Legitimate Core App Login):
    - Admin    : sec_admin   / EnterpriseAdmin#2026!
    - Engineer : devops_lead / DevOpsLead#2026!
    - Auditor  : soc_auditor / SocAuditor#2026!

  QUICK LIVE ATTACK DEMO:
    1. Open SOC Dashboard : http://{display_host}:{soc_port}
    2. Trigger Honey Trap : http://{display_host}:{gateway_port}/api/v1/internal/vault-keys
    3. Run Sandbox Shell  : http://{display_host}:{gateway_port}/api/v1/internal/debug-console?cmd=whoami
================================================================================
"""
    print(banner, flush=True)


async def run_all_layers() -> None:
    """Initialize storage/sandbox pools, attach telemetry hooks, and serve all 5 apps."""
    Path(os.environ["FORENSICS_VAULT_PATH"]).mkdir(parents=True, exist_ok=True)

    host = os.getenv("BIND_HOST", "0.0.0.0")
    check_host = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    gateway_port = int(os.getenv("GATEWAY_PORT", "8000"))
    core_port = int(os.getenv("CORE_APP_PORT", "8001"))
    sandbox_port = int(os.getenv("DECOY_SERVICE_PORT", "8080"))
    forensic_port = int(os.getenv("FORENSIC_ENGINE_PORT", "8090"))
    soc_port = int(os.getenv("SOC_DASHBOARD_PORT", "8500"))

    _ensure_ports_free(
        check_host,
        [gateway_port, core_port, sandbox_port, forensic_port, soc_port],
    )

    # Pre-initialize storage, prewarmed sandbox pool, and telemetry hooks in order
    await session_state_store.health_check()
    await fast_alerts_stream.ensure_consumer_group()
    await init_forensic_database()
    await init_and_seed_core_db()
    await prewarmed_pool_controller.initialize_warm_pool()
    forensic_engine_service.attach_sandbox_telemetry_hook()

    _print_startup_banner(
        host=host,
        gateway_port=gateway_port,
        core_port=core_port,
        sandbox_port=sandbox_port,
        forensic_port=forensic_port,
        soc_port=soc_port,
    )

    servers = [
        uvicorn.Server(
            uvicorn.Config(
                core_app,
                host=host,
                port=core_port,
                log_level="info",
                http=TCPL4DeceptionProtocol,
            )
        ),
        uvicorn.Server(
            uvicorn.Config(
                sandbox_app,
                host=host,
                port=sandbox_port,
                log_level="info",
                http=TCPL4DeceptionProtocol,
            )
        ),
        uvicorn.Server(
            uvicorn.Config(
                forensic_app,
                host=host,
                port=forensic_port,
                log_level="info",
                http=TCPL4DeceptionProtocol,
            )
        ),
        uvicorn.Server(
            uvicorn.Config(
                gateway_app,
                host=host,
                port=gateway_port,
                log_level="info",
                http=TCPL4DeceptionProtocol,
            )
        ),
        uvicorn.Server(
            uvicorn.Config(soc_app, host=host, port=soc_port, log_level="info")
        ),
    ]

    async def _open_browser_when_ready() -> None:
        for _ in range(50):
            if _is_port_in_use(check_host, soc_port) and _is_port_in_use(check_host, gateway_port):
                break
            await asyncio.sleep(0.2)
        await asyncio.sleep(0.3)
        arm_l4_scan_detection(True)
        if os.getenv("AUTO_OPEN_BROWSER", "true").lower() in ("0", "false", "no"):
            return
        try:
            # Open Layer 4 SOC Command Center Dashboard GUI, Decoy Login Portal, and Gateway Swagger UI
            webbrowser.open(f"http://{check_host}:{soc_port}")
            webbrowser.open_new_tab(f"http://{check_host}:{soc_port}/login")
            webbrowser.open_new_tab(f"http://{check_host}:{gateway_port}/docs")
        except Exception:
            pass

    asyncio.create_task(_open_browser_when_ready())
    await asyncio.gather(*(s.serve() for s in servers))


if __name__ == "__main__":
    try:
        asyncio.run(run_all_layers())
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down FastAPI Deception Architecture services...")
