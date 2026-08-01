#!/usr/bin/env python3
"""Static sync lint for #611's full and 3-paper directional calibration tiers."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _skill_lint import heading_section, read_or_exit2


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "academic-paper-reviewer/references/calibration_mode_protocol.md"
SKILL = "academic-paper-reviewer/SKILL.md"
RUBRICS = "academic-paper-reviewer/references/quality_rubrics.md"
REGISTRY = "MODE_REGISTRY.md"
SPECTRUM = "shared/mode_spectrum.md"
CROSS_MODEL = "shared/cross_model_verification.md"
CLAUDE = ".claude/CLAUDE.md"

PROTOCOL_WITNESSES = {
    "default-tier contract": (
        "`full` by default",
        "user explicitly selects `directional`",
        "Never auto-select a tier from paper count",
    ),
    "directional shape": (
        "**Directional tier**: exactly 3 papers",
        "**Directional tier:** verify exactly 3 papers",
        "exactly 3 papers × 1 panel = 3 panels total",
        "one run each, not ensembled",
    ),
    "directional gold composition": (
        "one `minor_revision`, one `major_revision`, and one extreme anchor",
        "`borderline` is not allowed in this tier",
    ),
    "gold-label enum": (
        "`accept`, `minor_revision`, `major_revision`, `reject`, or legacy `borderline`",
    ),
    "gold-label isolation": (
        "ground-truth labels, human scores, expected outcomes, "
        "`per_dimension_gold_scores`, and any gold rationale MUST NOT enter any "
        "field-analyst, reviewer, or synthesizer context",
        "Join them to the completed panel outputs only after the final verdict is frozen",
    ),
    "directional reporting boundary": (
        "directional tier **MUST NOT report** balanced accuracy, FNR, FPR, AUC",
        "bootstrap confidence intervals",
        "ensemble stability",
        "per-dimension mean absolute calibration error",
        "Lu numeric comparisons",
        "or any claim that it measured the reviewer's error profile",
        "not an error-rate estimate",
    ),
    "directional raw outputs": (
        "the exact gold label, exact panel verdict, and four raw scoring-seat "
        "weighted averages (Journal-Fit Reviewer, R1, R2, R3)",
        "raw `lenient` / `exact` / `harsh` counts",
        "raw `low` / `med` / `high` severity-miscalibration-risk counts",
    ),
    "directional score provenance": (
        "four standard-format scoring-seat `Weighted Average` values exactly as "
        "emitted: Journal-Fit Reviewer, R1, R2, and R3",
        "The Devil's Advocate's dedicated standard-mode format emits no 0-100 "
        "rubric score",
        "Do not average, median, select, or otherwise collapse those four values "
        "into a singular panel score, and do not mint a score for the Devil's Advocate.",
    ),
    "Minor/Major boundary matrix": (
        "| Minor Revision | stayed minor-side | harsh crossing |",
        "| Major Revision | lenient crossing | stayed major-side |",
        "NOT ESTIMABLE — gold set lacks both sides of the Minor/Major boundary",
    ),
    "full-tier contract": (
        "**Full tier**: 5-20 papers",
        "Select `runs_per_paper` from `{3, 5}` (default 5",
        "reduce `runs_per_paper` to 3",
        "do not allow 1 or 2 in the full tier",
    ),
    "full-tier metrics": (
        "| Balanced accuracy | (TPR + TNR) / 2 | 95% CI via bootstrap (1000 resamples) |",
        "| FNR (over-harsh) |",
        "| FPR (lenient) |",
        "| AUC |",
        "95% CI via bootstrap (1000 resamples)",
    ),
    "panel-engine invariant": (
        "same existing calibration-mode panel engine, reviewer prompts, and five-seat/synthesizer semantics",
        "changes only paper-count validation, replicate count, and reporting",
        "does not opt calibration into the v3.6.2 sprint contract",
    ),
    "cross-model substrate": (
        "apply the calibration-specific non-sprint Reviewer 2 transport in **every panel**",
        "lock one `substrate_plan` without consulting gold material",
        "identical for every paper and every replicate in either tier",
        "varying substrate by gold label or run would confound calibration",
        "mid-attempt cross-model failure invalidates the whole attempt",
        "restarts from paper 1 / replicate 1",
    ),
    "full-tier replicate disclosure": (
        "Runs per paper: <3|5> (ensembled)",
    ),
    "dimension-gold honesty": (
        "Optional per paper: `per_dimension_gold_scores`, an adjudicated 0-100 gold score",
        "`N` is the number of gold papers",
        "Compute each dimension's error only over its `annotated_n` papers",
        "Without this mapping, per-dimension calibration error is `NOT COMPUTABLE`",
        "Every reported dimension error must include `annotated_n=<n>/<N>` and `missing=<N-n>`",
        "Never present a subset-derived `±X` as a gold-set-wide estimate",
        "no ±X claim is available",
    ),
    "FNR/FPR interpretation": (
        "FNR is the over-harsh error rate",
        "FPR is the lenient error rate",
        "Never describe FNR as missed rejects or FPR as over-rejection",
    ),
    "tier disclosures": (
        "Reviewer Confidence Disclosure (from calibration session <id>)",
        "Directional Reviewer Calibration Disclosure (session <id>)",
        "A later full-tier report replaces the directional disclosure",
    ),
}

SKILL_WITNESSES = (
    "3-paper directional tier or the 5-20-paper full tier",
    "Explicit `directional`: 3 gold papers × 1 full panel",
    '"Run directional calibration on these 3 papers" -> calibration (directional tier)',
    "Calibration is the explicit exception: it uses the canonical "
    "calibration-specific non-sprint, single-call Reviewer 2 transport and "
    "attempt-atomic substrate plan",
)

CROSS_MODEL_WITNESSES = {
    "calibration transport": (
        "This branch applies only to the opt-in `reviewer_calibration` mode",
        "For each calibration panel, the Reviewer 2 substrate swap is exactly one "
        "stateless provider call",
        "byte-for-byte",
        "the same `domain_reviewer_agent` system persona",
        "Reviewer Configuration Card #3",
        "`<paper_content>...</paper_content>` data fence",
        "MUST NOT send a sprint contract, a paper-blind Phase 1 request, "
        "`<phase1_output>`, any gold label, human score, per-dimension gold, "
        "or gold rationale",
        "complete standard-mode Reviewer 2 report plus a substrate-provenance stamp",
    ),
    # Termination criterion: this collision family is exactly the two raw
    # blocks named by the calibration payload and the already-hardened #608
    # own-wrapper predicate. Do not grow a tolerant-parser denylist here; a
    # wider grammar requires the normative paragraph and mutation corpus to
    # move in the same change.
    "calibration delimiter collision": (
        "Calibration data-fence collision preflight (closed)",
        "byte-for-byte inside `<reviewer_configuration>...</reviewer_configuration>`",
        "byte-for-byte inside `<paper_content>...</paper_content>`",
        "case-insensitive predicates `</\\s*reviewer_configuration\\b[^>]*>` "
        "and `</\\s*paper_content\\b[^>]*>`",
        "refuse the entire calibration attempt before transport and send no "
        "provider call containing either payload",
        "MUST NOT escape, strip, rewrite, truncate, switch delimiters, or fall "
        "back to primary routing",
        "a different longer tag such as `</paper_contents>` does not match",
        "closed at exactly these two tag names",
        "Expanding this boundary requires the normative paragraph, lint "
        "witnesses, and mutation tests to change together",
    ),
    "attempt-atomic fallback": (
        "lock one `attempt_id` and one",
        "without consulting any gold material",
        "mark the entire attempt invalid; every completed panel in that attempt "
        "becomes diagnostic-only and MUST NOT enter any aggregate",
        "new `attempt_id`, an empty aggregate, and a restart at paper 1 / "
        "replicate 1",
        "Before a homogeneous attempt finishes, MUST NOT emit full-tier metrics",
        "This attempt-atomic override is calibration-only; ordinary "
        "`reviewer_full` keeps the per-seat disclosed fallback above.",
    ),
}

CLAUDE_WITNESSES = (
    "Calibration is the sole explicit exception and uses the canonical "
    "non-sprint single-call transport",
    "it never borrows the sprint payload or mixes substrates in one scored attempt",
)

RUBRIC_WITNESSES = (
    "calibration mode** full tier",
    "3-paper directional tier",
    "directional evidence, not an error-rate estimate",
)

REGISTRY_WITNESSES = (
    "Explicit 3-paper directional readout or default full Calibration Report",
)

SPECTRUM_WITNESSES = (
    "Explicit 3×1 directional tier or default 5× ensemble (3× override)",
)

EXACT_COUNTS = {
    # Inputs + Phase-0 validation must agree; one surviving copy elsewhere is
    # not enough to hide drift in the active intake clause.
    "one `minor_revision`, one `major_revision`, and one extreme anchor": 2,
}

FULL_REPORT_MARKER = "The **full-tier** output document is structured as:"
DIRECTIONAL_REPORT_MARKER = (
    "The **directional-tier** output is a separate, deliberately non-metric readout:"
)
FULL_DISCLOSURE_MARKER = "A full-tier disclosure appears before the verdict as:"
DIRECTIONAL_DISCLOSURE_MARKER = (
    "A directional result MUST use this different disclosure and must not borrow "
    "the measured-profile wording:"
)
FULL_REPORT_PREAMBLE_WITNESSES = (
    "# Calibration Report for <Reviewer Instance>",
    "Tier: full",
    "Domain: <domain>",
    "Gold set: n=<N> (accept=<a>, minor_revision=<m>, major_revision=<M>, reject=<r>, borderline=<b>)",
    "Runs per paper: <3|5> (ensembled)",
    "Cross-model: <yes/no, model families used>",
)
FULL_REPORT_SECTION_WITNESSES = {
    "## Summary metrics": (
        "- Balanced accuracy: 0.XX [95% CI:",
        "- FNR: 0.XX [95% CI",
        "- FPR: 0.XX [95% CI",
        "- AUC: 0.XX",
        "- Ensemble stability:",
    ),
    "## Comparison to Lu 2026 Table 1 baselines": (
        "NOT DIRECTLY COMPARABLE",
        "| Metric | This reviewer | Lu 2026 Automated Reviewer | Lu 2026 Human |",
    ),
    "## Per-dimension calibration error": (
        "annotated_n, and missing",
        "report `annotated_n=<n>/<N>` and `missing=<N-n>` for every dimension",
        "`annotated_n=0` is `NOT COMPUTABLE",
    ),
    "## Minor/Major boundary sub-matrix": (
        "<the Phase 2.5 raw-count matrix, or NOT ESTIMABLE with the missing-side reason>",
    ),
    "## Severity-miscalibration histogram (#215)": (
        "| Risk | Count | Share |",
        "| low | XX | XX% |",
        "| med | XX | XX% |",
        "| high | XX | XX% |",
    ),
    "## Systematic biases detected": (
        "Any quantified score bias must name one dimension and carry that dimension's coverage",
        "never generalize its observed error to unannotated papers or other dimensions",
    ),
    "## Recommendations for session use": (
        "For each dimension with `annotated_n>0`",
        "For each dimension with `annotated_n=0`",
        "FNR X% means X% of acceptable-side gold papers were judged too harshly",
        "FPR X% means X% of reject-side gold papers were judged too leniently",
    ),
}
DIRECTIONAL_REPORT_PREAMBLE_WITNESSES = (
    "# Directional Calibration Readout for <Reviewer Instance>",
    "Tier: directional",
    "Domain: <domain>",
    "Gold set: n=3 (minor_revision=1, major_revision=1, extreme_anchor=<accept|reject>=1)",
    "Runs per paper: 1 (not ensembled)",
    "Cross-model: <yes/no, model families used>",
)
DIRECTIONAL_REPORT_SECTION_WITNESSES = {
    "## Exact per-paper results": (
        "| Paper | Gold exact verdict | Panel exact verdict | Journal-Fit weighted average | R1 weighted average | R2 weighted average | R3 weighted average | Direction |",
        "| <id> | <Accept/Minor/Major/Reject> | <Accept/Minor/Major/Reject> | <0-100> | <0-100> | <0-100> | <0-100> | <lenient/exact/harsh> |",
    ),
    "## Directional raw counts": (
        "- lenient: <n>",
        "- exact: <n>",
        "- harsh: <n>",
    ),
    "## Minor/Major boundary sub-matrix": (
        "<the Phase 2.5 four raw cells>",
    ),
    "## Severity-miscalibration risk counts (#215)": (
        "| Risk | Raw count |",
        "| low | <n> |",
        "| med | <n> |",
        "| high | <n> |",
    ),
    "## Interpretation boundary": (
        "Directional evidence only: n=3, one run each, not ensembled",
        "not an error-rate estimate and does not measure balanced accuracy, FNR/FPR",
        "AUC, calibration error, or stability",
    ),
}
DIRECTIONAL_METRIC_ATOM = (
    r"(?:95\s*%\s*CI|(?:bootstrap\s+)?confidence\s+intervals?|CI|"
    r"balanced\s+accuracy|FNR|FPR|AUC|(?:ensemble\s+)?stability|"
    r"(?:per-dimension\s+)?(?:mean\s+absolute\s+)?calibration\s+error|"
    r"(?:the\s+)?(?:overall\s+)?error[-\s]+rates?|"
    r"(?:(?:the\s+)?reviewer(?:['’]s)?\s+)?error[-\s]+profiles?|"
    r"Lu\s+numeric\s+comparisons?)"
)
DIRECTIONAL_METRIC_LIST = (
    rf"{DIRECTIONAL_METRIC_ATOM}"
    rf"(?:\s*(?:,|/)\s*{DIRECTIONAL_METRIC_ATOM})*"
    rf"(?:\s*,?\s*(?:and|or)\s+{DIRECTIONAL_METRIC_ATOM})?"
)
DIRECTIONAL_METRIC_NAME = re.compile(
    rf"\b{DIRECTIONAL_METRIC_ATOM}\b", re.IGNORECASE
)
DIRECTIONAL_PURE_NON_MEASUREMENT = re.compile(
    rf"""
    ^\s*(?:[-*+]\s*)?
    (?:
        (?:This\s+readout\s+is\s+not\s+an?\s+error-rate\s+estimate\s+and\s+)?
        (?:do(?:es)?|did|will|must|should)\s+not\s+
        (?:measure|report|compute|estimate)\s+{DIRECTIONAL_METRIC_LIST}
      |
        never\s+(?:measure|report|compute|estimate)\s+
        {DIRECTIONAL_METRIC_LIST}
      |
        {DIRECTIONAL_METRIC_LIST}\s+(?:is|are|was|were)\s+not\s+
        (?:measured|reported|computed|estimated|estimable|computable|available)
        (?:\s+on\s+(?:these\s+)?\d+\s+papers?)?
      |
        {DIRECTIONAL_METRIC_LIST}\s*:\s*
        (?:not\s+(?:measured|reported|computed|estimated|estimable|computable)|unavailable)
      |
        (?:This(?:\s+readout)?|It)\s+is\s+not\s+an?\s+
        error[-\s]+rate\s+estimate
    )\s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)
