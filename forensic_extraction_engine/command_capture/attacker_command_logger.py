"""
Attacker Command Logger, Deobfuscator, IOC Extractor, and MITRE ATT&CK Mapper
(`forensic_extraction_engine.command_capture.attacker_command_logger`).

Captures shell commands executed inside isolated honey containers, automatically
deobfuscates encoded payloads (Base64, URL-encoding, Hex), calculates cryptographic
digests (SHA-256, MD5) and Shannon entropy, extracts Indicators of Compromise (IOCs),
maps behaviors to MITRE ATT&CK Tactics & Techniques, and persists
`AttackerCommandEvent` records to PostgreSQL and Redis Streams.
"""

from __future__ import annotations

import base64
import hashlib
import math
import re
import urllib.parse
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from data_storage.postgresql_store import (
    ForensicLogsRepository,
    forensic_logs_repository,
)
from data_storage.redis_store import FastAlertsStream, fast_alerts_stream
from shared_contracts.telemetry_schema import (
    AttackerCommandEvent,
    TelemetrySourceEnum,
    TelemetryStreamEnvelope,
)

_BASE64_TOKEN_REGEX = re.compile(
    r"(?:echo\s+['\"]?([A-Za-z0-9+/]{12,}={0,2})['\"]?\s*\|\s*base64\s+-d|base64\s+-d\s*<<<\s*['\"]?([A-Za-z0-9+/]{12,}={0,2})['\"]?)",
    re.IGNORECASE,
)
_HEX_ESCAPE_REGEX = re.compile(r"(?:\\x[0-9a-fA-F]{2}){4,}")
_IPV4_IOC_REGEX = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_URL_IOC_REGEX = re.compile(r"https?://[^\s\"'|;&<>]+", re.IGNORECASE)
_DOMAIN_IOC_REGEX = re.compile(
    r"\b(?:[a-zA-Z0-9-]+\.)+(?:com|net|org|io|ru|cn|xyz|top|onion|internal|local)\b",
    re.IGNORECASE,
)


@dataclass
class MITRETechniqueMapping:
    """Represents a matched MITRE ATT&CK Tactic and Technique."""

    technique_id: str
    technique_name: str
    tactic: str
    matched_indicator: str


@dataclass
class PayloadAnalysisReport:
    """
    Deep forensic analysis report for a captured command or exploit payload,
    including deobfuscated text, SHA-256/MD5 hashes, Shannon entropy, IOCs,
    and MITRE ATT&CK mappings.
    """

    raw_payload: str
    deobfuscated_payload: str
    was_obfuscated: bool
    encoding_layers_detected: List[str]
    sha256_hash: str
    md5_hash: str
    shannon_entropy: float
    extracted_iocs: Dict[str, List[str]] = field(default_factory=dict)
    mitre_techniques: List[MITRETechniqueMapping] = field(default_factory=list)


# MITRE ATT&CK Signature Rules: (Regex Pattern, Technique ID, Name, Tactic)
_MITRE_RULES = [
    (
        re.compile(r"(/etc/shadow|/etc/passwd|\.env|vault-keys|id_rsa|credentials)", re.I),
        "T1003",
        "OS Credential Dumping & Secret Harvesting",
        "Credential Access",
    ),
    (
        re.compile(r"\b(sh|bash|zsh|python|perl|php|nc|netcat|socat)\b|\|\s*sh", re.I),
        "T1059",
        "Command and Scripting Interpreter",
        "Execution",
    ),
    (
        re.compile(r"\b(curl|wget|scp|tftp|ftp)\b", re.I),
        "T1105",
        "Ingress Tool Transfer",
        "Command and Control",
    ),
    (
        re.compile(r"\b(ls|dir|find|locate|pwd|tree)\b", re.I),
        "T1083",
        "File and Directory Discovery",
        "Discovery",
    ),
    (
        re.compile(r"\b(uname|whoami|id|hostname|lscpu|env|printenv)\b", re.I),
        "T1082",
        "System Information Discovery",
        "Discovery",
    ),
    (
        re.compile(r"\b(netstat|ss|ifconfig|ip\s+a|arp|route)\b", re.I),
        "T1049",
        "System Network Connections Discovery",
        "Discovery",
    ),
    (
        re.compile(r"\b(sudo|su\b|chmod\s+\+s|chown\s+root|pkexec)", re.I),
        "T1548",
        "Abuse Elevation Control Mechanism",
        "Privilege Escalation",
    ),
    (
        re.compile(r"(union\s+select|'\s*or\s+'?1'?\s*=\s*'?1|\.\./|<script)", re.I),
        "T1190",
        "Exploit Public-Facing Application",
        "Initial Access",
    ),
]


