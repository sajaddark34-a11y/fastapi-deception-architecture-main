"""
Dynamic Isolation Sandbox Package (`isolation_sandbox`).

Unified interface for Layer 3 high-interaction containment:
- Docker Sandbox Manager (`isolation_sandbox.docker_sandbox_manager`): Dual-mode
  container lifecycle controller, resource quota enforcement, and air-gapped
  network quarantine (`sandbox_containment_net`).
- Prewarmed Dynamic Sandbox (`isolation_sandbox.prewarmed_dynamic_sandbox`):
  Zero-latency standby container pool (`PrewarmedPoolController`) and session
  binder (`SandboxSessionBinder`).
- Isolated Honey Containers (`isolation_sandbox.isolated_honey_containers`):
  High-interaction decoy service (`DecoyServiceApp`), fake Linux filesystem
  (`DecoyLinuxFilesystem`), SQLi emulator (`DecoySQLDatabaseEmulator`), and
  simulated interactive shell (`SimulatedInteractiveShell`).
"""

from isolation_sandbox.docker_sandbox_manager import (
    ContainerLifecycleController,
    ContainerStateEnum,
    DockerSandboxManager,
    HoneyContainerInstance,
    ResourceQuotaPolicy,
    docker_sandbox_manager,
)
from isolation_sandbox.isolated_honey_containers.decoy_service_app import (
    DecoyLinuxFilesystem,
    DecoySQLDatabaseEmulator,
    DecoyServiceApp,
    SimulatedInteractiveShell,
    app as decoy_fastapi_app,
    decoy_service_instance,
)
from isolation_sandbox.prewarmed_dynamic_sandbox import (
    PrewarmedPoolController,
    SandboxSessionBinder,
    prewarmed_pool_controller,
    sandbox_session_binder,
)

__all__ = [
    # Container Lifecycle & Manager
    "ContainerStateEnum",
    "ResourceQuotaPolicy",
    "HoneyContainerInstance",
    "ContainerLifecycleController",
    "DockerSandboxManager",
    "docker_sandbox_manager",
    # Prewarmed Pool & Session Binding
    "PrewarmedPoolController",
    "SandboxSessionBinder",
    "prewarmed_pool_controller",
    "sandbox_session_binder",
    # High-Interaction Decoy Service & Emulators
    "DecoyLinuxFilesystem",
    "DecoySQLDatabaseEmulator",
    "SimulatedInteractiveShell",
    "DecoyServiceApp",
    "decoy_service_instance",
    "decoy_fastapi_app",
]