# A decimal point is data, not a sentence boundary; every other full stop and
# the remaining hard punctuation split clauses as before.
DIRECTIONAL_CLAUSE_BOUNDARY = re.compile(
    r"(?:[;!?]+|(?<!\d)\.|\.(?!\d))"
)
DIRECTIONAL_METRIC_PATTERNS = {
    "plus-minus score error": re.compile(r"±\s*\d"),
}
# Closed Lu rule: inside the two controlled directional fences, require the
# literal author name, one of the comparison cues below, and a later numeric
# payload in the same folded logical clause. A four-digit publication year is
# not a payload, and a bare citation such as "Lu Table 1" has no cue before a
# later value. Do not chase author aliases or comparison synonyms unless the
# normative prohibition itself changes.
DIRECTIONAL_LU_NUMERIC_COMPARISON = re.compile(
    r"\bLu\b.*?(?:\bbaselines?\b|\bAutomated\s+Reviewer\b|\bHuman\b|"
    r"\bcompar(?:e[sd]?|isons?)\b|\breports?\b|\bscores?\b|"
    r"\bvs\b\.?|\bversus\b|[:=]).*?"
    r"(?<![\w.])(?!(?:19|20)\d{2}\b)"
    r"(?:\d+(?:\.\d+)?|\.\d+)\s*%?(?![\w.])",
    re.IGNORECASE,
)


