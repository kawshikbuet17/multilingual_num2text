"""Rules that find numbers in running text and hand them to the language for spelling.

The groups run in a fixed order (see Language.build_rules): specific shapes such as dates, phones
and money must run before the generic decimal and integer rules, which would otherwise read them
as plain numbers.
"""

from __future__ import annotations

import calendar
import re
from decimal import Decimal
from typing import TYPE_CHECKING

from .digits import ZERO_DIGITS, has_valid_grouping, only_digits, parse_int, starts_with_zero, to_ascii_digits
from .patterns import (
    NEGATIVE_SIGN,
    NOT_DIGIT_AFTER,
    NOT_DIGIT_BEFORE,
    NOT_LETTER_AFTER,
    NOT_NUMBER_BEFORE,
    NUMBER,
    UNSIGNED_AMOUNT,
    WORD_CHARS,
    alternation,
    compile_if_any,
)

if TYPE_CHECKING:
    from .language import Language, Rule

_STAR_CODE = re.compile(r"(?<![\w*#])[*#][\d*#]*\d[\d*#]*")
_CARD_NUMBER = re.compile(r"(?<!\d)\d{4}(?: \d{4}){3}(?!\d)")
_YEAR_SPAN = re.compile(r"(?<![\d./-])(\d{4})[-–/](\d{2})(?!\d|[-/.]\d)")
_DAY_MONTH_YEAR = re.compile(r"(?<![\d./-])(\d{1,2})([/.-])(\d{1,2})\2(\d{4}|\d{2})(?!\d|[/.-]\d)")
_YEAR_MONTH_DAY = re.compile(r"(?<![\d./-])(\d{4})([/.-])(\d{1,2})\2(\d{1,2})(?!\d|[/.-]\d)")
_CLOCK_WITH_PERIOD = re.compile(r"(?<![\d:.])(\d{1,2})(?::(\d{2})(?::(\d{2}))?)?\s?([AaPp])\.?[Mm]\.?(?![A-Za-z])")
_CLOCK_TIME = re.compile(r"(?<![\d:])(\d{1,2}):(\d{2})(?::(\d{2}))?(?![\d:])")
_AREA_CODE = re.compile(rf"(?<!\w)\(([{ZERO_DIGITS}]\d{{1,4}})\)\s?(?=\d)")
_ARITHMETIC = re.compile(r"(?<=\d)\s?([+×÷=])\s?(?=[-−]?\d)")
_MORE_THAN = re.compile(r"(?<=\d)\+(?![\d+])")
_MIXED_FRACTION = re.compile(r"(?<![\d.])(\d+)?\s?([½¼¾])")
_LEADING_DOT_DECIMAL = re.compile(r"(?:^|(?<=[\s(]))(?P<sign>[-−])?\.(?P<fraction>\d+)(?!\d|\.\d)", re.MULTILINE)
_LETTER_BEFORE_DIGIT = re.compile(rf"(?<=[{WORD_CHARS}])(?<![\d_])(?=\d)")
_RATIO = re.compile(r"(?<![\d:])\d+(?::\d+)+(?![\d:])")
_PHONE = re.compile(rf"(?<![{WORD_CHARS}.,+/])(?<!\d-)(?:\+\d|[{ZERO_DIGITS}]\d)(?:\d|[ -](?=\d))*(?!\d|[.,]\d)")
_PHONE_GROUP_SEPARATOR = re.compile(r"([ -])")
_HYPHENATED_CODE = re.compile(r"(?<![\d-])\d+(?:-\d+){2,}(?!\d|-\d)")
_DOTTED_NUMBER = re.compile(rf"(?<![\d.])\d+(?:\.\d+){{2,}}{NOT_DIGIT_AFTER}")
_SPACE_SPLIT_GROUPING = re.compile(rf"(?<![\d,])\d{{1,2}}(?:\s*,\s*\d{{2}})*\s*,\s*\d{{3}}{NOT_DIGIT_AFTER}")
_PERCENT = re.compile(rf"{NEGATIVE_SIGN}{NOT_NUMBER_BEFORE}(?P<amount>{UNSIGNED_AMOUNT})\s?%", re.MULTILINE)
_SLASH_LIST = re.compile(rf"{NOT_DIGIT_BEFORE}\d+(?:/\d+){{2,}}{NOT_DIGIT_AFTER}")
_SLASH_PAIR = re.compile(r"(?<=\d)/(?=\d)")
_DECIMAL = re.compile(rf"{NEGATIVE_SIGN}{NOT_NUMBER_BEFORE}(?P<amount>{NUMBER}\.\d+)(?!\d|\.\d)", re.MULTILINE)
_INTEGER = re.compile(rf"{NEGATIVE_SIGN}{NOT_DIGIT_BEFORE}(?P<amount>{NUMBER}){NOT_DIGIT_AFTER}", re.MULTILINE)


