#!/usr/bin/env python3
"""ARS v3.7.1 byte-equivalence SHA gate for v3.6.7-tagged PATTERN PROTECTION blocks.

Spec: docs/design/2026-04-30-ars-v3.6.8-trust-provenance-and-drift-transparency-spec.md
      § Step 0 — Lint manifest separation (round-1 codex F-004 amend)

Boundary rule (per spec):
- v3.7.1 work does NOT modify the v3.6.7-tagged PATTERN PROTECTION blocks in
  synthesis_agent.md / research_architect_agent.md / report_compiler_agent.md.
- v3.7.1 MAY add new prompt sections (e.g. "Two-Layer Citation Emission")
  OUTSIDE those v3.6.7-tagged blocks; those v3.6.8-tagged invariants ride
  this script's own manifest (scripts/v3_6_8_inversion_manifest.json), which
  starts empty in PR-1 and is populated by Step 3a.

Single source of truth (round-4 R4-002 + round-5 R5-001 + round-6 R6-002):
- The v3.6.7 frozen manifest at scripts/v3_6_7_inversion_manifest.json is the
  single source of truth for the protected file LIST.
- The v3.6.7 protected CONTENT is whatever the v3.6.7-tagged block shows at
  the v3.6.7 manifest's most recent modifying commit (derived via
  `git log -1 --format=%H scripts/v3_6_7_inversion_manifest.json`).
- v3.7.1 lint computes SHA on demand at runtime: hash(block at PR HEAD) ==
  hash(block at v3.6.7 base commit). No stored expected SHAs; no dual truth.

Shallow-clone safety (round-6 R6-002 + round-7 R7-001):
- `actions/checkout@v4` defaults to fetch-depth: 1 in CI; that would render
  `git log -1` vacuous. This lint detects shallow clones and either fetches
  --unshallow against the default branch or hard-fails with a fix-it message.

Exit codes: 0 on pass, 1 on any failure (including shallow-clone refusal).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Reuse v3.6.7 lint's heading-based block extractor for byte-equivalence.
# The extractor must be byte-equivalent between the two lints; the spec
# explicitly requires the SHARED function (see spec § Step 0 line ~389:
# "The extractor is the byte-equivalent function shared between v3.6.7 lint
# and v3.7.1 lint to guarantee identical results").
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_v3_6_7_pattern_protection import (  # noqa: E402
    PROTECTION_BLOCK as V3_6_7_PROTECTION_BLOCK,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
V3_6_7_MANIFEST = REPO_ROOT / "scripts" / "v3_6_7_inversion_manifest.json"
V3_6_8_MANIFEST = REPO_ROOT / "scripts" / "v3_6_8_inversion_manifest.json"

# Byte-order mark stripped per spec § Step 0: "the file's BOM (if any) is
# excluded; trailing whitespace of the last block line is preserved".
_BOM = b"\xef\xbb\xbf"


def _run_git(args: list[str], cwd: Path = REPO_ROOT) -> tuple[int, str, str]:
    """Run git and return (returncode, stdout, stderr) as decoded strings."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _resolve_default_branch() -> tuple[str | None, str | None]:
    """Resolve the repo's default branch via the spec's three-step ladder.

    (1) `git symbolic-ref --quiet --short refs/remotes/origin/HEAD` → strip 'origin/'
    (2) `$GITHUB_DEFAULT_BRANCH` env (GitHub Actions fallback)
    (3) None — caller must hard-fail.
    """
    rc, out, _ = _run_git(["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"])
    if rc == 0 and out.startswith("origin/"):
        return out[len("origin/"):], None
    env_default = os.environ.get("GITHUB_DEFAULT_BRANCH")
    if env_default:
        return env_default, None
    return None, (
        "[ARS-V3.7.1 LINT ERROR: default branch unresolvable; clone must "
        "include origin/HEAD or set GITHUB_DEFAULT_BRANCH env]"
    )


def _ensure_full_clone() -> str | None:
    """Return None on success, error string on hard-fail.

    If the repo is a shallow clone, attempt `git fetch --unshallow origin
    <default-branch>` first; if that itself fails, hard-fail.
    """
    rc, out, _ = _run_git(["rev-parse", "--is-shallow-repository"])
    if rc != 0:
        return f"[ARS-V3.7.1 LINT ERROR: cannot determine clone depth: {out!r}]"
    if out.strip().lower() != "true":
        return None  # full clone — proceed
    default_branch, err = _resolve_default_branch()
    if err is not None:
        return err
    rc, out, stderr = _run_git(["fetch", "--unshallow", "origin", default_branch])
    if rc != 0:
        return (
            "[ARS-V3.7.1 LINT ERROR: shallow clone detected; set fetch-depth: "
            f"0 in checkout step before running v3.7.1 byte-equivalence "
            f"check (unshallow attempt failed: {stderr!r})]"
        )
    return None


