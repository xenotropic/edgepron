"""TSV writers: full (plain / gzip) and condensed two-column lookup."""

from __future__ import annotations

import gzip
import os
import sys
from collections.abc import Iterable

from edgepron.model import Entry
from edgepron.cleanup import clean_phonetic

_HEADER = ["word", "ipa", "respell", "ipa_derived", "respell_derived", "respell_method", "source", "lang"]


def _row(entry: Entry) -> list[str]:
    return [
        entry.word,
        entry.ipa or "",
        entry.respell or "",
        "1" if entry.ipa_derived else "0",
        "1" if entry.respell_derived else "0",
        entry.respell_method or "",
        entry.source,
        entry.lang or "",
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


def write_condensed(entries: Iterable[Entry], path: str, phonetic: str = "respell",
                    header: bool = True) -> int:
    """Write a two-column ``word <TAB> phonetic`` lookup.

    ``phonetic`` selects the preferred form (``respell`` or ``ipa``); rows whose
    chosen form is missing are skipped. ``.gz`` suffix compresses the output.
    ``path == "-"`` writes to stdout; set ``header=False`` for data-only stdout.
    """
    entries = list(entries)
    written = 0

    def emit(fh) -> None:
        nonlocal written
        if header:
            fh.write("word\tphonetic\n")
        for entry in entries:
            value = entry.respell if phonetic == "respell" else entry.ipa
            if value:
                fh.write(f"{entry.word}\t{clean_phonetic(value, multiword=(' ' in entry.word))}\n")
                written += 1

    if path == "-":
        emit(sys.stdout)
        return written

    with _open(path, gz=path.endswith(".gz")) as fh:
        emit(fh)
    return written