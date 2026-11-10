"""
Forensic Extraction Engine Package (`forensic_extraction_engine`).

Exports the automated DFIR extraction pipeline:
- Command Capture (`AttackerCommandLogger`, `PayloadAnalysisReport`, `MITRETechniqueMapping`)
- Network & Kernel Capture (`PacketCaptureSniffer`, `FlowFingerprintMetadata`, `EbpfProbeHandler`, `EbpfSyscallTrace`)
- Telemetry Collector & Chain of Custody (`ForensicTelemetryCollector`, `TamperEvidentChainOfCustody`, `CustodyLedgerEntry`)
- Engine Service (`ForensicExtractionEngineService`, `forensic_engine_service`, `app`)
"""

from forensic_extraction_engine.command_capture import (
    AttackerCommandLogger,
    MITRETechniqueMapping,
    PayloadAnalysisReport,
    attacker_command_logger,
)
from forensic_extraction_engine.engine_service import (
    ForensicExtractionEngineService,
    app,
    forensic_engine_lifespan,
    forensic_engine_service,
)
from forensic_extraction_engine.network_capture import (
    EbpfProbeHandler,
    EbpfSyscallTrace,
    FlowFingerprintMetadata,
    PacketCaptureSniffer,
    ebpf_probe_handler,
    pcap_sniffer,
)
from forensic_extraction_engine.telemetry_collector import (
    CHAIN_OF_CUSTODY_HMAC_SECRET,
    CustodyLedgerEntry,
    ForensicTelemetryCollector,
    TamperEvidentChainOfCustody,
    forensic_telemetry_collector,
)

__all__ = [
    # Command Capture & Deobfuscation
    "MITRETechniqueMapping",
    "PayloadAnalysisReport",
    "AttackerCommandLogger",
    "attacker_command_logger",
    # Network & eBPF Capture
    "FlowFingerprintMetadata",
    "PacketCaptureSniffer",
    "EbpfSyscallTrace",
    "EbpfProbeHandler",
    "pcap_sniffer",
    "ebpf_probe_handler",
    # Unified Telemetry Collector & Chain of Custody
    "CHAIN_OF_CUSTODY_HMAC_SECRET",
    "CustodyLedgerEntry",
    "TamperEvidentChainOfCustody",
    "ForensicTelemetryCollector",
    "forensic_telemetry_collector",
    # Engine Service & FastAPI App
    "ForensicExtractionEngineService",
    "forensic_engine_service",
    "forensic_engine_lifespan",
    "app",
]
