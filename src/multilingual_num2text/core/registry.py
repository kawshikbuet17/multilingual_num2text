from .language import Language

_LANGUAGES: dict[str, Language] = {}


def register_language(language: Language, code: str | None = None) -> None:
    """Adds or replaces a language. code defaults to language.code, e.g. register a variant as 'en-IN'."""
    _LANGUAGES[(code or language.code).lower()] = language


def unregister_language(code: str) -> Language | None:
    """Removes a language and returns it, or None when the code was not registered."""
    return _LANGUAGES.pop(code.lower(), None)


def get_language(code: str) -> Language:
    try:
        return _LANGUAGES[code.lower()]
    except KeyError:
        raise ValueError(f"Unknown language {code!r}. Available: {', '.join(available_languages())}") from None


def available_languages() -> list[str]:
    return sorted(_LANGUAGES)
