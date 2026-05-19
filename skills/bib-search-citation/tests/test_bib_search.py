#!/usr/bin/env python3
"""Tests for the bib-search-citation helper scripts."""

from __future__ import annotations

import importlib
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

preview_bib_search = importlib.import_module("preview_bib_search")

SEARCH_SCRIPT = SCRIPTS_DIR / "search_bib.py"
PREVIEW_SCRIPT = SCRIPTS_DIR / "preview_bib_search.py"
FIXTURE_BIB = Path(__file__).parent / "fixtures" / "library.bib"
PREVIEW_INPUT = Path(__file__).parent / "fixtures" / "preview_input.json"


def run_python_script(
    script: Path, *args: str, input_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        input=input_text,
        capture_output=True,
        text=True,
        check=True,
    )


def run_search(*args: str) -> dict:
    completed = run_python_script(SEARCH_SCRIPT, "--bib", str(FIXTURE_BIB), *args)
    return json.loads(completed.stdout)


def test_search_bib_json_contract_and_citations():
    payload = run_search(
        "--query",
        "mamba forecasting author:Cheng year>=2024 has:code cite:both limit:1",
    )

    assert payload["meta"]["query"] == "mamba forecasting"
    assert payload["meta"]["returned_entries"] == 1
    assert payload["meta"]["applied_filters"]["author_contains"] == ["Cheng"]
    assert payload["meta"]["applied_filters"]["has"] == ["code"]

    result = payload["results"][0]
    assert result["key"] == "Doe2024Mamba"
    assert result["flags"]["code"] is True
    assert result["flags"]["pdf"] is True
    assert "raw_bib" not in result
    assert result["citations"]["latex"]["cite"] == r"\cite{Doe2024Mamba}"
    assert result["citations"]["typst"]["inline"] == "@Doe2024Mamba"


def test_search_bib_include_raw_bib_without_preview_fields():
    payload = run_search(
        "--query",
        "photovoltaic raw:true cite:none limit:1",
    )

    assert payload["meta"]["returned_entries"] == 1
    result = payload["results"][0]
    assert result["key"] == "Lee2025Photovoltaic"
    assert "raw_bib" in result
    assert "@article{Lee2025Photovoltaic" in result["raw_bib"]
    assert "citations" not in result


def test_filter_only_query_keeps_sort_behavior():
    payload = run_search(
        "--query",
        "type:article sort:year_desc limit:2",
    )

    years = [result["year"] for result in payload["results"]]
    assert years == [2025, 2024]
    assert all(result["score"] == 0 for result in payload["results"])


def test_empty_query_result_is_still_valid_json():
    payload = run_search(
        "--query",
        "author:Nonexistent year>=2030 limit:5",
    )

    assert payload["meta"]["matched_entries"] == 0
    assert payload["meta"]["returned_entries"] == 0
    assert payload["results"] == []


def test_preview_from_stdin_renders_summary_and_hides_raw_bib():
    payload = run_search(
        "--query",
        "photovoltaic raw:true cite:both limit:1",
    )
    preview = run_python_script(
        PREVIEW_SCRIPT,
        input_text=json.dumps(payload, ensure_ascii=False),
    ).stdout

    assert "Query: photovoltaic | sort=relevance | returned=1 of 3 matched (3 total)" in preview
    assert "Filters: none" in preview
    assert "1. Lee2025Photovoltaic [article]" in preview
    assert "DOI: 10.1000/pv-mamba" in preview
    assert "LaTeX: \\cite{Lee2025Photovoltaic}" in preview
    assert "Typst: @Lee2025Photovoltaic | #cite(<Lee2025Photovoltaic>)" in preview
    assert "@article{Lee2025Photovoltaic" not in preview


def test_preview_input_file_mode_and_truncation():
    preview = run_python_script(PREVIEW_SCRIPT, "--input", str(PREVIEW_INPUT)).stdout

    assert "Annotation: " + ("A" * 157) + "..." in preview
    assert "Abstract: " + ("B" * 237) + "..." in preview
    assert "Keywords: " in preview and "..." in preview
    assert "LaTeX:" not in preview
    assert "Typst:" not in preview
    assert "@article{Lee2025Photovoltaic" not in preview


def test_preview_reports_invalid_payload(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    with pytest.raises(ValueError, match="expected JSON input"):
        preview_bib_search.load_payload(type("Args", (), {"input": None})())
