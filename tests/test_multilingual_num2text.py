"""Every supported case, grouped by category. Run from the project root: python -m unittest discover -s tests"""

import re
import unittest

from multilingual_num2text import (
    BANGLA_LEXICON,
    BanglaLanguage,
    EnglishLanguage,
    Language,
    Lexicon,
    NumberStyle,
    Words,
    available_languages,
    convert_text,
    get_language,
    number_to_text,
    register_language,
)

BANGLA_CASES = {
    'cardinals': [
        ('০', 'শূন্য'),
        ('৫', 'পাঁচ'),
        ('১০', 'দশ'),
        ('১৯', 'উনিশ'),
        ('৩৭', 'সাঁইত্রিশ'),
        ('৮৮', 'অষ্টাশি'),
        ('৯৯', 'নিরানব্বই'),
        ('১০০', 'একশত'),
        ('১০১', 'একশত এক'),
        ('৯৯৯', 'নয়শত নিরানব্বই'),
        ('১০০০', 'এক হাজার'),
        ('১০০১', 'এক হাজার এক'),
        ('১,০০,০০০', 'এক লক্ষ'),
        ('১,২৩,৪৫,৬৭৮', 'এক কোটি তেইশ লক্ষ পঁয়তাল্লিশ হাজার ছয়শত আটাত্তর'),
        ('১০,০০,০০,০০০', 'দশ কোটি'),
        ('১০০০ কোটি', 'এক হাজার কোটি'),
        ('৬৫টি দেশ', 'পঁয়ষট্টিটি দেশ'),
        ('১০জন', 'দশজন'),
        ('মোট৫০০', 'মোট পাঁচশত'),
    ],
    'digit_scripts_and_grouping': [
        ('৫০,000 টাকা', 'পঞ্চাশ হাজার টাকা'),
        ('১২৩,৪৫৬', 'এক লক্ষ তেইশ হাজার চারশত ছাপ্পান্ন'),
        ('১০, ০০০ টাকা', 'দশ হাজার টাকা'),
        ('২৫০, ৫০০ টাকা', 'দুইশত পঞ্চাশ, পাঁচশত টাকা'),
        ('১,২,৩ নম্বর', 'এক, দুই, তিন নম্বর'),
        ('১০\xa0০০০ টাকা', 'দশ হাজার টাকা'),
    ],
    'decimals': [
        ('১.৪৯', 'এক দশমিক চার নয়'),
        ('০.৫', 'শূন্য দশমিক পাঁচ'),
        ('.৫ শতাংশ', 'শূন্য দশমিক পাঁচ শতাংশ'),
        ('১.০৫', 'এক দশমিক শূন্য পাঁচ'),
        ('২.৬০', 'দুই দশমিক ছয়'),
        ('৭,০০০.০০', 'সাত হাজার'),
        ('২.৫০০ কেজি', 'আড়াই কেজি'),
        ('-২.৫', 'ঋণাত্মক দুই দশমিক পাঁচ'),
    ],
    'negatives': [
        ('-৫ ডিগ্রি', 'ঋণাত্মক পাঁচ ডিগ্রি'),
        ('−১০', 'ঋণাত্মক দশ'),
        ('-৫°C', 'ঋণাত্মক পাঁচ ডিগ্রি সেলসিয়াস'),
    ],
    'percentages': [
        ('১.৪৯%', 'এক দশমিক চার নয় শতাংশ'),
        ('৯০%', 'নব্বই শতাংশ'),
        ('৫ %', 'পাঁচ শতাংশ'),
        ('-২.৫%', 'ঋণাত্মক দুই দশমিক পাঁচ শতাংশ'),
        ('৫-১০%', 'পাঁচ থেকে দশ শতাংশ'),
        ('০.০১%', 'শূন্য দশমিক শূন্য এক শতাংশ'),
    ],
    'money': [
        ('২,৫০,০০০ টাকা', 'দুই লক্ষ পঞ্চাশ হাজার টাকা'),
        ('৳১,২৫০.৫০', 'এক হাজার দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা'),
        ('৳ ১২৩', 'একশত তেইশ টাকা'),
        ('৳০.৫০', 'পঞ্চাশ পয়সা'),
        ('৳০', 'শূন্য টাকা'),
        ('১০.৫০ টাকার', 'দশ টাকা পঞ্চাশ পয়সার'),
        ('১০.৫ টাকা', 'দশ টাকা পঞ্চাশ পয়সা'),
        ('৫০০/-', 'পাঁচশত টাকা'),
        ('৳১০০০/-', 'এক হাজার টাকা'),
        ('৳৫০০ টাকা', 'পাঁচশত টাকা'),
        ('Tk 500', 'পাঁচশত টাকা'),
        ('500 tk', 'পাঁচশত টাকা'),
        ('BDT 1,500', 'এক হাজার পাঁচশত টাকা'),
        ('৫০০ টাকা ২ বার', 'পাঁচশত টাকা দুই বার'),
        ('০৫ টাকা', 'পাঁচ টাকা'),
        ('if৳১২৩', 'if একশত তেইশ টাকা'),
        ('দাম$৫', 'দাম পাঁচ ডলার'),
        ('$১০.৫০', 'দশ ডলার পঞ্চাশ সেন্ট'),
        ('$৫.৫', 'পাঁচ ডলার পঞ্চাশ সেন্ট'),
        ('৳৫ লাখ', 'পাঁচ লাখ টাকা'),
        ('৳২.৫ কোটি', 'আড়াই কোটি টাকা'),
        ('৫০০-১০০০ টাকা', 'পাঁচশত থেকে এক হাজার টাকা'),
    ],
    'world_currencies': [
        ('SAR ৫০.২৫', 'পঞ্চাশ সৌদি রিয়াল পঁচিশ হালালা'),
        ('৫০ সৌদি রিয়াল', 'পঞ্চাশ সৌদি রিয়াল'),
        ('১০০ রিয়ালের', 'একশত সৌদি রিয়ালের'),
        ('KWD ১.২৫০', 'এক কুয়েতি দিনার দুইশত পঞ্চাশ ফিলস'),
        ('¥৫০০', 'পাঁচশত জাপানি ইয়েন'),
        ('¥৫০০.৫০', 'পাঁচশত দশমিক পাঁচ জাপানি ইয়েন'),
        ('A$২০', 'বিশ অস্ট্রেলিয়ান ডলার'),
        ('৫০০ AUD', 'পাঁচশত অস্ট্রেলিয়ান ডলার'),
        ('₩১০০০', 'এক হাজার দক্ষিণ কোরিয়ান উওন'),
        ('RM ৫০', 'পঞ্চাশ মালয়েশিয়ান রিঙ্গিত'),
        ('৫০ মার্কিন ডলার', 'পঞ্চাশ ডলার'),
        ('£২.৫০', 'দুই পাউন্ড পঞ্চাশ পেনি'),
        ('€১', 'এক ইউরো'),
        ('₹৯৯.৯৯', 'নিরানব্বই রুপি নিরানব্বই পয়সা'),
        ('২.৫ পাউন্ড ওজন', 'দুই দশমিক পাঁচ পাউন্ড ওজন'),
    ],
    'phones': [
        ('০১৭১১১২৩৪৫৬', 'শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয়'),
        ('০১৭১১-১২৩৪৫৬', 'শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয়'),
        ('০১৭১১ ১২৩৪৫৬', 'শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয়'),
        ('০১৭১১ ১২৩৪৫৬ নম্বরে ৫০০ টাকা', 'শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয় নম্বরে পাঁচশত টাকা'),
        ('+৮৮০ ১৭১১ ১২৩৪৫৬', 'প্লাস আট আট শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয়'),
        ('+৮৮০১৭১১১২৩৪৫৬', 'প্লাস আট আট শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয়'),
        ('+৮৮-০২-৫৫৬৬৩০০১', 'প্লাস আট আট শূন্য দুই পাঁচ পাঁচ ছয় ছয় তিন শূন্য শূন্য এক'),
        ('(০২) ৯৫৬৬৩০০১', 'শূন্য দুই নয় পাঁচ ছয় ছয় তিন শূন্য শূন্য এক'),
        ('পিন ০১২৩', 'পিন শূন্য এক দুই তিন'),
        ('০০', 'শূন্য শূন্য'),
        ('২০ জিবি+২০০ মিনিট', 'বিশ জিবি দুইশত মিনিট'),
    ],
    'codes_and_account_numbers': [
        ('*123#', 'স্টার এক দুই তিন হ্যাশ'),
        ('*১২৩#', 'স্টার এক দুই তিন হ্যাশ'),
        ('*১৬৭*১#', 'স্টার এক ছয় সাত স্টার এক হ্যাশ'),
        ('#১২৩', 'হ্যাশ এক দুই তিন'),
        ('**৫০০** টাকা', 'পাঁচশত টাকা'),
        ('১৬,২৪৭ টাকা', 'ষোলো হাজার দুইশত সাতচল্লিশ টাকা'),
        ('১২৩৪৫৬৭৮৯০১২', 'এক দুই তিন চার পাঁচ ছয় সাত আট নয় শূন্য এক দুই'),
        ('১২৩৪-৫৬৭৮-৯০১২', 'এক দুই তিন চার পাঁচ ছয় সাত আট নয় শূন্য এক দুই'),
        ('১২৩৪ ৫৬৭৮ ৯০১২ ৩৪৫৬', 'এক দুই তিন চার পাঁচ ছয় সাত আট নয় শূন্য এক দুই তিন চার পাঁচ ছয়'),
        ('১০০০০০০০ টাকা', 'এক কোটি টাকা'),
    ],
    'dates': [
        ('১০/০৫/২০২৪', 'দশই মে দুই হাজার চব্বিশ'),
        ('২০২৪-০৫-১০', 'দশই মে দুই হাজার চব্বিশ'),
        ('১০-০৫-২০২৪', 'দশই মে দুই হাজার চব্বিশ'),
        ('১০.০৫.২০২৪', 'দশই মে দুই হাজার চব্বিশ'),
        ('১২/২৫/২০২৪', 'পঁচিশে ডিসেম্বর দুই হাজার চব্বিশ'),
        ('১০ মে ২০২৪', 'দশই মে দুই হাজার চব্বিশ'),
        ('০৫ মে', 'পাঁচই মে'),
        ('৩১ ডিসেম্বরের মধ্যে', 'একত্রিশে ডিসেম্বরের মধ্যে'),
        ('১৫ শ্রাবণ', 'পনেরোই শ্রাবণ'),
        ('১লা বৈশাখ', 'পহেলা বৈশাখ'),
        ('২১শে ফেব্রুয়ারি', 'একুশে ফেব্রুয়ারি'),
        ('১০ই মে', 'দশই মে'),
        ('৫ মেয়ে', 'পাঁচ মেয়ে'),
    ],
    'years': [
        ('১৯৭১ সালে', 'উনিশশো একাত্তর সালে'),
        ('২০২৪ সালের', 'দুই হাজার চব্বিশ সালের'),
        ('১৪৩১ বঙ্গাব্দ', 'চৌদ্দশো একত্রিশ বঙ্গাব্দ'),
        ('২০২৪-২৫ অর্থবছর', 'দুই হাজার চব্বিশ পঁচিশ অর্থবছর'),
        ('১৯৭১-৭২ সালে', 'উনিশশো একাত্তর বাহাত্তর সালে'),
        ('২০২০-২০২৪', 'দুই হাজার বিশ থেকে দুই হাজার চব্বিশ'),
    ],
    'times': [
        ('১০:৩০', 'দশটা ত্রিশ মিনিট'),
        ('০৯:০৫', 'নয়টা পাঁচ মিনিট'),
        ('১৫:৪৫', 'দুপুর তিনটা পঁয়তাল্লিশ মিনিট'),
        ('০০:১৫', 'রাত বারোটা পনেরো মিনিট'),
        ('২৪:০০', 'রাত বারোটা'),
        ('১০:৩০:২০', 'দশটা ত্রিশ মিনিট বিশ সেকেন্ড'),
        ('১০:৩০ PM', 'রাত দশটা ত্রিশ মিনিট'),
        ('১০ AM', 'সকাল দশটা'),
        ('১২ PM', 'দুপুর বারোটা'),
    ],
    'ratios': [
        ('১:২', 'এক অনুপাত দুই'),
        ('১০:৭৫', 'দশ অনুপাত পঁচাত্তর'),
    ],
    'ordinals': [
        ('১ম, ২য়, ৩য়, ৪র্থ, ৫ম, ৬ষ্ঠ, ১০ম', 'প্রথম, দ্বিতীয়, তৃতীয়, চতুর্থ, পঞ্চম, ষষ্ঠ, দশম'),
        ('১১তম', 'এগারোতম'),
        ('১০০তম', 'একশততম'),
    ],
    'ranges_slashes_lists': [
        ('৫০০-১০০০', 'পাঁচশত থেকে এক হাজার'),
        ('৫–১০ দিন', 'পাঁচ থেকে দশ দিন'),
        ('৬/১২/২৪ মাস', 'ছয়, বারো, চব্বিশ মাস'),
        ('১২/৩ নম্বর বাসা', 'বারো বাই তিন নম্বর বাসা'),
        ('24/7', 'চব্বিশ ঘণ্টা সাত দিন'),
    ],
    'fractions': [
        ('২.৫ লাখ টাকা', 'আড়াই লাখ টাকা'),
        ('১.৫ ঘণ্টা', 'দেড় ঘণ্টা'),
        ('৩.৫ কোটি', 'সাড়ে তিন কোটি'),
        ('১.২৫ ঘণ্টা', 'সোয়া এক ঘণ্টা'),
        ('২.৭৫ লাখ', 'পৌনে তিন লাখ'),
        ('২½ কেজি', 'আড়াই কেজি'),
        ('½ লিটার', 'আধা লিটার'),
        ('¼ অংশ', 'এক চতুর্থাংশ অংশ'),
    ],
    'units_and_magnitudes': [
        ('২০GB ডাটা', 'বিশ জিবি ডাটা'),
        ('৫ km', 'পাঁচ কিলোমিটার'),
        ('৩৫°C', 'পঁয়ত্রিশ ডিগ্রি সেলসিয়াস'),
        ('৫K ফলোয়ার', 'পাঁচ হাজার ফলোয়ার'),
        ('২.৫K টাকা', 'দুই হাজার পাঁচশত টাকা'),
    ],
    'arithmetic': [
        ('২+২=৪', 'দুই যোগ দুই সমান চার'),
        ('১০×৫', 'দশ গুণ পাঁচ'),
        ('১০÷২', 'দশ ভাগ দুই'),
        ('৫০০+ গ্রাহক', 'পাঁচশত প্লাস গ্রাহক'),
    ],
    'dotted_numbers': [
        ('১.২.৩ ভার্সন', 'এক ডট দুই ডট তিন ভার্সন'),
        ('১৯২.১৬৮.০.১', 'একশত বিরানব্বই ডট একশত আটষট্টি ডট শূন্য ডট এক'),
    ],
    'text_cleanup': [
        ('ATM থেকে OTP দিয়ে', 'এটিএম থেকে ওটিপি দিয়ে'),
        ('support@example.com এ', 'support অ্যাট example ডট কম এ'),
        ('user123@example.com', 'user এক দুই তিন অ্যাট example ডট কম'),
        ('https://www.example.com/offers দেখুন।', 'ডাব্লিউ ডাব্লিউ ডাব্লিউ ডট example ডট কম দেখুন।'),
        ('https://example.org:8080/x', 'example ডট অর্গ'),
        ('shop.example.com.bd এ যান', 'shop ডট example ডট কম ডট বিডি এ যান'),
        ('উদাহরণ.com', 'উদাহরণ ডট কম'),
        ('ক + খ', 'ক এবং খ'),
        ('তথ্য।।', 'তথ্য।'),
        ('`৫০০`', 'পাঁচশত'),
        ('কোনো সংখ্যা নেই', 'কোনো সংখ্যা নেই'),
    ],
}

