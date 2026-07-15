#!/usr/bin/env python3
"""Degradation-registry lint (#511 Part A).

Pins shared/contracts/degradation_registry.json — the machine-readable INDEX of
ARS's graceful-degradation mechanisms — to the repo state it cites, so the
registry can never drift into a stale (or second) authority:

  D1. Registry parses, carries registry_version + a non-empty mechanisms list,
      and every row has all required fields with non-empty string values
      (fail-closed: a missing or unparseable registry is an error, never a
      silent pass).
  D2. Mechanism ids are unique.
  D3. Every authority reference names an EXISTING repo file (no ':<line>'
      suffixes — line numbers drift; content anchors are required) and its
      anchor appears VERBATIM in that file. Anchors must be >= 16 chars so a
      trivially-common fragment cannot vacuously satisfy the pin.
  D4. Every pinned_by entry ('path' or 'path::test_function') names an existing
      file; when a ::function is given on a .py path, that function is defined
      in the file.

The registry indexes, it does not re-author (#511): this lint deliberately does
NOT re-verify the degradation SEMANTICS — those live in each row's authority
file and the tests/lints the row cites. What this lint guarantees is that every
citation in the index still resolves.

Usage: python3 scripts/check_degradation_registry.py [--registry PATH]
Exit 0 = all invariants hold; exit 1 = violations (listed on stderr).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = REPO_ROOT / "shared" / "contracts" / "degradation_registry.json"

_REQUIRED_ROW_FIELDS = (
    "mechanism",
    "failure_class",
    "degraded_state",
    "diagnostic_marker",
    "downstream_consumer",
    "terminal_policy_effect",
    "authority",
    "pinned_by",
)
_MIN_ANCHOR_LEN = 16
# 'path::test_function' — the '::' form is pytest's node-id convention.
_PINNED_BY_RE = re.compile(r"^(?P<path>[^:]+)(?:::(?P<func>\w+))?$")


def _load_registry(path: Path) -> tuple[dict | None, list[str]]:
    """D1 fail-closed loader: missing file or bad JSON is an ERROR."""
    if not path.is_file():
        return None, [f"D1: registry file missing: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return None, [f"D1: registry is not parseable JSON: {e}"]
    if not isinstance(data, dict):
        return None, ["D1: registry top level must be a JSON object"]
    return data, []


def _check_shape(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data.get("registry_version"), str) or not data.get(
        "registry_version"
    ):
        errors.append("D1: registry_version missing or not a non-empty string")
    mechanisms = data.get("mechanisms")
    if not isinstance(mechanisms, list) or not mechanisms:
        errors.append("D1: mechanisms must be a non-empty list")
        return errors
    for i, row in enumerate(mechanisms):
        label = f"mechanisms[{i}]"
        if not isinstance(row, dict):
            errors.append(f"D1: {label} is not an object")
            continue
        label = f"mechanisms[{i}] ({row.get('mechanism', '?')})"
        for field in _REQUIRED_ROW_FIELDS:
            if field not in row:
                errors.append(f"D1: {label} missing required field {field!r}")
                continue
            value = row[field]
            if field == "authority":
                if not isinstance(value, list) or not value:
                    errors.append(
                        f"D1: {label}.authority must be a non-empty list")
            elif field == "pinned_by":
                if not isinstance(value, list):
                    errors.append(f"D1: {label}.pinned_by must be a list")
            elif not isinstance(value, str) or not value.strip():
                errors.append(
                    f"D1: {label}.{field} must be a non-empty string")
    return errors


@lru_cache(maxsize=None)
def _read(path: Path) -> str:
    """Memoized file read: authority files repeat across rows as the registry
    grows (firm_rules.md, the corpus-entry schema), and the mutation-test
    suite calls run() dozens of times against the same unchanged repo files."""
    return path.read_text(encoding="utf-8")


def _check_unique_ids(mechanisms: list) -> list[str]:
    seen: set[str] = set()
    errors: list[str] = []
    for row in mechanisms:
        if not isinstance(row, dict):
            continue
        mid = row.get("mechanism")
        if isinstance(mid, str):
            if mid in seen:
                errors.append(f"D2: duplicate mechanism id {mid!r}")
            seen.add(mid)
    return errors


def _check_authorities(mechanisms: list) -> list[str]:
    errors: list[str] = []
    for row in mechanisms:
        if not isinstance(row, dict):
            continue
        label = row.get("mechanism", "?")
        for j, ref in enumerate(row.get("authority") or []):
            where = f"D3: {label}.authority[{j}]"
            if not isinstance(ref, dict):
                errors.append(f"{where} is not an object")
                continue
            file_ref = ref.get("file")
            anchor = ref.get("anchor")
            if not isinstance(file_ref, str) or not file_ref:
                errors.append(f"{where}.file must be a non-empty string")
                continue
            if ":" in file_ref:
                errors.append(
                    f"{where}.file {file_ref!r} carries a ':' — line-number "
                    "references are forbidden; cite a content anchor instead "
                    "(line numbers drift, anchors survive)")
                continue
            target = REPO_ROOT / file_ref
            if not target.is_file():
                errors.append(f"{where}.file does not exist: {file_ref}")
                continue
            if not isinstance(anchor, str) or len(anchor) < _MIN_ANCHOR_LEN:
                errors.append(
                    f"{where}.anchor must be a string of >= {_MIN_ANCHOR_LEN} "
                    "chars (too-short anchors match vacuously)")
                continue
            if anchor not in _read(target):
                errors.append(
                    f"{where}: anchor not found verbatim in {file_ref}: "
                    f"{anchor!r} — either the authority moved (update the "
                    "anchor) or the mechanism changed (update the row)")
    return errors


def _check_pinned_by(mechanisms: list) -> list[str]:
    errors: list[str] = []
    for row in mechanisms:
        if not isinstance(row, dict):
            continue
        label = row.get("mechanism", "?")
        for j, pin in enumerate(row.get("pinned_by") or []):
            where = f"D4: {label}.pinned_by[{j}]"
            if not isinstance(pin, str) or not pin:
                errors.append(f"{where} must be a non-empty string")
                continue
            m = _PINNED_BY_RE.match(pin)
            if not m:
                errors.append(
                    f"{where} {pin!r} is not 'path' or 'path::function'")
                continue
            path = REPO_ROOT / m.group("path")
            if not path.is_file():
                errors.append(f"{where}: pinned file does not exist: {pin}")
                continue
            func = m.group("func")
            if func:
                if path.suffix != ".py":
                    errors.append(
                        f"{where}: ::function form requires a .py path: {pin}")
                    continue
                if not re.search(
                    rf"^def {re.escape(func)}\(",
                    _read(path),
                    re.MULTILINE,
                ):
                    errors.append(
                        f"{where}: function {func!r} not defined in "
                        f"{m.group('path')}")
    return errors


def _run_checks(data: dict) -> list[str]:
    errors = _check_shape(data)
    mechanisms = data.get("mechanisms")
    if isinstance(mechanisms, list) and mechanisms:
        errors += _check_unique_ids(mechanisms)
        errors += _check_authorities(mechanisms)
        errors += _check_pinned_by(mechanisms)
    return errors


def run(registry_path: Path) -> list[str]:
    data, errors = _load_registry(registry_path)
    return errors if data is None else _run_checks(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry", type=Path, default=DEFAULT_REGISTRY,
        help="registry path override (tests); default: %(default)s")
    args = parser.parse_args(argv)
    data, errors = _load_registry(args.registry)
    if data is not None:
        errors = _run_checks(data)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"\ncheck_degradation_registry: {len(errors)} violation(s)",
              file=sys.stderr)
        return 1
    print(f"Degradation registry lint ok ({len(data['mechanisms'])} "
          "mechanisms, all anchors and pins resolve).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
