"""Diaphoneme normalization and IPA <-> respell conversion tests."""

from edgepron.extraction import diaphonemes


def test_ipa_to_respell_zeus():
    # /zjuːs/ is one syllable; the yod + vowel collapse into "zyoos".
    assert diaphonemes.ipa_to_respell("zjuːs") == "zyoos"


def test_ipa_to_respell_stressed_monosyllable():
    assert diaphonemes.ipa_to_respell("ˈæpəl") == "A-pəl"


def test_respell_to_ipa_istanbul():
    # "IST-an-BUUL" -> /ˌɪstænˈbʊl/ ("uu" is the /ʊ/ key; "an" splits a+n).
    assert diaphonemes.respell_to_ipa("IST-an-BUUL") == "ˈɪstænˈbʊl"


def test_respell_to_ipa_lowercase_has_no_stress_mark():
    assert diaphonemes.respell_to_ipa("yoh-sem-ih-tee") == "joʊsɛmɪtiː"


def test_round_trip_is_not_required_to_be_lossless():
    # Native -> derived is flagged lossy; only sanity-check it returns text.
    derived = diaphonemes.respell_to_ipa(diaphonemes.ipa_to_respell("zjuːs"))
    assert isinstance(derived, str) and derived