"""Mutation tests for check_decision_contract.py."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts import check_decision_contract as lint

REPO = Path(__file__).resolve().parents[1]
MIRROR_FILES = lint.LIVE_FILES + lint.CONTRACTS + (
    lint.QUALITY, lint.STANDARDS, lint.SKILL,
)


def mirror(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    # The checker intentionally scans these live rule trees recursively.
    for rel in lint.LIVE_ROOTS:
        shutil.copytree(REPO / rel, root / rel)
    for rel in MIRROR_FILES:
        destination = root / rel
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / rel, destination)
    return root


def mutate(root: Path, rel: str, old: str, new: str):
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_unmutated_mirror_passes(tmp_path):
    assert lint.check(mirror(tmp_path)) == []


def test_schema_enum_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, lint.SCHEMA,
        '"editorial_decision=minor_revision"',
        '"editorial_decision=revise"',
    )
    assert lint.check(root)


def test_hybrid_token_on_live_agent_surface_fails(tmp_path):
    root = mirror(tmp_path)
    rel = "academic-paper-reviewer/agents/eic_agent.md"
    mutate(
        root, rel,
        "## Expertise Configuration",
        "reject_or_major_revision\n\n## Expertise Configuration",
    )
    assert lint.check(root)


def test_authority_row_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(root, lint.STANDARDS, "`quick`", "`fast`")
    assert lint.check(root)


def test_threshold_removed_from_single_residency_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(root, lint.QUALITY, "| 65-79 |", "| 66-79 |")
    assert lint.check(root)


def test_threshold_duplicated_on_other_live_surface_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        "Duplicate threshold: 65-79\n\n## 0. Decision Authority by Mode",
    )
    assert lint.check(root)


@pytest.mark.parametrize(
    "wording",
    (
        "Accept applies to scores of 80 points or higher.",
        "Minor Revision applies to 65 points and above.",
        "Major Revision applies to 50 points and above.",
        "Reject applies below 50 points.",
    ),
)
def test_equivalent_threshold_wording_on_live_surface_fails(tmp_path, wording):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        f"{wording}\n\n## 0. Decision Authority by Mode",
    )
    assert lint.check(root)


def test_unrelated_decision_count_does_not_false_positive(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        "The calibration decision reviewed at least 80 submissions.\n\n"
        "## 0. Decision Authority by Mode",
    )
    assert lint.check(root) == []


def test_retired_one_to_five_threshold_in_standards_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, lint.STANDARDS,
        "Every applicable core criterion is positively verified",
        "Average score >= 4.0",
    )
    assert lint.check(root)
