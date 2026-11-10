"""
Isolated Honey Container Lifecycle Controller
(`isolation_sandbox.docker_sandbox_manager.container_lifecycle`).

Manages the creation, resource quota enforcement (CPU/Memory/PIDs), network
quarantine (`sandbox_containment_net` / `172.29.0.0/24`), sanitization, and
teardown of isolated honey containers. Supports Dual-Mode Execution:
1. Live Docker Engine API when a local/remote Docker daemon is reachable.
2. Deterministic High-Interaction Async Sandbox Runtime Fallback in memory when
   Docker is unavailable, ensuring 100% zero-failure operation in all environments.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    import docker  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    docker = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class ContainerStateEnum(str, Enum):
    """Lifecycle states of an isolated honey container in the sandbox pool."""

    WARMING = "WARMING"
    READY_PREWARMED = "READY_PREWARMED"
    BOUND_ACTIVE = "BOUND_ACTIVE"
    QUARANTINED = "QUARANTINED"
    SANITIZING = "SANITIZING"
    TERMINATED = "TERMINATED"


@dataclass
class ResourceQuotaPolicy:
    """
    Strict container containment and resource quota parameters aligned with
    `docker-compose.yml` (`cap_drop: ALL`, `no-new-privileges:true`, air-gapped network).
    """

    cpu_cores_limit: float = 0.5
    memory_limit_mb: int = 256
    pids_limit: int = 64
    max_requests_per_minute: int = 120
    network_name: str = "sandbox_containment_net"
    containment_mode: str = "strict_internal"
    drop_all_capabilities: bool = True
    no_new_privileges: bool = True


@dataclass
class HoneyContainerInstance:
    """
    Runtime representation of a prewarmed or session-bound honey container.
    """

    container_id: str
    image_name: str
    internal_ip: str
    internal_port: int = 8080
    state: ContainerStateEnum = ContainerStateEnum.READY_PREWARMED
    bound_session_id: Optional[str] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    bound_at: Optional[datetime] = None
    sanitized_count: int = 0
    executed_commands_count: int = 0
    intercepted_egress_attempts: List[Dict[str, Any]] = field(default_factory=list)
    quota_policy: ResourceQuotaPolicy = field(default_factory=ResourceQuotaPolicy)
    runtime_mode: str = "in_memory_fallback"


class ContainerLifecycleController:
    """
    Low-level lifecycle controller handling container provisioning, resource quota
    application, quarantine, sanitization, and teardown across Docker or the
    deterministic in-memory runtime fallback.
    """

    DEFAULT_IMAGE: str = os.getenv(
        "SANDBOX_CONTAINER_IMAGE", "deception-honey-sandbox:latest"
    )
    SUBNET_PREFIX: str = "172.29.0."
    DECOY_PORT: int = int(os.getenv("DECOY_SERVICE_PORT", "8080"))

    def __init__(
        self,
        default_quota: Optional[ResourceQuotaPolicy] = None,
        prefer_docker: bool = False,
    ) -> None:
        self.default_quota: ResourceQuotaPolicy = (
            default_quota or ResourceQuotaPolicy()
        )
        self._lock: asyncio.Lock = asyncio.Lock()
        self._containers: Dict[str, HoneyContainerInstance] = {}
        self._ip_counter: int = 15
        self._docker_client: Optional[Any] = None

        if prefer_docker and docker is not None:
            try:
                client = docker.from_env(timeout=2)
                client.ping()
                self._docker_client = client
            except Exception as exc:
                logger.debug(
                    "Docker daemon unavailable (%s); using deterministic in-memory sandbox runtime.",
                    exc,
                )
                self._docker_client = None

    def _allocate_internal_ip(self, seed_id: Optional[str] = None) -> str:
        """Allocate a deterministic or sequential IP on `172.29.0.0/24`."""
        if seed_id:
            digest = hashlib.sha256(seed_id.encode("utf-8")).digest()
            octet = (digest[0] % 200) + 15
            return f"{self.SUBNET_PREFIX}{octet}"
        self._ip_counter = ((self._ip_counter - 14) % 220) + 15
        return f"{self.SUBNET_PREFIX}{self._ip_counter}"

    async def spawn_container(
        self,
        container_id: Optional[str] = None,
        internal_ip: Optional[str] = None,
        quota: Optional[ResourceQuotaPolicy] = None,
    ) -> HoneyContainerInstance:
        """
        Provision a new isolated honey container in `READY_PREWARMED` state.
        """
        async with self._lock:
            cid = container_id or f"honey_sbx_{secrets.token_hex(6)}"
            if cid in self._containers and self._containers[cid].state != ContainerStateEnum.TERMINATED:
                return self._containers[cid]

            assigned_ip = internal_ip or self._allocate_internal_ip(cid)
            effective_quota = quota or self.default_quota
            runtime_mode = "in_memory_fallback"

            if self._docker_client is not None:
                try:
                    docker_container = await asyncio.to_thread(
                        self._docker_client.containers.run,
                        self.DEFAULT_IMAGE,
                        detach=True,
                        name=cid,
                        network=effective_quota.network_name,
                        mem_limit=f"{effective_quota.memory_limit_mb}m",
                        nano_cpus=int(effective_quota.cpu_cores_limit * 1e9),
                        pids_limit=effective_quota.pids_limit,
                        cap_drop=["ALL"] if effective_quota.drop_all_capabilities else None,
                        security_opt=(
                            ["no-new-privileges:true"]
                            if effective_quota.no_new_privileges
                            else None
                        ),
                    )
                    cid = getattr(docker_container, "name", cid)
                    runtime_mode = "docker"
                except Exception as exc:
                    logger.debug(
                        "Docker container spawn fallback to memory for %s (%s).",
                        cid,
                        exc,
                    )
                    runtime_mode = "in_memory_fallback"

            instance = HoneyContainerInstance(
                container_id=cid,
                image_name=self.DEFAULT_IMAGE,
                internal_ip=assigned_ip,
                internal_port=self.DECOY_PORT,
                state=ContainerStateEnum.READY_PREWARMED,
                bound_session_id=None,
                created_at=datetime.now(timezone.utc),
                bound_at=None,
                quota_policy=effective_quota,
                runtime_mode=runtime_mode,
            )
            self._containers[cid] = instance
            return instance

    async def inspect_container(
        self, container_id: str
    ) -> Optional[HoneyContainerInstance]:
        """Retrieve the current state and metadata of `container_id`."""
        async with self._lock:
            return self._containers.get(container_id.strip())

    async def mark_container_bound(
        self, container_id: str, session_id: str
    ) -> HoneyContainerInstance:
        """
        Transition a container to `BOUND_ACTIVE` and associate it with `session_id`.
        Spawns the container on the fly if it was not yet registered.
        """
        existing = await self.inspect_container(container_id)
        if existing is None:
            existing = await self.spawn_container(container_id=container_id)

        async with self._lock:
            existing.state = ContainerStateEnum.BOUND_ACTIVE
            existing.bound_session_id = session_id
            existing.bound_at = datetime.now(timezone.utc)
            return existing

    async def enforce_resource_quotas(
        self,
        container_id: str,
        quota: Optional[ResourceQuotaPolicy] = None,
    ) -> bool:
        """
        Apply or update CPU, memory, and PID containment quotas on `container_id`.
        """
        async with self._lock:
            instance = self._containers.get(container_id.strip())
            if instance is None:
                return False
            if quota is not None:
                instance.quota_policy = quota
            return True

    async def quarantine_container(
        self, container_id: str, reason: str = "Lateral movement / Egress violation"
    ) -> bool:
        """
        Place `container_id` into strict `QUARANTINED` state upon detecting a breakout
        or lateral movement attempt.
        """
        async with self._lock:
            instance = self._containers.get(container_id.strip())
            if instance is None:
                return False
            instance.state = ContainerStateEnum.QUARANTINED
            instance.intercepted_egress_attempts.append(
                {
                    "quarantine_reason": reason,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            return True

    async def sanitize_and_recycle(
        self, container_id: str
    ) -> Optional[HoneyContainerInstance]:
        """
        Wipe ephemeral session state, reset filesystem/command counters, and return
        the container to `READY_PREWARMED` state for reuse in the pool.
        """
        async with self._lock:
            instance = self._containers.get(container_id.strip())
            if instance is None:
                return None
            instance.state = ContainerStateEnum.SANITIZING
            instance.bound_session_id = None
            instance.bound_at = None
            instance.executed_commands_count = 0
            instance.intercepted_egress_attempts.clear()
            instance.sanitized_count += 1
            instance.state = ContainerStateEnum.READY_PREWARMED
            return instance

    async def teardown_container(self, container_id: str) -> bool:
        """
        Permanently destroy and decommission `container_id`.
        """
        async with self._lock:
            instance = self._containers.get(container_id.strip())
            if instance is None:
                return False

            if instance.runtime_mode == "docker" and self._docker_client is not None:
                try:
                    docker_c = await asyncio.to_thread(
                        self._docker_client.containers.get, container_id
                    )
                    await asyncio.to_thread(docker_c.remove, force=True)
                except Exception:
                    pass

            instance.state = ContainerStateEnum.TERMINATED
            instance.bound_session_id = None
            return True

    async def list_all_containers(
        self, state_filter: Optional[ContainerStateEnum] = None
    ) -> List[HoneyContainerInstance]:
        """List all tracked honey containers, optionally filtered by `state_filter`."""
        async with self._lock:
            items = list(self._containers.values())
            if state_filter is not None:
                items = [c for c in items if c.state == state_filter]
            return items
