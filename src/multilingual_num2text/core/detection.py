"""Picks the language of a text from its script, for lang="auto"."""

import re
import unicodedata
from functools import lru_cache

from .registry import available_languages, get_language

AUTO = "auto"
DEFAULT_LANGUAGE = "en"
UNSUPPORTED = "unsupported"

FALLBACK_END_MARKS = (".", "!", "?")
_ADDRESS = re.compile(r"\S+@\S+|(?:https?://|www\.)\S+|[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}(?![\w.])", re.IGNORECASE)
_ASCII_DIGITS = "0123456789"


def detect_language(text: str, default: str = DEFAULT_LANGUAGE, ignore: re.Pattern | None = None) -> str | None:
    """The language the text is written in, or None when it is written in a language that is not registered.

    Words decide: the language with the most words wins. Acronyms (OTP, ATM), emails and web addresses do not count.
    On a tie, the language whose own digits appear wins (৳৫০০ is Bangla), then the one whose word comes first.
    Without words, digits decide: ASCII digits count for the default language, the most digits win, a tie goes
    to the first digit. Nothing to decide by: the default.
    'Send $5' -> 'en', 'আপনার balance ৳৫০০' -> 'bn', '50০০' -> 'en', 'مرحبا 500' -> None, '' -> default.
    ignore: parts that do not count, such as tags passed as keep= to convert_text.
    """
    language, _ = _decide(_prepare(text, ignore), default)
    return language


def detect_sentence_languages(sentences: list[str], default: str = DEFAULT_LANGUAGE, ignore: re.Pattern | None = None) -> list[str | None]:
    """The language of each sentence. A sentence without words (a bare number, a list marker) takes the language
    of the nearest sentence before it that has words, else the nearest after it, else its own digits decide."""
    decisions = [_decide(_prepare(sentence, ignore), default) for sentence in sentences]
    languages = []
    for index, (language, by_words) in enumerate(decisions):
        if not by_words:
            context = _nearest_worded(decisions, index)
            if context is not _NO_CONTEXT:
                language = context
        languages.append(language)
    return languages


def split_sentences(text: str, ignore: re.Pattern | None = None) -> list[str]:
    """Splits at line breaks and at the sentence end marks of the registered languages (। . ! ?) before a space.

    The marks and abbreviations come from each language's Lexicon (sentence_end_marks, abbreviations), so they
    can be extended with Lexicon.extended(). A dot ends a sentence only when the next sentence starts with a
    capital or another script, and never after an abbreviation (Mr., ডা.), after a currency symbol before a
    digit (Tk. ৫০০) or after a bare list number (১. Open app).
    'Pay $5 now. ৫০০ টাকা দিন।' -> ['Pay $5 now. ', '৫০০ টাকা দিন।']; 'Dec. 25th', 'Mr. Karim' and '1.5' stay whole.
    """
    masked = _mask(text, ignore)
    sentences, start = [], 0
    for match in _sentence_end_pattern(_end_marks()).finditer(masked):
        mark = match.group().strip()[:1]
        if mark and _is_list_marker(masked[start:match.start()]):
            continue
        if mark == "." and not _starts_new_sentence(masked, match.start(), match.end()):
            continue
        sentences.append(text[start:match.end()])
        start = match.end()
    sentences.append(text[start:])
    return [sentence for sentence in sentences if sentence.strip()]


_NO_CONTEXT = object()


def _nearest_worded(decisions: list[tuple[str | None, bool]], index: int):
    for step in (-1, 1):
        position = index + step
        while 0 <= position < len(decisions):
            language, by_words = decisions[position]
            if by_words:
                return language
            position += step
    return _NO_CONTEXT


def _prepare(text: str, ignore: re.Pattern | None) -> str:
    """Leaves out what says nothing about the language: ignored parts, web and email addresses, abbreviations."""
    return _mask(_mask(_mask(text, ignore), _ADDRESS), _abbreviation_pattern(_abbreviations()))


def _decide(text: str, default: str) -> tuple[str | None, bool]:
    """(language, decided by words)."""
    words = _count_words(text)
    if words:
        winner = _pick(words, text)
        return (None if winner == UNSUPPORTED else winner), True
    digits = _count_digits(text, default)
    if not digits:
        return default, False
    winner = max(digits, key=lambda owner: (digits[owner][0], -digits[owner][1]))
    return (None if winner == UNSUPPORTED else winner), False


def _pick(words: dict[str, list[int]], text: str) -> str:
    most = max(count for count, _ in words.values())
    tied = [owner for owner, (count, _) in words.items() if count == most]
    if len(tied) == 1:
        return tied[0]
    own_digits = {owner: _count_own_digits(text, owner) for owner in tied}
    if max(own_digits.values()) > 0 and list(own_digits.values()).count(max(own_digits.values())) == 1:
        return max(own_digits, key=own_digits.get)
    return min(tied, key=lambda owner: words[owner][1])


