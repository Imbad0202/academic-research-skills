"""Regression tests for deep-research/agents/source_verification_agent.md (#1137).

Guards two invariants:
1. The Output Format report template includes a dedicated per-claim verdict
   entry (`### Claim Verification Verdicts`) separate from the optional
   `Claim Decomposition` block, matching the Phase Boundary deliverable and
   the 30% factual-claim cross-reference criterion.
2. `UNVERIFIABLE` and `FABRICATED` in `#### Verification Outcome` are mutually
   exclusive: an exhausted lookup across Tiers 0-2 stays `UNVERIFIABLE`, while
   `FABRICATED` requires positive evidence of invention and cannot be triggered
   by exhausted lookup tiers or a screening red flag (such as absence from
   Scopus/WoS/DOAJ) alone.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_DOC = REPO_ROOT / "deep-research" / "agents" / "source_verification_agent.md"


def _section(text: str, heading: str) -> str:
    """Return the markdown section starting at `heading` until the next heading of same/higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    pattern = re.compile(
        rf"^{re.escape(heading)}\s*$\n(.*?)(?=^#{{1,{level}}}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    assert match is not None, f"Missing section {heading!r} in {AGENT_DOC}"
    return match.group(1)


def _extract_output_format_template(text: str) -> str:
    match = re.search(
        r"^## Output Format\s*$\s*```markdown\s*\n(.*?)\n```",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None, "Missing ```markdown``` template block in ## Output Format"
    return match.group(1)


def test_output_format_has_claim_verification_verdicts_section() -> None:
    text = AGENT_DOC.read_text(encoding="utf-8")
    template = _extract_output_format_template(text)

    assert "### Claim Verification Verdicts" in template
    verdicts_pos = template.index("### Claim Verification Verdicts")
    decomp_pos = template.index("### Claim Decomposition")
    assert verdicts_pos < decomp_pos, (
        "Claim Verification Verdicts should appear as a standard report section "
        "before the conditional Claim Decomposition block"
    )

    verdicts_block = template[verdicts_pos:decomp_pos]
    for column in ("Claim", "Verdict", "Epistemic Status", "Independent Sources"):
        assert column in verdicts_block, f"Missing column {column!r} in Claim Verification Verdicts table"
    for verdict in ("Verified", "Partially True", "False", "Unverifiable"):
        assert verdict in verdicts_block, f"Missing verdict option {verdict!r} in Claim Verification Verdicts table"

    assert "Factual Claims Checked" in template


def test_unverifiable_and_fabricated_outcomes_do_not_overlap() -> None:
    text = AGENT_DOC.read_text(encoding="utf-8")
    outcomes = _section(text, "#### Verification Outcome")

    unverifiable_match = re.search(r"^- `UNVERIFIABLE`:(.*)$", outcomes, re.MULTILINE)
    fabricated_match = re.search(r"^- `FABRICATED`:(.*)$", outcomes, re.MULTILINE)
    assert unverifiable_match is not None, "Missing UNVERIFIABLE outcome"
    assert fabricated_match is not None, "Missing FABRICATED outcome"

    unverifiable_line = unverifiable_match.group(1).lower()
    fabricated_line = fabricated_match.group(1).lower()

    assert "tiers 0" in unverifiable_line or "exhausted" in unverifiable_line
    assert "human review" in unverifiable_line
    assert "do not auto-remove" in unverifiable_line

    assert "evidence of non-existence (all tiers fail)" not in fabricated_line
    assert "positive evidence" in fabricated_line
    assert "not" in fabricated_line and "unverifiable" in fabricated_line


def test_red_flags_do_not_equate_missing_index_with_nonexistent_journal() -> None:
    text = AGENT_DOC.read_text(encoding="utf-8")
    red_flags = _section(text, "#### Red Flags for Hallucinated References")

    assert "Journal name does not exist (not indexed in Scopus/WoS/DOAJ)" not in red_flags
    assert "screening flag" in red_flags.lower()
    assert "not standalone proof of fabrication" in red_flags.lower()
