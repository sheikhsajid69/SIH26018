from __future__ import annotations


class DemoAuthorityAdapter:
    """Synthetic adapter boundary. Replace only this class for an authorized state connector."""

    source_name = "SYNTHETIC DEMO authority record"

    def parcel(self, parcel_id: str) -> dict[str, object]:
        if parcel_id != "demo-parcel":
            raise KeyError(parcel_id)
        return {
            "id": parcel_id,
            "ulpin": "DEMO-ULPIN-27-000-124-2",
            "survey_number": "124/2",
            "plot_number": "18B",
            "owner": "Ramesh Kumar (synthetic demo person)",
            "area": "2.40 acre",
            "normalized_area_sqm": 9712.46,
            "state": "Demo State",
            "district": "Sample District",
            "tehsil": "Model Tehsil",
            "village": "Sampurna",
            "land_use": "Agricultural",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[77.5944, 12.9716], [77.5951, 12.9716], [77.5951, 12.9721], [77.5944, 12.9721], [77.5944, 12.9716]]],
            },
            "geometry_source": "SYNTHETIC DEMO GeoJSON",
            "authoritative_source": self.source_name,
        }
