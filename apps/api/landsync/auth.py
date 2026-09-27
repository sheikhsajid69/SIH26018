from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, status

from landsync.models import Role

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "landsync-ai-demo-secret-key-change-in-production-1234567890")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "120"))

# Static demo tokens mapping
DEMO_TOKENS: dict[str, tuple[str, Role]] = {
    "demo-citizen": ("demo-citizen", Role.CITIZEN),
    "demo-officer": ("demo-officer", Role.OFFICER),
    "demo-admin": ("demo-admin", Role.ADMIN),
}


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify raw password against bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


def create_access_token(user_id: str, role: str, expires_delta: timedelta | None = None) -> str:
    """Create signed HS256 JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=JWT_EXPIRATION_MINUTES)
    )
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> tuple[str, Role]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub", "")
        role_str: str = payload.get("role", "")
        if not user_id or not role_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims.",
            )
        return user_id, Role(role_str)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please re-authenticate.",
        )
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )


def get_current_user(authorization: Annotated[str | None, Header()] = None) -> tuple[str, Role]:
    """
    Unified authentication dependency.
    Accepts both demo Bearer tokens (demo-citizen, demo-officer, demo-admin)
    and cryptographically signed JWT Bearer tokens.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Use a demo Bearer token: demo-citizen, demo-officer, or demo-admin.",
        )

    token = authorization.removeprefix("Bearer ").strip()

    # 1. Fast path for demo tokens
    if token in DEMO_TOKENS:
        return DEMO_TOKENS[token]

    # 2. JWT verification
    return decode_access_token(token)


def require_roles(*roles: Role):
    """RBAC dependency ensuring the authenticated user possesses one of the allowed roles."""
    def role_checker(identity: tuple[str, Role] = Depends(get_current_user)) -> tuple[str, Role]:
        user_id, user_role = identity
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Your demo role '{user_role.value}' is not permitted to perform this action.",
            )
        return identity

    return role_checker
