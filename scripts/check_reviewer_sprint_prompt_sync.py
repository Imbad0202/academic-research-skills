#!/usr/bin/env python3
"""Exact sync lint for the #611 reviewer sprint-prompt canonical source.

The dispatcher sends each reviewer's Phase 1/Phase 2 H3 body verbatim. A file
pointer cannot replace those bytes under ``--bare --tools ""``. This lint keeps
the runtime mirrors inline while making one marked reference file the editing
source. It enforces two independent locks:

1. rendered canonical fragment == the dispatcher-visible agent section, byte for byte;
2. bounded role slots + canonical marker bodies == an explicitly pinned SHA-256.

The second lock makes a coordinated canonical+mirror edit fail until the
reviewer intentionally re-pins this checker in the same commit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from _skill_lint import heading_section, read_or_exit2


REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_REL = "academic-paper-reviewer/references/reviewer_sprint_prompt_source.md"
SPRINT_REF_REL = "academic-paper-reviewer/references/sprint_contract_protocol.md"
SYNTH_REL = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"

SPRINT_HEADING = "## v3.6.2 Sprint Contract Protocol"
PHASE1_HEADING = "### Phase 1 — Paper-content-blind pre-commitment"
PHASE2_HEADING = "### Phase 2 — Paper-visible review"
SYNTH_HEADING = "## v3.6.2 Sprint Contract Synthesizer Protocol"
SOURCE_CITATION = "reviewer_sprint_prompt_source.md"
BACKLINK = "`references/reviewer_sprint_prompt_source.md`"
SLOT_HEADING = "## Bounded reviewer slots"
SLOT_TABLE_HEADER = (
    "| Agent file | `ROLE` | `PARAPHRASE_LENS` | `REVIEW_BODY_LENS` | "
    "Phase 2 template |"
)
SLOT_TABLE_SEPARATOR = "|---|---|---|---|---|"
PHASE2_TABLE_LABELS = {
    "scoring-phase2": "scoring",
    "da-phase2": "DA-specific",
}

ROLE_CONFIG = {
    "academic-paper-reviewer/agents/eic_agent.md": {
        "ROLE": "eic",
        "PARAPHRASE_LENS": "editorial oversight",
        "REVIEW_BODY_LENS": "editorial oversight",
        "phase2": "scoring-phase2",
    },
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md": {
        "ROLE": "methodology",
        "PARAPHRASE_LENS": "methodology rigor",
        "REVIEW_BODY_LENS": "methodology rigor",
        "phase2": "scoring-phase2",
    },
    "academic-paper-reviewer/agents/domain_reviewer_agent.md": {
        "ROLE": "domain",
        "PARAPHRASE_LENS": "domain accuracy",
        "REVIEW_BODY_LENS": "domain accuracy",
        "phase2": "scoring-phase2",
    },
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md": {
        "ROLE": "perspective",
        "PARAPHRASE_LENS": "cross-disciplinary relevance",
        "REVIEW_BODY_LENS": "cross-disciplinary perspective",
        "phase2": "scoring-phase2",
    },
    "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md": {
        "ROLE": "da",
        "PARAPHRASE_LENS": "adversarial challenge",
        "phase2": "da-phase2",
    },
}

FRAGMENT_NAMES = ("phase1", "scoring-phase2", "da-phase2", "synth")
MARKER_RE = re.compile(
    r"^<!-- reviewer-sprint-canonical:(?P<name>[a-z0-9-]+):BEGIN -->\n"
    r"(?P<body>.*?)"
    r"^<!-- reviewer-sprint-canonical:(?P=name):END -->$",
    re.MULTILINE | re.DOTALL,
)
SLOT_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
DOUBLE_BRACE_RE = re.compile(r"\{\{|\}\}")

# Re-pin only after reviewing an intentional canonical protocol edit and its
# corresponding inline mirrors. This is the second v3.17-style content lock;
# exact canonical→mirror equality is the first.
CANONICAL_CONTENT_SHA256 = "b2390bdb66749624ad79141024a00ef5699b7afee6ba467e3baa9129daa74f09"


def _parse_fragments(text: str, errors: list[str]) -> dict[str, str]:
    matches = list(MARKER_RE.finditer(text))
    fragments: dict[str, str] = {}
    for match in matches:
        name = match.group("name")
        if name in fragments:
            errors.append(f"canonical fragment {name!r} appears more than once")
            continue
        fragments[name] = match.group("body")
    missing = set(FRAGMENT_NAMES) - set(fragments)
    extra = set(fragments) - set(FRAGMENT_NAMES)
    for name in sorted(missing):
        errors.append(f"canonical fragment missing: {name}")
    for name in sorted(extra):
        errors.append(f"unknown canonical fragment: {name}")
    return fragments


def canonical_digest(
    canonical_text: str,
    fragments: dict[str, str],
    role_config: dict[str, dict[str, str]],
) -> str:
    """Hash every operative source byte, including bounded slot configuration."""
    slot_section = heading_section(canonical_text, SLOT_HEADING) or ""
    payload = (
        b"bounded-slots\0"
        + slot_section.encode("utf-8")
        + b"\0role-config\0"
        + json.dumps(
            role_config,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\0fragments\0"
        + b"".join(
            name.encode("utf-8")
            + b"\0"
            + fragments.get(name, "").encode("utf-8")
            + b"\0"
            for name in FRAGMENT_NAMES
        )
    )
    return hashlib.sha256(payload).hexdigest()


def _expected_slot_table(errors: list[str]) -> tuple[str, ...]:
    rows = [SLOT_TABLE_HEADER, SLOT_TABLE_SEPARATOR]
    for rel, config in ROLE_CONFIG.items():
        phase2_label = PHASE2_TABLE_LABELS.get(config.get("phase2", ""))
        if phase2_label is None:
            errors.append(f"{rel}: unknown Phase 2 slot template {config.get('phase2')!r}")
            phase2_label = "INVALID"
        review_lens = config.get("REVIEW_BODY_LENS")
        review_cell = f"`{review_lens}`" if review_lens is not None else "—"
        rows.append(
            f"| `{Path(rel).name}` | `{config.get('ROLE', '')}` | "
            f"`{config.get('PARAPHRASE_LENS', '')}` | {review_cell} | "
            f"{phase2_label} |"
        )
    return tuple(rows)


def _check_slot_table(canonical_text: str, errors: list[str]) -> None:
    section = heading_section(canonical_text, SLOT_HEADING)
    if section is None:
        errors.append(f"canonical source missing {SLOT_HEADING!r}")
        return
    actual = tuple(line for line in section.splitlines() if line.startswith("|"))
    expected = _expected_slot_table(errors)
    if actual != expected:
        errors.append(
            "canonical bounded role-slot table drift: table must exactly mirror "
            "the rendered role configuration"
        )


def _render(template: str, values: dict[str, str], label: str, errors: list[str]) -> str:
    slots = set(SLOT_RE.findall(template))
    unknown = slots - set(values)
    if unknown:
        errors.append(f"{label}: unresolved canonical slots: {sorted(unknown)}")
    rendered = SLOT_RE.sub(
        lambda match: values.get(match.group(1), match.group(0)), template
    )
    # Termination criterion: double braces are reserved canonical-slot syntax.
    # Once known bounded slots render, any opener or closer left behind is an
    # unresolved or malformed placeholder; do not enumerate typo families.
    if DOUBLE_BRACE_RE.search(rendered):
        errors.append(
            f"{label}: canonical render left an unresolved or malformed "
            "double-brace placeholder"
        )
    return rendered


def _unfenced_exact_heading_count(text: str, heading: str) -> int:
    """Count exact column-zero headings under ``heading_section`` fence rules."""
    fence_re = re.compile(r"[ ]{0,3}(`{3,}|~{3,})")
    fence_close_re = re.compile(r"[ ]{0,3}(`{3,}|~{3,})\s*$")
    fence: str | None = None
    count = 0
    for line in text.splitlines():
        match = fence_re.match(line)
        if fence is not None:
            close = fence_close_re.match(line)
            if (
                close
                and close.group(1)[0] == fence[0]
                and len(close.group(1)) >= len(fence)
            ):
                fence = None
            continue
        if match:
            fence = match.group(1)
            continue
        if line == heading:
            count += 1
    return count


def check(root: Path) -> list[str]:
    errors: list[str] = []
    canonical_text = read_or_exit2(root, CANONICAL_REL)
    sprint_ref = read_or_exit2(root, SPRINT_REF_REL)
    fragments = _parse_fragments(canonical_text, errors)
    _check_slot_table(canonical_text, errors)

    actual_digest = canonical_digest(canonical_text, fragments, ROLE_CONFIG)
    if actual_digest != CANONICAL_CONTENT_SHA256:
        errors.append(
            "canonical content lock mismatch: "
            f"expected {CANONICAL_CONTENT_SHA256}, got {actual_digest}"
        )

    if BACKLINK not in sprint_ref:
        errors.append(
            f"{SPRINT_REF_REL}: canonical prompt-source backlink missing ({BACKLINK})"
        )

    for rel, config in ROLE_CONFIG.items():
        text = read_or_exit2(root, rel)
        if SOURCE_CITATION not in text:
            errors.append(f"{rel}: canonical source citation missing")
        sprint = heading_section(text, SPRINT_HEADING)
        if sprint is None:
            errors.append(f"{rel}: missing {SPRINT_HEADING!r}")
            continue
        phase1 = heading_section(sprint, PHASE1_HEADING)
        phase2 = heading_section(sprint, PHASE2_HEADING)
        expected1 = _render(fragments.get("phase1", ""), config, rel, errors)
        runtime_phase1 = heading_section(text, PHASE1_HEADING)
        runtime_phase2 = heading_section(text, PHASE2_HEADING)
        if runtime_phase1 != expected1:
            errors.append(
                f"{rel}: dispatcher-visible Phase 1 runtime extraction drift"
            )
        if phase1 is None:
            errors.append(f"{rel}: missing delivered Phase 1 section")
        elif phase1 != expected1:
            errors.append(f"{rel}: Phase 1 mirror drift (byte-exact compare failed)")
        phase2_name = config["phase2"]
        expected2 = _render(fragments.get(phase2_name, ""), config, rel, errors)
        if runtime_phase2 != expected2:
            errors.append(
                f"{rel}: dispatcher-visible Phase 2 runtime extraction drift"
            )
        if phase2 is None:
            errors.append(f"{rel}: missing delivered Phase 2 section")
        elif phase2 != expected2:
            label = "DA Phase 2" if phase2_name == "da-phase2" else "Phase 2"
            errors.append(f"{rel}: {label} mirror drift (byte-exact compare failed)")

    synth_text = read_or_exit2(root, SYNTH_REL)
    if SOURCE_CITATION not in synth_text:
        errors.append(f"{SYNTH_REL}: canonical source citation missing")
    expected_synth = _render(fragments.get("synth", ""), {}, SYNTH_REL, errors)
    # Termination criterion for shadow-section hardening: reject duplicate exact,
    # unfenced runtime H2s. Differently worded prose is outside this sync lint's
    # structural invariant; do not grow an open-ended synonym denylist.
    synth_heading_count = _unfenced_exact_heading_count(synth_text, SYNTH_HEADING)
    if synth_heading_count > 1:
        errors.append(
            f"{SYNTH_REL}: synthesizer protocol heading appears more than once"
        )
    synth = heading_section(synth_text, SYNTH_HEADING)
    if synth is None:
        errors.append(f"{SYNTH_REL}: missing {SYNTH_HEADING!r}")
    elif synth != expected_synth:
        errors.append(f"{SYNTH_REL}: synthesizer mirror drift (byte-exact compare failed)")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = check(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("reviewer sprint prompt sync: 5 reviewer pairs + synthesizer exact; canonical lock ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
