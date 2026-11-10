"""
Forensic Artifacts and SOC Incident Reports Repository
(`data_storage.postgresql_store.forensic_artifacts_repository`).

Manages SHA-256 chain-of-custody verification for extracted forensic evidence
(`ForensicArtifactContract`) and persists comprehensive SOC incident reports
(`IncidentReportContract`) in PostgreSQL with an automatic in-memory fallback.
"""

from __future__ import annotations

import asyncio
import hmac
import logging
from typing import Any, Dict, List, Optional

try:
    from sqlalchemy import desc, select
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
except ImportError:  # pragma: no cover
    AsyncSession = Any  # type: ignore[assignment,misc]
    async_sessionmaker = Any  # type: ignore[assignment,misc]
    desc = None  # type: ignore[assignment]
    select = None  # type: ignore[assignment]

from data_storage.postgresql_store.database_engine import (
    ForensicArtifactORM,
    ForensicSessionLocal,
    IncidentReportORM,
)
from shared_contracts.forensic_artifact_schema import (
    ArtifactTypeEnum,
    ForensicArtifactContract,
    IncidentReportContract,
)

logger = logging.getLogger(__name__)


class ForensicArtifactsRepository:
    """
    Asynchronous repository for storing, verifying, and retrieving forensic evidence
    artifacts (`ForensicArtifactContract`) and compiled SOC incident reports
    (`IncidentReportContract`).
    """

    def __init__(
        self,
        session_factory: Optional[Any] = None,
    ) -> None:
        """
        Initialize the repository with a SQLAlchemy async session factory and
        in-memory fallback collections.
        """
        self._session_factory = session_factory or ForensicSessionLocal
        self._lock = asyncio.Lock()
        self._mem_artifacts: Dict[str, ForensicArtifactContract] = {}
        self._mem_reports: Dict[str, IncidentReportContract] = {}

    @staticmethod
    def _orm_to_artifact(row: ForensicArtifactORM) -> ForensicArtifactContract:
        """Convert a `ForensicArtifactORM` entity into a validated `ForensicArtifactContract`."""
        return ForensicArtifactContract(
            artifact_id=row.artifact_id,
            session_id=row.session_id,
            container_id=row.container_id,
            artifact_type=ArtifactTypeEnum(row.artifact_type),
            file_name=row.file_name,
            storage_uri=row.storage_uri,
            sha256_checksum=row.sha256_checksum,
            file_size_bytes=row.file_size_bytes,
            captured_at=row.captured_at,
            is_verified=row.is_verified,
        )

    @staticmethod
    def _orm_to_report(row: IncidentReportORM) -> IncidentReportContract:
        """Convert an `IncidentReportORM` entity into a validated `IncidentReportContract`."""
        parsed_artifacts = [
            ForensicArtifactContract.model_validate(item)
            for item in (row.artifacts_list or [])
        ]
        return IncidentReportContract(
            report_id=row.report_id,
            generated_at=row.generated_at,
            session_id=row.session_id,
            attacker_ip=row.attacker_ip,
            attack_start_time=row.attack_start_time,
            attack_end_time=row.attack_end_time,
            total_commands_captured=row.total_commands_captured,
            total_packets_captured=row.total_packets_captured,
            triggered_tokens_list=list(row.triggered_tokens_list or []),
            alerts_timeline=list(row.alerts_timeline or []),
            artifacts_list=parsed_artifacts,
            executive_summary=row.executive_summary,
        )

    async def register_artifact(
        self, artifact: ForensicArtifactContract
    ) -> ForensicArtifactContract:
        """
        Register and persist a verified `ForensicArtifactContract` in PostgreSQL.

        Args:
            artifact: Validated `ForensicArtifactContract` instance.

        Returns:
            The persisted `ForensicArtifactContract`.
        """
        async with self._lock:
            self._mem_artifacts[artifact.artifact_id] = artifact

        if self._session_factory is not None:
            try:
                async with self._session_factory() as db:
                    orm_obj = ForensicArtifactORM(
                        artifact_id=artifact.artifact_id,
                        session_id=artifact.session_id,
                        container_id=artifact.container_id,
                        artifact_type=artifact.artifact_type.value,
                        file_name=artifact.file_name,
                        storage_uri=artifact.storage_uri,
                        sha256_checksum=artifact.sha256_checksum,
                        file_size_bytes=artifact.file_size_bytes,
                        captured_at=artifact.captured_at,
                        is_verified=artifact.is_verified,
                    )
                    await db.merge(orm_obj)
                    await db.commit()
            except Exception as exc:
                logger.warning(
                    "PostgreSQL register_artifact fallback to memory (%s).", exc
                )

        return artifact

    async def get_artifact_by_id(
        self, artifact_id: str
    ) -> Optional[ForensicArtifactContract]:
        """
        Retrieve a single forensic artifact by its unique `artifact_id`.

        Args:
            artifact_id: Unique identifier of the forensic artifact.

        Returns:
            `ForensicArtifactContract` if found, otherwise `None`.
        """
        cleaned_id = artifact_id.strip()
        if not cleaned_id:
            return None

        if self._session_factory is not None:
            try:
                async with self._session_factory() as db:
                    row = await db.get(ForensicArtifactORM, cleaned_id)
                    if row is not None:
                        return self._orm_to_artifact(row)
            except Exception as exc:
                logger.warning(
                    "PostgreSQL get_artifact_by_id fallback to memory (%s).", exc
                )

        async with self._lock:
            return self._mem_artifacts.get(cleaned_id)

    async def list_artifacts_by_session(
        self, session_id: str
    ) -> List[ForensicArtifactContract]:
        """
        List all forensic artifacts extracted for a specific `session_id`
        ordered chronologically by `captured_at`.

        Args:
            session_id: Session identifier of the trapped attacker.

        Returns:
            List of `ForensicArtifactContract` objects.
        """
        cleaned_id = session_id.strip()
        if not cleaned_id:
            return []

        results: Dict[str, ForensicArtifactContract] = {}

        if self._session_factory is not None and select is not None:
            try:
                async with self._session_factory() as db:
                    stmt = (
                        select(ForensicArtifactORM)
                        .where(ForensicArtifactORM.session_id == cleaned_id)
                        .order_by(ForensicArtifactORM.captured_at.asc())
                    )
                    rows = (await db.execute(stmt)).scalars().all()
                    for row in rows:
                        art = self._orm_to_artifact(row)
                        results[art.artifact_id] = art
            except Exception as exc:
                logger.warning(
                    "PostgreSQL list_artifacts_by_session fallback to memory (%s).",
                    exc,
                )

        async with self._lock:
            for art in self._mem_artifacts.values():
                if art.session_id == cleaned_id and art.artifact_id not in results:
                    results[art.artifact_id] = art

        return sorted(results.values(), key=lambda a: a.captured_at)

    async def verify_artifact_checksum(
        self, artifact_id: str, computed_sha256: str
    ) -> bool:
        """
        Cryptographically verify an artifact's chain-of-custody SHA-256 digest against
        `computed_sha256` using constant-time comparison, updating `is_verified` in storage.

        Args:
            artifact_id: Identifier of the artifact to verify.
            computed_sha256: Hexadecimal SHA-256 hash computed from the stored file.

        Returns:
            `True` if the artifact exists and its SHA-256 checksum matches `computed_sha256`,
            `False` otherwise.
        """
        artifact = await self.get_artifact_by_id(artifact_id)
        if artifact is None:
            return False

        expected = artifact.sha256_checksum.strip().lower()
        candidate = computed_sha256.strip().lower()
        is_match = hmac.compare_digest(expected, candidate)

        if artifact.is_verified != is_match:
            updated_artifact = artifact.model_copy(update={"is_verified": is_match})
            await self.register_artifact(updated_artifact)

        return is_match

    async def create_incident_report(
        self, report: IncidentReportContract
    ) -> IncidentReportContract:
        """
        Persist a comprehensive `IncidentReportContract` in PostgreSQL.

        Args:
            report: Validated `IncidentReportContract` instance.

        Returns:
            The persisted `IncidentReportContract`.
        """
        async with self._lock:
            self._mem_reports[report.report_id] = report

        if self._session_factory is not None:
            try:
                serialized_artifacts = [
                    art.model_dump(mode="json") for art in report.artifacts_list
                ]
                async with self._session_factory() as db:
                    orm_obj = IncidentReportORM(
                        report_id=report.report_id,
                        generated_at=report.generated_at,
                        session_id=report.session_id,
                        attacker_ip=report.attacker_ip,
                        attack_start_time=report.attack_start_time,
                        attack_end_time=report.attack_end_time,
                        total_commands_captured=report.total_commands_captured,
                        total_packets_captured=report.total_packets_captured,
                        triggered_tokens_list=list(report.triggered_tokens_list),
                        alerts_timeline=list(report.alerts_timeline),
                        artifacts_list=serialized_artifacts,
                        executive_summary=report.executive_summary,
                    )
                    await db.merge(orm_obj)
                    await db.commit()
            except Exception as exc:
                logger.warning(
                    "PostgreSQL create_incident_report fallback to memory (%s).", exc
                )

        return report

    async def get_incident_report(
        self, report_id: str
    ) -> Optional[IncidentReportContract]:
        """
        Retrieve a single compiled incident report by `report_id`.

        Args:
            report_id: Unique incident report identifier.

        Returns:
            `IncidentReportContract` if found, else `None`.
        """
        cleaned_id = report_id.strip()
        if not cleaned_id:
            return None

        if self._session_factory is not None:
            try:
                async with self._session_factory() as db:
                    row = await db.get(IncidentReportORM, cleaned_id)
                    if row is not None:
                        return self._orm_to_report(row)
            except Exception as exc:
                logger.warning(
                    "PostgreSQL get_incident_report fallback to memory (%s).", exc
                )

        async with self._lock:
            return self._mem_reports.get(cleaned_id)

    async def list_incident_reports(
        self, limit: int = 50
    ) -> List[IncidentReportContract]:
        """
        List compiled SOC incident reports ordered from newest to oldest (`generated_at` desc).

        Args:
            limit: Maximum number of incident reports to return (default 50).

        Returns:
            List of `IncidentReportContract` instances.
        """
        effective_limit = max(1, limit)
        results: Dict[str, IncidentReportContract] = {}

        if self._session_factory is not None and select is not None and desc is not None:
            try:
                async with self._session_factory() as db:
                    stmt = (
                        select(IncidentReportORM)
                        .order_by(desc(IncidentReportORM.generated_at))
                        .limit(effective_limit)
                    )
                    rows = (await db.execute(stmt)).scalars().all()
                    for row in rows:
                        rep = self._orm_to_report(row)
                        results[rep.report_id] = rep
            except Exception as exc:
                logger.warning(
                    "PostgreSQL list_incident_reports fallback to memory (%s).", exc
                )

        async with self._lock:
            for rep in self._mem_reports.values():
                if rep.report_id not in results:
                    results[rep.report_id] = rep

        sorted_reports = sorted(
            results.values(),
            key=lambda r: r.generated_at,
            reverse=True,
        )
        return sorted_reports[:effective_limit]
