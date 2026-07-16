"""Mutation tests for check_pipeline_boundary_semantics.py (#528 defrift lock).

One failing witness per invariant branch: each test mutates exactly one pinned
surface fragment and asserts the checker fires on that invariant (and, for the
baseline, that the committed repo state passes).
"""
import unittest
from pathlib import Path

from tests.test_helpers import load_module_from_path, run_script

SCRIPT = Path(__file__).resolve().parent / "check_pipeline_boundary_semantics.py"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_module():
    return load_module_from_path("check_pipeline_boundary_semantics", SCRIPT)


class PipelineBoundarySemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()
        cls.skill = (REPO_ROOT / cls.mod.SKILL).read_text(encoding="utf-8")
        cls.orch = (REPO_ROOT / cls.mod.ORCH).read_text(encoding="utf-8")
        cls.sm = (REPO_ROOT / cls.mod.SM).read_text(encoding="utf-8")
        cls.proto = (REPO_ROOT / cls.mod.PROTO).read_text(encoding="utf-8")
        cls.tracker = (REPO_ROOT / cls.mod.TRACKER).read_text(encoding="utf-8")

    def _check(self, skill=None, orch=None, sm=None, proto=None, tracker=None):
        return self.mod.check(
            skill if skill is not None else self.skill,
            orch if orch is not None else self.orch,
            sm if sm is not None else self.sm,
            proto if proto is not None else self.proto,
            tracker if tracker is not None else self.tracker,
        )

    def _authority_section(self, sm_text: str) -> str:
        """The H2 authority span, via the same shared helper the checker uses."""
        from _skill_lint import h2_section_body

        section = h2_section_body(sm_text, self.mod.AUTHORITY_HEADING)
        self.assertIsNotNone(section)
        return section

    # --- baseline ---

    def test_repo_baseline_passes(self) -> None:
        result = run_script(SCRIPT)
        self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
        self.assertIn("PASSED", result.stdout)

    def test_clean_contents_pass(self) -> None:
        self.assertEqual(self._check(), [])

    # --- INV-1: Methodology Blueprint in Stage 1→2 handoff ---

    def test_inv1_skill_blueprint_dropped(self) -> None:
        mutated = self.skill.replace(
            "RQ Brief + Methodology Blueprint + Bibliography", "RQ Brief + Bibliography"
        )
        errors = self._check(skill=mutated)
        self.assertTrue(any(e.startswith("invariant 1") and self.mod.SKILL in e for e in errors))

    def test_inv1_state_machine_blueprint_dropped(self) -> None:
        mutated = self.sm.replace(
            "handoff RQ Brief + Methodology Blueprint + Bibliography",
            "handoff RQ Brief + Bibliography",
        )
        errors = self._check(sm=mutated)
        self.assertTrue(any(e.startswith("invariant 1") and self.mod.SM in e for e in errors))

    def test_inv1_orchestrator_blueprint_dropped(self) -> None:
        mutated = self.orch.replace(
            "RQ Brief, Methodology Blueprint, Annotated Bibliography",
            "RQ Brief, Annotated Bibliography",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 1") and self.mod.ORCH in e for e in errors))

    # --- INV-2: Stage 3' Minor never triggers coaching ---

    def test_inv2_trigger_condition_reverted(self) -> None:
        mutated = self.orch.replace(
            "A Stage 3' Minor decision does NOT trigger coaching",
            "A Stage 3' Minor decision may trigger coaching",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 2") for e in errors))

    def test_inv2_exclusion_list_reverted(self) -> None:
        mutated = self.orch.replace(
            "a Stage 3' Minor decision also does not trigger coaching",
            "coaching applies to all Minor decisions",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 2") for e in errors))

    # --- codex round-5 witnesses ---

    def test_inv2_skill_routing_rerouted(self) -> None:
        """Adverse-value mutation (codex round-5 P1): SKILL rule 6 reroutes a
        Stage 3' Minor through coaching/Stage 4' — must fire."""
        mutated = self.skill.replace(
            "6. **Stage 3' RE-REVIEW** -> Accept|Minor -> Stage 4.5 / Major -> Stage 4'",
            "6. **Stage 3' RE-REVIEW** -> Accept -> Stage 4.5 / Minor|Major -> Stage 4'",
        )
        self.assertNotEqual(mutated, self.skill)
        errors = self._check(skill=mutated)
        self.assertTrue(
            any(e.startswith("invariant 2") and self.mod.SKILL in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv2_state_machine_minor_routing_dropped(self) -> None:
        """Adverse-value mutation (codex round-5 P1): the state machine's
        Accept/Minor -> Stage 4.5 transition row loses Minor — must fire."""
        mutated = self.sm.replace(
            "| checkpoint | Stage 4.5 | Decision = Accept/Minor, user confirms | Pass final draft to final verification |",
            "| checkpoint | Stage 4.5 | Decision = Accept, user confirms | Pass final draft to final verification |",
        )
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 2") and "stage3p-minor-routing-row" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_skill_rule9_outcome_flipped(self) -> None:
        """Adverse-value mutation (codex round-5 P1): rule 9 flips the
        completion type or the decline outcome — must fire."""
        type_mut = self.skill.replace(
            "completion checkpoint (FULL) -> Stage 6",
            "completion checkpoint (MANDATORY) -> Stage 6",
        )
        outcome_mut = self.skill.replace(
            "user may decline Stage 6: marked `skipped`, pipeline goes directly to `completed`",
            "user may not decline Stage 6",
        )
        for name, mut in (("type", type_mut), ("outcome", outcome_mut)):
            self.assertNotEqual(mut, self.skill, msg=name)
            errors = self._check(skill=mut)
            self.assertTrue(
                any(e.startswith("invariant 4") and "rule 9" in e for e in errors),
                msg=f"{name} errors: {errors}",
            )

    # --- codex round-6 witnesses ---

    def test_inv2_coaching_trigger_widened_to_minor(self) -> None:
        """Adverse-value mutation (codex round-6 P1): the affirmative coaching
        trigger widens Stage 3' back to Minor/Major — must fire; same for the
        handoff table's (if Major) qualifier."""
        trigger_mut = self.orch.replace(
            "after Stage 3' completion with Decision = Major Revision (routes to Stage 4')",
            "after Stage 3' completion with Decision = Minor/Major Revision (routes to Stage 4')",
        )
        handoff_mut = self.orch.replace(
            "| Stage 3' -> **coaching** -> 4' | New Revision Roadmap (if Major) |",
            "| Stage 3' -> **coaching** -> 4' | New Revision Roadmap (if Minor/Major) |",
        )
        for name, mut in (("trigger", trigger_mut), ("handoff", handoff_mut)):
            self.assertNotEqual(mut, self.orch, msg=name)
            errors = self._check(orch=mut)
            self.assertTrue(
                any(e.startswith("invariant 2") and "affirmative" in e for e in errors),
                msg=f"{name} errors: {errors}",
            )

    def test_inv4_completion_type_flipped_on_mirrors(self) -> None:
        """Adverse-value mutation (codex round-6 P1): the completion-checkpoint
        type flips (FULL)->(MANDATORY) on the orchestrator handoff row or the
        protocol trigger — must fire per mirror."""
        orch_mut = self.orch.replace(
            "Dispatched only after the user confirms the Stage 5 completion checkpoint (FULL)",
            "Dispatched only after the user confirms the Stage 5 completion checkpoint (MANDATORY)",
        )
        proto_mut = self.proto.replace(
            "After the user confirms the Stage 5 completion checkpoint (FULL)",
            "After the user confirms the Stage 5 completion checkpoint (MANDATORY)",
        )
        for kw, mut, orig in (("orch", orch_mut, self.orch), ("proto", proto_mut, self.proto)):
            self.assertNotEqual(mut, orig, msg=kw)
            errors = self._check(**{kw: mut})
            self.assertTrue(
                any(e.startswith("invariant 4") and "completion trigger" in e for e in errors),
                msg=f"{kw} errors: {errors}",
            )

    def test_inv4_sequencing_flipped(self) -> None:
        """Adverse-value mutation (codex round-6 P1): completion allowed
        before acknowledgement/delivery — must fire on each surface."""
        orch_mut = self.orch.replace(
            "Pipeline terminal transition: on the Stage 6 terminal acknowledgement (",
            "Pipeline terminal transition: before the Stage 6 terminal acknowledgement (",
        )
        proto_mut = self.proto.replace(
            "After delivering the process record, prompt the user to close the pipeline",
            "Before delivering the process record, prompt the user to close the pipeline",
        )
        sm_mut = self.sm.replace(
            "After delivering the Process Record (MD + PDF per the user's language choice), the orchestrator prompts for a terminal acknowledgement",
            "Before delivering the Process Record, the orchestrator prompts for a terminal acknowledgement",
        )
        for kw, mut, orig in (("orch", orch_mut, self.orch),
                              ("proto", proto_mut, self.proto),
                              ("sm", sm_mut, self.sm)):
            self.assertNotEqual(mut, orig, msg=kw)
            errors = self._check(**{kw: mut})
            self.assertTrue(
                any(e.startswith("invariant 4") and ("sequencing" in e or "post-delivery-prompt" in e) for e in errors),
                msg=f"{kw} errors: {errors}",
            )

    # --- codex round-7 witnesses ---

    def test_inv3_authority_auto_advance_flipped(self) -> None:
        mutated = self.sm.replace(
            "- explicit confirmation to proceed to finalization (no auto-advance);",
            "- confirmation to proceed to finalization (auto-advance permitted);",
        )
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 3") and "no-auto-advance" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_authority_stage6_made_mandatory(self) -> None:
        mutated = self.sm.replace(
            "Stage 6 is a non-mandatory stage (it is absent from the orchestrator's non-skippable list). At the Stage 5 completion checkpoint the user may decline it",
            "Stage 6 is a mandatory stage. The user may not decline it",
        )
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "stage6-non-mandatory" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_authority_terminal_moved_to_start(self) -> None:
        mutated = self.sm.replace(
            "When Stage 6 runs, its completion is the pipeline's **terminal checkpoint**:",
            "When Stage 6 runs, its start is the pipeline's **terminal checkpoint**:",
        )
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "terminal-checkpoint" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv2_diagram_minor_branch_rerouted(self) -> None:
        """Adverse-value mutation (codex round-7 P1): the diagram's Stage 3'
        Accept/Minor branch reroutes Minor — must fire."""
        mutated = self.sm.replace("|     /Minor        |", "|     /Reject       |")
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 2") and "stage3p-accept-minor-branch" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv2_diagram_terminal_edge_relabeled(self) -> None:
        mutated = self.sm.replace("[terminal acknowledgement]", "[record delivery]")
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 2") and "terminal-ack-edge" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_skill_step4_decline_reversed(self) -> None:
        mutated = self.skill.replace(
            "(user may decline Stage 6 at the Stage 5 completion checkpoint)",
            "(user may not decline Stage 6)",
        )
        self.assertNotEqual(mutated, self.skill)
        errors = self._check(skill=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "Step 4" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_proto_step5_retyped_or_continued(self) -> None:
        header_mut = self.proto.replace(
            "5. Terminal acknowledgement (pipeline terminal checkpoint):",
            "5. Acknowledgement (advisory, non-terminal):",
        )
        continuation_mut = self.proto.replace(
            "There is no next stage.",
            "Proceed to Stage 7 archival.",
        )
        for name, mut in (("header", header_mut), ("continuation", continuation_mut)):
            self.assertNotEqual(mut, self.proto, msg=name)
            errors = self._check(proto=mut)
            self.assertTrue(
                any(e.startswith("invariant 4") and self.mod.PROTO in e for e in errors),
                msg=f"{name} errors: {errors}",
            )

    # --- INV-3: Stage 5 boundary semantics ---

    def test_inv3_authority_section_removed(self) -> None:
        mutated = self.sm.replace(
            "## Stage 5 and Stage 6 Boundary Semantics", "## Stage notes"
        )
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 3") and "missing" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv3_entry_gate_fragment_lost(self) -> None:
        mutated = self.sm.replace(
            "refers to exactly ONE checkpoint: the **Stage 5 entry gate**",
            "may refer to more than one checkpoint",
        )
        errors = self._check(sm=mutated)
        self.assertTrue(any(e.startswith("invariant 3") and "entry-gate" in e for e in errors))

    def test_inv3_completion_row_removed(self) -> None:
        mutated = self.sm.replace(
            "| Stage 5 | **checkpoint** | Stage 5 completed, Final Paper delivered |",
            "| Stage 5 | END |",
        )
        errors = self._check(sm=mutated)
        self.assertTrue(any(e.startswith("invariant 3") and "completion-checkpoint" in e for e in errors))

    def test_inv3_completion_row_flipped_to_mandatory(self) -> None:
        """Adverse-value mutation (codex P1): the row survives as a prefix but
        its outcome cell flips FULL to MANDATORY — must fire."""
        mutated = self.sm.replace(
            "Wait for user confirmation (FULL — never SLIM; see § Stage 5 boundary semantics)",
            "Wait for user confirmation (MANDATORY; see § Stage 5 boundary semantics)",
        )
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 3") and "completion-checkpoint-row" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv3_not_on_mandatory_list_clause_deleted(self) -> None:
        """Adverse-value mutation (codex P1): deleting the 'not on the
        MANDATORY list' clause from the authority section must fire."""
        mutated = self.sm.replace(" — but it is not on the MANDATORY list", "")
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 3") and "completion-not-mandatory" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv3_skill_mandatory_cell_broadened(self) -> None:
        """The drift that motivated item 3: 'Stage 5' unqualified again."""
        mutated = self.skill.replace(
            "Stage 5 entry gate (before finalization)", "Stage 5"
        )
        errors = self._check(skill=mutated)
        self.assertTrue(any(e.startswith("invariant 3") and self.mod.SKILL in e for e in errors))

    def test_inv3_orchestrator_rule5_lost(self) -> None:
        mutated = self.orch.replace(
            "the checkpoint between Stage 4.5 PASS and the Stage 5 dispatch",
            "the finalization checkpoint",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 3") and self.mod.ORCH in e for e in errors))

    def test_inv3_completion_sentence_lost_in_skill(self) -> None:
        mutated = self.skill.replace(
            "The Stage 5 completion checkpoint (Final Paper delivered, before Stage 6) is FULL — never SLIM",
            "The Stage 5 completion checkpoint may be SLIM",
        )
        errors = self._check(skill=mutated)
        self.assertTrue(any(e.startswith("invariant 3") and "completion-" in e for e in errors))

    # --- INV-4: Stage 6 terminal semantics ---

    def test_inv4_vocabulary_lost_in_authority_section(self) -> None:
        """Dropping one canonical token (`confirm`) from the authority section
        must fire the section-scoped vocabulary literal."""
        section = self._authority_section(self.sm)
        mutated_section = section.replace(
            "`finish` / `end` / `done` / `confirm`,", "`finish` / `end` / `done`,"
        )
        self.assertNotEqual(section, mutated_section)
        mutated = self.sm.replace(section, mutated_section)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "acknowledgement-vocabulary" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_decline_path_fragment_lost(self) -> None:
        mutated = self.sm.replace(
            "marked `skipped` and the pipeline still terminates `completed`",
            "an error",
        )
        errors = self._check(sm=mutated)
        self.assertTrue(any(e.startswith("invariant 4") and "decline-path" in e for e in errors))

    def test_inv4_terminal_row_removed(self) -> None:
        mutated = self.sm.replace(
            "| Stage 6 | **terminal checkpoint** | Process Record delivered |",
            "| Stage 6 | END | done |",
        )
        errors = self._check(sm=mutated)
        self.assertTrue(any(e.startswith("invariant 4") and "terminal-checkpoint-row" in e for e in errors))

    def test_inv4_decline_row_removed(self) -> None:
        mutated = self.sm.replace(
            "| checkpoint | completed | User declines Stage 6 |",
            "| checkpoint | completed | n/a |",
        )
        errors = self._check(sm=mutated)
        self.assertTrue(any(e.startswith("invariant 4") and "decline-row" in e for e in errors))

    def test_inv4_terminal_row_outcome_flipped_to_skipped(self) -> None:
        """Adverse-value mutation (codex P1): the terminal row survives as a
        prefix but its action cell marks Stage 6 `skipped` — must fire."""
        mutated = self.sm.replace(
            "Mark Stage 6 `completed`; set pipeline global state `completed` |",
            "Mark Stage 6 `skipped`; set pipeline global state `completed` |",
        )
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "terminal-transition-row" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_protocol_narrowed_to_exact_keywords(self) -> None:
        """Adverse-value mutation (codex P1): the protocol keeps the four
        quoted keywords but drops the natural-language-equivalent clause —
        must fire."""
        mutated = self.proto.replace(
            "unambiguous natural-language equivalent that accepts the deliverables",
            "exact keyword from the list above (no paraphrase accepted)",
        )
        self.assertNotEqual(mutated, self.proto)
        errors = self._check(proto=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and self.mod.PROTO in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_skill_vocab_lost(self) -> None:
        mutated = self.skill.replace(
            "`finish` / `end` / `done` / `confirm`, or an unambiguous natural-language equivalent",
            "any reply",
        )
        errors = self._check(skill=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and self.mod.SKILL in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_protocol_vocab_lost(self) -> None:
        mutated = self.proto.replace('"finish" / "end" / "done" / "confirm"', '"whatever"')
        errors = self._check(proto=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and self.mod.PROTO in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_orchestrator_terminal_wiring_lost(self) -> None:
        mutated = self.orch.replace('update_pipeline_state("completed")', "")
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 4") and "pair missing" in e for e in errors))

    def test_inv4_orchestrator_ack_wiring_flipped_to_skipped(self) -> None:
        """Adverse-value mutation (codex round-2 P1): the acknowledgement
        branch flips Stage 6 to `skipped` while update_pipeline_state stays —
        must fire."""
        mutated = self.orch.replace(
            '`update_stage("6", "completed", outputs)` + `update_pipeline_state("completed")`',
            '`update_stage("6", "skipped", {})` + `update_pipeline_state("completed")`',
        )
        self.assertNotEqual(mutated, self.orch)
        errors = self._check(orch=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "acknowledgement-wiring" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv3_latex_moved_to_entry_gate(self) -> None:
        """Adverse-value mutation (codex round-2 P1): the authority section
        adds LaTeX to the gate decision and drops it from the in-stage
        clause — must fire (this is the P1-1 contradiction reopening)."""
        mutated = self.sm.replace(
            "the finalization-format decision: citation style (APA 7.0 / Chicago / IEEE, ...)",
            "the finalization-format decisions: citation style and whether to generate LaTeX (APA 7.0 / Chicago / IEEE, ...)",
        ).replace('the "Need LaTeX?" question (Step 3) and ', "")
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 3") and "gate-format-decision" in e for e in errors),
            msg=f"errors: {errors}",
        )
        self.assertTrue(
            any(e.startswith("invariant 3") and "latex-in-stage" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv3_gate_scope_clause_lost_in_skill(self) -> None:
        mutated = self.skill.replace(
            "makes the finalization-format decision (citation style); the in-stage LaTeX question and content confirmation stay inside Stage 5 execution",
            "makes all format decisions including LaTeX",
        )
        self.assertNotEqual(mutated, self.skill)
        errors = self._check(skill=mutated)
        self.assertTrue(
            any(e.startswith("invariant 3") and "gate-scope" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_change_requests_flipped_in_authority(self) -> None:
        """Adverse-value mutation (codex round-2 P1): change requests
        reclassified as acknowledgements in the authority section — must fire."""
        mutated = self.sm.replace(
            "keep Stage 6 `in_progress` — they are not acknowledgements",
            "immediately complete Stage 6",
        )
        self.assertNotEqual(mutated, self.sm)
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "change-requests-not-ack" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_change_requests_flipped_in_skill_and_proto(self) -> None:
        skill_mut = self.skill.replace(
            "keep Stage 6 `in_progress` and are not acknowledgements",
            "complete Stage 6 immediately",
        )
        proto_mut = self.proto.replace(
            "Stage 6 in_progress — they are not acknowledgements",
            "Stage 6 completed",
        )
        self.assertNotEqual(skill_mut, self.skill)
        self.assertNotEqual(proto_mut, self.proto)
        errors_skill = self._check(skill=skill_mut)
        errors_proto = self._check(proto=proto_mut)
        self.assertTrue(
            any(e.startswith("invariant 4") and "change-requests-not-ack" in e and self.mod.SKILL in e for e in errors_skill),
            msg=f"errors: {errors_skill}",
        )
        self.assertTrue(
            any(e.startswith("invariant 4") and "non-acknowledgement" in e and self.mod.PROTO in e for e in errors_proto),
            msg=f"errors: {errors_proto}",
        )

    # --- codex round-3 witnesses ---

    def test_inv3_full_row_reclaims_before_finalization(self) -> None:
        """Adverse-value mutation (codex round-3 P1): the FULL checkpoint-type
        row reclaims 'before finalization' (colliding with MANDATORY) — must
        fire on both mirrors."""
        for name, text, kw in (("skill", self.skill, "skill"), ("orch", self.orch, "orch")):
            mutated = text.replace(
                "| FULL | First checkpoint; after integrity boundaries; Stage 5 completion (final-deliverable acceptance) |",
                "| FULL | First checkpoint; after integrity boundaries; before finalization (Stage 5 entry gate) |",
            )
            self.assertNotEqual(mutated, text, msg=name)
            errors = self._check(**{kw: mutated})
            self.assertTrue(
                any(e.startswith("invariant 3") and "FULL checkpoint-type row" in e for e in errors),
                msg=f"{name} errors: {errors}",
            )

    def test_inv3_skill_step1_reasks_citation_style(self) -> None:
        """Adverse-value mutation (codex round-3 P1): Stage 5 execution Step 1
        reverts to always asking the citation style — must fire."""
        mutated = self.skill.replace(
            "Consume the citation-style decision recorded at the Stage 5 entry gate",
            "Ask user which academic formatting style",
        )
        self.assertNotEqual(mutated, self.skill)
        errors = self._check(skill=mutated)
        self.assertTrue(
            any(e.startswith("invariant 3") and "Step 1" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_decline_flipped_on_mirrors(self) -> None:
        """Adverse-value mutation (codex round-3 P1): a mirror surface makes
        Stage 6 mandatory / non-declinable — must fire per surface."""
        skill_mut = self.skill.replace(
            "the user may decline it at the Stage 5 completion checkpoint (Stage 6 marked `skipped`; the pipeline still terminates `completed`)",
            "Stage 6 is mandatory and may not be declined",
        )
        orch_mut = self.orch.replace(
            "User may decline Stage 6 there: mark it `skipped`, set pipeline state `completed`",
            "Stage 6 may not be declined",
        )
        proto_mut = self.proto.replace(
            "the user may decline it at that checkpoint; it is then marked `skipped` and the pipeline still terminates `completed`",
            "Stage 6 is mandatory; may not decline",
        )
        for kw, mut, orig in (("skill", skill_mut, self.skill),
                              ("orch", orch_mut, self.orch),
                              ("proto", proto_mut, self.proto)):
            self.assertNotEqual(mut, orig, msg=kw)
            errors = self._check(**{kw: mut})
            self.assertTrue(
                any(e.startswith("invariant 4") and "decline" in e for e in errors),
                msg=f"{kw} errors: {errors}",
            )

    def test_inv4_skill_rule10_pin_lost(self) -> None:
        section_heading = "## Stage 6: Process Summary Protocol"
        rule10 = "terminal acknowledgement (`finish` / `end` / `done` / `confirm`, or an unambiguous natural-language equivalent) -> pipeline global state `completed`"
        mutated = self.skill.replace(rule10, "terminal acknowledgement -> end")
        self.assertNotEqual(mutated, self.skill)
        self.assertIn(section_heading, mutated)  # the section copy is untouched
        errors = self._check(skill=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "rule 10" in e for e in errors),
            msg=f"errors: {errors}",
        )

    # --- codex round-4 witnesses ---

    def test_inv3_mandatory_type_flipped_to_full(self) -> None:
        """Adverse-value mutation (codex round-4 P1): the entry gate's
        MANDATORY classification flips to FULL on either declaration —
        must fire independently."""
        table_mut = self.skill.replace(
            "| MANDATORY | Integrity FAIL; Review decision; Stage 5 entry gate (before finalization) |",
            "| MANDATORY | Integrity FAIL; Review decision |",
        )
        rule_mut = self.orch.replace(
            "always MANDATORY — this is the checkpoint between Stage 4.5 PASS and the Stage 5 dispatch",
            "always FULL — this is the checkpoint between Stage 4.5 PASS and the Stage 5 dispatch",
        )
        self.assertNotEqual(table_mut, self.skill)
        self.assertNotEqual(rule_mut, self.orch)
        errors_table = self._check(skill=table_mut)
        errors_rule = self._check(orch=rule_mut)
        self.assertTrue(
            any(e.startswith("invariant 3") and self.mod.SKILL in e for e in errors_table),
            msg=f"errors: {errors_table}",
        )
        self.assertTrue(
            any(e.startswith("invariant 3") and self.mod.ORCH in e for e in errors_rule),
            msg=f"errors: {errors_rule}",
        )

    def test_inv4_ack_outcome_flipped_per_surface(self) -> None:
        """Adverse-value mutation (codex round-4 P1): the acknowledgement
        outcome flips completed→skipped on each operative copy — must fire
        per surface independently."""
        sm_mut = self.sm.replace(
            "On acknowledgement: state_tracker marks Stage 6 `completed` and sets the pipeline global state to `completed`",
            "On acknowledgement: state_tracker marks Stage 6 `skipped` and sets the pipeline global state to `completed`",
        )
        skill_mut = self.skill.replace(
            "On acknowledgement, Stage 6 is marked `completed` and the pipeline global state is set to `completed`",
            "On acknowledgement, Stage 6 is marked `skipped` and the pipeline global state is set to `completed`",
        )
        proto_mut = self.proto.replace(
            "On acknowledgement: state_tracker marks Stage 6 completed and sets the pipeline global state to completed",
            "On acknowledgement: state_tracker marks Stage 6 skipped and sets the pipeline global state to completed",
        )
        for kw, mut, orig in (("sm", sm_mut, self.sm),
                              ("skill", skill_mut, self.skill),
                              ("proto", proto_mut, self.proto)):
            self.assertNotEqual(mut, orig, msg=kw)
            errors = self._check(**{kw: mut})
            self.assertTrue(
                any(e.startswith("invariant 4") and ("ack-outcome" in e or "outcome" in e) for e in errors),
                msg=f"{kw} errors: {errors}",
            )

    def test_inv4_tracker_decline_outcome_flipped(self) -> None:
        mutated = self.tracker.replace(
            '`update_stage("6", "skipped", {reason: "user declined Stage 6"})` then `update_pipeline_state("completed")`',
            '`update_stage("6", "completed", {reason: "user declined Stage 6"})` then `update_pipeline_state("completed")`',
        )
        self.assertNotEqual(mutated, self.tracker)
        errors = self._check(tracker=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "decline-outcome" in e for e in errors),
            msg=f"errors: {errors}",
        )

    # --- codex round-8 witnesses ---

    def test_inv1_tracker_prereq_blueprint_dropped(self) -> None:
        """Adverse-value mutation (codex round-8 P1): check_prerequisites
        Stage 2 row drops the Methodology Blueprint — must fire."""
        mutated = self.tracker.replace(
            "| Stage 2 | None (but Stage 1 output recommended) | RQ Brief, Methodology Blueprint, Bibliography, Synthesis |",
            "| Stage 2 | None (but Stage 1 output recommended) | RQ Brief, Bibliography, Synthesis |",
        )
        self.assertNotEqual(mutated, self.tracker)
        errors = self._check(tracker=mutated)
        self.assertTrue(
            any(e.startswith("invariant 1") and self.mod.TRACKER in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_tracker_prereq_stage6_row_dropped(self) -> None:
        mutated = self.tracker.replace(
            "| Stage 6 | None (Final Paper already delivered at Stage 5) |",
            "| Stage 7 | None |",
        )
        self.assertNotEqual(mutated, self.tracker)
        errors = self._check(tracker=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "Stage 6 row" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_orch_stage6_moved_to_non_skippable(self) -> None:
        """Adverse-value mutation (codex round-8 P1): Stage 6 leaves the
        skippable list (the skip validator would then reject the pinned
        decline path) — must fire."""
        mutated = self.orch.replace(
            ", Stage 6 (process summary — declined at the Stage 5 completion checkpoint; marked `skipped`, pipeline still terminates `completed`)",
            "",
        )
        self.assertNotEqual(mutated, self.orch)
        errors = self._check(orch=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "skippable-stages" in e for e in errors),
            msg=f"errors: {errors}",
        )

    # --- codex round-9 witnesses ---

    def test_inv3_engagement_full_exception_dropped(self) -> None:
        """Adverse-value mutation (codex round-9 P1): the SLIM engagement
        downgrade loses its FULL-checkpoint exception — must fire."""
        mutated = self.orch.replace(
            "the Stage 5 completion checkpoint is FULL — never SLIM, regardless of the continue count",
            "all non-MANDATORY checkpoints downgrade to SLIM",
        )
        self.assertNotEqual(mutated, self.orch)
        errors = self._check(orch=mutated)
        self.assertTrue(
            any(e.startswith("invariant 3") and "engagement" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_non_skippable_gains_stage6(self) -> None:
        """Adverse-value mutation (codex round-9 P1): Stage 6 is added to the
        non-skippable side while the skippable declaration stays — must fire."""
        mutated = self.orch.replace(
            "- Non-Skippable: Stage 2 (writing), Stage 2.5 (pre-review integrity), Stage 3 (initial review), Stage 4.5 (final integrity), Stage 5 (finalize)",
            "- Non-Skippable: Stage 2 (writing), Stage 2.5 (pre-review integrity), Stage 3 (initial review), Stage 4.5 (final integrity), Stage 5 (finalize), Stage 6 (process summary)",
        )
        self.assertNotEqual(mutated, self.orch)
        errors = self._check(orch=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "non-skippable" in e.lower() for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_tracker_approval_gate_flipped(self) -> None:
        """Adverse-value mutation (codex round-9 P1): the Stage 6 SSOT block's
        approval_gate flips to false — must fire."""
        block = self.mod.TRACKER_STAGE6_ENTRY
        self.assertIn(block, self.tracker)
        mutated = self.tracker.replace(
            block, block.replace('"approval_gate": true', '"approval_gate": false')
        )
        self.assertNotEqual(mutated, self.tracker)
        errors = self._check(tracker=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "Stage 6 entry" in e for e in errors),
            msg=f"errors: {errors}",
        )

    # --- codex round-10 witnesses ---

    def test_inv4_tracker_status_enum_renamed(self) -> None:
        """Adverse-value mutation (codex round-10 P1): the tracker renames
        `skipped` in its status enum — the pinned decline wiring would then
        be rejected by the consumer — must fire."""
        mutated = self.tracker.replace(
            '| status | "pending", "in_progress", "completed", "skipped", "blocked" |',
            '| status | "pending", "in_progress", "completed", "declined", "blocked" |',
        )
        self.assertNotEqual(mutated, self.tracker)
        errors = self._check(tracker=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "status enum" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_tracker_global_completed_renamed(self) -> None:
        mutated = self.tracker.replace("- `completed`", "- `finished`")
        self.assertNotEqual(mutated, self.tracker)
        errors = self._check(tracker=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "legal" in e and "completed" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_tracker_stage6_dropped(self) -> None:
        """Adverse-value mutation (codex round-3 P1): the state_tracker enum
        reverts to '1'..'5' — must fire."""
        mutated = self.tracker.replace(
            '"1", "2", "2.5", "3", "4", "3p", "4p", "4.5", "5", "6"',
            '"1", "2", "2.5", "3", "4", "3p", "4p", "4.5", "5"',
        )
        self.assertNotEqual(mutated, self.tracker)
        errors = self._check(tracker=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "stage_id enum" in e for e in errors),
            msg=f"errors: {errors}",
        )
        mutated2 = self.tracker.replace('"6": {', '"6x": {')
        errors2 = self._check(tracker=mutated2)
        self.assertTrue(
            any(e.startswith("invariant 4") and "Stage 6 entry" in e for e in errors2),
            msg=f"errors: {errors2}",
        )

    # --- codex round-11 witnesses ---

    def test_inv4_skill_stage6_made_mandatory_in_section(self) -> None:
        """Adverse-value mutation (codex round-11 P1): the SKILL Stage 6
        section flips non-mandatory to mandatory — must fire."""
        mutated = self.skill.replace(
            "Stage 6 is non-mandatory — the user may decline it",
            "Stage 6 is mandatory — the user may not decline it",
        )
        self.assertNotEqual(mutated, self.skill)
        errors = self._check(skill=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "decline-path" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_proto_stage6_made_mandatory(self) -> None:
        mutated = self.proto.replace(
            "Stage 6 is non-mandatory — the user may decline it at that checkpoint",
            "Stage 6 is mandatory — the user may not decline it",
        )
        self.assertNotEqual(mutated, self.proto)
        errors = self._check(proto=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "decline" in e and self.mod.PROTO in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_skippable_label_flipped(self) -> None:
        """Adverse-value mutation (codex round-11 P1): the `- Skippable:`
        label flips to `- Non-Skippable:` — must fire (line-anchored pin
        includes the label)."""
        mutated = self.orch.replace(
            "- Skippable: Stage 1 (deep-research, if user provides own bibliography)",
            "- Non-Skippable: Stage 1 (deep-research, if user provides own bibliography)",
        )
        self.assertNotEqual(mutated, self.orch)
        errors = self._check(orch=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "skippable-stages" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv4_handoff_destination_rerouted(self) -> None:
        """Adverse-value mutation (codex round-11 P1): the handoff row's
        first cell reroutes Stage 5 -> END — must fire."""
        mutated = self.orch.replace("| Stage 5 -> 6 | Final deliverables", "| Stage 5 -> END | Final deliverables")
        self.assertNotEqual(mutated, self.orch)
        errors = self._check(orch=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "handoff row" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_inv3_reset_iron_rule_names_entry_gate(self) -> None:
        """The reset-boundary iron rule must scope its MANDATORY list to the
        Stage 5 entry gate (codex round-11 P1) — enforced via the content
        lock being on the state machine? No: the rule lives in the
        orchestrator; verify the committed prose carries the scoped form."""
        self.assertIn(
            "MANDATORY checkpoints (Stage 2.5 / 4.5, review decisions, the Stage 5 entry gate) remain MANDATORY",
            self.orch,
        )

    # --- content locks (round-11 endgame) ---

    def test_content_locks_baseline(self) -> None:
        self.assertEqual(self.mod.check_content_locks(), [])

    def test_content_lock_fires_on_any_byte_change(self) -> None:
        """Any single-byte change to a locked reference doc must fire — this
        closes the entire single-edit mutation class for the two
        #528-central operative docs."""
        import hashlib

        for path in self.mod.CONTENT_LOCKS:
            content = (REPO_ROOT / path).read_bytes()
            mutated = content.replace(b"completed", b"finished", 1)
            self.assertNotEqual(mutated, content, msg=path)
            self.assertNotEqual(
                hashlib.sha256(mutated).hexdigest(),
                self.mod.CONTENT_LOCKS[path],
                msg=path,
            )

    # --- scoping discipline ---

    def test_vocab_elsewhere_does_not_satisfy_section_check(self) -> None:
        """Removing the vocabulary from the authority section must fire even
        though the transitions table (outside the section) still carries the
        same canonical string — section-scoped means section-scoped."""
        section = self._authority_section(self.sm)
        mutated_section = section.replace(
            "`finish` / `end` / `done` / `confirm`, or an unambiguous natural-language equivalent",
            "an explicit closing reply",
        )
        self.assertNotEqual(section, mutated_section)
        mutated = self.sm.replace(section, mutated_section)
        self.assertIn(self.mod.VOCAB_CANON, mutated)  # still present outside the section
        errors = self._check(sm=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "acknowledgement-vocabulary" in e for e in errors),
            msg=f"errors: {errors}",
        )


if __name__ == "__main__":
    unittest.main()
