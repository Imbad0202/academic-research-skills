#!/usr/bin/env python3
"""Defrift lock for the four #528 pipeline-boundary resolutions.

The 2026-07 Mode-A structural replay (#528) surfaced four inconsistencies /
under-specified boundaries across the academic-pipeline prompt surfaces.
PR #529 fixed the two genuine contradictions (items 1-2); the #528 closure PR
defined the two under-specified boundaries (items 3-4). None of the four had
a lint, so any future prompt edit could silently re-open them — the same
drift class the #491 lock closed for the Bucket A enforcement sentence.

Pinned invariants (one per replay item):

1. **Methodology Blueprint in the Stage 1→2 handoff** — all three handoff
   surfaces (SKILL.md Step 4 list, state-machine transition row, orchestrator
   handoff table) carry the Blueprint alongside RQ Brief / Bibliography /
   Synthesis.

2. **Stage 3' Minor does not trigger coaching** — the orchestrator's coaching
   trigger condition and Coaching Rules exclusion list both state it.

3. **Stage 5 boundary semantics** — the MANDATORY finalization boundary is the
   Stage 5 ENTRY gate (between Stage 4.5 PASS and the Stage 5 dispatch); the
   Stage 5 completion checkpoint is FULL — never SLIM. Authority section in
   the state machine + mirrored canonical fragments in SKILL.md and the
   orchestrator + the completion-checkpoint transition row.

4. **Stage 6 terminal semantics** — the state machine defines Stage 6, the
   decline path, the terminal checkpoint, and the acknowledgement vocabulary
   (finish / end / done / confirm + natural-language equivalent); SKILL.md,
   the orchestrator, and process_summary_protocol.md carry the vocabulary;
   the orchestrator wires the terminal state_tracker transition.

Falsifiability discipline (per feedback_lint_passes_but_prompt_silent.md):
the state-machine authority fragments are scoped to the § Stage 5 and Stage 6
Boundary Semantics H2 span via the shared `check_section_literals` — the same
fragment appearing elsewhere in the file does not count. The SKILL.md /
orchestrator mirror fragments are file-unique canonical sentences and are
deliberately pinned file-wide.

Exit codes: 0 on pass, 1 on any failure.
"""
from __future__ import annotations

import sys
from pathlib import Path

from _skill_lint import check_section_literals

REPO_ROOT = Path(__file__).resolve().parent.parent

SKILL = "academic-pipeline/SKILL.md"
ORCH = "academic-pipeline/agents/pipeline_orchestrator_agent.md"
SM = "academic-pipeline/references/pipeline_state_machine.md"
PROTO = "academic-pipeline/references/process_summary_protocol.md"

# --- Invariant 1: Methodology Blueprint on all three Stage 1→2 surfaces ---
INV1_FRAGMENTS = {
    SKILL: "Stage 1  --> 2: deep-research handoff (RQ Brief + Methodology Blueprint + Bibliography + Synthesis)",
    SM: "| checkpoint | Stage 2 | User confirms | handoff RQ Brief + Methodology Blueprint + Bibliography + Synthesis |",
    ORCH: "| Stage 1 -> 2 | RQ Brief, Methodology Blueprint, Annotated Bibliography, Synthesis Report |",
}

# --- Invariant 2: Stage 3' Minor never triggers coaching (both ORCH spots) ---
INV2_FRAGMENTS = [
    "A Stage 3' Minor decision does NOT trigger coaching",
    "a Stage 3' Minor decision also does not trigger coaching",
]

# --- Invariants 3+4: the state-machine authority section (one H2, two H3s) ---
AUTHORITY_HEADING = "## Stage 5 and Stage 6 Boundary Semantics"
TRANSITIONS_HEADING = "## Legal State Transitions"

# Canonical terminal-acknowledgement vocabulary. Two spellings by surface:
# backtick form in the markdown prose (SKILL / ORCH / SM), double-quote form
# inside the protocol doc's fenced workflow block. The protocol additionally
# pins the natural-language-equivalent clause so the vocabulary cannot be
# narrowed to exact-keyword-only there (codex P1, 2026-07-16).
VOCAB_CANON = "`finish` / `end` / `done` / `confirm`, or an unambiguous natural-language equivalent"
VOCAB_PROTO = '"finish" / "end" / "done" / "confirm"'
VOCAB_PROTO_NL_CLAUSE = "unambiguous natural-language equivalent that accepts the deliverables"

