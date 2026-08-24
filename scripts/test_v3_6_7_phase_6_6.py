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

# v3.7.1 Step 3b additionally ships the `## Cite-Time Provenance Finalizer
# (v3.7.1)` subsection per spec § Step 3b (line 449). The subsection adds
# the §3.3 4-cell matrix + idempotency + revision-loop preservation +
# peer-file join semantics. Measured at first-write: 35 content lines
# (heading + matrix rows + bullets) + horizontal rule + paragraph breaks.
# Budget includes 5 lines of headroom for codex-round prose adjustments.
LINE_BUDGET_V3_7_1_STEP_3B = 40

# v3.7.3 additionally ships the `## Cite-Time Provenance Finalizer —
# v3.7.3 extension` subsection per spec
#   docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md
# §3.1+§3.2. The subsection adds the L3-1 precedence-zero NO-LOCATOR check
# + L3-2 contamination annotation matrix + updated resolution order +
# audit-trail columns. External motivation: Zhao et al. arXiv:2605.07723
# (2026-05). Measured at first-write: 44 lines (heading + two H3 subs +
# matrix rows + bullets + audit-trail paragraph). Budget includes ~15
# lines of headroom for codex-round prose adjustments since the v3.7.3
# section is larger than v3.7.1 Step 3b.
LINE_BUDGET_V3_7_3_EXTENSION = 60

# v3.8 additionally ships the `### 3.6 Claim-Faithfulness Audit Gate
# (v3.8)` subsection per spec
#   docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md §5
# The subsection adds the 8-row finalizer matrix + orchestrator dispatch
# wiring + mode flag + Stage-6 histogram + cross-references for the v3.8
# L3 claim-faithfulness audit. External motivation: Zhao et al.
# arXiv:2605.07723 (2026-05). Measured at first-write: 53 lines (heading
# + matrix + bullets + cross-refs). Budget includes ~7 lines headroom
# for codex-round prose adjustments; v3.8 matrix prose is more compact
# than v3.7.3 because the spec section already bears the full table
# explanation — orchestrator §3.6 only restates the bare table + mode
# flag + handoff bullets.
LINE_BUDGET_V3_8_AUDIT_GATE = 60

# v3.9.0 additionally ships the `## Cite-Time Provenance Finalizer —
# v3.9.0 extension (triangulation tiers)` subsection per spec
#   docs/design/2026-05-17-ars-v3.9.0-cross-index-triangulation-measurement-spec.md
# §3.3. The subsection adds the 4-tier advisory matrix (k=0/1/2/3 over
# present *_unmatched fields) + preprint composition shapes + gate
# semantics note + example markers. External motivation: Zhao et al.
# arXiv:2605.07723 §3 (cross-index triangulation). Measured at first-
# write: ~38 lines. Budget includes ~12 lines headroom for codex-round
# prose adjustments.
LINE_BUDGET_V3_9_0_EXTENSION = 50

# v3.10 additionally ships the `## Cite-Time Provenance Finalizer —
# v3.10 extension (terminal policy layer)` subsection per spec
#   docs/design/2026-05-31-ars-v3.10-policy-layer-rescope-spec.md §3 PR-B items 6-9.
# The subsection adds the policy_hash slug rules + the two marker grammar
# shapes (terminal / non-terminal) + strict & strict_articles_only promotion
# rules + manual-entry exemption + the terminal_blocked[] audit-trail note.
# It is the largest finalizer extension because it carries the full grammar
# definition. Measured at first-write: ~64 lines. Like the v3.7.x / v3.9.0 blocks,
# this v3.10 block has its own scope and MUST be subtracted from the v3.6.7
# Phase 6.6 +60 budget.
#
# v3.11 (#182 Delta 3 / INVARIANT C-V6) adds the `### Citation-existence terminal
# promotion under strict` subsection INSIDE this same H2 block (the second wired
# terminal policy alongside contamination_triangulation), plus the C-V6(f) manual-
# exemption sentence and the C-V6(g) multi-policy co-emit audit-trail paragraph.
# Measured after C-V6 landed: 84 lines. Budget raised 75 → 90 (rationale: the new
# policy is a binding spec deliverable carrying C-V6 (a)-(h) requirements, not codex-
# round prose; ~6 lines headroom retained for review adjustments).
LINE_BUDGET_V3_10_EXTENSION = 90

# #394 slice 4 ships the `## Submission-Package Terminal Gate` H2 block — a
# package-level Stage 5 post-formatter gate, deliberately compact because the
# evaluation mechanics live in scripts/verify_submission_package.py and the
# spec; the block carries the two boundary paragraphs + the six-step
# procedure whose load-bearing literals check_394_submission_policy.py
# invariant 2 pins. Measured at landing: 19 lines. Budget 25 (~6 lines
# headroom, the v3.10 convention).
LINE_BUDGET_394_GATE = 25

# #390 Slice B ships the `## Revision-Round Patch Sequencing (#390)` H2 block —
# the orchestrator side of diff/patch revision mode: the seven-step normative
# sequence, the no-rewrite window, the two-layer escalation gate + MANDATORY
# checkpoint, and the apply-failure path. Its own scope (the patch protocol,
# not the v3.6.7 audit gate), so like every vX finalizer/gate block it is
# SUBTRACTED from the v3.6.7 Phase 6.6 +60 budget and carries its own dedicated
# budget test below. The block embeds a fenced checkpoint template, so it is
# heading-anchored, not fence-anchored. Spec:
#   docs/design/2026-06-10-390-diff-patch-revision-mode-spec.md §3.3-§3.6.
# Measured at landing: 47 lines. Budget 55 (~8 lines headroom).
LINE_BUDGET_390_SEQUENCING = 55

