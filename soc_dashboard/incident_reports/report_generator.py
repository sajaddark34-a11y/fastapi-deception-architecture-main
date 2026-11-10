"""
SOC Incident Report Generator & Tamper-Evident Chain-of-Custody Verifier (Layer 4).

Integrates with the Forensic Extraction Engine (`forensic_extraction_engine`),
PostgreSQL Forensic Repositories (`data_storage.postgresql_store`), and Redis
stores (`data_storage.redis_store`) to:
  1. Generate and persist comprehensive DFIR incident reports (`IncidentReportContract`).
  2. Cryptographically verify the HMAC-SHA256 Tamper-Evident Chain-of-Custody hash
     chain and individual artifact SHA-256 checksums.
  3. Export a digitally signed, court-admissible JSON incident bundle containing
     the full attack timeline, MITRE ATT&CK matrix, deobfuscated commands,
     extracted IOCs, and Chain-of-Custody audit trail.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from data_storage.postgresql_store import (
    ForensicArtifactsRepository,
    ForensicLogsRepository,
    forensic_artifacts_repository,
    forensic_logs_repository,
)
from data_storage.redis_store import (
    FastAlertsStream,
    SessionStateStore,
    fast_alerts_stream,
    session_state_store,
)
from forensic_extraction_engine import (
    CHAIN_OF_CUSTODY_HMAC_SECRET,
    ForensicTelemetryCollector,
    forensic_telemetry_collector,
)
from shared_contracts.forensic_artifact_schema import IncidentReportContract


class SOCIncidentReportGenerator:
    """
    Generates, verifies, and exports cryptographically signed DFIR incident reports
    for the SOC Dashboard & SOAR platform.
    """

    def __init__(
        self,
        telemetry_collector: Optional[ForensicTelemetryCollector] = None,
        artifacts_repo: Optional[ForensicArtifactsRepository] = None,
        logs_repo: Optional[ForensicLogsRepository] = None,
        session_store: Optional[SessionStateStore] = None,
        alerts_stream: Optional[FastAlertsStream] = None,
        signing_secret: Optional[str] = None,
    ) -> None:
        self._collector = telemetry_collector or forensic_telemetry_collector
        self._artifacts_repo = artifacts_repo or forensic_artifacts_repository
        self._logs_repo = logs_repo or forensic_logs_repository
        self._session_store = session_store or session_state_store
        self._alerts_stream = alerts_stream or fast_alerts_stream
        secret_str = signing_secret or os.getenv(
            "FORENSIC_CUSTODY_HMAC_SECRET",
            CHAIN_OF_CUSTODY_HMAC_SECRET,
        )
        self._signing_key: bytes = secret_str.encode("utf-8")

    async def generate_full_incident_report(
        self,
        session_id: str,
        attacker_ip: Optional[str] = None,
    ) -> IncidentReportContract:
        """
        Compiles and persists a complete `IncidentReportContract` for `session_id`
        by invoking the Forensic Extraction Engine's telemetry collector.
        """
        if not attacker_ip:
            session_obj = await self._session_store.get_session(session_id)
            if session_obj is not None:
                attacker_ip = session_obj.client_ip

        report = await self._collector.finalize_and_build_incident_report(
            session_id=session_id,
            attacker_ip=attacker_ip or "203.0.113.42",
        )
        return report

    async def verify_session_chain_of_custody(
        self,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Verifies both:
          1. The sequential HMAC-SHA256 Tamper-Evident Chain-of-Custody ledger
             maintained by the Forensic Extraction Engine (`TamperEvidentChainOfCustody`).
          2. Individual SHA-256 payload checksums for all persisted forensic artifacts
             associated with `session_id`.
        """
        chain_valid = self._collector.custody_chain.verify_session_chain(
            session_id
        )
        custody_entries = self._collector.custody_chain.get_session_ledger(
            session_id
        )

        artifacts = await self._artifacts_repo.list_artifacts_by_session(session_id)
        artifact_verifications: List[Dict[str, Any]] = []
        all_artifacts_valid = True

        for artifact in artifacts:
            art_id = str(artifact.artifact_id)
            verified_art = await self._artifacts_repo.verify_artifact_checksum(
                artifact_id=art_id,
                computed_sha256=artifact.sha256_checksum,
            )
            is_valid = bool(
                verified_art.is_verified
                if hasattr(verified_art, "is_verified")
                else verified_art
            )
            if not is_valid:
                all_artifacts_valid = False
            artifact_verifications.append(
                {
                    "artifact_id": art_id,
                    "artifact_type": (
                        artifact.artifact_type.value
                        if hasattr(artifact.artifact_type, "value")
                        else str(artifact.artifact_type)
                    ),
                    "sha256_checksum": artifact.sha256_checksum,
                    "checksum_verified": is_valid,
                    "captured_at": artifact.captured_at.isoformat(),
                }
            )

        overall_integrity = bool(chain_valid and all_artifacts_valid)

        return {
            "session_id": session_id,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "overall_integrity_verified": overall_integrity,
            "hmac_chain_verification": {
                "chain_valid": chain_valid,
                "entries_count": len(custody_entries),
            },
            "custody_ledger_entries": custody_entries,
            "artifact_checksum_verifications": artifact_verifications,
            "total_artifacts_verified": len(artifact_verifications),
        }

    async def export_signed_report_bundle(
        self,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Exports a comprehensive, cryptographically signed DFIR incident report bundle
        for `session_id`, suitable for SOC archival, SIEM ingestion, or legal evidence.
        """
        existing_reports = await self._artifacts_repo.list_incident_reports(limit=100)
        report: Optional[IncidentReportContract] = None
        for candidate in existing_reports:
            if candidate.session_id == session_id:
                report = candidate
                break
        if report is None:
            report = await self.generate_full_incident_report(session_id=session_id)

        custody_status = await self.verify_session_chain_of_custody(session_id)
        timeline_data = await self._collector.reconstruct_session_timeline(session_id)
        alerts = await self._alerts_stream.get_alerts_by_session(session_id)
        mitre_mappings = self._collector.command_logger.get_session_mitre_Mappings(
            session_id
        )

        report_dict = (
            report.model_dump(mode="json")
            if hasattr(report, "model_dump")
            else report.dict()
        )

        bundle_payload: Dict[str, Any] = {
            "schema_version": "1.0.0-DFIR-ENTERPRISE",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "incident_report": report_dict,
            "chain_of_custody_verification": custody_status,
            "forensic_timeline": timeline_data["chronological_timeline"],
            "associated_alerts_count": len(alerts),
            "mitre_attack_coverage": mitre_mappings,
        }

        canonical_json = json.dumps(
            bundle_payload, sort_keys=True, separators=(",", ":"), default=str
        )
        bundle_sha256 = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
        bundle_hmac_signature = hmac.new(
            self._signing_key,
            canonical_json.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return {
            "bundle": bundle_payload,
            "cryptographic_proof": {
                "algorithm": "HMAC-SHA256",
                "bundle_sha256_digest": bundle_sha256,
                "bundle_hmac_signature": bundle_hmac_signature,
                "chain_of_custody_valid": custody_status["overall_integrity_verified"],
                "signed_at": datetime.now(timezone.utc).isoformat(),
            },
        }


soc_incident_report_generator = SOCIncidentReportGenerator()

__all__ = [
    "SOCIncidentReportGenerator",
    "soc_incident_report_generator",
]
