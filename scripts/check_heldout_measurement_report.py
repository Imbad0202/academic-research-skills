#!/usr/bin/env python3
"""Validate ARS held-out measurement reports against the #654 contract.

Layers:
  1. JSON Schema (evals/heldout/measurement_report.schema.json) — shape,
     enums, const attestations (rubric_precommitted / raw_published /
     raw_outputs.retained), and the suite-class branches B1-B4.
  2. Cross-field invariants I1-I12 — rules a schema cannot express.
     Invariants run only on schema-valid reports (schema errors short-circuit).
  3. Reference resolution R1-R3 (CLI/CI only; validate_report(...,
     resolve_refs=True)) — attested references must resolve: the rubric file
     exists and matches its hash, raw-output paths exist, the suite commit is
     a real object in this repository.
  4. Location binding L1 (path-aware entry points) — a report filed under
     evals/heldout/<dir>/ must declare suite == <dir>.

Invariants:
  I1   aggregate.agreement.rate equals 1 - |divergent| / |items judged by >=2
       distinct judges| (tolerance 0.005); null iff no such item exists.
  I2   derived judge minimum: a decision-relevant, non-mechanical run with
       judge_plan.exception == "none" requires >= 2 judges drawn from >= 2
       distinct model families (families compared case-/NFKC-folded).
  I3   declared divergent items that are not actually divergent are rejected
       (declared set must not exceed the recomputed set).
  I4   every adjudication override targets a judge that exists AND an item
       that judge actually scored.
  I5   suite is a key of evals/heldout/suite_registry.json and suite_class
       matches the registry; the registry itself must be well-formed.
  I6   decision_relevant runs require replicates.per_item >= 2 unless a
       written replicates.exception is present.
  I7   raw_outputs.paths is non-empty.
  I8   every recomputed divergent item must be listed in
       aggregate.agreement.divergent_items (divergence is never averaged
       away). With I3 this is set equality.
  I9   identity hygiene: no duplicate judge_id; no model_id under two
       families; no two judges sharing (model_id, prompt_ref); no duplicate
       item_id within one judge's per_item; no two distinct raw item ids that
       fold (NFKC + format-character strip) to the same id; per-item verdict
       key-sets must match across judges on comparable items.
  I10  in adjudication-required classes, every divergent item needs >= 1
       override recording its resolution; in judge-bearing classes without
       adjudication, divergence requires a non-empty agreement.note.
  I11  decision-relevant runs: an item judged by some judges but not others
       must be named in attempts.blocked_runs and partial_published must be
       true. (Non-decision runs get warning W1 instead.)
  I12  measurement_date must be a real calendar date.

Warnings (never gate):
  W1   judges cover different item sets on a non-decision-relevant run.

Usage:
  python scripts/check_heldout_measurement_report.py report.json [...]
  python scripts/check_heldout_measurement_report.py --all
      # walks evals/heldout/ (following directory symlinks, cycle-guarded)
      # and validates every JSON file carrying the opt-in
      # "measurement_contract" key. Files without the key are never parsed;
      # a file WITH the key that fails strict parsing (duplicate keys,
      # non-finite numbers, undecodable bytes) fails loudly; a near-miss
      # marker value (homoglyph / stray whitespace) fails loudly.
      # Legacy rows are out of scope by design.

Exit 0 on pass (warnings may print to stderr), 1 on any error.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import functools
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
HELDOUT_ROOT = REPO_ROOT / "evals" / "heldout"
SCHEMA_PATH = HELDOUT_ROOT / "measurement_report.schema.json"
REGISTRY_PATH = HELDOUT_ROOT / "suite_registry.json"
CONTRACT_PREFIX = "heldout-measurement/"
MARKER_KEY = "measurement_contract"
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
    return _validator().schema["properties"][MARKER_KEY]["const"]


def _suite_class_enum() -> list[str]:
    return _validator().schema["properties"]["suite_class"]["enum"]


@functools.cache
def _suite_registry() -> tuple[dict, tuple[str, ...]]:
    """(registry mapping, registry-level errors). Fail-closed on bad registry."""
    errors: list[str] = []
    try:
        raw = _loads_strict(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, (f"I5: suite_registry.json unreadable: {exc}",)
    registry = {k: v for k, v in raw.items() if not k.startswith("_")}
    valid_classes = set(_suite_class_enum())
    for suite, klass in registry.items():
        if klass not in valid_classes:
            errors.append(
                f"I5: suite_registry.json maps {suite!r} to unknown class {klass!r}"
            )
    return registry, tuple(errors)


def is_contract_report(obj: dict) -> bool:
    """True when the file opts into the #654 contract (any version)."""
    marker = obj.get(MARKER_KEY)
    return isinstance(marker, str) and marker.startswith(CONTRACT_PREFIX)


