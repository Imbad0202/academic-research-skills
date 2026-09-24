#!/usr/bin/env python3
"""Tests for check_routing_core_sync.py and the announce's routing core (#892).

Mutation tests confirm the lint is not accept-all: every break in the marker
grammar or in a copy's bytes must fail it, and the clean repository must pass.
The announce tests run the real SessionStart script, so the plugin path is
checked end to end rather than by reading the script's source.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.check_routing_core_sync import (
    ANNOUNCE,
    BEGIN,
    CANONICAL,
    COPIES,
    END,
    extract_block,
)
from tests.test_helpers import run_script

REPO_ROOT = Path(__file__).resolve().parents[1]
LINT = REPO_ROOT / "scripts" / "check_routing_core_sync.py"


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return run_script(LINT, "--root", str(root))


def _canonical_block() -> str:
    block, errors = extract_block((REPO_ROOT / CANONICAL).read_text(encoding="utf-8"), "t")
    assert block is not None, errors
    return block


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """A copy of just the files the lint reads, under a temp root."""
    for rel in (CANONICAL, *COPIES, ANNOUNCE):
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, dest)
    return tmp_path


def _edit(root: Path, rel: Path, old: str, new: str, count: int = 1) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not in {rel}"
    path.write_text(text.replace(old, new, count), encoding="utf-8")


def test_repository_passes() -> None:
    result = _run(REPO_ROOT)
    assert result.returncode == 0, result.stderr


def test_copied_tree_passes(tree: Path) -> None:
    assert _run(tree).returncode == 0


@pytest.mark.parametrize("rel", COPIES, ids=lambda rel: str(rel))
def test_one_changed_byte_in_a_copy_fails(tree: Path, rel: Path) -> None:
    _edit(tree, rel, "Do NOT auto-route", "Do not auto-route")
    result = _run(tree)
    assert result.returncode == 1
    assert f"RC-2 {rel}: routing-core block differs" in result.stderr


@pytest.mark.parametrize("rel", COPIES, ids=lambda rel: str(rel))
def test_copy_without_markers_fails(tree: Path, rel: Path) -> None:
    _edit(tree, rel, BEGIN + "\n", "")
    _edit(tree, rel, "\n" + END, "")
    result = _run(tree)
    assert result.returncode == 1
    assert f"RC-2 {rel}: expected one {BEGIN}" in result.stderr


def test_copy_with_block_twice_fails(tree: Path) -> None:
    rel = COPIES[1]
    text = (tree / rel).read_text(encoding="utf-8")
    block = f"{BEGIN}\n{_canonical_block()}\n{END}"
    (tree / rel).write_text(text + "\n" + block + "\n", encoding="utf-8")
    result = _run(tree)
    assert result.returncode == 1
    assert "found 2 occurrence(s)" in result.stderr


def test_marker_not_alone_on_its_line_fails(tree: Path) -> None:
    rel = COPIES[2]
    _edit(tree, rel, BEGIN + "\n", "Text " + BEGIN + "\n")
    result = _run(tree)
    assert result.returncode == 1
    assert "0 on their own line" in result.stderr


def test_canonical_markers_reversed_fails(tree: Path) -> None:
    _edit(tree, CANONICAL, BEGIN, "@@BEGIN@@")
    _edit(tree, CANONICAL, END, BEGIN)
    _edit(tree, CANONICAL, "@@BEGIN@@", END)
    result = _run(tree)
    assert result.returncode == 1
    assert f"RC-1 {CANONICAL}: {END} comes before {BEGIN}" in result.stderr


def test_empty_canonical_block_fails(tree: Path) -> None:
    text = (tree / CANONICAL).read_text(encoding="utf-8")
    head, rest = text.split(BEGIN + "\n", 1)
    _, tail = rest.split(END, 1)
    (tree / CANONICAL).write_text(head + BEGIN + "\n\n" + END + tail, encoding="utf-8")
    result = _run(tree)
    assert result.returncode == 1
    assert "block is empty" in result.stderr


def test_changed_canonical_fails_every_copy(tree: Path) -> None:
    _edit(tree, CANONICAL, "Do NOT auto-route", "Do not auto-route")
    result = _run(tree)
    assert result.returncode == 1
    for rel in COPIES:
        assert f"RC-2 {rel}: routing-core block differs" in result.stderr


def test_announce_without_canonical_path_fails(tree: Path) -> None:
    _edit(tree, ANNOUNCE, str(CANONICAL), "shared/references/routing.md")
    result = _run(tree)
    assert result.returncode == 1
    assert f"RC-3 {ANNOUNCE}: does not name {CANONICAL}" in result.stderr


def test_missing_copy_is_an_invocation_error(tree: Path) -> None:
    (tree / COPIES[3]).unlink()
    result = _run(tree)
    assert result.returncode == 2
    assert "missing file" in result.stderr


def _announce(script: Path, source: str) -> str:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_ROOT"}
    env["ARS_UPDATE_CHECK"] = "0"
    result = subprocess.run(
        ["bash", str(script)], input=json.dumps({"source": source}), text=True,
        capture_output=True, env=env, check=True,
    )
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


@pytest.mark.parametrize("source", ("startup", "clear", "resume", "compact"))
def test_announce_carries_the_block_for_every_source(source: str) -> None:
    context = _announce(REPO_ROOT / ANNOUNCE, source)
    assert _canonical_block() in context
    assert "routing-core:" not in context  # the markers themselves stay out
    assert "apply it before invoking an ARS skill" in context


def test_announce_without_the_core_file_still_emits_valid_json(tmp_path: Path) -> None:
    script = tmp_path / ANNOUNCE
    script.parent.mkdir(parents=True)
    shutil.copyfile(REPO_ROOT / ANNOUNCE, script)
    context = _announce(script, "startup")
    assert "ARS routing discipline" not in context
    assert "Requests outside academic research and writing do not invoke ARS" in context
