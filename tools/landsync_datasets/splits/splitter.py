"""
Group-aware dataset splitting and data-leakage auditing.
Strictly enforces Section 15: Entity grouping guarantees that all records belonging
to the same parcel family, document lineage, or scenario cluster remain in a single split.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any
import random


def split_validation_cases_by_group(
    cases: list[dict[str, Any]],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Splits validation cases into train, val, and test using group_id to prevent leakage.
    """
    rng = random.Random(seed)

    # Group cases by split_group_id
    group_map: dict[str, list[dict[str, Any]]] = {}
    for c in cases:
        grp = c.get("split_group_id", "DEFAULT_GROUP")
        group_map.setdefault(grp, []).append(c)

    unique_groups = sorted(list(group_map.keys()))
    rng.shuffle(unique_groups)

    n_groups = len(unique_groups)
    n_train = int(n_groups * train_ratio)
    n_val = int(n_groups * val_ratio)

    train_groups = set(unique_groups[:n_train])
    val_groups = set(unique_groups[n_train: n_train + n_val])
    test_groups = set(unique_groups[n_train + n_val:])

    train_cases = []
    val_cases = []
    test_cases = []

    for grp, grp_cases in group_map.items():
        if grp in train_groups:
            train_cases.extend(grp_cases)
        elif grp in val_groups:
            val_cases.extend(grp_cases)
        else:
            test_cases.extend(grp_cases)

    return train_cases, val_cases, test_cases


def verify_split_leakage(
    train_cases: list[dict[str, Any]],
    val_cases: list[dict[str, Any]],
    test_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Checks for any case_id, primary_parcel_id, or split_group_id leakage across splits.
    """
    train_ids = {c["case_id"] for c in train_cases}
    val_ids = {c["case_id"] for c in val_cases}
    test_ids = {c["case_id"] for c in test_cases}

    train_parcels = {c["primary_parcel_id"] for c in train_cases}
    val_parcels = {c["primary_parcel_id"] for c in val_cases}
    test_parcels = {c["primary_parcel_id"] for c in test_cases}

    train_groups = {c["split_group_id"] for c in train_cases}
    val_groups = {c["split_group_id"] for c in val_cases}
    test_groups = {c["split_group_id"] for c in test_cases}

    case_overlap_tv = train_ids.intersection(val_ids)
    case_overlap_tt = train_ids.intersection(test_ids)
    case_overlap_vt = val_ids.intersection(test_ids)

    parcel_overlap_tv = train_parcels.intersection(val_parcels)
    parcel_overlap_tt = train_parcels.intersection(test_parcels)
    parcel_overlap_vt = val_parcels.intersection(test_parcels)

    group_overlap_tv = train_groups.intersection(val_groups)
    group_overlap_tt = train_groups.intersection(test_groups)
    group_overlap_vt = val_groups.intersection(test_groups)

    has_leakage = (
        bool(case_overlap_tv)
        or bool(case_overlap_tt)
        or bool(case_overlap_vt)
        or bool(parcel_overlap_tv)
        or bool(parcel_overlap_tt)
        or bool(parcel_overlap_vt)
        or bool(group_overlap_tv)
        or bool(group_overlap_tt)
        or bool(group_overlap_vt)
    )

    def dist(cs: list[dict[str, Any]]) -> dict[str, int]:
        d: dict[str, int] = {}
        for c in cs:
            outcome = str(c.get("expected_outcome", ""))
            d[outcome] = d.get(outcome, 0) + 1
        return d

    return {
        "status": "PASS" if not has_leakage else "FAIL",
        "has_leakage": has_leakage,
        "train_count": len(train_cases),
        "validation_count": len(val_cases),
        "test_count": len(test_cases),
        "train_class_distribution": dist(train_cases),
        "validation_class_distribution": dist(val_cases),
        "test_class_distribution": dist(test_cases),
        "leakage_counts": {
            "case_id_overlap_train_val": len(case_overlap_tv),
            "case_id_overlap_train_test": len(case_overlap_tt),
            "case_id_overlap_val_test": len(case_overlap_vt),
            "parcel_overlap_train_val": len(parcel_overlap_tv),
            "parcel_overlap_train_test": len(parcel_overlap_tt),
            "parcel_overlap_val_test": len(parcel_overlap_vt),
            "group_overlap_train_val": len(group_overlap_tv),
            "group_overlap_train_test": len(group_overlap_tt),
            "group_overlap_val_test": len(group_overlap_vt),
        },
    }


def write_split_csvs(
    splits_dir: Path,
    train_cases: list[dict[str, Any]],
    val_cases: list[dict[str, Any]],
    test_cases: list[dict[str, Any]],
) -> None:
    splits_dir.mkdir(parents=True, exist_ok=True)

    for filename, case_list in [
        ("train_ids.csv", train_cases),
        ("validation_ids.csv", val_cases),
        ("test_ids.csv", test_cases),
    ]:
        filepath = splits_dir / filename
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["case_id", "primary_parcel_id", "split_group_id", "scenario_family", "expected_outcome", "difficulty"])
            for c in case_list:
                writer.writerow([
                    c.get("case_id", ""),
                    c.get("primary_parcel_id", ""),
                    c.get("split_group_id", ""),
                    c.get("scenario_family", ""),
                    c.get("expected_outcome", ""),
                    c.get("difficulty", ""),
                ])
