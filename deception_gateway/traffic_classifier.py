"""
Perimeter Traffic Classifier (`deception_gateway.traffic_classifier`).

Coordinates `RedisCacheVerifier` and `AttackDetector` on every incoming HTTP request
to determine whether the session should be routed to `CORE_WEB_APP` or transparently
diverted to `PREWARMED_SANDBOX`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping, Optional

from deception_gateway.attack_detector import (
    AttackDetectionOutcome,
    AttackDetector,
)
from deception_gateway.redis_cache_verifier import RedisCacheVerifier
from shared_contracts.alert_schema import SecurityAlertContract
from shared_contracts.session_schema import (
    RoutingTargetEnum,
    SandboxBindingContract,
    SessionStateContract,
)


@dataclass
class TrafficClassificationDecision:
    """
    Complete routing decision returned by `TrafficClassifier.classify_request`.
    """

    session: SessionStateContract
    routing_target: RoutingTargetEnum
    is_malicious: bool
    was_previously_trapped: bool
    alert: Optional[SecurityAlertContract] = None
    sandbox_binding: Optional[SandboxBindingContract] = None
    reason: str = "Legitimate session routed to CORE_WEB_APP"


class TrafficClassifier:
    """
    Orchestrates real-time session cache verification and deep attack/honey-token
    detection to classify and route incoming client traffic.
    """

    def __init__(
        self,
        cache_verifier: Optional[RedisCacheVerifier] = None,
        attack_detector: Optional[AttackDetector] = None,
    ) -> None:
        """
        Initialize the traffic classifier with `RedisCacheVerifier` and `AttackDetector`.
        """
        self.cache_verifier: RedisCacheVerifier = (
            cache_verifier or RedisCacheVerifier()
        )
        self.attack_detector: AttackDetector = attack_detector or AttackDetector()

    @staticmethod
    def _derive_container_id(session_id: str) -> str:
        """Deterministically assign a prewarmed honey container ID for a session."""
        digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:12]
        return f"honey_sbx_{digest}"

    async def classify_request(
        self,
        session_id: Optional[str],
        client_ip: str,
        request_path: str,
        request_method: str = "GET",
        headers: Optional[Mapping[str, str]] = None,
        query_params: Optional[Mapping[str, str]] = None,
        cookies: Optional[Mapping[str, str]] = None,
        body_text: str = "",
    ) -> TrafficClassificationDecision:
        """
        Evaluate an incoming HTTP request and decide its `RoutingTargetEnum`:
        1. Verify existing session state in Redis via `RedisCacheVerifier`.
        2. If already trapped (`MALICIOUS_TRAPPED` / `ISOLATED`), keep pinned to
           `PREWARMED_SANDBOX` while still logging any further exploit payloads.
        3. Otherwise inspect the request via `AttackDetector`. If a honey token or
           attack signature is detected, escalate the session in Redis (`risk_score=100.0`,
           `status=MALICIOUS_TRAPPED`, `routing_target=PREWARMED_SANDBOX`).
        4. If benign, route to `CORE_WEB_APP`.
        """
        hdr_map = {str(k).strip(): str(v).strip() for k, v in (headers or {}).items()}
        user_agent = (
            hdr_map.get("User-Agent")
            or hdr_map.get("user-agent")
            or "Mozilla/5.0 (Enterprise Client)"
        )

        session, is_already_malicious, active_binding = (
            await self.cache_verifier.verify_session_status(
                session_id=session_id,
                client_ip=client_ip,
                user_agent=user_agent,
            )
        )

        # If session is already trapped in Redis, immediately pin to PREWARMED_SANDBOX
        if is_already_malicious:
            detection_outcome: AttackDetectionOutcome = (
                await self.attack_detector.inspect_request(
                    session_id=session.session_id,
                    client_ip=session.client_ip,
                    request_path=request_path,
                    request_method=request_method,
                    headers=hdr_map,
                    query_params=query_params,
                    cookies=cookies,
                    body_text=body_text,
                )
            )
            return TrafficClassificationDecision(
                session=session,
                routing_target=RoutingTargetEnum.PREWARMED_SANDBOX,
                is_malicious=True,
                was_previously_trapped=True,
                alert=detection_outcome.alert,
                sandbox_binding=active_binding,
                reason="Session previously flagged as malicious in Redis; pinned to PREWARMED_SANDBOX.",
            )

        # Evaluate request through AttackDetector (Honey Token Validator + Threat Signatures)
        detection_outcome = await self.attack_detector.inspect_request(
            session_id=session.session_id,
            client_ip=session.client_ip,
            request_path=request_path,
            request_method=request_method,
            headers=hdr_map,
            query_params=query_params,
            cookies=cookies,
            body_text=body_text,
        )

        if detection_outcome.is_malicious:
            triggered_token_id = (
                detection_outcome.token_validation.token_id
                if (
                    detection_outcome.token_validation
                    and detection_outcome.token_validation.is_triggered
                )
                else None
            )
            container_id = (
                session.assigned_container_id
                or self._derive_container_id(session.session_id)
            )
            escalated_session = (
                await self.cache_verifier.store.escalate_session_to_malicious(
                    session_id=session.session_id,
                    triggered_token_id=triggered_token_id,
                    assigned_container_id=container_id,
                    risk_score=100.0,
                )
            )
            final_session = escalated_session or session
            return TrafficClassificationDecision(
                session=final_session,
                routing_target=RoutingTargetEnum.PREWARMED_SANDBOX,
                is_malicious=True,
                was_previously_trapped=False,
                alert=detection_outcome.alert,
                sandbox_binding=active_binding,
                reason=detection_outcome.reason,
            )

        return TrafficClassificationDecision(
            session=session,
            routing_target=RoutingTargetEnum.CORE_WEB_APP,
            is_malicious=False,
            was_previously_trapped=False,
            alert=None,
            sandbox_binding=None,
            reason="Legitimate traffic routed to CORE_WEB_APP.",
        )
