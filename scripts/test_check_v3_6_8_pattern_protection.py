"""Mutation tests for ARS v3.7.1 byte-equivalence SHA gate.

Spec: docs/design/2026-04-30-ars-v3.6.8-trust-provenance-and-drift-transparency-spec.md
      § Step 0 — Lint manifest separation (round-1 codex F-004 amend)

Tests verify that:
  1. Happy path: untouched v3.6.7 PATTERN PROTECTION blocks pass.
  2. Mutation: any byte change inside a v3.6.7-tagged block fails.
  3. Additive boundary: edits OUTSIDE v3.6.7-tagged blocks (e.g. appending
     a new "Two-Layer Citation Emission" section after the block) do NOT
     trigger SHA mismatch.
  4. v3.6.8 manifest shape validation (scope tag, files list).
  5. PR-1 expected state (v3.6.8 manifest with empty 'files' list) is OK.
  6. Boundary errors (v3.6.7 marker missing at HEAD; manifest absent).

The lint runs git operations against the actual repo, so each mutation
test backs up the file under test, mutates, runs the lint as a subprocess,
and restores the file in `finally` to keep the working tree clean.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
LINT = REPO_ROOT / "scripts" / "check_v3_6_8_pattern_protection.py"
V3_6_7_MANIFEST = REPO_ROOT / "scripts" / "v3_6_7_inversion_manifest.json"
V3_6_8_MANIFEST = REPO_ROOT / "scripts" / "v3_6_8_inversion_manifest.json"

# v3.6.7-protected agent files. We pick synthesis_agent.md as the canonical
# mutation target throughout; the lint hashes all three so mutating any one
# proves the gate works against the full manifest.
TARGET_AGENT = REPO_ROOT / "deep-research" / "agents" / "synthesis_agent.md"
PROTECTION_MARKER = "## PATTERN PROTECTION (v3.6.7)"


def _run_lint() -> subprocess.CompletedProcess[str]:
    """Run the v3.6.8 lint as a subprocess (so its sys.exit propagates)."""
    return subprocess.run(
        [sys.executable, str(LINT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


# ---------- Helpers for mutation + restore (file-level snapshot) ----------


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


# ---------- Tests ----------


def test_happy_path_passes_on_clean_tree() -> None:
    """Untouched v3.6.7 blocks → SHA gate passes."""
    result = _run_lint()
    assert result.returncode == 0, (
        f"Expected exit 0 on clean tree, got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASSED" in result.stdout
    # All three v3.6.7-protected files reported.
    assert "synthesis_agent.md" in result.stdout
    assert "research_architect_agent.md" in result.stdout
    assert "report_compiler_agent.md" in result.stdout


def test_mutation_inside_v3_6_7_block_fails() -> None:
    """Inject 1 byte inside the v3.6.7 PATTERN PROTECTION block → exit 1 + FAIL diagnostic."""
    with _Snapshot(TARGET_AGENT):
        text = TARGET_AGENT.read_text(encoding="utf-8")
        pos = text.find(PROTECTION_MARKER)
        assert pos != -1, "marker missing in test fixture (test would be vacuous)"
        # Inject a stray space at end of the marker line (still inside block).
        nl = text.index("\n", pos)
        mutated = text[:nl] + " " + text[nl:]
        TARGET_AGENT.write_text(mutated, encoding="utf-8")

        result = _run_lint()
        assert result.returncode == 1
        assert "BYTE-EQUIVALENCE FAIL" in result.stdout
        assert "synthesis_agent.md" in result.stdout
        assert "v3.7.1 boundary rule violated" in result.stdout


def test_appending_new_h2_directly_after_eof_newline_passes() -> None:
    """Append a new H2 directly after the file's trailing newline → SHA gate passes.

    Boundary rule (spec §388): v3.7.1 MAY add new prompt sections OUTSIDE
    the v3.6.7 PATTERN PROTECTION block. When the v3.6.7 block runs to EOF
    (the case for all three current manifest files), the appended H2 must
    be placed IMMEDIATELY after the file's trailing newline — no extra
    blank line — so the heading-based extractor's range stays byte-equal
    to the base commit's range. (The extractor terminates at the next
    H1/H2/H3 line; the bytes inside the range are file[marker_pos:next_h_line].
    Inserting a blank line between EOF and the new H2 would extend the
    extracted range by those blank-line bytes and trigger SHA mismatch.)

    This test pins the contract for Step 3a's "Two-Layer Citation Emission"
    section addition: append directly, no blank-line separator.
    """
    with _Snapshot(TARGET_AGENT):
        text = TARGET_AGENT.read_text(encoding="utf-8")
        # File already ends with a trailing newline; append H2 immediately.
        # NO leading "\n\n" — that would expand the v3.6.7 block range.
        assert text.endswith("\n"), "fixture assumption (file ends with newline) violated"
        appended = text + "## Two-Layer Citation Emission (v3.7.1 placeholder)\n\nbody\n"
        TARGET_AGENT.write_text(appended, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 0, (
            f"Appending H2 directly after EOF newline must keep byte-"
            f"equivalence; lint should PASS.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def test_appending_new_h2_with_blank_line_separator_fails() -> None:
    """Adding a blank-line separator before the new H2 → SHA mismatch.

    This is the dual of the test above: it pins the failure mode that
    Step 3a's section-addition contract must avoid. If a contributor
    accidentally adds `\\n\\n## New Section` (the natural Markdown idiom)
    after the v3.6.7 block, the byte-equivalence gate catches it. Step 3a's
    documentation will instruct contributors to elide the blank line for
    EOF-terminating PATTERN PROTECTION blocks.
    """
    with _Snapshot(TARGET_AGENT):
        text = TARGET_AGENT.read_text(encoding="utf-8")
        # The natural Markdown idiom — blank line then H2 — must FAIL when
        # the v3.6.7 block runs to EOF, because the blank line bytes get
        # absorbed into the extractor's range.
        appended = text + "\n## Two-Layer Citation Emission (v3.7.1 placeholder)\n\nbody\n"
        TARGET_AGENT.write_text(appended, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            "Adding a blank-line separator before the new H2 must trigger "
            "SHA mismatch (the blank line bytes fall inside the EOF-terminating "
            "extractor range). If this test fails, the contract for Step 3a "
            "section additions has weakened and v3.7.1 boundary rule is at risk."
        )
        assert "BYTE-EQUIVALENCE FAIL" in result.stdout


def test_v3_6_8_manifest_scope_must_be_correct() -> None:
    """Wrong scope tag → lint refuses to run (clear error)."""
    with _Snapshot(V3_6_8_MANIFEST):
        data = json.loads(V3_6_8_MANIFEST.read_text(encoding="utf-8"))
        data["scope"] = "v3.6.7-only"  # wrong — this is v3.6.8 manifest
        V3_6_8_MANIFEST.write_text(json.dumps(data), encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1
        assert "v3.6.8-only" in result.stdout
        assert "scope" in result.stdout


def test_v3_6_8_manifest_files_must_be_list() -> None:
    """'files' as non-list → reject."""
    with _Snapshot(V3_6_8_MANIFEST):
        V3_6_8_MANIFEST.write_text(
            json.dumps({"scope": "v3.6.8-only", "files": "not-a-list"}),
            encoding="utf-8",
        )
        result = _run_lint()
        assert result.returncode == 1
        assert "list of strings" in result.stdout


def test_pr1_initial_state_empty_files_list_is_ok() -> None:
    """PR-1 ships v3.6.8 manifest with files: [] until Step 3a populates."""
    with _Snapshot(V3_6_8_MANIFEST):
        V3_6_8_MANIFEST.write_text(
            json.dumps({"scope": "v3.6.8-only", "files": []}),
            encoding="utf-8",
        )
        result = _run_lint()
        assert result.returncode == 0, (
            f"Empty v3.6.8 'files' list is the expected PR-1 state and must "
            f"NOT block the lint.\nstdout:\n{result.stdout}"
        )


def test_v3_6_7_manifest_deletion_hard_fails() -> None:
    """v3.6.7 manifest is the source of truth. Missing it → hard error.

    After the round-2 anti-self-baseline guard, deletion is caught earlier:
    the guard's HEAD-vs-base comparison sees the file missing at HEAD but
    present at the PR base and rejects with a deletion-specific message.
    The guard message is more precise than the legacy "manifest missing"
    bare error, so this test just asserts a hard failure with a v3.7.1 lint
    error that mentions the manifest.
    """
    with _Snapshot(V3_6_7_MANIFEST):
        V3_6_7_MANIFEST.unlink()
        result = _run_lint()
        assert result.returncode == 1
        # Either the guard catches it ("missing at PR HEAD") or the inner
        # loader catches it ("v3.6.7 manifest missing"); both are correct.
        assert (
            "v3.6.7 manifest" in result.stdout
            and ("missing" in result.stdout or "guard" in result.stdout)
        ), f"Expected manifest-missing error; got: {result.stdout}"


def test_v3_6_8_manifest_deletion_hard_fails() -> None:
    """Missing v3.6.8 manifest → hard error (lint configuration broken)."""
    with _Snapshot(V3_6_8_MANIFEST):
        V3_6_8_MANIFEST.unlink()
        result = _run_lint()
        assert result.returncode == 1
        assert "v3.6.8 manifest missing" in result.stdout


def test_heading_prefix_mutation_is_caught() -> None:
    """Round-3 codex P2 closure: spec § 388 says the canonical byte range
    starts at the LINE containing `## PATTERN PROTECTION (v3.6.7)`, so the
    `## ` heading prefix is part of the hashed bytes.

    The v3.6.7 lint's underlying `_extract_block` does case-insensitive
    substring search for the marker text and returns a slice starting at
    `PATTERN...` — silently dropping the heading prefix. That's fine for
    v3.6.7's invariant greps, but it would let the v3.7.1 SHA gate accept
    a `## → ### ` mutation as byte-equivalent.

    This test mutates `## PATTERN PROTECTION (v3.6.7)` to
    `### PATTERN PROTECTION (v3.6.7)` and asserts the gate FAILS. The
    v3.6.8 lint extends the extractor's start position backward to the
    start of the marker's line specifically to close this gap.
    """
    with _Snapshot(TARGET_AGENT):
        text = TARGET_AGENT.read_text(encoding="utf-8")
        mutated = text.replace(
            "## PATTERN PROTECTION (v3.6.7)",
            "### PATTERN PROTECTION (v3.6.7)",
            1,
        )
        assert mutated != text, "heading-mutation fixture failed to apply"
        TARGET_AGENT.write_text(mutated, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1, (
            "Heading-prefix mutation must be caught by the SHA gate "
            "(round-3 codex P2 closure)."
        )
        assert "BYTE-EQUIVALENCE FAIL" in result.stdout


def test_extractor_includes_heading_prefix_bytes() -> None:
    """Verify the v3.6.8 extractor wraps the v3.6.7 extractor with line-start
    backtracking so heading prefix bytes are in the hashed range.
    """
    from scripts.check_v3_6_8_pattern_protection import _extract_block_bytes
    h2_text = "prelude\n\n## PATTERN PROTECTION (v3.6.7)\n\nbody1\n"
    h3_text = "prelude\n\n### PATTERN PROTECTION (v3.6.7)\n\nbody1\n"
    h2_bytes = _extract_block_bytes(h2_text)
    h3_bytes = _extract_block_bytes(h3_text)
    assert h2_bytes is not None and h3_bytes is not None
    # The extractor must distinguish H2 vs H3 in its returned bytes.
    assert h2_bytes != h3_bytes, (
        "heading prefix must be inside the byte range; H2 vs H3 "
        "should produce different SHAs"
    )
    # And the prefix bytes must literally be present.
    assert h2_bytes.startswith(b"## PATTERN")
    assert h3_bytes.startswith(b"### PATTERN")


def test_anti_self_baseline_guard_rejects_manifest_mutation_in_pr(monkeypatch) -> None:
    """Round-2 codex P2 closure: refuse to run on PRs that mutate the v3.6.7
    manifest, because `git log -1 -- manifest` would otherwise resolve to the
    PR's own commit and the SHA comparison would hash modified content against
    itself.

    The guard's BYTE-comparison backstop catches a worktree-level mutation
    (no commit needed). The round-4 history-scan layer catches the more
    subtle touch-and-revert pattern; that layer is exercised by the
    `test_anti_self_baseline_guard_history_scan_called` test below.

    GITHUB_BASE_REF is set explicitly so the guard exits the "advisory mode"
    branch (no PR base detectable → guard returns advisory pass). On
    GitHub `push` event runs, GITHUB_BASE_REF is unset and origin/HEAD
    resolution may fail; this test injects the env var so the guard's
    real reject path is exercised regardless of trigger event.
    """
    monkeypatch.setenv("GITHUB_BASE_REF", "main")
    with _Snapshot(V3_6_7_MANIFEST):
        text = V3_6_7_MANIFEST.read_text(encoding="utf-8")
        # Mutate `rationale_doc` so the byte-equivalence check fires while
        # leaving the schema valid (so the broken-schema branch isn't what
        # triggers the failure).
        mutated = text.replace(
            '"rationale_doc"',
            '"rationale_doc_mutated_for_test"',
            1,
        )
        assert mutated != text, "mutation fixture failed to apply"
        V3_6_7_MANIFEST.write_text(mutated, encoding="utf-8")

        result = _run_lint()
        assert result.returncode == 1, (
            "Guard MUST refuse to run when v3.6.7 manifest is modified in the "
            "PR (otherwise the SHA gate would self-baseline)."
        )
        assert "anti-self-baseline guard" in result.stdout
        # Worktree-mutation triggers the byte-mismatch backstop branch.
        assert (
            "manifest bytes differ" in result.stdout
            or "manifest touched by" in result.stdout
        ), f"Expected guard rejection; got: {result.stdout}"


def test_anti_self_baseline_guard_history_scan_called(monkeypatch) -> None:
    """Round-4 codex P2 closure: the guard MUST scan merge-base..HEAD for any
    commit touching the manifest, not just compare final bytes.

    The touch-and-revert attack: commit A modifies manifest + protected block,
    commit B reverts manifest only. Final bytes match base, but `git log -1`
    still resolves to commit B and `git show B:<protected>` returns modified
    content.

    Reproducing the attack in a unit test would require building a fake git
    history; instead, this test patches `_run_git` to inject a synthetic
    `git log merge-base..HEAD -- manifest` result and asserts the guard
    rejects when commits ARE listed (touch-and-revert simulation).

    GITHUB_BASE_REF is set so the guard's "no PR base detectable → advisory
    pass" branch is bypassed (matters on `push` event CI where the env var
    is normally absent).
    """
    monkeypatch.setenv("GITHUB_BASE_REF", "main")
    from scripts import check_v3_6_8_pattern_protection as mod

    real_run_git = mod._run_git
    fake_log_output = "abcdef1234567890" * 1  # one fake touching commit SHA

    def patched_run_git(args, cwd=None):
        # Intercept the merge-base..HEAD log query with the manifest path.
        if (
            len(args) >= 2
            and args[0] == "log"
            and any("v3_6_7_inversion_manifest.json" in a for a in args)
            and args[1] == "--format=%H"
        ):
            return 0, fake_log_output, ""
        return real_run_git(args, cwd=cwd) if cwd is not None else real_run_git(args)

    monkeypatch.setattr(mod, "_run_git", patched_run_git)
    # Call the guard directly (not via subprocess — monkeypatch wouldn't apply).
    ok, err = mod._v3_6_7_manifest_unchanged_in_pr()
    assert ok is False, "Guard must reject when history scan finds touching commits"
    assert err and "manifest touched by" in err
    assert "round-2 + round-4 codex P2 closure" in err


def test_v3_6_7_marker_removed_at_head_fails() -> None:
    """Removing the v3.6.7 marker line is a boundary violation; must hard-fail.

    This catches an attempt to evade the SHA gate by renaming the heading
    (which would make _extract_block return None at HEAD).
    """
    with _Snapshot(TARGET_AGENT):
        text = TARGET_AGENT.read_text(encoding="utf-8")
        # Replace marker text so the case-insensitive find returns -1.
        mutated = text.replace(PROTECTION_MARKER, "## (former pattern protection heading)")
        assert mutated != text, "test fixture failed to apply mutation"
        TARGET_AGENT.write_text(mutated, encoding="utf-8")
        result = _run_lint()
        assert result.returncode == 1
        assert "marker missing at PR HEAD" in result.stdout


# ---------- Module-level smoke test for the SHA-normalization helpers ----------


def test_normalize_strips_bom_only_when_present() -> None:
    from scripts.check_v3_6_8_pattern_protection import _normalize_bytes
    assert _normalize_bytes(b"\xef\xbb\xbfhello") == b"hello"
    assert _normalize_bytes(b"hello") == b"hello"
    # Multi-byte payloads with no BOM are passed through unchanged.
    assert _normalize_bytes(b"\xe4\xb8\xad\xe6\x96\x87") == b"\xe4\xb8\xad\xe6\x96\x87"


def test_sha256_helper_matches_hashlib() -> None:
    import hashlib
    from scripts.check_v3_6_8_pattern_protection import _sha256
    assert _sha256(b"abc") == hashlib.sha256(b"abc").hexdigest()
