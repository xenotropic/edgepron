"""Wiktionary dump lookup tests (fixture JSONL, no network)."""

import gzip
import json

from edgepron.wiktionary import entries_from_wiktionary, phrase_and_tokens, scan
from edgepron.wiktionary.dump import first_ipa
from edgepron.wiktionary.wordify import normalize_key

ROWS = [
    {"word": "Al Pacino", "lang": "English", "lang_code": "en",
     "sounds": [{"ipa": "/æl pəˈtʃiːnoʊ/"}]},
    {"word": "Pacino", "lang": "English", "lang_code": "en",
     "sounds": [{"ipa": "/pəˈtʃiːnoʊ/"}]},
    {"word": "miserables", "lang": "French", "lang_code": "fr",
     "sounds": [{"ipa": "/mi.ze.ʁabl/"}]},
    {"word": "chat", "lang": "English", "lang_code": "en",
     "sounds": [{"ipa": "/tʃæt/"}]},
    {"word": "chat", "lang": "French", "lang_code": "fr",
     "sounds": [{"ipa": "/ʃa/"}]},
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


def test_scan_prefers_english_then_falls_back(tmp_path):
    path = str(tmp_path / "dump.jsonl.gz")
    _write_dump(path)
    result = scan(path, ["pacino", "miserables", "chat", "al pacino"])
    assert result["pacino"] == ("pəˈtʃiːnoʊ", "en")
    assert result["miserables"] == ("mi.ze.ʁabl", "fr")
    assert result["chat"] == ("tʃæt", "en")  # en wins over the fr entry
    assert result["al pacino"] == ("æl pəˈtʃiːnoʊ", "en")


def test_entries_prefer_phrase_and_tag_language(tmp_path):
    path = str(tmp_path / "dump.jsonl.gz")
    _write_dump(path)
    entries = entries_from_wiktionary(["Al Pacino", "miserables"], path)
    words = {e.word: e for e in entries}
    assert set(words) == {"Al Pacino", "miserables"}
    assert words["Al Pacino"].ipa == "æl pəˈtʃiːnoʊ"
    assert words["Al Pacino"].lang == "en"
    assert words["Al Pacino"].source == "wiktionary"
    assert words["miserables"].ipa == "mi.ze.ʁabl"
    assert words["miserables"].lang == "fr"