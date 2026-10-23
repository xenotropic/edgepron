"""IPA -> pronunciation-respelling symbol table (ported).

Ported from ``src/scripts/mappings.ts`` of the MIT-licensed
``ipa-to-pronunciation-respelling`` project by Attacktive
(https://github.com/Attacktive/ipa-to-pronunciation-respelling).
Portions copyright 2023 Attacktive, licensed under the MIT License.
Pinned upstream commit: 69d9f60179710d98dbd4170bf02c9556449be717.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

CATEGORY_SONORITY = {
    "vowel": 8,
    "glide": 7,
    "liquid": 6,
    "nasal": 5,
    "fricative": 4,
    "affricate": 3,
    "stop": 2,
}


@dataclass(frozen=True)
class IpaSymbol:
    ipa: str
    canonical_respelling: str
    alternative_respellings: tuple[str, ...]
    category: str
    sonority: int
    support: str


def _define_symbol(category: str):
    def define(
        ipa: str,
        canonical_respelling: str,
        alternative_respellings: tuple[str, ...] = (),
        support: str = "english",
    ) -> IpaSymbol:
        return IpaSymbol(
            ipa=ipa,
            canonical_respelling=canonical_respelling,
            alternative_respellings=alternative_respellings,
            category=category,
            sonority=CATEGORY_SONORITY[category],
            support=support,
        )

    return define


vowel = _define_symbol("vowel")
glide = _define_symbol("glide")
liquid = _define_symbol("liquid")
nasal = _define_symbol("nasal")
fricative = _define_symbol("fricative")
affricate = _define_symbol("affricate")
stop = _define_symbol("stop")


def _rhotic_vowel(ipa: str, base_respelling: str) -> IpaSymbol:
    return vowel(ipa, f"{base_respelling}r")


CONSONANT_SYMBOLS = [
    stop("b", "b"),
    affricate("tʃ", "ch", ("tch",)),
    stop("d", "d"),
    fricative("ð", "dh"),
    fricative("f", "f"),
    stop("ɡ", "g", ("gh",)),
    fricative("h", "h"),
    fricative("ɦ", "h", support="safe-alias"),
    affricate("dʒ", "j"),
    stop("k", "k"),
    fricative("x", "kh", support="reference-foreign"),
    liquid("l", "l"),
    liquid("ɫ", "l", support="safe-alias"),
    nasal("m", "m"),
    nasal("ɱ", "m", support="safe-alias"),
    nasal("n", "n"),
    nasal("ŋ", "ng"),
    stop("ŋk", "nk"),
    stop("p", "p"),
    liquid("r", "r"),
    liquid("ɹ", "r"),
    fricative("s", "s", ("ss",)),
    fricative("ʃ", "sh"),
    stop("t", "t"),
    fricative("θ", "th"),
    fricative("v", "v"),
    fricative("ʍ", "wh"),
    glide("w", "w"),
    glide("hw", "wh", support="safe-alias"),
    glide("j", "y"),
    fricative("z", "z"),
    fricative("ʒ", "zh"),
    affricate("ʣ", "dz", support="safe-alias"),
    affricate("ʤ", "j", support="safe-alias"),
    affricate("ʦ", "ts", support="safe-alias"),
    affricate("ʧ", "ch", support="safe-alias"),
]

VOWEL_SYMBOLS = [
    vowel("æ", "a"),
    vowel("ɑ", "ah"),
    vowel("ɑː", "ah"),
    vowel("ɛər", "air"),
    _rhotic_vowel("ɑːr", "ah"),
    _rhotic_vowel("ɑr", "ah"),
    _rhotic_vowel("ær", "a"),
    vowel("ɔː", "aw"),
    vowel("eɪ", "ay"),
    vowel("e", "eh", ("e",)),
    vowel("ɛ", "eh", ("e",)),
    vowel("iː", "ee"),
    vowel("i", "ee"),
    vowel("ɪər", "eer"),
    _rhotic_vowel("ɛr", "eh"),
    vowel("juː", "ew"),
    vowel("ju", "ew"),
    vowel("aɪ", "eye", ("y",)),
    vowel("ɪ", "ih", ("i",)),
    vowel("aɪər", "ire"),
    _rhotic_vowel("ɪr", "ih"),
    vowel("ɒ", "o"),
    vowel("oʊ", "oh"),
    vowel("əʊ", "oh"),
    vowel("ɔɪər", "oir"),
    vowel("uː", "oo"),
    vowel("u", "oo"),
    vowel("ʊər", "oor"),
    _rhotic_vowel("ɔːr", "aw"),
    _rhotic_vowel("ɔr", "aw"),
    _rhotic_vowel("ɒr", "o"),
    vowel("aʊər", "our"),
    vowel("aʊ", "ow"),
    vowel("ɔɪ", "oy"),
    vowel("ʌ", "uh", ("u",)),
    vowel("ɜːr", "ur"),
    vowel("ɜr", "ur"),
    vowel("jʊər", "ure"),
    _rhotic_vowel("ʌr", "uh"),
    vowel("ʊ", "uu"),
    _rhotic_vowel("ʊr", "uu"),
    vowel("ə", "uh"),
    vowel("ər", "er"),
    vowel("y", "ue", support="reference-foreign"),
    vowel("œ", "eu", support="reference-foreign"),
    vowel("ɘ", "uh", support="safe-alias"),
    vowel("ɜ", "uh"),
    vowel("ɐ", "uh"),
    vowel("ɚ", "er"),
    vowel("ɝ", "ur"),
    vowel("ɔ", "aw"),
    vowel("o", "aw"),
    vowel("oː", "aw"),
    vowel("a", "ah", support="reference-foreign"),
    vowel("ɑ̃", "on", support="reference-foreign"),
    vowel("ɛ̃", "an", support="reference-foreign"),
    vowel("ɔ̃", "on", support="reference-foreign"),
    vowel("œ̃", "un", support="reference-foreign"),
]

SYMBOLS = CONSONANT_SYMBOLS + VOWEL_SYMBOLS

symbol_by_ipa = {unicodedata.normalize("NFD", s.ipa): s for s in SYMBOLS}

STRESS_MARK = "\u02c8"
SECONDARY_STRESS_MARK = "\u02cc"

consonants = [s.ipa for s in CONSONANT_SYMBOLS]
vowels = [s.ipa for s in VOWEL_SYMBOLS]

_phoneme_chunks = sorted(
    {
        unicodedata.normalize("NFD", chunk).replace("\u02d0", "")
        for chunk in consonants + vowels
    },
    key=len,
    reverse=True,
)

ignored_symbols = ("\u0361", "\u035c", "-")

__all__ = [
    "symbol_by_ipa",
    "STRESS_MARK",
    "SECONDARY_STRESS_MARK",
    "consonants",
    "vowels",
    "phonemeChunks",
    "ignoredSymbols",
]

phonemeChunks = _phoneme_chunks
ignoredSymbols = ignored_symbols