"""
Dataset manifest generator and checksum calculation.
Enforces Section 16: Manifest records relative path, format, row count,
column count, file size, SHA-256 digest, schema version, and synthetic status.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


def calculate_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def generate_manifest(root_dir: Path, schema_version: str = "1.0.0") -> dict[str, Any]:
    manifest_entries = []

    for file_path in sorted(root_dir.rglob("*")):
        if file_path.is_dir() or file_path.name == "manifest.json":
            continue

        rel_path = str(file_path.relative_to(root_dir)).replace("\\", "/")
        file_size = file_path.stat().st_size
        file_sha256 = calculate_sha256(file_path)
        ext = file_path.suffix.lower()

        row_count: int | None = None
        col_count: int | None = None

        if ext == ".csv":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if header:
                        col_count = len(header)
                        row_count = sum(1 for _ in reader)
                    else:
                        col_count = 0
                        row_count = 0
            except Exception:
                pass

        elif ext == ".jsonl":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    row_count = sum(1 for line in f if line.strip())
            except Exception:
                pass

        elif ext == ".geojson":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                    if isinstance(obj, dict) and "features" in obj:
                        row_count = len(obj["features"])
            except Exception:
                pass

        manifest_entries.append({
            "relative_path": rel_path,
            "file_format": ext.lstrip(".").upper(),
            "row_count": row_count,
            "column_count": col_count,
            "file_size_bytes": file_size,
            "sha256": file_sha256,
            "schema_version": schema_version,
            "synthetic_status": "100% SYNTHETIC DATA — NOT AN OFFICIAL GOVERNMENT RECORD",
        })

    manifest = {
        "dataset_name": "landsync-india-synthetic",
        "schema_version": schema_version,
        "total_files": len(manifest_entries),
        "disclaimer": "100% SYNTHETIC DATA — NOT AN OFFICIAL LAND RECORD.",
        "entries": manifest_entries,
    }

    manifest_path = root_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest
