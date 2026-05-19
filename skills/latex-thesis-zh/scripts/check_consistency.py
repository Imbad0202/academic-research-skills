#!/usr/bin/env python3
"""
Terminology Consistency Checker - Check term usage consistency in thesis

Usage:
    uv run python check_consistency.py main.tex
    uv run python check_consistency.py main.tex --terms
    uv run python check_consistency.py main.tex --abbreviations
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path


class ConsistencyChecker:
    """Check terminology and abbreviation consistency across thesis files."""

    # Built-in example term groups (common CS/AI terms)
    DEFAULT_TERM_GROUPS_ZH = [
        ["深度学习", "深度神经网络", "深层学习"],
        ["机器学习", "机器智能"],
        ["卷积神经网络", "卷积网络", "CNN"],
        ["循环神经网络", "递归神经网络", "RNN"],
        ["长短期记忆", "LSTM"],
        ["生成对抗网络", "GAN"],
        ["自然语言处理", "NLP"],
        ["计算机视觉", "CV"],
        ["强化学习", "RL"],
    ]

    DEFAULT_TERM_GROUPS_EN = [
        ["deep learning", "deep neural network"],
        ["machine learning", "ML"],
        ["convolutional neural network", "CNN"],
        ["recurrent neural network", "RNN"],
        ["long short-term memory", "LSTM"],
        ["generative adversarial network", "GAN"],
        ["natural language processing", "NLP"],
    ]

    def __init__(self, tex_files: list[str], custom_terms_file: str | None = None):
        self.tex_files = [Path(f).resolve() for f in tex_files]
        self.content_cache: dict[Path, str] = {}
        self.term_groups_zh = list(self.DEFAULT_TERM_GROUPS_ZH)
        self.term_groups_en = list(self.DEFAULT_TERM_GROUPS_EN)
        if custom_terms_file:
            self._load_custom_terms(custom_terms_file)

    def _load_custom_terms(self, path: str) -> None:
        """Load custom term groups from a JSON file.

        Expected format: {"zh": [["termA", "termB"], ...], "en": [["termC", "termD"], ...]}
        """
        import json

        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if "zh" in data:
                self.term_groups_zh.extend(data["zh"])
            if "en" in data:
                self.term_groups_en.extend(data["en"])
        except Exception as e:
            print(f"[WARNING] Failed to load custom terms: {e}", file=sys.stderr)

    def _load_content(self, tex_file: Path) -> str:
        """Load and cache file content."""
        if tex_file not in self.content_cache:
            try:
                self.content_cache[tex_file] = tex_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                self.content_cache[tex_file] = ""
        return self.content_cache[tex_file]

    def check_terms(self) -> dict:
        """Check term consistency across files."""
        term_occurrences: dict[str, list[tuple[str, int]]] = defaultdict(list)

        for tex_file in self.tex_files:
            content = self._load_content(tex_file)
            if not content:
                continue

            # Check each term group
            all_groups = self.term_groups_zh + self.term_groups_en

            for group in all_groups:
                for term in group:
                    # Find all occurrences
                    pattern = re.escape(term)
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        for match in matches:
                            # Find line number
                            line_num = content[: match.start()].count("\n") + 1
                            term_occurrences[term].append((str(tex_file.name), line_num))

        # Find inconsistencies
        inconsistencies = []
        checked_groups: set[frozenset] = set()

        all_groups = self.term_groups_zh + self.term_groups_en

        for group in all_groups:
            group_set = frozenset(group)
            if group_set in checked_groups:
                continue
            checked_groups.add(group_set)

            found_terms = {}
            for term in group:
                if term in term_occurrences:
                    found_terms[term] = len(term_occurrences[term])

            if len(found_terms) > 1:
                # Multiple variants used
                most_common = max(found_terms.items(), key=lambda x: x[1])
                inconsistencies.append(
                    {
                        "group": list(found_terms.keys()),
                        "counts": found_terms,
                        "suggestion": f"统一使用 '{most_common[0]}'",
                    }
                )

        return {
            "term_occurrences": {k: len(v) for k, v in term_occurrences.items()},
            "inconsistencies": inconsistencies,
            "status": "PASS" if not inconsistencies else "WARNING",
        }

    def check_abbreviations(self) -> dict:
        """Check abbreviation definitions and usage."""
        # Pattern for abbreviation definition: 全称（缩写）or 全称 (abbreviation)
        definition_pattern = r"([^（(]+)[（(]([A-Z]{2,})[）)]"

        definitions: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
        usages: dict[str, list[tuple[str, int]]] = defaultdict(list)

        for tex_file in self.tex_files:
            content = self._load_content(tex_file)
            if not content:
                continue

            # Find definitions
            for match in re.finditer(definition_pattern, content):
                full_name = match.group(1).strip()
                abbrev = match.group(2)
                line_num = content[: match.start()].count("\n") + 1
                definitions[abbrev].append((full_name, str(tex_file.name), line_num))

            # Find standalone abbreviation usages
            # Look for uppercase sequences that might be abbreviations
            abbrev_pattern = r"\b([A-Z]{2,})\b"
            for match in re.finditer(abbrev_pattern, content):
                abbrev = match.group(1)
                # Skip common non-abbreviation uppercase
                if abbrev in ["PDF", "URL", "HTTP", "HTTPS", "API", "TODO", "FIXME"]:
                    continue
                line_num = content[: match.start()].count("\n") + 1
                usages[abbrev].append((str(tex_file.name), line_num))

        # Find issues
        issues = []

        # Abbreviations used but not defined
        for abbrev, usage_list in usages.items():
            if abbrev not in definitions and len(usage_list) > 0:
                first_usage = usage_list[0]
                issues.append(
                    {
                        "type": "undefined",
                        "abbreviation": abbrev,
                        "first_usage": first_usage,
                        "usage_count": len(usage_list),
                        "message": f"'{abbrev}' used but not defined (first at {first_usage[0]}:{first_usage[1]})",
                    }
                )

        # Abbreviations defined multiple times
        for abbrev, def_list in definitions.items():
            if len(def_list) > 1:
                issues.append(
                    {
                        "type": "multiple_definitions",
                        "abbreviation": abbrev,
                        "definitions": def_list,
                        "message": f"'{abbrev}' defined {len(def_list)} times",
                    }
                )

        return {
            "definitions": {k: len(v) for k, v in definitions.items()},
            "usages": {k: len(v) for k, v in usages.items()},
            "issues": issues,
            "status": "PASS" if not issues else "WARNING",
        }

    def generate_report(self, terms_result: dict, abbrev_result: dict) -> str:
        """Generate human-readable report."""
        lines = []
        lines.append("=" * 60)
        lines.append("Consistency Check Report / 一致性检查报告")
        lines.append("=" * 60)

        # Term consistency
        lines.append("\n[1] Term Consistency / 术语一致性")
        lines.append("-" * 40)

        if terms_result["inconsistencies"]:
            lines.append(f"Status: ⚠️ {len(terms_result['inconsistencies'])} inconsistencies found")
            for inc in terms_result["inconsistencies"]:
                lines.append(f"\n  Group: {', '.join(inc['group'])}")
                for term, count in inc["counts"].items():
                    lines.append(f"    - '{term}': {count} times")
                lines.append(f"  Suggestion: {inc['suggestion']}")
        else:
            lines.append("Status: ✅ No inconsistencies found")

        # Abbreviation check
        lines.append("\n[2] Abbreviation Check / 缩略语检查")
        lines.append("-" * 40)

        if abbrev_result["issues"]:
            lines.append(f"Status: ⚠️ {len(abbrev_result['issues'])} issues found")
            for issue in abbrev_result["issues"]:
                lines.append(f"\n  [{issue['type']}] {issue['message']}")
        else:
            lines.append("Status: ✅ All abbreviations properly defined")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


def find_tex_files(main_file: str) -> list[str]:
    """Find all .tex files in the project."""
    main_path = Path(main_file).resolve()
    root_dir = main_path.parent

    # Find all .tex files
    tex_files = list(root_dir.rglob("*.tex"))

    # Also check common subdirectories
    for subdir in ["data", "chapters", "sections", "content"]:
        subdir_path = root_dir / subdir
        if subdir_path.exists():
            tex_files.extend(subdir_path.rglob("*.tex"))

    # Remove duplicates and sort
    tex_files = sorted(set(tex_files))

    return [str(f) for f in tex_files]


def main():
    parser = argparse.ArgumentParser(description="Terminology Consistency Checker")
    parser.add_argument("tex_file", help="Main .tex file or directory")
    parser.add_argument("--terms", "-t", action="store_true", help="Check only term consistency")
    parser.add_argument(
        "--abbreviations", "-a", action="store_true", help="Check only abbreviation consistency"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")
    parser.add_argument("--custom-terms", type=str, help="JSON file with custom term groups")

    args = parser.parse_args()

    # Find tex files
    if Path(args.tex_file).is_dir():
        tex_files = [str(p) for p in Path(args.tex_file).rglob("*.tex")]
    else:
        if not Path(args.tex_file).exists():
            print(f"[ERROR] File not found: {args.tex_file}", file=sys.stderr)
            sys.exit(1)
        tex_files = find_tex_files(args.tex_file)

    if not tex_files:
        print("[ERROR] No .tex files found", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Checking {len(tex_files)} files...")

    # Run checks
    checker = ConsistencyChecker(tex_files, custom_terms_file=args.custom_terms)

    if args.terms:
        result = checker.check_terms()
        if args.json:
            import json

            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\nTerm consistency: {result['status']}")
            for inc in result["inconsistencies"]:
                print(f"  - {inc['suggestion']}")
        sys.exit(0)

    if args.abbreviations:
        result = checker.check_abbreviations()
        if args.json:
            import json

            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\nAbbreviation check: {result['status']}")
            for issue in result["issues"]:
                print(f"  - {issue['message']}")
        sys.exit(0)

    # Full check
    terms_result = checker.check_terms()
    abbrev_result = checker.check_abbreviations()

    if args.json:
        import json

        output = {
            "terms": terms_result,
            "abbreviations": abbrev_result,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(checker.generate_report(terms_result, abbrev_result))

    # Exit code
    if terms_result["status"] != "PASS" or abbrev_result["status"] != "PASS":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
