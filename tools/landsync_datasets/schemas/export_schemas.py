"""
Export JSON Schema files for all benchmark entities.
"""

from __future__ import annotations

import json
from pathlib import Path

from landsync_datasets.schemas.models import (
    Parcel,
    Party,
    OwnershipClaim,
    DocumentRecord,
    DocumentField,
    MutationEvent,
    EncumbranceRecord,
    SpatialFeature,
    ValidationCase,
    ValidationFinding,
    SyntheticAuditEvent,
    LegalRuleRecord,
    ProvenanceRecord,
)

ENTITY_MODELS = {
    "parcel": Parcel,
    "party": Party,
    "ownership_claim": OwnershipClaim,
    "document": DocumentRecord,
    "document_field": DocumentField,
    "mutation_event": MutationEvent,
    "encumbrance": EncumbranceRecord,
    "spatial_feature": SpatialFeature,
    "validation_case": ValidationCase,
    "validation_finding": ValidationFinding,
    "audit_event": SyntheticAuditEvent,
    "rule_catalogue": LegalRuleRecord,
    "provenance": ProvenanceRecord,
}


def export_all_schemas(output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    exported = {}
    for name, model_cls in ENTITY_MODELS.items():
        schema_path = output_dir / f"{name}.schema.json"
        schema_dict = model_cls.model_json_schema()
        schema_dict["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema_dict["title"] = f"LANDSYNC Synthetic {name.replace('_', ' ').title()}"
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2)
        exported[name] = schema_path
    return exported
