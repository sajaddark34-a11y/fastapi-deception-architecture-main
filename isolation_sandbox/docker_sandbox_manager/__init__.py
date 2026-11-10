"""
Docker Sandbox Manager Subpackage (`isolation_sandbox.docker_sandbox_manager`).

Exports container lifecycle classes, resource quota policies, and the
`DockerSandboxManager` singleton.
"""

from isolation_sandbox.docker_sandbox_manager.container_lifecycle import (
    ContainerLifecycleController,
    ContainerStateEnum,
    HoneyContainerInstance,
    ResourceQuotaPolicy,
)
from isolation_sandbox.docker_sandbox_manager.manager import DockerSandboxManager

docker_sandbox_manager = DockerSandboxManager()

__all__ = [
    "ContainerStateEnum",
    "ResourceQuotaPolicy",
    "HoneyContainerInstance",
    "ContainerLifecycleController",
    "DockerSandboxManager",
    "docker_sandbox_manager",
]
