# Data sources

edgepron builds a pronunciation dictionary in two stages that draw from two
independent sources:

1. **Discovery** (`edgepron/discovery/`) — *what words to look up*, from English
   Wikipedia:
   - [Wikipedia:Vital articles](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles)
     (the canonical cultural-knowledge hierarchy), and
   - the [Wikimedia REST top-pageviews](https://wikimedia.org/api/rest_v1) metric
     for empirical popularity.
   These are fetched over the Wikipedia/`w`/Wikimedia REST APIs with a proper
   `User-Agent`, `maxlag=5`, and a configurable rate-limit sleep.

2. **Pronunciation** (`edgepron/wiktionary/`) — *how to say those words*, from
   English Wiktionary via the **kaikki.org** machine-readable extraction.

## Wiktionary dump (pronunciation source)

Pronunciations come from a **single, downloaded, offline JSONL dump** of the
English Wiktionary (enwiktionary). The dump is produced by the
[wiktextract](https://github.com/tatuylonen/wiktextract) project and hosted by
[kaikki.org](https://kaikki.org/dictionary/).

- **URL (recommended file, all languages):**
  `https://kaikki.org/dictionary/raw-wiktextract-data.jsonl.gz`
- **Size:** ~2.9 GB compressed / ~24.8 GB uncompressed (JSONL, one JSON object
  per line).
- **Scope:** the full English-Wiktionary edition, which describes words of
  **hundreds of languages** (not just English), with glosses in English. This is
  why foreign-only headwords such as *miserables* (French) resolve with their
  own-language IPA.
- **Date pinned at time of writing:** extracted 2026-10-21 from the enwiktionary
  dump dated 2026-10-01. The file is regenerated weekly; re-download for a newer
  snapshot.
- **Note:** the *English-only* post-processed file
  (`kaikki.org/dictionary/English/…`, ~3.2 GB) is marked DEPRECATED and is not
  used. The raw all-languages extract above is the durable source.

### Download

```bash
# 2.9 GB — keep it under the gitignored resources/ directory (never committed)
mkdir -p resources
curl -L -o resources/enwiktionary-20261001-raw.jsonl.gz \
  https://kaikki.org/dictionary/raw-wiktextract-data.jsonl.gz
```

### Run the pipeline

```bash
python -m edgepron.cli --vital-level 4 --popular-limit 500 \
  --wiktionary-dump resources/enwiktionary-20261001-raw.jsonl.gz \
  --condensed dist/lookup.tsv
```

The dump is streamed once per run (memory-safe; only the requested candidate
words are retained), and the resulting database/TSV is the deployable artifact —
so the dump is only needed on the machine that *builds* the dictionary, never on
the edge.

### Schema (relevant fields)

Each JSONL line is one `(word, language, part-of-speech, etymology)` entry. The
fields edgepron reads are:

| Field | Meaning |
|---|---|
| `word` | headword (e.g. `"Al Pacino"`, `"miserables"`) |
| `lang` | human language name (e.g. `"English"`, `"French"`) |
| `lang_code` | ISO 639 code (e.g. `"en"`, `"fr"`) |
| `pos` | part of speech (`"noun"`, `"proper noun"`, …) |
| `sounds` | list of `{ipa, tags, audio, …}` — `ipa` may be `null` or wrapped in `/…/` or `[…]` |

### Lookup policy

For each candidate word:

1. Prefer the entry with `lang_code == "en"`.
2. If there is no English entry, fall back to the first non-English entry and
   record its language in the output `lang` column (so downstream knows that
   e.g. *miserables* is French).
3. Take the first non-empty `sounds[].ipa` and strip the `/`/`[]` delimiters.
4. Convert that IPA to a pronunciation respelling with the existing
   `edgepron.respell` converter.

When the discovery title is a multi-word phrase, the whole phrase is looked up
first and preferred if present; otherwise the title is tokenized into words and
each word is looked up individually (`--no-phrase-passthrough` disables the
phrase fallback).

## Licensing & attribution

- **Wiktionary content** is [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)
  and [GFDL](https://www.gnu.org/copyleft/fdl.html). edgepron reads short IPA
  transcription fields (facts), but if you redistribute the extracted data
  please attribute Wiktionary per those terms.
- **wiktextract / kaikki.org** — please cite Tatu Ylonen: *Wiktextract:
  Wiktionary as Machine-Readable Structured Data*, LREC 2022, and link to
  <https://kaikki.org>.
- edgepron itself is [MIT](LICENSE).

## Rebuilding from scratch (for a future self / agent)

1. `git checkout wiktionary-pipeline` (or `main` once merged).
2. `pip install -r requirements.txt`.
3. Download the dump (see above) — it is >2 GB and must **not** be committed
   (`resources/` is in `.gitignore`).
4. Run the CLI with `--wiktionary-dump` pointing at the downloaded file and the
   desired `--vital-level` / `--popular-limit` / `--titles` discovery flags, plus
   any of the `--sqlite` / `--tsv` / `--condensed` outputs.