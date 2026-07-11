#!/usr/bin/env python3
"""Model-tiering classification drift guard (#517).

The tiering mechanism (shared/model_tiering.md) is prose + manifest: agent files are
never edited, so the only thing that can rot is the CLASSIFICATION — an agent added
without a tier, a manifest entry pointing at a deleted file, or the canonical table
and the manifest silently disagreeing. This lint pins all three:

  1. SET EQUALITY — the ``*_agent.md`` files on disk (five skill agent dirs; the
     top-level ``agents/`` plugin mirror is excluded, it is byte-pinned separately
     by check_agents_mirror_sync.py) exactly match the manifest's ``path`` set.
     A new agent without a tier assignment fails CI here.
  2. TIER ENUM — every manifest ``tier`` is ``judgment`` or ``execution``.
  3. DOC SYNC — shared/model_tiering.md's classification table names every agent
     (backticked short name, in the table row matching the agent's skill) under the
     correct tier section, and each section's headline count matches the manifest.

Exit codes: 0 = pass; 1 = drift found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "scripts" / "model_tiering_manifest.json"
DOC = REPO / "shared" / "model_tiering.md"

# The five skill agent dirs in scope. The top-level plugin mirror dir `agents/` is
# deliberately NOT listed (byte-copies, guarded by check_agents_mirror_sync.py).
AGENT_DIRS = [
    "deep-research/agents",
    "academic-paper/agents",
    "academic-paper-reviewer/agents",
    "academic-pipeline/agents",
    "shared/agents",
]

VALID_TIERS = {"judgment", "execution"}

JUDGMENT_HEADING = re.compile(r"^### Judgment-type \((\d+)\)", re.M)
EXECUTION_HEADING = re.compile(r"^### Execution-type \((\d+)\)", re.M)


def disk_agent_paths() -> set[str]:
    found: set[str] = set()
    for d in AGENT_DIRS:
        base = REPO / d
        if not base.is_dir():
            continue
        for f in sorted(base.glob("*_agent.md")):
            found.add(f.relative_to(REPO).as_posix())
    return found


def load_manifest() -> list[dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    agents = data.get("agents")
    if not isinstance(agents, list) or not agents:
        raise ValueError("manifest 'agents' must be a non-empty list")
    return agents


def short_name(path: str) -> str:
    return Path(path).name.removesuffix("_agent.md")


def skill_of(path: str) -> str:
    # 'shared/agents/x.md' -> 'shared'; 'deep-research/agents/x.md' -> 'deep-research'
    return path.split("/", 1)[0]


def doc_sections(text: str) -> tuple[str, int, str, int]:
    jm = JUDGMENT_HEADING.search(text)
    em = EXECUTION_HEADING.search(text)
    if not jm or not em:
        raise ValueError("canonical doc is missing a '### Judgment-type (N)' or '### Execution-type (N)' heading")
    if em.start() < jm.start():
        raise ValueError("canonical doc tier sections are out of the expected order (Judgment before Execution)")
    judgment_body = text[jm.end() : em.start()]
    execution_body = text[em.end() :]
    return judgment_body, int(jm.group(1)), execution_body, int(em.group(1))


def skill_row(section: str, skill: str) -> str:
    """Return the table row whose first cell starts with exactly this skill label."""
    for line in section.splitlines():
        if re.match(rf"^\|\s*{re.escape(skill)} \(\d+\)\s*\|", line):
            return line
    return ""


def main() -> int:
    errors: list[str] = []

    try:
        agents = load_manifest()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[model-tiering] FAIL: cannot load manifest: {exc}")
        return 1

    manifest_paths = [a.get("path", "") for a in agents]
    manifest_set = set(manifest_paths)
    if len(manifest_set) != len(manifest_paths):
        dupes = sorted({p for p in manifest_paths if manifest_paths.count(p) > 1})
        errors.append(f"manifest contains duplicate path(s): {dupes}")

    # 1. set equality with disk
    disk = disk_agent_paths()
    missing_from_manifest = sorted(disk - manifest_set)
    missing_from_disk = sorted(manifest_set - disk)
    for p in missing_from_manifest:
        errors.append(f"agent file on disk has NO tier classification: {p} (add it to scripts/model_tiering_manifest.json AND shared/model_tiering.md)")
    for p in missing_from_disk:
        errors.append(f"manifest classifies a file that does not exist on disk: {p}")

    # 2. tier enum
    for a in agents:
        if a.get("tier") not in VALID_TIERS:
            errors.append(f"invalid tier {a.get('tier')!r} for {a.get('path')} (must be one of {sorted(VALID_TIERS)})")

    # 3. doc sync
    try:
        text = DOC.read_text(encoding="utf-8")
        judgment_body, judgment_count, execution_body, execution_count = doc_sections(text)
    except (OSError, ValueError) as exc:
        print(f"[model-tiering] FAIL: cannot parse canonical doc: {exc}")
        return 1

    by_tier = {"judgment": [], "execution": []}
    for a in agents:
        if a.get("tier") in by_tier:
            by_tier[a["tier"]].append(a["path"])

    if judgment_count != len(by_tier["judgment"]):
        errors.append(f"doc says Judgment-type ({judgment_count}) but manifest has {len(by_tier['judgment'])}")
    if execution_count != len(by_tier["execution"]):
        errors.append(f"doc says Execution-type ({execution_count}) but manifest has {len(by_tier['execution'])}")

    for tier, body in (("judgment", judgment_body), ("execution", execution_body)):
        other_body = execution_body if tier == "judgment" else judgment_body
        for path in by_tier[tier]:
            name = short_name(path)
            skill = skill_of(path)
            row = skill_row(body, skill)
            token = f"`{name}`"
            if token not in row:
                errors.append(f"{path} is '{tier}' in the manifest but {token} is not in the {tier} section's '{skill}' table row of {DOC.relative_to(REPO)}")
            other_row = skill_row(other_body, skill)
            if token in other_row:
                errors.append(f"{path} appears in BOTH tier sections' '{skill}' rows in {DOC.relative_to(REPO)} — a tier must be unambiguous")

    if errors:
        print(f"[model-tiering] FAIL ({len(errors)} error(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"[model-tiering] PASS: {len(agents)} agents classified ({len(by_tier['judgment'])} judgment / {len(by_tier['execution'])} execution); disk, manifest, and canonical table agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