def _fenced_block_after(text: str, marker: str) -> str | None:
    marker_at = text.find(marker)
    if marker_at < 0:
        return None
    content_at = marker_at + len(marker)
    opening = text.find("```", content_at)
    if opening < 0:
        return None
    # A report marker owns only the immediately following fence. Otherwise a
    # deleted template silently borrows the next section's fence and the lint
    # fails open while claiming that the missing contract still exists.
    if text[content_at:opening].strip():
        return None
    closing = text.find("```", opening + 3)
    if closing < 0:
        return None
    return text[opening + 3 : closing]


def _check_report_contract(
    block: str | None,
    label: str,
    preamble_witnesses: tuple[str, ...],
    section_witnesses: dict[str, tuple[str, ...]],
    errors: list[str],
) -> None:
    if block is None:
        return

    # Termination criterion for emitted report structure: the two controlled
    # templates have a closed preamble plus an ordered, exactly-once H2 skeleton;
    # each H2 owns its load-bearing fields. Do not search the whole protocol or
    # grow a prose denylist. Extend this map only when the normative template
    # itself gains or changes an emitted section.
    first_heading = next(iter(section_witnesses))
    first_at = block.find(first_heading)
    preamble = block[:first_at] if first_at >= 0 else block
    for witness in preamble_witnesses:
        if witness not in preamble:
            errors.append(
                f"{PROTOCOL}: {label} contract preamble lost witness {witness!r}"
            )

    positions: list[int] = []
    for heading, witnesses in section_witnesses.items():
        count = sum(line == heading for line in block.splitlines())
        if count != 1:
            errors.append(
                f"{PROTOCOL}: {label} contract section {heading!r} appears "
                f"{count} times (expected 1)"
            )
            continue
        positions.append(block.find(heading))
        section = heading_section(block, heading)
        if section is None:
            errors.append(
                f"{PROTOCOL}: {label} contract section {heading!r} is unreadable"
            )
            continue
        for witness in witnesses:
            if witness not in section:
                errors.append(
                    f"{PROTOCOL}: {label} contract section {heading!r} "
                    f"lost witness {witness!r}"
                )
    if positions != sorted(positions):
        errors.append(f"{PROTOCOL}: {label} contract section order drift")


