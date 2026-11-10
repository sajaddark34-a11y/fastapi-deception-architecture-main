"""
PostgreSQL Storage Subpackage (`data_storage.postgresql_store`).

Exposes the asynchronous SQLAlchemy 2.0 database engine, ORM models, session
dependencies, and forensic repositories (`ForensicLogsRepository`,
`ForensicArtifactsRepository`).
"""

from data_storage.postgresql_store.database_engine import (
    FORENSIC_DATABASE_URL,
    AttackerCommandLogORM,
    ForensicArtifactORM,
    ForensicBase,
    ForensicSessionLocal,
    IncidentReportORM,
    NetworkTelemetryLogORM,
    SecurityAlertLogORM,
    build_forensic_database_url,
    check_db_health,
    forensic_engine,
    get_forensic_db_session,
    init_forensic_database,
)
from data_storage.postgresql_store.forensic_artifacts_repository import (
    ForensicArtifactsRepository,
)
from data_storage.postgresql_store.logs_repository import ForensicLogsRepository

forensic_logs_repository = ForensicLogsRepository()
forensic_artifacts_repository = ForensicArtifactsRepository()

__all__ = [
    # Engine & Session Management
    "FORENSIC_DATABASE_URL",
    "build_forensic_database_url",
    "forensic_engine",
    "ForensicSessionLocal",
    "ForensicBase",
    "init_forensic_database",
    "get_forensic_db_session",
    "check_db_health",
    # ORM Models
    "SecurityAlertLogORM",
    "AttackerCommandLogORM",
    "NetworkTelemetryLogORM",
    "ForensicArtifactORM",
    "IncidentReportORM",
    # Repositories & Singletons
    "ForensicLogsRepository",
    "ForensicArtifactsRepository",
    "forensic_logs_repository",
    "forensic_artifacts_repository",
]
