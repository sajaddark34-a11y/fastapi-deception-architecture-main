"""
Honey Token Injection Middleware and Response Enricher
(`honey_token_injector.injector_middleware`).

Provides `HoneyTokenInjectorMiddleware` (compatible with FastAPI/Starlette) and
direct payload/header enrichment helpers for `deception_gateway` to embed fake
HTTP headers, decoy cookies, fake API keys, and hidden decoy URLs into outgoing
legitimate responses without corrupting original JSON or HTML structures.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, List, MutableMapping, Optional, Tuple

try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_routes import Request  # type: ignore[assignment]
    from core_web_app.main import Response  # type: ignore[assignment]

    class BaseHTTPMiddleware:  # type: ignore[no-redef]
        def __init__(self, app: Any, dispatch: Optional[Callable[..., Any]] = None) -> None:
            self.app = app
            self.dispatch_func = dispatch

from honey_token_injector.fake_header_generator import FakeHeaderGenerator
from honey_token_injector.fake_url_generator import FakeUrlGenerator
from honey_token_injector.token_validator import HoneyTokenValidator
from shared_contracts.honey_token_schema import (
    HoneyTokenCreateContract,
    InjectionVectorEnum,
)

logger = logging.getLogger(__name__)


class HoneyTokenInjectorMiddleware(BaseHTTPMiddleware):
    """
    ASGI/FastAPI middleware and Reverse-Proxy response enricher that dynamically
    embeds cryptographic honey tokens into outgoing HTTP responses.
    """

    def __init__(
        self,
        app: Any = None,
        header_generator: Optional[FakeHeaderGenerator] = None,
        url_generator: Optional[FakeUrlGenerator] = None,
        token_validator: Optional[HoneyTokenValidator] = None,
        inject_json_lures: bool = True,
    ) -> None:
        if app is not None:
            super().__init__(app)
        self.header_generator = header_generator or FakeHeaderGenerator()
        self.url_generator = url_generator or FakeUrlGenerator()
        self.token_validator = token_validator or HoneyTokenValidator(
            header_generator=self.header_generator,
            url_generator=self.url_generator,
        )
        self.inject_json_lures = inject_json_lures

    def inject_headers_into_mapping(
        self, headers: MutableMapping[str, str]
    ) -> List[HoneyTokenCreateContract]:
        """
        Embed signed fake HTTP headers and a decoy session cookie into a mutable
        response headers mapping, registering all generated tokens with the validator.
        """
        injected_tokens: List[HoneyTokenCreateContract] = []

        header_token = self.header_generator.generate_header_token(
            header_name="X-Internal-Debug-Token",
            target_url_path="/api/v1/internal/debug-console",
        )
        staging_token = self.header_generator.generate_header_token(
            header_name="X-Staging-API-Key",
            target_url_path="/api/v1/internal/vault-keys",
        )

        headers[header_token.header_or_field_name] = header_token.decoy_value
        headers[staging_token.header_or_field_name] = staging_token.decoy_value

        self.token_validator.register_token(header_token)
        self.token_validator.register_token(staging_token)
        injected_tokens.extend([header_token, staging_token])
        return injected_tokens

    def enrich_json_payload(
        self, payload: Any
    ) -> Tuple[Any, List[HoneyTokenCreateContract]]:
        """
        Safely embed decoy URL and fake API key lures into a JSON dictionary without
        modifying or breaking any existing application keys.
        """
        injected: List[HoneyTokenCreateContract] = []
        if not isinstance(payload, dict) or not self.inject_json_lures:
            return payload, injected

        enriched = dict(payload)
        url_lure = self.url_generator.generate_hidden_url_token(
            target_url_path="/api/v1/internal/vault-keys",
            field_name="_debug_vault_endpoint",
            injection_vector=InjectionVectorEnum.JSON_PAYLOAD_FIELD,
        )
        key_lure = self.url_generator.generate_fake_api_key_token(
            field_name="_staging_api_key",
            target_url_path="/admin/debug/env-dump",
        )

        self.token_validator.register_token(url_lure)
        self.token_validator.register_token(key_lure)
        injected.extend([url_lure, key_lure])

        if "_deception_meta" not in enriched and "_debug_links" not in enriched:
            enriched["_debug_links"] = {
                url_lure.header_or_field_name: url_lure.decoy_value,
                key_lure.header_or_field_name: key_lure.decoy_value,
            }

        return enriched, injected

    def enrich_raw_response(
        self,
        body_bytes: bytes,
        status_code: int,
        headers: Dict[str, str],
        content_type: str = "application/json",
    ) -> Tuple[bytes, Dict[str, str], List[HoneyTokenCreateContract]]:
        """
        Enrich raw response bytes and headers from an upstream service (`core_web_app`),
        preserving valid JSON or HTML structure.
        """
        updated_headers = dict(headers)
        tokens = self.inject_headers_into_mapping(updated_headers)

        if status_code >= 400 or not body_bytes:
            return body_bytes, updated_headers, tokens

        ctype_lower = (content_type or "").lower()
        if "application/json" in ctype_lower and self.inject_json_lures:
            try:
                parsed = json.loads(body_bytes.decode("utf-8"))
                if isinstance(parsed, dict):
                    enriched_dict, json_tokens = self.enrich_json_payload(parsed)
                    tokens.extend(json_tokens)
                    new_body = json.dumps(enriched_dict).encode("utf-8")
                    updated_headers["content-length"] = str(len(new_body))
                    return new_body, updated_headers, tokens
            except Exception as exc:
                logger.debug("Skipped JSON honey token enrichment: %s", exc)

        elif "text/html" in ctype_lower:
            try:
                html_lure = self.url_generator.generate_hidden_url_token(
                    target_url_path="/admin/debug/env-dump",
                    field_name="html_debug_comment",
                    injection_vector=InjectionVectorEnum.HTML_COMMENT_LINK,
                )
                self.token_validator.register_token(html_lure)
                tokens.append(html_lure)
                new_body = body_bytes + f"\n{html_lure.decoy_value}\n".encode("utf-8")
                updated_headers["content-length"] = str(len(new_body))
                return new_body, updated_headers, tokens
            except Exception as exc:
                logger.debug("Skipped HTML honey token enrichment: %s", exc)

        return body_bytes, updated_headers, tokens

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        """
        FastAPI/Starlette middleware `dispatch` hook that injects decoy headers into
        every outgoing HTTP response.
        """
        response = await call_next(request)
        try:
            self.inject_headers_into_mapping(response.headers)
        except Exception as exc:
            logger.debug("Header injection skipped in middleware: %s", exc)
        return response
