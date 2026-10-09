"""
Fictional Indian names generator for 100% synthetic landowner personas.
Adheres strictly to synthetic data policy: No real persons, all personas fictional.
"""

from __future__ import annotations

import random

GIVEN_NAMES = [
    "Arjun", "Ramesh", "Meera", "Suresh", "Lakshmi", "Anand", "Deepa", "Vijay",
    "Pooja", "Girish", "Sunita", "Raghav", "Kavitha", "Manjunath", "Geetha",
    "Pradeep", "Rekha", "Naveen", "Shobha", "Santosh", "Divya", "Praveen",
    "Asha", "Chetan", "Bhavya", "Harish", "Mamatha", "Vinay", "Suma", "Kiran",
    "Vidya", "Mahesh", "Sujatha", "Venkatesh", "Roopa", "Shankar", "Sudha",
    "Rajesh", "Kamala", "Basavaraj", "Vimala", "Chandrashekar", "Pushpa", "Ravi",
    "Gowramma", "Shivakumar", "Sharada", "Jagadish", "Parvathi", "Ananth"
]

SURNAMES = [
    "Rao", "Kumar", "Gowda", "Patil", "Sharma", "Hegde", "Bhat", "Kulkarni",
    "Deshmukh", "Shetty", "Reddy", "Nayak", "Joshi", "Naik", "Prasad", "Murthy",
    "Acharya", "Hebbar", "Karanth", "Kamath", "Pai", "Shenoy", "Bhandary",
    "Somayaji", "Shastry", "Adiga", "Deshpande", "Nadkarni", "Sonavane", "Babu"
]

RELATIONS = [
    ("S/o", "Son of"),
    ("D/o", "Daughter of"),
    ("W/o", "Wife of"),
]

TRANSLITERATION_MAP = {
    "Rao": ["Row", "Ravu"],
    "Gowda": ["Gowdar", "Gouda"],
    "Hegde": ["Hedge", "Heggade"],
    "Kumar": ["Kumaar", "Koomar"],
    "Bhat": ["Bhatt", "Bhatta"],
    "Shetty": ["Setti", "Shettigar"],
    "Murthy": ["Moorthy", "Murthi"],
    "Prasad": ["Prasada", "Prasaad"],
    "Arjun": ["Arjuna"],
    "Suresh": ["Suresha"],
    "Ramesh": ["Ramesha"],
    "Mahesh": ["Mahesha"],
    "Deepa": ["Dipa"],
    "Sunita": ["Suneetha", "Suneeta"],
}


def generate_synthetic_name(rng: random.Random) -> dict[str, Any]:
    given = rng.choice(GIVEN_NAMES)
    surname = rng.choice(SURNAMES)
    full_name = f"{given} {surname}"

    # Generate variants
    variants = []
    # 1. Reversed order
    variants.append(f"{surname} {given}")

    # 2. Transliteration variant
    alt_surname = rng.choice(TRANSLITERATION_MAP.get(surname, [surname]))
    alt_given = rng.choice(TRANSLITERATION_MAP.get(given, [given]))
    if alt_surname != surname or alt_given != given:
        variants.append(f"{alt_given} {alt_surname}")

    # 3. Honorific / parentage variant
    rel_code, _ = rng.choice(RELATIONS)
    parent_given = rng.choice(GIVEN_NAMES)
    variants.append(f"{full_name} {rel_code} {parent_given} {surname}")

    return {
        "display_name": full_name,
        "given_name": given,
        "surname": surname,
        "variants": variants,
    }
