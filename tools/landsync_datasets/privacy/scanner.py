"""
Automated privacy and re-identification safety scanner.
Enforces Section 14: Zero real identity numbers (Aadhaar, PAN), zero real phone numbers,
zero real emails, zero exposed secrets, and zero local filesystem paths.
"""

from __future__ import annotations

import re
from typing import Any

# Regex patterns for prohibited authentic credentials
AADHAAR_PATTERN = re.compile(r"\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b")
PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b")
INDIAN_MOBILE_PATTERN = re.compile(r"\b(\+91[\-\s]?)?[6-9]\d{9}\b")
PROHIBITED_EMAIL_DOMAINS = re.compile(r"@(gmail\.com|yahoo\.com|outlook\.com|hotmail\.com|nic\.in|gov\.in)\b", re.IGNORECASE)
SECRET_PATTERN = re.compile(r"\b(AKIA[0-9A-Z]{16}|bearer\s+[A-Za-z0-9\-\._~\+\/]+=*|password\s*[:=]\s*['\"][^'\"]+['\"])\b", re.IGNORECASE)
LOCAL_PATH_PATTERN = re.compile(r"\b(?:[A-Za-z]:\\(?:Users|Windows|Program Files)[\\a-zA-Z0-9_\-\.]*|/(?:Users|home|root)/[a-zA-Z0-9_\-\.]+)\b", re.IGNORECASE)


class PrivacyViolation:
    def __init__(self, table_name: str, record_id: str, field_name: str, violation_type: str, details: str):
        self.table_name = table_name
        self.record_id = record_id
        self.field_name = field_name
        self.violation_type = violation_type
        self.details = details

    def to_dict(self) -> dict[str, str]:
        return {
            "table_name": self.table_name,
            "record_id": self.record_id,
            "field_name": self.field_name,
            "violation_type": self.violation_type,
            "details": self.details,
        }


def scan_record_for_privacy(
    table_name: str,
    record_id: str,
    record: dict[str, Any],
) -> list[PrivacyViolation]:
    """Scans a single record dictionary for potential PII or privacy violations."""
    violations: list[PrivacyViolation] = []

    for field_name, value in record.items():
        if value is None:
            continue
        val_str = str(value)

        # Check for Aadhaar format
        if AADHAAR_PATTERN.search(val_str):
            violations.append(
                PrivacyViolation(
                    table_name=table_name,
                    record_id=record_id,
                    field_name=field_name,
                    violation_type="PROHIBITED_AADHAAR_LIKE_IDENTIFIER",
                    details=f"Value matches 12-digit Aadhaar pattern in field '{field_name}'.",
                )
            )

        # Check for PAN format
        if PAN_PATTERN.search(val_str):
            violations.append(
                PrivacyViolation(
                    table_name=table_name,
                    record_id=record_id,
                    field_name=field_name,
                    violation_type="PROHIBITED_PAN_LIKE_IDENTIFIER",
                    details=f"Value matches 10-character PAN pattern in field '{field_name}'.",
                )
            )

        # Check for real phone numbers
        if INDIAN_MOBILE_PATTERN.search(val_str):
            # Exempt synthetic +91-00000-xxxxx pattern
            if "+91-00000-" not in val_str:
                violations.append(
                    PrivacyViolation(
                        table_name=table_name,
                        record_id=record_id,
                        field_name=field_name,
                        violation_type="PROHIBITED_REAL_PHONE_NUMBER",
                        details=f"Value matches Indian mobile number format in field '{field_name}'.",
                    )
                )

        # Check for public email domains
        if PROHIBITED_EMAIL_DOMAINS.search(val_str):
            violations.append(
                PrivacyViolation(
                    table_name=table_name,
                    record_id=record_id,
                    field_name=field_name,
                    violation_type="PROHIBITED_REAL_EMAIL_DOMAIN",
                    details=f"Value contains non-reserved email domain in field '{field_name}'.",
                )
            )

        # Check for secrets
        if SECRET_PATTERN.search(val_str):
            violations.append(
                PrivacyViolation(
                    table_name=table_name,
                    record_id=record_id,
                    field_name=field_name,
                    violation_type="EXPOSED_CREDENTIAL_OR_SECRET",
                    details=f"Value matches credential/secret pattern in field '{field_name}'.",
                )
            )

        # Check for accidental local paths
        if LOCAL_PATH_PATTERN.search(val_str):
            violations.append(
                PrivacyViolation(
                    table_name=table_name,
                    record_id=record_id,
                    field_name=field_name,
                    violation_type="ACCIDENTAL_LOCAL_PATH",
                    details=f"Value exposes local system filesystem path in field '{field_name}'.",
                )
            )

    return violations


def run_privacy_scan(tables: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """
    Executes comprehensive privacy scanner across all generated tables.
    Returns audit dictionary with summary metrics and list of any violations.
    """
    total_records = 0
    violations: list[PrivacyViolation] = []

    for table_name, rows in tables.items():
        id_field = f"{table_name.rstrip('s')}_id"
        if not rows:
            continue
        sample_keys = list(rows[0].keys())
        # Determine likely ID field
        candidate_ids = [k for k in sample_keys if "id" in k.lower()]
        key_id = candidate_ids[0] if candidate_ids else "id"

        for row in rows:
            total_records += 1
            rec_id = str(row.get(key_id, f"row-{total_records}"))
            record_violations = scan_record_for_privacy(table_name, rec_id, row)
            violations.extend(record_violations)

    passed = len(violations) == 0

    return {
        "status": "PASS" if passed else "FAIL",
        "total_records_scanned": total_records,
        "total_tables_scanned": len(tables),
        "violations_found": len(violations),
        "violations": [v.to_dict() for v in violations],
        "policy": "100% SYNTHETIC DATA POLICY — ZERO REAL PII TOLERANCE",
    }
