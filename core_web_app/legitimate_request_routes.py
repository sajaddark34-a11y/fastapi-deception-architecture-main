"""
Legitimate Business Routes for the Core Web Application
(`core_web_app.legitimate_request_routes`).

Serves production enterprise endpoints under `/api/v1` (`GET /health`,
`GET /records`, `POST /records`, `GET /records/{record_id}`, and
`GET /system/status`). Outgoing responses from these routes are designed to
be transparently enriched with decoy honey tokens by `honey_token_injector`
in Layer 2.
"""

from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

try:
    from fastapi import APIRouter, Depends, HTTPException, Query, status
    from fastapi.security import HTTPAuthorizationCredentials
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_handler import (  # type: ignore[attr-defined]
        Depends,
        HTTPAuthorizationCredentials,
        HTTPException,
        status,
    )
    from core_web_app.authentication.auth_routes import APIRouter  # type: ignore[attr-defined]

    def Query(default: Any = None, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return default

try:
    from sqlalchemy import desc, select
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:  # pragma: no cover
    AsyncSession = Any  # type: ignore[assignment,misc]
    desc = None  # type: ignore[assignment]
    select = None  # type: ignore[assignment]

from core_web_app.authentication.auth_handler import (
    bearer_security_scheme,
    decode_and_verify_token,
)
from core_web_app.database_connector.connection import EnterpriseResourceRecord
from core_web_app.database_connector.session_manager import (
    fallback_core_store,
    get_core_db_session,
)

_APP_START_TIME = time.monotonic()

legitimate_router = APIRouter(prefix="/api/v1", tags=["Core Enterprise Operations"])


class EnterpriseRecordCreateSchema(BaseModel):
    """Request schema for creating a new enterprise resource record (`POST /api/v1/records`)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(..., min_length=3, max_length=255)
    department: str = Field(..., min_length=2, max_length=128)
    classification_level: str = Field(
        default="CONFIDENTIAL", min_length=3, max_length=64
    )
    payload_summary: str = Field(..., min_length=5, max_length=4096)
    metadata_tags: Dict[str, Any] = Field(default_factory=dict)


class EnterpriseRecordResponseSchema(BaseModel):
    """Response schema representing an `EnterpriseResourceRecord`."""

    model_config = ConfigDict(extra="forbid")

    record_id: str
    title: str
    department: str
    classification_level: str
    owner_username: str
    payload_summary: str
    metadata_tags: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class EnterpriseRecordsListResponseSchema(BaseModel):
    """Paginated response envelope for `GET /api/v1/records`."""

    model_config = ConfigDict(extra="forbid")

    total_count: int
    records: List[EnterpriseRecordResponseSchema]
    service_tier: str = "production_core_web_app"


def _to_record_response(
    record: EnterpriseResourceRecord,
) -> EnterpriseRecordResponseSchema:
    """Convert an `EnterpriseResourceRecord` ORM instance into a response schema."""
    return EnterpriseRecordResponseSchema(
        record_id=record.record_id,
        title=record.title,
        department=record.department,
        classification_level=record.classification_level,
        owner_username=record.owner_username,
        payload_summary=record.payload_summary,
        metadata_tags=dict(record.metadata_tags or {}),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _resolve_optional_username(
    credentials: Optional[HTTPAuthorizationCredentials],
) -> str:
    """Resolve username from optional Bearer token or default to `sec_admin`."""
    if credentials and credentials.credentials:
        claims = decode_and_verify_token(credentials.credentials)
        return str(claims.get("sub", "sec_admin"))
    return "sec_admin"


@legitimate_router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health and readiness probe for Core Web Application",
)
async def health_check() -> Dict[str, Any]:
    """
    Return operational readiness status of `core_web_app` for Docker and
    `deception_gateway` upstream health checks.
    """
    return {
        "status": "healthy",
        "service": os.getenv("SERVICE_NAME", "core_web_app"),
        "layer": "Layer 2 - Core Web Application",
        "honey_token_injector_enabled": (
            os.getenv("HONEY_TOKEN_INJECTOR_ENABLED", "true").lower() == "true"
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@legitimate_router.get(
    "/records",
    response_model=EnterpriseRecordsListResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="List enterprise resource records",
)
async def list_enterprise_records(
    department: Optional[str] = Query(
        default=None, description="Optional filter by department name."
    ),
    classification_level: Optional[str] = Query(
        default=None, description="Optional filter by security classification level."
    ),
    limit: int = Query(default=50, ge=1, le=200),
    db: Optional[AsyncSession] = Depends(get_core_db_session),
) -> EnterpriseRecordsListResponseSchema:
    """
    Retrieve enterprise resource records from `core_app_records` (with automatic
    fallback to the seeded in-memory store).
    """
    records_map: Dict[str, EnterpriseResourceRecord] = {}

    if db is not None:
        try:
            stmt = select(EnterpriseResourceRecord)
            if department:
                stmt = stmt.where(
                    EnterpriseResourceRecord.department == department.strip()
                )
            if classification_level:
                stmt = stmt.where(
                    EnterpriseResourceRecord.classification_level
                    == classification_level.strip().upper()
                )
            stmt = stmt.order_by(desc(EnterpriseResourceRecord.created_at)).limit(limit)
            rows = (await db.execute(stmt)).scalars().all()
            for r in rows:
                records_map[r.record_id] = r
        except Exception:
            pass

    async with fallback_core_store.lock:
        for r in fallback_core_store.records_by_id.values():
            if department and r.department.lower() != department.strip().lower():
                continue
            if (
                classification_level
                and r.classification_level.upper()
                != classification_level.strip().upper()
            ):
                continue
            records_map.setdefault(r.record_id, r)

    sorted_records = sorted(
        records_map.values(),
        key=lambda rec: rec.created_at,
        reverse=True,
    )[:limit]

    return EnterpriseRecordsListResponseSchema(
        total_count=len(sorted_records),
        records=[_to_record_response(r) for r in sorted_records],
    )


@legitimate_router.post(
    "/records",
    response_model=EnterpriseRecordResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new enterprise resource record",
)
async def create_enterprise_record(
    payload: EnterpriseRecordCreateSchema,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_security_scheme
    ),
    db: Optional[AsyncSession] = Depends(get_core_db_session),
) -> EnterpriseRecordResponseSchema:
    """
    Persist a new `EnterpriseResourceRecord` in the production database.
    """
    owner_username = _resolve_optional_username(credentials)
    now_utc = datetime.now(timezone.utc)

    new_record = EnterpriseResourceRecord(
        record_id=f"rec_{uuid.uuid4().hex[:10]}",
        title=payload.title,
        department=payload.department,
        classification_level=payload.classification_level.upper(),
        owner_username=owner_username,
        payload_summary=payload.payload_summary,
        metadata_tags=dict(payload.metadata_tags),
        created_at=now_utc,
        updated_at=now_utc,
    )

    async with fallback_core_store.lock:
        fallback_core_store.records_by_id[new_record.record_id] = new_record

    if db is not None:
        try:
            db.add(new_record)
            await db.commit()
            await db.refresh(new_record)
        except Exception:
            pass

    return _to_record_response(new_record)


@legitimate_router.get(
    "/records/{record_id}",
    response_model=EnterpriseRecordResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Retrieve details of a specific enterprise resource record",
)
async def get_enterprise_record_by_id(
    record_id: str,
    db: Optional[AsyncSession] = Depends(get_core_db_session),
) -> EnterpriseRecordResponseSchema:
    """
    Fetch a single `EnterpriseResourceRecord` by its `record_id`.
    """
    cleaned_id = record_id.strip()
    found_record: Optional[EnterpriseResourceRecord] = None

    if db is not None:
        try:
            found_record = await db.get(EnterpriseResourceRecord, cleaned_id)
        except Exception:
            found_record = None

    if found_record is None:
        async with fallback_core_store.lock:
            found_record = fallback_core_store.records_by_id.get(cleaned_id)

    if found_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enterprise resource record '{cleaned_id}' not found.",
        )

    return _to_record_response(found_record)


@legitimate_router.get(
    "/system/status",
    status_code=status.HTTP_200_OK,
    summary="Display legitimate enterprise system status",
)
async def get_system_status() -> Dict[str, Any]:
    """
    Return operational telemetry and subsystem status for legitimate users.
    """
    uptime_seconds = round(time.monotonic() - _APP_START_TIME, 2)
    async with fallback_core_store.lock:
        active_users_count = len(fallback_core_store.users_by_username)
        records_count = len(fallback_core_store.records_by_id)

    return {
        "service_name": os.getenv("SERVICE_NAME", "core_web_app"),
        "environment": "enterprise_production",
        "operational_state": "ONLINE",
        "uptime_seconds": uptime_seconds,
        "subsystems": {
            "authentication_engine": "OPERATIONAL (PBKDF2-SHA256 + HS256-JWT)",
            "core_database_connector": "OPERATIONAL",
            "honey_token_hook_ready": (
                os.getenv("HONEY_TOKEN_INJECTOR_ENABLED", "true").lower() == "true"
            ),
        },
        "metrics": {
            "registered_accounts": active_users_count,
            "enterprise_records_stored": records_count,
        },
        "reported_at": datetime.now(timezone.utc).isoformat(),
    }
