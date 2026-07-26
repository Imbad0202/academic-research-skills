#!/usr/bin/env python3
"""Mutation test for check_reviewer_finding_contract.py (#574 behavior batch).

Each retired drift class, re-introduced, must make the lint FAIL: quota
restoration (A1), receipt/contract gutting (A1), anchor vocabulary loss (A2),
severity re-derivation surfaces (A3), base-rate anchors (B1), and the P0-3
overlap-prohibition residue. Positive control confirms the unmutated tree
PASSES.

Run:
    python -m pytest scripts/test_check_reviewer_finding_contract.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "check_reviewer_finding_contract.py"

SCORING_AGENTS = (
    "academic-paper-reviewer/agents/eic_agent.md",
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md",
    "academic-paper-reviewer/agents/domain_reviewer_agent.md",
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md",
)
DA_REL = "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md"
SYNTH_REL = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
TEMPLATE_REL = "academic-paper-reviewer/templates/peer_review_report_template.md"
DECISION_TEMPLATE_REL = "academic-paper-reviewer/templates/editorial_decision_template.md"
STANDARDS_REL = "academic-paper-reviewer/references/editorial_decision_standards.md"
SKILL_REL = "academic-paper-reviewer/SKILL.md"
SCHEMAS_REL = "shared/handoff_schemas.md"
CALIBRATION_REL = "academic-paper-reviewer/references/calibration_mode_protocol.md"
GUIDED_REL = "academic-paper-reviewer/references/guided_mode_protocol.md"
RQT_REL = "academic-paper-reviewer/references/review_quality_thinking.md"
RESPONSE_TEMPLATE_REL = "academic-paper-reviewer/templates/revision_response_template.md"
STATS_REL = "academic-paper-reviewer/references/statistical_reporting_standards.md"
RCF_REL = "academic-paper-reviewer/references/review_criteria_framework.md"
XM_REL = "shared/cross_model_verification.md"
FIELD_ANALYST_REL = "academic-paper-reviewer/agents/field_analyst_agent.md"
DOMAIN_REL = SCORING_AGENTS[2]

ALL_FILES = SCORING_AGENTS + (
    DA_REL, SYNTH_REL, TEMPLATE_REL, DECISION_TEMPLATE_REL, STANDARDS_REL,
    SKILL_REL, SCHEMAS_REL, CALIBRATION_REL, GUIDED_REL, RQT_REL,
    RESPONSE_TEMPLATE_REL, STATS_REL, RCF_REL, XM_REL, FIELD_ANALYST_REL,
)


def _run2(root: Path):
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stderr


def _run(root: Path) -> int:
    return _run2(root)[0]


def _mirror(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for rel in ALL_FILES:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / rel, dst)
    return root


def _edit(root: Path, rel: str, transform) -> None:
    p = root / rel
    p.write_text(transform(p.read_text(encoding="utf-8")), encoding="utf-8")


# --- positive control ---------------------------------------------------------

def test_unmutated_tree_passes(tmp_path):
    root = _mirror(tmp_path)
    code, err = _run2(root)
    assert code == 0, f"baseline tree should PASS, stderr:\n{err}"


def test_b1_band_anchor_mutation_fails(tmp_path):
    root = _mirror(tmp_path)
    _edit(
        root, SCORING_AGENTS[0],
        lambda text: text.replace(
            "if a defect needs sibling findings to reach rejection-level "
            "impact, it is not Critical alone.",
            "clusters may promote each member to Critical.",
            1,
        ),
    )
    code, err = _run2(root)
    assert code == 1
    assert "B1 band anchors missing" in err


def test_template_b1_anti_bundling_mutation_fails(tmp_path):
    root = _mirror(tmp_path)
    _edit(
        root, TEMPLATE_REL,
        lambda text: text.replace(
            "A finding never inherits a higher band from siblings",
            "A finding may inherit a higher band from siblings",
            1,
        ),
    )
    code, err = _run2(root)
    assert code == 1
    assert "expanded B1" in err


# --- A1: quotas + receipt + contract block --------------------------------------

def test_m1_quota_restored_in_agent(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[1],
          lambda t: t.replace("### Weaknesses\n", "### Weaknesses (3-5 items)\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m2_finding_contract_body_gutted(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[0],
          lambda t: t.replace("Do not manufacture findings to fill a quota; do not "
                              "omit real ones to seem agreeable.",
                              "Use your judgment."))
    code, err = _run2(root)
    assert code == 1
    assert "Finding Contract body missing" in err


def test_m3_weakness_field_line_dropped(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[2],
          lambda t: t.replace(
              "   - **Severity**: [Critical / Major / Minor] | **Evidence Anchor**: "
              "[`<type>: <locator>`] | **Confidence**: [1-5 — competence basis]\n", ""))
    code, err = _run2(root)
    assert code == 1
    assert "per-weakness field line" in err


def test_m4_coverage_receipt_skeleton_dropped(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[3],
          lambda t: t.replace(
              "### Coverage Receipt (only when Strengths or Weaknesses is empty)",
              "### Notes"))
    code, err = _run2(root)
    assert code == 1
    assert "coverage-receipt skeleton" in err


def test_m5_every_scoring_agent_is_pinned(tmp_path):
    """Gutting the Finding Contract heading in EACH scoring agent individually
    must fail."""
    for rel in SCORING_AGENTS:
        root = _mirror(tmp_path / rel.replace("/", "_"))
        _edit(root, rel,
              lambda t: t.replace("**Finding Contract (#574 A1/A2/A3)** — governs",
                                  "**Notes** — governs"))
        assert _run(root) == 1, f"removing Finding Contract heading in {rel} must fail"


def test_m6_template_quota_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, TEMPLATE_REL,
          lambda t: t.replace("List every weakness you actually found",
                              "List 3-5 weaknesses of the paper. List every weakness you actually found"))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m7_template_receipt_section_removed(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, TEMPLATE_REL,
          lambda t: t.replace("## Coverage Receipt (conditional *)", "## Extra Notes"))
    code, err = _run2(root)
    assert code == 1
    assert "coverage-receipt section" in err


# --- A2: anchor vocabulary -------------------------------------------------------

def test_m8_template_absence_row_removed(tmp_path):
    root = _mirror(tmp_path)
    def drop_absence_row(t: str) -> str:
        return "\n".join(l for l in t.splitlines() if not l.startswith("| `absence` |")) + "\n"
    _edit(root, TEMPLATE_REL, drop_absence_row)
    code, err = _run2(root)
    assert code == 1
    assert "anchor vocabulary missing type row" in err


def test_m9_template_must_anchor_weakened(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, TEMPLATE_REL,
          lambda t: t.replace("**Critical/Major findings MUST carry an adequate anchor",
                              "**Critical/Major findings should carry an anchor"))
    code, err = _run2(root)
    assert code == 1
    assert "MUST-anchor rule" in err


def test_m10_da_table_loses_anchor_column(tmp_path):
    root = _mirror(tmp_path)
    def strip_critical_anchor_col(t: str) -> str:
        return t.replace(
            "| # | Dimension | Issue Description | Evidence Anchor | Confidence | "
            "Field-Norm Boundary | Evidence-Crossing Rationale |",
            "| # | Dimension | Issue Description | Location | "
            "Field-Norm Boundary | Evidence-Crossing Rationale |", 1)
    _edit(root, DA_REL, strip_critical_anchor_col)
    code, err = _run2(root)
    assert code == 1
    assert "CRITICAL table: missing column" in err


# --- A3: severity single source + transport ---------------------------------------

def test_m11_schema6_canonical_sentence_removed(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SCHEMAS_REL,
          lambda t: t.replace("the CANONICAL single source for finding severity "
                              "across the reviewer stack (#574 A3)",
                              "a severity value"))
    code, err = _run2(root)
    assert code == 1
    assert "canonical-severity sentence" in err


def test_m12_synth_severity_fallback_tag_removed(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SYNTH_REL,
          lambda t: t.replace("[SEVERITY-SOURCE: letter-fallback]", "a note"))
    code, err = _run2(root)
    assert code == 1
    assert "severity fallback tag" in err


def test_m13_da_band_consistency_removed(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, DA_REL,
          lambda t: t.replace("the same defect class with the same decision impact "
                              "lands in the same band every time",
                              "severity is a judgment call"))
    code, err = _run2(root)
    assert code == 1
    assert "band-consistency" in err


def test_m14_standards_severity_column_restored(tmp_path):
    """Re-adding a Severity column to the cross-dimension table recreates the
    second severity-assignment path — must fail."""
    root = _mirror(tmp_path)
    _edit(root, STANDARDS_REL,
          lambda t: t.replace("| Situation | Decision impact |",
                              "| Situation | Severity | Decision impact |"))
    code, err = _run2(root)
    assert code == 1
    assert ("severity-assignment column regression" in err
            or "decision-impact table header" in err)


# --- B1: base rates + symmetry ------------------------------------------------------

def test_m15_synth_base_rate_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SYNTH_REL,
          lambda t: t.replace(
              "Granted whenever the criteria are met — the decision follows the "
              "evidence against `references/editorial_decision_standards.md`, never "
              "a base rate or target distribution (#574 B1)",
              "Rare — most papers don't pass on the first round"))
    code, err = _run2(root)
    assert code == 1
    assert "B1 accept rule" in err or "base-rate anchor regression" in err


def test_m16_standards_b1_principle_gutted(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, STANDARDS_REL,
          lambda t: t.replace("**Register is independent of severity.**",
                              "Politeness matters."))
    code, err = _run2(root)
    assert code == 1
    assert "B1 principle" in err


def test_m17_standards_base_rate_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, STANDARDS_REL,
          lambda t: t.replace("the decision follows the criteria, never a frequency "
                              "expectation (#574 B1: no base-rate anchoring, "
                              "qualitative or numeric)",
                              "rare (< 5% of submissions at top-tier journals)"))
    code, err = _run2(root)
    assert code == 1
    assert ("base-rate anchor regression" in err
            or "frequency-free first-pass acceptance" in err)


def test_m18_eic_acceptance_rate_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[0],
          lambda t: t.replace(
              "never from acceptance-rate base rates",
              "based on journal tier (Q1 journal acceptance rate ~10-15%)"))
    code, err = _run2(root)
    assert code == 1
    assert "venue-criteria rule" in err or "acceptance-rate anchor regression" in err


def test_m21_schema6_anchor_enum_renamed(tmp_path):
    """Renaming one anchor_type enum value in Schema 6 desyncs the machine-facing
    contract from the template vocabulary — must fail."""
    root = _mirror(tmp_path)
    _edit(root, SCHEMAS_REL, lambda t: t.replace('"dataset"', '"data"'))
    code, err = _run2(root)
    assert code == 1
    assert "anchor_type enum" in err


def test_m22_da_anchor_list_partially_edited(tmp_path):
    """Dropping one type from ONE of the DA's two six-type spellings (footnote vs
    discipline rule) must fail — both copies are pinned to ANCHOR_TYPES."""
    root = _mirror(tmp_path)
    _edit(root, DA_REL,
          lambda t: t.replace("`text` / `table` / `figure` / `equation` / `dataset` / `absence`",
                              "`text` / `table` / `figure` / `equation` / `dataset`", 1))
    code, err = _run2(root)
    assert code == 1
    assert "six-type anchor vocabulary" in err


def test_m23_schema6_confidence_row_deleted(tmp_path):
    """Deleting the Schema 6 confidence row must fail — the A3 transport
    contract's machine-facing field (codex round-1 P1: it was unpinned)."""
    root = _mirror(tmp_path)
    def drop_row(t: str) -> str:
        return "\n".join(l for l in t.splitlines()
                         if not l.startswith("| `confidence` | integer |")) + "\n"
    _edit(root, SCHEMAS_REL, drop_row)
    code, err = _run2(root)
    assert code == 1
    assert "Schema 6 weakness field row" in err


