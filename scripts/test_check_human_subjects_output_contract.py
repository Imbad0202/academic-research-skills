"""Mutation tests for the #665 human-subjects output boundary."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts import check_human_subjects_output_contract as contract


REPO_ROOT = Path(__file__).resolve().parents[1]


def mirror(tmp_path: Path) -> Path:
    for rel in contract.REQUIRED:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, target)
    return tmp_path


def mutate(root: Path, rel: Path, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"mutation target missing: {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_real_repository_passes() -> None:
    assert contract.run_checks(REPO_ROOT) == []


@pytest.mark.parametrize(
    "rel", [contract.ETHICS_CHECKLIST, contract.IRB_REFERENCE]
)
def test_post_migration_authority_boundary_is_pinned(
    tmp_path: Path, rel: Path
) -> None:
    root = mirror(tmp_path)
    mutate(
        root,
        rel,
        "Authority boundary (#665/#666/#680)",
        "Authority result",
    )
    assert contract.run_checks(root)


@pytest.mark.parametrize("rel", [contract.ETHICS_AGENT, contract.ARCHITECT_AGENT])
def test_fixed_footer_mutation_fails(tmp_path: Path, rel: Path) -> None:
    root = mirror(tmp_path)
    mutate(root, rel, contract.FOOTER, contract.FOOTER.replace("does not", "may"))
    assert contract.run_checks(root)


def test_readiness_cannot_promote_authorization(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    mutate(
        root,
        contract.ETHICS_AGENT,
        "A readiness result must never derive, promote, or update authorization status.",
        "A readiness result may update authorization status.",
    )
    assert contract.run_checks(root)


def test_authorization_field_cannot_collapse_into_readiness(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    mutate(
        root,
        contract.ETHICS_AGENT,
        "`authorization_status`: `documented | not_provided | cannot_verify`",
        "`submission_readiness`: `gaps_located | no_listed_gaps_located | unresolved`",
    )
    assert contract.run_checks(root)


def test_integrity_verdict_scope_mutation_fails(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    mutate(
        root,
        contract.ETHICS_AGENT,
        "It is not human-subjects clearance or authorization.",
        "It is human-subjects clearance and authorization.",
    )
    assert contract.run_checks(root)


def test_bare_pathway_output_is_rejected(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    mutate(
        root,
        contract.ARCHITECT_AGENT,
        "the pathway field must read `institutional determination required`",
        "Determine Exempt/Expedited/Full Board",
    )
    errors = contract.run_checks(root)
    assert errors
    assert any("forbidden determination-shaped text" in error for error in errors)


def test_universal_timeline_is_rejected(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    mutate(
        root,
        contract.ARCHITECT_AGENT,
        "`unknown — obtain current institutional estimate`",
        "IRB review timeline (2-8 weeks)",
    )
    assert contract.run_checks(root)


def test_legacy_architect_output_template_is_rejected(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    mutate(
        root,
        contract.ARCHITECT_AGENT,
        "### Human-Subjects Administrative Status (if human subjects involved)",
        "### IRB Plan (if human subjects involved)",
    )
    errors = contract.run_checks(root)
    assert any("forbidden determination-shaped text" in error for error in errors)


def test_decision_log_bytes_are_pinned(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    mutate(root, contract.ETHICS_AGENT, "| Item | Verdict |", "| Item | Status |")
    assert contract.run_checks(root)
