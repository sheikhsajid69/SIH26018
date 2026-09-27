from __future__ import annotations

import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from landsync.adapters.state.demo import DemoAuthorityAdapter
from landsync.auth import require_roles
from landsync.database import get_db
from landsync.db_models import AuditEventOrm, DocumentOrm, ReviewCaseOrm
from landsync.extraction import get_document_provider
from landsync.models import Role
from landsync.storage import get_storage_provider

router = APIRouter(prefix="/api/v1/admin", tags=["Administrative & System Operations"])
adapter = DemoAuthorityAdapter()
storage = get_storage_provider()


@router.get("/health")
def admin_health(
    _: tuple[str, Role] = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Retrieve operational diagnostics and platform sub-system telemetry."""
    doc_provider = get_document_provider()
    db_audit_count = db.query(AuditEventOrm).count()
    db_doc_count = db.query(DocumentOrm).count()
    open_cases = db.query(ReviewCaseOrm).filter(ReviewCaseOrm.status == "OPEN").count()

    storage_root = storage.root

    return {
        "system": "LANDSYNC AI Core",
        "state_adapters": [
            {
                "name": "DemoAuthorityAdapter",
                "type": "SYNTHETIC_MOCK",
                "status": "HEALTHY",
                "jurisdiction": "Karnataka (Demo State)",
                "parcels_loaded": len(adapter.all_parcel_ids()),
            }
        ],
        "document_providers": [
            {
                "name": doc_provider.provider,
                "version": doc_provider.model_version,
                "status": "OPERATIONAL",
                "mode": "PLUGGABLE_OCR_NER",
            },
            {
                "name": "mock-blueprint-cv",
                "version": "cv-sketch-0.3",
                "status": "OPERATIONAL",
                "mode": "ADVISORY_MOCK",
            },
        ],
        "storage": {
            "type": storage.__class__.__name__,
            "root": str(storage_root),
            "hashing_algorithm": "SHA-256",
            "documents_stored": db_doc_count,
        },
        "audit_events_count": db_audit_count,
        "open_review_cases": open_cases,
    }
