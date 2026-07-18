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

import hashlib

from _skill_lint import check_section_literals

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Whole-file content locks (sha256) for ALL FIVE #528 pipeline surfaces.
#
# Twelve codex xhigh review rounds demonstrated that sentence-level pins on
# pipeline prompt surfaces cannot converge: every round found another single
# green mutation of an operative sentence, label, predicate, or enum value.
# So every surface this lint reads carries the bibliography_agent-style
# whole-file hash lock: ANY byte change fails CI until this constant is
# updated in the same commit — which is the review surface working as
# designed (the same F2-lock convention the repo already applies to
# bibliography_agent). The sentence pins above/below stay for targeted
# error messages; the hash is the catch-all that terminates the
# single-edit-mutation class by construction.
#
# Update procedure: edit the doc, run
#   python3 -c "import hashlib,pathlib;p='<path>';print(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest())"
# and update the constant here IN THE SAME COMMIT, with the semantic change
# reviewed against the #528 resolutions.
# ---------------------------------------------------------------------------
CONTENT_LOCKS = {
    "academic-pipeline/SKILL.md": "085245226e00a9ed716fc7d0552f3df2e2cafa6662e259c6e95a4c3ad7639ec2",
    "academic-pipeline/agents/pipeline_orchestrator_agent.md": "a75b5d1e896a3e51b238d1235da68a7d490fee573e2576b39f52639fb6232486",
    "academic-pipeline/agents/state_tracker_agent.md": "b648eac4d4b35c217150539502c20fccc2f3fd026dda8efbb6178b199a288256",
    "academic-pipeline/references/pipeline_state_machine.md": "d507f3694cd4d282b9b3247d0d1855330c836c23ab6e5d41f280c6d455b4ed7f",
    "academic-pipeline/references/process_summary_protocol.md": "5c7053230d73b39d0a5d9d6f5e9f339c12570ae6d3aa2eae2eaf74f51d571e94",
}

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

# --- Invariant 2: Stage 3' Minor never triggers coaching (both ORCH spots),
# and the Minor -> Stage 4.5 routing declarations themselves (codex round-5
# P1: a mutation rerouting Minor left the coaching pins intact and green) ---
INV2_FRAGMENTS = [
    "A Stage 3' Minor decision does NOT trigger coaching",
    "a Stage 3' Minor decision also does not trigger coaching",
]
INV2_SKILL_ROUTING = "6. **Stage 3' RE-REVIEW** -> Accept|Minor -> Stage 4.5 / Major -> Stage 4'"
INV2_SM_ROUTING_ROW = "| checkpoint | Stage 4.5 | Decision = Accept/Minor, user confirms | Pass final draft to final verification |"
# Affirmative Major-only coaching predicates (codex round-6 P1: the negative
# exclusions alone let the operative trigger widen back to Minor/Major).
INV2_ORCH_AFFIRMATIVE = {
    "coaching-trigger-major-only": "after Stage 3' completion with Decision = Major Revision (routes to Stage 4')",
    "coaching-handoff-if-major": "| Stage 3' -> **coaching** -> 4' | New Revision Roadmap (if Major) |",
}

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
    "no-auto-advance": "- explicit confirmation to proceed to finalization (no auto-advance);",
    "gate-format-decision": 'the finalization-format decision: citation style (APA 7.0 / Chicago / IEEE, ...) — the "Stage 5 finalization format" pending decision the passport-reset machinery records at this boundary',
    "latex-in-stage": 'the "Need LaTeX?" question (Step 3) and the content confirmation before the final PDF (Step 4) — are part of Stage 5 execution, not pipeline checkpoints',
    "completion-full-never-slim": "FULL checkpoint — never SLIM",
    "completion-not-mandatory": "but it is not on the MANDATORY list",
}
S6_AUTHORITY_LITERALS = {
    "decline-path": "marked `skipped` and the pipeline still terminates `completed`",
    "stage6-non-mandatory": "Stage 6 is a non-mandatory stage (it is absent from the orchestrator's non-skippable list). At the Stage 5 completion checkpoint the user may decline it",
    "terminal-checkpoint": "When Stage 6 runs, its completion is the pipeline's **terminal checkpoint**:",
    "acknowledgement-vocabulary": VOCAB_CANON,
    "change-requests-not-ack": "Change requests (the other language version, content corrections) keep Stage 6 `in_progress` — they are not acknowledgements",
    "ack-outcome": "On acknowledgement: state_tracker marks Stage 6 `completed` and sets the pipeline global state to `completed`",
    "post-delivery-prompt": "After delivering the Process Record (MD + PDF per the user's language choice), the orchestrator prompts for a terminal acknowledgement",
    "no-transition-after-completed": "no stage transition is legal",
}

