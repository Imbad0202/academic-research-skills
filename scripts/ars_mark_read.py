"""ARS /ars-mark-read + /ars-unmark-read CLI implementation.

Implements v3.6.8 spec §3.6 + Step 7 (round-2 R2-002, round-5 R5-003 amends).

The command writes a peer file `<passport-stem>_human_read_log.yaml` next to
the active passport. The peer file is the canonical user-owned signal source;
the literature_corpus[] schema is adapter-owned and MUST NOT be mutated to
carry `human_read_source` (v3.6.8 §3.1 firm rule 3).

Usage:
    python3 scripts/ars_mark_read.py <citation_key>... --passport-path <path>
    python3 scripts/ars_mark_read.py <citation_key>... --passport-path <path> --unmark

Behavior summary:
- 4 fail-fast modes (no passport / not found / parent unreadable / unwritable)
  emit canonical `[ARS-MARK-READ ERROR: ...]` and exit non-zero.
- Invalid citation_key (not in active corpus) is a hard error per §3.6 firm
  rule 2. Batch with any invalid key is rejected whole (no partial writes).
- Append-only YAML write per §3.6 firm rule 3. /ars-unmark-read writes
  `rescinded_at` to the matching entry, never deletes.
- First-time write creates the file with the YAML schema header. Not a
  fail-fast condition.
- #513 read_scope attestation (declaration-only, never inferred): optional
  `--scope {full_text,sections,abstract_only,toc_only,unknown}` records HOW
  MUCH of the source was read; `--locator` (repeatable, requires
  `--scope sections`) names the read sections/pages; `--note` free text
  (requires `--scope`). Absent `--scope` writes no `read_scope` field —
  consumers treat absence as `unknown`; nothing is fabricated or backfilled.
  Attestation args are rejected with `--unmark` (rescinding takes no
  attestation). One invocation's attestation applies to every key in the
  batch. Sidecar schema: shared/contracts/passport/human_read_log.schema.json.
"""
from __future__ import annotations

import argparse
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

ERR_PREFIX = "[ARS-MARK-READ ERROR:"

# #513 closed level enum + text bounds — keep in lockstep with
# shared/contracts/passport/human_read_log.schema.json (level enum; locators
# items minLength 1 / maxLength 200; note minLength 1 / maxLength 1000). The
# CLI enforces the bounds at write time so it can never produce a ledger the
# committed schema rejects (codex #513 r1 P1).
READ_SCOPE_LEVELS = ("full_text", "sections", "abstract_only", "toc_only", "unknown")
LOCATOR_MAX_LEN = 200
NOTE_MAX_LEN = 1000


def _err(msg: str) -> str:
    return f"{ERR_PREFIX} {msg}]"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_log_path(passport_path: Path) -> Path:
    return passport_path.parent / f"{passport_path.stem}_human_read_log.yaml"


def _validate_passport_environment(passport_path: Path | None) -> tuple[Path, Path]:
    """Run the 4 fail-fast checks per §3.6 R5-003 amend.

    Returns (passport_path, read_log_path) if all checks pass; raises
    SystemExit with the canonical error message otherwise.
    """
    if passport_path is None:
        print(
            _err(
                "no active passport path; run a session with passport "
                "handoff first or pass --passport-path explicitly"
            ),
            file=sys.stderr,
        )
        raise SystemExit(2)

    parent = passport_path.parent
    # Check parent R_OK BEFORE passport.exists() — pathlib's stat() raises
    # PermissionError on an unreadable parent, which would mask the canonical
    # error we want to emit.
    if not os.access(parent, os.R_OK):
        print(
            _err(f"passport parent directory {parent} unreadable"),
            file=sys.stderr,
        )
        raise SystemExit(2)

    if not passport_path.exists():
        print(_err(f"passport file not found at {passport_path}"), file=sys.stderr)
        raise SystemExit(2)

    if not os.access(parent, os.W_OK):
        log_path = _read_log_path(passport_path)
        print(
            _err(
                f"read-log path target is unwritable at {log_path}; "
                "parent directory not writable"
            ),
            file=sys.stderr,
        )
        raise SystemExit(2)

    log_path = _read_log_path(passport_path)
    if log_path.exists() and not os.access(log_path, os.W_OK):
        print(
            _err(
                f"read-log path target is unwritable at {log_path}; "
                "existing file not writable"
            ),
            file=sys.stderr,
        )
        raise SystemExit(2)

    return passport_path, log_path


def _load_corpus_keys(passport_path: Path) -> set[str]:
    with passport_path.open(encoding="utf-8") as f:
        passport = yaml.safe_load(f) or {}
    corpus = passport.get("literature_corpus", []) or []
    return {entry["citation_key"] for entry in corpus if "citation_key" in entry}


def _load_log(log_path: Path) -> dict:
    if not log_path.exists():
        return {
            "session_id": str(uuid.uuid4()),
            "created_at": _now_iso(),
            "human_read": [],
        }
    with log_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("human_read", [])
    return data


