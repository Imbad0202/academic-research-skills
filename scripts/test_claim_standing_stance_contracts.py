from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import build_claim_standing_candidate_ledger as ledger
from scripts import claim_standing_discovery as discovery
from scripts.test_build_claim_standing_candidate_ledger import _rehash_plan as _rehash

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "scripts/fixtures/claim_standing_candidate_ledger"
CONTRACTS = ROOT / "shared/contracts"

STANCE_PLAN = {
    "provider_identity": "Synthetic Stance Provider",
    "model_identity": "synthetic-stance-model-1",
    "prompt_contract_version": "claim-standing-stance-prompt-1.0",
    "abstracts_to_llm_authorized": True,
    "session_held_full_text_to_llm_authorized": False,
    "retention_state": "unknown",
    "retention_reference": None,
}


def _plan_v1_0() -> dict:
    return json.loads((FIXTURES / "query_plan.json").read_text(encoding="utf-8"))


def _plan_v1_1(*, stance: bool = True) -> dict:
    plan = _plan_v1_0()
    plan["schema_version"] = ledger.PLAN_VERSION_1_1
    consent = plan["consent"]
    if stance:
        plan["stance_plan"] = copy.deepcopy(STANCE_PLAN)
        consent["decision"] = "retrieval_plus_stance"
        consent["stance_classification_authorized"] = True
        plan["authorized_content_classes"] = [
            "accepted_search_query",
            "claim_and_selected_evidence_to_stance_provider",
        ]
    else:
        plan["stance_plan"] = None
        consent["decision"] = "retrieval_only"
        consent["stance_classification_authorized"] = False
        plan["authorized_content_classes"] = ["accepted_search_query"]
    _rehash(plan)
    return plan


def _schema(relative: str) -> dict:
    return json.loads((CONTRACTS / relative).read_text(encoding="utf-8"))


# --- contract files ---------------------------------------------------------


@pytest.mark.parametrize(
    "relative",
    [
        "claim_standing/query_plan_v1_1.schema.json",
        "claim_standing/stance_record.schema.json",
        "evidence/evidence_row_v1_3.schema.json",
    ],
)
def test_new_contracts_are_valid_closed_draft_2020_12(relative):
    schema = _schema(relative)
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False


def test_v1_3_reuses_the_family_blocks_with_a_narrowed_state_vocabulary():
    v1_0 = _schema("evidence/evidence_row.schema.json")["properties"]
    v1_3 = _schema("evidence/evidence_row_v1_3.schema.json")["properties"]
    for block in ("cache", "content_handling", "row_sha256"):
        assert v1_3[block] == v1_0[block]
    # The excerpt block matches the family except its state vocabulary drops
    # the two anchor-derived states (this surface carries no anchor).
    for field in ("text", "excerpt_sha256", "source_span_utf8", "captured_at"):
        assert (
            v1_3["excerpt"]["properties"][field]
            == v1_0["excerpt"]["properties"][field]
        )
    family_states = set(v1_0["excerpt"]["properties"]["state"]["enum"])
    surface_states = set(v1_3["excerpt"]["properties"]["state"]["enum"])
    assert surface_states == family_states - {"unconfirmed_anchor", "anchorless"}
    assert v1_3["surface"] == {"const": "claim_standing_advisory"}


def test_v1_3_cross_field_invariants_hold():
    schema = _schema("evidence/evidence_row_v1_3.schema.json")
    validator = Draft202012Validator(schema)
    base = {
        "schema_version": "evidence-row/1.3",
        "surface": "claim_standing_advisory",
        "row_id": "EVR-CS-1",
        "claim": {"claim_id": "c1", "claim_sha256": "a" * 64, "probe_id": "probe-1"},
        "candidate": {
            "work_family_id": "wf-001",
            "canonical_raw_hit_id": "hit-1",
            "candidate_ledger_sha256": "b" * 64,
            "display_label": "Synthetic candidate",
            "doi": None,
        },
        "coverage": "abstract",
        "source": {"source_content_sha256": "c" * 64, "source_content_utf8_bytes": 120},
        "excerpt": {
            "state": "agent_extracted",
            "text": "bounded inspected excerpt",
            "excerpt_sha256": "d" * 64,
            "source_span_utf8": {"start": 0, "end": 25},
            "captured_at": "2026-08-14T00:00:00Z",
        },
        "cache": {"status": "miss", "key_sha256": "e" * 64},
        "content_handling": {
            "contains_external_text": True,
            "sharing_scope": "session_only",
            "rights_basis": "not_assessed",
        },
        "row_sha256": "f" * 64,
    }
    assert validator.is_valid(base)
    import copy as _copy

    smuggle = _copy.deepcopy(base)
    smuggle["excerpt"].update(state="source_missing")
    assert not validator.is_valid(smuggle)  # payload must be null on failure states
    rights = _copy.deepcopy(base)
    rights["content_handling"].update(sharing_scope="user_confirmed_shareable")
    assert not validator.is_valid(rights)  # shareable requires declared rights
    meta = _copy.deepcopy(base)
    meta["coverage"] = "metadata_only"
    assert not validator.is_valid(meta)  # metadata-only cannot carry inspected evidence


