"""Digit helpers. Any Unicode decimal digit works: ASCII, Bangla, Devanagari, Arabic-Indic and so on."""

import re
import unicodedata

ZERO_DIGITS = "".join(
    chr(code) for code in range(0x10000) if chr(code).isdecimal() and unicodedata.digit(chr(code)) == 0
)

_INDIAN_GROUPING = re.compile(r"[0-9]{1,2}(?:,[0-9]{2})*,[0-9]{3}")
_INTERNATIONAL_GROUPING = re.compile(r"[0-9]{1,3}(?:,[0-9]{3})+")


def to_ascii_digits(text: str) -> str:
    return "".join(str(unicodedata.digit(char)) if char.isdecimal() else char for char in text)


def only_digits(text: str) -> str:
    return "".join(char for char in text if char.isdecimal())


def parse_int(text: str) -> int:
    digits = to_ascii_digits(only_digits(text))
    return int(digits) if digits else 0


def starts_with_zero(number: str) -> bool:
    return number[:1] in ZERO_DIGITS


def has_valid_grouping(number: str) -> bool:
    """True for plain digits, Indian grouping (12,34,567) or international grouping (123,456)."""
    number = to_ascii_digits(number)
    if "," not in number:
        return True
    return bool(_INDIAN_GROUPING.fullmatch(number) or _INTERNATIONAL_GROUPING.fullmatch(number))


def split_number(text: str) -> tuple[bool, str, str]:
    """'-১,২৫০.৫০' -> (True, '1250', '50'). Returns ASCII digits without commas."""
    text = to_ascii_digits(text.strip())
    is_negative = text[:1] in "-−"
    integer, _, fraction = text.lstrip("+-−").replace(",", "").partition(".")
    return is_negative, integer, fraction