def _save_log(log_path: Path, data: dict) -> None:
    with log_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def _mark(log: dict, citation_key: str, read_scope: dict | None = None) -> None:
    entry: dict = {"citation_key": citation_key, "marked_at": _now_iso()}
    if read_scope is not None:
        entry["read_scope"] = read_scope
    log["human_read"].append(entry)


def _build_read_scope(args: argparse.Namespace) -> dict | None:
    """Validate the #513 attestation flags and build the read_scope object.

    Returns None when no attestation was given (legacy mark shape), the
    read_scope dict when valid, or raises SystemExit(2) with the canonical
    error surface on a contradictory attestation — a contradictory or
    partial attestation is refused, never recorded ambiguously."""
    # Presence is `is not None`, NEVER truthiness: `--note ""` is an explicitly
    # supplied (invalid) attestation argument, not an absent one — truthiness
    # would let it bypass both the requires-scope rule and the unmark rejection
    # (codex #513 r1 P1).
    locator_given = args.locator is not None
    note_given = args.note is not None
    errors: list[str] = []
    if args.unmark and (args.scope is not None or locator_given or note_given):
        errors.append("--scope/--locator/--note cannot be combined with --unmark (rescinding takes no attestation)")
    elif args.scope is None:
        if locator_given:
            errors.append("--locator requires --scope sections (an attestation needs a declared level)")
        if note_given:
            errors.append("--note requires --scope (an attestation needs a declared level)")
    else:
        if locator_given and args.scope != "sections":
            errors.append(
                f"--locator requires --scope sections; with --scope {args.scope} "
                "locators are redundant or contradict the declared level"
            )
        if locator_given:
            for loc in args.locator:
                if not 1 <= len(loc) <= LOCATOR_MAX_LEN:
                    errors.append(
                        f"--locator value must be 1-{LOCATOR_MAX_LEN} characters "
                        f"(got {len(loc)}); the sidecar schema would reject the ledger"
                    )
        if note_given and not 1 <= len(args.note) <= NOTE_MAX_LEN:
            errors.append(
                f"--note must be 1-{NOTE_MAX_LEN} characters (got {len(args.note)}); "
                "the sidecar schema would reject the ledger"
            )
    if errors:
        for e in errors:
            print(_err(e), file=sys.stderr)
        raise SystemExit(2)
    if args.scope is None:
        return None
    read_scope: dict = {"level": args.scope}
    if locator_given:
        read_scope["locators"] = list(args.locator)
    if note_given:
        read_scope["note"] = args.note
    return read_scope


def _unmark(log: dict, citation_key: str) -> bool:
    """Append `rescinded_at` to the most recent matching entry without a
    prior rescind. Returns True if found, False otherwise."""
    for entry in reversed(log["human_read"]):
        if entry["citation_key"] == citation_key and "rescinded_at" not in entry:
            entry["rescinded_at"] = _now_iso()
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ARS /ars-mark-read peer-file writer (v3.6.8 §3.6)."
    )
    parser.add_argument(
        "citation_keys",
        nargs="+",
        help="Citation keys to mark (or unmark with --unmark).",
    )
    parser.add_argument(
        "--passport-path",
        type=Path,
        default=None,
        help="Active Material Passport JSON path.",
    )
    parser.add_argument(
        "--unmark",
        action="store_true",
        help="Rescind prior marks (write rescinded_at instead of marked_at).",
    )
    parser.add_argument(
        "--scope",
        choices=READ_SCOPE_LEVELS,
        default=None,
        help="#513 read_scope attestation: how much of the source was read. "
        "Absent = no read_scope recorded (consumers treat as unknown).",
    )
    parser.add_argument(
        "--locator",
        action="append",
        default=None,
        help="Which sections/pages were read (repeatable; requires --scope sections).",
    )
    parser.add_argument(
        "--note",
        default=None,
        help="Free-text attestation note (requires --scope).",
    )
    args = parser.parse_args(argv)

    read_scope = _build_read_scope(args)
    passport_path, log_path = _validate_passport_environment(args.passport_path)
    corpus_keys = _load_corpus_keys(passport_path)

    # Validate all keys up-front; refuse to write on any invalid key
    # (§3.6 firm rule 2, batch-level all-or-nothing).
    invalid = [k for k in args.citation_keys if k not in corpus_keys]
    if invalid:
        for k in invalid:
            print(
                _err(f"citation_key '{k}' not in literature_corpus[]"),
                file=sys.stderr,
            )
        return 2

    log = _load_log(log_path)

    if args.unmark:
        not_found = [
            k for k in args.citation_keys if not _unmark(log, k)
        ]
        if not_found:
            for k in not_found:
                print(
                    _err(
                        f"citation_key '{k}' has no active mark to rescind"
                    ),
                    file=sys.stderr,
                )
            return 2
    else:
        for k in args.citation_keys:
            _mark(log, k, read_scope)

    _save_log(log_path, log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
