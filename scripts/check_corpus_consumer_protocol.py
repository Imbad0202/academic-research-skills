#!/usr/bin/env python3
"""Lint corpus consumer protocol per spec §5.2 (v3.6.5).

Enforces nine invariants L1–L9. Manifest-driven for L3–L6.
Exit 0 on pass, exit 1 on fail. Prints aggregated failure list.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Callable

# Path.cwd() (not __file__) is intentional: fixture-based tests in
# scripts/adapters/tests/test_check_corpus_consumer_protocol.py invoke
# this lint via subprocess.run(..., cwd=fixture_repo) and rely on cwd
# to swap repo state. Path(__file__) would hard-code the real repo.
REPO_ROOT = Path.cwd()
MANIFEST_PATH = REPO_ROOT / "scripts" / "corpus_consumer_manifest.json"
REF_DOC_PATH = REPO_ROOT / "academic-pipeline" / "references" / "literature_corpus_consumers.md"
HANDOFF_SCHEMAS = REPO_ROOT / "shared" / "handoff_schemas.md"

STUB_MARKER = "<!-- LINT_STUB: skip_cross_check -->"
STUB_STATUS_LINE = "**Status:** Stub — implementation in PR-B (v3.6.5)"
DEFERRED_CAVEAT = "Consumer-side integration deferred to v3.6.5+"
REF_DOC_BACKPOINTER = "academic-pipeline/references/literature_corpus_consumers.md"

PR_A_SET = frozenset({"bibliography_agent"})
PR_B_SET = frozenset({"bibliography_agent", "literature_strategist_agent"})


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def manifest_basenames() -> frozenset[str]:
    return frozenset(c["agent_basename"] for c in load_manifest()["supported_consumers"])


def find_consumer_blocks(ref_text: str) -> dict[str, str]:
    """Return mapping basename -> block text (from `## Consumer: <basename>` heading
    to next `## ` heading or EOF)."""
    pattern = re.compile(r"^## Consumer:\s+(\S+)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(ref_text))
    out: dict[str, str] = {}
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(ref_text)
        out[m.group(1)] = ref_text[start:end]
    return out


def check_l1() -> list[str]:
    if not REF_DOC_PATH.exists():
        return [f"L1: reference doc {REF_DOC_PATH.relative_to(REPO_ROOT)} does not exist"]
    return []


def check_l2() -> list[str]:
    if not REF_DOC_PATH.exists():
        return []  # L1 already failed
    text = REF_DOC_PATH.read_text(encoding="utf-8")
    blocks = find_consumer_blocks(text)
    failures: list[str] = []

    manifest_set = manifest_basenames()
    for basename in manifest_set:
        if basename not in blocks:
            failures.append(
                f"L2: manifest entry '{basename}' has no '## Consumer: {basename}' heading in reference doc"
            )

    for basename, block in blocks.items():
        is_stub = STUB_MARKER in block
        if is_stub:
            if STUB_STATUS_LINE not in block:
                failures.append(
                    f"L2: stub block '{basename}' has LINT_STUB marker but missing '{STUB_STATUS_LINE}'"
                )
            if basename in manifest_set:
                failures.append(
                    f"L2: '{basename}' is in manifest but block carries LINT_STUB marker (must be full block, not stub)"
                )
        else:
            if basename not in manifest_set:
                failures.append(
                    f"L2: '{basename}' has full consumer block but is not in manifest"
                )
    return failures


CHECKS: list[tuple[str, Callable[[], list[str]]]] = [
    ("L1", check_l1),
    ("L2", check_l2),
]


def main() -> int:
    all_failures: list[str] = []
    for name, fn in CHECKS:
        try:
            failures = fn()
        except Exception as exc:
            all_failures.append(f"{name}: check raised {type(exc).__name__}: {exc}")
            continue
        all_failures.extend(failures)

    if all_failures:
        print("Corpus consumer protocol lint FAILED:", file=sys.stderr)
        for f in all_failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("Corpus consumer protocol lint OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
