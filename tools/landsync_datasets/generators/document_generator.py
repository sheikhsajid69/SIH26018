"""
Synthetic Document and Field Annotation Generator.
Generates 5,500+ document records and 32,000+ field annotations.
"""

from __future__ import annotations

import random
from typing import Any

from landsync_datasets.primitives.identifiers import (
    document_id,
    field_id,
    synthetic_registration_ref,
    sha256_text,
)
from landsync_datasets.primitives.noise import apply_ocr_noise


DOC_TYPES = [
    ("RECORD_OF_RIGHTS", "synthetic_rtc_{pid}.txt", "REVENUE_TALUK_OFFICE"),
    ("SALE_DEED", "synthetic_sale_deed_{pid}.txt", "SUB_REGISTRAR_OFFICE"),
    ("PARTITION_DEED", "synthetic_partition_deed_{pid}.txt", "SUB_REGISTRAR_OFFICE"),
    ("GIFT_DEED", "synthetic_gift_deed_{pid}.txt", "SUB_REGISTRAR_OFFICE"),
    ("MORTGAGE_DEED", "synthetic_mortgage_{pid}.txt", "SUB_REGISTRAR_OFFICE"),
    ("CADASTRAL_SKETCH", "synthetic_sketch_{pid}.txt", "SURVEY_SETTLEMENT_OFFICE"),
]

DOC_QUALITIES = ["PRISTINE", "CLEAN", "SCANNED_FAINT", "OCR_DEGRADED"]


def generate_documents_and_fields(
    parcels: list[dict[str, Any]],
    ownership_claims: dict[str, list[dict[str, Any]]],
    target_documents: int,
    rng: random.Random,
    prov_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """
    Generates documents and fine-grained field annotations.
    Returns (documents_list, fields_list, docs_by_id).
    """
    documents: list[dict[str, Any]] = []
    fields: list[dict[str, Any]] = []
    doc_lookup: dict[str, Any] = {}

    field_seq = 1
    num_parcels = len(parcels)

    for doc_idx in range(1, target_documents + 1):
        did = document_id(doc_idx)
        parcel = parcels[(doc_idx - 1) % num_parcels]
        pid = parcel["parcel_id"]

        # Select document type
        dtype, fname_template, office_type = DOC_TYPES[(doc_idx - 1) % len(DOC_TYPES)]
        filename = fname_template.format(pid=pid.lower())

        reg_ref = synthetic_registration_ref("KLY", 2020 + (doc_idx % 5), 1 + (doc_idx % 4), doc_idx % 1000)
        quality = DOC_QUALITIES[(doc_idx - 1) % len(DOC_QUALITIES)]

        content_mock = (
            f"SYNTHETIC LAND RECORD — {dtype}\n"
            f"Document ID: {did}\n"
            f"Parcel ID: {pid}\n"
            f"Registration Ref: {reg_ref}\n"
            f"Office: {office_type}\n"
            f"Village: {parcel['village_name']}\n"
            f"Survey: {parcel['survey_number']}/{parcel['subdivision_number']}\n"
            f"Area: {parcel['area_value']} {parcel['area_unit']}\n"
            f"DISCLAIMER: 100% SYNTHETIC DEMO DATA — NOT AN OFFICIAL GOVERNMENT RECORD\n"
        )
        chash = sha256_text(content_mock)

        doc_row = {
            "document_id": did,
            "parcel_id": pid,
            "document_type": dtype,
            "synthetic_filename": filename,
            "language": "en",
            "document_date": parcel["record_effective_date"],
            "registration_reference": reg_ref,
            "issuing_office_type": office_type,
            "source_record_reference": f"ARCHIVE-VOL-{(doc_idx // 100) + 1:03d}",
            "page_count": 2 if dtype == "RECORD_OF_RIGHTS" else 4,
            "mime_type": "text/plain",
            "document_quality": quality,
            "synthetic_document_flag": True,
            "content_hash": chash,
            "extraction_status": "EXTRACTED",
            "provenance_id": prov_id,
        }
        documents.append(doc_row)
        doc_lookup[did] = doc_row

        # Determine primary owner name for annotations
        claims_for_p = ownership_claims.get(pid, [])
        owner_name = claims_for_p[0]["holder_name"] if claims_for_p else "Arjun Rao"

        # Generate 6 key fields per document
        field_specs = [
            ("owner", owner_name, owner_name, "STRING", None, 1, [120, 200, 150, 480]),
            ("survey_number", parcel["survey_number"], parcel["survey_number"], "STRING", None, 1, [200, 200, 230, 320]),
            ("subdivision_number", parcel["subdivision_number"], parcel["subdivision_number"], "STRING", None, 1, [200, 330, 230, 400]),
            ("plot_number", parcel["plot_number"], parcel["plot_number"], "STRING", None, 1, [240, 200, 270, 300]),
            ("area", f"{parcel['area_value']} {parcel['area_unit']}", str(parcel["area_value"]), "AREA", parcel["area_unit"], 2, [310, 200, 340, 420]),
            ("village", parcel["village_name"], parcel["village_name"], "STRING", None, 1, [160, 200, 190, 380]),
        ]

        for fname, gtruth, norm_val, dtype_field, unit_val, page_num, bbox in field_specs:
            fid = field_id(field_seq)
            field_seq += 1

            # Confidence based on quality
            base_conf = 0.98 if quality == "PRISTINE" else (0.92 if quality == "CLEAN" else 0.82)
            noise_type = "NONE"
            raw_text = gtruth

            # Inject OCR noise for OCR_DEGRADED documents
            if quality == "OCR_DEGRADED" and rng.random() < 0.35:
                raw_text, noise_type = apply_ocr_noise(gtruth, rng, rate=0.20)
                base_conf = round(rng.uniform(0.65, 0.79), 2)
            else:
                base_conf = round(rng.uniform(base_conf - 0.05, min(1.0, base_conf + 0.02)), 2)

            f_row = {
                "field_id": fid,
                "document_id": did,
                "field_name": fname,
                "raw_value": raw_text,
                "ground_truth_value": gtruth,
                "normalized_value": norm_val,
                "data_type": dtype_field,
                "unit": unit_val,
                "page_number": page_num,
                "bounding_box": bbox,
                "extraction_method": "OCR_TRANSCRIPTION",
                "confidence": base_conf,
                "noise_type": noise_type,
                "annotation_status": "VERIFIED_GROUND_TRUTH",
            }
            fields.append(f_row)

    return documents, fields, doc_lookup
