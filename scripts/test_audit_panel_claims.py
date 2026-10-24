#!/usr/bin/env python3
"""Tests for scripts/audit_panel_claims.py (#1002, part 2). Synthetic reports only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import audit_panel_claims as apc  # noqa: E402
from test_extract_panel_claims import DA_REPORT, _seat_report  # noqa: E402

MANUSCRIPT = ("# Study\n\n## 3 Method\n\nWe drew a random sample of 240 teachers. "
              "Cronbach's alpha for the 12-item scale was .87.\n")


def _reports(tmp_path: Path) -> list[tuple[str, Path]]:
    r1 = tmp_path / "r1.md"
    r1.write_text(_seat_report(["No reliability reported", "Small sample"]), encoding="utf-8")
    da = tmp_path / "da.md"
    da.write_text(DA_REPORT, encoding="utf-8")
    return [("methodology", r1), ("da", da)]


def _prompt(tmp_path: Path, reports=None):
    return apc.build_prompt(MANUSCRIPT, reports or _reports(tmp_path))


def _reply(key: dict, verdicts: dict[str, dict]) -> str:
    lines = []
    for item in key["items"]:
        row = {"claim_id": item["claim_id"], "verdict": "true", "severity": "minor",
               "evidence": None, "quote": None, "locator": None, "reason": "r"}
        row.update(verdicts.get((item["seat"], item["finding_id"]), {}))
        lines.append(json.dumps(row))
    return "\n".join(lines)


FALSE_OK = {"verdict": "false", "evidence": "contradiction",
            "quote": "Cronbach's alpha for the 12-item scale was .87.", "locator": "§3"}


def test_the_prompt_holds_every_finding_and_hides_the_seat(tmp_path):
    prompt, key = _prompt(tmp_path)
    assert len(key["items"]) == 5  # two W findings, one CRITICAL row, two MAJOR rows
    assert [i["claim_id"] for i in key["items"]] == ["c001", "c002", "c003", "c004", "c005"]
    assert "methodology" not in prompt and '"seat"' not in prompt
    assert MANUSCRIPT in prompt and "{claims}" not in prompt and "{manuscript}" not in prompt


def test_the_prompt_is_the_part_1_auditor_prompt(tmp_path):
    prompt, _key = _prompt(tmp_path)
    head = apc.PROMPT.read_text(encoding="utf-8").split("{manuscript}")[0]
    assert prompt.startswith(head)


def test_a_checked_contradiction_is_shown(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {("methodology", "W1"): FALSE_OK}))
    assert [(c["seat"], c["finding_id"]) for c in report["contradicted"]] == [("methodology", "W1")]
    out = apc.render(report, "en")
    assert "Reviewer 1 · W1: No reliability reported" in out
    assert "“Cronbach's alpha for the 12-item scale was .87.” (§3)" in out
    assert "1 contradicted" in out and "does not change the decision" in out


def test_a_false_verdict_whose_quote_is_not_in_the_manuscript_is_unconfirmed(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    bad = {**FALSE_OK, "quote": "alpha was .91"}
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {("methodology", "W1"): bad}))
    assert report["contradicted"] == [] and len(report["unconfirmed"]) == 1
    out = apc.render(report, "en")
    assert "0 contradicted" in out and "Reviewer 1 · W1" in out and "did not pass the check" in out


def test_an_absent_quotation_is_shown_only_when_the_words_are_not_in_the_manuscript(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    absent = {"verdict": "false", "evidence": "absent_quotation", "quote": "random", "locator": "absent"}
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {("da", "M1"): absent}))
    assert report["contradicted"] == [] and len(report["unconfirmed"]) == 1  # "random" is in the manuscript
    absent = {**absent, "quote": "Unreported attrition"}
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {("da", "M2"): absent}))
    assert [c["finding_id"] for c in report["contradicted"]] == ["M2"]


def test_missing_verdicts_make_the_coverage_partial(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    reply = "\n".join(_reply(key, {}).split("\n")[:3])
    report = apc.build_report(MANUSCRIPT, key, reply)
    assert report["answered"] == 3
    assert "Coverage: partial. 2 findings have no usable verdict." in apc.render(report, "en")


def test_not_verifiable_is_counted_and_not_listed(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {("da", "C1"): {"verdict": "not_verifiable"}}))
    assert report["not_verifiable"] == 1 and report["contradicted"] == []
    assert "1 cannot be checked" in apc.render(report, "en")


def test_an_unreadable_report_is_listed(tmp_path):
    bad = tmp_path / "da.md"
    bad.write_text("## Review Body\n\nno tables\n", encoding="utf-8")
    good = tmp_path / "r1.md"
    good.write_text(_seat_report(["Small sample"]), encoding="utf-8")
    _prompt_text, key = apc.build_prompt(MANUSCRIPT, [("methodology", good), ("da", bad)])
    assert key["unread"] == ["da"] and len(key["items"]) == 1
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {}))
    assert "Not read: Devil's Advocate." in apc.render(report, "en")


def test_no_findings_says_so(tmp_path):
    r1 = tmp_path / "r1.md"
    r1.write_text(_seat_report([]), encoding="utf-8")
    _prompt_text, key = apc.build_prompt(MANUSCRIPT, [("methodology", r1)])
    out = apc.render(apc.build_report(MANUSCRIPT, key, ""), "en")
    assert "no findings to check" in out


def test_a_changed_manuscript_stops_the_render(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    with pytest.raises(apc.Stop, match="not the one"):
        apc.build_report(MANUSCRIPT + "x", key, "")


def test_the_report_renders_in_traditional_chinese(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    out = apc.render(apc.build_report(MANUSCRIPT, key, _reply(key, {("methodology", "W1"): FALSE_OK})), "zh-TW")
    assert "審稿人 1 · W1" in out and "1 項與稿件內容矛盾" in out


def test_the_cli_writes_the_prompt_then_renders(tmp_path, capsys):
    (tmp_path / "ms.md").write_text(MANUSCRIPT, encoding="utf-8")
    reports = _reports(tmp_path)
    out_dir = tmp_path / "check"
    argv = ["prompt", "--manuscript", str(tmp_path / "ms.md"), "--out-dir", str(out_dir)]
    for seat, path in reports:
        argv += ["--report", f"{seat}={path}"]
    assert apc.main(argv) == 0
    key = json.loads((out_dir / "key.json").read_text(encoding="utf-8"))
    (tmp_path / "reply.txt").write_text(_reply(key, {("methodology", "W1"): FALSE_OK}), encoding="utf-8")
    capsys.readouterr()
    assert apc.main(["render", "--manuscript", str(tmp_path / "ms.md"), "--out-dir", str(out_dir),
                     "--reply", str(tmp_path / "reply.txt")]) == 0
    assert capsys.readouterr().out.startswith("## Attachment: Reviewer Claim Check (advisory, #1002)")


def test_the_cli_refuses_an_unknown_seat_and_a_repeated_seat(tmp_path, capsys):
    (tmp_path / "ms.md").write_text(MANUSCRIPT, encoding="utf-8")
    with pytest.raises(SystemExit):
        apc.main(["prompt", "--manuscript", str(tmp_path / "ms.md"), "--out-dir", str(tmp_path / "o"),
                  "--report", "R9=x.md"])
    r1 = tmp_path / "r1.md"
    r1.write_text(_seat_report(["x"]), encoding="utf-8")
    assert apc.main(["prompt", "--manuscript", str(tmp_path / "ms.md"), "--out-dir", str(tmp_path / "o"),
                     "--report", f"methodology={r1}", "--report", f"methodology={r1}"]) == 2
    assert "given twice" in capsys.readouterr().err
