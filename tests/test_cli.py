"""CLI entry-building tests (native vs derived forms, provenance)."""

from edgepron.cli import _build_entry
from edgepron.extraction.parser import Extracted


def test_native_respell_is_preferred_and_not_flagged_derived():
    entry = _build_entry("Istanbul", Extracted(ipa="ˌɪstænˈbʊl", respell="IST-an-BUUL"))
    assert entry.respell == "IST-an-BUUL"
    assert entry.respell_derived is False
    assert entry.respell_method is None


def test_ipa_only_uses_canonical_converter():
    entry = _build_entry("strict", Extracted(ipa="ˈstrɪkt", respell=None))
    assert entry.respell == "STRIHKT"
    assert entry.respell_derived is True
    assert entry.respell_method == "canonical"


def test_multi_pronunciation_uses_first_variant():
    entry = _build_entry("quinoa", Extracted(ipa="ˈkiːnwɑː,_kiˈnoʊə", respell=None))
    assert entry.respell == "KEENwah"
    assert entry.respell_method == "canonical"


def test_unsupported_ipa_falls_back_to_heuristic():
    # "q" is rejected by the canonical port but passes through the legacy heuristic.
    entry = _build_entry("q", Extracted(ipa="q", respell=None))
    assert entry.respell == "q"
    assert entry.respell_derived is True
    assert entry.respell_method == "heuristic"


def test_no_forms_is_skipped():
    assert _build_entry("Earth", Extracted(ipa=None, respell=None)) is None