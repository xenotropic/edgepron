# lexphon

A Python utility that builds a pronunciation dictionary for text-to-speech
(TTS) engines — targeting the proper nouns, foreign words, foreign phrases,
abbreviations, and acronyms that TTS systems typically mispronounce.

lexphon extracts pronunciations from English Wikipedia (lead-section
`{{IPAc-en}}` and `{{respell}}` templates), and is planned to fall back to
Wiktionary, Wikidata lexemes, and grapheme-to-phoneme (G2P) conversion to fill
gaps. The result is an offline, read-optimized dictionary mapping each word or
phrase to its IPA and/or respelling.

> 🚧 **Work in progress.** The repository is being scaffolded. See
> [`.todo/`](.todo) for the phased architecture and open tickets.

## License

MIT © 2026 Joseph Morris — see [LICENSE](LICENSE).