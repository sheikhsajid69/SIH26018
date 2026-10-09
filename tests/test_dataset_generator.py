"""
End-to-end tests for the synthetic dataset generator and quality gates.
"""

from pathlib import Path
from landsync_datasets.config.loader import load_config
from landsync_datasets.reports.reporter import run_quality_gates


def test_dataset_meets_all_quantitative_targets():
    root_dir = Path("datasets/landsync-india-synthetic")
    assert root_dir.exists()

    rep = run_quality_gates(root_dir)
    assert rep["status"] == "PASS"
    assert rep["passed_checks"] == rep["total_checks"]

    # Verify target counts from report checks
    checks_by_name = {c["check_name"]: c for c in rep["checks"]}

    # Cases >= 1,500
    cases_check = checks_by_name["distribution_validation_cases_count"]
    assert cases_check["passed"]
    assert cases_check["details"]["actual_count"] >= 1500

    # Parcels >= 10,000
    parcels_check = checks_by_name["distribution_parcels_count"]
    assert parcels_check["passed"]
    assert parcels_check["details"]["actual_count"] >= 10000


def test_all_13_schemas_exist():
    schemas_dir = Path("datasets/landsync-india-synthetic/schemas")
    assert schemas_dir.exists()
    schema_files = list(schemas_dir.glob("*.schema.json"))
    assert len(schema_files) == 13


def test_manifest_checksums_and_files_exist():
    manifest_path = Path("datasets/landsync-india-synthetic/manifest.json")
    assert manifest_path.exists()
    import json
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["total_files"] >= 40
    for entry in manifest["entries"]:
        file_path = Path("datasets/landsync-india-synthetic") / entry["relative_path"]
        assert file_path.exists()
        assert file_path.stat().st_size == entry["file_size_bytes"]
