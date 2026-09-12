# Product Requirements Document

## Executive Summary, Vision, and Problem

LANDSYNC AI transforms fragmented land documents into explainable, spatially linked, reviewable digital evidence. It supports SIH26018 (Smart Automation; Team Void) as an intelligence, validation, and interoperability layer over authorized ecosystems; it never replaces them or establishes title.

## Goals and Non-Goals

Goals: accept evidence; extract structured fields; associate a parcel identity; compare it with an authorized source; show GIS geometry; expose confidence, provenance, history, and review cases. Non-goals: live government integration without authorization, ownership certification, Aadhaar-based parcel identity, automated authoritative mutations, or dispute resolution.

## Users and Journeys

Citizen/landowner uploads a document, sees advisory extraction and consistency status, then requests review. A revenue officer inspects source evidence, discrepancies, parcel geometry, and audit history before recording a review decision. An administrator manages users, adapters, validation configuration, and dataset health. A citizen cannot access another citizen’s private parcel or approve a discrepancy.

## Functional Requirements and Acceptance Criteria

| Feature | Acceptance criterion |
| --- | --- |
| Demo authentication and RBAC | Citizen upload works; only officer token can record a review decision. |
| Immutable upload | API rejects unsupported/oversize files, stores content under a SHA-256-derived key, and returns hash/provenance. |
| Document AI | Provider, version, field confidence, source location, and review state accompany every extracted field. |
| Validation | Document and source values coexist; mismatch produces `REVIEW_REQUIRED`, never overwrites the source. |
| Digital Land Profile | UI displays only source values or “Not available,” a GIS geometry, documents, validation, and provenance. |
| Human review and audit | Officer decision records a case update and audit event. |
| Report | API returns a clearly advisory, synthetic demo consistency report. |

## Core Features and Requirements

AI uses swappable OCR/layout/NLP and blueprint providers, starting with a deterministic mock provider. GIS accepts GeoJSON with CRS metadata and eventual PostGIS validation. Validation compares owner, survey/plot, area, village, boundary, location, land use, and dates using configurable thresholds; it returns MATCH, PARTIAL_MATCH, MISMATCH, MISSING, or REVIEW_REQUIRED. Land identity is ULPIN/parcel/survey/plot—not citizen authentication data.

## Non-Functional, Security, Privacy, and Audit Requirements

Typed API contracts, structured errors, request traceability, environment-driven configuration, responsive WCAG-aware UI, migration-managed storage, hash-preserved originals, role authorization, and source hierarchy are required. Aadhaar is never a URL parameter, log field, or primary identifier. Audit records preserve actor, action, before/after state, rationale, and trace ID.

## Scope, Metrics, Risks, and Roadmap

Prototype scope is the runnable synthetic first slice. Production scope adds authorized adapters, PostgreSQL/PostGIS persistence, malware scanning, queues, signed object storage, real OCR evaluation, multilingual quality tests, and legal/governance review. Success means a fresh environment completes the demo flow with visible provenance and a routed discrepancy. Risks include poor scans, false extraction, source staleness, integration authorization, and privacy exposure; human review, confidence display, and adapter isolation mitigate them. Roadmap: blueprint CV, state adapters, full history, reports, i18n, resilience, and controlled production pilots.
