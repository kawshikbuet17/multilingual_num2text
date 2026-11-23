"""Rules only English needs: dates with month names, decades (1990s, '80s) and 1st/2nd/21st ordinals."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ...core.digits import parse_int
from ...core.patterns import alternation
from . import vocabulary as vocab

if TYPE_CHECKING:
    from ...core.language import Rule
    from .language import EnglishLanguage

_MONTH_FORMS = {name: index for index, name in enumerate(vocab.MONTHS, start=1)}
_MONTH_FORMS.update({short: vocab.MONTHS.index(full) + 1 for short, full in vocab.MONTH_ABBREVIATIONS.items()})
_MONTH_FORMS.update({name.upper(): index for name, index in list(_MONTH_FORMS.items())})
_MONTH = rf"(?P<month>{alternation(_MONTH_FORMS)})\.?(?![A-Za-z])"
_ORDINAL_SUFFIX = r"(?:st|nd|rd|th)?"
_YEAR = r"(?:,?\s(?P<year>\d{4})(?!\d|[.,]\d))?"

_DAY_BEFORE_MONTH = re.compile(rf"(?<!\w)(?P<day>\d{{1,2}}){_ORDINAL_SUFFIX}\s(?:of\s)?{_MONTH}{_YEAR}")
_MONTH_BEFORE_DAY = re.compile(rf"(?<![A-Za-z]){_MONTH}\s(?P<day>\d{{1,2}}){_ORDINAL_SUFFIX}(?!\d|[A-Za-z]|:\d){_YEAR}")
_MONTH_BEFORE_YEAR = re.compile(rf"(?<![A-Za-z]){_MONTH},?\s(?P<year>\d{{4}})(?!\d|[.,]\d)")
_DECADE = re.compile(r"(?<![\w'])'?(\d{4}|\d{2})s(?![A-Za-z])")
_ORDINAL = re.compile(r"(?<!\w)(\d+)(?:st|nd|rd|th)(?![A-Za-z])", re.IGNORECASE)


class EnglishRules:
    def __init__(self, language: EnglishLanguage) -> None:
        self.language = language

    def rules(self) -> list[Rule]:
        return [self.read_month_dates, self.read_decades, self.read_ordinals]

    def read_month_dates(self, text: str) -> str:
        """10 May 2024 -> the tenth of May, twenty twenty-four; May 10 -> May tenth; Jan 2024 -> January twenty twenty-four"""
        text = _DAY_BEFORE_MONTH.sub(self._speak_day_before_month, text)
        text = _MONTH_BEFORE_DAY.sub(self._speak_month_before_day, text)
        return _MONTH_BEFORE_YEAR.sub(
            lambda match: f"{vocab.MONTHS[_MONTH_FORMS[match['month']] - 1]} {self.language.to_year(parse_int(match['year']))}",
            text,
        )

    def _speak_day_before_month(self, match: re.Match) -> str:
        day = parse_int(match["day"])
        if not 1 <= day <= 31:
            return match.group()
        return self.language.to_date(day, _MONTH_FORMS[match["month"]], match["year"])

    def _speak_month_before_day(self, match: re.Match) -> str:
        day = parse_int(match["day"])
        if not 1 <= day <= 31:
            return match.group()
        return self.language.to_month_first_date(day, _MONTH_FORMS[match["month"]], match["year"])

    def read_decades(self, text: str) -> str:
        """1990s -> nineteen nineties, '80s -> eighties"""
        return _DECADE.sub(self._speak_decade, text)

    def _speak_decade(self, match: re.Match) -> str:
        number = parse_int(match[1])
        if number % 10:
            return match.group()
        words = self.language.to_year(number) if len(match[1]) == 4 else self.language.to_cardinal(number)
        return self.language.to_plural(words)

    def read_ordinals(self, text: str) -> str:
        """1st -> first, 21st -> twenty-first"""
        return _ORDINAL.sub(lambda match: self.language.to_ordinal(parse_int(match[1])), text)
