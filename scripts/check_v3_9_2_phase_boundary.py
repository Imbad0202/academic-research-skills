#!/usr/bin/env python3
"""Static lint for ARS v3.9.2 phase boundary coverage (#133 hot-fix).

Spec: docs/design/2026-05-18-ars-v3.9.2-phase-boundary-spec.md Phase 5
Classification: docs/design/2026-05-18-ars-v3.9.2-agent-phase-classification.md

Enforces three invariants:

1. **Bucket A coverage** — all 22 single-phase agents MUST carry a
   `## Phase Boundary (v3.9.2)` H2 block.

2. **Bucket B/C/D exclusion** — all 16 multi-phase / phase-orthogonal /
   cross-phase-meta agents MUST NOT carry the block. Adding a fence to
   these agents would either falsely block legitimate cross-phase work
   (Bucket B/C) or defeat orchestration (Bucket D).

3. **Block content shape** — each Bucket A block must contain the four
   load-bearing keywords/phrases that make the boundary detectable in
   prompt processing:
     - `Phase Boundary (v3.9.2)` (the H2 marker)
     - `MUST NOT` (the prohibition section)
     - `MAY READ` (the explicit upstream-read permission)
     - `Enforcement (v3.9.2)` (the trailing enforcement-paragraph marker)

   These are scoped to the Phase Boundary block itself (via H2 → next H2
   boundary), so the same keyword appearing elsewhere in the agent file
   does not count toward passing.

Falsifiability discipline (per feedback_lint_passes_but_prompt_silent.md):
keywords are scoped to the v3.9.2 block; bare keyword presence anywhere
in the agent file does NOT count. The block must include all four phrases
inside its own H2 span.

Exit codes: 0 on pass, 1 on any failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Bucket A — 22 single-phase agents that MUST have Phase Boundary block.
# Source: docs/design/2026-05-18-ars-v3.9.2-agent-phase-classification.md
BUCKET_A_AGENTS = [
    # deep-research/agents/ (9)
    "deep-research/agents/research_question_agent.md",
    "deep-research/agents/research_architect_agent.md",
    "deep-research/agents/bibliography_agent.md",
    "deep-research/agents/source_verification_agent.md",
    "deep-research/agents/synthesis_agent.md",
    "deep-research/agents/editor_in_chief_agent.md",
    "deep-research/agents/ethics_review_agent.md",
    "deep-research/agents/risk_of_bias_agent.md",
    "deep-research/agents/meta_analysis_agent.md",
    # academic-paper/agents/ (7)
    "academic-paper/agents/literature_strategist_agent.md",
    "academic-paper/agents/structure_architect_agent.md",
    "academic-paper/agents/draft_writer_agent.md",
    "academic-paper/agents/citation_compliance_agent.md",
    "academic-paper/agents/abstract_bilingual_agent.md",
    "academic-paper/agents/peer_reviewer_agent.md",
    "academic-paper/agents/formatter_agent.md",
    # academic-paper-reviewer/agents/ (6)
    "academic-paper-reviewer/agents/eic_agent.md",
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md",
    "academic-paper-reviewer/agents/domain_reviewer_agent.md",
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md",
    "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md",
    "academic-paper-reviewer/agents/editorial_synthesizer_agent.md",
]

# Buckets B/C/D — 16 agents that MUST NOT have the block.
# B (4): multi-phase; C (8): phase-orthogonal; D (4): cross-phase-meta.
BUCKET_BCD_AGENTS = [
    # Bucket B — multi-phase (4)
    "deep-research/agents/devils_advocate_agent.md",          # P1, 3, 5 + Socratic L2, 4
    "deep-research/agents/report_compiler_agent.md",          # P4, 6
    "academic-paper/agents/argument_builder_agent.md",        # P3 + Plan Step 3
    "academic-paper/agents/visualization_agent.md",           # P4 + P7
    # Bucket C — phase-orthogonal (8)
    "deep-research/agents/socratic_mentor_agent.md",          # Socratic Layer 1-5
    "academic-paper/agents/socratic_mentor_agent.md",         # Plan Step 0-3
    "deep-research/agents/monitoring_agent.md",               # post-pipeline
    "academic-paper/agents/revision_coach_agent.md",          # Revision-Coach standalone
    "academic-pipeline/agents/integrity_verification_agent.md",  # Stage 2.5 / 4.5 gates
    "academic-pipeline/agents/collaboration_depth_agent.md",  # FULL/SLIM advisory
    "academic-pipeline/agents/claim_ref_alignment_audit_agent.md",  # opt-in audit
    "shared/agents/compliance_agent.md",                      # cross-skill stage gates
    # Bucket D — cross-phase / meta (4)
    "academic-paper/agents/intake_agent.md",                  # Phase 0 cross-phase config
    "academic-pipeline/agents/pipeline_orchestrator_agent.md",  # orchestrator
    "academic-pipeline/agents/state_tracker_agent.md",        # meta state
    "academic-paper-reviewer/agents/field_analyst_agent.md",  # Phase 0 configures panel
]

BLOCK_MARKER = "## Phase Boundary (v3.9.2)"

# H2 marker that ends the Phase Boundary block scope.
# Used to scope keyword checks: keywords appearing elsewhere in the file
# (e.g., in v3.6.7 PATTERN PROTECTION further down) do NOT count.
H2_RE = re.compile(r"^## ", re.MULTILINE)

# Required keywords/phrases inside each Bucket A block.
REQUIRED_PHRASES = [
    "Phase Boundary (v3.9.2)",
    "MUST NOT",
    "MAY READ",
    "Enforcement (v3.9.2)",
]


def extract_block(text: str) -> str | None:
    """Extract the Phase Boundary (v3.9.2) block from H2 start to next H2."""
    start = text.find(BLOCK_MARKER)
    if start == -1:
        return None
    # Find next H2 after the block marker
    after_block_start = start + len(BLOCK_MARKER)
    next_h2 = H2_RE.search(text, after_block_start)
    end = next_h2.start() if next_h2 else len(text)
    return text[start:end]


def check_bucket_a(path: Path) -> list[str]:
    """Bucket A: must have block AND all required phrases inside block."""
    errors: list[str] = []
    if not path.is_file():
        errors.append(f"{path.relative_to(REPO_ROOT)}: file not found")
        return errors

    text = path.read_text(encoding="utf-8")
    block = extract_block(text)
    if block is None:
        errors.append(
            f"{path.relative_to(REPO_ROOT)}: missing '## Phase Boundary (v3.9.2)' "
            f"block (Bucket A agents MUST carry this block per "
            f"docs/design/2026-05-18-ars-v3.9.2-agent-phase-classification.md)"
        )
        return errors

    for phrase in REQUIRED_PHRASES:
        if phrase not in block:
            errors.append(
                f"{path.relative_to(REPO_ROOT)}: Phase Boundary block missing "
                f"required phrase: {phrase!r} (falsifiability discipline: phrase "
                f"must appear inside the H2 block, not elsewhere in the file)"
            )
    return errors


def check_bucket_bcd(path: Path) -> list[str]:
    """Bucket B/C/D: must NOT have the block (adding fence breaks multi-phase
    or cross-phase legitimate behavior)."""
    errors: list[str] = []
    if not path.is_file():
        errors.append(f"{path.relative_to(REPO_ROOT)}: file not found")
        return errors

    text = path.read_text(encoding="utf-8")
    if BLOCK_MARKER in text:
        errors.append(
            f"{path.relative_to(REPO_ROOT)}: unexpected '## Phase Boundary "
            f"(v3.9.2)' block on Bucket B/C/D agent. These agents are multi-phase "
            f"(B), phase-orthogonal (C), or cross-phase meta (D) by design — "
            f"adding a single-phase fence would either falsely block legitimate "
            f"cross-phase work or defeat orchestration. See "
            f"docs/design/2026-05-18-ars-v3.9.2-agent-phase-classification.md."
        )
    return errors


def main() -> int:
    errors: list[str] = []

    for rel_path in BUCKET_A_AGENTS:
        errors.extend(check_bucket_a(REPO_ROOT / rel_path))

    for rel_path in BUCKET_BCD_AGENTS:
        errors.extend(check_bucket_bcd(REPO_ROOT / rel_path))

    # Coverage sanity
    if len(BUCKET_A_AGENTS) != 22:
        errors.append(
            f"BUCKET_A_AGENTS has {len(BUCKET_A_AGENTS)} entries but "
            f"classification doc requires 22"
        )
    if len(BUCKET_BCD_AGENTS) != 16:
        errors.append(
            f"BUCKET_BCD_AGENTS has {len(BUCKET_BCD_AGENTS)} entries but "
            f"classification doc requires 16"
        )

    if errors:
        print("v3.9.2 Phase Boundary lint FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"v3.9.2 Phase Boundary lint PASSED: "
          f"{len(BUCKET_A_AGENTS)} Bucket A agents have block, "
          f"{len(BUCKET_BCD_AGENTS)} Bucket B/C/D agents excluded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
