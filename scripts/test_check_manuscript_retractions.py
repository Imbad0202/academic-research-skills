#!/usr/bin/env python3
"""Tests for scripts/check_manuscript_retractions.py (#1108).

Every fixture is synthetic and hermetic: the clients are fakes, so no test
reaches the network.
"""
from __future__ import annotations

import os
import sys
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
CRDOWN = "10.1000/crdown"
OADOWN = "10.1000/oadown"
SPLIT = "10.1000/split"
UNDERSCORE = "10.1007/978-3-030-58529-7_15"


def _notice(kind: str = "retraction") -> dict:
    return {"DOI": "10.1000/notice", "type": kind, "updated": {"date-time": "2026-03-01T00:00:00Z"}}


class FakeOpenAlex:
    def __init__(self, table: dict):
        self.table, self.calls, self.requests = table, [], []

    def _get(self, path, query):
        self.requests.append((path, dict(query)))  # the exact path and query that would be sent
        doi = path.removeprefix("/works/doi:").replace("%2F", "/")
        self.calls.append(doi)
        value = self.table.get(doi, {})
        if isinstance(value, Exception):
            raise value
        return value


class FakeCrossref:
    def __init__(self, table: dict):
        self.table, self.calls, self.requests = table, [], []

    def _get(self, path, query):
        self.requests.append((path, dict(query)))
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
    CRDOWN: {"id": "W7", "is_retracted": False},
    OADOWN: cmr.OpenAlexUnavailable("down"),
    SPLIT: {"id": "W8", "is_retracted": False},
    UNDERSCORE: {"id": "W9", "is_retracted": False},
}
CR = {
    RETRACTED: {"DOI": RETRACTED, "updated-by": [_notice()]},
    CLEAN: {"DOI": CLEAN},
    DOWN: cmr.CrossrefUnavailable("down"),
    DISPUTED: {"DOI": DISPUTED, "updated-by": [_notice()]},
    CRDOWN: cmr.CrossrefUnavailable("down"),
    OADOWN: {"DOI": OADOWN},
    SPLIT: {"DOI": SPLIT, "updated-by": [{"DOI": "10.1000/n1", "type": "retraction"}, {"DOI": "10.1000/n2", "type": "reinstatement"}]},
    UNDERSCORE: {"DOI": UNDERSCORE},
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


def test_extraction_stops_at_cjk_punctuation_and_at_a_url_fragment_or_query():
    text = (
        "見 10.1000/a。另見下節\n"
        "https://doi.org/10.1000/b#abstract\n"
        "https://doi.org/10.1000/c?utm_source=x\n"
        "（10.1000/d）與 10.1000/e、次\n"
        "10.1000/f另見\n"
        "bare 10.1000/g#keep\n"
    )
    assert [d for d, _ in cmr.extract_dois(text)] == [
        "10.1000/a", "10.1000/b", "10.1000/c", "10.1000/d", "10.1000/e", "10.1000/f", "10.1000/g#keep",
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
    opens = []
    real_os_open = os.open
    monkeypatch.setattr(cmr.os, "open", lambda path, flags, mode=0o777: (opens.append((flags, mode)), real_os_open(path, flags, mode))[1])
    with pytest.raises(cmr.Stop):
        cmr.run_list(tmp_path / "m.md", out)
    assert len(opens) == 1 and opens[0][0] & os.O_EXCL and not opens[0][0] & os.O_TRUNC
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
    real_new = cmr._open_new
    monkeypatch.setattr(cmr, "_open_new", lambda out: _FailingHandle(real_new(out), KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        cmr.run_list(manuscript, out)
    assert not out.exists()
    assert bystander.read_text(encoding="utf-8") == "untouched"


def test_oserror_during_write_becomes_stop_and_removes_the_file(tmp_path, monkeypatch, capsys):
    manuscript = tmp_path / "m.md"
    manuscript.write_text("10.1000/a\n", encoding="utf-8")
    out = tmp_path / "list.txt"
    real_new = cmr._open_new
    monkeypatch.setattr(cmr, "_open_new", lambda out: _FailingHandle(real_new(out), OSError("disk full")))
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
    assert invalid == [6]


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
    assert report["state"] == "partial" and report["invalid"] == [2]
    text = cmr.render(report)
    assert "list line 2" in text and "broken line" not in text


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


# --- list: cleanup reporting ----------------------------------------------


class _CloseFails(_FailingHandle):
    """Write works; closing the handle (the final flush) fails with an OSError."""

    def __exit__(self, *exc):
        self._handle.close()
        raise self._error

    def write(self, content):
        self._handle.write(content)


def _list_inputs(tmp_path):
    manuscript = tmp_path / "m.md"
    manuscript.write_text("10.1000/a\n", encoding="utf-8")
    return manuscript, tmp_path / "list.txt"


def test_close_failure_removes_the_new_file_and_says_so(tmp_path, monkeypatch, capsys):
    manuscript, out = _list_inputs(tmp_path)
    real_new = cmr._open_new
    monkeypatch.setattr(cmr, "_open_new", lambda out: _CloseFails(real_new(out), OSError("flush failed")))
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 2
    err = capsys.readouterr().err
    assert "flush failed" in err and "the new output file was removed" in err
    assert not out.exists()


def test_cleanup_success_is_reported_for_a_manuscript_read_failure(tmp_path, capsys):
    out = tmp_path / "list.txt"
    assert cmr.main(["list", "--manuscript", str(tmp_path / "gone.md"), "--out", str(out)]) == 2
    err = capsys.readouterr().err
    assert "cannot read manuscript" in err and "the new output file was removed" in err
    assert not out.exists()


def test_failed_cleanup_names_the_remaining_file_and_keeps_the_original_error(tmp_path, monkeypatch, capsys):
    manuscript, out = _list_inputs(tmp_path)
    real_new = cmr._open_new
    monkeypatch.setattr(cmr, "_open_new", lambda out: _FailingHandle(real_new(out), OSError("disk full")))

    def deny(path):
        raise PermissionError("locked by another process")

    monkeypatch.setattr(cmr.os, "unlink", deny)
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 2
    err = capsys.readouterr().err
    assert "disk full" in err  # the original error is kept
    assert "could not be removed and remains at" in err and str(out) in err and "locked by another process" in err
    assert "was removed" not in err
    assert out.exists()  # the partial file really is still there


def test_failed_cleanup_after_an_interrupt_reports_the_remaining_file_and_reraises(tmp_path, monkeypatch, capsys):
    manuscript, out = _list_inputs(tmp_path)
    real_new = cmr._open_new
    monkeypatch.setattr(cmr, "_open_new", lambda out: _FailingHandle(real_new(out), KeyboardInterrupt()))

    def deny(path):
        raise PermissionError("locked")

    monkeypatch.setattr(cmr.os, "unlink", deny)
    with pytest.raises(KeyboardInterrupt):
        cmr.run_list(manuscript, out)
    assert f"remains at {out}" in capsys.readouterr().err


def test_cleanup_never_touches_a_pre_existing_file_when_the_open_is_refused(tmp_path, monkeypatch, capsys):
    out = tmp_path / "list.txt"
    out.write_text("keep me", encoding="utf-8")
    calls = []
    monkeypatch.setattr(cmr.os, "unlink", lambda path: calls.append(path))
    assert cmr.main(["list", "--manuscript", str(tmp_path / "m.md"), "--out", str(out)]) == 2
    assert calls == [] and out.read_text(encoding="utf-8") == "keep me"


# --- check: record shape and stale date -----------------------------------


@pytest.mark.parametrize("message", [{}, "junk", ["x"], None])
def test_an_unreadable_crossref_message_is_degraded_not_no_record(message):
    class Client:
        def _get(self, path, query):
            return {"message": message}

    envelope, detail = cmr._crossref(Client(), "10.1000/x")
    assert detail == "degraded" and envelope == {"status": "degraded"}


@pytest.mark.parametrize("body", [["x"], "junk", 7])
def test_a_non_object_body_is_degraded_for_both_indexes(body):
    class Client:
        def _get(self, path, query):
            return body

    assert cmr._crossref(Client(), "10.1000/x")[1] == "degraded"
    assert cmr._openalex(Client(), "10.1000/x")[1] == "degraded"


def test_an_empty_body_from_a_404_is_still_no_record():
    class Client:
        def _get(self, path, query):
            return {}

    assert cmr._crossref(Client(), "10.1000/x") == ({"status": "checked", "records": []}, "no_record")
    assert cmr._openalex(Client(), "10.1000/x") == ({"status": "checked", "record": {}}, "no_record")


def test_stale_after_is_the_revalidation_window_after_the_check_time(tmp_path, monkeypatch):
    seen = {}
    real = cmr.resolve_retraction_signal

    def spy(entry, **kwargs):
        seen.update(checked_at=kwargs["checked_at"], stale_after=kwargs["stale_after"])
        return real(entry, **kwargs)

    monkeypatch.setattr(cmr, "resolve_retraction_signal", spy)
    _, factory = make_clients(OA, CR)
    now = cmr.datetime(2026, 1, 1, tzinfo=cmr.timezone.utc)
    cmr.build_report(write_list(tmp_path, f"{CLEAN}\n"), factory, now=now)
    expected = now + cmr.timedelta(days=cmr.CACHE_REVALIDATE_DAYS)
    assert seen["checked_at"] == "2026-01-01T00:00:00Z"
    assert seen["stale_after"] == expected.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert seen["stale_after"] > seen["checked_at"]


# --- maintainer review of 5f436a78 (items 1-12) ---------------------------


def test_only_the_doi_field_is_sent_never_the_note(tmp_path):
    body = f"{CLEAN} Section 2\tp. 4\n{DATACITE}\tSection 3 10.9999/other\n"
    report, (oa, cr) = report_for(tmp_path, body)
    select = {"select": cmr._OA_FIELDS}
    assert oa.requests == [("/works/doi:10.1000%2Fclean", select), ("/works/doi:10.5281%2Fzenodo.1", select)]
    assert cr.requests == [("/works/10.1000%2Fclean", {}), ("/works/10.5281%2Fzenodo.1", {})]
    assert [i["locations"] for i in report["items"]] == [["Section 2\tp. 4"], ["Section 3 10.9999/other"]]


def test_parse_list_splits_on_the_first_whitespace_run_and_checks_the_whole_doi_field():
    entries, invalid = cmr.parse_list("10.1000/a Section 2\tp. 4\n10.1000/b\t\t note\n10.1000/c<x note\n")
    assert [(e["doi"], e["locations"]) for e in entries] == [
        ("10.1000/a", ["Section 2\tp. 4"]),
        ("10.1000/b", ["note"]),
    ]
    assert invalid == [3]


def test_a_list_saved_with_a_byte_order_mark_is_read_from_its_first_line():
    assert cmr.parse_list("\ufeff# comment\n10.1000/a\n") == ([{"doi": "10.1000/a", "locations": []}], [])
    assert cmr.parse_list("\ufeff10.1000/a\tlines 1\n")[0] == [{"doi": "10.1000/a", "locations": ["lines 1"]}]


def test_a_bom_list_file_is_checked_from_the_first_line(tmp_path):
    path = tmp_path / "bom.txt"
    path.write_bytes("\ufeff10.1000/clean\n".encode("utf-8"))
    _, factory = make_clients(OA, CR)
    report = cmr.build_report(path, factory)
    assert [i["doi"] for i in report["items"]] == [CLEAN] and report["invalid"] == []


def test_manuscript_and_output_may_not_be_the_same_path(tmp_path, capsys):
    same = tmp_path / "same.md"
    assert cmr.main(["list", "--manuscript", str(same), "--out", str(same)]) == 2
    assert "same path" in capsys.readouterr().err and not same.exists()
    same.write_text("10.1000/a\n", encoding="utf-8")
    assert cmr.main(["list", "--manuscript", str(same), "--out", str(tmp_path / "." / "same.md")]) == 2
    assert same.read_text(encoding="utf-8") == "10.1000/a\n"


def test_a_failed_source_makes_the_run_partial_and_the_row_names_it(tmp_path):
    report, _ = report_for(tmp_path, f"{CRDOWN}\tlines 5\n{OADOWN}\tlines 6\n{CLEAN}\n")
    items = {i["doi"]: i for i in report["items"]}
    assert items[CRDOWN]["status"] == "not_retracted" and items[OADOWN]["status"] == "not_retracted"
    assert report["state"] == "partial"
    text = cmr.render(report)
    assert "(partial)" in text and "One index could not be read" in text and "2 DOI(s)" in text
    assert f"`{CRDOWN}` (lines 5): OpenAlex not retracted; Crossref unknown (unavailable or unreadable)." in text
    assert f"`{OADOWN}` (lines 6): OpenAlex unknown (unavailable or unreadable); Crossref not retracted." in text
    assert f"`{CLEAN}`" not in text


def test_a_retracted_doi_with_a_failed_source_stays_retracted_and_partial(tmp_path):
    oa = {**OA, RETRACTED: {"id": "W1", "is_retracted": True}}
    cr = {**CR, RETRACTED: cmr.CrossrefUnavailable("down")}
    report, _ = report_for(tmp_path, f"{RETRACTED}\tlines 1\n", oa=oa, cr=cr)
    assert report["items"][0]["status"] == "retracted" and report["state"] == "partial"
    assert "Crossref unknown (unavailable or unreadable)" in cmr.render(report)


def test_doi_text_in_a_code_span_has_no_backslash_escapes(tmp_path):
    cr = {k: v for k, v in CR.items() if k != UNDERSCORE}  # OpenAlex-only, so the row is listed
    report, _ = report_for(tmp_path, f"{UNDERSCORE}\tlines 2\n{RETRACTED}\tlines 3\n", cr=cr)
    text = cmr.render(report)
    assert report["items"][0]["openalex_only"]
    assert f"`{UNDERSCORE}`" in text and "\\_" not in text


def test_code_span_fence_is_longer_than_any_backtick_run_in_the_value():
    assert cmr._code("10.1000/a") == "`10.1000/a`"
    assert cmr._code("a`b") == "``a`b``"
    assert cmr._code("a``b`") == "``` a``b` ```"
    assert cmr._code("`x") == "`` `x ``"


def test_invalid_lines_are_reported_by_number_only(tmp_path):
    note = "Reviewer 2 is my former supervisor, see the private email thread"
    report, _ = report_for(tmp_path, f"{CLEAN}\n{note}\n``` injected\n")
    text = cmr.render(report)
    assert report["invalid"] == [2, 3]
    assert "list line 2" in text and "list line 3" in text
    assert "supervisor" not in text and "injected" not in text


def test_decode_errors_give_the_position_and_never_the_bytes(tmp_path, capsys):
    bad = tmp_path / "bad.txt"
    bad.write_bytes(b"10.1000/a secretword " + bytes([0xFF, 0xFE]))
    assert cmr.main(["check", "--list", str(bad)]) == 2
    err = capsys.readouterr().err
    assert "not valid UTF-8 (error at byte 21)" in err and "secretword" not in err and "0xff" not in err.lower()
    manuscript = tmp_path / "m.bin"
    manuscript.write_bytes(b"secretword " + bytes([0xFF]))
    out = tmp_path / "list.txt"
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 2
    err = capsys.readouterr().err
    assert "not valid UTF-8 (error at byte 11)" in err and "secretword" not in err and not out.exists()


def test_disputed_covers_a_conflict_inside_one_index(tmp_path):
    report, _ = report_for(tmp_path, f"{SPLIT}\tlines 4\n")
    item = report["items"][0]
    assert item["status"] == "disputed" and item["openalex"]["verdict"] == "not_retracted"
    text = cmr.render(report)
    assert "or one index reports conflicting retraction events" in text
    assert "單一索引內的撤稿事件互相矛盾" in cmr.render(report, "zh-TW")


def test_the_list_file_is_created_with_mode_0600_and_exclusive_flags(tmp_path, monkeypatch):
    manuscript, out = _list_inputs(tmp_path)
    seen = []
    real_os_open = os.open
    monkeypatch.setattr(cmr.os, "open", lambda path, flags, mode=0o777: (seen.append((flags, mode)), real_os_open(path, flags, mode))[1])
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 0
    flags, mode = seen[0]
    assert mode == 0o600 and flags & os.O_CREAT and flags & os.O_EXCL and flags & os.O_WRONLY


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits")
def test_the_list_file_has_no_group_or_other_permissions(tmp_path):
    manuscript, out = _list_inputs(tmp_path)
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 0
    assert out.stat().st_mode & 0o077 == 0


def test_the_list_file_keeps_unix_newlines(tmp_path):
    manuscript, out = _list_inputs(tmp_path)
    assert cmr.main(["list", "--manuscript", str(manuscript), "--out", str(out)]) == 0
    assert b"\r\n" not in out.read_bytes()


def test_docs_say_a_failed_removal_leaves_the_file_and_names_it():
    root = SCRIPT.parents[1]
    skill = (root / "academic-paper-reviewer" / "SKILL.md").read_text(encoding="utf-8")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    for text in (skill, changelog):
        assert "names the path that remains" in text
