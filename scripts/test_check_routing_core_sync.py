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
    BEGIN,
    CANONICAL,
    CLAUDE_MD,
    END,
    check,
    copies,
    extract_block,
)
from tests.test_helpers import run_script

REPO_ROOT = Path(__file__).resolve().parents[1]
LINT = REPO_ROOT / "scripts" / "check_routing_core_sync.py"
ANNOUNCE = REPO_ROOT / "scripts" / "announce-ars-loaded.sh"
SKILL = Path("academic-paper/SKILL.md")


def _canonical_block() -> str:
    block, errors = extract_block((REPO_ROOT / CANONICAL).read_text(encoding="utf-8"), "t")
    assert block is not None, errors
    return block


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """A copy of just the files the lint reads, under a temp root."""
    for rel in (CANONICAL, *copies(REPO_ROOT)):
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
    assert "5 copies match" in result.stdout


def test_copies_are_claude_md_and_every_skill() -> None:
    assert copies(REPO_ROOT) == [
        CLAUDE_MD,
        Path("academic-paper/SKILL.md"),
        Path("academic-paper-reviewer/SKILL.md"),
        Path("academic-pipeline/SKILL.md"),
        Path("deep-research/SKILL.md"),
    ]


def test_copied_tree_passes(tree: Path) -> None:
    assert check(tree) == []


def test_one_changed_byte_in_a_copy_fails(tree: Path) -> None:
    _edit(tree, SKILL, "Do NOT auto-route", "Do not auto-route")
    assert f"RC-2 {SKILL}: routing-core block differs" in _errors(tree)


def _to_crlf(path: Path) -> None:
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))


def test_line_ending_drift_in_a_copy_fails(tree: Path) -> None:
    _to_crlf(tree / SKILL)
    assert f"RC-2 {SKILL}: routing-core block differs" in _errors(tree)
    assert "differs only in its line ending" in _errors(tree)


def test_a_tree_checked_out_with_crlf_passes(tree: Path) -> None:
    for rel in (CANONICAL, *copies(tree)):
        _to_crlf(tree / rel)
    assert check(tree) == []


def test_copy_without_markers_fails(tree: Path) -> None:
    _edit(tree, CLAUDE_MD, BEGIN + "\n", "")
    _edit(tree, CLAUDE_MD, "\n" + END, "")
    assert f"RC-2 {CLAUDE_MD}: expected one {BEGIN}" in _errors(tree)


def test_new_skill_without_the_core_fails(tree: Path) -> None:
    (tree / "new-skill").mkdir()
    (tree / "new-skill" / "SKILL.md").write_text("# New skill\n", encoding="utf-8")
    assert f"RC-2 new-skill/SKILL.md: expected one {BEGIN}" in _errors(tree)


def test_copy_with_block_twice_fails(tree: Path) -> None:
    text = (tree / SKILL).read_text(encoding="utf-8")
    block = f"{BEGIN}\n{_canonical_block()}\n{END}"
    (tree / SKILL).write_text(text + "\n" + block + "\n", encoding="utf-8")
    assert "found 2 occurrence(s)" in _errors(tree)


def test_marker_not_alone_on_its_line_fails(tree: Path) -> None:
    _edit(tree, SKILL, BEGIN + "\n", "Text " + BEGIN + "\n")
    assert "0 on their own line" in _errors(tree)


def test_canonical_markers_reversed_fails(tree: Path) -> None:
    _edit(tree, CANONICAL, BEGIN, "@@BEGIN@@")
    _edit(tree, CANONICAL, END, BEGIN)
    _edit(tree, CANONICAL, "@@BEGIN@@", END)
    assert f"RC-1 {CANONICAL}: {END} comes before {BEGIN}" in _errors(tree)


def test_empty_canonical_block_fails(tree: Path) -> None:
    text = (tree / CANONICAL).read_text(encoding="utf-8")
    head, rest = text.split(BEGIN + "\n", 1)
    _, tail = rest.split(END, 1)
    (tree / CANONICAL).write_text(head + BEGIN + "\n\n" + END + tail, encoding="utf-8")
    assert "block is empty" in _errors(tree)


