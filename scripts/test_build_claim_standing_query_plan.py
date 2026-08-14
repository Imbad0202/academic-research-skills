"""#655 PR-C: consent-surface builder tests (design §3.1 trigger + §3.2 consent).

Gate 1 (§9): only exact high-impact registry rows are eligible; RANDOM /
TOP-UP / NOT-SELECTED / ALL never silently expand the trigger, and an
ambiguous row stays ineligible until the researcher confirms the recorded
classification. Gate 2 (§9): no dispatchable plan exists without an exact,
current consent receipt bound to the proposed consent surface; refusal or
cancellation produces an explicit local `not_checked` declination and no
plan. Hermetic: no network, no model, synthetic rows only.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts import build_claim_standing_candidate_ledger as substrate
from scripts import build_claim_standing_query_plan as builder
from scripts import claim_standing_discovery as discovery
from scripts.test_claim_standing_stance_contracts import STANCE_PLAN

CLAIM_TEXT = (
    "Retrieval-augmented drafting increases citation recall by 12% "
    "<!--ref:smith2026--> across the audited corpus."
)


def _registry_row(
    checkpoint: str = "stage_2_5",
    tier: str = "HIGH-IMPACT",
    basis: tuple[str, ...] | None = ("numerical",),
) -> dict:
    row = {
        "checkpoint": checkpoint,
        "claim_id": "claim-001",
        "claim_text": CLAIM_TEXT,
        "registry_selection_tier": tier,
    }
    if basis is not None:
        row["high_impact_basis"] = list(basis)
    return row


def _decisions(**overrides: object) -> dict:
    base = {
        "probe_id": "probe-001",
        "decision": "retrieval_only",
        "consent_receipt_id": "receipt-001",
        "created_at": "2026-08-14T01:00:00Z",
        "accepted_at": "2026-08-14T01:05:00Z",
        "indexes": ["semantic_scholar", "openalex"],
        "allowed_languages": ["en"],
        "allowed_document_types": ["journal_article", "preprint"],
        "default_query": {
            "language": "en",
            "date_filter": {"from_year": None, "through_year": None},
        },
        "local_persistence": "session_only",
        "authorized_output_path": None,
        "deletion_boundary": (
            "Deletion removes local working copies; provider records follow "
            "the disclosed provider terms."
        ),
    }
    base.update(overrides)
    return base


def _bound_decisions(row: dict, decisions: dict) -> dict:
    surface = builder.build_consent_surface(row, decisions)
    return {
        **decisions,
        "consent_surface_sha256": builder.consent_surface_sha256(surface),
    }


def _stance_decisions(**overrides: object) -> dict:
    return _decisions(
        decision="retrieval_plus_stance",
        stance_plan=copy.deepcopy(STANCE_PLAN),
        **overrides,
    )


# --- gate 1: exact trigger --------------------------------------------------


def test_stage_2_5_high_impact_row_is_eligible() -> None:
    verdict = builder.assess_eligibility(_registry_row())
    assert verdict["eligible"] is True
    assert verdict["high_impact_basis"] == ["numerical"]


@pytest.mark.parametrize("tier", ["RANDOM", "TOP-UP", "NOT-SELECTED", "ALL"])
def test_stage_2_5_other_tiers_are_ineligible(tier: str) -> None:
    row = _registry_row(tier=tier)
    verdict = builder.assess_eligibility(row)
    assert verdict["eligible"] is False
    with pytest.raises(builder.PlanBuilderError, match=tier):
        builder.build_consent_surface(row, _decisions())


def test_stage_4_5_all_tier_with_recorded_basis_is_eligible() -> None:
    row = _registry_row(checkpoint="stage_4_5", tier="ALL", basis=("causal",))
    verdict = builder.assess_eligibility(row)
    assert verdict["eligible"] is True


@pytest.mark.parametrize(
    "tier", ["HIGH-IMPACT", "RANDOM", "TOP-UP", "NOT-SELECTED"]
)
def test_stage_4_5_non_all_tiers_are_ineligible(tier: str) -> None:
    row = _registry_row(checkpoint="stage_4_5", tier=tier, basis=("causal",))
    assert builder.assess_eligibility(row)["eligible"] is False


@pytest.mark.parametrize("basis", [None, ()])
def test_missing_basis_is_ambiguous_until_researcher_confirms(basis) -> None:
    row = _registry_row(basis=basis)
    verdict = builder.assess_eligibility(row)
    assert verdict["eligible"] is False
    assert verdict["requires_confirmation"] is True
    with pytest.raises(builder.PlanBuilderError, match="confirm"):
        builder.build_consent_surface(row, _decisions())
    confirmation = {
        "confirmed_high_impact": True,
        "high_impact_basis": ["headline_conclusion"],
        "recorded_at": "2026-08-14T00:59:00Z",
    }
    confirmed = builder.assess_eligibility(row, confirmation=confirmation)
    assert confirmed["eligible"] is True
    assert confirmed["high_impact_basis"] == ["headline_conclusion"]


def test_confirmation_with_invalid_basis_token_is_refused() -> None:
    row = _registry_row(basis=None)
    confirmation = {
        "confirmed_high_impact": True,
        "high_impact_basis": ["seems_important"],
        "recorded_at": "2026-08-14T00:59:00Z",
    }
    with pytest.raises(builder.PlanBuilderError, match="basis"):
        builder.assess_eligibility(row, confirmation=confirmation)


def test_confirmation_does_not_mutate_the_registry_row() -> None:
    row = _registry_row(basis=None)
    before = copy.deepcopy(row)
    decisions = _decisions(
        eligibility_confirmation={
            "confirmed_high_impact": True,
            "high_impact_basis": ["disputed"],
            "recorded_at": "2026-08-14T00:59:00Z",
        }
    )
    plan = builder.bind_plan(row, _bound_decisions(row, decisions))
    assert row == before
    assert plan["claim"]["high_impact_basis"] == ["disputed"]


# --- gate 2: consent before any dispatchable plan ---------------------------


def test_bind_without_surface_hash_is_refused() -> None:
    row = _registry_row()
    with pytest.raises(builder.PlanBuilderError, match="consent surface"):
        builder.bind_plan(row, _decisions())


def test_bind_with_stale_surface_hash_is_refused() -> None:
    row = _registry_row()
    bound = _bound_decisions(row, _decisions())
    revised = dict(row)
    revised["claim_text"] = CLAIM_TEXT + " Revised after proposal."
    with pytest.raises(builder.PlanBuilderError, match="consent surface"):
        builder.bind_plan(revised, bound)


def test_cancel_produces_not_checked_declination_and_no_plan() -> None:
    row = _registry_row()
    decisions = _decisions(
        decision="cancel", recorded_at="2026-08-14T01:05:00Z"
    )
    record = builder.bind_plan(row, _bound_decisions(row, decisions))
    assert record["record_kind"] == "claim-standing-probe-declination/1.0"
    assert record["status"] == "not_checked"
    assert record["network_calls"] == "none"
    assert record["model_calls"] == "none"
    assert record["claim_sha256"] == substrate.text_digest(CLAIM_TEXT)
    assert "queries" not in record
    assert "consent" not in record


def test_retrieval_only_plan_validates_under_the_track_a_substrate() -> None:
    row = _registry_row()
    plan = builder.bind_plan(row, _bound_decisions(row, _decisions()))
    assert plan["schema_version"] == "claim-standing-query-plan/1.0"
    substrate.validate_plan(plan)
    substrate.validate_schema(plan, "query_plan.schema.json", "query plan")
    assert plan["consent"]["decision"] == "retrieval_only"
    assert plan["authorized_content_classes"] == ["accepted_search_query"]


def test_retrieval_plus_stance_plan_validates_as_1_1() -> None:
    row = _registry_row()
    plan = builder.bind_plan(row, _bound_decisions(row, _stance_decisions()))
    assert plan["schema_version"] == "claim-standing-query-plan/1.1"
    substrate.validate_plan(plan)
    substrate.validate_schema(plan, "query_plan_v1_1.schema.json", "query plan")
    assert plan["consent"]["stance_plan_sha256"] == substrate.digest(
        plan["stance_plan"]
    )
    assert plan["authorized_content_classes"] == [
        "accepted_search_query",
        "claim_and_selected_evidence_to_stance_provider",
    ]


def test_default_query_is_exact_claim_derivation() -> None:
    row = _registry_row()
    plan = builder.bind_plan(row, _bound_decisions(row, _decisions()))
    assert len(plan["queries"]) == 1
    query = plan["queries"][0]
    assert query["construction"] == "exact_claim"
    expected = substrate.exact_claim_query(CLAIM_TEXT)
    assert query["accepted_query_text"] == expected
    assert query["original_query_text"] == expected
    assert "<!--ref:" not in query["accepted_query_text"]
    assert sorted(query["index_targets"]) == ["openalex", "semantic_scholar"]


def test_researcher_edited_query_keeps_original_and_construction() -> None:
    row = _registry_row()
    decisions = _decisions(
        queries=[
            {
                "query_id": "q1",
                "accepted_query_text": "retrieval augmentation citation recall",
                "construction": "researcher_authored",
                "language": "en",
                "date_filter": {"from_year": 2020, "through_year": None},
                "index_targets": ["semantic_scholar"],
            }
        ]
    )
    plan = builder.bind_plan(row, _bound_decisions(row, decisions))
    query = plan["queries"][0]
    assert query["construction"] == "researcher_authored"
    assert query["accepted_query_text"] == "retrieval augmentation citation recall"
    substrate.validate_plan(plan)


def test_exact_claim_construction_with_edited_text_is_refused() -> None:
    row = _registry_row()
    decisions = _decisions(
        queries=[
            {
                "query_id": "q1",
                "accepted_query_text": "something else entirely",
                "construction": "exact_claim",
                "language": "en",
                "date_filter": {"from_year": None, "through_year": None},
                "index_targets": ["semantic_scholar"],
            }
        ]
    )
    with pytest.raises(builder.PlanBuilderError, match="exact_claim"):
        builder.bind_plan(row, _bound_decisions(row, decisions))


def test_assisted_construction_is_not_authorized_in_this_slice() -> None:
    row = _registry_row()
    decisions = _decisions(
        queries=[
            {
                "query_id": "q1",
                "accepted_query_text": "assisted draft query",
                "construction": "assisted_then_researcher_approved",
                "language": "en",
                "date_filter": {"from_year": None, "through_year": None},
                "index_targets": ["semantic_scholar"],
            }
        ]
    )
    with pytest.raises(builder.PlanBuilderError, match="assisted"):
        builder.build_consent_surface(row, decisions)


def test_more_than_three_queries_is_refused() -> None:
    row = _registry_row()
    query = {
        "accepted_query_text": "q",
        "construction": "researcher_authored",
        "language": "en",
        "date_filter": {"from_year": None, "through_year": None},
        "index_targets": ["semantic_scholar"],
    }
    decisions = _decisions(
        queries=[{**query, "query_id": f"q{i}"} for i in range(1, 5)]
    )
    with pytest.raises(builder.PlanBuilderError, match="quer"):
        builder.build_consent_surface(row, decisions)


def test_unknown_index_is_refused() -> None:
    row = _registry_row()
    with pytest.raises(builder.PlanBuilderError, match="index"):
        builder.build_consent_surface(
            row, _decisions(indexes=["semantic_scholar", "shadow_index"])
        )


def test_roster_entries_come_from_the_declared_discovery_adapters() -> None:
    row = _registry_row()
    plan = builder.bind_plan(row, _bound_decisions(row, _decisions()))
    defaults = discovery.provider_roster_defaults()
    assert plan["provider_roster"] == [
        defaults["openalex"],
        defaults["semantic_scholar"],
    ]


def test_acceptance_before_creation_is_refused() -> None:
    row = _registry_row()
    decisions = _decisions(accepted_at="2026-08-14T00:30:00Z")
    with pytest.raises(builder.PlanBuilderError):
        builder.bind_plan(row, _bound_decisions(row, decisions))


def test_explicit_local_export_binds_the_authorized_path() -> None:
    row = _registry_row()
    decisions = _decisions(
        local_persistence="explicit_local_export",
        authorized_output_path="/operator-named/probe-001",
    )
    plan = builder.bind_plan(row, _bound_decisions(row, decisions))
    substrate.validate_plan(plan)
    assert plan["consent"]["authorized_output_path"] == "/operator-named/probe-001"
    assert (
        plan["consent"]["export_boundary"]
        == substrate.EXPLICIT_LOCAL_EXPORT_BOUNDARY
    )


# --- consent surface content (§3.2 closed receipt) --------------------------


def test_surface_contains_every_required_consent_element() -> None:
    row = _registry_row()
    surface = builder.build_consent_surface(row, _stance_decisions())
    assert surface["surface_kind"] == "claim-standing-consent-surface/1.0"
    assert surface["claim"]["claim_text"] == CLAIM_TEXT
    assert surface["claim"]["claim_id"] == "claim-001"
    provider_ids = {p["index_id"] for p in surface["providers"]}
    assert provider_ids == {"semantic_scholar", "openalex"}
    assert all(p["purpose"] == "scholarly_discovery" for p in surface["providers"])
    assert surface["caps"] == substrate.CAPS
    assert surface["query_transmission"]["exact_claim_text"] is True
    assert surface["query_transmission"]["researcher_edited_query"] is False
    assert surface["llm_transmission"]["abstracts_to_llm"] is True
    assert surface["llm_transmission"]["session_held_full_text_to_llm"] is False
    assert surface["stance_provider"] == {
        "provider_identity": STANCE_PLAN["provider_identity"],
        "model_identity": STANCE_PLAN["model_identity"],
    }
    assert surface["local_persistence"] == "session_only"
    assert "advisory" in surface["advisory_statement"]
    assert "search-bounded" in surface["advisory_statement"]
    assert surface["choices"] == [
        "edit_or_redact_claim",
        "approve_retrieval_only",
        "approve_retrieval_plus_stance",
        "cancel",
    ]


def test_surface_for_retrieval_only_names_no_stance_provider() -> None:
    row = _registry_row()
    surface = builder.build_consent_surface(row, _decisions())
    assert surface["stance_provider"] is None
    assert surface["llm_transmission"]["abstracts_to_llm"] is False


def test_surface_digest_is_stable_and_claim_bound() -> None:
    row = _registry_row()
    decisions = _decisions()
    first = builder.consent_surface_sha256(
        builder.build_consent_surface(row, decisions)
    )
    second = builder.consent_surface_sha256(
        builder.build_consent_surface(row, decisions)
    )
    assert first == second
    revised = dict(row)
    revised["claim_text"] = CLAIM_TEXT + " Revised."
    third = builder.consent_surface_sha256(
        builder.build_consent_surface(revised, decisions)
    )
    assert third != first


# --- inputs stay unmutated (gate 12 support) --------------------------------


def test_bind_does_not_mutate_inputs() -> None:
    row = _registry_row()
    decisions = _bound_decisions(row, _stance_decisions())
    row_before = copy.deepcopy(row)
    decisions_before = copy.deepcopy(decisions)
    builder.bind_plan(row, decisions)
    assert row == row_before
    assert decisions == decisions_before


# --- CLI --------------------------------------------------------------------


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_cli_propose_prints_surface_and_digest(tmp_path, capsys) -> None:
    row = _registry_row()
    decisions = _decisions()
    rc = builder.main(
        [
            "propose",
            "--registry-claim", str(_write_json(tmp_path / "row.json", row)),
            "--decisions", str(_write_json(tmp_path / "decisions.json", decisions)),
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    surface = builder.build_consent_surface(row, decisions)
    assert payload["consent_surface"] == surface
    assert payload["consent_surface_sha256"] == builder.consent_surface_sha256(
        surface
    )


def test_cli_bind_writes_a_validating_plan(tmp_path, capsys) -> None:
    row = _registry_row()
    decisions = _bound_decisions(row, _decisions())
    output = tmp_path / "plan.json"
    rc = builder.main(
        [
            "bind",
            "--registry-claim", str(_write_json(tmp_path / "row.json", row)),
            "--decisions", str(_write_json(tmp_path / "decisions.json", decisions)),
            "--output", str(output),
        ]
    )
    assert rc == 0
    plan = json.loads(output.read_text(encoding="utf-8"))
    substrate.validate_plan(plan)


def test_cli_bind_refuses_ineligible_row_without_output(tmp_path, capsys) -> None:
    row = _registry_row(tier="RANDOM")
    output = tmp_path / "plan.json"
    rc = builder.main(
        [
            "bind",
            "--registry-claim", str(_write_json(tmp_path / "row.json", row)),
            "--decisions",
            str(_write_json(tmp_path / "decisions.json", _decisions())),
            "--output", str(output),
        ]
    )
    assert rc == 1
    assert "RANDOM" in capsys.readouterr().err
    assert not output.exists()


def test_cli_bind_cancel_prints_declination_and_writes_no_plan(
    tmp_path, capsys
) -> None:
    row = _registry_row()
    decisions = _bound_decisions(
        row, _decisions(decision="cancel", recorded_at="2026-08-14T01:05:00Z")
    )
    output = tmp_path / "plan.json"
    rc = builder.main(
        [
            "bind",
            "--registry-claim", str(_write_json(tmp_path / "row.json", row)),
            "--decisions", str(_write_json(tmp_path / "decisions.json", decisions)),
            "--output", str(output),
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["record_kind"] == "claim-standing-probe-declination/1.0"
    assert not output.exists()
