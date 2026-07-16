#!/usr/bin/env python3
"""Defrift lock for the #527 cross-model handoff contract.

#523 moved the blind-checkpoint transport to the dispatching layer, but left
the owner → dispatcher → owner path enforced by prose only. #527 gives it a
canonical envelope (normative grammar: `scripts/cross_model_handoff.py`) and
this lint pins the contract across its five prompt surfaces so a future edit
cannot silently demote the handoff to an ordinary deliverable.

Invariants:

1. The shared doc carries § Cross-model handoff envelope (#527) with both
   fence literals, all required header names, the payload-only blindness
   rule, the malformed→unavailable fail-safes, the agreement-no-reinvoke /
   divergence-minimum-context routing, the DA full-return rule, and the
   flag-unset-unchanged sentence — and names the reference module.
2. Each owner agent emits the canonical envelope with its correct
   checkpoint_kind / expected_result pair.
3. The Mode-A orchestrator carries the consumer contract: recognition
   (never an ordinary deliverable), fail-safe mapping, and the three-way
   outcome routing, naming the reference module.
4. The prose enums match the reference module's CHECKPOINT_KINDS (the
   module is normative — prose drift from it must fail).

Exit codes: 0 on pass, 1 on any failure.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cross_model_handoff as cmh

REPO_ROOT = Path(__file__).resolve().parent.parent

SHARED = "shared/cross_model_verification.md"
ORCH = "academic-pipeline/agents/pipeline_orchestrator_agent.md"
# Full backticked header declarations — pinning only the value would let a
# `checkpoint_knd:` typo emit malformed envelopes while staying green
# (codex #527 round-1 P1). The enum owners additionally pin their
# owner_decision blindness clause.
OWNER_BLINDNESS_CLAUSE = "never forwarded to the cross-model"
OWNERS = {
    "deep-research/agents/research_architect_agent.md": (
        "`checkpoint_kind: design_freeze`",
        "`expected_result: enum_comparison`",
        OWNER_BLINDNESS_CLAUSE,
    ),
    "academic-paper-reviewer/agents/editorial_synthesizer_agent.md": (
        "`checkpoint_kind: editorial_decision`",
        "`expected_result: enum_comparison`",
        OWNER_BLINDNESS_CLAUSE,
    ),
    "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md": (
        "`checkpoint_kind: da_critique`",
        "`expected_result: full_return`",
        "no `owner_decision` header",
    ),
}

SHARED_HEADING = "### Cross-model handoff envelope (#527)"
SHARED_REQUIRED = [
    cmh.OPEN_FENCE,
    cmh.CLOSE_FENCE,
    "scripts/cross_model_handoff.py",
    "checkpoint_kind: design_freeze | editorial_decision | da_critique",
    "expected_result: enum_comparison | full_return",
    "correlation_id:",
    "owner_decision:",
    "NEVER forwarded to the cross-model",
    "payload only",
    "[CROSS-MODEL-ERROR: malformed_handoff]",
    "[CROSS-MODEL-ERROR: malformed_result]",
    "outcome `unavailable`",
    "does **not** re-invoke the owner",
    "re-invokes the ORIGINAL owner with the minimum return context",
    "The dispatcher never authors it",
    "EVERY successful response is returned to the owner",
    "owners emit no envelope and behavior is byte-equivalent pre-#527",
]

ORCH_HEADING_LINE = "**Cross-model handoff consumption (#527, Mode A dispatcher).**"
ORCH_REQUIRED = [
    cmh.OPEN_FENCE,
    "a transport request, never an ordinary deliverable",
    "scripts/cross_model_handoff.py",
    "[CROSS-MODEL-ERROR: malformed_handoff]",
    "[CROSS-MODEL-ERROR: malformed_result]",
    "never fabricate a judgment",
    "do NOT re-invoke the owner",
    "re-invoke the ORIGINAL owner with the minimum return context",
    "never the dispatcher's",
    "every successful response returns to the owner",
    "[CROSS-MODEL-SKIPPED]",
]


def _module_prose_enums() -> list[str]:
    """The enum spellings the prose table must carry, derived from the
    normative module so prose can only drift by failing here."""
    fragments = []
    for kind, (_, enum) in cmh.CHECKPOINT_KINDS.items():
        if enum:
            fragments.append(" / ".join(f"`{v}`" for v in enum))
    return fragments


def check(shared: str, orch: str, owners: dict[str, str]) -> list[str]:
    errors: list[str] = []

    # Invariant 1 — shared canonical section
    if SHARED_HEADING not in shared:
        errors.append(f"invariant 1 ({SHARED}): section {SHARED_HEADING!r} missing")
    for fragment in SHARED_REQUIRED:
        if fragment not in shared:
            errors.append(
                f"invariant 1 ({SHARED}): canonical contract lost the pinned "
                f"fragment {fragment!r}"
            )

    # Invariant 2 — owner emission pins
    for path, fragments in OWNERS.items():
        text = owners[path]
        if cmh.OPEN_FENCE not in text:
            errors.append(
                f"invariant 2 ({path}): owner no longer names the canonical "
                f"envelope fence {cmh.OPEN_FENCE!r}"
            )
        for fragment in fragments:
            if fragment not in text:
                errors.append(
                    f"invariant 2 ({path}): owner lost its {fragment!r} "
                    f"declaration"
                )

    # Invariant 3 — Mode-A dispatcher consumer contract
    if ORCH_HEADING_LINE not in orch:
        errors.append(f"invariant 3 ({ORCH}): consumer block {ORCH_HEADING_LINE!r} missing")
    for fragment in ORCH_REQUIRED:
        if fragment not in orch:
            errors.append(
                f"invariant 3 ({ORCH}): consumer contract lost the pinned "
                f"fragment {fragment!r}"
            )

    # Invariant 4 — prose enums match the normative module
    for enum_fragment in _module_prose_enums():
        if enum_fragment not in shared:
            errors.append(
                f"invariant 4 ({SHARED}): checkpoint enum table drifted from "
                f"the normative module: expected {enum_fragment!r} "
                f"(source: scripts/cross_model_handoff.py CHECKPOINT_KINDS)"
            )

    return errors


def main() -> int:
    paths = [SHARED, ORCH, *OWNERS]
    contents: dict[str, str] = {}
    for path in paths:
        full = REPO_ROOT / path
        if not full.is_file():
            print(f"FAILED: surface file missing: {path}", file=sys.stderr)
            return 1
        contents[path] = full.read_text(encoding="utf-8")
    errors = check(contents[SHARED], contents[ORCH], {p: contents[p] for p in OWNERS})
    if errors:
        for e in errors:
            print(f"FAILED: {e}", file=sys.stderr)
        print(
            "\nUpdate procedure: scripts/cross_model_handoff.py is the "
            "normative grammar. If the contract must change, change the "
            "module, its fixtures, every listed surface, AND this lint's "
            "pinned constants in the same commit.",
            file=sys.stderr,
        )
        return 1
    print("PASSED: check_cross_model_handoff_contract — 4 invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
