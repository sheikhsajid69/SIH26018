# LANDSYNC AI — Production & Demonstration Readiness Checklist

> **SIH Problem Statement**: SIH26018 — Intelligent Land Record Digitization and Validation System  
> **Team**: Void  
> **Evaluation Milestone**: Final Working System & Public Repository Deployment  

---

## 1. Persistence & Database Verification

- [x] **SQLAlchemy 2.x Engine**: Configured with connection pooling and dynamic driver resolution (`postgresql+psycopg://` / `sqlite:///`).
- [x] **Alembic Migrations**: Initial migration `859e7fd7d564_initial_schema.py` generated and applied.
- [x] **ORM Schema**: 10 distinct entities modeled (`users`, `land_parcels`, `ownership_relationships`, `mutation_events`, `documents`, `extractions`, `extracted_fields`, `validation_results`, `review_cases`, `audit_events`).
- [x] **Composite Indexes**: Added for high-throughput queries (`survey_number + village`, `status + priority`, `entity_type + entity_id`).
- [x] **Deterministic Seeder**: `scripts/seed_demo.py` idempotently populates all 14 synthetic scenarios from `data/synthetic/`.
- [x] **PostGIS Integration**: Spatial geometry stored in GeoJSON format; PostGIS extension initialized on PostgreSQL.

---

## 2. Storage & Evidence Security

- [x] **Pluggable Storage Provider**: Implemented `EvidenceStorageProvider` protocol with `LocalEvidenceStorage` and `S3EvidenceStorage`.
- [x] **Deterministic Key Schema**: `documents/{tenant}/{parcel_id}/{sha256}/{version}/{filename}`.
- [x] **WORM Anti-Tamper Defense**: Raises `StorageTamperError` if existing key is overwritten with differing SHA-256 digest.
- [x] **Path Traversal Protection**: Enforced boundary resolution against storage root; blocks `../../` attacks.
- [x] **Presigned URLs**: S3 provider issues short-lived presigned URLs for authorized evidence viewing.

---

## 3. Document Extraction & OCR Pipeline

- [x] **Pluggable Document Provider**: Implemented `DocumentProvider` protocol.
- [x] **MockDocumentProvider**: Deterministic mock matching 14 synthetic scenarios for reliable offline demonstration.
- [x] **TextAndPdfDocumentProvider**: Native PDF parser using `pypdf` with heuristic regex NER for Indian land records.
- [x] **Explainable Output**: Returns `field_name`, `extracted_value`, `confidence`, and `source_location`.
- [x] **Rule 13 Unit Normalization**: Converts standard units to square meters; preserves formula; flags ambiguous regional units (*bigha*, *katha*).

---

## 4. Consistency Validation & Human Review Engine

- [x] **Rule 2 Authoritative Primacy**: Authoritative records are treated as ground truth; document values are evaluated against them.
- [x] **Rule 8 Human-in-the-Loop**: Discrepancies (`MISMATCH`, `REVIEW_REQUIRED`) automatically halt automated processing and route to review queue.
- [x] **Dynamic Case Provisioning**: Review cases are dynamically generated and persisted in the database with reason, priority, and discrepancy deltas.
- [x] **Rule 11 Officer Adjudication**: Strictly limits decision recording to `Role.OFFICER`.
- [x] **Immutable Audit Logging**: Every upload, analysis, and officer determination creates an append-only audit event.

---

## 5. GIS & Spatial Cadastre Engine

- [x] **Rule 14 Explicit CRS**: All spatial operations explicitly declare `EPSG:4326 (WGS84)`.
- [x] **Geodesic Polygon Area**: Metric Shoelace projection calculates parcel area in square meters.
- [x] **IoU Metric**: Bounding box and polygon Intersection over Union (IoU) scores computed.
- [x] **Centroid Offset**: Calculates metric distance variance between submitted deed sketch and authoritative boundary.
- [x] **Advisory Disclaimer**: All spatial outputs declare that mathematical comparison does not establish title.

---

## 6. Authentication, RBAC & Observability

- [x] **Multi-Mode Auth**: Supports both static demo Bearer tokens (`demo-citizen`, `demo-officer`, `demo-admin`) and cryptographic JWT tokens.
- [x] **Bcrypt Password Security**: Direct bcrypt hashing for user credentials in the database.
- [x] **Role-Based Protection**: Endpoint decorators enforce role privileges (Citizen, Officer, Admin).
- [x] **Observability Headers**: Middleware injects `X-Request-ID` and `X-Response-Time-Ms` on all HTTP responses.
- [x] **Probes**: `/health/live` and `/health/ready` implemented for Kubernetes and PaaS readiness.

---

## 7. Frontend User Experience

- [x] **Institutional DPI Aesthetic**: Clean, professional government portal UI (NIC / Digital India palette).
- [x] **Dynamic Role Switcher**: Instant switching between Landowner (Citizen), Revenue Officer, and System Administrator.
- [x] **14 Synthetic Scenarios**: Interactive selector demonstrating full consistency, area mismatch, holder variance, split parcel, and boundary dispute.
- [x] **Interactive GIS Viewer**: SVG cadastral map with toggleable layers (Cadastral Cadastre, Deed Sketch, CAD Blueprint).
- [x] **Digital Land Profile Report**: Modal and print-friendly comprehensive report generation.
- [x] **Clear Error Banners**: Prominent connection status and retryable error banners if API is unreachable.
- [x] **Zero Build Errors**: Next.js production build (`npm run build`) compiles cleanly with 0 TypeScript/ESLint errors.

---

## 8. Continuous Integration & Deployment

- [x] **Docker Compose**: Orchestrates PostgreSQL + PostGIS, FastAPI, and Next.js services.
- [x] **Cloud Port Binding**: FastAPI Dockerfile uses dynamic `${PORT:-8000}` for Render compatibility.
- [x] **GitHub Actions CI**: Automated workflow runs migrations, seed script, 23 pytest tests, and Next.js build.
- [x] **100% Passing Tests**: All 23 backend test suites passing without regression.
