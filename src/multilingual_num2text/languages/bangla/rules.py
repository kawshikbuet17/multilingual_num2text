"""Rules only Bangla needs: spoken times (সকাল ১০.৩০ টায়), dates with month names, ১ম/২য় ordinals,
১লা/২১শে date days and দেড়/আড়াই/সাড়ে fractions."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ...core.digits import parse_int
from ...core.patterns import NOT_DIGIT_BEFORE, NOT_NUMBER_BEFORE, alternation
from . import vocabulary as vocab
from .lexicon import COLLOQUIAL_FRACTION_NOUNS

if TYPE_CHECKING:
    from ...core.language import Rule
    from .language import BanglaLanguage

BANGLA_LETTER = r"[ঀ-৥ৰ-৿]"

_ENGLISH_MONTHS = {**vocab.ENGLISH_MONTH_NAMES, **{name.upper(): index for name, index in vocab.ENGLISH_MONTH_NAMES.items()}}
_MONTH = (
    rf"(?P<month>{alternation((*vocab.MONTHS, *vocab.MONTH_SPELLING_VARIANTS, *vocab.CALENDAR_MONTHS, *_ENGLISH_MONTHS))})"
    rf"(?P<inflection>{alternation(vocab.MONTH_INFLECTIONS)})?(?!{BANGLA_LETTER}|[A-Za-z])"
)
_DAY_BEFORE_MONTH = re.compile(rf"{NOT_DIGIT_BEFORE}(?P<day>\d{{1,2}})\s?{_MONTH}")
_YEAR_AFTER_MONTH = re.compile(rf"{_MONTH}\s(?P<year>\d{{4}})(?!\d|[.,]\d)")
_TIME_WITH_SUFFIX = re.compile(
    rf"(?:(?P<period>{alternation(vocab.DAY_PERIOD_WORDS)})\s)?(?<![\d:.])(?P<hour>\d{{1,2}})[:.](?P<minute>\d{{2}})"
    rf"\s?(?P<suffix>{alternation(vocab.TIME_SUFFIXES)})(?!{BANGLA_LETTER})"
)
_TIME_AFTER_PERIOD = re.compile(
    rf"(?P<period>{alternation(vocab.DAY_PERIOD_WORDS)})\s(?<![\d:.])(?P<hour>\d{{1,2}})[:.](?P<minute>\d{{2}})(?![\d:.])"
)
_ORDINAL = re.compile(rf"{NOT_DIGIT_BEFORE}(\d+)(?:ম|য়|র্থ|ষ্ঠ|তম)(?!{BANGLA_LETTER})")
_DATE_DAY = re.compile(rf"{NOT_DIGIT_BEFORE}(\d{{1,2}})(?:লা|রা|ঠা|শে)(?!{BANGLA_LETTER})")
_COLLOQUIAL_FRACTION = re.compile(
    rf"{NOT_NUMBER_BEFORE}(\d+)\.(\d+)(?=\s?(?:{alternation(COLLOQUIAL_FRACTION_NOUNS)}))"
)


class BanglaRules:
    def __init__(self, language: BanglaLanguage) -> None:
        self.language = language

    def rules(self) -> list[Rule]:
        return [
            self.read_spoken_times,
            self.read_month_dates,
            self.read_ordinals,
            self.read_date_days,
            self.read_colloquial_fractions,
        ]

    def read_spoken_times(self, text: str) -> str:
        """সকাল ১০.৩০ টায় -> সকাল দশটা ত্রিশ মিনিটে, ১০:০০ টার -> দশটার, রাত ১০.৩০ -> রাত দশটা ত্রিশ মিনিট.

        A period word (সকাল, রাত ...) or a টা/টায়/টার after the number makes it a time, also with a dot.
        """
        text = _TIME_WITH_SUFFIX.sub(self._speak_time, text)
        return _TIME_AFTER_PERIOD.sub(self._speak_time, text)

    def _speak_time(self, match: re.Match) -> str:
        hour, minute = parse_int(match["hour"]), parse_int(match["minute"])
        period = match["period"]
        if hour > 23 or minute > 59 or (period and hour == 0):
            return match.group()
        spoken = self.language.to_time(hour % 12 or 12, minute) if period else self.language.to_time(hour, minute)
        suffix = match.groupdict().get("suffix")
        if suffix:
            endings = vocab.TIME_SUFFIX_AFTER_MINUTES if minute else vocab.TIME_SUFFIX_ON_THE_HOUR
            spoken += endings[suffix]
        return f"{period} {spoken}" if period else spoken

    def read_month_dates(self, text: str) -> str:
        """১০ মে ২০২৪ -> দশই মে দুই হাজার চব্বিশ, ১৫ শ্রাবণ -> পনেরোই শ্রাবণ, ৩১ ডিসেম্বরের -> একত্রিশে ডিসেম্বরের,
        10 May 2024 -> দশই মে দুই হাজার চব্বিশ (English month names become Bangla)."""
        text = _DAY_BEFORE_MONTH.sub(self._speak_day_before_month, text)
        return _YEAR_AFTER_MONTH.sub(
            lambda match: f"{self._month_name(match)} {self.language.to_year(parse_int(match['year']))}",
            text,
        )

    def _speak_day_before_month(self, match: re.Match) -> str:
        day = parse_int(match["day"])
        if not 1 <= day <= 31:
            return match.group()
        return f"{self.language.to_date_day(day)} {self._month_name(match)}"

    @staticmethod
    def _month_name(match: re.Match) -> str:
        month = match["month"]
        if month in _ENGLISH_MONTHS:
            month = vocab.MONTHS[_ENGLISH_MONTHS[month] - 1]
        return month + (match["inflection"] or "")

    def read_ordinals(self, text: str) -> str:
        """১ম -> প্রথম, ২য় -> দ্বিতীয়, ১১তম -> এগারোতম"""
        return _ORDINAL.sub(lambda match: self.language.to_ordinal(parse_int(match[1])), text)

    def read_date_days(self, text: str) -> str:
        """১লা -> পহেলা, ২রা -> দোসরা, ২১শে -> একুশে"""
        return _DATE_DAY.sub(self._speak_date_day, text)

    def _speak_date_day(self, match: re.Match) -> str:
        day = parse_int(match[1])
        return self.language.to_date_day(day) if 1 <= day <= 31 else match.group()

    def read_colloquial_fractions(self, text: str) -> str:
        """২.৫ লাখ -> আড়াই লাখ, ১.৫ ঘণ্টা -> দেড় ঘণ্টা, ৩.৫ কোটি -> সাড়ে তিন কোটি"""
        return _COLLOQUIAL_FRACTION.sub(
            lambda match: self.language.to_colloquial_fraction(parse_int(match[1]), match[2]) or match.group(),
            text,
        )
