from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from landsync.adapters.state.demo import DemoAuthorityAdapter
from landsync.auth import DEMO_TOKENS, get_current_user, require_roles
from landsync.blueprint import MockBlueprintProvider
from landsync.database import SessionLocal, init_db
from landsync.db_models import LandParcelOrm
from landsync.models import AuditEvent, Document, ReviewCase, Role
from landsync.routers import (
    admin,
    auth,
    audit as audit_router,
    documents as documents_router,
    health,
    parcels,
    review_cases as review_cases_router,
    validation,
)
from landsync.services import LocalEvidenceStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes database schema and ensures baseline synthetic demo data is seeded.
    """
    init_db()
    # Auto-seed if database is newly initialized
    db = SessionLocal()
    try:
        if db.query(LandParcelOrm).count() == 0:
            import sys
            from pathlib import Path
            root_dir = Path(__file__).resolve().parents[3]
            sys.path.insert(0, str(root_dir / "scripts"))
            try:
                import seed_demo
                seed_demo.seed()
            except Exception as e:
                print(f"[!] Auto-seed note: {e}")
    finally:
        db.close()
    yield


app = FastAPI(
    title="LANDSYNC AI Intelligence & Consistency Validation API",
    version="1.0.0",
    description=(
        "Production-ready AI-assisted land-record intelligence, consistency-validation, "
        "provenance, GIS, and interoperability platform for SIH26018 (Team Void). "
        "All demonstration records are synthetic fixtures; no live government registry is contacted."
    ),
    lifespan=lifespan,
)

# CORS setup
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.middleware("http")
async def add_observability_headers(request: Request, call_next) -> Response:
    """Traceability & latency middleware: injects X-Request-ID and X-Response-Time-Ms."""
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
    return response


# Include modular routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(parcels.router)
app.include_router(documents_router.router)
app.include_router(validation.router)
app.include_router(review_cases_router.router)
app.include_router(audit_router.router)
app.include_router(admin.router)

# Legacy aliases for backward-compatibility with tests and existing imports
adapter = DemoAuthorityAdapter()
store = LocalEvidenceStore(os.getenv("LOCAL_STORAGE_ROOT", ".landsync-storage"))
blueprint_provider = MockBlueprintProvider()
audit: list[AuditEvent] = []
documents: list[Document] = []
review_cases: dict[str, ReviewCase] = {}
TOKENS = DEMO_TOKENS
actor = get_current_user
allowed = require_roles


def log(actor_id: str, action: str, entity_type: str, entity_id: str, *, before=None, after=None, reason=None) -> None:
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
