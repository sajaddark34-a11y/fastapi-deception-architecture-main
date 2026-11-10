"""
Shared Real-Time Security Alert Contracts.

This module standardizes instant security alert payloads streamed from:
- Attack Detector in the Deception Gateway (`deception_gateway/attack_detector.py`)
- Fast Alerts Stream in Redis (`data_storage/redis_store/fast_alerts_stream.py`)
- Defender SOC Dashboard (`soc_dashboard`)
"""

from __future__ import annotations

import ipaddress
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AlertSeverityEnum(str, Enum):
    """Enumeration of security alert severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AttackCategoryEnum(str, Enum):
    """Enumeration of detected threat and deception trigger categories."""

    HONEY_TOKEN_TRIGGERED = "HONEY_TOKEN_TRIGGERED"
    AUTOMATED_SCANNER_PROBE = "AUTOMATED_SCANNER_PROBE"
    UNAUTHORIZED_PATH_ACCESS = "UNAUTHORIZED_PATH_ACCESS"
    SANDBOX_COMMAND_EXECUTION = "SANDBOX_COMMAND_EXECUTION"
    BRUTE_FORCE_ATTEMPT = "BRUTE_FORCE_ATTEMPT"


class SecurityAlertContract(BaseModel):
    """
    Unified contract for real-time security alerts emitted upon detecting malicious activity
    or honey token activation, published over Redis streams to the SOC Dashboard.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=False,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "alert_id": "alt_3f4e5d6c7b8a9012",
                    "timestamp": "2026-11-05T00:12:01Z",
                    "severity": "CRITICAL",
                    "category": "HONEY_TOKEN_TRIGGERED",
                    "source_ip": "203.0.113.42",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "triggered_token_id": "htk_9f8e7d6c5b4a",
                    "target_endpoint": "/api/v1/internal/debug-console",
                    "http_method": "POST",
                    "action_taken": "REROUTED_TO_SANDBOX",
                    "summary_message": "Attacker presented decoy header X-Internal-Debug-Token; session transparently rerouted to isolated honey container.",
                    "raw_headers_snapshot": {
                        "Host": "api.enterprise-target.local",
                        "User-Agent": "python-requests/2.31.0",
                        "X-Internal-Debug-Token": "dbg_live_98a7b6c5d4e3f2a1",
                    },
                }
            ]
        },
    )

    alert_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Unique identifier for the generated security alert.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the alert was generated.",
    )
    severity: AlertSeverityEnum = Field(
        ...,
        description="Severity level of the security alert.",
    )
    category: AttackCategoryEnum = Field(
        ...,
        description="Threat classification category that triggered the alert.",
    )
    source_ip: str = Field(
        ...,
        description="Source IPv4 or IPv6 address of the attacker.",
    )
    session_id: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Tracked session identifier associated with the alert.",
    )
    triggered_token_id: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=128,
        description="Optional identifier of the honey token that triggered this alert.",
    )
    target_endpoint: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Target URI path or endpoint targeted by the attacker.",
    )
    http_method: str = Field(
        ...,
        min_length=3,
        max_length=16,
        description="HTTP request method used in the malicious request.",
    )
    action_taken: str = Field(
        ...,
        min_length=3,
        max_length=128,
        description="Automated defensive action executed (e.g., REROUTED_TO_SANDBOX, BLOCKED, FLAGGED).",
    )
    summary_message: str = Field(
        ...,
        min_length=5,
        max_length=2048,
        description="Human-readable summary describing the threat event for SOC analysts.",
    )
    raw_headers_snapshot: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary snapshot of string key-value HTTP headers captured from the request.",
    )

    @field_validator("source_ip")
    @classmethod
    def validate_source_ip(cls, value: str) -> str:
        """Validate that source_ip is a valid IPv4 or IPv6 address."""
        try:
            ip_obj = ipaddress.ip_address(value.strip())
            return str(ip_obj)
        except ValueError as exc:
            raise ValueError(f"Invalid source_ip address format: '{value}'.") from exc

    @field_validator("target_endpoint")
    @classmethod
    def validate_endpoint(cls, value: str) -> str:
        """Ensure target_endpoint starts with a leading '/'."""
        cleaned = value.strip()
        if not cleaned.startswith("/"):
            raise ValueError("target_endpoint must start with a leading '/'.")
        return cleaned

    @field_validator("http_method")
    @classmethod
    def validate_http_method(cls, value: str) -> str:
        """Normalize and validate the HTTP method."""
        allowed_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE", "CONNECT"}
        method_upper = value.strip().upper()
        if method_upper not in allowed_methods:
            raise ValueError(f"Invalid HTTP method '{value}'. Expected one of {sorted(allowed_methods)}.")
        return method_upper

    @field_validator("timestamp")
    @classmethod
    def ensure_timestamp_utc(cls, value: datetime) -> datetime:
        """Normalize alert timestamp to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @field_validator("raw_headers_snapshot")
    @classmethod
    def validate_headers_dict(cls, value: Dict[str, str]) -> Dict[str, str]:
        """Ensure all header keys and values are non-empty strings."""
        cleaned_headers: Dict[str, str] = {}
        for k, v in value.items():
            key_str = str(k).strip()
            val_str = str(v).strip()
            if not key_str:
                raise ValueError("HTTP header keys in raw_headers_snapshot cannot be empty.")
            cleaned_headers[key_str] = val_str
        return cleaned_headers
