"""
Integration tests between Benchmark Dataset records and the existing LANDSYNC AI engine.
"""

import pytest
from landsync_datasets.adapter.landsync_adapter import (
    to_landsync_parcel,
    to_landsync_document,
    HAS_LANDSYNC_APP,
)

if HAS_LANDSYNC_APP:
    from landsync.models import LandParcel, Document as AppDocument, ValidationState
    from landsync.services import validate


def test_landsync_app_model_conversion():
    assert HAS_LANDSYNC_APP, "LANDSYNC app models should be available"

    sample_parcel_dict = {
        "parcel_id": "SYN-PARCEL-000001",
        "ulpin": "SYN-ULPIN-KA-000001",
        "survey_number": "101",
        "plot_number": "4A",
        "village_name": "Hemavathi",
        "area_value": 2.40,
        "area_unit": "acre",
        "area_square_metres": 9712.46,
        "land_classification": "Agricultural Dry (Kushki)",
    }

    parcel_model = to_landsync_parcel(sample_parcel_dict)
    assert isinstance(parcel_model, LandParcel)
    assert parcel_model.id == "SYN-PARCEL-000001"
    assert parcel_model.survey_number == "101"
    assert parcel_model.normalized_area_sqm == 9712.46

    sample_doc_dict = {
        "document_id": "SYN-DOC-000001",
        "parcel_id": "SYN-PARCEL-000001",
        "document_type": "RECORD_OF_RIGHTS",
        "synthetic_filename": "synthetic_rtc_syn-parcel-000001.txt",
        "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    }
    sample_fields = [
        {
            "field_name": "owner",
            "raw_value": "Arjun Rao",
            "normalized_value": "Arjun Rao",
            "confidence": 0.98,
            "page_number": 1,
        },
        {
            "field_name": "survey_number",
            "raw_value": "101",
            "normalized_value": "101",
            "confidence": 0.95,
            "page_number": 1,
        },
        {
            "field_name": "area",
            "raw_value": "2.40 acre",
            "normalized_value": "2.40",
            "confidence": 0.96,
            "page_number": 2,
        },
        {
            "field_name": "village",
            "raw_value": "Hemavathi",
            "normalized_value": "Hemavathi",
            "confidence": 0.94,
            "page_number": 1,
        },
    ]

    doc_model = to_landsync_document(sample_doc_dict, sample_fields)
    assert isinstance(doc_model, AppDocument)
    assert doc_model.id == "SYN-DOC-000001"
    assert doc_model.extraction is not None
    assert len(doc_model.extraction.fields) == 4


def test_landsync_validation_engine_execution():
    assert HAS_LANDSYNC_APP

    sample_doc = {
        "document_id": "SYN-DOC-000001",
        "parcel_id": "SYN-PARCEL-000001",
        "document_type": "RECORD_OF_RIGHTS",
        "synthetic_filename": "synthetic_rtc.txt",
    }
    sample_fields = [
        {"field_name": "owner", "raw_value": "Arjun Rao", "normalized_value": "Arjun Rao", "confidence": 0.98},
        {"field_name": "survey_number", "raw_value": "101", "normalized_value": "101", "confidence": 0.98},
        {"field_name": "plot_number", "raw_value": "4A", "normalized_value": "4A", "confidence": 0.98},
        {"field_name": "area", "raw_value": "2.40 acre", "normalized_value": "2.40", "confidence": 0.98},
        {"field_name": "village", "raw_value": "Hemavathi", "normalized_value": "Hemavathi", "confidence": 0.98},
        {"field_name": "land_use", "raw_value": "Agricultural", "normalized_value": "Agricultural", "confidence": 0.98},
    ]

    doc_model = to_landsync_document(sample_doc, sample_fields)

    authority_record = {
        "owner": "Arjun Rao",
        "survey_number": "101",
        "plot_number": "4A",
        "area": "2.40 acre",
        "village": "Hemavathi",
        "land_use": "Agricultural",
    }

    # Run LANDSYNC validate service
    results = validate(doc_model.extraction, authority_record)
    assert len(results) == 6
    for r in results:
        assert r.result == ValidationState.MATCH
