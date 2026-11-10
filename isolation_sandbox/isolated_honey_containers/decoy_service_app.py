"""
High-Interaction Decoy Service Application, Fake Linux Filesystem, SQLi Emulator,
and Simulated Interactive Shell (`isolation_sandbox.isolated_honey_containers.decoy_service_app`).

Provides the deceptive server environment inside isolated honey containers (`port 8080`).
Responds convincingly to file-inclusion/traversal probes (`/etc/passwd`, `/.env`,
`/root/.ssh/id_rsa`), SQL injection queries, and interactive shell commands (`whoami`,
`id`, `uname -a`, `ls -la`, `ps aux`, `netstat`, `cat`, `curl`, `wget`), while blocking
real outbound C2 connections and streaming full telemetry to `forensic_extraction_engine`.
"""

from __future__ import annotations

import base64
import logging
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, Dict, List, Mapping, Optional, Tuple

try:
    from fastapi import APIRouter, FastAPI, Request
    from fastapi.responses import JSONResponse, Response
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_routes import (  # type: ignore[attr-defined]
        APIRouter,
        Request,
    )
    from core_web_app.main import FastAPI, JSONResponse, Response  # type: ignore[attr-defined]

from isolation_sandbox.docker_sandbox_manager import (
    DockerSandboxManager,
    docker_sandbox_manager,
)
from isolation_sandbox.prewarmed_dynamic_sandbox import (
    SandboxSessionBinder,
    sandbox_session_binder,
)

logger = logging.getLogger(__name__)

_OUTBOUND_URL_REGEX = re.compile(
    r"https?://([a-zA-Z0-9.\-_]+)(?::(\d+))?(/[^\s\"'|;&]*)?",
    re.IGNORECASE,
)


class DecoyLinuxFilesystem:
    """
    Simulated high-value Linux enterprise filesystem serving realistic bait files
    when attackers attempt Local File Inclusion (LFI), Path Traversal, or `cat` commands.
    """

    VIRTUAL_FILES: Dict[str, str] = {
        "/etc/passwd": (
            "root:x:0:0:root:/root:/bin/bash\n"
            "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
            "www-data:x:33:33:www-data:/var/www:/bin/bash\n"
            "postgres:x:109:117:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash\n"
            "devops:x:1001:1001:Enterprise DevOps Lead,,,:/home/devops:/bin/bash\n"
            "vault-svc:x:1002:1002:HashiCorp Vault Service,,,:/opt/vault:/usr/sbin/nologin\n"
        ),
        "/etc/shadow": (
            "root:$6$9kLmN8pQ$e8W2vXyZ1aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789abcdef.:19665:0:99999:7:::\n"
            "www-data:*:19665:0:99999:7:::\n"
            "devops:$6$saltsalt$7f8e9d0c1b2a3f4e5d6c7b8a90123456789abcdef0123456789.:19665:0:99999:7:::\n"
        ),
        "/etc/hosts": (
            "127.0.0.1\tlocalhost\n"
            "172.29.0.15\tprd-api-node-01.enterprise.internal prd-api-node-01\n"
            "10.240.12.88\tprd-postgres-master.enterprise.internal\n"
            "10.240.12.95\tprd-hsm-vault.enterprise.internal\n"
        ),
        "/.env": (
            "APP_ENV=production_staging_mirror\n"
            "DB_CONNECTION=postgresql+asyncpg://fin_admin:Prd_Vault_DB#9912@10.240.12.88:5432/sovereign_ledger\n"
            "REDIS_SENTINEL_URL=redis://10.240.12.90:6379/0\n"
            "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7DECOY99\n"
            "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYDECOYKEY\n"
            "VAULT_ROOT_UNSEAL_TOKEN=hvs.CAESIJ9m8n7b6v5c4x3z2a1_decoy_root\n"
        ),
        "/.git/config": (
            "[core]\n"
            "\trepositoryformatversion = 0\n"
            "\tfilemode = true\n"
            "[remote \"origin\"]\n"
            "\turl = https://git-deploy:glpat-9f8e7d6c5b4a3210@git.enterprise.internal/core/sovereign-api.git\n"
            "\tfetch = +refs/heads/*:refs/remotes/origin/*\n"
        ),
        "/root/.ssh/id_rsa": (
            "-----BEGIN OPENSSH PRIVATE KEY-----\n"
            "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn\n"
            "NhAAAAAwEAAQAAAIEA0Z9x8y7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g0f9e8d7c6b5a\n"
            "DECOY_SSH_PRIVATE_KEY_MATERIAL_FOR_FORENSIC_TRACKING_ONLY_2026==\n"
            "-----END OPENSSH PRIVATE KEY-----\n"
        ),
        "/home/devops/.aws/credentials": (
            "[default]\n"
            "aws_access_key_id = AKIAIOSFODNN7DECOY99\n"
            "aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYDECOYKEY\n"
            "region = eu-central-1\n"
        ),
        "/proc/self/environ": (
            "HOSTNAME=prd-api-node-01\n"
            "SERVICE_NAME=core_web_app\n"
            "INTERNAL_DEBUG_TOKEN=dbg_live_decoy_998877\n"
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
        ),
    }

    @classmethod
    def read_file(cls, path_or_query: str) -> Optional[Tuple[str, str]]:
        """
        Match a requested file path (including `../` traversal normalization) against
        the virtual decoy filesystem.

        Returns:
            Tuple of `(canonical_file_path, file_content)` if matched, else `None`.
        """
        cleaned = path_or_query.strip()
        for vpath, content in cls.VIRTUAL_FILES.items():
            basename = vpath.lstrip("/")
            if vpath in cleaned or basename in cleaned:
                return vpath, content
        return None


