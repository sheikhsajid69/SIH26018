"""
Data model definitions for LANDSYNC-India Synthetic Benchmark Dataset.
All models strictly adhere to the 100% Synthetic Data Policy and relational integrity specifications.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class VerificationStatus(StrEnum):
    VERIFIED_PRIMARY_SOURCE = "VERIFIED_PRIMARY_SOURCE"
    SECONDARY_SOURCE_ONLY = "SECONDARY_SOURCE_ONLY"
    NEEDS_LEGAL_REVIEW = "NEEDS_LEGAL_REVIEW"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    SUPERSEDED_OR_UNCERTAIN = "SUPERSEDED_OR_UNCERTAIN"


class RuleCategory(StrEnum):
    A_VERIFIED_PROCEDURAL_MANDATE = "A_VERIFIED_PROCEDURAL_MANDATE"
    B_CONFIGURABLE_DATA_QUALITY = "B_CONFIGURABLE_DATA_QUALITY"
    C_SYNTHETIC_BENCHMARK_ASSUMPTION = "C_SYNTHETIC_BENCHMARK_ASSUMPTION"
    D_LEGAL_INTERPRETATION_NEEDS_REVIEW = "D_LEGAL_INTERPRETATION_NEEDS_REVIEW"


class ValidationOutcome(StrEnum):
    MATCH = "MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    MISMATCH = "MISMATCH"
    MISSING = "MISSING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class FindingStatus(StrEnum):
    CONSISTENT = "CONSISTENT"
    RECORD_MISMATCH = "RECORD_MISMATCH"
    DOCUMENT_MISSING = "DOCUMENT_MISSING"
    SPATIAL_INCONSISTENCY = "SPATIAL_INCONSISTENCY"
    CHRONOLOGY_CONFLICT = "CHRONOLOGY_CONFLICT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"


# A. Parcel
class Parcel(BaseModel):
    parcel_id: str = Field(description="Deterministic synthetic primary key (e.g. SYN-PARCEL-000001)")
    synthetic_record_flag: bool = Field(default=True, description="Strict synthetic data flag, always true")
    jurisdiction_id: str = Field(description="Reference to jurisdiction profile (e.g. KA_PILOT)")
    village_code: str = Field(description="Synthetic village code")
    survey_number: str = Field(description="Survey number component (e.g. 101)")
    subdivision_number: str = Field(description="Hissa / subdivision component (e.g. 1 or 2A)")
    plot_number: str = Field(description="Plot or site number (for non-agricultural / layout)")
    parcel_type: str = Field(description="RURAL_AGRICULTURAL, URBAN_RESIDENTIAL, COMMERCIAL, etc.")
    land_classification: str = Field(description="Dry (Kushki), Wet (Tari), Garden (Bagayat), Non-Agri")
    area_value: float = Field(description="Numeric extent as stated in source record")
    area_unit: str = Field(description="Unit of area (acre, guntha, cent, sqm, bigha)")
    area_square_metres: float = Field(description="Normalized area in square metres (SI standard)")
    area_normalization_method: str = Field(description="STANDARD_SI_FORMULA, REGIONAL_SCHEDULE, UNRESOLVED_RULE13")
    boundary_geometry_id: str = Field(description="Foreign key to spatial_feature record")
    source_record_id: str = Field(description="Reference authority record ID (RTC/RoR)")
    record_effective_date: str = Field(description="ISO date when record became effective")
    record_status: str = Field(description="ACTIVE, HISTORICAL_SUPERSEDED, PENDING_MUTATION")
    provenance_id: str = Field(description="Foreign key to provenance record")


# B. Party
class Party(BaseModel):
    party_id: str = Field(description="Deterministic synthetic party key (e.g. SYN-PARTY-000001)")
    synthetic_record_flag: bool = Field(default=True, description="Always true")
    synthetic_display_name: str = Field(description="Synthetic landowner or entity name")
    party_type: str = Field(description="INDIVIDUAL, JOINT_FAMILY, CORPORATE_ENTITY, INSTITUTION")
    name_language: str = Field(default="en", description="Primary name script/language")
    name_variants: list[str] = Field(default_factory=list, description="Fictional aliases, transliterations, honorific variants")
    identity_reference_type: str = Field(description="SYNTHETIC_BENCHMARK_TOKEN (never real Aadhaar/PAN)")
    identity_reference_value: str = Field(description="Fictional reference value (e.g. SYN-ID-000001)")
    identity_reference_is_synthetic: bool = Field(default=True, description="Strict synthetic token flag")
    consent_or_authority_status: str = Field(description="SYNTHETIC_CONSENT_VERIFIED, NOT_APPLICABLE")


# C. Ownership Claim
class OwnershipClaim(BaseModel):
    claim_id: str = Field(description="Synthetic claim ID (e.g. SYN-CLAIM-000001)")
    parcel_id: str = Field(description="Foreign key to parcel")
    party_id: str = Field(description="Foreign key to party")
    claim_type: str = Field(description="SOLE_KHATEDAR, CO_PARCENER, JOINT_TENANT, LESSEE, MORTGAGOR")
    share_numerator: int = Field(description="Numerator of undivided interest (e.g. 1)")
    share_denominator: int = Field(description="Denominator of undivided interest (e.g. 1, 2, 4)")
    claim_start_date: str = Field(description="ISO start date of ownership claim")
    claim_end_date: str | None = Field(default=None, description="ISO end date if terminated/relinquished")
    source_document_id: str = Field(description="Supporting title document or mutation entry ID")
    source_status: str = Field(description="REGISTERED_DEED, MUTATION_ORDER, REVENUE_EXTRACT")
    verification_status: str = Field(description="RECORD_VERIFIED, PENDING_AUDIT, DISCREPANT")
    benchmark_note: str = Field(description="Synthetic context note regarding this claim")


# D. Document
class DocumentRecord(BaseModel):
    document_id: str = Field(description="Deterministic document ID (e.g. SYN-DOC-000001)")
    parcel_id: str = Field(description="Foreign key to parcel")
    document_type: str = Field(description="RECORD_OF_RIGHTS, SALE_DEED, PARTITION_DEED, GIFT_DEED, MORTGAGE_DEED, CADASTRAL_SKETCH")
    synthetic_filename: str = Field(description="Standardized synthetic filename")
    language: str = Field(default="en", description="Document language (en, kn, hi)")
    document_date: str = Field(description="ISO date of document execution/issue")
    registration_reference: str = Field(description="Synthetic book/volume/page or sro reference")
    issuing_office_type: str = Field(description="SUB_REGISTRAR_OFFICE, TEHSILDAR_OFFICE, SURVEY_SETTLEMENT_OFFICE")
    source_record_reference: str = Field(description="Synthetic office archive reference")
    page_count: int = Field(description="Number of pages in synthetic bundle")
    mime_type: str = Field(description="text/plain, application/pdf, image/png")
    document_quality: str = Field(description="PRISTINE, CLEAN, SCANNED_FAINT, OCR_DEGRADED")
    synthetic_document_flag: bool = Field(default=True, description="Strict synthetic data flag")
    content_hash: str = Field(description="SHA-256 digest of document content")
    extraction_status: str = Field(description="EXTRACTED, EXTRACTION_FAILED, UNPROCESSED")
    provenance_id: str = Field(description="Foreign key to provenance record")


# E. Document Field
class DocumentField(BaseModel):
    field_id: str = Field(description="Synthetic field annotation ID (e.g. SYN-FIELD-000001)")
    document_id: str = Field(description="Foreign key to document")
    field_name: str = Field(description="owner, survey_number, subdivision_number, plot_number, area, village, land_use, date")
    raw_value: str = Field(description="Raw text as extracted by simulated OCR/NER")
    ground_truth_value: str = Field(description="True underlying value in document")
    normalized_value: str = Field(description="Clean normalized representation")
    data_type: str = Field(description="STRING, NUMERIC, DATE, AREA")
    unit: str | None = Field(default=None, description="Extracted unit if applicable (acre, guntha, etc.)")
    page_number: int = Field(default=1, description="Page number of annotation (1-indexed)")
    bounding_box: list[int] = Field(default_factory=lambda: [0, 0, 0, 0], description="Normalized [ymin, xmin, ymax, xmax] coordinates (0-1000 scale)")
    extraction_method: str = Field(description="OCR_TRANSCRIPTION, REGEX_PATTERN, NER_ENTITY, LAYOUT_LM")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    noise_type: str = Field(description="NONE, CHAR_SUBSTITUTION, DROPPED_CHAR, WHITESPACE_VARIATION, LOW_RES")
    annotation_status: str = Field(description="VERIFIED_GROUND_TRUTH, SYNTHETIC_SIMULATED")


# F. Mutation Event
class MutationEvent(BaseModel):
    mutation_event_id: str = Field(description="Synthetic mutation key (e.g. SYN-MUT-000001)")
    parcel_id: str = Field(description="Foreign key to parcel")
    event_type: str = Field(description="SALE_TRANSFER, INHERITANCE_SUCCESSION, PARTITION, CONVERSION, MORTGAGE_CHARGE, RELEASE")
    application_date: str = Field(description="ISO date of mutation application (Sec 128 KLRA)")
    event_date: str = Field(description="ISO date of deed or triggering legal event")
    effective_date: str = Field(description="ISO date when mutation order took legal effect")
    recorded_date: str = Field(description="ISO date entered into revenue register")
    source_document_id: str = Field(description="Foreign key to registered instrument")
    previous_claim_id: str | None = Field(default=None, description="Previous ownership claim modified/extinguished")
    resulting_claim_id: str | None = Field(default=None, description="New ownership claim created")
    event_status: str = Field(description="SANCTIONED, PENDING_OBJECTION, REJECTED, APPEALED")
    event_sequence: int = Field(description="Chronological sequence order on this parcel")
    benchmark_expected_outcome: str = Field(description="MATCH, CHRONOLOGY_CONFLICT, EVIDENCE_MISSING, UNAPPROVED")


# G. Encumbrance or Interest
class EncumbranceRecord(BaseModel):
    interest_id: str = Field(description="Synthetic interest key (e.g. SYN-INT-000001)")
    parcel_id: str = Field(description="Foreign key to parcel")
    interest_type: str = Field(description="MORTGAGE_SIMPLE, MORTGAGE_EQUITABLE, EASEMENT_RIGHT_OF_WAY, STATUTORY_CHARGE, ACQUISITION_NOTICE")
    source_document_id: str = Field(description="Foreign key to document creating/recording interest")
    effective_from: str = Field(description="ISO start date of charge/interest")
    effective_until: str | None = Field(default=None, description="ISO end/discharge date if released")
    status: str = Field(description="ACTIVE, DISCHARGED, DISPUTED, UNCERTAIN")
    source_verification_status: str = Field(description="REGISTERED_CHARGE, REVENUE_NOTED, UNVERIFIED")
    benchmark_note: str = Field(description="Synthetic scenario context")


# H. Spatial Feature
class SpatialFeature(BaseModel):
    geometry_id: str = Field(description="Synthetic geometry key (e.g. SYN-GEOM-000001)")
    parcel_id: str = Field(description="Foreign key to parcel")
    geometry_type: str = Field(default="Polygon", description="GeoJSON geometry type (Polygon, MultiPolygon)")
    coordinate_reference_system: str = Field(default="EPSG:4326", description="CRS of coordinate pairs")
    geometry: dict[str, Any] = Field(description="GeoJSON geometry object")
    area_from_geometry: float = Field(description="Geodesic / projected area computed in square metres")
    perimeter_from_geometry: float = Field(description="Perimeter computed in metres")
    geometry_validity: str = Field(description="VALID, SELF_INTERSECTING, UNCLOSED_RING, DEGENERATE_COORDINATES")
    spatial_quality_status: str = Field(description="CONSISTENT, SPATIAL_VARIANCE_DETECTED, OVERLAP_ANOMALY, SLIVER_GAP")
    source_reference: str = Field(description="CADASTRAL_MAP_OFFICIAL, BLUEPRINT_SURVEY_SKETCH, GPS_FIELD_SURVEY")
    synthetic_geometry_flag: bool = Field(default=True, description="Always true")


# I. Validation Case
class ValidationCase(BaseModel):
    case_id: str = Field(description="Synthetic case ID (e.g. SYN-CASE-000001)")
    primary_parcel_id: str = Field(description="Foreign key to parcel under validation")
    scenario_family: str = Field(description="Scenario category (CORE_CONSISTENCY, SPATIAL_VALIDATION, etc.)")
    scenario_tags: list[str] = Field(default_factory=list, description="Descriptive tags")
    difficulty: str = Field(description="EASY, MEDIUM, HARD, ADVERSARIAL")
    input_record_ids: list[str] = Field(description="List of parcel, document, extraction, and geometry IDs")
    expected_outcome: ValidationOutcome = Field(description="MATCH, PARTIAL_MATCH, MISMATCH, MISSING, REVIEW_REQUIRED")
    expected_reason_codes: list[str] = Field(description="Standardized reason codes")
    expected_rule_ids: list[str] = Field(description="Legal and data quality rule IDs triggered")
    review_required: bool = Field(description="Whether a human officer decision is required")
    ground_truth_confidence: float = Field(ge=0.0, le=1.0, description="Benchmark certainty score")
    split_group_id: str = Field(description="Group ID for leakage-safe train/val/test splits")
    generator_version: str = Field(default="1.0.0")
    seed_reference: int = Field(default=42)


# J. Validation Finding
class ValidationFinding(BaseModel):
    finding_id: str = Field(description="Synthetic finding ID (e.g. SYN-FIND-000001)")
    case_id: str = Field(description="Foreign key to validation case")
    field_name: str = Field(description="Attribute evaluated (owner, area, survey_number, boundary, etc.)")
    source_value: str = Field(description="Value from submitted document")
    comparison_value: str = Field(description="Value from authoritative reference record")
    normalized_source_value: str = Field(description="Normalized source value")
    normalized_comparison_value: str = Field(description="Normalized reference value")
    rule_id: str = Field(description="Rule ID governing comparison")
    finding_status: FindingStatus = Field(description="Neutral status (RECORD_MISMATCH, SPATIAL_INCONSISTENCY, etc.)")
    severity: str = Field(description="NONE, LOW, MEDIUM, HIGH")
    explanation: str = Field(description="Detailed explainable finding rationale")
    review_required: bool = Field(description="Whether this individual finding mandates review")


# K. Audit Event
class SyntheticAuditEvent(BaseModel):
    audit_event_id: str = Field(description="Synthetic audit key (e.g. SYN-AUDIT-000001)")
    actor_id: str = Field(description="Synthetic actor ID (e.g. SYN-USER-OFFICER-001)")
    actor_role: str = Field(description="citizen, revenue_officer, administrator, system_engine")
    action_type: str = Field(description="DOCUMENT_INGEST, VALIDATION_RUN, CASE_REVIEW, DECISION_RECORDED")
    resource_type: str = Field(description="parcel, document, validation_case, mutation")
    resource_id: str = Field(description="ID of entity acted upon")
    event_timestamp: str = Field(description="ISO timestamp of event")
    reason: str = Field(description="Administrative justification or trigger")
    result: str = Field(description="SUCCESS, REVIEW_REQUIRED, REJECTED")
    synthetic_event_flag: bool = Field(default=True, description="Strict synthetic data flag")


# L. Rule Catalogue
class LegalRuleRecord(BaseModel):
    rule_id: str = Field(description="Unique rule ID (e.g. RULE-REG-1908-SEC17, RULE-AREA-TOL-001)")
    title: str = Field(description="Human-readable title of legal provision or quality check")
    jurisdiction: str = Field(description="IN_CENTRAL, IN_KARNATAKA, TECHNICAL_COMMON")
    instrument_type: str = Field(description="CENTRAL_ACT, STATE_ACT, STATE_RULE, TECHNICAL_SPECIFICATION")
    official_source_url: str = Field(description="Authoritative source URL (e.g. indiacode.nic.in, dharani/bhoomi)")
    provision_reference: str = Field(description="Specific statutory section / order clause")
    short_neutral_summary: str = Field(description="Objective summary of procedural requirement")
    applicable_workflow: str = Field(description="CONVEYANCE_REGISTRATION, MUTATION, BOUNDARY_SURVEY, DATA_QUALITY")
    effective_from: str = Field(description="Date or historical statute commencement")
    effective_until: str | None = Field(default=None, description="Date repealed or superseded, if any")
    source_last_verified_at: str = Field(description="Date verified against authoritative legal repository")
    amendment_status: str = Field(description="CURRENT, AMENDED, REPEALED, PROPOSED")
    verification_status: VerificationStatus = Field(description="VERIFIED_PRIMARY_SOURCE, NEEDS_LEGAL_REVIEW, etc.")
    reviewer_notes: str = Field(description="Legal analyst review observations")
    limitations: str = Field(description="Boundary conditions and jurisdictions where rule does not apply")
    dataset_scenarios_using_rule: list[str] = Field(description="Scenarios triggering this rule")
    rule_category: RuleCategory = Field(description="A, B, C, or D category distinguishing mandates from heuristics")


# M. Provenance
class ProvenanceRecord(BaseModel):
    provenance_id: str = Field(description="Synthetic provenance key (e.g. SYN-PROV-000001)")
    source_type: str = Field(description="DETERMINISTIC_SYNTHETIC_GENERATOR")
    source_reference: str = Field(description="Generator engine configuration and pipeline module")
    generation_method: str = Field(description="PSEUDO_RANDOM_STRATIFIED_SAMPLING")
    generator_version: str = Field(default="1.0.0")
    generation_seed: int = Field(default=42)
    transformation_history: str = Field(description="Summary of normalizations and transformations applied")
    creation_timestamp: str = Field(description="ISO creation timestamp")
    license_reference: str = Field(description="CC-BY-4.0 (Dataset) / MIT (Software Code)")
    synthetic_status: str = Field(default="100% SYNTHETIC DATA — NOT AN OFFICIAL GOVERNMENT RECORD")
