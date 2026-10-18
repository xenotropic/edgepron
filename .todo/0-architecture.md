# Lexphon — Phased Architecture

> Living design document. The original Gemini-generated draft this supersedes
> is preserved verbatim in git history (commit `a05b24f`, the initial import).
> This version restates it as a phased plan: full detail in phase 1, tapering
> detail afterward.

## 1. Goal

Build an **offline pronunciation dictionary** for text-to-speech (TTS) engines.
The dictionary targets exactly the tokens TTS gets wrong: proper nouns, foreign
words, foreign phrases, abbreviations, and acronyms. Each entry records the
pronunciation as **IPA**, **respell**, or both — whichever the source provides
natively.

## 2. Data tiers (the tiered union)

Sources are consulted in order of precision. Coverage grows as we move down the
list, so each entry records its provenance.

| Tier | Source | Role | Precision |
|------|--------|------|-----------|
| 1 | Wikipedia (lead-only) | Primary | Highest — human-curated IPAc-en/respell |
| 2 | Wiktionary | Gap-fill | High — human-curated IPA/respell |
| 3 | Wikidata lexemes | Fallback | Medium — structured IPA forms |
| 4 | G2P (grapheme-to-phoneme) | Last resort | Lowest — generated |

**IPA ↔ respell is lossy in both directions**, so neither is authoritative over
the other. Both are extracted natively wherever present. When a source yields
only one form, a synthesized second form is recorded with `derived=true` and
never presented as native.

## 3. Phase 1 — Wikipedia lead-only extractor

Phase 1 delivers the precision tier only: deterministic, top-down discovery over
English Wikipedia, lead-section extraction of the two pronunciation templates,
and a read-optimized SQLite + compressed-TSV output.

### 3.1 Discovery (deterministic, not random)

Candidates are the deduplicated union of two lists:

1. **Vital Articles hierarchy** — canonical cultural knowledge
   (`Category:All_Wikipedia_level_X_vital_articles`).
2. **Wikimedia REST top pageviews** — empirical popularity
   (`/metrics/pageviews/top/en.wikipedia/all-access/...`).

Configurable depth/limits control scale (vital level 4 ≈ 10k articles; popular
limit 1–10000; minimum monthly pageviews to filter bot spikes).

### 3.2 Extraction

1. **Fetch** the lead section only (`action=query&rvsection=0`), batched
   (`api_chunk_size`) with a polite rate-limit delay and a descriptive
   User-Agent. Wikipedia's public APIs need **no key**.
2. **Parse** wikitext with `mwparserfromhell`; locate `{{IPAc-en}}` and
   `{{respell}}` templates.
   - Titles with neither template are discarded. E.g. **Earth** has no
     pronunciation template, while **Istanbul**, **Zeus**, and **Yosemite** do.
     That coverage gap is exactly what later tiers fill.
3. **Normalize** into canonical IPA / respell syllables (strip disambiguation
   parentheses; keep multiword entities).

### 3.3 Storage

- **SQLite** with `WITHOUT ROWID` and low-memory PRAGMAs (journal OFF,
  synchronous OFF, cache_size -2000, temp_store MEMORY).
- **Compressed TSV** (`.tsv.gz`) mirror.

### 3.4 Package layout

```
lexphon/
├── cli.py               # python -m lexphon.cli
├── config.yaml          # all tunables (depth, limits, API, storage)
├── discovery/
│   ├── popular.py       # top-pageviews discovery
│   ├── vital.py         # vital-articles discovery
│   └── intersection.py  # dedupe candidate set
├── extraction/
│   ├── fetcher.py       # batched rvsection=0 fetcher
│   ├── parser.py        # mwparserfromhell IPAc-en/respell parser
│   └── diaphonemes.py   # IPAc-en → canonical IPA/respell
└── storage/
    ├── sqlite_writer.py
    └── tsv_writer.py
```

### 3.5 CLI

```bash
# smoke test: 1 vital + 1 popular article
python -m lexphon.cli --mode api --vital-level 1 --popular-limit 1 --sqlite dist/test_pronunc.db

# production: vital level 4 + top 5000 viewed
python -m lexphon.cli --mode api --vital-level 4 --popular-limit 5000 --popularity-timeframe last-month --sqlite dist/production_pronunc.db
```

(Phase 1 also permits a `--mode toolforge` path hitting MariaDB replicas / a
Toolforge batch job; the public-API mode is the default for local dev.)

## 4. Phase 2 — Wiktionary gap-fill (brief)

- Re-run the phase-1 candidate set against Wiktionary; harvest IPA/respell for
  titles Wikipedia lacked a pronunciation for.
- Add `source` / `tier` columns; distinguish Wikipedia-native vs
  Wiktionary-supplied entries.

## 5. Phase 3 — Wikidata lexemes (brief)

- Query Wikidata lexeme forms for IPA.
- Reconcile Wikipedia / Wiktionary / Wikidata forms for the same concept.

## 6. Phase 4 — G2P fallback (brief)

- Grapheme-to-phoneme model for anything still without a native form.
- Always flagged `derived=true`.

## 7. Non-goals / open questions (brief)

- No lossless IPA↔respell round-trip is required; derived forms are flagged.
- Toolforge deployment, scheduling, and download cadence are finalized later.
- Wiktionary / Wikidata / G2P schemas above are intentional stubs.
