"""
Synthetic Parcel Generator.
Produces 10,000+ relational parcel records conforming to the Parcel schema.
"""

from __future__ import annotations

import random
from typing import Any

from landsync_datasets.primitives.identifiers import (
    parcel_id,
    synthetic_ulpin,
    geometry_id,
    provenance_id,
)
from landsync_datasets.normalization.area import normalize_area


LAND_CLASSIFICATIONS = [
    "Agricultural Dry (Kushki)",
    "Agricultural Wet (Tari)",
    "Garden / Plantation (Bagayat)",
    "Converted Residential",
    "Commercial Layout",
    "Industrial Plot",
]

AREA_PRESETS = [
    (0.75, "acre"),
    (1.20, "acre"),
    (1.50, "acre"),
    (2.00, "acre"),
    (2.40, "acre"),
    (2.50, "acre"),
    (3.10, "acre"),
    (4.25, "acre"),
    (30.0, "guntha"),
    (50.0, "cent"),
    (100.0, "cent"),
    (4046.85, "sqm"),
]


def generate_parcels(
    target_count: int,
    profile: dict[str, Any],
    rng: random.Random,
    prov_id: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Generates target_count synthetic parcel records.
    Returns (parcels_list, parcel_lookup_by_id).
    """
    parcels: list[dict[str, Any]] = []
    lookup: dict[str, Any] = {}

    state_code = profile.get("state_code", "KA")
    jur_id = profile.get("profile_id", "KA_PILOT")
    villages = profile.get("villages", [])

    for seq in range(1, target_count + 1):
        pid = parcel_id(seq)
        ulpin_val = synthetic_ulpin(state_code, seq)
        vil = villages[(seq - 1) % len(villages)]

        survey_num = str(100 + (seq // 10))
        subdiv_num = str((seq % 8) + 1)
        plot_num = f"{((seq % 50) + 1)}{chr(65 + (seq % 4))}"

        # Select area
        base_val, base_unit = AREA_PRESETS[seq % len(AREA_PRESETS)]
        # For a small subset of parcels (e.g. sequence modulo 120 == 0), inject ambiguous regional unit bigha for Rule 13 test cases
        if seq % 120 == 0:
            area_val, area_unit = 2.5, "bigha"
        else:
            area_val, area_unit = base_val, base_unit

        norm_result = normalize_area(area_val, area_unit)
        norm_sqm = norm_result.normalized_value_sqm or 0.0

        p_type = "RURAL_AGRICULTURAL" if "Agricultural" in vil["village_name"] or seq % 4 != 0 else "URBAN_DEVELOPED"
        land_class = LAND_CLASSIFICATIONS[seq % len(LAND_CLASSIFICATIONS)]

        year = 2018 + (seq % 7)
        month = (seq % 12) + 1
        day = (seq % 28) + 1
        eff_date = f"{year:04d}-{month:02d}-{day:02d}"

        geom_id = geometry_id(seq)
        source_rec_id = f"SYN-ROR-EXTRACT-{seq:06d}"

        parcel_row = {
            "parcel_id": pid,
            "synthetic_record_flag": True,
            "jurisdiction_id": jur_id,
            "village_code": vil["village_code"],
            "village_name": vil["village_name"],
            "survey_number": survey_num,
            "subdivision_number": subdiv_num,
            "plot_number": plot_num,
            "parcel_type": p_type,
            "land_classification": land_class,
            "area_value": area_val,
            "area_unit": area_unit,
            "area_square_metres": norm_sqm,
            "area_normalization_method": norm_result.conversion_rule,
            "boundary_geometry_id": geom_id,
            "source_record_id": source_rec_id,
            "record_effective_date": eff_date,
            "record_status": "ACTIVE",
            "provenance_id": prov_id,
            "ulpin": ulpin_val,
        }

        parcels.append(parcel_row)
        lookup[pid] = parcel_row

    return parcels, lookup
