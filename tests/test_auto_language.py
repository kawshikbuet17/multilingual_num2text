"""lang="auto": every case. Each sentence is converted in the language it is written in."""

import re
import unittest

from multilingual_num2text import (
    BANGLA_LEXICON,
    ENGLISH_LEXICON,
    BanglaLanguage,
    EnglishLanguage,
    Language,
    Lexicon,
    Words,
    convert_text,
    detect_language,
    detect_sentence_languages,
    get_language,
    number_to_text,
    register_language,
    split_sentences,
    unregister_language,
)
from test_multilingual_num2text import BANGLA_CASES, ENGLISH_CASES

DETECTION_CASES = {
    'words decide': [
        ('Send $5', 'en'),
        ('৳৫০০ পাঠান', 'bn'),
        ('Your ব্যালেন্স is $5 today', 'en'),
        ('আপনার ব্যালেন্স 500 টাকা', 'bn'),
        ('আপনার account এ ৫০০ টাকা পাঠানো হয়েছে', 'bn'),
        ('Cash out charge ১.৮৫%', 'en'),
        ('Meeting on ৫ মে ২০২৪ at 3 PM', 'en'),
    ],
    'word tie: own digits decide, then the first word': [
        ('আপনার balance ৳৫০০', 'bn'),
        ('Balance ৫০০ টাকা', 'bn'),
        ('Send Money ফি ৫ টাকা', 'bn'),
        ('আপনার balance 500', 'bn'),
        ('balance আপনার 500', 'en'),
        ('ab কখ', 'en'),
        ('কখ ab', 'bn'),
        ('hi مرحبا', 'en'),
        ('مرحبا hi', None),
    ],
    'not counted: acronyms, addresses, abbreviations, tags': [
        ('OTP কোড 123456', 'bn'),
        ('PIN দিন: 1234', 'bn'),
        ('ATM থেকে টাকা তুলুন', 'bn'),
        ('যোগাযোগ: customer.support@example.com অথবা ০১৭১১-১২৩৪৫৬', 'bn'),
        ('বিস্তারিত জানতে visit করুন https://www.example.com/offers', 'bn'),
        ('e.g. ৫০০ টাকা', 'bn'),
        ('Dr. রহিম', 'bn'),
        ('ডা. Rahman', 'en'),
    ],
    'digits decide when there are no words': [
        ('1', 'en'),
        ('১', 'bn'),
        ('2712', 'en'),
        ('২৭১২', 'bn'),
        ('৳৫০০', 'bn'),
        ('+৮৮০', 'bn'),
        ('$5', 'en'),
        ('OTP 1234', 'en'),
        ('OTP ১২৩৪', 'bn'),
    ],
    'mixed digits: most digits win': [
        ('5০০০', 'bn'),
        ('500০', 'en'),
        ('৫০,000', 'en'),
        ('৫০,০০০', 'bn'),
        ('৫,০00,000', 'en'),
    ],
    'digit tie: the first digit wins': [
        ('50০০', 'en'),
        ('৫০00', 'bn'),
        ('5০', 'en'),
        ('৫0', 'bn'),
    ],
    'unsupported language': [
        ('مرحبا 500', None),
        ('नमस्ते १२३', None),
        ('१२३', None),
        ('٤٥', None),
        ('Привет 5', None),
        ('مرحبا hello', None),
        ('hello مرحبا', 'en'),
        ('مرحبا مرحبا hello', None),
        ('hello hello مرحبا', 'en'),
    ],
    'no words or digits': [
        ('', 'en'),
        ('   ', 'en'),
        ('৳', 'en'),
        ('$%', 'en'),
    ],
}

