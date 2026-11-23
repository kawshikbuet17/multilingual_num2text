import re

from ...core.digits import parse_int
from ...core.language import Language, Rule
from ...core.lexicon import Lexicon
from . import vocabulary as vocab
from .lexicon import LEXICON
from .rules import EnglishRules


class EnglishLanguage(Language):
    code = "en"
    script = "A-Za-z"
    words = vocab.WORDS
    lexicon = LEXICON
    separate_number_words = True

    def __init__(self, indian_scales: bool = False, lexicon: Lexicon | None = None) -> None:
        """indian_scales: read 2,50,000 as 'two lakh fifty thousand' instead of 'two hundred fifty thousand'."""
        super().__init__(lexicon)
        self.scales = vocab.INDIAN_SCALES if indian_scales else vocab.INTERNATIONAL_SCALES

    def to_cardinal(self, number: int) -> str:
        """2712 -> two thousand seven hundred twelve"""
        if number < 0:
            return f"{self.words.negative} {self.to_cardinal(-number)}"
        if number < 100:
            return self._below_hundred(number)

        parts = []
        for scale_value, scale_word in self.scales:
            if number >= scale_value:
                parts.append(f"{self.to_cardinal(number // scale_value)} {scale_word}")
                number %= scale_value
        if number >= 100:
            parts.append(f"{vocab.ONES[number // 100]} {vocab.HUNDRED}")
            number %= 100
        if number:
            parts.append(self._below_hundred(number))
        return " ".join(parts)

    def to_ordinal(self, number: int) -> str:
        """1 -> first, 21 -> twenty-first, 100 -> one hundredth"""
        *head, last = re.split(r"([ -])", self.to_cardinal(number))
        if last in vocab.IRREGULAR_ORDINALS:
            last = vocab.IRREGULAR_ORDINALS[last]
        elif last.endswith("y"):
            last = last[:-1] + "ieth"
        else:
            last += "th"
        return "".join(head) + last

    def to_year(self, year: int) -> str:
        """1971 -> nineteen seventy-one, 1905 -> nineteen oh five, 2024 -> twenty twenty-four"""
        if not 1000 <= year <= 2099 or year % 1000 < 10:
            return self.to_cardinal(year)
        century, rest = divmod(year, 100)
        if rest == 0:
            return f"{self._below_hundred(century)} {vocab.HUNDRED}"
        rest_words = f"{vocab.OH} {vocab.ONES[rest]}" if rest < 10 else self._below_hundred(rest)
        return f"{self._below_hundred(century)} {rest_words}"

    def to_date(self, day: int, month: int, year: str | None = None) -> str:
        """(10, 5, '2024') -> the tenth of May, twenty twenty-four"""
        fields = {"day": self.to_ordinal(day), "month": vocab.MONTHS[month - 1]}
        if not year:
            return vocab.DATE_FORMAT.format(**fields)
        year_number = parse_int(year)
        fields["year"] = self.to_year(year_number) if len(year) == 4 else self._below_hundred(year_number)
        return vocab.DATE_WITH_YEAR_FORMAT.format(**fields)

    def to_month_first_date(self, day: int, month: int, year: str | None = None) -> str:
        """May 10, 2024 -> May tenth, twenty twenty-four"""
        fields = {"day": self.to_ordinal(day), "month": vocab.MONTHS[month - 1]}
        if not year:
            return vocab.MONTH_FIRST_DATE_FORMAT.format(**fields)
        fields["year"] = self.to_year(parse_int(year))
        return vocab.MONTH_FIRST_DATE_WITH_YEAR_FORMAT.format(**fields)

    def to_time(self, hour: int, minute: int = 0, second: int | None = None, with_period: bool = False) -> str:
        """(10, 30) -> ten thirty, (10, 5) -> ten oh five, (15, 0) -> three o'clock PM, 10 AM -> ten AM"""
        spoken = self.to_cardinal(hour % 12 or 12)
        if minute == 0 and not second:
            if not with_period:
                spoken += f" {vocab.O_CLOCK}"
        elif minute < 10:
            spoken += f" {vocab.OH} {vocab.ONES[minute]}"
        else:
            spoken += f" {self._below_hundred(minute)}"
        if second:
            spoken += f" {vocab.AND} {self.to_cardinal(second)} {vocab.SECONDS}"
        if with_period or hour == 0 or hour > 12:
            spoken += f" {vocab.PM if hour >= 12 else vocab.AM}"
        return spoken

    def to_mixed_fraction(self, whole: int, fraction: str) -> str:
        """(2, '½') -> two and a half, (0, '¾') -> three quarters"""
        if whole == 0:
            return vocab.STANDALONE_FRACTIONS[fraction]
        return f"{self.to_cardinal(whole)} {vocab.AND} {vocab.FRACTIONS[fraction]}"

    def to_plural(self, words: str) -> str:
        """nineteen ninety -> nineteen nineties, eighty -> eighties"""
        return words[:-1] + "ies" if words.endswith("y") else words + "s"

    def language_rules(self) -> list[Rule]:
        return EnglishRules(self).rules()

    @staticmethod
    def _below_hundred(number: int) -> str:
        if number < 20:
            return vocab.ONES[number]
        tens, ones = divmod(number, 10)
        return vocab.TENS[tens] + (f"-{vocab.ONES[ones]}" if ones else "")
