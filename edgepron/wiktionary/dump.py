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


# Wiktionary proper-noun part-of-speech labels (raw wiktextract uses "name" for
# people/places/works; keep a few aliases for safety).
NAME_POS = frozenset({
    "name", "proper noun", "proper name", "given name", "surname",
    "family name", "toponym", "patronymic",
})


def _capitalized(word: str) -> bool:
    return bool(word and word[0].isupper())


def scan(gz_path: str, want: set[str] | list[str]) -> dict[str, tuple[str, str]]:
    """Stream ``gz_path`` once and return ``{normalized_key: (ipa, lang_code)}``.

    Only keys present in ``want`` are retained, so the 24.8 GB uncompressed
    stream is never held in memory. Selection policy (tickets 11 + 15):

    - single-character keys are dropped;
    - an English proper name (capitalized headword, ``pos`` in ``NAME_POS``) is
      preferred;
    - an English word with no proper-name sense is dropped (it is a common word
      — do NOT fall back to a same-spelling foreign entry, e.g. "ballet");
    - a word with no English entry at all but a non-English entry is kept as
      foreign vocabulary (tagged with its language code).

    Ambiguous homographs that are both a common word *and* a name (*ginger*,
    *Bill*, *Ball*, *saint*) are kept for now; culling them cleanly needs a
    common-words frequency list — see ticket 16.
    """
    wanted = {w for w in (normalize_key(x) for x in want) if len(w) > 1}
    state: dict[str, dict] = {
        w: {"proper": None, "en_common": False, "foreign": None} for w in wanted
    }

    opening = gzip.open if gz_path.endswith(".gz") else open
    with opening(gz_path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            word = str(entry.get("word") or "")
            key = normalize_key(word)
            if key not in wanted:
                continue
            ipa = first_ipa(entry.get("sounds"))
            if not ipa:
                continue
            lang = str(entry.get("lang_code") or entry.get("lang") or "?")
            pos = str(entry.get("pos") or "").strip().lower()
            rec = state[key]
            if lang == "en":
                if _capitalized(word) and pos in NAME_POS and rec["proper"] is None:
                    rec["proper"] = ipa
                elif pos and pos not in NAME_POS:
                    rec["en_common"] = True
            elif rec["foreign"] is None:
                rec["foreign"] = (ipa, lang)

    result: dict[str, tuple[str, str]] = {}
    for key, rec in state.items():
        if rec["proper"] is not None:
            result[key] = (rec["proper"], "en")
        elif rec["en_common"]:
            continue  # English common word; don't fall back to a foreign twin
        elif rec["foreign"] is not None:
            result[key] = rec["foreign"]
    return result