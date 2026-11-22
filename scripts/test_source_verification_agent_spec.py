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

    heading = re.search(r"^### Claim Verification Verdicts$", template, re.MULTILINE)
    assert heading is not None
    verdicts_pos = heading.start()
    decomp_pos = template.index("### Claim Decomposition")
    assert verdicts_pos < decomp_pos, (
        "Claim Verification Verdicts should appear as a standard report section "
        "before the conditional Claim Decomposition block"
    )

    verdicts_block = template[verdicts_pos:decomp_pos]
    table_lines = [line for line in verdicts_block.splitlines() if line.startswith("|")]
    assert len(table_lines) >= 3, "Missing header, separator, or example row in Claim Verification Verdicts table"
    header, _, example_row = table_lines[:3]
    columns = [cell.strip() for cell in header.strip("|").split("|")]
    assert columns == ["Claim", "Verdict", "Epistemic Status", "Independent Sources", "Basis / Notes"]
    cells = dict(zip(columns, (cell.strip() for cell in example_row.strip("|").split("|")), strict=True))
    for verdict in ("Verified", "Partially True", "False", "Unverifiable"):
        assert verdict in cells["Verdict"], f"Missing verdict option {verdict!r} in Verdict cell"
    for status in (
        "established fact",
        "supported hypothesis",
        "contested claim",
        "speculation",
        "undetermined (for Unverifiable)",
    ):
        assert status in cells["Epistemic Status"], f"Missing status option {status!r} in Epistemic Status cell"

    assert "**Factual Claims Checked**: X / Y (Z%; target >= 30%)" in template
    assert "Count only claims checked against two or more independent sources in X." in template
    assert "Keep attempts with fewer sources in the verdict table." in template


def test_unverifiable_and_fabricated_outcomes_do_not_overlap() -> None:
    text = AGENT_DOC.read_text(encoding="utf-8")
    outcomes = _section(text, "#### Verification Outcome")

    rows = re.findall(r"^- `([A-Z0-9_]+)`: (.*)$", outcomes, re.MULTILINE)
    lines = dict(rows)
    assert len(rows) == len(lines), "Each verification verdict must have exactly one outcome row"
    conditions = {verdict: line.partition("→")[0].strip() for verdict, line in lines.items()}
    actions = {verdict: line.partition("→")[2].strip() for verdict, line in lines.items()}
    assert set(actions) == {"S2_VERIFIED", "VERIFIED", "PLAUSIBLE", "UNVERIFIABLE", "FABRICATED"}
    assert all(conditions.values()) and all(actions.values())
    assert actions["UNVERIFIABLE"] == "Keep and flag for human review."
    assert actions["FABRICATED"] == "CRITICAL, must remove"
    assert {verdict for verdict, action in actions.items() if "remove" in action.lower()} == {"FABRICATED"}
    other_verdicts = set(lines) - {"FABRICATED"}
    assert not any(other in conditions["FABRICATED"] for other in other_verdicts)
    assert not any(phrase in conditions["FABRICATED"].lower() for phrase in ("classify as", "mark as", "instead"))
    assert "Positive evidence establishes that the cited work itself was invented" in conditions["FABRICATED"]
    assert "DOI_MISMATCH" not in lines["FABRICATED"]
    assert (
        "Existence remains unconfirmed and there is no positive evidence of invention, "
        "whether because lookup across Tiers 0–2 was exhausted or because lookup tools are unavailable."
    ) in conditions["UNVERIFIABLE"]
    assert "only when existence remains unconfirmed" in conditions["UNVERIFIABLE"]
    assert "publisher record" in conditions["PLAUSIBLE"].lower()
    assert "missing or does not resolve" in conditions["PLAUSIBLE"]
    assert "DOI result" in actions["PLAUSIBLE"]
    assert "Journal indexing flags do not change this verdict" in conditions["VERIFIED"]


def test_red_flags_do_not_equate_missing_index_with_nonexistent_journal() -> None:
    text = AGENT_DOC.read_text(encoding="utf-8")
    red_flags = _section(text, "#### Red Flags for Hallucinated References")

    assert "Journal name does not exist (not indexed in Scopus/WoS/DOAJ)" not in red_flags
    assert "screening flag" in red_flags.lower()
    assert "not standalone proof of fabrication" in red_flags.lower()
