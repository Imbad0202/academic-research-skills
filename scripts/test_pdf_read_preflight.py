"""Tests for scripts/pdf_read_preflight.py (#512 PDF read-integrity preflight).

Fixtures are synthetic PDFs assembled in-test with correct xref offsets (no binary
fixture files): a flat valid document, a nested page tree, a root /Count that lies,
a truncated tail, an encrypted trailer, a page-tree cycle, and non-PDF bytes. The
preflight must answer PASS only when the declared root /Count, its own /Kids-walk
enumeration, and pypdf's flattened page list all agree with no parser warnings —
anything less confident lands in FAIL (counts disagree) or UNAVAILABLE (cannot
vouch). Design: docs/design/2026-07-20-512-pdf-read-preflight-spec.md.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pdf_read_preflight as preflight  # noqa: E402


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


def _flat_text_pdf(page_count=2):
    """Like `_flat_pdf` but each page carries a real `Tj` text-showing content stream,
    so a real (non-stubbed) `pdf_inspector` classifies it `text_based` with no pages
    needing OCR — i.e. genuinely zero warnings on BOTH the structural and content
    dimensions. `_flat_pdf` itself stays content-free deliberately: it is reused
    verbatim by ~30 structural-only tests below (xref/trailer/coverage edge cases)
    that must not be perturbed by an unrelated content-classification signal."""
    font_idx = 3 + page_count * 2
    kids = []
    parts = []
    for i in range(page_count):
        page_num = 3 + i * 2
        content_num = page_num + 1
        kids.append(b"%d 0 R" % page_num)
        stream = b"BT /F1 24 Tf 72 720 Td (Hello World Test Document Page %d) Tj ET" % (
            i + 1
        )
        parts.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 %d 0 R >> >> /Contents %d 0 R >>"
            % (font_idx, content_num)
        )
        parts.append(b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
    objects = (
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [%s] /Count %d >>" % (b" ".join(kids), page_count),
        ]
        + parts
        + [b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    )
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


class PreflightVerdictTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def run_on(self, data, name="doc.pdf"):
        return preflight.run_preflight(_write(self.tmp, name, data))

    def test_flat_valid_pdf_passes_with_agreeing_counts(self):
        # Real text content (not `_flat_pdf`'s bare content-free pages) so that a real
        # `pdf_inspector`, if installed, also classifies this text_based with zero
        # pages needing OCR — the "fully clean, zero warnings on every axis" case.
        r = self.run_on(_flat_text_pdf(2))
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


class _FakeClassification:
    def __init__(self, pdf_type, confidence, pages_needing_ocr):
        self.pdf_type = pdf_type
        self.confidence = confidence
        self.pages_needing_ocr = pages_needing_ocr


class _FakePdfInspector:
    """Stub matching the real pdf_inspector module surface used by the preflight
    (`classify_pdf_bytes(data) -> object with .pdf_type/.confidence/.pages_needing_ocr`,
    verified against the installed package: pdf_type in {"text_based", "scanned", ...},
    confidence a float, pages_needing_ocr a list of 0-indexed page numbers)."""

    def __init__(self, result=None, raises=None):
        self._result = result
        self._raises = raises

    def classify_pdf_bytes(self, data):
        if self._raises is not None:
            raise self._raises
        return self._result


class ContentClassificationTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        self._real_pdf_inspector = preflight.pdf_inspector
        self.addCleanup(setattr, preflight, "pdf_inspector", self._real_pdf_inspector)

    def run_on(self, data, name="doc.pdf"):
        return preflight.run_preflight(_write(self.tmp, name, data))

    def test_unavailable_when_pdf_inspector_missing_is_silent(self):
        # Plain absence of the optional advisory extra is the common case and must
        # NOT add a warning — only an installed-but-erroring pdf_inspector, or an
        # actionable finding (scanned/OCR-needed), is worth surfacing.
        preflight.pdf_inspector = None
        r = self.run_on(_flat_pdf(2))
        self.assertEqual(r["verdict"], "PASS", r)  # advisory absence never blocks PASS
        self.assertEqual(
            r["content_classification"],
            {
                "available": False,
                "pdf_type": None,
                "confidence": None,
                "pages_needing_ocr": None,
            },
        )
        self.assertEqual(r["warnings"], [])

    def test_text_based_with_no_ocr_pages_adds_no_advisory_warning(self):
        preflight.pdf_inspector = _FakePdfInspector(
            _FakeClassification("text_based", 0.97, [])
        )
        r = self.run_on(_flat_pdf(2))
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(r["content_classification"]["available"], True)
        self.assertEqual(r["content_classification"]["pdf_type"], "text_based")
        self.assertEqual(r["content_classification"]["pages_needing_ocr"], [])
        self.assertFalse(
            any("content-classification:" in w for w in r["warnings"]), r["warnings"]
        )

    def test_scanned_pdf_adds_advisory_warning_but_verdict_still_pass(self):
        preflight.pdf_inspector = _FakePdfInspector(
            _FakeClassification("scanned", 0.95, [0])
        )
        r = self.run_on(_flat_pdf(1))
        # The structural three-count check still agrees, so the verdict must stay
        # PASS — content classification informs the caller without gating anything.
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(r["content_classification"]["pdf_type"], "scanned")
        self.assertEqual(r["content_classification"]["pages_needing_ocr"], [0])
        self.assertTrue(
            any("content-classification: pdf_type=scanned" in w for w in r["warnings"]),
            r["warnings"],
        )

    def test_classification_error_is_advisory_not_fatal(self):
        preflight.pdf_inspector = _FakePdfInspector(raises=RuntimeError("native panic"))
        r = self.run_on(_flat_pdf(1))
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(r["content_classification"]["available"], False)
        self.assertTrue(
            any("content-classification-error: native panic" in w for w in r["warnings"]),
            r["warnings"],
        )

    def test_malformed_classification_result_is_advisory_not_fatal(self):
        # Independent review finding: a call that SUCCEEDS but returns an object
        # missing/renaming an expected attribute (a future pdf_inspector build, or
        # any object without .pages_needing_ocr) must degrade like a raised
        # exception, not crash run_preflight() with an uncaught AttributeError.
        class _NoAttrs:
            pass

        preflight.pdf_inspector = _FakePdfInspector(_NoAttrs())
        r = self.run_on(_flat_pdf(1))
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(r["content_classification"]["available"], False)
        self.assertTrue(
            any(w.startswith("content-classification-error:") for w in r["warnings"]),
            r["warnings"],
        )

    def test_classification_runs_even_when_structural_verdict_is_unavailable(self):
        # An encrypted file forecloses the structural checks entirely, but content
        # classification is an independent signal and should still be attempted.
        preflight.pdf_inspector = _FakePdfInspector(
            _FakeClassification("text_based", 0.8, [])
        )
        r = self.run_on(_encrypted_pdf())
        self.assertEqual(r["verdict"], "UNAVAILABLE", r)
        self.assertEqual(r["content_classification"]["available"], True)


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


if __name__ == "__main__":
    unittest.main()
