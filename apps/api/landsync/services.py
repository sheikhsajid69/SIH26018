from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

from .models import Document, ExtractedField, Extraction, ValidationResult, ValidationState


class LocalEvidenceStore:
    """Local development evidence store. Content-addressed names prevent path traversal."""

    def __init__(self, root: str) -> None:
        self.root = Path(root)

    def save(self, parcel_id: str, body: bytes) -> tuple[str, str]:
        digest = hashlib.sha256(body).hexdigest()
        key = f"documents/demo/{parcel_id}/{digest}/1/original"
        target = self.root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        return key, digest


class MockDocumentProvider:
    """Deterministic substitute for OCR; it advertises itself as a mock at every boundary."""

    provider = "mock-document-ai"
    model_version = "demo-1.0"

    def extract(self) -> Extraction:
        return Extraction(
            provider=self.provider,
            model_version=self.model_version,
            fields=[
                ExtractedField(field_name="owner", extracted_value="Ramesh Kumar", normalized_value="ramesh kumar", confidence=0.97, source_location="page 1, block A", extraction_method="MOCK_OCR_NER"),
                ExtractedField(field_name="survey_number", extracted_value="124/2", normalized_value="124/2", confidence=0.99, source_location="page 1, row 3", extraction_method="MOCK_OCR_NER"),
                ExtractedField(field_name="area", extracted_value="2.31 acre", normalized_value="2.31 acre", confidence=0.88, source_location="page 1, row 6", extraction_method="MOCK_OCR_NER"),
                ExtractedField(field_name="village", extracted_value="Sampurna", normalized_value="sampurna", confidence=0.95, source_location="page 1, row 8", extraction_method="MOCK_OCR_NER"),
            ],
        )


def make_document(parcel_id: str, file_name: str, content_type: str, body: bytes, actor: str, store: LocalEvidenceStore) -> Document:
    key, digest = store.save(parcel_id, body)
    return Document(
        id=f"doc-{uuid4().hex[:12]}", parcel_id=parcel_id, document_type="UNKNOWN_REQUIRES_REVIEW",
        original_file_name=Path(file_name).name, mime_type=content_type, storage_key=key,
        sha256=digest, file_size=len(body), uploaded_by=actor, extraction=MockDocumentProvider().extract(),
    )


def validate(extraction: Extraction, authority: dict[str, object]) -> list[ValidationResult]:
    values = {field.field_name: field for field in extraction.fields}
    output: list[ValidationResult] = []
    for field, authority_key in (("owner", "owner"), ("survey_number", "survey_number"), ("area", "area"), ("village", "village")):
        extracted, expected = values[field], str(authority[authority_key])
        same = extracted.normalized_value == expected.lower().replace(" (synthetic demo person)", "")
        result = ValidationState.MATCH if same else ValidationState.REVIEW_REQUIRED
        output.append(ValidationResult(
            field=field, source_a="AI-extracted uploaded document (MOCK)", value_a=extracted.extracted_value,
            source_b="SYNTHETIC DEMO authority record", value_b=expected, comparison_operator="normalized equality",
            result=result, confidence=extracted.confidence, severity="MEDIUM" if result == ValidationState.REVIEW_REQUIRED else "NONE",
            explanation=("Values are consistent; this is not legal title verification." if same else "The uploaded document reports 2.31 acre while the synthetic reference reports 2.40 acre. Officer review is required."),
        ))
    return output
