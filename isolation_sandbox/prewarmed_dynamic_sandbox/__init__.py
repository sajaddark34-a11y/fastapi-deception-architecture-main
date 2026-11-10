"""
Prewarmed Dynamic Sandbox Subpackage (`isolation_sandbox.prewarmed_dynamic_sandbox`).

Exports `PrewarmedPoolController` and `SandboxSessionBinder` along with their
ready-to-use singleton instances.
"""

from isolation_sandbox.prewarmed_dynamic_sandbox.pool_controller import (
    PrewarmedPoolController,
)
from isolation_sandbox.prewarmed_dynamic_sandbox.session_binder import (
    SandboxSessionBinder,
)

prewarmed_pool_controller = PrewarmedPoolController()
sandbox_session_binder = SandboxSessionBinder(
    pool_controller=prewarmed_pool_controller
)

__all__ = [
    "PrewarmedPoolController",
    "SandboxSessionBinder",
    "prewarmed_pool_controller",
    "sandbox_session_binder",
]
