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

## Conventions

API paths use `/api/v1`; request/response contracts use Pydantic; timestamps are UTC; GeoJSON is EPSG:4326 unless explicitly labelled otherwise; audit is append-only; storage paths are system-generated; configuration comes from environment. Source hierarchy: authorized record, authorized GIS, digitized official evidence, AI extraction, user input.

## Completed Milestones

- Phase 0 inventory: repository was empty, with Node/npm and Python available but no Docker binary detected and no existing implementation.
- Phase 1 first vertical slice: FastAPI provider/adapter/storage/validation/RBAC foundation, tests, synthetic authority data, migration contract, and responsive Next.js dashboard are complete. The UI uploads to the API and records officer decisions; unavailable API calls fall back only to a clearly labelled local demo state.

## Limitations, Questions, Debt, and Rejected Alternatives

No real OCR, CV, government connector, persistent ORM, malware scanner, signed URLs, queue, migration runner, or MapLibre tile service is included. No geographic/legal claim may be inferred from the demo parcel. Confirm selected target state(s), legal authorization, retention policy, OIDC provider, source schema, CRS, data residency, and human-review policy before production. Rejected: hard-coding a state schema, calling demo data authoritative, using Aadhaar as a key, and allowing AI to approve title.

## Next Work

Add migration execution and SQLModel repository, explicit user-to-parcel authorization, production-grade auth/storage/scanning, controlled OCR/blueprint provider evaluation, PostGIS geometry checks, reports, queue/observability, and regional-language testing.
