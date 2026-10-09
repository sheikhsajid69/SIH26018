"""
Synthetic Administrative Audit Event Generator.
Produces 4,000+ append-only immutable audit trail events.
"""

from __future__ import annotations

import random
from typing import Any

from landsync_datasets.primitives.identifiers import audit_event_id

ACTORS = [
    ("SYN-USER-CITIZEN-001", "citizen"),
    ("SYN-USER-OFFICER-001", "revenue_officer"),
    ("SYN-USER-ADMIN-001", "administrator"),
    ("SYSTEM-VALIDATION-ENGINE", "system_engine"),
]

ACTIONS = [
    ("DOCUMENT_INGEST", "document", "Citizen evidence upload and SHA-256 vault ingest", "SUCCESS"),
    ("VALIDATION_RUN", "validation_case", "Automated multi-field statutory comparison pipeline", "SUCCESS"),
    ("CASE_REVIEW", "validation_case", "Revenue officer inspected cadastral discrepancy", "REVIEW_REQUIRED"),
    ("DECISION_RECORDED", "validation_case", "Officer adjudication recorded in case log", "SUCCESS"),
    ("MUTATION_AUDIT", "mutation", "Review of mutation notice period under Sec 129 KLRA", "SUCCESS"),
]


def generate_audit_events(
    parcels: list[dict[str, Any]],
    validation_cases: list[dict[str, Any]],
    target_count: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    """
    Generates append-only synthetic audit trail events.
    """
    events: list[dict[str, Any]] = []
    num_parcels = len(parcels)
    num_cases = len(validation_cases)

    for seq in range(1, target_count + 1):
        aid = audit_event_id(seq)
        actor_id, actor_role = ACTORS[seq % len(ACTORS)]
        act_type, res_type, reason, result = ACTIONS[seq % len(ACTIONS)]

        if res_type == "parcel":
            res_id = parcels[(seq - 1) % num_parcels]["parcel_id"]
        elif res_type == "validation_case" and num_cases > 0:
            res_id = validation_cases[(seq - 1) % num_cases]["case_id"]
        else:
            res_id = f"SYN-RES-{seq:06d}"

        year = 2024
        month = (seq % 12) + 1
        day = (seq % 28) + 1
        hour = seq % 24
        minute = seq % 60
        ts = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00Z"

        audit_row = {
            "audit_event_id": aid,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "action_type": act_type,
            "resource_type": res_type,
            "resource_id": res_id,
            "event_timestamp": ts,
            "reason": reason,
            "result": result,
            "synthetic_event_flag": True,
        }
        events.append(audit_row)

    return events
