"""Consensus levels for findings below the consensus bar (#1100).

`revision-roadmap/1.1` adds `CORROBORATED` (agree = 2) and `SINGLE-REVIEWER`
(agree = 1). A `revision-roadmap/1.0` roadmap stays readable but cannot carry
either value. A matching DA row goes into `corroborating_sources[]`.
"""
from __future__ import annotations

import copy

import pytest

from scripts.revision_roadmap import (
    CURRENT_ROADMAP_VERSION,
    ROADMAP_SCHEMA_PATH,
    _schema_failures,
)

NEW_LEVELS = ("CORROBORATED", "SINGLE-REVIEWER")
OLD_LEVELS = ("CONSENSUS-4", "CONSENSUS-3", "SPLIT", "DA-CRITICAL", "SINGLE-VERIFIER")


def _item(level: str) -> dict:
    return {
        "id": "REV-001",
        "source_refs": [{"seat": "R3", "channel": "finding", "ordinal": 1, "subclaim_ordinal": 0}],
        "description": "The funding recommendation assumes every site benefits.",
        "reviewer": "R3",
        "obligation_class": "should_fix",
        "severity": "minor",
        "evidence_anchor": {
            "anchor_type": "text",
            "locator": "§6 Implications",
            "quote": "every site gains from the pooled rule",
        },
        "confidence": 2,
        "competence_basis": "adjacent: policy implications",
        "cost_scope": {"kind": "section", "locator": "§6 Implications"},
        "consequence_if_unaddressed": {
            "code": "reader_traceability_reduced",
            "target": {"kind": "section", "locator": "§6 Implications"},
        },
        "target_section": "§6 Implications",
        "suggested_action": "Support the premise or narrow the recommendation.",
        "consensus_level": level,
        "verification_criteria": "The premise is supported or the recommendation is narrowed.",
        "proposed_targets": [{"block_id": "B0001", "allowed_operations": ["replace_block"]}],
    }


def _roadmap(version: str, level: str) -> dict:
    return {
        "schema_version": version,
        "revision_round": 1,
        "base_draft_sha256": "a" * 64,
        "block_manifest_sha256": "b" * 64,
        "items": [_item(level)],
        "total_items": 1,
        "obligation_counts": {"must_fix": 0, "should_fix": 1, "consider": 0},
        "editorial_decision": "Minor Revision",
        "consensus_summary": "One finding below the consensus bar.",
        "dissenting_opinions": [],
    }


def _failures(roadmap: dict) -> list[str]:
    return _schema_failures(roadmap, ROADMAP_SCHEMA_PATH, "roadmap")


def test_current_version_is_1_1() -> None:
    assert CURRENT_ROADMAP_VERSION == "revision-roadmap/1.1"


def test_fixture_is_valid_apart_from_the_level() -> None:
    assert _failures(_roadmap("revision-roadmap/1.1", "SINGLE-VERIFIER")) == []


@pytest.mark.parametrize("level", NEW_LEVELS + OLD_LEVELS)
def test_version_1_1_accepts_every_level(level: str) -> None:
    assert _failures(_roadmap("revision-roadmap/1.1", level)) == []


@pytest.mark.parametrize("level", OLD_LEVELS)
def test_version_1_0_stays_readable(level: str) -> None:
    assert _failures(_roadmap("revision-roadmap/1.0", level)) == []


@pytest.mark.parametrize("level", NEW_LEVELS)
def test_version_1_0_rejects_the_new_levels(level: str) -> None:
    failures = _failures(_roadmap("revision-roadmap/1.0", level))
    assert any("consensus_level" in failure for failure in failures), failures


def test_unknown_version_fails() -> None:
    assert _failures(_roadmap("revision-roadmap/1.2", "SINGLE-REVIEWER"))


def test_da_row_fits_corroborating_sources() -> None:
    roadmap = _roadmap("revision-roadmap/1.1", "SINGLE-REVIEWER")
    item = roadmap["items"][0]
    item["corroborating_sources"] = [
        {
            "reviewer": "DA",
            "severity": "major",
            "evidence_anchor": copy.deepcopy(item["evidence_anchor"]),
            "confidence": 4,
            "competence_basis": "core: adversarial challenge of premises",
        }
    ]
    assert _failures(roadmap) == []
