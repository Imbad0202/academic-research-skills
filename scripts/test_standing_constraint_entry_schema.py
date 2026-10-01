"""Schema tests for Material Passport standing_constraints[] entries (#927)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = (
    REPO_ROOT / "shared" / "contracts" / "passport" / "standing_constraint_entry.schema.json"
)
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)

CEILING = {
    "constraint_id": "UC-001",
    "user_words": "body under 6,000 words",
    "kind": "word_ceiling",
    "max_words": 6000,
    "applies_to_stages": ["2", "4", "4'", "5"],
    "confirmed_at": "2026-10-02T09:00:00Z",
}
SCOPE = {
    "constraint_id": "UC-004",
    "user_words": "只看台灣的大學",
    "kind": "scope",
    "applies_to_stages": ["2", "2.5", "4", "4'", "4.5"],
    "stated_at_stage": "1",
    "confirmed_at": "2026-10-02T09:20:00Z",
}


def _errors(entry: dict) -> list[str]:
    return [e.message for e in VALIDATOR.iter_errors(entry)]


def test_schema_is_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("entry", [CEILING, SCOPE])
def test_valid_entries_pass(entry: dict) -> None:
    assert _errors(entry) == []


def test_withdrawn_entry_passes() -> None:
    entry = dict(
        SCOPE,
        withdrawn_at="2026-10-02T11:00:00Z",
        withdrawal_words="範圍改回全部亞洲",
    )
    assert _errors(entry) == []


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda e: e.pop("max_words"), id="ceiling-without-max-words"),
        pytest.param(lambda e: e.update(kind="prohibition"), id="max-words-on-non-ceiling"),
        pytest.param(lambda e: e.update(stated_at_stage=""), id="empty-stated-at-stage"),
        pytest.param(lambda e: e.update(user_words="   "), id="blank-user-words"),
        pytest.param(lambda e: e.update(applies_to_stages=[]), id="no-stages"),
        pytest.param(lambda e: e.update(applies_to_stages=["7"]), id="unknown-stage"),
        pytest.param(lambda e: e.update(constraint_id="SC-001"), id="bad-id"),
        pytest.param(lambda e: e.update(kind="preference"), id="unknown-kind"),
        pytest.param(lambda e: e.pop("confirmed_at"), id="unconfirmed"),
        pytest.param(
            lambda e: e.update(withdrawn_at="2026-10-02T11:00:00Z"),
            id="withdrawal-without-words",
        ),
        pytest.param(lambda e: e.update(withdrawal_words="never mind"), id="words-without-withdrawal"),
        pytest.param(lambda e: e.update(note="extra"), id="unknown-field"),
    ],
)
def test_invalid_entries_fail(mutate) -> None:
    entry = copy.deepcopy(CEILING)
    mutate(entry)
    assert _errors(entry), f"expected a schema error for {entry}"
