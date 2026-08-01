#!/usr/bin/env python3
"""Deterministic test oracle for the venue disclosure contract.

This module exists only to exercise the documentation-owned contract in CI.  It
is deliberately not imported by the disclosure runtime and is not a general
submission-policy engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping
import re


ALL_OUTCOMES = frozenset({"REQUIRED", "ACTION_ONLY", "NOT_REQUIRED", "UNKNOWN"})
ALL_CATEGORIES = frozenset(
    {
        "RESEARCH_ASSISTANCE",
        "CITATION_CHECKING",
        "DRAFTING_ASSISTANCE",
        "REVISION_ASSISTANCE",
        "EDITING_ASSISTANCE",
        "ANALYSIS_ASSISTANCE",
        "VISUAL_ARTWORK_MEDIA_ASSISTANCE",
        "PEER_REVIEW_SIMULATION",
        "OTHER_UNCLASSIFIED",
    }
)
ALL_OPERATIONS = frozenset(
    {
        "GENERATED",
        "SUBSTANTIVELY_DRAFTED",
        "EDITED",
        "ANALYSED",
        "SEARCHED",
        "CHECKED_CITATIONS",
        "FORMATTED_CITATIONS",
        "OTHER_CONFIRMED",
    }
)
ALL_TARGETS = frozenset(
    {
        "WHOLE_PAPER",
        "TITLE",
        "ABSTRACT",
        "INTRODUCTION_OR_BACKGROUND",
        "METHODS",
        "RESULTS",
        "DISCUSSION",
        "CONCLUSION",
        "RESULT_INTERPRETATION",
        "CORE_ARGUMENT",
        "INNOVATION_CLAIM",
        "RESEARCH_FIGURE_OR_MEDIA",
        "ORIGINAL_RESEARCH_DATA",
        "RESEARCH_PROCESS",
        "SUPPORTING_DATA_FILE",
        "REFERENCE_OR_CITATION",
        "CODE",
        "PEER_REVIEW_MATERIAL",
        "OTHER_SUBMISSION_TEXT",
        "OTHER_CONFIRMED",
    }
)

CANONICAL_VENUES = (
    "ACL",
    "BMJ",
    "Chinese Nursing Journals Publishing House",
    "EMNLP",
    "Frontiers",
    "ICLR",
    "ICMJE",
    "International Eye Science",
    "JAMA",
    "Nature",
    "NEJM",
    "NeurIPS",
    "PLOS",
    "Science",
    "The Lancet",
)
ALIASES = {
    "the bmj": "BMJ",
    "中华护理杂志社": "Chinese Nursing Journals Publishing House",
    "frontiers journals": "Frontiers",
    "international committee of medical journal editors": "ICMJE",
    "国际眼科杂志": "International Eye Science",
    "journal of the american medical association": "JAMA",
    "the new england journal of medicine": "NEJM",
    "new england journal of medicine": "NEJM",
    "plos journals": "PLOS",
    "plos one": "PLOS",
    "lancet": "The Lancet",
}
for _venue in CANONICAL_VENUES:
    ALIASES[_venue.casefold()] = _venue

ICMJE_MEMBER_TARGETS = frozenset({"BMJ", "JAMA", "NEJM", "The Lancet"})
AUTHORSHIP_TARGETS = frozenset(set(CANONICAL_VENUES) - {"PLOS"})
SCOPE_TARGETS = frozenset(
    {
        "Chinese Nursing Journals Publishing House",
        "Frontiers",
        "International Eye Science",
    }
)
TEXT_TARGETS = frozenset(
    {
        "WHOLE_PAPER",
        "TITLE",
        "ABSTRACT",
        "INTRODUCTION_OR_BACKGROUND",
        "METHODS",
        "RESULTS",
        "DISCUSSION",
        "CONCLUSION",
        "RESULT_INTERPRETATION",
        "CORE_ARGUMENT",
        "INNOVATION_CLAIM",
        "OTHER_SUBMISSION_TEXT",
    }
)


@dataclass(frozen=True)
class Fact:
    state: str
    value: Any = None
    owner: str | None = None


def known(value: Any, owner: str | None = None) -> Fact:
    return Fact("KNOWN", value, owner)


def unknown(owner: str | None = None) -> Fact:
    return Fact("UNKNOWN", None, owner)


def not_applicable(owner: str | None = None) -> Fact:
    return Fact("NOT_APPLICABLE", None, owner)


@dataclass(frozen=True)
class UseRecord:
    record_id: str
    tool: str
    task: str
    artifact: str
    category: str
    operations: tuple[str, ...]
    targets: tuple[str, ...]
    research_use: bool = False
    facts: Mapping[str, Fact] = field(default_factory=dict)


@dataclass(frozen=True)
class Block:
    placement: str
    purpose: str
    text: str


@dataclass(frozen=True)
class ContractResult:
    track: str
    outcome: str | None
    execution_status: str
    halt_reason: str | None = None
    phases: tuple[str, ...] = ()
    blocks: tuple[Block, ...] = ()
    actions: tuple[str, ...] = ()
    advisories: tuple[str, ...] = ()
    ledger: Mapping[str, Mapping[str, Fact]] = field(default_factory=dict)
    diagnostics: tuple[str, ...] = ()


class _ContractStop(RuntimeError):
    pass


class _Evaluator:
    def __init__(self, case: Mapping[str, object]) -> None:
        self.case = case
        self.track = "venue"
        self.outcome: str | None = None
        self.status = "READY"
        self.halt_reason: str | None = None
        self.phases: list[str] = []
        self.blocks: list[Block] = []
        self.actions: list[str] = []
        self.advisories: list[str] = []
        self.ledger: dict[str, dict[str, Fact]] = {}
        self.diagnostics: list[str] = []
        self.records: tuple[UseRecord, ...] = tuple(case.get("records", ()))  # type: ignore[arg-type]
        self.global_facts: Mapping[str, Fact] = case.get("global_facts", {})  # type: ignore[assignment]
        self.venue: str | None = None

    def result(self) -> ContractResult:
        return ContractResult(
            track=self.track,
            outcome=self.outcome,
            execution_status=self.status,
            halt_reason=self.halt_reason,
            phases=tuple(self.phases),
            blocks=tuple(self.blocks),
            actions=tuple(self.actions),
            advisories=tuple(self.advisories),
            ledger={key: dict(value) for key, value in self.ledger.items()},
            diagnostics=tuple(self.diagnostics),
        )

    def halt(self, outcome: str, reason: str, diagnostic: str) -> None:
        self.outcome = outcome
        self.status = "HALTED"
        self.halt_reason = reason
        self.diagnostics.append(diagnostic)
        self.blocks.clear()
        raise _ContractStop

    def require_global(self, name: str, required_value: object | None = None) -> Fact:
        fact = self.global_facts.get(name, unknown())
        if fact.state != "KNOWN":
            self.halt(self.outcome or "UNKNOWN", "UNRESOLVED_INPUT", f"global fact {name} is UNKNOWN")
        if required_value is not None and fact.value != required_value:
            self.halt(self.outcome or "UNKNOWN", "INCOMPATIBLE_FACT", f"global fact {name} is incompatible")
        return fact

    def require_record(
        self,
        record: UseRecord,
        name: str,
        *,
        required_value: object | None = None,
    ) -> Fact:
        fact = record.facts.get(name, unknown(record.record_id))
        self.ledger.setdefault(record.record_id, {})[name] = fact
        if fact.owner not in {None, record.record_id}:
            self.halt(
                self.outcome or "UNKNOWN",
                "UNRESOLVED_INPUT",
                f"cross-record fact borrowing: {name} for {record.record_id} belongs to {fact.owner}",
            )
        if fact.state != "KNOWN":
            self.halt(self.outcome or "UNKNOWN", "UNRESOLVED_INPUT", f"{record.record_id}.{name} is UNKNOWN")
        if required_value is not None and fact.value != required_value:
            self.halt(
                self.outcome or "UNKNOWN",
                "INCOMPATIBLE_FACT",
                f"{record.record_id}.{name} must be {required_value!r}",
            )
        return fact

    def prohibit_true(self, record: UseRecord, name: str) -> Fact:
        fact = self.require_record(record, name)
        if fact.value is True:
            self.halt(self.outcome or "REQUIRED", "PROHIBITED_USE", f"prohibited predicate true: {record.record_id}.{name}")
        if fact.value is not False:
            self.halt(self.outcome or "REQUIRED", "INCOMPATIBLE_FACT", f"{record.record_id}.{name} is not boolean")
        return fact

    def conditional(
        self,
        record: UseRecord,
        parent: str,
        children: tuple[str, ...],
    ) -> bool:
        fact = self.require_record(record, parent)
        if fact.value is False:
            for child in children:
                supplied = record.facts.get(child)
                if supplied is not None and supplied.state == "KNOWN":
                    self.halt(
                        self.outcome or "REQUIRED",
                        "INCOMPATIBLE_FACT",
                        f"{child} cannot be KNOWN when {parent} is false",
                    )
                self.ledger.setdefault(record.record_id, {})[child] = not_applicable(record.record_id)
            return False
        if fact.value is not True:
            self.halt(self.outcome or "REQUIRED", "INCOMPATIBLE_FACT", f"{parent} is not boolean")
        for child in children:
            self.require_record(record, child)
        return True

    def run(self) -> ContractResult:
        try:
            self._dispatch()
            if self.track == "anchor":
                return self.result()
            self._intake()
            self._phase2a()
            if self.outcome == "ACTION_ONLY":
                self._cover_actions()
                self._member_advisory()
                return self.result()
            if self.outcome == "NOT_REQUIRED":
                self._member_advisory()
                return self.result()
            self._phase2b()
            self._render()
            self._phase5_actions()
            self._member_advisory()
        except _ContractStop:
            pass
        return self.result()

    def _dispatch(self) -> None:
        self.phases.append("Selector dispatch")
        raw_venue = self.case.get("venue")
        raw_anchor = self.case.get("policy_anchor")
        if raw_anchor is not None:
            anchor = str(raw_anchor).casefold()
            venue_text = str(raw_venue).strip() if raw_venue is not None else None
            nature_pair = anchor == "nature" and venue_text is not None and (
                venue_text.casefold() in {
                    "nature",
                    "nature portfolio",
                    "nature (nature publishing group)",
                    "nature publishing group",
                }
                or venue_text.startswith("Nature ")
            )
            if raw_venue is not None and not nature_pair:
                self.halt("UNKNOWN", "INCOMPATIBLE_FACT", "selector conflict")
            if anchor not in {"prisma-traice", "icmje", "nature", "ieee"}:
                self.halt("UNKNOWN", "UNRESOLVED_INPUT", "unknown policy anchor")
            self.track = "anchor"
            self.phases.append("Anchor intake")
            return
        if raw_venue is None:
            self.halt("UNKNOWN", "UNRESOLVED_INPUT", "selector required")
        key = str(raw_venue).strip().casefold()
        self.venue = ALIASES.get(key)
        if self.venue is None:
            self.phases.append("Venue lookup")
            self.halt(
                "UNKNOWN",
                "UNCURATED_POLICY",
                f"I do not have a curated executable policy for {raw_venue}",
            )

    def _intake(self) -> None:
        self.phases.append("Intake")
        self.outcome = "UNKNOWN"
        self.require_global("external_use_inventory_confirmed")
        categories = self.case.get("categories")
        if not isinstance(categories, Mapping) or set(categories) != ALL_CATEGORIES:
            self.halt("UNKNOWN", "UNRESOLVED_INPUT", "complete category inventory required")
        invalid = {value for value in categories.values() if value not in {"USED", "NOT_USED", "UNCERTAIN"}}
        if invalid or "UNCERTAIN" in categories.values():
            self.halt("UNKNOWN", "UNRESOLVED_INPUT", "category inventory unresolved")
        used_categories = {name for name, state in categories.items() if state == "USED"}
        if used_categories and not self.records:
            self.halt("UNKNOWN", "UNRESOLVED_INPUT", "USED category has no use record")
        for record in self.records:
            if record.category not in ALL_CATEGORIES or record.category not in used_categories:
                self.halt("UNKNOWN", "INCOMPATIBLE_FACT", f"record/category mismatch: {record.record_id}")
            if not record.record_id or not record.tool or not record.task or not record.artifact:
                self.halt("UNKNOWN", "UNRESOLVED_INPUT", "tool x task/run/artifact identity incomplete")
            if not record.operations or not set(record.operations) <= ALL_OPERATIONS:
                self.halt("UNKNOWN", "UNRESOLVED_INPUT", f"operation unresolved: {record.record_id}")
            if not record.targets or not set(record.targets) <= ALL_TARGETS:
                self.halt("UNKNOWN", "UNRESOLVED_INPUT", f"target unresolved: {record.record_id}")
        other = [record for record in self.records if record.category == "OTHER_UNCLASSIFIED"]
        if other:
            description = other[0].facts.get("verbatim_description", unknown()).value
            self.halt(
                "UNKNOWN",
                "UNRESOLVED_INPUT",
                f"unclassified use preserved: {description}",
            )

    def _phase2a(self) -> None:
        assert self.venue is not None
        self.phases.extend(("Venue Phase 2", "Venue Phase 2a"))
        if self.venue in AUTHORSHIP_TARGETS:
            author_fact = self.require_global("ai_listed_or_proposed_as_author")
            if author_fact.value is True:
                self.halt("REQUIRED" if self.records else "NOT_REQUIRED", "INCOMPATIBLE_FACT", "AI cannot be listed as author")
            if author_fact.value is not False:
                self.halt("UNKNOWN", "INCOMPATIBLE_FACT", "authorship fact is not boolean")

        if self.venue in SCOPE_TARGETS and self.records:
            scopes = [self.require_record(record, "policy_tool_scope").value for record in self.records]
            if any(scope == "OTHER_AI" for scope in scopes):
                self.halt("UNKNOWN", "POLICY_SCOPE_GAP", "OTHER_AI inventory requires current non-generative policy")
            if any(scope != "GENAI_OR_AIGC" for scope in scopes):
                self.halt("UNKNOWN", "INCOMPATIBLE_FACT", "invalid policy_tool_scope")

        self.outcome = "REQUIRED" if self.records else "NOT_REQUIRED"
        if not self.records:
            return
        handler = {
            "Chinese Nursing Journals Publishing House": self._phase2a_chinese_nursing,
            "ICMJE": self._phase2a_icmje,
            "International Eye Science": self._phase2a_ies,
            "JAMA": self._phase2a_jama,
            "Nature": self._phase2a_nature,
            "NEJM": self._phase2a_nejm,
            "PLOS": self._phase2a_plos,
            "The Lancet": self._phase2a_lancet,
        }.get(self.venue)
        if handler is not None:
            handler()

    def _phase2a_chinese_nursing(self) -> None:
        names = (
            "ai_performed_scientific_or_intellectual_contribution",
            "generated_research_figure_or_media",
            "altered_original_research_data_process_or_results",
            "used_unverified_genai_reference",
        )
        for record in self.records:
            for name in names:
                self.prohibit_true(record, name)

    def _phase2a_icmje(self) -> None:
        for record in self.records:
            if "REFERENCE_OR_CITATION" in record.targets:
                self.prohibit_true(record, "ai_generated_material_used_as_primary_source")
                self.prohibit_true(record, "ai_cited_as_author")

    def _phase2a_ies(self) -> None:
        allowed_scopes = {
            "LANGUAGE_POLISHING",
            "LITERATURE_RETRIEVAL",
            "DATA_ORGANIZATION",
            "CHART_ANNOTATION",
            "OTHER_CONFIRMED_NON_CORE_RESEARCH_STEP",
            "CORE_RESEARCH_STEP",
        }
        prohibitions = (
            "generated_core_main_text_conclusion_analysis_viewpoint_or_innovation_claim",
            "fabricated_experimental_plan_technical_route_or_citation",
            "replaced_author_in_experimental_design_or_data_validation",
            "fabricated_data_invented_results_or_tampered_conclusions",
            "rewrote_plagiarized_work_to_evade_detection",
            "generated_peer_review_response_grant_contribution_or_integrity_statement",
            "uploaded_secret_research_data_or_unpublished_results_to_public_ai_platform",
            "aigc_generated_or_tampered_data",
            "aigc_replaced_core_analysis",
            "uploaded_undeidentified_data_to_aigc",
            "uploaded_data_lacking_required_ethics_review_to_aigc",
            "fabricated_data_or_ethics_proof",
        )
        for record in self.records:
            scope = self.require_record(record, "use_scope").value
            if scope not in allowed_scopes:
                self.halt("UNKNOWN", "INCOMPATIBLE_FACT", "invalid International Eye Science use_scope")
            if scope == "CORE_RESEARCH_STEP":
                self.halt("REQUIRED", "PROHIBITED_USE", "CORE_RESEARCH_STEP is prohibited")
            if scope == "OTHER_CONFIRMED_NON_CORE_RESEARCH_STEP":
                self.require_record(record, "use_scope_basis")
            overseas = self.require_record(record, "tool_is_overseas")
            if overseas.value is True:
                self.require_record(record, "lawful_compliance_qualification", required_value=True)
            elif overseas.value is not False:
                self.halt("UNKNOWN", "INCOMPATIBLE_FACT", "tool_is_overseas is not boolean")
            for name in prohibitions:
                self.prohibit_true(record, name)
            data = self.require_record(record, "use_involves_data")
            if scope in {"DATA_ORGANIZATION", "CHART_ANNOTATION"} and data.value is not True:
                self.halt("REQUIRED", "INCOMPATIBLE_FACT", "data scope requires use_involves_data=true")

    def _phase2a_jama(self) -> None:
        for record in self.records:
            generated_text = bool(
                set(record.operations) & {"GENERATED", "SUBSTANTIVELY_DRAFTED"}
                and set(record.targets) & TEXT_TARGETS
            )
            if generated_text or "OTHER_CONFIRMED" in record.operations or "OTHER_CONFIRMED" in record.targets:
                submission_type = self.require_record(record, "jama_submission_type")
                prohibited = self.require_record(record, "jama_submission_type_is_prohibited")
                known_prohibited = submission_type.value in {
                    "OPINION_MANUSCRIPT",
                    "LETTER_TO_THE_EDITOR",
                    "ONLINE_COMMENT",
                    "A_PIECE_OF_MY_MIND",
                    "POETRY",
                }
                if prohibited.value is not known_prohibited:
                    self.halt("REQUIRED", "INCOMPATIBLE_FACT", "JAMA submission-type predicate contradicts exact type")
                if known_prohibited:
                    self.halt("REQUIRED", "PROHIBITED_USE", f"JAMA prohibits AI drafting for {submission_type.value}")
            if "RESEARCH_FIGURE_OR_MEDIA" in record.targets:
                created = self.require_record(record, "clinical_image_or_illustration_created_or_manipulated")
                if created.value is True:
                    self.require_record(record, "part_of_formal_research_design_or_methods", required_value=True)
                elif created.value is not False:
                    self.halt("UNKNOWN", "INCOMPATIBLE_FACT", "clinical image predicate is not boolean")

    def _phase2a_nature(self) -> None:
        if any("RESEARCH_FIGURE_OR_MEDIA" in record.targets for record in self.records):
            self.halt("UNKNOWN", "CONTRACT_GAP", "NATURE_VENUE_IMAGE_CONTAINMENT")

    def _phase2a_nejm(self) -> None:
        for record in self.records:
            if "REFERENCE_OR_CITATION" in record.targets:
                self.prohibit_true(record, "ai_generated_material_used_as_primary_source")

    def _phase2a_plos(self) -> None:
        data_targets = {"ORIGINAL_RESEARCH_DATA", "RESULTS", "SUPPORTING_DATA_FILE"}
        for record in self.records:
            if set(record.targets) & data_targets:
                self.prohibit_true(record, "ai_fabricated_or_misrepresented_primary_research_data")

    def _phase2a_lancet(self) -> None:
        cover_count = 0
        for record in self.records:
            self.prohibit_true(record, "ai_replaced_authors_intellectual_contribution")
            if "RESEARCH_FIGURE_OR_MEDIA" not in record.targets:
                continue
            self.prohibit_true(record, "generated_media_duplicates_or_refers_to_protected_subject")
            artifact_class = self.require_record(record, "artifact_class").value
            if artifact_class == "PRIMARY_RESEARCH_IMAGE":
                formal = self.require_record(record, "ai_is_formal_research_design_or_method")
                direct = self.require_record(record, "image_output_directly_obtained_in_research_through_that_method")
                if formal.value is not True or direct.value is not True:
                    self.halt("REQUIRED", "PROHIBITED_USE", "AI-created primary research image is prohibited")
            elif artifact_class == "RESEARCH_METHOD_IMAGE":
                self.require_record(record, "ai_is_formal_research_design_or_method", required_value=True)
                self.require_record(record, "image_output_directly_obtained_in_research_through_that_method", required_value=True)
                self.require_record(record, "reproducible_method_details")
            elif artifact_class == "GRAPHICAL_ABSTRACT":
                self.require_record(record, "graphical_abstract_used_ai_or_ai_assisted_illustration", required_value=True)
                tool_class = self.require_record(record, "graphical_abstract_tool_class").value
                if tool_class == "GENERAL_PURPOSE_GENERATIVE_AI_IMAGE_TOOL":
                    self.halt("REQUIRED", "PROHIBITED_USE", "general-purpose GenAI graphical abstracts are prohibited")
                if tool_class != "DEDICATED_SCIENTIFIC_OR_PROFESSIONAL_ILLUSTRATION_TOOL":
                    self.halt("UNKNOWN", "INCOMPATIBLE_FACT", "unknown graphical-abstract tool class")
            elif artifact_class == "COVER_ART":
                cover_count += 1
                self.require_record(record, "editor_permission", required_value=True)
                self.require_record(record, "publisher_permission", required_value=True)
                has_third_party = self.require_record(record, "cover_art_contains_third_party_material")
                if has_third_party.value is True:
                    self.require_record(record, "third_party_material_permission")
                elif has_third_party.value is False:
                    self.ledger[record.record_id]["third_party_material_permission"] = not_applicable(record.record_id)
                else:
                    self.halt("UNKNOWN", "INCOMPATIBLE_FACT", "third-party predicate is not boolean")
                self.require_record(record, "content_attribution")
            elif artifact_class not in {"EXPLANATORY_IMAGE", "DATA_VISUALIZATION"}:
                self.halt("UNKNOWN", "CONTRACT_GAP", "unmodelled visual/media class")

            self.require_record(record, "visual_accuracy_confirmed", required_value=True)
            self.require_record(record, "visual_originality_confirmed", required_value=True)
            based = self.require_record(record, "based_on_existing_artwork_or_graphics")
            if based.value is True:
                self.require_record(record, "rights_holder_permission")
                self.require_record(record, "existing_artwork_attribution")
            elif based.value is False:
                self.ledger[record.record_id]["rights_holder_permission"] = not_applicable(record.record_id)
                self.ledger[record.record_id]["existing_artwork_attribution"] = not_applicable(record.record_id)
            else:
                self.halt("UNKNOWN", "INCOMPATIBLE_FACT", "existing-artwork predicate is not boolean")
            if artifact_class == "DATA_VISUALIZATION":
                self.require_record(record, "directly_derived_from_data_by_reproducible_method", required_value=True)

        if cover_count == len(self.records):
            self.outcome = "ACTION_ONLY"

    def _phase2b(self) -> None:
        assert self.venue is not None
        self.phases.append("Venue Phase 2b")
        for record in self.records:
            if self.venue == "ICLR":
                self.require_record(record, "specific_assisted_tasks")
                self.require_record(record, "author_accepts_full_responsibility", required_value=True)
                self.require_record(record, "affected_content")
            elif self.venue == "BMJ":
                for name in ("technology_description", "why_used", "how_used"):
                    self.require_record(record, name)
            elif self.venue == "Chinese Nursing Journals Publishing House":
                for name in ("purpose", "affected_content", "human_review_editing_performed", "author_accepts_full_responsibility"):
                    required = True if name in {"human_review_editing_performed", "author_accepts_full_responsibility"} else None
                    self.require_record(record, name, required_value=required)
            elif self.venue == "Frontiers":
                for name in ("version", "model", "source_provider", "content_operation", "affected_content_kind", "affected_content"):
                    self.require_record(record, name)
            elif self.venue == "ICMJE":
                for name in ("technology_description", "how_used"):
                    self.require_record(record, name)
            elif self.venue == "International Eye Science":
                self._phase2b_ies(record)
            elif self.venue == "JAMA":
                self._phase2b_jama(record)
            elif self.venue == "Nature":
                for name in ("how_used", "affected_content", "author_accepts_accountability"):
                    required = True if name == "author_accepts_accountability" else None
                    self.require_record(record, name, required_value=required)
            elif self.venue == "NEJM":
                for name in ("technology_description", "produced_content", "human_review_editing_performed", "no_plagiarism_confirmed"):
                    required = True if name in {"human_review_editing_performed", "no_plagiarism_confirmed"} else None
                    self.require_record(record, name, required_value=required)
            elif self.venue == "PLOS":
                for name in ("how_used", "outputs_validated", "affected_content"):
                    self.require_record(record, name)
            elif self.venue == "The Lancet":
                self._phase2b_lancet(record)

    def _phase2b_ies(self, record: UseRecord) -> None:
        for name in ("version", "purpose", "use_scope", "generated_proportion"):
            self.require_record(record, name)
        data = self.require_record(record, "use_involves_data")
        data_children = ("data_types", "data_verification_status", "data_involves_clinical_or_case_data")
        if data.value is False:
            for child in data_children:
                self.ledger[record.record_id][child] = not_applicable(record.record_id)
            self.ledger[record.record_id]["de_identification_measures"] = not_applicable(record.record_id)
            return
        if data.value is not True:
            self.halt("REQUIRED", "INCOMPATIBLE_FACT", "use_involves_data is not boolean")
        for child in data_children:
            self.require_record(record, child)
        clinical = self.ledger[record.record_id]["data_involves_clinical_or_case_data"]
        if clinical.value is True:
            self.require_record(record, "de_identification_measures")
        elif clinical.value is False:
            self.ledger[record.record_id]["de_identification_measures"] = not_applicable(record.record_id)
        else:
            self.halt("REQUIRED", "INCOMPATIBLE_FACT", "clinical-data predicate is not boolean")

    def _phase2b_jama(self, record: UseRecord) -> None:
        self.require_record(record, "author_review_accuracy", required_value=True)
        self.require_record(record, "author_accepts_content_integrity_responsibility", required_value=True)
        for name in ("model_or_tool_version", "manufacturer", "dates_of_use", "use_description", "affected_portions"):
            self.require_record(record, name)
        self.conditional(record, "extension_numbers_applicable", ("extension_numbers",))
        self.ledger[record.record_id]["ai_used_in_scientific_study"] = known(
            record.research_use, record.record_id
        )
        if not record.research_use:
            return
        self.require_record(record, "specific_research_use")
        self.conditional(
            record,
            "study_uses_llm",
            ("llm_prompts", "llm_prompt_sequence", "llm_prompt_revisions"),
        )
        self.conditional(
            record,
            "copyright_protected_content_entered",
            ("copyright_permission_copy", "copyright_permission_methods_description"),
        )
        self.conditional(
            record,
            "ai_generated_content_included_in_submission",
            ("included_content_type", "publication_rights_basis"),
        )

    def _phase2b_lancet(self, record: UseRecord) -> None:
        artifact = self.ledger.get(record.record_id, {}).get("artifact_class")
        if artifact is not None and artifact.value == "COVER_ART":
            return
        if artifact is not None and artifact.value == "GRAPHICAL_ABSTRACT":
            self.require_record(record, "publication_rights_basis")
            return
        if artifact is not None and artifact.value == "RESEARCH_METHOD_IMAGE":
            self.require_record(record, "model_or_tool_version")
            self.conditional(
                record,
                "developer_or_manufacturer_applicable",
                ("developer_or_manufacturer",),
            )
            return
        if artifact is not None and artifact.value in {"EXPLANATORY_IMAGE", "DATA_VISUALIZATION"}:
            self.require_record(record, "model_or_tool_version")
            return
        for name in (
            "tool_service_name",
            "purpose",
            "extent_of_human_oversight",
            "author_reviewed_and_edited",
            "author_accepts_full_responsibility",
        ):
            required = True if name in {"author_reviewed_and_edited", "author_accepts_full_responsibility"} else None
            self.require_record(record, name, required_value=required)

    def _render(self) -> None:
        assert self.venue is not None
        self.phases.extend(("Venue Phase 3", "Venue Phase 4", "Venue Phase 5"))
        if self.venue == "NEJM":
            self.blocks.extend(
                (
                    Block("COVER_LETTER", "submission disclosure", "Tell the editor which technology was used and what it produced."),
                    Block("SUBMITTED_WORK", "reader-facing disclosure", "Describe the reviewed AI-produced material and originality confirmation in the submitted work."),
                )
            )
        elif self.venue == "ICMJE":
            self.blocks.extend(
                (
                    Block("COVER_LETTER", "editor disclosure", "Describe the AI-assisted technology and use for the editor."),
                    Block("SUBMITTED_WORK", "article disclosure", "Describe the AI-assisted technology and use in the appropriate article section."),
                )
            )
        elif self.venue == "JAMA":
            if any(record.research_use for record in self.records):
                self.blocks.append(Block("METHODS", "AI-use disclosure portion", "Describe the specific research AI use and confirmed conditional rights facts."))
            if any(not record.research_use for record in self.records):
                self.blocks.append(Block("ACKNOWLEDGEMENTS", "manuscript-preparation disclosure", "Identify the tool, dates, affected portions, review, and responsibility."))
            if any(
                self.ledger.get(record.record_id, {}).get("ai_generated_content_included_in_submission", unknown()).value is True
                for record in self.records
            ):
                self.blocks.append(Block("RELEVANT_LEGEND", "item-specific publication-rights disclosure", "State the confirmed publication-rights basis for the affected item."))
        elif self.venue == "The Lancet":
            for record in self.records:
                artifact = self.ledger.get(record.record_id, {}).get("artifact_class")
                if artifact is None:
                    self.blocks.append(Block("DECLARATION_BEFORE_REFERENCES", f"manuscript-preparation declaration for {record.record_id}", f"Declare {record.tool}'s purpose, oversight, review, and author responsibility."))
                elif artifact.value == "GRAPHICAL_ABSTRACT":
                    self.blocks.append(Block("GRAPHICAL_ABSTRACT_CAPTION", "illustration-tool disclosure", f"Name {record.tool} and its publication-rights basis in this caption."))
                elif artifact.value in {"RESEARCH_METHOD_IMAGE", "DATA_VISUALIZATION"}:
                    self.blocks.append(Block("METHODS", f"research visual method for {record.record_id}", f"Describe reproducible use of {record.tool} for {record.artifact}."))
                elif artifact.value == "EXPLANATORY_IMAGE":
                    self.blocks.append(Block("IMAGE_CAPTION", f"explanatory-image disclosure for {record.record_id}", f"Identify {record.tool} for {record.artifact}."))
        else:
            placements = {
                "ACL": "ACKNOWLEDGEMENTS",
                "BMJ": "ACKNOWLEDGEMENTS_OR_METHODS",
                "Chinese Nursing Journals Publishing House": "END_OF_MAIN_TEXT",
                "EMNLP": "ACKNOWLEDGEMENTS",
                "Frontiers": "ACKNOWLEDGEMENTS_OR_METHODS",
                "ICLR": "PAPER_BODY",
                "International Eye Science": "END_OF_MAIN_TEXT",
                "Nature": "METHODS_OR_ACKNOWLEDGEMENTS",
                "PLOS": "METHODS",
                "Science": "ACKNOWLEDGEMENTS_OR_METHODS",
            }
            placement = placements.get(self.venue, "POLICY_SPECIFIED_LOCATION")
            self.blocks.append(Block(placement, "venue AI-use disclosure", f"Render confirmed per-record facts for {self.venue}."))

    def _phase5_actions(self) -> None:
        if self.venue == "Frontiers":
            for record in self.records:
                operation = self.ledger[record.record_id]["content_operation"].value
                kind = self.ledger[record.record_id]["affected_content_kind"].value
                if operation == "CREATED":
                    self.actions.append(f"{record.record_id}: factual accuracy")
                self.actions.append(f"{record.record_id}: plagiarism-free")
                if kind == "VISUAL":
                    represents = record.facts.get("figure_represents_data", unknown(record.record_id))
                    if represents.state != "KNOWN":
                        self.actions.append("resolve figure_represents_data")
                    elif represents.value is True:
                        self.actions.append(f"{record.record_id}: accuracy to data")
        self._cover_actions()

    def _cover_actions(self) -> None:
        if self.venue != "The Lancet":
            return
        for record in self.records:
            artifact = self.ledger.get(record.record_id, {}).get("artifact_class")
            if artifact is not None and artifact.value == "COVER_ART":
                self.actions.extend(
                    (
                        f"{record.record_id}: editor permission confirmed",
                        f"{record.record_id}: publisher permission confirmed",
                        f"{record.record_id}: third-party material and attribution checked",
                    )
                )

    def _member_advisory(self) -> None:
        if self.venue in ICMJE_MEMBER_TARGETS and self.records:
            self.advisories.append("ICMJE-alongside advisory")


def evaluate(case: Mapping[str, object]) -> ContractResult:
    """Evaluate one synthetic fixture against the documentation-owned contract."""
    return _Evaluator(case).run()


SURFACE_FILES = (
    "academic-paper/SKILL.md",
    "commands/ars-disclosure.md",
    "academic-paper/references/mode_selection_guide.md",
    "README.md",
    "README.ja-JP.md",
    "README.ko-KR.md",
    "README.zh-CN.md",
    "README.zh-TW.md",
)
SURFACE_TOKENS = {
    "ACL": ("ACL",),
    "BMJ": ("BMJ",),
    "Chinese Nursing Journals Publishing House": (
        "Chinese Nursing Journals Publishing House",
        "中华护理杂志社",
    ),
    "EMNLP": ("EMNLP",),
    "Frontiers": ("Frontiers",),
    "ICLR": ("ICLR",),
    "ICMJE": ("ICMJE",),
    "International Eye Science": ("International Eye Science", "国际眼科杂志"),
    "JAMA": ("JAMA",),
    "Nature": ("Nature",),
    "NEJM": ("NEJM",),
    "NeurIPS": ("NeurIPS",),
    "PLOS": ("PLOS",),
    "Science": ("Science",),
    "The Lancet": ("The Lancet",),
}


def surface_sync_errors(root: Path) -> list[str]:
    """Return deterministic selector/database/user-surface drift diagnostics."""
    errors: list[str] = []
    policies_path = root / "academic-paper/references/venue_disclosure_policies.md"
    protocol_path = root / "academic-paper/references/disclosure_mode_protocol.md"
    try:
        policies = policies_path.read_text(encoding="utf-8")
        protocol = protocol_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        return [f"required contract surface missing: {exc.filename}"]
    headings = re.findall(r"^## Venue: (.+)$", policies, re.MULTILINE)
    labels = tuple(heading.split(" (", 1)[0].strip() for heading in headings)
    if labels != CANONICAL_VENUES:
        errors.append("runnable database canonical inventory/order drift")
    for venue, tokens in SURFACE_TOKENS.items():
        if not any(token in protocol for token in tokens):
            errors.append(f"disclosure_mode_protocol.md missing selector for {venue}")
    for rel in SURFACE_FILES:
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{rel}: surface missing")
            continue
        for venue, tokens in SURFACE_TOKENS.items():
            if not any(token in text for token in tokens):
                errors.append(f"{rel}: selector drift for {venue}")
    return errors

