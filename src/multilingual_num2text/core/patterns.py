"""Regex building blocks shared by the rule classes. \\d matches a digit in any script."""

import re

NUMBER = r"\d(?:\d|,(?=\d))*"
UNSIGNED_AMOUNT = rf"{NUMBER}(?:\.\d+)?"
NEGATIVE_SIGN = r"(?P<sign>(?:^|(?<=[\s(]))[-−])?"
NOT_DIGIT_BEFORE = r"(?<!\d)"
NOT_DIGIT_AFTER = r"(?!\d)"
NOT_NUMBER_BEFORE = r"(?<![\d.,])"
NOT_LETTER_AFTER = r"(?![^\W\d_])"
WORD_CHARS = r"\wऀ-෿"


def alternation(options) -> str:
    return "|".join(re.escape(option) for option in sorted(options, key=len, reverse=True))


def compile_if_any(options, build_pattern, flags: int = 0) -> re.Pattern | None:
    """Compiles build_pattern(alternation) only when there is something to match."""
    options = list(options)
    return re.compile(build_pattern(alternation(options)), flags) if options else None
