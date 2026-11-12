"""
Real-Time Deception and Threat Attack Detector (`deception_gateway.attack_detector`).

Combines deterministic Honey Token validation (`HoneyTokenValidator`) with deep
inspection for automated vulnerability scanners (Nikto, sqlmap, Nuclei, Nmap),
SQL Injection, Cross-Site Scripting (XSS), Path Traversal, Command Injection,
and unauthorized sensitive path probing (`/.env`, `/.git`). Automatically emits
`SecurityAlertContract` events to Redis (`FastAlertsStream`) and PostgreSQL
(`ForensicLogsRepository`).
"""

from __future__ import annotations

import hashlib
import re
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Mapping, Optional, Tuple

from data_storage.postgresql_store import (
    ForensicLogsRepository,
    forensic_logs_repository,
)
from data_storage.redis_store import (
    FastAlertsStream,
    fast_alerts_stream,
    session_state_store,
)
from honey_token_injector import (
    HoneyTokenValidator,
    honey_token_validator,
)
from shared_contracts.alert_schema import (
    AlertSeverityEnum,
    AttackCategoryEnum,
    SecurityAlertContract,
)
from shared_contracts.honey_token_schema import HoneyTokenValidationContract

_SCANNER_UA_REGEX = re.compile(
    r"(sqlmap|nikto|nuclei|nmap|masscan|dirbuster|gobuster|wfuzz|acunetix|nessus|zgrab|burpsuite|hydra|metasploit)",
    re.IGNORECASE,
)

_NMAP_SERVICE_PROBE_REGEX = re.compile(
    r"(/nice%20ports|tri%6eity\.txt|trinity\.txt|/nmaplowercheck|/evox/about|/hnap1|/sdk\b|/gponform|rtsp/1\.0|sip/2\.0)",
    re.IGNORECASE,
)

_SENSITIVE_PATH_REGEX = re.compile(
    r"(^/\.env|^/\.git|^/\.aws|^/wp-admin|^/wp-login\.php|^/phpmyadmin|^/actuator|^/etc/passwd|^/etc/shadow|^/proc/self|\.\./|\.\.\\)",
    re.IGNORECASE,
)

_COMMAND_INJECTION_REGEX = re.compile(
    r"(;\s*(cat|ls|id|whoami|uname|curl|wget|bash|sh|nc)\b|\|\s*(sh|bash|zsh)\b|\$\([^)]+\)|`[^`]+`)",
    re.IGNORECASE,
)

_SQLI_XSS_REGEX = re.compile(
    r"(union\s+all\s+select|union\s+select|'\s*or\s+'?1'?\s*=\s*'?1|information_schema|<script\b|javascript:|onerror\s*=|onload\s*=)",
    re.IGNORECASE,
)


@dataclass
class AttackDetectionOutcome:
    """Structured result produced by `AttackDetector.inspect_request`."""

    is_malicious: bool
    risk_score: float
    alert: Optional[SecurityAlertContract] = None
    token_validation: Optional[HoneyTokenValidationContract] = None
    reason: str = "Benign request"


