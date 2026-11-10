"""
Data Storage Layer Package (`data_storage`).

Unified export interface for Layer 4 persistence subsystems:
- Redis Store (`data_storage.redis_store`): Sub-millisecond session states, sandbox
  bindings, and real-time security alert/telemetry streams.
- PostgreSQL Store (`data_storage.postgresql_store`): Immutable forensic logs,
  SHA-256 verified artifacts, and SOC incident reports.
"""

from data_storage.postgresql_store import (
    FORENSIC_DATABASE_URL,
    AttackerCommandLogORM,
    ForensicArtifactORM,
    ForensicArtifactsRepository,
    ForensicBase,
    ForensicLogsRepository,
    ForensicSessionLocal,
    IncidentReportORM,
    NetworkTelemetryLogORM,
    SecurityAlertLogORM,
    build_forensic_database_url,
    check_db_health,
    forensic_artifacts_repository,
    forensic_engine,
    forensic_logs_repository,
    get_forensic_db_session,
    init_forensic_database,
)
from data_storage.redis_store import (
    FastAlertsStream,
    SessionStateStore,
    fast_alerts_stream,
    session_state_store,
)

__all__ = [
    # Redis Store
    "SessionStateStore",
    "FastAlertsStream",
    "session_state_store",
    "fast_alerts_stream",
    # PostgreSQL Engine & Lifecycle
    "FORENSIC_DATABASE_URL",
    "build_forensic_database_url",
    "forensic_engine",
    "ForensicSessionLocal",
    "ForensicBase",
    "init_forensic_database",
    "get_forensic_db_session",
    "check_db_health",
    # PostgreSQL ORM Models
    "SecurityAlertLogORM",
    "AttackerCommandLogORM",
    "NetworkTelemetryLogORM",
    "ForensicArtifactORM",
    "IncidentReportORM",
    # PostgreSQL Repositories & Singletons
    "ForensicLogsRepository",
    "ForensicArtifactsRepository",
    "forensic_logs_repository",
    "forensic_artifacts_repository",
]
