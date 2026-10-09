"""
Tests for Area Extent Normalization Module and Rule 13 Ambiguous Unit Defense.
"""

import pytest
from landsync_datasets.normalization.area import (
    normalize_area,
    parse_area_text,
    DECIMAL_FACTORS_TO_SQM,
    AMBIGUOUS_UNITS,
)


def test_standard_acre_conversion():
    res = normalize_area(2.40, "acre")
    assert not res.is_ambiguous
    assert res.normalized_value_sqm is not None
    # 2.40 * 4046.8564224 = 9712.4554
    assert pytest.approx(res.normalized_value_sqm, 0.01) == 9712.4554
    assert "ACRE" in res.conversion_rule


def test_standard_guntha_conversion():
    res = normalize_area(40.0, "guntha")
    assert not res.is_ambiguous
    # 40 gunthas = 1 acre = 4046.8564 m²
    assert pytest.approx(res.normalized_value_sqm, 0.01) == 4046.8564


def test_standard_cent_conversion():
    res = normalize_area(100.0, "cent")
    assert not res.is_ambiguous
    # 100 cents = 1 acre = 4046.8564 m²
    assert pytest.approx(res.normalized_value_sqm, 0.01) == 4046.8564


def test_standard_hectare_conversion():
    res = normalize_area(1.5, "hectare")
    assert not res.is_ambiguous
    assert pytest.approx(res.normalized_value_sqm, 0.01) == 15000.0


def test_standard_sqft_conversion():
    res = normalize_area(1000.0, "sq ft")
    assert not res.is_ambiguous
    assert pytest.approx(res.normalized_value_sqm, 0.01) == 92.9030


def test_rule_13_ambiguous_bigha_defense():
    """Rule 13 invariant: Ambiguous regional units must never be automatically converted."""
    for amb_unit in ["bigha", "biswa", "katha", "kanal", "marla", "ground"]:
        res = normalize_area(2.5, amb_unit)
        assert res.is_ambiguous
        assert res.normalized_value_sqm is None
        assert res.conversion_rule == "RULE_13_AMBIGUOUS_REGIONAL_UNIT"
        assert "Rule 13" in res.advisory_notice


def test_parse_area_text():
    val, unit = parse_area_text("2.40 acre")
    assert val == 2.40
    assert unit == "acre"

    val2, unit2 = parse_area_text("40,468.56 sq m")
    assert val2 == 40468.56
    assert unit2 == "sq m"

    val3, unit3 = parse_area_text("3.5 bigha")
    assert val3 == 3.5
    assert unit3 == "bigha"