def test_m24_da_minor_header_renamed(tmp_path):
    """Renaming the MINOR table's Evidence Anchor column must fail even though
    the shared footnote below still mentions 'Evidence Anchor' (codex round-1
    P2: subsection-wide search was masked by the footnote)."""
    root = _mirror(tmp_path)
    _edit(root, DA_REL,
          lambda t: t.replace("| # | Dimension | Issue Description | Evidence Anchor | Confidence |\n"
                              "|---|-----------|-------------------|-----------------|------------|",
                              "| # | Dimension | Issue Description | Location | Confidence |\n"
                              "|---|-----------|-------------------|----------|------------|"))
    code, err = _run2(root)
    assert code == 1
    assert "MINOR table: missing column" in err


def test_m25_reworded_quota_caught(tmp_path):
    """A quota re-introduced in different words than the retired literals must
    still fail (codex round-1 P2: literal-only patterns were fail-open)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[1],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nYou must include at least 3 weaknesses.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m26_skill_fake_diversity_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SKILL_REL,
          lambda t: t.replace("**Overlap suppression**", "**Duplicate criticisms across reviewers**")
                     .replace("unexecutable under blindness (Iron Rule #2) and destroys the corroboration signal",
                              "R1/R2/R3 raise identical points = fake diversity"))
    code, err = _run2(root)
    assert code == 1
    assert ("overlap-prohibition regression" in err
            or "overlap-suppression anti-pattern row" in err)


def test_m27_synth_mandatory_merit_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SYNTH_REL,
          lambda t: t.replace("Point out genuine merits where the reviewer cards found them — "
                              "never manufacture praise to soften a Reject (#574 A1/B1)",
                              "Point out the paper's merits (they always exist)"))
    code, err = _run2(root)
    assert code == 1
    assert ("mandatory-merit regression" in err or "genuine-merits rule" in err)


def test_m28_da_critical_band_reverted(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, DA_REL,
          lambda t: t.replace("Fatal flaw in core argument or methodology that blocks acceptance "
                              "until fixed — the same decision-impact bar as the canonical Critical "
                              "(template § Severity Levels); state explicitly when you judge it "
                              "unfixable by revision",
                              "Fatal flaw in core argument or methodology that cannot be rescued by revision"))
    code, err = _run2(root)
    assert code == 1
    assert ("DA CRITICAL decision-impact definition" in err
            or "unfixable-only definition" in err)


def test_m30_contract_relocated_outside_phase2(tmp_path):
    """Contract kept verbatim but moved out of the delivered Phase 2 subsection
    (appended at end of file) — sprint calls would never receive it (codex
    round-2 P1). Must fail."""
    root = _mirror(tmp_path)
    rel = SCORING_AGENTS[0]
    def relocate(t: str) -> str:
        start = t.index("**Finding Contract (#574 A1/A2/A3)**")
        end = t.index("  - **Confidence**: 1-5 plus a one-phrase competence basis.", start)
        end = t.index("\n", end) + 1
        block = t[start:end]
        return t.replace(block, "") + "\n---\n\n" + block
    _edit(root, rel, relocate)
    code, err = _run2(root)
    assert code == 1
    assert "OUTSIDE the delivered Phase 2" in err


def test_m31_minimum_of_quota_caught(tmp_path):
    """'a minimum of 3 weaknesses' — the round-2 fail-open rewording — must fail."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[2],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nYou must include a minimum of 3 weaknesses.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m32_da_header_superset_rename(tmp_path):
    """Renaming CRITICAL columns to supersets ('Evidence Anchor Note') defeats
    substring membership — exact cell compare must fail it (round-2 P2)."""
    root = _mirror(tmp_path)
    def rename(t: str) -> str:
        idx = t.index("#### CRITICAL")
        head, tail = t[:idx], t[idx:]
        tail = tail.replace("| Evidence Anchor | Confidence |",
                            "| Evidence Anchor Note | Confidence Basis |", 1)
        return head + tail
    _edit(root, DA_REL, rename)
    code, err = _run2(root)
    assert code == 1
    assert "CRITICAL table: missing column" in err


