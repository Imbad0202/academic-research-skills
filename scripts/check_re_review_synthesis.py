#!/usr/bin/env python3
"""Recompute the #576 Spec B three-gate re-review contract from its artifacts.

Stdlib-only, same architecture class as ``check_panel_synthesis.py`` (#510:
recompute every layer from the primary artifacts; any mismatch voids the
synthesis). Normative source:
``docs/design/2026-07-27-576-spec-b-re-review-precommitment-contract-spec.md``
§5 (artifact shapes), §6 (decision derivation), §10 (reviewer-label
normalization grammar), §11 (input manifest + apply-chain witness), §13
(checker responsibilities).

Responsibilities (spec §13):

1. Schema-validate the three phase artifacts + manifest (self-contained
   validators), and replay the hash-bound #670 Revision-Evidence Bundle.
2. Hash-chain: ``input_manifest_hash`` -> ``precommitment_hash`` ->
   ``verdict_record_hash`` verbatim binding; criterion inheritance binding
   (roadmap_text / letter_text byte comparison + R<n> ordinal recomputation
   with the §5.1 contiguity degradation).
3. Consumer-side apply-chain witness (§11), including mandatory report-1.3
   ``patch_digest`` content-bound positional pairing. Older reports are
   accepted only by the isolated archived loader.
4. Recompute invariants: coverage cardinalities, applied_criterion rules,
   adjustment-chain grammar, deferral-loop referential integrity
   (reapplications / resolutions / adjudications / acceptances / pending
   rebuttal upgrades), the G2 deferral biconditional, DecisionInputs
   operand equality, and the §6 Step 1-3 derivation (Steps 2-3 recomputed
   BOTH from DecisionInputs AND independently from the raw records).
5. Goalpost witness: the frozen new-issue set is byte-identical across
   §5.2/§5.3 and only ``regression`` attribution enters the decision path.

Exit codes (graded, spec §13):

  0  pass
  1  recomputation mismatch -> ``[RE-REVIEW-ABORT: synthesis_mismatch]``
     (referential-integrity failures are recomputation mismatches and
     always exit 1)
  2  schema or manifest invalid -> the matching §3.5 abort reason
     (``manifest_incomplete`` / ``manifest_hash_mismatch`` for the
     manifest layer; ``phase1_lint_failed`` / ``phase2a_lint_failed`` /
     ``phase2b_lint_failed`` for a phase artifact that fails its schema)

Classification note (documented design decision): the three hash-chain
links and the manifest-side §11 rules (artifact byte hashes, freshness,
patch_digest pairing, apply-chain witness ``fail``) are the same-inputs
proof — their violation is graded exit 2 with ``manifest_hash_mismatch``,
mirroring §11's "-> manifest_hash_mismatch, G0". Content recomputation on
top of a sound binding (criterion quotes, letter ordinals, chains,
decision) is graded exit 1.

Hashing convention: sha256 hex over JSON Canonical Form (RFC 8785 / JCS,
the v3.6.3 passport convention). For this contract's value domain
(objects/arrays/strings/integers/booleans/null) Python's
``json.dumps(obj, sort_keys=True, separators=(",", ":"),
ensure_ascii=False)`` produces the JCS byte stream.

Usage:
    python scripts/check_re_review_synthesis.py \
        --manifest M.json --precommitment P.json \
        --verdict-record V.json --traceability T.json \
        --roadmap roadmap.json --author-adjudication author.json \
        --revision-evidence-bundle bundle.json \
        [--revision-evidence-root bundle-root] \
        [--letter letter.md] \
        [--apply-report R1.json ...]

The roadmap, author sidecar, Revision-Evidence Bundle, optional letter, and
ordered apply reports are exact §11 files the checker reads. Bundle replay
uses only its explicitly declared local artifacts under the supplied root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

if __package__ in (None, ""):  # pragma: no cover - direct CLI invocation
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.revision_roadmap import ContractError as RevisionContractError
from scripts.revision_roadmap import validate_bundle

EXIT_PASS = 0
EXIT_SYNTHESIS = 1
EXIT_INVALID = 2

VERDICTS = ("FULLY_ADDRESSED", "PARTIALLY_ADDRESSED", "NOT_ADDRESSED", "MADE_WORSE", "CANNOT_VERIFY")
JUDGE_VERDICTS = ("FULLY_ADDRESSED", "PARTIALLY_ADDRESSED", "NOT_ADDRESSED", "MADE_WORSE")
OBLIGATION_CLASSES = ("must_fix", "should_fix", "consider")
ROW_OBLIGATION_MAP = {"MUST_FIX": "must_fix", "SHOULD_FIX": "should_fix", "CONSIDER": "consider"}
SEVERITIES = ("critical", "major", "minor")
RESIDUAL_OBLIGATION_CLASSES = ("must_fix", "should_fix", "consider")
SEAT_LABELS = ("EIC", "R1", "R2", "R3", "DA")
VERIFIER_SEATS = ("EIC", "R1", "R2", "R3")
ADJUSTMENT_BASES = (
    "author_pointer_located_evidence",
    "valid_rebuttal",
    "scope_correction",
    "user_accepted_fail_closed",
    "cross_model_adjudication",
)
ATTRIBUTIONS = ("regression", "previously_missed", "indeterminate")
DECISION_STATES = ("Accept", "Minor Revision", "Major Revision", "user_review_required", "aborted")
ABORT_REASONS = (
    "phase1_lint_failed",
    "phase2a_lint_failed",
    "phase2b_lint_failed",
    "manifest_incomplete",
    "manifest_hash_mismatch",
    "criteria_drift",
    "synthesis_mismatch",
)
WITNESS_STATES = ("pass", "fail", "not_run_no_reports")
DECISION_ORDER = {"Accept": 0, "Minor Revision": 1, "Major Revision": 2}
# §5.3 mechanical 5->4 map (MADE_WORSE -> NO: the concern stands unresolved —
# verification happened, outcome negative).
VERIFIED_MAP = {
    "FULLY_ADDRESSED": "YES",
    "PARTIALLY_ADDRESSED": "PARTIAL",
    "NOT_ADDRESSED": "NO",
    "MADE_WORSE": "NO",
    "CANNOT_VERIFY": "CANNOT_VERIFY",
}
ESCALATION_CLASSES = ("research_integrity", "ethics", "safety", "legal_compliance", "fatal_validity")

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_HASH12_RE = re.compile(r"^[0-9a-f]{12}$")
_REPORT_VERSION_RE = re.compile(r"^[0-9]+(\.[0-9]+)*$")
_ITEM_ID_RE = re.compile(r"^REV-[A-Za-z0-9-]+$")
_CONCERN_ID_RE = re.compile(r"^[RSN][1-9][0-9]*$")
_LETTER_REF_RE = re.compile(r"^R([1-9][0-9]*)$")
_ANCHOR_RE = re.compile(r"^(text|table|figure|equation|dataset|absence): .+$")
_ARTIFACT_REF_RE = re.compile(r"^(passport|path):.+$")
_ANSWER_REF_RE = re.compile(r"^(adjudication:DIS-[1-9][0-9]*|intent:INT-[1-9][0-9]*)$")
_CRITERION_REF_RE = re.compile(r"^(phase1:REV-[A-Za-z0-9-]+|dissent:DIS-[1-9][0-9]*)$")
_SOURCE_REF_RE = re.compile(r"^(reapplication:RAP-[1-9][0-9]*|acceptance:ACC-[1-9][0-9]*)$")
_CHECK_ADJUDICATED_RE = re.compile(r"^adjudicated:(RADJ-[1-9][0-9]*)$")
_AUTHOR_EVENT_RE = re.compile(r"^AUTHOR-EVENT-[A-Za-z0-9._-]+$")
_BLOCK_ID_RE = re.compile(r"^(?:B[0-9]{4,}|DOC-BODY-START)$")
_CLAIM_AUTH_RE = re.compile(r"^CLAIM-AUTH-[A-Za-z0-9._-]+$")
_CLAIM_SURFACE_RE = re.compile(r"^CLAIM-SURFACE-[A-Za-z0-9._-]+$")
_CLAIM_ID_RE = re.compile(r"^C-[0-9]{3,}$")
_MANIFEST_ID_RE = re.compile(
    r"^M-[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z-[0-9a-f]{4}$"
)
_ID_RES = {
    "NS": re.compile(r"^NS-[1-9][0-9]*$"),
    "NEW": re.compile(r"^NEW-[1-9][0-9]*$"),
    "DIS": re.compile(r"^DIS-[1-9][0-9]*$"),
    "ESC": re.compile(r"^ESC-[1-9][0-9]*$"),
    "ADJ": re.compile(r"^ADJ-[1-9][0-9]*$"),
    "INT": re.compile(r"^INT-[1-9][0-9]*$"),
    "RES": re.compile(r"^RES-[1-9][0-9]*$"),
    "RADJ": re.compile(r"^RADJ-[1-9][0-9]*$"),
    "ACC": re.compile(r"^ACC-[1-9][0-9]*$"),
    "RAP": re.compile(r"^RAP-[1-9][0-9]*$"),
    "PRB": re.compile(r"^PRB-[1-9][0-9]*$"),
}


class ManifestError(Exception):
    """Manifest-layer failure -> exit 2 with a §3.5 G0 reason."""

    def __init__(self, reason: str, message: str):
        self.reason = reason
        super().__init__(message)


class ArtifactSchemaError(Exception):
    """Phase-artifact schema failure -> exit 2 with the phase lint reason."""

    def __init__(self, reason: str, message: str):
        self.reason = reason
        super().__init__(message)


def canonical_hash(obj) -> str:
    """sha256 hex over the object's JSON Canonical Form (RFC 8785 / JCS)."""
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _strict_json_bytes(raw: bytes, label: str):
    """Parse interoperable JSON: UTF-8, unique keys, no NaN/Infinity."""
    def unique_object(pairs):
        value = {}
        for key, child in pairs:
            if key in value:
                raise ValueError(f"duplicate object key {key!r}")
            value[key] = child
        return value

    def reject_constant(token):
        raise ValueError(f"non-finite JSON constant {token!r}")

    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label}: invalid interoperable JSON ({exc})") from exc


# --- §10 normalization grammar -------------------------------------------------

_PAREN_RE = re.compile(r"\([^()]*\)")
_SEPARATOR_RE = re.compile(r",|/|;| and |&")
_R_TOKEN_RES = (
    re.compile(r"^r([1-3])$"),
    re.compile(r"^reviewer ([1-3])$"),
    re.compile(r"^peer reviewer ([1-3])$"),
)


def normalize_reviewer_labels(raw: str):
    """§10 emitter-side normalization grammar, in declared order.

    (1a) strip every parenthetical group FIRST; (1b) THEN strip any
    " — <suffix>" tail from the residual (order normative and
    non-commutative); (2) split on {",", "/", ";", " and ", "&"};
    (3) trim whitespace; case-fold. A stripped token normalizes by
    WHOLE-TOKEN EXACT MATCH (no substring extraction); unrecognized
    tokens are DROPPED, never guessed. Returns ``(labels, parse_failure)``
    where labels is the deduplicated, original-order result and
    ``parse_failure`` is True when a non-empty input produced zero
    recognized tokens (§10: routes to EIC but counts as unmapped — a
    distinct state from a genuinely empty list).
    """
    text = unicodedata.normalize("NFC", raw)
    prev = None
    while prev != text:  # nested groups collapse outside-in
        prev = text
        text = _PAREN_RE.sub("", text)
    dash_idx = text.find(" — ")
    if dash_idx != -1:
        text = text[:dash_idx]
    labels = []
    for token in _SEPARATOR_RE.split(text):
        token = token.strip().casefold()
        if not token:
            continue
        label = None
        if token in ("eic", "editor-in-chief"):
            label = "EIC"
        elif token in ("da", "devil's advocate", "devil’s advocate"):
            label = "DA"
        else:
            for pattern in _R_TOKEN_RES:
                match = pattern.match(token)
                if match:
                    label = "R" + match.group(1)
                    break
        if label is not None and label not in labels:
            labels.append(label)
    parse_failure = bool(raw.strip()) and not labels
    return labels, parse_failure


# --- validation helpers --------------------------------------------------------


def _is_str(value, nonempty=True) -> bool:
    return isinstance(value, str) and (not nonempty or len(value) > 0)


class _V:
    """Accumulating validator for one artifact; raises on first failure."""

    def __init__(self, reason: str, artifact_name: str):
        self.reason = reason
        self.artifact = artifact_name

    def fail(self, path: str, message: str):
        raise ArtifactSchemaError(self.reason, f"{self.artifact}: {path}: {message}")

    def obj(self, value, path, required, optional=()):
        if not isinstance(value, dict):
            self.fail(path, "must be an object")
        allowed = set(required) | set(optional)
        for key in value:
            if key not in allowed:
                self.fail(path, f"unexpected field {key!r}")
        for key in required:
            if key not in value:
                self.fail(path, f"missing required field {key!r}")

    def string(self, value, path, nonempty=True):
        if not _is_str(value, nonempty):
            self.fail(path, "must be a non-empty string" if nonempty else "must be a string")

    def enum(self, value, path, allowed):
        if value not in allowed:
            self.fail(path, f"must be one of {sorted(allowed)!r}, got {value!r}")

    def pattern(self, value, path, regex, label):
        if not isinstance(value, str) or not regex.match(value):
            self.fail(path, f"must match {label}, got {value!r}")

    def integer(self, value, path, minimum=None, maximum=None):
        if not isinstance(value, int) or isinstance(value, bool):
            self.fail(path, "must be an integer")
        if minimum is not None and value < minimum:
            self.fail(path, f"must be >= {minimum}")
        if maximum is not None and value > maximum:
            self.fail(path, f"must be <= {maximum}")

    def array(self, value, path):
        if not isinstance(value, list):
            self.fail(path, "must be an array")


def _validate_residual_gap(v: _V, gap, path):
    v.obj(gap, path, ["text", "residual_obligation_class"])
    v.string(gap["text"], f"{path}.text")
    v.enum(gap["residual_obligation_class"], f"{path}.residual_obligation_class", RESIDUAL_OBLIGATION_CLASSES)


def _validate_author_targets(v: _V, targets, path):
    v.array(targets, path)
    seen = set()
    operation_order = {"replace_block": 0, "insert_after": 1, "delete_block": 2}
    prior_key = None
    for i, target in enumerate(targets):
        row_path = f"{path}[{i}]"
        v.obj(target, row_path, ["block_id", "allowed_operations"])
        v.pattern(target["block_id"], f"{row_path}.block_id", _BLOCK_ID_RE, "B<n> | DOC-BODY-START")
        if target["block_id"] in seen:
            v.fail(path, f"duplicate block_id {target['block_id']!r}")
        seen.add(target["block_id"])
        v.array(target["allowed_operations"], f"{row_path}.allowed_operations")
        if not target["allowed_operations"]:
            v.fail(f"{row_path}.allowed_operations", "must not be empty")
        if len(target["allowed_operations"]) != len(set(target["allowed_operations"])):
            v.fail(f"{row_path}.allowed_operations", "must be duplicate-free")
        for op in target["allowed_operations"]:
            v.enum(op, f"{row_path}.allowed_operations", tuple(operation_order))
        if target["allowed_operations"] != sorted(
            target["allowed_operations"], key=operation_order.__getitem__
        ):
            v.fail(f"{row_path}.allowed_operations", "must use canonical operation order")
        block_order = -1 if target["block_id"] == "DOC-BODY-START" else int(target["block_id"][1:])
        key = (block_order, target["block_id"])
        if prior_key is not None and key < prior_key:
            v.fail(path, "must use canonical block order")
        prior_key = key


def _validate_claim_authorizations(v: _V, authorizations, path):
    v.array(authorizations, path)
    seen = set()
    required = [
        "authorization_id",
        "author_event_id",
        "surface_id",
        "scoped_manifest_id",
        "claim_id",
        "block_id",
        "original_text_sha256",
        "replacement_text",
        "replacement_text_sha256",
        "from_rung",
        "to_rung",
        "direction",
        "reason",
    ]
    for i, authorization in enumerate(authorizations):
        row_path = f"{path}[{i}]"
        v.obj(authorization, row_path, required)
        v.pattern(authorization["authorization_id"], f"{row_path}.authorization_id", _CLAIM_AUTH_RE, "CLAIM-AUTH-<id>")
        if authorization["authorization_id"] in seen:
            v.fail(path, f"duplicate authorization_id {authorization['authorization_id']!r}")
        seen.add(authorization["authorization_id"])
        v.pattern(authorization["author_event_id"], f"{row_path}.author_event_id", _AUTHOR_EVENT_RE, "AUTHOR-EVENT-<id>")
        v.pattern(authorization["surface_id"], f"{row_path}.surface_id", _CLAIM_SURFACE_RE, "CLAIM-SURFACE-<id>")
        v.pattern(authorization["scoped_manifest_id"], f"{row_path}.scoped_manifest_id", _MANIFEST_ID_RE, "scoped manifest id")
        v.pattern(authorization["claim_id"], f"{row_path}.claim_id", _CLAIM_ID_RE, "C-<n>")
        if authorization["block_id"] == "DOC-BODY-START":
            v.fail(f"{row_path}.block_id", "claim surfaces require an anchored B<n> block")
        v.pattern(authorization["block_id"], f"{row_path}.block_id", _BLOCK_ID_RE, "B<n>")
        for field in ("original_text_sha256", "replacement_text_sha256"):
            v.pattern(authorization[field], f"{row_path}.{field}", _SHA256_RE, "sha256 hex")
        v.string(authorization["replacement_text"], f"{row_path}.replacement_text", nonempty=False)
        if hashlib.sha256(authorization["replacement_text"].encode("utf-8")).hexdigest() != authorization["replacement_text_sha256"]:
            v.fail(row_path, "replacement_text_sha256 does not match replacement_text")
        for field in ("from_rung", "to_rung", "reason"):
            v.string(authorization[field], f"{row_path}.{field}")
        if authorization["from_rung"] == authorization["to_rung"]:
            v.fail(row_path, "from_rung and to_rung must differ")
        v.enum(authorization["direction"], f"{row_path}.direction", ("strengthen", "weaken"))