SENTENCE_CASES = {
    'split': [
        ('Pay $5 now. ৫০০ টাকা দিন।', ['Pay $5 now. ', '৫০০ টাকা দিন।']),
        ('এক। দুই। তিন', ['এক। ', 'দুই। ', 'তিন']),
        ('Hi! Bye? Ok', ['Hi! ', 'Bye? ', 'Ok']),
        ('line one\nline two', ['line one\n', 'line two']),
        ('First. Second', ['First. ', 'Second']),
        ('Hello. مرحبا 500. ৫০০ টাকা।', ['Hello. ', 'مرحبا 500. ', '৫০০ টাকা।']),
        ('Price $5.50. Thanks', ['Price $5.50. ', 'Thanks']),
        ('Wait... ৫০০ টাকা দিন', ['Wait... ', '৫০০ টাকা দিন']),
        ('Pay Tk. 500. ৫০০ টাকা দিন।', ['Pay Tk. 500. ', '৫০০ টাকা দিন।']),
        ('Mrs. Rahman paid $5. ধন্যবাদ।', ['Mrs. Rahman paid $5. ', 'ধন্যবাদ।']),
        ('ডা. রহিম ৫০০ টাকা দিলেন। Thanks!', ['ডা. রহিম ৫০০ টাকা দিলেন। ', 'Thanks!']),
        ('Steps:\n১. Open app\n২. Login', ['Steps:\n', '১. Open app\n', '২. Login']),
        ('তথ্য।।', ['তথ্য।।']),
    ],
    'not split': [
        ('Dec. 25th', ['Dec. 25th']),
        ('e.g. this one', ['e.g. this one']),
        ('10:30 a.m. today', ['10:30 a.m. today']),
        ('1.5 kg', ['1.5 kg']),
        ('example.com/?page=2', ['example.com/?page=2']),
        ('v1.2.3', ['v1.2.3']),
        ('Wow!Really', ['Wow!Really']),
        ('৳১,২৫০.৫০', ['৳১,২৫০.৫০']),
        ('Tk. ৫০০ মাত্র', ['Tk. ৫০০ মাত্র']),
        ('Rs. ৫০০ মাত্র', ['Rs. ৫০০ মাত্র']),
        ('BDT. 500 only', ['BDT. 500 only']),
        ('ডা. রহিম', ['ডা. রহিম']),
        ('মো. করিম ৫০০ টাকা', ['মো. করিম ৫০০ টাকা']),
        ('No. 5', ['No. 5']),
        ('U.S. dollars', ['U.S. dollars']),
        ('Mr. Karim, call 01711-123456.', ['Mr. Karim, call 01711-123456.']),
        ('Dr. Rahman paid $5', ['Dr. Rahman paid $5']),
        ('etc. ৫০০ টাকা', ['etc. ৫০০ টাকা']),
        ('১০.০৫.২০২৪', ['১০.০৫.২০২৪']),
        ('১. Open app', ['১. Open app']),
        ('১। প্রথম ধাপ', ['১। প্রথম ধাপ']),
        ('ধন্যবাদ।আপনার ৫০০ টাকা', ['ধন্যবাদ।আপনার ৫০০ টাকা']),
        ('ধাপ ২. টাকা', ['ধাপ ২. টাকা']),
    ],
    'blank': [
        ('', []),
        ('   ', []),
    ],
}

AUTO_CASES = {
    'standalone numbers follow their digits': [
        ('1', 'one'),
        ('১', 'এক'),
        ('2712', 'two thousand seven hundred twelve'),
        ('২৭১২', 'দুই হাজার সাতশত বারো'),
        ('300', 'three hundred'),
    ],
    'mixed digits are one number': [
        ('50০০', 'five thousand'),
        ('৫০00', 'পাঁচ হাজার'),
        ('5০০০', 'পাঁচ হাজার'),
        ('500০', 'five thousand'),
        ('৫০,000', 'fifty thousand'),
        ('৫০,০০০', 'পঞ্চাশ হাজার'),
    ],
    'numbers follow their sentence': [
        ('আপনার 50০০ টাকা', 'আপনার পাঁচ হাজার টাকা'),
        ('Pay 50০০ taka', 'Pay five thousand taka'),
        ('আপনার ব্যালেন্স 500 টাকা', 'আপনার ব্যালেন্স পাঁচশত টাকা'),
        ('Your ৫০০ taka', 'Your five hundred taka'),
        ('Your balance is ৳৫০০', 'Your balance is five hundred taka'),
        ('Pay ৳500 now', 'Pay five hundred taka now'),
        ('Call ১৬২৪৭ for help', 'Call sixteen thousand two hundred forty-seven for help'),
    ],
    'code-mixed sentences': [
        ('আপনার balance ৳৫০০', 'আপনার balance পাঁচশত টাকা'),
        ('আপনার balance 500', 'আপনার balance পাঁচশত'),
        ('Balance ৫০০ টাকা', 'Balance পাঁচশত টাকা'),
        ('Send Money ফি ৫ টাকা', 'Send Money ফি পাঁচ টাকা'),
        ('আপনার account এ ৫০০ টাকা পাঠানো হয়েছে', 'আপনার account এ পাঁচশত টাকা পাঠানো হয়েছে'),
        ('আপনার bKash account এ 500 টাকা জমা হয়েছে', 'আপনার bKash account এ পাঁচশত টাকা জমা হয়েছে'),
        ('মোট amount 1,500 টাকা', 'মোট amount এক হাজার পাঁচশত টাকা'),
        ('Cash out charge ১.৮৫%', 'Cash out charge one point eight five percent'),
        ('Amount: 500 (৫০০ টাকা)', 'Amount: পাঁচশত পাঁচশত টাকা'),
    ],
    'codes after OTP, PIN, code, ID': [
        ('OTP কোড 123456', 'ওটিপি কোড এক দুই তিন চার পাঁচ ছয়'),
        ('PIN দিন: 1234', 'পিন দিন: এক দুই তিন চার'),
        ('আপনার ওটিপি কোডটি হলো ৪৮২৯১৩', 'আপনার ওটিপি কোডটি হলো চার আট দুই নয় এক তিন'),
        ('Your OTP is 482913.', 'Your OTP is four eight two nine one three.'),
        ('Transaction ID: 9876543', 'Transaction ID: nine eight seven six five four three'),
        ('OTP দিয়ে, ১০০০ টাকা দিন', 'ওটিপি দিয়ে, এক হাজার টাকা দিন'),
    ],
    'emails and web addresses do not decide': [
        ('যোগাযোগ: customer.support@example.com অথবা ০১৭১১-১২৩৪৫৬', 'যোগাযোগ: customer ডট support অ্যাট example ডট কম অথবা শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয়'),
        ('বিস্তারিত জানতে visit করুন https://www.example.com/offers?ref=123', 'বিস্তারিত জানতে visit করুন ডাব্লিউ ডাব্লিউ ডাব্লিউ ডট example ডট কম'),
        ('ইমেইল করুন help@example.com এ, ২৪ ঘণ্টার মধ্যে উত্তর পাবেন', 'ইমেইল করুন help অ্যাট example ডট কম এ, চব্বিশ ঘণ্টার মধ্যে উত্তর পাবেন'),
    ],
    'sentences without words take their context': [
        ('মোট পরিমাণ:\n৫০০\n300', 'মোট পরিমাণ: পাঁচশত তিনশত'),
        ('আপনার ব্যালেন্স।\n500 টাকা', 'আপনার ব্যালেন্স। পাঁচশত টাকা'),
        ('500\nআপনার ব্যালেন্স', 'পাঁচশত আপনার ব্যালেন্স'),
        ('Total:\n৫০০', 'Total: five hundred'),
        ('Steps:\n১. Open app\n২. Login', 'Steps: one. Open app two. Login'),
        ('১. প্রথম ধাপ\n2. দ্বিতীয় ধাপ', 'এক. প্রথম ধাপ দুই. দ্বিতীয় ধাপ'),
    ],
    'abbreviations': [
        ('Mr. Karim, call 01711-123456.', 'Mr. Karim, call zero one seven one one one two three four five six.'),
        ('Mrs. Rahman paid $5. ধন্যবাদ।', 'Mrs. Rahman paid five dollars. ধন্যবাদ।'),
        ('Dr. Rahman paid $5', 'Dr. Rahman paid five dollars'),
        ('e.g. ৫০০ টাকা', 'e.g. পাঁচশত টাকা'),
        ('etc. ৫০০ টাকা', 'etc. পাঁচশত টাকা'),
        ('ডা. রহিম ৫০০ টাকা দিলেন। Thanks!', 'ডা. রহিম পাঁচশত টাকা দিলেন। Thanks!'),
        ('মো. করিম ৫০০ টাকা পাঠিয়েছেন', 'মো. করিম পাঁচশত টাকা পাঠিয়েছেন'),
        ('U.S. dollars 5', 'U.S. dollars five'),
        ('No. 5 is next', 'No. five is next'),
    ],
    'dates and times in mixed text': [
        ('আপনার মিটিং 2/3/24 তারিখে 10:30 AM এ', 'আপনার মিটিং দুই তিন চব্বিশ তারিখে সকাল দশটা ত্রিশ মিনিট এ'),
        ('Meeting on ৫ মে ২০২৪ at 3 PM', 'Meeting on the fifth of May, twenty twenty-four at three PM'),
        ('আপনার মিটিং 10 May 2024 তারিখে', 'আপনার মিটিং দশই মে দুই হাজার চব্বিশ তারিখে'),
        ('সকাল ১০.৩০ টায় আসুন', 'সকাল দশটা ত্রিশ মিনিটে আসুন'),
        ('৬/১২/২৪ months installment', 'six, twelve, twenty-four months installment'),
        ('6/12/24 মাসের কিস্তি', 'ছয়, বারো, চব্বিশ মাসের কিস্তি'),
        ('২/৩/২৪ তারিখে। Due 2/3/24.', 'দুই তিন চব্বিশ তারিখে। Due two three twenty-four.'),
        ('২৫/১২/২৪ তারিখে। Due 25/12/24.', 'পঁচিশে ডিসেম্বর চব্বিশ তারিখে। Due the twenty-fifth of December, twenty-four.'),
        ('Meeting on Dec. 25th at 10:30 a.m. ঠিক আছে।', 'Meeting on December twenty-fifth at ten thirty AM ঠিক আছে।'),
    ],
    'unsupported language kept as it is': [
        ('مرحبا 500', 'مرحبا 500'),
        ('नमस्ते १२३', 'नमस्ते १२३'),
        ('१२३', '१२३'),
        ('Привет 5', 'Привет 5'),
        ('Hello. مرحبا 500. ৫০০ টাকা।', 'Hello. مرحبا 500. পাঁচশত টাকা।'),
    ],
    'each sentence in its own language': [
        ('Pay $5 now. ৫০০ টাকা দিন। Call 01711-123456!', 'Pay five dollars now. পাঁচশত টাকা দিন। Call zero one seven one one one two three four five six!'),
        ('Rate 1.5% today.\n১.৫% আজ', 'Rate one point five percent today. এক দশমিক পাঁচ শতাংশ আজ'),
        ('Thanks! ৫০০ টাকা জমা হয়েছে', 'Thanks! পাঁচশত টাকা জমা হয়েছে'),
        ('Done? ৫০০ টাকা বাকি', 'Done? পাঁচশত টাকা বাকি'),
        ('Wait... ৫০০ টাকা দিন', 'Wait... পাঁচশত টাকা দিন'),
    ],
    'dots that do not end a sentence': [
        ('Pay 1.5% now', 'Pay one point five percent now'),
        ('১.৫% চার্জ', 'এক দশমিক পাঁচ শতাংশ চার্জ'),
        ('Total ৳১,২৫০.৫০ only', 'Total one thousand two hundred fifty taka and fifty paisa only'),
        ('Tk. 500 only', 'five hundred taka only'),
        ('Tk. ৫০০ মাত্র', 'পাঁচশত টাকা মাত্র'),
        ('Rs. 500 only', 'five hundred rupees only'),
        ('Rs. ৫০০ মাত্র', 'পাঁচশত রুপি মাত্র'),
        ('BDT. 500 only', 'five hundred taka only'),
        ('Meeting on Dec. 25th', 'Meeting on December twenty-fifth'),
        ('১০.০৫.২০২৪ তারিখে', 'দশ পাঁচ দুই হাজার চব্বিশ তারিখে'),
        ('ধাপ ২. টাকা পাঠান।', 'ধাপ দুই. টাকা পাঠান।'),
    ],
    'dots that end a sentence': [
        ('Price $5.50. Thanks', 'Price five dollars and fifty cents. Thanks'),
        ('Version 1.2.3. Next one', 'Version one dot two dot three. Next one'),
        ('IP 192.168.0.1. Done', 'IP one hundred ninety-two dot one hundred sixty-eight dot zero dot one. Done'),
        ('Visit example.com. Then pay $5', 'Visit example dot com. Then pay five dollars'),
        ('Wait. ৫০০ টাকা দিন', 'Wait. পাঁচশত টাকা দিন'),
        ('Paid ৫০০. Thanks', 'Paid five hundred. Thanks'),
        ('Due 25.12.2024. ঠিক আছে।', 'Due the twenty-fifth of December, twenty twenty-four. ঠিক আছে।'),
        ('Step 1. Open app. ধাপ ২. টাকা পাঠান।', 'Step one. Open app. ধাপ দুই. টাকা পাঠান।'),
        ('৫০০ টাকা. Thank you', 'পাঁচশত টাকা. Thank you'),
        ('Pay Tk. 500. ৫০০ টাকা দিন।', 'Pay five hundred taka. পাঁচশত টাকা দিন।'),
    ],
}

