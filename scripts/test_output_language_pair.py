"""Unit tests for the #862 Phase-1 output-language-pair contract helpers.

The helpers under test live in `scripts/check_spec_consistency.py`; the registry
itself lives in `shared/output_language_pair.md` and is parsed from the real file,
never duplicated here. The `tests/fixtures/output_language_pair/` corpus drives the
same helpers from Schema-4 excerpts, so the four deterministic cases (omitted,
default, unsupported, malformed) are pinned twice: as synthetic input and as text.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

from scripts import check_spec_consistency as csc

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "shared/output_language_pair.md"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "output_language_pair"

_FENCED_YAML = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)

_REGISTRY_TEMPLATE = """\
# Synthetic contract

## Registry

<!-- output-language-pair-registry:start -->
| Token | L1 language | L1 script | L2 language | L2 script | Status |
|-------|-------------|-----------|-------------|-----------|--------|
{rows}
<!-- output-language-pair-registry:end -->
"""


def _contract_with_rows(rows: str) -> str:
    return _REGISTRY_TEMPLATE.replace("{rows}", rows.rstrip("\n"))


class OutputLanguagePairRegistryTest(unittest.TestCase):
    """The registry is parsed from the shipped contract, not from a test copy."""

    def setUp(self) -> None:
        self.registry = csc.parse_output_language_pair_registry(
            CONTRACT.read_text(encoding="utf-8")
        )

    def test_default_entry_is_the_legacy_pair(self) -> None:
        self.assertEqual(sorted(self.registry), [csc.LEGACY_DEFAULT_OUTPUT_LANGUAGE_PAIR])
        self.assertEqual(
            self.registry[csc.LEGACY_DEFAULT_OUTPUT_LANGUAGE_PAIR]["status"], "default"
        )

    def test_entry_declares_roles_and_script_classes(self) -> None:
        entry = self.registry[csc.LEGACY_DEFAULT_OUTPUT_LANGUAGE_PAIR]
        self.assertIn("Traditional Chinese", entry["l1_language"])
        self.assertEqual(entry["l1_script"], "CJK")
        self.assertIn("English", entry["l2_language"])
        self.assertEqual(entry["l2_script"], "Latin")

    def test_no_unary_entry_parses(self) -> None:
        # Every Phase-1 entry declares two language slots; a unary row has no L2
        # language column to fill, so the table shape itself rejects it.
        for entry in self.registry.values():
            self.assertTrue(entry["l1_language"])
            self.assertTrue(entry["l2_language"])

    def test_missing_registry_markers_raise(self) -> None:
        with self.assertRaises(ValueError):
            csc.parse_output_language_pair_registry("# Contract\n\nno registry here\n")

    def test_unary_entry_table_raises(self) -> None:
        text = (
            "# Synthetic contract\n\n"
            "<!-- output-language-pair-registry:start -->\n"
            "| Token | L1 language | L1 script | Status |\n"
            "|-------|-------------|-----------|--------|\n"
            "| `zh-tw` | Traditional Chinese (`zh-TW`) | CJK | default |\n"
            "<!-- output-language-pair-registry:end -->\n"
        )
        with self.assertRaises(ValueError) as ctx:
            csc.parse_output_language_pair_registry(text)
        self.assertIn("single-language pairs are not supported", str(ctx.exception))

    def test_malformed_registry_token_raises(self) -> None:
        with self.assertRaises(ValueError):
            csc.parse_output_language_pair_registry(
                _contract_with_rows("| `ZH-TW-EN` | Traditional Chinese | CJK | English | Latin | default |")
            )

    def test_duplicate_registry_token_raises(self) -> None:
        row = "| `zh-tw-en` | Traditional Chinese | CJK | English | Latin | default |"
        with self.assertRaises(ValueError):
            csc.parse_output_language_pair_registry(_contract_with_rows(f"{row}\n{row}"))

    def test_entry_without_an_l2_language_raises(self) -> None:
        # P2-e: a row that fills one language slot and leaves the other empty is not a
        # pair; it must fail the parse rather than validate as a usable entry.
        with self.assertRaises(ValueError) as ctx:
            csc.parse_output_language_pair_registry(
                _contract_with_rows(
                    "| `zh-tw-en` | Traditional Chinese | CJK |  | Latin | default |"
                )
            )
        self.assertIn("must declare both an L1 and an L2 language", str(ctx.exception))

    def test_entry_declaring_one_language_twice_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            csc.parse_output_language_pair_registry(
                _contract_with_rows(
                    "| `en-en` | English (`en`) | Latin | English (`en`) | Latin | default |"
                )
            )
        self.assertIn("declares the same language twice", str(ctx.exception))

    def test_empty_registry_raises(self) -> None:
        text = (
            "# Synthetic contract\n\n"
            "<!-- output-language-pair-registry:start -->\n"
            "| Token | L1 language | L2 language |\n"
            "|-------|-------------|-------------|\n"
            "<!-- output-language-pair-registry:end -->\n"
        )
        with self.assertRaises(ValueError) as ctx:
            csc.parse_output_language_pair_registry(text)
        self.assertIn("no entries", str(ctx.exception))


class OutputLanguagePairValidationTest(unittest.TestCase):
    """`validate_output_language_pair` is the visible-failure gate (no fallback)."""

    def setUp(self) -> None:
        self.registry = csc.parse_output_language_pair_registry(
            CONTRACT.read_text(encoding="utf-8")
        )

    def test_omitted_field_is_valid_legacy(self) -> None:
        self.assertEqual(csc.validate_output_language_pair(csc.PAIR_FIELD_ABSENT, self.registry), [])

    def test_default_token_is_valid(self) -> None:
        self.assertEqual(
            csc.validate_output_language_pair(
                csc.LEGACY_DEFAULT_OUTPUT_LANGUAGE_PAIR, self.registry
            ),
            [],
        )

    def test_unregistered_pair_is_rejected_and_names_the_registry(self) -> None:
        errors = csc.validate_output_language_pair("ja-en", self.registry)
        self.assertEqual(len(errors), 1)
        self.assertIn("unsupported token", errors[0])
        self.assertIn(csc.OUTPUT_LANGUAGE_PAIR_CONTRACT, errors[0])
        self.assertIn("registry holds: zh-tw-en", errors[0])

    def test_unary_token_is_rejected_as_unsupported(self) -> None:
        errors = csc.validate_output_language_pair("zh-tw", self.registry)
        self.assertEqual(len(errors), 1)
        self.assertIn("unsupported token", errors[0])

    def test_malformed_values_are_rejected_and_name_the_registry(self) -> None:
        for malformed in (None, 42, True, ["zh-tw-en"], {"pair": "zh-tw-en"}, "", "   "):
            with self.subTest(malformed=malformed):
                errors = csc.validate_output_language_pair(malformed, self.registry)
                self.assertTrue(errors, msg=f"{malformed!r} must be rejected")
                for error in errors:
                    self.assertIn(csc.OUTPUT_LANGUAGE_PAIR_CONTRACT, error)

    def test_padded_and_newline_terminated_values_are_unsupported(self) -> None:
        # P1-3: the comparison is raw. Registry tokens are opaque, so a padded value is a
        # different value, not the entry it resembles — normalizing it would accept a token
        # the contract never declared.
        for padded in (" zh-tw-en", "zh-tw-en ", " zh-tw-en ", "zh-tw-en\n", "\tzh-tw-en"):
            with self.subTest(value=padded):
                errors = csc.validate_output_language_pair(padded, self.registry)
                self.assertEqual(len(errors), 1, msg=f"{padded!r} must be rejected")
                self.assertIn("unsupported token", errors[0])
                self.assertIn(csc.OUTPUT_LANGUAGE_PAIR_CONTRACT, errors[0])

    def test_whitespace_only_value_is_an_empty_token_not_an_unsupported_one(self) -> None:
        errors = csc.validate_output_language_pair("   ", self.registry)
        self.assertEqual(len(errors), 1)
        self.assertIn("non-empty string token", errors[0])

    def test_null_is_not_treated_as_absent(self) -> None:
        # A present-but-unusable value never collapses into the legacy state.
        self.assertNotEqual(csc.validate_output_language_pair(None, self.registry), [])


class AdvertisedPairTokenTest(unittest.TestCase):
    """The tokenizer feeds the "no unregistered pair advertised" parity rule."""

    def test_backticked_token_is_collected(self) -> None:
        self.assertEqual(
            csc.advertised_output_language_pair_tokens("the pair `zh-tw-en` is the default"),
            {"zh-tw-en"},
        )

    def test_backticked_span_that_is_not_a_token_is_ignored(self) -> None:
        self.assertEqual(
            csc.advertised_output_language_pair_tokens(
                "`{en: list[string], zh_tw: list[string]}` and `output_language_pair`"
            ),
            set(),
        )

    def test_bare_tokens_are_never_collected(self) -> None:
        # P2-c: the backtick is the contract's own spelling rule, so the scan accepts only
        # that spelling. The bare-token branch read ordinary hyphenated prose as an
        # advertised pair on any line that mentioned the field, and it missed a bare
        # two-subtag pair; one uniform rule replaces both halves of that guesswork.
        self.assertEqual(
            csc.advertised_output_language_pair_tokens(
                "the output_language_pair token zh-tw-en selects the pair"
            ),
            set(),
        )
        self.assertEqual(
            csc.advertised_output_language_pair_tokens("an up-to-date checklist line"),
            set(),
        )
        self.assertEqual(
            csc.advertised_output_language_pair_tokens("the output_language_pair is es-en here"),
            set(),
        )
        self.assertEqual(
            csc.advertised_output_language_pair_tokens("the pair is `zh-tw-en`"),
            {"zh-tw-en"},
        )


class OutputLanguagePairFixtureTest(unittest.TestCase):
    """The four deterministic cases, driven from tests/fixtures/output_language_pair/."""

    def setUp(self) -> None:
        self.registry = csc.parse_output_language_pair_registry(
            CONTRACT.read_text(encoding="utf-8")
        )

    def test_fixture_corpus_covers_the_four_cases(self) -> None:
        self.assertEqual(
            sorted(path.name for path in FIXTURE_ROOT.iterdir() if path.is_dir()),
            ["default", "malformed", "omitted", "unsupported"],
        )

    def test_fixture_cases_match_expected_outcomes(self) -> None:
        for fixture in sorted(path for path in FIXTURE_ROOT.iterdir() if path.is_dir()):
            expected = yaml.safe_load((fixture / "expected.yaml").read_text(encoding="utf-8"))
            blocks = _FENCED_YAML.findall((fixture / "input.md").read_text(encoding="utf-8"))
            cases = expected["cases"]
            with self.subTest(fixture=fixture.name):
                self.assertEqual(len(blocks), len(cases), "one YAML block per expected case")
                for block, case in zip(blocks, cases):
                    data = yaml.safe_load(block)
                    if "output_language_pair" in data:
                        value = data["output_language_pair"]
                    else:
                        value = csc.PAIR_FIELD_ABSENT
                    errors = csc.validate_output_language_pair(value, self.registry)
                    self.assertEqual(
                        errors == [],
                        case["expected_valid"],
                        msg=f"{fixture.name}/{case['name']}: {errors!r}",
                    )
                    expected_status = ("legacy" if value is csc.PAIR_FIELD_ABSENT else "malformed" if errors and "must be a string token" in " ".join(errors) else "default" if not errors else "unsupported")
                    self.assertEqual(case["expected_status"], expected_status)
                    for needle in case["error_contains"]:
                        self.assertTrue(
                            any(needle in error for error in errors),
                            msg=f"{fixture.name}/{case['name']}: {needle!r} not in {errors!r}",
                        )
                    # The legacy object keys are untouched by the additive field.
                    self.assertEqual(sorted(data["abstract"]), ["chinese", "english"])
                    self.assertEqual(sorted(data["keywords"]), ["en", "zh_tw"])


if __name__ == "__main__":
    unittest.main()
