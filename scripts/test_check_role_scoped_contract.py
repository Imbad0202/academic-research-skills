"""Mutation tests for check_role_scoped_contract.py."""
from __future__ import annotations

import shutil
from pathlib import Path

from scripts import check_role_scoped_contract as lint

REPO = Path(__file__).resolve().parents[1]
MIRROR_FILES = tuple(lint.CONTRACTS) + tuple(lint.AGENTS) + (
    lint.PROTOCOL, lint.SYNTH, lint.PANEL_CHECKER,
)


def mirror(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for rel in MIRROR_FILES:
        destination = root / rel
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


def test_eligibility_map_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, "shared/contracts/reviewer/full.json",
        '"eligible_roles": ["methodology"]',
        '"eligible_roles": ["eic"]',
    )
    assert lint.check(root)


def test_delivered_phase1_literal_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, next(iter(lint.AGENTS)),
        "`what_triggers_fatal: <single-line non-empty text>`",
        "`fatal_trigger: <single-line non-empty text>`",
    )
    assert lint.check(root)


def test_delivered_phase2_literal_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, next(iter(lint.AGENTS)),
        "block_class: <fatal|repairable>",
        "block_kind: <fatal|repairable>",
    )
    assert lint.check(root)


def test_protocol_pattern_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, lint.PROTOCOL,
        "any dimension scores '<score>' or worse",
        "some dimension scores '<score>' or worse",
    )
    assert lint.check(root)


def test_da_old_no_scoring_clause_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md",
        "Score any dimension outside the contract's `eligible_roles` for `da`",
        "Score the paper — your job is to challenge, not score.",
    )
    assert lint.check(root)
