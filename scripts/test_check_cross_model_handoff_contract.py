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

    def test_owner_header_typo_fires(self) -> None:
        """codex round-1 P1: a checkpoint_knd typo in an owner's declaration
        would emit malformed envelopes — must fire."""
        path = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
        owners = dict(self.owners)
        owners[path] = owners[path].replace(
            "`checkpoint_kind: editorial_decision`", "`checkpoint_knd: editorial_decision`"
        )
        errors = self._check(owners=owners)
        self.assertTrue(
            any(e.startswith("invariant 2") and path in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_owner_header_spellings_pinned(self) -> None:
        """codex round-12 P1: correlation_id/owner_decision typos and a
        wrong owner_agent value in an owner instruction must fire — each
        would emit envelopes the normative parser rejects."""
        path = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
        mutations = [
            ("a `correlation_id` you choose", "a `correlation_idd` you choose"),
            ("`owner_decision` header", "`owner_decison` header"),
            ("`owner_agent: editorial_synthesizer_agent`", "`owner_agent: research_architect_agent`"),
        ]
        for old, new in mutations:
            owners = dict(self.owners)
            self.assertIn(old, owners[path], msg=old)
            owners[path] = owners[path].replace(old, new)
            errors = self._check(owners=owners)
            self.assertTrue(
                any(e.startswith("invariant 2") and path in e for e in errors),
                msg=f"{old} -> {new}: {errors}",
            )

    def test_owner_blindness_clause_dropped(self) -> None:
        path = "deep-research/agents/research_architect_agent.md"
        owners = dict(self.owners)
        owners[path] = owners[path].replace("never forwarded to the cross-model", "forwarded as context")
        errors = self._check(owners=owners)
        self.assertTrue(
            any(e.startswith("invariant 2") and path in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_owner_payload_exclusion_inverted(self) -> None:
        """codex round-2 P1: inverting the editorial payload exclusion would
        leak the primary judgment into the transported payload — must fire."""
        path = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
        owners = dict(self.owners)
        owners[path] = owners[path].replace(
            "**Never include your decision, the scoring matrix outcome, or your rationale**",
            "**Include your decision for context**",
        )
        errors = self._check(owners=owners)
        self.assertTrue(
            any(e.startswith("invariant 2") and path in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_shared_data_minimization_dropped(self) -> None:
        """codex round-4 P1 (boundary): the data-minimization rule flips to
        permitting identity metadata — must fire."""
        mutated = self.shared.replace(
            "Sanitized also means data-minimized: strip personal names, affiliations, and private URLs not essential to the judgment",
            "Identity and location metadata may be included for context",
        )
        errors = self._check(shared=mutated)
        self.assertTrue(any(e.startswith("invariant 1") for e in errors), msg=f"{errors}")

    def test_shared_all_three_fields_narrowed(self) -> None:
        mutated = self.shared.replace(
            "Structured decisions carry ALL THREE fields (`decision`, `drivers`, `confidence`)",
            "Structured decisions carry a decision field",
        )
        errors = self._check(shared=mutated)
        self.assertTrue(any(e.startswith("invariant 1") for e in errors), msg=f"{errors}")

    def test_shared_owner_agent_header_renamed(self) -> None:
        mutated = self.shared.replace("owner_agent:", "agent:")
        errors = self._check(shared=mutated)
        self.assertTrue(any(e.startswith("invariant 1") for e in errors), msg=f"{errors}")

    def test_owner_consent_predicate_inverted(self) -> None:
        """codex round-5 P1: flipping an owner's consent predicate must fire."""
        path = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
        owners = dict(self.owners)
        owners[path] = owners[path].replace(
            "the consent gate in `shared/cross_model_verification.md` has been passed",
            "the consent gate in `shared/cross_model_verification.md` has not been passed",
        )
        errors = self._check(owners=owners)
        self.assertTrue(
            any(e.startswith("invariant 2") and path in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_orch_trigger_narrowed_to_v1_only(self) -> None:
        """codex round-5 P1: the Mode-A trigger must stay any-version
        (generous detection) — narrowing it must fire."""
        mutated = self.orch.replace("ANY version, detection is generous", "the v1 fence only")
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 3") for e in errors), msg=f"{errors}")

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

    def test_orch_blindness_clause_dropped(self) -> None:
        """codex round-11 P1: the dispatcher's never-forwarded clause flips
        to full-envelope — must fire."""
        mutated = self.orch.replace(
            "the `owner_decision` header is never forwarded — blindness",
            "the full envelope is forwarded for context",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 3") for e in errors), msg=f"{errors}")

    def test_orch_flag_unset_transport_flipped(self) -> None:
        mutated = self.orch.replace(
            "a stray envelope is logged `[CROSS-MODEL-SKIPPED]` and not transported",
            "a stray envelope is transported anyway",
        )
        errors = self._check(orch=mutated)
        self.assertTrue(any(e.startswith("invariant 3") for e in errors), msg=f"{errors}")

    def test_prose_enum_owner_rewired_to_full_return_fires(self) -> None:
        """codex round-11 P1: each triple is pinned independently — flipping
        an enum owner's result shape to full_return must fire."""
        mutated = self.shared.replace(
            "`design_freeze` (`research_architect_agent`) is `enum_comparison`",
            "`design_freeze` (`research_architect_agent`) is `full_return`",
        )
        errors = self._check(shared=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "design_freeze" in e for e in errors),
            msg=f"errors: {errors}",
        )

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

    def test_prose_triple_rewire_fires(self) -> None:
        """codex round-10 P1: rewiring the shared kind/owner/result triple
        must fail against the module-derived pins."""
        mutated = self.shared.replace(
            "`da_critique` (`devils_advocate_reviewer_agent`) is `full_return`",
            "`da_critique` (`research_architect_agent`) is `enum_comparison`",
        )
        errors = self._check(shared=mutated)
        self.assertTrue(
            any(e.startswith("invariant 4") and "EXPECTED_OWNERS" in e for e in errors),
            msg=f"errors: {errors}",
        )

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
