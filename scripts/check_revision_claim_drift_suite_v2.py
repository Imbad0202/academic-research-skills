#!/usr/bin/env python3
"""Hermetic contract guard for revision_claim_drift suite v2 (#679).

This checker never invokes a model, judge, adjudicator, network API, or eval
runner.  It validates repository-owned bytes and prospective record bindings.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE_REL = "evals/heldout/revision_claim_drift"
SUITE = Path(SUITE_REL)
RUNS_PREFIX = f"{SUITE_REL}/runs/"

V1_RUBRIC_SHA256 = "56e014d5da2c9074afa7d327803caa2de0e16c864cf0374e4cd1f3cf90e35863"
V2_RUBRIC_SHA256 = "6bb537807f7f0ab02ae2379764551aa0896ca9390919a69cc5812e2f889a315d"
CLAIM_LADDER_SHA256 = "22f51a6fefb2525e685b6938cc446fa658bdfb6e43157b5d2e6d5051f2212dfe"
SUBJECT_SCHEMA_SHA256 = "c6c317610958cb72f7370d6c2099b93dfebae77381381122aea70d960799e4ab"
LAUNCHER_SCHEMA_SHA256 = "897ea22dc64af59e787976e161e687a2b20b52a9ca16f8ef6c22bee8eeba5070"
CALL_PLAN_SCHEMA_SHA256 = "360ca3f54fa653c79550df61609dc14714d9f628f955376178d30bd75ff4e647"
HISTORICAL_TREE_SHA256 = "71dcc3bd6a391c80a38fbe504970ac5e0780be9deb3ef8fa2d07e0954044ae61"
HISTORICAL_TREE_COUNT = 128

HISTORICAL_FILES = {
    f"{SUITE_REL}/adjudication_rubric.md": V1_RUBRIC_SHA256,
    f"{SUITE_REL}/heldout_set.json":
        "4b2392e95ae7569907438d9e731ead8eb1db35489b0583a601631d22cdc4eb98",
    f"{SUITE_REL}/measurement-2026-07-22.json":
        "d0c7e5f53d21775d32fb820665cf17f6baec056262765767467e56d1e428bd1f",
    f"{SUITE_REL}/measurement-2026-08-07.json":
        "1af137c798e6cf3a5d0a742e379a8af78fe802cb924b4ece22cdf57cb881f573",
}
HISTORICAL_MEASUREMENTS = {
    "measurement-2026-07-22.json",
    "measurement-2026-08-07.json",
}
HISTORICAL_TREE_REL = f"{SUITE_REL}/runs/2026-08-07"
TREE_ALGORITHM = (
    "Recursively select regular files; use POSIX paths relative to this tree; "
    "sort paths by UTF-8 bytes; append for each file: relative-path UTF-8, "
    "one NUL byte, lowercase file sha256 ASCII, one LF byte; sha256 the "
    "concatenated bytes."
)

FIXTURE_HASHES = {
    "README.md": "660ad28ad484cec61aa3d7d5cb47c3119eb75b8a548f9de891e743497732e1c3",
    "subject_context_attested_only.json":
        "d8636dc2d8d8173300e04e211a2411a3e0b1cc644e73c0cf5bc46315b5ae7eca",
    "subject_context_machine_supported.json":
        "7263fd771706d8e407b8ff7f3750bb1558e4d75524f5454bbfeadfb67118f5bc",
    "subject_context_not_isolated.json":
        "24c5d462c9b0184ad2e719dd39cab99d2a08ca598f46ece706fff8e863d6bb5d",
    "subject_context_unknown.json":
        "8b470acdf748b629fefed542c1f3d5578eb72ec44423bf8a98c73fcb6a941727",
}
FIXTURE_STATUSES = {
    "subject_context_attested_only.json": "attested_only",
    "subject_context_machine_supported.json": "machine_supported",
    "subject_context_not_isolated.json": "not_isolated",
    "subject_context_unknown.json": "unknown",
}

ROOT_KEYS = {
    "schema_version", "suite", "run_id", "suite_commit", "execution_manifest",
    "subject_call_plan",
    "recorded_at", "status", "neutral_cwd", "cli", "instruction_visibility",
    "context_probe", "attestation", "data_minimization",
}
STATUS_VALUES = {"machine_supported", "attested_only", "not_isolated", "unknown"}
STATUS_CLAIMS = {
    "machine_supported": "repository-instruction isolated (machine-supported)",
    "attested_only": "repository-instruction isolated (operator-attested only)",
    "not_isolated": "repository-instruction isolation not established",
    "unknown": "repository-instruction isolation not established — evidence unknown",
}
JUDGE_SUBJECT_INPUT_SEPARATOR = b"\n\n--- ARS SUBJECT INPUT ---\n"
JUDGE_SUBJECT_OUTPUT_SEPARATOR = b"\n\n--- ARS SUBJECT OUTPUT ---\n"


class ContractError(ValueError):
    """A fail-closed #679 contract violation."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_object_sha256(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _strict_json(path: Path) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ContractError(f"{path}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    def bad_constant(value: str) -> Any:
        raise ContractError(f"{path}: non-finite JSON number {value}")

    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=pairs,
            parse_constant=bad_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"{path}: strict JSON parse failed: {exc}") from exc


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label}: expected JSON object")
    return value


