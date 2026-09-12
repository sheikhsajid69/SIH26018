# Delivery Phases

| Phase | Objective / key tasks | Dependencies / files | Completion checks |
| --- | --- | --- | --- |
| 0 Repository initialization | root layout, environment, docs | root files | inventory and runnable commands recorded |
| 1 Architecture + domain | contracts and source hierarchy | docs, `landsync/models.py` | terminology/rules reviewed |
| 2 Database + PostGIS | migrations and geometry indexes | `infra/migrations` | migration applies to PostGIS |
| 3 Authentication + RBAC | auth adapter and permissions | API | role tests pass |
| 4 Upload/storage | validate, hash, version evidence | services | invalid upload rejected; hash retained |
| 5 OCR/extraction | provider contract and fixtures | document providers | extraction provenance shown |
| 6 Blueprint intelligence | calibrated boundary/dimension provider | service + fixtures | geometry uncertainty shown |
| 7 Normalization/identity | ULPIN/survey/units rules | core + adapters | ambiguous units require review |
| 8 Validation engine | field comparisons and thresholds | validation | mismatch test passes |
| 9 Citizen dashboard | upload, profile, status | web | keyboard-visible flow works |
| 10 Officer dashboard | decision, notes, queue | web/API | officer-only decision test |
| 11 GIS | MapLibre/Leaflet and geometry validation | web/PostGIS | parcel geometry renders |
| 12 Provenance/history | audit and versions | API/DB | append-only event shown |
| 13 Reports | advisory downloadable report | API | disclaimer is present |
| 14 Mock adapter | seeded controlled source | adapters/data | visibly synthetic |
| 15 Demo data | repeatable seed/reset | data | seed idempotence |
| 16 Testing | API, validation, UI checks | tests | CI commands green |
| 17 Security | scanning, threat review, rate limits | infra/API | security checklist signed |
| 18 Docker/deploy | images, health, migration job | compose/infra | fresh deploy works |
| 19 Performance | profiling and indexes | all | targets documented |
| 20 SIH demo | rehearsed scripts and recovery | docs | full demo acceptance passes |

For every phase: complete dependencies before merging, update affected docs, add relevant tests, run the defined checks, and record the completion decision in `Memory.md`.
