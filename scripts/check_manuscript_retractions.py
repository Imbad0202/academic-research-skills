#!/usr/bin/env python3
"""Opt-in advisory retraction check for references cited in a manuscript (#1108).

Two-step workflow so unpublished manuscripts never trigger silent network calls:

  list   Read ``--manuscript`` (sends nothing), extract DOIs with 1-based line
         numbers, and write them to a NEW ``--out`` file for the user to inspect
         and edit. Refuses an existing or uncheckable ``--out`` path BEFORE
         reading the manuscript, and writes via a sibling temp file + atomic
         link so an interrupt never leaves a partial list file.
  check  Read the user-reviewed ``--list`` file, send ONLY the DOIs left in that
         file to OpenAlex (``openalex_client.py``) and Crossref
         (``crossref_client.py``), resolve each with ``retraction_status.py``,
         and print the Markdown attachment (``--lang en|zh-TW``) plus optional
         ``--json-out``.

List-file rules (same in code and docs):
- Blank lines and lines whose first non-whitespace character is ``#`` are
  ignored and not counted.
- Every other line is read as ``<doi>[<tab or whitespace><location>]`` or
  counted as an invalid line.
- When a location starts with ``line `` or ``lines `` followed by numbers, each
  line number must be a positive integer of 1 to 9 digits (``1``..``999999999``).
  A 10+ digit number or ``0`` marks that list line invalid.

Verdict rules:
- Unknown status stays unknown; a missing ``is_retracted`` flag is never
  treated as ``not_retracted``.
- When Crossref returns no record (HTTP 404) AND OpenAlex returns a verdict,
  the result rests on OpenAlex alone and EVERY such DOI is listed explicitly
  in the report (not only a bare count).
- A retracted (or disputed) hit names where the manuscript cites that work so
  the author can judge the effect; this check never decides the effect and
  never alters the editorial decision, consensus counts, or Revision Roadmap.
- References without a DOI are not checked.
- Lookups run live and do not read or write any retraction cache.

Exit 0: ``list`` wrote the file, or ``check`` read the list and wrote a report
(status ``checked`` or ``partial``).
Exit 2: ``STOP: ...`` on stderr (``not_checked``).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

try:
    from crossref_client import CrossrefClient, CrossrefUnavailable
    from openalex_client import OpenAlexClient, OpenAlexUnavailable, _FIELDS as _OA_FIELDS
    from retraction_status import (
        CACHE_REVALIDATE_DAYS,
        normalize_doi,
        resolve_retraction_signal,
    )
except ImportError:  # pragma: no cover - dual-path import
    from scripts.crossref_client import CrossrefClient, CrossrefUnavailable
    from scripts.openalex_client import OpenAlexClient, OpenAlexUnavailable, _FIELDS as _OA_FIELDS
    from scripts.retraction_status import (
        CACHE_REVALIDATE_DAYS,
        normalize_doi,
        resolve_retraction_signal,
    )

CHECKER = "check_manuscript_retractions/1"
LANGS = ("en", "zh-TW")
MAX_LINE_NUMBER = 999_999_999  # 9-digit limit
_LINE_NUM_RE = re.compile(r"^[1-9][0-9]{0,8}$")
_LINES_SPEC_RE = re.compile(r"^lines?\s+(.+)$", re.IGNORECASE)
_DIGITS_LIST_RE = re.compile(r"^[0-9,\s]+$")
_DOI_CANDIDATE_RE = re.compile(
    r"(?:https?://(?:dx\.)?doi\.org/|doi:\s*)?(10\.[0-9]{4,9}/[^\s<>\"{}|\\^`\[\]]+)",
    re.IGNORECASE,
)
_MD_SPECIAL = re.compile(r"([\\`*_\[\]|~])")


class Stop(Exception):
    """Unrecoverable setup/I/O error; exits with status 2."""


_TEXT: dict[str, dict[str, Any]] = {
    "en": {
        "title": "Retraction check (opt-in script output, not a reviewer finding; #1108)",
        "not_checked": "Not checked: {reason}.",
        "coverage": "DOIs checked: {checked} ({state}). Retracted: {retracted}; disputed: {disputed}; reinstated: {reinstated}; not retracted: {not_retracted}; unknown: {unknown}.",
        "states": {"checked": "complete", "partial": "partial"},
        "invalid_header": "Not read (invalid lines in list — blank lines and `#` comments are ignored; every other line is counted):",
        "invalid_reasons": {
            "invalid_doi": "not a valid DOI",
            "invalid_line_number": "line number must be 1 to 9 digits (1-999999999)",
        },
        "invalid_row": "- line {line}: {reason} (`{text}`).",
        "none": "No DOIs were listed to check. References without a DOI are not checked.",
        "none_valid": "No valid DOI could be read from the list. References without a DOI are not checked.",
        "retracted_heading": "Retracted DOIs (verify how the manuscript relies on each work):",
        "disputed_heading": "Disputed DOIs (OpenAlex and Crossref disagree):",
        "reinstated_heading": "Reinstated DOIs (previously retracted, later reinstated):",
        "table_header": "| DOI | Manuscript location | OpenAlex | Crossref | Event date |",
        "oa_only_heading": "OpenAlex-only verdicts (Crossref returned no record; expected for DataCite DOIs such as arXiv or Zenodo, or an unregistered DOI — {count} DOI(s)):",
        "single_resolver_heading": "Single-resolver verdicts (one index did not settle the DOI — {count} DOI(s)):",
        "unknown_heading": "Unknown status (neither OpenAlex nor Crossref settled the DOI — {count} DOI(s)):",
        "verdicts": {
            "retracted": "retracted",
            "not_retracted": "not retracted",
            "reinstated": "reinstated",
            "disputed": "disputed",
            "unknown": "unknown",
        },
        "resolver_detail": {
            "degraded": "unavailable/degraded",
            "no_record": "no record",
            "missing_flag": "flag missing",
        },
        "no_location": "(location not given)",
        "note": (
            "A retracted hit names where the manuscript cites that work so the author can judge the effect; "
            "this check does not decide the effect and does not change the decision, consensus counts, or Revision Roadmap. "
            "Unknown status stays unknown; a missing flag is not \"not retracted\". "
            "References without a DOI are not checked."
        ),
    },
    "zh-TW": {
        "title": "撤稿狀態查核（選擇性啟用之腳本輸出，不是審稿意見；#1108）",
        "not_checked": "未檢查：{reason}。",
        "coverage": "已查 DOI：{checked} 筆（{state}）。已撤稿：{retracted}；索引分歧：{disputed}；已恢復：{reinstated}；未見撤稿：{not_retracted}；狀態不明：{unknown}。",
        "states": {"checked": "完整", "partial": "部分"},
        "invalid_header": "未讀取（清單中的無效行——空白行與 `#` 註解行會略過不計，其餘每一行皆計入）：",
        "invalid_reasons": {
            "invalid_doi": "不是有效的 DOI",
            "invalid_line_number": "行號須為 1 至 9 位正整數（1-999999999）",
        },
        "invalid_row": "- 第 {line} 行：{reason}（`{text}`）。",
        "none": "清單中沒有待查的 DOI。沒有 DOI 的參考文獻不在此查核範圍內。",
        "none_valid": "清單中沒有讀到任何有效的 DOI。沒有 DOI 的參考文獻不在此查核範圍內。",
        "retracted_heading": "已撤稿 DOI（請作者確認稿件如何依賴這些文獻）：",
        "disputed_heading": "索引分歧 DOI（OpenAlex 與 Crossref 結果不一致）：",
        "reinstated_heading": "已恢復 DOI（曾撤稿但後來恢復）：",
        "table_header": "| DOI | 稿件位置 | OpenAlex | Crossref | 事件日期 |",
        "oa_only_heading": "僅依 OpenAlex 判定（Crossref 查無紀錄；arXiv 或 Zenodo 等 DataCite DOI 或未登錄 DOI 常見此情形——共 {count} 筆）：",
        "single_resolver_heading": "僅單一索引判定（另一索引未給出判定——共 {count} 筆）：",
        "unknown_heading": "狀態不明（OpenAlex 與 Crossref 皆未給出判定——共 {count} 筆）：",
        "verdicts": {
            "retracted": "已撤稿",
            "not_retracted": "未見撤稿",
            "reinstated": "已恢復",
            "disputed": "分歧",
            "unknown": "不明",
        },
        "resolver_detail": {
            "degraded": "索引無法使用",
            "no_record": "查無紀錄",
            "missing_flag": "缺少撤稿旗標",
        },
        "no_location": "（未提供位置）",
        "note": (
            "已撤稿項目會標出稿件引用該文獻的位置，供作者自行評估影響；"
            "此查核不判斷影響，也不改變審稿決定、共識計數或修訂路線圖。"
            "狀態不明維持不明；缺少旗標不等於「未撤稿」。"
            "沒有 DOI 的參考文獻不在此查核範圍內。"
        ),
    },
}


# ---------------------------------------------------------------------------
# Step 1: Extract DOIs from manuscript & write new list file atomically.
# ---------------------------------------------------------------------------


def _trim_doi_candidate(raw: str) -> str:
    """Strip trailing prose punctuation while preserving balanced parentheses."""
    s = raw
    while s:
        last = s[-1]
        if last in ".,;:'\"!?":
            s = s[:-1]
        elif last == ")" and s.count(")") > s.count("("):
            s = s[:-1]
        elif last == "]" and s.count("]") > s.count("["):
            s = s[:-1]
        elif last == "}" and s.count("}") > s.count("{"):
            s = s[:-1]
        else:
            break
    return s


def extract_dois(text: str) -> list[dict[str, Any]]:
    """Extract unique normalized DOIs with 1-based manuscript line numbers."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    by_doi: dict[str, list[int]] = {}
    order: list[str] = []
    for lineno, line in enumerate(lines, start=1):
        if lineno > MAX_LINE_NUMBER:
            raise Stop(f"manuscript exceeds {MAX_LINE_NUMBER} lines")
        for match in _DOI_CANDIDATE_RE.finditer(line):
            cleaned = _trim_doi_candidate(match.group(1))
            doi = normalize_doi(cleaned)
            if not doi:
                continue
            if doi not in by_doi:
                by_doi[doi] = [lineno]
                order.append(doi)
            elif by_doi[doi][-1] != lineno:
                by_doi[doi].append(lineno)
    return [{"doi": doi, "lines": by_doi[doi]} for doi in order]


