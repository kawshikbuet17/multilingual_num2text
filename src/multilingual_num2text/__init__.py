"""Convert numbers to words in several languages.

    from multilingual_num2text import convert_text, number_to_text, NumberStyle

    number_to_text(2712, "bn")                       # দুই হাজার সাতশত বারো
    number_to_text(2712, "en", "digitwise")          # two seven one two
    convert_text("Send ৳1,250.50 to 01711-123456", "en")
"""

import re

from .core import (
    Currency,
    Language,
    Lexicon,
    NumberStyle,
    Rule,
    Words,
    available_languages,
    get_language,
    register_language,
)
from .languages import BanglaLanguage, EnglishLanguage
from .languages.bangla.lexicon import LEXICON as BANGLA_LEXICON
from .languages.english.lexicon import LEXICON as ENGLISH_LEXICON

register_language(BanglaLanguage())
register_language(EnglishLanguage())


def convert_text(text: str, lang: str, keep: re.Pattern | None = None) -> str:
    """Write out every number in the text as words, in the given language."""
    return get_language(lang).convert_text(text, keep)


def number_to_text(value: int | float | str, lang: str, style: NumberStyle | str = NumberStyle.CARDINAL) -> str:
    """Speak one number. style: 'cardinal' (default), 'digitwise' or 'auto'."""
    return get_language(lang).number_to_text(value, style)


__all__ = [
    "BANGLA_LEXICON",
    "ENGLISH_LEXICON",
    "BanglaLanguage",
    "Currency",
    "EnglishLanguage",
    "Language",
    "Lexicon",
    "NumberStyle",
    "Rule",
    "Words",
    "available_languages",
    "convert_text",
    "get_language",
    "number_to_text",
    "register_language",
]
