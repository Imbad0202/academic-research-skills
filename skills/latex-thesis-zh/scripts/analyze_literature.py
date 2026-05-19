#!/usr/bin/env python3
"""
文献综述分析器 — 中文学位论文版本

聚焦相关工作/文献综述段：
- A1: 作者年份罗列
- A2: 缺少比较分析
- A3: 缺少研究空白推导
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from parsers import get_parser
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from parsers import get_parser


AUTHOR_ENUM_ZH = re.compile(
    r"^.*?[（(]\d{4}[)）].*?(?:提出|引入|设计|开发|采用|构建|建立)",
)

GAP_KEYWORDS_ZH = re.compile(
    r"(研究空白|不足|然而.*?尚未|仍然.*?(?:挑战|困难)|有待|缺乏|"
    r"尚未解决|亟待|亟需|鲜有研究|未能充分)",
)

COMPARISON_MARKERS_ZH = re.compile(
    r"(然而|但是|相比(?:之下)?|相较于|不同于|共同局限|共同不足|"
    r"对比|差异|优于|弱于|优劣|局限性|共同问题|trade-?off)",
    re.IGNORECASE,
)

SUMMARY_MARKERS_ZH = re.compile(
    r"(总体来看|整体上|综合来看|总体而言|归纳来看|这些工作表明|这类研究表明|共同趋势|总体趋势)",
    re.IGNORECASE,
)


def _visible_lines(lines: list[str], start: int, end: int, parser) -> list[tuple[int, str, str]]:
    visible: list[tuple[int, str, str]] = []
    comment_prefix = parser.get_comment_prefix()
    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(comment_prefix):
            continue
        text = parser.extract_visible_text(raw)
        if text:
            visible.append((line_no, raw, text))
    return visible


def _find_section_bounds(
    sections: dict[str, tuple[int, int]], section: str | None
) -> tuple[int, int] | None:
    if section:
        return sections.get(section.lower())
    for key in ("related", "literature", "related work"):
        if key in sections:
            return sections[key]
    return None


def _paragraphs(
    lines: list[str], start: int, end: int, parser
) -> list[tuple[int, int, list[str], list[str]]]:
    paragraphs: list[tuple[int, int, list[str], list[str]]] = []
    comment_prefix = parser.get_comment_prefix()
    current_texts: list[str] = []
    current_raws: list[str] = []
    para_start: int | None = None
    last_line = start

    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw:
            if current_texts and para_start is not None:
                paragraphs.append((para_start, last_line, current_raws[:], current_texts[:]))
                current_texts.clear()
                current_raws.clear()
                para_start = None
            continue
        if raw.startswith(comment_prefix):
            continue
        text = parser.extract_visible_text(raw)
        if not text:
            continue
        if para_start is None:
            para_start = line_no
        current_raws.append(raw)
        current_texts.append(text)
        last_line = line_no

    if current_texts and para_start is not None:
        paragraphs.append((para_start, last_line, current_raws, current_texts))
    return paragraphs


def _paragraph_a2_status(raws: list[str], texts: list[str]) -> tuple[str, int]:
    joined = "".join(texts)
    cite_hits = sum(
        1
        for raw, text in zip(raws, texts, strict=False)
        if "\\cite{" in raw or AUTHOR_ENUM_ZH.search(text)
    )
    has_comparison = bool(COMPARISON_MARKERS_ZH.search(joined))
    has_summary = bool(SUMMARY_MARKERS_ZH.search(joined))
    has_gap = bool(GAP_KEYWORDS_ZH.search(joined))

    if cite_hits < 2:
        return "pass", 99

    score = 0
    if cite_hits >= 2:
        score -= 2
    if cite_hits >= 3 and not (has_comparison or has_summary):
        score -= 1
    if has_comparison:
        score += 2
    if has_summary:
        score += 1
    if has_gap:
        score += 1

    if score <= -2:
        return "fail", score
    if score >= 1:
        return "pass", score
    return "uncertain", score


def analyze(file_path: Path, section: str | None = None) -> list[str]:
    parser = get_parser(file_path)
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")
    sections = parser.split_sections(content)
    bounds = _find_section_bounds(sections, section)
    comment = parser.get_comment_prefix()

    if bounds is None:
        target = section or "related"
        return [f"{comment} ERROR [Severity: Critical] [Priority: P0]: 未找到章节: {target}"]

    start, end = bounds
    visible = _visible_lines(lines, start, end, parser)
    out: list[str] = []

    consecutive = 0
    streak_start = 0
    for line_no, _raw, text in visible:
        if AUTHOR_ENUM_ZH.search(text):
            if consecutive == 0:
                streak_start = line_no
            consecutive += 1
        else:
            if consecutive >= 3:
                out.extend(
                    [
                        f"{comment} 文献综述（第{streak_start}-{line_no - 1}行）[Severity: Major] [Priority: P1]: "
                        f"检测到作者/年份罗列模式（连续{consecutive}条）",
                        f"{comment} 建议：按研究主题重组文献，并在组内显式比较方法差异与共同局限。",
                        f"{comment} 理由：仅按作者和年份罗列，会削弱文献综述的综合深度。",
                        "",
                    ]
                )
            consecutive = 0
    if consecutive >= 3:
        out.extend(
            [
                f"{comment} 文献综述（第{streak_start}-{visible[-1][0]}行）[Severity: Major] [Priority: P1]: "
                f"检测到作者/年份罗列模式（连续{consecutive}条）",
                f"{comment} 建议：按研究主题重组文献，并在组内显式比较方法差异与共同局限。",
                f"{comment} 理由：仅按作者和年份罗列，会削弱文献综述的综合深度。",
                "",
            ]
        )

    paragraphs = _paragraphs(lines, start, end, parser)
    paragraph_statuses = [
        (para_start, para_end, _paragraph_a2_status(raws, texts))
        for para_start, para_end, raws, texts in paragraphs
    ]
    fail_ranges = [
        (para_start, para_end)
        for para_start, para_end, (status, _score) in paragraph_statuses
        if status == "fail"
    ]
    uncertain_ranges = [
        (para_start, para_end)
        for para_start, para_end, (status, _score) in paragraph_statuses
        if status == "uncertain"
    ]

    if len(fail_ranges) >= 2:
        out.extend(
            [
                f"{comment} 文献综述（第{fail_ranges[0][0]}-{fail_ranges[-1][1]}行）[Severity: Major] [Priority: P1]: "
                "多个引文密集段落仍偏向文献罗列，缺少充分的比较分析句。",
                f"{comment} 建议：每个主题簇结尾补一两句，概括共同优势、关键差异或共享不足。",
                f"{comment} 理由：综述的价值不在于列举做过什么，而在于说明这些工作之间如何对话。",
                "",
            ]
        )
    elif len(fail_ranges) == 1 or uncertain_ranges:
        review_start = fail_ranges[0][0] if fail_ranges else uncertain_ranges[0][0]
        review_end = fail_ranges[0][1] if fail_ranges else uncertain_ranges[-1][1]
        out.extend(
            [
                f"{comment} 文献综述（第{review_start}-{review_end}行）[Severity: Needs Review] [Priority: P2]: "
                "至少有一个引文密集段落的比较分析可能偏弱，建议复核。",
                f"{comment} 建议：检查该段是否在段末明确总结共同局限、关键差异或 theme-level synthesis。",
                f"{comment} 理由：边界样例更适合模型或人工复核，不宜直接作为硬规则失败处理。",
                "",
            ]
        )

    scan_start = max(start, end - 10)
    tail = "".join(text for line_no, _, text in visible if line_no >= scan_start)
    if tail and not GAP_KEYWORDS_ZH.search(tail):
        out.extend(
            [
                f"{comment} 文献综述（第{scan_start}-{end}行）[Severity: Major] [Priority: P1]: "
                "相关工作末尾未发现明确的研究空白推导。",
                f"{comment} 建议：在结尾指出尚未解决的限制、边界条件或被忽略的情形，再引出本文切入点。",
                f"{comment} 理由：研究空白应从既有文献的共识与不足中自然推出，而不是直接跳到本文工作。",
                "",
            ]
        )

    out.extend(
        [
            f"{comment} 文献综述重写蓝图：共识 -> 分歧 -> 局限 -> 空白 -> 本文切入点",
            f"{comment} 建议改写链条：先概括多篇文献的共同结论，再指出方法分歧或 trade-off，随后提炼仍未解决的限制，最后再连接到本文贡献。",
        ]
    )

    return out


def main() -> int:
    cli = argparse.ArgumentParser(description="中文学位论文文献综述分析")
    cli.add_argument("file", type=Path, help="目标 .tex/.typ 文件")
    cli.add_argument(
        "--section",
        default="related",
        help="指定分析章节，默认 related",
    )
    args = cli.parse_args()

    if not args.file.exists():
        print(f"[错误] 文件未找到: {args.file}", file=sys.stderr)
        return 1

    print("\n".join(analyze(args.file, args.section)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
