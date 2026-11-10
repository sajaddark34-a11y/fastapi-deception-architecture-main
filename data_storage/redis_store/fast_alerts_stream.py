"""
Asynchronous Redis Streams and Pub/Sub Engine for Real-Time Security Alerts and Telemetry.

Streams `SecurityAlertContract` and `TelemetryStreamEnvelope` payloads from the
Deception Gateway and Forensic Extraction Engine to the Defender SOC Dashboard,
with full in-memory `asyncio.Queue` and ring-buffer fallback for local execution.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections import deque
from typing import AsyncGenerator, Deque, Dict, List, Optional, Set

from shared_contracts.alert_schema import (
    AlertSeverityEnum,
    SecurityAlertContract,
)
from shared_contracts.telemetry_schema import TelemetryStreamEnvelope

try:
    import redis.asyncio as aioredis
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover
    aioredis = None  # type: ignore[assignment]

    class RedisError(Exception):  # type: ignore[no-redef]
        """Fallback exception when redis package is unavailable."""


logger = logging.getLogger(__name__)

_SEVERITY_RANK: Dict[AlertSeverityEnum, int] = {
    AlertSeverityEnum.LOW: 1,
    AlertSeverityEnum.MEDIUM: 2,
    AlertSeverityEnum.HIGH: 3,
    AlertSeverityEnum.CRITICAL: 4,
}


class FastAlertsStream:
    """
    Real-time alert and forensic telemetry broadcaster backed by Redis Streams (`XADD`/`XREVRANGE`)
    and Redis Pub/Sub (`PUBLISH`/`SUBSCRIBE`), with an automatic in-memory queue fallback.
    """

    ALERTS_STREAM_KEY: str = "deception:streams:alerts"
    ALERTS_PUBSUB_CHANNEL: str = "deception:pubsub:alerts"
    TELEMETRY_STREAM_KEY: str = "deception:streams:telemetry"
    TELEMETRY_PUBSUB_CHANNEL: str = "deception:pubsub:telemetry"

    def __init__(
        self,
        redis_url: Optional[str] = None,
        max_stream_length: int = 2000,
    ) -> None:
        """
        Initialize the fast alerts stream manager.

        Args:
            redis_url: Optional Redis connection URI. Defaults to `REDIS_URL` env var
                or constructs from `REDIS_HOST` and `REDIS_PORT`.
            max_stream_length: Maximum entries retained in the Redis stream and memory buffer.
        """
        host = os.getenv("REDIS_HOST", "redis_store")
        port = os.getenv("REDIS_PORT", "6379")
        self._redis_url: str = redis_url or os.getenv(
            "REDIS_URL", f"redis://{host}:{port}/0"
        )
        self._max_stream_length: int = max_stream_length
        self._redis_client: Optional["aioredis.Redis"] = None
        self._use_memory_fallback: bool = aioredis is None
        self._lock: asyncio.Lock = asyncio.Lock()
        self._seq_counter: int = 0

        # In-memory ring buffers and subscriber queues
        self._mem_alerts: Deque[SecurityAlertContract] = deque(maxlen=max_stream_length)
        self._mem_telemetry: Deque[TelemetryStreamEnvelope] = deque(
            maxlen=max_stream_length
        )
        self._alert_subscribers: Set[asyncio.Queue[SecurityAlertContract]] = set()
        self._telemetry_subscribers: Set[asyncio.Queue[TelemetryStreamEnvelope]] = set()

    async def _get_client(self) -> Optional["aioredis.Redis"]:
        """Return an active Redis async client or fall back to in-memory structures."""
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
                    "Redis unreachable at %s (%s). Switching FastAlertsStream to in-memory fallback.",
                    self._redis_url,
                    exc,
                )
                self._use_memory_fallback = True
                self._redis_client = None
                return None

        return self._redis_client

    def _next_fallback_stream_id(self) -> str:
        """Generate a Redis-style monotonic stream ID (`<ms_timestamp>-<seq>`)."""
        self._seq_counter += 1
        ms = int(time.time() * 1000)
        return f"{ms}-{self._seq_counter}"

    async def publish_alert(self, alert: SecurityAlertContract) -> str:
        """
        Publish a `SecurityAlertContract` to the Redis Stream and real-time Pub/Sub
        channel, while also updating in-memory buffers and local async subscribers.

        Args:
            alert: Validated `SecurityAlertContract` instance.

        Returns:
            The Redis Stream entry ID (or fallback stream ID).
        """
        payload_json = alert.model_dump_json()
        stream_id: Optional[str] = None

        async with self._lock:
            self._mem_alerts.append(alert)
            fallback_id = self._next_fallback_stream_id()
            for sub_queue in list(self._alert_subscribers):
                try:
                    sub_queue.put_nowait(alert)
                except asyncio.QueueFull:
                    try:
                        sub_queue.get_nowait()
                        sub_queue.put_nowait(alert)
                    except Exception:
                        pass

        client = await self._get_client()
        if client is not None:
            try:
                stream_id = await client.xadd(
                    self.ALERTS_STREAM_KEY,
                    {
                        "alert_id": alert.alert_id,
                        "session_id": alert.session_id,
                        "severity": alert.severity.value,
                        "category": alert.category.value,
                        "source_ip": alert.source_ip,
                        "payload": payload_json,
                    },
                    maxlen=self._max_stream_length,
                    approximate=True,
                )
                await client.publish(self.ALERTS_PUBSUB_CHANNEL, payload_json)
            except (RedisError, OSError) as exc:
                logger.warning(
                    "Redis publish_alert error (%s); published via memory queue.", exc
                )
                self._use_memory_fallback = True

        return str(stream_id or fallback_id)

    async def publish_telemetry_envelope(
        self, envelope: TelemetryStreamEnvelope
    ) -> str:
        """
        Publish a `TelemetryStreamEnvelope` containing attacker command or network/eBPF
        telemetry to the Redis Stream and Pub/Sub channel.

        Args:
            envelope: Validated `TelemetryStreamEnvelope` instance.

        Returns:
            The Redis Stream entry ID (or fallback stream ID).
        """
        payload_json = envelope.model_dump_json()
        stream_id: Optional[str] = None

        async with self._lock:
            self._mem_telemetry.append(envelope)
            fallback_id = self._next_fallback_stream_id()
            for sub_queue in list(self._telemetry_subscribers):
                try:
                    sub_queue.put_nowait(envelope)
                except asyncio.QueueFull:
                    try:
                        sub_queue.get_nowait()
                        sub_queue.put_nowait(envelope)
                    except Exception:
                        pass

        client = await self._get_client()
        if client is not None:
            try:
                stream_id = await client.xadd(
                    self.TELEMETRY_STREAM_KEY,
                    {
                        "envelope_id": envelope.envelope_id,
                        "session_id": envelope.session_id,
                        "container_id": envelope.container_id,
                        "source": envelope.source.value,
                        "payload": payload_json,
                    },
                    maxlen=self._max_stream_length,
                    approximate=True,
                )
                await client.publish(self.TELEMETRY_PUBSUB_CHANNEL, payload_json)
            except (RedisError, OSError) as exc:
                logger.warning(
                    "Redis publish_telemetry_envelope error (%s); published via memory queue.",
                    exc,
                )
                self._use_memory_fallback = True

        return str(stream_id or fallback_id)

    async def get_recent_alerts(
        self,
        limit: int = 50,
        min_severity: Optional[AlertSeverityEnum] = None,
    ) -> List[SecurityAlertContract]:
        """
        Retrieve the most recent security alerts in reverse chronological order,
        optionally filtered by a minimum severity threshold.

        Args:
            limit: Maximum number of alerts to return (default 50).
            min_severity: Optional minimum `AlertSeverityEnum` filter.

        Returns:
            List of `SecurityAlertContract` objects (newest first).
        """
        effective_limit = max(1, limit)
        min_rank = _SEVERITY_RANK.get(min_severity, 0) if min_severity else 0
        collected: Dict[str, SecurityAlertContract] = {}

        client = await self._get_client()
        if client is not None:
            try:
                fetch_count = effective_limit * 4 if min_severity else effective_limit
                entries = await client.xrevrange(
                    self.ALERTS_STREAM_KEY,
                    max="+",
                    min="-",
                    count=fetch_count,
                )
                for _entry_id, fields in entries:
                    raw_payload = fields.get("payload")
                    if not raw_payload:
                        continue
                    alert = SecurityAlertContract.model_validate_json(raw_payload)
                    if _SEVERITY_RANK.get(alert.severity, 0) >= min_rank:
                        collected[alert.alert_id] = alert
                        if len(collected) >= effective_limit:
                            break
            except (RedisError, OSError) as exc:
                logger.warning(
                    "Redis get_recent_alerts error (%s); reading from memory.", exc
                )
                self._use_memory_fallback = True

        async with self._lock:
            for alert in reversed(self._mem_alerts):
                if len(collected) >= effective_limit:
                    break
                if alert.alert_id not in collected:
                    if _SEVERITY_RANK.get(alert.severity, 0) >= min_rank:
                        collected[alert.alert_id] = alert

        sorted_alerts = sorted(
            collected.values(),
            key=lambda a: a.timestamp,
            reverse=True,
        )
        return sorted_alerts[:effective_limit]

    async def get_alerts_by_session(
        self, session_id: str
    ) -> List[SecurityAlertContract]:
        """
        Retrieve all security alerts associated with a specific `session_id`
        in chronological order.

        Args:
            session_id: Tracked session identifier.

        Returns:
            List of `SecurityAlertContract` instances for the given session.
        """
        cleaned_id = session_id.strip()
        if not cleaned_id:
            return []

        matched: Dict[str, SecurityAlertContract] = {}

        client = await self._get_client()
        if client is not None:
            try:
                entries = await client.xrange(
                    self.ALERTS_STREAM_KEY,
                    min="-",
                    max="+",
                    count=self._max_stream_length,
                )
                for _entry_id, fields in entries:
                    if fields.get("session_id") == cleaned_id:
                        raw_payload = fields.get("payload")
                        if raw_payload:
                            alert = SecurityAlertContract.model_validate_json(
                                raw_payload
                            )
                            matched[alert.alert_id] = alert
            except (RedisError, OSError) as exc:
                logger.warning(
                    "Redis get_alerts_by_session error (%s); reading from memory.", exc
                )
                self._use_memory_fallback = True

        async with self._lock:
            for alert in self._mem_alerts:
                if alert.session_id == cleaned_id and alert.alert_id not in matched:
                    matched[alert.alert_id] = alert

        return sorted(matched.values(), key=lambda a: a.timestamp)

    async def subscribe_alerts(
        self,
    ) -> AsyncGenerator[SecurityAlertContract, None]:
        """
        Asynchronous generator yielding live `SecurityAlertContract` instances as they
        are published, suitable for streaming over WebSockets or Server-Sent Events (SSE)
        in the Defender SOC Dashboard.
        """
        client = await self._get_client()
        if client is not None:
            pubsub = client.pubsub()
            try:
                await pubsub.subscribe(self.ALERTS_PUBSUB_CHANNEL)
                async for message in pubsub.listen():
                    if message and message.get("type") == "message":
                        data = message.get("data")
                        if isinstance(data, str) and data:
                            yield SecurityAlertContract.model_validate_json(data)
                return
            except (RedisError, OSError) as exc:
                logger.warning(
                    "Redis Pub/Sub interrupted (%s); switching subscriber to memory queue.",
                    exc,
                )
                self._use_memory_fallback = True
            finally:
                try:
                    await pubsub.unsubscribe(self.ALERTS_PUBSUB_CHANNEL)
                    await pubsub.close()
                except Exception:
                    pass

        queue: asyncio.Queue[SecurityAlertContract] = asyncio.Queue(maxsize=256)
        async with self._lock:
            self._alert_subscribers.add(queue)
        try:
            while True:
                alert = await queue.get()
                yield alert
        finally:
            async with self._lock:
                self._alert_subscribers.discard(queue)
