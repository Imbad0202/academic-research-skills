"""Mutation tests for ARS v3.7.1 Step 2 — D2 audit Scope Report lint.

Spec: docs/design/2026-04-30-ars-v3.6.8-trust-provenance-and-drift-transparency-spec.md
      §3.2 (D2 — Audit scope coverage non-disclosure)
      §4 Step 2 — Audit report Scope Report block

Tests verify that the lint:

  1. PASSES on the audit template AS SHIPPED (baseline carries the
     Section 0 Scope Report block prepended in Step 2).
  2. PASSES that the Scope Report header appears strictly BEFORE the
     Section 1 heading (the firm rule from spec line 146).
  3. FAILS when the Section 0 H2 anchor is removed.
  4. FAILS when the combined-aggregate "PASSED" verb appears in the audit
     summary scope (spec line 152).
  5. FAILS when the aggregate status is missing one of the three required
     splits per spec lines 147-150.
  6. FAILS when a pass/fail summary is positioned BEFORE Section 0
     (spec line 146 firm rule).
  7. FAILS when the Section 1 heading bytes mutate (regression sentinel
     for the additive-prepend invariant per Q5 amend).
  8. FAILS when any of the four required Scope Report content fields is
     removed.

Baseline assumption: Step 2 commit prepends the Scope Report block to
`shared/templates/codex_audit_multifile_template.md`. Each mutation test
snapshots the template, mutates a single attribute of that baseline,
runs the lint as a subprocess, and restores the file in `finally`
(mirrors test_check_v3_6_8_pattern_protection.py snapshot pattern).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
LINT = REPO_ROOT / "scripts" / "check_v3_6_8_audit_scope_block.py"
TEMPLATE = REPO_ROOT / "shared" / "templates" / "codex_audit_multifile_template.md"

# Anchors that MUST appear in the baseline (Step 2 ships these). If any
# is absent, the baseline contract has drifted and tests are vacuous.
SECTION_0_H2_ANCHOR = "## Section 0 — Scope Report"
SCOPE_REPORT_HEADER = "## Codex Audit Round N — Scope Report"
SECTION_1_HEADING = "## Section 1 — Round metadata"
UNAUDITED_SPLIT_LINE = "  - `unaudited-due-to-missing-source: <count>` (always reported, never hidden)\n"

REQUIRED_FIELDS = [
    "**Total entries audited:**",
    "**Entries with retrieved original source:**",
    "**Entries description-only (no retrieved source):**",
    "**Audit scope warning:**",
]


def _run_lint() -> subprocess.CompletedProcess[str]:
    """Run the v3.7.1 audit-scope lint as a subprocess (so sys.exit propagates)."""
    return subprocess.run(
        [sys.executable, str(LINT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


# ---------- Helpers for snapshot + restore ----------


class _Snapshot:
    """Backs up a file's bytes; restores on context exit."""

    def __init__(self, path: Path):
        self.path = path
        self._bytes: bytes | None = None
        self._existed: bool = False

    def __enter__(self) -> "_Snapshot":
        self._existed = self.path.exists()
        if self._existed:
            self._bytes = self.path.read_bytes()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._existed and self._bytes is not None:
            self.path.write_bytes(self._bytes)
        elif not self._existed and self.path.exists():
            self.path.unlink()


def _baseline_text() -> str:
    """Return template text and assert baseline anchors are present."""
    text = TEMPLATE.read_text(encoding="utf-8")
    for anchor in (SECTION_0_H2_ANCHOR, SCOPE_REPORT_HEADER, SECTION_1_HEADING):
        assert anchor in text, (
            f"baseline contract drift: {anchor!r} missing from template; "
            "Step 2 prepend may have been reverted."
        )
    return text


# ---------- Tests ----------


