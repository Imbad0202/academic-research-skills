#!/usr/bin/env python3
"""Static audit for ARS v3.6.7 downstream-agent pattern protection.

Spec: docs/design/2026-04-29-ars-v3.6.7-downstream-agent-pattern-protection-spec.md

Greps the v3.6.7 reference files, audit template, and downstream agent prompts
for the keywords and obligation phrases that make each pattern-protection
clause detectable. Static only — does not validate runtime behaviour.
Behavioural validation belongs to spec §9 step 8 (live pipeline evaluation
case) and is out of scope here.

Falsifiability discipline (per feedback_lint_passes_but_prompt_silent.md):
- Agent-prompt checks scope grep to the `PATTERN PROTECTION (v3.6.7)` block
  via `block_marker`. A keyword that lands outside the block in unrelated
  prose does not count toward passing.
- Obligation-bearing patterns (forbidden / required / only-if) are enforced
  via `must_contain_regex` so the prohibition is grep-detectable as a
  contiguous fragment, not as two unrelated nouns elsewhere in the file.

Exit codes: 0 on pass, 1 on any failure.
"""

from __future__ import annotations

import re
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

# Markdown heading pattern that closes a `block_marker` scope. A check's scope
# starts at the marker and ends at the next H1/H2/H3 heading or EOF.
_HEADING_RE = re.compile(r"^#{1,3} ", re.MULTILINE)


@dataclass
class Check:
    pattern_id: str
    description: str
    target: Path
    must_contain: list[str] = field(default_factory=list)
    must_contain_regex: list[tuple[str, str]] = field(default_factory=list)
    block_marker: str | None = None
    """If set, scope all keyword/regex checks to the text between the marker
    and the next H1/H2/H3 heading. Use for agent-prompt checks where the
    PATTERN PROTECTION clause must be inside its own block, not scattered
    elsewhere in the file."""

    def _scoped_text(self, full_text: str) -> tuple[str | None, str]:
        """Return (scoped_text, error_message). scoped_text is None on failure."""
        if self.block_marker is None:
            return full_text, ""
        marker_pos = full_text.lower().find(self.block_marker.lower())
        if marker_pos == -1:
            return None, f"block marker missing: {self.block_marker!r}"
        # Find next heading after the marker; scope ends there.
        rest = full_text[marker_pos:]
        match = _HEADING_RE.search(rest, pos=len(self.block_marker))
        scoped_end = marker_pos + (match.start() if match else len(rest))
        return full_text[marker_pos:scoped_end], ""

    def _display_path(self) -> str:
        try:
            return str(self.target.relative_to(REPO_ROOT))
        except ValueError:
            return str(self.target)

    def run(self) -> tuple[bool, str]:
        display = self._display_path()
        if not self.target.exists():
            return False, f"target file missing: {display}"
        full = self.target.read_text(encoding="utf-8")
        scoped, err = self._scoped_text(full)
        if scoped is None:
            return False, f"{display}: {err}"
        scoped_lower = scoped.lower()
        missing_substr = [s for s in self.must_contain if s.lower() not in scoped_lower]
        missing_regex = [
            label
            for label, pattern in self.must_contain_regex
            if not re.search(pattern, scoped, re.IGNORECASE | re.DOTALL)
        ]
        problems = []
        if missing_substr:
            problems.append(f"missing keywords: {missing_substr}")
        if missing_regex:
            problems.append(f"missing obligation phrases: {missing_regex}")
        if problems:
            scope_note = f" within {self.block_marker!r} block" if self.block_marker else ""
            return False, f"{display}{scope_note}: {'; '.join(problems)}"
        return True, "OK"


def reference_file_checks() -> list[Check]:
    """Spec §7.1 — 4 reference files. No block scoping; whole-file grep."""
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


# Block marker every agent-prompt check scopes to. Defined once so the value
# stays in sync across agents.
PROTECTION_BLOCK = "PATTERN PROTECTION (v3.6.7)"


