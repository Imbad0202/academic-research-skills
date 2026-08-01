#!/usr/bin/env python3
"""Deterministic venue-track contract coverage for issue #615."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from venue_disclosure_contract_harness import (
    ALL_CATEGORIES,
    ALL_OPERATIONS,
    ALL_OUTCOMES,
    ALL_TARGETS,
    Fact,
    UseRecord,
    evaluate,
    known,
    surface_sync_errors,
    unknown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_CHECKER = REPO_ROOT / "scripts" / "check_venue_disclosure_policies.py"
POLICIES = "academic-paper/references/venue_disclosure_policies.md"
PROTOCOL = "academic-paper/references/disclosure_mode_protocol.md"


def _categories(**updates: str) -> dict[str, str]:
    values = {name: "NOT_USED" for name in ALL_CATEGORIES}
    values.update(updates)
    return values


def _record(
    record_id: str = "use-1",
    *,
    tool: str = "ExampleAI",
    task: str = "draft-1",
    artifact: str = "manuscript.md",
    category: str = "DRAFTING_ASSISTANCE",
    operations: tuple[str, ...] = ("SUBSTANTIVELY_DRAFTED",),
    targets: tuple[str, ...] = ("METHODS",),
    research_use: bool = False,
    facts: dict[str, Fact] | None = None,
) -> UseRecord:
    bound = {
        name: value if value.owner is not None else Fact(value.state, value.value, record_id)
        for name, value in (facts or {}).items()
    }
    return UseRecord(
        record_id=record_id,
        tool=tool,
        task=task,
        artifact=artifact,
        category=category,
        operations=operations,
        targets=targets,
        research_use=research_use,
        facts=bound,
    )


def _base_case(
    venue: str,
    records: tuple[UseRecord, ...] = (),
    *,
    categories: dict[str, str] | None = None,
    global_facts: dict[str, Fact] | None = None,
) -> dict[str, object]:
    facts = {
        "external_use_inventory_confirmed": known("list supplied" if records else "none"),
        "ai_listed_or_proposed_as_author": known(False),
    }
    facts.update(global_facts or {})
    return {
        "venue": venue,
        "categories": categories or _categories(
            **({records[0].category: "USED"} if records else {})
        ),
        "records": records,
        "global_facts": facts,
    }


def _iclrfacts() -> dict[str, Fact]:
    return {
        "specific_assisted_tasks": known("checked source-to-claim alignment"),
        "author_accepts_full_responsibility": known(True),
        "affected_content": known("reference list and linked claims"),
    }


def _jama_facts(*, llm: bool, included: bool = False, protected_input: bool = False) -> dict[str, Fact]:
    facts = {
        "author_review_accuracy": known(True),
        "author_accepts_content_integrity_responsibility": known(True),
        "model_or_tool_version": known("2.1"),
        "extension_numbers_applicable": known(False),
        "manufacturer": known("Example Labs"),
        "dates_of_use": known("2026-07-30"),
        "use_description": known("assisted the registered analysis"),
        "affected_portions": known("Methods"),
        "specific_research_use": known("classified preregistered records"),
        "study_uses_llm": known(llm),
        "copyright_protected_content_entered": known(protected_input),
        "ai_generated_content_included_in_submission": known(included),
    }
    if llm:
        facts.update({
            "llm_prompts": known(("classify record", "explain exclusion")),
            "llm_prompt_sequence": known((1, 2)),
            "llm_prompt_revisions": known("second prompt narrowed the date range"),
        })
    if protected_input:
        facts.update({
            "copyright_permission_copy": known("permissions/input-license.pdf"),
            "copyright_permission_methods_description": known("licensed corpus under agreement 7"),
        })
    if included:
        facts.update({
            "included_content_type": known("supplementary classification table"),
            "publication_rights_basis": known("service terms grant publication rights"),
        })
    return facts


def _ies_facts(*, data: bool, clinical: bool = False) -> dict[str, Fact]:
    facts = {
        "policy_tool_scope": known("GENAI_OR_AIGC"),
        "use_scope": known("OTHER_CONFIRMED_NON_CORE_RESEARCH_STEP"),
        "use_scope_basis": known("terminology harmonization after analysis"),
        "tool_is_overseas": known(False),
        "generated_core_main_text_conclusion_analysis_viewpoint_or_innovation_claim": known(False),
        "fabricated_experimental_plan_technical_route_or_citation": known(False),
        "replaced_author_in_experimental_design_or_data_validation": known(False),
        "fabricated_data_invented_results_or_tampered_conclusions": known(False),
        "rewrote_plagiarized_work_to_evade_detection": known(False),
        "generated_peer_review_response_grant_contribution_or_integrity_statement": known(False),
        "uploaded_secret_research_data_or_unpublished_results_to_public_ai_platform": known(False),
        "use_involves_data": known(data),
        "aigc_generated_or_tampered_data": known(False),
        "aigc_replaced_core_analysis": known(False),
        "uploaded_undeidentified_data_to_aigc": known(False),
        "uploaded_data_lacking_required_ethics_review_to_aigc": known(False),
        "fabricated_data_or_ethics_proof": known(False),
        "version": known("2026.7"),
        "purpose": known("terminology harmonization"),
        "generated_proportion": known("8%"),
    }
    if data:
        facts.update({
            "data_types": known(("coded outcome labels",)),
            "data_verification_status": known("dual human verification complete"),
            "data_involves_clinical_or_case_data": known(clinical),
        })
    if clinical:
        facts["de_identification_measures"] = known("direct identifiers removed before use")
    return facts


def _frontiers_facts(*, represents_data: bool | None, created: bool = True) -> dict[str, Fact]:
    return {
        "policy_tool_scope": known("GENAI_OR_AIGC"),
        "version": known("4.2"),
        "model": known("Example Vision"),
        "source_provider": known("Example Labs"),
        "content_operation": known("CREATED" if created else "EDITED"),
        "affected_content_kind": known("VISUAL"),
        "affected_content": known("Figure 2 conceptual workflow"),
        "figure_represents_data": unknown() if represents_data is None else known(represents_data),
    }


def _lancet_common() -> dict[str, Fact]:
    return {
        "ai_replaced_authors_intellectual_contribution": known(False),
        "generated_media_duplicates_or_refers_to_protected_subject": known(False),
        "visual_accuracy_confirmed": known(True),
        "visual_originality_confirmed": known(True),
        "based_on_existing_artwork_or_graphics": known(False),
    }


def _copy_contract_tree(tmp_path: Path) -> Path:
    rels = (
        POLICIES,
        PROTOCOL,
        "academic-paper/SKILL.md",
        "commands/ars-disclosure.md",
        "academic-paper/references/mode_selection_guide.md",
        "README.md",
        "README.ja-JP.md",
        "README.ko-KR.md",
        "README.zh-CN.md",
        "README.zh-TW.md",
    )
    for rel in rels:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / rel, dst)
    return tmp_path


def _mutate(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"missing mutation anchor: {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# Static database and vocabulary regression coverage.


def test_existing_15_venue_structural_checker_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(POLICY_CHECKER)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("mutation", ("field-deletion", "ordering-drift"))
def test_existing_structural_checker_rejects_mutations(tmp_path: Path, mutation: str) -> None:
    policies = tmp_path / "policies.md"
    shutil.copy(REPO_ROOT / POLICIES, policies)
    text = policies.read_text(encoding="utf-8")
    if mutation == "field-deletion":
        text = text.replace("| Authorship rule |", "| Removed field |", 1)
    else:
        acl = text.index("## Venue: ACL")
        bmj = text.index("## Venue: BMJ")
        chinese = text.index("## Venue: Chinese Nursing", bmj)
        first = text[acl:bmj]
        second = text[bmj:chinese]
        text = text[:acl] + second + first + text[chinese:]
    policies.write_text(text, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(POLICY_CHECKER), str(policies)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1


def test_closed_vocabulary_matches_protocol() -> None:
    protocol = (REPO_ROOT / PROTOCOL).read_text(encoding="utf-8")
    for token in ALL_OUTCOMES | ALL_OPERATIONS | ALL_TARGETS:
        assert f"`{token}`" in protocol
    for label in (
        "Citation checking",
        "Other / unclassified AI use (logged or external)",
    ):
        assert label in protocol


def test_selector_and_user_surfaces_are_in_sync() -> None:
    assert surface_sync_errors(REPO_ROOT) == []


def test_selector_surface_drift_is_detected(tmp_path: Path) -> None:
    tree = _copy_contract_tree(tmp_path)
    _mutate(
        tree,
        "commands/ars-disclosure.md",
        " / journal-level 国际眼科杂志",
        "",
    )
    assert any("ars-disclosure.md" in error for error in surface_sync_errors(tree))


# Intake, dispatch, halt, and four-outcome fixtures.


def test_citation_checking_is_a_first_class_used_category() -> None:
    record = _record(
        category="CITATION_CHECKING",
        operations=("CHECKED_CITATIONS",),
        targets=("REFERENCE_OR_CITATION",),
        facts=_iclrfacts(),
    )
    result = evaluate(_base_case("ICLR", (record,), categories=_categories(CITATION_CHECKING="USED")))
    assert (result.outcome, result.execution_status) == ("REQUIRED", "READY")
    assert result.ledger[record.record_id]["specific_assisted_tasks"].value


def test_unknown_external_inventory_halts_before_categorization() -> None:
    case = _base_case("ICLR")
    case["global_facts"]["external_use_inventory_confirmed"] = unknown()  # type: ignore[index]
    result = evaluate(case)
    assert (result.outcome, result.execution_status, result.halt_reason) == (
        "UNKNOWN", "HALTED", "UNRESOLVED_INPUT"
    )
    assert "Phase 2a" not in result.phases


def test_used_other_unclassified_is_preserved_and_halted() -> None:
    record = _record(
        category="OTHER_UNCLASSIFIED",
        operations=("OTHER_CONFIRMED",),
        targets=("OTHER_CONFIRMED",),
        facts={"verbatim_description": known("AI sorted an uncategorized submission object")},
    )
    result = evaluate(
        _base_case("ICLR", (record,), categories=_categories(OTHER_UNCLASSIFIED="USED"))
    )
    assert result.outcome == "UNKNOWN"
    assert result.halt_reason == "UNRESOLVED_INPUT"
    assert "AI sorted an uncategorized submission object" in result.diagnostics[0]


def test_unknown_venue_never_falls_back_or_emits_placeholders() -> None:
    result = evaluate(_base_case("Imaginary Journal"))
    assert (result.outcome, result.execution_status, result.halt_reason) == (
        "UNKNOWN", "HALTED", "UNCURATED_POLICY"
    )
    rendered = " ".join(block.text for block in result.blocks)
    assert result.blocks == ()
    assert "generic" not in rendered.casefold()
    assert "[" not in rendered


def test_all_four_outcomes_are_exercised() -> None:
    required = evaluate(
        _base_case(
            "ICLR",
            (_record(facts=_iclrfacts()),),
            categories=_categories(DRAFTING_ASSISTANCE="USED"),
        )
    )
    not_required = evaluate(_base_case("ICLR"))
    unknown_result = evaluate(_base_case("Unknown Venue"))
    cover_facts = _lancet_common() | {
        "artifact_class": known("COVER_ART"),
        "editor_permission": known(True),
        "publisher_permission": known(True),
        "cover_art_contains_third_party_material": known(False),
        "content_attribution": known("none_applicable"),
    }
    action_only = evaluate(
        _base_case(
            "The Lancet",
            (_record(category="VISUAL_ARTWORK_MEDIA_ASSISTANCE", operations=("GENERATED",), targets=("RESEARCH_FIGURE_OR_MEDIA",), facts=cover_facts),),
            categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED"),
        )
    )
    assert {required.outcome, not_required.outcome, unknown_result.outcome, action_only.outcome} == ALL_OUTCOMES
    assert action_only.blocks == ()
    assert "editor permission" in " ".join(action_only.actions).casefold()


def test_unknown_required_fact_and_incompatible_confirmed_fact_halt_before_render() -> None:
    missing = _record(facts=_iclrfacts() | {"author_accepts_full_responsibility": unknown()})
    incompatible = _record(facts=_iclrfacts() | {"author_accepts_full_responsibility": known(False)})
    missing_result = evaluate(_base_case("ICLR", (missing,), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    incompatible_result = evaluate(_base_case("ICLR", (incompatible,), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert (missing_result.outcome, missing_result.halt_reason, missing_result.blocks) == (
        "REQUIRED", "UNRESOLVED_INPUT", ()
    )
    assert (incompatible_result.outcome, incompatible_result.halt_reason, incompatible_result.blocks) == (
        "REQUIRED", "INCOMPATIBLE_FACT", ()
    )


def test_policy_anchor_never_enters_venue_phases() -> None:
    result = evaluate({"policy_anchor": "icmje", "categories": _categories(), "records": (), "global_facts": {"external_use_inventory_confirmed": known("none")}})
    assert result.track == "anchor"
    assert all(not phase.startswith("Venue Phase") for phase in result.phases)
    assert result.outcome is None


def test_nature_consistent_dual_selector_routes_to_anchor() -> None:
    result = evaluate({"venue": "Nature Medicine", "policy_anchor": "nature", "categories": _categories(), "records": (), "global_facts": {"external_use_inventory_confirmed": known("none")}})
    assert result.track == "anchor"
    assert "Venue Phase 2a" not in result.phases


def test_multi_placement_blocks_are_distinct_and_purpose_specific() -> None:
    facts = {
        "ai_generated_material_used_as_primary_source": known(False),
        "human_review_editing_performed": known(True),
        "no_plagiarism_confirmed": known(True),
        "technology_description": known("ExampleAI 2.1"),
        "produced_content": known("citation verification notes"),
    }
    record = _record(category="CITATION_CHECKING", operations=("CHECKED_CITATIONS",), targets=("REFERENCE_OR_CITATION",), facts=facts)
    result = evaluate(_base_case("NEJM", (record,), categories=_categories(CITATION_CHECKING="USED")))
    assert [block.placement for block in result.blocks] == ["COVER_LETTER", "SUBMITTED_WORK"]
    assert len({block.text for block in result.blocks}) == 2
    assert len({block.purpose for block in result.blocks}) == 2


# Record binding and venue-specific fixtures from the accepted #599 vocabulary.


def test_per_record_facts_cannot_be_borrowed_across_tools_or_figures() -> None:
    first = _record("figure-1", artifact="figure-1.png", facts=_frontiers_facts(represents_data=False))
    borrowed = _frontiers_facts(represents_data=True)
    borrowed["model"] = Fact("KNOWN", "Example Vision", "figure-1")
    second = _record("figure-2", artifact="figure-2.png", facts=borrowed)
    result = evaluate(
        _base_case(
            "Frontiers",
            (first, second),
            categories=_categories(DRAFTING_ASSISTANCE="USED"),
        )
    )
    assert result.execution_status == "HALTED"
    assert result.halt_reason == "UNRESOLVED_INPUT"
    assert "cross-record" in " ".join(result.diagnostics)


@pytest.mark.parametrize(
    ("represents_data", "expected", "absent"),
    (
        (False, {"factual accuracy", "plagiarism-free"}, "accuracy to data"),
        (True, {"factual accuracy", "plagiarism-free", "accuracy to data"}, ""),
    ),
)
def test_frontiers_conceptual_vs_data_figure_actions(
    represents_data: bool, expected: set[str], absent: str
) -> None:
    record = _record(
        category="VISUAL_ARTWORK_MEDIA_ASSISTANCE",
        operations=("GENERATED",),
        targets=("RESEARCH_FIGURE_OR_MEDIA",),
        facts=_frontiers_facts(represents_data=represents_data),
    )
    result = evaluate(_base_case("Frontiers", (record,), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED")))
    actions = " ".join(result.actions).casefold()
    assert result.execution_status == "READY"
    assert all(item in actions for item in expected)
    if absent:
        assert absent not in actions


def test_frontiers_unknown_data_routing_is_outstanding_not_halted() -> None:
    record = _record(
        category="VISUAL_ARTWORK_MEDIA_ASSISTANCE",
        operations=("EDITED",),
        targets=("RESEARCH_FIGURE_OR_MEDIA",),
        facts=_frontiers_facts(represents_data=None, created=False),
    )
    result = evaluate(_base_case("Frontiers", (record,), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED")))
    assert result.execution_status == "READY"
    assert "resolve figure_represents_data" in result.actions
    assert "accuracy to data" not in " ".join(result.actions).casefold()


def test_frontiers_missing_model_or_source_halts() -> None:
    facts = _frontiers_facts(represents_data=False)
    facts["source_provider"] = unknown()
    record = _record(facts=facts)
    result = evaluate(_base_case("Frontiers", (record,), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert (result.execution_status, result.halt_reason) == ("HALTED", "UNRESOLVED_INPUT")


def test_frontiers_mixed_genai_and_other_ai_scope_halts_without_partial_bundle() -> None:
    genai = _record("genai", facts=_frontiers_facts(represents_data=False))
    other_facts = _frontiers_facts(represents_data=False)
    other_facts["policy_tool_scope"] = known("OTHER_AI")
    other = _record("other-ai", tool="Classifier", task="screen", facts=other_facts)
    result = evaluate(_base_case("Frontiers", (genai, other), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert (result.outcome, result.halt_reason, result.blocks) == (
        "UNKNOWN", "POLICY_SCOPE_GAP", ()
    )


def test_jama_non_llm_study_requires_date_and_rights_but_not_prompt_history() -> None:
    facts = _jama_facts(llm=False, included=True, protected_input=True) | {
        "jama_submission_type": known("ORIGINAL_INVESTIGATION"),
        "jama_submission_type_is_prohibited": known(False),
    }
    record = _record(research_use=True, facts=facts)
    result = evaluate(_base_case("JAMA", (record,), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert result.execution_status == "READY"
    ledger = result.ledger[record.record_id]
    assert ledger["dates_of_use"].value == "2026-07-30"
    assert ledger["llm_prompts"].state == "NOT_APPLICABLE"
    assert ledger["copyright_permission_copy"].value.endswith(".pdf")
    assert ledger["publication_rights_basis"].value


def test_jama_llm_study_requires_prompt_sequence_and_revisions() -> None:
    facts = _jama_facts(llm=True) | {
        "jama_submission_type": known("ORIGINAL_INVESTIGATION"),
        "jama_submission_type_is_prohibited": known(False),
    }
    record = _record(research_use=True, facts=facts)
    result = evaluate(_base_case("JAMA", (record,), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert result.execution_status == "READY"
    assert result.ledger[record.record_id]["llm_prompt_sequence"].value == (1, 2)


def test_conditional_children_are_not_applicable_only_after_explicit_false_parent() -> None:
    facts = _jama_facts(llm=False)
    facts.update({
        "jama_submission_type": known("ORIGINAL_INVESTIGATION"),
        "jama_submission_type_is_prohibited": known(False),
    })
    ready = evaluate(_base_case("JAMA", (_record(research_use=True, facts=facts),), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert ready.ledger["use-1"]["llm_prompt_sequence"].state == "NOT_APPLICABLE"
    facts["study_uses_llm"] = unknown()
    halted = evaluate(_base_case("JAMA", (_record(research_use=True, facts=facts),), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert halted.execution_status == "HALTED"
    assert "llm_prompt_sequence" not in halted.ledger.get("use-1", {}) or halted.ledger["use-1"]["llm_prompt_sequence"].state != "NOT_APPLICABLE"


def test_jama_prohibited_manuscript_class_halts_as_known_prohibited_use() -> None:
    facts = _jama_facts(llm=False) | {
        "jama_submission_type": known("POETRY"),
        "jama_submission_type_is_prohibited": known(True),
    }
    record = _record(research_use=False, facts=facts)
    result = evaluate(_base_case("JAMA", (record,), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert (result.outcome, result.halt_reason) == ("REQUIRED", "PROHIBITED_USE")


def test_international_eye_science_non_core_data_and_deidentification_fields() -> None:
    record = _record(
        category="ANALYSIS_ASSISTANCE",
        operations=("ANALYSED",),
        targets=("ORIGINAL_RESEARCH_DATA",),
        research_use=True,
        facts=_ies_facts(data=True, clinical=True),
    )
    result = evaluate(_base_case("International Eye Science", (record,), categories=_categories(ANALYSIS_ASSISTANCE="USED")))
    assert result.execution_status == "READY"
    ledger = result.ledger[record.record_id]
    assert ledger["generated_proportion"].value == "8%"
    assert ledger["data_types"].value == ("coded outcome labels",)
    assert ledger["data_verification_status"].value
    assert ledger["de_identification_measures"].value


def test_international_eye_science_other_ai_only_and_mixed_halt_as_scope_gap() -> None:
    genai = _record("genai", facts=_ies_facts(data=False))
    other_facts = _ies_facts(data=False)
    other_facts["policy_tool_scope"] = known("OTHER_AI")
    other = _record("other", facts=other_facts)
    for records in ((other,), (genai, other)):
        result = evaluate(_base_case("International Eye Science", records, categories=_categories(DRAFTING_ASSISTANCE="USED")))
        assert (result.outcome, result.halt_reason, result.blocks) == (
            "UNKNOWN", "POLICY_SCOPE_GAP", ()
        )


def test_chinese_nursing_scientific_contribution_hard_prohibition() -> None:
    facts = {
        "policy_tool_scope": known("GENAI_OR_AIGC"),
        "ai_performed_scientific_or_intellectual_contribution": known(True),
        "generated_research_figure_or_media": known(False),
        "altered_original_research_data_process_or_results": known(False),
        "used_unverified_genai_reference": known(False),
    }
    record = _record(facts=facts)
    result = evaluate(_base_case("Chinese Nursing Journals Publishing House", (record,), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert result.halt_reason == "PROHIBITED_USE"


def test_chinese_nursing_confirmed_non_core_use_reaches_render() -> None:
    facts = {
        "policy_tool_scope": known("GENAI_OR_AIGC"),
        "ai_performed_scientific_or_intellectual_contribution": known(False),
        "generated_research_figure_or_media": known(False),
        "altered_original_research_data_process_or_results": known(False),
        "used_unverified_genai_reference": known(False),
        "purpose": known("surface-level terminology consistency"),
        "affected_content": known("non-scientific submission metadata"),
        "human_review_editing_performed": known(True),
        "author_accepts_full_responsibility": known(True),
    }
    record = _record(
        category="EDITING_ASSISTANCE",
        operations=("EDITED",),
        targets=("OTHER_SUBMISSION_TEXT",),
        facts=facts,
    )
    result = evaluate(
        _base_case(
            "Chinese Nursing Journals Publishing House",
            (record,),
            categories=_categories(EDITING_ASSISTANCE="USED"),
        )
    )
    assert (result.outcome, result.execution_status) == ("REQUIRED", "READY")


def test_nature_venue_image_is_contained_before_phase2b() -> None:
    record = _record(category="VISUAL_ARTWORK_MEDIA_ASSISTANCE", operations=("GENERATED",), targets=("RESEARCH_FIGURE_OR_MEDIA",))
    result = evaluate(_base_case("Nature", (record,), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED")))
    assert (result.outcome, result.halt_reason) == ("UNKNOWN", "CONTRACT_GAP")
    assert "Venue Phase 2b" not in result.phases
    assert "NATURE_VENUE_IMAGE_CONTAINMENT" in result.diagnostics


@pytest.mark.parametrize(
    ("venue", "facts", "target"),
    (
        ("ICMJE", {"ai_generated_material_used_as_primary_source": known(True), "ai_cited_as_author": known(False)}, "REFERENCE_OR_CITATION"),
        ("NEJM", {"ai_generated_material_used_as_primary_source": known(True)}, "REFERENCE_OR_CITATION"),
        ("PLOS", {"ai_fabricated_or_misrepresented_primary_research_data": known(True)}, "ORIGINAL_RESEARCH_DATA"),
    ),
)
def test_western_hard_prohibitions_halt(venue: str, facts: dict[str, Fact], target: str) -> None:
    record = _record(category="CITATION_CHECKING", operations=("CHECKED_CITATIONS",), targets=(target,), facts=facts)
    result = evaluate(_base_case(venue, (record,), categories=_categories(CITATION_CHECKING="USED")))
    assert result.halt_reason == "PROHIBITED_USE"


def test_icmje_member_venue_gets_separate_advisory_without_channel_merge() -> None:
    facts = {
        "technology_description": known("ExampleAI"),
        "why_used": known("draft organization"),
        "how_used": known("outlined the discussion"),
    }
    record = _record(facts=facts)
    result = evaluate(_base_case("BMJ", (record,), categories=_categories(DRAFTING_ASSISTANCE="USED")))
    assert result.execution_status == "READY"
    assert "ICMJE-alongside advisory" in result.advisories
    assert all(block.purpose != "ICMJE-alongside advisory" for block in result.blocks)


def test_lancet_graphical_abstract_uses_dedicated_caption_path() -> None:
    facts = _lancet_common() | {
        "artifact_class": known("GRAPHICAL_ABSTRACT"),
        "graphical_abstract_used_ai_or_ai_assisted_illustration": known(True),
        "graphical_abstract_tool_class": known("DEDICATED_SCIENTIFIC_OR_PROFESSIONAL_ILLUSTRATION_TOOL"),
        "publication_rights_basis": known("tool terms grant publication rights"),
    }
    record = _record(category="VISUAL_ARTWORK_MEDIA_ASSISTANCE", operations=("GENERATED",), targets=("RESEARCH_FIGURE_OR_MEDIA",), facts=facts)
    result = evaluate(_base_case("The Lancet", (record,), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED")))
    assert result.execution_status == "READY"
    assert [block.placement for block in result.blocks] == ["GRAPHICAL_ABSTRACT_CAPTION"]


def test_lancet_general_purpose_graphical_abstract_tool_is_prohibited() -> None:
    facts = _lancet_common() | {
        "artifact_class": known("GRAPHICAL_ABSTRACT"),
        "graphical_abstract_used_ai_or_ai_assisted_illustration": known(True),
        "graphical_abstract_tool_class": known("GENERAL_PURPOSE_GENERATIVE_AI_IMAGE_TOOL"),
    }
    record = _record(category="VISUAL_ARTWORK_MEDIA_ASSISTANCE", operations=("GENERATED",), targets=("RESEARCH_FIGURE_OR_MEDIA",), facts=facts)
    result = evaluate(_base_case("The Lancet", (record,), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED")))
    assert result.halt_reason == "PROHIBITED_USE"


def test_lancet_primary_image_vs_research_method_paths() -> None:
    common = _lancet_common() | {"artifact_class": known("PRIMARY_RESEARCH_IMAGE")}
    primary = common | {
        "ai_is_formal_research_design_or_method": known(False),
        "image_output_directly_obtained_in_research_through_that_method": known(False),
    }
    prohibited = evaluate(_base_case("The Lancet", (_record(category="VISUAL_ARTWORK_MEDIA_ASSISTANCE", operations=("GENERATED",), targets=("RESEARCH_FIGURE_OR_MEDIA",), facts=primary),), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED")))
    assert prohibited.halt_reason == "PROHIBITED_USE"

    method = _lancet_common() | {
        "artifact_class": known("RESEARCH_METHOD_IMAGE"),
        "ai_is_formal_research_design_or_method": known(True),
        "image_output_directly_obtained_in_research_through_that_method": known(True),
        "reproducible_method_details": known("registered segmentation pipeline and seed"),
        "model_or_tool_version": known("3.0"),
        "developer_or_manufacturer_applicable": known(True),
        "developer_or_manufacturer": known("Example Labs"),
    }
    ready = evaluate(_base_case("The Lancet", (_record(category="VISUAL_ARTWORK_MEDIA_ASSISTANCE", operations=("GENERATED",), targets=("RESEARCH_FIGURE_OR_MEDIA",), facts=method),), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED")))
    assert ready.execution_status == "READY"
    assert [block.placement for block in ready.blocks] == ["METHODS"]


def test_lancet_protected_subject_halts_before_visual_classification() -> None:
    facts = _lancet_common() | {
        "generated_media_duplicates_or_refers_to_protected_subject": known(True),
    }
    record = _record(category="VISUAL_ARTWORK_MEDIA_ASSISTANCE", operations=("GENERATED",), targets=("RESEARCH_FIGURE_OR_MEDIA",), facts=facts)
    result = evaluate(_base_case("The Lancet", (record,), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED")))
    assert result.halt_reason == "PROHIBITED_USE"
    assert "artifact_class" not in result.ledger.get(record.record_id, {})


def test_lancet_cover_art_permission_missing_halts_and_mixed_use_is_required() -> None:
    cover = _lancet_common() | {
        "artifact_class": known("COVER_ART"),
        "editor_permission": known(True),
        "publisher_permission": known(False),
        "cover_art_contains_third_party_material": known(False),
        "content_attribution": known("none_applicable"),
    }
    cover_record = _record("cover", category="VISUAL_ARTWORK_MEDIA_ASSISTANCE", operations=("GENERATED",), targets=("RESEARCH_FIGURE_OR_MEDIA",), facts=cover)
    halted = evaluate(_base_case("The Lancet", (cover_record,), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED")))
    assert halted.halt_reason == "INCOMPATIBLE_FACT"

    cover["publisher_permission"] = known(True)
    cover_record = _record("cover", category="VISUAL_ARTWORK_MEDIA_ASSISTANCE", operations=("GENERATED",), targets=("RESEARCH_FIGURE_OR_MEDIA",), facts=cover)
    prep = _lancet_common() | {
        "tool_service_name": known("ExampleAI"),
        "purpose": known("language revision"),
        "extent_of_human_oversight": known("sentence-level review"),
        "author_reviewed_and_edited": known(True),
        "author_accepts_full_responsibility": known(True),
    }
    prep_record = _record("prep", facts=prep)
    mixed = evaluate(_base_case("The Lancet", (cover_record, prep_record), categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED", DRAFTING_ASSISTANCE="USED")))
    assert mixed.outcome == "REQUIRED"
    assert mixed.blocks
    assert "editor permission" in " ".join(mixed.actions).casefold()


@pytest.mark.parametrize(
    ("mutated_fact", "replacement", "expected_reason"),
    (
        ("editor_permission", known(False), "INCOMPATIBLE_FACT"),
        ("publisher_permission", known(False), "INCOMPATIBLE_FACT"),
        ("third_party_material_permission", unknown(), "UNRESOLVED_INPUT"),
        ("rights_holder_permission", unknown(), "UNRESOLVED_INPUT"),
    ),
)
def test_lancet_permission_failures_always_halt(
    mutated_fact: str, replacement: Fact, expected_reason: str
) -> None:
    facts = _lancet_common() | {
        "artifact_class": known("COVER_ART"),
        "editor_permission": known(True),
        "publisher_permission": known(True),
        "cover_art_contains_third_party_material": known(True),
        "third_party_material_permission": known("license/third-party.pdf"),
        "content_attribution": known("artist and source credited"),
        "based_on_existing_artwork_or_graphics": known(True),
        "rights_holder_permission": known("license/source-art.pdf"),
        "existing_artwork_attribution": known("source artist credited"),
    }
    facts[mutated_fact] = replacement
    record = _record(
        category="VISUAL_ARTWORK_MEDIA_ASSISTANCE",
        operations=("GENERATED",),
        targets=("RESEARCH_FIGURE_OR_MEDIA",),
        facts=facts,
    )
    result = evaluate(
        _base_case(
            "The Lancet",
            (record,),
            categories=_categories(VISUAL_ARTWORK_MEDIA_ASSISTANCE="USED"),
        )
    )
    assert (result.execution_status, result.halt_reason, result.blocks) == (
        "HALTED",
        expected_reason,
        (),
    )
