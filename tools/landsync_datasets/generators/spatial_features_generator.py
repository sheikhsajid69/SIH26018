"""
Spatial Features Generator.
Produces 5,500+ GeoJSON cadastral parcel polygons within fictional village envelopes.
"""

from __future__ import annotations

import random
from typing import Any

from landsync_datasets.geospatial.spatial_generator import generate_parcel_polygon
from landsync_datasets.geospatial.geometry import (
    polygon_geodesic_area_sqm,
    polygon_perimeter_meters,
)
from landsync_datasets.primitives.identifiers import geometry_id


def generate_spatial_features(
    parcels: list[dict[str, Any]],
    target_count: int,
    village_profiles: list[dict[str, Any]],
    rng: random.Random,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Generates spatial features for parcels.
    Returns (spatial_features_list, features_by_id).
    """
    features: list[dict[str, Any]] = []
    features_lookup: dict[str, Any] = {}

    vil_map = {v["village_code"]: v for v in village_profiles}

    for seq in range(1, target_count + 1):
        gid = geometry_id(seq)
        parcel = parcels[(seq - 1) % len(parcels)]
        pid = parcel["parcel_id"]

        vil = vil_map.get(parcel["village_code"], village_profiles[0])
        env = vil["envelope"]

        # Sample a point within the village envelope
        c_lon = rng.uniform(env["min_lon"] + 0.005, env["max_lon"] - 0.005)
        c_lat = rng.uniform(env["min_lat"] + 0.005, env["max_lat"] - 0.005)

        target_area = parcel["area_square_metres"] if parcel["area_square_metres"] > 0 else 4046.85

        # In a small percentage of cases, inject controlled anomalies
        anomaly = "NONE"
        if seq % 90 == 0:
            anomaly = "SELF_INTERSECTING"
        elif seq % 120 == 0:
            anomaly = "UNCLOSED_RING"
        elif seq % 100 == 0:
            anomaly = "SLIVER"
        elif seq % 50 == 0:
            anomaly = "AREA_VARIANCE"

        geom_dict, validity, quality_status = generate_parcel_polygon(
            center_lon=c_lon,
            center_lat=c_lat,
            target_area_sqm=target_area,
            rng=rng,
            anomaly_type=anomaly,
            num_vertices=rng.randint(4, 7),
        )

        ring = geom_dict["coordinates"][0]
        area_calc = polygon_geodesic_area_sqm(ring)
        perim_calc = polygon_perimeter_meters(ring)

        sf_row = {
            "geometry_id": gid,
            "parcel_id": pid,
            "geometry_type": "Polygon",
            "coordinate_reference_system": "EPSG:4326",
            "geometry": geom_dict,
            "area_from_geometry": round(area_calc, 2),
            "perimeter_from_geometry": perim_calc,
            "geometry_validity": validity,
            "spatial_quality_status": quality_status,
            "source_reference": "CADASTRAL_MAP_OFFICIAL" if anomaly == "NONE" else "BLUEPRINT_SURVEY_SKETCH",
            "synthetic_geometry_flag": True,
        }

        features.append(sf_row)
        features_lookup[gid] = sf_row

    return features, features_lookup
