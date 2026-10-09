# LANDSYNC-India: Synthetic Cadastral & Land Record Benchmark (Release v1.0.0)

> **CONSPICUOUS LEGAL NOTICE:**  
> **100% SYNTHETIC DATA — NOT AN OFFICIAL LAND RECORD.**  
> All natural persons, land parcels, survey numbers, deeds, boundary coordinates, encumbrances, and revenue entries contained herein are mathematically generated synthetic fixtures. This dataset does not represent actual citizens, real-world land parcels, authentic government records, or title adjudications. Never query or submit these fictional tokens against real-world government registries.

---

## 1. Overview & Problem Context

The **LANDSYNC-India Synthetic Benchmark** is a reproducible, legally informed, and mathematically consistent dataset engineered for evaluating automated land-record digitization, Document AI extraction, entity resolution, and cadastral boundary validation systems in India.

- **Project**: LANDSYNC AI
- **Problem Statement**: SIH26018 — *Intelligent Land Record Digitization and Validation System* (Smart India Hackathon)
- **Repository**: [https://github.com/sheikhsajid69/SIH26018](https://github.com/sheikhsajid69/SIH26018)
- **Primary Distribution**: Kaggle Datasets (`sheikhsajid69/landsync-india-synthetic`)
- **Version**: 1.0.0
- **License**: Creative Commons Attribution 4.0 International (CC-BY-4.0)

Indian land administration presents unique data challenges: multi-lingual deed formats, varied regional area metrics, historical manual mutations, complex coparcenary inheritance rights, and subtle spatial boundary discrepancies between survey blueprints and digital GIS vectors. Real land records contain sensitive private citizen information, making public benchmark sharing impossible without severe privacy risks. This dataset solves that bottleneck by providing a realistic, comprehensive, and privacy-safe synthetic collection.

---

## 2. Benchmark Composition & Table Summary

| Table / Entity | File Formats | Records | Primary Key | Description |
| :--- | :--- | :---: | :--- | :--- |
| **`parcels`** | CSV, Parquet | 10,000 | `parcel_id` | Core synthetic land parcels with ULPIN tokens, extent, and land class |
| **`parties`** | CSV, Parquet | 10,000 | `party_id` | Fictional landowner personas with aliases and synthetic benchmark ID tokens |
| **`ownership_claims`** | CSV, Parquet | 11,250 | `claim_id` | Relational ownership rights, sole titles, and fractional co-parcenary shares |
| **`documents`** | CSV, Parquet | 5,500 | `document_id` | Registered deeds, RTC extracts, blueprints, and SHA-256 evidence digests |
| **`document_fields`** | CSV, Parquet, JSONL | 33,000 | `field_id` | Fine-grained OCR/NER field annotations with pixel bounding boxes and noise tags |
| **`mutation_events`** | CSV, Parquet | 3,500 | `mutation_event_id` | Revenue transfer timelines under Section 128/129 KLRA statutory notice rules |
| **`encumbrances`** | CSV, Parquet | 1,500 | `interest_id` | Mortgages (TPA Sec 58), charges (Sec 100), easements, and statutory notices |
| **`spatial_features`** | GeoJSON, CSV, Parquet | 5,500 | `geometry_id` | Geodesic cadastral parcel polygons (EPSG:4326) with metric areas and perimeters |
| **`validation_cases`** | CSV, Parquet | 2,880 | `case_id` | Stratified ground-truth benchmark cases covering 34 scenario families |
| **`validation_findings`**| CSV, Parquet | 2,880 | `finding_id` | Explainable statutory findings with severity and rule citations |
| **`audit_events`** | CSV, Parquet | 4,000 | `audit_event_id` | Immutable administrative audit trails tracking officer and citizen actions |
| **`rule_catalogue`** | CSV, Parquet | 17 | `rule_id` | Authoritative legal reference register distinguishing mandates from heuristics |
| **`provenance`** | CSV, Parquet | 1 | `provenance_id` | Complete lineage, generation seed, and licensing declaration |

---

## 3. Directory Layout

```text
datasets/landsync-india-synthetic/
├── README.md                           # This documentation guide
├── LICENSE                             # CC-BY-4.0 Public License
├── CITATION.cff                        # Machine-readable academic citation
├── DATA_CARD.md                        # Formal HuggingFace / Kaggle dataset card
├── DATA_DICTIONARY.md                  # Comprehensive column data dictionary
├── LEGAL_SCOPE.md                      # Legal research register and statutory scope
├── GENERATION_METHODOLOGY.md           # Algorithmic generation methodology
├── QUALITY_ASSURANCE.md                # 18 automated quality gates & test reports
├── PRIVACY_AND_SYNTHETIC_DATA.md       # Privacy audit and zero-PII certification
├── CHANGELOG.md                        # Version release history
├── dataset-metadata.json               # Kaggle dataset publishing descriptor
├── manifest.json                       # SHA-256 integrity manifest for all 44 files
├── data/                               # CSV and Parquet primary dataset tables
│   ├── parcels.csv / .parquet
│   ├── parties.csv / .parquet
│   ├── ownership_claims.csv / .parquet
│   ├── documents.csv / .parquet
│   ├── document_fields.csv / .parquet
│   ├── mutation_events.csv / .parquet
│   ├── encumbrances.csv / .parquet
│   ├── spatial_features.csv / .parquet / .geojson
│   ├── validation_cases.csv / .parquet
│   ├── validation_findings.csv / .parquet
│   ├── audit_events.csv / .parquet
│   ├── rule_catalogue.csv / .parquet
│   └── provenance.csv / .parquet
├── annotations/
│   └── document_field_annotations.jsonl # JSONL OCR & Document AI annotations
├── schemas/                            # 13 JSON Schema (Draft 2020-12) contracts
│   ├── parcel.schema.json
│   ├── document.schema.json
│   └── ...
├── splits/                             # Group-aware leakage-safe splits
│   ├── train_ids.csv                   # 2,015 training cases (70.0%)
│   ├── validation_ids.csv              # 430 validation cases (14.9%)
│   └── test_ids.csv                    # 435 test evaluation cases (15.1%)
├── reports/
│   └── quality_report.json             # Automated QA execution report (18/18 PASS)
└── notebooks/
    └── 01_getting_started_landsync_synthetic.ipynb
```

---

## 4. Key Benchmark Tasks & Supported Use Cases

1. **Document AI & Field Extraction**: Evaluate OCR / LayoutLM models on deed metadata, survey schedules, and extents across clean, faint, and noisy simulated document scans.
2. **Entity Resolution & Name Matching**: Resolve variations in Indian personal names across honorary prefixes (`Shri`, `S/o`, `W/o`), reverse ordering (`Surname Given`), and regional transliterations.
3. **Record Consistency Validation**: Test rule engines for detecting discrepancies in extents, survey hissas, and land-use categories between deeds and government extracts.
4. **Cadastral Geospatial Validation**: Compute Intersection-over-Union (IoU), geodesic metric areas, ring topology, and centroid offsets between deed sketches and GIS polygons.
5. **Mutation Chronology Verification**: Audit historical title chains to detect backdated instruments or mutations unapproved during statutory 30-day notice windows.
6. **Rule 13 Ambiguous Unit Defense**: Detect and protect regional variable land units (e.g. *bigha*, *biswa*, *katha*) from unsafe automated conversions.

---

## 5. Quick Start (Python)

```python
import pandas as pd
import json

# 1. Load benchmark validation cases
cases = pd.read_csv("data/validation_cases.csv")
print(f"Total Validation Cases: {len(cases)}")
print("Class Distribution:\n", cases["expected_outcome"].value_counts())

# 2. Inspect an adversarial case
sample = cases[cases["difficulty"] == "ADVERSARIAL"].iloc[0]
print("\nSample Adversarial Case:", sample["case_id"], sample["scenario_family"])
print("Expected Outcome:", sample["expected_outcome"])

# 3. Load spatial GeoJSON
with open("data/spatial_features.geojson") as f:
    geojson_data = json.load(f)
print(f"Loaded {len(geojson_data['features'])} cadastral parcel polygons in EPSG:4326.")
```

---

## 6. Synthetic Data & Ethical Integrity Policy

This dataset is released under a strict **Zero-PII synthetic mandate**:
- No real Aadhaar numbers, PAN numbers, or government credentials exist in any row.
- All personal names are fictional combinations generated from regional statistical frequency lists.
- Geographic coordinates are confined to a fictional study envelope and do not correspond to authentic private properties.
- All identifiers are explicitly prefixed with `SYN-` (e.g., `SYN-PARCEL-`, `SYN-ULPIN-KA-`, `SYN-ID-BENCHMARK-`).