# #670 adds the `## Revision Authority and Evidence-Bundle Extension` H2
# block. It carries the bundle's exact continuous chain plus the separate
# integrity-correction proposal -> exact author patch approval -> apply ->
# issuing-gate re-verification path. Keeping it separate preserves the #390
# sequencing budget instead of silently charging new authority semantics to
# that older block. Measured at landing: 42 lines. Budget 48 (~6 lines
# headroom).
LINE_BUDGET_670_AUTHORITY_EXTENSION = 48

# #576 Spec B PR-B2 ships the `## Stage 3' Re-Review Contract Dispatch
# (#576 Spec B)` H2 block — the orchestrator-side three-gate dispatch
# contract (manifest emission, gate sequencing, post-2B passes, mandatory
# checker invocation, deferral loop, abort surfacing, producer obligations,
# legacy boundary). Like the other extension subsections it has its own
# scope and budget, subtracted from the v3.6.7 Phase 6.6 measurement.
# Measured at first-write: 20 lines (heading + intro + 7 numbered steps +
# producer-obligations + legacy paragraphs). Spec:
#   docs/design/2026-07-27-576-spec-b-re-review-precommitment-contract-spec.md §16.
LINE_BUDGET_576_STAGE3P_DISPATCH = 30

# #656 ships the `##### Phase E Evidence-Row Rendering (#656)` checkpoint
# block. It carries the source-replay trust boundary, bounded pagination,
# explicit legacy compatibility, claim-summary consistency, and read-ledger /
# verdict noninterference rules, plus the checkpoint-template insertion point.
# This is a separate 2026-08 feature scope, so it is subtracted from the
# historical v3.6.7 +60 budget and gets its own bounded test. Measured at
# landing: 54 lines; budget 60 leaves 6 lines of headroom.
LINE_BUDGET_656_EVIDENCE_RENDERING = 60

# #660 ships the `## Tortured-Phrase Advisory Dispatch (#660)` H2 block.
# It carries the exact pre-format dispatch, explicit-time/no-network boundary,
# degraded-artifact handoff, advisory-only claim ceiling, and read-only cited
# carrier rules. This is an independent 2026-08 extension, so it is subtracted
# from the historical v3.6.7 budget and receives its own bounded test. Measured
# at landing: 55 lines; budget 60 leaves 5 lines of headroom.
LINE_BUDGET_660_ADVISORY_DISPATCH = 60

# #672 ships the `## Cross-Document Consistency Advisory Dispatch (#672)`
# H2 block. It binds the preregistration sidecar, exact accepted-draft join,
# independent #660/#672 failure semantics, and advisory-only Stage-5 routing.
# This independent 2026-08 extension is subtracted from the historical v3.6.7
# budget and receives its own bounded test. The measurement includes the
# nine-line Stage-1 sidecar-continuity paragraph next to the handoff table.
# Measured at first write: 60 lines; budget 66 leaves 6 lines of headroom.
LINE_BUDGET_672_ADVISORY_DISPATCH = 66

# #673 adds three bounded orchestrator surfaces: the stable run-identity
# paragraph, the action-time receipt hook, and the post-terminal seal/append
# sequence. They form one independent 2026-08 advisory side-channel scope, so
# they are subtracted from the historical v3.6.7 budget and receive a dedicated
# cap. Measured at landing: 51 lines; budget 57 leaves 6 lines of headroom.
LINE_BUDGET_673_ADJUDICATION_ACTIVITY = 57

# #684 adds one bounded H2 lifecycle that carries the exact manifest pointer,
# three consumer receipts, paper-blind panel dispatch, mid-entry coverage, and
# non-gate boundary. It is independent of the historical v3.6.7 audit gate,
# so it is subtracted and receives its own cap. Measured at first write: 39
# lines; budget 44 leaves five lines of review headroom.
LINE_BUDGET_684_REVIEW_CRITERIA_BINDING = 44

# #743 adds one bounded H4 checkpoint lifecycle plus the stable-sidecar
# expansion of the pre-existing passport-reset rule 9. Both are independent
# of the historical v3.6.7 audit gate, so only the rule-9 growth over its
# one-line baseline is charged here. Measured at landing: 54 lines; budget 60
# leaves six lines of review headroom.
LINE_BUDGET_743_INQUIRY_LEDGER = 60

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


_PROMPT_CACHE: str | None = None


def _read_prompt() -> str:
    """Read pipeline_orchestrator_agent.md once per test pass.

    Module-level cache: the orchestrator prompt is treated as immutable
    by every test in this file (no mutation, no fixture write). Step 8
    /simplify advisory P2-1 closure — 10 test methods each calling
    `read_text()` produced 10 disk reads of the same ~600-line file per
    `python -m unittest` invocation. The cache collapses to 1× IO with
    zero behavioral change.

    To bust the cache during a debugger session (e.g. when iterating on
    prompt text and re-running tests in the same process), set
    `_PROMPT_CACHE = None` manually.
    """
    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        _PROMPT_CACHE = ORCHESTRATOR_PROMPT.read_text(encoding="utf-8")
    return _PROMPT_CACHE


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


