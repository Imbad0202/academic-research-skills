#!/usr/bin/env python3
"""Check the references a review panel suggests (#1001).

Reads saved reviewer reports and never changes them. No model call. Domain
Reviewer (R2) and Perspective Reviewer (R3) list each specific work they
recommend in a fenced block whose info string is ``yaml suggested-references``
(a ``~~~`` fence works the same as a backtick fence)::

    ~~~yaml suggested-references
    - title: "Perceived usefulness, perceived ease of use, and user acceptance of information technology"
      authors: ["Davis, F. D."]
      year: 1989
      doi: "10.2307/249008"
      arxiv_id: null
    ~~~

A block holding only an empty list (``[]``) says the seat recommends no
specific work; an empty block, or one with only comments, is not read. Each item
needs a ``title``; ``authors``, ``year``, ``doi``, and ``arxiv_id`` are
optional. Each item goes through ``verification_gate.verify_citation`` with
the four resolver clients that ``verify_passport.py`` builds (Crossref,
OpenAlex, Semantic Scholar, arXiv), so the result follows the same rule as the
citation gate (C-V6(a)):

  found           an index holds a record that matches the DOI and title, the
                  arXiv ID and title, or the title;
  id_not_found    no index matches, and at least one index queried by the DOI
                  or arXiv ID reports no record for it;
  title_not_found no DOI or arXiv ID was given, no index matches, and at
                  least one index answered that it holds no match for the
                  title, so this check cannot tell a missing work from an
                  unindexed one;
  no_answer       every other case: no index matches, none reports no record
                  for the DOI or arXiv ID, and either the item has a DOI or
                  arXiv ID or no index answered for its title (each one failed
                  to answer or was skipped); also when the lookup failed.

``found`` shows only that a record exists. It does not show that the work
supports the recommendation, or that the given authors and year are right.

The lookups run live and do not read or write the verification cache: the
cache is keyed by citation_key, and a suggestion has none.

Exit 0: a report was written (status ``checked`` or ``partial``; ``partial``
lists what was not read). Exit 2: nothing was checked (``not_checked``: no
report file could be read).

    python3 scripts/verify_panel_recommendations.py \\
        --report R2=r2_report.md --report R3=r3_report.md --lang en
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

try:
    from verification_gate import verify_citation
    from verify_passport import _real_clients
except ImportError:  # pragma: no cover - dual-path import
    from scripts.verification_gate import verify_citation
    from scripts.verify_passport import _real_clients

CHECKER = "verify_panel_recommendations/1"
BLOCK_TAG = ("yaml", "suggested-references")
LANGS = ("en", "zh-TW")
_SEAT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,19}$")
_FENCE_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
_DOI_PREFIX_RE = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)
_ARXIV_PREFIX_RE = re.compile(r"^(?:https?://arxiv\.org/abs/|arxiv:\s*)", re.IGNORECASE)

_TEXT = {
    "en": {
        "title": "Suggested-reference check (script output, not a reviewer finding; #1001)",
        "coverage": "Seats read: {seats} ({state}).",
        "states": {"checked": "complete", "partial": "partial"},
        "not_checked": "Not checked: {reason}.",
        "reasons": {"no_readable_report": "no reviewer report file could be read"},
        "unread": "Not read:",
        "report_problems": {
            "unreadable": "- {seat}: the report file could not be read.",
            "missing": "- {seat}: the report has no suggested-references block.",
            "empty_block": "- {seat}: block {block} is empty.",
            "bad_yaml": "- {seat}: block {block} is not valid YAML.",
            "not_a_list": "- {seat}: block {block} is not a list.",
        },
        "item_problem": "- {seat} item {index}: {why}.",
        "item_reasons": {"not_a_mapping": "not a key-value entry",
                         "no_title": "no title"},
        "none": "No seat recommends a specific work.",
        "none_read": "No suggested reference could be read.",
        "header": "| Seat | # | Reference | Result |",
        "results": {
            "found": "Found in an index",
            "id_not_found": "DOI or arXiv ID not found, and no title match",
            "title_not_found": "Title not matched; no DOI or arXiv ID to check",
            "no_answer": "Not checked: an index that could settle it did not answer",
        },
        "note": ("\"Found\" means an index holds a record with this DOI or arXiv ID and title, "
                 "or with this title. It does not show that the work supports the "
                 "recommendation, or that the authors and year are right."),
    },
    "zh-TW": {
        "title": "建議文獻查核（腳本輸出，不是審稿意見；#1001）",
        "coverage": "已讀審稿席次：{seats}（{state}）。",
        "states": {"checked": "完整", "partial": "部分"},
        "not_checked": "未檢查：{reason}。",
        "reasons": {"no_readable_report": "沒有任何一份審稿報告檔可以讀取"},
        "unread": "未讀取：",
        "report_problems": {
            "unreadable": "- {seat}：報告檔無法讀取。",
            "missing": "- {seat}：報告裡沒有 suggested-references 區塊。",
            "empty_block": "- {seat}：第 {block} 個區塊是空的。",
            "bad_yaml": "- {seat}：第 {block} 個區塊不是有效的 YAML。",
            "not_a_list": "- {seat}：第 {block} 個區塊不是清單。",
        },
        "item_problem": "- {seat} 第 {index} 筆：{why}。",
        "item_reasons": {"not_a_mapping": "不是鍵值格式的條目",
                         "no_title": "沒有標題"},
        "none": "沒有任何席次建議具體文獻。",
        "none_read": "沒有讀到任何可查核的建議文獻。",
        "header": "| 席次 | # | 文獻 | 結果 |",
        "results": {
            "found": "索引查得到",
            "id_not_found": "DOI 或 arXiv 編號查不到，標題也比對不到",
            "title_not_found": "標題比對不到；沒有 DOI 或 arXiv 編號可查",
            "no_answer": "未檢查：能判定此筆的索引沒有回應",
        },
        "note": ("「索引查得到」表示有索引收錄了相同 DOI 或 arXiv 編號加標題，或相同標題的紀錄。"
                 "這不表示該文獻支持審稿人的建議，也不表示作者與年份正確。"),
    },
}


# ---------------------------------------------------------------------------
# Reading the blocks.
# ---------------------------------------------------------------------------


def extract_blocks(text: str) -> list[str]:
    """Return the body of every fenced block tagged ``yaml suggested-references``.

    Only tagged fences open a block. Other fences are read through, so a block
    inside a report that a reviewer wrapped in a ``markdown`` fence is still
    found. A closing fence uses the same character as the opening fence, is at
    least as long, has no info string, and is indented at most three columns
    more than the opening fence; a deeper fence line is block content, as in a
    YAML literal scalar. The opening fence's indentation is
    removed from each body line (up to as many leading spaces as the line has),
    so a block inside a list item reads the same as one at the margin. An unclosed block runs to the end of the text.
    """
    blocks: list[str] = []
    # Tabs count as four columns, so a tab-indented fence and a space-indented
    # one compare by column.
    lines = [line.expandtabs(4) for line in text.split("\n")]
    i = 0
    while i < len(lines):
        m = _FENCE_RE.match(lines[i])
        i += 1
        if not m or tuple(m.group("info").split()) != BLOCK_TAG:
            continue
        fence, indent = m.group("fence"), m.group("indent")
        body: list[str] = []
        while i < len(lines):
            close = _FENCE_RE.match(lines[i])
            if (close and close.group("fence")[0] == fence[0]
                    and len(close.group("fence")) >= len(fence)
                    and len(close.group("indent")) <= len(indent) + 3
                    and not close.group("info").strip()):
                i += 1
                break
            line = lines[i]
            lead = len(line) - len(line.lstrip(" "))
            body.append(line[min(lead, len(indent)):])
            i += 1
        blocks.append("\n".join(body))
    return blocks


# The blocks load with yaml.BaseLoader, so every scalar stays the text the
# reviewer wrote: an unquoted arXiv ID such as 2401.10230 keeps its last zero.
_NULLS = frozenset({"", "~", "null", "none"})


def _scalar(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(value.split())
    return None if text.casefold() in _NULLS else text


def _clean_id(value: Any, prefix_re: re.Pattern[str]) -> str | None:
    text = _scalar(value)
    return (prefix_re.sub("", text).strip() or None) if text else None


def _year(value: Any) -> int | None:
    text = _scalar(value)
    return int(text) if text and re.fullmatch(r"[0-9]{4}", text) else None


def _authors(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [a for a in (_scalar(v) for v in value) if a]


def read_report(seat: str, path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Read one report. Return (report record, items, item problems)."""
    record: dict[str, Any] = {"seat": seat, "input": str(path), "input_sha256": None,
                              "blocks": 0, "problems": []}
    items: list[dict[str, Any]] = []
    item_problems: list[dict[str, Any]] = []
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        record["problems"].append({"kind": "unreadable"})
        return record, items, item_problems
    record["input_sha256"] = hashlib.sha256(raw).hexdigest()
    blocks = extract_blocks(text.replace("\r\n", "\n"))
    record["blocks"] = len(blocks)
    if not blocks:
        record["problems"].append({"kind": "missing"})
    index = 0
    for number, body in enumerate(blocks, start=1):
        try:
            data = yaml.load(body, Loader=yaml.BaseLoader)
        except yaml.YAMLError:
            record["problems"].append({"kind": "bad_yaml", "block": number})
            continue
        if data is None:
            record["problems"].append({"kind": "empty_block", "block": number})
            continue
        if not isinstance(data, list):
            record["problems"].append({"kind": "not_a_list", "block": number})
            continue
        for entry in data:
            index += 1
            if not isinstance(entry, dict):
                item_problems.append({"seat": seat, "index": index, "reason": "not_a_mapping"})
                continue
            title = _scalar(entry.get("title"))
            if not title:
                item_problems.append({"seat": seat, "index": index, "reason": "no_title"})
                continue
            items.append({
                "seat": seat,
                "index": index,
                "title": title,
                "authors": _authors(entry.get("authors")),
                "year": _year(entry.get("year")),
                "doi": _clean_id(entry.get("doi"), _DOI_PREFIX_RE),
                "arxiv_id": _clean_id(entry.get("arxiv_id"), _ARXIV_PREFIX_RE),
            })
    return record, items, item_problems


