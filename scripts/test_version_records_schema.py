"""Tests for Kong #258 version_records sidecar schema."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = REPO_ROOT / "shared/contracts/passport"


def _schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text())


def _valid_version_records() -> dict:
    return {
        "schema_version": "1.0",
        "version_records": [
            {
                "version_family_id": "attention-transformer-family",
                "canonical_slug": "vaswani2017",
                "primary_version_key": "attention-neurips-2017",
                "discovery_status": "user_confirmed",
                "reconciliation_note": "Scholar selected proceedings as the primary rendered citation.",
                "known_versions": [
                    {
                        "version_key": "attention-arxiv-v1",
                        "citation_key": "vaswani2017-arxiv-v1",
                        "kind": "arxiv_preprint",
                        "title": "Attention Is All You Need",
                        "year": 2017,
                        "venue": "arXiv",
                        "doi": None,
                        "arxiv_id": "1706.03762v1",
                        "url": "https://arxiv.org/abs/1706.03762v1",
                        "publication_date": {"value": "2017-06", "precision": "month"},
                        "metadata_provenance": "arxiv_api",
                        "source_locator": "arxiv:1706.03762v1",
                        "claim_scope_note": "Use only for claims verified against the v1 preprint text.",
                        "notes": None,
                    },
                    {
                        "version_key": "attention-neurips-2017",
                        "citation_key": "vaswani2017-neurips",
                        "kind": "proceedings",
                        "title": "Attention Is All You Need",
                        "year": 2017,
                        "venue": "NeurIPS 2017",
                        "doi": None,
                        "arxiv_id": None,
                        "url": "https://papers.nips.cc/paper/7181-attention-is-all-you-need",
                        "publication_date": {"value": "2017", "precision": "year"},
                        "metadata_provenance": "user_override",
                        "source_locator": "papers.nips.cc:7181",
                        "claim_scope_note": "Use for proceedings metadata and final citable record.",
                        "notes": None,
                    },
                ],
            }
        ],
    }


def test_version_records_schema_validates_canonical_example():
    jsonschema.validate(_valid_version_records(), _schema("version_records.schema.json"))


def test_version_records_rejects_unknown_top_level_field():
    bad = _valid_version_records()
    bad["literature_corpus_patch"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _schema("version_records.schema.json"))


def test_version_records_rejects_invalid_arxiv_id():
    bad = _valid_version_records()
    bad["version_records"][0]["known_versions"][0]["arxiv_id"] = "arXiv:1706.03762v1"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _schema("version_records.schema.json"))


def test_literature_corpus_entry_contract_remains_unmodified_for_version_families():
    """Kong #258 keeps version-family data in sidecar, not literature_corpus_entry."""
    literature_schema = _schema("literature_corpus_entry.schema.json")
    props = literature_schema["properties"]
    assert "version_family_id" not in props
    assert "version_records" not in props


def test_kong_258_agent_and_formatter_markers_present():
    timeline_agent = (REPO_ROOT / "deep-research/agents/timeline_extraction_agent.md").read_text()
    draft_writer = (REPO_ROOT / "academic-paper/agents/draft_writer_agent.md").read_text()
    formatter = (REPO_ROOT / "academic-paper/agents/formatter_agent.md").read_text()

    assert "## Academic Citation Version Discovery (Kong #258)" in timeline_agent
    assert "phase2_investigation/version_records.yaml" in timeline_agent
    assert "## Citation Version-Family Check (Kong #258)" in draft_writer
    assert "VERSION_INCONSISTENT_CITATION" in draft_writer
    assert "## Citation Version-Family Advisory (Kong #258)" in formatter
    assert "VERSION_INCONSISTENT_CITATION" in formatter


def test_kong_258_design_doc_documents_127_boundary_and_example_exists():
    design = (REPO_ROOT / "docs/design/2026-05-28-kong-258-version-family-reconciliation.md").read_text()
    example = REPO_ROOT / "academic-paper/examples/version_family_reconciliation_example.md"
    assert "#127 Boundary" in design
    assert "literature_corpus_entry.schema.json" in design
    assert "remains unchanged" in design
    assert "VERSION_INCONSISTENT_CITATION" in design
    assert example.exists()
