"""PDF read-integrity preflight (#512).

Guards the LOCAL EXTRACTION CHANNEL behind v3.7.3 `page` anchors: PDF readers silently
truncate documents with malformed cross-reference tables and misreport page counts, so a
real, correctly-cited source can acquire an apparently valid page locator derived from a
truncated or mispaginated read — and pass every downstream gate (the v3.7.3 lint checks
anchor shape, the #182 gate reduces anchors to a kind-only boolean). This preflight is run
at the orchestration/retrieval layer (never by Bucket A writer agents, which cannot run
Bash) BEFORE page numbers from a locally-read PDF are trusted as anchor values.

Mechanism (observed in kengo006/alexandria, reshaped per the #512 dual-track review):
three independent page-count signals must agree —

  1. declared_page_count   — the root page tree's /Count, read from the raw object;
  2. enumerated_page_count — this script's own recursive /Kids walk counting /Type /Page
                             leaves (cycle-guarded, node-budgeted);
  3. reader_page_count     — pypdf's flattened page list, as a third opinion.

Verdict: PASS only when all three agree, the count is positive, and the parse emitted no
repair warnings. FAIL when the parse completed but counts disagree (the truncation /
mispagination signal itself). UNAVAILABLE for anything the preflight cannot vouch for:
unreadable or missing file, encryption, missing/malformed page tree, a /Kids cycle or
node-budget hit, pypdf absent, or parser-repair warnings even with agreeing counts (a
repaired read may be complete, but only PASS licenses a page anchor downstream, so the
conservative bucket is the honest one).

Object plumbing rides pypdf (already a repo dependency; `verify_submission_package.py`
precedent), which handles classic xref tables, xref streams, /Prev incremental-update
chains, and object streams — this is deliberately NOT a "grep the first /Count" check.

Optional content classification is a separate, explicitly requested advisory.  The
parent never imports the optional native classifier: it sends the exact bytes already
hashed here to a fixed subprocess worker, applies timeout and pipe-size ceilings, and
accepts only a closed result.  The structural verdict remains structural; callers that
opt in must read the separate `content_advisory` field.

CLI: `python scripts/pdf_read_preflight.py FILE [--classify-content]
[--classifier-diagnostics LOCAL.json] [--output SIDECAR.json]`. Exit 0 whenever a
verdict was produced (the verdict is data, not an error; orchestration consumes the JSON
without exit-code branching); exit 2 on usage errors only.

Design: docs/design/2026-07-20-512-pdf-read-preflight-spec.md.
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import math
import os
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from audit_snapshot import sha256_hex
except ImportError:  # pragma: no cover - dual-path import (verify_submission_package precedent)
    from scripts.audit_snapshot import sha256_hex

try:
    import pypdf
except ImportError:  # degrade to UNAVAILABLE, mirroring verify_submission_package.py
    pypdf = None

TOOL_VERSION = "pdf_read_preflight/1.0.0"
CONTENT_TOOL_VERSION = "pdf_read_preflight/1.1.0"
SCHEMA = "pdf_read_preflight/1"
CONTENT_SCHEMA = "pdf_content_classification/1"
WORKER_SCHEMA = "pdf_content_classifier_worker/1"
DIAGNOSTIC_SCHEMA = "pdf_content_classifier_diagnostic/1"

CLASSIFIER_WORKER = Path(__file__).with_name("pdf_content_classifier_worker.py")
CLASSIFIER_TIMEOUT_SECONDS = 5.0
CLASSIFIER_STDOUT_LIMIT = 8_192
CLASSIFIER_STDERR_LIMIT = 4_096
CLASSIFIER_OPERATOR_DETAIL_LIMIT = 512
CLASSIFIER_MAX_PAGE_ENTRIES = 50_000

# Hard ceiling on page-tree nodes visited by the enumeration walk. Real documents sit
# far below this; hitting it means a pathological or adversarial tree we must not vouch
# for (and must not spin on).
NODE_BUDGET = 50_000

PASS, FAIL, UNAVAILABLE = "PASS", "FAIL", "UNAVAILABLE"


class _WarningCollector(logging.Handler):
    """Captures pypdf's parser chatter — repair messages ARE the silent-xref-repair
    signal this preflight exists to surface."""

    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.messages: list[str] = []

    def emit(self, record):
        self.messages.append(record.getMessage())


class _TreeProblem(Exception):
    """Structural page-tree problem that forecloses a confident enumeration."""


class _ClassifierProtocolError(Exception):
    """The isolated worker did not satisfy its closed result contract."""


class _CappedPipeReader:
    """Drain one worker pipe while retaining at most ``limit + 1`` bytes."""

    def __init__(self, stream: Any, limit: int):
        self.stream = stream
        self.limit = limit
        self.buffer = bytearray()
        self.total = 0
        self.exceeded = threading.Event()
        self.done = threading.Event()
        self.error: BaseException | None = None
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self) -> None:
        try:
            while True:
                chunk = self.stream.read(4_096)
                if not chunk:
                    return
                self.total += len(chunk)
                remaining = self.limit + 1 - len(self.buffer)
                if remaining > 0:
                    self.buffer.extend(chunk[:remaining])
                if self.total > self.limit:
                    self.exceeded.set()
                    return
        except BaseException as exc:  # pragma: no cover - OS pipe failure
            self.error = exc
        finally:
            self.done.set()

    def join(self, timeout: float = 1.0) -> bool:
        self.thread.join(timeout)
        return not self.thread.is_alive()


class _InputWriter:
    """Write the exact already-hashed PDF bytes without blocking the timeout loop."""

    def __init__(self, stream: Any, data: bytes):
        self.stream = stream
        self.data = data
        self.bytes_written = 0
        self.completed = False
        self.error: BaseException | None = None
        self.unexpected_error: BaseException | None = None
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self) -> None:
        try:
            view = memoryview(self.data)
            while self.bytes_written < len(view):
                written = self.stream.write(view[self.bytes_written :])
                if not isinstance(written, int) or written <= 0:
                    raise OSError("worker stdin made no forward progress")
                self.bytes_written += written
            self.stream.flush()
            self.completed = True
        except (BrokenPipeError, OSError) as exc:
            # A dependency-absent worker intentionally exits without consuming
            # stdin.  The closed stdout result, not this expected broken pipe,
            # determines whether that run is valid.
            self.error = exc
        except BaseException as exc:  # pragma: no cover - unexpected stream failure
            self.error = exc
            self.unexpected_error = exc
        finally:
            try:
                self.stream.close()
            except OSError:
                pass

    def join(self, timeout: float = 1.0) -> bool:
        self.thread.join(timeout)
        return not self.thread.is_alive()


def _content_state(
    *,
    requested: bool,
    status: str,
    reason: str,
    classification: str | None = None,
    confidence: float | None = None,
    pages_needing_ocr: list[int] | None = None,
) -> dict[str, Any]:
    return {
        "schema": CONTENT_SCHEMA,
        "requested": requested,
        "status": status,
        "reason": reason,
        "classification": classification,
        "confidence": confidence,
        "pages_needing_ocr": pages_needing_ocr,
    }


def _unavailable_content(reason: str) -> dict[str, Any]:
    return _content_state(requested=True, status="UNAVAILABLE", reason=reason)


def _strict_json_object(raw: bytes) -> dict[str, Any]:
    def reject_constant(value: str) -> Any:
        raise ValueError(f"non-finite JSON constant {value}")

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise _ClassifierProtocolError("worker result has duplicate keys")
            result[key] = value
        return result

    value = json.loads(
        raw.decode("utf-8", errors="strict"),
        parse_constant=reject_constant,
        object_pairs_hook=reject_duplicate_keys,
    )
    if not isinstance(value, dict):
        raise _ClassifierProtocolError("worker result is not an object")
    return value


def _validate_worker_result(payload: dict[str, Any], page_count: int) -> dict[str, Any]:
    expected = {
        "schema",
        "status",
        "reason",
        "classification",
        "confidence",
        "pages_needing_ocr",
    }
    if set(payload) != expected or payload.get("schema") != WORKER_SCHEMA:
        raise _ClassifierProtocolError("worker result has unknown or missing fields")

    status = payload.get("status")
    reason = payload.get("reason")
    classification = payload.get("classification")
    confidence = payload.get("confidence")
    pages = payload.get("pages_needing_ocr")

    if status == "UNAVAILABLE":
        if reason not in {
            "DEPENDENCY_ABSENT",
            "CLASSIFIER_ERROR",
            "INVALID_CLASSIFIER_RESULT",
        }:
            raise _ClassifierProtocolError("unknown unavailable reason")
        if classification is not None or confidence is not None or pages is not None:
            raise _ClassifierProtocolError("unavailable worker result carries values")
        return _unavailable_content(reason)

    if status != "CLASSIFIED" or reason != "CLASSIFIED":
        raise _ClassifierProtocolError("invalid worker state transition")
    if classification not in {"TEXT_AVAILABLE", "OCR_RECOMMENDED"}:
        raise _ClassifierProtocolError("unknown classification")
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not math.isfinite(float(confidence))
        or not 0.0 <= float(confidence) <= 1.0
    ):
        raise _ClassifierProtocolError("confidence is not finite and bounded")
    if not isinstance(pages, list) or len(pages) > CLASSIFIER_MAX_PAGE_ENTRIES:
        raise _ClassifierProtocolError("OCR page list is not bounded")
    if any(isinstance(page, bool) or not isinstance(page, int) for page in pages):
        raise _ClassifierProtocolError("OCR page is not an integer")
    if pages != sorted(set(pages)):
        raise _ClassifierProtocolError("OCR pages are not sorted and unique")
    if any(page < 0 or page >= page_count for page in pages):
        raise _ClassifierProtocolError("OCR page is outside the structural page count")
    if classification == "TEXT_AVAILABLE" and pages:
        raise _ClassifierProtocolError("text-available result carries OCR pages")

    return _content_state(
        requested=True,
        status="CLASSIFIED",
        reason="CLASSIFIED",
        classification=classification,
        confidence=float(confidence),
        pages_needing_ocr=pages,
    )


def _bounded_operator_detail(raw: bytes) -> str:
    # Dropping a partial/invalid trailing code unit preserves the byte ceiling;
    # replacement decoding could expand one clipped byte into a three-byte U+FFFD.
    return raw[:CLASSIFIER_OPERATOR_DETAIL_LIMIT].decode("utf-8", errors="ignore")


def _diagnostic(
    reason: str,
    *,
    detail: bytes = b"",
    stdout_bytes: int = 0,
    stderr_bytes: int = 0,
) -> dict[str, Any]:
    return {
        "schema": DIAGNOSTIC_SCHEMA,
        "reason": reason,
        "untrusted_detail": _bounded_operator_detail(detail),
        "stdout_bytes_observed": stdout_bytes,
        "stderr_bytes_observed": stderr_bytes,
    }


def _kill_worker(proc: subprocess.Popen[bytes]) -> None:
    """Terminate the isolated POSIX worker group, or the direct Windows worker.

    ``start_new_session`` makes the POSIX worker its process-group leader, so the
    saved ``proc.pid`` remains the group identifier even after the leader exits.
    Calling this on every terminal path also removes ordinary descendants that
    inherited the worker's pipes.  The portable Windows stdlib path has no
    equivalent process-tree handle and therefore kills only the direct process.
    """
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:  # pragma: no cover - exercised on Windows CI only
            proc.kill()
    except OSError:
        try:
            proc.kill()
        except OSError:
            pass


def _teardown_worker(
    proc: subprocess.Popen[bytes],
    *,
    stdout_reader: _CappedPipeReader | None = None,
    stderr_reader: _CappedPipeReader | None = None,
    input_writer: _InputWriter | None = None,
) -> None:
    """Best-effort terminal cleanup that cannot replace a closed result with a crash."""
    _kill_worker(proc)
    try:
        proc.wait(timeout=1.0)
    except (OSError, subprocess.TimeoutExpired):
        _kill_worker(proc)
        try:
            proc.wait(timeout=1.0)
        except (OSError, subprocess.TimeoutExpired):
            pass
    for helper in (input_writer, stdout_reader, stderr_reader):
        if helper is not None:
            helper.join()


def _run_content_classifier(
    data: bytes,
    *,
    page_count: int,
    worker_path: Path = CLASSIFIER_WORKER,
    timeout: float = CLASSIFIER_TIMEOUT_SECONDS,
    worker_env: dict[str, str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    command = [sys.executable, str(worker_path)]
    try:
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=worker_env,
            start_new_session=(os.name == "posix"),
        )
    except OSError as exc:
        reason = "WORKER_LAUNCH_ERROR"
        detail = f"{type(exc).__name__}: {exc}".encode("utf-8", errors="replace")
        return _unavailable_content(reason), _diagnostic(reason, detail=detail)

    if proc.stdin is None or proc.stdout is None or proc.stderr is None:  # pragma: no cover
        _teardown_worker(proc)
        reason = "WORKER_IO_ERROR"
        return _unavailable_content(reason), _diagnostic(reason)

    stdout_reader = _CappedPipeReader(proc.stdout, CLASSIFIER_STDOUT_LIMIT)
    stderr_reader = _CappedPipeReader(proc.stderr, CLASSIFIER_STDERR_LIMIT)
    input_writer = _InputWriter(proc.stdin, data)
    try:
        deadline = time.monotonic() + timeout
        forced_reason: str | None = None

        while proc.poll() is None:
            if stdout_reader.exceeded.is_set():
                forced_reason = "WORKER_STDOUT_LIMIT"
                break
            if stderr_reader.exceeded.is_set():
                forced_reason = "WORKER_STDERR_LIMIT"
                break
            if time.monotonic() >= deadline:
                forced_reason = "WORKER_TIMEOUT"
                break
            time.sleep(0.005)

        if forced_reason is not None:
            _kill_worker(proc)
        try:
            returncode = proc.wait(timeout=1.0)
        except subprocess.TimeoutExpired:  # pragma: no cover - SIGKILL should be terminal
            _kill_worker(proc)
            returncode = proc.wait(timeout=1.0)

        stdout_closed = stdout_reader.join()
        stderr_closed = stderr_reader.join()
        input_closed = input_writer.join()
        io_closed = stdout_closed and stderr_closed and input_closed
        stdout = bytes(stdout_reader.buffer)
        stderr = bytes(stderr_reader.buffer)

        if forced_reason is None:
            if stdout_reader.exceeded.is_set():
                forced_reason = "WORKER_STDOUT_LIMIT"
            elif stderr_reader.exceeded.is_set():
                forced_reason = "WORKER_STDERR_LIMIT"
            elif (
                not io_closed
                or stdout_reader.error
                or stderr_reader.error
                or input_writer.unexpected_error
            ):
                forced_reason = "WORKER_IO_ERROR"

        if forced_reason is not None:
            return _unavailable_content(forced_reason), _diagnostic(
                forced_reason,
                detail=stderr,
                stdout_bytes=stdout_reader.total,
                stderr_bytes=stderr_reader.total,
            )
        if returncode < 0:
            reason = "WORKER_SIGNAL"
            return _unavailable_content(reason), _diagnostic(
                reason,
                detail=f"signal={-returncode}; ".encode("ascii") + stderr,
                stdout_bytes=stdout_reader.total,
                stderr_bytes=stderr_reader.total,
            )
        if returncode != 0:
            reason = "WORKER_NONZERO_EXIT"
            return _unavailable_content(reason), _diagnostic(
                reason,
                detail=f"exit={returncode}; ".encode("ascii") + stderr,
                stdout_bytes=stdout_reader.total,
                stderr_bytes=stderr_reader.total,
            )

        try:
            payload = _strict_json_object(stdout)
        except (UnicodeError, ValueError, RecursionError, _ClassifierProtocolError):
            reason = "WORKER_MALFORMED_OUTPUT"
            return _unavailable_content(reason), _diagnostic(
                reason,
                detail=stderr,
                stdout_bytes=stdout_reader.total,
                stderr_bytes=stderr_reader.total,
            )
        try:
            state = _validate_worker_result(payload, page_count)
        except _ClassifierProtocolError:
            reason = "WORKER_INVALID_OUTPUT"
            return _unavailable_content(reason), _diagnostic(
                reason,
                detail=stderr,
                stdout_bytes=stdout_reader.total,
                stderr_bytes=stderr_reader.total,
            )
        if state["status"] == "CLASSIFIED" and not input_writer.completed:
            reason = "WORKER_IO_ERROR"
            return _unavailable_content(reason), _diagnostic(
                reason,
                detail=stderr,
                stdout_bytes=stdout_reader.total,
                stderr_bytes=stderr_reader.total,
            )
        return state, _diagnostic(
            state["reason"],
            detail=stderr,
            stdout_bytes=stdout_reader.total,
            stderr_bytes=stderr_reader.total,
        )
    finally:
        # A successful direct child can still leave descendants behind.  POSIX
        # cleanup therefore targets its isolated process group on every return,
        # including reasons discovered only after reader/writer joins.
        _teardown_worker(
            proc,
            stdout_reader=stdout_reader,
            stderr_reader=stderr_reader,
            input_writer=input_writer,
        )


def _write_local_diagnostic(path: Path, payload: dict[str, Any]) -> None:
    raw = (
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False, sort_keys=True)
        + "\n"
    ).encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        offset = 0
        while offset < len(raw):
            offset += os.write(fd, raw[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)


def _kid_key(kid):
    """Stable identity for a /Kids entry (indirect ref when available)."""
    ref = getattr(kid, "indirect_reference", None) or (
        kid if hasattr(kid, "idnum") else None
    )
    if ref is not None:
        return ("ref", ref.idnum, ref.generation)
    return ("id", id(kid))


def _walk_page_tree(node, visited, budget):
    """Count /Type /Page leaves under `node`, guarding cycles and runaway trees."""
    count = 0
    stack = [node]
    while stack:
        if len(visited) > budget:
            raise _TreeProblem("page-tree node budget exceeded")
        current = stack.pop()
        key = _kid_key(current)
        if key in visited:
            raise _TreeProblem("page-tree cycle detected")
        visited.add(key)
        obj = current.get_object() if hasattr(current, "get_object") else current
        node_type = str(obj.get("/Type", ""))
        if node_type == "/Page":
            count += 1
        elif node_type == "/Pages":
            kids = obj.get("/Kids", [])
            stack.extend(kids)
        else:
            raise _TreeProblem(f"unexpected page-tree node type {node_type or '(none)'}")
    return count


def _run_structural_preflight(path) -> tuple[dict[str, Any], bytes | None]:
    """Run the unchanged #512 structural preflight and retain its exact input bytes."""
    path = Path(path)
    result = {
        "schema": SCHEMA,
        "verdict": UNAVAILABLE,
        "file": str(path),
        "sha256": None,
        "declared_page_count": None,
        "enumerated_page_count": None,
        "reader_page_count": None,
        "warnings": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": TOOL_VERSION,
    }
    warnings = result["warnings"]

    try:
        data = path.read_bytes()
    except OSError as exc:
        warnings.append(f"unreadable: {exc}")
        return result, None
    result["sha256"] = sha256_hex(data)

    # Structural check independent of the parser: a PDF truncated partway through an
    # incremental update keeps an OLDER valid %%EOF, and pypdf silently reads that
    # previous revision — all three counts then agree on the OLD page tree, which would
    # PASS the exact truncation case this preflight exists to catch (codex #512 P1).
    # Non-whitespace bytes after the LAST %%EOF are that signature: record the warning
    # now, veto PASS at the verdict step. A complete incremental update always ends
    # with its own %%EOF, so legitimate multi-revision files are not flagged.
    # PDF whitespace per ISO 32000 §7.2.2 — NOT Python's: NUL is whitespace (common
    # padding after %%EOF, must not veto), vertical tab 0x0B is NOT (r3 P1).
    _PDF_WS = b"\x00\x09\x0a\x0c\x0d\x20"
    trailing_ok = True
    eof_at = data.rfind(b"%%EOF")
    if eof_at != -1 and data[eof_at + 5 :].translate(None, _PDF_WS):
        trailing_ok = False
        warnings.append(
            f"trailing-data: {len(data) - (eof_at + 5)} bytes after the final %%EOF "
            "include non-whitespace content (possible truncated incremental update)"
        )

    if pypdf is None:
        warnings.append("pypdf-not-installed: preflight cannot parse the document")
        return result, data

    collector = _WarningCollector()
    pypdf_logger = logging.getLogger("pypdf")
    pypdf_logger.addHandler(collector)
    try:
        try:
            reader = pypdf.PdfReader(io.BytesIO(data))  # bytes already in hand for the hash
        except Exception as exc:  # malformed beyond pypdf's tolerance
            warnings.append(f"parse-error: {exc}")
            return result, data

        if getattr(reader, "is_encrypted", False):
            warnings.append("encrypted: preflight cannot verify an encrypted document")
            return result, data

        try:
            root = reader.trailer["/Root"].get_object()
            pages_node = root["/Pages"]
            pages_obj = pages_node.get_object()
            raw_count = pages_obj["/Count"]
            # Require an actual PDF integer object. `int()` would coerce a float
            # /Count 2.7 to 2 (or a text string "2") and then agree with two real
            # leaves — a malformed page tree must be UNAVAILABLE, not PASS (r2 P1).
            # pypdf NumberObject subclasses int; FloatObject subclasses float.
            if isinstance(raw_count, bool) or not isinstance(raw_count, int):
                warnings.append(
                    f"page-tree-unresolvable: /Count is not an integer object "
                    f"({type(raw_count).__name__}: {raw_count!r})"
                )
                return result, data
            declared = int(raw_count)
        except Exception as exc:
            warnings.append(f"page-tree-unresolvable: {exc}")
            return result, data
        result["declared_page_count"] = declared

        try:
            enumerated = _walk_page_tree(pages_node, set(), NODE_BUDGET)
        except Exception as exc:  # incl. _TreeProblem — same degradation either way
            warnings.append(f"page-tree-walk: {exc}")
            return result, data
        result["enumerated_page_count"] = enumerated

        # The walk above verified the /Kids tree is cycle-free, so flattening the same
        # tree cannot spin.
        try:
            reader_count = len(reader.pages)
        except Exception as exc:
            warnings.append(f"reader-page-list: {exc}")
            return result, data
        result["reader_page_count"] = reader_count

        # Xref-coverage check (r2 P1): a malformed incremental update can append new
        # objects PLUS a syntactically complete startxref that still points at the
        # PREVIOUS revision's xref, followed by its own %%EOF — the trailing-data
        # check then sees nothing after the final %%EOF while pypdf silently reads
        # the old revision. Cross-check: every raw `N M obj` header in the file must
        # be an object number the parsed xref chain knows about. An unreferenced
        # object number = a revision the active xref chain cannot see. (Offsets are
        # deliberately not compared — pypdf normalizes them; object-number coverage
        # is the stable signal. Best-effort: if pypdf's xref internals are absent,
        # skip rather than crash.)
        try:
            xref_map = getattr(reader, "xref", None)
            if isinstance(xref_map, dict) and xref_map:
                known_objs = set()
                for gen_table in xref_map.values():
                    if isinstance(gen_table, dict):
                        known_objs.update(gen_table.keys())
                compressed = getattr(reader, "xref_objStm", None)
                if isinstance(compressed, dict):
                    known_objs.update(compressed.keys())
                # Header token separators implement the FULL ISO 32000 lexer model,
                # not Python's \s and not just whitespace: PDF permits bare-CR line
                # endings (r4 P1), treats NUL as whitespace (r5 P1), and treats
                # %-comments-to-end-of-line as token separators (r7 P1) — so
                # `2 0%note\nobj` is a valid header. Anything the PDF lexer accepts
                # as a separator must not hide a header from the coverage checks.
                # Numeric tokens carry the full ISO 32000 integer form too (r8 P1):
                # an optional sign and any leading-zero padding are valid and
                # accepted by pypdf's int() coercion, so `+2 0 obj` or
                # `00000000002 0 obj` must not hide from the scan either.
                _ws = rb"[\x00\t\n\x0c\r ]"
                _sep = rb"(?:" + _ws + rb"|%[^\r\n]*[\r\n])"
                _num = rb"[+-]?0*\d{1,10}"
                raw_offsets: dict[int, list[int]] = {}
                for m in re.finditer(
                    rb"(?:^|" + _sep + rb")" + _sep + rb"*(" + _num + rb")" + _sep + rb"+" + _num + _sep + rb"+obj\b",
                    data,
                ):
                    raw_offsets.setdefault(int(m.group(1)), []).append(m.start(1))
                orphaned = set(raw_offsets) - {int(n) for n in known_objs}
                if orphaned:
                    warnings.append(
                        "xref-coverage: object number(s) "
                        f"{sorted(orphaned)[:5]} present in the file but absent from "
                        "the active xref chain (possible stale startxref / "
                        "unreachable newer revision)"
                    )
                    trailing_ok = False
                # Redefined-object variant (r3 P1): a malformed update can append a
                # REPLACEMENT body for an existing object number plus a stale
                # startxref — number-membership alone then sees no orphan while
                # pypdf reads the old copy. The newest raw copy of every directly-
                # stored object must be the one the active chain references.
                # Calibration guard: pypdf applies a global delta when a file has
                # junk before %PDF; if NO active offset matches any raw offset the
                # comparison is uncalibrated — skip rather than mass-flag.
                direct_offsets = {}
                for gen_table in xref_map.values():
                    if isinstance(gen_table, dict):
                        for objnum, off in gen_table.items():
                            if isinstance(off, int) and int(objnum) in raw_offsets:
                                direct_offsets[int(objnum)] = off
                if direct_offsets and any(
                    off in raw_offsets[n] for n, off in direct_offsets.items()
                ):
                    superseded = sorted(
                        n
                        for n, off in direct_offsets.items()
                        if max(raw_offsets[n]) > off
                    )
                    if superseded:
                        warnings.append(
                            "xref-coverage: later unreferenced revision(s) of object "
                            f"number(s) {superseded[:5]} exist after the copy the "
                            "active xref chain references (possible stale startxref)"
                        )
                        trailing_ok = False
                # Compressed-object variant (r5 P1): the active copy of N lives
                # inside an object stream (no direct offset in reader.xref), so the
                # loop above never inspects it — but a direct raw replacement of N
                # appended AFTER its container, with a stale startxref, is exactly
                # the unreachable-newer-revision case. A raw copy BEFORE the
                # container is the legitimate superseded-into-objstm update and is
                # not flagged.
                if isinstance(compressed, dict):
                    compressed_superseded = []
                    for objnum, ref in compressed.items():
                        n = int(objnum)
                        if n not in raw_offsets or n in direct_offsets:
                            continue
                        container = ref[0] if isinstance(ref, (tuple, list)) and ref else None
                        container_off = None
                        if container is not None:
                            for gen_table in xref_map.values():
                                if (
                                    isinstance(gen_table, dict)
                                    and container in gen_table
                                    and isinstance(gen_table[container], int)
                                ):
                                    container_off = gen_table[container]
                                    break
                        if container_off is not None and max(raw_offsets[n]) > container_off:
                            compressed_superseded.append(n)
                    if compressed_superseded:
                        warnings.append(
                            "xref-coverage: direct replacement(s) of compressed object "
                            f"number(s) {sorted(compressed_superseded)[:5]} appear after "
                            "their object-stream container (possible stale startxref)"
                        )
                        trailing_ok = False
        except Exception as exc:  # best-effort cross-check, never a crash path
            warnings.append(f"xref-coverage-skipped: {exc}")
    finally:
        pypdf_logger.removeHandler(collector)
        # Append captured parser chatter HERE so every early return above (encryption,
        # unresolvable tree, walk problems) still carries it — the repair warning that
        # preceded a later structural error is part of the sidecar contract too.
        warnings.extend(f"pypdf: {m}" for m in collector.messages)

    if not (declared == enumerated == reader_count):
        result["verdict"] = FAIL
        return result, data
    if declared <= 0:
        warnings.append("empty-page-tree: agreeing counts but zero pages")
        return result, data
    if collector.messages or not trailing_ok:
        # Counts agree, but the parse needed repair or the file carries data after its
        # final %%EOF — cannot vouch, per the spec.
        return result, data
    result["verdict"] = PASS
    return result, data