ENGLISH_CASES = {
    'cardinals': [
        ('0', 'zero'),
        ('15', 'fifteen'),
        ('42', 'forty-two'),
        ('100', 'one hundred'),
        ('101', 'one hundred one'),
        ('1001', 'one thousand one'),
        ('1,000,000', 'one million'),
        ('2,50,000 people', 'two hundred fifty thousand people'),
        ('covid19 cases', 'covid nineteen cases'),
    ],
    'decimals': [
        ('2.60', 'two point six'),
        ('0.5', 'zero point five'),
        ('.5 percent', 'zero point five percent'),
        ('-1.25', 'minus one point two five'),
        ('Version 2.0', 'Version two'),
    ],
    'percentages': [
        ('1.49%', 'one point four nine percent'),
        ('90%', 'ninety percent'),
        ('-2.5%', 'minus two point five percent'),
    ],
    'money': [
        ('$1,250.50', 'one thousand two hundred fifty dollars and fifty cents'),
        ('$1', 'one dollar'),
        ('$0.01', 'one cent'),
        ('1 Dollar', 'one dollar'),
        ('10 DOLLARS', 'ten dollars'),
        ('৳500', 'five hundred taka'),
        ('500 taka', 'five hundred taka'),
        ('$5 million', 'five million dollars'),
        ('$2.5 billion', 'two point five billion dollars'),
        ('₹5 lakh', 'five lakh rupees'),
        ('$5.5', 'five dollars and fifty cents'),
    ],
    'world_currencies': [
        ('SAR 50.25', 'fifty Saudi riyals and twenty-five halalas'),
        ('KWD 1.250', 'one Kuwaiti dinar and two hundred fifty fils'),
        ('¥500', 'five hundred yen'),
        ('A$20', 'twenty Australian dollars'),
        ('50 Australian dollars', 'fifty Australian dollars'),
        ('£2.50', 'two pounds and fifty pence'),
        ('2.5 pounds of rice', 'two point five pounds of rice'),
        ('€1', 'one euro'),
        ('₹99.99', 'ninety-nine rupees and ninety-nine paise'),
        ('RM 50.50', 'fifty ringgit and fifty sen'),
        ('₩5000', 'five thousand South Korean won'),
        ('ALL 500', 'five hundred Albanian lekë'),
        ('all 5 items', 'all five items'),
        ('5 ft tall', 'five ft tall'),
        ('5000 won the game', 'five thousand won the game'),
    ],
    'phones_and_codes': [
        ('01711-123456', 'zero one seven one one one two three four five six'),
        ('+880 1711 123456', 'plus eight eight zero one seven one one one two three four five six'),
        ('(02) 95663001', 'zero two nine five six six three zero zero one'),
        ('*123#', 'star one two three hash'),
        ('account 123456789012', 'account one two three four five six seven eight nine zero one two'),
        ('1234 5678 9012 3456', 'one two three four five six seven eight nine zero one two three four five six'),
    ],
    'dates': [
        ('10/05/2024', 'the tenth of May, twenty twenty-four'),
        ('May 10, 2024', 'May tenth, twenty twenty-four'),
        ('10 May 2024', 'the tenth of May, twenty twenty-four'),
        ('10th of May', 'the tenth of May'),
        ('Jan 5', 'January fifth'),
        ('Dec. 25th', 'December twenty-fifth'),
        ('May 2024', 'May twenty twenty-four'),
        ('you may 5', 'you may five'),
    ],
    'years_and_decades': [
        ('in 1971', 'in nineteen seventy-one'),
        ('in 1905', 'in nineteen oh five'),
        ('in 2005', 'in two thousand five'),
        ('2024 AD', 'twenty twenty-four AD'),
        ('FY 2024-25', 'FY twenty twenty-four twenty-five'),
        ('the 1990s', 'the nineteen nineties'),
        ("the '80s", 'the eighties'),
        ('the 2000s', 'the two thousands'),
    ],
    'times': [
        ('10:30', 'ten thirty'),
        ('10:05', 'ten oh five'),
        ('10:00', "ten o'clock"),
        ('15:45', 'three forty-five PM'),
        ('10:30 PM', 'ten thirty PM'),
        ('10 AM', 'ten AM'),
        ('12 PM', 'twelve PM'),
        ('12 AM', 'twelve AM'),
        ('10:30 a.m.', 'ten thirty AM'),
    ],
    'ratios': [
        ('1:2', 'one to two'),
    ],
    'ordinals': [
        ('1st, 2nd, 3rd, 12th, 21st, 100th', 'first, second, third, twelfth, twenty-first, one hundredth'),
    ],
    'ranges_and_lists': [
        ('500-1000 dollars', 'five hundred to one thousand dollars'),
        ('5-10%', 'five to ten percent'),
        ('1,2,3 items', 'one, two, three items'),
        ("It's 24/7 support", "It's twenty-four seven support"),
    ],
    'fractions': [
        ('2½ kg', 'two and a half kg'),
        ('½ cup', 'one half cup'),
    ],
    'units_and_magnitudes': [
        ('20km away', 'twenty kilometers away'),
        ('35°C', 'thirty-five degrees Celsius'),
        ('2.5K followers', 'two thousand five hundred followers'),
    ],
    'arithmetic': [
        ('2+2=4', 'two plus two equals four'),
        ('500+ users', 'five hundred plus users'),
    ],
    'text_cleanup': [
        ('version 1.2.3', 'version one dot two dot three'),
        ('Email support@example.com', 'Email support at example dot com'),
        ('user123@example.com', 'user one two three at example dot com'),
        ('-5 degrees', 'minus five degrees'),
    ],
}


