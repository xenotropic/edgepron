"""Normalize English Wikipedia pronunciation templates.

Sources:
- ``Module:IPAc-en/phonemes`` — diaphoneme code -> IPA label table (kept
  machine-generated in ``edgepron.extraction._ipac_table``).
- ``Help:Pronunciation respelling key`` — respell <-> IPA correspondence.

``{{IPAc-en}}`` spells a word as diaphoneme codes (optionally X-SAMPA shorthand
— ``{`` -> æ, ``@`` -> ə, ``'`` -> ˈ, ``,`` -> ˌ, ...); concatenating each code's
IPA label yields the transcription. ``{{respell}}`` spells syllables separated
by ``|``; Wikipedia renders hyphens between them and marks stress with capitals.
"""

from __future__ import annotations

import re

from edgepron.extraction._ipac_table import IPAC_EN_TO_IPA  # noqa: F401

# The first positional argument of {{IPAc-en}} can be a pronunciation *label*
# (``lang``, ``us``, ``also``, ...) rather than a phoneme.
LABEL_CODES = frozenset({
    "lang", "pron", "local", "ipa", "also",
    "uk", "us", "uklang", "uslang",
    "ukalso", "usalso", "alsouk", "alsous",
})

# Table labels that are separators/prosodic breaks, not sounds — they must never
# leak into a canonical IPA string.
NON_PHONEMIC = frozenset({"&#124;", "‖", "#", " ", "(", ")", "-", "."})

# IPA diaphonemes able to carry a syllable nucleus (for syllabification when
# synthesizing a respelling from IPA).
_NUCLEI = frozenset({
    "æ", "ɑː", "ɑːr", "ær", "ɒ", "ɒr", "ɒ̃", "æ̃",
    "eɪ", "ɛ", "ɛr", "ɛər", "ɛəˈr", "ɛəˌr",
    "iː", "i", "ɪ", "ɪr", "ɪər", "ɪəˈr", "ɪəˌr",
    "oʊ", "əʊ", "əu", "ɔː", "ɔːr", "ɔɪ", "ɔɪər",
    "uː", "u", "ʊ", "ʊr", "ʊər", "ʊəˈr", "ʊəˌr",
    "aɪ", "aɪər", "aʊ", "aʊər", "ʌ", "ʌr",
    "ɜː", "ɜːr", "ə", "ər", "əl", "ən", "əm", "juː", "jʊər",
})

_STRESS = {"ˈ", "ˌ"}

# IPA -> pronunciation respelling (Help:Pronunciation respelling key), extended
# with the IPAc-en yod-cluster / r-colored diaphonemes.
IPA_TO_RESPELL = {
    # vowels / nuclei
    "æ": "a", "ɑː": "ah", "ɑːr": "ar", "ær": "arr",
    "ɛər": "air", "ɛəˈr": "air", "ɛəˌr": "air",
    "ɔː": "aw", "ɔːr": "or", "ɒ": "o", "ɒr": "orr",
    "eɪ": "ay", "ɛ": "e", "ɛr": "err",
    "iː": "ee", "i": "i", "ɪ": "i", "ɪr": "irr",
    "ɪər": "eer", "ɪəˈr": "eer", "ɪəˌr": "eer",
    "oʊ": "oh", "əʊ": "oh", "əu": "oh",
    "ɔɪ": "oy", "ɔɪər": "oir",
    "uː": "oo", "u": "u", "ʊ": "uu", "ʊr": "uurr",
    "ʊər": "oor", "ʊəˈr": "oor", "ʊəˌr": "oor",
    "aɪ": "eye", "aɪər": "ire",
    "aʊ": "ow", "aʊər": "our",
    "ʌ": "u", "ʌr": "urr",
    "ɜː": "ur", "ɜːr": "ur",
    "ə": "ə", "ər": "ər", "əl": "əl", "ən": "ən", "əm": "əm",
    "juː": "ew", "jʊər": "ure",
    "ɒ̃": "on", "æ̃": "an",
    # consonants
    "b": "b", "d": "d", "dj": "dy", "dʒ": "j", "ð": "dh",
    "f": "f", "ɡ": "g", "h": "h", "hw": "wh", "j": "y",
    "k": "k", "l": "l", "lj": "ly", "m": "m", "n": "n",
    "nj": "ny", "ŋ": "ng", "p": "p", "r": "r", "s": "s",
    "sj": "sy", "ʃ": "sh", "t": "t", "tj": "ty", "tʃ": "ch",
    "θ": "th", "θj": "thy", "v": "v", "w": "w", "x": "kh",
    "z": "z", "zj": "zy", "ʒ": "zh", "ʔ": "",
}

