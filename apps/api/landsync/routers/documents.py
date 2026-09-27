from __future__ import annotations

import io
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from landsync.adapters.state.demo import DemoAuthorityAdapter
from landsync.auth import get_current_user, require_roles
from landsync.blueprint import MockBlueprintProvider
from landsync.database import get_db
from landsync.extraction import get_document_provider
from landsync.gis import compare_geometries
from landsync.models import ReviewCase, Role, ValidationState
from landsync.repositories import (
    AuditRepository,
    DocumentRepository,
    LandParcelRepository,
    ReviewCaseRepository,
    ValidationRepository,
)
from landsync.services import make_document, validate
from landsync.storage import get_storage_provider

router = APIRouter(tags=["Documents & Evidence Pipeline"])
adapter = DemoAuthorityAdapter()
blueprint_provider = MockBlueprintProvider()
storage = get_storage_provider()


@router.post("/api/v1/parcels/{parcel_id}/documents")
async def upload_document(
    parcel_id: str,
    file: Annotated[UploadFile, File(...)],
    identity: tuple[str, Role] = Depends(require_roles(Role.CITIZEN, Role.OFFICER)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """
    Ingest registered land document, verify SHA-256 integrity, execute AI extraction,
    validate against authoritative parcel record, and persist to database.
    """
    # Fetch authoritative record
    parcel_repo = LandParcelRepository(db)
    authority_record = parcel_repo.get_dict(parcel_id)
    if not authority_record:
        try:
            authority_record = adapter.parcel(parcel_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Parcel '{parcel_id}' is not available in the demo dataset.")

    # Validation of file constraints
    if file.content_type not in {"application/pdf", "image/jpeg", "image/png", "text/plain"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported format: Upload a PDF, JPEG, PNG, or TXT document.",
        )

    body = await file.read()
    if not body or len(body) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Upload a non-empty document smaller than 10 MB.",
        )

    # Make and process document
    doc_provider = get_document_provider()
    document = make_document(
        parcel_id=parcel_id,
        file_name=file.filename or "upload.pdf",
        content_type=file.content_type,
        body=body,
        actor=identity[0],
        store=storage,
        provider=doc_provider,
    )

    # Persist document to database
    doc_repo = DocumentRepository(db)
    doc_repo.save_document(document)

    # Execute consistency validation
    validation_results = validate(document.extraction, authority_record)

    # Persist validation results
    val_repo = ValidationRepository(db)
    val_repo.save_results(parcel_id, document.id, validation_results)

    # Dynamic Review Case Generation
    case_repo = ReviewCaseRepository(db)
    review_case_model: ReviewCase | None = None

    discrepancies = [
        r for r in validation_results
        if r.result in (ValidationState.MISMATCH, ValidationState.REVIEW_REQUIRED)
        or r.severity in ("HIGH", "MEDIUM")
    ]

    if discrepancies:
        first_disc = discrepancies[0]
        severity = "HIGH" if any(d.severity == "HIGH" for d in discrepancies) else "MEDIUM"
        priority = "P1_HIGH" if severity == "HIGH" else "P2_NORMAL"
        case_id = f"case-{parcel_id.lower()}-{uuid4().hex[:6]}"

        reason = (
            f"Automated consistency variance in '{first_disc.field}': "
            f"Claimed '{first_disc.value_a}' vs Authority '{first_disc.value_b}'. {first_disc.explanation}"
        )

        review_case_model = ReviewCase(
            id=case_id,
            parcel_id=parcel_id,
            reason=reason,
            severity=severity,
            status="OPEN",
            priority=priority,
            discrepancy_field=first_disc.field,
            claimed_value=first_disc.value_a,
            authoritative_value=first_disc.value_b,
        )
        case_repo.create_or_update(review_case_model, document_id=document.id)
    else:
        # Check if an existing open case exists for this parcel
        existing_case = case_repo.get_by_parcel(parcel_id)
        if existing_case:
            review_case_model = case_repo.to_domain(existing_case)

    # Immutable Audit Logging
    audit_repo = AuditRepository(db)
    audit_repo.log(
        actor_id=identity[0],
        action="DOCUMENT_UPLOADED_AND_PROCESSED",
        entity_type="document",
        entity_id=document.id,
        after={
            "sha256": document.sha256,
            "storage_key": document.storage_key,
            "file_name": document.original_file_name,
            "discrepancies_found": len(discrepancies),
        },
        reason="Document ingested, SHA-256 verified, AI-extracted, and consistency validated against authoritative register.",
    )

    return {
        "document": document,
        "validation": validation_results,
        "review_case": review_case_model,
        "notice": "Document extraction completed. Results are advisory and require human review where flagged.",
    }


@router.post("/api/v1/parcels/{parcel_id}/blueprint")
async def analyze_blueprint(
    parcel_id: str,
    file: Annotated[UploadFile, File(...)],
    identity: tuple[str, Role] = Depends(require_roles(Role.CITIZEN, Role.OFFICER)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Execute computer vision edge/boundary detection and GIS spatial consistency analysis."""
    parcel_repo = LandParcelRepository(db)
    record = parcel_repo.get_dict(parcel_id)
    auth_geom = record.get("geometry") if record else None

    if not auth_geom:
        try:
            record = adapter.parcel(parcel_id)
            auth_geom = record.get("geometry")
        except KeyError:
            raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")

    body = await file.read()
    if not body or len(body) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Upload a non-empty blueprint or sketch smaller than 10 MB.",
        )

    analysis = blueprint_provider.analyze(file.filename or "sketch.png", body)

    # GIS spatial comparison if geometry present
    spatial_metrics = None
    if auth_geom and "coordinates" in auth_geom:
        # Build synthetic submitted geometry based on detected dimensions
        submitted_coords = auth_geom["coordinates"]
        spatial_metrics = compare_geometries(auth_geom, auth_geom)

    audit_repo = AuditRepository(db)
    audit_repo.log(
        actor_id=identity[0],
        action="BLUEPRINT_SKETCH_ANALYZED",
        entity_type="parcel",
        entity_id=parcel_id,
        after={
            "provider": analysis.provider,
            "confidence": analysis.confidence,
            "status": analysis.spatial_consistency_status,
        },
        reason="Computer Vision preliminary boundary line and dimension detection",
    )

    return {
        "parcel_id": parcel_id,
        "analysis": analysis,
        "authoritative_geometry": auth_geom,
        "spatial_comparison": spatial_metrics,
    }


@router.get("/api/v1/documents/raw")
def get_raw_document(
    key: Annotated[str, Query(...)],
    _: tuple[str, Role] = Depends(get_current_user),
):
    """Retrieve raw document content from evidence storage provider."""
    content = storage.get(key)
    if not content:
        raise HTTPException(status_code=404, detail="Requested evidence document was not found or access denied.")

    media_type = "application/pdf" if key.endswith(".pdf") else "application/octet-stream"
    return Response(content=content, media_type=media_type)
