#!/usr/bin/env python3
"""
Experiment review helper for LaTeX/Typst papers.

Outputs reviewer-style LaTeX comments without modifying source files.
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


SECTION_ALIASES = {
    "experiment": "experiment",
    "experiments": "experiment",
    "evaluation": "experiment",
    "evaluations": "experiment",
    "result": "result",
    "results": "result",
}

CLAIM_MARKERS = {
    "improve",
    "improves",
    "improved",
    "outperform",
    "outperforms",
    "outperformed",
    "better",
    "superior",
    "gain",
    "gains",
    "gained",
    "reduce",
    "reduces",
    "reduced",
    "state-of-the-art",
    "sota",
}
GENERIC_COMPARATORS = (
    "baseline",
    "baselines",
    "previous methods",
    "prior methods",
    "existing methods",
    "conventional methods",
    "other methods",
    "prior work",
)
METRIC_RE = re.compile(
    r"\b(acc(?:uracy)?|f1|precision|recall|auc|auroc|map|ndcg|mrr|mae|mse|rmse|"
    r"bleu|rouge|wer|iou|miou|psnr|ssim|loss|latency|throughput|runtime|"
    r"memory|flops|parameter(?:s)?|params?)\b",
    re.IGNORECASE,
)
NUMERIC_RE = re.compile(r"(?:\b\d+(?:\.\d+)?\b|%|±)")
OVERCLAIM_RE = re.compile(
    r"\b(significant improvement|dramatically|substantially|clearly superior|"
    r"state-of-the-art|best-ever|remarkable)\b",
    re.IGNORECASE,
)
UNSUPPORTED_RE = re.compile(
    r"\b(proves?|guarantees?|always|universally|in all settings|for all datasets|"
    r"for any dataset|without exception)\b",
    re.IGNORECASE,
)
COMPARATOR_HINT_RE = re.compile(
    r"\b(compared with|against|versus|vs\.?|than|over)\b", re.IGNORECASE
)
SPECIFIC_COMPARATOR_RE = re.compile(
    r"(\\cite\{|"
    r"\b(?:ResNet|BERT|Transformer|LSTM|GRU|CNN|RNN|SVM|XGBoost|LightGBM|"
    r"CatBoost|YOLO|UNet|U-Net|ViT|CLIP|GPT|T5|RoBERTa)\b|"
    r"\b[A-Z]{2,}[A-Z0-9-]*\b)"
)
ABLATION_RE = re.compile(r"\b(ablation|component study|without [a-z]|w/o)\b", re.IGNORECASE)
STATS_RE = re.compile(
    r"(p\s*[<=>]|standard deviation|std\.?|confidence interval|variance|±)",
    re.IGNORECASE,
)
EFFICIENCY_RE = re.compile(
    r"\b(latency|runtime|throughput|inference|memory|flops|parameter(?:s)?|params?)\b",
    re.IGNORECASE,
)

# ── Discussion depth & literature echo (B3, B4) ────────────────

ATTRIBUTION_MARKERS_EN = re.compile(
    r"\b(because|due to|owing to|as a result of|attributed to|caused by|"
    r"mechanism|explains|explanation|reason|hypothesis|interpret|"
    r"stems from|arises from|driven by|suggests that|indicates that)\b",
    re.IGNORECASE,
)
DISCUSSION_CATEGORY_MARKERS_EN = {
    "mechanism": re.compile(
        r"\b(because|due to|mechanism|explains|reason|stems from|driven by|suggests that)\b",
        re.IGNORECASE,
    ),
    "comparison": re.compile(
        r"\b(compared with|compared to|relative to|unlike|consistent with|prior work|baseline)\b",
        re.IGNORECASE,
    ),
    "limitation": re.compile(
        r"\b(limitation|limitations|boundary|boundaries|fails? when|trade-off|caveat|underperforms)\b",
        re.IGNORECASE,
    ),
    "implication": re.compile(
        r"\b(implication|practical|application|future work|future direction|suggests broader)\b",
        re.IGNORECASE,
    ),
}

CITE_KEY_RE = re.compile(r"\\(?:cite\w*)\*?(?:\[[^\]]*\]\s*)*\{([^}]*)\}")


def _check_discussion_depth(lines: list[str], start: int, end: int, parser) -> list[str]:
    """B3: Check ratio of explanatory vs data-repetition lines in discussion."""
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
                f"language ({attribution_lines}/{total_visible} lines). "
                "Add causal analysis explaining why results occur.",
            )
        )
        out.append("")
    return out


def _check_discussion_structure(lines: list[str], start: int, end: int, parser) -> list[str]:
    """Check whether long discussions cover multiple argumentative categories."""
    out: list[str] = []
    visible_lines: list[str] = []
    category_hits = dict.fromkeys(DISCUSSION_CATEGORY_MARKERS_EN, 0)

    for line_no in range(start, min(end, len(lines)) + 1):
        raw = lines[line_no - 1].strip()
        if not raw or raw.startswith(parser.get_comment_prefix()):
            continue
        visible = parser.extract_visible_text(raw)
        if not visible:
            continue
        visible_lines.append(visible)
        for name, pattern in DISCUSSION_CATEGORY_MARKERS_EN.items():
            if pattern.search(visible):
                category_hits[name] += 1

    if len(visible_lines) < 6:
        return out

    covered_categories = [name for name, count in category_hits.items() if count > 0]
    topic_sentence_count = sum(
        1 for visible in visible_lines if visible[:1].isupper() and len(visible.split()) >= 6
    )
    if len(covered_categories) < 2 or topic_sentence_count < 2:
        out.extend(
            _format_issue(
                start,
                "Major",
                "P1",
                "Discussion may lack layered structure: it should cover at least two categories "
                "(mechanism, comparison with prior work, limitations/boundaries, implications/outlook) "
                "instead of only restating results.",
            )
        )
        out.append("")
    return out


def _extract_cite_keys_in_range(lines: list[str], start: int, end: int) -> set[str]:
    """Extract all citation keys from lines in a given range."""
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
    """B4: Check if citation keys from Related Work appear in Discussion."""
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
                "No citations from Related Work reappear in Discussion. "
                "Compare your findings with prior work to strengthen the narrative.",
            )
        )
        out.append("")
    return out


# ── Conclusion completeness (B5) ───────────────────────────────

CONCLUSION_FINDINGS_RE = re.compile(
    r"\b(we have shown|we demonstrated|results show|this paper has presented|"
    r"our experiments confirm|we proposed|we have proposed|findings indicate|"
    r"key findings?|main results?)\b",
    re.IGNORECASE,
)
CONCLUSION_IMPLICATIONS_RE = re.compile(
    r"\b(implication|suggests that.*practical|enables|opens|paves the way|"
    r"facilitates|contributes to|advance|potential for|applicable to)\b",
    re.IGNORECASE,
)
CONCLUSION_LIMITATIONS_RE = re.compile(
    r"\b(limitation|future work|future direction|remain|challenge|"
    r"could be extended|further research|further investigation|"
    r"not addressed|beyond the scope|caveat)\b",
    re.IGNORECASE,
)


def _check_conclusion_completeness(lines: list[str], start: int, end: int, parser) -> list[str]:
    """B5: Conclusion must contain findings + implications + limitations/future."""
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

    has_findings = bool(CONCLUSION_FINDINGS_RE.search(section_text))
    has_implications = bool(CONCLUSION_IMPLICATIONS_RE.search(section_text))
    has_limitations = bool(CONCLUSION_LIMITATIONS_RE.search(section_text))

    if not has_limitations:
        out.extend(
            _format_issue(
                start, "Major", "P1", "Conclusion lacks limitations or future work discussion."
            )
        )
        out.append("")
    if not has_implications:
        out.extend(
            _format_issue(
                start, "Minor", "P2", "Conclusion lacks implications or broader impact statement."
            )
        )
        out.append("")
    if not has_findings:
        out.extend(
            _format_issue(
                start, "Minor", "P2", "Conclusion lacks explicit summary of core findings."
            )
        )
        out.append("")
    return out


FALLBACK_SECTION_PATTERNS = {
    "experiment": re.compile(
        r"(\\section\*?\{.*(?:Experiment|Experiments|Evaluation|Evaluations|Implementation).*\}|"
        r"^=\s+.*(?:Experiment|Experiments|Evaluation|Evaluations|Implementation).*)",
        re.IGNORECASE,
    ),
    "result": re.compile(
        r"(\\section\*?\{.*(?:Result|Results|Performance).*\}|"
        r"^=\s+.*(?:Result|Results|Performance).*)",
        re.IGNORECASE,
    ),
}


def _normalize_section(section: str | None) -> str | None:
    if not section:
        return None
    normalized = section.strip().lower()
    return SECTION_ALIASES.get(normalized, normalized)


def _format_issue(line_no: int, severity: str, priority: str, message: str) -> list[str]:
    return [
        f"% EXPERIMENT (Line {line_no}) [Severity: {severity}] [Priority: {priority}]: {message}"
    ]


def _has_claim(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in CLAIM_MARKERS)


def _has_specific_comparator(raw: str, visible: str) -> bool:
    return bool(SPECIFIC_COMPARATOR_RE.search(raw) or SPECIFIC_COMPARATOR_RE.search(visible))


def _add_issue(output: list[str], line_no: int, severity: str, priority: str, message: str) -> None:
    output.extend(_format_issue(line_no, severity, priority, message))
    output.append("")


def _fallback_ranges(lines: list[str], section_key: str) -> list[tuple[int, int]]:
    pattern = FALLBACK_SECTION_PATTERNS.get(section_key)
    if not pattern:
        return []

    starts = [idx for idx, line in enumerate(lines, 1) if pattern.search(line)]
    if not starts:
        return []

    ranges: list[tuple[int, int]] = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] - 1 if idx + 1 < len(starts) else len(lines)
        ranges.append((start, end))
    return ranges


def analyze(file_path: Path, section: str | None = None) -> list[str]:
    parser = get_parser(file_path)
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")
    sections = parser.split_sections(content)

    selected_ranges: list[tuple[int, int]] = []
    normalized_section = _normalize_section(section)
    if normalized_section:
        if normalized_section not in sections:
            selected_ranges.extend(_fallback_ranges(lines, normalized_section))
            if not selected_ranges:
                return [
                    f"% ERROR [Severity: Critical] [Priority: P0]: Section not found: {section}"
                ]
        else:
            selected_ranges.append(sections[normalized_section])
    else:
        if sections:
            selected_ranges.extend(
                bounds for name, bounds in sections.items() if name in {"experiment", "result"}
            )
        if not selected_ranges:
            selected_ranges.extend(_fallback_ranges(lines, "experiment"))
            selected_ranges.extend(_fallback_ranges(lines, "result"))
        if not selected_ranges:
            selected_ranges.append((1, len(lines)))

    output: list[str] = []
    for start, end in selected_ranges:
        section_visible_lines: list[str] = []
        line_level_baseline_flagged = False
        has_specific_baseline = False

        for line_no in range(start, min(end, len(lines)) + 1):
            raw = lines[line_no - 1].strip()
            if not raw or raw.startswith(parser.get_comment_prefix()):
                continue

            visible = parser.extract_visible_text(raw)
            if not visible:
                continue

            section_visible_lines.append(visible)
            lowered = visible.lower()
            has_claim = _has_claim(visible)

            if _has_specific_comparator(raw, visible):
                has_specific_baseline = True

            if has_claim:
                if any(marker in lowered for marker in GENERIC_COMPARATORS):
                    if not _has_specific_comparator(raw, visible):
                        _add_issue(
                            output,
                            line_no,
                            "Major",
                            "P1",
                            "Comparison claim names only generic baselines; cite or name the exact comparator.",
                        )
                        line_level_baseline_flagged = True
                elif not COMPARATOR_HINT_RE.search(lowered):
                    _add_issue(
                        output,
                        line_no,
                        "Major",
                        "P1",
                        "Performance claim lacks an explicit baseline or comparator.",
                    )
                    line_level_baseline_flagged = True

                if not (METRIC_RE.search(visible) or NUMERIC_RE.search(raw)):
                    _add_issue(
                        output,
                        line_no,
                        "Major",
                        "P1",
                        "Performance claim is not tied to a concrete metric or numeric result.",
                    )

            if OVERCLAIM_RE.search(lowered):
                _add_issue(
                    output,
                    line_no,
                    "Major",
                    "P1",
                    "Wording sounds promotional; keep the claim evidence-backed and specific.",
                )

            if UNSUPPORTED_RE.search(lowered):
                _add_issue(
                    output,
                    line_no,
                    "Critical",
                    "P0",
                    "Conclusion overreaches the reported evidence; avoid universal or guarantee-style claims.",
                )

        section_anchor = start
        section_text = "\n".join(section_visible_lines)
        has_claims = any(_has_claim(line) for line in section_visible_lines)

        if has_claims and not has_specific_baseline and not line_level_baseline_flagged:
            _add_issue(
                output,
                section_anchor,
                "Major",
                "P1",
                "Section does not identify a concrete baseline or comparator for the main claim.",
            )
        if section_text and not ABLATION_RE.search(section_text):
            _add_issue(
                output,
                section_anchor,
                "Minor",
                "P2",
                "No ablation or component-level evidence is mentioned; verify that contribution attribution is covered.",
            )
        if section_text and not STATS_RE.search(section_text):
            _add_issue(
                output,
                section_anchor,
                "Minor",
                "P2",
                "No statistical significance, variance, or confidence information is mentioned.",
            )
        if section_text and not EFFICIENCY_RE.search(section_text):
            _add_issue(
                output,
                section_anchor,
                "Minor",
                "P2",
                "No efficiency comparison is mentioned; verify whether runtime, memory, or parameter cost should be reported.",
            )

    # ── Section-level discussion, echo & conclusion checks ─────
    if sections:
        if (
            not normalized_section or normalized_section == "discussion"
        ) and "discussion" in sections:
            d_start, d_end = sections["discussion"]
            output.extend(_check_discussion_depth(lines, d_start, d_end, parser))
            output.extend(_check_discussion_structure(lines, d_start, d_end, parser))

        if not normalized_section:
            output.extend(_check_results_literature_echo(lines, sections))

        if (
            not normalized_section or normalized_section == "conclusion"
        ) and "conclusion" in sections:
            c_start, c_end = sections["conclusion"]
            output.extend(_check_conclusion_completeness(lines, c_start, c_end, parser))

    if not output:
        output.append("% EXPERIMENT: No rule-based experiment review issues detected.")
    return output


def main() -> int:
    cli = argparse.ArgumentParser(description="Experiment section review for LaTeX/Typst files")
    cli.add_argument("file", type=Path, help="Target .tex/.typ file")
    cli.add_argument("--section", help="Section name to analyze")
    args = cli.parse_args()

    if not args.file.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        return 1

    print("\n".join(analyze(args.file, args.section)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
