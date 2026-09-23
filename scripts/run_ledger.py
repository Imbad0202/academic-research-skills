#!/usr/bin/env python3
"""ARS pipeline run ledger (#887): write and check the handoff record.

The ledger is a peer file of the Material Passport, named
``<passport-stem>_run_ledger.yaml`` and kept beside it. It holds what context
compaction and subagent returns can drop: the user's initial instructions,
checkpoint questions and the user's exact answers, partly collected
multi-item answers, receipts for tool steps that report only on stdout or by
exit status, progress counters, and fingerprints of transient input files.
Design: docs/design/2026-09-23-887-handoff-integrity-design.md.
Entry schema: shared/contracts/passport/run_ledger.schema.json.

Usage:
    python3 scripts/run_ledger.py append --passport-path P --entry-file F
    python3 scripts/run_ledger.py report --passport-path P [--claims F]

``append`` validates one entry (a JSON object with ``kind`` and that kind's
fields), gives it the next ``seq``, the UTC time, the previous entry's hash,
and its own hash, and replaces the whole ledger atomically under the peer
lock that /ars-mark-read uses. It refuses to extend an unreadable ledger or
a broken chain, so a damaged record is never blessed by a later entry.

``report`` checks every hash, then compares the trusted entries with what a
summary or a subagent report claims (``--claims``, a JSON file). It prints
one JSON object carrying the four groups of the handoff check
(``awaiting_answer``, ``cannot_confirm``, ``not_run``, ``missing``) and
``backed``, the number of examined items the ledger supports, and the latest
counters grouped by stage ("run" when a progress entry names no stage). Exit
0 means there is nothing to report, 1 means the handoff check has items, and
2 means a usage or environment error.

What the hashes catch: an accidental change to any entry (each entry carries
its own hash) and a deleted entry that has a later entry (each entry carries
the previous entry's hash). What they do not catch: a lost tail, an edit
that recomputes the hashes, or an older copy of the whole file. They detect
accidental damage, not deliberate edits, and the orchestrator that writes the
entries can still write a false one; that failure stays R11's. The report is
deterministic only over what the ledger contains.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

try:  # Dual-path import: sibling module on sys.path vs package import.
    from ars_mark_read import LedgerLockError, _ledger_lock
    from human_read_attestation_resolver import _UniqueKeySafeLoader
except ImportError:  # pragma: no cover - package-import path
    from scripts.ars_mark_read import LedgerLockError, _ledger_lock  # type: ignore[no-redef]
    from scripts.human_read_attestation_resolver import (  # type: ignore[no-redef]
        _UniqueKeySafeLoader,
    )

LEDGER_FORMAT = "ars-run-ledger/1.0"
ERR_PREFIX = "[ARS-RUN-LEDGER ERROR:"

CHECKPOINT_TYPES = ("FULL", "SLIM", "MANDATORY")
RECEIPT_STATUSES = ("passed", "failed", "not_run")
WRITER_FIELDS = ("seq", "at", "prev_hash", "hash")
BASE_FIELDS = ("kind",) + WRITER_FIELDS
WORDS_MAX = 20000
TEXT_MAX = 4000
SHORT_MAX = 200
PATH_MAX = 4096
LIST_MAX = 50

_UTC_Z = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_COUNTER_NAME = re.compile(r"[a-z][a-z0-9_]{0,63}")

Check = Callable[[Any], "str | None"]


class LedgerUnreadable(Exception):
    """The ledger exists but cannot be read as a well-formed run ledger."""


class LedgerRefused(Exception):
    """The ledger or the new entry fails validation; nothing was written."""


def _err(msg: str) -> str:
    return f"{ERR_PREFIX} {msg}]"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ledger_path(passport_path: Path) -> Path:
    return passport_path.parent / f"{passport_path.stem}_run_ledger.yaml"


# ---------------------------------------------------------------------------
# Field checks. Each returns None when the value is valid, else a reason.
# ---------------------------------------------------------------------------


def _text(max_len: int) -> Check:
    def check(value: Any) -> str | None:
        if not isinstance(value, str) or not 1 <= len(value) <= max_len:
            return f"must be a string of 1-{max_len} characters"
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:  # a lone surrogate, e.g. from a \ud800 escape
            return "must be valid Unicode text"
        return None

    return check


def _enum(values: tuple[str, ...]) -> Check:
    def check(value: Any) -> str | None:
        return None if value in values else f"must be one of {', '.join(values)}"

    return check


def _count(value: Any) -> str | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return "must be a non-negative integer"
    return None


def _exit_status(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        return "must be an integer or null"
    return None


def _hex(length: int) -> Check:
    pattern = re.compile(f"[0-9a-f]{{{length}}}")

    def check(value: Any) -> str | None:
        if not isinstance(value, str) or not pattern.fullmatch(value):
            return f"must be {length} lowercase hexadecimal characters"
        return None

    return check


# One check per schema definition ($defs short, text, words; the inline path).
_short = _text(SHORT_MAX)
_long = _text(TEXT_MAX)
_words = _text(WORDS_MAX)
_path = _text(PATH_MAX)
_sha256 = _hex(64)
_boundary_hash = _hex(12)  # the reset_boundary[] entry hash format


def _short_list(value: Any) -> str | None:
    if not isinstance(value, list) or not 1 <= len(value) <= LIST_MAX:
        return f"must be a list of 1-{LIST_MAX} strings"
    if any(_short(item) for item in value):
        return f"items must be strings of 1-{SHORT_MAX} characters"
    return None


def _sha_map(value: Any) -> str | None:
    if not isinstance(value, dict) or not 1 <= len(value) <= LIST_MAX:
        return f"must be a mapping of 1-{LIST_MAX} paths to sha256 digests"
    for key, digest in value.items():
        if _path(key):
            return f"keys must be paths of 1-{PATH_MAX} characters"
        if _sha256(digest):
            return "values must be 64 lowercase hexadecimal characters"
    return None


def _counters(value: Any) -> str | None:
    if not isinstance(value, dict) or not 1 <= len(value) <= LIST_MAX:
        return f"must be a mapping of 1-{LIST_MAX} counter names to integers"
    for key, number in value.items():
        if not isinstance(key, str) or not _COUNTER_NAME.fullmatch(key):
            return "counter names must match [a-z][a-z0-9_]{0,63}"
        if _count(number):
            return "counter values must be non-negative integers"
    return None


# kind -> (required fields, optional fields); every other field is rejected.
# Keep in lockstep with shared/contracts/passport/run_ledger.schema.json.
FIELDS: dict[str, tuple[dict[str, Check], dict[str, Check]]] = {
    "initial_instructions": ({"user_words": _words}, {}),
    "checkpoint_opened": (
        {
            "checkpoint_id": _short,
            "stage": _short,
            "checkpoint_type": _enum(CHECKPOINT_TYPES),
            "question": _long,
        },
        {"options": _short_list, "reset_boundary_hash": _boundary_hash},
    ),
    "checkpoint_closed": (
        {"checkpoint_id": _short, "answer": _short, "user_words": _words},
        {},
    ),
    "partial_answer": (
        {"checkpoint_id": _short, "item_id": _short, "answer": _short, "user_words": _words},
        {},
    ),
    "tool_receipt": (
        {
            "step": _short,
            "command": _long,
            "status": _enum(RECEIPT_STATUSES),
            "exit_status": _exit_status,
            "retries_used": _count,
        },
        {"input_sha256": _sha_map, "output_sha256": _sha256, "gate_tokens": _short_list},
    ),
    "progress": ({"counters": _counters}, {"stage": _short}),
    "file_reference": ({"path": _path, "sha256": _sha256, "role": _short}, {}),
}
KINDS = tuple(FIELDS)


def _kind_field_errors(entry: dict[str, Any], *, extra_allowed: tuple[str, ...]) -> list[str]:
    kind = entry.get("kind")
    if not isinstance(kind, str) or kind not in FIELDS:
        return [f"kind must be one of {', '.join(KINDS)}"]
    required, optional = FIELDS[kind]
    errors = [f"{kind}: missing field {name}" for name in required if name not in entry]
    allowed = set(required) | set(optional) | set(extra_allowed) | {"kind"}
    errors += [f"{kind}: unknown field {name}" for name in entry if name not in allowed]
    for name, check in {**required, **optional}.items():
        if name in entry:
            problem = check(entry[name])
            if problem:
                errors.append(f"{kind}.{name} {problem}")
    return errors


def _stored_entry_ok(entry: Any, index: int, prev_hash: str | None) -> bool:
    """True when a stored entry is well formed and chained; hashed only if so."""
    return (
        isinstance(entry, dict)
        and all(name in entry for name in BASE_FIELDS)
        and not _kind_field_errors(entry, extra_allowed=BASE_FIELDS)
        and entry["seq"] == index and not isinstance(entry["seq"], bool)
        and isinstance(entry["at"], str) and _UTC_Z.fullmatch(entry["at"]) is not None
        and entry["prev_hash"] == prev_hash
        and entry["hash"] == entry_hash(entry)
    )


def entry_hash(entry: dict[str, Any]) -> str:
    """SHA-256 over the canonical JSON of the entry without its ``hash``.

    Callers hash only entries whose fields already validated, so every value
    is a JSON type; a hand-edited YAML timestamp or date never reaches here.
    """
    body = {key: value for key, value in entry.items() if key != "hash"}
    blob = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Reading and writing.
# ---------------------------------------------------------------------------


def load_ledger(path: Path) -> dict[str, Any] | None:
    """Return the parsed ledger, None when the file is absent.

    Raises LedgerUnreadable for undecodable bytes, invalid or duplicate-key
    YAML, or a top level that is not this format. Entry-level problems are
    left to first_untrusted_seq so that the entries before them stay usable.
    """
    if not path.exists():
        return None
    try:
        text = path.read_bytes().decode("utf-8")
        data = yaml.load(text, Loader=_UniqueKeySafeLoader)
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise LedgerUnreadable(f"cannot parse {path.name}: {exc}") from exc
    if (
        not isinstance(data, dict)
        or set(data) != {"ledger", "created_at", "entries"}
        or data["ledger"] != LEDGER_FORMAT
        or not isinstance(data["created_at"], str)
        or not _UTC_Z.fullmatch(data["created_at"])
        or not isinstance(data["entries"], list)
    ):
        raise LedgerUnreadable(
            f"{path.name} is not an {LEDGER_FORMAT} file "
            "(keys ledger, created_at, entries)"
        )
    return data


def first_untrusted_seq(entries: list[Any]) -> int | None:
    """Return the seq of the first entry that fails validation, or None.

    Every entry from that seq onward is untrusted: a broken chain fails closed
    from the break onward, and the entries before it stay usable.
    """
    prev_hash: str | None = None
    for index, entry in enumerate(entries, start=1):
        if not _stored_entry_ok(entry, index, prev_hash):
            return index
        prev_hash = entry["hash"]
    return None


def _write_atomic(path: Path, data: dict[str, Any]) -> None:
    """Replace the ledger from a same-directory temp file (never open "w")."""
    payload = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).encode("utf-8")
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def _state(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Fold trusted entries into the latest state per checkpoint, step, and file."""
    state: dict[str, Any] = {
        "opened": {}, "closed": {}, "partial": {}, "receipts": {},
        "counters": {}, "files": {},
    }
    for entry in entries:
        kind = entry["kind"]
        if kind == "checkpoint_opened":
            state["opened"][entry["checkpoint_id"]] = entry
        elif kind == "checkpoint_closed":
            state["closed"][entry["checkpoint_id"]] = entry
        elif kind == "partial_answer":
            state["partial"].setdefault(entry["checkpoint_id"], set()).add(entry["item_id"])
        elif kind == "tool_receipt":
            state["receipts"][entry["step"]] = entry
        elif kind == "progress":
            state["counters"].setdefault(entry.get("stage", "run"), {}).update(entry["counters"])
        elif kind == "file_reference":
            state["files"][entry["path"]] = entry
    return state


