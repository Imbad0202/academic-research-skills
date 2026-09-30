#!/usr/bin/env python3
"""Tests for check_method_weaknesses_sync.py (#916).

Mutation tests confirm the lint is not accept-all: every break in the marker
grammar or in a surface's bytes must fail it, and the clean repository must pass.
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
    extract_block,
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


def test_line_ending_drift_in_a_surface_fails(tree: Path) -> None:
    path = tree / AGENT
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert "differs only in its line ending" in _errors(tree)


def test_surface_without_markers_fails(tree: Path) -> None:
    _edit(tree, AGENT, BEGIN + "\n", "")
    _edit(tree, AGENT, "\n" + END, "")
    assert f"MW-2 {AGENT}: expected one {BEGIN}" in _errors(tree)


def test_surface_with_block_twice_fails(tree: Path) -> None:
    block, errors = extract_block((REPO_ROOT / CANONICAL).read_text(encoding="utf-8"), "t")
    assert block is not None, errors
    text = (tree / AGENT).read_text(encoding="utf-8")
    (tree / AGENT).write_text(f"{text}\n{BEGIN}\n{block}\n{END}\n", encoding="utf-8")
    assert "found 2 occurrence(s)" in _errors(tree)


def test_marker_not_alone_on_its_line_fails(tree: Path) -> None:
    _edit(tree, AGENT, BEGIN + "\n", "Text " + BEGIN + "\n")
    assert "0 on their own line" in _errors(tree)


def test_canonical_markers_reversed_fails(tree: Path) -> None:
    _edit(tree, CANONICAL, BEGIN, "@@BEGIN@@")
    _edit(tree, CANONICAL, END, BEGIN)
    _edit(tree, CANONICAL, "@@BEGIN@@", END)
    assert f"MW-1 {CANONICAL}: {END} comes before {BEGIN}" in _errors(tree)


def test_empty_canonical_block_fails(tree: Path) -> None:
    text = (tree / CANONICAL).read_text(encoding="utf-8")
    head, rest = text.split(BEGIN + "\n", 1)
    _, tail = rest.split(END, 1)
    (tree / CANONICAL).write_text(head + BEGIN + "\n\n" + END + tail, encoding="utf-8")
    assert "block is empty" in _errors(tree)


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
