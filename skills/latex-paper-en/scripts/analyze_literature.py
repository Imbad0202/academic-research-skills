#!/usr/bin/env python3
"""
Literature review analyzer for LaTeX papers.

Focuses on Related Work / literature review sections:
- A1: author/year enumeration
- A2: missing comparative synthesis
- A3: missing research-gap derivation
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


AUTHOR_ENUM_EN = re.compile(
    r"^(?:In \d{4}|.*?\(\d{4}\).*?(?:proposed|introduced|presented|developed|designed))",
    re.IGNORECASE,
)

GAP_KEYWORDS_EN = re.compile(
    r"\b(gap|limitation|however.*(?:no|not|few)|remains|lack|overlooked|"
    r"under-explored|open problem|yet to be|inadequate|insufficient)\b",
    re.IGNORECASE,
)

COMPARISON_MARKERS_EN = re.compile(
    r"\b(however|whereas|while|although|despite|unlike|in contrast|by contrast|"
    r"compared with|compared to|similarly|different from|common limitation|"
    r"shared limitation|trade-?off|strength|weakness|still struggle|perform worse|"
    r"perform better|advantage|disadvantage)\b",
    re.IGNORECASE,
)

SUMMARY_MARKERS_EN = re.compile(
    r"\b(overall|collectively|taken together|as a group|in summary|on balance|"
    r"across these studies|common pattern|shared pattern)\b",
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
    joined = " ".join(texts)
    cite_hits = sum(
        1
        for raw, text in zip(raws, texts, strict=False)
        if "\\cite{" in raw or AUTHOR_ENUM_EN.search(text)
    )
    has_comparison = bool(COMPARISON_MARKERS_EN.search(joined))
    has_summary = bool(SUMMARY_MARKERS_EN.search(joined))
    has_gap = bool(GAP_KEYWORDS_EN.search(joined))

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
        return [f"{comment} ERROR [Severity: Critical] [Priority: P0]: Section not found: {target}"]

    start, end = bounds
    visible = _visible_lines(lines, start, end, parser)
    out: list[str] = []

    consecutive = 0
    streak_start = 0
    for line_no, _raw, text in visible:
        if AUTHOR_ENUM_EN.search(text):
            if consecutive == 0:
                streak_start = line_no
            consecutive += 1
        else:
            if consecutive >= 3:
                out.extend(
                    [
                        f"{comment} LITERATURE (Lines {streak_start}-{line_no - 1}) "
                        "[Severity: Major] [Priority: P1]: "
                        f"Author/year enumeration detected ({consecutive} consecutive entries)",
                        f"{comment} Suggested: Reorganize the cluster by theme, then compare methods inside the cluster.",
                        f"{comment} Rationale: Listing papers one by one weakens synthesis and hides the research conversation.",
                        "",
                    ]
                )
            consecutive = 0
    if consecutive >= 3:
        out.extend(
            [
                f"{comment} LITERATURE (Lines {streak_start}-{visible[-1][0]}) "
                "[Severity: Major] [Priority: P1]: "
                f"Author/year enumeration detected ({consecutive} consecutive entries)",
                f"{comment} Suggested: Reorganize the cluster by theme, then compare methods inside the cluster.",
                f"{comment} Rationale: Listing papers one by one weakens synthesis and hides the research conversation.",
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
                f"{comment} LITERATURE (Lines {fail_ranges[0][0]}-{fail_ranges[-1][1]}) [Severity: Major] [Priority: P1]: "
                "Citation-heavy theme clusters repeatedly catalog prior work without enough comparative synthesis.",
                f"{comment} Suggested: Close each theme cluster with one sentence on common strengths, differences, or shared limitations.",
                f"{comment} Rationale: A strong literature review should move from citation listing to analytical dialogue.",
                "",
            ]
        )
    elif len(fail_ranges) == 1 or uncertain_ranges:
        review_start = fail_ranges[0][0] if fail_ranges else uncertain_ranges[0][0]
        review_end = fail_ranges[0][1] if fail_ranges else uncertain_ranges[-1][1]
        out.extend(
            [
                f"{comment} LITERATURE (Lines {review_start}-{review_end}) [Severity: Needs Review] [Priority: P2]: "
                "Comparative synthesis may be too weak in at least one citation-heavy paragraph.",
                f"{comment} Suggested: Check whether the paragraph ends with an explicit comparison, shared limitation, or cluster-level synthesis sentence.",
                f"{comment} Rationale: Borderline literature-review cases often need manual or LLM review rather than a hard rule-based failure.",
                "",
            ]
        )

    scan_start = max(start, end - 10)
    tail = " ".join(text for line_no, _, text in visible if line_no >= scan_start)
    if tail and not GAP_KEYWORDS_EN.search(tail):
        out.extend(
            [
                f"{comment} LITERATURE (Lines {scan_start}-{end}) [Severity: Major] [Priority: P1]: "
                "No explicit research-gap derivation found at the end of the literature review.",
                f"{comment} Suggested: End the section with the unresolved limitation or under-explored condition that motivates the present paper.",
                f"{comment} Rationale: Readers need a literature-derived gap, not an abrupt jump from prior work to your method.",
                "",
            ]
        )

    out.extend(
        [
            f"{comment} LITERATURE BLUEPRINT: Consensus -> Disagreement -> Limitations -> Gap -> This paper",
            f"{comment} Suggested rewrite chain: summarize what multiple papers agree on, surface one key disagreement or trade-off, isolate the unresolved limitation, then connect that gap to your contribution.",
        ]
    )

    return out


def main() -> int:
    cli = argparse.ArgumentParser(description="Literature review analysis for LaTeX papers")
    cli.add_argument("file", type=Path, help="Target .tex/.typ file")
    cli.add_argument(
        "--section",
        default="related",
        help="Section to analyze (defaults to related)",
    )
    args = cli.parse_args()

    if not args.file.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        return 1

    print("\n".join(analyze(args.file, args.section)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
