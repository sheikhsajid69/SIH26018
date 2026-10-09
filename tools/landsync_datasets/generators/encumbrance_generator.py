"""
Synthetic Encumbrance and Interest Generator.
Produces 1,500+ records for mortgages, easements, statutory charges, and acquisition notices.
"""

from __future__ import annotations

import random
from typing import Any

from landsync_datasets.primitives.identifiers import encumbrance_id

INTEREST_TYPES = [
    "MORTGAGE_SIMPLE",
    "MORTGAGE_EQUITABLE",
    "EASEMENT_RIGHT_OF_WAY",
    "STATUTORY_CHARGE",
    "ACQUISITION_NOTICE",
]

INTEREST_STATUSES = ["ACTIVE", "ACTIVE", "DISCHARGED", "UNCERTAIN"]


def generate_encumbrances(
    parcels: list[dict[str, Any]],
    documents: list[dict[str, Any]],
    target_count: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    """
    Generates encumbrances and interest records.
    """
    encumbrances: list[dict[str, Any]] = []
    num_parcels = len(parcels)
    num_docs = len(documents)

    for seq in range(1, target_count + 1):
        iid = encumbrance_id(seq)
        parcel = parcels[(seq - 1) % num_parcels]
        pid = parcel["parcel_id"]
        doc = documents[(seq - 1) % num_docs]
        did = doc["document_id"]

        itype = INTEREST_TYPES[(seq - 1) % len(INTEREST_TYPES)]
        status = INTEREST_STATUSES[(seq - 1) % len(INTEREST_STATUSES)]

        year = 2018 + (seq % 6)
        eff_from = f"{year:04d}-03-15"
        eff_until = f"{year + 3:04d}-03-15" if status == "DISCHARGED" else None

        note = f"Synthetic {itype.lower().replace('_', ' ')} recorded under TPA Sec 58/100 or Easements Act."
        if itype == "ACQUISITION_NOTICE":
            note = "Preliminary notification under RFCTLARR Act 2013 Section 11."

        enc_row = {
            "interest_id": iid,
            "parcel_id": pid,
            "interest_type": itype,
            "source_document_id": did,
            "effective_from": eff_from,
            "effective_until": eff_until,
            "status": status,
            "source_verification_status": "REGISTERED_CHARGE",
            "benchmark_note": note,
        }
        encumbrances.append(enc_row)

    return encumbrances
