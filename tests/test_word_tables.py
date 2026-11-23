"""Every word the languages produce, checked against reference tables written independently of the package."""

import re
import unittest

from multilingual_num2text import convert_text, get_language

BANGLA_0_TO_99 = """
শূন্য এক দুই তিন চার পাঁচ ছয় সাত আট নয়
দশ এগারো বারো তেরো চৌদ্দ পনেরো ষোলো সতেরো আঠারো উনিশ
বিশ একুশ বাইশ তেইশ চব্বিশ পঁচিশ ছাব্বিশ সাতাশ আটাশ উনত্রিশ
ত্রিশ একত্রিশ বত্রিশ তেত্রিশ চৌত্রিশ পঁয়ত্রিশ ছত্রিশ সাঁইত্রিশ আটত্রিশ উনচল্লিশ
চল্লিশ একচল্লিশ বিয়াল্লিশ তেতাল্লিশ চুয়াল্লিশ পঁয়তাল্লিশ ছেচল্লিশ সাতচল্লিশ আটচল্লিশ উনপঞ্চাশ
পঞ্চাশ একান্ন বায়ান্ন তিপ্পান্ন চুয়ান্ন পঞ্চান্ন ছাপ্পান্ন সাতান্ন আটান্ন উনষাট
ষাট একষট্টি বাষট্টি তেষট্টি চৌষট্টি পঁয়ষট্টি ছেষট্টি সাতষট্টি আটষট্টি উনসত্তর
সত্তর একাত্তর বাহাত্তর তিয়াত্তর চুয়াত্তর পঁচাত্তর ছিয়াত্তর সাতাত্তর আটাত্তর উনআশি
আশি একাশি বিরাশি তিরাশি চুরাশি পঁচাশি ছিয়াশি সাতাশি অষ্টাশি উননব্বই
নব্বই একানব্বই বিরানব্বই তিরানব্বই চুরানব্বই পঁচানব্বই ছিয়ানব্বই সাতানব্বই আটানব্বই নিরানব্বই
""".split()

ENGLISH_ONES = (
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen"
).split()
ENGLISH_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
ENGLISH_0_TO_99 = [
    ENGLISH_ONES[n] if n < 20 else ENGLISH_TENS[n // 10] + (f"-{ENGLISH_ONES[n % 10]}" if n % 10 else "")
    for n in range(100)
]

BANGLA_DATE_DAYS = """
পহেলা দোসরা তেসরা চৌঠা পাঁচই ছয়ই সাতই আটই নয়ই দশই এগারোই বারোই তেরোই চৌদ্দই পনেরোই ষোলোই সতেরোই আঠারোই
উনিশে বিশে একুশে বাইশে তেইশে চব্বিশে পঁচিশে ছাব্বিশে সাতাশে আটাশে উনত্রিশে ত্রিশে একত্রিশে
""".split()

BANGLA_MONTHS = "জানুয়ারি ফেব্রুয়ারি মার্চ এপ্রিল মে জুন জুলাই আগস্ট সেপ্টেম্বর অক্টোবর নভেম্বর ডিসেম্বর".split()
ENGLISH_MONTHS = "January February March April May June July August September October November December".split()

ENGLISH_ORDINALS_1_TO_31 = """
first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth fourteenth
fifteenth sixteenth seventeenth eighteenth nineteenth twentieth twenty-first twenty-second twenty-third
twenty-fourth twenty-fifth twenty-sixth twenty-seventh twenty-eighth twenty-ninth thirtieth thirty-first
""".split()

BANGLA_PERIOD_BY_HOUR = ["রাত"] * 4 + ["ভোর"] * 2 + ["সকাল"] * 6 + ["দুপুর"] * 4 + ["বিকাল"] * 2 + ["সন্ধ্যা"] * 2 + ["রাত"] * 4


def to_bangla_digits(number) -> str:
    return str(number).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))