def test_changed_canonical_fails_every_copy(tree: Path) -> None:
    _edit(tree, CANONICAL, "Do NOT auto-route", "Do not auto-route")
    errors = _errors(tree)
    for rel in copies(tree):
        assert f"RC-2 {rel}: routing-core block differs" in errors


def test_cli_exit_codes(tree: Path) -> None:
    _edit(tree, SKILL, "Do NOT auto-route", "Do not auto-route")
    assert run_script(LINT, "--root", str(tree)).returncode == 1
    (tree / CLAUDE_MD).unlink()
    result = run_script(LINT, "--root", str(tree))
    assert result.returncode == 2
    assert f"required file missing: {CLAUDE_MD}" in result.stderr


def _announce(script: Path, source: str, path: str | None = None) -> list[str]:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_ROOT"}
    if path is not None:
        env["PATH"] = path
    result = subprocess.run(
        [shutil.which("bash"), str(script)], input=json.dumps({"source": source}), text=True,
        capture_output=True, env=env, check=True,
    )
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"].split("\n\n")


@pytest.mark.parametrize("source, lead", [
    ("startup", "ARS routing discipline: apply it before invoking an ARS skill or dispatching "
                "an ARS agent for a natural-language request."),
    ("clear", "ARS routing discipline: apply it before invoking an ARS skill or dispatching "
              "an ARS agent for a natural-language request."),
    ("resume", "ARS routing discipline, for a new natural-language request: apply it before "
               "invoking an ARS skill or dispatching an ARS agent. Messages inside a workflow "
               "already under way go to that workflow's active skill and are not routed again."),
    ("compact", "ARS routing discipline, for a new natural-language request: apply it before "
                "invoking an ARS skill or dispatching an ARS agent. Messages inside a workflow "
                "already under way go to that workflow's active skill and are not routed again."),
    ("fork", "ARS routing discipline, for a new natural-language request: apply it before "
             "invoking an ARS skill or dispatching an ARS agent. Messages inside a workflow "
             "already under way go to that workflow's active skill and are not routed again."),
])
def test_announce_carries_the_block_for_every_source(source: str, lead: str) -> None:
    paragraphs = _announce(ANNOUNCE, source)
    at = paragraphs.index(lead)
    assert "\n\n".join(paragraphs[at + 1:]) == _canonical_block()


def _plugin_copy(tmp_path: Path) -> Path:
    """The announce script and the canonical file in a plugin-shaped temp tree."""
    script = tmp_path / "scripts" / ANNOUNCE.name
    script.parent.mkdir(parents=True)
    shutil.copyfile(ANNOUNCE, script)
    core = tmp_path / CANONICAL
    core.parent.mkdir(parents=True)
    shutil.copyfile(REPO_ROOT / CANONICAL, core)
    return script


def test_announce_reads_a_crlf_core_file(tmp_path: Path) -> None:
    script = _plugin_copy(tmp_path)
    _to_crlf(tmp_path / CANONICAL)
    assert _announce(script, "startup") == _announce(ANNOUNCE, "startup")


def test_announce_keeps_the_core_on_a_minimal_path(tmp_path: Path) -> None:
    # Only bash and cat: no sed, dirname, or tr (the reader uses builtins).
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for name in ("bash", "cat"):
        (bindir / name).symlink_to(shutil.which(name))
    assert _announce(ANNOUNCE, "startup", path=str(bindir)) == _announce(ANNOUNCE, "startup")


def test_announce_without_the_core_file_still_emits_valid_json(tmp_path: Path) -> None:
    script = tmp_path / "scripts" / ANNOUNCE.name
    script.parent.mkdir(parents=True)
    shutil.copyfile(ANNOUNCE, script)
    context = "\n\n".join(_announce(script, "startup"))
    assert "ARS routing discipline" not in context
    assert "Requests outside academic research and writing do not invoke ARS" in context
