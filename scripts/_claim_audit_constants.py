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

# Condition 1: numerical quantifier regex. Catches percentages (`50%`,
# `12.5%`) and `N of M` quantifier idioms; both are unambiguous quantitative
# claims in academic prose. Bare years (`2026`) and version triples
# (`v3.7.3`) are deliberately excluded — the previous `\b\d+(?:\.\d+)?%?`
# shape flagged them as quantifiers and produced false-positive LOW-WARN
# advisories. The detector concatenates the matched substring into
# trigger_tokens verbatim so the schema's minItems=1 invariant holds.
RE_NUMERIC_QUANTIFIER = re.compile(
    r"\b\d+(?:\.\d+)?%"               # percent quantifier
    r"|\b\d+(?:\.\d+)?\s+of\s+\d+\b"  # "N of M" quantifier idiom
)

# Condition 2: three-layer-citation ref-marker probe. Aligned with v3.7.3
# canonical slug pattern `[A-Za-z][A-Za-z0-9_:-]*` and accepts up to 2
# post-finalizer status tokens (`<!--ref:slug ok-->`,
# `<!--ref:slug LOW-WARN-->`, `<!--ref:slug ok CONTAMINATED-PREPRINT-->`).
# Pattern stays permissive (presence-probe, not strict validator): a
# strict regex would reject malformed slugs and erroneously flag those
# sentences as D4-c candidates. Source of truth lives at
# scripts/check_v3_7_3_three_layer_citation.py REF_PATTERN; this clone
# exists because the detector needs presence semantics, not validator
# semantics, and importing across the module boundary would couple the
# two readers' regex shapes.
RE_REF_MARKER = re.compile(
    r"<!--\s*ref:[A-Za-z][A-Za-z0-9_:-]*(?:\s+[\w+-]+){0,2}\s*-->"
)

# Condition 3: definitional-phrase substrings (case-insensitive). Spec list:
# `refers to`, `is defined as`, `we define`, `for the purposes of`.
UNCITED_DEFINITION_PHRASES: tuple[str, ...] = (
    "refers to",
    "is defined as",
    "we define",
    "for the purposes of",
)
