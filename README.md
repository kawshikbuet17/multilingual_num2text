# multilingual_num2text

Turns every number in a piece of text into words, the way a person would say it.

It works out what a number is from how it is written: `$1,250.50` becomes money with cents,
`01711-123456` a phone number read digit by digit, `10/05/2024` a date, `15:45` a time, `*123#` a code.
The same in Bangla: `৳১,২৫০.৫০` becomes money with paisa, `০১৭১১-১২৩৪৫৬` a phone number, `১০/০৫/২০২৪` a date, `১৫:৪৫` a time.
Amounts, percentages, 153 currencies, years, ordinals, ranges, fractions and units are covered.
Use it wherever numbers must appear as words.

English (`en`) and Bangla/Bengali (`bn`) are built in, and new languages can be added.
No dependencies. Python 3.10+.

## Install

```bash
pip install multilingual-num2text
```

Latest from GitHub: `pip install git+https://github.com/kawshikbuet17/multilingual_num2text.git`

## Use

```python
from multilingual_num2text import convert_text, number_to_text

# One number
number_to_text(2712, "en")                  # two thousand seven hundred twelve
number_to_text(2712, "en", "digitwise")     # two seven one two
number_to_text("$1,250.50", "en", "auto")   # one thousand two hundred fifty dollars and fifty cents
number_to_text(2712, "bn")                  # দুই হাজার সাতশত বারো
number_to_text(2712, "bn", "digitwise")     # দুই সাত এক দুই
number_to_text("৳১,২৫০.৫০", "bn", "auto")    # এক হাজার দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা

# Every number inside a text
convert_text("Send $1,250.50 on May 10, 2024", "en")
# Send one thousand two hundred fifty dollars and fifty cents on May tenth, twenty twenty-four
convert_text("৳১,২৫০.৫০ পাঠান ০১৭১১-১২৩৪৫৬ নম্বরে", "bn")
# এক হাজার দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা পাঠান শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয় নম্বরে
```

| Style | Meaning |
|---|---|
| `cardinal` (default) | the value as one number |
| `digitwise` | digit by digit |
| `auto` | decided by the shape, like `convert_text` |

ASCII, Bangla or mixed digits all work (`50,000` = `৫০,০০০` = `৫০,000`).

## What gets converted

| Case | English (`en`) | Bangla/Bengali (`bn`) |
|---|---|---|
| Number | `1,000,000` → one million | `২,৫০,০০০` → দুই লক্ষ পঞ্চাশ হাজার |
| Decimal | `0.5` → zero point five | `১.৪৯` → এক দশমিক চার নয় |
| Negative | `-5` → minus five | `-৫` → ঋণাত্মক পাঁচ |
| Percent | `90%` → ninety percent | `১.৪৯%` → এক দশমিক চার নয় শতাংশ |
| Money (sign before) | `$1.50` → one dollar and fifty cents | `৳১,২৫০.৫০` → এক হাজার দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা |
| Money (unit after) | `500 taka` → five hundred taka | `১০.৫০ টাকার` → দশ টাকা পঞ্চাশ পয়সার, `৫০০/-` → পাঁচশত টাকা |
| Any currency (153 ISO codes) | `KWD 1.250` → one Kuwaiti dinar and two hundred fifty fils | `SAR ৫০.২৫` → পঞ্চাশ সৌদি রিয়াল পঁচিশ হালালা |
| Money with scale | `$5 million` → five million dollars | `৳২.৫ কোটি` → আড়াই কোটি টাকা |
| Starts with `0` or `+` | `+880 1711 123456` → plus eight eight zero … | `০১৭১১-১২৩৪৫৬` → শূন্য এক সাত এক এক … |
| Starts with `*` or `#` | `*123#` → star one two three hash | `*১২৩#` → স্টার এক দুই তিন হ্যাশ |
| Long number (10+ digits), card | `account 123456789012` → account one two three … | `১২৩৪ ৫৬৭৮ ৯০১২ ৩৪৫৬` → এক দুই তিন চার … |
| Date | `10/05/2024` → the tenth of May, twenty twenty-four; `May 10` → May tenth | `১০/০৫/২০২৪`, `১০ মে ২০২৪` → দশই মে দুই হাজার চব্বিশ |
| Day form | — | `১লা বৈশাখ` → পহেলা বৈশাখ, `২১শে` → একুশে |
| Year | `in 1971` → in nineteen seventy-one, `1990s` → nineteen nineties | `১৯৭১ সালে` → উনিশশো একাত্তর সালে, `২০২৪-২৫` → দুই হাজার চব্বিশ পঁচিশ |
| Time | `10:05` → ten oh five, `15:45` → three forty-five PM | `১০:৩০` → দশটা ত্রিশ মিনিট, `১৫:৪৫` → দুপুর তিনটা পঁয়তাল্লিশ মিনিট, `১০ AM` → সকাল দশটা |
| Ratio | `1:2` → one to two | `১:২` → এক অনুপাত দুই |
| Ordinal | `21st` → twenty-first | `১ম` → প্রথম, `২য়` → দ্বিতীয়, `১১তম` → এগারোতম |
| Range | `5-10%` → five to ten percent | `৫০০-১০০০ টাকা` → পাঁচশত থেকে এক হাজার টাকা |
| Slash | `12/3` → twelve slash three | `১২/৩` → বারো বাই তিন, `৬/১২/২৪` → ছয়, বারো, চব্বিশ |
| Fraction | `2½` → two and a half | `২.৫ লাখ` → আড়াই লাখ, `১.৫ ঘণ্টা` → দেড় ঘণ্টা, `২½` → আড়াই |
| Unit, shorthand | `20km` → twenty kilometers, `2.5K` → two thousand five hundred | `২০GB` → বিশ জিবি, `৩৫°C` → পঁয়ত্রিশ ডিগ্রি সেলসিয়াস, `৫K` → পাঁচ হাজার |
| Arithmetic | `2+2=4` → two plus two equals four | `২+২=৪` → দুই যোগ দুই সমান চার, `৫০০+` → পাঁচশত প্লাস |
| Version, IP | `1.2.3` → one dot two dot three | `১.২.৩` → এক ডট দুই ডট তিন |
| Email, URL | `user1@example.com` → user one at example dot com | `user1@example.com` → user এক অ্যাট example ডট কম |

