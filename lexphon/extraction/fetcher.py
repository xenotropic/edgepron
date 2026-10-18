"""Batched lead-section fetcher (``action=query``, ``rvsection=0``)."""

from __future__ import annotations

import time
from collections.abc import Iterable
from typing import Iterator


class FetchError(RuntimeError):
    """Raised when the API cannot be reached after retries."""


def _norm(title: str) -> str:
    return (title or "").replace("_", " ").strip()


def _get_json(session, url: str, params, timeout: int, max_retries: int) -> dict:
    for _attempt in range(max_retries + 1):
        response = session.get(url, params=params, timeout=timeout)
        if response.status_code == 429:
            time.sleep(float(response.headers.get("retry-after", 5)))
            continue
        response.raise_for_status()
        return response.json()
    raise FetchError(f"giving up after {max_retries} retries on {url}")


def fetch_leads(
    titles: Iterable[str],
    base_url: str,
    session,
    chunk_size: int = 50,
    rate_limit_sleep: float = 0.0,
    timeout: int = 30,
    max_retries: int = 3,
) -> Iterator[tuple[str, str]]:
    """Yield ``(requested_title, lead_wikitext)`` for each fetchable title.

    Redirects are followed (``redirects=1``) but keys stay on the *requested*
    title so a candidate like "Yosemite" is not silently renamed "Yosemite
    National Park".  Titles that don't exist are skipped.
    """
    titles = list(dict.fromkeys(titles))
    for start in range(0, len(titles), chunk_size):
        chunk = titles[start : start + chunk_size]
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "rvsection": "0",
            "rvslots": "main",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
            "maxlag": "5",
            "titles": "|".join(chunk),
        }
        data = _get_json(session, base_url, params, timeout, max_retries)
        query = data.get("query", {}) or {}
        requested = {_norm(t): t for t in chunk}
        redirect_map = {_norm(r.get("from", "")): _norm(r.get("to", "")) for r in query.get("redirects", [])}

        for page in query.get("pages", []):
            if page.get("missing") or page.get("invalid"):
                continue
            resolved = _norm(page.get("title", ""))
            title = requested.get(resolved)
            if title is None:
                for source in requested:
                    if redirect_map.get(source) == resolved:
                        title = requested[source]
                        break
            if title is None:
                title = page.get("title", "")
            content = (page.get("revisions") or [{}])[0].get("slots", {}).get("main", {}).get("content")
            if content is None:
                continue
            yield title, content

        if rate_limit_sleep:
            time.sleep(rate_limit_sleep)