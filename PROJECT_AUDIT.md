# LANDSYNC AI — Comprehensive Repository & Architecture Audit

**Project:** LANDSYNC AI (Intelligent Land Record Digitalisation, Validation and Spatial Intelligence Platform)  
**Smart India Hackathon:** SIH26018 — Smart Automation  
**Team:** Void  
**Audit Timestamp:** September 2026  
**Auditor Role:** Principal Software Architect & Full-Stack Systems Engineer  

---

## 1. Current Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Layer (Next.js 15 App Router)"]
        UI[Interactive Dashboard<br/>apps/web/src/app/page.tsx]
        Scenarios[Synthetic Scenarios Engine<br/>14 Demonstration Cases]
        GISPlot[SVG Cadastral GIS Component<br/>Authority + Deed + CV Blueprint Layers]
    end

    subgraph Server["API & Intelligence Layer (FastAPI)"]
        Routes[API Routing & RBAC Auth<br/>apps/api/landsync/main.py]
        Services[Services & Validation Engine<br/>apps/api/landsync/services.py]
        Units[Regional Land Units & Rule 13<br/>apps/api/landsync/units.py]
        Blueprint[Mock Blueprint CV Provider<br/>apps/api/landsync/blueprint.py]
        Adapter[Demo State Authority Adapter<br/>apps/api/landsync/adapters/state/demo.py]
    end

    subgraph Persistence["Current Runtime State vs Intended Storage"]
        InMemoryState["In-Memory Python Structures<br/>(audit: list, documents: list, review_cases: dict)"]
        LocalDisk[".landsync-storage/<br/>SHA-256 Content-Addressed Files"]
        Postgres[(Intended: PostgreSQL 16 + PostGIS<br/>infra/migrations/001_initial.sql — NOT WIRED)]
    end

    UI -->|HTTP / JSON (Bearer Token)| Routes
    Routes --> Services
    Services --> Units
    Routes --> Blueprint
    Routes --> Adapter
    Routes -->|Read / Mutate| InMemoryState
    Services -->|write_bytes| LocalDisk
    Server -.->|Intended Future Wire| Postgres
```

### Architectural Assessment
The repository possesses a well-thought-out domain model, a robust Indian regional land unit conversion engine adhering to Rule 13, and a structured multi-layer SVG Cadastral GIS visualizer. However, the system currently operates primarily **in-memory**:
- Document uploads, review decisions, and audit events are stored in global Python lists and dictionaries (`audit: list[AuditEvent]`, `documents: list[Document]`, `review_cases: dict[str, ReviewCase]`).
- PostgreSQL and PostGIS are defined in `docker-compose.yml` and `infra/migrations/001_initial.sql`, but the FastAPI application has no ORM models (SQLAlchemy/SQLModel), no database connection pool, and does not execute database queries.
- A restart of the backend wipes all uploaded documents, review case decisions, and audit trails.

---

## 2. Current Runtime Flow

1. **Client Request**:
   - The user selects a persona from the topbar (Citizen, Revenue Officer, or Administrator).
   - The client selects a synthetic scenario index (0 to 13) from `scenarios.ts`.
2. **Document Ingestion**:
   - Citizen uploads a deed file (`.pdf`, `.png`, `.jpg`, `.txt`).
   - The frontend sends `POST /api/v1/parcels/{parcel_id}/documents` with a demo bearer token (`Bearer demo-citizen`).
   - The backend computes a SHA-256 digest, writes the binary to `.landsync-storage/documents/demo/{parcel_id}/{digest}/1/original`, and stores a `Document` object in memory.
   - It invokes `MockDocumentProvider.extract()`, which returns deterministic mock field extractions.
   - It runs `validate(active_extraction, authority_record)` across 6 fields (`owner`, `survey_number`, `plot_number`, `area`, `village`, `land_use`).
   - It logs an in-memory `AuditEvent`.
   - The response returns `review_cases.get("demo-case")` (hardcoded assumption).
3. **Discrepancy Review**:
   - Officer reviews the case and submits `POST /api/v1/review-cases/{case_id}/decision` with `{ resolution, notes }`.
   - The backend mutates the in-memory `ReviewCase` object and appends an `AuditEvent`.
4. **Fallback Runtime**:
   - If the API server is unreachable, the frontend silently catches the error and creates an in-memory local fallback document or decision, masking service failure from the user.

---

## 3. Existing Frontend Features

Located in `apps/web/`:
- **Framework**: Next.js 15.2.4 (App Router), React 19, Tailwind CSS 3.4.17.
- **Design System**: MongoDB visual design tokens (`#001e2b` deep teal, `#00ed64` brand green, `#00684a` dark green, `#e3fcef` soft mint, pill buttons, 12px card borders).
- **Navigation & Layout**: Fixed sidebar with brand mark, topbar with role switcher, breadcrumb navigation, and responsive tabs (Digital Land Profile & GIS, Officer Review Queue, Mutation Timeline, Admin Health).
- **Interactive Multi-Layer Cadastral GIS**: Custom SVG renderer displaying authoritative parcel boundary, claimed deed boundary, and CV blueprint edge overlay with EPSG:4326 coordinate display, north arrow, and 25m scale indicator.
- **Dynamic Scenario Selector**: 14 distinct synthetic cases representing real-world disputes (clean match, area mismatch, spelling drift, sub-division divergence, undisclosed mortgage, eco-sensitive forest buffer, ambiguous bigha, boundary encroachment, etc.).
- **Evidence Vault**: Document list displaying SHA-256 hashes, file metadata, extraction status, and verification badges.
- **Review Console**: Officer decision interface with resolution options (`ACCEPTED_FOR_CORRECTION`, `REQUIRES_DOCUMENT`, `NO_ACTION`) and mandatory rationale input.
- **Printable Consistency Report Modal**: Institutional advisory land profile report formatted for `window.print()`.
- **SEO & Metadata**: Vector favicon (`icon.svg`), dynamic `robots.ts`, dynamic `sitemap.ts`, PWA `manifest.json`, and Schema.org JSON-LD structured data.

