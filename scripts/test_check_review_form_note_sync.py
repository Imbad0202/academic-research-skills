#!/usr/bin/env python3
"""Tests for check_review_form_note_sync.py (#921).

Mutation tests confirm the lint is not accept-all: every break in the marker
grammar, in a surface's bytes, or in the note's neutral option list must fail
it, and the clean repository must pass.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts.check_review_form_note_sync import (
    BEGIN,
    CANONICAL,
    END,
    NEUTRALITY,
    SURFACES,
    check,
    extract_block,
)
from tests.test_helpers import run_script

REPO_ROOT = Path(__file__).resolve().parents[1]
LINT = REPO_ROOT / "scripts" / "check_review_form_note_sync.py"
SKILL = Path("academic-paper/SKILL.md")
PHRASE = "The author decides whether to run a systematic review."
EN_SCOPING = "> - **Scoping review**: maps what has been studied"
ZH_SCOPING = "> - **範疇回顧（scoping review）**：用系統化的做法"
EN_NEUTRALITY = NEUTRALITY[0].removeprefix("> ")
EN_NO_FORMAL = "It does not claim to cover the literature."
ZH_NO_FORMAL = "不宣稱涵蓋整體文獻。"


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


def _edit_everywhere(root: Path, old: str, new: str) -> None:
    """Change the canonical block and every copy, so only RF-3 can fail."""
    for rel in (CANONICAL, *SURFACES):
        _edit(root, rel, old, new)


def _line(root: Path, prefix: str) -> str:
    """The first canonical line that starts with `prefix`."""
    text = (root / CANONICAL).read_text(encoding="utf-8")
    return next(line for line in text.split("\n") if line.startswith(prefix))


def _errors(root: Path) -> str:
    return "\n".join(check(root))


def test_repository_passes() -> None:
    result = run_script(LINT, "--root", str(REPO_ROOT))
    assert result.returncode == 0, result.stderr
    assert "2 surfaces match" in result.stdout


def test_canonical_lists_every_surface() -> None:
    text = (REPO_ROOT / CANONICAL).read_text(encoding="utf-8")
    for rel in SURFACES:
        assert f"`{rel}`" in text


def test_copied_tree_passes(tree: Path) -> None:
    assert check(tree) == []


@pytest.mark.parametrize("rel", SURFACES)
def test_one_changed_byte_in_a_surface_fails(tree: Path, rel: Path) -> None:
    _edit(tree, rel, PHRASE, PHRASE.replace("decides", "Decides"))
    assert f"RF-2 {rel}: review-form note block differs" in _errors(tree)


def test_line_ending_drift_in_a_surface_fails(tree: Path) -> None:
    path = tree / SKILL
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert "differs only in its line ending" in _errors(tree)


def test_surface_without_markers_fails(tree: Path) -> None:
    _edit(tree, SKILL, BEGIN + "\n", "")
    _edit(tree, SKILL, "\n" + END, "")
    assert f"RF-2 {SKILL}: expected one {BEGIN}" in _errors(tree)


def test_surface_with_block_twice_fails(tree: Path) -> None:
    block, errors = extract_block((REPO_ROOT / CANONICAL).read_text(encoding="utf-8"), "t")
    assert block is not None, errors
    text = (tree / SKILL).read_text(encoding="utf-8")
    (tree / SKILL).write_text(f"{text}\n{BEGIN}\n{block}\n{END}\n", encoding="utf-8")
    assert "found 2 occurrence(s)" in _errors(tree)


def test_marker_not_alone_on_its_line_fails(tree: Path) -> None:
    _edit(tree, SKILL, BEGIN + "\n", "Text " + BEGIN + "\n")
    assert "0 on their own line" in _errors(tree)


def test_canonical_markers_reversed_fails(tree: Path) -> None:
    _edit(tree, CANONICAL, BEGIN, "@@BEGIN@@")
    _edit(tree, CANONICAL, END, BEGIN)
    _edit(tree, CANONICAL, "@@BEGIN@@", END)
    assert f"RF-1 {CANONICAL}: {END} comes before {BEGIN}" in _errors(tree)


def test_empty_canonical_block_fails(tree: Path) -> None:
    text = (tree / CANONICAL).read_text(encoding="utf-8")
    head, rest = text.split(BEGIN + "\n", 1)
    _, tail = rest.split(END, 1)
    (tree / CANONICAL).write_text(head + BEGIN + "\n\n" + END + tail, encoding="utf-8")
    assert "block is empty" in _errors(tree)


def test_changed_canonical_fails_every_surface(tree: Path) -> None:
    _edit(tree, CANONICAL, PHRASE, PHRASE.replace("decides", "Decides"))
    errors = _errors(tree)
    for rel in SURFACES:
        assert f"RF-2 {rel}: review-form note block differs" in errors


@pytest.mark.parametrize(
    ("old", "new", "word"),
    [
        (EN_SCOPING, EN_SCOPING + " Recommended for most theses.", "Recommended"),
        (EN_SCOPING, EN_SCOPING + " (default)", "default"),
        (EN_SCOPING, EN_SCOPING + " Often the best fit.", "best"),
        (EN_NO_FORMAL, "Least effort; " + EN_NO_FORMAL, "Least"),
        (ZH_SCOPING, ZH_SCOPING + "（推薦）", "推薦"),
        (ZH_SCOPING, ZH_SCOPING + "多數論文較適合", "較適合"),
        (ZH_NO_FORMAL, "最省力，但" + ZH_NO_FORMAL, "最"),
        ("> Reply with the form you want", "> We suggest a systematic review. Reply with the form you want",
         "suggest"),
    ],
)
def test_ranking_word_in_the_note_fails(tree: Path, old: str, new: str, word: str) -> None:
    _edit_everywhere(tree, old, new)
    errors = _errors(tree)
    assert f"carries the ranking word {word!r}" in errors
    assert "RF-2" not in errors


@pytest.mark.parametrize("mark", ["[x] ", "✅ ", "(*) "])
def test_selection_mark_on_an_option_fails(tree: Path, mark: str) -> None:
    _edit_everywhere(tree, EN_NO_FORMAL, EN_NO_FORMAL + " " + mark)
    errors = _errors(tree)
    assert f"carries the selection mark {mark.strip()!r}" in errors


def test_replaced_neutrality_sentence_fails(tree: Path) -> None:
    _edit_everywhere(tree, EN_NEUTRALITY, "We recommend a systematic review.")
    errors = _errors(tree)
    assert "(English):** lacks its neutrality sentence verbatim" in errors
    assert "carries the ranking word 'recommend'" in errors


def test_ranking_word_inside_another_word_passes(tree: Path) -> None:
    _edit_everywhere(tree, EN_NO_FORMAL, EN_NO_FORMAL + " Asbestos studies included.")
    assert check(tree) == []


def test_crlf_in_every_file_passes(tree: Path) -> None:
    for rel in (CANONICAL, *SURFACES):
        path = tree / rel
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert check(tree) == []


def test_dropped_option_fails(tree: Path) -> None:
    line = _line(tree, "> - **Rapid review**")
    _edit_everywhere(tree, line + "\n", "")
    assert "(English):** lists 4 options, expected 5" in _errors(tree)


def test_sixth_unbolded_option_fails(tree: Path) -> None:
    _edit_everywhere(tree, "> - **No formal review**", "> - Umbrella review: a review of reviews.\n> - **No formal review**")
    assert "(English):** lists 6 options, expected 5" in _errors(tree)


@pytest.mark.parametrize(
    "inserted",
    [
        "We recommend a systematic review.",
        "  > - Umbrella review: a review of reviews.",
    ],
)
def test_line_outside_the_quote_fails(tree: Path, inserted: str) -> None:
    _edit_everywhere(tree, EN_NEUTRALITY + "\n", EN_NEUTRALITY + "\n" + inserted + "\n")
    assert f"(English):** has a line outside the quoted note text: {inserted!r}" in _errors(tree)


def test_relabelled_option_fails(tree: Path) -> None:
    _edit_everywhere(tree, "> - **Scoping review**: maps", "> - **Mapping review**: a Scoping review maps")
    assert "(English):** option out of order or relabelled" in _errors(tree)


def test_reordered_options_fail(tree: Path) -> None:
    first = _line(tree, "> - **系統性回顧")
    second = _line(tree, "> - **範疇回顧")
    _edit_everywhere(tree, first + "\n" + second, second + "\n" + first)
    assert "(Traditional Chinese):** option out of order or relabelled" in _errors(tree)


def test_missing_language_fails(tree: Path) -> None:
    _edit_everywhere(tree, "**Note text (Traditional Chinese):**", "**Note text (zh):**")
    assert "heading **Note text (Traditional Chinese):** is missing" in _errors(tree)


def test_cli_exit_codes(tree: Path) -> None:
    _edit(tree, SKILL, PHRASE, PHRASE.replace("decides", "Decides"))
    assert run_script(LINT, "--root", str(tree)).returncode == 1
    (tree / SKILL).unlink()
    result = run_script(LINT, "--root", str(tree))
    assert result.returncode == 2
    assert f"required file missing: {SKILL}" in result.stderr
