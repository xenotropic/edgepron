"""Command-line entry point: ``python -m edgepron.cli``.

Builds a pronunciation dictionary from English Wikipedia lead sections.
All output types are opt-in via flags:

- ``--sqlite PATH``         full ``WITHOUT ROWID`` SQLite DB
- ``--sqlite-minimal PATH`` two-column ``word -> phonetic`` SQLite lookup
- ``--tsv PATH``            full seven-column TSV (uncompressed)
- ``--tsv-gz PATH``         full seven-column TSV (gzip-compressed)
- ``--condensed PATH``      two-column ``word <TAB> phonetic`` lookup
                            (``.gz`` suffix compresses)

With no output flag, the two-column ``word <TAB> respell`` lookup (respell by
default; ``--condensed-phonetic ipa`` switches) is written to stdout without a
header.

Discovery depth is controlled with ``--vital-level``, ``--popular-limit`` and
``--titles``. Set a limit/level to ``0`` to disable that source.
"""

from __future__ import annotations

import argparse
import os
import sys

import requests

from edgepron.config import load_config
from edgepron.discovery import dedupe, fetch_top_pageviews, fetch_vital_titles
from edgepron.extraction import diaphonemes, extract_pronunciations, fetch_leads
from edgepron.model import Entry
from edgepron.respell import ipa_to_canonical_respell
from edgepron.storage import write_condensed, write_sqlite, write_sqlite_lookup, write_tsv
from edgepron.wiktionary import entries_from_wiktionary