class DetectLanguageTest(unittest.TestCase):
    def test_every_case(self):
        for category, cases in DETECTION_CASES.items():
            for text, lang in cases:
                with self.subTest(category=category, text=text):
                    self.assertEqual(detect_language(text), lang)

    def test_default_when_nothing_decides(self):
        self.assertEqual(detect_language("2712", default="bn"), "bn")
        self.assertEqual(detect_language("", default="bn"), "bn")

    def test_ignored_parts_do_not_count(self):
        tags = re.compile(r"(\[[a-z]+\])")
        self.assertEqual(detect_language("[warm] [calm] ৫ টাকা"), "en")
        self.assertEqual(detect_language("[warm] [calm] ৫ টাকা", ignore=tags), "bn")

    def test_sentences_without_words_take_their_context(self):
        self.assertEqual(detect_sentence_languages(["মোট পরিমাণ:", "৫০০", "300", "Total:", "500"]), ["bn", "bn", "bn", "en", "en"])
        self.assertEqual(detect_sentence_languages(["500", "আপনার ব্যালেন্স"]), ["bn", "bn"])
        self.assertEqual(detect_sentence_languages(["500"]), ["en"])
        self.assertEqual(detect_sentence_languages(["৫০০"]), ["bn"])
        self.assertEqual(detect_sentence_languages(["مرحبا", "500"]), [None, None])


