# LANDSYNC AI — Synthetic Demo Dataset
**Identifier**: `LANDSYNC-SYNTHETIC-SEED-V1`  
**Notice**: SYNTHETIC DEMO DATA — NOT A REAL GOVERNMENT RECORD — FOR LANDSYNC AI PROTOTYPE ONLY

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