class ConvertTextTest(unittest.TestCase):
    def test_bangla(self):
        self._check_all("bn", BANGLA_CASES)

    def test_english(self):
        self._check_all("en", ENGLISH_CASES)

    def test_no_digit_survives(self):
        for lang, categories in (("bn", BANGLA_CASES), ("en", ENGLISH_CASES)):
            for category, cases in categories.items():
                for written, _ in cases:
                    with self.subTest(lang=lang, category=category, written=written):
                        self.assertIsNone(re.search(r"\d", convert_text(written, lang)))

    def test_empty_and_blank_text(self):
        for lang in ("bn", "en"):
            with self.subTest(lang=lang):
                self.assertEqual(convert_text("", lang), "")
                self.assertEqual(convert_text("   ", lang), "")

    def test_full_sentence(self):
        written = (
            "আপনার অ্যাকাউন্ট ০১৭১১-১২৩৪৫৬ থেকে ১০ মে ২০২৪ তারিখে সকাল ১০:৩০ এ ৳১,২৫০.৫০ পাঠানো হয়েছে। "
            "চার্জ ১.৮৫%। বিস্তারিত: *123# ডায়াল করুন।"
        )
        spoken = (
            "আপনার অ্যাকাউন্ট শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয় থেকে দশই মে দুই হাজার চব্বিশ তারিখে "
            "সকাল দশটা ত্রিশ মিনিট এ এক হাজার দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা পাঠানো হয়েছে। "
            "চার্জ এক দশমিক আট পাঁচ শতাংশ। বিস্তারিত: স্টার এক দুই তিন হ্যাশ ডায়াল করুন।"
        )
        self.assertEqual(convert_text(written, "bn"), spoken)

    def test_keep_pattern_passes_tags_through(self):
        keep = re.compile(r"(\[[a-z]+\])")
        self.assertEqual(convert_text("[warm] ৫০০ টাকা [calm]", "bn", keep), "[warm] পাঁচশত টাকা [calm]")

    def _check_all(self, lang, categories):
        for category, cases in categories.items():
            for written, spoken in cases:
                with self.subTest(category=category, written=written):
                    self.assertEqual(convert_text(written, lang), spoken)