def _validate_tagged_anchors(v: _V, anchors, path):
    v.array(anchors, path)
    if not anchors:
        v.fail(path, "must carry at least one anchor")
    for i, entry in enumerate(anchors):
        v.obj(entry, f"{path}[{i}]", ["anchor", "anchor_artifact"])
        v.pattern(entry["anchor"], f"{path}[{i}].anchor", _ANCHOR_RE, "the Schema 6 typed-anchor grammar")
        v.enum(entry["anchor_artifact"], f"{path}[{i}].anchor_artifact", ("manuscript", "letter"))


def _validate_new_issue(v: _V, rec, path):
    v.obj(rec, path, [
        "new_issue_id", "description", "location_anchor", "severity", "found_by",
        "confidence", "competence_basis", "attribution", "attribution_evidence",
        "nearest_roadmap_item", "non_match_rationale",
    ])
    v.pattern(rec["new_issue_id"], f"{path}.new_issue_id", _ID_RES["NEW"], "NEW-<n>")
    v.string(rec["description"], f"{path}.description")
    v.pattern(rec["location_anchor"], f"{path}.location_anchor", _ANCHOR_RE, "typed anchor")
    v.enum(rec["severity"], f"{path}.severity", SEVERITIES)
    v.enum(rec["found_by"], f"{path}.found_by", VERIFIER_SEATS)
    v.integer(rec["confidence"], f"{path}.confidence", 1, 5)
    v.string(rec["competence_basis"], f"{path}.competence_basis")
    v.enum(rec["attribution"], f"{path}.attribution", ATTRIBUTIONS)
    v.string(rec["attribution_evidence"], f"{path}.attribution_evidence")
    nearest = rec["nearest_roadmap_item"]
    if nearest is not None:
        v.pattern(nearest, f"{path}.nearest_roadmap_item", _ITEM_ID_RE, "REV-<id> or null")
    v.string(rec["non_match_rationale"], f"{path}.non_match_rationale")


def validate_precommitment(art: dict):
    v = _V("phase1_lint_failed", "precommitment")
    v.obj(art, "$", ["contract_version", "round_id", "input_manifest_hash", "items", "new_standards"])
    v.enum(art["contract_version"], "$.contract_version", ("1.1",))
    v.string(art["round_id"], "$.round_id")
    v.pattern(art["input_manifest_hash"], "$.input_manifest_hash", _SHA256_RE, "sha256 hex")
    v.array(art["items"], "$.items")
    for i, rec in enumerate(art["items"]):
        path = f"$.items[{i}]"
        v.obj(rec, path, [
            "item_id", "obligation_class", "inherited_criterion", "operationalization",
            "expected_change_surface", "equivalence_policy", "source_reviewer",
            "source_reviewer_labels",
        ])
        v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.enum(rec["obligation_class"], f"{path}.obligation_class", ("must_fix", "should_fix"))
        crit = rec["inherited_criterion"]
        v.obj(crit, f"{path}.inherited_criterion", ["roadmap_text"], ["letter_text", "letter_item_ref"])
        v.string(crit["roadmap_text"], f"{path}.inherited_criterion.roadmap_text")
        has_text = "letter_text" in crit
        has_ref = "letter_item_ref" in crit
        if has_text != has_ref:
            v.fail(f"{path}.inherited_criterion", "letter_text and letter_item_ref are biconditional (§5.1)")
        if has_text:
            v.string(crit["letter_text"], f"{path}.inherited_criterion.letter_text")
            v.pattern(crit["letter_item_ref"], f"{path}.inherited_criterion.letter_item_ref", _LETTER_REF_RE, "R<n>")
            if rec["obligation_class"] != "must_fix":
                v.fail(f"{path}.inherited_criterion", "letter fields exist ONLY on must_fix items (§5.1)")
        op = rec["operationalization"]
        v.obj(op, f"{path}.operationalization", ["fully_addressed"], ["partially_addressed", "made_worse_discriminator"])
        v.string(op["fully_addressed"], f"{path}.operationalization.fully_addressed")
        if rec["obligation_class"] == "must_fix":
            for field in ("partially_addressed", "made_worse_discriminator"):
                if field not in op:
                    v.fail(f"{path}.operationalization", f"must_fix items require {field!r} (§5.1)")
                v.string(op[field], f"{path}.operationalization.{field}")
        else:
            for field in ("partially_addressed", "made_worse_discriminator"):
                if field in op:
                    v.fail(f"{path}.operationalization", f"should_fix lighter form forbids {field!r} (§5.1)")
        v.string(rec["expected_change_surface"], f"{path}.expected_change_surface")
        v.enum(rec["equivalence_policy"], f"{path}.equivalence_policy", ("allowed",))
        v.string(rec["source_reviewer"], f"{path}.source_reviewer")
        v.array(rec["source_reviewer_labels"], f"{path}.source_reviewer_labels")
        seen = set()
        for j, label in enumerate(rec["source_reviewer_labels"]):
            v.enum(label, f"{path}.source_reviewer_labels[{j}]", SEAT_LABELS)
            if label in seen:
                v.fail(f"{path}.source_reviewer_labels", f"duplicate label {label!r}")
            seen.add(label)
    v.array(art["new_standards"], "$.new_standards")
    ns_ids = set()
    for i, rec in enumerate(art["new_standards"]):
        path = f"$.new_standards[{i}]"
        v.obj(rec, path, ["new_standard_id", "item_id", "standard_text", "why_not_in_round1", "classification"])
        v.pattern(rec["new_standard_id"], f"{path}.new_standard_id", _ID_RES["NS"], "NS-<n>")
        if rec["new_standard_id"] in ns_ids:
            v.fail(path, f"duplicate new_standard_id {rec['new_standard_id']!r}")
        ns_ids.add(rec["new_standard_id"])
        if rec["item_id"] != "global":
            v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, 'REV-<id> or "global"')
        v.string(rec["standard_text"], f"{path}.standard_text")
        v.string(rec["why_not_in_round1"], f"{path}.why_not_in_round1")
        v.enum(rec["classification"], f"{path}.classification", ("advisory", "escalation_requested"))


def validate_verdict_record(art: dict):
    v = _V("phase2a_lint_failed", "verdict_record")
    v.obj(art, "$", ["contract_version", "round_id", "precommitment_hash", "items", "new_issues", "dissents", "escalation_exceptions"])
    v.enum(art["contract_version"], "$.contract_version", ("1.1",))
    v.string(art["round_id"], "$.round_id")
    v.pattern(art["precommitment_hash"], "$.precommitment_hash", _SHA256_RE, "sha256 hex")
    v.array(art["items"], "$.items")
    for i, rec in enumerate(art["items"]):
        path = f"$.items[{i}]"
        v.obj(rec, path, ["item_id", "verdict", "change_summary", "verified_by", "applied_criterion"],
              ["evidence_anchor", "cannot_verify_reason", "residual_gap"])
        v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.enum(rec["verdict"], f"{path}.verdict", VERDICTS)
        if rec["verdict"] == "CANNOT_VERIFY":
            if "cannot_verify_reason" not in rec or "evidence_anchor" in rec:
                v.fail(path, "CANNOT_VERIFY carries cannot_verify_reason and no evidence_anchor (§3.3)")
            v.string(rec["cannot_verify_reason"], f"{path}.cannot_verify_reason")
        else:
            if "evidence_anchor" not in rec or "cannot_verify_reason" in rec:
                v.fail(path, "non-CANNOT_VERIFY verdicts carry evidence_anchor and no cannot_verify_reason (§3.3)")
            v.array(rec["evidence_anchor"], f"{path}.evidence_anchor")
            if not rec["evidence_anchor"]:
                v.fail(f"{path}.evidence_anchor", "must carry at least one anchor")
            for j, anchor in enumerate(rec["evidence_anchor"]):
                v.pattern(anchor, f"{path}.evidence_anchor[{j}]", _ANCHOR_RE, "typed anchor")
        if rec["verdict"] == "PARTIALLY_ADDRESSED":
            if "residual_gap" not in rec:
                v.fail(path, "PARTIALLY_ADDRESSED requires residual_gap (§3.3)")
            _validate_residual_gap(v, rec["residual_gap"], f"{path}.residual_gap")
        elif "residual_gap" in rec:
            v.fail(path, "residual_gap is required iff verdict = PARTIALLY_ADDRESSED")
        v.string(rec["change_summary"], f"{path}.change_summary")
        v.enum(rec["verified_by"], f"{path}.verified_by", VERIFIER_SEATS)
        applied = rec["applied_criterion"]
        if applied not in ("precommitted", "not_precommitted") and not (
            isinstance(applied, str) and re.match(r"^dissented:DIS-[1-9][0-9]*$", applied)
        ):
            v.fail(f"{path}.applied_criterion", f"invalid value {applied!r}")
    v.array(art["new_issues"], "$.new_issues")
    for i, rec in enumerate(art["new_issues"]):
        _validate_new_issue(v, rec, f"$.new_issues[{i}]")
    v.array(art["dissents"], "$.dissents")
    for i, rec in enumerate(art["dissents"]):
        path = f"$.dissents[{i}]"
        v.obj(rec, path, [
            "dissent_id", "item_id", "criterion_hash", "reason_code",
            "original_operationalization", "replacement_operationalization",
            "evidence", "decision_impact_note",
        ])
        v.pattern(rec["dissent_id"], f"{path}.dissent_id", _ID_RES["DIS"], "DIS-<n>")
        v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.pattern(rec["criterion_hash"], f"{path}.criterion_hash", _SHA256_RE, "sha256 hex")
        v.enum(rec["reason_code"], f"{path}.reason_code",
               ("criterion_ambiguous", "criterion_infeasible_as_written", "evidence_surface_moved", "criterion_error"))
        for field in ("original_operationalization", "replacement_operationalization", "evidence", "decision_impact_note"):
            v.string(rec[field], f"{path}.{field}")
    v.array(art["escalation_exceptions"], "$.escalation_exceptions")
    for i, rec in enumerate(art["escalation_exceptions"]):
        path = f"$.escalation_exceptions[{i}]"
        v.obj(rec, path, [
            "exception_id", "escalation_class", "reason_code", "evidence_anchor",
            "why_round1_missed_it", "mechanical_decision_impact", "approval_state",
        ], ["new_standard_ref"])
        v.pattern(rec["exception_id"], f"{path}.exception_id", _ID_RES["ESC"], "ESC-<n>")
        if "new_standard_ref" in rec:
            v.pattern(rec["new_standard_ref"], f"{path}.new_standard_ref", _ID_RES["NS"], "NS-<n>")
        v.enum(rec["escalation_class"], f"{path}.escalation_class", ESCALATION_CLASSES)
        v.string(rec["reason_code"], f"{path}.reason_code")
        v.pattern(rec["evidence_anchor"], f"{path}.evidence_anchor", _ANCHOR_RE, "typed anchor")
        v.string(rec["why_round1_missed_it"], f"{path}.why_round1_missed_it")
        v.enum(rec["mechanical_decision_impact"], f"{path}.mechanical_decision_impact", ("Minor Revision", "Major Revision"))
        v.enum(rec["approval_state"], f"{path}.approval_state", ("pending",))


def _validate_adjustment_body(v: _V, rec, path, *, drafted: bool):
    required = ["item_id", "from_verdict", "to_verdict", "basis", "rationale"]
    optional = ["evidence_anchor", "cannot_verify_reason", "residual_gap"]
    if drafted:
        pass  # drafted bodies carry no booking-assigned fields
    else:
        required.insert(0, "adjustment_id")
        optional += ["critical_rebuttal_check", "source_ref", "supersedes_adjustment_id"]
    v.obj(rec, path, required, optional)
    if not drafted:
        v.pattern(rec["adjustment_id"], f"{path}.adjustment_id", _ID_RES["ADJ"], "ADJ-<n>")
        if "supersedes_adjustment_id" in rec:
            v.pattern(rec["supersedes_adjustment_id"], f"{path}.supersedes_adjustment_id", _ID_RES["ADJ"], "ADJ-<n>")
    v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
    v.enum(rec["from_verdict"], f"{path}.from_verdict", VERDICTS)
    v.enum(rec["to_verdict"], f"{path}.to_verdict", VERDICTS)
    if drafted:
        v.enum(rec["basis"], f"{path}.basis", ("valid_rebuttal",))
    else:
        v.enum(rec["basis"], f"{path}.basis", ADJUSTMENT_BASES)
    v.string(rec["rationale"], f"{path}.rationale")
    if rec["to_verdict"] == "CANNOT_VERIFY":
        if "cannot_verify_reason" not in rec or "evidence_anchor" in rec:
            v.fail(path, "to_verdict CANNOT_VERIFY carries cannot_verify_reason and no evidence_anchor")
        v.string(rec["cannot_verify_reason"], f"{path}.cannot_verify_reason")
        if rec["basis"] != "user_accepted_fail_closed":
            v.fail(path, "user_accepted_fail_closed is the ONLY basis that may land on CANNOT_VERIFY (§3.4)")
    else:
        if "evidence_anchor" not in rec or "cannot_verify_reason" in rec:
            v.fail(path, "non-CANNOT_VERIFY adjustments carry evidence_anchor and no cannot_verify_reason")
        _validate_tagged_anchors(v, rec["evidence_anchor"], f"{path}.evidence_anchor")
        if rec["basis"] in ("author_pointer_located_evidence", "scope_correction"):
            for j, anchor in enumerate(rec["evidence_anchor"]):
                if anchor["anchor_artifact"] != "manuscript":
                    v.fail(f"{path}.evidence_anchor[{j}]",
                           f"basis {rec['basis']} requires manuscript-side anchors (§5.3)")
    if rec["to_verdict"] == "PARTIALLY_ADDRESSED":
        if "residual_gap" not in rec:
            v.fail(path, "to_verdict PARTIALLY_ADDRESSED requires residual_gap (§5.3)")
        _validate_residual_gap(v, rec["residual_gap"], f"{path}.residual_gap")
    elif "residual_gap" in rec:
        v.fail(path, "residual_gap is required iff to_verdict = PARTIALLY_ADDRESSED")
    # §3.4 Direction column. valid_rebuttal — the only basis allowing
    # letter-side anchors — is "upgrade to FULLY_ADDRESSED"; anything else
    # would let a persuasive letter move a verdict sideways/downward, the
    # exact channel §1 exists to close. author_pointer_located_evidence is
    # an UPGRADE: located evidence satisfies the Phase-1 operationalization
    # (fully or partially), so the target is PARTIALLY/FULLY and strictly
    # better than the source (MADE_WORSE/CANNOT_VERIFY rank lowest).
    if rec["basis"] == "valid_rebuttal":
        if rec["to_verdict"] != "FULLY_ADDRESSED" or rec["from_verdict"] == "FULLY_ADDRESSED":
            v.fail(path, "valid_rebuttal adjustments upgrade to FULLY_ADDRESSED (§3.4 Direction)")
    elif rec["basis"] == "author_pointer_located_evidence":
        rank = {"MADE_WORSE": 0, "CANNOT_VERIFY": 0, "NOT_ADDRESSED": 1, "PARTIALLY_ADDRESSED": 2, "FULLY_ADDRESSED": 3}
        if rec["to_verdict"] not in ("PARTIALLY_ADDRESSED", "FULLY_ADDRESSED") or rank[rec["to_verdict"]] <= rank[rec["from_verdict"]]:
            v.fail(path, "author_pointer_located_evidence adjustments are upgrades to PARTIALLY/FULLY_ADDRESSED (§3.4 Direction)")
    if drafted:
        return
    source_ref = rec.get("source_ref")
    if rec["basis"] == "cross_model_adjudication":
        if not (isinstance(source_ref, str) and source_ref.startswith("reapplication:")):
            v.fail(path, 'basis cross_model_adjudication requires source_ref "reapplication:<id>"')
    elif rec["basis"] == "user_accepted_fail_closed":
        if not (isinstance(source_ref, str) and source_ref.startswith("acceptance:")):
            v.fail(path, 'basis user_accepted_fail_closed requires source_ref "acceptance:<id>"')
    elif source_ref is not None:
        v.fail(path, f"source_ref is FORBIDDEN on basis {rec['basis']} (§5.3)")
    if source_ref is not None:
        v.pattern(source_ref, f"{path}.source_ref", _SOURCE_REF_RE, "reapplication:RAP-<n> | acceptance:ACC-<n>")
    check = rec.get("critical_rebuttal_check")
    if check is not None:
        if rec["basis"] != "valid_rebuttal":
            v.fail(path, "critical_rebuttal_check exists only on valid_rebuttal adjustments (§3.4)")
        if check not in ("single_family_disclosed", "pass_unavailable_disclosed") and not _CHECK_ADJUDICATED_RE.match(check):
            v.fail(f"{path}.critical_rebuttal_check", f"invalid value {check!r}")