class BanglaWordTableTest(unittest.TestCase):
    def setUp(self):
        self.bangla = get_language("bn")

    def test_every_word_from_0_to_99(self):
        for number, word in enumerate(BANGLA_0_TO_99):
            with self.subTest(number=number):
                self.assertEqual(self.bangla.to_cardinal(number), word)
                self.assertEqual(convert_text(to_bangla_digits(number), "bn"), word)

    def test_every_hundred(self):
        for hundreds in range(1, 10):
            with self.subTest(hundreds=hundreds):
                self.assertEqual(self.bangla.to_cardinal(hundreds * 100), BANGLA_0_TO_99[hundreds] + "শত")

    def test_scales(self):
        cases = {
            1_000: "এক হাজার", 10_000: "দশ হাজার", 100_000: "এক লক্ষ", 1_000_000: "দশ লক্ষ",
            10_000_000: "এক কোটি", 100_000_000: "দশ কোটি", 1_000_000_000: "একশত কোটি",
            10_000_000_000: "এক হাজার কোটি", 1_000_000_000_000: "এক লক্ষ কোটি",
            100_000_000_000_000: "এক কোটি কোটি",
        }
        for number, words in cases.items():
            with self.subTest(number=number):
                self.assertEqual(self.bangla.to_cardinal(number), words)

    def test_composition_up_to_one_lakh(self):
        for number in range(100, 100_000):
            thousands, rest = divmod(number, 1000)
            hundreds, below_hundred = divmod(rest, 100)
            parts = []
            if thousands:
                parts.append(f"{BANGLA_0_TO_99[thousands]} হাজার")
            if hundreds:
                parts.append(BANGLA_0_TO_99[hundreds] + "শত")
            if below_hundred:
                parts.append(BANGLA_0_TO_99[below_hundred])
            self.assertEqual(self.bangla.to_cardinal(number), " ".join(parts), number)

    def test_negative(self):
        self.assertEqual(self.bangla.to_cardinal(-1), "ঋণাত্মক এক")
        self.assertEqual(self.bangla.to_cardinal(-100_000), "ঋণাত্মক এক লক্ষ")

    def test_digitwise_every_digit(self):
        self.assertEqual(self.bangla.to_digitwise("0123456789"), " ".join(BANGLA_0_TO_99[:10]))
        self.assertEqual(self.bangla.to_digitwise("০১২৩৪৫৬৭৮৯"), " ".join(BANGLA_0_TO_99[:10]))

    def test_ordinals(self):
        special = "প্রথম দ্বিতীয় তৃতীয় চতুর্থ পঞ্চম ষষ্ঠ সপ্তম অষ্টম নবম দশম".split()
        for number in range(1, 101):
            expected = special[number - 1] if number <= 10 else BANGLA_0_TO_99[number % 100] + "তম" if number < 100 else "একশততম"
            with self.subTest(number=number):
                self.assertEqual(self.bangla.to_ordinal(number), expected)

    def test_written_ordinal_suffixes(self):
        cases = {"১ম": "প্রথম", "২য়": "দ্বিতীয়", "৩য়": "তৃতীয়", "৪র্থ": "চতুর্থ", "৫ম": "পঞ্চম", "৬ষ্ঠ": "ষষ্ঠ",
                 "৭ম": "সপ্তম", "৮ম": "অষ্টম", "৯ম": "নবম", "১০ম": "দশম", "৫তম": "পঞ্চম", "২১তম": "একুশতম"}
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn"), spoken)

    def test_every_date_day(self):
        suffixes = {1: "লা", 2: "রা", 3: "রা", 4: "ঠা"}
        for day, word in enumerate(BANGLA_DATE_DAYS, start=1):
            with self.subTest(day=day):
                self.assertEqual(self.bangla.to_date_day(day), word)
                written_suffix = suffixes.get(day, "ই" if day <= 18 else "শে")
                self.assertEqual(convert_text(f"{to_bangla_digits(day)}{written_suffix}", "bn"), word)
                self.assertEqual(convert_text(f"{to_bangla_digits(day)} মে", "bn"), f"{word} মে")

    def test_every_month(self):
        for month, name in enumerate(BANGLA_MONTHS, start=1):
            with self.subTest(month=month):
                self.assertEqual(self.bangla.to_date(1, month), f"পহেলা {name}")
                self.assertEqual(convert_text(f"১৩/{month:02d}/২০২৪", "bn"), f"তেরোই {name} দুই হাজার চব্বিশ")

    def test_bangla_calendar_months(self):
        for name in "বৈশাখ জ্যৈষ্ঠ আষাঢ় শ্রাবণ ভাদ্র আশ্বিন কার্তিক অগ্রহায়ণ পৌষ মাঘ ফাল্গুন চৈত্র".split():
            with self.subTest(month=name):
                self.assertEqual(convert_text(f"১৫ {name}", "bn"), f"পনেরোই {name}")

    def test_every_hour_without_period(self):
        for hour in range(24):
            clock = BANGLA_0_TO_99[hour % 12 or 12] + "টা"
            expected = f"{BANGLA_PERIOD_BY_HOUR[hour]} {clock}" if hour == 0 or hour > 12 else clock
            with self.subTest(hour=hour):
                self.assertEqual(convert_text(f"{to_bangla_digits(hour).zfill(2)}:০০", "bn"), expected)

    def test_every_hour_with_am_pm(self):
        for hour in range(24):
            written = f"{hour % 12 or 12} {'PM' if hour >= 12 else 'AM'}"
            expected = f"{BANGLA_PERIOD_BY_HOUR[hour]} {BANGLA_0_TO_99[hour % 12 or 12]}টা"
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn"), expected)

    def test_every_minute_and_second(self):
        for value in range(1, 60):
            with self.subTest(value=value):
                self.assertEqual(convert_text(f"১০:{value:02d}", "bn"), f"দশটা {BANGLA_0_TO_99[value]} মিনিট")
                self.assertEqual(
                    convert_text(f"১০:০১:{value:02d}", "bn"), f"দশটা এক মিনিট {BANGLA_0_TO_99[value]} সেকেন্ড"
                )

    def test_years(self):
        cases = {
            1099: "এক হাজার নিরানব্বই", 1100: "এগারোশো", 1900: "উনিশশো", 1905: "উনিশশো পাঁচ",
            1971: "উনিশশো একাত্তর", 1999: "উনিশশো নিরানব্বই", 2000: "দুই হাজার", 2024: "দুই হাজার চব্বিশ",
            1431: "চৌদ্দশো একত্রিশ",
        }
        for year, words in cases.items():
            with self.subTest(year=year):
                self.assertEqual(self.bangla.to_year(year), words)
                self.assertEqual(convert_text(f"{to_bangla_digits(year)} সালে", "bn"), f"{words} সালে")

    def test_colloquial_fractions(self):
        cases = {
            "০.৫": "আধা", "১.৫": "দেড়", "২.৫": "আড়াই", "৩.৫": "সাড়ে তিন", "১০.৫": "সাড়ে দশ",
            "১.২৫": "সোয়া এক", "৪.২৫": "সোয়া চার", "০.৭৫": "পৌনে এক", "২.৭৫": "পৌনে তিন", "২.৫০": "আড়াই",
        }
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(f"{written} লাখ", "bn"), f"{spoken} লাখ")
        self.assertEqual(convert_text("২.৪ লাখ", "bn"), "দুই দশমিক চার লাখ")

    def test_mixed_fraction_signs(self):
        cases = {"½": "আধা", "¼": "এক চতুর্থাংশ", "¾": "তিন চতুর্থাংশ", "১½": "দেড়", "২½": "আড়াই", "৩½": "সাড়ে তিন",
                 "১¼": "সোয়া এক", "১¾": "পৌনে দুই"}
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn"), spoken)