def _v3_6_7_base_commit() -> tuple[str | None, str | None]:
    """Derive the v3.6.7 base commit via `git log -1` against the v3.6.7 manifest.

    This is the single source of truth derivation per spec § Step 0
    (round-4 R4-002 + round-5 R5-001 + round-6 R6-002 amend; no stored
    base_commit field, no dual truth).
    """
    rc, out, stderr = _run_git([
        "log", "-1", "--format=%H", "--",
        "scripts/v3_6_7_inversion_manifest.json",
    ])
    if rc != 0 or not out:
        return None, (
            "[ARS-V3.7.1 LINT ERROR: cannot derive v3.6.7 base commit "
            f"from `git log -1 -- scripts/v3_6_7_inversion_manifest.json`: "
            f"rc={rc} stderr={stderr!r}]"
        )
    return out.strip(), None


def _detect_pr_base_ref() -> str | None:
    """Return a ref that names the PR's base for anti-self-baseline guard.

    Order: $GITHUB_BASE_REF (CI fast path) → origin/<default-branch> (resolved
    via the same ladder as the shallow-clone safety check). Returns None when
    no remote / default branch is reachable (e.g. detached local check on a
    fork without origin); callers treat that as "skip the guard, fall back to
    derivation alone" — local-only attacks are out of scope (the user can see
    their own diff).
    """
    env_base = os.environ.get("GITHUB_BASE_REF")
    if env_base:
        return f"origin/{env_base}"
    default_branch, _ = _resolve_default_branch()
    if default_branch:
        return f"origin/{default_branch}"
    return None


def _v3_6_7_manifest_unchanged_in_pr() -> tuple[bool, str | None]:
    """Anti-self-baseline guard (round-2 + round-4 codex P2 closure).

    Without this, a PR could mutate `scripts/v3_6_7_inversion_manifest.json`
    AND a v3.6.7-tagged PATTERN PROTECTION block, causing the SHA gate to
    hash modified content against itself.

    Round-2 guard (initial): compare manifest bytes at HEAD vs at
    `merge-base <pr-base> HEAD`; refuse to run on byte-difference.

    Round-4 closure: byte-equality at HEAD is NOT sufficient. A PR with
    commit A (modify manifest + modify protected block) followed by
    commit B (revert manifest to original bytes; leave protected block
    edit) leaves HEAD-vs-base manifest BYTES equal, but `git log -1
    -- manifest` still resolves to commit B as the baseline, and
    `git show B:<protected>` returns the modified content — self-baseline
    attack reappears. Fix: also reject any commit that *touches* the
    manifest in the `merge-base..HEAD` range, regardless of final bytes.

    Returns (True, None) on success or when the guard cannot be evaluated
    (no PR base detectable — local detached state). Returns (False, msg)
    when the manifest changed in the PR or was touched by any PR commit.
    """
    pr_base = _detect_pr_base_ref()
    if pr_base is None:
        # Local-only / detached state: treat as advisory — surface a note but
        # don't block. The CI run will catch the attack.
        return True, None
    rc_mb, mb, _ = _run_git(["merge-base", pr_base, "HEAD"])
    if rc_mb != 0 or not mb:
        # Cannot compute merge-base (fork without origin?). Be conservative:
        # warn but do not block — CI on the canonical repo will catch it.
        return True, None
    mb = mb.strip()
    rel = "scripts/v3_6_7_inversion_manifest.json"

    # Round-4 closure: scan merge-base..HEAD for ANY commit that touches the
    # manifest, regardless of whether the final HEAD bytes equal the base
    # bytes. This catches the "touch and revert" pattern where a PR commit
    # modifies the manifest + a protected block, then a later PR commit
    # reverts only the manifest.
    rc_log, log_out, log_err = _run_git([
        "log", "--format=%H", f"{mb}..HEAD", "--", rel,
    ])
    if rc_log != 0:
        # Couldn't list touching commits — be loud, don't pass silently.
        return False, (
            "[ARS-V3.7.1 LINT ERROR: anti-self-baseline guard cannot list "
            f"manifest-touching commits in {mb[:12]}..HEAD: rc={rc_log} "
            f"stderr={log_err!r}]"
        )
    touching = [c for c in log_out.splitlines() if c.strip()]
    if touching:
        commits_str = ", ".join(c[:12] for c in touching[:5])
        suffix = f" (and {len(touching) - 5} more)" if len(touching) > 5 else ""
        return False, (
            "[ARS-V3.7.1 LINT ERROR: anti-self-baseline guard tripped: "
            f"v3.6.7 manifest touched by {len(touching)} commit(s) in "
            f"{mb[:12]}..HEAD: {commits_str}{suffix}. The byte-equivalence "
            "SHA gate uses the manifest's most recent modifying commit as "
            "its baseline; allowing ANY manifest touch in the PR (even one "
            "later reverted) would let the gate hash modified content "
            "against itself. Land manifest amendments in a SEPARATE PR "
            "under a v3.7+ amendment process so the next SHA gate run "
            "sees the new manifest as its baseline. "
            "(round-2 + round-4 codex P2 closure)]"
        )

    # Defense-in-depth: also verify final HEAD bytes match base bytes.
    # If `git log` somehow under-reports touches (e.g. a corrupted history
    # or a bug in the path filter), the byte comparison still catches the
    # final-state mismatch. This is the round-2 guard, kept as backstop.
    head_path = REPO_ROOT / rel
    head_bytes = head_path.read_bytes() if head_path.exists() else None
    base_bytes, err = _read_blob_at_commit(mb, rel)
    if err is not None:
        return False, (
            "[ARS-V3.7.1 LINT ERROR: anti-self-baseline guard tripped: "
            "v3.6.7 manifest does not exist at PR base commit "
            f"{mb[:12]}. Manifest creation / re-creation is not a "
            "v3.7.1-work-PR action. Land manifest changes in a separate "
            "amendment PR (round-2 codex P2 closure)]"
        )
    if head_bytes is None:
        return False, (
            "[ARS-V3.7.1 LINT ERROR: anti-self-baseline guard tripped: "
            "v3.6.7 manifest is missing at PR HEAD but present at PR base. "
            "Deletion is not a v3.7.1-work-PR action]"
        )
    if head_bytes != base_bytes:
        return False, (
            "[ARS-V3.7.1 LINT ERROR: anti-self-baseline guard tripped: "
            "v3.6.7 manifest bytes differ between HEAD and PR base, but "
            "no commit in merge-base..HEAD lists it as a path. This is a "
            "history-shape anomaly — investigate before proceeding]"
        )
    return True, None


