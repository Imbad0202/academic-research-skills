from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts import build_review_pathway_rule_trace as runtime
from scripts import check_review_pathway_output as output_lint
from scripts.resolve_human_subjects_authority import (
    ContractError,
    digest,
    resolve,
)


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_FIXTURES = ROOT / "scripts" / "fixtures" / "human_subjects_authority"
TRACE_FIXTURES = ROOT / "scripts" / "fixtures" / "review_pathway_rule_trace"
REGISTRY_PATH = ROOT / "shared" / "human_subjects_authority_registry.json"
REQUEST_SCHEMA_PATH = (
    ROOT
    / "shared"
    / "contracts"
    / "human_subjects"
    / "review_pathway_trace_request.schema.json"
)
TRACE_SCHEMA_PATH = (
    ROOT
    / "shared"
    / "contracts"
    / "human_subjects"
    / "review_pathway_rule_trace.schema.json"
)
LINT_FIXTURE_PATH = TRACE_FIXTURES / "lint-near-misses.json"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _registry() -> dict[str, Any]:
    return _json(REGISTRY_PATH)


def _context(name: str) -> dict[str, Any]:
    return _json(AUTHORITY_FIXTURES / name)


def _fixture_request(name: str) -> dict[str, Any]:
    return _json(TRACE_FIXTURES / name)


