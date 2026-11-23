"""English words used to speak numbers. Language data only, no logic."""

from ...core.words import Words

AND = "and"

ONES = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
)
TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")

WORDS = Words(
    digits=ONES[:10],
    negative="minus",
    decimal_point="point",
    percent="percent",
    range="to",
    slash="slash",
    ratio="to",
    dot="dot",
    at="at",
    star="star",
    hash="hash",
    plus="plus",
    money_joiner=AND,
    add="plus",
    times="times",
    divided_by="divided by",
    equals="equals",
)

HUNDRED = "hundred"
INTERNATIONAL_SCALES = (
    (1_000_000_000_000, "trillion"),
    (1_000_000_000, "billion"),
    (1_000_000, "million"),
    (1_000, "thousand"),
)
INDIAN_SCALES = (
    (10_000_000, "crore"),
    (100_000, "lakh"),
    (1_000, "thousand"),
)

IRREGULAR_ORDINALS = {
    "one": "first", "two": "second", "three": "third", "five": "fifth",
    "eight": "eighth", "nine": "ninth", "twelve": "twelfth",
}

MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)
MONTH_ABBREVIATIONS = {
    "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April", "Jun": "June", "Jul": "July",
    "Aug": "August", "Sep": "September", "Sept": "September", "Oct": "October", "Nov": "November", "Dec": "December",
}
BANGLA_MONTH_NAMES = {
    "জানুয়ারি": 1, "জানুয়ারী": 1, "ফেব্রুয়ারি": 2, "ফেব্রুয়ারী": 2, "মার্চ": 3, "এপ্রিল": 4, "মে": 5, "জুন": 6,
    "জুলাই": 7, "আগস্ট": 8, "আগষ্ট": 8, "সেপ্টেম্বর": 9, "অক্টোবর": 10, "নভেম্বর": 11, "ডিসেম্বর": 12,
}
DATE_FORMAT = "the {day} of {month}"
DATE_WITH_YEAR_FORMAT = "the {day} of {month}, {year}"
MONTH_FIRST_DATE_FORMAT = "{month} {day}"
MONTH_FIRST_DATE_WITH_YEAR_FORMAT = "{month} {day}, {year}"

FRACTIONS = {"½": "a half", "¼": "a quarter", "¾": "three quarters"}
STANDALONE_FRACTIONS = {"½": "one half", "¼": "one quarter", "¾": "three quarters"}

O_CLOCK = "o'clock"
OH = "oh"
SECONDS = "seconds"
AM = "AM"
PM = "PM"
