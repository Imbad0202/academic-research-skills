"""Unit tests for check_v3_9_2_phase_boundary.py."""
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.test_helpers import run_script

SCRIPT = Path(__file__).resolve().parent / "check_v3_9_2_phase_boundary.py"


def _run() -> subprocess.CompletedProcess:
    return run_script(SCRIPT)


class CheckV392PhaseBoundaryTests(unittest.TestCase):

    def test_repo_baseline_passes(self) -> None:
        """The committed v3.9.2/v3.9.4 branch state must pass the lint."""
        result = _run()
        self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
        self.assertIn("PASSED", result.stdout)
        self.assertIn("23 Bucket A", result.stdout)
        self.assertIn("16 Bucket B/C/D", result.stdout)

    def test_module_invariants(self) -> None:
        """BUCKET counts must match classification doc (23 + 16 = 39)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "check_v3_9_2_phase_boundary", SCRIPT
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertEqual(len(module.BUCKET_A_AGENTS), 23)
        self.assertEqual(len(module.BUCKET_BCD_AGENTS), 16)
        # No agent appears in both buckets
        overlap = set(module.BUCKET_A_AGENTS) & set(module.BUCKET_BCD_AGENTS)
        self.assertEqual(overlap, set(), msg=f"agents in both buckets: {overlap}")
        # All 39 agent paths are unique (23 A + 16 BCD)
        all_paths = module.BUCKET_A_AGENTS + module.BUCKET_BCD_AGENTS
        self.assertEqual(len(all_paths), len(set(all_paths)),
                         msg="duplicate paths across buckets")

    def test_required_phrases_constant(self) -> None:
        """REQUIRED_PHRASES must include the version-neutral load-bearing markers.
        Version-specific markers (Phase Boundary, Enforcement) are handled via
        PHASE_BOUNDARY_RE / ENFORCEMENT_RE regexes (widened to v3.9.2|v3.9.4 in v3.9.4).
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "check_v3_9_2_phase_boundary", SCRIPT
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        required = set(module.REQUIRED_PHRASES)
        self.assertIn("MUST NOT", required)
        self.assertIn("MAY READ", required)
        # Version-specific markers are now regex-based
        self.assertTrue(
            hasattr(module, "PHASE_BOUNDARY_RE"),
            "PHASE_BOUNDARY_RE must exist (widened to v3.9.2|v3.9.4)"
        )
        self.assertTrue(
            hasattr(module, "ENFORCEMENT_RE"),
            "ENFORCEMENT_RE must exist (widened to v3.9.2|v3.9.4)"
        )
        # Both regexes must match either version
        self.assertIsNotNone(module.PHASE_BOUNDARY_RE.search("## Phase Boundary (v3.9.2)"))
        self.assertIsNotNone(module.PHASE_BOUNDARY_RE.search("## Phase Boundary (v3.9.4)"))
        self.assertIsNotNone(module.ENFORCEMENT_RE.search("Enforcement (v3.9.2)"))
        self.assertIsNotNone(module.ENFORCEMENT_RE.search("Enforcement (v3.9.4)"))

    def test_timeline_extraction_agent_in_bucket_a(self) -> None:
        """timeline_extraction_agent.md (v3.9.4) must be in BUCKET_A_AGENTS."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "check_v3_9_2_phase_boundary", SCRIPT
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertIn(
            "deep-research/agents/timeline_extraction_agent.md",
            module.BUCKET_A_AGENTS,
            "timeline_extraction_agent.md must be in BUCKET_A_AGENTS (v3.9.4 Phase 2 sibling)"
        )


if __name__ == "__main__":
    unittest.main()
