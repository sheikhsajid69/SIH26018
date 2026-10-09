"""
Dedicated, mathematically auditable Area Normalization Module.
Strictly enforces LANDSYNC Engineering Constitution Rule 13:
'Never silently normalize ambiguous land units; retain original unit and conversion evidence.'
"""

from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Final
from pydantic import BaseModel, Field


class AreaNormalizationResult(BaseModel):
    original_value: float
    original_unit: str
    normalized_value_sqm: float | None
    normalized_unit: str = "square_metre"
    conversion_rule: str
    conversion_factor: float | None
    precision_decimals: int = 4
    rounding_policy: str = "ROUND_HALF_UP"
    is_ambiguous: bool
    ambiguity_status: str
    formula: str
    advisory_notice: str


# Authoritative Decimal conversion factors to Square Metres (SI standard)
DECIMAL_FACTORS_TO_SQM: Final[dict[str, Decimal]] = {
    "acre": Decimal("4046.8564224"),
    "hectare": Decimal("10000.0"),
    "ha": Decimal("10000.0"),
    "sqm": Decimal("1.0"),
    "sq m": Decimal("1.0"),
    "square metre": Decimal("1.0"),
    "square meter": Decimal("1.0"),
    "m2": Decimal("1.0"),
    "sqft": Decimal("0.09290304"),
    "sq ft": Decimal("0.09290304"),
    "square feet": Decimal("0.09290304"),
    "guntha": Decimal("101.17141056"),  # exactly 1/40 of an acre
    "cent": Decimal("40.468564224"),   # exactly 1/100 of an acre
}

AMBIGUOUS_UNITS: Final[set[str]] = {
    "bigha", "biswa", "ground", "kanal", "marla", "katha", "kattha", "chatak", "nali", "mutthi"
}

_CLEAN_RE = re.compile(r"^([0-9.,]+)\s*([a-zA-Z\s]+)$")


def parse_area_text(area_text: str) -> tuple[float, str]:
    """Extract numeric extent and unit string from raw input."""
    cleaned = area_text.strip().lower()
    parts = cleaned.split(maxsplit=1)
    if len(parts) == 2:
        try:
            return float(parts[0].replace(",", "")), parts[1].strip()
        except ValueError:
            pass
    m = _CLEAN_RE.match(cleaned)
    if m:
        try:
            return float(m.group(1).replace(",", "")), m.group(2).strip()
        except ValueError:
            pass
    return 0.0, cleaned


def normalize_area(
    value: float,
    unit_raw: str,
    precision: int = 4,
) -> AreaNormalizationResult:
    """
    Normalizes numeric land extent to square metres using high-precision Decimal arithmetic.
    Returns structured AreaNormalizationResult preserving complete conversion provenance.
    """
    clean_unit = unit_raw.strip().lower()
    clean_base = clean_unit.rstrip("s")

    # 1. Rule 13 Check: Ambiguous regional units
    for amb in AMBIGUOUS_UNITS:
        if amb in clean_unit or amb in clean_base:
            return AreaNormalizationResult(
                original_value=value,
                original_unit=unit_raw,
                normalized_value_sqm=None,
                normalized_unit="unresolved",
                conversion_rule="RULE_13_AMBIGUOUS_REGIONAL_UNIT",
                conversion_factor=None,
                precision_decimals=precision,
                rounding_policy="NONE",
                is_ambiguous=True,
                ambiguity_status="REGIONALLY_VARIABLE_AMBIGUOUS_UNIT",
                formula=f"Unresolved: '{unit_raw}' definition varies by state/tehsil.",
                advisory_notice=(
                    f"The regional unit '{unit_raw}' is legally variable across districts. "
                    "Rule 13 prohibits automated normalization. Qualified revenue authority review required."
                ),
            )

    # 2. Standard SI and statutory factor lookup
    matched_factor: Decimal | None = None
    matched_key: str | None = None

    for key, factor in DECIMAL_FACTORS_TO_SQM.items():
        if clean_unit == key or clean_base == key or clean_unit.startswith(key):
            matched_factor = factor
            matched_key = key
            break

    if matched_factor is not None and matched_key is not None:
        val_dec = Decimal(str(value))
        converted_dec = val_dec * matched_factor
        quantize_pattern = Decimal("1." + "0" * precision)
        rounded_dec = converted_dec.quantize(quantize_pattern, rounding=ROUND_HALF_UP)
        result_float = float(rounded_dec)

        return AreaNormalizationResult(
            original_value=value,
            original_unit=unit_raw,
            normalized_value_sqm=result_float,
            normalized_unit="square_metre",
            conversion_rule=f"STANDARD_STATUTORY_CONVERSION_{matched_key.upper().replace(' ', '_')}",
            conversion_factor=float(matched_factor),
            precision_decimals=precision,
            rounding_policy="ROUND_HALF_UP",
            is_ambiguous=False,
            ambiguity_status="VERIFIED_STANDARD_UNIT",
            formula=f"{value} {unit_raw} × {float(matched_factor):.{precision}f} = {result_float} m²",
            advisory_notice="Standard statutory conversion applied. Original unit and extent preserved in audit trail.",
        )

    # 3. Unrecognized unit
    return AreaNormalizationResult(
        original_value=value,
        original_unit=unit_raw,
        normalized_value_sqm=None,
        normalized_unit="unresolved",
        conversion_rule="UNRECOGNIZED_UNIT_METRIC",
        conversion_factor=None,
        precision_decimals=precision,
        rounding_policy="NONE",
        is_ambiguous=True,
        ambiguity_status="UNRECOGNIZED_LAND_UNIT",
        formula=f"Unresolved: Unknown unit metric '{unit_raw}'.",
        advisory_notice=f"Unrecognized unit '{unit_raw}'. Officer review required to determine official conversion ratio.",
    )