def _default_config_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m edgepron.cli",
        description="Build a pronunciation dictionary from English Wikipedia lead sections.",
    )
    parser.add_argument("--config", help="path to config.yaml")
    parser.add_argument("--mode", choices=["api", "toolforge"], default=None,
                        help="data source (toolforge is not implemented in phase 1)")
    discovery = parser.add_argument_group("discovery")
    discovery.add_argument("--vital-level", type=int, default=None,
                           help="vital-articles level to fetch (0 disables)")
    discovery.add_argument("--popular-limit", type=int, default=None,
                           help="number of top-pageview articles (0 disables)")
    discovery.add_argument("--popularity-timeframe", choices=["last-day", "last-month"],
                           default=None)
    discovery.add_argument("--min-pageviews", type=int, default=None)
    discovery.add_argument("--titles", default=None,
                           help="comma-separated explicit titles to fetch")
    source = parser.add_argument_group("wiktionary pronunciation source")
    source.add_argument("--wiktionary-dump", default=None,
                        help="path to a raw enwiktionary JSONL(.gz); when set, "
                             "pronunciations come from Wiktionary instead of Wikipedia leads")
    source.add_argument("--no-phrase-passthrough", action="store_true",
                        help="disable whole-phrase lookup fallback over word tokens")
    output = parser.add_argument_group("output (at least one required)")
    output.add_argument("--sqlite", default=None)
    output.add_argument("--sqlite-minimal", default=None,
                        help="minimal two-column `word -> phonetic` SQLite lookup")
    output.add_argument("--tsv", default=None)
    output.add_argument("--tsv-gz", default=None)
    output.add_argument("--condensed", default=None)
    output.add_argument("--condensed-phonetic", choices=["respell", "ipa"], default=None,
                        help="which form the condensed lookup emits (default: respell)")
    tuning = parser.add_argument_group("tuning")
    tuning.add_argument("--api-chunk-size", type=int, default=None)
    tuning.add_argument("--rate-limit-sleep", type=float, default=None)
    tuning.add_argument("--user-agent", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    outputs = [o for o in (args.sqlite, args.sqlite_minimal, args.tsv, args.tsv_gz, args.condensed) if o]

    if args.mode == "toolforge":
        print("error: --mode toolforge is not implemented in phase 1; use --mode api", file=sys.stderr)
        return 2

    cfg = load_config(args.config or _default_config_path(), {
        "vital_level": args.vital_level,
        "popular_limit": args.popular_limit,
        "popularity_timeframe": args.popularity_timeframe,
        "min_pageviews": args.min_pageviews,
        "api_chunk_size": args.api_chunk_size,
        "rate_limit_sleep": args.rate_limit_sleep,
        "user_agent": args.user_agent,
    })
    if args.titles is not None:
        cfg.titles = [t.strip() for t in args.titles.split(",") if t.strip()]

    session = requests.Session()
    session.headers["User-Agent"] = cfg.user_agent

    source_lists: list[list[str]] = [cfg.titles]
    if cfg.vital_level:
        print(f"discovering vital articles (level {cfg.vital_level})...", file=sys.stderr)
        source_lists.append(fetch_vital_titles(
            cfg.vital_level, cfg.base_url, session, cfg.timeout, cfg.max_retries, cfg.rate_limit_sleep))
    if cfg.popular_limit:
        print(f"discovering top pageviews (limit {cfg.popular_limit}, {cfg.popularity_timeframe})...",
              file=sys.stderr)
        source_lists.append([
            title for title, _views in fetch_top_pageviews(
                cfg.popular_limit, cfg.popularity_timeframe, cfg.rest_base_url, session,
                cfg.min_pageviews, cfg.timeout, cfg.max_retries, cfg.rate_limit_sleep)
        ])

    titles = dedupe(*source_lists)
    print(f"candidates: {len(titles)}", file=sys.stderr)
    if not titles:
        print("no candidates to fetch", file=sys.stderr)
        return 1

    entries: list[Entry] = []
    if args.wiktionary_dump:
        print(f"resolving {len(titles)} titles against Wiktionary dump...", file=sys.stderr)
        entries = entries_from_wiktionary(
            titles, args.wiktionary_dump,
            phrase_passthrough=not args.no_phrase_passthrough,
        )
    else:
        print("fetching lead sections...", file=sys.stderr)
        for title, wikitext in fetch_leads(
            titles, cfg.base_url, session, cfg.api_chunk_size,
            cfg.rate_limit_sleep, cfg.timeout, cfg.max_retries,
        ):
            entry = _build_entry(title, extract_pronunciations(wikitext))
            if entry is not None:
                entries.append(entry)

    if args.sqlite:
        write_sqlite(entries, args.sqlite, low_memory=cfg.low_memory)
        print(f"wrote {len(entries)} rows -> {args.sqlite}", file=sys.stderr)
    if args.sqlite_minimal:
        phonetic = args.condensed_phonetic or "respell"
        n = write_sqlite_lookup(entries, args.sqlite_minimal, phonetic=phonetic,
                                low_memory=cfg.low_memory)
        print(f"wrote {n} rows -> {args.sqlite_minimal}", file=sys.stderr)
    if args.tsv:
        write_tsv(entries, args.tsv)
        print(f"wrote {len(entries)} rows -> {args.tsv}", file=sys.stderr)
    if args.tsv_gz:
        target = args.tsv_gz if args.tsv_gz.endswith(".gz") else args.tsv_gz + ".gz"
        write_tsv(entries, target)
        print(f"wrote {len(entries)} rows -> {target}", file=sys.stderr)
    if args.condensed:
        phonetic = args.condensed_phonetic or "respell"
        n = write_condensed(entries, args.condensed, phonetic=phonetic)
        print(f"wrote {n} rows -> {args.condensed}", file=sys.stderr)

    if not outputs:
        # Default: two-column respell lookup on stdout (headerless, data only).
        phonetic = args.condensed_phonetic or "respell"
        write_condensed(entries, "-", phonetic=phonetic, header=False)

    print(f"done: {len(entries)} pronunciations extracted", file=sys.stderr)
    return 0


def _build_entry(word: str, extracted) -> Entry | None:
    ipa, respell = extracted.ipa, extracted.respell
    ipa_derived = respell_derived = False
    respell_method = None
    if ipa is None and respell:
        ipa = diaphonemes.respell_to_ipa(respell) or None
        ipa_derived = ipa is not None
    if respell is None and ipa:
        respell, respell_method = _ipa_to_respell(ipa)
        respell_derived = respell is not None
    if ipa is None and respell is None:
        return None
    return Entry(word=word, ipa=ipa, respell=respell,
                 ipa_derived=ipa_derived, respell_derived=respell_derived,
                 respell_method=respell_method)


def _ipa_to_respell(ipa: str) -> tuple[str | None, str | None]:
    """Best-effort IPA -> respelling, preferring the canonical port.

    Multi-pronunciation alternates (``,``) are reduced to the first variant and
    word separators (``_``) become spaces. On failure the legacy heuristic is
    used. Returns ``(respell, method)`` where ``method`` is ``"canonical"`` or
    ``"heuristic"`` (or ``None`` when no respelling could be produced).
    """
    try:
        cleaned = ipa.replace("_", " ").split(",")[0].strip()
        return (ipa_to_canonical_respell(cleaned) or None), "canonical"
    except ValueError:
        return (diaphonemes.ipa_to_respell(ipa) or None), "heuristic"


if __name__ == "__main__":
    sys.exit(main())