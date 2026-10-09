"""
Spatial quality validation and topology checker.
Evaluates GeoJSON features against strict cadastral validation rules.
"""

from __future__ import annotations

from typing import Any
from landsync_datasets.geospatial.geometry import (
    polygon_centroid,
    polygon_geodesic_area_sqm,
    polygon_perimeter_meters,
    bounding_box,
    has_self_intersection,
)


def validate_spatial_feature(
    geometry: dict[str, Any],
    expected_area_sqm: float | None = None,
    envelope: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Validates a GeoJSON polygon geometry dictionary.
    Returns validation dictionary with geometry_validity, spatial_quality_status,
    computed area, perimeter, and explanatory messages.
    """
    geom_type = geometry.get("type", "")
    if geom_type != "Polygon":
        return {
            "is_valid": False,
            "geometry_validity": "UNSUPPORTED_GEOMETRY_TYPE",
            "spatial_quality_status": "SPATIAL_VARIANCE_DETECTED",
            "area_sqm": 0.0,
            "perimeter_meters": 0.0,
            "explanation": f"Unsupported geometry type '{geom_type}'; expected 'Polygon'.",
        }

    rings = geometry.get("coordinates", [])
    if not rings or not isinstance(rings, list) or len(rings) == 0:
        return {
            "is_valid": False,
            "geometry_validity": "DEGENERATE_COORDINATES",
            "spatial_quality_status": "SPATIAL_VARIANCE_DETECTED",
            "area_sqm": 0.0,
            "perimeter_meters": 0.0,
            "explanation": "Polygon contains empty coordinate rings.",
        }

    exterior_ring = rings[0]
    if len(exterior_ring) < 4:
        return {
            "is_valid": False,
            "geometry_validity": "DEGENERATE_COORDINATES",
            "spatial_quality_status": "SPATIAL_VARIANCE_DETECTED",
            "area_sqm": 0.0,
            "perimeter_meters": 0.0,
            "explanation": f"Exterior ring has only {len(exterior_ring)} points; minimum 4 required.",
        }

    # 1. Coordinate range check (EPSG:4326: [lon, lat])
    for pt in exterior_ring:
        if not (isinstance(pt, (list, tuple)) and len(pt) >= 2):
            return {
                "is_valid": False,
                "geometry_validity": "DEGENERATE_COORDINATES",
                "spatial_quality_status": "SPATIAL_VARIANCE_DETECTED",
                "area_sqm": 0.0,
                "perimeter_meters": 0.0,
                "explanation": "Malformed coordinate point in exterior ring.",
            }
        lon, lat = pt[0], pt[1]
        if not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
            return {
                "is_valid": False,
                "geometry_validity": "OUT_OF_BOUNDS_COORDINATES",
                "spatial_quality_status": "SPATIAL_VARIANCE_DETECTED",
                "area_sqm": 0.0,
                "perimeter_meters": 0.0,
                "explanation": f"Coordinate [{lon}, {lat}] outside valid WGS84 range.",
            }

    # 2. Ring closure check
    is_closed = (exterior_ring[0][0] == exterior_ring[-1][0]) and (
        exterior_ring[0][1] == exterior_ring[-1][1]
    )
    if not is_closed:
        return {
            "is_valid": False,
            "geometry_validity": "UNCLOSED_RING",
            "spatial_quality_status": "SPATIAL_VARIANCE_DETECTED",
            "area_sqm": 0.0,
            "perimeter_meters": 0.0,
            "explanation": "Exterior ring first and last coordinates do not match.",
        }

    # 3. Self-intersection check
    if has_self_intersection(exterior_ring):
        area = polygon_geodesic_area_sqm(exterior_ring)
        perim = polygon_perimeter_meters(exterior_ring)
        return {
            "is_valid": False,
            "geometry_validity": "SELF_INTERSECTING",
            "spatial_quality_status": "SPATIAL_VARIANCE_DETECTED",
            "area_sqm": round(area, 2),
            "perimeter_meters": perim,
            "explanation": "Self-intersecting polygon boundary detected (bow-tie topology).",
        }

    # 4. Metric calculations
    computed_area = polygon_geodesic_area_sqm(exterior_ring)
    computed_perim = polygon_perimeter_meters(exterior_ring)

    # 5. Envelope containment check
    if envelope:
        min_lon, min_lat, max_lon, max_lat = bounding_box(exterior_ring)
        if (
            min_lon < envelope["min_lon"] - 0.05
            or max_lon > envelope["max_lon"] + 0.05
            or min_lat < envelope["min_lat"] - 0.05
            or max_lat > envelope["max_lat"] + 0.05
        ):
            return {
                "is_valid": True,
                "geometry_validity": "VALID",
                "spatial_quality_status": "SPATIAL_VARIANCE_DETECTED",
                "area_sqm": round(computed_area, 2),
                "perimeter_meters": computed_perim,
                "explanation": "Parcel boundary extends outside synthetic jurisdiction envelope.",
            }

    # 6. Area variance vs expected textual area
    quality_status = "CONSISTENT"
    explanation = "Valid cadastral polygon topology."
    if expected_area_sqm and expected_area_sqm > 0:
        pct_diff = (abs(computed_area - expected_area_sqm) / expected_area_sqm) * 100.0
        if pct_diff > 5.0:
            quality_status = "SPATIAL_VARIANCE_DETECTED"
            explanation = (
                f"Computed polygon area ({computed_area:.1f} m²) differs by {pct_diff:.1f}% "
                f"from recorded extent ({expected_area_sqm:.1f} m²)."
            )

    return {
        "is_valid": True,
        "geometry_validity": "VALID",
        "spatial_quality_status": quality_status,
        "area_sqm": round(computed_area, 2),
        "perimeter_meters": computed_perim,
        "explanation": explanation,
    }