---

## 4. Existing Backend Endpoints

Located in `apps/api/landsync/main.py`:

| Method | Endpoint | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Public | Service health & synthetic mode status |
| `GET` | `/api/v1/auth/demo` | Public | List available demo tokens & roles |
| `GET` | `/api/v1/parcels/search` | Citizen / Officer / Admin | Keyword search across synthetic parcels |
| `GET` | `/api/v1/parcels/{id}` | Citizen / Officer / Admin | Retrieve parcel attributes & GeoJSON geometry |
| `GET` | `/api/v1/parcels/{id}/ownership` | Citizen / Officer / Admin | Retrieve ownership khatedar relationships |
| `GET` | `/api/v1/parcels/{id}/history` | Citizen / Officer / Admin | Retrieve mutation chronology |
| `POST` | `/api/v1/parcels/{id}/documents` | Citizen / Officer | Ingest deed, SHA-256 hash, run mock OCR |
| `POST` | `/api/v1/parcels/{id}/blueprint` | Citizen / Officer | Run advisory blueprint edge detection |
| `GET` | `/api/v1/parcels/{id}/validation` | Citizen / Officer / Admin | Run multi-field consistency validation |
| `GET` | `/api/v1/review-cases` | Officer / Admin | List discrepancy review queue |
| `GET` | `/api/v1/review-cases/{id}` | Officer / Admin | Retrieve single review case detail |
| `POST` | `/api/v1/review-cases/{id}/decision` | Officer only | Record adjudication decision & rationale |
| `GET` | `/api/v1/audit` | Officer / Admin | Retrieve append-only audit event stream |
| `GET` | `/api/v1/admin/health` | Admin only | Adapter health, storage metrics, queue counts |
| `GET` | `/api/v1/parcels/{id}/report` | Citizen / Officer / Admin | Generate full typed ConsistencyReport |

---

## 5. Existing Data Model

