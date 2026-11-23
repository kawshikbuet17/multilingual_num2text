"""Every case combined with every other case in one text must convert exactly as each does alone."""

import unittest

from multilingual_num2text import convert_text
from test_multilingual_num2text import BANGLA_CASES, ENGLISH_CASES

SEPARATOR = " ¦ "


def flatten(categories):
    return [case for cases in categories.values() for case in cases]


class CombinationTest(unittest.TestCase):
    def check_every_pair(self, lang, categories):
        cases = flatten(categories)
        failures = []
        for first_written, first_spoken in cases:
            for second_written, second_spoken in cases:
                written = first_written + SEPARATOR + second_written
                expected = first_spoken + SEPARATOR + second_spoken
                spoken = convert_text(written, lang)
                if spoken != expected:
                    failures.append(f"{written!r}\n  got:      {spoken!r}\n  expected: {expected!r}")
        self.assertFalse(failures, f"{len(failures)} of {len(cases) ** 2} pairs differ:\n" + "\n".join(failures[:20]))

    def check_all_at_once(self, lang, categories):
        cases = flatten(categories)
        written = SEPARATOR.join(written for written, _ in cases)
        expected = SEPARATOR.join(spoken for _, spoken in cases)
        self.assertEqual(convert_text(written, lang), expected)

    def test_bangla_every_pair(self):
        self.check_every_pair("bn", BANGLA_CASES)

    def test_english_every_pair(self):
        self.check_every_pair("en", ENGLISH_CASES)

    def test_bangla_all_cases_in_one_text(self):
        self.check_all_at_once("bn", BANGLA_CASES)

    def test_english_all_cases_in_one_text(self):
        self.check_all_at_once("en", ENGLISH_CASES)


if __name__ == "__main__":
    unittest.main()
