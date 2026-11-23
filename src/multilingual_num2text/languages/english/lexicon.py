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
    duration_words=(
        "month", "months", "day", "days", "week", "weeks", "year", "years",
        "installment", "installments", "instalment", "instalments", "hour", "hours", "minute", "minutes",
        "মাস", "দিন", "বছর", "সপ্তাহ", "কিস্তি",
    ),
    digitwise_after=("OTP", "PIN", "code", "ID", "TrxID", "TxnID", "reference", "ref"),
    sentence_end_marks=(".", "!", "?"),
    abbreviations=(
        "Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "Sr.", "Jr.", "St.", "Mt.", "No.", "Nos.", "vs.", "etc.", "e.g.", "i.e.",
        "a.m.", "p.m.", "approx.", "dept.", "est.", "fig.", "Inc.", "Ltd.", "Co.", "Corp.", "U.S.", "U.K.",
        "Jan.", "Feb.", "Mar.", "Apr.", "Jun.", "Jul.", "Aug.", "Sep.", "Sept.", "Oct.", "Nov.", "Dec.",
    ),
    year_markers_after=("AD", "BC", "CE", "BCE"),
    year_markers_before=("in", "since", "until", "year"),
)
