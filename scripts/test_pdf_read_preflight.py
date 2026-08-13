"""Tests for scripts/pdf_read_preflight.py (#512 PDF read-integrity preflight).

Fixtures are synthetic PDFs assembled in-test with correct xref offsets (no binary
fixture files): a flat valid document, a nested page tree, a root /Count that lies,
a truncated tail, an encrypted trailer, a page-tree cycle, and non-PDF bytes. The
preflight must answer PASS only when the declared root /Count, its own /Kids-walk
enumeration, and pypdf's flattened page list all agree with no parser warnings —
anything less confident lands in FAIL (counts disagree) or UNAVAILABLE (cannot
vouch). Design: docs/design/2026-07-20-512-pdf-read-preflight-spec.md.
"""

import ast
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from unittest import mock
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pdf_read_preflight as preflight  # noqa: E402

WORKER_PATH = REPO_ROOT / "scripts" / "pdf_content_classifier_worker.py"
PDF_CONTRACTS = REPO_ROOT / "shared" / "contracts" / "pdf"


# --- synthetic-PDF assembly ---------------------------------------------------------------


def _build_pdf(objects):
    """Assemble a classic-xref PDF from `objects` (list of object BODIES, bytes, without
    the `N 0 obj`/`endobj` wrapper; object numbers are 1-based list positions). Returns
    the full file bytes with a correct xref table and trailer pointing at object 1 as
    /Root."""
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref_at = len(out)
    out += b"xref\n0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += (
        b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
        % (len(objects) + 1, xref_at)
    )
    return bytes(out)


def _page(parent_num):
    return b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 612 792] >>" % parent_num


def _flat_pdf(page_count=2, declared=None):
    """Catalog(1) -> Pages(2) -> `page_count` leaf pages. `declared` overrides /Count."""
    declared = page_count if declared is None else declared
    kids = b" ".join(b"%d 0 R" % (3 + i) for i in range(page_count))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, declared),
    ]
    objects += [_page(2) for _ in range(page_count)]
    return _build_pdf(objects)


def _nested_pdf():
    """Root Pages(2) -> [inner Pages(3) -> [page(4), page(5)], page(6)]; 3 leaves."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R 6 0 R] /Count 3 >>",
        b"<< /Type /Pages /Parent 2 0 R /Kids [4 0 R 5 0 R] /Count 2 >>",
        _page(3),
        _page(3),
        _page(2),
    ]
    return _build_pdf(objects)


def _cyclic_pdf():
    """Pages(2) -> Pages(3) -> back to Pages(2): a /Kids cycle, zero real leaves."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Pages /Parent 2 0 R /Kids [2 0 R] /Count 1 >>",
    ]
    return _build_pdf(objects)


def _encrypted_pdf():
    """Structurally flat PDF whose trailer carries /Encrypt — preflight must not vouch."""
    raw = _flat_pdf(1)
    return raw.replace(
        b"/Root 1 0 R >>",
        b"/Root 1 0 R /Encrypt << /Filter /Standard /V 1 /R 2 /O (x) /U (x) /P -1 >> >>",
    )


def _objstm_pdf():
    """PDF 1.5-style fixture: catalog/pages/page live in an object stream (obj 4),
    the xref is a cross-reference stream (obj 5); both unfiltered so offsets stay
    computable. Exercises the compressed-object side of the coverage checks."""
    import struct

    bodies = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",
    ]
    offs, payload = [], b""
    for b in bodies:
        offs.append(len(payload))
        payload += b + b" "
    header = b" ".join(b"%d %d" % (i + 1, o) for i, o in enumerate(offs)) + b" "
    content = header + payload
    out = bytearray(b"%PDF-1.5\n%\xe2\xe3\xcf\xd3\n")
    objstm_at = len(out)
    out += (
        b"4 0 obj\n<< /Type /ObjStm /N 3 /First %d /Length %d >>\nstream\n"
        % (len(header), len(content))
    ) + content + b"\nendstream\nendobj\n"
    xref_at = len(out)
    rows = [(0, 0, 0), (2, 4, 0), (2, 4, 1), (2, 4, 2), (1, objstm_at, 0), (1, xref_at, 0)]
    xdata = b"".join(struct.pack(">BHB", *r) for r in rows)
    out += (
        b"5 0 obj\n<< /Type /XRef /Size 6 /Root 1 0 R /W [1 2 1] /Index [0 6] /Length %d >>\nstream\n"
        % len(xdata)
    ) + xdata + b"\nendstream\nendobj\n"
    out += b"startxref\n%d\n%%%%EOF\n" % xref_at
    return bytes(out)


def _write(tmpdir, name, data):
    p = Path(tmpdir) / name
    p.write_bytes(data)
    return p


def _write_worker(tmpdir, source, name="fake_worker.py"):
    path = Path(tmpdir) / name
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