def _directional_clauses(block: str) -> list[str]:
    """Fold the controlled Markdown blocks into closed logical clauses."""
    # Termination criterion: the protected vocabulary is the normative
    # directional MUST-NOT metric list plus its literal generic error-rate and
    # error-profile claim families. Physical wrapping inside one Markdown
    # paragraph or list item is folded before checking. A controlled template
    # sentence may name one only when the whole sentence matches one of the
    # closed pure non-measurement productions above; adversatives are not
    # boundaries because they could otherwise launder trailing positive text.
    # Blank lines, headings, new list items, table rows, and hard sentence
    # punctuation are the closed boundaries. Do not chase hyphenation, inline
    # emphasis, nested-list variants, values, or synonyms; extend only when the
    # normative metric list or a controlled disclosure form itself changes.
    statements: list[str] = []
    prose: list[str] = []

    def flush_prose() -> None:
        if prose:
            statements.append(" ".join(prose))
            prose.clear()

    for raw_line in block.splitlines():
        line = re.sub(r"^\s*>\s?", "", raw_line).strip()
        if not line:
            flush_prose()
        elif re.match(r"^(?:#{1,6}\s|\|)", line):
            flush_prose()
            statements.append(line)
        elif re.match(r"^[-*+]\s", line):
            flush_prose()
            prose.append(line)
        else:
            prose.append(line)
    flush_prose()

    return [
        clause
        for statement in statements
        for clause in DIRECTIONAL_CLAUSE_BOUNDARY.split(statement)
        if clause.strip()
    ]


