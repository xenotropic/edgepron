"""Wiktionary dump lookup tests (fixture JSONL, no network)."""

import gzip
import json

from edgepron.wiktionary import entries_from_wiktionary, phrase_and_tokens, scan
from edgepron.wiktionary.dump import first_ipa
from edgepron.wiktionary.wordify import is_roman_numeral, normalize_key

ROWS = [
    {"word": "Al Pacino", "lang": "English", "lang_code": "en", "pos": "name",
     "sounds": [{"ipa": "/æl pəˈtʃiːnoʊ/"}]},
    {"word": "Pacino", "lang": "English", "lang_code": "en", "pos": "name",
     "sounds": [{"ipa": "/pəˈtʃiːnoʊ/"}]},
    {"word": "miserables", "lang": "French", "lang_code": "fr", "pos": "adj",
     "sounds": [{"ipa": "/mi.ze.ʁabl/"}]},
    # proper name + lowercase common sense -> dropped (ambiguous/common word)
    {"word": "Ginger", "lang": "English", "lang_code": "en", "pos": "name",
     "sounds": [{"ipa": "/ˈdʒɪndʒə/"}]},
    {"word": "ginger", "lang": "English", "lang_code": "en", "pos": "noun",
     "sounds": [{"ipa": "/ˈdʒɪndʒə/"}]},
    # pure common English noun -> dropped
    {"word": "lope", "lang": "English", "lang_code": "en", "pos": "noun",
     "sounds": [{"ipa": "/loʊp/"}]},
    # proper noun with a capitalized (figurative) noun sense -> kept
    {"word": "Paris", "lang": "English", "lang_code": "en", "pos": "name",
     "sounds": [{"ipa": "/ˈpærɪs/"}]},
    # common English word that also exists in French -> dropped (ticket 15)
    {"word": "ballet", "lang": "English", "lang_code": "en", "pos": "noun",
     "sounds": [{"ipa": "/bæˈleɪ/"}]},
    {"word": "ballet", "lang": "French", "lang_code": "fr", "pos": "noun",
     "sounds": [{"ipa": "/ba.lɛ/"}]},
    # roman numeral + common given name -> culled (tickets 18, 17)
    {"word": "XV", "lang": "English", "lang_code": "en", "pos": "name",
     "sounds": [{"ipa": "/ˈɛks ˈviː/"}]},
    {"word": "John", "lang": "English", "lang_code": "en", "pos": "name",
     "sounds": [{"ipa": "/dʒɒn/"}]},
]


def _write_dump(path, rows=ROWS):
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


def test_normalize_key_preserves_accents():
    assert normalize_key("Ångström") == "ångström"
    assert normalize_key("  New Orleans ") == "new orleans"


def test_phrase_and_tokens():
    assert phrase_and_tokens("Al Pacino") == ["Al Pacino", "Al", "Pacino"]
    assert phrase_and_tokens("Al Pacino", phrase_passthrough=False) == ["Al", "Pacino"]
    assert phrase_and_tokens("miserables") == ["miserables"]


def test_first_ipa_skips_null_and_strips_braces():
    assert first_ipa([{"ipa": None}, {"ipa": "/tʃæt/"}]) == "tʃæt"
    assert first_ipa([{"ipa": "[fɹi]"}, {"ipa": "/fɹiː/"}]) == "fɹi"


def test_scan_prefers_proper_and_drops_common(tmp_path):
    path = str(tmp_path / "dump.jsonl.gz")
    _write_dump(path)
    result = scan(path, ["pacino", "miserables", "ginger", "lope", "c", "paris", "al pacino", "ballet"])
    assert result["pacino"] == ("pəˈtʃiːnoʊ", "en")
    assert result["miserables"] == ("mi.ze.ʁabl", "fr")   # foreign kept
    assert result["al pacino"] == ("æl pəˈtʃiːnoʊ", "en")  # phrase kept
    assert result["paris"] == ("ˈpærɪs", "en")
    assert "ginger" not in result      # common word + name -> culled per ticket 16
    assert "lope" not in result        # common noun, no name sense -> dropped
    assert "ballet" not in result   # English common word, don't keep foreign twin
    assert "c" not in result        # single char -> dropped


def test_is_roman_numeral():
    assert is_roman_numeral("XV")
    assert is_roman_numeral("VIII")
    assert not is_roman_numeral("Li")
    assert not is_roman_numeral("mix")
    assert not is_roman_numeral("X")  # single letter handled separately


def test_roman_and_common_names_culled(tmp_path):
    path = str(tmp_path / "dump.jsonl.gz")
    _write_dump(path)
    entries = entries_from_wiktionary(["XV", "John", "Paris"], path)
    assert {e.word for e in entries} == {"Paris"}


def test_entries_prefer_phrase_and_tag_language(tmp_path):
    path = str(tmp_path / "dump.jsonl.gz")
    _write_dump(path)
    entries = entries_from_wiktionary(["Al Pacino", "miserables", "lope"], path)
    words = {e.word: e for e in entries}
    assert set(words) == {"Al Pacino", "miserables"}
    assert words["Al Pacino"].ipa == "æl pəˈtʃiːnoʊ"
    assert words["Al Pacino"].lang == "en"
    assert words["Al Pacino"].source == "wiktionary"
    assert words["miserables"].ipa == "mi.ze.ʁabl"
    assert words["miserables"].lang == "fr"