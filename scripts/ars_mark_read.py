"""ARS /ars-mark-read + /ars-unmark-read CLI implementation.

Implements v3.6.8 spec §3.6 + Step 7 (round-2 R2-002, round-5 R5-003 amends).

The command writes a peer file `<passport-stem>_human_read_log.yaml` next to
the active passport. The peer file is the canonical user-owned attestation source;
the literature_corpus[] schema is adapter-owned and MUST NOT be mutated to
carry reading-attestation state (v3.6.8 §3.1 firm rule 3).

Usage:
    python3 scripts/ars_mark_read.py <citation_key>... --passport-path <path> --scope <level>
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
- #513/#738 read_scope attestation (declaration-only, never inferred): every
  new mark requires an explicit
  `--scope {full_text,sections,abstract_only,toc_only,unknown}` records HOW
  MUCH of the source was read; `--locator` (repeatable, requires
  `--scope sections`) names the read sections/pages; `--note` free text
  (requires `--scope`). Scope-less records remain valid only as legacy input;
  consumers treat their coverage as unknown and never promote them to `ok`.
  Every new entry is labelled `USER_ATTESTED_READ`: this is the user's
  declaration, not proof of reading or comprehension.
  Attestation args are rejected with `--unmark` (rescinding takes no
  attestation). One invocation's attestation applies to every key in the
  batch. Sidecar schema: shared/contracts/passport/human_read_log.schema.json.
"""
from __future__ import annotations

import argparse
import errno
import fcntl
import os
import sys
import tempfile
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import yaml

try:
    from scripts.human_read_attestation_resolver import (
        LedgerValidationError,
        _UniqueKeySafeLoader,
        _validated_rows,
    )
except ModuleNotFoundError:  # direct ``python scripts/ars_mark_read.py`` use
    from human_read_attestation_resolver import (  # type: ignore[no-redef]
        LedgerValidationError,
        _UniqueKeySafeLoader,
        _validated_rows,
    )

ERR_PREFIX = "[ARS-MARK-READ ERROR:"

# #513 closed level enum + text bounds — keep in lockstep with
# shared/contracts/passport/human_read_log.schema.json (level enum; locators
# items minLength 1 / maxLength 200; note minLength 1 / maxLength 1000). The
# CLI enforces the bounds at write time so it can never produce a ledger the
# committed schema rejects (codex #513 r1 P1).
READ_SCOPE_LEVELS = ("full_text", "sections", "abstract_only", "toc_only", "unknown")
LOCATOR_MAX_LEN = 200
NOTE_MAX_LEN = 1000
LEDGER_LOCK_TIMEOUT_SECONDS = 10.0
LEDGER_LOCK_POLL_SECONDS = 0.05


class LedgerLockError(RuntimeError):
    """The same-directory ledger transaction lock could not be used."""


def _err(msg: str) -> str:
    return f"{ERR_PREFIX} {msg}]"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_log_path(passport_path: Path) -> Path:
    return passport_path.parent / f"{passport_path.stem}_human_read_log.yaml"


def _ledger_lock_path(log_path: Path) -> Path:
    """Return the stable peer lock path for one ledger.

    The lock file is deliberately persistent.  Unlinking it after release can
    split concurrent writers across different inodes and defeat advisory
    locking even though every writer appears to hold a lock.
    """
    return log_path.parent / f".{log_path.name}.lock"


@contextmanager
def _ledger_lock(
    log_path: Path,
    *,
    timeout_seconds: float | None = None,
) -> Iterator[None]:
    """Acquire a bounded, same-directory exclusive advisory lock.

    Every read/validate/mutate/replace transaction must run inside this lock.
    Acquisition is non-blocking with a bounded retry loop so contention or an
    unusable lock path fails visibly instead of hanging a command forever.
    """
    timeout = (
        LEDGER_LOCK_TIMEOUT_SECONDS
        if timeout_seconds is None
        else timeout_seconds
    )
    if timeout < 0:
        raise LedgerLockError("ledger lock timeout must be non-negative")

    lock_path = _ledger_lock_path(log_path)
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise LedgerLockError(f"cannot open peer lock: {exc}") from exc

    acquired = False
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except InterruptedError:
                continue
            except OSError as exc:
                if exc.errno in (errno.EACCES, errno.EAGAIN):
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise LedgerLockError(
                            f"timed out after {timeout:g}s waiting for peer lock"
                        ) from exc
                    time.sleep(min(LEDGER_LOCK_POLL_SECONDS, remaining))
                    continue
                raise LedgerLockError(
                    f"cannot acquire peer lock: {exc}"
                ) from exc

        yield
    finally:
        active_exception = sys.exc_info()[0] is not None
        release_error: OSError | None = None
        if acquired:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError as exc:
                release_error = exc
        try:
            os.close(fd)
        except OSError as exc:
            if release_error is None:
                release_error = exc
        if release_error is not None and not active_exception:
            raise LedgerLockError(
                f"cannot release peer lock cleanly: {release_error}"
            ) from release_error


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


