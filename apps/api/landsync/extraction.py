from __future__ import annotations

import io
import json
import os
import re
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from landsync.models import ExtractedField, Extraction

REPO_ROOT = Path(__file__).resolve().parents[3]
SYNTHETIC_DIR = REPO_ROOT / "data" / "synthetic"


@runtime_checkable
class DocumentProvider(Protocol):
    """Protocol for pluggable document extraction providers."""

    def extract(
        self,
        file_name: str = "deed.pdf",
        body: bytes = b"",
        content_type: str = "application/pdf",
        parcel_id: str | None = None,
    ) -> Extraction:
        ...


class MockDocumentProvider:
    """
    Deterministic substitute for OCR and document extraction.
    Supports synthetic scenarios from data/synthetic/extractions.json.
    """

    provider = "mock-document-ai"
    model_version = "demo-1.2"

    def __init__(self) -> None:
        self._scenario_cache: dict[str, dict[str, Any]] = {}
        ext_file = SYNTHETIC_DIR / "extractions.json"
        if ext_file.exists():
            try:
                data = json.loads(ext_file.read_text(encoding="utf-8"))
                for item in data:
                    if "parcel_id" in item:
                        self._scenario_cache[item["parcel_id"]] = item
                    if "document_id" in item:
                        self._scenario_cache[item["document_id"]] = item
            except Exception:
                pass

    def extract(
        self,
        file_name: str = "deed.pdf",
        body: bytes = b"",
        content_type: str = "application/pdf",
        parcel_id: str | None = None,
    ) -> Extraction:
        # Check if matched to a known synthetic parcel or document
        matched = None
        if parcel_id and parcel_id in self._scenario_cache:
            matched = self._scenario_cache[parcel_id]
        elif file_name:
            for key, val in self._scenario_cache.items():
                if key.lower() in file_name.lower():
                    matched = val
                    break

        if matched and "extracted_fields" in matched:
            fields = []
            for f in matched["extracted_fields"]:
                raw_val = str(f["extracted_value"])
                fields.append(
                    ExtractedField(
                        field_name=f["field_name"],
                        extracted_value=raw_val,
                        normalized_value=raw_val.lower().strip(),
                        confidence=float(f.get("confidence", 0.95)),
                        source_location=f.get("source_location", "page 1"),
                        page_number=1,
                        extraction_method="SYNTHETIC_SCENARIO_MOCK",
                        reviewer_status=f.get("review_state", "PENDING"),
                    )
                )
            return Extraction(
                provider=matched.get("provider", self.provider),
                model_version=matched.get("provider_version", self.model_version),
                fields=fields,
            )

        # Default synthetic baseline extraction for demo-parcel
        raw_fields = [
            ("owner", "Ramesh Kumar", "ramesh kumar", 0.97, "page 1, block A, line 2"),
            ("survey_number", "124/2", "124/2", 0.99, "page 1, schedule section, row 3"),
            ("plot_number", "18B", "18b", 0.94, "page 1, schedule section, row 4"),
            ("area", "2.31 acre", "2.31 acre", 0.88, "page 1, schedule property extent, row 6"),
            ("village", "Sampurna", "sampurna", 0.95, "page 1, property address, row 8"),
            ("land_use", "Agricultural", "agricultural", 0.92, "page 2, recital clause 4"),
        ]
        return Extraction(
            provider=self.provider,
            model_version=self.model_version,
            fields=[
                ExtractedField(
                    field_name=f[0],
                    extracted_value=f[1],
                    normalized_value=f[2],
                    confidence=f[3],
                    source_location=f[4],
                    extraction_method="MOCK_OCR_NER",
                )
                for f in raw_fields
            ],
        )


class TextAndPdfDocumentProvider:
    """
    Real document parser extracting text from plain text or PDF files.
    Uses pypdf and heuristic NER pattern extraction tailored to Indian land records.
    Falls back gracefully if fields are absent or file is binary/scanned.
    """

    provider = "landsync-pdf-text-engine"
    model_version = "v1.0"

    def __init__(self, fallback: DocumentProvider | None = None) -> None:
        self.fallback = fallback or MockDocumentProvider()

    def _extract_text_from_pdf(self, body: bytes) -> tuple[str, int]:
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(body))
            pages_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n\n".join(pages_text), len(reader.pages)
        except Exception:
            return "", 0

    def extract(
        self,
        file_name: str = "deed.pdf",
        body: bytes = b"",
        content_type: str = "application/pdf",
        parcel_id: str | None = None,
    ) -> Extraction:
        text = ""
        page_count = 1

        if content_type == "application/pdf" or file_name.lower().endswith(".pdf"):
            text, page_count = self._extract_text_from_pdf(body)
        elif content_type.startswith("text/") or file_name.lower().endswith((".txt", ".csv")):
            try:
                text = body.decode("utf-8", errors="replace")
            except Exception:
                text = ""

        # If no extractable text found, delegate to mock provider
        if not text.strip():
            return self.fallback.extract(file_name, body, content_type, parcel_id)

        fields: list[ExtractedField] = []

        patterns = [
            (
                "owner",
                r"(?:Owner|Khatedar|Holder|Purchaser|In favour of|Name of Holder)[:\s]+([A-Za-z\s.'-]+?)(?:\n|,|;|$)",
                0.92,
            ),
            (
                "survey_number",
                r"(?:Survey\s*(?:No\.?|Number)|Sy\.?\s*No\.?)[:\s]*([0-9]+(?:\/[0-9]+[a-zA-Z]*)?)",
                0.95,
            ),
            (
                "plot_number",
                r"(?:Plot\s*(?:No\.?|Number))[:\s]*([0-9a-zA-Z\/-]+)",
                0.90,
            ),
            (
                "area",
                r"(?:Area|Extent|Total\s*Area)[:\s]*([0-9]+(?:\.[0-9]+)?\s*(?:acre|acres|guntha|gunthas|sqm|sq\s*ft|bigha|hectare|hectares))",
                0.89,
            ),
            (
                "village",
                r"(?:Village|Mauza|Gram)[:\s]*([A-Za-z\s]+?)(?:\n|,|;|$)",
                0.93,
            ),
            (
                "land_use",
                r"(?:Land\s*Use|Classification|Nature\s*of\s*Land)[:\s]*([A-Za-z\s]+?)(?:\n|,|;|$)",
                0.88,
            ),
        ]

        found_fields = set()
        for field_name, regex, conf in patterns:
            match = re.search(regex, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                fields.append(
                    ExtractedField(
                        field_name=field_name,
                        extracted_value=val,
                        normalized_value=val.lower(),
                        confidence=conf,
                        source_location="regex heuristic",
                        page_number=1,
                        extraction_method="PDF_REGEX_EXTRACTION",
                    )
                )
                found_fields.add(field_name)

        # If minimal land parcel fields weren't found, merge fallback fields
        if len(fields) < 2:
            return self.fallback.extract(file_name, body, content_type, parcel_id)

        return Extraction(
            provider=self.provider,
            model_version=self.model_version,
            fields=fields,
        )


def get_document_provider() -> DocumentProvider:
    provider_name = os.getenv("DOCUMENT_PROVIDER", "mock").lower().strip()
    if provider_name in ("pdf", "pdf_text", "real"):
        return TextAndPdfDocumentProvider()
    return MockDocumentProvider()