def _strip_file_bom(file_bytes: bytes) -> bytes:
    """Strip a UTF-8 BOM at byte 0 of the FILE, if present.

    Per spec § Step 0 SHA normalization: "the FILE's BOM (if any) is
    excluded". This strips ONLY the file-level BOM, NOT BOMs that may
    appear later in the file (e.g. inserted right before a protected
    heading as a hidden mutation — round-8 codex P2 closure: spec
    exclusion is file-level only, so block-level BOMs must remain in
    the hashed range so heading-prefix attacks like inserting U+FEFF
    before `## PATTERN PROTECTION (v3.6.7)` are caught).
    """
    if file_bytes.startswith(_BOM):
        return file_bytes[len(_BOM):]
    return file_bytes


# Backward-compat alias for the old name used by the unit test that pins
# BOM-stripping behaviour (test renamed in the round-8 closure commit).
_normalize_bytes = _strip_file_bom


def _extract_block_bytes(file_bytes: bytes) -> bytes | None:
    """Extract the v3.6.7 PATTERN PROTECTION block as bytes.

    Spec § 388 canonical range: "start at the line containing
    `## PATTERN PROTECTION (v3.6.7)` heading; end at the line before the
    next H1 / H2 / H3 heading or EOF". The `## ` heading prefix is part
    of the canonical byte range.

    Spec § Step 0 SHA normalization: "bytes are read raw; the FILE's
    BOM (if any) is excluded". File-level BOM stripping happens BEFORE
    extraction (caller passes raw file bytes to this function); BOMs
    that appear later in the file (e.g. inserted before a protected
    heading) are NOT stripped — they're real content mutations the
    gate must detect (round-8 codex P2 closure).

    The v3.6.7 lint's `_extract_block` finds the marker via case-
    insensitive substring match, so it starts the returned slice at
    `PATTERN...` and silently strips the `## ` (or any other) heading
    prefix. That means a mutation of `## PATTERN...` to `### PATTERN...`
    leaves the v3.6.7 lint's extracted block byte-identical, which is
    fine for v3.6.7's invariant greps but DEFEATS the v3.7.1 byte-
    equivalence gate's heading-prefix check (round-3 codex P2 closure).

    This wrapper extends the start of the v3.6.7 extractor's range
    backward to the start of the marker's line, so the hashed bytes
    include the heading prefix exactly as the spec requires. The end
    position and termination logic are untouched, so the byte range
    stays byte-equivalent to the v3.6.7 extractor everywhere except the
    heading prefix.

    Returns None when the marker is missing.
    """
    # Strip file-level BOM (byte 0 only) per spec § Step 0. This is the
    # ONLY BOM-stripping point in the pipeline; block-level BOMs stay in
    # the hashed range (round-8 closure: BOM-before-heading mutation
    # must be caught).
    file_bytes = _strip_file_bom(file_bytes)
    text = file_bytes.decode("utf-8", errors="replace")

    # Round-10 codex P2 closure: do NOT delegate to the v3.6.7 extractor.
    # That extractor uses a substring search (`text.lower().find(marker)`),
    # so when prose before the protected block mentions
    # `PATTERN PROTECTION (v3.6.7)`, it returns the slice starting at the
    # PROSE position. Earlier rounds tried to "correct" by anchoring the
    # heading line afterward and reusing `len(block)`, but the slice
    # length still came from the prose-to-heading fragment, not the real
    # block — so the hashed range was wrong.
    #
    # Round-9 + Round-10 fix: anchor the START at the heading line, AND
    # compute the END independently by searching for the next H1/H2/H3
    # heading after the marker line (or EOF). This mirrors the v3.6.7
    # lint's heading-to-next-heading-or-EOF termination semantics, but
    # with a true heading-anchored start.
    #
    # Pattern: line start, optional indent, 1-3 `#`, whitespace, the marker
    # text. NO `\b` after the marker (ends with `)`, a non-word char).
    # `(?m)` makes `^` match line starts; `(?i)` is the v3.6.7 convention.
    heading_re = re.compile(
        r"(?im)^[ \t]*#{1,3}[ \t]+" + re.escape(V3_6_7_PROTECTION_BLOCK)
    )
    match = heading_re.search(text)
    if match is None:
        # Heading-anchored search found nothing; the marker may exist only
        # as prose (no `#` prefix). Treat as missing.
        return None
    line_start = match.start()

    # Find block end at next H1/H2/H3 heading after the marker LINE, or EOF.
    next_heading_re = re.compile(r"(?m)^[ \t]*#{1,3}[ \t]+")
    eol = text.find("\n", match.end())
    search_start = (eol + 1) if eol >= 0 else len(text)
    next_match = next_heading_re.search(text, pos=search_start)
    block_end = next_match.start() if next_match else len(text)
    block_with_prefix = text[line_start:block_end]
    return block_with_prefix.encode("utf-8")


