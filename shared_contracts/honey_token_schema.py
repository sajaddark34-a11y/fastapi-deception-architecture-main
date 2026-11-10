"""
Shared Honey Token Generation, Injection, and Validation Contracts.

This module standardizes honey token data models across:
- Honey Token Injector (`honey_token_injector`)
- Core Web Application (`core_web_app`)
- Deception Gateway (`deception_gateway`)
"""

from __future__ import annotations

import ipaddress
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class HoneyTokenTypeEnum(str, Enum):
    """Enumeration of deception decoy (honey token) categories."""

    FAKE_HTTP_HEADER = "FAKE_HTTP_HEADER"
    HIDDEN_DECOY_URL = "HIDDEN_DECOY_URL"
    FAKE_API_KEY = "FAKE_API_KEY"
    DECOY_SESSION_COOKIE = "DECOY_SESSION_COOKIE"


class InjectionVectorEnum(str, Enum):
    """Enumeration of HTTP response vectors where honey tokens are injected."""

    RESPONSE_HEADER = "RESPONSE_HEADER"
    JSON_PAYLOAD_FIELD = "JSON_PAYLOAD_FIELD"
    HTML_COMMENT_LINK = "HTML_COMMENT_LINK"


class HoneyTokenCreateContract(BaseModel):
    """
    Contract defining the generation and injection parameters of a honey token
    created by `honey_token_injector` and embedded into responses from `core_web_app`.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=False,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "token_id": "htk_9f8e7d6c5b4a",
                    "token_type": "FAKE_HTTP_HEADER",
                    "injection_vector": "RESPONSE_HEADER",
                    "header_or_field_name": "X-Internal-Debug-Token",
                    "decoy_value": "dbg_live_98a7b6c5d4e3f2a1",
                    "target_url_path": "/api/v1/internal/debug-console",
                    "created_at": "2026-11-05T00:00:00Z",
                    "expires_at": "2026-11-06T00:00:00Z",
                }
            ]
        },
    )

    token_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Unique identifier assigned to the generated honey token.",
    )
    token_type: HoneyTokenTypeEnum = Field(
        ...,
        description="Classification type of the honey token.",
    )
    injection_vector: InjectionVectorEnum = Field(
        ...,
        description="Location vector within the HTTP response where the token is injected.",
    )
    header_or_field_name: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Name of the HTTP header, cookie, or JSON field carrying the decoy token.",
    )
    decoy_value: str = Field(
        ...,
        min_length=4,
        max_length=2048,
        description="Secret-looking decoy value injected to lure attackers.",
    )
    target_url_path: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Decoy URL path associated with or monitored for this honey token.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the honey token was generated.",
    )
    expires_at: datetime = Field(
        ...,
        description="UTC timestamp when the honey token expires.",
    )

    @field_validator("target_url_path")
    @classmethod
    def validate_url_path(cls, value: str) -> str:
        """Ensure target_url_path starts with a forward slash '/'."""
        cleaned = value.strip()
        if not cleaned.startswith("/"):
            raise ValueError("target_url_path must start with a leading '/'.")
        return cleaned

    @field_validator("created_at", "expires_at")
    @classmethod
    def ensure_utc_timestamps(cls, value: datetime) -> datetime:
        """Ensure token timestamps are timezone-aware and normalized to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_expiration_order(self) -> "HoneyTokenCreateContract":
        """Ensure expires_at is strictly after created_at."""
        if self.expires_at <= self.created_at:
            raise ValueError("expires_at must be strictly later than created_at.")
        return self


class HoneyTokenValidationContract(BaseModel):
    """
    Contract representing the result of inspecting an incoming HTTP request at
    `deception_gateway` against active honey tokens.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "token_id": "htk_9f8e7d6c5b4a",
                    "is_triggered": True,
                    "triggered_by_ip": "203.0.113.42",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "request_path": "/api/v1/internal/debug-console",
                    "request_method": "POST",
                    "matched_value": "dbg_live_98a7b6c5d4e3f2a1",
                    "detected_at": "2026-11-05T00:12:00Z",
                }
            ]
        },
    )

    token_id: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Identifier of the honey token that was evaluated or triggered.",
    )
    is_triggered: bool = Field(
        ...,
        description="Boolean flag indicating whether the incoming request tripped the honey token.",
    )
    triggered_by_ip: str = Field(
        ...,
        description="Source IPv4 or IPv6 address of the client that presented the token.",
    )
    session_id: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Session identifier associated with the inspected request.",
    )
    request_path: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="HTTP request path accessed when the token was evaluated.",
    )
    request_method: str = Field(
        ...,
        min_length=3,
        max_length=16,
        description="HTTP method (GET, POST, PUT, DELETE, etc.) used in the request.",
    )
    matched_value: str = Field(
        ...,
        min_length=1,
        max_length=2048,
        description="Exact decoy value or path fragment matched during inspection.",
    )
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the honey token trigger was detected.",
    )

    @field_validator("triggered_by_ip")
    @classmethod
    def validate_triggered_ip(cls, value: str) -> str:
        """Validate that triggered_by_ip is a valid IPv4 or IPv6 address."""
        try:
            ip_obj = ipaddress.ip_address(value.strip())
            return str(ip_obj)
        except ValueError as exc:
            raise ValueError(f"Invalid IPv4/IPv6 address for triggered_by_ip: '{value}'.") from exc

    @field_validator("request_path")
    @classmethod
    def validate_request_path(cls, value: str) -> str:
        """Ensure request_path starts with '/'."""
        cleaned = value.strip()
        if not cleaned.startswith("/"):
            raise ValueError("request_path must start with a leading '/'.")
        return cleaned

    @field_validator("request_method")
    @classmethod
    def validate_http_method(cls, value: str) -> str:
        """Normalize and validate the HTTP request method."""
        allowed_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"}
        method_upper = value.strip().upper()
        if method_upper not in allowed_methods:
            raise ValueError(f"Unsupported HTTP method '{value}'. Must be one of {sorted(allowed_methods)}.")
        return method_upper

    @field_validator("detected_at")
    @classmethod
    def ensure_detected_at_utc(cls, value: datetime) -> datetime:
        """Normalize detected_at timestamp to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
