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

    def _check(self, skill=None, orch=None, sm=None, proto=None):
        return self.mod.check(
            skill if skill is not None else self.skill,
            orch if orch is not None else self.orch,
            sm if sm is not None else self.sm,
            proto if proto is not None else self.proto,
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
        self.assertTrue(any(e.startswith("invariant 4") and "transition row" in e for e in errors))

    def test_inv4_decline_row_removed(self) -> None:
        mutated = self.sm.replace(
            "| checkpoint | completed | User declines Stage 6 |",
            "| checkpoint | completed | n/a |",
        )
        errors = self._check(sm=mutated)
        self.assertTrue(any(e.startswith("invariant 4") and "transition row" in e for e in errors))

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
        self.assertTrue(any(e.startswith("invariant 4") and "terminal wiring" in e for e in errors))

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
