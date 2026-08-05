#!/usr/bin/env python3
"""Mutation tests for the #610 receipt closed-enum defrift lint."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "check_receipt_enum_sync.py"
CANONICAL = "academic-paper-reviewer/references/reviewer_sprint_prompt_source.md"
SPEC = "docs/design/2026-08-02-610-statistical-recompute-baseline-spec.md"


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    for rel in (CANONICAL, SPEC):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / rel, dst)
    return tmp_path


def _mutate(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"anchor missing in {rel}: {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_clean_tree_passes(tree: Path) -> None:
    result = _run(tree)
    assert result.returncode == 0, result.stderr
    assert "RECEIPT-ENUM-SYNC: PASS" in result.stdout


def test_fragment_procedure_enum_drift_fails(tree: Path) -> None:
    _mutate(
        tree,
        CANONICAL,
        "`procedure_id: <p_from_test_statistic|grim|grimmer|n_from_df>`",
        "`procedure_id: <p_from_test_statistic|grim|grimmer|n_from_df"
        "|effect_size_consistency>`",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "procedure_id: fragment enum drifted" in result.stderr


def test_fragment_status_enum_drift_fails(tree: Path) -> None:
    _mutate(
        tree,
        CANONICAL,
        "`status: <consistent|mismatch|not_computable|not_applicable>`",
        "`status: <consistent|mismatch|not_computable>`",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "status: fragment enum drifted" in result.stderr


def test_fragment_tail_enum_drift_fails(tree: Path) -> None:
    _mutate(
        tree,
        CANONICAL,
        "`tail_convention: <two-tailed|one-tailed|upper-tail|unstated>`",
        "`tail_convention: <two-tailed|one-tailed|unstated>`",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "tail_convention: fragment enum drifted" in result.stderr


def test_fragment_reason_enum_drift_fails(tree: Path) -> None:
    _mutate(
        tree,
        CANONICAL,
        "`reachability_not_completed`. Every other status",
        "`reachability_incomplete`. Every other status",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "not_computable_reason: fragment enum drifted" in result.stderr


def test_spec_procedure_row_drift_fails(tree: Path) -> None:
    _mutate(
        tree,
        SPEC,
        "`p_from_test_statistic`, `grim`, `grimmer`, or `n_from_df` |",
        "`p_from_test_statistic`, `grim`, or `n_from_df` |",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "procedure_id: spec §4 enum drifted" in result.stderr


def test_spec_reason_bullet_drift_fails(tree: Path) -> None:
    _mutate(tree, SPEC, "- `tail_ambiguous`\n", "")
    result = _run(tree)
    assert result.returncode == 1
    assert "not_computable_reason: spec §4 enum drifted" in result.stderr


def test_fragment_missing_enum_spelling_fails(tree: Path) -> None:
    _mutate(
        tree,
        CANONICAL,
        "`status: <consistent|mismatch|not_computable|not_applicable>`",
        "`status: any of the closed statuses`",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "expected exactly one" in result.stderr


def test_missing_spec_file_is_invocation_error(tree: Path) -> None:
    (tree / SPEC).unlink()
    result = _run(tree)
    assert result.returncode == 2
    assert "required file unreadable" in result.stderr