def _measure_finalizer_block_lines(text: str) -> int:
    """Return the number of lines in the v3.7.1 Step 3b finalizer
    subsection (`## Cite-Time Provenance Finalizer (v3.7.1)` H2 block).

    R1 P2-2 closure: keeps the v3.6.7 Phase 6.6 +60 budget test focused
    on its own contract by subtracting the finalizer block lines before
    applying the +60 ceiling. The Step 3b block has its own dedicated
    budget test (`V371Step3bLineBudgetTest`) below.
    """
    import re as _re
    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Cite-Time Provenance Finalizer \(v3\.7\.1\)[ \t]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,3}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_v3_8_audit_gate_block_lines(text: str) -> int:
    """Return the number of lines in the v3.8 §3.6 Claim-Faithfulness Audit
    Gate subsection (`### 3.6 Claim-Faithfulness Audit Gate (v3.8)` H3 block).

    v3.8 adds §3.6 as the orchestrator handoff slot between the v3.7.x
    finalizer pass and the formatter hard gate. Like the v3.7.1 / v3.7.3
    blocks, the v3.8 block has its own scope and MUST be subtracted from
    the v3.6.7 Phase 6.6 +60 budget. Spec:
      docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md §5

    Returns 0 if the v3.8 H3 heading is absent (e.g. when Step 8 has not
    yet shipped on a given branch).

    The block-end anchor matches the next H1, H2, OR H3 (`#{1,3} `) so the
    measurer reads exactly the §3.6 H3 block. v3.7.x extension measurers
    use `#{1,2}` because those blocks are H2 — H3 internals are part of
    their scope. §3.6 is itself an H3, so the next H3 closes it.
    """
    import re as _re
    anchor = _re.compile(
        r"(?m)^[ \t]*###[ \t]+3\.6[ \t]+Claim-Faithfulness Audit Gate[ \t]+\(v3\.8\)[^\n]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,3}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_v3_7_3_extension_block_lines(text: str) -> int:
    """Return the number of lines in the v3.7.3 finalizer extension
    subsection (`## Cite-Time Provenance Finalizer — v3.7.3 extension ...`
    H2 block).

    v3.7.3 adds an L3-1 + L3-2 extension to the finalizer (NO-LOCATOR
    precedence-zero check + contamination annotation). Like the v3.7.1
    Step 3b block, this v3.7.3 block has its own scope and MUST be
    subtracted from the v3.6.7 Phase 6.6 +60 budget. Spec:
      docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md §3.1+§3.2

    Returns 0 if the v3.7.3 H2 heading is absent.

    The v3.7.3 section uses H3 (`### ...`) subsections internally, so the
    block-end anchor matches the next H1 (`# `) or H2 (`## `) only — NOT
    H3 — distinct from `_measure_finalizer_block_lines()` which uses
    `#{1,3}` because the v3.7.1 Step 3b block has no internal H3.
    """
    import re as _re
    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Cite-Time Provenance Finalizer "
        r"[—-]+[ \t]*v3\.7\.3 extension[^\n]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,2}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_v3_9_0_extension_block_lines(text: str) -> int:
    """Return the number of lines in the v3.9.0 finalizer extension
    subsection (`## Cite-Time Provenance Finalizer — v3.9.0 extension ...`
    H2 block).

    Counts from the heading line up to (but not including) the next
    `## ` heading at the same level, or end of file. Mirrors
    `_measure_v3_7_3_extension_block_lines`.

    Returns 0 if the v3.9.0 H2 heading is absent.

    The v3.9.0 section uses H3 (`### ...`) subsections internally (like
    v3.7.3), so the block-end anchor matches the next H1 or H2 only —
    NOT H3 — to avoid prematurely closing on internal subheadings.
    """
    import re as _re
    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Cite-Time Provenance Finalizer "
        r"[—-]+[ \t]*v3\.9\.0 extension[^\n]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,2}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_v3_10_extension_block_lines(text: str) -> int:
    """Return the number of lines in the v3.10 finalizer extension
    subsection (`## Cite-Time Provenance Finalizer — v3.10 extension ...`
    H2 block).

    v3.10 adds the terminal-policy layer: policy_hash slug rules + the two
    marker grammar shapes + strict / strict_articles_only promotion + the
    terminal_blocked[] audit note. Like the v3.7.x / v3.9.0 blocks, it has
    its own scope and MUST be subtracted from the v3.6.7 Phase 6.6 +60 budget.
    Spec: docs/design/2026-05-31-ars-v3.10-policy-layer-rescope-spec.md §3 PR-B.

    Returns 0 if the v3.10 H2 heading is absent. The v3.10 section uses H3
    subsections internally, so the block-end anchor matches the next H1/H2
    only — NOT H3.
    """
    import re as _re
    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Cite-Time Provenance Finalizer "
        r"[—-]+[ \t]*v3\.10 extension[^\n]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,2}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_390_sequencing_block_lines(text: str) -> int:
    """Return the number of lines in the #390 Slice B revision-patch
    sequencing subsection (`## Revision-Round Patch Sequencing (#390)` H2
    block).

    Slice B adds the orchestrator side of diff/patch revision mode: the
    seven-step sequence, the no-rewrite window, the two-layer escalation
    gate + MANDATORY checkpoint, and the apply-failure path. Like the
    v3.7.x / v3.9.0 / v3.10 / #394 blocks, it has its own scope and MUST be
    subtracted from the v3.6.7 Phase 6.6 +60 budget. Spec:
      docs/design/2026-06-10-390-diff-patch-revision-mode-spec.md §3.3-§3.6.

    Returns 0 if the H2 heading is absent. The block embeds a fenced
    checkpoint template; the block-end anchor matches the next H1/H2 only
    (`#{1,2}`) so a fenced `## ...` line inside the template would only end
    it if it began at column 0 — the template's content does not, so the
    measure spans the whole block.
    """
    import re as _re
    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Revision-Round Patch Sequencing[^\n]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,2}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_670_authority_extension_lines(text: str) -> int:
    """Return the number of lines in the #670 authority/bundle H2 block.

    The exact bundle chain and integrity-correction author-approval path are
    a #670 extension, not part of the older #390 line budget. The next H1/H2
    closes the block; there are no internal H2 headings.
    """
    import re as _re
    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Revision Authority and Evidence-Bundle "
        r"Extension \(#670\)[ \t]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,2}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_394_gate_block_lines(text: str) -> int:
    """Return the number of lines in the #394 slice-4 submission-package
    gate subsection (`## Submission-Package Terminal Gate ...` H2 block).

    Slice 4 adds the Stage 5 post-formatter package-level gate: policy
    resolution, the CLI dispatch, token-not-exit-code gating, the bounded
    fix loop, the freshness guard, and the recompute-each-pass rule. Like
    the v3.7.x / v3.9.0 / v3.10 blocks, it has its own scope and MUST be
    subtracted from the v3.6.7 Phase 6.6 +60 budget. Spec:
      docs/design/2026-06-10-394-submission-package-verifier-spec.md §5.

    Returns 0 if the H2 heading is absent. The block uses one H3
    internally, so the block-end anchor matches the next H1/H2 only —
    NOT H3.
    """
    import re as _re
    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Submission-Package Terminal Gate[^\n]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,2}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_576_stage3p_dispatch_block_lines(text: str) -> int:
    """Return the number of lines in the #576 Spec B Stage 3' re-review
    contract-dispatch subsection (`## Stage 3' Re-Review Contract Dispatch
    (#576 Spec B)` H2 block).

    PR-B2 adds the orchestrator-side three-gate dispatch contract. Like
    the v3.7.x / v3.9.0 / v3.10 / #394 / #390 blocks, it has its own
    scope and MUST be subtracted from the v3.6.7 Phase 6.6 +60 budget.
    Spec: docs/design/2026-07-27-576-spec-b-re-review-precommitment-contract-spec.md §16.

    Returns 0 if the H2 heading is absent. The block has no internal
    headings; the block-end anchor matches the next H1/H2.
    """
    import re as _re
    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Stage 3' Re-Review Contract Dispatch[^\n]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,2}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_656_evidence_rendering_block_lines(text: str) -> int:
    """Return lines in the complete #656 orchestrator checkpoint scope."""
    import re as _re

    anchor = _re.compile(
        r"(?m)^[ \t]*#####[ \t]+Phase E Evidence-Row Rendering \(#656\)[ \t]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,5}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    policy_lines = len(text[m.start():end].splitlines())

    template_lines = text.splitlines()
    insertion_start = next(
        (
            index
            for index, line in enumerate(template_lines)
            if line.startswith("[Phase E evidence:")
        ),
        None,
    )
    if insertion_start is None:
        return 0
    insertion_end = next(
        (
            index
            for index in range(insertion_start, len(template_lines))
            if template_lines[index].endswith("evidence.]")
        ),
        None,
    )
    if insertion_end is None:
        return 0
    return policy_lines + insertion_end - insertion_start + 1


def _measure_660_advisory_dispatch_block_lines(text: str) -> int:
    """Return lines in the #660 tortured-phrase dispatch H2 block."""
    import re as _re

    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Tortured-Phrase Advisory Dispatch "
        r"\(#660\)[ \t]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,2}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    return len(text[m.start():end].splitlines())


def _measure_672_advisory_dispatch_block_lines(text: str) -> int:
    """Return lines in the #672 dispatch H2 plus sidecar handoff paragraph."""
    import re as _re

    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Cross-Document Consistency Advisory Dispatch "
        r"\(#672\)[ \t]*$"
    )
    m = anchor.search(text)
    if m is None:
        return 0
    next_h = _re.compile(r"(?m)^[ \t]*#{1,2}[ \t]+")
    head_eol = text.find("\n", m.end())
    search_start = (head_eol + 1) if head_eol >= 0 else len(text)
    nm = next_h.search(text, search_start)
    end = nm.start() if nm else len(text)
    dispatch_lines = len(text[m.start():end].splitlines())
    sidecar_marker = "**#672 sidecar continuity:**"
    sidecar_start = text.find(sidecar_marker)
    if sidecar_start < 0:
        return 0
    sidecar_end = text.find("\n\n", sidecar_start)
    if sidecar_end < 0:
        sidecar_end = len(text)
    sidecar_lines = len(text[sidecar_start:sidecar_end].splitlines())
    return dispatch_lines + sidecar_lines


