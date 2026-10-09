# LANDSYNC-India Benchmark: Data Dictionary

Comprehensive column-level schema documentation for all 13 relational entities in the LANDSYNC-India Synthetic Benchmark.

---

## 1. `parcels`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `parcel_id` | string | No | Deterministic synthetic primary key | `SYN-PARCEL-000001` |
| `synthetic_record_flag` | boolean | No | Strict synthetic data indicator (always `true`) | `true` |
| `jurisdiction_id` | string | No | Jurisdiction profile reference | `KA_PILOT` |
| `village_code` | string | No | Synthetic village identifier | `SYN-VIL-01` |
| `village_name` | string | No | Fictional village name | `Hemavathi` |
| `survey_number` | string | No | Primary cadastral survey number | `101` |
| `subdivision_number` | string | No | Subdivision / Hissa number | `1` |
| `plot_number` | string | No | Plot / site layout number | `12A` |
| `parcel_type` | string | No | Broad land category | `RURAL_AGRICULTURAL` |
| `land_classification` | string | No | Soil or use classification | `Agricultural Dry (Kushki)` |
| `area_value` | float | No | Extent value stated in source record | `2.40` |
| `area_unit` | string | No | Stated extent unit metric | `acre` |
| `area_square_metres` | float | No | Normalized extent in SI square metres | `9712.4554` |
| `area_normalization_method`| string | No | Statutory rule applied for conversion | `STANDARD_STATUTORY_CONVERSION_ACRE` |
| `boundary_geometry_id` | string | No | Foreign key to `spatial_features` | `SYN-GEOM-000001` |
| `source_record_id` | string | No | Reference authority record extract ID | `SYN-ROR-EXTRACT-000001` |
| `record_effective_date` | string | No | ISO 8601 date when record took effect | `2021-04-12` |
| `record_status` | string | No | Current administrative status | `ACTIVE` |
| `provenance_id` | string | No | Foreign key to `provenance` table | `SYN-PROV-000001` |
| `ulpin` | string | No | Fictional benchmark ULPIN token | `SYN-ULPIN-KA-000001` |

---

## 2. `parties`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `party_id` | string | No | Deterministic synthetic party key | `SYN-PARTY-000001` |
| `synthetic_record_flag` | boolean | No | Strict synthetic indicator (always `true`) | `true` |
| `synthetic_display_name` | string | No | Fictional landowner full name | `Arjun Rao` |
| `party_type` | string | No | Persona legal type | `INDIVIDUAL` |
| `name_language` | string | No | Primary language script | `en` |
| `name_variants` | json/list | No | Aliases, inverted forms, honorifics | `["Rao Arjun", "Arjuna Rao"]` |
| `identity_reference_type`| string | No | Benchmark token classification | `SYNTHETIC_BENCHMARK_TOKEN` |
| `identity_reference_value`| string| No | Fictional identity token (never real ID) | `SYN-ID-BENCHMARK-0000001` |
| `identity_reference_is_synthetic` | boolean | No | Strict synthetic indicator | `true` |
| `consent_or_authority_status` | string | No | Synthetic consent metadata | `SYNTHETIC_CONSENT_VERIFIED` |

---

## 3. `ownership_claims`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `claim_id` | string | No | Synthetic claim primary key | `SYN-CLAIM-000001` |
| `parcel_id` | string | No | Foreign key to `parcels` | `SYN-PARCEL-000001` |
| `party_id` | string | No | Foreign key to `parties` | `SYN-PARTY-000001` |
| `holder_name` | string | No | Cached display name of claimant | `Arjun Rao` |
| `claim_type` | string | No | Legal category of interest | `SOLE_KHATEDAR` |
| `share_numerator` | integer| No | Numerator of undivided interest | `1` |
| `share_denominator` | integer| No | Denominator of undivided interest | `1` |
| `claim_start_date` | string | No | ISO start date of claim | `2021-04-12` |
| `claim_end_date` | string | Yes | ISO end date if extinguished | `None` |
| `source_document_id` | string | No | Supporting registered deed/extract ID | `SYN-DOC-000001` |
| `source_status` | string | No | Source category | `REVENUE_RECORD_OF_RIGHTS` |
| `verification_status` | string | No | Administrative verification status | `RECORD_VERIFIED` |
| `benchmark_note` | string | No | Contextual scenario notes | `Sole recorded title holder.` |

