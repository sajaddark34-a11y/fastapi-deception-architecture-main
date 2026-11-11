"""
Transparent Malicious Session Router and Built-In Decoy Fallback Responder
(`deception_gateway.malicious_session_router`).

Maintains `SandboxBindingContract` records in Redis and transparently proxies
trapped attacker requests to the Prewarmed Dynamic Sandbox (`SANDBOX_POOL_URL`)
over `httpx.AsyncClient`. Includes a high-interaction Built-In Decoy Fallback
Responder that emulates convincing vulnerable enterprise endpoints whenever
Phase 4 Docker sandbox containers are offline during testing.
"""

from __future__ import annotations

import hashlib
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional, Tuple

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore[assignment]

from data_storage.postgresql_store import (
    ForensicLogsRepository,
    forensic_logs_repository,
)
from data_storage.redis_store import (
    FastAlertsStream,
    SessionStateStore,
    fast_alerts_stream,
    session_state_store,
)
from shared_contracts.session_schema import (
    SandboxBindingContract,
    SessionStateContract,
)
from shared_contracts.telemetry_schema import (
    AttackerCommandEvent,
    TelemetrySourceEnum,
    TelemetryStreamEnvelope,
)

logger = logging.getLogger(__name__)


class MaliciousSessionRouter:
    """
    Diverts malicious/trapped sessions to isolated honey containers while maintaining
    persistent session-to-container bindings (`SandboxBindingContract`) and providing
    a realistic built-in decoy responder fallback.
    """

    def __init__(
        self,
        sandbox_pool_url: Optional[str] = None,
        state_store: Optional[SessionStateStore] = None,
        alerts_stream: Optional[FastAlertsStream] = None,
        logs_repo: Optional[ForensicLogsRepository] = None,
    ) -> None:
        """
        Initialize the malicious session router.
        """
        self.sandbox_pool_url: str = (
            sandbox_pool_url
            or os.getenv("SANDBOX_POOL_URL", "http://isolation_sandbox:8080")
        ).rstrip("/")
        self.state_store: SessionStateStore = state_store or session_state_store
        self.alerts_stream: FastAlertsStream = alerts_stream or fast_alerts_stream
        self.logs_repo: ForensicLogsRepository = logs_repo or forensic_logs_repository

    async def ensure_sandbox_binding(
        self, session: SessionStateContract
    ) -> SandboxBindingContract:
        """
        Retrieve an existing active `SandboxBindingContract` for `session.session_id`,
        or allocate and bind a deterministic isolated container from the prewarmed pool.
        """
        existing = await self.state_store.get_active_sandbox_binding(
            session.session_id
        )
        if existing is not None:
            return existing

        hash_bytes = hashlib.sha256(session.session_id.encode("utf-8")).digest()
        host_octet = (hash_bytes[0] % 200) + 10
        container_id = (
            session.assigned_container_id
            or f"honey_sbx_{hash_bytes.hex()[:12]}"
        )
        binding = SandboxBindingContract(
            binding_id=f"bind_{hash_bytes.hex()[:12]}",
            session_id=session.session_id,
            container_id=container_id,
            container_internal_ip=f"172.29.0.{host_octet}",
            container_port=8080,
            bound_at=datetime.now(timezone.utc),
            is_active=True,
        )
        return await self.state_store.bind_sandbox(binding)

    async def _record_sandbox_interaction_telemetry(
        self,
        session: SessionStateContract,
        binding: SandboxBindingContract,
        request_method: str,
        request_path: str,
        query_params: Optional[Mapping[str, str]],
        body_text: str,
    ) -> None:
        """
        Capture attacker interaction inside the decoy responder as a forensic
        `AttackerCommandEvent` and broadcast via `TelemetryStreamEnvelope`.
        """
        cmd_candidate = (
            (query_params or {}).get("cmd")
            or (query_params or {}).get("exec")
            or body_text.strip()
            or f"{request_method.upper()} {request_path}"
        )
        now_utc = datetime.now(timezone.utc)
        cmd_event = AttackerCommandEvent(
            event_id=f"cmd_evt_{uuid.uuid4().hex[:12]}",
            session_id=session.session_id,
            container_id=binding.container_id,
            timestamp=now_utc,
            command_line=cmd_candidate[:2048],
            working_directory="/var/www/enterprise-decoy",
            process_id=4100 + (session.request_count % 500),
            parent_process_id=4096,
            executed_by_user="www-data",
            exit_code=0,
        )
        envelope = TelemetryStreamEnvelope(
            envelope_id=f"env_{uuid.uuid4().hex[:12]}",
            source=TelemetrySourceEnum.COMMAND_LOGGER,
            session_id=session.session_id,
            container_id=binding.container_id,
            captured_at=now_utc,
            command_event=cmd_event,
            network_event=None,
        )
        await self.logs_repo.save_telemetry_envelope(envelope)
        await self.alerts_stream.publish_telemetry_envelope(envelope)

    def _build_decoy_fallback_payload(
        self,
        session: SessionStateContract,
        binding: SandboxBindingContract,
        request_path: str,
        request_method: str,
        query_params: Optional[Mapping[str, str]] = None,
        body_text: str = "",
    ) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        """
        Built-in Decoy Fallback Responder: generates convincing, high-interaction
        deceptive responses tailored to the endpoint probed by the attacker.
        """
        clean_path = (request_path or "/").split("?")[0].strip().lower()
        now_iso = datetime.now(timezone.utc).isoformat()
        response_headers = {
            "X-Server-Node": f"prd-node-{binding.container_id[-6:]}",
            "X-Enterprise-Server-Node": f"prd-api-gateway-{binding.container_id[-6:]}",
            "X-Deception-Upstream-Target": "PREWARMED_SANDBOX",
            "X-Sandbox-Container-ID": binding.container_id,
            "X-Session-ID": session.session_id,
        }

        if "vault-keys" in clean_path or "secrets" in clean_path:
            payload: Dict[str, Any] = {
                "status": "ok",
                "vault_cluster": "prd-hsm-vault-01.internal",
                "unseal_status": "UNSEALED",
                "keys": [
                    {
                        "key_id": "kv_prod_master_db_01",
                        "cipher": "AES-256-GCM",
                        "secret_handle": "hvs.CAESIJ9m8n7b6v5c4x3z2a1_decoy",
                        "rotated_at": now_iso,
                    },
                    {
                        "key_id": "kv_aws_s3_backup_role",
                        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
                        "region": "eu-central-1",
                    },
                ],
                "node_ip": binding.container_internal_ip,
            }
            return 200, payload, response_headers

        if "env-dump" in clean_path or ".env" in clean_path:
            payload = {
                "status": "debug_env_exposed",
                "environment": "staging_mirror",
                "variables": {
                    "APP_ENV": "production",
                    "DB_HOST": "10.240.12.88",
                    "DB_USER": "postgres_ro_replica",
                    "DB_PASS_HASH": "md5_9f8e7d6c5b4a3f2e1d0c",
                    "REDIS_CLUSTER_ENDPOINT": "10.240.12.90:6379",
                    "INTERNAL_DEBUG_MODE": "true",
                },
                "container_node": binding.container_id,
            }
            return 200, payload, response_headers

        if "db-snapshot" in clean_path or "backup" in clean_path:
            payload = {
                "status": "snapshot_ready",
                "snapshot_id": "snap_20261105_prod_full",
                "engine": "postgresql-16.2",
                "size_mb": 4820,
                "download_stream_uri": "/api/v1/backup/db-snapshot/stream?part=1",
                "checksum_sha256": hashlib.sha256(
                    session.session_id.encode("utf-8")
                ).hexdigest(),
            }
            return 200, payload, response_headers

        if "debug-console" in clean_path:
            executed_cmd = (
                (query_params or {}).get("cmd")
                or body_text.strip()
                or "id && uname -a"
            )
            payload = {
                "console_status": "interactive_debug_shell",
                "effective_user": "www-data (uid=33, gid=33)",
                "kernel": "Linux prd-app-node 6.1.0-21-amd64 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux",
                "last_command": executed_cmd[:256],
                "stdout": (
                    "uid=33(www-data) gid=33(www-data) groups=33(www-data)\n"
                    f"eth0: inet {binding.container_internal_ip}/24 brd 172.29.0.255 scope global"
                ),
                "timestamp": now_iso,
            }
            return 200, payload, response_headers

        # Default realistic decoy enterprise response keeping the attacker engaged
        payload = {
            "status": "success",
            "service": "core_enterprise_api_node",
            "request_method": request_method.upper(),
            "endpoint": request_path,
            "node_id": binding.container_id,
            "internal_ip": binding.container_internal_ip,
            "data": {
                "records_count": 3,
                "notice": "Authenticated staging session active. Elevated diagnostic endpoints enabled.",
                "diagnostic_ console": "/api/v1/internal/debug-console",
            },
            "timestamp": now_iso,
        }
        return 200, payload, response_headers

    async def route_to_sandbox(
        self,
        session: SessionStateContract,
        request_method: str,
        request_path: str,
        headers: Optional[Mapping[str, str]] = None,
        query_params: Optional[Mapping[str, str]] = None,
        body_bytes: bytes = b"",
    ) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        """
        Transparently forward a trapped attacker's HTTP request to the isolated
        sandbox container pool (`SANDBOX_POOL_URL`), or serve a convincing response
        from the Built-in Decoy Fallback Responder if the sandbox container is offline.

        Returns:
            Tuple of `(status_code, json_payload_dict, response_headers_dict)`.
        """
        binding = await self.ensure_sandbox_binding(session)
        body_text = body_bytes.decode("utf-8", errors="replace") if body_bytes else ""

        await self._record_sandbox_interaction_telemetry(
            session=session,
            binding=binding,
            request_method=request_method,
            request_path=request_path,
            query_params=query_params,
            body_text=body_text,
        )

        norm_path = request_path if request_path.startswith("/") else f"/{request_path}"
        target_url = f"{self.sandbox_pool_url}{norm_path}"

        if httpx is not None and os.getenv("DISABLE_EXTERNAL_SANDBOX_PROXY", "false").lower() != "true":
            proxy_headers = {
                str(k): str(v)
                for k, v in (headers or {}).items()
                if str(k).lower() not in {"host", "content-length"}
            }
            proxy_headers["X-Trapped-Session-ID"] = session.session_id
            proxy_headers["X-Assigned-Container-ID"] = binding.container_id
            proxy_headers["X-Original-Attacker-IP"] = session.client_ip

            try:
                async with httpx.AsyncClient(timeout=1.5) as client:
                    resp = await client.request(
                        method=request_method.upper(),
                        url=target_url,
                        params=dict(query_params or {}),
                        headers=proxy_headers,
                        content=body_bytes,
                    )
                    resp_headers = {
                        "X-Deception-Upstream-Target": "PREWARMED_SANDBOX",
                        "X-Sandbox-Container-ID": binding.container_id,
                        "X-Session-ID": session.session_id,
                    }
                    try:
                        data = resp.json()
                        if not isinstance(data, dict):
                            data = {"result": data}
                    except Exception:
                        data = {"raw_output": resp.text}
                    return resp.status_code, data, resp_headers
            except Exception as exc:
                logger.debug(
                    "Sandbox container pool at %s offline (%s); engaging Built-in Decoy Responder.",
                    target_url,
                    exc,
                )

        try:
            from forensic_extraction_engine.engine_service import (
                forensic_engine_service,
            )
            from isolation_sandbox.isolated_honey_containers.decoy_service_app import (
                decoy_service_instance,
            )

            forensic_engine_service.attach_sandbox_telemetry_hook()
            await decoy_service_instance.handle_trapped_request(
                session_id=session.session_id,
                client_ip=session.client_ip,
                request_method=request_method,
                request_path=norm_path,
                headers=headers,
                query_params=query_params,
                body_bytes=body_bytes,
                preferred_container_id=binding.container_id,
            )
        except Exception as exc:
            logger.debug("In-process decoy telemetry hook skipped: %s", exc)

        return self._build_decoy_fallback_payload(
            session=session,
            binding=binding,
            request_path=norm_path,
            request_method=request_method,
            query_params=query_params,
            body_text=body_text,
        )
