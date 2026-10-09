"""
Export pipeline supporting CSV, Parquet, JSON, JSONL, and GeoJSON formats.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    HAS_PYARROW = True
except ImportError:
    HAS_PYARROW = False

from landsync_datasets.exports.manifest import generate_manifest


def export_table_csv(filepath: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            # Flatten lists or dicts for CSV representation
            clean_row = {}
            for k, v in r.items():
                if isinstance(v, (list, dict)):
                    clean_row[k] = json.dumps(v, ensure_ascii=False)
                elif v is None:
                    clean_row[k] = ""
                else:
                    clean_row[k] = v
            writer.writerow(clean_row)


def export_table_parquet(filepath: Path, rows: list[dict[str, Any]]) -> bool:
    if not HAS_PYARROW or not rows:
        return False
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Convert complex objects to JSON strings for consistent parquet schemas
    flat_rows = []
    for r in rows:
        flat_r = {}
        for k, v in r.items():
            if isinstance(v, (list, dict)):
                flat_r[k] = json.dumps(v, ensure_ascii=False)
            else:
                flat_r[k] = v
        flat_rows.append(flat_r)

    table = pa.Table.from_pylist(flat_rows)
    pq.write_table(table, filepath)
    return True


def export_geojson(filepath: Path, spatial_features: list[dict[str, Any]]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)

    features = []
    for sf in spatial_features:
        geom = sf.get("geometry")
        if isinstance(geom, str):
            try:
                geom = json.loads(geom)
            except Exception:
                geom = {"type": "Polygon", "coordinates": []}

        props = {k: v for k, v in sf.items() if k != "geometry"}
        props["disclaimer"] = "100% SYNTHETIC DATA — NOT AN OFFICIAL GOVERNMENT RECORD"

        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": geom,
        })

    geojson_doc = {
        "type": "FeatureCollection",
        "name": "LANDSYNC_AI_SYNTHETIC_SPATIAL_FEATURES",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "disclaimer": "100% SYNTHETIC DATA — NOT AN OFFICIAL LAND RECORD.",
        "features": features,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(geojson_doc, f, indent=2)


def export_jsonl(filepath: Path, records: list[dict[str, Any]]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def export_all_dataset_artifacts(
    root_dir: Path,
    tables: dict[str, list[dict[str, Any]]],
    spatial_features: list[dict[str, Any]],
    document_annotations: list[dict[str, Any]],
    schema_version: str = "1.0.0",
) -> dict[str, Any]:
    """Exports all dataset artifacts to disk in target publication formats."""
    data_dir = root_dir / "data"
    ann_dir = root_dir / "annotations"

    data_dir.mkdir(parents=True, exist_ok=True)
    ann_dir.mkdir(parents=True, exist_ok=True)

    # 1. Export standard tabular tables
    for table_name, rows in tables.items():
        csv_path = data_dir / f"{table_name}.csv"
        export_table_csv(csv_path, rows)

        if HAS_PYARROW:
            parquet_path = data_dir / f"{table_name}.parquet"
            export_table_parquet(parquet_path, rows)

    # 2. Export spatial GeoJSON
    geojson_path = data_dir / "spatial_features.geojson"
    export_geojson(geojson_path, spatial_features)

    # 3. Export JSONL document field annotations
    jsonl_path = ann_dir / "document_field_annotations.jsonl"
    export_jsonl(jsonl_path, document_annotations)

    # 4. Generate manifest with SHA-256 digests
    manifest = generate_manifest(root_dir, schema_version=schema_version)
    return manifest
