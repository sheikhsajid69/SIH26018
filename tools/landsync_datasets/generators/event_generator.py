"""
Synthetic Mutation and Transaction Event Generator.
Produces 3,500+ mutation timeline events conforming to Section 128/129 KLRA workflows.
"""

from __future__ import annotations

import random
from typing import Any

from landsync_datasets.primitives.identifiers import mutation_id

EVENT_TYPES = [
    "SALE_TRANSFER",
    "INHERITANCE_SUCCESSION",
    "PARTITION",
    "CONVERSION",
    "MORTGAGE_CHARGE",
    "RELEASE",
]

EVENT_STATUSES = ["SANCTIONED", "SANCTIONED", "SANCTIONED", "PENDING_OBJECTION", "REJECTED"]


def generate_mutation_events(
    parcels: list[dict[str, Any]],
    documents: list[dict[str, Any]],
    target_count: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    """
    Generates target_count mutation history records across parcels.
    """
    events: list[dict[str, Any]] = []
    num_parcels = len(parcels)
    num_docs = len(documents)

    for seq in range(1, target_count + 1):
        mid = mutation_id(seq)
        parcel = parcels[(seq - 1) % num_parcels]
        pid = parcel["parcel_id"]
        doc = documents[(seq - 1) % num_docs]
        did = doc["document_id"]

        etype = EVENT_TYPES[(seq - 1) % len(EVENT_TYPES)]
        status = EVENT_STATUSES[(seq - 1) % len(EVENT_STATUSES)]

        year = 2015 + (seq % 10)
        month = (seq % 12) + 1
        day = (seq % 20) + 1

        app_date = f"{year:04d}-{month:02d}-{day:02d}"
        event_date = f"{year:04d}-{month:02d}-{min(28, day + 3):02d}"

        # Standard legal sequence: application -> event deed -> 30-day notice -> effective / recorded
        # For small subset (seq % 150 == 0), inject chronology conflict (effective precedes application)
        if seq % 150 == 0:
            eff_date = f"{year - 1:04d}-{month:02d}-{day:02d}"
            expected_outcome = "CHRONOLOGY_CONFLICT"
        else:
            eff_month = min(12, month + 1)
            eff_date = f"{year:04d}-{eff_month:02d}-{day:02d}"
            expected_outcome = "MATCH" if status == "SANCTIONED" else "REVIEW_REQUIRED"

        recorded_date = eff_date

        event_row = {
            "mutation_event_id": mid,
            "parcel_id": pid,
            "event_type": etype,
            "application_date": app_date,
            "event_date": event_date,
            "effective_date": eff_date,
            "recorded_date": recorded_date,
            "source_document_id": did,
            "previous_claim_id": f"SYN-CLAIM-{(seq % 1000) + 1:06d}",
            "resulting_claim_id": f"SYN-CLAIM-{(seq % 1000) + 2:06d}",
            "event_status": status,
            "event_sequence": (seq % 3) + 1,
            "benchmark_expected_outcome": expected_outcome,
        }
        events.append(event_row)

    return events
