"""
Core Web Application Database Session Manager and Seeding Engine
(`core_web_app.database_connector.session_manager`).

Provides FastAPI dependency injection (`get_core_db_session`) and automatic table
initialization + realistic enterprise seed data (`init_and_seed_core_db`), complete
with an in-memory fallback store for offline testing.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import secrets
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

try:
    from sqlalchemy import func, select
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:  # pragma: no cover
    AsyncSession = Any  # type: ignore[assignment,misc]
    func = None  # type: ignore[assignment]
    select = None  # type: ignore[assignment]

from core_web_app.database_connector.connection import (
    CoreAppBase,
    CoreAppSessionLocal,
    CoreUserAccount,
    EnterpriseResourceRecord,
    core_db_engine,
)

logger = logging.getLogger(__name__)

_PBKDF2_ITERATIONS = 260_000


def _seed_pbkdf2_hash(password: str, salt_hex: Optional[str] = None) -> str:
    """Compute a deterministic-format PBKDF2-HMAC-SHA256 password hash string."""
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt.hex()}${derived.hex()}"


class InMemoryCoreStore:
    """
    Synchronized in-memory fallback store mirroring `core_app_users` and
    `core_app_records` when PostgreSQL is unreachable in local/CI environments.
    """

    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.users_by_username: Dict[str, CoreUserAccount] = {}
        self.users_by_id: Dict[str, CoreUserAccount] = {}
        self.records_by_id: Dict[str, EnterpriseResourceRecord] = {}
        self.is_seeded: bool = False


fallback_core_store = InMemoryCoreStore()


def _build_default_users() -> List[CoreUserAccount]:
    """Construct the initial legitimate enterprise user accounts."""
    now_utc = datetime.now(timezone.utc)
    return [
        CoreUserAccount(
            user_id="usr_admin_001",
            username="sec_admin",
            email="sec_admin@enterprise-core.internal",
            password_hash=_seed_pbkdf2_hash("EnterpriseAdmin#2026!"),
            role="admin",
            is_active=True,
            created_at=now_utc,
        ),
        CoreUserAccount(
            user_id="usr_eng_002",
            username="devops_lead",
            email="devops_lead@enterprise-core.internal",
            password_hash=_seed_pbkdf2_hash("DevOpsLead#2026!"),
            role="engineer",
            is_active=True,
            created_at=now_utc,
        ),
        CoreUserAccount(
            user_id="usr_aud_003",
            username="soc_auditor",
            email="soc_auditor@enterprise-core.internal",
            password_hash=_seed_pbkdf2_hash("SocAuditor#2026!"),
            role="auditor",
            is_active=True,
            created_at=now_utc,
        ),
    ]


def _build_default_records() -> List[EnterpriseResourceRecord]:
    """Construct realistic enterprise resource records for the production web application."""
    now_utc = datetime.now(timezone.utc)
    return [
        EnterpriseResourceRecord(
            record_id="rec_fin_1001",
            title="Q4 Sovereign Cloud Infrastructure Ledger",
            department="Cloud FinOps & Treasury",
            classification_level="CONFIDENTIAL",
            owner_username="sec_admin",
            payload_summary=(
                "Quarterly multi-region compute allocation and cryptographic HSM cluster "
                "maintenance schedule across primary production availability zones."
            ),
            metadata_tags={
                "region": "eu-central-1",
                "compliance_tier": "ISO-27001",
                "audit_cycle": "2026-Q4",
            },
            created_at=now_utc,
            updated_at=now_utc,
        ),
        EnterpriseResourceRecord(
            record_id="rec_sec_1002",
            title="Zero-Trust Micro-Segmentation Policy Matrix",
            department="Enterprise Information Security",
            classification_level="RESTRICTED",
            owner_username="devops_lead",
            payload_summary=(
                "East-West mutual TLS (mTLS) service mesh enforcement baselines and "
                "egress firewall rules for tier-1 core payment microservices."
            ),
            metadata_tags={
                "mesh_version": "istio-1.22",
                "mtls_mode": "STRICT",
                "last_reviewed_by": "sec_admin",
            },
            created_at=now_utc,
            updated_at=now_utc,
        ),
        EnterpriseResourceRecord(
            record_id="rec_ops_1003",
            title="Disaster Recovery Active-Active Failover Runbook",
            department="Site Reliability Engineering",
            classification_level="INTERNAL",
            owner_username="soc_auditor",
            payload_summary=(
                "AutomatedPostgreSQL synchronous replication switchover procedure and "
                "RTO/RPO verification metrics for core API clusters."
            ),
            metadata_tags={
                "rto_seconds": 30,
                "rpo_seconds": 0,
                "cluster_topology": "primary-standby-async",
            },
            created_at=now_utc,
            updated_at=now_utc,
        ),
    ]


async def _seed_memory_fallback() -> None:
    """Populate the in-memory fallback store if not already seeded."""
    async with fallback_core_store.lock:
        if fallback_core_store.is_seeded:
            return
        for user in _build_default_users():
            fallback_core_store.users_by_username[user.username] = user
            fallback_core_store.users_by_id[user.user_id] = user
        for rec in _build_default_records():
            fallback_core_store.records_by_id[rec.record_id] = rec
        fallback_core_store.is_seeded = True


async def init_and_seed_core_db() -> bool:
    """
    Create the `core_app_users` and `core_app_records` tables if they do not exist,
    and seed initial accounts and enterprise resource records if the tables are empty.

    Returns:
        `True` if PostgreSQL seeding succeeded, `False` if operating on the in-memory fallback.
    """
    await _seed_memory_fallback()

    if core_db_engine is None or CoreAppSessionLocal is None:
        return False

    try:
        async with core_db_engine.begin() as conn:
            await conn.run_sync(CoreAppBase.metadata.create_all)

        async with CoreAppSessionLocal() as session:
            user_count_stmt = select(func.count()).select_from(CoreUserAccount)
            user_count = (await session.execute(user_count_stmt)).scalar() or 0
            if user_count == 0:
                session.add_all(_build_default_users())

            record_count_stmt = select(func.count()).select_from(
                EnterpriseResourceRecord
            )
            record_count = (await session.execute(record_count_stmt)).scalar() or 0
            if record_count == 0:
                session.add_all(_build_default_records())

            await session.commit()

        logger.info("Core Web App database tables initialized and seeded.")
        return True
    except Exception as exc:
        logger.warning(
            "PostgreSQL unavailable during init_and_seed_core_db (%s). Using seeded in-memory store.",
            exc,
        )
        return False


async def get_core_db_session() -> AsyncGenerator[Optional[AsyncSession], None]:
    """
    FastAPI dependency generator yielding an `AsyncSession` connected to the
    legitimate Core Web Application database, or `None` when using fallback storage.
    """
    await _seed_memory_fallback()

    if CoreAppSessionLocal is None:
        yield None
        return

    session: Optional[AsyncSession] = None
    try:
        session = CoreAppSessionLocal()
        yield session
        await session.commit()
    except Exception:
        if session is not None:
            try:
                await session.rollback()
            except Exception:
                pass
        raise
    finally:
        if session is not None:
            try:
                await session.close()
            except Exception:
                pass
