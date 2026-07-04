"""Unit tests for check_setup_cross_model_parity.py (#491 fold-in)."""
import unittest
from pathlib import Path

from tests.test_helpers import run_script

SCRIPT = Path(__file__).resolve().parent / "check_setup_cross_model_parity.py"

EN_OK = 'export ARS_CROSS_MODEL="gpt-5.5"\n# or: export ARS_CROSS_MODEL="gemini-3.1-pro-preview"\n'
ZH_OK = EN_OK
CANONICAL_OK = "| GPT-5.5 | `gpt-5.5` | ... |\n| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | ... |\n"


def _load_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_setup_cross_model_parity", SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SetupCrossModelParityTests(unittest.TestCase):

    def test_repo_baseline_passes(self) -> None:
        """The committed SETUP + canonical doc state must pass."""
        result = run_script(SCRIPT)
        self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
        self.assertIn("PASSED", result.stdout)

    def test_clean_fixture_passes(self) -> None:
        module = _load_module()
        self.assertEqual(module.check(EN_OK, ZH_OK, CANONICAL_OK), [])

    def test_en_zh_drift_fails(self) -> None:
        """One-sided edit (the B4-F02 shape: en updated, zh-TW forgotten)."""
        module = _load_module()
        zh_stale = 'export ARS_CROSS_MODEL="gpt-5.4-pro"\n'
        canonical = CANONICAL_OK + "| legacy | `gpt-5.4-pro` | ... |\n"
        errors = module.check(EN_OK, zh_stale, canonical)
        self.assertTrue(any("drift" in e for e in errors), msg=f"errors: {errors}")

    def test_unknown_model_fails(self) -> None:
        """Example naming a model outside the canonical lineup."""
        module = _load_module()
        bad = 'export ARS_CROSS_MODEL="gpt-9.9-imaginary"\n'
        errors = module.check(bad, bad, CANONICAL_OK)
        self.assertTrue(
            any("gpt-9.9-imaginary" in e and "canonical" in e for e in errors),
            msg=f"errors: {errors}",
        )

    def test_zero_examples_fails_closed(self) -> None:
        """Regex-went-stale / block-removed must be an error, not a pass."""
        module = _load_module()
        errors = module.check("no examples here", ZH_OK, CANONICAL_OK)
        self.assertTrue(
            any("Fail-closed" in e for e in errors), msg=f"errors: {errors}"
        )

    def test_commented_example_lines_are_extracted(self) -> None:
        """`# or:` alternates count — they are user-pasteable examples too."""
        module = _load_module()
        ids = module.extract_ids(EN_OK)
        self.assertEqual(ids, ["gpt-5.5", "gemini-3.1-pro-preview"])


if __name__ == "__main__":
    unittest.main()
