"""Shared data model for the edgepron pipeline."""

from __future__ import annotations

from dataclasses import dataclass

SOURCE_WIKIPEDIA = "wikipedia"


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
    source: str = SOURCE_WIKIPEDIA