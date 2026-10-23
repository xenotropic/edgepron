"""Wikitext -> pronunciation extraction via ``mwparserfromhell``."""

from __future__ import annotations

from dataclasses import dataclass

import mwparserfromhell

from edgepron.extraction import diaphonemes


@dataclass
class Extracted:
    """Native forms straight from the lead section (either may be None)."""

    ipa: str | None = None
    respell: str | None = None


def extract_pronunciations(wikitext: str) -> Extracted:
    """Return the first ``{{IPAc-en}}`` and ``{{respell}}`` found in ``wikitext``."""
    code = mwparserfromhell.parse(wikitext)
    ipa: str | None = None
    respell: str | None = None
    for template in code.filter_templates(recursive=True):
        name = template.name.strip().lower()
        if name == "ipac-en":
            value = diaphonemes.normalize_ipac_en(template.params)
            if value and ipa is None:
                ipa = value
        elif name == "respell":
            value = diaphonemes.normalize_respell(template.params)
            if value and respell is None:
                respell = value
    return Extracted(ipa=ipa, respell=respell)