# ---------------------------------------------------------------------------
# Looking the items up.
# ---------------------------------------------------------------------------


def classify(summary: dict[str, Any], has_id: bool) -> str:
    """Map the gate's 3-class verdict to a result. ``unresolvable`` is
    ``title_not_found`` only for an item with no identifier; with one, an index
    queried by it did not answer, so the identifier is unchecked."""
    verdict = summary["lookup_verified"]
    if verdict == "true":
        return "found"
    if verdict == "false":
        return "id_not_found"
    if not has_id and any(o.get("status") == "unmatched"
                          for o in summary["resolver_outcomes"].values()):
        return "title_not_found"
    return "no_answer"


def look_up(items: list[dict[str, Any]], clients: dict[str, Any]) -> None:
    """Add ``result`` and ``resolver_outcomes`` to each item, in place.

    Items with the same title, DOI, arXiv ID, and year share one lookup.
    """
    done: dict[tuple, tuple[str, dict[str, Any] | None]] = {}
    for item in items:
        key = (item["title"].casefold(), (item["doi"] or "").casefold(),
               (item["arxiv_id"] or "").casefold(), item["year"])
        if key not in done:
            slug = f"panel-suggestion-{len(done) + 1}"
            entry = {"citation_key": slug, "title": item["title"], "year": item["year"],
                     "doi": item["doi"], "arxiv_id": item["arxiv_id"],
                     "obtained_via": "panel_suggestion"}
            try:
                summary = verify_citation(entry, clients, ref_slug=slug,
                                          cache=None, revalidate_stale=False)
                has_id = bool(item["doi"] or item["arxiv_id"])
                done[key] = (classify(summary, has_id), summary["resolver_outcomes"])
            except Exception:  # an advisory attachment must not stop on one lookup
                done[key] = ("no_answer", None)
        item["result"], item["resolver_outcomes"] = done[key]


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def build_report(reports: list[tuple[str, Path]],
                 clients_factory: Callable[[], dict[str, Any]] = _real_clients) -> dict[str, Any]:
    report: dict[str, Any] = {"checker": CHECKER, "status": "not_checked", "reports": [],
                              "items": [], "item_problems": []}
    for seat, path in reports:
        record, items, problems = read_report(seat, path)
        report["reports"].append(record)
        report["items"] += items
        report["item_problems"] += problems
    if all(r["input_sha256"] is None for r in report["reports"]):
        report["reason"] = "no_readable_report"
        return report
    if report["items"]:
        look_up(report["items"], clients_factory())
    incomplete = (any(r["problems"] for r in report["reports"]) or report["item_problems"]
                  or any(i["result"] == "no_answer" for i in report["items"]))
    report["status"] = "partial" if incomplete else "checked"
    return report


