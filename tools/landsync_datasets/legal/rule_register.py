"""
Authoritative legal research register and technical validation rule catalogue.
Strictly separates verified statutory mandates, configurable data quality rules,
synthetic benchmark assumptions, and legal interpretations requiring qualified review.
"""

from __future__ import annotations

from landsync_datasets.schemas.models import (
    LegalRuleRecord,
    RuleCategory,
    VerificationStatus,
)

LEGAL_RULES: list[LegalRuleRecord] = [
    # 1. Registration Act, 1908 - Section 17
    LegalRuleRecord(
        rule_id="RULE-REG-1908-SEC17",
        title="Compulsory Registration of Real Property Conveyance Instruments",
        jurisdiction="IN_CENTRAL",
        instrument_type="CENTRAL_ACT",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/2261",
        provision_reference="Section 17(1)(b)",
        short_neutral_summary=(
            "Non-testamentary instruments which purport or operate to create, declare, assign, limit or extinguish "
            "any right, title or interest of value of one hundred rupees and upwards to or in immovable property "
            "must be registered compulsorily."
        ),
        applicable_workflow="CONVEYANCE_REGISTRATION",
        effective_from="1909-01-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Verified against official India Code gazette text. Applies uniformly across Indian states subject to state amendments.",
        limitations="Does not apply to wills, testamentary instruments, or leases not exceeding one year unless state law prescribes otherwise.",
        dataset_scenarios_using_rule=[
            "FULL_MATCH",
            "OWNER_NAME_MISMATCH",
            "INCOMPLETE_TRANSFER_EVIDENCE",
            "MULTI_FAULT_COMPOUND",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 2. Registration Act, 1908 - Section 49
    LegalRuleRecord(
        rule_id="RULE-REG-1908-SEC49",
        title="Effect of Non-Registration of Compulsorily Registrable Documents",
        jurisdiction="IN_CENTRAL",
        instrument_type="CENTRAL_ACT",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/2261",
        provision_reference="Section 49",
        short_neutral_summary=(
            "No document required by Section 17 or by any provision of the Transfer of Property Act, 1882 to be registered "
            "shall affect any immovable property comprised therein, or be received as evidence of any transaction affecting such property, "
            "unless it has been registered."
        ),
        applicable_workflow="CONVEYANCE_REGISTRATION",
        effective_from="1909-01-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Proviso allows unregistered document to be received as evidence of part performance under Section 53A TPA or as collateral transaction.",
        limitations="Admissibility for collateral purposes requires judicial interpretation.",
        dataset_scenarios_using_rule=[
            "INCOMPLETE_TRANSFER_EVIDENCE",
            "MUTATION_PENDING_UNAPPROVED",
            "ADVERSARIAL_BORDERLINE",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 3. Transfer of Property Act, 1882 - Section 54
    LegalRuleRecord(
        rule_id="RULE-TPA-1882-SEC54",
        title="Definition of Sale and Mode of Transfer of Tangible Immovable Property",
        jurisdiction="IN_CENTRAL",
        instrument_type="CENTRAL_ACT",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/2338",
        provision_reference="Section 54",
        short_neutral_summary=(
            "Sale is a transfer of ownership in exchange for a price paid or promised. Transfer of tangible immovable property "
            "of the value of one hundred rupees and upwards can be made only by a registered instrument."
        ),
        applicable_workflow="CONVEYANCE_REGISTRATION",
        effective_from="1882-07-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Contract for sale does not, of itself, create any interest in or charge on such property.",
        limitations="Applies to inter vivos transfers between living persons.",
        dataset_scenarios_using_rule=[
            "FULL_MATCH",
            "OWNER_NAME_MISMATCH",
            "AREA_MISMATCH",
            "SURVEY_NUMBER_MISMATCH",
            "MULTI_FAULT_COMPOUND",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 4. Transfer of Property Act, 1882 - Section 58 & 100
    LegalRuleRecord(
        rule_id="RULE-TPA-1882-SEC58",
        title="Mortgage and Encumbrance Formats on Immovable Property",
        jurisdiction="IN_CENTRAL",
        instrument_type="CENTRAL_ACT",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/2338",
        provision_reference="Section 58 & Section 100",
        short_neutral_summary=(
            "A mortgage is the transfer of an interest in specific immovable property for the purpose of securing payment of money. "
            "Where immovable property of one person is by act of parties or operation of law made security for payment of money, "
            "a charge is created."
        ),
        applicable_workflow="ENCUMBRANCE_MANAGEMENT",
        effective_from="1882-07-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Equitable mortgages (deposit of title deeds) require entry in CERSAI or local sub-registrar notice of intimation in several states.",
        limitations="Distinction between mortgage and charge depends on whether an interest in property is transferred.",
        dataset_scenarios_using_rule=[
            "UNDISCLOSED_MORTGAGE",
            "RELEASE_DATE_AMBIGUITY",
            "MULTI_FAULT_COMPOUND",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 5. Indian Easements Act, 1882 - Section 4 & 15
    LegalRuleRecord(
        rule_id="RULE-IEA-1882-SEC04",
        title="Easement Definition and Prescriptive Rights",
        jurisdiction="IN_CENTRAL",
        instrument_type="CENTRAL_ACT",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/2311",
        provision_reference="Section 4 & Section 15",
        short_neutral_summary=(
            "An easement is a right which the owner or occupier of certain land possesses, for the beneficial enjoyment of that land, "
            "to do and continue to do something, or to prevent and continue to prevent something being done, in or upon certain other land not his own. "
            "Prescriptive easement of way or water requires 20 years uninterrupted peaceful enjoyment."
        ),
        applicable_workflow="BOUNDARY_SURVEY",
        effective_from="1882-07-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Dominant and servient heritage rights must be examined during boundary surveys and access disputes.",
        limitations="Does not apply in territories where the Indian Easements Act has not been extended by notification.",
        dataset_scenarios_using_rule=[
            "EASEMENT_RESTRICTION_CONFLICT",
            "SPATIAL_OVERLAP_ANOMALY",
            "ADVERSARIAL_BORDERLINE",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 6. Karnataka Land Revenue Act, 1964 - Section 128
    LegalRuleRecord(
        rule_id="RULE-KLRA-1964-SEC128",
        title="Statutory Reporting of Acquisition of Rights in Land Records",
        jurisdiction="IN_KARNATAKA",
        instrument_type="STATE_ACT",
        official_source_url="http://dpal.karnataka.gov.in/storage/pdf-files/Acts/1964/12%20of%201964%20(E).pdf",
        provision_reference="Section 128",
        short_neutral_summary=(
            "Any person acquiring by succession, survivorship, inheritance, partition, purchase, mortgage, gift, lease or otherwise, "
            "any right as holder, occupant, owner, mortgagee, landlord or tenant of land shall report orally or in writing "
            "his acquisition of such right to the prescribed revenue officer within three months from date of acquisition."
        ),
        applicable_workflow="MUTATION",
        effective_from="1964-04-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Under Karnataka Bhoomi integration, sub-registrars transmit registered deeds electronically (J-slip) to revenue authorities.",
        limitations="Applicable strictly within Karnataka revenue jurisdiction.",
        dataset_scenarios_using_rule=[
            "FULL_MATCH",
            "MUTATION_PENDING_UNAPPROVED",
            "MUTATION_CHRONOLOGY_CONFLICT",
            "STALE_RECORD",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 7. Karnataka Land Revenue Act, 1964 - Section 129
    LegalRuleRecord(
        rule_id="RULE-KLRA-1964-SEC129",
        title="Register of Mutations and Statutory Objection Notice Period",
        jurisdiction="IN_KARNATAKA",
        instrument_type="STATE_ACT",
        official_source_url="http://dpal.karnataka.gov.in/storage/pdf-files/Acts/1964/12%20of%201964%20(E).pdf",
        provision_reference="Section 129",
        short_neutral_summary=(
            "The prescribed officer shall enter in the register of mutations every report made under Section 128 and post a copy of entry "
            "in the chavadi. Notice is issued to all persons interested, allowing a 30-day statutory period for filing objections before certifying the mutation."
        ),
        applicable_workflow="MUTATION",
        effective_from="1964-04-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Mutation entry does not create title; it represents fiscal liability for land revenue assessment.",
        limitations="Disputed cases are entered into a separate disputed cases register and heard by the Revenue Sheristedar/Tahsildar.",
        dataset_scenarios_using_rule=[
            "MUTATION_PENDING_UNAPPROVED",
            "MUTATION_CHRONOLOGY_CONFLICT",
            "INHERITANCE_COMPETING_CLAIM",
            "UNAUTHORIZED_MUTATION_ATTEMPT",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 8. Karnataka Land Revenue Act, 1964 - Section 95
    LegalRuleRecord(
        rule_id="RULE-KLRA-1964-SEC95",
        title="Diversion of Agricultural Land for Non-Agricultural Use (Conversion)",
        jurisdiction="IN_KARNATAKA",
        instrument_type="STATE_ACT",
        official_source_url="http://dpal.karnataka.gov.in/storage/pdf-files/Acts/1964/12%20of%201964%20(E).pdf",
        provision_reference="Section 95",
        short_neutral_summary=(
            "An occupant of land assessed for agriculture wishes to divert such land to any other purpose must apply to the Deputy Commissioner. "
            "Unauthorized non-agricultural use without sanction is prohibited and liable to eviction and penalties."
        ),
        applicable_workflow="LAND_USE_VALIDATION",
        effective_from="1964-04-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="AMENDED",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Amended by Karnataka Act 27 of 2022 providing deemed conversion process in master-plan areas.",
        limitations="Requires verified conversion order number and layout approval for residential/commercial claims.",
        dataset_scenarios_using_rule=[
            "LAND_USE_CONFLICT_CONVERSION",
            "PLANNING_ECO_RESTRICTION_OVERLAP",
            "MULTI_FAULT_COMPOUND",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 9. Hindu Succession Act, 1956 - Section 6
    LegalRuleRecord(
        rule_id="RULE-HSA-1956-SEC06",
        title="Equal Devolution of Interest in Coparcenary Property",
        jurisdiction="IN_CENTRAL",
        instrument_type="CENTRAL_ACT",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/1715",
        provision_reference="Section 6 (as amended by Act 39 of 2005)",
        short_neutral_summary=(
            "In a Joint Hindu family governed by Mitakshara law, the daughter of a coparcener shall by birth become a coparcener "
            "in her own right in the same manner as the son, having the same rights and liabilities."
        ),
        applicable_workflow="SUCCESSION_VALIDATION",
        effective_from="2005-09-09",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Confirmed by Supreme Court of India in Vineeta Sharma v. Rakesh Sharma (2020) 9 SCC 1 as conferring retroactive birthright.",
        limitations="Applies to persons governed by Hindu Succession Act; partition effected registered prior to 20 December 2004 protected.",
        dataset_scenarios_using_rule=[
            "CO_OWNERSHIP_INCONSISTENCY",
            "INHERITANCE_COMPETING_CLAIM",
            "ADVERSARIAL_BORDERLINE",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 10. RFCTLARR Act, 2013 - Section 11 & 19
    LegalRuleRecord(
        rule_id="RULE-RFCTLARR-2013-SEC11",
        title="Preliminary Notification of Land Acquisition and Transfer Restriction",
        jurisdiction="IN_CENTRAL",
        instrument_type="CENTRAL_ACT",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/2121",
        provision_reference="Section 11(4)",
        short_neutral_summary=(
            "No person shall make any transaction or cause any transaction of land specified in the preliminary notification "
            "published under Section 11, or create any encumbrance on such land from date of publication without prior sanction."
        ),
        applicable_workflow="ACQUISITION_VERIFICATION",
        effective_from="2014-01-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Transaction executed after Section 11 notification without sanction is void against the acquisition authority.",
        limitations="Applies to lands notified for public purpose acquisition.",
        dataset_scenarios_using_rule=[
            "PLANNING_ECO_RESTRICTION_OVERLAP",
            "UNDISCLOSED_MORTGAGE",
            "ADVERSARIAL_BORDERLINE",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 11. DPDP Act, 2023 - Section 4
    LegalRuleRecord(
        rule_id="RULE-DPDPA-2023-SEC04",
        title="Grounds for Processing and Strict Synthetic Data Demarcation",
        jurisdiction="IN_CENTRAL",
        instrument_type="CENTRAL_ACT",
        official_source_url="https://www.meity.gov.in/content/digital-personal-data-protection-act-2023",
        provision_reference="Section 4 & Section 6",
        short_neutral_summary=(
            "Personal data shall only be processed for lawful purpose with consent or legitimate uses. "
            "Synthetic data architecture mandates complete absence of real natural person identifiers to guarantee zero privacy harm."
        ),
        applicable_workflow="DATA_GOVERNANCE",
        effective_from="2023-08-11",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="All benchmark records must carry synthetic_record_flag=True and prohibit real Aadhaar/PAN tokens.",
        limitations="Dataset benchmarks must not ingest unconsented real citizen records.",
        dataset_scenarios_using_rule=[
            "FULL_MATCH",
            "OWNER_NAME_VARIATION",
            "OWNER_NAME_MISMATCH",
            "GOVERNANCE",
        ],
        rule_category=RuleCategory.A_VERIFIED_PROCEDURAL_MANDATE,
    ),
    # 12. DILRMP ULPIN Benchmark Rule
    LegalRuleRecord(
        rule_id="RULE-DILRMP-ULPIN-STD",
        title="Digital India Land Records Modernization - ULPIN Standard",
        jurisdiction="IN_CENTRAL",
        instrument_type="TECHNICAL_SPECIFICATION",
        official_source_url="https://dolr.gov.in/programmes/digital-india-land-records-modernization-programme-dilrmp",
        provision_reference="DoLR ULPIN Specification Guidelines 2021",
        short_neutral_summary=(
            "Unique Land Parcel Identification Number (ULPIN) is a 14-digit alphanumeric identification derived from "
            "geographic longitude and latitude centroid coordinates of the land parcel."
        ),
        applicable_workflow="PARCEL_IDENTIFICATION",
        effective_from="2021-04-01",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.SECONDARY_SOURCE_ONLY,
        reviewer_notes="Benchmark uses SYN-ULPIN- prefixed tokens to prevent collision with actual assigned Bhu-Aadhaar numbers.",
        limitations="Benchmark tokens are fictional and must not be queried against official Bhu-Aadhaar registries.",
        dataset_scenarios_using_rule=[
            "FULL_MATCH",
            "SURVEY_NUMBER_MISMATCH",
            "SUBDIVISION_MISMATCH",
        ],
        rule_category=RuleCategory.C_SYNTHETIC_BENCHMARK_ASSUMPTION,
    ),
    # 13. Area Tolerance Rule (Configurable Data Quality)
    LegalRuleRecord(
        rule_id="RULE-AREA-TOL-001",
        title="Area Extent Normalization and Comparison Tolerance",
        jurisdiction="TECHNICAL_COMMON",
        instrument_type="TECHNICAL_SPECIFICATION",
        official_source_url="https://github.com/sheikhsajid69/SIH26018/blob/main/apps/api/landsync/services.py",
        provision_reference="LANDSYNC Validation Specification Section 7.2",
        short_neutral_summary=(
            "Area comparisons apply a multi-tier tolerance: variance < 0.20% yields MATCH; "
            "0.20% <= variance < 1.00% yields PARTIAL_MATCH; variance >= 1.00% yields MISMATCH requiring human officer review."
        ),
        applicable_workflow="DATA_QUALITY",
        effective_from="2026-09-01",
        effective_until=None,
        source_last_verified_at="2026-10-09",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Tolerances accommodate rounding discrepancies between traditional guntha (101.17 m²) and decimal acre calculations.",
        limitations="Configurable threshold. High value urban parcels may require stricter absolute square metre tolerances.",
        dataset_scenarios_using_rule=[
            "FULL_MATCH",
            "AREA_MISMATCH",
            "MULTI_FAULT_COMPOUND",
            "ADVERSARIAL_BORDERLINE",
        ],
        rule_category=RuleCategory.B_CONFIGURABLE_DATA_QUALITY,
    ),
    # 14. Rule 13: Ambiguous Land Unit Protection
    LegalRuleRecord(
        rule_id="RULE-AMBIGUOUS-UNIT-R13",
        title="LANDSYNC Engineering Constitution Rule 13 (Ambiguous Unit Protection)",
        jurisdiction="TECHNICAL_COMMON",
        instrument_type="TECHNICAL_SPECIFICATION",
        official_source_url="https://github.com/sheikhsajid69/SIH26018/blob/main/Rules.md",
        provision_reference="Rule 13",
        short_neutral_summary=(
            "Never silently normalize ambiguous land units (e.g. bigha, biswa, katha, ground, kanal, marla); "
            "retain original unit and conversion evidence, and route to human review."
        ),
        applicable_workflow="DATA_QUALITY",
        effective_from="2026-09-12",
        effective_until=None,
        source_last_verified_at="2026-10-09",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Prevents automated corruption of revenue extents caused by variable definitions of bigha across tehsils.",
        limitations="Requires manual human officer input or verified tehsil conversion schedule.",
        dataset_scenarios_using_rule=[
            "UNIT_CONVERSION_AMBIGUITY",
            "MULTI_FAULT_COMPOUND",
        ],
        rule_category=RuleCategory.B_CONFIGURABLE_DATA_QUALITY,
    ),
    # 15. Spatial Topology and IoU Validation Rule
    LegalRuleRecord(
        rule_id="RULE-SPATIAL-IOU-001",
        title="Cadastral Cadastre Boundary Polygon Alignment and IoU Validation",
        jurisdiction="TECHNICAL_COMMON",
        instrument_type="TECHNICAL_SPECIFICATION",
        official_source_url="https://github.com/sheikhsajid69/SIH26018/blob/main/apps/api/landsync/gis.py",
        provision_reference="LANDSYNC GIS Module Section 3.1",
        short_neutral_summary=(
            "Submitted polygon boundaries compared to authoritative cadastral records evaluate IoU >= 0.90 as CONSISTENT, "
            "0.70 <= IoU < 0.90 as ADVISORY_ALIGNMENT_NEEDED, and IoU < 0.70 or centroid offset > 10m as SPATIAL_VARIANCE_DETECTED."
        ),
        applicable_workflow="SPATIAL_VALIDATION",
        effective_from="2026-09-23",
        effective_until=None,
        source_last_verified_at="2026-10-09",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Geodesic metric area and shoelace formula used at centroid latitude on EPSG:4326 coordinates.",
        limitations="Planar approximation at centroid latitude valid for parcel scales; large district polygons require spherical geodesics.",
        dataset_scenarios_using_rule=[
            "SPATIAL_EXTENT_VARIANCE",
            "SPATIAL_OVERLAP_ANOMALY",
            "CRS_OR_COORDINATE_SHIFT",
            "SLIVER_OR_GAP_DISCREPANCY",
        ],
        rule_category=RuleCategory.B_CONFIGURABLE_DATA_QUALITY,
    ),
    # 16. Rule 8: Low Confidence AI Extraction Rule
    LegalRuleRecord(
        rule_id="RULE-DOC-CONFIDENCE-R8",
        title="LANDSYNC Engineering Constitution Rule 8 (Low-Confidence Escalation)",
        jurisdiction="TECHNICAL_COMMON",
        instrument_type="TECHNICAL_SPECIFICATION",
        official_source_url="https://github.com/sheikhsajid69/SIH26018/blob/main/Rules.md",
        provision_reference="Rule 8",
        short_neutral_summary=(
            "Always route low-confidence or conflicting information to human review. "
            "AI extractions with field-level confidence < 0.80 must produce REVIEW_REQUIRED even if text matches reference."
        ),
        applicable_workflow="DOCUMENT_AI",
        effective_from="2026-09-12",
        effective_until=None,
        source_last_verified_at="2026-10-09",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.VERIFIED_PRIMARY_SOURCE,
        reviewer_notes="Enforces human-in-the-loop governance for faded, noisy, or low-resolution historical land records.",
        limitations="Threshold parameter may be tuned per document quality tier.",
        dataset_scenarios_using_rule=[
            "LOW_CONFIDENCE_EXTRACTION",
            "OCR_NOISE_TRANSCRIPTION",
            "MISSING_SCHEDULE_PAGE",
        ],
        rule_category=RuleCategory.B_CONFIGURABLE_DATA_QUALITY,
    ),
    # 17. Karnataka Land Reforms Act, 1961 - Agricultural Ceiling
    LegalRuleRecord(
        rule_id="RULE-KLRA-1961-SEC63",
        title="Ceiling on Agricultural Land Holdings and Transfer Disqualification",
        jurisdiction="IN_KARNATAKA",
        instrument_type="STATE_ACT",
        official_source_url="http://dpal.karnataka.gov.in/storage/pdf-files/Acts/1962/10%20of%201962%20(E).pdf",
        provision_reference="Section 63 & Section 64",
        short_neutral_summary=(
            "Ceiling area for a person or family unit in Karnataka is determined by standard units (ranging from 10 to 54 acres "
            "depending on soil/irrigation class). Any transfer exceeding ceiling limit is void and vests in the State Government."
        ),
        applicable_workflow="CONVEYANCE_REGISTRATION",
        effective_from="1962-03-15",
        effective_until=None,
        source_last_verified_at="2026-09-15",
        amendment_status="CURRENT",
        verification_status=VerificationStatus.NEEDS_LEGAL_REVIEW,
        reviewer_notes="Calculation of standard units requires revenue soil class schedule. Requires qualified legal review before automated adjudication.",
        limitations="Complex soil classification formulas apply; synthetic scenarios model advisory warnings.",
        dataset_scenarios_using_rule=[
            "CO_OWNERSHIP_INCONSISTENCY",
            "ADVERSARIAL_BORDERLINE",
        ],
        rule_category=RuleCategory.D_LEGAL_INTERPRETATION_NEEDS_REVIEW,
    ),
]


def get_rule_by_id(rule_id: str) -> LegalRuleRecord | None:
    for r in LEGAL_RULES:
        if r.rule_id == rule_id:
            return r
    return None


def get_all_rules() -> list[LegalRuleRecord]:
    return list(LEGAL_RULES)
