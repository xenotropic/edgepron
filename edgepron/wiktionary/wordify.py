"""Turn discovery titles (phrases) into Wiktionary lookup keys."""

from __future__ import annotations

import re

# Unicode word characters (letters/digits), excluding underscore; allows an
# internal apostrophe (O'Toole, l'état). Splits "Al Pacino" -> Al, Pacino.
_WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)


def normalize_key(word: str) -> str:
    """Lowercase a lookup key (accents preserved) for Wiktionary matching."""
    return (word or "").strip().lower()


def phrase_and_tokens(title: str, phrase_passthrough: bool = True) -> list[str]:
    """Ordered candidate keys for a discovery title.

    When ``phrase_passthrough`` is enabled the whole phrase is emitted first, so
    a caller can prefer the multi-word headword ("Al Pacino") and fall back to
    word tokens ("Al", "Pacino") when the phrase itself is absent.
    """
    title = (title or "").strip()
    if not title:
        return []
    keys: list[str] = []
    if phrase_passthrough:
        keys.append(title)
    for token in _WORD_RE.findall(title):
        if token not in keys:
            keys.append(token)
    return keys


_ROMAN_RE = re.compile(r"[IVXLCDM]{2,}")


def is_roman_numeral(word: str) -> bool:
    """True if ``word`` is entirely uppercase roman-numeral letters (XV, VIII)."""
    return bool(_ROMAN_RE.fullmatch((word or "").strip()))