def test_m33_synth_split_prior_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SYNTH_REL,
          lambda t: t.replace(
              "the divergence is signal about a genuinely weak dimension — decide "
              "from the criteria against that dimension (commonly Major Revision, "
              "because a real weak dimension needs fixing), never from a strictness "
              "prior (#574 B1)",
              "lean toward Major Revision"))
    code, err = _run2(root)
    assert code == 1
    assert ("directional split prior regression" in err
            or "divergence-weighting edge case" in err)


def test_m34_decision_template_conservative_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, DECISION_TEMPLATE_REL,
          lambda t: t.replace("unresolved-dissent principle (#574 B1)", "conservative principle"))
    code, err = _run2(root)
    assert code == 1
    assert ("asymmetric arbitration regression" in err
            or "arbitration rationale vocabulary" in err)


def test_m35_guided_mandatory_opener_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, GUIDED_REL,
          lambda t: t.replace(
              "First acknowledges the paper's genuine core strengths (1-2, when "
              "they exist — never manufactured praise, #574 A1/B1)",
              "First points out 1-2 core strengths of the paper (building confidence)"))
    code, err = _run2(root)
    assert code == 1
    assert ("mandatory-strength opener regression" in err
            or "guided-mode conditional-strengths opener" in err)


def test_m36_rqt_minimum_strength_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, RQT_REL,
          lambda t: t.replace(
              "Did I acknowledge every genuine strength I found — and manufacture "
              "none? (Evidence-driven balance check, #574 A1/B1)",
              "Did I identify at least one genuine strength? (Balance check)"))
    code, err = _run2(root)
    assert code == 1
    assert ("minimum-strength check regression" in err
            or "review-quality balance check" in err)


