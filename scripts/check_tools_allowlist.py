#!/usr/bin/env python3
"""Lint: pin the #514 tools-allowlist CONTENT on the three plugin agents (#524).

#521 shipped `tools: Read, Write, Edit, Grep, Glob` on the three top-level
plugin agents (deep-research sources + agents/ mirrors), but no lint read a
frontmatter `tools` key: check_agents_mirror_sync.py pins mirror==source
byte-equality (the PAIR, never the VALUE), and the runtime write-scope guard
(scripts/ars_write_scope_guard.py) keys on agent NAME, never frontmatter. A
future PR editing a source+mirror pair symmetrically back to `..., Bash` (or
dropping `Grep`, or typoing a tool name) would pass every CI gate green —
exactly the drift class the repo's defrift locks exist to catch (cf. the
v3.15 locks). This lint pins the VALUE.

Design: YAML is the authority, not a line scan. Claude Code defines these
files as YAML frontmatter, and a raw-line/regex scan can never see every
YAML-legal spelling of a key or value (quoted, tagged, aliased, escaped,
`\\u0073`-escaped, tab-indented, flow/block list, `Bash(...)` specifier). So
every semantic decision is read from a DUPLICATE-PRESERVING YAML node tree
(`yaml.compose`, which — unlike `safe_load` — keeps a shadowed duplicate key
visible AND resolves an alias into shared node identity). Any frontmatter
that will not compose to a mapping, OR uses a merge key (`<<`) / alias
(constructs that inject or share keys the literal-key scan cannot see), is a
fail-closed ERROR, never a skip. The frontmatter fence is a COLUMN-0 `---`
only, so an indented `---` inside a block scalar cannot truncate the block
and hide keys below it. The exact PINNED_TOOLS_LINE raw-line check is kept
ON TOP as an additive, stricter witness (it also pins byte-level form:
CR-sensitive, so a symmetric LF→CRLF conversion is drift; and it fires when
the verbatim pinned line is absent), but it can only ADD findings, never
subtract them — the semantic node-tree check stands alone as the security
floor.

Invariants:
  1. Every file in ALLOWLISTED_FILES exists, its frontmatter composes to a
     YAML mapping with EXACTLY ONE `tools` key (counted from the
     duplicate-preserving node tree, so a shadowed `"tools":` / `"tool\\u0073":`
     duplicate is caught), and that key's value normalizes to exactly the
     canonical five tools. On top, the single raw `tools:` frontmatter line
     must be byte-equal to PINNED_TOOLS_LINE. Changing the allowlist is a
     deliberate security-surface change: edit the agent files AND this
     lint's PINNED_TOOLS_LINE in the same commit (standard lock semantics).
  2. Frontmatter/guard reconciliation: any agent file under AGENT_DIRS whose
     frontmatter `name` is a Bucket A key in
     scripts/ars_phase_scope_manifest.json must NOT declare Bash in a
     `tools:` key — in ANY YAML-legal form. `Bash` is matched as an exact
     base tool name (`BashOutput` is a different tool and is not flagged;
     `Bash(git:*)` normalizes to `Bash` and IS). The runtime guard denies
     Bucket A agents ALL Bash (zero fail-open); a frontmatter advertising
     Bash would silently widen capability in hook-less installs while
     contradicting the guard in hook-active ones. Agents with no `tools:`
     key inherit and are untouched (the runtime guard still fences them).
     Fail-closed: an agent file whose frontmatter will not compose to a
     mapping is treated as a POSSIBLE Bucket A member and errors (we cannot
     read its `name` to clear it), and a Bucket A agent whose `tools` value
     has an unrecognized shape (non-string list member, mapping) errors.

The manifest is load-bearing for invariant 2, so a missing, unparseable, or
non-mapping manifest FAILS the lint (fail-closed) rather than skipping.
"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# The exact frontmatter line shipped by #521 (frozen #514 spec). Single
# source of truth for the VALUE — a symmetric source+mirror edit cannot
# change it without touching this lint in the same commit.
PINNED_TOOLS_LINE = "tools: Read, Write, Edit, Grep, Glob"
CANONICAL_TOOLS = ("Read", "Write", "Edit", "Grep", "Glob")

# The six #514 surfaces: three canonical sources + three agents/ mirrors
# (mirror==source byte-equality is check_agents_mirror_sync.py's job; the
# mirrors are still listed here so THIS lint stays correct even if that one
# is skipped or edited — deliberately re-derived, not imported, per the
# repo's independent-second-witness lint convention).
ALLOWLISTED_FILES = (
    "deep-research/agents/report_compiler_agent.md",
    "deep-research/agents/research_architect_agent.md",
    "deep-research/agents/synthesis_agent.md",
    "agents/report_compiler_agent.md",
    "agents/research_architect_agent.md",
    "agents/synthesis_agent.md",
)

# Every directory that holds agent prompt files (invariant 2 scan surface).
AGENT_DIRS = (
    "deep-research/agents",
    "academic-paper/agents",
    "academic-paper-reviewer/agents",
    "academic-pipeline/agents",
    "shared/agents",
    "agents",
)

MANIFEST = "scripts/ars_phase_scope_manifest.json"


def _read_raw(path: Path) -> str:
    """Read WITHOUT universal-newline translation, so a CRLF file keeps its
    `\\r` bytes and cannot satisfy an exact LF line pin. A leading UTF-8 BOM
    is stripped: a YAML reader (and Claude Code) skips it, so leaving it on
    would make `\\ufeff---` fail the column-0 fence match and the whole file
    read as frontmatter-less — a fail-open that lets a BOM-prefixed Bucket A
    agent smuggle Bash past invariant 2's skip-when-no-frontmatter branch."""
    return path.read_bytes().decode("utf-8").lstrip("﻿")


