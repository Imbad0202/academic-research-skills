#!/usr/bin/env python3
"""
Venue reporting checklist auditor.

Checks whether a LaTeX paper contains the venue-required disclosure
statements (Limitations, Broader Impact, Reproducibility, Ethics, Compute
resources, IRB, etc.) that go beyond language and formatting.

Data source of truth: ../references/REPORTING_CHECKLISTS.md
Keep VENUE_CHECKLISTS below aligned when updating the markdown table.

Usage:
    uv run python -B check_reporting.py main.tex --venue neurips
    uv run python -B check_reporting.py main.tex --venue acl --json
    uv run python -B check_reporting.py main.tex --venue iclr --strict
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Reuse the shared parser factory (matches the import pattern of analyze_*.py).
try:
    from parsers import get_parser
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from parsers import get_parser

POLICY_URLS = {
    "neurips": "https://neurips.cc/public/guides/PaperChecklist",
    "icml": "https://icml.cc/Conferences/2024/PublicationEthics",
    "iclr": "https://iclr.cc/Conferences/2025/AuthorGuide",
    "acl": "https://aclrollingreview.org/responsibleNLPresearch/",
    "chi": "https://chi2025.acm.org/submission-guides/chi-publication-policies/",
    "acm": "https://www.acm.org/publications/policies/artifact-review-and-badging-current",
    "ieee": "https://journals.ieeeauthorcenter.ieee.org/",
    "springer-lncs": "https://www.springer.com/gp/computer-science/lncs",
}

# Each item: (item_id, severity, [regex patterns])
# severity in {"CRITICAL", "MAJOR", "MINOR"}.
# Patterns use case-insensitive search on visible prose.
VENUE_CHECKLISTS: dict[str, list[tuple[str, str, list[str]]]] = {
    "neurips": [
        (
            "Limitations statement",
            "CRITICAL",
            [
                r"\\section\*?\{[^}]*Limitation",
                r"limitations of (our|this) (work|study|approach|method)",
                r"we (acknowledge|note|discuss) (the following |several )?limitation",
            ],
        ),
        (
            "Broader / societal impact",
            "CRITICAL",
            [
                r"\\section\*?\{[^}]*(Broader Impact|Societal Impact|Impact Statement)",
                r"broader impact",
                r"societal (impact|consequences)",
            ],
        ),
        (
            "Reproducibility statement",
            "CRITICAL",
            [
                r"\\section\*?\{[^}]*Reproducib",
                r"reproducibility (statement|checklist)",
                r"to (ensure|support) reproducibility",
            ],
        ),
        (
            "Compute resources disclosure",
            "MAJOR",
            [
                r"compute (resources|budget)",
                r"(GPU|TPU)[- ]hours",
                r"trained on \d+\s*(GPU|TPU)",
                r"wall[- ]?clock time",
            ],
        ),
        (
            "Safeguards for high-risk artifacts",
            "MAJOR",
            [
                r"safeguard",
                r"release (policy|plan)",
                r"responsible (release|disclosure)",
            ],
        ),
        (
            "Code / data availability",
            "MAJOR",
            [
                r"(code|data) (is|are|will be) (available|released|provided)",
                r"https?://github\.com/",
                r"anonymous (github|repository)",
            ],
        ),
        (
            "Licenses for assets",
            "MINOR",
            [r"\bMIT\b", r"Apache 2", r"CC[- ]BY", r"license:"],
        ),
        (
            "Crowdsourcing / human subjects",
            "MINOR",
            [
                r"\bIRB\b",
                r"institutional review board",
                r"crowdworker (compensation|wage)",
                r"informed consent",
            ],
        ),
    ],
    "icml": [
        ("Limitations statement", "CRITICAL", [r"\\section\*?\{[^}]*Limitation", r"limitations of (our|this) (work|study|approach)"]),
        ("Broader impact discussion", "MAJOR", [r"broader impact", r"societal (impact|consequences)", r"ethical (consideration|implication)"]),
        ("Reproducibility: code release", "CRITICAL", [r"(code|implementation) (is|will be) (available|released)", r"https?://github\.com/", r"anonymous repository"]),
        ("Reproducibility: data details", "CRITICAL", [r"dataset (statistics|split|preprocessing)", r"train(ing)?[/ ]val(idation)?[/ ]test split", r"data preprocessing"]),
        ("Reproducibility: hyperparameters", "CRITICAL", [r"hyper[- ]?parameter", r"learning rate", r"batch size", r"random seed"]),
        ("Reproducibility: compute", "MAJOR", [r"(GPU|TPU)[- ]hours", r"trained on \d+\s*(GPU|TPU)", r"compute (resources|budget)"]),
        ("Error bars / variance reporting", "MAJOR", [r"error bar", r"confidence interval", r"standard deviation", r"\\pm\s*\d", r"over \d+\s*(runs|seeds)"]),
        ("Statistical significance", "MINOR", [r"statistical(ly)? significan", r"p[- ]value", r"t[- ]test", r"Wilcoxon"]),
    ],
    "iclr": [
        ("Reproducibility statement", "CRITICAL", [r"\\section\*?\{[^}]*Reproducib", r"reproducibility statement"]),
        ("Ethics statement", "CRITICAL", [r"\\section\*?\{[^}]*Ethic", r"ethics statement", r"ethical consideration"]),
        ("Code release", "MAJOR", [r"(code|implementation) (is|will be) (available|released)", r"https?://github\.com/", r"anonymous (github|repository)"]),
        ("Compute resources", "MAJOR", [r"(GPU|TPU)[- ]hours", r"trained on \d+\s*(GPU|TPU)"]),
        ("Hyperparameters in appendix", "MAJOR", [r"(see|in) (the|our)?\s*[Aa]ppendix", r"hyper[- ]?parameter", r"Table \d.*hyper"]),
    ],
    "acl": [
        ("Limitations section (mandatory, not in page count)", "CRITICAL", [r"\\section\*?\{Limitations?\}", r"\\section\*?\{[^}]*Limitation"]),
        ("Ethics / risks discussion", "CRITICAL", [r"\\section\*?\{[^}]*Ethic", r"ethics statement", r"potential risk", r"misuse"]),
        ("Use of AI assistants disclosure", "MAJOR", [r"AI (assistant|writing tool)", r"ChatGPT|GPT[- ]?4|Claude|Gemini", r"(was|were) used (to|for) (assist|help|polish)"]),
        ("Computational budget", "MAJOR", [r"(GPU|TPU)[- ]hours", r"trained on \d+\s*(GPU|TPU)", r"compute (budget|cost)", r"inference (cost|time)"]),
        ("Hyperparameter search", "MAJOR", [r"hyper[- ]?parameter (search|tuning|sweep)", r"grid search", r"Bayesian optimization", r"best validation"]),
        ("Dataset documentation", "MAJOR", [r"dataset (card|statistics|description)", r"train(ing)?[/ ]val(idation)?[/ ]test", r"data preprocessing", r"data collection"]),
        ("Licenses of artifacts used", "MAJOR", [r"license:", r"\bMIT\b", r"Apache 2", r"CC[- ]BY", r"dataset license"]),
        ("Demographic / annotator information", "MINOR", [r"annotator (demographic|background|compensation)", r"crowdworker", r"\bIRB\b", r"informed consent"]),
    ],
    "chi": [
        ("IRB / ethics approval for human subjects", "CRITICAL", [r"\bIRB\b", r"institutional review board", r"ethics (committee|approval)", r"approved by"]),
        ("Informed consent", "CRITICAL", [r"informed consent", r"participants (consented|gave consent)"]),
        ("Participant compensation", "MAJOR", [r"(compensated|paid) (participants|with)", r"\$\d+\s*(per hour|/hr)", r"gift card", r"compensation"]),
        ("Demographic reporting", "MAJOR", [r"(age|gender|ethnicity) of (participants|the sample)", r"participant demographic", r"Mage\s*=", r"participants \(N\s*="]),
        ("Data handling / privacy", "MAJOR", [r"anonymi[sz]ed", r"pseudonym", r"data (storage|handling|retention)", r"GDPR"]),
        ("Positionality / reflexivity (qualitative)", "MINOR", [r"positionality", r"reflexivity", r"our (background|perspective)"]),
    ],
    "acm": [
        ("Artifact availability statement", "MAJOR", [r"artifact (is|will be) (available|published)", r"https?://zenodo\.org/", r"https?://figshare\.com/", r"DOI:\s*10\."]),
        ("Reproducibility instructions", "MAJOR", [r"(see|in) the (artifact|README)", r"to reproduce", r"README\.md", r"install instructions"]),
        ("Conflict of interest", "MINOR", [r"conflict of interest", r"competing interest", r"the authors declare"]),
        ("Funding disclosure", "MINOR", [r"funded by", r"supported (in part|by) (grant|award)", r"grant (number|no)\.?\s*\w"]),
    ],
    "ieee": [
        ("Data availability statement", "MAJOR", [r"data (availability|sharing) statement", r"(data|code) (is|are|will be) (available|released)"]),
        ("Conflict of interest", "MAJOR", [r"conflict of interest", r"competing interest", r"the authors declare (no|the following)"]),
        ("Funding statement", "MAJOR", [r"funded by", r"supported (in part|by)", r"grant (number|no)\.?\s*\w"]),
        ("Ethical approval (if human / animal subjects)", "MAJOR", [r"\bIRB\b", r"ethics (committee|approval)", r"animal (care|use) committee"]),
        ("Author contributions (CRediT)", "MINOR", [r"author contribution", r"CRediT", r"\bconceptualization\b", r"\bmethodology\b.*\bvalidation\b"]),
    ],
    "springer-lncs": [
        ("Competing interests", "MAJOR", [r"competing interest", r"conflict of interest", r"the authors declare"]),
        ("Funding statement", "MAJOR", [r"funded by", r"supported (in part|by)", r"grant (number|no)\.?\s*\w"]),
        ("Data availability", "MAJOR", [r"data availability", r"(data|code) (is|are|will be) (available|released)"]),
        ("Ethical approval (if applicable)", "MAJOR", [r"\bIRB\b", r"ethics (committee|approval)"]),
    ],
}


def load_tex_prose(tex_path: Path) -> str:
    """Read .tex, strip comments and most markup, return visible prose."""
    content = tex_path.read_text(encoding="utf-8", errors="replace")
    parser = get_parser(tex_path)
    return parser.clean_text(content, keep_structure=True)


def scan_item(prose: str, raw_source: str, patterns: list[str]) -> tuple[bool, str | None]:
    """
    Return (present, matched_pattern_or_None).

    Section-heading patterns (\\section{...}) are matched against raw source;
    prose patterns against cleaned text. This avoids missing \\section
    headings that the parser drops, and avoids false positives in \\cite{}.
    """
    for pat in patterns:
        target = raw_source if pat.startswith(r"\\section") else prose
        if re.search(pat, target, re.IGNORECASE):
            return True, pat
    return False, None


def audit(tex_path: Path, venue: str) -> dict[str, Any]:
    if venue not in VENUE_CHECKLISTS:
        raise ValueError(f"unknown venue: {venue}. choices: {sorted(VENUE_CHECKLISTS)}")

    raw = tex_path.read_text(encoding="utf-8", errors="replace")
    prose = load_tex_prose(tex_path)

    items_out: list[dict[str, Any]] = []
    counts = {"PASS": 0, "MISSING_CRITICAL": 0, "MISSING_MAJOR": 0, "MISSING_MINOR": 0}

    for item_id, severity, patterns in VENUE_CHECKLISTS[venue]:
        present, matched = scan_item(prose, raw, patterns)
        status = "PASS" if present else f"MISSING_{severity}"
        counts[status if present else f"MISSING_{severity}"] += 1
        items_out.append(
            {
                "item": item_id,
                "severity": severity,
                "status": "PASS" if present else "MISSING",
                "matched_pattern": matched,
            }
        )

    return {
        "venue": venue,
        "policy_url": POLICY_URLS.get(venue, ""),
        "summary": counts,
        "items": items_out,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Reporting Checklist Audit — {report['venue']}",
        f"Policy reference: {report['policy_url']}",
        "",
        f"PASS: {report['summary']['PASS']}, "
        f"MISSING-CRITICAL: {report['summary']['MISSING_CRITICAL']}, "
        f"MISSING-MAJOR: {report['summary']['MISSING_MAJOR']}, "
        f"MISSING-MINOR: {report['summary']['MISSING_MINOR']}",
        "",
        "| Status | Severity | Item | Matched pattern |",
        "|---|---|---|---|",
    ]
    for it in report["items"]:
        matched = it["matched_pattern"] or ""
        lines.append(f"| {it['status']} | {it['severity']} | {it['item']} | `{matched}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Audit a LaTeX paper against a venue reporting checklist.")
    p.add_argument("tex_file", help="path to main .tex file")
    p.add_argument("--venue", required=True, choices=sorted(VENUE_CHECKLISTS.keys()))
    p.add_argument("--json", action="store_true", help="output JSON instead of Markdown")
    p.add_argument("--strict", action="store_true", help="exit non-zero on any MAJOR-missing item, not just CRITICAL")
    args = p.parse_args()

    tex_path = Path(args.tex_file).resolve()
    if not tex_path.is_file():
        print(f"error: file not found: {tex_path}", file=sys.stderr)
        return 2

    report = audit(tex_path, args.venue)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report))

    if report["summary"]["MISSING_CRITICAL"] > 0:
        return 1
    if args.strict and report["summary"]["MISSING_MAJOR"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
