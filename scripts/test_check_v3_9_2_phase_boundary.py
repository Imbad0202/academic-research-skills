"""Unit tests for check_v3_9_2_phase_boundary.py."""
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts._test_helpers import run_script

SCRIPT = Path(__file__).resolve().parent / "check_v3_9_2_phase_boundary.py"


def _run() -> subprocess.CompletedProcess:
    return run_script(SCRIPT)


class CheckV392PhaseBoundaryTests(unittest.TestCase):

    def test_repo_baseline_passes(self) -> None:
        """The committed v3.9.2 branch state must pass the lint."""
        result = _run()
        self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
        self.assertIn("PASSED", result.stdout)
        self.assertIn("22 Bucket A", result.stdout)
        self.assertIn("16 Bucket B/C/D", result.stdout)

    def test_module_invariants(self) -> None:
        """BUCKET counts must match classification doc (22 + 16 = 38)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "check_v3_9_2_phase_boundary", SCRIPT
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertEqual(len(module.BUCKET_A_AGENTS), 22)
        self.assertEqual(len(module.BUCKET_BCD_AGENTS), 16)
        # No agent appears in both buckets
        overlap = set(module.BUCKET_A_AGENTS) & set(module.BUCKET_BCD_AGENTS)
        self.assertEqual(overlap, set(), msg=f"agents in both buckets: {overlap}")
        # All 38 agent paths are unique
        all_paths = module.BUCKET_A_AGENTS + module.BUCKET_BCD_AGENTS
        self.assertEqual(len(all_paths), len(set(all_paths)),
                         msg="duplicate paths across buckets")

    def test_required_phrases_constant(self) -> None:
        """REQUIRED_PHRASES must include the four load-bearing markers."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "check_v3_9_2_phase_boundary", SCRIPT
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        required = set(module.REQUIRED_PHRASES)
        self.assertIn("Phase Boundary (v3.9.2)", required)
        self.assertIn("MUST NOT", required)
        self.assertIn("MAY READ", required)
        self.assertIn("Enforcement (v3.9.2)", required)


if __name__ == "__main__":
    unittest.main()
