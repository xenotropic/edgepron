"""Build dictionary entries from discovery titles via Wiktionary lookup."""

from __future__ import annotations

from collections.abc import Iterable

from edgepron.extraction import diaphonemes
from edgepron.model import SOURCE_WIKTIONARY, Entry
from edgepron.respell import ipa_to_canonical_respell
from edgepron.wiktionary.dump import scan
from edgepron.wiktionary.wordify import normalize_key, phrase_and_tokens


def _respell_from_ipa(ipa: str) -> tuple[str | None, str | None]:
    """Best-effort IPA -> respelling, mirroring ``cli._ipa_to_respell``.

    Returns ``(respell, method)`` where ``method`` is ``"canonical"`` or
    ``"heuristic"`` (or ``None`` when no respelling could be produced).
    """
    try:
        cleaned = ipa.replace("_", " ").split(",")[0].strip()
        respell = ipa_to_canonical_respell(cleaned)
        return (respell or None), ("canonical" if respell else None)
    except ValueError:
        respell = diaphonemes.ipa_to_respell(ipa)
        return (respell or None), ("heuristic" if respell else None)


def _append(entries: list[Entry], seen: set[str], word: str,
            ipa_map: dict[str, tuple[str, str]]) -> None:
    key = normalize_key(word)
    if key in seen or key not in ipa_map:
        return
    seen.add(key)
    ipa, lang = ipa_map[key]
    respell, method = _respell_from_ipa(ipa)
    entries.append(Entry(
        word=word, ipa=ipa, respell=respell,
        respell_derived=respell is not None, respell_method=method,
        source=SOURCE_WIKTIONARY, lang=lang,
    ))


def entries_from_wiktionary(
    titles: Iterable[str],
    dump_path: str,
    phrase_passthrough: bool = True,
) -> list[Entry]:
    """Resolve discoveries against a raw enwiktionary dump.

    With ``phrase_passthrough`` the full phrase is preferred and each title
    contributes one entry when it resolves; otherwise (or on a miss) its word
    tokens are emitted individually.
    """
    plan: list[list[str]] = []
    all_keys: set[str] = set()
    for title in titles:
        keys = phrase_and_tokens(title, phrase_passthrough)
        if keys:
            plan.append(keys)
            all_keys.update(keys)

    ipa_map = scan(dump_path, all_keys)

    entries: list[Entry] = []
    seen: set[str] = set()
    for keys in plan:
        start = 1 if phrase_passthrough else 0
        if phrase_passthrough and normalize_key(keys[0]) in ipa_map:
            _append(entries, seen, keys[0], ipa_map)
            continue
        for token in keys[start:]:
            _append(entries, seen, token, ipa_map)
    return entries