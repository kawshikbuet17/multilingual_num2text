# multilingual_num2text

Turns every number in a piece of text into words, the way a person would say it.

It works out what a number is from how it is written: `$1,250.50` becomes money with cents,
`01711-123456` a phone number read digit by digit, `25/12/2024` a date, `15:45` a time, `*123#` a code.
The same in Bangla: `৳১,২৫০.৫০` becomes money with paisa, `০১৭১১-১২৩৪৫৬` a phone number, `২৫/১২/২০২৪` a date, `১৫:৪৫` a time.
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
number_to_text(2712, lang="en")                        # two thousand seven hundred twelve
number_to_text(2712, lang="en", style="digitwise")     # two seven one two
number_to_text("$1,250.50", lang="en", style="auto")   # one thousand two hundred fifty dollars and fifty cents
number_to_text(2712, lang="bn")                        # দুই হাজার সাতশত বারো
number_to_text(2712, lang="bn", style="digitwise")     # দুই সাত এক দুই
number_to_text("৳১,২৫০.৫০", lang="bn", style="auto")    # এক হাজার দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা

# Every number inside a text
convert_text("Send $1,250.50 on May 10, 2024", lang="en")
# Send one thousand two hundred fifty dollars and fifty cents on May tenth, twenty twenty-four
convert_text("৳১,২৫০.৫০ পাঠান ০১৭১১-১২৩৪৫৬ নম্বরে", lang="bn")
# এক হাজার দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা পাঠান শূন্য এক সাত এক এক এক দুই তিন চার পাঁচ ছয় নম্বরে

# Language detected per sentence
convert_text("Pay $5 now. ৫০০ টাকা দিন।", lang="auto")    # Pay five dollars now. পাঁচশত টাকা দিন।
convert_text("Hello. مرحبا 500. ৫০০ টাকা।", lang="auto")   # Hello. مرحبا 500. পাঁচশত টাকা।
number_to_text("২৭১২", lang="auto")                       # দুই হাজার সাতশত বারো
```

Positional arguments also work: `number_to_text(2712, "en", "digitwise")`.

## Parameters

### `convert_text(text, lang, keep=None, splitter=None)` → `str`

Converts every number inside a text.

| Parameter | Type | Meaning |
|---|---|---|
| `text` | `str` | The text. `""` and `None` are returned unchanged. |
| `lang` | `str` | `"en"`, `"bn"`, any code added with `register_language`, or `"auto"` (see below). Not case-sensitive. An unknown code raises `ValueError`. |
| `keep` | `re.Pattern`, optional | Parts to leave exactly as they are, such as tags like `[warm]`. The pattern needs one capturing group around the whole match: `re.compile(r"(\[[a-z]+\])")`. With `"auto"`, these parts also do not count when detecting the language. |
| `splitter` | function, optional | Only for `"auto"`: your own function that takes the text and returns its sentences. Default: `split_sentences`. |

### `number_to_text(value, lang, style="cardinal")` → `str`

Converts one number.

| Parameter | Type | Meaning |
|---|---|---|
| `value` | `int`, `float` or `str` | `2712`, `2.5`, `"১,২৫০.৫০"`, `"-15"`. With `style="auto"` also `"৳500"`, `"*123#"`, `"01711-123456"`. |
| `lang` | `str` | As in `convert_text`. With `"auto"`, a number in digits of an unsupported language is returned unchanged. |
| `style` | `str` or `NumberStyle` | `"cardinal"` (default): the value as one number. `"digitwise"`: digit by digit. `"auto"`: decided by the shape, like `convert_text` (leading `0` or `+` → digit by digit, leading `*` or `#` → a code, currency → money). |

Raises `ValueError` when `value` is not a number (in `cardinal` style) or `style` is unknown.

### `detect_language(text, default="en", ignore=None)` → `str` or `None`

The language `lang="auto"` would use for a text.

| Parameter | Type | Meaning |
|---|---|---|
| `text` | `str` | The text to look at. |
| `default` | `str` | Returned when the text has no words or digits. ASCII digits also count as this language. |
| `ignore` | `re.Pattern`, optional | Parts that do not count, like `keep` in `convert_text`. |

Returns the language code, or `None` when the text is written in a language that is not registered.

### Languages and sentences