def format_list_file(entries: list[dict[str, Any]]) -> str:
    """Render the editable DOI list file."""
    out = [
        "# Advisory retraction check DOI list (#1108)",
        "# Delete any DOI you do not want sent to OpenAlex and Crossref.",
        "# One DOI per line; optional location or claim note after a tab (e.g. lines 12, 45).",
        "# Blank lines and lines starting with # are ignored. Every other line is read or counted as invalid.",
    ]
    if not entries:
        out.append("# No DOIs found in the manuscript.")
    for entry in entries:
        loc = "lines " + ", ".join(str(n) for n in entry["lines"])
        out.append(f"{entry['doi']}\t{loc}")
    return "\n".join(out) + "\n"


def _check_new_output_path(out_path: Path) -> None:
    """Refuse an existing or uncheckable output path BEFORE reading the manuscript."""
    try:
        os.lstat(out_path)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise Stop(f"cannot check output path {out_path}: {exc}") from exc
    raise Stop(f"output file already exists: {out_path}")


def _write_new_file_atomic(out_path: Path, content: str) -> None:
    """Write ``content`` to a new file without leaving a partial file on interrupt."""
    parent = out_path.parent
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=parent,
            prefix=".ars-retraction-list-",
            suffix=".tmp",
            delete=False,
        ) as handle:
            tmp_path = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(tmp_path, out_path)
    except FileExistsError as exc:
        raise Stop(f"output file already exists: {out_path}") from exc
    except OSError as exc:
        raise Stop(f"cannot write output file {out_path}: {exc}") from exc
    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def run_list(manuscript: Path, out_path: Path) -> int:
    """Step 1: extract DOIs from manuscript into a new list file (sends nothing)."""
    _check_new_output_path(out_path)
    try:
        text = manuscript.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Stop(f"cannot read manuscript {manuscript}: {exc}") from exc
    entries = extract_dois(text)
    _write_new_file_atomic(out_path, format_list_file(entries))
    print(f"Wrote {len(entries)} DOI(s) to {out_path}. Review and edit before running `check`.")
    return 0


