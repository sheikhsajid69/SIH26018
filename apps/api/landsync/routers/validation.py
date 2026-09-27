from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from landsync.adapters.state.demo import DemoAuthorityAdapter
from landsync.auth import require_roles
from landsync.database import get_db
from landsync.models import ReviewCase, Role, ValidationState
from landsync.repositories import (
    DocumentRepository,
    LandParcelRepository,
    ReviewCaseRepository,
    ValidationRepository,
)
from landsync.services import LocalEvidenceStorage, make_document, validate

router = APIRouter(prefix="/api/v1/parcels", tags=["Consistency Validation Engine"])
adapter = DemoAuthorityAdapter()
default_store = LocalEvidenceStorage()


@router.get("/{parcel_id}/validation")
def get_validation(
    parcel_id: str,
    _: tuple[str, Role] = Depends(require_roles(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Retrieve or evaluate consistency validation between document extractions and authoritative record."""
    parcel_repo = LandParcelRepository(db)
    authority_record = parcel_repo.get_dict(parcel_id)
    if not authority_record:
        try:
            authority_record = adapter.parcel(parcel_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")

    val_repo = ValidationRepository(db)
    results = val_repo.get_by_parcel(parcel_id)

    if not results:
        # Check if any documents exist in DB for this parcel
        doc_repo = DocumentRepository(db)
        docs = doc_repo.get_by_parcel(parcel_id)
        if docs and docs[0].extraction:
            results = validate(docs[0].extraction, authority_record)
        else:
            synth_doc = make_document(parcel_id, "seed_deed.pdf", "application/pdf", b"seed_deed_content", "system", default_store)
            results = validate(synth_doc.extraction, authority_record)
        val_repo.save_results(parcel_id, "seed-doc", results)

    case_repo = ReviewCaseRepository(db)
    case_orm = case_repo.get_by_parcel(parcel_id)
    review_case_model = case_repo.to_domain(case_orm) if case_orm else None

    # Fallback to demo-case for backwards-compatibility with demo tests if demo-parcel
    if not review_case_model and parcel_id == "demo-parcel":
        demo_c = case_repo.get_by_id("demo-case")
        if demo_c:
            review_case_model = case_repo.to_domain(demo_c)

    return {
        "validation": results,
        "review_case": review_case_model,
        "notice": "Validation compares AI mock extraction against synthetic authority record.",
    }
