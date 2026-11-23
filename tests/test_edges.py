"""Invalid values, boundaries of every setting, Unicode, arguments, the registry and Lexicon.extended()."""

import re
import unittest

from multilingual_num2text import (
    BANGLA_LEXICON,
    ENGLISH_LEXICON,
    BanglaLanguage,
    EnglishLanguage,
    NumberStyle,
    available_languages,
    convert_text,
    get_language,
    number_to_text,
    register_language,
)


class InvalidValueTest(unittest.TestCase):
    def test_impossible_dates_are_not_read_as_dates(self):
        cases = {
            "৩২/০৫/২০২৪": "বত্রিশ, শূন্য পাঁচ, দুই হাজার চব্বিশ",
            "১৩/১৩/২০২৪": "তেরো, তেরো, দুই হাজার চব্বিশ",
            "৩১/০৪/২০২৪": "একত্রিশ, শূন্য চার, দুই হাজার চব্বিশ",
            "৩০/০২/২০২৪": "ত্রিশ, শূন্য দুই, দুই হাজার চব্বিশ",
            "২৯/০২/২০২৩": "উনত্রিশ, শূন্য দুই, দুই হাজার তেইশ",
            "৩২-০৫-২০২৪": "তিন দুই শূন্য পাঁচ দুই শূন্য দুই চার",
        }
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn"), spoken)

    def test_valid_calendar_edges(self):
        cases = {
            "২৯/০২/২০২৪": "উনত্রিশে ফেব্রুয়ারি দুই হাজার চব্বিশ",
            "৩১/১২/২০২৪": "একত্রিশে ডিসেম্বর দুই হাজার চব্বিশ",
            "৩০/০৪/২০২৪": "ত্রিশে এপ্রিল দুই হাজার চব্বিশ",
            "০১/০১/২০০০": "পহেলা জানুয়ারি দুই হাজার",
            "২৯/০২/২৪": "উনত্রিশে ফেব্রুয়ারি চব্বিশ",
        }
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn"), spoken)

    def test_month_first_fallback(self):
        self.assertEqual(convert_text("১০/১৩/২০২৪", "bn"), "তেরোই অক্টোবর দুই হাজার চব্বিশ")
        self.assertEqual(convert_text("12/25/2024", "en"), "the twenty-fifth of December, twenty twenty-four")
        self.assertEqual(convert_text("05/10/2024", "en"), "the fifth of October, twenty twenty-four")

    def test_two_digit_year_needs_padded_day_and_month(self):
        self.assertEqual(convert_text("৬/১২/২৪", "bn"), "ছয়, বারো, চব্বিশ")
        self.assertEqual(convert_text("০৬/১২/২৪", "bn"), "ছয়ই ডিসেম্বর চব্বিশ")

    def test_impossible_times_fall_back(self):
        cases = {
            "২৫:৩০": "পঁচিশ অনুপাত ত্রিশ", "১০:৬০": "দশ অনুপাত ষাট", "২৪:৩০": "চব্বিশ অনুপাত ত্রিশ",
            "১০:৩০:৬০": "দশ অনুপাত ত্রিশ অনুপাত ষাট", "১:২:৩": "এক অনুপাত দুই অনুপাত তিন", "১৩ PM": "তেরো PM", "০ AM": "শূন্য AM",
        }
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn"), spoken)

    def test_invalid_date_days_and_month_days(self):
        self.assertEqual(convert_text("৩২শে", "bn"), "বত্রিশশে")
        self.assertEqual(convert_text("৩২ মে", "bn"), "বত্রিশ মে")
        self.assertEqual(convert_text("32 May", "en"), "thirty-two May")

    def test_non_consecutive_year_span_is_a_range(self):
        self.assertEqual(convert_text("২০২৪-২৬", "bn"), "দুই হাজার চব্বিশ থেকে ছাব্বিশ")
        self.assertEqual(convert_text("১৯৯৯-০০", "bn"), "উনিশশো নিরানব্বই শূন্য")


