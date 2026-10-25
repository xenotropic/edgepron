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


def clean_phonetic(text: str | None) -> str:
    """Apply the env-driven cleanup to a pronunciation string."""
    if not text:
        return ""
    out = text
    if DASHES == "remove":
        out = out.replace("-", "")
    if PARENS == "strip":
        out = out.replace("(", "").replace(")", "")
    return out


__all__ = ["clean_phonetic", "PARENS", "DASHES"]