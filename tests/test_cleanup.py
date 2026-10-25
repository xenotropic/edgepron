"""Post-processing cleanup and non-English respell tests."""

from edgepron.cleanup import DASHES, PARENS, clean_phonetic
from edgepron.extraction.diaphonemes import ipa_to_respell
from edgepron.respell import ipa_to_canonical_respell


def test_cleanup_defaults():
    assert PARENS == "strip"
    assert DASHES == "remove"


def test_clean_phonetic_removes_dash_and_parens_by_default():
    assert clean_phonetic("N(Y)OO awr-LEENZ") == "NYOO awrLEENZ"
    assert clean_phonetic("ROOdo(l)f") == "ROOdolf"


def test_heuristic_respells_foreign_phonemes():
    out = ipa_to_respell("ˈdiːtʁɪç")
    assert "ʁ" not in out
    assert "ç" not in out
    assert "kh" in out  # ç -> kh
    assert "t" in out


def test_canonical_handles_foreign_without_raising():
    # ʁ / ç / ɨ previously raised ValueError; now they must respell.
    out = ipa_to_canonical_respell("diːtʁɪç")
    assert out
    assert "ʁ" not in out
    assert "ç" not in out
    out2 = ipa_to_canonical_respell("juːˌnaɪtɨd")
    assert out2
    assert "ɨ" not in out2