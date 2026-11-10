"""
Forensic Extraction Engine Service (`forensic_extraction_engine.engine_service`).

Provides the Layer 3 automated DFIR microservice (`app`) and hooks directly into
`isolation_sandbox.decoy_service_instance` so every command, file probe, and
network packet inside the isolation sandbox is automatically captured, deobfuscated,
mapped to MITRE ATT&CK, signed in the Chain-of-Custody, and stored in PostgreSQL
and Redis.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Optional

try:
    from fastapi import APIRouter, FastAPI, status
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_handler import status  # type: ignore[attr-defined]
    from core_web_app.authentication.auth_routes import APIRouter  # type: ignore[attr-defined]
    from core_web_app.main import FastAPI  # type: ignore[attr-defined]

from data_storage.postgresql_store import init_forensic_database
from forensic_extraction_engine.telemetry_collector import (
    ForensicTelemetryCollector,
    forensic_telemetry_collector,
)
from isolation_sandbox.isolated_honey_containers.decoy_service_app import (
    DecoyServiceApp,
    decoy_service_instance,
)
from isolation_sandbox.prewarmed_dynamic_sandbox import (
    prewarmed_pool_controller,
)
from shared_contracts.forensic_artifact_schema import IncidentReportContract

logger = logging.getLogger(__name__)


class ForensicExtractionEngineService:
    """
    High-level service managing real-time telemetry ingestion hooks between
    `isolation_sandbox` and `ForensicTelemetryCollector`.
    """

    def __init__(
        self,
        collector: Optional[ForensicTelemetryCollector] = None,
        decoy_app: Optional[DecoyServiceApp] = None,
    ) -> None:
        self.collector: ForensicTelemetryCollector = (
            collector or forensic_telemetry_collector
        )
        self.decoy_app: DecoyServiceApp = decoy_app or decoy_service_instance
        self._hook_attached: bool = False
        self.attach_sandbox_telemetry_hook()

    def attach_sandbox_telemetry_hook(self) -> None:
        """
        Bind `collector.ingest_sandbox_interaction` to `decoy_service_instance`
        so every sandbox interaction triggers automated forensic extraction.
        """
        if not self._hook_attached:
            self.decoy_app.register_telemetry_hook(
                self.collector.ingest_sandbox_interaction
            )
            self._hook_attached = True

    async def process_sandbox_interaction(
        self, interaction_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Directly process a sandbox interaction event through the forensic collector."""
        return await self.collector.ingest_sandbox_interaction(interaction_payload)

    async def finalize_session_forensics(
        self,
        session_id: str,
        attacker_ip: Optional[str] = None,
        container_id: Optional[str] = None,
    ) -> IncidentReportContract:
        """
        Export all session artifacts, seal the HMAC-SHA256 Chain of Custody, and
        persist the final `IncidentReportContract`.
        """
        return await self.collector.finalize_and_build_incident_report(
            session_id=session_id,
            attacker_ip=attacker_ip,
            container_id=container_id,
        )

    async def get_session_forensic_timeline(
        self, session_id: str
    ) -> Dict[str, Any]:
        """Retrieve the full reconstructed forensic timeline and MITRE matrix for `session_id`."""
        return await self.collector.reconstruct_session_timeline(session_id)


forensic_engine_service = ForensicExtractionEngineService()


@asynccontextmanager
async def forensic_engine_lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize PostgreSQL forensic tables, prewarmed sandbox pool, and telemetry hooks."""
    await init_forensic_database()
    await prewarmed_pool_controller.initialize_warm_pool()
    forensic_engine_service.attach_sandbox_telemetry_hook()
    logger.info("Forensic Extraction Engine (Layer 3) initialized and attached.")
    yield


app = FastAPI(
    title="Forensic Extraction Engine Service (Layer 3)",
    description=(
        "Automated DFIR pipeline capturing attacker commands, PCAP flows, and eBPF "
        "syscalls from isolated honey containers with MITRE ATT&CK mapping and "
        "HMAC-SHA256 Chain-of-Custody verification."
    ),
    version="1.0.0",
    lifespan=forensic_engine_lifespan,
)


forensics_router = APIRouter(tags=["Forensic Extraction Engine"])


@forensics_router.get(
    "/forensics/health",
    status_code=status.HTTP_200_OK,
    summary="Health check for Forensic Extraction Engine",
)
async def forensics_health_check() -> Dict[str, Any]:
    """Return operational readiness of the Forensic Extraction Engine."""
    pool_metrics = await prewarmed_pool_controller.get_pool_metrics()
    return {
        "status": "healthy",
        "service": os.getenv("SERVICE_NAME", "forensic_extraction_engine"),
        "sandbox_hook_attached": forensic_engine_service._hook_attached,
        "prewarmed_pool": pool_metrics,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@forensics_router.get(
    "/forensics/sessions/{session_id}/timeline",
    status_code=status.HTTP_200_OK,
    summary="Reconstruct full chronological forensic timeline for a trapped session",
)
async def get_session_timeline_endpoint(session_id: str) -> Dict[str, Any]:
    """Return chronological timeline, MITRE ATT&CK matrix, and chain of custody for `session_id`."""
    return await forensic_engine_service.get_session_forensic_timeline(session_id)


@forensics_router.post(
    "/forensics/sessions/{session_id}/finalize-report",
    status_code=status.HTTP_201_CREATED,
    summary="Finalize session artifacts and generate signed SOC Incident Report",
)
async def finalize_incident_report_endpoint(session_id: str) -> Dict[str, Any]:
    """Generate and persist a verified `IncidentReportContract` for `session_id`."""
    report = await forensic_engine_service.finalize_session_forensics(
        session_id=session_id
    )
    return report.model_dump(mode="json")


app.include_router(forensics_router)
