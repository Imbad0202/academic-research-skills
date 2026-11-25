#!/usr/bin/env python3
"""Opt-in advisory retraction check for the DOIs a reviewed manuscript cites (#1108).

Two steps, so nothing from an unpublished manuscript is sent anywhere before
the user has seen and edited what would be sent:

  list   Read ``--manuscript`` (no network), find its DOIs, and write each one
         with its manuscript lines to a NEW file named by ``--out``. The
         output file is created exclusively (``O_CREAT | O_EXCL``, mode 0600)
         BEFORE the manuscript is read, which is the destination check; an
         existing path is never touched, and ``--manuscript`` and ``--out``
         may not be the same path. If anything fails after the file is
         created (reading the manuscript or writing), the script removes that
         new file, and if the removal fails it says so and names the path
         that remains.
  check  Read the edited ``--list`` file and look up ONLY the DOIs left in it
         with OpenAlex (``openalex_client.py``) and Crossref
         (``crossref_client.py``), through ``retraction_status.py``. Lookups
         run live, one after another, and read or write no cache.

List file: blank lines and lines starting with ``#`` are ignored (a leading
byte order mark is dropped). Every other line is ``<doi>`` or
``<doi><whitespace><location note>``: the DOI is the first whitespace-free
field, and only that field is sent. A line whose first field is not a DOI is
reported by its line number only; its text is never copied into the report.

Rules the report keeps:
- Unknown stays unknown. A missing ``is_retracted`` flag, an unavailable or
  unreadable index, or no record anywhere is never read as "not retracted".
  When either index could not be read for a DOI, the run is partial and the
  row names that index.
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
# A DOI body stops at whitespace, markup characters, and CJK punctuation, full-width forms, kana,
# ideographs and hangul, so prose that follows a DOI in running CJK text is not read into it.
_DOI_BODY = r"[^\s<>\"{}|\\^`\[\]　-〿぀-ヿ㐀-䶿一-鿿가-힯＀-￯]+"
_DOI_RE = re.compile(
    r"(?P<url>https?://(?:dx\.)?doi\.org/)?(?:doi:\s*)?(?P<doi>10\.[0-9]{4,9}/" + _DOI_BODY + ")",
    re.IGNORECASE,
)
_DOI_FIELD = re.compile(r"10\.[0-9]{4,9}/" + _DOI_BODY)
_MD_SPECIAL = re.compile(r"([\\`*_\[\]|~])")
_STATUSES = ("retracted", "disputed", "reinstated", "not_retracted", "unknown")


class Stop(Exception):
    """Unrecoverable setup or I/O problem; the script exits 2."""


_TEXT: dict[str, dict[str, Any]] = {
    "en": {
        "title": "Retraction check (opt-in script output, not a reviewer finding; #1108)",
        "coverage": "DOIs checked: {n} ({state}). Retracted: {retracted}; disputed: {disputed}; reinstated: {reinstated}; not retracted: {not_retracted}; unknown: {unknown}.",
        "state": {"checked": "complete", "partial": "partial"},
        "invalid": "Not read (these list lines are not blank, not `#` comments, and do not start with a DOI; their text is not repeated here):",
        "invalid_row": "- list line {line}",
        "none": "No DOIs were listed to check.",
        "retracted": "Retracted (check how the manuscript relies on each work):",
        "disputed": "Disputed (OpenAlex and Crossref disagree, or one index reports conflicting retraction events):",
        "reinstated": "Reinstated (retracted earlier, reinstated later):",
        "oa_only": "OpenAlex-only verdicts (Crossref has no record, as for many DataCite DOIs; {n} DOI(s)):",
        "unknown_head": "Unknown status (no index settled it; this is not \"not retracted\"; {n} DOI(s)):",
        "degraded_head": "One index could not be read (the DOI was settled by the other index only; {n} DOI(s)):",
        "verdict": {"retracted": "retracted", "disputed": "disputed", "reinstated": "reinstated",
                    "not_retracted": "not retracted", "unknown": "unknown"},
        "detail": {"degraded": "unavailable or unreadable", "no_record": "no record", "missing_flag": "flag missing"},
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
        "invalid": "未讀取（這些清單行非空白、非 `#` 註解，且不以 DOI 開頭；報告不重複其內容）：",
        "invalid_row": "- 清單第 {line} 行",
        "none": "清單中沒有待查的 DOI。",
        "retracted": "已撤稿（請確認稿件如何依賴這些文獻）：",
        "disputed": "索引分歧（OpenAlex 與 Crossref 結果不一致，或單一索引內的撤稿事件互相矛盾）：",
        "reinstated": "已恢復（曾撤稿，後來恢復）：",
        "oa_only": "僅依 OpenAlex 判定（Crossref 查無紀錄，DataCite DOI 常見此情形；共 {n} 筆）：",
        "unknown_head": "狀態不明（兩個索引都未給出判定；這不等於「未撤稿」；共 {n} 筆）：",
        "degraded_head": "有一個索引無法讀取（僅依另一個索引判定；共 {n} 筆）：",
        "verdict": {"retracted": "已撤稿", "disputed": "分歧", "reinstated": "已恢復",
                    "not_retracted": "未見撤稿", "unknown": "不明"},
        "detail": {"degraded": "無法使用或無法讀取", "no_record": "查無紀錄", "missing_flag": "缺少旗標"},
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
            raw = match.group("doi")
            if match.group("url"):  # in a doi.org URL, a fragment or query is not part of the DOI
                raw = re.split(r"[#?]", raw, maxsplit=1)[0]
            doi = normalize_doi(_trim(raw))
            if doi and lineno not in found.setdefault(doi, []):
                found[doi].append(lineno)
    return list(found.items())


def format_list(entries: list[tuple[str, list[int]]]) -> str:
    out = [
        "# DOIs found in the manuscript (#1108). Only the DOIs left in this file are sent to OpenAlex and Crossref.",
        "# Delete a line to keep its DOI out of the lookup. A note after the DOI (whitespace) is shown in the report, never sent.",
        "# Blank lines and lines starting with # are ignored.",
    ]
    if not entries:
        out.append("# No DOIs found in the manuscript.")
    out += [f"{doi}\tlines {', '.join(map(str, lines))}" for doi, lines in entries]
    return "\n".join(out) + "\n"


def _same_path(a: Path, b: Path) -> bool:
    try:
        return os.path.normcase(a.resolve()) == os.path.normcase(b.resolve())
    except OSError:
        return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def _open_new(out: Path) -> Any:
    """Create ``out`` exclusively with mode 0600 and return a text handle. Raises if it exists."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    fd = os.open(out, flags, 0o600)
    try:
        return os.fdopen(fd, "w", encoding="utf-8", newline="\n")
    except BaseException:
        os.close(fd)
        raise


