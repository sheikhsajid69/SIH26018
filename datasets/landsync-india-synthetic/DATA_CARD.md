# Dataset Card for LANDSYNC-India Synthetic Benchmark

## Dataset Description

- **Repository**: [sheikhsajid69/SIH26018](https://github.com/sheikhsajid69/SIH26018)
- **Paper / Technical Spec**: LANDSYNC AI Product Requirements & Architecture Specifications
- **Point of Contact**: Sajid Sheikh (`sajid@example.invalid`)
- **License**: Creative Commons Attribution 4.0 International (`CC-BY-4.0`)
- **Version**: `1.0.0`
- **Release Date**: October 9, 2026

### Dataset Summary

The **LANDSYNC-India Synthetic Benchmark** is a specialized benchmark dataset designed to evaluate machine learning, document AI, and rule-based validation systems operating on Indian land records. It models the intricate legal, clerical, typographical, and geospatial patterns found in Indian revenue administration across 10,000 linked parcels, 5,500 documents, 33,000 field annotations, 3,500 mutation events, 5,500 cadastral spatial polygons, and 2,880 stratified ground-truth validation cases.

**Primary Notice:** 100% SYNTHETIC DATA — NOT AN OFFICIAL GOVERNMENT RECORD.

### Supported Tasks and Leaderboards

1. **Record Consistency Validation (`MATCH`, `PARTIAL_MATCH`, `MISMATCH`, `MISSING`, `REVIEW_REQUIRED`)**:
   Binary and multi-class classification determining whether submitted document evidence agrees with authoritative revenue records.
2. **Document Information Extraction (NER / LayoutLM)**:
   Extracting structured fields (`owner`, `survey_number`, `hissa`, `area`, `village`, `date`) from simulated text deeds.
3. **Entity Resolution / Party Linking**:
   Clustering and resolving variant name representations, patronymics, and honorific aliases.
4. **Cadastral Boundary IoU Evaluation**:
   Spatial overlap, centroid offset, and area variance evaluation between submitted survey sketches and cadastral GIS layers.
5. **Human Review Escalation Routing**:
   Predicting when discrepancies mandate review by a human revenue officer under administrative governance policies.

### Languages

- English (primary administrative vocabulary for deeds and RTC extracts)
- Transliterated Kannada / Indian revenue terminology (RTC, Pahani, Tippani, Akarband, Khatedar, Hissa, Kushki, Tari, Bagayat)

---

## Dataset Structure

### Data Instances

Each validation case (`SYN-CASE-xxxxxx`) links:
- A primary parcel (`SYN-PARCEL-xxxxxx`)
- Associated title documents (`SYN-DOC-xxxxxx`)
- Document field annotations (`SYN-FIELD-xxxxxx`)
- Cadastral polygon geometry (`SYN-GEOM-xxxxxx`)
- Expected outcome label (`MATCH`, `PARTIAL_MATCH`, `MISMATCH`, `MISSING`, `REVIEW_REQUIRED`)
- Associated legal rule references (e.g. `RULE-TPA-1882-SEC54`, `RULE-AREA-TOL-001`)
- Explainable statutory findings (`SYN-FIND-xxxxxx`)

### Data Splits

The benchmark uses a **group-aware split strategy** (`split_group_id`) ensuring that all documents, claims, and findings for a given parcel lineage are isolated within a single split:

| Split | Case Count | Ratio | Parcels | Leaked IDs |
| :--- | :---: | :---: | :---: | :---: |
| **Train** | 2,015 | 70.0% | Isolated | 0 |
| **Validation** | 430 | 14.9% | Isolated | 0 |
| **Test** | 435 | 15.1% | Isolated | 0 |
| **Total** | 2,880 | 100.0% | 10,000 | 0 |

---

## Dataset Creation

### Curation Rationale

Real Indian land records contain private biometric, demographic, and financial data belonging to living citizens. Public sharing of real disputed property dossiers presents severe legal and privacy hazards under the Digital Personal Data Protection Act, 2023. This synthetic benchmark was created to enable transparent, open-source scientific evaluation of land-record intelligence systems without compromising citizen privacy.

### Synthetic Data Policy

1. **No Real PII**: All names, telephone numbers, emails, and address strings are generated algorithmically.
2. **No Real Government Credentials**: Fictional ULPIN identifiers use the `SYN-ULPIN-` prefix. Real 12-digit Aadhaar patterns and 10-character PAN patterns are prohibited by automated regex quality gates.
3. **Controlled Coordinate Envelope**: All cadastral geometries are located within a fictionalized study envelope in Karnataka and do not correspond to authentic private parcel boundaries.

---

## Considerations for Using the Data

### Known Limitations

1. **State Law Specificity**: The pilot profile models Karnataka revenue administration rules (Karnataka Land Revenue Act 1964, Karnataka Land Reforms Act 1961). It does not reflect state-specific land revenue codes of Uttar Pradesh, Maharashtra, West Bengal, or Tamil Nadu.
2. **Simulated Document Text**: Documents are synthetic text representations rather than high-resolution physical scans of aged paper.
3. **Advisory Nature**: Predictions made by models trained on this benchmark must be presented to users as advisory AI guidance, never as legally binding title certifications.
