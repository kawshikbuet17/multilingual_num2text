"""Built-in Bangla data. Add project data (hotlines, brand names ...) with LEXICON.extended(...), not here."""

from ...core.lexicon import Lexicon
from .currencies import CURRENCIES

LEXICON = Lexicon(
    currencies=CURRENCIES,
    fixed_phrases={
        "24/7": "চব্বিশ ঘণ্টা সাত দিন",
    },
    word_replacements={
        " + ": " এবং ",
    },
    acronyms={
        "ATM": "এটিএম",
        "OTP": "ওটিপি",
        "PIN": "পিন",
        "SMS": "এসএমএস",
        "NID": "এনআইডি",
    },
    domain_words={
        "www": "ডাব্লিউ ডাব্লিউ ডাব্লিউ",
        "com": "কম",
        "net": "নেট",
        "org": "অর্গ",
        "gov": "গভ",
        "edu": "এডু",
        "info": "ইনফো",
        "io": "আইও",
        "bd": "বিডি",
    },
    units={
        "kb": "কেবি",
        "mb": "এমবি",
        "gb": "জিবি",
        "tb": "টিবি",
        "km": "কিলোমিটার",
        "cm": "সেন্টিমিটার",
        "mm": "মিলিমিটার",
        "kg": "কেজি",
        "ml": "মিলি",
        "hr": "ঘণ্টা",
        "hrs": "ঘণ্টা",
        "min": "মিনিট",
        "mins": "মিনিট",
        "sec": "সেকেন্ড",
        "secs": "সেকেন্ড",
        "°c": "ডিগ্রি সেলসিয়াস",
        "°f": "ডিগ্রি ফারেনহাইট",
        "°": "ডিগ্রি",
    },
    scale_words=("হাজার", "লাখ", "লক্ষ", "কোটি"),
    year_markers_after=("সাল", "সন", "খ্রিস্টাব্দ", "খ্রিষ্টাব্দ", "বঙ্গাব্দ", "হিজরি"),
)

COLLOQUIAL_FRACTION_NOUNS = (
    "হাজার", "লাখ", "লক্ষ", "কোটি",
    "ঘণ্টা", "মিনিট", "দিন", "মাস", "বছর",
    "কেজি", "লিটার", "কিলোমিটার", "কিলো",
)
