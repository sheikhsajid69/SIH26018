from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .adapters.state.demo import DemoAuthorityAdapter
from .blueprint import MockBlueprintProvider
from .models import (
    AuditEvent,
    ConsistencyReport,
    Document,
    LandParcel,
    MutationEvent,
    OwnershipRelationship,
    ReviewCase,
    ReviewDecision,
    Role,
    now,
)
from .services import LocalEvidenceStore, make_document, validate

app = FastAPI(
    title="LANDSYNC AI Intelligence & Consistency Validation API",
    version="0.2.0",
    description="Synthetic demo platform; no government system or live land registry is contacted.",
)

# CORS setup
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

adapter = DemoAuthorityAdapter()
store = LocalEvidenceStore(os.getenv("LOCAL_STORAGE_ROOT", ".landsync-storage"))
blueprint_provider = MockBlueprintProvider()

audit: list[AuditEvent] = []
documents: list[Document] = []

# Seed review cases
review_cases: dict[str, ReviewCase] = {
    "demo-case": ReviewCase(
        id="demo-case",
        parcel_id="demo-parcel",
        reason="Area variance detected: Submitted deed reports 2.31 acre while synthetic authority record reports 2.40 acre (~364 m² variance).",
        severity="MEDIUM",
        priority="P2_NORMAL",
        discrepancy_field="area",
        claimed_value="2.31 acre",
        authoritative_value="2.40 acre",
        status="OPEN",
    ),
    "case-102": ReviewCase(
        id="case-102",
        parcel_id="demo-parcel",
        reason="Boundary sketch variance: Preliminary raster edge detection indicates partial overlap along eastern boundary.",
        severity="LOW",
        priority="P3_ADVISORY",
        discrepancy_field="boundaries",
        claimed_value="Deed Sketch 192.8m East",
        authoritative_value="Cadastral Footprint 190.0m East",
        status="OPEN",
    ),
}

cases_file = Path(__file__).resolve().parents[3] / "data" / "synthetic" / "review_cases.json"
if cases_file.exists():
    for rc in json.loads(cases_file.read_text(encoding="utf-8")):
        review_cases[rc["review_case_id"]] = ReviewCase(
            id=rc["review_case_id"],
            parcel_id=rc["parcel_id"],
            reason=rc["reason"],
            severity="HIGH" if rc.get("priority") == "P1_HIGH" else "MEDIUM",
            priority=rc.get("priority", "P2_NORMAL"),
            status=rc.get("status", "OPEN"),
        )

TOKENS = {
    "demo-citizen": ("demo-citizen", Role.CITIZEN),
    "demo-officer": ("demo-officer", Role.OFFICER),
    "demo-admin": ("demo-admin", Role.ADMIN),
}


def actor(authorization: Annotated[str | None, Header()] = None) -> tuple[str, Role]:
    token = authorization.removeprefix("Bearer ") if authorization else ""
    identity = TOKENS.get(token)
    if not identity:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Use a demo Bearer token: demo-citizen, demo-officer, or demo-admin.",
        )
    return identity


def allowed(*roles: Role):
    def check(identity: tuple[str, Role] = Depends(actor)) -> tuple[str, Role]:
        if identity[1] not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: Your demo role '{identity[1]}' is not permitted to perform this action.",
            )
        return identity

    return check


def log(
    actor_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    *,
    before=None,
    after=None,
    reason=None,
) -> None:
    audit.append(
        AuditEvent(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before,
            after_state=after,
            reason=reason,
            trace_id=uuid4().hex,
        )
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "LANDSYNC AI",
        "mode": "DEMO_SYNTHETIC_ONLY",
        "notice": "All records and model extractions are synthetic. No live government database is connected.",
    }


@app.get("/api/v1/auth/demo")
def demo_login() -> dict[str, object]:
    return {
        "mode": "DEMO_ONLY",
        "tokens": [
            {
                "role": role.value,
                "bearer_token": token,
                "label": "Landowner / Citizen" if role == Role.CITIZEN else ("Revenue Officer" if role == Role.OFFICER else "System Administrator"),
            }
            for token, (_, role) in TOKENS.items()
        ],
    }