class DecoySQLDatabaseEmulator:
    """
    Emulates vulnerable SQL Injection query outputs to keep automated SQLi tools
    (like `sqlmap`) and manual attackers engaged inside the sandbox.
    """

    DECOY_TABLES: List[Dict[str, Any]] = [
        {
            "table_name": "enterprise_users",
            "rows": [
                {
                    "id": 1,
                    "username": "sec_admin",
                    "email": "sec_admin@enterprise.internal",
                    "password_hash": "$2b$12$9f8e7d6c5b4a3f2e1d0c.DecoyHashValue001",
                    "mfa_secret": "JBSWY3DPEHPK3PXP",
                },
                {
                    "id": 2,
                    "username": "treasury_controller",
                    "email": "treasury@enterprise.internal",
                    "password_hash": "$2b$12$1a2b3c4d5e6f7a8b9c0d.DecoyHashValue002",
                    "mfa_secret": "KRSXG5CTMVRXEZLU",
                },
            ],
        },
        {
            "table_name": "hsm_vault_keys",
            "rows": [
                {
                    "key_id": "hsm_master_01",
                    "key_alias": "swift_settlement_signing_key",
                    "vault_token": "hvs.CAESIJ9m8n7b6v5c4x3z2a1_decoy",
                }
            ],
        },
    ]

    @classmethod
    def evaluate_sqli_probe(cls, raw_input: str) -> Optional[Dict[str, Any]]:
        """
        Check if `raw_input` contains SQL injection syntax and return a realistic
        leaked recordset dictionary.
        """
        lowered = raw_input.lower()
        if any(
            sig in lowered
            for sig in ("union select", "union all select", "' or ", "1=1", "information_schema", "pg_sleep")
        ):
            return {
                "database_engine": "PostgreSQL 16.2 (Debian 16.2-1.pgdg120+2)",
                "current_database": "sovereign_ledger",
                "current_user": "fin_admin",
                "extracted_tables": cls.DECOY_TABLES,
            }
        return None


