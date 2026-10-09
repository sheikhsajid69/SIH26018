"""
Synthetic Validation Case and Finding Generator.
Executes scenario quotas, creating 2,500+ reproducible benchmark validation cases
and fine-grained explainable validation findings.
"""

from __future__ import annotations

import random
from typing import Any

from landsync_datasets.primitives.identifiers import (
    validation_case_id,
    validation_finding_id,
    split_group_id,
)

# Standard reason codes and rule mappings for scenario families
SCENARIO_CONFIG_MAPPING = {
    "FULL_MATCH": {
        "reason_codes": ["CONSISTENT_ACROSS_REGISTERS"],
        "rule_ids": ["RULE-REG-1908-SEC17", "RULE-TPA-1882-SEC54", "RULE-AREA-TOL-001"],
        "field_name": "overall",
        "finding_status": "CONSISTENT",
        "severity": "NONE",
        "explanation": "Document fields and authoritative revenue records match completely within statutory tolerances.",
    },
    "OWNER_NAME_VARIATION": {
        "reason_codes": ["NAME_ORDER_OR_HONORIFIC_VARIANT"],
        "rule_ids": ["RULE-TPA-1882-SEC54"],
        "field_name": "owner",
        "finding_status": "CONSISTENT",
        "severity": "LOW",
        "explanation": "Acceptable name ordering, honorific (S/o), or transliteration difference.",
    },
    "OWNER_NAME_MISMATCH": {
        "reason_codes": ["HOLDER_IDENTITY_DISCREPANCY"],
        "rule_ids": ["RULE-TPA-1882-SEC54", "RULE-REG-1908-SEC17"],
        "field_name": "owner",
        "finding_status": "RECORD_MISMATCH",
        "severity": "HIGH",
        "explanation": "Holder name in deed does not match recorded khatedar in revenue register.",
    },
    "AREA_MISMATCH": {
        "reason_codes": ["EXTENT_VARIANCE_EXCEEDS_TOLERANCE"],
        "rule_ids": ["RULE-AREA-TOL-001"],
        "field_name": "area",
        "finding_status": "RECORD_MISMATCH",
        "severity": "MEDIUM",
        "explanation": "Area variance between document and authority record exceeds 1.0% statutory tolerance.",
    },
    "UNIT_CONVERSION_AMBIGUITY": {
        "reason_codes": ["RULE_13_AMBIGUOUS_REGIONAL_UNIT"],
        "rule_ids": ["RULE-AMBIGUOUS-UNIT-R13"],
        "field_name": "area",
        "finding_status": "REVIEW_REQUIRED",
        "severity": "HIGH",
        "explanation": "Regional unit (e.g. bigha) varies by tehsil and cannot be automatically converted safely under Rule 13.",
    },
    "SURVEY_NUMBER_MISMATCH": {
        "reason_codes": ["PRIMARY_SURVEY_IDENTIFIER_CONFLICT"],
        "rule_ids": ["RULE-KLRA-1964-SEC128", "RULE-DILRMP-ULPIN-STD"],
        "field_name": "survey_number",
        "finding_status": "RECORD_MISMATCH",
        "severity": "HIGH",
        "explanation": "Submitted document specifies different primary survey number than authority profile.",
    },
    "SUBDIVISION_MISMATCH": {
        "reason_codes": ["HISSA_SUBDIVISION_CONFLICT"],
        "rule_ids": ["RULE-KLRA-1964-SEC128"],
        "field_name": "subdivision_number",
        "finding_status": "RECORD_MISMATCH",
        "severity": "MEDIUM",
        "explanation": "Subdivision (Hissa) number mismatch between deed and RTC extract.",
    },
    "PLOT_MISMATCH": {
        "reason_codes": ["PLOT_LAYOUT_NUMBER_CONFLICT"],
        "rule_ids": ["RULE-TPA-1882-SEC54"],
        "field_name": "plot_number",
        "finding_status": "RECORD_MISMATCH",
        "severity": "MEDIUM",
        "explanation": "Plot/site number mismatch in converted non-agricultural layout.",
    },
    "VILLAGE_MISMATCH": {
        "reason_codes": ["REVENUE_VILLAGE_MISMATCH"],
        "rule_ids": ["RULE-KLRA-1964-SEC128"],
        "field_name": "village",
        "finding_status": "RECORD_MISMATCH",
        "severity": "HIGH",
        "explanation": "Document specifies different revenue village jurisdiction than authoritative parcel index.",
    },
    "MISSING_FIELD": {
        "reason_codes": ["MANDATORY_FIELD_NOT_EXTRACTED"],
        "rule_ids": ["RULE-REG-1908-SEC17"],
        "field_name": "area",
        "finding_status": "DOCUMENT_MISSING",
        "severity": "MEDIUM",
        "explanation": "Mandatory property extent schedule was missing from uploaded instrument.",
    },
    "DUPLICATE_DOCUMENT": {
        "reason_codes": ["IDENTICAL_DOCUMENT_SHA256_MATCH"],
        "rule_ids": ["RULE-REG-1908-SEC17"],
        "field_name": "document",
        "finding_status": "POSSIBLE_DUPLICATE",
        "severity": "LOW",
        "explanation": "Duplicate document hash detected across previous uploads for this parcel.",
    },
    "STALE_RECORD": {
        "reason_codes": ["SUPERSEDED_HISTORICAL_RECORD"],
        "rule_ids": ["RULE-KLRA-1964-SEC128"],
        "field_name": "mutation",
        "finding_status": "SOURCE_CONFLICT",
        "severity": "MEDIUM",
        "explanation": "Submitted record reflects superseded historical entry prior to a subsequent certified mutation.",
    },
    "CO_OWNERSHIP_INCONSISTENCY": {
        "reason_codes": ["UNDIVIDED_SHARE_SUM_DISCREPANCY"],
        "rule_ids": ["RULE-HSA-1956-SEC06", "RULE-KLRA-1961-SEC63"],
        "field_name": "share_extent",
        "finding_status": "RECORD_MISMATCH",
        "severity": "HIGH",
        "explanation": "Sum of declared co-parcenary shares does not equal unity or sole party claims undivided interest.",
    },
    "INHERITANCE_COMPETING_CLAIM": {
        "reason_codes": ["COMPETING_SUCCESSION_CLAIMS"],
        "rule_ids": ["RULE-HSA-1956-SEC06"],
        "field_name": "owner",
        "finding_status": "SOURCE_CONFLICT",
        "severity": "HIGH",
        "explanation": "Multiple competing succession declarations recorded under Hindu Succession Act Sec 6.",
    },
    "MUTATION_PENDING_UNAPPROVED": {
        "reason_codes": ["STATUTORY_OBJECTION_PERIOD_ACTIVE"],
        "rule_ids": ["RULE-KLRA-1964-SEC129"],
        "field_name": "mutation",
        "finding_status": "REVIEW_REQUIRED",
        "severity": "MEDIUM",
        "explanation": "Mutation entry under 30-day statutory notice period pursuant to Section 129 KLRA.",
    },
    "MUTATION_CHRONOLOGY_CONFLICT": {
        "reason_codes": ["EVENT_PRECEDES_TRIGGERING_INSTRUMENT"],
        "rule_ids": ["RULE-KLRA-1964-SEC128", "RULE-KLRA-1964-SEC129"],
        "field_name": "effective_date",
        "finding_status": "CHRONOLOGY_CONFLICT",
        "severity": "HIGH",
        "explanation": "Mutation effective date is recorded earlier than the underlying registered conveyance deed.",
    },
    "INCOMPLETE_TRANSFER_EVIDENCE": {
        "reason_codes": ["MISSING_INTERMEDIATE_LINK_DEED"],
        "rule_ids": ["RULE-REG-1908-SEC49", "RULE-TPA-1882-SEC54"],
        "field_name": "chain_of_title",
        "finding_status": "DOCUMENT_MISSING",
        "severity": "HIGH",
        "explanation": "Chain of title transfer missing intermediate registered deed link.",
    },
    "UNDISCLOSED_MORTGAGE": {
        "reason_codes": ["ACTIVE_MORTGAGE_CHARGE_RECORDED"],
        "rule_ids": ["RULE-TPA-1882-SEC58"],
        "field_name": "encumbrance",
        "finding_status": "RECORD_MISMATCH",
        "severity": "HIGH",
        "explanation": "Active mortgage recorded in revenue register was not disclosed in conveyance schedule.",
    },
    "EASEMENT_RESTRICTION_CONFLICT": {
        "reason_codes": ["SERVIENT_EASEMENT_RIGHT_OF_WAY"],
        "rule_ids": ["RULE-IEA-1882-SEC04"],
        "field_name": "easement",
        "finding_status": "REVIEW_REQUIRED",
        "severity": "MEDIUM",
        "explanation": "Prescriptive right-of-way easement documented in survey sketch omitted in deed schedule.",
    },
    "RELEASE_DATE_AMBIGUITY": {
        "reason_codes": ["DISCHARGE_DEED_DATE_AMBIGUITY"],
        "rule_ids": ["RULE-TPA-1882-SEC58"],
        "field_name": "encumbrance",
        "finding_status": "REVIEW_REQUIRED",
        "severity": "LOW",
        "explanation": "Discharge voucher date lacks formal sub-registrar certification timestamp.",
    },
    "SPATIAL_EXTENT_VARIANCE": {
        "reason_codes": ["POLYGON_AREA_DIFFERS_FROM_SCHEDULE"],
        "rule_ids": ["RULE-SPATIAL-IOU-001"],
        "field_name": "geometry",
        "finding_status": "SPATIAL_INCONSISTENCY",
        "severity": "MEDIUM",
        "explanation": "Polygon area computed from geometry deviates > 5% from schedule textual area.",
    },
    "SPATIAL_OVERLAP_ANOMALY": {
        "reason_codes": ["CADASTRAL_BOUNDARY_OVERLAP"],
        "rule_ids": ["RULE-SPATIAL-IOU-001"],
        "field_name": "geometry",
        "finding_status": "SPATIAL_INCONSISTENCY",
        "severity": "HIGH",
        "explanation": "Cadastral boundary overlaps with adjacent parcel or reserved common land.",
    },
    "INVALID_GEOMETRY_RING": {
        "reason_codes": ["TOPOLOGY_RING_OR_INTERSECTION_ERROR"],
        "rule_ids": ["RULE-SPATIAL-IOU-001"],
        "field_name": "geometry",
        "finding_status": "SPATIAL_INCONSISTENCY",
        "severity": "HIGH",
        "explanation": "Self-intersecting bow-tie polygon or unclosed coordinate ring detected.",
    },
    "CRS_OR_COORDINATE_SHIFT": {
        "reason_codes": ["COORDINATE_OFFSET_OR_DATUM_SHIFT"],
        "rule_ids": ["RULE-SPATIAL-IOU-001"],
        "field_name": "geometry",
        "finding_status": "SPATIAL_INCONSISTENCY",
        "severity": "HIGH",
        "explanation": "Centroid offset greater than 10 meters indicating CRS mismatch or datum shift.",
    },
    "SLIVER_OR_GAP_DISCREPANCY": {
        "reason_codes": ["SLIVER_POLYGON_ANOMALY"],
        "rule_ids": ["RULE-SPATIAL-IOU-001"],
        "field_name": "geometry",
        "finding_status": "SPATIAL_INCONSISTENCY",
        "severity": "MEDIUM",
        "explanation": "Extreme aspect ratio sliver polygon detected along boundary line.",
    },
    "OCR_NOISE_TRANSCRIPTION": {
        "reason_codes": ["OCR_CHARACTER_SUBSTITUTION"],
        "rule_ids": ["RULE-DOC-CONFIDENCE-R8"],
        "field_name": "owner",
        "finding_status": "CONSISTENT",
        "severity": "LOW",
        "explanation": "Simulated OCR character substitution resolved via fuzzy string matching.",
    },
    "LOW_CONFIDENCE_EXTRACTION": {
        "reason_codes": ["LOW_CONFIDENCE_BELOW_RULE8_THRESHOLD"],
        "rule_ids": ["RULE-DOC-CONFIDENCE-R8"],
        "field_name": "survey_number",
        "finding_status": "REVIEW_REQUIRED",
        "severity": "LOW",
        "explanation": "Extracted field value matches text but model confidence is < 0.80 triggering Rule 8 review.",
    },
    "MISSING_SCHEDULE_PAGE": {
        "reason_codes": ["DEED_SCHEDULE_PAGE_OMITTED"],
        "rule_ids": ["RULE-REG-1908-SEC17"],
        "field_name": "document",
        "finding_status": "DOCUMENT_MISSING",
        "severity": "HIGH",
        "explanation": "Deed boundary schedule page omitted from uploaded document bundle.",
    },
    "LAND_USE_CONFLICT_CONVERSION": {
        "reason_codes": ["UNAUTHORIZED_NON_AGRICULTURAL_USE"],
        "rule_ids": ["RULE-KLRA-1964-SEC95"],
        "field_name": "land_use",
        "finding_status": "RECORD_MISMATCH",
        "severity": "HIGH",
        "explanation": "Non-agricultural commercial claim without Section 95 conversion sanction order.",
    },
    "PLANNING_ECO_RESTRICTION_OVERLAP": {
        "reason_codes": ["ECO_BUFFER_RESTRICTION_OVERLAP"],
        "rule_ids": ["RULE-RFCTLARR-2013-SEC11"],
        "field_name": "planning_zone",
        "finding_status": "REVIEW_REQUIRED",
        "severity": "HIGH",
        "explanation": "Parcel boundary intersects protected lake buffer or preliminary acquisition zone.",
    },
    "UNAUTHORIZED_MUTATION_ATTEMPT": {
        "reason_codes": ["ROLE_AUTHORIZATION_VIOLATION"],
        "rule_ids": ["RULE-KLRA-1964-SEC129"],
        "field_name": "audit",
        "finding_status": "REVIEW_REQUIRED",
        "severity": "HIGH",
        "explanation": "Non-authorized persona attempted to sanction mutation without officer credentials.",
    },
    "AUDIT_TRAIL_GAP": {
        "reason_codes": ["UNTRACED_HISTORICAL_TRANSITION"],
        "rule_ids": ["RULE-DPDPA-2023-SEC04"],
        "field_name": "audit",
        "finding_status": "REVIEW_REQUIRED",
        "severity": "MEDIUM",
        "explanation": "Historical revenue ledger transition lacking digital signature or officer trace ID.",
    },
    "MULTI_FAULT_COMPOUND": {
        "reason_codes": ["COMPOUND_AREA_AND_HOLDER_MISMATCH", "SPATIAL_VARIANCE_PRESENT"],
        "rule_ids": ["RULE-TPA-1882-SEC54", "RULE-AREA-TOL-001", "RULE-SPATIAL-IOU-001"],
        "field_name": "multi_field",
        "finding_status": "RECORD_MISMATCH",
        "severity": "HIGH",
        "explanation": "Multiple interacting discrepancies across holder name, extent, and spatial geometry.",
    },
    "ADVERSARIAL_BORDERLINE": {
        "reason_codes": ["MARGINAL_TOLERANCE_EDGE_CASE"],
        "rule_ids": ["RULE-AREA-TOL-001", "RULE-HSA-1956-SEC06"],
        "field_name": "multi_field",
        "finding_status": "REVIEW_REQUIRED",
        "severity": "HIGH",
        "explanation": "Adversarial borderline case combining fractional coparcenary shares and boundary shift.",
    },
}


