"""Every currency, in every language, written every supported way."""

import re
import unittest

from multilingual_num2text import convert_text, get_language
from multilingual_num2text.core.currencies import CURRENCY_CODES

LANGUAGES = ("bn", "en")

KNOWN_NAMES = {
    "bn": {"BDT": "টাকা", "USD": "ডলার", "EUR": "ইউরো", "GBP": "পাউন্ড", "INR": "রুপি", "SAR": "সৌদি রিয়াল",
           "AED": "আমিরাতি দিরহাম", "JPY": "জাপানি ইয়েন", "CNY": "চীনা ইউয়ান", "MYR": "মালয়েশিয়ান রিঙ্গিত",
           "KWD": "কুয়েতি দিনার", "AUD": "অস্ট্রেলিয়ান ডলার", "CAD": "কানাডিয়ান ডলার", "SGD": "সিঙ্গাপুর ডলার",
           "PKR": "পাকিস্তানি রুপি", "NPR": "নেপালি রুপি", "LKR": "শ্রীলঙ্কান রুপি", "QAR": "কাতারি রিয়াল",
           "OMR": "ওমানি রিয়াল", "THB": "থাই বাত", "KRW": "দক্ষিণ কোরিয়ান উওন", "RUB": "রাশিয়ান রুবল",
           "TRY": "তুর্কি লিরা", "CHF": "সুইস ফ্রাঁ"},
    "en": {"BDT": "taka", "USD": "dollar", "EUR": "euro", "GBP": "pound", "INR": "rupee", "SAR": "Saudi riyal",
           "AED": "UAE dirham", "JPY": "yen", "CNY": "yuan", "MYR": "ringgit", "KWD": "Kuwaiti dinar",
           "AUD": "Australian dollar", "CAD": "Canadian dollar", "SGD": "Singapore dollar", "PKR": "Pakistani rupee",
           "THB": "baht", "KRW": "South Korean won", "RUB": "Russian ruble", "TRY": "Turkish lira", "CHF": "Swiss franc"},
}

SUFFIX_CONFLICTS = {"KM"}


def currencies(lang):
    return {currency.code: currency for currency in get_language(lang).lexicon.currencies}


class CurrencyTableTest(unittest.TestCase):
    def test_every_code_is_unique_and_named_in_every_language(self):
        codes = [entry.code for entry in CURRENCY_CODES]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(len(codes), 153)
        for lang in LANGUAGES:
            with self.subTest(lang=lang):
                self.assertEqual(set(currencies(lang)), set(codes))

    def test_no_symbol_belongs_to_two_currencies(self):
        seen = {}
        for entry in CURRENCY_CODES:
            for symbol in entry.symbols:
                with self.subTest(symbol=symbol):
                    self.assertNotIn(symbol, seen, f"{symbol} used by {seen.get(symbol)} and {entry.code}")
                    seen[symbol] = entry.code

    def test_names_are_unique_and_clean(self):
        for lang in LANGUAGES:
            units = [currency.unit for currency in currencies(lang).values()]
            with self.subTest(lang=lang):
                self.assertEqual(len(units), len(set(units)))
            for code, currency in currencies(lang).items():
                with self.subTest(lang=lang, code=code):
                    for name in (currency.unit, currency.unit_plural, currency.subunit, currency.subunit_plural):
                        if name:
                            self.assertEqual(name, name.strip())
                            self.assertIsNone(re.search(r"\d", name))
                    self.assertEqual(currency.minor_digits == 0, currency.subunit is None)

    def test_known_names(self):
        for lang, names in KNOWN_NAMES.items():
            for code, unit in names.items():
                with self.subTest(lang=lang, code=code):
                    self.assertEqual(currencies(lang)[code].unit, unit)

    def test_minor_digits(self):
        three = {"BHD", "IQD", "JOD", "KWD", "LYD", "OMR", "TND"}
        none = {"BIF", "CLP", "DJF", "GNF", "IRR", "ISK", "JPY", "KMF", "KRW", "MGA", "MRU", "PYG", "RWF", "UGX",
                "VND", "VUV", "XAF", "XOF", "XPF"}
        for entry in CURRENCY_CODES:
            with self.subTest(code=entry.code):
                self.assertEqual(entry.minor_digits, 3 if entry.code in three else 0 if entry.code in none else 2)


