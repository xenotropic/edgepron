"""IPA -> pronunciation respelling assembly (ported).

Ported from ``src/scripts/converter.ts`` of the MIT-licensed
``ipa-to-pronunciation-respelling`` project by Attacktive.
Portions copyright 2023 Attacktive, licensed under the MIT License.
"""

from __future__ import annotations

from edgepron.respell.mappings import symbol_by_ipa
from edgepron.respell.parser import (
    BoundaryToken,
    LiteralToken,
    OptionalToken,
    PhonemeToken,
    StressToken,
    parse_ipa,
)
from edgepron.respell.syllabifier import find_syllable_boundaries


def _convert_token(token: PhonemeToken) -> str:
    symbol = symbol_by_ipa.get(token.ipa)
    if symbol is None:
        raise ValueError(f'Token "{token.ipa}" has no mapping!')
    return symbol.canonical_respelling


def convert(ipa: str) -> str:
    tokens = parse_ipa(ipa)
    syllable_boundaries = find_syllable_boundaries(tokens)
    result: list[str] = []
    current_syllable: list[str] = []
    pending_stress = False

    def flush_syllable() -> None:
        nonlocal pending_stress
        if not current_syllable:
            return
        syllable_text = "".join(current_syllable)
        if pending_stress:
            result.append(syllable_text.upper())
        else:
            result.append(syllable_text)
        pending_stress = False
        current_syllable.clear()

    for i, token in enumerate(tokens):
        if i in syllable_boundaries:
            flush_syllable()
        if isinstance(token, PhonemeToken):
            current_syllable.append(_convert_token(token))
            continue
        if isinstance(token, OptionalToken):
            current_syllable.append("(" if token.boundary == "start" else ")")
            continue
        if isinstance(token, StressToken):
            flush_syllable()
            pending_stress = token.level == "primary"
            continue
        if isinstance(token, BoundaryToken):
            flush_syllable()
            result.append(" ")
            continue
        flush_syllable()
        result.append(token.value)  # LiteralToken

    flush_syllable()
    return "".join(result).replace("()", "")


def ipa_to_canonical_respell(ipa: str) -> str:
    """Convert an IPA string to the canonical English pronunciation respelling."""
    return convert(ipa)


__all__ = ["convert", "ipa_to_canonical_respell"]