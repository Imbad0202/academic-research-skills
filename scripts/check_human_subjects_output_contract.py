#!/usr/bin/env python3
"""Lint the #665 human-subjects readiness/authorization output boundary.

This is a prompt/reference contract lint, not an authorization engine.  It pins
the load-bearing output grammar on the two emitting agents and the durable
post-migration authority boundary on their references.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ETHICS_AGENT = Path("deep-research/agents/ethics_review_agent.md")
ARCHITECT_AGENT = Path("deep-research/agents/research_architect_agent.md")
DEEP_RESEARCH_SKILL = Path("deep-research/SKILL.md")
ETHICS_CHECKLIST = Path("deep-research/references/ethics_checklist.md")
IRB_REFERENCE = Path("deep-research/references/irb_decision_tree.md")
FAILURE_PATHS = Path("deep-research/references/failure_paths.md")

FOOTER = (
    "**Human-subjects boundary:** This output does not authorize recruitment, "
    "consent, access to identifiable data, intervention, or data collection."
)

DECISION_LOG_BLOCK = """### Ethics Decision Log
[One row per CONDITIONAL or BLOCKED item the user acted on. This is the standalone-deep-research analog of the pipeline's override record in the Stage 6 AI Self-Reflection Report + Material Passport ledger (`shared/compliance_checkpoint_protocol.md`). It surfaces, to the user, the record of "who decided what counts as harm, and why," so it travels with the research. Omit the table only when the verdict was CLEARED with no actioned items.]

| Item | Verdict | User decision | Reasoning |
|------|---------|---------------|-----------|
| [what was flagged] | [CONDITIONAL / BLOCKED] | [accept fix / override with reasoning / revise] | [why — user's stated reasoning, recorded verbatim for an override] |"""

REQUIRED: dict[Path, tuple[str, ...]] = {
    ETHICS_AGENT: (
        "### AI-Assisted Research-Integrity Verdict: [CLEARED / CONDITIONAL / BLOCKED]",
        "`submission_readiness`: `gaps_located | no_listed_gaps_located | unresolved`",
        "`authorization_status`: `documented | not_provided | cannot_verify`",
        "`review_pathway`: always `institutional determination required`",
        "A readiness result must never derive, promote, or update authorization status.",
        "It is not human-subjects clearance or authorization.",
        FOOTER,
        DECISION_LOG_BLOCK,
    ),
    ARCHITECT_AGENT: (
        "the pathway field must read `institutional determination required`",
        "`submission_readiness` (`gaps_located | no_listed_gaps_located | unresolved`)",
        "`authorization_status` (`documented | not_provided | cannot_verify`)",
        "Readiness never establishes or updates authorization.",
        "`unknown — obtain current institutional estimate`",
        "### Human-Subjects Administrative Status (if human subjects involved)",
        "- Review pathway: institutional determination required",
        "- Submission readiness: [gaps_located / no_listed_gaps_located / unresolved]",
        "- Authorization status: [documented / not_provided / cannot_verify]",
        "- Review timeline: unknown — obtain current institutional estimate",
        FOOTER,
    ),
    DEEP_RESEARCH_SKILL: (
        "Integrity verdict only: CLEARED / CONDITIONAL / BLOCKED",
        "readiness and authorization reported separately; institutional determination required",
    ),
    ETHICS_CHECKLIST: (
        "Authority boundary (#665/#666/#680)",
        "the output pathway is `institutional determination required`",
    ),
    IRB_REFERENCE: (
        "Authority boundary (#665/#666/#680)",
        "ARS output must use `institutional determination required`",
    ),
    FAILURE_PATHS: (
        "any human-subjects authorization remains a separate institutional status",
    ),
}

FORBIDDEN: dict[Path, tuple[str, ...]] = {
    ETHICS_AGENT: (
        "| Human Subjects Ethics | pass/warn/fail/N-A",
        "IRB Level: [Exempt/Expedited/Full/N-A]",
        "### Verdict: [CLEARED / CONDITIONAL / BLOCKED]",
    ),
    ARCHITECT_AGENT: (
        "Determine Exempt/Expedited/Full Board",
        "IRB review timeline (2-8 weeks)",
        "### IRB Plan (if human subjects involved)",
        "IRB level: [Exempt / Expedited / Full Board]",
        "IRB timeline: [estimated weeks]",
    ),
}


def run_checks(root: Path) -> list[str]:
    errors: list[str] = []
    texts: dict[Path, str] = {}
    for rel in REQUIRED:
        path = root / rel
        try:
            texts[rel] = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{rel}: cannot read: {exc}")

    for rel, needles in REQUIRED.items():
        text = texts.get(rel)
        if text is None:
            continue
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel}: missing required #665 contract text: {needle!r}")

    for rel, needles in FORBIDDEN.items():
        text = texts.get(rel)
        if text is None:
            continue
        for needle in needles:
            if needle in text:
                errors.append(f"{rel}: forbidden determination-shaped text remains: {needle!r}")

    for rel in (ETHICS_AGENT, ARCHITECT_AGENT):
        text = texts.get(rel)
        if text is not None and text.count(FOOTER) != 1:
            errors.append(f"{rel}: fixed boundary footer must appear exactly once")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = run_checks(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Human-subjects output contract lint passed (#665).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
