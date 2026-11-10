"""
Honey Token Injector Package (`honey_token_injector`).

Exports cryptographic fake header generators (`FakeHeaderGenerator`), decoy URL and
API key generators (`FakeUrlGenerator`), request validators (`HoneyTokenValidator`),
and response injection middleware (`HoneyTokenInjectorMiddleware`), along with
shared singleton instances.
"""

from honey_token_injector.fake_header_generator import (
    DEFAULT_HONEY_HMAC_SECRET,
    HEADER_LURE_TEMPLATES,
    FakeHeaderGenerator,
)
from honey_token_injector.fake_url_generator import (
    DECOY_ENDPOINT_CATALOG,
    DEFAULT_HONEY_URL_SECRET,
    FakeUrlGenerator,
)
from honey_token_injector.injector_middleware import HoneyTokenInjectorMiddleware
from honey_token_injector.token_validator import HoneyTokenValidator

fake_header_generator = FakeHeaderGenerator()
fake_url_generator = FakeUrlGenerator()
honey_token_validator = HoneyTokenValidator(
    header_generator=fake_header_generator,
    url_generator=fake_url_generator,
)
honey_token_injector_middleware = HoneyTokenInjectorMiddleware(
    header_generator=fake_header_generator,
    url_generator=fake_url_generator,
    token_validator=honey_token_validator,
)

__all__ = [
    # Constants & Catalogs
    "DEFAULT_HONEY_HMAC_SECRET",
    "DEFAULT_HONEY_URL_SECRET",
    "HEADER_LURE_TEMPLATES",
    "DECOY_ENDPOINT_CATALOG",
    # Classes
    "FakeHeaderGenerator",
    "FakeUrlGenerator",
    "HoneyTokenValidator",
    "HoneyTokenInjectorMiddleware",
    # Singletons
    "fake_header_generator",
    "fake_url_generator",
    "honey_token_validator",
    "honey_token_injector_middleware",
]
