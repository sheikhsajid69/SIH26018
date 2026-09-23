from __future__ import annotations

import json
from pathlib import Path
from landsync.models import LandParcel, MutationEvent, OwnershipRelationship


class DemoAuthorityAdapter:
    """
    Synthetic adapter boundary.
    Strictly isolated from core business logic (Rule 10).
    Replace only this adapter for an authorized state connector.
    """

    source_name = "SYNTHETIC DEMO authority record"

    def __init__(self) -> None:
        self._PARCELS: dict[str, dict[str, object]] = {}
        self._OWNERSHIP: dict[str, list[dict[str, object]]] = {}
        self._HISTORY: dict[str, list[dict[str, object]]] = {}
        self._load_fixtures()

    def _load_fixtures(self) -> None:
        data_file = Path(__file__).resolve().parents[5] / "data" / "synthetic" / "authority_records.json"
        if data_file.exists():
            try:
                records = json.loads(data_file.read_text(encoding="utf-8"))
                for r in records:
                    pid = r["parcel_id"]
                    self._PARCELS[pid] = {
                        "id": pid,
                        "ulpin": r.get("synthetic_ulpin", f"SYN-ULPIN-{pid}"),
                        "survey_number": r["survey_number"],
                        "plot_number": r.get("plot_number", "1"),
                        "owner": r["owner"],
                        "area": r["area"],
                        "normalized_area_sqm": r.get("normalized_area_sqm", 4046.86),
                        "state": "Karnataka (Synthetic)",
                        "district": "Synthetic District",
                        "tehsil": "Demo Taluk",
                        "village": r["village"],
                        "land_use": r.get("land_use", "Agricultural"),
                        "geometry": r.get("geometry", {
                            "type": "Polygon",
                            "coordinates": [[[77.5944, 12.9716], [77.5951, 12.9716], [77.5951, 12.9721], [77.5944, 12.9721], [77.5944, 12.9716]]],
                        }),
                        "geometry_source": r.get("geometry_source", "SYNTHETIC DEMO GeoJSON"),
                        "authoritative_source": self.source_name,
                    }
                    self._OWNERSHIP[pid] = [{
                        "id": f"own-{pid.lower()}",
                        "parcel_id": pid,
                        "holder_name": r["owner"],
                        "share_extent": "100%",
                        "relationship_type": "SOLE_PROPRIETOR",
                        "recorded_date": "2018-05-20",
                        "source_ref": f"Sanction Order SO-{pid}",
                        "is_synthetic": True,
                    }]
                    self._HISTORY[pid] = [{
                        "id": f"mut-{pid.lower()}-1",
                        "parcel_id": pid,
                        "mutation_number": f"MUT-{pid}-2018",
                        "event_type": "REGISTRATION",
                        "recorded_date": "2018-05-20",
                        "parties_involved": f"Registered record for {r['owner']}",
                        "description": f"Initial digitization of parcel {pid} in {r['village']}.",
                        "order_reference": f"Tahsildar Order LND-{pid}/2018",
                        "is_synthetic": True,
                    }]
            except Exception:
                pass

        # Demo parcel alias for seed tests
        base = self._PARCELS.get("SYN-PARCEL-002", self._PARCELS.get("SYN-PARCEL-001", {}))
        self._PARCELS["demo-parcel"] = {
            **base,
            "id": "demo-parcel",
            "ulpin": "DEMO-ULPIN-27-000-124-2",
            "owner": "Ramesh Kumar (synthetic demo person)",
            "survey_number": "124/2",
            "area": "2.40 acre",
            "plot_number": "18B",
            "village": "Sampurna",
        }
        self._OWNERSHIP["demo-parcel"] = self._OWNERSHIP.get("SYN-PARCEL-002", [{
            "id": "own-001", "parcel_id": "demo-parcel", "holder_name": "Ramesh Kumar",
            "share_extent": "100% (Sole Khatedar)", "relationship_type": "SOLE_PROPRIETOR",
            "recorded_date": "2012-04-18", "source_ref": "Mutation Entry MR-44/2012", "is_synthetic": True,
        }])
        self._HISTORY["demo-parcel"] = [
            {"id": "mut-001", "parcel_id": "demo-parcel", "mutation_number": "MR-12/1994", "event_type": "PARTITION", "recorded_date": "1994-08-11", "parties_involved": "Ancestral partition among Suresh Kumar & Brothers", "description": "Ancestral land division in Sy No 124 creating sub-division 124/2 (extent 2.40 acre).", "order_reference": "Tahsildar Order No. LND/CR/1994/88", "is_synthetic": True},
            {"id": "mut-002", "parcel_id": "demo-parcel", "mutation_number": "MR-44/2012", "event_type": "SUCCESSION", "recorded_date": "2012-04-18", "parties_involved": "Inheritance by Ramesh Kumar upon succession", "description": "Succession entry sanctioned in favour of legal heir Ramesh Kumar.", "order_reference": "Revenue Inspector Sanction RI/MUT/2012/104", "is_synthetic": True},
            {"id": "mut-003", "parcel_id": "demo-parcel", "mutation_number": "DEMARC-2021-09", "event_type": "DEMARCATION", "recorded_date": "2021-11-04", "parties_involved": "ADLR Taluk Survey Division", "description": "Cadastral field sketch digitization and boundary fixing for Sy No 124/2.", "order_reference": "Survey Settlement Order SO-2021/772", "is_synthetic": True},
        ]

    def parcel(self, parcel_id: str) -> dict[str, object]:
        if parcel_id not in self._PARCELS:
            raise KeyError(parcel_id)
        return self._PARCELS[parcel_id]

    def parcel_model(self, parcel_id: str) -> LandParcel:
        data = self.parcel(parcel_id)
        return LandParcel(**data)

    def ownership(self, parcel_id: str) -> list[OwnershipRelationship]:
        raw_list = self._OWNERSHIP.get(parcel_id, [])
        return [OwnershipRelationship(**item) for item in raw_list]

    def mutation_history(self, parcel_id: str) -> list[MutationEvent]:
        raw_list = self._HISTORY.get(parcel_id, [])
        return [MutationEvent(**item) for item in raw_list]

    def search(self, query: str) -> list[dict[str, object]]:
        q = query.strip().lower()
        return [
            p for p in self._PARCELS.values()
            if any(q in str(p.get(k, "")).lower() for k in ("id", "ulpin", "survey_number", "village", "owner"))
        ]

    def all_parcel_ids(self) -> list[str]:
        return list(self._PARCELS.keys())
