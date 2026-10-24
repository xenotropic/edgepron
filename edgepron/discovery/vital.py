"""Vital-articles discovery from the curated ``Wikipedia:Vital articles/Level N``
list pages (including their topic subpages for the larger levels, which the
index page links to with wikilinks rather than transcluding).
"""

from __future__ import annotations

import re
import time

_LINK_RE = re.compile(r"\[\[(?P<target>[^\[\]|#]+)(?:#[^\[\]]*)?(?:\|[^\]]*)?\]\]")
_TRANSCLUSION_RE = re.compile(r"\{\{\s*(Wikipedia:Vital articles[^}|]*)(?:\|[^}]*)?\}\}")
_BASE_NAMESPACES = {
    "file", "wikipedia", "category", "template", "help", "portal",
    "talk", "user", "draft", "module", "mediawiki", "special",
}
# Interwiki/interlanguage prefixes seen in the vital-article list chrome
# (e.g. ``[[m:List of articles every Wikipedia should have/Expanded]]``).
# These are not articles, so they must not be treated as mainspace.
_INTERWIKI_PREFIXES = {
    "m", "w", "meta", "mw", "commons", "simple", "species", "incubator",
    "wikibooks", "wikidata", "wikinews", "wikiquote", "wikisource",
    "wikiversity", "wikivoyage", "wiktionary",
}


def _normalize_title(title: str) -> str:
    return (title or "").replace("_", " ").strip()


def _is_mainspace(title: str) -> bool:
    """True if ``title`` is a plain article (no non-mainspace namespace)."""
    if not title:
        return False
    if title.startswith(":"):
        # ``[[:Category:...]]`` renders a link to a namespace page, not an article.
        return False
    if ":" not in title:
        return True
    prefix = title.split(":", 1)[0].strip().lower()
    if prefix in _BASE_NAMESPACES or prefix in _INTERWIKI_PREFIXES:
        return False
    return not (prefix.endswith(" talk") and prefix[:-len(" talk")] in _BASE_NAMESPACES)


def _is_sublist(target: str, level: int) -> bool:
    """True if ``target`` is a topic subpage of the given vital-articles level
    (e.g. ``Wikipedia:Vital articles/Level 4/People``) rather than the page
    chrome (``.../Level/header``, ``.../Level/Nav bar``) or another level."""
    return target.lower().startswith(f"wikipedia:vital articles/level {level}/")


def fetch_vital_titles(
    level: int,
    base_url: str,
    session,
    timeout: int = 30,
    max_retries: int = 3,
    rate_limit_sleep: float = 0.0,
) -> list[str]:
    """Return the article titles in the given vital-articles level.

    Each level is a strict superset of the previous one (Level 4 ⊇ Level 3 ⊇
    Level 2 ⊇ Level 1), so requesting a higher level already includes every
    lower level's titles.
    """
    root = f"Wikipedia:Vital articles/Level {level}"
    titles: list[str] = []
    visited: set[str] = set()
    _collect(root, level, base_url, session, timeout, max_retries, rate_limit_sleep, visited, titles)
    return list(dict.fromkeys(titles))


def _collect(page, level, base_url, session, timeout, max_retries, sleep, visited, titles):
    if page in visited:
        return
    visited.add(page)
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "formatversion": "2",
        "titles": page,
        "redirects": "1",
    }
    data = _get_json(session, base_url, params, timeout, max_retries)
    pages = (data.get("query", {}) or {}).get("pages", [])
    if not pages:
        return
    content = (pages[0].get("revisions") or [{}])[0].get("slots", {}).get("main", {}).get("content")
    if not content:
        return

    for match in _LINK_RE.finditer(content):
        target = _normalize_title(match.group("target"))
        if _is_mainspace(target):
            titles.append(target)
        elif _is_sublist(target, level):
            # Larger levels (4 and 5) are split across topic subpages that the
            # index page links to with ordinary wikilinks (``[[...:Level 4/People|People]]``).
            _collect(target, level, base_url, session, timeout, max_retries,
                     sleep, visited, titles)
            if sleep:
                time.sleep(sleep)

    for match in _TRANSCLUSION_RE.finditer(content):
        target = _normalize_title(match.group(1))
        # Follow only the list subpages (e.g. ``.../Level 4/People``), not the
        # chrome (``.../Level/header``, ``.../Level/Nav bar``).
        if _is_sublist(target, level):
            _collect(target, level, base_url, session, timeout, max_retries,
                     sleep, visited, titles)
            if sleep:
                time.sleep(sleep)


def _get_json(session, base_url, params, timeout, max_retries):
    for _attempt in range(max_retries + 1):
        response = session.get(base_url, params=params, timeout=timeout)
        if response.status_code == 429:
            time.sleep(float(response.headers.get("retry-after", 5)))
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError(f"vital discovery: giving up after {max_retries} retries")