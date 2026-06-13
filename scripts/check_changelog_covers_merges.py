"""Pre-tag lint: every release-worthy commit since the previous release tag
must be referenced in CHANGELOG.md's [Unreleased] section.

Closes the "merged but undocumented" gap that check_version_consistency.py
(invariants 1-8, pure file reads) does not cover. Runs in PRE-TAG mode: before
the vX.Y.Z tag exists, so [Unreleased] is not yet promoted and `git describe`
returns the PREVIOUS release tag directly.

Spec: docs/design/2026-06-13-changelog-covers-merges-release-gate-spec.md.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# The canonical PR identity is the TRAILING `(#N)` (the GitHub squash suffix).
# Mid-subject refs (tracking issues, spec refs) are NOT the PR identity.
_TRAILING_PR_RE = re.compile(r"\(#(\d+)\)\s*$")


def pr_number(subject: str) -> int | None:
    """Return the trailing `(#N)` PR number of a commit subject, or None."""
    m = _TRAILING_PR_RE.search(subject.rstrip())
    return int(m.group(1)) if m else None


# Conventional-commit prefix: type + optional (scope) + optional ! + colon.
_PREFIX_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]*)\))?!?:")

# Pure-engineering types — never user-facing.
_EXEMPT_TYPES = frozenset({"chore", "test", "ci", "build"})
# Internal design/spec docs that do not belong in a user-facing CHANGELOG.
_EXEMPT_DOCS_SCOPES = frozenset({"design", "superpowers"})


def is_covered(pr: int, unreleased_text: str) -> bool:
    """True iff `#<pr>` appears in the Unreleased text delimited by a non-digit
    on the right (so `#42` does not match `#420`). The leading `#` is required,
    so a bare number in prose cannot spuriously cover."""
    pattern = re.compile(r"#" + str(pr) + r"(?!\d)")
    return pattern.search(unreleased_text) is not None


def is_exempt(subject: str) -> bool:
    """True iff the commit need not be referenced in CHANGELOG.

    Exempt: chore/test/ci/build (any scope), and docs(design)/docs(superpowers).
    Everything else — feat, fix, bare docs, other docs scopes, refactor, perf,
    AND no-prefix subjects — is REQUIRED. Broadening this set reopens the
    original "merged but undocumented" failure mode under different prefixes.
    """
    m = _PREFIX_RE.match(subject)
    if not m:
        return False  # no-prefix subjects are required
    ctype = m.group("type")
    scope = m.group("scope")
    if ctype in _EXEMPT_TYPES:
        return True
    if ctype == "docs" and scope in _EXEMPT_DOCS_SCOPES:
        return True
    return False


@dataclass(frozen=True)
class Uncovered:
    subject: str
    pr: int | None
    reason: str  # "not in [Unreleased]" | "no trailing (#N)"


def audit(subjects: list[str], unreleased_text: str) -> list[Uncovered]:
    """Return the release-worthy commits not provably covered by [Unreleased].

    A no-trailing-(#N) subject is `unverifiable` (a failure, not a skip): we
    cannot prove coverage, so it must be made exempt or given a PR suffix.
    """
    failures: list[Uncovered] = []
    for subject in subjects:
        if is_exempt(subject):
            continue
        pr = pr_number(subject)
        if pr is None:
            failures.append(Uncovered(subject, None, "no trailing (#N)"))
            continue
        if not is_covered(pr, unreleased_text):
            failures.append(Uncovered(subject, pr, "not in [Unreleased]"))
    return failures


# The [Unreleased] section: from its heading to the next top-level `## ` heading.
_UNRELEASED_RE = re.compile(
    r"^##\s*\[Unreleased\]\s*$(?P<body>.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)


def extract_unreleased(changelog_text: str) -> str | None:
    """Return the body text under `## [Unreleased]` up to the next `## ` heading,
    or None if there is no Unreleased section."""
    m = _UNRELEASED_RE.search(changelog_text)
    return m.group("body") if m else None


_TAG_GRAMMAR_RE = re.compile(r"^v\d+(?:\.\d+){1,3}$")


def _git_out(repo: Path, *args: str) -> str | None:
    """Run git in `repo`, return stdout stripped, or None on non-zero exit."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return proc.stdout.strip()


def previous_release_tag(repo: Path) -> str | None:
    """Most recent release tag reachable from HEAD (pre-tag mode: HEAD has no
    new tag, so this IS the previous release). Restricted to the v-tag grammar;
    non-v / nonstandard tags are ignored. None when no matching tag exists."""
    out = _git_out(repo, "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*")
    if out is None or not _TAG_GRAMMAR_RE.match(out):
        return None
    return out


def merged_commit_subjects(repo: Path, since_tag: str) -> list[str]:
    """First-parent commit subjects in `<since_tag>..HEAD`."""
    out = _git_out(repo, "log", "--first-parent", "--format=%s", f"{since_tag}..HEAD")
    if not out:
        return []
    return out.splitlines()


def check(repo: Path, *, first_release: bool = False) -> list[str]:
    """Return a list of error lines; empty means the gate passes."""
    errors: list[str] = []

    changelog = repo / "CHANGELOG.md"
    if not changelog.is_file():
        return [f"{changelog}: not found"]
    unreleased = extract_unreleased(changelog.read_text(encoding="utf-8"))
    if unreleased is None:
        return ["CHANGELOG.md: no '## [Unreleased]' section to verify against"]

    tag = previous_release_tag(repo)
    if tag is None:
        if first_release:
            return []  # explicit first-release: nothing to compare against
        return [
            "no previous release tag found (expected a vX.Y.Z tag reachable "
            "from HEAD). If this is genuinely the first release, pass "
            "--first-release; otherwise this is usually a shallow checkout "
            "(fetch-depth: 0 + fetch-tags: true)."
        ]

    subjects = merged_commit_subjects(repo, tag)
    failures = audit(subjects, unreleased)
    for f in failures:
        ident = f"#{f.pr}" if f.pr is not None else "NO-PR"
        errors.append(f"  {ident}  {f.subject}  [{f.reason}]")
    if errors:
        required = sum(1 for s in subjects if not is_exempt(s))
        errors.insert(
            0,
            f"{len(failures)} of {required} release-worthy commit(s) since "
            f"{tag} are not referenced in CHANGELOG [Unreleased]:",
        )
        errors.append(
            "  Fix: add a CHANGELOG [Unreleased] entry citing the PR number, "
            "or mark the commit exempt via an accepted conventional prefix."
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pre-tag lint: CHANGELOG [Unreleased] must cover every "
        "release-worthy commit since the previous release tag."
    )
    parser.add_argument("--repo", default=".", help="Repo root (default: cwd).")
    parser.add_argument(
        "--first-release", action="store_true",
        help="No previous release tag is expected (first release).",
    )
    args = parser.parse_args(argv)
    errors = check(Path(args.repo), first_release=args.first_release)
    if errors:
        print("\n".join(errors))
        return 1
    print("CHANGELOG [Unreleased] covers all release-worthy commits.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
