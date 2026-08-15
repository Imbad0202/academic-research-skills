"""Regression tests for #738 USER_ATTESTED_READ resolution."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

try:
    from scripts.human_read_attestation_resolver import (
        resolve_user_attested_read,
    )
except ModuleNotFoundError:  # direct execution from scripts/
    from human_read_attestation_resolver import resolve_user_attested_read


SCRIPT = Path(__file__).resolve().parent / "human_read_attestation_resolver.py"


def _ledger(*rows: dict) -> dict:
    return {
        "session_id": "session-test",
        "created_at": "2026-08-14T23:59:00Z",
        "human_read": list(rows),
    }


def _mark(scope: dict | None, **extra: str) -> dict:
    row = {
        "citation_key": "ref1",
        "marked_at": "2026-08-15T00:00:00Z",
        **extra,
    }
    if scope is not None:
        row["attestation_type"] = "USER_ATTESTED_READ"
        row["read_scope"] = scope
    return row


class UserAttestedReadResolverTests(unittest.TestCase):
    def resolve(
        self, ledger: dict, kind: str = "page", value: str = "12"
    ) -> dict:
        return resolve_user_attested_read(
            ledger,
            citation_key="ref1",
            anchor_kind=kind,
            anchor_value=value,
        )

    def test_absent_mark_is_not_attested(self) -> None:
        out = self.resolve(_ledger())
        self.assertEqual(out["state"], "not_attested")
        self.assertFalse(out["ok_eligible"])
        self.assertEqual(
            out["finalizer_disposition"], "unacknowledged_low_warn"
        )

    def test_legacy_missing_scope_remains_coverage_unknown(self) -> None:
        out = self.resolve(_ledger(_mark(None)))
        self.assertEqual(out["state"], "coverage_unknown")
        self.assertFalse(out["ok_eligible"])
        self.assertEqual(out["finalizer_disposition"], "acknowledged_partial")

    def test_explicit_unknown_never_promotes(self) -> None:
        out = self.resolve(_ledger(_mark({"level": "unknown"})))
        self.assertEqual(out["state"], "coverage_unknown")
        self.assertFalse(out["ok_eligible"])

    def test_full_text_is_covered_for_resolved_anchor(self) -> None:
        out = self.resolve(_ledger(_mark({"level": "full_text"})))
        self.assertEqual(out["state"], "covered")
        self.assertTrue(out["ok_eligible"])
        self.assertEqual(out["finalizer_disposition"], "eligible_for_ok")

    def test_abstract_only_is_partial(self) -> None:
        out = self.resolve(_ledger(_mark({"level": "abstract_only"})))
        self.assertEqual(out["state"], "partial_coverage")
        self.assertFalse(out["ok_eligible"])

    def test_page_range_locator_is_deterministic(self) -> None:
        covered = self.resolve(
            _ledger(
                _mark({"level": "sections", "locators": ["pp. 10-24"]})
            )
        )
        missed = self.resolve(
            _ledger(
                _mark({"level": "sections", "locators": ["pp. 1-9"]})
            )
        )
        self.assertTrue(covered["ok_eligible"])
        self.assertEqual(missed["state"], "partial_coverage")

    def test_page_locator_rejects_bare_number_and_section_number(self) -> None:
        for locator in ("12", "section 12", "paragraph 12", "DOI 12"):
            with self.subTest(locator=locator):
                out = self.resolve(
                    _ledger(
                        _mark({"level": "sections", "locators": [locator]})
                    )
                )
                self.assertEqual(out["state"], "partial_coverage")
                self.assertFalse(out["ok_eligible"])

    def test_page_locator_accepts_only_explicit_page_grammar(self) -> None:
        for locator in ("page 12", "page:12", "p. 12", "pp. 10-24", "pages 10-24"):
            with self.subTest(locator=locator):
                out = self.resolve(
                    _ledger(
                        _mark({"level": "sections", "locators": [locator]})
                    )
                )
                self.assertTrue(out["ok_eligible"])

    def test_page_locator_rejects_reversed_range(self) -> None:
        out = self.resolve(
            _ledger(
                _mark({"level": "sections", "locators": ["pp. 24-10"]})
            )
        )
        self.assertEqual(out["state"], "partial_coverage")
        self.assertFalse(out["ok_eligible"])

    def test_section_locator_requires_exact_normalized_match(self) -> None:
        out = self.resolve(
            _ledger(
                _mark(
                    {"level": "sections", "locators": ["section:Methods"]}
                )
            ),
            "section",
            "methods",
        )
        self.assertTrue(out["ok_eligible"])

    def test_quote_anchor_requires_full_text(self) -> None:
        out = self.resolve(
            _ledger(
                _mark(
                    {"level": "sections", "locators": ["section:Methods"]}
                )
            ),
            "quote",
            "quoted words",
        )
        self.assertEqual(out["state"], "partial_coverage")

    def test_unresolved_anchor_never_promotes(self) -> None:
        out = self.resolve(
            _ledger(_mark({"level": "full_text"})), "none", ""
        )
        self.assertEqual(out["state"], "anchor_unresolved")
        self.assertFalse(out["ok_eligible"])
        self.assertEqual(out["finalizer_disposition"], "anchor_precedence")

    def test_out_of_enum_anchor_never_promotes(self) -> None:
        out = self.resolve(
            _ledger(_mark({"level": "full_text"})), "garbage", "12"
        )
        self.assertEqual(out["state"], "anchor_unresolved")
        self.assertEqual(out["finalizer_disposition"], "anchor_precedence")

    def test_latest_rescind_wins(self) -> None:
        row = _mark(
            {"level": "full_text"},
            rescinded_at="2026-08-15T00:01:00Z",
        )
        out = self.resolve(_ledger(row))
        self.assertEqual(out["state"], "rescinded")
        self.assertEqual(
            out["finalizer_disposition"], "unacknowledged_low_warn"
        )

    def test_newer_mark_after_rescind_wins_even_same_second(self) -> None:
        old = _mark(
            {"level": "full_text"},
            rescinded_at="2026-08-15T00:01:00Z",
        )
        new = _mark({"level": "full_text"})
        new["marked_at"] = "2026-08-15T00:01:00Z"
        out = self.resolve(_ledger(old, new))
        self.assertTrue(out["ok_eligible"])

    def test_invalid_timestamp_fails_visible(self) -> None:
        row = _mark({"level": "full_text"})
        row["marked_at"] = "not-a-time"
        out = self.resolve(_ledger(row))
        self.assertEqual(out["state"], "ledger_invalid")
        self.assertFalse(out["ok_eligible"])
        self.assertEqual(out["finalizer_disposition"], "block_invalid_ledger")

    def test_naive_timestamp_and_mixed_timestamp_forms_fail_closed(self) -> None:
        first = _mark({"level": "full_text"})
        second = _mark({"level": "full_text"})
        second["marked_at"] = "2026-08-15T01:00:00"
        out = self.resolve(_ledger(first, second))
        self.assertEqual(out["state"], "ledger_invalid")
        self.assertEqual(out["finalizer_disposition"], "block_invalid_ledger")

    def test_non_z_and_invalid_calendar_timestamps_fail_closed(self) -> None:
        for timestamp in (
            "2026-08-15T01:00:00+00:00",
            "2026-08-15T01:00:00.1234567Z",
            "2026-02-30T01:00:00Z",
        ):
            with self.subTest(timestamp=timestamp):
                row = _mark({"level": "full_text"})
                row["marked_at"] = timestamp
                out = self.resolve(_ledger(row))
                self.assertEqual(out["state"], "ledger_invalid")
                self.assertEqual(
                    out["finalizer_disposition"], "block_invalid_ledger"
                )

    def test_rescind_before_mark_fails_closed(self) -> None:
        row = _mark(
            {"level": "full_text"},
            rescinded_at="2026-08-14T23:59:59Z",
        )
        out = self.resolve(_ledger(row))
        self.assertEqual(out["state"], "ledger_invalid")

    def test_current_scope_requires_user_attestation_type(self) -> None:
        row = _mark({"level": "full_text"})
        row.pop("attestation_type")
        out = self.resolve(_ledger(row))
        self.assertEqual(out["state"], "ledger_invalid")

    def test_wrong_attestation_type_fails_closed(self) -> None:
        row = _mark({"level": "full_text"})
        row["attestation_type"] = "MODEL_INFERRED"
        out = self.resolve(_ledger(row))
        self.assertEqual(out["state"], "ledger_invalid")
        self.assertFalse(out["ok_eligible"])

    def test_extra_ledger_keys_fail_closed(self) -> None:
        row = _mark({"level": "full_text"})
        row["unexpected"] = True
        out = self.resolve(_ledger(row))
        self.assertEqual(out["state"], "ledger_invalid")
        self.assertFalse(out["ok_eligible"])

    def test_invalid_anchor_precedes_invalid_ledger(self) -> None:
        invalid_ledger = {"not": "a current ledger"}
        out = self.resolve(invalid_ledger, "none", "")
        self.assertEqual(out["state"], "anchor_unresolved")
        self.assertEqual(out["finalizer_disposition"], "anchor_precedence")

    def test_resolution_is_explicitly_transient(self) -> None:
        out = self.resolve(_ledger(_mark({"level": "full_text"})))
        self.assertEqual(
            out["schema_version"], "user-attested-read-resolution/1.0"
        )
        self.assertEqual(out["artifact_role"], "transient_routing_decision")
        self.assertNotIn("ledger_sha256", out)
        self.assertNotIn("anchor_sha256", out)

    def test_adversarial_state_to_finalizer_mapping_is_closed(self) -> None:
        cases = [
            (_ledger(_mark({"level": "full_text"})), "covered", "eligible_for_ok"),
            (
                _ledger(_mark({"level": "abstract_only"})),
                "partial_coverage",
                "acknowledged_partial",
            ),
            (
                _ledger(_mark({"level": "unknown"})),
                "coverage_unknown",
                "acknowledged_partial",
            ),
            (_ledger(), "not_attested", "unacknowledged_low_warn"),
            (
                _ledger(
                    _mark(
                        {"level": "full_text"},
                        rescinded_at="2026-08-15T00:01:00Z",
                    )
                ),
                "rescinded",
                "unacknowledged_low_warn",
            ),
        ]
        for ledger, state, disposition in cases:
            with self.subTest(state=state):
                out = self.resolve(ledger)
                self.assertEqual(out["state"], state)
                self.assertEqual(out["finalizer_disposition"], disposition)

    def test_finalizer_and_formatter_consume_closed_mapping(self) -> None:
        repo = Path(__file__).resolve().parent.parent
        orchestrator = (
            repo / "academic-pipeline/agents/pipeline_orchestrator_agent.md"
        ).read_text(encoding="utf-8")
        formatter = (
            repo / "academic-paper/agents/formatter_agent.md"
        ).read_text(encoding="utf-8")

        for token in (
            "`partial_coverage` or `coverage_unknown`",
            "`not_attested` or `rescinded`",
            "`block_invalid_ledger`",
            "<!--ref:slug READ-LEDGER-INVALID-->",
            "scripts/human_read_attestation_resolver.py",
        ):
            with self.subTest(surface="orchestrator", token=token):
                self.assertIn(token, orchestrator)
        for token in (
            "`not_attested` and `rescinded` remain plain unacknowledged `LOW-WARN`",
            "`READ-LEDGER-INVALID`",
            "MUST refuse",
        ):
            with self.subTest(surface="formatter", token=token):
                self.assertIn(token, formatter)

    def test_cli_duplicate_yaml_key_is_ledger_invalid(self) -> None:
        duplicate = """session_id: test\ncreated_at: 2026-08-14T23:59:00Z\nhuman_read:\n  - citation_key: ref1\n    marked_at: 2026-08-15T00:00:00Z\n    attestation_type: USER_ATTESTED_READ\n    read_scope: {level: full_text}\n    read_scope: {level: unknown}\n"""
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "read.yaml"
            path.write_text(duplicate, encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--read-log",
                    str(path),
                    "--citation-key",
                    "ref1",
                    "--anchor-kind",
                    "page",
                    "--anchor-value",
                    "12",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertEqual(out["state"], "ledger_invalid")
        self.assertEqual(out["finalizer_disposition"], "block_invalid_ledger")

    def test_cli_non_utf8_ledger_is_closed_json_not_traceback(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "read.yaml"
            path.write_bytes(b"session_id: \xff\n")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--read-log",
                    str(path),
                    "--citation-key",
                    "ref1",
                    "--anchor-kind",
                    "page",
                    "--anchor-value",
                    "12",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("Traceback (most recent call last)", proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["state"], "ledger_invalid")
        self.assertEqual(out["finalizer_disposition"], "block_invalid_ledger")

    def test_cli_anchor_precedence_does_not_open_invalid_yaml(self) -> None:
        duplicate = "session_id: first\nsession_id: second\n"
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "read.yaml"
            path.write_text(duplicate, encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--read-log",
                    str(path),
                    "--citation-key",
                    "ref1",
                    "--anchor-kind",
                    "none",
                    "--anchor-value",
                    "",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertEqual(out["state"], "anchor_unresolved")
        self.assertEqual(out["finalizer_disposition"], "anchor_precedence")

    def test_cli_missing_ledger_is_unacknowledged_not_attested(self) -> None:
        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist.yaml"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--read-log",
                    str(missing),
                    "--citation-key",
                    "ref1",
                    "--anchor-kind",
                    "page",
                    "--anchor-value",
                    "12",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertEqual(out["state"], "not_attested")
        self.assertEqual(
            out["finalizer_disposition"], "unacknowledged_low_warn"
        )

    @unittest.skipIf(jsonschema is None, "jsonschema not installed")
    def test_every_state_shape_validates_against_resolution_schema(self) -> None:
        schema_path = (
            Path(__file__).resolve().parent.parent
            / "shared/contracts/passport/user_attested_read_resolution.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        outputs = [
            self.resolve(_ledger()),
            self.resolve(_ledger(_mark(None))),
            self.resolve(_ledger(_mark({"level": "full_text"}))),
            self.resolve(_ledger(_mark({"level": "abstract_only"}))),
            self.resolve({"not": "a current ledger"}),
            self.resolve(_ledger(), "none", ""),
            self.resolve(
                _ledger(
                    _mark(
                        {"level": "full_text"},
                        rescinded_at="2026-08-15T00:01:00Z",
                    )
                )
            ),
        ]
        for output in outputs:
            jsonschema.validate(output, schema)

    @unittest.skipIf(jsonschema is None, "jsonschema not installed")
    def test_resolution_schema_rejects_forged_state_mapping(self) -> None:
        schema_path = (
            Path(__file__).resolve().parent.parent
            / "shared/contracts/passport/user_attested_read_resolution.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        valid = self.resolve(_ledger(_mark({"level": "full_text"})))
        forged = dict(valid)
        forged["finalizer_disposition"] = "acknowledged_partial"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(forged, schema)

        missing_binding = dict(valid)
        missing_binding.pop("governing_marked_at")
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(missing_binding, schema)


if __name__ == "__main__":
    unittest.main()
