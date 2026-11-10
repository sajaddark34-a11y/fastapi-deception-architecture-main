"""
Authentication, PBKDF2-HMAC Password Hashing, and RFC-7519 JWT Handler
(`core_web_app.authentication.auth_handler`).

Implements zero-C-dependency cryptographic password hashing (`hashlib.pbkdf2_hmac`
with random CSPRNG salts), standard HS256 JWT token signing and verification, and
FastAPI security dependencies (`get_current_authenticated_user`, `require_privileged_role`).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional, Sequence

try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
except ImportError:  # pragma: no cover
    class _StatusFallback:
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_401_UNAUTHORIZED = 401
        HTTP_403_FORBIDDEN = 403
        HTTP_404_NOT_FOUND = 404
        HTTP_409_CONFLICT = 409
        HTTP_422_UNPROCESSABLE_ENTITY = 422
        HTTP_500_INTERNAL_SERVER_ERROR = 500

    status = _StatusFallback()  # type: ignore[assignment]

    class HTTPException(Exception):  # type: ignore[no-redef]
        def __init__(
            self,
            status_code: int,
            detail: Any = None,
            headers: Optional[Dict[str, str]] = None,
        ) -> None:
            super().__init__(str(detail))
            self.status_code = status_code
            self.detail = detail
            self.headers = headers

    def Depends(dependency: Any = None) -> Any:  # type: ignore[misc]
        return dependency

    class HTTPAuthorizationCredentials:  # type: ignore[no-redef]
        def __init__(self, scheme: str = "Bearer", credentials: str = "") -> None:
            self.scheme = scheme
            self.credentials = credentials

    class HTTPBearer:  # type: ignore[no-redef]
        def __init__(self, auto_error: bool = True) -> None:
            self.auto_error = auto_error

try:
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:  # pragma: no cover
    AsyncSession = Any  # type: ignore[assignment,misc]
    select = None  # type: ignore[assignment]

from core_web_app.database_connector.connection import CoreUserAccount
from core_web_app.database_connector.session_manager import (
    fallback_core_store,
    get_core_db_session,
)

PBKDF2_ALGORITHM: str = "sha256"
PBKDF2_ITERATIONS: int = 260_000
SALT_BYTES_LENGTH: int = 16

JWT_SECRET_KEY: str = os.getenv(
    "CORE_JWT_SECRET_KEY",
    "deception_arch_core_app_jwt_hmac_sha256_secret_2026_key",
)
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

bearer_security_scheme = HTTPBearer(auto_error=False)


def _b64url_encode(data: bytes) -> str:
    """Base64URL-encode raw bytes without padding per RFC 7515."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(encoded: str) -> bytes:
    """Decode a Base64URL string, restoring required padding per RFC 7515."""
    padding = "=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode((encoded + padding).encode("ascii"))


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using `hashlib.pbkdf2_hmac` (HMAC-SHA256) with a
    16-byte cryptographically random salt.

    Args:
        plain_password: User plaintext password.

    Returns:
        Formatted hash string `pbkdf2_sha256$<iterations>$<salt_hex>$<derived_hex>`.
    """
    if not plain_password:
        raise ValueError("Password cannot be empty.")

    salt = secrets.token_bytes(SALT_BYTES_LENGTH)
    derived = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        plain_password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify a plaintext password against a stored PBKDF2-HMAC-SHA256 hash using
    constant-time comparison (`hmac.compare_digest`).

    Args:
        plain_password: Candidate plaintext password.
        stored_hash: Stored hash string from `hash_password`.

    Returns:
        `True` if the password matches, `False` otherwise.
    """
    if not plain_password or not stored_hash:
        return False

    try:
        parts = stored_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hex = parts[3]

        candidate_derived = hashlib.pbkdf2_hmac(
            PBKDF2_ALGORITHM,
            plain_password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(candidate_derived.hex(), expected_hex)
    except Exception:
        return False


def create_access_token(
    subject: str,
    user_id: str,
    role: str = "engineer",
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create and digitally sign a standard RFC 7519 HS256 JSON Web Token (JWT).

    Args:
        subject: Username (`sub` claim).
        user_id: Unique user account identifier (`uid` claim).
        role: User role (`role` claim).
        expires_delta: Optional custom expiration lifetime.
        extra_claims: Optional dictionary of additional JWT payload claims.

    Returns:
        Signed compact JWT string (`<header>.<payload>.<signature>`).
    """
    now_ts = int(time.time())
    lifetime_seconds = int(
        (
            expires_delta
            if expires_delta is not None
            else timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        ).total_seconds()
    )
    exp_ts = now_ts + max(60, lifetime_seconds)

    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload: Dict[str, Any] = {
        "sub": subject,
        "uid": user_id,
        "role": role,
        "iat": now_ts,
        "exp": exp_ts,
        "jti": f"jwt_{uuid.uuid4().hex[:16]}",
        "iss": "core_web_app",
    }
    if extra_claims:
        payload.update(extra_claims)

    header_b64 = _b64url_encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    payload_b64 = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    signature_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_and_verify_token(token: str) -> Dict[str, Any]:
    """
    Verify the HMAC-SHA256 signature and expiration of a JWT token and return its claims.

    Args:
        token: Compact JWT string.

    Returns:
        Decoded JWT claims dictionary.

    Raises:
        HTTPException(401): If the token is malformed, forged, or expired.
    """
    if not token or not isinstance(token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or empty authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = token.strip().split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed JWT token structure.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    header_b64, payload_b64, signature_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_sig = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    try:
        provided_sig = _b64url_decode(signature_b64)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT signature encoding.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if not hmac.compare_digest(expected_sig, provided_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT signature verification failed.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        header = json.loads(_b64url_decode(header_b64).decode("utf-8"))
        claims = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT payload encoding.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if header.get("alg") != JWT_ALGORITHM:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unsupported JWT signing algorithm.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    exp_ts = claims.get("exp")
    if not isinstance(exp_ts, (int, float)) or int(time.time()) >= int(exp_ts):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT access token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not claims.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT token missing subject ('sub') claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return claims


async def lookup_user_by_username(
    username: str,
    db: Optional[AsyncSession] = None,
) -> Optional[CoreUserAccount]:
    """
    Look up a `CoreUserAccount` by `username` in PostgreSQL with seamless fallback
    to `fallback_core_store`.
    """
    cleaned = username.strip()
    if not cleaned:
        return None

    if db is not None:
        try:
            stmt = select(CoreUserAccount).where(CoreUserAccount.username == cleaned)
            user = (await db.execute(stmt)).scalar_one_or_none()
            if user is not None:
                return user
        except Exception:
            pass

    async with fallback_core_store.lock:
        return fallback_core_store.users_by_username.get(cleaned)


async def get_current_authenticated_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_security_scheme
    ),
    db: Optional[AsyncSession] = Depends(get_core_db_session),
) -> CoreUserAccount:
    """
    FastAPI dependency that extracts, verifies, and resolves the bearer JWT token
    to an active `CoreUserAccount`.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = decode_and_verify_token(credentials.credentials)
    username = str(claims.get("sub", ""))
    user = await lookup_user_by_username(username, db=db)

    if user is None:
        # Synthesize transient account context if valid signed token was issued
        user = CoreUserAccount(
            user_id=str(claims.get("uid", f"usr_{username}")),
            username=username,
            email=f"{username}@enterprise-core.internal",
            password_hash="",
            role=str(claims.get("role", "engineer")),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled.",
        )

    return user


def require_privileged_role(
    allowed_roles: Sequence[str] = ("admin", "engineer"),
) -> Callable[..., Any]:
    """
    FastAPI dependency factory enforcing role-based access control (RBAC) for
    privileged routes.

    Args:
        allowed_roles: Sequence of permitted role names (defaults to `("admin", "engineer")`).

    Returns:
        Async FastAPI dependency returning the verified `CoreUserAccount`.
    """
    normalized_roles = {r.strip().lower() for r in allowed_roles}

    async def _role_enforcer(
        current_user: CoreUserAccount = Depends(get_current_authenticated_user),
    ) -> CoreUserAccount:
        if current_user.role.strip().lower() not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not authorized for this resource.",
            )
        return current_user

    return _role_enforcer
