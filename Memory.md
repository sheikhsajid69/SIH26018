# Architectural Memory

## Vision and Terminology

LANDSYNC AI is an AI-assisted land-record intelligence, consistency-validation, and interoperability layer. A **parcel** is identified by ULPIN/parcel/survey/plot data; a **person** is a separate authenticated actor. **Authoritative** means an authorized source, never a user upload or model output. **Review required** means a human authority must decide.

## Decisions

| Decision | Why | Consequence |
| --- | --- | --- |
| Start with an in-memory synthetic vertical slice | The initial repository was empty and has no authorized connector or supplied records. | Demo works locally; process restart clears demo activity. |
| State adapter boundary | Indian schemas differ and live integrations need authorization. | `DemoAuthorityAdapter` is the only current synthetic source. |
| Deterministic mock document provider | Allows repeatable tests and visible model provenance without representing real OCR capability. | Replace through provider boundary after evaluation. |
| Content-hash local store | Preserves evidence without trusting filename paths. | Production replaces it with versioned S3-compatible object storage. |
| PostGIS migration is included before persistence adapter | Geometry needs a durable production contract. | API will adopt SQLAlchemy/SQLModel after migration runner and connection policy are added. |
| Static demo bearer tokens | Allows the required demo roles without pretending to provide production authentication. | Replace with OIDC/JWT adapter before deployment. |
| Unit normalization & Rule 13 defense | Land units (acres, ha, cents, gunthas, bighas) must be mathematically auditable; regional variations cannot be guessed. | Ambiguous units trigger `REVIEW_REQUIRED`; formula and original unit are always preserved. |
| Blueprint CV provider boundary | Land deed sketches contain boundary lines and dimensions that need advisory edge detection. | `MockBlueprintProvider` models preliminary dimension extraction without claiming certified surveyor authority. |
| Interactive multi-layer Cadastral GIS | Visualizing spatial discrepancy (0.09 acre delta) requires comparing authoritative PostGIS polygon with deed claim and blueprint overlay. | SVG/GeoJSON layer toggles allow judges/officers to see spatial boundary variance immediately. |
| Role-based UI switcher | SIH demonstration must showcase Citizen, Revenue Officer, and Administrator journeys seamlessly. | Header role switcher alters API bearer tokens and exposes respective role dashboards. |

## Conventions

API paths use `/api/v1`; request/response contracts use Pydantic; timestamps are UTC; GeoJSON is EPSG:4326 unless explicitly labelled otherwise; audit is append-only; storage paths are system-generated; configuration comes from environment. Source hierarchy: authorized record, authorized GIS, digitized official evidence, AI extraction, user input.

## Completed Milestones

- Phase 0 inventory: repository layout, docs, runtime scripts.
- Phase 1 architecture & domain: Core typed Pydantic models for `LandParcel`, `OwnershipRelationship`, `MutationEvent`, `ConsistencyReport`, `Document`, `ValidationResult`, `ReviewCase`, and `AuditEvent`.
- Phase 2 database & PostGIS: Migration contract `001_initial.sql` defining spatial parcel geometry, evidence vault, and audit trail tables.
- Phase 3 authentication & RBAC: Token-based role authorization (`demo-citizen`, `demo-officer`, `demo-admin`), strict endpoint guards, citizen decision block.
- Phase 4 upload/storage: SHA-256 content-addressing, directory traversal defenses, immutable file storage in `.landsync-storage`.
- Phase 5 & 6 document intelligence & blueprint: Swappable `MockDocumentProvider` (OCR/NER) and `MockBlueprintProvider` (sketch dimension & edge detection) with advisory disclaimers.
- Phase 7 & 8 normalization & validation: Strict Indian unit engine (`units.py`), ambiguous unit defense (Rule 13), multi-field comparison (`MATCH`, `PARTIAL_MATCH`, `MISMATCH`, `MISSING`, `REVIEW_REQUIRED`), confidence weighting.
- Phase 9, 10 & Admin dashboards: Next.js responsive interface with interactive role switcher, Discrepancy Queue, case resolution controls, and System Admin health console.
- Phase 11 GIS spatial intelligence: Multi-layer Cadastral GIS visualizer with EPSG:4326 coordinates, scale bar, North arrow, and boundary delta overlay.
- Phase 12 & 13 provenance, history & reports: Mutation timeline (`/parcels/{id}/history`), SHA-256 evidence tracking, printable Advisory Consistency Report modal.
- Phase 16 automated testing: 15 automated test suites spanning unit normalizations, validation logic, RBAC security, upload integrity, and API contracts.

## Limitations, Questions, Debt, and Rejected Alternatives

No real OCR, CV, live government connector, persistent ORM, malware scanner, signed URLs, queue, or MapLibre vector tile server is included. No geographic/legal claim may be inferred from the demo parcel. Confirm selected target state(s), legal authorization, retention policy, OIDC provider, source schema, CRS, data residency, and human-review policy before production. Rejected: hard-coding a state schema, calling demo data authoritative, using Aadhaar as a key, and allowing AI to approve title.

## Next Work

Add migration runner execution and SQLModel repository, production-grade auth (Keycloak/OIDC), virus/malware scanning, real PaddleOCR/Tesseract evaluation, and multi-state adapter pilots.