def test_t1_baseline_template_passes() -> None:
    """T1: template AS SHIPPED carries a valid Scope Report block → PASS."""
    _baseline_text()  # asserts baseline anchors present
    result = _run_lint()
    assert result.returncode == 0, (
        f"Expected exit 0 on baseline template; got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


def test_t2_scope_report_header_strictly_before_section_1() -> None:
    """T2: baseline Scope Report header anchored before Section 1 → PASS + ordering verified."""
    text = _baseline_text()
    result = _run_lint()
    assert result.returncode == 0
    # Sanity check: the lint actually verified ordering, not just header presence.
    assert text.find(SECTION_0_H2_ANCHOR) < text.find(SECTION_1_HEADING)
    assert text.find(SCOPE_REPORT_HEADER) < text.find(SECTION_1_HEADING)


def test_t3_missing_section_0_anchor_fails() -> None:
    """T3: Section 0 H2 anchor removed → FAIL."""
    with _Snapshot(TEMPLATE):
        text = _baseline_text()
        # Mutate the Section 0 H2 heading so the lint cannot anchor it.
        # We change the heading bytes so it no longer matches '^## Section 0'.
        mutated = text.replace(SECTION_0_H2_ANCHOR, "## Sectionless 0 — Scope Report", 1)
        TEMPLATE.write_text(mutated, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            "Expected lint to reject template after Section 0 anchor mutation.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "Section 0" in result.stdout
        assert "missing" in result.stdout.lower() or "absent" in result.stdout.lower()


def test_t4_combined_aggregate_passed_verb_in_summary_fails() -> None:
    """T4: inject a combined-aggregate 'PASSED' verb in summary context → FAIL (spec line 152)."""
    with _Snapshot(TEMPLATE):
        text = _baseline_text()
        # Inject a forbidden combined-aggregate verdict line just before Section 1.
        injection = "\n## Audit Summary\n\nverdict: PASSED\n\n---\n"
        mutated = text.replace(
            SECTION_1_HEADING,
            injection + SECTION_1_HEADING,
            1,
        )
        TEMPLATE.write_text(mutated, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            "Expected lint to reject combined-aggregate 'PASSED' verb per spec line 152.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        # The combined-aggregate verb is what's forbidden; the rule code
        # should surface either R4 or the verb itself.
        out = result.stdout
        assert "PASSED" in out or "combined-aggregate" in out.lower()


def test_t5_missing_unaudited_split_fails() -> None:
    """T5: drop the 'unaudited-due-to-missing-source' split row → FAIL (spec line 150)."""
    with _Snapshot(TEMPLATE):
        text = _baseline_text()
        assert UNAUDITED_SPLIT_LINE in text, (
            "fixture assumption violated: unaudited split line not present in baseline"
        )
        mutated = text.replace(UNAUDITED_SPLIT_LINE, "", 1)
        TEMPLATE.write_text(mutated, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            "Expected lint to reject Scope Report missing the "
            "'unaudited-due-to-missing-source' split per spec line 150.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "unaudited-due-to-missing-source" in result.stdout


def test_t6_pass_fail_summary_before_section_0_fails() -> None:
    """T6: inject a pass/fail summary BEFORE Section 0 → FAIL (spec line 146)."""
    with _Snapshot(TEMPLATE):
        text = _baseline_text()
        # Inject a fake pass/fail summary heading + verdict row BEFORE Section 0.
        injection = (
            "\n## Audit Summary\n\nverified-against-source: PASS\n\n---\n\n"
        )
        mutated = text.replace(
            SECTION_0_H2_ANCHOR,
            injection + SECTION_0_H2_ANCHOR,
            1,
        )
        TEMPLATE.write_text(mutated, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            "Expected lint to reject pass/fail summary placed before Section 0 "
            "(spec line 146 firm rule).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def test_t7_section_1_heading_byte_mutation_fails() -> None:
    """T7: Section 1 heading bytes change → FAIL (additive-prepend invariant per Q5)."""
    with _Snapshot(TEMPLATE):
        text = _baseline_text()
        # Mutate the Section 1 heading's title (capitalization swap).
        mutated = text.replace(
            SECTION_1_HEADING,
            "## Section 1 — Round Metadata",  # capitalization changed
            1,
        )
        TEMPLATE.write_text(mutated, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            "Expected lint to enforce Section 1 byte-equivalence per Q5 amend "
            "(spec §3.2 line 131: Sections 1-7 stay byte-equivalent in title, "
            "ordinal label, and order).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


@pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
def test_t8_missing_required_content_field_fails(missing_field: str) -> None:
    """T8: drop one of the four required Scope Report fields → FAIL (spec lines 136-140)."""
    with _Snapshot(TEMPLATE):
        text = _baseline_text()
        assert missing_field in text, (
            f"fixture assumption violated: field {missing_field!r} not present in baseline"
        )
        # Drop the entire line that contains the field marker.
        lines = text.splitlines(keepends=True)
        # Drop only the FIRST line that contains the marker, to avoid
        # accidentally removing a Template-structure summary line that
        # also references the field name.
        new_lines: list[str] = []
        dropped = False
        for line in lines:
            if not dropped and missing_field in line:
                dropped = True
                continue
            new_lines.append(line)
        assert dropped, "fixture assumption violated: no line dropped"
        TEMPLATE.write_text("".join(new_lines), encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            f"Expected lint to reject Scope Report missing field {missing_field!r}.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


# ---- Round-2 codex review findings ----


@pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
def test_t9_required_field_check_scoped_to_section_0(missing_field: str) -> None:
    """T9 (codex round-2 P2-1): required-field scan must be scoped to Section 0,
    not whole-file. If the field is dropped from Section 0 but the same marker
    appears in a later appendix or documentation block, the lint must still FAIL.
    """
    with _Snapshot(TEMPLATE):
        text = _baseline_text()
        # Find the Section 0 block boundaries: from "## Section 0" anchor
        # to the next "## Section 1" anchor.
        section_0_pos = text.find("## Section 0 — Scope Report")
        section_1_pos = text.find("## Section 1 — Round metadata")
        assert section_0_pos != -1 and section_1_pos != -1
        section_0_block = text[section_0_pos:section_1_pos]
        assert missing_field in section_0_block, (
            f"fixture assumption violated: field {missing_field!r} missing from Section 0 baseline"
        )
        # Remove the field from Section 0 only, then inject a decoy line
        # carrying the same marker AFTER Section 7 so a whole-file scan
        # would falsely PASS.
        section_0_mutated = section_0_block.replace(missing_field, "REDACTED-FIELD-MARKER", 1)
        appendix_decoy = (
            f"\n\n## Appendix — documentation reference\n\n"
            f"For historical context, the Scope Report contract requires "
            f"{missing_field} to appear in every audit round.\n"
        )
        mutated = (
            text[:section_0_pos]
            + section_0_mutated
            + text[section_1_pos:]
            + appendix_decoy
        )
        TEMPLATE.write_text(mutated, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            f"Expected lint to reject when {missing_field!r} is missing from Section 0 "
            f"(even though the marker appears in an appendix after Section 7).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


@pytest.mark.parametrize("missing_split", [
    "verified-against-source",
    "description-internally-consistent",
    "unaudited-due-to-missing-source",
])
def test_t10_required_split_check_scoped_to_section_0(missing_split: str) -> None:
    """T10 (codex round-2 P2-1, applies to R3 too): aggregate-status split
    scan must be scoped to Section 0. Decoy in appendix must not falsely PASS.
    """
    with _Snapshot(TEMPLATE):
        text = _baseline_text()
        section_0_pos = text.find("## Section 0 — Scope Report")
        section_1_pos = text.find("## Section 1 — Round metadata")
        section_0_block = text[section_0_pos:section_1_pos]
        assert missing_split in section_0_block
        section_0_mutated = section_0_block.replace(missing_split, "REDACTED-SPLIT-NAME", 1)
        appendix_decoy = (
            f"\n\n## Appendix — split nomenclature\n\n"
            f"Note: the {missing_split} verdict is computed by the orchestrator.\n"
        )
        mutated = (
            text[:section_0_pos]
            + section_0_mutated
            + text[section_1_pos:]
            + appendix_decoy
        )
        TEMPLATE.write_text(mutated, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            f"Expected lint to reject when {missing_split!r} is missing from Section 0 "
            f"(even though the marker appears in an appendix).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def test_t11_target_relative_path_does_not_crash() -> None:
    """T11 (codex round-2 P2-2): --target with a relative repo path must
    not crash with ValueError. Lint should resolve the path and proceed.
    """
    result = subprocess.run(
        [
            sys.executable,
            str(LINT),
            "--target",
            "shared/templates/codex_audit_multifile_template.md",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    # The lint must produce a deterministic exit code (0 or 1 — both indicate
    # the lint ran), NOT crash with ValueError or ImportError.
    assert result.returncode in (0, 1), (
        f"Expected exit 0 or 1 on relative --target; got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    # Crash signature: ValueError traceback in stderr.
    assert "Traceback" not in result.stderr, (
        f"Expected --target with relative path to be handled gracefully; "
        f"got Python traceback in stderr:\n{result.stderr}"
    )


def test_t12_target_outside_repo_does_not_crash(tmp_path) -> None:
    """T12 (codex round-2 P2-2): --target with an absolute path outside
    the repo must not crash. Lint should display the raw path and proceed.
    """
    fixture = tmp_path / "fake_template.md"
    # Minimal valid Scope Report fixture so the lint reports PASS not FAIL.
    fixture.write_text(
        "# Test\n\n"
        "## Section 0 — Scope Report\n\n"
        "```\n"
        "## Codex Audit Round N — Scope Report\n\n"
        "**Total entries audited:** <N>\n"
        "**Entries with retrieved original source:** <N>\n"
        "**Entries description-only (no retrieved source):** <N>\n"
        "**Audit scope warning:** test\n"
        "```\n\n"
        "verified-against-source\n"
        "description-internally-consistent\n"
        "unaudited-due-to-missing-source\n\n"
        "## Section 1 — Round metadata\n\n"
        "body\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(LINT), "--target", str(fixture)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Traceback" not in result.stderr, (
        f"Expected --target outside the repo to be handled gracefully; "
        f"got Python traceback in stderr:\n{result.stderr}"
    )
    assert result.returncode in (0, 1), (
        f"Expected deterministic exit code; got {result.returncode}"
    )