def _run_preflight(
    path: str | Path,
    *,
    classify_content: bool = False,
    worker_path: Path = CLASSIFIER_WORKER,
    classifier_timeout: float = CLASSIFIER_TIMEOUT_SECONDS,
    worker_env: dict[str, str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    result, data = _run_structural_preflight(path)
    diagnostic = _diagnostic("NOT_REQUESTED")

    if not classify_content:
        return result, diagnostic
    result["tool"] = CONTENT_TOOL_VERSION
    result["verdict_scope"] = "STRUCTURE_ONLY"
    result["content_advisory"] = "CONTENT_UNAVAILABLE"
    result["content_classification"] = _unavailable_content("STRUCTURAL_NOT_PASS")
    if result["verdict"] != PASS or data is None:
        reason = "STRUCTURAL_NOT_PASS"
        result["content_advisory"] = "STRUCTURAL_UNAVAILABLE"
        result["content_classification"] = _unavailable_content(reason)
        return result, _diagnostic(reason)

    page_count = result["reader_page_count"]
    if isinstance(page_count, bool) or not isinstance(page_count, int) or page_count <= 0:
        # Defensive: PASS already proves this cannot happen, but do not invoke a
        # native child if that structural invariant ever drifts.
        reason = "STRUCTURAL_NOT_PASS"
        result["content_advisory"] = "STRUCTURAL_UNAVAILABLE"
        result["content_classification"] = _unavailable_content(reason)
        return result, _diagnostic(reason)

    state, diagnostic = _run_content_classifier(
        data,
        page_count=page_count,
        worker_path=worker_path,
        timeout=classifier_timeout,
        worker_env=worker_env,
    )
    result["content_classification"] = state
    if state["status"] == "CLASSIFIED":
        result["content_advisory"] = state["classification"]
    else:
        result["content_advisory"] = "CONTENT_UNAVAILABLE"
    return result, diagnostic


def run_preflight(path, *, classify_content: bool = False) -> dict[str, Any]:
    """Return a structural sidecar, optionally with isolated content advisory data."""
    result, _diagnostic_payload = _run_preflight(
        path,
        classify_content=classify_content,
    )
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="PDF read-integrity preflight (#512): PASS/FAIL/UNAVAILABLE sidecar "
        "for page-anchor trust decisions."
    )
    parser.add_argument("pdf", help="path to the locally-read PDF")
    parser.add_argument(
        "--output",
        help="write the JSON sidecar here instead of stdout",
    )
    parser.add_argument(
        "--classify-content",
        action="store_true",
        help=(
            "opt in to the isolated optional text/OCR advisory; the structural "
            "verdict remains unchanged"
        ),
    )
    parser.add_argument(
        "--classifier-diagnostics",
        help=(
            "exclusive local 0600 JSON for bounded untrusted worker detail; "
            "requires --classify-content and is never referenced by the sidecar"
        ),
    )
    args = parser.parse_args(argv)

    if args.classifier_diagnostics and not args.classify_content:
        parser.error("--classifier-diagnostics requires --classify-content")

    result, diagnostic = _run_preflight(
        args.pdf,
        classify_content=args.classify_content,
    )
    if args.classifier_diagnostics:
        try:
            _write_local_diagnostic(Path(args.classifier_diagnostics), diagnostic)
        except OSError as exc:
            parser.error(f"cannot create classifier diagnostic: {exc}")

    sidecar = json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )
    if args.output:
        Path(args.output).write_text(sidecar + "\n", encoding="utf-8")
    else:
        print(sidecar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