def validate_traceability(art: dict):
    v = _V("phase2b_lint_failed", "traceability")
    v.obj(art, "$", [
        "contract_version", "round_id", "revision", "verdict_record_hash", "rows", "adjustments",
        "new_issues", "post_letter_observations", "dissent_adjudications",
        "resolution_intents", "cross_model_resolutions", "rebuttal_adjudications",
        "g2d_acceptances", "pending_rebuttal_upgrades", "escalation_approvals",
        "reapplications", "decision_inputs", "decision_state",
    ], ["supersedes_hash", "abort_reason"])
    v.enum(art["contract_version"], "$.contract_version", ("1.1",))
    v.string(art["round_id"], "$.round_id")
    v.integer(art["revision"], "$.revision", minimum=1)
    if art["revision"] == 1:
        if "supersedes_hash" in art:
            v.fail("$", "revision 1 must not carry supersedes_hash")
    else:
        if "supersedes_hash" not in art:
            v.fail("$", "revision >= 2 requires supersedes_hash")
        v.pattern(art["supersedes_hash"], "$.supersedes_hash", _SHA256_RE, "sha256 hex")
    v.pattern(art["verdict_record_hash"], "$.verdict_record_hash", _SHA256_RE, "sha256 hex")
    v.enum(art["decision_state"], "$.decision_state", DECISION_STATES)
    if art["decision_state"] == "aborted":
        if "abort_reason" not in art:
            v.fail("$", "decision_state aborted requires abort_reason")
        v.enum(art["abort_reason"], "$.abort_reason", ABORT_REASONS)
    elif "abort_reason" in art:
        v.fail("$", "abort_reason is required iff decision_state = aborted")

    v.array(art["rows"], "$.rows")
    for i, row in enumerate(art["rows"]):
        path = f"$.rows[{i}]"
        v.obj(row, path, [
            "item_id", "concern_id", "obligation_class", "original_comment", "authors_claim",
            "revision_location", "verified", "status", "quality_assessment",
            "final_verdict", "phase2a_verdict", "verified_by", "author_triage",
            "authorized_targets", "claim_strength_authorizations",
        ], ["adjustment_id", "addressed_by_rebuttal", "cross_model_status", "cross_model_verdict", "author_reason"])
        v.pattern(row["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.pattern(row["concern_id"], f"{path}.concern_id", _CONCERN_ID_RE, "R<n>/S<n>/N<n>")
        v.enum(row["obligation_class"], f"{path}.obligation_class", tuple(ROW_OBLIGATION_MAP))
        for field in ("original_comment", "authors_claim", "revision_location", "quality_assessment"):
            v.string(row[field], f"{path}.{field}")
        v.enum(row["verified"], f"{path}.verified", ("YES", "PARTIAL", "NO", "CANNOT_VERIFY"))
        v.enum(row["status"], f"{path}.status", VERDICTS)
        v.enum(row["final_verdict"], f"{path}.final_verdict", VERDICTS)
        v.enum(row["phase2a_verdict"], f"{path}.phase2a_verdict", VERDICTS)
        v.enum(row["verified_by"], f"{path}.verified_by", VERIFIER_SEATS)
        v.enum(
            row["author_triage"],
            f"{path}.author_triage",
            ("will_address", "wont_address", "not_on_point"),
        )
        _validate_author_targets(v, row["authorized_targets"], f"{path}.authorized_targets")
        _validate_claim_authorizations(
            v,
            row["claim_strength_authorizations"],
            f"{path}.claim_strength_authorizations",
        )
        if row["author_triage"] in ("wont_address", "not_on_point"):
            if "author_reason" not in row:
                v.fail(path, "declined author triage requires author_reason")
            v.string(row["author_reason"], f"{path}.author_reason")
            if row["authorized_targets"] or row["claim_strength_authorizations"]:
                v.fail(path, "declined author triage carries no work/claim authority")
        elif "author_reason" in row:
            v.fail(path, "will_address rows do not carry an inferred author_reason")
        if "adjustment_id" in row:
            v.pattern(row["adjustment_id"], f"{path}.adjustment_id", _ID_RES["ADJ"], "ADJ-<n>")
        if "addressed_by_rebuttal" in row and row["addressed_by_rebuttal"] is not True:
            v.fail(f"{path}.addressed_by_rebuttal", "when present the marker is the literal true")
        has_status = "cross_model_status" in row
        has_cmv = "cross_model_verdict" in row
        if row["obligation_class"] == "MUST_FIX":
            if not has_status:
                v.fail(path, "MUST_FIX rows always carry cross_model_status (§5.3 / #539)")
        elif has_status or has_cmv:
            v.fail(path, "SHOULD_FIX/CONSIDER rows carry neither cross-model field (#539 scope)")
        if has_status:
            v.enum(row["cross_model_status"], f"{path}.cross_model_status",
                   ("agree", "diverges", "unavailable", "not_configured"))
            if row["cross_model_status"] in ("agree", "diverges"):
                if not has_cmv:
                    v.fail(path, "evaluated (agree/diverges) rows carry cross_model_verdict")
                v.enum(row["cross_model_verdict"], f"{path}.cross_model_verdict", JUDGE_VERDICTS)
            elif has_cmv:
                v.fail(path, "unavailable/not_configured rows carry no cross_model_verdict")

    v.array(art["adjustments"], "$.adjustments")
    for i, rec in enumerate(art["adjustments"]):
        _validate_adjustment_body(v, rec, f"$.adjustments[{i}]", drafted=False)

    v.array(art["new_issues"], "$.new_issues")
    for i, rec in enumerate(art["new_issues"]):
        _validate_new_issue(v, rec, f"$.new_issues[{i}]")

    v.array(art["post_letter_observations"], "$.post_letter_observations")
    for i, entry in enumerate(art["post_letter_observations"]):
        v.string(entry, f"$.post_letter_observations[{i}]")

    v.array(art["dissent_adjudications"], "$.dissent_adjudications")
    for i, rec in enumerate(art["dissent_adjudications"]):
        path = f"$.dissent_adjudications[{i}]"
        v.obj(rec, path, ["dissent_id", "adjudicator", "outcome", "rationale"])
        v.pattern(rec["dissent_id"], f"{path}.dissent_id", _ID_RES["DIS"], "DIS-<n>")
        v.enum(rec["adjudicator"], f"{path}.adjudicator", ("cross_model", "user"))
        v.enum(rec["outcome"], f"{path}.outcome", ("replacement_approved", "original_upheld"))
        v.string(rec["rationale"], f"{path}.rationale")

    v.array(art["resolution_intents"], "$.resolution_intents")
    for i, rec in enumerate(art["resolution_intents"]):
        path = f"$.resolution_intents[{i}]"
        v.obj(rec, path, ["intent_id", "item_id", "answered_by"], ["guidance_note"])
        v.pattern(rec["intent_id"], f"{path}.intent_id", _ID_RES["INT"], "INT-<n>")
        v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.enum(rec["answered_by"], f"{path}.answered_by", ("system", "user"))
        if "guidance_note" in rec:
            if rec["answered_by"] == "system":
                v.fail(path, "guidance_note exists only on user intents (§5.3)")
            v.string(rec["guidance_note"], f"{path}.guidance_note")

    v.array(art["cross_model_resolutions"], "$.cross_model_resolutions")
    for i, rec in enumerate(art["cross_model_resolutions"]):
        path = f"$.cross_model_resolutions[{i}]"
        v.obj(rec, path, ["resolution_id", "item_id", "intent_id", "reapplication_id", "state", "resolved_by", "rationale"])
        v.pattern(rec["resolution_id"], f"{path}.resolution_id", _ID_RES["RES"], "RES-<n>")
        v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.pattern(rec["intent_id"], f"{path}.intent_id", _ID_RES["INT"], "INT-<n>")
        v.pattern(rec["reapplication_id"], f"{path}.reapplication_id", _ID_RES["RAP"], "RAP-<n>")
        v.enum(rec["state"], f"{path}.state", ("primary_upheld", "primary_revised"))
        v.enum(rec["resolved_by"], f"{path}.resolved_by", ("system", "user"))
        if rec["resolved_by"] == "user" and rec["state"] != "primary_upheld":
            v.fail(path, "the user acceptance form is always primary_upheld — the user never hand-sets a verdict (§5.3)")
        v.string(rec["rationale"], f"{path}.rationale")

    v.array(art["rebuttal_adjudications"], "$.rebuttal_adjudications")
    for i, rec in enumerate(art["rebuttal_adjudications"]):
        path = f"$.rebuttal_adjudications[{i}]"
        v.obj(rec, path, ["rebuttal_adjudication_id", "item_id", "verdict", "rationale"])
        v.pattern(rec["rebuttal_adjudication_id"], f"{path}.rebuttal_adjudication_id", _ID_RES["RADJ"], "RADJ-<n>")
        v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.enum(rec["verdict"], f"{path}.verdict", ("upheld", "challenged"))
        v.string(rec["rationale"], f"{path}.rationale")

    v.array(art["g2d_acceptances"], "$.g2d_acceptances")
    for i, rec in enumerate(art["g2d_acceptances"]):
        path = f"$.g2d_acceptances[{i}]"
        v.obj(rec, path, ["acceptance_id", "item_id", "reapplication_id", "accepted_by"])
        v.pattern(rec["acceptance_id"], f"{path}.acceptance_id", _ID_RES["ACC"], "ACC-<n>")
        v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.pattern(rec["reapplication_id"], f"{path}.reapplication_id", _ID_RES["RAP"], "RAP-<n>")
        v.enum(rec["accepted_by"], f"{path}.accepted_by", ("user",))

    v.array(art["pending_rebuttal_upgrades"], "$.pending_rebuttal_upgrades")
    for i, rec in enumerate(art["pending_rebuttal_upgrades"]):
        path = f"$.pending_rebuttal_upgrades[{i}]"
        v.obj(rec, path, ["proposal_id", "item_id", "drafted_adjustment", "disposition"])
        v.pattern(rec["proposal_id"], f"{path}.proposal_id", _ID_RES["PRB"], "PRB-<n>")
        v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        _validate_adjustment_body(v, rec["drafted_adjustment"], f"{path}.drafted_adjustment", drafted=True)
        disposition = rec["disposition"]
        if not isinstance(disposition, str) or not re.match(
            r"^(booked:ADJ-[1-9][0-9]*|challenged:RADJ-[1-9][0-9]*|booked_disclosed:ADJ-[1-9][0-9]*|booked_single_family:ADJ-[1-9][0-9]*)$",
            disposition,
        ):
            v.fail(f"{path}.disposition", f"invalid disposition {disposition!r}")

    v.array(art["escalation_approvals"], "$.escalation_approvals")
    for i, rec in enumerate(art["escalation_approvals"]):
        path = f"$.escalation_approvals[{i}]"
        v.obj(rec, path, ["exception_id", "approval_state", "approved_by"])
        v.pattern(rec["exception_id"], f"{path}.exception_id", _ID_RES["ESC"], "ESC-<n>")
        v.enum(rec["approval_state"], f"{path}.approval_state", ("approved", "rejected"))
        v.enum(rec["approved_by"], f"{path}.approved_by", ("user",))

    v.array(art["reapplications"], "$.reapplications")
    for i, rec in enumerate(art["reapplications"]):
        path = f"$.reapplications[{i}]"
        v.obj(rec, path, [
            "reapplication_id", "item_id", "answer_refs", "pre_reapplication_verdict",
            "reapplied_verdict", "rationale", "criterion_ref",
        ], ["supersedes_reapplication_id", "evidence_anchor", "cannot_verify_reason", "residual_gap"])
        v.pattern(rec["reapplication_id"], f"{path}.reapplication_id", _ID_RES["RAP"], "RAP-<n>")
        v.pattern(rec["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.array(rec["answer_refs"], f"{path}.answer_refs")
        if not rec["answer_refs"]:
            v.fail(f"{path}.answer_refs", "must carry at least one tagged ref")
        seen_refs = set()
        for j, ref in enumerate(rec["answer_refs"]):
            v.pattern(ref, f"{path}.answer_refs[{j}]", _ANSWER_REF_RE, "adjudication:DIS-<n> | intent:INT-<n>")
            if ref in seen_refs:
                v.fail(f"{path}.answer_refs", f"duplicate ref {ref!r}")
            seen_refs.add(ref)
        if "supersedes_reapplication_id" in rec:
            v.pattern(rec["supersedes_reapplication_id"], f"{path}.supersedes_reapplication_id", _ID_RES["RAP"], "RAP-<n>")
        v.enum(rec["pre_reapplication_verdict"], f"{path}.pre_reapplication_verdict", VERDICTS)
        v.enum(rec["reapplied_verdict"], f"{path}.reapplied_verdict", VERDICTS)
        if rec["reapplied_verdict"] == "CANNOT_VERIFY":
            if "cannot_verify_reason" not in rec or "evidence_anchor" in rec:
                v.fail(path, "CANNOT_VERIFY carries cannot_verify_reason and no evidence_anchor")
            v.string(rec["cannot_verify_reason"], f"{path}.cannot_verify_reason")
        else:
            if "evidence_anchor" not in rec or "cannot_verify_reason" in rec:
                v.fail(path, "non-CANNOT_VERIFY reapplications carry evidence_anchor and no cannot_verify_reason")
            _validate_tagged_anchors(v, rec["evidence_anchor"], f"{path}.evidence_anchor")
        if rec["reapplied_verdict"] == "PARTIALLY_ADDRESSED":
            if "residual_gap" not in rec:
                v.fail(path, "reapplied PARTIALLY_ADDRESSED requires residual_gap")
            _validate_residual_gap(v, rec["residual_gap"], f"{path}.residual_gap")
        elif "residual_gap" in rec:
            v.fail(path, "residual_gap is required iff reapplied_verdict = PARTIALLY_ADDRESSED")
        v.string(rec["rationale"], f"{path}.rationale")
        v.pattern(rec["criterion_ref"], f"{path}.criterion_ref", _CRITERION_REF_RE, "phase1:REV-<id> | dissent:DIS-<n>")

    di = art["decision_inputs"]
    v.obj(di, "$.decision_inputs", [
        "per_item", "verdict_counts", "residual_obligation_class_counts", "should_fix_addressed_rate",
        "regressions", "non_regression_new_issue_ids", "escalations", "apply_chain_witness",
    ], ["reject_recommended"])
    v.array(di["per_item"], "$.decision_inputs.per_item")
    for i, entry in enumerate(di["per_item"]):
        path = f"$.decision_inputs.per_item[{i}]"
        v.obj(entry, path, ["item_id", "final_verdict", "driving_severity"], ["residual_obligation_class"])
        v.pattern(entry["item_id"], f"{path}.item_id", _ITEM_ID_RE, "REV-<id>")
        v.enum(entry["final_verdict"], f"{path}.final_verdict", VERDICTS)
        if entry["driving_severity"] is not None:
            v.enum(entry["driving_severity"], f"{path}.driving_severity", SEVERITIES)
        if "residual_obligation_class" in entry:
            v.enum(entry["residual_obligation_class"], f"{path}.residual_obligation_class", RESIDUAL_OBLIGATION_CLASSES)
    for bucket_name in ("verdict_counts", "residual_obligation_class_counts"):
        bucket = di[bucket_name]
        v.obj(bucket, f"$.decision_inputs.{bucket_name}", list(OBLIGATION_CLASSES))
        keys = VERDICTS if bucket_name == "verdict_counts" else RESIDUAL_OBLIGATION_CLASSES
        for prio in OBLIGATION_CLASSES:
            v.obj(bucket[prio], f"$.decision_inputs.{bucket_name}.{prio}", list(keys))
            for key in keys:
                v.integer(bucket[prio][key], f"$.decision_inputs.{bucket_name}.{prio}.{key}", minimum=0)
    rate = di["should_fix_addressed_rate"]
    v.obj(rate, "$.decision_inputs.should_fix_addressed_rate", ["numerator", "denominator"])
    v.integer(rate["numerator"], "$.decision_inputs.should_fix_addressed_rate.numerator", minimum=0)
    v.integer(rate["denominator"], "$.decision_inputs.should_fix_addressed_rate.denominator", minimum=0)
    v.array(di["regressions"], "$.decision_inputs.regressions")
    for i, entry in enumerate(di["regressions"]):
        path = f"$.decision_inputs.regressions[{i}]"
        v.obj(entry, path, ["new_issue_id", "severity"])
        v.pattern(entry["new_issue_id"], f"{path}.new_issue_id", _ID_RES["NEW"], "NEW-<n>")
        v.enum(entry["severity"], f"{path}.severity", SEVERITIES)
    v.array(di["non_regression_new_issue_ids"], "$.decision_inputs.non_regression_new_issue_ids")
    for i, entry in enumerate(di["non_regression_new_issue_ids"]):
        v.pattern(entry, f"$.decision_inputs.non_regression_new_issue_ids[{i}]", _ID_RES["NEW"], "NEW-<n>")
    v.array(di["escalations"], "$.decision_inputs.escalations")
    for i, entry in enumerate(di["escalations"]):
        path = f"$.decision_inputs.escalations[{i}]"
        v.obj(entry, path, ["exception_id", "effective_approval_state", "escalation_class", "mechanical_decision_impact"])
        v.pattern(entry["exception_id"], f"{path}.exception_id", _ID_RES["ESC"], "ESC-<n>")
        v.enum(entry["effective_approval_state"], f"{path}.effective_approval_state", ("pending", "approved", "rejected"))
        v.enum(entry["escalation_class"], f"{path}.escalation_class", ESCALATION_CLASSES)
        v.enum(entry["mechanical_decision_impact"], f"{path}.mechanical_decision_impact", ("Minor Revision", "Major Revision"))
    if "reject_recommended" in di and not isinstance(di["reject_recommended"], bool):
        v.fail("$.decision_inputs.reject_recommended", "must be a boolean")
    v.enum(di["apply_chain_witness"], "$.decision_inputs.apply_chain_witness", WITNESS_STATES)


# --- manifest ------------------------------------------------------------------


def validate_manifest(manifest: dict):
    """Structural manifest validation (§11). Failures -> manifest_incomplete."""

    def fail(message: str):
        raise ManifestError("manifest_incomplete", f"manifest: {message}")

    if not isinstance(manifest, dict):
        fail("must be an object")
    expected_top = {"contract_version", "round_id", "cross_model_active", "artifacts"}
    if set(manifest) != expected_top:
        fail(f"top-level fields must be exactly {sorted(expected_top)}")
    if manifest["contract_version"] != "1.1":
        fail("contract_version must be current 1.1; legacy/mixed chains use the archived loader")
    if not _is_str(manifest["round_id"]):
        fail("round_id must be a non-empty string")
    if not isinstance(manifest["cross_model_active"], bool):
        fail("cross_model_active must be a boolean")
    artifacts = manifest["artifacts"]
    single_keys = (
        "original_manuscript", "revised_manuscript", "revision_roadmap",
        "author_adjudication", "revision_evidence_bundle",
        "editorial_decision_letter", "response_to_reviewers",
        "round1_findings", "round1_config_cards",
    )
    array_keys = ("revision_patches", "apply_reports")
    if not isinstance(artifacts, dict) or set(artifacts) != set(single_keys) | set(array_keys):
        fail("artifacts must carry exactly the eleven current §11 keys")

    def check_entry_fields(entry, key, path):
        ref = entry.get("path_or_passport_ref")
        if not _is_str(ref) or not _ARTIFACT_REF_RE.match(ref):
            fail(f"{path}: path_or_passport_ref must be passport:<ref> | path:<relative path>")
        if ref.startswith("path:"):
            rel = ref[len("path:"):]
            segments = re.split(r"[/\\]", rel)
            if (
                rel.startswith(("/", "\\"))
                or re.match(r"^[A-Za-z]:", rel)
                or any(segment == ".." for segment in segments)
                or not rel
            ):
                fail(f"{path}: path: refs carry a RELATIVE path — no absolute, drive-letter, or traversal segments (§11)")
        sha = entry.get("sha256")
        if not isinstance(sha, str) or not _SHA256_RE.match(sha):
            fail(f"{path}: sha256 must be 64-hex")
        for field in ("version_label", "origin_date"):
            value = entry.get(field, "MISSING")
            if value == "MISSING":
                fail(f"{path}: missing {field}")
            if value is not None and not _is_str(value):
                fail(f"{path}: {field} must be a non-empty string or null")
            if value is None and entry["path_or_passport_ref"].startswith("passport:"):
                fail(f"{path}: null {field} on a passport:-tagged entry (§11)")

    for key in single_keys:
        entry = artifacts[key]
        if not isinstance(entry, dict) or not isinstance(entry.get("present"), bool):
            fail(f"artifacts.{key}: present-discriminated union required")
        if entry["present"]:
            if set(entry) != {"present", "path_or_passport_ref", "sha256", "version_label", "origin_date"}:
                fail(f"artifacts.{key}: present entry carries exactly ref/sha256/version_label/origin_date")
            check_entry_fields(entry, key, f"artifacts.{key}")
        elif set(entry) != {"present"}:
            fail(f"artifacts.{key}: an absent artifact carries NO ref, hash, or freshness fields (§11)")
    for key in array_keys:
        entry = artifacts[key]
        if not isinstance(entry, dict) or not isinstance(entry.get("present"), bool):
            fail(f"artifacts.{key}: present-discriminated union required")
        if entry["present"]:
            if set(entry) != {"present", "items"}:
                fail(f"artifacts.{key}: present array entry carries exactly items")
            items = entry["items"]
            if not isinstance(items, list) or not items:
                fail(f"artifacts.{key}: present: false is the canonical empty encoding (§11)")
            for i, element in enumerate(items):
                if not isinstance(element, dict) or set(element) != {"path_or_passport_ref", "sha256", "version_label", "origin_date"}:
                    fail(f"artifacts.{key}[{i}]: every element FULLY populated (no per-element absence)")
                check_entry_fields(element, key, f"artifacts.{key}[{i}]")
        elif set(entry) != {"present"}:
            fail(f"artifacts.{key}: an absent artifact carries NO ref, hash, or freshness fields (§11)")

    # Required set + array pairing (G0).
    for key in (
        "original_manuscript",
        "revised_manuscript",
        "revision_roadmap",
        "author_adjudication",
        "revision_evidence_bundle",
    ):
        if not artifacts[key]["present"]:
            raise ManifestError("manifest_incomplete", f"manifest: hard-required artifact {key} absent (§11)")
    patches = artifacts["revision_patches"]
    reports = artifacts["apply_reports"]
    if patches["present"] != reports["present"]:
        raise ManifestError(
            "manifest_incomplete",
            "manifest: revision_patches and apply_reports must travel together (§11)",
        )
    if reports["present"]:
        if len(reports["items"]) != len(patches["items"]):
            raise ManifestError("manifest_incomplete", "manifest: apply_reports / revision_patches length mismatch (§11)")

    # Freshness: a roadmap older than the letter it should pair with fails
    # closed (§11). Comparable only when both origin_dates are non-null.
    roadmap_entry = artifacts["revision_roadmap"]
    letter_entry = artifacts["editorial_decision_letter"]
    if letter_entry["present"] and roadmap_entry["origin_date"] is not None and letter_entry["origin_date"] is not None:
        if roadmap_entry["origin_date"] < letter_entry["origin_date"]:
            raise ManifestError(
                "manifest_hash_mismatch",
                "manifest: revision_roadmap origin_date predates editorial_decision_letter (freshness, §11)",
            )


def _hash_prefix(sha256_hex: str) -> str:
    """§11: apply reports use the 12-hex base_draft_hash format."""
    return sha256_hex[:12]


def compute_apply_chain_witness(manifest: dict, report_payloads):
    """§11 apply-chain witness over the ordered report payloads.

    Returns (witness, notes). A broken checked link raises ManifestError
    (manifest_hash_mismatch, G0) — positive breakage evidence outranks the
    absence markers, matching the declared precedence
    fail > not_run_no_reports > pass.
    """
    artifacts = manifest["artifacts"]
    notes = []
    if not report_payloads:
        return "not_run_no_reports", notes
    patches = artifacts["revision_patches"]["items"]
    for i, report in enumerate(report_payloads):
        if not isinstance(report, dict):
            raise ManifestError("manifest_incomplete", f"apply report [{i}]: must be a JSON object")
        for field in ("report_format_version", "base_draft_hash", "output_draft_hash"):
            if not _is_str(report.get(field)):
                raise ManifestError("manifest_incomplete", f"apply report [{i}]: missing {field}")
        if not _REPORT_VERSION_RE.match(report["report_format_version"]):
            raise ManifestError(
                "manifest_incomplete",
                f"apply report [{i}]: report_format_version {report['report_format_version']!r} is not a numeric "
                "dotted version; current contract requires exact report format 1.3 (§11)",
            )
        for field in ("base_draft_hash", "output_draft_hash"):
            if not _HASH12_RE.match(report[field]):
                raise ManifestError(
                    "manifest_incomplete",
                    f"apply report [{i}]: {field} must be the 12-hex base_draft_hash format (§11)",
                )
        version = tuple(int(part) for part in report["report_format_version"].split("."))
        if version != (1, 3):
            raise ManifestError(
                "manifest_incomplete",
                f"apply report [{i}]: current contract requires report format 1.3; legacy reports use the archived loader",
            )
        digest = report.get("patch_digest")
        if not isinstance(digest, str) or not _SHA256_RE.match(digest):
            raise ManifestError("manifest_incomplete", f"apply report [{i}]: format 1.3 requires patch_digest")
        if digest != patches[i]["sha256"]:
            raise ManifestError(
                "manifest_hash_mismatch",
                f"apply report [{i}]: patch_digest does not equal the paired revision_patches[{i}].sha256 (§11 content-bound pairing)",
            )
        authorization = report.get("authorization_witness")
        if not isinstance(authorization, dict) or authorization.get("status") not in (
            "pass",
            "not_applicable_integrity_correction",
        ):
            raise ManifestError(
                "manifest_incomplete",
                f"apply report [{i}]: format 1.3 requires a current replayed authorization_witness",
            )
        if authorization.get("unregistered_claim_drift_review_required") is not True:
            raise ManifestError(
                "manifest_incomplete",
                f"apply report [{i}]: authorization witness must surface the E6 unregistered-claim review boundary",
            )
    original = artifacts["original_manuscript"]
    if not original["present"]:
        raise ManifestError(
            "manifest_incomplete",
            "apply-chain witness: current contract hard-requires original_manuscript",
        )
    if report_payloads[0]["base_draft_hash"] != _hash_prefix(original["sha256"]):
        raise ManifestError(
            "manifest_hash_mismatch",
            "apply-chain witness: first report base_draft_hash does not equal the original_manuscript hash prefix (§11)",
        )
    for i in range(1, len(report_payloads)):
        if report_payloads[i]["base_draft_hash"] != report_payloads[i - 1]["output_draft_hash"]:
            raise ManifestError(
                "manifest_hash_mismatch",
                f"apply-chain witness: report [{i}] base_draft_hash does not equal report [{i - 1}] output_draft_hash (§11)",
            )
    revised = artifacts["revised_manuscript"]
    if report_payloads[-1]["output_draft_hash"] != _hash_prefix(revised["sha256"]):
        raise ManifestError(
            "manifest_hash_mismatch",
            "apply-chain witness: last report output_draft_hash does not equal the revised_manuscript hash prefix (§11)",
        )
    return "pass", notes


def validate_revision_bundle_binding(bundle: dict, manifest: dict) -> None:
    """Bind the replayed bundle to the exact §11 current-round artifacts."""
    artifacts = manifest["artifacts"]
    revised_sha = artifacts["revised_manuscript"]["sha256"]
    if bundle["final_draft"]["sha256"] != revised_sha:
        raise ManifestError(
            "manifest_hash_mismatch",
            "revision_evidence_bundle.final_draft does not equal revised_manuscript",
        )

    roadmap_sha = artifacts["revision_roadmap"]["sha256"]
    author_sha = artifacts["author_adjudication"]["sha256"]
    partial_matches = []
    exact_matches = []
    for index, row in enumerate(bundle["rounds"]):
        if row["kind"] not in ("review_roadmap", "review_noop"):
            continue
        roadmap_match = row["revision_roadmap"]["sha256"] == roadmap_sha
        author_match = row["author_adjudication"]["sha256"] == author_sha
        if roadmap_match != author_match:
            partial_matches.append(index)
        if roadmap_match and author_match:
            exact_matches.append((index, row))
    if partial_matches:
        raise ManifestError(
            "manifest_hash_mismatch",
            "revision_evidence_bundle splits the current roadmap/author pair across rounds",
        )
    if len(exact_matches) != 1:
        raise ManifestError(
            "manifest_hash_mismatch",
            "revision_evidence_bundle must contain exactly one round with the exact current roadmap/author pair",
        )

    _index, current = exact_matches[0]
    original = artifacts["original_manuscript"]
    if original["present"] and current["pre_round_draft"]["sha256"] != original["sha256"]:
        raise ManifestError(
            "manifest_hash_mismatch",
            "revision_evidence_bundle current round pre draft differs from original_manuscript",
        )
    bundle_pairs = [
        (row["revision_patch"]["sha256"], row["apply_report"]["sha256"])
        for row in bundle["rounds"]
        if row["kind"] in ("review_roadmap", "integrity_correction")
    ]
    patches = artifacts["revision_patches"]
    reports = artifacts["apply_reports"]
    if patches["present"] != reports["present"]:
        raise ManifestError(
            "manifest_incomplete",
            "revision_evidence_bundle cannot bind asymmetric revision_patches/apply_reports state",
        )
    manifest_pairs = []
    if patches["present"] and reports["present"]:
        manifest_pairs = [
            (patch["sha256"], report["sha256"])
            for patch, report in zip(patches["items"], reports["items"])
        ]
    if bundle_pairs != manifest_pairs:
        raise ManifestError(
            "manifest_hash_mismatch",
            "revision_evidence_bundle ordered write patch/report pairs differ from the input manifest",
        )


# --- letter + roadmap parsing --------------------------------------------------

_LETTER_SECTION_RE = re.compile(r"^### Required Item Details\s*$")
_LETTER_BLOCK_RE = re.compile(r"^\*\*(R[1-9][0-9]*): .*\*\*\s*$")
_LETTER_CRITERIA_RE = re.compile(r"^- \*\*Acceptance criteria\*\*: (.*)$")


def parse_letter_blocks(text: str):
    """Extract the letter's Required Item Details blocks in document order.

    Returns an ordered list of (rid, acceptance_text) where acceptance_text
    is the single-line payload after the ``- **Acceptance criteria**:``
    bullet, or None when the block carries no such bullet (a block without
    an Acceptance-criteria field offers nothing to inherit — treated as
    no-block-at-ordinal for the §5.1 letter-fields rule; its id still
    participates in the contiguity check).
    """
    lines = text.splitlines()
    blocks = []
    in_section = False
    current = None
    for line in lines:
        if _LETTER_SECTION_RE.match(line):
            in_section = True
            continue
        if not in_section:
            continue
        if line.startswith("## "):
            break
        header = _LETTER_BLOCK_RE.match(line)
        if header:
            current = [header.group(1), None]
            blocks.append(current)
            continue
        if current is not None and current[1] is None:
            criteria = _LETTER_CRITERIA_RE.match(line)
            if criteria:
                current[1] = criteria.group(1)
    return [(rid, text_value) for rid, text_value in blocks]


def letter_ordinals_sound(blocks, must_fix_count: int) -> bool:
    """§5.1 contiguity: ids EXACTLY the contiguous sequence R1..Rk, k <= n.

    A gap, duplicate, or extra id (beyond the must_fix count) makes the
    ordinal derivation unsound and degrades the WHOLE letter layer to
    absent; a mere count shortfall (contiguous prefix) does not.
    """
    for i, (rid, _text) in enumerate(blocks):
        if rid != f"R{i + 1}":
            return False
    return len(blocks) <= must_fix_count


def load_roadmap(payload: dict):
    """Minimal Schema 7 machine-form validation for checker consumption."""

    def fail(message: str):
        raise ManifestError("manifest_incomplete", f"revision_roadmap: {message}")

    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        fail("must be an object with an items array (Schema 7)")
    items = []
    seen = set()
    for i, item in enumerate(payload["items"]):
        if not isinstance(item, dict):
            fail(f"items[{i}] must be an object")
        for field in ("id", "obligation_class", "verification_criteria", "reviewer"):
            if not _is_str(item.get(field)):
                fail(f"items[{i}].{field} must be a non-empty string")
        if not _ITEM_ID_RE.match(item["id"]):
            fail(f"items[{i}].id must be REV-<id>")
        if item["id"] in seen:
            fail(f"duplicate roadmap id {item['id']!r}")
        seen.add(item["id"])
        if item["obligation_class"] not in OBLIGATION_CLASSES:
            fail(f"items[{i}].obligation_class must be one of {OBLIGATION_CLASSES}")
        severity = item.get("severity")
        if severity is not None and severity not in SEVERITIES:
            fail(f"items[{i}].severity must be one of {SEVERITIES} when present")
        source_kind = item.get("source_kind")
        if source_kind is not None and source_kind not in ("question", "editorial"):
            fail(f"items[{i}].source_kind must be question|editorial when present")
        transported = {
            "severity",
            "severity_source",
            "evidence_anchor",
            "confidence",
            "competence_basis",
            "confidence_source",
            "corroborating_sources",
        }
        if source_kind is None:
            for field in ("severity", "evidence_anchor", "confidence", "competence_basis"):
                if field not in item:
                    fail(f"items[{i}] finding-driven row requires transported {field}")
        elif transported & set(item):
            fail(f"items[{i}] source_kind row must not carry transported finding fields")
        items.append(item)
    return items


def load_author_adjudication(
    payload: dict,
    *,
    roadmap_items: list[dict],
    roadmap_sha256: str,
    original_manuscript_sha256: str | None,
):
    """Validate the #670 sidecar projection this consumer copies.

    Full target/claim-surface replay already occurs at patch apply and bundle
    validation. This consumer independently validates the closed sidecar shape,
    exact roadmap/base bindings, explicit user-event references, full item
    cardinality, and the author-owned fields Schema 11 must copy unchanged.
    """

    def fail(message: str):
        raise ManifestError("manifest_incomplete", f"author_adjudication: {message}")

    expected_top = {
        "schema_version",
        "revision_round",
        "roadmap_sha256",
        "base_draft_sha256",
        "claim_surface_manifest_sha256",
        "adjudication_status",
        "author_events",
        "display_order",
        "author_adjudications",
        "collateral_authorizations",
    }
    if not isinstance(payload, dict) or set(payload) != expected_top:
        fail(f"top-level fields must be exactly {sorted(expected_top)}")
    if payload["schema_version"] != "author-adjudication/1.0":
        fail("schema_version must be author-adjudication/1.0")
    if not isinstance(payload["revision_round"], int) or isinstance(payload["revision_round"], bool) or payload["revision_round"] < 1:
        fail("revision_round must be an integer >= 1")
    for field in ("roadmap_sha256", "base_draft_sha256", "claim_surface_manifest_sha256"):
        if not isinstance(payload[field], str) or not _SHA256_RE.match(payload[field]):
            fail(f"{field} must be 64-hex")
    if payload["roadmap_sha256"] != roadmap_sha256:
        raise ManifestError(
            "manifest_hash_mismatch",
            "author_adjudication.roadmap_sha256 does not match the exact roadmap bytes",
        )
    if (
        original_manuscript_sha256 is not None
        and payload["base_draft_sha256"] != original_manuscript_sha256
    ):
        raise ManifestError(
            "manifest_hash_mismatch",
            "author_adjudication.base_draft_sha256 does not match original_manuscript bytes",
        )
    if payload["adjudication_status"] != "complete":
        fail("adjudication_status must be complete")

    events = payload["author_events"]
    if not isinstance(events, list):
        fail("author_events must be an array")
    event_ids = set()
    for index, event in enumerate(events):
        if not isinstance(event, dict) or set(event) != {
            "event_id",
            "source",
            "actor_role",
            "input_sha256",
        }:
            fail(f"author_events[{index}] has an invalid closed shape")
        if not _AUTHOR_EVENT_RE.match(event["event_id"]):
            fail(f"author_events[{index}].event_id is invalid")
        if event["event_id"] in event_ids:
            fail(f"duplicate author event {event['event_id']!r}")
        event_ids.add(event["event_id"])
        if event["source"] != "explicit_session_user_message" or event["actor_role"] != "author":
            fail(f"author_events[{index}] is not an explicit author session event")
        if not isinstance(event["input_sha256"], str) or not _SHA256_RE.match(event["input_sha256"]):
            fail(f"author_events[{index}].input_sha256 must be 64-hex")

    roadmap_ids = [item["id"] for item in roadmap_items]
    display = payload["display_order"]
    if not isinstance(display, dict) or set(display) != {"mode", "item_ids", "author_event_id"}:
        fail("display_order has an invalid closed shape")
    if display["mode"] not in ("source_traceability", "user_selected"):
        fail("display_order.mode is invalid")
    if (
        not isinstance(display["item_ids"], list)
        or len(display["item_ids"]) != len(set(display["item_ids"]))
        or set(display["item_ids"]) != set(roadmap_ids)
    ):
        fail("display_order.item_ids must be a full unique roadmap permutation")
    if display["mode"] == "source_traceability" and display["item_ids"] != roadmap_ids:
        fail("source_traceability display order must equal immutable roadmap order")
    if display["author_event_id"] not in event_ids:
        fail("display_order.author_event_id does not resolve")

    records = payload["author_adjudications"]
    if not isinstance(records, list):
        fail("author_adjudications must be an array")
    by_item = {}
    for index, record in enumerate(records):
        required = {
            "item_id",
            "author_event_id",
            "author_triage",
            "authorized_targets",
            "claim_strength_authorizations",
        }
        allowed = required | {"author_reason"}
        if not isinstance(record, dict) or not required.issubset(record) or not set(record).issubset(allowed):
            fail(f"author_adjudications[{index}] has an invalid closed shape")
        item_id = record["item_id"]
        if item_id in by_item:
            fail(f"duplicate author adjudication for {item_id!r}")
        by_item[item_id] = record
        if record["author_event_id"] not in event_ids:
            fail(f"author adjudication {item_id}: author_event_id does not resolve")
        if record["author_triage"] not in ("will_address", "wont_address", "not_on_point"):
            fail(f"author adjudication {item_id}: invalid author_triage")
        try:
            validator = _V("manifest_incomplete", f"author adjudication {item_id}")
            _validate_author_targets(validator, record["authorized_targets"], "$.authorized_targets")
            _validate_claim_authorizations(
                validator,
                record["claim_strength_authorizations"],
                "$.claim_strength_authorizations",
            )
        except ArtifactSchemaError as exc:
            fail(str(exc))
        if record["author_triage"] == "will_address":
            if not record["authorized_targets"]:
                fail(f"author adjudication {item_id}: will_address requires exact targets")
            if "author_reason" in record:
                fail(f"author adjudication {item_id}: will_address must not invent author_reason")
        else:
            if not _is_str(record.get("author_reason")):
                fail(f"author adjudication {item_id}: declined choice requires author_reason")
            if record["authorized_targets"] or record["claim_strength_authorizations"]:
                fail(f"author adjudication {item_id}: declined choice carries no authority")
    if set(by_item) != set(roadmap_ids):
        fail("complete sidecar must carry exactly one author adjudication per roadmap item")

    collateral = payload["collateral_authorizations"]
    if not isinstance(collateral, list):
        fail("collateral_authorizations must be an array")
    for index, record in enumerate(collateral):
        required = {
            "authorization_id",
            "author_event_id",
            "authorizing_item_id",
            "constrained_item_id",
            "block_id",
            "operation",
            "reason",
        }
        if not isinstance(record, dict) or set(record) != required:
            fail(f"collateral_authorizations[{index}] has an invalid closed shape")
        if record["author_event_id"] not in event_ids:
            fail(f"collateral_authorizations[{index}].author_event_id does not resolve")
        if record["authorizing_item_id"] not in by_item or record["constrained_item_id"] not in by_item:
            fail(f"collateral_authorizations[{index}] item reference does not resolve")
        if by_item[record["authorizing_item_id"]]["author_triage"] != "will_address":
            fail(f"collateral_authorizations[{index}] authorizing item is not will_address")
        if by_item[record["constrained_item_id"]]["author_triage"] not in (
            "wont_address",
            "not_on_point",
        ):
            fail(f"collateral_authorizations[{index}] constrained item is not declined")
        if not _BLOCK_ID_RE.match(record["block_id"]):
            fail(f"collateral_authorizations[{index}].block_id is invalid")
        if record["operation"] not in ("replace_block", "insert_after", "delete_block"):
            fail(f"collateral_authorizations[{index}].operation is invalid")
        if not _is_str(record["reason"]):
            fail(f"collateral_authorizations[{index}].reason must be non-empty")
    return by_item


# --- synthesis recomputation ---------------------------------------------------


class Failures:
    def __init__(self):
        self.messages = []

    def add(self, message: str):
        self.messages.append(message)


def _decision_max(*decisions):
    return max(decisions, key=lambda d: DECISION_ORDER[d])


def derive_decision(p1_items, p2_partial_magnitudes, p2_made_worse, rate_num, rate_den, regression_severities, escalations):
    """§6 Steps 2-3. ``p1_items`` = [(final_verdict, driving_severity, residual_obligation_class)].

    Returns (decision, reject_recommended, base_rule).
    """
    p1_count = len(p1_items)
    rate_below_80 = rate_den > 0 and rate_num * 5 < rate_den * 4  # < 80%, integer-exact
    base = None
    rule = None
    if any(v == "MADE_WORSE" and sev == "critical" for v, sev, _m in p1_items) or ("critical" in regression_severities):
        base, rule = "Major Revision", "B1"
    elif p1_count > 0 and 2 * sum(1 for v, _s, _m in p1_items if v in ("NOT_ADDRESSED", "MADE_WORSE")) >= p1_count:
        base, rule = "Major Revision", "B2"
    elif any(v in ("NOT_ADDRESSED", "MADE_WORSE", "CANNOT_VERIFY") for v, _s, _m in p1_items) or ("major" in regression_severities):
        base, rule = "Major Revision", "B3"
    elif any(v == "PARTIALLY_ADDRESSED" and m == "must_fix" for v, _s, m in p1_items) or ("must_fix" in p2_partial_magnitudes):
        base, rule = "Major Revision", "B4"
    elif (
        any(v == "PARTIALLY_ADDRESSED" and m in ("should_fix", "consider") for v, _s, m in p1_items)
        or rate_below_80
        or p2_made_worse
        or ("minor" in regression_severities)
    ):
        base, rule = "Minor Revision", "B5"
    else:
        base, rule = "Accept", "B6"
    decision = base
    reject = rule in ("B1", "B2")
    for esc in escalations:
        if esc["effective_approval_state"] == "approved":
            decision = _decision_max(decision, esc["mechanical_decision_impact"])
            if esc["escalation_class"] == "research_integrity":
                reject = True
    return decision, reject, rule


def _adjustment_chains(traceability, fails: Failures):
    """Build per-item ordered adjustment chains (§5.3 grammar).

    Returns {item_id: [records head..tail]} (empty dict entries omitted);
    reports every grammar violation into ``fails``.
    """
    by_id = {}
    for rec in traceability["adjustments"]:
        if rec["adjustment_id"] in by_id:
            fails.add(f"adjustment ids must be unique: {rec['adjustment_id']}")
            return {}
        by_id[rec["adjustment_id"]] = rec
    chains = {}
    by_item = {}
    for rec in traceability["adjustments"]:
        by_item.setdefault(rec["item_id"], []).append(rec)
    for item_id, records in by_item.items():
        superseded = {}
        heads = []
        for rec in records:
            prev = rec.get("supersedes_adjustment_id")
            if prev is None:
                heads.append(rec)
            else:
                prev_rec = by_id.get(prev)
                if prev_rec is None or prev_rec["item_id"] != item_id:
                    fails.add(f"adjustment {rec['adjustment_id']}: supersedes_adjustment_id {prev!r} does not resolve on item {item_id}")
                    return {}
                if prev in superseded:
                    fails.add(f"adjustment chain on {item_id}: {prev} superseded twice")
                    return {}
                superseded[prev] = rec
        if len(heads) != 1:
            fails.add(f"adjustment chain on {item_id}: exactly one head required, found {len(heads)}")
            return {}
        chain = [heads[0]]
        while chain[-1]["adjustment_id"] in superseded:
            chain.append(superseded[chain[-1]["adjustment_id"]])
        if len(chain) != len(records):
            fails.add(f"adjustment chain on {item_id}: records outside the linear chain (cycle or fork)")
            return {}
        for prev_rec, next_rec in zip(chain, chain[1:]):
            if next_rec["from_verdict"] != prev_rec["to_verdict"]:
                fails.add(
                    f"adjustment chain on {item_id}: {next_rec['adjustment_id']}.from_verdict "
                    f"!= {prev_rec['adjustment_id']}.to_verdict (head-to-tail join)"
                )
        chains[item_id] = chain
    return chains


def check(
    manifest,
    precommitment,
    verdict_record,
    traceability,
    roadmap_items,
    author_by_item,
    letter_blocks,
    witness,
    witness_notes,
):
    """All §13 recomputation on schema-valid, hash-bound inputs.

    Returns (failures, warnings, recomputed_outcome) where
    recomputed_outcome is the Step 1-3 emission expectation.
    """
    fails = Failures()
    warnings = list(witness_notes)

    roadmap_by_id = {item["id"]: item for item in roadmap_items}
    must_fix_order = [item["id"] for item in roadmap_items if item["obligation_class"] == "must_fix"]
    p12_ids = {item["id"] for item in roadmap_items if item["obligation_class"] in ("must_fix", "should_fix")}
    cross_model_active = manifest["cross_model_active"]

    # round_id equality across all artifacts.
    for name, art in (("precommitment", precommitment), ("verdict_record", verdict_record), ("traceability", traceability)):
        if art["round_id"] != manifest["round_id"]:
            fails.add(f"{name}.round_id != manifest.round_id")
        if art["contract_version"] != manifest["contract_version"]:
            fails.add(f"{name}.contract_version != manifest.contract_version")

    # --- Phase 1 coverage + criterion binding (§4/§5.1) ---
    pre_by_item = {}
    for rec in precommitment["items"]:
        if rec["item_id"] in pre_by_item:
            fails.add(f"precommitment: duplicate record for {rec['item_id']}")
        pre_by_item[rec["item_id"]] = rec
    if set(pre_by_item) != p12_ids:
        fails.add(
            "precommitment coverage: records must exist for exactly the must_fix/should_fix roadmap items "
            f"(missing {sorted(p12_ids - set(pre_by_item))}, extra {sorted(set(pre_by_item) - p12_ids)})"
        )
    letter_present = manifest["artifacts"]["editorial_decision_letter"]["present"]
    letter_sound = letter_blocks is not None and letter_ordinals_sound(letter_blocks, len(must_fix_order))
    if letter_present and letter_blocks is not None and not letter_sound:
        warnings.append("[CRITERIA-LAYER-ABSENT: letter/roadmap ordinal mismatch]")
    if letter_present and letter_sound and not letter_blocks:
        warnings.append(
            "NOTE: editorial decision letter present but no Required Item Details blocks parsed — the level-2 "
            "criteria layer is empty (template drift or a genuinely block-less letter)"
        )
    block_by_rid = {}
    if letter_sound and letter_blocks:
        block_by_rid = {rid: text for rid, text in letter_blocks}
    for item_id, rec in pre_by_item.items():
        item = roadmap_by_id.get(item_id)
        if item is None:
            continue
        if rec["obligation_class"] != item["obligation_class"]:
            fails.add(f"precommitment {item_id}: obligation_class {rec['obligation_class']} != roadmap {item['obligation_class']}")
        if rec["inherited_criterion"]["roadmap_text"] != item["verification_criteria"]:
            fails.add(f"precommitment {item_id}: inherited_criterion.roadmap_text does not match the roadmap verbatim (§4)")
        if rec["source_reviewer"] != item["reviewer"]:
            fails.add(
                f"precommitment {item_id}: source_reviewer is a VERBATIM copy of the Schema 7 reviewer field "
                f"({rec['source_reviewer']!r} != {item['reviewer']!r}, §5.1)"
            )
        labels, _parse_failure = normalize_reviewer_labels(rec["source_reviewer"])
        if rec["source_reviewer_labels"] != labels:
            fails.add(
                f"precommitment {item_id}: source_reviewer_labels {rec['source_reviewer_labels']!r} "
                f"!= §10 normalization of source_reviewer ({labels!r})"
            )
        has_letter_fields = "letter_text" in rec["inherited_criterion"]
        if item["obligation_class"] == "must_fix":
            ordinal = must_fix_order.index(item_id) + 1
            derived_ref = f"R{ordinal}"
            block_text = block_by_rid.get(derived_ref) if letter_present and letter_sound else None
            if block_text is not None:
                if not has_letter_fields:
                    fails.add(f"precommitment {item_id}: letter carries block {derived_ref} — letter_text/letter_item_ref REQUIRED (§5.1)")
                else:
                    if rec["inherited_criterion"]["letter_item_ref"] != derived_ref:
                        fails.add(
                            f"precommitment {item_id}: letter_item_ref {rec['inherited_criterion']['letter_item_ref']!r} "
                            f"!= derived ordinal {derived_ref!r} (§5.1 — the ref is DERIVED, never chosen)"
                        )
                    if rec["inherited_criterion"]["letter_text"] != block_text:
                        fails.add(f"precommitment {item_id}: letter_text does not match the letter's Acceptance criteria byte-for-byte (§13)")
            elif has_letter_fields:
                fails.add(f"precommitment {item_id}: letter layer absent at this item — letter fields must be absent (§5.1/§13)")
        elif has_letter_fields:
            fails.add(f"precommitment {item_id}: letter fields on a non-must_fix item (§5.1)")

    # --- Phase 2A coverage + applied_criterion (§5.2) ---
    verdict_by_item = {}
    for rec in verdict_record["items"]:
        if rec["item_id"] in verdict_by_item:
            fails.add(f"verdict_record: duplicate record for {rec['item_id']}")
        verdict_by_item[rec["item_id"]] = rec
    if set(verdict_by_item) != set(roadmap_by_id):
        fails.add(
            "verdict_record coverage: exactly one record per roadmap item, ALL priorities "
            f"(missing {sorted(set(roadmap_by_id) - set(verdict_by_item))}, extra {sorted(set(verdict_by_item) - set(roadmap_by_id))})"
        )
    dissent_by_id = {}
    for rec in verdict_record["dissents"]:
        if rec["dissent_id"] in dissent_by_id:
            fails.add(f"verdict_record: duplicate dissent_id {rec['dissent_id']}")
        dissent_by_id[rec["dissent_id"]] = rec
        pre = pre_by_item.get(rec["item_id"])
        if pre is None:
            fails.add(f"dissent {rec['dissent_id']}: item {rec['item_id']} has no pre-commitment record")
        elif rec["criterion_hash"] != canonical_hash(pre):
            fails.add(f"dissent {rec['dissent_id']}: criterion_hash does not recompute from the Phase-1 record (§7)")
        # Reverse witness (§7): a dissent swaps the criterion BEFORE the
        # verdict — "The item's verdict record then carries
        # applied_criterion: dissented:<dissent_id>". A ghost dissent that
        # was never applied cannot exist, trip the §7 bound, or authorize
        # an original_upheld re-application of a criterion that was in
        # fact applied at 2A.
        applied = verdict_by_item.get(rec["item_id"], {}).get("applied_criterion")
        if applied != f"dissented:{rec['dissent_id']}":
            fails.add(
                f"dissent {rec['dissent_id']}: the item's verdict record must carry "
                f"applied_criterion dissented:{rec['dissent_id']} — a dissent that was never applied is a ghost (§7)"
            )
    # §7 bounds (SD-5): dissent on a must_fix item, or dissents on > ceil(N/3) of
    # all items, trips independent adjudication of EVERY dissent record.
    total_items = len(roadmap_items)
    bound_tripped = any(
        roadmap_by_id.get(dissent["item_id"], {}).get("obligation_class") == "must_fix"
        for dissent in dissent_by_id.values()
    ) or (len(dissent_by_id) > math.ceil(total_items / 3))
    for item_id, rec in verdict_by_item.items():
        item = roadmap_by_id.get(item_id)
        if item is None:
            continue
        applied = rec["applied_criterion"]
        if item["obligation_class"] == "consider":
            if applied != "not_precommitted":
                fails.add(f"verdict {item_id}: consider items carry applied_criterion not_precommitted (§5.2)")
        else:
            if applied == "not_precommitted":
                fails.add(f"verdict {item_id}: not_precommitted is valid ONLY for consider items (§5.2)")
            elif applied.startswith("dissented:"):
                dissent = dissent_by_id.get(applied.split(":", 1)[1])
                if dissent is None or dissent["item_id"] != item_id:
                    fails.add(f"verdict {item_id}: applied_criterion {applied!r} does not resolve to a dissent on this item")

    ns_by_id = {rec["new_standard_id"]: rec for rec in precommitment["new_standards"]}
    exceptions_by_id = {}
    for rec in verdict_record["escalation_exceptions"]:
        if rec["exception_id"] in exceptions_by_id:
            fails.add(f"verdict_record: duplicate exception_id {rec['exception_id']}")
        exceptions_by_id[rec["exception_id"]] = rec
        ref = rec.get("new_standard_ref")
        if ref is not None:
            target = ns_by_id.get(ref)
            if target is None:
                fails.add(f"escalation exception {rec['exception_id']}: new_standard_ref {ref!r} does not resolve")
            elif target["classification"] != "escalation_requested":
                fails.add(f"escalation exception {rec['exception_id']}: new_standard_ref target is not escalation_requested (§5.1)")

    # --- new-issue freeze witness (§13.5) ---
    if traceability["new_issues"] != verdict_record["new_issues"]:
        fails.add("new_issues: §5.3 set is not WHOLE-RECORD byte-identical to the frozen §5.2 set (§3.3 freeze witness)")
    new_issue_by_id = {}
    for rec in verdict_record["new_issues"]:
        if rec["new_issue_id"] in new_issue_by_id:
            fails.add(f"verdict_record: duplicate new_issue_id {rec['new_issue_id']}")
        new_issue_by_id[rec["new_issue_id"]] = rec
        nearest = rec["nearest_roadmap_item"]
        if nearest is not None and nearest not in roadmap_by_id:
            fails.add(f"new issue {rec['new_issue_id']}: nearest_roadmap_item {nearest!r} does not resolve")
        if rec["attribution"] == "regression" and nearest is not None:
            warnings.append(
                f"ADVISORY: regression {rec['new_issue_id']} names nearest_roadmap_item {nearest} — "
                "review for roadmap-item overlap (§8)"
            )
    # --- rows (§5.3) ---
    row_by_item = {}
    for row in traceability["rows"]:
        if row["item_id"] in row_by_item:
            fails.add(f"traceability: duplicate row for {row['item_id']}")
        row_by_item[row["item_id"]] = row
    if set(row_by_item) != set(roadmap_by_id):
        fails.add(
            "row coverage: EVERY roadmap item, all priorities, has exactly one row "
            f"(missing {sorted(set(roadmap_by_id) - set(row_by_item))}, extra {sorted(set(row_by_item) - set(roadmap_by_id))})"
        )
    for item_id, row in row_by_item.items():
        item = roadmap_by_id.get(item_id)
        if item is None:
            continue
        if ROW_OBLIGATION_MAP[row["obligation_class"]] != item["obligation_class"]:
            fails.add(f"row {item_id}: obligation_class {row['obligation_class']} does not match the roadmap ({item['obligation_class']})")
        author = author_by_item.get(item_id)
        if author is None:
            fails.add(f"row {item_id}: no hash-bound author adjudication exists")
        else:
            for field in (
                "author_triage",
                "authorized_targets",
                "claim_strength_authorizations",
            ):
                if row[field] != author[field]:
                    fails.add(
                        f"row {item_id}: {field} is not an exact copy of the hash-bound author adjudication"
                    )
            row_has_reason = "author_reason" in row
            author_has_reason = "author_reason" in author
            if row_has_reason != author_has_reason or (
                row_has_reason and row["author_reason"] != author["author_reason"]
            ):
                fails.add(
                    f"row {item_id}: author_reason presence/value is not an exact author-adjudication copy"
                )
        vrec = verdict_by_item.get(item_id)
        if vrec is not None:
            if row["phase2a_verdict"] != vrec["verdict"]:
                fails.add(f"row {item_id}: phase2a_verdict != committed §5.2 verdict")
            if row["verified_by"] != vrec["verified_by"]:
                fails.add(f"row {item_id}: verified_by not copied from the §5.2 verdict record")
        if row["status"] != row["final_verdict"]:
            fails.add(f"row {item_id}: status must map 1:1 from final_verdict (§5.3)")
        if row["verified"] != VERIFIED_MAP[row["final_verdict"]]:
            fails.add(f"row {item_id}: verified must follow the mechanical 5->4 map (§5.3)")
        if "cross_model_verdict" in row:
            derived = "agree" if row["cross_model_verdict"] == row["final_verdict"] else "diverges"
            if row["cross_model_status"] != derived:
                fails.add(f"row {item_id}: cross_model_status {row['cross_model_status']!r} != per-emission derivation {derived!r} (§5.3)")

    # --- adjustment chains (§5.3) ---
    chains = _adjustment_chains(traceability, fails)
    for item_id, row in row_by_item.items():
        chain = chains.get(item_id)
        if chain:
            if row.get("adjustment_id") != chain[-1]["adjustment_id"]:
                fails.add(f"row {item_id}: adjustment_id must name the chain's LATEST record")
            if chain[0]["from_verdict"] != row["phase2a_verdict"]:
                fails.add(f"adjustment chain on {item_id}: head from_verdict != phase2a_verdict")
            if chain[-1]["to_verdict"] != row["final_verdict"]:
                fails.add(f"adjustment chain on {item_id}: tail to_verdict != final_verdict")
        else:
            if "adjustment_id" in row:
                fails.add(f"row {item_id}: adjustment_id present with no adjustment chain")
        tail_rebuttal = bool(chain) and chain[-1]["basis"] == "valid_rebuttal" and chain[-1]["to_verdict"] == "FULLY_ADDRESSED"
        if bool(row.get("addressed_by_rebuttal")) != tail_rebuttal:
            fails.add(f"row {item_id}: addressed_by_rebuttal marker must reflect a valid_rebuttal chain-tail upgrade to FULLY_ADDRESSED (§3.4)")
    for item_id in chains:
        if item_id not in row_by_item:
            fails.add(f"adjustment chain on {item_id}: no matrix row exists")

    # --- deferral-loop referential integrity (§5.3/§6) ---
    intents_by_id = {}
    for rec in traceability["resolution_intents"]:
        if rec["intent_id"] in intents_by_id:
            fails.add(f"duplicate intent_id {rec['intent_id']}")
        intents_by_id[rec["intent_id"]] = rec
        if rec["answered_by"] == "system":
            # §5.3: system intents are emitted for every must_fix diverges row —
            # the row must be an evaluated must_fix row (cross_model_verdict
            # present implies an active configuration).
            intent_row = row_by_item.get(rec["item_id"])
            if intent_row is None or intent_row["obligation_class"] != "MUST_FIX" or "cross_model_verdict" not in intent_row:
                fails.add(
                    f"resolution intent {rec['intent_id']}: system intents exist only for evaluated must_fix diverges "
                    "rows under ACTIVE cross-model (§5.3)"
                )
    adjudications_by_dissent = {}
    for rec in traceability["dissent_adjudications"]:
        if rec["dissent_id"] in adjudications_by_dissent:
            fails.add(f"duplicate dissent adjudication for {rec['dissent_id']}")
        adjudications_by_dissent[rec["dissent_id"]] = rec
        if rec["dissent_id"] not in dissent_by_id:
            fails.add(f"dissent adjudication {rec['dissent_id']}: no such dissent record")
        if rec["adjudicator"] == "cross_model" and not cross_model_active:
            fails.add(f"dissent adjudication {rec['dissent_id']}: cross_model adjudicator on an inactive configuration (§11)")
        if not bound_tripped:
            fails.add(
                f"dissent adjudication {rec['dissent_id']}: no §7 bound tripped — dissents below the bound stand "
                "unadjudicated by design (§7)"
            )
        dissent = dissent_by_id.get(rec["dissent_id"])
        dissent_item = roadmap_by_id.get(dissent["item_id"]) if dissent else None
        if rec["adjudicator"] == "cross_model":
            if dissent_item is None or dissent_item["obligation_class"] != "must_fix":
                fails.add(
                    f"dissent adjudication {rec['dissent_id']}: the judge's adjudication scope EQUALS the §9 pass's "
                    "must_fix coverage — dissents on non-must_fix items always take the G2(a) user path, even on an active "
                    "setup (§7)"
                )
        # A `user` adjudication on an active-setup must_fix dissent stays legal:
        # the §6 deferral loop records "a user-adjudicated DissentAdjudication
        # ... DIRECTLY" without an activity qualifier, and the §9 pass can be
        # per-row unavailable — rejecting the user path would make a
        # judge-transport failure unrecoverable (adjudicated against the
        # stricter one-way reading; see PR #605 round-4/5 record).
    reapp_by_id = {}
    for rec in traceability["reapplications"]:
        if rec["reapplication_id"] in reapp_by_id:
            fails.add(f"duplicate reapplication_id {rec['reapplication_id']}")
        reapp_by_id[rec["reapplication_id"]] = rec
    superseded_reapps = {}
    for rec in traceability["reapplications"]:
        prev = rec.get("supersedes_reapplication_id")
        if prev is not None:
            prev_rec = reapp_by_id.get(prev)
            if prev_rec is None or prev_rec["item_id"] != rec["item_id"]:
                fails.add(f"reapplication {rec['reapplication_id']}: supersedes_reapplication_id {prev!r} does not resolve on the same item")
            elif prev in superseded_reapps:
                fails.add(f"reapplication supersession: {prev} superseded twice")
            else:
                superseded_reapps[prev] = rec["reapplication_id"]
    # acyclicity of supersession
    for rec in traceability["reapplications"]:
        seen_ids = set()
        cursor = rec
        while cursor is not None:
            if cursor["reapplication_id"] in seen_ids:
                fails.add(f"reapplication supersession cycle at {cursor['reapplication_id']}")
                break
            seen_ids.add(cursor["reapplication_id"])
            prev = cursor.get("supersedes_reapplication_id")
            cursor = reapp_by_id.get(prev) if prev is not None else None
    current_reapps = [rec for rec in traceability["reapplications"] if rec["reapplication_id"] not in superseded_reapps]

    def _chain_tail_verdict(item_id):
        chain = chains.get(item_id)
        if chain:
            return chain[-1]["to_verdict"]
        row = row_by_item.get(item_id)
        return row["phase2a_verdict"] if row else None

    for rec in traceability["reapplications"]:
        item_id = rec["item_id"]
        has_adjudication_ref = False
        has_intent_ref = False
        for ref in rec["answer_refs"]:
            kind, ref_id = ref.split(":", 1)
            if kind == "intent":
                has_intent_ref = True
            if kind == "adjudication":
                has_adjudication_ref = True
                adjudication = adjudications_by_dissent.get(ref_id)
                dissent = dissent_by_id.get(ref_id)
                if adjudication is None or dissent is None:
                    fails.add(f"reapplication {rec['reapplication_id']}: answer ref {ref!r} does not resolve")
                    continue
                if adjudication["outcome"] != "original_upheld":
                    fails.add(f"reapplication {rec['reapplication_id']}: adjudication ref {ref!r} must resolve to original_upheld (§6)")
                if dissent["item_id"] != item_id:
                    fails.add(f"reapplication {rec['reapplication_id']}: adjudication ref {ref!r} is on a different item")
            else:
                intent = intents_by_id.get(ref_id)
                if intent is None:
                    fails.add(f"reapplication {rec['reapplication_id']}: answer ref {ref!r} does not resolve")
                elif intent["item_id"] != item_id:
                    fails.add(f"reapplication {rec['reapplication_id']}: intent ref {ref!r} is on a different item")
        # effective-criterion rule (§6)
        replacement_dissents = [
            dissent_id for dissent_id, adjudication in adjudications_by_dissent.items()
            if adjudication["outcome"] == "replacement_approved"
            and dissent_by_id.get(dissent_id, {}).get("item_id") == item_id
        ]
        if has_adjudication_ref:
            expected_ref = f"phase1:{item_id}"
        elif replacement_dissents:
            expected_ref = f"dissent:{replacement_dissents[0]}"
        else:
            expected_ref = f"phase1:{item_id}"
        if rec["criterion_ref"] != expected_ref:
            fails.add(
                f"reapplication {rec['reapplication_id']}: criterion_ref {rec['criterion_ref']!r} "
                f"violates the §6 effective-criterion rule (expected {expected_ref!r})"
            )
        # derived adjustment (§6 loop step 2)
        derived = [
            adj for adj in traceability["adjustments"]
            if adj.get("source_ref") == f"reapplication:{rec['reapplication_id']}"
        ]
        # §6 trigger binding: a reapplication whose answer_refs carry ONLY
        # intent refs is a DIVERGENCE re-verification — it exists only for
        # an evaluated must_fix row (one carrying cross_model_verdict, which
        # itself implies an active configuration): "diverges rows exist
        # only under ACTIVE cross-model (a not_configured run has none)".
        # A G2(d) retry is unaffected — its refs are CUMULATIVE and always
        # include the mandating adjudication.
        if has_intent_ref and not has_adjudication_ref:
            row = row_by_item.get(item_id)
            if row is None or row["obligation_class"] != "MUST_FIX" or "cross_model_verdict" not in row:
                fails.add(
                    f"reapplication {rec['reapplication_id']}: a divergence-only re-application exists only for an "
                    "evaluated must_fix row under active cross-model (§6/§5.3) — no committed verdict moves without its "
                    "triggering divergence"
                )
            elif row["cross_model_verdict"] == rec["pre_reapplication_verdict"]:
                # §6 dispatch order is normative: diverges is identified
                # FIRST (judge verdict vs the row's verdict), THEN the
                # system intent is emitted and the 2B' call dispatched. A
                # judge verdict equal to the dispatch-time pre-value means
                # no divergence existed to resolve — the chain manufactures
                # its own diverges status after the fact.
                fails.add(
                    f"reapplication {rec['reapplication_id']}: no divergence existed at dispatch — the judge's "
                    "verdict equals the dispatch-time pre_reapplication_verdict (§6)"
                )
            if not any(
                intents_by_id.get(ref.split(":", 1)[1], {}).get("answered_by") == "system"
                for ref in rec["answer_refs"]
                if ref.startswith("intent:")
            ):
                fails.add(
                    f"reapplication {rec['reapplication_id']}: a divergence re-application chain carries the "
                    "ORIGINAL mandating system intent (§6 — divergence resolution is MECHANICAL by default; user "
                    "intents exist only on the retry paths, cumulatively alongside it)"
                )
        # §5.3 letter-tag condition: a letter-tagged anchor on a
        # reapplication (and hence on its mechanically-copied
        # cross_model_adjudication adjustment) is valid EXACTLY when the
        # re-examined chain projection carried a booked valid_rebuttal
        # record — the §3.4 machine witness that an assertion in the letter
        # with no locatable manuscript evidence changes nothing. The 2B'
        # input set withholds the Response Letter itself, so a booked
        # rebuttal anchor is the only legal letter-side source.
        if rec["reapplied_verdict"] != "CANNOT_VERIFY" and any(
            anchor["anchor_artifact"] == "letter" for anchor in rec["evidence_anchor"]
        ):
            letter_tag_allowed = False
            for chain_adj in chains.get(item_id, []):
                if len(derived) == 1 and chain_adj["adjustment_id"] == derived[0]["adjustment_id"]:
                    break
                if chain_adj["basis"] == "valid_rebuttal":
                    letter_tag_allowed = True
                    break
            if not letter_tag_allowed:
                fails.add(
                    f"reapplication {rec['reapplication_id']}: letter-tagged anchors are valid exactly when the "
                    "re-examined chain carries a booked valid_rebuttal record (§5.3/§3.4)"
                )
        changing = rec["reapplied_verdict"] != "CANNOT_VERIFY" and rec["reapplied_verdict"] != rec["pre_reapplication_verdict"]
        if rec["reapplied_verdict"] == "CANNOT_VERIFY":
            if derived:
                fails.add(f"reapplication {rec['reapplication_id']}: CANNOT_VERIFY appends NOTHING mechanically (§6)")
        elif changing:
            if len(derived) != 1:
                fails.add(f"reapplication {rec['reapplication_id']}: a verdict-changing reapplication requires exactly one derived adjustment (§13)")
            else:
                adj = derived[0]
                if adj["item_id"] != item_id or adj["basis"] != "cross_model_adjudication":
                    fails.add(f"reapplication {rec['reapplication_id']}: derived adjustment must be a cross_model_adjudication on the same item")
                if adj["from_verdict"] != rec["pre_reapplication_verdict"] or adj["to_verdict"] != rec["reapplied_verdict"]:
                    fails.add(f"reapplication {rec['reapplication_id']}: derived adjustment endpoints must bind to the RECORDED pre-value (§6)")
                if adj["rationale"] != rec["rationale"]:
                    fails.add(f"reapplication {rec['reapplication_id']}: derived adjustment rationale must be MECHANICALLY COPIED (§6)")
                if adj.get("residual_gap") != rec.get("residual_gap"):
                    fails.add(f"reapplication {rec['reapplication_id']}: derived adjustment residual_gap must be MECHANICALLY COPIED (§6)")
                if adj.get("evidence_anchor") != rec.get("evidence_anchor"):
                    fails.add(f"reapplication {rec['reapplication_id']}: derived adjustment anchors must be MECHANICALLY COPIED, tags included (§5.3)")
        else:
            if derived:
                fails.add(f"reapplication {rec['reapplication_id']}: no verdict change, so no derived adjustment may exist (§6)")

    # every original_upheld adjudication + every intent appears in exactly one CURRENT record's answer_refs
    def _answers_in_current(ref: str):
        return [rec for rec in current_reapps if ref in rec["answer_refs"]]

    for dissent_id, adjudication in adjudications_by_dissent.items():
        if adjudication["outcome"] == "original_upheld":
            holders = _answers_in_current(f"adjudication:{dissent_id}")
            if len(holders) != 1:
                fails.add(
                    f"dissent adjudication {dissent_id}: original_upheld must appear in exactly one CURRENT reapplication's "
                    f"answer_refs (found {len(holders)}) — silent non-reapplication cannot pass (§6)"
                )
    for intent_id in intents_by_id:
        holders = _answers_in_current(f"intent:{intent_id}")
        if len(holders) != 1:
            fails.add(
                f"resolution intent {intent_id}: must appear in exactly one CURRENT reapplication's answer_refs "
                f"(found {len(holders)}) (§6)"
            )

    # --- cross-model resolutions (§5.3/§9) ---
    resolutions_by_reapp = {}
    for rec in traceability["cross_model_resolutions"]:
        if rec["reapplication_id"] in resolutions_by_reapp:
            fails.add(f"reapplication {rec['reapplication_id']}: referenced by more than one CrossModelResolution")
        resolutions_by_reapp[rec["reapplication_id"]] = rec
    # §6 loop step 2: when an intent-mandated re-application derives a state
    # (reapplied_verdict != CANNOT_VERIFY) the resolution is created
    # MECHANICALLY — its absence means the pipeline skipped a mechanical step.
    for rec in current_reapps:
        has_intent_ref = any(ref.startswith("intent:") for ref in rec["answer_refs"])
        if has_intent_ref and rec["reapplied_verdict"] != "CANNOT_VERIFY":
            resolution = resolutions_by_reapp.get(rec["reapplication_id"])
            if resolution is None or resolution["resolved_by"] != "system":
                fails.add(
                    f"reapplication {rec['reapplication_id']}: a derived state mandates a mechanically-created "
                    "system CrossModelResolution (§6 loop step 2)"
                )
    for rec in traceability["cross_model_resolutions"]:
        intent = intents_by_id.get(rec["intent_id"])
        reapp = reapp_by_id.get(rec["reapplication_id"])
        if intent is None or intent["item_id"] != rec["item_id"]:
            fails.add(f"resolution {rec['resolution_id']}: intent_id does not resolve on the same item")
        if reapp is None or reapp["item_id"] != rec["item_id"]:
            fails.add(f"resolution {rec['resolution_id']}: reapplication_id does not resolve on the same item")
            continue
        if f"intent:{rec['intent_id']}" not in reapp["answer_refs"]:
            fails.add(
                f"resolution {rec['resolution_id']}: reapplication {rec['reapplication_id']} did not answer "
                f"intent {rec['intent_id']} — the resolution derives FROM the mandated re-application, never from "
                "an unrelated same-item record (§6 loop step 2)"
            )
        if rec["resolved_by"] == "system":
            if reapp["reapplied_verdict"] == "CANNOT_VERIFY":
                fails.add(f"resolution {rec['resolution_id']}: a CANNOT_VERIFY reapplication derives no system resolution (§5.3)")
            else:
                expected_state = "primary_upheld" if reapp["reapplied_verdict"] == reapp["pre_reapplication_verdict"] else "primary_revised"
                if rec["state"] != expected_state:
                    fails.add(f"resolution {rec['resolution_id']}: state {rec['state']!r} != §9 derivation ({expected_state!r})")
        else:
            if reapp["reapplied_verdict"] != "CANNOT_VERIFY":
                fails.add(f"resolution {rec['resolution_id']}: the user acceptance form requires a CANNOT_VERIFY reapplication (§5.3)")

    # --- G2(d) acceptances ---
    acceptances_by_id = {}
    for rec in traceability["g2d_acceptances"]:
        if rec["acceptance_id"] in acceptances_by_id:
            fails.add(f"duplicate acceptance_id {rec['acceptance_id']}")
        acceptances_by_id[rec["acceptance_id"]] = rec
        reapp = reapp_by_id.get(rec["reapplication_id"])
        if reapp is None or reapp["item_id"] != rec["item_id"]:
            fails.add(f"acceptance {rec['acceptance_id']}: reapplication_id does not resolve on the same item")
        elif reapp["reapplied_verdict"] != "CANNOT_VERIFY":
            fails.add(f"acceptance {rec['acceptance_id']}: the accepted reapplication must be CANNOT_VERIFY (§6 G2(d))")
        if rec["reapplication_id"] in superseded_reapps:
            fails.add(
                f"acceptance {rec['acceptance_id']}: references a SUPERSEDED reapplication — an acceptance binds "
                "to the CURRENT failed attempt, never a stale one (§6 G2(d))"
            )
        row = row_by_item.get(rec["item_id"])
        if row is not None and row["final_verdict"] != "CANNOT_VERIFY":
            fails.add(f"acceptance {rec['acceptance_id']}: the accepted item's final_verdict must be CANNOT_VERIFY (§6 G2(d))")
        backing = [
            adj for adj in traceability["adjustments"]
            if adj["basis"] == "user_accepted_fail_closed"
            and adj.get("source_ref") == f"acceptance:{rec['acceptance_id']}"
        ]
        if len(backing) != 1:
            fails.add(
                f"acceptance {rec['acceptance_id']}: a G2(d) acceptance backs exactly ONE user_accepted_fail_closed "
                f"adjustment (found {len(backing)}) — the one legal CANNOT_VERIFY append; an orphan acceptance cannot "
                "clear the deferral (§6 G2(d)/§3.4)"
            )
    acceptance_adj_by_reapp = {}
    for adj in traceability["adjustments"]:
        if adj["basis"] == "user_accepted_fail_closed":
            acc_id = adj["source_ref"].split(":", 1)[1]
            acceptance = acceptances_by_id.get(acc_id)
            if acceptance is None or acceptance["item_id"] != adj["item_id"]:
                fails.add(f"adjustment {adj['adjustment_id']}: acceptance ref does not resolve on the same item")
                continue
            acceptance_adj_by_reapp[acceptance["reapplication_id"]] = adj
            reapp = reapp_by_id.get(acceptance["reapplication_id"])
            if reapp is not None and reapp.get("cannot_verify_reason") != adj.get("cannot_verify_reason"):
                fails.add(f"adjustment {adj['adjustment_id']}: cannot_verify_reason must be copied from the accepted reapplication (§3.4)")
        elif adj["basis"] == "cross_model_adjudication":
            rap_id = adj["source_ref"].split(":", 1)[1]
            if rap_id not in reapp_by_id:
                fails.add(f"adjustment {adj['adjustment_id']}: reapplication ref does not resolve")

    # pre_reapplication_verdict consistency (§13): the recorded pre-value is
    # the TIME ANCHOR — it equals this reapplication's own derived
    # adjustment's from_verdict when one exists; on the G2(d) path it equals
    # the acceptance-backed adjustment's from_verdict (that adjustment
    # consumed this reapplication, so the tail moved AFTER dispatch); else
    # the current chain tail; else phase2a_verdict when the item has no chain.
    for rec in traceability["reapplications"]:
        derived = [
            adj for adj in traceability["adjustments"]
            if adj.get("source_ref") == f"reapplication:{rec['reapplication_id']}"
        ]
        if rec["reapplication_id"] in superseded_reapps:
            # UNCONDITIONAL for every superseded record — a derived
            # adjustment must not bypass this branch. Supersession is
            # defined for FAILED attempts only (§6 — "a retry names the
            # failed attempt it supersedes"), and a failed attempt appends
            # nothing, so its dispatch tail equals its direct retry's
            # recorded pre-value. The current-tail fallback never applies
            # to a historical record (the tail may have moved since).
            successor = reapp_by_id[superseded_reapps[rec["reapplication_id"]]]
            if rec["reapplied_verdict"] != "CANNOT_VERIFY":
                fails.add(
                    f"reapplication {rec['reapplication_id']}: only FAILED (CANNOT_VERIFY) attempts are superseded "
                    "by a retry (§6)"
                )
            if rec["pre_reapplication_verdict"] != successor["pre_reapplication_verdict"]:
                fails.add(
                    f"reapplication {rec['reapplication_id']}: a failed attempt appends nothing, so its dispatch "
                    f"tail equals its direct retry's pre_reapplication_verdict "
                    f"({rec['pre_reapplication_verdict']!r} != {successor['pre_reapplication_verdict']!r}, §6/§13)"
                )
            continue
        if len(derived) == 1:
            expected_pre = derived[0]["from_verdict"]
        elif rec["reapplication_id"] in acceptance_adj_by_reapp:
            expected_pre = acceptance_adj_by_reapp[rec["reapplication_id"]]["from_verdict"]
        else:
            expected_pre = _chain_tail_verdict(rec["item_id"])
        if expected_pre is not None and rec["pre_reapplication_verdict"] != expected_pre:
            fails.add(
                f"reapplication {rec['reapplication_id']}: pre_reapplication_verdict {rec['pre_reapplication_verdict']!r} "
                f"!= the chain tail as it stood at dispatch ({expected_pre!r}, §13)"
            )

    # --- critical-rebuttal machinery (§3.4/§5.3) ---
    radj_by_id = {}
    for rec in traceability["rebuttal_adjudications"]:
        if rec["rebuttal_adjudication_id"] in radj_by_id:
            fails.add(f"duplicate rebuttal_adjudication_id {rec['rebuttal_adjudication_id']}")
        radj_by_id[rec["rebuttal_adjudication_id"]] = rec
        if not cross_model_active:
            fails.add(f"rebuttal adjudication {rec['rebuttal_adjudication_id']}: the §3.4 pass exists only under active cross-model (§11)")
    adjustments_by_id = {adj["adjustment_id"]: adj for adj in traceability["adjustments"]}

    def _is_critical(item_id):
        item = roadmap_by_id.get(item_id)
        return item is not None and item.get("severity") == "critical"

    for adj in traceability["adjustments"]:
        should_have_check = adj["basis"] == "valid_rebuttal" and _is_critical(adj["item_id"])
        has_check = "critical_rebuttal_check" in adj
        if should_have_check != has_check:
            fails.add(
                f"adjustment {adj['adjustment_id']}: critical_rebuttal_check present iff the adjustment is a critical "
                f"valid_rebuttal (§3.4)"
            )
        if has_check:
            check_value = adj["critical_rebuttal_check"]
            match = _CHECK_ADJUDICATED_RE.match(check_value) if isinstance(check_value, str) else None
            if match:
                radj = radj_by_id.get(match.group(1))
                if radj is None or radj["verdict"] != "upheld" or radj["item_id"] != adj["item_id"]:
                    fails.add(f"adjustment {adj['adjustment_id']}: adjudicated:* must resolve to an upheld RebuttalAdjudication on the same item (§3.4)")
            elif check_value == "single_family_disclosed" and cross_model_active:
                fails.add(f"adjustment {adj['adjustment_id']}: single_family_disclosed is invalid on an active cross-model run (§3.4)")

    proposals_by_id = {}
    booked_by_adjustment = {}
    seen_drafted_bodies = {}
    challenged_bodies = []
    for rec in traceability["pending_rebuttal_upgrades"]:
        if rec["proposal_id"] in proposals_by_id:
            fails.add(f"duplicate proposal_id {rec['proposal_id']}")
        proposals_by_id[rec["proposal_id"]] = rec
        kind, ref_id = rec["disposition"].split(":", 1)
        if rec["drafted_adjustment"]["item_id"] != rec["item_id"]:
            fails.add(f"proposal {rec['proposal_id']}: drafted_adjustment.item_id must equal the proposal's item_id (§5.3)")
        body_key = (rec["item_id"], canonical_hash(rec["drafted_adjustment"]))
        if body_key in seen_drafted_bodies:
            fails.add(
                f"proposal {rec['proposal_id']}: duplicate PendingRebuttalUpgrade drafted body on item {rec['item_id']} "
                f"(same canonical body as {seen_drafted_bodies[body_key]}) — one proposal per drafted upgrade (§5.3)"
            )
        seen_drafted_bodies[body_key] = rec["proposal_id"]
        if kind == "challenged":
            challenged_bodies.append((rec["proposal_id"], rec["item_id"], rec["drafted_adjustment"]))
        if kind == "challenged":
            radj = radj_by_id.get(ref_id)
            if radj is None or radj["item_id"] != rec["item_id"]:
                fails.add(f"proposal {rec['proposal_id']}: challenged ref does not resolve on the same item")
            elif radj["verdict"] != "challenged":
                fails.add(f"proposal {rec['proposal_id']}: challenged disposition must reference a challenged adjudication")
        else:
            adj = adjustments_by_id.get(ref_id)
            if adj is None or adj["item_id"] != rec["item_id"] or adj["basis"] != "valid_rebuttal":
                fails.add(f"proposal {rec['proposal_id']}: booked ref must resolve to a valid_rebuttal adjustment on the same item")
                continue
            if ref_id in booked_by_adjustment:
                fails.add(f"proposal {rec['proposal_id']}: adjustment {ref_id} already booked by {booked_by_adjustment[ref_id]}")
            booked_by_adjustment[ref_id] = rec["proposal_id"]
            drafted = dict(rec["drafted_adjustment"])
            booked = {
                key: value for key, value in adj.items()
                if key not in ("adjustment_id", "supersedes_adjustment_id", "critical_rebuttal_check")
            }
            if drafted != booked:
                fails.add(
                    f"proposal {rec['proposal_id']}: booked adjustment must content-equal the drafted body "
                    "field-for-field, excluding EXACTLY {adjustment_id, supersedes_adjustment_id, critical_rebuttal_check} (§5.3)"
                )
            check_value = adj.get("critical_rebuttal_check")
            if kind == "booked":
                match = _CHECK_ADJUDICATED_RE.match(check_value) if isinstance(check_value, str) else None
                if not match or radj_by_id.get(match.group(1), {}).get("verdict") != "upheld":
                    fails.add(f"proposal {rec['proposal_id']}: booked disposition requires an upheld adjudicated:* check (§3.4)")
            elif kind == "booked_disclosed":
                if check_value != "pass_unavailable_disclosed":
                    fails.add(f"proposal {rec['proposal_id']}: booked_disclosed requires critical_rebuttal_check pass_unavailable_disclosed")
                if not cross_model_active:
                    fails.add(f"proposal {rec['proposal_id']}: booked_disclosed exists only under active cross-model (§11)")
            elif kind == "booked_single_family":
                if check_value != "single_family_disclosed":
                    fails.add(f"proposal {rec['proposal_id']}: booked_single_family requires critical_rebuttal_check single_family_disclosed")
                if cross_model_active:
                    fails.add(f"proposal {rec['proposal_id']}: booked_single_family is invalid under active cross-model (§3.4)")
    for adj in traceability["adjustments"]:
        if adj["basis"] == "valid_rebuttal" and _is_critical(adj["item_id"]) and adj["adjustment_id"] not in booked_by_adjustment:
            fails.add(
                f"adjustment {adj['adjustment_id']}: every critical valid_rebuttal adjustment traces to exactly one "
                "booked* PendingRebuttalUpgrade (§5.3)"
            )
        if adj["basis"] == "valid_rebuttal":
            booked_view = {
                key: value for key, value in adj.items()
                if key not in ("adjustment_id", "supersedes_adjustment_id", "critical_rebuttal_check")
            }
            for proposal_id, item_id, drafted in challenged_bodies:
                if adj["item_id"] == item_id and booked_view == drafted:
                    fails.add(
                        f"adjustment {adj['adjustment_id']}: content-equals CHALLENGED proposal {proposal_id}'s "
                        "drafted body — a challenged upgrade is NEVER booked (§3.4)"
                    )

    # --- escalation approvals ---
    approvals_by_exception = {}
    for rec in traceability["escalation_approvals"]:
        if rec["exception_id"] in approvals_by_exception:
            fails.add(f"duplicate escalation approval for {rec['exception_id']}")
        approvals_by_exception[rec["exception_id"]] = rec
        if rec["exception_id"] not in exceptions_by_id:
            fails.add(f"escalation approval {rec['exception_id']}: no such exception record")

    # --- cross-model activity consistency (§11) ---
    if not cross_model_active:
        for item_id, row in row_by_item.items():
            if row.get("cross_model_status") in ("agree", "diverges", "unavailable"):
                fails.add(f"row {item_id}: cross_model_status {row['cross_model_status']!r} implies an active configuration (§11)")

    # --- DecisionInputs recomputation (§13) ---
    di = traceability["decision_inputs"]

    def _final_residual_obligation_class(item_id):
        row = row_by_item.get(item_id)
        if row is None or row["final_verdict"] != "PARTIALLY_ADDRESSED":
            return None
        chain = chains.get(item_id)
        record = chain[-1] if chain else verdict_by_item.get(item_id)
        if record is None:
            return None
        gap = record.get("residual_gap")
        return gap["residual_obligation_class"] if gap else None

    expected_per_item = []
    for item_id in must_fix_order:
        row = row_by_item.get(item_id)
        if row is None:
            continue
        item = roadmap_by_id[item_id]
        severity = item.get("severity")
        # §5.3: a null driving_severity is legal ONLY for source_kind items
        # and legacy roadmaps. A must_fix item carrying other transported markers
        # (#574 A2/A3) but no severity is a half-transported finding-driven
        # item, not a legacy one — B1's critical join would be silently
        # suppressed, so it fails here.
        if (
            severity is None
            and item.get("source_kind") is None
            and any(item.get(field) is not None for field in ("evidence_anchor", "confidence", "competence_basis"))
        ):
            fails.add(
                f"roadmap item {item_id}: transported fields present but severity absent — a non-legacy "
                "finding-driven must_fix item cannot carry driving_severity null (§5.3)"
            )
        entry = {
            "item_id": item_id,
            "final_verdict": row["final_verdict"],
            "driving_severity": severity if severity in SEVERITIES else None,
        }
        magnitude = _final_residual_obligation_class(item_id)
        if magnitude is not None:
            entry["residual_obligation_class"] = magnitude
        expected_per_item.append(entry)
    if di["per_item"] != expected_per_item:
        fails.add("decision_inputs.per_item does not equal the recomputed per-must_fix operand list (immutable roadmap order, §13)")

    expected_counts = {prio: {verdict: 0 for verdict in VERDICTS} for prio in OBLIGATION_CLASSES}
    expected_magnitudes = {prio: {mag: 0 for mag in RESIDUAL_OBLIGATION_CLASSES} for prio in OBLIGATION_CLASSES}
    for item_id, row in row_by_item.items():
        item = roadmap_by_id.get(item_id)
        if item is None:
            continue
        expected_counts[item["obligation_class"]][row["final_verdict"]] += 1
        if row["final_verdict"] == "PARTIALLY_ADDRESSED":
            magnitude = _final_residual_obligation_class(item_id)
            if magnitude is not None:
                expected_magnitudes[item["obligation_class"]][magnitude] += 1
    if di["verdict_counts"] != expected_counts:
        fails.add("decision_inputs.verdict_counts does not recompute from the final row verdicts (§13)")
    if di["residual_obligation_class_counts"] != expected_magnitudes:
        fails.add("decision_inputs.residual_obligation_class_counts does not recompute from the PARTIALLY_ADDRESSED rows (§13)")

    p2_ids = [item["id"] for item in roadmap_items if item["obligation_class"] == "should_fix"]
    expected_num = sum(
        1 for item_id in p2_ids
        if row_by_item.get(item_id, {}).get("final_verdict") in ("FULLY_ADDRESSED", "PARTIALLY_ADDRESSED")
    )
    if di["should_fix_addressed_rate"] != {"numerator": expected_num, "denominator": len(p2_ids)}:
        fails.add("decision_inputs.should_fix_addressed_rate does not recompute over final should_fix verdicts (§6)")

    expected_regressions = [
        {"new_issue_id": rec["new_issue_id"], "severity": rec["severity"]}
        for rec in verdict_record["new_issues"] if rec["attribution"] == "regression"
    ]
    expected_non_regression = [
        rec["new_issue_id"] for rec in verdict_record["new_issues"] if rec["attribution"] != "regression"
    ]
    if di["regressions"] != expected_regressions:
        fails.add("decision_inputs.regressions does not equal the regression-attributed frozen new issues (§8/§13)")
    if di["non_regression_new_issue_ids"] != expected_non_regression:
        fails.add("decision_inputs.non_regression_new_issue_ids does not equal the frozen previously_missed/indeterminate ids (§8/§13)")

    expected_escalations = []
    for rec in verdict_record["escalation_exceptions"]:
        approval = approvals_by_exception.get(rec["exception_id"])
        expected_escalations.append({
            "exception_id": rec["exception_id"],
            "effective_approval_state": approval["approval_state"] if approval else "pending",
            "escalation_class": rec["escalation_class"],
            "mechanical_decision_impact": rec["mechanical_decision_impact"],
        })
    if di["escalations"] != expected_escalations:
        fails.add("decision_inputs.escalations does not equal the joined exception/approval summary (§5.3)")

    if di["apply_chain_witness"] != witness:
        fails.add(f"decision_inputs.apply_chain_witness {di['apply_chain_witness']!r} != recomputed witness {witness!r} (§11)")

    # --- §6 Step 1 recomputation (gates) ---
    g1 = any(
        row["final_verdict"] != row["phase2a_verdict"] and row["item_id"] not in chains
        for row in traceability["rows"]
    )
    pending = []
    # bound_tripped computed once, next to dissent_by_id (§7 SD-5).
    if bound_tripped:
        for dissent_id in dissent_by_id:
            if dissent_id not in adjudications_by_dissent:
                pending.append(f"G2(a): dissent {dissent_id} lacks its DissentAdjudication (bound tripped — covering cardinality)")

    def _covering_resolution(item_id, final_verdict):
        for rec in traceability["cross_model_resolutions"]:
            if rec["item_id"] != item_id:
                continue
            reapp = reapp_by_id.get(rec["reapplication_id"])
            if reapp is None:
                continue
            anchor = reapp["reapplied_verdict"] if rec["resolved_by"] == "system" else reapp["pre_reapplication_verdict"]
            if anchor == final_verdict:
                return True
        return False

    for item_id, row in row_by_item.items():
        if row.get("cross_model_status") == "diverges" and ROW_OBLIGATION_MAP[row["obligation_class"]] == "must_fix":
            if not _covering_resolution(item_id, row["final_verdict"]):
                pending.append(f"G2(b): must_fix diverges row {item_id} has no covering CrossModelResolution")
    for rec in verdict_record["escalation_exceptions"]:
        if rec["exception_id"] not in approvals_by_exception:
            pending.append(f"G2(c): escalation exception {rec['exception_id']} is pending user approval")
    accepted_reapps = {rec["reapplication_id"] for rec in traceability["g2d_acceptances"]}
    for dissent_id, adjudication in adjudications_by_dissent.items():
        if adjudication["outcome"] != "original_upheld":
            continue
        holders = _answers_in_current(f"adjudication:{dissent_id}")
        if len(holders) != 1:
            continue  # already a synthesis failure above
        current = holders[0]
        if current["reapplied_verdict"] == "CANNOT_VERIFY" and current["reapplication_id"] not in accepted_reapps:
            pending.append(f"G2(d): original_upheld dissent {dissent_id} fail-closed reapplication awaits user resolution")

    # --- emission-kind-scoped equality set (§13) ---
    recomputed = {"pending": pending, "g1": g1}
    emitted_state = traceability["decision_state"]
    if emitted_state == "aborted":
        # §13: an aborted emission carries its true root-cause abort_reason
        # and is EXEMPT from the deferral biconditional and Steps 2-3 (abort
        # precedence over deferral). The only checker-recomputable reason is
        # criteria_drift; the phase-lint reasons are fenced-call facts the
        # checker cannot re-derive and are accepted as recorded (the
        # manifest-class reasons would already have exited 2 above).
        reason = traceability.get("abort_reason")
        recomputed["expect"] = ("aborted", reason)
        if "reject_recommended" in di:
            fails.add("decision_inputs.reject_recommended must be ABSENT on a gated emission (§5.3 presence biconditional)")
        if reason in ("manifest_incomplete", "manifest_hash_mismatch", "synthesis_mismatch"):
            fails.add(
                f"aborted emission claims {reason!r} as root cause, but the checker reached recomputation — the "
                "§11 manifest layer validated against these same hash-bound inputs, so the claimed abort cannot be "
                "the true root cause (§13: an aborted emission carries its TRUE root-cause abort_reason)"
            )
        if g1 and reason != "criteria_drift":
            fails.add("Step 1 recomputes G1 (silent verdict change) — the aborted emission's true root cause is criteria_drift (§13)")
        if reason == "criteria_drift" and not g1:
            fails.add("the emission claims [RE-REVIEW-ABORT: criteria_drift] but no silent verdict change recomputes (§13)")
    elif g1:
        recomputed["expect"] = ("aborted", "criteria_drift")
        fails.add("Step 1 recomputes G1 (silent verdict change) — the emission must be [RE-REVIEW-ABORT: criteria_drift]")
    elif pending:
        recomputed["expect"] = ("user_review_required", None)
        if emitted_state != "user_review_required":
            fails.add(
                "G2 deferral biconditional: pending user-input state(s) exist, so user_review_required is the only "
                "checker-valid decision_state — " + "; ".join(pending)
            )
        if "reject_recommended" in di:
            fails.add("decision_inputs.reject_recommended must be ABSENT on a gated emission (§5.3 presence biconditional)")
    else:
        if emitted_state == "user_review_required":
            fails.add(
                "Step 1 recomputes no gate, but the emission carries decision_state 'user_review_required' "
                "(the G2 biconditional runs both directions)"
            )
        else:
            # Steps 2-3, recomputed independently from the raw records...
            p1_operands = []
            for item_id in must_fix_order:
                row = row_by_item.get(item_id)
                if row is None:
                    continue
                item = roadmap_by_id[item_id]
                severity = item.get("severity") if item.get("severity") in SEVERITIES else None
                p1_operands.append((row["final_verdict"], severity, _final_residual_obligation_class(item_id)))
            p2_partial_magnitudes = [
                _final_residual_obligation_class(item_id) for item_id in p2_ids
                if row_by_item.get(item_id, {}).get("final_verdict") == "PARTIALLY_ADDRESSED"
            ]
            p2_made_worse = any(
                row_by_item.get(item_id, {}).get("final_verdict") == "MADE_WORSE" for item_id in p2_ids
            )
            regression_severities = {entry["severity"] for entry in expected_regressions}
            raw_decision, raw_reject, raw_rule = derive_decision(
                p1_operands, p2_partial_magnitudes, p2_made_worse,
                expected_num, len(p2_ids), regression_severities, expected_escalations,
            )
            # ...AND from the emitted DecisionInputs copies.
            di_p1 = [
                (entry["final_verdict"], entry["driving_severity"], entry.get("residual_obligation_class"))
                for entry in di["per_item"]
            ]
            di_p2_partials = [
                mag for mag in RESIDUAL_OBLIGATION_CLASSES
                for _ in range(di["residual_obligation_class_counts"]["should_fix"][mag])
            ]
            di_decision, di_reject, _di_rule = derive_decision(
                di_p1,
                di_p2_partials,
                di["verdict_counts"]["should_fix"]["MADE_WORSE"] > 0,
                di["should_fix_addressed_rate"]["numerator"],
                di["should_fix_addressed_rate"]["denominator"],
                {entry["severity"] for entry in di["regressions"]},
                di["escalations"],
            )
            recomputed["expect"] = (raw_decision, None)
            recomputed["rule"] = raw_rule
            if emitted_state != raw_decision:
                fails.add(f"decision_state {emitted_state!r} != Steps 2-3 recomputed from the raw records ({raw_decision!r}, base {raw_rule})")
            if di_decision != raw_decision:
                fails.add(f"Steps 2-3 from DecisionInputs ({di_decision!r}) diverge from the raw-record recomputation ({raw_decision!r})")
            if "reject_recommended" not in di:
                fails.add("decision_inputs.reject_recommended must be PRESENT on a non-gated emission (§5.3 presence biconditional)")
            else:
                if di["reject_recommended"] != raw_reject:
                    fails.add(f"reject_recommended {di['reject_recommended']!r} != recomputed {raw_reject!r} (§6)")
                if di_reject != raw_reject:
                    fails.add("reject_recommended recomputed from DecisionInputs diverges from the raw-record recomputation")

    return fails, warnings, recomputed


# --- CLI -----------------------------------------------------------------------


def _load_json(path: Path, reason: str, label: str):
    try:
        return _strict_json_bytes(path.read_bytes(), label)
    except (OSError, ValueError) as exc:
        if reason.startswith("manifest"):
            raise ManifestError(reason, f"{label}: unreadable or invalid JSON ({exc})")
        raise ArtifactSchemaError(reason, f"{label}: unreadable or invalid JSON ({exc})")


def _verify_file_hash(path: Path, expected_sha256: str, label: str) -> bytes:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ManifestError("manifest_incomplete", f"{label}: unreadable ({exc})")
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise ManifestError("manifest_hash_mismatch", f"{label}: file bytes do not match the manifest sha256 (§11)")
    return raw


def run(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--precommitment", type=Path, required=True)
    parser.add_argument("--verdict-record", type=Path, required=True)
    parser.add_argument("--traceability", type=Path, required=True)
    parser.add_argument("--roadmap", type=Path, required=True,
                        help="the file the manifest's revision_roadmap entry hash-binds (Schema 7 machine form)")
    parser.add_argument(
        "--author-adjudication",
        type=Path,
        required=True,
        help="the exact #670 author sidecar hash-bound by the current input manifest",
    )
    parser.add_argument(
        "--revision-evidence-bundle",
        type=Path,
        required=True,
        help="the exact #670 bundle hash-bound by the current input manifest",
    )
    parser.add_argument(
        "--revision-evidence-root",
        type=Path,
        default=None,
        help="root for paths declared inside the bundle (default: bundle parent)",
    )
    parser.add_argument("--letter", type=Path, default=None,
                        help="the file the manifest's editorial_decision_letter entry hash-binds (markdown)")
    parser.add_argument("--apply-report", type=Path, action="append", default=[], dest="apply_reports",
                        help="apply-report file(s), in the manifest's apply_reports[] order")
    args = parser.parse_args(argv)

    try:
        manifest = _load_json(args.manifest, "manifest_incomplete", "manifest")
        validate_manifest(manifest)
        artifacts = manifest["artifacts"]

        roadmap_raw = _verify_file_hash(args.roadmap, artifacts["revision_roadmap"]["sha256"], "revision_roadmap file")
        try:
            roadmap_payload = _strict_json_bytes(roadmap_raw, "revision_roadmap file")
        except ValueError as exc:
            raise ManifestError("manifest_incomplete", str(exc)) from exc
        roadmap_items = load_roadmap(roadmap_payload)
        author_raw = _verify_file_hash(
            args.author_adjudication,
            artifacts["author_adjudication"]["sha256"],
            "author_adjudication file",
        )
        try:
            author_payload = _strict_json_bytes(author_raw, "author_adjudication file")
        except ValueError as exc:
            raise ManifestError("manifest_incomplete", str(exc)) from exc
        original_sha = (
            artifacts["original_manuscript"]["sha256"]
            if artifacts["original_manuscript"]["present"]
            else None
        )
        author_by_item = load_author_adjudication(
            author_payload,
            roadmap_items=roadmap_items,
            roadmap_sha256=hashlib.sha256(roadmap_raw).hexdigest(),
            original_manuscript_sha256=original_sha,
        )

        letter_blocks = None
        if artifacts["editorial_decision_letter"]["present"]:
            if args.letter is None:
                raise ManifestError("manifest_incomplete", "manifest declares editorial_decision_letter present — --letter is required")
            letter_raw = _verify_file_hash(args.letter, artifacts["editorial_decision_letter"]["sha256"], "editorial_decision_letter file")
            letter_blocks = parse_letter_blocks(letter_raw.decode("utf-8"))
        elif args.letter is not None:
            raise ManifestError("manifest_incomplete", "--letter provided but the manifest declares the letter absent")

        report_entries = artifacts["apply_reports"]["items"] if artifacts["apply_reports"]["present"] else []
        if len(args.apply_reports) != len(report_entries):
            raise ManifestError(
                "manifest_incomplete",
                f"manifest declares {len(report_entries)} apply report(s); {len(args.apply_reports)} provided via --apply-report",
            )
        report_payloads = []
        for i, (path, entry) in enumerate(zip(args.apply_reports, report_entries)):
            raw = _verify_file_hash(path, entry["sha256"], f"apply report [{i}]")
            try:
                report_payloads.append(_strict_json_bytes(raw, f"apply report [{i}]"))
            except ValueError as exc:
                raise ManifestError("manifest_incomplete", str(exc)) from exc
        witness, witness_notes = compute_apply_chain_witness(manifest, report_payloads)

        bundle_entry = artifacts["revision_evidence_bundle"]
        bundle_raw = _verify_file_hash(
            args.revision_evidence_bundle,
            bundle_entry["sha256"],
            "revision_evidence_bundle file",
        )
        try:
            bundle = _strict_json_bytes(bundle_raw, "revision_evidence_bundle file")
        except ValueError as exc:
            raise ManifestError("manifest_incomplete", str(exc)) from exc
        try:
            validate_bundle(
                bundle,
                root=args.revision_evidence_root or args.revision_evidence_bundle.parent,
            )
        except RevisionContractError as exc:
            raise ManifestError(
                "manifest_hash_mismatch",
                "revision_evidence_bundle replay failed: " + "; ".join(exc.failures),
            ) from exc
        validate_revision_bundle_binding(bundle, manifest)

        precommitment = _load_json(args.precommitment, "phase1_lint_failed", "precommitment")
        validate_precommitment(precommitment)
        verdict_record = _load_json(args.verdict_record, "phase2a_lint_failed", "verdict_record")
        validate_verdict_record(verdict_record)
        traceability = _load_json(args.traceability, "phase2b_lint_failed", "traceability")
        validate_traceability(traceability)

        # Hash chain (§11): the same-inputs proof.
        if precommitment["input_manifest_hash"] != canonical_hash(manifest):
            raise ManifestError("manifest_hash_mismatch", "precommitment.input_manifest_hash does not recompute from the manifest (§11 chain)")
        if verdict_record["precommitment_hash"] != canonical_hash(precommitment):
            raise ManifestError("manifest_hash_mismatch", "verdict_record.precommitment_hash does not recompute from the precommitment artifact (§11 chain)")
        if traceability["verdict_record_hash"] != canonical_hash(verdict_record):
            raise ManifestError("manifest_hash_mismatch", "traceability.verdict_record_hash does not recompute from the verdict_record artifact (§11 chain)")
    except ManifestError as exc:
        print(f"[RE-REVIEW-ABORT: {exc.reason}]")
        print(f"FAIL: {exc}")
        return EXIT_INVALID
    except ArtifactSchemaError as exc:
        print(f"[RE-REVIEW-ABORT: {exc.reason}]")
        print(f"FAIL: {exc}")
        return EXIT_INVALID

    fails, warnings, recomputed = check(
        manifest, precommitment, verdict_record, traceability,
        roadmap_items, author_by_item, letter_blocks, witness, witness_notes,
    )
    for note in warnings:
        print(note, file=sys.stderr)
    if fails.messages:
        print("[RE-REVIEW-ABORT: synthesis_mismatch]")
        for message in fails.messages:
            print(f"MISMATCH: {message}")
        return EXIT_SYNTHESIS
    expect = recomputed.get("expect")
    outcome = expect[0] if expect else traceability["decision_state"]
    print(
        f"re-review synthesis ok: round {manifest['round_id']!r}, revision {traceability['revision']}, "
        f"decision_state {outcome!r}, apply_chain_witness {witness!r}"
    )
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(run())
