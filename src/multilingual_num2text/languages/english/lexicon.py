"""Built-in English data. Add project data (hotlines, brand names ...) with LEXICON.extended(...), not here."""

from ...core.lexicon import Lexicon
from .currencies import CURRENCIES

LEXICON = Lexicon(
    currencies=CURRENCIES,
    fixed_phrases={"24/7": "twenty-four seven"},
    word_replacements={" + ": " plus "},
    domain_words={"www": "w w w"},
    units={
        "km": "kilometers",
        "kg": "kilograms",
        "hr": "hours",
        "hrs": "hours",
        "min": "minutes",
        "mins": "minutes",
        "sec": "seconds",
        "secs": "seconds",
        "°c": "degrees Celsius",
        "°f": "degrees Fahrenheit",
        "°": "degrees",
    },
    scale_words=("thousand", "million", "billion", "trillion", "lakh", "crore"),
    year_markers_after=("AD", "BC", "CE", "BCE"),
    year_markers_before=("in", "since", "until", "year"),
)
