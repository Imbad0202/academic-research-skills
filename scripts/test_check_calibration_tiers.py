#!/usr/bin/env python3
"""Mutation tests for the #611 full/directional calibration-tier contract."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "check_calibration_tiers.py"
PROTOCOL = "academic-paper-reviewer/references/calibration_mode_protocol.md"
SKILL = "academic-paper-reviewer/SKILL.md"
RUBRICS = "academic-paper-reviewer/references/quality_rubrics.md"
REGISTRY = "MODE_REGISTRY.md"
SPECTRUM = "shared/mode_spectrum.md"
CROSS_MODEL = "shared/cross_model_verification.md"
CLAUDE = ".claude/CLAUDE.md"
FILES = (PROTOCOL, SKILL, RUBRICS, REGISTRY, SPECTRUM, CROSS_MODEL, CLAUDE)


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


def _remove_fenced_block_after(root: Path, rel: str, marker: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    marker_at = text.index(marker)
    opening = text.index("```", marker_at + len(marker))
    closing = text.index("```", opening + 3) + 3
    path.write_text(text[:opening] + text[closing:], encoding="utf-8")


def _remove_section_from_fenced_block(
    root: Path,
    rel: str,
    marker: str,
    heading: str,
    next_heading: str | None,
) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    marker_at = text.index(marker)
    opening = text.index("```", marker_at + len(marker))
    closing = text.index("```", opening + 3)
    section_at = text.index(heading, opening + 3, closing)
    next_at = (
        text.index(next_heading, section_at + len(heading), closing)
        if next_heading is not None
        else closing
    )
    path.write_text(text[:section_at] + text[next_at:], encoding="utf-8")


def test_clean_tree_passes(tree: Path) -> None:
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_directional_tier_stays_three_papers_one_run(tree: Path) -> None:
    _mutate(tree, PROTOCOL, "exactly 3 papers", "exactly 4 papers")
    result = _run(tree)
    assert result.returncode == 1
    assert "directional shape" in result.stderr


def test_directional_phase0_rechecks_exactly_three_papers(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "**Directional tier:** verify exactly 3 papers",
        "**Directional tier:** verify exactly 4 papers",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional shape" in result.stderr


def test_directional_tier_stays_explicit_opt_in(tree: Path) -> None:
    _mutate(tree, PROTOCOL, "explicitly selects `directional`", "uses calibration")
    result = _run(tree)
    assert result.returncode == 1
    assert "default-tier contract" in result.stderr


def test_directional_gold_composition_is_pinned(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "one `minor_revision`, one `major_revision`, and one extreme anchor",
        "three convenient papers",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional gold composition" in result.stderr


def test_gold_labels_remain_blind_to_panel(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "MUST NOT enter any field-analyst, reviewer, or synthesizer context",
        "may be shown to reviewers",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "gold-label isolation" in result.stderr


def test_per_dimension_gold_scores_remain_blind_to_panel(tree: Path) -> None:
    old = (
        "ground-truth labels, human scores, expected outcomes, and any gold rationale "
        "MUST NOT enter any field-analyst, reviewer, or synthesizer context"
    )
    new = (
        "ground-truth labels, human scores, expected outcomes, "
        "`per_dimension_gold_scores`, and any gold rationale MUST NOT enter any "
        "field-analyst, reviewer, or synthesizer context"
    )
    _mutate(tree, PROTOCOL, new, old)
    result = _run(tree)
    assert result.returncode == 1
    assert "gold-label isolation" in result.stderr


def test_directional_report_cannot_collapse_panel_scores_to_one_number(
    tree: Path,
) -> None:
    header = (
        "| Paper | Gold exact verdict | Panel exact verdict | "
        "Journal-Fit weighted average | R1 weighted average | "
        "R2 weighted average | R3 weighted average | Direction |"
    )
    assert header in (tree / PROTOCOL).read_text(encoding="utf-8")
    _mutate(
        tree,
        PROTOCOL,
        header,
        "| Paper | Gold exact verdict | Panel exact verdict | Rubric score | Direction |",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional report contract" in result.stderr


def test_directional_score_provenance_forbids_aggregation_and_a_da_score(
    tree: Path,
) -> None:
    witness = (
        "Do not average, median, select, or otherwise collapse those four values "
        "into a singular panel score, and do not mint a score for the Devil's Advocate."
    )
    assert witness in (tree / PROTOCOL).read_text(encoding="utf-8")
    _mutate(
        tree,
        PROTOCOL,
        witness,
        "Average the five seats into a singular panel score.",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional score provenance" in result.stderr


def test_directional_forbidden_metrics_are_pinned(tree: Path) -> None:
    _mutate(tree, PROTOCOL, "MUST NOT report", "should usually not report")
    result = _run(tree)
    assert result.returncode == 1
    assert "directional reporting boundary" in result.stderr


@pytest.mark.parametrize(
    ("forbidden_output", "replacement"),
    (
        ("bootstrap confidence intervals", "resampled intervals"),
        ("ensemble stability", "panel stability"),
        ("per-dimension mean absolute calibration error", "dimension score error"),
        ("Lu numeric comparisons", "numeric literature comparisons"),
    ),
)
def test_each_directional_forbidden_output_is_pinned(
    tree: Path, forbidden_output: str, replacement: str
) -> None:
    _mutate(tree, PROTOCOL, forbidden_output, replacement)
    result = _run(tree)
    assert result.returncode == 1
    assert "directional reporting boundary" in result.stderr


def test_minor_major_boundary_matrix_is_pinned(tree: Path) -> None:
    _mutate(tree, PROTOCOL, "harsh crossing", "strict crossing")
    result = _run(tree)
    assert result.returncode == 1
    assert "Minor/Major boundary matrix" in result.stderr


def test_full_tier_and_three_run_override_survive(tree: Path) -> None:
    _mutate(tree, PROTOCOL, "5-20 papers", "3-20 papers")
    result = _run(tree)
    assert result.returncode == 1
    assert "full-tier contract" in result.stderr


def test_fnr_direction_cannot_be_reversed_again(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "FNR is the over-harsh error rate",
        "FNR is the lenient miss rate",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "FNR/FPR interpretation" in result.stderr


def test_five_value_gold_enum_is_pinned(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "`accept`, `minor_revision`, `major_revision`, `reject`, or legacy `borderline`",
        "`accept`, `major_revision`, `reject`, or legacy `borderline`",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "gold-label enum" in result.stderr


def test_directional_exact_results_and_raw_counts_are_pinned(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "the exact gold label, exact panel verdict, and four raw scoring-seat "
        "weighted averages (Journal-Fit Reviewer, R1, R2, R3)",
        "a rounded verdict and summary score",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional raw outputs" in result.stderr


def test_directional_raw_severity_counts_are_pinned(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "raw `low` / `med` / `high` severity-miscalibration-risk counts",
        "a severity-risk summary",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional raw outputs" in result.stderr


def test_full_metrics_cannot_be_silently_deleted(tree: Path) -> None:
    _mutate(tree, PROTOCOL, "| Balanced accuracy |", "| Accuracy |")
    result = _run(tree)
    assert result.returncode == 1
    assert "full-tier metrics" in result.stderr


def test_existing_panel_engine_and_prompt_semantics_are_frozen(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "same existing calibration-mode panel engine, reviewer prompts, and five-seat/synthesizer semantics",
        "new directional-only reviewer prompts and a smaller panel engine",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "panel-engine invariant" in result.stderr


def test_cross_model_substrate_is_consistent_in_every_panel(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "apply the calibration-specific non-sprint Reviewer 2 transport in **every panel**",
        "apply the calibration-specific transport in at least one panel",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "cross-model substrate" in result.stderr


def test_calibration_has_a_non_sprint_single_call_transport(tree: Path) -> None:
    rel = CROSS_MODEL
    expected = (
        "For each calibration panel, the Reviewer 2 substrate swap is exactly one "
        "stateless provider call"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "Use the reviewer_full two-call sprint transport")
    result = _run(tree)
    assert result.returncode == 1
    assert "calibration transport" in result.stderr


def test_calibration_transport_excludes_sprint_and_gold_inputs(tree: Path) -> None:
    rel = CROSS_MODEL
    expected = (
        "MUST NOT send a sprint contract, a paper-blind Phase 1 request, "
        "`<phase1_output>`, any gold label, human score, per-dimension gold, "
        "or gold rationale"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "may send the sprint contract and gold labels")
    result = _run(tree)
    assert result.returncode == 1
    assert "calibration transport" in result.stderr


def test_calibration_transport_rejects_manuscript_fence_collisions(
    tree: Path,
) -> None:
    rel = CROSS_MODEL
    expected = r"`</\s*paper_content\b[^>]*>`"
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "the exact lowercase closing tag only")
    result = _run(tree)
    assert result.returncode == 1
    assert "calibration delimiter collision" in result.stderr


def test_calibration_transport_rejects_configuration_fence_collisions(
    tree: Path,
) -> None:
    rel = CROSS_MODEL
    expected = r"`</\s*reviewer_configuration\b[^>]*>`"
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "the exact lowercase closing tag only")
    result = _run(tree)
    assert result.returncode == 1
    assert "calibration delimiter collision" in result.stderr


def test_calibration_transport_never_rewrites_colliding_source_bytes(
    tree: Path,
) -> None:
    rel = CROSS_MODEL
    expected = (
        "MUST NOT escape, strip, rewrite, truncate, switch delimiters, or fall "
        "back to primary routing"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "escape the delimiter and continue dispatch")
    result = _run(tree)
    assert result.returncode == 1
    assert "calibration delimiter collision" in result.stderr


def test_calibration_collision_refusal_sends_no_provider_call(tree: Path) -> None:
    rel = CROSS_MODEL
    expected = (
        "refuse the entire calibration attempt before transport and send no "
        "provider call containing either payload"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "warn and continue with the provider call")
    result = _run(tree)
    assert result.returncode == 1
    assert "calibration delimiter collision" in result.stderr


def test_calibration_collision_matcher_keeps_longer_tag_boundary(
    tree: Path,
) -> None:
    rel = CROSS_MODEL
    expected = "a different longer tag such as `</paper_contents>` does not match"
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "`</paper_contents>` also matches")
    result = _run(tree)
    assert result.returncode == 1
    assert "calibration delimiter collision" in result.stderr


def test_cross_model_failure_invalidates_the_whole_calibration_attempt(
    tree: Path,
) -> None:
    rel = CROSS_MODEL
    expected = (
        "mark the entire attempt invalid; every completed panel in that attempt "
        "becomes diagnostic-only and MUST NOT enter any aggregate"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "fall back only the failed panel and keep aggregating")
    result = _run(tree)
    assert result.returncode == 1
    assert "attempt-atomic fallback" in result.stderr


def test_calibration_restart_cannot_resume_at_the_failed_panel(tree: Path) -> None:
    rel = CROSS_MODEL
    expected = (
        "new `attempt_id`, an empty aggregate, and a restart at paper 1 / "
        "replicate 1"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "the same attempt_id resumed at the failed panel")
    result = _run(tree)
    assert result.returncode == 1
    assert "attempt-atomic fallback" in result.stderr


def test_calibration_override_does_not_change_reviewer_full_fallback(
    tree: Path,
) -> None:
    rel = CROSS_MODEL
    expected = (
        "This attempt-atomic override is calibration-only; ordinary "
        "`reviewer_full` keeps the per-seat disclosed fallback above."
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "All reviewer modes use attempt-atomic fallback.")
    result = _run(tree)
    assert result.returncode == 1
    assert "attempt-atomic fallback" in result.stderr


def test_skill_cross_model_section_names_calibration_exception(tree: Path) -> None:
    rel = SKILL
    expected = (
        "Calibration is the explicit exception: it uses the canonical "
        "calibration-specific non-sprint, single-call Reviewer 2 transport and "
        "attempt-atomic substrate plan"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "Calibration has no cross-model exception.")
    result = _run(tree)
    assert result.returncode == 1
    assert "SKILL calibration summary" in result.stderr


def test_project_guidance_points_to_the_calibration_transport_exception(
    tree: Path,
) -> None:
    rel = CLAUDE
    expected = (
        "Calibration is the sole explicit exception and uses the canonical "
        "non-sprint single-call transport"
    )
    text = (tree / rel).read_text(encoding="utf-8")
    assert expected in text
    _mutate(tree, rel, expected, "Calibration reuses reviewer_full transport.")
    result = _run(tree)
    assert result.returncode == 1
    assert "project guidance" in result.stderr


def test_directional_output_contract_rejects_metric_insertion(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n- FNR: 0.25\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


def test_directional_output_contract_rejects_metric_insertion_as_prose(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n- Balanced accuracy is 0.75\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


@pytest.mark.parametrize(
    "claim",
    (
        "Overall error rate: 33%",
        "This measured the reviewer error profile",
    ),
)
def test_directional_generic_error_profile_claim_is_rejected(
    tree: Path, claim: str
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        f"## Directional raw counts\n- {claim}\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


@pytest.mark.parametrize(
    "non_measurement",
    (
        "Overall error rate: not measured",
        "The reviewer error profile was not measured",
    ),
)
def test_directional_generic_error_profile_non_measurement_is_legal(
    tree: Path, non_measurement: str
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        f"## Directional raw counts\n- {non_measurement}\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "comparison",
    (
        "Lu baseline: 0.65",
        "| Lu Automated Reviewer | 0.65 |",
        "Lu 2026 Automated Reviewer: 0.65",
    ),
)
def test_directional_lu_numeric_comparison_without_year_is_rejected(
    tree: Path, comparison: str
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        f"## Directional raw counts\n{comparison}\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "forbidden Lu numeric comparison" in result.stderr


def test_directional_wrapped_lu_numeric_comparison_is_rejected(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n"
        "- Lu baseline\n"
        "  = 0.65\n"
        "- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


def test_directional_lu_table_reference_without_comparison_is_legal(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n"
        "- Lu Table 1 is cited for context; no numeric comparison is reported\n"
        "- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_directional_lu_numeric_comparison_non_measurement_is_legal(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n"
        "- Lu numeric comparisons were not reported\n"
        "- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_directional_output_contract_allows_explicit_non_measurement(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n- Balanced accuracy is not measured\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_directional_wrapped_metric_name_cannot_bypass_output_contract(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n- Balanced\n  accuracy: 0.75\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


def test_directional_wrapped_non_measurement_remains_legal(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n"
        "- Balanced\n"
        "  accuracy is not measured\n"
        "- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_directional_non_measurement_cannot_launder_a_trailing_value(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n"
        "- Balanced accuracy is not measured but 0.75 was observed\n"
        "- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


def test_directional_non_measurement_can_name_the_directional_sample_size(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n- Balanced accuracy is not measured on these 3 papers\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_directional_leading_metric_value_cannot_be_laundered_by_adversative(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n- 0.75 is the balanced accuracy, although it is not measured\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


def test_one_metric_non_measurement_cannot_launder_another_metric_claim(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n- Balanced accuracy is not measured, but FPR is high\n- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


@pytest.mark.parametrize("reported_claim", ("FPR is 25%", "FPR is high"))
def test_same_clause_non_measurement_cannot_launder_another_metric_claim(
    tree: Path, reported_claim: str
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n"
        f"- Balanced accuracy is not measured, {reported_claim}\n"
        "- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


def test_directional_output_rejects_generic_confidence_interval_value(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n"
        "- Confidence interval = [0.20, 0.80]\n"
        "- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output contract" in result.stderr


def test_directional_output_allows_explicit_confidence_interval_non_measurement(
    tree: Path,
) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "## Directional raw counts\n- lenient: <n>",
        "## Directional raw counts\n"
        "- Confidence interval: not measured\n"
        "- lenient: <n>",
    )
    result = _run(tree)
    assert result.returncode == 0, result.stderr


def test_directional_output_marker_cannot_borrow_a_later_fence(tree: Path) -> None:
    _remove_fenced_block_after(
        tree,
        PROTOCOL,
        "The **directional-tier** output is a separate, deliberately non-metric readout:",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional output fenced contract missing" in result.stderr


@pytest.mark.parametrize(
    ("heading", "next_heading"),
    (
        ("## Summary metrics", "## Comparison to Lu 2026 Table 1 baselines"),
        ("## Comparison to Lu 2026 Table 1 baselines", "## Per-dimension calibration error"),
        ("## Per-dimension calibration error", "## Minor/Major boundary sub-matrix"),
        ("## Minor/Major boundary sub-matrix", "## Severity-miscalibration histogram (#215)"),
        ("## Severity-miscalibration histogram (#215)", "## Systematic biases detected"),
        ("## Systematic biases detected", "## Recommendations for session use"),
        ("## Recommendations for session use", None),
    ),
)
def test_each_full_report_section_is_bound_to_the_emitted_fence(
    tree: Path, heading: str, next_heading: str | None
) -> None:
    _remove_section_from_fenced_block(
        tree,
        PROTOCOL,
        "The **full-tier** output document is structured as:",
        heading,
        next_heading,
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "full report contract" in result.stderr


@pytest.mark.parametrize(
    ("heading", "next_heading"),
    (
        ("## Exact per-paper results", "## Directional raw counts"),
        ("## Directional raw counts", "## Minor/Major boundary sub-matrix"),
        ("## Minor/Major boundary sub-matrix", "## Severity-miscalibration risk counts (#215)"),
        ("## Severity-miscalibration risk counts (#215)", "## Interpretation boundary"),
        ("## Interpretation boundary", None),
    ),
)
def test_each_directional_report_section_is_bound_to_the_emitted_fence(
    tree: Path, heading: str, next_heading: str | None
) -> None:
    _remove_section_from_fenced_block(
        tree,
        PROTOCOL,
        "The **directional-tier** output is a separate, deliberately non-metric readout:",
        heading,
        next_heading,
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional report contract" in result.stderr


def test_full_report_block_keeps_not_computable(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "`annotated_n=0` is `NOT COMPUTABLE — adjudicated",
        "`annotated_n=0` is `unavailable — adjudicated",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "full report honesty" in result.stderr


def test_full_disclosure_block_keeps_not_computable(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        ": NOT COMPUTABLE (annotated_n=0/<N>, missing=<N>)`",
        ": unavailable (annotated_n=0/<N>, missing=<N>)`",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "full disclosure honesty" in result.stderr


def test_full_report_discloses_selected_replicate_count(tree: Path) -> None:
    _mutate(tree, PROTOCOL, "Runs per paper: <3|5> (ensembled)", "Runs per paper: 5 (ensembled)")
    result = _run(tree)
    assert result.returncode == 1
    assert "full-tier replicate disclosure" in result.stderr


def test_missing_dimension_gold_scores_cannot_yield_fake_error(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "Without this mapping, per-dimension calibration error is `NOT COMPUTABLE`",
        "Without this mapping, infer per-dimension calibration error from the verdict",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "dimension-gold honesty" in result.stderr


def test_partial_dimension_gold_discloses_coverage_in_report_and_header(
    tree: Path, tmp_path: Path
) -> None:
    report_tree = tmp_path.parent / f"{tmp_path.name}-report"
    disclosure_tree = tmp_path.parent / f"{tmp_path.name}-disclosure"
    shutil.copytree(tree, report_tree)
    shutil.copytree(tree, disclosure_tree)

    _mutate(
        report_tree,
        PROTOCOL,
        "report `annotated_n=<n>/<N>` and `missing=<N-n>` for every dimension",
        "report the available calibration errors",
    )
    report_result = _run(report_tree)
    assert report_result.returncode == 1
    assert "full report honesty" in report_result.stderr

    _mutate(
        disclosure_tree,
        PROTOCOL,
        "`<dimension>: ±X points (annotated_n=<n>/<N>, missing=<N-n>)`",
        "`<dimension>: ±X points (available gold scores only)`",
    )
    disclosure_result = _run(disclosure_tree)
    assert disclosure_result.returncode == 1
    assert "full disclosure honesty" in disclosure_result.stderr


def test_full_report_never_globalizes_partial_dimension_gold(
    tree: Path, tmp_path: Path
) -> None:
    bias_tree = tmp_path.parent / f"{tmp_path.name}-bias"
    recommendation_tree = tmp_path.parent / f"{tmp_path.name}-recommendation"
    shutil.copytree(tree, bias_tree)
    shutil.copytree(tree, recommendation_tree)

    _mutate(
        bias_tree,
        PROTOCOL,
        "by ~8 points vs ground truth (annotated_n=<n>/<N>, missing=<N-n>)",
        "by ~8 points vs ground truth",
    )
    bias_result = _run(bias_tree)
    assert bias_result.returncode == 1
    assert "full report honesty" in bias_result.stderr

    _mutate(
        recommendation_tree,
        PROTOCOL,
        "report only that dimension's observed mean absolute calibration error",
        "treat this reviewer's rubric scores as having calibration error",
    )
    recommendation_result = _run(recommendation_tree)
    assert recommendation_result.returncode == 1
    assert "full report honesty" in recommendation_result.stderr


def test_zero_dimension_gold_discloses_coverage(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "`<dimension>: NOT COMPUTABLE (annotated_n=0/<N>, missing=<N>)`",
        "`<dimension>: NOT COMPUTABLE`",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "full disclosure honesty" in result.stderr


def test_directional_disclosure_cannot_impersonate_full_profile(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "Directional Reviewer Calibration Disclosure (session <id>)",
        "Reviewer Confidence Disclosure (session <id>)",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "tier disclosures" in result.stderr


def test_directional_disclosure_rejects_a_measured_error_rate(tree: Path) -> None:
    _mutate(
        tree,
        PROTOCOL,
        "> stability were not measured. Escalate boundary decisions to human judgement.",
        "> stability were not measured.\n> Overall error rate: 33%.\n"
        "> Escalate boundary decisions to human judgement.",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "directional disclosure contract" in result.stderr


def test_rubric_summary_keeps_directional_epistemic_boundary(tree: Path) -> None:
    _mutate(
        tree,
        RUBRICS,
        "directional evidence, not an error-rate estimate",
        "a measured error-rate estimate",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "rubric disclosure sync" in result.stderr


def test_public_mode_registries_expose_both_tiers(tree: Path) -> None:
    _mutate(
        tree,
        REGISTRY,
        "Explicit 3-paper directional readout or default full Calibration Report",
        "Calibration Report",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "mode registry sync" in result.stderr


def test_skill_summary_cannot_fall_back_to_full_only(tree: Path) -> None:
    _mutate(
        tree,
        SKILL,
        "3-paper directional tier or the 5-20-paper full tier",
        "5-20-paper full tier",
    )
    result = _run(tree)
    assert result.returncode == 1
    assert "SKILL calibration summary" in result.stderr


def test_missing_required_file_is_invocation_error(tree: Path) -> None:
    (tree / PROTOCOL).unlink()
    result = _run(tree)
    assert result.returncode == 2
    assert "required file missing" in result.stderr
