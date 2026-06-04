#!/usr/bin/env python3
"""Tests for the verify_passport CLI (Delta 5 ad-hoc entry point).

Spec: docs/design/2026-05-21-v3.10-182-promote-citation-gate-spec.md §2 Delta 5
(`python -m scripts.verify_passport <passport.yaml>`).

The CLI is a thin wrapper: it loads a passport YAML and prints the
verification summary as JSON. Network resolvers are real by default; tests
inject a no-network clients factory via the public `run` seam.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _no_network_clients():
    def default():
        m = MagicMock()
        m.doi_lookup_with_title_check.return_value = None
        m.title_search.return_value = None
        m.arxiv_id_lookup.return_value = None
        m.lookup.return_value = {"matched": False}
        return m
    return {n: default() for n in
            ("crossref", "openalex", "semantic_scholar", "arxiv")}


def _write_passport(tmp_path, corpus):
    p = tmp_path / "passport.yaml"
    p.write_text(yaml.safe_dump({"literature_corpus": corpus}), encoding="utf-8")
    return p


def test_cli_emits_json_summary(tmp_path, capsys):
    from verify_passport import run

    # Production-shaped corpus entry: no anchor field (the anchor lives in writer
    # prose, not in literature_corpus). The ad-hoc CLI has no prose document, so
    # anchor_present is honestly False — a prose-join is a later-batch concern.
    passport = _write_passport(tmp_path, [
        {"citation_key": "a", "ref_slug": "slug-a", "title": "T",
         "doi": "10.5/x", "obtained_via": "folder-scan"},
    ])
    rc = run([str(passport)], clients_factory=_no_network_clients)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out) == 1
    assert out[0]["citation_key"] == "a"
    assert out[0]["lookup_verified"] == "false"  # id-keyed unmatched
    assert out[0]["anchor_present"] is False  # no prose anchor available


def test_cli_missing_file_errors(tmp_path):
    from verify_passport import run
    rc = run([str(tmp_path / "nope.yaml")], clients_factory=_no_network_clients)
    assert rc != 0


def test_cli_requires_path_arg():
    from verify_passport import run
    with pytest.raises(SystemExit):
        run([], clients_factory=_no_network_clients)
