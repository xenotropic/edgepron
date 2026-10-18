"""TSV writer tests (plain, gzip, condensed)."""

import gzip

from lexphon.model import Entry
from lexphon.storage.tsv_writer import write_condensed, write_tsv

ENTRIES = [
    Entry(word="Istanbul", ipa="ˌɪstænˈbʊl", respell="IST-an-BUUL"),
    Entry(word="Zeus", ipa="zjuːs", respell="zy-oos", respell_derived=True),
]


def test_plain_tsv(tmp_path):
    path = str(tmp_path / "out.tsv")
    assert write_tsv(ENTRIES, path) == 2
    lines = open(path, encoding="utf-8").read().splitlines()
    assert lines[0] == "word\tipa\trespell\tipa_derived\trespell_derived\tsource"
    assert lines[1] == "Istanbul\tˌɪstænˈbʊl\tIST-an-BUUL\t0\t0\twikipedia"
    assert lines[2] == "Zeus\tzjuːs\tzy-oos\t0\t1\twikipedia"


def test_gzip_tsv(tmp_path):
    path = str(tmp_path / "out.tsv.gz")
    assert write_tsv(ENTRIES, path) == 2
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    assert len(lines) == 3
    assert lines[1].startswith("Istanbul\t")


def test_condensed_tsv_prefers_respell(tmp_path):
    path = str(tmp_path / "lookup.tsv")
    assert write_condensed(ENTRIES, path, phonetic="respell") == 2
    lines = open(path, encoding="utf-8").read().splitlines()
    assert lines[0] == "word\tphonetic"
    assert lines[1] == "Istanbul\tIST-an-BUUL"
    assert lines[2] == "Zeus\tzy-oos"


def test_condensed_tsv_ipa_choice(tmp_path):
    path = str(tmp_path / "lookup.tsv")
    assert write_condensed(ENTRIES, path, phonetic="ipa") == 2
    lines = open(path, encoding="utf-8").read().splitlines()
    assert lines[1] == "Istanbul\tˌɪstænˈbʊl"


def test_condensed_skips_missing_form(tmp_path):
    path = str(tmp_path / "lookup.tsv")
    entries = [Entry(word="X", ipa=None, respell=None)]
    assert write_condensed(entries, path, phonetic="respell") == 0