class SplitSentencesTest(unittest.TestCase):
    def test_every_case(self):
        for category, cases in SENTENCE_CASES.items():
            for text, sentences in cases:
                with self.subTest(category=category, text=text):
                    self.assertEqual(split_sentences(text), sentences)


class AutoConvertTest(unittest.TestCase):
    def test_every_case(self):
        for category, cases in AUTO_CASES.items():
            for written, spoken in cases:
                with self.subTest(category=category, written=written):
                    self.assertEqual(convert_text(written, lang="auto"), spoken)

    def test_every_sample_whose_language_is_clear(self):
        for lang, categories in (("bn", BANGLA_CASES), ("en", ENGLISH_CASES)):
            for category, cases in categories.items():
                for written, spoken in cases:
                    if detect_language(written) != lang:
                        continue
                    with self.subTest(lang=lang, category=category, written=written):
                        self.assertEqual(convert_text(written, lang="auto"), spoken)

    def test_case_insensitive_and_blank(self):
        self.assertEqual(convert_text("৫", lang="AUTO"), "পাঁচ")
        self.assertEqual(convert_text("৫", "Auto"), "পাঁচ")
        self.assertEqual(convert_text("", lang="auto"), "")
        self.assertEqual(convert_text(None, lang="auto"), None)

    def test_keep_pattern(self):
        tags = re.compile(r"(\[[a-z]+\])")
        cases = {
            "[warm] Pay $5. [calm] ৫ টাকা দিন।": "[warm] Pay five dollars. [calm] পাঁচ টাকা দিন।",
            "[warm] ৫ টাকা": "[warm] পাঁচ টাকা",
            "[warm] [calm] ৫ টাকা": "[warm] [calm] পাঁচ টাকা",
            "[warm] مرحبا 500": "[warm] مرحبا 500",
            "[warm] $5. [calm] ৫ টাকা।": "[warm] পাঁচ ডলার. [calm] পাঁচ টাকা।",
        }
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(convert_text(written, lang="auto", keep=tags), spoken)

    def test_number_to_text(self):
        cases = [
            (2712, "cardinal", "two thousand seven hundred twelve"), ("২৭১২", "cardinal", "দুই হাজার সাতশত বারো"),
            ("2712", "digitwise", "two seven one two"), ("৳৫০০", "auto", "পাঁচশত টাকা"), ("$5", "auto", "five dollars"),
            ("50০০", "cardinal", "five thousand"), ("৫০00", "cardinal", "পাঁচ হাজার"),
            ("१२३", "cardinal", "१२३"), (" ١٢٣ ", "digitwise", "١٢٣"),
        ]
        for value, style, spoken in cases:
            with self.subTest(value=value, style=style):
                self.assertEqual(number_to_text(value, lang="auto", style=style), spoken)


