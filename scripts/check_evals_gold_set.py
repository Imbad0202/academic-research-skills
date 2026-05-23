#!/usr/bin/env python3
"""Validator for evals/gold/<task>/ gold subsets.

Enforces 9 invariants documented in
docs/design/2026-05-21-v3.10-184-extend-eval-harness-spec.md
implementation plan (Task 4 of #184 Phase 1a).

Usage:
    python -m scripts.check_evals_gold_set <gold-set-dir>

Exit code 0 = clean, non-zero = invariants violated. Prints one line per
violation prefixed with the invariant tag (I1..I9).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

LABEL_ENUM = {"true", "false", "unresolvable"}
KIND_ENUM = {"valid_doi", "valid_arxiv", "valid_unresolvable", "manual_exempt", "fabricated"}
RESOLVER_NAMES = ("crossref", "openalex", "semantic_scholar", "arxiv")
STATUS_ENUM = {"matched", "unmatched", "unreachable", "skipped"}


def _load_json_strict(path: Path) -> Any:
    """Load JSON; raise on duplicate keys (I4)."""
    def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        seen: set[str] = set()
        for k, _ in pairs:
            if k in seen:
                raise ValueError(f"duplicate JSON key: {k!r}")
            seen.add(k)
        return dict(pairs)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicates)


def validate(root: Path) -> list[str]:
    """Return a list of invariant-violation messages. Empty list = clean."""
    errors: list[str] = []
    root = Path(root)
    expected_path = root / "expected_outcomes.json"
    tuples_dir = root / "tuples"

    if not tuples_dir.is_dir():
        errors.append(f"I1: tuples/ directory not found at {tuples_dir}")
        return errors

    # I1: tuple filename stems == expected_outcomes keys
    tuple_stems = {p.stem for p in tuples_dir.glob("*.json")}
    try:
        expected = _load_json_strict(expected_path)
    except ValueError as e:
        errors.append(f"I4: {e}")
        return errors
    expected_keys = set(expected.keys())
    missing = expected_keys - tuple_stems
    extra = tuple_stems - expected_keys
    if missing:
        errors.append(f"I1: tuples missing for expected_outcomes keys: {sorted(missing)}")
    if extra:
        errors.append(f"I1: extra tuple files without expected_outcomes entry: {sorted(extra)}")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python -m scripts.check_evals_gold_set <gold-set-dir>", file=sys.stderr)
        return 2
    root = Path(argv[1])
    errors = validate(root)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"OK: {root} passes all gold-set invariants")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
