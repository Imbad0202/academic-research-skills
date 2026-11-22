#!/usr/bin/env python3
"""Tests for scripts/check_manuscript_retractions.py (#1108).

Every fixture is synthetic and hermetic: the clients are fakes, so no test
reaches the network.
"""
from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from scripts import check_manuscript_retractions as cmr
from tests.test_helpers import run_script

SCRIPT = Path(cmr.__file__)

RETRACTED = "10.1000/retracted"
CLEAN = "10.1000/clean"
DATACITE = "10.5281/zenodo.1"
NOFLAG = "10.1000/noflag"
DOWN = "10.1000/down"
DISPUTED = "10.1000/disputed"


def _notice(kind: str = "retraction") -> dict:
    return {"DOI": "10.1000/notice", "type": kind, "updated": {"date-time": "2026-03-01T00:00:00Z"}}


class FakeOpenAlex:
    def __init__(self, table: dict):
        self.table, self.calls = table, []

    def _get(self, path, query):
        doi = path.removeprefix("/works/doi:").replace("%2F", "/")
        self.calls.append(doi)
        value = self.table.get(doi, {})
        if isinstance(value, Exception):
            raise value
        return value


class FakeCrossref:
    def __init__(self, table: dict):
        self.table, self.calls = table, []

    def _get(self, path, query):
        doi = path.removeprefix("/works/").replace("%2F", "/")
        self.calls.append(doi)
        value = self.table.get(doi)
        if isinstance(value, Exception):
            raise value
        return {"message": value} if value else {}


def make_clients(oa: dict, cr: dict):
    pair = (FakeOpenAlex(oa), FakeCrossref(cr))
    return pair, lambda: pair


OA = {
    RETRACTED: {"id": "W1", "is_retracted": True},
    CLEAN: {"id": "W2", "is_retracted": False},
    DATACITE: {"id": "W3", "is_retracted": False},
    NOFLAG: {"id": "W4", "title": "No flag here"},
    DOWN: cmr.OpenAlexUnavailable("down"),
    DISPUTED: {"id": "W6", "is_retracted": False},
}
CR = {
    RETRACTED: {"DOI": RETRACTED, "updated-by": [_notice()]},
    CLEAN: {"DOI": CLEAN},
    DOWN: cmr.CrossrefUnavailable("down"),
    DISPUTED: {"DOI": DISPUTED, "updated-by": [_notice()]},
}