# Pinned as the complete row / the type-bearing clause so the MANDATORY
# classification itself cannot flip to FULL while staying green (codex
# round-4 P1: the previous pins started after the type keyword).
S5_ENTRY_GATE_TABLE_CELL = "| MANDATORY | Integrity FAIL; Review decision; Stage 5 entry gate (before finalization) | Cannot be skipped; requires explicit user input |"
S5_CANON_RULE5 = "always MANDATORY — this is the checkpoint between Stage 4.5 PASS and the Stage 5 dispatch"
S5_CANON_GATE_SCOPE = "makes the finalization-format decision (citation style); the in-stage LaTeX question and content confirmation stay inside Stage 5 execution"
S5_CANON_COMPLETION = "The Stage 5 completion checkpoint (Final Paper delivered, before Stage 6) is FULL — never SLIM"

# Non-acknowledgement classification of change requests, per mirror surface.
SKILL_CHANGE_REQUESTS_NOT_ACK = "keep Stage 6 `in_progress` and are not acknowledgements"
PROTO_CHANGE_REQUESTS_NOT_ACK = "Stage 6 in_progress — they are not acknowledgements"

# The FULL row must NOT reclaim "before finalization" — that boundary is the
# MANDATORY Stage 5 entry gate; FULL owns the Stage 5 COMPLETION checkpoint
# (codex round-3 P1: both types claimed "before finalization").
FULL_ROW = "| FULL | First checkpoint; after integrity boundaries; Stage 5 completion (final-deliverable acceptance) | Full deliverables list + decision dashboard + all options |"

# Stage 5 execution consumes the gate decision instead of re-asking (SKILL
# execution contract Step 1; codex round-3 P1).
SKILL_STEP1_CONSUME = "Consume the citation-style decision recorded at the Stage 5 entry gate; ask which academic formatting style (APA 7.0 / Chicago / IEEE, etc.) only when no gate decision exists (direct format-convert / mid-entry invocation)"
# The overview summary's terminal ordering (codex round-12 P1).
SKILL_OVERVIEW_ORDERING = "delivered before the terminal acknowledgement that completes the pipeline"
# The reset-boundary iron rule scopes MANDATORY to the entry gate (codex
# round-12 P1: the round-11 prose fix had no pin).
ORCH_RESET_IRON_RULE = "MANDATORY checkpoints (Stage 2.5 / 4.5, review decisions, the Stage 5 entry gate) remain MANDATORY even when reset co-occurs"

