# Phase 1 — Wikipedia lead-only pronunciation extractor

Implement tier 1 from `.todo/0-architecture.md` (§2 data tiers, §3 phase 1): a
Python CLI that builds a deterministic candidate list of English Wikipedia
titles, fetches each title's lead section, extracts `{{IPAc-en}}` and
`{{respell}}` templates, and writes the results to a `WITHOUT ROWID` SQLite
database plus a compressed TSV.

## Deliverables
- `lexphon.discovery` — vital-articles + top-pageviews discovery, deduplicated
  into a single candidate set.
- `lexphon.extraction` — batched `rvsection=0` fetcher, `mwparserfromhell`
  parser, and `IPAc-en` → IPA/respell normalization.
- `lexphon.storage` — SQLite writer (`WITHOUT ROWID`, low-memory PRAGMAs) and
  `.tsv.gz` writer.
- `config.yaml` + `python -m lexphon.cli` entry point.
- Unit tests for the parser and SQLite writer.

## Acceptance criteria
- `python -m lexphon.cli --vital-level 1 --popular-limit 1` produces a DB that
  contains known-good cases (Istanbul, Zeus, Yosemite) and correctly skips
  titles with no pronunciation template (e.g. Earth).
- Both IPA and respell are recorded when present; if a missing form is
  synthesized it is stored with `derived=true`.
- Tests pass.