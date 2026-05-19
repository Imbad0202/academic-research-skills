#!/usr/bin/env python3
"""
Title Optimization Tool for LaTeX Academic Papers (English)

Based on IEEE Author Center and top-tier venue best practices.
Generates and optimizes paper titles following academic standards.
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

try:
    from parsers import extract_abstract, extract_title
except ImportError:
    import os

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parsers import extract_abstract, extract_title


# Ineffective words to remove
INEFFECTIVE_WORDS = [
    "a study of",
    "research on",
    "novel",
    "new",
    "improved",
    "enhanced",
    "based on",
    "using",
    "utilizing",
    "an investigation of",
    "analysis of",
]

# Common abbreviations acceptable in titles
ACCEPTABLE_ABBREVS = {
    "AI",
    "ML",
    "DL",
    "LSTM",
    "GRU",
    "CNN",
    "RNN",
    "GAN",
    "VAE",
    "IoT",
    "5G",
    "GPS",
    "DNA",
    "RNA",
    "MRI",
    "CT",
    "PID",
    "API",
    "GPU",
    "CPU",
    "RAM",
    "SQL",
    "HTTP",
    "TCP",
    "IP",
}


def extract_keywords_from_abstract(abstract: str) -> dict[str, list[str]]:
    """Extract potential keywords from abstract."""
    method_keywords = []
    problem_keywords = []
    domain_keywords = []

    method_patterns = [
        r"\b(transformer|attention|lstm|gru|cnn|neural network|deep learning|"
        r"machine learning|reinforcement learning|graph neural network|"
        r"convolutional|recurrent)\b"
    ]
    problem_patterns = [
        r"\b(forecasting|prediction|detection|classification|segmentation|"
        r"recognition|optimization|control|diagnosis|monitoring)\b"
    ]
    domain_patterns = [
        r"\b(industrial|manufacturing|medical|healthcare|autonomous|"
        r"smart|intelligent|real-time|time series)\b"
    ]

    abstract_lower = abstract.lower()
    for pattern in method_patterns:
        method_keywords.extend(re.findall(pattern, abstract_lower, re.IGNORECASE))
    for pattern in problem_patterns:
        problem_keywords.extend(re.findall(pattern, abstract_lower, re.IGNORECASE))
    for pattern in domain_patterns:
        domain_keywords.extend(re.findall(pattern, abstract_lower, re.IGNORECASE))

    return {
        "method": list(dict.fromkeys(method_keywords))[:3],
        "problem": list(dict.fromkeys(problem_keywords))[:3],
        "domain": list(dict.fromkeys(domain_keywords))[:2],
    }


def score_title(title: str) -> dict[str, Any]:
    """Score a title based on best practices."""
    scores: dict[str, int] = {}
    issues: list[str] = []

    title_lower = title.lower()

    ineffective_found = [word for word in INEFFECTIVE_WORDS if word in title_lower]
    if ineffective_found:
        scores["conciseness"] = max(0, 25 - len(ineffective_found) * 10)
        issues.append(f"[Critical] Contains ineffective words: {', '.join(ineffective_found)}")
    else:
        scores["conciseness"] = 25

    first_65 = title[:65]
    technical_terms = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b", first_65)
    if len(technical_terms) >= 2:
        scores["searchability"] = 30
    elif len(technical_terms) == 1:
        scores["searchability"] = 20
        issues.append("[Major] Consider placing more key terms in first 65 characters")
    else:
        scores["searchability"] = 10
        issues.append("[Critical] Key terms should appear in first 65 characters")

    word_count = len(title.split())
    if 10 <= word_count <= 15:
        scores["length"] = 15
    elif 8 <= word_count <= 20:
        scores["length"] = 10
        issues.append(f"[Minor] Length is acceptable ({word_count} words) but could be optimized")
    else:
        scores["length"] = 5
        issues.append(f"[Major] Length is suboptimal ({word_count} words, target: 10-15)")

    vague_terms = ["method", "approach", "system", "model", "algorithm"]
    vague_found = sum(1 for term in vague_terms if term in title_lower)
    if vague_found == 0:
        scores["specificity"] = 20
    elif vague_found == 1:
        scores["specificity"] = 15
    else:
        scores["specificity"] = 10
        issues.append("[Major] Title contains vague terms, be more specific")

    words = title.split()
    abbrevs = [word for word in words if word.isupper() and len(word) > 1]
    obscure_abbrevs = [abbr for abbr in abbrevs if abbr not in ACCEPTABLE_ABBREVS]
    if obscure_abbrevs:
        scores["jargon"] = 5
        issues.append(f"[Minor] Obscure abbreviations found: {', '.join(obscure_abbrevs)}")
    else:
        scores["jargon"] = 10

    total = sum(scores.values())
    return {"total": total, "breakdown": scores, "issues": issues}


def generate_title_candidates(
    keywords: dict[str, list[str]], current_title: Optional[str] = None
) -> list[tuple[str, str]]:
    """Generate title candidates based on extracted keywords."""
    candidates: list[tuple[str, str]] = []

    method_candidates = keywords.get("method") or ["Deep Learning"]
    problem_candidates = keywords.get("problem") or ["Analysis"]
    domain_candidates = keywords.get("domain") or [""]

    method = method_candidates[0].title()
    problem = problem_candidates[0].title()
    domain = domain_candidates[0].title()

    if method and problem:
        title = f"{method} for {problem}"
        if domain:
            title += f" in {domain}"
        candidates.append((title, "method_for_problem"))

    if method and problem and domain:
        candidates.append((f"{method}: {problem} in {domain}", "method_problem_domain"))

    if problem and method:
        candidates.append((f"{problem} via {method}", "problem_via_method"))

    if method and problem:
        candidates.append((f"Lightweight {method} for {problem}", "method_feature"))

    # De-duplicate while preserving order
    seen: set[str] = set()
    deduped: list[tuple[str, str]] = []
    for title, template in candidates:
        normalized = title.strip().lower()
        if normalized not in seen:
            seen.add(normalized)
            deduped.append((title, template))
    return deduped


def optimize_title(title: str) -> str:
    """Optimize an existing title by removing ineffective words."""
    optimized = title
    for word in INEFFECTIVE_WORDS:
        optimized = re.compile(re.escape(word), re.IGNORECASE).sub("", optimized)
    optimized = re.sub(r"\s+", " ", optimized).strip()
    optimized = re.sub(r"^(A|An|The)\s+", "", optimized, flags=re.IGNORECASE)
    return optimized


def format_report(
    title: str, score_data: dict, candidates: list[tuple[str, str]] | None = None
) -> str:
    """Format optimization report."""
    report = []
    report.append("% " + "=" * 60)
    report.append("% TITLE OPTIMIZATION REPORT")
    report.append("% " + "=" * 60)
    report.append(f'% Current Title: "{title}"')
    report.append(f"% Quality Score: {score_data['total']}/100")
    report.append("%")

    if score_data["issues"]:
        report.append("% Issues Detected:")
        for idx, issue in enumerate(score_data["issues"], 1):
            report.append(f"% {idx}. {issue}")
        report.append("%")

    if candidates:
        report.append("% Recommended Titles (Ranked):")
        report.append("%")
        for idx, (candidate, _template) in enumerate(candidates, 1):
            candidate_score = score_title(candidate)
            report.append(f'% {idx}. "{candidate}" [Score: {candidate_score["total"]}/100]')
            report.append(
                f"%    - Concise: {'✅' if candidate_score['breakdown']['conciseness'] >= 20 else '⚠️'}"
            )
            report.append(
                f"%    - Searchable: {'✅' if candidate_score['breakdown']['searchability'] >= 20 else '⚠️'}"
            )
            report.append(
                f"%    - Length: {'✅' if candidate_score['breakdown']['length'] >= 10 else '⚠️'} "
                f"({len(candidate.split())} words)"
            )
            report.append("%")

        best_title = sorted(
            candidates, key=lambda item: score_title(item[0])["total"], reverse=True
        )[0][0]
        report.append("% Suggested LaTeX Update:")
        report.append(f"% \\title{{{best_title}}}")
    report.append("% " + "=" * 60)
    return "\n".join(report)


def _load_content(tex_path: Path) -> str:
    return tex_path.read_text(encoding="utf-8", errors="ignore")


def _resolve_batch_files(pattern_or_file: str) -> list[Path]:
    path = Path(pattern_or_file)
    if path.is_file():
        return [path]
    if any(char in pattern_or_file for char in ["*", "?", "["]):
        return [Path(p) for p in sorted(glob.glob(pattern_or_file))]
    return sorted(path.glob("*.tex")) if path.is_dir() else []


def _rank_candidates(candidates: list[tuple[str, str]]) -> list[tuple[str, str, int]]:
    scored = [(title, template, score_title(title)["total"]) for title, template in candidates]
    return sorted(scored, key=lambda item: item[2], reverse=True)


def _interactive_title_flow(current_title: str | None) -> int:
    print("Interactive title generation")
    print("Leave blank to use defaults.")
    method = input("Method keyword (e.g., Transformer): ").strip() or "Transformer"
    problem = (
        input("Problem keyword (e.g., Time Series Forecasting): ").strip()
        or "Time Series Forecasting"
    )
    domain = input("Domain keyword (optional, e.g., Industrial Control): ").strip()

    keywords = {
        "method": [method.lower()],
        "problem": [problem.lower()],
        "domain": [domain.lower()] if domain else [],
    }
    candidates = generate_title_candidates(keywords, current_title)
    ranked = _rank_candidates(candidates)
    top_candidates = [(title, template) for title, template, _ in ranked[:5]]

    if current_title:
        print(format_report(current_title, score_title(current_title), top_candidates))
    else:
        print("% Generated Title Candidates:")
        for idx, (title, _template, total) in enumerate(ranked[:5], 1):
            print(f'% {idx}. "{title}" [Score: {total}/100]')
    return 0


def _run_compare_mode(titles: list[str]) -> int:
    if len(titles) < 2:
        print("Error: --compare requires at least two title candidates.", file=sys.stderr)
        return 1

    ranked = sorted(
        [(title, score_title(title)) for title in titles], key=lambda x: x[1]["total"], reverse=True
    )
    print("% TITLE COMPARISON")
    print("% " + "=" * 60)
    for idx, (title, data) in enumerate(ranked, 1):
        print(f'% {idx}. "{title}" [Score: {data["total"]}/100]')
        if data["issues"]:
            print(f"%    Issues: {'; '.join(data['issues'])}")
    print("% " + "=" * 60)
    return 0


def _run_batch_mode(pattern_or_file: str, output: str | None) -> int:
    files = _resolve_batch_files(pattern_or_file)
    if not files:
        print(f"Error: No files matched for batch mode: {pattern_or_file}", file=sys.stderr)
        return 1

    results = []
    for tex_path in files:
        content = _load_content(tex_path)
        current_title = extract_title(content)
        abstract = extract_abstract(content) or content[:1000]
        keywords = extract_keywords_from_abstract(abstract)
        candidates = generate_title_candidates(keywords, current_title)
        ranked = _rank_candidates(candidates)
        best_title = ranked[0][0] if ranked else ""
        best_score = ranked[0][2] if ranked else 0
        current_score = score_title(current_title)["total"] if current_title else 0
        results.append(
            {
                "file": str(tex_path),
                "current_title": current_title,
                "current_score": current_score,
                "best_candidate": best_title,
                "best_score": best_score,
            }
        )

    if output:
        output_path = Path(output)
        output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved batch title report to: {output_path}")
    else:
        print("% BATCH TITLE REPORT")
        print("% " + "=" * 60)
        for item in results:
            print(f"% File: {item['file']}")
            print(
                f"% Current: {item['current_title'] or '[No title]'} ({item['current_score']}/100)"
            )
            print(f"% Best:    {item['best_candidate'] or '[N/A]'} ({item['best_score']}/100)")
            print("%")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Optimize LaTeX paper titles following IEEE/ACM/Springer best practices"
    )
    parser.add_argument("tex_file", help="Main .tex file, file glob, or directory in --batch mode")
    parser.add_argument(
        "--generate", action="store_true", help="Generate title candidates from abstract content"
    )
    parser.add_argument("--optimize", action="store_true", help="Optimize existing title")
    parser.add_argument("--check", action="store_true", help="Check title quality")
    parser.add_argument(
        "--interactive", action="store_true", help="Interactive mode with user input"
    )
    parser.add_argument(
        "--batch", action="store_true", help="Batch mode: process multiple .tex files"
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        metavar="TITLE",
        help="Compare multiple candidate titles and rank by score",
    )
    parser.add_argument("--output", help="Output file path for --batch mode")

    args = parser.parse_args()

    if args.compare:
        return _run_compare_mode(args.compare)

    if args.batch:
        return _run_batch_mode(args.tex_file, args.output)

    tex_path = Path(args.tex_file)
    if not tex_path.exists():
        print(f"Error: File not found: {tex_path}", file=sys.stderr)
        return 1

    content = _load_content(tex_path)
    current_title = extract_title(content)

    if args.interactive:
        return _interactive_title_flow(current_title)

    if args.check or not (args.generate or args.optimize):
        if not current_title:
            print("Error: No title found in document", file=sys.stderr)
            return 1
        print(format_report(current_title, score_title(current_title)))
        return 0

    if args.generate:
        abstract = extract_abstract(content)
        if not abstract:
            print(
                "Warning: No abstract found, using file head for keyword extraction",
                file=sys.stderr,
            )
            abstract = content[:1000]

        candidates = generate_title_candidates(
            extract_keywords_from_abstract(abstract), current_title
        )
        ranked = _rank_candidates(candidates)
        top_candidates = [(title, template) for title, template, _ in ranked[:5]]

        if current_title:
            print(format_report(current_title, score_title(current_title), top_candidates))
        else:
            print("% Generated Title Candidates:")
            for idx, (title, _template, total) in enumerate(ranked[:5], 1):
                print(f'% {idx}. "{title}" [Score: {total}/100]')
        return 0

    if args.optimize:
        if not current_title:
            print("Error: No title found in document", file=sys.stderr)
            return 1

        optimized = optimize_title(current_title)
        score_before = score_title(current_title)
        score_after = score_title(optimized)

        print(f'% Original: "{current_title}" [Score: {score_before["total"]}/100]')
        print(f'% Optimized: "{optimized}" [Score: {score_after["total"]}/100]')
        print(f"% Improvement: +{score_after['total'] - score_before['total']} points")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