@pytest.mark.parametrize(
    "state, reference",
    [("known", None), ("unknown", "https://example.org/retention")],
)
def test_stance_plan_retention_coupling_is_schema_enforced(state, reference):
    schema = _schema("claim_standing/query_plan_v1_1.schema.json")
    plan = _plan_v1_1(stance=True)
    plan["stance_plan"]["retention_state"] = state
    plan["stance_plan"]["retention_reference"] = reference
    _rehash(plan)
    assert not Draft202012Validator(schema).is_valid(plan)


def test_stance_record_carries_no_scalar_score_field():
    schema = _schema("claim_standing/stance_record.schema.json")

    def property_names(node) -> set[str]:
        names: set[str] = set()
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "properties" and isinstance(value, dict):
                    names.update(value.keys())
                names.update(property_names(value))
        elif isinstance(node, list):
            for item in node:
                names.update(property_names(item))
        return names

    for forbidden in ("confidence", "probability", "credibility", "score", "trust"):
        assert not any(forbidden in name for name in property_names(schema))


# --- substrate plan-version support -----------------------------------------


def test_substrate_accepts_both_plan_versions():
    for plan in (_plan_v1_0(), _plan_v1_1(stance=True), _plan_v1_1(stance=False)):
        ledger.validate_schema(
            plan, ledger.plan_schema_filename(plan), "query plan"
        )
        ledger.validate_plan(plan)


def test_v1_1_projection_includes_the_stance_plan():
    plan = _plan_v1_1(stance=True)
    projection = ledger.consentable_plan_projection(plan)
    assert projection["stance_plan"] == STANCE_PLAN
    retrieval_only = ledger.consentable_plan_projection(_plan_v1_1(stance=False))
    assert retrieval_only["stance_plan"] is None
    v1_0 = ledger.consentable_plan_projection(_plan_v1_0())
    assert "stance_plan" not in v1_0


@pytest.mark.parametrize(
    "mutate, message",
    [
        (
            lambda plan: plan.__setitem__("stance_plan", None),
            "stance_plan",
        ),
        (
            lambda plan: plan["consent"].__setitem__(
                "stance_plan_sha256", "0" * 64
            ),
            "stance_plan_sha256|does not bind",
        ),
        (
            lambda plan: plan.__setitem__(
                "authorized_content_classes", ["accepted_search_query"]
            ),
            "authorized_content_classes",
        ),
    ],
)
def test_v1_1_stance_bindings_fail_closed(mutate, message):
    plan = _plan_v1_1(stance=True)
    mutate(plan)
    plan["plan_sha256"] = ledger.bound_digest(plan, "plan_sha256")
    with pytest.raises(ledger.LedgerError, match=message):
        ledger.validate_plan(plan)


def test_retrieval_only_v1_1_cannot_carry_the_stance_content_class():
    plan = _plan_v1_1(stance=False)
    plan["authorized_content_classes"] = [
        "accepted_search_query",
        "claim_and_selected_evidence_to_stance_provider",
    ]
    plan["plan_sha256"] = ledger.bound_digest(plan, "plan_sha256")
    with pytest.raises(ledger.LedgerError, match="authorized_content_classes"):
        ledger.validate_plan(plan)


def test_v1_0_plans_cannot_smuggle_stance_fields():
    plan = _plan_v1_0()
    plan["stance_plan"] = copy.deepcopy(STANCE_PLAN)
    with pytest.raises(ledger.LedgerError, match="schema"):
        ledger.validate_schema(
            plan, ledger.plan_schema_filename(plan), "query plan"
        )


def test_builder_finalizes_under_a_v1_1_plan():
    plan = _plan_v1_1(stance=True)
    retained = json.loads(
        (FIXTURES / "retrieval_input.json").read_text(encoding="utf-8")
    )
    retained["query_plan_sha256"] = plan["plan_sha256"]
    hits = {row["raw_hit_id"]: row for row in retained["raw_hits"]}
    for assessment in retained["relevance_assessments"]:
        hit = hits[assessment["canonical_raw_hit_id"]]
        projection = ledger.relevance_assessment_input_projection(
            plan, hit, assessment
        )
        prompt = ledger.render_relevance_prompt(projection)
        assessment["assessment_input_sha256"] = ledger.digest(projection)
        assessment["prompt_utf8"] = prompt
        assessment["prompt_sha256"] = ledger.text_digest(prompt)
    retained["retrieval_input_sha256"] = ledger.bound_digest(
        retained, "retrieval_input_sha256"
    )
    result = ledger.build_ledger(plan, retained)
    assert result["query_plan_sha256"] == plan["plan_sha256"]


