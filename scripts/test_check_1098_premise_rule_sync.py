"""Mutation tests for check_1098_premise_rule_sync.py (#1099).

The shipped repository must pass. Each test copies the three checked files into a
temporary root, breaks one copy of the #1098 sentence, and expects a failure.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts import check_1098_premise_rule_sync as lint

FILES = (lint.SOURCE, lint.DA_AGENT, lint.SKILL)


@pytest.fixture()
def tmp_root(tmp_path: Path) -> Path:
    for rel in FILES:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(lint.REPO_ROOT / rel, target)
    return tmp_path


def _sentence() -> str:
    errors: list[str] = []
    sentence = lint.canonical_sentence(lint.REPO_ROOT, errors)
    assert sentence is not None, errors
    return sentence


def _replace_nth(path: Path, old: str, new: str, index: int) -> None:
    text = path.read_text(encoding="utf-8")
    position = -1
    for _ in range(index + 1):
        position = text.index(old, position + 1)
    path.write_text(text[:position] + new + text[position + len(old):], encoding="utf-8")


COPIES = [
    (rel, index)
    for rel, count in lint.EXPECTED_COPIES.items()
    if rel != lint.SOURCE
    for index in range(count)
]


def test_shipped_repository_passes() -> None:
    assert lint.check() == []


@pytest.mark.parametrize(("rel", "index"), COPIES)
def test_one_reworded_copy_fails(tmp_root: Path, rel: str, index: int) -> None:
    sentence = _sentence()
    reworded = sentence.replace("core claim", "main claim")
    assert reworded != sentence
    _replace_nth(tmp_root / rel, sentence, reworded, index)
    errors = lint.check(tmp_root)
    assert any(rel in error for error in errors), errors


@pytest.mark.parametrize(("rel", "index"), COPIES)
def test_one_removed_copy_fails(tmp_root: Path, rel: str, index: int) -> None:
    _replace_nth(tmp_root / rel, _sentence(), "", index)
    errors = lint.check(tmp_root)
    assert any(rel in error and "exact copies" in error for error in errors), errors


def test_extra_copy_fails(tmp_root: Path) -> None:
    path = tmp_root / lint.SKILL
    path.write_text(path.read_text(encoding="utf-8") + "\n" + _sentence() + "\n", encoding="utf-8")
    errors = lint.check(tmp_root)
    assert any(lint.SKILL in error and "exact copies" in error for error in errors), errors


def test_source_change_alone_fails_every_mirror(tmp_root: Path) -> None:
    sentence = _sentence()
    _replace_nth(tmp_root / lint.SOURCE, sentence, sentence.replace("core claim", "main claim"), 0)
    errors = lint.check(tmp_root)
    assert any(lint.DA_AGENT in error for error in errors), errors
    assert any(lint.SKILL in error for error in errors), errors


def test_missing_fragment_markers_fail(tmp_root: Path) -> None:
    path = tmp_root / lint.SOURCE
    path.write_text(
        path.read_text(encoding="utf-8").replace("da-phase2:BEGIN", "da-phase2:START"),
        encoding="utf-8",
    )
    errors = lint.check(tmp_root)
    assert any("markers not found" in error for error in errors), errors


def test_truncated_canonical_sentence_fails(tmp_root: Path) -> None:
    sentence = _sentence()
    _replace_nth(tmp_root / lint.SOURCE, sentence, "Short rule (#1098).", 0)
    errors = lint.check(tmp_root)
    assert any("truncated" in error for error in errors), errors


def test_stray_noncanonical_ending_fails(tmp_root: Path) -> None:
    path = tmp_root / lint.SKILL
    path.write_text(path.read_text(encoding="utf-8") + "\nExtra rule (#1098).\n", encoding="utf-8")
    errors = lint.check(tmp_root)
    assert any(lint.SKILL in error and "differs from the canonical" in error for error in errors), errors
    assert not any("exact copies" in error for error in errors), errors


def test_line_break_hiding_an_edit_fails(tmp_root: Path) -> None:
    sentence = _sentence()
    edited = sentence.replace("does not support", "does support").replace(
        " must be a CRITICAL or MAJOR", "\nmust be a CRITICAL or MAJOR"
    )
    assert "\n" in edited and "does support" in edited
    _replace_nth(tmp_root / lint.SOURCE, sentence, edited, 0)
    errors = lint.check(tmp_root)
    assert any("must sit on one line" in error for error in errors), errors


def test_copy_moved_between_da_sections_fails(tmp_root: Path) -> None:
    sentence = _sentence()
    path = tmp_root / lint.DA_AGENT
    _replace_nth(path, sentence, "", 2)
    _replace_nth(path, sentence, sentence + " " + sentence, 1)
    errors = lint.check(tmp_root)
    assert not any("exact copies" in error for error in errors), errors
    assert any("Frame-Lock Detection" in error and "found 0" in error for error in errors), errors
    assert any("Stakeholder Blind Spots" in error and "found 2" in error for error in errors), errors


def test_missing_da_section_heading_fails(tmp_root: Path) -> None:
    path = tmp_root / lint.DA_AGENT
    path.write_text(
        path.read_text(encoding="utf-8").replace("### Frame-Lock Detection", "### Frame Lock"),
        encoding="utf-8",
    )
    errors = lint.check(tmp_root)
    assert any("must appear exactly once" in error for error in errors), errors


def test_fenced_example_heading_inside_a_section_passes(tmp_root: Path) -> None:
    path = tmp_root / lint.DA_AGENT
    heading = "### Frame-Lock Detection\n"
    path.write_text(
        path.read_text(encoding="utf-8").replace(heading, heading + "\n```markdown\n## Example\n```\n"),
        encoding="utf-8",
    )
    assert lint.check(tmp_root) == []


@pytest.mark.parametrize("heading", ["### Frame-Lock Detection", "### Origin"])
def test_duplicated_boundary_heading_fails(tmp_root: Path, heading: str) -> None:
    path = tmp_root / lint.DA_AGENT
    path.write_text(path.read_text(encoding="utf-8") + "\n```\n" + heading + "\n```\n", encoding="utf-8")
    errors = lint.check(tmp_root)
    assert any(heading in error and "found 2" in error for error in errors), errors


def test_boundary_heading_out_of_order_fails(tmp_root: Path) -> None:
    path = tmp_root / lint.DA_AGENT
    text = path.read_text(encoding="utf-8")
    origin = "### Origin\n"
    text = text.replace(origin, "")
    path.write_text(text.replace("### Frame-Lock Detection\n", origin + "### Frame-Lock Detection\n"), encoding="utf-8")
    errors = lint.check(tmp_root)
    assert any("must follow" in error for error in errors), errors
