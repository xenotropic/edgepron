"""Shared data model for the edgepron pipeline."""

from __future__ import annotations

from dataclasses import dataclass

SOURCE_WIKIPEDIA = "wikipedia"
SOURCE_WIKTIONARY = "wiktionary"


@dataclass
class Entry:
    """One pronunciation dictionary entry.

    ``ipa`` / ``respell`` may be ``None`` when a form could not be determined.
    ``*_derived`` is ``True`` when the form was synthesized from the other form
    (and never presented as native), per the tiered-union design.
    """

    word: str
    ipa: str | None = None
    respell: str | None = None
    ipa_derived: bool = False
    respell_derived: bool = False
    # Provenance of a *derived* respelling: "canonical" (ticket-4 port) or
    # "heuristic" (legacy diaphonemes.ipa_to_respell fallback).
    respell_method: str | None = None
    source: str = SOURCE_WIKIPEDIA
    # ISO 639 source-language code when the entry comes from a non-English
    # Wiktionary section (e.g. "fr" for a French-only headword). None when the
    # language is English or not applicable.
    lang: str | None = None