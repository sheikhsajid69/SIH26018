from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from landsync.auth import (
    DEMO_TOKENS,
    create_access_token,
    get_current_user,
    verify_password,
)
from landsync.database import get_db
from landsync.models import Role
from landsync.repositories import UserRepository

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & Access"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


@router.get("/demo")
def demo_login() -> dict[str, object]:
    """Lists available synthetic demo roles and bearer tokens for immediate evaluation."""
    return {
        "mode": "DEMO_ONLY",
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
    user = repo.get_by_username(request.username)
    if not user:
        # Fallback for demo users
        if request.username in DEMO_TOKENS and request.password in ("demo123", "password", "demo"):
            user_id, role = DEMO_TOKENS[request.username]
            token = create_access_token(user_id, role.value)
            return TokenResponse(access_token=token, role=role.value, username=request.username)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    if user.password_hash and not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token, role=user.role, username=user.username)


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