def generate_validation_cases_and_findings(
    scenario_quotas: dict[str, Any],
    parcels: list[dict[str, Any]],
    documents: list[dict[str, Any]],
    rng: random.Random,
    generator_version: str = "1.0.0",
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Generates validation cases and findings matching scenario quotas.
    Returns (cases_list, findings_list).
    """
    cases: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    case_seq = 1
    finding_seq = 1
    num_parcels = len(parcels)
    num_docs = len(documents)

    parcel_offset = 0

    for scenario_family, quota_info in scenario_quotas.items():
        count = quota_info.get("count", 10)
        difficulty = quota_info.get("difficulty", "MEDIUM")
        expected_outcome = quota_info.get("expected_outcome", "MATCH")
        review_required = quota_info.get("review_required", False)

        cfg = SCENARIO_CONFIG_MAPPING.get(scenario_family, SCENARIO_CONFIG_MAPPING["FULL_MATCH"])

        for i in range(count):
            cid = validation_case_id(case_seq)
            case_seq += 1

            p_idx = (parcel_offset + i) % num_parcels
            parcel = parcels[p_idx]
            pid = parcel["parcel_id"]
            doc = documents[(parcel_offset + i) % num_docs]
            did = doc["document_id"]
            gid = parcel["boundary_geometry_id"]

            grp_id = split_group_id(p_idx + 1)

            # Expected ground truth confidence
            conf = 0.99 if expected_outcome == "MATCH" else (0.85 if difficulty == "MEDIUM" else 0.75)

            case_row = {
                "case_id": cid,
                "primary_parcel_id": pid,
                "scenario_family": scenario_family,
                "scenario_tags": [scenario_family.lower(), difficulty.lower(), expected_outcome.lower()],
                "difficulty": difficulty,
                "input_record_ids": [pid, did, gid],
                "expected_outcome": expected_outcome,
                "expected_reason_codes": cfg["reason_codes"],
                "expected_rule_ids": cfg["rule_ids"],
                "review_required": review_required,
                "ground_truth_confidence": round(conf, 2),
                "split_group_id": grp_id,
                "generator_version": generator_version,
                "seed_reference": seed,
            }
            cases.append(case_row)

            # Generate primary finding
            fid = validation_finding_id(finding_seq)
            finding_seq += 1

            fname = cfg["field_name"]
            src_val = "Document Value"
            cmp_val = "Authority Value"
            norm_src = "Norm Doc"
            norm_cmp = "Norm Auth"

            if fname == "owner":
                src_val = "Submitted Owner" if expected_outcome != "MATCH" else parcel.get("holder_name", "Arjun Rao")
                cmp_val = parcel.get("holder_name", "Arjun Rao")
            elif fname == "area":
                src_val = f"{parcel['area_value'] * 1.05:.2f} {parcel['area_unit']}" if expected_outcome != "MATCH" else f"{parcel['area_value']} {parcel['area_unit']}"
                cmp_val = f"{parcel['area_value']} {parcel['area_unit']}"
            elif fname == "survey_number":
                src_val = f"{parcel['survey_number']}_DISC" if expected_outcome != "MATCH" else parcel["survey_number"]
                cmp_val = parcel["survey_number"]

            finding_row = {
                "finding_id": fid,
                "case_id": cid,
                "field_name": fname,
                "source_value": src_val,
                "comparison_value": cmp_val,
                "normalized_source_value": norm_src,
                "normalized_comparison_value": norm_cmp,
                "rule_id": cfg["rule_ids"][0],
                "finding_status": cfg["finding_status"],
                "severity": cfg["severity"],
                "explanation": cfg["explanation"],
                "review_required": review_required,
            }
            findings.append(finding_row)

        parcel_offset += count

    return cases, findings