class SimulatedInteractiveShell:
    """
    High-interaction simulated Linux shell responder that executes attacker commands
    in a virtualized sandbox context, intercepts outbound `curl`/`wget` C2 downloads,
    and returns realistic stdout, exit codes, and process metadata.
    """

    def __init__(
        self,
        sandbox_manager: Optional[DockerSandboxManager] = None,
    ) -> None:
        self.sandbox_manager: DockerSandboxManager = (
            sandbox_manager or docker_sandbox_manager
        )

    async def execute_command(
        self,
        session_id: str,
        container_id: str,
        container_ip: str,
        command_line: str,
        working_directory: str = "/var/www/enterprise-decoy",
    ) -> Dict[str, Any]:
        """
        Simulate execution of an attacker shell command and return structured process
        output (`stdout`, `exit_code`, `process_id`, `parent_process_id`, `executed_by_user`,
        `intercepted_egress`).
        """
        cmd_clean = urllib.parse.unquote(command_line.strip())
        b64_pipe = re.search(
            r"echo\s+['\"]?([A-Za-z0-9+/]{8,}={0,2})['\"]?\s*\|\s*base64\s+-d",
            cmd_clean,
            re.IGNORECASE,
        )
        if b64_pipe:
            try:
                decoded_inner = base64.b64decode(b64_pipe.group(1)).decode(
                    "utf-8", errors="replace"
                )
                cmd_clean = f"{cmd_clean} ; {decoded_inner}"
            except Exception:
                pass
        cmd_lower = cmd_clean.lower()
        executed_by = "root" if "sudo " in cmd_lower else "www-data"
        outputs: List[str] = []
        intercepted_egress: List[Dict[str, Any]] = []

        # Intercept any outbound URLs in curl / wget / http commands
        for match in _OUTBOUND_URL_REGEX.finditer(cmd_clean):
            host = match.group(1)
            port_str = match.group(2)
            uri_path = match.group(3) or "/"
            port = int(port_str) if port_str else (443 if "https://" in match.group(0).lower() else 80)
            egress_rec = await self.sandbox_manager.intercept_outbound_egress(
                container_id=container_id,
                session_id=session_id,
                destination_ip=host if re.match(r"^\d+\.\d+\.\d+\.\d+$", host) else "198.51.100.200",
                destination_port=port,
                protocol="TCP",
                payload_preview=f"GET {uri_path} Host: {host}",
            )
            intercepted_egress.append(egress_rec)
            outputs.append(
                f"--2026-11-05--  Connecting to {host}:{port}... connected.\n"
                f"HTTP request sent, awaiting response... 200 OK\n"
                f"Length: 2048 (2.0K) [application/x-sh]\n"
                f"Saving to: '/tmp/{uri_path.split('/')[-1] or 'payload.sh'}' [quarantined]"
            )

        if "whoami" in cmd_lower:
            outputs.append(executed_by)
        if re.search(r"\bid\b", cmd_lower):
            if executed_by == "root":
                outputs.append("uid=0(root) gid=0(root) groups=0(root)")
            else:
                outputs.append(
                    "uid=33(www-data) gid=33(www-data) groups=33(www-data),1001(devops)"
                )
        if "uname" in cmd_lower:
            outputs.append(
                f"Linux {container_id} 6.1.0-21-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.90-1 x86_64 GNU/Linux"
            )
        if "ls" in cmd_lower:
            outputs.append(
                "total 48\n"
                "drwxr-xr-x 5 www-data www-data 4096 Nov  5 00:01 .\n"
                "drwxr-xr-x 3 root     root     4096 Nov  5 00:00 ..\n"
                "-rw-r----- 1 www-data www-data  412 Nov  5 00:01 .env\n"
                "drwxr-xr-x 2 www-data www-data 4096 Nov  5 00:01 .git\n"
                "-rwxr-xr-x 1 www-data www-data 8192 Nov  5 00:01 app_server.py\n"
                "-rw-r----- 1 devops   devops   2048 Nov  5 00:01 vault_unseal_backup.key"
            )
        if "ps " in cmd_lower or cmd_lower == "ps":
            outputs.append(
                "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n"
                "root         1  0.1  0.4  24512 12400 ?        Ss   00:00   0:01 /usr/bin/python3 /app/server.py\n"
                "www-data  4096  0.3  1.2  68120 31200 ?        Sl   00:01   0:04 uvicorn core_web_app.main:app --port 8001\n"
                "www-data  4128  0.0  0.1   4216  1820 ?        R    00:12   0:00 /bin/sh -c "
                + cmd_clean[:60]
            )
        if "netstat" in cmd_lower or "ss " in cmd_lower or "ip a" in cmd_lower or "ifconfig" in cmd_lower:
            outputs.append(
                f"Active Internet connections (servers and established)\n"
                f"Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name\n"
                f"tcp        0      0 {container_ip}:8080      0.0.0.0:*               LISTEN      4096/python3\n"
                f"tcp        0      0 {container_ip}:49152     10.240.12.88:5432       ESTABLISHED 4096/python3"
            )
        if "cat " in cmd_lower or "head " in cmd_lower or "tail " in cmd_lower:
            matched_file = DecoyLinuxFilesystem.read_file(cmd_clean)
            if matched_file is not None:
                outputs.append(matched_file[1])
            else:
                outputs.append("# Decoy configuration file\nSECRET_KEY=decoy_991122aabbcc")
        if "env" in cmd_lower or "printenv" in cmd_lower:
            outputs.append(DecoyLinuxFilesystem.VIRTUAL_FILES["/.env"])

        if not outputs:
            outputs.append(
                f"[sh] executed ({executed_by}@{container_id}:{working_directory})$ {cmd_clean}"
            )

        return {
            "command_line": cmd_clean,
            "working_directory": working_directory,
            "executed_by_user": executed_by,
            "process_id": 4128,
            "parent_process_id": 4096,
            "exit_code": 0,
            "stdout": "\n".join(outputs),
            "intercepted_egress": intercepted_egress,
        }


