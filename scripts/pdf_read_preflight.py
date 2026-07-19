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
    trailing_ok = True
    eof_at = data.rfind(b"%%EOF")
    if eof_at != -1 and data[eof_at + 5 :].strip():
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
            declared = int(pages_obj["/Count"])
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
