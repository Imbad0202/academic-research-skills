#!/usr/bin/env python3
"""Pin #611's public Journal-Fit Reviewer name and frozen eic/EIC tokens."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _skill_lint import read_or_exit2


REPO_ROOT = Path(__file__).resolve().parents[1]
DISPLAY_LABEL = "Journal-Fit Reviewer"
INTERNAL_ROLE = "eic"
SERIALIZED_ROLE = "EIC"

REQUIRED = {
    "README.md": (
        "(Journal-Fit Reviewer + 3 dynamic reviewers + Devil's Advocate)",
        "full mode (Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate)",
        "First-round review panel vs. contract-governed re-review dispatch boundary",
    ),
    "README.zh-TW.md": (
        "（Journal-Fit Reviewer + 3 位動態審查者 + 魔鬼代言人）",
        "full mode（Journal-Fit Reviewer + R1/R2/R3 + 魔鬼代言人）",
        "第一輪審查面板 vs. 契約治理再審派送的分界",
    ),
    "README.zh-CN.md": (
        "（Journal-Fit Reviewer + 3 位动态审查者 + 魔鬼代言人）",
        "full mode（Journal-Fit Reviewer + R1/R2/R3 + 魔鬼代言人）",
        "第一轮审查面板 vs. 契约治理再审调度的分界",
    ),
    "README.ja-JP.md": (
        "（Journal-Fit Reviewer + 3 動的レビュアー + Devil's Advocate）",
        "full モード（Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate）",
        "初回レビューパネル vs. 契約管理された再レビューディスパッチの境界",
    ),
    "README.ko-KR.md": (
        "(Journal-Fit Reviewer + 동적 리뷰어 3명 + Devil's Advocate)",
        "full 모드 (Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate)",
        "1차 심사 패널 대 계약 기반 re-review 디스패치 경계",
    ),
    "MODE_REGISTRY.md": (
        "Journal-Fit Reviewer quick assessment + key issues list",
    ),
    "shared/mode_spectrum.md": (
        "Fixed Journal-Fit Reviewer quick-assessment format",
    ),
    "academic-paper-reviewer/SKILL.md": (
        "the public display name is **Journal-Fit Reviewer**",
        "`eic_agent` (agent), `eic` (`contract_role` / dispatch role), and `EIC`",
        "| 2 | `eic_agent` | Journal-Fit Reviewer",
        "Journal-Fit Reviewer quick assessment",
        "Those compatibility tokens do not select a Stage 3' agent file",
        "Three dedicated contract calls owned by the orchestrating layer",
        "orchestrating layer; routed-seat Phase 1/2A calls; Phase 2B integration call",
    ),
    "academic-paper-reviewer/agents/eic_agent.md": (
        "name: eic_agent",
        'description: "Journal-Fit Reviewer seat;',
        "# Journal-Fit Reviewer Agent",
        "## Journal-Fit Review Report",
        "contract_role: eic",
    ),
    "academic-paper-reviewer/agents/field_analyst_agent.md": (
        "**Role**: [EIC / Peer Reviewer 1 / Peer Reviewer 2 / Peer Reviewer 3]",
        "**Display role**: [Journal-Fit Reviewer",
        "**Journal-Fit Reviewer Configuration** (internal role `EIC`)",
        "[Card #1: Journal-Fit Reviewer (serialized source ID: EIC)]",
    ),
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md": (
        "Journal-Fit Reviewer recommendation, domain expertise score",
    ),
    "academic-paper-reviewer/agents/domain_reviewer_agent.md": (
        "Journal-Fit Reviewer recommendation, methodology score",
    ),
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md": (
        "Journal-Fit Reviewer recommendation, methodology score",
    ),
    "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md": (
        "The Journal-Fit Reviewer and R1/R2/R3",
        "Journal-Fit Reviewer recommendation, methodology/domain/perspective dimension scores",
        "the Journal-Fit Reviewer's role",
    ),
    "academic-paper-reviewer/agents/editorial_synthesizer_agent.md": (
        "| Dimension | Journal-Fit Reviewer | R1 (Methodology)",
        "### Journal-Fit Review Report Summary",
        "[EIC/R1/R2/R3/DA]",
        "A genuine SPLIT requires Journal-Fit Reviewer arbitration: the Journal-Fit Reviewer reviews all positions and makes a binding recommendation.",
        "one the Journal-Fit Reviewer adjudicates and rejects",
    ),
    "academic-paper-reviewer/references/sprint_contract_protocol.md": (
        "Journal-Fit Reviewer (`eic`) + methodology + domain + perspective + DA",
        "Journal-Fit Reviewer (`eic`) + methodology (only)",
    ),
    "academic-paper-reviewer/references/guided_mode_protocol.md": (
        "**Journal-Fit Reviewer opens**",
    ),
    "academic-paper-reviewer/references/top_journals_by_field.md": (
        "calibrating the Journal-Fit Reviewer identity",
        "### Logic for Selecting Journals for the Journal-Fit Reviewer",
    ),
    "academic-paper-reviewer/references/editorial_decision_standards.md": (
        "Journal-Fit Reviewer assessment only; advisory, not an editorial decision",
        "| Journal-Fit Reviewer | R1 | R2 | R3 | -> Recommended Decision |",
        "The Journal-Fit Reviewer (or synthesizer) needs to deeply analyze the cause of disagreement",
        "real journal's Editor-in-Chief (EIC)",
    ),
    "academic-paper-reviewer/references/re_review_mode_protocol.md": (
        "not by a single Journal-Fit Reviewer persona",
        "`EIC` (the stable wire label for the Journal-Fit Reviewer)",
        "Contract-governed default re-review invokes neither `eic_agent` nor `editorial_synthesizer_agent` as an agent-file worker",
        "Phase 2B is the dedicated Journal-Fit Reviewer (`EIC` wire label) / synthesizer-function integration call",
        "the closed rules derive the candidate decision state and `scripts/check_re_review_synthesis.py` recomputes it before surfacing",
        "Journal-Fit Reviewer guides user through Socratic dialogue",
    ),
    "academic-paper-reviewer/templates/peer_review_report_template.md": (
        "used by the Journal-Fit Reviewer and Reviewers 1-3",
        "[Journal-Fit Reviewer / Peer Reviewer 1",
    ),
    "academic-paper-reviewer/templates/editorial_decision_template.md": (
        "| Journal-Fit Reviewer | [Senior-editor or associate-editor identity]",
        "[EIC/R1/R2/R3/DA]",
    ),
    "academic-paper-reviewer/templates/revision_response_template.md": (
        "## Response to Journal-Fit Reviewer",
        "### Journal-Fit Reviewer Comment 1",
        "### Journal-Fit Reviewer Comment 2",
        "Journal-Fit Reviewer's comment",
        "each Journal-Fit Reviewer comment",
    ),
    "academic-paper-reviewer/examples/hei_paper_review_example.md": (
        "**Role**: EIC\n**Display role**: Journal-Fit Reviewer",
        "### Journal-Fit Review Report",
        "| Journal-Fit Reviewer | *Higher Education* Associate Editor",
        "Source: EIC-W1",
    ),
    "academic-paper-reviewer/examples/interdisciplinary_review_example.md": (
        "**Role**: EIC\n**Display role**: Journal-Fit Reviewer",
        "### Journal-Fit Review Report (Summary)",
        "Source: EIC-W1",
    ),
    "academic-paper-reviewer/examples/subclaim_decomposition_example.md": (
        "stable serialized reviewer ID `EIC` maps to the public display role **Journal-Fit Reviewer**",
        "| SC-1 | Statistics | EIC | not-mentioned",
        "Journal-Fit Reviewer arbitration",
    ),
    "academic-pipeline/SKILL.md": (
        "Complete 5-person review (Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate)",
    ),
    "academic-paper/examples/revision_recovery_example.md": (
        "Journal-Fit Reviewer (serialized source ID EIC):",
    ),
    "academic-pipeline/agents/pipeline_orchestrator_agent.md": (
        "Launch Revision Coaching — the Journal-Fit Reviewer follows",
        "These are dedicated contract calls, not dispatches of the first-round `eic_agent` or `editorial_synthesizer_agent` files",
        "the closed rules derive the candidate decision state and `scripts/check_re_review_synthesis.py` recomputes it before surfacing",
    ),
    "academic-pipeline/agents/state_tracker_agent.md": (
        "5 Review Reports (Journal-Fit Reviewer + R1 + R2 + R3 + Devil's Advocate)",
    ),
    "academic-pipeline/examples/full_pipeline_example.md": (
        "Journal-Fit Reviewer (serialized source ID EIC):",
    ),
    "academic-pipeline/examples/integrity_failure_recovery.md": (
        "(Journal-Fit Reviewer + R1 Methodology + R2 Domain + R3 Perspective + Devil's Advocate)",
    ),
    "academic-pipeline/examples/mid_entry_example.md": (
        "full: Complete 4-person review (Journal-Fit Reviewer + 3 Peer Reviewers)",
    ),
    "academic-pipeline/references/reproducibility_audit.md": (
        "Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate — five fixed perspectives",
    ),
    "academic-pipeline/references/two_stage_review_protocol.md": (
        "**Review team**: Journal-Fit Reviewer + R1",
        "The Journal-Fit Reviewer uses Socratic dialogue",
    ),
    "examples/showcase/README.md": (
        "Round 1: Journal-Fit Reviewer + 3 Reviewers + Devil's Advocate",
        "legacy serialized source ID now displayed as **Journal-Fit Reviewer**",
    ),
    "docs/ARCHITECTURE.md": (
        "5 review reports (Journal-Fit Reviewer + R1 methodology + R2 domain + R3 interdisciplinary + Devil's Advocate)",
        "**Contract-governed re-review dispatch**: orchestrating layer + three sequential fenced calls",
    ),
    "docs/PERFORMANCE.md": (
        "Two reviewers (Journal-Fit Reviewer + methodology) each run two phases",
    ),
    "docs/PERFORMANCE.zh-TW.md": (
        "Journal-Fit Reviewer + methodology 兩位 reviewer 各跑兩階段",
    ),
    "shared/model_tiering.md": (
        "Stage 3' uses three dedicated contract judgment calls",
        "They are protocol calls, not agent-manifest identities",
        "Do not reuse Stage 3 `eic` or `editorial_synthesizer` workers for Stage 3'",
    ),
}

DECISION_AUTHORITY_NEEDLES = {
    "Those compatibility tokens do not select a Stage 3' agent file",
    "A genuine SPLIT requires Journal-Fit Reviewer arbitration: the Journal-Fit Reviewer reviews all positions and makes a binding recommendation.",
    "one the Journal-Fit Reviewer adjudicates and rejects",
    "The Journal-Fit Reviewer (or synthesizer) needs to deeply analyze the cause of disagreement",
    "the closed rules derive the candidate decision state and `scripts/check_re_review_synthesis.py` recomputes it before surfacing",
}

INTERNAL_ROSTER_NEEDLES = {
    "Contract-governed default re-review invokes neither `eic_agent` nor `editorial_synthesizer_agent` as an agent-file worker",
}

REVIEW_DISPATCH_NEEDLES = {
    "Three dedicated contract calls owned by the orchestrating layer",
    "orchestrating layer; routed-seat Phase 1/2A calls; Phase 2B integration call",
    "These are dedicated contract calls, not dispatches of the first-round `eic_agent` or `editorial_synthesizer_agent` files",
    "**Contract-governed re-review dispatch**: orchestrating layer + three sequential fenced calls",
    "Stage 3' uses three dedicated contract judgment calls",
    "They are protocol calls, not agent-manifest identities",
    "Do not reuse Stage 3 `eic` or `editorial_synthesizer` workers for Stage 3'",
    "First-round review panel vs. contract-governed re-review dispatch boundary",
    "第一輪審查面板 vs. 契約治理再審派送的分界",
    "第一轮审查面板 vs. 契约治理再审调度的分界",
    "初回レビューパネル vs. 契約管理された再レビューディスパッチの境界",
    "1차 심사 패널 대 계약 기반 re-review 디스패치 경계",
}

FORBIDDEN_REVIEW_DISPATCH = {
    "academic-paper-reviewer/SKILL.md": (
        "+ eic/editorial_synthesizer (integration + Phase 2B + decision derivation",
        "the inherited internal narrow roster `eic_agent` / `editorial_synthesizer_agent`",
    ),
    "academic-paper-reviewer/references/re_review_mode_protocol.md": (
        "The inherited #576 narrow roster remains `eic_agent` plus `editorial_synthesizer_agent`",
    ),
    "docs/ARCHITECTURE.md": (
        "**Narrow re-review team**: eic_agent + editorial_synthesizer_agent",
    ),
    "shared/model_tiering.md": (
        "Stage 3' re-review dispatches the narrow team",
        "the narrow re-review team: `eic`, `editorial_synthesizer`",
    ),
    "README.md": ("First-round review team vs. narrow re-review team boundary",),
    "README.zh-TW.md": ("第一輪審查團隊 vs. 精簡再審團隊的分界",),
    "README.zh-CN.md": ("第一轮审查团队 vs. 精简再审团队的分界",),
    "README.ja-JP.md": ("初回レビューチーム vs. 限定的な再レビューチームの境界",),
    "README.ko-KR.md": ("1차 심사팀 대 좁은 re-review 팀 경계",),
}

# These are display contexts, not a repo-wide ban on EIC. Serialized source IDs,
# `contract_role: eic`, frozen evidence, and real-journal EIC roles remain valid.
FORBIDDEN_DISPLAY = {
    "README.md": ("(EIC + 3 dynamic reviewers",),
    "README.zh-TW.md": ("（主編 +",),
    "README.zh-CN.md": ("（主编 +",),
    "README.ja-JP.md": ("（EIC +",),
    "README.ko-KR.md": ("(EIC +",),
    "academic-paper-reviewer/agents/eic_agent.md": (
        "# EIC Agent",
        'description: "Editor-in-Chief seat;',
        "## EIC Review Report",
    ),
    "academic-paper-reviewer/agents/field_analyst_agent.md": (
        "**EIC Configuration**",
        "[Card #1: EIC]",
    ),
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md": ("EIC verdict",),
    "academic-paper-reviewer/agents/domain_reviewer_agent.md": ("EIC verdict",),
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md": ("EIC verdict",),
    "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md": (
        "The EIC and R1/R2/R3",
        "EIC verdict",
        "EIC's role",
    ),
    "academic-paper-reviewer/agents/editorial_synthesizer_agent.md": (
        "| Dimension | EIC | R1 (Methodology)",
        "### EIC Report Summary",
    ),
    "academic-paper-reviewer/templates/editorial_decision_template.md": (
        "| EIC | [Journal editor identity]",
    ),
    "academic-paper-reviewer/references/guided_mode_protocol.md": ("**EIC opens**",),
    "academic-paper-reviewer/references/top_journals_by_field.md": (
        "calibrating EIC identity",
        "Selecting Journals for EIC",
    ),
    "academic-paper-reviewer/references/editorial_decision_standards.md": (
        "EIC assessment only; advisory",
        "| EIC | R1 | R2 | R3 | -> Recommended Decision |",
        "EIC (or synthesizer) needs to deeply analyze",
    ),
    "academic-paper-reviewer/templates/revision_response_template.md": (
        "## Response to Editor (EIC)",
        "### Editor Comment ",
        "EIC's comment",
        "each EIC comment",
    ),
    "academic-paper-reviewer/examples/hei_paper_review_example.md": (
        "### EIC Review Report",
        "within EIC's core remit",
    ),
    "academic-paper-reviewer/examples/interdisciplinary_review_example.md": (
        "### EIC Review Report",
        "within EIC's core remit",
    ),
    "academic-paper-reviewer/examples/subclaim_decomposition_example.md": (
        "EIC arbitration",
    ),
}


def check(root: Path) -> list[str]:
    errors: list[str] = []
    texts = {rel: read_or_exit2(root, rel) for rel in REQUIRED}
    for rel, needles in REQUIRED.items():
        text = texts[rel]
        for needle in needles:
            if needle not in text:
                kind = (
                    "internal compatibility token"
                    if needle in {"name: eic_agent", "contract_role: eic"}
                    else "internal roster drift"
                    if needle in INTERNAL_ROSTER_NEEDLES
                    else "re-review dispatch drift"
                    if needle in REVIEW_DISPATCH_NEEDLES
                    else "decision-authority drift"
                    if needle in DECISION_AUTHORITY_NEEDLES
                    else "serialized compatibility token"
                    if "[EIC/R1/R2/R3/DA]" in needle
                    or needle
                    == "**Role**: [EIC / Peer Reviewer 1 / Peer Reviewer 2 / Peer Reviewer 3]"
                    else "display-label drift"
                )
                errors.append(f"{rel}: {kind}; missing {needle!r}")
    for rel, needles in FORBIDDEN_DISPLAY.items():
        text = texts[rel]
        for needle in needles:
            if needle in text:
                errors.append(f"{rel}: display-label drift; legacy display {needle!r} remains")
    for rel, needles in FORBIDDEN_REVIEW_DISPATCH.items():
        text = texts[rel]
        for needle in needles:
            if needle in text:
                errors.append(
                    f"{rel}: re-review dispatch drift; fixed-agent roster {needle!r} remains"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = check(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("reviewer role label: Journal-Fit Reviewer public; eic/EIC compatibility frozen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
