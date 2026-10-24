"""Stream the raw enwiktionary wiktextract JSONL and pick pronunciations."""

from __future__ import annotations

import gzip
import json

from edgepron.wiktionary.wordify import normalize_key


def _strip_ipa(text: str) -> str:
    """Remove the ``/.../`` or ``[...]`` delimiters around an IPA string."""
    t = (text or "").strip()
    if len(t) >= 2 and (t[0], t[-1]) in (("/", "/"), ("[", "]")):
        t = t[1:-1]
    return t.strip()


def first_ipa(sounds: list) -> str | None:
    """Return the first non-empty IPA in a wiktextract ``sounds`` list."""
    for sound in sounds or []:
        if not isinstance(sound, dict):
            continue
        ipa = _strip_ipa(str(sound.get("ipa") or ""))
        if ipa:
            return ipa
    return None


def scan(gz_path: str, want: set[str] | list[str]) -> dict[str, tuple[str, str]]:
    """Stream ``gz_path`` once and return ``{normalized_key: (ipa, lang_code)}``.

    For each wanted key the best pronunciation is chosen English-first, else the
    first non-English language section encountered. Only keys present in
    ``want`` are retained, so the 24.8 GB uncompressed stream is never held in
    memory.
    """
    wanted = {normalize_key(w) for w in want}
    found: dict[str, list[tuple[str, str]]] = {w: [] for w in wanted}

    opening = gzip.open if gz_path.endswith(".gz") else open
    with opening(gz_path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = normalize_key(str(entry.get("word") or ""))
            if key not in wanted:
                continue
            ipa = first_ipa(entry.get("sounds"))
            if not ipa:
                continue
            lang = str(entry.get("lang_code") or entry.get("lang") or "?")
            found[key].append((lang, ipa))

    result: dict[str, tuple[str, str]] = {}
    for key, records in found.items():
        if not records:
            continue
        english = next((r for r in records if r[0] == "en"), None)
        best = english or records[0]
        result[key] = (best[1], best[0])
    return result