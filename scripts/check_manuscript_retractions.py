#!/usr/bin/env python3
"""Opt-in advisory retraction check for the DOIs a reviewed manuscript cites (#1108).

Two steps, so nothing from an unpublished manuscript is sent anywhere before
the user has seen and edited what would be sent:

  list   Read ``--manuscript`` (no network), find its DOIs, and write each one
         with its manuscript lines to a NEW file named by ``--out``. The
         output file is created exclusively (``open(..., "x")``) BEFORE the
         manuscript is read, which is the destination check; an existing path
         is never touched. If anything fails after the file is created
         (reading the manuscript or writing), that new file is removed.
  check  Read the edited ``--list`` file and look up ONLY the DOIs left in it
         with OpenAlex (``openalex_client.py``) and Crossref
         (``crossref_client.py``), through ``retraction_status.py``. Lookups
         run live, one after another, and read or write no cache.

List file: blank lines and lines starting with ``#`` are ignored. Every other
line is ``<doi>`` or ``<doi><TAB or spaces><location note>``; a line that does
not start with a DOI is reported as not read.

Rules the report keeps:
- Unknown stays unknown. A missing ``is_retracted`` flag, an unavailable index,
  or no record anywhere is never read as "not retracted".
- When Crossref has no record and OpenAlex gives a verdict, the verdict rests
  on OpenAlex alone; every such DOI is listed with its manuscript location.
- A retracted or disputed DOI is listed with the manuscript location, so the
  author can judge the effect. The script does not decide the effect.
- References without a DOI are not checked.

Exit 0: the step finished (``check`` may report partial coverage).
Exit 2: ``STOP: ...`` on stderr; nothing was checked or written.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

try:
    from crossref_client import CrossrefClient, CrossrefUnavailable
    from openalex_client import OpenAlexClient, OpenAlexUnavailable, _FIELDS as _OA_FIELDS
    from retraction_status import CACHE_REVALIDATE_DAYS, normalize_doi, resolve_retraction_signal
except ImportError:  # pragma: no cover - namespace import
    from scripts.crossref_client import CrossrefClient, CrossrefUnavailable
    from scripts.openalex_client import OpenAlexClient, OpenAlexUnavailable, _FIELDS as _OA_FIELDS
    from scripts.retraction_status import (
        CACHE_REVALIDATE_DAYS,
        normalize_doi,
        resolve_retraction_signal,
    )

LANGS = ("en", "zh-TW")
_DOI_RE = re.compile(
    r"(?:https?://(?:dx\.)?doi\.org/|doi:\s*)?(10\.[0-9]{4,9}/[^\s<>\"{}|\\^`\[\]]+)",
    re.IGNORECASE,
)
_MD_SPECIAL = re.compile(r"([\\`*_\[\]|~])")
_STATUSES = ("retracted", "disputed", "reinstated", "not_retracted", "unknown")


class Stop(Exception):
    """Unrecoverable setup or I/O problem; the script exits 2."""


_TEXT: dict[str, dict[str, Any]] = {
    "en": {
        "title": "Retraction check (opt-in script output, not a reviewer finding; #1108)",
        "coverage": "DOIs checked: {n} ({state}). Retracted: {retracted}; disputed: {disputed}; reinstated: {reinstated}; not retracted: {not_retracted}; unknown: {unknown}.",
        "state": {"checked": "complete", "partial": "partial"},
        "invalid": "Not read (a line that is not blank, not a `#` comment, and does not start with a DOI):",
        "invalid_row": "- list line {line}: `{text}`",
        "none": "No DOIs were listed to check.",
        "retracted": "Retracted (check how the manuscript relies on each work):",
        "disputed": "Disputed (OpenAlex and Crossref disagree):",
        "reinstated": "Reinstated (retracted earlier, reinstated later):",
        "oa_only": "OpenAlex-only verdicts (Crossref has no record, as for many DataCite DOIs; {n} DOI(s)):",
        "unknown_head": "Unknown status (no index settled it; this is not \"not retracted\"; {n} DOI(s)):",
        "verdict": {"retracted": "retracted", "disputed": "disputed", "reinstated": "reinstated",
                    "not_retracted": "not retracted", "unknown": "unknown"},
        "detail": {"degraded": "unavailable", "no_record": "no record", "missing_flag": "flag missing"},
        "no_location": "location not given",
        "dated": "event date {date}",
        "note": (
            "This check names where the manuscript cites a retracted work so the author can judge the effect; "
            "it does not decide the effect and does not change the decision, consensus counts, or Revision Roadmap. "
            "References without a DOI are not checked."
        ),
    },
    "zh-TW": {
        "title": "撤稿狀態查核（選擇性啟用之腳本輸出，不是審稿意見；#1108）",
        "coverage": "已查 DOI：{n} 筆（{state}）。已撤稿：{retracted}；索引分歧：{disputed}；已恢復：{reinstated}；未見撤稿：{not_retracted}；狀態不明：{unknown}。",
        "state": {"checked": "完整", "partial": "部分"},
        "invalid": "未讀取（非空白、非 `#` 註解，且不以 DOI 開頭的行）：",
        "invalid_row": "- 清單第 {line} 行：`{text}`",
        "none": "清單中沒有待查的 DOI。",
        "retracted": "已撤稿（請確認稿件如何依賴這些文獻）：",
        "disputed": "索引分歧（OpenAlex 與 Crossref 結果不一致）：",
        "reinstated": "已恢復（曾撤稿，後來恢復）：",
        "oa_only": "僅依 OpenAlex 判定（Crossref 查無紀錄，DataCite DOI 常見此情形；共 {n} 筆）：",
        "unknown_head": "狀態不明（兩個索引都未給出判定；這不等於「未撤稿」；共 {n} 筆）：",
        "verdict": {"retracted": "已撤稿", "disputed": "分歧", "reinstated": "已恢復",
                    "not_retracted": "未見撤稿", "unknown": "不明"},
        "detail": {"degraded": "無法使用", "no_record": "查無紀錄", "missing_flag": "缺少旗標"},
        "no_location": "未提供位置",
        "dated": "事件日期 {date}",
        "note": (
            "此查核標出稿件引用已撤稿文獻的位置，供作者自行評估影響；"
            "不判斷影響，也不改變審稿決定、共識計數或修訂路線圖。"
            "沒有 DOI 的參考文獻不在此查核範圍內。"
        ),
    },
}


# ---------------------------------------------------------------------------
# list: manuscript -> new editable file
# ---------------------------------------------------------------------------


def _trim(raw: str) -> str:
    """Drop trailing prose punctuation, keeping brackets that are balanced."""
    pairs = {")": "(", "]": "[", "}": "{"}
    while raw:
        last = raw[-1]
        if last in ".,;:'\"!?" or (last in pairs and raw.count(last) > raw.count(pairs[last])):
            raw = raw[:-1]
        else:
            break
    return raw


def extract_dois(text: str) -> list[tuple[str, list[int]]]:
    """Return each distinct normalized DOI with its 1-based manuscript lines, in first-seen order."""
    found: dict[str, list[int]] = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in _DOI_RE.finditer(line):
            doi = normalize_doi(_trim(match.group(1)))
            if doi and lineno not in found.setdefault(doi, []):
                found[doi].append(lineno)
    return list(found.items())


def format_list(entries: list[tuple[str, list[int]]]) -> str:
    out = [
        "# DOIs found in the manuscript (#1108). Only the DOIs left in this file are sent to OpenAlex and Crossref.",
        "# Delete a line to keep its DOI out of the lookup. A note after the DOI (tab or spaces) is shown in the report.",
        "# Blank lines and lines starting with # are ignored.",
    ]
    if not entries:
        out.append("# No DOIs found in the manuscript.")
    out += [f"{doi}\tlines {', '.join(map(str, lines))}" for doi, lines in entries]
    return "\n".join(out) + "\n"


def run_list(manuscript: Path, out: Path) -> int:
    """Create ``out`` exclusively (this is the destination check), then read the manuscript and write.

    A refused path is reported before the manuscript is read, so it is never mistaken for "no DOI".
    An existing file is never opened for writing. Once the new file exists, any failure removes it.
    """
    try:
        handle = open(out, "x", encoding="utf-8", newline="\n")
    except FileExistsError:
        raise Stop(f"output file already exists: {out}") from None
    except OSError as exc:
        raise Stop(f"cannot create output file {out}: {exc}") from exc
    try:
        with handle:
            try:
                text = manuscript.read_bytes().decode("utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                raise Stop(f"cannot read manuscript {manuscript}: {exc}") from exc
            entries = extract_dois(text)
            handle.write(format_list(entries))
    except BaseException as exc:
        try:
            os.unlink(out)  # the file this call just created
        except OSError:
            pass
        if isinstance(exc, OSError):
            raise Stop(f"cannot write output file {out} (removed the new file): {exc}") from exc
        raise
    print(f"Wrote {len(entries)} DOI(s) to {out}. Review and edit the file before running `check`.")
    return 0


# ---------------------------------------------------------------------------
# check: edited list -> live lookups -> report
# ---------------------------------------------------------------------------


def parse_list(text: str) -> tuple[list[dict[str, Any]], list[tuple[int, str]]]:
    """Return ``(entries, invalid)``; entries are distinct DOIs with their location notes."""
    entries: dict[str, dict[str, Any]] = {}
    invalid: list[tuple[int, str]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        head, _, note = line.partition("\t") if "\t" in line else line.partition(" ")
        doi = normalize_doi(head)
        if doi is None:
            invalid.append((lineno, line))
            continue
        entry = entries.setdefault(doi, {"doi": doi, "locations": []})
        note = note.strip()
        if note and note not in entry["locations"]:
            entry["locations"].append(note)
    return list(entries.values()), invalid


def _openalex(client: Any, doi: str) -> tuple[dict[str, Any], str]:
    try:
        data = client._get(f"/works/doi:{urllib.parse.quote(doi, safe='')}", {"select": _OA_FIELDS})
    except (OpenAlexUnavailable, OSError, ValueError):
        return {"status": "degraded"}, "degraded"
    if not isinstance(data, dict) or not data:
        return {"status": "checked", "record": {}}, "no_record"
    if not isinstance(data.get("is_retracted"), bool):
        return {"status": "checked", "record": data}, "missing_flag"
    return {"status": "checked", "record": data}, "ok"


def _crossref(client: Any, doi: str) -> tuple[dict[str, Any], str]:
    try:
        data = client._get(f"/works/{urllib.parse.quote(doi, safe='')}", {})
    except (CrossrefUnavailable, OSError, ValueError):
        return {"status": "degraded"}, "degraded"
    message = data.get("message") if isinstance(data, dict) else None
    if not isinstance(message, dict) or not message:
        return {"status": "checked", "records": []}, "no_record"
    return {"status": "checked", "records": [message]}, "ok"


def build_report(
    list_path: Path,
    clients: Callable[[], tuple[Any, Any]] = lambda: (OpenAlexClient(), CrossrefClient()),
    now: datetime | None = None,
) -> dict[str, Any]:
    try:
        text = list_path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Stop(f"cannot read list file {list_path}: {exc}") from exc
    entries, invalid = parse_list(text)
    items: list[dict[str, Any]] = []
    if entries:
        oa_client, cr_client = clients()
        moment = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        stamp = moment.strftime("%Y-%m-%dT%H:%M:%SZ")
        stale = (moment + timedelta(days=CACHE_REVALIDATE_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for number, entry in enumerate(entries, start=1):
            oa_env, oa_detail = _openalex(oa_client, entry["doi"])
            cr_env, cr_detail = _crossref(cr_client, entry["doi"])
            signal = resolve_retraction_signal(
                {"citation_key": f"manuscript-doi-{number}", "doi": entry["doi"]},
                openalex=oa_env,
                crossref=cr_env,
                checked_at=stamp,
                recorded_at=stamp,
                stale_after=stale,
            )
            ctx = signal["retraction_context"]
            seen = {o["resolver"]: o["verdict"] for o in ctx["resolver_observations"]}
            items.append({
                "doi": entry["doi"],
                "locations": entry["locations"],
                "status": ctx["effective_status"],
                "event_date": ctx["retraction_event_date"],
                "openalex": {"verdict": seen["OpenAlex"], "detail": oa_detail},
                "crossref": {"verdict": seen["Crossref"], "detail": cr_detail},
                "openalex_only": cr_detail == "no_record" and seen["OpenAlex"] != "unknown",
            })
    partial = bool(invalid) or any(i["status"] == "unknown" for i in items)
    return {"state": "partial" if partial else "checked", "items": items, "invalid": invalid}


def _cell(value: str) -> str:
    """Escape untrusted text so it renders as literal Markdown."""
    value = " ".join(value.split()).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return _MD_SPECIAL.sub(r"\\\1", value)


def _side(side: dict[str, str], t: dict[str, Any]) -> str:
    text = t["verdict"][side["verdict"]]
    if side["verdict"] == "unknown" and side["detail"] in t["detail"]:
        text += f" ({t['detail'][side['detail']]})"
    return text


def _row(item: dict[str, Any], t: dict[str, Any]) -> str:
    where = _cell("; ".join(item["locations"])) if item["locations"] else t["no_location"]
    row = f"- `{_cell(item['doi'])}` ({where}): OpenAlex {_side(item['openalex'], t)}; Crossref {_side(item['crossref'], t)}"
    if item["event_date"]:
        row += "; " + t["dated"].format(date=_cell(item["event_date"]))
    return row + "."


def render(report: dict[str, Any], lang: str = "en") -> str:
    t = _TEXT[lang]
    items, invalid = report["items"], report["invalid"]
    lines = [t["title"]]
    if items:
        counts = {k: sum(1 for i in items if i["status"] == k) for k in _STATUSES}
        lines.append(t["coverage"].format(n=len(items), state=t["state"][report["state"]], **counts))
    else:
        lines.append(t["none"])
    if invalid:
        lines += ["", t["invalid"]] + [t["invalid_row"].format(line=n, text=_cell(s)) for n, s in invalid]
    groups = [
        (t["retracted"], [i for i in items if i["status"] == "retracted"]),
        (t["disputed"], [i for i in items if i["status"] == "disputed"]),
        (t["reinstated"], [i for i in items if i["status"] == "reinstated"]),
    ]
    oa_only = [i for i in items if i["openalex_only"]]
    unknown = [i for i in items if i["status"] == "unknown"]
    groups.append((t["oa_only"].format(n=len(oa_only)), oa_only))
    groups.append((t["unknown_head"].format(n=len(unknown)), unknown))
    for heading, rows in groups:
        if rows:
            lines += ["", heading] + [_row(i, t) for i in rows]
    return "\n".join(lines + ["", t["note"]])


def main(argv: list[str] | None = None, clients: Callable[[], tuple[Any, Any]] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Opt-in advisory retraction check for manuscript DOIs (#1108).")
    sub = parser.add_subparsers(dest="command", required=True)
    p_list = sub.add_parser("list", help="Write the manuscript's DOIs to a new editable file (no network).")
    p_list.add_argument("--manuscript", type=Path, required=True)
    p_list.add_argument("--out", type=Path, required=True, help="New file; must not exist yet.")
    p_check = sub.add_parser("check", help="Look up only the DOIs left in the edited list.")
    p_check.add_argument("--list", dest="list_path", type=Path, required=True)
    p_check.add_argument("--lang", choices=LANGS, default="en")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            return run_list(args.manuscript, args.out)
        kwargs = {"clients": clients} if clients else {}
        print(render(build_report(args.list_path, **kwargs), args.lang))
        return 0
    except Stop as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