def write_list(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "dois.txt"
    path.write_text(body, encoding="utf-8")
    return path


def report_for(tmp_path: Path, body: str, oa=OA, cr=CR):
    pair, factory = make_clients(oa, cr)
    return cmr.build_report(write_list(tmp_path, body), factory), pair


# --- list: extraction ------------------------------------------------------


def test_extract_dois_forms_lines_and_trailing_punctuation():
    text = (
        "See https://doi.org/10.1000/ABC.1, and (doi:10.1000/x(1)) here.\n"
        "Again 10.1000/abc.1; also [10.2000/y].\n"
        "no doi on this line\n"
    )
    assert cmr.extract_dois(text) == [
        ("10.1000/abc.1", [1, 2]),
        ("10.1000/x(1)", [1]),
        ("10.2000/y", [2]),
    ]


def test_list_writes_dois_with_manuscript_lines_and_sends_nothing(tmp_path, monkeypatch):
    def no_network(*a, **k):
        raise AssertionError("list must not touch the network")

    monkeypatch.setattr("urllib.request.urlopen", no_network)
    monkeypatch.setattr(cmr, "OpenAlexClient", no_network)
    monkeypatch.setattr(cmr, "CrossrefClient", no_network)
    manuscript = tmp_path / "m.md"
    manuscript.write_text("intro\nCite 10.1000/a and 10.1000/b.\nLater 10.1000/a.\n", encoding="utf-8")
    out = tmp_path / "list.txt"
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 0
    entries, invalid = cmr.parse_list(out.read_text(encoding="utf-8"))
    assert invalid == []
    assert [(e["doi"], e["locations"]) for e in entries] == [
        ("10.1000/a", ["lines 2, 3"]),
        ("10.1000/b", ["lines 2"]),
    ]


def test_list_with_no_dois_still_writes_a_commented_file(tmp_path):
    manuscript = tmp_path / "m.md"
    manuscript.write_text("nothing cited\n", encoding="utf-8")
    out = tmp_path / "list.txt"
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 0
    assert cmr.parse_list(out.read_text(encoding="utf-8")) == ([], [])


# --- list: destination checks and the write path --------------------------


def test_existing_output_is_refused_before_the_manuscript_is_read(tmp_path, capsys):
    out = tmp_path / "list.txt"
    out.write_text("keep me", encoding="utf-8")
    missing = tmp_path / "no-such-manuscript.md"
    assert cmr.main(["list", "--manuscript", str(missing), "--out", str(out)]) == 2
    err = capsys.readouterr().err
    assert "output file already exists" in err and "cannot read manuscript" not in err
    assert out.read_text(encoding="utf-8") == "keep me"


def test_missing_output_folder_is_refused_before_the_manuscript_is_read(tmp_path, capsys):
    out = tmp_path / "no-such-folder" / "list.txt"
    missing = tmp_path / "no-such-manuscript.md"
    assert cmr.main(["list", "--manuscript", str(missing), "--out", str(out)]) == 2
    err = capsys.readouterr().err
    assert "cannot create output file" in err and "cannot read manuscript" not in err


def test_output_that_is_a_directory_is_refused(tmp_path, capsys):
    assert cmr.main(["list", "--manuscript", str(tmp_path / "m.md"), "--out", str(tmp_path)]) == 2
    err = capsys.readouterr().err
    assert err.startswith("STOP: ") and "cannot read manuscript" not in err


def test_unreadable_manuscript_stops_and_removes_the_new_output(tmp_path, capsys):
    out = tmp_path / "list.txt"
    assert cmr.main(["list", "--manuscript", str(tmp_path / "gone.md"), "--out", str(out)]) == 2
    assert "cannot read manuscript" in capsys.readouterr().err
    assert not out.exists()


def test_non_utf8_manuscript_stops_and_removes_the_new_output(tmp_path, capsys):
    manuscript = tmp_path / "m.bin"
    manuscript.write_bytes(bytes([0xFF, 0xFE, 0x00]) + b" 10.1000/a")
    out = tmp_path / "list.txt"
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 2
    assert "cannot read manuscript" in capsys.readouterr().err
    assert not out.exists()


def test_existing_output_is_never_opened_for_writing(tmp_path, monkeypatch):
    out = tmp_path / "list.txt"
    out.write_text("keep me", encoding="utf-8")
    modes = []
    real_open = builtins.open
    monkeypatch.setattr(cmr, "open", lambda f, mode="r", *a, **k: (modes.append(mode), real_open(f, mode, *a, **k))[1], raising=False)
    with pytest.raises(cmr.Stop):
        cmr.run_list(tmp_path / "m.md", out)
    assert modes == ["x"]
    assert out.read_text(encoding="utf-8") == "keep me"


class _FailingHandle:
    def __init__(self, handle, error):
        self._handle, self._error = handle, error

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._handle.close()
        return False

    def write(self, content):
        self._handle.write(content[:5])  # a partial file is on disk when the error hits
        raise self._error


def test_interrupted_write_removes_only_the_new_partial_file_and_reraises(tmp_path, monkeypatch):
    manuscript = tmp_path / "m.md"
    manuscript.write_text("10.1000/a\n", encoding="utf-8")
    bystander = tmp_path / "other.txt"
    bystander.write_text("untouched", encoding="utf-8")
    out = tmp_path / "list.txt"
    real_open = builtins.open
    monkeypatch.setattr(
        cmr, "open", lambda *a, **k: _FailingHandle(real_open(*a, **k), KeyboardInterrupt()), raising=False
    )
    with pytest.raises(KeyboardInterrupt):
        cmr.run_list(manuscript, out)
    assert not out.exists()
    assert bystander.read_text(encoding="utf-8") == "untouched"


def test_oserror_during_write_becomes_stop_and_removes_the_file(tmp_path, monkeypatch, capsys):
    manuscript = tmp_path / "m.md"
    manuscript.write_text("10.1000/a\n", encoding="utf-8")
    out = tmp_path / "list.txt"
    real_open = builtins.open
    monkeypatch.setattr(
        cmr, "open", lambda *a, **k: _FailingHandle(real_open(*a, **k), OSError("disk full")), raising=False
    )
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 2
    assert "disk full" in capsys.readouterr().err
    assert not out.exists()


def test_cli_list_end_to_end_and_second_run_refuses(tmp_path):
    manuscript = tmp_path / "m.md"
    manuscript.write_text("A 10.1000/a.\n", encoding="utf-8")
    out = tmp_path / "list.txt"
    first = run_script(SCRIPT, "list", "--manuscript", str(manuscript), "--out", str(out))
    assert first.returncode == 0, first.stderr
    again = run_script(SCRIPT, "list", "--manuscript", str(manuscript), "--out", str(out))
    assert again.returncode == 2 and again.stderr.startswith("STOP: ")


# --- check: parsing --------------------------------------------------------


def test_parse_list_ignores_comments_and_blanks_and_counts_other_lines():
    entries, invalid = cmr.parse_list(
        "# comment\n\n   \n10.1000/a\tlines 3\n10.1000/a  Section 2\nnot a doi\n  # indented comment\n"
        "https://doi.org/10.1000/B\n"
    )
    assert [(e["doi"], e["locations"]) for e in entries] == [
        ("10.1000/a", ["lines 3", "Section 2"]),
        ("10.1000/b", []),
    ]
    assert invalid == [(6, "not a doi")]


# --- check: lookups and verdicts ------------------------------------------


def test_only_dois_left_in_the_edited_list_are_looked_up(tmp_path):
    report, (oa, cr) = report_for(tmp_path, f"{CLEAN}\tlines 2\n# {RETRACTED}\n")
    assert oa.calls == [CLEAN] and cr.calls == [CLEAN]
    assert [i["doi"] for i in report["items"]] == [CLEAN]


def test_retracted_hit_names_the_manuscript_location(tmp_path):
    report, _ = report_for(tmp_path, f"{RETRACTED}\tlines 12, 45\n")
    text = cmr.render(report)
    assert report["items"][0]["status"] == "retracted"
    assert f"`{RETRACTED}` (lines 12, 45)" in text and "2026-03-01" in text
    assert "does not decide the effect" in text


def test_openalex_only_dois_are_listed_with_locations_and_not_hidden_as_clean(tmp_path):
    report, _ = report_for(tmp_path, f"{DATACITE}\tlines 7\n{CLEAN}\tlines 8\n")
    items = {i["doi"]: i for i in report["items"]}
    assert items[DATACITE]["openalex_only"] and items[DATACITE]["status"] == "not_retracted"
    assert not items[CLEAN]["openalex_only"]
    text = cmr.render(report)
    heading = [ln for ln in text.splitlines() if ln.startswith("OpenAlex-only verdicts")]
    assert heading and "1 DOI(s)" in heading[0]
    assert f"- `{DATACITE}` (lines 7): OpenAlex not retracted; Crossref unknown (no record)." in text
    assert CLEAN not in text.split("OpenAlex-only verdicts")[1]


def test_unknown_stays_unknown_and_makes_coverage_partial(tmp_path):
    report, _ = report_for(tmp_path, f"{NOFLAG}\tlines 3\n{DOWN}\tlines 4\n{CLEAN}\n")
    items = {i["doi"]: i for i in report["items"]}
    assert items[NOFLAG]["status"] == "unknown" and items[DOWN]["status"] == "unknown"
    assert items[CLEAN]["status"] == "not_retracted"
    assert report["state"] == "partial"
    text = cmr.render(report)
    assert "(partial)" in text and "unknown: 2" in text
    assert "flag missing" in text and "unavailable" in text
    assert "not \"not retracted\"" in text


def test_a_doi_neither_index_knows_is_unknown_not_clean(tmp_path):
    report, _ = report_for(tmp_path, "10.9999/nowhere\tlines 1\n")
    assert report["items"][0]["status"] == "unknown"
    assert report["items"][0]["openalex"]["detail"] == "no_record"
    assert report["items"][0]["openalex_only"] is False


def test_disagreeing_indexes_are_reported_as_disputed(tmp_path):
    report, _ = report_for(tmp_path, f"{DISPUTED}\tlines 9\n")
    assert report["items"][0]["status"] == "disputed"
    assert "Disputed" in cmr.render(report)


def test_invalid_list_lines_are_listed_and_make_coverage_partial(tmp_path):
    report, _ = report_for(tmp_path, f"{CLEAN}\nbroken line\n")
    assert report["state"] == "partial" and report["invalid"] == [(2, "broken line")]
    assert "list line 2: `broken line`" in cmr.render(report)


def test_empty_list_reports_nothing_checked_and_calls_no_client(tmp_path):
    def forbidden():
        raise AssertionError("no client should be built for an empty list")

    report = cmr.build_report(write_list(tmp_path, "# nothing left\n"), forbidden)
    text = cmr.render(report)
    assert report["items"] == [] and "No DOIs were listed to check." in text
    assert "References without a DOI are not checked." in text


def test_untrusted_location_text_is_escaped(tmp_path):
    report, _ = report_for(tmp_path, f"{RETRACTED}\t**bold** <b>x</b> [l](u) | `c`\n")
    text = cmr.render(report)
    assert "<b>" not in text and "\\*\\*bold\\*\\*" in text and "\\[l\\]" in text and "\\|" in text


def test_zh_tw_report_renders_the_same_sections(tmp_path):
    report, _ = report_for(tmp_path, f"{RETRACTED}\tlines 1\n{DATACITE}\tlines 2\n{NOFLAG}\n")
    text = cmr.render(report, "zh-TW")
    assert "已撤稿" in text and "僅依 OpenAlex 判定" in text and "狀態不明" in text
    assert "沒有 DOI 的參考文獻不在此查核範圍內。" in text


# --- check: CLI ------------------------------------------------------------


def test_unreadable_list_stops_with_exit_2(tmp_path, capsys):
    assert cmr.main(["check", "--list", str(tmp_path / "gone.txt")]) == 2
    assert capsys.readouterr().err.startswith("STOP: cannot read list file")


def test_non_utf8_list_stops_with_exit_2(tmp_path, capsys):
    bad = tmp_path / "bad.txt"
    bad.write_bytes(b"\xff\xfe\x00")
    assert cmr.main(["check", "--list", str(bad)]) == 2
    assert "STOP:" in capsys.readouterr().err


def test_check_prints_the_report_and_exits_zero(tmp_path, capsys):
    _, factory = make_clients(OA, CR)
    path = write_list(tmp_path, f"{RETRACTED}\tlines 4\n")
    assert cmr.main(["check", "--list", str(path), "--lang", "en"], clients=factory) == 0
    out = capsys.readouterr().out
    assert out.startswith(cmr._TEXT["en"]["title"]) and RETRACTED in out


def test_coverage_is_complete_only_when_every_doi_is_settled_and_every_line_read(tmp_path):
    settled, _ = report_for(tmp_path, f"{CLEAN}\tlines 1\n{RETRACTED}\tlines 2\n")
    assert settled["state"] == "checked"
    assert "(complete)" in cmr.render(settled)
    only_unknown, _ = report_for(tmp_path, f"{NOFLAG}\tlines 3\n")
    assert only_unknown["state"] == "partial"
