"""
Tests for Group-Aware Splitting and Data Leakage Auditing.
"""

from landsync_datasets.splits.splitter import (
    split_validation_cases_by_group,
    verify_split_leakage,
)


def test_group_aware_splits_have_zero_leakage():
    # Construct mock cases belonging to 20 distinct groups
    mock_cases = []
    for g in range(1, 21):
        grp_id = f"GRP-{g:05d}"
        for c in range(5):
            mock_cases.append({
                "case_id": f"SYN-CASE-{g:02d}-{c}",
                "primary_parcel_id": f"SYN-PARCEL-{g:04d}",
                "split_group_id": grp_id,
                "expected_outcome": "MATCH" if c == 0 else "MISMATCH",
            })

    train_c, val_c, test_c = split_validation_cases_by_group(
        mock_cases, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42
    )

    assert len(train_c) > 0
    assert len(val_c) > 0
    assert len(test_c) > 0
    assert len(train_c) + len(val_c) + len(test_c) == len(mock_cases)

    # Verify leakage check passes
    leakage_rep = verify_split_leakage(train_c, val_c, test_c)
    assert leakage_rep["status"] == "PASS"
    assert not leakage_rep["has_leakage"]
    for k, v in leakage_rep["leakage_counts"].items():
        assert v == 0


def test_leakage_verifier_catches_intentional_leakage():
    case_leaked = {
        "case_id": "SYN-CASE-LEAKED",
        "primary_parcel_id": "SYN-PARCEL-LEAKED",
        "split_group_id": "GRP-00001",
        "expected_outcome": "MATCH",
    }
    train_c = [case_leaked]
    val_c = [case_leaked]  # Duplicate in validation!
    test_c = []

    leakage_rep = verify_split_leakage(train_c, val_c, test_c)
    assert leakage_rep["status"] == "FAIL"
    assert leakage_rep["has_leakage"]
    assert leakage_rep["leakage_counts"]["case_id_overlap_train_val"] == 1