def _closed_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ContractError(
            f"{label}: keys mismatch; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def _safe_file(root: Path, ref: str, label: str, prefix: str | None = None) -> Path:
    if not isinstance(ref, str) or not ref or "\\" in ref or "\x00" in ref:
        raise ContractError(f"{label}: invalid repository-relative path {ref!r}")
    parts = ref.split("/")
    if ref.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise ContractError(f"{label}: path traversal or non-canonical path {ref!r}")
    if prefix is not None and not ref.startswith(prefix):
        raise ContractError(f"{label}: path is outside required prefix {prefix!r}")

    current = root
    for index, part in enumerate(parts):
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise ContractError(f"{label}: missing/unreadable path {ref!r}: {exc}") from exc
        if stat.S_ISLNK(mode):
            raise ContractError(f"{label}: symlink component forbidden in {ref!r}")
        final = index == len(parts) - 1
        if final and not stat.S_ISREG(mode):
            raise ContractError(f"{label}: final path is not a regular file: {ref!r}")
        if not final and not stat.S_ISDIR(mode):
            raise ContractError(f"{label}: non-directory path component in {ref!r}")

    try:
        current.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise ContractError(f"{label}: path escapes repository root: {ref!r}") from exc
    return current


def _tree_inventory(root: Path, rel: str) -> tuple[int, str]:
    base = root.joinpath(*rel.split("/"))
    if base.is_symlink() or not base.is_dir():
        raise ContractError(f"historical tree is missing, symlinked, or not a directory: {rel}")
    rows: list[tuple[bytes, str]] = []
    for current, dirnames, filenames in os.walk(base, followlinks=False):
        current_path = Path(current)
        for name in list(dirnames):
            child = current_path / name
            mode = child.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise ContractError(f"historical tree contains forbidden directory entry: {child}")
        for name in filenames:
            child = current_path / name
            mode = child.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                raise ContractError(f"historical tree contains non-regular entry: {child}")
            relative = child.relative_to(base).as_posix()
            rows.append((relative.encode("utf-8"), _sha256(child)))
    rows.sort(key=lambda item: item[0])
    payload = b"".join(path + b"\0" + digest.encode("ascii") + b"\n" for path, digest in rows)
    return len(rows), hashlib.sha256(payload).hexdigest()


def _expected_lock() -> dict[str, Any]:
    return {
        "schema_version": "revision-claim-drift-historical-lock/1.0",
        "suite": "revision_claim_drift",
        "baseline_commit": "682b30a200951e058a7ac7848aab600959669198",
        "hash_algorithm": "sha256",
        "readme_exclusion": {
            "path": f"{SUITE_REL}/README.md",
            "reason": (
                "Issue #679 must document the prospective v2 context protocol; the README "
                "is not a scored row, frozen rubric, held-out item set, or retained raw run "
                "artifact."
            ),
        },
        "protected_files": [
            {"path": path, "sha256": digest}
            for path, digest in HISTORICAL_FILES.items()
        ],
        "protected_trees": [{
            "path": HISTORICAL_TREE_REL,
            "file_count": HISTORICAL_TREE_COUNT,
            "inventory_algorithm": TREE_ALGORITHM,
            "inventory_sha256": HISTORICAL_TREE_SHA256,
        }],
        "mutation_policy": "fail_closed",
    }


def _discover_contract_rows(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    """Find every exact or near-miss measurement marker under the suite.

    Discovery is recursive and filename-independent.  A future report cannot
    hide under ``runs/``, a nonstandard basename, a case-variant extension, or
    an escaped spelling of the decoded JSON member name.
    """
    suite_root = root / SUITE
    rows: list[tuple[Path, dict[str, Any]]] = []
    marker_hint = re.compile(r"measurement(?:_|\\u005[fF])contract")
    for current, dirnames, filenames in os.walk(suite_root, followlinks=False):
        current_path = Path(current)
        for name in list(dirnames):
            child = current_path / name
            mode = child.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise ContractError(
                    f"measurement discovery encountered forbidden directory entry: {child}"
                )
        for name in sorted(filenames):
            path = current_path / name
            if path.suffix.casefold() != ".json":
                continue
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                raise ContractError(
                    f"measurement discovery encountered non-regular JSON: {path}"
                )
            try:
                text = path.read_bytes().decode("utf-8")
            except (OSError, UnicodeError) as exc:
                raise ContractError(f"measurement discovery cannot read {path}: {exc}") from exc
            try:
                lenient = json.loads(text)
            except (ValueError, RecursionError) as exc:
                if marker_hint.search(text):
                    raise ContractError(
                        f"contract-marker JSON does not parse under discovery: {path}: {exc}"
                    ) from exc
                continue
            if not isinstance(lenient, dict) or "measurement_contract" not in lenient:
                continue
            value = lenient["measurement_contract"]
            if not isinstance(value, str) or not value.startswith("heldout-measurement/"):
                raise ContractError(
                    f"near-miss measurement_contract marker fails closed: {path}: {value!r}"
                )
            strict = _strict_json(path)
            if not isinstance(strict, dict):
                raise ContractError(f"contract-marked JSON root is not an object: {path}")
            rows.append((path, strict))
    return rows


def _check_history(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    lock_path = _safe_file(root, f"{SUITE_REL}/historical_artifacts.lock.json", "history lock")
    lock = _strict_json(lock_path)
    if lock != _expected_lock():
        raise ContractError("historical lock differs from hard-coded #679 lock semantics")
    for ref, expected in HISTORICAL_FILES.items():
        path = _safe_file(root, ref, "protected historical file")
        actual = _sha256(path)
        if actual != expected:
            raise ContractError(f"protected historical byte drift: {ref}: {actual} != {expected}")
    count, digest = _tree_inventory(root, HISTORICAL_TREE_REL)
    if (count, digest) != (HISTORICAL_TREE_COUNT, HISTORICAL_TREE_SHA256):
        raise ContractError(
            f"protected historical run-tree drift: count={count}, sha256={digest}"
        )
    measurements = {
        path.name
        for path in (root / SUITE).iterdir()
        if path.name.casefold().startswith("measurement-")
        and path.suffix.casefold() == ".json"
        and (path.is_file() or path.is_symlink())
    }
    if measurements != HISTORICAL_MEASUREMENTS:
        raise ContractError(
            "#679 creates no measurement row; expected only frozen historical rows, "
            f"found {sorted(measurements)}"
        )
    rows = _discover_contract_rows(root)
    expected_marked = {f"{SUITE_REL}/measurement-2026-08-07.json"}
    actual_marked = {path.relative_to(root).as_posix() for path, _ in rows}
    if actual_marked != expected_marked:
        raise ContractError(
            "#679 creates no contract-marked measurement row anywhere under the suite; "
            f"expected {sorted(expected_marked)}, found {sorted(actual_marked)}"
        )
    return rows


def _expected_amendments() -> dict[str, Any]:
    v1_path = f"{SUITE_REL}/adjudication_rubric.md"
    v2_path = f"{SUITE_REL}/adjudication_rubric_v2.md"
    rows = [
        f"{SUITE_REL}/measurement-2026-07-22.json",
        f"{SUITE_REL}/measurement-2026-08-07.json",
    ]
    return {
        "schema_version": "revision-claim-drift-rubric-amendments/1.0",
        "suite": "revision_claim_drift",
        "append_only": True,
        "rubrics": [
            {"version": "1.0", "path": v1_path, "sha256": V1_RUBRIC_SHA256,
             "status": "frozen_historical"},
            {"version": "2.0", "path": v2_path, "sha256": V2_RUBRIC_SHA256,
             "status": "prospective"},
        ],
        "amendments": [{
            "amendment_id": "RCD-RUBRIC-2026-08-10-001",
            "recorded_on": "2026-08-10",
            "issue": 679,
            "from_version": "1.0",
            "from_sha256": V1_RUBRIC_SHA256,
            "to_version": "2.0",
            "to_sha256": V2_RUBRIC_SHA256,
            "changes": [
                "add_C9_non_control_citation_attachment",
                "replace_ladder_examples_with_canonical_pointers",
            ],
            "historical_effect": "none",
            "historical_rows": rows,
            "rescoring_permitted": False,
        }],
    }


def _check_rubric(root: Path) -> None:
    v2_ref = f"{SUITE_REL}/adjudication_rubric_v2.md"
    v2_path = _safe_file(root, v2_ref, "v2 rubric")
    if _sha256(v2_path) != V2_RUBRIC_SHA256:
        raise ContractError("v2 rubric byte identity differs from frozen prospective hash")
    text = v2_path.read_text(encoding="utf-8")
    headings = re.findall(r"^### C([1-9])\s+—\s+(.+)$", text, flags=re.MULTILINE)
    if [number for number, _ in headings] != [str(value) for value in range(1, 10)]:
        raise ContractError("v2 rubric must contain exactly ordered criteria C1 through C9")
    if headings[-1][1].strip().casefold() != "non-control citation-attachment violation":
        raise ContractError("v2 rubric C9 title/authority drift")
    for marker in (
        "../../../shared/references/claim_strength_ladder.md#the-ladder",
        "../../../shared/references/claim_strength_ladder.md#what-counts-as-a-move-and-what-does-not",
        CLAIM_LADDER_SHA256,
        "Status: **prospective only**",
        "C9 is not a retroactive basis",
    ):
        if text.count(marker) != 1:
            raise ContractError(f"v2 rubric missing or duplicates frozen marker: {marker}")
    if any(arrow in text for arrow in ("→", "⇒", "->")):
        raise ContractError("v2 rubric must point to, not copy, local ladder-arrow examples")

    ladder_path = _safe_file(
        root,
        "shared/references/claim_strength_ladder.md",
        "canonical claim-strength ladder",
    )
    if _sha256(ladder_path) != CLAIM_LADDER_SHA256:
        raise ContractError("canonical claim-strength ladder target hash drifted")
    ladder_text = ladder_path.read_text(encoding="utf-8")
    if ladder_text.count("## The ladder") != 1 or ladder_text.count(
        "## What counts as a move (and what does not)"
    ) != 1:
        raise ContractError("canonical claim-strength ladder target headings drifted")

    ledger_path = _safe_file(root, f"{SUITE_REL}/rubric_amendments.json", "rubric ledger")
    ledger = _strict_json(ledger_path)
    if ledger != _expected_amendments():
        raise ContractError("rubric amendment ledger differs from frozen closed amendment")
    for item in ledger["rubrics"]:
        resolved = _safe_file(root, item["path"], "ledger rubric ref")
        if _sha256(resolved) != item["sha256"]:
            raise ContractError(f"ledger rubric hash mismatch: {item['path']}")


_RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$"
)


def _time(value: str, label: str) -> dt.datetime:
    if not isinstance(value, str) or not _RFC3339.fullmatch(value):
        raise ContractError(f"{label}: expected RFC 3339 date-time")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError as exc:
        raise ContractError(f"{label}: invalid RFC 3339 date-time") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{label}: date-time must carry an offset")
    return parsed


def _schema_validator(schema: Mapping[str, Any], label: str) -> Draft202012Validator:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema exposes version-specific subclasses.
        raise ContractError(f"{label}: invalid Draft 2020-12 schema: {exc}") from exc
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_subject_context(
    record: Mapping[str, Any], schema: Mapping[str, Any], label: str = "subject context"
) -> None:
    errors = sorted(_schema_validator(schema, "subject-context schema").iter_errors(record),
                    key=lambda error: tuple(str(part) for part in error.absolute_path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "<root>"
        raise ContractError(f"{label}.{location}: {first.message}")
    _closed_keys(record, ROOT_KEYS, label)
    if record["status"] not in STATUS_VALUES:
        raise ContractError(f"{label}: status is outside the frozen vocabulary")
    recorded = _time(record["recorded_at"], f"{label}.recorded_at")
    probe = record["context_probe"]
    if probe["started_at"] is not None:
        started = _time(probe["started_at"], f"{label}.context_probe.started_at")
        completed = _time(probe["completed_at"], f"{label}.context_probe.completed_at")
        if started > completed or completed > recorded:
            raise ContractError(f"{label}: probe timestamps are not start <= completion <= record")
    attestation = record["attestation"]
    if attestation is not None:
        attested = _time(attestation["attested_at"], f"{label}.attestation.attested_at")
        if attested > recorded:
            raise ContractError(f"{label}: attestation occurs after the record timestamp")
        if probe["completed_at"] is not None and attested < _time(
            probe["completed_at"], f"{label}.context_probe.completed_at"
        ):
            raise ContractError(f"{label}: attestation precedes completed context evidence")


def _pinned_schema(
    root: Path, ref: str, expected_sha256: str, label: str
) -> dict[str, Any]:
    path = _safe_file(root, ref, label)
    if _sha256(path) != expected_sha256:
        raise ContractError(f"{label} byte identity differs from frozen hash")
    schema = _require_object(_strict_json(path), label)
    _schema_validator(schema, label)
    return schema


def _check_subject_assets(
    root: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, dict[str, Any]],
]:
    schema_ref = f"{SUITE_REL}/subject_context_record.schema.json"
    schema = _pinned_schema(
        root, schema_ref, SUBJECT_SCHEMA_SHA256, "subject-context schema"
    )
    launcher_schema = _pinned_schema(
        root,
        f"{SUITE_REL}/subject_launcher_config.schema.json",
        LAUNCHER_SCHEMA_SHA256,
        "subject-launcher-config schema",
    )
    call_plan_schema = _pinned_schema(
        root,
        f"{SUITE_REL}/subject_call_plan.schema.json",
        CALL_PLAN_SCHEMA_SHA256,
        "subject-call-plan schema",
    )
    if set(schema.get("required", [])) != ROOT_KEYS or set(schema.get("properties", {})) != ROOT_KEYS:
        raise ContractError("subject-context schema root keys differ from the frozen closed grammar")
    status_enum = set(schema["properties"]["status"].get("enum", []))
    if status_enum != STATUS_VALUES:
        raise ContractError("subject-context schema status vocabulary drift")

    fixture_dir = root / "scripts/fixtures/revision_claim_drift_v2"
    actual_files = {path.name for path in fixture_dir.iterdir() if path.is_file() or path.is_symlink()}
    if actual_files != set(FIXTURE_HASHES):
        raise ContractError(f"subject-context fixture inventory drift: {sorted(actual_files)}")
    records: dict[str, dict[str, Any]] = {}
    for name, expected_hash in FIXTURE_HASHES.items():
        rel = f"scripts/fixtures/revision_claim_drift_v2/{name}"
        path = _safe_file(root, rel, "subject-context fixture")
        if _sha256(path) != expected_hash:
            raise ContractError(f"subject-context fixture byte drift: {name}")
        if name.endswith(".json"):
            record = _require_object(_strict_json(path), name)
            validate_subject_context(record, schema, name)
            if record["status"] != FIXTURE_STATUSES[name]:
                raise ContractError(f"{name}: fixture/status mapping drift")
            records[name] = record

    # The four checked-in fixtures cover the four public statuses.  These
    # derived positive relations pin two additional truthful not-isolated
    # routes without turning them into reusable run artifacts.
    inside = copy.deepcopy(records["subject_context_machine_supported.json"])
    inside["status"] = "not_isolated"
    inside["neutral_cwd"]["repo_membership_probe"] = "inside_suite_repository"
    validate_subject_context(inside, schema, "derived inside-repository record")

    repository_visible = copy.deepcopy(records["subject_context_unknown.json"])
    repository_visible["status"] = "not_isolated"
    repository_visible["neutral_cwd"]["repo_membership_probe"] = (
        "outside_suite_repository"
    )
    repository_visible["instruction_visibility"]["repository_instructions"] = (
        "visible"
    )
    validate_subject_context(
        repository_visible, schema, "derived repository-visible record"
    )
    return schema, launcher_schema, call_plan_schema, records


def _run_artifact_ref(run_id: str, filename: str) -> str:
    return f"{RUNS_PREFIX}{run_id}/{filename}"


def _validate_launcher_binding(
    root: Path,
    record: Mapping[str, Any],
    config: Mapping[str, Any],
    raw_paths: list[str],
    launcher_schema: Mapping[str, Any],
) -> dict[str, Any]:
    context_binding = record["cli"]["launcher_config"]
    row_binding = config.get("launcher_config")
    if not isinstance(row_binding, Mapping):
        raise ContractError("subject.config.launcher_config binding is required")
    _closed_keys(row_binding, {"ref", "sha256"}, "subject.config.launcher_config")
    if dict(row_binding) != context_binding:
        raise ContractError("row/context launcher_config binding mismatch")
    expected_ref = _run_artifact_ref(record["run_id"], "launcher-config.json")
    if context_binding["ref"] != expected_ref:
        raise ContractError("launcher-config ref is not the canonical run sibling")
    path = _safe_file(root, expected_ref, "launcher-config artifact", RUNS_PREFIX)
    if _sha256(path) != context_binding["sha256"]:
        raise ContractError("launcher-config artifact hash mismatch")
    if expected_ref not in raw_paths:
        raise ContractError("launcher-config ref must appear in raw_outputs.paths")
    artifact = _require_object(_strict_json(path), "launcher-config artifact")
    errors = list(
        _schema_validator(launcher_schema, "subject-launcher-config schema").iter_errors(
            artifact
        )
    )
    if errors:
        raise ContractError(f"launcher-config artifact fails schema: {errors[0].message}")
    if artifact["suite"] != record["suite"] or artifact["run_id"] != record["run_id"]:
        raise ContractError("launcher-config suite/run_id mismatch")
    invocation = {
        key: artifact[key]
        for key in ("launcher", "working_directory", "instruction_loading")
    }
    if artifact["invocation_sha256"] != _canonical_object_sha256(invocation):
        raise ContractError("launcher-config invocation hash mismatch")
    for key in ("mode", "bare_requested", "bare_used", "authentication_result"):
        if artifact["launcher"][key] != record["cli"][key]:
            raise ContractError(f"launcher-config/context CLI {key} mismatch")
    membership_to_policy = {
        "outside_suite_repository": "fresh_outside_suite_repository",
        "inside_suite_repository": "inside_suite_repository",
        "unresolved": "unresolved",
    }
    if artifact["working_directory"]["policy"] != membership_to_policy[
        record["neutral_cwd"]["repo_membership_probe"]
    ]:
        raise ContractError("launcher-config/context working-directory policy mismatch")
    if artifact["working_directory"]["pwd_p_sha256"] != record["neutral_cwd"][
        "pwd_p_sha256"
    ]:
        raise ContractError("launcher-config/context pwd -P hash mismatch")
    sealed_at = _time(artifact["sealed_at"], "launcher_config.sealed_at")
    probe_started_at = record["context_probe"]["started_at"]
    launcher_deadline = _time(
        probe_started_at if probe_started_at is not None else record["recorded_at"],
        "launcher-config preflight deadline",
    )
    if sealed_at > launcher_deadline:
        raise ContractError("launcher-config artifact was not sealed before probe/preflight")
    return artifact


def _validate_call_plan_binding(
    root: Path,
    report: Mapping[str, Any],
    record: Mapping[str, Any],
    config: Mapping[str, Any],
    raw_paths: list[str],
    call_plan_schema: Mapping[str, Any],
) -> dict[str, Any]:
    context_binding = record["subject_call_plan"]
    row_binding = config.get("subject_call_plan")
    if not isinstance(row_binding, Mapping):
        raise ContractError("subject.config.subject_call_plan binding is required")
    _closed_keys(row_binding, {"ref", "sha256"}, "subject.config.subject_call_plan")
    if dict(row_binding) != context_binding:
        raise ContractError("row/context subject_call_plan binding mismatch")
    expected_ref = _run_artifact_ref(record["run_id"], "subject-call-plan.json")
    if context_binding["ref"] != expected_ref:
        raise ContractError("subject-call-plan ref is not the canonical run sibling")
    path = _safe_file(root, expected_ref, "subject-call-plan artifact", RUNS_PREFIX)
    if _sha256(path) != context_binding["sha256"]:
        raise ContractError("subject-call-plan artifact hash mismatch")
    if expected_ref not in raw_paths:
        raise ContractError("subject-call-plan ref must appear in raw_outputs.paths")
    plan = _require_object(_strict_json(path), "subject-call-plan artifact")
    errors = list(
        _schema_validator(call_plan_schema, "subject-call-plan schema").iter_errors(plan)
    )
    if errors:
        raise ContractError(f"subject-call-plan artifact fails schema: {errors[0].message}")
    if (
        plan["suite"] != record["suite"]
        or plan["run_id"] != record["run_id"]
        or plan["suite_commit"] != record["suite_commit"]
        or plan["subject_model_id"] != report.get("subject", {}).get("model_id")
        or plan["launcher_config"] != record["cli"]["launcher_config"]
    ):
        raise ContractError("subject-call-plan provenance differs from context record")
    plan_created = _time(plan["created_at"], "subject_call_plan.created_at")
    probe_started_at = record["context_probe"]["started_at"]
    plan_deadline = _time(
        probe_started_at if probe_started_at is not None else record["recorded_at"],
        "subject-call plan preflight deadline",
    )
    if plan_created > plan_deadline:
        raise ContractError("subject-call plan was not frozen before probe/preflight")
    launcher_path = _safe_file(
        root,
        plan["launcher_config"]["ref"],
        "subject-call-plan launcher config",
        RUNS_PREFIX,
    )
    launcher_artifact = _require_object(
        _strict_json(launcher_path), "subject-call-plan launcher config"
    )
    if _time(launcher_artifact["sealed_at"], "launcher_config.sealed_at") > plan_created:
        raise ContractError("launcher config was not sealed before the subject-call plan")

    heldout_binding = plan["heldout_set"]
    expected_heldout_ref = f"{SUITE_REL}/heldout_set.json"
    if heldout_binding != {
        "ref": expected_heldout_ref,
        "sha256": HISTORICAL_FILES[expected_heldout_ref],
    }:
        raise ContractError("subject-call plan does not bind the frozen held-out set")
    heldout = _require_object(
        _strict_json(_safe_file(root, expected_heldout_ref, "frozen held-out set")),
        "frozen held-out set",
    )
    item_rows = heldout.get("items")
    if not isinstance(item_rows, list):
        raise ContractError("frozen held-out set has no item roster")
    item_ids = [item.get("id") if isinstance(item, Mapping) else None for item in item_rows]
    expected_item_ids = [f"rp-{index:02d}" for index in range(1, 9)]
    if item_ids != expected_item_ids:
        raise ContractError("frozen held-out item roster differs from rp-01 through rp-08")
    control_ids = {"rp-07", "rp-08"}

    arm_ids = plan["arm_ids"]
    if arm_ids != sorted(set(arm_ids)):
        raise ContractError("subject-call-plan arm_ids must be sorted and unique")
    result_arm_ids = (
        report.get("results", {})
        .get("revision_claim_drift_v2", {})
        .get("arm_ids")
    )
    if result_arm_ids != arm_ids:
        raise ContractError("subject-call plan arm_ids differ from the published v2 layer")
    arm_roles = report.get("results", {}).get("arm_roles", {})
    treatment_arms = arm_roles.get("treatment_or_cohort_arms", [])
    variant_arms = arm_roles.get("variant_packet_arms", [])
    if (
        not isinstance(treatment_arms, list)
        or not isinstance(variant_arms, list)
        or treatment_arms != sorted(set(treatment_arms))
        or variant_arms != sorted(set(variant_arms))
        or set(treatment_arms).intersection(variant_arms)
        or sorted(treatment_arms + variant_arms) != arm_ids
    ):
        raise ContractError("published arm roles do not exactly partition call-plan arm_ids")
    replicate_count = report.get("replicates", {}).get("per_item")
    if (
        not isinstance(replicate_count, int)
        or isinstance(replicate_count, bool)
        or not 2 <= replicate_count <= 10
    ):
        raise ContractError("future #679 rows require 2..10 replicates per item and arm")

    expected_subjects = [
        {
            "item_id": item_id,
            "item_replicate_id": f"{item_id}.{arm_id}.r{replicate_index}",
            "replicate_index": replicate_index,
            "arm_id": arm_id,
            "control_item": item_id in control_ids,
        }
        for item_id in item_ids
        for arm_id in arm_ids
        for replicate_index in range(1, replicate_count + 1)
    ]

    calls = plan["calls"]
    indexes = [call["sequence_index"] for call in calls]
    if indexes != list(range(1, len(calls) + 1)):
        raise ContractError("subject-call-plan sequence indexes must be ordered 1..N")
    call_ids = [call["call_id"] for call in calls]
    item_replicates = [call["item_replicate_id"] for call in calls if call["role"] == "subject"]
    if len(call_ids) != len(set(call_ids)):
        raise ContractError("subject-call-plan call_id values must be unique")
    if not item_replicates or len(item_replicates) != len(set(item_replicates)):
        raise ContractError("subject calls must name unique non-empty item-replicates")

    subject_calls = [call for call in calls if call["role"] == "subject"]
    if len(subject_calls) != len(expected_subjects):
        raise ContractError("subject-call plan does not exactly cover item x arm x replicate")
    for call, expected in zip(subject_calls, expected_subjects, strict=True):
        item_replicate_id = expected["item_replicate_id"]
        expected_call_id = f"subject.{item_replicate_id}"
        if (
            call["call_id"] != expected_call_id
            or call["judge_id"] is not None
            or any(call[key] != value for key, value in expected.items())
        ):
            raise ContractError("subject-call roster differs from the frozen run design")

    subject_by_replicate = {call["item_replicate_id"]: call for call in subject_calls}
    judge_rows = report.get("judges", [])
    judge_ids = [judge.get("judge_id") for judge in judge_rows]
    plan_judges = plan["judges"]
    plan_judge_ids = [judge["judge_id"] for judge in plan_judges]
    if (
        not judge_ids
        or not all(isinstance(judge_id, str) and judge_id for judge_id in judge_ids)
        or judge_ids != sorted(set(judge_ids))
        or not 2 <= len(judge_ids) <= 8
        or judge_ids != plan_judge_ids
    ):
        raise ContractError("future #679 row and call plan require the same 2..8 sorted judges")
    if (
        report.get("suite_class") != "llm_judged"
        or report.get("decision_relevant") is not True
        or report.get("judge_plan") != {"exception": "none"}
    ):
        raise ContractError("future #679 rows are decision-relevant with no judge exception")
    model_families = [judge.get("model_family") for judge in judge_rows]
    if (
        not all(isinstance(family, str) and family for family in model_families)
        or len(set(model_families)) < 2
    ):
        raise ContractError("future #679 rows require at least two judge model families")
    required_blinding = ["arm_identity", "control_status", "mechanism_state"]
    if any(judge.get("blinded_to") != required_blinding for judge in judge_rows):
        raise ContractError("future #679 judges must use the frozen blinding dimensions")
    for plan_judge, row_judge in zip(plan_judges, judge_rows, strict=True):
        if any(
            row_judge.get(key) != plan_judge[key]
            for key in ("judge_id", "model_id", "model_family", "blinded_to")
        ) or row_judge.get("prompt_ref") != plan_judge["prompt_template"]["ref"]:
            raise ContractError("published judge identity/template differs from call plan")
        template_ref = plan_judge["prompt_template"]["ref"]
        expected_template_ref = (
            f"{RUNS_PREFIX}{record['run_id']}/raw/"
            f"judge.{plan_judge['judge_id']}.template.txt"
        )
        if template_ref != expected_template_ref:
            raise ContractError("judge prompt-template ref is not canonical")
        template_path = _safe_file(
            root,
            template_ref,
            "judge prompt template",
            f"{RUNS_PREFIX}{record['run_id']}/",
        )
        if _sha256(template_path) != plan_judge["prompt_template"]["sha256"]:
            raise ContractError("judge prompt-template hash mismatch")
        if template_ref not in raw_paths:
            raise ContractError("judge prompt-template ref must appear in raw_outputs.paths")
    plan_judge_by_id = {judge["judge_id"]: judge for judge in plan_judges}
    expected_judges = [
        {
            **subject,
            "call_id": f"judge.{judge_id}.{subject['item_replicate_id']}",
            "judge_id": judge_id,
        }
        for judge_id in judge_ids
        for subject in expected_subjects
    ]
    judge_calls = [call for call in calls if call["role"] == "judge"]
    if len(judge_calls) != len(expected_judges):
        raise ContractError("subject-call plan does not exactly cover judge x item-replicate")
    for call, expected in zip(judge_calls, expected_judges, strict=True):
        if call["call_id"] != expected["call_id"] or any(
            call[key] != expected[key]
            for key in (
                "judge_id",
                "item_id",
                "item_replicate_id",
                "replicate_index",
                "arm_id",
                "control_item",
            )
        ):
            raise ContractError("judge-call roster differs from the frozen run design")
    expected_call_ids = [
        f"subject.{subject['item_replicate_id']}" for subject in expected_subjects
    ] + [judge["call_id"] for judge in expected_judges]
    if call_ids != expected_call_ids:
        raise ContractError("subject-call-plan global order must be subjects then judges")

    judge_pairs: set[tuple[str, str]] = set()
    prompt_refs: set[str] = set()
    output_refs: set[str] = set()
    run_prefix = f"{RUNS_PREFIX}{record['run_id']}/"
    for index, call in enumerate(calls):
        prompt = call["prompt"]
        prompt_ref = prompt["ref"]
        output_ref = call["output_ref"]
        expected_prompt_ref = f"{run_prefix}raw/{call['call_id']}.prompt.txt"
        expected_output_ref = f"{run_prefix}raw/{call['call_id']}.output.txt"
        if prompt_ref != expected_prompt_ref or output_ref != expected_output_ref:
            raise ContractError("subject-call-plan prompt/output ref is not canonical")
        if prompt_ref in prompt_refs or output_ref in output_refs:
            raise ContractError("subject-call-plan prompt/output refs must be unique")
        prompt_refs.add(prompt_ref)
        output_refs.add(output_ref)
        prompt_path = _safe_file(root, prompt_ref, f"call-plan prompt[{index}]", run_prefix)
        _safe_file(root, output_ref, f"call-plan output[{index}]", run_prefix)
        if call["role"] == "subject":
            if _sha256(prompt_path) != prompt["sha256"]:
                raise ContractError("subject-call-plan subject prompt hash mismatch")
        else:
            expected_template_ref = plan_judge_by_id[call["judge_id"]][
                "prompt_template"
            ]["ref"]
            expected_subject_prompt_ref = subject_by_replicate[
                call["item_replicate_id"]
            ]["prompt"]["ref"]
            expected_subject_output_ref = subject_by_replicate[
                call["item_replicate_id"]
            ]["output_ref"]
            expected_deferred = {
                "ref": expected_prompt_ref,
                "sha256": None,
                "composition": "template_then_subject_input_then_subject_output/1.0",
                "template_ref": expected_template_ref,
                "subject_prompt_ref": expected_subject_prompt_ref,
                "subject_output_ref": expected_subject_output_ref,
            }
            if prompt != expected_deferred:
                raise ContractError("judge prompt dependency differs from frozen plan")
            template_path = _safe_file(
                root,
                expected_template_ref,
                "judge prompt template dependency",
                run_prefix,
            )
            subject_output_path = _safe_file(
                root,
                expected_subject_output_ref,
                "judge subject-output dependency",
                run_prefix,
            )
            subject_prompt_path = _safe_file(
                root,
                expected_subject_prompt_ref,
                "judge subject-input dependency",
                run_prefix,
            )
            expected_prompt_bytes = (
                template_path.read_bytes()
                + JUDGE_SUBJECT_INPUT_SEPARATOR
                + subject_prompt_path.read_bytes()
                + JUDGE_SUBJECT_OUTPUT_SEPARATOR
                + subject_output_path.read_bytes()
            )
            if prompt_path.read_bytes() != expected_prompt_bytes:
                raise ContractError(
                    "judge prompt bytes do not replay template + subject input + subject output"
                )
        if prompt_ref not in raw_paths or output_ref not in raw_paths:
            raise ContractError("every planned prompt/output ref must be retained raw")
        if call["role"] == "judge":
            pair = (call["judge_id"], call["item_replicate_id"])
            if pair in judge_pairs:
                raise ContractError("duplicate judge/item call in subject-call plan")
            judge_pairs.add(pair)
            subject = subject_by_replicate.get(call["item_replicate_id"])
            if subject is None:
                raise ContractError("judge call names an unplanned subject item-replicate")
            for key in ("item_id", "replicate_index", "arm_id", "control_item"):
                if call[key] != subject[key]:
                    raise ContractError(f"judge/subject call-plan {key} mismatch")

    reported_judge_pairs = [
        (judge["judge_id"], item["item_id"])
        for judge in report.get("judges", [])
        for item in judge.get("per_item", [])
    ]
    if len(reported_judge_pairs) != len(set(reported_judge_pairs)):
        raise ContractError("prospective row contains duplicate judge/item results")
    expected_judge_pairs = set(reported_judge_pairs)
    if judge_pairs != expected_judge_pairs:
        raise ContractError("subject-call plan does not exactly cover every judge/item pair")
    for judge in report.get("judges", []):
        for item in judge.get("per_item", []):
            raw_c9 = item.get("citation_attachment")
            if not isinstance(raw_c9, Mapping):
                raise ContractError("every raw judge/item row requires a typed C9 verdict")
            _closed_keys(
                raw_c9,
                {"criterion", "flag"},
                "raw judge/item citation_attachment",
            )
            if raw_c9["criterion"] != "C9" or not isinstance(raw_c9["flag"], bool):
                raise ContractError("raw judge/item C9 verdict must be criterion C9 + boolean flag")
    return plan


def _check_manifest_binding(
    root: Path,
    record: Mapping[str, Any],
    row_manifest: Mapping[str, Any],
    plan: Mapping[str, Any],
    raw_paths: list[str],
) -> dict[str, Any]:
    binding = record["execution_manifest"]
    ref = binding["ref"]
    path = _safe_file(root, ref, "subject-context execution manifest", RUNS_PREFIX)
    if row_manifest.get("ref") != ref:
        raise ContractError("row/context execution-manifest ref mismatch")
    if ref != _run_artifact_ref(record["run_id"], "execution-manifest.json"):
        raise ContractError("execution-manifest ref is not the canonical run sibling")
    if _sha256(path) != row_manifest.get("sha256"):
        raise ContractError("row execution-manifest hash mismatch")
    if ref not in raw_paths:
        raise ContractError("execution-manifest ref must appear in raw_outputs.paths")
    parts = ref.split("/")
    if len(parts) < 2 or parts[-2] != record["run_id"]:
        raise ContractError("subject-context run_id does not match manifest parent directory")
    manifest = _require_object(_strict_json(path), "execution manifest")
    schema_path = _safe_file(root, "evals/heldout/execution_manifest.schema.json",
                             "execution-manifest schema")
    manifest_schema = _require_object(_strict_json(schema_path), "execution-manifest schema")
    errors = list(_schema_validator(manifest_schema, "execution-manifest schema").iter_errors(manifest))
    if errors:
        raise ContractError(f"bound execution manifest fails schema: {errors[0].message}")
    if manifest["suite"] != record["suite"]:
        raise ContractError("subject-context and execution manifest suite mismatch")
    calls = manifest["calls"]
    planned_calls = plan["calls"]
    if len(calls) != len(planned_calls):
        raise ContractError("execution manifest does not exactly cover the call plan")
    indexes = [call["sequence_index"] for call in calls]
    if indexes != list(range(1, len(calls) + 1)):
        raise ContractError("execution-manifest sequence indexes must be ordered 1..N")
    call_ids = [call["call_id"] for call in calls]
    if len(call_ids) != len(set(call_ids)):
        raise ContractError("execution-manifest call_id values must be unique")
    starts: list[dt.datetime] = []
    completions: list[dt.datetime] = []
    subject_starts: list[dt.datetime] = []
    subject_completions: list[dt.datetime] = []
    judge_starts: list[dt.datetime] = []
    for index, (call, planned) in enumerate(zip(calls, planned_calls, strict=True)):
        planned_prompt_path = _safe_file(
            root,
            planned["prompt"]["ref"],
            f"executed prompt[{index}]",
            f"{RUNS_PREFIX}{record['run_id']}/",
        )
        if (
            call["call_id"] != planned["call_id"]
            or call["sequence_index"] != planned["sequence_index"]
            or call["prompt_sha256"] != _sha256(planned_prompt_path)
        ):
            raise ContractError("execution-manifest call differs from precommitted call plan")
        output_path = _safe_file(
            root,
            planned["output_ref"],
            f"executed output[{index}]",
            f"{RUNS_PREFIX}{record['run_id']}/",
        )
        if _sha256(output_path) != call["output_sha256"]:
            raise ContractError("execution-manifest output hash differs from retained bytes")
        started = _time(call["started_at"], f"execution_manifest.calls[{index}].started_at")
        completed = _time(call["completed_at"], f"execution_manifest.calls[{index}].completed_at")
        if started > completed:
            raise ContractError("execution-manifest call completes before it starts")
        starts.append(started)
        completions.append(completed)
        if planned["role"] == "subject":
            subject_starts.append(started)
            subject_completions.append(completed)
        else:
            judge_starts.append(started)
    if _time(manifest["created_at"], "execution_manifest.created_at") < max(completions):
        raise ContractError("execution manifest was recorded before its final call completed")
    if "execution_window" in manifest:
        window = manifest["execution_window"]
        if window["window_id"] != record["run_id"]:
            raise ContractError("execution-window ID and subject-context run_id mismatch")
        window_start = _time(window["started_at"], "execution_window.started_at")
        window_end = _time(window["completed_at"], "execution_window.completed_at")
        if window_start > min(starts) or window_end < max(completions) or window_start > window_end:
            raise ContractError("execution window does not contain all calls")
        if _time(manifest["created_at"], "execution_manifest.created_at") < window_end:
            raise ContractError("execution manifest was recorded before its window ended")
    if any(later < earlier for earlier, later in zip(starts, starts[1:])):
        raise ContractError("execution-manifest calls are not chronological by plan order")
    if judge_starts and min(judge_starts) < max(subject_completions):
        raise ContractError("judge calls began before the subject fleet completed")
    first_call_start = min(starts)
    if _time(record["recorded_at"], "subject_context.recorded_at") > first_call_start:
        raise ContractError("subject-context gate was not sealed before the first planned call")
    probe_completed = record["context_probe"]["completed_at"]
    if probe_completed is not None and _time(probe_completed, "context_probe.completed_at") > first_call_start:
        raise ContractError("context probe was not completed before the first planned call")
    attestation = record["attestation"]
    if attestation is not None and _time(attestation["attested_at"], "attestation.attested_at") > first_call_start:
        raise ContractError("operator attestation was not recorded before the first planned call")
    return manifest


def _walk_strings(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_strings(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{path}[{index}]")


def _walk_keys(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield f"{path}.<key:{key}>", str(key)
            yield from _walk_keys(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{path}[{index}]")


def _check_claim_language(report: Mapping[str, Any], status: str) -> None:
    expected = STATUS_CLAIMS[status]
    actual = report.get("results", {}).get("subject_context_claim")
    if actual != expected:
        raise ContractError(
            "results.subject_context_claim must be the exact status-derived ceiling"
        )
    for location, value in _walk_strings(report):
        if location == "$.results.subject_context_claim":
            continue
        lowered = value.casefold()
        if (
            "clean context" in lowered
            or "prompt isolation" in lowered
            or re.search(r"\b(?:isolated|isolation)\b", lowered)
        ):
            raise ContractError(
                f"{location}: isolation wording is allowed only in the exact derived field"
            )
    for location, key in _walk_keys(report):
        normalized = re.sub(r"[_\-/]+", " ", key.casefold())
        if (
            "clean context" in normalized
            or "prompt isolation" in normalized
            or re.search(r"\b(?:isolated|isolation)\b", normalized)
        ):
            raise ContractError(
                f"{location}: claim-shaped isolation keys are forbidden"
            )


def validate_prospective_measurement(
    report: Mapping[str, Any], root: Path, schema: Mapping[str, Any] | None = None
) -> None:
    """Replay #679 bindings for a future heldout-measurement/1.1 row."""
    measurement_schema_path = _safe_file(
        root,
        "evals/heldout/measurement_report.schema.json",
        "measurement-report schema",
    )
    measurement_schema = _require_object(
        _strict_json(measurement_schema_path), "measurement-report schema"
    )
    measurement_errors = sorted(
        _schema_validator(
            measurement_schema, "measurement-report schema"
        ).iter_errors(report),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if measurement_errors:
        first = measurement_errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "<root>"
        raise ContractError(f"prospective measurement.{location}: {first.message}")
    if report.get("measurement_contract") != "heldout-measurement/1.1":
        raise ContractError("prospective row must use heldout-measurement/1.1")
    if report.get("suite") != "revision_claim_drift":
        raise ContractError("prospective row suite mismatch")
    try:
        config = report["subject"]["config"]
        binding = config["subject_context"]
    except (KeyError, TypeError) as exc:
        raise ContractError("missing subject.config.subject_context binding") from exc
    _closed_keys(
        config,
        {"suite_commit", "subject_context", "launcher_config", "subject_call_plan"},
        "subject.config",
    )
    _closed_keys(binding, {"ref", "sha256", "status"}, "subject.config.subject_context")
    if binding["status"] not in STATUS_VALUES:
        raise ContractError("subject-context binding has unknown status")
    ref = binding["ref"]
    context_path = _safe_file(root, ref, "subject-context row ref", RUNS_PREFIX)
    parts = ref.split("/")
    if parts[-1] != "subject-context.json":
        raise ContractError("subject-context ref must end in subject-context.json")
    if _sha256(context_path) != binding["sha256"]:
        raise ContractError("subject-context row hash mismatch")
    if schema is None:
        schema = _pinned_schema(
            root,
            f"{SUITE_REL}/subject_context_record.schema.json",
            SUBJECT_SCHEMA_SHA256,
            "subject-context schema",
        )
    launcher_schema = _pinned_schema(
        root,
        f"{SUITE_REL}/subject_launcher_config.schema.json",
        LAUNCHER_SCHEMA_SHA256,
        "subject-launcher-config schema",
    )
    call_plan_schema = _pinned_schema(
        root,
        f"{SUITE_REL}/subject_call_plan.schema.json",
        CALL_PLAN_SCHEMA_SHA256,
        "subject-call-plan schema",
    )
    record = _require_object(_strict_json(context_path), "bound subject-context record")
    validate_subject_context(record, schema, "bound subject-context record")
    if ref != _run_artifact_ref(record["run_id"], "subject-context.json"):
        raise ContractError("subject-context ref is not the canonical run sibling")
    if binding["status"] != record["status"]:
        raise ContractError("subject-context binding status differs from record")
    if config.get("suite_commit") != record["suite_commit"]:
        raise ContractError("subject.config.suite_commit differs from context record")
    raw_paths = report.get("raw_outputs", {}).get("paths", [])
    if not isinstance(raw_paths, list) or not all(isinstance(path, str) for path in raw_paths):
        raise ContractError("raw_outputs.paths must be a string array")
    if len(raw_paths) != len(set(raw_paths)):
        raise ContractError("raw_outputs.paths must not contain duplicate refs")
    for index, raw_ref in enumerate(raw_paths):
        _safe_file(root, raw_ref, f"raw_outputs.paths[{index}]")
    if ref not in raw_paths:
        raise ContractError("subject-context ref must appear verbatim in raw_outputs.paths")
    _validate_launcher_binding(root, record, config, raw_paths, launcher_schema)
    plan = _validate_call_plan_binding(
        root, report, record, config, raw_paths, call_plan_schema
    )
    row_manifest = report.get("execution_manifest")
    if not isinstance(row_manifest, Mapping):
        raise ContractError("prospective row lacks execution_manifest binding")
    _closed_keys(
        row_manifest,
        {"ref", "sha256", "write_once", "claims"},
        "execution_manifest",
    )
    if row_manifest.get("ref") != record["execution_manifest"]["ref"]:
        raise ContractError("row/context execution_manifest ref mismatch")
    _check_manifest_binding(root, record, row_manifest, plan, raw_paths)
    expected_ref = f"{SUITE_REL}/adjudication_rubric_v2.md"
    adjudication = report.get("adjudication", {})
    prereg = report.get("preregistration", {})
    for label, value in (("adjudication", adjudication), ("preregistration", prereg)):
        if value.get("rubric_ref") != expected_ref or value.get("rubric_sha256") != V2_RUBRIC_SHA256:
            raise ContractError(f"{label}: prospective row did not opt into the frozen v2 rubric")
    if prereg.get("frozen_commit") != record["suite_commit"]:
        raise ContractError("preregistration frozen_commit differs from context record")
    if (
        prereg.get("plan_ref") != config["subject_call_plan"]["ref"]
        or prereg.get("plan_sha256") != config["subject_call_plan"]["sha256"]
    ):
        raise ContractError("preregistration plan binding differs from subject-call plan")
    if adjudication.get("resolution_direction") != "flags_only":
        raise ContractError("v2 adjudication resolution_direction must be flags_only")
    headline = report.get("aggregate", {}).get("headline", {})
    headline_value = headline.get("value")
    expected_headline = {
        "metric_name": "claim_strength_hedge_drift_rate",
        "value": headline_value,
        "construction_rule": (
            "Confirmed C1/C2 item-replicate flags divided by evaluated "
            "item-replicates; flags-only adjudication makes this a lower bound."
        ),
        "estimand_status": "lower_bound",
    }
    if (
        headline != expected_headline
        or not isinstance(headline_value, (int, float))
        or isinstance(headline_value, bool)
        or not 0 <= headline_value <= 1
    ):
        raise ContractError("aggregate headline must be the closed C1/C2 lower-bound layer")
    subject_calls = [call for call in plan["calls"] if call["role"] == "subject"]
    expected_evaluated = sorted(call["item_replicate_id"] for call in subject_calls)
    expected_controls = sorted(
        call["item_replicate_id"] for call in subject_calls if call["control_item"]
    )
    expected_v2_results = {
        "rubric_version": "2.0",
        "claim_strength_headline_criteria": ["C1", "C2"],
        "deterministic_token_criterion": "C6",
        "arm_ids": plan["arm_ids"],
        "citation_attachment": {
            "criterion": "C9",
            "scope": "all_items_including_non_controls",
            "reported_separately": True,
            "evaluated_item_replicates": expected_evaluated,
            "control_item_replicates": expected_controls,
            "finding_count": report.get("results", {})
            .get("revision_claim_drift_v2", {})
            .get("citation_attachment", {})
            .get("finding_count"),
            "decisions": report.get("results", {})
            .get("revision_claim_drift_v2", {})
            .get("citation_attachment", {})
            .get("decisions"),
            "findings": report.get("results", {})
            .get("revision_claim_drift_v2", {})
            .get("citation_attachment", {})
            .get("findings"),
        },
    }
    actual_v2_results = report.get("results", {}).get("revision_claim_drift_v2")
    if actual_v2_results != expected_v2_results:
        raise ContractError("prospective row lacks the closed separate C9 result binding")
    citation_layer = expected_v2_results["citation_attachment"]
    evaluated = citation_layer["evaluated_item_replicates"]
    controls = citation_layer["control_item_replicates"]
    decisions = citation_layer["decisions"]
    findings = citation_layer["findings"]
    if (
        not evaluated
        or not isinstance(controls, list)
        or len(controls) != len(set(controls))
        or not set(controls).issubset(evaluated)
        or set(controls) == set(evaluated)
    ):
        raise ContractError(
            "C9 coverage must include every judged item-replicate and at least one non-control"
        )
    if (
        not isinstance(citation_layer["finding_count"], int)
        or isinstance(citation_layer["finding_count"], bool)
        or not isinstance(findings, list)
        or citation_layer["finding_count"] != len(findings)
    ):
        raise ContractError("C9 finding_count must equal the findings list length")
    judge_rows = report.get("judges", [])
    judge_ids = [judge.get("judge_id") for judge in judge_rows]
    if (
        not judge_ids
        or not all(isinstance(judge_id, str) and judge_id for judge_id in judge_ids)
        or len(judge_ids) != len(set(judge_ids))
    ):
        raise ContractError("prospective row judge_id values must be non-empty and unique")
    reported_judges = {judge["judge_id"]: judge for judge in judge_rows}
    raw_true_pairs = sorted(
        (judge["judge_id"], item["item_id"])
        for judge in judge_rows
        for item in judge.get("per_item", [])
        if item.get("citation_attachment") == {"criterion": "C9", "flag": True}
    )
    if not isinstance(decisions, list):
        raise ContractError("C9 decisions must be a closed array")
    decision_pairs: list[tuple[str, str]] = []
    confirmed_by_finding: dict[str, list[tuple[str, str]]] = {}
    for index, decision in enumerate(decisions):
        if not isinstance(decision, Mapping):
            raise ContractError(f"C9 decisions[{index}] must be an object")
        _closed_keys(
            decision,
            {
                "decision_id",
                "judge_id",
                "item_replicate_id",
                "raw_flag",
                "disposition",
                "criterion_ref",
                "reason_code",
                "finding_id",
            },
            f"C9 decisions[{index}]",
        )
        judge_id = decision["judge_id"]
        item_replicate_id = decision["item_replicate_id"]
        if (
            not isinstance(judge_id, str)
            or not isinstance(item_replicate_id, str)
            or decision["decision_id"] != f"c9d.{judge_id}.{item_replicate_id}"
            or decision["raw_flag"] is not True
        ):
            raise ContractError("C9 decision identity/raw flag is not canonical")
        pair = (judge_id, item_replicate_id)
        decision_pairs.append(pair)
        disposition = decision["disposition"]
        criterion_ref = decision["criterion_ref"]
        reason_code = decision["reason_code"]
        finding_id = decision["finding_id"]
        if disposition == "confirmed":
            if (
                criterion_ref != "C9"
                or reason_code != "violation_confirmed"
                or not isinstance(finding_id, str)
                or not finding_id
            ):
                raise ContractError("confirmed C9 decision has invalid authority/result")
            confirmed_by_finding.setdefault(finding_id, []).append(pair)
        elif disposition == "rejected":
            valid_rejection = (
                criterion_ref == "C3" and reason_code == "authorized_under_C3"
            ) or (
                criterion_ref == "C9"
                and reason_code == "no_citation_attachment_violation"
            )
            if not valid_rejection or finding_id is not None:
                raise ContractError("rejected C9 decision has invalid closed reason")
        else:
            raise ContractError("C9 decision disposition is outside the closed vocabulary")
    if decision_pairs != raw_true_pairs or len(decision_pairs) != len(set(decision_pairs)):
        raise ContractError("C9 decisions must exactly resolve every typed raw true flag")

    for _location, override_text in _walk_strings(report.get("adjudication", {}).get("overrides", [])):
        lowered_override = override_text.casefold()
        if re.search(r"\bc9\b", lowered_override) or "citation_attachment" in lowered_override or "citation-attachment" in lowered_override:
            raise ContractError("C9 decisions cannot be routed through generic overrides")
    finding_ids: set[str] = set()
    for index, finding in enumerate(findings):
        if not isinstance(finding, Mapping):
            raise ContractError(f"C9 findings[{index}] must be an object")
        _closed_keys(
            finding,
            {
                "finding_id",
                "item_replicate_id",
                "criterion",
                "authorization",
                "citation_tokens_ref",
                "citation_tokens_sha256",
                "original_attachment_ref",
                "original_attachment_sha256",
                "revised_attachment_ref",
                "revised_attachment_sha256",
                "evidence_ref",
                "evidence_sha256",
                "raw_flag_judge_ids",
                "adjudication_disposition",
            },
            f"C9 findings[{index}]",
        )
        finding_id = finding["finding_id"]
        if (
            not isinstance(finding_id, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", finding_id)
            or finding_id in finding_ids
        ):
            raise ContractError("C9 finding_id values must be non-empty and unique")
        finding_ids.add(finding_id)
        if finding["item_replicate_id"] not in evaluated:
            raise ContractError("C9 finding names an unevaluated item-replicate")
        if finding["criterion"] != "C9" or finding["authorization"] != "unauthorized_under_C3":
            raise ContractError("C9 finding authority must be C9 and unauthorized_under_C3")
        raw_judge_ids = finding["raw_flag_judge_ids"]
        if (
            not isinstance(raw_judge_ids, list)
            or not raw_judge_ids
            or not all(isinstance(judge_id, str) and judge_id for judge_id in raw_judge_ids)
            or raw_judge_ids != sorted(set(raw_judge_ids))
        ):
            raise ContractError("C9 raw_flag_judge_ids must be a sorted non-empty unique list")
        if finding["adjudication_disposition"] != "confirmed":
            raise ContractError("published C9 findings must be confirmed raw flags")
        expected_confirmed_pairs = [
            (judge_id, finding["item_replicate_id"]) for judge_id in raw_judge_ids
        ]
        if confirmed_by_finding.get(finding_id) != expected_confirmed_pairs:
            raise ContractError("C9 finding raw judges differ from confirmed decisions")
        for judge_id in raw_judge_ids:
            judge = reported_judges.get(judge_id)
            if judge is None or not any(
                item.get("item_id") == finding["item_replicate_id"]
                and item.get("citation_attachment") == {
                    "criterion": "C9",
                    "flag": True,
                }
                for item in judge.get("per_item", [])
            ):
                raise ContractError(
                    "each confirmed C9 finding must replay to a raw judge flag"
                )
        for key in (
            "citation_tokens_sha256",
            "original_attachment_sha256",
            "revised_attachment_sha256",
            "evidence_sha256",
        ):
            if not isinstance(finding[key], str) or not re.fullmatch(r"[0-9a-f]{64}", finding[key]):
                raise ContractError(f"C9 findings[{index}].{key} must be lowercase SHA-256")
        attachment_specs = (
            ("citation_tokens", "citation-tokens.txt"),
            ("original_attachment", "original-attachment.txt"),
            ("revised_attachment", "revised-attachment.txt"),
        )
        attachment_bindings: dict[str, dict[str, str]] = {}
        for field, suffix in attachment_specs:
            attachment_ref = finding[f"{field}_ref"]
            expected_attachment_ref = (
                f"{RUNS_PREFIX}{record['run_id']}/c9/{finding_id}.{suffix}"
            )
            if attachment_ref != expected_attachment_ref:
                raise ContractError(f"C9 {field}_ref is not the canonical run-local path")
            attachment_path = _safe_file(
                root,
                attachment_ref,
                f"C9 findings[{index}] {field}",
                f"{RUNS_PREFIX}{record['run_id']}/",
            )
            if not 1 <= attachment_path.stat().st_size <= 65_536:
                raise ContractError(f"C9 {field} artifact must be 1..65536 bytes")
            if _sha256(attachment_path) != finding[f"{field}_sha256"]:
                raise ContractError(f"C9 {field} artifact hash mismatch")
            if attachment_ref not in raw_paths:
                raise ContractError(f"C9 {field}_ref must appear in raw_outputs.paths")
            attachment_bindings[field] = {
                "ref": attachment_ref,
                "sha256": finding[f"{field}_sha256"],
            }
        evidence_ref = finding["evidence_ref"]
        expected_evidence_ref = (
            f"{RUNS_PREFIX}{record['run_id']}/c9/{finding_id}.json"
        )
        if evidence_ref != expected_evidence_ref:
            raise ContractError("C9 evidence_ref is not the canonical run-local path")
        evidence_path = _safe_file(
            root,
            evidence_ref,
            f"C9 findings[{index}] evidence",
            f"{RUNS_PREFIX}{record['run_id']}/",
        )
        if _sha256(evidence_path) != finding["evidence_sha256"]:
            raise ContractError("C9 evidence artifact hash mismatch")
        if evidence_ref not in raw_paths:
            raise ContractError("C9 evidence_ref must appear in raw_outputs.paths")
        evidence = _require_object(
            _strict_json(evidence_path), f"C9 findings[{index}] evidence"
        )
        expected_evidence = {
            "schema_version": "revision-claim-drift-c9-evidence/1.0",
            "suite": "revision_claim_drift",
            "run_id": record["run_id"],
            "finding_id": finding_id,
            "item_replicate_id": finding["item_replicate_id"],
            "criterion": "C9",
            "raw_flags": [
                {"judge_id": judge_id, "criterion": "C9", "flag": True}
                for judge_id in raw_judge_ids
            ],
            "adjudication": {
                "disposition": "confirmed",
                "authorization": "unauthorized_under_C3",
            },
            "citation_tokens": attachment_bindings["citation_tokens"],
            "original_attachment": attachment_bindings["original_attachment"],
            "revised_attachment": attachment_bindings["revised_attachment"],
            "data_minimization": {"raw_rationale_stored": False},
        }
        if evidence != expected_evidence:
            raise ContractError("C9 evidence artifact differs from its closed replay grammar")
    if set(confirmed_by_finding) != finding_ids:
        raise ContractError("confirmed C9 decisions and published findings differ")
    _check_claim_language(report, record["status"])


def _check_docs(root: Path) -> None:
    readme_path = _safe_file(root, f"{SUITE_REL}/README.md", "suite README")
    design_path = _safe_file(
        root, "docs/design/2026-08-10-679-revision-claim-drift-suite-v2-spec.md", "v2 design"
    )
    readme = readme_path.read_text(encoding="utf-8")
    design = design_path.read_text(encoding="utf-8")
    readme_markers = (
        "### v2 subject-context isolation protocol (prospective)",
        "performs no re-run, creates no new\nmeasurement row, and does not rescore",
        "repository-instruction isolation",
        "physical path",
        "repository-membership probe",
        "`--bare`",
        "authentication result",
        "pre-fleet contamination probe",
        "prompt/output SHA-256",
        "subject-call plan",
        "launcher-config artifact",
        "subject.config.subject_context={ref,sha256,status}",
        "`raw_outputs.paths`",
        "`machine_supported`",
        "`attested_only`",
        "`not_isolated`",
        "`unknown`",
        "negative probe is evidence, not proof",
    )
    for marker in readme_markers:
        if marker not in readme:
            raise ContractError(f"suite README missing #679 protocol marker: {marker}")
    design_markers = (
        "DESIGN-FROZEN / PROSPECTIVE-ONLY",
        "creates no measurement row",
        "subject_context_record.schema.json",
        "subject.config.subject_context = {",
        "raw_outputs.paths",
        "preflight hash cycle",
        "results.revision_claim_drift_v2 = {",
        "all_items_including_non_controls",
        "resolution_direction` is `flags_only`",
        "inside_suite_repository",
        "machine_supported",
        "attested_only",
        "not_isolated",
        "unknown",
        "pwd_p_sha256",
        "repo_membership_probe",
        "authentication_result",
        "launcher-config artifact",
        "instruction_visibility",
        "context_probe",
        "subject_call_plan",
        "subject-call-plan.json",
        "launcher-config.json",
        "raw_flag_judge_ids",
        "adjudication_disposition",
        "decisions = [{",
        "data_minimization",
    )
    for marker in design_markers:
        if marker not in design:
            raise ContractError(f"v2 design missing frozen marker: {marker}")


def run_checks(root: Path | str = REPO_ROOT) -> list[str]:
    """Run every hermetic #679 guard and return human-readable successes."""
    root_path = Path(root).resolve()
    measurement_rows = _check_history(root_path)
    _check_rubric(root_path)
    schema, _launcher_schema, _call_plan_schema, _ = _check_subject_assets(root_path)
    _check_docs(root_path)

    # A future row cannot be introduced accidentally.  Once the explicit
    # no-measurement boundary is intentionally revised, every 1.1 row must also
    # survive the prospective context replay below.
    for _path, value in measurement_rows:
        if isinstance(value, Mapping) and value.get("measurement_contract") == "heldout-measurement/1.1":
            validate_prospective_measurement(value, root_path, schema)

    return [
        "historical bytes/tree and no-new-measurement boundary",
        "v2 rubric and closed amendment ledger",
        "subject-context/launcher/call-plan schemas and four synthetic fixtures",
        "README/design prospective protocol",
        "prospective heldout-measurement/1.1 context replay",
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args(argv)
    try:
        checks = run_checks(args.root)
    except ContractError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    for check in checks:
        print(f"PASS: {check}")
    print("PASS: #679 is hermetic; this guard made no model/API/judge/eval call")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
