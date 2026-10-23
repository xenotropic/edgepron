"""Vital-articles discovery from the curated ``Wikipedia:Vital articles/Level N``
list pages (including their transcluded topic subpages for the larger levels).
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


def _is_mainspace(title: str) -> bool:
    """True if ``title`` is a plain article (no non-mainspace namespace)."""
    if ":" not in title:
        return True
    prefix = title.split(":", 1)[0].strip().lower()
    if prefix in _BASE_NAMESPACES:
        return False
    return not (prefix.endswith(" talk") and prefix[:-len(" talk")] in _BASE_NAMESPACES)


def fetch_vital_titles(
    level: int,
    base_url: str,
    session,
    timeout: int = 30,
    max_retries: int = 3,
    rate_limit_sleep: float = 0.0,
) -> list[str]:
    """Return the article titles in the given vital-articles level."""
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
        target = match.group("target").strip()
        if not _is_mainspace(target):
            continue
        titles.append(target)

    for match in _TRANSCLUSION_RE.finditer(content):
        target = match.group(1).strip().replace("_", " ")
        # Follow only the list subpages (e.g. ``.../Level/4/People``), not the
        # chrome (``.../Level/header``, ``.../Level/Nav bar``).
        if target.lower().startswith(f"wikipedia:vital articles/level/{level}/"):
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