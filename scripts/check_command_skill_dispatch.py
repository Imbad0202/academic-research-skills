"""Check plugin command entry points and rooted skill references (#857).

This is a static packaging check, not evidence of model invocation. Runtime
acceptance also inspects Skill calls and supporting-file reads outside the repo.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

TARGETS = {
    "ars-full": "academic-pipeline",
    "ars-reviewer": "academic-paper-reviewer",
    "ars-3w": "deep-research",
    **{f"ars-{mode}": "academic-paper" for mode in (
        "plan", "outline", "revision", "revision-coach", "rebuttal-audit",
        "abstract", "lit-review", "format-convert", "citation-check", "disclosure",
    )},
}
UTILITY_COMMANDS = {"ars-mark-read", "ars-unmark-read", "ars-cache-invalidate"}
ROOT = "${CLAUDE_PLUGIN_ROOT}/"
REFERENCES = re.compile(
    r"(?:\$\{CLAUDE_PLUGIN_ROOT\}/)?"
    r"(?:MODE_REGISTRY\.md|(?:[A-Za-z0-9_.-]+/)+SKILL\.md)"
)


def check(root: Path) -> list[str]:
    errors = []
    paths = {p.stem: p for p in (root / "commands").glob("*.md")}
    for name in sorted(set(TARGETS) - paths.keys()):
        errors.append(f"commands/{name}.md: missing command")
    for name, path in sorted(paths.items()):
        text = path.read_text(encoding="utf-8")
        for reference in REFERENCES.findall(text):
            if not reference.startswith(ROOT):
                errors.append(f"{path.name}: unrooted plugin reference {reference!r}")
        if name in UTILITY_COMMANDS:
            continue
        if name not in TARGETS:
            errors.append(f"{path.name}: classify new command as skill dispatch or utility")
            continue
        target = TARGETS[name]
        frontmatter = text.split("---", 2)[1] if text.startswith("---\n") and text.count("---") >= 2 else ""
        visibility = re.findall(
            r'''(?m)^\s*(?:disable-model-invocation|'disable-model-invocation'|"disable-model-invocation")\s*:.*$''',
            frontmatter,
        )
        if len(visibility) != 1 or visibility[0].strip() != "disable-model-invocation: true":
            errors.append(f"{path.name}: command must be user-invocable only; models invoke the core skill")
        call = f'First invoke the Skill tool with `skill: "academic-research-skills:{target}"`.'
        if call not in text:
            errors.append(f"{path.name}: missing explicit Skill call to {target}")
        for reference in (
            f"Mode reference: `{ROOT}MODE_REGISTRY.md`",
            f"Skill entry: `{ROOT}{target}/SKILL.md`.",
        ):
            if reference not in text:
                errors.append(f"{path.name}: missing {reference}")
        if not (root / target / "SKILL.md").is_file():
            errors.append(f"{path.name}: target skill file does not exist")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check(args.repo_root)
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {len(TARGETS)} mode commands invoke their skill with rooted references")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