class SingleNumberTest(unittest.TestCase):
    def test_styles(self):
        cases = [
            (2712, "bn", NumberStyle.CARDINAL, "দুই হাজার সাতশত বারো"),
            (2712, "bn", NumberStyle.DIGITWISE, "দুই সাত এক দুই"),
            ("২৭১২", "bn", "digitwise", "দুই সাত এক দুই"),
            ("১,২৫০.৫০", "bn", "cardinal", "এক হাজার দুইশত পঞ্চাশ দশমিক পাঁচ"),
            (-15, "bn", "cardinal", "ঋণাত্মক পনেরো"),
            (2.5, "bn", "cardinal", "দুই দশমিক পাঁচ"),
            ("৳১,২৫০.৫০", "bn", "auto", "এক হাজার দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা"),
            ("০১৭১১১২৩৪৫৬", "bn", "auto", "শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয়"),
            ("*123#", "bn", "auto", "স্টার এক দুই তিন হ্যাশ"),
            (2712, "en", "cardinal", "two thousand seven hundred twelve"),
            (2712, "en", "digitwise", "two seven one two"),
            ("*123#", "en", "auto", "star one two three hash"),
            (-1.25, "en", "cardinal", "minus one point two five"),
        ]
        for value, lang, style, expected in cases:
            with self.subTest(value=value, lang=lang, style=style):
                self.assertEqual(number_to_text(value, lang, style), expected)

    def test_bangla_word_table(self):
        bangla = get_language("bn")
        expected = {
            0: "শূন্য", 11: "এগারো", 37: "সাঁইত্রিশ", 53: "তিপ্পান্ন", 56: "ছাপ্পান্ন", 88: "অষ্টাশি", 99: "নিরানব্বই",
            250000: "দুই লক্ষ পঞ্চাশ হাজার", 1_000_000_000: "একশত কোটি",
        }
        for number, words in expected.items():
            with self.subTest(number=number):
                self.assertEqual(bangla.to_cardinal(number), words)

    def test_english_words(self):
        english = get_language("en")
        expected = {
            0: "zero", 15: "fifteen", 42: "forty-two", 100: "one hundred", 1001: "one thousand one",
            1_000_000: "one million", 2_500_000_000: "two billion five hundred million",
        }
        for number, words in expected.items():
            with self.subTest(number=number):
                self.assertEqual(english.to_cardinal(number), words)

    def test_english_indian_scales(self):
        self.assertEqual(EnglishLanguage(indian_scales=True).convert_text("2,50,000 people"), "two lakh fifty thousand people")

    def test_rejects_non_numbers(self):
        with self.assertRaises(ValueError):
            number_to_text("abc", "bn")

    def test_rejects_unknown_language(self):
        with self.assertRaises(ValueError):
            number_to_text(5, "xx-unknown")


