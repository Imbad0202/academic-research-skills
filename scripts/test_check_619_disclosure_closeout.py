#!/usr/bin/env python3
"""Focused mutation coverage for the #619 disclosure closeout."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "check_619_disclosure_closeout.py"
PROTOCOL = "academic-paper/references/disclosure_mode_protocol.md"
POLICIES = "academic-paper/references/venue_disclosure_policies.md"
AUDIT = "audits/external-contribution-audit-prompt.md"
ALL_FILES = (PROTOCOL, POLICIES, AUDIT)


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    for rel in ALL_FILES:
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


@pytest.mark.parametrize(
    ("scenario", "old", "new"),
    (
        (
            "created text",
            "| Created written content | REQUIRED | REQUIRED | — |",
            "| Created written content | — | REQUIRED | — |",
        ),
        (
            "edited text",
            "| Edited written content | — | REQUIRED | — |",
            "| Edited written content | REQUIRED | REQUIRED | — |",
        ),
        (
            "non-data visual",
            "| Produced non-data visual content | REQUIRED | REQUIRED | — |",
            "| Produced non-data visual content | REQUIRED | REQUIRED | REQUIRED |",
        ),
        (
            "data-representing figure",
            "| Produced figure representing manuscript data | REQUIRED | REQUIRED | REQUIRED |",
            "| Produced figure representing manuscript data | REQUIRED | REQUIRED | — |",
        ),
    ),
)
def test_frontiers_action_matrix_is_semantically_pinned(
    tree: Path, scenario: str, old: str, new: str
) -> None:
    _mutate(tree, PROTOCOL, old, new)
    result = _run(tree)
    assert result.returncode == 1
    assert scenario in result.stderr


def test_frontiers_phase2_render_gate_cannot_regrow(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "Use that forms part of the research method: method-level description.",
        "Use that forms part of the research method: method-level description. "
        "Figure use: plagiarism-free confirmation before render.",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "Phase 2b" in result.stderr


def test_unknown_action_state_stays_outstanding_not_halted(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "UNKNOWN or false action state is OUTSTANDING",
        "UNKNOWN action state is UNKNOWN/HALTED",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "OUTSTANDING" in result.stderr


def test_frontiers_quality_actions_are_not_categorical_prohibitions(tree: Path) -> None:
    _mutate(
        tree,
        POLICIES,
        "Editors/reviewers uploading manuscript content to external generative AI tools.",
        "Editors/reviewers uploading manuscript content to external generative AI tools. "
        "Unchecked figures are prohibited.",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "Prohibited uses" in result.stderr


def test_jama_snapshot_gap_is_explicit(tree: Path) -> None:
    _mutate(
        tree,
        POLICIES,
        "A Piece of My Mind and Poetry drafting clauses were verified on the live official page on 2026-08-01 and are absent from the cited 2026-07-01 snapshot.",
        "The cited snapshot includes all current manuscript-class clauses.",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "JAMA" in result.stderr
    assert "snapshot" in result.stderr


def test_audit_round_exact_heads_and_counts_are_pinned(tree: Path) -> None:
    _mutate(tree, AUDIT, "Template A: 8 P1 / 6 P2 / 1 P3", "Template A: 7 P1 / 6 P2 / 1 P3")
    result = _run(tree)
    assert result.returncode == 1
    assert "2026-08-01" in result.stderr


def test_old_multi_pr_head_cannot_be_reassigned_to_new_round(tree: Path) -> None:
    _mutate(
        tree,
        AUDIT,
        "PR #599 blind audit head `7bb578d3`",
        "PR #599 blind audit head `45653587`",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "7bb578d3" in result.stderr


def test_missing_required_file_is_invocation_error(tree: Path) -> None:
    (tree / AUDIT).unlink()
    result = _run(tree)
    assert result.returncode == 2
    assert "required file missing" in result.stderr
