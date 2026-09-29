from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from landsync.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(256), nullable=True)
    role: Mapped[str] = mapped_column(String(32), index=True)  # citizen, revenue_officer, administrator
    name: Mapped[str] = mapped_column(String(256))
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(256), nullable=True)
    permitted_parcels: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class LandParcelOrm(Base):
    __tablename__ = "land_parcels"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    ulpin: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    survey_number: Mapped[str] = mapped_column(String(64), index=True)
    plot_number: Mapped[str] = mapped_column(String(64), index=True)
    owner: Mapped[str] = mapped_column(String(256), index=True)
    area: Mapped[str] = mapped_column(String(64))
    area_unit: Mapped[str] = mapped_column(String(32), default="acre")
    normalized_area_sqm: Mapped[float] = mapped_column(Float, default=0.0)
    state: Mapped[str] = mapped_column(String(128), default="Karnataka")
    district: Mapped[str] = mapped_column(String(128), default="Synthetic District")
    tehsil: Mapped[str] = mapped_column(String(128), default="Demo Taluk")
    village: Mapped[str] = mapped_column(String(128), index=True)
    land_use: Mapped[str] = mapped_column(String(64), default="Agricultural")
    geometry: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    geometry_source: Mapped[str] = mapped_column(String(256), default="SYNTHETIC DEMO GeoJSON (EPSG:4326)")
    authoritative_source: Mapped[str] = mapped_column(String(256), default="SYNTHETIC DEMO authority record")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    ownerships: Mapped[list[OwnershipRelationshipOrm]] = relationship(
        "OwnershipRelationshipOrm", back_populates="parcel", cascade="all, delete-orphan"
    )
    mutations: Mapped[list[MutationEventOrm]] = relationship(
        "MutationEventOrm", back_populates="parcel", cascade="all, delete-orphan"
    )
    documents: Mapped[list[DocumentOrm]] = relationship(
        "DocumentOrm", back_populates="parcel", cascade="all, delete-orphan"
    )
    review_cases: Mapped[list[ReviewCaseOrm]] = relationship(
        "ReviewCaseOrm", back_populates="parcel", cascade="all, delete-orphan"
    )


class OwnershipRelationshipOrm(Base):
    __tablename__ = "ownership_relationships"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    parcel_id: Mapped[str] = mapped_column(String(64), ForeignKey("land_parcels.id"), index=True)
    holder_name: Mapped[str] = mapped_column(String(256), index=True)
    share_extent: Mapped[str] = mapped_column(String(64), default="100%")
    relationship_type: Mapped[str] = mapped_column(String(64), default="SOLE_PROPRIETOR")
    recorded_date: Mapped[str] = mapped_column(String(32))
    source_ref: Mapped[str] = mapped_column(String(256))
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)

    parcel: Mapped[LandParcelOrm] = relationship("LandParcelOrm", back_populates="ownerships")


class MutationEventOrm(Base):
    __tablename__ = "mutation_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    parcel_id: Mapped[str] = mapped_column(String(64), ForeignKey("land_parcels.id"), index=True)
    mutation_number: Mapped[str] = mapped_column(String(128), index=True)
    event_type: Mapped[str] = mapped_column(String(64))  # PARTITION, SUCCESSION, DEMARCATION, SALE
    recorded_date: Mapped[str] = mapped_column(String(32))
    parties_involved: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    order_reference: Mapped[str] = mapped_column(String(256))
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)

    parcel: Mapped[LandParcelOrm] = relationship("LandParcelOrm", back_populates="mutations")


