"""Environment-driven post-processing of the emitted phonetic string.

The two-column lookups (condensed TSV / sqlite) are the TTS-facing artifacts,
so they can be cleaned independently of the raw ``Entry``/full-TSV forms.
"""

from __future__ import annotations

import os


def _mode(name: str, default: str) -> str:
    return os.environ.get(name, default).strip().lower()


# Parenthesized segments mark optional (dialect/region) sounds. ``strip`` drops
# the parentheses but keeps the content (sounds better pronounced than skipped);
# ``keep`` leaves "(...)" as-is.
PARENS = _mode("EDGEPRON_PARENS", "strip")

# Dashes/hyphens separate respelling syllables. ``remove`` (default) drops them;
# ``keep`` leaves them.
DASHES = _mode("EDGEPRON_DASHES", "remove")

# Spaces: ``remove`` (default) drops syllable-separator spaces from a single
# word's respelling (word-boundary spaces in multi-word phrases are kept);
# ``keep`` leaves all spaces.
SPACES = _mode("EDGEPRON_SPACES", "remove")


def clean_phonetic(text: str | None, multiword: bool = False) -> str:
    """Apply the env-driven cleanup to a pronunciation string.

    ``multiword`` tells the cleaner the headword is a multi-word phrase, so
    spaces between its words are real word boundaries rather than syllable
    separators.
    """
    if not text:
        return ""
    out = text
    if DASHES == "remove":
        out = out.replace("-", "")
    if PARENS == "strip":
        out = out.replace("(", "").replace(")", "")
    # Periods in respellings are accent/syllable markers, never wanted in a
    # TTS string (ticket 14).
    out = out.replace(".", "")
    if SPACES == "remove":
        if multiword:
            out = " ".join(out.split())
        else:
            out = out.replace(" ", "")
    return out


__all__ = ["clean_phonetic", "PARENS", "DASHES", "SPACES"]