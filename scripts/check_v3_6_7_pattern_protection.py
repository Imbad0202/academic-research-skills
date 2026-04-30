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

import os
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

# Negation / weakening patterns that, if present in the sentence containing
# an obligation match, indicate the obligation is being denied or weakened
# rather than asserted. R2-004 flagged "does not enumerate fully" / "not non-
# negotiable"; R3-002 expanded the list with should not / fails to / instead
# of / rarely / sometimes / is unable to. The patterns split into two groups:
#
# - _GENERAL_NEGATION_PATTERNS: DO NOT-style imperative prohibitions and
#   weakening modals. These reject most obligations BUT they would also
#   reject a legitimate prohibition like C3's "DO NOT simulate". For
#   prohibition-style obligations, callers pass `allow_prohibition=True` to
#   skip this group.
# - _ALWAYS_NEGATION_PATTERNS: weakening verbs and adverbs that never
#   constitute a valid prohibition signal (rarely / sometimes / fails to /
#   etc.). These apply regardless of `allow_prohibition`.
_GENERAL_NEGATION_PATTERNS = [
    # Subject + auxiliary negation that directly weakens an obligation.
    # These are the verb-negation forms most commonly used to undo a rule
    # ("X does not Y", "X must not Y"). They are excluded by default but
    # exempted for prohibition-style obligations like C3 via
    # `allow_prohibition`.
    re.compile(r"\bdoes not\b", re.IGNORECASE),
    re.compile(r"\bdo not\b", re.IGNORECASE),
    re.compile(r"\bDO NOT\b"),  # case-sensitive imperative form
    re.compile(r"\bdoesn'?t\b", re.IGNORECASE),
    re.compile(r"\bdon'?t\b", re.IGNORECASE),
    re.compile(r"\bshould not\b", re.IGNORECASE),
    re.compile(r"\bshouldn'?t\b", re.IGNORECASE),
    re.compile(r"\bmust not\b", re.IGNORECASE),
    re.compile(r"\bmustn'?t\b", re.IGNORECASE),
    # Adjective-targeted negations: explicit "not <obligation-adjective>"
    # forms that directly negate the contract vocabulary.
    re.compile(r"\bnot\s+(?:non[- ]negotiable|enumerate|required|mandatory|forbidden|verbatim|reserved)\b", re.IGNORECASE),
    re.compile(r"\bneed not\b", re.IGNORECASE),
    re.compile(r"\bno\s+buffer\b", re.IGNORECASE),
    re.compile(r"\bno\s+enumeration\b", re.IGNORECASE),
    # NOTE: `cannot` and `can't` are intentionally NOT in this list. They
    # are routinely used in benign conditional phrasing ("if X cannot fit,
    # the compiler reports..."), where `cannot` describes a trigger
    # condition rather than weakening an obligation. The other negation
    # patterns are tight enough to catch genuine weakening even without
    # `cannot`.
]
_ALWAYS_NEGATION_PATTERNS = [
    re.compile(r"\bisn'?t\b", re.IGNORECASE),
    re.compile(r"\baren'?t\b", re.IGNORECASE),
    # `optional` only counts as a weakener when it directly modifies an
    # obligation noun. The bare token can appear in unrelated context
    # ("optional `approved_synonyms` field"), so we narrow this rule to
    # `optional <obligation-noun>` forms.
    re.compile(r"\boptional\s+(?:buffer|enumeration|preservation|inclusion|verbatim|hedge|hedges|enforcement|requirement|reservation)\b", re.IGNORECASE),
    # Same narrowing for `may` — only flag when `may` directly weakens an
    # action verb that should be obligatory.
    re.compile(r"\bmay\s+(?:not\s+)?(?:invite|enumerate|preserve|drop|skip|substitute|paraphrase)\b", re.IGNORECASE),
    re.compile(r"\bfails? to\b", re.IGNORECASE),
    re.compile(r"\binstead of\b", re.IGNORECASE),
    # `rarely` / `sometimes` / `occasionally` similarly need to be near
    # an obligation verb to count as weakeners.
    re.compile(r"\brarely\s+(?:enumerate|enforce|invoke|reserve|preserve|verify)", re.IGNORECASE),
    re.compile(r"\bsometimes\s+(?:enumerate|enforce|invoke|reserve|preserve|verify)", re.IGNORECASE),
    re.compile(r"\boccasionally\s+(?:enumerate|enforce|invoke|reserve|preserve|verify)", re.IGNORECASE),
    re.compile(r"\bis unable to\b", re.IGNORECASE),
    re.compile(r"\bare unable to\b", re.IGNORECASE),
    re.compile(r"\bonly when convenient\b", re.IGNORECASE),
    re.compile(r"\bif (?:space|time) (?:allows|permits)\b", re.IGNORECASE),
    # Feasibility qualifiers (R6-001). "when possible" / "where possible"
    # /etc. tail-attached to an obligation phrase silently downgrades it
    # from mandatory to best-effort.
    re.compile(r"\bwhen\s+possible\b", re.IGNORECASE),
    re.compile(r"\bwhere\s+possible\b", re.IGNORECASE),
    re.compile(r"\bwherever\s+feasible\b", re.IGNORECASE),
    re.compile(r"\bif\s+practical\b", re.IGNORECASE),
    re.compile(r"\bif\s+feasible\b", re.IGNORECASE),
    re.compile(r"\bbest[- ]effort\b", re.IGNORECASE),
]