def _measure_673_adjudication_activity_lines(text: str) -> int:
    """Return the three #673 orchestrator paragraphs/sections."""
    import re as _re

    run_marker = "**Run identity (#673):**"
    run_start = text.find(run_marker)
    if run_start < 0:
        return 0
    run_end = text.find("\n\n", run_start)
    if run_end < 0:
        return 0
    total = len(text[run_start:run_end].splitlines())

    for heading, maximum_level in (
        ("#### Adjudication-activity action-time hook (#673)", 4),
        ("### Post-terminal adjudication-activity sequence (#673)", 3),
    ):
        start = text.find(heading)
        if start < 0:
            return 0
        heading_end = text.find("\n", start)
        if heading_end < 0:
            return 0
        next_heading = _re.search(
            rf"(?m)^#{{1,{maximum_level}}}[ \t]+", text[heading_end + 1 :]
        )
        end = (
            heading_end + 1 + next_heading.start()
            if next_heading is not None
            else len(text)
        )
        total += len(text[start:end].splitlines())
    return total


def _measure_684_review_criteria_binding_lines(text: str) -> int:
    """Return lines in the #684 criteria-binding lifecycle H2 block."""
    import re as _re

    anchor = _re.compile(
        r"(?m)^[ \t]*##[ \t]+Review-target criteria binding lifecycle "
        r"\(#684\)[ \t]*$"
    )
    match = anchor.search(text)
    if match is None:
        return 0
    heading_end = text.find("\n", match.end())
    search_start = heading_end + 1 if heading_end >= 0 else len(text)
    next_heading = _re.search(r"(?m)^[ \t]*#{1,2}[ \t]+", text[search_start:])
    end = search_start + next_heading.start() if next_heading else len(text)
    return len(text[match.start():end].splitlines())


