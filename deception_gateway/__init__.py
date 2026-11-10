"""
Deception Gateway Package (`deception_gateway`).

Exports the Layer 1 FastAPI reverse-proxy application (`app`), router (`gateway_router`),
and core perimeter classification components (`RedisCacheVerifier`, `AttackDetector`,
`TrafficClassifier`, `MaliciousSessionRouter`).
"""

from deception_gateway.attack_detector import (
    AttackDetectionOutcome,
    AttackDetector,
)
from deception_gateway.gateway_router import (
    attack_detector,
    forward_legitimate_request,
    gateway_health_check,
    gateway_metrics,
    gateway_router,
    malicious_session_router,
    process_gateway_request,
    redis_cache_verifier,
    traffic_classifier,
)
from deception_gateway.main import app, gateway_lifespan
from deception_gateway.malicious_session_router import MaliciousSessionRouter
from deception_gateway.redis_cache_verifier import RedisCacheVerifier
from deception_gateway.traffic_classifier import (
    TrafficClassificationDecision,
    TrafficClassifier,
)

__all__ = [
    "app",
    "gateway_lifespan",
    "gateway_router",
    "gateway_health_check",
    "gateway_metrics",
    "forward_legitimate_request",
    "process_gateway_request",
    # Classes & Dataclasses
    "RedisCacheVerifier",
    "AttackDetector",
    "AttackDetectionOutcome",
    "TrafficClassifier",
    "TrafficClassificationDecision",
    "MaliciousSessionRouter",
    # Singletons
    "redis_cache_verifier",
    "attack_detector",
    "traffic_classifier",
    "malicious_session_router",
]
