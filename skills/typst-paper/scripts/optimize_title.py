#!/usr/bin/env python3
"""
Title Optimization Tool for Typst Academic Papers

Supports both English and Chinese papers.
Based on IEEE/ACM/Springer/NeurIPS best practices.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

# Import parsers from the same directory
try:
    from parsers import extract_abstract, extract_title
except ImportError:
    import os

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parsers import extract_abstract, extract_title


# Ineffective words (English)
INEFFECTIVE_WORDS_EN = [
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

# Ineffective words (Chinese)
INEFFECTIVE_WORDS_ZH = [
    "关于",
    "的研究",
    "的探索",
    "新型",
    "新颖的",
    "改进的",
    "优化的",
    "基于",
    "研究与",
    "分析与",
]

# Acceptable abbreviations
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


def detect_language(text: str) -> str:
    """Detect if text is primarily Chinese or English."""
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    total_chars = len(text.strip())

    if total_chars == 0:
        return "en"

    chinese_ratio = chinese_chars / total_chars
    return "zh" if chinese_ratio > 0.3 else "en"


def count_chinese_chars(text: str) -> int:
    """Count Chinese characters."""
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def extract_keywords_from_abstract(abstract: str, lang: str) -> dict[str, list[str]]:
    """Extract keywords from abstract."""
    method_keywords = []
    problem_keywords = []
    domain_keywords = []

    if lang == "en":
        # English patterns
        method_patterns = [
            r"\b(transformer|attention|lstm|gru|cnn|neural network|deep learning|"
            r"machine learning|reinforcement learning|graph neural network)\b"
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

    else:  # Chinese
        method_patterns = [
            r"(Transformer|注意力机制|LSTM|GRU|卷积神经网络|循环神经网络|"
            r"深度学习|机器学习|强化学习|图神经网络|神经网络)"
        ]
        problem_patterns = [
            r"(预测|检测|分类|分割|识别|优化|控制|诊断|监测|"
            r"时间序列|故障|异常|图像|文本)"
        ]
        domain_patterns = [
            r"(工业|制造|医疗|医学|自动驾驶|智能|实时|"
            r"工业控制|智能制造|医学影像)"
        ]

        for pattern in method_patterns:
            method_keywords.extend(re.findall(pattern, abstract))
        for pattern in problem_patterns:
            problem_keywords.extend(re.findall(pattern, abstract))
        for pattern in domain_patterns:
            domain_keywords.extend(re.findall(pattern, abstract))

    return {
        "method": list(set(method_keywords))[:3],
        "problem": list(set(problem_keywords))[:3],
        "domain": list(set(domain_keywords))[:2],
    }


def score_title(title: str, lang: str = None) -> dict[str, any]:
    """Score a title based on best practices."""
    if lang is None:
        lang = detect_language(title)

    scores = {}
    issues = []

    ineffective_words = INEFFECTIVE_WORDS_ZH if lang == "zh" else INEFFECTIVE_WORDS_EN

    # 1. Conciseness (25%)
    title_lower = title.lower() if lang == "en" else title
    ineffective_found = [word for word in ineffective_words if word in title_lower]
    if ineffective_found:
        conciseness_score = max(0, 25 - len(ineffective_found) * 10)
        issues.append(
            f"[Critical/严重] Contains ineffective words/包含无效词汇: {', '.join(ineffective_found)}"
        )
    else:
        conciseness_score = 25
    scores["conciseness"] = conciseness_score

    # 2. Searchability (30%)
    if lang == "en":
        first_part = title[:65]
        technical_terms = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b", first_part)
        if len(technical_terms) >= 2:
            searchability_score = 30
        elif len(technical_terms) == 1:
            searchability_score = 20
            issues.append(
                "[Major/重要] Consider placing more key terms in first 65 characters/建议在前65字符内放置更多关键词"
            )
        else:
            searchability_score = 10
            issues.append(
                "[Critical/严重] Key terms should appear in first 65 characters/关键术语应出现在前65字符内"
            )
    else:  # Chinese
        first_20 = title[:20]
        has_method = bool(re.search(r"(Transformer|LSTM|神经网络|深度学习|机器学习)", first_20))
        has_problem = bool(re.search(r"(预测|检测|分类|控制|优化)", first_20))

        if has_method and has_problem:
            searchability_score = 30
        elif has_method or has_problem:
            searchability_score = 20
            issues.append(
                "[Major/重要] Suggest including both method and problem keywords in first 20 chars/建议在前20字内同时包含方法和问题关键词"
            )
        else:
            searchability_score = 10
            issues.append(
                "[Critical/严重] Key terms should appear in first 20 chars/关键术语应出现在前20字内"
            )

    scores["searchability"] = searchability_score

    # 3. Length (15%)
    if lang == "en":
        word_count = len(title.split())
        if 10 <= word_count <= 15:
            length_score = 15
        elif 8 <= word_count <= 20:
            length_score = 10
            issues.append(
                f"[Minor/次要] Length acceptable ({word_count} words) but could be optimized/长度可接受但可优化"
            )
        else:
            length_score = 5
            issues.append(
                f"[Major/重要] Length suboptimal ({word_count} words, target: 10-15)/长度不理想（目标：10-15词）"
            )
    else:  # Chinese
        char_count = count_chinese_chars(title)
        if 15 <= char_count <= 25:
            length_score = 15
        elif 10 <= char_count <= 30:
            length_score = 10
            issues.append(
                f"[Minor/次要] Length acceptable ({char_count} chars) but could be optimized/长度可接受（{char_count}字）但可优化"
            )
        else:
            length_score = 5
            issues.append(
                f"[Major/重要] Length suboptimal ({char_count} chars, target: 15-25)/长度不理想（{char_count}字，建议：15-25字）"
            )

    scores["length"] = length_score

    # 4. Specificity (20%)
    vague_terms = (
        ["method", "approach", "system", "model", "algorithm"]
        if lang == "en"
        else ["方法", "系统", "模型", "算法", "技术"]
    )
    vague_found = sum(1 for term in vague_terms if term in title_lower)
    if vague_found == 0:
        specificity_score = 20
    elif vague_found == 1:
        specificity_score = 15
    else:
        specificity_score = 10
        issues.append(
            "[Major/重要] Title contains vague terms, be more specific/标题包含模糊术语，需更具体"
        )
    scores["specificity"] = specificity_score

    # 5. Jargon-Free (10%)
    words = title.split()
    abbrevs = [w for w in words if w.isupper() and len(w) > 1]
    obscure_abbrevs = [a for a in abbrevs if a not in ACCEPTABLE_ABBREVS]
    if obscure_abbrevs:
        jargon_score = 5
        issues.append(
            f"[Minor/次要] Obscure abbreviations found/发现生僻缩写: {', '.join(obscure_abbrevs)}"
        )
    else:
        jargon_score = 10
    scores["jargon"] = jargon_score

    total_score = sum(scores.values())

    return {"total": total_score, "breakdown": scores, "issues": issues}


def generate_title_candidates(
    keywords: dict[str, list[str]], lang: str, current_title: Optional[str] = None
) -> list[tuple[str, str]]:
    """Generate title candidates based on keywords."""
    candidates = []

    if lang == "en":
        method = keywords.get("method", ["Deep Learning"])[0].title()
        problem = keywords.get("problem", ["Analysis"])[0].title()
        domain = keywords.get("domain", [""])[0].title()

        # Template 1: Method for Problem
        if method and problem:
            title = f"{method} for {problem}"
            if domain:
                title += f" in {domain}"
            candidates.append((title, "method_for_problem"))

        # Template 2: Method: Problem in Domain
        if method and problem and domain:
            title = f"{method}: {problem} in {domain}"
            candidates.append((title, "method_problem_domain"))

        # Template 3: Problem via Method
        if problem and method:
            title = f"{problem} via {method}"
            candidates.append((title, "problem_via_method"))

        # Template 4: Feature + Method
        if method and problem:
            title = f"Lightweight {method} for {problem}"
            candidates.append((title, "method_feature"))

    else:  # Chinese
        method = keywords.get("method", ["深度学习"])[0]
        problem = keywords.get("problem", ["分析"])[0]
        domain = keywords.get("domain", [""])[0]

        # Template 1: 问题的方法
        if method and problem:
            title = f"{problem}的{method}"
            if domain:
                title = f"{domain}{problem}的{method}"
            candidates.append((title, "method_for_problem"))

        # Template 2: 方法及应用
        if method and domain:
            title = f"{method}及其在{domain}中的应用"
            candidates.append((title, "method_application"))

        # Template 3: 面向领域的方法
        if method and problem and domain:
            title = f"面向{domain}的{method}{problem}方法"
            candidates.append((title, "domain_oriented"))

    return candidates


def optimize_title(title: str, lang: str = None) -> str:
    """Optimize existing title by removing ineffective words."""
    if lang is None:
        lang = detect_language(title)

    optimized = title
    ineffective_words = INEFFECTIVE_WORDS_ZH if lang == "zh" else INEFFECTIVE_WORDS_EN

    for word in ineffective_words:
        if lang == "en":
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            optimized = pattern.sub("", optimized)
        else:
            optimized = optimized.replace(word, "")

    # Clean up spaces
    optimized = re.sub(r"\s+", " " if lang == "en" else "", optimized).strip()

    # Remove leading articles (English only)
    if lang == "en":
        optimized = re.sub(r"^(A|An|The)\s+", "", optimized, flags=re.IGNORECASE)

    return optimized


def format_report(
    title: str, score_data: dict, candidates: list[tuple[str, str]] = None, lang: str = "en"
) -> str:
    """Format optimization report."""
    report = []
    report.append("// " + "=" * 60)
    report.append("// TITLE OPTIMIZATION REPORT / 标题优化报告")
    report.append("// " + "=" * 60)
    report.append(f'// Current Title / 当前标题: "{title}"')
    report.append(f"// Quality Score / 质量评分: {score_data['total']}/100")
    report.append("//")

    if score_data["issues"]:
        report.append("// Issues Detected / 检测到的问题:")
        for i, issue in enumerate(score_data["issues"], 1):
            report.append(f"// {i}. {issue}")
        report.append("//")

    if candidates:
        report.append("// Recommended Titles (Ranked) / 推荐标题（按评分排序）:")
        report.append("//")
        for i, (candidate, _template) in enumerate(candidates, 1):
            cand_score = score_title(candidate, lang)
            word_count = len(candidate.split()) if lang == "en" else count_chinese_chars(candidate)
            unit = "words" if lang == "en" else "字"
            report.append(f'// {i}. "{candidate}" [Score/评分: {cand_score["total"]}/100]')
            report.append(
                f"//    - Concise/简洁: {'✅' if cand_score['breakdown']['conciseness'] >= 20 else '⚠️'}"
            )
            report.append(
                f"//    - Searchable/可搜索: {'✅' if cand_score['breakdown']['searchability'] >= 20 else '⚠️'}"
            )
            report.append(
                f"//    - Length/长度: {'✅' if cand_score['breakdown']['length'] >= 10 else '⚠️'} ({word_count} {unit})"
            )
            report.append("//")

    report.append("// Suggested Typst Update / 建议的 Typst 更新:")
    if candidates:
        best_title = candidates[0][0]
        report.append("// #align(center)[")
        report.append('//   #text(size: 18pt, weight: "bold")[')
        report.append(f"//     {best_title}")
        report.append("//   ]")
        report.append("// ]")
    report.append("// " + "=" * 60)

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Optimize Typst paper titles (English/Chinese) following best practices"
    )
    parser.add_argument("typ_file", help="Main .typ file")
    parser.add_argument(
        "--generate", action="store_true", help="Generate title candidates from content"
    )
    parser.add_argument("--optimize", action="store_true", help="Optimize existing title")
    parser.add_argument("--check", action="store_true", help="Check title quality")
    parser.add_argument(
        "--lang", choices=["en", "zh"], help="Force language (auto-detect if not specified)"
    )

    args = parser.parse_args()

    typ_path = Path(args.typ_file)
    if not typ_path.exists():
        print(f"Error/错误: File not found/文件不存在: {typ_path}", file=sys.stderr)
        return 1

    # Extract current title
    with open(typ_path, encoding="utf-8") as f:
        content = f.read()

    current_title = extract_title(content)

    # Detect language
    lang = args.lang
    if not lang and current_title:
        lang = detect_language(current_title)
    elif not lang:
        lang = detect_language(content[:500])

    if args.check or not (args.generate or args.optimize):
        # Check mode (default)
        if not current_title:
            print("Error/错误: No title found/未找到标题", file=sys.stderr)
            return 1

        score_data = score_title(current_title, lang)
        print(format_report(current_title, score_data, lang=lang))

    elif args.generate:
        # Generate mode
        abstract = extract_abstract(content)
        if not abstract:
            print("Warning/警告: No abstract found/未找到摘要", file=sys.stderr)
            abstract = content[:1000]

        keywords = extract_keywords_from_abstract(abstract, lang)
        candidates = generate_title_candidates(keywords, lang, current_title)

        # Score and sort
        scored_candidates = [(c, t, score_title(c, lang)["total"]) for c, t in candidates]
        scored_candidates.sort(key=lambda x: x[2], reverse=True)

        top_candidates = [(c, t) for c, t, s in scored_candidates[:5]]

        if current_title:
            score_data = score_title(current_title, lang)
            print(format_report(current_title, score_data, top_candidates, lang))
        else:
            print("// Generated Title Candidates / 生成的标题候选:")
            for i, (candidate, _template) in enumerate(top_candidates, 1):
                cand_score = score_title(candidate, lang)
                print(f'// {i}. "{candidate}" [Score/评分: {cand_score["total"]}/100]')

    elif args.optimize:
        # Optimize mode
        if not current_title:
            print("Error/错误: No title found/未找到标题", file=sys.stderr)
            return 1

        optimized = optimize_title(current_title, lang)
        score_before = score_title(current_title, lang)
        score_after = score_title(optimized, lang)

        print(f'// Original/原标题: "{current_title}" [Score/评分: {score_before["total"]}/100]')
        print(f'// Optimized/优化后: "{optimized}" [Score/评分: {score_after["total"]}/100]')
        print(f"// Improvement/提升: +{score_after['total'] - score_before['total']} points/分")

    return 0


if __name__ == "__main__":
    sys.exit(main())
