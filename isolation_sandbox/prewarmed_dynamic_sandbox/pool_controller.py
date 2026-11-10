"""
Pre-Warmed Dynamic Sandbox Pool Controller
(`isolation_sandbox.prewarmed_dynamic_sandbox.pool_controller`).

Maintains a standby pool of pre-initialized isolated honey containers so that
when `deception_gateway` diverts an adversary, container allocation occurs with
sub-millisecond zero-latency overhead.
"""

from __future__ import annotations

import asyncio
import logging
import os
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from isolation_sandbox.docker_sandbox_manager.container_lifecycle import (
    ContainerStateEnum,
    HoneyContainerInstance,
)
from isolation_sandbox.docker_sandbox_manager import (
    DockerSandboxManager,
    docker_sandbox_manager,
)

logger = logging.getLogger(__name__)


class PrewarmedPoolController:
    """
    Manages a warm standby queue of isolated honey containers (`READY_PREWARMED`)
    and automatically replenishes capacity as containers are bound to trapped sessions.
    """

    def __init__(
        self,
        sandbox_manager: Optional[DockerSandboxManager] = None,
        target_pool_size: int = int(os.getenv("PREWARMED_POOL_SIZE", "3")),
    ) -> None:
        self.sandbox_manager: DockerSandboxManager = (
            sandbox_manager or docker_sandbox_manager
        )
        self.target_pool_size: int = max(1, target_pool_size)
        self._lock: asyncio.Lock = asyncio.Lock()
        self._warm_queue: Deque[str] = deque()
        self._initialized: bool = False

    async def initialize_warm_pool(
        self, pool_size: Optional[int] = None
    ) -> List[HoneyContainerInstance]:
        """
        Pre-provision standby honey containers up to `target_pool_size`.
        """
        if pool_size is not None:
            self.target_pool_size = max(1, pool_size)

        provisioned: List[HoneyContainerInstance] = []
        async with self._lock:
            while len(self._warm_queue) < self.target_pool_size:
                idx = len(self._warm_queue) + 1
                cid = f"honey_sbx_warm_{idx:03d}"
                instance = await self.sandbox_manager.provision_honey_container(
                    preferred_container_id=cid
                )
                if instance.container_id not in self._warm_queue:
                    self._warm_queue.append(instance.container_id)
                provisioned.append(instance)
            self._initialized = True

        return provisioned

    async def replenish_pool(self) -> List[HoneyContainerInstance]:
        """
        Ensure the number of standby `READY_PREWARMED` containers meets `target_pool_size`.
        """
        created: List[HoneyContainerInstance] = []
        async with self._lock:
            while len(self._warm_queue) < self.target_pool_size:
                instance = await self.sandbox_manager.provision_honey_container()
                if instance.container_id not in self._warm_queue:
                    self._warm_queue.append(instance.container_id)
                created.append(instance)
        return created

    async def acquire_warm_container(
        self,
        session_id: str,
        preferred_container_id: Optional[str] = None,
    ) -> HoneyContainerInstance:
        """
        Claim an immediately available warm container for `session_id` with zero
        cold-start delay, and replenish the standby pool.
        """
        if not self._initialized:
            await self.initialize_warm_pool()

        if preferred_container_id:
            async with self._lock:
                if preferred_container_id in self._warm_queue:
                    self._warm_queue.remove(preferred_container_id)
            bound = await self.sandbox_manager.bind_container_to_session(
                container_id=preferred_container_id,
                session_id=session_id,
            )
            await self.replenish_pool()
            return bound

        chosen_cid: Optional[str] = None
        async with self._lock:
            while self._warm_queue:
                candidate = self._warm_queue.popleft()
                inspected = await self.sandbox_manager.lifecycle.inspect_container(
                    candidate
                )
                if (
                    inspected is not None
                    and inspected.state == ContainerStateEnum.READY_PREWARMED
                ):
                    chosen_cid = candidate
                    break

        if chosen_cid is None:
            fresh = await self.sandbox_manager.provision_honey_container()
            chosen_cid = fresh.container_id

        bound_instance = await self.sandbox_manager.bind_container_to_session(
            container_id=chosen_cid,
            session_id=session_id,
        )
        await self.replenish_pool()
        return bound_instance

    async def release_container(
        self,
        container_id: str,
        destroy_permanently: bool = False,
    ) -> bool:
        """
        Release a bound container, sanitize or destroy it, and return it to the warm pool.
        """
        ok = await self.sandbox_manager.release_and_sanitize_container(
            container_id=container_id,
            destroy_permanently=destroy_permanently,
        )
        if ok and not destroy_permanently:
            async with self._lock:
                if container_id not in self._warm_queue:
                    self._warm_queue.append(container_id)
        elif destroy_permanently:
            await self.replenish_pool()
        return ok

    async def get_pool_metrics(self) -> Dict[str, Any]:
        """Return real-time capacity and utilization metrics of the prewarmed pool."""
        mgr_status = await self.sandbox_manager.get_manager_status()
        async with self._lock:
            warm_ids = list(self._warm_queue)
        return {
            "target_pool_size": self.target_pool_size,
            "available_warm_containers_count": len(warm_ids),
            "available_warm_container_ids": warm_ids,
            "manager_status": mgr_status,
        }
