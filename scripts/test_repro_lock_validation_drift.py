"""Drift guard: the nested repro_lock sub-shape in
experiment_provenance_entry.schema.json MUST stay in sync with the canonical
field set in scripts/repro_lock_validation.py (#260 D1 drift guard).

The repro_lock shape is now declared in TWO places:
  1. scripts/repro_lock_validation.py REQUIRED_* constants (single source of
     truth, also imported by scripts/check_repro_lock.py).
  2. The nested `repro_lock` sub-object inside
     shared/contracts/passport/experiment_provenance_entry.schema.json (each
     experiment_provenance[] entry carries its own lock).

Without this test the two copies silently diverge over time — a field added to
the standalone validator but forgotten in the nested schema (or vice versa)
would pass every other gate. This test asserts the required-key sets are equal
at the top level AND inside each sub-block, that the supported-value constants
equal the schema's `const` values, and that validate_block and the nested schema
give the same pass/fail answer for each required value tried against a fixed set
of wrong and edge-case values (#1050). Extra keys are the one known difference:
the nested schema rejects them and validate_block allows them. A passing run
shows agreement on the tried values only, not on every possible value.

Run:
    python -m unittest scripts.test_repro_lock_validation_drift -v
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from jsonschema import Draft202012Validator  # noqa: E402

from repro_lock_validation import (  # noqa: E402
    REQUIRED_CROSSMODEL,
    REQUIRED_EXTERNAL,
    REQUIRED_FIELDS,
    REQUIRED_MATERIALS,
    REQUIRED_MODEL,
    REQUIRED_PROMPTS,
    SUPPORTED_HASH_TIMINGS,
    SUPPORTED_SCHEMA_VERSIONS,
    validate_block,
)

ENTRY_SCHEMA = REPO / "shared/contracts/passport/experiment_provenance_entry.schema.json"


def _nested_repro_lock() -> dict:
    schema = json.loads(ENTRY_SCHEMA.read_text(encoding="utf-8"))
    return schema["properties"]["repro_lock"]


class ReproLockDriftTest(unittest.TestCase):
    """The nested schema's required keys equal the shared canonical constants."""

    def setUp(self) -> None:
        self.lock = _nested_repro_lock()

    def test_top_level_required_matches_canonical(self) -> None:
        nested = set(self.lock["required"])
        self.assertEqual(
            nested,
            REQUIRED_FIELDS,
            msg="nested repro_lock top-level required drifted from "
            f"repro_lock_validation.REQUIRED_FIELDS: only-in-schema="
            f"{nested - REQUIRED_FIELDS}, only-in-constant={REQUIRED_FIELDS - nested}",
        )

    def test_sub_block_required_match_canonical(self) -> None:
        cases = {
            "model": REQUIRED_MODEL,
            "prompts": REQUIRED_PROMPTS,
            "materials": REQUIRED_MATERIALS,
            "external_protocols": REQUIRED_EXTERNAL,
            "cross_model": REQUIRED_CROSSMODEL,
        }
        for block, expected in cases.items():
            with self.subTest(block=block):
                nested = set(self.lock["properties"][block]["required"])
                self.assertEqual(
                    nested,
                    expected,
                    msg=f"nested repro_lock.{block}.required drifted: "
                    f"only-in-schema={nested - expected}, only-in-constant={expected - nested}",
                )

    def test_check_repro_lock_imports_shared_constant(self) -> None:
        """check_repro_lock.py re-exports the shared constant (no duplicate copy).

        Pins that the standalone validator imports from repro_lock_validation
        rather than re-declaring REQUIRED_FIELDS — the drift guard is only sound
        if BOTH copies trace back to the single source.
        """
        import check_repro_lock

        self.assertIs(
            check_repro_lock.REQUIRED_FIELDS,
            REQUIRED_FIELDS,
            msg="check_repro_lock.REQUIRED_FIELDS is not the shared "
            "repro_lock_validation.REQUIRED_FIELDS object — a duplicate copy "
            "would defeat the drift guard.",
        )