class DocumentOrm(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    parcel_id: Mapped[str] = mapped_column(String(64), ForeignKey("land_parcels.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(128))
    original_file_name: Mapped[str] = mapped_column(String(256))
    mime_type: Mapped[str] = mapped_column(String(64))
    storage_key: Mapped[str] = mapped_column(String(512), unique=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    file_size: Mapped[int] = mapped_column(BigInteger)
    source: Mapped[str] = mapped_column(String(64), default="USER_UPLOAD")
    uploaded_by: Mapped[str] = mapped_column(String(128))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    version: Mapped[int] = mapped_column(Integer, default=1)
    processing_status: Mapped[str] = mapped_column(String(32), default="COMPLETED")

    parcel: Mapped[LandParcelOrm] = relationship("LandParcelOrm", back_populates="documents")
    extraction: Mapped[ExtractionOrm | None] = relationship(
        "ExtractionOrm", back_populates="document", uselist=False, cascade="all, delete-orphan"
    )


class ExtractionOrm(Base):
    __tablename__ = "extractions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(64), ForeignKey("documents.id"), unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(128))
    model_version: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    document: Mapped[DocumentOrm] = relationship("DocumentOrm", back_populates="extraction")
    fields: Mapped[list[ExtractedFieldOrm]] = relationship(
        "ExtractedFieldOrm", back_populates="extraction", cascade="all, delete-orphan"
    )


class ExtractedFieldOrm(Base):
    __tablename__ = "extracted_fields"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    extraction_id: Mapped[str] = mapped_column(String(64), ForeignKey("extractions.id"), index=True)
    field_name: Mapped[str] = mapped_column(String(64), index=True)
    extracted_value: Mapped[str] = mapped_column(Text)
    normalized_value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    source_location: Mapped[str] = mapped_column(String(256))
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    extraction_method: Mapped[str] = mapped_column(String(64))
    reviewer_status: Mapped[str] = mapped_column(String(32), default="PENDING")

    extraction: Mapped[ExtractionOrm] = relationship("ExtractionOrm", back_populates="fields")


class ValidationResultOrm(Base):
    __tablename__ = "validation_results"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    parcel_id: Mapped[str] = mapped_column(String(64), ForeignKey("land_parcels.id"), index=True)
    document_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("documents.id"), nullable=True, index=True)
    field: Mapped[str] = mapped_column(String(64), index=True)
    source_a: Mapped[str] = mapped_column(String(128))
    value_a: Mapped[str] = mapped_column(Text)
    source_b: Mapped[str] = mapped_column(String(128))
    value_b: Mapped[str] = mapped_column(Text)
    comparison_operator: Mapped[str] = mapped_column(String(64))
    result: Mapped[str] = mapped_column(String(32), index=True)  # MATCH, PARTIAL_MATCH, MISMATCH, MISSING, REVIEW_REQUIRED
    confidence: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(32))  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ReviewCaseOrm(Base):
    __tablename__ = "review_cases"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    parcel_id: Mapped[str] = mapped_column(String(64), ForeignKey("land_parcels.id"), index=True)
    document_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("documents.id"), nullable=True)
    reason: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(32), default="MEDIUM")
    status: Mapped[str] = mapped_column(String(32), default="OPEN", index=True)  # OPEN, IN_REVIEW, RESOLVED
    priority: Mapped[str] = mapped_column(String(32), default="P2_NORMAL")  # P1_HIGH, P2_NORMAL, P3_ADVISORY
    discrepancy_field: Mapped[str | None] = mapped_column(String(64), nullable=True)
    claimed_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    authoritative_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_officer: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution: Mapped[str | None] = mapped_column(String(64), nullable=True)  # ACCEPTED_FOR_CORRECTION, REQUIRES_DOCUMENT, NO_ACTION, REJECTED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    parcel: Mapped[LandParcelOrm] = relationship("LandParcelOrm", back_populates="review_cases")


class AuditEventOrm(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(String(128), index=True)
    action: Mapped[str] = mapped_column(String(128), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(128), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    before_state: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_id: Mapped[str] = mapped_column(String(64), index=True)


class AdministrativeActionOrm(Base):
    __tablename__ = "administrative_actions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    action_type: Mapped[str] = mapped_column(String(64), index=True)
    actor_id: Mapped[str] = mapped_column(String(128), index=True)
    actor_role: Mapped[str] = mapped_column(String(32), default="administrator")
    target_resource_type: Mapped[str] = mapped_column(String(64), index=True)
    target_resource_id: Mapped[str] = mapped_column(String(128), index=True)
    reason: Mapped[str] = mapped_column(Text)
    before_state: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="EXECUTED")
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


# Composite indexes for high-throughput queries
Index("idx_parcels_survey_village", LandParcelOrm.survey_number, LandParcelOrm.village)
Index("idx_review_cases_status_priority", ReviewCaseOrm.status, ReviewCaseOrm.priority)
Index("idx_audit_events_entity", AuditEventOrm.entity_type, AuditEventOrm.entity_id)
Index("idx_admin_actions_actor", AdministrativeActionOrm.actor_id, AdministrativeActionOrm.created_at)
