"""
Shared Forensic Artifact Persistence and SOC Incident Reporting Contracts.

This module standardizes the contracts for storing verified forensic evidence in
PostgreSQL (`data_storage/postgresql_store/forensic_artifacts_repository.py`) and
generating comprehensive incident reports in the SOC Dashboard (`soc_dashboard/incident_reports`).
"""

from __future__ import annotations

import ipaddress
import re
from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_SHA256_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")


class ArtifactTypeEnum(str, Enum):
    """Enumeration of extracted forensic evidence artifact categories."""

    PCAP_CAPTURE_FILE = "PCAP_CAPTURE_FILE"
    EBPF_TRACE_LOG = "EBPF_TRACE_LOG"
    COMMAND_HISTORY_DUMP = "COMMAND_HISTORY_DUMP"
    DROPPED_MALWARE_SAMPLE = "DROPPED_MALWARE_SAMPLE"
    CONTAINER_FILESYSTEM_DIFF = "CONTAINER_FILESYSTEM_DIFF"


class ForensicArtifactContract(BaseModel):
    """
    Contract representing a single extracted forensic artifact with cryptographic
    SHA-256 chain-of-custody verification stored in PostgreSQL.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=False,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "artifact_id": "art_88d9e0f1a2b3",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "container_id": "honey_sbx_01a2b3c4d5e6",
                    "artifact_type": "PCAP_CAPTURE_FILE",
                    "file_name": "session_550e8400_capture.pcap",
                    "storage_uri": "file:///var/forensics/artifacts/550e8400/session_550e8400_capture.pcap",
                    "sha256_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "file_size_bytes": 245760,
                    "captured_at": "2026-11-05T00:18:00Z",
                    "is_verified": True,
                }
            ]
        },
    )

    artifact_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Unique identifier for the forensic artifact record.",
    )
    session_id: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Session identifier of the trapped attacker.",
    )
    container_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Identifier of the isolated honey container from which the artifact was extracted.",
    )
    artifact_type: ArtifactTypeEnum = Field(
        ...,
        description="Type classification of the forensic artifact.",
    )
    file_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Sanitized file name of the captured forensic artifact.",
    )
    storage_uri: str = Field(
        ...,
        min_length=5,
        max_length=2048,
        description="Persistent storage URI or path pointing to the raw evidence file.",
    )
    sha256_checksum: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="64-character hexadecimal SHA-256 hash ensuring forensic integrity.",
    )
    file_size_bytes: int = Field(
        ...,
        ge=0,
        description="Size of the forensic artifact file in bytes.",
    )
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the artifact was extracted and hashed.",
    )
    is_verified: bool = Field(
        default=True,
        description="Indicates whether the artifact's SHA-256 integrity check passed.",
    )

    @field_validator("sha256_checksum")
    @classmethod
    def validate_sha256_hex(cls, value: str) -> str:
        """Strictly validate that sha256_checksum is a 64-character hexadecimal string."""
        cleaned = value.strip().lower()
        if not _SHA256_REGEX.match(cleaned):
            raise ValueError(
                "sha256_checksum must be an exact 64-character hexadecimal string (0-9, a-f)."
            )
        return cleaned

    @field_validator("file_name")
    @classmethod
    def validate_safe_filename(cls, value: str) -> str:
        """Prevent path traversal characters in file_name."""
        cleaned = value.strip()
        if "/" in cleaned or "\\" in cleaned or ".." in cleaned:
            raise ValueError("file_name must not contain path separators or traversal sequences.")
        return cleaned

    @field_validator("captured_at")
    @classmethod
    def ensure_captured_at_utc(cls, value: datetime) -> datetime:
        """Normalize captured_at timestamp to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class IncidentReportContract(BaseModel):
    """
    Comprehensive SOC Incident Report contract aggregating session timeline,
    telemetry counts, triggered honey tokens, alerts, and verified forensic artifacts.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "report_id": "inc_rep_20261105_001",
                    "generated_at": "2026-11-05T00:20:00Z",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "attacker_ip": "203.0.113.42",
                    "attack_start_time": "2026-11-05T00:10:00Z",
                    "attack_end_time": "2026-11-05T00:18:30Z",
                    "total_commands_captured": 12,
                    "total_packets_captured": 485,
                    "triggered_tokens_list": ["htk_9f8e7d6c5b4a"],
                    "alerts_timeline": ["alt_3f4e5d6c7b8a9012"],
                    "artifacts_list": [
                        {
                            "artifact_id": "art_88d9e0f1a2b3",
                            "session_id": "550e8400-e29b-41d4-a716-446655440000",
                            "container_id": "honey_sbx_01a2b3c4d5e6",
                            "artifact_type": "PCAP_CAPTURE_FILE",
                            "file_name": "session_550e8400_capture.pcap",
                            "storage_uri": "file:///var/forensics/artifacts/550e8400/session_550e8400_capture.pcap",
                            "sha256_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                            "file_size_bytes": 245760,
                            "captured_at": "2026-11-05T00:18:00Z",
                            "is_verified": True,
                        }
                    ],
                    "executive_summary": "Attacker from 203.0.113.42 triggered decoy header token htk_9f8e7d6c5b4a and was isolated inside honey container honey_sbx_01a2b3c4d5e6, where 12 shell commands and 485 network packets were forensically captured.",
                }
            ]
        },
    )

    report_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Unique identifier for the generated SOC incident report.",
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the incident report was compiled.",
    )
    session_id: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Session identifier of the investigated incident.",
    )
    attacker_ip: str = Field(
        ...,
        description="Source IPv4 or IPv6 address of the attacker.",
    )
    attack_start_time: datetime = Field(
        ...,
        description="UTC timestamp marking the start of the malicious session.",
    )
    attack_end_time: datetime = Field(
        ...,
        description="UTC timestamp marking the containment termination or end of the attack.",
    )
    total_commands_captured: int = Field(
        default=0,
        ge=0,
        description="Total count of attacker shell commands captured in the sandbox.",
    )
    total_packets_captured: int = Field(
        default=0,
        ge=0,
        description="Total count of network packets captured during sandbox containment.",
    )
    triggered_tokens_list: List[str] = Field(
        default_factory=list,
        description="List of honey token IDs triggered during the session.",
    )
    alerts_timeline: List[str] = Field(
        default_factory=list,
        description="Chronological list of security alert IDs associated with the incident.",
    )
    artifacts_list: List[ForensicArtifactContract] = Field(
        default_factory=list,
        description="List of verified forensic artifacts collected during the incident.",
    )
    executive_summary: str = Field(
        ...,
        min_length=10,
        max_length=8192,
        description="Executive summary of the attack lifecycle, containment, and extracted evidence.",
    )

    @field_validator("attacker_ip")
    @classmethod
    def validate_attacker_ip(cls, value: str) -> str:
        """Validate that attacker_ip is a valid IPv4 or IPv6 address."""
        try:
            ip_obj = ipaddress.ip_address(value.strip())
            return str(ip_obj)
        except ValueError as exc:
            raise ValueError(f"Invalid attacker IPv4/IPv6 address: '{value}'.") from exc

    @field_validator("generated_at", "attack_start_time", "attack_end_time")
    @classmethod
    def ensure_report_timestamps_utc(cls, value: datetime) -> datetime:
        """Normalize report timestamps to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_attack_window(self) -> "IncidentReportContract":
        """Ensure attack_end_time is not earlier than attack_start_time."""
        if self.attack_end_time < self.attack_start_time:
            raise ValueError("attack_end_time cannot be earlier than attack_start_time.")
        return self
