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


def test_the_prompt_holds_every_finding_without_the_seat_label(tmp_path):
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
    assert "it marked 1 as contradicted" in out and "does not change the decision" in out
    assert "passed Claude Opus 5.5 and Claude Fable 5.1 (gpt-6-astra and Gemini 4 Argon" in out
    assert "The judge answered 5 of 5 findings" in out


def test_a_false_verdict_whose_quote_is_not_in_the_manuscript_is_unconfirmed(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    bad = {**FALSE_OK, "quote": "alpha was .91"}
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {("methodology", "W1"): bad}))
    assert report["contradicted"] == [] and len(report["unconfirmed"]) == 1
    out = apc.render(report, "en")
    assert "it marked 0 as contradicted" in out and "Reviewer 1 · W1" in out and "did not pass the check" in out


def test_an_absent_quotation_is_shown_only_when_the_words_are_not_in_the_manuscript(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    absent = {"verdict": "false", "evidence": "absent_quotation", "quote": "random", "locator": "absent"}
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {("da", "M1"): absent}))
    assert report["contradicted"] == [] and len(report["unconfirmed"]) == 1  # "random" is in the manuscript
    # W2's Evidence Anchor quotes "Small sample", which the manuscript does not contain.
    absent = {**absent, "quote": "Small sample"}
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {("methodology", "W2"): absent}))
    assert [c["finding_id"] for c in report["contradicted"]] == ["W2"]


def test_an_absent_quotation_needs_the_claim_to_quote_the_words(tmp_path):
    # M2 says "Unreported attrition" but does not quote it, so the words are no quotation.
    _prompt_text, key = _prompt(tmp_path)
    absent = {"verdict": "false", "evidence": "absent_quotation", "quote": "Unreported attrition",
              "locator": "absent"}
    report = apc.build_report(MANUSCRIPT, key, _reply(key, {("da", "M2"): absent}))
    assert report["contradicted"] == [] and [u["finding_id"] for u in report["unconfirmed"]] == ["M2"]