def _read_blob_at_commit(commit: str, repo_relpath: str) -> tuple[bytes | None, str | None]:
    """Return (raw bytes, error). Uses `git show <commit>:<path>`."""
    result = subprocess.run(
        ["git", "show", f"{commit}:{repo_relpath}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        return None, (
            f"[ARS-V3.7.1 LINT ERROR: `git show {commit}:{repo_relpath}` "
            f"failed: {stderr!r}]"
        )
    return result.stdout, None


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _load_v3_6_7_manifest() -> tuple[list[str] | None, str | None]:
    """Read the v3.6.7 manifest and return (file_list, error)."""
    if not V3_6_7_MANIFEST.exists():
        return None, (
            "[ARS-V3.7.1 LINT ERROR: v3.6.7 manifest missing at "
            f"{V3_6_7_MANIFEST.relative_to(REPO_ROOT)}]"
        )
    try:
        data = json.loads(V3_6_7_MANIFEST.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"[ARS-V3.7.1 LINT ERROR: v3.6.7 manifest unreadable: {exc}]"
    files = data.get("files")
    if not isinstance(files, list) or not all(isinstance(p, str) for p in files):
        return None, (
            "[ARS-V3.7.1 LINT ERROR: v3.6.7 manifest 'files' must be a list "
            "of strings]"
        )
    return files, None


def _load_v3_6_8_manifest() -> tuple[dict | None, str | None]:
    """Read the v3.6.8 manifest. PR-1 ships an empty list; Step 3a populates."""
    if not V3_6_8_MANIFEST.exists():
        return None, (
            "[ARS-V3.7.1 LINT ERROR: v3.6.8 manifest missing at "
            f"{V3_6_8_MANIFEST.relative_to(REPO_ROOT)}]"
        )
    try:
        data = json.loads(V3_6_8_MANIFEST.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"[ARS-V3.7.1 LINT ERROR: v3.6.8 manifest unreadable: {exc}]"
    if data.get("scope") != "v3.6.8-only":
        return None, (
            "[ARS-V3.7.1 LINT ERROR: v3.6.8 manifest 'scope' must be "
            f"'v3.6.8-only', got {data.get('scope')!r}]"
        )
    files = data.get("files")
    if not isinstance(files, list) or not all(isinstance(p, str) for p in files):
        return None, (
            "[ARS-V3.7.1 LINT ERROR: v3.6.8 manifest 'files' must be a list "
            "of strings (may be empty until Step 3a populates)]"
        )
    return data, None


def check_byte_equivalence(verbose: bool = True) -> int:
    """Run the SHA byte-equivalence gate.

    Returns 0 on PASS, 1 on FAIL. Side effect: prints diagnostic lines to stdout.
    """
    # 1. Shallow-clone gate (CI safety)
    err = _ensure_full_clone()
    if err is not None:
        print(err)
        return 1

    # 2. Anti-self-baseline guard (round-2 codex P2 closure):
    #    Refuse to run on PRs that mutate the v3.6.7 manifest. Without this,
    #    `git log -1 -- v3_6_7_inversion_manifest.json` would resolve to the
    #    PR's own commit and the SHA comparison would hash modified content
    #    against itself.
    ok, err = _v3_6_7_manifest_unchanged_in_pr()
    if not ok:
        print(err)
        return 1

    # 3. v3.6.7 base commit derivation (single source of truth)
    base_commit, err = _v3_6_7_base_commit()
    if err is not None:
        print(err)
        return 1
    if verbose:
        print(f"[v3.7.1 SHA gate] v3.6.7 base commit: {base_commit[:12]}")

    # 3. Load v3.6.7 manifest (file list = single source of truth)
    files_v367, err = _load_v3_6_7_manifest()
    if err is not None:
        print(err)
        return 1
    if not files_v367:
        # An empty v3.6.7 manifest would be a contract violation; fail loud.
        print(
            "[ARS-V3.7.1 LINT ERROR: v3.6.7 manifest carries empty file list; "
            "expected the three v3.6.7-frozen agent files]"
        )
        return 1

    # 4. Load v3.6.8 manifest (just for shape validation; entries unused here)
    _, err = _load_v3_6_8_manifest()
    if err is not None:
        print(err)
        return 1

    # 5. For each v3.6.7 protected file: extract block at HEAD and at base
    # commit, hash both, assert equality.
    failures: list[str] = []
    for rel in files_v367:
        head_path = REPO_ROOT / rel
        if not head_path.exists():
            failures.append(
                f"  [{rel}] missing at PR HEAD (deletion of v3.6.7-protected "
                "file would re-open v3.6.7 convergence; restore the file)"
            )
            continue
        head_bytes_full = head_path.read_bytes()
        head_block = _extract_block_bytes(head_bytes_full)
        if head_block is None:
            failures.append(
                f"  [{rel}] PATTERN PROTECTION (v3.6.7) marker missing at "
                "PR HEAD (the v3.6.7-tagged block was renamed or removed; "
                "boundary rule violated — v3.7.1 must NOT mutate v3.6.7 blocks)"
            )
            continue
        base_bytes_full, err = _read_blob_at_commit(base_commit, rel)
        if err is not None:
            failures.append(f"  [{rel}] {err}")
            continue
        base_block = _extract_block_bytes(base_bytes_full)
        if base_block is None:
            failures.append(
                f"  [{rel}] PATTERN PROTECTION (v3.6.7) marker missing at "
                f"v3.6.7 base commit {base_commit[:12]} — manifest "
                "derivation produced an inconsistent base"
            )
            continue
        head_sha = _sha256(head_block)
        base_sha = _sha256(base_block)
        if head_sha != base_sha:
            failures.append(
                f"  [{rel}] BYTE-EQUIVALENCE FAIL\n"
                f"      HEAD     SHA-256: {head_sha}\n"
                f"      v3.6.7   SHA-256: {base_sha}\n"
                f"      v3.6.7-tagged PATTERN PROTECTION block changed; "
                f"v3.7.1 boundary rule violated. Restore the block or land "
                f"a v3.6.7+ amendment manifest first."
            )
        elif verbose:
            print(f"  [{rel}] PASS (sha256={head_sha[:12]})")

    if failures:
        print("[ARS-V3.7.1 LINT ERROR: v3.6.7 PATTERN PROTECTION block byte-equivalence failures]")
        for line in failures:
            print(line)
        return 1
    if verbose:
        print(f"[v3.7.1 SHA gate] PASSED ({len(files_v367)} v3.6.7 protected file(s))")
    return 0


def main() -> int:
    return check_byte_equivalence()


if __name__ == "__main__":
    sys.exit(main())
