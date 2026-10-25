"""Ported test corpus for edgepron.respell (IPA -> pronunciation respelling).

These cases are byte-for-byte ports of the acceptance tests from the
MIT-licensed ``ipa-to-pronunciation-respelling`` project (Attacktive):
``scheme-conformance.test.ts`` and ``converter.test.ts``. Portions copyright
2023 Attacktive, licensed under the MIT License.
"""

from __future__ import annotations

import pytest

from edgepron.respell.converter import ipa_to_canonical_respell
from edgepron.respell.mappings import symbol_by_ipa
from edgepron.respell.parser import OptionalToken, PhonemeToken, parse_ipa


def convert(ipa: str) -> str:
    return ipa_to_canonical_respell(ipa)


# Copied from scheme-conformance.test.ts CONFORMANCE_CASES.
CONFORMANCE_CASES = [
    ("short vowels", "cat vowel", "æ", "a"),
    ("short vowels", "kit vowel", "ɪ", "ih"),
    ("long vowels", "fleece vowel", "iː", "ee"),
    ("long vowels", "goose vowel", "uː", "oo"),
    ("diphthongs", "face vowel", "eɪ", "ay"),
    ("diphthongs", "price vowel", "aɪ", "eye"),
    ("diphthongs", "mouth vowel", "aʊ", "ow"),
    ("diphthongs", "choice vowel", "ɔɪ", "oy"),
    ("diphthongs", "British goat vowel", "əʊ", "oh"),
    ("consonants", "voiceless wh", "/ʍɛn/", "/whehn/"),
    ("affricates", "judge", "/d͡ʒʌd͡ʒ/", "/juhj/"),
    ("affricates", "choose", "/t͡ʃuːz/", "/chooz/"),
    ("rhotic vowels", "ordinary vowel plus r", "/kɑr/", "/kahr/"),
    ("rhotic vowels", "open-o plus r", "/stɔr/", "/stawr/"),
    ("rhotic vowels", "fused cure-like vowel", "/pʊər/", "/poor/"),
    ("stress", "primary stress uppercases the syllable", "ˈstrɪkt", "STRIHKT"),
    ("stress", "secondary stress stops primary stress propagation", "ˈæbˌstrækt", "ABstrakt"),
    (
        "multisyllabic",
        "explicit syllable boundaries become spaces",
        "kæt.ər.pɪl.ər",
        "kat er pihl er",
    ),
    ("optional segments", "optional glide stays parenthesized", "/səˈl(j)uːʃən/", "/suhL(Y)OOshuhn/"),
    ("syllabicity", "syllabic consonant remains a nucleus", "/ˈɹiːd͡ʒn̩/", "/REEjn/"),
    ("syllabicity", "non-syllabic adjacent vowel stays in the stressed nucleus", "ˈɛə̯", "EHUH"),
    ("syllabicity", "unmarked adjacent vowel starts a new nucleus", "ˈɛə", "EHuh"),
    ("nasal vowels", "open back nasal vowel", "ɑ̃", "on"),
    ("nasal vowels", "open-mid front nasal vowel", "ɛ̃", "an"),
    ("ignored detail", "aspiration is intentionally ignored", "tʰ", "t"),
    ("ignored detail", "half-length is intentionally ignored", "ɛˑ", "eh"),
]

# Copied from scheme-conformance.test.ts UNSUPPORTED_CASES.
UNSUPPORTED_DETAIL_CASES = [
    "ẽ", "n̥", "tʷ", "ʔ", "q",
]

# Additional converter.test.ts english-inventory cases.
CONVERTER_CASES = [
    ("aɪ", "eye"),
    ("ɡ", "g"),
    ("s", "s"),
    ("b", "b"),
    ("/ʍɛn/", "/whehn/"),
    ("æ", "a"),
    ("/", "/"),
    (" ", " "),
    ("x", "kh"),
    ("y", "ue"),
    ("œ", "eu"),
    ("a", "ah"),
    ("ɑ̃", "on"),
    ("kæt", "kat"),
    ("strɛŋθ", "strehngth"),
    ("hɛlp", "hehlp"),
    ("skrɪpt", "skrihpt"),
    ("hænd", "hand"),
    ("æskt", "askt"),
    ("wɜrld", "wurld"),
    ("æpl", "apl"),
    ("ˈkæt.ər", "KAT er"),
    ("kæt.ər.pɪl.ər", "kat er pihl er"),
    ("ˈstrɪkt", "STRIHKT"),
    ("ˈkæt.ə.ˈpɪl.ər", "KAT uh PIHL er"),
    ("/həˈloʊ(ː)/", "/huhLOH/"),
    ("(həˈloʊ)", "huhLOH"),
    ("həˈloːʊ", "huhLOH"),
    ("fjuː", "few"),
    ("kæˈtər", "kaTER"),
    ("ˈbɛri", "BEHree"),
    ("/d͡ʒʌd͡ʒ/", "/juhj/"),
    ("/ˈkjɔː-/", "/KYAW/"),
    ("/kleːn/", "/klehn/"),
    ("/ˈkoː.tɘ/", "/KAW tuh/"),
    ("/ˈɛə̯ɹɪə̯/", "/EHUHrihuh/"),
    ("/ˈaʊ̯tɪŋ/", "/OWtihng/"),
    ("ˈbaɪoʊ", "BEYEoh"),
    ("/ˈɹiːd͡ʒn̩/", "/REEjn/"),
    ("/bəʊɫ/", "/bohl/"),
    ("/t͡ʃuːz/", "/chooz/"),
    ("ˈæbˌstrækt", "ABstrakt"),
    ("ˈeɪˌbiː", "AYbee"),
    ("/ˈhaʊshəʊld/", "/HOWShohld/"),
    ("/səˈl(j)uːʃən/", "/suhL(Y)OOshuhn/"),
    ("/(st)/", "/(st)/"),
    ("/(s)/", "/(s)/"),
    ("/ˈɑː(ɹ).tʃə(ɹ)/", "/AH(R) chuh(r)/"),
    ("tʰ", "t"),
    ("ɛˑ", "eh"),
    ("ɑ̃", "on"),
    ("ɑr", "ahr"),
    ("ær", "ar"),
    ("ɛr", "ehr"),
    ("ɪr", "ihr"),
    ("ɔr", "awr"),
    ("ɒr", "or"),
    ("ʌr", "uhr"),
    ("ʊr", "uur"),
    ("ɛər", "air"),
    ("ɪər", "eer"),
    ("aɪər", "ire"),
    ("ɔɪər", "oir"),
    ("ʊər", "oor"),
    ("aʊər", "our"),
    ("ɜr", "ur"),
    ("jʊər", "ure"),
    ("ər", "er"),
]

