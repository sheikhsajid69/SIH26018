"""
Tests for pure-Python geospatial coordinate algorithms, area calculation, and topology validator.
"""

import math
import random
import pytest

from landsync_datasets.geospatial.geometry import (
    meters_per_degree,
    polygon_centroid,
    polygon_geodesic_area_sqm,
    polygon_perimeter_meters,
    bounding_box,
    has_self_intersection,
)
from landsync_datasets.geospatial.spatial_validator import validate_spatial_feature
from landsync_datasets.geospatial.spatial_generator import generate_parcel_polygon


def test_meters_per_degree_at_equator_and_bangalore():
    m_lon, m_lat = meters_per_degree(12.97)
    # At ~13 degrees latitude, 1 deg lat is ~110.6 km, 1 deg lon is ~108.5 km
    assert 110000 < m_lat < 112000
    assert 107000 < m_lon < 110000


def test_polygon_geodesic_area_and_centroid():
    # Square 100m x 100m around (77.5944, 12.9716)
    c_lon, c_lat = 77.5944, 12.9716
    m_lon, m_lat = meters_per_degree(c_lat)

    half_w = 50.0 / m_lon
    half_h = 50.0 / m_lat

    coords = [
        [c_lon - half_w, c_lat - half_h],
        [c_lon + half_w, c_lat - half_h],
        [c_lon + half_w, c_lat + half_h],
        [c_lon - half_w, c_lat + half_h],
        [c_lon - half_w, c_lat - half_h],
    ]

    area = polygon_geodesic_area_sqm(coords)
    # Expected area = 100 * 100 = 10,000 m² (~2.47 acres)
    assert pytest.approx(area, 0.05) == 10000.0

    centroid = polygon_centroid(coords)
    assert pytest.approx(centroid[0], 0.0001) == c_lon
    assert pytest.approx(centroid[1], 0.0001) == c_lat


def test_ring_closure_and_self_intersection():
    # Valid convex ring
    valid_ring = [
        [77.0, 12.0],
        [77.1, 12.0],
        [77.1, 12.1],
        [77.0, 12.1],
        [77.0, 12.0],
    ]
    assert not has_self_intersection(valid_ring)

    # Self-intersecting bow-tie (swap vertices)
    bowtie_ring = [
        [77.0, 12.0],
        [77.1, 12.1],
        [77.1, 12.0],
        [77.0, 12.1],
        [77.0, 12.0],
    ]
    assert has_self_intersection(bowtie_ring)


def test_spatial_validator_on_valid_and_anomalous_features():
    rng = random.Random(42)

    # 1. Valid parcel
    geom_valid, val_stat, qual_stat = generate_parcel_polygon(
        center_lon=77.59, center_lat=12.97, target_area_sqm=4046.85, rng=rng, anomaly_type="NONE"
    )
    res_valid = validate_spatial_feature(geom_valid, expected_area_sqm=4046.85)
    assert res_valid["is_valid"]
    assert res_valid["geometry_validity"] == "VALID"
    assert res_valid["spatial_quality_status"] == "CONSISTENT"

    # 2. Self-intersecting anomaly
    geom_bow, val_stat_b, qual_stat_b = generate_parcel_polygon(
        center_lon=77.59, center_lat=12.97, target_area_sqm=4046.85, rng=rng, anomaly_type="SELF_INTERSECTING"
    )
    res_bow = validate_spatial_feature(geom_bow)
    assert not res_bow["is_valid"]
    assert res_bow["geometry_validity"] == "SELF_INTERSECTING"

    # 3. Unclosed ring anomaly
    geom_unclosed, val_stat_u, qual_stat_u = generate_parcel_polygon(
        center_lon=77.59, center_lat=12.97, target_area_sqm=4046.85, rng=rng, anomaly_type="UNCLOSED_RING"
    )
    res_unclosed = validate_spatial_feature(geom_unclosed)
    assert not res_unclosed["is_valid"]
    assert res_unclosed["geometry_validity"] == "UNCLOSED_RING"
