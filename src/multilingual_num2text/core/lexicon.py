"""Per-language data and settings. Each language fills one Lexicon."""

from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class Currency:
    """symbols may come before or after the amount (৳500, 500 BDT); suffix_symbols only after (500 টাকা).
    subunit is None for currencies without a fractional unit (yen, won); minor_digits is 3 for dinars like KWD.
    """

    unit: str
    subunit: str | None
    symbols: tuple[str, ...] = ()
    suffix_symbols: tuple[str, ...] = ()
    unit_plural: str | None = None
    subunit_plural: str | None = None
    code: str = ""
    minor_digits: int = 2

    def unit_for(self, count: int) -> str:
        return self.unit_plural if count != 1 and self.unit_plural else self.unit

    def subunit_for(self, count: int) -> str:
        return self.subunit_plural if count != 1 and self.subunit_plural else self.subunit


@dataclass(frozen=True)
class Lexicon:
    """Data and settings for one language.

    digitwise_numbers: numbers always read digit by digit wherever they appear (hotlines, short codes).
    fixed_phrases: written -> spoken, matched case-insensitively ("24/7").
    word_replacements: plain text replacements applied first.
    removed_patterns: regexes deleted before reading (e.g. citation tags like [Source 1]).
    acronyms / domain_words / email_name_words: how to pronounce those parts.
    """

    currencies: tuple[Currency, ...] = ()
    digitwise_numbers: tuple[str, ...] = ()
    fixed_phrases: dict[str, str] = field(default_factory=dict)
    word_replacements: dict[str, str] = field(default_factory=dict)
    removed_patterns: tuple[str, ...] = ()
    acronyms: dict[str, str] = field(default_factory=dict)
    domain_words: dict[str, str] = field(default_factory=dict)
    bare_domain_endings: tuple[str, ...] = ("com", "net", "org", "gov", "edu", "bd", "info", "io")
    email_name_words: dict[str, str] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)
    magnitudes: dict[str, int] = field(
        default_factory=lambda: {"k": 1_000, "K": 1_000, "M": 1_000_000, "bn": 1_000_000_000}
    )
    scale_words: tuple[str, ...] = ()
    year_markers_after: tuple[str, ...] = ()
    year_markers_before: tuple[str, ...] = ()
    digitwise_min_length: int = 10
    phone_max_digits: int = 15
    phone_min_digits_after_plus: int = 6
    strip_decimal_trailing_zeros: bool = True

    def extended(self, **changes) -> "Lexicon":
        """A copy with project data added: dicts are merged, tuples appended, other fields replaced.

        BANGLA_LEXICON.extended(digitwise_numbers=("999",), domain_words={"example": "এক্সাম্পল"})
        """
        merged = {}
        for name, value in changes.items():
            current = getattr(self, name)
            if isinstance(current, dict):
                merged[name] = {**current, **value}
            elif isinstance(current, tuple):
                merged[name] = (*current, *value)
            else:
                merged[name] = value
        return replace(self, **merged)