# Stage 6 decline semantics per mirror surface (codex round-3 P1: only the
# state machine pinned the decline path).
SKILL_STAGE6_HEADING = "## Stage 6: Process Summary Protocol"
SKILL_STAGE6_LITERALS = {
    "acknowledgement-vocabulary": "`finish` / `end` / `done` / `confirm`, or an unambiguous natural-language equivalent",
    "decline-path": "Stage 6 is non-mandatory — the user may decline it at the Stage 5 completion checkpoint (Stage 6 marked `skipped`; the pipeline still terminates `completed`)",
    "ack-outcome": "On acknowledgement, Stage 6 is marked `completed` and the pipeline global state is set to `completed`",
    "change-requests-not-ack": SKILL_CHANGE_REQUESTS_NOT_ACK,
}
PROTO_ACK_OUTCOME = "On acknowledgement: state_tracker marks Stage 6 completed and sets the pipeline global state to completed"
SKILL_RULE9_PIN = "completion checkpoint (FULL) -> Stage 6 (user may decline Stage 6: marked `skipped`, pipeline goes directly to `completed`)"
SKILL_RULE10_PIN = "terminal acknowledgement (`finish` / `end` / `done` / `confirm`, or an unambiguous natural-language equivalent) -> pipeline global state `completed`"
ORCH_DECLINE_HANDOFF_PIN = "User may decline Stage 6 there: mark it `skipped`, set pipeline state `completed`"
PROTO_DECLINE_PIN = "Stage 6 is non-mandatory — the user may decline it at that checkpoint; it is then marked `skipped` and the pipeline still terminates `completed`"
# Type-bearing completion-checkpoint triggers on the mirrors (codex round-6
# P1: a (FULL)->(MANDATORY) flip on either mirror stayed green).
ORCH_STAGE56_TRIGGER_PIN = "Dispatched only after the user confirms the Stage 5 completion checkpoint (FULL)"
ORCH_STAGE56_HANDOFF_ROW = "| Stage 5 -> 6 | Final deliverables list + pipeline state history (state_tracker JSON, agent logs) | — (Process Record; no numbered schema) | Dispatched only after the user confirms the Stage 5 completion checkpoint (FULL). User may decline Stage 6 there: mark it `skipped`, set pipeline state `completed`. Protocol: `../references/process_summary_protocol.md`; terminal semantics: `../references/pipeline_state_machine.md` § Stage 6 terminal semantics |"
PROTO_TRIGGER_PIN = "After the user confirms the Stage 5 completion checkpoint (FULL)"
# Delivery-before-acknowledgement sequencing (codex round-6 P1: on->before /
# After->Before mutations stayed green).
PROTO_SEQUENCING_PIN = "After delivering the process record, prompt the user to close the pipeline"
# Protocol step-5 header + terminal-outcome sentence (codex round-7 P1: the
# step could be retyped non-terminal / gain a Stage 7 continuation).
PROTO_STEP5_HEADER = "5. Terminal acknowledgement (pipeline terminal checkpoint):"
PROTO_NO_NEXT_STAGE = "There is no next stage."
# SKILL Step 4 handoff line (codex round-7 P1: the executing transition list
# could reverse the decline option while the Stage 6 section stayed pinned).
SKILL_STEP4_HANDOFF = "- Stage 5  --> 6: Pass final deliverables list + pipeline state history to Process Summary (user may decline Stage 6 at the Stage 5 completion checkpoint)"

# The #528/#529 diagram edges (codex round-7 P1: the ASCII diagram is an
# operative surface too — a /Minor -> /Reject or relabeled terminal edge
# would contradict the transitions table while staying green). Scoped to the
# ## State Transition Diagram span.
DIAGRAM_HEADING = "## State Transition Diagram (ASCII)"
DIAGRAM_EDGES = {
    "stage3p-accept-minor-branch": "|     Accept      Major               |\n              |     /Minor        |",
    "terminal-ack-edge": "[terminal acknowledgement]",
    "decline-edge": "[decline Stage 6]",
}

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
    "acknowledgement-sequencing": "Pipeline terminal transition: on the Stage 6 terminal acknowledgement (",
    "acknowledgement-wiring": '`update_stage("6", "completed", outputs)` + `update_pipeline_state("completed")`',
    "decline-wiring": 'if the user declined Stage 6 at the Stage 5 completion checkpoint — `update_stage("6", "skipped", {reason: "user declined Stage 6"})` + `update_pipeline_state("completed")`',
}

# The state_tracker contract must accept Stage 6 (codex round-3 P1: the
# orchestrator wiring called update_stage(6, ...) against a "1".."5" enum).
TRACKER = "academic-pipeline/agents/state_tracker_agent.md"
TRACKER_STAGE_ID_ENUM = '"1", "2", "2.5", "3", "4", "3p", "4p", "4.5", "5", "6"'
# The complete Stage 6 SSOT block — pinning only the key would let a
# load-bearing field (approval_gate) flip while staying green (codex
# round-9 P1).
TRACKER_STAGE6_ENTRY = '''"6": {
      "name": "PROCESS SUMMARY",
      "skill": "academic-pipeline",
      "status": "pending",
      "mode": null,
      "outputs": [],
      "started_at": null,
      "completed_at": null,
      "checkpoint_confirmed": false,
      "checkpoint_type": null,
      "schema_validated": false,
      "assigned_to": null,
      "approval_gate": true,
      "team_notes": null
    }'''