---

## 4. `documents`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `document_id` | string | No | Primary key for document | `SYN-DOC-000001` |
| `parcel_id` | string | No | Foreign key to `parcels` | `SYN-PARCEL-000001` |
| `document_type` | string | No | Category of legal instrument | `RECORD_OF_RIGHTS` |
| `synthetic_filename` | string | No | Standardized mock filename | `synthetic_rtc_syn-parcel-000001.txt` |
| `language` | string | No | Document language | `en` |
| `document_date` | string | No | Date of execution / extract issue | `2021-04-12` |
| `registration_reference` | string | No | Fictional sub-registrar volume/number | `SYN-SRO-KLY/BK1/0001/2021` |
| `issuing_office_type` | string | No | Issuing administrative agency | `REVENUE_TALUK_OFFICE` |
| `source_record_reference`| string | No | Archive volume reference | `ARCHIVE-VOL-001` |
| `page_count` | integer| No | Number of pages | `2` |
| `mime_type` | string | No | Content MIME type | `text/plain` |
| `document_quality` | string | No | Simulated scan quality grade | `PRISTINE` |
| `synthetic_document_flag`| boolean| No | Strict synthetic flag | `true` |
| `content_hash` | string | No | SHA-256 digest of document body | `e3b0c44298fc1c149afbf4c89...` |
| `extraction_status` | string | No | Document AI extraction pipeline state | `EXTRACTED` |
| `provenance_id` | string | No | Foreign key to `provenance` | `SYN-PROV-000001` |

---

## 5. `document_fields`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `field_id` | string | No | Synthetic field annotation key | `SYN-FIELD-000001` |
| `document_id` | string | No | Foreign key to `documents` | `SYN-DOC-000001` |
| `field_name` | string | No | Extracted attribute name | `owner` |
| `raw_value` | string | No | Raw extracted text from simulated OCR | `Arjun Rao` |
| `ground_truth_value` | string | No | True underlying clean value | `Arjun Rao` |
| `normalized_value` | string | No | Standardized canonical string | `Arjun Rao` |
| `data_type` | string | No | Semantic data type | `STRING` |
| `unit` | string | Yes | Extracted unit if applicable | `None` |
| `page_number` | integer| No | Page index (1-based) | `1` |
| `bounding_box` | json/list | No | Normalized [ymin, xmin, ymax, xmax] | `[120, 200, 150, 480]` |
| `extraction_method` | string | No | Simulated AI extraction technique | `OCR_TRANSCRIPTION` |
| `confidence` | float | No | Model extraction confidence (0.0–1.0) | `0.98` |
| `noise_type` | string | No | Simulated scan degradation applied | `NONE` |
| `annotation_status` | string | No | Annotation quality status | `VERIFIED_GROUND_TRUTH` |

---

## 6. `mutation_events`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `mutation_event_id` | string | No | Mutation timeline primary key | `SYN-MUT-000001` |
| `parcel_id` | string | No | Foreign key to `parcels` | `SYN-PARCEL-000001` |
| `event_type` | string | No | Legal transfer or succession type | `SALE_TRANSFER` |
| `application_date` | string | No | ISO date of reporting under Sec 128 | `2021-03-01` |
| `event_date` | string | No | Date of deed execution | `2021-03-04` |
| `effective_date` | string | No | Date mutation certified / effective | `2021-04-01` |
| `recorded_date` | string | No | Date entered in revenue ledger | `2021-04-01` |
| `source_document_id` | string | No | Foreign key to `documents` | `SYN-DOC-000001` |
| `previous_claim_id` | string | Yes | Extinguished claim reference | `SYN-CLAIM-000001` |
| `resulting_claim_id` | string | Yes | Created claim reference | `SYN-CLAIM-000002` |
| `event_status` | string | No | Administrative certification status | `SANCTIONED` |
| `event_sequence` | integer| No | Chronological order on this parcel | `1` |
| `benchmark_expected_outcome`| string| No| Ground truth evaluation label | `MATCH` |

