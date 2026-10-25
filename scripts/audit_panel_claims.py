#!/usr/bin/env python3
"""Check the panel's findings against the manuscript (#1002, part 2).

An advisory attachment to the Editorial Decision Letter, written after the
decision is final (``academic-paper-reviewer/SKILL.md`` § Reviewer claim check
attachment). The judge is one subagent of the session model with no tools; this
script only prepares its prompt and reads its reply:

  prompt  read the saved Phase 2 reports, take every ``### W<n>`` finding of the
          four scoring seats and every CRITICAL and MAJOR row of the Devil's
          Advocate (the part 1 extraction), give each a neutral id in hash
          order so the prompt carries no seat label (a finding's own words can
          still show its seat), and write the part 1 auditor prompt and the
          key into --out-dir
  render  read the judge's reply against the key and print the Markdown
          attachment. A ``false`` verdict is listed as one the judge marked
          contradicted only when its quote passes the part 1 mechanical check:
          a contradiction quote occurs in the manuscript, or words the claim
          presents in quotation marks occur nowhere in the manuscript. The check
          reads only the quote's words, not its locator or whether it
          contradicts the finding, and the attachment says so. Any other
          ``false`` verdict is listed as unconfirmed. A scoring report with a
          ``### W<n>`` heading that cannot be read, or a Severity line outside
          every read finding, counts as not read, and all report and judge text goes into
          the letter as literal text.

The report never changes the decision, the consensus counts, or the roadmap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from check_panel_synthesis import ReportError
    from dispatch_panel_claim_audit import _item_line, _norm, evidence_ok, json_lines, read_verdicts
    from check_panel_synthesis import split_sections, strip_fences
    from extract_panel_claims import _SECTION_END_RE, _W_HEADING_RE, da_claims, w_claims
except ImportError:  # pragma: no cover - dual-path import
    from scripts.check_panel_synthesis import ReportError
    from scripts.dispatch_panel_claim_audit import _item_line, _norm, evidence_ok, json_lines, read_verdicts
    from scripts.check_panel_synthesis import split_sections, strip_fences
    from scripts.extract_panel_claims import _SECTION_END_RE, _W_HEADING_RE, da_claims, w_claims

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
        "summary": "The judge answered {a} of {n} findings from {k} reviewers: it marked {false} "
                   "as contradicted, and {nv} cannot be checked from the manuscript alone.",
        "partial": "Coverage: partial. {missing} findings have no usable verdict.",
        "none": "The reports hold no findings to check.",
        "none_read": "No report could be read, so no finding was checked.",
        "unread": "Coverage: partial. Not read: {seats}.",
        "contradicted": "The judge marked these findings as contradicted by the manuscript. The script checked "
                        "only the words of each quote: that they occur in the manuscript, or, for words the "
                        "finding quotes, that they do not. The judge gave the locations, and the script did not "
                        "check them. Read each quote to decide:",
        "absent": "The claim quotes words that the manuscript does not contain: “{quote}”",
        "row": "- {seat} · {fid}: {title}",
        "quote": "  > “{quote}” ({locator})",
        "unconfirmed": "The judge also marked {items} as false, but its quote did not pass the check, "
                       "so they are not shown as contradicted.",
        "note": "The author decides what to do with each row. This check does not change the decision, "
                "the consensus counts, or the Revision Roadmap. The judge is the session model; as this judge, the #1002 "
                "contrast test passed Claude Opus 5.5 and Claude Fable 5.1 (gpt-6-astra and Gemini 4 Argon "
                "passed it in part one, through other transports); other models are untested.",
    },
    "zh-TW": {
        "title": "## Attachment: Reviewer Claim Check (advisory, #1002)",
        "seats": {"eic": "期刊適配審稿人", "methodology": "審稿人 1", "domain": "審稿人 2",
                  "perspective": "審稿人 3", "da": "魔鬼代言人"},
        "summary": "{k} 位審稿人共 {n} 項意見，判官回答了 {a} 項：判官判定 {false} 項與稿件內容矛盾，"
                   "{nv} 項無法只靠稿件判斷。",
        "partial": "涵蓋範圍：部分。{missing} 項意見沒有可用的判定。",
        "none": "審稿報告中沒有可檢查的意見。",
        "none_read": "沒有能讀取的審稿報告，未檢查任何意見。",
        "unread": "涵蓋範圍：部分。未能讀取：{seats}。",
        "contradicted": "判官判定下列意見與稿件內容矛盾。腳本只核對引文的文字：引文出現在稿件中，"
                        "或意見引用的文字確實不在稿件中。章節或表格位置由判官提供，腳本未核對。"
                        "是否矛盾請讀引文後判斷：",
        "absent": "意見引用了稿件中沒有的文字：「{quote}」",
        "row": "- {seat} · {fid}：{title}",
        "quote": "  > 「{quote}」（{locator}）",
        "unconfirmed": "判定者另將 {items} 判為錯誤，但引文未通過比對，因此不列為矛盾。",
        "note": "每一項由作者決定如何處理。這項檢查不改變審稿決定、共識計數或修訂路線圖。"
                "判官是 session 模型；作為這個判官，#1002 的對照測驗通過了 Claude Opus 5.5 與 Claude Fable 5.1"
                "（gpt-6-astra 與 Gemini 4 Argon 在第一部分經由其他傳輸方式通過）；其他模型未經測試。",
    },
}


class Stop(Exception):
    """A problem that stops the script; the attachment then says the check did not run."""


# A "### W<n>" heading, also one that `w_claims` cannot read (no colon, or the
# W number in bold, say).
_W_HEADING_LIKE = re.compile(r"^\s{0,3}###\s+[*_`\s]*[Ww]\s*\d")
# Each finding with a Severity has its own W subsection (sprint_contract_protocol.md
# § Anchor gate), so a Severity line outside every read finding shows one that
# was not read.
_SEVERITY_LINE = re.compile(r"^\s*(?:[-*+]\s+)?[*_]*Severity[*_]*\s*:", re.IGNORECASE)
# A span the claim presents in quotation marks; straight single quotes are left
# out, since they also serve as apostrophes.
_QUOTED = re.compile(r'"([^"\n]+)"|“([^”\n]+)”|‘([^’\n]+)’|「([^」\n]+)」|『([^』\n]+)』')


def _claims(seat: str, text: str, path: str) -> list[tuple[str, str]]:
    if seat == "da":
        return da_claims(text, path)
    sections, _dupes = split_sections(strip_fences(text, preserve_fenced_blocks=True))
    if "Review Body" not in sections:
        raise ReportError(f"{path}: no Review Body section")
    # Walk the body as `w_claims` does. A heading line is a title, so only the
    # lines under a heading count as its finding's text.
    inside = False
    for line in sections["Review Body"]:
        if _W_HEADING_LIKE.match(line) and not _W_HEADING_RE.match(line):
            raise ReportError(f"{path}: a W heading cannot be read")
        if _SECTION_END_RE.match(line):
            inside = bool(_W_HEADING_RE.match(line))
        elif not inside and _SEVERITY_LINE.match(line):
            raise ReportError(f"{path}: a finding with a Severity is outside every W heading")
    return w_claims(text)


def _quoted_in_claim(quote: str, claim: str) -> bool:
    """True when the claim presents ``quote`` inside quotation marks."""
    q = _norm(quote)
    # A quotation can wrap onto the next line, so the claim is read as one line.
    return bool(q) and any(q in _norm(next(g for g in m.groups() if g is not None))
                           for m in _QUOTED.finditer(" ".join(claim.split())))


def _checked(row: dict[str, Any], claim: str, manuscript: str) -> bool:
    """The part 1 quote check, and for an absent quotation also that the claim
    presents the quoted words as a quotation."""
    return evidence_ok(row, claim, manuscript) and (
        row.get("evidence") != "absent_quotation" or _quoted_in_claim(row["quote"], claim))


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
    try:
        template = PROMPT.read_text(encoding="utf-8")
    except OSError as exc:
        raise Stop(f"cannot read the auditor prompt ({type(exc).__name__})") from None
    # One pass, so a placeholder written in the manuscript or a claim stays as text.
    fill = {"manuscript": manuscript, "claims": claims}
    prompt = re.sub(r"\{(manuscript|claims)\}", lambda m: fill[m.group(1)], template)
    key = {"checker": CHECKER, "seats": [s for s, _p in reports if s not in unread], "unread": unread,
           "manuscript_sha256": hashlib.sha256(manuscript.encode("utf-8")).hexdigest(), "items": items}
    return prompt, key


def _key_ok(key: Any) -> bool:
    if not isinstance(key, dict) or key.get("checker") != CHECKER:
        return False
    lists = all(isinstance(key.get(f), list) for f in ("seats", "unread", "items"))
    return (lists and isinstance(key.get("manuscript_sha256"), str)
            and all(s in SEATS for s in key["seats"] + key["unread"])
            and all(isinstance(i, dict) and i.get("seat") in SEATS
                    and all(isinstance(i.get(f), str) for f in ("claim_id", "finding_id", "text"))
                    for i in key["items"]))


def build_report(manuscript: str, key: dict[str, Any], reply: str) -> dict[str, Any]:
    if not _key_ok(key):
        raise Stop("the key was not written by this script")
    if key["manuscript_sha256"] != hashlib.sha256(manuscript.encode("utf-8")).hexdigest():
        raise Stop("the manuscript is not the one the prompt was built from")
    items = key["items"]
    ids = [i["claim_id"] for i in items]
    rows, _problem = read_verdicts(reply, ids) if items else ({}, None)
    # An id answered more than once has no usable verdict, whichever line came first.
    seen = Counter(r["claim_id"] for r in json_lines(reply) if isinstance(r.get("claim_id"), str))
    rows = {cid: row for cid, row in rows.items() if seen[cid] == 1}
    contradicted, unconfirmed, nv = [], [], 0
    for item in items:
        row = rows.get(item["claim_id"])
        if row is None:
            continue
        if row["verdict"] == "not_verifiable":
            nv += 1
        elif row["verdict"] == "false":
            entry = {**item, "evidence": row["evidence"], "quote": row["quote"], "locator": row["locator"]}
            (contradicted if _checked(row, item["text"], manuscript) else unconfirmed).append(entry)
    return {"checker": CHECKER, "seats": key["seats"], "unread": key["unread"], "findings": len(items),
            "answered": len(rows), "not_verifiable": nv, "contradicted": contradicted,
            "unconfirmed": unconfirmed}


# Text from the reports and the judge goes into the letter as literal text, as
# `verify_panel_recommendations._cell` renders it: one line, HTML characters as
# entities, and inline Markdown punctuation backslash-escaped.
_MD_SPECIAL = re.compile(r"([\\`*_\[\]|~])")


def _one_line(text: str) -> str:
    text = " ".join(str(text).split())
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return _MD_SPECIAL.sub(r"\\\1", text)


def render(report: dict[str, Any], lang: str) -> str:
    text = _TEXT[lang]
    seat = text["seats"]
    lines = [text["title"], ""]
    if report["unread"]:
        lines.append(text["unread"].format(seats=", ".join(seat[s] for s in report["unread"])))
    if not report["findings"]:
        lines.append(text["none_read"] if not report["seats"] else text["none"])
        return "\n".join(lines)
    lines.append(text["summary"].format(a=report["answered"], n=report["findings"], k=len(report["seats"]),
                                        false=len(report["contradicted"]), nv=report["not_verifiable"]))
    if report["answered"] < report["findings"]:
        lines.append(text["partial"].format(missing=report["findings"] - report["answered"]))
    if report["contradicted"]:
        lines += ["", text["contradicted"]]
        for c in report["contradicted"]:
            lines.append(text["row"].format(seat=seat[c["seat"]], fid=_one_line(c["finding_id"]),
                                            title=_one_line(c["text"].split("\n", 1)[0])))
            if c["evidence"] == "absent_quotation":
                lines.append("  " + text["absent"].format(quote=_one_line(c["quote"])))
            else:
                lines.append(text["quote"].format(quote=_one_line(c["quote"]), locator=_one_line(c["locator"])))
    if report["unconfirmed"]:
        items = ", ".join(f"{seat[u['seat']]} · {_one_line(u['finding_id'])}" for u in report["unconfirmed"])
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
            try:
                args.out_dir.mkdir(parents=True, exist_ok=True)
                (args.out_dir / PROMPT_FILE).write_text(prompt, encoding="utf-8")
                (args.out_dir / KEY_FILE).write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n",
                                                     encoding="utf-8")
            except OSError as exc:
                raise Stop(f"cannot write to {args.out_dir} ({type(exc).__name__})") from None
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
