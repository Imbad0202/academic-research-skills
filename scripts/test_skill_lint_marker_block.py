#!/usr/bin/env python3
"""Tests for the shared marker-block sync helpers in _skill_lint.py (#923).

check_routing_core_sync, check_method_weaknesses_sync, and
check_review_form_note_sync all call these helpers, so the marker grammar is
tested here once. Each lint's own test file keeps its wiring tests: the
repository passes, every listed surface is checked, and the CLI exit codes.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts._skill_lint import (
    check_marker_copies,
    extract_marker_block,
    first_difference,
)

BEGIN = "<!-- sample:begin -->"
END = "<!-- sample:end -->"
NAME = "sample"
BLOCK = "line one\nline two"
CANONICAL = Path("canonical.md")
COPIES = (Path("a/copy.md"), Path("b/copy.md"))


def _wrap(block: str = BLOCK, head: str = "Intro\n", tail: str = "\nOutro\n") -> str:
    return f"{head}{BEGIN}\n{block}\n{END}{tail}"


def _extract(text: str) -> tuple[str | None, list[str]]:
    return extract_marker_block(text, "L", BEGIN, END, NAME)


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    for rel in (CANONICAL, *COPIES):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(_wrap(), encoding="utf-8")
    return tmp_path


def _check(root: Path) -> tuple[str | None, str]:
    block, errors = check_marker_copies(root, CANONICAL, COPIES, BEGIN, END, NAME, "X-1", "X-2")
    return block, "\n".join(errors)


def test_block_between_markers_is_returned() -> None:
    assert _extract(_wrap()) == (BLOCK, [])


def test_marker_line_may_end_in_cr_and_the_block_keeps_its_crs() -> None:
    block, errors = _extract(_wrap().replace("\n", "\r\n"))
    assert errors == []
    assert block == BLOCK.replace("\n", "\r\n") + "\r"


def test_missing_markers_fail() -> None:
    block, errors = _extract("no markers here\n")
    assert block is None
    assert f"L: expected one {BEGIN} alone on its line, found 0 occurrence(s)" in errors[0]
    assert f"L: expected one {END} alone on its line, found 0 occurrence(s)" in errors[1]


def test_block_twice_fails() -> None:
    _, errors = _extract(_wrap() + _wrap())
    assert "found 2 occurrence(s), 2 on their own line" in "\n".join(errors)


def test_marker_not_alone_on_its_line_fails() -> None:
    _, errors = _extract(_wrap().replace(BEGIN, "Text " + BEGIN))
    assert "found 1 occurrence(s), 0 on their own line" in errors[0]


def test_reversed_markers_fail() -> None:
    text = f"{END}\n{BLOCK}\n{BEGIN}\n"
    assert _extract(text) == (None, [f"L: {END} comes before {BEGIN}"])


def test_empty_block_fails_and_names_the_block() -> None:
    assert _extract(_wrap(block="  ")) == (None, [f"L: the {NAME} block is empty"])


@pytest.mark.parametrize(
    ("copy", "expected"),
    [
        ("line one\nline 2", "block line 2 differs"),
        ("line one\r\nline two", "block line 1 differs only in its line ending"),
        ("line one", "block has 1 lines, canonical has 2"),
    ],
)
def test_first_difference(copy: str, expected: str) -> None:
    assert first_difference(copy, BLOCK) == expected


def test_matching_copies_pass(tree: Path) -> None:
    assert _check(tree) == (BLOCK, "")


def test_changed_copy_fails_with_its_id_and_name(tree: Path) -> None:
    (tree / COPIES[1]).write_text(_wrap(block="line one\nline 2"), encoding="utf-8")
    block, errors = _check(tree)
    assert block == BLOCK
    assert errors == f"X-2 {COPIES[1]}: {NAME} block differs from {CANONICAL} (block line 2 differs)"


def test_line_ending_drift_in_one_copy_fails(tree: Path) -> None:
    path = tree / COPIES[0]
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert "differs only in its line ending" in _check(tree)[1]


def test_crlf_everywhere_passes(tree: Path) -> None:
    for rel in (CANONICAL, *COPIES):
        path = tree / rel
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert _check(tree)[1] == ""


def test_malformed_canonical_returns_none_and_skips_the_compare(tree: Path) -> None:
    (tree / CANONICAL).write_text("no markers\n", encoding="utf-8")
    block, errors = _check(tree)
    assert block is None
    assert f"X-1 {CANONICAL}: expected one {BEGIN}" in errors
    assert "differs" not in errors


def test_malformed_copy_is_reported_with_the_copy_id(tree: Path) -> None:
    (tree / COPIES[0]).write_text(_wrap() + _wrap(), encoding="utf-8")
    assert f"X-2 {COPIES[0]}: expected one {BEGIN}" in _check(tree)[1]


def test_missing_file_exits_2(tree: Path) -> None:
    (tree / COPIES[0]).unlink()
    with pytest.raises(SystemExit) as raised:
        _check(tree)
    assert raised.value.code == 2
