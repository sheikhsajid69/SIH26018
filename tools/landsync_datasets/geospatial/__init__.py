"""
Geospatial processing and generation package.
"""

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

__all__ = [
    "meters_per_degree",
    "polygon_centroid",
    "polygon_geodesic_area_sqm",
    "polygon_perimeter_meters",
    "bounding_box",
    "has_self_intersection",
    "validate_spatial_feature",
    "generate_parcel_polygon",
]