def _match_excludes_negation(text_window: str, allow_prohibition: bool = False) -> bool:
    """Return True if the sentence around an obligation match does NOT
    contain any negation that would weaken it.

    `allow_prohibition=True` exempts only the literal `DO NOT` imperative
    token (the prohibition obligation itself, e.g. C3 anti-fake-audit
    guard's "DO NOT simulate" / "DO NOT claim to have run"). All OTHER
    general negation patterns (cannot / must not / not required / need
    not / etc.) still apply, so a window like "DO NOT simulate ...
    this is not required" is still rejected (R4-001).

    The `_ALWAYS_NEGATION_PATTERNS` (rarely, sometimes, fails to,
    optional, etc.) apply regardless because no legitimate obligation
    framing should rely on those.
    """
    if any(p.search(text_window) for p in _ALWAYS_NEGATION_PATTERNS):
        return False
    # When the caller signals this is a prohibition obligation, the
    # subject-verb negation forms ("does not paraphrase", "DO NOT
    # simulate") are how the obligation is *expressed*, not weakened.
    # Exempt those forms but still enforce adjective-targeted negation
    # ("not required", "not non-negotiable") and explicit weakeners
    # (no buffer, no enumeration), which always indicate the contract
    # is being undone rather than asserted.
    PROHIBITION_VERB_PATTERNS = {
        r"\bDO NOT\b",
        r"\bdo not\b",
        r"\bdoes not\b",
        r"\bdoesn'?t\b",
        r"\bdon'?t\b",
        # `must not` is a prohibition expression of obligation, not a
        # weakener — used in C3 ("Output metadata must not claim audit-
        # passed state") and equivalent verbatim-only style rules.
        r"\bmust not\b",
        r"\bmustn'?t\b",
    }
    for p in _GENERAL_NEGATION_PATTERNS:
        if allow_prohibition and p.pattern in PROHIBITION_VERB_PATTERNS:
            continue
        if p.search(text_window):
            return False
    return True


