"""
Sub-Millisecond Redis Session Cache Verifier (`deception_gateway.redis_cache_verifier`).

Interfaces with `SessionStateStore` (`data_storage.redis_store.session_state_store`)
to resolve incoming client sessions by `session_id` or `client_ip`, evaluate whether
a session is already flagged as `MALICIOUS_TRAPPED` or `ISOLATED`, and retrieve
any active `SandboxBindingContract`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

from data_storage.redis_store import SessionStateStore, session_state_store
from shared_contracts.session_schema import (
    RoutingTargetEnum,
    SandboxBindingContract,
    SessionStateContract,
    SessionStatusEnum,
)


class RedisCacheVerifier:
    """
    High-speed session state verifier evaluating client identity and containment
    status at the perimeter of the Deception Gateway.
    """

    def __init__(
        self,
        store: Optional[SessionStateStore] = None,
        default_ttl_seconds: int = 3600,
    ) -> None:
        """
        Initialize the verifier with a `SessionStateStore` instance.
        """
        self.store: SessionStateStore = store or session_state_store
        self.default_ttl_seconds: int = default_ttl_seconds

    async def resolve_or_create_session(
        self,
        session_id: Optional[str],
        client_ip: str,
        user_agent: str,
    ) -> SessionStateContract:
        """
        Look up an existing session in Redis by `session_id` or `client_ip`. If found,
        increment its `request_count` and update `last_active_at`. If not found,
        initialize and persist a new `LEGITIMATE` session contract.

        Args:
            session_id: Optional session identifier extracted from header or cookie.
            client_ip: Client source IPv4/IPv6 address.
            user_agent: Client HTTP User-Agent string.

        Returns:
            Active `SessionStateContract`.
        """
        safe_ip = (client_ip or "127.0.0.1").strip()
        if safe_ip == "testclient":
            safe_ip = "127.0.0.1"
        safe_ua = (user_agent or "Mozilla/5.0 (Unknown)").strip()[:1024]

        existing: Optional[SessionStateContract] = None
        if session_id and len(session_id.strip()) >= 8:
            existing = await self.store.get_session(session_id.strip())

        if existing is None:
            existing = await self.store.get_session_by_ip(safe_ip)

        if existing is not None:
            now_utc = datetime.now(timezone.utc)
            updated = existing.model_copy(
                update={
                    "request_count": existing.request_count + 1,
                    "last_active_at": max(now_utc, existing.first_seen_at),
                    "user_agent": safe_ua or existing.user_agent,
                }
            )
            return await self.store.upsert_session(updated)

        new_session_id = (
            session_id.strip()
            if (session_id and len(session_id.strip()) >= 8)
            else str(uuid.uuid4())
        )
        now_utc = datetime.now(timezone.utc)
        fresh_session = SessionStateContract(
            session_id=new_session_id,
            client_ip=safe_ip,
            user_agent=safe_ua,
            status=SessionStatusEnum.LEGITIMATE,
            routing_target=RoutingTargetEnum.CORE_WEB_APP,
            risk_score=0.0,
            triggered_token_id=None,
            assigned_container_id=None,
            request_count=1,
            first_seen_at=now_utc,
            last_active_at=now_utc,
            ttl_seconds=self.default_ttl_seconds,
        )
        return await self.store.upsert_session(fresh_session)

    async def verify_session_status(
        self,
        session_id: Optional[str],
        client_ip: str,
        user_agent: str = "Mozilla/5.0",
    ) -> Tuple[SessionStateContract, bool, Optional[SandboxBindingContract]]:
        """
        Verify a client's session state and determine whether it is already trapped
        or isolated, returning the session contract, a boolean `is_already_malicious`,
        and any active `SandboxBindingContract`.
        """
        session = await self.resolve_or_create_session(
            session_id=session_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        is_malicious = (
            session.status
            in (
                SessionStatusEnum.MALICIOUS_TRAPPED,
                SessionStatusEnum.ISOLATED,
            )
            or session.routing_target == RoutingTargetEnum.PREWARMED_SANDBOX
        )
        binding: Optional[SandboxBindingContract] = None
        if is_malicious:
            binding = await self.store.get_active_sandbox_binding(session.session_id)
        return session, is_malicious, binding

    async def get_assigned_container_id(self, session_id: str) -> Optional[str]:
        """
        Retrieve the isolated honey container ID bound to `session_id`, if any.
        """
        binding = await self.store.get_active_sandbox_binding(session_id)
        if binding is not None:
            return binding.container_id

        session = await self.store.get_session(session_id)
        if session is not None:
            return session.assigned_container_id
        return None
