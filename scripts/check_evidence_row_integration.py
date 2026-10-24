#!/usr/bin/env python3
"""Static integration guard for the #656 shared evidence-row contract.

The executable runtime owns dynamic row validation and rendering.  This guard
owns the cross-file pointers and non-goals that could otherwise drift while the
runtime tests remain green: one schema/state/label vocabulary, the Schema-5 and
Phase-E producer/consumer wiring, no display-time retrieval imports, no human-read
fields, and no accidental opt-in claim-audit adoption.

Exit codes: 0 pass, 1 one or more integration errors, 2 invocation error.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent

SCHEMA_REL = "shared/contracts/evidence/evidence_row.schema.json"
RUNTIME_REL = "scripts/evidence_rows.py"

EXPECTED_STATES = {
    "verified_exact_match",
    "agent_extracted",
    "unconfirmed_anchor",
    "not_checked",
    "source_missing",
    "access_failed",
    "retrieval_failed",
    "anchorless",
}

EXPECTED_LABELS = {
    "verified_exact_match": "VERIFIED EXACT MATCH",
    "agent_extracted": "AGENT-EXTRACTED — NOT AUTHORITATIVE",
    "unconfirmed_anchor": "UNCONFIRMED ANCHOR",
    "not_checked": "NOT CHECKED",
    "source_missing": "SOURCE NOT HELD",
    "access_failed": "ACCESS FAILED",
    "retrieval_failed": "RETRIEVAL FAILED",
    "anchorless": "ANCHORLESS — NO EXCERPT",
}

REQUIRED_POINTERS = {
    "shared/contracts/README.md": (
        SCHEMA_REL,
        RUNTIME_REL,
        "evidence-row/1.0",
        "phase_e_claim_verification",
        "--allow-legacy-absence",
    ),
    "shared/handoff_schemas.md": (
        "phases.E_claims.evidence_rows[]",
        SCHEMA_REL,
        RUNTIME_REL,
        "LEGACY — EVIDENCE ROWS UNAVAILABLE",
        "--allow-legacy-absence",
    ),
    "shared/references/evidence_row_protocol.md": (
        SCHEMA_REL,
        RUNTIME_REL,
        "evidence-row/1.0",
        "phase_e_claim_verification",
        "human-read",
        "--allow-legacy-absence",
    ),
    "academic-pipeline/references/claim_verification_protocol.md": (
        "phases.E_claims.evidence_rows[]",
        SCHEMA_REL,
        RUNTIME_REL,
        "LEGACY — EVIDENCE ROWS UNAVAILABLE",
        "--allow-legacy-absence",
    ),
    "academic-pipeline/agents/integrity_verification_agent.md": (
        "phases.E_claims.evidence_rows[]",
        SCHEMA_REL,
        RUNTIME_REL,
        "build(...)",
        "validate(...)",
        "human_read_log",
        "--allow-legacy-absence",
    ),
    "academic-pipeline/agents/pipeline_orchestrator_agent.md": (
        "phases.E_claims.evidence_rows[]",
        SCHEMA_REL,
        RUNTIME_REL,
        "LEGACY — EVIDENCE ROWS UNAVAILABLE",
        "requested page",
        "--allow-legacy-absence",
    ),
    "docs/design/2026-08-09-656-shared-evidence-row-contract-spec.md": (
        SCHEMA_REL,
        RUNTIME_REL,
        "evidence-row/1.0",
        "phase_e_claim_verification",
        "claim_audit_results[]",
        "--allow-legacy-absence",
    ),
}

# #1006: Phase E compares a claim only with the cited version of a work, turns an
# unreadable cited version into an access note, and names the version in the
# row's display_label (no schema field; the renderer already prints the label).
CITED_VERSION_RULES = {
    "academic-pipeline/references/claim_verification_protocol.md": (
        "Cited version only (#1006)",
        "Never substitute another version of the work",
        "If the cited version's full text cannot be read, record UNVERIFIABLE_ACCESS for that source",
        "do not choose one: record UNVERIFIABLE_ACCESS for that source",
        "never a support verdict",
        "ask the user for the PDF of the cited version",
        "open-access page that cannot be read",
        "`VERSION_INCONSISTENT_CITATION`",
        "`phase2_investigation/version_records.yaml`",
        "use its `known_versions[]` to tell that record apart",
        "whether or not `version_records.yaml` exists",
        "An access note on one source never hides a distortion found in another",
        "the part of the claim it is cited for (its own anchor)",
        "per-source results in this order: MAJOR_DISTORTION, UNVERIFIABLE, MINOR_DISTORTION, UNVERIFIABLE_ACCESS, VERIFIED",
        "VERIFIED only when every cited source was read and supports the part it is cited for",
        "`source.display_label`",
        "`version not identified`",
    ),
    "academic-pipeline/agents/integrity_verification_agent.md": (
        "Compare the claim only with the cited version",
        "Never substitute another version of the work",
        "If the cited version's full text cannot be read, record UNVERIFIABLE_ACCESS for that source",
        "do not choose one: record UNVERIFIABLE_ACCESS for that source",
        "never a support verdict",
        "ask the user for the PDF of the cited version",
        "open-access page that cannot be read",
        "VERSION_INCONSISTENT_CITATION",
        "phase2_investigation/version_records.yaml",
        "use its known_versions[] to tell that record apart",
        "whether or not version_records.yaml exists",
        "An access note on one source never hides a distortion found in another",
        "the part of the claim it is cited for (its own anchor)",
        "per-source results in this order: MAJOR_DISTORTION, UNVERIFIABLE, MINOR_DISTORTION, UNVERIFIABLE_ACCESS, VERIFIED",
        "VERIFIED only when every cited source was read and supports the part it is cited for",
        "source.display_label",
        '"version not identified"',
    ),
    "academic-pipeline/agents/pipeline_orchestrator_agent.md": (
        "cited version not readable or not identified (UNVERIFIABLE_ACCESS",
        "ask for the PDF of that version",
        "`VERSION_INCONSISTENT_CITATION`",
    ),
}

# The pre-#1006 rule named only a paywall, which let an unreadable open-access
# page fall through to another version of the work.
RETIRED_ACCESS_RULES = {
    "academic-pipeline/references/claim_verification_protocol.md": (
        "If source is behind paywall, note as UNVERIFIABLE_ACCESS",
    ),
    "academic-pipeline/agents/integrity_verification_agent.md": (
        "If source is behind paywall, note as UNVERIFIABLE_ACCESS",
    ),
}

OUT_OF_SCOPE = (
    "shared/contracts/passport/claim_audit_result.schema.json",
    "scripts/claim_audit_pipeline.py",
    "scripts/claim_audit_finalizer.py",
    "scripts/check_claim_audit_consistency.py",
    "academic-pipeline/agents/claim_ref_alignment_audit_agent.md",
    "academic-paper/agents/formatter_agent.md",
)

FORBIDDEN_IMPORT_ROOTS = {
    "anthropic",
    "http",
    "openai",
    "os",
    "requests",
    "socket",
    "subprocess",
}

# ``urllib.parse`` is the runtime's strict once-decode substrate.  Retrieval
# siblings are forbidden even though they share that allowed top-level package.
FORBIDDEN_IMPORT_PREFIXES = {
    "urllib.error",
    "urllib.request",
    "urllib3",
}

RENDER_ROOTS = {"paginate", "render_html", "render_markdown"}
FORBIDDEN_RENDER_CALLS = {
    "Popen",
    "check_call",
    "check_output",
    "connect",
    "create_connection",
    "open",
    "read_bytes",
    "read_text",
    "run",
    "system",
    "urlopen",
    "write_bytes",
    "write_text",
}

FORBIDDEN_SCHEMA_FIELDS = {
    "abstract",
    "full_text",
    "human_read_at",
    "human_read_source",
    "marked_at",
    "read_scope",
    "source_bytes",
    "source_pointer",
    "user_notes",
}


class DuplicateKeyError(ValueError):
    pass


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite number {token!r}")
        ),
    )


def _assignment(tree: ast.Module, name: str) -> Any:
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                value = node.value
                if value is None:
                    break
                if (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Name)
                    and value.func.id in {"frozenset", "set"}
                    and len(value.args) == 1
                    and not value.keywords
                ):
                    return set(ast.literal_eval(value.args[0]))
                return ast.literal_eval(value)
    raise KeyError(name)


def _runtime_checks(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return [f"{RUNTIME_REL}: cannot parse runtime: {exc}"]

    for name, expected in (
        ("SCHEMA_VERSION", "evidence-row/1.0"),
        ("SURFACE", "phase_e_claim_verification"),
        ("DEFAULT_PAGE_SIZE", 25),
        ("MAX_PAGE_SIZE", 25),
        ("LEGACY_UNAVAILABLE_LABEL", "LEGACY — EVIDENCE ROWS UNAVAILABLE"),
    ):
        try:
            actual = _assignment(tree, name)
        except (KeyError, ValueError) as exc:
            errors.append(f"{RUNTIME_REL}: missing literal {name}: {exc}")
        else:
            if actual != expected:
                errors.append(f"{RUNTIME_REL}: {name}={actual!r}, expected {expected!r}")

    if "--allow-legacy-absence" not in text:
        errors.append(
            f"{RUNTIME_REL}: missing explicit --allow-legacy-absence compatibility gate"
        )

    try:
        states = set(_assignment(tree, "EXCERPT_STATES"))
    except (KeyError, ValueError) as exc:
        errors.append(f"{RUNTIME_REL}: cannot read EXCERPT_STATES: {exc}")
    else:
        if states != EXPECTED_STATES:
            errors.append(
                f"{RUNTIME_REL}: excerpt-state vocabulary drift: "
                f"missing={sorted(EXPECTED_STATES - states)}, extra={sorted(states - EXPECTED_STATES)}"
            )

    try:
        labels = _assignment(tree, "STATE_LABELS")
    except (KeyError, ValueError) as exc:
        errors.append(f"{RUNTIME_REL}: cannot read STATE_LABELS: {exc}")
    else:
        if labels != EXPECTED_LABELS:
            errors.append(f"{RUNTIME_REL}: canonical rendering vocabulary drift")

    for node in ast.walk(tree):
        imported: list[str] = []
        if isinstance(node, ast.Import):
            imported = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported = [node.module]
        for module in imported:
            if (
                module.split(".", 1)[0] in FORBIDDEN_IMPORT_ROOTS
                or any(
                    module == prefix or module.startswith(prefix + ".")
                    for prefix in FORBIDDEN_IMPORT_PREFIXES
                )
            ):
                errors.append(f"{RUNTIME_REL}:{node.lineno}: forbidden retrieval/model/system import {module!r}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "add_argument" and node.args:
                try:
                    option = ast.literal_eval(node.args[0])
                except (ValueError, TypeError):
                    option = None
                if option == "--all":
                    errors.append(f"{RUNTIME_REL}:{node.lineno}: resource-unbounded --all option is forbidden")

    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    pending = [name for name in sorted(RENDER_ROOTS) if name in functions]
    reachable: set[str] = set()
    while pending:
        name = pending.pop()
        if name in reachable:
            continue
        reachable.add(name)
        for node in ast.walk(functions[name]):
            if not isinstance(node, ast.Call):
                continue
            called_name: str | None
            if isinstance(node.func, ast.Name):
                called_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                called_name = node.func.attr
            else:
                called_name = None
            if called_name in functions and called_name not in reachable:
                pending.append(called_name)
            if called_name in FORBIDDEN_RENDER_CALLS:
                errors.append(
                    f"{RUNTIME_REL}:{node.lineno}: renderer-reachable ambient I/O/process call "
                    f"{called_name!r} is forbidden"
                )
    return errors


def run_checks(root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    schema_path = root / SCHEMA_REL
    runtime_path = root / RUNTIME_REL
    try:
        schema = _load_json(schema_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{SCHEMA_REL}: cannot load strict JSON: {exc}")
        schema = None

    if isinstance(schema, dict):
        if schema.get("additionalProperties") is not False:
            errors.append(f"{SCHEMA_REL}: root must remain closed")
        properties = schema.get("properties", {})
        if properties.get("schema_version", {}).get("const") != "evidence-row/1.0":
            errors.append(f"{SCHEMA_REL}: schema_version const drift")
        if properties.get("surface", {}).get("const") != "phase_e_claim_verification":
            errors.append(f"{SCHEMA_REL}: V1 surface const drift")
        states = set(
            properties.get("excerpt", {}).get("properties", {}).get("state", {}).get("enum", [])
        )
        if states != EXPECTED_STATES:
            errors.append(
                f"{SCHEMA_REL}: excerpt-state vocabulary drift: "
                f"missing={sorted(EXPECTED_STATES - states)}, extra={sorted(states - EXPECTED_STATES)}"
            )
        source_fields = set(properties.get("source", {}).get("properties", {}))
        forbidden = source_fields & FORBIDDEN_SCHEMA_FIELDS
        if forbidden:
            errors.append(f"{SCHEMA_REL}: forbidden source/private/read fields: {sorted(forbidden)}")
        schema_text = json.dumps(schema, ensure_ascii=False, sort_keys=True)
        leaked = sorted(field for field in FORBIDDEN_SCHEMA_FIELDS if f'"{field}"' in schema_text)
        if leaked:
            errors.append(f"{SCHEMA_REL}: forbidden persisted fields anywhere in schema: {leaked}")

    errors.extend(_runtime_checks(runtime_path))

    for rel, required in REQUIRED_POINTERS.items():
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{rel}: cannot read: {exc}")
            continue
        for token in required:
            if token not in text:
                errors.append(f"{rel}: missing #656 pointer/contract token {token!r}")

    for rel, required in CITED_VERSION_RULES.items():
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{rel}: cannot read: {exc}")
            continue
        for token in required:
            if token not in text:
                errors.append(f"{rel}: missing #1006 cited-version rule {token!r}")
        for token in RETIRED_ACCESS_RULES.get(rel, ()):
            if token in text:
                errors.append(f"{rel}: retired paywall-only access rule returned {token!r}")

    adoption_tokens = (SCHEMA_REL, RUNTIME_REL, "evidence-row/1.0")
    for rel in OUT_OF_SCOPE:
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{rel}: cannot read out-of-scope boundary file: {exc}")
            continue
        found = [token for token in adoption_tokens if token in text]
        if found:
            errors.append(
                f"{rel}: opt-in claim-audit/formatter V1 boundary crossed by {found!r}"
            )
    return errors


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        errors = run_checks(args.root.resolve())
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("PASS: #656 shared evidence-row integration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
