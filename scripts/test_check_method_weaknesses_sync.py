#!/usr/bin/env python3
"""Tests for check_method_weaknesses_sync.py (#916).

The marker grammar is tested once in test_skill_lint_marker_block.py (#923).
These tests check the wiring: the clean repository passes, each listed surface
and the canonical file are checked under this lint's ids, and the exit codes.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts.check_method_weaknesses_sync import (
    BEGIN,
    CANONICAL,
    END,
    SURFACES,
    check,
)
from tests.test_helpers import run_script

REPO_ROOT = Path(__file__).resolve().parents[1]
LINT = REPO_ROOT / "scripts" / "check_method_weaknesses_sync.py"
AGENT = Path("deep-research/agents/bibliography_agent.md")
PHRASE = "Small sample"


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """A copy of just the files the lint reads, under a temp root."""
    for rel in (CANONICAL, *SURFACES):
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, dest)
    return tmp_path


def _edit(root: Path, rel: Path, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not in {rel}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _errors(root: Path) -> str:
    return "\n".join(check(root))


def test_repository_passes() -> None:
    result = run_script(LINT, "--root", str(REPO_ROOT))
    assert result.returncode == 0, result.stderr
    assert "4 surfaces match" in result.stdout


def test_canonical_lists_every_surface() -> None:
    text = (REPO_ROOT / CANONICAL).read_text(encoding="utf-8")
    for rel in SURFACES:
        assert f"`{rel}`" in text


def test_copied_tree_passes(tree: Path) -> None:
    assert check(tree) == []


@pytest.mark.parametrize("rel", SURFACES)
def test_one_changed_byte_in_a_surface_fails(tree: Path, rel: Path) -> None:
    _edit(tree, rel, PHRASE, "Small Sample")
    assert f"MW-2 {rel}: method-weaknesses block differs" in _errors(tree)


def test_malformed_canonical_is_reported_as_mw_1(tree: Path) -> None:
    _edit(tree, CANONICAL, BEGIN, "@@BEGIN@@")
    _edit(tree, CANONICAL, END, BEGIN)
    _edit(tree, CANONICAL, "@@BEGIN@@", END)
    assert f"MW-1 {CANONICAL}: {END} comes before {BEGIN}" in _errors(tree)

def test_changed_canonical_fails_every_surface(tree: Path) -> None:
    _edit(tree, CANONICAL, PHRASE, "Small Sample")
    errors = _errors(tree)
    for rel in SURFACES:
        assert f"MW-2 {rel}: method-weaknesses block differs" in errors


def test_cli_exit_codes(tree: Path) -> None:
    _edit(tree, AGENT, PHRASE, "Small Sample")
    assert run_script(LINT, "--root", str(tree)).returncode == 1
    (tree / AGENT).unlink()
    result = run_script(LINT, "--root", str(tree))
    assert result.returncode == 2
    assert f"required file missing: {AGENT}" in result.stderr
