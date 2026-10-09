"""
Synthetic Party Generator.
Generates fictional landowner personas strictly adhering to the 100% Synthetic Data Policy.
"""

from __future__ import annotations

import random
from typing import Any

from landsync_datasets.primitives.names import generate_synthetic_name
from landsync_datasets.primitives.identifiers import (
    party_id,
    synthetic_identity_reference,
)


def generate_parties(
    target_count: int,
    rng: random.Random,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Generates target_count synthetic parties.
    Returns (party_list, party_lookup_by_id).
    """
    parties: list[dict[str, Any]] = []
    lookup: dict[str, Any] = {}

    for seq in range(1, target_count + 1):
        pid = party_id(seq)
        name_info = generate_synthetic_name(rng)

        party_type = "INDIVIDUAL"
        if seq % 25 == 0:
            party_type = "JOINT_FAMILY"
        elif seq % 80 == 0:
            party_type = "CORPORATE_ENTITY"

        id_ref_val = synthetic_identity_reference(seq)

        party_row = {
            "party_id": pid,
            "synthetic_record_flag": True,
            "synthetic_display_name": name_info["display_name"],
            "party_type": party_type,
            "name_language": "en",
            "name_variants": name_info["variants"],
            "identity_reference_type": "SYNTHETIC_BENCHMARK_TOKEN",
            "identity_reference_value": id_ref_val,
            "identity_reference_is_synthetic": True,
            "consent_or_authority_status": "SYNTHETIC_CONSENT_VERIFIED",
        }

        parties.append(party_row)
        lookup[pid] = party_row

    return parties, lookup
