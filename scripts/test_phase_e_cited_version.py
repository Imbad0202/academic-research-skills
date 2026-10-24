#!/usr/bin/env python3
"""#1006 fixture: Phase E rows for a cited published version.

The manuscript cites the published version of an article. Only a working-paper
version of the same work is readable, and it says something different. Under
the #1006 rule the claim gets an access note (UNVERIFIABLE_ACCESS with an
``access_failed`` excerpt), never a verdict built from the working paper, and
the row's display_label names the cited version. These tests pin that the
evidence-row carrier records and renders that outcome. Whether an agent follows
the rule is prompt-level and is not measured here.
"""

from __future__ import annotations

import json

from scripts import evidence_rows as er


CITED_LABEL = "Lee 2023, journal article, doi:10.5555/example.2023.001"
PUBLISHED_TEXT = (
    "Results. Across 412 firms, the adoption rate rose by 4.1 percentage points."
)
WORKING_PAPER_TEXT = (
    "Preliminary results. Across 380 firms, the adoption rate rose by 6.3 percentage points."
)


def _raw(verdict: str, detail: str, anchor: str) -> dict:
    return {
        "surface": "phase_e_claim_verification",
        "row_id": "EVR-1006-001",
        "claim": {
            "claim_id": "E-C-1006",
            "text": "Adoption rose by 4.1 percentage points across 412 firms.",
            "paper_locator": "Literature review, paragraph 2",
            "selection_tier": "HIGH-IMPACT",
        },
        "source": {
            "ref_slug": "lee2023",
            "display_label": CITED_LABEL,
            "source_artifact_sha256": None,
        },
        "anchor": {"kind": "quote", "value_encoded": anchor},
        "verdict": verdict,
        "detail": detail,
        "content_handling": {
            "sharing_scope": "session_only",
            "rights_basis": "not_assessed",
        },
    }


def test_unreadable_cited_version_is_an_access_note_not_a_verdict() -> None:
    raw = _raw(
        "UNVERIFIABLE_ACCESS",
        "Cited version not readable; asked the user for its PDF.",
        "the%20adoption%20rate%20rose%20by%204.1%20percentage%20points",
    )
    row = er.build(raw, None, failure_state="access_failed")
    er.validate(row)

    assert row["verdict"] == "UNVERIFIABLE_ACCESS"
    assert row["excerpt"]["state"] == "access_failed"
    assert row["excerpt"]["text"] is None
    assert row["source"]["source_content_sha256"] is None
    assert row["source"]["display_label"] == CITED_LABEL
    serialized = json.dumps(row, ensure_ascii=False)
    assert "380 firms" not in serialized
    assert "6.3" not in serialized

    rendered = er.render_markdown([row])
    assert "ACCESS FAILED" in rendered
    assert "Lee 2023, journal article, doi" in rendered


def test_verified_row_names_the_version_that_was_read() -> None:
    raw = _raw(
        "VERIFIED",
        "Claim matches the cited published version.",
        "the%20adoption%20rate%20rose%20by%204.1%20percentage%20points",
    )
    row = er.build(raw, PUBLISHED_TEXT)
    er.validate(row, PUBLISHED_TEXT)

    assert row["excerpt"]["state"] == "verified_exact_match"
    rendered = er.render_markdown([row], session_sources={"lee2023": PUBLISHED_TEXT})
    assert "Lee 2023, journal article, doi" in rendered
    assert WORKING_PAPER_TEXT not in rendered