class CurrencyReadingTest(unittest.TestCase):
    def expected(self, lang, currency, major, minor):
        language = get_language(lang)
        parts = []
        if major or not minor:
            parts.append(f"{language.to_cardinal(major)} {currency.unit_for(major)}")
        if minor:
            parts.append(f"{language.to_cardinal(minor)} {currency.subunit_for(minor)}")
        return (" and " if lang == "en" else " ").join(parts)

    def test_whole_amounts_with_code_before_and_after(self):
        for lang in LANGUAGES:
            for code, currency in currencies(lang).items():
                for amount in (1, 2, 1500):
                    with self.subTest(lang=lang, code=code, amount=amount):
                        expected = self.expected(lang, currency, amount, 0)
                        self.assertEqual(convert_text(f"{code} {amount:,}", lang), expected)
                        self.assertEqual(convert_text(f"{amount:,} {code}", lang), expected)

    def test_fractions_follow_minor_digits(self):
        for lang in LANGUAGES:
            language = get_language(lang)
            for code, currency in currencies(lang).items():
                with self.subTest(lang=lang, code=code):
                    digits = currency.minor_digits
                    if digits == 0:
                        self.assertEqual(
                            convert_text(f"{code} 1.5", lang), f"{language.spell_number('1.5')} {currency.unit_for(2)}"
                        )
                        continue
                    one_minor = "0." + "0" * (digits - 1) + "1"
                    self.assertEqual(convert_text(f"{code} {one_minor}", lang), self.expected(lang, currency, 0, 1))
                    self.assertEqual(convert_text(f"{code} 1{one_minor[1:]}", lang), self.expected(lang, currency, 1, 1))
                    half = int("5" + "0" * (digits - 1))
                    self.assertEqual(convert_text(f"{code} 2.5", lang), self.expected(lang, currency, 2, half))
                    too_precise = "1." + "1" * (digits + 1)
                    self.assertEqual(
                        convert_text(f"{code} {too_precise}", lang),
                        f"{language.spell_number(too_precise)} {currency.unit_for(2)}",
                    )

    def test_negative_amounts(self):
        for lang in LANGUAGES:
            negative = get_language(lang).words.negative
            for code, currency in currencies(lang).items():
                with self.subTest(lang=lang, code=code):
                    self.assertEqual(convert_text(f"{code} -5", lang), f"{negative} {self.expected(lang, currency, 5, 0)}")

    def test_every_symbol_before_and_after(self):
        for lang in LANGUAGES:
            by_code = currencies(lang)
            for entry in CURRENCY_CODES:
                currency = by_code[entry.code]
                expected = self.expected(lang, currency, 7, 0)
                for symbol in entry.symbols:
                    with self.subTest(lang=lang, code=entry.code, symbol=symbol):
                        self.assertEqual(convert_text(f"{symbol}7", lang), expected)
                        self.assertEqual(convert_text(f"{symbol} 7", lang), expected)
                        if symbol not in SUFFIX_CONFLICTS:
                            self.assertEqual(convert_text(f"7 {symbol}", lang), expected)

    def test_every_written_name_after_the_amount(self):
        for lang in LANGUAGES:
            for code, currency in currencies(lang).items():
                expected = self.expected(lang, currency, 7, 0)
                for name in currency.suffix_symbols:
                    with self.subTest(lang=lang, code=code, name=name):
                        self.assertEqual(convert_text(f"7 {name}", lang), expected)
                        if lang == "en" and name[0].isalpha():
                            self.assertEqual(convert_text(f"7 {name.upper()}", lang), expected)
                            self.assertEqual(convert_text(f"7 {name.title()}", lang), expected)

    def test_symbol_and_repeated_name_together(self):
        for lang, written in (("bn", "৳৫০০ টাকা"), ("bn", "৳১০০০/-"), ("en", "$5 dollars"), ("en", "৳500 taka")):
            with self.subTest(lang=lang, written=written):
                self.assertIsNone(re.search(r"[\d৳$]|টাকা টাকা|dollars dollars", convert_text(written, lang)))

    def test_scale_words_with_every_sign(self):
        for lang, scale in (("bn", "লাখ"), ("en", "million")):
            by_code = currencies(lang)
            for entry in CURRENCY_CODES:
                for symbol in entry.symbols:
                    if symbol[0].isalpha():
                        continue
                    with self.subTest(lang=lang, symbol=symbol):
                        spoken = convert_text(f"{symbol}5 {scale}", lang)
                        self.assertTrue(spoken.endswith(f"{scale} {by_code[entry.code].unit_for(2)}"), spoken)

    def test_bangla_inflections_kept(self):
        cases = {"৫০০ টাকার": "পাঁচশত টাকার", "৫০০ টাকায়": "পাঁচশত টাকায়", "১০.৫০ টাকার": "দশ টাকা পঞ্চাশ পয়সার",
                 "১০০ ডলারের": "একশত ডলারের", "SAR ১০ এর": "দশ সৌদি রিয়াল এর"}
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn"), spoken)

    def test_ambiguous_words_are_not_money(self):
        cases = [("bn", "২.৫ পাউন্ড ওজন", "দুই দশমিক পাঁচ পাউন্ড ওজন"), ("en", "2.5 pounds", "two point five pounds"),
                 ("en", "5000 won the game", "five thousand won the game"), ("en", "all 5 items", "all five items"),
                 ("en", "5 ft tall", "five ft tall"), ("bn", "৫ KM", "পাঁচ কিলোমিটার")]
        for lang, written, spoken in cases:
            with self.subTest(lang=lang, written=written):
                self.assertEqual(convert_text(written, lang), spoken)


if __name__ == "__main__":
    unittest.main()
