"""Contract tests for Socratic research-question authorship boundaries.

These are file-content tests: they pin the default non-generation fallback and
the visible transition required before system-authored candidate questions.

Run standalone:
    python -m pytest scripts/test_socratic_rq_non_generation_contract.py -q
"""
from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MARKER = "[SOCRATIC-NON-GENERATION-EXIT: explicit_user_request]"

# #834: the mentor agent is the single authority for auto-end round caps
# (#490). Reference files point at it and carry no round count of their own.
AUTO_END_AUTHORITY_HEADING = "### Auto-End Conditions (Precise)"
AUTO_END_POINTER = "Auto-End Conditions"
AUTO_END_AUTHORITY_FILE = "socratic_mentor_agent.md"

# #834: vocabulary that turns the user's own directions into a ranked or
# preselected option, or narrows the dialogue on the system's initiative.
# The #735 boundary forbids ranking and preselection, not only generation.
F6_RANKING_PHRASES = (
    "most promising",
    "convergence potential",
    "restrict discussion scope",
    "restrict scope",
    "restrict the scope",
    "narrow the scope",
)
_ROUND_COUNT = re.compile(r"\b\d+\s+rounds?\b|\bround\s+\d+\b", re.IGNORECASE)
_END_VERB = re.compile(
    r"auto-?compile|automatically compile|\bends?\b|\bterminat", re.IGNORECASE
)

PATHS = {
    "positioning": REPO_ROOT / "POSITIONING.md",
    "skill": REPO_ROOT / "deep-research" / "SKILL.md",
    "mentor": REPO_ROOT / "deep-research" / "agents" / "socratic_mentor_agent.md",
    "rq_agent": REPO_ROOT / "deep-research" / "agents" / "research_question_agent.md",
    "failure_paths": REPO_ROOT / "deep-research" / "references" / "failure_paths.md",
    "protocol": REPO_ROOT / "deep-research" / "references" / "socratic_mode_protocol.md",
}


def _read_all() -> dict[str, str]:
    return {name: path.read_text(encoding="utf-8") for name, path in PATHS.items()}


def _between(text: str, start: str, end: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at + len(start))
    return text[start_at:end_at]


def _contract_errors(documents: dict[str, str]) -> list[str]:
    """Return cross-surface drift errors for mutation tests and baseline QA."""
    errors: list[str] = []

    for name, text in documents.items():
        if MARKER not in text:
            errors.append(f"{name}: missing visible exit marker")

    mentor_boundary = _between(
        documents["mentor"],
        "## Research-Question Authorship Boundary",
        "## Wording-Pattern Advisory",
    )
    rq_branch = _between(
        documents["rq_agent"],
        "## Socratic Mode Branch",
        "#### FINER Guiding Questions",
    )
    socratic_failure = _between(
        documents["failure_paths"],
        "**Handling Steps — `socratic` mode (default)**",
        "**Explicit generation request — visible exit from Socratic mode**",
    )

    for name, section in {
        "mentor": mentor_boundary,
        "rq_agent": rq_branch,
        "failure_paths": socratic_failure,
    }.items():
        lowered = section.lower()
        if "non-convergence" not in lowered:
            errors.append(f"{name}: non-convergence boundary missing")
        if "summar" not in lowered or "user" not in lowered:
            errors.append(f"{name}: user-expressed summary fallback missing")
        if "lit-review" not in section:
            errors.append(f"{name}: literature-exploration fallback missing")

    if "until the user cannot converge" in rq_branch:
        errors.append("rq_agent: round-triggered candidate escape hatch remains")
    if "only then offer candidates" in rq_branch:
        errors.append("rq_agent: non-convergence still authorizes candidates")
    if "Produce 3 candidate RQs" in socratic_failure:
        errors.append("failure_paths: Socratic default still produces candidates")
    if "select the closest" in socratic_failure.lower():
        errors.append("failure_paths: Socratic default still presents an AI menu")

    for name in ("mentor", "rq_agent", "failure_paths", "protocol", "skill", "positioning"):
        prose = documents[name].replace(MARKER, "")
        normalized = " ".join(prose.lower().split())
        if "explicit user request" not in normalized and "explicitly asks" not in normalized:
            errors.append(f"{name}: exit is not bound to an explicit user request")

    # #834 — F6 (non-convergence) must not rank, preselect, or narrow.
    f6 = _between(documents["failure_paths"], "### F6:", "### F7:")
    f6_lower = f6.lower()
    for phrase in F6_RANKING_PHRASES:
        if phrase in f6_lower:
            errors.append(
                f"failure_paths: F6 still ranks, preselects, or narrows a direction ({phrase!r})"
            )

    # #834 — no reference file states its own auto-end round count; both
    # point at the agent file, which must still carry the authority heading.
    management = _between(
        documents["protocol"], "## Dialogue Management Rules", "## Reading Probe"
    )
    for name, section in {"failure_paths": f6, "protocol": management}.items():
        for line in section.splitlines():
            probe = line.replace(AUTO_END_POINTER, "")
            if _ROUND_COUNT.search(probe) and _END_VERB.search(probe):
                errors.append(f"{name}: carries its own auto-end round count")
                break
        if AUTO_END_POINTER not in section or AUTO_END_AUTHORITY_FILE not in section:
            errors.append(f"{name}: auto-end authority pointer missing")
    if AUTO_END_AUTHORITY_HEADING not in documents["mentor"]:
        errors.append("mentor: auto-end authority heading missing")

    return errors