def _read_utf8(path: Path, what: str) -> str:
    """Read a UTF-8 file. Errors name the path and the failure, never the file's content."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise Stop(f"cannot read {what} {path}: {exc.strerror or type(exc).__name__}") from None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Stop(f"cannot read {what} {path}: not valid UTF-8 (error at byte {exc.start})") from None


def run_list(manuscript: Path, out: Path) -> int:
    """Create ``out`` exclusively (this is the destination check), then read the manuscript and write.

    A refused path is reported before the manuscript is read, so it is never mistaken for "no DOI".
    An existing file is never opened for writing. Once the new file exists, any failure removes it.
    """
    if _same_path(manuscript, out):
        raise Stop(f"--manuscript and --out are the same path: {out}")
    try:
        handle = _open_new(out)
    except FileExistsError:
        raise Stop(f"output file already exists: {out}") from None
    except OSError as exc:
        raise Stop(f"cannot create output file {out}: {exc}") from exc
    try:
        with handle:
            text = _read_utf8(manuscript, "manuscript")
            entries = extract_dois(text)
            handle.write(format_list(entries))
    except BaseException as exc:
        # Remove the file this call just created. Say so only if that worked.
        leftover: OSError | None = None
        try:
            os.unlink(out)
        except FileNotFoundError:
            pass
        except OSError as unlink_exc:
            leftover = unlink_exc
        if isinstance(exc, Stop):
            problem = str(exc)
        elif isinstance(exc, OSError):
            problem = f"cannot write output file {out}: {exc}"
        else:
            if leftover is not None:
                print(f"STOP: interrupted; the new file could not be removed and remains at {out}: {leftover}", file=sys.stderr)
            raise
        if leftover is None:
            raise Stop(problem + " (the new output file was removed)") from exc
        raise Stop(f"{problem}; the new output file could not be removed and remains at {out}: {leftover}") from exc
    print(f"Wrote {len(entries)} DOI(s) to {out}. Review and edit the file before running `check`.")
    return 0


# ---------------------------------------------------------------------------
# check: edited list -> live lookups -> report
# ---------------------------------------------------------------------------


def parse_list(text: str) -> tuple[list[dict[str, Any]], list[int]]:
    """Return ``(entries, invalid)``: distinct DOIs with their notes, and the numbers of unreadable lines.

    The DOI is the first whitespace-free field of a line and must be a whole DOI. The rest of the
    line is a note: it is shown in the report and never sent.
    """
    entries: dict[str, dict[str, Any]] = {}
    invalid: list[int] = []
    for lineno, raw in enumerate(text.removeprefix("﻿").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(None, 1)
        doi = normalize_doi(fields[0])
        if doi is None or not _DOI_FIELD.fullmatch(doi):
            invalid.append(lineno)
            continue
        entry = entries.setdefault(doi, {"doi": doi, "locations": []})
        note = fields[1].strip() if len(fields) > 1 else ""
        if note and note not in entry["locations"]:
            entry["locations"].append(note)
    return list(entries.values()), invalid


def _openalex(client: Any, doi: str) -> tuple[dict[str, Any], str]:
    try:
        data = client._get(f"/works/doi:{urllib.parse.quote(doi, safe='')}", {"select": _OA_FIELDS})
    except (OpenAlexUnavailable, OSError, ValueError):
        return {"status": "degraded"}, "degraded"
    if not isinstance(data, dict):  # an unreadable body is not "no record"
        return {"status": "degraded"}, "degraded"
    if not data:  # the client returns {} for a 404
        return {"status": "checked", "record": {}}, "no_record"
    if not isinstance(data.get("is_retracted"), bool):
        return {"status": "checked", "record": data}, "missing_flag"
    return {"status": "checked", "record": data}, "ok"


def _crossref(client: Any, doi: str) -> tuple[dict[str, Any], str]:
    try:
        data = client._get(f"/works/{urllib.parse.quote(doi, safe='')}", {})
    except (CrossrefUnavailable, OSError, ValueError):
        return {"status": "degraded"}, "degraded"
    if not isinstance(data, dict):  # an unreadable body is not "no record"
        return {"status": "degraded"}, "degraded"
    if not data:  # the client returns {} for a 404
        return {"status": "checked", "records": []}, "no_record"
    message = data.get("message")
    if not isinstance(message, dict) or not message:
        return {"status": "degraded"}, "degraded"
    return {"status": "checked", "records": [message]}, "ok"


def build_report(
    list_path: Path,
    clients: Callable[[], tuple[Any, Any]] = lambda: (OpenAlexClient(), CrossrefClient()),
    now: datetime | None = None,
) -> dict[str, Any]:
    entries, invalid = parse_list(_read_utf8(list_path, "list file"))
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
    partial = bool(invalid) or any(
        i["status"] == "unknown" or "degraded" in (i["openalex"]["detail"], i["crossref"]["detail"]) for i in items
    )
    return {"state": "partial" if partial else "checked", "items": items, "invalid": invalid}


def _cell(value: str) -> str:
    """Escape untrusted text so it renders as literal Markdown."""
    value = " ".join(value.split()).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return _MD_SPECIAL.sub(r"\\\1", value)


def _code(value: str) -> str:
    """Render text as a Markdown code span: no backslash escapes, a fence longer than any backtick run."""
    value = " ".join(value.split())
    longest = max((len(run) for run in re.findall(r"`+", value)), default=0)
    fence = "`" * (longest + 1)
    pad = " " if value.startswith("`") or value.endswith("`") else ""
    return f"{fence}{pad}{value}{pad}{fence}"


def _side(side: dict[str, str], t: dict[str, Any]) -> str:
    text = t["verdict"][side["verdict"]]
    if side["verdict"] == "unknown" and side["detail"] in t["detail"]:
        text += f" ({t['detail'][side['detail']]})"
    return text


def _row(item: dict[str, Any], t: dict[str, Any]) -> str:
    where = _cell("; ".join(item["locations"])) if item["locations"] else t["no_location"]
    row = f"- {_code(item['doi'])} ({where}): OpenAlex {_side(item['openalex'], t)}; Crossref {_side(item['crossref'], t)}"
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
        lines += ["", t["invalid"]] + [t["invalid_row"].format(line=n) for n in invalid]
    groups = [
        (t["retracted"], [i for i in items if i["status"] == "retracted"]),
        (t["disputed"], [i for i in items if i["status"] == "disputed"]),
        (t["reinstated"], [i for i in items if i["status"] == "reinstated"]),
    ]
    oa_only = [i for i in items if i["openalex_only"]]
    unknown = [i for i in items if i["status"] == "unknown"]
    # A degraded source is shown in the row of a retracted, disputed, or unknown DOI; for the rest it needs its own group.
    degraded = [
        i for i in items
        if i["status"] in ("not_retracted", "reinstated")
        and "degraded" in (i["openalex"]["detail"], i["crossref"]["detail"])
    ]
    groups.append((t["oa_only"].format(n=len(oa_only)), oa_only))
    groups.append((t["degraded_head"].format(n=len(degraded)), degraded))
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
