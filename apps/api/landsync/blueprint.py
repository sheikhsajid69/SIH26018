from __future__ import annotations

from pydantic import BaseModel, Field


class DetectedDimension(BaseModel):
    label: str
    dimension_metres: float
    confidence: float
    source_segment: str


class BlueprintAnalysis(BaseModel):
    provider: str
    model_version: str
    is_mock: bool = True
    confidence: float = Field(ge=0, le=1)
    detected_labels: list[str]
    detected_dimensions: list[DetectedDimension]
    detected_geometry_geojson: dict[str, object]
    spatial_consistency_status: str
    area_estimate_sqm: float
    advisory_disclaimer: str


class MockBlueprintProvider:
    """
    Deterministic Computer Vision provider for land sketches and blueprint drawings.
    Explicitly advertises itself as MOCK / SYNTHETIC ADVISORY to prevent deceptive claims.
    """

    provider = "mock-blueprint-cv"
    model_version = "cv-sketch-0.3"

    def analyze(self, file_name: str, body: bytes) -> BlueprintAnalysis:
        # Synthetic mock extraction of boundary lines, dimensions, and annotations from deed sketch
        return BlueprintAnalysis(
            provider=self.provider,
            model_version=self.model_version,
            is_mock=True,
            confidence=0.86,
            detected_labels=["SURVEY 124/2", "PLOT 18B", "ACCESS ROAD 12M", "NORTH BOUNDARY"],
            detected_dimensions=[
                DetectedDimension(label="North Border", dimension_metres=48.5, confidence=0.89, source_segment="Line Segment N1-N2"),
                DetectedDimension(label="East Border", dimension_metres=192.8, confidence=0.85, source_segment="Line Segment E1-E2"),
                DetectedDimension(label="South Border", dimension_metres=49.1, confidence=0.87, source_segment="Line Segment S1-S2"),
                DetectedDimension(label="West Border", dimension_metres=190.2, confidence=0.83, source_segment="Line Segment W1-W2"),
            ],
            detected_geometry_geojson={
                "type": "Polygon",
                "coordinates": [
                    [
                        [77.59445, 12.97162],
                        [77.59508, 12.97162],
                        [77.59506, 12.97208],
                        [77.59443, 12.97208],
                        [77.59445, 12.97162],
                    ]
                ],
            },
            spatial_consistency_status="PARTIAL_OVERLAP_WITH_AUTHORITY",
            area_estimate_sqm=9348.0,  # ~2.31 acres extracted from sketch
            advisory_disclaimer=(
                "MOCK COMPUTER VISION RESULT: Geometry generated from raster edge detection is advisory only. "
                "It does NOT establish legal boundary lines or substitute for a certified Total Station / DGPS survey."
            ),
        )
