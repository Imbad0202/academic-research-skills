#!/usr/bin/env python3
"""
Abstract Structure Analyzer - Diagnose five-element abstract completeness.

Usage:
    uv run python -B analyze_abstract.py main.tex
    uv run python -B analyze_abstract.py main.tex --lang en --max-words 250
    uv run python -B analyze_abstract.py main.tex --lang zh --max-chars 300
    uv run python -B analyze_abstract.py main.tex --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

from parsers import extract_abstract


class AbstractAnalyzer:
    """Analyze abstract structure against the five-element model."""

    STATUS_PRESENT = "PRESENT"
    STATUS_VAGUE = "VAGUE"
    STATUS_MISSING = "MISSING"

    # Detection markers per element
    MARKERS_EN = {
        "background": [
            r"\bhowever\b",
            r"\bremains?\s+unclear\b",
            r"\blimited\s+research\b",
            r"\bgrowing\s+interest\b",
            r"\bchalleng\w*\b",
            r"\bgap\b",
            r"\bdespite\b",
            r"\blittle\s+is\s+known\b",
            r"\bincreasingly\s+important\b",
            r"\bproblem\b",
            r"\bmotivat\w+\b",
            r"\bcrucial\b",
            r"\bcritical\b",
        ],
        "objective": [
            r"\bthis\s+(?:study|paper|work|research)\s+(?:aims?|presents?|proposes?|investigates?|examines?|addresses?|introduces?)\b",
            r"\bwe\s+(?:investigate|propose|present|introduce|address|examine|aim)\b",
            r"\bthe\s+purpose\s+of\b",
            r"\bour\s+goal\b",
            r"\bin\s+this\s+(?:paper|work|study)\b",
            r"\bwe\s+aim\s+to\b",
            r"\bthe\s+objective\b",
        ],
        "methods": [
            r"\bwe\s+propose\b",
            r"\busing\b",
            r"\bdataset\b",
            r"\bparticipants?\b",
            r"\bmethod\b",
            r"\bapproach\b",
            r"\bframework\b",
            r"\bmodel\b",
            r"\balgorithm\b",
            r"\bcollect\w*\b",
            r"\btrain\w*\b",
            r"\bevaluat\w*\b",
            r"\bsample\b",
            r"\bexperiment\w*\b",
            r"\bimplement\w*\b",
            r"\bsurve[ys]\w*\b",
            r"\banalysi[sz]\b",
            r"\bsimulat\w*\b",
        ],
        "results": [
            r"\bresults?\s+show\b",
            r"\bachiev\w*\b",
            r"\boutperform\w*\b",
            r"\baccuracy\b",
            r"\bimprov\w*\b",
            r"\breduc\w*\b",
            r"\bfound\s+that\b",
            r"\bdemonstr\w*\b",
            r"\bsignificant\w*\b",
            r"\bF1\b",
            r"\bprecision\b",
            r"\brecall\b",
            r"\bAUC\b",
            r"\bBLEU\b",
        ],
        "conclusion": [
            r"\bour\s+findings?\s+suggest\b",
            r"\bcontribut\w*\b",
            r"\bimplication\w*\b",
            r"\bcan\s+be\s+used\b",
            r"\benabl\w*\b",
            r"\bprovid\w*\b",
            r"\badvance\w*\b",
            r"\bpotential\b",
            r"\bfuture\s+work\b",
            r"\bpromising\b",
        ],
    }

    MARKERS_ZH = {
        "background": [
            r"然而",
            r"尚不清楚",
            r"研究不足",
            r"日益增长",
            r"挑战",
            r"空白",
            r"尽管",
            r"鲜有研究",
            r"亟需",
            r"问题",
            r"随着",
            r"近年来",
        ],
        "objective": [
            r"本文旨在",
            r"本研究探讨",
            r"本文提出",
            r"研究目的",
            r"为此",
            r"本工作",
            r"本文研究",
            r"旨在",
            r"目的是",
            r"针对",
        ],
        "methods": [
            r"采用",
            r"方法",
            r"数据集",
            r"样本",
            r"模型",
            r"算法",
            r"框架",
            r"实验",
            r"训练",
            r"评估",
            r"构建",
            r"设计",
            r"基于",
        ],
        "results": [
            r"结果表明",
            r"达到",
            r"优于",
            r"准确率",
            r"提高",
            r"降低",
            r"发现",
            r"显著",
            r"表现",
            r"性能",
        ],
        "conclusion": [
            r"研究发现表明",
            r"为.*提供",
            r"有助于",
            r"具有.*意义",
            r"可用于",
            r"推动",
            r"贡献",
            r"展望",
            r"未来",
        ],
    }

    # Vague patterns — signs that an element is present but weak
    VAGUE_PATTERNS_EN = {
        "objective": [
            r"\bwe\s+study\b(?!\s+(?:how|whether|the\s+effect))",
            r"\bthis\s+paper\s+is\s+about\b",
        ],
        "results": [
            r"\bperforms?\s+well\b",
            r"\beffective\b(?!.*\d)",
            r"\bgood\s+results?\b(?!.*\d)",
        ],
        "conclusion": [
            # Conclusion that just echoes results without adding implications
        ],
    }

    def __init__(
        self,
        tex_file: str,
        lang: str = "auto",
        max_words: int = 250,
        max_chars: int = 300,
    ):
        self.tex_file = Path(tex_file).resolve()
        self.lang = lang
        self.max_words = max_words
        self.max_chars = max_chars

    def analyze(self) -> dict:
        """Run the full abstract structure analysis."""
        if not self.tex_file.exists():
            return {
                "status": "ERROR",
                "message": f"File not found: {self.tex_file}",
                "elements": {},
            }

        content = self.tex_file.read_text(encoding="utf-8", errors="replace")
        abstract_text = extract_abstract(content)

        if not abstract_text.strip():
            return {
                "status": "ERROR",
                "message": "No abstract found in document.",
                "elements": {},
            }

        # Detect language
        lang = self.lang
        if lang == "auto":
            lang = self._detect_lang(abstract_text)

        # Split into sentences
        sentences = self._split_sentences(abstract_text, lang)

        # Analyze each element
        markers = self.MARKERS_ZH if lang == "zh" else self.MARKERS_EN
        vague_patterns = {} if lang == "zh" else self.VAGUE_PATTERNS_EN

        elements = {}
        for element_name in ["background", "objective", "methods", "results", "conclusion"]:
            elements[element_name] = self._analyze_element(
                element_name,
                sentences,
                markers.get(element_name, []),
                vague_patterns.get(element_name, []),
                lang,
            )

        # Word/char count
        count_info = self._check_count(abstract_text, lang)

        # Overall status
        statuses = [e["status"] for e in elements.values()]
        if self.STATUS_MISSING in statuses:
            overall = "FAIL"
        elif self.STATUS_VAGUE in statuses:
            overall = "WARNING"
        else:
            overall = "PASS"

        return {
            "status": overall,
            "file": str(self.tex_file),
            "language": lang,
            "elements": elements,
            "count": count_info,
        }

    def _detect_lang(self, text: str) -> str:
        """Detect language from text content."""
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        total_chars = len(text.strip())
        if total_chars == 0:
            return "en"
        return "zh" if chinese_chars / total_chars > 0.3 else "en"

    def _split_sentences(self, text: str, lang: str) -> list[str]:
        """Split text into sentences."""
        if lang == "zh":
            # Split on Chinese sentence-ending punctuation
            parts = re.split(r"([。！？；])", text)
            sentences = []
            for i in range(0, len(parts) - 1, 2):
                sent = parts[i] + (parts[i + 1] if i + 1 < len(parts) else "")
                sent = sent.strip()
                if sent:
                    sentences.append(sent)
            # Handle trailing text
            if len(parts) % 2 == 1 and parts[-1].strip():
                sentences.append(parts[-1].strip())
            return sentences if sentences else [text]
        else:
            # English: split on period/question/exclamation followed by space or end
            raw = re.split(r"(?<=[.!?])\s+", text)
            return [s.strip() for s in raw if s.strip()]

    def _analyze_element(
        self,
        element_name: str,
        sentences: list[str],
        markers: list[str],
        vague_patterns: list[str],
        lang: str,
    ) -> dict:
        """Analyze a single structural element."""
        matched_sentences = []
        for sent in sentences:
            for marker in markers:
                if re.search(marker, sent, re.IGNORECASE):
                    matched_sentences.append(sent)
                    break

        if not matched_sentences:
            return {
                "status": self.STATUS_MISSING,
                "evidence": "",
                "suggestion": self._get_suggestion(element_name, self.STATUS_MISSING, lang),
            }

        # Check for vagueness
        is_vague = False
        for sent in matched_sentences:
            for pattern in vague_patterns:
                if re.search(pattern, sent, re.IGNORECASE):
                    is_vague = True
                    break

        # Special check: results must contain numbers
        if element_name == "results":
            has_numbers = False
            for sent in matched_sentences:
                if re.search(r"\d+\.?\d*\s*[%‰]?", sent):
                    has_numbers = True
                    break
            if not has_numbers:
                is_vague = True

        # Pick the best evidence sentence (first match)
        evidence = matched_sentences[0]
        if len(evidence) > 120:
            evidence = evidence[:117] + "..."

        if is_vague:
            return {
                "status": self.STATUS_VAGUE,
                "evidence": evidence,
                "suggestion": self._get_suggestion(element_name, self.STATUS_VAGUE, lang),
            }

        return {
            "status": self.STATUS_PRESENT,
            "evidence": evidence,
            "suggestion": "",
        }

    def _get_suggestion(self, element: str, status: str, lang: str) -> str:
        """Get improvement suggestion for an element."""
        suggestions = {
            "en": {
                "background": {
                    "MISSING": "Add 1-2 sentences establishing the research context and knowledge gap.",
                    "VAGUE": "Sharpen the background: identify the specific gap this work addresses.",
                },
                "objective": {
                    "MISSING": "Add a sentence starting with 'This study aims to...' or 'We investigate...'",
                    "VAGUE": "Specify the research question: what exactly are you testing or proposing?",
                },
                "methods": {
                    "MISSING": "Describe the core methodology, data source, and evaluation approach.",
                    "VAGUE": "Name the specific technique, dataset, or experimental setup used.",
                },
                "results": {
                    "MISSING": "Report at least one key finding with a concrete number or comparison.",
                    "VAGUE": "Add quantitative evidence: accuracy, improvement percentage, or effect size.",
                },
                "conclusion": {
                    "MISSING": "Add a sentence on the broader significance or practical implications.",
                    "VAGUE": "Go beyond restating results: what does this mean for the field or practice?",
                },
            },
            "zh": {
                "background": {
                    "MISSING": "添加1-2句研究背景，明确研究领域的知识空白或现实需求。",
                    "VAGUE": "细化背景描述：指出本研究要解决的具体问题。",
                },
                "objective": {
                    "MISSING": "添加以'本文旨在...'或'本研究探讨...'开头的研究目标句。",
                    "VAGUE": "明确研究问题：具体要验证什么假设或解决什么问题?",
                },
                "methods": {
                    "MISSING": "描述核心方法、数据来源和评估方式。",
                    "VAGUE": "指明具体的技术手段、数据集或实验设置。",
                },
                "results": {
                    "MISSING": "报告至少一项包含具体数值的关键发现。",
                    "VAGUE": "补充定量证据：准确率、提升百分比或效果量。",
                },
                "conclusion": {
                    "MISSING": "补充研究的理论意义或实践价值。",
                    "VAGUE": "超越结果复述，阐明对领域或实践的启示。",
                },
            },
        }
        lang_key = "zh" if lang == "zh" else "en"
        return suggestions.get(lang_key, {}).get(element, {}).get(status, "")

    def _check_count(self, text: str, lang: str) -> dict:
        """Check word/character count against limits."""
        if lang == "zh":
            # Count Chinese characters (excluding punctuation and spaces)
            chars = len(re.findall(r"[\u4e00-\u9fff]", text))
            return {
                "type": "characters",
                "count": chars,
                "limit": {"min": 200, "max": self.max_chars},
                "status": "PASS" if 200 <= chars <= self.max_chars else "WARNING",
            }
        else:
            words = len(text.split())
            return {
                "type": "words",
                "count": words,
                "limit": {"min": 150, "max": self.max_words},
                "status": "PASS" if 150 <= words <= self.max_words else "WARNING",
            }

    def generate_report(self, result: dict) -> str:
        """Generate human-readable diagnostic report."""
        lines = []
        lines.append("=" * 60)
        lines.append("Abstract Structure Diagnosis")
        lines.append("=" * 60)
        lines.append(f"File: {result.get('file', 'N/A')}")
        lines.append(f"Language: {result.get('language', 'N/A')}")
        lines.append(f"Status: {result['status']}")

        if result["status"] == "ERROR":
            lines.append(f"Error: {result.get('message', '')}")
            return "\n".join(lines)

        lines.append("")
        lines.append("-" * 60)
        lines.append("Element Diagnosis")
        lines.append("-" * 60)

        icons = {
            self.STATUS_PRESENT: "PRESENT ",
            self.STATUS_VAGUE: "VAGUE   ",
            self.STATUS_MISSING: "MISSING ",
        }

        element_labels = {
            "background": "Background",
            "objective": "Objective",
            "methods": "Methods",
            "results": "Results",
            "conclusion": "Conclusion",
        }

        for key in ["background", "objective", "methods", "results", "conclusion"]:
            elem = result["elements"].get(key, {})
            status = elem.get("status", self.STATUS_MISSING)
            label = element_labels[key]
            icon = icons.get(status, "???")

            lines.append(f"\n  {label:12s}: [{icon}]")
            if elem.get("evidence"):
                ev = elem["evidence"]
                lines.append(f'    Evidence: "{ev}"')
            if elem.get("suggestion"):
                lines.append(f"    Suggestion: {elem['suggestion']}")

        # Word count
        count = result.get("count", {})
        if count:
            lines.append("")
            lines.append("-" * 60)
            ctype = count.get("type", "words")
            cval = count.get("count", 0)
            lim = count.get("limit", {})
            cstatus = count.get("status", "N/A")
            lines.append(
                f"  {ctype.capitalize()}: {cval} "
                f"(limit: {lim.get('min', '?')}–{lim.get('max', '?')}) "
                f"[{cstatus}]"
            )

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Abstract Structure Analyzer - five-element diagnosis"
    )
    parser.add_argument("tex_file", help=".tex or .typ file to analyze")
    parser.add_argument(
        "--lang",
        choices=["en", "zh", "auto"],
        default="auto",
        help="Abstract language (default: auto-detect)",
    )
    parser.add_argument(
        "--max-words", type=int, default=250, help="Max word count for EN (default: 250)"
    )
    parser.add_argument(
        "--max-chars", type=int, default=300, help="Max char count for ZH (default: 300)"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if not Path(args.tex_file).exists():
        print(f"[ERROR] File not found: {args.tex_file}")
        sys.exit(1)

    analyzer = AbstractAnalyzer(
        args.tex_file,
        lang=args.lang,
        max_words=args.max_words,
        max_chars=args.max_chars,
    )
    result = analyzer.analyze()

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(analyzer.generate_report(result))

    sys.exit(1 if result["status"] == "ERROR" else 0)


if __name__ == "__main__":
    main()
