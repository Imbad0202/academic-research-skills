"""Shared constants for v3.8 claim-faithfulness audit.

Single source of truth for the literals + regexes that appear in BOTH the
lint (`check_claim_audit_consistency.py`) and the pipeline runtime
(`claim_audit_pipeline.py`). Re-declaring these in both places opens a
drift hole — a spec bump that updates the lint without updating the
runtime would change one side silently. Tests cover both call sites; the
shared import binds them.

See docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md §3.1
(matrix + INV catalogue) and §4 step 3 (sampling) for canonical
definitions.
"""
from __future__ import annotations

import re

# Canonical sentinel for the MANIFEST-MISSING fallback path (spec §3.1 INV-15).
SENTINEL_MANIFEST_ID = "M-0000-00-00T00:00:00Z-0000"

# INV-6 canonical rationale prefix (v3.7.3 R-L3-1-A firm rule).
INV6_RATIONALE_PREFIX = "v3.7.3 R-L3-1-A violation"

# INV-14 audit-tool-failure rationale fault-class tags.
INV14_FAULT_CLASS_TAGS: tuple[str, ...] = (
    "judge_timeout",
    "judge_api_error",
    "judge_parse_error",
    "cache_corruption",
    "retrieval_api_error",
    "retrieval_timeout",
    "retrieval_network_error",
)

# Sampling strategy literal (S-INV schema constant).
SAMPLING_STRATEGY = "stratified_buckets_v1"

# rule_version literals for v3.8.0 release. Future revisions bump the literal
# and require re-lint per spec §3.3 / §3.4 / §3.5.
UNCITED_RULE_VERSION = "D4-c-v1"
DRIFT_RULE_VERSION = "D4-a-v1"

# Constraint id parse rules (spec §3.2 + INV-17 canonical form).
RE_NC_CONSTRAINT = re.compile(r"^NC-C([0-9]{3,})-([0-9]+)$")
RE_MNC_CONSTRAINT = re.compile(r"^MNC-([0-9]+)$")
RE_CLAIM_ID = re.compile(r"^C-([0-9]{3,})$")

# Schema rejects this pattern, but for malformed-on-purpose fixtures the lint
# surfaces INV-17 explicitly before schema validation runs.
RE_NC_INNER_HYPHEN = re.compile(r"^NC-C-[0-9]+-[0-9]+$")

# ---------------------------------------------------------------------------
# D4-c uncited-assertion detector constants (spec §"Uncited-assertion
# detector (D4-c)" in claim_ref_alignment_audit_agent.md).
#
# Centralised here so pipeline runtime, lint, and detector share one source
# of truth — a spec bump touches one literal, not three.
# ---------------------------------------------------------------------------

# Condition 1: empirical-claim verbs (case-insensitive whole-word match).
# Spec list: showed, demonstrated, observed, proved, confirmed.
UNCITED_EMPIRICAL_VERBS: frozenset[str] = frozenset(
    {"showed", "demonstrated", "observed", "proved", "confirmed"}
)

# Condition 1: fuzzy English quantifier words (case-insensitive whole-word).
# Spec list: most, several, two-thirds. Kept literal; numerical / percent
# quantifiers are caught by RE_NUMERIC_QUANTIFIER below.
UNCITED_FUZZY_QUANTIFIERS: frozenset[str] = frozenset(
    {"most", "several", "two-thirds"}
)

# Condition 1: numerical quantifier regex. Spec line 250 lists three numeric
# classes — `numbers / percentages / explicit quantifiers (50%, 67 of 100)`.
# All three fire D4-c condition 1; the detector then applies a guard pass
# (RE_NUMERIC_QUANTIFIER_GUARD below) that rejects matches whose surrounding
# context proves them to be years, version triples, or section numbers
# instead of quantifiers. Splitting into match-broadly + guard-narrowly is
# easier to read and to test than stuffing every exclusion into a single
# regex's negative lookaheads. The detector concatenates the matched
# substring into trigger_tokens verbatim so the schema's minItems=1
# invariant holds.
RE_NUMERIC_QUANTIFIER = re.compile(
    # Order matters: longest-prefix-first so percent and "N of M" bind
    # before the bare-number branch swallows the leading digits.
    r"\b\d+(?:\.\d+)?%"                  # percent quantifier
    r"|\b\d+(?:\.\d+)?\s+of\s+\d+\b"     # "N of M" quantifier idiom
    r"|\b\d+(?:\.\d+)*\b"                # bare number, possibly dotted
                                          # (3+ segments routed to guard
                                          # as version/section)
)