def _authority(
    context_name: str = "us-gdpr-two-axis.json",
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    context = _context(context_name)
    registry = _registry()
    return context, registry, resolve(context, registry)


def _profile_ref(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "axis": row["axis"],
        "profile_id": row["profile_id"],
        "profile_version": row["profile_version"],
        "profile_digest": row["profile_digest"],
    }


def _request_for(
    resolved: dict[str, Any],
    *,
    split_requirements: bool = False,
    name_by_profile: dict[str, str] | None = None,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    eligible_by_profile: dict[tuple[str, str, str, str], list[str]] = {}
    for row in resolved["requirement_results"]:
        if (
            row["authority_kind"] == "profile"
            and "pathway_trace" in row["consumer_scopes"]
        ):
            key = (
                row["axis"],
                row["authority_id"],
                row["authority_version"],
                row["authority_digest"],
            )
            eligible_by_profile.setdefault(key, []).append(row["requirement_id"])
    profile_by_key = {
        (
            row["axis"],
            row["profile_id"],
            row["profile_version"],
            row["profile_digest"],
        ): row
        for row in resolved["selected_profiles"]
    }
    for profile_index, key in enumerate(sorted(eligible_by_profile), start=1):
        requirements = sorted(eligible_by_profile[key])
        groups = [[requirement_id] for requirement_id in requirements] if split_requirements else [requirements]
        for group_index, group in enumerate(groups, start=1):
            profile = profile_by_key[key]
            candidates.append(
                {
                    "candidate_id": f"candidate.route_{profile_index}_{group_index}",
                    "profile_ref": _profile_ref(profile),
                    "candidate_pathway_name": (
                        name_by_profile or {}
                    ).get(profile["profile_id"], f"Candidate Route {profile_index}-{group_index}"),
                    "candidate_name_source": {
                        "source_kind": "author_declared_question",
                        "source_locator": f"Author question {profile_index}-{group_index}",
                        "source_url": None,
                        "effective_date": None,
                    },
                    "predicate_requirement_ids": group,
                }
            )
    return {
        "schema_version": runtime.REQUEST_VERSION,
        "trace_request_id": "test.pathway-trace",
        "context_pointer": copy.deepcopy(resolved["context_pointer"]),
        "registry_pointer": copy.deepcopy(resolved["registry_pointer"]),
        "resolved_digest": resolved["resolved_digest"],
        "ordering_semantics": runtime.ORDERING,
        "candidate_pathways": candidates,
    }


def _build_fixture(
    context_name: str,
    request_name: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    context, registry, resolved = _authority(context_name)
    request = _fixture_request(request_name)
    trace = runtime.build_review_pathway_rule_trace(request, context, registry, resolved)
    return request, context, registry, resolved, trace


def _schema_errors(schema: dict[str, Any], value: dict[str, Any]) -> list[Any]:
    return list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)
    )


def test_schemas_pass_draft_2020_12_metaschema() -> None:
    for path in (REQUEST_SCHEMA_PATH, TRACE_SCHEMA_PATH):
        Draft202012Validator.check_schema(_json(path))


@pytest.mark.parametrize(
    ("context_name", "request_name"),
    [
        ("us-gdpr-two-axis.json", "us-candidates-request.json"),
        ("tw-gdpr-two-axis.json", "tw-candidates-request.json"),
        ("no-profile.json", "no-profile-request.json"),
    ],
)
def test_positive_fixtures_validate_schema_replay_and_lint(
    context_name: str,
    request_name: str,
) -> None:
    request, context, registry, resolved, trace = _build_fixture(
        context_name, request_name
    )
    assert _schema_errors(_json(REQUEST_SCHEMA_PATH), request) == []
    assert _schema_errors(_json(TRACE_SCHEMA_PATH), trace) == []
    runtime.validate_review_pathway_rule_trace(
        trace, request, context, registry, resolved
    )
    rendered = runtime.render_review_pathway_rule_trace(trace)
    assert output_lint.lint_artifacts(trace, rendered) == []


def test_request_and_trace_schema_negative_payloads() -> None:
    request, _context_value, _registry_value, _resolved, trace = _build_fixture(
        "us-gdpr-two-axis.json", "us-candidates-request.json"
    )
    request_schema = _json(REQUEST_SCHEMA_PATH)
    trace_schema = _json(TRACE_SCHEMA_PATH)

    bad_request = copy.deepcopy(request)
    bad_request["extra"] = True
    assert _schema_errors(request_schema, bad_request)
    bad_request = copy.deepcopy(request)
    bad_request["candidate_pathways"][0]["profile_ref"]["axis"] = "unsupported_axis"
    assert _schema_errors(request_schema, bad_request)
    bad_request = copy.deepcopy(request)
    bad_request["candidate_pathways"][0]["predicate_requirement_ids"] = []
    assert _schema_errors(request_schema, bad_request)

    bad_trace = copy.deepcopy(trace)
    bad_trace["result"] = "pathway selected"
    assert _schema_errors(trace_schema, bad_trace)
    bad_trace = copy.deepcopy(trace)
    bad_trace["extra"] = True
    assert _schema_errors(trace_schema, bad_trace)
    bad_trace = copy.deepcopy(trace)
    bad_trace["halt_reasons"] = [
        {
            "code": "JURISDICTION_UNRESOLVED",
            "axis": "review_ethics",
            "authority_id": None,
            "requirement_id": None,
        }
    ]
    assert _schema_errors(trace_schema, bad_trace)


def test_every_predicate_has_exact_requirement_and_anchor() -> None:
    _request, _context_value, registry, resolved, trace = _build_fixture(
        "us-gdpr-two-axis.json", "us-candidates-request.json"
    )
    resolved_by_id = {
        row["requirement_id"]: row for row in resolved["requirement_results"]
    }
    seen: set[str] = set()
    for candidate in trace["candidate_pathways"]:
        own = (
            candidate["matched_predicates"]
            + candidate["unmatched_predicates"]
            + candidate["unresolved_predicates"]
        )
        for row in own:
            if candidate["profile_ref"]["axis"] == "review_ethics":
                seen.add(row["requirement_id"])
            source = resolved_by_id[row["requirement_id"]]
            assert row["requirement_pointer"] == source["requirement_pointer"]
            assert row["authority_anchor_pointer"] == source["authority_anchor_pointer"]
            requirement = runtime._pointer_get(  # noqa: SLF001 - exact acceptance assertion
                registry, row["requirement_pointer"], "test.pointer"
            )
            assert row["requirement_digest"] == digest(requirement)
            assert row["authority_anchor"] == {
                key: requirement["authority_anchor"][key]
                for key in ("source_id", "authority_url", "provision", "effective_date")
            }
    assert seen == {
        "us.45cfr46.107.irb-composition",
        "us.45cfr46.116.informed-consent",
    }


def test_same_declared_facts_under_two_profiles_produce_different_traces() -> None:
    registry = _registry()
    base = _context("cross-border-us-tw-gdpr.json")
    results: dict[str, tuple[list[dict[str, Any]], set[str]]] = {}
    for profile_id in (
        "us.hhs.45-cfr-46.subpart-a",
        "tw.mohw.human-subjects-research-act",
    ):
        context = copy.deepcopy(base)
        context["context_record_id"] = "test.same-facts." + profile_id.split(".")[0]
        context["selected_profiles"] = [
            row
            for row in context["selected_profiles"]
            if row["axis"] == "data_protection" or row["profile_id"] == profile_id
        ]
        review_display = next(
            row for row in context["display_precedence"] if row["axis"] == "review_ethics"
        )
        review_display["ordered_authorities"] = [
            row
            for row in review_display["ordered_authorities"]
            if row["authority_id"] == profile_id
        ]
        resolved = resolve(context, registry)
        request = _request_for(resolved)
        trace = runtime.build_review_pathway_rule_trace(
            request, context, registry, resolved
        )
        ids = {
            row["requirement_id"]
            for candidate in trace["candidate_pathways"]
            for row in candidate["matched_predicates"]
        }
        results[profile_id] = (copy.deepcopy(context["declared_facts"]), ids)
    assert results["us.hhs.45-cfr-46.subpart-a"][0] == results[
        "tw.mohw.human-subjects-research-act"
    ][0]
    assert results["us.hhs.45-cfr-46.subpart-a"][1] != results[
        "tw.mohw.human-subjects-research-act"
    ][1]


def _unknown_requirement_authority(
    *, false_dominates: bool = False
) -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    context = _context("us-gdpr-two-axis.json")
    registry = _registry()
    fact_id = "pathway.local_category_confirmed"
    registry["fact_definitions"].append(
        {
            "fact_id": fact_id,
            "value_type": "boolean",
            "allowed_values": None,
            "description": "Author declaration used only by the synthetic #669 unknown-predicate fixture.",
        }
    )
    profile = next(
        row
        for row in registry["profiles"]
        if row["profile_id"] == "us.hhs.45-cfr-46.subpart-a"
    )
    requirement = profile["requirements"][0]
    requirement["applies_if"]["operands"].append(
        {"op": "fact_equals", "fact_id": fact_id, "value": True}
    )
    if false_dominates:
        requirement["applies_if"]["operands"].append(
            {
                "op": "fact_equals",
                "fact_id": "data.special_category",
                "value": True,
            }
        )
    unsigned = copy.deepcopy(profile)
    unsigned.pop("profile_digest")
    profile["profile_digest"] = digest(unsigned)
    for selection in context["selected_profiles"]:
        if selection["profile_id"] == profile["profile_id"]:
            selection["profile_digest"] = profile["profile_digest"]
    for display in context["display_precedence"]:
        for authority in display["ordered_authorities"]:
            if authority["authority_id"] == profile["profile_id"]:
                authority["authority_digest"] = profile["profile_digest"]
    context["declared_facts"].append(
        {
            "fact_id": fact_id,
            "value_type": "boolean",
            "state": "unknown",
            "value": None,
            "provenance": "author_declared",
        }
    )
    resolved = resolve(context, registry)
    assert resolved["resolution_state"] == (
        "resolved" if false_dominates else "applicability_unresolved"
    )
    assert resolved["selected_profiles"][-1]["applicability"] == "true"
    request = _request_for(resolved)
    return request, context, registry, resolved


def test_unknown_requirement_fact_stays_unresolved_and_names_holder() -> None:
    request, context, registry, resolved = _unknown_requirement_authority()
    trace = runtime.build_review_pathway_rule_trace(
        request, context, registry, resolved
    )
    assert trace["trace_state"] == "completed"
    rows = [
        row
        for candidate in trace["candidate_pathways"]
        for row in candidate["unresolved_predicates"]
    ]
    row = next(
        row
        for row in rows
        if row["requirement_id"] == "us.45cfr46.107.irb-composition"
    )
    assert row["applicability"] == "unknown"
    assert row["unresolved_fact_ids"] == ["pathway.local_category_confirmed"]
    assert row["responsible_authority_role_id"] == "institution_or_irb"
    assert all(
        row["requirement_id"] != "us.45cfr46.107.irb-composition"
        for candidate in trace["candidate_pathways"]
        for row in candidate["matched_predicates"] + candidate["unmatched_predicates"]
    )


def test_false_aggregate_with_unknown_leaf_remains_in_unresolved_bucket() -> None:
    request, context, registry, resolved = _unknown_requirement_authority(
        false_dominates=True
    )
    trace = runtime.build_review_pathway_rule_trace(
        request, context, registry, resolved
    )
    row = next(
        row
        for candidate in trace["candidate_pathways"]
        for row in candidate["unresolved_predicates"]
        if row["requirement_id"] == "us.45cfr46.107.irb-composition"
    )
    assert row["applicability"] == "false"
    assert row["unresolved_fact_ids"] == ["pathway.local_category_confirmed"]


def test_overlay_requirement_unknown_cannot_open_trace_exception() -> None:
    _context_value, _registry_value, resolved = _authority()
    forged = copy.deepcopy(resolved)
    forged["unresolved_reasons"] = [
        {
            "code": "APPLICABILITY_UNRESOLVED",
            "axis": "review_ethics",
            "authority_id": "institution.overlay",
            "requirement_id": "institution.overlay.rule",
        }
    ]
    forged["downstream_gate"]["all_applicability_resolved"] = False
    forged["downstream_gate"]["profile_dependent_result_allowed"] = False
    forged["resolution_state"] = "applicability_unresolved"
    assert runtime._trace_state(forged) == "authority_context_unresolved"  # noqa: SLF001


def test_no_profile_halts_at_jurisdiction_unresolved() -> None:
    _request, _context_value, _registry_value, _resolved, trace = _build_fixture(
        "no-profile.json", "no-profile-request.json"
    )
    assert trace["trace_state"] == "jurisdiction_unresolved"
    assert trace["candidate_pathways"] == []
    assert {row["code"] for row in trace["halt_reasons"]} == {
        "JURISDICTION_UNRESOLVED"
    }
    assert trace["result"] == runtime.RESULT


def test_profile_level_unknown_or_source_problem_emits_no_partial_trace() -> None:
    context, registry, _resolved = _authority()
    target = next(
        row
        for row in context["declared_facts"]
        if row["fact_id"] == "support.us_hhs_or_common_rule"
    )
    target["state"] = "unknown"
    target["value"] = None
    resolved = resolve(context, registry)
    request = _request_for(resolved)
    request["candidate_pathways"] = []
    trace = runtime.build_review_pathway_rule_trace(
        request, context, registry, resolved
    )
    assert trace["trace_state"] == "authority_context_unresolved"
    assert trace["candidate_pathways"] == []


@pytest.mark.parametrize(
    "mutation",
    ["missing", "duplicate", "foreign", "wrong_profile", "wrong_axis", "unsorted"],
)
def test_candidate_requirement_partition_fails_closed(mutation: str) -> None:
    context, registry, resolved = _authority()
    request = _request_for(resolved, split_requirements=True)
    rows = request["candidate_pathways"]
    if mutation == "missing":
        rows.pop()
    elif mutation == "duplicate":
        rows[1]["predicate_requirement_ids"] = copy.deepcopy(
            rows[0]["predicate_requirement_ids"]
        )
    elif mutation == "foreign":
        rows[0]["predicate_requirement_ids"] = [
            "eu.gdpr.article-6.lawful-basis"
        ]
    elif mutation == "wrong_profile":
        rows[0]["profile_ref"]["profile_id"] = "tw.mohw.human-subjects-research-act"
    elif mutation == "wrong_axis":
        rows[0]["profile_ref"]["axis"] = "unsupported_axis"
    else:
        rows.reverse()
    with pytest.raises(ContractError):
        runtime.build_review_pathway_rule_trace(
            request, context, registry, resolved
        )


@pytest.mark.parametrize("field", ["context_pointer", "registry_pointer", "resolved_digest"])
def test_request_exact_binding_drift_fails(field: str) -> None:
    context, registry, resolved = _authority()
    request = _request_for(resolved)
    if field == "context_pointer":
        request[field]["context_digest"] = "0" * 64
    elif field == "registry_pointer":
        request[field]["registry_digest"] = "0" * 64
    else:
        request[field] = "0" * 64
    with pytest.raises(ContractError):
        runtime.build_review_pathway_rule_trace(
            request, context, registry, resolved
        )


def test_alternative_triggers_are_complete_same_profile_rows_without_ranking() -> None:
    _request, _context_value, _registry_value, _resolved, trace = _build_fixture(
        "us-gdpr-two-axis.json", "us-candidates-request.json"
    )
    first, second = [
        candidate
        for candidate in trace["candidate_pathways"]
        if candidate["profile_ref"]["profile_id"]
        == "us.hhs.45-cfr-46.subpart-a"
    ]
    assert [
        row["target_candidate_id"] for row in first["alternative_pathway_triggers"]
    ] == [second["candidate_id"]]
    assert [
        row["target_candidate_id"] for row in second["alternative_pathway_triggers"]
    ] == [first["candidate_id"]]
    assert trace["ordering_semantics"] == "display_only_sequence_no_decision_meaning"


def test_projected_alternative_row_cap_fails_before_expansion() -> None:
    key = (
        "review_ethics",
        "profile.synthetic",
        "1.0",
        "0" * 64,
    )
    with pytest.raises(ContractError, match="alternative rows"):
        runtime._validate_alternative_volume({key: [4] * 128})  # noqa: SLF001
    runtime._validate_alternative_volume({key: [512]})  # noqa: SLF001


def test_trace_and_renderer_size_caps_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, context, registry, resolved, trace = _build_fixture(
        "us-gdpr-two-axis.json", "us-candidates-request.json"
    )
    monkeypatch.setattr(runtime, "MAX_TRACE_BYTES", 100)
    with pytest.raises(ContractError, match="canonical artifact"):
        runtime.build_review_pathway_rule_trace(
            request, context, registry, resolved
        )
    monkeypatch.setattr(runtime, "MAX_TRACE_BYTES", 8 * 1024 * 1024)
    monkeypatch.setattr(runtime, "MAX_RENDERED_BYTES", 100)
    with pytest.raises(ContractError, match="rendered"):
        runtime.render_review_pathway_rule_trace(trace)


def test_lint_walk_is_iterative_and_node_capped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nested: dict[str, Any] = {"leaf": "safe"}
    for _ in range(2000):
        nested = {"next": nested}
    assert output_lint._walk_strings(nested)[0][1] == "safe"  # noqa: SLF001
    monkeypatch.setattr(output_lint, "MAX_SURFACE_NODES", 5)
    with pytest.raises(ContractError, match="JSON nodes"):
        output_lint._walk_strings(nested)  # noqa: SLF001


def test_rendered_input_reader_enforces_byte_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "large.md"
    path.write_text("123456", encoding="utf-8")
    monkeypatch.setattr(output_lint, "MAX_RENDERED_BYTES", 5)
    with pytest.raises(ContractError, match="exceeds"):
        output_lint._read_text_limited(path)  # noqa: SLF001


def test_trace_digest_and_any_replayed_field_drift_fail() -> None:
    request, context, registry, resolved, trace = _build_fixture(
        "us-gdpr-two-axis.json", "us-candidates-request.json"
    )
    drifted = copy.deepcopy(trace)
    drifted["candidate_pathways"][0]["matched_predicates"][0]["authority_anchor"][
        "effective_date"
    ] = "2026-01-01"
    with pytest.raises(ContractError, match="trace_digest"):
        runtime.validate_review_pathway_rule_trace(
            drifted, request, context, registry, resolved
        )
    drifted["trace_digest"] = digest(
        {key: value for key, value in drifted.items() if key != "trace_digest"}
    )
    with pytest.raises(ContractError, match="deterministic replay"):
        runtime.validate_review_pathway_rule_trace(
            drifted, request, context, registry, resolved
        )


@pytest.mark.parametrize(
    "text",
    [
        "No\u00a0IRB\tneeded",
        "No_IRB_required",
        "IRB not required",
        "ＡＰＰＲＯＶＥＤ",
        "A\u200bpproved",
        "Cleared",
        "Low\u2009risk",
        "There is a 75 % chance",
        "Probably exempt",
        "Approval confidence is high",
        "Most studies like yours use this route",
        "The timeline is two weeks",
        "It takes 2 weeks",
        "This is the recommended route",
        "Result: Exempt",
        "Candidate pathway examined - Expedited",
        "The study may be full board",
    ],
)
def test_normalized_banned_output_near_misses_fail(text: str) -> None:
    assert output_lint._string_violations(  # noqa: SLF001 - policy mutation fixture
        text, permit_pathway_name=False
    )


def test_shipped_lint_near_miss_fixture_matrix() -> None:
    fixture = _json(LINT_FIXTURE_PATH)
    assert fixture["schema_version"] == "review-pathway-lint-fixtures/1.0"
    assert fixture["passing_candidate_names"] == sorted(
        fixture["passing_candidate_names"]
    )
    for name in fixture["passing_candidate_names"]:
        assert output_lint._string_violations(  # noqa: SLF001
            name, permit_pathway_name=True
        ) == []
        assert output_lint._candidate_name_violations(name) == []  # noqa: SLF001
    ids: list[str] = []
    for row in fixture["failing_surfaces"]:
        ids.append(row["fixture_id"])
        assert output_lint._string_violations(  # noqa: SLF001
            row["text"], permit_pathway_name=False
        )
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "name", ["Exempt", "Expedited", "Full Board", "Convened Board", "NHSR"]
)
def test_exact_candidate_name_context_is_not_a_false_positive(name: str) -> None:
    request, context, registry, resolved, _trace = _build_fixture(
        "us-gdpr-two-axis.json", "us-candidates-request.json"
    )
    request["candidate_pathways"][0]["candidate_pathway_name"] = name
    trace = runtime.build_review_pathway_rule_trace(
        request, context, registry, resolved
    )
    rendered = runtime.render_review_pathway_rule_trace(trace)
    assert output_lint.lint_artifacts(trace, rendered) == []