def test_discovery_accepts_a_v1_1_plan(tmp_path):
    plan = _plan_v1_1(stance=True)
    plan["provider_roster"] = [
        discovery.provider_roster_defaults()["semantic_scholar"]
    ]
    plan["queries"] = plan["queries"][:1]
    plan["queries"][0]["index_targets"] = ["semantic_scholar"]
    plan["queries"][0]["date_filter"] = {"from_year": None, "through_year": None}
    _rehash(plan)
    body = json.dumps(
        {
            "total": 1,
            "data": [
                {
                    "paperId": "s2paper1",
                    "title": "Synthetic S2 result",
                    "abstract": "Synthetic abstract describing the finding.",
                    "year": 2022,
                    "authors": [{"name": "Author S1"}],
                    "externalIds": {"DOI": "10.5555/s2-1"},
                    "publicationTypes": ["JournalArticle"],
                    "url": "https://example.org/s2/1",
                }
            ],
        }
    ).encode("utf-8")

    def transport(url, headers, timeout):
        return 200, body

    retained = discovery.retrieve(plan, transport=transport)
    assert retained["query_plan_sha256"] == plan["plan_sha256"]
    assert retained["attempts"][0]["outcome"] == "success"


# --- stance record and evidence-row instances --------------------------------


def _valid_stance_record() -> dict:
    return {
        "schema_version": "claim-standing-stance-record/1.0",
        "probe_id": "probe-655-fixture",
        "unmeasured_banner": "STANCE CLASSIFICATION UNMEASURED",
        "advisory_boundary": {
            "layer": "LLM-ADVISORY",
            "gate_effect": "none",
            "read_ledger_effect": "none",
            "manuscript_mutation": "none",
        },
        "identity": {
            "claim_sha256": "a" * 64,
            "consent_receipt_sha256": "b" * 64,
            "query_plan_sha256": "c" * 64,
            "adapter_registry_sha256": "d" * 64,
            "candidate_ledger_sha256": "e" * 64,
            "stance_plan_sha256": "f" * 64,
        },
        "stance_runtime": {
            "provider_identity": "Synthetic Stance Provider",
            "model_identity": "synthetic-stance-model-1",
            "prompt_contract_version": "claim-standing-stance-prompt-1.0",
            "runtime_identity": "offline-test",
        },
        "rows": [
            {
                "work_family_id": "wf-001",
                "canonical_raw_hit_id": "hit-1",
                "check_state": "performed",
                "stance": "support",
                "failure_state": None,
                "conditions_noted": None,
                "evidence_scope": "abstract",
                "evidence_row_refs": [{"row_id": "EVR-CS-1", "row_sha256": "0" * 64}],
                "prompt_sha256": "1" * 64,
                "assessment_input_sha256": "2" * 64,
                "raw_output": "support",
                "raw_output_sha256": "3" * 64,
                "rationale": "The abstract reports the same direction.",
                "assessed_at": "2026-08-14T00:00:00Z",
            }
        ],
        "distribution": {
            "denominator": "all_selected_work_families",
            "selected_total": 1,
            "support": 1,
            "contradict": 0,
            "mixed": 0,
            "not_addressed": 0,
            "INSUFFICIENT_EVIDENCE": 0,
            "AMBIGUOUS": 0,
            "not_checked": 0,
        },
        "completed_at": "2026-08-14T00:00:00Z",
        "stance_record_sha256": "9" * 64,
    }


def test_stance_record_schema_accepts_a_valid_record():
    schema = _schema("claim_standing/stance_record.schema.json")
    Draft202012Validator(schema).validate(_valid_stance_record())


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.__setitem__("unmeasured_banner", "measured"),
        lambda r: r["rows"][0].__setitem__("evidence_row_refs", []),
        lambda r: r["rows"][0].__setitem__("stance", None),
        lambda r: r["rows"][0].update(
            evidence_scope="metadata_only"
        ),
        lambda r: r["rows"][0].__setitem__("raw_output", None),
        lambda r: r.__setitem__("extra_score", 0.9),
    ],
)
def test_stance_record_schema_rejects_contract_violations(mutate):
    schema = _schema("claim_standing/stance_record.schema.json")
    record = _valid_stance_record()
    mutate(record)
    assert not Draft202012Validator(schema).is_valid(record)
