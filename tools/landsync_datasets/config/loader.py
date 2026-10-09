"""
Configuration loader for synthetic dataset generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml


def load_yaml(path: Path | str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Configuration file not found: {p}")
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class DatasetConfig:
    def __init__(self, config_dict: dict[str, Any], root_dir: Path):
        self.raw = config_dict
        self.root_dir = root_dir

        self.dataset_name = config_dict.get("dataset_name", "landsync-india-synthetic")
        self.dataset_title = config_dict.get("dataset_title", "LANDSYNC-India: Synthetic Cadastral & Land Record Benchmark")
        self.version = str(config_dict.get("version", "1.0.0"))
        self.seed = int(config_dict.get("generator_seed", 42))

        # Output paths
        paths_cfg = config_dict.get("paths", {})
        self.output_root = root_dir / paths_cfg.get("output_root", "datasets/landsync-india-synthetic")

        # Quotas
        quotas_rel = config_dict.get("quotas", {}).get("scenario_quotas_path", "configs/scenario_quotas.yaml")
        quotas_path = root_dir / quotas_rel
        self.scenario_quotas = load_yaml(quotas_path).get("scenario_quotas", {})

        # Jurisdiction profiles
        jur_rel = config_dict.get("jurisdiction", {}).get("profiles_config_path", "configs/jurisdiction_profiles.yaml")
        jur_path = root_dir / jur_rel
        self.jurisdiction_profiles = load_yaml(jur_path).get("jurisdiction_profiles", {})
        self.primary_profile_id = config_dict.get("jurisdiction", {}).get("primary_profile", "KA_PILOT")

        # Targets
        targets_cfg = config_dict.get("targets", {})
        self.target_parcels = int(targets_cfg.get("parcels", 10000))
        self.target_validation_cases = int(targets_cfg.get("validation_cases", 2520))
        self.target_documents = int(targets_cfg.get("documents", 5500))
        self.target_document_fields = int(targets_cfg.get("document_fields", 32000))
        self.target_mutation_events = int(targets_cfg.get("mutation_events", 3500))
        self.target_encumbrances = int(targets_cfg.get("encumbrances", 1500))
        self.target_spatial_features = int(targets_cfg.get("spatial_features", 5500))
        self.target_audit_events = int(targets_cfg.get("audit_events", 4000))


def load_config(config_path: Path | str | None = None) -> DatasetConfig:
    repo_root = Path(__file__).resolve().parents[3]
    if config_path is None:
        config_path = repo_root / "configs" / "default.yaml"
    else:
        config_path = Path(config_path)
        if not config_path.is_absolute():
            config_path = repo_root / config_path

    cfg_dict = load_yaml(config_path)
    return DatasetConfig(cfg_dict, repo_root)
