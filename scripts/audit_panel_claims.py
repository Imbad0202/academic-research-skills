#!/usr/bin/env python3
"""Check the panel's findings against the manuscript (#1002, part 2).

An advisory attachment to the Editorial Decision Letter, written after the
decision is final (``academic-paper-reviewer/SKILL.md`` § Reviewer claim check
attachment). The judge is one subagent of the session model with no tools; this
script only prepares its prompt and reads its reply:

  prompt  read the saved Phase 2 reports, take every ``### W<n>`` finding of the
          four scoring seats and every CRITICAL and MAJOR row of the Devil's
          Advocate (the part 1 extraction), give each a neutral id in hash
          order so the judge cannot see the seat, and write the part 1 auditor
          prompt and the key into --out-dir
  render  read the judge's reply against the key and print the Markdown
          attachment. A ``false`` verdict is shown as contradicted only when
          its quote passes the part 1 mechanical check: a contradiction quote
          occurs in the manuscript, or a quotation the claim presents occurs in
          the claim and nowhere in the manuscript. Any other ``false`` verdict
          is listed as unconfirmed.

The report never changes the decision, the consensus counts, or the roadmap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    from check_panel_synthesis import ReportError
    from dispatch_panel_claim_audit import _item_line, evidence_ok, read_verdicts
    from extract_panel_claims import da_claims, w_claims
except ImportError:  # pragma: no cover - dual-path import
    from scripts.check_panel_synthesis import ReportError
    from scripts.dispatch_panel_claim_audit import _item_line, evidence_ok, read_verdicts
    from scripts.extract_panel_claims import da_claims, w_claims

CHECKER = "audit_panel_claims/1"
# The prompt that passed the part 1 contrast test, used unchanged.
PROMPT = (Path(__file__).resolve().parent.parent / "evals" / "heldout" / "panel_claim_factuality"
          / "prompts" / "auditor.md")
SEATS = ("eic", "methodology", "domain", "perspective", "da")
LANGS = ("en", "zh-TW")
KEY_FILE, PROMPT_FILE = "key.json", "prompt.md"

_TEXT = {
    "en": {
        "title": "## Attachment: Reviewer Claim Check (advisory, #1002)",
        "seats": {"eic": "Journal-Fit Reviewer", "methodology": "Reviewer 1", "domain": "Reviewer 2",
                  "perspective": "Reviewer 3", "da": "Devil's Advocate"},
        "summary": "Checked {n} findings from {k} reviewers against the manuscript: {false} contradicted, "
                   "{nv} cannot be checked from the manuscript alone.",
        "partial": "Coverage: partial. {missing} findings have no usable verdict.",
        "none": "The reports hold no findings to check.",
        "unread": "Not read: {seats}.",
        "contradicted": "Contradicted by the manuscript:",
        "absent": "The claim quotes words that the manuscript does not contain: “{quote}”",
        "row": "- {seat} · {fid}: {title}",
        "quote": "  > “{quote}” ({locator})",
        "unconfirmed": "The judge also marked {items} as false, but its quote did not pass the check, "
                       "so they are not shown as contradicted.",
        "note": "The author decides what to do with each row. This check does not change the decision, "
                "the consensus counts, or the Revision Roadmap.",
    },
    "zh-TW": {
        "title": "## Attachment: Reviewer Claim Check (advisory, #1002)",
        "seats": {"eic": "期刊適配審稿人", "methodology": "審稿人 1", "domain": "審稿人 2",
                  "perspective": "審稿人 3", "da": "魔鬼代言人"},
        "summary": "已對照稿件檢查 {k} 位審稿人的 {n} 項意見：{false} 項與稿件內容矛盾，"
                   "{nv} 項無法只靠稿件判斷。",
        "partial": "涵蓋範圍：部分。{missing} 項意見沒有可用的判定。",
        "none": "審稿報告中沒有可檢查的意見。",
        "unread": "未能讀取：{seats}。",
        "contradicted": "與稿件內容矛盾的意見：",
        "absent": "意見引用了稿件中沒有的文字：「{quote}」",
        "row": "- {seat} · {fid}：{title}",
        "quote": "  > 「{quote}」（{locator}）",
        "unconfirmed": "判定者另將 {items} 判為錯誤，但引文未通過比對，因此不列為矛盾。",
        "note": "每一項由作者決定如何處理。這項檢查不改變審稿決定、共識計數或修訂路線圖。",
    },
}


class Stop(Exception):
    """A problem that stops the script; the attachment then says the check did not run."""


def _claims(seat: str, text: str, path: str) -> list[tuple[str, str]]:
    return da_claims(text, path) if seat == "da" else w_claims(text)


def build_prompt(manuscript: str, reports: list[tuple[str, Path]]) -> tuple[str, dict[str, Any]]:
    """The judge prompt and the key that maps each neutral id to its seat and finding."""
    findings, unread = [], []
    for seat, path in reports:
        try:
            text = path.read_text(encoding="utf-8")
            found = _claims(seat, text, str(path))
        except (OSError, UnicodeDecodeError, ReportError):
            unread.append(seat)
            continue
        findings += [(seat, fid, claim) for fid, claim in found]
    findings.sort(key=lambda f: hashlib.sha256(f"{f[0]}\0{f[1]}\0{f[2]}".encode("utf-8")).hexdigest())
    items = [{"claim_id": f"c{n:03d}", "seat": seat, "finding_id": fid, "text": claim}
             for n, (seat, fid, claim) in enumerate(findings, start=1)]
    claims = "\n".join(_item_line(i["claim_id"], i["text"]) for i in items)
    prompt = PROMPT.read_text(encoding="utf-8").replace("{manuscript}", manuscript).replace("{claims}", claims)
    key = {"checker": CHECKER, "seats": [s for s, _p in reports if s not in unread], "unread": unread,
           "manuscript_sha256": hashlib.sha256(manuscript.encode("utf-8")).hexdigest(), "items": items}
    return prompt, key


def build_report(manuscript: str, key: dict[str, Any], reply: str) -> dict[str, Any]:
    if key.get("checker") != CHECKER:
        raise Stop("the key was not written by this script")
    if key["manuscript_sha256"] != hashlib.sha256(manuscript.encode("utf-8")).hexdigest():
        raise Stop("the manuscript is not the one the prompt was built from")
    items = key["items"]
    rows, _problem = read_verdicts(reply, [i["claim_id"] for i in items]) if items else ({}, None)
    contradicted, unconfirmed, nv = [], [], 0
    for item in items:
        row = rows.get(item["claim_id"])
        if row is None:
            continue
        if row["verdict"] == "not_verifiable":
            nv += 1
        elif row["verdict"] == "false":
            entry = {**item, "evidence": row["evidence"], "quote": row["quote"], "locator": row["locator"]}
            (contradicted if evidence_ok(row, item["text"], manuscript) else unconfirmed).append(entry)
    return {"checker": CHECKER, "seats": key["seats"], "unread": key["unread"], "findings": len(items),
            "answered": len(rows), "not_verifiable": nv, "contradicted": contradicted,
            "unconfirmed": unconfirmed}


def _one_line(text: str) -> str:
    return " ".join(str(text).split())


def render(report: dict[str, Any], lang: str) -> str:
    text = _TEXT[lang]
    seat = text["seats"]
    lines = [text["title"], ""]
    if report["unread"]:
        lines.append(text["unread"].format(seats=", ".join(seat[s] for s in report["unread"])))
    if not report["findings"]:
        lines.append(text["none"])
        return "\n".join(lines)
    lines.append(text["summary"].format(n=report["findings"], k=len(report["seats"]),
                                        false=len(report["contradicted"]), nv=report["not_verifiable"]))
    if report["answered"] < report["findings"]:
        lines.append(text["partial"].format(missing=report["findings"] - report["answered"]))
    if report["contradicted"]:
        lines += ["", text["contradicted"]]
        for c in report["contradicted"]:
            lines.append(text["row"].format(seat=seat[c["seat"]], fid=c["finding_id"],
                                            title=_one_line(c["text"].split("\n", 1)[0])))
            if c["evidence"] == "absent_quotation":
                lines.append("  " + text["absent"].format(quote=_one_line(c["quote"])))
            else:
                lines.append(text["quote"].format(quote=_one_line(c["quote"]), locator=_one_line(c["locator"])))
    if report["unconfirmed"]:
        items = ", ".join(f"{seat[u['seat']]} · {u['finding_id']}" for u in report["unconfirmed"])
        lines += ["", text["unconfirmed"].format(items=items)]
    lines += ["", text["note"]]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _report_arg(value: str) -> tuple[str, Path]:
    seat, sep, path = value.partition("=")
    if not sep or not path or seat not in SEATS:
        raise argparse.ArgumentTypeError(f"expected SEAT=PATH with SEAT one of {', '.join(SEATS)}, got {value!r}")
    return seat, Path(path)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Stop(f"cannot read {path.name} ({type(exc).__name__})") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the panel's findings against the manuscript (#1002).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prompt", help="Write the judge prompt and the key.")
    p.add_argument("--manuscript", type=Path, required=True)
    p.add_argument("--report", type=_report_arg, action="append", required=True, metavar="SEAT=PATH",
                   help=f"A saved Phase 2 report; SEAT is one of {', '.join(SEATS)}. Repeatable.")
    p.add_argument("--out-dir", type=Path, required=True)
    r = sub.add_parser("render", help="Read the judge's reply and print the attachment.")
    r.add_argument("--manuscript", type=Path, required=True)
    r.add_argument("--out-dir", type=Path, required=True, help="The directory that prompt wrote.")
    r.add_argument("--reply", type=Path, required=True)
    r.add_argument("--lang", choices=LANGS, default="en")
    args = parser.parse_args(argv)
    try:
        manuscript = _read(args.manuscript)
        if args.cmd == "prompt":
            seats = [s for s, _p in args.report]
            if len(set(seats)) != len(seats):
                raise Stop("a seat is given twice")
            prompt, key = build_prompt(manuscript, args.report)
            args.out_dir.mkdir(parents=True, exist_ok=True)
            (args.out_dir / PROMPT_FILE).write_text(prompt, encoding="utf-8")
            (args.out_dir / KEY_FILE).write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n",
                                                 encoding="utf-8")
            print(f"{len(key['items'])} findings; prompt in {args.out_dir / PROMPT_FILE}")
            return 0
        try:
            key = json.loads(_read(args.out_dir / KEY_FILE))
        except ValueError:
            raise Stop("the key is not JSON") from None
        print(render(build_report(manuscript, key, _read(args.reply)), args.lang))
        return 0
    except Stop as stop:
        print(f"STOP: {stop}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
