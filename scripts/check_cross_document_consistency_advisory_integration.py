#!/usr/bin/env python3
"""Check the hermetic #672 cross-document advisory integration boundary.

Behavioral tests own byte replay and finalization semantics.  This guard keeps
the independently editable surfaces aligned: five closed schemas, the standard-
library runtime boundary, frozen legacy evidence/ClaimIntent identities, the
one #660-then-#672 Stage-5 checkpoint, consumer wording, and the honest
UNMEASURED-with-no-measurement-artifact boundary.

Exit 0 on success, 1 on integration errors, and 2 on invocation errors.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import stat
import sys
import tomllib
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent

SIDECAR_SCHEMA = Path(
    "shared/contracts/passport/preregistration_artifact.schema.json"
)
EVIDENCE_SCHEMA = Path("shared/contracts/evidence/evidence_row_v1_2.schema.json")
MANIFEST_SCHEMA = Path(
    "shared/contracts/audit/cross_document_source_manifest.schema.json"
)
DRAFT_SCHEMA = Path(
    "shared/contracts/audit/cross_document_consistency_advisory_draft.schema.json"
)
ADVISORY_SCHEMA = Path(
    "shared/contracts/audit/cross_document_consistency_advisory.schema.json"
)
RUNTIME = Path("scripts/build_cross_document_consistency_advisory.py")
RUNTIME_TEST = Path("scripts/test_cross_document_consistency_advisory.py")
DESIGN_SPEC = Path(
    "docs/design/2026-08-10-672-cross-document-consistency-advisory-spec.md"
)
PROTOCOL = Path(
    "shared/references/cross_document_consistency_advisory_protocol.md"
)
CONTRACT_README = Path("shared/contracts/README.md")
EVIDENCE_PROTOCOL = Path("shared/references/evidence_row_protocol.md")
CLAIM_LADDER = Path("shared/references/claim_strength_ladder.md")
PREREG_GUIDE = Path("deep-research/references/preregistration_guide.md")
HANDOFF_SCHEMAS = Path("shared/handoff_schemas.md")
DEEP_SKILL = Path("deep-research/SKILL.md")
ARCHITECT = Path("deep-research/agents/research_architect_agent.md")
ARCHITECT_MIRROR = Path("agents/research_architect_agent.md")
HANDOFF_EXAMPLE = Path("deep-research/examples/handoff_to_paper.md")
PAPER_SKILL = Path("academic-paper/SKILL.md")
INTAKE_AGENT = Path("academic-paper/agents/intake_agent.md")
PIPELINE_SKILL = Path("academic-pipeline/SKILL.md")
PIPELINE_ORCHESTRATOR = Path(
    "academic-pipeline/agents/pipeline_orchestrator_agent.md"
)
INTEGRITY_PROTOCOL = Path(
    "academic-pipeline/references/integrity_review_protocol.md"
)
STATE_MACHINE = Path("academic-pipeline/references/pipeline_state_machine.md")
CHANGELOG = Path("CHANGELOG.md")
HELDOUT_ROOT = Path("evals/heldout/cross_document_consistency")
HELDOUT_STATUS = HELDOUT_ROOT / "README.md"
CI_MANIFEST = Path("scripts/_ci_pytest_manifest.toml")
WORKFLOW = Path(".github/workflows/spec-consistency.yml")

LEGACY_HASHES = {
    Path("shared/contracts/evidence/evidence_row.schema.json"):
        "02f4fc4e32658249e7065724f1cb5c2f9dcec3f599f86a1a7ffee726ae422f5a",
    Path("shared/contracts/evidence/evidence_row_v1_1.schema.json"):
        "ab7fdb15b8845bcf898fef5177c636b8ca43f2785c3b79bf284fa04a4ede14b9",
    Path("scripts/evidence_rows.py"):
        "eccfa0a5cfe9b438aac9c4ec85cd6c2ca07052de7eb521cfc1e7f799a971d7e3",
    Path("shared/contracts/passport/claim_intent_manifest.schema.json"):
        "d6c4fd060812dc2a2b2dd73b6d9e77e366fcc0803486d5f38b4def6893d70cec",
    Path("shared/contracts/revision/claim_surface_manifest.schema.json"):
        "85460c1c195c890eb505c95e2767f72461c4a1f631203b7b26decb7a841afb1d",
    Path("deep-research/templates/preregistration_template.md"):
        "40054e26c527ff3dd237a5eef3fee60b821cf8549e210d48a057005333c8e0d2",
}

SCHEMA_VERSIONS = {
    SIDECAR_SCHEMA: "preregistration-artifact/1.0",
    EVIDENCE_SCHEMA: "evidence-row/1.2",
    MANIFEST_SCHEMA: "cross-document-source-manifest/1.0",
    DRAFT_SCHEMA: "cross-document-consistency-advisory-draft/1.0",
    ADVISORY_SCHEMA: "cross-document-consistency-advisory/1.0",
}
NEW_SCHEMA_HASHES = {
    SIDECAR_SCHEMA:
        "998c8a1df9149a591fc722fabc2b2afce4bc27ea23212c2b7a8e0c4f1bcea05b",
    EVIDENCE_SCHEMA:
        "277e7b7b437a523286e06d2f55d058989f88865f4a364045405c5bcb33d94c51",
    MANIFEST_SCHEMA:
        "875285713a881d6228d7d1a4af882d66d881628549b6917b96c350e0b4fd3d4a",
    DRAFT_SCHEMA:
        "fa061192e0d97f3913b9af83228f4355f1879a56955d2609cc1279b7f206f3e0",
    ADVISORY_SCHEMA:
        "2bc6229ad77a5e86bd96021b3ac1d1fc8afc6834c4158280ca01091629652418",
}
SCHEMA_EXTERNAL_REF_ALLOWLIST = {
    SIDECAR_SCHEMA: frozenset(),
    EVIDENCE_SCHEMA: frozenset(),
    MANIFEST_SCHEMA: frozenset(),
    DRAFT_SCHEMA: frozenset(),
    ADVISORY_SCHEMA: frozenset(
        {"../evidence/evidence_row_v1_2.schema.json"}
    ),
}
PAIR_ORDER = (
    "abstract_results",
    "discussion_results",
    "methods_reported_analyses",
    "manuscript_preregistration",
)
PAIR_ROLES = {
    "abstract_results": ("abstract", "results"),
    "discussion_results": ("discussion", "results"),
    "methods_reported_analyses": ("methods", "reported_analyses"),
    "manuscript_preregistration": (
        "manuscript_report",
        "preregistration",
        "disclosure_scope",
    ),
}
FINDING_TYPES = {
    "abstract_results": {
        "numeric_mismatch",
        "direction_mismatch",
        "significance_mismatch",
        "claim_strength_rung_mismatch",
    },
    "discussion_results": {
        "direction_mismatch",
        "claim_strength_rung_mismatch",
        "scope_or_population_overreach",
    },
    "methods_reported_analyses": {
        "declared_analysis_no_reported_counterpart",
        "reported_analysis_no_declared_counterpart",
        "analysis_specification_conflict",
    },
    "manuscript_preregistration": {"undisclosed_preregistration_deviation"},
}
OUTCOMES = {
    "POTENTIAL_INCONSISTENCY_LOCATED",
    "NO_LISTED_INCONSISTENCY_LOCATED",
}
NEGATIVE_BASES = {
    "legitimate_compression",
    "same_rung_rewording",
    "disclosed_deviation",
    "other_no_listed_observation",
}
FAILURE_STATES = {
    "not_checked",
    "source_missing",
    "access_failed",
    "retrieval_failed",
}
EVIDENCE_STATES = FAILURE_STATES | {"agent_extracted", "checked_no_match"}
DIAGNOSTIC_CODES = {
    "NAMED_INPUT_UNREADABLE",
    "DRAFT_CONTRACT_INVALID",
    "SOURCE_MANIFEST_INVALID",
    "SOURCE_BINDING_INVALID",
    "EVIDENCE_REPLAY_INVALID",
    "FINAL_ARTIFACT_INVALID",
    "RESOURCE_LIMIT",
}
BOUNDARY = {
    "semantic_observation_not_recomputed": True,
    "stage_4_5_verdict_unchanged": True,
    "stage_5_routing_unchanged": True,
    "integrity_issue_counts_unchanged": True,
    "formatter_gate_unchanged": True,
    "terminal_policy_unchanged": True,
    "score_not_produced": True,
    "automatic_rewrite_not_performed": True,
    "agreement_not_certified": True,
}
RESOURCE_LIMITS = {
    "MAX_DRAFT_BYTES": 16 * 1024 * 1024,
    "MAX_MANIFEST_BYTES": 1 * 1024 * 1024,
    "MAX_SIDECAR_BYTES": 1 * 1024 * 1024,
    "MAX_FINAL_BYTES": 32 * 1024 * 1024,
    "MAX_ACCEPTED_DRAFT_BYTES": 8 * 1024 * 1024,
    "MAX_PREREGISTRATION_BYTES": 64 * 1024 * 1024,
    "MAX_TOTAL_SOURCE_BYTES": 72 * 1024 * 1024,
    "MAX_OBSERVATIONS": 4096,
    "MAX_JSON_DEPTH": 100,
    "MAX_JSON_NODES": 1_000_000,
    "MAX_PAGE_SIZE": 25,
}
FORBIDDEN_PROPERTY_NAMES = {
    "acceptance",
    "adequacy",
    "approval",
    "authorization",
    "clean_certificate",
    "compliance",
    "confidence",
    "consent_protocol",
    "gate",
    "measurement_rows",
    "pass_fail",
    "probability",
    "readiness",
    "revision_operation",
    "rewrite",
    "score",
    "severity",
    "verdict",
}
FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp",
    "anthropic",
    "cohere",
    "http",
    "httpx",
    "mistralai",
    "multiprocessing",
    "openai",
    "requests",
    "socket",
    "subprocess",
    "urllib3",
}
FORBIDDEN_IMPORT_PREFIXES = {"http.client", "urllib.request"}
FORBIDDEN_CALLS = {
    "__import__",
    "compile",
    "eval",
    "exec",
    "os.getenv",
    "os.popen",
    "os.system",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.run",
    "time.monotonic",
    "time.perf_counter",
    "time.time",
    "urllib.request.urlopen",
}
ALLOWED_RUNTIME_IMPORTS = frozenset(
    {
        "__future__",
        "argparse",
        "collections.abc",
        "copy",
        "datetime",
        "hashlib",
        "json",
        "os",
        "pathlib",
        "re",
        "stat",
        "sys",
        "tempfile",
        "typing",
        "unicodedata",
        "urllib.parse",
    }
)
ALLOWED_CLI_OPTIONS = frozenset(
    {
        "--accepted-draft",
        "--advisory",
        "--artifact-id",
        "--artifact-provenance",
        "--companion",
        "--declared-at",
        "--draft",
        "--manifest",
        "--output",
        "--page",
        "--page-size",
        "--preregistration-companion",
        "--preregistration-record",
        "--relative-path",
        "--status",
    }
)
ALLOWED_SUBCOMMANDS = frozenset(
    {"build-preregistration-artifact", "finalize", "render", "validate"}
)
FORBIDDEN_CONSUMER_IDENTIFIER_PARTS = frozenset(
    {
        "auditartifactentry",
        "auditresult",
        "auditverdict",
        "claimintent",
        "codexaudit",
        "multifileaudit",
        "p1finding",
        "p2finding",
        "p3finding",
        "torturedphrase",
    }
)
FORBIDDEN_LEGACY_MAPPING_LITERALS = frozenset(
    {"P1", "P2", "P3", "PASS", "MINOR", "MATERIAL"}
)
FORBIDDEN_CLOCK_SUFFIXES = {
    "datetime.now",
    "datetime.today",
    "datetime.utcnow",
    "date.today",
}
FORBIDDEN_SCAN_NAMES = {
    "fwalk",
    "glob",
    "iglob",
    "iterdir",
    "listdir",
    "rglob",
    "scandir",
    "walk",
}
PURE_RENDER_FORBIDDEN_NAMES = FORBIDDEN_SCAN_NAMES | {
    "open",
    "read_bytes",
    "read_text",
    "write_bytes",
    "write_text",
    "urlopen",
}

AFFIRMATIVE_CLAIM_RE = re.compile(
    r"\b(?:improves?|increases?|boosts?|achieves?|demonstrates?|establishes?|"
    r"guarantees?|ensures?|proves?|certifies?|delivers?|provides?)\b"
    r"[^.\n]{0,100}\b(?:accuracy|efficacy|coverage(?:\s+improvement)?|"
    r"clean(?:[- ]document)?|cross[- ]document\s+agreement|agreement)\b",
    flags=re.IGNORECASE,
)
OWNED_DOC_MARKERS = (
    "#672",
    "ADV-XDOC",
    "build-preregistration-artifact",
    "cross-document",
    "cross_document_consistency",
    "evidence-row/1.2",
    "preregistration-artifact/1.0",
)
DEDICATED_CLAIM_CEILING_DOCS = frozenset(
    {DESIGN_SPEC, PROTOCOL, HELDOUT_STATUS}
)
RENDERER_CLAIM_CEILING_SENTENCE = (
    "NO LISTED INCONSISTENCY LOCATED — not proof of agreement, completeness, "
    "or a clean document."
)
FUNCTION_SCOPED_RUNTIME_MARKERS: dict[str, tuple[str, ...]] = {
    "_array": ("len(value) > maximum",),
    "_precheck_depth": ("if depth > MAX_JSON_DEPTH:",),
    "_count_nodes": ("if count > MAX_JSON_NODES:",),
    "_strict_json_bytes": (
        "_precheck_depth(text, code=code, path=path)",
        "value = json.loads(",
        "_count_nodes(value, code=code, path=path)",
        "_reject_unsafe_json_strings(value, code=code, path=path)",
    ),
    "build_preregistration_artifact": (
        'if state == "provided":',
        "text = _strict_source(\n            companion_bytes,",
        'label="preregistration companion"',
        "if not text.strip():",
        '_fail("SOURCE_BINDING_INVALID", "companion", "must not be blank")',
    ),
    "_prepare_inputs": ("if total > MAX_TOTAL_SOURCE_BYTES:",),
    "finalize_advisory": (
        "if len(_canonical_bytes(report)) > MAX_FINAL_BYTES:",
    ),
    "paginate": ("page_size > MAX_PAGE_SIZE",),
    "render_advisory": (
        RENDERER_CLAIM_CEILING_SENTENCE,
        'if observation["outcome"] == "NO_LISTED_INCONSISTENCY_LOCATED":',
        "result = f\"{observation['outcome']} — {observation['negative_basis']}\"",
    ),
}

REQUIRED_POINTERS: dict[Path, tuple[str, ...]] = {
    DESIGN_SPEC: (
        "DESIGN-FROZEN / UNMEASURED",
        "evidence-row/1.2",
        "build-preregistration-artifact",
        "#660 first and #672 second",
        "ADVISORY_UNAVAILABLE:<CODE>",
    ),
    PROTOCOL: (
        "preregistration-artifact/1.0",
        "evidence-row/1.2",
        "cross-document-source-manifest/1.0",
        "cross-document-consistency-advisory-draft/1.0",
        "cross-document-consistency-advisory/1.0",
        "LLM-ADVISORY",
        "UNMEASURED",
        "ADVISORY_UNAVAILABLE:<CODE>",
    ),
    CONTRACT_README: (
        "Cross-document consistency advisory (#672)",
        "preregistration-artifact/1.0",
        str(EVIDENCE_SCHEMA),
        "#660 runs first and #672 second",
        "ADVISORY_UNAVAILABLE:<CODE>",
    ),
    EVIDENCE_PROTOCOL: (
        str(EVIDENCE_SCHEMA),
        "cross_document_consistency",
        "disclosure_scope",
        "UNMEASURED",
    ),
    CLAIM_LADDER: ("#672", "LLM-ADVISORY", "UNMEASURED"),
    PREREG_GUIDE: (
        "build-preregistration-artifact",
        "preregistration-artifact/1.0",
        "UNMEASURED",
    ),
    HANDOFF_SCHEMAS: (
        "preregistration-artifact/1.0",
        "digest-check",
        "byte-for-byte",
    ),
    DEEP_SKILL: (
        "preregistration-artifact/1.0",
        "build-preregistration-artifact",
        "research_architect_agent",
    ),
    ARCHITECT: (
        "preregistration-artifact/1.0",
        "build-preregistration-artifact",
        "must not",
    ),
    ARCHITECT_MIRROR: (
        "preregistration-artifact/1.0",
        "build-preregistration-artifact",
        "must not",
    ),
    HANDOFF_EXAMPLE: (
        "preregistration-artifact/1.0",
        "agreement",
        "record_digest",
    ),
    PAPER_SKILL: (
        "preregistration-artifact/1.0",
        str(PROTOCOL),
    ),
    INTAKE_AGENT: (
        "preregistration-artifact/1.0",
        "record_digest",
        "companion",
    ),
    PIPELINE_SKILL: (
        "#660 first and #672 second",
        "ADVISORY_UNAVAILABLE:<CODE>",
        "LLM-ADVISORY",
        "UNMEASURED",
    ),
    PIPELINE_ORCHESTRATOR: (
        "#660",
        "#672",
        "ADVISORY_UNAVAILABLE:<CODE>",
        "accepted_draft_artifact_id",
        "accepted_draft_sha256",
    ),
    INTEGRITY_PROTOCOL: (
        "#660",
        "#672",
        "Stage 4.5",
        "Stage 5",
    ),
    STATE_MACHINE: (
        "#660",
        "#672",
        "ADVISORY_UNAVAILABLE:<CODE>",
        "Stage 5",
    ),
    HELDOUT_STATUS: (
        "UNMEASURED",
        "no `measurement-*.json`",
        "not proof of agreement",
    ),
    CHANGELOG: (
        "cross-document consistency advisory",
        "#672",
        "UNMEASURED",
    ),
}


class DuplicateKeyError(ValueError):
    """Raised when strict JSON encounters a duplicate member name."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant {token!r}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError("top level must be an object")
    return value


