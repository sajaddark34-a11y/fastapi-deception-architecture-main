"""
Honey Token Request Inspector and Validator (`honey_token_injector.token_validator`).

Inspects incoming HTTP requests (headers, `Authorization` bearer/API keys, cookies,
query parameters, and URL paths) against issued `HoneyTokenCreateContract` records
and HMAC-SHA256 signatures, returning a validated `HoneyTokenValidationContract`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Mapping, Optional

from honey_token_injector.fake_header_generator import (
    HEADER_LURE_TEMPLATES,
    FakeHeaderGenerator,
)
from honey_token_injector.fake_url_generator import (
    DECOY_ENDPOINT_CATALOG,
    FakeUrlGenerator,
)
from shared_contracts.honey_token_schema import (
    HoneyTokenCreateContract,
    HoneyTokenValidationContract,
)


class HoneyTokenValidator:
    """
    Validates incoming HTTP request telemetry against active honey tokens,
    monitored decoy endpoints, and cryptographic HMAC-SHA256 decoy signatures.
    """

    MONITORED_HEADER_NAMES = {
        hdr.lower() for hdr, _, _ in HEADER_LURE_TEMPLATES
    } | {
        "x-api-key",
        "x-debug-token",
        "x-internal-token",
    }

    MONITORED_COOKIE_NAMES = {
        "enterprise_debug_sid",
        "staging_admin_token",
        "debug_trace_session",
    }

    def __init__(
        self,
        header_generator: Optional[FakeHeaderGenerator] = None,
        url_generator: Optional[FakeUrlGenerator] = None,
    ) -> None:
        """
        Initialize the validator linked to `FakeHeaderGenerator` and `FakeUrlGenerator`.
        """
        self.header_generator = header_generator or FakeHeaderGenerator()
        self.url_generator = url_generator or FakeUrlGenerator()
        self._custom_tokens_by_value: Dict[str, HoneyTokenCreateContract] = {}
        self._custom_tokens_by_path: Dict[str, HoneyTokenCreateContract] = {}

    def register_token(self, token: HoneyTokenCreateContract) -> None:
        """
        Explicitly register a generated `HoneyTokenCreateContract` for instant lookup.
        """
        self._custom_tokens_by_value[token.decoy_value] = token
        self._custom_tokens_by_path[token.target_url_path] = token

    def validate_request(
        self,
        session_id: str,
        client_ip: str,
        request_path: str,
        request_method: str = "GET",
        headers: Optional[Mapping[str, str]] = None,
        query_params: Optional[Mapping[str, str]] = None,
        cookies: Optional[Mapping[str, str]] = None,
    ) -> HoneyTokenValidationContract:
        """
        Inspect all vectors of an incoming HTTP request and return a
        `HoneyTokenValidationContract` indicating whether any honey token was triggered.

        Args:
            session_id: Tracked session identifier.
            client_ip: Client source IPv4/IPv6 address.
            request_path: HTTP URI path (starting with `/`).
            request_method: HTTP verb (GET, POST, etc.).
            headers: Dictionary/Mapping of HTTP request headers.
            query_params: Dictionary/Mapping of URL query parameters.
            cookies: Dictionary/Mapping of HTTP cookies.

        Returns:
            Validated `HoneyTokenValidationContract` (`is_triggered=True` if tripped).
        """
        now_utc = datetime.now(timezone.utc)
        norm_path = request_path.split("?")[0].strip() if request_path else "/"
        if not norm_path.startswith("/"):
            norm_path = f"/{norm_path}"
        norm_method = (request_method or "GET").strip().upper()

        hdr_map = {str(k).strip(): str(v).strip() for k, v in (headers or {}).items()}
        qry_map = {
            str(k).strip(): str(v).strip() for k, v in (query_params or {}).items()
        }
        ck_map = {str(k).strip(): str(v).strip() for k, v in (cookies or {}).items()}

        # 1. Inspect decoy URL paths first
        if norm_path in self._custom_tokens_by_path:
            tok = self._custom_tokens_by_path[norm_path]
            return HoneyTokenValidationContract(
                token_id=tok.token_id,
                is_triggered=True,
                triggered_by_ip=client_ip,
                session_id=session_id,
                request_path=norm_path,
                request_method=norm_method,
                matched_value=norm_path,
                detected_at=now_utc,
            )

        matched_path_token_id = self.url_generator.match_decoy_path(norm_path)
        if matched_path_token_id is not None:
            return HoneyTokenValidationContract(
                token_id=matched_path_token_id,
                is_triggered=True,
                triggered_by_ip=client_ip,
                session_id=session_id,
                request_path=norm_path,
                request_method=norm_method,
                matched_value=norm_path,
                detected_at=now_utc,
            )

        # 2. Inspect HTTP headers (including Authorization and custom decoy headers)
        for h_name, h_val in hdr_map.items():
            if not h_val:
                continue

            if h_val in self._custom_tokens_by_value:
                tok = self._custom_tokens_by_value[h_val]
                return HoneyTokenValidationContract(
                    token_id=tok.token_id,
                    is_triggered=True,
                    triggered_by_ip=client_ip,
                    session_id=session_id,
                    request_path=norm_path,
                    request_method=norm_method,
                    matched_value=h_val,
                    detected_at=now_utc,
                )

            candidate_values = [h_val]
            if h_name.lower() == "authorization" and " " in h_val:
                candidate_values.append(h_val.split(" ", 1)[1].strip())

            for candidate in candidate_values:
                verified_hdr_id = self.header_generator.verify_signed_decoy_value(
                    candidate
                )
                if verified_hdr_id:
                    return HoneyTokenValidationContract(
                        token_id=verified_hdr_id,
                        is_triggered=True,
                        triggered_by_ip=client_ip,
                        session_id=session_id,
                        request_path=norm_path,
                        request_method=norm_method,
                        matched_value=candidate,
                        detected_at=now_utc,
                    )

                verified_key_id = self.url_generator.verify_fake_api_key(candidate)
                if verified_key_id:
                    return HoneyTokenValidationContract(
                        token_id=verified_key_id,
                        is_triggered=True,
                        triggered_by_ip=client_ip,
                        session_id=session_id,
                        request_path=norm_path,
                        request_method=norm_method,
                        matched_value=candidate,
                        detected_at=now_utc,
                    )

            # Even if an attacker modified the value of a dedicated trap header name
            if h_name.lower() in {hdr.lower() for hdr, _, _ in HEADER_LURE_TEMPLATES}:
                synthetic_id = f"htk_hdr_{h_name.lower().replace('-', '_')[:16]}"
                return HoneyTokenValidationContract(
                    token_id=synthetic_id,
                    is_triggered=True,
                    triggered_by_ip=client_ip,
                    session_id=session_id,
                    request_path=norm_path,
                    request_method=norm_method,
                    matched_value=f"{h_name}: {h_val}",
                    detected_at=now_utc,
                )

        # 3. Inspect HTTP Cookies
        for c_name, c_val in ck_map.items():
            if not c_val:
                continue
            if c_val in self._custom_tokens_by_value:
                tok = self._custom_tokens_by_value[c_val]
                return HoneyTokenValidationContract(
                    token_id=tok.token_id,
                    is_triggered=True,
                    triggered_by_ip=client_ip,
                    session_id=session_id,
                    request_path=norm_path,
                    request_method=norm_method,
                    matched_value=c_val,
                    detected_at=now_utc,
                )

            verified_cookie_id = self.header_generator.verify_signed_decoy_value(c_val)
            if verified_cookie_id:
                return HoneyTokenValidationContract(
                    token_id=verified_cookie_id,
                    is_triggered=True,
                    triggered_by_ip=client_ip,
                    session_id=session_id,
                    request_path=norm_path,
                    request_method=norm_method,
                    matched_value=c_val,
                    detected_at=now_utc,
                )

            if c_name.lower() in self.MONITORED_COOKIE_NAMES:
                return HoneyTokenValidationContract(
                    token_id="htk_cookie_decoy_sid",
                    is_triggered=True,
                    triggered_by_ip=client_ip,
                    session_id=session_id,
                    request_path=norm_path,
                    request_method=norm_method,
                    matched_value=f"{c_name}={c_val}",
                    detected_at=now_utc,
                )

        # 4. Inspect Query Parameters
        for q_name, q_val in qry_map.items():
            if not q_val:
                continue
            verified_q_hdr = self.header_generator.verify_signed_decoy_value(q_val)
            if verified_q_hdr:
                return HoneyTokenValidationContract(
                    token_id=verified_q_hdr,
                    is_triggered=True,
                    triggered_by_ip=client_ip,
                    session_id=session_id,
                    request_path=norm_path,
                    request_method=norm_method,
                    matched_value=q_val,
                    detected_at=now_utc,
                )
            verified_q_key = self.url_generator.verify_fake_api_key(q_val)
            if verified_q_key:
                return HoneyTokenValidationContract(
                    token_id=verified_q_key,
                    is_triggered=True,
                    triggered_by_ip=client_ip,
                    session_id=session_id,
                    request_path=norm_path,
                    request_method=norm_method,
                    matched_value=q_val,
                    detected_at=now_utc,
                )
            if q_name.lower() in {"access_ticket", "trace_token", "debug_token"}:
                return HoneyTokenValidationContract(
                    token_id=f"htk_qry_{q_name.lower()}",
                    is_triggered=True,
                    triggered_by_ip=client_ip,
                    session_id=session_id,
                    request_path=norm_path,
                    request_method=norm_method,
                    matched_value=f"{q_name}={q_val}",
                    detected_at=now_utc,
                )

        # Benign result (not triggered)
        default_token_ref = DECOY_ENDPOINT_CATALOG[0][1]
        return HoneyTokenValidationContract(
            token_id="htk_none_benign",
            is_triggered=False,
            triggered_by_ip=client_ip,
            session_id=session_id,
            request_path=norm_path,
            request_method=norm_method,
            matched_value=default_token_ref,
            detected_at=now_utc,
        )

    def inspect_for_triggered_token(
        self,
        session_id: str,
        client_ip: str,
        request_path: str,
        request_method: str = "GET",
        headers: Optional[Mapping[str, str]] = None,
        query_params: Optional[Mapping[str, str]] = None,
        cookies: Optional[Mapping[str, str]] = None,
    ) -> Optional[HoneyTokenValidationContract]:
        """
        Convenience wrapper returning the `HoneyTokenValidationContract` only when
        `is_triggered` is `True`, or `None` for benign requests.
        """
        result = self.validate_request(
            session_id=session_id,
            client_ip=client_ip,
            request_path=request_path,
            request_method=request_method,
            headers=headers,
            query_params=query_params,
            cookies=cookies,
        )
        return result if result.is_triggered else None