# check_prerequisites drives the automatic material-gap warnings — its Stage 2
# row must carry the Methodology Blueprint like every other Stage 1→2 surface
# (codex round-8 P1), and Stage 6 must be a known target stage.
TRACKER_PREREQ_STAGE2_ROW = "| Stage 2 | None (but Stage 1 output recommended) | RQ Brief, Methodology Blueprint, Bibliography, Synthesis |"
# The tracker's accepted-value declarations — the terminal wiring calls are
# pinned, but a renamed enum value would make the named consumer reject them
# (codex round-10 P1).
TRACKER_STATUS_ENUM_ROW = '| status | "pending", "in_progress", "completed", "skipped", "blocked" |'
TRACKER_GLOBAL_COMPLETED = "- `completed`"
TRACKER_PREREQ_STAGE6_ROW = "| Stage 6 | None (Final Paper already delivered at Stage 5) |"
# The skip-command validator only honors explicitly-skippable stages — the
# decline path requires Stage 6 on the skippable list (codex round-8 P1).
ORCH_SKIPPABLE_PIN = "- Skippable: Stage 1 (deep-research, if user provides own bibliography), Stage 3' (re-review, if only minor revisions), Stage 4' (re-revise, if accepted), Stage 6 (process summary — declined at the Stage 5 completion checkpoint; marked `skipped`, pipeline still terminates `completed`)"
# Both sides of the skip classification are pinned as complete lines — adding
# Stage 6 to the non-skippable side would otherwise stay green while
# contradicting the skippable declaration (codex round-9 P1).
ORCH_NON_SKIPPABLE_LINE = "- Non-Skippable: Stage 2 (writing), Stage 2.5 (pre-review integrity), Stage 3 (initial review), Stage 4.5 (final integrity), Stage 5 (finalize)"
# The SLIM engagement downgrade must not swallow the FULL-pinned Stage 5
# completion checkpoint (codex round-9 P1).
ORCH_ENGAGEMENT_FULL_EXCEPTION = "the Stage 5 completion checkpoint is FULL — never SLIM, regardless of the continue count"
TRACKER_WIRING = {
    "acknowledgement-outcome": 'on the terminal acknowledgement, `update_stage("6", "completed", outputs)` then `update_pipeline_state("completed")`',
    "decline-outcome": 'if the user declines Stage 6 at the Stage 5 completion checkpoint, `update_stage("6", "skipped", {reason: "user declined Stage 6"})` then `update_pipeline_state("completed")`',
}


def _line_pinned(text: str, pinned: str) -> bool:
    """True when `pinned` matches a COMPLETE line of `text` (whitespace-
    stripped equality). Substring pins on list lines are append-exploitable:
    ', Stage 6' after 'Stage 5 (finalize)' keeps the pin as a prefix and
    stays green (codex round-9 P1 witness)."""
    return any(line.strip() == pinned for line in text.splitlines())


