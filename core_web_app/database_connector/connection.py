"""
Core Web Application Database Connector (`core_web_app.database_connector.connection`).

Configures an independent SQLAlchemy 2.0 `AsyncEngine` and declarative base for the
legitimate production application (`core_web_app`), strictly segregated from Layer 4
forensic tables by using the `core_app_` table namespace (`core_app_users` and
`core_app_records`).
"""

from __future__ import annotations

import logging
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from sqlalchemy import JSON, Boolean, DateTime, String, Text
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
        """Fallback declarative base when SQLAlchemy is unavailable in local test env."""

        metadata = type("_Meta", (), {"create_all": staticmethod(lambda *a, **kw: None)})()

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

    def Boolean(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return bool

    def DateTime(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return datetime

    def Text(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return str

    def JSON(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        return dict

    def create_async_engine(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[misc]
        raise RuntimeError("SQLAlchemy is not installed.")

logger = logging.getLogger(__name__)


def _is_tcp_reachable(host: str, port: int, timeout: float = 0.25) -> bool:
    """Return True if `host:port` accepts a TCP connection."""
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except Exception:
        return False


def build_core_database_url() -> str:
    """
    Construct the asynchronous PostgreSQL database connection URL for `core_web_app`
    aligned with `docker-compose.yml` environment variables, with automatic
    `sqlite+aiosqlite` fallback when an external PostgreSQL server is offline.
    """
    explicit_url = os.getenv("CORE_DATABASE_URL") or os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    pg_user = os.getenv("POSTGRES_USER", "deception_admin")
    pg_password = os.getenv("POSTGRES_PASSWORD", "deception_sec_pass_2026")
    pg_host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_db = os.getenv("POSTGRES_DB", "deception_forensics_db")

    if _is_tcp_reachable(pg_host, int(pg_port)):
        return f"postgresql+asyncpg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"

    try:
        import aiosqlite  # noqa: F401

        sqlite_dir = Path(__file__).resolve().parents[2] / "artifacts_vault"
        sqlite_dir.mkdir(parents=True, exist_ok=True)
        sqlite_path = (sqlite_dir / "core_web_app.db").as_posix()
        return f"sqlite+aiosqlite:///{sqlite_path}"
    except ImportError:
        return f"postgresql+asyncpg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"


CORE_DATABASE_URL: str = build_core_database_url()


class CoreAppBase(DeclarativeBase):
    """Independent declarative base for the legitimate Core Web Application."""


class CoreUserAccount(CoreAppBase):
    """
    ORM model representing a legitimate user account in the enterprise web application.
    Stored in the isolated `core_app_users` table.
    """

    __tablename__ = "core_app_users"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="engineer")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class EnterpriseResourceRecord(CoreAppBase):
    """
    ORM model representing sensitive enterprise resource records managed by legitimate
    authenticated users in the production application (`core_app_records`).
    """

    __tablename__ = "core_app_records"

    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    classification_level: Mapped[str] = mapped_column(
        String(64), nullable=False, default="CONFIDENTIAL", index=True
    )
    owner_username: Mapped[str] = mapped_column(
        String(128), nullable=False, index=True
    )
    payload_summary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_tags: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


def _create_core_engine(db_url: str) -> AsyncEngine:
    """Create the SQLAlchemy 2.0 `AsyncEngine` for `core_web_app`."""
    engine_kwargs: Dict[str, Any] = {
        "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
        "future": True,
    }
    if db_url.startswith("postgresql"):
        engine_kwargs.update(
            {
                "pool_size": 8,
                "max_overflow": 16,
                "pool_pre_ping": True,
            }
        )
    return create_async_engine(db_url, **engine_kwargs)


try:
    core_db_engine: Optional[AsyncEngine] = _create_core_engine(CORE_DATABASE_URL)
    CoreAppSessionLocal: Optional[async_sessionmaker[AsyncSession]] = (
        async_sessionmaker(
            bind=core_db_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    )
except Exception as exc:  # pragma: no cover
    logger.warning(
        "Core web app database engine initialization deferred (%s); fallback storage enabled.",
        exc,
    )
    core_db_engine = None
    CoreAppSessionLocal = None
