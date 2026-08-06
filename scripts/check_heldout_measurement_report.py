#!/usr/bin/env python3
"""Validate ARS held-out measurement reports against the #654 contract.

Two layers:
  1. JSON Schema (evals/heldout/measurement_report.schema.json) — shape,
     enums, required disclosure fields.
  2. Cross-field invariants I1-I8 (below) — the contract rules a schema
     cannot express.

Invariants:
  I1  judge_plan.actual == len(judges)
  I2  actual < minimum_for_scored requires a non-"none" exception; and a
      non-mechanical suite_class requires at least one judge regardless of
      any exception.
  I3  every aggregate.agreement.divergent_items id exists in some judge's
      per_item rows.
  I4  when adjudication applies: raw_published is true, rubric_precommitted
      is true, and every override's item_id exists in the judged item set.
  I5  llm_judged and seeded_manifest_adjudicated suites require
      adjudication.applies == true.
  I6  decision_relevant runs require replicates.per_item >= 2 unless a
      written replicates.exception is present.
  I7  raw_outputs.retained must be true, with at least one path.
  I8  an item actually judged differently by >=2 judges must be listed in
      aggregate.agreement.divergent_items (divergence is never averaged away).

Warnings (never gate):
  W1  judges cover different item sets (partial judge failure — must be
      reflected in attempts.blocked_runs / the run notes).

Usage:
  python scripts/check_heldout_measurement_report.py report.json [...]
  python scripts/check_heldout_measurement_report.py --all
      # scans evals/heldout/*/measurement-*.json and validates only files
      # carrying the opt-in "measurement_contract" marker; legacy rows are
      # ignored by design (retrofit scope: future runs and re-runs only).

Exit 0 on pass (warnings may print to stderr), 1 on any error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "evals" / "heldout" / "measurement_report.schema.json"
CONTRACT_PREFIX = "heldout-measurement/"
NON_MECHANICAL_CLASSES = {"llm_judged", "seeded_manifest_adjudicated", "paired_controls"}
ADJUDICATION_REQUIRED_CLASSES = {"llm_judged", "seeded_manifest_adjudicated"}


def is_contract_report(obj: dict) -> bool:
    """True when the file opts into the #654 contract (any version)."""
    marker = obj.get("measurement_contract")
    return isinstance(marker, str) and marker.startswith(CONTRACT_PREFIX)


def _schema_errors(report: dict) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"schema {list(e.absolute_path)}: {e.message}"
        for e in validator.iter_errors(report)
    ]


def _judged_item_ids(judges: list[dict]) -> set[str]:
    ids: set[str] = set()
    for judge in judges:
        for row in judge.get("per_item", []):
            item_id = row.get("item_id")
            if isinstance(item_id, str):
                ids.add(item_id)
    return ids


def _cross_judge_divergent_items(judges: list[dict]) -> set[str]:
    """Item ids whose per-item payloads (minus item_id) differ across judges.

    Only items judged by >= 2 judges are comparable. Payload equality is the
    mechanical divergence rule; suites must keep verdict fields comparable
    across judges (MEASUREMENT_CONTRACT.md § Aggregation).
    """
    seen: dict[str, list[dict]] = {}
    for judge in judges:
        for row in judge.get("per_item", []):
            item_id = row.get("item_id")
            if not isinstance(item_id, str):
                continue
            payload = {k: v for k, v in row.items() if k != "item_id"}
            seen.setdefault(item_id, []).append(payload)
    divergent = set()
    for item_id, payloads in seen.items():
        if len(payloads) >= 2 and any(p != payloads[0] for p in payloads[1:]):
            divergent.add(item_id)
    return divergent


