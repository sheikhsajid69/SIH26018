from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from landsync.auth import require_roles
from landsync.database import get_db
from landsync.models import Role
from landsync.repositories import AuditRepository

router = APIRouter(prefix="/api/v1/audit", tags=["Immutable Audit Trail & Provenance"])


@router.get("")
def get_audit(
    actor_id: Annotated[str | None, Query()] = None,
    entity_type: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    _: tuple[str, Role] = Depends(require_roles(Role.OFFICER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Retrieve immutable cryptographic audit event log."""
    repo = AuditRepository(db)
    events = repo.list_events(actor_id=actor_id, entity_type=entity_type, limit=limit)
    return {
        "count": len(events),
        "events": events,
        "notice": "IMMUTABLE AUDIT TRAIL: Cryptographic activity logged during this session.",
    }
