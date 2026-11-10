"""
Database Connector Subpackage for the Core Web Application (`core_web_app.database_connector`).

Exports the isolated SQLAlchemy 2.0 `AsyncEngine`, ORM models (`CoreUserAccount`,
`EnterpriseResourceRecord`), FastAPI session dependency (`get_core_db_session`),
and database initialization/seeding utility (`init_and_seed_core_db`).
"""

from core_web_app.database_connector.connection import (
    CORE_DATABASE_URL,
    CoreAppBase,
    CoreAppSessionLocal,
    CoreUserAccount,
    EnterpriseResourceRecord,
    build_core_database_url,
    core_db_engine,
)
from core_web_app.database_connector.session_manager import (
    InMemoryCoreStore,
    fallback_core_store,
    get_core_db_session,
    init_and_seed_core_db,
)

__all__ = [
    "CORE_DATABASE_URL",
    "build_core_database_url",
    "core_db_engine",
    "CoreAppSessionLocal",
    "CoreAppBase",
    "CoreUserAccount",
    "EnterpriseResourceRecord",
    "InMemoryCoreStore",
    "fallback_core_store",
    "get_core_db_session",
    "init_and_seed_core_db",
]
