#!/usr/bin/env python3
"""Validate ARS held-out measurement reports against the #654 contract.

Two layers:
  1. JSON Schema (evals/heldout/measurement_report.schema.json) — shape,
     enums, const attestations (rubric_precommitted / raw_published /
     raw_outputs.retained), and the suite-class branches B1-B3.
  2. Cross-field invariants I1-I8 (below) — rules a schema cannot express.
     Invariants run only on schema-valid reports (schema errors short-circuit).

Invariants:
  I1  aggregate.agreement.rate equals 1 - |divergent| / |items judged by >=2
      judges| (tolerance 0.005); null iff no item is judged by >=2 judges.
  I2  derived judge minimum: a decision-relevant, non-mechanical run with
      judge_plan.exception == "none" requires >= 2 judges drawn from >= 2
      distinct model families. The minimum is derived, never author-declared.
  I3  every aggregate.agreement.divergent_items id exists in some judge's
      per_item rows.
  I4  every adjudication override's item_id exists in the judged item set.
  I5  suite is a key of evals/heldout/suite_registry.json and suite_class
      matches the registry.
  I6  decision_relevant runs require replicates.per_item >= 2 unless a
      written replicates.exception is present.
  I7  raw_outputs.paths is non-empty.
  I8  an item actually judged differently by >= 2 judges must be listed in
      aggregate.agreement.divergent_items (divergence is never averaged away).

Warnings (never gate):
  W1  judges cover different item sets (partial judge failure — must be
      reflected in attempts.blocked_runs / the run notes).

Usage:
  python scripts/check_heldout_measurement_report.py report.json [...]
  python scripts/check_heldout_measurement_report.py --all
      # walks evals/heldout/**/*.json and validates every file carrying the
      # opt-in "measurement_contract" marker, wherever the suite files it;
      # legacy rows without the marker are ignored by design (retrofit
      # scope: future runs and re-runs only).

Exit 0 on pass (warnings may print to stderr), 1 on any error.
"""
from __future__ import annotations

import argparse
import functools
import json
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
HELDOUT_ROOT = REPO_ROOT / "evals" / "heldout"
SCHEMA_PATH = HELDOUT_ROOT / "measurement_report.schema.json"
REGISTRY_PATH = HELDOUT_ROOT / "suite_registry.json"
CONTRACT_PREFIX = "heldout-measurement/"
RATE_TOLERANCE = 0.005


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    seen: dict[str, object] = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key {key!r}")
        seen[key] = value
    return seen


def _loads_strict(text: str) -> dict:
    """JSON load rejecting duplicate keys and NaN/Infinity.

    Duplicate keys are last-value-wins in plain json.loads, which would let a
    file carry `"raw_published": false, ... "raw_published": true` — passing
    the const attestation while reading as false to a human. Same fail-closed
    stance as cross_model_handoff / check_degradation_registry /
    check_evals_gold_set.
    """
    return json.loads(
        text,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=lambda name: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant {name!r}")
        ),
    )


