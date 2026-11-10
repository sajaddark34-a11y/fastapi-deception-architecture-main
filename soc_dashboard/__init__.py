"""
Defender SOC Command Center, SOAR Controls & Incident Reporting Package (Layer 4).

Exposes the unified FastAPI application (`app`), real-time attack visualization
engines (`TelemetryChartView`, `visualization_router`), SOAR containment actions,
and cryptographically verified DFIR incident report generators (`SOCIncidentReportGenerator`,
`report_export_router`).
"""

from soc_dashboard.attack_visualizations import (
    SOARContainerTeardownRequest,
    SOARIsolateSessionRequest,
    SOARRotateTokensRequest,
    TelemetryChartView,
    get_live_alerts_feed,
    get_mitre_attack_matrix,
    get_sandbox_pool_status,
    get_session_terminal_replay,
    get_soc_kpi_summary,
    handle_alerts_websocket,
    list_malicious_sessions,
    soar_isolate_session,
    soar_rotate_honey_tokens,
    soar_teardown_container,
    stream_alerts_sse,
    telemetry_chart_view,
    visualization_router,
)
from soc_dashboard.dashboard_server import (
    app,
    dashboard_core_router,
    render_soc_command_center_ui,
    soc_dashboard_health_check,
    soc_dashboard_lifespan,
    soc_dashboard_metrics,
)
from soc_dashboard.incident_reports import (
    SOCIncidentReportGenerator,
    export_signed_incident_bundle_endpoint,
    generate_incident_report_endpoint,
    get_incident_report_by_id_endpoint,
    list_incident_reports_endpoint,
    list_session_forensic_artifacts_endpoint,
    report_export_router,
    soc_incident_report_generator,
    verify_session_custody_endpoint,
)

__all__ = [
    "app",
    "soc_dashboard_lifespan",
    "dashboard_core_router",
    "render_soc_command_center_ui",
    "soc_dashboard_health_check",
    "soc_dashboard_metrics",
    "TelemetryChartView",
    "telemetry_chart_view",
    "visualization_router",
    "SOARIsolateSessionRequest",
    "SOARContainerTeardownRequest",
    "SOARRotateTokensRequest",
    "get_soc_kpi_summary",
    "get_live_alerts_feed",
    "stream_alerts_sse",
    "get_mitre_attack_matrix",
    "list_malicious_sessions",
    "get_session_terminal_replay",
    "get_sandbox_pool_status",
    "soar_isolate_session",
    "soar_teardown_container",
    "soar_rotate_honey_tokens",
    "handle_alerts_websocket",
    "SOCIncidentReportGenerator",
    "soc_incident_report_generator",
    "report_export_router",
    "generate_incident_report_endpoint",
    "list_incident_reports_endpoint",
    "get_incident_report_by_id_endpoint",
    "verify_session_custody_endpoint",
    "export_signed_incident_bundle_endpoint",
    "list_session_forensic_artifacts_endpoint",
]