def _fold(value: str) -> str:
    """NFKC-fold, strip Unicode format characters (Cf), casefold.

    The #524 lesson: fold BEFORE comparison in a gate, or a homoglyph /
    zero-width re-spelling slips through.
    """
    normalized = unicodedata.normalize("NFKC", value)
    stripped = "".join(c for c in normalized if unicodedata.category(c) != "Cf")
    return stripped.casefold().strip()


def marker_status(obj: dict) -> str:
    """'contract' | 'near_miss' | 'absent' for a parsed JSON object.

    Any presence of the marker KEY with a non-conforming value (null, number,
    empty or unrelated string, homoglyph spelling) is a near-miss — a file
    that mentions the contract never silently skips validation.
    """
    if MARKER_KEY not in obj:
        return "absent"
    marker = obj[MARKER_KEY]
    if isinstance(marker, str) and marker.startswith(CONTRACT_PREFIX):
        return "contract"
    return "near_miss"


def _names_item(folded_entry: str, folded_item: str) -> bool:
    """True when folded_entry names folded_item as a delimited token — an id
    embedded in a longer id (rp-02 in rp-020) or a concatenated blob does not
    count as naming the gap."""
    pattern = rf"(?<![0-9a-z_-]){re.escape(folded_item)}(?![0-9a-z_-])"
    return re.search(pattern, folded_entry) is not None


def _typed(value: object) -> object:
    """Type-tagged canonical form so 1 != True != 1.0 in payload comparison."""
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, float):
        return ("float", value)
    if isinstance(value, str):
        return ("str", value)
    if value is None:
        return ("null",)
    if isinstance(value, list):
        return ("list", tuple(_typed(v) for v in value))
    if isinstance(value, dict):
        return ("dict", tuple(sorted((k, _typed(v)) for k, v in value.items())))
    return ("other", repr(value))


