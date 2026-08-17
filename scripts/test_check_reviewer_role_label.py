#!/usr/bin/env python3
"""Mutation tests for the #611 Journal-Fit Reviewer display-name contract."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from check_reviewer_role_label import REQUIRED


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "check_reviewer_role_label.py"
UNCOVERED_PUBLIC_SURFACES = {
    "academic-paper/examples/revision_recovery_example.md": (
        "Journal-Fit Reviewer (serialized source ID EIC):",
    ),
    "academic-pipeline/agents/pipeline_orchestrator_agent.md": (
        "Launch Revision Coaching — the Journal-Fit Reviewer follows",
    ),
    "academic-pipeline/agents/state_tracker_agent.md": (
        "5 Review Reports (Journal-Fit Reviewer + R1 + R2 + R3 + Devil's Advocate)",
    ),
    "academic-pipeline/examples/full_pipeline_example.md": (
        "Journal-Fit Reviewer (serialized source ID EIC):",
        "5 role-separated review reports (Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate)",
    ),
    "academic-pipeline/examples/integrity_failure_recovery.md": (
        "(Journal-Fit Reviewer + R1 Methodology + R2 Domain + R3 Perspective + Devil's Advocate)",
    ),
    "academic-pipeline/examples/mid_entry_example.md": (
        "full: Complete 5-person review (Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate)",
    ),
    "academic-pipeline/references/reproducibility_audit.md": (
        "Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate — five role-separated perspectives",
    ),
    "docs/ARCHITECTURE.md": (
        "5 review reports (Journal-Fit Reviewer + R1 methodology + R2 domain + R3 interdisciplinary + Devil's Advocate)",
    ),
    "docs/PERFORMANCE.md": (
        "Two reviewers (Journal-Fit Reviewer + methodology) each run two phases",
    ),
    "docs/PERFORMANCE.zh-TW.md": (
        "Journal-Fit Reviewer + methodology 兩位 reviewer 各跑兩階段",
    ),
}
REVIEW_DISPATCH_SURFACES = {
    "academic-paper-reviewer/references/re_review_mode_protocol.md": (
        "Contract-governed default re-review invokes neither `eic_agent` nor "
        "`editorial_synthesizer_agent` as an agent-file worker",
    ),
    "docs/ARCHITECTURE.md": (
        "**Contract-governed re-review dispatch**: orchestrating layer + three "
        "sequential fenced calls",
    ),
    "shared/model_tiering.md": (
        "Stage 3' uses three dedicated contract judgment calls",
        "Do not reuse Stage 3 `eic` or `editorial_synthesizer` workers for Stage 3'",
    ),
    "README.md": (
        "First-round review panel vs. contract-governed re-review dispatch boundary",
    ),
    "README.zh-TW.md": ("第一輪審查面板 vs. 契約治理再審派送的分界",),
    "README.zh-CN.md": ("第一轮审查面板 vs. 契约治理再审调度的分界",),
    "README.ja-JP.md": ("初回レビューパネル vs. 契約管理された再レビューディスパッチの境界",),
    "README.ko-KR.md": ("1차 심사 패널 대 계약 기반 re-review 디스패치 경계",),
}
PROVENANCE_LANGUAGE_SURFACES = {
    ".claude/CLAUDE.md": (
        "a blind and separately executed Devil's Advocate critique",
        "independent Devil's Advocate critique",
    ),
    "docs/SETUP.md": (
        "Cross-model generates a blind, separately executed critique",
        "Cross-model generates independent critique",
    ),
    "deep-research/agents/devils_advocate_agent.md": (
        "needed for a blind, separately executed critique",
        "needed for an independent critique",
    ),
    "shared/handoff_schemas.md": (
        "the blind, separately executed pass evaluates",
        "the independent pass evaluates",
    ),
    "shared/cross_model_verification.md": (
        "blind-separately-executed-DA-critique prompt",
        "independent-DA-critique prompt",
    ),
}
FILES = tuple(
    dict.fromkeys(
        (*REQUIRED, *UNCOVERED_PUBLIC_SURFACES, *REVIEW_DISPATCH_SURFACES)
    )
)


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    for rel in FILES:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / rel, dst)
    return tmp_path


def _mutate(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"anchor missing in {rel}: {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_clean_tree_passes(tree: Path) -> None:
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_public_agent_heading_cannot_regress_to_eic(tree: Path) -> None:
    _mutate(
        tree,
        "academic-paper-reviewer/agents/eic_agent.md",
        "# Journal-Fit Reviewer Agent",
        "# EIC Agent",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "display-label drift" in result.stderr


def test_internal_agent_codename_is_frozen(tree: Path) -> None:
    _mutate(
        tree,
        "academic-paper-reviewer/agents/eic_agent.md",
        "name: eic_agent",
        "name: journal_fit_reviewer_agent",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "internal compatibility token" in result.stderr


def test_internal_contract_role_is_frozen(tree: Path) -> None:
    _mutate(
        tree,
        "academic-paper-reviewer/agents/eic_agent.md",
        "contract_role: eic",
        "contract_role: journal_fit",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "internal compatibility token" in result.stderr


def test_field_card_has_public_display_and_stable_wire_role(tree: Path) -> None:
    rel = "academic-paper-reviewer/agents/field_analyst_agent.md"
    _mutate(
        tree,
        rel,
        "**Display role**: [Journal-Fit Reviewer",
        "**Display role**: [Editor-in-Chief",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "display-label drift" in result.stderr


def test_field_card_preserves_existing_non_eic_role_values(tree: Path) -> None:
    rel = "academic-paper-reviewer/agents/field_analyst_agent.md"
    text = (tree / rel).read_text(encoding="utf-8")
    existing_role_field = (
        "**Role**: [EIC / Peer Reviewer 1 / Peer Reviewer 2 / Peer Reviewer 3]"
    )
    assert existing_role_field in text

    _mutate(
        tree,
        rel,
        existing_role_field,
        "**Role**: [EIC / R1 / R2 / R3]",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "serialized compatibility token" in result.stderr


def test_serialized_source_label_is_not_renamed(tree: Path) -> None:
    rel = "academic-paper-reviewer/templates/editorial_decision_template.md"
    _mutate(tree, rel, "[EIC/R1/R2/R3/DA]", "[JFR/R1/R2/R3/DA]")
    result = _run(tree)
    assert result.returncode == 1
    assert "serialized compatibility token" in result.stderr


def test_other_reviewer_cannot_restore_eic_verdict_display(tree: Path) -> None:
    rel = "academic-paper-reviewer/agents/methodology_reviewer_agent.md"
    _mutate(
        tree,
        rel,
        "Journal-Fit Reviewer recommendation, domain expertise score",
        "EIC verdict, domain expertise score",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "display-label drift" in result.stderr


def test_shipped_card_requires_display_role_but_keeps_eic_source_id(tree: Path) -> None:
    rel = "academic-paper-reviewer/examples/hei_paper_review_example.md"
    _mutate(
        tree,
        rel,
        "**Role**: EIC\n**Display role**: Journal-Fit Reviewer",
        "**Role**: EIC",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "display-label drift" in result.stderr

    tree = tree.parent / "wire-id-case"
    for path in FILES:
        dst = tree / path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / path, dst)
    _mutate(
        tree,
        rel,
        "**Role**: EIC\n**Display role**: Journal-Fit Reviewer",
        "**Role**: JFR\n**Display role**: Journal-Fit Reviewer",
    )
    result = _run(tree)
    assert result.returncode == 1


def test_revision_response_heading_cannot_restore_editor_eic(tree: Path) -> None:
    rel = "academic-paper-reviewer/templates/revision_response_template.md"
    _mutate(
        tree,
        rel,
        "## Response to Journal-Fit Reviewer",
        "## Response to Editor (EIC)",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "display-label drift" in result.stderr


def test_revision_comment_subheadings_use_public_role_name(tree: Path) -> None:
    rel = "academic-paper-reviewer/templates/revision_response_template.md"
    text = (tree / rel).read_text(encoding="utf-8")
    assert "### Journal-Fit Reviewer Comment 1" in text
    assert "### Journal-Fit Reviewer Comment 2" in text

    _mutate(
        tree,
        rel,
        "### Journal-Fit Reviewer Comment 1",
        "### Editor Comment 1",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "display-label drift" in result.stderr


def test_synthesis_keeps_journal_fit_arbitration_as_panel_input(tree: Path) -> None:
    rel = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
    expected = (
        "A genuine SPLIT requires Journal-Fit Reviewer arbitration: the "
        "Journal-Fit Reviewer reviews all positions and makes a binding recommendation."
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(
        tree,
        rel,
        expected,
        "A genuine SPLIT requires synthesizer arbitration and a binding decision.",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "decision-authority drift" in result.stderr


def test_re_review_decision_is_checker_derived_not_reviewer_derived(tree: Path) -> None:
    rel = "academic-paper-reviewer/references/re_review_mode_protocol.md"
    expected = (
        "the closed rules derive the candidate decision state and "
        "`scripts/check_re_review_synthesis.py` recomputes it before surfacing"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(
        tree,
        rel,
        expected,
        "the Journal-Fit Reviewer derives the decision state",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "decision-authority drift" in result.stderr


def test_contract_re_review_uses_dedicated_calls_not_agent_file_roster(
    tree: Path,
) -> None:
    rel = "academic-paper-reviewer/references/re_review_mode_protocol.md"
    expected = (
        "Contract-governed default re-review invokes neither `eic_agent` nor "
        "`editorial_synthesizer_agent` as an agent-file worker"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(
        tree,
        rel,
        expected,
        "Contract-governed default re-review invokes eic_agent and "
        "editorial_synthesizer_agent as a fixed two-agent team",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "internal roster drift" in result.stderr


@pytest.mark.parametrize(
    ("rel", "witness"),
    tuple(
        (rel, witness)
        for rel, witnesses in REVIEW_DISPATCH_SURFACES.items()
        for witness in witnesses
        if rel != "academic-paper-reviewer/references/re_review_mode_protocol.md"
    ),
)
def test_re_review_dispatch_consumers_cannot_restore_a_fixed_agent_team(
    tree: Path, rel: str, witness: str
) -> None:
    text = (tree / rel).read_text(encoding="utf-8")
    assert witness in text
    _mutate(tree, rel, witness, "narrow re-review team: eic + synthesizer")
    result = _run(tree)
    assert result.returncode == 1
    assert "re-review dispatch drift" in result.stderr


def test_compatibility_tokens_never_confer_decision_authority(tree: Path) -> None:
    rel = "academic-paper-reviewer/SKILL.md"
    expected = (
        "Those compatibility tokens do not select a Stage 3' agent file: "
        "`editorial_synthesizer_agent` emits first-round decisions, while "
        "contract-governed re-review uses its three dedicated calls and "
        "checker-derived outcome."
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(
        tree,
        rel,
        expected,
        "Those compatibility tokens grant the Journal-Fit Reviewer decision authority.",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "decision-authority drift" in result.stderr


def test_real_journal_editor_in_chief_remains_distinct(tree: Path) -> None:
    rel = "academic-paper-reviewer/references/editorial_decision_standards.md"
    _mutate(
        tree,
        rel,
        "real journal's Editor-in-Chief (EIC)",
        "real journal's Journal-Fit Reviewer",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "display-label drift" in result.stderr


def test_public_readme_cannot_restore_legacy_role_name(tree: Path) -> None:
    _mutate(
        tree,
        "README.md",
        "(Journal-Fit Reviewer + 3 dynamic reviewers",
        "(EIC + 3 dynamic reviewers",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "display-label drift" in result.stderr


def test_full_mode_example_cannot_regress_to_four_person_panel(tree: Path) -> None:
    rel = "academic-pipeline/examples/full_pipeline_example.md"
    _mutate(
        tree,
        rel,
        "5 role-separated review reports (Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate)",
        "Complete 4-person review",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "panel-cardinality/provenance drift" in result.stderr


def test_full_mode_example_cannot_claim_binary_independence(tree: Path) -> None:
    rel = "academic-pipeline/examples/full_pipeline_example.md"
    _mutate(
        tree,
        rel,
        "5 role-separated review reports",
        "4 independent review reports",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "panel-cardinality/provenance drift" in result.stderr


@pytest.mark.parametrize(
    ("rel", "safe_phrase", "binary_phrase"),
    tuple(
        (rel, phrases[0], phrases[1])
        for rel, phrases in PROVENANCE_LANGUAGE_SURFACES.items()
    ),
)
def test_active_surfaces_cannot_restore_binary_independence(
    tree: Path, rel: str, safe_phrase: str, binary_phrase: str
) -> None:
    _mutate(tree, rel, safe_phrase, binary_phrase)
    result = _run(tree)
    assert result.returncode == 1
    assert "provenance drift" in result.stderr


def test_reviewer_skill_cannot_call_fixed_da_dynamically_configured(tree: Path) -> None:
    rel = "academic-paper-reviewer/SKILL.md"
    _mutate(
        tree,
        rel,
        "dynamically configures 4 card-backed identities (Journal-Fit Reviewer + 3 peer reviewers), and adds the fixed Devil's Advocate as the fifth execution seat",
        "dynamically configures 5 reviewers",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "panel-cardinality/provenance drift" in result.stderr


def test_decision_template_cannot_drop_fixed_da_report(tree: Path) -> None:
    rel = "academic-paper-reviewer/templates/editorial_decision_template.md"
    _mutate(
        tree,
        rel,
        "[Attach all 5 complete reviewer reports — four card-backed scoring reports plus the fixed Devil's Advocate — for the author's reference]",
        "[Attach all 4 complete reviewer reports for the author's reference]",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "panel-cardinality/provenance drift" in result.stderr


@pytest.mark.parametrize(
    ("rel", "witness"),
    tuple(
        (rel, witness)
        for rel, witnesses in UNCOVERED_PUBLIC_SURFACES.items()
        for witness in witnesses
    ),
)
def test_every_changed_public_surface_is_role_linted(
    tree: Path, rel: str, witness: str
) -> None:
    _mutate(tree, rel, witness, witness.replace("Journal-Fit Reviewer", "EIC"))
    result = _run(tree)
    assert result.returncode == 1
    assert rel in result.stderr
    assert "display-label drift" in result.stderr


def test_missing_required_file_is_invocation_error(tree: Path) -> None:
    (tree / FILES[0]).unlink()
    result = _run(tree)
    assert result.returncode == 2
    assert "required file missing" in result.stderr
