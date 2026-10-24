#!/usr/bin/env python3
"""Mutation tests for the #656 cross-file integration guard."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts import check_evidence_row_integration as guard


REPO_ROOT = Path(__file__).resolve().parents[1]
COPIED = tuple(
    dict.fromkeys(
        (
            guard.SCHEMA_REL,
            guard.RUNTIME_REL,
            *guard.REQUIRED_POINTERS,
            *guard.OUT_OF_SCOPE,
        )
    )
)


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for rel in COPIED:
        source = REPO_ROOT / rel
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return root


def _replace(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _replace_all(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


def test_clean_repository_passes() -> None:
    assert guard.run_checks(REPO_ROOT) == []


@pytest.mark.parametrize("rel", tuple(guard.REQUIRED_POINTERS))
def test_each_consumer_contract_pointer_is_required(tmp_path: Path, rel: str) -> None:
    root = _tree(tmp_path)
    token = guard.REQUIRED_POINTERS[rel][0]
    _replace_all(root, rel, token, "removed-656-pointer")
    errors = guard.run_checks(root)
    assert any(rel in error and "missing #656 pointer/contract token" in error for error in errors)


@pytest.mark.parametrize("rel", tuple(guard.REQUIRED_POINTERS))
def test_each_surface_requires_explicit_legacy_compatibility_gate(
    tmp_path: Path, rel: str
) -> None:
    root = _tree(tmp_path)
    _replace_all(root, rel, "--allow-legacy-absence", "removed-explicit-legacy-gate")
    errors = guard.run_checks(root)
    assert any(
        rel in error
        and "missing #656 pointer/contract token '--allow-legacy-absence'" in error
        for error in errors
    )


@pytest.mark.parametrize(
    ("rel", "token"),
    [
        (rel, token)
        for rel, tokens in guard.CITED_VERSION_RULES.items()
        for token in tokens
    ],
)
def test_each_cited_version_rule_is_required(
    tmp_path: Path, rel: str, token: str
) -> None:
    root = _tree(tmp_path)
    _replace_all(root, rel, token, "removed-1006-rule")
    errors = guard.run_checks(root)
    assert any(
        rel in error and f"missing #1006 cited-version rule {token!r}" in error
        for error in errors
    )


@pytest.mark.parametrize("rel", tuple(guard.RETIRED_ACCESS_RULES))
def test_retired_paywall_only_rule_cannot_return(tmp_path: Path, rel: str) -> None:
    root = _tree(tmp_path)
    retired = guard.RETIRED_ACCESS_RULES[rel][0]
    path = root / rel
    path.write_text(
        path.read_text(encoding="utf-8") + f"\n- {retired}\n", encoding="utf-8"
    )
    errors = guard.run_checks(root)
    assert any(
        rel in error and "retired paywall-only access rule returned" in error
        for error in errors
    )


@pytest.mark.parametrize("rel", tuple(guard.RETIRED_ACCESS_RULES))
def test_reordered_multi_source_verdict_order_is_rejected(
    tmp_path: Path, rel: str
) -> None:
    root = _tree(tmp_path)
    _replace_all(
        root,
        rel,
        "MAJOR_DISTORTION, UNVERIFIABLE, MINOR_DISTORTION, UNVERIFIABLE_ACCESS, VERIFIED",
        "MAJOR_DISTORTION, UNVERIFIABLE, UNVERIFIABLE_ACCESS, MINOR_DISTORTION, VERIFIED",
    )
    errors = guard.run_checks(root)
    assert any(rel in error and "missing #1006 cited-version rule" in error for error in errors)


@pytest.mark.parametrize("rel", tuple(guard.RETIRED_ACCESS_RULES))
def test_access_failure_cannot_become_a_blocking_verdict(
    tmp_path: Path, rel: str
) -> None:
    root = _tree(tmp_path)
    _replace_all(
        root,
        rel,
        "record UNVERIFIABLE_ACCESS for that source",
        "record UNVERIFIABLE for that source",
    )
    errors = guard.run_checks(root)
    assert any(rel in error and "missing #1006 cited-version rule" in error for error in errors)


def test_schema_state_synonym_is_rejected(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.SCHEMA_REL
    schema = json.loads(path.read_text(encoding="utf-8"))
    states = schema["properties"]["excerpt"]["properties"]["state"]["enum"]
    states[states.index("verified_exact_match")] = "verified_quote"
    path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert any("excerpt-state vocabulary drift" in error for error in guard.run_checks(root))


def test_runtime_rendering_label_drift_is_rejected(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _replace(root, guard.RUNTIME_REL, '"SOURCE NOT HELD"', '"SOURCE MISSING"')
    assert any("rendering vocabulary drift" in error for error in guard.run_checks(root))


@pytest.mark.parametrize(
    "statement",
    [
        "import socket\n",
        "import requests\n",
        "import subprocess\n",
        "import urllib.request\n",
        "from urllib.request import urlopen\n",
    ],
)
def test_runtime_retrieval_or_process_import_is_rejected(
    tmp_path: Path, statement: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME_REL
    path.write_text(statement + path.read_text(encoding="utf-8"), encoding="utf-8")
    errors = guard.run_checks(root)
    assert any("forbidden retrieval/model/system import" in error for error in errors)


def test_unbounded_all_cli_option_is_rejected(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME_REL
    text = path.read_text(encoding="utf-8")
    anchor = "def _parser() -> argparse.ArgumentParser:\n"
    injected = (
        "def _forbidden_all(parser: argparse.ArgumentParser) -> None:\n"
        "    parser.add_argument(\"--all\", action=\"store_true\")\n\n\n"
    )
    assert anchor in text
    path.write_text(text.replace(anchor, injected + anchor, 1), encoding="utf-8")
    assert any("--all option is forbidden" in error for error in guard.run_checks(root))


def test_runtime_requires_explicit_legacy_compatibility_option(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _replace_all(
        root,
        guard.RUNTIME_REL,
        "--allow-legacy-absence",
        "--removed-legacy-compatibility",
    )
    assert any(
        "missing explicit --allow-legacy-absence compatibility gate" in error
        for error in guard.run_checks(root)
    )


def test_renderer_reachable_ambient_file_read_is_rejected(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME_REL
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    start = next(index for index, line in enumerate(lines) if line.startswith("def render_markdown("))
    body = next(index for index in range(start + 1, len(lines)) if lines[index].startswith("    \"\"\""))
    lines.insert(body, '    Path("ambient-source.txt").read_text(encoding="utf-8")\n')
    path.write_text("".join(lines), encoding="utf-8")
    errors = guard.run_checks(root)
    assert any("renderer-reachable ambient I/O/process call" in error for error in errors)


@pytest.mark.parametrize("field", ["full_text", "human_read_source", "read_scope", "source_pointer"])
def test_private_read_or_source_body_field_is_rejected(
    tmp_path: Path, field: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.SCHEMA_REL
    schema = json.loads(path.read_text(encoding="utf-8"))
    schema["properties"]["source"]["properties"][field] = {"type": "string"}
    path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert any("forbidden source/private/read fields" in error for error in guard.run_checks(root))


@pytest.mark.parametrize("rel", guard.OUT_OF_SCOPE)
def test_opt_in_claim_audit_and_formatter_cannot_adopt_v1_pointer(
    tmp_path: Path, rel: str
) -> None:
    root = _tree(tmp_path)
    path = root / rel
    path.write_text(
        path.read_text(encoding="utf-8") + f"\n{guard.SCHEMA_REL}\n",
        encoding="utf-8",
    )
    errors = guard.run_checks(root)
    assert any(rel in error and "boundary crossed" in error for error in errors)


def test_duplicate_schema_key_fails_closed(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.SCHEMA_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"title":', '"title": "shadow",\n  "title":', 1), encoding="utf-8")
    assert any("duplicate JSON key" in error for error in guard.run_checks(root))
