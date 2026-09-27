from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from landsync.auth import require_roles
from landsync.database import get_db
from landsync.models import ReviewCase, ReviewDecision, Role, now
from landsync.repositories import AuditRepository, ReviewCaseRepository

router = APIRouter(prefix="/api/v1/review-cases", tags=["Officer Human-in-the-Loop Review Queue"])


@router.get("")
def list_review_cases(
    status: Annotated[str | None, Query()] = None,
    _: tuple[str, Role] = Depends(require_roles(Role.OFFICER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Retrieve queue of discrepancy review cases for authorized revenue officers."""
    repo = ReviewCaseRepository(db)
    cases = repo.list_all(status_filter=status)
    domain_cases = [repo.to_domain(c) for c in cases]
    return {
        "count": len(domain_cases),
        "cases": domain_cases,
        "notice": "OFFICER REVIEW QUEUE: Synthetic discrepancy cases awaiting human decision.",
    }


@router.get("/{case_id}")
def get_review_case(
    case_id: str,
    _: tuple[str, Role] = Depends(require_roles(Role.OFFICER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> ReviewCase:
    """Retrieve detailed adjudication dossier for a specific review case."""
    repo = ReviewCaseRepository(db)
    case_orm = repo.get_by_id(case_id)
    if not case_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review case '{case_id}' was not found.",
        )
    return repo.to_domain(case_orm)


@router.post("/{case_id}/decision")
def record_decision(
    case_id: str,
    decision: ReviewDecision,
    identity: tuple[str, Role] = Depends(require_roles(Role.OFFICER)),
    db: Session = Depends(get_db),
) -> ReviewCase:
    """
    Record legally binding officer determination on discrepancy case.
    Strictly restricted to authorized revenue officers (Rule 11).
    Generates immutable audit trail record.
    """
    repo = ReviewCaseRepository(db)
    case_orm = repo.get_by_id(case_id)
    if not case_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review case '{case_id}' was not found.",
        )

    before_state = {
        "id": case_orm.id,
        "parcel_id": case_orm.parcel_id,
        "status": case_orm.status,
        "severity": case_orm.severity,
        "priority": case_orm.priority,
        "discrepancy_field": case_orm.discrepancy_field,
    }

    # Apply adjudication update
    case_orm.status = "RESOLVED"
    case_orm.assigned_officer = identity[0]
    case_orm.reviewer_notes = decision.notes
    case_orm.resolution = decision.resolution
    case_orm.resolved_at = now()
    db.commit()
    db.refresh(case_orm)

    domain_case = repo.to_domain(case_orm)

    # Immutable audit logging
    audit_repo = AuditRepository(db)
    audit_repo.log(
        actor_id=identity[0],
        action="REVIEW_DECISION_RECORDED",
        entity_type="review_case",
        entity_id=case_id,
        before_state=before_state,
        after_state=domain_case.model_dump(mode="json"),
        reason=decision.notes,
    )

    return domain_case
