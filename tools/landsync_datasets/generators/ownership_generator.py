"""
Synthetic Ownership Claim Generator.
Connects Parcels and Parties via relationally consistent ownership rights and shares.
"""

from __future__ import annotations

import random
from typing import Any

from landsync_datasets.primitives.identifiers import claim_id


def generate_ownership_claims(
    parcels: list[dict[str, Any]],
    parties: list[dict[str, Any]],
    rng: random.Random,
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    """
    Generates ownership claims linking parcels and parties.
    Returns (claims_list, claims_by_parcel_id).
    """
    claims: list[dict[str, Any]] = []
    claims_by_parcel: dict[str, list[dict[str, Any]]] = {}

    claim_seq = 1
    party_count = len(parties)

    for idx, p in enumerate(parcels):
        pid = p["parcel_id"]
        primary_party = parties[idx % party_count]
        doc_ref = f"SYN-DOC-{(idx % 5500) + 1:06d}"

        eff_date = p["record_effective_date"]

        # Check if co-ownership parcel
        is_joint = (idx % 8 == 0)

        if not is_joint:
            # Sole Khatedar
            cid = claim_id(claim_seq)
            claim_seq += 1
            claim_row = {
                "claim_id": cid,
                "parcel_id": pid,
                "party_id": primary_party["party_id"],
                "holder_name": primary_party["synthetic_display_name"],
                "claim_type": "SOLE_KHATEDAR",
                "share_numerator": 1,
                "share_denominator": 1,
                "claim_start_date": eff_date,
                "claim_end_date": None,
                "source_document_id": doc_ref,
                "source_status": "REVENUE_RECORD_OF_RIGHTS",
                "verification_status": "RECORD_VERIFIED",
                "benchmark_note": "Sole recorded title holder in village extract.",
            }
            claims.append(claim_row)
            claims_by_parcel.setdefault(pid, []).append(claim_row)
        else:
            # Co-parceners (2 parties with 1/2 share each)
            secondary_party = parties[(idx + 1) % party_count]

            # Primary co-owner
            cid1 = claim_id(claim_seq)
            claim_seq += 1
            c1 = {
                "claim_id": cid1,
                "parcel_id": pid,
                "party_id": primary_party["party_id"],
                "holder_name": primary_party["synthetic_display_name"],
                "claim_type": "CO_PARCENER",
                "share_numerator": 1,
                "share_denominator": 2,
                "claim_start_date": eff_date,
                "claim_end_date": None,
                "source_document_id": doc_ref,
                "source_status": "REVENUE_RECORD_OF_RIGHTS",
                "verification_status": "RECORD_VERIFIED",
                "benchmark_note": "Undivided 50% co-parcenary interest.",
            }
            claims.append(c1)
            claims_by_parcel.setdefault(pid, []).append(c1)

            # Secondary co-owner
            cid2 = claim_id(claim_seq)
            claim_seq += 1
            c2 = {
                "claim_id": cid2,
                "parcel_id": pid,
                "party_id": secondary_party["party_id"],
                "holder_name": secondary_party["synthetic_display_name"],
                "claim_type": "CO_PARCENER",
                "share_numerator": 1,
                "share_denominator": 2,
                "claim_start_date": eff_date,
                "claim_end_date": None,
                "source_document_id": doc_ref,
                "source_status": "REVENUE_RECORD_OF_RIGHTS",
                "verification_status": "RECORD_VERIFIED",
                "benchmark_note": "Undivided 50% co-parcenary interest.",
            }
            claims.append(c2)
            claims_by_parcel.setdefault(pid, []).append(c2)

    return claims, claims_by_parcel
