"""
Master Synthetic Dataset Generation Pipeline.
Coordinates end-to-end deterministic synthesis of all 13 relational entities,
enforces referential integrity, executes privacy scans, generates group-aware splits,
and exports Kaggle-ready benchmark releases.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from landsync_datasets.config.loader import DatasetConfig, load_config
from landsync_datasets.primitives.identifiers import provenance_id
from landsync_datasets.legal.rule_register import get_all_rules
from landsync_datasets.generators.parcel_generator import generate_parcels
from landsync_datasets.generators.party_generator import generate_parties
from landsync_datasets.generators.ownership_generator import generate_ownership_claims
from landsync_datasets.generators.document_generator import generate_documents_and_fields
from landsync_datasets.generators.event_generator import generate_mutation_events
from landsync_datasets.generators.encumbrance_generator import generate_encumbrances
from landsync_datasets.generators.spatial_features_generator import generate_spatial_features
from landsync_datasets.generators.validation_case_generator import generate_validation_cases_and_findings
from landsync_datasets.generators.audit_generator import generate_audit_events
from landsync_datasets.splits.splitter import (
    split_validation_cases_by_group,
    verify_split_leakage,
    write_split_csvs,
)
from landsync_datasets.privacy.scanner import run_privacy_scan
from landsync_datasets.schemas.export_schemas import export_all_schemas
from landsync_datasets.exports.exporter import export_all_dataset_artifacts


class DatasetPipelineResult:
    def __init__(
        self,
        counts: dict[str, int],
        privacy_report: dict[str, Any],
        leakage_report: dict[str, Any],
        manifest: dict[str, Any],
        output_dir: Path,
    ):
        self.counts = counts
        self.privacy_report = privacy_report
        self.leakage_report = leakage_report
        self.manifest = manifest
        self.output_dir = output_dir


def run_pipeline(config: DatasetConfig | None = None) -> DatasetPipelineResult:
    if config is None:
        config = load_config()

    output_root = config.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    # Initialize dedicated deterministic random state
    rng = random.Random(config.seed)

    # 1. Provenance record
    prov_key = provenance_id(1)
    prov_row = {
        "provenance_id": prov_key,
        "source_type": "DETERMINISTIC_SYNTHETIC_GENERATOR",
        "source_reference": f"landsync_datasets v{config.version}",
        "generation_method": "PSEUDO_RANDOM_STRATIFIED_SAMPLING",
        "generator_version": config.version,
        "generation_seed": config.seed,
        "transformation_history": "SI unit conversion; GeoJSON EPSG:4326 projection; SHA-256 evidence digests.",
        "creation_timestamp": "2026-10-09T00:00:00Z",
        "license_reference": "CC-BY-4.0 (Dataset) / MIT (Software Code)",
        "synthetic_status": "100% SYNTHETIC DATA — NOT AN OFFICIAL GOVERNMENT RECORD",
    }
    provenance_table = [prov_row]

    # 2. Legal Rule Catalogue
    rules_table = [r.model_dump() for r in get_all_rules()]

    # 3. Parties
    parties, party_lookup = generate_parties(
        target_count=config.target_parcels,
        rng=rng,
    )

    # 4. Parcels
    profile = config.jurisdiction_profiles[config.primary_profile_id]
    parcels, parcel_lookup = generate_parcels(
        target_count=config.target_parcels,
        profile=profile,
        rng=rng,
        prov_id=prov_key,
    )

    # 5. Ownership Claims
    claims, claims_by_parcel = generate_ownership_claims(
        parcels=parcels,
        parties=parties,
        rng=rng,
    )

    # 6. Spatial Features
    spatial_features, spatial_lookup = generate_spatial_features(
        parcels=parcels,
        target_count=config.target_spatial_features,
        village_profiles=profile["villages"],
        rng=rng,
    )

    # 7. Documents and Document Field Annotations
    documents, document_fields, doc_lookup = generate_documents_and_fields(
        parcels=parcels,
        ownership_claims=claims_by_parcel,
        target_documents=config.target_documents,
        rng=rng,
        prov_id=prov_key,
    )

    # 8. Mutation Events
    mutation_events = generate_mutation_events(
        parcels=parcels,
        documents=documents,
        target_count=config.target_mutation_events,
        rng=rng,
    )

    # 9. Encumbrances
    encumbrances = generate_encumbrances(
        parcels=parcels,
        documents=documents,
        target_count=config.target_encumbrances,
        rng=rng,
    )

    # 10. Validation Cases and Findings
    validation_cases, validation_findings = generate_validation_cases_and_findings(
        scenario_quotas=config.scenario_quotas,
        parcels=parcels,
        documents=documents,
        rng=rng,
        generator_version=config.version,
        seed=config.seed,
    )

    # 11. Audit Events
    audit_events = generate_audit_events(
        parcels=parcels,
        validation_cases=validation_cases,
        target_count=config.target_audit_events,
        rng=rng,
    )

    # Compile master table dictionary
    tables: dict[str, list[dict[str, Any]]] = {
        "parcels": parcels,
        "parties": parties,
        "ownership_claims": claims,
        "documents": documents,
        "document_fields": document_fields,
        "mutation_events": mutation_events,
        "encumbrances": encumbrances,
        "spatial_features": spatial_features,
        "validation_cases": validation_cases,
        "validation_findings": validation_findings,
        "audit_events": audit_events,
        "rule_catalogue": rules_table,
        "provenance": provenance_table,
    }

    # 12. Group-aware splits and leakage verification
    train_c, val_c, test_c = split_validation_cases_by_group(
        cases=validation_cases,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        seed=config.seed,
    )
    leakage_report = verify_split_leakage(train_c, val_c, test_c)
    write_split_csvs(output_root / "splits", train_c, val_c, test_c)

    # 13. Privacy Scan
    privacy_report = run_privacy_scan(tables)

    # 14. Export JSON Schemas
    export_all_schemas(output_root / "schemas")

    # 15. Export Dataset Artifacts (CSV, Parquet, GeoJSON, JSONL, Manifest)
    manifest = export_all_dataset_artifacts(
        root_dir=output_root,
        tables=tables,
        spatial_features=spatial_features,
        document_annotations=document_fields,
        schema_version=config.version,
    )

    # Counts
    counts = {name: len(rows) for name, rows in tables.items()}
    counts["validation_cases_total"] = len(validation_cases)
    counts["train_cases"] = len(train_c)
    counts["validation_cases_split"] = len(val_c)
    counts["test_cases"] = len(test_c)

    return DatasetPipelineResult(
        counts=counts,
        privacy_report=privacy_report,
        leakage_report=leakage_report,
        manifest=manifest,
        output_dir=output_root,
    )
