"""Schema tests for Material Passport excluded_sources[] entries (#936)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = (
    REPO_ROOT / "shared" / "contracts" / "passport" / "excluded_source_entry.schema.json"
)
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)

EXCLUDED = {
    "citation_key": "lin2024governance",
    "gate": "2.5",
    "correction_id": "IL-SERIOUS-2",
    "recorded_at": "2026-10-02T09:00:00Z",
}


def _errors(entry: dict) -> list[str]:
    return [e.message for e in VALIDATOR.iter_errors(entry)]


def test_schema_is_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(SCHEMA)


def test_valid_entry_passes() -> None:
    assert _errors(EXCLUDED) == []


def test_restored_entry_passes() -> None:
    entry = dict(
        EXCLUDED,
        gate="4.5",
        restored_at="2026-10-02T11:00:00Z",
        restoration_words="這篇是真的，DOI 在附檔裡",
    )
    assert _errors(entry) == []


def test_confirmed_cross_model_entry_without_report_row_passes() -> None:
    entry = copy.deepcopy(EXCLUDED)
    entry.pop("correction_id")
    assert _errors(entry) == []


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda e: e.update(gate="3"), id="not-an-integrity-gate"),
        pytest.param(lambda e: e.update(citation_key="  "), id="blank-citation-key"),
        pytest.param(lambda e: e.update(citation_key=" lin2024governance "), id="padded-citation-key"),
        pytest.param(
            lambda e: e.update(citation_key="<!--ref:lin2024governance-->"), id="marker-not-key"
        ),
        pytest.param(lambda e: e.update(recorded_at="not-a-date"), id="bad-recorded-at"),
        pytest.param(
            lambda e: e.update(restored_at="", restoration_words="it exists"), id="bad-restored-at"
        ),
        pytest.param(lambda e: e.update(correction_id="EA-001"), id="alignment-row-id"),
        pytest.param(lambda e: e.pop("recorded_at"), id="unrecorded"),
        pytest.param(
            lambda e: e.update(restored_at="2026-10-02T11:00:00Z"),
            id="restoration-without-words",
        ),
        pytest.param(lambda e: e.update(restoration_words="it exists"), id="words-without-restoration"),
        pytest.param(lambda e: e.update(note="extra"), id="unknown-field"),
    ],
)
def test_invalid_entries_fail(mutate) -> None:
    entry = copy.deepcopy(EXCLUDED)
    mutate(entry)
    assert _errors(entry), f"expected a schema error for {entry}"