# ---------------------------------------------------------------------------
# Step 2: Parse user-reviewed list file & query OpenAlex + Crossref.
# ---------------------------------------------------------------------------


def _parse_location(note: str) -> tuple[str | None, str | None]:
    """Validate optional location note.

    Returns ``(normalized_location, error_reason)``. If ``note`` has the form
    ``line(s) <numbers>``, every number must be a 1-to-9-digit positive integer.
    Any other freeform note (e.g. ``Section 2, Claim 1``) is preserved as-is.
    """
    note = note.strip()
    if not note:
        return None, None
    m = _LINES_SPEC_RE.match(note)
    if m and _DIGITS_LIST_RE.match(m.group(1)):
        raw_nums = [tok for tok in re.split(r"[,\s]+", m.group(1).strip()) if tok]
        if not raw_nums or any(not _LINE_NUM_RE.match(tok) for tok in raw_nums):
            return None, "invalid_line_number"
        nums = sorted({int(tok) for tok in raw_nums})
        prefix = "line" if len(nums) == 1 else "lines"
        return f"{prefix} " + ", ".join(str(n) for n in nums), None
    return note, None


def parse_list_text(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse the DOI list file.

    Blank lines and ``#`` comment lines are ignored and not counted.
    Every other line is parsed as a DOI entry or recorded in ``invalid_lines``.
    """
    items: list[dict[str, Any]] = []
    by_doi: dict[str, dict[str, Any]] = {}
    invalid_lines: list[dict[str, Any]] = []
    for lineno, raw_line in enumerate(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "\t" in stripped:
            raw_doi, note = stripped.split("\t", 1)
        else:
            parts = stripped.split(None, 1)
            raw_doi = parts[0]
            note = parts[1] if len(parts) > 1 else ""
        doi = normalize_doi(raw_doi)
        if doi is None:
            invalid_lines.append({"line": lineno, "text": stripped, "reason": "invalid_doi"})
            continue
        location, loc_err = _parse_location(note)
        if loc_err is not None:
            invalid_lines.append({"line": lineno, "text": stripped, "reason": loc_err})
            continue
        if doi in by_doi:
            if location and location not in by_doi[doi]["locations"]:
                by_doi[doi]["locations"].append(location)
        else:
            entry = {"doi": doi, "locations": [location] if location else []}
            by_doi[doi] = entry
            items.append(entry)
    return items, invalid_lines


def _default_clients() -> tuple[Any, Any]:
    return OpenAlexClient(), CrossrefClient()


def _query_openalex(client: Any, doi: str) -> tuple[dict[str, Any], str]:
    """Return ``(envelope, detail)`` where detail is ``ok``, ``no_record``, ``missing_flag``, or ``degraded``."""
    quoted = urllib.parse.quote(doi, safe="")
    try:
        data = client._get(f"/works/doi:{quoted}", {"select": _OA_FIELDS})
    except (OpenAlexUnavailable, Exception):
        return {"status": "degraded"}, "degraded"
    if not isinstance(data, dict) or not data:
        return {"status": "checked", "record": {}}, "no_record"
    if not isinstance(data.get("is_retracted"), bool):
        return {"status": "checked", "record": data}, "missing_flag"
    return {"status": "checked", "record": data}, "ok"


def _query_crossref(client: Any, doi: str) -> tuple[dict[str, Any], str]:
    """Return ``(envelope, detail)`` where detail is ``ok``, ``no_record``, or ``degraded``."""
    quoted = urllib.parse.quote(doi, safe="")
    try:
        data = client._get(f"/works/{quoted}", {})
    except (CrossrefUnavailable, Exception):
        return {"status": "degraded"}, "degraded"
    message = data.get("message") if isinstance(data, dict) else None
    if not isinstance(message, dict) or not message:
        return {"status": "checked", "records": []}, "no_record"
    return {"status": "checked", "records": [message]}, "ok"


def build_report(
    list_path: Path,
    clients_factory: Callable[[], tuple[Any, Any]] = _default_clients,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Read ``list_path``, look up each DOI live, and build the structured report."""
    report: dict[str, Any] = {
        "checker": CHECKER,
        "status": "not_checked",
        "list_path": str(list_path),
        "list_sha256": None,
        "items": [],
        "invalid_lines": [],
    }
    try:
        raw = list_path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report["reason"] = f"cannot read list file: {exc}"
        return report
    report["list_sha256"] = hashlib.sha256(raw).hexdigest()
    parsed_items, invalid_lines = parse_list_text(text)
    report["invalid_lines"] = invalid_lines

    if not parsed_items:
        report["status"] = "partial" if invalid_lines else "checked"
        return report

    oa_client, cr_client = clients_factory()
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    checked_at = current.strftime("%Y-%m-%dT%H:%M:%SZ")
    stale_after = (current + timedelta(days=CACHE_REVALIDATE_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")

    any_degraded_or_unknown = False
    for idx, item in enumerate(parsed_items, start=1):
        doi = item["doi"]
        oa_env, oa_detail = _query_openalex(oa_client, doi)
        cr_env, cr_detail = _query_crossref(cr_client, doi)
        signal = resolve_retraction_signal(
            {"citation_key": f"manuscript-doi-{idx}", "doi": doi},
            openalex=oa_env,
            crossref=cr_env,
            checked_at=checked_at,
            recorded_at=checked_at,
            stale_after=stale_after,
        )
        ctx = signal["retraction_context"]
        obs = {o["resolver"]: o for o in ctx["resolver_observations"]}
        oa_obs = obs["OpenAlex"]
        cr_obs = obs["Crossref"]
        oa_only_no_cr = (cr_detail == "no_record" and oa_obs["verdict"] != "unknown")
        if oa_detail == "degraded" or cr_detail == "degraded" or ctx["effective_status"] == "unknown":
            any_degraded_or_unknown = True
        report["items"].append({
            "doi": doi,
            "locations": item["locations"],
            "effective_status": ctx["effective_status"],
            "resolver_agreement": ctx["resolver_agreement"],
            "retraction_event_date": ctx["retraction_event_date"],
            "openalex": {"status": oa_obs["status"], "verdict": oa_obs["verdict"], "detail": oa_detail},
            "crossref": {"status": cr_obs["status"], "verdict": cr_obs["verdict"], "detail": cr_detail},
            "openalex_only_no_crossref": oa_only_no_cr,
        })

    report["status"] = "partial" if (invalid_lines or any_degraded_or_unknown) else "checked"
    return report


# ---------------------------------------------------------------------------
# Rendering.
# ---------------------------------------------------------------------------


def _cell(text: str) -> str:
    """Escape untrusted text for literal Markdown table/list rendering."""
    cleaned = " ".join(text.split())
    cleaned = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return _MD_SPECIAL.sub(r"\\\1", cleaned)


def _loc_str(item: dict[str, Any], t: dict[str, Any]) -> str:
    return _cell("; ".join(item["locations"])) if item["locations"] else t["no_location"]


def _resolver_cell(side: dict[str, Any], t: dict[str, Any]) -> str:
    if side["verdict"] != "unknown":
        return t["verdicts"][side["verdict"]]
    detail = side.get("detail")
    if detail in t["resolver_detail"]:
        return f"{t['verdicts']['unknown']} ({t['resolver_detail'][detail]})"
    return t["verdicts"]["unknown"]


def _render_table(rows: list[dict[str, Any]], heading: str, t: dict[str, Any]) -> list[str]:
    out = ["", heading, "", t["table_header"], "|---|---|---|---|---|"]
    for item in rows:
        date = _cell(item["retraction_event_date"]) if item["retraction_event_date"] else "—"
        out.append(
            f"| `{_cell(item['doi'])}` | {_loc_str(item, t)} | "
            f"{_resolver_cell(item['openalex'], t)} | {_resolver_cell(item['crossref'], t)} | {date} |"
        )
    return out


def render(report: dict[str, Any], lang: str = "en") -> str:
    t = _TEXT[lang]
    lines = [t["title"]]
    if report["status"] == "not_checked":
        lines.append(t["not_checked"].format(reason=_cell(report.get("reason", "unknown error"))))
        return "\n".join(lines)

    items = report["items"]
    invalid = report["invalid_lines"]
    counts = {k: sum(1 for i in items if i["effective_status"] == k)
              for k in ("retracted", "disputed", "reinstated", "not_retracted", "unknown")}

    if items:
        lines.append(t["coverage"].format(
            checked=len(items),
            state=t["states"][report["status"]],
            **counts,
        ))
    if invalid:
        lines.append(t["invalid_header"])
        for err in invalid:
            lines.append(t["invalid_row"].format(
                line=err["line"],
                reason=t["invalid_reasons"][err["reason"]],
                text=_cell(err["text"]),
            ))
    if not items:
        lines.append(t["none_valid"] if invalid else t["none"])
        return "\n".join(lines)

    retracted = [i for i in items if i["effective_status"] == "retracted"]
    disputed = [i for i in items if i["effective_status"] == "disputed"]
    reinstated = [i for i in items if i["effective_status"] == "reinstated"]
    oa_only_no_cr = [i for i in items if i["openalex_only_no_crossref"]]
    single_other = [
        i for i in items
        if i["effective_status"] != "unknown"
        and i["resolver_agreement"] == "partial"
        and not i["openalex_only_no_crossref"]
    ]
    unknown = [i for i in items if i["effective_status"] == "unknown"]

    if retracted:
        lines += _render_table(retracted, t["retracted_heading"], t)
    if disputed:
        lines += _render_table(disputed, t["disputed_heading"], t)
    if reinstated:
        lines += _render_table(reinstated, t["reinstated_heading"], t)
    if oa_only_no_cr:
        lines += ["", t["oa_only_heading"].format(count=len(oa_only_no_cr))]
        for item in oa_only_no_cr:
            lines.append(
                f"- `{_cell(item['doi'])}` ({_loc_str(item, t)}): "
                f"OpenAlex={_resolver_cell(item['openalex'], t)}, Crossref={_resolver_cell(item['crossref'], t)}"
            )
    if single_other:
        lines += ["", t["single_resolver_heading"].format(count=len(single_other))]
        for item in single_other:
            lines.append(
                f"- `{_cell(item['doi'])}` ({_loc_str(item, t)}): "
                f"OpenAlex={_resolver_cell(item['openalex'], t)}, Crossref={_resolver_cell(item['crossref'], t)}"
            )
    if unknown:
        lines += ["", t["unknown_heading"].format(count=len(unknown))]
        for item in unknown:
            lines.append(
                f"- `{_cell(item['doi'])}` ({_loc_str(item, t)}): "
                f"OpenAlex={_resolver_cell(item['openalex'], t)}, Crossref={_resolver_cell(item['crossref'], t)}"
            )

    lines += ["", t["note"]]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _same_file(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve() or a.samefile(b)
    except OSError:
        return False


def main(
    argv: list[str] | None = None,
    clients_factory: Callable[[], tuple[Any, Any]] = _default_clients,
) -> int:
    parser = argparse.ArgumentParser(
        description="Opt-in advisory retraction check for cited manuscript DOIs (#1108)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="Extract manuscript DOIs into a new editable file (sends nothing).")
    p_list.add_argument("--manuscript", type=Path, required=True, help="Reviewed manuscript file.")
    p_list.add_argument("--out", type=Path, required=True, help="New file to write the DOI list to.")

    p_check = sub.add_parser("check", help="Look up only the DOIs in the user-reviewed list file.")
    p_check.add_argument("--list", dest="list_path", type=Path, required=True, help="User-reviewed DOI list file.")
    p_check.add_argument("--lang", choices=LANGS, default="en", help="Language of the Markdown report.")
    p_check.add_argument("--json-out", type=Path, help="Optional JSON report output path.")

    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            return run_list(args.manuscript, args.out)
        if args.json_out and _same_file(args.json_out, args.list_path):
            parser.error("--json-out may not be the list file")
        report = build_report(args.list_path, clients_factory)
        if report["status"] == "not_checked":
            print(f"STOP: {report['reason']}", file=sys.stderr)
            print(render(report, args.lang))
            return 2
        if args.json_out:
            args.json_out.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        print(render(report, args.lang))
        return 0
    except Stop as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
