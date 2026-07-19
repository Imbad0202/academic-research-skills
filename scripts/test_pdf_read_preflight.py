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
