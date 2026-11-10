"""
PostgreSQL Asynchronous Database Engine and Forensic ORM Models.

Configures SQLAlchemy 2.0 `AsyncEngine` and `async_sessionmaker` aligned with the
`docker-compose.yml` environment variables, and defines the five core forensic
persistence tables corresponding strictly to `shared_contracts`.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

try:
    from sqlalchemy import (
        JSON,
        BigInteger,
        Boolean,
        DateTime,
        Index,
        Integer,
        String,
        Text,
        text,
    )
    from sqlalchemy.ext.asyncio import (
        AsyncEngine,
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    _SQLALCHEMY_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SQLALCHEMY_AVAILABLE = False
    AsyncEngine = Any  # type: ignore[assignment,misc]
    AsyncSession = Any  # type: ignore[assignment,misc]
    async_sessionmaker = Any  # type: ignore[assignment,misc]
    Mapped = Any  # type: ignore[assignment,misc]

    class DeclarativeBase:  # type: ignore[no-redef]
        """Fallback declarative base when SQLAlchemy is not installed in local test env."""

        metadata = type(" _Meta", (), {"create_all": staticmethod(lambda *a, **kw: None)})()

        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def mapped_column(*_args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        default = kwargs.get("default")
        if callable(default):
            return None
        return default

    def String(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return str

    def Integer(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return int

    def BigInteger(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return int

    def Boolean(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return bool

    def DateTime(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return datetime

    def Text(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return str

    def JSON(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return dict

    def Index(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return None

    def text(sql: str) -> str:  # type: ignore[misc]
        return sql

    def create_async_engine(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        raise RuntimeError("SQLAlchemy is not installed.")


logger = logging.getLogger(__name__)


def build_forensic_database_url() -> str:
    """
    Construct the asynchronous PostgreSQL database connection URL from environment
    variables defined in `docker-compose.yml`.
    """
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    pg_user = os.getenv("POSTGRES_USER", "deception_admin")
    pg_password = os.getenv("POSTGRES_PASSWORD", "deception_sec_pass_2026")
    pg_host = os.getenv("POSTGRES_HOST", "postgresql_store")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_db = os.getenv("POSTGRES_DB", "deception_forensics_db")
    return f"postgresql+asyncpg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"


FORENSIC_DATABASE_URL: str = build_forensic_database_url()


class ForensicBase(DeclarativeBase):
    """Declarative base class for all Layer 4 forensic and SOC ORM models."""


class SecurityAlertLogORM(ForensicBase):
    """
    ORM model for the `security_alerts_log` table storing `SecurityAlertContract` records.
    """

    __tablename__ = "security_alerts_log"

    alert_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    severity: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_ip: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    triggered_token_id: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, index=True
    )
    target_endpoint: Mapped[str] = mapped_column(String(1024), nullable=False)
    http_method: Mapped[str] = mapped_column(String(16), nullable=False)
    action_taken: Mapped[str] = mapped_column(String(128), nullable=False)
    summary_message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_headers_snapshot: Mapped[Dict[str, str]] = mapped_column(
        JSON, nullable=False, default=dict
    )

    __table_args__ = (
        Index("ix_security_alerts_session_ts", "session_id", "timestamp"),
    )


class AttackerCommandLogORM(ForensicBase):
    """
    ORM model for the `attacker_commands_log` table storing `AttackerCommandEvent` records.
    """

    __tablename__ = "attacker_commands_log"

    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    container_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    command_line: Mapped[str] = mapped_column(Text, nullable=False)
    working_directory: Mapped[str] = mapped_column(String(1024), nullable=False)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    executed_by_user: Mapped[str] = mapped_column(String(128), nullable=False)
    exit_code: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_attacker_commands_session_ts", "session_id", "timestamp"),
    )


class NetworkTelemetryLogORM(ForensicBase):
    """
    ORM model for the `network_telemetry_log` table storing `NetworkTelemetryEvent` records.
    """

    __tablename__ = "network_telemetry_log"

    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    container_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    source_ip: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_port: Mapped[int] = mapped_column(Integer, nullable=False)
    destination_ip: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    destination_port: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[str] = mapped_column(String(16), nullable=False)
    packet_length_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    ebpf_syscall_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    pcap_chunk_ref: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    __table_args__ = (
        Index("ix_network_telemetry_session_ts", "session_id", "timestamp"),
    )


class ForensicArtifactORM(ForensicBase):
    """
    ORM model for the `forensic_artifacts` table storing `ForensicArtifactContract` records.
    """

    __tablename__ = "forensic_artifacts"

    artifact_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    container_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(2048), nullable=False)
    sha256_checksum: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class IncidentReportORM(ForensicBase):
    """
    ORM model for the `incident_reports` table storing `IncidentReportContract` records.
    """

    __tablename__ = "incident_reports"

    report_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    session_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    attacker_ip: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    attack_start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    attack_end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    total_commands_captured: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    total_packets_captured: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    triggered_tokens_list: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    alerts_timeline: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    artifacts_list: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)


def _create_forensic_engine(db_url: str) -> AsyncEngine:
    """Create the SQLAlchemy 2.0 `AsyncEngine` with appropriate pooling parameters."""
    if not _SQLALCHEMY_AVAILABLE:
        raise RuntimeError("SQLAlchemy is not available.")
    engine_kwargs: Dict[str, Any] = {
        "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
        "future": True,
    }
    if db_url.startswith("postgresql"):
        engine_kwargs.update(
            {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_pre_ping": True,
            }
        )
    return create_async_engine(db_url, **engine_kwargs)


try:
    forensic_engine: Optional[AsyncEngine] = _create_forensic_engine(
        FORENSIC_DATABASE_URL
    )
    ForensicSessionLocal: Optional[async_sessionmaker[AsyncSession]] = (
        async_sessionmaker(
            bind=forensic_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    )
except Exception as exc:  # pragma: no cover
    logger.debug(
        "Forensic asyncpg engine deferred (%s); repositories using in-memory fallback.",
        exc,
    )
    forensic_engine = None
    ForensicSessionLocal = None


async def init_forensic_database() -> bool:
    """
    Create all forensic database tables (`security_alerts_log`, `attacker_commands_log`,
    `network_telemetry_log`, `forensic_artifacts`, `incident_reports`) if they do not exist.

    Returns:
        `True` if DDL execution succeeded against PostgreSQL, `False` if operating in fallback mode.
    """
    if forensic_engine is None:
        return False

    try:
        async with forensic_engine.begin() as conn:
            await conn.run_sync(ForensicBase.metadata.create_all)
        logger.info("Forensic PostgreSQL tables verified and initialized.")
        return True
    except Exception as exc:
        logger.warning(
            "PostgreSQL database unreachable during init_forensic_database (%s). Operating with fallback storage.",
            exc,
        )
        return False


async def get_forensic_db_session() -> AsyncGenerator[Optional[AsyncSession], None]:
    """
    FastAPI-compatible asynchronous dependency generator yielding an `AsyncSession`
    for the forensic PostgreSQL store.
    """
    if ForensicSessionLocal is None:
        yield None
        return

    async with ForensicSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_health() -> bool:
    """
    Execute a lightweight `SELECT 1` probe to verify PostgreSQL database connectivity.

    Returns:
        `True` if the database responds healthy, `False` otherwise.
    """
    if forensic_engine is None:
        return False

    try:
        async with forensic_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as exc:
        logger.debug("Forensic DB health check failed: %s", exc)
        return False
