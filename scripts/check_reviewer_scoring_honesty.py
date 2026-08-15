#!/usr/bin/env python3
"""Guard criterion-bound reviewer judgement and calibration honesty.

This lint protects current runtime/documentation surfaces. Historical design
records and unrelated scoring systems are intentionally out of scope.

Exit 0: contract present; 1: drift; 2: required input missing.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

LIVE_FILES = (
    "academic-paper-reviewer/SKILL.md",
    "academic-paper-reviewer/agents/eic_agent.md",
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md",
    "academic-paper-reviewer/agents/domain_reviewer_agent.md",
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md",
    "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md",
    "academic-paper-reviewer/agents/editorial_synthesizer_agent.md",
    "academic-paper-reviewer/references/quality_rubrics.md",
    "academic-paper-reviewer/references/review_criteria_framework.md",
    "academic-paper-reviewer/references/review_quality_thinking.md",
    "academic-paper-reviewer/references/editorial_decision_standards.md",
    "academic-paper-reviewer/references/statistical_reporting_standards.md",
    "academic-paper-reviewer/references/calibration_mode_protocol.md",
    "academic-paper-reviewer/references/sprint_contract_protocol.md",
    "academic-paper-reviewer/templates/peer_review_report_template.md",
    "academic-paper-reviewer/examples/hei_paper_review_example.md",
    "academic-paper-reviewer/examples/interdisciplinary_review_example.md",
    "academic-paper-reviewer/examples/subclaim_decomposition_example.md",
    "academic-paper/agents/peer_reviewer_agent.md",
    "academic-paper/agents/literature_strategist_agent.md",
    "academic-paper/SKILL.md",
    "academic-paper/references/failure_paths.md",
    "academic-paper/references/workflow_phase_details.md",
    "academic-pipeline/SKILL.md",
    "academic-pipeline/agents/pipeline_orchestrator_agent.md",
    "academic-pipeline/references/score_trajectory_protocol.md",
    "academic-pipeline/references/integrity_review_protocol.md",
    "shared/handoff_schemas.md",
    "docs/ARCHITECTURE.md",
    "README.md",
)

REQUIRED = {
    "academic-paper-reviewer/references/quality_rubrics.md": (
        "`NOT_CALIBRATED` — the required default",
        "Individual reviewer seats always emit `NOT_CALIBRATED`",
        "current Schema 6 package adapter also remains",
        "`EXCEEDS` / `MEETS` / `PARTLY_MEETS` / `DOES_NOT_MEET` / `NOT_ASSESSED`",
        "no universal minimum source count",
        "no universal peer-reviewed-source ratio",
        "Do not map any total or count of labels mechanically",
    ),
    "academic-paper-reviewer/templates/peer_review_report_template.md": (
        "Calibration status: `NOT_CALIBRATED`",
        "self-upgrade from a candidate profile",
        "Do not assign points, calculate a weighted total, rank papers",
        "Confidence is an uncertainty/scope disclosure only",
    ),
    "academic-paper-reviewer/references/calibration_mode_protocol.md": (
        "An ordinary review has `calibration_status: NOT_CALIBRATED`",
        "The directional tier always reports `calibration_status: NOT_CALIBRATED`",
        "application_status: NOT_WIRED_TO_LIVE_REVIEW",
        "future application example only",
        "per_dimension_gold_judgements",
        "Do not report AUC: there is no continuous rubric score",
        "execution_topology_sha256",
    ),
    "academic-pipeline/references/score_trajectory_protocol.md": (
        "No current producer emits `criterion_trajectory`",
        "design contract, not wired to a current machine producer",
        "does not calculate rubric scores, numerical deltas, or a paper-quality ranking",
    ),
    "academic-paper/agents/literature_strategist_agent.md": (
        "Do not impose a universal final-source count",
        "no universal peer-reviewed ratio applies",
        "no universal per-theme source count",
        "no universal recent-source ratio",
        "do not total points or use journal rank/citation",
    ),
    "shared/handoff_schemas.md": (
        "Current Schema 6 producer emits `NOT_CALIBRATED`",
        "judgement_scale: sprint_contract",
        "Producers never translate between the two scales",
        "Historical numeric values cannot feed current synthesis, trajectory, or calibration",
        "*(legacy/read-only)* Historical 0-100 editorial-confidence field",
    ),
    "docs/ARCHITECTURE.md": (
        "No numerical delta or typed machine trajectory is currently emitted",
        "100% of E1 registered claims; semantic extraction completeness unknown",
    ),
    "academic-paper-reviewer/agents/editorial_synthesizer_agent.md": (
        "Schema 6 criterion adapter and calibration boundary",
        "judgement_scale: sprint_contract",
        "Set the package-level `calibration_status` to `NOT_CALIBRATED`",
        "Confidence and competence disclosure — never a weighting rule",
    ),
    "academic-paper-reviewer/references/sprint_contract_protocol.md": (
        "The Schema 6 adapter preserves the sprint vocabulary exactly",
        "Package calibration remains `NOT_CALIBRATED`",
    ),
    "academic-paper-reviewer/examples/hei_paper_review_example.md": (
        "R1's confidence remains uncertainty/scope metadata and does not determine the resolution",
    ),
    "academic-paper-reviewer/examples/interdisciplinary_review_example.md": (
        "Confidence is retained only as uncertainty/scope metadata and never governs arbitration",
        "Confidence neither strengthens nor softens that conclusion",
    ),
    "academic-paper-reviewer/examples/subclaim_decomposition_example.md": (
        "Confidence remains uncertainty/scope metadata and does not prioritize the finding",
    ),
    "academic-paper/SKILL.md": (
        "five-perspective categorical assessment",
    ),
    "academic-paper/references/failure_paths.md": (
        "Criterion-bound trigger: at least one named, decision-critical criterion is",
        "`DOES_NOT_MEET`, with the manuscript evidence and applicable standard stated",
        "A decision-critical criterion is `NOT_ASSESSED` because required evidence is",
    ),
    "academic-pipeline/SKILL.md": (
        "Criterion status: [named criterion + evidence-anchored categorical judgement, or `NOT_COMPARABLE`]",
        "Never reduce this to a hidden scalar",
    ),
    "academic-pipeline/agents/pipeline_orchestrator_agent.md": (
        "Criterion status: [named criterion + evidence-anchored categorical judgement, or `NOT_COMPARABLE`]",
    ),
    "README.md": (
        "Current live reviews remain `NOT_CALIBRATED`",
        "the typed trajectory carrier is deferred",
    ),
}

for _agent in (
    "academic-paper-reviewer/agents/eic_agent.md",
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md",
    "academic-paper-reviewer/agents/domain_reviewer_agent.md",
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md",
    "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md",
):
    REQUIRED[_agent] = (
        "### Calibration Status",
        "Seat reports always emit `NOT_CALIBRATED`",
        "### Criterion-Bound Judgements",
        "Do not total, weight, average, or mechanically map",
        "Confidence is an uncertainty/scope disclosure only",
    )

# Positive forms only. Prohibitory prose such as "do not calculate a weighted
# total" is allowed and protected by REQUIRED witnesses.
FORBIDDEN = (
    ("fixed 0-100 decision boundary", re.compile(
        r"(?i)(?:>=|≥)\s*80.{0,35}\baccept|"
        r"\b65\s*[-–]\s*79.{0,35}\bminor|"
        r"\b50\s*[-–]\s*64.{0,35}\bmajor|"
        r"(?:<|below)\s*50.{0,35}\breject"
    )),
    ("numeric reviewer rubric table", re.compile(
        r"(?im)^\|\s*(?:90\s*[-–]\s*100|9\s*[-–]\s*10)\s*\|"
    )),
    ("weighted reviewer result", re.compile(
        r"\b(?:final|overall)\s+score\s*=|"
        r"^\|\s*\*\*weighted average\*\*\s*\||"
        r"\bfour raw scoring-seat weighted averages\b",
        re.IGNORECASE | re.MULTILINE,
    )),
    ("fixed peer-reviewed ratio", re.compile(
        r"(?i)peer[- ]reviewed\s+(?:ratio\s*)?(?:>=|≥|>|at least)\s*\d+\s*%|"
        r"\d+\s*%\+?\s+peer[- ]reviewed"
    )),
    ("cross-domain source quota", re.compile(
        r"(?im)^\|\s*(?:IMRaD|Literature Review|Theoretical|Case Study|Policy Brief|Conference)\s*\|\s*\d+\s*\|"
    )),
    ("fixed per-theme literature quota", re.compile(
        r"(?i)(?:every|each)\s+theme.{0,25}(?:>=|≥|at least)\s*\d+\s+sources?"
    )),
    ("fixed literature-gap quota", re.compile(
        r"(?i)research\s+gaps?.{0,15}(?:>=|≥|at least)\s*\d+"
    )),
    ("fixed recency ratio", re.compile(
        r"(?i)currency.{0,35}(?:>=|≥|at least)\s*\d+\s*%.{0,20}(?:last|recent)"
    )),
    ("fixed language ratio", re.compile(
        r"(?i)(?:chinese|english)\s+literature.{0,25}(?:>=|≥|at least|comprise)\s*\d+\s*%"
    )),
    ("retired score trajectory", re.compile(
        r"(?i)score\s+trajectory(?:\s+tracked|\s+visualization)"
    )),
    ("unbounded all-claim final check", re.compile(
        r"(?i)final-check\s+mode:\s*100%\s+of\s+claims\b"
    )),
    ("calibration overclaim", re.compile(
        r"(?i)provides calibrated scoring rubrics|"
        r"ensures consistent, reproducible scoring|"
        r"without calibration.{0,80}ordinally meaningful"
    )),
    ("retired statistical completeness score", re.compile(
        r"(?i)statistical reporting completeness score"
    )),
    ("retired score-first reviewer heuristic", re.compile(
        r"(?i)write the score first"
    )),
    ("seat-level measured-profile upgrade", re.compile(
        r"(?i)(?:replace|upgrade).{0,40}PROFILE_MEASURED"
    )),
    ("scalar checkpoint quality comparison", re.compile(
        r"(?i)quality indicators:\s*\[score if available\]|"
        r"latest output\s*[≥>]\s*the quality"
    )),
    ("live typed-trajectory overclaim", re.compile(
        r"(?i)(?:criterion trajectory tracks|criterion trajectory visualization|"
        r"current producers emit `criterion_trajectory`)"
    )),
    ("mechanical confidence weighting", re.compile(
        r"(?is)(?:\bScore-?5\b.{0,160}\b(?:outweighs|takes precedence over|overrides)\b.{0,160}\bScore-?2\b|"
        r"^\|\s*Score\s*\|[^\n]*Weight in Synthesis|"
        r"this reviewer's opinion carries the highest weight)"
    )),
    ("confidence-driven arbitration", re.compile(
        r"(?is)(?:"
        r"prioriti[sz]ed\s+by[^\n]{0,100}confidence[^\n]{0,40}weight|"
        r"per-finding\s+confidence[^\n]{0,180}governs?\s+arbitration|"
        r"arbitration\s+was\s+based\s+on\s*:\s*(?:\n[-*][^\n]*){0,5}confidence|"
        r"confidence\s+is\s+\d/5[^\n]{0,160}should\s+be\s+respected|"
        r"only\s+\d/5\s+confidence[^\n]{0,200}confidence\s+limitation"
        r")"
    )),
    ("retired reviewer scoring label", re.compile(
        r"(?i)five-dimension scoring"
    )),
    ("fixed dimension-score rejection threshold", re.compile(
        r"(?is)(?:two|2)\s+or\s+more.{0,60}dimensions?.{0,40}"
        r"(?:scored?\s*)?(?:below|under|<)\s*\d+"
    )),
)


def check(root: Path) -> tuple[list[str], bool]:
    errors: list[str] = []
    missing = False
    texts: dict[str, str] = {}
    for rel in LIVE_FILES:
        path = root / rel
        try:
            texts[rel] = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{rel}: required input unavailable: {exc}")
            missing = True

    for rel, witnesses in REQUIRED.items():
        text = texts.get(rel, "")
        for witness in witnesses:
            if witness not in text:
                errors.append(f"{rel}: missing honesty witness {witness!r}")

    for rel, text in texts.items():
        for label, pattern in FORBIDDEN:
            match = pattern.search(text)
            if match:
                excerpt = " ".join(match.group(0).split())
                errors.append(f"{rel}: {label}: {excerpt!r}")

    quality = texts.get("academic-paper-reviewer/references/quality_rubrics.md", "")
    for legacy in ("## Decision Mapping", "## Aggregation Formula", "Score Range", "Weight:"):
        if legacy in quality:
            errors.append(f"quality_rubrics.md: retired numeric surface remains: {legacy!r}")

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
    print("check_reviewer_scoring_honesty: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
