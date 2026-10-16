#!/usr/bin/env python3
"""Mutation tests for the static #681 advisory integration guard."""
from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path, PureWindowsPath

import pytest

from scripts import check_content_coverage_advisory_integration as guard


REPO_ROOT = Path(__file__).resolve().parents[1]
HELDOUT_SENTINEL = Path("evals/heldout/suite_registry.json")
COPIED = tuple(
    dict.fromkeys(
        (
            guard.EVIDENCE_SCHEMA,
            guard.ADVISORY_SCHEMA,
            guard.EVIDENCE_RUNTIME,
            guard.ADVISORY_RUNTIME,
            *guard.REQUIRED_POINTERS,
            HELDOUT_SENTINEL,
        )
    )
)


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for relative in COPIED:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative, target)
    return root


def _replace(root: Path, relative: Path, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _replace_all(root: Path, relative: Path, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def test_current_repository_passes_content_coverage_integration() -> None:
    assert guard.run_checks(REPO_ROOT) == []


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("layer", "MODEL-ADVISORY"),
        ("evaluation_status", "MEASURED"),
        ("schema_version", "content-coverage-advisory/2.0"),
    ],
)
def test_final_schema_marker_drift_fails(
    tmp_path: Path, field: str, replacement: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.ADVISORY_SCHEMA
    schema = json.loads(path.read_text(encoding="utf-8"))
    schema["properties"][field]["const"] = replacement
    _write_json(path, schema)
    assert any(field in error for error in guard.run_checks(root))


def test_reason_synonym_or_boundary_weakening_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.ADVISORY_SCHEMA
    schema = json.loads(path.read_text(encoding="utf-8"))
    schema["$defs"]["reason_code"]["enum"][0] = "COVERAGE_OK"
    schema["properties"]["boundary"]["properties"][
        "authorization_status_unchanged"
    ] = {"type": "boolean"}
    _write_json(path, schema)
    errors = guard.run_checks(root)
    assert any("reason vocabulary drifted" in error for error in errors)
    assert any("authorization_status_unchanged" in error for error in errors)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_captured_at",
        "open_judgment",
        "status_drift",
        "failure_drift",
        "conditional_drift",
    ],
)
def test_draft_schema_shape_and_conditionals_are_load_bearing(
    tmp_path: Path, mutation: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.ADVISORY_SCHEMA
    schema = json.loads(path.read_text(encoding="utf-8"))
    judgment = schema["$defs"]["advisory_draft_judgment"]
    if mutation == "missing_captured_at":
        judgment["required"].remove("captured_at")
    elif mutation == "open_judgment":
        judgment["additionalProperties"] = True
    elif mutation == "status_drift":
        judgment["properties"]["advisory_coverage_status"]["oneOf"][0]["enum"][
            0
        ] = "COVERED"
    elif mutation == "failure_drift":
        judgment["properties"]["failure_state"]["oneOf"][0]["enum"][0] = (
            "model_failed"
        )
    else:
        judgment["allOf"][2]["then"]["properties"]["captured_at"] = {
            "type": ["string", "null"]
        }
    _write_json(path, schema)
    errors = guard.run_checks(root)
    assert any("draft" in error for error in errors)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        (
            'PERFORMED_STATUSES = frozenset({"DOCUMENTED", "NOT_LOCATED", "CONFLICTING"})',
            'PERFORMED_STATUSES = frozenset({"DOCUMENTED", "COVERED", "CONFLICTING"})',
        ),
        (
            '{"not_checked", "source_missing", "access_failed", "retrieval_failed"}',
            '{"not_checked", "model_failed", "access_failed", "retrieval_failed"}',
        ),
        (
            '        "captured_at",\n    }\n    for index, raw in enumerate(',
            '        "removed_captured_at",\n    }\n    for index, raw in enumerate(',
        ),
        (
            "if failure is not None:",
            "if False and failure is not None:",
        ),
    ],
)
def test_manual_draft_validator_parity_is_load_bearing(
    tmp_path: Path, old: str, new: str
) -> None:
    root = _tree(tmp_path)
    _replace(root, guard.ADVISORY_RUNTIME, old, new)
    errors = guard.run_checks(root)
    assert any(
        "manual draft" in error
        or "PERFORMED_STATUSES" in error
        or "FAILURE_STATES" in error
        for error in errors
    )


def test_parallel_verdict_field_is_rejected_from_either_schema(
    tmp_path: Path,
) -> None:
    for relative in (guard.EVIDENCE_SCHEMA, guard.ADVISORY_SCHEMA):
        root = _tree(tmp_path / relative.stem)
        path = root / relative
        schema = json.loads(path.read_text(encoding="utf-8"))
        schema["properties"]["verdict"] = {"type": "string"}
        _write_json(path, schema)
        assert any("forbidden determination fields" in error for error in guard.run_checks(root))


