"""
Shared Contracts Package (`shared_contracts`).

Centralized Pydantic v2 data schemas and enumerations enforcing strict architectural
contracts across all four layers of the FastAPI-Driven Deception Architecture:
1. Session State & Sandbox Binding (`session_schema`)
2. Honey Token Generation, Injection & Validation (`honey_token_schema`)
3. Real-Time Security Alerts (`alert_schema`)
4. Sandbox Command & Network/eBPF Telemetry (`telemetry_schema`)
5. Forensic Artifacts & SOC Incident Reports (`forensic_artifact_schema`)
"""

from shared_contracts.alert_schema import (
    AlertSeverityEnum,
    AttackCategoryEnum,
    SecurityAlertContract,
)
from shared_contracts.forensic_artifact_schema import (
    ArtifactTypeEnum,
    ForensicArtifactContract,
    IncidentReportContract,
)
from shared_contracts.honey_token_schema import (
    HoneyTokenCreateContract,
    HoneyTokenTypeEnum,
    HoneyTokenValidationContract,
    InjectionVectorEnum,
)
from shared_contracts.session_schema import (
    RoutingTargetEnum,
    SandboxBindingContract,
    SessionStateContract,
    SessionStatusEnum,
)
from shared_contracts.telemetry_schema import (
    AttackerCommandEvent,
    NetworkTelemetryEvent,
    TelemetrySourceEnum,
    TelemetryStreamEnvelope,
)

__all__ = [
    # 1. Session & Sandbox Binding Contracts
    "SessionStatusEnum",
    "RoutingTargetEnum",
    "SessionStateContract",
    "SandboxBindingContract",
    # 2. Honey Token Contracts
    "HoneyTokenTypeEnum",
    "InjectionVectorEnum",
    "HoneyTokenCreateContract",
    "HoneyTokenValidationContract",
    # 3. Security Alert Contracts
    "AlertSeverityEnum",
    "AttackCategoryEnum",
    "SecurityAlertContract",
    # 4. Forensic Telemetry Contracts
    "TelemetrySourceEnum",
    "AttackerCommandEvent",
    "NetworkTelemetryEvent",
    "TelemetryStreamEnvelope",
    # 5. Forensic Artifact & Incident Report Contracts
    "ArtifactTypeEnum",
    "ForensicArtifactContract",
    "IncidentReportContract",
]
