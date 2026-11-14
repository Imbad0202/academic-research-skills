#!/usr/bin/env python3
"""Install the ARS wrapper plugin for Google Antigravity (`agy`).

Usage: python3 antigravity/install.py

Writes a native Antigravity plugin to ~/.gemini/config/plugins/academic-research-skills/.
The plugin holds no ARS content: each skill is a short loader that points at the original
file in this checkout. Antigravity loads only the first 24,000 bytes of a skill body and
ignores symlinked skills, so the original SKILL.md files cannot be mounted directly.
Re-run after moving the checkout. Remove with `agy plugin uninstall academic-research-skills`.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ["deep-research", "academic-paper", "academic-paper-reviewer", "academic-pipeline"]
MARKER = ".ars-antigravity-wrapper"  # proves a directory is ours before we replace it

LOADER = """
This is the Antigravity loader for the ARS `{name}` skill. The skill's instructions are not on this page.

Before anything else, read this file from its first line to its last line:

    {root}/{name}/SKILL.md

It is about {kb} KB. If one read returns only part of it, keep reading until the end. Then follow it as this skill's instructions, under the rules below.

"""


def split_frontmatter(text):
    """Return (frontmatter block including both --- lines, body)."""
    if not text.startswith("---\n"):
        raise SystemExit("error: expected YAML frontmatter at the top of an ARS file")
    end = text.index("\n---\n", 4) + len("\n---\n")
    return text[:end], text[end:]


def build(dest):
    root = ROOT.as_posix()
    note = (ROOT / "antigravity" / "compatibility.md").read_text(encoding="utf-8").replace("{root}", root)
    out = {}
    for name in SKILLS:
        src = ROOT / name / "SKILL.md"
        front, _ = split_frontmatter(src.read_text(encoding="utf-8"))
        kb = -(-src.stat().st_size // 1024)
        out[name] = front + LOADER.format(name=name, root=root, kb=kb) + note
    for cmd in sorted((ROOT / "commands").glob("ars-*.md")):
        front, body = split_frontmatter(cmd.read_text(encoding="utf-8"))
        out[cmd.stem] = front + body.replace("${CLAUDE_PLUGIN_ROOT}", root).rstrip() + "\n\n" + note
    version = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    manifest = {
        "name": "academic-research-skills",
        "description": "Antigravity wrapper for Academic Research Skills (ARS): research, write, "
                       "review, revise, finalize. Loads the original ARS files from " + root + ".",
        "version": version,
        "homepage": "https://github.com/Imbad0202/academic-research-skills",
    }
    dest.mkdir(parents=True)
    (dest / MARKER).write_text(root + "\n", encoding="utf-8")
    (dest / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for name, text in out.items():
        assert len(text.encode("utf-8")) < 24000, name  # the limit this wrapper exists to avoid
        skill = dest / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(text, encoding="utf-8")
    return len(out)


def main():
    dest = Path.home() / ".gemini" / "config" / "plugins" / "academic-research-skills"
    if dest.is_symlink() or (dest.exists() and not (dest / MARKER).is_file()):
        sys.exit(f"error: {dest} exists and was not created by this installer.\n"
                 "Remove it first: agy plugin uninstall academic-research-skills")
    if dest.exists():
        shutil.rmtree(dest)
    count = build(dest)
    print(f"Installed {count} skills to {dest}\nARS files are read from {ROOT}\n"
          "Start a new agy session and check /skills.")
    py = shutil.which("python3")
    if not py or subprocess.run([py, "-c", "import yaml"], capture_output=True).returncode != 0:
        print("warning: the python3 on your PATH has no PyYAML. ARS scripts such as the run\n"
              "ledger will not run until you install it (pip install pyyaml).")


if __name__ == "__main__":
    main()