def _classified_payload(classification="TEXT_AVAILABLE", confidence=0.97, pages=None):
    return {
        "schema": "pdf_content_classifier_worker/1",
        "status": "CLASSIFIED",
        "reason": "CLASSIFIED",
        "classification": classification,
        "confidence": confidence,
        "pages_needing_ocr": [] if pages is None else pages,
    }


class PreflightVerdictTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def run_on(self, data, name="doc.pdf"):
        return preflight.run_preflight(_write(self.tmp, name, data))

    def test_flat_valid_pdf_passes_with_agreeing_counts(self):
        r = self.run_on(_flat_pdf(2))
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(
            (r["declared_page_count"], r["enumerated_page_count"], r["reader_page_count"]),
            (2, 2, 2),
        )
        self.assertEqual(r["warnings"], [])

    def test_nested_page_tree_enumerates_leaves_only(self):
        r = self.run_on(_nested_pdf())
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(r["enumerated_page_count"], 3)
        self.assertEqual(r["declared_page_count"], 3)

    def test_lying_root_count_fails(self):
        # Root declares 5 pages, the tree holds 2 — the mispagination signal itself.
        r = self.run_on(_flat_pdf(2, declared=5))
        self.assertEqual(r["verdict"], "FAIL", r)
        self.assertEqual(r["declared_page_count"], 5)
        self.assertEqual(r["enumerated_page_count"], 2)

    def test_truncated_pdf_never_passes(self):
        whole = _flat_pdf(3)
        r = self.run_on(whole[: int(len(whole) * 0.6)], name="cut.pdf")
        self.assertNotEqual(r["verdict"], "PASS", r)

    def test_encrypted_pdf_unavailable(self):
        r = self.run_on(_encrypted_pdf())
        self.assertEqual(r["verdict"], "UNAVAILABLE", r)
        self.assertTrue(any("encrypt" in w.lower() for w in r["warnings"]), r["warnings"])

    def test_page_tree_cycle_unavailable_not_hang(self):
        r = self.run_on(_cyclic_pdf())
        self.assertEqual(r["verdict"], "UNAVAILABLE", r)
        self.assertTrue(any("cycle" in w.lower() for w in r["warnings"]), r["warnings"])

    def test_non_pdf_bytes_unavailable(self):
        r = self.run_on(b"just some text, not a PDF at all\n", name="not.pdf")
        self.assertEqual(r["verdict"], "UNAVAILABLE", r)

    def test_missing_file_unavailable_with_null_hash(self):
        r = preflight.run_preflight(Path(self.tmp) / "nope.pdf")
        self.assertEqual(r["verdict"], "UNAVAILABLE", r)
        self.assertIsNone(r["sha256"])

    def test_pypdf_missing_unavailable(self):
        real = preflight.pypdf
        preflight.pypdf = None
        try:
            r = self.run_on(_flat_pdf(1))
        finally:
            preflight.pypdf = real
        self.assertEqual(r["verdict"], "UNAVAILABLE", r)
        self.assertTrue(any("pypdf" in w for w in r["warnings"]), r["warnings"])

    def test_zero_page_tree_never_passes(self):
        r = self.run_on(_flat_pdf(0))
        self.assertNotEqual(r["verdict"], "PASS", r)

    def test_trailing_data_after_final_eof_never_passes(self):
        # A PDF truncated partway through an incremental update keeps the OLDER valid
        # %%EOF; pypdf silently reads that revision and all three counts agree on the
        # old tree. The trailing-bytes check must veto PASS (codex #512 P1).
        data = _flat_pdf(2) + b"6 0 obj\n<< /Type /Page /Parent 2 0 R >>\n"
        r = self.run_on(data, name="cut_incremental.pdf")
        self.assertEqual(r["verdict"], "UNAVAILABLE", r)
        self.assertTrue(any("trailing-data" in w for w in r["warnings"]), r["warnings"])

    def test_whitespace_after_final_eof_still_passes(self):
        r = self.run_on(_flat_pdf(2) + b"\n\n  \n")
        self.assertEqual(r["verdict"], "PASS", r)

    def test_stale_startxref_with_own_eof_never_passes(self):
        # Malformed incremental update: new objects appended, then a syntactically
        # complete startxref that still points at the PREVIOUS revision's xref,
        # followed by its own %%EOF. The trailing-data check alone sees nothing after
        # the final %%EOF; the xref-coverage check must flag the unreachable object
        # (codex #512 r2 P1).
        base = _build_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
                _page(2),
            ]
        )
        old_startxref = base[base.rfind(b"startxref") :]  # points at revision-1 xref
        stale = base + b"\n4 0 obj\n<< /Type /Page /Parent 2 0 R >>\nendobj\n" + old_startxref
        r = self.run_on(stale, name="stale.pdf")
        self.assertNotEqual(r["verdict"], "PASS", r)
        self.assertTrue(any("xref-coverage" in w for w in r["warnings"]), r["warnings"])

    def test_nul_padding_after_final_eof_still_passes(self):
        # NUL is PDF whitespace (ISO 32000 §7.2.2) and a common post-%%EOF padding;
        # Python's strip() does not know that (codex #512 r3 P1).
        r = self.run_on(_flat_pdf(2) + b"\x00" * 16)
        self.assertEqual(r["verdict"], "PASS", r)

    def test_vertical_tab_after_final_eof_vetoes_pass(self):
        # 0x0B is Python whitespace but NOT PDF whitespace — it is data.
        r = self.run_on(_flat_pdf(2) + b"\x0b")
        self.assertNotEqual(r["verdict"], "PASS", r)

    def test_redefined_object_with_stale_startxref_never_passes(self):
        # Malformed update variant (codex #512 r3 P1): a REPLACEMENT body for an
        # EXISTING object number is appended, then a stale copy of the original
        # startxref/%%EOF. Object-number membership sees no orphan; the newest-copy-
        # must-be-referenced check must flag it.
        base = _flat_pdf(2)
        old_startxref = base[base.rfind(b"startxref") :]
        replacement = b"\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        r = self.run_on(base + replacement + old_startxref, name="redefined.pdf")
        self.assertNotEqual(r["verdict"], "PASS", r)
        self.assertTrue(any("xref-coverage" in w for w in r["warnings"]), r["warnings"])

    def test_cr_only_line_endings_still_pass(self):
        # ISO 32000 permits bare-CR line endings; byte count is unchanged so the
        # xref offsets stay valid.
        r = self.run_on(_flat_pdf(2).replace(b"\n", b"\r"), name="cr.pdf")
        self.assertEqual(r["verdict"], "PASS", r)

    def test_cr_only_stale_startxref_never_passes(self):
        # r4 P1: a CR-only file must not blind the object-header scan — the stale
        # startxref variant has to be caught in this convention too.
        base = _flat_pdf(2).replace(b"\n", b"\r")
        old_startxref = base[base.rfind(b"startxref") :]
        replacement = b"\r2 0 obj\r<< /Type /Pages /Kids [3 0 R] /Count 1 >>\rendobj\r"
        r = self.run_on(base + replacement + old_startxref, name="cr_stale.pdf")
        self.assertNotEqual(r["verdict"], "PASS", r)
        self.assertTrue(any("xref-coverage" in w for w in r["warnings"]), r["warnings"])

    def test_objstm_xref_stream_pdf_passes(self):
        # Object-stream + cross-reference-stream layout must parse and PASS.
        r = self.run_on(_objstm_pdf(), name="objstm.pdf")
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(r["enumerated_page_count"], 1)

    def test_direct_replacement_of_compressed_object_never_passes(self):
        # r5 P1: active copy of object 2 lives inside an object stream; a direct raw
        # replacement appended AFTER the container with a stale startxref is
        # unreachable but is neither orphaned nor covered by the direct-offset loop.
        base = _objstm_pdf()
        old_startxref = base[base.rfind(b"startxref") :]
        replacement = b"\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        r = self.run_on(base + replacement + old_startxref, name="objstm_stale.pdf")
        self.assertNotEqual(r["verdict"], "PASS", r)
        self.assertTrue(any("compressed object" in w for w in r["warnings"]), r["warnings"])

    def test_nul_preceded_replacement_header_never_passes(self):
        # r5 P1: NUL is PDF whitespace; a replacement header preceded only by NUL
        # padding must still be seen by the coverage scan.
        base = _flat_pdf(2)
        old_startxref = base[base.rfind(b"startxref") :]
        replacement = b"\x002 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        r = self.run_on(base + replacement + old_startxref, name="nul_stale.pdf")
        self.assertNotEqual(r["verdict"], "PASS", r)
        self.assertTrue(any("xref-coverage" in w for w in r["warnings"]), r["warnings"])

    def test_ten_digit_object_id_replacement_never_passes(self):
        # r6 P1: object numbers may reach ten digits; the header scan's digit cap
        # must not blind the coverage checks to such replacements.
        base = _flat_pdf(2)
        old_startxref = base[base.rfind(b"startxref") :]
        replacement = b"\n1000000001 0 obj\n<< /Type /Pages /Count 9 >>\nendobj\n"
        r = self.run_on(base + replacement + old_startxref, name="tendigit.pdf")
        self.assertNotEqual(r["verdict"], "PASS", r)
        self.assertTrue(any("xref-coverage" in w for w in r["warnings"]), r["warnings"])

    def test_comment_separated_replacement_header_never_passes(self):
        # r7 P1: %-comments are token separators in the PDF lexer, so
        # `2 0%note\nobj` is a valid object header the scan must still see.
        base = _flat_pdf(2)
        old_startxref = base[base.rfind(b"startxref") :]
        replacement = b"\n2 0%note\nobj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        r = self.run_on(base + replacement + old_startxref, name="comment_stale.pdf")
        self.assertNotEqual(r["verdict"], "PASS", r)
        self.assertTrue(any("xref-coverage" in w for w in r["warnings"]), r["warnings"])

    def test_signed_or_zero_padded_replacement_header_never_passes(self):
        # r8 P1: ISO 32000 integers permit a leading sign (and arbitrary zero
        # padding); pypdf's header reader coerces via int(), so these header forms
        # must not hide from the scan.
        base = _flat_pdf(2)
        old_startxref = base[base.rfind(b"startxref") :]
        for header in (b"+2 0 obj", b"00000000002 0 obj"):
            with self.subTest(header=header):
                replacement = (
                    b"\n" + header + b"\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
                )
                r = self.run_on(base + replacement + old_startxref, name="signed_stale.pdf")
                self.assertNotEqual(r["verdict"], "PASS", r)
                self.assertTrue(any("xref-coverage" in w for w in r["warnings"]), r["warnings"])

    def test_non_integer_count_unavailable(self):
        # /Count 1.0 — int() would truncate-coerce and agree with one real leaf; a
        # malformed page tree must be UNAVAILABLE, not PASS (codex #512 r2 P1).
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1.0 >>",
            _page(2),
        ]
        r = self.run_on(_build_pdf(objects), name="floatcount.pdf")
        self.assertEqual(r["verdict"], "UNAVAILABLE", r)
        self.assertTrue(any("not an integer" in w for w in r["warnings"]), r["warnings"])

    def test_parser_warnings_survive_early_exit(self):
        # pypdf logs a repair warning, THEN parsing dies: the sidecar must carry BOTH
        # the captured warning and the later error (codex #512 P2 — early returns must
        # not drop collector messages).
        import logging as _logging

        class _StubReader:
            def __init__(self, stream):
                _logging.getLogger("pypdf").warning("synthetic repair warning")
                raise ValueError("boom")

        class _StubPypdf:
            PdfReader = _StubReader

        real = preflight.pypdf
        preflight.pypdf = _StubPypdf
        try:
            r = self.run_on(_flat_pdf(1))
        finally:
            preflight.pypdf = real
        self.assertEqual(r["verdict"], "UNAVAILABLE", r)
        self.assertTrue(any(w == "pypdf: synthetic repair warning" for w in r["warnings"]), r["warnings"])
        self.assertTrue(any(w.startswith("parse-error:") for w in r["warnings"]), r["warnings"])


class ContentClassificationSandboxTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def run_with_worker(self, worker, *, data=None, timeout=1.0, worker_env=None):
        pdf = _write(self.tmp, "doc.pdf", _flat_pdf(1) if data is None else data)
        result = preflight._run_preflight(
            pdf,
            classify_content=True,
            worker_path=Path(worker),
            classifier_timeout=timeout,
            worker_env=worker_env,
        )
        schema = json.loads((PDF_CONTRACTS / "pdf_read_preflight.schema.json").read_text())
        Draft202012Validator(schema).validate(result[0])
        return result

    def assert_process_gone(self, pid):
        def alive():
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return False
            return True

        try:
            deadline = time.monotonic() + 2.0
            while alive() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertFalse(alive(), f"descendant {pid} survived")
        finally:
            if alive():
                os.kill(pid, 9)

    def json_worker(self, payload):
        raw = json.dumps(payload, allow_nan=True)
        return _write_worker(
            self.tmp,
            f"""
            import sys
            sys.stdin.buffer.read()
            sys.stdout.write({raw!r})
            """,
        )

    def test_default_path_is_not_requested_and_never_spawns_worker(self):
        pdf = _write(self.tmp, "default.pdf", _flat_pdf(1))
        result, diagnostic = preflight._run_preflight(
            pdf,
            worker_path=self.tmp / "must-not-exist.py",
        )
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["tool"], "pdf_read_preflight/1.0.0")
        self.assertNotIn("verdict_scope", result)
        self.assertNotIn("content_advisory", result)
        self.assertNotIn("content_classification", result)
        self.assertEqual(diagnostic["reason"], "NOT_REQUESTED")

    def test_nonpass_structural_result_never_spawns_worker(self):
        result, diagnostic = self.run_with_worker(
            self.tmp / "must-not-exist.py",
            data=b"not a PDF",
        )
        self.assertNotEqual(result["verdict"], "PASS")
        self.assertEqual(result["content_advisory"], "STRUCTURAL_UNAVAILABLE")
        self.assertEqual(result["content_classification"]["reason"], "STRUCTURAL_NOT_PASS")
        self.assertEqual(diagnostic["reason"], "STRUCTURAL_NOT_PASS")

    def test_valid_text_result_is_observable_without_changing_structural_verdict(self):
        worker = self.json_worker(_classified_payload())
        result, _ = self.run_with_worker(worker)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["verdict_scope"], "STRUCTURE_ONLY")
        self.assertEqual(result["content_advisory"], "TEXT_AVAILABLE")
        self.assertEqual(result["content_classification"]["classification"], "TEXT_AVAILABLE")

    def test_scanned_result_is_not_misrepresented_as_text_usable(self):
        worker = self.json_worker(
            _classified_payload("OCR_RECOMMENDED", confidence=0.95, pages=[0])
        )
        result, _ = self.run_with_worker(worker)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["verdict_scope"], "STRUCTURE_ONLY")
        self.assertEqual(result["content_advisory"], "OCR_RECOMMENDED")
        self.assertEqual(result["content_classification"]["pages_needing_ocr"], [0])

    def _module_env(self, module_source):
        module_root = self.tmp / f"module-{len(list(self.tmp.glob('module-*')))}"
        module_root.mkdir()
        (module_root / "pdf_inspector.py").write_text(
            textwrap.dedent(module_source),
            encoding="utf-8",
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = str(module_root)
        return env

    def _absent_module_env(self):
        module_root = self.tmp / f"module-{len(list(self.tmp.glob('module-*')))}"
        module_root.mkdir()
        (module_root / "sitecustomize.py").write_text(
            textwrap.dedent(
                """
                import sys

                sys.path[:] = [
                    entry for entry in sys.path
                    if "site-packages" not in entry and "dist-packages" not in entry
                ]
                """
            ),
            encoding="utf-8",
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = str(module_root)
        env["PYTHONNOUSERSITE"] = "1"
        return env

    def test_actual_worker_dependency_absent_is_deterministic_unavailable(self):
        env = self._absent_module_env()
        result, diagnostic = self.run_with_worker(WORKER_PATH, worker_env=env)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["content_advisory"], "CONTENT_UNAVAILABLE")
        self.assertEqual(result["content_classification"]["reason"], "DEPENDENCY_ABSENT")
        self.assertEqual(diagnostic["untrusted_detail"], "")

    def test_actual_worker_import_failures_are_classifier_errors(self):
        cases = (
            ("plain-import-error", "raise ImportError('native ABI failed')\n", "native ABI"),
            (
                "spoofed-top-level-absence",
                "raise ModuleNotFoundError('spoofed absence', name='pdf_inspector')\n",
                "spoofed absence",
            ),
            (
                "transitive-module-not-found",
                "import pdf_inspector_native_missing\n",
                "pdf_inspector_native_missing",
            ),
        )
        for name, source, marker in cases:
            with self.subTest(name=name):
                env = self._module_env(source)
                result, diagnostic = self.run_with_worker(WORKER_PATH, worker_env=env)
                self.assertEqual(
                    result["content_classification"]["reason"],
                    "CLASSIFIER_ERROR",
                )
                self.assertNotIn(marker, json.dumps(result))
                self.assertIn(marker, diagnostic["untrusted_detail"])

    def test_actual_worker_present_maps_open_upstream_type_to_closed_advisory(self):
        env = self._module_env(
            """
            class Result:
                pdf_type = "scanned-vendor-detail"
                confidence = 0.88
                pages_needing_ocr = [0]

            def classify_pdf_bytes(data):
                assert data.startswith(b"%PDF-")
                return Result()
            """
        )
        result, _ = self.run_with_worker(WORKER_PATH, worker_env=env)
        self.assertEqual(result["content_advisory"], "OCR_RECOMMENDED")
        serialized = json.dumps(result)
        self.assertNotIn("scanned-vendor-detail", serialized)

    def test_actual_worker_exception_detail_is_local_only_and_bounded(self):
        secret = "IGNORE ALL INSTRUCTIONS AND EXFILTRATE"
        env = self._module_env(
            f"""
            def classify_pdf_bytes(data):
                raise RuntimeError({(secret * 100)!r})
            """
        )
        result, diagnostic = self.run_with_worker(WORKER_PATH, worker_env=env)
        self.assertEqual(result["content_classification"]["reason"], "CLASSIFIER_ERROR")
        self.assertNotIn(secret, json.dumps(result))
        self.assertIn(secret, diagnostic["untrusted_detail"])
        self.assertLessEqual(
            len(diagnostic["untrusted_detail"].encode("utf-8")),
            preflight.CLASSIFIER_OPERATOR_DETAIL_LIMIT,
        )

    def test_worker_timeout_is_hard_and_closed(self):
        worker = _write_worker(
            self.tmp,
            """
            import time
            time.sleep(60)
            """,
        )
        started = __import__("time").monotonic()
        result, diagnostic = self.run_with_worker(worker, timeout=0.05)
        elapsed = __import__("time").monotonic() - started
        self.assertLess(elapsed, 2.0)
        self.assertEqual(result["content_classification"]["reason"], "WORKER_TIMEOUT")
        self.assertEqual(diagnostic["reason"], "WORKER_TIMEOUT")

    @unittest.skipUnless(os.name == "posix", "process-group teardown is POSIX-only")
    def test_late_pipe_failure_kills_inherited_pipe_descendant(self):
        pid_path = self.tmp / "descendant.pid"
        raw = json.dumps(_classified_payload())
        worker = _write_worker(
            self.tmp,
            f"""
            import pathlib
            import subprocess
            import sys

            sys.stdin.buffer.read()
            child = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(60)"]
            )
            pathlib.Path({str(pid_path)!r}).write_text(str(child.pid), encoding="utf-8")
            sys.stdout.write({raw!r})
            sys.stdout.flush()
            """,
            name="inherited_pipe_descendant.py",
        )
        started = time.monotonic()
        result, diagnostic = self.run_with_worker(worker, timeout=0.25)
        elapsed = time.monotonic() - started
        self.assertLess(elapsed, 4.0)
        self.assertEqual(result["content_classification"]["reason"], "WORKER_IO_ERROR")
        self.assertEqual(diagnostic["reason"], "WORKER_IO_ERROR")

        descendant_pid = int(pid_path.read_text())
        self.assert_process_gone(descendant_pid)

    @unittest.skipUnless(os.name == "posix", "process-group teardown is POSIX-only")
    def test_successful_worker_also_kills_background_descendant(self):
        pid_path = self.tmp / "successful-descendant.pid"
        raw = json.dumps(_classified_payload())
        worker = _write_worker(
            self.tmp,
            f"""
            import pathlib
            import subprocess
            import sys

            sys.stdin.buffer.read()
            child = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(60)"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            pathlib.Path({str(pid_path)!r}).write_text(str(child.pid), encoding="utf-8")
            sys.stdout.write({raw!r})
            sys.stdout.flush()
            """,
            name="successful_background_descendant.py",
        )
        result, diagnostic = self.run_with_worker(worker)
        self.assertEqual(result["content_classification"]["status"], "CLASSIFIED")
        self.assertEqual(diagnostic["reason"], "CLASSIFIED")
        self.assert_process_gone(int(pid_path.read_text()))

    def test_classified_result_requires_complete_exact_input_delivery(self):
        raw = json.dumps(_classified_payload())
        worker = _write_worker(
            self.tmp,
            f"""
            import sys
            sys.stdout.write({raw!r})
            sys.stdout.flush()
            """,
            name="classified_without_reading.py",
        )
        state, diagnostic = preflight._run_content_classifier(
            b"NOT-A-PDF-BYTE" * 1_000_000,
            page_count=1,
            worker_path=worker,
            timeout=1.0,
        )
        self.assertEqual(state["status"], "UNAVAILABLE")
        self.assertEqual(state["reason"], "WORKER_IO_ERROR")
        self.assertEqual(diagnostic["reason"], "WORKER_IO_ERROR")

    def test_nonzero_exit_is_closed_and_raw_stderr_is_not_in_sidecar(self):
        worker = _write_worker(
            self.tmp,
            """
            import sys
            sys.stderr.write("PRIVATE-RAW-ERROR")
            raise SystemExit(7)
            """,
        )
        result, diagnostic = self.run_with_worker(worker)
        self.assertEqual(result["content_classification"]["reason"], "WORKER_NONZERO_EXIT")
        self.assertNotIn("PRIVATE-RAW-ERROR", json.dumps(result))
        self.assertIn("PRIVATE-RAW-ERROR", diagnostic["untrusted_detail"])

    @unittest.skipUnless(os.name == "posix", "negative signal return codes are POSIX")
    def test_signal_exit_is_distinct_closed_reason(self):
        worker = _write_worker(
            self.tmp,
            """
            import os
            import signal
            os.kill(os.getpid(), signal.SIGTERM)
            """,
        )
        result, diagnostic = self.run_with_worker(worker)
        self.assertEqual(result["content_classification"]["reason"], "WORKER_SIGNAL")
        self.assertEqual(diagnostic["reason"], "WORKER_SIGNAL")

    def test_malformed_output_is_closed(self):
        worker = _write_worker(
            self.tmp,
            """
            import sys
            sys.stdin.buffer.read()
            sys.stdout.write("{not-json")
            """,
        )
        result, _ = self.run_with_worker(worker)
        self.assertEqual(result["content_classification"]["reason"], "WORKER_MALFORMED_OUTPUT")

    def test_stdout_and_stderr_caps_stop_flooding_workers(self):
        cases = (
            (
                "stdout",
                "import sys\nsys.stdout.write('x' * 20000)\nsys.stdout.flush()\n",
                "WORKER_STDOUT_LIMIT",
            ),
            (
                "stderr",
                "import sys\nsys.stderr.write('x' * 20000)\nsys.stderr.flush()\n",
                "WORKER_STDERR_LIMIT",
            ),
        )
        for name, source, reason in cases:
            with self.subTest(name=name):
                worker = _write_worker(self.tmp, source, name=f"{name}_flood.py")
                result, diagnostic = self.run_with_worker(worker)
                self.assertEqual(result["content_classification"]["reason"], reason)
                self.assertEqual(diagnostic["reason"], reason)

    def test_limit_plus_one_precedes_timeout_for_flushed_hanging_worker(self):
        cases = (
            (
                "stdout",
                "stdout",
                preflight.CLASSIFIER_STDOUT_LIMIT + 1,
                "WORKER_STDOUT_LIMIT",
            ),
            (
                "stderr",
                "stderr",
                preflight.CLASSIFIER_STDERR_LIMIT + 1,
                "WORKER_STDERR_LIMIT",
            ),
        )
        for name, stream, byte_count, reason in cases:
            with self.subTest(name=name):
                worker = _write_worker(
                    self.tmp,
                    f"""
                    import sys
                    import time
                    sys.{stream}.buffer.write(b'x' * {byte_count})
                    sys.{stream}.buffer.flush()
                    time.sleep(60)
                    """,
                    name=f"{name}_limit_plus_one_then_hang.py",
                )
                result, diagnostic = self.run_with_worker(worker, timeout=0.25)
                self.assertEqual(result["content_classification"]["reason"], reason)
                self.assertEqual(diagnostic["reason"], reason)
                self.assertEqual(
                    diagnostic[f"{stream}_bytes_observed"],
                    byte_count,
                )

    def test_closed_validator_rejects_schema_types_and_page_bound_drift(self):
        cases = []
        extra = _classified_payload()
        extra["extra"] = "escape"
        cases.append(("extra", json.dumps(extra), "WORKER_INVALID_OUTPUT"))
        duplicate = json.dumps(_classified_payload()).replace(
            '"status": "CLASSIFIED"',
            '"status": "CLASSIFIED", "status": "UNAVAILABLE"',
        )
        cases.append(("duplicate-key", duplicate, "WORKER_MALFORMED_OUTPUT"))
        cases.append(
            (
                "nan",
                json.dumps(_classified_payload(confidence=float("nan"))),
                "WORKER_MALFORMED_OUTPUT",
            )
        )
        cases.append(
            (
                "range",
                json.dumps(_classified_payload(confidence=2.0)),
                "WORKER_INVALID_OUTPUT",
            )
        )
        cases.append(
            (
                "page-upper",
                json.dumps(_classified_payload("OCR_RECOMMENDED", pages=[1])),
                "WORKER_INVALID_OUTPUT",
            )
        )
        cases.append(
            (
                "page-bool",
                json.dumps(_classified_payload("OCR_RECOMMENDED", pages=[True])),
                "WORKER_INVALID_OUTPUT",
            )
        )
        cases.append(
            (
                "page-duplicate",
                json.dumps(_classified_payload("OCR_RECOMMENDED", pages=[0, 0])),
                "WORKER_INVALID_OUTPUT",
            )
        )
        unknown = _classified_payload()
        unknown["classification"] = "VENDOR_OPEN_ENUM"
        cases.append(("enum", json.dumps(unknown), "WORKER_INVALID_OUTPUT"))
        classification_list = _classified_payload()
        classification_list["classification"] = []
        cases.append(
            (
                "classification-list",
                json.dumps(classification_list),
                "WORKER_INVALID_OUTPUT",
            )
        )
        classification_object = _classified_payload()
        classification_object["classification"] = {"open": "enum"}
        cases.append(
            (
                "classification-object",
                json.dumps(classification_object),
                "WORKER_INVALID_OUTPUT",
            )
        )
        unavailable_reason_list = {
            "schema": "pdf_content_classifier_worker/1",
            "status": "UNAVAILABLE",
            "reason": [],
            "classification": None,
            "confidence": None,
            "pages_needing_ocr": None,
        }
        cases.append(
            (
                "unavailable-reason-list",
                json.dumps(unavailable_reason_list),
                "WORKER_INVALID_OUTPUT",
            )
        )
        unavailable_reason_object = dict(unavailable_reason_list)
        unavailable_reason_object["reason"] = {"open": "reason"}
        cases.append(
            (
                "unavailable-reason-object",
                json.dumps(unavailable_reason_object),
                "WORKER_INVALID_OUTPUT",
            )
        )
        for name, raw, expected_reason in cases:
            with self.subTest(name=name):
                worker = _write_worker(
                    self.tmp,
                    f"import sys\nsys.stdin.buffer.read()\nsys.stdout.write({raw!r})\n",
                    name=f"invalid_{name}.py",
                )
                result, _ = self.run_with_worker(worker)
                self.assertEqual(
                    result["content_classification"]["reason"],
                    expected_reason,
                )

    def test_local_diagnostic_is_exclusive_private_and_schema_valid(self):
        diagnostic = preflight._diagnostic(
            "WORKER_NONZERO_EXIT",
            detail=b"untrusted local detail",
            stdout_bytes=4,
            stderr_bytes=22,
        )
        path = self.tmp / "operator-only.json"
        preflight._write_local_diagnostic(path, diagnostic)
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        schema = json.loads(
            (PDF_CONTRACTS / "pdf_content_classifier_diagnostic.schema.json").read_text()
        )
        Draft202012Validator(schema).validate(json.loads(path.read_text()))
        with self.assertRaises(FileExistsError):
            preflight._write_local_diagnostic(path, diagnostic)

    def test_local_diagnostic_rejects_unsupported_platform_before_creation(self):
        diagnostic = preflight._diagnostic("WORKER_IO_ERROR")
        path = self.tmp / "must-not-be-created.json"
        with mock.patch.object(preflight.os, "name", "nt"):
            with self.assertRaisesRegex(OSError, "POSIX fchmod"):
                preflight._write_local_diagnostic(path, diagnostic)
        self.assertFalse(path.exists())

    def test_operator_detail_byte_bound_survives_multibyte_cutoff(self):
        raw = b"x" * (preflight.CLASSIFIER_OPERATOR_DETAIL_LIMIT - 1) + "界".encode("utf-8")
        detail = preflight._bounded_operator_detail(raw)
        self.assertLessEqual(
            len(detail.encode("utf-8")),
            preflight.CLASSIFIER_OPERATOR_DETAIL_LIMIT,
        )

    def test_parent_never_imports_optional_native_classifier(self):
        source = (REPO_ROOT / "scripts" / "pdf_read_preflight.py").read_text()
        tree = ast.parse(source)
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertNotIn("pdf_inspector", imported)
        self.assertIn("importlib.import_module(\"pdf_inspector\")", WORKER_PATH.read_text())

    def test_all_pdf_contracts_are_valid_draft_2020_12(self):
        paths = sorted(PDF_CONTRACTS.glob("*.schema.json"))
        self.assertEqual(len(paths), 3)
        for path in paths:
            with self.subTest(path=path.name):
                Draft202012Validator.check_schema(json.loads(path.read_text()))

    def test_sidecar_schema_binds_tool_version_to_extension_shape(self):
        schema = json.loads((PDF_CONTRACTS / "pdf_read_preflight.schema.json").read_text())
        validator = Draft202012Validator(schema)
        pdf = _write(self.tmp, "version-bound.pdf", _flat_pdf(1))

        legacy, _ = preflight._run_preflight(pdf)
        self.assertTrue(validator.is_valid(legacy))
        legacy["tool"] = "pdf_read_preflight/1.1.0"
        self.assertFalse(validator.is_valid(legacy))

        opted, _ = self.run_with_worker(self.json_worker(_classified_payload()))
        self.assertEqual(opted["tool"], "pdf_read_preflight/1.1.0")
        opted["tool"] = "pdf_read_preflight/1.0.0"
        self.assertFalse(validator.is_valid(opted))


class SidecarShapeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_sidecar_fields_and_hash(self):
        data = _flat_pdf(2)
        p = _write(self.tmp, "doc.pdf", data)
        r = preflight.run_preflight(p)
        self.assertEqual(r["schema"], "pdf_read_preflight/1")
        self.assertEqual(r["file"], str(p))
        self.assertEqual(r["sha256"], hashlib.sha256(data).hexdigest())
        datetime.fromisoformat(r["generated_at"])  # parses or raises
        self.assertTrue(r["tool"].startswith("pdf_read_preflight/"))
        json.dumps(r)  # JSON-serializable end to end
        schema = json.loads((PDF_CONTRACTS / "pdf_read_preflight.schema.json").read_text())
        Draft202012Validator(schema).validate(r)


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def _cli(self, *args):
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "pdf_read_preflight.py"), *args],
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_cli_stdout_json_and_exit_zero_on_verdict(self):
        p = _write(self.tmp, "doc.pdf", _flat_pdf(2))
        proc = self._cli(str(p))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["verdict"], "PASS")

    def test_cli_missing_file_is_a_verdict_not_an_error(self):
        proc = self._cli(str(Path(self.tmp) / "nope.pdf"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["verdict"], "UNAVAILABLE")

    def test_cli_output_flag_writes_sidecar(self):
        p = _write(self.tmp, "doc.pdf", _flat_pdf(1))
        out = Path(self.tmp) / "doc.read_integrity.json"
        proc = self._cli(str(p), "--output", str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(out.read_text())["verdict"], "PASS")

    def test_cli_no_args_usage_error(self):
        proc = self._cli()
        self.assertEqual(proc.returncode, 2)

    def test_cli_diagnostics_requires_explicit_classification_opt_in(self):
        p = _write(self.tmp, "doc.pdf", _flat_pdf(1))
        proc = self._cli(str(p), "--classifier-diagnostics", str(Path(self.tmp) / "diag.json"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("requires --classify-content", proc.stderr)


if __name__ == "__main__":
    unittest.main()
