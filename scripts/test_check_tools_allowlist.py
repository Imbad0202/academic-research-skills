#!/usr/bin/env python3
"""Tests for check_tools_allowlist.py (#524).

Mutation discipline: every invariant branch has a passing case (green fixture
tree + the real repo tree) and a failing case proving the check fires when
the guarded property is broken. Two load-bearing families:

  * The SYMMETRIC source+mirror edit re-adding Bash — it passes
    check_agents_mirror_sync.py (byte-equal pair) and the name-keyed runtime
    guard lint, so before #524 it sailed through CI green (the drift the
    issue documents).
  * YAML-form bypasses of the semantic checks — quoted/flow/block/escaped
    spellings that a raw line scan cannot see. These were found by the codex
    xhigh review; the node-tree parse closes them and each has a witness
    here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from check_tools_allowlist import (
    ALLOWLISTED_FILES,
    CANONICAL_TOOLS,
    MANIFEST,
    PINNED_TOOLS_LINE,
    REPO_ROOT,
    check,
)


def make_tree(tmp_path: Path) -> Path:
    """A green fixture tree: six allowlisted files carrying the pinned line,
    a minimal Bucket A manifest, a fenced no-tools agent, and an unfenced
    Bash-holding agent."""
    for rel in ALLOWLISTED_FILES:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\nname: {p.stem}\ndescription: \"x\"\nmodel: inherit\n"
            f"{PINNED_TOOLS_LINE}\n---\n\nbody\n",
            encoding="utf-8",
        )
    manifest = tmp_path / MANIFEST
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"agents": {
        "report_compiler_agent": {},
        "research_architect_agent": {},
        "synthesis_agent": {},
        "eic_agent": {},
    }}), encoding="utf-8")
    # A Bucket A agent with NO tools key (inherit) — must pass untouched.
    eic = tmp_path / "academic-paper-reviewer/agents/eic_agent.md"
    eic.parent.mkdir(parents=True, exist_ok=True)
    eic.write_text("---\nname: eic_agent\n---\n\nbody\n", encoding="utf-8")
    # A NON-Bucket-A agent advertising Bash — allowed (invariant 2 is
    # scoped to fenced agents; the orchestrator legitimately holds shell).
    orch = tmp_path / "academic-pipeline/agents/pipeline_orchestrator_agent.md"
    orch.parent.mkdir(parents=True, exist_ok=True)
    orch.write_text(
        "---\nname: pipeline_orchestrator_agent\ntools: Read, Bash\n---\n\nbody\n",
        encoding="utf-8",
    )
    return tmp_path


def first_pair() -> tuple[str, str]:
    """One (source, mirror) pair for symmetric-edit mutations."""
    return ("deep-research/agents/research_architect_agent.md",
            "agents/research_architect_agent.md")


def rewrite_tools_line(path: Path, new_line: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(PINNED_TOOLS_LINE, new_line),
                    encoding="utf-8")


def errs_for(tmp_path: Path, rel: str) -> list[str]:
    return [e for e in check(tmp_path) if rel in e]


# --- invariant 0: the real tree is green --------------------------------------

def test_real_repo_passes():
    assert check(REPO_ROOT) == []


# --- green fixture -------------------------------------------------------------

def test_green_tree_passes(tmp_path):
    make_tree(tmp_path)
    assert check(tmp_path) == []


# --- invariant 1: exact value + semantic parse ---------------------------------

def test_symmetric_bash_readd_fails_on_both_files(tmp_path):
    # THE #524 drift scenario: source+mirror edited together to re-add Bash.
    # Mirror-sync stays green (byte-equal pair); this lint must fire on BOTH,
    # via the semantic value check AND the byte-exact witness.
    make_tree(tmp_path)
    src, mirror = first_pair()
    for rel in (src, mirror):
        rewrite_tools_line(tmp_path / rel, PINNED_TOOLS_LINE + ", Bash")
    assert any("diverges from the canonical" in e for e in errs_for(tmp_path, src))
    assert any("diverges from the canonical" in e for e in errs_for(tmp_path, mirror))


def test_dropped_tool_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    rewrite_tools_line(tmp_path / src, "tools: Read, Write, Edit, Glob")
    assert any("diverges from the canonical" in e for e in errs_for(tmp_path, src))


def test_typoed_tool_name_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    rewrite_tools_line(tmp_path / src, "tools: Read, Write, Edit, Gerp, Glob")
    assert any("diverges from the canonical" in e for e in errs_for(tmp_path, src))


def test_trailing_whitespace_is_byte_drift(tmp_path):
    # A trailing space keeps the semantic value intact but breaks the
    # byte-exact witness — the exact-form pin must still fire.
    make_tree(tmp_path)
    src, _ = first_pair()
    rewrite_tools_line(tmp_path / src, PINNED_TOOLS_LINE + " ")
    assert any("not byte-equal" in e for e in errs_for(tmp_path, src))


def test_crlf_conversion_is_byte_drift(tmp_path):
    # A symmetric LF->CRLF conversion leaves YAML semantics intact, so only
    # the CR-sensitive byte witness catches it (codex round-1 P2).
    make_tree(tmp_path)
    src, mirror = first_pair()
    for rel in (src, mirror):
        p = tmp_path / rel
        p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    assert any("not byte-equal" in e for e in errs_for(tmp_path, src))
    assert any("not byte-equal" in e for e in errs_for(tmp_path, mirror))


def test_missing_tools_key_fails_as_widening(tmp_path):
    # Dropping the key silently widens capability (agent inherits ALL tools).
    make_tree(tmp_path)
    src, _ = first_pair()
    p = tmp_path / src
    p.write_text(p.read_text(encoding="utf-8").replace(
        PINNED_TOOLS_LINE + "\n", ""), encoding="utf-8")
    assert any("no `tools:` key" in e for e in errs_for(tmp_path, src))


def test_escaped_duplicate_key_fails(tmp_path):
    # The sharpest round-2 bypass: keep the pinned bare line AND add a
    # `s`-escaped `"tools":` duplicate. safe_load collapses the two
    # to the last-wins canonical value; the duplicate-preserving node tree
    # sees TWO `tools` keys and fires.
    make_tree(tmp_path)
    src, _ = first_pair()
    rewrite_tools_line(
        tmp_path / src,
        '"tool\\u0073": Read, Write, Edit, Grep, Glob, Bash\n'
        + PINNED_TOOLS_LINE,
    )
    assert any("2 `tools` keys" in e for e in errs_for(tmp_path, src))


def test_quoted_duplicate_key_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    rewrite_tools_line(tmp_path / src,
                       f'{PINNED_TOOLS_LINE}\n"tools": Read, Bash')
    assert any("2 `tools` keys" in e for e in errs_for(tmp_path, src))


def test_missing_allowlisted_file_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    (tmp_path / src).unlink()
    assert any("missing" in e for e in errs_for(tmp_path, src))


def test_no_frontmatter_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    (tmp_path / src).write_text("body only\n", encoding="utf-8")
    assert any("no YAML frontmatter" in e for e in errs_for(tmp_path, src))


def test_uncomposable_frontmatter_fails_closed(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    p = tmp_path / src
    p.write_text(p.read_text(encoding="utf-8").replace(
        PINNED_TOOLS_LINE, "tools: [unclosed"), encoding="utf-8")
    assert any("does not compose" in e for e in errs_for(tmp_path, src))


def test_body_tools_line_does_not_satisfy_pin(tmp_path):
    # The pinned line must live in FRONTMATTER; a body mention is not a grant.
    make_tree(tmp_path)
    src, _ = first_pair()
    p = tmp_path / src
    p.write_text(p.read_text(encoding="utf-8").replace(
        PINNED_TOOLS_LINE + "\n", "") + f"\n{PINNED_TOOLS_LINE}\n",
        encoding="utf-8")
    assert any("no `tools:` key" in e for e in errs_for(tmp_path, src))


# --- invariant 2: Bucket A frontmatter must not declare Bash --------------------

def bash_fixture(tmp_path, frontmatter_body: str) -> list[str]:
    """Write a Bucket A agent with the given frontmatter body and return the
    errors mentioning it."""
    eic = tmp_path / "academic-paper-reviewer/agents/eic_agent.md"
    eic.write_text(f"---\n{frontmatter_body}\n---\n\nbody\n",
                   encoding="utf-8")
    return [e for e in check(tmp_path) if "eic_agent" in e]


def test_bucket_a_agent_advertising_bash_fails(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, Bash")
    assert any("declares Bash" in e for e in errs)


def test_quoted_string_value_bash_fails(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, 'name: eic_agent\ntools: "Read, Bash"')
    assert any("declares Bash" in e for e in errs)


def test_quoted_name_with_bash_fails(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, 'name: "eic_agent"\ntools: Read, Bash')
    assert any("declares Bash" in e for e in errs)


def test_flow_list_bash_fails(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: [Read, Bash]")
    assert any("declares Bash" in e for e in errs)


def test_block_list_bash_fails(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path,
                        "name: eic_agent\ntools:\n  - Read\n  - Bash")
    assert any("declares Bash" in e for e in errs)


def test_inline_comment_bash_fails(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path,
                        "name: eic_agent\ntools: Read, Bash # reviewed")
    assert any("declares Bash" in e for e in errs)


def test_permission_specifier_bash_fails(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, Bash(git:*)")
    assert any("declares Bash" in e for e in errs)


def test_bashoutput_is_a_different_tool_and_passes(tmp_path):
    # Exact base-name match: BashOutput grants no shell; a prefix match
    # would false-fire on it.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, BashOutput")
    assert errs == []


def test_lowercase_bash_is_a_different_tool_and_passes(tmp_path):
    # Tool names are exact: `bash` (lowercase) is not the shell-granting
    # `Bash` tool. Case-folding would false-fire on a legitimate value.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, bash")
    assert errs == []


def test_bom_padded_bash_fails(tmp_path):
    # #524 r9: a BOM (U+FEFF) is NOT stripped by str.strip(), so `﻿Bash`
    # would survive as a token != `Bash` and slip the membership test.
    # _fold drops Cf format chars so it collapses back to Bash.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, ﻿Bash﻿")
    assert any("declares Bash" in e for e in errs)


def test_zero_width_space_padded_bash_fails(tmp_path):
    # #524 r9: zero-width space (U+200B) — a Cf format char str.strip() leaves.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, ​Bash​")
    assert any("declares Bash" in e for e in errs)


def test_zero_width_non_joiner_padded_bash_fails(tmp_path):
    # #524 r9: zero-width non-joiner (U+200C) — another Cf format char.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, ‌Bash‌")
    assert any("declares Bash" in e for e in errs)


def test_fullwidth_bash_fails(tmp_path):
    # #524 r9: fullwidth "Ｂａｓｈ" (U+FF22 etc.) is a compatibility homoglyph;
    # NFKC in _fold folds it onto ASCII "Bash".
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, Ｂａｓｈ")
    assert any("declares Bash" in e for e in errs)


def test_fullwidth_paren_permission_specifier_bash_fails(tmp_path):
    # #524 r10: fullwidth parens U+FF08/U+FF09 in a permission specifier. The
    # ASCII "(" split misses them, so folding must happen BEFORE the split —
    # otherwise NFKC leaves the whole "Bash（git:*）" as one token != "Bash".
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, Bash（git:*）")
    assert any("declares Bash" in e for e in errs)


def test_fullwidth_bash_and_paren_specifier_fails(tmp_path):
    # #524 r10: both the tool name AND its parens fullwidth — the whole thing
    # must fold to ASCII "Bash" and be caught.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, Ｂａｓｈ（git:*）")
    assert any("declares Bash" in e for e in errs)


def test_fullwidth_comma_separated_bash_fails(tmp_path):
    # #524 r11: fullwidth comma U+FF0C. split(",") misses it, so "Read，Bash"
    # stays one token — folding must happen on the WHOLE value BEFORE the comma
    # split (the r11 corollary of r10), or "Read，Bash" folds to "Read,Bash"
    # (one token != "Bash") and slips.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read，Bash")
    assert any("declares Bash" in e for e in errs)


def test_small_comma_separated_bash_fails(tmp_path):
    # #524 r11: small comma U+FE50 — another compatibility comma NFKC folds to
    # ASCII "," only if the fold precedes the split.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read﹐Bash")
    assert any("declares Bash" in e for e in errs)


def test_fullwidth_comma_and_name_and_paren_bash_fails(tmp_path):
    # #524 r11: fullwidth comma + fullwidth name + fullwidth parens all at once
    # — the whole-value fold must reduce it to Read + Bash.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read，Ｂａｓｈ（git:*）")
    assert any("declares Bash" in e for e in errs)


def test_nfkc_stable_alt_separator_is_not_a_bash_grant(tmp_path):
    # #524 r12 (convergence boundary, documented as a NON-bug): an alternate
    # separator that NFKC does NOT fold to ASCII "," — e.g. an ideographic comma
    # U+3001, an Arabic comma U+060C, or a semicolon — keeps "Read、Bash" as ONE
    # token for EVERYONE: the string is a single YAML scalar, this lint splits
    # only on ASCII "," (and any NFKC-normalizing consumer would too), so no
    # consumer extracts a bare "Bash" from it and no shell is granted. The
    # fullwidth comma/paren cases fail (above) precisely because NFKC DOES fold
    # them into the ASCII separators the split honors; these do not. Not
    # flagging this is correct — flagging it would be a false positive a future
    # maintainer might "fix" by over-broadening the separator set.
    make_tree(tmp_path)
    assert bash_fixture(tmp_path, "name: eic_agent\ntools: Read、Bash") == []
    assert bash_fixture(tmp_path, "name: eic_agent\ntools: Read؍Bash") == []
    assert bash_fixture(tmp_path, "name: eic_agent\ntools: Read;Bash") == []


def test_bom_canonical_allowlist_value_still_fires_byte_witness(tmp_path):
    # #524 r9 companion: folding the SEMANTIC check must not weaken invariant 1.
    # A plugin agent whose tools value is BOM-padded canonical now folds to the
    # five canonical tools semantically — but the additive byte-witness must
    # STILL fire (the raw line is not byte-equal to PINNED_TOOLS_LINE).
    make_tree(tmp_path)
    target = tmp_path / sorted(ALLOWLISTED_FILES)[0]
    target.write_text(
        "---\nname: report_compiler_agent\n"
        "tools: ﻿Read﻿, Write, Edit, Grep, Glob\n---\n\nbody\n",
        encoding="utf-8")
    errs = [e for e in check(tmp_path) if "byte-equal" in e]
    assert errs, "byte-witness must still fire on an invisible-char canonical value"


def test_repeated_identical_scalars_are_not_aliases(tmp_path):
    # False-positive guard for the alias-by-shared-identity detector:
    # `yaml.compose` does NOT intern identical scalar values (each gets a
    # distinct node), so a clean file repeating a value must still pass.
    make_tree(tmp_path)
    errs = bash_fixture(
        tmp_path,
        "name: eic_agent\ntools: Read, Read, Grep\ndescription: Read Read")
    assert errs == []


def test_non_string_manifest_agent_key_still_reconciles(tmp_path):
    # A manifest whose `agents` mapping carries a non-string key alongside
    # the real ones must not break reconciliation of the real Bucket A agent.
    make_tree(tmp_path)
    (tmp_path / MANIFEST).write_text(
        '{"agents": {"123": {}, "report_compiler_agent": {}, '
        '"research_architect_agent": {}, "synthesis_agent": {}, '
        '"eic_agent": {}}}', encoding="utf-8")
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Read, Bash")
    assert any("declares Bash" in e for e in errs)


def test_nested_list_member_fails_closed(tmp_path):
    # A non-scalar list member is an unrecognized shape — must not be
    # silently stringified into a passing value (codex round-2 P2).
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: [Read, [Bash]]")
    assert any("unrecognized shape" in e for e in errs)


def test_mapping_list_member_fails_closed(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: [Read, {Bash: 1}]")
    assert any("unrecognized shape" in e for e in errs)


def test_mapping_tools_value_fails_closed(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: {Read: yes}")
    assert any("unrecognized shape" in e for e in errs)


def test_typed_scalar_tools_on_bucket_a_fails_closed(tmp_path):
    # A Bucket A `tools` that is an int/bool/null/timestamp scalar is an
    # unrecognized shape — the reconciliation cannot confirm it excludes
    # Bash, so it fails closed (scoped to Bucket A; out-of-scope agents with
    # a nonsense tools value are not this lint's concern).
    make_tree(tmp_path)
    for val in ("5", "true", "null", "2020-01-01"):
        errs = bash_fixture(tmp_path, f"name: eic_agent\ntools: {val}")
        assert any("unrecognized shape" in e for e in errs), val


def test_bare_bash_scalar_fails_closed(tmp_path):
    # Bash as the whole scalar value (not a list member) still resolves to
    # the `Bash` base name.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, "name: eic_agent\ntools: Bash")
    assert any("declares Bash" in e for e in errs)


def test_merge_nested_in_sequence_fails_closed(tmp_path):
    # The merge/alias walk must recurse into sequence values, not only
    # mapping values — a `<<`/alias buried in a list still fails closed.
    make_tree(tmp_path)
    errs = bash_fixture(
        tmp_path,
        "name: eic_agent\n_a: &a {tools: [Read, Bash]}\nx: [<<, *a]")
    assert any("merge key / alias" in e for e in errs)


def test_merge_tagged_complex_key_fails_closed(tmp_path):
    # codex round-5 P1: the merge tag can land on a non-scalar KEY
    # (`? !!merge [x]` is a merge-tagged sequence key). safe_load applies
    # merge semantics and injects `tools: [Read, Bash]`; the tag check must
    # fire on any node type, not just scalars.
    make_tree(tmp_path)
    for key in ("!!merge [x]", "!!merge {a: 1}"):
        errs = bash_fixture(
            tmp_path,
            f"name: eic_agent\n? {key}\n: {{tools: [Read, Bash]}}")
        assert any("merge key / alias" in e for e in errs), key


def test_deeply_nested_frontmatter_does_not_crash(tmp_path):
    # codex round-5 P2: a pathologically deep flow sequence must never crash
    # the lint with an unhandled traceback — check() must RETURN. Whether a
    # given depth trips RecursionError is Python-version-dependent (3.14
    # tolerates far deeper nesting than 3.11), so the version-independent
    # contract is "returns, does not raise", not "fails at depth N". A
    # depth that does NOT recurse past the limit is a harmless (if odd) file
    # and legitimately passes; the fail-closed path is exercised
    # deterministically by test_recursion_error_fails_closed below.
    make_tree(tmp_path)
    deep = "name: eic_agent\ntools: Read, Grep\nx: " + "[" * 400 + "]" * 400
    errs = bash_fixture(tmp_path, deep)  # must not raise
    assert isinstance(errs, list)


def test_compose_recursion_error_maps_to_none():
    # _mapping_node must turn a RecursionError from yaml.compose into None
    # (→ the caller emits a fail-closed "does not compose" error), not let it
    # escape. Driven by monkeypatching compose to raise, so it is
    # deterministic and Python-version-independent (unlike relying on a
    # specific nesting depth tripping the interpreter's own limit).
    import check_tools_allowlist as m

    def boom(*a, **k):
        raise RecursionError("maximum recursion depth exceeded")

    orig = m.yaml.compose
    m.yaml.compose = boom
    try:
        assert m._mapping_node("name: x\n") is None
    finally:
        m.yaml.compose = orig


def test_walk_recursion_error_fails_closed():
    # _uses_merge_or_alias must treat a RecursionError in the walk as True
    # (fail closed — the tree could not be proven clean). Forced
    # deterministically: a MappingNode whose `.value` is an iterable that
    # raises RecursionError on iteration (standing in for a walk that
    # recurses past the interpreter limit), so the test does not depend on
    # any Python-version recursion depth.
    import check_tools_allowlist as m
    import yaml as y

    class ExplodingValue:
        def __iter__(self):
            raise RecursionError("maximum recursion depth exceeded")

    node = y.MappingNode("tag:yaml.org,2002:map", [])
    node.value = ExplodingValue()
    assert m._uses_merge_or_alias(node) is True


def test_uncomposable_bucket_a_frontmatter_fails_closed(tmp_path):
    # Frontmatter that won't compose can't be cleared by name — fail closed
    # (codex round-2 P2: a quoted/indented name under malformed YAML must
    # not be silently skipped).
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path, 'name: "eic_agent"\ndescription: [unclosed')
    assert any("does not compose" in e for e in errs)


def test_merge_key_injecting_bash_fails_closed(tmp_path):
    # codex round-3: `<<: *base` merges a `tools: [..., Bash]` the
    # duplicate-preserving node scan never sees (the top level only shows a
    # literal `<<` key). The composed node tree carries the `merge` tag —
    # detected there, not by text, and failed closed.
    make_tree(tmp_path)
    errs = bash_fixture(
        tmp_path,
        "_base: &b {tools: [Read, Bash]}\n<<: *b\nname: eic_agent")
    assert any("merge key / alias" in e for e in errs)


def test_flow_merge_with_quoted_hash_key_fails_closed(tmp_path):
    # codex round-3 P1-2: a `#` inside a quoted flow key fooled the old
    # text-scan comment strip; the node-tree merge-tag detector is immune.
    make_tree(tmp_path)
    eic = tmp_path / "academic-paper-reviewer/agents/eic_agent.md"
    eic.write_text(
        '---\n{ "x#": y, name: eic_agent, <<: &b {tools: "Read, Bash"} }\n'
        "---\n\nbody\n", encoding="utf-8")
    assert any("merge key / alias" in e
               for e in check(tmp_path) if "eic_agent" in e)


def test_alias_value_bash_fails_closed(tmp_path):
    # An alias makes `tools` share another node's value — the node tree sees
    # the SAME node object twice (shared identity). Fail closed.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path,
                        "name: eic_agent\n_x: &a [Read, Bash]\ntools: *a")
    assert any("merge key / alias" in e for e in errs)


def test_ampersand_in_quoted_value_is_not_an_anchor(tmp_path):
    # False-positive guard: a literal `&`/`*` inside a quoted scalar is not a
    # YAML anchor/alias (the node carries a plain str value) and must NOT
    # fail the clean file — the node-tree detector, unlike a text scan, sees
    # this correctly.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path,
                        'name: eic_agent\ndescription: "A & B, 3 * 4"\n'
                        "tools: Read, Grep")
    assert errs == []


def test_allowlisted_file_with_alias_fails_closed(tmp_path):
    # Invariant 1 also fails closed on aliases (a `<<`/alias could inject the
    # pinned value from elsewhere, defeating the value lock).
    make_tree(tmp_path)
    src, _ = first_pair()
    p = tmp_path / src
    p.write_text(
        "---\nname: research_architect_agent\n_t: &t Read, Write, Edit, "
        "Grep, Glob\ntools: *t\n---\n\nbody\n", encoding="utf-8")
    assert any("merge key / alias" in e for e in errs_for(tmp_path, src))


def test_indented_fence_in_block_scalar_does_not_truncate(tmp_path):
    # codex round-3 P1-1: an indented `---` inside a `description: |` block
    # scalar must NOT be read as the closing fence — doing so truncated the
    # block and hid a Bucket A `name` + `tools: Read, Bash` below it. Only a
    # column-0 `---` closes frontmatter.
    make_tree(tmp_path)
    eic = tmp_path / "academic-paper-reviewer/agents/eic_agent.md"
    eic.write_text(
        "---\ndescription: |\n  ---\nname: eic_agent\ntools: Read, Bash\n"
        "---\n\nbody\n", encoding="utf-8")
    assert any("declares Bash" in e
               for e in check(tmp_path) if "eic_agent" in e)


def test_bom_prefixed_bucket_a_bash_fails_closed(tmp_path):
    # A leading UTF-8 BOM makes `﻿---` fail the column-0 fence match, so
    # the file would read as frontmatter-less and skip invariant 2 — while a
    # real YAML reader strips the BOM and sees `tools: Read, Bash`. _read_raw
    # strips the BOM so the two agree; the smuggled Bash fails closed.
    make_tree(tmp_path)
    eic = tmp_path / "academic-paper-reviewer/agents/eic_agent.md"
    eic.write_bytes(
        "﻿---\nname: eic_agent\ntools: Read, Bash\n---\n\nbody\n"
        .encode("utf-8"))
    assert any("declares Bash" in e
               for e in check(tmp_path) if "eic_agent" in e)


def test_bom_prefixed_clean_file_passes(tmp_path):
    make_tree(tmp_path)
    eic = tmp_path / "academic-paper-reviewer/agents/eic_agent.md"
    eic.write_bytes(
        "﻿---\nname: eic_agent\ntools: Read, Grep\n---\n\nbody\n"
        .encode("utf-8"))
    assert not [e for e in check(tmp_path) if "eic_agent" in e]


def test_block_scalar_containing_tools_text_no_false_positive(tmp_path):
    # codex round-6 P2: a `description: |` block scalar whose body contains a
    # `tools: ...` line must NOT trip the byte-witness — that line is not the
    # `tools` KEY. The witness is anchored to the composed key's own line, so
    # a clean allowlisted file with such documentation passes.
    make_tree(tmp_path)
    src, _ = first_pair()
    p = tmp_path / src
    p.write_text(
        f"---\nname: research_architect_agent\n{PINNED_TOOLS_LINE}\n"
        "description: |\n  tools: this is documentation, not the key\n"
        "---\n\nbody\n", encoding="utf-8")
    assert errs_for(tmp_path, src) == []


def test_block_scalar_containing_triple_dash_is_not_a_fence(tmp_path):
    # The companion false-positive: a block scalar that legitimately contains
    # an indented `---` line must still parse the real keys below it and PASS
    # a clean file.
    make_tree(tmp_path)
    errs = bash_fixture(
        tmp_path,
        "name: eic_agent\ndescription: |\n  intro\n  --- not a fence\n"
        "tools: Read, Grep")
    assert errs == []


def test_escaped_tools_key_fires_byte_witness_on_allowlisted(tmp_path):
    # codex round-3 P2-1: replacing the pinned line with an escaped-key
    # spelling makes raw_lines empty; the byte witness must still fire
    # (require the verbatim pinned line), and the semantic check fires too.
    make_tree(tmp_path)
    src, _ = first_pair()
    p = tmp_path / src
    p.write_text(
        '---\nname: research_architect_agent\n"tool\\u0073": Read, Write, '
        "Edit, Grep, Glob\n---\n\nbody\n", encoding="utf-8")
    assert any("not byte-equal" in e for e in errs_for(tmp_path, src))


def test_duplicate_tools_on_bucket_a_fails_closed(tmp_path):
    # codex round-4 P2: last-wins would pick `Read, Grep` and pass, but a
    # first-wins parser would grant Bash. Duplicate-key resolution is
    # parser-dependent, so invariant 2 fails closed (as invariant 1 does).
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path,
                        "name: eic_agent\ntools: Read, Bash\ntools: Read, Grep")
    assert any("`tools` keys" in e and "parser-dependent" in e for e in errs)


def test_duplicate_tools_first_wins_bash_fails_closed(tmp_path):
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path,
                        "name: eic_agent\ntools: Read, Grep\ntools: Read, Bash")
    assert any("`tools` keys" in e and "parser-dependent" in e for e in errs)


def test_duplicate_name_one_bucket_a_fails_closed(tmp_path):
    # A duplicate `name` where one resolution is Bucket A: a non-Bucket-A
    # last-wins name would skip the file, hiding a Bucket A first-wins name +
    # Bash. Fail closed.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path,
                        "name: safe_agent\nname: eic_agent\ntools: Read, Bash")
    assert any("`name` keys" in e and "parser-dependent" in e for e in errs)


def test_duplicate_name_neither_bucket_a_passes(tmp_path):
    # If NO resolution is a Bucket A name, the file is out of scope whichever
    # way a parser resolves it — no need to fail closed.
    make_tree(tmp_path)
    errs = bash_fixture(tmp_path,
                        "name: safe_one\nname: safe_two\ntools: Read, Bash")
    assert errs == []


def test_nested_bucket_a_agent_declaring_bash_fails_closed(tmp_path):
    # codex round-7 P1: invariant 2 must reach nested agent files (rglob, not
    # glob) — the runtime guard keys on `name` regardless of path, so a
    # `agents/subdir/x.md` with a Bucket A name + Bash is a real exposure.
    make_tree(tmp_path)
    nested = (tmp_path
              / "academic-paper-reviewer/agents/subdir/eic_agent.md")
    nested.parent.mkdir(parents=True, exist_ok=True)
    nested.write_text("---\nname: eic_agent\ntools: Read, Bash\n---\nbody\n",
                      encoding="utf-8")
    assert any("declares Bash" in e for e in check(tmp_path)
               if "eic_agent" in e)


def test_directory_symlink_under_agent_dir_fails_closed(tmp_path):
    # codex round-8 P1: rglob does not descend into directory symlinks, so a
    # tracked `agents/nested -> ../payload` could hide a Bucket A agent
    # declaring Bash. Fail closed on the symlink itself.
    make_tree(tmp_path)
    agents = tmp_path / "academic-paper-reviewer/agents"
    agents.mkdir(parents=True, exist_ok=True)
    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "eic_agent.md").write_text(
        "---\nname: eic_agent\ntools: Read, Bash\n---\nbody\n",
        encoding="utf-8")
    try:
        (agents / "nested").symlink_to(payload, target_is_directory=True)
    except (OSError, NotImplementedError):
        import pytest
        pytest.skip("symlinks unavailable on this platform")
    assert any("directory symlink" in e for e in check(tmp_path))


def test_bare_cr_frontmatter_bucket_a_bash_fails_closed(tmp_path):
    # codex round-8 P1: bare `\r` (old-Mac) is a YAML line break, but a
    # split-on-`\n` fence scan reads the file as frontmatter-less and skips
    # it, hiding a Bucket A `tools: Bash`. splitlines() recognizes bare CR so
    # the declaration is caught.
    make_tree(tmp_path)
    eic = tmp_path / "academic-paper-reviewer/agents/eic_agent.md"
    eic.write_bytes(
        "---\rname: eic_agent\rtools: Read, Bash\r---\r".encode("utf-8"))
    assert any("declares Bash" in e for e in check(tmp_path)
               if "eic_agent" in e)


def test_unicode_line_break_before_tools_no_false_positive(tmp_path):
    # codex round-7 P2: YAML counts NEL (U+0085) / LS (U+2028) / PS (U+2029)
    # as line breaks but str.split("\n") does not. Placed in a quoted value
    # BEFORE the tools key, they shift YAML's start_mark.line off the
    # split("\n") index, so a line-based anchor would read the WRONG physical
    # line. The byte witness anchors via start_mark.index (byte offset), so
    # the clean allowlisted file is not falsely rejected and no non-verbatim
    # key line slips past.
    make_tree(tmp_path)
    src, _ = first_pair()
    p = tmp_path / src
    p.write_text(
        f"---\nname: research_architect_agent\n"
        'description: "ab c d"\n'
        f"{PINNED_TOOLS_LINE}\n---\n\nbody\n",
        encoding="utf-8")
    assert errs_for(tmp_path, src) == []



def test_non_bucket_a_agent_with_bash_passes(tmp_path):
    # Baked into the green fixture (pipeline_orchestrator_agent declares
    # Bash); assert it raises nothing on its own.
    make_tree(tmp_path)
    assert check(tmp_path) == []


def test_bucket_a_agent_without_tools_key_passes(tmp_path):
    # eic_agent in the green fixture has no tools key — inherit is fine;
    # the runtime guard still fences it.
    make_tree(tmp_path)
    assert not [e for e in check(tmp_path) if "eic_agent" in e]


def test_missing_manifest_fails_closed(tmp_path):
    make_tree(tmp_path)
    (tmp_path / MANIFEST).unlink()
    errs = check(tmp_path)
    assert any(MANIFEST in e and "failing closed" in e for e in errs)


def test_unparseable_manifest_fails_closed(tmp_path):
    make_tree(tmp_path)
    (tmp_path / MANIFEST).write_text("{not json", encoding="utf-8")
    errs = check(tmp_path)
    assert any(MANIFEST in e and "failing closed" in e for e in errs)


def test_valid_json_non_object_manifest_fails_closed(tmp_path):
    # A JSON array parses fine but has no `agents` mapping — must be a
    # curated diagnostic, not a traceback (codex round-1 P2).
    make_tree(tmp_path)
    (tmp_path / MANIFEST).write_text("[]", encoding="utf-8")
    errs = check(tmp_path)
    assert any(MANIFEST in e and "no `agents` mapping" in e for e in errs)


def test_non_mapping_agents_value_fails_closed(tmp_path):
    make_tree(tmp_path)
    (tmp_path / MANIFEST).write_text('{"agents": []}', encoding="utf-8")
    errs = check(tmp_path)
    assert any(MANIFEST in e and "no `agents` mapping" in e for e in errs)


# --- lock shape ------------------------------------------------------------------

def test_pinned_line_is_the_frozen_514_value():
    # Editing the allowlist is a deliberate security-surface change: it must
    # touch this lint in the same commit. This test is the second witness.
    assert PINNED_TOOLS_LINE == "tools: Read, Write, Edit, Grep, Glob"
    assert CANONICAL_TOOLS == ("Read", "Write", "Edit", "Grep", "Glob")


def test_allowlisted_files_are_the_three_pairs():
    assert set(ALLOWLISTED_FILES) == {
        "deep-research/agents/report_compiler_agent.md",
        "deep-research/agents/research_architect_agent.md",
        "deep-research/agents/synthesis_agent.md",
        "agents/report_compiler_agent.md",
        "agents/research_architect_agent.md",
        "agents/synthesis_agent.md",
    }
