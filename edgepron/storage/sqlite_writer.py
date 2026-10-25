"""SQLite writer: ``WITHOUT ROWID``, low-memory PRAGMAs."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterable

from edgepron.model import Entry
from edgepron.cleanup import clean_phonetic

_SCHEMA = """
CREATE TABLE IF NOT EXISTS pronunciations (
    word            TEXT PRIMARY KEY,
    ipa             TEXT,
    respell         TEXT,
    ipa_derived     INTEGER NOT NULL DEFAULT 0,
    respell_derived INTEGER NOT NULL DEFAULT 0,
    respell_method  TEXT,
    source          TEXT NOT NULL DEFAULT 'wikipedia',
    lang            TEXT
) WITHOUT ROWID;
"""


def write_sqlite(entries: Iterable[Entry], path: str, low_memory: bool = True) -> int:
    """Write entries to ``path`` and return the number of rows written."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        if low_memory:
            conn.execute("PRAGMA journal_mode=OFF")
            conn.execute("PRAGMA synchronous=OFF")
            conn.execute("PRAGMA cache_size=-2000")
            conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute(_SCHEMA)
        conn.executemany(
            "INSERT OR REPLACE INTO pronunciations "
            "(word, ipa, respell, ipa_derived, respell_derived, respell_method, source, lang) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                (e.word, e.ipa, e.respell, int(e.ipa_derived), int(e.respell_derived),
                 e.respell_method, e.source, e.lang)
                for e in entries
            ),
        )
        conn.commit()
        return conn.total_changes
    finally:
        conn.close()


_LOOKUP_SCHEMA = """
CREATE TABLE IF NOT EXISTS pronunciations (
    word     TEXT PRIMARY KEY,
    phonetic TEXT
) WITHOUT ROWID;
"""


def write_sqlite_lookup(entries: Iterable[Entry], path: str, phonetic: str = "respell",
                        lowercase: bool = True, low_memory: bool = True) -> int:
    """Write a minimal two-column ``word -> phonetic`` lookup table.

    ``phonetic`` selects the value form (``respell`` or ``ipa``); rows whose
    chosen form is missing are skipped. ``lowercase`` folds keys via
    ``str.lower()`` (accents preserved). Same low-memory PRAGMAs as
    ``write_sqlite``. Returns the number of rows written.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path)
    written = 0
    try:
        if low_memory:
            conn.execute("PRAGMA journal_mode=OFF")
            conn.execute("PRAGMA synchronous=OFF")
            conn.execute("PRAGMA cache_size=-2000")
            conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute(_LOOKUP_SCHEMA)
        for entry in entries:
            value = entry.respell if phonetic == "respell" else entry.ipa
            if not value:
                continue
            key = entry.word.lower() if lowercase else entry.word
            conn.execute(
                "INSERT OR REPLACE INTO pronunciations (word, phonetic) VALUES (?, ?)",
                (key, clean_phonetic(value)),
            )
            written += 1
        conn.commit()
        return written
    finally:
        conn.close()