def test_evidence_state_or_cache_reuse_drift_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.EVIDENCE_SCHEMA
    schema = json.loads(path.read_text(encoding="utf-8"))
    schema["$defs"]["excerpt"]["properties"]["state"]["enum"].append(
        "probably_covered"
    )
    schema["properties"]["cache"]["properties"]["status"] = {
        "enum": ["not_used", "hit"]
    }
    _write_json(path, schema)
    errors = guard.run_checks(root)
    assert any("excerpt-state vocabulary drifted" in error for error in errors)
    assert any("cache must stay not_used/null" in error for error in errors)


def test_duplicate_or_nonfinite_schema_json_fails_closed(tmp_path: Path) -> None:
    for payload in (
        '{"$schema":"a","$schema":"b"}',
        '{"value":NaN}',
    ):
        root = _tree(tmp_path / str(len(payload)))
        (root / guard.EVIDENCE_SCHEMA).write_text(payload, encoding="utf-8")
        assert any("schema load/check failed" in error for error in guard.run_checks(root))


@pytest.mark.parametrize(
    "statement",
    [
        "import socket\n",
        "import requests\n",
        "import subprocess\n",
        "import urllib.request\n",
        "from openai import OpenAI\n",
    ],
)
def test_runtime_model_network_or_process_import_fails(
    tmp_path: Path, statement: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.ADVISORY_RUNTIME
    path.write_text(statement + path.read_text(encoding="utf-8"), encoding="utf-8")
    assert any("forbidden model/network/process import" in error for error in guard.run_checks(root))


def test_runtime_ambient_scan_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.ADVISORY_RUNTIME
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n\ndef forbidden_scan(path):\n    return path.rglob('*')\n",
        encoding="utf-8",
    )
    assert any("forbidden ambient scan" in error for error in guard.run_checks(root))


def test_exact_manifest_replay_call_removal_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _replace(
        root,
        guard.ADVISORY_RUNTIME,
        "validate_submission_packet_manifest(",
        "removed_exact_manifest_replay(",
    )
    assert any("exact #667 replay" in error for error in guard.run_checks(root))


def test_renderer_reachable_file_read_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.ADVISORY_RUNTIME
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_advisory"
    )
    lines = source.splitlines(keepends=True)
    lines.insert(
        function.body[0].lineno - 1,
        '    Path("ambient-source.txt").read_text(encoding="utf-8")\n',
    )
    path.write_text("".join(lines), encoding="utf-8")
    assert any("pure advisory path" in error for error in guard.run_checks(root))


@pytest.mark.parametrize("relative", tuple(guard.REQUIRED_POINTERS))
def test_each_documented_integration_pointer_is_load_bearing(
    tmp_path: Path, relative: Path
) -> None:
    root = _tree(tmp_path)
    token = guard.REQUIRED_POINTERS[relative][0]
    _replace_all(root, relative, token, "removed-681-pointer")
    assert any(
        str(relative) in error and "missing #681 token" in error
        for error in guard.run_checks(root)
    )


def test_architect_consumer_mirror_drift_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.ARCHITECT_MIRROR
    path.write_text(
        path.read_text(encoding="utf-8") + "\n# mirror drift\n",
        encoding="utf-8",
    )
    assert any("architect mirror drift" in error for error in guard.run_checks(root))


def test_fictitious_unmeasured_measurement_row_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _write_json(
        root / guard.HELDOUT_ROOT / "content-coverage" / "measurement.json",
        {
            "surface": "authority_profile_content_coverage",
            "status": "UNMEASURED",
        },
    )
    assert any("fictitious #681 held-out measurement row" in error for error in guard.run_checks(root))


def test_guard_cli_success_and_unknown_flag(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    assert guard.main(["--root", str(root)]) == 0
    assert guard.main(["--root", str(root), "--unknown"]) == 2


def test_required_pointers_match_windows_posix_paths(tmp_path, monkeypatch) -> None:
    root = _tree(tmp_path)
    pointers = guard._required_pointers(**{
        name.lower(): PureWindowsPath(*getattr(guard, name).parts)
        for name in ("EVIDENCE_SCHEMA", "ADVISORY_SCHEMA", "ADVISORY_RUNTIME", "ADVISORY_PROTOCOL")
    })
    monkeypatch.setattr(guard, "REQUIRED_POINTERS", pointers)
    assert guard._documentation_errors(root) == []