# respelling -> IPA. Inverse of the key above (first-wins for the few genuinely
# ambiguous pairs); only used for the "cheap and easy" respell -> IPA direction.
RESPELL_TO_IPA = {
    "a": "æ", "ah": "ɑː", "ar": "ɑːr", "arr": "ær",
    "air": "ɛər", "aw": "ɔː", "or": "ɔːr", "o": "ɒ", "orr": "ɒr",
    "ay": "eɪ", "e": "ɛ", "err": "ɛr",
    "ee": "iː", "i": "ɪ", "irr": "ɪr",
    "eer": "ɪər", "oh": "oʊ", "oy": "ɔɪ", "oir": "ɔɪər",
    "oo": "uː", "uu": "ʊ", "uurr": "ʊr", "oor": "ʊər",
    "eye": "aɪ", "ire": "aɪər", "ow": "aʊ", "our": "aʊər",
    "u": "ʌ", "urr": "ʌr", "ur": "ɜːr",
    "ə": "ə", "ər": "ər", "əl": "əl", "ən": "ən", "əm": "əm",
    "ew": "juː", "ure": "jʊər", "ih": "ɪ", "eh": "ɛ",
    "b": "b", "d": "d", "dy": "dj", "j": "dʒ", "dh": "ð",
    "f": "f", "g": "ɡ", "h": "h", "wh": "hw", "y": "j",
    "k": "k", "l": "l", "ly": "lj", "m": "m", "n": "n",
    "ny": "nj", "ng": "ŋ", "p": "p", "r": "r", "s": "s",
    "sy": "sj", "sh": "ʃ", "t": "t", "ty": "tj", "ch": "tʃ",
    "th": "θ", "thy": "θj", "v": "v", "w": "w", "kh": "x",
    "z": "z", "zy": "zj", "zh": "ʒ",
}

def _strip_comment(value: str) -> str:
    """Remove an inline HTML comment (``<!-- ... -->``) glued onto a template
    parameter value and trim surrounding whitespace."""
    return re.sub(r"<!--.*?-->", "", value).strip()


def normalize_ipac_en(params) -> str | None:
    """Turn ``{{IPAc-en}}`` template params into a canonical IPA string."""
    out: list[str] = []
    for p in params:
        name = str(getattr(p, "name", "")).strip()
        if name and not name.isdigit():
            continue  # named params (audio=..., lang=...)
        value = _strip_comment(str(getattr(p, "value", "")).strip())
        if not value:
            continue
        if value.lower() in LABEL_CODES:
            continue
        label = IPAC_EN_TO_IPA.get(value, value)
        if label in NON_PHONEMIC:
            continue
        out.append(label)
    ipa = "".join(out).strip()
    return ipa or None


def normalize_respell(params) -> str | None:
    """Turn ``{{respell}}`` template params into ``SYL-la-ble`` form.

    A comma introduces an alternate pronunciation; only the first variant is
    kept for a single canonical pairing.
    """
    syllables: list[str] = []
    for p in params:
        name = str(getattr(p, "name", "")).strip()
        if name and not name.isdigit():
            continue
        value = _strip_comment(str(getattr(p, "value", "")).strip())
        if value:
            syllables.append(value)
    if not syllables:
        return None
    first = "-".join(syllables).split(",")[0].rstrip("-_ \t").strip()
    return first or None


def _tokenize_ipa(ipa: str) -> list[str]:
    """Longest-match tokenization of an IPA string into diaphonemes."""
    keys = sorted((k for k in IPA_TO_RESPELL if len(k) > 1), key=len, reverse=True)
    tokens: list[str] = []
    i = 0
    while i < len(ipa):
        ch = ipa[i]
        if ch in _STRESS:
            tokens.append(ch)
            i += 1
            continue
        for key in keys:
            if ipa.startswith(key, i):
                tokens.append(key)
                i += len(key)
                break
        else:
            tokens.append(ch)
            i += 1
    return tokens


def ipa_to_respell(ipa: str) -> str:
    """Best-effort, *lossy* IPA -> respelling (flagged ``derived`` upstream).

    Syllables are delimited by hyphens and stressed syllables are uppercased,
    matching Wikipedia's convention. Syllabification uses a maximal-onset
    heuristic, so multi-syllable output is approximate — native respellings are
    always preferred when available.
    """
    if not ipa:
        return ""
    syllables: list[tuple[str, bool]] = []
    onset: list[str] = []
    stressed = False
    for token in _tokenize_ipa(ipa):
        if token in _STRESS:
            stressed = True
            continue
        resp = IPA_TO_RESPELL.get(token, token)
        if token in _NUCLEI:
            syllables.append(("".join(onset) + resp, stressed))
            onset = []
            stressed = False
        else:
            onset.append(resp)
    if not syllables:
        return "".join(onset)
    if onset:  # trailing consonants -> coda of the final syllable
        text, flag = syllables[-1]
        syllables[-1] = (text + "".join(onset), flag)
    return "-".join(text.upper() if flag else text for text, flag in syllables)


def respell_to_ipa(respell: str) -> str:
    """Best-effort respelling -> IPA (stressed syllables get a leading ˈ)."""
    if not respell:
        return ""
    keys = sorted(RESPELL_TO_IPA, key=len, reverse=True)
    out: list[str] = []
    for syllable in respell.split("-"):
        if not syllable:
            continue
        if syllable[0].isupper():
            out.append("ˈ")
        token = syllable.lower()
        i = 0
        while i < len(token):
            for key in keys:
                if token.startswith(key, i):
                    out.append(RESPELL_TO_IPA[key])
                    i += len(key)
                    break
            else:
                out.append(token[i])
                i += 1
    return "".join(out)