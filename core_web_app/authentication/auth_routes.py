"""
Authentication API Routes for the Core Web Application (`core_web_app.authentication.auth_routes`).

Exposes `/api/v1/auth` endpoints for legitimate user login (`POST /login`),
account registration (`POST /register`), profile retrieval (`GET /me`), and
token verification (`POST /verify`).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

try:
    from fastapi import APIRouter, Depends, HTTPException, Request, status
except ImportError:  # pragma: no cover
    from core_web_app.authentication.auth_handler import (  # type: ignore[attr-defined]
        Depends,
        HTTPException,
        status,
    )

    class Request:  # type: ignore[no-redef]
        def __init__(
            self,
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            path: str = "/",
        ) -> None:
            self.headers = headers or {}
            self.cookies = cookies or {}
            self.url = type("_URL", (), {"path": path})()

    class APIRouter:  # type: ignore[no-redef]
        def __init__(self, prefix: str = "", tags: Optional[Any] = None) -> None:
            self.prefix = prefix
            self.tags = tags or []
            self.routes: list[Any] = []

        def _register(self, method: str, path: str, **kwargs: Any) -> Any:
            def decorator(fn: Any) -> Any:
                self.routes.append((method, f"{self.prefix}{path}", fn, kwargs))
                return fn

            return decorator

        def get(self, path: str, **kwargs: Any) -> Any:
            return self._register("GET", path, **kwargs)

        def post(self, path: str, **kwargs: Any) -> Any:
            return self._register("POST", path, **kwargs)

        def put(self, path: str, **kwargs: Any) -> Any:
            return self._register("PUT", path, **kwargs)

        def delete(self, path: str, **kwargs: Any) -> Any:
            return self._register("DELETE", path, **kwargs)

        def api_route(self, path: str, **kwargs: Any) -> Any:
            return self._register("ANY", path, **kwargs)

try:
    from sqlalchemy import or_, select
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:  # pragma: no cover
    AsyncSession = Any  # type: ignore[assignment,misc]
    or_ = None  # type: ignore[assignment]
    select = None  # type: ignore[assignment]

from core_web_app.authentication.auth_handler import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_and_verify_token,
    get_current_authenticated_user,
    hash_password,
    lookup_user_by_username,
    verify_password,
)
from core_web_app.database_connector.connection import CoreUserAccount
from core_web_app.database_connector.session_manager import (
    fallback_core_store,
    get_core_db_session,
)

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Core Authentication"])


class LoginRequestSchema(BaseModel):
    """Request payload for `POST /api/v1/auth/login`."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    username: str = Field(..., min_length=3, max_length=128)
    password: str = Field(..., min_length=6, max_length=256)


class RegisterRequestSchema(BaseModel):
    """Request payload for `POST /api/v1/auth/register`."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    username: str = Field(..., min_length=3, max_length=128)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=256)
    role: str = Field(default="engineer", min_length=3, max_length=64)


class UserProfileResponseSchema(BaseModel):
    """Public profile representation of a `CoreUserAccount`."""

    model_config = ConfigDict(extra="forbid")

    user_id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class TokenResponseSchema(BaseModel):
    """Response payload returned upon successful authentication."""

    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    session_id: str
    user: UserProfileResponseSchema


class TokenVerifyRequestSchema(BaseModel):
    """Request payload for `POST /api/v1/auth/verify`."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    token: str = Field(..., min_length=16)


class TokenVerifyResponseSchema(BaseModel):
    """Response payload for `POST /api/v1/auth/verify`."""

    model_config = ConfigDict(extra="forbid")

    is_valid: bool
    subject: str
    user_id: str
    role: str
    expires_at_epoch: int
    claims: Dict[str, Any]


def _to_user_profile(user: CoreUserAccount) -> UserProfileResponseSchema:
    """Convert a `CoreUserAccount` ORM instance into a `UserProfileResponseSchema`."""
    return UserProfileResponseSchema(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@auth_router.post(
    "/login",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Authenticate legitimate user and issue signed JWT",
)
async def login_user(
    payload: LoginRequestSchema,
    request: Request,
    db: Optional[AsyncSession] = Depends(get_core_db_session),
) -> TokenResponseSchema:
    """
    Validate user credentials against `core_app_users` and issue an RFC-7519 JWT
    access token along with session metadata.
    """
    user = await lookup_user_by_username(payload.username, db=db)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    session_id = (
        request.headers.get("X-Session-ID")
        or request.cookies.get("deception_session_id")
        or str(uuid.uuid4())
    )
    access_token = create_access_token(
        subject=user.username,
        user_id=user.user_id,
        role=user.role,
        extra_claims={"sid": session_id},
    )

    return TokenResponseSchema(
        access_token=access_token,
        token_type="bearer",
        expires_in_seconds=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        session_id=session_id,
        user=_to_user_profile(user),
    )


@auth_router.post(
    "/register",
    response_model=UserProfileResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new legitimate user account",
)
async def register_user(
    payload: RegisterRequestSchema,
    db: Optional[AsyncSession] = Depends(get_core_db_session),
) -> UserProfileResponseSchema:
    """
    Create a new `CoreUserAccount` with PBKDF2-HMAC-SHA256 password hashing.
    """
    if "@" not in payload.email or "." not in payload.email.split("@")[-1]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email address format.",
        )

    allowed_roles = {"admin", "engineer", "auditor", "analyst", "operator"}
    normalized_role = payload.role.lower()
    if normalized_role not in allowed_roles:
        normalized_role = "engineer"

    # Check uniqueness in memory store
    async with fallback_core_store.lock:
        if payload.username in fallback_core_store.users_by_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{payload.username}' is already registered.",
            )
        for existing_usr in fallback_core_store.users_by_username.values():
            if existing_usr.email.lower() == payload.email.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{payload.email}' is already registered.",
                )

    # Check uniqueness in PostgreSQL if connected
    if db is not None:
        try:
            stmt = select(CoreUserAccount).where(
                or_(
                    CoreUserAccount.username == payload.username,
                    CoreUserAccount.email == payload.email,
                )
            )
            existing_db_user = (await db.execute(stmt)).scalar_one_or_none()
            if existing_db_user is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username or email already exists.",
                )
        except HTTPException:
            raise
        except Exception:
            pass

    new_user = CoreUserAccount(
        user_id=f"usr_{uuid.uuid4().hex[:12]}",
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=normalized_role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    async with fallback_core_store.lock:
        fallback_core_store.users_by_username[new_user.username] = new_user
        fallback_core_store.users_by_id[new_user.user_id] = new_user

    if db is not None:
        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        except Exception:
            pass

    return _to_user_profile(new_user)


@auth_router.get(
    "/me",
    response_model=UserProfileResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current authenticated user profile",
)
async def get_authenticated_profile(
    current_user: CoreUserAccount = Depends(get_current_authenticated_user),
) -> UserProfileResponseSchema:
    """
    Return the profile of the currently authenticated user resolved from the bearer JWT.
    """
    return _to_user_profile(current_user)


@auth_router.post(
    "/verify",
    response_model=TokenVerifyResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Verify JWT token signature and expiration",
)
async def verify_jwt_token(
    payload: TokenVerifyRequestSchema,
) -> TokenVerifyResponseSchema:
    """
    Cryptographically verify a bearer JWT token and return its decoded claims.
    """
    claims = decode_and_verify_token(payload.token)
    return TokenVerifyResponseSchema(
        is_valid=True,
        subject=str(claims.get("sub", "")),
        user_id=str(claims.get("uid", "")),
        role=str(claims.get("role", "engineer")),
        expires_at_epoch=int(claims.get("exp", 0)),
        claims=claims,
    )
