from __future__ import annotations

from typing import Final
from pydantic import BaseModel


class UnitConversionRecord(BaseModel):
    original_value: float
    original_unit: str
    normalized_area_sqm: float | None
    conversion_ratio: float | None
    formula: str
    is_ambiguous: bool
    rule_reference: str
    advisory_notice: str


# Authoritative conversion factors to Square Metres (SI standard)
# 1 Acre = 4046.8564224 m²
# 1 Hectare = 10000 m²
# 1 Sq Foot = 0.09290304 m²
# 1 Guntha (Standard Western/Southern India: 1/40th acre = 1089 sq ft) = 101.17141 m²
# 1 Cent (Southern India: 1/100th acre = 435.6 sq ft) = 40.46856 m²
STANDARD_FACTORS_TO_SQM: Final[dict[str, float]] = {
    "acre": 4046.8564224,
    "acres": 4046.8564224,
    "hectare": 10000.0,
    "hectares": 10000.0,
    "ha": 10000.0,
    "sqm": 1.0,
    "sq m": 1.0,
    "square metre": 1.0,
    "square meter": 1.0,
    "square metres": 1.0,
    "square meters": 1.0,
    "m2": 1.0,
    "sqft": 0.09290304,
    "sq ft": 0.09290304,
    "square feet": 0.09290304,
    "guntha": 101.17141,
    "gunthas": 101.17141,
    "cent": 40.468564,
    "cents": 40.468564,
}

# Ambiguous regional units whose definitions vary across states or districts
# Examples: Bigha, Biswa, Ground, Kanal, Marla, Kattha
AMBIGUOUS_REGIONAL_UNITS: Final[set[str]] = {
    "bigha", "bighas", "biswa", "biswas", "ground", "grounds",
    "kanal", "kanals", "marla", "marlas", "katha", "kattha"
}


def parse_area_string(area_str: str) -> tuple[float, str]:
    """Extract numeric value and unit string from textual area."""
    cleaned = area_str.strip().lower()
    parts = cleaned.split()
    if len(parts) >= 2:
        try:
            val = float(parts[0].replace(",", ""))
            unit = " ".join(parts[1:])
            return val, unit
        except ValueError:
            pass
    # fallback simple digit extract
    import re
    m = re.match(r"^([0-9.,]+)\s*([a-zA-Z\s]+)$", cleaned)
    if m:
        val = float(m.group(1).replace(",", ""))
        unit = m.group(2).strip()
        return val, unit
    return 0.0, cleaned


def normalize_land_unit(value: float, unit_raw: str, state: str | None = None) -> UnitConversionRecord:
    """
    Normalizes land area to square metres while strictly adhering to Rule 13:
    'Never silently normalize ambiguous land units; retain original unit and conversion evidence.'
    """
    clean_unit = unit_raw.strip().lower()

    # Check if this is an ambiguous regional unit
    for amb in AMBIGUOUS_REGIONAL_UNITS:
        if amb in clean_unit:
            return UnitConversionRecord(
                original_value=value,
                original_unit=unit_raw,
                normalized_area_sqm=None,
                conversion_ratio=None,
                formula=f"Unresolved: {unit_raw} is a regionally variable unit without calibrated state schedule.",
                is_ambiguous=True,
                rule_reference="LANDSYNC Engineering Constitution Rule 13 (Ambiguous Unit Protection)",
                advisory_notice=(
                    f"The unit '{unit_raw}' varies significantly across states and tehsils. "
                    "Conversion requires human revenue authority calibration and cannot be automated safely."
                )
            )

    # Standard conversion lookup
    for key, factor in STANDARD_FACTORS_TO_SQM.items():
        if clean_unit == key or clean_unit.startswith(key):
            converted = round(value * factor, 4)
            return UnitConversionRecord(
                original_value=value,
                original_unit=unit_raw,
                normalized_area_sqm=converted,
                conversion_ratio=factor,
                formula=f"{value} {unit_raw} × {factor:.4f} m²/{key} = {converted} m²",
                is_ambiguous=False,
                rule_reference="Standard Indian Revenue Metrics (SI Units)",
                advisory_notice="Standard conversion applied. Original unit and extent preserved in immutable record."
            )

    # Unknown unit
    return UnitConversionRecord(
        original_value=value,
        original_unit=unit_raw,
        normalized_area_sqm=None,
        conversion_ratio=None,
        formula="Unknown unit metric.",
        is_ambiguous=True,
        rule_reference="LANDSYNC Unclassified Unit Protocol",
        advisory_notice=f"Unrecognized unit '{unit_raw}'. Officer review required to establish metric equivalence."
    )