def _valid_lock() -> dict:
    return {
        "schema_version": "1.0",
        "stochasticity_declaration": "Configuration, not a replay guarantee.",
        "ars_version": "3.24.1",
        "model": {"family": "claude", "id": "model-id", "weight_stable": False},
        "prompts": {
            "hash_timing": "skill-load",
            "skill_md_hash": "sha256:" + "a" * 64,
            "agents_bundle_hash": "sha256:" + "b" * 64,
        },
        "materials": {"list_hash": "sha256:" + "c" * 64, "count": 3},
        "external_protocols": {
            "s2_api_protocol_version": "3.3",
            "s2_snapshot_available": False,
        },
        "cross_model": {"enabled": False, "secondary_model_id": None},
    }


# Values tried in every required position. Strings and numbers near a rule's
# edge are included so a one-sided check shows up as a disagreement.
_PROBES = (None, "", " ", "x", "1.0", "skill-load", 0, -1, 1, 3, 3.0, 1.5, True, False, [], {}, [1], {"a": 1})


class ValidatorAgreementTest(unittest.TestCase):
    """validate_block and the nested schema answer the same way, value by value (#1050)."""

    def setUp(self) -> None:
        schema = dict(_nested_repro_lock())
        schema["type"] = "object"  # the passport-level null opt-out is the caller's case
        self.schema_validator = Draft202012Validator(schema)

    def _agree(self, lock: dict, label: str) -> None:
        by_schema = bool(list(self.schema_validator.iter_errors(lock)))
        by_block = bool(validate_block(lock))
        self.assertEqual(
            by_block,
            by_schema,
            msg=f"{label}: validate_block rejects={by_block}, schema rejects={by_schema}",
        )

    def test_valid_lock_passes_both(self) -> None:
        self.assertEqual(validate_block(_valid_lock()), [])
        self.assertEqual(list(self.schema_validator.iter_errors(_valid_lock())), [])

    def test_top_level_values_agree(self) -> None:
        for field in sorted(REQUIRED_FIELDS):
            for probe in _PROBES:
                with self.subTest(field=field, probe=probe):
                    lock = _valid_lock()
                    lock[field] = probe
                    self._agree(lock, f"{field}={probe!r}")

    def test_sub_block_values_agree(self) -> None:
        blocks = {
            "model": REQUIRED_MODEL,
            "prompts": REQUIRED_PROMPTS,
            "materials": REQUIRED_MATERIALS,
            "external_protocols": REQUIRED_EXTERNAL,
            "cross_model": REQUIRED_CROSSMODEL,
        }
        for block, fields in blocks.items():
            for field in sorted(fields):
                for probe in _PROBES:
                    with self.subTest(block=block, field=field, probe=probe):
                        lock = _valid_lock()
                        lock[block][field] = probe
                        self._agree(lock, f"{block}.{field}={probe!r}")

    def test_extra_key_is_the_known_difference(self) -> None:
        """Pins the one allowed difference, so widening it is a visible change."""
        lock = _valid_lock()
        lock["extra_note"] = "kept"
        self.assertEqual(validate_block(lock), [])
        self.assertTrue(list(self.schema_validator.iter_errors(lock)))


class SupportedValueDriftTest(unittest.TestCase):
    """The supported-value constants equal the schema's `const` values (#1050)."""

    def test_schema_version_const(self) -> None:
        const = _nested_repro_lock()["properties"]["schema_version"]["const"]
        self.assertEqual(SUPPORTED_SCHEMA_VERSIONS, {const})

    def test_hash_timing_const(self) -> None:
        props = _nested_repro_lock()["properties"]["prompts"]["properties"]
        self.assertEqual(SUPPORTED_HASH_TIMINGS, {props["hash_timing"]["const"]})


if __name__ == "__main__":
    unittest.main()
