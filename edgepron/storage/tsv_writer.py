"""TSV writers: full (plain / gzip) and condensed two-column lookup."""

from __future__ import annotations

import gzip
import os
from collections.abc import Iterable

from edgepron.model import Entry

_HEADER = ["word", "ipa", "respell", "ipa_derived", "respell_derived", "source"]


def _row(entry: Entry) -> list[str]:
    return [
        entry.word,
        entry.ipa or "",
        entry.respell or "",
        "1" if entry.ipa_derived else "0",
        "1" if entry.respell_derived else "0",
        entry.source,
    ]


def _open(path: str, gz: bool):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if gz:
        return gzip.open(path, "wt", encoding="utf-8", newline="")
    return open(path, "w", encoding="utf-8", newline="")


def write_tsv(entries: Iterable[Entry], path: str) -> int:
    """Write the full six-column TSV (gzip-compressed when ``path`` ends in .gz)."""
    entries = list(entries)
    with _open(path, gz=path.endswith(".gz")) as fh:
        fh.write("\t".join(_HEADER) + "\n")
        for entry in entries:
            fh.write("\t".join(_row(entry)) + "\n")
    return len(entries)


def write_tsv_gz(entries: Iterable[Entry], path: str) -> int:
    """Write the full TSV, gzip-compressed (``.gz`` suffix added if missing)."""
    if not path.endswith(".gz"):
        path += ".gz"
    return write_tsv(entries, path)


def write_condensed(entries: Iterable[Entry], path: str, phonetic: str = "respell") -> int:
    """Write a two-column ``word <TAB> phonetic`` lookup.

    ``phonetic`` selects the preferred form (``respell`` or ``ipa``); rows whose
    chosen form is missing are skipped. ``.gz`` suffix compresses the output.
    """
    entries = list(entries)
    written = 0
    with _open(path, gz=path.endswith(".gz")) as fh:
        fh.write("word\tphonetic\n")
        for entry in entries:
            value = entry.respell if phonetic == "respell" else entry.ipa
            if value:
                fh.write(f"{entry.word}\t{value}\n")
                written += 1
    return written