@functools.cache
def _validator() -> jsonschema.Draft202012Validator:
    schema = _loads_strict(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def contract_version() -> str:
    """The exact contract marker — single-sourced from the schema const."""
    return _validator().schema["properties"]["measurement_contract"]["const"]


@functools.cache
def _suite_registry() -> dict:
    registry = _loads_strict(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in registry.items() if not k.startswith("_")}


def is_contract_report(obj: dict) -> bool:
    """True when the file opts into the #654 contract (any version)."""
    marker = obj.get("measurement_contract")
    return isinstance(marker, str) and marker.startswith(CONTRACT_PREFIX)


def _index_judges(judges: list[dict]) -> dict[str, list[dict]]:
    """item_id -> list of per-item payloads (minus item_id), one per judge."""
    by_item: dict[str, list[dict]] = {}
    for judge in judges:
        for row in judge["per_item"]:
            payload = {k: v for k, v in row.items() if k != "item_id"}
            by_item.setdefault(row["item_id"], []).append(payload)
    return by_item


def _invariant_findings(report: dict) -> tuple[list[str], list[str]]:
    """Cross-field invariants. Assumes the report is schema-valid."""
    errors: list[str] = []
    warnings: list[str] = []

    suite = report["suite"]
    suite_class = report["suite_class"]
    judges = report["judges"]
    exception = report["judge_plan"]["exception"]
    agreement = report["aggregate"]["agreement"]

    by_item = _index_judges(judges)
    judged_ids = set(by_item)
    comparable = {i for i, payloads in by_item.items() if len(payloads) >= 2}
    divergent = {
        i
        for i in comparable
        if any(p != by_item[i][0] for p in by_item[i][1:])
    }

    # I1 — agreement rate is recomputed, not trusted.
    rate = agreement["rate"]
    if comparable:
        expected = 1 - len(divergent) / len(comparable)
        if rate is None:
            errors.append(
                f"I1: agreement.rate is null but {len(comparable)} item(s) are "
                f"judged by >=2 judges (expected ~{expected:.3f})"
            )
        elif abs(rate - expected) > RATE_TOLERANCE:
            errors.append(
                f"I1: agreement.rate={rate} but recomputation gives "
                f"{expected:.3f} (1 - {len(divergent)}/{len(comparable)})"
            )
    elif rate is not None:
        errors.append("I1: agreement.rate must be null when no item is judged by >=2 judges")

    # I2 — derived judge minimum + family diversity.
    if (
        report["decision_relevant"]
        and suite_class != "mechanical_match"
        and exception == "none"
    ):
        families = {j["model_family"] for j in judges}
        if len(judges) < 2:
            errors.append(
                f"I2: decision-relevant {suite_class} run with {len(judges)} judge(s) "
                "and exception='none' — the derived minimum is 2 judges; label the "
                "exception or add judges"
            )
        elif len(families) < 2:
            errors.append(
                f"I2: judges span a single model family {sorted(families)!r} — "
                "decision-relevant runs require >=2 distinct families "
                "(or a labeled exception)"
            )

    # I3 — listed divergent items must be judged items.
    for item_id in agreement["divergent_items"]:
        if item_id not in judged_ids:
            errors.append(
                f"I3: divergent item {item_id!r} not present in any judge's per_item rows"
            )

    # I4 — overrides must target judged items.
    adjudication = report["adjudication"]
    for override in adjudication.get("overrides", []):
        if override["item_id"] not in judged_ids:
            errors.append(
                f"I4: override targets unknown item {override['item_id']!r} "
                "(not in any judge's rows)"
            )

    # I5 — suite registry binding.
    registry = _suite_registry()
    if suite not in registry:
        errors.append(
            f"I5: suite {suite!r} is not in evals/heldout/suite_registry.json — "
            "register it (with its class) before publishing contract rows"
        )
    elif registry[suite] != suite_class:
        errors.append(
            f"I5: suite {suite!r} is registered as {registry[suite]!r} "
            f"but the report declares suite_class={suite_class!r}"
        )

    # I6 — decision-relevant runs replicate.
    replicates = report["replicates"]
    if (
        report["decision_relevant"]
        and replicates["per_item"] < 2
        and not replicates.get("exception")
    ):
        errors.append(
            f"I6: decision_relevant run with replicates.per_item={replicates['per_item']} — "
            "require >=2 or a written replicates.exception"
        )

    # I7 — retained raw outputs need paths (retained itself is a schema const).
    if not report["raw_outputs"]["paths"]:
        errors.append("I7: raw_outputs.paths is empty")

    # I8 — actual cross-judge divergence must be listed.
    unlisted = divergent - set(agreement["divergent_items"])
    if unlisted:
        errors.append(
            "I8: cross-judge divergence on "
            f"{sorted(unlisted)} not listed in aggregate.agreement.divergent_items"
        )

    # W1 — judges cover different item sets.
    per_judge_sets = [{row["item_id"] for row in j["per_item"]} for j in judges]
    if per_judge_sets and any(s != per_judge_sets[0] for s in per_judge_sets[1:]):
        warnings.append(
            "W1: judges cover different item sets (partial judge failure?) — "
            "reflect it in attempts.blocked_runs / run notes"
        )

    return errors, warnings


def validate_report(report: dict) -> tuple[list[str], list[str]]:
    """Full validation: (errors, warnings). Does not mutate the input.

    Schema errors short-circuit: invariants only run on schema-valid reports,
    so a schema-invalid file reports its schema errors alone.
    """
    validator = _validator()
    schema_errors = [
        f"schema {list(e.absolute_path)}: {e.message}"
        for e in validator.iter_errors(report)
    ]
    if schema_errors:
        return schema_errors, []
    return _invariant_findings(report)


def _load(path: Path) -> dict | None:
    try:
        obj = _loads_strict(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {path}: failed to load: {exc}")
        return None
    if not isinstance(obj, dict):
        print(f"ERROR: {path}: top-level JSON value is not an object")
        return None
    return obj


def _validate_obj(path: Path, report: dict) -> int:
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
        help="walk evals/heldout/**/*.json; validate opt-in files only",
    )
    args = parser.parse_args()

    if args.all:
        rc = 0
        opted_in = 0
        scanned = 0
        for path in sorted(HELDOUT_ROOT.rglob("*.json")):
            if path == SCHEMA_PATH or path == REGISTRY_PATH:
                continue
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            try:
                obj = _loads_strict(text)
            except ValueError:
                # Legacy / non-report JSON (fixtures, run records) may be
                # arbitrary and is skipped — but a contract-MARKED file that
                # fails strict parsing (duplicate keys, NaN) must fail loudly,
                # not vanish from validation.
                try:
                    lenient = json.loads(text)
                except ValueError:
                    continue
                if isinstance(lenient, dict) and is_contract_report(lenient):
                    print(f"ERROR: {path}: contract-marked file fails strict JSON parse")
                    rc = 1
                    opted_in += 1
                continue
            if isinstance(obj, dict) and is_contract_report(obj):
                opted_in += 1
                rc = max(rc, _validate_obj(path, obj))
        if opted_in == 0:
            print(
                f"OK: no contract-marked reports among {scanned} JSON file(s) "
                "under evals/heldout/; legacy rows are out of scope by design"
            )
        return rc

    if not args.reports:
        print("ERROR: pass report path(s) or --all", file=sys.stderr)
        return 2
    rc = 0
    for path in args.reports:
        obj = _load(path)
        rc = max(rc, 1 if obj is None else _validate_obj(path, obj))
    return rc


if __name__ == "__main__":
    sys.exit(main())
