#!/usr/bin/env python3
"""
Experiment analysis helper for Typst papers.

Supports two modes:
- Prompt generation: format raw data into LLM prompt (original behavior)
- Review analysis: check discussion depth, literature echo, conclusion completeness
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from parsers import get_parser
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from parsers import get_parser


# ── Prompt generation (original) ───────────────────────────────


def generate_request(input_data: str) -> str:
    path = Path(input_data)
    if path.exists() and path.is_file():
        content = path.read_text(encoding="utf-8", errors="ignore")
    else:
        content = input_data

    prompt = [
        "### Experiment Analysis Request",
        "Please generate a top-tier academic experiment analysis paragraph based on the following data.",
        "Ensure you follow the constraints in `references/modules/EXPERIMENT.md`.",
        "",
        "#### Requirements Reminder:",
        "- Use strong emphasis `**Title Case Heading.**` as the paragraph starter.",
        "- NO `*...*` or `_..._` in the body text.",
        "- NO list formats (`- item`). Use a cohesive narrative.",
        "- Include SOTA comparison, ablation insights, and statistical significance if applicable.",
        "- Objective tone, no exaggerated claims.",
        "",
        "#### Raw Data / Draft:",
        content,
        "",
        "#### Output Format:",
        "// EXPERIMENT ANALYSIS DRAFT",
        "// [Insert Typst paragraph here]",
    ]
    return "\n".join(prompt)


# ── Review analysis (B3, B4, B5) ──────────────────────────────

SECTION_ALIASES = {
    "experiment": "experiment",
    "experiments": "experiment",
    "result": "result",
    "results": "result",
    "discussion": "discussion",
    "conclusion": "conclusion",
}

ATTRIBUTION_MARKERS_EN = re.compile(
    r"\b(because|due to|owing to|as a result of|attributed to|caused by|"
    r"mechanism|explains|explanation|reason|hypothesis|interpret|"
    r"stems from|arises from|driven by|suggests that|indicates that)\b|"
    r"(原因|机制|解释|归因于|由于|之所以|本质上|究其原因)",
    re.IGNORECASE,
)
DISCUSSION_CATEGORY_MARKERS = {
    "mechanism": re.compile(
        r"\b(because|due to|mechanism|explains|reason|stems from|driven by|suggests that)\b|"
        r"(原因|机制|解释|归因于|由于|之所以|本质上|究其原因)",
        re.IGNORECASE,
    ),
    "comparison": re.compile(
        r"\b(compared with|compared to|relative to|unlike|consistent with|prior work|baseline)\b|"
        r"(相比|相较于|与.*相比|前人工作|已有研究|基线|文献)",
        re.IGNORECASE,
    ),
    "limitation": re.compile(
        r"\b(limitation|limitations|boundary|boundaries|fails? when|trade-off|caveat|underperforms)\b|"
        r"(局限|不足|边界|失效|代价|受限于|仍存在)",
        re.IGNORECASE,
    ),
    "implication": re.compile(
        r"\b(implication|practical|application|future work|future direction|suggests broader)\b|"
        r"(启示|应用价值|实际意义|展望|未来工作|后续研究|推广)",
        re.IGNORECASE,
    ),
}

# Typst uses @key for citations
TYPST_CITE_KEY_RE = re.compile(r"@([a-zA-Z0-9_-]+)")

CONCLUSION_FINDINGS_RE = re.compile(
    r"\b(we have shown|we demonstrated|results show|this paper has presented|"
    r"our experiments confirm|we proposed|we have proposed|findings indicate)\b|"
    r"(实验表明|结果表明|研究发现|本文证明了|验证了|主要结果)",
    re.IGNORECASE,
)
CONCLUSION_IMPLICATIONS_RE = re.compile(
    r"\b(implication|suggests that.*practical|enables|opens|paves the way|"
    r"facilitates|contributes to|advance|potential for|applicable to)\b|"
    r"(启示|应用价值|实际意义|推动|促进|有助于|展望)",
    re.IGNORECASE,
)
CONCLUSION_LIMITATIONS_RE = re.compile(
    r"\b(limitation|future work|future direction|remain|challenge|"
    r"could be extended|further research|further investigation|"
    r"not addressed|beyond the scope|caveat)\b|"
    r"(局限|不足|未来工作|后续研究|有待|进一步研究|改进方向)",
    re.IGNORECASE,
)


def _format_issue(line_no: int, severity: str, priority: str, message: str) -> list[str]:
    return [
        f"// EXPERIMENT (Line {line_no}) [Severity: {severity}] [Priority: {priority}]: {message}"
    ]


def _normalize_section(section: str | None) -> str | None:
    if not section:
        return None
    return SECTION_ALIASES.get(section.strip().lower(), section.strip().lower())


def _check_discussion_depth(lines: list[str], start: int, end: int, parser) -> list[str]:
    """B3: Check ratio of explanatory lines in discussion."""
    out: list[str] = []
    total_visible = 0
    attribution_lines = 0

    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(parser.get_comment_prefix()):
            continue
        visible = parser.extract_visible_text(raw)
        if not visible:
            continue
        total_visible += 1
        if ATTRIBUTION_MARKERS_EN.search(visible):
            attribution_lines += 1

    if total_visible >= 5 and attribution_lines / total_visible < 0.15:
        out.extend(
            _format_issue(
                start,
                "Major",
                "P1",
                "Discussion may lack depth: low ratio of explanatory/attribution "
                f"language ({attribution_lines}/{total_visible} lines).",
            )
        )
        out.append("")
    return out


def _check_discussion_structure(lines: list[str], start: int, end: int, parser) -> list[str]:
    """Check whether discussion covers multiple argumentative categories."""
    out: list[str] = []
    visible_lines: list[str] = []
    category_hits = dict.fromkeys(DISCUSSION_CATEGORY_MARKERS, 0)

    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(parser.get_comment_prefix()):
            continue
        visible = parser.extract_visible_text(raw)
        if not visible:
            continue
        visible_lines.append(visible)
        for name, pattern in DISCUSSION_CATEGORY_MARKERS.items():
            if pattern.search(visible):
                category_hits[name] += 1

    if len(visible_lines) < 6:
        return out

    covered_categories = [name for name, count in category_hits.items() if count > 0]
    if len(covered_categories) < 2:
        out.extend(
            _format_issue(
                start,
                "Major",
                "P1",
                "Discussion may lack layered structure: cover at least two categories such as mechanism, prior-work comparison, limitations/boundaries, or implications/outlook.",
            )
        )
        out.append("")
    return out


def _extract_cite_keys_in_range(lines: list[str], start: int, end: int) -> set[str]:
    """Extract Typst citation keys (@key) from lines in range."""
    keys: set[str] = set()
    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1]
        for match in TYPST_CITE_KEY_RE.finditer(raw):
            keys.add(match.group(1))
    return keys


def _check_results_literature_echo(
    lines: list[str],
    sections: dict[str, tuple[int, int]],
) -> list[str]:
    """B4: Check if Related Work citations reappear in Discussion."""
    out: list[str] = []
    if "related" not in sections or "discussion" not in sections:
        return out

    rel_start, rel_end = sections["related"]
    disc_start, disc_end = sections["discussion"]

    related_keys = _extract_cite_keys_in_range(lines, rel_start, rel_end)
    discussion_keys = _extract_cite_keys_in_range(lines, disc_start, disc_end)

    if related_keys and not related_keys & discussion_keys:
        out.extend(
            _format_issue(
                disc_start,
                "Major",
                "P1",
                "No citations from Related Work reappear in Discussion.",
            )
        )
        out.append("")
    return out


def _check_conclusion_completeness(lines: list[str], start: int, end: int, parser) -> list[str]:
    """B5: Conclusion must contain findings + implications + limitations."""
    out: list[str] = []
    section_text = ""
    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(parser.get_comment_prefix()):
            continue
        visible = parser.extract_visible_text(raw)
        if visible:
            section_text += " " + visible

    if not section_text.strip():
        return out

    if not CONCLUSION_LIMITATIONS_RE.search(section_text):
        out.extend(
            _format_issue(start, "Major", "P1", "Conclusion lacks limitations or future work.")
        )
        out.append("")
    if not CONCLUSION_IMPLICATIONS_RE.search(section_text):
        out.extend(_format_issue(start, "Minor", "P2", "Conclusion lacks implications statement."))
        out.append("")
    if not CONCLUSION_FINDINGS_RE.search(section_text):
        out.extend(
            _format_issue(start, "Minor", "P2", "Conclusion lacks explicit core findings summary.")
        )
        out.append("")
    return out


def analyze(file_path: Path, section: str | None = None) -> list[str]:
    """Review-mode analysis for experiment/discussion/conclusion sections."""
    parser = get_parser(file_path)
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")
    sections = parser.split_sections(content)

    normalized = _normalize_section(section)
    output: list[str] = []

    if sections:
        if (not normalized or normalized == "discussion") and "discussion" in sections:
            d_start, d_end = sections["discussion"]
            output.extend(_check_discussion_depth(lines, d_start, d_end, parser))
            output.extend(_check_discussion_structure(lines, d_start, d_end, parser))

        if not normalized:
            output.extend(_check_results_literature_echo(lines, sections))

        if (not normalized or normalized == "conclusion") and "conclusion" in sections:
            c_start, c_end = sections["conclusion"]
            output.extend(_check_conclusion_completeness(lines, c_start, c_end, parser))

    if not output:
        output.append("// EXPERIMENT: No discussion/conclusion issues detected.")
    return output


def main() -> int:
    cli = argparse.ArgumentParser(description="Experiment analysis for Typst files")
    cli.add_argument("input", help="Typst file path or raw data")
    cli.add_argument("--section", help="Section name to analyze")
    cli.add_argument(
        "--generate",
        action="store_true",
        help="Generate analysis prompt instead of reviewing",
    )
    args = cli.parse_args()

    path = Path(args.input)
    if args.generate or not path.exists() or path.suffix != ".typ":
        print(generate_request(args.input))
        return 0

    print("\n".join(analyze(path, args.section)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