class CustomLanguageTest(unittest.TestCase):
    """A new language only needs Words, a Lexicon and five methods."""

    def test_register_and_use(self):
        def letters(number):
            return "".join("abcdefghij"[int(digit)] for digit in str(number))

        class LetterLanguage(Language):
            code = "test-letters"
            words = Words(
                digits=tuple("abcdefghij"),
                negative="neg", decimal_point="pt", percent="pc", range="to", slash="sl",
                ratio="ra", dot="dt", at="at", star="st", hash="hs", plus="pl",
            )
            lexicon = Lexicon()

            def to_cardinal(self, number):
                return f"n{letters(number)}"

            def to_ordinal(self, number):
                return f"o{letters(number)}"

            def to_year(self, year):
                return f"y{letters(year)}"

            def to_date(self, day, month, year=None):
                return f"date {letters(day)} {letters(month)}"

            def to_time(self, hour, minute=0, second=None, with_period=False):
                return f"time {letters(hour)} {letters(minute)}"

        register_language(LetterLanguage())
        self.assertIn("test-letters", available_languages())
        self.assertEqual(
            convert_text("5 and 1.5% at 10:30, 017", "test-letters"),
            "nf and nb pt f pc at time ba da, a b h",
        )


class ProjectDataTest(unittest.TestCase):
    """Project data (hotlines, brand names, citation tags) stays outside the package: add it with Lexicon.extended()."""

    def setUp(self):
        lexicon = BANGLA_LEXICON.extended(
            digitwise_numbers=("54321",),
            domain_words={"example": "এক্সাম্পল"},
            email_name_words={"support": "সাপোর্ট"},
            removed_patterns=(r"\[Source\s*\d*\]",),
            acronyms={"KYC": "কেওয়াইসি"},
            word_replacements={"চুয়ান্ন হাজার তিনশত একুশ": "পাঁচ চার তিন দুই এক"},
        )
        self.project = BanglaLanguage(lexicon=lexicon)

    def test_project_data_applies(self):
        cases = [
            ("[Source 1] ৫৪৩২১ বা ৫৪3২১ নম্বরে কল করুন", "পাঁচ চার তিন দুই এক বা পাঁচ চার তিন দুই এক নম্বরে কল করুন"),
            ("support@example.com", "সাপোর্ট অ্যাট এক্সাম্পল ডট কম"),
            ("KYC ও ATM", "কেওয়াইসি ও এটিএম"),
            ("চুয়ান্ন হাজার তিনশত একুশ", "পাঁচ চার তিন দুই এক"),
            ("৳৫০০", "পাঁচশত টাকা"),
        ]
        for written, spoken in cases:
            with self.subTest(written=written):
                self.assertEqual(self.project.convert_text(written), spoken)

    def test_built_in_language_is_unchanged(self):
        self.assertEqual(convert_text("৫৪৩২১", "bn"), "চুয়ান্ন হাজার তিনশত একুশ")
        self.assertEqual(convert_text("[Source 1]", "bn"), "Source এক")
        self.assertNotIn("example", BANGLA_LEXICON.domain_words)

    def test_register_under_own_code(self):
        register_language(self.project, code="bn-project")
        self.assertEqual(convert_text("৫৪৩২১", "bn-project"), "পাঁচ চার তিন দুই এক")


if __name__ == "__main__":
    unittest.main()
