"""
Deterministic generator for 100% SYNTHETIC / DEMO land records for LANDSYNC AI.
Strictly adheres to:
- No real personal information, Aadhaar numbers, or real government IDs.
- All records clearly marked SYNTHETIC DEMO DATA.
- Generates JSON, CSV, GeoJSON, document mock files, and README documentation.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent / "synthetic"
DOCS_DIR = BASE_DIR / "documents"

BASE_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

DISCLAIMER_NOTICE = (
    "SYNTHETIC DEMO DATA — NOT A REAL GOVERNMENT RECORD — FOR LANDSYNC AI PROTOTYPE ONLY"
)

# 1. SYNTHETIC USERS
USERS = [
    {
        "user_id": "SYN-USER-CITIZEN-001",
        "name": "Arjun Rao (Synthetic Persona)",
        "role": "citizen",
        "demo_bearer_token": "demo-citizen",
        "email": "demo.arjun001@example.invalid",
        "phone": "+91-00000-00001",
        "permitted_parcels": ["SYN-PARCEL-001", "SYN-PARCEL-002", "demo-parcel"],
        "status": "ACTIVE_SYNTHETIC"
    },
    {
        "user_id": "SYN-USER-OFFICER-001",
        "name": "S. K. Murthy (Synthetic Revenue Officer)",
        "role": "revenue_officer",
        "demo_bearer_token": "demo-officer",
        "email": "demo.officer001@example.invalid",
        "phone": "+91-00000-00002",
        "jurisdiction": "Model Tehsil, Synthetic District",
        "status": "ACTIVE_SYNTHETIC"
    },
    {
        "user_id": "SYN-USER-ADMIN-001",
        "name": "Platform Admin (Synthetic)",
        "role": "administrator",
        "demo_bearer_token": "demo-admin",
        "email": "demo.admin001@example.invalid",
        "phone": "+91-00000-00003",
        "status": "ACTIVE_SYNTHETIC"
    }
]

# 2. SYNTHETIC PARCELS & AUTHORITY RECORDS (14 SCENARIOS)
SCENARIOS = [
    {
        "parcel_id": "SYN-PARCEL-001",
        "ulpin": "SYN-ULPIN-KA-000001",
        "survey_number": "101/1",
        "plot_number": "4A",
        "holder_name": "Arjun Rao",
        "area": "2.40 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 9712.46,
        "village": "Sample Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560001",
        "land_use": "Agricultural",
        "lat": 12.9716,
        "lon": 77.5944,
        "scenario": "MATCH (Fully Consistent)",
        "expected_result": "MATCH",
        "review_required": False,
        "notes": "All extracted values match authority record perfectly.",
        "doc_area": "2.40 acre",
        "doc_holder": "Arjun Rao",
        "doc_survey": "101/1",
        "doc_type": "Record of Rights (RTC)",
        "confidence": 0.98,
        "priority": "NONE",
        "reason": "Consistent record across deed and authority extract."
    },
    {
        "parcel_id": "SYN-PARCEL-002",
        "ulpin": "SYN-ULPIN-KA-000002",
        "survey_number": "124/2",
        "plot_number": "18B",
        "holder_name": "Ramesh Kumar",
        "area": "2.40 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 9712.46,
        "village": "Sampurna Village",
        "taluk": "Model Tehsil",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560002",
        "land_use": "Agricultural",
        "lat": 12.9725,
        "lon": 77.5955,
        "scenario": "AREA_MISMATCH",
        "expected_result": "REVIEW_REQUIRED",
        "review_required": True,
        "notes": "Document reports 2.31 acres while authority states 2.40 acres (0.09 acre variance).",
        "doc_area": "2.31 acre",
        "doc_holder": "Ramesh Kumar",
        "doc_survey": "124/2",
        "doc_type": "Registered Sale Deed",
        "confidence": 0.88,
        "priority": "P2_NORMAL",
        "reason": "Area variance of 0.09 acre (~364 m²) detected between deed and authority record."
    },
    {
        "parcel_id": "SYN-PARCEL-003",
        "ulpin": "SYN-ULPIN-KA-000003",
        "survey_number": "158/4",
        "plot_number": "12C",
        "holder_name": "Meera Rao",
        "area": "1.85 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 7486.68,
        "village": "Sample Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560003",
        "land_use": "Agricultural",
        "lat": 12.9735,
        "lon": 77.5965,
        "scenario": "OWNER_MISMATCH",
        "expected_result": "REVIEW_REQUIRED",
        "review_required": True,
        "notes": "Document holder is Meera Nair, but authority states Meera Rao.",
        "doc_area": "1.85 acre",
        "doc_holder": "Meera Nair",
        "doc_survey": "158/4",
        "doc_type": "Sale Deed",
        "confidence": 0.96,
        "priority": "P1_HIGH",
        "reason": "Holder name differs between submitted deed ('Meera Nair') and authority extract ('Meera Rao')."
    },
    {
        "parcel_id": "SYN-PARCEL-004",
        "ulpin": "SYN-ULPIN-KA-000004",
        "survey_number": "204/8",
        "plot_number": "7",
        "holder_name": "Kiran Shetty",
        "area": "3.10 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 12545.25,
        "village": "Greenfield Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560004",
        "land_use": "Agricultural",
        "lat": 12.9745,
        "lon": 77.5975,
        "scenario": "SURVEY_NUMBER_MISMATCH",
        "expected_result": "REVIEW_REQUIRED",
        "review_required": True,
        "notes": "Document reports survey 204/3 while authority states 204/8.",
        "doc_area": "3.10 acre",
        "doc_holder": "Kiran Shetty",
        "doc_survey": "204/3",
        "doc_type": "Partition Deed",
        "confidence": 0.97,
        "priority": "P1_HIGH",
        "reason": "Survey number discrepancy: Deed cites '204/3' while authority record specifies '204/8'."
    },
    {
        "parcel_id": "SYN-PARCEL-005",
        "ulpin": "SYN-ULPIN-KA-000005",
        "survey_number": "77/1",
        "plot_number": "3",
        "holder_name": "Ananya Iyer",
        "area": "1.25 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 5058.57,
        "village": "Sample Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560005",
        "land_use": "Agricultural",
        "lat": 12.9755,
        "lon": 77.5985,
        "scenario": "MISSING_FIELD",
        "expected_result": "REVIEW_REQUIRED",
        "review_required": True,
        "notes": "Deed schedule is torn/faded; area is MISSING from document extraction.",
        "doc_area": "NOT_AVAILABLE",
        "doc_holder": "Ananya Iyer",
        "doc_survey": "77/1",
        "doc_type": "Faded Settlement Extract",
        "confidence": 0.85,
        "priority": "P2_NORMAL",
        "reason": "Essential extent attribute missing from uploaded document extraction."
    },
    {
        "parcel_id": "SYN-PARCEL-006",
        "ulpin": "SYN-ULPIN-KA-000006",
        "survey_number": "318/2",
        "plot_number": "14",
        "holder_name": "Rohan Kulkarni",
        "area": "4.20 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 16996.80,
        "village": "Adarsh Nagar",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560006",
        "land_use": "Agricultural",
        "lat": 12.9765,
        "lon": 77.5995,
        "scenario": "LOW_CONFIDENCE_EXTRACTION",
        "expected_result": "REVIEW_REQUIRED",
        "review_required": True,
        "notes": "Survey number extracted as 318/? with low confidence 0.51.",
        "doc_area": "4.20 acre",
        "doc_holder": "Rohan Kulkarni",
        "doc_survey": "318/?",
        "doc_type": "Faded Certified Copy",
        "confidence": 0.51,
        "priority": "P2_NORMAL",
        "reason": "Extraction confidence of 51% falls below the 80% automated validation threshold."
    },
    {
        "parcel_id": "SYN-PARCEL-007",
        "ulpin": "SYN-ULPIN-KA-000007",
        "survey_number": "89/1A",
        "plot_number": "5",
        "holder_name": "Vikram Sharma",
        "area": "0.95 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 3844.51,
        "village": "Sample Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560007",
        "land_use": "Agricultural",
        "lat": 12.9775,
        "lon": 77.6005,
        "scenario": "PARTIAL_MATCH",
        "expected_result": "PARTIAL_MATCH",
        "review_required": False,
        "notes": "Name includes parentage 'Vikram Sharma S/o Devendra Sharma' matching 'Vikram Sharma'.",
        "doc_area": "0.95 acre",
        "doc_holder": "Vikram Sharma S/o Devendra Sharma",
        "doc_survey": "89/1A",
        "doc_type": "Sale Deed",
        "confidence": 0.94,
        "priority": "P3_ADVISORY",
        "reason": "Partial match on holder name: parentage honorific present in submitted deed."
    },
    {
        "parcel_id": "SYN-PARCEL-008",
        "ulpin": "SYN-ULPIN-KA-000008",
        "survey_number": "112/5",
        "plot_number": "9",
        "holder_name": "Sneha Patil",
        "area": "2.00 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 8093.71,
        "village": "Sample Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560008",
        "land_use": "Agricultural",
        "lat": 12.9785,
        "lon": 77.6015,
        "scenario": "BOUNDARY_SPATIAL_REVIEW",
        "expected_result": "REVIEW_REQUIRED",
        "review_required": True,
        "notes": "Sketch CV detects 192.8m eastern edge vs 185.0m authoritative cadastral footprint.",
        "doc_area": "2.00 acre",
        "doc_holder": "Sneha Patil",
        "doc_survey": "112/5",
        "doc_type": "Land Cadastral Sketch Blueprint",
        "confidence": 0.86,
        "priority": "P2_NORMAL",
        "reason": "Spatial discrepancy: Sketch boundary detects 7.8m variance along eastern edge."
    },
    {
        "parcel_id": "SYN-PARCEL-009",
        "ulpin": "SYN-ULPIN-KA-000009",
        "survey_number": "64/3",
        "plot_number": "21",
        "holder_name": "Rajesh Gowda",
        "area": "3.50 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 14164.00,
        "village": "Vikas Nagar",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560009",
        "land_use": "Agricultural",
        "lat": 12.9795,
        "lon": 77.6025,
        "scenario": "MULTIPLE_DOCUMENTS",
        "expected_result": "MATCH",
        "review_required": False,
        "notes": "4 associated documents: RoR, Sale Deed, FMB Survey Sketch, and Mutation Sanction.",
        "doc_area": "3.50 acre",
        "doc_holder": "Rajesh Gowda",
        "doc_survey": "64/3",
        "doc_type": "Multi-Document Bundle",
        "confidence": 0.97,
        "priority": "NONE",
        "reason": "All 4 cross-document evidences confirm consistent title extent and geometry."
    },
    {
        "parcel_id": "SYN-PARCEL-010",
        "ulpin": "SYN-ULPIN-KA-000010",
        "survey_number": "140/2",
        "plot_number": "11",
        "holder_name": "Divya Menon",
        "area": "2.75 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 11128.85,
        "village": "Sample Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560010",
        "land_use": "Agricultural",
        "lat": 12.9805,
        "lon": 77.6035,
        "scenario": "MUTATION_HISTORY",
        "expected_result": "MATCH",
        "review_required": False,
        "notes": "Traces 3 historical mutations: 1994 Partition, 2012 Succession, 2024 Gift Deed.",
        "doc_area": "2.75 acre",
        "doc_holder": "Divya Menon",
        "doc_survey": "140/2",
        "doc_type": "Registered Gift Deed",
        "confidence": 0.98,
        "priority": "NONE",
        "reason": "Deed matches latest sanctioned mutation entry MR-89/2024."
    },
    {
        "parcel_id": "SYN-PARCEL-011",
        "ulpin": "SYN-ULPIN-KA-000011",
        "survey_number": "99/1",
        "plot_number": "16",
        "holder_name": "Suresh Deshmukh",
        "area": "1.50 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 6070.28,
        "village": "Sample Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560011",
        "land_use": "Agricultural",
        "lat": 12.9815,
        "lon": 77.6045,
        "scenario": "DUPLICATE_DOCUMENT",
        "expected_result": "MATCH",
        "review_required": False,
        "notes": "Identical deed uploaded twice; system flags duplicate SHA-256 hash.",
        "doc_area": "1.50 acre",
        "doc_holder": "Suresh Deshmukh",
        "doc_survey": "99/1",
        "doc_type": "Sale Deed (Duplicate Upload)",
        "confidence": 0.99,
        "priority": "P3_ADVISORY",
        "reason": "Duplicate file upload detected via SHA-256 integrity match."
    },
    {
        "parcel_id": "SYN-PARCEL-012",
        "ulpin": "SYN-ULPIN-KA-000012",
        "survey_number": "215/6",
        "plot_number": "8",
        "holder_name": "Kavita Reddy",
        "area": "1.80 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 7284.34,
        "village": "Demo Hamlet",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560012",
        "land_use": "Agricultural",
        "lat": 12.9825,
        "lon": 77.6055,
        "scenario": "AMBIGUOUS_LAND_UNIT",
        "expected_result": "REVIEW_REQUIRED",
        "review_required": True,
        "notes": "Deed specifies '2.5 local bigha'; Rule 13 prohibits automated conversion.",
        "doc_area": "2.5 local bigha",
        "doc_holder": "Kavita Reddy",
        "doc_survey": "215/6",
        "doc_type": "Old Revenue Extract",
        "confidence": 0.91,
        "priority": "P1_HIGH",
        "reason": "Regional unit 'bigha' lacks state-level metric schedule. Automated conversion blocked."
    },
    {
        "parcel_id": "SYN-PARCEL-013",
        "ulpin": "SYN-ULPIN-KA-000013",
        "survey_number": "52/1",
        "plot_number": "2",
        "holder_name": "Amit Joshi",
        "area": "2.10 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 8498.40,
        "village": "Sample Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560013",
        "land_use": "Agricultural",
        "lat": 12.9835,
        "lon": 77.6065,
        "scenario": "CO_OWNERSHIP_DISCREPANCY",
        "expected_result": "REVIEW_REQUIRED",
        "review_required": True,
        "notes": "Deed lists joint co-parceners (Amit & Sumit Joshi) while authority lists sole holder.",
        "doc_area": "2.10 acre",
        "doc_holder": "Amit Joshi & Sumit Joshi (Co-parceners)",
        "doc_survey": "52/1",
        "doc_type": "Family Settlement Deed",
        "confidence": 0.93,
        "priority": "P2_NORMAL",
        "reason": "Undivided joint share claim in deed vs sole khatedar in revenue register."
    },
    {
        "parcel_id": "SYN-PARCEL-014",
        "ulpin": "SYN-ULPIN-KA-000014",
        "survey_number": "180/7",
        "plot_number": "15",
        "holder_name": "Priya Swaminathan",
        "area": "1.10 acre",
        "area_unit": "acre",
        "normalized_area_sqm": 4451.54,
        "village": "Sample Village",
        "taluk": "Demo Taluk",
        "district": "Synthetic District",
        "state": "Karnataka",
        "pincode": "560014",
        "land_use": "Agricultural",
        "lat": 12.9845,
        "lon": 77.6075,
        "scenario": "LAND_USE_MISMATCH",
        "expected_result": "REVIEW_REQUIRED",
        "review_required": True,
        "notes": "Deed asserts Commercial/Industrial Non-Agricultural (NA), but authority records Agricultural.",
        "doc_area": "1.10 acre",
        "doc_holder": "Priya Swaminathan",
        "doc_survey": "180/7",
        "doc_type": "Commercial Lease / Sale Deed",
        "confidence": 0.95,
        "priority": "P1_HIGH",
        "reason": "Unsanctioned land conversion: Deed claims Commercial use without DC NA conversion order."
    },
]

def make_geometry(lat: float, lon: float, offset: float = 0.0006) -> dict:
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [round(lon, 5), round(lat, 5)],
                [round(lon + offset, 5), round(lat, 5)],
                [round(lon + offset, 5), round(lat + offset, 5)],
                [round(lon, 5), round(lat + offset, 5)],
                [round(lon, 5), round(lat, 5)],
            ]
        ]
    }

# Build dataset lists
parcels = []
authority_records = []
documents = []
extractions = []
validation_results = []
review_cases = []
audit_events = []
geojson_features = []

for idx, sc in enumerate(SCENARIOS, 1):
    pid = sc["parcel_id"]
    geom = make_geometry(sc["lat"], sc["lon"])

    # 1. Parcel Record
    p = {
        "parcel_id": pid,
        "synthetic_ulpin": sc["ulpin"],
        "survey_number": sc["survey_number"],
        "plot_number": sc["plot_number"],
        "village": sc["village"],
        "taluk": sc["taluk"],
        "district": sc["district"],
        "state": sc["state"],
        "pincode": sc["pincode"],
        "land_area": sc["area"],
        "land_area_unit": sc["area_unit"],
        "normalized_area_sqm": sc["normalized_area_sqm"],
        "land_use": sc["land_use"],
        "latitude": sc["lat"],
        "longitude": sc["lon"],
        "source": "SYNTHETIC_DEMO_FIXTURE",
        "source_status": "SYNTHETIC / NOT CONNECTED",
        "disclaimer": DISCLAIMER_NOTICE
    }
    parcels.append(p)

    # 2. Authority Reference Record
    auth = {
        "parcel_id": pid,
        "source_type": "SYNTHETIC_AUTHORITY",
        "source_name": "Demo Authority Adapter",
        "source_status": "SYNTHETIC / NOT CONNECTED",
        "survey_number": sc["survey_number"],
        "plot_number": sc["plot_number"],
        "owner": sc["holder_name"],
        "area": sc["area"],
        "area_unit": sc["area_unit"],
        "normalized_area_sqm": sc["normalized_area_sqm"],
        "village": sc["village"],
        "land_use": sc["land_use"],
        "geometry": geom,
        "geometry_source": "SYNTHETIC DEMO PostGIS GeoJSON (EPSG:4326)",
        "last_updated": "2026-01-15T00:00:00Z",
        "source_version": "demo-v1.2",
        "disclaimer": DISCLAIMER_NOTICE
    }
    authority_records.append(auth)

    # 3. Document Record
    doc_id = f"SYN-DOC-{idx:03d}"
    doc_fname = f"synthetic_{sc['doc_type'].lower().replace(' ', '_').replace('/', '_')}_{pid.lower()}.txt"
    doc_hash = f"SYN-HASH-{idx:06d}"
    
    doc = {
        "document_id": doc_id,
        "parcel_id": pid,
        "document_type": sc["doc_type"],
        "document_version": 1,
        "issue_date": "2018-03-24",
        "source": "USER_UPLOAD",
        "synthetic_filename": doc_fname,
        "document_status": "PROCESSED_MOCK",
        "content_summary": f"{sc['doc_type']} for parcel {pid} in {sc['village']}",
        "provenance": {
            "source_type": "DIGITIZED_OFFICIAL_EVIDENCE (MOCK)",
            "uploaded_by": "SYN-USER-CITIZEN-001",
            "uploaded_at": "2026-09-23T10:00:00Z",
            "sha256": doc_hash,
            "storage_key": f"documents/demo/{pid}/{doc_hash}/1/original"
        },
        "disclaimer": DISCLAIMER_NOTICE
    }
    documents.append(doc)

    # Write synthetic document text file
    doc_txt_content = f"""================================================================================
{DISCLAIMER_NOTICE}
================================================================================
DOCUMENT TYPE: {sc['doc_type'].upper()}
DOCUMENT REF: {doc_id}
PARCEL IDENTIFIER: {pid} (ULPIN: {sc['ulpin']})
JURISDICTION: {sc['village']}, {sc['taluk']}, {sc['district']}, {sc['state']}
--------------------------------------------------------------------------------
SCHEDULE PROPERTY PARTICULARS:
Survey Number: {sc['doc_survey']}
Plot Number: {sc['plot_number']}
Recorded Holder: {sc['doc_holder']}
Extent / Area: {sc['doc_area']}
Land Classification: {sc['land_use']}