@dataclass
class Check:
    pattern_id: str
    description: str
    target: Path
    must_contain: list[str] = field(default_factory=list)
    must_contain_regex: list[tuple[str, str] | tuple[str, str, bool]] = field(default_factory=list)
    """Each entry is `(label, pattern)` or `(label, pattern, allow_prohibition)`.
    `allow_prohibition` is per-regex (not per-Check) so a check can mix
    prohibition-style obligations (REF-3 verbatim preservation, C3 anti-
    fake-audit guard, C3 audit-passed metadata) with assertion-style
    obligations (C1 protected hedges non-negotiable) without the
    prohibition exemption leaking across regexes (B2 codex R2-001)."""
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
        missing_regex = []
        for entry in self.must_contain_regex:
            if len(entry) == 2:
                label, pattern = entry
                allow_prohibition = False
            else:
                label, pattern, allow_prohibition = entry
            # First try to find an obligation match.
            match = re.search(pattern, scoped, re.IGNORECASE | re.DOTALL)
            if match is None:
                missing_regex.append(label)
                continue
            # Reject if the bullet/paragraph containing the match carries
            # a negation that weakens the obligation (per R2-004 + R3-001
            # + R4-001). The check looks backward from the match start to
            # the start of the current bullet (or paragraph start) and
            # forward from the match end to the next bullet (or blank line
            # / EOF). This catches trailing weakeners like
            # "...obligation. This is not required."
            iterator = re.finditer(pattern, scoped, re.IGNORECASE | re.DOTALL)
            accepted = False
            for m in iterator:
                start, end = m.start(), m.end()
                # Lookback to the start of this bullet/paragraph: previous
                # blank line, list-bullet marker on its own line, or start
                # of scoped text. Capped at 400 chars so very long bullets
                # do not pull in unrelated negation from far above.
                lookback_floor = max(0, start - 400)
                lookback = scoped[lookback_floor:start]
                blank_line = lookback.rfind("\n\n")
                bullet_back_match = list(re.finditer(r"\n\s*-\s", lookback))
                bullet_back = bullet_back_match[-1].start() if bullet_back_match else -1
                last_break_back = max(blank_line, bullet_back)
                bullet_start = (
                    lookback_floor + last_break_back + 1
                    if last_break_back >= 0
                    else lookback_floor
                )
                # Lookahead to the start of the next bullet, blank line,
                # or EOF (capped 400 chars).
                lookahead_ceiling = min(len(scoped), end + 400)
                lookahead = scoped[end:lookahead_ceiling]
                blank_fwd = lookahead.find("\n\n")
                bullet_fwd_match = re.search(r"\n\s*-\s", lookahead)
                bullet_fwd = bullet_fwd_match.start() if bullet_fwd_match else -1
                fwd_breaks = [i for i in (blank_fwd, bullet_fwd) if i >= 0]
                next_break = min(fwd_breaks) if fwd_breaks else -1
                bullet_end = end + next_break if next_break >= 0 else lookahead_ceiling
                window = scoped[bullet_start:bullet_end]
                if _match_excludes_negation(window, allow_prohibition=allow_prohibition):
                    accepted = True
                    break
            if not accepted:
                missing_regex.append(f"{label} (only negated forms found)")
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
            description="protected_hedging_phrases defines upstream-marked hedge protocol with 5 contract rules",
            target=REF_DIR / "protected_hedging_phrases.md",
            must_contain=[
                "protected hedging phrases",
                "upstream calibration",
                "word budget",
            ],
            must_contain_regex=[
                # Rule 1: conservative inclusion — "include the phrase" is
                # the operative directive (R5-002 mutation showed
                # "ask upstream for advice" was previously accepted).
                (
                    "Rule: Conservative inclusion",
                    r"\bConservative inclusion\b.{0,200}\bWhen in doubt\b.{0,150}\binclude\s+the\s+phrase\b",
                ),
                # Rule 2: anchor every entry — "where … and why" is the
                # specific obligation; bare "must cite" was previously
                # accepted with weakened content.
                (
                    "Rule: Anchor every entry (where + why)",
                    r"\bAnchor every entry\b.{0,200}\bmust\s+cite\s+where\b.{0,200}\bwhy\b",
                ),
                # Rule 3: no duplicates — bullet body must assert
                # "One entry per phrase" then back-reference the count.
                # R5-002 showed bare "One entry per phrase" alone could be
                # suffixed with "is optional" and still pass; require the
                # full "One entry per phrase. The compiler counts ... once"
                # sequence so a tail weakener cannot land between them.
                # Allow Markdown markup (`**`) between the heading word and
                # the body sentence.
                (
                    "Rule: No duplicates",
                    r"\bNo duplicates\b[\s.*\-]{0,10}One entry per phrase\.\s+The compiler counts[^.]{0,150}\bonce\b",
                ),
                # Rule 4: verbatim preservation — both the title and the
                # imperative body ("does not paraphrase") must appear. The
                # body uses "does not paraphrase / substitute" as the
                # prohibition expressing the obligation, so this specific
                # regex needs prohibition exemption (was per-Check before
                # B2 R2-001; now per-regex so other regexes in this Check
                # still reject inverted forms).
                (
                    "Rule: Verbatim preservation",
                    r"\bVerbatim preservation\b.{0,250}\brides\s+verbatim\b.{0,300}\bdoes\s+not\s+paraphrase\b",
                    True,  # allow_prohibition: prohibition-style obligation body
                ),
                # Rule 5: failure surface — must say "rather than dropping",
                # not "while dropping" (R5-002 mutation flipped this).
                (
                    "Rule: Conflict reporting (no silent drop)",
                    r"\breports the conflict\b[^.\n]{0,100}\brather than\s+dropping a protected hedge\b",
                ),
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
        # The report_compiler bundle's Section 4(f) is mandatory three-part:
        # (i) word-count cap-minus-buffer, (ii) protected-hedge verbatim,
        # (iii) abstract no less hedged than body. R1-006 upgraded this from
        # an example to a mandatory contract; lint must verify the contract
        # rides verbatim in the template, not just the prose around it.
        # Scoped to the `report_compiler_agent bundle` clause so scattered
        # text elsewhere in the template cannot satisfy the contract (R3-004).
        Check(
            pattern_id="TPL-2 (4f-compiler)",
            description="audit template encodes mandatory three-part (f) check for report_compiler bundles",
            target=TPL_DIR / "codex_audit_multifile_template.md",
            block_marker="report_compiler_agent bundle (mandatory three-part check)",
            must_contain_regex=[
                # Sub-check (i): whitespace-split cap minus 3-5% buffer
                (
                    "4f sub-check (i) word-count algorithm + buffer",
                    r"len\(body\.split\(\)\).{0,200}\b3[-–]5%\s+buffer\b",
                ),
                # Sub-check (ii): protected_hedges appear verbatim
                # unconditionally. R5-003 mutation showed bare
                # "appear verbatim when possible" was previously accepted;
                # the obligation must be unconditional ("appears verbatim
                # in the abstract" without "when possible" / "if space").
                # The negation post-filter already rejects "when convenient"
                # / "if space allows", so the regex requires the
                # imperative-tense phrasing.
                (
                    "4f sub-check (ii) protected_hedges verbatim (unconditional)",
                    r"every entry of upstream\s+`?protected_hedges`?[^\n]{0,200}\bappears? verbatim in the abstract\b",
                ),
                # Sub-check (iii): "no claim in the abstract is less hedged
                # than its anchor in the body" — anchored on "no claim" so
                # an inverted form ("every claim ... is less hedged") fails.
                (
                    "4f sub-check (iii) less-hedged-than-body prohibition",
                    r"\bno claim in the abstract is less hedged than its anchor in the body\b",
                ),
                # P1 severity assignment for any sub-check failure
                (
                    "4f failures severity P1",
                    r"\bFailure of any sub-check is a P1 finding\b",
                ),
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
                # explicitly forbidden in one contiguous injunction, sentence-
                # bounded so unrelated clauses elsewhere in the block do not
                # syntactically satisfy the obligation (per R2-003).
                (
                    "A5 sentence-bounded injunction",
                    r"declarative claims? about un-provided[^.\n]{0,200}\bare forbidden\b",
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
                # Spec wording naturally spans two sentences ("default to..."
                # then "calendar... only when..."), so the gap allows one
                # sentence boundary; the 'only when' tail must sit in the
                # same sentence as 'calendar-anchored' to bind the conditional.
                (
                    "B3 retrospective default + calendar conditional",
                    r"event-anchored[^.\n]{0,200}\.[^.\n]{0,100}\bcalendar[- ]anchored[^.\n]{0,200}\bonly when\b",
                ),
                # B4 — open-text prompts invite all valences. Sentence-bounded
                # so a stray 'neutral' elsewhere does not satisfy.
                (
                    "B4 open-text invites all valences",
                    r"\b(?:all valences|positive,? negative,? (?:or|and) neutral)\b",
                ),
                # B5 — option lists must declare primary-source list AND
                # enumerate fully AND prohibit subsetting. All three are
                # the contract; matching any one alone (e.g. "enumerate
                # fully" with "subsetting is acceptable" elsewhere) is a
                # silent gap. Require all three obligation phrases.
                (
                    "B5 primary-source list + enumerate fully",
                    r"\bprimary-source list\b[^.\n]{0,100}\benumerate(?:s|d)?\s+fully\b",
                ),
                (
                    "B5 no subsetting prohibition",
                    r"\bno\s+subsetting\b",
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
                # C1 — protected hedges are budget-protected / non-negotiable
                # / verbatim. Sentence-bounded; negation post-filter rejects
                # "are not non-negotiable" (R2-004) AND must reject inverted
                # "Compression must not preserve protected hedging phrases"
                # (B2 R2-001), so this regex does NOT take prohibition
                # exemption — it is an assertion-style obligation.
                (
                    "C1 protected hedges non-negotiable",
                    r"protected\s+hedg(?:e|ing)\s+phrases[^.\n]{0,200}\b(?:budget[- ]protected|non-negotiable|verbatim)\b",
                ),
                # C3 — anti-fake-audit guard. Both DO NOT clauses must appear
                # in either order. The gap allows two short sentences (the
                # natural "DO NOT simulate ... DO NOT claim ..." wording).
                # This is itself a prohibition obligation, so allow the
                # `DO NOT` imperative through the negation post-filter
                # (R4-001 still applies — trailing "this is not required"
                # is rejected by the adjective-targeted negation rules).
                (
                    "C3 anti-fake-audit guard pair",
                    r"DO NOT simulate[^\n]{0,300}\.[^\n]{0,100}\bDO NOT claim to have run\b"
                    r"|DO NOT claim to have run[^\n]{0,300}\.[^\n]{0,100}\bDO NOT simulate\b",
                    True,  # allow_prohibition: this IS the prohibition
                ),
                # C3 — output metadata prohibition. Spec §6.3 explicitly
                # closes the loop: "Output metadata must not claim
                # audit-passed state." Without this, an agent could
                # honour the DO NOT pair while still surfacing fake
                # audit-passed metadata (B2 codex R1-001). Uses `must not`
                # as the prohibition expression — exemption is per-regex
                # so it does not leak to C1's assertion-style obligation
                # (B2 R2-001).
                (
                    "C3 output metadata audit-passed prohibition",
                    r"\bOutput metadata must not claim audit-passed state\b",
                    True,  # allow_prohibition: `must not` is the obligation
                ),
            ],
        )
    ]


# Environment variable controlling whether agent-prompt checks run.
#
# Spec §9 ships v3.6.7 across multiple steps. Step 1 (this PR) shipped the
# 4 reference files + audit template + this lint. Step 2 (this PR / Step 1+2
# bundle) lands the actual PATTERN PROTECTION (v3.6.7) blocks in the three
# downstream agent prompts. With Step 2 in, the agent-prompt checks are
# default-on so CI enforces the contract.
#
# Set ARS_V3_6_7_AGENT_CHECKS=0 to skip agent-prompt checks (e.g. for a
# repo bisect that crosses a pre-Step-2 commit, or for partial test runs).
_AGENT_CHECKS_ENV = "ARS_V3_6_7_AGENT_CHECKS"


def _agent_checks_enabled() -> bool:
    return os.environ.get(_AGENT_CHECKS_ENV, "1") == "1"


def all_checks() -> list[Check]:
    checks = [
        *reference_file_checks(),
        *template_file_checks(),
    ]
    if _agent_checks_enabled():
        checks.extend([
            *synthesis_agent_checks(),
            *architect_agent_checks(),
            *compiler_agent_checks(),
        ])
    return checks


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

    deferred_note = ""
    if not _agent_checks_enabled():
        deferred_note = " (agent-prompt checks skipped — ARS_V3_6_7_AGENT_CHECKS=0)"
    summary = (
        f"v3.6.7 pattern-protection static audit: {len(passed)}/{len(checks)} "
        f"checks passed{deferred_note}"
    )
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