def _count_words(text: str) -> dict[str, list[int]]:
    """owner -> [word count, index of the first word]. Acronyms like OTP or ATM are left out."""
    tally = {}
    for match in _word_spans(text):
        word = text[match[0]:match[1]]
        if len(word) > 1 and word.isascii() and word.isupper():
            continue
        owner = next((owner for owner in map(_owner, word) if owner), UNSUPPORTED)
        _add(tally, owner, match[0])
    return tally


def _word_spans(text: str):
    start = None
    for index, char in enumerate(text):
        if _is_letter(char):
            if start is None:
                start = index
        elif start is not None:
            yield start, index
            start = None
    if start is not None:
        yield start, len(text)


def _count_digits(text: str, default: str) -> dict[str, list[int]]:
    """owner -> [count, first index] for every digit. ASCII digits belong to the default language."""
    tally = {}
    for index, char in enumerate(text):
        if char.isdecimal():
            _add(tally, default if char in _ASCII_DIGITS else _owner(char) or UNSUPPORTED, index)
    return tally


def _count_own_digits(text: str, owner: str) -> int:
    """Digits written in the language's own script (not ASCII, which every language uses)."""
    return sum(1 for char in text if char.isdecimal() and char not in _ASCII_DIGITS and _owner(char) == owner)


def _add(tally: dict[str, list[int]], owner: str, index: int) -> None:
    if owner in tally:
        tally[owner][0] += 1
    else:
        tally[owner] = [1, index]


def _is_letter(char: str) -> bool:
    """Letters and the vowel signs that attach to them (Bangla া, ি ...). Digits and signs like ৳ are not letters."""
    return unicodedata.category(char)[0] in "LM"


def _is_list_marker(segment: str) -> bool:
    """'১' or '2' before the dot: a numbered list item, the sentence continues after it."""
    stripped = segment.strip()
    return bool(stripped) and stripped.isdecimal()


def _owner(char: str) -> str | None:
    """The registered language whose script contains the character, UNSUPPORTED for other letters, else None."""
    for code in available_languages():
        script = get_language(code).script
        if script and _script_pattern(script).match(char):
            return code
    return UNSUPPORTED if _is_letter(char) else None


@lru_cache(maxsize=None)
def _script_pattern(script: str) -> re.Pattern:
    return re.compile(f"[{script}]")


def _mask(text: str, ignore: re.Pattern | None) -> str:
    """Blanks out ignored parts without moving anything, so positions still match the original text."""
    return ignore.sub(lambda match: " " * len(match.group()), text) if ignore else text


def _starts_new_sentence(text: str, dot: int, next_start: int) -> bool:
    words_before = text[: dot + 1].split()
    if words_before and words_before[-1].lower() in {abbreviation.lower() for abbreviation in _abbreviations()}:
        return False
    next_char = next((char for char in text[next_start:] if char.isalnum()), None)
    if next_char is None:
        return True
    if next_char.isdecimal() and _ends_with_currency_symbol(text[: dot + 1]):
        return False
    if next_char.isupper():
        return True
    next_script = _owner(next_char)
    return next_script is not None and next_script != _owner_of_last_letter(text[:dot])


def _ends_with_currency_symbol(text: str) -> bool:
    """'Tk.', 'Rs.' or 'BDT.' before the dot: the amount follows, it is not the end of a sentence."""
    words = text.split()
    if not words:
        return False
    symbols = _currency_symbols()
    return words[-1] in symbols or words[-1].rstrip(".") in symbols


def _end_marks() -> tuple[str, ...]:
    marks = {mark for code in available_languages() for mark in get_language(code).lexicon.sentence_end_marks}
    return tuple(sorted(marks)) or FALLBACK_END_MARKS


def _abbreviations() -> tuple[str, ...]:
    return tuple(sorted({word for code in available_languages() for word in get_language(code).lexicon.abbreviations}))


@lru_cache(maxsize=None)
def _sentence_end_pattern(marks: tuple[str, ...]) -> re.Pattern:
    alternatives = "|".join(re.escape(mark) for mark in sorted(marks, key=len, reverse=True))
    return re.compile(rf"(?:{alternatives})+(?:\s+|$)|\n+")


@lru_cache(maxsize=None)
def _abbreviation_pattern(abbreviations: tuple[str, ...]) -> re.Pattern | None:
    if not abbreviations:
        return None
    alternatives = "|".join(re.escape(word) for word in sorted(abbreviations, key=len, reverse=True))
    return re.compile(rf"(?<![^\W\d_])(?:{alternatives})", re.IGNORECASE)


def _currency_symbols() -> set[str]:
    return {
        symbol
        for code in available_languages()
        for currency in get_language(code).lexicon.currencies
        for symbol in (*currency.symbols, *currency.suffix_symbols)
    }


def _owner_of_last_letter(text: str) -> str | None:
    for char in reversed(text):
        owner = _owner(char)
        if owner:
            return owner
    return None