@pytest.mark.parametrize("name", ["Approved", "Cleared", "Low risk", "Exempt likely"])
def test_always_banned_claim_fails_even_in_candidate_name(name: str) -> None:
    request, context, registry, resolved, _trace = _build_fixture(
        "us-gdpr-two-axis.json", "us-candidates-request.json"
    )
    request["candidate_pathways"][0]["candidate_pathway_name"] = name
    with pytest.raises(ContractError, match="banned"):
        runtime.build_review_pathway_rule_trace(
            request, context, registry, resolved
        )


@pytest.mark.parametrize(
    "name",
    [
        "This study is Exempt",
        "The project appears Expedited",
        "Full Board: selected route",
        "one two three four five six seven eight nine ten eleven twelve thirteen",
    ],
)
def test_candidate_field_accepts_a_name_not_determination_prose(name: str) -> None:
    request, context, registry, resolved, _trace = _build_fixture(
        "us-gdpr-two-axis.json", "us-candidates-request.json"
    )
    request["candidate_pathways"][0]["candidate_pathway_name"] = name
    with pytest.raises(ContractError):
        runtime.build_review_pathway_rule_trace(
            request, context, registry, resolved
        )


def test_rendered_candidate_prefix_near_miss_and_extra_claim_fail() -> None:
    _request, _context_value, _registry_value, _resolved, trace = _build_fixture(
        "us-gdpr-two-axis.json", "us-candidates-request.json"
    )
    rendered = runtime.render_review_pathway_rule_trace(trace)
    assert output_lint.lint_artifacts(trace, rendered) == []
    prefix_drift = rendered.replace(
        "Candidate pathway examined:", "Candidate pathway examined -", 1
    )
    assert output_lint.lint_artifacts(trace, prefix_drift)
    assert output_lint.lint_artifacts(trace, rendered + "Result: Exempt\n")


