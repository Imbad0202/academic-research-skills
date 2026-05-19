#!/usr/bin/env python3
"""
逻辑与方法论分析器 — 中文学位论文版本

检查：段落级逻辑衔接、标题后导语完整性、方法论论证、
文献综述质量（A1/A3）、跨章节逻辑链闭合（C3）。
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


TRANSITIONS_ZH = {
    "递进": {"此外", "进一步", "更重要的是", "不仅如此", "同时"},
    "转折": {"然而", "但是", "相反", "尽管如此", "不过"},
    "因果": {"因此", "由此可见", "故而", "所以", "从而"},
}


def _has_transition_zh(text: str) -> bool:
    return any(token in text for values in TRANSITIONS_ZH.values() for token in values)


def _needs_method_justification_zh(text: str) -> bool:
    if "本文采用" not in text and "本文使用" not in text and "我们采用" not in text:
        return False
    return not any(m in text for m in ["因为", "由于", "鉴于", "考虑到", "基于", "原因"])


# ── 文献综述质量检查 (A1, A3) ──────────────────────────────────

AUTHOR_ENUM_ZH = re.compile(
    r"^.*?[（(]\d{4}[)）].*?(?:提出|引入|设计|开发|采用|构建|建立)",
)

GAP_KEYWORDS_ZH = re.compile(
    r"(研究空白|不足|然而.*?尚未|仍然.*?(?:挑战|困难)|有待|缺乏|"
    r"尚未解决|亟待|亟需|鲜有研究|未能充分)",
)


def _check_lit_review_enumeration(lines: list[str], start: int, end: int, parser) -> list[str]:
    """A1: 检测3条及以上连续的作者/年份罗列模式。"""
    out: list[str] = []
    consecutive = 0
    streak_start = 0
    comment_prefix = parser.get_comment_prefix()
    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(comment_prefix):
            continue
        visible = parser.extract_visible_text(raw)
        if not visible:
            continue
        if AUTHOR_ENUM_ZH.search(visible):
            if consecutive == 0:
                streak_start = line_no
            consecutive += 1
        else:
            if consecutive >= 3:
                out.extend(
                    [
                        f"% 文献综述（第{streak_start}-{line_no - 1}行）"
                        "[Severity: Major] [Priority: P1]: "
                        f"检测到作者/年份罗列模式（连续{consecutive}条）",
                        "% 建议：按研究主题分组，组内进行批判性对比分析。",
                        "% 理由：按时间或作者罗列文献会削弱文献综述的综合深度。",
                        "",
                    ]
                )
            consecutive = 0
    if consecutive >= 3:
        out.extend(
            [
                f"% 文献综述（第{streak_start}-{min(end, len(lines))}行）"
                "[Severity: Major] [Priority: P1]: "
                f"检测到作者/年份罗列模式（连续{consecutive}条）",
                "% 建议：按研究主题分组，组内进行批判性对比分析。",
                "% 理由：按时间或作者罗列文献会削弱文献综述的综合深度。",
                "",
            ]
        )
    return out


def _check_gap_derivation(lines: list[str], start: int, end: int, parser) -> list[str]:
    """A3: 检查相关工作末尾是否包含研究空白描述。"""
    out: list[str] = []
    scan_start = max(start, end - 10)
    comment_prefix = parser.get_comment_prefix()
    found_gap = False
    for line_no in range(scan_start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(comment_prefix):
            continue
        visible = parser.extract_visible_text(raw)
        if visible and GAP_KEYWORDS_ZH.search(visible):
            found_gap = True
            break
    if not found_gap:
        out.extend(
            [
                f"% 文献综述（第{scan_start}-{end}行）"
                "[Severity: Major] [Priority: P1]: "
                "相关工作末尾未发现研究空白推导",
                "% 建议：添加明确的研究空白陈述，连接文献综述与本文贡献。",
                "% 理由：相关工作应以识别研究空白作为结尾，为本研究提供动机。",
                "",
            ]
        )
    return out


# ── 跨章节逻辑链闭合 (C3) ──────────────────────────────────────

CONTRIBUTION_KEYWORDS_ZH = re.compile(
    r"(本文提出|本文的贡献|本文设计|本文开发|主要贡献|本研究提出|本文构建)",
)
ANSWER_KEYWORDS_ZH = re.compile(
    r"(本文证明了|实验表明|结果表明|本文提出了|验证了|证实了|研究发现)",
)

LEAD_EXEMPT_TITLES_ZH = (
    "摘要",
    "abstract",
    "参考文献",
    "bibliography",
    "致谢",
    "附录",
    "目录",
    "contents",
)
LEAD_STRUCTURAL_COMMANDS = (
    r"\chapter",
    r"\section",
    r"\subsection",
    r"\subsubsection",
    r"\paragraph",
    r"\begin{figure",
    r"\begin{table",
    r"\begin{equation",
    r"\begin{align",
    r"\begin{itemize",
    r"\begin{enumerate",
    r"\item",
)
LEAD_GUIDE_KEYWORDS_ZH = (
    "本章",
    "本节",
    "本部分",
    "本小节",
    "本小章",
    "本段",
    "下面",
    "首先",
    "然后",
    "最后",
    "具体",
    "围绕",
    "从而",
)
INTRO_BACKGROUND_RE_ZH = re.compile(r"(背景|需求|近年来|应用|场景|行业|领域|现实)")
INTRO_PROBLEM_RE_ZH = re.compile(r"(问题|挑战|瓶颈|局限|不足|困难|代价高|尚未解决)")
INTRO_PRIOR_RE_ZH = re.compile(r"(现有|已有|既有|前人|相关工作|文献|已有研究|然而|但是)")
TRIAD_PROBLEM_RE_ZH = re.compile(r"(问题|挑战|任务|目标|瓶颈|局限|研究问题)")
TRIAD_METHOD_RE_ZH = re.compile(r"(提出|设计|构建|方法|框架|模型|机制|策略)")
TRIAD_RESULT_RE_ZH = re.compile(r"(结果表明|实验表明|研究发现|提升|优于|准确率|召回率|性能|基准)")
TRIAD_CONTRIBUTION_RE_ZH = re.compile(r"(贡献|创新点|本文提出|主要贡献|本研究提出|独特之处)")
CHAPTER_BRIDGE_KEYWORDS_ZH = (
    "基于上一章",
    "承接上一章",
    "在上一章基础上",
    "在前文基础上",
    "进一步",
    "针对尚未解决",
    "围绕上述问题",
    "为解决上述问题",
    "延续前文",
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


def _coverage_map_zh(text: str) -> dict[str, bool]:
    return {
        "problem": bool(TRIAD_PROBLEM_RE_ZH.search(text)),
        "method": bool(TRIAD_METHOD_RE_ZH.search(text)),
        "result": bool(TRIAD_RESULT_RE_ZH.search(text) or re.search(r"\d+(?:\.\d+)?%?", text)),
        "contribution": bool(TRIAD_CONTRIBUTION_RE_ZH.search(text)),
    }


def _check_introduction_funnel(
    lines: list[str], sections: dict[str, tuple[int, int]], parser
) -> list[str]:
    out: list[str] = []
    if "introduction" not in sections:
        return out

    visible_lines = _section_visible_lines(lines, sections["introduction"], parser)
    if len(visible_lines) < 3:
        return out

    first_problem = first_prior = first_contribution = None
    for line_no, visible in visible_lines:
        if first_problem is None and INTRO_PROBLEM_RE_ZH.search(visible):
            first_problem = line_no
        if first_prior is None and (
            INTRO_PRIOR_RE_ZH.search(visible) or "\\cite{" in lines[line_no - 1]
        ):
            first_prior = line_no
        if first_contribution is None and CONTRIBUTION_KEYWORDS_ZH.search(visible):
            first_contribution = line_no

    if first_contribution is None:
        return out

    if first_problem is None or first_contribution < first_problem:
        out.extend(
            [
                f"% 绪论结构（第{first_contribution}行）[Severity: Major] [Priority: P1]: "
                "绪论可能从背景直接跳到本文方案，缺少技术瓶颈铺垫",
                "% 建议：先明确主流方法解决不了什么，再提出本文研究问题或方法。",
                "% 理由：绪论应按背景→瓶颈→前人不足→本文工作的漏斗链展开。",
                "",
            ]
        )

    if first_problem is not None and first_prior is None:
        out.extend(
            [
                f"% 绪论结构（第{first_problem}行）[Severity: Major] [Priority: P1]: "
                "绪论提出了问题，但没有从前人工作不足推导该问题",
                "% 建议：补充已有工作的尝试与局限，再落到本文研究动机。",
                "% 理由：只有问题没有前人不足，会让研究动机显得突兀。",
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
                f"% 绪论结构（第{first_contribution}行）[Severity: Major] [Priority: P1]: "
                "本文工作出现在前人不足之前，绪论漏斗链顺序可能错误",
                "% 建议：先交代已有方法的不足，再引出本文方法。",
                "% 理由：研究问题和方法应建立在明确的文献缺口之上。",
                "",
            ]
        )
    return out


def _check_tri_section_alignment(
    content: str, lines: list[str], sections: dict[str, tuple[int, int]], parser
) -> list[str]:
    out: list[str] = []
    if "conclusion" not in sections:
        return out

    abstract_text = extract_abstract(content)
    if not abstract_text:
        return out

    contribution_key = "contribution" if "contribution" in sections else "introduction"
    if contribution_key not in sections:
        return out

    contribution_text = " ".join(
        text for _, text in _section_visible_lines(lines, sections[contribution_key], parser)
    )
    conclusion_text = " ".join(
        text for _, text in _section_visible_lines(lines, sections["conclusion"], parser)
    )
    if not contribution_text or not conclusion_text:
        return out

    coverage = {
        "abstract": _coverage_map_zh(abstract_text),
        "contribution_source": _coverage_map_zh(contribution_text),
        "conclusion": _coverage_map_zh(conclusion_text),
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
            mismatches.append(f"{section_name} 缺少 {', '.join(missing)}")

    if coverage["contribution_source"]["contribution"]:
        if not coverage["abstract"]["contribution"]:
            mismatches.append("abstract 缺少贡献表述")
        if not coverage["conclusion"]["contribution"]:
            mismatches.append("conclusion 缺少贡献回应")
    if coverage["abstract"]["method"] and not coverage["conclusion"]["result"]:
        mismatches.append("conclusion 缺少结果支撑")

    if mismatches:
        out.extend(
            [
                "% 跨章节一致性 [Severity: Major] [Priority: P1]: 摘要、创新点/贡献来源、结论之间可能存在错位",
                f"% 观察：{'；'.join(mismatches)}。",
                "% 建议：三处都要围绕研究问题、方法、核心结果、增量贡献形成对应关系。",
                "% 理由：摘要、创新点与结论应长得像但不应各说各话。",
                "",
            ]
        )
    return out


def _check_chapter_mainline(content: str, lines: list[str], parser) -> list[str]:
    """Check whether major chapters are bridged into one thesis storyline."""
    out: list[str] = []
    headings = [h for h in parser.extract_headings(content) if h["level"] == 1]
    if len(headings) < 3:
        return out

    substantive = [
        h
        for h in headings
        if not _is_exempt_heading(h["title"])
        and "结论" not in h["title"]
        and "总结" not in h["title"]
    ]
    if len(substantive) < 3:
        return out

    missing_bridges: list[str] = []
    for heading in substantive[1:]:
        start_line = heading["line"] + 1
        lead_text = ""
        for line_no in range(start_line, min(start_line + 8, len(lines)) + 1):
            raw = lines[line_no - 1].strip()
            kind = _classify_lead_gap(raw)
            if kind in {"empty", "comment", "structural"}:
                continue
            visible = parser.extract_visible_text(raw)
            if visible:
                lead_text = visible
                break
        if not lead_text:
            continue
        has_bridge = any(keyword in lead_text for keyword in CHAPTER_BRIDGE_KEYWORDS_ZH)
        generic_chapter_open = lead_text.startswith("本章") or lead_text.startswith("本文")
        if not has_bridge and generic_chapter_open:
            missing_bridges.append(f"{heading['title']}（第{heading['line']}行）")

    if len(missing_bridges) >= 2:
        out.extend(
            [
                "% 章节主线 [Severity: Major] [Priority: P1]: 多个核心章节缺少与前章结论的桥接，整体主线可能偏向工作罗列",
                f"% 观察：{', '.join(missing_bridges)} 的开头未明确承接上一章或说明递进关系。",
                "% 建议：在章节引言或本章小结中显式写出“基于上一章……本章进一步……”。",
                "% 理由：学位论文需要体现递进或并列互补的系统性，而不是可任意换序的工作堆砌。",
                "",
            ]
        )
    return out


def _check_cross_section_closure(
    lines: list[str], sections: dict[str, tuple[int, int]], parser
) -> list[str]:
    """C3: 验证绪论中的贡献声明在结论中得到回应。"""
    out: list[str] = []
    if "introduction" not in sections or "conclusion" not in sections:
        return out

    intro_start, intro_end = sections["introduction"]
    concl_start, concl_end = sections["conclusion"]
    comment_prefix = parser.get_comment_prefix()

    intro_claims = 0
    for line_no in range(intro_start, min(intro_end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(comment_prefix):
            continue
        visible = parser.extract_visible_text(raw)
        if visible and CONTRIBUTION_KEYWORDS_ZH.search(visible):
            intro_claims += 1

    if intro_claims == 0:
        return out

    concl_answers = 0
    for line_no in range(concl_start, min(concl_end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(comment_prefix):
            continue
        visible = parser.extract_visible_text(raw)
        if visible and ANSWER_KEYWORDS_ZH.search(visible):
            concl_answers += 1

    if concl_answers == 0:
        out.extend(
            [
                f"% 逻辑衔接（第{concl_start}-{concl_end}行）"
                "[Severity: Major] [Priority: P1]: "
                "[Script] 跨章节逻辑链可能不完整",
                f"% 观察：绪论中有{intro_claims}处贡献声明，但结论中未发现明确回应。",
                "% 建议：在结论中添加明确回应每项贡献的陈述。",
                "% 理由：结论应当闭合绪论中开启的逻辑链。",
                "",
            ]
        )
    return out


def _is_exempt_heading(title: str) -> bool:
    normalized = title.strip().lower()
    return any(token in normalized for token in LEAD_EXEMPT_TITLES_ZH)


def _classify_lead_gap(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return "empty"
    if stripped.startswith("%") or stripped.startswith("//"):
        return "comment"
    if any(stripped.startswith(token) for token in LEAD_STRUCTURAL_COMMANDS):
        return "structural"
    return "text"


def _check_heading_leads(content: str, lines: list[str], parser) -> list[str]:
    """检查标题后是否先给出导语段落，而不是直接跳入结构元素。"""
    out: list[str] = []
    headings = parser.extract_headings(content)
    if not headings:
        return out

    for index, heading in enumerate(headings):
        title = heading["title"]
        if _is_exempt_heading(title):
            continue

        start_line = heading["line"] + 1
        end_line = headings[index + 1]["line"] - 1 if index + 1 < len(headings) else len(lines)
        if start_line > end_line:
            out.extend(
                [
                    f"% 结构衔接（第{heading['line']}行）[Severity: Major] [Priority: P1]: "
                    f"标题“{title}”后未发现导语段落",
                    "% 建议：在标题后先用一段导语交代本层级的研究对象、写作目的和行文安排。",
                    "% 理由：标题后直接结束或切到下一级标题，会导致结构展开过于突兀。",
                    "",
                ]
            )
            continue

        first_text_line = None
        first_structural_line = None
        first_text = ""
        for line_no in range(start_line, min(end_line, len(lines)) + 1):
            raw = lines[line_no - 1].strip()
            kind = _classify_lead_gap(raw)
            if kind in {"empty", "comment"}:
                continue
            if kind == "structural":
                first_structural_line = line_no
                break

            visible = parser.extract_visible_text(raw)
            if visible:
                first_text_line = line_no
                first_text = visible
                break

        if first_text_line is None:
            reason = (
                f"标题后直接进入结构元素（第{first_structural_line}行）"
                if first_structural_line
                else "标题后未发现可见正文"
            )
            out.extend(
                [
                    f"% 结构衔接（第{heading['line']}行）[Severity: Major] [Priority: P1]: "
                    f"标题“{title}”后缺少导语段落",
                    f"% 观察：{reason}。",
                    "% 建议：先补一段完整导语，再进入列表、图表、公式或下一级标题。",
                    "% 理由：章节、小节和四级标题展开时应先说明本段写什么、为何写、如何组织。",
                    "",
                ]
            )
            continue

        is_short = len(first_text) < 18
        has_guide_signal = any(keyword in first_text for keyword in LEAD_GUIDE_KEYWORDS_ZH)
        if heading["level"] <= 4 and is_short and not has_guide_signal:
            out.extend(
                [
                    f"% 结构衔接（第{first_text_line}行）[Severity: Minor] [Priority: P2]: "
                    f"标题“{title}”后的导语可能过短",
                    f"% 原文: {first_text}",
                    "% 建议：扩展为一段完整导语，交代本层级内容范围、与上文关系及展开顺序。",
                    "% 理由：过短句子难以承担章节导入和逻辑承接功能。",
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
            return [f"% ERROR [Severity: Critical] [Priority: P0]: 未找到章节: {section}"]
        ranges = [sections[key]]
    else:
        ranges = list(sections.values()) if sections else [(1, len(lines))]

    out: list[str] = []
    previous_visible = ""
    comment_prefix = parser.get_comment_prefix()
    for start, end in ranges:
        for line_no in range(start, min(end, len(lines)) + 1):
            raw = lines[line_no - 1].strip()
            if not raw or raw.startswith(comment_prefix):
                continue

            visible = parser.extract_visible_text(raw)
            if not visible:
                continue

            if _needs_method_justification_zh(visible):
                out.extend(
                    [
                        f"% 方法论深度（第{line_no}行）[Severity: Major] [Priority: P1]: "
                        "方法选择缺乏论证",
                        f"% 原文: {visible}",
                        "% 建议：添加选择理由（如效率/准确率/可复现性）。",
                        "% 理由：方法选择应说明为何采用该方案。",
                        "",
                    ]
                )

            if (
                previous_visible
                and not _has_transition_zh(visible)
                and any(k in previous_visible for k in ["问题", "挑战", "困难", "噪声"])
                and any(k in visible for k in ["本文提出", "本文设计", "我们的方法"])
            ):
                out.extend(
                    [
                        f"% 逻辑衔接（第{line_no}行）[Severity: Major] [Priority: P1]: "
                        "问题与解决方案间可能存在逻辑跳跃",
                        f"% 原文: {visible}",
                        '% 建议：添加显式过渡（如"因此"、"为解决上述问题"）。',
                        "% 理由：增强段落间的逻辑连贯性。",
                        "",
                    ]
                )

            previous_visible = visible

    # ── 章节级检查 ─────────────────────────────────────────────
    if not section:
        out.extend(_check_heading_leads(content, lines, parser))
        out.extend(_check_chapter_mainline(content, lines, parser))

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
        out.append("% 逻辑/方法论：未检测到规则级逻辑问题。")
    return out


def main() -> int:
    cli = argparse.ArgumentParser(description="中文学位论文逻辑与方法论分析")
    cli.add_argument("file", type=Path, help="目标 .tex/.typ 文件")
    cli.add_argument("--section", help="指定分析章节")
    cli.add_argument(
        "--cross-section",
        action="store_true",
        help="启用跨章节逻辑链闭合检查",
    )
    args = cli.parse_args()

    if not args.file.exists():
        print(f"[错误] 文件未找到: {args.file}", file=sys.stderr)
        return 1

    print("\n".join(analyze(args.file, args.section, args.cross_section)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
