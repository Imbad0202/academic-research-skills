#!/usr/bin/env python3
"""Pin Schema 13.2 role-scoped reviewer delivery surfaces.

Threat model: accidental well-intentioned drift. Adversarial repository editors
are out of scope because they can edit this lint too. Witnesses are hardcoded
and parent-bound to the sprint-delivered Phase 1/Phase 2 subsections.

Exit 0 pass / 1 drift / 2 missing input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _skill_lint import heading_section, norm_ws, read_or_exit2

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = {
    "shared/contracts/reviewer/full.json": {
        "D1": (["methodology"], "methodology"),
        "D2": (["domain"], "domain"),
        "D3": (["da", "methodology"], "da"),
        "D4": (["perspective"], "perspective"),
        "D5": (["eic"], "eic"),
        "D6": (["eic"], "eic"),
    },
    "shared/contracts/reviewer/methodology_focus.json": {
        "D1": (["methodology"], "methodology"),
        "D2": (["eic"], "eic"),
    },
}
AGENTS = {
    "academic-paper-reviewer/agents/eic_agent.md": "eic",
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md": "methodology",
    "academic-paper-reviewer/agents/domain_reviewer_agent.md": "domain",
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md": "perspective",
    "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md": "da",
}
PROTOCOL = "academic-paper-reviewer/references/sprint_contract_protocol.md"
SYNTH = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
PANEL_CHECKER = "scripts/check_panel_synthesis.py"
PHASE_CHECKER = "scripts/check_phase_conformance.py"
TEMPLATE = "academic-paper-reviewer/templates/peer_review_report_template.md"
SPRINT = "## v3.6.2 Sprint Contract Protocol"
PHASE1 = "### Phase 1 — Paper-content-blind pre-commitment"
PHASE2 = "### Phase 2 — Paper-visible review"
PHASE1_FIELDS = (
    "`dimension_id: <Dn>`",
    "`what_to_look_for: <single-line non-empty text>`",
    "`what_triggers_block: <single-line non-empty text>`",
    "`what_triggers_warn: <single-line non-empty text>`",
    "`what_triggers_fatal: <single-line non-empty text>`",
)
PHASE2_WITNESSES = (
    "`dimension_id: <Dn>` and `rationale: <nonempty explanation>`",
    "score: <block|warn|pass|not_assessed>",
    "abstain_reason: <one line>",
    'trigger: "<verbatim substring of the matching Phase 1 trigger>"',
    "block_class: <fatal|repairable>",
    "Do not emit `## Failure Condition Checks`, `## Editorial Decision`",
)
SCORING_FINDING_WITNESS = (
    "each finding with a Severity has its own `### W<n>: <title>` subsection, "
    "exactly one `**Severity**:` line, and its own `**Evidence Anchor**:` line "
    "when Critical or Major. Findings never share an anchor"
)
SCORING_FIELD_VARIANT_WITNESS = (
    "Finding fields may be unindented or Markdown-list-indented, and may be "
    "separate lines or pipe-delimited on one line. A typed anchor value may "
    "be bare or backtick-wrapped; these presentation variants do not weaken "
    "the one-finding/one-Severity/one-anchor gate"
)
DA_FINDING_WITNESS = (
    "emit exactly one `#### CRITICAL` section and exactly one `#### MAJOR` "
    "section, always present even when empty. Each is a Markdown table whose "
    "header includes exact `#` and `Evidence Anchor` columns; every data row "
    "is outer-pipe-delimited and has exactly the header column count"
)
PATTERNS = (
    "any <priority> dimension scores '<score>'",
    "any dimension with priority=<priority> scores '<score>'",
    "any <priority>-priority dimension scores '<score>'",
    "two or more <priority> dimensions score '<score>' or worse",
    "two or more dimensions with priority=<priority> score '<score>' or worse",
    "every <priority> dimension scores '<score>'",
    "<Dn> scores '<score>'",
    "any <priority> dimension has a fatal block",
    "<Dn> has a fatal block",
    "any dimension scores '<score>' or worse",
    "<Dn> scores '<score>' or worse",
    "every dimension scores '<score>'",
)
# Hardcoded textual witnesses for the executable regex bodies. Identifiers alone
# are insufficient: an editor could preserve ``fatal_priority`` while widening
# or otherwise changing the grammar it executes.
EXECUTABLE_PATTERN_WITNESSES = (
    r'''_SCORE = r"'(?P<score>block|warn|pass)'"''',
    r'r"^any (?:(?P<p1>[a-z]+) dimension|dimension with priority="',
    r'r"(?P<p2>[a-z]+)|(?P<p3>[a-z]+)-priority dimension) scores "',
    r'r"^two or more (?:(?P<p1>[a-z]+) dimensions|dimensions with priority="',
    r'r"(?P<p2>[a-z]+)) score " + _SCORE + r" or worse$"',
    r'r"^every (?P<p1>[a-z]+) dimension scores " + _SCORE + r"$"',
    r'r"^(?P<dim>D\d+) scores " + _SCORE + r"$"',
    r'r"^any (?P<p1>[a-z]+) dimension has a fatal block$"',
    r'r"^(?P<dim>D\d+) has a fatal block$"',
    r'r"^any dimension scores " + _SCORE + r" or worse$"',
    r'r"^(?P<dim>D\d+) scores " + _SCORE + r" or worse$"',
    r'r"^every dimension scores " + _SCORE + r"$"',
)
PHASE_FINDING_REGEX_WITNESSES = (
    r'r"(?:^|\|\s*)\s*(?:[-*]\s*)?\*\*Severity\*\*:\s*"',
    r'r"(?:^|\|\s*)\s*(?:[-*]\s*)?\*\*Evidence Anchor\*\*:\s*"',
    r'_SEVERITY_DECL_RE = re.compile(r"\*\*Severity(?:\*\*)?\s*:")',
    r'_FINDING_H3_RE = re.compile(r"^W[1-9]\d*: \S.*$")',
)


def _read(root: Path, rel: str) -> str:
    return read_or_exit2(root, rel)


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, expected in CONTRACTS.items():
        contract = json.loads(_read(root, rel))
        actual = {
            dim["id"]: (dim.get("eligible_roles"), dim.get("owner_role"))
            for dim in contract["acceptance_dimensions"]
        }
        if actual != expected:
            errors.append(
                f"{rel}: eligibility map drift; expected={expected}, actual={actual}"
            )

    for rel, role in AGENTS.items():
        raw = _read(root, rel)
        sprint = heading_section(raw, SPRINT)
        phase1 = heading_section(sprint, PHASE1) if sprint is not None else None
        phase2 = heading_section(sprint, PHASE2) if sprint is not None else None
        if phase1 is None or phase2 is None:
            errors.append(f"{rel}: delivered Phase 1/Phase 2 subsection missing")
            continue
        phase1_norm, phase2_norm = norm_ws(phase1), norm_ws(phase2)
        scope = (
            "per dimension whose `eligible_roles` includes "
            f"`{role}`; do not plan a score for any other dimension"
        )
        if norm_ws(scope) not in phase1_norm:
            errors.append(f"{rel}: Phase 1 eligible-only scope witness missing")
        for field in PHASE1_FIELDS:
            if norm_ws(field) not in phase1_norm:
                errors.append(f"{rel}: Phase 1 field witness missing: {field}")
        score_scope = (
            "Score only dimensions whose `eligible_roles` includes "
            f"`{role}`; every other dimension must say `score: not_assessed`"
        )
        if norm_ws(score_scope) not in phase2_norm:
            errors.append(f"{rel}: Phase 2 role-scoped score witness missing")
        for witness in PHASE2_WITNESSES:
            if norm_ws(witness) not in phase2_norm:
                errors.append(f"{rel}: Phase 2 grammar witness missing: {witness}")
        finding_witness = (
            DA_FINDING_WITNESS if role == "da" else SCORING_FINDING_WITNESS
        )
        if norm_ws(finding_witness) not in phase2_norm:
            errors.append(f"{rel}: Phase 2 per-finding grammar witness missing")
        if role != "da" and norm_ws(SCORING_FIELD_VARIANT_WITNESS) not in phase2_norm:
            errors.append(f"{rel}: Phase 2 finding-field variant witness missing")

    da = _read(root, "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md")
    if "Score the paper — your job is to challenge, not score." in da:
        errors.append("DA retired no-scoring clause returned")
    if "Score any dimension outside the contract's `eligible_roles` for `da`" not in da:
        errors.append("DA role-scoped Phase Boundary clause missing")

    protocol = heading_section(_read(root, PROTOCOL), "## 9. Recognised expression vocabulary")
    synth = heading_section(_read(root, SYNTH), SPRINT.replace("Protocol", "Synthesizer Protocol"))
    checker = _read(root, PANEL_CHECKER)
    phase_checker = _read(root, PHASE_CHECKER)
    if protocol is None or synth is None:
        errors.append("protocol/synthesizer expression section missing")
    else:
        for pattern in PATTERNS:
            if pattern not in protocol:
                errors.append(f"{PROTOCOL}: expression pattern missing: {pattern}")
            if pattern not in synth:
                errors.append(f"{SYNTH}: expression pattern missing: {pattern}")
    # A third, independent surface witness: pin executable regex source, not
    # merely the stable tuple identifiers surrounding it.
    for token in (
        '"fatal_priority"', '"fatal_dim"', '"any_all"',
        '"dim_threshold"', '"every_all"',
    ):
        if token not in checker:
            errors.append(f"{PANEL_CHECKER}: executable pattern token missing: {token}")
    for witness in EXECUTABLE_PATTERN_WITNESSES:
        if witness not in checker:
            errors.append(
                f"{PANEL_CHECKER}: executable regex witness missing: {witness}"
            )
    for witness in PHASE_FINDING_REGEX_WITNESSES:
        if witness not in phase_checker:
            errors.append(
                f"{PHASE_CHECKER}: finding regex witness missing: {witness}"
            )
    if norm_ws(SCORING_FIELD_VARIANT_WITNESS) not in norm_ws(_read(root, TEMPLATE)):
        errors.append(f"{TEMPLATE}: finding-field variant witness missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("check_role_scoped_contract: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
