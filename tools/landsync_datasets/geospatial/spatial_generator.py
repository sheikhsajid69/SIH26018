"""
Cadastral parcel polygon geometry generator.
Produces realistic synthetic parcels within controlled fictional village envelopes.
Supports intentional generation of topology anomalies for validation benchmarking.
"""

from __future__ import annotations

import math
import random
from typing import Any
from landsync_datasets.geospatial.geometry import (
    meters_per_degree,
    polygon_geodesic_area_sqm,
    polygon_perimeter_meters,
)


def generate_parcel_polygon(
    center_lon: float,
    center_lat: float,
    target_area_sqm: float,
    rng: random.Random,
    anomaly_type: str = "NONE",
    num_vertices: int = 5,
) -> tuple[dict[str, Any], str, str]:
    """
    Generates a synthetic parcel polygon in GeoJSON format.
    Returns (geometry_dict, geometry_validity, spatial_quality_status).
    """
    m_lon, m_lat = meters_per_degree(center_lat)

    # Approximate radius for target area: Area = pi * r^2  =>  r = sqrt(Area / pi)
    base_radius_meters = math.sqrt(max(100.0, target_area_sqm) / math.pi)

    angles = sorted([rng.uniform(0, 2 * math.pi) for _ in range(num_vertices)])
    coords_local_metric = []

    for angle in angles:
        r = base_radius_meters * rng.uniform(0.75, 1.25)
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        coords_local_metric.append((x, y))

    # Scale metric coordinates so initial polygon area matches target_area_sqm
    temp_ring = coords_local_metric + [coords_local_metric[0]]
    initial_area = 0.0
    for i in range(len(temp_ring) - 1):
        initial_area += temp_ring[i][0] * temp_ring[i + 1][1] - temp_ring[i + 1][0] * temp_ring[i][1]
    initial_area = abs(initial_area) / 2.0

    if initial_area > 0 and anomaly_type != "AREA_VARIANCE":
        scale = math.sqrt(target_area_sqm / initial_area)
        coords_local_metric = [(x * scale, y * scale) for x, y in coords_local_metric]

    # Convert metric offsets back to (lon, lat)
    ring = [[round(center_lon + (x / m_lon), 7), round(center_lat + (y / m_lat), 7)] for x, y in coords_local_metric]

    # Close the ring
    ring.append(ring[0][:])

    validity = "VALID"
    quality_status = "CONSISTENT"

    if anomaly_type == "SELF_INTERSECTING":
        w = base_radius_meters
        h = base_radius_meters
        bowtie_pts = [
            (-w, -h), (w, h), (-w, h), (w, -h)
        ]
        ring = [[round(center_lon + (x / m_lon), 7), round(center_lat + (y / m_lat), 7)] for x, y in bowtie_pts]
        ring.append(ring[0][:])
        validity = "SELF_INTERSECTING"
        quality_status = "SPATIAL_VARIANCE_DETECTED"

    elif anomaly_type == "UNCLOSED_RING" and len(ring) >= 4:
        # Intentionally tamper with last point
        ring[-1] = [round(ring[-1][0] + 0.0001, 7), round(ring[-1][1] + 0.0001, 7)]
        validity = "UNCLOSED_RING"
        quality_status = "SPATIAL_VARIANCE_DETECTED"

    elif anomaly_type == "SLIVER":
        # Create an extremely narrow sliver parcel
        w = base_radius_meters * 0.05
        h = base_radius_meters * 2.5
        sliver_pts = [
            (-w, -h), (w, -h), (w, h), (-w, h)
        ]
        ring = [[round(center_lon + (x / m_lon), 7), round(center_lat + (y / m_lat), 7)] for x, y in sliver_pts]
        ring.append(ring[0][:])
        validity = "VALID"
        quality_status = "SLIVER_GAP"

    elif anomaly_type == "AREA_VARIANCE":
        # Scale polygon vertices up by 25% (area increases by ~56%)
        scaled_ring = []
        for pt in ring[:-1]:
            dx = (pt[0] - center_lon) * 1.25
            dy = (pt[1] - center_lat) * 1.25
            scaled_ring.append([round(center_lon + dx, 7), round(center_lat + dy, 7)])
        scaled_ring.append(scaled_ring[0][:])
        ring = scaled_ring
        validity = "VALID"
        quality_status = "SPATIAL_VARIANCE_DETECTED"

    elif anomaly_type == "COORDINATE_SHIFT":
        # Translate coordinates significantly (e.g. 50 meters offset)
        shift_deg_lat = 50.0 / m_lat
        shift_deg_lon = 50.0 / m_lon
        ring = [[round(p[0] + shift_deg_lon, 7), round(p[1] + shift_deg_lat, 7)] for p in ring]
        validity = "VALID"
        quality_status = "SPATIAL_VARIANCE_DETECTED"

    geometry = {
        "type": "Polygon",
        "coordinates": [ring],
    }

    return geometry, validity, quality_status