def _frontmatter(text: str) -> str | None:
    """The raw YAML frontmatter block (the byte-faithful substring between the
    two `---` fences), or None when the file has no frontmatter.

    Line breaks are found with `str.splitlines`, which recognizes EVERY YAML
    line break — `\\n`, `\\r\\n`, and a bare `\\r` (old-Mac) plus the Unicode
    breaks NEL/LS/PS — so a bare-CR-delimited file is not silently read as
    frontmatter-less and skipped (a real fail-open, #524 r8). A fence is
    exactly `---` at column 0: an INDENTED `---` is block-scalar content, not
    a fence (matching it would truncate the block and hide keys). The block
    returned is the raw substring (original break bytes intact) so `compose`
    sees the true bytes and the byte-witness — anchored to `start_mark.index`
    — stays byte-faithful; a bare `\\r`/CRLF file therefore still fires the
    byte-witness as drift."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].splitlines()[0] != "---":
        return None
    # Byte offset just past the opening fence line (start of the block body).
    body_start = len(lines[0])
    offset = body_start
    for raw in lines[1:]:
        content = raw.splitlines()[0] if raw.splitlines() else raw
        if content == "---":  # column-0 closing fence
            return text[body_start:offset]
        offset += len(raw)
    return None


def _mapping_node(block: str) -> yaml.MappingNode | None:
    """The frontmatter composed to a DUPLICATE-PRESERVING mapping node, or
    None when it is not a mapping / will not compose / is too deeply nested
    to compose safely. Unlike `safe_load`, `compose` keeps a shadowed
    duplicate key visible in the node tree. A RecursionError on pathological
    nesting maps to None so the caller fails closed rather than crashing."""
    try:
        node = yaml.compose(block, Loader=yaml.SafeLoader)
    except (yaml.YAMLError, RecursionError):
        return None
    return node if isinstance(node, yaml.MappingNode) else None


_UNRESOLVED = object()


def _scalar_py(scalar: yaml.ScalarNode) -> object:
    """The Python value a scalar node resolves to, so `"tool\\u0073"`,
    `'tools'`, and `tools` all compare equal. `compose` already stamps each
    node with its resolved tag, so the SafeLoader constructs it exactly as
    `safe_load` would (quotes, `\\u` escapes, explicit `!!` tags, block/flow
    styles all honored). Any tag the safe constructor cannot build (a `<<`
    merge scalar, an unknown `!Tag`) yields _UNRESOLVED so callers fail
    closed rather than crash."""
    try:
        return yaml.SafeLoader("").construct_object(scalar)
    except yaml.YAMLError:
        return _UNRESOLVED


_MERGE_TAG = "tag:yaml.org,2002:merge"


def _uses_merge_or_alias(node: yaml.Node) -> bool:
    """True if the composed frontmatter uses a YAML merge key (`<<`) or an
    alias (`*name`). safe_load resolves both — a `<<: *base` injects a
    `tools`/`name` the literal-key scan never sees, and an alias shares a
    value node — so their presence makes the duplicate-preserving key scan
    unsound. Detected from the COMPOSED NODE TREE, not text (text scanning is
    not a sound YAML authority — the reviews' recurring lesson): the `merge`
    tag can land on a node of ANY type (`<<:` is a scalar key, but `? !!merge
    [x]` is a merge-tagged sequence/mapping key), so we check the tag on
    every node before dispatching on its type; an alias surfaces as the SAME
    node object reachable by two paths (compose resolves `*a` to shared
    identity). These hand-authored files never need either, so we fail closed
    rather than reimplement merge resolution. A RecursionError on pathological
    nesting also fails closed (True) — we could not prove the tree clean."""
    seen: set[int] = set()

    def walk(nd: yaml.Node) -> bool:
        if nd is None:
            return False
        if nd.tag == _MERGE_TAG:  # merge tag on ANY node type (key or value)
            return True
        if id(nd) in seen:
            return True  # reached twice = an alias shares this node
        seen.add(id(nd))
        if isinstance(nd, yaml.SequenceNode):
            return any(walk(i) for i in nd.value)
        if isinstance(nd, yaml.MappingNode):
            return any(walk(k) or walk(v) for k, v in nd.value)
        return False

    try:
        return walk(node)
    except RecursionError:
        return True


def _key_values(node: yaml.MappingNode, key: str) -> list[yaml.Node]:
    """Every value node whose key resolves to `key`, duplicates included
    (the node tree preserves a shadowed key that safe_load would collapse)."""
    return [v for k, v in node.value
            if isinstance(k, yaml.ScalarNode) and _scalar_py(k) == key]


def _key_nodes(node: yaml.MappingNode, key: str) -> list[yaml.ScalarNode]:
    """Every KEY node that resolves to `key` (for line marks), duplicates
    included."""
    return [k for k, v in node.value
            if isinstance(k, yaml.ScalarNode) and _scalar_py(k) == key]


def _node_to_py(value_node: yaml.Node) -> object:
    """A value node converted to its Python value, or the sentinel
    _UNRESOLVED when it is not a plain scalar/sequence of scalars (a nested
    list, a mapping member, or a mapping value — all unrecognized shapes)."""
    if isinstance(value_node, yaml.ScalarNode):
        return _scalar_py(value_node)
    if isinstance(value_node, yaml.SequenceNode):
        if not all(isinstance(i, yaml.ScalarNode) for i in value_node.value):
            return _UNRESOLVED  # nested list / mapping member
        return [_scalar_py(i) for i in value_node.value]
    return _UNRESOLVED


def _fold(text: str) -> str:
    """Text folded so an invisible/compatibility re-spelling collapses onto its
    plain ASCII form. Removes Unicode format characters (category `Cf` —
    BOM/`\\ufeff`, zero-width space/`\\u200b`, zero-width non-joiner/`\\u200c`,
    etc.), which `str.strip()` does NOT remove, so `\\ufeffBash\\ufeff` would
    otherwise survive as a token distinct from `Bash` and slip the `"Bash" in
    declared` membership test (#524 r9) — a fenced Bucket A agent could declare
    a zero-width-padded Bash and pass. Then NFKC-normalizes to fold
    compatibility homoglyphs (fullwidth, etc.) onto ASCII. All six real tool
    names + the `Bash(git:*)` permission form are pure ASCII and fold to
    themselves, so no legitimate value is altered."""
    stripped = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return unicodedata.normalize("NFKC", stripped)


def _normalized_tools(value: object) -> list[str] | None:
    """A `tools` value normalized to base tool names, or None when the shape
    is unrecognized. Accepts the comma-string form and a list of strings; a
    `Bash(git:*)`-style permission specifier normalizes to `Bash`. Folding
    (`_fold`) happens BEFORE any split, on the whole string (or on each list
    member whole), so every compatibility separator becomes its ASCII form
    first: a fullwidth comma `，` (U+FF0C) in the string form — which
    `split(",")` would miss, leaving `Read，Bash` as one token that an
    NFKC-normalizing consumer would re-split to grant Bash (#524 r11) — and a
    fullwidth-paren specifier `Bash（git:*）` (U+FF08/U+FF09) that the ASCII `(`
    split would miss (#524 r10) both reduce correctly. Splitting before folding
    reintroduces either hole. `value` comes from `_node_to_py`, which already
    collapses a non-scalar list member to `_UNRESOLVED`, so a list reaching
    here is all-strings; any non-str/list value (including `_UNRESOLVED`) is
    unrecognized."""
    if isinstance(value, str):
        items: list[str] = _fold(value).split(",")
    elif isinstance(value, list) and all(isinstance(i, str) for i in value):
        # A YAML list is already tokenized; fold each member whole (a
        # fullwidth comma inside a member is not a YAML separator, so it stays
        # one token — correctly, since no list consumer re-splits an element).
        items = [_fold(i) for i in value]
    else:
        return None
    out = []
    for item in items:
        base = item.split("(", 1)[0].strip()
        if base:
            out.append(base)
    return out


def _raw_tools_line(block: str, key_node: yaml.ScalarNode) -> str | None:
    """The raw frontmatter line the composed `tools` key SITS ON, for the
    byte-exact PINNED_TOOLS_LINE witness. Anchored to the node's
    `start_mark.index` — the character offset into `block` — sliced to the
    surrounding physical-`\\n` line, NOT `start_mark.line` (which counts
    YAML's Unicode line breaks NEL/LS/PS that `split("\\n")` does not, so the
    two indexings can diverge and select the wrong line — #524 r7). Using the
    byte offset makes the two agree by construction. Anchoring (not a text
    scan) also means a `tools:`-looking line inside a block scalar — e.g. a
    `description: |` documenting the tools — is never mistaken for the key
    line (round-6 false-positive). An ADDITIVE (still CI-gating) layer on top
    of the node-tree check: it only adds findings a capability-equivalent
    re-spelling would slip past (CRLF, trailing/interior whitespace, exact
    spelling), never clears the semantic check. Returns None when the offset
    is out of range."""
    idx = key_node.start_mark.index
    if not (0 <= idx <= len(block)):
        return None
    start = block.rfind("\n", 0, idx) + 1        # char after the prev newline
    end = block.find("\n", idx)                  # next newline, or end
    return block[start:] if end == -1 else block[start:end]


def _tools_value(node: yaml.MappingNode) -> object:
    """The effective (last-wins) `tools` Python value from the node tree, or
    _UNRESOLVED when the key is absent or its value has an unreadable shape."""
    values = _key_values(node, "tools")
    if not values:
        return _UNRESOLVED
    return _node_to_py(values[-1])  # YAML last-wins


def _name_value(node: yaml.MappingNode) -> str:
    """The effective `name` from the node tree ('' when absent/non-scalar)."""
    values = _key_values(node, "name")
    if not values:
        return ""
    py = _node_to_py(values[-1])
    return str(py).strip() if isinstance(py, str) else ""


def _bucket_a_names(root: Path) -> tuple[set[str] | None, str | None]:
    """Bucket A agent names from the manifest, or (None, error)."""
    mp = root / MANIFEST
    try:
        data = json.loads(mp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, (
            f"{MANIFEST}: unreadable or unparseable ({exc}) — invariant 2 "
            "(frontmatter/guard reconciliation) cannot run; failing closed."
        )
    agents = data.get("agents") if isinstance(data, dict) else None
    if not isinstance(agents, dict):
        return None, (
            f"{MANIFEST}: no `agents` mapping — invariant 2 cannot run; "
            "failing closed."
        )
    return set(agents), None


def check(root: Path) -> list[str]:
    errors: list[str] = []

    # --- invariant 1: exactly-one canonical `tools` on the six files ---------
    for rel in ALLOWLISTED_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(
                f"{rel}: allowlisted agent file is missing — the #514 "
                "surface changed; update ALLOWLISTED_FILES in "
                "check_tools_allowlist.py deliberately or restore the file."
            )
            continue
        block = _frontmatter(_read_raw(path))
        if block is None:
            errors.append(f"{rel}: no YAML frontmatter block found.")
            continue
        node = _mapping_node(block)
        if node is None:
            errors.append(
                f"{rel}: frontmatter does not compose to a YAML mapping — "
                "the tools allowlist cannot be verified; failing closed."
            )
            continue
        if _uses_merge_or_alias(node):
            errors.append(
                f"{rel}: frontmatter uses a YAML merge key / alias — these "
                "resolve to keys the pin cannot see (a `<<` can inject a "
                "`tools` value); not supported in agent frontmatter, "
                "failing closed."
            )
            continue
        tools_nodes = _key_values(node, "tools")
        if not tools_nodes:
            errors.append(
                f"{rel}: frontmatter has no `tools:` key — the #514 "
                "allowlist was dropped (a silent capability widening: the "
                "agent would inherit ALL tools). Restore "
                f"`{PINNED_TOOLS_LINE}`."
            )
        elif len(tools_nodes) > 1:
            errors.append(
                f"{rel}: {len(tools_nodes)} `tools` keys in frontmatter "
                "(duplicate-preserving parse — quoted / escaped variants "
                "included) — exactly one expected; a duplicate key overrides "
                "the pinned value under YAML last-wins resolution."
            )
        else:
            normalized = _normalized_tools(_node_to_py(tools_nodes[0]))
            if normalized != list(CANONICAL_TOOLS):
                errors.append(
                    f"{rel}: the `tools` value diverges from the canonical "
                    f"{', '.join(CANONICAL_TOOLS)} — the effective allowlist "
                    "is not what #514 froze."
                )
        # Byte-exact witness ON TOP (also pins CRLF / spelling). Additive
        # layer: it can only add findings, never clear the semantic check.
        # Anchored to the composed `tools` key's own line (not a text scan),
        # so a `tools:`-looking line inside a block scalar is not mistaken for
        # it. Only meaningful for the exactly-one-key case; the missing /
        # duplicate cases already fired via the semantic branch above. A
        # non-verbatim line (escaped/tagged/folded spelling, or CRLF /
        # whitespace drift) fires — the semantic check independently catches
        # the value-changing subset.
        key_nodes = _key_nodes(node, "tools")
        if len(key_nodes) == 1:
            raw_line = _raw_tools_line(block, key_nodes[0])
            if raw_line != PINNED_TOOLS_LINE:
                found = raw_line if raw_line is not None else \
                    "(tools key not on its own line)"
                errors.append(
                    f"{rel}: the `tools` line is not byte-equal to the frozen "
                    f"#514 form.\n    expected: {PINNED_TOOLS_LINE}\n    "
                    f"found:    {found!r}\n  Changing the allowlist is a "
                    "deliberate security-surface change: update "
                    "PINNED_TOOLS_LINE in check_tools_allowlist.py in the "
                    "same commit."
                )

    # --- invariant 2: no Bucket A agent declares Bash -------------------------
    bucket_a, manifest_err = _bucket_a_names(root)
    if manifest_err:
        errors.append(manifest_err)
        return errors
    for rel_dir in AGENT_DIRS:
        d = root / rel_dir
        if not d.is_dir():
            continue
        # rglob does NOT descend into directory symlinks, so a tracked
        # `agents/nested -> ../payload` could hide a Bucket A `.md` declaring
        # Bash (#524 r8). Fail closed on any directory symlink under an agent
        # dir — these hand-authored trees have no reason for one, and
        # reconciliation cannot see through it.
        for sub in sorted(d.rglob("*")):
            if sub.is_symlink() and sub.is_dir():
                errors.append(
                    f"{sub.relative_to(root).as_posix()}: directory symlink "
                    "under an agent dir — rglob does not descend into it, so a "
                    "Bucket A agent declaring Bash could hide behind it; "
                    "failing closed. Replace with real files."
                )
        # rglob, not glob: a nested `agents/subdir/x.md` could carry a Bucket
        # A `name` + Bash and the runtime guard keys on name regardless of
        # path, so the reconciliation must reach nested files too (#524 r7).
        for path in sorted(d.rglob("*.md")):
            rel = path.relative_to(root).as_posix()
            block = _frontmatter(_read_raw(path))
            if block is None:
                continue
            node = _mapping_node(block)
            if node is None:
                # Cannot read `name` to clear it — treat as a possible
                # Bucket A member and fail closed.
                errors.append(
                    f"{rel}: agent frontmatter does not compose to a YAML "
                    "mapping — cannot confirm it is not a Bucket A agent "
                    "advertising Bash; failing closed."
                )
                continue
            if _uses_merge_or_alias(node):
                # A `<<`/alias could inject `tools` or rewrite `name`
                # invisibly to the literal-key scan — fail closed rather than
                # clear the file on a name it may not really carry.
                errors.append(
                    f"{rel}: agent frontmatter uses a YAML merge key / alias "
                    "— cannot soundly confirm it is not a Bucket A agent "
                    "advertising Bash; failing closed."
                )
                continue
            # Duplicate `name`/`tools` handling is parser-dependent (last-wins
            # here, but another consumer may take first-wins). If ANY resolved
            # `name` is a Bucket A key, the file is in scope — and if it also
            # carries a duplicate `tools`, one resolution could hide Bash
            # behind the other. Fail closed rather than pick a winner, exactly
            # as invariant 1 rejects a duplicate `tools`.
            name_nodes = _key_values(node, "name")
            resolved_names = {_node_to_py(n) for n in name_nodes}
            if not resolved_names & bucket_a:
                continue
            if len(name_nodes) > 1:
                errors.append(
                    f"{rel}: {len(name_nodes)} `name` keys in frontmatter, one "
                    "resolving to a Bucket A agent — duplicate-key resolution "
                    "is parser-dependent; failing closed."
                )
                continue
            if len(_key_values(node, "tools")) > 1:
                errors.append(
                    f"{rel}: Bucket A agent has {len(_key_values(node, 'tools'))} "
                    "`tools` keys — duplicate-key resolution is "
                    "parser-dependent and one could hide Bash behind another; "
                    "failing closed."
                )
                continue
            tools_value = _tools_value(node)
            if tools_value is _UNRESOLVED:
                if _key_values(node, "tools"):
                    errors.append(
                        f"{rel}: Bucket A agent has a `tools` value of "
                        "unrecognized shape — cannot verify it excludes "
                        "Bash; failing closed."
                    )
                continue
            declared = _normalized_tools(tools_value)
            if declared is None:
                errors.append(
                    f"{rel}: Bucket A agent has a `tools` value of "
                    "unrecognized shape — cannot verify it excludes Bash; "
                    "failing closed."
                )
            elif "Bash" in declared:
                errors.append(
                    f"{rel}: frontmatter declares Bash but this is a Bucket "
                    f"A agent in {MANIFEST} — the runtime guard denies "
                    "Bucket A agents ALL Bash (zero fail-open), so this "
                    "grant is either dead (hook-active) or a silent widening "
                    "(hook-less). Remove Bash from the tools list."
                )

    return errors


def main() -> int:
    errors = check(REPO_ROOT)
    if errors:
        print("tools allowlist check failed (#524):")
        for err in errors:
            print(f"- {err}")
        return 1
    print("tools allowlist check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