def counting_language(code_name, script_range, lexicon):
    """A minimal language for tests: numbers become letters a-j."""

    class CountingLanguage(Language):
        code = code_name
        script = script_range
        words = Words(digits=tuple("abcdefghij"), negative="n", decimal_point="p", percent="c", range="r",
                      slash="s", ratio="t", dot="d", at="a", star="st", hash="h", plus="pl")

        def to_cardinal(self, number):
            return "n" + "".join("abcdefghij"[int(digit)] for digit in str(number))

        def to_ordinal(self, number):
            return self.to_cardinal(number)

        def to_year(self, year):
            return self.to_cardinal(year)

        def to_date(self, day, month, year=None):
            return self.to_cardinal(day)

        def to_time(self, hour, minute=0, second=None, with_period=False):
            return self.to_cardinal(hour)

    return CountingLanguage(lexicon=lexicon)


class ExtensionTest(unittest.TestCase):
    """Abbreviations, sentence end marks, code keywords and the splitter can all be extended."""

    def use(self, language, code):
        original = get_language(code)
        register_language(language, code=code)
        self.addCleanup(register_language, original, code)

    def test_own_abbreviation(self):
        self.assertEqual(split_sentences("Engr. Karim paid $5"), ["Engr. ", "Karim paid $5"])
        self.use(EnglishLanguage(lexicon=ENGLISH_LEXICON.extended(abbreviations=("Engr.",))), "en")
        self.assertEqual(split_sentences("Engr. Karim paid $5"), ["Engr. Karim paid $5"])
        self.assertEqual(convert_text("Engr. Karim paid $5", lang="auto"), "Engr. Karim paid five dollars")

    def test_own_bangla_abbreviation(self):
        self.assertEqual(split_sentences("প্রকৌ. Karim ৫০০ টাকা দিলেন"), ["প্রকৌ. ", "Karim ৫০০ টাকা দিলেন"])
        self.use(BanglaLanguage(lexicon=BANGLA_LEXICON.extended(abbreviations=("প্রকৌ.",))), "bn")
        self.assertEqual(split_sentences("প্রকৌ. Karim ৫০০ টাকা দিলেন"), ["প্রকৌ. Karim ৫০০ টাকা দিলেন"])

    def test_own_sentence_end_mark(self):
        self.assertEqual(split_sentences("Pay $5; ৫০০ টাকা দিন"), ["Pay $5; ৫০০ টাকা দিন"])
        self.use(EnglishLanguage(lexicon=ENGLISH_LEXICON.extended(sentence_end_marks=(";",))), "en")
        self.assertEqual(split_sentences("Pay $5; ৫০০ টাকা দিন"), ["Pay $5; ", "৫০০ টাকা দিন"])
        self.assertEqual(convert_text("Pay $5; ৫০০ টাকা দিন", lang="auto"), "Pay five dollars; পাঁচশত টাকা দিন")

    def test_new_language_brings_its_marks_and_abbreviations(self):
        self.assertEqual(split_sentences("مرحبا؟ Pay $5"), ["مرحبا؟ Pay $5"])
        register_language(counting_language("test-arabic", "؀-ۿ", Lexicon(sentence_end_marks=("؟",), abbreviations=("د.",))))
        self.addCleanup(unregister_language, "test-arabic")
        self.assertEqual(split_sentences("مرحبا؟ Pay $5"), ["مرحبا؟ ", "Pay $5"])
        self.assertEqual(split_sentences("Hi. د. Ali"), ["Hi. ", "د. Ali"])
        self.assertEqual(convert_text("مرحبا 5؟ Pay $5", lang="auto"), "مرحبا nf؟ Pay five dollars")

    def test_own_code_keyword(self):
        self.assertEqual(convert_text("Voucher 4821", lang="en"), "Voucher four thousand eight hundred twenty-one")
        self.use(EnglishLanguage(lexicon=ENGLISH_LEXICON.extended(digitwise_after=("Voucher",))), "en")
        self.assertEqual(convert_text("Voucher 4821", lang="en"), "Voucher four eight two one")

    def test_own_splitter(self):
        def split_at_bars(text):
            return text.split("|")

        self.assertEqual(convert_text("Pay $5|৫০০ টাকা দিন", lang="auto", splitter=split_at_bars), "Pay five dollars পাঁচশত টাকা দিন")
        one_sentence = convert_text("Pay $5 ৫০০ টাকা", lang="auto", splitter=lambda text: [text])
        self.assertEqual(one_sentence, "Pay পাঁচ ডলার পাঁচশত টাকা")

    def test_unregister_language(self):
        self.assertIsNone(unregister_language("not-registered"))
        register_language(counting_language("test-temporary", "", Lexicon()))
        self.assertIsNotNone(unregister_language("test-temporary"))
        self.assertIsNone(unregister_language("test-temporary"))

    def test_custom_language_is_detected_by_its_script(self):
        self.assertIsNone(detect_language("αριθμός 5"))
        register_language(counting_language("test-greek", "Ͱ-Ͽ", Lexicon()))
        self.addCleanup(unregister_language, "test-greek")
        self.assertEqual(detect_language("αριθμός 5"), "test-greek")
        self.assertEqual(convert_text("αριθμός 5. Number 5", lang="auto"), "αριθμός nf. Number five")


if __name__ == "__main__":
    unittest.main()
