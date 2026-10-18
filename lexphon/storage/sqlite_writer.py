"""SQLite writer: ``WITHOUT ROWID``, low-memory PRAGMAs."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterable

from lexphon.model import Entry

_SCHEMA = """
CREATE TABLE IF NOT EXISTS pronunciations (
    word            TEXT PRIMARY KEY,
    ipa             TEXT,
    respell         TEXT,
    ipa_derived     INTEGER NOT NULL DEFAULT 0,
    respell_derived INTEGER NOT NULL DEFAULT 0,
    source          TEXT NOT NULL DEFAULT 'wikipedia'
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
            "(word, ipa, respell, ipa_derived, respell_derived, source) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                (e.word, e.ipa, e.respell, int(e.ipa_derived), int(e.respell_derived), e.source)
                for e in entries
            ),
        )
        conn.commit()
        return conn.total_changes
    finally:
        conn.close()