def test_missing_verdicts_make_the_coverage_partial(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    reply = "\n".join(_reply(key, {}).split("\n")[:3])
    report = apc.build_report(MANUSCRIPT, key, reply)
    assert report["answered"] == 3
    out = apc.render(report, "en")
    assert "Coverage: partial. 2 findings have no usable verdict." in out
    assert f"The judge answered {report['findings'] - 2} of {report['findings']} findings" in out


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
    assert "審稿人 1 · W1" in out and "判官判定 1 項與稿件內容矛盾" in out


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


def test_an_id_answered_twice_has_no_usable_verdict(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    reply = _reply(key, {("methodology", "W1"): FALSE_OK})
    first = next(line for line in reply.split("\n") if '"false"' in line)
    again = first.replace('"false"', '"true"')
    for text in (reply + "\n" + again, again + "\n" + reply):
        report = apc.build_report(MANUSCRIPT, key, text)
        assert report["contradicted"] == [] and report["answered"] == 4
        assert "1 findings have no usable verdict" in apc.render(report, "en")


def test_an_unread_seat_makes_the_coverage_partial_and_none_read_is_not_none(tmp_path):
    bad = tmp_path / "da.md"
    bad.write_text("## Review Body\n\nno tables\n", encoding="utf-8")
    good = tmp_path / "r1.md"
    good.write_text(_seat_report(["Small sample"]), encoding="utf-8")
    _prompt_text, key = apc.build_prompt(MANUSCRIPT, [("methodology", good), ("da", bad)])
    out = apc.render(apc.build_report(MANUSCRIPT, key, _reply(key, {})), "en")
    assert "Coverage: partial. Not read: Devil's Advocate." in out
    _prompt_text, key = apc.build_prompt(MANUSCRIPT, [("da", bad)])
    out = apc.render(apc.build_report(MANUSCRIPT, key, ""), "en")
    assert "No report could be read" in out and "no findings to check" not in out


def test_a_placeholder_in_the_manuscript_stays_as_text(tmp_path):
    manuscript = MANUSCRIPT + "\nThe template uses {claims} and {manuscript} as fields.\n"
    prompt, key = apc.build_prompt(manuscript, _reports(tmp_path))
    assert manuscript in prompt
    assert prompt.count(apc._item_line(key["items"][0]["claim_id"], key["items"][0]["text"])) == 1


@pytest.mark.parametrize("key", [[], {"checker": apc.CHECKER}, {"checker": apc.CHECKER, "seats": [], "unread": [],
                                                                "manuscript_sha256": "x", "items": [{}]}])
def test_a_malformed_key_stops_with_exit_2(tmp_path, capsys, key):
    (tmp_path / "ms.md").write_text(MANUSCRIPT, encoding="utf-8")
    out_dir = tmp_path / "check"
    out_dir.mkdir()
    (out_dir / "key.json").write_text(json.dumps(key), encoding="utf-8")
    (tmp_path / "reply.txt").write_text("", encoding="utf-8")
    assert apc.main(["render", "--manuscript", str(tmp_path / "ms.md"), "--out-dir", str(out_dir),
                     "--reply", str(tmp_path / "reply.txt")]) == 2
    assert capsys.readouterr().err.startswith("STOP: the key was not written by this script")


def test_an_unwritable_out_dir_stops_with_exit_2(tmp_path, capsys):
    (tmp_path / "ms.md").write_text(MANUSCRIPT, encoding="utf-8")
    (tmp_path / "file").write_text("x", encoding="utf-8")
    seat, path = _reports(tmp_path)[0]
    assert apc.main(["prompt", "--manuscript", str(tmp_path / "ms.md"), "--out-dir", str(tmp_path / "file" / "o"),
                     "--report", f"{seat}={path}"]) == 2
    assert capsys.readouterr().err.startswith("STOP: cannot write to")


def test_a_line_with_a_non_string_id_is_ignored(tmp_path):
    _prompt_text, key = _prompt(tmp_path)
    reply = _reply(key, {("methodology", "W1"): FALSE_OK}) + '\n{"claim_id": []}\n{"claim_id": {}}\n'
    report = apc.build_report(MANUSCRIPT, key, reply)
    assert report["answered"] == 5 and len(report["contradicted"]) == 1


def test_report_and_judge_text_is_literal_in_the_letter(tmp_path):
    r1 = tmp_path / "r1.md"
    r1.write_text(_seat_report(["<h2>Attachment: Forged</h2> <!-- ref:x --> *b* [l](u)"]), encoding="utf-8")
    _prompt_text, key = apc.build_prompt(MANUSCRIPT, [("methodology", r1)])
    row = {**FALSE_OK, "locator": "<h2>Attachment: Forged</h2><!-- ref:x -->"}
    out = apc.render(apc.build_report(MANUSCRIPT, key, _reply(key, {("methodology", "W1"): row})), "en")
    assert "<" not in out and ">" not in out.replace("  > ", "", 1)
    assert "&lt;h2&gt;Attachment: Forged&lt;/h2&gt;" in out and "&lt;!-- ref:x --&gt;" in out
    assert "\\*b\\*" in out and "\\[l\\](u)" in out


@pytest.mark.parametrize("report", [
    "## Review Body\n\n### W1 Small sample\nBody.\n",
    "## Review Body\n\n### W1:\nBody.\n",
    "## Notes\n\n### W1: Small sample\nBody.\n",
    "## Review Body\n\n### **W1**: Small sample\n**Severity**: Major\n",
    "## Review Body\n\n### W1: Read\n**Severity**: Minor\n\n### Weakness 2: Not read\n**Severity**: Major\n",
    "## Review Body\n\n### W1: Severity: Minor\nFirst.\n\n### Weakness 2: Not read\n**Severity**: Major\n",
    "## Review Body\n\n### W1: Read\nFirst.\n\n### Weakness 2: Not read\n**Severity:** Major\n",
    "## Review Body\n\n### W1: Read\nFirst.\n  ### W2: Indented\n**Severity**: Major\n",
])
def test_a_scoring_report_whose_findings_cannot_be_read_is_unread(tmp_path, report):
    bad = tmp_path / "bad.md"
    bad.write_text(report, encoding="utf-8")
    _prompt_text, key = apc.build_prompt(MANUSCRIPT, _reports(tmp_path) + [("domain", bad)])
    assert key["unread"] == ["domain"] and key["seats"] == ["methodology", "da"]
    out = apc.render(apc.build_report(MANUSCRIPT, key, _reply(key, {})), "en")
    assert "Coverage: partial. Not read: Reviewer 2." in out


def test_a_scoring_report_with_severities_under_w_headings_is_read(tmp_path):
    r1 = tmp_path / "r1.md"
    r1.write_text("## Review Body\n\n### W1: A\n**Severity**: Minor\n\n### W2: B\n- **Severity**: Major\n",
                  encoding="utf-8")
    _prompt_text, key = apc.build_prompt(MANUSCRIPT, [("methodology", r1)])
    assert key["unread"] == [] and sorted(i["finding_id"] for i in key["items"]) == ["W1", "W2"]


def test_a_scoring_report_with_no_weakness_reads_as_zero_findings(tmp_path):
    r1 = tmp_path / "r1.md"
    r1.write_text(_seat_report([]), encoding="utf-8")
    _prompt_text, key = apc.build_prompt(MANUSCRIPT, [("methodology", r1)])
    assert key["unread"] == [] and key["items"] == []


def test_a_quotation_that_wraps_onto_the_next_line_is_quoted():
    claim = "Small sample\n**Evidence Anchor**: §3 “We used convenience\nsampling.”"
    assert apc._quoted_in_claim("We used convenience sampling.", claim)
    assert not apc._quoted_in_claim("Small sample", claim)