def _days_in_month(month: int, year: str) -> int:
    """Uses the real calendar for a 4-digit year; a 2-digit year allows 29 February."""
    if len(year) == 4:
        return calendar.monthrange(int(year), month)[1]
    return 29 if month == 2 else calendar.monthrange(2001, month)[1]


def spaced(spoken: str) -> str:
    return f" {spoken} "


class NumberRules:
    def __init__(self, language: Language) -> None:
        self.language = language
        self.lexicon = lexicon = language.lexicon

        self._symbol_to_currency = self._map_written_forms(lexicon.currencies)
        prefix_symbols = [symbol for currency in lexicon.currencies for symbol in currency.symbols]
        prefix_signs = [symbol for symbol in prefix_symbols if not symbol[0].isalpha()]
        prefix_words = [symbol for symbol in prefix_symbols if symbol[0].isalpha()]

        self._money_ahead = compile_if_any(self._symbol_to_currency, lambda symbols: rf"\s?(?:{symbols})(?![A-Za-z])")
        self._money_after_amount = compile_if_any(
            self._symbol_to_currency,
            lambda symbols: (
                rf"{NEGATIVE_SIGN}{NOT_NUMBER_BEFORE}(?P<amount>{UNSIGNED_AMOUNT})\s?(?P<symbol>{symbols})"
                rf"(?P<inflection>{language.money_inflection_pattern})(?![A-Za-z])"
            ),
            re.MULTILINE,
        )
        prefix_alternatives = [f"(?:{alternation(prefix_signs)})"] if prefix_signs else []
        if prefix_words:
            prefix_alternatives.append(f"(?<![A-Za-z])(?:{alternation(prefix_words)})")
        prefix_symbol = f"(?P<symbol>{'|'.join(prefix_alternatives)})"
        repeated_unit = (
            rf"(?:\s?(?:{alternation(self._symbol_to_currency)})(?P<inflection>{language.money_inflection_pattern}))?"
            if self._symbol_to_currency
            else ""
        )
        self._money_before_amount = (
            re.compile(
                rf"{prefix_symbol}\s?(?P<sign>[-−])?(?P<amount>{UNSIGNED_AMOUNT}){NOT_DIGIT_AFTER}{repeated_unit}(?![A-Za-z])"
            )
            if prefix_alternatives
            else None
        )
        self._scaled_money = (
            compile_if_any(
                lexicon.scale_words,
                lambda scales: rf"{prefix_symbol}\s?(?P<amount>{UNSIGNED_AMOUNT})\s?(?P<scale>{scales})(?![A-Za-z])",
            )
            if prefix_alternatives
            else None
        )
        currency_signs = re.escape("".join(prefix_signs))
        self._range_dash = re.compile(rf"(?<=[\d%])\s*[-–—]\s*(?=[{currency_signs}]?\s?\d)" if prefix_signs else r"(?<=[\d%])\s*[-–—]\s*(?=\d)")

        self._year_after_number = compile_if_any(
            lexicon.year_markers_after, lambda markers: rf"{NOT_DIGIT_BEFORE}(\d{{4}})(?=\s?(?:{markers}))"
        )
        self._year_before_number = compile_if_any(
            lexicon.year_markers_before,
            lambda markers: rf"\b((?:{markers})\s)(\d{{4}})(?!\d|[.,]\d)",
            re.IGNORECASE,
        )
        self._unit = compile_if_any(
            lexicon.units, lambda units: rf"(?<=\d)\s?({units}){NOT_LETTER_AFTER}", re.IGNORECASE
        )
        self._magnitude = compile_if_any(
            lexicon.magnitudes, lambda names: rf"{NOT_NUMBER_BEFORE}({UNSIGNED_AMOUNT})\s?({names}){NOT_LETTER_AFTER}"
        )
        self._long_digit_run = re.compile(rf"{NOT_NUMBER_BEFORE}\d{{{lexicon.digitwise_min_length},}}{NOT_DIGIT_AFTER}")

    @staticmethod
    def _map_written_forms(currencies) -> dict:
        """Codes and signs match exactly (so 'all' is not ALL, 'ft' is not Ft).
        Currency names also match in lower, Title and UPPER case ('Dollars', 'DOLLARS')."""
        written_forms = {}
        for currency in currencies:
            for symbol in currency.symbols:
                written_forms.setdefault(symbol, currency)
            for name in currency.suffix_symbols:
                for form in (name, name.lower(), name.title(), name.upper()):
                    written_forms.setdefault(form, currency)
        return written_forms

    def early_rules(self) -> list[Rule]:
        return [
            self.read_star_codes,
            self.read_card_numbers,
            self.read_scaled_money,
            self.read_year_spans,
        ]

    def shape_rules(self) -> list[Rule]:
        return [
            self.read_dates,
            self.read_clock_times,
            self.read_ratios,
            self.read_area_codes,
            self.read_phone_numbers,
            self.read_hyphenated_codes,
            self.read_years,
            self.read_dotted_numbers,
        ]

    def amount_rules(self) -> list[Rule]:
        return [
            self.read_arithmetic,
            self.read_more_than,
            self.read_mixed_fractions,
            self.mark_ranges,
            self.join_space_split_grouping,
            self.expand_units,
            self.expand_magnitudes,
            self.read_money,
            self.read_percentages,
            self.read_slashes,
        ]

    def plain_number_rules(self) -> list[Rule]:
        return [
            self.separate_letters_from_numbers,
            self.read_decimals,
            self.read_long_digit_runs,
            self.read_integers,
        ]

    def read_star_codes(self, text: str) -> str:
        """*123# is read digit by digit with the symbols spoken."""
        return _STAR_CODE.sub(lambda match: spaced(self.language.to_digitwise(match.group())), text)

    def read_card_numbers(self, text: str) -> str:
        """1234 5678 9012 3456 is read digit by digit."""
        return _CARD_NUMBER.sub(lambda match: spaced(self.language.to_digitwise(match.group())), text)

    def read_scaled_money(self, text: str) -> str:
        """৳5 লাখ -> পাঁচ লাখ টাকা, $2.5 million -> two point five million dollars."""
        if not self._scaled_money:
            return text
        return self._scaled_money.sub(self._speak_scaled_money, text)

    def _speak_scaled_money(self, match: re.Match) -> str:
        currency = self._symbol_to_currency[match["symbol"]]
        amount = self.language.spell_scaled_amount(match["amount"])
        return spaced(f"{amount} {match['scale']} {currency.unit_for(2)}")

    def read_year_spans(self, text: str) -> str:
        """Fiscal or academic years: 2024-25 -> <2024 as a year> <25>. Only when the years are consecutive."""
        return _YEAR_SPAN.sub(self._speak_year_span, text)

    def _speak_year_span(self, match: re.Match) -> str:
        first, second = parse_int(match[1]), parse_int(match[2])
        if (first + 1) % 100 != second:
            return match.group()
        return spaced(f"{self.language.to_year(first)} {self.language.to_cardinal(second)}")

    def read_dates(self, text: str) -> str:
        """10/05/2024, 10-05-2024, 10.05.2024 and 2024-05-10."""
        text = _YEAR_MONTH_DAY.sub(self._speak_year_month_day, text)
        return _DAY_MONTH_YEAR.sub(self._speak_day_month_year, text)

    def _speak_year_month_day(self, match: re.Match) -> str:
        year, _, month, day = match.groups()
        return self._speak_date(parse_int(day), parse_int(month), year) or match.group()

    def _speak_day_month_year(self, match: re.Match) -> str:
        day, _, month, year = match.groups()
        if len(year) == 2 and (len(day) < 2 or len(month) < 2):
            return match.group()
        return self._speak_date(parse_int(day), parse_int(month), year) or match.group()

    def _speak_date(self, day: int, month: int, year: str) -> str | None:
        """Day first, else month first (US). None when neither is a real calendar date."""
        year = to_ascii_digits(year)
        for day_value, month_value in ((day, month), (month, day)):
            if 1 <= month_value <= 12 and 1 <= day_value <= _days_in_month(month_value, year):
                return spaced(self.language.to_date(day_value, month_value, year))
        return None

    def read_clock_times(self, text: str) -> str:
        """10:30, 10:30:20, 24:00, 10 AM, 10:30 p.m. Anything else with a colon is left for read_ratios."""
        text = _CLOCK_WITH_PERIOD.sub(self._speak_clock_with_period, text)
        return _CLOCK_TIME.sub(self._speak_clock_time, text)

    def _speak_clock_with_period(self, match: re.Match) -> str:
        hour = parse_int(match[1])
        minute = parse_int(match[2]) if match[2] else 0
        second = parse_int(match[3]) if match[3] else None
        if not 1 <= hour <= 12 or minute > 59 or (second is not None and second > 59):
            return match.group()
        is_pm = match[4].lower() == "p"
        hour = hour % 12 + (12 if is_pm else 0)
        return spaced(self.language.to_time(hour, minute, second, with_period=True))

    def _speak_clock_time(self, match: re.Match) -> str:
        hour, minute = parse_int(match[1]), parse_int(match[2])
        second = parse_int(match[3]) if match[3] else None
        if hour == 24 and minute == 0 and not second:
            hour = 0
        if hour > 23 or minute > 59 or (second is not None and second > 59):
            return match.group()
        return spaced(self.language.to_time(hour, minute, second))

    def read_area_codes(self, text: str) -> str:
        """(02) 9566300 -> 02-9566300, so the phone rule reads the whole number digit by digit."""
        return _AREA_CODE.sub(r"\1-", text)

    def read_ratios(self, text: str) -> str:
        """1:2 -> one to two, 1:2:3 -> one to two to three"""
        return _RATIO.sub(lambda match: spaced(self._speak_ratio(match.group())), text)

    def _speak_ratio(self, written: str) -> str:
        parts = [parse_int(part) for part in written.split(":")]
        spoken = self.language.to_ratio(parts[0], parts[1])
        for part in parts[2:]:
            spoken += f" {self.language.words.ratio} {self.language.to_cardinal(part)}"
        return spoken

    def read_phone_numbers(self, text: str) -> str:
        """Numbers starting with + or 0 are read digit by digit, with hyphen or space separated groups."""
        return _PHONE.sub(self._speak_phone, text)

    def _speak_phone(self, match: re.Match) -> str:
        pieces = _PHONE_GROUP_SEPARATOR.split(match.group())
        is_money = bool(self._money_ahead and self._money_ahead.match(match.string, match.end()))
        if is_money and len(pieces) == 1:
            return match.group()
        usable_pieces = len(pieces) - 2 if is_money else len(pieces)

        phone, digit_count, index = pieces[0], len(only_digits(pieces[0])), 1
        while index + 1 < usable_pieces:
            separator, group = pieces[index], pieces[index + 1]
            if digit_count + len(group) > self.lexicon.phone_max_digits or (separator == " " and len(group) < 3):
                break
            phone, digit_count, index = phone + group, digit_count + len(group), index + 2
        rest = "".join(pieces[index:])

        if phone.startswith("+") and digit_count < self.lexicon.phone_min_digits_after_plus:
            return spaced(f"{self.language.words.plus} {self.language.to_cardinal(parse_int(phone))}") + rest
        return spaced(self.language.to_digitwise(phone)) + rest

    def read_hyphenated_codes(self, text: str) -> str:
        """Card or reference numbers like 1234-5678-9012 are read digit by digit."""
        return _HYPHENATED_CODE.sub(lambda match: spaced(self.language.to_digitwise(match.group())), text)

    def read_years(self, text: str) -> str:
        if self._year_after_number:
            text = self._year_after_number.sub(lambda match: self.language.to_year(parse_int(match[1])), text)
        if self._year_before_number:
            text = self._year_before_number.sub(self._speak_year_after_marker, text)
        return text

    def _speak_year_after_marker(self, match: re.Match) -> str:
        year = parse_int(match[2])
        return match[1] + self.language.to_year(year) if 1000 <= year <= 2099 else match.group()

    def read_dotted_numbers(self, text: str) -> str:
        """Versions and IP addresses: 1.2.3 is read with the language's word for dot."""
        joiner = f" {self.language.words.dot} "
        return _DOTTED_NUMBER.sub(
            lambda match: spaced(joiner.join(self.language.to_cardinal(parse_int(part)) for part in match.group().split("."))),
            text,
        )

    def read_arithmetic(self, text: str) -> str:
        """2+2=4 -> 2 <add> 2 <equals> 4, using the language's words. Skipped when a word is missing."""
        return _ARITHMETIC.sub(self._speak_operator, text)

    def _speak_operator(self, match: re.Match) -> str:
        words = self.language.words
        word = {"+": words.add, "×": words.times, "÷": words.divided_by, "=": words.equals}[match[1]]
        return f" {word} " if word else match.group()

    def read_more_than(self, text: str) -> str:
        """500+ users -> 500 <plus> users"""
        word = self.language.words.more_than or self.language.words.plus
        return _MORE_THAN.sub(f" {word}", text)

    def read_mixed_fractions(self, text: str) -> str:
        """2½ -> two point five (English: two and a half, Bangla: আড়াই)"""
        return _MIXED_FRACTION.sub(
            lambda match: spaced(self.language.to_mixed_fraction(parse_int(match[1] or "0"), match[2])), text
        )

    def mark_ranges(self, text: str) -> str:
        """500-1000 -> 500 <range word> 1000"""
        return self._range_dash.sub(f" {self.language.words.range} ", text)

    def join_space_split_grouping(self, text: str) -> str:
        """'10, 000' -> '10,000', only when the shape is real digit grouping, not a list."""
        return _SPACE_SPLIT_GROUPING.sub(lambda match: re.sub(r"\s+", "", match.group()), text)

    def expand_units(self, text: str) -> str:
        if not self._unit:
            return text
        return self._unit.sub(lambda match: f" {self.lexicon.units[match[1].lower()]}", text)

    def expand_magnitudes(self, text: str) -> str:
        """5K -> 5000. Produces digits so money and number rules still apply."""
        if not self._magnitude:
            return text
        return self._magnitude.sub(self._expand_magnitude, text)

    def _expand_magnitude(self, match: re.Match) -> str:
        value = Decimal(to_ascii_digits(match[1]).replace(",", "")) * self.lexicon.magnitudes[match[2]]
        plain = format(value, "f")
        return plain.rstrip("0").rstrip(".") if "." in plain else plain

    def read_money(self, text: str) -> str:
        """Symbol before the amount wins, and swallows a repeated unit after it (৳১০০০/-, ৳৫০০ টাকা)."""
        if self._money_before_amount:
            text = self._money_before_amount.sub(self._speak_money, text)
        if self._money_after_amount:
            text = self._money_after_amount.sub(self._speak_money, text)
        return text

    def _speak_money(self, match: re.Match) -> str:
        currency = self._symbol_to_currency[match["symbol"]]
        amount = (match["sign"] or "") + match["amount"]
        inflection = match.groupdict().get("inflection") or ""
        return spaced(self.language.to_money(amount, currency) + inflection)

    def read_percentages(self, text: str) -> str:
        return _PERCENT.sub(lambda match: spaced(self.language.to_percent((match["sign"] or "") + match["amount"])), text)

    def read_slashes(self, text: str) -> str:
        """6/12/24 is a list; 12/3 is read with the language's word for slash."""
        text = _SLASH_LIST.sub(lambda match: match.group().replace("/", ", "), text)
        return _SLASH_PAIR.sub(f" {self.language.words.slash} ", text)

    def separate_letters_from_numbers(self, text: str) -> str:
        """মোট৫০০ -> মোট ৫০০. Number-then-suffix (৫টি) stays joined."""
        return _LETTER_BEFORE_DIGIT.sub(" ", text)

    def read_decimals(self, text: str) -> str:
        """1.49 and .5"""
        text = _DECIMAL.sub(lambda match: spaced(self.language.spell_number((match["sign"] or "") + match["amount"])), text)
        return _LEADING_DOT_DECIMAL.sub(
            lambda match: spaced(self.language.spell_number(f"{match['sign'] or ''}0.{match['fraction']}")), text
        )

    def read_long_digit_runs(self, text: str) -> str:
        """Account numbers and other long digit runs are read digit by digit."""
        return self._long_digit_run.sub(lambda match: spaced(self.language.to_digitwise(match.group())), text)

    def read_integers(self, text: str) -> str:
        return _INTEGER.sub(self._speak_integer, text)

    def _speak_integer(self, match: re.Match) -> str:
        number = match["amount"]
        if not has_valid_grouping(number):
            return ", ".join(self.language.to_cardinal(parse_int(part)) for part in number.split(","))
        if len(number) > 1 and starts_with_zero(number):
            return spaced(self.language.to_digitwise(number))
        value = parse_int(number)
        spoken = self.language.to_cardinal(-value if match["sign"] else value)
        return spaced(spoken) if self.language.separate_number_words else spoken