S5_AUTHORITY_LITERALS = {
    "entry-gate": "refers to exactly ONE checkpoint: the **Stage 5 entry gate**",
    "gate-format-decision": 'the finalization-format decision: citation style (APA 7.0 / Chicago / IEEE, ...) — the "Stage 5 finalization format" pending decision the passport-reset machinery records at this boundary',
    "latex-in-stage": 'the "Need LaTeX?" question (Step 3) and the content confirmation before the final PDF (Step 4) — are part of Stage 5 execution, not pipeline checkpoints',
    "completion-full-never-slim": "FULL checkpoint — never SLIM",
    "completion-not-mandatory": "but it is not on the MANDATORY list",
}
S6_AUTHORITY_LITERALS = {
    "decline-path": "marked `skipped` and the pipeline still terminates `completed`",
    "terminal-checkpoint": "terminal checkpoint",
    "acknowledgement-vocabulary": VOCAB_CANON,
    "change-requests-not-ack": "Change requests (the other language version, content corrections) keep Stage 6 `in_progress` — they are not acknowledgements",
    "no-transition-after-completed": "no stage transition is legal",
}

S5_ENTRY_GATE_TABLE_CELL = "Stage 5 entry gate (before finalization)"
S5_CANON_RULE5 = "the checkpoint between Stage 4.5 PASS and the Stage 5 dispatch"
S5_CANON_GATE_SCOPE = "makes the finalization-format decision (citation style); the in-stage LaTeX question and content confirmation stay inside Stage 5 execution"
S5_CANON_COMPLETION = "The Stage 5 completion checkpoint (Final Paper delivered, before Stage 6) is FULL — never SLIM"

# Non-acknowledgement classification of change requests, per mirror surface.
SKILL_CHANGE_REQUESTS_NOT_ACK = "keep Stage 6 `in_progress` and are not acknowledgements"
PROTO_CHANGE_REQUESTS_NOT_ACK = "Stage 6 in_progress — they are not acknowledgements"

# Transition rows are pinned as COMPLETE rows (all four cells), scoped to the
# ## Legal State Transitions span — a prefix pin would let a mutation flip the
# outcome cell (FULL→MANDATORY, completed→skipped) and stay green (codex P1).
S5_TRANSITION_ROWS = {
    "entry-gate-row": "| checkpoint | Stage 5 | User confirms (MANDATORY — the Stage 5 entry gate; see § Stage 5 boundary semantics) | Pass final accepted draft; record the finalization-format decision (citation style) |",
    "completion-checkpoint-row": "| Stage 5 | **checkpoint** | Stage 5 completed, Final Paper delivered | Wait for user confirmation (FULL — never SLIM; see § Stage 5 boundary semantics) |",
}
S6_TRANSITION_ROWS = {
    "stage6-dispatch-row": "| checkpoint | Stage 6 | User confirms | Dispatch Process Summary per `process_summary_protocol.md` |",
    "terminal-checkpoint-row": "| Stage 6 | **terminal checkpoint** | Process Record delivered | Wait for terminal acknowledgement (see § Stage 6 terminal semantics) |",
    "terminal-transition-row": "| terminal checkpoint | completed | User acknowledges (`finish` / `end` / `done` / `confirm`, or an unambiguous natural-language equivalent) | Mark Stage 6 `completed`; set pipeline global state `completed` |",
    "decline-row": "| checkpoint | completed | User declines Stage 6 | Mark Stage 6 `skipped` (non-mandatory stage); set pipeline global state `completed` |",
}
# The orchestrator's state_tracker wiring, pinned as complete action pairs —
# a bare update_pipeline_state("completed") pin would let the acknowledgement
# branch flip Stage 6 to `skipped` while staying green (codex round-2 P1).
ORCH_TERMINAL_WIRING = {
    "acknowledgement-wiring": '`update_stage(6, "completed", outputs)` + `update_pipeline_state("completed")`',
    "decline-wiring": '`update_stage(6, "skipped")` + `update_pipeline_state("completed")`',
}