# Condition 1 guard: rejects bare-number matches whose surrounding context
# identifies them as years, version triples, or section numbers — none of
# those are quantitative claims, and treating them as such produced
# false-positive LOW-WARN advisories before the guard landed (see codex
# R1 P1-3). Applied AFTER RE_NUMERIC_QUANTIFIER to the matched substring +
# its character offsets in the sentence; bare-number matches that satisfy
# any guard branch are dropped, percent and `N of M` matches always pass
# through.
#
# Guard branches:
#   1. Standalone 4-digit year in plausible academic range (1900-2099).
#   2. Version triple `X.Y.Z` (dotted form with 3+ segments — the broad
#      regex captures only the first two segments, so we re-scan).
#   3. Dotted section number `X.Y[.Z…]` (treated as section ref, not
#      quantifier). Distinguished from version by `section` / `§` /
#      `chapter` / `figure` / `table` cue word within a 24-char left
#      window, OR by `v` immediately preceding (version literal).
RE_BARE_NUMERIC_YEAR = re.compile(r"^(19|20)\d{2}$")
RE_DOTTED_TRIPLE_OR_MORE = re.compile(r"^\d+(?:\.\d+){2,}$")
RE_DOTTED_PAIR = re.compile(r"^\d+\.\d+$")
RE_SECTION_CUE = re.compile(
    r"(?:section|chapter|figure|table|fig\.|tbl\.|step|appendix|§)\s*$",
    re.IGNORECASE,
)
RE_VERSION_PREFIX = re.compile(r"v\s*$", re.IGNORECASE)
# Catches the case where Python's `\b` fails between a letter and a digit
# (both are \w characters) — e.g. `v3.7.3` has no \b between `v` and `3`,
# so RE_NUMERIC_QUANTIFIER starts matching from the SECOND segment (`7.3`)
# and the guard never sees the version-triple shape. This pattern detects
# a digit-then-dot prefix immediately attached to the left of the match.
# Requires exactly one digit-run + `.` ending the window — combined with
# the surrounding match (also dotted or bare number), this signals a
# multi-segment dotted form that should be treated as a version/section
# reference rather than a quantifier.
RE_NUMERIC_LEFT_ATTACHED = re.compile(r"\d+\.$")

# Condition 2: three-layer-citation ref-marker probe. Presence probe
# WITHIN the v3.7.3 ref-marker namespace — accepts any `<!--ref:...-->`
# shape where the slug payload begins with a non-whitespace character,
# rejects HTML comments that happen to start with `ref:` but use it as
# a label rather than a citation marker (e.g.
# `<!-- ref: $internal.notebook.cell -->`).
#
# Iteration history:
#   R0 `[^-]+`                                — rejected hyphenated slugs.
#   R1 `[A-Za-z][A-Za-z0-9_:-]* + 0-2 tokens` — rejected digit-leading
#                                                 slugs, plus-sign slugs,
#                                                 and 3+ status tokens.
#   R2 `[^>]*?`                                — too broad; matched
#                                                 `<!-- ref: $analysis -->`
#                                                 and similar code/internal
#                                                 ref comments (codex
#                                                 R3 P2-NEW-A).
#   R3 `[^\s>][^>]*?`                          — current. Slug must begin
#                                                 with a non-whitespace
#                                                 non-`>` character; the
#                                                 v3.7.3 strict validator
#                                                 in
#                                                 scripts/check_v3_7_3_three_layer_citation.py
#                                                 catches any remaining
#                                                 shape errors.
RE_REF_MARKER = re.compile(r"<!--\s*ref:[^\s>][^>]*?-->")

# Condition 3: definitional-phrase substrings (case-insensitive). Spec list:
# `refers to`, `is defined as`, `we define`, `for the purposes of`.
UNCITED_DEFINITION_PHRASES: tuple[str, ...] = (
    "refers to",
    "is defined as",
    "we define",
    "for the purposes of",
)