# Characters that start inline Markdown inside a table cell; "(" and "!" act
# only next to "[" or "]", which are escaped.
_MD_SPECIAL = re.compile(r"([\\`*_\[\]|~])")


def _cell(text: str) -> str:
    """Render reviewer-written text as literal table text: one line, HTML
    characters as entities, Markdown punctuation backslash-escaped."""
    text = " ".join(text.split())
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return _MD_SPECIAL.sub(r"\\\1", text)


def _reference(item: dict[str, Any]) -> str:
    parts = []
    if item["authors"]:
        parts.append(item["authors"][0] + (" et al." if len(item["authors"]) > 1 else ""))
    if item["year"]:
        parts.append(f"({item['year']})")
    parts.append(f"\"{item['title']}\"")
    if item["doi"]:
        parts.append(f"doi:{item['doi']}")
    if item["arxiv_id"]:
        parts.append(f"arXiv:{item['arxiv_id']}")
    return _cell(" ".join(parts))


def render(report: dict[str, Any], lang: str) -> str:
    text = _TEXT[lang]
    lines = [text["title"]]
    if report["status"] == "not_checked":
        lines.append(text["not_checked"].format(reason=text["reasons"][report["reason"]]))
        return "\n".join(lines)
    seats = ", ".join(r["seat"] for r in report["reports"] if r["input_sha256"] is not None)
    lines.append(text["coverage"].format(seats=seats, state=text["states"][report["status"]]))
    problems = [text["report_problems"][p["kind"]].format(seat=r["seat"], block=p.get("block"))
                for r in report["reports"] for p in r["problems"]]
    problems += [text["item_problem"].format(seat=p["seat"], index=p["index"],
                                             why=text["item_reasons"][p["reason"]])
                 for p in report["item_problems"]]
    if problems:
        lines.append(text["unread"])
        lines += problems
    if not report["items"]:
        lines.append(text["none_read"] if problems else text["none"])
        return "\n".join(lines)
    lines += ["", text["header"], "|---|---|---|---|"]
    lines += [f"| {_cell(i['seat'])} | {i['index']} | {_reference(i)} | {text['results'][i['result']]} |"
              for i in report["items"]]
    lines += ["", text["note"]]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _report_arg(value: str) -> tuple[str, Path]:
    seat, sep, path = value.partition("=")
    if not sep or not path or not _SEAT_RE.match(seat):
        raise argparse.ArgumentTypeError(
            f"expected SEAT=PATH with a seat label of letters, digits, '_' or '-', got {value!r}")
    return seat, Path(path)


def main(argv: list[str] | None = None,
         clients_factory: Callable[[], dict[str, Any]] = _real_clients) -> int:
    parser = argparse.ArgumentParser(description="Check the references a review panel suggests (#1001).")
    parser.add_argument("--report", type=_report_arg, action="append", required=True,
                        metavar="SEAT=PATH", help="A saved reviewer report, such as R2=r2.md. Repeatable.")
    parser.add_argument("--lang", choices=LANGS, default="en", help="Language of the Markdown report.")
    parser.add_argument("--json-out", type=Path, help="Write the JSON report to this file.")
    args = parser.parse_args(argv)
    if args.json_out and any(_same_file(args.json_out, path) for _seat, path in args.report):
        parser.error("--json-out may not be one of the report files")
    report = build_report(args.report, clients_factory)
    if args.json_out:
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(render(report, args.lang))
    return 2 if report["status"] == "not_checked" else 0


def _same_file(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve() or a.samefile(b)
    except OSError:
        return False


if __name__ == "__main__":
    sys.exit(main())
