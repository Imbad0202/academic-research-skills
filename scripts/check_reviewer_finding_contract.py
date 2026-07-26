#!/usr/bin/env python3
"""Reviewer finding-contract lint (#574 behavior batch: A1/A2/A3/B1).

Pins the behavior batch's prompt surfaces so the drift classes it retired
cannot silently return:

- A1 — finding quotas removed + Coverage Receipt: the four scoring agents and
  the peer-review template carry NO `(3-5 items)` / `List 3-5` quotas, carry
  the canonical `## Finding Contract` block verbatim, and carry the Coverage
  Receipt surface (zero findings requires a receipt, not silence).
- A2 — typed evidence anchors: the template owns the six-type anchor
  vocabulary + the Critical/Major MUST-anchor rule; the DA tables carry the
  `Evidence Anchor` column; the skill's Specificity standard is anchor-typed.
- A3 — severity single source + transport: Schema 6 carries the canonical
  enum sentence + the optional `evidence_anchor` / `confidence` /
  `competence_basis` fields; the synthesizer transports (never re-derives)
  severity/confidence with visible fallback tags; the decision standards use
  no parallel severity scale.
- B1 — register/severity separation + no base-rate anchoring: the decision
  standards carry the Decision Symmetry section; the EIC and synthesizer
  carry no acceptance-rate/base-rate anchors.

COMMIT-TIME text pin only (witnesses are hardcoded literals per the repo's
defrift-lock discipline); it does not measure runtime reviewer behavior — that
is the E4 seeded-defect held-out set's job. Companion mutation test:
test_check_reviewer_finding_contract.py.

Threat model: ACCIDENTAL drift by well-intentioned edits — deletions,
rewordings, relocations, renames, and ordinary quota re-spellings. An
adversarial repo editor is explicitly out of scope: anyone who can craft a
pathological decoy in these files can equally edit this lint, so the terminal
defense for that class is human review of lint-file diffs, not ever-deeper
witness scoping.

Usage:
    python scripts/check_reviewer_finding_contract.py
    python scripts/check_reviewer_finding_contract.py --root PATH   (for fixtures)

Exit codes: 0 pass / 1 fail / 2 invocation error (missing file).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _skill_lint import heading_section, norm_ws as _norm, read_or_exit2

REPO_ROOT = Path(__file__).resolve().parents[1]

SCORING_AGENTS = (
    "academic-paper-reviewer/agents/eic_agent.md",
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md",
    "academic-paper-reviewer/agents/domain_reviewer_agent.md",
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md",
)
DA_REL = "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md"
SYNTH_REL = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
TEMPLATE_REL = "academic-paper-reviewer/templates/peer_review_report_template.md"
DECISION_TEMPLATE_REL = "academic-paper-reviewer/templates/editorial_decision_template.md"
STANDARDS_REL = "academic-paper-reviewer/references/editorial_decision_standards.md"
SKILL_REL = "academic-paper-reviewer/SKILL.md"
SCHEMAS_REL = "shared/handoff_schemas.md"
CALIBRATION_REL = "academic-paper-reviewer/references/calibration_mode_protocol.md"
GUIDED_REL = "academic-paper-reviewer/references/guided_mode_protocol.md"
RQT_REL = "academic-paper-reviewer/references/review_quality_thinking.md"
RESPONSE_TEMPLATE_REL = "academic-paper-reviewer/templates/revision_response_template.md"
STATS_REL = "academic-paper-reviewer/references/statistical_reporting_standards.md"
RCF_REL = "academic-paper-reviewer/references/review_criteria_framework.md"
XM_REL = "shared/cross_model_verification.md"
FIELD_ANALYST_REL = "academic-paper-reviewer/agents/field_analyst_agent.md"

# The canonical Finding Contract block — byte-identical across the four scoring
# agents, and located INSIDE the delivered Phase 2 subsection (sprint runs
# inject ONLY that subsection as the system prompt, so a contract placed
# anywhere else is never delivered — codex round-2 P1). The lint OWNS this
# string.
SPRINT_HEADING = "## v3.6.2 Sprint Contract Protocol"
PHASE2_HEADING = "### Phase 2 — Paper-visible review"
FINDING_CONTRACT_HEADING = (
    "**Finding Contract (#574 A1/A2/A3)** — governs every finding you report "
    "in `## Review Body` here, and the standard-mode report (§ Output Format "
    "below) alike:"
)
FINDING_CONTRACT_BODY = (
    "- List every strength and weakness you actually found — no minimum, no "
    "maximum. Do not manufacture findings to fill a quota; do not omit real "
    "ones to seem agreeable.\n"
    "- Every strength carries a typed Evidence Anchor too (the same six-type "
    "vocabulary; a section-level locator suffices for a strength, and a "
    "`text` anchor still carries its short verbatim quote — the Schema 6 "
    "conditional member applies to both polarities) — A2's every-finding "
    "rule covers strengths and weaknesses alike.\n"
    "- If either list is empty, you MUST emit a `### Coverage Receipt` "
    "section: state which polarity it covers (Strengths / Weaknesses / "
    "both), then one row per review dimension you examined (your Detailed "
    "Comments sub-sections in standard mode; the contract's "
    "`acceptance_dimensions` under a sprint contract), with what you checked "
    "and the basis for finding nothing of that polarity. An empty finding "
    "list without its receipt is invalid.\n"
    "- Every weakness carries three fields "
    "(`templates/peer_review_report_template.md` § Evidence Anchor Types + "
    "§ Severity Levels):\n"
    "  - **Severity**: Critical / Major / Minor — the Schema 6 enum, set by "
    "decision impact alone; register never lowers it, rigor-signaling never "
    "raises it (#574 B1).\n"
    "  - **Evidence Anchor**: one typed anchor (`text` / `table` / `figure` "
    "/ `equation` / `dataset` / `absence`). REQUIRED with an adequate, "
    "applicable type for Critical/Major; an `absence` anchor names the "
    "surfaces you checked.\n"
    "  - **Confidence**: 1-5 plus a one-phrase competence basis."
)

# The DA's delivered Phase 2 contract — pinned verbatim (round-7 P1).
DA_FINDING_CONTRACT = (
    "**Finding Contract (#574 A2/A3)** — governs every issue you report in "
    "`## Review Body` here, and the standard-mode Issue List (§ Output Format "
    "below) alike: every issue carries a typed evidence anchor (`text` / "
    "`table` / `figure` / `equation` / `dataset` / `absence`; CRITICAL/MAJOR "
    "require an adequate, applicable one, and an `absence` anchor names the "
    "surfaces you checked), every issue carries a Confidence (1-5 "
    "plus a one-phrase competence basis), and severity is assigned by "
    "decision impact alone — adversarial register never inflates a band, and "
    "the same defect class with the same decision impact lands in the same "
    "band on every seat (#574 B1)."
)

BAND_ANCHORS = (
    "- **Band anchors (per finding, never distributional targets):** Critical "
    "means this single defect, uncorrected, invalidates the core claim or makes "
    "acceptance impossible; it alone would justify `block` on a mandatory "
    "dimension. Major materially weakens a core claim and requires substantial "
    "re-analysis, rewriting, or new data, while the core survives. Minor "
    "improves quality or clarity without changing core claims.\n"
    "- **Anti-bundling:** assign each finding the band justified by its own "
    "decision impact; it never inherits a cluster or narrative's band. Joint "
    "impact belongs in the dimension score and synthesis.\n"
    "- **Singleton-Critical:** if a defect needs sibling findings to reach "
    "rejection-level impact, it is not Critical alone. These tests "
    "operationalize severity-by-decision-impact and never prescribe expected "
    "band frequencies."
)
TEMPLATE_BAND_WITNESS = (
    "Apply the test to each finding independently, never to its surrounding "
    "narrative or defect cluster. A finding never inherits a higher band from "
    "siblings; joint impact belongs in the dimension score and synthesis. If "
    "a defect needs siblings to reach rejection-level impact, it is not "
    "Critical alone. These are per-finding decision-impact tests, never "
    "distributional targets: there is no expected frequency for any band."
)

# The per-weakness field line in the four agents' output skeletons.
WEAKNESS_FIELD_LINE = (
    "- **Severity**: [Critical / Major / Minor] | **Evidence Anchor**: "
    "[`<type>: <locator>`] | **Confidence**: [1-5 — competence basis]"
)

COVERAGE_RECEIPT_SKELETON = (
    "### Coverage Receipt (only when Strengths or Weaknesses is empty)"
)
COVERAGE_RECEIPT_COVERS = "**Covers**: [Strengths / Weaknesses / both]"

# Quota regressions (A1). Beyond the retired literals, these patterns catch the
# fail-open class codex round 1 demonstrated: any numeric floor/range attached
# to the finding nouns ("include at least 3 weaknesses", "3–5 strengths",
# "between three and five weaknesses"). The noun set is deliberately findings-
# only — counts on questions, words, or scale anchors (1-5, 0-100, 150-250
# words, 2-4 questions) are not finding quotas and must not false-fire.
_QUOTA_NOUNS = r"(?:strengths|weaknesses|findings|issues)"
_QUOTA_NUMS = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
# Up to two ordinary modifiers may sit between the count and the finding noun
# ("3 major issues", "five high-priority findings"). 'points' is deliberately
# NOT a finding noun — "Award at most 5 points" is scoring language, not a
# quota; only the retired "Still find 2-3 points" literal is pinned.
_QUOTA_GAP = r"(?:[\w-]+\s+){0,2}"
QUOTA_PATTERNS = (
    # Bound to the finding nouns: a "(2-4 items)" count on a NON-finding
    # section (Questions) is legitimately exempt and must not false-fire.
    re.compile(rf"{_QUOTA_NOUNS}\s*\(\s*\d+\s*[-–]\s*\d+\s+items\s*\)", re.I),
    # Ranges with a non-zero floor ("3-5 weaknesses", "three to five
    # weaknesses"). A 0-N range ("0-3 issues", the E7 blocker cap) allows zero
    # and is not a quota. Acknowledged precision-over-recall tradeoff: these
    # fire ANYWHERE in the five scanned prompt surfaces, including would-be
    # descriptive prose ("select 1-3 major issues" in a survey example) — on
    # curated reviewer-prompt files a numeric range on a finding noun is
    # near-always a quota, and a rare false fire is a visible CI failure
    # resolved by rewording, which beats a silent quota regression.
    re.compile(rf"\b[1-9]\d*\s*[-–—]\s*\d+\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    re.compile(
        rf"\b(?:[1-9]\d*|one|two|three|four|five|six|seven|eight|nine|ten)"
        rf"\s+to\s+{_QUOTA_NUMS}\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    re.compile(rf"\bat (?:least|minimum|most)\s+{_QUOTA_NUMS}\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    # Imperative direct counts ("List 3 weaknesses", "Identify 3 major
    # issues") and maximums ("no more than 5 findings") — both contradict the
    # no-minimum/no-maximum contract.
    re.compile(rf"\b(?:list|find|include|provide|identify|give|report|produce|select|choose|pick|name)\s+"
               rf"(?:exactly\s+)?{_QUOTA_NUMS}\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    re.compile(rf"\b(?:no more than|a maximum(?: of)?|maximum of|up to)\s+{_QUOTA_NUMS}\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    # Limit/cap constructions ("Limit findings to five", "Cap weaknesses at 5").
    re.compile(rf"\blimit\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\s+to\s+{_QUOTA_NUMS}\b", re.I),
    re.compile(rf"\bcap\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\s+at\s+{_QUOTA_NUMS}\b", re.I),
    re.compile(rf"\b(?:a\s+)?minimum of\s+{_QUOTA_NUMS}\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    re.compile(rf"\b(?:no|not) fewer than\s+{_QUOTA_NUMS}\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    re.compile(rf"\b{_QUOTA_NUMS}\s+or more\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    re.compile(rf"\b[1-9]\d*\+\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    re.compile(rf"\bexactly\s+{_QUOTA_NUMS}\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    # Top-N forms ("Report the top 3 weaknesses", "the 3 most serious
    # weaknesses") — a fixed selection count is a quota (round-10 P2).
    re.compile(rf"\b(?:the\s+)?top\s+{_QUOTA_NUMS}\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    re.compile(rf"\bthe\s+{_QUOTA_NUMS}\s+most\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    # Both endpoints must be numeric — "between major and minor issues" is
    # ordinary prose, not a quota.
    re.compile(rf"\bbetween\s+{_QUOTA_NUMS}\s+and\s+{_QUOTA_NUMS}\s+{_QUOTA_GAP}{_QUOTA_NOUNS}\b", re.I),
    # Noun-first heading forms: "Weaknesses (at least 3)", "Strengths (3+)",
    # "Weaknesses (minimum 3)", "Strengths (3-5)". Floor must be non-zero — a
    # 0-N cap ("Issues (0-3, ranked)") allows zero and is not a quota.
    re.compile(
        rf"{_QUOTA_NOUNS}\s*\(\s*(?:at least |at minimum |a )?"
        rf"(?:minimum(?: of)? |no fewer than |not fewer than )?"
        rf"(?:[1-9]\d*|one|two|three|four|five|six|seven|eight|nine|ten)"
        rf"\s*(?:[-–—]\s*\d+|\+)?\s*[,)]", re.I),
    re.compile(r"\bStill find 2-3 points\b"),
)

ANCHOR_TYPES = ("`text`", "`table`", "`figure`", "`equation`", "`dataset`", "`absence`")

# The same six-type vocabulary, in every spelling the suite carries it — all
# derived from ANCHOR_TYPES so one hardcoded tuple pins every surface:
# Schema 6's machine-facing enum cell (escaped pipes inside a markdown table)…
SCHEMA6_ANCHOR_ENUM = " \\| ".join(f'"{t.strip("`")}"' for t in ANCHOR_TYPES)
# …and the inline prose list (Finding Contract blocks, DA footnote + discipline).
ANCHOR_LIST_INLINE = " / ".join(ANCHOR_TYPES)


def _read(root: Path, rel: str) -> str:
    return read_or_exit2(root, rel)


def _require(errors: list[str], haystack_norm: str, rel: str, witness: str, label: str) -> None:
    if _norm(witness) not in haystack_norm:
        errors.append(f"{rel}: {label} witness missing: {witness[:70]!r}...")


def check(root: Path) -> list[str]:
    errors: list[str] = []

    # --- A1 + A2 + A3: the four scoring agents -------------------------------
    for rel in SCORING_AGENTS:
        raw = _read(root, rel)
        norm = _norm(raw)

        n = norm.count(_norm(FINDING_CONTRACT_HEADING))
        if n != 1:
            errors.append(f"{rel}: expected exactly one Finding Contract heading, found {n}")
        if _norm(FINDING_CONTRACT_BODY) not in norm:
            errors.append(
                f"{rel}: Finding Contract body missing or does not match the "
                f"canonical verbatim block"
            )
        # Delivery scoping: sprint runs inject ONLY the Phase 2 subsection as
        # the system prompt, so the contract must live INSIDE it (parent-bound
        # — a decoy heading elsewhere is not the injected block).
        sprint = heading_section(raw, SPRINT_HEADING)
        phase2 = heading_section(sprint, PHASE2_HEADING) if sprint is not None else None
        if phase2 is None:
            errors.append(f"{rel}: missing '{PHASE2_HEADING}' under '{SPRINT_HEADING}'")
        elif _norm(FINDING_CONTRACT_HEADING) not in _norm(phase2) \
                or _norm(FINDING_CONTRACT_BODY) not in _norm(phase2):
            errors.append(
                f"{rel}: Finding Contract sits OUTSIDE the delivered Phase 2 "
                f"subsection — sprint-mode calls would never receive the "
                f"A1/A2/A3 rules"
            )
        if phase2 is not None and _norm(BAND_ANCHORS) not in _norm(phase2):
            errors.append(
                f"{rel}: B1 band anchors missing from the delivered Phase 2 "
                "Finding Contract"
            )
        _require(errors, norm, rel, WEAKNESS_FIELD_LINE, "per-weakness field line")
        _require(errors, norm, rel, COVERAGE_RECEIPT_SKELETON, "coverage-receipt skeleton")
        _require(errors, norm, rel, COVERAGE_RECEIPT_COVERS, "coverage-receipt Covers line")
        for pat in QUOTA_PATTERNS:
            if pat.search(raw):
                errors.append(f"{rel}: finding-quota regression: pattern {pat.pattern!r} present")
        if rel.endswith("/eic_agent.md"):
            # B1: the EIC seat is the one that carried the acceptance-rate anchor.
            _require(errors, norm, rel, "never from acceptance-rate base rates",
                     "EIC venue-criteria rule (B1)")
            if "acceptance rate ~" in raw:
                errors.append(f"{rel}: acceptance-rate anchor regression")
        if rel.endswith("/domain_reviewer_agent.md"):
            # Ungroundable field norms → canonical Minor, never off-enum
            # 'advisory' (round-2 P1; check_215 pins the rest of Step 5).
            _require(errors, norm, rel,
                     "down-rate the finding's severity to **Minor**",
                     "field-norm enum disposition (A3)")
            if "down-rate the finding to advisory" in raw:
                errors.append(f"{rel}: off-enum severity disposition regression")
        if rel.endswith("/perspective_reviewer_agent.md"):
            # The assumption-audit gate is conditional, never a mini-quota
            # (round-3 P1).
            _require(errors, norm, rel,
                     "do not manufacture one, #574 A1",
                     "conditional assumption-audit gate (A1)")
            if "at least 1 implicit assumption" in raw:
                errors.append(f"{rel}: assumption-audit quota regression")

    # --- A2 + A3: Devil's Advocate tables ------------------------------------
    # Column checks parse the HEADER ROW directly, not the whole subsection —
    # the shared six-type footnote inside a subsection otherwise masks a
    # renamed column (codex round-1 P2).
    da = _read(root, DA_REL)
    da_norm = _norm(da)
    # Scope to the Output Format section first — a correctly-shaped decoy
    # table elsewhere in the file must not satisfy the check (round-3 P2).
    da_output = heading_section(da, "## Output Format")
    if da_output is None:
        errors.append(f"{DA_REL}: missing '## Output Format' section")
        da_output = ""
    required_cols = {"CRITICAL": ("Evidence Anchor", "Confidence"),
                     "MAJOR": ("Evidence Anchor", "Confidence"),
                     "MINOR": ("Evidence Anchor", "Confidence")}
    for severity, cols in required_cols.items():
        sub = re.search(rf"^#### {severity}\n(.*?)(?=^#### |^### |\Z)", da_output, re.M | re.S)
        if sub is None:
            errors.append(f"{DA_REL}: missing '#### {severity}' table")
            continue
        header = re.search(r"^\| # \| Dimension \| Issue Description \|.*$", sub.group(1), re.M)
        if header is None:
            errors.append(f"{DA_REL} {severity} table: missing header row")
            continue
        # Exact cell compare — substring membership lets a renamed superset
        # ("Evidence Anchor Note") pass (codex round-2 P2).
        cells = [c.strip() for c in header.group(0).strip().strip("|").split("|")]
        for column in cols:
            if column not in cells:
                errors.append(f"{DA_REL} {severity} table: missing column {column!r}")
    _require(errors, da_norm, DA_REL,
             "the same defect class with the same decision impact lands in the "
             "same band every time", "band-consistency (A3/B1)")
    _require(errors, da_norm, DA_REL,
             "OBSERVATION is a non-defect channel and never enters `weaknesses[]`",
             "OBSERVATION mapping (A3)")
    _require(errors, da_norm, DA_REL, "**Typed evidence anchors**", "typed-anchor discipline (A2)")
    n_lists = da_norm.count(ANCHOR_LIST_INLINE)
    if n_lists != 3:
        errors.append(
            f"{DA_REL}: six-type anchor vocabulary must appear exactly 3 times "
            f"(Phase 2 contract + table footnote + discipline rule), found {n_lists}"
        )
    # DA CRITICAL band definition must share the canonical decision-impact bar
    # (a fixable acceptance-blocker is Critical on every seat — codex round-1 P1).
    _require(errors, da_norm, DA_REL, "blocks acceptance until fixed",
             "DA CRITICAL decision-impact definition (A3)")
    if "cannot be rescued by revision | Must be reflected" in da_norm:
        errors.append(f"{DA_REL}: CRITICAL band regressed to the unfixable-only definition")
    # Manufactured-balance regression guards (A1/B1).
    _require(errors, da_norm, DA_REL,
             "Skip the affirmation rather than manufacture one",
             "DA genuine-strengths rule (A1/B1)")
    # The concession ladder stays (v3.0 anti-sycophancy), WITH its B1 bridge:
    # pressure-time procedure, never first-pass severity (round-3 adjudication).
    _require(errors, da_norm, DA_REL,
             "a dispositive score-5 rebuttal always prevails regardless of sequence",
             "concession-ladder B1 bridge")
    if "(for fairness)" in da:
        errors.append(f"{DA_REL}: forced-balance regression ('for fairness' affirmation)")
    # DA's contract must also ride the delivered Phase 2 subsection, pinned
    # VERBATIM — a heading-only check lets the modalities weaken while later,
    # undelivered sections still carry the strong rules (round-7 P1).
    da_sprint = heading_section(da, SPRINT_HEADING)
    da_phase2 = heading_section(da_sprint, PHASE2_HEADING) if da_sprint is not None else None
    if da_phase2 is None or _norm(DA_FINDING_CONTRACT) not in _norm(da_phase2):
        errors.append(
            f"{DA_REL}: delivered Finding Contract (#574 A2/A3) missing from the "
            f"Phase 2 subsection or does not match the canonical verbatim block"
        )
    if da_phase2 is not None and _norm(BAND_ANCHORS) not in _norm(da_phase2):
        errors.append(
            f"{DA_REL}: B1 band anchors missing from the delivered Phase 2 "
            "Finding Contract"
        )
    # Ungroundable field norms take a canonical enum disposition, never an
    # off-enum 'advisory' tier (round-2 P1).
    for phrase in ("down-rate to advisory", "down-rates to advisory"):
        if phrase in da:
            errors.append(f"{DA_REL}: off-enum severity disposition regression ({phrase!r})")

    # --- A2: template owns the anchor vocabulary ------------------------------
    tmpl = _read(root, TEMPLATE_REL)
    tmpl_norm = _norm(tmpl)
    _require(errors, tmpl_norm, TEMPLATE_REL, "### Evidence Anchor Types (#574 A2)",
             "anchor vocabulary section")
    _require(
        errors, tmpl_norm, TEMPLATE_REL, TEMPLATE_BAND_WITNESS,
        "expanded B1 per-finding/anti-bundling/singleton-Critical rules",
    )
    for t in ANCHOR_TYPES:
        if not re.search(rf"^\| {re.escape(t)} \|", tmpl, re.M):
            errors.append(f"{TEMPLATE_REL}: anchor vocabulary missing type row {t}")
    _require(errors, tmpl_norm, TEMPLATE_REL,
             "**Critical/Major findings MUST carry an adequate anchor of an "
             "applicable type** (#574 A2)", "MUST-anchor rule")
    _require(errors, tmpl_norm, TEMPLATE_REL, "## Coverage Receipt (conditional *)",
             "coverage-receipt section")
    _require(errors, tmpl_norm, TEMPLATE_REL,
             "An empty finding list without its Coverage Receipt is invalid.",
             "receipt-required rule")
    _require(errors, tmpl_norm, TEMPLATE_REL, COVERAGE_RECEIPT_COVERS,
             "receipt polarity (Covers) line")
    _require(errors, tmpl_norm, TEMPLATE_REL,
             "a one-polarity review mentions only that polarity",
             "polarity-conditional summary requirement (A1)")
    _require(errors, tmpl_norm, TEMPLATE_REL,
             "**Non-finding channel (#574 A2/A3 boundary):**",
             "Minor-Issues channel boundary (A2/A3)")
    _require(errors, tmpl_norm, TEMPLATE_REL,
             "the single source for finding severity across the reviewer stack (#574 A3)",
             "severity single-source note")
    _require(errors, tmpl_norm, TEMPLATE_REL, "Tone is register, not severity (#574 B1)",
             "register-independence line")
    for field in ("**Evidence Anchor**:", "**Severity**:", "**Confidence**:"):
        if field not in tmpl:
            errors.append(f"{TEMPLATE_REL}: weakness entry field missing: {field!r}")
    for pat in QUOTA_PATTERNS:
        if pat.search(tmpl):
            errors.append(f"{TEMPLATE_REL}: finding-quota regression: pattern {pat.pattern!r} present")

    # --- A3: Schema 6 canonical fields ----------------------------------------
    # Scoped to the Schema 6 section — a witness that migrated into a
    # neighbouring schema would leave the ReviewerReport contract incomplete
    # while a file-wide search still passed (round-5 P2).
    schemas_raw = _read(root, SCHEMAS_REL)
    schema6 = heading_section(
        schemas_raw, "## Schema 6: Review Report (academic-paper-reviewer -> pipeline)")
    if schema6 is None:
        errors.append(f"{SCHEMAS_REL}: missing the Schema 6 section heading")
        schema6 = ""
    schemas_norm = _norm(schema6)
    _require(errors, schemas_norm, SCHEMAS_REL,
             "the CANONICAL single source for finding severity across the "
             "reviewer stack (#574 A3)", "Schema 6 canonical-severity sentence")
    # Full row-start witnesses — a bare backticked field name appears in other
    # schemas' prose, so presence-of-name alone cannot pin the row (codex
    # round-1 P1: the confidence row was unpinned).
    for row in ("| `evidence_anchor` | object | *(optional, #574 A2)*",
                "| `confidence` | integer | *(optional, #574 A3)*",
                "| `competence_basis` | string | *(optional, #574 A3)*"):
        _require(errors, schemas_norm, SCHEMAS_REL, row, "Schema 6 weakness field row")
    # The machine-facing anchor_type enum must spell the SAME six values as the
    # template vocabulary — both pinned to the one ANCHOR_TYPES tuple, so the
    # prose layer and the schema layer cannot silently desync.
    _require(errors, schemas_norm, SCHEMAS_REL, SCHEMA6_ANCHOR_ENUM,
             "Schema 6 anchor_type enum (lockstep with ANCHOR_TYPES)")
    # Type-conditional members: a text anchor without its quote or an absence
    # anchor without the checked surfaces must not conform (codex round-1 P2).
    _require(errors, schemas_norm, SCHEMAS_REL,
             'REQUIRED when `anchor_type = "text"`', "Schema 6 conditional quote member")
    _require(errors, schemas_norm, SCHEMAS_REL,
             'REQUIRED when `anchor_type = "absence"`', "Schema 6 conditional absence members")
    # Strength anchors are machine-addressable too (round-4 P2).
    _require(errors, schemas_norm, SCHEMAS_REL,
             "Strength objects `{description: string, evidence_anchor: object}`",
             "Schema 6 structured strengths (A2)")
    # Receipt + report-level confidence survive serialization (rounds 14-15).
    _require(errors, schemas_norm, SCHEMAS_REL,
             "| `coverage_receipt` | object | *(conditional, #574 A1)*",
             "Schema 6 coverage_receipt field (A1)")
    _require(errors, schemas_norm, SCHEMAS_REL,
             "| `reviewer_confidence` | integer | *(optional, #574 A3)*",
             "Schema 6 reviewer_confidence field (A3)")

    # --- A3: synthesizer transports, never re-derives -------------------------
    synth = _read(root, SYNTH_REL)
    synth_norm = _norm(synth)
    _require(errors, synth_norm, SYNTH_REL, "TRANSPORTED, never re-derived (#574 A3)",
             "severity-transport rule")
    _require(errors, synth_norm, SYNTH_REL, "[SEVERITY-SOURCE: letter-fallback]",
             "severity fallback tag")
    _require(errors, synth_norm, SYNTH_REL, "[CONFIDENCE-SOURCE: report-level]",
             "confidence fallback tag")
    if not re.search(r"^\| sub_claim_id \|.*\| severity \| confidence \|", synth, re.M):
        errors.append(f"{SYNTH_REL}: Step 1b inventory header lacks severity+confidence columns")

    # --- B1: no base-rate anchoring, symmetric standards -----------------------
    _require(errors, synth_norm, SYNTH_REL,
             "never a base rate or target distribution (#574 B1)", "B1 accept rule")
    if "Rare — most papers don't pass" in synth:
        errors.append(f"{SYNTH_REL}: base-rate anchor regression ('Rare — most papers…')")
    _require(errors, synth_norm, SYNTH_REL, "**Unresolved-dissent principle**",
             "symmetric unresolved-dissent arbitration rule (B1)")
    if "rather than directly dismissing" in synth:
        errors.append(f"{SYNTH_REL}: asymmetric arbitration regression ('lean toward … rather than directly dismissing')")
    _require(errors, synth_norm, SYNTH_REL,
             "never manufacture praise to soften a Reject (#574 A1/B1)",
             "genuine-merits rule (A1/B1)")
    if "(they always exist)" in synth:
        errors.append(f"{SYNTH_REL}: mandatory-merit regression ('they always exist')")
    # Edge Case 1 must not retain a directional split prior (round-2 P1).
    _require(errors, synth_norm, SYNTH_REL,
             "never from a strictness prior (#574 B1)",
             "divergence-weighting edge case (B1)")
    if "lean toward Major Revision" in synth:
        errors.append(f"{SYNTH_REL}: directional split prior regression ('lean toward Major Revision')")
    # A lone Major recommendation arbitrates before escalating (round-4 P1).
    _require(errors, synth_norm, SYNTH_REL,
             "A lone Major recommendation goes through arbitration FIRST",
             "lone-Major arbitration rule (B1)")
    # Sub-claims inherit the parent's transported severity (round-6 P1).
    _require(errors, synth_norm, SYNTH_REL,
             "All sub-claims decomposed from one parent share the parent's "
             "transported severity", "sub-claim severity inheritance (A3)")
    if "Conditions: Any reviewer recommends Major Revision" in synth:
        errors.append(f"{SYNTH_REL}: unconditional lone-Major escalation regression")

    dt = _read(root, DECISION_TEMPLATE_REL)
    _require(errors, _norm(dt), DECISION_TEMPLATE_REL,
             "unresolved-dissent principle (#574 B1)", "arbitration rationale vocabulary (B1)")
    if "conservative principle" in dt:
        errors.append(f"{DECISION_TEMPLATE_REL}: asymmetric arbitration regression ('conservative principle')")

    std = _read(root, STANDARDS_REL)
    std_norm = _norm(std)
    _require(errors, std_norm, STANDARDS_REL,
             "### Decision Symmetry and Register Independence (#574 B1)", "B1 section")
    for bold in ("**Symmetric evidence standards.**",
                 "**Decisions follow criteria, not distributions.**",
                 "**Register is independent of severity.**"):
        _require(errors, std_norm, STANDARDS_REL, bold, "B1 principle")
    if "< 5% of submissions" in std:
        errors.append(f"{STANDARDS_REL}: base-rate anchor regression ('< 5% of submissions')")
    if "uncommon in practice" in std:
        errors.append(f"{STANDARDS_REL}: qualitative base-rate cue regression ('uncommon in practice')")
    _require(errors, std_norm, STANDARDS_REL,
             "never a frequency expectation (#574 B1: no base-rate anchoring, qualitative or numeric)",
             "frequency-free first-pass acceptance (B1)")
    if "| Serious |" in std or "| Moderate |" in std:
        errors.append(f"{STANDARDS_REL}: parallel severity scale regression (Serious/Moderate)")
    # The Cross-Dimension table is decision-impact-only: it must not grow back a
    # severity-assignment column (a second severity path — codex round-1 P1).
    _require(errors, std_norm, STANDARDS_REL, "### Cross-Dimension Decision Impact",
             "decision-impact table heading (A3)")
    _require(errors, std_norm, STANDARDS_REL, "| Situation | Decision impact |",
             "decision-impact table header (A3)")
    _require(errors, std_norm, STANDARDS_REL, "this table assigns NO severities (#574 A3)",
             "no-severity-assignment note (A3)")
    if "| Situation | Severity" in std:
        errors.append(f"{STANDARDS_REL}: severity-assignment column regression in the cross-dimension table")
    _require(errors, std_norm, STANDARDS_REL,
             "not a policy of rounding splits toward the stricter verdict (#574 B1)",
             "symmetric split-resolution rule (B1)")
    if "Lean toward conservative strategy" in std:
        errors.append(f"{STANDARDS_REL}: asymmetric split-handling regression ('Lean toward conservative strategy')")
    _require(errors, std_norm, STANDARDS_REL, "Affirm genuine merits where they exist",
             "genuine-merits Reject rule (A1/B1)")

    # The calibration leniency prior must stay bridged to B1 (a measurement-
    # reading prior, never a decision rule) so the two cannot be read as
    # contradicting surfaces.
    cal_norm = _norm(_read(root, CALIBRATION_REL))
    _require(errors, cal_norm, CALIBRATION_REL,
             "measurement-reading prior for calibration", "B1 bridge note")
    _require(errors, cal_norm, CALIBRATION_REL,
             "no verdict is shaded stricter on this prior's account", "B1 bridge rule")

    # Mandatory-strength mirrors (round-2 P2): guided mode's opener and the
    # review-quality balance check are genuine-merit-conditional, never quotas.
    guided = _read(root, GUIDED_REL)
    _require(errors, _norm(guided), GUIDED_REL,
             "when they exist — never manufactured praise, #574 A1/B1",
             "guided-mode conditional-strengths opener")
    if "building confidence" in guided:
        errors.append(f"{GUIDED_REL}: mandatory-strength opener regression")
    rqt = _read(root, RQT_REL)
    _require(errors, _norm(rqt), RQT_REL,
             "and manufacture none? (Evidence-driven balance check, #574 A1/B1)",
             "review-quality balance check")
    if "at least one genuine strength" in rqt:
        errors.append(f"{RQT_REL}: minimum-strength check regression")
    _require(errors, _norm(rqt), RQT_REL,
             "never an author-population base rate (#574 B1)",
             "criterion-only generalizability heuristic (B1)")
    if "Most authors overstate" in rqt:
        errors.append(f"{RQT_REL}: author-population base-rate regression")

    # Downstream response template must accept unbounded weakness lists
    # (round-3 P1: a W6 finding must never lose its author response).
    resp = _read(root, RESPONSE_TEMPLATE_REL)
    resp_norm = _norm(resp)
    _require(errors, resp_norm, RESPONSE_TEMPLATE_REL,
             "EVERY additional weakness in the report", "unbounded response skeleton (A1)")
    # EACH mirror (R2 + R3) must carry its own unbounded witness exactly once —
    # a file-wide count would accept a duplicated-R2/deleted-R3 arrangement
    # (round-5 P2).
    # (Plain string slicing, not heading_section: the whole template body is
    # legitimately fenced ```markdown content — the fenced text IS the surface
    # under check here.)
    mirror_witness = "W1..Wn (every emitted weakness, unbounded — #574 A1)"
    for mirror_heading, next_heading in (
        ("## Response to Reviewer 2 (Domain Expert)",
         "## Response to Reviewer 3"),
        ("## Response to Reviewer 3 (Interdisciplinary Perspective)",
         "## Response to Required Revisions"),
    ):
        start = resp.find(mirror_heading)
        if start == -1:
            errors.append(f"{RESPONSE_TEMPLATE_REL}: missing '{mirror_heading}' section")
            continue
        end = resp.find(next_heading, start + len(mirror_heading))
        seg = resp[start:end] if end != -1 else resp[start:]
        n = _norm(seg).count(mirror_witness)
        if n != 1:
            errors.append(
                f"{RESPONSE_TEMPLATE_REL}: '{mirror_heading}' must carry the "
                f"unbounded W1..Wn witness exactly once, found {n}"
            )
    # Reject bounded W-range grammar generally: any separator, multi-digit
    # endpoints, worded ranges ("W1 to W5", "the first five weaknesses").
    if re.search(r"\bW1\s*(?:[-–—…]|\.\.+|\s+to\s+)\s*W?\d+\b", resp):
        errors.append(f"{RESPONSE_TEMPLATE_REL}: bounded W-range mirror regression")
    if re.search(rf"\bthe first\s+{_QUOTA_NUMS}\s+weaknesses\b", resp, re.I):
        errors.append(f"{RESPONSE_TEMPLATE_REL}: bounded first-N mirror regression")
    _require(errors, resp_norm, RESPONSE_TEMPLATE_REL,
             "skip this block rather than invent praise to fill it (#574 A1)",
             "conditional strengths-acknowledged block (A1)")

    # The statistical red-flag HIGH/MEDIUM/LOW labels are triage, never a
    # competing severity vocabulary (round-4 P1).
    stats_norm = _norm(_read(root, STATS_REL))
    _require(errors, stats_norm, STATS_REL,
             "**Triage levels, not finding severities (#574 A3).**",
             "red-flag triage note (A3)")
    _require(errors, stats_norm, STATS_REL,
             "never copied from the triage label", "triage-to-enum rule (A3)")

    # Developmental register never softens the verdict (round-10 P2).
    fa = _read(root, FIELD_ANALYST_REL)
    _require(errors, _norm(fa), FIELD_ANALYST_REL,
             "tone changes wording, never the verdict", "developmental-register rule (B1)")
    if 'rather than strict "accept/reject" judgment' in fa:
        errors.append(f"{FIELD_ANALYST_REL}: register-softens-verdict regression")

    # Remaining affirm-first mirrors are genuine-merit-conditional (round-4 P2).
    rcf_norm = _norm(_read(root, RCF_REL))
    _require(errors, rcf_norm, RCF_REL,
             "Affirm genuine strengths first when they exist",
             "conditional hypercriticism guidance (A1/B1)")

    # The cross-model DA prompt carries no fixed finding count (round-7 P1),
    # and the ACTIVE prompt block passes the same quota grammar as every other
    # prompt surface (round-9 P2: the retired literal alone is not the class).
    xm = _read(root, XM_REL)
    _require(errors, _norm(xm), XM_REL,
             "no fixed count, and do not pad to reach one (#574 A1)",
             "cross-model DA no-quota prompt (A1)")
    if "the 3 most serious weaknesses" in xm:
        errors.append(f"{XM_REL}: cross-model DA fixed-count regression")
    p_start = xm.find("a simplified DA prompt to the cross-model:")
    p_end = xm.find("2. Compare cross-model findings", p_start)
    if p_start == -1 or p_end == -1:
        errors.append(f"{XM_REL}: cross-model DA prompt block not found")
    else:
        for pat in QUOTA_PATTERNS:
            if pat.search(xm[p_start:p_end]):
                errors.append(
                    f"{XM_REL}: finding-quota regression in the cross-model DA "
                    f"prompt: pattern {pat.pattern[:50]!r}..."
                )

    # Transported metadata reaches the emitted decision package on EVERY row
    # (round-7 P1, extended round-8: Confidence + Evidence Anchor columns too,
    # and the template's tables in lockstep).
    n_sev_tables = synth.count(
        "| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |")
    if n_sev_tables != 2:
        errors.append(
            f"{SYNTH_REL}: expected the transported-metadata columns on both "
            f"roadmap tables (Required + Suggested), found {n_sev_tables}"
        )
    for header in (
        "| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source Reviewer | Section | Estimated Effort |",
        "| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source Reviewer | Priority | Section | Expected Improvement |",
    ):
        if header not in dt:
            errors.append(
                f"{DECISION_TEMPLATE_REL}: roadmap table lost its transported-metadata "
                f"columns: {header[:60]!r}..."
            )
    _require(errors, synth_norm, SYNTH_REL,
             "never dies in the Step 1b working inventory (#574 A2/A3)",
             "emitted-package metadata rule (A3)")
    # Machine handoff carries ALL transported fields + fallback provenance,
    # scoped to the Schema 7 section (round-8 P1; round-9 P1: witnessing only
    # severity left evidence_anchor/confidence deletable).
    schema7 = heading_section(
        schemas_raw, "## Schema 7: Revision Roadmap (reviewer -> academic-paper revision)")
    if schema7 is None:
        errors.append(f"{SCHEMAS_REL}: missing the Schema 7 section heading")
    else:
        s7_norm = _norm(schema7)
        # Witnesses cover the transport SEMANTICS, not just row existence — a
        # description rewritten to contradict A2/A3 must fail (round-10 P2).
        for row in ("| `severity` | enum | *(optional, #574 A3)* Transported Schema 6 "
                    "finding severity (`critical`/`major`/`minor`) of the driving sub-claim",
                    "| `severity_source` | string | *(optional, #574 A3)* Fallback "
                    "provenance for `severity` — the verbatim tag",
                    "| `evidence_anchor` | object | *(optional, #574 A2)* The driving "
                    "finding's typed anchor — same shape as the Schema 6 Weakness",
                    "| `confidence` | integer | *(optional, #574 A3)* The driving "
                    "finding's per-finding confidence 1-5",
                    "| `confidence_source` | string | *(optional, #574 A3)* Fallback "
                    "provenance for `confidence` — the verbatim tag",
                    "| `corroborating_sources` | list[object] | *(optional, #574 A2/A3)*",
                    "| `source_kind` | enum | *(optional, #574 A3)*"):
            _require(errors, s7_norm, SCHEMAS_REL, row, "Schema 7 RoadmapItem transported-field row")
        _require(errors, s7_norm, SCHEMAS_REL,
                 "nothing is dropped or merged", "Schema 7 multi-source rule (A2/A3)")
    for rel_, txt in ((SYNTH_REL, synth), (DECISION_TEMPLATE_REL, dt)):
        if "transported from the finding (#574 A2)" not in _norm(txt):
            errors.append(f"{rel_}: Top Blocking Issues anchor cell lost its typed-anchor form (A2)")

    # DA-CRITICAL is adjudicated, never an automatic veto (round-7 P1).
    _require(errors, synth_norm, SYNTH_REL,
             "never an automatic veto (#574 B1)", "DA-CRITICAL adjudication rule (B1)")

    # --- P0-3 residue + A1/A2 skill-level standards ----------------------------
    skill = _read(root, SKILL_REL)
    skill_norm = _norm(skill)
    _require(errors, skill_norm, SKILL_REL,
             "independent overlap in findings is legitimate corroboration",
             "overlap-corroboration standard (P0-3)")
    _require(errors, skill_norm, SKILL_REL,
             "no manufactured balance and no finding quotas (#574 A1/B1)",
             "evidence-driven balance standard")
    _require(errors, skill_norm, SKILL_REL, "**Overlap suppression**",
             "overlap-suppression anti-pattern row (P0-3)")
    _require(errors, skill_norm, SKILL_REL,
             "EIC opens with genuine strengths when they exist",
             "conditional guided-mode summary (A1/B1)")
    # DA-CRITICAL: visible adjudication on both SKILL surfaces, no
    # unconditional veto (round-7 P1).
    n_adjudicated = skill_norm.count("adjudicated visibly")
    if n_adjudicated < 2:
        errors.append(
            f"{SKILL_REL}: DA-CRITICAL adjudication wording missing from the "
            f"Checkpoint Rule and/or the anti-pattern row (found {n_adjudicated})"
        )
    if "Decision cannot be Accept (Checkpoint Rule #4)" in skill \
            or "the Editorial Decision cannot be Accept." in skill:
        errors.append(f"{SKILL_REL}: unconditional DA-CRITICAL veto regression")
    for phrase in ("no duplicate criticisms", "fake diversity"):
        if phrase in skill:
            errors.append(f"{SKILL_REL}: overlap-prohibition regression ({phrase!r})")

    # --- A3: decision template does not re-derive severity ---------------------
    dt_norm = _norm(_read(root, DECISION_TEMPLATE_REL))
    _require(errors, dt_norm, DECISION_TEMPLATE_REL,
             "transported from the reviewer cards (#574 A3)", "roadmap severity-transport note")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT,
                        help="tree root to lint (default: repo root)")
    args = parser.parse_args()

    errors = check(args.root)
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        print(f"\ncheck_reviewer_finding_contract: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print("check_reviewer_finding_contract: OK (A1 quotas/receipt + A2 anchors + "
          "A3 severity transport + B1 symmetry pinned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
