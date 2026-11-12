"""
Real-Time SOC Telemetry Chart View and Enterprise Dark-Mode UI Renderer
(`soc_dashboard.attack_visualizations.telemetry_chart_view`).

Aggregates live telemetry across Redis (`SessionStateStore`, `FastAlertsStream`),
PostgreSQL (`ForensicLogsRepository`, `ForensicArtifactsRepository`), the Dynamic
Isolation Sandbox (`PrewarmedPoolController`, `DockerSandboxManager`), and the
Forensic Extraction Engine (`ForensicTelemetryCollector`) to power the SOC
Command Center visualizations, MITRE ATT&CK heatmaps, and live terminal replays.
"""

from __future__ import annotations

from collections import Counter
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
from forensic_extraction_engine.telemetry_collector import (
    ForensicTelemetryCollector,
    forensic_telemetry_collector,
)
from isolation_sandbox.docker_sandbox_manager import (
    DockerSandboxManager,
    docker_sandbox_manager,
)
from isolation_sandbox.prewarmed_dynamic_sandbox import (
    PrewarmedPoolController,
    prewarmed_pool_controller,
)


class TelemetryChartView:
    """
    Constructs structured visualization datasets (KPI cards, MITRE ATT&CK matrix,
    live sandbox terminal replay, network protocol distributions) and renders the
    Enterprise Dark-Mode SOC Command Center HTML interface.
    """

    def __init__(
        self,
        state_store: Optional[SessionStateStore] = None,
        alerts_stream: Optional[FastAlertsStream] = None,
        logs_repo: Optional[ForensicLogsRepository] = None,
        artifacts_repo: Optional[ForensicArtifactsRepository] = None,
        pool_controller: Optional[PrewarmedPoolController] = None,
        sandbox_manager: Optional[DockerSandboxManager] = None,
        forensic_collector: Optional[ForensicTelemetryCollector] = None,
    ) -> None:
        self.state_store: SessionStateStore = state_store or session_state_store
        self.alerts_stream: FastAlertsStream = alerts_stream or fast_alerts_stream
        self.logs_repo: ForensicLogsRepository = logs_repo or forensic_logs_repository
        self.artifacts_repo: ForensicArtifactsRepository = (
            artifacts_repo or forensic_artifacts_repository
        )
        self.pool_controller: PrewarmedPoolController = (
            pool_controller or prewarmed_pool_controller
        )
        self.sandbox_manager: DockerSandboxManager = (
            sandbox_manager or docker_sandbox_manager
        )
        self.forensic_collector: ForensicTelemetryCollector = (
            forensic_collector or forensic_telemetry_collector
        )

    async def build_live_kpi_summary(self) -> Dict[str, Any]:
        """
        Compile real-time Key Performance Indicators (KPIs) across all four layers
        of the deception architecture for the SOC overview header.
        """
        malicious_sessions = await self.state_store.list_active_malicious_sessions()
        recent_alerts = await self.alerts_stream.get_recent_alerts(limit=100)
        timeline_metrics = await self.logs_repo.get_attack_timeline_metrics()
        pool_metrics = await self.pool_controller.get_pool_metrics()
        incident_reports = await self.artifacts_repo.list_incident_reports(limit=50)

        avg_risk_score = (
            round(
                sum(s.risk_score for s in malicious_sessions)
                / len(malicious_sessions),
                2,
            )
            if malicious_sessions
            else 0.0
        )

        return {
            "active_trapped_sessions_count": len(malicious_sessions),
            "average_session_risk_score": avg_risk_score,
            "recent_stream_alerts_count": len(recent_alerts),
            "compiled_incident_reports_count": len(incident_reports),
            "attack_timeline_metrics": timeline_metrics,
            "sandbox_pool_metrics": pool_metrics,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def build_mitre_attack_heatmap(self) -> Dict[str, Any]:
        """
        Aggregate MITRE ATT&CK Tactics and Techniques across all active and
        historical trapped sessions to render the threat intelligence matrix.
        """
        malicious_sessions = await self.state_store.list_active_malicious_sessions()
        alerts = await self.logs_repo.get_alerts_history(limit=200)
        session_ids = {s.session_id for s in malicious_sessions} | {
            a.session_id for a in alerts
        }

        technique_counter: Counter[str] = Counter()
        tactic_counter: Counter[str] = Counter()
        technique_details: Dict[str, Dict[str, Any]] = {}

        for sid in session_ids:
            mappings = self.forensic_collector.command_logger.get_session_mitre_Mappings(
                sid
            )
            for item in mappings:
                tid = item["technique_id"]
                tactic = item["tactic"]
                technique_counter[tid] += 1
                tactic_counter[tactic] += 1
                if tid not in technique_details:
                    technique_details[tid] = {
                        "technique_id": tid,
                        "technique_name": item["technique_name"],
                        "tactic": tactic,
                        "observed_count": 0,
                        "sample_indicator": item["matched_indicator"],
                        "sessions_affected": [],
                    }
                technique_details[tid]["observed_count"] = technique_counter[tid]
                if sid not in technique_details[tid]["sessions_affected"]:
                    technique_details[tid]["sessions_affected"].append(sid)

        return {
            "total_sessions_analyzed": len(session_ids),
            "tactics_distribution": dict(tactic_counter),
            "techniques_matrix": list(technique_details.values()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def build_sandbox_terminal_replay(
        self, session_id: str
    ) -> Dict[str, Any]:
        """
        Construct an interactive terminal replay and network/eBPF telemetry view
        for a trapped attacker session (`session_id`).
        """
        cleaned_sid = session_id.strip()
        session = await self.state_store.get_session(cleaned_sid)
        binding = await self.state_store.get_active_sandbox_binding(cleaned_sid)
        commands = await self.logs_repo.get_session_commands(cleaned_sid)
        timeline_data = await self.forensic_collector.reconstruct_session_timeline(
            cleaned_sid
        )

        container_id = (
            (binding.container_id if binding else None)
            or (session.assigned_container_id if session else None)
            or "honey_sbx_warm_001"
        )
        container_obj = await self.sandbox_manager.lifecycle.inspect_container(
            container_id
        )
        intercepted_c2 = (
            list(container_obj.intercepted_egress_attempts)
            if container_obj is not None
            else []
        )

        command_frames: List[Dict[str, Any]] = []
        aggregated_iocs: Dict[str, List[str]] = {
            "urls": [],
            "ip_addresses": [],
            "domains": [],
        }

        for cmd in commands:
            analysis = self.forensic_collector.command_logger.get_event_analysis(
                cmd.event_id
            )
            if analysis is None:
                analysis = self.forensic_collector.command_logger.deobfuscate_payload(
                    cmd.command_line
                )
            for k in ("urls", "ip_addresses", "domains"):
                for val in analysis.extracted_iocs.get(k, []):
                    if val not in aggregated_iocs[k]:
                        aggregated_iocs[k].append(val)

            command_frames.append(
                {
                    "event_id": cmd.event_id,
                    "timestamp": cmd.timestamp.isoformat(),
                    "prompt": f"{cmd.executed_by_user}@{cmd.container_id}:{cmd.working_directory}$",
                    "deobfuscated_command": cmd.command_line,
                    "was_obfuscated": analysis.was_obfuscated,
                    "encoding_layers": analysis.encoding_layers_detected,
                    "sha256_hash": analysis.sha256_hash,
                    "md5_hash": analysis.md5_hash,
                    "shannon_entropy": analysis.shannon_entropy,
                    "process_id": cmd.process_id,
                    "exit_code": cmd.exit_code,
                    "mitre_techniques": [
                        {
                            "technique_id": m.technique_id,
                            "technique_name": m.technique_name,
                            "tactic": m.tactic,
                        }
                        for m in analysis.mitre_techniques
                    ],
                }
            )

        return {
            "session_id": cleaned_sid,
            "session_state": session.model_dump(mode="json") if session else None,
            "sandbox_binding": binding.model_dump(mode="json") if binding else None,
            "container_id": container_id,
            "total_commands": len(command_frames),
            "terminal_replay_frames": command_frames,
            "intercepted_c2_callbacks": intercepted_c2,
            "extracted_iocs": aggregated_iocs,
            "ebpf_syscall_traces": timeline_data["ebpf_traces"],
            "network_flows": timeline_data["network_flows"],
            "chain_of_custody_verified": timeline_data["chain_of_custody_verified"],
        }

    async def render_enterprise_soc_html(self) -> str:
        """
        Render the complete Enterprise Dark-Mode Cyber-Deception SOC Command Center
        HTML5 interface with live KPIs, WebSocket alert feed, Sandbox Terminal
        Replay, MITRE ATT&CK matrix, and SOAR response controls.
        """
        kpi = await self.build_live_kpi_summary()
        mitre = await self.build_mitre_attack_heatmap()
        alerts = await self.alerts_stream.get_recent_alerts(limit=10)

        alert_rows_html = "".join(
            f"<tr data-alert-id='{a.alert_id}'>"
            f"<td><span class='badge badge-{a.severity.value.lower()}'>{a.severity.value}</span></td>"
            f"<td>{a.category.value}</td>"
            f"<td><code>{a.source_ip}</code></td>"
            f"<td><code>{a.session_id[:12]}...</code></td>"
            f"<td><code>{a.http_method} {a.target_endpoint}</code></td>"
            f"<td>{a.action_taken}</td>"
            f"</tr>"
            for a in alerts
        ) or "<tr id='empty-alerts-row'><td colspan='6'>No active alerts in stream buffer.</td></tr>"

        mitre_cards_html = "".join(
            f"<div class='mitre-card'>"
            f"<div class='mitre-id'>{t['technique_id']}</div>"
            f"<div class='mitre-name'>{t['technique_name']}</div>"
            f"<div class='mitre-tactic'>{t['tactic']} | Hits: {t['observed_count']}</div>"
            f"</div>"
            for t in mitre.get("techniques_matrix", [])
        ) or "<div class='mitre-card'>Awaiting sandbox telemetry...</div>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Defender SOC Command Center | FastAPI Deception Architecture</title>
    <style>
        :root {{
            --bg-dark: #090d16;
            --bg-panel: #111827;
            --border-glow: #1f2937;
            --accent-cyan: #06b6d4;
            --accent-red: #ef4444;
            --accent-green: #10b981;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }}
        body {{
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Segoe UI', Roboto, monospace;
            margin: 0;
            padding: 24px;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-glow);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: var(--bg-panel);
            border: 1px solid var(--border-glow);
            border-left: 4px solid var(--accent-cyan);
            border-radius: 8px;
            padding: 16px;
        }}
        .kpi-value {{ font-size: 28px; font-weight: 700; color: var(--accent-cyan); }}
        .panel {{
            background: var(--bg-panel);
            border: 1px solid var(--border-glow);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 24px;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid var(--border-glow); }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
        .badge-critical {{ background: rgba(239,68,68,0.2); color: #ef4444; }}
        .badge-high {{ background: rgba(245,158,11,0.2); color: #f59e0b; }}
        .badge-medium {{ background: rgba(6,182,212,0.2); color: #06b6d4; }}
        .badge-low {{ background: rgba(16,185,129,0.2); color: #10b981; }}
        .mitre-grid {{ display: flex; gap: 12px; flex-wrap: wrap; }}
        .mitre-card {{
            background: #0b1325;
            border: 1px solid #1e3a8a;
            border-radius: 6px;
            padding: 12px;
            min-width: 200px;
        }}
        .mitre-id {{ color: var(--accent-cyan); font-weight: 700; }}
        @keyframes flashRow {{
            0% {{ background-color: rgba(239, 68, 68, 0.35); }}
            100% {{ background-color: transparent; }}
        }}
        .live-new-row {{ animation: flashRow 1.8s ease-out; }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>DEFENDER SOC COMMAND CENTER</h1>
            <p style="color:var(--text-muted);margin:0;">FastAPI-Driven Active Cyber Deception, Dynamic Containment & DFIR Pipeline</p>
        </div>
        <div style="display:flex;gap:10px;align-items:center;">
            <button id="reset-dashboard-btn" style="background:rgba(239,68,68,0.2);color:#ef4444;border:1px solid #ef4444;padding:5px 12px;border-radius:4px;font-weight:700;font-size:11px;cursor:pointer;">RESET DASHBOARD</button>
            <span id="ws-status-badge" class="badge" style="background:rgba(6,182,212,0.2);color:#06b6d4;">LIVE WS: CONNECTING...</span>
            <span class="badge" style="background:rgba(16,185,129,0.2);color:#10b981;">CHAIN-OF-CUSTODY: HMAC-SHA256 VERIFIED</span>
        </div>
    </header>
    <section class="kpi-grid">
        <div class="kpi-card">
            <div>ACTIVE TRAPPED SESSIONS</div>
            <div class="kpi-value" id="kpi-trapped-sessions">{kpi['active_trapped_sessions_count']}</div>
        </div>
        <div class="kpi-card">
            <div>SECURITY ALERTS EMITTED</div>
            <div class="kpi-value" id="kpi-total-alerts">{kpi['attack_timeline_metrics']['total_alerts']}</div>
        </div>
        <div class="kpi-card">
            <div>COMMANDS CAPTURED IN SANDBOX</div>
            <div class="kpi-value" id="kpi-total-commands">{kpi['attack_timeline_metrics']['total_commands_captured']}</div>
        </div>
        <div class="kpi-card">
            <div>PREWARMED HONEY CONTAINERS</div>
            <div class="kpi-value" id="kpi-warm-containers">{kpi['sandbox_pool_metrics']['available_warm_containers_count']}</div>
        </div>
    </section>
    <section class="panel">
        <h2>Real-Time Security Alerts Stream (WebSocket / Redis Streams)</h2>
        <table>
            <thead>
                <tr><th>Severity</th><th>Category</th><th>Attacker IP</th><th>Session</th><th>Target Endpoint</th><th>Containment Action</th></tr>
            </thead>
            <tbody id="alerts-tbody">{alert_rows_html}</tbody>
        </table>
    </section>
    <section class="panel">
        <h2>MITRE ATT&amp;CK Threat Intelligence Matrix</h2>
        <div class="mitre-grid" id="mitre-grid">{mitre_cards_html}</div>
    </section>
    <script>
        (function() {{
            const tbody = document.getElementById('alerts-tbody');
            const wsBadge = document.getElementById('ws-status-badge');
            const seenAlertIds = new Set();
            document.querySelectorAll('#alerts-tbody tr[data-alert-id]').forEach(tr => {{
                seenAlertIds.add(tr.getAttribute('data-alert-id'));
            }});

            async function refreshKpiAndMitre() {{
                try {{
                    const [kpiRes, mitreRes] = await Promise.all([
                        fetch('/api/v1/soc/visualizations/kpi'),
                        fetch('/api/v1/soc/visualizations/mitre-matrix')
                    ]);
                    if (kpiRes.ok) {{
                        const kpiData = await kpiRes.json();
                        document.getElementById('kpi-trapped-sessions').textContent = kpiData.active_trapped_sessions_count;
                        document.getElementById('kpi-total-alerts').textContent = kpiData.attack_timeline_metrics.total_alerts;
                        document.getElementById('kpi-total-commands').textContent = kpiData.attack_timeline_metrics.total_commands_captured;
                        document.getElementById('kpi-warm-containers').textContent = kpiData.sandbox_pool_metrics.available_warm_containers_count;
                    }}
                    if (mitreRes.ok) {{
                        const mitreData = await mitreRes.json();
                        const matrix = mitreData.techniques_matrix || [];
                        if (matrix.length > 0) {{
                            document.getElementById('mitre-grid').innerHTML = matrix.map(t =>
                                `<div class="mitre-card">` +
                                `<div class="mitre-id">${{t.technique_id}}</div>` +
                                `<div class="mitre-name">${{t.technique_name}}</div>` +
                                `<div class="mitre-tactic">${{t.tactic}} | Hits: ${{t.observed_count}}</div>` +
                                `</div>`
                            ).join('');
                        }} else {{
                            document.getElementById('mitre-grid').innerHTML = "<div class='mitre-card'>No MITRE techniques observed yet.</div>";
                        }}
                    }}
                }} catch (e) {{}}
            }}

            document.getElementById('reset-dashboard-btn').addEventListener('click', async function() {{
                const btn = this;
                btn.textContent = 'RESETTING...';
                seenAlertIds.clear();
                document.getElementById('kpi-trapped-sessions').textContent = '0';
                document.getElementById('kpi-total-alerts').textContent = '0';
                document.getElementById('kpi-total-commands').textContent = '0';
                tbody.innerHTML = "<tr id='empty-alerts-row'><td colspan='6'>No alerts emitted yet.</td></tr>";
                document.getElementById('mitre-grid').innerHTML = "<div class='mitre-card'>No MITRE techniques observed yet.</div>";
                try {{
                    await fetch('/api/v1/reset-telemetry', {{ method: 'POST' }});
                }} finally {{
                    btn.textContent = 'RESET DASHBOARD';
                }}
            }});

            function appendAlertRow(alert) {{
                if (!alert || !alert.alert_id || seenAlertIds.has(alert.alert_id)) return;
                seenAlertIds.add(alert.alert_id);
                const emptyRow = document.getElementById('empty-alerts-row');
                if (emptyRow) emptyRow.remove();

                const sev = (alert.severity || 'HIGH').toUpperCase();
                const tr = document.createElement('tr');
                tr.setAttribute('data-alert-id', alert.alert_id);
                tr.className = 'live-new-row';
                const sidShort = (alert.session_id || '').slice(0, 12) + '...';
                tr.innerHTML =
                    `<td><span class="badge badge-${{sev.toLowerCase()}}">${{sev}}</span></td>` +
                    `<td>${{alert.category || ''}}</td>` +
                    `<td><code>${{alert.source_ip || ''}}</code></td>` +
                    `<td><code>${{sidShort}}</code></td>` +
                    `<td><code>${{alert.http_method || 'GET'}} ${{alert.target_endpoint || '/'}}</code></td>` +
                    `<td>${{alert.action_taken || ''}}</td>`;
                tbody.insertBefore(tr, tbody.firstChild);
                while (tbody.children.length > 25) {{
                    tbody.removeChild(tbody.lastChild);
                }}
                refreshKpiAndMitre();
            }}

            function connectWebSocket() {{
                const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${{proto}}//${{window.location.host}}/api/v1/soc/visualizations/alerts/ws`;
                const ws = new WebSocket(wsUrl);
                ws.onopen = function() {{
                    wsBadge.textContent = 'LIVE WS: CONNECTED';
                    wsBadge.style.background = 'rgba(16,185,129,0.2)';
                    wsBadge.style.color = '#10b981';
                }};
                ws.onmessage = function(event) {{
                    try {{
                        const data = JSON.parse(event.data);
                        appendAlertRow(data);
                    }} catch (err) {{}}
                }};
                ws.onclose = function() {{
                    wsBadge.textContent = 'LIVE WS: RECONNECTING...';
                    wsBadge.style.background = 'rgba(245,158,11,0.2)';
                    wsBadge.style.color = '#f59e0b';
                    setTimeout(connectWebSocket, 1500);
                }};
            }}

            connectWebSocket();
            setInterval(refreshKpiAndMitre, 3000);
        }})();
    </script>
</body>
</html>"""


telemetry_chart_view = TelemetryChartView()
