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

CLI: `python scripts/pdf_read_preflight.py FILE [--output SIDECAR.json]`. Exit 0 whenever
a verdict was produced (the verdict is data, not an error; orchestration consumes the
JSON without exit-code branching); exit 2 on usage errors only.

Design: docs/design/2026-07-20-512-pdf-read-preflight-spec.md.
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from audit_snapshot import sha256_hex
except ImportError:  # pragma: no cover - dual-path import (verify_submission_package precedent)
    from scripts.audit_snapshot import sha256_hex

try:
    import pypdf
except ImportError:  # degrade to UNAVAILABLE, mirroring verify_submission_package.py
    pypdf = None

TOOL_VERSION = "pdf_read_preflight/1.0.0"
SCHEMA = "pdf_read_preflight/1"

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


def run_preflight(path) -> dict:
    """Run the read-integrity preflight on one PDF; always returns a sidecar dict."""
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
        return result
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
        return result

    collector = _WarningCollector()
    pypdf_logger = logging.getLogger("pypdf")
    pypdf_logger.addHandler(collector)
    try:
        try:
            reader = pypdf.PdfReader(io.BytesIO(data))  # bytes already in hand for the hash
        except Exception as exc:  # malformed beyond pypdf's tolerance
            warnings.append(f"parse-error: {exc}")
            return result

        if getattr(reader, "is_encrypted", False):
            warnings.append("encrypted: preflight cannot verify an encrypted document")
            return result

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
                return result
            declared = int(raw_count)
        except Exception as exc:
            warnings.append(f"page-tree-unresolvable: {exc}")
            return result
        result["declared_page_count"] = declared

        try:
            enumerated = _walk_page_tree(pages_node, set(), NODE_BUDGET)
        except Exception as exc:  # incl. _TreeProblem — same degradation either way
            warnings.append(f"page-tree-walk: {exc}")
            return result
        result["enumerated_page_count"] = enumerated

        # The walk above verified the /Kids tree is cycle-free, so flattening the same
        # tree cannot spin.
        try:
            reader_count = len(reader.pages)
        except Exception as exc:
            warnings.append(f"reader-page-list: {exc}")
            return result
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
        return result
    if declared <= 0:
        warnings.append("empty-page-tree: agreeing counts but zero pages")
        return result
    if collector.messages or not trailing_ok:
        # Counts agree, but the parse needed repair or the file carries data after its
        # final %%EOF — cannot vouch, per the spec.
        return result
    result["verdict"] = PASS
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
    args = parser.parse_args(argv)

    sidecar = json.dumps(run_preflight(args.pdf), indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(sidecar + "\n", encoding="utf-8")
    else:
        print(sidecar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
