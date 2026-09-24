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
    python3 scripts/run_ledger.py report --passport-path P [--claims F] [--render LANG]

``append`` validates one entry (a JSON object with ``kind`` and that kind's
fields), gives it the next ``seq``, the UTC time, the previous entry's hash,
and its own hash, and replaces the whole ledger atomically under the peer
lock that /ars-mark-read uses. It refuses to extend an unreadable ledger or
a broken chain, so a damaged record is never blessed by a later entry. It
also hashes the files an entry names (a ``file_reference`` path, and a
receipt's ``input_paths``, which it stores as ``input_sha256``) and refuses a
supplied digest that does not match its file (#898). Relative paths resolve
against the ledger's directory, for the writer and the report alike.

``report`` checks every hash, then compares the trusted entries with what a
summary or a subagent report claims (``--claims``, a JSON file). It prints
one JSON object carrying the four groups of the handoff check
(``awaiting_answer``, ``cannot_confirm``, ``not_run``, ``missing``),
``backed``, the number of examined items the ledger supports,
``step_outcomes``, the recorded outcome of every step whose receipt still
backs it, and the latest counters grouped by stage ("run" when a progress
entry names no stage). A receipt whose input files changed or disappeared
after it was written no longer backs its step, so its step is absent from
``step_outcomes``. With ``--render en`` or ``--render zh-TW`` it prints
the finished handoff-check block instead, for the orchestrator to insert
verbatim, and prints nothing when there is nothing to report (#898). Exit
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

_UTC_Z = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
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


_TEXT_RULE = f"valid text of 1-{SHORT_MAX} characters"

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
        and (entry["kind"] != "initial_instructions" or index == 1)
        and isinstance(entry["at"], str) and _UTC_Z.fullmatch(entry["at"]) is not None
        and entry["prev_hash"] == prev_hash
        and _hash_matches(entry)
    )


def _hash_matches(entry: dict[str, Any]) -> bool:
    try:
        return entry["hash"] == entry_hash(entry)
    except ValueError:  # e.g. a hand-edited integer too long to print as JSON
        return False


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
    except (OSError, ValueError, yaml.YAMLError) as exc:  # ValueError: bad bytes, impossible dates
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


def _file_status(target: Path, digest: str) -> str | None:
    """None when the file still has this digest, else "absent" or "changed"."""
    if not target.is_file():
        return "absent"
    return None if _file_sha256(target) == digest else "changed"


def _hash_named_files(fields: dict[str, Any], base: Path) -> list[str]:
    """Fill in the digests of the files an entry names, read from the files.

    A ``file_reference`` gets its ``sha256``; a receipt's ``input_paths``
    (accepted on input only) become ``input_sha256``. A digest the entry
    supplies must match its file. Values that are not valid paths are left
    to the field checks, which refuse them.
    """
    kind = fields.get("kind")
    if kind == "file_reference" and not _path(fields.get("path")):
        named = {fields["path"]: fields.get("sha256")}
    elif kind == "tool_receipt":
        paths = fields.pop("input_paths", [])
        if not isinstance(paths, list) or len(paths) > LIST_MAX or any(_path(p) for p in paths):
            return [f"tool_receipt.input_paths must be a list of up to {LIST_MAX} paths"]
        supplied = fields.get("input_sha256", {})
        if not isinstance(supplied, dict) or any(_path(name) for name in supplied):
            return []
        named = {**dict.fromkeys(paths), **supplied}
    else:
        return []
    errors: list[str] = []
    digests: dict[str, str] = {}
    for name, supplied_digest in named.items():
        target = base / name  # an absolute path replaces the base
        try:
            digest = _file_sha256(target) if target.is_file() else None
        except OSError as exc:
            errors.append(f"cannot read {name}: {exc}")
            continue
        if digest is None:
            errors.append(f"{name} is not a file beside the ledger or at that absolute path")
        elif supplied_digest is not None and supplied_digest != digest:
            errors.append(f"the digest supplied for {name} does not match the file; "
                          "omit it and the writer computes it")
        else:
            digests[name] = digest
    if errors:
        return errors
    if kind == "file_reference":
        fields["sha256"] = digests[fields["path"]]
    elif digests:
        fields["input_sha256"] = digests
    return []


def append_entry(
    passport_path: Path, fields: dict[str, Any], *, now: Callable[[], str] = _now_iso
) -> dict[str, Any]:
    """Validate and append one entry under the peer lock; return the entry."""
    path = ledger_path(passport_path)
    fields = dict(fields)
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
        errors = _hash_named_files(fields, path.parent) or _append_errors(entries, fields)
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
            and not any(_short(value) for value in item.values()))


def _is_step(item: Any) -> bool:
    return (isinstance(item, dict) and set(item) == {"step", "status"}
            and not _short(item["step"]) and item["status"] in ("passed", "failed"))


def _claims_errors(claims: Any) -> list[str]:
    """Validate the --claims JSON: what a summary or subagent report asserts."""
    if not isinstance(claims, dict):
        return ["claims must be a JSON object"]
    shapes = {
        "decisions": (_is_decision, f"a list of {{checkpoint_id, answer}}, each {_TEXT_RULE}"),
        "steps": (_is_step, f"a list of {{step, status}}, step {_TEXT_RULE}, status passed or failed"),
        "expected_steps": (lambda s: not _short(s), f"a list of strings, each {_TEXT_RULE}"),
    }
    errors = [f"unknown claims key {key}" for key in claims if key not in shapes]
    for key, (is_valid, shape) in shapes.items():
        value = claims.get(key, [])
        if not isinstance(value, list) or not all(is_valid(item) for item in value):
            errors.append(f"{key} must be {shape}")
    return errors


def _group(claims: list[dict[str, str]], key: str, value: str) -> dict[str, list[str]]:
    """Every distinct claimed value per id, in order, so contradictions stay visible."""
    grouped: dict[str, list[str]] = {}
    for claim in claims:
        values = grouped.setdefault(claim[key], [])
        if claim[value] not in values:
            values.append(claim[value])
    return grouped


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
    outcomes: dict[str, str] = {}
    backed = 0

    claimed = _group(claims.get("decisions", []), "checkpoint_id", "answer")
    for checkpoint, opened in state["opened"].items():
        closed = state["closed"].get(checkpoint)
        answers = claimed.pop(checkpoint, [])
        if closed is None and not answers:
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
            cannot_confirm += [{
                "item": "decision", "checkpoint_id": checkpoint, "claimed": answer,
                "reason": "the checkpoint is still open in the ledger",
            } for answer in answers]
        else:
            differing = [answer for answer in answers if answer != closed["answer"]]
            cannot_confirm += [{
                "item": "decision", "checkpoint_id": checkpoint, "claimed": answer,
                "recorded": closed["answer"],
                "reason": "the ledger records a different answer",
            } for answer in differing]
            if not differing:
                backed += 1
    for checkpoint, answers in claimed.items():
        cannot_confirm += [{
            "item": "decision", "checkpoint_id": checkpoint, "claimed": answer,
            "reason": "no answer in the user's words is recorded",
        } for answer in answers]

    claimed_steps = _group(claims.get("steps", []), "step", "status")
    expected = set(claims.get("expected_steps", []))
    for step in sorted(set(state["receipts"]) | set(claimed_steps) | expected):
        receipt = state["receipts"].get(step)
        statuses = claimed_steps.get(step, [])
        usable = receipt is not None and receipt["status"] != "not_run"
        changed = [
            {"path": name, "reason": reason}
            for name, digest in sorted(receipt.get("input_sha256", {}).items())
            if (reason := _file_status(path.parent / name, digest))
        ] if usable else []
        if not usable or changed:
            reason = ("the receipt's inputs changed after it was written" if changed
                      else "no receipt" if receipt is None else "the receipt records not_run")
            extra = {"changed_inputs": changed} if changed else {}
            not_run += [{"step": step, "claimed": status, "reason": reason, **extra}
                        for status in statuses or [None]]
        else:
            outcomes[step] = receipt["status"]
            differing = [status for status in statuses if status != receipt["status"]]
            cannot_confirm += [{
                "item": "step", "step": step, "claimed": status,
                "recorded": receipt["status"],
                "reason": "the receipt records a different outcome",
            } for status in differing]
            if not differing:
                backed += 1

    for recorded_path, ref in state["files"].items():
        reason = _file_status(path.parent / recorded_path, ref["sha256"])
        if reason:
            missing.append({"path": recorded_path, "role": ref["role"], "reason": reason})
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
        "step_outcomes": outcomes,
        "counters": state["counters"],
    }