def _measure_743_inquiry_ledger_lines(text: str) -> int:
    """Return #743's H4 block plus reset-rule-9 growth over its baseline line."""
    import re as _re

    anchor = _re.compile(
        r"(?m)^[ \t]*####[ \t]+Inquiry Branch Ledger "
        r"\(#743, opt-in alpha\)[ \t]*$"
    )
    match = anchor.search(text)
    if match is None:
        return 0
    heading_end = text.find("\n", match.end())
    search_start = heading_end + 1 if heading_end >= 0 else len(text)
    next_heading = _re.search(r"(?m)^[ \t]*#{1,4}[ \t]+", text[search_start:])
    end = search_start + next_heading.start() if next_heading else len(text)
    inquiry_lines = len(text[match.start():end].splitlines())

    rule_marker = "9. Resume consumption MUST hold an exclusive advisory lock"
    rule_start = text.find(rule_marker)
    if rule_start < 0:
        return 0
    rule_end = text.find("\n\n", rule_start)
    if rule_end < 0:
        return 0
    current_rule_lines = len(text[rule_start:rule_end].splitlines())
    return inquiry_lines + max(0, current_rule_lines - 1)


class Advisory660LineBudgetTest(unittest.TestCase):
    """#660 tortured-phrase dispatch block stays independently bounded."""

    def test_660_advisory_dispatch_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_660_advisory_dispatch_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "#660 tortured-phrase advisory dispatch block is missing from "
            "pipeline_orchestrator_agent.md",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_660_ADVISORY_DISPATCH,
            f"#660 tortured-phrase advisory dispatch block is {block_lines} "
            f"lines, over its {LINE_BUDGET_660_ADVISORY_DISPATCH}-line budget",
        )


class Advisory672LineBudgetTest(unittest.TestCase):
    """#672 dispatch and sidecar continuity stay independently bounded."""

    def test_672_advisory_dispatch_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_672_advisory_dispatch_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "#672 cross-document advisory dispatch block is missing from "
            "pipeline_orchestrator_agent.md",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_672_ADVISORY_DISPATCH,
            f"#672 cross-document advisory dispatch block is {block_lines} "
            f"lines, over its {LINE_BUDGET_672_ADVISORY_DISPATCH}-line budget",
        )


class Advisory673LineBudgetTest(unittest.TestCase):
    """#673 action-time and post-terminal wiring stays independently bounded."""

    def test_673_adjudication_activity_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_673_adjudication_activity_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "#673 adjudication-activity wiring is missing from "
            "pipeline_orchestrator_agent.md",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_673_ADJUDICATION_ACTIVITY,
            f"#673 adjudication-activity wiring is {block_lines} lines, "
            f"over its {LINE_BUDGET_673_ADJUDICATION_ACTIVITY}-line budget",
        )


class ReviewCriteria684LineBudgetTest(unittest.TestCase):
    """#684 criteria-binding orchestration stays independently bounded."""

    def test_684_review_criteria_binding_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_684_review_criteria_binding_lines(text)
        self.assertGreater(block_lines, 0, "#684 criteria-binding block is missing")
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_684_REVIEW_CRITERIA_BINDING,
            f"#684 criteria-binding block is {block_lines} lines, over its "
            f"{LINE_BUDGET_684_REVIEW_CRITERIA_BINDING}-line budget",
        )


class InquiryLedger743LineBudgetTest(unittest.TestCase):
    """#743 inquiry-ledger orchestration stays independently bounded."""

    def test_743_inquiry_ledger_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_743_inquiry_ledger_lines(text)
        self.assertGreater(block_lines, 0, "#743 inquiry-ledger block is missing")
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_743_INQUIRY_LEDGER,
            f"#743 inquiry-ledger wiring is {block_lines} lines, over its "
            f"{LINE_BUDGET_743_INQUIRY_LEDGER}-line budget",
        )


class Dispatch576LineBudgetTest(unittest.TestCase):
    """#576 Spec B Stage 3' contract-dispatch block within
    `LINE_BUDGET_576_STAGE3P_DISPATCH` line budget.

    Dedicated budget test for the `## Stage 3' Re-Review Contract
    Dispatch (#576 Spec B)` subsection, decoupled from the v3.6.7
    Phase 6.6 budget and the other extension-subsection budgets. If a
    future #576 cascade legitimately requires more lines, raise
    `LINE_BUDGET_576_STAGE3P_DISPATCH` explicitly with rationale.
    """

    def test_576_dispatch_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_576_stage3p_dispatch_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "#576 Stage 3' contract-dispatch subsection missing from "
            "pipeline_orchestrator_agent.md (expected H2 heading "
            "'## Stage 3' Re-Review Contract Dispatch (#576 Spec B)')",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_576_STAGE3P_DISPATCH,
            f"#576 Stage 3' contract-dispatch block is {block_lines} lines, "
            f"over its {LINE_BUDGET_576_STAGE3P_DISPATCH}-line budget",
        )


