# LANDSYNC AI — Security & Trust Architecture

> **SIH Problem Statement**: SIH26018 — Intelligent Land Record Digitization and Validation System  
> **Team**: Void  
> **Classification**: Educational & Hackathon Evaluation Platform  

---

## 1. Core Security Principles

LANDSYNC AI is designed following defense-in-depth principles for public sector digital public infrastructure (DPI):

1. **Synthetic Data Isolation**: Zero citizen personally identifiable information (PII). All records, ULPINs, survey numbers, coordinates, and identities are 100% synthetically generated for demonstration.
2. **Authoritative Primacy (Rule 2)**: Authoritative state land records are the supreme single source of truth. AI extractions from uploaded deeds are treated as untrusted claims until validated against the authoritative register.
3. **Content-Addressed Immutability (Rule 5)**: All evidence files are stored using SHA-256 content addressing. Modification of an existing record raises an unrecoverable `StorageTamperError`.
4. **Mandatory Human-in-the-Loop (Rule 8 & 11)**: Automated systems never make title adjudications. Any variance or low-confidence extraction automatically halts and routes to an authorized revenue officer.

---

## 2. Authentication & Access Control (RBAC)

The platform enforces strict role-based access control across all endpoints:

```
┌───────────────────┬─────────────────────────────────────────────────────────────┐
│ Role              │ Permitted Actions                                           │
├───────────────────┼─────────────────────────────────────────────────────────────┤
│ Citizen / Owner   │ - Search parcels & view Digital Land Profiles               │
│                   │ - Ingest sale deeds & view automated consistency checks     │
│                   │ - Upload preliminary boundary sketches for CAD analysis     │
├───────────────────┼─────────────────────────────────────────────────────────────┤
│ Revenue Officer   │ - Access officer review queue of flagged discrepancies      │
│                   │ - Inspect evidence dossiers and discrepancy deltas          │
│                   │ - Adjudicate review cases (Accepted / Requires Doc / Reject)│
│                   │ - Inspect immutable audit log                               │
├───────────────────┼─────────────────────────────────────────────────────────────┤
│ Administrator     │ - Inspect operational health & sub-system telemetry         │
│                   │ - Monitor state adapters and storage quotas                 │
│                   │ - System audit log oversight                                │
└───────────────────┴─────────────────────────────────────────────────────────────┘
```

### Authentication Modes
- **Demo Mode**: Static Bearer tokens (`demo-citizen`, `demo-officer`, `demo-admin`) for automated testing and SIH jury evaluation without credentials setup.
- **Production Mode**: Cryptographically signed HS256 JWT access tokens with short-lived expiration (default 120 minutes) and bcrypt password hashing.

---

## 3. Storage Integrity & Anti-Tamper Protections

Evidence files are stored with strict Write-Once-Read-Many (WORM) semantics:

- **Path Traversal Defense**: All storage keys are resolved against the absolute root directory. Keys attempting directory escape (`../../`) are blocked and raise `StorageTraversalError`.
- **WORM Verification**: If an upload attempts to overwrite an existing storage key with differing bytes, the storage engine rejects the operation with `StorageTamperError`.
- **Presigned URLs**: When operating with S3, files are accessed via time-limited (3600s) presigned URLs, avoiding public bucket permissions.

---

## 4. Explainable AI & Transparency

In compliance with public administrative law:
- Every extracted field reports exact `page_number`, `source_location`, and `confidence` score (0.0 to 1.0).
- Normalization operations (such as converting acres to square meters) retain the explicit mathematical formula and original units in the response.
- Ambiguous regional land units (e.g. *bigha*, *katha*, *guntha*) are flagged for human officer calibration rather than silently guessed.

---

## 5. Vulnerability Disclosure

To report security vulnerabilities or concerns regarding this repository:
- **Email**: [security-demo@landsync.gov.in](mailto:security-demo@landsync.gov.in) (demo address) or open a GitHub Security Advisory.
- **Scope**: LANDSYNC AI backend, frontend, API contracts, and container configurations.
