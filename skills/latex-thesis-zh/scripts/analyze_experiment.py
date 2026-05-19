#!/usr/bin/env python3
"""
Experiment analysis helper for Chinese LaTeX thesis and journals.

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
        "### 中文实验分析生成请求 (Experiment Analysis Request)",
        "请根据以下原始数据或草稿，生成符合中文顶刊与学位论文标准的完美实验分析段落。",
        "务必严格遵守 `references/modules/EXPERIMENT.md` 中的所有约束条件。",
        "",
        "#### 规范要点提醒:",
        "- 强制使用 `\\paragraph{核心结论概括}` 引导段落。",
        "- 正文中**禁止**任何 `\\textbf{}` 等显式加粗。",
        "- **禁止**使用列表环境 (`\\begin{itemize}`) 罗列数据，需串联成连贯的论述段落。",
        "- 包含 SOTA 对比、消融结论，并确保具有深度的比较逻辑而不仅是报数字。",
        "- 极致客观、去口语化，严禁出现\u201c碾压、遥遥领先\u201d等夸张词汇及主观代词。",
        "",
        "#### 原始数据 / 打点草稿:",
        content,
        "",
        "#### 输出格式:",
        "% EXPERIMENT ANALYSIS DRAFT",
        "% [Insert LaTeX paragraph here]",
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

ATTRIBUTION_MARKERS_ZH = re.compile(
    r"(原因|机制|表明|解释为|归因于|导致|由于|之所以|这是因为|根本原因|"
    r"本质上|究其原因|可能是因为)",
)
DISCUSSION_CATEGORY_MARKERS_ZH = {
    "mechanism": re.compile(r"(原因|机制|解释|归因于|由于|之所以|本质上|究其原因)"),
    "comparison": re.compile(r"(相比|相较于|与.*相比|前人工作|已有研究|基线|文献)"),
    "limitation": re.compile(r"(局限|不足|边界|失效|代价|受限于|仍存在)"),
    "implication": re.compile(r"(启示|应用价值|实际意义|展望|未来工作|后续研究|推广)"),
}

CITE_KEY_RE = re.compile(r"\\(?:cite\w*)\*?(?:\[[^\]]*\]\s*)*\{([^}]*)\}")

CONCLUSION_FINDINGS_ZH = re.compile(
    r"(本文证明了|实验表明|结果表明|本文提出了|研究发现|关键发现|主要结果)",
)
CONCLUSION_IMPLICATIONS_ZH = re.compile(
    r"(启示|应用价值|实际意义|使.*成为可能|推动|促进|有助于|实践意义)",
)
CONCLUSION_LIMITATIONS_ZH = re.compile(
    r"(局限|不足|展望|未来工作|有待|进一步研究|改进方向|后续工作)",
)


def _format_issue(line_no: int, severity: str, priority: str, message: str) -> list[str]:
    return [
        f"% EXPERIMENT (Line {line_no}) [Severity: {severity}] [Priority: {priority}]: {message}"
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
        if ATTRIBUTION_MARKERS_ZH.search(visible):
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
    category_hits = dict.fromkeys(DISCUSSION_CATEGORY_MARKERS_ZH, 0)

    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(parser.get_comment_prefix()):
            continue
        visible = parser.extract_visible_text(raw)
        if not visible:
            continue
        visible_lines.append(visible)
        for name, pattern in DISCUSSION_CATEGORY_MARKERS_ZH.items():
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
                "Discussion may lack layered structure: it should separately cover mechanism, prior-work comparison, limitations/boundaries, or implications/outlook.",
            )
        )
        out.append("")
    return out


def _extract_cite_keys_in_range(lines: list[str], start: int, end: int) -> set[str]:
    """Extract citation keys from lines in range."""
    keys: set[str] = set()
    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1]
        for match in CITE_KEY_RE.finditer(raw):
            for key in match.group(1).split(","):
                k = key.strip()
                if k:
                    keys.add(k)
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

    if not CONCLUSION_LIMITATIONS_ZH.search(section_text):
        out.extend(
            _format_issue(start, "Major", "P1", "Conclusion lacks limitations or future work.")
        )
        out.append("")
    if not CONCLUSION_IMPLICATIONS_ZH.search(section_text):
        out.extend(_format_issue(start, "Minor", "P2", "Conclusion lacks implications statement."))
        out.append("")
    if not CONCLUSION_FINDINGS_ZH.search(section_text):
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
        output.append("% EXPERIMENT: No discussion/conclusion issues detected.")
    return output


def main() -> int:
    cli = argparse.ArgumentParser(
        description="Experiment analysis for Chinese LaTeX thesis (review + prompt generation)"
    )
    cli.add_argument("input", help="File path or raw experiment data")
    cli.add_argument("--section", help="Section name to analyze")
    cli.add_argument(
        "--generate",
        action="store_true",
        help="Generate analysis prompt instead of reviewing",
    )
    args = cli.parse_args()

    path = Path(args.input)
    if args.generate or not path.exists() or path.suffix != ".tex":
        print(generate_request(args.input))
        return 0

    print("\n".join(analyze(path, args.section)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