TelemetryHookCallback = Callable[
    [Dict[str, Any]], Coroutine[Any, Any, Any]
]


class DecoyServiceApp:
    """
    Main High-Interaction Decoy Service orchestrator handling requests diverted by
    `MaliciousSessionRouter` in `deception_gateway`.
    """

    def __init__(
        self,
        session_binder: Optional[SandboxSessionBinder] = None,
        shell_emulator: Optional[SimulatedInteractiveShell] = None,
    ) -> None:
        self.session_binder: SandboxSessionBinder = (
            session_binder or sandbox_session_binder
        )
        self.shell_emulator: SimulatedInteractiveShell = (
            shell_emulator or SimulatedInteractiveShell()
        )
        self._telemetry_hooks: List[TelemetryHookCallback] = []

    def register_telemetry_hook(self, hook: TelemetryHookCallback) -> None:
        """Register an async callback (e.g., from `forensic_extraction_engine`) invoked on every interaction."""
        if hook not in self._telemetry_hooks:
            self._telemetry_hooks.append(hook)

    async def handle_trapped_request(
        self,
        session_id: str,
        client_ip: str = "127.0.0.1",
        request_method: str = "GET",
        request_path: str = "/",
        headers: Optional[Mapping[str, str]] = None,
        query_params: Optional[Mapping[str, str]] = None,
        body_bytes: bytes = b"",
        preferred_container_id: Optional[str] = None,
    ) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        """
        Process an attacker's HTTP request inside the isolated honey container:
        1. Ensure zero-latency session-to-container binding (`SandboxBindingContract`).
        2. Evaluate for shell commands, LFI/path traversal files, SQLi probes, or
           decoy endpoint accesses (`/api/v1/internal/vault-keys`, `/admin/debug/env-dump`, etc.).
        3. Notify registered forensic extraction hooks (`forensic_extraction_engine`).
        4. Return a realistic HTTP status code, JSON payload, and response headers.
        """
        binding = await self.session_binder.get_or_create_binding(
            session_id=session_id,
            preferred_container_id=preferred_container_id,
        )
        hdr_dict = {str(k): str(v) for k, v in (headers or {}).items()}
        qry_dict = {str(k): str(v) for k, v in (query_params or {}).items()}
        body_text = body_bytes.decode("utf-8", errors="replace") if body_bytes else ""
        norm_path = request_path if request_path.startswith("/") else f"/{request_path}"

        combined_probe = f"{norm_path} {' '.join(f'{k}={v}' for k, v in qry_dict.items())} {body_text}".strip()

        # Check explicit command execution or shell syntax
        explicit_cmd = (
            qry_dict.get("cmd")
            or qry_dict.get("exec")
            or qry_dict.get("command")
            or (body_text if any(tok in body_text for tok in ("whoami", "id", "uname", "cat ", "ls ", "curl ", "wget ", "ps ", "netstat", ";", "|")) else "")
        )
        if not explicit_cmd and any(
            kw in combined_probe.lower()
            for kw in ("whoami", "uname", "/etc/passwd", "/etc/shadow", "cat ", "curl ", "wget ", "id;")
        ):
            explicit_cmd = combined_probe

        shell_result: Optional[Dict[str, Any]] = None
        if explicit_cmd:
            shell_result = await self.shell_emulator.execute_command(
                session_id=session_id,
                container_id=binding.container_id,
                container_ip=binding.container_internal_ip,
                command_line=explicit_cmd,
            )

        # Check virtual filesystem access
        lfi_match = DecoyLinuxFilesystem.read_file(combined_probe)
        # Check SQLi access
        sqli_match = DecoySQLDatabaseEmulator.evaluate_sqli_probe(combined_probe)

        now_iso = datetime.now(timezone.utc).isoformat()
        response_headers = {
            "X-Deception-Upstream-Target": "PREWARMED_SANDBOX",
            "X-Sandbox-Container-ID": binding.container_id,
            "X-Sandbox-Internal-IP": binding.container_internal_ip,
            "X-Session-ID": session_id,
        }

        if shell_result is not None:
            response_payload: Dict[str, Any] = {
                "status": "interactive_shell_output",
                "container_node": binding.container_id,
                "internal_ip": binding.container_internal_ip,
                "executed_by": shell_result["executed_by_user"],
                "command": shell_result["command_line"],
                "exit_code": shell_result["exit_code"],
                "stdout": shell_result["stdout"],
                "timestamp": now_iso,
            }
        elif lfi_match is not None:
            file_path, file_content = lfi_match
            response_payload = {
                "status": "file_stream_ok",
                "container_node": binding.container_id,
                "file_path": file_path,
                "content": file_content,
                "timestamp": now_iso,
            }
        elif sqli_match is not None:
            response_payload = {
                "status": "query_executed",
                "container_node": binding.container_id,
                "sql_result": sqli_match,
                "timestamp": now_iso,
            }
        elif "vault-keys" in norm_path.lower():
            response_payload = {
                "status": "ok",
                "vault_cluster": "prd-hsm-vault.enterprise.internal",
                "keys": [
                    {
                        "key_id": "kv_prod_master_db_01",
                        "cipher": "AES-256-GCM",
                        "secret_handle": "hvs.CAESIJ9m8n7b6v5c4x3z2a1_decoy",
                    }
                ],
                "container_node": binding.container_id,
                "timestamp": now_iso,
            }
        else:
            response_payload = {
                "status": "ok",
                "service": "enterprise_staging_decoy_node",
                "container_node": binding.container_id,
                "internal_ip": binding.container_internal_ip,
                "endpoint": norm_path,
                "method": request_method.upper(),
                "filesystem_hint": "/admin/debug/env-dump",
                "timestamp": now_iso,
            }

        # Dispatch interaction context to registered forensic telemetry hooks
        interaction_event = {
            "session_id": session_id,
            "client_ip": client_ip,
            "container_id": binding.container_id,
            "container_ip": binding.container_internal_ip,
            "container_port": binding.container_port,
            "request_method": request_method.upper(),
            "request_path": norm_path,
            "headers": hdr_dict,
            "query_params": qry_dict,
            "body_text": body_text,
            "shell_result": shell_result,
            "lfi_file_accessed": lfi_match[0] if lfi_match else None,
            "sqli_triggered": sqli_match is not None,
            "timestamp": datetime.now(timezone.utc),
        }
        for hook in list(self._telemetry_hooks):
            try:
                await hook(interaction_event)
            except Exception as exc:
                logger.warning("Forensic telemetry hook error: %s", exc)

        return 200, response_payload, response_headers