Defined with Pydantic v2 in `apps/api/landsync/models.py`:
- `Role`: Enum (`citizen`, `revenue_officer`, `administrator`).
- `ValidationState`: Enum (`MATCH`, `PARTIAL_MATCH`, `MISMATCH`, `MISSING`, `REVIEW_REQUIRED`).
- `ExtractedField`: `field_name`, `extracted_value`, `normalized_value`, `confidence`, `source_location`, `page_number`, `extraction_method`, `reviewer_status`.
- `Extraction`: `provider`, `model_version`, `created_at`, `fields`.
- `Document`: `id`, `parcel_id`, `document_type`, `original_file_name`, `mime_type`, `storage_key`, `sha256`, `file_size`, `source`, `uploaded_by`, `uploaded_at`, `version`, `processing_status`, `extraction`.
- `ValidationResult`: `field`, `source_a`, `value_a`, `source_b`, `value_b`, `comparison_operator`, `result`, `confidence`, `severity`, `explanation`, `created_at`.
- `ReviewCase`: `id`, `parcel_id`, `reason`, `severity`, `status`, `priority`, `discrepancy_field`, `claimed_value`, `authoritative_value`, `assigned_officer`, `reviewer_notes`, `resolution`, `created_at`, `resolved_at`.
- `AuditEvent`: `id`, `actor_id`, `action`, `entity_type`, `entity_id`, `timestamp`, `before_state`, `after_state`, `reason`, `trace_id`.
- `LandParcel`: `id`, `ulpin`, `survey_number`, `plot_number`, `state`, `district`, `tehsil`, `village`, `area`, `normalized_area_sqm`, `land_use`, `geometry`, `geometry_source`, `authoritative_source`.
- `OwnershipRelationship`: `id`, `parcel_id`, `holder_name`, `share_extent`, `relationship_type`, `recorded_date`, `source_ref`.
- `MutationEvent`: `id`, `parcel_id`, `mutation_number`, `event_type`, `recorded_date`, `parties_involved`, `description`, `order_reference`.
- `ConsistencyReport`: Aggregated report model binding parcel, ownership, validation results, review case, and mutation history.

---

## 6. Existing Tests

Located in `apps/api/tests/`:
- `test_services.py`:
  - Unit conversions (Acre, Hectare, Guntha, Cent to m²).
  - Rule 13 Ambiguous Unit Defense (Unambiguous vs Ambiguous Bigha detection).
  - Blueprint analysis structure and mock CV results.
  - Evidence store path-traversal prevention.
  - Multi-field validation logic (Match, Area mismatch, Holder name aliases).
  - Domain model serialization.
- `test_api.py`:
  - Health check endpoint contract.
  - Parcel retrieval and mutation history.
  - Document upload, MIME validation, and SHA-256 calculation.
  - RBAC authorization (Citizen permitted to upload, forbidden from deciding cases; Officer permitted to decide; Admin health).
  - Review case lifecycle.
  - Consistency report generation.
- **Current Test Status**: 15/15 tests passing in ~0.07s.

---

## 7. Existing Docker Setup

Defined in `docker-compose.yml`:
- `db`: `postgis/postgis:16-3.4` on port `5432:5432`.
- `migrate`: Runs `psql -f /migrations/001_initial.sql` once `db` is healthy.
- `api`: Builds `apps/api/Dockerfile`, mounts `.landsync-storage` to `/data`, exposes port `8000`.
- `web`: Builds `apps/web/Dockerfile`, exposes port `3000`.
- **Limitation**: The API service in Compose does not pass `DATABASE_URL` to FastAPI, because the API doesn't yet connect to PostgreSQL.

---

## 8. Existing Deployment Limitations

1. **Ephemeral State**: Backend relies on process memory. On Render or Docker restarts, all uploads, decisions, and audit events vanish.
2. **Hardcoded Port 8000 in Dockerfile**: Render assigns dynamic ports via `$PORT`. The Dockerfile must respect `$PORT` with `0.0.0.0`.
3. **Hardcoded CORS Origins**: `main.py` defaults to `localhost:3000`. Public deployment on custom domains or Vercel requires environment-driven allowlists.
4. **Client-Side Assumptions**: Frontend uses `http://localhost:8000` default and silently falls back to offline mock state on network errors, hiding broken backend connections.
5. **Lack of Readiness/Liveness Probes**: Only `/health` exists; there is no `/health/live` or `/health/ready` verifying database and storage connectivity.

---

## 9. Existing Security Limitations

