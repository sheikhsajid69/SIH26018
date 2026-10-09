"""
Name normalization and fuzzy matching utilities for party identification.
"""

from __future__ import annotations

import re


HONORIFICS = {
    "shri", "sri", "smt", "smt.", "shrimati", "mr", "mr.", "mrs", "mrs.", "dr", "dr.",
    "late", "s/o", "d/o", "w/o", "c/o", "bin", "b/o"
}


def normalize_name(raw_name: str) -> str:
    """
    Normalizes a name string by removing honorifics, extra whitespace,
    and punctuation for robust canonical comparison.
    """
    if not raw_name:
        return ""

    # Lowercase and clean punctuation
    cleaned = raw_name.lower().replace(",", " ").replace(".", " ").replace("-", " ")
    tokens = [t.strip() for t in cleaned.split() if t.strip()]

    # Filter out known honorifics and relational markers
    filtered = [t for t in tokens if t not in HONORIFICS]
    return " ".join(filtered)


def token_set_match(name_a: str, name_b: str) -> bool:
    """Check if all key tokens from name_a match name_b regardless of ordering."""
    norm_a = normalize_name(name_a)
    norm_b = normalize_name(name_b)
    if not norm_a or not norm_b:
        return False
    set_a = set(norm_a.split())
    set_b = set(norm_b.split())
    return set_a == set_b or set_a.issubset(set_b) or set_b.issubset(set_a)
