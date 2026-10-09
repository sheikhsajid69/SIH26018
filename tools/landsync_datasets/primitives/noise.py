"""
Deterministic OCR and transcription noise simulation.
Simulates realistic optical scan degradations without calling real OCR engines.
"""

from __future__ import annotations

import random

# Common OCR confusion pairs in printed and typed documents
CHAR_CONFUSIONS = {
    "0": "O",
    "O": "0",
    "1": "l",
    "l": "1",
    "I": "1",
    "8": "B",
    "B": "8",
    "5": "S",
    "S": "5",
    "2": "Z",
    "Z": "2",
    "/": "|",
    ".": ",",
    ",": ".",
    "-": "_",
}


def apply_ocr_noise(text: str, rng: random.Random, rate: float = 0.15) -> tuple[str, str]:
    """
    Applies simulated OCR noise to text.
    Returns (noisy_text, noise_type_applied).
    """
    if not text:
        return text, "NONE"

    chars = list(text)
    noise_applied = "NONE"

    for i in range(len(chars)):
        c = chars[i]
        if rng.random() < rate:
            if c in CHAR_CONFUSIONS:
                chars[i] = CHAR_CONFUSIONS[c]
                noise_applied = "CHAR_SUBSTITUTION"
            elif c.isalpha() and rng.random() < 0.3:
                # Slight casing variation
                chars[i] = c.lower() if c.isupper() else c.upper()
                noise_applied = "CASE_INVERSION"
            elif c.isspace() and rng.random() < 0.4:
                # Multiple spaces or dropped space
                chars[i] = "  " if rng.random() < 0.5 else ""
                noise_applied = "WHITESPACE_VARIATION"

    result = "".join(chars).strip()
    if not result:
        result = text
        noise_applied = "NONE"

    return result, noise_applied
