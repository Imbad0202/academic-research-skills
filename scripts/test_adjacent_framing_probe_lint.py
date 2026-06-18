"""Lint tests for the opt-in Socratic adjacent-framing probe.

Target spec: docs/design/2026-06-18-socratic-adjacent-framing-probe-spec.md.

File-content lints (read bytes + regex, no LLM runtime, no subprocess fork) against:
- deep-research/agents/socratic_mentor_agent.md §"Optional Adjacent-Framing Probe Layer"

Pattern matches scripts/test_reading_probe_lint.py.

Run standalone:
    python -m unittest scripts/test_adjacent_framing_probe_lint.py -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MENTOR_AGENT = REPO_ROOT / "deep-research" / "agents" / "socratic_mentor_agent.md"
# Scoring / pipeline files the probe must NOT leak into:
COLLABORATION_RUBRIC = REPO_ROOT / "shared" / "collaboration_depth_rubric.md"
PIPELINE_PROCESS_SUMMARY = REPO_ROOT / "academic-pipeline" / "references" / "process_summary_protocol.md"

PROBE_HEADING = "## Optional Adjacent-Framing Probe Layer"
ENV_VAR = "ARS_SOCRATIC_ADJACENT_PROBE"

REQUIRED_PROBE_SUBHEADINGS = [
    "### Activation",
    "### Probe Wording",
    "### Response Handling",
    "### Banned Patterns",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_probe_section(text: str) -> str:
    """Return the bytes from PROBE_HEADING up to the next H2 (## ) or EOF."""
    start = text.find(PROBE_HEADING)
    if start == -1:
        return ""
    rest = text[start + len(PROBE_HEADING):]
    nxt = re.search(r"\n## ", rest)
    return rest[: nxt.start()] if nxt else rest


class TestAdjacentFramingProbeStructure(unittest.TestCase):
    def setUp(self) -> None:
        self.mentor_text = _read(MENTOR_AGENT)
        self.section = _extract_probe_section(self.mentor_text)

    def test_mentor_file_has_probe_section(self) -> None:
        self.assertIn(
            PROBE_HEADING,
            self.mentor_text,
            f"{MENTOR_AGENT.name} must contain '{PROBE_HEADING}'",
        )

    def test_required_subheadings_present(self) -> None:
        for sub in REQUIRED_PROBE_SUBHEADINGS:
            self.assertIn(
                sub, self.section, f"Adjacent-framing probe section missing '{sub}'"
            )

    def test_env_var_gates_the_layer(self) -> None:
        self.assertIn(
            ENV_VAR,
            self.section,
            f"Probe layer must be gated by env var {ENV_VAR}",
        )
        # The "=1" activation discipline must be explicit somewhere in the section.
        self.assertRegex(
            self.section,
            re.escape(ENV_VAR) + r"[^\n]*?(?:=|\bset to\b)[^\n]*?`?1`?",
            "Probe layer must specify the env var activates on the string '1'",
        )


if __name__ == "__main__":
    unittest.main()