def synthesis_agent_checks() -> list[Check]:
    """Spec §6.1 — synthesis_agent A1-A5 protection.

    Scoped to the PATTERN PROTECTION (v3.6.7) block so keyword presence
    elsewhere in the agent prompt does not count toward passing.
    """
    return [
        Check(
            pattern_id="A1-A5",
            description="synthesis_agent carries 5 narrative-side protection clauses",
            target=SYNTHESIS_AGENT,
            block_marker=PROTECTION_BLOCK,
            must_contain=[
                # A1 — cross-section consistency self-check
                "effect inventory",
                "cross-section consistency",
                # A2 — pending-verification hedge
                "pending verification",
                # A3 — anchor justification
                "anchor justification",
                # A4 — quote scope boundary
                "verified phrase boundary",
            ],
            must_contain_regex=[
                # A5 — declarative claims about un-provided documents must be
                # explicitly forbidden in one contiguous injunction, not split
                # across unrelated clauses.
                (
                    "A5 contiguous injunction",
                    r"declarative claims? about un-provided.{0,300}\bare forbidden\b",
                ),
            ],
        )
    ]


def architect_agent_checks() -> list[Check]:
    """Spec §6.2 — research_architect_agent (survey designer mode) B1-B5 protection."""
    return [
        Check(
            pattern_id="B1-B5",
            description="research_architect_agent (survey designer) carries 5 instrument-side protection clauses",
            target=ARCHITECT_AGENT,
            block_marker=PROTECTION_BLOCK,
            must_contain=[
                # B1 — IRB terminology pass-through (back-pointer to glossary)
                "irb_terminology_glossary.md",
                # B2 — reverse-coded construct equivalence
                "construct-equivalence",
                "reverse-coded",
                # B5 — primary-source list enumeration (named term)
                "primary-source list",
            ],
            must_contain_regex=[
                # B3 — retrospective items default to event-anchored;
                # calendar-anchored is conditional on a shared event date.
                (
                    "B3 retrospective default + calendar conditional",
                    r"event-anchored.{0,400}\bcalendar[- ]anchored.{0,300}\bonly when\b",
                ),
                # B4 — open-text prompts invite all valences (positive +
                # negative + neutral). Bare 'neutral' is too weak.
                (
                    "B4 open-text invites all valences",
                    r"all valences|positive,? negative,? (?:or|and) neutral",
                ),
                # B5 — option lists must enumerate fully (no subsetting).
                # Bare 'primary-source list' is too weak; require the
                # subsetting prohibition.
                (
                    "B5 enumerate fully / no subsetting",
                    r"enumerate(?:s|d)?\s+fully\b|no\s+subsetting\b",
                ),
            ],
        )
    ]


def compiler_agent_checks() -> list[Check]:
    """Spec §6.3 — report_compiler_agent (abstract-only mode) C1-C3 protection."""
    return [
        Check(
            pattern_id="C1-C3",
            description="report_compiler_agent (abstract-only) carries 3 publication-side protection clauses incl. anti-fake-audit guard",
            target=COMPILER_AGENT,
            block_marker=PROTECTION_BLOCK,
            must_contain=[
                # C1 — word-count algorithm
                "whitespace-split",
                # C2 — temporal disambiguation marker
                "explicit year range",
            ],
            must_contain_regex=[
                # C1 — protected hedges are budget-protected / non-negotiable.
                # Bare 'protected hedging phrases' was too weak; require the
                # obligation that they ride into the abstract verbatim.
                (
                    "C1 protected hedges non-negotiable",
                    r"protected\s+hedg(?:e|ing)\s+phrases.{0,300}\b(?:budget[- ]protected|non-negotiable|verbatim)\b",
                ),
                # C3 — anti-fake-audit guard. Both DO NOT clauses must appear,
                # in either order, within a 400-char window so the guard reads
                # as one injunction rather than two unrelated sentences.
                (
                    "C3 anti-fake-audit guard pair",
                    r"DO NOT simulate.{0,400}\bDO NOT claim to have run\b"
                    r"|DO NOT claim to have run.{0,400}\bDO NOT simulate\b",
                ),
            ],
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
