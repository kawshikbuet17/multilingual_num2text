"""Rules for everything around the numbers: removed patterns, links, acronyms and leftover symbols."""

from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING

from .digits import to_ascii_digits
from .patterns import WORD_CHARS, compile_if_any

if TYPE_CHECKING:
    from .language import Language, Rule

_BOLD = re.compile(r"(\*\*|__)(.+?)\1")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_URL = re.compile(r"(?:https?://|www\.)[^\s)\]]*[^\s)\].,!?।]", re.IGNORECASE)
_DIGIT_RUN = re.compile(r"(?<![\d,.])\d+(?!\d|[,.]\d)")
_GROUPING_SPACE = re.compile(r"(?<=\d)[   ](?=\d{3}(?!\d))")
_SPACE_VARIANTS =str.maketrans({" ": " ", " ": " ", " ": " ", " ": " ", "​": ""})


class TextRules:
    def __init__(self, language: Language) -> None:
        self.language = language
        self.lexicon = language.lexicon
        self._removed = re.compile("|".join(self.lexicon.removed_patterns)) if self.lexicon.removed_patterns else None
        self._acronym = compile_if_any(self.lexicon.acronyms, lambda names: rf"(?<![A-Za-z])(?:{names})(?![A-Za-z])")
        self._bare_domain = compile_if_any(
            self.lexicon.bare_domain_endings,
            lambda endings: rf"(?<![{WORD_CHARS}@.])[{WORD_CHARS}-]+(?:\.[{WORD_CHARS}-]+)*\.(?:{endings})(?!\w)",
            re.IGNORECASE,
        )

    def preparation_rules(self) -> list[Rule]:
        return [
            self.normalize_unicode,
            self.remove_patterns,
            self.remove_markdown_emphasis,
            self.apply_word_replacements,
            self.apply_fixed_phrases,
            self.read_digitwise_numbers,
            self.read_emails,
            self.read_urls,
            self.read_bare_domains,
            self.expand_acronyms,
        ]

    def normalize_unicode(self, text: str) -> str:
        """NFC, digit groups joined by no-break or thin spaces (10 000), other space variants to plain spaces."""
        text = _GROUPING_SPACE.sub("", unicodedata.normalize("NFC", text))
        return text.translate(_SPACE_VARIANTS)

    def remove_patterns(self, text: str) -> str:
        return self._removed.sub("", text) if self._removed else text

    def remove_markdown_emphasis(self, text: str) -> str:
        return _BOLD.sub(r"\2", text)

    def apply_word_replacements(self, text: str) -> str:
        for written, spoken in self.lexicon.word_replacements.items():
            text = text.replace(written, spoken)
        return text

    def apply_fixed_phrases(self, text: str) -> str:
        for written, spoken in self.lexicon.fixed_phrases.items():
            pattern = re.escape(written)
            if written[0].isdecimal():
                pattern = rf"(?<!\d){pattern}"
            if written[-1].isdecimal():
                pattern = rf"{pattern}(?!\d)"
            text = re.sub(pattern, spoken, text, flags=re.IGNORECASE)
        return text

    def read_digitwise_numbers(self, text: str) -> str:
        """Helplines and other listed numbers, written in any digit script or a mix."""
        if not self.lexicon.digitwise_numbers:
            return text
        return _DIGIT_RUN.sub(self._digitwise_if_listed, text)

    def _digitwise_if_listed(self, match: re.Match) -> str:
        number = match.group()
        if to_ascii_digits(number) in self.lexicon.digitwise_numbers:
            return self.language.to_digitwise(number)
        return number

    def read_emails(self, text: str) -> str:
        return _EMAIL.sub(lambda match: f" {self.speak_email(match.group())} ", text)

    def read_urls(self, text: str) -> str:
        return _URL.sub(lambda match: f" {self.speak_url(match.group())} ", text)

    def read_bare_domains(self, text: str) -> str:
        if not self._bare_domain:
            return text
        return self._bare_domain.sub(lambda match: f" {self.speak_host(match.group())} ", text)

    def expand_acronyms(self, text: str) -> str:
        if not self._acronym:
            return text
        return self._acronym.sub(lambda match: self.lexicon.acronyms[match.group()], text)

    def speak_email(self, email: str) -> str:
        name, domain = email.split("@", 1)
        spoken_name = self.lexicon.email_name_words.get(name.lower()) or self.speak_host(name)
        return f"{spoken_name} {self.language.words.at} {self.speak_host(domain)}"

    def speak_url(self, url: str) -> str:
        host = re.sub(r"^https?://", "", url, flags=re.IGNORECASE).split("/")[0].split(":")[0]
        return self.speak_host(host)

    def speak_host(self, host: str) -> str:
        return f" {self.language.words.dot} ".join(self._speak_host_part(part) for part in host.split(".") if part)

    def _speak_host_part(self, part: str) -> str:
        if part.lower() in self.lexicon.domain_words:
            return self.lexicon.domain_words[part.lower()]
        spoken = re.sub(r"\d+", lambda match: f" {self.language.to_digitwise(match.group())} ", part)
        return re.sub(r"\s+", " ", spoken).strip()

    def cleanup_symbols(self, text: str) -> str:
        text = text.replace("\\", "").replace("/-", " ")
        text = re.sub(r"[\"“”‘’`]|(?<!\w)'|'(?!\w)", "", text)
        text = re.sub(r"[()\[\]{}【】]", " ", text)
        text = re.sub(r"[*#@&+=<>|~^_/]", " ", text)
        text = re.sub(r"।\s*।", "।", text)
        text = re.sub(r"\s+([,।?!.;:])", r"\1", text)
        return re.sub(r"\s+", " ", text).strip()