1. **Static Demo Tokens**: Authentication uses static strings (`demo-citizen`, `demo-officer`, `demo-admin`) passed as Bearer tokens. There is no real JWT verification, expiration, or signing key for production.
2. **No Rate Limiting**: Upload and search endpoints are unthrottled.
3. **Storage Path Bound to Local Filesystem**: Documents are written to local disk (`.landsync-storage`), which is ephemeral in cloud containers (e.g., Render web services without persistent disks).
4. **Permissive Error Handling**: While stack traces are mostly suppressed, no unified structured error response standard (with error codes and request IDs) is enforced across all routes.
5. **No Request ID Tracing Middleware**: Requests lack unique incoming `X-Request-ID` correlation headers for distributed observability.

---

## 10. Missing Functionality

1. **SQLAlchemy 2.x / SQLModel Database Persistence**: Repositories connecting domain models to PostgreSQL + PostGIS tables.
2. **Alembic Database Migration Pipeline**: Versioned, forward-and-rollback database migrations replacing raw single-file execution.
3. **Deterministic Database Seeder**: `scripts/seed_demo.py` to idempotently seed all 14 scenarios into PostgreSQL.
4. **Pluggable Evidence Storage Provider**: Interface supporting both `LocalEvidenceStorage` and `S3EvidenceStorage` (AWS S3 / Cloudflare R2 / MinIO).
5. **Pluggable Document Provider Interface**: Real OCR/Text extraction fallback (`pypdf`, `tesseract`, text extractor) alongside `MockDocumentProvider`.
6. **Dynamic Review Case Provisioning**: Generating new review cases dynamically when validation mismatches occur, rather than returning static `demo-case`.
7. **Production JWT Authentication Provider**: Real password hashing, token generation, and claims validation alongside `DemoAuthProvider`.
8. **Organized Route Routers**: Splitting monolithic `main.py` into dedicated APIRouter modules (`/auth`, `/parcels`, `/documents`, `/validation`, `/review-cases`, `/audit`, `/admin`).
9. **Production Error Banner in Frontend**: Explicit error presentation when backend calls fail, disabling silent fake success when in production mode.
10. **CI/CD Pipeline**: `.github/workflows/ci.yml` validating backend tests, linting, and Next.js builds.

---

## 11. Technical Debt

1. **Monolithic API File**: `apps/api/landsync/main.py` handles auth, routing, audit logging, file uploads, and health all in one file.
2. **Schema Inconsistency**: `001_initial.sql` defines tables for `land_parcel`, `document`, and `audit_event`, but lacks tables for `ownership_relationship`, `mutation_event`, `extracted_field`, `validation_result`, and `review_case`.
3. **Hardcoded Fallback in Frontend**: `page.tsx` embeds hardcoded fallbacks for documents, audit events, and decisions, mixing demo scaffolding with production logic.
4. **Duplicate Scenario Data**: Scenario definitions exist in both `data/synthetic/` and `apps/web/src/app/scenarios.ts`.
5. **Unused Protocol Warning**: In cleanups, ensure protocols or abstract interfaces are used wherever multiple implementations (Local vs S3, Mock vs OCR) exist.

---

## 12. Recommended Implementation Order

```
[Phase 1] Persistence Layer (SQLAlchemy 2.x + PostGIS + Alembic)
    ↓
[Phase 2] Real Data Seeder (scripts/seed_demo.py — 14 Scenarios)
    ↓
[Phase 3 & 4] Storage Architecture (EvidenceStorageProvider: Local & S3)
    ↓
[Phase 5] Pluggable Document Processing (DocumentProvider: Mock + Text/OCR)
    ↓
[Phase 6 & 7] Dynamic Validation Engine & Review Case Provisioning
    ↓
[Phase 8 & 9] Real GIS Spatial Computations (PostGIS Polygon IoU)
    ↓
[Phase 10 & 11] Production Authentication & RBAC (JWT + DemoAuthProvider)
    ↓
[Phase 12] Production API Organization (APIRouter Modularization & Probes)
    ↓
[Phase 13 & 14] Frontend Hardening (Real API Driven, Explicit Error States)
    ↓
[Phase 15, 16 & 17] Security, Observability & Structured Errors
    ↓
[Phase 18, 19 & 20] Reports, Digital Land Profile & UI Verification
    ↓
[Phase 23 & 24] Comprehensive Test Suite & GitHub Actions CI
    ↓
[Phase 25, 26 & 27] Docker, Deployment Docs & Verification
```

---
*End of Audit. Proceeding immediately to Phase 1 implementation.*
