"""
Forensic Logs Repository (`data_storage.postgresql_store.logs_repository`).

Implements the Repository Pattern for persisting and querying security alerts
(`SecurityAlertContract`), attacker shell commands (`AttackerCommandEvent`), and
network/eBPF telemetry (`NetworkTelemetryEvent`) in PostgreSQL, with an integrated
in-memory fallback for local testing without an external database server.
"""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
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
    AttackerCommandLogORM,
    ForensicSessionLocal,
    NetworkTelemetryLogORM,
    SecurityAlertLogORM,
)
from shared_contracts.alert_schema import (
    AlertSeverityEnum,
    AttackCategoryEnum,
    SecurityAlertContract,
)
from shared_contracts.telemetry_schema import (
    AttackerCommandEvent,
    NetworkTelemetryEvent,
    TelemetryStreamEnvelope,
)

logger = logging.getLogger(__name__)


class ForensicLogsRepository:
    """
    Asynchronous repository providing persistence and analytical aggregation over
    security alerts, sandbox attacker commands, and network/eBPF telemetry.
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
        self._mem_alerts: Dict[str, SecurityAlertContract] = {}
        self._mem_commands: Dict[str, AttackerCommandEvent] = {}
        self._mem_network: Dict[str, NetworkTelemetryEvent] = {}

    @staticmethod
    def _orm_to_alert(row: SecurityAlertLogORM) -> SecurityAlertContract:
        """Convert a `SecurityAlertLogORM` entity into a validated `SecurityAlertContract`."""
        return SecurityAlertContract(
            alert_id=row.alert_id,
            timestamp=row.timestamp,
            severity=AlertSeverityEnum(row.severity),
            category=AttackCategoryEnum(row.category),
            source_ip=row.source_ip,
            session_id=row.session_id,
            triggered_token_id=row.triggered_token_id,
            target_endpoint=row.target_endpoint,
            http_method=row.http_method,
            action_taken=row.action_taken,
            summary_message=row.summary_message,
            raw_headers_snapshot=dict(row.raw_headers_snapshot or {}),
        )

    @staticmethod
    def _orm_to_command(row: AttackerCommandLogORM) -> AttackerCommandEvent:
        """Convert an `AttackerCommandLogORM` entity into a validated `AttackerCommandEvent`."""
        return AttackerCommandEvent(
            event_id=row.event_id,
            session_id=row.session_id,
            container_id=row.container_id,
            timestamp=row.timestamp,
            command_line=row.command_line,
            working_directory=row.working_directory,
            process_id=row.process_id,
            parent_process_id=row.parent_process_id,
            executed_by_user=row.executed_by_user,
            exit_code=row.exit_code,
        )

    @staticmethod
    def _orm_to_network(row: NetworkTelemetryLogORM) -> NetworkTelemetryEvent:
        """Convert a `NetworkTelemetryLogORM` entity into a validated `NetworkTelemetryEvent`."""
        return NetworkTelemetryEvent(
            event_id=row.event_id,
            session_id=row.session_id,
            container_id=row.container_id,
            timestamp=row.timestamp,
            source_ip=row.source_ip,
            source_port=row.source_port,
            destination_ip=row.destination_ip,
            destination_port=row.destination_port,
            protocol=row.protocol,
            packet_length_bytes=row.packet_length_bytes,
            ebpf_syscall_name=row.ebpf_syscall_name,
            pcap_chunk_ref=row.pcap_chunk_ref,
        )

    async def save_security_alert(
        self, alert: SecurityAlertContract
    ) -> SecurityAlertContract:
        """
        Persist a `SecurityAlertContract` into the `security_alerts_log` table.

        Args:
            alert: Validated `SecurityAlertContract` instance.

        Returns:
            The persisted `SecurityAlertContract`.
        """
        async with self._lock:
            self._mem_alerts[alert.alert_id] = alert

        if self._session_factory is not None:
            try:
                async with self._session_factory() as db:
                    orm_obj = SecurityAlertLogORM(
                        alert_id=alert.alert_id,
                        timestamp=alert.timestamp,
                        severity=alert.severity.value,
                        category=alert.category.value,
                        source_ip=alert.source_ip,
                        session_id=alert.session_id,
                        triggered_token_id=alert.triggered_token_id,
                        target_endpoint=alert.target_endpoint,
                        http_method=alert.http_method,
                        action_taken=alert.action_taken,
                        summary_message=alert.summary_message,
                        raw_headers_snapshot=dict(alert.raw_headers_snapshot),
                    )
                    await db.merge(orm_obj)
                    await db.commit()
            except Exception as exc:
                logger.warning(
                    "PostgreSQL save_security_alert fallback to memory (%s).", exc
                )

        return alert

    async def save_command_event(
        self, event: AttackerCommandEvent
    ) -> AttackerCommandEvent:
        """
        Persist an `AttackerCommandEvent` into the `attacker_commands_log` table.

        Args:
            event: Validated `AttackerCommandEvent` instance.

        Returns:
            The persisted `AttackerCommandEvent`.
        """
        async with self._lock:
            self._mem_commands[event.event_id] = event

        if self._session_factory is not None:
            try:
                async with self._session_factory() as db:
                    orm_obj = AttackerCommandLogORM(
                        event_id=event.event_id,
                        session_id=event.session_id,
                        container_id=event.container_id,
                        timestamp=event.timestamp,
                        command_line=event.command_line,
                        working_directory=event.working_directory,
                        process_id=event.process_id,
                        parent_process_id=event.parent_process_id,
                        executed_by_user=event.executed_by_user,
                        exit_code=event.exit_code,
                    )
                    await db.merge(orm_obj)
                    await db.commit()
            except Exception as exc:
                logger.warning(
                    "PostgreSQL save_command_event fallback to memory (%s).", exc
                )

        return event

    async def save_network_event(
        self, event: NetworkTelemetryEvent
    ) -> NetworkTelemetryEvent:
        """
        Persist a `NetworkTelemetryEvent` into the `network_telemetry_log` table.

        Args:
            event: Validated `NetworkTelemetryEvent` instance.

        Returns:
            The persisted `NetworkTelemetryEvent`.
        """
        async with self._lock:
            self._mem_network[event.event_id] = event

        if self._session_factory is not None:
            try:
                async with self._session_factory() as db:
                    orm_obj = NetworkTelemetryLogORM(
                        event_id=event.event_id,
                        session_id=event.session_id,
                        container_id=event.container_id,
                        timestamp=event.timestamp,
                        source_ip=event.source_ip,
                        source_port=event.source_port,
                        destination_ip=event.destination_ip,
                        destination_port=event.destination_port,
                        protocol=event.protocol,
                        packet_length_bytes=event.packet_length_bytes,
                        ebpf_syscall_name=event.ebpf_syscall_name,
                        pcap_chunk_ref=event.pcap_chunk_ref,
                    )
                    await db.merge(orm_obj)
                    await db.commit()
            except Exception as exc:
                logger.warning(
                    "PostgreSQL save_network_event fallback to memory (%s).", exc
                )

        return event

    async def save_telemetry_envelope(
        self, envelope: TelemetryStreamEnvelope
    ) -> bool:
        """
        Unpack a `TelemetryStreamEnvelope` and persist its embedded `command_event`
        and/or `network_event` into PostgreSQL.

        Args:
            envelope: Validated `TelemetryStreamEnvelope` instance.

        Returns:
            `True` if at least one embedded telemetry event was persisted.
        """
        saved_any = False
        if envelope.command_event is not None:
            await self.save_command_event(envelope.command_event)
            saved_any = True
        if envelope.network_event is not None:
            await self.save_network_event(envelope.network_event)
            saved_any = True
        return saved_any

    async def get_session_commands(
        self, session_id: str
    ) -> List[AttackerCommandEvent]:
        """
        Retrieve all shell commands executed during a trapped `session_id`
        ordered chronologically by `timestamp`.

        Args:
            session_id: Session identifier of the trapped attacker.

        Returns:
            Chronological list of `AttackerCommandEvent` records.
        """
        cleaned_id = session_id.strip()
        if not cleaned_id:
            return []

        results: Dict[str, AttackerCommandEvent] = {}

        if self._session_factory is not None and select is not None:
            try:
                async with self._session_factory() as db:
                    stmt = (
                        select(AttackerCommandLogORM)
                        .where(AttackerCommandLogORM.session_id == cleaned_id)
                        .order_by(AttackerCommandLogORM.timestamp.asc())
                    )
                    rows = (await db.execute(stmt)).scalars().all()
                    for row in rows:
                        evt = self._orm_to_command(row)
                        results[evt.event_id] = evt
            except Exception as exc:
                logger.warning(
                    "PostgreSQL get_session_commands fallback to memory (%s).", exc
                )

        async with self._lock:
            for evt in self._mem_commands.values():
                if evt.session_id == cleaned_id and evt.event_id not in results:
                    results[evt.event_id] = evt

        return sorted(results.values(), key=lambda e: e.timestamp)

    async def get_session_network_events(
        self, session_id: str
    ) -> List[NetworkTelemetryEvent]:
        """
        Retrieve all network and eBPF telemetry events captured for `session_id`
        ordered chronologically by `timestamp`.

        Args:
            session_id: Session identifier of the trapped attacker.

        Returns:
            Chronological list of `NetworkTelemetryEvent` records.
        """
        cleaned_id = session_id.strip()
        if not cleaned_id:
            return []

        results: Dict[str, NetworkTelemetryEvent] = {}

        if self._session_factory is not None and select is not None:
            try:
                async with self._session_factory() as db:
                    stmt = (
                        select(NetworkTelemetryLogORM)
                        .where(NetworkTelemetryLogORM.session_id == cleaned_id)
                        .order_by(NetworkTelemetryLogORM.timestamp.asc())
                    )
                    rows = (await db.execute(stmt)).scalars().all()
                    for row in rows:
                        evt = self._orm_to_network(row)
                        results[evt.event_id] = evt
            except Exception as exc:
                logger.warning(
                    "PostgreSQL get_session_network_events fallback to memory (%s).",
                    exc,
                )

        async with self._lock:
            for evt in self._mem_network.values():
                if evt.session_id == cleaned_id and evt.event_id not in results:
                    results[evt.event_id] = evt

        return sorted(results.values(), key=lambda e: e.timestamp)

    async def get_alerts_history(
        self,
        limit: int = 100,
        attacker_ip: Optional[str] = None,
    ) -> List[SecurityAlertContract]:
        """
        Query historical security alerts ordered from newest to oldest, optionally
        filtered by `attacker_ip` (`source_ip`).

        Args:
            limit: Maximum number of records to return (default 100).
            attacker_ip: Optional source IPv4/IPv6 filter.

        Returns:
            List of `SecurityAlertContract` records ordered by `timestamp` descending.
        """
        effective_limit = max(1, limit)
        cleaned_ip = attacker_ip.strip() if attacker_ip else None
        results: Dict[str, SecurityAlertContract] = {}

        if self._session_factory is not None and select is not None and desc is not None:
            try:
                async with self._session_factory() as db:
                    stmt = select(SecurityAlertLogORM)
                    if cleaned_ip:
                        stmt = stmt.where(SecurityAlertLogORM.source_ip == cleaned_ip)
                    stmt = stmt.order_by(desc(SecurityAlertLogORM.timestamp)).limit(
                        effective_limit
                    )
                    rows = (await db.execute(stmt)).scalars().all()
                    for row in rows:
                        alert = self._orm_to_alert(row)
                        results[alert.alert_id] = alert
            except Exception as exc:
                logger.warning(
                    "PostgreSQL get_alerts_history fallback to memory (%s).", exc
                )

        async with self._lock:
            for alert in self._mem_alerts.values():
                if cleaned_ip and alert.source_ip != cleaned_ip:
                    continue
                if alert.alert_id not in results:
                    results[alert.alert_id] = alert

        sorted_alerts = sorted(
            results.values(),
            key=lambda a: a.timestamp,
            reverse=True,
        )
        return sorted_alerts[:effective_limit]

    async def get_attack_timeline_metrics(self) -> Dict[str, Any]:
        """
        Compute aggregated attack metrics across alerts, sandbox commands, and
        network telemetry for the Defender SOC Dashboard.

        Returns:
            Dictionary containing severity breakdowns, attack categories, unique attacker
            IP counts, total commands/packets captured, and timeline distributions.
        """
        alerts = await self.get_alerts_history(limit=1000)

        commands_map: Dict[str, AttackerCommandEvent] = {}
        network_map: Dict[str, NetworkTelemetryEvent] = {}

        if self._session_factory is not None and select is not None and desc is not None:
            try:
                async with self._session_factory() as db:
                    cmd_rows = (
                        (
                            await db.execute(
                                select(AttackerCommandLogORM)
                                .order_by(desc(AttackerCommandLogORM.timestamp))
                                .limit(1000)
                            )
                        )
                        .scalars()
                        .all()
                    )
                    for r in cmd_rows:
                        commands_map[r.event_id] = self._orm_to_command(r)

                    net_rows = (
                        (
                            await db.execute(
                                select(NetworkTelemetryLogORM)
                                .order_by(desc(NetworkTelemetryLogORM.timestamp))
                                .limit(1000)
                            )
                        )
                        .scalars()
                        .all()
                    )
                    for r in net_rows:
                        network_map[r.event_id] = self._orm_to_network(r)
            except Exception as exc:
                logger.warning(
                    "PostgreSQL get_attack_timeline_metrics fallback to memory (%s).",
                    exc,
                )

        async with self._lock:
            for eid, cmd in self._mem_commands.items():
                commands_map.setdefault(eid, cmd)
            for eid, net in self._mem_network.items():
                network_map.setdefault(eid, net)

        severity_counts: Counter[str] = Counter(a.severity.value for a in alerts)
        category_counts: Counter[str] = Counter(a.category.value for a in alerts)
        attacker_ips: Counter[str] = Counter(a.source_ip for a in alerts)
        protocol_counts: Counter[str] = Counter(
            n.protocol for n in network_map.values()
        )
        unique_sessions = {a.session_id for a in alerts} | {
            c.session_id for c in commands_map.values()
        } | {n.session_id for n in network_map.values()}

        total_bytes_captured = sum(
            n.packet_length_bytes for n in network_map.values()
        )

        return {
            "total_alerts": len(alerts),
            "total_commands_captured": len(commands_map),
            "total_network_events_captured": len(network_map),
            "total_packet_bytes_captured": total_bytes_captured,
            "unique_trapped_sessions": len(unique_sessions),
            "unique_attacker_ips": len(attacker_ips),
            "top_attacker_ips": dict(attacker_ips.most_common(10)),
            "alerts_by_severity": {
                sev.value: severity_counts.get(sev.value, 0)
                for sev in AlertSeverityEnum
            },
            "alerts_by_category": {
                cat.value: category_counts.get(cat.value, 0)
                for cat in AttackCategoryEnum
            },
            "network_protocols_breakdown": dict(protocol_counts),
        }
