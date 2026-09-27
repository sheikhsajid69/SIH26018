from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from landsync.database import get_db

router = APIRouter(tags=["Health & Probes"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "LANDSYNC AI",
        "mode": "DEMO_SYNTHETIC_ONLY",
        "notice": "All records and model extractions are synthetic. No live government database is connected.",
    }


@router.get("/health/live")
def liveness() -> dict[str, str]:
    """Kubernetes / Cloud liveness probe: returns 200 OK if service process is running."""
    return {"status": "alive"}


@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    """
    Kubernetes / Cloud readiness probe.
    Verifies database connection and schema responsiveness.
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "service": "LANDSYNC AI",
        }
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "error",
                "detail": str(exc),
            },
        )