class Evidence656LineBudgetTest(unittest.TestCase):
    """#656 checkpoint-rendering block stays within its own prompt budget."""

    def test_656_evidence_rendering_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_656_evidence_rendering_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "#656 Phase E evidence-row rendering block is missing from "
            "pipeline_orchestrator_agent.md",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_656_EVIDENCE_RENDERING,
            f"#656 Phase E evidence-row rendering block is {block_lines} lines, "
            f"over its {LINE_BUDGET_656_EVIDENCE_RENDERING}-line budget",
        )


class Phase66LineBudgetTest(unittest.TestCase):
    """Test 4 — Prompt size within v3.6.7 Phase 6.6 +60 line budget,
    measured EXCLUDING any v3.7.1+ subsections.

    Per spec §10 Phase 6.6 verification gate: orchestrator prompt is no
    more than +60 lines vs pre-Step-6 baseline (the ~50-line decision-
    policy summary plus 5–10 lines of headroom).

    R1 P2-2 closure: v3.7.1 Step 3b adds the `## Cite-Time Provenance
    Finalizer (v3.7.1)` subsection. To preserve the v3.6.7 regression
    signal, this test SUBTRACTS the v3.7.1 Step 3b block's line count
    from the total before applying the +60 ceiling. v3.7.1+ subsections
    have their own dedicated budget tests; the v3.6.7 contract is
    measured against its own scope only.

    Baseline is BASELINE_LINE_COUNT (579 lines from main commit 02b87ae).
    """

    def test_prompt_size_within_budget(self) -> None:
        text = _read_prompt()
        total_lines = len(text.splitlines())
        step_3b_lines = _measure_finalizer_block_lines(text)
        v3_7_3_lines = _measure_v3_7_3_extension_block_lines(text)
        v3_8_lines = _measure_v3_8_audit_gate_block_lines(text)
        v3_9_0_lines = _measure_v3_9_0_extension_block_lines(text)
        v3_10_lines = _measure_v3_10_extension_block_lines(text)
        gate_394_lines = _measure_394_gate_block_lines(text)
        seq_390_lines = _measure_390_sequencing_block_lines(text)
        authority_670_lines = _measure_670_authority_extension_lines(text)
        dispatch_576_lines = _measure_576_stage3p_dispatch_block_lines(text)
        evidence_656_lines = _measure_656_evidence_rendering_block_lines(text)
        advisory_660_lines = _measure_660_advisory_dispatch_block_lines(text)
        advisory_672_lines = _measure_672_advisory_dispatch_block_lines(text)
        advisory_673_lines = _measure_673_adjudication_activity_lines(text)
        criteria_684_lines = _measure_684_review_criteria_binding_lines(text)
        inquiry_743_lines = _measure_743_inquiry_ledger_lines(text)
        # v3.6.7-only line count: total minus v3.7.1 Step 3b, v3.7.3
        # finalizer extension, v3.8 §3.6 audit-gate, v3.9.0 triangulation
        # extension, v3.10 terminal-policy extension, the #394 slice-4
        # submission-package gate, the #390 Slice B revision-patch
        # sequencing, the #670 authority/bundle extension, the #576 Spec B
        # Stage 3' contract-dispatch, AND the #656 Phase E evidence-row
        # checkpoint-rendering, the #660 tortured-phrase advisory dispatch,
        # the #672 cross-document advisory dispatch, AND the #673
        # adjudication-activity wiring, the #684 review-criteria binding
        # lifecycle, AND the #743 inquiry-ledger/sidecar extension (each has
        # its own dedicated budget test).
        v367_line_count = (
            total_lines - step_3b_lines - v3_7_3_lines - v3_8_lines
            - v3_9_0_lines - v3_10_lines - gate_394_lines - seq_390_lines
            - authority_670_lines - dispatch_576_lines - evidence_656_lines
            - advisory_660_lines - advisory_672_lines - advisory_673_lines
            - criteria_684_lines - inquiry_743_lines
        )
        ceiling = BASELINE_LINE_COUNT + LINE_BUDGET_OVER_BASELINE
        self.assertLessEqual(
            v367_line_count,
            ceiling,
            f"Phase 6.6 line budget exceeded (v3.6.7-only scope): "
            f"orchestrator prompt is {total_lines} lines, of which "
            f"{step_3b_lines} are in the v3.7.1 Step 3b finalizer "
            f"subsection, {v3_7_3_lines} are in the v3.7.3 finalizer "
            f"extension subsection, {v3_8_lines} are in the v3.8 "
            f"§3.6 audit-gate subsection, {v3_9_0_lines} are in "
            f"the v3.9.0 triangulation extension subsection, "
            f"{v3_10_lines} are in the v3.10 terminal-policy extension "
            f"subsection, {gate_394_lines} are in the #394 submission-"
            f"package gate, {seq_390_lines} are in the #390 revision-patch "
            f"sequencing subsection, {dispatch_576_lines} are in the #576 "
            f"dispatch subsection, {evidence_656_lines} are in the #656 "
            f"evidence-rendering subsection, and {advisory_660_lines} are in "
            f"the #660 advisory-dispatch subsection, and {advisory_672_lines} "
            f"are in the #672 advisory-dispatch subsection, and "
            f"{advisory_673_lines} are in the #673 adjudication-activity "
            f"wiring, and {criteria_684_lines} are in the #684 criteria-"
            f"binding lifecycle, and {inquiry_743_lines} are in the #743 "
            f"inquiry-ledger/sidecar extension; "
            f"v3.6.7-attributed lines = "
            f"{v367_line_count} exceeds {ceiling} (baseline "
            f"{BASELINE_LINE_COUNT} + Phase 6.6 budget "
            f"{LINE_BUDGET_OVER_BASELINE}). Tighten the §3.5 Audit "
            f"Artifact Gate subsection.",
        )