def test_repository_contract_is_consistent() -> None:
    assert _contract_errors(_read_all()) == []


def test_full_mode_candidate_workflow_remains_separate() -> None:
    documents = _read_all()
    full_agent = documents["rq_agent"].split("## Socratic Mode Branch", 1)[0]
    full_failure = _between(
        documents["failure_paths"],
        "**Handling Steps — `full` mode**",
        "**Handling Steps — `socratic` mode (default)**",
    )
    assert "Generate 3-5 candidate research questions" in full_agent
    assert "Produce 3 candidate RQs" in full_failure


def test_default_fallback_does_not_treat_round_count_as_consent() -> None:
    documents = _read_all()
    rq_branch = _between(
        documents["rq_agent"],
        "## Socratic Mode Branch",
        "#### FINER Guiding Questions",
    )
    mentor_boundary = _between(
        documents["mentor"],
        "## Research-Question Authorship Boundary",
        "## Wording-Pattern Advisory",
    )
    assert "After any number of" in rq_branch
    assert "Non-convergence, elapsed rounds, stagnation" in mentor_boundary
    assert "never consent" in mentor_boundary


def test_generated_candidates_are_not_recorded_as_user_insights() -> None:
    documents = _read_all()
    mentor_boundary = _between(
        documents["mentor"],
        "## Research-Question Authorship Boundary",
        "## Wording-Pattern Advisory",
    )
    assert "AI-generated starting points" in mentor_boundary
    assert "Do not tag" in mentor_boundary
    assert "do not silently re-enter" in mentor_boundary


def test_marker_removal_is_detected() -> None:
    documents = _read_all()
    documents["mentor"] = documents["mentor"].replace(MARKER, "")
    assert "mentor: missing visible exit marker" in _contract_errors(documents)


def test_round_triggered_candidate_regression_is_detected() -> None:
    documents = _read_all()
    anchor = "- **Never turn non-convergence into candidate generation.**"
    documents["rq_agent"] = documents["rq_agent"].replace(
        anchor,
        "- **Withhold candidate RQs until the user cannot converge; only then offer candidates.**",
        1,
    )
    errors = _contract_errors(documents)
    assert "rq_agent: round-triggered candidate escape hatch remains" in errors
    assert "rq_agent: non-convergence still authorizes candidates" in errors


