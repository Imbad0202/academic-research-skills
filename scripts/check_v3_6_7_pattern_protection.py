#!/usr/bin/env python3
"""Static audit for ARS v3.6.7 downstream-agent pattern protection.

Spec: docs/design/2026-04-29-ars-v3.6.7-downstream-agent-pattern-protection-spec.md

Greps the v3.6.7 reference files, audit template, and downstream agent prompts
for the keywords that make each pattern-protection clause detectable. Static
only — does not validate runtime behaviour. Behavioural validation belongs to
spec §9 step 8 (live pipeline evaluation case) and is out of scope here.

Exit codes: 0 on pass, 1 on any failure.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REF_DIR = REPO_ROOT / "shared" / "references"
TPL_DIR = REPO_ROOT / "shared" / "templates"
AGENT_DIR = REPO_ROOT / "deep-research" / "agents"

SYNTHESIS_AGENT = AGENT_DIR / "synthesis_agent.md"
ARCHITECT_AGENT = AGENT_DIR / "research_architect_agent.md"
COMPILER_AGENT = AGENT_DIR / "report_compiler_agent.md"


@dataclass
class Check:
    pattern_id: str
    description: str
    target: Path
    must_contain: list[str]
    _needles: list[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Match case-insensitively so Markdown headings ("Primary-source integrity")
        # satisfy a check that names the term in lowercase.
        self._needles = [s.lower() for s in self.must_contain]

    def run(self) -> tuple[bool, str]:
        if not self.target.exists():
            return False, f"target file missing: {self.target.relative_to(REPO_ROOT)}"
        text = self.target.read_text(encoding="utf-8").lower()
        missing = [s for s, n in zip(self.must_contain, self._needles) if n not in text]
        if missing:
            return False, f"missing keywords in {self.target.relative_to(REPO_ROOT)}: {missing}"
        return True, "OK"


def reference_file_checks() -> list[Check]:
    """Spec §7.1 — 4 reference files."""
    return [
        Check(
            pattern_id="REF-1 (B1)",
            description="irb_terminology_glossary covers 4 IRB terms with operational distinctions",
            target=REF_DIR / "irb_terminology_glossary.md",
            must_contain=[
                "Anonymity",
                "Confidentiality",
                "De-identification",
                "Pseudonymization",
            ],
        ),
        Check(
            pattern_id="REF-2 (B2)",
            description="psychometric_terminology_glossary distinguishes true reverse-coded vs contrast",
            target=REF_DIR / "psychometric_terminology_glossary.md",
            must_contain=[
                "true reverse-coded",
                "contrast item",
                "acquiescence",
                "recall bias",
            ],
        ),
        Check(
            pattern_id="REF-3 (C1)",
            description="protected_hedging_phrases defines upstream-marked hedge protocol",
            target=REF_DIR / "protected_hedging_phrases.md",
            must_contain=[
                "protected hedging phrases",
                "upstream calibration",
                "word budget",
            ],
        ),
        Check(
            pattern_id="REF-4 (word-count)",
            description="word_count_conventions specifies whitespace-split + 3-5% buffer",
            target=REF_DIR / "word_count_conventions.md",
            must_contain=[
                "whitespace",
                "split()",
                "3–5%",
                "hyphenated",
            ],
        ),
    ]


def template_file_checks() -> list[Check]:
    """Spec §7.2 — audit prompt template."""
    return [
        Check(
            pattern_id="TPL-1 (D1)",
            description="codex_audit_multifile_template enumerates 7 audit dimensions",
            target=TPL_DIR / "codex_audit_multifile_template.md",
            must_contain=[
                "cross-ref",
                "hallucination",
                "primary-source integrity",
                "internal coherence",
                "instrument quality",
                "Round-N framing",
                "COI adequacy",
            ],
        ),
    ]


def synthesis_agent_checks() -> list[Check]:
    """Spec §6.1 — synthesis_agent A1-A5 protection."""
    must = [
        # Block marker
        "PATTERN PROTECTION (v3.6.7)",
        # A1 — cross-section consistency
        "effect inventory",
        "cross-section consistency",
        # A2 — pending verification hedge
        "pending verification",
        # A3 — anchor justification
        "anchor justification",
        # A4 — quote scope
        "verified phrase boundary",
        # A5 — sibling-document fabrication. The injunction phrase
        # "Declarative claims ... are forbidden" is what distinguishes
        # an actual prohibition from narrative vocabulary about it.
        "declarative claims about un-provided",
        "are forbidden",
    ]
    return [
        Check(
            pattern_id="A1-A5",
            description="synthesis_agent carries 5 narrative-side protection clauses",
            target=SYNTHESIS_AGENT,
            must_contain=must,
        )
    ]


def architect_agent_checks() -> list[Check]:
    """Spec §6.2 — research_architect_agent (survey designer mode) B1-B5 protection."""
    must = [
        "PATTERN PROTECTION (v3.6.7)",
        # B1 — IRB terminology pass-through
        "irb_terminology_glossary.md",
        # B2 — reverse-coded construct equivalence
        "construct-equivalence",
        "reverse-coded",
        # B3 — retrospective event-anchored phrasing
        "event-anchored",
        # B4 — neutral/balanced phrasing
        "neutral",
        "all valences",
        # B5 — primary-source list enumeration
        "primary-source list",
    ]
    return [
        Check(
            pattern_id="B1-B5",
            description="research_architect_agent (survey designer) carries 5 instrument-side protection clauses",
            target=ARCHITECT_AGENT,
            must_contain=must,
        )
    ]


def compiler_agent_checks() -> list[Check]:
    """Spec §6.3 — report_compiler_agent (abstract-only mode) C1-C3 protection."""
    must = [
        "PATTERN PROTECTION (v3.6.7)",
        # C1 — word-count + buffer
        "whitespace-split",
        # Compression hedge protection
        "protected hedging phrases",
        # C2 — temporal disambiguation
        "explicit year range",
        # C3 — anti-fake-audit guard (THE critical clause per feedback_subagent_tool_hallucination.md)
        "DO NOT simulate",
        "DO NOT claim to have run",
    ]
    return [
        Check(
            pattern_id="C1-C3",
            description="report_compiler_agent (abstract-only) carries 3 publication-side protection clauses incl. anti-fake-audit guard",
            target=COMPILER_AGENT,
            must_contain=must,
        )
    ]


def all_checks() -> list[Check]:
    return [
        *reference_file_checks(),
        *template_file_checks(),
        *synthesis_agent_checks(),
        *architect_agent_checks(),
        *compiler_agent_checks(),
    ]


def main(argv: list[str]) -> int:
    checks = all_checks()
    passed: list[Check] = []
    failed: list[tuple[Check, str]] = []

    for check in checks:
        ok, msg = check.run()
        if ok:
            passed.append(check)
        else:
            failed.append((check, msg))

    summary = f"v3.6.7 pattern-protection static audit: {len(passed)}/{len(checks)} checks passed"
    print(summary)
    print()

    if passed:
        print("PASS:")
        for c in passed:
            print(f"  [{c.pattern_id}] {c.description}")
        print()

    if failed:
        # Failures go to stderr so CI harnesses that route stderr to a failure
        # channel (matching scripts/check_corpus_consumer_protocol.py) surface
        # the diagnostics correctly.
        print("FAIL:", file=sys.stderr)
        for c, msg in failed:
            print(f"  [{c.pattern_id}] {c.description}", file=sys.stderr)
            print(f"      → {msg}", file=sys.stderr)
        print(file=sys.stderr)
        print(
            f"{len(failed)} check(s) failed. See spec for protection clause wording:",
            file=sys.stderr,
        )
        print(
            "  docs/design/2026-04-29-ars-v3.6.7-downstream-agent-pattern-protection-spec.md",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