class V371Step3bLineBudgetTest(unittest.TestCase):
    """Test 5 — v3.7.1 Step 3b finalizer block within +40 line budget.

    R1 P2-2 closure: dedicated budget test for the
    `## Cite-Time Provenance Finalizer (v3.7.1)` subsection. Measures
    ONLY the finalizer block's own lines, decoupled from the v3.6.7
    Phase 6.6 budget. Spec § Step 3b (line 449) does not specify a
    line cap; this test pins +40 lines as the contract for ARS prompt
    hygiene (the canonical subsection at first ship measured 35 lines;
    +40 leaves 5 lines of codex-round headroom).

    If a future Step 3b cascade legitimately requires more lines, raise
    `LINE_BUDGET_V3_7_1_STEP_3B` explicitly and document the rationale.
    """

    def test_step_3b_finalizer_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_finalizer_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "v3.7.1 Step 3b finalizer subsection missing from "
            "pipeline_orchestrator_agent.md (expected H2 heading "
            "'## Cite-Time Provenance Finalizer (v3.7.1)').",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_V3_7_1_STEP_3B,
            f"v3.7.1 Step 3b finalizer block exceeds "
            f"{LINE_BUDGET_V3_7_1_STEP_3B} lines (measured: "
            f"{block_lines}). Tighten the subsection or raise the "
            f"`LINE_BUDGET_V3_7_1_STEP_3B` constant with rationale.",
        )


class V373ExtensionLineBudgetTest(unittest.TestCase):
    """Test 6 — v3.7.3 finalizer extension block within
    `LINE_BUDGET_V3_7_3_EXTENSION` line budget.

    Dedicated budget test for the `## Cite-Time Provenance Finalizer —
    v3.7.3 extension` subsection. Measures ONLY this block's lines,
    decoupled from both the v3.6.7 Phase 6.6 budget and the v3.7.1
    Step 3b budget. External motivation: Zhao et al. arXiv:2605.07723
    (2026-05). Spec:
      docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md
      §3.1+§3.2

    If a future v3.7.3 cascade legitimately requires more lines, raise
    `LINE_BUDGET_V3_7_3_EXTENSION` explicitly and document the rationale.
    """

    def test_v3_7_3_extension_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_v3_7_3_extension_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "v3.7.3 finalizer extension subsection missing from "
            "pipeline_orchestrator_agent.md (expected H2 heading "
            "'## Cite-Time Provenance Finalizer — v3.7.3 extension ...').",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_V3_7_3_EXTENSION,
            f"v3.7.3 finalizer extension block exceeds "
            f"{LINE_BUDGET_V3_7_3_EXTENSION} lines (measured: "
            f"{block_lines}). Tighten the subsection or raise the "
            f"`LINE_BUDGET_V3_7_3_EXTENSION` constant with rationale.",
        )


class V38AuditGateLineBudgetTest(unittest.TestCase):
    """Test 7 — v3.8 §3.6 Claim-Faithfulness Audit Gate block within
    `LINE_BUDGET_V3_8_AUDIT_GATE` line budget.

    Dedicated budget test for the `### 3.6 Claim-Faithfulness Audit Gate
    (v3.8)` H3 subsection. Measures ONLY this block's lines, decoupled
    from the v3.6.7 Phase 6.6 budget AND the v3.7.x subsection budgets.
    External motivation: Zhao et al. arXiv:2605.07723 (2026-05) +
    Li et al. RubricEM arXiv:2605.10899. Spec:
      docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md §5

    If a future v3.8 cascade legitimately requires more lines, raise
    `LINE_BUDGET_V3_8_AUDIT_GATE` explicitly and document the rationale.
    """

    def test_v3_8_audit_gate_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_v3_8_audit_gate_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "v3.8 §3.6 audit-gate subsection missing from "
            "pipeline_orchestrator_agent.md (expected H3 heading "
            "'### 3.6 Claim-Faithfulness Audit Gate (v3.8)').",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_V3_8_AUDIT_GATE,
            f"v3.8 §3.6 audit-gate block exceeds "
            f"{LINE_BUDGET_V3_8_AUDIT_GATE} lines (measured: "
            f"{block_lines}). Tighten the subsection or raise the "
            f"`LINE_BUDGET_V3_8_AUDIT_GATE` constant with rationale.",
        )


class V390ExtensionLineBudgetTest(unittest.TestCase):
    """Test 8 — v3.9.0 finalizer extension block within
    `LINE_BUDGET_V3_9_0_EXTENSION` line budget.

    Dedicated budget test for the `## Cite-Time Provenance Finalizer —
    v3.9.0 extension (triangulation tiers)` subsection. Measures ONLY
    this block's lines, decoupled from the v3.6.7 Phase 6.6 budget AND
    the v3.7.x / v3.8 subsection budgets. External motivation: Zhao et
    al. arXiv:2605.07723 §3 (cross-index triangulation). Spec:
      docs/design/2026-05-17-ars-v3.9.0-cross-index-triangulation-measurement-spec.md
      §3.3

    If a future v3.9.0 cascade legitimately requires more lines, raise
    `LINE_BUDGET_V3_9_0_EXTENSION` explicitly and document the rationale.
    """

    def test_v3_9_0_extension_block_within_budget(self) -> None:
        """v3.9.0 finalizer extension block within +50 line budget.

        Dedicated budget test for the `## Cite-Time Provenance Finalizer —
        v3.9.0 extension (triangulation tiers)` subsection per spec
        docs/design/2026-05-17-ars-v3.9.0-cross-index-triangulation-measurement-spec.md §3.3.
        """
        text = _read_prompt()
        block_lines = _measure_v3_9_0_extension_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "v3.9.0 triangulation extension subsection missing from "
            "pipeline_orchestrator_agent.md (expected H2 heading "
            "'## Cite-Time Provenance Finalizer — v3.9.0 extension "
            "(triangulation tiers)').",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_V3_9_0_EXTENSION,
            f"v3.9.0 triangulation extension block exceeds "
            f"{LINE_BUDGET_V3_9_0_EXTENSION}-line budget (currently "
            f"{block_lines} lines). Tighten the subsection or raise "
            f"`LINE_BUDGET_V3_9_0_EXTENSION` with rationale.",
        )