def _append_errors(entries: list[dict[str, Any]], fields: dict[str, Any]) -> list[str]:
    errors = [f"{name} is assigned by the writer" for name in WRITER_FIELDS if name in fields]
    errors = errors or _kind_field_errors(fields, extra_allowed=())
    if errors:
        return errors
    state = _state(entries)
    kind = fields["kind"]
    checkpoint = fields.get("checkpoint_id")
    if kind == "initial_instructions" and entries:
        errors.append("initial_instructions is allowed only as the first entry")
    if kind == "checkpoint_opened" and checkpoint in state["opened"]:
        errors.append(f"checkpoint_id {checkpoint!r} was already opened; use a new id")
    if kind in ("checkpoint_closed", "partial_answer") and (
        checkpoint not in state["opened"] or checkpoint in state["closed"]
    ):
        errors.append(f"checkpoint_id {checkpoint!r} is not an open checkpoint")
    return errors


def append_entry(
    passport_path: Path, fields: dict[str, Any], *, now: Callable[[], str] = _now_iso
) -> dict[str, Any]:
    """Validate and append one entry under the peer lock; return the entry."""
    path = ledger_path(passport_path)
    with _ledger_lock(path):
        data = load_ledger(path)
        if data is None:
            data = {"ledger": LEDGER_FORMAT, "created_at": now(), "entries": []}
        entries = data["entries"]
        broken = first_untrusted_seq(entries)
        if broken is not None:
            raise LedgerRefused(
                f"entry {broken} fails validation; refusing to extend a broken "
                "chain (report it to the user; see the design's rollback limit)"
            )
        errors = _append_errors(entries, fields)
        if errors:
            raise LedgerRefused("; ".join(errors))
        entry: dict[str, Any] = {
            "seq": len(entries) + 1, "kind": fields["kind"], "at": now(), **fields,
            "prev_hash": entries[-1]["hash"] if entries else None,
        }
        entry["hash"] = entry_hash(entry)
        entries.append(entry)
        _write_atomic(path, data)
    return entry


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def _is_decision(item: Any) -> bool:
    return (isinstance(item, dict) and set(item) == {"checkpoint_id", "answer"}
            and all(isinstance(value, str) and value for value in item.values()))