def has_items(report: dict[str, Any]) -> bool:
    return report["ledger_status"] != "ok" or any(
        report[group] for group in ("awaiting_answer", "cannot_confirm", "not_run", "missing")
    )


# ---------------------------------------------------------------------------
# Rendered handoff check (#898). The orchestrator inserts this block verbatim,
# so a deterministic result is never re-worded by the model. English and
# Traditional Chinese; the orchestrator picks zh-TW when the user writes in
# Traditional Chinese and en otherwise. Ledger text (ids, questions, answers,
# paths, roles) is shown as written: whitespace runs collapse so it stays on its
# line, and Markdown and HTML characters are escaped so it displays as the JSON
# holds it.
# ---------------------------------------------------------------------------

_TEXT: dict[str, dict[str, str]] = {
    "en": {
        "title": "### Handoff check",
        "ledger_missing": "Ledger problem: no {name} beside the Material Passport.",
        "ledger_unreadable": "Ledger problem: {name} cannot be read.",
        "ledger_chain_broken": "Ledger problem: entry {seq} fails validation; entries from {seq} on are not used.",
        "awaiting": "Awaiting your answer ({n})",
        "cannot_confirm": "Cannot confirm ({n})",
        "not_run": "Not run ({n})",
        "missing": "Missing ({n})",
        "checkpoint": "- {id}, stage {stage} ({type}):",
        "question": '  "{text}"',
        "recorded_one": "  1 item recorded: {ids}",
        "recorded_many": "  {n} items recorded: {ids}",
        "decision_open": '- Decision {id}: the summary or report says "{claimed}"; the checkpoint is still open in the ledger',
        "decision_other": '- Decision {id}: the summary or report says "{claimed}"; the ledger records "{recorded}"',
        "decision_none": '- Decision {id}: the summary or report says "{claimed}"; no answer in your words is recorded',
        "step_other": "- Step {step}: the summary or report says {claimed}; the receipt records {recorded}",
        "no_receipt": "- {step}: no receipt",
        "receipt_not_run": "- {step}: the receipt records not run",
        "inputs_changed": "- {step}: its inputs changed after the receipt was written ({files})",
        "claimed_suffix": "; the summary or report says {claimed}",
        "input_file": "{path}: {state}",
        "file": "- {path} ({role}): {state}",
        "absent": "absent", "changed": "changed", "passed": "passed", "failed": "failed",
        "and": " and ", "sep": "; ",
        "backed_none": "The ledger backs no items.",
        "backed_one": "The ledger backs 1 item; it will not be asked again.",
        "backed_many": "The ledger backs {n} items; they will not be asked again.",
    },
    "zh-TW": {
        "title": "### 交接檢查",
        "ledger_missing": "紀錄檔問題：Material Passport 旁邊沒有 {name}。",
        "ledger_unreadable": "紀錄檔問題：{name} 無法讀取。",
        "ledger_chain_broken": "紀錄檔問題：第 {seq} 筆紀錄驗證失敗，從第 {seq} 筆起都不採用。",
        "awaiting": "等你回答（{n}）",
        "cannot_confirm": "無法確認（{n}）",
        "not_run": "沒跑過（{n}）",
        "missing": "不見了（{n}）",
        "checkpoint": "- {id}，階段 {stage}（{type}）：",
        "question": "  「{text}」",
        "recorded_one": "  已記下 1 項：{ids}",
        "recorded_many": "  已記下 {n} 項：{ids}",
        "decision_open": "- 決定 {id}：摘要或報告寫「{claimed}」，紀錄裡這個檢查點還沒有回答",
        "decision_other": "- 決定 {id}：摘要或報告寫「{claimed}」，紀錄裡是「{recorded}」",
        "decision_none": "- 決定 {id}：摘要或報告寫「{claimed}」，紀錄裡沒有你的原話",
        "step_other": "- 步驟 {step}：摘要或報告寫{claimed}，執行收據記錄的是{recorded}",
        "no_receipt": "- {step}：沒有執行收據",
        "receipt_not_run": "- {step}：執行收據記錄為沒跑",
        "inputs_changed": "- {step}：執行收據寫下後，輸入檔有變動（{files}）",
        "claimed_suffix": "，摘要或報告寫{claimed}",
        "input_file": "{path}：{state}",
        "file": "- {path}（{role}）：{state}",
        "absent": "檔案不見了", "changed": "檔案被改過", "passed": "通過", "failed": "未通過",
        "and": "和", "sep": "；",
        "backed_none": "紀錄沒有確認任何項目。",
        "backed_one": "紀錄已確認 1 項，這一項不會再問你。",
        "backed_many": "紀錄已確認 {n} 項，這些不會再問你。",
    },
}
RENDER_LANGUAGES = tuple(_TEXT)
# build_report's reason strings -> the _TEXT line that shows them.
_REASON_LINES = {
    "the checkpoint is still open in the ledger": "decision_open",
    "the ledger records a different answer": "decision_other",
    "no answer in the user's words is recorded": "decision_none",
    "the receipt records a different outcome": "step_other",
    "no receipt": "no_receipt",
    "the receipt records not_run": "receipt_not_run",
    "the receipt's inputs changed after it was written": "inputs_changed",
}


