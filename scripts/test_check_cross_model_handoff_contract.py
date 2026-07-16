"""Mutation tests for check_cross_model_handoff_contract.py (#527).

One failing witness per invariant branch, on in-memory mutations of the
committed surfaces.
"""
import unittest
from pathlib import Path

from tests.test_helpers import load_module_from_path, run_script

SCRIPT = Path(__file__).resolve().parent / "check_cross_model_handoff_contract.py"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_module():
    return load_module_from_path("check_cross_model_handoff_contract", SCRIPT)


class HandoffContractLintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()
        cls.shared = (REPO_ROOT / cls.mod.SHARED).read_text(encoding="utf-8")
        cls.orch = (REPO_ROOT / cls.mod.ORCH).read_text(encoding="utf-8")
        cls.owners = {
            p: (REPO_ROOT / p).read_text(encoding="utf-8") for p in cls.mod.OWNERS
        }

    def _check(self, shared=None, orch=None, owners=None):
        return self.mod.check(
            shared if shared is not None else self.shared,
            orch if orch is not None else self.orch,
            owners if owners is not None else self.owners,
        )

    def test_repo_baseline_passes(self) -> None:
        result = run_script(SCRIPT)
        self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
        self.assertIn("PASSED", result.stdout)

    def test_clean_contents_pass(self) -> None:
        self.assertEqual(self._check(), [])

    # --- invariant 1: shared canonical section ---

    def test_shared_section_removed(self) -> None:
        mutated = self.shared.replace("### Cross-model handoff envelope (#527)", "### Handoff notes")
        errors = self._check(shared=mutated)
        self.assertTrue(any(e.startswith("invariant 1") and "missing" in e for e in errors))

    def test_shared_blindness_rule_dropped(self) -> None:
        mutated = self.shared.replace("NEVER forwarded to the cross-model", "forwarded as needed")
        errors = self._check(shared=mutated)
        self.assertTrue(any(e.startswith("invariant 1") for e in errors), msg=f"{errors}")

    def test_shared_agreement_routing_flipped(self) -> None:
        """Adverse-value: agreement re-invokes the owner — must fire."""
        mutated = self.shared.replace(
            "does **not** re-invoke the owner", "re-invokes the owner for confirmation"
        )
        errors = self._check(shared=mutated)
        self.assertTrue(any(e.startswith("invariant 1") for e in errors), msg=f"{errors}")

    def test_shared_failsafe_softened(self) -> None:
        """Adverse-value: malformed result coerced instead of unavailable."""
        mutated = self.shared.replace(
            "[CROSS-MODEL-ERROR: malformed_result]", "a best-effort repair"
        )
        errors = self._check(shared=mutated)
        self.assertTrue(any(e.startswith("invariant 1") for e in errors), msg=f"{errors}")

    def test_shared_flag_unset_promise_dropped(self) -> None:
        mutated = self.shared.replace(
            "owners emit no envelope and behavior is byte-equivalent pre-#527",
            "owners may still emit envelopes",
        )
        errors = self._check(shared=mutated)
        self.assertTrue(any(e.startswith("invariant 1") for e in errors), msg=f"{errors}")

    # --- invariant 2: owner emission pins ---

    def test_owner_fence_dropped(self) -> None:
        for path in self.mod.OWNERS:
            owners = dict(self.owners)
            owners[path] = owners[path].replace("[CROSS-MODEL-HANDOFF v1]", "a clearly-delimited block")
            errors = self._check(owners=owners)
            self.assertTrue(
                any(e.startswith("invariant 2") and path in e for e in errors),
                msg=f"{path}: {errors}",
            )

    def test_owner_kind_swapped(self) -> None:
        """Adverse-value: the DA owner claims enum_comparison — must fire."""
        path = "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md"
        owners = dict(self.owners)
        owners[path] = owners[path].replace("`expected_result: full_return`", "`expected_result: enum_comparison`")
        errors = self._check(owners=owners)
        self.assertTrue(
            any(e.startswith("invariant 2") and path in e for e in errors),
            msg=f"errors: {errors}",
        )

    # --- invariant 3: dispatcher consumer contract ---

    def test_orch_consumer_block_removed(self) -> None:
        mutated = self.orch.replace(
            "**Cross-model handoff consumption (#527, Mode A dispatcher).**",
            "**Handoff notes.**",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 3") and "missing" in e for e in errors))

    def test_orch_recognition_demoted_to_deliverable(self) -> None:
        """Adverse-value: the exact #527 drift risk — the dispatcher treats
        the handoff as an ordinary deliverable — must fire."""
        mutated = self.orch.replace(
            "a transport request, never an ordinary deliverable",
            "an ordinary deliverable to be filed",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 3") for e in errors), msg=f"{errors}")

    def test_orch_divergence_authorship_flipped(self) -> None:
        mutated = self.orch.replace(
            "the rebuttal is the owner's, never the dispatcher's",
            "the dispatcher drafts the rebuttal for efficiency",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 3") for e in errors), msg=f"{errors}")

    def test_orch_full_return_dropped(self) -> None:
        mutated = self.orch.replace(
            "every successful response returns to the owner",
            "responses are summarized by the dispatcher",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 3") for e in errors), msg=f"{errors}")

    # --- invariant 4: prose enums follow the normative module ---

    def test_prose_enum_drift_fires(self) -> None:
        mutated = self.shared.replace(
            "`sound` / `revise_before_freeze` / `fundamental_concern`",
            "`sound` / `revise` / `concern`",
        )
        errors = self._check(shared=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "normative module" in e for e in errors),
            msg=f"errors: {errors}",
        )


if __name__ == "__main__":
    unittest.main()
