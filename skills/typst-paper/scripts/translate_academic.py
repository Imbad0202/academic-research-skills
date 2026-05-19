#!/usr/bin/env python3
"""
Chinese -> English academic translation helper (MVP).

This script is terminology-driven and provides:
1) terminology confirmation table
2) draft translation
3) ambiguity notes requiring manual confirmation
"""

import argparse
import sys
from pathlib import Path

TERMINOLOGY = {
    "deep-learning": {
        "注意力机制": "attention mechanism",
        "损失函数": "loss function",
        "神经网络": "neural network",
        "时间序列预测": "time series forecasting",
        "模型": "model",
    },
    "time-series": {
        "时间序列": "time series",
        "预测": "forecasting",
        "滑动窗口": "sliding window",
        "趋势": "trend",
        "季节性": "seasonality",
    },
    "industrial-control": {
        "故障检测": "fault detection",
        "工业控制": "industrial control",
        "控制系统": "control system",
        "实时": "real-time",
        "鲁棒性": "robustness",
    },
}

AMBIGUOUS_TERMS = {
    "控制": ["control", "controller", "regulation"],
    "性能": ["performance", "efficiency"],
    "优化": ["optimization", "improvement"],
}

COMMON_PATTERNS = {
    "本文提出": "We propose",
    "实验结果表明": "Experimental results demonstrate that",
    "与...相比": "Compared with ...",
    "在...中": "in ...",
}


def _load_source(input_arg: str) -> str:
    path = Path(input_arg)
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8", errors="ignore")
    return input_arg


def _build_term_table(text: str, domain: str) -> list[tuple[str, str, str]]:
    table: list[tuple[str, str, str]] = []
    domain_terms = TERMINOLOGY.get(domain, {})
    for zh, en in domain_terms.items():
        if zh in text:
            table.append((zh, en, domain))
    return table


def _draft_translate(text: str, domain: str) -> tuple[str, list[str]]:
    translated = text
    notes: list[str] = []

    for zh, en in TERMINOLOGY.get(domain, {}).items():
        if zh in translated:
            translated = translated.replace(zh, en)

    for zh, en in COMMON_PATTERNS.items():
        if zh in translated:
            translated = translated.replace(zh, en)

    for term, options in AMBIGUOUS_TERMS.items():
        if term in translated:
            notes.append(f"Ambiguous term '{term}' -> choose one: {', '.join(options)}")

    # Minimal sentence formatting
    translated = translated.replace("。", ". ").replace("，", ", ")
    translated = " ".join(translated.split())
    return translated, notes


def translate(input_arg: str, domain: str) -> str:
    text = _load_source(input_arg)
    table = _build_term_table(text, domain)
    draft, notes = _draft_translate(text, domain)

    lines: list[str] = []
    lines.append("### Terminology Confirmation")
    lines.append("| 中文 | English | Domain |")
    lines.append("|------|---------|--------|")
    if table:
        for zh, en, dom in table:
            lines.append(f"| {zh} | {en} | {dom} |")
    else:
        lines.append("| (none detected) | - | - |")

    lines.append("\n### Translation Draft")
    lines.append(f"% ORIGINAL: {text}")
    lines.append(f"% TRANSLATION: {draft}")

    lines.append("\n### Notes")
    if notes:
        for note in notes:
            lines.append(f"- ⚠️ [PENDING CONFIRMATION] {note}")
    else:
        lines.append("- No high-risk ambiguous terms detected by rule set.")

    return "\n".join(lines)


def main() -> int:
    cli = argparse.ArgumentParser(description="Terminology-driven academic translation helper")
    cli.add_argument("input", help="Chinese text or a file path containing Chinese text")
    cli.add_argument(
        "--domain",
        choices=["deep-learning", "time-series", "industrial-control"],
        default="deep-learning",
        help="Domain terminology set",
    )
    cli.add_argument("--output", help="Output file path")
    args = cli.parse_args()

    result = translate(args.input, args.domain)
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"[SUCCESS] Translation report written to: {args.output}")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
