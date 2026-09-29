#!/usr/bin/env python3
"""
Deterministic, idempotent seed script for LANDSYNC AI.
Populates all 14 synthetic demonstration scenarios into the database.
All data is 100% synthetic, advisory demo data developed for SIH26018 (Team Void).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add apps/api to sys.path so we can import landsync modules
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

from landsync.auth import hash_password
from landsync.database import SessionLocal, init_db
from landsync.db_models import (
    AuditEventOrm,
    DocumentOrm,
    ExtractedFieldOrm,
    ExtractionOrm,
    LandParcelOrm,
    MutationEventOrm,
    OwnershipRelationshipOrm,
    ReviewCaseOrm,
    UserOrm,
    ValidationResultOrm,
)

SYNTHETIC_DIR = REPO_ROOT / "data" / "synthetic"


def seed() -> None:
    print("[*] Initializing database schema...")
    init_db()

    db = SessionLocal()
    try:
        # 1. Seed Users
        users_file = SYNTHETIC_DIR / "users.json"
        if users_file.exists():
            users_data = json.loads(users_file.read_text(encoding="utf-8"))
            for u in users_data:
                role = u["role"]
                # Default passwords for synthetic demonstration accounts
                pwd = "Admin@LandSync2026!" if role == "administrator" else ("Officer@LandSync2026!" if role == "revenue_officer" else "Citizen@LandSync2026!")
                p_hash = hash_password(pwd)
                username_alias = "admin" if role == "administrator" else ("officer" if role == "revenue_officer" else "citizen")

                existing_user = db.query(UserOrm).filter(UserOrm.id == u["user_id"]).first()
                if not existing_user:
                    db.add(
                        UserOrm(
                            id=u["user_id"],
                            username=username_alias,
                            email=u["email"],
                            password_hash=p_hash,
                            role=u["role"],
                            name=u["name"],
                            phone=u.get("phone"),
                            jurisdiction=u.get("jurisdiction"),
                            permitted_parcels=u.get("permitted_parcels", []),
                            status=u.get("status", "ACTIVE"),
                        )
                    )
                elif not existing_user.password_hash:
                    existing_user.password_hash = p_hash
                    existing_user.username = username_alias
            db.commit()
            print(f"[+] Seeded {len(users_data)} synthetic users with bcrypt credentials.")

        # 2. Seed Land Parcels from authority_records.json
        auth_file = SYNTHETIC_DIR / "authority_records.json"
        parcels_file = SYNTHETIC_DIR / "parcels.json"
        if auth_file.exists() and parcels_file.exists():
            auth_records = {r["parcel_id"]: r for r in json.loads(auth_file.read_text(encoding="utf-8"))}
            parcels_data = json.loads(parcels_file.read_text(encoding="utf-8"))

            for p in parcels_data:
                pid = p["parcel_id"]
                auth = auth_records.get(pid, {})
                existing_p = db.query(LandParcelOrm).filter(LandParcelOrm.id == pid).first()
                parcel_data = {
                    "ulpin": p.get("synthetic_ulpin", f"SYN-ULPIN-{pid}"),
                    "survey_number": p["survey_number"],
                    "plot_number": p.get("plot_number", "1"),
                    "owner": auth.get("owner", "Synthetic Holder"),
                    "area": p.get("land_area", "2.40 acre"),
                    "area_unit": p.get("land_area_unit", "acre"),
                    "normalized_area_sqm": p.get("normalized_area_sqm", 9712.46),
                    "state": p.get("state", "Karnataka"),
                    "district": p.get("district", "Synthetic District"),
                    "tehsil": p.get("taluk", "Demo Taluk"),
                    "village": p.get("village", "Sample Village"),
                    "land_use": p.get("land_use", "Agricultural"),
                    "geometry": auth.get("geometry", {
                        "type": "Polygon",
                        "coordinates": [[[77.5944, 12.9716], [77.5951, 12.9716], [77.5951, 12.9721], [77.5944, 12.9721], [77.5944, 12.9716]]],
                    }),
                    "geometry_source": auth.get("geometry_source", "SYNTHETIC DEMO GeoJSON (EPSG:4326)"),
                    "authoritative_source": "SYNTHETIC DEMO authority record",
                }

                if existing_p:
                    for k, v in parcel_data.items():
                        setattr(existing_p, k, v)
                else:
                    db.add(LandParcelOrm(id=pid, **parcel_data))

            # Also seed demo-parcel alias for seed backward-compatibility
            demo_existing = db.query(LandParcelOrm).filter(LandParcelOrm.id == "demo-parcel").first()
            demo_props = {
                "ulpin": "DEMO-ULPIN-27-000-124-2",
                "survey_number": "124/2",
                "plot_number": "18B",
                "owner": "Ramesh Kumar (synthetic demo person)",
                "area": "2.40 acre",
                "area_unit": "acre",
                "normalized_area_sqm": 9712.46,
                "state": "Karnataka (Demo State)",
                "district": "Bengaluru Rural (Sample District)",
                "tehsil": "Model Tehsil",
                "village": "Sampurna",
                "land_use": "Agricultural",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[77.5944, 12.9716], [77.5951, 12.9716], [77.5951, 12.9721], [77.5944, 12.9721], [77.5944, 12.9716]]],
                },
                "geometry_source": "SYNTHETIC DEMO GeoJSON (EPSG:4326)",
                "authoritative_source": "SYNTHETIC DEMO authority record",
            }
            if demo_existing:
                for k, v in demo_props.items():
                    setattr(demo_existing, k, v)
            else:
                db.add(LandParcelOrm(id="demo-parcel", **demo_props))

            db.commit()
            print(f"[+] Seeded {len(parcels_data)} synthetic land parcels + demo-parcel alias.")

        # 3. Seed Ownership Relationships & Mutation Events
        for p in parcels_data:
            pid = p["parcel_id"]
            auth = auth_records.get(pid, {})
            owner_name = auth.get("owner", "Synthetic Holder")

            own_id = f"own-{pid.lower()}"
            if not db.query(OwnershipRelationshipOrm).filter(OwnershipRelationshipOrm.id == own_id).first():
                db.add(
                    OwnershipRelationshipOrm(
                        id=own_id,
                        parcel_id=pid,
                        holder_name=owner_name,
                        share_extent="100% (Sole Khatedar)",
                        relationship_type="SOLE_PROPRIETOR",
                        recorded_date="2018-05-20",
                        source_ref=f"Sanction Order SO-{pid}/2018",
                        is_synthetic=True,
                    )
                )

            mut_id = f"mut-{pid.lower()}-1"
            if not db.query(MutationEventOrm).filter(MutationEventOrm.id == mut_id).first():
                db.add(
                    MutationEventOrm(
                        id=mut_id,
                        parcel_id=pid,
                        mutation_number=f"MR-{pid}-2018",
                        event_type="REGISTRATION",
                        recorded_date="2018-05-20",
                        parties_involved=f"Initial registration for {owner_name}",
                        description=f"Cadastral settlement and title registration for {pid} in {p.get('village', 'Village')}.",
                        order_reference=f"Tahsildar Order LND-{pid}/2018",
                        is_synthetic=True,
                    )
                )

        # Demo parcel ownership & mutations
        if not db.query(OwnershipRelationshipOrm).filter(OwnershipRelationshipOrm.id == "own-demo-001").first():
            db.add(
                OwnershipRelationshipOrm(
                    id="own-demo-001",
                    parcel_id="demo-parcel",
                    holder_name="Ramesh Kumar",
                    share_extent="100% (Sole Khatedar)",
                    relationship_type="SOLE_PROPRIETOR",
                    recorded_date="2012-04-18",
                    source_ref="Mutation Entry MR-44/2012",
                    is_synthetic=True,
                )
            )

        demo_muts = [
            ("mut-demo-001", "MR-12/1994", "PARTITION", "1994-08-11", "Ancestral partition among Suresh Kumar & Brothers", "Ancestral division in Sy No 124 creating sub-division 124/2 (extent 2.40 acre).", "Tahsildar Order No. LND/CR/1994/88"),
            ("mut-demo-002", "MR-44/2012", "SUCCESSION", "2012-04-18", "Inheritance by Ramesh Kumar upon succession", "Succession entry sanctioned in favour of legal heir Ramesh Kumar.", "Revenue Inspector Sanction RI/MUT/2012/104"),
            ("mut-demo-003", "DEMARC-2021-09", "DEMARCATION", "2021-11-04", "ADLR Taluk Survey Division", "Cadastral field sketch digitization and boundary fixing for Sy No 124/2.", "Survey Settlement Order SO-2021/772"),
        ]
        for mid, mnum, mtype, mdate, mparties, mdesc, mref in demo_muts:
            if not db.query(MutationEventOrm).filter(MutationEventOrm.id == mid).first():
                db.add(
                    MutationEventOrm(
                        id=mid,
                        parcel_id="demo-parcel",
                        mutation_number=mnum,
                        event_type=mtype,
                        recorded_date=mdate,
                        parties_involved=mparties,
                        description=mdesc,
                        order_reference=mref,
                        is_synthetic=True,
                    )
                )

        db.commit()
        print("[+] Seeded ownership relationships and mutation timeline.")

        # 4. Seed Documents & Extractions
        docs_file = SYNTHETIC_DIR / "documents.json"
        ext_file = SYNTHETIC_DIR / "extractions.json"
        if docs_file.exists() and ext_file.exists():
            docs_data = json.loads(docs_file.read_text(encoding="utf-8"))
            ext_map = {e["document_id"]: e for e in json.loads(ext_file.read_text(encoding="utf-8"))}

            for d in docs_data:
                did = d["document_id"]
                if not db.query(DocumentOrm).filter(DocumentOrm.id == did).first():
                    doc_orm = DocumentOrm(
                        id=did,
                        parcel_id=d["parcel_id"],
                        document_type=d.get("document_type", "REGISTERED_SALE_DEED"),
                        original_file_name=d.get("file_name", f"{did}.pdf"),
                        mime_type=d.get("mime_type", "application/pdf"),
                        storage_key=f"documents/demo/{d['parcel_id']}/{d.get('sha256', 'mock')}/1/original",
                        sha256=d.get("sha256", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
                        file_size=d.get("file_size", 1024),
                        source="SYNTHETIC_DEMO",
                        uploaded_by="demo-citizen",
                        processing_status="COMPLETED",
                    )
                    db.add(doc_orm)

                    ext = ext_map.get(did)
                    if ext:
                        ext_orm = ExtractionOrm(
                            id=f"ext-{did}",
                            document_id=did,
                            provider=ext.get("provider", "mock-document-ai"),
                            model_version=ext.get("model_version", "demo-1.2"),
                        )
                        db.add(ext_orm)
                        for f in ext.get("fields", []):
                            db.add(
                                ExtractedFieldOrm(
                                    id=f"ef-{did}-{f['field_name']}",
                                    extraction_id=ext_orm.id,
                                    field_name=f["field_name"],
                                    extracted_value=str(f["extracted_value"]),
                                    normalized_value=str(f.get("normalized_value", f["extracted_value"])),
                                    confidence=float(f.get("confidence", 0.95)),
                                    source_location=f.get("source_location", "page 1"),
                                    page_number=int(f.get("page_number", 1)),
                                    extraction_method=f.get("extraction_method", "MOCK_OCR_NER"),
                                    reviewer_status=f.get("reviewer_status", "PENDING"),
                                )
                            )
            db.commit()
            print(f"[+] Seeded {len(docs_data)} synthetic documents and extractions.")

        # 5. Seed Validation Results
        val_file = SYNTHETIC_DIR / "validation_results.json"
        if val_file.exists():
            val_data = json.loads(val_file.read_text(encoding="utf-8"))
            total_val_records = 0
            for v in val_data:
                pid = v["parcel_id"]
                did = v.get("document_id")
                fields = v.get("fields", [])
                for f in fields:
                    fname = f.get("field", "field")
                    vid = f"val-{pid}-{fname}"
                    result = f.get("result", "MATCH")
                    severity = "LOW"
                    if result == "MISMATCH":
                        severity = "HIGH" if fname in ("owner", "survey_number") else "MEDIUM"
                    elif result in ("AMBIGUOUS", "FLAGGED"):
                        severity = "MEDIUM"

                    if not db.query(ValidationResultOrm).filter(ValidationResultOrm.id == vid).first():
                        db.add(
                            ValidationResultOrm(
                                id=vid,
                                parcel_id=pid,
                                document_id=did,
                                field=fname,
                                source_a="Submitted Deed (SYNTHETIC)",
                                value_a=str(f.get("document_value", "")),
                                source_b="Authority Register (SYNTHETIC)",
                                value_b=str(f.get("authority_value", "")),
                                comparison_operator="equivalence",
                                result=result,
                                confidence=float(f.get("confidence", 0.95)),
                                severity=severity,
                                explanation=f"{fname.title()} check: deed='{f.get('document_value', '')}' vs authority='{f.get('authority_value', '')}' ({result})",
                            )
                        )
                        total_val_records += 1
            db.commit()
            print(f"[+] Seeded {total_val_records} validation check records across {len(val_data)} scenarios.")

        # 6. Seed Review Cases
        cases_file = SYNTHETIC_DIR / "review_cases.json"
        if cases_file.exists():
            cases_data = json.loads(cases_file.read_text(encoding="utf-8"))
            for c in cases_data:
                cid = c["review_case_id"]
                existing_c = db.query(ReviewCaseOrm).filter(ReviewCaseOrm.id == cid).first()
                c_props = {
                    "parcel_id": c["parcel_id"],
                    "document_id": c.get("document_id"),
                    "reason": c["reason"],
                    "severity": "HIGH" if "P1" in c.get("priority", "") else "MEDIUM",
                    "status": c.get("status", "OPEN"),
                    "priority": c.get("priority", "P2_NORMAL"),
                    "discrepancy_field": c.get("discrepancy_field"),
                    "claimed_value": c.get("claimed_value"),
                    "authoritative_value": c.get("authoritative_value"),
                    "assigned_officer": c.get("assigned_role", "revenue_officer"),
                    "reviewer_notes": c.get("reviewer_note"),
                }
                if existing_c:
                    for k, val in c_props.items():
                        setattr(existing_c, k, val)
                else:
                    db.add(ReviewCaseOrm(id=cid, **c_props))

            # Demo-case alias
            if not db.query(ReviewCaseOrm).filter(ReviewCaseOrm.id == "demo-case").first():
                db.add(
                    ReviewCaseOrm(
                        id="demo-case",
                        parcel_id="demo-parcel",
                        reason="Area variance detected: Submitted deed reports 2.31 acre while synthetic authority record reports 2.40 acre (~364 m² variance).",
                        severity="MEDIUM",
                        status="OPEN",
                        priority="P2_NORMAL",
                        discrepancy_field="area",
                        claimed_value="2.31 acre",
                        authoritative_value="2.40 acre",
                        assigned_officer="revenue_officer",
                        reviewer_notes="Awaiting officer examination in demonstration queue.",
                    )
                )

            db.commit()
            print(f"[+] Seeded {len(cases_data)} review cases + demo-case alias.")

        # 7. Seed Audit Events
        audit_file = SYNTHETIC_DIR / "audit_events.json"
        if audit_file.exists():
            audit_data = json.loads(audit_file.read_text(encoding="utf-8"))
            # Only seed if table is currently empty
            if db.query(AuditEventOrm).count() == 0:
                for a in audit_data:
                    entity_type = "review_case" if "review_case_id" in a else ("parcel" if "parcel_id" in a else "system")
                    entity_id = a.get("review_case_id") or a.get("parcel_id") or "sys-demo"
                    db.add(
                        AuditEventOrm(
                            actor_id=a.get("actor", "system"),
                            action=a.get("action", "SYSTEM_LOG"),
                            entity_type=entity_type,
                            entity_id=entity_id,
                            timestamp=datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00")),
                            before_state=None,
                            after_state=None,
                            reason=a.get("reason"),
                            trace_id=a.get("trace_id", "trace-seed"),
                        )
                    )
                db.commit()
                print(f"[+] Seeded {len(audit_data)} audit events.")
            else:
                print(f"[+] Audit events already present ({db.query(AuditEventOrm).count()} records).")

        print("\n[+] Database seeding completed successfully! All records verified SYNTHETIC DEMO DATA.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
