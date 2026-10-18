"""SQLite writer tests."""

import sqlite3

from lexphon.model import Entry
from lexphon.storage.sqlite_writer import write_sqlite


def _rows(path):
    conn = sqlite3.connect(path)
    try:
        return conn.execute("SELECT word, ipa, respell, ipa_derived, respell_derived, source "
                            "FROM pronunciations ORDER BY word").fetchall()
    finally:
        conn.close()


def test_write_and_readback(tmp_path):
    path = str(tmp_path / "out.db")
    entries = [
        Entry(word="Istanbul", ipa="ˌɪstænˈbʊl", respell="IST-an-BUUL"),
        Entry(word="Zeus", ipa="zjuːs", respell="zy-oos", respell_derived=True),
    ]
    written = write_sqlite(entries, path)
    assert written == 2

    rows = _rows(path)
    assert rows == [
        ("Istanbul", "ˌɪstænˈbʊl", "IST-an-BUUL", 0, 0, "wikipedia"),
        ("Zeus", "zjuːs", "zy-oos", 0, 1, "wikipedia"),
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