"""Wiktionary pronunciation provider (offline raw-dump lookup)."""

from edgepron.wiktionary.build import entries_from_wiktionary
from edgepron.wiktionary.dump import scan
from edgepron.wiktionary.wordify import normalize_key, phrase_and_tokens

__all__ = ["entries_from_wiktionary", "scan", "normalize_key", "phrase_and_tokens"]