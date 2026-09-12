from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def now() -> datetime:
    return datetime.now(timezone.utc)


class Role(StrEnum):
    CITIZEN = "citizen"
    OFFICER = "revenue_officer"
    ADMIN = "administrator"


class ValidationState(StrEnum):
    MATCH = "MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    MISMATCH = "MISMATCH"
    MISSING = "MISSING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class ExtractedField(BaseModel):
    field_name: str
    extracted_value: str
    normalized_value: str
    confidence: float = Field(ge=0, le=1)
    source_location: str
    page_number: int = 1
    extraction_method: str
    reviewer_status: str = "PENDING"


class Extraction(BaseModel):
    provider: str
    model_version: str
    created_at: datetime = Field(default_factory=now)
    fields: list[ExtractedField]


class Document(BaseModel):
    id: str
    parcel_id: str
    document_type: str
    original_file_name: str
    mime_type: str
    storage_key: str
    sha256: str
    file_size: int
    source: str = "USER_UPLOAD"
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=now)
    version: int = 1
    processing_status: str = "COMPLETED"
    extraction: Extraction | None = None


class ValidationResult(BaseModel):
    field: str
    source_a: str
    value_a: str
    source_b: str
    value_b: str
    comparison_operator: str
    result: ValidationState
    confidence: float = Field(ge=0, le=1)
    severity: str
    explanation: str
    created_at: datetime = Field(default_factory=now)


class ReviewCase(BaseModel):
    id: str
    parcel_id: str
    reason: str
    severity: str
    status: str = "OPEN"
    assigned_officer: str | None = None
    reviewer_notes: str | None = None
    resolution: str | None = None
    created_at: datetime = Field(default_factory=now)
    resolved_at: datetime | None = None


class AuditEvent(BaseModel):
    actor_id: str
    action: str
    entity_type: str
    entity_id: str
    timestamp: datetime = Field(default_factory=now)
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    reason: str | None = None
    trace_id: str


class ReviewDecision(BaseModel):
    resolution: str = Field(pattern="^(ACCEPTED_FOR_CORRECTION|REQUIRES_DOCUMENT|NO_ACTION)$")
    notes: str = Field(min_length=3, max_length=1000)