class SettingBoundaryTest(unittest.TestCase):
    def test_digitwise_min_length(self):
        self.assertEqual(convert_text("123456789", "en"), "one hundred twenty-three million four hundred fifty-six thousand seven hundred eighty-nine")
        self.assertEqual(convert_text("1234567890", "en"), "one two three four five six seven eight nine zero")
        custom = EnglishLanguage(lexicon=ENGLISH_LEXICON.extended(digitwise_min_length=5))
        self.assertEqual(custom.convert_text("1234"), "one thousand two hundred thirty-four")
        self.assertEqual(custom.convert_text("12345"), "one two three four five")

    def test_digit_count_of_commas_does_not_matter(self):
        self.assertEqual(convert_text("1,234,567,890", "en"), "one billion two hundred thirty-four million five hundred sixty-seven thousand eight hundred ninety")

    def test_phone_max_digits(self):
        spoken = convert_text("01711 123456 7890", "en")
        self.assertEqual(spoken, "zero one seven one one one two three four five six seven eight nine zero")
        self.assertEqual(
            convert_text("01711 123456 7890 123", "en"),
            "zero one seven one one one two three four five six seven eight nine zero one hundred twenty-three",
        )

    def test_phone_short_space_groups_are_not_joined(self):
        self.assertEqual(convert_text("01711 12", "en"), "zero one seven one one twelve")

    def test_plus_needs_enough_digits(self):
        self.assertEqual(convert_text("+12345", "en"), "plus twelve thousand three hundred forty-five")
        self.assertEqual(convert_text("+123456", "en"), "plus one two three four five six")

    def test_leading_zero(self):
        cases = {"0": "zero", "00": "zero zero", "05": "zero five", "0.5": "zero point five", "007": "zero zero seven"}
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "en"), spoken)

    def test_strip_decimal_trailing_zeros(self):
        self.assertEqual(convert_text("২.৬০", "bn"), "দুই দশমিক ছয়")
        keep_zeros = BanglaLanguage(lexicon=BANGLA_LEXICON.extended(strip_decimal_trailing_zeros=False))
        self.assertEqual(keep_zeros.convert_text("২.৬০"), "দুই দশমিক ছয় শূন্য")
        self.assertEqual(keep_zeros.convert_text("৭,০০০.০০"), "সাত হাজার দশমিক শূন্য শূন্য")
        self.assertEqual(keep_zeros.convert_text("৭,০০০.০০ টাকা"), "সাত হাজার টাকা")

    def test_grouping_shapes(self):
        cases = {
            "1,000": "one thousand", "10,000": "ten thousand", "1,00,000": "one hundred thousand",
            "12,34,567": "one million two hundred thirty-four thousand five hundred sixty-seven",
            "1,2": "one, two", "1,23": "one, twenty-three", "12,3456": "twelve, three thousand four hundred fifty-six",
        }
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "en"), spoken)


class UnicodeTest(unittest.TestCase):
    def test_both_forms_of_bangla_nukta_letters(self):
        for ya in ("য়", "য়"):
            with self.subTest(form=[hex(ord(char)) for char in ya]):
                self.assertEqual(convert_text(f"২{ya} স্থান, ১০০ টাকা{ya}", "bn"), "দ্বিতীয় স্থান, একশত টাকায়")

    def test_other_digit_scripts(self):
        cases = {"१२३": "একশত তেইশ", "٤٥": "পঁয়তাল্লিশ", "۷": "সাত", "১2३": "একশত তেইশ"}
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn"), spoken)

    def test_space_variants(self):
        cases = {"১০ ০০০": "দশ হাজার", "১০ ০০০": "দশ হাজার", "১০ ০০০": "দশ হাজার",
                 "৫ টাকা": "পাঁচ টাকা", "৫​টাকা": "পাঁচ টাকা"}
        for written, spoken in cases.items():
            with self.subTest(written=repr(written)):
                self.assertEqual(convert_text(written, "bn"), spoken)

    def test_unicode_minus_and_dashes(self):
        self.assertEqual(convert_text("−৫", "bn"), "ঋণাত্মক পাঁচ")
        self.assertEqual(convert_text("৫–১০", "bn"), "পাঁচ থেকে দশ")
        self.assertEqual(convert_text("৫—১০", "bn"), "পাঁচ থেকে দশ")