---

## 7. `encumbrances`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `interest_id` | string | No | Primary key for encumbrance | `SYN-INT-000001` |
| `parcel_id` | string | No | Foreign key to `parcels` | `SYN-PARCEL-000001` |
| `interest_type` | string | No | Nature of charge or easement | `MORTGAGE_SIMPLE` |
| `source_document_id` | string | No | Foreign key to `documents` | `SYN-DOC-000005` |
| `effective_from` | string | No | ISO start date of encumbrance | `2020-03-15` |
| `effective_until` | string | Yes | ISO discharge date if released | `None` |
| `status` | string | No | Current legal status of interest | `ACTIVE` |
| `source_verification_status`| string| No | Registry notation status | `REGISTERED_CHARGE` |
| `benchmark_note` | string | No | Scenario description | `Mortgage recorded under TPA Sec 58.` |

---

## 8. `spatial_features`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `geometry_id` | string | No | Spatial feature primary key | `SYN-GEOM-000001` |
| `parcel_id` | string | No | Foreign key to `parcels` | `SYN-PARCEL-000001` |
| `geometry_type` | string | No | GeoJSON geometry type | `Polygon` |
| `coordinate_reference_system`| string| No | CRS of coordinates | `EPSG:4326` |
| `geometry` | json/dict| No | GeoJSON geometry dictionary | `{"type": "Polygon", ...}` |
| `area_from_geometry` | float | No | Geodesic area in square metres | `9712.46` |
| `perimeter_from_geometry` | float | No | Geodesic perimeter in metres | `398.42` |
| `geometry_validity` | string | No | Topology check result | `VALID` |
| `spatial_quality_status` | string | No | Consistency vs recorded extent | `CONSISTENT` |
| `source_reference` | string | No | Provenance of spatial data | `CADASTRAL_MAP_OFFICIAL` |
| `synthetic_geometry_flag`| boolean| No | Strict synthetic flag | `true` |

---

## 9. `validation_cases`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `case_id` | string | No | Unique benchmark test case ID | `SYN-CASE-000001` |
| `primary_parcel_id` | string | No | Foreign key to parcel under test | `SYN-PARCEL-000001` |
| `scenario_family` | string | No | Test scenario category | `FULL_MATCH` |
| `scenario_tags` | json/list | No | Categorical test tags | `["full_match", "easy", "match"]` |
| `difficulty` | string | No | Difficulty grade (EASY/MEDIUM/HARD/ADVERSARIAL) | `EASY` |
| `input_record_ids` | json/list | No | IDs of parcel, doc, and geometry | `["SYN-PARCEL-000001", ...]` |
| `expected_outcome` | string | No | Ground truth benchmark outcome | `MATCH` |
| `expected_reason_codes` | json/list | No | Standardized failure/match codes | `["CONSISTENT_ACROSS_REGISTERS"]` |
| `expected_rule_ids` | json/list | No | Rules expected to trigger | `["RULE-REG-1908-SEC17", ...]` |
| `review_required` | boolean | No | Whether human officer review is required | `false` |
| `ground_truth_confidence`| float | No | Benchmark label confidence | `0.99` |
| `split_group_id` | string | No | Leakage control group identifier | `GRP-00001` |
| `generator_version` | string | No | Generator pipeline version | `1.0.0` |
| `seed_reference` | integer | No | PRNG generation seed | `42` |

---

## 10. `validation_findings`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `finding_id` | string | No | Primary key for finding | `SYN-FIND-000001` |
| `case_id` | string | No | Foreign key to `validation_cases` | `SYN-CASE-000001` |
| `field_name` | string | No | Evaluated attribute name | `overall` |
| `source_value` | string | No | Raw submitted value | `Document Value` |
| `comparison_value` | string | No | Authority reference value | `Authority Value` |
| `normalized_source_value`| string | No | Normalized submitted value | `Norm Doc` |
| `normalized_comparison_value`| string | No | Normalized reference value | `Norm Auth` |
| `rule_id` | string | No | Foreign key to `rule_catalogue` | `RULE-REG-1908-SEC17` |
| `finding_status` | string | No | Neutral finding classification | `CONSISTENT` |
| `severity` | string | No | Discrepancy severity level | `NONE` |
| `explanation` | string | No | Explainable statutory reasoning | `Document fields match revenue records.` |
| `review_required` | boolean | No | Whether this finding triggers review | `false` |

