#!/usr/bin/env python3
"""Static contract for bounded reviewer calibration tiers."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "academic-paper-reviewer/references/calibration_mode_protocol.md"
SKILL = "academic-paper-reviewer/SKILL.md"
HANDOFF = "shared/handoff_schemas.md"
SYNTHESIZER = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
PEER_REVIEWER = "academic-paper/agents/peer_reviewer_agent.md"
WORKFLOW = "academic-paper/references/workflow_phase_details.md"
CROSS_MODEL = "shared/cross_model_verification.md"

PROTOCOL_WITNESSES = (
    "An ordinary review has `calibration_status: NOT_CALIBRATED`",
    "The full tier may produce a candidate empirical target profile only after completing the protocol",
    "application_status: NOT_WIRED_TO_LIVE_REVIEW",
    "future application example only",
    "The directional tier always reports `calibration_status: NOT_CALIBRATED`",
    "Full: 5–20 user-adjudicated papers",
    "Directional: exactly three papers",
    "per_dimension_gold_judgements",
    "Gold verdicts, dimension judgements, rationales, and human assessments must not enter field-analyst, reviewer, or synthesizer context",
    "Run 3 or 5 panel replicates per paper",
    "does not establish cross-replicate freshness or independent error processes",
    "Do not report AUC: there is no continuous rubric score",
    "Do not assign distances between categories, average the labels",
    "It must not report balanced accuracy, FNR, FPR, AUC, confidence intervals, stability",
    "calibration_status: NOT_CALIBRATED",
    "calibration_status: PROFILE_MEASURED",
    "a candidate cannot be applied to a live review",
    "This isolation applies to transport as well as prompt construction",
    "joined material cannot be fed back into another panel",
    "run its closed calibration data-fence collision preflight",
    "A collision refuses the entire attempt before transport",
    "use the same transport and substrate for every paper",
    "execute the complete schedule on that",
    "invalidates the whole attempt",
    "diagnostic-only and must not enter any aggregate",
    "new `attempt_id`, an empty aggregate, and restarts at paper 1 /",
    "Never resume the failed attempt, mix",
    "> application_status: NOT_WIRED_TO_LIVE_REVIEW",
    "Live profile application is not implemented in the current release",
    "cannot upgrade this live review",
    "cross-replicate freshness is unverified",
    "must not describe the repeated panels as independent",
)

SKILL_WITNESSES = (
    "Current live reviews and Schema 6 packages declare `NOT_CALIBRATED`",
    "application_status: NOT_WIRED_TO_LIVE_REVIEW",
    "per-seat categorical judgements",
    "remains `NOT_CALIBRATED`",
    "current tooling does not compare context IDs across replicates",
    "cross-replicate freshness as unverified",
)

HANDOFF_WITNESSES = (
    "Current Schema 6 producer emits `NOT_CALIBRATED`",
    "`PROFILE_MEASURED` is reserved until a closed, hash-bound empirical-profile contract",
)

SYNTHESIZER_WITNESSES = (
    "Set the package-level `calibration_status` to `NOT_CALIBRATED`",
    "A candidate profile, prose profile ID, or apparent match",
)

PEER_REVIEWER_WITNESSES = (
    "Every live Phase 6 report declares `calibration_status: NOT_CALIBRATED`",
    "unconditionally in the current release",
    "`application_status: NOT_WIRED_TO_LIVE_REVIEW`",
    "apparent metadata match cannot upgrade a live reviewer report",
)

WORKFLOW_WITNESSES = (
    "Every live Phase 6 report and downstream review package emits",
    "`calibration_status: NOT_CALIBRATED` unconditionally in the current release",
    "`application_status: NOT_WIRED_TO_LIVE_REVIEW`",
    "apparent metadata match cannot upgrade the live status",
)

# These clauses are non-numeric safety boundaries. They deliberately remain
# independent of the categorical calibration/reporting contract above: removing
# numeric scoring must never remove transport, isolation, or retry guards.
CROSS_MODEL_WITNESSES = {
    "homogeneous calibration transport": (
        "Calibration transport exception (#611 — non-sprint, attempt-atomic)",
        "Reviewer 2 substrate swap is exactly one stateless provider call",
        "byte-for-byte mirrors the same replicate's primary-family calibration Reviewer 2 invocation",
        "every paper and replicate uses the single-call branch above",
        "This is a transport-only substitution",
    ),
    "gold isolation": (
        "MUST NOT send a sprint contract, a paper-blind Phase 1 request",
        "any gold label, human score, per-dimension gold, or gold rationale",
        "without consulting any gold material",
    ),
    "delimiter-collision preflight": (
        "Calibration data-fence collision preflight (closed)",
        "byte-for-byte inside `<reviewer_configuration>...</reviewer_configuration>`",
        "byte-for-byte inside `<paper_content>...</paper_content>`",
        "`</\\s*reviewer_configuration\\b[^>]*>`",
        "`</\\s*paper_content\\b[^>]*>`",
        "refuse the entire calibration attempt before transport and send no provider call containing either payload",
        "MUST NOT escape, strip, rewrite, truncate, switch delimiters, or fall back to primary routing",
        "a different longer tag such as `</paper_contents>` does not match",
        "closed at exactly these two tag names",
    ),
    "attempt-atomic restart": (
        "lock one `attempt_id` and one `substrate_plan`",
        "mark the entire attempt invalid",
        "diagnostic-only and MUST NOT enter any aggregate",
        "Never continue the failed paper or a later replicate on primary routing",
        "new `attempt_id`, an empty aggregate, and a restart at paper 1 / replicate 1",
        "Before a homogeneous attempt finishes, MUST NOT emit full-tier metrics",
        "This attempt-atomic override is calibration-only",
    ),
}

FORBIDDEN_PROTOCOL = (
    "per_dimension_gold_scores",
    "Weighted Average",
    "weighted averages",
    "median rubric score",
    "mean absolute calibration error",
    "±X points",
)

FORBIDDEN_FRESHNESS_CLAIMS = (
    "fresh-context panels per paper",
    "Full-tier repeats use fresh contexts",
)


def check(root: Path) -> tuple[list[str], bool]:
    errors: list[str] = []
    missing = False
    texts: dict[str, str] = {}
    for rel in (
        PROTOCOL,
        SKILL,
        HANDOFF,
        SYNTHESIZER,
        PEER_REVIEWER,
        WORKFLOW,
        CROSS_MODEL,
    ):
        try:
            texts[rel] = (root / rel).read_text(encoding="utf-8")
        except OSError as exc:
            texts[rel] = ""
            errors.append(f"{rel}: unavailable: {exc}")
            missing = True
    protocol = texts[PROTOCOL]
    skill = texts[SKILL]

    for witness in PROTOCOL_WITNESSES:
        if witness not in protocol:
            errors.append(f"{PROTOCOL}: missing witness {witness!r}")
    for witness in SKILL_WITNESSES:
        if witness not in skill:
            errors.append(f"{SKILL}: missing witness {witness!r}")
    for rel, witnesses in (
        (HANDOFF, HANDOFF_WITNESSES),
        (SYNTHESIZER, SYNTHESIZER_WITNESSES),
        (PEER_REVIEWER, PEER_REVIEWER_WITNESSES),
        (WORKFLOW, WORKFLOW_WITNESSES),
    ):
        for witness in witnesses:
            if witness not in texts[rel]:
                errors.append(f"{rel}: missing witness {witness!r}")
    for label, witnesses in CROSS_MODEL_WITNESSES.items():
        for witness in witnesses:
            if witness not in texts[CROSS_MODEL]:
                errors.append(
                    f"{CROSS_MODEL}: {label} lost witness {witness!r}"
                )
    for forbidden in FORBIDDEN_PROTOCOL:
        if forbidden in protocol:
            errors.append(f"{PROTOCOL}: retired numeric calibration token {forbidden!r}")
    for forbidden in FORBIDDEN_FRESHNESS_CLAIMS:
        if forbidden in protocol:
            errors.append(
                f"{PROTOCOL}: overstated cross-replicate freshness claim {forbidden!r}"
            )

    # A score-to-decision mapping must never be smuggled into calibration mode.
    if re.search(
        r"(?i)(?:>=|≥)\s*80.{0,30}accept|65\s*[-–]\s*79.{0,30}minor|"
        r"50\s*[-–]\s*64.{0,30}major|(?:<|below)\s*50.{0,30}reject",
        protocol,
    ):
        errors.append(f"{PROTOCOL}: fixed score-to-decision mapping is prohibited")

    # The current live producer is not profile-applying. An apparent match is
    # therefore never a condition for upgrading either the reviewer report or
    # Schema 6 package.
    for rel in (PEER_REVIEWER, WORKFLOW):
        if re.search(
            r"(?is)calibration_status:\s*NOT_CALIBRATED.{0,160}\bunless\b",
            texts[rel],
        ):
            errors.append(
                f"{rel}: live NOT_CALIBRATED status must be unconditional"
            )
    if "No empirical target profile matches this review" in protocol:
        errors.append(
            f"{PROTOCOL}: live disclosure must say application is NOT_WIRED, "
            "not merely that no profile matched"
        )

    return errors, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    errors, missing = check(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 2 if missing else 1
    print("check_calibration_tiers: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