def _invariant_findings(report: dict) -> tuple[list[str], list[str]]:
    """Cross-field invariants I1-I12. Assumes the report is schema-valid."""
    errors: list[str] = []
    warnings: list[str] = []

    suite = report["suite"]
    suite_class = report["suite_class"]
    judges = report["judges"]
    exception = report["judge_plan"]["exception"]
    agreement = report["aggregate"]["agreement"]
    adjudication = report["adjudication"]

    # ---- I9: identity hygiene (judges) -------------------------------------
    judge_ids = [_fold(j["judge_id"]) for j in judges]
    if len(judge_ids) != len(set(judge_ids)):
        errors.append(f"I9: duplicate judge_id among {sorted(judge_ids)!r} (fold-compared)")
    model_to_families: dict[str, set[str]] = {}
    config_pairs: dict[tuple[str, str], list[str]] = {}
    for j in judges:
        model_to_families.setdefault(_fold(j["model_id"]), set()).add(_fold(j["model_family"]))
        config_pairs.setdefault(
            (_fold(j["model_id"]), _fold(j["prompt_ref"])), []
        ).append(j["judge_id"])
    for model_id, families in model_to_families.items():
        if len(families) > 1:
            errors.append(
                f"I9: model_id {model_id!r} listed under {len(families)} different "
                "model_family values — one physical judge cannot span families"
            )
    for (model_id, _prompt), ids in config_pairs.items():
        if len(ids) > 1:
            errors.append(
                f"I9: judges {sorted(ids)!r} share the same (model_id, prompt_ref) "
                f"({model_id!r}) — the same judge configuration listed twice does "
                "not add independence"
            )

    # ---- I9: identity hygiene (item ids) + per-judge indexing ---------------
    fold_to_raw: dict[str, str] = {}
    by_item: dict[str, dict[int, dict]] = {}
    for idx, judge in enumerate(judges):
        seen_in_judge: set[str] = set()
        for row in judge["per_item"]:
            raw_id = row["item_id"]
            fid = _fold(raw_id)
            prior_raw = fold_to_raw.setdefault(fid, raw_id)
            if prior_raw != raw_id:
                errors.append(
                    f"I9: item ids {prior_raw!r} and {raw_id!r} fold to the same "
                    f"identifier {fid!r} — homoglyph/format-character re-spellings "
                    "are rejected"
                )
            if fid in seen_in_judge:
                errors.append(
                    f"I9: judge {judge['judge_id']!r} lists item {raw_id!r} more "
                    "than once"
                )
                continue
            seen_in_judge.add(fid)
            payload = {k: v for k, v in row.items() if k != "item_id"}
            by_item.setdefault(fid, {})[idx] = payload

    judged_ids = set(by_item)
    comparable = {i for i, per_judge in by_item.items() if len(per_judge) >= 2}
    divergent: set[str] = set()
    for fid in comparable:
        payloads = list(by_item[fid].values())
        keysets = {tuple(sorted(p)) for p in payloads}
        if len(keysets) > 1:
            errors.append(
                f"I9: judges score different field sets on item {fid!r} "
                f"({sorted(sorted(k) for k in keysets)!r}) — verdict fields must "
                "be comparable across judges"
            )
        if any(_typed(p) != _typed(payloads[0]) for p in payloads[1:]):
            divergent.add(fid)

    # ---- I1: agreement rate recomputed -------------------------------------
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
        errors.append(
            "I1: agreement.rate must be null when no item is judged by >=2 judges"
        )

    # ---- I2: derived judge minimum + family diversity ----------------------
    if (
        report["decision_relevant"]
        and suite_class != "mechanical_match"
        and exception == "none"
    ):
        families = {_fold(j["model_family"]) for j in judges}
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

    # ---- I3 + I8: declared divergence == recomputed divergence -------------
    declared = [_fold(i) for i in agreement["divergent_items"]]
    declared_set = set(declared)
    over_declared = declared_set - divergent
    if over_declared:
        errors.append(
            f"I3: declared divergent items {sorted(over_declared)!r} are not "
            "actually divergent (agreeing, single-judge, or unknown items)"
        )
    unlisted = divergent - declared_set
    if unlisted:
        errors.append(
            "I8: cross-judge divergence on "
            f"{sorted(unlisted)} not listed in aggregate.agreement.divergent_items"
        )

    # ---- I4: overrides bind to a judge AND an item that judge scored -------
    judge_index = {j["judge_id"]: idx for idx, j in enumerate(judges)}
    for override in adjudication.get("overrides", []):
        o_item, o_judge = _fold(override["item_id"]), override["judge_id"]
        if o_judge not in judge_index:
            errors.append(
                f"I4: override references unknown judge {o_judge!r}"
            )
        elif o_item not in by_item or judge_index[o_judge] not in by_item[o_item]:
            errors.append(
                f"I4: override targets item {override['item_id']!r} which judge "
                f"{o_judge!r} never scored"
            )

    # ---- I5: suite registry binding ----------------------------------------
    registry, registry_errors = _suite_registry()
    errors.extend(registry_errors)
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

    # ---- I6: decision-relevant runs replicate ------------------------------
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

    # ---- I7: retained raw outputs need paths -------------------------------
    if not report["raw_outputs"]["paths"]:
        errors.append("I7: raw_outputs.paths is empty")

    # ---- I10: every divergent item has a recorded resolution ---------------
    if divergent:
        if adjudication.get("applies") is True:
            overridden = {_fold(o["item_id"]) for o in adjudication.get("overrides", [])}
            unresolved = divergent - overridden
            if unresolved:
                errors.append(
                    f"I10: divergent items {sorted(unresolved)!r} have no "
                    "adjudication override recording their resolution"
                )
        elif not agreement["note"].strip():
            errors.append(
                "I10: divergence present without adjudication — "
                "aggregate.agreement.note must record the resolution"
            )

    # ---- I11 / W1: partial judge coverage ----------------------------------
    per_judge_sets = [
        {_fold(row["item_id"]) for row in j["per_item"]} for j in judges
    ]
    if per_judge_sets:
        union = set().union(*per_judge_sets)
        gaps = {i for s in per_judge_sets for i in union - s}
        if gaps:
            if report["decision_relevant"]:
                blocked = report["attempts"]["blocked_runs"]
                uncovered = {
                    g
                    for g in gaps
                    if not any(_names_item(_fold(b), g) for b in blocked)
                }
                if uncovered:
                    errors.append(
                        f"I11: items {sorted(uncovered)!r} are missing from some "
                        "judge's rows and not named in attempts.blocked_runs"
                    )
                if report["attempts"]["partial_published"] is not True:
                    errors.append(
                        "I11: partial judge coverage requires "
                        "attempts.partial_published=true"
                    )
            else:
                warnings.append(
                    "W1: judges cover different item sets (partial judge failure?) — "
                    "reflect it in attempts.blocked_runs / run notes"
                )

    # ---- I12: real calendar date -------------------------------------------
    try:
        _dt.date.fromisoformat(report["measurement_date"])
    except ValueError:
        errors.append(
            f"I12: measurement_date {report['measurement_date']!r} is not a real "
            "calendar date"
        )

    return errors, warnings


