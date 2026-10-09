"""
Pure-Python geospatial algorithms and coordinate geometry calculations.
Strictly adheres to Section 13: Geodesic area calculation on EPSG:4326 coordinates,
coordinate range validation, ring closure, and segment intersection checks.
"""

from __future__ import annotations

import math
from typing import Any


def meters_per_degree(lat_deg: float) -> tuple[float, float]:
    """
    Returns (meters_per_deg_lon, meters_per_deg_lat) at a given latitude.
    Based on WGS84 ellipsoid parameters.
    """
    lat_rad = math.radians(lat_deg)
    m_per_deg_lat = 111132.92 - 559.82 * math.cos(2 * lat_rad) + 1.175 * math.cos(4 * lat_rad)
    m_per_deg_lon = 111412.84 * math.cos(lat_rad) - 93.5 * math.cos(3 * lat_rad)
    return m_per_deg_lon, m_per_deg_lat


def polygon_centroid(coords: list[list[float]]) -> tuple[float, float]:
    """Calculate centroid (mean_lon, mean_lat) for polygon ring."""
    if not coords:
        return 0.0, 0.0
    pts = coords[:-1] if coords[0] == coords[-1] and len(coords) > 1 else coords
    mean_lon = sum(p[0] for p in pts) / len(pts)
    mean_lat = sum(p[1] for p in pts) / len(pts)
    return round(mean_lon, 7), round(mean_lat, 7)


def polygon_geodesic_area_sqm(coords: list[list[float]]) -> float:
    """
    Calculate geodesic area in square metres for EPSG:4326 polygon coordinates.
    Projects local coordinates onto metric Cartesian plane at centroid latitude,
    then applies Shoelace formula.
    """
    if len(coords) < 3:
        return 0.0

    # Ensure closed ring
    ring = coords[:]
    if ring[0] != ring[-1]:
        ring.append(ring[0])

    centroid_lon, centroid_lat = polygon_centroid(ring)
    m_lon, m_lat = meters_per_degree(centroid_lat)

    # Project to local metric Cartesian coordinates
    pts = [(p[0] * m_lon, p[1] * m_lat) for p in ring]

    # Shoelace formula
    area = 0.0
    n = len(pts)
    for i in range(n - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        area += x1 * y2 - x2 * y1

    return abs(area) / 2.0


def polygon_perimeter_meters(coords: list[list[float]]) -> float:
    """Calculate perimeter in metres for EPSG:4326 polygon coordinates."""
    if len(coords) < 2:
        return 0.0

    ring = coords[:]
    if ring[0] != ring[-1]:
        ring.append(ring[0])

    centroid_lon, centroid_lat = polygon_centroid(ring)
    m_lon, m_lat = meters_per_degree(centroid_lat)

    perimeter = 0.0
    for i in range(len(ring) - 1):
        dx = (ring[i + 1][0] - ring[i][0]) * m_lon
        dy = (ring[i + 1][1] - ring[i][1]) * m_lat
        perimeter += math.hypot(dx, dy)

    return round(perimeter, 2)


def bounding_box(coords: list[list[float]]) -> tuple[float, float, float, float]:
    """Return (min_lon, min_lat, max_lon, max_lat)."""
    if not coords:
        return 0.0, 0.0, 0.0, 0.0
    return (
        min(p[0] for p in coords),
        min(p[1] for p in coords),
        max(p[0] for p in coords),
        max(p[1] for p in coords),
    )


def segments_intersect(
    p1: list[float], p2: list[float], p3: list[float], p4: list[float]
) -> bool:
    """
    Check if line segment p1-p2 strictly intersects line segment p3-p4.
    """
    def ccw(a: list[float], b: list[float], c: list[float]) -> float:
        return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])

    d1 = ccw(p1, p2, p3)
    d2 = ccw(p1, p2, p4)
    d3 = ccw(p3, p4, p1)
    d4 = ccw(p3, p4, p2)

    return ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
        (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
    )


def has_self_intersection(coords: list[list[float]]) -> bool:
    """
    Check if polygon ring contains any self-intersecting non-adjacent edges.
    """
    ring = coords[:]
    if ring[0] != ring[-1]:
        ring.append(ring[0])

    n = len(ring) - 1  # number of segments
    if n < 4:
        return False

    for i in range(n):
        seg1_a = ring[i]
        seg1_b = ring[i + 1]
        for j in range(i + 2, n):
            # If adjacent at the ring closure wrap, skip
            if i == 0 and j == n - 1:
                continue
            seg2_a = ring[j]
            seg2_b = ring[j + 1]
            if segments_intersect(seg1_a, seg1_b, seg2_a, seg2_b):
                return True

    return False