| Call | Parameters |
|---|---|
| `EnglishLanguage(indian_scales=False, lexicon=None)` | `indian_scales=True` reads `2,50,000` as two lakh fifty thousand. `lexicon` replaces the built-in data (see below). |
| `BanglaLanguage(lexicon=None)` | `lexicon` replaces the built-in data. |
| `register_language(language, code=None)` | Makes a language usable by its code. `code` defaults to `language.code`; registering an existing code replaces it. |
| `unregister_language(code)` | Removes a language and returns it, or `None` if it was not registered. |
| `get_language(code)` | The registered language object, with `convert_text(text, keep=None)` and `number_to_text(value, style="cardinal")`. |
| `available_languages()` | The registered codes, sorted. |
| `split_sentences(text, ignore=None)` | The sentences `lang="auto"` works with. |
| `detect_sentence_languages(sentences, default="en", ignore=None)` | The language of each sentence, as `lang="auto"` uses it (sentences without words take their context). |

### `lang="auto"`

The text is split into sentences, and each sentence is converted in the language it is written in.
Every number in a sentence follows the sentence.

**Which language a sentence is in:**

| Rule | Example |
|---|---|
| The language with the most words wins | `আপনার account এ ৫০০ টাকা পাঠানো হয়েছে` → bn, `Cash out charge ১.৮৫%` → en |
| Acronyms (`OTP`, `ATM`), emails, web addresses, abbreviations (`Mr.`, `ডা.`) and `keep=` tags do not count | `OTP কোড 123456` → bn, `যোগাযোগ: support@example.com অথবা ০১৭১১-১২৩৪৫৬` → bn |
| Equal words: the language whose own digits appear wins, then the one whose word comes first | `আপনার balance ৳৫০০` → bn, `Send Money ফি ৫ টাকা` → bn, `আপনার balance 500` → bn |
| No words: the digits decide, ASCII digits count as English, most digits win, a tie goes to the first digit | `১` → এক, `1` → one, `5০০০` → পাঁচ হাজার, `50০০` → five thousand, `৫০00` → পাঁচ হাজার |
| A sentence without words inside a longer text takes the language of the sentences around it | `মোট পরিমাণ:⏎৫০০⏎300` → মোট পরিমাণ: পাঁচশত তিনশত |
| A sentence in a language that is not supported is kept exactly as it is | `مرحبا 500` → مرحبا 500, `Hello. مرحبا 500. ৫০০ টাকা।` → Hello. مرحبا 500. পাঁচশত টাকা। |

**Where a sentence ends:**

| Rule | Example |
|---|---|
| A line break | `Total:⏎৫০০` → two sentences |
| An end mark (`।` `!` `?` and `.`) followed by a space or the end | `Pay $5 now. ৫০০ টাকা দিন।`, `Thanks! ৫০০ টাকা জমা হয়েছে` |
| `.` only when the next sentence starts with a capital or another script | `First. Second` splits; `e.g. this one`, `1.5 kg` do not |
| Never after an abbreviation | `Mr. Karim`, `Dr. Rahman`, `e.g.`, `etc.`, `ডা. রহিম`, `মো. করিম` |
| Never after a currency symbol before a number | `Tk. ৫০০ মাত্র` → পাঁচশত টাকা মাত্র, `BDT. 500` → five hundred taka |
| Never after a bare list number | `১. Open app`, `১। প্রথম ধাপ` |
| Never without a space after the mark | `Wow!Really`, `example.com/?page=2`, `ধন্যবাদ।আপনার` |

End marks and abbreviations come from each language's `Lexicon` (`sentence_end_marks`, `abbreviations`) and can be extended:

```python
register_language(EnglishLanguage(lexicon=ENGLISH_LEXICON.extended(abbreviations=("Engr.",), sentence_end_marks=(";",))), code="en")
convert_text("Engr. Karim paid $5; ৫০০ টাকা দিন", lang="auto")   # Engr. Karim paid five dollars; পাঁচশত টাকা দিন
convert_text(text, lang="auto", splitter=lambda text: text.split("|"))   # or split sentences yourself
```

