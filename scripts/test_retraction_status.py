"""Hermetic acceptance matrix for #651 retraction status."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import bibliographic_integrity_signals as carrier  # noqa: E402
import openalex_client  # noqa: E402
import retraction_status as status  # noqa: E402


NOW = "2026-08-08T00:00:00Z"
STALE_AFTER = "2026-09-07T00:00:00Z"
DOI = "10.1234/original.1"


def _entry(**updates: object) -> dict:
    value = {
        "citation_key": "smith2024",
        "doi": DOI,
        "title": "A Study",
        "source_pointer": f"https://doi.org/{DOI}",
        "source_acquisition_date": "2026-01-15T00:00:00Z",
    }
    value.update(updates)
    return value


def _oa(retracted: bool) -> dict:
    return {
        "status": "checked",
        "record": {
            "id": "https://openalex.org/W1",
            "doi": f"https://doi.org/{DOI}",
            "title": "A Study",
            "is_retracted": retracted,
        },
    }


def _event(kind: str, date: str | None = "2026-06-01T00:00:00Z") -> dict:
    value = {
        "DOI": "10.1234/notice.1",
        "type": kind,
        "source": "retraction-watch",
        "record-id": 42,
    }
    if date is not None:
        value["updated"] = {"date-time": date}
    return value


def _cr(*events: dict) -> dict:
    return {
        "status": "checked",
        "records": [{"DOI": DOI, "title": ["A Study"], "updated-by": list(events)}],
    }


def _resolve(
    *,
    entry: dict | None = None,
    openalex: dict | None = None,
    crossref: dict | None = None,
    **kwargs: object,
) -> dict:
    return status.resolve_retraction_signal(
        entry or _entry(),
        openalex=openalex or _oa(True),
        crossref=crossref or _cr(_event("retraction")),
        checked_at=NOW,
        recorded_at=NOW,
        stale_after=STALE_AFTER,
        **kwargs,
    )


def test_openalex_select_retains_retraction_field_without_another_request() -> None:
    assert "is_retracted" in openalex_client._FIELDS.split(",")


def test_retracted_resolvers_agree_and_row_is_strict_eligible() -> None:
    signal = _resolve()
    context = signal["retraction_context"]
    assert signal["schema_version"].endswith("/1.1")
    assert signal["finding"] == "detected"
    assert context["effective_status"] == "retracted"
    assert context["resolver_agreement"] == "agree"
    assert signal["terminal_policy"]["eligible"] is True
    assert not carrier.validation_errors(signal)


def test_both_clean_is_not_detected() -> None:
    signal = _resolve(openalex=_oa(False), crossref=_cr())
    assert signal["finding"] == "not_detected"
    assert signal["retraction_context"]["effective_status"] == "not_retracted"
    assert signal["terminal_policy"]["eligible"] is False


def test_crossref_updated_by_is_parsed_on_original() -> None:
    signal = _resolve(openalex={"status": "degraded"})
    crossref = signal["retraction_context"]["resolver_observations"][1]
    assert crossref["verdict"] == "retracted"
    assert crossref["events"][0]["direction"] == "updated-by"


def test_crossref_update_to_is_parsed_from_notice() -> None:
    notice = {
        "DOI": "10.1234/notice.1",
        "update-to": [{
            "DOI": DOI,
            "type": "retraction",
            "source": "publisher",
            "updated": {"date-time": "2026-06-01T00:00:00Z"},
        }],
    }
    signal = _resolve(
        openalex={"status": "degraded"},
        crossref={"status": "checked", "records": [notice]},
    )
    observation = signal["retraction_context"]["resolver_observations"][1]
    assert observation["verdict"] == "retracted"
    assert observation["events"][0]["direction"] == "update-to"


def test_nested_relation_updated_by_is_supported() -> None:
    record = {"DOI": DOI, "relation": {"updated-by": [_event("retraction")]}}
    signal = _resolve(
        openalex={"status": "degraded"},
        crossref={"status": "checked", "records": [record]},
    )
    assert signal["retraction_context"]["effective_status"] == "retracted"


def test_later_reinstatement_wins() -> None:
    signal = _resolve(
        openalex=_oa(False),
        crossref=_cr(
            _event("retraction", "2026-05-01T00:00:00Z"),
            _event("reinstatement", "2026-07-01T00:00:00Z"),
        ),
    )
    assert signal["retraction_context"]["effective_status"] == "reinstated"
    assert signal["finding"] == "not_detected"
    assert status.evaluate_retraction_policy(signal, "strict") is None


def test_conflicting_undated_crossref_events_are_disputed() -> None:
    signal = _resolve(
        openalex={"status": "degraded"},
        crossref=_cr(_event("retraction", None), _event("reinstatement", None)),
    )
    assert signal["retraction_context"]["effective_status"] == "disputed"
    assert signal["finding"] == "unresolved"


def test_resolver_disagreement_is_visible_and_never_terminal() -> None:
    signal = _resolve(openalex=_oa(False))
    assert signal["retraction_context"]["resolver_agreement"] == "disagree"
    assert signal["retraction_context"]["effective_status"] == "disputed"
    assert signal["terminal_policy"]["eligible"] is False


def test_missing_acquisition_date_is_not_decidable() -> None:
    signal = _resolve(entry=_entry(source_acquisition_date=None))
    assert signal["retraction_context"]["timing_vs_acquisition"] == "not_decidable"


def test_retraction_after_acquisition_is_refresh_context() -> None:
    signal = _resolve()
    assert signal["retraction_context"]["timing_vs_acquisition"] == "after_acquisition"


def test_obtained_at_is_never_substituted_for_acquisition_date() -> None:
    entry = _entry(source_acquisition_date=None, obtained_at="2026-01-15T00:00:00Z")
    signal = _resolve(entry=entry)
    assert signal["retraction_context"]["source_acquisition_date"] is None
    assert signal["retraction_context"]["timing_vs_acquisition"] == "not_decidable"


def test_worst_tier_wins_for_multi_claim_citation() -> None:
    signal = _resolve(
        affected_claims=["claim:minor", "claim:main"],
        claim_impacts={"claim:minor": "OTHER", "claim:main": "HIGH-IMPACT"},
    )
    assert signal["retraction_context"]["load_bearing"] == "high_impact"
    assert signal["retraction_context"]["claim_join_rule"] == "worst_tier_wins"


def test_manual_entry_with_doi_is_attemptable() -> None:
    signal = _resolve(entry=_entry(obtained_via="manual"))
    assert signal["check_status"] == "checked"
    assert signal["finding"] == "detected"


def test_manual_entry_without_doi_is_unresolved_not_clean() -> None:
    entry = _entry(obtained_via="manual")
    del entry["doi"]
    signal = _resolve(entry=entry)
    assert signal["check_status"] == "not_checked"
    assert signal["finding"] == "unresolved"
    assert signal["retraction_context"]["doi"] is None


def test_doi_less_entry_ignores_supplied_title_match_metadata() -> None:
    entry = _entry()
    del entry["doi"]
    signal = _resolve(entry=entry, openalex=_oa(True), crossref=_cr(_event("retraction")))
    assert signal["retraction_context"]["effective_status"] == "unknown"


def test_declaration_without_notice_does_not_waive_strict() -> None:
    signal = _resolve(declaration={"declared": True, "declaration_id": "decl-1"})
    assert signal["terminal_policy"]["eligible"] is True
    assert signal["retraction_context"]["declared_legitimate_citation"]["deterministic_exception"] is False


def test_boolean_declaration_without_auditable_ids_does_not_waive_strict() -> None:
    signal = _resolve(declaration={
        "declared": True,
        "retraction_notice_cited": True,
    })
    assert signal["retraction_context"]["declared_legitimate_citation"]["deterministic_exception"] is False
    assert signal["terminal_policy"]["eligible"] is True


def test_declaration_plus_notice_disables_strict_without_context_judgment() -> None:
    signal = _resolve(declaration={
        "declared": True,
        "declaration_id": "decl-1",
        "retraction_notice_cited": True,
        "notice_citation_key": "notice2026",
    })
    context = signal["retraction_context"]["declared_legitimate_citation"]
    assert context["deterministic_exception"] is True
    assert context["contextual_judgment"] == "not_performed"
    assert signal["terminal_policy"]["eligible"] is False
    assert status.evaluate_retraction_policy(signal, "strict") is None


def test_advisory_default_never_emits_terminal_token() -> None:
    assert status.evaluate_retraction_policy(_resolve(), None) is None
    assert status.evaluate_retraction_policy(_resolve(), "advisory") is None


def test_strict_emits_generic_terminal_token() -> None:
    token = status.evaluate_retraction_policy(_resolve(), "strict")
    assert token == "TERMINAL-BLOCK severity=HIGH-BLOCK policy=retraction reason=retracted_reference mode=strict"
    assert "CONTAMINATED-" not in token


def test_stale_signal_is_visible_but_not_strict_eligible() -> None:
    signal = status.resolve_retraction_signal(
        _entry(),
        openalex=_oa(True),
        crossref=_cr(_event("retraction")),
        checked_at="2026-06-01T00:00:00Z",
        recorded_at=NOW,
        stale_after="2026-08-01T00:00:00Z",
    )
    assert signal["provenance"]["freshness"] == "stale"
    assert signal["terminal_policy"]["eligible"] is False


def test_reason_codes_are_only_carried_when_served() -> None:
    plain = _resolve()
    enriched = _resolve(crossref={
        **_cr(_event("retraction")),
        "retraction_reasons": ["Data falsification", "Data falsification", "Error"],
    })
    assert plain["retraction_context"]["reason_availability"] == "not_served"
    assert plain["retraction_context"]["retraction_reasons"] == []
    assert enriched["retraction_context"]["reason_availability"] == "served"
    assert enriched["retraction_context"]["retraction_reasons"] == ["Data falsification", "Error"]


def test_policy_slug_composes_in_sorted_existing_grammar() -> None:
    slug = status.citation_policy_slug({
        "retraction": "strict",
        "citation_existence": "strict",
        "submission_package": "strict",
    })
    assert slug == "citation_existence.strict+retraction.strict"


def test_retraction_cache_current_round_trip(tmp_path: Path) -> None:
    cache = status.RetractionStatusCache(tmp_path / "cache.sqlite")
    cache.put(DOI.upper(), "openalex", {"status": "checked", "verdict": "not_retracted"}, checked_at=NOW)
    found = cache.lookup(DOI, "openalex", now="2026-08-20T00:00:00Z")
    assert found == {
        "cache_state": "current",
        "checked_at": NOW,
        "observation": {"status": "checked", "verdict": "not_retracted"},
    }


def test_retraction_cache_marks_non_retracted_row_stale_for_revalidation(tmp_path: Path) -> None:
    cache = status.RetractionStatusCache(tmp_path / "cache.sqlite")
    cache.put(DOI, "crossref", {"status": "checked", "verdict": "not_retracted"}, checked_at=NOW)
    found = cache.lookup(DOI, "crossref", now="2026-09-20T00:00:00Z")
    assert found is not None
    assert found["cache_state"] == "stale"
    assert found["observation"]["verdict"] == "not_retracted"


def test_cache_preserves_degraded_instead_of_coercing_clean(tmp_path: Path) -> None:
    cache = status.RetractionStatusCache(tmp_path / "cache.sqlite")
    cache.put(DOI, "openalex", {"status": "degraded", "verdict": "unknown"}, checked_at=NOW)
    found = cache.lookup(DOI, "openalex", now=NOW)
    assert found is not None
    assert found["observation"] == {"status": "degraded", "verdict": "unknown"}


def test_cache_rejects_untyped_status(tmp_path: Path) -> None:
    cache = status.RetractionStatusCache(tmp_path / "cache.sqlite")
    with pytest.raises(ValueError, match="typed status"):
        cache.put(DOI, "openalex", {"status": "clean"}, checked_at=NOW)


def test_v1_carrier_remains_backward_compatible() -> None:
    fixture = json.loads(
        (SCRIPTS / "fixtures/bibliographic_integrity_signals/retraction.json").read_text(encoding="utf-8")
    )
    assert not carrier.validation_errors(fixture)


def test_v11_schema_requires_retraction_context() -> None:
    fixture = json.loads(
        (SCRIPTS / "fixtures/bibliographic_integrity_signals/retraction.json").read_text(encoding="utf-8")
    )
    fixture["schema_version"] = status.SCHEMA_VERSION
    validator = Draft202012Validator(
        carrier.load_schema(), format_checker=Draft202012Validator.FORMAT_CHECKER
    )
    assert any("retraction_context" in error.message for error in validator.iter_errors(fixture))


def test_v1_schema_rejects_v11_context() -> None:
    signal = _resolve()
    signal["schema_version"] = "bibliographic-integrity-signal/1.0"
    assert carrier.validation_errors(signal)


def test_cli_emits_valid_signal(tmp_path: Path) -> None:
    payload = {
        "entry": _entry(),
        "openalex": _oa(True),
        "crossref": _cr(_event("retraction")),
        "checked_at": NOW,
        "recorded_at": NOW,
        "stale_after": STALE_AFTER,
    }
    path = tmp_path / "input.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "retraction_status.py"), str(path)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["finding"] == "detected"


def test_signal_is_json_round_trip_stable() -> None:
    signal = _resolve()
    assert json.loads(json.dumps(copy.deepcopy(signal), sort_keys=True)) == signal


def test_retraction_context_survives_advisory_projection() -> None:
    rendered = carrier.render_advisory_section([_resolve()])
    assert rendered.count("## Bibliographic Integrity Advisories") == 1
    assert "effective=retracted" in rendered
    assert "agreement=agree" in rendered
    assert "legitimate_exception=false" in rendered
    assert "<!--ref:" not in rendered


def test_terminal_policy_schema_accepts_retraction_without_default() -> None:
    schema = json.loads(
        (REPO_ROOT / "shared/contracts/passport/terminal_policies.schema.json").read_text(encoding="utf-8")
    )
    retraction = schema["properties"]["retraction"]
    assert set(retraction["enum"]) == {"advisory", "strict"}
    assert "default" not in retraction
    validator = Draft202012Validator(schema)
    assert list(validator.iter_errors({"retraction": "strict"})) == []


def test_authority_and_policy_surfaces_are_wired() -> None:
    required = {
        "academic-pipeline/agents/pipeline_orchestrator_agent.md": (
            "policy=retraction",
            "reason=retracted_reference",
            "Ignore legacy",
            "`retraction_check` for both status and policy",
        ),
        "academic-paper/agents/formatter_agent.md": (
            "`contamination_triangulation`, `citation_existence`, `retraction`, `temporal_integrity`",
            "formatter never evaluates it",
        ),
        "deep-research/agents/bibliography_agent.md": (
            "Retraction Status Production (#651)",
            "Do not write or update legacy",
        ),
        "deep-research/agents/ethics_review_agent.md": (
            "Retraction-status authority",
            "does not independently label retraction CRITICAL or block delivery",
        ),
        "shared/references/firm_rules.md": (
            "R-L3-2-F",
            "No retraction advisory marker token is minted",
        ),
    }
    for relative, needles in required.items():
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text, f"{relative} missing {needle!r}"


def test_schema_rejects_stale_strict_eligible_row() -> None:
    signal = _resolve()
    signal["provenance"]["freshness"] = "stale"
    assert carrier.validation_errors(signal)


def test_schema_rejects_fabricated_legitimate_exception() -> None:
    signal = _resolve(declaration={
        "declared": True,
        "declaration_id": "decl-1",
        "retraction_notice_cited": True,
        "notice_citation_key": "notice2026",
    })
    signal["retraction_context"]["declared_legitimate_citation"]["declared"] = False
    assert carrier.validation_errors(signal)


def test_schema_binds_reason_availability_to_nonempty_reasons() -> None:
    signal = _resolve(crossref={
        **_cr(_event("retraction")),
        "retraction_reasons": ["Error"],
    })
    signal["retraction_context"]["retraction_reasons"] = []
    assert carrier.validation_errors(signal)
