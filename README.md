# edgepron

A Python utility that builds a pronunciation dictionary for text-to-speech
(TTS) engines — targeting the proper nouns, foreign words, foreign phrases,
abbreviations, and acronyms that TTS systems typically mispronounce.

edgepron extracts pronunciations from English Wikipedia (lead-section
`{{IPAc-en}}` and `{{respell}}` templates), and is planned to fall back to
Wiktionary, Wikidata lexemes, and grapheme-to-phoneme (G2P) conversion to fill
gaps. The result is an offline, read-optimized dictionary mapping each word or
phrase to its IPA and/or respelling.

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
```

Output formats (all opt-in):

- `--sqlite PATH` — full `WITHOUT ROWID` SQLite
  (`word, ipa, respell, ipa_derived, respell_derived, source`).
- `--tsv PATH` / `--tsv-gz PATH` — the same six columns, plain or gzip.
- `--condensed PATH` — two-column `word <TAB> phonetic` lookup (respell by
  default; `--condensed-phonetic ipa` to switch; `.gz` suffix compresses).

## License

MIT © 2026 Joseph Morris — see [LICENSE](LICENSE).