def test_inert_candidate_text_rejects_normalization_controls_and_markdown() -> None:
    context, registry, resolved = _authority()
    request = _request_for(resolved)
    for bad in (" Route", "Ｒｏｕｔｅ", "Route\u200bA", "Route [A]", "Route\nA"):
        mutated = copy.deepcopy(request)
        mutated["candidate_pathways"][0]["candidate_pathway_name"] = bad
        with pytest.raises(ContractError):
            runtime.build_review_pathway_rule_trace(
                mutated, context, registry, resolved
            )


def test_cli_build_validate_render_lint_and_no_overwrite(tmp_path: Path) -> None:
    context, registry, resolved = _authority()
    request = _request_for(resolved)
    context_path = tmp_path / "context.json"
    registry_path = tmp_path / "registry.json"
    resolved_path = tmp_path / "resolved.json"
    request_path = tmp_path / "request.json"
    trace_path = tmp_path / "trace.json"
    rendered_path = tmp_path / "trace.md"
    for path, value in (
        (context_path, context),
        (registry_path, registry),
        (resolved_path, resolved),
        (request_path, request),
    ):
        path.write_text(json.dumps(value), encoding="utf-8")
    bound = [
        "--request",
        str(request_path),
        "--context",
        str(context_path),
        "--registry",
        str(registry_path),
        "--resolved",
        str(resolved_path),
    ]
    build = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_review_pathway_rule_trace.py"), "build", *bound, "--output", str(trace_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert build.returncode == 0, build.stderr
    validate = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_review_pathway_rule_trace.py"), "validate", *bound, "--trace", str(trace_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert validate.returncode == 0, validate.stderr
    render = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_review_pathway_rule_trace.py"), "render", *bound, "--trace", str(trace_path), "--output", str(rendered_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert render.returncode == 0, render.stderr
    lint = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_review_pathway_output.py"), "--trace-json", str(trace_path), "--rendered", str(rendered_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert lint.returncode == 0, lint.stderr
    retry = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_review_pathway_rule_trace.py"), "build", *bound, "--output", str(trace_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert retry.returncode == 2
    assert "refusing to overwrite" in retry.stderr


