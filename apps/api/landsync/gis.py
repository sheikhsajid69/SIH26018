from __future__ import annotations

import math
from typing import Any


def polygon_area_sqm(coordinates: list[list[float]]) -> float:
    """
    Calculate approximate geodesic area in square meters for EPSG:4326 polygon coordinates.
    Uses spherical excess / planar projection at polygon centroid latitude.
    """
    if len(coordinates) < 3:
        return 0.0

    # Ensure closed ring
    coords = coordinates[:]
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    # Find mean latitude for local meter projection
    mean_lat = sum(p[1] for p in coords[:-1]) / len(coords[:-1])
    lat_rad = math.radians(mean_lat)

    # Conversion factors for degree to meters
    meters_per_deg_lat = 111132.92 - 559.82 * math.cos(2 * lat_rad) + 1.175 * math.cos(4 * lat_rad)
    meters_per_deg_lon = 111412.84 * math.cos(lat_rad) - 93.5 * math.cos(3 * lat_rad)

    # Project to metric Cartesian coords
    metric_pts = [(lon * meters_per_deg_lon, lat * meters_per_deg_lat) for lon, lat in coords]

    # Shoelace formula
    area = 0.0
    n = len(metric_pts)
    for i in range(n - 1):
        x1, y1 = metric_pts[i]
        x2, y2 = metric_pts[i + 1]
        area += x1 * y2 - x2 * y1

    return abs(area) / 2.0


def bounding_box(coordinates: list[list[float]]) -> tuple[float, float, float, float]:
    """Return (min_lon, min_lat, max_lon, max_lat) for polygon coordinates."""
    return (
        min(p[0] for p in coordinates),
        min(p[1] for p in coordinates),
        max(p[0] for p in coordinates),
        max(p[1] for p in coordinates),
    )


def bbox_iou(bbox_a: tuple[float, float, float, float], bbox_b: tuple[float, float, float, float]) -> float:
    """Calculate Intersection over Union (IoU) of two bounding boxes."""
    min_x_a, min_y_a, max_x_a, max_y_a = bbox_a
    min_x_b, min_y_b, max_x_b, max_y_b = bbox_b

    inter_min_x = max(min_x_a, min_x_b)
    inter_min_y = max(min_y_a, min_y_b)
    inter_max_x = min(max_x_a, max_x_b)
    inter_max_y = min(max_y_a, max_y_b)

    inter_w = max(0.0, inter_max_x - inter_min_x)
    inter_h = max(0.0, inter_max_y - inter_min_y)
    inter_area = inter_w * inter_h

    area_a = max(0.0, max_x_a - min_x_a) * max(0.0, max_y_a - min_y_a)
    area_b = max(0.0, max_x_b - min_x_b) * max(0.0, max_y_b - min_y_b)
    union_area = area_a + area_b - inter_area

    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def polygon_centroid(coordinates: list[list[float]]) -> tuple[float, float]:
    """Calculate centroid (mean lon, mean lat) for coordinates."""
    if not coordinates:
        return (0.0, 0.0)
    pts = coordinates[:-1] if coordinates[0] == coordinates[-1] and len(coordinates) > 1 else coordinates
    mean_lon = sum(p[0] for p in pts) / len(pts)
    mean_lat = sum(p[1] for p in pts) / len(pts)
    return (round(mean_lon, 6), round(mean_lat, 6))


def compare_geometries(
    submitted_geometry: dict[str, Any],
    authoritative_geometry: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare submitted blueprint / CAD / GeoJSON geometry with authoritative cadastral geometry.
    Adheres strictly to Rule 14: All GIS operations report coordinate reference system (EPSG:4326)
    and include explicit advisory notice that mathematical overlap does not establish title.
    """
    sub_coords = submitted_geometry.get("coordinates", [[]])[0]
    auth_coords = authoritative_geometry.get("coordinates", [[]])[0]

    sub_area = polygon_area_sqm(sub_coords)
    auth_area = polygon_area_sqm(auth_coords)

    sub_bbox = bounding_box(sub_coords) if sub_coords else (0, 0, 0, 0)
    auth_bbox = bounding_box(auth_coords) if auth_coords else (0, 0, 0, 0)

    iou = bbox_iou(sub_bbox, auth_bbox)
    centroid_sub = polygon_centroid(sub_coords)
    centroid_auth = polygon_centroid(auth_coords)

    # Calculate centroid offset in meters
    lat_diff = abs(centroid_sub[1] - centroid_auth[1]) * 111139.0
    lon_diff = abs(centroid_sub[0] - centroid_auth[0]) * 111139.0 * math.cos(math.radians(centroid_auth[1]))
    offset_meters = math.hypot(lat_diff, lon_diff)

    area_variance_pct = (abs(sub_area - auth_area) / auth_area * 100.0) if auth_area > 0 else 0.0

    status = "CONSISTENT"
    if iou < 0.70 or area_variance_pct > 5.0 or offset_meters > 10.0:
        status = "SPATIAL_VARIANCE_DETECTED"
    elif iou < 0.90 or area_variance_pct > 1.0 or offset_meters > 2.0:
        status = "ADVISORY_ALIGNMENT_NEEDED"

    return {
        "status": status,
        "crs": "EPSG:4326 (WGS84)",
        "iou_score": round(iou, 4),
        "submitted_area_sqm": round(sub_area, 2),
        "authoritative_area_sqm": round(auth_area, 2),
        "area_variance_sqm": round(abs(sub_area - auth_area), 2),
        "area_variance_percent": round(area_variance_pct, 2),
        "centroid_offset_meters": round(offset_meters, 2),
        "submitted_centroid": centroid_sub,
        "authoritative_centroid": centroid_auth,
        "advisory_disclaimer": (
            "SPATIAL ADVISORY: Spatial comparison metrics (IoU, centroid offset, and area variance) "
            "are calculated for advisory validation purposes only. They do not constitute a legal demarcation, "
            "cadastral survey settlement, or boundary adjudication."
        ),
    }
