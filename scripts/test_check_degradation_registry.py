#!/usr/bin/env python3
"""Mutation tests for scripts/check_degradation_registry.py (#511 Part A).

One failing witness per invariant branch (repo lint-test convention): each test
mutates a copy of the shipped registry and asserts the exact invariant fires.
The shipped registry itself must pass (the zero-mutation baseline).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_degradation_registry import DEFAULT_REGISTRY, run  # noqa: E402


def _shipped() -> dict:
    return json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8"))


def _write(tmp_path: Path, data) -> Path:
    p = tmp_path / "registry.json"
    p.write_text(
        data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
    return p


def _errors_for(tmp_path: Path, data) -> list[str]:
    return run(_write(tmp_path, data))


# ---------- baseline ----------


def test_shipped_registry_passes():
    assert run(DEFAULT_REGISTRY) == []


# ---------- D1 shape / fail-closed ----------


def test_missing_registry_file_fails(tmp_path):
    errors = run(tmp_path / "nope.json")
    assert any("D1" in e and "missing" in e for e in errors)


def test_unparseable_json_fails_closed(tmp_path):
    errors = _errors_for(tmp_path, "{not json")
    assert any("D1" in e and "parseable" in e for e in errors)


def test_non_object_top_level_fails(tmp_path):
    errors = _errors_for(tmp_path, "[]")
    assert any("top level" in e for e in errors)


def test_missing_registry_version_fails(tmp_path):
    data = _shipped()
    del data["registry_version"]
    assert any("registry_version" in e for e in _errors_for(tmp_path, data))


def test_empty_mechanisms_fails(tmp_path):
    data = _shipped()
    data["mechanisms"] = []
    assert any("non-empty list" in e for e in _errors_for(tmp_path, data))


@pytest.mark.parametrize("field", [
    "mechanism", "failure_class", "degraded_state", "diagnostic_marker",
    "downstream_consumer", "terminal_policy_effect", "authority", "pinned_by",
])
def test_missing_required_field_fails(tmp_path, field):
    data = _shipped()
    del data["mechanisms"][0][field]
    errors = _errors_for(tmp_path, data)
    assert any("D1" in e and repr(field) in e for e in errors), errors


def test_blank_string_field_fails(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["failure_class"] = "   "
    errors = _errors_for(tmp_path, data)
    assert any("failure_class" in e and "non-empty" in e for e in errors)


def test_empty_authority_list_fails(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["authority"] = []
    errors = _errors_for(tmp_path, data)
    assert any("authority must be a non-empty list" in e for e in errors)


# ---------- D2 uniqueness ----------


def test_duplicate_mechanism_id_fails(tmp_path):
    data = _shipped()
    data["mechanisms"].append(dict(data["mechanisms"][0]))
    errors = _errors_for(tmp_path, data)
    assert any("D2" in e and "duplicate" in e for e in errors)


# ---------- D3 authority anchors ----------


def test_nonexistent_authority_file_fails(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["authority"][0]["file"] = "scripts/does_not_exist.py"
    errors = _errors_for(tmp_path, data)
    assert any("D3" in e and "does not exist" in e for e in errors)


def test_line_number_reference_forbidden(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["authority"][0]["file"] = (
        "scripts/citation_verification_summary.py:62")
    errors = _errors_for(tmp_path, data)
    assert any("line-number references are forbidden" in e for e in errors)


def test_absent_anchor_fails(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["authority"][0]["anchor"] = (
        "this exact sentence appears nowhere in the cited authority file")
    errors = _errors_for(tmp_path, data)
    assert any("D3" in e and "not found verbatim" in e for e in errors)


def test_too_short_anchor_fails(tmp_path):
    data = _shipped()
    # Short AND present in the file — must still fail on length alone.
    data["mechanisms"][0]["authority"][0]["anchor"] = "return"
    errors = _errors_for(tmp_path, data)
    assert any("D3" in e and ">= 16" in e for e in errors)


# ---------- D4 pinned_by ----------


def test_nonexistent_pinned_file_fails(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["pinned_by"] = ["scripts/test_ghost.py"]
    errors = _errors_for(tmp_path, data)
    assert any("D4" in e and "does not exist" in e for e in errors)


def test_missing_pinned_function_fails(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["pinned_by"] = [
        "scripts/test_verification_gate.py::test_that_was_never_written"]
    errors = _errors_for(tmp_path, data)
    assert any("D4" in e and "not defined" in e for e in errors)


def test_function_form_on_non_py_fails(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["pinned_by"] = [
        "shared/contracts/degradation_registry.json::test_x"]
    errors = _errors_for(tmp_path, data)
    assert any("requires a .py path" in e for e in errors)


def test_existing_pinned_function_passes(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["pinned_by"] = [
        "scripts/test_verification_gate.py::test_all_unreachable_is_unresolvable"]
    assert _errors_for(tmp_path, data) == []


def test_traversal_authority_ref_fails(tmp_path):
    """Containment hardening: a ref resolving outside the repo is refused
    before any read or existence probe (#511 security-review note)."""
    data = _shipped()
    data["mechanisms"][0]["authority"][0]["file"] = "../outside.md"
    errors = _errors_for(tmp_path, data)
    assert any("escapes the repo root" in e for e in errors)


def test_traversal_pinned_ref_fails(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["pinned_by"] = ["../../outside_test.py"]
    errors = _errors_for(tmp_path, data)
    assert any("escapes the repo root" in e for e in errors)


# ---------- D5 inventory lock + duplicate keys ----------


def test_deleted_row_fails_inventory_lock(tmp_path):
    """D5: silently deleting a mechanism row must fail until the lint's
    pinned inventory is updated in the same commit (lock semantics)."""
    data = _shipped()
    data["mechanisms"] = [
        r for r in data["mechanisms"] if r["mechanism"] != "vlm_unavailable"]
    errors = _errors_for(tmp_path, data)
    assert any("D5" in e and "missing from the registry" in e for e in errors)


def test_renamed_row_fails_both_directions(tmp_path):
    data = _shipped()
    data["mechanisms"][0]["mechanism"] = "citation_resolver_outage_v2"
    errors = _errors_for(tmp_path, data)
    assert any("D5" in e and "missing" in e for e in errors)
    assert any("D5" in e and "not in the pinned inventory" in e for e in errors)


def test_unpinned_new_row_fails(tmp_path):
    data = _shipped()
    extra = dict(data["mechanisms"][0])
    extra["mechanism"] = "brand_new_mechanism"
    data["mechanisms"].append(extra)
    errors = _errors_for(tmp_path, data)
    assert any("D5" in e and "not in the pinned inventory" in e for e in errors)


def test_duplicate_json_key_fails_closed(tmp_path):
    """Plain json.loads is last-value-wins on duplicate keys — two consumers
    could read different rows from one file. Reject at parse time."""
    dup = '{"registry_version": "1.0.0", "mechanisms": [], "mechanisms": []}'
    errors = _errors_for(tmp_path, dup)
    assert any("D1" in e and "duplicate JSON object key" in e for e in errors)