@app.get("/api/v1/parcels/search")
def search_parcels(
    q: Annotated[str, Query(min_length=1)] = "",
    _: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
) -> dict[str, object]:
    results = adapter.search(q)
    return {
        "query": q,
        "count": len(results),
        "results": results,
        "notice": "SYNTHETIC DEMO SEARCH: Results from local synthetic authority fixtures only.",
    }


@app.get("/api/v1/parcels/{parcel_id}")
def get_parcel(
    parcel_id: str,
    _: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
) -> dict[str, object]:
    try:
        record = adapter.parcel(parcel_id)
        return {
            "record": record,
            "notice": "SYNTHETIC DEMO DATA — not connected to government records.",
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Parcel '{parcel_id}' is not available in the demo dataset.")


@app.get("/api/v1/parcels/{parcel_id}/ownership")
def get_ownership(
    parcel_id: str,
    _: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
) -> dict[str, object]:
    try:
        adapter.parcel(parcel_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")
    return {
        "parcel_id": parcel_id,
        "ownership": adapter.ownership(parcel_id),
        "notice": "SYNTHETIC DEMO OWNERSHIP RECORD",
    }


@app.get("/api/v1/parcels/{parcel_id}/history")
def get_history(
    parcel_id: str,
    _: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
) -> dict[str, object]:
    try:
        adapter.parcel(parcel_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")
    return {
        "parcel_id": parcel_id,
        "mutation_history": adapter.mutation_history(parcel_id),
        "notice": "SYNTHETIC MUTATION TIMELINE: All historic records are demonstration fixtures.",
    }


@app.post("/api/v1/parcels/{parcel_id}/documents")
async def upload(
    parcel_id: str,
    file: Annotated[UploadFile, File(...)],
    identity: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER)),
) -> dict[str, object]:
    try:
        authority_record = adapter.parcel(parcel_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")

    if file.content_type not in {"application/pdf", "image/jpeg", "image/png", "text/plain"}:
        raise HTTPException(status_code=415, detail="Unsupported format: Upload a PDF, JPEG, PNG, or TXT document.")

    body = await file.read()
    if not body or len(body) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Upload a non-empty document smaller than 10 MB.")

    document = make_document(parcel_id, file.filename or "upload", file.content_type, body, identity[0], store)
    documents.append(document)

    validation_results = validate(document.extraction, authority_record)
    log(
        identity[0],
        "DOCUMENT_UPLOADED_AND_MOCK_PROCESSED",
        "document",
        document.id,
        after={"sha256": document.sha256, "storage_key": document.storage_key, "file_name": document.original_file_name},
        reason="Demo mock document pipeline extraction and SHA-256 integrity storage",
    )

    return {
        "document": document,
        "validation": validation_results,
        "review_case": review_cases.get("demo-case"),
        "notice": "MOCK extraction completed. Results are advisory and require human review where flagged.",
    }


@app.post("/api/v1/parcels/{parcel_id}/blueprint")
async def analyze_blueprint(
    parcel_id: str,
    file: Annotated[UploadFile, File(...)],
    identity: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER)),
) -> dict[str, object]:
    try:
        record = adapter.parcel(parcel_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")

    body = await file.read()
    if not body or len(body) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Upload a non-empty blueprint or sketch smaller than 10 MB.")

    analysis = blueprint_provider.analyze(file.filename or "sketch.png", body)
    log(
        identity[0],
        "BLUEPRINT_SKETCH_ANALYZED",
        "parcel",
        parcel_id,
        after={"provider": analysis.provider, "confidence": analysis.confidence, "status": analysis.spatial_consistency_status},
        reason="Computer Vision preliminary boundary line and dimension detection",
    )
    return {
        "parcel_id": parcel_id,
        "analysis": analysis,
        "authoritative_geometry": record.get("geometry"),
    }


@app.get("/api/v1/parcels/{parcel_id}/validation")
def validation(
    parcel_id: str,
    _: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
) -> dict[str, object]:
    try:
        authority_record = adapter.parcel(parcel_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")

    active_extraction = (
        documents[-1].extraction
        if documents and documents[-1].extraction
        else make_document(parcel_id, "seed_deed.pdf", "application/pdf", b"seed_deed_content", "system", store).extraction
    )
    results = validate(active_extraction, authority_record)
    return {
        "validation": results,
        "review_case": review_cases.get("demo-case"),
        "notice": "Validation compares AI mock extraction against synthetic authority record.",
    }


@app.get("/api/v1/review-cases")
def list_review_cases(
    status: str | None = None,
    _: tuple[str, Role] = Depends(allowed(Role.OFFICER, Role.ADMIN)),
) -> dict[str, object]:
    cases = list(review_cases.values())
    if status:
        cases = [c for c in cases if c.status.upper() == status.upper()]
    return {
        "count": len(cases),
        "cases": cases,
        "notice": "OFFICER REVIEW QUEUE: Synthetic discrepancy cases awaiting human decision.",
    }


@app.get("/api/v1/review-cases/{case_id}")
def get_review_case(
    case_id: str,
    _: tuple[str, Role] = Depends(allowed(Role.OFFICER, Role.ADMIN)),
) -> ReviewCase:
    case = review_cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Review case was not found.")
    return case


@app.post("/api/v1/review-cases/{case_id}/decision")
def decide(
    case_id: str,
    decision: ReviewDecision,
    identity: tuple[str, Role] = Depends(allowed(Role.OFFICER)),
) -> ReviewCase:
    case = review_cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Review case was not found.")

    before = case.model_dump(mode="json")
    case.status = "RESOLVED"
    case.assigned_officer = identity[0]
    case.reviewer_notes = decision.notes
    case.resolution = decision.resolution
    case.resolved_at = now()

    log(
        identity[0],
        "REVIEW_DECISION_RECORDED",
        "review_case",
        case_id,
        before=before,
        after=case.model_dump(mode="json"),
        reason=decision.notes,
    )
    return case


@app.get("/api/v1/audit")
def get_audit(
    _: tuple[str, Role] = Depends(allowed(Role.OFFICER, Role.ADMIN)),
) -> dict[str, object]:
    return {
        "count": len(audit),
        "events": audit,
        "notice": "IMMUTABLE AUDIT TRAIL: Activity logged during this demonstration session.",
    }


@app.get("/api/v1/admin/health")
def admin_health(
    _: tuple[str, Role] = Depends(allowed(Role.ADMIN)),
) -> dict[str, object]:
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
                "name": "mock-document-ai",
                "version": "demo-1.2",
                "status": "OPERATIONAL",
                "mode": "DETERMINISTIC_MOCK",
            },
            {
                "name": "mock-blueprint-cv",
                "version": "cv-sketch-0.3",
                "status": "OPERATIONAL",
                "mode": "ADVISORY_MOCK",
            },
        ],
        "storage": {
            "type": "LocalEvidenceStore",
            "root": str(store.root),
            "hashing_algorithm": "SHA-256",
            "documents_stored": len(documents),
        },
        "audit_events_count": len(audit),
        "open_review_cases": sum(1 for c in review_cases.values() if c.status == "OPEN"),
    }


@app.get("/api/v1/parcels/{parcel_id}/report")
def report(
    parcel_id: str,
    _: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
) -> ConsistencyReport:
    try:
        parcel_model = adapter.parcel_model(parcel_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")

    ownership = adapter.ownership(parcel_id)
    mutation_history = adapter.mutation_history(parcel_id)
    active_extraction = (
        documents[-1].extraction
        if documents and documents[-1].extraction
        else make_document(parcel_id, "seed_deed.pdf", "application/pdf", b"seed", "system", store).extraction
    )
    validation_results = validate(active_extraction, adapter.parcel(parcel_id))
    case = review_cases.get("demo-case") or list(review_cases.values())[0]

    return ConsistencyReport(
        parcel=parcel_model,
        ownership=ownership,
        validation_summary=validation_results,
        review_case=case,
        mutation_history=mutation_history,
    )
