#!/usr/bin/env python3
"""Mutation tests for the #1030 card-confirmation pause."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from check_reviewer_card_confirmation import (
    FLOW_LITERAL,
    RETIRED,
    RULE_LITERALS,
    RULE_PREFIX,
    SKILL,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "check_reviewer_card_confirmation.py"


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    dst = tmp_path / SKILL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO_ROOT / SKILL, dst)
    return tmp_path


def _mutate(root: Path, old: str, new: str) -> None:
    # Match across any whitespace run, as the lint does, so rewrapping a
    # pinned sentence does not break its mutation test.
    path = root / SKILL
    text = path.read_text(encoding="utf-8")
    pattern = r"\s+".join(re.escape(word) for word in old.split())
    mutated, count = re.subn(pattern, lambda _: new, text, count=1)
    assert count == 1, f"anchor missing: {old!r}"
    path.write_text(mutated, encoding="utf-8")


def test_clean_tree_passes(tree: Path) -> None:
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_missing_skill_is_exit_2(tmp_path: Path) -> None:
    assert _run(tmp_path).returncode == 2


@pytest.mark.parametrize("literal", RULE_LITERALS)
def test_each_rule_literal_is_load_bearing(tree: Path, literal: str) -> None:
    _mutate(tree, literal, "")
    result = _run(tree)
    assert result.returncode == 1
    assert "rule 1 lacks" in result.stderr


def test_calibration_exemption_cannot_flip(tree: Path) -> None:
    _mutate(tree, "`calibration` does not pause,", "`calibration` also pauses,")
    result = _run(tree)
    assert result.returncode == 1
    assert "rule 1 lacks" in result.stderr


def test_rewrapped_rule_still_passes(tree: Path) -> None:
    literal = RULE_LITERALS[1]
    _mutate(tree, literal, literal.replace(" until ", "\n   until "))
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_rule_cannot_lose_iron_rule_marker(tree: Path) -> None:
    _mutate(tree, RULE_PREFIX, "1. **After Phase 0 completes**")
    result = _run(tree)
    assert result.returncode == 1
    assert "must open with" in result.stderr


def test_flow_line_cannot_regress(tree: Path) -> None:
    _mutate(tree, FLOW_LITERAL, f"** {RETIRED[1]} **")
    result = _run(tree)
    assert result.returncode == 1
    assert "retired pre-#1030 wording" in result.stderr
    assert "flow line" in result.stderr


def test_retired_rule_wording_fails_even_beside_the_new_rule(tree: Path) -> None:
    _mutate(
        tree,
        "2. ⚠️ **IRON RULE**",
        f"   - {RETIRED[0]}\n2. ⚠️ **IRON RULE**",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "retired pre-#1030 wording" in result.stderr


def test_rewrapped_retired_wording_still_fails(tree: Path) -> None:
    wrapped = RETIRED[0].replace("; ", ";\n   ")
    _mutate(tree, "2. ⚠️ **IRON RULE**", f"   - {wrapped}\n2. ⚠️ **IRON RULE**")
    result = _run(tree)
    assert result.returncode == 1
    assert "retired pre-#1030 wording" in result.stderr


def test_literal_moved_out_of_rule_one_fails(tree: Path) -> None:
    # A load-bearing sentence relocated to rule 2 no longer binds Phase 1.
    literal = RULE_LITERALS[1]
    _mutate(tree, literal, "")
    _mutate(tree, "2. ⚠️ **IRON RULE**", f"2. ⚠️ **IRON RULE** {literal}")
    result = _run(tree)
    assert result.returncode == 1
    assert "rule 1 lacks" in result.stderr
