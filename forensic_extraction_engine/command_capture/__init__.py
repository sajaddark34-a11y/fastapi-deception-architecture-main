"""
Command Capture Subpackage (`forensic_extraction_engine.command_capture`).

Exports `AttackerCommandLogger`, `PayloadAnalysisReport`, `MITRETechniqueMapping`,
and the singleton `attacker_command_logger`.
"""

from forensic_extraction_engine.command_capture.attacker_command_logger import (
    AttackerCommandLogger,
    MITRETechniqueMapping,
    PayloadAnalysisReport,
)

attacker_command_logger = AttackerCommandLogger()

__all__ = [
    "MITRETechniqueMapping",
    "PayloadAnalysisReport",
    "AttackerCommandLogger",
    "attacker_command_logger",
]
