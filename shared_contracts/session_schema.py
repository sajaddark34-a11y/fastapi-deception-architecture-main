"""
Shared Session State and Sandbox Binding Contracts.

This module standardizes the session state contract across:
- Deception Gateway (`deception_gateway`)
- Redis State Store (`data_storage/redis_store`)
- Prewarmed Dynamic Sandbox (`isolation_sandbox/prewarmed_dynamic_sandbox`)
"""

from __future__ import annotations

import ipaddress
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SessionStatusEnum(str, Enum):
    """Enumeration of lifecycle states for a tracked client session."""

    LEGITIMATE = "LEGITIMATE"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS_TRAPPED = "MALICIOUS_TRAPPED"
    ISOLATED = "ISOLATED"
    TERMINATED = "TERMINATED"


class RoutingTargetEnum(str, Enum):
    """Enumeration of upstream routing destinations determined by the gateway."""

    CORE_WEB_APP = "CORE_WEB_APP"
    PREWARMED_SANDBOX = "PREWARMED_SANDBOX"
    BLOCKED = "BLOCKED"


class SessionStateContract(BaseModel):
    """
    Unified contract representing the real-time state and risk profile of a session.
    Stored in Redis and evaluated on every incoming HTTP request at the Deception Gateway.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=False,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "client_ip": "203.0.113.42",
                    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                    "status": "MALICIOUS_TRAPPED",
                    "routing_target": "PREWARMED_SANDBOX",
                    "risk_score": 92.5,
                    "triggered_token_id": "htk_9f8e7d6c5b4a",
                    "assigned_container_id": "honey_sbx_01a2b3c4d5e6",
                    "request_count": 14,
                    "first_seen_at": "2026-11-05T00:10:00Z",
                    "last_active_at": "2026-11-05T00:15:30Z",
                    "ttl_seconds": 3600,
                }
            ]
        },
    )

    session_id: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Unique session identifier (UUIDv4 string or standardized session token).",
    )
    client_ip: str = Field(
        ...,
        description="Client source IPv4 or IPv6 address.",
    )
    user_agent: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="HTTP User-Agent string presented by the client.",
    )
    status: SessionStatusEnum = Field(
        default=SessionStatusEnum.LEGITIMATE,
        description="Current security classification state of the session.",
    )
    routing_target: RoutingTargetEnum = Field(
        default=RoutingTargetEnum.CORE_WEB_APP,
        description="Target environment where session traffic is routed.",
    )
    risk_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Calculated threat risk score ranging from 0.0 (benign) to 100.0 (critical).",
    )
    triggered_token_id: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=128,
        description="Identifier of the honey token that exposed the attacker, if any.",
    )
    assigned_container_id: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=128,
        description="Identifier of the isolated honey container bound to this session, if any.",
    )
    request_count: int = Field(
        default=1,
        ge=1,
        description="Positive integer count of requests observed during this session.",
    )
    first_seen_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the session was first initiated.",
    )
    last_active_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the most recent request in this session.",
    )
    ttl_seconds: int = Field(
        default=3600,
        gt=0,
        le=604800,
        description="Time-to-live (TTL) in seconds for session persistence in Redis.",
    )

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str) -> str:
        """Validate that session_id is either a valid UUID or a non-empty standardized identifier."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("session_id cannot be empty.")
        try:
            UUID(cleaned)
            return cleaned
        except ValueError:
            if not all(c.isalnum() or c in ("-", "_") for c in cleaned):
                raise ValueError(
                    "session_id must be a valid UUID or contain only alphanumeric characters, hyphens, or underscores."
                )
            return cleaned

    @field_validator("client_ip")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        """Validate that client_ip conforms to strict IPv4 or IPv6 syntax."""
        try:
            ip_obj = ipaddress.ip_address(value.strip())
            return str(ip_obj)
        except ValueError as exc:
            raise ValueError(f"Invalid IPv4/IPv6 address format: '{value}'.") from exc

    @field_validator("first_seen_at", "last_active_at")
    @classmethod
    def ensure_utc_timestamp(cls, value: datetime) -> datetime:
        """Ensure timestamps are timezone-aware and normalized to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_chronological_order(self) -> "SessionStateContract":
        """Ensure last_active_at is not earlier than first_seen_at."""
        if self.last_active_at < self.first_seen_at:
            raise ValueError("last_active_at cannot be earlier than first_seen_at.")
        return self


class SandboxBindingContract(BaseModel):
    """
    Contract binding a malicious or trapped session to a specific isolated container
    in the prewarmed dynamic sandbox pool (`prewarmed_dynamic_sandbox`).
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "binding_id": "bind_77f8a9b0c1d2",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "container_id": "honey_sbx_01a2b3c4d5e6",
                    "container_internal_ip": "172.29.0.15",
                    "container_port": 8080,
                    "bound_at": "2026-11-05T00:12:05Z",
                    "is_active": True,
                }
            ]
        },
    )

    binding_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Unique identifier for the session-to-container binding record.",
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
        description="Docker container ID or name allocated from the prewarmed pool.",
    )
    container_internal_ip: str = Field(
        ...,
        description="Internal IPv4/IPv6 address of the isolated sandbox container on sandbox_containment_net.",
    )
    container_port: int = Field(
        ...,
        ge=1,
        le=65535,
        description="Internal TCP port exposed by the decoy service inside the container.",
    )
    bound_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the session was bound to the container.",
    )
    is_active: bool = Field(
        default=True,
        description="Indicates whether the sandbox binding is currently active.",
    )

    @field_validator("container_internal_ip")
    @classmethod
    def validate_container_ip(cls, value: str) -> str:
        """Validate that container_internal_ip is a valid IPv4 or IPv6 address."""
        try:
            ip_obj = ipaddress.ip_address(value.strip())
            return str(ip_obj)
        except ValueError as exc:
            raise ValueError(f"Invalid container internal IP address: '{value}'.") from exc

    @field_validator("bound_at")
    @classmethod
    def ensure_bound_at_utc(cls, value: datetime) -> datetime:
        """Normalize bound_at timestamp to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
