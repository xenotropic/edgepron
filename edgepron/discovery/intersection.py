"""Deduplicate candidate title lists into one ordered set."""

from __future__ import annotations


def normalize_title(title: str) -> str:
    return (title or "").replace("_", " ").strip()


def dedupe(*lists: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for lst in lists:
        for title in lst:
            title = normalize_title(title)
            if not title or title in seen:
                continue
            seen.add(title)
            out.append(title)
    return out