---

## 11. `audit_events`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `audit_event_id` | string | No | Immutable audit log primary key | `SYN-AUDIT-000001` |
| `actor_id` | string | No | Synthetic user ID performing action | `SYN-USER-OFFICER-001` |
| `actor_role` | string | No | Role RBAC category | `revenue_officer` |
| `action_type` | string | No | Administrative action taken | `CASE_REVIEW` |
| `resource_type` | string | No | Type of resource affected | `validation_case` |
| `resource_id` | string | No | ID of resource affected | `SYN-CASE-000001` |
| `event_timestamp` | string | No | ISO 8601 UTC timestamp | `2024-04-15T10:30:00Z` |
| `reason` | string | No | Administrative justification | `Revenue officer inspected discrepancy.` |
| `result` | string | No | Outcome of action | `REVIEW_REQUIRED` |
| `synthetic_event_flag` | boolean | No | Strict synthetic flag | `true` |

---

## 12. `rule_catalogue`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `rule_id` | string | No | Unique rule identifier | `RULE-REG-1908-SEC17` |
| `title` | string | No | Human-readable title of provision | `Compulsory Registration of Instruments` |
| `jurisdiction` | string | No | Statutory jurisdiction | `IN_CENTRAL` |
| `instrument_type` | string | No | Instrument type (CENTRAL_ACT, etc.) | `CENTRAL_ACT` |
| `official_source_url` | string | No | Authoritative legislative repository | `https://www.indiacode.nic.in/...` |
| `provision_reference` | string | No | Specific section or clause citation | `Section 17(1)(b)` |
| `short_neutral_summary`| string | No | Neutral summary of requirement | `Conveyance of immovable property >= Rs 100...` |
| `applicable_workflow` | string | No | Revenue workflow category | `CONVEYANCE_REGISTRATION` |
| `effective_from` | string | No | Statute commencement date | `1909-01-01` |
| `effective_until` | string | Yes | Date repealed or amended | `None` |
| `source_last_verified_at`| string | No | Date verified against official source | `2026-09-15` |
| `amendment_status` | string | No | Legislative status | `CURRENT` |
| `verification_status` | string | No | Degree of primary source verification | `VERIFIED_PRIMARY_SOURCE` |
| `reviewer_notes` | string | No | Legal research analyst notes | `Verified against India Code text.` |
| `limitations` | string | No | Territorial and statutory scope bounds | `Does not apply to testamentary wills.` |
| `dataset_scenarios_using_rule`| json/list| No| Scenarios evaluating this rule | `["FULL_MATCH", "OWNER_NAME_MISMATCH"]` |
| `rule_category` | string | No | Rule category (A, B, C, D) | `A_VERIFIED_PROCEDURAL_MANDATE` |

---

## 13. `provenance`

| Column | Type | Nullable | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `provenance_id` | string | No | Primary key for provenance | `SYN-PROV-000001` |
| `source_type` | string | No | Nature of generation pipeline | `DETERMINISTIC_SYNTHETIC_GENERATOR` |
| `source_reference` | string | No | Software package version | `landsync_datasets v1.0.0` |
| `generation_method` | string | No | Sampling technique applied | `PSEUDO_RANDOM_STRATIFIED_SAMPLING` |
| `generator_version` | string | No | Generator semantic version | `1.0.0` |
| `generation_seed` | integer | No | PRNG generation seed | `42` |
| `transformation_history`| string | No | High-level data transformations applied| `SI unit conversion; GeoJSON EPSG:4326...` |
| `creation_timestamp` | string | No | Release build timestamp | `2026-10-09T00:00:00Z` |
| `license_reference` | string | No | Governing public license | `CC-BY-4.0 (Dataset) / MIT (Code)` |
| `synthetic_status` | string | No | Conspicuous synthetic declaration | `100% SYNTHETIC DATA — NOT AN OFFICIAL...` |
