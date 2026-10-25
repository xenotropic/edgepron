# edgepron

A Python utility that builds a pronunciation dictionary for text-to-speech
(TTS) engines — targeting the proper nouns, foreign words, foreign phrases,
abbreviations, and acronyms that TTS systems typically mispronounce.

edgepron **discovers** candidate terms from English Wikipedia (the Vital Articles
hierarchy + top pageviews), then **looks up their pronunciations** in an offline
English Wiktionary dump (wiktextract via kaikki.org), converting IPA to a
pronunciation respelling. Direct lead-section template extraction from Wikipedia
(`{{IPAc-en}}` / `{{respell}}`) remains available as the default engine; a
Wikidata/G2P fallback is planned. The result is an offline, read-optimized
dictionary mapping each word or phrase to its IPA and/or respelling. See
[`docs/data-sources.md`](docs/data-sources.md) for how to obtain the Wiktionary
dump and reconstruct the environment.

> 🚧 **Work in progress.** The repository is being scaffolded. See
> [`.todo/`](.todo) for the phased architecture and open tickets.

## Usage

```bash
# install dependencies
pip install -r requirements.txt

# smoke test: 1 vital + 1 popular article (level-1 core articles carry no
# lead pronunciation, so this writes 0 rows but exercises the full pipeline)
python -m edgepron.cli --vital-level 1 --popular-limit 1 --sqlite dist/test_pronunc.db

# small, human-inspectable set (known-good cases; plain TSV for eyeballing)
python -m edgepron.cli --vital-level 0 --titles "Istanbul,Zeus,Yosemite,Earth" \
  --sqlite dist/test.db --tsv dist/test.tsv --tsv-gz dist/test.tsv.gz \
  --condensed dist/test.lookup.tsv

# production scale: vital level 4 + top 5000 viewed (last month)
python -m edgepron.cli --vital-level 4 --popular-limit 5000 \
  --popularity-timeframe last-month --sqlite dist/production_pronunc.db

# Wiktionary pronunciation source (offline, recommended for clean IPA):
# 1. download the raw dump once (see docs/data-sources.md; ~2.9 GB, gitignored)
# 2. resolve discoveries against it instead of Wikipedia lead templates
python -m edgepron.cli --vital-level 4 --popular-limit 500 \
  --wiktionary-dump resources/enwiktionary-20261001-raw.jsonl.gz \
  --condensed dist/lookup.tsv
```

Output formats (all opt-in):

- `--sqlite PATH` — full `WITHOUT ROWID` SQLite
  (`word, ipa, respell, ipa_derived, respell_derived, respell_method, source, lang`).
- `--sqlite-minimal PATH` — deployment two-column `word -> phonetic` SQLite
  (keys lowercased, accents preserved; respell by default, `--condensed-phonetic
  ipa` to switch).
- `--tsv PATH` / `--tsv-gz PATH` — the same seven columns, plain or gzip.
- `--condensed PATH` — two-column `word <TAB> phonetic` lookup (respell by
  default; `--condensed-phonetic ipa` to switch; `.gz` suffix compresses).

With no output flag the two-column `word <TAB> respell` lookup is written to
stdout **without** a header (data only), which is the default for quick testing.
`respell_method` records how a derived respelling was produced: `canonical`
(ticket-4 converter) or `heuristic` (legacy fallback).

## License

MIT © 2026 Joseph Morris — see [LICENSE](LICENSE).