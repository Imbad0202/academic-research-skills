#!/usr/bin/env python3
"""Distribution-surface claim discipline lint (#753).

The #745 capability matrix pins README claim anchors, and version-consistency
invariant 8 binds the plugin.json agent-count number to the tree — but the
2026-08-17 ISO 42001-spirit audit (T-1) found the marketing surfaces
themselves (`.claude-plugin/plugin.json` / `.claude-plugin/marketplace.json`
description fields) sat outside every lock, so their language had silently
outrun the evidence record ("Production-grade", "39-agent ensemble" against 8
`NOT_RUN` task families and 3 plugin-exposed agents). This lint closes that
surface so the same drift class fails CI instead of shipping. It lives apart
from check_version_consistency.py on purpose: claim language is not
version-scoped, and that script's manifest checks deliberately fail OPEN on
these conditions (invariant 8 defers absence to invariant 4) where this lint
must fail CLOSED.

  D1. Both distribution manifests exist and parse as JSON (fail-closed: a
      missing or unparseable manifest is an error, never a silent pass —
      the invariant-4 lesson: deleting or renaming a claim surface must not
      disable its check).
  D2. Every description field (plugin.json top-level; marketplace.json
      top-level and each plugins[] entry) is a non-empty string.
  D3. No description carries claim language the evidence record does not
      license. Descriptions are marketing surfaces, never evidence-carrying
      matrix rows, so the capability matrix's effectiveness vocabulary
      (imported from check_stage_capability_matrix so a matrix-side stem
      addition binds this surface in the same commit) is refused
      unconditionally — a description cannot cite the MEASURED-row
      licensing the matrix's M6 check honors — as is any percentage figure
      (the matrix's unmeasured-percentage rule, `_PERCENT_RE`; the T-3
      "31% -> ~5-10%" class), plus the two surface-specific phrases the
      audit removed: "production-grade" and "agent ensemble"
      (execution/error independence the default inline path does not
      provide). Word-boundary matching, not semantic parsing (the M6
      convention; see the semantics note at FORBIDDEN_PATTERNS).
  D4. The plugin.json description carries at least one agent-count token
      in a spelling invariant 8 can bind ("N-agent" / "N prompt roles",
      canonical casing). Invariant 8 is opt-in by spelling — a reworded
      or dropped count silently detaches the number from the tree (#414's
      drift class, nearly reintroduced by the #753 reword itself) — so
      the presence half fails closed here while the value half stays
      invariant 8's job.
  D5. Any "N plugin-exposed" count in a description equals the
      check_agents_mirror_sync MIRRORS roster size — the same #414 drift
      class for the second number the #753 description introduced.

The manifests are also read by check_version_consistency.py (invariants 4
and 8); the double-report on a missing/malformed manifest is intentional —
per-script fail-closed loaders are the repo convention, and this lint must
not inherit invariant 8's silent-pass posture.

Usage:
  python3 scripts/check_distribution_surface_claims.py [--root PATH]

Exit 0 = all invariants hold; exit 1 = violations (listed on stderr).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from check_agents_mirror_sync import MIRRORS  # noqa: E402
from check_stage_capability_matrix import (  # noqa: E402
    _MEASURED_LICENSED_STEMS,
    _NEVER_LICENSED_STEMS,
    _PERCENT_RE,
)
from check_version_consistency import AGENT_CLAIM_RE  # noqa: E402

REPO_ROOT = _SCRIPTS_DIR.parent

# Matching-semantics note: the matrix's M6 check scans row prose with plain
# case-insensitive SUBSTRING matching; descriptions are short marketing
# strings, so this surface uses word-boundary regexes instead — same
# vocabulary, deliberately stricter about false fires ("proven" must not
# fire inside "provenance", pinned by test). Stems that are complete words
# take a trailing boundary; the rest are prefix stems (improv*, guarantee*).
_WHOLE_WORD_STEMS = frozenset({"proven"})

# Surface-specific phrases the 2026-08-17 audit removed; not part of the
# matrix vocabulary because they are only over-claims on a distribution
# surface (a matrix row could legitimately discuss an "ensemble" design).
_SURFACE_ONLY_PHRASES = (
    ("production-grade", r"\bproduction[- ]grade\b"),
    ("agent ensemble", r"\bagent ensembles?\b"),
)

FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (
        stem,
        re.compile(
            r"\b" + re.escape(stem)
            + (r"\b" if stem in _WHOLE_WORD_STEMS else ""),
            re.IGNORECASE,
        ),
    )
    for stem in _NEVER_LICENSED_STEMS + _MEASURED_LICENSED_STEMS
) + tuple(
    (label, re.compile(pattern, re.IGNORECASE))
    for label, pattern in _SURFACE_ONLY_PHRASES
)

_PLUGIN_EXPOSED_RE = re.compile(r"(\d+)\s+plugin-exposed", re.IGNORECASE)


def _reject_json_constant(value: str) -> None:
    """`json.loads` accepts non-standard NaN/Infinity by default; strict
    distribution consumers reject them, so D1 must too (fail-closed)."""
    raise ValueError(f"non-standard JSON constant {value!r}")


def _load_manifest(path: Path, errors: list[str]) -> dict | None:
    """D1: fail-closed manifest load."""
    if not path.is_file():
        errors.append(f"D1: {path} is missing — the claim surface cannot "
                      f"silently leave this lint's coverage")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"),
                          parse_constant=_reject_json_constant)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        errors.append(f"D1: {path} failed to parse as JSON ({exc})")
        return None
    if not isinstance(data, dict):
        errors.append(f"D1: {path} top level is not a JSON object")
        return None
    return data


def _check_description(surface: str, value, errors: list[str]) -> None:
    """D2 shape + D3 claim-language discipline + D5 plugin-exposed binding
    for one description field."""
    if not isinstance(value, str) or not value.strip():
        errors.append(f"D2: {surface} description is missing, empty, or "
                      f"not a string")
        return
    for label, pattern in FORBIDDEN_PATTERNS:
        if pattern.search(value):
            errors.append(
                f"D3: {surface} description contains unlicensed claim "
                f"language ({label!r}) — distribution surfaces must stay "
                f"within the evidence record "
                f"(docs/STAGE_CAPABILITY_MATRIX.md); see #753"
            )
    # _PERCENT_RE spells "percent" lowercase and its matrix caller lowercases
    # its input first — mirror that here so "31 Percent" cannot slip through.
    if _PERCENT_RE.search(value.lower()):
        errors.append(
            f"D3: {surface} description carries a percentage figure — "
            f"descriptions can never carry the measurement provenance the "
            f"capability matrix requires for numeric claims; see #753"
        )
    for m in _PLUGIN_EXPOSED_RE.finditer(value):
        if int(m.group(1)) != len(MIRRORS):
            errors.append(
                f"D5: {surface} description claims {m.group(1)} "
                f"plugin-exposed agents but the check_agents_mirror_sync "
                f"MIRRORS roster has {len(MIRRORS)}"
            )


def run(root: Path) -> list[str]:
    errors: list[str] = []
    plugin_dir = root / ".claude-plugin"

    plugin = _load_manifest(plugin_dir / "plugin.json", errors)
    if plugin is not None:
        description = plugin.get("description")
        _check_description("plugin.json", description, errors)
        if isinstance(description, str) and not AGENT_CLAIM_RE.search(
            description
        ):
            errors.append(
                "D4: plugin.json description carries no agent-count token "
                "invariant 8 can bind ('N-agent' / 'N prompt roles', "
                "canonical casing) — a reworded or dropped count detaches "
                "the advertised number from the tree (#414); see #753"
            )

    marketplace = _load_manifest(plugin_dir / "marketplace.json", errors)
    if marketplace is not None:
        _check_description(
            "marketplace.json", marketplace.get("description"), errors
        )
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            errors.append("D2: marketplace.json plugins[] is missing or "
                          "empty — the per-plugin description surface cannot "
                          "silently leave this lint's coverage")
        else:
            for i, entry in enumerate(plugins):
                if not isinstance(entry, dict):
                    errors.append(f"D2: marketplace.json plugins[{i}] is "
                                  f"not an object")
                    continue
                _check_description(
                    f"marketplace.json plugins[{i}]",
                    entry.get("description"),
                    errors,
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    errors = run(args.root)
    if errors:
        for e in errors:
            print(f"check_distribution_surface_claims: {e}", file=sys.stderr)
        return 1
    print("PASSED: check_distribution_surface_claims — distribution-surface "
          "descriptions stay within the evidence record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
