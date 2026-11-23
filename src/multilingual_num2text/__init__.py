"""Convert numbers to words in several languages.

    from multilingual_num2text import convert_text, number_to_text, NumberStyle

    number_to_text(2712, lang="en")                      # two thousand seven hundred twelve
    number_to_text(2712, lang="en", style="digitwise")   # two seven one two
    number_to_text(2712, lang="bn")                      # দুই হাজার সাতশত বারো
    convert_text("Send $1,250.50 to 01711-123456", lang="en")
    convert_text("Pay $5 now. ৫০০ টাকা দিন।", lang="auto")   # each sentence in its own language
"""

import re
from collections.abc import Callable

from .core import (
    AUTO,
    Currency,
    Language,
    Lexicon,
    NumberStyle,
    Rule,
    Words,
    available_languages,
    detect_language,
    detect_sentence_languages,
    get_language,
    register_language,
    split_sentences,
    unregister_language,
)
from .languages import BanglaLanguage, EnglishLanguage
from .languages.bangla.lexicon import LEXICON as BANGLA_LEXICON
from .languages.english.lexicon import LEXICON as ENGLISH_LEXICON

register_language(BanglaLanguage())
register_language(EnglishLanguage())


def convert_text(
    text: str,
    lang: str,
    keep: re.Pattern | None = None,
    splitter: Callable[[str], list[str]] | None = None,
) -> str:
    """Write out every number in the text as words.

    lang: a language code such as "en" or "bn", or "auto" to pick the language of each sentence from its script.
          With "auto", a sentence written in a language that is not registered is kept exactly as it is.
    keep: parts to leave unchanged, such as tags like [warm]; one capturing group around the whole match.
    splitter: for "auto", your own function that splits the text into sentences (default: split_sentences).
    """
    if lang.lower() != AUTO:
        return get_language(lang).convert_text(text, keep)
    if not text:
        return text
    sentences = splitter(text) if splitter else split_sentences(text, ignore=keep)
    languages = detect_sentence_languages(sentences, ignore=keep)
    converted = (_convert_sentence(sentence, language, keep) for sentence, language in zip(sentences, languages))
    return " ".join(sentence for sentence in converted if sentence)


def number_to_text(value: int | float | str, lang: str, style: NumberStyle | str = NumberStyle.CARDINAL) -> str:
    """Write one number as words. style: 'cardinal' (default), 'digitwise' or 'auto'.

    lang may be "auto"; a number written in digits of a language that is not registered is returned unchanged.
    """
    if lang.lower() == AUTO:
        lang = detect_language(str(value))
        if lang is None:
            return str(value).strip()
    return get_language(lang).number_to_text(value, style)


def _convert_sentence(sentence: str, lang: str | None, keep: re.Pattern | None) -> str:
    return sentence.strip() if lang is None else get_language(lang).convert_text(sentence, keep)


__all__ = [
    "AUTO",
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
    "detect_language",
    "detect_sentence_languages",
    "get_language",
    "number_to_text",
    "register_language",
    "split_sentences",
    "unregister_language",
]