class EnglishWordTableTest(unittest.TestCase):
    def setUp(self):
        self.english = get_language("en")

    def test_every_word_from_0_to_99(self):
        for number, word in enumerate(ENGLISH_0_TO_99):
            with self.subTest(number=number):
                self.assertEqual(self.english.to_cardinal(number), word)
                self.assertEqual(convert_text(str(number), "en"), word)

    def test_composition_up_to_one_million(self):
        for number in range(100, 1_000_000, 7):
            thousands, rest = divmod(number, 1000)
            hundreds, below_hundred = divmod(rest, 100)
            parts = []
            if thousands:
                parts.append(f"{self.english.to_cardinal(thousands)} thousand")
            if hundreds:
                parts.append(f"{ENGLISH_ONES[hundreds]} hundred")
            if below_hundred:
                parts.append(ENGLISH_0_TO_99[below_hundred])
            self.assertEqual(self.english.to_cardinal(number), " ".join(parts), number)

    def test_scales(self):
        cases = {
            1_000: "one thousand", 1_000_000: "one million", 1_000_000_000: "one billion",
            1_000_000_000_000: "one trillion", 1_000_000_000_000_000: "one thousand trillion",
            2_500_000_000: "two billion five hundred million",
        }
        for number, words in cases.items():
            with self.subTest(number=number):
                self.assertEqual(self.english.to_cardinal(number), words)

    def test_negative(self):
        self.assertEqual(self.english.to_cardinal(-42), "minus forty-two")

    def test_digitwise_every_digit(self):
        self.assertEqual(self.english.to_digitwise("0123456789"), " ".join(ENGLISH_ONES[:10]))

    def test_ordinals(self):
        for number, word in enumerate(ENGLISH_ORDINALS_1_TO_31, start=1):
            with self.subTest(number=number):
                self.assertEqual(self.english.to_ordinal(number), word)
        cases = {40: "fortieth", 99: "ninety-ninth", 100: "one hundredth", 101: "one hundred first",
                 111: "one hundred eleventh", 1000: "one thousandth", 1_000_000: "one millionth"}
        for number, word in cases.items():
            with self.subTest(number=number):
                self.assertEqual(self.english.to_ordinal(number), word)

    def test_written_ordinal_suffixes(self):
        for number in range(1, 32):
            suffix = "th" if 11 <= number <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
            with self.subTest(number=number):
                self.assertEqual(convert_text(f"{number}{suffix}", "en"), ENGLISH_ORDINALS_1_TO_31[number - 1])

    def test_every_month(self):
        for month, name in enumerate(ENGLISH_MONTHS, start=1):
            with self.subTest(month=month):
                self.assertEqual(convert_text(f"13/{month:02d}/2024", "en"), f"the thirteenth of {name}, twenty twenty-four")
                self.assertEqual(convert_text(f"{name} 1", "en"), f"{name} first")
                self.assertEqual(convert_text(f"{name[:3]} 1", "en"), f"{name} first")

    def test_every_hour(self):
        for hour in range(24):
            clock = ENGLISH_0_TO_99[hour % 12 or 12]
            expected = f"{clock} o'clock" + (" AM" if hour == 0 else " PM" if hour > 12 else "")
            with self.subTest(hour=hour):
                self.assertEqual(convert_text(f"{hour:02d}:00", "en"), expected)
                written = f"{hour % 12 or 12} {'PM' if hour >= 12 else 'AM'}"
                self.assertEqual(convert_text(written, "en"), f"{clock} {'PM' if hour >= 12 else 'AM'}")

    def test_every_minute(self):
        for minute in range(1, 60):
            minute_words = f"oh {ENGLISH_ONES[minute]}" if minute < 10 else ENGLISH_0_TO_99[minute]
            with self.subTest(minute=minute):
                self.assertEqual(convert_text(f"10:{minute:02d}", "en"), f"ten {minute_words}")

    def test_years(self):
        cases = {
            999: "nine hundred ninety-nine", 1000: "one thousand", 1005: "one thousand five", 1010: "ten ten", 1066: "ten sixty-six", 1900: "nineteen hundred",
            1905: "nineteen oh five", 1999: "nineteen ninety-nine", 2000: "two thousand", 2009: "two thousand nine",
            2010: "twenty ten", 2024: "twenty twenty-four", 2099: "twenty ninety-nine", 2100: "two thousand one hundred",
        }
        for year, words in cases.items():
            with self.subTest(year=year):
                self.assertEqual(self.english.to_year(year), words)

    def test_decades(self):
        cases = {"1990s": "nineteen nineties", "1900s": "nineteen hundreds", "2000s": "two thousands",
                 "2010s": "twenty tens", "'80s": "eighties", "70s": "seventies"}
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "en"), spoken)

    def test_mixed_fraction_signs(self):
        cases = {"½": "one half", "¼": "one quarter", "¾": "three quarters", "1½": "one and a half",
                 "2¼": "two and a quarter", "3¾": "three and three quarters"}
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "en"), spoken)


