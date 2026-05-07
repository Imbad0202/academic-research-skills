"""Tests for ARS v3.7.1 trust-chain frontmatter lint (Step 1 of v3.7.1 impl).

Spec: docs/design/2026-04-30-ars-v3.6.8-trust-provenance-and-drift-transparency-spec.md
      § 3.1 D1, § Step 1

Each spec firm rule gets at least one positive (valid combination passes)
and one negative (deliberately-violated combination fails) test. JSON
Schema validation runs alongside the lint to confirm defense-in-depth:
schema-side `allOf` branches and lint-side rule checks both reject.

Per the user's iron law: positive + negative tests for every rule.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from scripts.check_v3_6_8_frontmatter_trust_schema import (
    check_entry,
    check_payload,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
ENTRY_SCHEMA_PATH = REPO_ROOT / "shared" / "contracts" / "passport" / "literature_corpus_entry.schema.json"


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    with ENTRY_SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def validator(schema: dict[str, Any]) -> Draft202012Validator:
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _minimal_entry(**overrides: Any) -> dict[str, Any]:
    """Smallest valid v3.6.4 entry; tests overlay trust fields on top."""
    base = {
        "citation_key": "smith2024",
        "title": "Sample title",
        "authors": [{"family": "Smith", "given": "Alex"}],
        "year": 2024,
        "source_pointer": "file:///fixture/smith2024.pdf",
    }
    base.update(overrides)
    return base


# ---------- Schema self-consistency ----------


def test_schema_is_valid_draft_2020_12(schema: dict[str, Any]) -> None:
    """The schema itself must be a valid JSON Schema 2020-12 document."""
    Draft202012Validator.check_schema(schema)


def test_schema_includes_seven_v3_7_1_trust_fields(schema: dict[str, Any]) -> None:
    """Spec § Step 1 requires exactly seven entry-stored trust fields."""
    expected = {
        "source_acquired",
        "source_acquisition_date",
        "source_acquisition_path",
        "source_verified_against_original",
        "source_verification_method",
        "description_source",
        "description_last_audit",
    }
    assert expected.issubset(schema["properties"].keys()), (
        f"Missing trust fields: {expected - schema['properties'].keys()}"
    )
    # Must NOT add human_read_source / human_read_at to entry schema
    # (per spec §3.1 firm rule #3 + §3.6 firm rule #1).
    assert "human_read_source" not in schema["properties"]
    assert "human_read_at" not in schema["properties"]


def test_schema_keeps_additional_properties_false(schema: dict[str, Any]) -> None:
    assert schema.get("additionalProperties") is False, (
        "additionalProperties: false is the contract that prevents adapters / "
        "consumer agents from sneaking human_read_* fields onto entries."
    )


# ---------- Rule #1 — verified=true preconditions ----------


def test_rule1_verified_true_with_acquired_true_and_valid_method_passes(validator) -> None:
    entry = _minimal_entry(
        source_acquired=True,
        source_verified_against_original=True,
        source_verification_method="codex_audit",
    )
    assert list(validator.iter_errors(entry)) == []
    assert check_entry(entry, "smith2024") == []


def test_rule1_verified_true_without_acquired_fails(validator) -> None:
    entry = _minimal_entry(
        source_acquired=False,
        source_verified_against_original=True,
        source_verification_method="codex_audit",
    )
    # Schema-side: rule #1 allOf branch fires
    assert any(validator.iter_errors(entry))
    # Lint-side: friendly diagnostic
    errors = check_entry(entry, "smith2024")
    assert any("Rule #1 violated" in e and "source_acquired=true" in e for e in errors)


def test_rule1_verified_true_with_method_none_fails(validator) -> None:
    """Round-2 R2-007 amend: 'none' is enumerated but FORBIDDEN with verified=true."""
    entry = _minimal_entry(
        source_acquired=True,
        source_verified_against_original=True,
        source_verification_method="none",
    )
    assert any(validator.iter_errors(entry))
    errors = check_entry(entry, "smith2024")
    assert any("Rule #1" in e and "'none'" in e for e in errors)


def test_rule1_verified_true_missing_method_fails(validator) -> None:
    entry = _minimal_entry(
        source_acquired=True,
        source_verified_against_original=True,
        # source_verification_method intentionally omitted
    )
    # Schema fires because allOf branch sets `required: [source_acquired, source_verification_method]`
    assert any(validator.iter_errors(entry))
    errors = check_entry(entry, "smith2024")
    assert any("Rule #1" in e and "source_verification_method" in e for e in errors)


def test_rule1_verified_false_does_not_constrain_method(validator) -> None:
    """When verified=false, method='none' is fine.

    Rule #2 still applies (source_acquired=false REQUIRES description_last_audit
    to be present + null/'none'); we satisfy it here so the test isolates Rule #1.
    """
    entry = _minimal_entry(
        source_acquired=False,
        source_verified_against_original=False,
        source_verification_method="none",
        description_last_audit="none",  # Rule #2 strict-REQUIRES presence
    )
    assert list(validator.iter_errors(entry)) == []
    assert check_entry(entry, "smith2024") == []


# ---------- Rule #2 — source_acquired=false → description_last_audit ∈ {null, 'none'} ----------


def test_rule2_acquired_false_with_audit_none_passes(validator) -> None:
    entry = _minimal_entry(
        source_acquired=False,
        description_last_audit="none",
    )
    assert list(validator.iter_errors(entry)) == []
    assert check_entry(entry, "smith2024") == []


def test_rule2_acquired_false_with_audit_null_fails(validator) -> None:
    """Round-6 codex P2 closure: spec §3.1 firm rule #2 says REQUIRES
    description_last_audit: 'none' (literal sentinel). Spec yaml at line 111
    lists the value vocabulary as `<round_id> | none` with no null alternative.
    null in the rule-#2 case must be rejected by both schema and lint.
    """
    entry = _minimal_entry(
        source_acquired=False,
        description_last_audit=None,
    )
    schema_errs = list(validator.iter_errors(entry))
    assert schema_errs, (
        "Schema must reject source_acquired=false + description_last_audit=null "
        "(round-6 closure: only literal 'none' is allowed)"
    )
    lint_errs = check_entry(entry, "smith2024")
    assert any(
        "Rule #2" in e and "literal sentinel string" in e for e in lint_errs
    ), f"Lint must surface literal-only enforcement; got: {lint_errs}"


def test_rule2_acquired_false_with_real_audit_round_fails(validator) -> None:
    entry = _minimal_entry(
        source_acquired=False,
        description_last_audit="round-3-codex",
    )
    assert any(validator.iter_errors(entry))
    errors = check_entry(entry, "smith2024")
    assert any("Rule #2" in e and "round-3-codex" in e for e in errors)


def test_rule2_acquired_false_with_missing_audit_field_fails(validator) -> None:
    """Round-1 codex P2 closure: REQUIRES is strict — the field MUST be present.

    Schema-side `then.required` enforces this; lint-side mirrors with a
    friendly 'field is missing' diagnostic.
    """
    entry = _minimal_entry(source_acquired=False)
    # description_last_audit deliberately omitted
    assert "description_last_audit" not in entry
    schema_errs = list(validator.iter_errors(entry))
    assert schema_errs, (
        "Schema must reject source_acquired=false with missing "
        "description_last_audit (Rule #2 REQUIRES is strict)"
    )
    lint_errs = check_entry(entry, "smith2024")
    assert any(
        "Rule #2" in e and "is missing" in e for e in lint_errs
    ), f"Lint must surface missing-field violation; got: {lint_errs}"


def test_description_source_accepts_arbitrary_bibliography_revision(validator) -> None:
    """Round-1 codex P2 closure: spec § 3.1 yaml uses `bibliography_v<n>` as a
    template (any non-negative integer n), not a hard-coded enum of v1..v3.
    A revision number above the initial release range must validate.
    """
    for v in ["bibliography_v0", "bibliography_v4", "bibliography_v17", "bibliography_v999"]:
        entry = _minimal_entry(description_source=v)
        assert list(validator.iter_errors(entry)) == [], (
            f"description_source={v!r} should validate against the "
            f"`bibliography_v<n>` template"
        )


def test_description_source_still_accepts_canonical_values(validator) -> None:
    """Sanity: the original_pdf / secondary_summary canonical values keep working."""
    for v in ["original_pdf", "secondary_summary", "bibliography_v1"]:
        entry = _minimal_entry(description_source=v)
        assert list(validator.iter_errors(entry)) == [], (
            f"description_source={v!r} (canonical) must validate"
        )


def test_description_source_rejects_unrelated_strings(validator) -> None:
    """The pattern is anchored — typos and unrelated strings still fail."""
    for v in ["bib_v1", "bibliography_vX", "bibliography", "other"]:
        entry = _minimal_entry(description_source=v)
        assert list(validator.iter_errors(entry)), (
            f"description_source={v!r} should be rejected by the pattern"
        )


def test_rule2_acquired_true_with_real_audit_round_passes(validator) -> None:
    """When source_acquired=true, any audit round id is fine."""
    entry = _minimal_entry(
        source_acquired=True,
        source_verified_against_original=False,  # Rule #1 allows this
        source_verification_method="none",
        description_last_audit="round-3-codex",
    )
    assert list(validator.iter_errors(entry)) == []
    assert check_entry(entry, "smith2024") == []


# ---------- Rule #3 — no literal human_read_* on entry ----------


def test_rule3_literal_human_read_source_rejected_by_schema(validator) -> None:
    """additionalProperties: false catches this at the schema layer."""
    entry = _minimal_entry(human_read_source=True)
    errs = list(validator.iter_errors(entry))
    assert errs, "schema must reject literal human_read_source via additionalProperties: false"
    assert any("human_read_source" in str(e.message) for e in errs)


def test_rule3_literal_human_read_source_rejected_by_lint() -> None:
    """Lint emits a spec-cited friendly message in addition to schema rejection."""
    entry = _minimal_entry(human_read_source=True)
    errors = check_entry(entry, "smith2024")
    assert any(
        "Rule #3" in e and "human_read_source" in e and "§3.6 peer file" in e
        for e in errors
    )


def test_rule3_literal_human_read_at_rejected(validator) -> None:
    """The 'derived at read-time' contract covers human_read_at as well."""
    entry = _minimal_entry(human_read_at="2026-05-07T00:00:00Z")
    assert any(validator.iter_errors(entry))
    errors = check_entry(entry, "smith2024")
    assert any("Rule #3" in e and "human_read_at" in e for e in errors)


# ---------- Payload-shape coverage ----------


def test_check_payload_handles_passport_shape() -> None:
    payload = {
        "literature_corpus": [
            _minimal_entry(citation_key="ok2024"),
            _minimal_entry(citation_key="bad2024", human_read_source=True),
        ]
    }
    failures = check_payload(payload, "<test>")
    assert any("bad2024" in f for f in failures)
    assert all("ok2024" not in f or "Rule" not in f for f in failures)


def test_check_payload_handles_bare_entry() -> None:
    entry = _minimal_entry(human_read_source=True)
    failures = check_payload(entry, "<test>")
    assert any("Rule #3" in f for f in failures)


def test_check_payload_handles_bare_entry_list() -> None:
    payload = [_minimal_entry(citation_key="x", human_read_source=True)]
    failures = check_payload(payload, "<test>")
    assert any("Rule #3" in f for f in failures)


def test_check_payload_clean_passport_returns_empty() -> None:
    payload = {"literature_corpus": [_minimal_entry()]}
    assert check_payload(payload, "<test>") == []


# ---------- Existing fixtures stay green ----------


def test_existing_v3_6_4_fixtures_still_pass() -> None:
    """v3.7.1 schema must be backward-compatible with v3.6.4 adapter fixtures
    (they don't carry trust fields; absence is allowed)."""
    import yaml
    examples_root = REPO_ROOT / "scripts" / "adapters" / "examples"
    fixtures = list(examples_root.rglob("expected_passport.yaml"))
    assert fixtures, "fixture set unexpectedly empty"
    for path in fixtures:
        with path.open(encoding="utf-8") as f:
            payload = yaml.safe_load(f)
        failures = check_payload(payload, str(path.relative_to(REPO_ROOT)))
        assert failures == [], (
            f"v3.6.4 fixture {path.relative_to(REPO_ROOT)} must remain valid "
            f"under v3.7.1 schema; got: {failures}"
        )
