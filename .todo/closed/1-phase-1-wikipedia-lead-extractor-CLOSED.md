# Phase 1 — Wikipedia lead-only pronunciation extractor

Implement tier 1 from `.todo/0-architecture.md` (§2 data tiers, §3 phase 1): a
Python CLI that builds a deterministic candidate list of English Wikipedia
titles, fetches each title's lead section, extracts `{{IPAc-en}}` and
`{{respell}}` templates, and writes the results to a `WITHOUT ROWID` SQLite
database plus a compressed TSV.

## Deliverables
- `edgepron.discovery` — vital-articles + top-pageviews discovery, deduplicated
  into a single candidate set.
- `edgepron.extraction` — batched `rvsection=0` fetcher, `mwparserfromhell`
  parser, and `IPAc-en` → IPA/respell normalization.
- `edgepron.storage` — SQLite writer (`WITHOUT ROWID`, low-memory PRAGMAs) and
  `.tsv.gz` writer.
- `config.yaml` + `python -m edgepron.cli` entry point.
- Unit tests for the parser and SQLite writer.

## Acceptance criteria
- `python -m edgepron.cli --vital-level 1 --popular-limit 1` produces a DB that
  contains known-good cases (Istanbul, Zeus, Yosemite) and correctly skips
  titles with no pronunciation template (e.g. Earth).
- Both IPA and respell are recorded when present; if a missing form is
  synthesized it is stored with `derived=true`.
- Tests pass.
==reply==
Okay, go ahead and do it. Make sure to have parameters for what the outputs are, compressed TSV, regular TSV, SQLite, all. Like, as a human testing, I'd rather just have unzipped TSVs when I'm doing small sets to test just to see what they look like.
The other thing I'm not sure about, but let's just leave it to your sense of what to do. The end result, we don't want IPA or respell, we just want a phonetic pronunciation from dictionary word, just two rows. I can see how we might want to have an intermediate that preserves information about source origin with two columns: one for IPA one for respell. But let's have an output possibility for condensing output down to just one lookup table of written text to phonetic text, where the IPA is all converted (and vice versa if cheap and easy, but IPA is not for me a desired output type -- yet).

==implemented==
Phase 1 implemented and tested (`python -m edgepron.cli`):

- `edgepron.discovery` — vital-articles list pages (incl. transcluded topic
  subpages) + top-pageviews REST, deduped. Flags: `--vital-level N`,
  `--popular-limit N`, `--popularity-timeframe`, `--min-pageviews`, `--titles`.
- `edgepron.extraction` — batched `rvsection=0` fetcher, `mwparserfromhell`
  parser, `IPAc-en`/`respell` normalization (diaphoneme code table extracted
  from `Module:IPAc-en/phonemes`), and lossy IPA<->respell synthesis
  (`*_derived` flags, never presented as native).
- `edgepron.storage` — WITHOUT ROWID SQLite, plain + gzip TSV, and a condensed
  two-column word<->phonetic lookup.
- Output flags per the reply: `--sqlite`, `--tsv` (uncompressed), `--tsv-gz`,
  `--condensed` (`.gz` suffix compresses), `--condensed-phonetic respell|ipa`.
- 23 unit tests pass (parser, diaphonemes, sqlite, tsv, discovery).

Acceptance-criteria correction: vital **level 1** is the 10 core articles
(Earth, Human, Life, ...) — none of them carries a lead pronunciation template,
so `--vital-level 1 --popular-limit 1` writes 0 rows by design (Earth is
correctly skipped). The known-good cases Istanbul/Zeus/Yosemite live at
levels 4-5 and are verified end-to-end via
`python -m edgepron.cli --vital-level 0 --titles Istanbul,Zeus,Yosemite,Earth ...`
plus parser unit tests. Derived vs native flags behave per spec (e.g. Zeus:
IPA native, respell `derived=true`).
