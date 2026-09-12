from __future__ import annotations

import os
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .adapters.state.demo import DemoAuthorityAdapter
from .models import AuditEvent, ReviewCase, ReviewDecision, Role, now
from .services import LocalEvidenceStore, make_document, validate

app = FastAPI(title="LANDSYNC AI Demo API", version="0.1.0", description="Synthetic demo only; no government system is connected.")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","), allow_methods=["*"], allow_headers=["*"], allow_credentials=False)
adapter = DemoAuthorityAdapter()
store = LocalEvidenceStore(os.getenv("LOCAL_STORAGE_ROOT", ".landsync-storage"))
audit: list[AuditEvent] = []
documents = []
review_case = ReviewCase(id="demo-case", parcel_id="demo-parcel", reason="Area differs between mock extraction and synthetic authority record", severity="MEDIUM")

TOKENS = {"demo-citizen": ("demo-citizen", Role.CITIZEN), "demo-officer": ("demo-officer", Role.OFFICER), "demo-admin": ("demo-admin", Role.ADMIN)}


def actor(authorization: Annotated[str | None, Header()] = None) -> tuple[str, Role]:
    token = authorization.removeprefix("Bearer ") if authorization else ""
    identity = TOKENS.get(token)
    if not identity:
        raise HTTPException(401, "Use a demo Bearer token: demo-citizen, demo-officer, or demo-admin.")
    return identity


def allowed(*roles: Role):
    def check(identity: tuple[str, Role] = Depends(actor)) -> tuple[str, Role]:
        if identity[1] not in roles:
            raise HTTPException(403, "Your demo role is not permitted to perform this action.")
        return identity
    return check


def log(actor_id: str, action: str, entity_type: str, entity_id: str, *, before=None, after=None, reason=None) -> None:
    audit.append(AuditEvent(actor_id=actor_id, action=action, entity_type=entity_type, entity_id=entity_id, before_state=before, after_state=after, reason=reason, trace_id=uuid4().hex))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "DEMO_SYNTHETIC_ONLY"}


@app.get("/api/v1/auth/demo")
def demo_login() -> dict[str, object]:
    return {"mode": "DEMO_ONLY", "tokens": [{"role": role.value, "bearer_token": token} for token, (_, role) in TOKENS.items()]}


@app.get("/api/v1/parcels/{parcel_id}")
def get_parcel(parcel_id: str, _: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER, Role.ADMIN))) -> dict[str, object]:
    try:
        return {"record": adapter.parcel(parcel_id), "notice": "SYNTHETIC DEMO DATA — not connected to government records."}
    except KeyError:
        raise HTTPException(404, "Parcel is not available in the demo dataset.")


@app.post("/api/v1/parcels/{parcel_id}/documents")
async def upload(parcel_id: str, file: Annotated[UploadFile, File(...)], identity: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER))) -> dict[str, object]:
    if parcel_id != "demo-parcel":
        raise HTTPException(404, "Parcel is not available in the demo dataset.")
    if file.content_type not in {"application/pdf", "image/jpeg", "image/png"}:
        raise HTTPException(415, "Upload a PDF, JPEG, or PNG document.")
    body = await file.read()
    if not body or len(body) > 10 * 1024 * 1024:
        raise HTTPException(413, "Upload a non-empty document smaller than 10 MB.")
    document = make_document(parcel_id, file.filename or "upload", file.content_type, body, identity[0], store)
    documents.append(document)
    results = validate(document.extraction, adapter.parcel(parcel_id))
    log(identity[0], "DOCUMENT_UPLOADED_AND_MOCK_PROCESSED", "document", document.id, after={"sha256": document.sha256, "storage_key": document.storage_key}, reason="Demo mock document pipeline")
    return {"document": document, "validation": results, "review_case": review_case, "notice": "MOCK extraction completed. Results are advisory and require human review where flagged."}


@app.get("/api/v1/parcels/{parcel_id}/validation")
def validation(parcel_id: str, _: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER, Role.ADMIN))) -> dict[str, object]:
    if parcel_id != "demo-parcel":
        raise HTTPException(404, "Parcel is not available in the demo dataset.")
    return {"validation": validate(documents[-1].extraction, adapter.parcel(parcel_id)) if documents else validate(make_document(parcel_id, "seed.pdf", "application/pdf", b"seed", "system", store).extraction, adapter.parcel(parcel_id)), "review_case": review_case}


@app.post("/api/v1/review-cases/{case_id}/decision")
def decide(case_id: str, decision: ReviewDecision, identity: tuple[str, Role] = Depends(allowed(Role.OFFICER))) -> ReviewCase:
    if case_id != review_case.id:
        raise HTTPException(404, "Review case was not found.")
    before = review_case.model_dump(mode="json")
    review_case.status, review_case.assigned_officer = "RESOLVED", identity[0]
    review_case.reviewer_notes, review_case.resolution, review_case.resolved_at = decision.notes, decision.resolution, now()
    log(identity[0], "REVIEW_DECISION_RECORDED", "review_case", case_id, before=before, after=review_case.model_dump(mode="json"), reason=decision.notes)
    return review_case


@app.get("/api/v1/audit")
def get_audit(_: tuple[str, Role] = Depends(allowed(Role.OFFICER, Role.ADMIN))) -> dict[str, object]:
    return {"events": audit, "notice": "Audit contains only activity from this demo process."}


@app.get("/api/v1/parcels/{parcel_id}/report")
def report(parcel_id: str, _: tuple[str, Role] = Depends(allowed(Role.CITIZEN, Role.OFFICER, Role.ADMIN))) -> dict[str, object]:
    if parcel_id != "demo-parcel":
        raise HTTPException(404, "Parcel is not available in the demo dataset.")
    return {"title": "LANDSYNC AI Consistency Report", "mode": "SYNTHETIC DEMO", "disclaimer": "This advisory report does not establish ownership, title, or an official record.", "parcel": adapter.parcel(parcel_id), "review_case": review_case}
