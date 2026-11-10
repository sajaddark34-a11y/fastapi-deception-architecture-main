"""
Authentication Subpackage for the Core Web Application (`core_web_app.authentication`).

Exports the authentication FastAPI router (`auth_router`), PBKDF2-HMAC password
utilities, JWT token handlers, and security dependencies.
"""

from core_web_app.authentication.auth_handler import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    bearer_security_scheme,
    create_access_token,
    decode_and_verify_token,
    get_current_authenticated_user,
    hash_password,
    lookup_user_by_username,
    require_privileged_role,
    verify_password,
)
from core_web_app.authentication.auth_routes import (
    LoginRequestSchema,
    RegisterRequestSchema,
    TokenResponseSchema,
    TokenVerifyRequestSchema,
    TokenVerifyResponseSchema,
    UserProfileResponseSchema,
    auth_router,
)

__all__ = [
    # Router & Schemas
    "auth_router",
    "LoginRequestSchema",
    "RegisterRequestSchema",
    "UserProfileResponseSchema",
    "TokenResponseSchema",
    "TokenVerifyRequestSchema",
    "TokenVerifyResponseSchema",
    # Password & JWT Handlers
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    "bearer_security_scheme",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_and_verify_token",
    "lookup_user_by_username",
    "get_current_authenticated_user",
    "require_privileged_role",
]