def check(skill: str, orch: str, sm: str, proto: str) -> list[str]:
    """Pure invariant evaluation over the four surface contents."""
    errors: list[str] = []
    texts = {SKILL: skill, ORCH: orch, SM: sm, PROTO: proto}

    # Invariant 1
    for path, fragment in INV1_FRAGMENTS.items():
        if fragment not in texts[path]:
            errors.append(
                f"invariant 1 ({path}): Stage 1→2 handoff no longer carries "
                f"the Methodology Blueprint in the pinned form: {fragment!r} "
                f"(#529; keep all three surfaces in lockstep)"
            )

    # Invariant 2
    for fragment in INV2_FRAGMENTS:
        if fragment not in orch:
            errors.append(
                f"invariant 2 ({ORCH}): coaching-trigger exclusion missing: "
                f"{fragment!r} (#529; a Stage 3' Minor routes directly to "
                f"Stage 4.5 and must not trigger coaching)"
            )

    # Invariant 3 — authority section + transition rows (both H2-scoped)
    errors.extend(
        check_section_literals(3, sm, AUTHORITY_HEADING,
                               f"{SM} Stage-5/6 authority",
                               S5_AUTHORITY_LITERALS)
    )
    errors.extend(
        check_section_literals(3, sm, TRANSITIONS_HEADING,
                               f"{SM} legal-transitions",
                               S5_TRANSITION_ROWS)
    )
    # Invariant 3 — mirrors (file-unique canonical sentences, pinned file-wide)
    for path in (SKILL, ORCH):
        if S5_ENTRY_GATE_TABLE_CELL not in texts[path]:
            errors.append(
                f"invariant 3 ({path}): checkpoint-type table no longer "
                f"scopes MANDATORY to {S5_ENTRY_GATE_TABLE_CELL!r}"
            )
        if S5_CANON_RULE5 not in texts[path]:
            errors.append(
                f"invariant 3 ({path}): checkpoint rule 5 lost the entry-gate "
                f"definition {S5_CANON_RULE5!r}"
            )
        if S5_CANON_GATE_SCOPE not in texts[path]:
            errors.append(
                f"invariant 3 ({path}): checkpoint rule 5 lost the gate-scope "
                f"clause {S5_CANON_GATE_SCOPE!r} (citation style is the sole "
                f"gate format decision; LaTeX stays in-stage)"
            )
        if S5_CANON_COMPLETION not in texts[path]:
            errors.append(
                f"invariant 3 ({path}): checkpoint rule 5 lost the "
                f"completion-checkpoint sentence {S5_CANON_COMPLETION!r}"
            )

    # Invariant 4 — authority section + transition rows (both H2-scoped)
    errors.extend(
        check_section_literals(4, sm, AUTHORITY_HEADING,
                               f"{SM} Stage-5/6 authority",
                               S6_AUTHORITY_LITERALS)
    )
    errors.extend(
        check_section_literals(4, sm, TRANSITIONS_HEADING,
                               f"{SM} legal-transitions",
                               S6_TRANSITION_ROWS)
    )
    # Invariant 4 — vocabulary on the mirror surfaces
    for path in (SKILL, ORCH):
        if VOCAB_CANON not in texts[path]:
            errors.append(
                f"invariant 4 ({path}): canonical terminal-acknowledgement "
                f"vocabulary missing: {VOCAB_CANON!r}"
            )
    for fragment in (VOCAB_PROTO, VOCAB_PROTO_NL_CLAUSE):
        if fragment not in proto:
            errors.append(
                f"invariant 4 ({PROTO}): canonical terminal-acknowledgement "
                f"vocabulary missing: {fragment!r}"
            )
    # Invariant 4 — change requests are never acknowledgements (all surfaces)
    if SKILL_CHANGE_REQUESTS_NOT_ACK not in skill:
        errors.append(
            f"invariant 4 ({SKILL}): change-request non-acknowledgement rule "
            f"missing: {SKILL_CHANGE_REQUESTS_NOT_ACK!r}"
        )
    if PROTO_CHANGE_REQUESTS_NOT_ACK not in proto:
        errors.append(
            f"invariant 4 ({PROTO}): change-request non-acknowledgement rule "
            f"missing: {PROTO_CHANGE_REQUESTS_NOT_ACK!r}"
        )
    for name, fragment in ORCH_TERMINAL_WIRING.items():
        if fragment not in orch:
            errors.append(
                f"invariant 4 ({ORCH}): state_tracker {name} pair missing: "
                f"{fragment!r}"
            )

    return errors


def main() -> int:
    contents = {}
    for path in (SKILL, ORCH, SM, PROTO):
        full = REPO_ROOT / path
        if not full.is_file():
            print(f"FAILED: surface file missing: {path}", file=sys.stderr)
            return 1
        contents[path] = full.read_text(encoding="utf-8")
    errors = check(contents[SKILL], contents[ORCH], contents[SM], contents[PROTO])
    if errors:
        for e in errors:
            print(f"FAILED: {e}", file=sys.stderr)
        print(
            "\nUpdate procedure: these fragments pin the #528/#529 boundary "
            "resolutions. If the wording must change, change it on every "
            "listed surface AND in this lint's pinned constants in the same "
            "commit.",
            file=sys.stderr,
        )
        return 1
    print("PASSED: check_pipeline_boundary_semantics — 4 invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