def _properties(schema: dict[str, Any]) -> set[str]:
    value = schema.get("properties")
    return set(value) if isinstance(value, dict) else set()


def _all_property_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(properties)
        for child in value.values():
            names.update(_all_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(_all_property_names(child))
    return names


def _all_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            refs.add(ref)
        for child in value.values():
            refs.update(_all_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_all_refs(child))
    return refs


def _check_closed(value: Any, location: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        # Partial conditional/contains fragments intentionally constrain a base
        # object without reopening it.  A shape-owning object has two or more
        # required members and must close them itself.
        if (
            value.get("type") == "object"
            and len(value.get("required", [])) >= 2
            and value.get("additionalProperties") is not False
        ):
            errors.append(f"{location}: object schema must be recursively closed")
        for key, child in value.items():
            _check_closed(child, f"{location}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_closed(child, f"{location}[{index}]", errors)


def _const(schema: dict[str, Any], field: str) -> Any:
    return schema["properties"][field].get("const")


def _schema_errors(root: Path) -> list[str]:
    errors: list[str] = []
    schemas: dict[Path, dict[str, Any]] = {}
    for relative, version in SCHEMA_VERSIONS.items():
        try:
            schema_path = root / relative
            raw = schema_path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != NEW_SCHEMA_HASHES[relative]:
                errors.append(f"{relative}: frozen new schema sha256 drifted")
            schema = _load_json(schema_path)
            Draft202012Validator.check_schema(schema)
            _check_closed(schema, str(relative), errors)
            if _const(schema, "schema_version") != version:
                errors.append(f"{relative}: schema_version must equal {version}")
                continue
            schemas[relative] = schema
            forbidden = _all_property_names(schema) & FORBIDDEN_PROPERTY_NAMES
            if forbidden:
                errors.append(
                    f"{relative}: forbidden determination fields: {sorted(forbidden)}"
                )
            external_refs = {ref for ref in _all_refs(schema) if not ref.startswith("#")}
            if external_refs != set(SCHEMA_EXTERNAL_REF_ALLOWLIST[relative]):
                errors.append(
                    f"{relative}: schema external $ref allowlist drifted: "
                    f"{sorted(external_refs)}"
                )
        except (OSError, UnicodeError, ValueError, KeyError) as exc:
            errors.append(f"{relative}: schema load/check failed: {type(exc).__name__}")
    if len(schemas) != len(SCHEMA_VERSIONS):
        return errors

    sidecar = schemas[SIDECAR_SCHEMA]
    if set(sidecar["properties"]["status"].get("enum", [])) != {
        "provided", "not_provided", "access_failed", "retrieval_failed"
    }:
        errors.append("preregistration sidecar status mapping vocabulary drifted")
    if sidecar["properties"]["source_artifact_size_bytes"].get("maximum") != 67108864:
        errors.append("preregistration sidecar 64 MiB ceiling drifted")
    if len(sidecar.get("allOf", [])) != 1:
        errors.append("preregistration sidecar provided/unavailable conditional drifted")

    manifest = schemas[MANIFEST_SCHEMA]
    artifacts = manifest["properties"]["artifacts"]
    if (artifacts.get("minItems"), artifacts.get("maxItems")) != (2, 2):
        errors.append("source manifest must contain exactly two artifacts")
    if len(artifacts.get("allOf", [])) != 2:
        errors.append("source manifest one-manuscript/one-preregistration matrix drifted")
    manifest_required = set(manifest.get("required", []))
    if not {"accepted_draft_artifact_id", "accepted_draft_sha256", "manifest_digest"} <= manifest_required:
        errors.append("source manifest designated accepted-draft binding drifted")
    artifact = manifest["$defs"]["artifact"]
    if set(artifact["properties"]["artifact_state"].get("enum", [])) != {
        "present", "source_missing", "access_failed", "retrieval_failed"
    }:
        errors.append("source manifest availability vocabulary drifted")

    evidence = schemas[EVIDENCE_SCHEMA]
    if _const(evidence, "surface") != "cross_document_consistency":
        errors.append("evidence-row/1.2 surface drifted")
    if set(evidence["$defs"]["pair_kind"].get("enum", [])) != set(PAIR_ORDER):
        errors.append("evidence-row pair roster drifted")
    if set(evidence["$defs"]["evidence_slot"]["properties"]["evidence_state"].get("enum", [])) != EVIDENCE_STATES:
        errors.append("evidence-row state vocabulary drifted")
    for pair, roles in PAIR_ROLES.items():
        slot_def = evidence["$defs"][f"{pair}_slots"]
        expected_count = len(roles)
        if (slot_def.get("minItems"), slot_def.get("maxItems")) != (expected_count, expected_count):
            errors.append(f"evidence-row {pair} slot cardinality drifted")
        prefix = slot_def.get("prefixItems", [])
        actual_roles: list[Any] = []
        for item in prefix:
            ref = item.get("$ref", "")
            actual_roles.append(ref.rsplit("/slot_", 1)[-1] if "/slot_" in ref else None)
        if tuple(actual_roles) != roles:
            errors.append(f"evidence-row {pair} ordered roles drifted")
    checked = evidence["$defs"].get("checked_scope", {})
    if set(checked.get("required", [])) != {
        "source_span_utf8", "scope_sha256", "scope_utf8_bytes", "checked_at", "completeness_provenance"
    }:
        errors.append("checked_no_match checked_scope binding drifted")
    if evidence["$defs"].get("cache", {}).get("properties", {}).get("status", {}).get("const") != "not_used":
        errors.append("evidence-row cache must remain not_used")

    draft = schemas[DRAFT_SCHEMA]
    if _const(draft, "layer") != "LLM-ADVISORY":
        errors.append("draft layer must equal LLM-ADVISORY")
    observations = draft["properties"]["observations"]
    if observations.get("maxItems") != 4096:
        errors.append("draft observation ceiling drifted")
    if set(draft["$defs"]["pair_kind"].get("enum", [])) != set(PAIR_ORDER):
        errors.append("draft pair roster drifted")
    if set(draft["$defs"]["outcome"].get("enum", [])) != OUTCOMES:
        errors.append("draft outcome vocabulary drifted")
    if set(draft["$defs"]["negative_basis"].get("enum", [])) != NEGATIVE_BASES:
        errors.append("draft negative-basis vocabulary drifted")
    if set(draft["$defs"]["finding_type"].get("enum", [])) != set().union(*FINDING_TYPES.values()):
        errors.append("draft finding-type vocabulary drifted")
    if len(observations.get("allOf", [])) != 4:
        errors.append("draft must require at least one observation for every pair")
    observation = draft["$defs"]["observation"]
    if set(observation["properties"]["check_state"].get("enum", [])) != {"performed", "not_checked"}:
        errors.append("draft check-state vocabulary drifted")
    if len(observation.get("allOf", [])) < 15:
        errors.append("draft pair/outcome/witness conditional matrix weakened")
    prereg_slots = draft["$defs"]["manuscript_preregistration_slots"]
    if (prereg_slots.get("minItems"), prereg_slots.get("maxItems")) != (3, 3):
        errors.append("draft preregistration three-witness rule drifted")

    final = schemas[ADVISORY_SCHEMA]
    if _const(final, "layer") != "LLM-ADVISORY":
        errors.append("final layer must equal LLM-ADVISORY")
    if _const(final, "evaluation_status") != "UNMEASURED":
        errors.append("final evaluation_status must equal UNMEASURED")
    pair_results = final["properties"]["pair_results"]
    if (pair_results.get("minItems"), pair_results.get("maxItems")) != (4, 4):
        errors.append("final pair roster cardinality drifted")
    refs = tuple(item.get("$ref") for item in pair_results.get("prefixItems", []))
    expected_refs = tuple(f"#/$defs/pair_result_{pair}" for pair in PAIR_ORDER)
    if refs != expected_refs or pair_results.get("items") is not False:
        errors.append("final canonical pair ordering drifted")
    binding_required = set(final["$defs"]["input_binding"].get("required", []))
    required_binding = {
        "draft_sha256", "source_manifest_sha256", "preregistration_record_sha256",
        "preregistration_record_digest", "accepted_draft_artifact_id",
        "accepted_draft_sha256", "source_bundle_sha256",
    }
    if not required_binding <= binding_required:
        errors.append("final complete source/input binding drifted")
    boundary = final["$defs"]["boundary"]
    actual_boundary = {
        key: item.get("const") for key, item in boundary.get("properties", {}).items()
    }
    if actual_boundary != BOUNDARY or set(boundary.get("required", [])) != set(BOUNDARY):
        errors.append("final noninterference boundary drifted")
    final_observation = final["$defs"]["final_observation"]
    row_ref = final_observation["properties"]["evidence_row"].get("$ref")
    if row_ref != "../evidence/evidence_row_v1_2.schema.json":
        errors.append("final carrier must embed evidence-row/1.2 by relative ref")
    return errors


def _call_name(node: ast.Call) -> str:
    parts: list[str] = []
    value: ast.expr = node.func
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def _literal(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        values = [_literal(item) for item in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(values)
        if isinstance(node, ast.Set):
            return set(values)
        return values
    if isinstance(node, ast.Dict):
        return {_literal(key): _literal(value) for key, value in zip(node.keys, node.values)}
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Add)):
        left, right = _literal(node.left), _literal(node.right)
        return left * right if isinstance(node.op, ast.Mult) else left + right
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "frozenset" and len(node.args) == 1:
        return frozenset(_literal(node.args[0]))
    raise ValueError(f"unsupported literal: {type(node).__name__}")


def _assignments(tree: ast.Module) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                result[node.targets[0].id] = _literal(node.value)
            except ValueError:
                pass
    return result


def _normalized_identifier(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def _docstring_nodes(tree: ast.Module) -> set[int]:
    result: set[int] = set()
    owners: list[ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef] = [tree]
    owners.extend(
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    for owner in owners:
        if owner.body and isinstance(owner.body[0], ast.Expr):
            value = owner.body[0].value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                result.add(id(value))
    return result


def _runtime_errors(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        source = (root / RUNTIME).read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, UnicodeError, SyntaxError) as exc:
        return [f"{RUNTIME}: runtime parse failed: {type(exc).__name__}"]

    constants = _assignments(tree)
    expected_constants: dict[str, Any] = {
        "SIDECAR_SCHEMA_VERSION": SCHEMA_VERSIONS[SIDECAR_SCHEMA],
        "EVIDENCE_SCHEMA_VERSION": SCHEMA_VERSIONS[EVIDENCE_SCHEMA],
        "MANIFEST_SCHEMA_VERSION": SCHEMA_VERSIONS[MANIFEST_SCHEMA],
        "DRAFT_SCHEMA_VERSION": SCHEMA_VERSIONS[DRAFT_SCHEMA],
        "REPORT_SCHEMA_VERSION": SCHEMA_VERSIONS[ADVISORY_SCHEMA],
        "SURFACE": "cross_document_consistency",
        "LAYER": "LLM-ADVISORY",
        "EVALUATION_STATUS": "UNMEASURED",
        "PAIR_ORDER": PAIR_ORDER,
        "PAIR_ROLES": PAIR_ROLES,
        "DIAGNOSTIC_CODES": frozenset(DIAGNOSTIC_CODES),
        "BOUNDARY": BOUNDARY,
        **RESOURCE_LIMITS,
    }
    for name, expected in expected_constants.items():
        if constants.get(name) != expected:
            errors.append(f"runtime constant {name} drifted")
    if constants.get("TEMPLATE_SHA256") != LEGACY_HASHES[Path("deep-research/templates/preregistration_template.md")]:
        errors.append("runtime frozen preregistration-template digest drifted")
    runtime_findings = constants.get("FINDING_TYPES")
    if runtime_findings != {key: frozenset(value) for key, value in FINDING_TYPES.items()}:
        errors.append("runtime pair/finding matrix drifted")

    imports: set[str] = set()
    calls: list[tuple[str, ast.Call]] = []
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
        elif isinstance(node, ast.Call):
            calls.append((_call_name(node), node))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = node
    unexpected_imports = sorted(imports - ALLOWED_RUNTIME_IMPORTS)
    if unexpected_imports:
        errors.append(f"runtime import allowlist drifted: {unexpected_imports}")
    bad_imports = sorted(
        name for name in imports
        if name.split(".", 1)[0] in FORBIDDEN_IMPORT_ROOTS
        or any(name == prefix or name.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES)
    )
    if bad_imports:
        errors.append(f"runtime has forbidden model/network/process import: {bad_imports}")

    forbidden_identifiers: set[str] = set()
    for node in ast.walk(tree):
        candidate: str | None = None
        if isinstance(node, (ast.Name, ast.Attribute)):
            candidate = node.id if isinstance(node, ast.Name) else node.attr
        elif isinstance(node, ast.arg):
            candidate = node.arg
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            candidate = node.name
        if candidate is None:
            continue
        normalized = _normalized_identifier(candidate)
        if any(part in normalized for part in FORBIDDEN_CONSUMER_IDENTIFIER_PARTS):
            forbidden_identifiers.add(candidate)
    docs = _docstring_nodes(tree)
    forbidden_literals: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if id(node) in docs:
            continue
        normalized = _normalized_identifier(node.value)
        if (
            node.value in FORBIDDEN_LEGACY_MAPPING_LITERALS
            or any(part in normalized for part in FORBIDDEN_CONSUMER_IDENTIFIER_PARTS)
        ):
            forbidden_literals.add(node.value)
    if forbidden_identifiers or forbidden_literals:
        errors.append(
            "runtime structured nonconsumer boundary drifted: "
            f"identifiers={sorted(forbidden_identifiers)}, "
            f"literals={sorted(forbidden_literals)}"
        )

    cli_options: set[str] = set()
    subcommands: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr == "add_argument" and node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                cli_options.add(first.value)
        elif node.func.attr == "add_parser" and node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                subcommands.add(first.value)
    for node in ast.walk(tree):
        if not isinstance(node, ast.For) or not isinstance(node.target, ast.Name):
            continue
        if not isinstance(node.iter, (ast.Tuple, ast.List)):
            continue
        if any(
            isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and call.func.attr == "add_parser"
            and call.args
            and isinstance(call.args[0], ast.Name)
            and call.args[0].id == node.target.id
            for statement in node.body
            for call in ast.walk(statement)
        ):
            subcommands.update(
                item.value
                for item in node.iter.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            )
    if cli_options != set(ALLOWED_CLI_OPTIONS) or subcommands != set(ALLOWED_SUBCOMMANDS):
        errors.append(
            "runtime parser input allowlist drifted: "
            f"options={sorted(cli_options)}, subcommands={sorted(subcommands)}"
        )
    bad_calls = sorted(
        {
            name
            for name, _ in calls
            if name in FORBIDDEN_CALLS
            or any(name == suffix or name.endswith("." + suffix) for suffix in FORBIDDEN_CLOCK_SUFFIXES)
        }
    )
    if bad_calls:
        errors.append(f"runtime has forbidden model/network/process/clock call: {bad_calls}")
    scan_calls = sorted({name for name, _ in calls if name.rsplit(".", 1)[-1] in FORBIDDEN_SCAN_NAMES})
    if scan_calls:
        errors.append(f"runtime has forbidden ambient directory scan: {scan_calls}")
    if "--all" in source:
        errors.append("runtime renderer must not expose --all")
    for marker in (
        'add_parser("build-preregistration-artifact"',
        'for name in ("finalize", "validate", "render")',
        'add_argument("--page"',
        'add_argument("--page-size"',
        'print(f"ADVISORY_UNAVAILABLE:{exc.code}"',
    ):
        if marker not in source:
            errors.append(f"runtime CLI/restricted diagnostic marker missing: {marker}")

    for function_name, markers in FUNCTION_SCOPED_RUNTIME_MARKERS.items():
        function = functions.get(function_name)
        function_source = (
            ast.get_source_segment(source, function) if function is not None else None
        )
        if function_source is None:
            errors.append(
                f"runtime function-scoped hardened structure drifted: "
                f"missing {function_name}"
            )
            continue
        missing = [marker for marker in markers if marker not in function_source]
        if missing:
            errors.append(
                f"runtime function-scoped hardened structure drifted: "
                f"{function_name} missing {missing}"
            )
            continue
        positions = tuple(function_source.index(marker) for marker in markers)
        if positions != tuple(sorted(positions)):
            errors.append(
                f"runtime function-scoped hardened structure drifted: "
                f"{function_name} marker order"
            )

    structure_markers = (
        "class _ClosedArgumentParser(argparse.ArgumentParser):",
        "parser = _ClosedArgumentParser(description=__doc__, allow_abbrev=False)",
        "args = _parser().parse_args(argv)",
        "flags |= os.O_NOFOLLOW",
        "flags |= os.O_NONBLOCK",
        "if not stat.S_ISREG(metadata.st_mode):",
        "object_pairs_hook=object_pairs",
        "parse_constant=reject_constant",
        "parse_float=reject_float",
        "def _strict_accepted_draft(raw: bytes) -> str:",
        "if not text.strip():",
        'unreadable_code="SOURCE_BINDING_INVALID"',
        'locator = slot["document_locator"]',
        "locator['kind']",
        "locator['value']",
    )
    missing_structure = [marker for marker in structure_markers if marker not in source]
    if missing_structure:
        errors.append(f"runtime hardened structure drifted: {missing_structure}")
    accepted_draft_validator = functions.get("_strict_accepted_draft")
    accepted_draft_source = (
        ast.get_source_segment(source, accepted_draft_validator)
        if accepted_draft_validator is not None
        else None
    )
    if (
        accepted_draft_source is None
        or "if not text.strip():" not in accepted_draft_source
        or '"SOURCE_BINDING_INVALID", "accepted draft", "must not be blank"'
        not in accepted_draft_source
    ):
        errors.append(
            "runtime hardened structure drifted: accepted-draft blank preflight"
        )
    try:
        preflight_order = tuple(
            source.index(marker)
            for marker in (
                "descriptor = os.open(path, flags)",
                "metadata = os.fstat(descriptor)",
                "if not stat.S_ISREG(metadata.st_mode):",
                "chunk = os.read(descriptor",
            )
        )
        if preflight_order != tuple(sorted(preflight_order)):
            errors.append("runtime regular-file preflight must precede every read")
    except ValueError:
        errors.append("runtime regular-file preflight structure missing")
    reachable = {"render_advisory", "paginate", "_markdown_inert"}
    queue = list(reachable)
    while queue:
        name = queue.pop()
        function = functions.get(name)
        if function is None:
            errors.append(f"pure renderer helper missing: {name}")
            continue
        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            called = _call_name(node)
            leaf = called.rsplit(".", 1)[-1]
            if leaf in functions and leaf not in reachable:
                reachable.add(leaf)
                queue.append(leaf)
            if leaf in PURE_RENDER_FORBIDDEN_NAMES:
                errors.append(f"pure renderer reaches forbidden I/O call: {called}")
    return errors


def _legacy_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, expected in LEGACY_HASHES.items():
        try:
            actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        except OSError as exc:
            errors.append(f"{relative}: frozen identity unreadable: {type(exc).__name__}")
            continue
        if actual != expected:
            errors.append(f"{relative}: frozen legacy/template sha256 drifted")
    return errors


def _documentation_errors(root: Path) -> list[str]:
    errors: list[str] = []
    texts: dict[Path, str] = {}
    for relative, markers in REQUIRED_POINTERS.items():
        try:
            text = (root / relative).read_text(encoding="utf-8")
            texts[relative] = text
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: documentation unreadable: {type(exc).__name__}")
            continue
        missing = [marker for marker in markers if marker not in text]
        if missing:
            errors.append(f"{relative}: required #672 pointers missing: {missing}")
        claim_regions = (
            [text]
            if relative in DEDICATED_CLAIM_CEILING_DOCS
            else [
                paragraph
                for paragraph in re.split(r"\n\s*\n", text)
                if any(marker in paragraph for marker in OWNED_DOC_MARKERS)
            ]
        )
        if any(AFFIRMATIVE_CLAIM_RE.search(region) for region in claim_regions):
            errors.append(
                f"{relative}: affirmative #672 accuracy/efficacy/coverage/clean/agreement claim"
            )
    if texts.get(ARCHITECT) != texts.get(ARCHITECT_MIRROR):
        errors.append("research architect mirror drifted")

    combined_pipeline = "\n".join(
        texts.get(path, "")
        for path in (PIPELINE_SKILL, PIPELINE_ORCHESTRATOR, INTEGRITY_PROTOCOL, STATE_MACHINE)
    )
    exact_join_markers = (
        "input_binding.artifact.artifact_id",
        "artifact_sha256",
        "accepted_draft_artifact_id",
        "accepted_draft_sha256",
    )
    if any(marker not in combined_pipeline for marker in exact_join_markers):
        errors.append("#660/#672 exact accepted-draft ID/SHA machine join is undocumented")
    coexistence_markers = (
        "#660 first and #672 second",
        "writes no",
        "Stage 5",
        "revision",
        "stale",
    )
    if any(marker not in combined_pipeline for marker in coexistence_markers):
        errors.append("#660/#672 order, distinct failure, nonblocking, or stale semantics drifted")

    semantic_docs = "\n".join(texts.get(path, "") for path in REQUIRED_POINTERS)
    if "consent/protocol" not in semantic_docs or "#667/#681" not in semantic_docs:
        errors.append("consent/protocol authority must remain an interface note to #667/#681")
    if "ClaimIntent" not in semantic_docs or "no score" not in semantic_docs:
        errors.append("ClaimIntent/no-score noninterference boundary is undocumented")
    return errors


def _heldout_errors(root: Path) -> list[str]:
    errors: list[str] = []
    heldout = root / HELDOUT_ROOT
    try:
        metadata = heldout.lstat()
    except OSError as exc:
        return [f"{HELDOUT_ROOT}: held-out status directory missing: {type(exc).__name__}"]
    if heldout.is_symlink() or not stat.S_ISDIR(metadata.st_mode):
        return [f"{HELDOUT_ROOT}: must be a real canonical directory"]
    entries = list(heldout.iterdir())
    unexpected = sorted(entry.name for entry in entries if entry.name != "README.md")
    if unexpected:
        errors.append(
            f"{HELDOUT_ROOT}: only canonical README.md is allowed; unexpected entries: "
            f"{unexpected}"
        )
    status = root / HELDOUT_STATUS
    try:
        status_metadata = status.lstat()
        if status.is_symlink() or not stat.S_ISREG(status_metadata.st_mode):
            errors.append(f"{HELDOUT_STATUS}: must be one real regular file")
    except OSError as exc:
        errors.append(f"{HELDOUT_STATUS}: canonical README unreadable: {type(exc).__name__}")
    return errors


def _ci_errors(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = tomllib.loads((root / CI_MANIFEST).read_text(encoding="utf-8"))
        serialized = json.dumps(manifest, sort_keys=True)
        for marker in (
            "672-cross-document-consistency-advisory",
            "672-cross-document-consistency-integration",
            str(RUNTIME_TEST),
            "scripts/test_check_cross_document_consistency_advisory_integration.py",
        ):
            if marker not in serialized:
                errors.append(f"CI manifest missing #672 marker: {marker}")
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"{CI_MANIFEST}: CI manifest unreadable: {type(exc).__name__}")
    try:
        workflow = (root / WORKFLOW).read_text(encoding="utf-8")
        if "check_cross_document_consistency_advisory_integration.py" not in workflow:
            errors.append("spec-consistency workflow missing direct #672 integration guard")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{WORKFLOW}: workflow unreadable: {type(exc).__name__}")
    return errors


def run_checks(root: Path) -> list[str]:
    """Return all static #672 integration errors beneath *root*."""
    return [
        *_legacy_errors(root),
        *_schema_errors(root),
        *_runtime_errors(root),
        *_documentation_errors(root),
        *_heldout_errors(root),
        *_ci_errors(root),
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        root = _parser().parse_args(argv).root.resolve()
    except SystemExit as exc:
        return int(exc.code)
    errors = run_checks(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Cross-document consistency advisory integration check passed (#672).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
