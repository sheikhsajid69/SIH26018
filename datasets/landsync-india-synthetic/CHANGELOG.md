# Changelog — LANDSYNC-India Synthetic Benchmark

All notable changes to the LANDSYNC-India Synthetic Benchmark dataset releases are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-10-09

### Added
- **Initial Public Benchmark Release** for SIH26018 (Smart India Hackathon).
- Generated **10,000 synthetic land parcels** with fictional ULPIN tokens (`SYN-ULPIN-KA-xxxxxx`), survey numbers, extent, and land classifications.
- Generated **10,000 fictional party personas** with parentage honorifics, transliteration variants, and synthetic benchmark tokens.
- Generated **11,250 relationally linked ownership claims** modeling sole khatedars and co-parcenary joint holdings.
- Generated **5,500 document metadata records** and **33,000 fine-grained document field annotations** in CSV, Parquet, and JSONL formats with simulated OCR bounding boxes and noise tags.
- Generated **3,500 mutation event histories** adhering to Section 128/129 KLRA statutory reporting and notice workflows.
- Generated **1,500 encumbrance and interest records** (simple mortgages, easements, statutory charges, acquisition notices).
- Generated **5,500 spatial features** in EPSG:4326 GeoJSON and Parquet with geodesic metric areas and perimeters.
- Generated **2,880 stratified validation benchmark cases** across 34 scenario families (exceeding the 1,500 case minimum requirement).
- Included **530 compound and adversarial test cases** covering multi-variable discrepancies.
- Added **17 authoritative legal reference entries** in `rule_catalogue` with India Code citations and four-tier categorization.
- Created **group-aware leakage-safe splits**: Train (2,015 cases / 70.0%), Validation (430 cases / 14.9%), Test (435 cases / 15.1%).
- Automated **18 data quality gates** and privacy scanner certifying 0 real PII leaks and 0 split leakage.
- Self-contained Getting Started Jupyter Notebook in `notebooks/01_getting_started_landsync_synthetic.ipynb`.
- Exported JSON Schema definitions (Draft 2020-12) for all 13 dataset entities.
