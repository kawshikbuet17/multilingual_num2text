"""The interface every language implements.

A new language subclasses Language, sets `code`, `words` and `lexicon`, and implements the five
abstract methods. Everything else (finding numbers in text, money, phones, ranges ...) is shared.
"""

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from decimal import Decimal
from enum import Enum

from .digits import parse_int, split_number, to_ascii_digits
from .lexicon import Currency, Lexicon
from .patterns import UNSIGNED_AMOUNT
from .words import Words

Rule = Callable[[str], str]

_NUMBER_TEXT = re.compile(rf"[-−+]?{UNSIGNED_AMOUNT}")


class NumberStyle(str, Enum):
    CARDINAL = "cardinal"
    DIGITWISE = "digitwise"
    AUTO = "auto"


class Language(ABC):
    code: str
    words: Words
    lexicon: Lexicon
    money_inflection_pattern: str = ""
    separate_number_words: bool = False

    def __init__(self, lexicon: Lexicon | None = None) -> None:
        """lexicon: replaces the language's built-in data, usually built with DEFAULT_LEXICON.extended(...)."""
        if lexicon is not None:
            self.lexicon = lexicon
        self._rules: list[Rule] | None = None

    @abstractmethod
    def to_cardinal(self, number: int) -> str:
        """2712 -> 'two thousand seven hundred twelve'"""

    @abstractmethod
    def to_ordinal(self, number: int) -> str:
        """21 -> 'twenty-first'"""

    @abstractmethod
    def to_year(self, year: int) -> str:
        """1971 -> 'nineteen seventy-one'"""

    @abstractmethod
    def to_date(self, day: int, month: int, year: str | None = None) -> str:
        """(10, 5, '2024') -> 'the tenth of May, twenty twenty-four'. year keeps its written digits."""

    @abstractmethod
    def to_time(self, hour: int, minute: int = 0, second: int | None = None, with_period: bool = False) -> str:
        """(15, 45) -> 'three forty-five PM'. hour is 0-23; with_period=True when the text said AM/PM."""

    def language_rules(self) -> list[Rule]:
        """Extra rules only this language needs (month names, ordinals ...).
        They run after codes and scaled money, before dates, times and phones."""
        return []

    def build_rules(self) -> list[Rule]:
        from .number_rules import NumberRules
        from .text_rules import TextRules

        text_rules, number_rules = TextRules(self), NumberRules(self)
        return [
            *text_rules.preparation_rules(),
            *number_rules.early_rules(),
            *self.language_rules(),
            *number_rules.shape_rules(),
            *number_rules.amount_rules(),
            *number_rules.plain_number_rules(),
            text_rules.cleanup_symbols,
        ]

    def to_mixed_fraction(self, whole: int, fraction: str) -> str:
        """(2, '½') -> 'two point five' by default. Languages override with natural forms."""
        decimal = {"½": "5", "¼": "25", "¾": "75"}[fraction]
        return self.spell_number(f"{whole}.{decimal}")

    def spell_scaled_amount(self, amount: str) -> str:
        """The number in '৳2.5 crore' or '$5 million'. Languages may override (Bangla: আড়াই)."""
        return self.spell_number(amount)

    @property
    def rules(self) -> list[Rule]:
        if self._rules is None:
            self._rules = self.build_rules()
        return self._rules

    def to_digitwise(self, text: str | int) -> str:
        spoken = []
        symbols = self.words.symbols
        for char in str(text):
            if char.isdecimal():
                spoken.append(self.words.digits[int(to_ascii_digits(char))])
            elif char in symbols:
                spoken.append(symbols[char])
        return " ".join(spoken)

    def to_decimal(self, integer: str, fraction: str) -> str:
        if self.lexicon.strip_decimal_trailing_zeros:
            fraction = to_ascii_digits(fraction).rstrip("0")
        whole = self.to_cardinal(parse_int(integer))
        if not fraction:
            return whole
        return f"{whole} {self.words.decimal_point} {self.to_digitwise(fraction)}"

    def spell_number(self, text: str) -> str:
        if not _NUMBER_TEXT.fullmatch(text.strip()):
            raise ValueError(f"Not a number: {text!r}")
        is_negative, integer, fraction = split_number(text)
        spoken = self.to_decimal(integer, fraction)
        return f"{self.words.negative} {spoken}" if is_negative else spoken

    def to_money(self, amount: str, currency: Currency) -> str:
        is_negative, integer, fraction = split_number(amount)
        fraction = fraction.rstrip("0")

        if len(fraction) > currency.minor_digits:
            spoken = f"{self.to_decimal(integer, fraction)} {currency.unit_for(2)}"
        else:
            major = parse_int(integer)
            minor = int(fraction.ljust(currency.minor_digits, "0")) if fraction else 0
            parts = []
            if major or not minor:
                parts.append(f"{self.to_cardinal(major)} {currency.unit_for(major)}")
            if minor:
                parts.append(f"{self.to_cardinal(minor)} {currency.subunit_for(minor)}")
            joiner = f" {self.words.money_joiner} " if self.words.money_joiner else " "
            spoken = joiner.join(parts)

        return f"{self.words.negative} {spoken}" if is_negative else spoken

    def to_percent(self, text: str) -> str:
        return f"{self.spell_number(text)} {self.words.percent}"

    def to_ratio(self, first: int, second: int) -> str:
        return f"{self.to_cardinal(first)} {self.words.ratio} {self.to_cardinal(second)}"

    def convert_text(self, text: str, keep: re.Pattern | None = None) -> str:
        """Write out every number in the text as words.

        keep: a pattern with one capturing group around the whole match, for parts that must
        pass through untouched, e.g. emotion tags like "[warm]".
        """
        if not text:
            return text
        if keep is None:
            return self._apply_rules(str(text))

        spoken = []
        for index, piece in enumerate(keep.split(str(text))):
            said = piece if index % 2 else self._apply_rules(piece)
            if said.strip():
                spoken.append(said.strip())
        return " ".join(spoken)

    def number_to_text(self, value: int | float | str, style: NumberStyle | str = NumberStyle.CARDINAL) -> str:
        """CARDINAL: 2712 as one number. DIGITWISE: digit by digit.
        AUTO: picks from the shape (0.../+... digit by digit, *123# as a code, currency as money).
        """
        text = _as_text(value)
        style = NumberStyle(style)
        if style is NumberStyle.DIGITWISE:
            return self.to_digitwise(text)
        if style is NumberStyle.AUTO:
            return self.convert_text(text)
        return self.spell_number(text)

    def _apply_rules(self, text: str) -> str:
        for rule in self.rules:
            text = rule(text)
        return text


def _as_text(value: int | float | str) -> str:
    if isinstance(value, float):
        return format(Decimal(repr(value)), "f")
    return str(value).strip()
