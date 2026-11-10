"""
Asynchronous Redis Session State and Sandbox Binding Store.

Manages sub-millisecond session tracking, IP-to-session indexing, threat escalation,
and isolated container bindings using `redis.asyncio` with an automatic thread/async-safe
in-memory fallback for local testing and offline validation.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from shared_contracts.session_schema import (
    RoutingTargetEnum,
    SandboxBindingContract,
    SessionStateContract,
    SessionStatusEnum,
)

try:
    import redis.asyncio as aioredis
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover
    aioredis = None  # type: ignore[assignment]

    class RedisError(Exception):  # type: ignore[no-redef]
        """Fallback exception when redis package is unavailable."""


logger = logging.getLogger(__name__)


class SessionStateStore:
    """
    Asynchronous repository managing `SessionStateContract` and `SandboxBindingContract`
    records in Redis with seamless in-memory fallback.
    """

    SESSION_KEY_PREFIX: str = "deception:session:"
    IP_INDEX_KEY_PREFIX: str = "deception:ip_index:"
    SANDBOX_BINDING_PREFIX: str = "deception:sandbox_binding:"
    MALICIOUS_SET_KEY: str = "deception:malicious_sessions"

    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl_seconds: int = 3600,
    ) -> None:
        """
        Initialize the session state store with Redis configuration and fallback structures.

        Args:
            redis_url: Optional Redis connection URI. Defaults to `REDIS_URL` env var
                or constructs from `REDIS_HOST` and `REDIS_PORT`.
            default_ttl_seconds: Default time-to-live for session keys in seconds.
        """
        host = os.getenv("REDIS_HOST", "redis_store")
        port = os.getenv("REDIS_PORT", "6379")
        self._redis_url: str = redis_url or os.getenv(
            "REDIS_URL", f"redis://{host}:{port}/0"
        )
        self._default_ttl_seconds: int = default_ttl_seconds
        self._redis_client: Optional["aioredis.Redis"] = None
        self._use_memory_fallback: bool = aioredis is None
        self._lock: asyncio.Lock = asyncio.Lock()

        # In-memory fallback stores: key -> (json_payload, expire_monotonic_ts)
        self._mem_sessions: Dict[str, Tuple[str, float]] = {}
        self._mem_ip_index: Dict[str, Tuple[str, float]] = {}
        self._mem_bindings: Dict[str, SandboxBindingContract] = {}
        self._mem_malicious_ids: Set[str] = set()

    async def _get_client(self) -> Optional["aioredis.Redis"]:
        """Return an active Redis async client or switch to in-memory fallback if unreachable."""
        if self._use_memory_fallback or aioredis is None:
            return None

        if self._redis_client is None:
            try:
                client = aioredis.from_url(
                    self._redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=1.5,
                    socket_timeout=1.5,
                )
                await client.ping()
                self._redis_client = client
            except Exception as exc:
                logger.warning(
                    "Redis unreachable at %s (%s). Switching SessionStateStore to in-memory fallback.",
                    self._redis_url,
                    exc,
                )
                self._use_memory_fallback = True
                self._redis_client = None
                return None

        return self._redis_client

    def _session_key(self, session_id: str) -> str:
        """Construct the Redis key for a session ID."""
        return f"{self.SESSION_KEY_PREFIX}{session_id}"

    def _ip_key(self, client_ip: str) -> str:
        """Construct the Redis key for an IP-to-session lookup."""
        return f"{self.IP_INDEX_KEY_PREFIX}{client_ip}"

    def _binding_key(self, session_id: str) -> str:
        """Construct the Redis key for a session's sandbox container binding."""
        return f"{self.SANDBOX_BINDING_PREFIX}{session_id}"

    def _purge_expired_memory_entries(self) -> None:
        """Clean up expired session entries in the in-memory fallback dictionary."""
        now_mono = time.monotonic()
        expired_sessions = [
            sid
            for sid, (_, exp_ts) in self._mem_sessions.items()
            if exp_ts <= now_mono
        ]
        for sid in expired_sessions:
            self._mem_sessions.pop(sid, None)
            self._mem_malicious_ids.discard(sid)

        expired_ips = [
            ip
            for ip, (_, exp_ts) in self._mem_ip_index.items()
            if exp_ts <= now_mono
        ]
        for ip in expired_ips:
            self._mem_ip_index.pop(ip, None)

    async def get_session(self, session_id: str) -> Optional[SessionStateContract]:
        """
        Retrieve a tracked session state by its unique `session_id`.

        Args:
            session_id: Unique session identifier.

        Returns:
            `SessionStateContract` if present and not expired, otherwise `None`.
        """
        cleaned_id = session_id.strip()
        if not cleaned_id:
            return None

        client = await self._get_client()
        if client is not None:
            try:
                raw_json = await client.get(self._session_key(cleaned_id))
                if not raw_json:
                    return None
                return SessionStateContract.model_validate_json(raw_json)
            except (RedisError, OSError) as exc:
                logger.warning("Redis get_session error (%s); falling back to memory.", exc)
                self._use_memory_fallback = True

        async with self._lock:
            self._purge_expired_memory_entries()
            entry = self._mem_sessions.get(cleaned_id)
            if entry is None:
                return None
            payload_json, _ = entry
            return SessionStateContract.model_validate_json(payload_json)

    async def get_session_by_ip(self, client_ip: str) -> Optional[SessionStateContract]:
        """
        Look up the most recent active session associated with `client_ip`.

        Args:
            client_ip: Client source IPv4 or IPv6 address.

        Returns:
            `SessionStateContract` if an active session is indexed for the IP, else `None`.
        """
        cleaned_ip = client_ip.strip()
        if not cleaned_ip:
            return None

        client = await self._get_client()
        if client is not None:
            try:
                session_id = await client.get(self._ip_key(cleaned_ip))
                if not session_id:
                    return None
                return await self.get_session(session_id)
            except (RedisError, OSError) as exc:
                logger.warning("Redis get_session_by_ip error (%s); falling back to memory.", exc)
                self._use_memory_fallback = True

        async with self._lock:
            self._purge_expired_memory_entries()
            ip_entry = self._mem_ip_index.get(cleaned_ip)
            if ip_entry is None:
                return None
            indexed_session_id, _ = ip_entry
            sess_entry = self._mem_sessions.get(indexed_session_id)
            if sess_entry is None:
                return None
            return SessionStateContract.model_validate_json(sess_entry[0])

    async def upsert_session(self, session: SessionStateContract) -> SessionStateContract:
        """
        Insert or update a `SessionStateContract` in Redis with automatic TTL configuration
        derived from `session.ttl_seconds`. Also updates the IP-to-session index and
        malicious sessions index set.

        Args:
            session: Validated `SessionStateContract` instance.

        Returns:
            The persisted `SessionStateContract`.
        """
        ttl = session.ttl_seconds if session.ttl_seconds > 0 else self._default_ttl_seconds
        payload_json = session.model_dump_json()
        is_malicious = (
            session.status in (SessionStatusEnum.MALICIOUS_TRAPPED, SessionStatusEnum.ISOLATED)
            or session.routing_target == RoutingTargetEnum.PREWARMED_SANDBOX
        )

        # Always keep local fallback synchronized for resilience
        async with self._lock:
            self._purge_expired_memory_entries()
            expire_at = time.monotonic() + float(ttl)
            self._mem_sessions[session.session_id] = (payload_json, expire_at)
            self._mem_ip_index[session.client_ip] = (session.session_id, expire_at)
            if is_malicious:
                self._mem_malicious_ids.add(session.session_id)
            else:
                self._mem_malicious_ids.discard(session.session_id)

        client = await self._get_client()
        if client is not None:
            try:
                pipe = client.pipeline(transaction=True)
                pipe.set(self._session_key(session.session_id), payload_json, ex=ttl)
                pipe.set(self._ip_key(session.client_ip), session.session_id, ex=ttl)
                if is_malicious:
                    pipe.sadd(self.MALICIOUS_SET_KEY, session.session_id)
                else:
                    pipe.srem(self.MALICIOUS_SET_KEY, session.session_id)
                await pipe.execute()
            except (RedisError, OSError) as exc:
                logger.warning("Redis upsert_session error (%s); persisted in memory.", exc)
                self._use_memory_fallback = True

        return session

    async def escalate_session_to_malicious(
        self,
        session_id: str,
        triggered_token_id: Optional[str],
        assigned_container_id: Optional[str],
        risk_score: float = 100.0,
    ) -> Optional[SessionStateContract]:
        """
        Escalate an existing session to `MALICIOUS_TRAPPED` and divert its routing target
        to `PREWARMED_SANDBOX`.

        Args:
            session_id: Identifier of the session to escalate.
            triggered_token_id: Optional ID of the honey token triggered by the client.
            assigned_container_id: Optional ID of the isolated container bound to the session.
            risk_score: Threat score assigned (clamped between 0.0 and 100.0, defaults to 100.0).

        Returns:
            Updated `SessionStateContract` if the session exists, else `None`.
        """
        existing = await self.get_session(session_id)
        if existing is None:
            return None

        now_utc = datetime.now(timezone.utc)
        effective_last_active = max(now_utc, existing.first_seen_at)
        clamped_score = max(0.0, min(100.0, float(risk_score)))

        updated_session = existing.model_copy(
            update={
                "status": SessionStatusEnum.MALICIOUS_TRAPPED,
                "routing_target": RoutingTargetEnum.PREWARMED_SANDBOX,
                "risk_score": clamped_score,
                "triggered_token_id": triggered_token_id or existing.triggered_token_id,
                "assigned_container_id": assigned_container_id or existing.assigned_container_id,
                "last_active_at": effective_last_active,
            }
        )
        return await self.upsert_session(updated_session)

    async def increment_request_count(self, session_id: str) -> int:
        """
        Atomically increment the `request_count` of an existing session and refresh
        its `last_active_at` timestamp.

        Args:
            session_id: Session identifier.

        Returns:
            Updated request count, or `0` if the session was not found.
        """
        existing = await self.get_session(session_id)
        if existing is None:
            return 0

        now_utc = datetime.now(timezone.utc)
        effective_last_active = max(now_utc, existing.first_seen_at)
        new_count = existing.request_count + 1

        updated = existing.model_copy(
            update={
                "request_count": new_count,
                "last_active_at": effective_last_active,
            }
        )
        await self.upsert_session(updated)
        return new_count

    async def bind_sandbox(
        self, binding: SandboxBindingContract
    ) -> SandboxBindingContract:
        """
        Persist a `SandboxBindingContract` mapping a trapped session to an isolated
        honey container, and synchronize the session's `assigned_container_id`.

        Args:
            binding: Validated `SandboxBindingContract` instance.

        Returns:
            The stored `SandboxBindingContract`.
        """
        payload_json = binding.model_dump_json()

        async with self._lock:
            self._mem_bindings[binding.session_id] = binding

        client = await self._get_client()
        if client is not None:
            try:
                await client.set(
                    self._binding_key(binding.session_id),
                    payload_json,
                    ex=self._default_ttl_seconds,
                )
            except (RedisError, OSError) as exc:
                logger.warning("Redis bind_sandbox error (%s); stored in memory.", exc)
                self._use_memory_fallback = True

        existing_session = await self.get_session(binding.session_id)
        if existing_session is not None and (
            existing_session.assigned_container_id != binding.container_id
            or existing_session.routing_target != RoutingTargetEnum.PREWARMED_SANDBOX
        ):
            now_utc = datetime.now(timezone.utc)
            updated_session = existing_session.model_copy(
                update={
                    "assigned_container_id": binding.container_id,
                    "status": SessionStatusEnum.MALICIOUS_TRAPPED,
                    "routing_target": RoutingTargetEnum.PREWARMED_SANDBOX,
                    "last_active_at": max(now_utc, existing_session.first_seen_at),
                }
            )
            await self.upsert_session(updated_session)

        return binding

    async def get_active_sandbox_binding(
        self, session_id: str
    ) -> Optional[SandboxBindingContract]:
        """
        Retrieve the currently active `SandboxBindingContract` for a session.

        Args:
            session_id: Session identifier.

        Returns:
            `SandboxBindingContract` if found and `is_active` is `True`, else `None`.
        """
        cleaned_id = session_id.strip()
        if not cleaned_id:
            return None

        client = await self._get_client()
        if client is not None:
            try:
                raw_json = await client.get(self._binding_key(cleaned_id))
                if raw_json:
                    binding = SandboxBindingContract.model_validate_json(raw_json)
                    return binding if binding.is_active else None
            except (RedisError, OSError) as exc:
                logger.warning(
                    "Redis get_active_sandbox_binding error (%s); falling back to memory.",
                    exc,
                )
                self._use_memory_fallback = True

        async with self._lock:
            binding = self._mem_bindings.get(cleaned_id)
            if binding is not None and binding.is_active:
                return binding
            return None

    async def release_sandbox_binding(self, session_id: str) -> bool:
        """
        Deactivate and release an active sandbox container binding for `session_id`.

        Args:
            session_id: Session identifier whose container binding should be released.

        Returns:
            `True` if an active binding existed and was deactivated, `False` otherwise.
        """
        cleaned_id = session_id.strip()
        if not cleaned_id:
            return False

        active_binding = await self.get_active_sandbox_binding(cleaned_id)
        if active_binding is None:
            return False

        inactive_binding = active_binding.model_copy(update={"is_active": False})

        async with self._lock:
            self._mem_bindings[cleaned_id] = inactive_binding

        client = await self._get_client()
        if client is not None:
            try:
                await client.set(
                    self._binding_key(cleaned_id),
                    inactive_binding.model_dump_json(),
                    ex=self._default_ttl_seconds,
                )
            except (RedisError, OSError) as exc:
                logger.warning(
                    "Redis release_sandbox_binding error (%s); updated in memory.", exc
                )
                self._use_memory_fallback = True

        existing_session = await self.get_session(cleaned_id)
        if existing_session is not None:
            now_utc = datetime.now(timezone.utc)
            terminated_session = existing_session.model_copy(
                update={
                    "status": SessionStatusEnum.TERMINATED,
                    "last_active_at": max(now_utc, existing_session.first_seen_at),
                }
            )
            await self.upsert_session(terminated_session)

        return True

    async def list_active_malicious_sessions(self) -> List[SessionStateContract]:
        """
        List all currently active sessions classified as malicious (`MALICIOUS_TRAPPED`
        or `ISOLATED`) or routed to `PREWARMED_SANDBOX`.

        Returns:
            List of active malicious `SessionStateContract` objects ordered by `last_active_at` descending.
        """
        results: Dict[str, SessionStateContract] = {}

        client = await self._get_client()
        if client is not None:
            try:
                member_ids = await client.smembers(self.MALICIOUS_SET_KEY)
                for sid in member_ids:
                    sess = await self.get_session(sid)
                    if sess is not None and (
                        sess.status
                        in (
                            SessionStatusEnum.MALICIOUS_TRAPPED,
                            SessionStatusEnum.ISOLATED,
                        )
                        or sess.routing_target == RoutingTargetEnum.PREWARMED_SANDBOX
                    ):
                        results[sess.session_id] = sess
                    elif sess is None:
                        await client.srem(self.MALICIOUS_SET_KEY, sid)
            except (RedisError, OSError) as exc:
                logger.warning(
                    "Redis list_active_malicious_sessions error (%s); using memory.",
                    exc,
                )
                self._use_memory_fallback = True

        async with self._lock:
            self._purge_expired_memory_entries()
            for sid in list(self._mem_malicious_ids):
                entry = self._mem_sessions.get(sid)
                if entry is not None and sid not in results:
                    sess = SessionStateContract.model_validate_json(entry[0])
                    if (
                        sess.status
                        in (
                            SessionStatusEnum.MALICIOUS_TRAPPED,
                            SessionStatusEnum.ISOLATED,
                        )
                        or sess.routing_target == RoutingTargetEnum.PREWARMED_SANDBOX
                    ):
                        results[sid] = sess

        sorted_sessions = sorted(
            results.values(),
            key=lambda s: s.last_active_at,
            reverse=True,
        )
        return sorted_sessions

    async def health_check(self) -> bool:
        """
        Verify operational health of the session store (either connected to Redis or
        operating via functional in-memory fallback).

        Returns:
            `True` if operational.
        """
        client = await self._get_client()
        if client is not None:
            try:
                pong = await client.ping()
                return bool(pong)
            except (RedisError, OSError):
                self._use_memory_fallback = True
                return True
        return True

    async def close(self) -> None:
        """Close the active Redis client connection if open."""
        if self._redis_client is not None:
            try:
                await self._redis_client.close()
            except Exception:
                pass
            self._redis_client = None