class AmbiguousDateTest(unittest.TestCase):
    """Day and month both 12 or less: different numbers are read as written, equal numbers with the month name."""

    def test_every_day_month_pair(self):
        for first in range(1, 13):
            for second in range(1, 13):
                with self.subTest(first=first, second=second):
                    if first == second:
                        bangla = f"{BANGLA_DATE_DAYS[first - 1]} {BANGLA_MONTHS[first - 1]} দুই হাজার চব্বিশ"
                        english = f"the {ENGLISH_ORDINALS_1_TO_31[first - 1]} of {ENGLISH_MONTHS[first - 1]}, twenty twenty-four"
                    else:
                        bangla = f"{BANGLA_0_TO_99[first]} {BANGLA_0_TO_99[second]} দুই হাজার চব্বিশ"
                        english = f"{ENGLISH_0_TO_99[first]} {ENGLISH_0_TO_99[second]} twenty twenty-four"
                    for separator in "/-.":
                        written = f"{first:02d}{separator}{second:02d}{separator}2024"
                        self.assertEqual(convert_text(to_bangla_digits(written), lang="bn"), bangla)
                        self.assertEqual(convert_text(written, lang="en"), english)
                    self.assertEqual(convert_text(f"{first}/{second}/2024", lang="en"), english)

    def test_iso_order_keeps_month_names(self):
        for month in range(1, 13):
            with self.subTest(month=month):
                self.assertEqual(convert_text(f"2024-{month:02d}-05", lang="en"), f"the fifth of {ENGLISH_MONTHS[month - 1]}, twenty twenty-four")
                self.assertEqual(convert_text(to_bangla_digits(f"2024-{month:02d}-05"), lang="bn"), f"পাঁচই {BANGLA_MONTHS[month - 1]} দুই হাজার চব্বিশ")


class NoDigitsLeftTest(unittest.TestCase):
    def test_every_number_up_to_ten_thousand(self):
        for number in range(10_000):
            for lang, written in (("bn", to_bangla_digits(number)), ("en", str(number))):
                spoken = convert_text(written, lang)
                self.assertIsNone(re.search(r"\d", spoken), (lang, written, spoken))
                self.assertNotIn("  ", spoken)


if __name__ == "__main__":
    unittest.main()