Leftover symbols (`*`, `#`, brackets, quotes, `**bold**`) are removed. The text is NFC-normalized first.

### Keep parts unchanged

```python
import re
tags = re.compile(r"(\[[a-z]+\])")
convert_text("[warm] 500 dollars", "en", keep=tags)   # [warm] five hundred dollars
convert_text("[warm] ৫০০ টাকা", "bn", keep=tags)      # [warm] পাঁচশত টাকা
```

## Add your own data

Project data (hotlines, brand names, acronyms, tags to strip) stays in your code:

```python
from multilingual_num2text import (
    BANGLA_LEXICON, ENGLISH_LEXICON, BanglaLanguage, EnglishLanguage, convert_text, register_language,
)

lexicon = ENGLISH_LEXICON.extended(
    digitwise_numbers=("54321",),                 # always digit by digit
    acronyms={"KYC": "K Y C"},
    fixed_phrases={"N/A": "not applicable"},
    removed_patterns=(r"\[Source\s*\d*\]",),     # deleted before converting
    strip_decimal_trailing_zeros=False,           # 2.60 → two point six zero
)
register_language(EnglishLanguage(lexicon=lexicon), code="en")
convert_text("[Source 1] Call 54321", "en")       # Call five four three two one

lexicon = BANGLA_LEXICON.extended(
    digitwise_numbers=("54321",),
    domain_words={"example": "এক্সাম্পল"},        # example.com → এক্সাম্পল ডট কম
    email_name_words={"support": "সাপোর্ট"},
)
register_language(BanglaLanguage(lexicon=lexicon), code="bn")
convert_text("৫৪৩২১ নম্বরে কল করুন", "bn")        # পাঁচ চার তিন দুই এক নম্বরে কল করুন
```

`extended()` merges dictionaries, appends to tuples and replaces other settings. Other settings:
`digitwise_min_length` (10), `phone_max_digits` (15), `units`, `scale_words`, `year_markers_after`, `year_markers_before`.

English: `EnglishLanguage(indian_scales=True)` reads `2,50,000` as two lakh fifty thousand.

## Add a language

Subclass `Language` and implement five methods. Everything else (money, phones, ranges …) is shared.

```python
from multilingual_num2text import Language, Lexicon, Words, register_language

class HindiLanguage(Language):
    code = "hi"
    words = Words(digits=("शून्य", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ"),
                  negative="ऋण", decimal_point="दशमलव", percent="प्रतिशत", range="से", slash="बटा",
                  ratio="अनुपात", dot="डॉट", at="एट", star="स्टार", hash="हैश", plus="प्लस")
    lexicon = Lexicon()

    def to_cardinal(self, number): ...
    def to_ordinal(self, number): ...
    def to_year(self, year): ...
    def to_date(self, day, month, year=None): ...
    def to_time(self, hour, minute=0, second=None, with_period=False): ...

register_language(HindiLanguage())
```

Optional: `language_rules()` for rules only that language needs, `build_currencies()` in `core/currencies.py`
to name all currencies, and overrides of `to_money`, `to_mixed_fraction`, `spell_scaled_amount`.
See `src/multilingual_num2text/languages/bangla/` for a complete example.

## Test

```bash
pip install -e .
python -m unittest discover -s tests
```

The tests cover every case above, for both languages, in all combinations:

| File | Checks |
|---|---|
| `test_multilingual_num2text.py` | 259 example cases across every category in the table |
| `test_combinations.py` | every case paired with every other case in one text (36,505 pairs), and all cases at once |
| `test_word_tables.py` | every word from 0 to 99, every hundred and scale, every Bangla number up to 1,00,000, every ordinal, date day, month, hour, minute and year boundary; no digit left for any number up to 10,000 |
| `test_currencies.py` | all 153 currencies in both languages: code before and after, every symbol, every name, fractions, negatives, scale words |
| `test_edges.py` | impossible dates and times, every setting's limit, Unicode forms and digit scripts, bad arguments, the registry, `Lexicon.extended()` |

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](https://github.com/kawshikbuet17/multilingual_num2text/blob/main/CONTRIBUTING.md).

## License

Copyright 2026 Kawshik Kumar Paul. Licensed under the [Apache License 2.0](https://github.com/kawshikbuet17/multilingual_num2text/blob/main/LICENSE).