class AttackerCommandLogger:
    """
    Captures, deobfuscates, analyzes, and persists attacker shell commands executed
    inside isolated honey containers.
    """

    def __init__(
        self,
        logs_repo: Optional[ForensicLogsRepository] = None,
        alerts_stream: Optional[FastAlertsStream] = None,
    ) -> None:
        self.logs_repo: ForensicLogsRepository = logs_repo or forensic_logs_repository
        self.alerts_stream: FastAlertsStream = alerts_stream or fast_alerts_stream
        self._analysis_by_event_id: Dict[str, PayloadAnalysisReport] = {}
        self._session_mitre_map: Dict[str, List[MITRETechniqueMapping]] = {}

    @staticmethod
    def compute_shannon_entropy(data: str) -> float:
        """Compute the Shannon entropy (bits per character, 0.0 to 8.0) of `data`."""
        if not data:
            return 0.0
        length = len(data)
        counts = Counter(data)
        entropy = -sum(
            (count / length) * math.log2(count / length)
            for count in counts.values()
        )
        return round(entropy, 4)

    @classmethod
    def deobfuscate_payload(cls, raw_payload: str) -> PayloadAnalysisReport:
        """
        Automatically decode URL-encoded, Base64-piped, and Hex-escaped command
        payloads, extract IOCs, compute SHA-256/MD5 & entropy, and map to MITRE ATT&CK.
        """
        current = raw_payload or ""
        layers: List[str] = []

        # 1. URL Decoding
        if "%" in current:
            unquoted = urllib.parse.unquote(current)
            if unquoted != current:
                current = unquoted
                layers.append("URL_ENCODED")

        # 2. Base64 Decoding (`echo <b64> | base64 -d`)
        b64_match = _BASE64_TOKEN_REGEX.search(current)
        if b64_match:
            b64_token = b64_match.group(1) or b64_match.group(2)
            if b64_token:
                try:
                    decoded_bytes = base64.b64decode(b64_token)
                    decoded_str = decoded_bytes.decode("utf-8", errors="replace")
                    current = f"{current} [DECODED_BASE64: {decoded_str}]"
                    layers.append("BASE64")
                except Exception:
                    pass

        # 3. Hex Escape Decoding (`\x63\x61\x74`)
        hex_match = _HEX_ESCAPE_REGEX.search(current)
        if hex_match:
            hex_seq = hex_match.group(0).replace("\\x", "")
            try:
                decoded_hex = bytes.fromhex(hex_seq).decode("utf-8", errors="replace")
                current = f"{current} [DECODED_HEX: {decoded_hex}]"
                layers.append("HEX_ESCAPED")
            except Exception:
                pass

        raw_bytes = raw_payload.encode("utf-8", errors="replace")
        sha256_hex = hashlib.sha256(raw_bytes).hexdigest()
        md5_hex = hashlib.md5(raw_bytes).hexdigest()  # noqa: S324
        entropy = cls.compute_shannon_entropy(raw_payload)

        # Extract IOCs
        urls = sorted(set(_URL_IOC_REGEX.findall(current)))
        ips = sorted(set(_IPV4_IOC_REGEX.findall(current)))
        domains = sorted(set(_DOMAIN_IOC_REGEX.findall(current)))
        iocs = {
            "urls": urls,
            "ip_addresses": ips,
            "domains": domains,
        }

        # Map to MITRE ATT&CK
        mitre_matches: List[MITRETechniqueMapping] = []
        seen_tech_ids = set()
        for pattern, tech_id, tech_name, tactic in _MITRE_RULES:
            m = pattern.search(current)
            if m and tech_id not in seen_tech_ids:
                seen_tech_ids.add(tech_id)
                mitre_matches.append(
                    MITRETechniqueMapping(
                        technique_id=tech_id,
                        technique_name=tech_name,
                        tactic=tactic,
                        matched_indicator=m.group(0)[:64],
                    )
                )

        if not mitre_matches:
            mitre_matches.append(
                MITRETechniqueMapping(
                    technique_id="T1059",
                    technique_name="Command and Scripting Interpreter",
                    tactic="Execution",
                    matched_indicator=current[:48],
                )
            )

        return PayloadAnalysisReport(
            raw_payload=raw_payload,
            deobfuscated_payload=current,
            was_obfuscated=len(layers) > 0,
            encoding_layers_detected=layers,
            sha256_hash=sha256_hex,
            md5_hash=md5_hex,
            shannon_entropy=entropy,
            extracted_iocs=iocs,
            mitre_techniques=mitre_matches,
        )

    async def log_attacker_command(
        self,
        session_id: str,
        container_id: str,
        command_line: str,
        working_directory: str = "/var/www/enterprise-decoy",
        process_id: int = 4128,
        parent_process_id: int = 4096,
        executed_by_user: str = "www-data",
        exit_code: int = 0,
    ) -> Tuple[AttackerCommandEvent, PayloadAnalysisReport]:
        """
        Analyze an attacker command, create a validated `AttackerCommandEvent`,
        stream it via `TelemetryStreamEnvelope` to Redis, and persist it in PostgreSQL.
        """
        analysis = self.deobfuscate_payload(command_line)
        now_utc = datetime.now(timezone.utc)
        work_dir = (
            working_directory
            if working_directory.startswith("/")
            else f"/{working_directory}"
        )

        event = AttackerCommandEvent(
            event_id=f"cmd_evt_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            container_id=container_id,
            timestamp=now_utc,
            command_line=analysis.deobfuscated_payload[:8192],
            working_directory=work_dir,
            process_id=max(1, int(process_id)),
            parent_process_id=max(0, int(parent_process_id)),
            executed_by_user=executed_by_user or "www-data",
            exit_code=max(-255, min(255, int(exit_code))),
        )

        self._analysis_by_event_id[event.event_id] = analysis
        session_techs = self._session_mitre_map.setdefault(session_id, [])
        existing_ids = {t.technique_id for t in session_techs}
        for tech in analysis.mitre_techniques:
            if tech.technique_id not in existing_ids:
                session_techs.append(tech)
                existing_ids.add(tech.technique_id)

        envelope = TelemetryStreamEnvelope(
            envelope_id=f"env_{uuid.uuid4().hex[:12]}",
            source=TelemetrySourceEnum.COMMAND_LOGGER,
            session_id=session_id,
            container_id=container_id,
            captured_at=now_utc,
            command_event=event,
            network_event=None,
        )
        await self.logs_repo.save_command_event(event)
        await self.alerts_stream.publish_telemetry_envelope(envelope)
        return event, analysis

    def get_session_mitre_Mappings(
        self, session_id: str
    ) -> List[Dict[str, str]]:
        """Return all MITRE ATT&CK techniques observed for `session_id`."""
        mappings = self._session_mitre_map.get(session_id, [])
        return [
            {
                "technique_id": m.technique_id,
                "technique_name": m.technique_name,
                "tactic": m.tactic,
                "matched_indicator": m.matched_indicator,
            }
            for m in mappings
        ]

    def get_event_analysis(
        self, event_id: str
    ) -> Optional[PayloadAnalysisReport]:
        """Retrieve the `PayloadAnalysisReport` for a specific `event_id`."""
        return self._analysis_by_event_id.get(event_id)
