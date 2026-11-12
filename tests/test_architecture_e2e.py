"""
End-to-End Integration and Security Test Suite for the 4-Layer
FastAPI-Driven Deception Architecture (`tests/test_architecture_e2e.py`).
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from core_web_app.main import app as core_app
from deception_gateway.main import app as gateway_app
from forensic_extraction_engine.engine_service import (
    app as forensic_app,
    forensic_engine_service,
)
from isolation_sandbox.isolated_honey_containers.decoy_service_app import (
    decoy_service_instance,
)
from soc_dashboard.dashboard_server import app as soc_app


def test_layer1_and_layer2_legitimate_flow_and_honey_token_injection() -> None:
    """
    Verify that legitimate client requests are routed to `core_web_app` and
    enriched with cryptographic Honey Tokens (`X-Internal-Debug-Token`, `_debug_links`).
    """
    with TestClient(gateway_app) as client:
        resp = client.get(
            "/api/v1/records",
            headers={"X-Session-ID": "legit_session_0001"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["service_tier"] == "production_core_web_app"
        assert data["total_count"] >= 3
        assert "_debug_links" in data
        assert "X-Internal-Debug-Token" in resp.headers
        assert resp.headers.get("X-Deception-Upstream-Target") == "CORE_WEB_APP"


def test_core_authentication_login_and_jwt_verification() -> None:
    """
    Verify PBKDF2-HMAC-SHA256 authentication and RFC-7519 HS256 JWT token verification.
    """
    with TestClient(core_app) as client:
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"username": "sec_admin", "password": "EnterpriseAdmin#2026!"},
        )
        assert login_resp.status_code == 200
        token_data = login_resp.json()
        jwt_token = token_data["access_token"]
        assert token_data["user"]["role"] == "admin"

        me_resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["username"] == "sec_admin"


def test_honey_token_trigger_diverts_session_to_sandbox() -> None:
    """
    Verify that accessing a decoy honey token endpoint transparently diverts
    the attacker session into `PREWARMED_SANDBOX` and pins subsequent requests.
    """
    attacker_sid = "attacker_session_9901"
    with TestClient(gateway_app) as client:
        # 1. Trigger decoy endpoint
        trap_resp = client.get(
            "/api/v1/internal/vault-keys",
            headers={"X-Session-ID": attacker_sid},
        )
        assert trap_resp.status_code == 200
        assert trap_resp.headers.get("X-Deception-Upstream-Target") == "PREWARMED_SANDBOX"
        assert "X-Enterprise-Server-Node" in trap_resp.headers

        # 2. Subsequent request to normal path remains pinned to sandbox
        pinned_resp = client.get(
            "/api/v1/records",
            headers={"X-Session-ID": attacker_sid},
        )
        assert pinned_resp.status_code == 200
        assert pinned_resp.headers.get("X-Deception-Upstream-Target") == "PREWARMED_SANDBOX"


def test_layer3_and_layer4_forensics_custody_and_soc_dashboard() -> None:
    """
    Verify sandbox command capture, deobfuscation, MITRE ATT&CK mapping,
    on-disk artifact writing, HMAC-SHA256 Chain-of-Custody verification,
    and SOC Dashboard incident report export.
    """
    with tempfile.TemporaryDirectory() as tmp_vault:
        os.environ["FORENSICS_VAULT_PATH"] = tmp_vault
        forensic_engine_service.attach_sandbox_telemetry_hook()

        trapped_sid = "forensic_session_77889900"

        # Execute simulated attacker command in decoy sandbox via TestClient / async call
        import asyncio

        status_code, payload, _headers = asyncio.run(
            decoy_service_instance.handle_trapped_request(
                session_id=trapped_sid,
                client_ip="198.51.100.77",
                request_method="GET",
                request_path="/api/v1/internal/debug-console",
                query_params={"cmd": "whoami && cat /etc/passwd"},
            )
        )
        assert status_code == 200
        assert "root:x:0:0" in payload["stdout"]

        with TestClient(soc_app) as soc_client:
            # 1. Check SOC Dashboard UI & Health
            ui_resp = soc_client.get("/")
            assert ui_resp.status_code == 200
            assert "SOC" in ui_resp.text

            health_resp = soc_client.get("/health")
            assert health_resp.status_code == 200

            # 2. Generate Incident Report & Verify On-Disk Artifacts
            gen_resp = soc_client.post(f"/api/v1/soc/reports/generate/{trapped_sid}")
            assert gen_resp.status_code == 200
            rep_data = gen_resp.json()["incident_report"]
            assert rep_data["total_commands_captured"] >= 1
            assert len(rep_data["artifacts_list"]) >= 3

            short_sid = trapped_sid[:8]
            vault_subdir = Path(tmp_vault) / short_sid
            assert (vault_subdir / f"session_{short_sid}_capture.pcap").exists()
            assert (vault_subdir / f"session_{short_sid}_ebpf_trace.log").exists()
            assert (vault_subdir / f"session_{short_sid}_commands.jsonl").exists()

            # 3. Verify Tamper-Evident Chain of Custody
            custody_resp = soc_client.get(
                f"/api/v1/soc/reports/session/{trapped_sid}/verify-custody"
            )
            assert custody_resp.status_code == 200
            custody_json = custody_resp.json()
            assert custody_json["overall_integrity_verified"] is True
            assert custody_json["hmac_chain_verification"]["chain_valid"] is True

            # 4. Verify Signed Bundle Export
            export_resp = soc_client.get(
                f"/api/v1/soc/reports/session/{trapped_sid}/export"
            )
            assert export_resp.status_code == 200
            assert export_resp.json()["cryptographic_proof"]["chain_of_custody_valid"] is True

        # 5. Verify Forensic Extraction Engine FastAPI microservice endpoints directly
        with TestClient(forensic_app) as f_client:
            fh_resp = f_client.get("/forensics/health")
            assert fh_resp.status_code == 200
            assert fh_resp.json()["sandbox_hook_attached"] is True

            tl_resp = f_client.get(f"/forensics/sessions/{trapped_sid}/timeline")
            assert tl_resp.status_code == 200
            assert tl_resp.json()["total_timeline_events"] >= 2


def test_tcp_l4_nmap_scan_detection_and_realtime_soc_websocket() -> None:
    """
    Verify that raw TCP L4 port scans (`nmap -sS` / `nmap -sT` / `nmap -sV`) are
    captured by `attack_detector.inspect_tcp_l4_scan`, logged as MITRE ATT&CK `T1046`
    in the Forensic Extraction Engine, and streamed via the SOC WebSocket endpoint.
    """
    import asyncio
    from deception_gateway.main import attack_detector

    alert = asyncio.run(
        attack_detector.inspect_tcp_l4_scan(
            client_ip="10.0.2.15",
            client_port=54321,
            destination_port=8000,
            raw_probe_bytes=b"",
            scan_type="TCP_L4_PORT_SCAN",
        )
    )
    assert alert is not None
    assert alert.category.value == "AUTOMATED_SCANNER_PROBE"
    assert alert.source_ip == "10.0.2.15"

    with TestClient(soc_app) as soc_client:
        ui_resp = soc_client.get("/")
        assert "/api/v1/soc/visualizations/alerts/ws" in ui_resp.text

        live_resp = soc_client.get("/api/v1/soc/visualizations/alerts/live?limit=10")
        assert live_resp.status_code == 200
        alerts_list = live_resp.json()["alerts"]
        assert any(a["alert_id"] == alert.alert_id for a in alerts_list)

        mitre_resp = soc_client.get("/api/v1/soc/visualizations/mitre-matrix")
        assert mitre_resp.status_code == 200
        technique_ids = [
            t["technique_id"] for t in mitre_resp.json()["techniques_matrix"]
        ]
        assert "T1046" in technique_ids