def _load_log(log_path: Path) -> dict[str, Any]:
    """Load an existing ledger only after duplicate-safe closed validation.

    Mutation commands are intentionally stricter than PyYAML's default
    loader: duplicate mapping keys, malformed UTF-8/YAML, missing fields,
    unknown fields, invalid timestamps, and invalid row/scope combinations
    all fail closed.  In particular, this function never repairs or defaults
    an existing ledger because doing so would destroy the evidence needed to
    diagnose it.
    """
    if not log_path.exists():
        return {
            "session_id": str(uuid.uuid4()),
            "created_at": _now_iso(),
            "human_read": [],
        }

    try:
        raw = log_path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise LedgerValidationError(
            f"existing ledger cannot be read as UTF-8: {exc}"
        ) from exc
    try:
        data = yaml.load(text, Loader=_UniqueKeySafeLoader)
    except yaml.YAMLError as exc:
        raise LedgerValidationError(
            f"existing ledger is not duplicate-safe valid YAML: {exc}"
        ) from exc

    # This is the same closed runtime contract used by the resolver.  Calling
    # it here, before returning the object to main(), guarantees there is no
    # mutation path from an invalid on-disk ledger.
    _validated_rows(data)
    return data


def _save_log(log_path: Path, data: dict[str, Any]) -> None:
    """Validate and atomically replace the ledger from a same-dir temp file.

    The destination is never opened with ``"w"``.  A serialization, flush,
    fsync, or replace failure therefore leaves an existing ledger untouched;
    an owned temporary file is removed on failure.
    """
    _validated_rows(data)
    payload = yaml.safe_dump(
        data, sort_keys=False, allow_unicode=True
    ).encode("utf-8")
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=log_path.parent,
            prefix=f".{log_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(payload)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, log_path)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def _mark(log: dict, citation_key: str, read_scope: dict | None = None) -> None:
    entry: dict = {
        "citation_key": citation_key,
        "marked_at": _now_iso(),
        "attestation_type": "USER_ATTESTED_READ",
    }
    if read_scope is not None:
        entry["read_scope"] = read_scope
    log["human_read"].append(entry)


def _build_read_scope(args: argparse.Namespace) -> dict | None:
    """Validate the #513 attestation flags and build the read_scope object.

    Returns None only for unmark, the read_scope dict when a new mark is
    valid, or raises SystemExit(2) with the canonical
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
        if not args.unmark:
            errors.append(
                "--scope is required for every new USER_ATTESTED_READ mark; "
                "use --scope unknown when coverage cannot be specified"
            )
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


def _update_log_locked(
    log_path: Path,
    citation_keys: list[str],
    *,
    read_scope: dict | None,
    unmark: bool,
) -> list[str]:
    """Reload, validate, mutate, and atomically replace under one lock.

    Returning missing active marks keeps batch unmark all-or-nothing: the
    in-memory partial mutation is discarded and no replacement occurs.
    """
    with _ledger_lock(log_path):
        log = _load_log(log_path)
        if unmark:
            not_found = [
                key for key in citation_keys if not _unmark(log, key)
            ]
            if not_found:
                return not_found
        else:
            for key in citation_keys:
                _mark(log, key, read_scope)
        _save_log(log_path, log)
    return []


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
        help="#513/#738 USER_ATTESTED_READ scope: how much of the source the "
        "user declares reading. Required for new marks; use unknown when "
        "coverage cannot be specified.",
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

    # Preserve the four canonical environment errors and corpus-membership
    # error before enforcing the new-mark attestation shape.
    read_scope = _build_read_scope(args)

    try:
        not_found = _update_log_locked(
            log_path,
            args.citation_keys,
            read_scope=read_scope,
            unmark=args.unmark,
        )
    except LedgerLockError as exc:
        print(
            _err(
                "read ledger lock lifecycle failed; mutation status is not "
                f"assumed: {exc}"
            ),
            file=sys.stderr,
        )
        return 2
    except LedgerValidationError as exc:
        print(
            _err(f"existing read ledger is invalid; refusing mutation: {exc}"),
            file=sys.stderr,
        )
        return 2
    except (OSError, yaml.YAMLError) as exc:
        print(
            _err(f"read ledger write failed without in-place truncation: {exc}"),
            file=sys.stderr,
        )
        return 2
    if not_found:
        for k in not_found:
            print(
                _err(
                    f"citation_key '{k}' has no active mark to rescind"
                ),
                file=sys.stderr,
            )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
