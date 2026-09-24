#!/usr/bin/env python3
"""Tests for scripts/check_acronyms.py (#849).

Every fixture is synthetic. The small cases below give one manuscript per
token rule and exclusion in the issue; the full manuscript under
tests/fixtures/acronym_check/ pins the JSON and both Markdown reports
byte for byte, so a change in wording, ordering, or line numbers shows.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.check_acronyms import (
    DEFAULT_ALLOWLIST,
    SCOPES,
    build_report,
    check,
    is_candidate,
    render,
)
from tests.test_helpers import run_script

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "check_acronyms.py"
FIXTURES = REPO / "tests" / "fixtures" / "acronym_check"


def findings(text: str, scopes: tuple[str, ...] = SCOPES, allow: frozenset[str] = DEFAULT_ALLOWLIST):
    report = check(text, scopes, allow)
    return [(f["scope"], f["line"], f["rule"], f["acronym"]) for f in report["findings"]]


# --- rules ---------------------------------------------------------------


def test_defined_before_use_is_clean() -> None:
    assert findings("A randomized controlled trial (RCT) ran. The RCT ended.\n") == []


def test_undefined_is_reported_at_first_use_with_the_count() -> None:
    report = check("We ran an RCT.\n\nThe RCT ended.\n", SCOPES, DEFAULT_ALLOWLIST)
    assert report["findings"] == [{"scope": "body", "line": 1, "rule": "undefined", "acronym": "RCT",
                                   "expansion": None, "occurrences": 2}]


def test_use_before_the_definition() -> None:
    text = "The RCT ran.\nA randomized controlled trial (RCT) is a design.\n"
    report = check(text, SCOPES, DEFAULT_ALLOWLIST)
    [finding] = report["findings"]
    assert (finding["line"], finding["rule"], finding["expansion"]) == (
        1, "defined_after_use", "randomized controlled trial")


def test_each_repeated_definition_is_reported_on_its_line() -> None:
    text = ("A large language model (LLM) helps.\n"
            "Later, a large language model (LLM) again.\n"
            "And large language models (LLMs) a third time.\n")
    assert findings(text) == [("body", 2, "defined_again", "LLM"), ("body", 3, "defined_again", "LLM")]


def test_scopes_define_independently() -> None:
    text = ("## Abstract\n\nThe RCT worked.\n\n"
            "## 摘要\n\n本研究採隨機對照試驗（randomized controlled trial, RCT）。\n\n"
            "## Introduction\n\nA randomized controlled trial (RCT) ran; the RCT ended.\n")
    assert findings(text) == [("abstract_en", 3, "undefined", "RCT")]


def test_chinese_definition_forms() -> None:
    text = ("## 中文摘要\n\n以大型語言模型（LLM）與隨機對照試驗（randomized controlled trial，RCT）。"
            "使用RCT設計與LLM輔助。\n")
    assert findings(text) == []


def test_unread_definition_form_is_a_coverage_limit_not_a_finding() -> None:
    report = check("The RCT (randomized controlled trial) ran. The RCT ended.\n", SCOPES,
                   DEFAULT_ALLOWLIST)
    assert report["findings"] == []
    assert report["status"] == "partial"
    assert report["coverage_limits"] == [{"scope": "body", "line": 1, "acronym": "RCT",
                                          "reason": "unread_definition_form"}]


def test_a_parenthetical_whose_words_do_not_spell_the_acronym_is_a_use() -> None:
    assert findings("The RCT (n = 120) ran. The LLM (see Section 2) helped.\n") == [
        ("body", 1, "undefined", "LLM"), ("body", 1, "undefined", "RCT")]


def test_a_definition_across_a_line_break() -> None:
    assert findings("A randomized controlled\ntrial (RCT) ran; the RCT ended.\n") == []
    assert findings("In a trial (randomized controlled trial,\nRCT) we saw the RCT end.\n") == []


def test_a_parenthetical_at_the_start_of_a_line_is_not_a_definition() -> None:
    assert findings("(RCT) was run.\n") == [("body", 1, "undefined", "RCT")]


# --- allowlist -------------------------------------------------------------


def test_default_and_user_allowlists() -> None:
    assert findings("DNA and HIV and the PhD and MHz.\n") == []
    assert findings("NLP helped.\n", allow=DEFAULT_ALLOWLIST | {"NLP"}) == []
    assert findings("NLP helped.\n") == [("body", 1, "undefined", "NLP")]


def test_allowlist_file_and_repeated_flags(tmp_path: Path) -> None:
    manuscript = tmp_path / "m.md"
    manuscript.write_text("NLP and SEM and IRT.\n", encoding="utf-8")
    allow = tmp_path / "allow.txt"
    allow.write_text("# discipline list\nSEM\n\nIRT  # item response theory\n", encoding="utf-8")
    report = build_report(manuscript, ",".join(SCOPES), ["NLP"], allow)
    assert report["findings"] == [] and report["allowlist"]["user"] == ["IRT", "NLP", "SEM"]


# --- token rules -----------------------------------------------------------


@pytest.mark.parametrize("token, expected", [
    ("RCT", True), ("eGFR", True), ("qPCR", True), ("mRNA", True), ("PhD", True), ("AI", True),
    ("BRCA1", True), ("RCT2", True), ("IV", True),
    ("H2O", False), ("CO2", False), ("H1N1", False),        # element symbols with counts
    ("II", False), ("XII", False),                          # Roman numerals
    ("SD", False), ("SE", False), ("CI", False),            # statistical symbols
    ("A", False), ("ABCDEFG", False), ("Hello", False), ("iPad", False),
])
def test_candidate_shape(token: str, expected: bool) -> None:
    assert is_candidate(token) is expected


def test_plural_and_possessive_count_as_the_base() -> None:
    text = "Large language models (LLMs) help. The LLM's output and two LLMs' outputs.\n"
    report = check(text, SCOPES, DEFAULT_ALLOWLIST)
    assert report["findings"] == []
    assert findings("The RCTs and the RCT's arm.\n") == [("body", 1, "undefined", "RCT")]


def test_whole_token_matching() -> None:
    report = check("The AIDS cohort and AI-based tools.\n", SCOPES, DEFAULT_ALLOWLIST)
    assert [(f["acronym"], f["occurrences"]) for f in report["findings"]] == [("AI", 1)]


# --- exclusions ------------------------------------------------------------


@pytest.mark.parametrize("label, text", [
    ("code span", "Use `RCT` here.\n"),
    ("code fence", "```\nRCT\n```\n"),
    ("tilde fence", "~~~python\nRCT = 1\n~~~\n"),
    ("html comment", "Text <!-- RCT --> text.\n"),
    ("multi-line comment", "<!-- a\nRCT\n-->\n"),
    ("ref and anchor markers", "A claim.<!--ref:smith2020--><!--anchor:quote:RCT%20arm-->\n"),
    ("front matter", "---\ntitle: RCT\n---\n\nBody.\n"),
    ("heading", "## The RCT\n\nBody.\n"),
    ("reference list", "Body.\n\n## References\n\nSmith, J. (2020). RCT methods. *RCT Journal*.\n"),
    ("table", "| RCT | x |\n|---|---|\n| LLM | y |\n"),
    ("image", "![RCT flow](flow.png)\n"),
    ("figure caption", "Figure 2. The RCT flow\n"),
    ("table caption", "**Table 1**\n"),
    ("note", "*Note.* RCT = randomized controlled trial.\n"),
    ("chinese note", "註：RCT 為隨機對照試驗。\n"),
    ("keywords", "**Keywords**: RCT, LLM\n"),
    ("chinese keywords", "關鍵詞：RCT、LLM\n"),
    ("scoring section", "Body.\n\n## Dimension Scores\n\nD1 RCT score.\n"),
    ("inline math", "The effect $F_{RCT}$ held.\n"),
    ("display math", "$$\nRCT = 1\n$$\n"),
    ("url", "See https://example.org/RCT and [a link](https://example.org/LLM).\n"),
    ("year citation", "As reported (WHO, 2020), it held.\n"),
    ("group author", "The World Health Organization [WHO] said so.\n"),
    ("author initials", "Smith JA, Jones BC (2019) agreed, as did Lee KM et al.\n"),
    ("statistical symbol", "The SD was 2.1 and the CI was narrow.\n"),
])
def test_exclusions(label: str, text: str) -> None:
    assert findings(text) == [], label


def test_sentence_start_word_before_an_acronym_is_not_an_author() -> None:
    assert findings("The RCT, conducted in 2020, ended.\n") == [("body", 1, "undefined", "RCT")]


def test_caption_word_at_sentence_start_is_still_prose() -> None:
    assert findings("Table 2 shows the RCT arm.\n") == [("body", 1, "undefined", "RCT")]


# --- scopes and coverage ---------------------------------------------------


def test_scope_runs_to_the_next_heading_at_its_level() -> None:
    text = ("## English Abstract\n\n### Paper title\n\nThe RCT worked.\n\n"
            "## Chinese Abstract (zh-TW)\n\n這項 LLM 研究。\n\n## Methods\n\nThe SEM fit.\n")
    report = check(text, SCOPES, DEFAULT_ALLOWLIST)
    assert findings(text) == [("body", 13, "undefined", "SEM"), ("abstract_en", 5, "undefined", "RCT"),
                              ("abstract_zh", 9, "undefined", "LLM")]
    assert report["scope_lines"] == {"body": [[12, 13]], "abstract_en": [[2, 2], [4, 6]],
                                     "abstract_zh": [[8, 10]]}


def test_unread_abstract_section_makes_coverage_partial() -> None:
    report = check("## Resumen\n\nUn ECA.\n\n## Body\n\nText.\n", SCOPES, DEFAULT_ALLOWLIST)
    assert report["unread_sections"] == [{"line": 1, "heading": "Resumen"}]
    assert report["status"] == "partial" and report["findings"] == []


def test_requested_scope_absent_from_the_input() -> None:
    report = check("Body text.\n", ("body", "abstract_en"), DEFAULT_ALLOWLIST)
    assert report["coverage"] == {"body": "checked", "abstract_en": "not_in_input",
                                  "abstract_zh": "not_requested"}
    assert report["status"] == "partial"


def test_unrequested_scope_is_not_read() -> None:
    text = "## Abstract\n\nThe RCT.\n\n## Body\n\nText.\n"
    assert findings(text, scopes=("body",)) == []


# --- clean versus not checked ------------------------------------------------


def _write(tmp_path: Path, name: str, data: bytes) -> Path:
    path = tmp_path / name
    path.write_bytes(data)
    return path


def test_clean_result_is_distinct_from_not_checked(tmp_path: Path) -> None:
    clean = build_report(_write(tmp_path, "m.md", b"A randomized controlled trial (RCT).\n"),
                         "body", [], None)
    assert (clean["status"], clean["findings"]) == ("checked", [])
    assert "reason" not in clean
    assert render(clean, "en").endswith("Coverage: body (complete)\nNo findings.")
    cases = {
        "unsupported_format": (_write(tmp_path, "m.docx", b"PK"), "body"),
        "unreadable_input": (_write(tmp_path, "bad.md", b"\xff\xfe RCT"), "body"),
        "unknown_scope": (_write(tmp_path, "ok.md", b"RCT\n"), "body,methods"),
        "no_requested_scope_in_input": (_write(tmp_path, "body.md", b"Body only.\n"), "abstract_zh"),
    }
    for reason, (path, scopes) in cases.items():
        report = build_report(path, scopes, [], None)
        assert (report["status"], report["reason"]) == ("not_checked", reason)
        assert "findings" not in report
        assert render(report, "en").splitlines()[1].startswith("Not checked: ")
        assert render(report, "zh-TW").splitlines()[1].startswith("未檢查：")
    missing = build_report(tmp_path / "absent.md", "body", [], None)
    assert missing["reason"] == "unreadable_input"


def test_cli_exit_codes_and_outputs(tmp_path: Path) -> None:
    manuscript = _write(tmp_path, "m.md", b"We ran an RCT.\n")
    out = tmp_path / "report.json"
    result = run_script(SCRIPT, "--input", str(manuscript), "--json-out", str(out))
    assert result.returncode == 0, result.stderr
    assert "| Body | 1 | Not defined | RCT | 1 |" in result.stdout
    assert json.loads(out.read_text(encoding="utf-8"))["findings"][0]["acronym"] == "RCT"
    result = run_script(SCRIPT, "--input", str(_write(tmp_path, "m.pdf", b"%PDF")))
    assert result.returncode == 2 and "Not checked:" in result.stdout
    result = run_script(SCRIPT, "--input", str(manuscript), "--json-out", str(manuscript))
    assert result.returncode == 2 and "may not be the input file" in result.stderr
    assert manuscript.read_bytes() == b"We ran an RCT.\n"


# --- fidelity and determinism -------------------------------------------------


def test_full_fixture_matches_the_pinned_reports(tmp_path: Path) -> None:
    source = FIXTURES / "manuscript.md"
    before = source.read_bytes()
    report = build_report(source, ",".join(SCOPES), [], None)
    assert source.read_bytes() == before  # the checker never edits the manuscript
    assert report.pop("input") == str(source)
    assert report["input_sha256"] == hashlib.sha256(before).hexdigest()
    expected = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
    assert report == expected
    for lang in ("en", "zh-TW"):
        pinned = (FIXTURES / f"expected.{lang}.md").read_text(encoding="utf-8")
        assert render(report, lang) + "\n" == pinned


def test_source_lines_survive_masking() -> None:
    text = ("<!-- one\ntwo\nthree -->\n```\ncode\n```\n---\n\nThe RCT ran.\n")
    assert findings(text) == [("body", 9, "undefined", "RCT")]
    lines = (FIXTURES / "manuscript.md").read_text(encoding="utf-8").split("\n")
    report = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
    for finding in report["findings"]:
        assert finding["acronym"] in lines[finding["line"] - 1], finding


def test_ordering_is_deterministic() -> None:
    text = ("## 摘要\n\nLLM。\n\n## Abstract\n\nThe SEM and the RCT.\n\n## Body\n\n"
            "ZZZ then AAA.\n")
    first = check(text, SCOPES, DEFAULT_ALLOWLIST)
    assert first == check(text, SCOPES, DEFAULT_ALLOWLIST)
    assert findings(text) == [("body", 11, "undefined", "AAA"), ("body", 11, "undefined", "ZZZ"),
                              ("abstract_en", 7, "undefined", "RCT"),
                              ("abstract_en", 7, "undefined", "SEM"),
                              ("abstract_zh", 3, "undefined", "LLM")]


def test_crlf_input_keeps_line_numbers(tmp_path: Path) -> None:
    path = _write(tmp_path, "m.md", b"First line.\r\n\r\nThe RCT ran.\r\n")
    report = build_report(path, "body", [], None)
    assert report["findings"][0]["line"] == 3