def _invariant_findings(report: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    suite_class = report.get("suite_class")
    judges = report.get("judges", [])
    plan = report.get("judge_plan", {})
    if not isinstance(judges, list):
        judges = []

    # I1 — declared judge count matches reality.
    actual = plan.get("actual")
    if isinstance(actual, int) and actual != len(judges):
        errors.append(
            f"I1: judge_plan.actual={actual} but {len(judges)} judge(s) present"
        )

    # I2 — under-minimum needs a labeled exception; non-mechanical needs >=1 judge.
    minimum = plan.get("minimum_for_scored")
    exception = plan.get("exception")
    if (
        isinstance(actual, int)
        and isinstance(minimum, int)
        and actual < minimum
        and exception == "none"
    ):
        errors.append(
            f"I2: judge_plan.actual={actual} < minimum_for_scored={minimum} "
            "with exception='none' — label the exception or add judges"
        )
    if suite_class in NON_MECHANICAL_CLASSES and len(judges) == 0:
        errors.append(
            f"I2: suite_class={suite_class!r} requires at least one judge; "
            "no exception permits zero judges outside mechanical_match"
        )

    judged_ids = _judged_item_ids(judges)

    # I3 — divergent_items must reference judged items.
    agreement = report.get("aggregate", {}).get("agreement", {})
    listed_divergent = agreement.get("divergent_items", [])
    if isinstance(listed_divergent, list):
        for item_id in listed_divergent:
            if item_id not in judged_ids:
                errors.append(
                    f"I3: divergent item {item_id!r} not present in any judge's per_item rows"
                )

    # I4 — adjudication honesty.
    adjudication = report.get("adjudication", {})
    if isinstance(adjudication, dict) and adjudication.get("applies") is True:
        if adjudication.get("raw_published") is not True:
            errors.append(
                "I4: adjudication.raw_published must be true — raw pre-adjudication "
                "numbers always publish alongside adjudicated ones"
            )
        if adjudication.get("rubric_precommitted") is not True:
            errors.append(
                "I4: adjudication.rubric_precommitted must be true — the rubric is "
                "committed and hashed before any judge output exists"
            )
        for override in adjudication.get("overrides", []):
            item_id = override.get("item_id") if isinstance(override, dict) else None
            if isinstance(item_id, str) and item_id not in judged_ids:
                errors.append(
                    f"I4: override targets unknown item {item_id!r} (not in any judge's rows)"
                )

    # I5 — judged suite classes cannot opt out of adjudication.
    if suite_class in ADJUDICATION_REQUIRED_CLASSES and (
        not isinstance(adjudication, dict) or adjudication.get("applies") is not True
    ):
        errors.append(
            f"I5: suite_class={suite_class!r} requires adjudication.applies=true"
        )

    # I6 — decision-relevant runs replicate.
    replicates = report.get("replicates", {})
    if report.get("decision_relevant") is True and isinstance(replicates, dict):
        per_item = replicates.get("per_item")
        rep_exception = replicates.get("exception")
        if isinstance(per_item, int) and per_item < 2 and not rep_exception:
            errors.append(
                f"I6: decision_relevant run with replicates.per_item={per_item} — "
                "require >=2 or a written replicates.exception"
            )

    # I7 — raw outputs retained.
    raw = report.get("raw_outputs", {})
    if isinstance(raw, dict):
        if raw.get("retained") is not True:
            errors.append("I7: raw_outputs.retained must be true for contract reports")
        elif not raw.get("paths"):
            errors.append("I7: raw_outputs.retained=true but paths is empty")

    # I8 — actual cross-judge divergence must be listed.
    actual_divergent = _cross_judge_divergent_items(judges)
    if isinstance(listed_divergent, list):
        unlisted = actual_divergent - set(listed_divergent)
        if unlisted:
            errors.append(
                "I8: cross-judge divergence on "
                f"{sorted(unlisted)} not listed in aggregate.agreement.divergent_items"
            )

    # W1 — judges cover different item sets.
    per_judge_sets = [
        {row.get("item_id") for row in judge.get("per_item", [])} for judge in judges
    ]
    if per_judge_sets and any(s != per_judge_sets[0] for s in per_judge_sets[1:]):
        warnings.append(
            "W1: judges cover different item sets (partial judge failure?) — "
            "reflect it in attempts.blocked_runs / run notes"
        )

    return errors, warnings


def validate_report(report: dict) -> tuple[list[str], list[str]]:
    """Full validation: (errors, warnings). Does not mutate the input."""
    errors = _schema_errors(report)
    inv_errors, warnings = _invariant_findings(report)
    return errors + inv_errors, warnings


def _validate_file(path: Path) -> int:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {path}: failed to load: {exc}")
        return 1
    errors, warnings = validate_report(report)
    for w in warnings:
        print(f"{path}: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"ERROR: {path}: {e}")
        return 1
    print(f"OK: {path} validates against {report.get('measurement_contract')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="*", type=Path)
    parser.add_argument(
        "--all",
        action="store_true",
        help="scan evals/heldout/*/measurement-*.json; validate opt-in files only",
    )
    args = parser.parse_args()

    if args.all:
        candidates = sorted((REPO_ROOT / "evals" / "heldout").glob("*/measurement-*.json"))
        opted_in: list[Path] = []
        for path in candidates:
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"ERROR: {path}: failed to load: {exc}")
                return 1
            if isinstance(obj, dict) and is_contract_report(obj):
                opted_in.append(path)
        if not opted_in:
            print(
                f"OK: no contract-marked reports among {len(candidates)} "
                "measurement file(s); legacy rows are out of scope by design"
            )
            return 0
        return max(_validate_file(p) for p in opted_in)

    if not args.reports:
        print("ERROR: pass report path(s) or --all", file=sys.stderr)
        return 2
    return max(_validate_file(p) for p in args.reports)


if __name__ == "__main__":
    sys.exit(main())
