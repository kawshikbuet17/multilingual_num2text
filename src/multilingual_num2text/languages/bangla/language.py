from ...core.digits import parse_int, split_number, to_ascii_digits
from ...core.language import Language, Rule
from . import vocabulary as vocab
from .lexicon import LEXICON
from .rules import BANGLA_LETTER, BanglaRules


class BanglaLanguage(Language):
    code = "bn"
    words = vocab.WORDS
    lexicon = LEXICON
    money_inflection_pattern = f"{BANGLA_LETTER}*"

    def to_cardinal(self, number: int, hundred: str = vocab.HUNDRED) -> str:
        """2712 -> দুই হাজার সাতশত বারো"""
        if number < 0:
            return f"{self.words.negative} {self.to_cardinal(-number, hundred)}"
        if number < 100:
            return vocab.NUMBER_WORDS[number]

        parts = []
        for scale_value, scale_word in vocab.SCALES:
            if number >= scale_value:
                parts.append(f"{self.to_cardinal(number // scale_value, hundred)} {scale_word}")
                number %= scale_value
        if number >= 100:
            parts.append(vocab.NUMBER_WORDS[number // 100] + hundred)
            number %= 100
        if number:
            parts.append(vocab.NUMBER_WORDS[number])
        return " ".join(parts)

    def to_ordinal(self, number: int) -> str:
        """5 -> পঞ্চম, 21 -> একুশতম"""
        return vocab.ORDINALS.get(number) or self.to_cardinal(number) + vocab.ORDINAL_SUFFIX

    def to_year(self, year: int) -> str:
        """1971 -> উনিশশো একাত্তর, 2024 -> দুই হাজার চব্বিশ"""
        if not 1100 <= year <= 1999:
            return self.to_cardinal(year)
        century, rest = divmod(year, 100)
        spoken = vocab.NUMBER_WORDS[century] + vocab.SPOKEN_HUNDRED
        return f"{spoken} {vocab.NUMBER_WORDS[rest]}" if rest else spoken

    def to_date(self, day: int, month: int, year: str | None = None) -> str:
        """(10, 5, '2024') -> দশই মে দুই হাজার চব্বিশ"""
        spoken = f"{self.to_date_day(day)} {vocab.MONTHS[month - 1]}"
        if not year:
            return spoken
        year_number = parse_int(year)
        year_words = self.to_year(year_number) if len(year) == 4 else self.to_cardinal(year_number)
        return f"{spoken} {year_words}"

    def to_time(self, hour: int, minute: int = 0, second: int | None = None, with_period: bool = False) -> str:
        """(10, 30) -> দশটা ত্রিশ মিনিট, (15, 30) -> দুপুর তিনটা ত্রিশ মিনিট, 10 AM -> সকাল দশটা"""
        period = self._day_period(hour) if with_period or hour == 0 or hour > 12 else None
        parts = [period] if period else []
        parts.append(self.to_cardinal(hour % 12 or 12) + vocab.O_CLOCK)
        if minute or second:
            parts.append(f"{self.to_cardinal(minute)} {vocab.MINUTE}")
        if second:
            parts.append(f"{self.to_cardinal(second)} {vocab.SECOND}")
        return " ".join(parts)

    def to_date_day(self, day: int) -> str:
        """1 -> পহেলা, 10 -> দশই, 21 -> একুশে"""
        if day in vocab.DATE_DAYS:
            return vocab.DATE_DAYS[day]
        suffix = vocab.DATE_DAY_SUFFIX_UNTIL_18 if day <= 18 else vocab.DATE_DAY_SUFFIX_FROM_19
        return self.to_cardinal(day) + suffix

    def to_colloquial_fraction(self, whole: int, fraction: str) -> str | None:
        """(2, '5') -> আড়াই, (3, '5') -> সাড়ে তিন, (1, '25') -> সোয়া এক, (2, '75') -> পৌনে তিন"""
        fraction = to_ascii_digits(fraction).rstrip("0")
        if fraction == "5":
            special = {0: vocab.HALF, 1: vocab.ONE_AND_HALF, 2: vocab.TWO_AND_HALF}
            return special.get(whole) or f"{vocab.AND_A_HALF} {self.to_cardinal(whole)}"
        if fraction == "25" and whole:
            return f"{vocab.AND_A_QUARTER} {self.to_cardinal(whole)}"
        if fraction == "75":
            return f"{vocab.QUARTER_TO} {self.to_cardinal(whole + 1)}"
        return None

    def to_mixed_fraction(self, whole: int, fraction: str) -> str:
        """(2, '½') -> আড়াই, (0, '½') -> আধা, (0, '¼') -> এক চতুর্থাংশ, (1, '¾') -> পৌনে দুই"""
        if whole == 0 and fraction == "¼":
            return vocab.ONE_QUARTER
        if whole == 0 and fraction == "¾":
            return vocab.THREE_QUARTERS
        decimal = {"½": "5", "¼": "25", "¾": "75"}[fraction]
        return self.to_colloquial_fraction(whole, decimal) or self.spell_number(f"{whole}.{decimal}")

    def spell_scaled_amount(self, amount: str) -> str:
        """'2.5' before লাখ/কোটি -> আড়াই"""
        _, integer, fraction = split_number(amount)
        if fraction:
            colloquial = self.to_colloquial_fraction(parse_int(integer), fraction)
            if colloquial:
                return colloquial
        return self.spell_number(amount)

    def language_rules(self) -> list[Rule]:
        return BanglaRules(self).rules()

    @staticmethod
    def _day_period(hour: int) -> str | None:
        for hours, period in vocab.DAY_PERIODS:
            if hour in hours:
                return period
        return None
