"""Hermetic tests for scripts/check_manuscript_retractions.py (#1108)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import check_manuscript_retractions as cmr  # noqa: E402
from crossref_client import CrossrefUnavailable  # noqa: E402
from openalex_client import OpenAlexUnavailable  # noqa: E402


class _FakeOA:
    def __init__(self, responses: dict[str, Any]) -> None:
        self._responses = responses
        self.calls: list[str] = []

    def _get(self, path: str, query: dict[str, str]) -> dict[str, Any]:
        self.calls.append(path)
        for doi, val in self._responses.items():
            if doi in path.lower() or doi.replace("/", "%2f") in path.lower():
                if isinstance(val, Exception):
                    raise val
                return val
        return {}


class _FakeCR:
    def __init__(self, responses: dict[str, Any]) -> None:
        self._responses = responses
        self.calls: list[str] = []

    def _get(self, path: str, query: dict[str, str]) -> dict[str, Any]:
        self.calls.append(path)
        for doi, val in self._responses.items():
            if doi in path.lower() or doi.replace("/", "%2f") in path.lower():
                if isinstance(val, Exception):
                    raise val
                return val
        return {}


def _oa_work(doi: str, is_retracted: Any) -> dict[str, Any]:
    rec: dict[str, Any] = {"id": f"https://openalex.org/W-{doi}", "doi": f"https://doi.org/{doi}"}
    if is_retracted is not _OMIT:
        rec["is_retracted"] = is_retracted
    return rec


_OMIT = object()


def _cr_work(doi: str, events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    msg: dict[str, Any] = {"DOI": doi, "title": ["Test Work"]}
    if events:
        msg["updated-by"] = events
    return {"message": msg}


def _retraction_event(date: str = "2025-04-10T00:00:00Z", kind: str = "retraction") -> dict[str, Any]:
    return {
        "DOI": "10.1234/retraction-notice.1",
        "type": kind,
        "source": "retraction-watch",
        "record-id": 101,
        "updated": {"date-time": date},
    }


def _factory(oa: dict[str, Any], cr: dict[str, Any]):
    oa_client = _FakeOA(oa)
    cr_client = _FakeCR(cr)
    return (lambda: (oa_client, cr_client)), oa_client, cr_client


# ---------------------------------------------------------------------------
# Step 1: list
# ---------------------------------------------------------------------------


def test_list_extracts_normalized_unique_dois_with_line_numbers_and_sends_nothing(tmp_path: Path, capsys) -> None:
    ms = tmp_path / "paper.md"
    ms.write_text(
        "Intro cites https://doi.org/10.1234/Alpha.1.\n"
        "Also doi:10.1234/alpha.1 and (10.1002/(SICI)1097-0142(1998)1.0).\n"
        "Preprint 10.48550/arXiv.2401.12345; and repeat 10.1234/ALPHA.1\n",
        encoding="utf-8",
    )
    out = tmp_path / "dois.txt"
    rc = cmr.main(["list", "--manuscript", str(ms), "--out", str(out)])
    assert rc == 0
    assert "Wrote 3 DOI(s)" in capsys.readouterr().out
    content = out.read_text(encoding="utf-8")
    data_lines = [ln for ln in content.splitlines() if ln and not ln.startswith("#")]
    assert data_lines == [
        "10.1234/alpha.1\tlines 1, 2, 3",
        "10.1002/(sici)1097-0142(1998)1.0\tlines 2",
        "10.48550/arxiv.2401.12345\tlines 3",
    ]


def test_list_refuses_existing_output_before_reading_manuscript(tmp_path: Path, capsys) -> None:
    missing_ms = tmp_path / "does_not_exist.md"
    existing_out = tmp_path / "existing.txt"
    existing_out.write_text("keep me\n", encoding="utf-8")
    rc = cmr.main(["list", "--manuscript", str(missing_ms), "--out", str(existing_out)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "STOP:" in err
    assert "already exists" in err
    assert "cannot read manuscript" not in err
    assert existing_out.read_text(encoding="utf-8") == "keep me\n"


def test_list_permission_error_stops_before_reading_manuscript(tmp_path: Path, monkeypatch, capsys) -> None:
    missing_ms = tmp_path / "does_not_exist.md"
    out = tmp_path / "locked.txt"

    def _boom(path, *args, **kwargs):
        if Path(path) == out:
            raise PermissionError("access denied")
        return os.lstat(path)

    monkeypatch.setattr(cmr.os, "lstat", _boom)
    rc = cmr.main(["list", "--manuscript", str(missing_ms), "--out", str(out)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "STOP:" in err
    assert "cannot check output path" in err
    assert "cannot read manuscript" not in err
    assert "no doi" not in err.lower()


def test_list_interrupt_during_write_leaves_no_partial_file(tmp_path: Path, monkeypatch) -> None:
    ms = tmp_path / "paper.md"
    ms.write_text("See 10.1234/example.1\n", encoding="utf-8")
    out = tmp_path / "dois.txt"

    def _interrupt(_fd):
        raise KeyboardInterrupt()

    monkeypatch.setattr(cmr.os, "fsync", _interrupt)
    with pytest.raises(KeyboardInterrupt):
        cmr.run_list(ms, out)
    assert not out.exists()
    leftovers = list(tmp_path.glob(".ars-retraction-list-*.tmp"))
    assert leftovers == []


# ---------------------------------------------------------------------------
# Step 2: parsing & 9-digit line-number limit
# ---------------------------------------------------------------------------


def test_list_and_check_9_digit_line_number_limit() -> None:
    text = (
        "# comment\n"
        "10.1234/ok.1\tlines 1, 999999999\n"
        "10.1234/too-big.1\tlines 1000000000\n"
        "10.1234/zero.1\tlines 0\n"
        "10.1234/freeform.1\tSection 2, Claim 1\n"
    )
    items, invalid = cmr.parse_list_text(text)
    assert [i["doi"] for i in items] == ["10.1234/ok.1", "10.1234/freeform.1"]
    assert items[0]["locations"] == ["lines 1, 999999999"]
    assert items[1]["locations"] == ["Section 2, Claim 1"]
    assert [(e["line"], e["reason"]) for e in invalid] == [
        (3, "invalid_line_number"),
        (4, "invalid_line_number"),
    ]


def test_comment_and_blank_lines_ignored_while_invalid_lines_counted(tmp_path: Path) -> None:
    lst = tmp_path / "dois.txt"
    lst.write_text(
        "\n"
        "# top comment\n"
        "   # indented comment\n"
        "10.1234/clean.1\tlines 4\n"
        "Smith (2020) without a DOI\n"
        "   \n",
        encoding="utf-8",
    )
    fac, _, _ = _factory(
        {"10.1234/clean.1": _oa_work("10.1234/clean.1", False)},
        {"10.1234/clean.1": _cr_work("10.1234/clean.1")},
    )
    report = cmr.build_report(lst, fac)
    assert report["status"] == "partial"
    assert len(report["items"]) == 1
    assert len(report["invalid_lines"]) == 1
    assert report["invalid_lines"][0]["line"] == 5
    assert report["invalid_lines"][0]["reason"] == "invalid_doi"
    md = cmr.render(report, "en")
    assert "blank lines and `#` comments are ignored; every other line is counted" in md
    assert "line 5: not a valid DOI" in md


# ---------------------------------------------------------------------------
# Step 2: verdicts, OpenAlex-only listing, unknown, degraded
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lang", ["en", "zh-TW"])
def test_retracted_hit_names_manuscript_location_and_both_langs(tmp_path: Path, lang: str) -> None:
    lst = tmp_path / "dois.txt"
    lst.write_text("10.1234/retracted.1\tSection 3, lines 42, 88\n", encoding="utf-8")
    fac, oa_client, cr_client = _factory(
        {"10.1234/retracted.1": _oa_work("10.1234/retracted.1", True)},
        {"10.1234/retracted.1": _cr_work("10.1234/retracted.1", [_retraction_event()])},
    )
    report = cmr.build_report(lst, fac)
    assert report["status"] == "checked"
    assert len(oa_client.calls) == 1 and len(cr_client.calls) == 1
    assert report["items"][0]["effective_status"] == "retracted"
    md = cmr.render(report, lang)
    assert "10.1234/retracted.1" in md
    assert "Section 3, lines 42, 88" in md
    assert "2025-04-10T00:00:00Z" in md


def test_disputed_and_reinstated_verdicts(tmp_path: Path) -> None:
    lst = tmp_path / "dois.txt"
    lst.write_text(
        "10.1234/disputed.1\tlines 10\n"
        "10.1234/reinstated.1\tlines 20\n",
        encoding="utf-8",
    )
    fac, _, _ = _factory(
        {
            "10.1234/disputed.1": _oa_work("10.1234/disputed.1", True),
            "10.1234/reinstated.1": _oa_work("10.1234/reinstated.1", False),
        },
        {
            "10.1234/disputed.1": _cr_work("10.1234/disputed.1"),
            "10.1234/reinstated.1": _cr_work(
                "10.1234/reinstated.1",
                [
                    _retraction_event("2024-01-01T00:00:00Z", "retraction"),
                    _retraction_event("2025-01-01T00:00:00Z", "reinstatement"),
                ],
            ),
        },
    )
    report = cmr.build_report(lst, fac)
    assert report["status"] == "checked"
    statuses = {i["doi"]: i["effective_status"] for i in report["items"]}
    assert statuses == {"10.1234/disputed.1": "disputed", "10.1234/reinstated.1": "reinstated"}
    md = cmr.render(report, "en")
    assert "Disputed DOIs" in md
    assert "Reinstated DOIs" in md


def test_unknown_missing_flag_stays_unknown_and_partial(tmp_path: Path) -> None:
    lst = tmp_path / "dois.txt"
    lst.write_text("10.1234/missing-flag.1\tlines 7\n", encoding="utf-8")
    fac, _, _ = _factory(
        {"10.1234/missing-flag.1": _oa_work("10.1234/missing-flag.1", _OMIT)},
        {},  # Crossref 404
    )
    report = cmr.build_report(lst, fac)
    assert report["status"] == "partial"
    item = report["items"][0]
    assert item["effective_status"] == "unknown"
    assert item["openalex_only_no_crossref"] is False
    md = cmr.render(report, "en")
    assert "Unknown status" in md
    assert "10.1234/missing-flag.1" in md
    assert "flag missing" in md


def test_crossref_no_record_with_openalex_verdict_lists_every_such_doi(tmp_path: Path) -> None:
    lst = tmp_path / "dois.txt"
    lst.write_text(
        "10.48550/arxiv.2401.00001\tlines 5\n"
        "10.9999/unregistered.1\tlines 9\n"
        "10.9999/both-missing.1\tlines 12\n",
        encoding="utf-8",
    )
    fac, _, _ = _factory(
        {
            "10.48550/arxiv.2401.00001": _oa_work("10.48550/arxiv.2401.00001", False),
            "10.9999/unregistered.1": _oa_work("10.9999/unregistered.1", False),
        },
        {},  # Crossref 404 for all three
    )
    report = cmr.build_report(lst, fac)
    by_doi = {i["doi"]: i for i in report["items"]}
    assert by_doi["10.48550/arxiv.2401.00001"]["openalex_only_no_crossref"] is True
    assert by_doi["10.9999/unregistered.1"]["openalex_only_no_crossref"] is True
    assert by_doi["10.9999/both-missing.1"]["openalex_only_no_crossref"] is False
    assert by_doi["10.9999/both-missing.1"]["effective_status"] == "unknown"

    md = cmr.render(report, "en")
    assert "OpenAlex-only verdicts" in md
    assert "2 DOI(s)" in md
    assert "10.48550/arxiv.2401.00001" in md
    assert "10.9999/unregistered.1" in md
    assert "Unknown status" in md
    assert "10.9999/both-missing.1" in md


def test_degraded_resolver_makes_report_partial(tmp_path: Path) -> None:
    lst = tmp_path / "dois.txt"
    lst.write_text("10.1234/one-down.1\tlines 3\n", encoding="utf-8")
    fac, _, _ = _factory(
        {"10.1234/one-down.1": OpenAlexUnavailable("timeout")},
        {"10.1234/one-down.1": _cr_work("10.1234/one-down.1")},
    )
    report = cmr.build_report(lst, fac)
    assert report["status"] == "partial"
    assert report["items"][0]["effective_status"] == "not_retracted"
    assert report["items"][0]["openalex"]["detail"] == "degraded"
    md = cmr.render(report, "en")
    assert "Single-resolver verdicts" in md
    assert "unavailable/degraded" in md


def test_check_unreadable_list_returns_exit_2_and_not_checked(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.txt"
    rc = cmr.main(["check", "--list", str(missing)])
    assert rc == 2
    captured = capsys.readouterr()
    assert "STOP:" in captured.err
    assert "Not checked:" in captured.out


def test_check_empty_list_notes_references_without_doi_not_checked(tmp_path: Path, capsys) -> None:
    lst = tmp_path / "empty.txt"
    lst.write_text("# header only\n\n", encoding="utf-8")
    fac, oa_client, cr_client = _factory({}, {})
    rc = cmr.main(["check", "--list", str(lst)], clients_factory=fac)
    assert rc == 0
    assert oa_client.calls == [] and cr_client.calls == []
    out = capsys.readouterr().out
    assert "No DOIs were listed to check" in out
    assert "References without a DOI are not checked" in out


def test_markdown_escaping_and_json_out(tmp_path: Path, capsys) -> None:
    lst = tmp_path / "dois.txt"
    lst.write_text("10.1234/retracted.1\t<h2>Forged</h2> *bold* [link](u)\n", encoding="utf-8")
    json_out = tmp_path / "out.json"
    fac, _, _ = _factory(
        {"10.1234/retracted.1": _oa_work("10.1234/retracted.1", True)},
        {"10.1234/retracted.1": _cr_work("10.1234/retracted.1", [_retraction_event()])},
    )
    rc = cmr.main(["check", "--list", str(lst), "--json-out", str(json_out)], clients_factory=fac)
    assert rc == 0
    out = capsys.readouterr().out
    assert "&lt;h2&gt;Forged&lt;/h2&gt;" in out
    assert r"\*bold\*" in out
    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["checker"] == cmr.CHECKER
    assert data["status"] == "checked"


# ---------------------------------------------------------------------------
# Reviewer Editorial Decision Letter attachment integration
# ---------------------------------------------------------------------------

ATTACHMENT_HEADING = "## Attachment: Retraction Check (advisory, #1108)"
ACRONYM_HEADING = "## Attachment: Acronym Check (advisory, #849)"
DECISION_TEMPLATE = REPO_ROOT / "academic-paper-reviewer" / "templates" / "editorial_decision_template.md"


def _attachment(tmp_path: Path, lang: str) -> str:
    lst = tmp_path / f"dois_{lang}.txt"
    lst.write_text("10.1234/retracted.1\tlines 12\n", encoding="utf-8")
    fac, _, _ = _factory(
        {"10.1234/retracted.1": _oa_work("10.1234/retracted.1", True)},
        {"10.1234/retracted.1": _cr_work("10.1234/retracted.1", [_retraction_event()])},
    )
    report = cmr.build_report(lst, fac)
    return f"\n---\n\n{ATTACHMENT_HEADING}\n\n{cmr.render(report, lang)}"


@pytest.mark.parametrize("lang", ["en", "zh-TW"])
def test_the_attachment_leaves_the_panel_decision_unchanged(tmp_path: Path, lang: str) -> None:
    from scripts import check_panel_synthesis as cps
    from scripts.test_check_panel_synthesis import FULL, reports, synthesis_for

    panel = reports()
    synthesis, expressions = synthesis_for(panel)
    parsed = cps.parse_synthesis("s.md", synthesis + "\n" + _attachment(tmp_path, lang), FULL)
    assert parsed == cps.parse_synthesis("s.md", synthesis, FULL)
    assert cps.layer2_check(panel, FULL, expressions, parsed, []) == []


def test_the_attachment_leaves_the_re_review_letter_extraction_unchanged(tmp_path: Path) -> None:
    from scripts.check_re_review_synthesis import parse_letter_blocks

    letter = (
        "# Editorial Decision\n\n## Required Revisions * (Must Fix)\n\n"
        "### Required Item Details\n\n"
        "**R1: Sample size justification**\n"
        "- **Acceptance criteria**: A formal power analysis appears in Methods §3.2.\n"
    )
    blocks = parse_letter_blocks(letter)
    assert [rid for rid, _ in blocks] == ["R1"]
    for lang in ("en", "zh-TW"):
        assert parse_letter_blocks(letter + _attachment(tmp_path, lang)) == blocks


def test_the_template_puts_retraction_check_between_claim_check_and_acronym_check() -> None:
    text = DECISION_TEMPLATE.read_text(encoding="utf-8")
    start = text.index("```markdown\n")
    letter = text[start:text.index("\n```\n", start)]
    headings = [line for line in letter.split("\n") if line.startswith("## ")]
    assert headings[-4:] == [
        "## Attachment: Suggested-Reference Check (advisory, #1001)",
        "## Attachment: Reviewer Claim Check (advisory, #1002)",
        ATTACHMENT_HEADING,
        ACRONYM_HEADING,
    ]
    skill = (REPO_ROOT / "academic-paper-reviewer" / "SKILL.md").read_text(encoding="utf-8")
    assert f"`{ATTACHMENT_HEADING}`" in skill
    assert "before the acronym check attachment, which stays the letter's last write" in skill