def _resolution_findings(report: dict) -> list[str]:
    """R1-R3: attested references must resolve. Repo-relative, traversal-safe."""
    errors: list[str] = []

    def _repo_path(ref: str, label: str) -> Path | None:
        candidate = (REPO_ROOT / ref).resolve()
        if not candidate.is_relative_to(REPO_ROOT):
            errors.append(f"{label}: reference {ref!r} escapes the repository root")
            return None
        return candidate

    adjudication = report["adjudication"]
    if adjudication.get("applies") is True:
        rubric = _repo_path(adjudication["rubric_ref"], "R1")
        if rubric is not None:
            if not rubric.is_file():
                errors.append(
                    f"R1: rubric_ref {adjudication['rubric_ref']!r} does not exist "
                    "in the repository — the rubric must be committed"
                )
            else:
                digest = hashlib.sha256(rubric.read_bytes()).hexdigest()
                if digest != adjudication["rubric_sha256"]:
                    errors.append(
                        f"R1: rubric_sha256 does not match the committed rubric "
                        f"(declared {adjudication['rubric_sha256'][:12]}…, "
                        f"actual {digest[:12]}…)"
                    )

    suite_dir = (HELDOUT_ROOT / report["suite"]).resolve()
    for ref in report["raw_outputs"]["paths"]:
        target = _repo_path(ref, "R2")
        if target is None:
            continue
        if not target.is_relative_to(suite_dir):
            errors.append(
                f"R2: raw_outputs path {ref!r} is not under "
                f"evals/heldout/{report['suite']}/ — raw outputs live in their "
                "suite's directory"
            )
        elif not target.exists():
            errors.append(f"R2: raw_outputs path {ref!r} does not exist")

    baseline_ref = report["judge_plan"].get("legacy_baseline_ref")
    if baseline_ref is not None:
        baseline = _repo_path(baseline_ref, "R1")
        if baseline is not None and not baseline.is_file():
            errors.append(
                f"R1: legacy_baseline_ref {baseline_ref!r} does not exist in the "
                "repository — the comparability claim must name a real legacy row"
            )

    commit = report["subject"]["config"]["suite_commit"]
    try:
        probe = subprocess.run(
            ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        missing = probe.returncode != 0
    except (OSError, ValueError) as exc:
        errors.append(f"R3: could not verify suite_commit ({exc})")
        missing = False
    if missing:
        errors.append(
            f"R3: subject.config.suite_commit {commit!r} is not a commit in this "
            "repository"
        )

    return errors


def location_errors(path: Path, report: dict) -> list[str]:
    """L1: a report filed under evals/heldout/<dir>/ must declare suite == <dir>.

    Uses the path AS FILED (absolute but unresolved), so a row reached through
    a symlinked suite directory is judged by where it is filed, not where the
    bytes physically live. Paths outside evals/heldout/ (drafts) are unchecked.
    """
    try:
        rel = path.absolute().relative_to(HELDOUT_ROOT.absolute())
    except ValueError:
        return []
    parts = rel.parts
    if len(parts) < 2:
        return [
            "L1: a contract row must live inside a suite directory "
            "(evals/heldout/<suite>/...), not at the evals/heldout/ root"
        ]
    if parts[0] != report.get("suite"):
        return [
            f"L1: report filed under evals/heldout/{parts[0]}/ declares "
            f"suite={report.get('suite')!r} — the containing suite directory "
            "and the declared suite must match"
        ]
    return []


def validate_report(
    report: dict, *, resolve_refs: bool = False
) -> tuple[list[str], list[str]]:
    """Full validation: (errors, warnings). Does not mutate the input.

    Schema errors short-circuit: invariants only run on schema-valid reports,
    so a schema-invalid file reports its schema errors alone. resolve_refs
    additionally runs R1-R3 (CLI/CI mode; needs the repository checkout).
    """
    validator = _validator()
    schema_errors = [
        f"schema {list(e.absolute_path)}: {e.message}"
        for e in validator.iter_errors(report)
    ]
    if schema_errors:
        return schema_errors, []
    errors, warnings = _invariant_findings(report)
    if resolve_refs and not errors:
        errors.extend(_resolution_findings(report))
    return errors, warnings


def _validate_obj(path: Path, report: dict) -> int:
    errors, warnings = validate_report(report, resolve_refs=True)
    errors.extend(location_errors(path, report))
    for w in warnings:
        print(f"{path}: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"ERROR: {path}: {e}")
        return 1
    print(f"OK: {path} validates against {report.get(MARKER_KEY)}")
    return 0


def _walk_json_files(root: Path) -> tuple[list[Path], list[str]]:
    """All *.json files under root (case-insensitive extension), following
    directory symlinks with a resolved-path cycle guard.

    Symlinked directories are followed only when their resolved target stays
    inside the repository — an external target cannot hold repo-published
    rows (git stores the link, not the content) and following it would let
    the walk traverse arbitrary trees. Unreadable directories are surfaced
    as walk errors, never silently skipped."""
    found: list[Path] = []
    walk_errors: list[str] = []
    visited: set[Path] = set()
    repo_real = REPO_ROOT.resolve()
    root_real = root.resolve()

    def _walk(directory: Path) -> None:
        real = directory.resolve()
        if real in visited:
            return
        if not (real.is_relative_to(root_real) or real.is_relative_to(repo_real)):
            walk_errors.append(
                f"{directory}: symlinked directory resolves outside the "
                "repository — not scanned (repo-published rows cannot live there)"
            )
            return
        visited.add(real)
        try:
            entries = sorted(os.scandir(directory), key=lambda e: e.name)
        except OSError as exc:
            walk_errors.append(f"{directory}: unreadable directory: {exc}")
            return
        for entry in entries:
            p = directory / entry.name
            try:
                is_dir = entry.is_dir(follow_symlinks=True)
            except OSError:
                is_dir = False
            if is_dir:
                _walk(p)
            elif p.suffix.lower() == ".json":
                try:
                    file_real = p.resolve()
                except OSError:
                    file_real = p
                if not (
                    file_real.is_relative_to(root_real)
                    or file_real.is_relative_to(repo_real)
                ):
                    walk_errors.append(
                        f"{p}: file symlink resolves outside the repository — "
                        "not scanned (repo-published rows cannot live there)"
                    )
                    continue
                found.append(p)

    _walk(root)
    return found, walk_errors


def _scan_all() -> int:
    rc = 0
    opted_in = 0
    scanned = 0
    files, walk_errors = _walk_json_files(HELDOUT_ROOT)
    for err in walk_errors:
        print(f"ERROR: {err}")
        rc = 1
    for path in files:
        if path.resolve() in (SCHEMA_PATH.resolve(), REGISTRY_PATH.resolve()):
            continue
        scanned += 1
        try:
            raw = path.read_bytes()
        except OSError as exc:
            print(f"ERROR: {path}: unreadable JSON file under evals/heldout/: {exc}")
            rc = 1
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            print(f"ERROR: {path}: not valid UTF-8 ({exc}) — JSON must be UTF-8")
            rc = 1
            continue
        # Detection is on the PARSED document, so a \u-escaped spelling of
        # the marker key cannot hide a report from the scan.
        try:
            lenient = json.loads(text)
        except (ValueError, RecursionError) as exc:
            if MARKER_KEY in text.replace("\\u005f", "_"):
                print(
                    f"ERROR: {path}: mentions {MARKER_KEY!r} but does not parse "
                    f"as JSON ({exc})"
                )
                rc = 1
            continue
        if not isinstance(lenient, dict):
            continue
        status = marker_status(lenient)
        if status == "absent":
            continue
        # Marked (or near-miss-marked) files must survive the strict parse.
        try:
            obj = _loads_strict(text)
        except (ValueError, RecursionError) as exc:
            print(
                f"ERROR: {path}: carries {MARKER_KEY!r} but fails strict JSON "
                f"parse ({exc}) — a contract-marked file may not carry duplicate "
                "keys or non-finite numbers"
            )
            rc = 1
            opted_in += 1
            continue
        if status == "near_miss":
            print(
                f"ERROR: {path}: {MARKER_KEY} value {lenient.get(MARKER_KEY)!r} is "
                f"not the exact contract marker (expected prefix {CONTRACT_PREFIX!r}) "
                "— near-miss markers fail loudly rather than skipping validation"
            )
            rc = 1
            opted_in += 1
        else:
            opted_in += 1
            rc = max(rc, _validate_obj(path, obj))
    if opted_in == 0 and rc == 0:
        print(
            f"OK: no contract-marked reports among {scanned} JSON file(s) "
            "under evals/heldout/; legacy rows are out of scope by design"
        )
    return rc


def _load(path: Path) -> dict | None:
    try:
        obj = _loads_strict(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as exc:
        print(f"ERROR: {path}: failed to load: {exc}")
        return None
    if not isinstance(obj, dict):
        print(f"ERROR: {path}: top-level JSON value is not an object")
        return None
    return obj


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="*", type=Path)
    parser.add_argument(
        "--all",
        action="store_true",
        help="walk evals/heldout/ and validate every contract-marked JSON file",
    )
    args = parser.parse_args()

    if args.all:
        return _scan_all()

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
