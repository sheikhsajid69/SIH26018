from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

from landsync.models import (
    Document,
    ExtractedField,
    Extraction,
    ValidationResult,
    ValidationState,
)
from landsync.units import normalize_land_unit, parse_area_string


class LocalEvidenceStore:
    """
    Local development evidence store.
    Content-addressed SHA-256 storage keys prevent arbitrary path traversal.
    """

    def __init__(self, root: str) -> None:
        self.root = Path(root)

    def save(self, parcel_id: str, body: bytes) -> tuple[str, str]:
        digest = hashlib.sha256(body).hexdigest()
        key = f"documents/demo/{parcel_id}/{digest}/1/original"
        target = self.root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        return key, digest

    def get(self, storage_key: str) -> bytes | None:
        target = self.root / storage_key
        # Strict boundary defense
        try:
            resolved = target.resolve()
            if not str(resolved).startswith(str(self.root.resolve())):
                raise ValueError("Path traversal attempt detected")
            if resolved.is_file():
                return resolved.read_bytes()
        except Exception:
            return None
        return None


class MockDocumentProvider:
    """
    Deterministic substitute for OCR and document extraction.
    Advertises itself as a mock at every boundary (Rules 1 & 12).
    """

    provider = "mock-document-ai"
    model_version = "demo-1.2"

    def extract(self) -> Extraction:
        return Extraction(
            provider=self.provider,
            model_version=self.model_version,
            fields=[
                ExtractedField(
                    field_name="owner",
                    extracted_value="Ramesh Kumar",
                    normalized_value="ramesh kumar",
                    confidence=0.97,
                    source_location="page 1, block A, line 2",
                    extraction_method="MOCK_OCR_NER",
                ),
                ExtractedField(
                    field_name="survey_number",
                    extracted_value="124/2",
                    normalized_value="124/2",
                    confidence=0.99,
                    source_location="page 1, schedule section, row 3",
                    extraction_method="MOCK_OCR_NER",
                ),
                ExtractedField(
                    field_name="plot_number",
                    extracted_value="18B",
                    normalized_value="18b",
                    confidence=0.94,
                    source_location="page 1, schedule section, row 4",
                    extraction_method="MOCK_OCR_NER",
                ),
                ExtractedField(
                    field_name="area",
                    extracted_value="2.31 acre",
                    normalized_value="2.31 acre",
                    confidence=0.88,
                    source_location="page 1, schedule property extent, row 6",
                    extraction_method="MOCK_OCR_NER",
                ),
                ExtractedField(
                    field_name="village",
                    extracted_value="Sampurna",
                    normalized_value="sampurna",
                    confidence=0.95,
                    source_location="page 1, property address, row 8",
                    extraction_method="MOCK_OCR_NER",
                ),
                ExtractedField(
                    field_name="land_use",
                    extracted_value="Agricultural",
                    normalized_value="agricultural",
                    confidence=0.92,
                    source_location="page 2, recital clause 4",
                    extraction_method="MOCK_OCR_NER",
                ),
            ],
        )


def make_document(
    parcel_id: str,
    file_name: str,
    content_type: str,
    body: bytes,
    actor: str,
    store: LocalEvidenceStore,
) -> Document:
    key, digest = store.save(parcel_id, body)
    return Document(
        id=f"doc-{uuid4().hex[:12]}",
        parcel_id=parcel_id,
        document_type="REGISTERED_DEED_OR_EXTRACT",
        original_file_name=Path(file_name).name,
        mime_type=content_type,
        storage_key=key,
        sha256=digest,
        file_size=len(body),
        uploaded_by=actor,
        extraction=MockDocumentProvider().extract(),
    )


def validate_owner(extracted_raw: str, authority_raw: str, confidence: float) -> tuple[ValidationState, str, str]:
    clean_extracted = extracted_raw.strip().lower()
    clean_auth = authority_raw.strip().lower().replace(" (synthetic demo person)", "").strip()

    if clean_extracted == clean_auth:
        return (
            ValidationState.MATCH,
            "NONE",
            f"Extracted holder name '{extracted_raw}' matches authoritative record '{clean_auth}'."
        )
    elif clean_extracted in clean_auth or clean_auth in clean_extracted:
        return (
            ValidationState.PARTIAL_MATCH,
            "LOW",
            f"Partial name match ('{extracted_raw}' vs '{authority_raw}'). Possible honorific or alias."
        )
    else:
        return (
            ValidationState.MISMATCH,
            "HIGH",
            f"Holder mismatch: Document specifies '{extracted_raw}', but authoritative record specifies '{authority_raw}'."
        )


