"""
Tests for Privacy Scanner and 100% Synthetic Data Policy Enforcement.
"""

from landsync_datasets.privacy.scanner import scan_record_for_privacy, run_privacy_scan


def test_clean_synthetic_record_passes():
    record = {
        "parcel_id": "SYN-PARCEL-000001",
        "holder_name": "Arjun Rao",
        "identity_reference_type": "SYNTHETIC_BENCHMARK_TOKEN",
        "identity_reference_value": "SYN-ID-BENCHMARK-0000001",
        "email": "demo.arjun@example.invalid",
        "phone": "+91-00000-00001",
        "synthetic_record_flag": True,
    }
    violations = scan_record_for_privacy("parcels", "SYN-PARCEL-000001", record)
    assert len(violations) == 0


def test_detects_prohibited_aadhaar_pattern():
    bad_record = {
        "parcel_id": "SYN-PARCEL-000002",
        "aadhaar": "9876 5432 1098",  # real-looking 12-digit sequence
    }
    violations = scan_record_for_privacy("parcels", "SYN-PARCEL-000002", bad_record)
    assert len(violations) == 1
    assert violations[0].violation_type == "PROHIBITED_AADHAAR_LIKE_IDENTIFIER"


def test_detects_prohibited_pan_pattern():
    bad_record = {
        "party_id": "SYN-PARTY-000003",
        "pan": "ABCDE1234F",  # 5 letters, 4 digits, 1 letter
    }
    violations = scan_record_for_privacy("parties", "SYN-PARTY-000003", bad_record)
    assert len(violations) == 1
    assert violations[0].violation_type == "PROHIBITED_PAN_LIKE_IDENTIFIER"


def test_detects_prohibited_real_email_domain():
    bad_record = {
        "party_id": "SYN-PARTY-000004",
        "email": "test.user@gmail.com",
    }
    violations = scan_record_for_privacy("parties", "SYN-PARTY-000004", bad_record)
    assert len(violations) == 1
    assert violations[0].violation_type == "PROHIBITED_REAL_EMAIL_DOMAIN"


def test_detects_accidental_local_path():
    bad_record = {
        "doc_id": "SYN-DOC-000005",
        "storage_path": "C:\\Users\\Sajid\\secret_evidence.txt",
    }
    violations = scan_record_for_privacy("documents", "SYN-DOC-000005", bad_record)
    assert len(violations) == 1
    assert violations[0].violation_type == "ACCIDENTAL_LOCAL_PATH"


def test_run_privacy_scan_on_table_dict():
    clean_tables = {
        "parties": [
            {
                "party_id": "SYN-PARTY-000001",
                "synthetic_display_name": "Ramesh Kumar",
                "identity_reference_value": "SYN-ID-BENCHMARK-0000001",
            }
        ]
    }
    report = run_privacy_scan(clean_tables)
    assert report["status"] == "PASS"
    assert report["violations_found"] == 0
