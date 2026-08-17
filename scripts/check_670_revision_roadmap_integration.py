#!/usr/bin/env python3
"""Static integration guard for the #670 non-ranking revision contract.

The executable runtimes own artifact replay. This guard pins the pieces that
could otherwise drift independently: current/legacy version isolation, the
authority split, #576 lockstep names and required inputs, hermetic runtime
shape, author-facing no-rank presentation, documentation wiring, and the
unchanged upstream finding-detection prompts.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent

REVISION_SCHEMAS = (
    Path("shared/contracts/revision/revision_roadmap.schema.json"),
    Path("shared/contracts/revision/author_adjudication.schema.json"),
    Path("shared/contracts/revision/author_adjudication_input.schema.json"),
    Path("shared/contracts/revision/claim_surface_manifest.schema.json"),
    Path("shared/contracts/revision/integrity_pass_receipt.schema.json"),
    Path("shared/contracts/revision/integrity_correction_list.schema.json"),
    Path("shared/contracts/revision/integrity_correction_authorization.schema.json"),
    Path("shared/contracts/revision/integrity_correction_authorization_input.schema.json"),
    Path("shared/contracts/revision/revision_evidence_bundle.schema.json"),
)
PATCH_SCHEMA = Path("shared/contracts/patch/revision_patch.schema.json")
PATCH_LEGACY_SCHEMA = Path(
    "shared/contracts/patch/legacy/v1_0/revision_patch.schema.json"
)
RE_REVIEW_SCHEMAS = tuple(
    Path("shared/contracts/re_review") / name
    for name in (
        "input_manifest.schema.json",
        "precommitment.schema.json",
        "verdict_record.schema.json",
        "traceability.schema.json",
    )
)
RE_REVIEW_LEGACY_SCHEMAS = tuple(
    Path("shared/contracts/re_review/legacy/v1_0") / name.name
    for name in RE_REVIEW_SCHEMAS
)

ROADMAP_RUNTIME = Path("scripts/revision_roadmap.py")
APPLY_RUNTIME = Path("scripts/ars_apply_revision_patch.py")
RE_REVIEW_RUNTIME = Path("scripts/check_re_review_synthesis.py")
LEGACY_APPLY_RUNTIME = Path("scripts/legacy/ars_apply_revision_patch_v1_0.py")

RUNTIME_HASHES = {
    ROADMAP_RUNTIME: "5341358d489a550b56f0e7efde850c551b6d9df41106b0462e2f804ab4de9998",
    APPLY_RUNTIME: "9aa84eb23c1b10f5c23008ff51d2feb6e64440834b48b090c833fe44669014b3",
    RE_REVIEW_RUNTIME: "8347ec3766857366cc0c6ffd30021afcebf8d0528a83927fabfce9ecb66a59ab",
}

# #670 originally froze the five reviewer finding producers. Subsequent
# deliberate contract changes added pointer-only criteria binding, categorical
# criterion judgements, an explicit NOT_CALIBRATED boundary, typed provenance,
# and confidence-as-disclosure-only semantics. These hashes are re-pinned with
# those reviewed changes; exact hashes keep later drift auditable without a
# live-model comparison.
DETECTION_HASHES = {
    Path("academic-paper-reviewer/agents/eic_agent.md"):
        "c5ec3150c7e7cc4c89358853d13af0bde8f211e0a735bcd8c72330d1f931943d",
    Path("academic-paper-reviewer/agents/methodology_reviewer_agent.md"):
        "91e462ee104cc253a44d387570ea95a49a4efffcc2b4765617baf292431de6cb",
    Path("academic-paper-reviewer/agents/domain_reviewer_agent.md"):
        "eb6660aafadc851e3fc4545111b5113d467c9eb263ef069394db62c944ece1e5",
    Path("academic-paper-reviewer/agents/perspective_reviewer_agent.md"):
        "49bb946547593a918bd60faee88555d46a2a10b39f2857ef94163eef65920d81",
    Path("academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md"):
        "b42eb5559bf91c8767f85e532dfa240e5e30feb92ae3fc0be96f20058acfcf6a",
    Path("academic-paper-reviewer/templates/peer_review_report_template.md"):
        "5da1f9d24d6e321cec5f38c13fa03fe23b9363b1842cb0d8111c5e39a810c7d1",
}

AUTHOR_PRESENTATION_FILES = (
    Path("academic-paper-reviewer/templates/editorial_decision_template.md"),
    Path("academic-paper-reviewer/agents/editorial_synthesizer_agent.md"),
    Path("academic-paper/agents/revision_coach_agent.md"),
)
AUTHOR_RANK_RE = re.compile(
    r"\bPriority\s+[123]\b|\bP[123]\b|Estimated\s+(?:total\s+)?effort|"
    r"Suggested\s+Revision\s+Order|address\s+these\s+first|if\s+time\s+permits|"
    r"\(\s*ranked\s*\)|most\s+severe\s+first|\|\s*Rank\s*\|",
    re.IGNORECASE,
)

REQUIRED_POINTERS = {
    Path("docs/design/2026-08-10-670-non-ranking-revision-roadmap-spec.md"): (
        "immutable reviewer-owned core",
        "author-adjudication/1.0",
        "claim-surface-manifest/1.0",
        "revision-evidence-bundle/1.0",
        "unregistered_claim_drift_review_required: true",
    ),
    Path("shared/contracts/README.md"): (
        "Non-ranking revision authority (#670)",
        "patch/legacy/v1_0/",
        "re_review/legacy/v1_0/",
    ),
    Path("shared/handoff_schemas.md"): (
        "revision-roadmap/1.0",
        "author_adjudication.schema.json",
        "revision_evidence_bundle.schema.json",
        "obligation_class",
    ),
    Path("academic-paper-reviewer/agents/editorial_synthesizer_agent.md"): (
        "revision-roadmap/1.0",
        "proposed_targets[]",
        "transport reference, not a rank",
    ),
    Path("academic-paper-reviewer/templates/editorial_decision_template.md"): (
        "Obligation class",
        "Cost scope",
        "Bounded consequence",
        "never a work rank",
    ),
    Path("academic-paper/agents/revision_coach_agent.md"): (
        "build-adjudication",
        "will_address",
        "wont_address",
        "not_on_point",
    ),
    Path("academic-paper/agents/draft_writer_agent.md"): (
        "patch_format_version: 1.1",
        "author-adjudication/1.0",
        "collateral_authorization_ids[]",
    ),
    Path("academic-paper/references/revision_patch_protocol.md"): (
        "--author-adjudication",
        "--claim-surface-manifest",
        "validate-bundle",
        "unregistered_claim_drift_review_required: true",
    ),
    Path("academic-pipeline/agents/pipeline_orchestrator_agent.md"): (
        "build-adjudication",
        "review_noop",
        "report 1.3",
        "revision-evidence-bundle/1.0",
        "--revision-evidence-bundle",
    ),
    Path("academic-paper-reviewer/references/re_review_mode_protocol.md"): (
        "author-adjudication/1.0",
        "revision-evidence-bundle/1.0",
        "--author-adjudication",
        "mixed 1.0/1.1",
        "--revision-evidence-bundle",
    ),
}

FORBIDDEN_IMPORT_ROOTS = {
    "anthropic",
    "datetime",
    "http",
    "openai",
    "requests",
    "socket",
    "subprocess",
    "time",
    "urllib",
}
FORBIDDEN_SCAN_CALLS = {"glob", "rglob", "iterdir", "listdir", "scandir", "walk"}


class DuplicateKeyError(ValueError):
    pass


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


def _property_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(properties)
        for child in value.values():
            names.update(_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(_property_names(child))
    return names


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _schema_checks(root: Path) -> list[str]:
    errors: list[str] = []
    schemas: dict[Path, dict[str, Any]] = {}
    for relative in (
        *REVISION_SCHEMAS,
        PATCH_SCHEMA,
        PATCH_LEGACY_SCHEMA,
        *RE_REVIEW_SCHEMAS,
        *RE_REVIEW_LEGACY_SCHEMAS,
    ):
        try:
            schema = _load_json(root / relative)
            Draft202012Validator.check_schema(schema)
            schemas[relative] = schema
        except (OSError, UnicodeError, ValueError, DuplicateKeyError) as exc:
            errors.append(f"{relative}: schema load/check failed: {exc}")
        except Exception as exc:  # jsonschema.SchemaError without version coupling
            errors.append(f"{relative}: schema load/check failed: {exc}")

    if len(schemas) < len(
        (*REVISION_SCHEMAS, PATCH_SCHEMA, PATCH_LEGACY_SCHEMA, *RE_REVIEW_SCHEMAS, *RE_REVIEW_LEGACY_SCHEMAS)
    ):
        return errors

    roadmap = schemas[REVISION_SCHEMAS[0]]
    roadmap_props = roadmap.get("properties", {})
    item = roadmap.get("$defs", {}).get("roadmap_item", {})
    item_props = item.get("properties", {})
    if roadmap_props.get("schema_version", {}).get("const") != "revision-roadmap/1.0":
        errors.append("roadmap current schema_version drifted")
    if not {"base_draft_sha256", "block_manifest_sha256"}.issubset(roadmap.get("required", [])):
        errors.append("roadmap lost exact draft/manifest bindings")
    if not {
        "source_refs",
        "obligation_class",
        "cost_scope",
        "consequence_if_unaddressed",
        "proposed_targets",
    }.issubset(item.get("required", [])):
        errors.append("roadmap item lost independent/source/exact-scope requirements")
    forbidden_current = {"priority", "type", "deadline_suggestion", "author_triage", "display_order"}
    if forbidden_current & (set(roadmap_props) | set(item_props)):
        errors.append("roadmap current schema reintroduced legacy/author-owned fields")

    author = schemas[REVISION_SCHEMAS[1]]
    author_defs = author.get("$defs", {})
    if author.get("properties", {}).get("schema_version", {}).get("const") != "author-adjudication/1.0":
        errors.append("author sidecar version drifted")
    event_props = author_defs.get("author_event", {}).get("properties", {})
    if event_props.get("source", {}).get("const") != "explicit_session_user_message":
        errors.append("author event no longer requires explicit session user input")
    triage = author_defs.get("adjudication", {}).get("properties", {}).get("author_triage", {}).get("enum")
    if triage != ["will_address", "wont_address", "not_on_point"]:
        errors.append("author triage vocabulary drifted")
    claim_required = set(author_defs.get("claim_authorization", {}).get("required", []))
    if not {
        "surface_id", "scoped_manifest_id", "claim_id", "block_id",
        "original_text_sha256", "replacement_text", "replacement_text_sha256",
        "from_rung", "to_rung", "direction",
    }.issubset(claim_required):
        errors.append("claim authorization lost exact surface/replacement/movement fields")

    claim_surface = schemas[REVISION_SCHEMAS[3]]
    surface_required = set(claim_surface.get("$defs", {}).get("surface", {}).get("required", []))
    if not {
        "scoped_manifest_id", "claim_id", "block_id", "utf8_start", "utf8_end",
        "original_text", "original_text_sha256", "intent_claim_text_sha256", "current_rung",
    }.issubset(surface_required):
        errors.append("claim surface lost exact Claim Intent/UTF-8 bindings")

    bundle = schemas[REVISION_SCHEMAS[-1]]
    bundle_refs = {
        row.get("$ref")
        for row in bundle.get("properties", {}).get("rounds", {}).get("items", {}).get("oneOf", [])
    }
    if bundle_refs != {
        "#/$defs/review_roadmap_round",
        "#/$defs/review_noop_round",
        "#/$defs/integrity_correction_round",
    }:
        errors.append("bundle round union drifted")

    patch = schemas[PATCH_SCHEMA]
    patch_defs = patch.get("$defs", {})
    if patch.get("oneOf") != [
        {"$ref": "#/$defs/review_patch"},
        {"$ref": "#/$defs/integrity_patch"},
    ]:
        errors.append("current patch is not the closed review/integrity union")
    for name, context in (("review_patch", "review_roadmap"), ("integrity_patch", "integrity_correction")):
        props = patch_defs.get(name, {}).get("properties", {})
        if props.get("patch_format_version", {}).get("const") != "1.1":
            errors.append(f"{name} no longer pins current patch 1.1")
        if props.get("authorization_context", {}).get("const") != context:
            errors.append(f"{name} authorization context drifted")
    legacy = schemas[PATCH_LEGACY_SCHEMA]
    if legacy.get("properties", {}).get("patch_format_version", {}).get("const") != "1.0":
        errors.append("archived patch schema no longer pins 1.0")

    for relative in RE_REVIEW_SCHEMAS:
        schema = schemas[relative]
        if schema.get("properties", {}).get("contract_version", {}).get("const") != "1.1":
            errors.append(f"{relative}: current contract_version must be 1.1")
        old_names = {"priority", "residual_magnitude", "residual_magnitude_counts", "p2_addressed_rate"}
        if old_names & _property_names(schema):
            errors.append(f"{relative}: legacy field name reintroduced")
    for relative in RE_REVIEW_LEGACY_SCHEMAS:
        schema = schemas[relative]
        version = schema.get("properties", {}).get("contract_version", {}).get("const")
        if version is not None and version != "1.0":
            errors.append(f"{relative}: archived version drifted")
    manifest = schemas[RE_REVIEW_SCHEMAS[0]]
    required_artifacts = set(manifest["properties"]["artifacts"]["required"])
    if required_artifacts != {
        "original_manuscript", "revised_manuscript", "revision_roadmap",
        "author_adjudication", "revision_evidence_bundle", "editorial_decision_letter",
        "response_to_reviewers", "revision_patches", "apply_reports",
        "round1_findings", "round1_config_cards",
    }:
        errors.append("#576 current manifest does not carry exactly eleven artifact keys")
    artifact_properties = manifest["properties"]["artifacts"]["properties"]
    for artifact in (
        "original_manuscript",
        "revised_manuscript",
        "revision_roadmap",
        "author_adjudication",
        "revision_evidence_bundle",
    ):
        if artifact_properties.get(artifact, {}).get("$ref") != (
            "#/$defs/required_artifact_entry"
        ):
            errors.append(
                f"#576 current manifest {artifact} is not a hard-required present artifact"
            )
    trace_names = _property_names(schemas[RE_REVIEW_SCHEMAS[-1]])
    if not {"author_triage", "author_reason", "authorized_targets", "claim_strength_authorizations"}.issubset(trace_names):
        errors.append("#576 traceability lost exact author-sidecar copy fields")
    return errors


def _schema_id_uniqueness_checks(root: Path) -> list[str]:
    errors: list[str] = []
    contracts_root = root / "shared" / "contracts"
    seen: dict[str, Path] = {}
    for path in sorted(contracts_root.rglob("*.schema.json")):
        relative = path.relative_to(root)
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: cannot inspect shipped schema $id: {exc}")
            continue
        schema_id = schema.get("$id") if isinstance(schema, dict) else None
        if not isinstance(schema_id, str) or not schema_id:
            errors.append(f"{relative}: shipped schema has no nonempty $id")
            continue
        prior = seen.get(schema_id)
        if prior is not None:
            errors.append(
                f"duplicate shipped schema $id {schema_id!r}: "
                f"{prior.relative_to(root)} and {relative}"
            )
        else:
            seen[schema_id] = path
    return errors


def _runtime_checks(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, expected in RUNTIME_HASHES.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing runtime: {relative}")
            continue
        actual = _sha256(path)
        if actual != expected:
            errors.append(f"{relative}: frozen runtime hash drifted ({actual})")
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, SyntaxError) as exc:
            errors.append(f"{relative}: runtime parse failed: {exc}")
            continue
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in FORBIDDEN_IMPORT_ROOTS:
                        errors.append(f"{relative}:{node.lineno}: forbidden model/network/clock/process import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.split(".")[0] in FORBIDDEN_IMPORT_ROOTS:
                    errors.append(f"{relative}:{node.lineno}: forbidden model/network/clock/process import {module}")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in FORBIDDEN_SCAN_CALLS:
                    errors.append(f"{relative}:{node.lineno}: forbidden ambient scan {node.func.attr}()")

    apply_text = (root / APPLY_RUNTIME).read_text(encoding="utf-8")
    for token in (
        'REPORT_FORMAT_VERSION = "1.3"',
        '"--block-manifest"',
        '"--author-adjudication"',
        '"--claim-surface-manifest"',
        '"--integrity-issue-list"',
        '"--integrity-authorization"',
    ):
        if token not in apply_text:
            errors.append(f"current apply runtime missing {token!r}")
    roadmap_text = (root / ROADMAP_RUNTIME).read_text(encoding="utf-8")
    for token in (
        'CURRENT_PATCH_VERSION = "1.1"',
        'CURRENT_REPORT_VERSION = "1.3"',
        '"unregistered_claim_drift_review_required": True',
        '"revision_patch_sha256"',
        '"integrity_authorization"',
        'sub.add_parser("validate-bundle")',
    ):
        if token not in roadmap_text:
            errors.append(f"roadmap runtime missing {token!r}")

    re_review_text = (root / RE_REVIEW_RUNTIME).read_text(encoding="utf-8")
    for token in (
        '"--revision-evidence-bundle"',
        '"--revision-evidence-root"',
        "validate_bundle(",
        "validate_revision_bundle_binding(bundle, manifest)",
    ):
        if token not in re_review_text:
            errors.append(f"re-review runtime missing {token!r}")

    legacy_text = (root / LEGACY_APPLY_RUNTIME).read_text(encoding="utf-8")
    for token in (
        "REPO_ROOT = Path(__file__).resolve().parent.parent.parent",
        '/ "legacy"',
        '/ "v1_0"',
        'REPORT_FORMAT_VERSION = "1.2"',
    ):
        if token not in legacy_text:
            errors.append(f"legacy apply isolation missing {token!r}")
    return errors


def _documentation_checks(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, tokens in REQUIRED_POINTERS.items():
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: cannot read required integration surface: {exc}")
            continue
        for token in tokens:
            if token not in text:
                errors.append(f"{relative}: missing required #670 pointer {token!r}")
    for relative in AUTHOR_PRESENTATION_FILES:
        text = (root / relative).read_text(encoding="utf-8")
        match = AUTHOR_RANK_RE.search(text)
        if match:
            errors.append(f"{relative}: author-facing work-rank/time presentation {match.group(0)!r}")
    return errors


def _hash_boundary_checks(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, expected in DETECTION_HASHES.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing frozen reviewer detection surface: {relative}")
            continue
        actual = _sha256(path)
        if actual != expected:
            errors.append(f"{relative}: reviewer detection surface drifted ({actual})")
    return errors


def run_checks(root: Path = REPO_ROOT) -> list[str]:
    return [
        *_schema_id_uniqueness_checks(root),
        *_schema_checks(root),
        *_runtime_checks(root),
        *_documentation_checks(root),
        *_hash_boundary_checks(root),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    errors = run_checks(args.root.resolve())
    if errors:
        print("#670 revision-roadmap integration failed", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("#670 revision-roadmap integration ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
