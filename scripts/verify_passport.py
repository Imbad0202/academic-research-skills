#!/usr/bin/env python3
"""verify_passport CLI — ad-hoc citation existence verification (Delta 5).

    python -m scripts.verify_passport <passport.yaml>

Loads a Material Passport YAML, runs verification_gate.verify_passport over its
literature_corpus[], and prints the list of per-citation summaries as JSON. A
standalone entry point for ad-hoc verification, separate from the Stage 4->5
audit pipeline.

Anchor note: the v3.7.3 anchor lives in writer prose (the <!--anchor:...-->
markers), not in literature_corpus. This ad-hoc CLI has no prose document to
join against, so every `anchor_present` is False. The prose-marker join (passing
an {ref_slug: anchor} map into verify_passport) is wired by the Stage 4->5
pipeline / formatter batch, not by this standalone tool.

Spec: docs/design/2026-05-21-v3.10-182-promote-citation-gate-spec.md §2 Delta 5.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

try:
    from verification_gate import verify_passport
except ImportError:  # pragma: no cover
    from scripts.verification_gate import verify_passport


def _real_clients() -> dict:
    """Construct the four production resolver clients. Imported lazily so the
    CLI module loads without network deps and tests can inject a stub factory.
    Dual-path import: under `python -m scripts.verify_passport` the repo root is
    on sys.path (not scripts/), so the bare imports fall back to scripts.*."""
    try:
        from crossref_client import CrossrefClient
        from openalex_client import OpenAlexClient
        from arxiv_client import ArxivClient
        from semantic_scholar_client import SemanticScholarClient
    except ImportError:  # pragma: no cover - exercised via `python -m`
        from scripts.crossref_client import CrossrefClient
        from scripts.openalex_client import OpenAlexClient
        from scripts.arxiv_client import ArxivClient
        from scripts.semantic_scholar_client import SemanticScholarClient
    return {
        "crossref": CrossrefClient(),
        "openalex": OpenAlexClient(),
        "semantic_scholar": SemanticScholarClient(),
        "arxiv": ArxivClient(),
    }


def run(argv: list[str] | None = None, *, clients_factory=_real_clients) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_passport",
        description="Verify citation existence across a Material Passport.",
    )
    parser.add_argument("passport", help="Path to the passport YAML file.")
    args = parser.parse_args(argv)

    path = Path(args.passport)
    if not path.is_file():
        print(f"[verify_passport ERROR] passport not found: {path}",
              file=sys.stderr)
        return 1
    try:
        passport = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print(f"[verify_passport ERROR] could not parse YAML: {e}",
              file=sys.stderr)
        return 1

    outcomes = verify_passport(passport, clients=clients_factory())
    print(json.dumps(outcomes, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(run())
