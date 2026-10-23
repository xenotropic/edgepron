"""IPA parser/tokenizer (ported).

Ported from ``src/scripts/parser.ts`` of the MIT-licensed
``ipa-to-pronunciation-respelling`` project by Attacktive.
Portions copyright 2023 Attacktive, licensed under the MIT License.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

from edgepron.respell.mappings import (
    STRESS_MARK,
    SECONDARY_STRESS_MARK,
    phonemeChunks,
    ignoredSymbols,
    vowels,
)

LENGTH_MARK = "\u02d0"

SYLLABICITY_BY_DIACRITIC = {
    "\u030d": True,
    "\u0329": True,
    "\u032f": False,
}

STRESS_LEVEL_BY_MARK = {
    STRESS_MARK: "primary",
    SECONDARY_STRESS_MARK: "secondary",
}

SYLLABLE_SEPARATORS = {" ", "."}
LITERALS = {"/", "[", "]"}
OPTIONAL_BOUNDARY_BY_PARENTHESIS = {"(": "start", ")": "end"}
PARENTHESIS_DEPTH_CHANGE = {"(": 1, ")": -1}

IGNORED_PHONETIC_MARKS = {LENGTH_MARK, "\u02b0", "\u02d1"}


def _clean_vowel(value: str) -> str:
    return unicodedata.normalize("NFD", value).replace(LENGTH_MARK, "")


_normalized_vowels = sorted({_clean_vowel(v) for v in vowels}, key=lambda v: -len(v))
vowel_chunks = set(_normalized_vowels)
r_colored_vowels = {v for v in _normalized_vowels if v.endswith("r")}


def _has_multiple_segments(ipa: str) -> bool:
    return sum(1 for c in ipa if unicodedata.category(c).startswith("L")) > 1


def _closes_outer_parenthesis_early(ipa: str) -> bool:
    depth = 0
    for i in range(len(ipa) - 1):
        depth += PARENTHESIS_DEPTH_CHANGE.get(ipa[i], 0)
        if depth == 0:
            return True
    return False


def _unwrap_outer_parentheses(ipa: str) -> str:
    if not ipa.startswith("(") or not ipa.endswith(")") or _closes_outer_parenthesis_early(ipa):
        return ipa
    return ipa[1:-1]


def _match_candidate_at(ipa: str, index: int, candidate: str):
    source_index = index
    long = False
    for candidate_char in candidate:
        while source_index < len(ipa) and ipa[source_index] == LENGTH_MARK:
            long = True
            source_index += 1
        if source_index >= len(ipa) or ipa[source_index] != candidate_char:
            return None
        source_index += 1
    while source_index < len(ipa) and ipa[source_index] == LENGTH_MARK:
        long = True
        source_index += 1
    return {"ipa": candidate, "next_index": source_index, "long": long}


def _starts_with_vowel_at(ipa: str, index: int) -> bool:
    return any(_match_candidate_at(ipa, index, v) is not None for v in _normalized_vowels)


def _match_phoneme_at(ipa: str, index: int):
    for chunk in phonemeChunks:
        match = _match_candidate_at(ipa, index, chunk)
        if match is None:
            continue
        if chunk in r_colored_vowels and _starts_with_vowel_at(ipa, match["next_index"]):
            continue
        return match
    return None


def _clean_ipa(ipa: str) -> str:
    result = _unwrap_outer_parentheses(unicodedata.normalize("NFD", ipa))
    for ignored in ignoredSymbols:
        result = result.replace(ignored, "")
    return result


@dataclass
class PhonemeToken:
    ipa: str
    long: bool
    syllabic: bool | None = None
    contains_non_syllabic_component: bool = False


@dataclass
class StressToken:
    level: str


@dataclass
class BoundaryToken:
    separator: str


@dataclass
class LiteralToken:
    value: str


@dataclass
class OptionalToken:
    boundary: str


ParsedToken = PhonemeToken | StressToken | BoundaryToken | LiteralToken | OptionalToken


@dataclass
class ParserContext:
    original_ipa: str
    cleaned_ipa: str
    tokens: list = field(default_factory=list)
    index: int = 0
    optional_depth: int = 0
def _consume_parenthesis(ctx: ParserContext) -> bool:
    char = ctx.cleaned_ipa[ctx.index]
    boundary = OPTIONAL_BOUNDARY_BY_PARENTHESIS.get(char)
    if boundary is None:
        return False
    if boundary == "end" and ctx.optional_depth == 0:
        raise ValueError(f"{ctx.original_ipa} contains an unmatched closing parenthesis.")
    ctx.tokens.append(OptionalToken(boundary=boundary))
    ctx.optional_depth += PARENTHESIS_DEPTH_CHANGE[char]
    ctx.index += 1
    return True


def _consume_stress(ctx: ParserContext) -> bool:
    level = STRESS_LEVEL_BY_MARK.get(ctx.cleaned_ipa[ctx.index])
    if level is None:
        return False
    ctx.tokens.append(StressToken(level=level))
    ctx.index += 1
    return True


def _consume_boundary(ctx: ParserContext) -> bool:
    char = ctx.cleaned_ipa[ctx.index]
    if char not in SYLLABLE_SEPARATORS:
        return False
    ctx.tokens.append(BoundaryToken(separator=char))
    ctx.index += 1
    return True


def _consume_literal(ctx: ParserContext) -> bool:
    char = ctx.cleaned_ipa[ctx.index]
    if char not in LITERALS:
        return False
    ctx.tokens.append(LiteralToken(value=char))
    ctx.index += 1
    return True


def _consume_syllabicity(ctx: ParserContext) -> bool:
    syllabic = SYLLABICITY_BY_DIACRITIC.get(ctx.cleaned_ipa[ctx.index])
    if syllabic is None:
        return False
    if ctx.tokens and isinstance(ctx.tokens[-1], PhonemeToken):
        token = ctx.tokens[-1]
        if not syllabic and token.ipa in vowel_chunks and _has_multiple_segments(token.ipa):
            token.contains_non_syllabic_component = True
        else:
            token.syllabic = syllabic
    ctx.index += 1
    return True


def _consume_phoneme(ctx: ParserContext) -> bool:
    match = _match_phoneme_at(ctx.cleaned_ipa, ctx.index)
    if match is None:
        return False
    ctx.tokens.append(PhonemeToken(ipa=match["ipa"], long=match["long"]))
    ctx.index = match["next_index"]
    return True


def _consume_ignored_phonetic_mark(ctx: ParserContext) -> bool:
    if ctx.cleaned_ipa[ctx.index] not in IGNORED_PHONETIC_MARKS:
        return False
    ctx.index += 1
    return True


TOKEN_CONSUMERS = [
    _consume_parenthesis,
    _consume_stress,
    _consume_boundary,
    _consume_literal,
    _consume_syllabicity,
    _consume_phoneme,
    _consume_ignored_phonetic_mark,
]


def parse_ipa(ipa: str) -> list[ParsedToken]:
    ctx = ParserContext(original_ipa=ipa, cleaned_ipa=_clean_ipa(ipa))
    while ctx.index < len(ctx.cleaned_ipa):
        consumed = any(consumer(ctx) for consumer in TOKEN_CONSUMERS)
        if not consumed:
            raise ValueError(
                f'{ipa} contains unsupported symbol(s) around: "{ctx.cleaned_ipa[ctx.index]}".'
            )
    if ctx.optional_depth != 0:
        raise ValueError(f"{ipa} contains an unclosed optional group.")
    return ctx.tokens


__all__ = ["parse_ipa", "ParsedToken", "PhonemeToken"]