def _is_step(item: Any) -> bool:
    return (isinstance(item, dict) and set(item) == {"step", "status"}
            and isinstance(item["step"], str) and bool(item["step"])
            and item["status"] in ("passed", "failed"))


def _claims_errors(claims: Any) -> list[str]:
    """Validate the --claims JSON: what a summary or subagent report asserts."""
    if not isinstance(claims, dict):
        return ["claims must be a JSON object"]
    shapes = {
        "decisions": (_is_decision, "a list of {checkpoint_id, answer} with non-empty strings"),
        "steps": (_is_step, "a list of {step, status} with status passed or failed"),
        "expected_steps": (lambda s: isinstance(s, str) and bool(s), "a list of non-empty strings"),
    }
    errors = [f"unknown claims key {key}" for key in claims if key not in shapes]
    for key, (is_valid, shape) in shapes.items():
        value = claims.get(key, [])
        if not isinstance(value, list) or not all(is_valid(item) for item in value):
            errors.append(f"{key} must be {shape}")
    return errors


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def build_report(passport_path: Path, claims: dict[str, Any] | None = None) -> dict[str, Any]:
    """Classify the ledger against the claims into the handoff check's groups."""
    claims = claims or {}
    path = ledger_path(passport_path)
    status, detail, entries, broken = "ok", None, [], None
    try:
        data = load_ledger(path)
    except LedgerUnreadable as exc:
        status, detail = "unreadable", str(exc)
    else:
        if data is None:
            status, detail = "missing", f"no {path.name} beside the passport"
        else:
            entries = data["entries"]
            broken = first_untrusted_seq(entries)
            if broken is not None:
                status = "chain_broken"
                detail = f"entry {broken} fails validation; entries from {broken} on are untrusted"
    trusted = entries[: broken - 1] if broken is not None else entries
    state = _state(trusted)

    awaiting: list[dict[str, Any]] = []
    cannot_confirm: list[dict[str, Any]] = []
    not_run: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    backed = 0

    claimed = {d["checkpoint_id"]: d["answer"] for d in claims.get("decisions", [])}
    for checkpoint, opened in state["opened"].items():
        closed = state["closed"].get(checkpoint)
        claim = claimed.pop(checkpoint, None)
        if closed is None and claim is None:
            item = {
                "checkpoint_id": checkpoint,
                "stage": opened["stage"],
                "checkpoint_type": opened["checkpoint_type"],
                "question": opened["question"],
                "answered_items": sorted(state["partial"].get(checkpoint, ())),
            }
            if "reset_boundary_hash" in opened:
                item["reset_boundary_hash"] = opened["reset_boundary_hash"]
            awaiting.append(item)
        elif closed is None:
            cannot_confirm.append({
                "item": "decision", "checkpoint_id": checkpoint, "claimed": claim,
                "reason": "the checkpoint is still open in the ledger",
            })
        elif claim is not None and claim != closed["answer"]:
            cannot_confirm.append({
                "item": "decision", "checkpoint_id": checkpoint, "claimed": claim,
                "recorded": closed["answer"],
                "reason": "the ledger records a different answer",
            })
        else:
            backed += 1
    for checkpoint, claim in claimed.items():
        cannot_confirm.append({
            "item": "decision", "checkpoint_id": checkpoint, "claimed": claim,
            "reason": "no answer in the user's words is recorded",
        })

    claimed_steps = {s["step"]: s["status"] for s in claims.get("steps", [])}
    expected = set(claims.get("expected_steps", []))
    for step in sorted(set(state["receipts"]) | set(claimed_steps) | expected):
        receipt = state["receipts"].get(step)
        claim = claimed_steps.get(step)
        if receipt is None or receipt["status"] == "not_run":
            not_run.append({
                "step": step, "claimed": claim,
                "reason": "no receipt" if receipt is None else "the receipt records not_run",
            })
        elif claim is not None and claim != receipt["status"]:
            cannot_confirm.append({
                "item": "step", "step": step, "claimed": claim,
                "recorded": receipt["status"],
                "reason": "the receipt records a different outcome",
            })
        else:
            backed += 1

    for recorded_path, ref in state["files"].items():
        target = path.parent / recorded_path  # an absolute path replaces the parent
        if not target.is_file():
            missing.append({"path": recorded_path, "role": ref["role"], "reason": "absent"})
        elif _file_sha256(target) != ref["sha256"]:
            missing.append({"path": recorded_path, "role": ref["role"], "reason": "changed"})
        else:
            backed += 1

    return {
        "ledger": str(path),
        "ledger_status": status,
        "detail": detail,
        "untrusted_from_seq": broken,
        "entries": len(entries),
        "awaiting_answer": awaiting,
        "cannot_confirm": cannot_confirm,
        "not_run": not_run,
        "missing": missing,
        "backed": backed,
        "counters": state["counters"],
    }