def test_socratic_candidate_menu_regression_is_detected() -> None:
    documents = _read_all()
    anchor = "1. Compile a clearly labeled summary"
    documents["failure_paths"] = documents["failure_paths"].replace(
        anchor,
        "1. Produce 3 candidate RQs and ask the user to select the closest.\n1. Compile a clearly labeled summary",
        1,
    )
    errors = _contract_errors(documents)
    assert "failure_paths: Socratic default still produces candidates" in errors
    assert "failure_paths: Socratic default still presents an AI menu" in errors


def test_no_answer_iron_rule_is_scoped_to_active_non_generation_mode() -> None:
    documents = _read_all()
    for name in ("skill", "mentor", "protocol"):
        assert "while non-generation Socratic mode is active" in documents[name], name
        assert MARKER in documents[name], name


def test_f6_ranked_or_preselected_direction_regression_is_detected() -> None:
    """The pre-#834 F6 bytes (ranked pick, convergence-potential triage, scope
    restriction) must fail the contract."""
    documents = _read_all()
    anchor = "### F6: Socratic Dialogue Does Not Converge\n"
    pre_fix_lines = (
        "> (A) Continue the Socratic dialogue, but focus on [the most promising direction] you just mentioned?\n"
        "2. Identify the 1-2 directions with the most convergence potential\n"
        "- Continue with focus → restrict discussion scope, converge within 5 rounds\n"
    )
    documents["failure_paths"] = documents["failure_paths"].replace(
        anchor, anchor + "\n" + pre_fix_lines, 1
    )
    errors = _contract_errors(documents)
    for phrase in ("most promising", "convergence potential", "restrict discussion scope"):
        assert any(phrase in error for error in errors), (phrase, errors)


def test_reference_file_own_round_cap_regression_is_detected() -> None:
    """The pre-#834 'round 15 → end' sentences on both reference files must fail."""
    documents = _read_all()
    documents["protocol"] = documents["protocol"].replace(
        "## Dialogue Management Rules\n",
        "## Dialogue Management Rules\n\n"
        "- If dialogue exceeds 15 rounds -> automatically compile INSIGHTs and end\n",
        1,
    )
    documents["failure_paths"] = documents["failure_paths"].replace(
        "### F6: Socratic Dialogue Does Not Converge\n",
        "### F6: Socratic Dialogue Does Not Converge\n\n"
        "4. If user chooses to continue but still hasn't converged by round 15 → auto-compile + end\n",
        1,
    )
    errors = _contract_errors(documents)
    assert "protocol: carries its own auto-end round count" in errors
    assert "failure_paths: carries its own auto-end round count" in errors


def test_auto_end_authority_pointer_removal_is_detected() -> None:
    documents = _read_all()
    documents["failure_paths"] = documents["failure_paths"].replace(
        AUTO_END_POINTER, "auto-end rules"
    )
    documents["protocol"] = documents["protocol"].replace(
        AUTO_END_AUTHORITY_FILE, "the mentor agent"
    )
    documents["mentor"] = documents["mentor"].replace(
        AUTO_END_AUTHORITY_HEADING, "### Auto-End Conditions", 1
    )
    errors = _contract_errors(documents)
    assert "failure_paths: auto-end authority pointer missing" in errors
    assert "protocol: auto-end authority pointer missing" in errors
    assert "mentor: auto-end authority heading missing" in errors


def test_stagnation_trigger_and_layer_minimums_are_not_round_caps() -> None:
    """Round counts that are triggers or layer minimums, not termination rules,
    stay allowed on the reference files."""
    documents = _read_all()
    documents["protocol"] = documents["protocol"].replace(
        "## Dialogue Management Rules\n",
        "## Dialogue Management Rules\n\n"
        "- At least 2 rounds of dialogue per layer before moving to the next\n"
        "- If no convergence after 10 rounds -> summarize only user-expressed directions\n",
        1,
    )
    errors = _contract_errors(documents)
    assert "protocol: carries its own auto-end round count" not in errors
