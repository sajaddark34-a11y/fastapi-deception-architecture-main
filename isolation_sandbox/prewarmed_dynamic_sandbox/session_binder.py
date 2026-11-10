"""
Dynamic Session-to-Sandbox Binder (`isolation_sandbox.prewarmed_dynamic_sandbox.session_binder`).

Binds malicious sessions (`SessionStateContract`) to prewarmed honey containers
using `SandboxBindingContract` (`shared_contracts.session_schema`) and persists
the binding in `SessionStateStore` (`data_storage.redis_store`).
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

from data_storage.redis_store import SessionStateStore, session_state_store
from isolation_sandbox.prewarmed_dynamic_sandbox.pool_controller import (
    PrewarmedPoolController,
)
from shared_contracts.session_schema import SandboxBindingContract

logger = logging.getLogger(__name__)


class SandboxSessionBinder:
    """
    Coordinates zero-latency session pinning between `SessionStateStore` in Redis
    and `PrewarmedPoolController`.
    """

    def __init__(
        self,
        pool_controller: Optional[PrewarmedPoolController] = None,
        state_store: Optional[SessionStateStore] = None,
    ) -> None:
        self.pool_controller: PrewarmedPoolController = (
            pool_controller or PrewarmedPoolController()
        )
        self.state_store: SessionStateStore = state_store or session_state_store

    async def get_or_create_binding(
        self,
        session_id: str,
        preferred_container_id: Optional[str] = None,
    ) -> SandboxBindingContract:
        """
        Retrieve an existing active `SandboxBindingContract` for `session_id`, or
        allocate a warm container from `PrewarmedPoolController` and persist the
        new binding in Redis.
        """
        cleaned_sid = session_id.strip()
        existing = await self.state_store.get_active_sandbox_binding(cleaned_sid)
        if existing is not None:
            await self.pool_controller.sandbox_manager.bind_container_to_session(
                container_id=existing.container_id,
                session_id=cleaned_sid,
            )
            return existing

        container = await self.pool_controller.acquire_warm_container(
            session_id=cleaned_sid,
            preferred_container_id=preferred_container_id,
        )
        digest_hex = hashlib.sha256(
            f"{cleaned_sid}:{container.container_id}".encode("utf-8")
        ).hexdigest()[:12]

        binding = SandboxBindingContract(
            binding_id=f"bind_{digest_hex}",
            session_id=cleaned_sid,
            container_id=container.container_id,
            container_internal_ip=container.internal_ip,
            container_port=container.internal_port,
            bound_at=datetime.now(timezone.utc),
            is_active=True,
        )
        return await self.state_store.bind_sandbox(binding)

    async def unbind_and_recycle_session(
        self,
        session_id: str,
        destroy_container: bool = False,
    ) -> bool:
        """
        Deactivate the session's `SandboxBindingContract` in Redis and sanitize
        or destroy the assigned honey container.
        """
        cleaned_sid = session_id.strip()
        active_binding = await self.state_store.get_active_sandbox_binding(cleaned_sid)
        released_in_redis = await self.state_store.release_sandbox_binding(cleaned_sid)

        if active_binding is not None:
            await self.pool_controller.release_container(
                container_id=active_binding.container_id,
                destroy_permanently=destroy_container,
            )
            return True

        return released_in_redis