def test_m37_domain_advisory_disposition_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, DOMAIN_REL,
          lambda t: t.replace(
              "down-rate the finding's severity to **Minor** — the canonical enum "
              "has no off-enum \"advisory\" tier (#574 A3) — and label it",
              "down-rate the finding to advisory and label it"))
    code, err = _run2(root)
    assert code == 1
    assert ("off-enum severity disposition regression" in err
            or "field-norm enum disposition" in err)


def test_m38_strength_anchor_bullet_gutted(tmp_path):
    """Removing the strengths-anchor bullet from the delivered contract lets
    sprint reviews emit unanchored positive findings (round-3 P1)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[1],
          lambda t: t.replace("- Every strength carries a typed Evidence Anchor too "
                              "(the same six-type vocabulary; a section-level locator "
                              "suffices for a strength, and a `text` anchor still "
                              "carries its short verbatim quote — the Schema 6 "
                              "conditional member applies to both polarities) — A2's "
                              "every-finding rule covers strengths and weaknesses "
                              "alike.\n", ""))
    code, err = _run2(root)
    assert code == 1
    assert "Finding Contract body missing" in err


def test_m39_response_template_bounded_again(tmp_path):
    """Restoring the W1-W5 bound in the response template can drop W6+ author
    responses (round-3 P1)."""
    root = _mirror(tmp_path)
    _edit(root, RESPONSE_TEMPLATE_REL,
          lambda t: t.replace("W1..Wn (every emitted weakness, unbounded — #574 A1)",
                              "W1-W5"))
    code, err = _run2(root)
    assert code == 1
    assert ("bounded W-range mirror regression" in err
            or "unbounded W1..Wn witness" in err)


def test_m40_three_to_five_quota_caught(tmp_path):
    """'three to five weaknesses' — a worded range quota — must fail (round-3 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[3],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nProvide three to five weaknesses.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m41_plus_form_quota_caught(tmp_path):
    """'3+ weaknesses' must fail (round-3 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[0],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nAim for 3+ weaknesses.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m42_da_decoy_table_before_output_format(tmp_path):
    """A correctly-shaped decoy CRITICAL table BEFORE ## Output Format must not
    satisfy the column check when the real table loses its columns (round-3 P2)."""
    root = _mirror(tmp_path)
    def decoy(t: str) -> str:
        decoy_block = ("\n#### CRITICAL\n"
                       "| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |\n"
                       "|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|\n\n")
        t = t.replace("## Severity Classification", decoy_block + "## Severity Classification", 1)
        idx = t.index("## Output Format")
        head, tail = t[:idx], t[idx:]
        tail = tail.replace("| Evidence Anchor | Confidence |", "| Location | Notes |", 1)
        return head + tail
    _edit(root, DA_REL, decoy)
    code, err = _run2(root)
    assert code == 1
    assert "CRITICAL table: missing column" in err


def test_m43_perspective_assumption_quota_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[3],
          lambda t: t.replace(
              "Assumption audit was actually performed; implicit assumptions "
              "identified where they exist (an all-explicit paper legitimately "
              "yields none — do not manufacture one, #574 A1)",
              "Assumption audit has identified at least 1 implicit assumption"))
    code, err = _run2(root)
    assert code == 1
    assert ("assumption-audit quota regression" in err
            or "conditional assumption-audit gate" in err)


def test_m44_rqt_base_rate_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, RQT_REL,
          lambda t: t.replace(
              "Check the manuscript's claimed scope of generalization against its "
              "sampling frame — a criterion-only comparison, never an "
              "author-population base rate (#574 B1).",
              "Most authors overstate generalizability."))
    code, err = _run2(root)
    assert code == 1
    assert ("author-population base-rate regression" in err
            or "criterion-only generalizability heuristic" in err)


def test_m45_da_concession_bridge_removed(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, DA_REL,
          lambda t: t.replace("a dispositive score-5 rebuttal always prevails "
                              "regardless of sequence", "the ladder applies"))
    code, err = _run2(root)
    assert code == 1
    assert "concession-ladder B1 bridge" in err


def test_m46_noun_first_quota_caught(tmp_path):
    """'### Weaknesses (at least 3)' — noun-first heading quota — must fail
    (round-4 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[1],
          lambda t: t.replace("### Weaknesses\n", "### Weaknesses (at least 3)\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m47_single_mirror_rebounded(tmp_path):
    """Rebounding ONLY the R3 mirror (W1–W4, en dash) must fail even though R2
    keeps the unbounded witness (round-4 P2)."""
    root = _mirror(tmp_path)
    def rebound_r3(t: str) -> str:
        idx = t.index("## Response to Reviewer 3")
        head, tail = t[:idx], t[idx:]
        tail = tail.replace("W1..Wn (every emitted weakness, unbounded — #574 A1)",
                            "W1–W4", 1)
        return head + tail
    _edit(root, RESPONSE_TEMPLATE_REL, rebound_r3)
    code, err = _run2(root)
    assert code == 1
    assert ("unbounded W1..Wn witness" in err or "bounded W-range mirror regression" in err)


def test_m48_stats_triage_note_removed(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, STATS_REL,
          lambda t: t.replace("**Triage levels, not finding severities (#574 A3).**",
                              "**Severity legend.**"))
    code, err = _run2(root)
    assert code == 1
    assert "red-flag triage note" in err


def test_m49_synth_lone_major_escalation_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SYNTH_REL,
          lambda t: t.replace(
              "Conditions: a validated — or genuinely unresolved — Major issue "
              "exists, or multiple Minor items accumulate to Major. A lone Major "
              "recommendation goes through arbitration FIRST (One-Outlier "
              "handling, `references/editorial_decision_standards.md`): an "
              "outlier whose rationale arbitration finds insufficient does not "
              "escalate the decision by itself (#574 B1)",
              "Conditions: Any reviewer recommends Major Revision, or multiple "
              "Minor items accumulate to Major"))
    code, err = _run2(root)
    assert code == 1
    assert ("lone-Major arbitration rule" in err
            or "unconditional lone-Major escalation regression" in err)


def test_m50_rcf_affirm_first_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, RCF_REL,
          lambda t: t.replace("Affirm genuine strengths first when they exist "
                              "(never manufactured — #574 A1/B1), then point out issues",
                              "Affirm strengths first, then point out issues"))
    code, err = _run2(root)
    assert code == 1
    assert "conditional hypercriticism guidance" in err


def test_m51_schema6_strengths_destructured(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SCHEMAS_REL,
          lambda t: t.replace("Strength objects `{description: string, "
                              "evidence_anchor: object}`",
                              "bare strings"))
    code, err = _run2(root)
    assert code == 1
    assert "structured strengths" in err


def test_m52_direct_count_quota_caught(tmp_path):
    """'List 3 weaknesses' — an imperative direct count — must fail (round-5 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[0],
          lambda t: t.replace("### Weaknesses\n", "### Weaknesses\nList 3 weaknesses.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m53_maximum_quota_caught(tmp_path):
    """'no more than 5 findings' — an upper bound — must fail (round-5 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[1],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nReport no more than 5 findings.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m54_mirror_duplicated_and_deleted(tmp_path):
    """Duplicating the unbounded witness in R2 while deleting it from R3 keeps
    the file-wide count at 2 — the per-mirror check must still fail (round-5 P2)."""
    root = _mirror(tmp_path)
    w = "W1..Wn (every emitted weakness, unbounded — #574 A1)"
    def shuffle(t: str) -> str:
        r3 = t.index("## Response to Reviewer 3")
        head, tail = t[:r3], t[r3:]
        head = head.replace(w, w + " / " + w, 1)   # R2 now carries it twice
        tail = tail.replace(w, "all weaknesses", 1)  # R3 loses it
        return head + tail
    _edit(root, RESPONSE_TEMPLATE_REL, shuffle)
    code, err = _run2(root)
    assert code == 1
    assert "exactly once" in err


def test_m55_wide_bounded_range_caught(tmp_path):
    """'W1-W10' (multi-digit endpoint) must fail (round-5 P2)."""
    root = _mirror(tmp_path)
    _edit(root, RESPONSE_TEMPLATE_REL,
          lambda t: t.replace("W1..Wn (every emitted weakness, unbounded — #574 A1)",
                              "W1-W10", 1))
    code, err = _run2(root)
    assert code == 1
    assert ("bounded W-range mirror regression" in err or "exactly once" in err)


def test_m56_schema6_row_migrated_to_schema7(tmp_path):
    """Moving the confidence row OUT of Schema 6 (re-adding it under Schema 7)
    keeps a file-wide search green — the Schema-6-scoped check must fail
    (round-5 P2)."""
    root = _mirror(tmp_path)
    def migrate(t: str) -> str:
        row = next(l for l in t.splitlines() if l.startswith("| `confidence` | integer |"))
        t = t.replace(row + "\n", "")
        return t.replace("## Schema 7: Revision Roadmap (reviewer -> academic-paper revision)",
                         "## Schema 7: Revision Roadmap (reviewer -> academic-paper revision)\n\n" + row)
    _edit(root, SCHEMAS_REL, migrate)
    code, err = _run2(root)
    assert code == 1
    assert "Schema 6 weakness field row" in err


def test_m57_up_to_maximum_quota_caught(tmp_path):
    """'Report up to five findings' — an accidental maximum — must fail
    (round-6 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[2],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nReport up to five findings.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m58_legit_question_count_does_not_false_fire(tmp_path):
    """'### Questions (2-4 items)' is a NON-finding count and must PASS —
    the lint must not block legitimate prompt edits (round-6 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[0],
          lambda t: t.replace("### Questions for Authors\n",
                              "### Questions for Authors (2-4 items)\n", 1))
    code, err = _run2(root)
    assert code == 0, f"legitimate question count false-fired:\n{err}"


def test_m59_legit_between_prose_does_not_false_fire(tmp_path):
    """'Distinguish between major and minor issues' is ordinary prose and must
    PASS (round-6 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[1],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nDistinguish between major and minor issues.\n", 1))
    code, err = _run2(root)
    assert code == 0, f"legitimate prose false-fired:\n{err}"


def test_m60_subclaim_severity_inheritance_removed(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SYNTH_REL,
          lambda t: t.replace("All sub-claims decomposed from one parent share "
                              "the parent's transported severity",
                              "Sub-claims may be re-rated individually"))
    code, err = _run2(root)
    assert code == 1
    assert "sub-claim severity inheritance" in err


def test_m61_cross_model_da_quota_restored(tmp_path):
    """Restoring 'Find the 3 most serious weaknesses' in the cross-model DA
    prompt must fail (round-7 P1)."""
    root = _mirror(tmp_path)
    _edit(root, XM_REL,
          lambda t: t.replace(
              "Find the most serious weaknesses — every one the evidence supports,\n"
              "   ranked most severe first; no fixed count, and do not pad to reach one\n"
              "   (#574 A1).",
              "Find the 3 most serious weaknesses."))
    code, err = _run2(root)
    assert code == 1
    assert ("cross-model DA fixed-count regression" in err
            or "cross-model DA no-quota prompt" in err)


def test_m62_synth_roadmap_severity_column_dropped(tmp_path):
    """Dropping the Severity column from a roadmap table lets transported
    metadata die in the working inventory (round-7 P1)."""
    root = _mirror(tmp_path)
    _edit(root, SYNTH_REL,
          lambda t: t.replace(
              "| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |",
              "| # | Revision Item | Sub-Claim(s) | Source | Priority | Estimated Effort |", 1))
    code, err = _run2(root)
    assert code == 1
    assert "transported-metadata columns" in err


def test_m63_skill_unconditional_veto_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SKILL_REL,
              lambda t: t.replace(
                  "Every Devil's Advocate CRITICAL issue is adjudicated visibly in the "
                  "Editorial Decision — a validated or genuinely unresolved one blocks "
                  "silent Accept finalization; under a sprint contract the mechanical "
                  "Accept remains unchanged and `[DA-CRITICAL-VS-ACCEPT: <n> "
                  "validated/unresolved]` escalates to the user. One the EIC adjudicates "
                  "and rejects is recorded with its "
                  "rejection rationale and does not veto by itself (#574 B1: an "
                  "unvalidated negative claim carries the same evidence burden as a "
                  "positive one). Silently bypassing a DA CRITICAL is never allowed.",
              "If the Devil's Advocate finds CRITICAL issues, the Editorial "
              "Decision cannot be Accept."))
    code, err = _run2(root)
    assert code == 1
    assert ("unconditional DA-CRITICAL veto regression" in err
            or "adjudication wording missing" in err)


def test_m64_da_delivered_contract_weakened(tmp_path):
    """Weakening the DA's delivered contract modality (require → may use) must
    fail even though stronger rules survive in undelivered sections (round-7 P1)."""
    root = _mirror(tmp_path)
    _edit(root, DA_REL,
          lambda t: t.replace("CRITICAL/MAJOR require an adequate, applicable one",
                              "CRITICAL/MAJOR may use one", 1))
    code, err = _run2(root)
    assert code == 1
    assert "does not match the canonical verbatim block" in err


def test_m65_modifier_quota_caught(tmp_path):
    """'Identify 3 major issues' — count + modifier + noun — must fail (round-7 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[3],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nIdentify 3 major issues.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m66_scoring_points_do_not_false_fire(tmp_path):
    """'Award at most 5 points for clarity' is scoring language, not a finding
    quota — must PASS (round-7 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[0],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nAward at most 5 points for clarity.\n", 1))
    code, err = _run2(root)
    assert code == 0, f"scoring points false-fired:\n{err}"


def test_m67_limit_cap_quota_caught(tmp_path):
    """'Limit findings to five' / 'Cap weaknesses at 5' must fail (round-8 P2)."""
    for phrase in ("Limit findings to five.", "Cap weaknesses at 5."):
        root = _mirror(tmp_path / phrase[:4].strip().lower())
        _edit(root, SCORING_AGENTS[1],
              lambda t, ph=phrase: t.replace("### Weaknesses\n", f"### Weaknesses\n{ph}\n", 1))
        code, err = _run2(root)
        assert code == 1, f"{phrase!r} passed the lint"
        assert "finding-quota regression" in err


def test_m68_schema7_severity_field_deleted(tmp_path):
    """Deleting the Schema 7 RoadmapItem severity row breaks the machine
    handoff of transported metadata (round-8 P1)."""
    root = _mirror(tmp_path)
    def drop(t: str) -> str:
        return "\n".join(l for l in t.splitlines()
                         if "Transported Schema 6 finding severity" not in l) + "\n"
    _edit(root, SCHEMAS_REL, drop)
    code, err = _run2(root)
    assert code == 1
    assert "Schema 7 RoadmapItem transported-field row" in err


def test_m69_template_suggested_columns_dropped(tmp_path):
    """The decision template's Suggested table losing its transported columns
    must fail (round-8 P1: the template mirror, not only the synthesizer)."""
    root = _mirror(tmp_path)
    _edit(root, DECISION_TEMPLATE_REL,
          lambda t: t.replace(
              "| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source Reviewer | Priority | Section | Expected Improvement |",
              "| # | Revision Item | Sub-Claim(s) | Source Reviewer | Priority | Section | Expected Improvement |"))
    code, err = _run2(root)
    assert code == 1
    assert "lost its transported-metadata columns" in err


def test_m70_standards_qualitative_base_rate_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, STANDARDS_REL,
          lambda t: t.replace("never a frequency expectation",
                              "uncommon in practice, but judged on the criteria"))
    code, err = _run2(root)
    assert code == 1
    assert ("qualitative base-rate cue regression" in err
            or "frequency-free first-pass acceptance" in err)


def test_m71_schema7_anchor_row_deleted(tmp_path):
    """Deleting the Schema 7 evidence_anchor row must fail — round-9 P1: a
    severity-only witness left the other transported fields deletable."""
    root = _mirror(tmp_path)
    def drop(t: str) -> str:
        keep = []
        in_s7 = False
        for l in t.splitlines():
            if l.startswith("## Schema 7:"):
                in_s7 = True
            elif l.startswith("## Schema 8:"):
                in_s7 = False
            if in_s7 and l.startswith("| `evidence_anchor` | object |"):
                continue
            keep.append(l)
        return "\n".join(keep) + "\n"
    _edit(root, SCHEMAS_REL, drop)
    code, err = _run2(root)
    assert code == 1
    assert "Schema 7 RoadmapItem transported-field row" in err


def test_m72_xm_prompt_quota_added(tmp_path):
    """A quota added to the cross-model DA prompt while the canonical
    no-fixed-count sentence survives must fail (round-9 P2)."""
    root = _mirror(tmp_path)
    _edit(root, XM_REL,
          lambda t: t.replace("   - What the weakness is",
                              "   Report up to five findings.\n   - What the weakness is", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression in the cross-model DA prompt" in err


def test_m73_between_range_with_modifier_caught(tmp_path):
    """'Provide between three and five major weaknesses' must fail (round-9 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[0],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nProvide between three and five major weaknesses.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m74_da_minor_confidence_dropped(tmp_path):
    """The DA MINOR table losing its Confidence column must fail (round-9 P2:
    a MINOR issue that becomes a Suggested Revision transports confidence)."""
    root = _mirror(tmp_path)
    def strip(t: str) -> str:
        return t.replace("| # | Dimension | Issue Description | Evidence Anchor | Confidence |\n"
                         "|---|-----------|-------------------|-----------------|------------|",
                         "| # | Dimension | Issue Description | Evidence Anchor |\n"
                         "|---|-----------|-------------------|-----------------|", 1)
    _edit(root, DA_REL, strip)
    code, err = _run2(root)
    assert code == 1
    assert "MINOR table: missing column" in err


def test_m75_top_n_quota_caught(tmp_path):
    """'Report the top 3 weaknesses' — a fixed selection count — must fail
    (round-10 P2: the exact retired cross-model wording class, now caught on
    every scanned surface)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[2],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nReport the top 3 weaknesses.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m76_field_analyst_register_softening_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, FIELD_ANALYST_REL,
          lambda t: t.replace(
              '- Suggest reviewers adopt "developmental feedback" as the REGISTER — '
              "the recommendation itself stays evidence-based against the criteria "
              "(#574 B1: tone changes wording, never the verdict)",
              '- Suggest reviewers adopt "developmental feedback" as the main '
              'approach, rather than strict "accept/reject" judgment'))
    code, err = _run2(root)
    assert code == 1
    assert ("register-softens-verdict regression" in err
            or "developmental-register rule" in err)


def test_m77_schema7_semantics_rewritten(tmp_path):
    """Rewriting a Schema 7 field's transport semantics (keeping the row) must
    fail — row existence alone was fail-open (round-10 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCHEMAS_REL,
          lambda t: t.replace("Fallback provenance for `confidence` — the verbatim tag",
                              "A synthesizer-generated confidence estimate"))
    code, err = _run2(root)
    assert code == 1
    assert "Schema 7 RoadmapItem transported-field row" in err


def test_m78_selection_verb_quota_caught(tmp_path):
    """'Select three weaknesses' — a selection-verb direct count — must fail
    (round-11 P2)."""
    root = _mirror(tmp_path)
    _edit(root, SCORING_AGENTS[1],
          lambda t: t.replace("### Weaknesses\n",
                              "### Weaknesses\nSelect three weaknesses.\n", 1))
    code, err = _run2(root)
    assert code == 1
    assert "finding-quota regression" in err


def test_m29_calibration_bridge_removed(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, CALIBRATION_REL,
          lambda t: t.replace("measurement-reading prior for calibration", "prior")
                     .replace("no verdict is shaded stricter on this prior's account",
                              "verdicts may account for it"))
    code, err = _run2(root)
    assert code == 1
    assert "B1 bridge" in err


# --- P0-3 residue ---------------------------------------------------------------------

def test_m19_skill_overlap_prohibition_restored(tmp_path):
    root = _mirror(tmp_path)
    _edit(root, SKILL_REL,
          lambda t: t.replace("independent overlap in findings is legitimate corroboration",
                              "no duplicate criticisms"))
    code, err = _run2(root)
    assert code == 1
    assert ("overlap-corroboration standard" in err
            or "overlap-prohibition regression" in err)


# --- invocation error --------------------------------------------------------------

def test_m20_missing_file_exits_2(tmp_path):
    root = _mirror(tmp_path)
    (root / SCHEMAS_REL).unlink()
    assert _run(root) == 2


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
