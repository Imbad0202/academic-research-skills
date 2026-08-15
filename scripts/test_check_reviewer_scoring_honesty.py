"""Mutation tests for check_reviewer_scoring_honesty.py."""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from check_reviewer_scoring_honesty import LIVE_FILES
from tests.test_helpers import run_script


SCRIPT = Path(__file__).resolve().parent / "check_reviewer_scoring_honesty.py"
REPO_ROOT = SCRIPT.parent.parent


def _run(root: Path) -> subprocess.CompletedProcess:
    return run_script(SCRIPT, "--root", str(root))


def _copy_live_tree(destination: Path) -> None:
    for rel in LIVE_FILES:
        source = REPO_ROOT / rel
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _append(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


class TestReviewerScoringHonesty(unittest.TestCase):
    def test_real_repo_passes(self) -> None:
        result = _run(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_required_surface_fails_loud(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            (root / LIVE_FILES[0]).unlink()
            result = _run(root)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_fixed_decision_mapping_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper-reviewer/references/quality_rubrics.md",
                "\n≥80 Accept; 65-79 Minor; 50-64 Major; <50 Reject\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("fixed 0-100 decision boundary", result.stderr)

    def test_weighted_total_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper-reviewer/templates/peer_review_report_template.md",
                "\nOverall Score = weighted dimension sum\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("weighted reviewer result", result.stderr)

    def test_cross_domain_source_quota_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper/agents/literature_strategist_agent.md",
                "\n| IMRaD | 20 | 25-40 |\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("cross-domain source quota", result.stderr)

    def test_fixed_peer_reviewed_ratio_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper/agents/literature_strategist_agent.md",
                "\nPeer-reviewed ratio >= 70%\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("fixed peer-reviewed ratio", result.stderr)

    def test_not_calibrated_witness_is_required(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            path = root / "academic-paper-reviewer/references/quality_rubrics.md"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "`NOT_CALIBRATED` — the required default",
                    "`UNMEASURED` — the required default",
                ),
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing honesty witness", result.stderr)

    def test_standard_reviewer_cannot_offer_profile_upgrade(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper-reviewer/agents/eic_agent.md",
                "\nReplace with PROFILE_MEASURED when a profile name is supplied.\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("seat-level measured-profile upgrade", result.stderr)

    def test_statistical_completeness_score_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper-reviewer/agents/methodology_reviewer_agent.md",
                "\nStatistical reporting completeness score: Adequate\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("retired statistical completeness score", result.stderr)

    def test_scalar_checkpoint_comparison_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-pipeline/agents/pipeline_orchestrator_agent.md",
                "\nQuality indicators: [score if available]\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("scalar checkpoint quality comparison", result.stderr)

    def test_live_typed_trajectory_overclaim_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "docs/ARCHITECTURE.md",
                "\nCriterion trajectory visualization ships by default.\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("live typed-trajectory overclaim", result.stderr)

    def test_mechanical_confidence_weighting_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper-reviewer/agents/editorial_synthesizer_agent.md",
                "\nA Score-5 finding takes precedence over two Score-2 findings.\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("mechanical confidence weighting", result.stderr)

    def test_confidence_cannot_govern_example_arbitration(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper-reviewer/examples/interdisciplinary_review_example.md",
                "\nPer-finding Confidence governs arbitration.\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("confidence-driven arbitration", result.stderr)

    def test_reviewer_workflow_cannot_restore_numeric_scoring_label(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper/SKILL.md",
                "\nPeer review — five-dimension scoring\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("retired reviewer scoring label", result.stderr)

    def test_failure_path_cannot_restore_dimension_score_threshold(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_live_tree(root)
            _append(
                root,
                "academic-paper/references/failure_paths.md",
                "\nTwo or more of the five dimensions\nscored below 60.\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("fixed dimension-score rejection threshold", result.stderr)


if __name__ == "__main__":
    unittest.main()
