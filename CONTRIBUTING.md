# Contributing

Thanks for helping. Bug reports, new cases, new languages and fixes are all welcome.

## Setup

Fork https://github.com/kawshikbuet17/multilingual_num2text, then:

```bash
git clone https://github.com/<your-username>/multilingual_num2text.git
cd multilingual_num2text
pip install -e .
python -m unittest discover -s tests
```

No other dependencies are needed.

## Reporting a wrong conversion

Open an [issue](https://github.com/kawshikbuet17/multilingual_num2text/issues) with the input, the language, what you got and what you expected:

```
convert_text("১০:৩০ PM", "bn")
got:      ...
expected: রাত দশটা ত্রিশ মিনিট
```

## Making a change

1. Add the case to `tests/test_multilingual_num2text.py`, in the matching category of `BANGLA_CASES` or `ENGLISH_CASES`.
2. Make it pass. Keep all other tests passing.
3. Open a pull request that explains the case.

Where things go:

| Change | File |
|---|---|
| A word or pronunciation | `languages/<lang>/vocabulary.py` |
| A unit, acronym, phrase or setting | `languages/<lang>/lexicon.py` |
| A currency name | `languages/<lang>/currencies.py` |
| A currency code or symbol | `core/currencies.py` |
| A rule only one language needs | `languages/<lang>/rules.py` |
| A rule every language needs | `core/number_rules.py` or `core/text_rules.py` |

## Adding a language

1. Copy `languages/english/` to `languages/<name>/`.
2. Fill `vocabulary.py` (words), `lexicon.py` (units, phrases) and `currencies.py` (names for the codes in `core/currencies.py`).
3. Implement the five methods in `language.py`: `to_cardinal`, `to_ordinal`, `to_year`, `to_date`, `to_time`.
4. Register it in `src/multilingual_num2text/__init__.py` and add a `<NAME>_CASES` table with tests.

## Guidelines

- Keep built-in data general. Company names, hotlines, brand names and project tags belong in the user's code
  through `Lexicon.extended()`, not in the package.
- No dependencies.
- Readable names over comments. Add a docstring only when it helps, usually with an input → output example.
- Bangla text must stay NFC-normalized.

## Releasing (maintainers)

1. Raise `version` in `pyproject.toml` and push to `main`.
2. On GitHub, publish a release with tag `v<version>` (for example `v0.1.1`).
3. The Publish workflow runs the tests on every supported Python, builds the package and uploads it to PyPI.
   It stops if the tag does not match the version.