def test_cli_strict_duplicate_json_fails(tmp_path: Path) -> None:
    request_path = tmp_path / "duplicate.json"
    request_path.write_text('{"schema_version":"one","schema_version":"two"}', encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_review_pathway_rule_trace.py"),
            "build",
            "--request",
            str(request_path),
            "--context",
            str(AUTHORITY_FIXTURES / "us-gdpr-two-axis.json"),
            "--registry",
            str(REGISTRY_PATH),
            "--resolved",
            str(request_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "duplicate JSON key" in result.stderr


def test_atomic_create_handles_short_writes_and_rejects_zero_progress(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = b"0123456789" * 20
    real_write = os.write

    def short_write(fd: int, value: bytes | memoryview) -> int:
        return real_write(fd, bytes(value[: max(1, len(value) // 2)]))

    monkeypatch.setattr(runtime.os, "write", short_write)
    path = tmp_path / "short.bin"
    runtime._atomic_create(path, raw)  # noqa: SLF001 - fault-injection assertion
    assert path.read_bytes() == raw

    def zero_write(_fd: int, _value: bytes | memoryview) -> int:
        return 0

    monkeypatch.setattr(runtime.os, "write", zero_write)
    with pytest.raises(OSError, match="zero-progress"):
        runtime._atomic_create(tmp_path / "zero.bin", raw)  # noqa: SLF001
    assert not (tmp_path / "zero.bin").exists()
