"""
Deterministic synthetic identifiers generator.
Strict synthetic data policy: No real government identity numbers (Aadhaar, PAN, authentic ULPIN).
All tokens are clearly prefixed with SYN- and documented as benchmark identifiers.
"""

from __future__ import annotations

import hashlib


def parcel_id(seq: int) -> str:
    return f"SYN-PARCEL-{seq:06d}"


def synthetic_ulpin(state_code: str, seq: int) -> str:
    # Fictional internal benchmark token, explicitly prefixed with SYN-ULPIN-
    return f"SYN-ULPIN-{state_code}-{seq:06d}"


def party_id(seq: int) -> str:
    return f"SYN-PARTY-{seq:06d}"


def claim_id(seq: int) -> str:
    return f"SYN-CLAIM-{seq:06d}"


def document_id(seq: int) -> str:
    return f"SYN-DOC-{seq:06d}"


def field_id(seq: int) -> str:
    return f"SYN-FIELD-{seq:06d}"


def mutation_id(seq: int) -> str:
    return f"SYN-MUT-{seq:06d}"


def encumbrance_id(seq: int) -> str:
    return f"SYN-INT-{seq:06d}"


def geometry_id(seq: int) -> str:
    return f"SYN-GEOM-{seq:06d}"


def validation_case_id(seq: int) -> str:
    return f"SYN-CASE-{seq:06d}"


def validation_finding_id(seq: int) -> str:
    return f"SYN-FIND-{seq:06d}"


def audit_event_id(seq: int) -> str:
    return f"SYN-AUDIT-{seq:06d}"


def provenance_id(seq: int) -> str:
    return f"SYN-PROV-{seq:06d}"


def split_group_id(parcel_seq: int) -> str:
    # Split group links all documents, claims, geometries, and findings of a parcel family
    group_num = (parcel_seq - 1) // 5 + 1
    return f"GRP-{group_num:05d}"


def synthetic_registration_ref(office_code: str, year: int, book: int, seq: int) -> str:
    return f"SYN-SRO-{office_code}/BK{book}/{seq:04d}/{year}"


def synthetic_identity_reference(seq: int) -> str:
    # Clearly fictional token, never matches 12-digit Aadhaar or 10-char PAN format
    return f"SYN-ID-BENCHMARK-{seq:07d}"


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