def _reports_directional_metric(block: str) -> bool:
    for clause in _directional_clauses(block):
        if DIRECTIONAL_METRIC_NAME.search(
            clause
        ) and not DIRECTIONAL_PURE_NON_MEASUREMENT.fullmatch(clause):
            return True
    return False


def _reports_lu_numeric_comparison(block: str) -> bool:
    for clause in _directional_clauses(block):
        if DIRECTIONAL_PURE_NON_MEASUREMENT.fullmatch(clause):
            continue
        if DIRECTIONAL_LU_NUMERIC_COMPARISON.search(clause):
            return True
    return False


def check(root: Path) -> list[str]:
    protocol = read_or_exit2(root, PROTOCOL)
    skill = read_or_exit2(root, SKILL)
    rubrics = read_or_exit2(root, RUBRICS)
    registry = read_or_exit2(root, REGISTRY)
    spectrum = read_or_exit2(root, SPECTRUM)
    cross_model = read_or_exit2(root, CROSS_MODEL)
    claude = read_or_exit2(root, CLAUDE)
    errors: list[str] = []
    for label, witnesses in PROTOCOL_WITNESSES.items():
        for witness in witnesses:
            if witness not in protocol:
                errors.append(f"{PROTOCOL}: {label} lost witness {witness!r}")
    for witness, expected in EXACT_COUNTS.items():
        actual = protocol.count(witness)
        if actual != expected:
            errors.append(
                f"{PROTOCOL}: directional gold composition witness {witness!r} "
                f"appears {actual} times (expected {expected})"
            )
    for witness in SKILL_WITNESSES:
        if witness not in skill:
            errors.append(f"{SKILL}: SKILL calibration summary lost witness {witness!r}")
    for witness in RUBRIC_WITNESSES:
        if witness not in rubrics:
            errors.append(f"{RUBRICS}: rubric disclosure sync lost witness {witness!r}")
    for witness in REGISTRY_WITNESSES:
        if witness not in registry:
            errors.append(f"{REGISTRY}: mode registry sync lost witness {witness!r}")
    for witness in SPECTRUM_WITNESSES:
        if witness not in spectrum:
            errors.append(f"{SPECTRUM}: mode spectrum sync lost witness {witness!r}")
    for label, witnesses in CROSS_MODEL_WITNESSES.items():
        for witness in witnesses:
            if witness not in cross_model:
                errors.append(f"{CROSS_MODEL}: {label} lost witness {witness!r}")
    for witness in CLAUDE_WITNESSES:
        if witness not in claude:
            errors.append(f"{CLAUDE}: project guidance lost witness {witness!r}")

    full_report = _fenced_block_after(protocol, FULL_REPORT_MARKER)
    directional_report = _fenced_block_after(protocol, DIRECTIONAL_REPORT_MARKER)
    full_disclosure = _fenced_block_after(protocol, FULL_DISCLOSURE_MARKER)
    directional_disclosure = _fenced_block_after(protocol, DIRECTIONAL_DISCLOSURE_MARKER)
    for label, block in (
        ("full report", full_report),
        ("directional output", directional_report),
        ("full disclosure", full_disclosure),
        ("directional disclosure", directional_disclosure),
    ):
        if block is None:
            errors.append(f"{PROTOCOL}: {label} fenced contract missing")

    _check_report_contract(
        full_report,
        "full report",
        FULL_REPORT_PREAMBLE_WITNESSES,
        FULL_REPORT_SECTION_WITNESSES,
        errors,
    )
    _check_report_contract(
        directional_report,
        "directional report",
        DIRECTIONAL_REPORT_PREAMBLE_WITNESSES,
        DIRECTIONAL_REPORT_SECTION_WITNESSES,
        errors,
    )

    for label, block in (
        ("directional output contract", directional_report),
        ("directional disclosure contract", directional_disclosure),
    ):
        if block is None:
            continue
        if _reports_directional_metric(block):
            errors.append(f"{PROTOCOL}: {label} reports forbidden metric")
        if _reports_lu_numeric_comparison(block):
            errors.append(
                f"{PROTOCOL}: {label} reports forbidden Lu numeric comparison"
            )
        for metric, pattern in DIRECTIONAL_METRIC_PATTERNS.items():
            if pattern.search(block):
                errors.append(f"{PROTOCOL}: {label} reports forbidden {metric}")

    # Termination criterion for partial-gold honesty: pin every normative
    # full-tier score-error emission surface (table, quantified bias,
    # recommendation, and session disclosure). Do not grow an open-ended
    # synonym denylist unless a new score-error emission surface is introduced.
    if full_report is not None:
        for witness in (
            "report `annotated_n=<n>/<N>` and `missing=<N-n>` for every dimension",
            "`annotated_n=0` is `NOT COMPUTABLE",
            "by ~8 points vs ground truth (annotated_n=<n>/<N>, missing=<N-n>)",
            "never generalize its observed error to unannotated papers or other dimensions",
            "report only that dimension's observed mean absolute calibration error",
            "`NOT COMPUTABLE (annotated_n=0/<N>, missing=<N>)`",
        ):
            if witness not in full_report:
                errors.append(
                    f"{PROTOCOL}: full report honesty lost coverage witness {witness!r}"
                )
    if full_disclosure is not None:
        for witness in (
            "(annotated_n=<n>/<N>, missing=<N-n>)",
            "`<dimension>: NOT COMPUTABLE (annotated_n=0/<N>, missing=<N>)`",
            "A subset-derived error is not a",
            "gold-set-wide estimate",
        ):
            if witness not in full_disclosure:
                errors.append(
                    f"{PROTOCOL}: full disclosure honesty lost coverage witness {witness!r}"
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
    print("calibration tiers: full metrics + 3x1 directional boundary readout in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
