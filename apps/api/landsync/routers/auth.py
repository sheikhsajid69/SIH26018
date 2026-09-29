from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from landsync.auth import (
    DEMO_TOKENS,
    create_access_token,
    get_current_user,
    is_demo_mode,
    verify_password,
)
from landsync.database import get_db
from landsync.models import Role
from landsync.repositories import AuditRepository, UserRepository

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & Access"])


class LoginRequest(BaseModel):
    username: str  # Supports email, username, or user_id
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    user_id: str | None = None
    name: str | None = None


@router.get("/demo")
def demo_login() -> dict[str, object]:
    """Lists available synthetic demo roles and bearer tokens for immediate evaluation."""
    return {
        "mode": "DEMO_ONLY",
        "demo_mode_enabled": is_demo_mode(),
        "tokens": [
            {
                "role": role.value,
                "bearer_token": token,
                "label": (
                    "Landowner / Citizen"
                    if role == Role.CITIZEN
                    else ("Revenue Officer" if role == Role.OFFICER else "System Administrator")
                ),
            }
            for token, (_, role) in DEMO_TOKENS.items()
        ],
    }


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate registered users and generate cryptographically signed JWT access token."""
    repo = UserRepository(db)
    user = repo.get_by_email_or_username(request.username)
    
    if not user:
        # Fallback for demo users (only if demo mode is enabled)
        if is_demo_mode() and request.username in DEMO_TOKENS and request.password in ("demo123", "password", "demo", "Admin@LandSync2026!"):
            user_id, role = DEMO_TOKENS[request.username]
            token = create_access_token(user_id, role.value)
            return TokenResponse(
                access_token=token,
                role=role.value,
                username=request.username,
                user_id=user_id,
                name=f"Demo {role.value.capitalize()}",
            )

        # Generic authentication failure message (Phase 4 & 15)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    # Check account status
    if user.status == "DEACTIVATED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated by an administrator. Please contact revenue authority support.",
        )

    # Verify password hash
    password_valid = False
    if user.password_hash:
        password_valid = verify_password(request.password, user.password_hash)
    elif is_demo_mode() and request.password in ("demo123", "password", "demo", "Admin@LandSync2026!", "Officer@LandSync2026!", "Citizen@LandSync2026!"):
        # Fallback for seeded users in demo mode
        password_valid = True

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    repo.update_last_login(user.id)
    token = create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=token,
        role=user.role,
        username=user.username,
        user_id=user.id,
        name=user.name,
    )


@router.post("/logout")
def logout(
    identity: tuple[str, Role] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Terminates active session and records immutable audit log."""
    user_id, role = identity
    AuditRepository(db).log(
        actor_id=user_id,
        action="LOGOUT",
        entity_type="USER_SESSION",
        entity_id=user_id,
        reason="User initiated explicit session termination.",
    )
    return {"status": "SUCCESS", "message": "Successfully logged out."}


@router.get("/me")
def me(identity: tuple[str, Role] = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return profile of currently authenticated user session."""
    user_id, role = identity
    repo = UserRepository(db)
    user = repo.get_by_id(user_id) or repo.get_by_username(user_id)
    if user:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "jurisdiction": user.jurisdiction,
            "status": user.status,
        }
    return {
        "id": user_id,
        "username": user_id,
        "role": role.value,
        "status": "DEMO_SESSION",
    }
