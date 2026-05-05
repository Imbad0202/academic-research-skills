"""Static checks for ARS v3.6.7 Step 6 Phase 6.6 — orchestrator prompt §3.5
Audit Artifact Gate subsection.

Spec: docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md
Implementation plan: docs/design/2026-05-05-phase-6.6-scoping-note.md §5

Phase 6.6 ships a ~50-line decision-policy summary of the §5.6 audit gate
into pipeline_orchestrator_agent.md. The full Path A → Path B procedure
stays in spec §5.6 as the implementation contract; the prompt only carries
the policy summary plus P-PA-* / P-PB-* phase IDs as cross-references.

Verification gate (per spec §10 Phase 6.6, line 2387 of the spec): the
orchestrator prompt is no more than +60 lines vs pre-Step-6 baseline; the
24 phase IDs (7 P-PA-* + 17 P-PB-*) appear at least once each in the
prompt as cross-references to spec §5.6.

This test file enforces that gate as four assertions:
    1. The §3.5 Audit Artifact Gate subsection exists.
    2. All 24 P-PA-* / P-PB-* phase IDs are present.
    3. The three hard rules from spec §5.6 are present.
    4. Prompt size is within the +60-line budget over the baseline.

Pre-Step-6 baseline is recorded as `BASELINE_LINE_COUNT` below — captured
from main commit 02b87ae (the SKILL.md drift fix that landed alongside
the Phase 6.6 prep work, which did not touch the orchestrator prompt).

Tests use `unittest` and read pipeline_orchestrator_agent.md directly from
the working tree. No mutation; no temp dir. Each test is self-contained.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ORCHESTRATOR_PROMPT = (
    REPO_ROOT / "academic-pipeline" / "agents" / "pipeline_orchestrator_agent.md"
)

# Pre-Step-6 baseline line count of pipeline_orchestrator_agent.md, recorded
# from main commit 02b87ae (the last main commit before any Phase 6.6 prompt
# work). Confirmed by `wc -l` on that revision: 579 lines.
BASELINE_LINE_COUNT = 579

# Per Phase 6.6 verification gate (spec §10): +60 lines over pre-Step-6
# baseline. The ~50-line decision-policy summary plus 5–10 lines of headroom.
LINE_BUDGET_OVER_BASELINE = 60

# All 24 failure phase IDs from spec §5.6 inventory (7 P-PA-* + 17 P-PB-*).
# These must each appear at least once in the orchestrator prompt as
# cross-references to spec §5.6 (NOT inline procedural definitions —
# those stay in spec).
REQUIRED_PHASE_IDS = (
    # 7 Path A phases
    "P-PA-precond",
    "P-PA-schema",
    "P-PA-gate",
    "P-PA-verdict-schema",
    "P-PA-verdict-mirror",
    "P-PA-stale-late",
    "P-PA-supersede-preempt",
    # 17 Path B phases
    "P-PB-empty",
    "P-PB-supersede-missing",
    "P-PB-ambig",
    "P-PB-proposal-schema",
    "P-PB-audit-failed",
    "P-PB-gate",
    "P-PB-verdict-schema",
    "P-PB-verdict-mirror",
    "P-PB-stale-late",
    "P-PB-dup-early",
    "P-PB-dup-other",
    "P-PB-dup-late",
    "P-PB-snapshot",
    "P-PB-persisted-schema",
    "P-PB-passport-write",
    "P-PB-consume-fail",
    "P-PB-crash",
)


def _read_prompt() -> str:
    return ORCHESTRATOR_PROMPT.read_text(encoding="utf-8")


class Phase66SubsectionPresenceTest(unittest.TestCase):
    """Test 1 — §3.5 Audit Artifact Gate subsection exists."""

    def test_subsection_heading_present(self) -> None:
        text = _read_prompt()
        self.assertIn(
            "### 3.5 Audit Artifact Gate",
            text,
            "Phase 6.6 deliverable missing: §3.5 Audit Artifact Gate "
            "subsection heading not found in orchestrator prompt. Per spec "
            "§10 Phase 6.6, the subsection must exist between current §3 "
            "Checkpoint Management and §4 Transition Management.",
        )


class Phase66PhaseIdReferencesTest(unittest.TestCase):
    """Test 2 — All 24 P-PA-* / P-PB-* phase IDs are present.

    Per spec §10 Phase 6.6 verification gate: phase IDs appear "as
    cross-references to spec §5.6, not as inline procedural definitions"
    (the procedural definitions stay in §5.6). This test enforces presence
    only — whether each citation contextualises as a cross-reference is
    not statically verifiable from grep alone; the codex iterative review
    in implementation Step 4 catches drift away from cross-reference framing.
    """

    def test_all_24_phase_ids_present(self) -> None:
        text = _read_prompt()
        missing = [pid for pid in REQUIRED_PHASE_IDS if pid not in text]
        self.assertFalse(
            missing,
            f"Phase 6.6 deliverable missing {len(missing)} of "
            f"{len(REQUIRED_PHASE_IDS)} required phase IDs in orchestrator "
            f"prompt: {missing}. Per spec §10 Phase 6.6 verification gate, "
            f"the §5.6 inventory's phase IDs (P-PA-* / P-PB-*) appear at "
            f"least once each in the prompt as referenceable handles.",
        )


class Phase66HardRulesTest(unittest.TestCase):
    """Test 3 — Three hard rules from spec §5.6 are present.

    Spec §5.6 Hard rules block:
        - Audit gate cannot be skipped (no skip-audit option)
        - Audit gate runs BEFORE collaboration_depth_agent + integrity_verification_agent
        - PASS does NOT imply integrity check is skipped
    """

    def test_hard_rule_no_skip(self) -> None:
        text = _read_prompt()
        self.assertTrue(
            "cannot be skipped" in text or "no skip-audit" in text or
            "no \"skip audit\"" in text or 'no "skip audit"' in text,
            "Phase 6.6 hard rule missing: audit gate cannot be skipped. "
            "Spec §5.6 declares this as the first hard rule.",
        )

    def test_hard_rule_runs_before_observers(self) -> None:
        text = _read_prompt()
        self.assertIn(
            "BEFORE collaboration_depth_agent",
            text,
            "Phase 6.6 hard rule missing: audit gate runs BEFORE "
            "collaboration_depth_agent. Spec §5.6 declares this as the "
            "second hard rule (audit is first transition-time check).",
        )
        self.assertIn(
            "BEFORE integrity_verification_agent",
            text,
            "Phase 6.6 hard rule missing: audit gate runs BEFORE "
            "integrity_verification_agent. Spec §5.6 declares this as the "
            "second hard rule (audit is first transition-time check).",
        )

    def test_hard_rule_pass_does_not_skip_integrity(self) -> None:
        text = _read_prompt()
        # Either phrasing is acceptable; both convey the rule.
        self.assertTrue(
            "PASS does not imply integrity check is skipped" in text
            or "PASS does NOT imply integrity check is skipped" in text
            or "Stage 2.5 / 4.5 integrity gates remain mandatory" in text,
            "Phase 6.6 hard rule missing: PASS does not skip integrity "
            "check. Spec §5.6 declares this as the third hard rule "
            "(Stage 2.5 / 4.5 integrity gates remain mandatory).",
        )


class Phase66LineBudgetTest(unittest.TestCase):
    """Test 4 — Prompt size within +60 line budget over pre-Step-6 baseline.

    Per spec §10 Phase 6.6 verification gate: orchestrator prompt is no
    more than +60 lines vs pre-Step-6 baseline (R3 budget — the ~50-line
    decision-policy summary plus 5–10 lines of headroom).

    Baseline is BASELINE_LINE_COUNT (579 lines from main commit 02b87ae).
    """

    def test_prompt_size_within_budget(self) -> None:
        text = _read_prompt()
        line_count = len(text.splitlines())
        ceiling = BASELINE_LINE_COUNT + LINE_BUDGET_OVER_BASELINE
        self.assertLessEqual(
            line_count,
            ceiling,
            f"Phase 6.6 line budget exceeded: orchestrator prompt is "
            f"{line_count} lines, exceeds {ceiling} (baseline "
            f"{BASELINE_LINE_COUNT} + budget {LINE_BUDGET_OVER_BASELINE}). "
            f"Per spec §10 Phase 6.6 verification gate, the §3.5 Audit "
            f"Artifact Gate subsection must add no more than +60 lines "
            f"(the ~50-line decision-policy summary plus headroom).",
        )


if __name__ == "__main__":
    unittest.main()
