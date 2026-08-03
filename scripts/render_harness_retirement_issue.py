#!/usr/bin/env python3
"""Render the monthly harness-retirement tracking issue (#617).

The Bucket A inventory comes only from ``ars_phase_scope_manifest.json``.
Keeping scope assembly out of the workflow prevents the generated issue from
silently drifting when an agent is added, renamed, or moved between skills.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "scripts" / "ars_phase_scope_manifest.json"
MONTH_RE = re.compile(r"[0-9]{4}-(?:0[1-9]|1[0-2])")
SAFE_ID_RE = re.compile(r"[a-z0-9][a-z0-9_-]*")

DEBT_CATEGORIES = (
    (
        "Capability-era workarounds",
        "role priming, coercion, or retries justified only by superseded "
        "capability limits",
    ),
    (
        "Pre-tool-use scaffolds",
        "manual validation duplicated by deterministic runtime or tool "
        "enforcement",
    ),
    (
        "Verbose reasoning scaffolds",
        "step-by-step templates retained without a current task-level need",
    ),
    (
        "Defensive few-shot examples",
        "examples retained only for historical failure modes that no longer "
        "reproduce",
    ),
    (
        "Format guards",
        "duplicated output-shape instructions already enforced by schemas or "
        "checkers",
    ),
    (
        "Deprecated tool references",
        "renamed or removed tools, options, and signatures",
    ),
)


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load scope manifest {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("scope manifest root must be an object")
    return data


def bucket_a_by_skill(manifest: dict[str, Any]) -> dict[str, list[str]]:
    agents = manifest.get("agents")
    if not isinstance(agents, dict):
        raise ValueError("scope manifest must contain an agents object")

    grouped: dict[str, list[str]] = defaultdict(list)
    for name, row in agents.items():
        if not isinstance(name, str) or SAFE_ID_RE.fullmatch(name) is None:
            raise ValueError(f"unsafe agent name in scope manifest: {name!r}")
        if not isinstance(row, dict):
            raise ValueError(f"agent {name!r} must map to an object")
        if row.get("bucket") != "A":
            continue
        skill = row.get("skill")
        if not isinstance(skill, str) or SAFE_ID_RE.fullmatch(skill) is None:
            raise ValueError(f"Bucket A agent {name!r} has an invalid skill")
        grouped[skill].append(name)

    if not grouped:
        raise ValueError("scope manifest contains no Bucket A agents")
    return dict(grouped)


def render_issue(month: str, manifest: dict[str, Any]) -> str:
    if MONTH_RE.fullmatch(month) is None:
        raise ValueError("month must use YYYY-MM with a valid month number")

    grouped = bucket_a_by_skill(manifest)
    total = sum(len(names) for names in grouped.values())
    version = manifest.get("version")
    version_note = f" (manifest v{version})" if isinstance(version, int) else ""

    lines = [
        f"## Harness retirement audit — {month}",
        "",
        "Run `/harness-retirement` locally against ARS agents and paste the report below.",
        "",
        "### Scope",
        "",
        (
            f"All {total} Bucket A agents from "
            f"`scripts/ars_phase_scope_manifest.json`{version_note}:"
        ),
        "",
    ]
    for skill, names in grouped.items():
        rendered_names = ", ".join(f"`{name}`" for name in names)
        lines.append(f"- `{skill}` (×{len(names)}): {rendered_names}")

    lines.extend(["", "### Six debt categories", ""])
    for heading, description in DEBT_CATEGORIES:
        lines.append(f"- [ ] **{heading}** — {description}")

    lines.extend([
        "",
        "### Output checklist",
        "",
        "- [ ] Audit report posted as comment",
        (
            "- [ ] P0 retirements scheduled (open separate issues with "
            "`harness-retirement` label)"
        ),
        "- [ ] P1 retirements logged in CHANGELOG [Unreleased]",
        "- [ ] P2+ added to backlog",
        "",
        "---",
        "_Auto-opened by harness-retirement-monthly.yml. Close once audit complete._",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True, help="Audit month in YYYY-MM form")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Bucket A scope manifest",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write Markdown to this path instead of stdout",
    )
    args = parser.parse_args(argv)

    try:
        rendered = render_issue(args.month, load_manifest(args.manifest))
    except ValueError as exc:
        parser.error(str(exc))

    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