decoy_service_instance = DecoyServiceApp()

app = FastAPI(
    title="Isolated Honey Container Decoy Service (Layer 3)",
    description="High-interaction decoy service running inside air-gapped honey containers.",
    version="1.0.0",
)


decoy_router = APIRouter(tags=["Isolated Honey Container Decoy Service"])


@decoy_router.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def decoy_catch_all_route(request: Request, full_path: str) -> Response:
    """ASGI route handling all requests forwarded to the isolated honey container."""
    headers = dict(getattr(request, "headers", {}) or {})
    query_params = dict(getattr(request, "query_params", {}) or {})
    session_id = (
        headers.get("X-Trapped-Session-ID")
        or headers.get("X-Session-ID")
        or "550e8400-e29b-41d4-a716-446655440000"
    )
    preferred_cid = headers.get("X-Assigned-Container-ID")
    client_ip = headers.get("X-Original-Attacker-IP", "127.0.0.1")

    body_bytes = b""
    if hasattr(request, "body") and callable(request.body):
        try:
            body_bytes = await request.body()
        except Exception:
            body_bytes = b""

    status_code, payload, resp_headers = (
        await decoy_service_instance.handle_trapped_request(
            session_id=session_id,
            client_ip=client_ip,
            request_method=getattr(request, "method", "GET"),
            request_path=f"/{full_path}",
            headers=headers,
            query_params=query_params,
            body_bytes=body_bytes,
            preferred_container_id=preferred_cid,
        )
    )
    return JSONResponse(
        content=payload,
        status_code=status_code,
        headers=resp_headers,
    )


app.include_router(decoy_router)
