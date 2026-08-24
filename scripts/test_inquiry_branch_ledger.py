#!/usr/bin/env python3
"""Hermetic contract/replay/storage tests for inquiry-branch-ledger/1.0 (#743)."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.inquiry_branch_ledger import (
    ENV_FLAG,
    ContractError,
    LedgerBindingError,
    TransactionRecoveryError,
    append_event,
    canonical_bytes,
    checkpoint_summary,
    commit_ledger_transaction,
    default_ledger_relative_path,
    inquiry_ledger_enabled,
    load_bound_ledger,
    load_ledger,
    new_ledger,
    recover_ledger_transaction,
    render_summary,
    replay_ledger,
    validate_ledger_shape,
    validate_pointer,
)
from scripts.research_workflow_profile import (
    DEFAULT_FIELD_GENERAL_PROFILE,
    load_profile,
    seal_profile,
)

try:
    import fcntl
except ImportError:  # pragma: no cover - POSIX-only alpha coverage
    fcntl = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_SCHEMA = (
    REPO_ROOT
    / "shared"
    / "contracts"
    / "research_workflow"
    / "inquiry_branch_ledger.schema.json"
)
POINTER_SCHEMA = (
    REPO_ROOT / "shared" / "contracts" / "passport" / "inquiry_ledger_ref.schema.json"
)
RUNTIME = REPO_ROOT / "scripts" / "inquiry_branch_ledger.py"


def _profile(*, profile_id: str = "field_general", branch_budget: int = 3) -> dict:
    profile = copy.deepcopy(load_profile(DEFAULT_FIELD_GENERAL_PROFILE))
    if profile_id != "field_general" or branch_budget != 3:
        profile.update(
            {
                "profile_id": profile_id,
                "branch_budget": branch_budget,
                "provenance": {
                    "source": "user_modified",
                    "source_pointer": f"synthetic test profile: {profile_id}",
                    "last_reviewed_at": "2026-08-24",
                    "freshness_state": "unverified",
                },
            }
        )
        profile = seal_profile(profile)
    return profile


def _event(
    kind: str,
    branch_id: str | None,
    payload: dict,
    *,
    actor: str = "author",
    minute: int = 0,
) -> dict:
    return {
        "recorded_at": f"2026-08-24T10:{minute:02d}:00+08:00",
        "actor": actor,
        "kind": kind,
        "branch_id": branch_id,
        "payload": payload,
    }


def _created_payload(
    statement: str,
    *,
    parent_id: str | None = None,
    refs: list[str] | None = None,
    conditions: list[dict] | None = None,
) -> dict:
    return {
        "parent_id": parent_id,
        "statement": statement,
        "assumptions": [],
        "evidence_sought": [],
        "reopen_conditions": [] if conditions is None else conditions,
        "downstream_refs": [] if refs is None else refs,
    }


def _two_branch_ledger(profile: dict | None = None) -> tuple[dict, dict]:
    profile = profile or _profile()
    ledger = new_ledger("project-alpha", profile)
    ledger = append_event(
        ledger,
        _event(
            "branch_created",
            "main",
            _created_payload(
                "Primary framing",
                refs=["draft-v1", "shared-table"],
                conditions=[
                    {
                        "condition_id": "invariance-fails",
                        "statement": "Reopen if measurement invariance fails",
                    }
                ],
            ),
        ),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "facet_surfaced",
            "facet",
            {"parent_id": "main", "surfaced_text": "Alternative mechanism"},
            actor="ai",
            minute=1,
        ),
        [profile],
    )
    return ledger, profile


def _adopt_facet(ledger: dict, profiles) -> dict:
    return append_event(
        ledger,
        _event(
            "branch_adopted",
            "facet",
            {
                "source_event_id": 2,
                "surfaced_text": "Alternative mechanism",
                "author_formulation": "Author-owned alternative mechanism",
            },
            minute=2,
        ),
        profiles,
    )


def _write_canonical(path: Path, value: dict) -> Path:
    path.write_bytes(canonical_bytes(value))
    return path


def _passport(path: Path) -> Path:
    path.write_text(
        "# keep this comment\n"
        "origin_skill: academic-paper\n"
        "origin_mode: full\n"
        "verification_status: UNVERIFIED\n"
        "version_label: v1\n",
        encoding="utf-8",
    )
    return path


def _append_raw_event(ledger: dict, event_input: dict) -> dict:
    """Test-only chain completion for malformed semantic histories."""

    updated = copy.deepcopy(ledger)
    events = updated["events"]
    events.append(
        {
            "event_id": len(events) + 1,
            **event_input,
            "prev_event_sha256": (
                "0" * 64
                if not events
                else hashlib.sha256(canonical_bytes(events[-1])).hexdigest()
            ),
        }
    )
    return updated


def _leave_update_journal(tmp_path: Path) -> tuple[Path, Path, Path, dict, dict]:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    ledger_path = tmp_path / "passport.inquiry-branch-ledger.json"
    commit_ledger_transaction(
        passport, ledger_path, tmp_path, ledger, [profile], "project-alpha"
    )
    updated = _adopt_facet(ledger, [profile])

    def crash(phase: str) -> None:
        if phase == "journal_durable":
            raise RuntimeError("leave journal")

    with pytest.raises(RuntimeError, match="leave journal"):
        commit_ledger_transaction(
            passport,
            ledger_path,
            tmp_path,
            updated,
            [profile],
            "project-alpha",
            crash_hook=crash,
        )
    journal = tmp_path / ".passport.yaml.inquiry-ledger.transaction.json"
    assert journal.is_file()
    return passport, ledger_path, journal, updated, profile


# ---------------------------------------------------------------------------
# JSON Schemas + closed shape
# ---------------------------------------------------------------------------


def test_schemas_compile_and_accept_runtime_artifacts() -> None:
    ledger, profile = _two_branch_ledger()
    ledger_schema = json.loads(LEDGER_SCHEMA.read_text(encoding="utf-8"))
    pointer_schema = json.loads(POINTER_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(ledger_schema)
    Draft202012Validator.check_schema(pointer_schema)
    ledger_validator = Draft202012Validator(
        ledger_schema, format_checker=FormatChecker()
    )
    pointer_validator = Draft202012Validator(pointer_schema)
    assert list(ledger_validator.iter_errors(ledger)) == []
    pointer = {
        "ledger_path": "project.inquiry-branch-ledger.json",
        "ledger_version": "inquiry-branch-ledger/1.0",
        "content_sha256": hashlib.sha256(canonical_bytes(ledger)).hexdigest(),
    }
    assert list(pointer_validator.iter_errors(pointer)) == []
    replay_ledger(ledger, [profile], require_materialized=True)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda ledger: ledger.update({"projection": {}}),
        lambda ledger: ledger["events"][0].update({"unknown": True}),
        lambda ledger: ledger["events"][0]["payload"].update({"patch": []}),
        lambda ledger: ledger["events"][0].update({"actor": "ai"}),
        lambda ledger: ledger["events"][0].update({"branch_id": None}),
    ],
)
def test_schema_and_runtime_reject_closed_shape_mutations(mutation) -> None:
    ledger, profile = _two_branch_ledger()
    mutation(ledger)
    schema = json.loads(LEDGER_SCHEMA.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(ledger))
    with pytest.raises(ContractError):
        replay_ledger(ledger, [profile])


def test_pointer_schema_and_runtime_reject_escape_and_unknown_fields() -> None:
    schema = json.loads(POINTER_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    base = {
        "ledger_path": "../escape.json",
        "ledger_version": "inquiry-branch-ledger/1.0",
        "content_sha256": "a" * 64,
        "extra": True,
    }
    assert list(validator.iter_errors(base))
    with pytest.raises(ContractError):
        validate_pointer(base)
    del base["extra"]
    with pytest.raises(ContractError, match=r"workspace-relative|\.\."):
        validate_pointer(base)


@pytest.mark.parametrize(
    "ledger_path",
    [
        r"nested\\ledger.json",
        "./ledger.json",
        "nested/../ledger.json",
        "nested//ledger.json",
        "nested/",
        "nested/ledger\u0007.json",
        "nested/ledger\u202e.json",
    ],
)
def test_pointer_schema_and_runtime_share_normalized_path_grammar(
    ledger_path: str,
) -> None:
    schema = json.loads(POINTER_SCHEMA.read_text(encoding="utf-8"))
    pointer = {
        "ledger_path": ledger_path,
        "ledger_version": "inquiry-branch-ledger/1.0",
        "content_sha256": "a" * 64,
    }
    assert list(Draft202012Validator(schema).iter_errors(pointer))
    with pytest.raises(ContractError):
        validate_pointer(pointer)


def test_schema_and_runtime_share_frozen_free_text_and_optional_reopen_shape() -> None:
    profile = _profile()
    ledger = new_ledger("project-alpha", profile)
    ledger = append_event(
        ledger,
        _event(
            "branch_created",
            "main",
            {
                "parent_id": None,
                "statement": "Main",
                "assumptions": ["same", "same"],
                "evidence_sought": ["same", "same"],
                "reopen_conditions": [
                    {
                        "condition_id": "measurement condition 1",
                        "statement": "Reopen on failed invariance",
                    }
                ],
                "downstream_refs": [],
            },
        ),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "facet_surfaced",
            "facet",
            {"parent_id": "main", "surfaced_text": "Facet"},
            actor="ai",
            minute=1,
        ),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "wait"}, minute=2),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "branch_reopened",
            "main",
            {"reason": "condition met", "condition_id": "measurement condition 1"},
            minute=3,
        ),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "wait again"}, minute=4),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "branch_reopened",
            "main",
            {"reason": "other evidence", "evidence_pointer": "results#secondary"},
            minute=5,
        ),
        [profile],
    )
    schema = json.loads(LEDGER_SCHEMA.read_text(encoding="utf-8"))
    assert list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            ledger
        )
    ) == []
    replay_ledger(ledger, [profile], require_materialized=True)


def test_schema_and_runtime_reject_leading_zero_semver_identifier() -> None:
    ledger, profile = _two_branch_ledger()
    ledger["initial_profile_binding"]["profile_version"] = "1.0.0-01"
    schema = json.loads(LEDGER_SCHEMA.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(ledger))
    with pytest.raises(ContractError, match="SemVer"):
        replay_ledger(ledger, [profile])


def test_duplicate_json_keys_and_noncanonical_storage_fail(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(
        '{"schema_version":"inquiry-branch-ledger/1.0",'
        '"schema_version":"inquiry-branch-ledger/1.0"}',
        encoding="utf-8",
    )
    with pytest.raises(ContractError, match="duplicate JSON key"):
        load_ledger(duplicate)

    ledger, _ = _two_branch_ledger()
    pretty = tmp_path / "pretty.json"
    pretty.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    with pytest.raises(ContractError, match="exact JSON Canonical Form"):
        load_ledger(pretty)


def test_schema_and_runtime_share_frozen_non_slug_condition_and_list_domain() -> None:
    """Only branch ids are frozen as slugs; ordinary text lists are lists."""

    profile = _profile()
    ledger = new_ledger("project-alpha", profile)
    ledger = append_event(
        ledger,
        _event(
            "branch_created",
            "main",
            {
                **_created_payload(
                    "Main",
                    conditions=[
                        {
                            "condition_id": "Condition 1 / confirmatory",
                            "statement": "Reopen on contrary evidence",
                        }
                    ],
                ),
                "assumptions": ["same text", "same text"],
                "evidence_sought": ["same source", "same source"],
            },
        ),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "facet_surfaced",
            "facet",
            {"parent_id": "main", "surfaced_text": "Facet"},
            actor="ai",
            minute=1,
        ),
        [profile],
    )
    replay_ledger(ledger, [profile], require_materialized=True)
    schema = json.loads(LEDGER_SCHEMA.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(ledger)) == []


@pytest.mark.parametrize(
    "reopen_payload",
    [
        {"reason": "stored condition", "condition_id": "invariance-fails"},
        {"reason": "uncatalogued evidence", "evidence_pointer": "results#row-2"},
    ],
)
def test_schema_and_runtime_allow_each_optional_reopen_field_independently(
    reopen_payload: dict,
) -> None:
    ledger, profile = _two_branch_ledger()
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "wait"}, minute=2),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event("branch_reopened", "main", reopen_payload, minute=3),
        [profile],
    )
    replay_ledger(ledger, [profile])
    schema = json.loads(LEDGER_SCHEMA.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(ledger)) == []


def test_schema_and_runtime_share_strict_semver_domain() -> None:
    ledger, _ = _two_branch_ledger()
    ledger["initial_profile_binding"]["profile_version"] = "1.0.0-01"
    with pytest.raises(ContractError, match="SemVer"):
        validate_ledger_shape(ledger)
    schema = json.loads(LEDGER_SCHEMA.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(ledger))


@pytest.mark.parametrize(
    "unsafe_path",
    ["folder\\ledger.json", "folder/./ledger.json", "folder//ledger.json", "folder/"],
)
def test_pointer_schema_and_runtime_share_normalized_posix_path_domain(
    unsafe_path: str,
) -> None:
    pointer = {
        "ledger_path": unsafe_path,
        "ledger_version": "inquiry-branch-ledger/1.0",
        "content_sha256": "a" * 64,
    }
    with pytest.raises(ContractError, match="normalized"):
        validate_pointer(pointer)
    schema = json.loads(POINTER_SCHEMA.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(pointer))


# ---------------------------------------------------------------------------
# State machine, provenance, conditions, and budget
# ---------------------------------------------------------------------------


def test_full_lawful_transition_history_replays_deterministically() -> None:
    ledger, profile = _two_branch_ledger()
    ledger = _adopt_facet(ledger, [profile])
    for minute, field, value in (
        (3, "assumptions", ["measurement is comparable"]),
        (4, "evidence_sought", ["invariance test"]),
        (
            5,
            "reopen_conditions",
            [
                {
                    "condition_id": "invariance-fails",
                    "statement": "Reopen if measurement invariance fails",
                    "evidence_pointer": "analysis-plan#invariance",
                }
            ],
        ),
        (6, "downstream_refs", ["draft-v1", "table-v1"]),
    ):
        ledger = append_event(
            ledger,
            _event(
                "branch_annotated",
                "main",
                {"field": field, "value": value},
                minute=minute,
            ),
            [profile],
        )
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "await evidence"}, minute=7),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "reopen_condition_signal",
            "main",
            {
                "branch_id_ref": "main",
                "condition_id": "invariance-fails",
                "evidence_pointer": "results#table-2",
            },
            actor="ai",
            minute=8,
        ),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "branch_reopened",
            "main",
            {
                "reason": "author judges condition satisfied",
                "condition_id": "invariance-fails",
                "evidence_pointer": "results#table-2",
            },
            minute=9,
        ),
        [profile],
    )
    first = replay_ledger(ledger, [profile], require_materialized=True)
    second = replay_ledger(
        json.loads(canonical_bytes(ledger)), [profile], require_materialized=True
    )
    assert first == second
    main = first["branches"][0]
    assert main["status"] == "reopened"
    assert main["assumptions"] == ["measurement is comparable"]
    assert main["evidence_sought"] == ["invariance test"]
    assert [row["artifact_ref"] for row in first["artifacts"]] == [
        "draft-v1",
        "table-v1",
    ]
    assert all(row["stale"] for row in first["artifacts"])
    assert first["reopen_condition_signals"][0]["condition_statement"].startswith(
        "Reopen if"
    )


def test_ai_facet_requires_origin_bound_substantive_adoption() -> None:
    ledger, profile = _two_branch_ledger()
    mutations = [
        {
            "source_event_id": 1,
            "surfaced_text": "Alternative mechanism",
            "author_formulation": "Author alternative",
        },
        {
            "source_event_id": 2,
            "surfaced_text": "changed",
            "author_formulation": "Author alternative",
        },
        {
            "source_event_id": 2,
            "surfaced_text": "Alternative mechanism",
            "author_formulation": "Alternative mechanism",
        },
        {
            "source_event_id": 2,
            "surfaced_text": "Alternative mechanism",
            "author_formulation": " OK ",
        },
    ]
    for payload in mutations:
        with pytest.raises(ContractError):
            append_event(
                ledger,
                _event("branch_adopted", "facet", payload, minute=2),
                [profile],
            )

    adopted = _adopt_facet(ledger, [profile])
    branch = replay_ledger(adopted, [profile])["branches"][1]
    assert branch["provenance"] == "author_adopted"
    assert branch["adoption_receipt"]["source_event_id"] == 2
    assert branch["surfaced_text"] == "Alternative mechanism"
    assert branch["statement"] == "Author-owned alternative mechanism"


def test_unadopted_facet_reopen_and_post_rejection_events_fail() -> None:
    ledger, profile = _two_branch_ledger()
    with pytest.raises(ContractError, match="unadopted"):
        append_event(
            ledger,
            _event("branch_reopened", "facet", {"reason": "try"}, minute=2),
            [profile],
        )
    rejected = append_event(
        ledger,
        _event("branch_rejected", "facet", {"reason": "not adopted"}, minute=2),
        [profile],
    )
    for kind, payload in (
        ("branch_archived", {"reason": "archive"}),
        (
            "branch_adopted",
            {
                "source_event_id": 2,
                "surfaced_text": "Alternative mechanism",
                "author_formulation": "Changed mind",
            },
        ),
    ):
        with pytest.raises(ContractError, match="terminal|parked"):
            append_event(rejected, _event(kind, "facet", payload, minute=3), [profile])


def test_condition_identity_is_immutable_and_removed_ids_are_retired() -> None:
    ledger, profile = _two_branch_ledger()
    changed = _event(
        "branch_annotated",
        "main",
        {
            "field": "reopen_conditions",
            "value": [
                {
                    "condition_id": "invariance-fails",
                    "statement": "Different condition text",
                }
            ],
        },
        minute=2,
    )
    with pytest.raises(ContractError, match="cannot be rebound"):
        append_event(ledger, changed, [profile])

    removed = append_event(
        ledger,
        _event(
            "branch_annotated",
            "main",
            {"field": "reopen_conditions", "value": []},
            minute=2,
        ),
        [profile],
    )
    with pytest.raises(ContractError, match="retired"):
        append_event(
            removed,
            _event(
                "branch_annotated",
                "main",
                {
                    "field": "reopen_conditions",
                    "value": [
                        {
                            "condition_id": "invariance-fails",
                            "statement": "Reopen if measurement invariance fails",
                        }
                    ],
                },
                minute=3,
            ),
            [profile],
        )
    with pytest.raises(ContractError, match="currently stored"):
        append_event(
            removed,
            _event(
                "reopen_condition_signal",
                "main",
                {
                    "branch_id_ref": "main",
                    "condition_id": "invariance-fails",
                    "evidence_pointer": "row",
                },
                actor="ai",
                minute=3,
            ),
            [profile],
        )


def test_unknown_parent_duplicate_branch_and_terminal_mutation_fail() -> None:
    profile = _profile()
    ledger = new_ledger("project-alpha", profile)
    with pytest.raises(ContractError, match="earlier event"):
        append_event(
            ledger,
            _event(
                "branch_created",
                "child",
                _created_payload("Child", parent_id="missing"),
            ),
            [profile],
        )
    ledger, _ = _two_branch_ledger(profile)
    with pytest.raises(ContractError, match="cannot be reused"):
        append_event(
            ledger,
            _event("branch_created", "main", _created_payload("Again"), minute=2),
            [profile],
        )
    archived = append_event(
        ledger,
        _event("branch_archived", "main", {"reason": "closed"}, minute=2),
        [profile],
    )
    with pytest.raises(ContractError, match="terminal"):
        append_event(
            archived,
            _event(
                "branch_annotated",
                "main",
                {"field": "assumptions", "value": ["late"]},
                minute=3,
            ),
            [profile],
        )


def test_budget_allows_parked_facet_but_blocks_adoption_and_creation() -> None:
    profile = _profile(profile_id="budget-one", branch_budget=1)
    ledger, _ = _two_branch_ledger(profile)
    assert replay_ledger(ledger, [profile])["live_count"] == 1
    with pytest.raises(ContractError, match="branch_budget"):
        _adopt_facet(ledger, [profile])
    with pytest.raises(ContractError, match="branch_budget"):
        append_event(
            ledger,
            _event("branch_created", "second", _created_payload("Second"), minute=2),
            [profile],
        )
    parked = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "make room"}, minute=2),
        [profile],
    )
    adopted = _adopt_facet(parked, [profile])
    assert replay_ledger(adopted, [profile])["live_count"] == 1


def test_profile_rebound_requires_exact_catalog_and_prior_disposition() -> None:
    ledger, wide = _two_branch_ledger()
    ledger = _adopt_facet(ledger, [wide])
    narrow = _profile(profile_id="narrow", branch_budget=1)
    payload = {
        "profile_id": narrow["profile_id"],
        "profile_version": narrow["profile_version"],
        "content_sha256": narrow["content_sha256"],
        "selection_receipt_ref": "receipts/profile-selection.json",
    }
    with pytest.raises(ContractError, match="unresolved"):
        append_event(
            ledger,
            _event("profile_rebound", None, payload, minute=3),
            [wide],
        )
    with pytest.raises(ContractError, match="dispose live branches"):
        append_event(
            ledger,
            _event("profile_rebound", None, payload, minute=3),
            [wide, narrow],
        )
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "lower budget"}, minute=3),
        [wide],
    )
    rebound = append_event(
        ledger,
        _event("profile_rebound", None, payload, minute=4),
        [wide, narrow],
    )
    projection = replay_ledger(rebound, [wide, narrow])
    assert projection["effective_profile_binding"] == {
        key: narrow[key] for key in ("profile_id", "profile_version", "content_sha256")
    }
    assert projection["branch_budget"] == 1


def test_event_order_is_ids_not_timestamp_monotonicity() -> None:
    ledger, profile = _two_branch_ledger()
    ledger["events"][1]["recorded_at"] = "2026-08-23T00:00:00Z"
    # recorded_at is deliberately not part of the ordering rule. Event 2's
    # own change does not affect its prev hash, and there is no event 3.
    assert replay_ledger(ledger, [profile])["event_count"] == 2


# ---------------------------------------------------------------------------
# Hash chain, invalidation causes, merge, and supersession
# ---------------------------------------------------------------------------


def test_dense_ids_and_previous_event_hash_are_fail_closed() -> None:
    ledger, profile = _two_branch_ledger()
    bad_id = copy.deepcopy(ledger)
    bad_id["events"][1]["event_id"] = 3
    with pytest.raises(ContractError, match="dense event id 2"):
        replay_ledger(bad_id, [profile])
    changed_interior = copy.deepcopy(ledger)
    changed_interior["events"][0]["payload"]["statement"] = "rewritten"
    with pytest.raises(ContractError, match="previous event"):
        replay_ledger(changed_interior, [profile])


def test_truncation_needs_materialization_or_passport_head_to_detect() -> None:
    ledger, profile = _two_branch_ledger()
    truncated = copy.deepcopy(ledger)
    truncated["events"] = truncated["events"][:1]
    # Chain alone has no later edge and therefore accepts a well-formed prefix.
    assert replay_ledger(truncated, [profile])["event_count"] == 1
    with pytest.raises(ContractError, match="at least two"):
        replay_ledger(truncated, [profile], require_materialized=True)


def test_reopen_auto_emits_contiguous_ordered_stale_events() -> None:
    ledger, profile = _two_branch_ledger()
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "wait"}, minute=2),
        [profile],
    )
    reopened = append_event(
        ledger,
        _event("branch_reopened", "main", {"reason": "new evidence"}, minute=3),
        [profile],
    )
    assert [event["kind"] for event in reopened["events"][-3:]] == [
        "branch_reopened",
        "artifact_marked_stale",
        "artifact_marked_stale",
    ]
    assert [event["payload"]["artifact_ref"] for event in reopened["events"][-2:]] == [
        "draft-v1",
        "shared-table",
    ]
    assert all(event["actor"] == "system" for event in reopened["events"][-2:])

    missing = copy.deepcopy(reopened)
    missing["events"].pop()
    with pytest.raises(ContractError, match="ends before"):
        replay_ledger(missing, [profile])

    reordered = copy.deepcopy(reopened)
    first, second = reordered["events"][-2:]
    reordered["events"][-2:] = [second, first]
    # Repair chain links so the failure specifically exercises stale ordering.
    for index in range(len(reordered["events"])):
        reordered["events"][index]["event_id"] = index + 1
        reordered["events"][index]["prev_event_sha256"] = (
            "0" * 64
            if index == 0
            else hashlib.sha256(canonical_bytes(reordered["events"][index - 1])).hexdigest()
        )
    with pytest.raises(ContractError, match="downstream_refs order"):
        replay_ledger(reordered, [profile])


def test_direct_or_orphan_stale_event_is_refused() -> None:
    ledger, profile = _two_branch_ledger()
    raw = _event(
        "artifact_marked_stale",
        None,
        {"artifact_ref": "draft-v1", "reopening_event_id": 1},
        actor="system",
        minute=2,
    )
    with pytest.raises(ContractError, match="mechanically"):
        append_event(ledger, raw, [profile])
    malformed = _append_raw_event(ledger, raw)
    with pytest.raises(ContractError, match="orphan"):
        replay_ledger(malformed, [profile])


def test_two_stale_causes_clear_independently() -> None:
    profile = _profile()
    ledger = new_ledger("project-alpha", profile)
    for minute, branch_id in enumerate(("a", "b")):
        ledger = append_event(
            ledger,
            _event(
                "branch_created",
                branch_id,
                _created_payload(branch_id.upper(), refs=["shared"]),
                minute=minute,
            ),
            [profile],
        )
    for minute, branch_id in ((2, "a"), (4, "b")):
        ledger = append_event(
            ledger,
            _event("branch_parked", branch_id, {"reason": "wait"}, minute=minute),
            [profile],
        )
        ledger = append_event(
            ledger,
            _event(
                "branch_reopened", branch_id, {"reason": "evidence"}, minute=minute + 1
            ),
            [profile],
        )
    projection = replay_ledger(ledger, [profile])
    causes = projection["artifacts"][0]["outstanding_stale_causes"]
    assert len(causes) == 2
    ledger = append_event(
        ledger,
        _event(
            "artifact_reconfirmed",
            None,
            {
                "artifact_ref": "shared",
                "resolves_stale_event_id": causes[0],
                "note": "valid for branch a",
            },
            minute=6,
        ),
        [profile],
    )
    artifact = replay_ledger(ledger, [profile])["artifacts"][0]
    assert artifact["stale"] is True
    assert artifact["outstanding_stale_causes"] == [causes[1]]
    ledger = append_event(
        ledger,
        _event(
            "artifact_reconfirmed",
            None,
            {
                "artifact_ref": "shared",
                "resolves_stale_event_id": causes[1],
                "note": "valid for branch b",
            },
            minute=7,
        ),
        [profile],
    )
    artifact = replay_ledger(ledger, [profile])["artifacts"][0]
    assert artifact["stale"] is False
    assert len(artifact["resolution_history"]) == 2
    with pytest.raises(ContractError, match="already been resolved"):
        append_event(
            ledger,
            _event(
                "artifact_reconfirmed",
                None,
                {
                    "artifact_ref": "shared",
                    "resolves_stale_event_id": causes[0],
                    "note": "duplicate",
                },
                minute=8,
            ),
            [profile],
        )


def test_merge_order_and_supersession_update_every_branch() -> None:
    profile = _profile()
    ledger = new_ledger("project-alpha", profile)
    ledger = append_event(
        ledger,
        _event(
            "branch_created",
            "target",
            _created_payload("Target", refs=["a", "shared"]),
        ),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "branch_created",
            "source",
            _created_payload("Source", refs=["shared", "b"]),
            minute=1,
        ),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "branch_merged",
            "source",
            {"merged_into": "target", "reason": "combine"},
            minute=2,
        ),
        [profile],
    )
    projection = replay_ledger(ledger, [profile])
    assert projection["branches"][0]["downstream_refs"] == ["a", "shared", "b"]
    assert projection["branches"][1]["status"] == "merged"

    ledger = append_event(
        ledger,
        _event("branch_parked", "target", {"reason": "wait"}, minute=3),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event("branch_reopened", "target", {"reason": "new"}, minute=4),
        [profile],
    )
    projection = replay_ledger(ledger, [profile])
    cause = next(
        row["outstanding_stale_causes"][0]
        for row in projection["artifacts"]
        if row["artifact_ref"] == "shared"
    )
    ledger = append_event(
        ledger,
        _event(
            "artifact_superseded",
            None,
            {
                "artifact_ref": "shared",
                "resolves_stale_event_id": cause,
                "note": "replaced",
                "replaced_by": "shared-v2",
            },
            minute=5,
        ),
        [profile],
    )
    branches = replay_ledger(ledger, [profile])["branches"]
    assert branches[0]["downstream_refs"] == ["a", "shared-v2", "b"]
    assert branches[1]["downstream_refs"] == ["shared-v2", "b"]


def test_merge_requires_distinct_live_target() -> None:
    ledger, profile = _two_branch_ledger()
    ledger = _adopt_facet(ledger, [profile])
    with pytest.raises(ContractError, match="itself"):
        append_event(
            ledger,
            _event(
                "branch_merged",
                "main",
                {"merged_into": "main", "reason": "self"},
                minute=3,
            ),
            [profile],
        )
    parked = append_event(
        ledger,
        _event("branch_parked", "facet", {"reason": "not live"}, minute=3),
        [profile],
    )
    with pytest.raises(ContractError, match="currently-live"):
        append_event(
            parked,
            _event(
                "branch_merged",
                "main",
                {"merged_into": "facet", "reason": "bad target"},
                minute=4,
            ),
            [profile],
        )


# ---------------------------------------------------------------------------
# Pointer authority, default-off behavior, and transaction recovery
# ---------------------------------------------------------------------------


def test_default_flag_and_simple_path_are_silent() -> None:
    assert inquiry_ledger_enabled({}) is False
    assert inquiry_ledger_enabled({ENV_FLAG: "0"}) is False
    assert inquiry_ledger_enabled({ENV_FLAG: "true"}) is False
    assert inquiry_ledger_enabled({ENV_FLAG: "1"}) is True
    profile = _profile()
    one = new_ledger("project-alpha", profile)
    one = append_event(
        one,
        _event("branch_created", "main", _created_payload("Main")),
        [profile],
    )
    projection = replay_ledger(one, [profile])
    assert checkpoint_summary(
        projection, moment="design_freeze", env={ENV_FLAG: "1"}
    ) is None
    two, profile = _two_branch_ledger(profile)
    projection = replay_ledger(two, [profile])
    assert checkpoint_summary(projection, moment="stage_2_5", env={}) is None
    rendered = checkpoint_summary(
        projection, moment="stage_4_5", env={ENV_FLAG: "1"}
    )
    assert rendered is not None
    assert "main [active; author_originated]" in rendered
    assert "parked=1" in rendered
    assert "archived" not in rendered
    assert "skip | off | reset-to-simple-path" in rendered


def test_signal_summary_names_parked_branch_for_author_judgment() -> None:
    ledger, profile = _two_branch_ledger()
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "await evidence"}, minute=2),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event(
            "reopen_condition_signal",
            "main",
            {
                "branch_id_ref": "main",
                "condition_id": "invariance-fails",
                "evidence_pointer": "result-row-7",
            },
            actor="ai",
            minute=3,
        ),
        [profile],
    )
    projection = replay_ledger(ledger, [profile])
    signal_id = projection["reopen_condition_signals"][0]["event_id"]
    rendered = checkpoint_summary(
        projection,
        moment="reopen_condition_signal",
        signal_event_id=signal_id,
        env={ENV_FLAG: "1"},
    )
    assert (
        "main [parked; author_originated] — AUTHOR JUDGMENT REQUIRED" in rendered
    )
    assert "result-row-7" in rendered
    with pytest.raises(ContractError, match="required"):
        checkpoint_summary(
            projection,
            moment="reopen_condition_signal",
            env={ENV_FLAG: "1"},
        )


def test_signal_summary_rejects_retired_condition_or_nonreopenable_branch() -> None:
    ledger, profile = _two_branch_ledger()
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "await evidence"}, minute=2),
        [profile],
    )
    signaled = append_event(
        ledger,
        _event(
            "reopen_condition_signal",
            "main",
            {
                "branch_id_ref": "main",
                "condition_id": "invariance-fails",
                "evidence_pointer": "result-row-7",
            },
            actor="ai",
            minute=3,
        ),
        [profile],
    )
    signal_id = replay_ledger(signaled, [profile])["reopen_condition_signals"][0][
        "event_id"
    ]

    retired = append_event(
        signaled,
        _event(
            "branch_annotated",
            "main",
            {"field": "reopen_conditions", "value": []},
            minute=4,
        ),
        [profile],
    )
    with pytest.raises(ContractError, match="condition_id is no longer current"):
        checkpoint_summary(
            replay_ledger(retired, [profile]),
            moment="reopen_condition_signal",
            signal_event_id=signal_id,
            env={ENV_FLAG: "1"},
        )

    archived = append_event(
        signaled,
        _event("branch_archived", "main", {"reason": "closed"}, minute=4),
        [profile],
    )
    with pytest.raises(ContractError, match="not currently eligible"):
        checkpoint_summary(
            replay_ledger(archived, [profile]),
            moment="reopen_condition_signal",
            signal_event_id=signal_id,
            env={ENV_FLAG: "1"},
        )


def test_signal_summary_rejects_active_or_unadopted_ai_branch() -> None:
    ledger, profile = _two_branch_ledger()
    active_signal = append_event(
        ledger,
        _event(
            "reopen_condition_signal",
            "main",
            {
                "branch_id_ref": "main",
                "condition_id": "invariance-fails",
                "evidence_pointer": "result-row-7",
            },
            actor="ai",
            minute=2,
        ),
        [profile],
    )
    projection = replay_ledger(active_signal, [profile])
    with pytest.raises(ContractError, match="not currently eligible"):
        checkpoint_summary(
            projection,
            moment="reopen_condition_signal",
            signal_event_id=projection["reopen_condition_signals"][0]["event_id"],
            env={ENV_FLAG: "1"},
        )

    annotated = append_event(
        ledger,
        _event(
            "branch_annotated",
            "facet",
            {
                "field": "reopen_conditions",
                "value": [
                    {"condition_id": "facet-signal", "statement": "Facet condition"}
                ],
            },
            minute=2,
        ),
        [profile],
    )
    facet_signal = append_event(
        annotated,
        _event(
            "reopen_condition_signal",
            "facet",
            {
                "branch_id_ref": "facet",
                "condition_id": "facet-signal",
                "evidence_pointer": "result-row-9",
            },
            actor="ai",
            minute=3,
        ),
        [profile],
    )
    projection = replay_ledger(facet_signal, [profile])
    with pytest.raises(ContractError, match="not currently eligible"):
        checkpoint_summary(
            projection,
            moment="reopen_condition_signal",
            signal_event_id=projection["reopen_condition_signals"][0]["event_id"],
            env={ENV_FLAG: "1"},
        )


def test_absent_and_orphan_pointer_states(tmp_path: Path) -> None:
    profile = _profile()
    passport = _passport(tmp_path / "passport.yaml")
    absent = load_bound_ledger(
        passport, tmp_path, [profile], expected_project_ref="project-alpha"
    )
    assert absent["state"] == "absent"
    assert (tmp_path / ".passport.yaml.lock").is_file()
    assert not (tmp_path / ".passport.yaml.inquiry-ledger.lock").exists()
    default_relative = default_ledger_relative_path(passport, tmp_path)
    (tmp_path / default_relative).write_text("not even json", encoding="utf-8")
    orphan = load_bound_ledger(
        passport, tmp_path, [profile], expected_project_ref="project-alpha"
    )
    assert orphan["state"] == "orphan_ignored"
    assert "passport is authoritative" in orphan["notice"]


def test_shared_passport_sidecar_excludes_another_current_writer(
    tmp_path: Path,
) -> None:
    if fcntl is None:
        pytest.skip("POSIX advisory locking is unavailable")
    profile = _profile()
    passport = _passport(tmp_path / "passport.yaml")
    lock_path = tmp_path / ".passport.yaml.lock"
    lock_path.touch(mode=0o600)

    with lock_path.open("r+") as held:
        fcntl.flock(held.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ContractError, match="passport locked by another session"):
            load_bound_ledger(
                passport,
                tmp_path,
                [profile],
                expected_project_ref="project-alpha",
                lock_timeout=0,
            )


@pytest.mark.parametrize("lock_timeout", [float("nan"), float("inf"), float("-inf")])
def test_authoritative_lock_timeout_must_be_finite(
    tmp_path: Path, lock_timeout: float
) -> None:
    profile = _profile()
    passport = _passport(tmp_path / "passport.yaml")
    with pytest.raises(ContractError, match="finite number between 0 and 60"):
        load_bound_ledger(
            passport,
            tmp_path,
            [profile],
            expected_project_ref="project-alpha",
            lock_timeout=lock_timeout,
        )
    assert not (tmp_path / ".passport.yaml.lock").exists()


def test_authoritative_calls_require_project_identity_and_reject_null_pointer(
    tmp_path: Path,
) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    with pytest.raises(ContractError, match="expected_project_ref"):
        load_bound_ledger(passport, tmp_path, [profile])
    with pytest.raises(ContractError, match="expected_project_ref"):
        commit_ledger_transaction(
            passport,
            "passport.inquiry-branch-ledger.json",
            tmp_path,
            ledger,
            [profile],
        )

    passport.write_text(
        passport.read_text(encoding="utf-8") + "inquiry_ledger_ref: null\n",
        encoding="utf-8",
    )
    with pytest.raises(LedgerBindingError, match="present but null"):
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="project-alpha"
        )
    with pytest.raises(LedgerBindingError, match="present but null"):
        commit_ledger_transaction(
            passport,
            "passport.inquiry-branch-ledger.json",
            tmp_path,
            ledger,
            [profile],
            "project-alpha",
        )


@pytest.mark.parametrize(
    "reserved_name",
    [
        ".passport.yaml.lock",
        ".passport.yaml.inquiry-ledger.transaction.json",
        ".passport.yaml.inquiry-ledger.transaction.tmp",
        ".passport.yaml.inquiry-ledger.passport.tmp",
        ".passport.yaml.inquiry-ledger.ledger.tmp",
        ".passport.yaml.inquiry-ledger.register.tmp",
        ".PASSPORT.YAML.INQUIRY-LEDGER.LEDGER.TMP",
        ".PASSPORT.YAML.INQUIRY-LEDGER.REGISTER.TMP",
    ],
)
def test_commit_rejects_every_reserved_passport_transaction_target(
    tmp_path: Path, reserved_name: str
) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    with pytest.raises(ContractError, match="reserved passport transaction"):
        commit_ledger_transaction(
            passport,
            reserved_name,
            tmp_path,
            ledger,
            [profile],
            "project-alpha",
        )


def test_commit_rejects_casefolded_passport_target_alias(tmp_path: Path) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    with pytest.raises(ContractError, match="must not equal passport_path"):
        commit_ledger_transaction(
            passport,
            "PASSPORT.YAML",
            tmp_path,
            ledger,
            [profile],
            "project-alpha",
        )


@pytest.mark.parametrize("absolute", [False, True])
def test_commit_rejects_relative_and_absolute_symlink_ledger_targets(
    tmp_path: Path, absolute: bool
) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    target = tmp_path / "actual-ledger.json"
    alias = tmp_path / "ledger-alias.json"
    alias.symlink_to(target.name)
    ledger_argument = alias if absolute else alias.name

    with pytest.raises(ContractError, match="regular non-symlink"):
        commit_ledger_transaction(
            passport,
            ledger_argument,
            tmp_path,
            ledger,
            [profile],
            "project-alpha",
        )
    assert alias.is_symlink()
    assert not target.exists()


@pytest.mark.parametrize("operation", ["commit", "load", "recover"])
def test_authoritative_operations_reject_symlinked_passport_parent(
    tmp_path: Path, operation: str
) -> None:
    ledger, profile = _two_branch_ledger()
    actual = tmp_path / "actual"
    actual.mkdir()
    passport = _passport(actual / "passport.yaml")
    alias = tmp_path / "alias"
    alias.symlink_to(actual, target_is_directory=True)
    alias_passport = alias / passport.name

    with pytest.raises(ContractError, match="parent directory.*symlink"):
        if operation == "commit":
            commit_ledger_transaction(
                alias_passport,
                actual / "passport.inquiry-branch-ledger.json",
                tmp_path,
                ledger,
                [profile],
                "project-alpha",
            )
        elif operation == "load":
            load_bound_ledger(
                alias_passport,
                tmp_path,
                [profile],
                expected_project_ref="project-alpha",
            )
        else:
            recover_ledger_transaction(alias_passport, tmp_path)


def test_commit_and_bound_load_preserve_passport_comment_and_mode(tmp_path: Path) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    os.chmod(passport, 0o640)
    pointer = commit_ledger_transaction(
        passport,
        "passport.inquiry-branch-ledger.json",
        tmp_path,
        ledger,
        [profile],
        "project-alpha",
    )
    assert pointer["content_sha256"] == hashlib.sha256(canonical_bytes(ledger)).hexdigest()
    assert "# keep this comment" in passport.read_text(encoding="utf-8")
    assert stat.S_IMODE(passport.stat().st_mode) == 0o640
    loaded = load_bound_ledger(
        passport, tmp_path, [profile], expected_project_ref="project-alpha"
    )
    assert loaded["state"] == "bound"
    assert loaded["ledger"] == ledger
    assert loaded["projection"]["introduced_branch_count"] == 2


def test_binding_breaks_on_missing_mismatch_noncanonical_and_project_drift(
    tmp_path: Path,
) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    ledger_path = tmp_path / "passport.inquiry-branch-ledger.json"
    commit_ledger_transaction(
        passport, ledger_path, tmp_path, ledger, [profile], "project-alpha"
    )
    raw = ledger_path.read_bytes()
    ledger_path.unlink()
    with pytest.raises(LedgerBindingError, match="LEDGER-BINDING-BROKEN"):
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="project-alpha"
        )
    ledger_path.write_bytes(raw + b"\n")
    with pytest.raises(LedgerBindingError, match="exact canonical"):
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="project-alpha"
        )
    ledger_path.write_bytes(raw)
    with pytest.raises(LedgerBindingError, match="expected project_ref"):
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="another-project"
        )
    ledger_path.write_bytes(raw[:-1] + (b"0" if raw[-1:] != b"0" else b"1"))
    with pytest.raises(LedgerBindingError):
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="project-alpha"
        )


def test_passport_digest_detects_valid_prefix_truncation(tmp_path: Path) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    relative = "passport.inquiry-branch-ledger.json"
    commit_ledger_transaction(
        passport, relative, tmp_path, ledger, [profile], "project-alpha"
    )
    truncated = copy.deepcopy(ledger)
    truncated["events"] = truncated["events"][:1]
    (tmp_path / relative).write_bytes(canonical_bytes(truncated))
    with pytest.raises(LedgerBindingError, match="pointer digest"):
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="project-alpha"
        )


@pytest.mark.parametrize(
    "crash_phase",
    ["journal_durable", "ledger_published", "passport_published"],
)
def test_transaction_recovers_every_post_journal_crash(
    tmp_path: Path, crash_phase: str
) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    relative = "passport.inquiry-branch-ledger.json"
    commit_ledger_transaction(
        passport, relative, tmp_path, ledger, [profile], "project-alpha"
    )
    updated = _adopt_facet(ledger, [profile])

    def crash(phase: str) -> None:
        if phase == crash_phase:
            raise RuntimeError(f"crash at {phase}")

    with pytest.raises(RuntimeError, match="crash at"):
        commit_ledger_transaction(
            passport,
            relative,
            tmp_path,
            updated,
            [profile],
            "project-alpha",
            crash_hook=crash,
        )
    assert recover_ledger_transaction(passport, tmp_path) is True
    loaded = load_bound_ledger(
        passport, tmp_path, [profile], expected_project_ref="project-alpha"
    )
    assert loaded["ledger"] == updated
    assert loaded["projection"]["event_count"] == 3
    assert recover_ledger_transaction(passport, tmp_path) is False


def test_journal_binds_complete_old_and_new_passport_generations(
    tmp_path: Path,
) -> None:
    passport, ledger_path, journal_path, updated, profile = _leave_update_journal(
        tmp_path
    )
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    passport_temp = tmp_path / journal["passport_temp_path"]
    ledger_temp = tmp_path / journal["ledger_temp_path"]

    assert journal["old_passport_sha256"] == hashlib.sha256(
        passport.read_bytes()
    ).hexdigest()
    assert journal["new_passport_sha256"] == hashlib.sha256(
        passport_temp.read_bytes()
    ).hexdigest()
    assert journal["old_ledger_sha256"] == journal["old_pointer"]["content_sha256"]
    assert journal["new_ledger_sha256"] == journal["new_pointer"]["content_sha256"]
    assert journal["new_pointer"]["ledger_path"] == journal["ledger_path"]
    assert hashlib.sha256(ledger_temp.read_bytes()).hexdigest() == journal[
        "new_ledger_sha256"
    ]

    assert recover_ledger_transaction(passport, tmp_path) is True
    loaded = load_bound_ledger(
        passport, tmp_path, [profile], expected_project_ref="project-alpha"
    )
    assert Path(loaded["ledger_path"]) == ledger_path
    assert loaded["ledger"] == updated


@pytest.mark.parametrize(
    "mutation",
    [
        "new_pointer_path",
        "old_pointer_digest",
        "passport_temp_path",
        "ledger_temp_path",
        "reserved_lock_target",
        "reserved_journal_target",
        "reserved_journal_temp_target",
        "reserved_passport_temp_target",
        "reserved_ledger_temp_target",
        "reserved_register_temp_target",
        "casefold_reserved_ledger_temp_target",
        "casefold_reserved_register_temp_target",
    ],
)
def test_recovery_rejects_mutated_journal_relations_before_publication(
    tmp_path: Path, mutation: str
) -> None:
    passport, ledger_path, journal_path, _, _ = _leave_update_journal(tmp_path)
    old_passport = passport.read_bytes()
    old_ledger = ledger_path.read_bytes()
    journal = json.loads(journal_path.read_text(encoding="utf-8"))

    if mutation == "new_pointer_path":
        journal["new_pointer"]["ledger_path"] = "unbound.json"
    elif mutation == "old_pointer_digest":
        journal["old_ledger_sha256"] = "f" * 64
    elif mutation == "passport_temp_path":
        journal["passport_temp_path"] = "unrelated-passport.yaml"
    elif mutation == "ledger_temp_path":
        journal["ledger_temp_path"] = "unrelated-ledger.json"
    else:
        reserved = {
            "reserved_lock_target": ".passport.yaml.lock",
            "reserved_journal_target": (
                ".passport.yaml.inquiry-ledger.transaction.json"
            ),
            "reserved_journal_temp_target": (
                ".passport.yaml.inquiry-ledger.transaction.tmp"
            ),
            "reserved_passport_temp_target": (
                ".passport.yaml.inquiry-ledger.passport.tmp"
            ),
            "reserved_ledger_temp_target": (
                ".passport.yaml.inquiry-ledger.ledger.tmp"
            ),
            "reserved_register_temp_target": (
                ".passport.yaml.inquiry-ledger.register.tmp"
            ),
            "casefold_reserved_ledger_temp_target": (
                ".PASSPORT.YAML.INQUIRY-LEDGER.LEDGER.TMP"
            ),
            "casefold_reserved_register_temp_target": (
                ".PASSPORT.YAML.INQUIRY-LEDGER.REGISTER.TMP"
            ),
        }[mutation]
        journal["ledger_path"] = reserved
        journal["old_pointer"]["ledger_path"] = reserved
        journal["new_pointer"]["ledger_path"] = reserved
    journal_path.write_bytes(canonical_bytes(journal))

    with pytest.raises(TransactionRecoveryError, match="RECOVERY-REQUIRED"):
        recover_ledger_transaction(passport, tmp_path)
    assert passport.read_bytes() == old_passport
    assert ledger_path.read_bytes() == old_ledger
    assert journal_path.is_file()


def test_recovery_validates_complete_staged_passport_before_either_replace(
    tmp_path: Path,
) -> None:
    passport, ledger_path, journal_path, _, _ = _leave_update_journal(tmp_path)
    old_passport = passport.read_bytes()
    old_ledger = ledger_path.read_bytes()
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    passport_temp = tmp_path / journal["passport_temp_path"]
    passport_temp.write_bytes(passport_temp.read_bytes() + b"# external mutation\n")

    with pytest.raises(TransactionRecoveryError, match="complete new byte image"):
        recover_ledger_transaction(passport, tmp_path)
    assert passport.read_bytes() == old_passport
    assert ledger_path.read_bytes() == old_ledger


@pytest.mark.parametrize("temp_field", ["ledger_temp_path", "passport_temp_path"])
def test_recovery_rejects_symlinked_staged_sources_before_digest_or_replace(
    tmp_path: Path, temp_field: str
) -> None:
    passport, ledger_path, journal_path, _, _ = _leave_update_journal(tmp_path)
    old_passport = passport.read_bytes()
    old_ledger = ledger_path.read_bytes()
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    staged = tmp_path / journal[temp_field]
    staged_copy = tmp_path / f"copy-{temp_field}"
    staged_copy.write_bytes(staged.read_bytes())
    staged.unlink()
    staged.symlink_to(staged_copy)

    with pytest.raises(TransactionRecoveryError, match="non-symlink"):
        recover_ledger_transaction(passport, tmp_path)
    assert passport.read_bytes() == old_passport
    assert ledger_path.read_bytes() == old_ledger


def test_live_passport_full_byte_cas_preserves_concurrent_edit(tmp_path: Path) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    ledger_path = tmp_path / "passport.inquiry-branch-ledger.json"
    commit_ledger_transaction(
        passport, ledger_path, tmp_path, ledger, [profile], "project-alpha"
    )
    old_ledger = ledger_path.read_bytes()
    updated = _adopt_facet(ledger, [profile])

    def mutate_without_crashing(phase: str) -> None:
        if phase == "journal_durable":
            passport.write_text(
                passport.read_text(encoding="utf-8") + "external_note: keep-me\n",
                encoding="utf-8",
            )

    with pytest.raises(TransactionRecoveryError, match="live passport changed"):
        commit_ledger_transaction(
            passport,
            ledger_path,
            tmp_path,
            updated,
            [profile],
            "project-alpha",
            crash_hook=mutate_without_crashing,
        )
    assert "external_note: keep-me" in passport.read_text(encoding="utf-8")
    assert ledger_path.read_bytes() == old_ledger
    with pytest.raises(TransactionRecoveryError, match="neither the recorded old nor new"):
        recover_ledger_transaction(passport, tmp_path)


def test_live_ledger_full_byte_cas_preserves_concurrent_edit(tmp_path: Path) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    ledger_path = tmp_path / "passport.inquiry-branch-ledger.json"
    commit_ledger_transaction(
        passport, ledger_path, tmp_path, ledger, [profile], "project-alpha"
    )
    old_passport = passport.read_bytes()
    updated = _adopt_facet(ledger, [profile])

    def mutate_without_crashing(phase: str) -> None:
        if phase == "journal_durable":
            ledger_path.write_bytes(ledger_path.read_bytes() + b"\n")

    with pytest.raises(TransactionRecoveryError, match="live ledger changed"):
        commit_ledger_transaction(
            passport,
            ledger_path,
            tmp_path,
            updated,
            [profile],
            "project-alpha",
            crash_hook=mutate_without_crashing,
        )
    assert passport.read_bytes() == old_passport
    assert ledger_path.read_bytes().endswith(b"\n")
    with pytest.raises(TransactionRecoveryError, match="neither the recorded old nor new"):
        recover_ledger_transaction(passport, tmp_path)


def test_prejournal_crash_keeps_old_pair_and_retry_cleans_temps(tmp_path: Path) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    relative = "passport.inquiry-branch-ledger.json"
    commit_ledger_transaction(
        passport, relative, tmp_path, ledger, [profile], "project-alpha"
    )
    updated = _adopt_facet(ledger, [profile])

    def crash(phase: str) -> None:
        if phase == "temps_durable":
            raise RuntimeError("prejournal")

    with pytest.raises(RuntimeError, match="prejournal"):
        commit_ledger_transaction(
            passport,
            relative,
            tmp_path,
            updated,
            [profile],
            "project-alpha",
            crash_hook=crash,
        )
    assert recover_ledger_transaction(passport, tmp_path) is False
    assert (
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="project-alpha"
        )["ledger"]
        == ledger
    )
    commit_ledger_transaction(
        passport, relative, tmp_path, updated, [profile], "project-alpha"
    )
    assert (
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="project-alpha"
        )["ledger"]
        == updated
    )


def test_crash_after_journal_clear_is_already_committed(tmp_path: Path) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    relative = "passport.inquiry-branch-ledger.json"

    def crash(phase: str) -> None:
        if phase == "journal_cleared":
            raise RuntimeError("after commit")

    with pytest.raises(RuntimeError, match="after commit"):
        commit_ledger_transaction(
            passport,
            relative,
            tmp_path,
            ledger,
            [profile],
            "project-alpha",
            crash_hook=crash,
        )
    assert recover_ledger_transaction(passport, tmp_path) is False
    assert (
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="project-alpha"
        )["ledger"]
        == ledger
    )


def test_corrupt_recovery_journal_fails_visible(tmp_path: Path) -> None:
    profile = _profile()
    passport = _passport(tmp_path / "passport.yaml")
    journal = tmp_path / ".passport.yaml.inquiry-ledger.transaction.json"
    journal.write_text("{broken", encoding="utf-8")
    with pytest.raises(TransactionRecoveryError, match="RECOVERY-REQUIRED"):
        load_bound_ledger(
            passport, tmp_path, [profile], expected_project_ref="project-alpha"
        )


def test_transaction_refuses_rewrite_noop_path_switch_and_orphan_adoption(
    tmp_path: Path,
) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    relative = "passport.inquiry-branch-ledger.json"
    commit_ledger_transaction(
        passport, relative, tmp_path, ledger, [profile], "project-alpha"
    )
    with pytest.raises(ContractError, match="append at least one"):
        commit_ledger_transaction(
            passport, relative, tmp_path, ledger, [profile], "project-alpha"
        )
    rewritten = _adopt_facet(ledger, [profile])
    rewritten["events"][0]["payload"]["statement"] = "history rewrite"
    # Repair the chain to prove append-only prefix comparison, not hash checking,
    # is what catches a fully rehashed historical rewrite.
    for index, event in enumerate(rewritten["events"]):
        event["prev_event_sha256"] = (
            "0" * 64
            if index == 0
            else hashlib.sha256(canonical_bytes(rewritten["events"][index - 1])).hexdigest()
        )
    with pytest.raises((ContractError, LedgerBindingError), match="rewritten|reordered"):
        commit_ledger_transaction(
            passport, relative, tmp_path, rewritten, [profile], "project-alpha"
        )
    with pytest.raises(ContractError, match="stable ledger_path"):
        commit_ledger_transaction(
            passport,
            "other.inquiry-branch-ledger.json",
            tmp_path,
            _adopt_facet(ledger, [profile]),
            [profile],
            "project-alpha",
        )

    orphan_passport = _passport(tmp_path / "other-passport.yaml")
    orphan_relative = "other-passport.inquiry-branch-ledger.json"
    (tmp_path / orphan_relative).write_bytes(canonical_bytes(ledger))
    with pytest.raises(ContractError, match="ignored orphan"):
        commit_ledger_transaction(
            orphan_passport,
            orphan_relative,
            tmp_path,
            ledger,
            [profile],
            "project-alpha",
        )


def test_publication_refuses_simple_path_and_workspace_escape(tmp_path: Path) -> None:
    profile = _profile()
    passport = _passport(tmp_path / "passport.yaml")
    one = new_ledger("project-alpha", profile)
    one = append_event(
        one,
        _event("branch_created", "main", _created_payload("Main")),
        [profile],
    )
    with pytest.raises(ContractError, match="at least two"):
        commit_ledger_transaction(
            passport,
            "passport.inquiry-branch-ledger.json",
            tmp_path,
            one,
            [profile],
            "project-alpha",
        )
    with pytest.raises(ContractError, match=r"\.\.|workspace-relative"):
        commit_ledger_transaction(
            passport,
            "../escape.json",
            tmp_path,
            _two_branch_ledger(profile)[0],
            [profile],
            "project-alpha",
        )


def test_cli_validate_replay_append_and_default_off_summary(tmp_path: Path) -> None:
    ledger, profile = _two_branch_ledger()
    ledger_path = _write_canonical(tmp_path / "ledger.json", ledger)
    profile_path = _write_canonical(tmp_path / "profile.json", profile)
    validate = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "validate",
            str(ledger_path),
            "--profile",
            str(profile_path),
            "--project-ref",
            "project-alpha",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert validate.returncode == 0, validate.stderr
    assert json.loads(validate.stdout)["status"] == "valid"

    replay = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "replay",
            str(ledger_path),
            "--profile",
            str(profile_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert replay.returncode == 0, replay.stderr
    assert json.loads(replay.stdout)["introduced_branch_count"] == 2

    event_path = _write_canonical(
        tmp_path / "event.json",
        _event(
            "branch_adopted",
            "facet",
            {
                "source_event_id": 2,
                "surfaced_text": "Alternative mechanism",
                "author_formulation": "Author-owned alternative mechanism",
            },
            minute=2,
        ),
    )
    appended = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "append",
            str(ledger_path),
            "--profile",
            str(profile_path),
            "--project-ref",
            "project-alpha",
            "--event",
            str(event_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert appended.returncode == 0, appended.stderr
    assert len(json.loads(appended.stdout)["events"]) == 3

    env = dict(os.environ)
    env.pop(ENV_FLAG, None)
    summary = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "summary",
            str(ledger_path),
            "--profile",
            str(profile_path),
            "--project-ref",
            "project-alpha",
            "--moment",
            "stage_2_5",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert summary.returncode == 0, summary.stderr
    assert summary.stdout == ""
    forced = subprocess.run(
        [*summary.args, "--force"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert forced.returncode == 0, forced.stderr
    assert "Inquiry branches" in forced.stdout


@pytest.mark.parametrize("command", ["append", "summary", "load-bound", "commit"])
def test_authoritative_cli_commands_require_project_ref(
    tmp_path: Path, command: str
) -> None:
    ledger, profile = _two_branch_ledger()
    passport = _passport(tmp_path / "passport.yaml")
    ledger_path = _write_canonical(tmp_path / "ledger-input.json", ledger)
    profile_path = _write_canonical(tmp_path / "profile.json", profile)
    if command in {"append", "summary"}:
        args = [
            sys.executable,
            str(RUNTIME),
            command,
            str(ledger_path),
            "--profile",
            str(profile_path),
        ]
        if command == "append":
            event_path = _write_canonical(
                tmp_path / "event.json",
                _event(
                    "branch_adopted",
                    "facet",
                    {
                        "source_event_id": 2,
                        "surfaced_text": "Alternative mechanism",
                        "author_formulation": "Author-owned alternative mechanism",
                    },
                    minute=2,
                ),
            )
            args.extend(["--event", str(event_path)])
        else:
            args.extend(["--moment", "stage_2_5"])
    else:
        args = [
            sys.executable,
            str(RUNTIME),
            command,
            "--passport",
            str(passport),
            "--workspace-root",
            str(tmp_path),
            "--profile",
            str(profile_path),
        ]
    if command == "commit":
        args.extend(
            [
                "--ledger-path",
                "passport.inquiry-branch-ledger.json",
                "--ledger",
                str(ledger_path),
            ]
        )
    result = subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "--project-ref" in result.stderr and "required" in result.stderr


def test_render_summary_excludes_archived_and_merged_details() -> None:
    ledger, profile = _two_branch_ledger()
    ledger = _adopt_facet(ledger, [profile])
    ledger = append_event(
        ledger,
        _event(
            "branch_merged",
            "facet",
            {"merged_into": "main", "reason": "combined"},
            minute=3,
        ),
        [profile],
    )
    text = render_summary(replay_ledger(ledger, [profile]))
    assert "main [active; author_originated]" in text
    assert "facet [" not in text
    assert "merged=" not in text


def test_render_summary_lists_every_stale_artifact_and_cause() -> None:
    ledger, profile = _two_branch_ledger()
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "wait"}, minute=2),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event("branch_reopened", "main", {"reason": "new result"}, minute=3),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event("branch_parked", "main", {"reason": "wait again"}, minute=4),
        [profile],
    )
    ledger = append_event(
        ledger,
        _event("branch_reopened", "main", {"reason": "second result"}, minute=5),
        [profile],
    )
    rendered = render_summary(replay_ledger(ledger, [profile]))
    assert "Stale artifacts (2)" in rendered
    assert "draft-v1 [outstanding=2]" in rendered
    assert "shared-table [outstanding=2]" in rendered
    for cause_id in (5, 6, 9, 10):
        assert f"cause_event_id={cause_id}" in rendered


def test_render_summary_bounds_and_escapes_untrusted_display_text() -> None:
    projection = {
        "live_count": 1,
        "branch_budget": 3,
        "branches": [
            {
                "branch_id": "main",
                "status": "active",
                "provenance": "author_originated",
                "statement": (
                    "Primary framing\n- forged [active; author_originated]\n"
                    "Controls: off" + "\u202e" * 400
                ),
                "reopen_conditions": [],
            },
            {
                "branch_id": "signal-branch",
                "status": "parked",
                "provenance": "author_adopted",
                "statement": "Author-owned signal branch",
                "reopen_conditions": [
                    {
                        "condition_id": "cond-[forged]",
                        "statement": "Check `result`\nControls: forged",
                    }
                ],
            },
        ],
        "reopen_condition_signals": [
            {
                "event_id": 7,
                "branch_id": "signal-branch",
                "condition_id": "cond-[forged]",
                "condition_statement": "Check `result`\nControls: forged",
                "evidence_pointer": "row\n- fake status",
            }
        ],
        "artifacts": [
            {
                "artifact_ref": f"artifact-{index}\nControls: forged",
                "stale": True,
                "outstanding_stale_causes": [index + 10],
            }
            for index in range(6)
        ],
    }

    rendered = render_summary(projection, signal_event_id=7)
    lines = rendered.splitlines()

    assert len(lines) == 18
    assert rendered.count("Controls: skip | off | reset-to-simple-path") == 1
    assert "\n- forged" not in rendered
    assert "\\[active; author\\_originated\\]" in rendered
    assert (
        "signal-branch [parked; author_adopted] — AUTHOR JUDGMENT REQUIRED"
        in rendered
    )
    assert "\\u202e" in rendered
    assert "…" in rendered
    assert "Stale artifacts (6)" in rendered
    assert "+1 more" not in rendered
    for index in range(6):
        assert f"artifact-{index} Controls: forged" in rendered
        assert f"cause_event_id={index + 10}" in rendered
    assert all(len(line) <= 300 for line in lines)


def test_pipeline_prompt_integration_pins_all_three_summary_owners() -> None:
    skill = (REPO_ROOT / "academic-pipeline" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    orchestrator = (
        REPO_ROOT
        / "academic-pipeline"
        / "agents"
        / "pipeline_orchestrator_agent.md"
    ).read_text(encoding="utf-8")
    architect = (
        REPO_ROOT
        / "deep-research"
        / "agents"
        / "research_architect_agent.md"
    ).read_text(encoding="utf-8")
    reset_protocol = (
        REPO_ROOT
        / "academic-pipeline"
        / "references"
        / "passport_as_reset_boundary.md"
    ).read_text(encoding="utf-8")

    for surface in (skill, orchestrator):
        assert "ARS_INQUIRY_LEDGER=1" in surface
        assert "scripts/inquiry_branch_ledger.py" in surface
        assert "Stage 1 design-freeze" in surface
        assert "Stage 2.5" in surface and "Stage 4.5" in surface
        assert "reset-to-simple-path" in surface
    assert "scripts/inquiry_branch_ledger.py::checkpoint_summary" in architect
    assert "moment=design_freeze" in architect
    assert (
        "omit the entire heading and ask no additional branch question"
        in " ".join(architect.split())
    )
    for surface in (orchestrator, reset_protocol):
        assert ".<passport-basename>.lock" in surface
        assert "replaceable passport inode" in surface