def check(skill: str, orch: str, sm: str, proto: str, tracker: str = "") -> list[str]:
    """Pure invariant evaluation over the five surface contents."""
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
    if not _line_pinned(skill, INV2_SKILL_ROUTING):
        errors.append(
            f"invariant 2 ({SKILL}): the Stage 3' routing declaration "
            f"drifted from the pinned form: {INV2_SKILL_ROUTING!r}"
        )
    for name, fragment in INV2_ORCH_AFFIRMATIVE.items():
        if fragment not in orch:
            errors.append(
                f"invariant 2 ({ORCH}): affirmative {name} predicate "
                f"drifted from the pinned form: {fragment!r}"
            )
    errors.extend(
        check_section_literals(2, sm, TRANSITIONS_HEADING,
                               f"{SM} legal-transitions",
                               {"stage3p-minor-routing-row": INV2_SM_ROUTING_ROW})
    )
    errors.extend(
        check_section_literals(2, sm, DIAGRAM_HEADING,
                               f"{SM} transition-diagram",
                               DIAGRAM_EDGES)
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
        if FULL_ROW not in texts[path]:
            errors.append(
                f"invariant 3 ({path}): the FULL checkpoint-type row drifted "
                f"from the pinned form (it must claim the Stage 5 COMPLETION "
                f"checkpoint, never 'before finalization' — that boundary is "
                f"MANDATORY): {FULL_ROW!r}"
            )
    if SKILL_STEP1_CONSUME not in skill:
        errors.append(
            f"invariant 3 ({SKILL}): Stage 5 execution contract Step 1 no "
            f"longer consumes the entry-gate citation-style decision (with "
            f"the ask-only-when-absent fallback): {SKILL_STEP1_CONSUME!r}"
        )
    if ORCH_RESET_IRON_RULE not in orch:
        errors.append(
            f"invariant 3 ({ORCH}): the reset-boundary iron rule no longer "
            f"scopes its MANDATORY list to the Stage 5 entry gate: "
            f"{ORCH_RESET_IRON_RULE!r}"
        )
    if SKILL_OVERVIEW_ORDERING not in skill:
        errors.append(
            f"invariant 4 ({SKILL}): the overview summary lost the "
            f"delivery-before-acknowledgement ordering: "
            f"{SKILL_OVERVIEW_ORDERING!r}"
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
    # Invariant 4 — SKILL mirror: section-scoped Stage 6 protocol block (the
    # operative copy) + the rule-10 state-machine-list copy (file-unique pin)
    errors.extend(
        check_section_literals(4, skill, SKILL_STAGE6_HEADING,
                               f"{SKILL} Stage-6 protocol",
                               SKILL_STAGE6_LITERALS)
    )
    if not _line_pinned(skill, SKILL_STEP4_HANDOFF):
        errors.append(
            f"invariant 4 ({SKILL}): Step 4 transition list lost the Stage "
            f"5->6 handoff line: {SKILL_STEP4_HANDOFF!r}"
        )
    if SKILL_RULE9_PIN not in skill:
        errors.append(
            f"invariant 4 ({SKILL}): state-machine rule 9 lost the "
            f"completion-type + decline-outcome pin: {SKILL_RULE9_PIN!r}"
        )
    if SKILL_RULE10_PIN not in skill:
        errors.append(
            f"invariant 4 ({SKILL}): state-machine rule 10 lost the terminal-"
            f"acknowledgement pin: {SKILL_RULE10_PIN!r}"
        )
    # Invariant 4 — ORCH mirror: vocabulary + decline handoff + wiring pairs
    if VOCAB_CANON not in orch:
        errors.append(
            f"invariant 4 ({ORCH}): canonical terminal-acknowledgement "
            f"vocabulary missing: {VOCAB_CANON!r}"
        )
    if ORCH_DECLINE_HANDOFF_PIN not in orch:
        errors.append(
            f"invariant 4 ({ORCH}): Stage 5->6 handoff row lost the decline "
            f"semantics: {ORCH_DECLINE_HANDOFF_PIN!r}"
        )
    if ORCH_STAGE56_TRIGGER_PIN not in orch:
        errors.append(
            f"invariant 4 ({ORCH}): Stage 5->6 handoff row lost the type-"
            f"bearing completion trigger: {ORCH_STAGE56_TRIGGER_PIN!r}"
        )
    if not _line_pinned(orch, ORCH_SKIPPABLE_PIN):
        errors.append(
            f"invariant 4 ({ORCH}): the skippable-stages line drifted from "
            f"the pinned form (it must carry Stage 6 with its decline "
            f"scope): {ORCH_SKIPPABLE_PIN!r}"
        )
    if not _line_pinned(orch, ORCH_STAGE56_HANDOFF_ROW):
        errors.append(
            f"invariant 4 ({ORCH}): the Stage 5 -> 6 handoff row drifted "
            f"from the pinned form: {ORCH_STAGE56_HANDOFF_ROW!r}"
        )
    if not _line_pinned(orch, ORCH_NON_SKIPPABLE_LINE):
        errors.append(
            f"invariant 4 ({ORCH}): the non-skippable line drifted from the "
            f"pinned form (it must not gain Stage 6): "
            f"{ORCH_NON_SKIPPABLE_LINE!r}"
        )
    if ORCH_ENGAGEMENT_FULL_EXCEPTION not in orch:
        errors.append(
            f"invariant 3 ({ORCH}): the engagement-tracking SLIM downgrade "
            f"lost its FULL-checkpoint exception: "
            f"{ORCH_ENGAGEMENT_FULL_EXCEPTION!r}"
        )
    for name, fragment in ORCH_TERMINAL_WIRING.items():
        if fragment not in orch:
            errors.append(
                f"invariant 4 ({ORCH}): state_tracker {name} pair missing: "
                f"{fragment!r}"
            )
    # Invariant 4 — protocol mirror: vocabulary + decline + non-ack rule
    for fragment in (VOCAB_PROTO, VOCAB_PROTO_NL_CLAUSE):
        if fragment not in proto:
            errors.append(
                f"invariant 4 ({PROTO}): canonical terminal-acknowledgement "
                f"vocabulary missing: {fragment!r}"
            )
    if PROTO_DECLINE_PIN not in proto:
        errors.append(
            f"invariant 4 ({PROTO}): trigger line lost the decline semantics: "
            f"{PROTO_DECLINE_PIN!r}"
        )
    if PROTO_CHANGE_REQUESTS_NOT_ACK not in proto:
        errors.append(
            f"invariant 4 ({PROTO}): change-request non-acknowledgement rule "
            f"missing: {PROTO_CHANGE_REQUESTS_NOT_ACK!r}"
        )
    if PROTO_ACK_OUTCOME not in proto:
        errors.append(
            f"invariant 4 ({PROTO}): terminal-acknowledgement outcome "
            f"sentence missing: {PROTO_ACK_OUTCOME!r}"
        )
    if PROTO_TRIGGER_PIN not in proto:
        errors.append(
            f"invariant 4 ({PROTO}): trigger line lost the type-bearing "
            f"completion trigger: {PROTO_TRIGGER_PIN!r}"
        )
    if PROTO_SEQUENCING_PIN not in proto:
        errors.append(
            f"invariant 4 ({PROTO}): delivery-before-acknowledgement "
            f"sequencing missing: {PROTO_SEQUENCING_PIN!r}"
        )
    if PROTO_STEP5_HEADER not in proto:
        errors.append(
            f"invariant 4 ({PROTO}): step-5 terminal-checkpoint header "
            f"missing: {PROTO_STEP5_HEADER!r}"
        )
    if PROTO_NO_NEXT_STAGE not in proto:
        errors.append(
            f"invariant 4 ({PROTO}): terminal-outcome sentence missing: "
            f"{PROTO_NO_NEXT_STAGE!r}"
        )
    # Invariant 4 — state_tracker contract accepts Stage 6 + outcome pairs
    if tracker:
        if TRACKER_STAGE_ID_ENUM not in tracker:
            errors.append(
                f"invariant 4 ({TRACKER}): update_stage stage_id enum no "
                f"longer includes \"6\": {TRACKER_STAGE_ID_ENUM!r}"
            )
        if TRACKER_STAGE6_ENTRY not in tracker:
            errors.append(
                f"invariant 4 ({TRACKER}): the stages example lost its "
                f"Stage 6 entry ({TRACKER_STAGE6_ENTRY!r})"
            )
        for name, fragment in TRACKER_WIRING.items():
            if fragment not in tracker:
                errors.append(
                    f"invariant 4 ({TRACKER}): {name} pair missing: "
                    f"{fragment!r}"
                )
        if TRACKER_PREREQ_STAGE2_ROW not in tracker:
            errors.append(
                f"invariant 1 ({TRACKER}): check_prerequisites Stage 2 row "
                f"no longer recommends the Methodology Blueprint: "
                f"{TRACKER_PREREQ_STAGE2_ROW!r}"
            )
        if TRACKER_PREREQ_STAGE6_ROW not in tracker:
            errors.append(
                f"invariant 4 ({TRACKER}): check_prerequisites lost its "
                f"Stage 6 row: {TRACKER_PREREQ_STAGE6_ROW!r}"
            )
        if not _line_pinned(tracker, TRACKER_STATUS_ENUM_ROW):
            errors.append(
                f"invariant 4 ({TRACKER}): update_stage status enum drifted "
                f"from the pinned form (the terminal wiring depends on "
                f"'completed'/'skipped'): {TRACKER_STATUS_ENUM_ROW!r}"
            )
        if not _line_pinned(tracker, TRACKER_GLOBAL_COMPLETED):
            errors.append(
                f"invariant 4 ({TRACKER}): update_pipeline_state legal "
                f"values lost `completed`: {TRACKER_GLOBAL_COMPLETED!r}"
            )

    return errors


def check_content_locks() -> list[str]:
    """Whole-file sha256 locks for the two #528-central reference docs."""
    errors: list[str] = []
    for path, expected in CONTENT_LOCKS.items():
        full = REPO_ROOT / path
        if not full.is_file():
            errors.append(f"content lock: file missing: {path}")
            continue
        actual = hashlib.sha256(full.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(
                f"content lock ({path}): sha256 {actual} != pinned "
                f"{expected}. Any change to this operative reference doc "
                f"must update CONTENT_LOCKS in the same commit, with the "
                f"semantic change reviewed against the #528 resolutions "
                f"(see the update procedure in this lint's header)."
            )
    return errors


def main() -> int:
    contents = {}
    for path in (SKILL, ORCH, SM, PROTO, TRACKER):
        full = REPO_ROOT / path
        if not full.is_file():
            print(f"FAILED: surface file missing: {path}", file=sys.stderr)
            return 1
        contents[path] = full.read_text(encoding="utf-8")
    errors = check(contents[SKILL], contents[ORCH], contents[SM],
                   contents[PROTO], contents[TRACKER])
    errors.extend(check_content_locks())
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
