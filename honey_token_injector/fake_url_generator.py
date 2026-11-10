"""
Decoy URL and Fake API Key Generator (`honey_token_injector.fake_url_generator`).

Generates high-value decoy endpoints (`/api/v1/internal/vault-keys`,
`/admin/debug/env-dump`, `/api/v1/backup/db-snapshot`, `/api/v1/internal/debug-console`)
and signed fake API keys for embedding into outgoing JSON payloads and HTML comments.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Tuple

from shared_contracts.honey_token_schema import (
    HoneyTokenCreateContract,
    HoneyTokenTypeEnum,
    InjectionVectorEnum,
)

DEFAULT_HONEY_URL_SECRET: str = os.getenv(
    "HONEY_TOKEN_HMAC_SECRET",
    "deception_honey_token_hmac_sha256_master_secret_2026",
)

# Canonical decoy paths monitored by the Deception Gateway: (field_name, path)
DECOY_ENDPOINT_CATALOG: List[Tuple[str, str]] = [
    ("_debug_vault_endpoint", "/api/v1/internal/vault-keys"),
    ("_admin_Diagnostics_url", "/admin/debug/env-dump"),
    ("_backup_snapshot_uri", "/api/v1/backup/db-snapshot"),
    ("_internal_console_url", "/api/v1/internal/debug-console"),
    ("_staging_secrets_uri", "/internal/k8s/cluster-secrets"),
]


class FakeUrlGenerator:
    """
    Generates and registers `HIDDEN_DECOY_URL` and `FAKE_API_KEY` honey token
    contracts for embedding in JSON responses and HTML comment lures.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        default_ttl_hours: int = 24,
    ) -> None:
        """
        Initialize the decoy URL and fake API key generator.

        Args:
            secret_key: HMAC secret key for signing fake API keys and URL tokens.
            default_ttl_hours: Default token lifetime in hours.
        """
        self._secret_bytes: bytes = (
            secret_key or DEFAULT_HONEY_URL_SECRET
        ).encode("utf-8")
        self._default_ttl_hours: int = max(1, default_ttl_hours)
        self._issued_tokens: Dict[str, HoneyTokenCreateContract] = {}
        self._registered_decoy_paths: Dict[str, str] = {
            path: f"htk_path_{hashlib.sha256(path.encode('utf-8')).hexdigest()[:10]}"
            for _, path in DECOY_ENDPOINT_CATALOG
        }
        self._api_key_to_token_id: Dict[str, str] = {}

    def _sign_fragment(self, label: str) -> str:
        """Create a 12-character HMAC-SHA256 signature for URL/API key lures."""
        return hmac.new(
            self._secret_bytes, label.encode("utf-8"), hashlib.sha256
        ).hexdigest()[:12]

    def generate_hidden_url_token(
        self,
        target_url_path: Optional[str] = None,
        field_name: Optional[str] = None,
        injection_vector: InjectionVectorEnum = InjectionVectorEnum.JSON_PAYLOAD_FIELD,
        ttl_hours: Optional[int] = None,
    ) -> HoneyTokenCreateContract:
        """
        Generate a `HIDDEN_DECOY_URL` honey token contract pointing to a monitored
        trap endpoint.

        Args:
            target_url_path: Optional explicit trap path starting with `/`.
            field_name: Optional JSON field or HTML comment attribute name.
            injection_vector: Either `JSON_PAYLOAD_FIELD` or `HTML_COMMENT_LINK`.
            ttl_hours: Optional expiration window in hours.

        Returns:
            Validated `HoneyTokenCreateContract`.
        """
        idx = secrets.randbelow(len(DECOY_ENDPOINT_CATALOG))
        default_field, default_path = DECOY_ENDPOINT_CATALOG[idx]

        chosen_path = (target_url_path or default_path).strip()
        if not chosen_path.startswith("/"):
            chosen_path = f"/{chosen_path}"
        chosen_field = field_name or default_field

        short_id = secrets.token_hex(6)
        token_id = f"htk_{short_id}"
        sig = self._sign_fragment(f"{token_id}:{chosen_path}")

        if injection_vector == InjectionVectorEnum.HTML_COMMENT_LINK:
            decoy_value = (
                f"<!-- DEPRECATED STAGING ENDPOINT: {chosen_path}?trace_token={sig} -->"
            )
        else:
            decoy_value = f"{chosen_path}?access_ticket={sig}"

        now_utc = datetime.now(timezone.utc)
        expires_utc = now_utc + timedelta(
            hours=ttl_hours if ttl_hours is not None else self._default_ttl_hours
        )

        contract = HoneyTokenCreateContract(
            token_id=token_id,
            token_type=HoneyTokenTypeEnum.HIDDEN_DECOY_URL,
            injection_vector=injection_vector,
            header_or_field_name=chosen_field,
            decoy_value=decoy_value,
            target_url_path=chosen_path,
            created_at=now_utc,
            expires_at=expires_utc,
        )
        self._issued_tokens[contract.token_id] = contract
        self._registered_decoy_paths[chosen_path] = contract.token_id
        return contract

    def generate_fake_api_key_token(
        self,
        field_name: str = "_internal_service_api_key",
        target_url_path: str = "/api/v1/internal/vault-keys",
        ttl_hours: Optional[int] = None,
    ) -> HoneyTokenCreateContract:
        """
        Generate a `FAKE_API_KEY` honey token contract embedded inside JSON responses
        to lure credential harvesters.

        Args:
            field_name: JSON key name where the fake API key will be placed.
            target_url_path: Decoy endpoint associated with the fake API key.
            ttl_hours: Optional expiration lifetime in hours.

        Returns:
            Validated `HoneyTokenCreateContract`.
        """
        short_id = secrets.token_hex(6)
        token_id = f"htk_{short_id}"
        nonce = secrets.token_hex(4)
        sig = self._sign_fragment(f"{short_id}:{nonce}")
        decoy_api_key = f"ak_live_ent_{short_id}_{nonce}_{sig}"

        now_utc = datetime.now(timezone.utc)
        expires_utc = now_utc + timedelta(
            hours=ttl_hours if ttl_hours is not None else self._default_ttl_hours
        )

        contract = HoneyTokenCreateContract(
            token_id=token_id,
            token_type=HoneyTokenTypeEnum.FAKE_API_KEY,
            injection_vector=InjectionVectorEnum.JSON_PAYLOAD_FIELD,
            header_or_field_name=field_name,
            decoy_value=decoy_api_key,
            target_url_path=target_url_path,
            created_at=now_utc,
            expires_at=expires_utc,
        )
        self._issued_tokens[contract.token_id] = contract
        self._api_key_to_token_id[decoy_api_key] = contract.token_id
        self._registered_decoy_paths[target_url_path] = contract.token_id
        return contract

    def verify_fake_api_key(self, candidate_key: str) -> Optional[str]:
        """
        Verify if `candidate_key` is a fake API key issued by `FakeUrlGenerator`.

        Returns:
            Matching `token_id` if verified, else `None`.
        """
        if not candidate_key or not isinstance(candidate_key, str):
            return None

        cleaned = candidate_key.strip()
        if cleaned in self._api_key_to_token_id:
            return self._api_key_to_token_id[cleaned]

        if not cleaned.startswith("ak_live_ent_"):
            return None

        parts = cleaned.split("_")
        if len(parts) != 6:
            return None

        short_id, nonce, provided_sig = parts[3], parts[4], parts[5]
        expected_sig = self._sign_fragment(f"{short_id}:{nonce}")
        if hmac.compare_digest(expected_sig, provided_sig.lower()):
            return f"htk_{short_id}"
        return None

    def match_decoy_path(self, request_path: str) -> Optional[str]:
        """
        Check if `request_path` matches a registered decoy URL path.

        Returns:
            Associated `token_id` if matched, else `None`.
        """
        if not request_path:
            return None
        clean_path = request_path.split("?")[0].strip().rstrip("/") or "/"
        for decoy_path, token_id in self._registered_decoy_paths.items():
            normalized_decoy = decoy_path.rstrip("/") or "/"
            if clean_path == normalized_decoy or clean_path.startswith(
                f"{normalized_decoy}/"
            ):
                return token_id
        return None

    def get_registered_decoy_paths(self) -> Set[str]:
        """Return the set of all monitored decoy URL paths."""
        return set(self._registered_decoy_paths.keys())

    def get_issued_tokens(self) -> Dict[str, HoneyTokenCreateContract]:
        """Return a copy of all issued decoy URL and fake API key contracts."""
        return dict(self._issued_tokens)
