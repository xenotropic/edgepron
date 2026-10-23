"""Syllable-boundary inference (ported).

Ported from ``src/scripts/syllabifier.ts`` of the MIT-licensed
``ipa-to-pronunciation-respelling`` project by Attacktive.
Portions copyright 2023 Attacktive, licensed under the MIT License.
"""

from __future__ import annotations

from edgepron.respell.mappings import symbol_by_ipa
from edgepron.respell.parser import ParsedToken, PhonemeToken

LEGAL_ONSET_CLUSTERS = {
    "pl", "bl", "kl", "gl", "fl", "sl",
    "pr", "br", "tr", "dr", "kr", "gr", "fr", "θr", "ʃr",
    "tw", "dw", "kw", "gw", "sw", "θw", "hw",
    "pj", "bj", "tj", "dj", "kj", "gj", "fj", "vj", "θj", "sj", "zj", "hj", "mj", "nj", "lj",
    "sp", "st", "sk", "sm", "sn",
    "spl", "spr", "str", "skr", "skw",
}

NON_ONSET_PHONEMES = {"ŋ", "ɴ", "ŋk"}
ONSET_EQUIVALENTS = {
    "ɡ": "g",
    "ɹ": "r",
    "ɾ": "r",
    "ɽ": "r",
    "ʁ": "r",
    "ɫ": "l",
}


def _is_vowel(token: PhonemeToken) -> bool:
    symbol = symbol_by_ipa.get(token.ipa)
    return symbol is not None and symbol.category == "vowel"


def _is_nucleus(token: PhonemeToken) -> bool:
    if token.syllabic is not None:
        return token.syllabic
    return _is_vowel(token)


def _is_non_syllabic_vowel(token: PhonemeToken) -> bool:
    return _is_vowel(token) and token.syllabic is False


def _normalize_onset(tokens: list[PhonemeToken]) -> str:
    return "".join(ONSET_EQUIVALENTS.get(t.ipa, t.ipa) for t in tokens)


def _can_be_onset(tokens: list[PhonemeToken]) -> bool:
    if len(tokens) == 1:
        return tokens[0].ipa not in NON_ONSET_PHONEMES and not _is_nucleus(tokens[0])
    return _normalize_onset(tokens) in LEGAL_ONSET_CLUSTERS


def _find_boundary_before(
    tokens: list[ParsedToken],
    consonant_indexes: list[int],
    next_nucleus_index: int,
) -> int:
    for onset_start in range(len(consonant_indexes)):
        onset = [
            t
            for i in consonant_indexes[onset_start:]
            if isinstance((t := tokens[i]), PhonemeToken)
        ]
        if _can_be_onset(onset):
            return consonant_indexes[onset_start]
    return next_nucleus_index


def _finish_nucleus(nuclei: list[list[int]], current: list[int]) -> list[int]:
    if current:
        nuclei.append(current)
    return []


def _find_nuclei(tokens: list[ParsedToken], start: int, end: int) -> list[list[int]]:
    nuclei: list[list[int]] = []
    current: list[int] = []
    for i in range(start, end):
        token = tokens[i]
        if not isinstance(token, PhonemeToken):
            continue
        if _is_nucleus(token):
            _finish_nucleus(nuclei, current)
            current = [i]
            continue
        if _is_non_syllabic_vowel(token) and current:
            current.append(i)
            continue
        current = _finish_nucleus(nuclei, current)
    _finish_nucleus(nuclei, current)
    return nuclei


def _find_consonant_indexes(
    tokens: list[ParsedToken], previous_nucleus: list[int], next_nucleus: list[int]
) -> list[int]:
    result: list[int] = []
    for token_index in range(previous_nucleus[-1] + 1, next_nucleus[0]):
        if isinstance(tokens[token_index], PhonemeToken):
            result.append(token_index)
    return result


def _find_boundary_between_nuclei(
    tokens: list[ParsedToken], previous_nucleus: list[int], next_nucleus: list[int]
) -> int:
    consonant_indexes = _find_consonant_indexes(tokens, previous_nucleus, next_nucleus)
    if not consonant_indexes:
        return next_nucleus[0]
    return _find_boundary_before(tokens, consonant_indexes, next_nucleus[0])


def _find_region_boundaries(tokens: list[ParsedToken], start: int, end: int) -> list[int]:
    nuclei = _find_nuclei(tokens, start, end)
    boundaries: list[int] = []
    for i in range(1, len(nuclei)):
        boundaries.append(_find_boundary_between_nuclei(tokens, nuclei[i - 1], nuclei[i]))
    return boundaries


def _add_region_boundaries(
    boundaries: set[int], tokens: list[ParsedToken], start: int, end: int
) -> None:
    for boundary in _find_region_boundaries(tokens, start, end):
        boundaries.add(boundary)


def _is_region_break(token: ParsedToken) -> bool:
    from edgepron.respell.parser import StressToken, BoundaryToken, LiteralToken

    return isinstance(token, (StressToken, BoundaryToken, LiteralToken))


def find_syllable_boundaries(tokens: list[ParsedToken]) -> set[int]:
    boundaries: set[int] = set()
    region_start = 0
    for i in range(len(tokens)):
        if not _is_region_break(tokens[i]):
            continue
        _add_region_boundaries(boundaries, tokens, region_start, i)
        region_start = i + 1
    _add_region_boundaries(boundaries, tokens, region_start, len(tokens))
    return boundaries


__all__ = ["find_syllable_boundaries"]