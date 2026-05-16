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