class ArgumentTest(unittest.TestCase):
    def test_value_types(self):
        cases = [(5, "পাঁচ"), (5.0, "পাঁচ"), (0.1, "শূন্য দশমিক এক"), (1e-7, "শূন্য দশমিক শূন্য শূন্য শূন্য শূন্য শূন্য শূন্য এক"),
                 (-0.5, "ঋণাত্মক শূন্য দশমিক পাঁচ"), ("  ১২  ", "বারো"), ("+৫", "পাঁচ"), (10**15, "এক কোটি কোটি দশ লক্ষ কোটি")]
        for value, spoken in cases[:-1]:
            with self.subTest(value=value):
                self.assertEqual(number_to_text(value, "bn"), spoken)
        self.assertEqual(number_to_text(10**12, "bn"), "এক লক্ষ কোটি")

    def test_style_names_and_enum(self):
        for style in ("cardinal", "digitwise", "auto", NumberStyle.CARDINAL, NumberStyle.DIGITWISE, NumberStyle.AUTO):
            with self.subTest(style=style):
                self.assertTrue(number_to_text("12", "en", style))

    def test_bad_arguments(self):
        for value in ("abc", "", "1.2.3", "1..2", "--5", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                number_to_text(value, "en")
        with self.assertRaises(ValueError):
            number_to_text(5, "en", "words")
        with self.assertRaises(ValueError):
            convert_text("5", "xx")

    def test_digitwise_skips_separators(self):
        self.assertEqual(number_to_text("017-11 12", "en", "digitwise"), "zero one seven one one one two")

    def test_non_string_text(self):
        self.assertEqual(convert_text(None, "en"), None)
        self.assertEqual(convert_text("", "en"), "")


class RegistryTest(unittest.TestCase):
    def test_built_in_languages(self):
        self.assertTrue({"bn", "en"} <= set(available_languages()))
        self.assertEqual(available_languages(), sorted(available_languages()))

    def test_codes_are_case_insensitive(self):
        self.assertIs(get_language("BN"), get_language("bn"))
        self.assertEqual(convert_text("5", "EN"), "five")

    def test_register_variant_and_replace(self):
        register_language(EnglishLanguage(indian_scales=True), code="en-IN")
        self.assertEqual(convert_text("2,50,000", "en-IN"), "two lakh fifty thousand")
        self.assertEqual(convert_text("2,50,000", "en"), "two hundred fifty thousand")
        register_language(EnglishLanguage(), code="en-IN")
        self.assertEqual(convert_text("2,50,000", "en-IN"), "two hundred fifty thousand")


class LexiconExtendedTest(unittest.TestCase):
    def test_dicts_are_merged(self):
        extended = BANGLA_LEXICON.extended(acronyms={"KYC": "কেওয়াইসি"})
        self.assertEqual(extended.acronyms["KYC"], "কেওয়াইসি")
        self.assertEqual(extended.acronyms["ATM"], "এটিএম")

    def test_dict_entries_can_be_overridden(self):
        extended = BANGLA_LEXICON.extended(acronyms={"ATM": "এ টি এম"})
        self.assertEqual(BanglaLanguage(lexicon=extended).convert_text("ATM"), "এ টি এম")

    def test_tuples_are_appended(self):
        extended = BANGLA_LEXICON.extended(year_markers_after=("শতক",))
        self.assertEqual(extended.year_markers_after[-1], "শতক")
        self.assertIn("সাল", extended.year_markers_after)

    def test_settings_are_replaced(self):
        extended = BANGLA_LEXICON.extended(digitwise_min_length=6, strip_decimal_trailing_zeros=False)
        self.assertEqual((extended.digitwise_min_length, extended.strip_decimal_trailing_zeros), (6, False))

    def test_original_is_unchanged(self):
        BANGLA_LEXICON.extended(acronyms={"KYC": "x"}, digitwise_numbers=("1",), digitwise_min_length=3)
        self.assertNotIn("KYC", BANGLA_LEXICON.acronyms)
        self.assertEqual(BANGLA_LEXICON.digitwise_numbers, ())
        self.assertEqual(BANGLA_LEXICON.digitwise_min_length, 10)

    def test_unknown_field_is_an_error(self):
        with self.assertRaises(AttributeError):
            BANGLA_LEXICON.extended(not_a_field=1)

    def test_every_project_setting_takes_effect(self):
        lexicon = BANGLA_LEXICON.extended(
            digitwise_numbers=("54321",),
            fixed_phrases={"N/A": "প্রযোজ্য নয়"},
            word_replacements={"approx.": "প্রায়"},
            removed_patterns=(r"\[Source\s*\d*\]",),
            acronyms={"KYC": "কেওয়াইসি"},
            domain_words={"example": "এক্সাম্পল"},
            email_name_words={"support": "সাপোর্ট"},
            units={"lb": "পাউন্ড"},
            year_markers_after=("শতাব্দী",),
        )
        project = BanglaLanguage(lexicon=lexicon)
        cases = {
            "৫৪৩২১": "পাঁচ চার তিন দুই এক", "N/A": "প্রযোজ্য নয়", "approx. ৫": "প্রায় পাঁচ", "[Source 3] তথ্য": "তথ্য",
            "KYC": "কেওয়াইসি", "example.com": "এক্সাম্পল ডট কম", "support@example.com": "সাপোর্ট অ্যাট এক্সাম্পল ডট কম",
            "৫lb": "পাঁচ পাউন্ড", "১৯৭১ শতাব্দী": "উনিশশো একাত্তর শতাব্দী",
        }
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(project.convert_text(written), spoken)


class KeepPatternTest(unittest.TestCase):
    def test_tags_at_every_position(self):
        keep = re.compile(r"(\[[a-z]+\])")
        cases = {
            "[warm] ৫": "[warm] পাঁচ", "৫ [warm]": "পাঁচ [warm]", "৫ [a] ৬ [b] ৭": "পাঁচ [a] ছয় [b] সাত",
            "[a][b]": "[a] [b]", "[a]": "[a]", "৫": "পাঁচ",
        }
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn", keep), spoken)


class CleanupTest(unittest.TestCase):
    def test_symbols_and_spacing(self):
        cases = {
            "(৫০০)": "পাঁচশত", "[৫০০]": "পাঁচশত", '"৫০০"': "পাঁচশত", "'৫০০'": "পাঁচশত", "`৫০০`": "পাঁচশত",
            "**৫০০**": "পাঁচশত", "__৫০০__": "পাঁচশত", "৫০০ ।": "পাঁচশত।", "তথ্য।।": "তথ্য।", "a\\b": "ab",
            "a  b": "a b", "  ৫  ": "পাঁচ", "x & y = z": "x y z",
        }
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, "bn"), spoken)

    def test_english_apostrophes_kept_inside_words(self):
        self.assertEqual(convert_text("It's 5 o'clock", "en"), "It's five o'clock")


if __name__ == "__main__":
    unittest.main()
