#!/usr/bin/env python3
"""
Detect thesis template and report key requirements.

Usage:
    uv run python detect_template.py main.tex
    uv run python detect_template.py main.tex --json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

try:
    from map_structure import ThesisStructureMapper
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from map_structure import ThesisStructureMapper

TEMPLATE_REFERENCE_FILES = {
    "thuthesis": "tsinghua.md",
    "pkuthss": "pku.md",
    "ctexbook": "generic.md",
    "ustcthesis": "generic.md",
    "fduthesis": "generic.md",
}


def _reference_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "UNIVERSITIES"


def _reference_file(template_id: Optional[str]) -> Optional[Path]:
    if not template_id:
        template_id = "ctexbook"
    file_name = TEMPLATE_REFERENCE_FILES.get(template_id)
    if not file_name:
        return None
    path = _reference_dir() / file_name
    return path if path.exists() else None


def _extract_key_requirements(md_path: Path) -> list[str]:
    try:
        lines = md_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []

    in_section = False
    subsection = None
    requirements: list[str] = []

    for line in lines:
        if line.startswith("## "):
            title = line[3:].strip()
            in_section = "特殊格式要求" in title or "注意事项" in title
            subsection = None
            continue

        if line.startswith("### "):
            subsection = line[4:].strip()
            continue

        if not in_section:
            continue

        stripped = line.strip()
        if not stripped:
            continue

        is_bullet = stripped.startswith(("-", "*")) or re.match(r"^\d+\.", stripped)
        if not is_bullet:
            continue

        text = re.sub(r"^[-*]\s*", "", stripped)
        text = re.sub(r"^\d+\.\s*", "", text)
        if subsection:
            requirements.append(f"{subsection}: {text}")
        else:
            requirements.append(text)

    return requirements


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect thesis template")
    parser.add_argument("tex_file", help="Main .tex file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    tex_path = Path(args.tex_file)
    if not tex_path.exists():
        print(f"[ERROR] File not found: {args.tex_file}", file=sys.stderr)
        sys.exit(1)

    mapper = ThesisStructureMapper(str(tex_path))
    mapper.map()

    template_id = mapper.template
    template_info = mapper.get_template_info() or {}
    ref_path = _reference_file(template_id)
    key_requirements = _extract_key_requirements(ref_path) if ref_path else []

    result = {
        "template": template_id or "unknown",
        "name": template_info.get("name"),
        "figure_format": template_info.get("figure_format"),
        "reference_file": str(ref_path) if ref_path else None,
        "key_requirements": key_requirements,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"Template: {result['template']}")
    if result["name"]:
        print(f"Name: {result['name']}")
    if result["figure_format"]:
        print(f"Figure format: {result['figure_format']}")
    if result["reference_file"]:
        print(f"Reference: {result['reference_file']}")
    if result["key_requirements"]:
        print("Key requirements:")
        for item in result["key_requirements"]:
            print(f"  - {item}")
    else:
        print("Key requirements: (not found)")


if __name__ == "__main__":
    main()