RECITAL / NOTES:
This document is a synthetic demonstrator generated for LANDSYNC AI.
Scenario: {sc['scenario']}
Rationale: {sc['notes']}
================================================================================
"""
    (DOCS_DIR / doc_fname).write_text(doc_txt_content, encoding="utf-8")

    # 4. Extractions
    ext = {
        "document_id": doc_id,
        "parcel_id": pid,
        "provider": "MockDocumentProvider",
        "provider_version": "demo-v1.2",
        "confidence": sc["confidence"],
        "extracted_fields": [
            {
                "field_name": "owner",
                "extracted_value": sc["doc_holder"],
                "confidence": sc["confidence"],
                "source_location": "page 1, line 7",
                "review_state": "PENDING"
            },
            {
                "field_name": "survey_number",
                "extracted_value": sc["doc_survey"],
                "confidence": sc["confidence"],
                "source_location": "page 1, line 5",
                "review_state": "PENDING"
            },
            {
                "field_name": "area",
                "extracted_value": sc["doc_area"],
                "confidence": sc["confidence"],
                "source_location": "page 1, line 8",
                "review_state": "PENDING"
            },
            {
                "field_name": "village",
                "extracted_value": sc["village"],
                "confidence": 0.96,
                "source_location": "page 1, line 4",
                "review_state": "AUTO_ACCEPTED"
            },
            {
                "field_name": "land_use",
                "extracted_value": sc["land_use"] if sc["scenario"] != "LAND_USE_MISMATCH" else "Commercial (NA)",
                "confidence": 0.92,
                "source_location": "page 1, line 9",
                "review_state": "PENDING"
            }
        ],
        "disclaimer": DISCLAIMER_NOTICE
    }
    extractions.append(ext)

    # 5. Validation Result
    val_status = "MATCH" if sc["expected_result"] == "MATCH" else (
        "PARTIAL_MATCH" if sc["expected_result"] == "PARTIAL_MATCH" else "REVIEW_REQUIRED"
    )
    val = {
        "parcel_id": pid,
        "document_id": doc_id,
        "overall_status": val_status,
        "confidence": sc["confidence"],
        "scenario": sc["scenario"],
        "review_required": sc["review_required"],
        "explanation": sc["reason"],
        "fields": [
            {
                "field": "owner",
                "document_value": sc["doc_holder"],
                "authority_value": sc["holder_name"],
                "result": "MATCH" if sc["doc_holder"] == sc["holder_name"] else (
                    "PARTIAL_MATCH" if sc["scenario"] == "PARTIAL_MATCH" else "MISMATCH"
                ),
                "confidence": sc["confidence"]
            },
            {
                "field": "survey_number",
                "document_value": sc["doc_survey"],
                "authority_value": sc["survey_number"],
                "result": "MATCH" if sc["doc_survey"] == sc["survey_number"] else "MISMATCH",
                "confidence": sc["confidence"]
            },
            {
                "field": "area",
                "document_value": sc["doc_area"],
                "authority_value": sc["area"],
                "result": "MATCH" if sc["doc_area"] == sc["area"] else (
                    "MISSING" if sc["doc_area"] == "NOT_AVAILABLE" else "MISMATCH"
                ),
                "confidence": sc["confidence"]
            },
            {
                "field": "village",
                "document_value": sc["village"],
                "authority_value": sc["village"],
                "result": "MATCH",
                "confidence": 0.96
            }
        ],
        "disclaimer": DISCLAIMER_NOTICE
    }
    validation_results.append(val)

    # 6. Review Case (if review required)
    if sc["review_required"]:
        case_id = f"SYN-CASE-{idx:03d}"
        case = {
            "review_case_id": case_id,
            "parcel_id": pid,
            "document_id": doc_id,
            "reason": sc["reason"],
            "priority": sc["priority"],
            "status": "OPEN",
            "assigned_role": "revenue_officer",
            "evidence_refs": [doc_id, f"AUTH-EXTRACT-{pid}"],
            "recommended_action": "Inspect original physical deed register and order ground verification.",
            "reviewer": "DECISION_PENDING",
            "reviewer_note": "Awaiting officer examination in demonstration queue.",
            "created_at": "2026-09-23T10:05:00Z",
            "decision": None,
            "disclaimer": DISCLAIMER_NOTICE
        }
        review_cases.append(case)

        # Audit Event for Review Creation
        audit_events.append({
            "audit_event_id": f"SYN-AUDIT-{len(audit_events)+1:04d}",
            "actor": "LANDSYNC_VALIDATION_ENGINE",
            "role": "SYSTEM",
            "action": "REVIEW_CASE_CREATED",
            "timestamp": "2026-09-23T10:05:00Z",
            "parcel_id": pid,
            "review_case_id": case_id,
            "reason": sc["reason"],
            "trace_id": f"trace-sys-{idx:04d}",
            "disclaimer": DISCLAIMER_NOTICE
        })

    # Standard Audit Events for Upload & Extraction
    audit_events.extend([
        {
            "audit_event_id": f"SYN-AUDIT-{len(audit_events)+1:04d}",
            "actor": "demo-citizen",
            "role": "CITIZEN",
            "action": "DOCUMENT_UPLOADED",
            "timestamp": "2026-09-23T10:00:00Z",
            "parcel_id": pid,
            "reason": f"Citizen uploaded {doc_fname}",
            "trace_id": f"trace-up-{idx:04d}",
            "disclaimer": DISCLAIMER_NOTICE
        },
        {
            "audit_event_id": f"SYN-AUDIT-{len(audit_events)+1:04d}",
            "actor": "MockDocumentProvider",
            "role": "AI_EXTRACTION_ENGINE",
            "action": "EXTRACTION_COMPLETED",
            "timestamp": "2026-09-23T10:02:00Z",
            "parcel_id": pid,
            "reason": f"Completed mock extraction for {doc_id} with conf {sc['confidence']}",
            "trace_id": f"trace-ai-{idx:04d}",
            "disclaimer": DISCLAIMER_NOTICE
        }
    ])

    # 7. GeoJSON Feature
    geojson_features.append({
        "type": "Feature",
        "properties": {
            "parcel_id": pid,
            "ulpin": sc["ulpin"],
            "survey_number": sc["survey_number"],
            "plot_number": sc["plot_number"],
            "holder_name": sc["holder_name"],
            "area": sc["area"],
            "scenario": sc["scenario"],
            "validation_status": val_status,
            "disclaimer": DISCLAIMER_NOTICE
        },
        "geometry": geom
    })

# Save JSON datasets
def dump_json(file_path: Path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

dump_json(BASE_DIR / "parcels.json", parcels)
dump_json(BASE_DIR / "authority_records.json", authority_records)
dump_json(BASE_DIR / "documents.json", documents)
dump_json(BASE_DIR / "extractions.json", extractions)
dump_json(BASE_DIR / "validation_results.json", validation_results)
dump_json(BASE_DIR / "review_cases.json", review_cases)
dump_json(BASE_DIR / "audit_events.json", audit_events)
dump_json(BASE_DIR / "users.json", USERS)

# Save GeoJSON
geojson_obj = {
    "type": "FeatureCollection",
    "name": "LANDSYNC_AI_SYNTHETIC_PARCELS",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": geojson_features,
    "disclaimer": DISCLAIMER_NOTICE
}
dump_json(BASE_DIR / "parcels.geojson", geojson_obj)

# Save CSV dataset
csv_file = BASE_DIR / "parcels.csv"
fieldnames = [
    "parcel_id", "synthetic_ulpin", "survey_number", "plot_number", "holder_name",
    "village", "taluk", "district", "state", "pincode", "land_area", "land_area_unit",
    "normalized_area_sqm", "land_use", "latitude", "longitude", "scenario",
    "expected_result", "review_required", "notes"
]

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for sc in SCENARIOS:
        row = {k: sc.get(k, "") for k in fieldnames}
        writer.writerow(row)

# Save master index README.md
readme_content = f"""# LANDSYNC AI — Synthetic Demo Dataset
**Identifier**: `LANDSYNC-SYNTHETIC-SEED-V1`  
**Notice**: {DISCLAIMER_NOTICE}

