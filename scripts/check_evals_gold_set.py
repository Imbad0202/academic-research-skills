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
import re
import sys
from pathlib import Path
from typing import Any

import yaml

LABEL_ENUM = {"true", "false", "unresolvable"}
KIND_ENUM = {"valid_doi", "valid_arxiv", "valid_unresolvable", "manual_exempt", "fabricated"}
RESOLVER_NAMES = ("crossref", "openalex", "semantic_scholar", "arxiv")
STATUS_ENUM = {"matched", "unmatched", "unreachable", "skipped"}

_PROVENANCE_RE = re.compile(r"^last verified unresolvable: \d{4}-\d{2}-\d{2}")


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

    # I2: per-tuple tuple_id == filename stem
    for path in sorted(tuples_dir.glob("*.json")):
        try:
            tup = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"I2: {path.name} is not valid JSON: {e}")
            continue
        tid = tup.get("tuple_id")
        if tid != path.stem:
            errors.append(f"I2: {path.name} tuple_id={tid!r} != filename stem {path.stem!r}")

    # I3: kind distribution matches manifest tuple_distribution
    manifest_path = root / "manifest.yaml"
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        errors.append(f"I3: manifest.yaml does not parse: {e}")
        return errors
    declared = {entry["kind"]: entry["n"] for entry in manifest["tuple_distribution"]}
    observed: dict[str, int] = {}
    for path in sorted(tuples_dir.glob("*.json")):
        try:
            tup = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        k = tup.get("kind")
        if k not in KIND_ENUM:
            errors.append(f"I3: {path.name} has unknown kind {k!r}")
            continue
        observed[k] = observed.get(k, 0) + 1
    for k, declared_n in declared.items():
        obs_n = observed.get(k, 0)
        if obs_n != declared_n:
            errors.append(f"I3: kind {k!r} count {obs_n} != manifest declared {declared_n}")

    # I5: expected_outcomes label matches manifest's kind->label mapping
    kind_to_label = {entry["kind"]: entry["expected_lookup_verified"]
                     for entry in manifest["tuple_distribution"]}
    tuple_id_to_kind: dict[str, str] = {}
    for path in sorted(tuples_dir.glob("*.json")):
        try:
            tup = json.loads(path.read_text(encoding="utf-8"))
            tuple_id_to_kind[path.stem] = tup.get("kind")
        except json.JSONDecodeError:
            pass
    for tid, outcome in expected.items():
        label = outcome.get("lookup_verified")
        if label not in LABEL_ENUM:
            errors.append(f"I5: {tid} lookup_verified={label!r} not in {sorted(LABEL_ENUM)}")
            continue
        kind = tuple_id_to_kind.get(tid)
        if kind is None:
            continue  # I1 already reported missing tuple
        expected_label = kind_to_label.get(kind)
        if expected_label is not None and label != expected_label:
            errors.append(
                f"I5: {tid} lookup_verified={label!r} but manifest declares "
                f"kind {kind!r} -> {expected_label!r}"
            )

    # I6: arxiv_id placement consistency
    for path in sorted(tuples_dir.glob("*.json")):
        try:
            tup = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        kind = tup.get("kind")
        arxiv_id = tup.get("arxiv_id")
        doi = (tup.get("corpus_entry") or {}).get("doi")
        if kind == "valid_arxiv":
            if not arxiv_id:
                errors.append(f"I6: {path.name} kind=valid_arxiv but arxiv_id is null/missing")
            if doi:
                errors.append(f"I6: {path.name} kind=valid_arxiv but corpus_entry.doi={doi!r} present")
        elif kind == "valid_doi":
            if arxiv_id:
                errors.append(f"I6: {path.name} kind=valid_doi but arxiv_id={arxiv_id!r} present")
            if not doi:
                errors.append(f"I6: {path.name} kind=valid_doi but corpus_entry.doi missing/null")
        else:
            if arxiv_id:
                errors.append(f"I6: {path.name} kind={kind!r} but arxiv_id={arxiv_id!r} present (must be null)")

    # I7: fabrication_intent <-> kind == "fabricated"
    for path in sorted(tuples_dir.glob("*.json")):
        try:
            tup = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        kind = tup.get("kind")
        marker = tup.get("fabrication_intent")
        if kind == "fabricated" and marker is not True:
            errors.append(f"I7: {path.name} kind=fabricated but fabrication_intent={marker!r} (must be true)")
        if kind != "fabricated" and marker is True:
            errors.append(f"I7: {path.name} kind={kind!r} but fabrication_intent=true (must be false)")

    # I8: valid_unresolvable tuples carry provenance_note matching the date pattern
    for path in sorted(tuples_dir.glob("*.json")):
        try:
            tup = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if tup.get("kind") != "valid_unresolvable":
            continue
        note = tup.get("provenance_note")
        if not note:
            errors.append(f"I8: {path.name} kind=valid_unresolvable but provenance_note is null/missing")
            continue
        if not _PROVENANCE_RE.match(note):
            errors.append(
                f"I8: {path.name} provenance_note={note!r} does not match "
                f"required pattern 'last verified unresolvable: YYYY-MM-DD...'"
            )

    # I9: resolver_outcomes has all four resolver keys with valid status enum
    for tid, outcome in expected.items():
        ros = outcome.get("resolver_outcomes", {})
        for resolver in RESOLVER_NAMES:
            entry = ros.get(resolver)
            if entry is None:
                errors.append(f"I9: {tid} resolver_outcomes missing resolver {resolver!r}")
                continue
            status = entry.get("status")
            if status not in STATUS_ENUM:
                errors.append(
                    f"I9: {tid} resolver_outcomes.{resolver}.status={status!r} "
                    f"not in {sorted(STATUS_ENUM)}"
                )

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