class V310ExtensionLineBudgetTest(unittest.TestCase):
    """Test 9 — v3.10 finalizer extension block within
    `LINE_BUDGET_V3_10_EXTENSION` line budget.

    Dedicated budget test for the `## Cite-Time Provenance Finalizer —
    v3.10 extension (terminal policy layer)` subsection. Measures ONLY this
    block's lines, decoupled from the v3.6.7 Phase 6.6 budget AND the
    v3.7.x / v3.8 / v3.9.0 subsection budgets. Spec:
      docs/design/2026-05-31-ars-v3.10-policy-layer-rescope-spec.md §3 PR-B.

    If a future v3.10 cascade legitimately requires more lines, raise
    `LINE_BUDGET_V3_10_EXTENSION` explicitly and document the rationale.
    """

    def test_v3_10_extension_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_v3_10_extension_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "v3.10 terminal-policy extension subsection missing from "
            "pipeline_orchestrator_agent.md (expected H2 heading "
            "'## Cite-Time Provenance Finalizer — v3.10 extension "
            "(terminal policy layer)').",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_V3_10_EXTENSION,
            f"v3.10 terminal-policy extension block exceeds "
            f"{LINE_BUDGET_V3_10_EXTENSION}-line budget (currently "
            f"{block_lines} lines). Tighten the subsection or raise "
            f"`LINE_BUDGET_V3_10_EXTENSION` with rationale.",
        )


class Gate394LineBudgetTest(unittest.TestCase):
    """Test 10 — #394 slice-4 submission-package gate block within
    `LINE_BUDGET_394_GATE` line budget.

    Dedicated budget test for the `## Submission-Package Terminal Gate`
    subsection. Measures ONLY this block's lines, decoupled from the
    v3.6.7 Phase 6.6 budget AND the other extension-subsection budgets.
    Spec: docs/design/2026-06-10-394-submission-package-verifier-spec.md §5.

    If a future #394 cascade legitimately requires more lines, raise
    `LINE_BUDGET_394_GATE` explicitly and document the rationale.
    """

    def test_394_gate_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_394_gate_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "#394 submission-package gate subsection missing from "
            "pipeline_orchestrator_agent.md (expected H2 heading "
            "'## Submission-Package Terminal Gate ...').",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_394_GATE,
            f"#394 submission-package gate block exceeds "
            f"{LINE_BUDGET_394_GATE}-line budget (currently "
            f"{block_lines} lines). Tighten the subsection or raise "
            f"`LINE_BUDGET_394_GATE` with rationale.",
        )


class Sequencing390LineBudgetTest(unittest.TestCase):
    """Test 11 — #390 Slice B revision-patch sequencing block within
    `LINE_BUDGET_390_SEQUENCING` line budget.

    Dedicated budget test for the `## Revision-Round Patch Sequencing
    (#390)` subsection. Measures ONLY this block's lines, decoupled from
    the v3.6.7 Phase 6.6 budget AND the other extension-subsection budgets.
    Spec: docs/design/2026-06-10-390-diff-patch-revision-mode-spec.md §3.3-§3.6.

    If a future #390 cascade legitimately requires more lines, raise
    `LINE_BUDGET_390_SEQUENCING` explicitly and document the rationale.
    """

    def test_390_sequencing_block_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_390_sequencing_block_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "#390 revision-patch sequencing subsection missing from "
            "pipeline_orchestrator_agent.md (expected H2 heading "
            "'## Revision-Round Patch Sequencing (#390)').",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_390_SEQUENCING,
            f"#390 revision-patch sequencing block exceeds "
            f"{LINE_BUDGET_390_SEQUENCING}-line budget (currently "
            f"{block_lines} lines). Tighten the subsection or raise "
            f"`LINE_BUDGET_390_SEQUENCING` with rationale.",
        )


class Authority670LineBudgetTest(unittest.TestCase):
    """#670 authority/bundle extension has its own explicit line budget."""

    def test_670_authority_extension_within_budget(self) -> None:
        text = _read_prompt()
        block_lines = _measure_670_authority_extension_lines(text)
        self.assertGreater(
            block_lines,
            0,
            "#670 authority/bundle extension missing from "
            "pipeline_orchestrator_agent.md.",
        )
        self.assertLessEqual(
            block_lines,
            LINE_BUDGET_670_AUTHORITY_EXTENSION,
            f"#670 authority/bundle extension exceeds "
            f"{LINE_BUDGET_670_AUTHORITY_EXTENSION}-line budget (currently "
            f"{block_lines} lines). Tighten it or raise "
            "`LINE_BUDGET_670_AUTHORITY_EXTENSION` with rationale.",
        )


if __name__ == "__main__":
    unittest.main()
