#!/usr/bin/env python3
"""
Logic and methodology analyzer for LaTeX/Typst papers.

Checks: paragraph-level coherence, method justification,
literature review quality (A1/A3), cross-section logic chain (C3).
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from parsers import extract_abstract, get_parser
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from parsers import extract_abstract, get_parser


TRANSITIONS = {
    "addition": {"furthermore", "moreover", "in addition", "additionally"},
    "contrast": {"however", "nevertheless", "in contrast", "conversely"},
    "cause": {"therefore", "consequently", "as a result", "thus"},
}


def _has_transition(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for values in TRANSITIONS.values() for token in values)


def _needs_method_justification(text: str) -> bool:
    lowered = text.lower()
    if "we use" not in lowered and "we adopt" not in lowered:
        return False
    return not any(marker in lowered for marker in ["because", "due to", "to ", "for "])


# ── Literature review quality checks (A1, A3) ──────────────────

AUTHOR_ENUM_EN = re.compile(
    r"^(?:In \d{4}|.*?\(\d{4}\).*?(?:proposed|introduced|presented|developed|designed))",
    re.IGNORECASE,
)

GAP_KEYWORDS_EN = re.compile(
    r"\b(gap|limitation|however.*(?:no|not|few)|remains|lack|overlooked|"
    r"under-explored|open problem|yet to be|inadequate|insufficient)\b",
    re.IGNORECASE,
)


def _check_lit_review_enumeration(lines: list[str], start: int, end: int, parser) -> list[str]:
    """A1: Detect 3+ consecutive author/year enumeration patterns."""
    out: list[str] = []
    consecutive = 0
    streak_start = 0
    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(parser.get_comment_prefix()):
            continue
        visible = parser.extract_visible_text(raw)
        if not visible:
            continue
        if AUTHOR_ENUM_EN.search(visible):
            if consecutive == 0:
                streak_start = line_no
            consecutive += 1
        else:
            if consecutive >= 3:
                out.extend(
                    [
                        f"% LIT-REVIEW (Lines {streak_start}-{line_no - 1}) "
                        "[Severity: Major] [Priority: P1]: "
                        f"Author/year enumeration detected ({consecutive} consecutive entries)",
                        "% Suggested: Reorganize by theme clusters with critical analysis.",
                        "% Rationale: Chronological/author enumeration weakens literature synthesis.",
                        "",
                    ]
                )
            consecutive = 0
    if consecutive >= 3:
        out.extend(
            [
                f"% LIT-REVIEW (Lines {streak_start}-{min(end, len(lines))}) "
                "[Severity: Major] [Priority: P1]: "
                f"Author/year enumeration detected ({consecutive} consecutive entries)",
                "% Suggested: Reorganize by theme clusters with critical analysis.",
                "% Rationale: Chronological/author enumeration weakens literature synthesis.",
                "",
            ]
        )
    return out


def _check_gap_derivation(lines: list[str], start: int, end: int, parser) -> list[str]:
    """A3: Check last 10 lines of Related Work for research gap language."""
    out: list[str] = []
    scan_start = max(start, end - 10)
    found_gap = False
    for line_no in range(scan_start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(parser.get_comment_prefix()):
            continue
        visible = parser.extract_visible_text(raw)
        if visible and GAP_KEYWORDS_EN.search(visible):
            found_gap = True
            break
    if not found_gap:
        out.extend(
            [
                f"% LIT-REVIEW (Lines {scan_start}-{end}) "
                "[Severity: Major] [Priority: P1]: "
                "No research gap derivation found at end of Related Work",
                "% Suggested: Add explicit gap statement connecting literature to your contribution.",
                "% Rationale: Related Work should conclude by identifying gaps that motivate the study.",
                "",
            ]
        )
    return out


# ── Cross-section logic chain closure (C3) ──────────────────────

CONTRIBUTION_KEYWORDS_EN = re.compile(
    r"\b(we propose|we present|we introduce|our contribution|we design|we develop|"
    r"this paper proposes|this work presents|main contributions)\b",
    re.IGNORECASE,
)
ANSWER_KEYWORDS_EN = re.compile(
    r"\b(we have shown|we demonstrated|results show|results demonstrate|"
    r"experiments confirm|we have proposed|this paper has presented|"
    r"our experiments show|findings indicate|we have addressed)\b",
    re.IGNORECASE,
)

INTRO_BACKGROUND_RE = re.compile(
    r"\b(important|growing|widely used|demand|need|application|applications|"
    r"real-world|industry|practical|in recent years|increasingly)\b",
    re.IGNORECASE,
)
INTRO_PROBLEM_RE = re.compile(
    r"\b(problem|challenge|bottleneck|limitation|difficult|difficulty|issue|"
    r"expensive|costly|fails?|cannot|struggle|insufficient|inefficient)\b",
    re.IGNORECASE,
)
INTRO_PRIOR_RE = re.compile(
    r"\b(existing|previous|prior|earlier|current|traditional|state-of-the-art|"
    r"studies|literature|methods|approaches|however|nevertheless|recent work)\b",
    re.IGNORECASE,
)
TRIAD_PROBLEM_RE = re.compile(
    r"\b(problem|challenge|task|goal|objective|bottleneck|limitation|address)\b",
    re.IGNORECASE,
)
TRIAD_METHOD_RE = re.compile(
    r"\b(propose|present|introduce|design|develop|framework|method|approach|"
    r"model|mechanism|pipeline|strategy)\b",
    re.IGNORECASE,
)
TRIAD_RESULT_RE = re.compile(
    r"\b(result|results|improve|improvement|achieve|achieves|outperform|gain|"
    r"accuracy|f1|mae|mse|latency|throughput|benchmark|experiments show)\b",
    re.IGNORECASE,
)
TRIAD_CONTRIBUTION_RE = re.compile(
    r"\b(contribution|contributions|novel|we propose|we present|we introduce|"
    r"main contributions)\b",
    re.IGNORECASE,
)


def _section_visible_lines(
    lines: list[str], bounds: tuple[int, int], parser
) -> list[tuple[int, str]]:
    visible_lines: list[tuple[int, str]] = []
    comment_prefix = parser.get_comment_prefix()
    start, end = bounds
    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(comment_prefix):
            continue
        visible = parser.extract_visible_text(raw)
        if visible:
            visible_lines.append((line_no, visible))
    return visible_lines


def _coverage_map(text: str) -> dict[str, bool]:
    lowered = text.lower()
    return {
        "problem": bool(TRIAD_PROBLEM_RE.search(lowered)),
        "method": bool(TRIAD_METHOD_RE.search(lowered)),
        "result": bool(TRIAD_RESULT_RE.search(lowered) or re.search(r"\d+(?:\.\d+)?%?", lowered)),
        "contribution": bool(TRIAD_CONTRIBUTION_RE.search(lowered)),
    }


def _check_introduction_funnel(
    lines: list[str], sections: dict[str, tuple[int, int]], parser
) -> list[str]:
    """Check whether introduction follows background -> problem -> prior work -> contribution."""
    out: list[str] = []
    if "introduction" not in sections:
        return out

    visible_lines = _section_visible_lines(lines, sections["introduction"], parser)
    if len(visible_lines) < 3:
        return out

    first_background = first_problem = first_prior = first_contribution = None
    for line_no, visible in visible_lines:
        lowered = visible.lower()
        if first_background is None and INTRO_BACKGROUND_RE.search(lowered):
            first_background = line_no
        if first_problem is None and INTRO_PROBLEM_RE.search(lowered):
            first_problem = line_no
        if first_prior is None and (
            INTRO_PRIOR_RE.search(lowered) or "\\cite{" in lines[line_no - 1] or "[" in visible
        ):
            first_prior = line_no
        if first_contribution is None and CONTRIBUTION_KEYWORDS_EN.search(lowered):
            first_contribution = line_no

    if first_contribution is None:
        return out

    if first_problem is None or first_contribution < first_problem:
        out.extend(
            [
                f"% INTRODUCTION (Line {first_contribution}) [Severity: Major] [Priority: P1]: "
                "Introduction may jump from background directly to contribution.",
                "% Suggested: Insert the unresolved technical bottleneck before presenting the method.",
                "% Rationale: Readers need the problem statement before the solution.",
                "",
            ]
        )

    if first_problem is not None and first_prior is None:
        out.extend(
            [
                f"% INTRODUCTION (Line {first_problem}) [Severity: Major] [Priority: P1]: "
                "Introduction states the problem but does not derive it from prior work limitations.",
                "% Suggested: Add a prior-work paragraph explaining what existing methods still fail to solve.",
                "% Rationale: The contribution should be motivated by concrete insufficiencies in the literature.",
                "",
            ]
        )
    elif (
        first_problem is not None
        and first_prior is not None
        and first_contribution is not None
        and first_prior > first_contribution
    ):
        out.extend(
            [
                f"% INTRODUCTION (Line {first_contribution}) [Severity: Major] [Priority: P1]: "
                "Contribution claim appears before prior-work insufficiencies are established.",
                "% Suggested: Reorder the introduction so literature limitations appear before the paper contribution.",
                "% Rationale: This preserves the background -> bottleneck -> prior effort -> contribution funnel.",
                "",
            ]
        )
    return out


def _check_tri_section_alignment(
    content: str, lines: list[str], sections: dict[str, tuple[int, int]], parser
) -> list[str]:
    """Check alignment among abstract, contribution source, and conclusion."""
    out: list[str] = []
    if "introduction" not in sections or "conclusion" not in sections:
        return out

    abstract_text = extract_abstract(content)
    if not abstract_text:
        return out

    intro_text = " ".join(
        text for _, text in _section_visible_lines(lines, sections["introduction"], parser)
    )
    conclusion_text = " ".join(
        text for _, text in _section_visible_lines(lines, sections["conclusion"], parser)
    )
    if not intro_text or not conclusion_text:
        return out

    coverage = {
        "abstract": _coverage_map(abstract_text),
        "contribution_source": _coverage_map(intro_text),
        "conclusion": _coverage_map(conclusion_text),
    }
    required_facets = {
        facet
        for facet in ("problem", "method", "result", "contribution")
        if sum(1 for sec in coverage.values() if sec[facet]) >= 2
    }

    mismatches: list[str] = []
    for section_name, section_coverage in coverage.items():
        missing = sorted(facet for facet in required_facets if not section_coverage[facet])
        if len(missing) >= 2 or (
            section_name in {"abstract", "conclusion"}
            and ("result" in missing or "contribution" in missing)
        ):
            mismatches.append(f"{section_name} missing {', '.join(missing)}")

    if coverage["contribution_source"]["contribution"]:
        if not coverage["abstract"]["contribution"]:
            mismatches.append("abstract missing contribution claim")
        if not coverage["conclusion"]["contribution"]:
            mismatches.append("conclusion missing contribution response")
    if coverage["abstract"]["method"] and not coverage["conclusion"]["result"]:
        mismatches.append("conclusion missing result evidence")

    if mismatches:
        out.extend(
            [
                "% LOGIC [Severity: Major] [Priority: P1]: "
                "Abstract, contribution claims, and conclusion may be misaligned.",
                f"% Observation: {'; '.join(mismatches)}.",
                "% Suggested: Make sure all three sections consistently state the problem, method, key results, and contribution.",
                "% Rationale: These sections should tell the same core story with different emphasis, not diverge.",
                "",
            ]
        )
    return out


def _check_cross_section_closure(
    lines: list[str], sections: dict[str, tuple[int, int]], parser
) -> list[str]:
    """C3: Verify that intro contributions are answered in conclusion."""
    out: list[str] = []
    if "introduction" not in sections or "conclusion" not in sections:
        return out

    intro_start, intro_end = sections["introduction"]
    concl_start, concl_end = sections["conclusion"]

    intro_claims = 0
    for line_no in range(intro_start, min(intro_end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(parser.get_comment_prefix()):
            continue
        visible = parser.extract_visible_text(raw)
        if visible and CONTRIBUTION_KEYWORDS_EN.search(visible):
            intro_claims += 1

    if intro_claims == 0:
        return out

    concl_answers = 0
    for line_no in range(concl_start, min(concl_end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(parser.get_comment_prefix()):
            continue
        visible = parser.extract_visible_text(raw)
        if visible and ANSWER_KEYWORDS_EN.search(visible):
            concl_answers += 1

    if concl_answers == 0:
        out.extend(
            [
                f"% LOGIC (Lines {concl_start}-{concl_end}) "
                "[Severity: Major] [Priority: P1]: "
                "[Script] Cross-section logic chain may be incomplete",
                f"% Observation: {intro_claims} contribution claim(s) in Introduction "
                "but no explicit answer language in Conclusion.",
                "% Suggested: Add statements that explicitly address each contribution.",
                "% Rationale: Conclusion should close the logic chain opened in Introduction.",
                "",
            ]
        )
    return out


def analyze(file_path: Path, section: str | None = None, cross_section: bool = False) -> list[str]:
    parser = get_parser(file_path)
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")
    sections = parser.split_sections(content)

    if section:
        key = section.lower()
        if key not in sections:
            return [f"% ERROR [Severity: Critical] [Priority: P0]: Section not found: {section}"]
        ranges = [sections[key]]
    else:
        ranges = list(sections.values()) if sections else [(1, len(lines))]

    out: list[str] = []
    previous_visible = ""
    for start, end in ranges:
        for line_no in range(start, min(end, len(lines)) + 1):
            raw = lines[line_no - 1].strip()
            if not raw or raw.startswith(parser.get_comment_prefix()):
                continue

            visible = parser.extract_visible_text(raw)
            if not visible:
                continue

            if _needs_method_justification(visible):
                out.extend(
                    [
                        f"% METHODOLOGY (Line {line_no}) [Severity: Major] [Priority: P1]: "
                        "Method choice lacks explicit justification",
                        f"% Current: {visible}",
                        "% Suggested: Add rationale (e.g., efficiency/accuracy/reproducibility reasons).",
                        "% Rationale: Method statements should explain why the approach is selected.",
                        "",
                    ]
                )

            if (
                previous_visible
                and not _has_transition(visible)
                and re.search(
                    r"\b(problem|challenge|noisy|difficult)\b", previous_visible, re.IGNORECASE
                )
                and re.search(r"\b(we propose|we design|our method)\b", visible, re.IGNORECASE)
            ):
                out.extend(
                    [
                        f"% LOGIC (Line {line_no}) [Severity: Major] [Priority: P1]: "
                        "Potential logical jump between problem and solution",
                        f"% Current: {visible}",
                        "% Suggested: Add explicit transition (e.g., Therefore/Thus/To address this).",
                        "% Rationale: Strengthens paragraph-level coherence.",
                        "",
                    ]
                )

            previous_visible = visible

    # ── Section-level checks ───────────────────────────────────
    if sections:
        if not section and "introduction" in sections:
            out.extend(_check_introduction_funnel(lines, sections, parser))

        related_key = "related"
        if related_key in sections:
            r_start, r_end = sections[related_key]
            if not section or section.lower() == related_key:
                out.extend(_check_lit_review_enumeration(lines, r_start, r_end, parser))
                out.extend(_check_gap_derivation(lines, r_start, r_end, parser))

        if cross_section and not section:
            out.extend(_check_cross_section_closure(lines, sections, parser))
        if not section:
            out.extend(_check_tri_section_alignment(content, lines, sections, parser))

    if not out:
        out.append("% LOGIC/METHODOLOGY: No rule-based coherence issues detected.")
    return out


def main() -> int:
    cli = argparse.ArgumentParser(
        description="Logic and methodology analysis for LaTeX/Typst files"
    )
    cli.add_argument("file", type=Path, help="Target .tex/.typ file")
    cli.add_argument("--section", help="Section name to analyze")
    cli.add_argument(
        "--cross-section",
        action="store_true",
        help="Enable cross-section logic chain closure check",
    )
    args = cli.parse_args()

    if not args.file.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        return 1

    print("\n".join(analyze(args.file, args.section, args.cross_section)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