`detect_language(text)` returns the code alone, or `None` when unsupported.

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
| Currency symbol with a dot | `BDT. 500` → five hundred taka, `Rs. 500` → five hundred rupees | `Tk.৫০০` → পাঁচশত টাকা |
| Code after OTP, PIN, code, ID, reference (4+ digits, up to two words after) | `Your OTP is 482913` → Your OTP is four eight two nine one three, `PIN: 1234` → PIN: one two three four | `OTP কোড 123456` → ওটিপি কোড এক দুই তিন চার পাঁচ ছয়, `আপনার ওটিপি ৪৮২৯১৩` → … চার আট দুই নয় এক তিন |
| Starts with `0` or `+` | `+880 1711 123456` → plus eight eight zero … | `০১৭১১-১২৩৪৫৬` → শূন্য এক সাত এক এক … |
| Starts with `*` or `#` | `*123#` → star one two three hash | `*১২৩#` → স্টার এক দুই তিন হ্যাশ |
| Long number (10+ digits), card | `account 123456789012` → account one two three … | `১২৩৪ ৫৬৭৮ ৯০১২ ৩৪৫৬` → এক দুই তিন চার … |
| Date | `25/12/2024`, `12/25/2024` → the twenty-fifth of December, twenty twenty-four; `May 10` → May tenth | `২৫/১২/২০২৪`, `২৫ ডিসেম্বর ২০২৪` → পঁচিশে ডিসেম্বর দুই হাজার চব্বিশ |
| Date where day and month could swap | `2/5/2024` → two five twenty twenty-four, `2/3/24` → two three twenty-four | `২/৫/২০২৪` → দুই পাঁচ দুই হাজার চব্বিশ, `২/৩/২৪` → দুই তিন চব্বিশ |
| Month name from the other language | `৫ মে ২০২৪` → the fifth of May, twenty twenty-four | `10 May 2024` → দশই মে দুই হাজার চব্বিশ |
| Day form | — | `১লা বৈশাখ` → পহেলা বৈশাখ, `২১শে` → একুশে |
| Year | `in 1971` → in nineteen seventy-one, `1990s` → nineteen nineties | `১৯৭১ সালে` → উনিশশো একাত্তর সালে, `২০২৪-২৫` → দুই হাজার চব্বিশ পঁচিশ |
| Time | `10:05` → ten oh five, `15:45` → three forty-five PM, `10.30 AM` → ten thirty AM | `১০:৩০` → দশটা ত্রিশ মিনিট, `১৫:৪৫` → দুপুর তিনটা পঁয়তাল্লিশ মিনিট, `১০ AM` → সকাল দশটা |
| Time with টা / টায় / টার or a period word (`.` or `:`) | — | `সকাল ১০.৩০ টায়` → সকাল দশটা ত্রিশ মিনিটে, `১০:০০ টায়` → দশটায়, `বিকেল ৪.১৫ টার` → বিকেল চারটা পনেরো মিনিটের, `রাত ২২:৩০` → রাত দশটা ত্রিশ মিনিট |
| Ratio | `1:2` → one to two | `১:২` → এক অনুপাত দুই |
| Ordinal | `21st` → twenty-first | `১ম` → প্রথম, `২য়` → দ্বিতীয়, `১১তম` → এগারোতম |
| Range | `5-10%` → five to ten percent | `৫০০-১০০০ টাকা` → পাঁচশত থেকে এক হাজার টাকা |
| Slash | `12/3` → twelve slash three, `6/12/24 months` → six, twelve, twenty-four months, `৬/১২/২৪ মাস` → six, twelve, twenty-four মাস | `১২/৩` → বারো বাই তিন, `৬/১২/২৪ মাস` → ছয়, বারো, চব্বিশ মাস, `6/12/24 months` → ছয়, বারো, চব্বিশ months |
| Fraction | `2½` → two and a half | `২.৫ লাখ` → আড়াই লাখ, `১.৫ ঘণ্টা` → দেড় ঘণ্টা, `২½` → আড়াই |
| Unit, shorthand | `20km` → twenty kilometers, `2.5K` → two thousand five hundred | `২০GB` → বিশ জিবি, `৩৫°C` → পঁয়ত্রিশ ডিগ্রি সেলসিয়াস, `৫K` → পাঁচ হাজার |
| Arithmetic | `2+2=4` → two plus two equals four | `২+২=৪` → দুই যোগ দুই সমান চার, `৫০০+` → পাঁচশত প্লাস |
| Version, IP | `1.2.3` → one dot two dot three | `১.২.৩` → এক ডট দুই ডট তিন |
| Email, URL | `user1@example.com` → user one at example dot com | `user1@example.com` → user এক অ্যাট example ডট কম |

Dates: when day and month are both 12 or less and differ, the order can't be known, so the numbers are read as written
instead of guessing a month. Equal values (`5/5/2024`), one value above 12, ISO `2024-05-10` and written month names use the month name.

Leftover symbols (`*`, `#`, brackets, quotes, `**bold**`) are removed. The text is NFC-normalized first.

### Keep parts unchanged

```python
import re
tags = re.compile(r"(\[[a-z]+\])")
convert_text("[warm] 500 dollars", lang="en", keep=tags)   # [warm] five hundred dollars
convert_text("[warm] ৫০০ টাকা", lang="bn", keep=tags)      # [warm] পাঁচশত টাকা
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
convert_text("[Source 1] Call 54321", lang="en")  # Call five four three two one

lexicon = BANGLA_LEXICON.extended(
    digitwise_numbers=("54321",),
    domain_words={"example": "এক্সাম্পল"},        # example.com → এক্সাম্পল ডট কম
    email_name_words={"support": "সাপোর্ট"},
)
register_language(BanglaLanguage(lexicon=lexicon), code="bn")
convert_text("৫৪৩২১ নম্বরে কল করুন", lang="bn")   # পাঁচ চার তিন দুই এক নম্বরে কল করুন
```