def validate_area(extracted_raw: str, authority_raw: str, confidence: float) -> tuple[ValidationState, str, str]:
    num_ext, unit_ext = parse_area_string(extracted_raw)
    num_auth, unit_auth = parse_area_string(authority_raw)

    conv_ext = normalize_land_unit(num_ext, unit_ext)
    conv_auth = normalize_land_unit(num_auth, unit_auth)

    if conv_ext.is_ambiguous or conv_auth.is_ambiguous:
        return (
            ValidationState.REVIEW_REQUIRED,
            "HIGH",
            f"Ambiguous land unit encountered ({unit_ext} or {unit_auth}). Conversion requires officer calibration."
        )

    if conv_ext.normalized_area_sqm is not None and conv_auth.normalized_area_sqm is not None:
        delta_sqm = abs(conv_ext.normalized_area_sqm - conv_auth.normalized_area_sqm)
        mean_sqm = (conv_ext.normalized_area_sqm + conv_auth.normalized_area_sqm) / 2.0
        pct_diff = (delta_sqm / mean_sqm) * 100.0 if mean_sqm > 0 else 0.0

        if pct_diff < 0.2:  # very minor rounding difference
            return (
                ValidationState.MATCH,
                "NONE",
                f"Area values match within 0.2% tolerance ({conv_ext.formula} vs {conv_auth.formula})."
            )
        elif pct_diff < 1.0:
            return (
                ValidationState.PARTIAL_MATCH,
                "LOW",
                f"Minor area variance of {pct_diff:.2f}% detected ({delta_sqm:.2f} m²). Advisory review recommended."
            )
        else:
            delta_acre = abs(num_ext - num_auth)
            return (
                ValidationState.MISMATCH,
                "MEDIUM",
                (
                    f"Area discrepancy detected: Submitted document reports {extracted_raw} (~{conv_ext.normalized_area_sqm:.1f} m²), "
                    f"while synthetic authority record reports {authority_raw} (~{conv_auth.normalized_area_sqm:.1f} m²). "
                    f"Variance of {delta_acre:.2f} acre ({delta_sqm:.1f} m²). Human verification required."
                )
            )

    return (ValidationState.REVIEW_REQUIRED, "MEDIUM", "Unable to compute area equivalence safely.")


def validate(extraction: Extraction, authority: dict[str, object]) -> list[ValidationResult]:
    """
    Core validation engine comparing extracted document evidence against authorized authority reference.
    Strictly adheres to Rule 2 (Authoritative data wins) and Rule 8 (Route discrepancies to human review).
    """
    extracted_dict = {field.field_name: field for field in extraction.fields}
    results: list[ValidationResult] = []

    fields_to_check = [
        ("owner", "owner"),
        ("survey_number", "survey_number"),
        ("plot_number", "plot_number"),
        ("area", "area"),
        ("village", "village"),
        ("land_use", "land_use"),
    ]

    for doc_field, auth_field in fields_to_check:
        auth_val = str(authority.get(auth_field, "")).strip()
        if not auth_val:
            # Field missing in authoritative record
            results.append(
                ValidationResult(
                    field=doc_field,
                    source_a="AI-extracted document (MOCK)",
                    value_a=extracted_dict[doc_field].extracted_value if doc_field in extracted_dict else "MISSING",
                    source_b="SYNTHETIC DEMO authority record",
                    value_b="NOT_SPECIFIED",
                    comparison_operator="existence",
                    result=ValidationState.MISSING,
                    confidence=0.90,
                    severity="LOW",
                    explanation=f"Field '{doc_field}' is not recorded in the authority profile.",
                )
            )
            continue

        if doc_field not in extracted_dict:
            # Field missing in extracted document
            results.append(
                ValidationResult(
                    field=doc_field,
                    source_a="AI-extracted document (MOCK)",
                    value_a="MISSING",
                    source_b="SYNTHETIC DEMO authority record",
                    value_b=auth_val,
                    comparison_operator="existence",
                    result=ValidationState.MISSING,
                    confidence=0.90,
                    severity="MEDIUM",
                    explanation=f"Field '{doc_field}' could not be extracted from the uploaded document.",
                )
            )
            continue

        extracted = extracted_dict[doc_field]
        val_a = extracted.extracted_value
        conf = extracted.confidence

        # Field-specific validation
        if doc_field == "owner":
            state, severity, expl = validate_owner(val_a, auth_val, conf)
        elif doc_field == "area":
            state, severity, expl = validate_area(val_a, auth_val, conf)
        else:
            # Normalized string equality
            clean_a = extracted.normalized_value.lower()
            clean_b = auth_val.lower()
            if clean_a == clean_b:
                state = ValidationState.MATCH
                severity = "NONE"
                expl = f"Field '{doc_field}' matches authoritative record ('{val_a}')."
            else:
                state = ValidationState.MISMATCH
                severity = "MEDIUM"
                expl = f"Discrepancy in '{doc_field}': Document specifies '{val_a}', but authoritative record has '{auth_val}'."

        # Rule 8: Low confidence automatically flags for review
        if conf < 0.80 and state == ValidationState.MATCH:
            state = ValidationState.REVIEW_REQUIRED
            severity = "LOW"
            expl += f" (Advisory: Low extraction confidence of {conf * 100:.0f}%; human spot-check recommended.)"

        results.append(
            ValidationResult(
                field=doc_field,
                source_a="AI-extracted document (MOCK)",
                value_a=val_a,
                source_b="SYNTHETIC DEMO authority record",
                value_b=auth_val,
                comparison_operator="normalized comparison",
                result=state,
                confidence=conf,
                severity=severity,
                explanation=expl,
            )
        )

    return results
