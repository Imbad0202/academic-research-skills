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
        "phase2_insert": "methodology-receipt",
        "extraction": "methodology-extraction",
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

FRAGMENT_NAMES = (
    "phase1",
    "scoring-phase2",
    "methodology-receipt",
    "methodology-extraction",
    "da-phase2",
    "synth",
)
# #610 step 5: the methodology seat's free-standing extraction section, a
# third dispatcher-visible H3 mirrored byte-for-byte like Phase 1/Phase 2.
EXTRACTION_HEADING = (
    "### Phase 2E — Numeric extraction (script-adapter dispatch)"
)
# The #610 methodology receipt block is spliced into the shared scoring
# fragment immediately before this terminal-preflight line, so the shared
# scoring text exists once and the composed methodology mirror cannot drift
# from it independently. The anchor is a full canonical line: rewording the
# preflight opener is an intentional protocol edit and must fail here until
# the splice anchor is updated in the same commit.
RECEIPT_SPLICE_ANCHOR = (
    "Terminal Phase 2 structural preflight (mandatory). Silently inspect "
    "the exact text you are about to send against your supplied Phase 1:\n"
)
MARKER_RE = re.compile(
    r"^<!-- reviewer-sprint-canonical:(?P<name>[a-z0-9-]+):BEGIN -->\n"
    r"(?P<body>.*?)"
    r"^<!-- reviewer-sprint-canonical:(?P=name):END -->$",
    re.MULTILINE | re.DOTALL,
)
SLOT_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
DOUBLE_BRACE_RE = re.compile(r"\{\{|\}\}")

# Re-pin only after reviewing an intentional canonical protocol edit and its
# corresponding inline mirrors. The current pin includes the explicit
# confidence-as-uncertainty-only boundary in the DA Phase 2 fragment. This is
# the second v3.17-style content lock; exact canonical→mirror equality is the
# first.
CANONICAL_CONTENT_SHA256 = "231ba4bebb7fb031dc59b82bebd025d577a292258fbc5f570c2624746779e608"


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
    """Hash every operative source byte, including bounded slot configuration.

    The receipt splice anchor is part of the payload (#610 round-1 fix 7):
    the anchor decides WHERE the receipt fragment lands in the composed
    methodology prompt, so rewording it is a content change and must fail
    the lock until re-pinned in the same commit.
    """
    slot_section = heading_section(canonical_text, SLOT_HEADING) or ""
    payload = (
        b"receipt-splice-anchor\0"
        + RECEIPT_SPLICE_ANCHOR.encode("utf-8")
        + b"\0bounded-slots\0"
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
        if config.get("phase2_insert") == "methodology-receipt":
            phase2_label += " + receipts"
        elif "phase2_insert" in config:
            errors.append(
                f"{rel}: unknown Phase 2 insert fragment "
                f"{config.get('phase2_insert')!r}"
            )
        if config.get("extraction") == "methodology-extraction":
            phase2_label += " + extraction"
        elif "extraction" in config:
            errors.append(
                f"{rel}: unknown extraction fragment "
                f"{config.get('extraction')!r}"
            )
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


def _splice(base: str, insert: str, label: str, errors: list[str]) -> str:
    """Compose a Phase 2 template from the shared scoring fragment (#610).

    The insert lands immediately before the terminal-preflight anchor line so
    the receipt grammar precedes the preflight in the delivered prompt. The
    anchor must occur exactly once: zero means the preflight opener was
    reworded without updating this checker; more than once means the fragment
    grew a second preflight and the splice point is ambiguous.
    """
    count = base.count(RECEIPT_SPLICE_ANCHOR)
    if count != 1:
        errors.append(
            f"{label}: receipt splice anchor must occur exactly once in the "
            f"base Phase 2 fragment, found {count}"
        )
        return base
    if not insert.endswith("\n"):
        errors.append(f"{label}: receipt insert fragment must end with a newline")
        return base
    return base.replace(RECEIPT_SPLICE_ANCHOR, insert + RECEIPT_SPLICE_ANCHOR, 1)


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
        template2 = fragments.get(phase2_name, "")
        insert_name = config.get("phase2_insert")
        if insert_name:
            template2 = _splice(
                template2, fragments.get(insert_name, ""), rel, errors
            )
        expected2 = _render(template2, config, rel, errors)
        if runtime_phase2 != expected2:
            errors.append(
                f"{rel}: dispatcher-visible Phase 2 runtime extraction drift"
            )
        if phase2 is None:
            errors.append(f"{rel}: missing delivered Phase 2 section")
        elif phase2 != expected2:
            label = "DA Phase 2" if phase2_name == "da-phase2" else "Phase 2"
            errors.append(f"{rel}: {label} mirror drift (byte-exact compare failed)")
        extraction_name = config.get("extraction")
        if not extraction_name and EXTRACTION_HEADING in text:
            # Defense in depth: the dispatcher and the gate both refuse a
            # non-methodology extraction, but a stray Phase 2E section in
            # another agent file would still be dead prompt text inviting
            # drift.
            errors.append(
                f"{rel}: carries {EXTRACTION_HEADING!r} but declares no "
                "extraction fragment"
            )
        if extraction_name:
            expected_extraction = _render(
                fragments.get(extraction_name, ""), config, rel, errors
            )
            runtime_extraction = heading_section(text, EXTRACTION_HEADING)
            delivered_extraction = heading_section(sprint, EXTRACTION_HEADING)
            if runtime_extraction != expected_extraction:
                errors.append(
                    f"{rel}: dispatcher-visible extraction runtime "
                    "extraction drift"
                )
            if delivered_extraction is None:
                errors.append(f"{rel}: missing delivered extraction section")
            elif delivered_extraction != expected_extraction:
                errors.append(
                    f"{rel}: extraction mirror drift (byte-exact compare "
                    "failed)"
                )

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
