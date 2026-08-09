#!/usr/bin/env python3
"""Hermetic mutation tests for the static #670 integration guard."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts import check_670_revision_roadmap_integration as guard


REPO_ROOT = Path(__file__).resolve().parents[1]
COPIED = tuple(
    dict.fromkeys(
        (
            *guard.REVISION_SCHEMAS,
            guard.PATCH_SCHEMA,
            guard.PATCH_LEGACY_SCHEMA,
            *guard.RE_REVIEW_SCHEMAS,
            *guard.RE_REVIEW_LEGACY_SCHEMAS,
            *guard.RUNTIME_HASHES,
            guard.LEGACY_APPLY_RUNTIME,
            *guard.DETECTION_HASHES,
            *guard.AUTHOR_PRESENTATION_FILES,
            *guard.REQUIRED_POINTERS,
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


def _read_json(root: Path, relative: Path) -> dict[str, object]:
    value = json.loads((root / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _write_json(root: Path, relative: Path, value: object) -> None:
    (root / relative).write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _replace(root: Path, relative: Path, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _append(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


def test_current_repository_passes_670_integration() -> None:
    assert guard.run_checks(REPO_ROOT) == []


@pytest.mark.parametrize("mutation", ["version", "legacy_field"])
def test_current_roadmap_version_and_legacy_fields_are_load_bearing(
    tmp_path: Path, mutation: str
) -> None:
    root = _tree(tmp_path)
    schema = _read_json(root, guard.REVISION_SCHEMAS[0])
    if mutation == "version":
        schema["properties"]["schema_version"]["const"] = "revision-roadmap/0.9"  # type: ignore[index]
    else:
        schema["$defs"]["roadmap_item"]["properties"]["priority"] = {  # type: ignore[index]
            "type": "integer"
        }
    _write_json(root, guard.REVISION_SCHEMAS[0], schema)
    errors = guard.run_checks(root)
    expected = "schema_version drifted" if mutation == "version" else "legacy/author-owned fields"
    assert any(expected in error for error in errors)


@pytest.mark.parametrize("surface", ["current", "legacy"])
def test_patch_current_1_1_and_legacy_1_0_are_isolated(
    tmp_path: Path, surface: str
) -> None:
    root = _tree(tmp_path)
    if surface == "current":
        schema = _read_json(root, guard.PATCH_SCHEMA)
        schema["$defs"]["review_patch"]["properties"]["patch_format_version"][  # type: ignore[index]
            "const"
        ] = "1.0"
        _write_json(root, guard.PATCH_SCHEMA, schema)
        expected = "review_patch no longer pins current patch 1.1"
    else:
        schema = _read_json(root, guard.PATCH_LEGACY_SCHEMA)
        schema["properties"]["patch_format_version"]["const"] = "1.1"  # type: ignore[index]
        _write_json(root, guard.PATCH_LEGACY_SCHEMA, schema)
        expected = "archived patch schema no longer pins 1.0"
    assert any(expected in error for error in guard.run_checks(root))


def test_every_shipped_schema_id_is_globally_unique(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    current = _read_json(root, guard.PATCH_SCHEMA)
    legacy = _read_json(root, guard.PATCH_LEGACY_SCHEMA)
    legacy["$id"] = current["$id"]
    _write_json(root, guard.PATCH_LEGACY_SCHEMA, legacy)
    assert any(
        "duplicate shipped schema $id" in error for error in guard.run_checks(root)
    )


def test_re_review_current_version_is_load_bearing(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    relative = guard.RE_REVIEW_SCHEMAS[0]
    schema = _read_json(root, relative)
    schema["properties"]["contract_version"]["const"] = "1.0"  # type: ignore[index]
    _write_json(root, relative, schema)
    assert any(
        "current contract_version must be 1.1" in error
        for error in guard.run_checks(root)
    )


def test_re_review_legacy_field_name_is_rejected(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    relative = guard.RE_REVIEW_SCHEMAS[2]
    schema = _read_json(root, relative)
    schema["properties"]["priority"] = {"type": "integer"}  # type: ignore[index]
    _write_json(root, relative, schema)
    assert any("legacy field name reintroduced" in error for error in guard.run_checks(root))


@pytest.mark.parametrize("artifact", ["author_adjudication", "revision_evidence_bundle"])
def test_re_review_requires_author_sidecar_and_bundle(
    tmp_path: Path, artifact: str
) -> None:
    root = _tree(tmp_path)
    relative = guard.RE_REVIEW_SCHEMAS[0]
    schema = _read_json(root, relative)
    schema["properties"]["artifacts"]["required"].remove(artifact)  # type: ignore[index]
    _write_json(root, relative, schema)
    assert any(
        "exactly eleven artifact keys" in error for error in guard.run_checks(root)
    )


def test_re_review_original_schema_cannot_degrade_to_optional_absence(
    tmp_path: Path,
) -> None:
    root = _tree(tmp_path)
    relative = guard.RE_REVIEW_SCHEMAS[0]
    schema = _read_json(root, relative)
    schema["properties"]["artifacts"]["properties"]["original_manuscript"][  # type: ignore[index]
        "$ref"
    ] = "#/$defs/artifact_entry"
    _write_json(root, relative, schema)
    assert any(
        "original_manuscript is not a hard-required present artifact" in error
        for error in guard.run_checks(root)
    )


def test_frozen_detection_surface_drift_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    relative = next(iter(guard.DETECTION_HASHES))
    _append(root, relative, "\n<!-- unauthorized detection drift -->\n")
    assert any(
        "reviewer detection surface drifted" in error
        for error in guard.run_checks(root)
    )


@pytest.mark.parametrize(
    "phrase",
    [
        "Priority 1",
        "Estimated total effort",
        "(ranked)",
        "most severe first",
        "| Rank |",
    ],
)
def test_author_facing_rank_or_time_presentation_fails(
    tmp_path: Path, phrase: str
) -> None:
    root = _tree(tmp_path)
    relative = guard.AUTHOR_PRESENTATION_FILES[0]
    _append(root, relative, f"\n{phrase}\n")
    assert any(
        "author-facing work-rank/time presentation" in error
        for error in guard.run_checks(root)
    )


def test_required_documentation_pointer_removal_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    relative = Path("docs/design/2026-08-10-670-non-ranking-revision-roadmap-spec.md")
    _replace(
        root,
        relative,
        "immutable reviewer-owned core",
        "mutable reviewer-owned core",
    )
    assert any(
        "missing required #670 pointer" in error for error in guard.run_checks(root)
    )


def test_runtime_forbidden_import_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _append(root, guard.ROADMAP_RUNTIME, "\nimport socket\n")
    assert any(
        "forbidden model/network/clock/process import socket" in error
        for error in guard.run_checks(root)
    )


def test_runtime_ambient_scan_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _append(
        root,
        guard.ROADMAP_RUNTIME,
        "\n\ndef forbidden_scan(path):\n    return path.rglob('*')\n",
    )
    assert any("forbidden ambient scan rglob()" in error for error in guard.run_checks(root))


def test_runtime_frozen_hash_drift_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _append(root, guard.APPLY_RUNTIME, "\n# unauthorized runtime drift\n")
    assert any("frozen runtime hash drifted" in error for error in guard.run_checks(root))


def test_legacy_loader_path_is_load_bearing(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _replace(root, guard.LEGACY_APPLY_RUNTIME, '/ "v1_0"', '/ "v1_1"')
    assert any("legacy apply isolation missing" in error for error in guard.run_checks(root))


@pytest.mark.parametrize(
    "payload",
    [
        '{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","type":"array"}',
        '{"type":"number","minimum":NaN}',
    ],
)
def test_duplicate_or_nonfinite_schema_json_fails_closed(
    tmp_path: Path, payload: str
) -> None:
    root = _tree(tmp_path)
    (root / guard.REVISION_SCHEMAS[0]).write_text(payload, encoding="utf-8")
    assert any("schema load/check failed" in error for error in guard.run_checks(root))
