"""Static regression contract for #737 coverage-bounded claims language."""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class ClaimVerificationCoverageContractTests(unittest.TestCase):
    def test_mode_two_names_registered_claim_denominator(self) -> None:
        protocol = (
            ROOT / "academic-pipeline/references/claim_verification_protocol.md"
        ).read_text(encoding="utf-8")
        agent = (
            ROOT / "academic-pipeline/agents/integrity_verification_agent.md"
        ).read_text(encoding="utf-8")
        self.assertIn("100% of **registered claims**", protocol)
        self.assertIn("semantic extraction completeness remains unknown", protocol)
        self.assertIn("semantic extraction completeness remains unknown", agent)
        self.assertNotIn("Mode 2 (final-check): 100% of claims", protocol)
        self.assertNotIn("Mode 2 (final-check): 100% of claims", agent)

    def test_mechanical_gap_detector_keeps_semantic_limit_visible(self) -> None:
        protocol = (
            ROOT / "academic-pipeline/references/claim_verification_protocol.md"
        ).read_text(encoding="utf-8")
        flattened = " ".join(protocol.split())
        self.assertIn("scripts/claim_registry_coverage.py", protocol)
        self.assertIn(
            "semantic_extraction_coverage: not_machine_detectable", protocol
        )
        self.assertIn("citation-bearing sentences", flattened)
        self.assertIn("quantitative sentences", flattened)
        self.assertIn("claim-registry/1.0", protocol)
        self.assertIn("exact raw draft bytes", protocol)
        self.assertIn("--validate-report", protocol)
        self.assertIn("E1-COVERAGE-UNRESOLVED", protocol)
        self.assertIn("mixed_or_partial_registry_coverage", protocol)
        self.assertIn("Both non-clean states contribute", protocol)

    def test_current_skill_surface_has_no_unqualified_guarantees(self) -> None:
        skill = (ROOT / "academic-pipeline/SKILL.md").read_text(encoding="utf-8")
        prohibited = (
            "reproducible quality gates",
            "100% reference and data verification",
            "data are 100% correct",
            "100% reference/citation/data verification",
            "must achieve 100% pass",
            "Standardized workflow producing consistent quality assurance each time",
            "Same input follows the same workflow across different sessions",
        )
        for phrase in prohibited:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, skill)
        self.assertIn("coverage-bounded integrity checks", skill)
        self.assertIn("Auditability and replay boundaries", skill)

    def test_reexecution_reference_disclaims_output_equivalence(self) -> None:
        text = (
            ROOT / "academic-pipeline/references/reproducibility_audit.md"
        ).read_text(encoding="utf-8")
        self.assertIn("does not promise consistent outputs", text)
        self.assertIn("not a byte-replay guarantee", text)

    def test_current_integrity_authorities_bound_every_percentage_denominator(self) -> None:
        paths = (
            ROOT / "academic-pipeline/agents/integrity_verification_agent.md",
            ROOT / "academic-pipeline/references/integrity_review_protocol.md",
        )
        prohibited = (
            "perform 100% verification of all references",
            "Confirm the revised paper is 100% correct",
            "Phase E (100% claim verification)",
            "Phase E verifies 100% of all quantitative/factual claims",
            "E1 (claim extraction) on ALL claims",
            "References 100%, statistical data 100%",
            "Purpose**: Ensure all references and data",
            "Purpose**: Confirm the revised paper is 100% correct",
        )
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for phrase in prohibited:
                with self.subTest(path=path.name, phrase=phrase):
                    self.assertNotIn(phrase, text)
        joined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        self.assertIn("semantic extraction completeness remains unknown", joined)
        self.assertIn("100% of registered claims", joined)

    def test_integrity_handoff_carries_replayable_coverage_pointer(self) -> None:
        handoff = (ROOT / "shared/handoff_schemas.md").read_text(encoding="utf-8")
        for token in (
            "claim_registry_coverage",
            "report_sha256",
            "draft_raw_sha256",
            "registry_raw_sha256",
            "E1-COVERAGE-UNRESOLVED",
        ):
            self.assertIn(token, handoff)


if __name__ == "__main__":
    unittest.main()