class AttackDetector:
    """
    Multi-vector threat detection engine evaluating incoming HTTP requests against
    active honey tokens and adversarial exploit signatures.
    """

    def __init__(
        self,
        validator: Optional[HoneyTokenValidator] = None,
        alerts_stream: Optional[FastAlertsStream] = None,
        logs_repo: Optional[ForensicLogsRepository] = None,
    ) -> None:
        """
        Initialize the attack detector with honey token validator and storage sinks.
        """
        self.validator: HoneyTokenValidator = validator or honey_token_validator
        self.alerts_stream: FastAlertsStream = alerts_stream or fast_alerts_stream
        self.logs_repo: ForensicLogsRepository = logs_repo or forensic_logs_repository
        self._l4_scan_dedup: Dict[Tuple[str, int, str], float] = {}

    async def _emit_security_alert(
        self,
        severity: AlertSeverityEnum,
        category: AttackCategoryEnum,
        source_ip: str,
        session_id: str,
        target_endpoint: str,
        http_method: str,
        summary_message: str,
        headers_snapshot: Dict[str, str],
        triggered_token_id: Optional[str] = None,
        action_taken: str = "REROUTED_TO_SANDBOX",
    ) -> SecurityAlertContract:
        """
        Construct a `SecurityAlertContract` and persist it to both Redis Streams/PubSub
        and PostgreSQL forensic logs.
        """
        clean_headers = {
            str(k).strip(): str(v).strip()
            for k, v in (headers_snapshot or {}).items()
            if str(k).strip()
        }
        alert = SecurityAlertContract(
            alert_id=f"alt_{uuid.uuid4().hex[:16]}",
            timestamp=datetime.now(timezone.utc),
            severity=severity,
            category=category,
            source_ip=source_ip,
            session_id=session_id,
            triggered_token_id=triggered_token_id,
            target_endpoint=(
                target_endpoint if target_endpoint.startswith("/") else f"/{target_endpoint}"
            ),
            http_method=http_method.upper(),
            action_taken=action_taken,
            summary_message=summary_message,
            raw_headers_snapshot=clean_headers,
        )
        await self.alerts_stream.publish_alert(alert)
        await self.logs_repo.save_security_alert(alert)
        return alert

    async def inspect_request(
        self,
        session_id: str,
        client_ip: str,
        request_path: str,
        request_method: str = "GET",
        headers: Optional[Mapping[str, str]] = None,
        query_params: Optional[Mapping[str, str]] = None,
        cookies: Optional[Mapping[str, str]] = None,
        body_text: str = "",
    ) -> AttackDetectionOutcome:
        """
        Perform comprehensive inspection on an incoming HTTP request:
        1. Check for Honey Token triggers (100% confidence CRITICAL alert).
        2. Check for Automated Scanner User-Agents (`AUTOMATED_SCANNER_PROBE`).
        3. Check for Sensitive Path Probing / Directory Traversal (`UNAUTHORIZED_PATH_ACCESS`).
        4. Check for Command Injection / SQLi / XSS payloads.

        Returns:
            `AttackDetectionOutcome` detailing detection status, risk score, and emitted alert.
        """
        safe_ip = (client_ip or "127.0.0.1").strip()
        if safe_ip == "testclient":
            safe_ip = "127.0.0.1"
        norm_path = (request_path or "/").split("?")[0].strip()
        if not norm_path.startswith("/"):
            norm_path = f"/{norm_path}"
        norm_method = (request_method or "GET").strip().upper()
        hdr_dict = {str(k).strip(): str(v).strip() for k, v in (headers or {}).items()}
        qry_dict = {
            str(k).strip(): str(v).strip() for k, v in (query_params or {}).items()
        }
        ck_dict = {str(k).strip(): str(v).strip() for k, v in (cookies or {}).items()}

        # 1. Honey Token Inspection (Highest Priority - Zero False Positives)
        token_result = self.validator.validate_request(
            session_id=session_id,
            client_ip=safe_ip,
            request_path=norm_path,
            request_method=norm_method,
            headers=hdr_dict,
            query_params=qry_dict,
            cookies=ck_dict,
        )
        if token_result.is_triggered:
            summary = (
                f"Attacker at {safe_ip} triggered deception honey token "
                f"'{token_result.token_id}' (matched: '{token_result.matched_value[:80]}') "
                f"on {norm_method} {norm_path}; session transparently diverted to sandbox."
            )
            alert = await self._emit_security_alert(
                severity=AlertSeverityEnum.CRITICAL,
                category=AttackCategoryEnum.HONEY_TOKEN_TRIGGERED,
                source_ip=safe_ip,
                session_id=session_id,
                target_endpoint=norm_path,
                http_method=norm_method,
                summary_message=summary,
                headers_snapshot=hdr_dict,
                triggered_token_id=token_result.token_id,
            )
            return AttackDetectionOutcome(
                is_malicious=True,
                risk_score=100.0,
                alert=alert,
                token_validation=token_result,
                reason=summary,
            )

        # Combine request surfaces for signature analysis
        user_agent = hdr_dict.get("User-Agent") or hdr_dict.get("user-agent") or ""
        query_blob = "&".join(f"{k}={v}" for k, v in qry_dict.items())
        combined_payload = f"{norm_path} {query_blob} {body_text}"

        # 2. Automated Scanner Fingerprinting (User-Agent + Nmap Service Probes)
        scanner_match = _SCANNER_UA_REGEX.search(user_agent)
        nmap_probe_match = _NMAP_SERVICE_PROBE_REGEX.search(combined_payload)
        if scanner_match or nmap_probe_match:
            scanner_name = (
                scanner_match.group(1)
                if scanner_match
                else f"nmap-service-probe ({nmap_probe_match.group(0)})"
            )
            summary = (
                f"Automated vulnerability scanner '{scanner_name}' detected from {safe_ip} "
                f"probing {norm_method} {norm_path}; session isolated in honey sandbox."
            )
            alert = await self._emit_security_alert(
                severity=AlertSeverityEnum.HIGH,
                category=AttackCategoryEnum.AUTOMATED_SCANNER_PROBE,
                source_ip=safe_ip,
                session_id=session_id,
                target_endpoint=norm_path,
                http_method=norm_method,
                summary_message=summary,
                headers_snapshot=hdr_dict,
            )
            return AttackDetectionOutcome(
                is_malicious=True,
                risk_score=100.0,
                alert=alert,
                token_validation=token_result,
                reason=summary,
            )

        # 3. Command Injection Signatures
        cmd_match = _COMMAND_INJECTION_REGEX.search(combined_payload)
        if cmd_match:
            snippet = cmd_match.group(0)[:64]
            summary = (
                f"Remote command execution payload ('{snippet}') detected from {safe_ip} "
                f"on {norm_method} {norm_path}; session routed to containment sandbox."
            )
            alert = await self._emit_security_alert(
                severity=AlertSeverityEnum.CRITICAL,
                category=AttackCategoryEnum.SANDBOX_COMMAND_EXECUTION,
                source_ip=safe_ip,
                session_id=session_id,
                target_endpoint=norm_path,
                http_method=norm_method,
                summary_message=summary,
                headers_snapshot=hdr_dict,
            )
            return AttackDetectionOutcome(
                is_malicious=True,
                risk_score=100.0,
                alert=alert,
                token_validation=token_result,
                reason=summary,
            )

        # 4. Sensitive Path Probing / Path Traversal
        path_match = _SENSITIVE_PATH_REGEX.search(combined_payload)
        if path_match:
            matched_probe = path_match.group(0)
            summary = (
                f"Unauthorized sensitive path or traversal probe ('{matched_probe}') "
                f"from {safe_ip} targeting {norm_path}; session diverted to sandbox."
            )
            alert = await self._emit_security_alert(
                severity=AlertSeverityEnum.HIGH,
                category=AttackCategoryEnum.UNAUTHORIZED_PATH_ACCESS,
                source_ip=safe_ip,
                session_id=session_id,
                target_endpoint=norm_path,
                http_method=norm_method,
                summary_message=summary,
                headers_snapshot=hdr_dict,
            )
            return AttackDetectionOutcome(
                is_malicious=True,
                risk_score=100.0,
                alert=alert,
                token_validation=token_result,
                reason=summary,
            )

        # 5. SQL Injection / XSS Signatures
        sqli_match = _SQLI_XSS_REGEX.search(combined_payload)
        if sqli_match:
            matched_sig = sqli_match.group(0)[:64]
            summary = (
                f"Injection exploit payload ('{matched_sig}') detected from {safe_ip} "
                f"on {norm_method} {norm_path}; session trapped in sandbox."
            )
            alert = await self._emit_security_alert(
                severity=AlertSeverityEnum.HIGH,
                category=AttackCategoryEnum.UNAUTHORIZED_PATH_ACCESS,
                source_ip=safe_ip,
                session_id=session_id,
                target_endpoint=norm_path,
                http_method=norm_method,
                summary_message=summary,
                headers_snapshot=hdr_dict,
            )
            return AttackDetectionOutcome(
                is_malicious=True,
                risk_score=100.0,
                alert=alert,
                token_validation=token_result,
                reason=summary,
            )

        return AttackDetectionOutcome(
            is_malicious=False,
            risk_score=0.0,
            alert=None,
            token_validation=token_result,
            reason="Legitimate traffic verified",
        )

    async def inspect_tcp_l4_scan(
        self,
        client_ip: str,
        client_port: int,
        destination_port: int,
        raw_probe_bytes: bytes = b"",
        scan_type: str = "TCP_L4_PORT_SCAN",
    ) -> Optional[SecurityAlertContract]:
        """
        Intercept, log, and forward raw Layer-4 TCP port scan / service enumeration
        probes (e.g. `nmap -sS`, `nmap -sT`, `nmap -sV`) to `ForensicExtractionEngine`
        and broadcast a real-time `SecurityAlertContract` to the SOC Dashboard.
        """
        safe_ip = (client_ip or "127.0.0.1").strip()
        now_mono = time.monotonic()
        dedup_key = (safe_ip, int(destination_port), scan_type)
        last_seen = self._l4_scan_dedup.get(dedup_key, 0.0)
        if now_mono - last_seen < 1.5:
            return None
        self._l4_scan_dedup[dedup_key] = now_mono

        existing_sess = await session_state_store.get_session_by_ip(safe_ip)
        session_id = (
            existing_sess.session_id
            if existing_sess is not None
            else f"l4_scan_{hashlib.sha256(f'{safe_ip}:{destination_port}'.encode()).hexdigest()[:16]}"
        )
        container_id = f"honey_sbx_{hashlib.sha256(session_id.encode()).hexdigest()[:12]}"

        await session_state_store.escalate_session_to_malicious(
            session_id=session_id,
            triggered_token_id=None,
            assigned_container_id=container_id,
            risk_score=100.0,
        )

        probe_preview = (
            raw_probe_bytes[:96].decode("utf-8", errors="replace").strip()
            if raw_probe_bytes
            else "SYN/ACK -> RST/FIN (0-byte L4 port probe)"
        )
        summary = (
            f"Raw Layer-4 TCP Scan ({scan_type}) intercepted from {safe_ip}:{client_port} "
            f"targeting port {destination_port} [probe: {probe_preview[:64]}]; "
            f"forwarded to Forensic Extraction Engine."
        )
        alert = await self._emit_security_alert(
            severity=AlertSeverityEnum.HIGH,
            category=AttackCategoryEnum.AUTOMATED_SCANNER_PROBE,
            source_ip=safe_ip,
            session_id=session_id,
            target_endpoint=f"/tcp-l4/port-{destination_port}",
            http_method="TCP_SYN",
            summary_message=summary,
            headers_snapshot={
                "X-Layer4-Scan-Type": scan_type,
                "X-Source-Port": str(client_port),
                "X-Destination-Port": str(destination_port),
                "X-Raw-Probe-Bytes": str(len(raw_probe_bytes)),
            },
            action_taken="L4_SCAN_LOGGED_AND_PINNED_TO_SANDBOX",
        )

        try:
            from forensic_extraction_engine.engine_service import (
                forensic_engine_service,
            )

            await forensic_engine_service.process_sandbox_interaction(
                {
                    "session_id": session_id,
                    "client_ip": safe_ip,
                    "container_id": container_id,
                    "container_ip": "172.29.0.15",
                    "container_port": int(destination_port),
                    "request_method": "TCP_SYN",
                    "request_path": f"/tcp-l4/port-{destination_port}",
                    "headers": {
                        "X-Layer4-Scan-Type": scan_type,
                        "X-Source-Port": str(client_port),
                        "X-Destination-Port": str(destination_port),
                    },
                    "body_text": f"nmap tcp_l4_scan {scan_type} port {destination_port} ({probe_preview[:80]})",
                    "shell_result": {
                        "command_line": f"nmap tcp_l4_scan {scan_type} port {destination_port} ({probe_preview[:80]})",
                        "working_directory": "/network/l4-perimeter",
                        "executed_by_user": "remote-scanner",
                        "exit_code": 0,
                    },
                }
            )
        except Exception:
            pass

        return alert
