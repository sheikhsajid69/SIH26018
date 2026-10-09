"""
Integration Adapter between Benchmark Dataset records and the LANDSYNC AI application models.
Maintains full backward and forward compatibility without modifying existing application behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure apps/api is importable if needed
api_path = Path(__file__).resolve().parents[3] / "apps" / "api"
if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))

try:
    from landsync.models import (
        LandParcel,
        Document as AppDocument,
        Extraction,
        ExtractedField,
        ValidationResult as AppValidationResult,
        ReviewCase as AppReviewCase,
        AuditEvent as AppAuditEvent,
        ValidationState,
    )
    HAS_LANDSYNC_APP = True
except ImportError:
    HAS_LANDSYNC_APP = False


def to_landsync_parcel(
    parcel_dict: dict[str, Any],
    geometry_dict: dict[str, Any] | None = None,
) -> LandParcel | dict[str, Any]:
    """Converts a benchmark synthetic parcel record to LANDSYNC LandParcel domain model."""
    geom = geometry_dict or {"type": "Polygon", "coordinates": [[[77.59, 12.97], [77.60, 12.97], [77.60, 12.98], [77.59, 12.98], [77.59, 12.97]]]}

    payload = {
        "id": parcel_dict["parcel_id"],
        "ulpin": parcel_dict.get("ulpin", f"SYN-ULPIN-{parcel_dict['parcel_id']}"),
        "survey_number": parcel_dict["survey_number"],
        "plot_number": parcel_dict.get("plot_number", "1"),
        "state": "Karnataka",
        "district": "Mayura District",
        "tehsil": "Kalyana Taluk",
        "village": parcel_dict.get("village_name", "Hemavathi"),
        "area": f"{parcel_dict['area_value']} {parcel_dict['area_unit']}",
        "normalized_area_sqm": float(parcel_dict.get("area_square_metres", 0.0)),
        "land_use": parcel_dict.get("land_classification", "Agricultural Dry (Kushki)"),
        "geometry": geom,
        "geometry_source": "SYNTHETIC_CADASTRAL_ENGINE",
        "authoritative_source": "SYNTHETIC_DEMO_AUTHORITY",
    }

    if HAS_LANDSYNC_APP:
        return LandParcel(**payload)
    return payload


def to_landsync_document(
    doc_dict: dict[str, Any],
    field_dicts: list[dict[str, Any]] | None = None,
) -> AppDocument | dict[str, Any]:
    """Converts a benchmark synthetic document record to LANDSYNC Document domain model."""
    fields_list = []
    if field_dicts:
        for f in field_dicts:
            fields_list.append(
                ExtractedField(
                    field_name=f["field_name"],
                    extracted_value=f["raw_value"],
                    normalized_value=f["normalized_value"],
                    confidence=float(f["confidence"]),
                    source_location=f"Page {f.get('page_number', 1)}",
                    page_number=int(f.get("page_number", 1)),
                    extraction_method=f.get("extraction_method", "OCR_TRANSCRIPTION"),
                    reviewer_status="PENDING",
                )
            )

    ext = Extraction(
        provider="SYNTHETIC_BENCHMARK_EXTRACTOR",
        model_version="1.0.0",
        fields=fields_list,
    ) if HAS_LANDSYNC_APP else {"provider": "SYNTHETIC", "fields": field_dicts or []}

    payload = {
        "id": doc_dict["document_id"],
        "parcel_id": doc_dict["parcel_id"],
        "document_type": doc_dict["document_type"],
        "original_file_name": doc_dict["synthetic_filename"],
        "mime_type": doc_dict.get("mime_type", "text/plain"),
        "storage_key": f"vault/{doc_dict['document_id']}",
        "sha256": doc_dict.get("content_hash", "0" * 64),
        "file_size": 2048,
        "source": "SYNTHETIC_BENCHMARK_UPLOAD",
        "uploaded_by": "SYN-USER-CITIZEN-001",
        "version": 1,
        "processing_status": "COMPLETED",
        "extraction": ext if HAS_LANDSYNC_APP else None,
    }

    if HAS_LANDSYNC_APP:
        return AppDocument(**payload)
    return payload
