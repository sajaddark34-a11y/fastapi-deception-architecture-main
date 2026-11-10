"""
SOC Incident Report & Chain-of-Custody API Routes (Layer 4).

Exposes REST endpoints for generating, querying, verifying, and exporting
cryptographically signed DFIR incident reports (`IncidentReportContract`)
and forensic artifacts (`ForensicArtifactContract`).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from fastapi import APIRouter, HTTPException, status
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_handler import HTTPException, status
    from core_web_app.authentication.auth_routes import APIRouter

from data_storage.postgresql_store import forensic_artifacts_repository
from soc_dashboard.incident_reports.report_generator import (
    soc_incident_report_generator,
)

report_export_router = APIRouter(
    prefix="/api/v1/soc/reports",
    tags=["SOC Incident Reports & Chain of Custody"],
)


@report_export_router.post("/generate/{session_id}")
async def generate_incident_report_endpoint(
    session_id: str,
    attacker_ip: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Triggers full DFIR incident report compilation (`IncidentReportContract`)
    for `session_id` and persists it to PostgreSQL.
    """
    report = await soc_incident_report_generator.generate_full_incident_report(
        session_id=session_id,
        attacker_ip=attacker_ip,
    )
    report_dict = (
        report.model_dump(mode="json")
        if hasattr(report, "model_dump")
        else report.dict()
    )
    return {
        "status": "generated",
        "session_id": session_id,
        "report_id": str(report.report_id),
        "incident_report": report_dict,
    }


@report_export_router.get("/")
async def list_incident_reports_endpoint(limit: int = 50) -> Dict[str, Any]:
    """
    Lists persisted DFIR incident reports ordered by creation time.
    """
    reports = await forensic_artifacts_repository.list_incident_reports(limit=limit)
    serialized = [
        r.model_dump(mode="json") if hasattr(r, "model_dump") else r.dict()
        for r in reports
    ]
    return {
        "count": len(serialized),
        "reports": serialized,
    }


@report_export_router.get("/{report_id}")
async def get_incident_report_by_id_endpoint(report_id: str) -> Dict[str, Any]:
    """
    Retrieves a single `IncidentReportContract` by its `report_id`.
    """
    report = await forensic_artifacts_repository.get_incident_report(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident report '{report_id}' not found.",
        )
    report_dict = (
        report.model_dump(mode="json")
        if hasattr(report, "model_dump")
        else report.dict()
    )
    return {
        "report_id": str(report.report_id),
        "incident_report": report_dict,
    }


@report_export_router.get("/session/{session_id}/verify-custody")
async def verify_session_custody_endpoint(session_id: str) -> Dict[str, Any]:
    """
    Cryptographically verifies the HMAC-SHA256 Tamper-Evident Chain-of-Custody
    ledger and SHA-256 artifact checksums for `session_id`.
    """
    return await soc_incident_report_generator.verify_session_chain_of_custody(
        session_id=session_id
    )


@report_export_router.get("/session/{session_id}/export")
async def export_signed_incident_bundle_endpoint(session_id: str) -> Dict[str, Any]:
    """
    Exports a court-admissible, HMAC-SHA256 digitally signed JSON incident bundle
    for `session_id`, including MITRE ATT&CK mappings, IOCs, and custody proofs.
    """
    return await soc_incident_report_generator.export_signed_report_bundle(
        session_id=session_id
    )


@report_export_router.get("/session/{session_id}/artifacts")
async def list_session_forensic_artifacts_endpoint(session_id: str) -> Dict[str, Any]:
    """
    Lists all raw forensic artifacts (`ForensicArtifactContract`) captured for `session_id`.
    """
    artifacts = await forensic_artifacts_repository.list_artifacts_by_session(
        session_id
    )
    serialized = [
        a.model_dump(mode="json") if hasattr(a, "model_dump") else a.dict()
        for a in artifacts
    ]
    return {
        "session_id": session_id,
        "count": len(serialized),
        "artifacts": serialized,
    }


__all__ = [
    "report_export_router",
    "generate_incident_report_endpoint",
    "list_incident_reports_endpoint",
    "get_incident_report_by_id_endpoint",
    "verify_session_custody_endpoint",
    "export_signed_incident_bundle_endpoint",
    "list_session_forensic_artifacts_endpoint",
]
