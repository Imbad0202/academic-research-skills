"""Contract tests for Socratic research-question authorship boundaries.

These are file-content tests: they pin the default non-generation fallback and
the visible transition required before system-authored candidate questions.

Run standalone:
    python -m pytest scripts/test_socratic_rq_non_generation_contract.py -q
"""
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MARKER = "[SOCRATIC-NON-GENERATION-EXIT: explicit_user_request]"

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