def has_items(report: dict[str, Any]) -> bool:
    return report["ledger_status"] != "ok" or any(
        report[group] for group in ("awaiting_answer", "cannot_confirm", "not_run", "missing")
    )


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Refuse duplicate keys, as the ledger's own YAML loader does."""
    seen: set[str] = set()
    for key, _ in pairs:
        if key in seen:
            raise ValueError(f"duplicate key {key!r}")
        seen.add(key)
    return dict(pairs)


def _read_json_file(file: Path, label: str) -> Any:
    try:
        return json.loads(file.read_text(encoding="utf-8"), object_pairs_hook=_unique_keys)
    except (OSError, ValueError) as exc:
        raise LedgerRefused(f"{label} is not readable JSON: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ARS pipeline run ledger (#887).")
    sub = parser.add_subparsers(dest="command", required=True)
    append = sub.add_parser("append", help="Append one entry to the ledger.")
    append.add_argument("--passport-path", type=Path, required=True)
    append.add_argument("--entry-file", type=Path, required=True,
                        help="A file holding the entry as a JSON object.")
    report = sub.add_parser("report", help="Check the ledger against claims.")
    report.add_argument("--passport-path", type=Path, required=True)
    report.add_argument("--claims", type=Path, help="JSON file of what a summary or report claims.")
    args = parser.parse_args(argv)

    if not args.passport_path.is_file():
        print(_err(f"passport file not found at {args.passport_path}"), file=sys.stderr)
        return 2
    try:
        if args.command == "append":
            fields = _read_json_file(args.entry_file, "the entry")
            if not isinstance(fields, dict):
                raise LedgerRefused("the entry must be a JSON object")
            entry = append_entry(args.passport_path, fields)
            print(json.dumps({"seq": entry["seq"], "hash": entry["hash"]}))
            return 0
        claims = None
        if args.claims is not None:
            claims = _read_json_file(args.claims, "the claims file")
            problems = _claims_errors(claims)
            if problems:
                raise LedgerRefused("; ".join(problems))
        result = build_report(args.passport_path, claims)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (LedgerRefused, LedgerUnreadable) as exc:
        outcome = "nothing written" if args.command == "append" else "no report"
        print(_err(f"{outcome}: {exc}"), file=sys.stderr)
        return 2
    except LedgerLockError as exc:
        print(_err(f"ledger lock failed; write status is not assumed: {exc}"), file=sys.stderr)
        return 2
    except OSError as exc:
        what = ("ledger write failed without in-place truncation" if args.command == "append"
                else "cannot read a file the ledger names")
        print(_err(f"{what}: {exc}"), file=sys.stderr)
        return 2
    except Exception as exc:  # exit 1 means "has items", so no crash may exit 1
        print(_err(f"unexpected error: {exc!r}"), file=sys.stderr)
        return 2
    return 1 if has_items(result) else 0


if __name__ == "__main__":
    sys.exit(main())