# Phonemes the canonical scheme still refuses to approximate — rare / typologically
# exotic set only. The common foreign set (uvular r, palatal fricative, taps,
# retroflexes, centralized vowels, …) is now approximated; see ticket 12.
REJECTED_CONSONANTS = ["q", "ħ", "ɴ", "ɥ", "ɰ", "ʝ"]
REJECTED_VOWELS = ["ɞ"]
REJECTED_DETAILS = {
    "ẽ": "ẽ contains unsupported symbol(s) around: \"\u0303\".",
    "n̥": "n̥ contains unsupported symbol(s) around: \"\u0325\".",
    "tʷ": "tʷ contains unsupported symbol(s) around: \"\u02b7\".",
    "ʔ": "ʔ contains unsupported symbol(s) around: \"ʔ\".",
    "ʕ": "ʕ contains unsupported symbol(s) around: \"ʕ\".",
}


@pytest.mark.parametrize(("family", "label", "ipa", "expected"), CONFORMANCE_CASES, ids=[c[1] for c in CONFORMANCE_CASES])
def test_conformance(family, label, ipa, expected):
    assert convert(ipa) == expected


@pytest.mark.parametrize(("ipa", "expected"), CONVERTER_CASES, ids=[c[0] for c in CONVERTER_CASES])
def test_converter(ipa, expected):
    assert convert(ipa) == expected


@pytest.mark.parametrize("ipa", UNSUPPORTED_DETAIL_CASES)
def test_unsupported_detail_throws(ipa):
    with pytest.raises(ValueError):
        convert(ipa)


@pytest.mark.parametrize("ipa", REJECTED_CONSONANTS)
def test_rejects_lossy_foreign_consonants(ipa):
    with pytest.raises(ValueError):
        convert(ipa)


@pytest.mark.parametrize("ipa", REJECTED_VOWELS)
def test_rejects_lossy_foreign_vowels(ipa):
    with pytest.raises(ValueError):
        convert(ipa)


@pytest.mark.parametrize(("ipa", "message"), list(REJECTED_DETAILS.items()))
def test_unsupported_descriptive_messages(ipa, message):
    with pytest.raises(ValueError) as excinfo:
        convert(ipa)
    assert str(excinfo.value) == message
def test_alternative_respellings_retained_as_metadata():
    assert symbol_by_ipa["aɪ"].canonical_respelling == "eye"
    assert symbol_by_ipa["aɪ"].alternative_respellings == ("y",)


def test_no_symbol_silently_drops_a_phoneme():
    assert [s for s in symbol_by_ipa.values() if s.canonical_respelling == ""] == []


def test_safe_aliases_marked():
    assert symbol_by_ipa["ɫ"].support == "safe-alias"
    assert symbol_by_ipa["ɱ"].support == "safe-alias"
    assert symbol_by_ipa["ʧ"].support == "safe-alias"
    assert symbol_by_ipa["ɘ"].support == "safe-alias"


def test_foreign_reference_marked():
    assert symbol_by_ipa["x"].support == "reference-foreign"
    assert symbol_by_ipa["œ"].support == "reference-foreign"
    assert symbol_by_ipa["ɑ̃"].support == "reference-foreign"


def test_parser_preserves_vowel_length_and_optionals():
    tokens = parse_ipa("/ˈɑː(ɹ).tʃə(ɹ)/")
    phonemes = [t for t in tokens if isinstance(t, PhonemeToken)]
    assert [(p.ipa, p.long) for p in phonemes] == [
        ("ɑ", True), ("ɹ", False), ("tʃ", False), ("ə", False), ("ɹ", False),
    ]
    optionals = [t for t in tokens if isinstance(t, OptionalToken)]
    assert [o.boundary for o in optionals] == ["start", "end", "start", "end"]


def test_parser_preserves_syllabicity_diacritics():
    syllabic = next(t for t in parse_ipa("/n̩/") if isinstance(t, PhonemeToken))
    non_syllabic = next(t for t in parse_ipa("/ə̯/") if isinstance(t, PhonemeToken))
    assert syllabic.ipa == "n" and syllabic.syllabic is True
    assert non_syllabic.ipa == "ə" and non_syllabic.syllabic is False


def test_parser_keeps_non_syllabic_component_in_diphthong():
    token = next(t for t in parse_ipa("/aʊ̯/") if isinstance(t, PhonemeToken))
    assert token.ipa == "aʊ" and token.contains_non_syllabic_component is True


def test_parser_rejects_unclosed_optional_group():
    with pytest.raises(ValueError):
        parse_ipa("(s")


def test_parser_rejects_unmatched_closing_parenthesis():
    with pytest.raises(ValueError):
        parse_ipa("s)")