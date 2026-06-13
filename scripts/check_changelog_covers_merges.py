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