# Always special inline, and "_" where it can open or close emphasis (not
# between two letters or digits, as in "paper_v2.md").
_MARKUP = re.compile(r"[\\`*\[\]<>&~]|(?<![^\W_])_|_(?![^\W_])")
# A value can open a list item's text, where a leading "#", "-", "+", or list
# number ("1." or "1)") followed by a space or the end of the value would start
# a heading or a nested list; "2.5" or "#tag" opens nothing.
_BLOCK_OPENER = re.compile(r"^(?:#{1,6}|[+-]|\d{1,9}[.)])(?=\s|$)")


def _one_line(value: Any) -> str:
    text = _MARKUP.sub(lambda m: "\\" + m.group(0), " ".join(str(value).split()))
    opener = _BLOCK_OPENER.match(text)
    if opener is None:
        return text
    if opener.group(0)[0].isdigit():  # escape the "." or ")" after the number
        return f"{text[:opener.end() - 1]}\\{text[opener.end() - 1:]}"
    return f"\\{text}"


def render_block(report: dict[str, Any], lang: str) -> str:
    """The handoff check as shown to the user, or "" when there is nothing to report."""
    if not has_items(report):
        return ""
    text = _TEXT[lang]
    lines = [text["title"], ""]
    if report["ledger_status"] != "ok":
        lines += [text[f"ledger_{report['ledger_status']}"].format(
            name=_one_line(Path(report["ledger"]).name), seq=report["untrusted_from_seq"]), ""]

    awaiting: list[str] = []
    for item in report["awaiting_answer"]:
        entry = [text["checkpoint"].format(id=_one_line(item["checkpoint_id"]),
                                           stage=_one_line(item["stage"]),
                                           type=item["checkpoint_type"]),
                 text["question"].format(text=_one_line(item["question"]))]
        answered = item["answered_items"]
        if answered:
            key = "recorded_one" if len(answered) == 1 else "recorded_many"
            entry.append(text[key].format(n=len(answered),
                                          ids=", ".join(_one_line(i) for i in answered)))
        awaiting.append("\n".join(entry))

    cannot = [text[_REASON_LINES[item["reason"]]].format(
        id=_one_line(item.get("checkpoint_id", "")), step=_one_line(item.get("step", "")),
        claimed=(_one_line(item["claimed"]) if item["item"] == "decision"
                 else text[item["claimed"]]),
        recorded=(_one_line(item.get("recorded", "")) if item["item"] == "decision"
                  else text[item["recorded"]]))
        for item in report["cannot_confirm"]]

    not_run: list[str] = []
    by_step: dict[str, list[dict[str, Any]]] = {}
    for item in report["not_run"]:
        by_step.setdefault(item["step"], []).append(item)
    for step, items in by_step.items():
        files = text["sep"].join(
            text["input_file"].format(path=_one_line(f["path"]), state=text[f["reason"]])
            for f in items[0].get("changed_inputs", []))
        line = text[_REASON_LINES[items[0]["reason"]]].format(step=_one_line(step), files=files)
        claimed = [text[i["claimed"]] for i in items if i["claimed"] is not None]
        if claimed:
            line += text["claimed_suffix"].format(claimed=text["and"].join(claimed))
        not_run.append(line)

    missing = [text["file"].format(path=_one_line(item["path"]), role=_one_line(item["role"]),
                                   state=text[item["reason"]])
               for item in report["missing"]]

    for key, group in (("awaiting", awaiting), ("cannot_confirm", cannot),
                       ("not_run", not_run), ("missing", missing)):
        if group:
            lines += [text[key].format(n=len(group)), *group, ""]

    backed = report["backed"]
    lines.append(text["backed_none"] if backed == 0 else text["backed_one"] if backed == 1
                 else text["backed_many"].format(n=backed))
    return "\n".join(lines)


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
    report.add_argument("--render", choices=RENDER_LANGUAGES,
                        help="Print the finished handoff-check block in this language instead of JSON.")
    args = parser.parse_args(argv)

    try:
        passport_found = args.passport_path.is_file()
    except OSError as exc:  # e.g. a name too long, or no permission to look
        print(_err(f"cannot check the passport path: {exc}"), file=sys.stderr)
        return 2
    if not passport_found:
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
        if args.render:
            block = render_block(result, args.render)
            if block:
                print(block)
        else:
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
        print(_err(f"unexpected error: {type(exc).__name__}: {exc}"), file=sys.stderr)
        return 2
    return 1 if has_items(result) else 0


if __name__ == "__main__":
    sys.exit(main())
