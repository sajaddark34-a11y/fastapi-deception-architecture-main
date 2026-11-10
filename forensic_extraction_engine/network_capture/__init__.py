"""
Network and Kernel Capture Subpackage (`forensic_extraction_engine.network_capture`).

Exports `PacketCaptureSniffer`, `FlowFingerprintMetadata`, `EbpfProbeHandler`,
`EbpfSyscallTrace`, and the singletons `pcap_sniffer` and `ebpf_probe_handler`.
"""

from forensic_extraction_engine.network_capture.ebpf_probe_handler import (
    EbpfProbeHandler,
    EbpfSyscallTrace,
)
from forensic_extraction_engine.network_capture.pcap_sniffer import (
    FlowFingerprintMetadata,
    PacketCaptureSniffer,
)

pcap_sniffer = PacketCaptureSniffer()
ebpf_probe_handler = EbpfProbeHandler()

__all__ = [
    "FlowFingerprintMetadata",
    "PacketCaptureSniffer",
    "EbpfSyscallTrace",
    "EbpfProbeHandler",
    "pcap_sniffer",
    "ebpf_probe_handler",
]
