"""SQLite writer tests."""

import sqlite3

from edgepron.model import Entry
from edgepron.storage.sqlite_writer import write_sqlite, write_sqlite_lookup


def _rows(path):
    conn = sqlite3.connect(path)
    try:
        return conn.execute(
            "SELECT word, ipa, respell, ipa_derived, respell_derived, respell_method, source, lang "
            "FROM pronunciations ORDER BY word").fetchall()
    finally:
        conn.close()


def test_write_and_readback(tmp_path):
    path = str(tmp_path / "out.db")
    entries = [
        Entry(word="Istanbul", ipa="ˌɪstænˈbʊl", respell="IST-an-BUUL"),
        Entry(word="Zeus", ipa="zjuːs", respell="zy-oos", respell_derived=True,
              respell_method="canonical"),
    ]
    written = write_sqlite(entries, path)
    assert written == 2

    rows = _rows(path)
    assert rows == [
        ("Istanbul", "ˌɪstænˈbʊl", "IST-an-BUUL", 0, 0, None, "wikipedia", None),
        ("Zeus", "zjuːs", "zy-oos", 0, 1, "canonical", "wikipedia", None),
    ]


def test_schema_is_without_rowid(tmp_path):
    path = str(tmp_path / "out.db")
    write_sqlite([Entry(word="Earth")], path)
    conn = sqlite3.connect(path)
    try:
        schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='pronunciations'").fetchone()[0]
    finally:
        conn.close()
    assert "WITHOUT ROWID" in schema


def test_upsert_on_duplicate_word(tmp_path):
    path = str(tmp_path / "out.db")
    write_sqlite([Entry(word="Zeus", ipa="zjuːs")], path)
    write_sqlite([Entry(word="Zeus", ipa="zjuːs", respell="zy-oos")], path)
    rows = _rows(path)
    assert len(rows) == 1
    assert rows[0][2] == "zy-oos"


def _lookup_rows(path):
    conn = sqlite3.connect(path)
    try:
        return conn.execute("SELECT word, phonetic FROM pronunciations ORDER BY word").fetchall()
    finally:
        conn.close()


def test_sqlite_lookup_lowercases_and_keeps_accents(tmp_path):
    path = str(tmp_path / "lookup.db")
    entries = [
        Entry(word="Ångström", ipa=None, respell="ANG-struhm"),
        Entry(word="Istanbul", ipa="ˌɪstænˈbʊl", respell="IST-an-BUUL"),
    ]
    assert write_sqlite_lookup(entries, path) == 2
    assert _lookup_rows(path) == [
        ("istanbul", "IST-an-BUUL"),
        ("ångström", "ANG-struhm"),
    ]


def test_sqlite_lookup_ipa_choice_and_skips_missing(tmp_path):
    path = str(tmp_path / "lookup.db")
    entries = [
        Entry(word="Zeus", ipa="zjuːs", respell=None),
        Entry(word="Earth", ipa=None, respell=None),
    ]
    assert write_sqlite_lookup(entries, path, phonetic="ipa") == 1
    assert _lookup_rows(path) == [("zeus", "zjuːs")]


def test_sqlite_lookup_schema_is_without_rowid(tmp_path):
    path = str(tmp_path / "lookup.db")
    write_sqlite_lookup([Entry(word="X", respell="ex")], path)
    conn = sqlite3.connect(path)
    try:
        schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='pronunciations'").fetchone()[0]
    finally:
        conn.close()
    assert "WITHOUT ROWID" in schema