`extended()` merges dictionaries, appends to tuples and replaces other settings. The built-in lexicon is not changed.
Every setting:

| Setting | Type (default) | Meaning |
|---|---|---|
| `currencies` | tuple of `Currency` | Currencies with their names and symbols. Built in: all 153 ISO currencies. |
| `digitwise_numbers` | tuple of `str` | Numbers always read digit by digit wherever they appear (hotlines, short codes). |
| `fixed_phrases` | dict | Written → spoken, matched in any case: `{"24/7": "twenty-four seven"}`. |
| `word_replacements` | dict | Plain text replacements done first: `{" + ": " plus "}`. |
| `removed_patterns` | tuple of regex `str` | Deleted before converting: `(r"\[Source\s*\d*\]",)`. |
| `acronyms` | dict | How to say acronyms: `{"ATM": "এটিএম"}`. |
| `domain_words` | dict | How to say parts of web and email addresses: `{"com": "কম"}`. |
| `bare_domain_endings` | tuple (`com`, `net`, `org`, `gov`, `edu`, `bd`, `info`, `io`) | Endings that make `example.com` a domain without `https://`. |
| `email_name_words` | dict | How to say the part before `@`: `{"support": "সাপোর্ট"}`. |
| `units` | dict | Units after a number: `{"km": "kilometers"}`. |
| `magnitudes` | dict (`k`, `K` = 1,000, `M` = 1,000,000, `bn` = 1,000,000,000) | Shorthand after a number: `5K` → 5000. |
| `scale_words` | tuple | Words after an amount that belong to it: `$5 million` → five million dollars. |
| `duration_words` | tuple | Words that make `6/12/24` a list instead of a date: `6/12/24 months`. Built in: both languages' words in both lexicons. |
| `digitwise_after` | tuple | Words after which a number of 4+ digits (up to two words later) is read digit by digit: `("OTP", "PIN", "code", "ID")`. |
| `sentence_end_marks` | tuple | Marks that end a sentence for `lang="auto"`: Bangla `("।", "!", "?")`, English `(".", "!", "?")`. |
| `abbreviations` | tuple | Words whose dot never ends a sentence and which do not count for `lang="auto"`: `("Mr.", "Dr.", "e.g.", "ডা.")`. |
| `year_markers_after` / `year_markers_before` | tuple | Words that mark a year: `১৯৭১ সালে`, `in 1971`. |
| `digitwise_min_length` | `int` (10) | Digit runs this long or longer are read digit by digit (account numbers). |
| `phone_max_digits` | `int` (15) | Most digits joined into one phone number across spaces and hyphens. |
| `phone_min_digits_after_plus` | `int` (6) | Fewer digits after `+` are read as a number (`+500`), not a phone. |
| `strip_decimal_trailing_zeros` | `bool` (True) | `2.60` → two point six. Set `False` for two point six zero. |

## Add a language

Subclass `Language` and implement five methods. Everything else (money, phones, ranges …) is shared.

```python
from multilingual_num2text import Language, Lexicon, Words, register_language

class HindiLanguage(Language):
    code = "hi"
    script = "\u0900-\u097F"     # Devanagari, used by lang="auto"
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
| `test_multilingual_num2text.py` | 303 example cases across every category in the table |
| `test_combinations.py` | every case paired with every other case in one text (49,349 pairs), and all cases at once |
| `test_word_tables.py` | every word from 0 to 99, every hundred and scale, every Bangla number up to 1,00,000, every ordinal, date day, month, day/month pair from 1 to 12, hour, minute and year boundary; no digit left for any number up to 10,000 |
| `test_currencies.py` | all 153 currencies in both languages: code before and after, every symbol, every name, fractions, negatives, scale words |
| `test_auto_language.py` | `lang="auto"`, every rule above: 55 detection cases (words, ties, what does not count, digits, mixed digits, unsupported languages), 38 sentence-splitting cases, 91 conversions (code-mixed text, codes, addresses, sentences without words, abbreviations, dates and times, dots), every sample whose language is clear, `keep=`, and extending abbreviations, end marks, code keywords, the splitter and new languages |
| `test_edges.py` | impossible dates and times, every setting's limit, Unicode forms and digit scripts, bad arguments, the registry, `Lexicon.extended()` |

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](https://github.com/kawshikbuet17/multilingual_num2text/blob/main/CONTRIBUTING.md).

## License

Copyright 2026 Kawshik Kumar Paul. Licensed under the [Apache License 2.0](https://github.com/kawshikbuet17/multilingual_num2text/blob/main/LICENSE).