This dataset contains **14 synthetic land parcels**, accompanying documents, mock AI extractions, synthetic authority reference records, validation matrices, review cases, and immutable audit logs. It is designed to demonstrate the complete capability spectrum of the LANDSYNC AI platform during Smart India Hackathon 2026.

---

## Scenario Distribution Matrix

| Record ID | Parcel ID | Synthetic ULPIN | Scenario / Edge Case | Expected Result | Review Req? | Key Demonstration Feature |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| `SYN-CASE-001` | `SYN-PARCEL-001` | `SYN-ULPIN-KA-000001` | **MATCH (Fully Consistent)** | `MATCH` | No | Baseline consistent Digital Land Profile |
| `SYN-CASE-002` | `SYN-PARCEL-002` | `SYN-ULPIN-KA-000002` | **AREA_MISMATCH** | `REVIEW_REQUIRED` | **Yes** | 2.31 ac vs 2.40 ac (0.09 ac / 364 m² variance) |
| `SYN-CASE-003` | `SYN-PARCEL-003` | `SYN-ULPIN-KA-000003` | **OWNER_MISMATCH** | `REVIEW_REQUIRED` | **Yes** | Meera Nair vs Meera Rao (P1 priority case) |
| `SYN-CASE-004` | `SYN-PARCEL-004` | `SYN-ULPIN-KA-000004` | **SURVEY_MISMATCH** | `REVIEW_REQUIRED` | **Yes** | Survey 204/3 vs 204/8 discrepancy |
| `SYN-CASE-005` | `SYN-PARCEL-005` | `SYN-ULPIN-KA-000005` | **MISSING_FIELD** | `REVIEW_REQUIRED` | **Yes** | Missing area in schedule clause |
| `SYN-CASE-006` | `SYN-PARCEL-006` | `SYN-ULPIN-KA-000006` | **LOW_CONFIDENCE** | `REVIEW_REQUIRED` | **Yes** | Survey '318/?' at 51% confidence triggers review |
| `SYN-CASE-007` | `SYN-PARCEL-007` | `SYN-ULPIN-KA-000007` | **PARTIAL_MATCH** | `PARTIAL_MATCH` | No | Parentage honorific match ('S/o Devendra') |
| `SYN-CASE-008` | `SYN-PARCEL-008` | `SYN-ULPIN-KA-000008` | **SPATIAL_REVIEW** | `REVIEW_REQUIRED` | **Yes** | Blueprint CV edge detects 7.8m variance |
| `SYN-CASE-009` | `SYN-PARCEL-009` | `SYN-ULPIN-KA-000009` | **MULTI_DOCUMENT** | `MATCH` | No | 4 attached documents (RoR, Deed, Sketch, Mut) |
| `SYN-CASE-010` | `SYN-PARCEL-010` | `SYN-ULPIN-KA-000010` | **MUTATION_HISTORY** | `MATCH` | No | 4-step mutation timeline (1994 to 2024) |
| `SYN-CASE-011` | `SYN-PARCEL-011` | `SYN-ULPIN-KA-000011` | **DUPLICATE_DOC** | `MATCH` | No | SHA-256 duplicate detection flag |
| `SYN-CASE-012` | `SYN-PARCEL-012` | `SYN-ULPIN-KA-000012` | **AMBIGUOUS_UNIT** | `REVIEW_REQUIRED` | **Yes** | Rule 13: '2.5 local bigha' blocked from auto-convert |
| `SYN-CASE-013` | `SYN-PARCEL-013` | `SYN-ULPIN-KA-000013` | **CO_OWNERSHIP** | `REVIEW_REQUIRED` | **Yes** | Co-parcenary share claim vs sole khatedar |
| `SYN-CASE-014` | `SYN-PARCEL-014` | `SYN-ULPIN-KA-000014` | **LAND_USE_CONFLICT**| `REVIEW_REQUIRED` | **Yes** | Commercial NA claim vs Agricultural dry in RoR |

---

## Directory Layout
- `parcels.json` — 14 synthetic parcels with ULPIN, survey, extent, and coordinates.
- `parcels.csv` — Tabular dataset for data analysis and quick review.
- `authority_records.json` — Synthetic reference authority records (Demo Authority Adapter).
- `documents.json` — Registered deeds, RTCs, FMB sketches, and mutations.
- `extractions.json` — Mock AI extracted fields with field-level confidence scores.
- `validation_results.json` — Comprehensive 5-state validation evaluations.
- `review_cases.json` — Open officer review cases for the demonstration queue.
- `audit_events.json` — Append-only audit logs with trace IDs.
- `users.json` — Demo personas for Citizen, Officer, and Administrator.
- `parcels.geojson` — EPSG:4326 GeoJSON polygons for the Cadastral GIS map.
- `documents/` — Mock plain text copies of each uploaded deed/extract.
"""
(BASE_DIR / "README.md").write_text(readme_content, encoding="utf-8")

print(f"Synthetic dataset successfully generated in: {BASE_DIR.resolve()}")
