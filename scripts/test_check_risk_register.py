"""Mutation tests for check_risk_register.py (#759).

Strategy: build a tmp repo root that mirrors the real register, README, and
capability matrix, materialize every path the real register cites as a
placeholder file, verify the baseline passes, then apply one mutation per
test and assert the intended invariant fires.

The fixture derives the placeholder list with the lint's own extractors, so
a new register row cannot silently outgrow the fixture — and two hardcoded
witness assertions keep the extractors themselves honest (a broken extractor
would empty the witness set, not pass vacuously). A real-tree test pins the
lint against the actual repository as well, so a local pytest run catches
what the separate CI lint step would.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from check_risk_register import (
    DOC_RELPATH,
    MATRIX_RELPATH,
    README_RELPATH,
    _doc_text,
    referenced_paths,
    run_all_checks,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files whose real content the lint reads (not merely existence-checks).
_MIRRORED_FILES = tuple(
    str(p) for p in (DOC_RELPATH, README_RELPATH, MATRIX_RELPATH)
)

# Extractor witnesses: paths the real register is known to cite. If the
# extractor regressed, these assertions fail loudly instead of letting the
# placeholder fixture (and every RR-1 test) go vacuous.
_WITNESS_SPAN = "scripts/verify_passport.py"
_WITNESS_LINK = "STAGE_CAPABILITY_MATRIX.md"


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    for rel in _MIRRORED_FILES:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, dst)
    links, spans = referenced_paths(_doc_text(REPO_ROOT))
    assert _WITNESS_SPAN in spans
    assert _WITNESS_LINK in links
    doc_dir = tmp_path / DOC_RELPATH.parent
    for rel in spans:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
    for rel in links:
        target = (doc_dir / rel.partition("#")[0]).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.touch()
    return tmp_path


def _mutate(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"mutation anchor missing from {rel}: {old!r}"
    path.write_text(text.replace(old, new), encoding="utf-8")


def test_baseline_passes(repo: Path) -> None:
    assert run_all_checks(repo) == []


def test_real_tree_passes() -> None:
    assert run_all_checks(REPO_ROOT) == []


def test_missing_doc_is_single_fatal_error(repo: Path) -> None:
    (repo / DOC_RELPATH).unlink()
    errors = run_all_checks(repo)
    assert errors == [f"RR-1: {DOC_RELPATH} is missing"]


# --- RR-1 pointer integrity -------------------------------------------------


def test_nonexistent_backtick_path_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(DOC_RELPATH),
        f"`{_WITNESS_SPAN}`",
        "`scripts/no_such_gate.py`",
    )
    errors = run_all_checks(repo)
    assert any("RR-1" in e and "no_such_gate" in e for e in errors)


def test_deleted_cited_file_fires(repo: Path) -> None:
    (repo / _WITNESS_SPAN).unlink()
    errors = run_all_checks(repo)
    assert any("RR-1" in e and _WITNESS_SPAN in e for e in errors)


def test_broken_relative_link_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(DOC_RELPATH),
        f"({_WITNESS_LINK})",
        "(NO_SUCH_PAGE.md)",
    )
    errors = run_all_checks(repo)
    assert any("RR-1" in e and "NO_SUCH_PAGE.md" in e for e in errors)


def test_repo_escaping_link_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(DOC_RELPATH),
        f"({_WITNESS_LINK})",
        "(../../outside/escape.md)",
    )
    errors = run_all_checks(repo)
    assert any("RR-1" in e and "escapes" in e for e in errors)


def test_unresolvable_anchor_fragment_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(DOC_RELPATH),
        f"({_WITNESS_LINK})",
        f"({_WITNESS_LINK}#no-such-heading)",
    )
    errors = run_all_checks(repo)
    assert any("RR-1" in e and "no-such-heading" in e for e in errors)


def test_case_wrong_fragment_is_not_re_slugified(repo: Path) -> None:
    target = repo / DOC_RELPATH.parent / _WITNESS_LINK
    target.write_text("# Mixed Case\n", encoding="utf-8")
    _mutate(
        repo,
        str(DOC_RELPATH),
        f"({_WITNESS_LINK})",
        f"({_WITNESS_LINK}#Mixed-Case)",
    )

    errors = run_all_checks(repo)

    assert any("RR-1" in e and "Mixed-Case" in e for e in errors)


def test_anchor_on_non_markdown_target_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(DOC_RELPATH),
        f"({_WITNESS_LINK})",
        f"(../{MATRIX_RELPATH.as_posix()}#some-heading)",
    )
    errors = run_all_checks(repo)
    assert any("RR-1" in e and "non-markdown" in e for e in errors)


def test_leading_slash_span_is_not_a_path(repo: Path) -> None:
    # Slash commands like `/ars-mark-read` must stay opted out of RR-1.
    _, spans = referenced_paths(_doc_text(repo))
    assert not any(token.startswith("/") for token in spans)


# --- RR-2 status mirroring --------------------------------------------------


def test_doc_side_status_upgrade_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(DOC_RELPATH),
        "`NOT_RUN` (capability matrix row `retrieval.citation_existence_gate`)",
        "`MEASURED` (capability matrix row `retrieval.citation_existence_gate`)",
    )
    errors = run_all_checks(repo)
    assert any(
        "RR-2" in e and "retrieval.citation_existence_gate" in e for e in errors
    )


def test_matrix_side_status_change_fires(repo: Path) -> None:
    matrix_path = repo / MATRIX_RELPATH
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    mutated = False
    for row in matrix["rows"]:
        if row["row_id"] == "review.calibration":
            row["behavioral_evidence"]["status"] = "MEASURED"
            mutated = True
    assert mutated
    matrix_path.write_text(json.dumps(matrix), encoding="utf-8")
    errors = run_all_checks(repo)
    assert any("RR-2" in e and "matrix records" in e for e in errors)


def test_unknown_row_id_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(DOC_RELPATH),
        "`retrieval.citation_existence_gate`)",
        "`retrieval.no_such_row`)",
    )
    errors = run_all_checks(repo)
    assert any("RR-2" in e and "does not exist" in e for e in errors)


def test_invalid_status_token_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(DOC_RELPATH),
        "`DESIGNED` (asserted here; no capability-matrix row)",
        "`RUNNING` (asserted here; no capability-matrix row)",
    )
    errors = run_all_checks(repo)
    assert any("RR-2" in e and "RUNNING" in e for e in errors)


def test_asserted_measurement_claim_fires(repo: Path) -> None:
    # The matrix is the sole authority for MEASURED/MIXED: an asserted-here
    # citation may not carry a measurement status.
    _mutate(
        repo,
        str(DOC_RELPATH),
        "`DESIGNED` (asserted here; no capability-matrix row)",
        "`MEASURED` (asserted here; no capability-matrix row)",
    )
    errors = run_all_checks(repo)
    assert any("RR-2" in e and "sole authority" in e for e in errors)


def test_demoted_matrix_citation_fires_inventory_lock(repo: Path) -> None:
    # Rewriting a lint-pinned matrix citation as an asserted-here one must
    # fail until _EXPECTED_MATRIX_ROW_CITATIONS is updated in the same
    # commit.
    _mutate(
        repo,
        str(DOC_RELPATH),
        "`MEASURED` (capability matrix row `revision.claim_drift_guard`)",
        "`NOT_RUN` (asserted here; no capability-matrix row)",
    )
    errors = run_all_checks(repo)
    assert any(
        "RR-2" in e and "revision.claim_drift_guard" in e and "no longer" in e
        for e in errors
    )


def test_relocated_matrix_citation_fires_inventory_lock(repo: Path) -> None:
    # Moving a matrix citation out of the Evidence-status bullet (into the
    # Residual-gap bullet) while asserting the status must not satisfy the
    # inventory lock.
    _mutate(
        repo,
        str(DOC_RELPATH),
        "- **Evidence status**: `MEASURED` (capability matrix row "
        "`revision.claim_drift_guard`).\n- **Residual gap**:",
        "- **Evidence status**: `NOT_RUN` (asserted here; no "
        "capability-matrix row).\n- **Residual gap**: `MEASURED` "
        "(capability matrix row `revision.claim_drift_guard`) —",
    )
    errors = run_all_checks(repo)
    assert any(
        "RR-2" in e and "revision.claim_drift_guard" in e and "no longer" in e
        for e in errors
    )


def test_space_containing_span_path_still_checked(repo: Path) -> None:
    # A typo'd path with a space must fail RR-1, not silently opt out.
    _mutate(
        repo,
        str(DOC_RELPATH),
        f"`{_WITNESS_SPAN}`",
        "`scripts/no such gate.py`",
    )
    errors = run_all_checks(repo)
    assert any("RR-1" in e and "no such gate" in e for e in errors)


def test_malformed_matrix_citation_fires(repo: Path) -> None:
    # Dropping the row_id backticks must not silently demote the citation
    # to unchecked prose.
    _mutate(
        repo,
        str(DOC_RELPATH),
        "(capability matrix row `revision.claim_drift_guard`)",
        "(capability matrix row revision.claim_drift_guard)",
    )
    errors = run_all_checks(repo)
    assert any("RR-2" in e and "well-formed" in e for e in errors)


def test_citation_free_evidence_bullet_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(DOC_RELPATH),
        "- **Evidence status**: `MEASURED` (capability matrix row "
        "`revision.claim_drift_guard`).",
        "- **Evidence status**: measured, trust me.",
    )
    errors = run_all_checks(repo)
    assert any("RR-2" in e and "no recognized" in e for e in errors)


# --- RR-3 discoverability ---------------------------------------------------


def test_removed_readme_link_fires(repo: Path) -> None:
    _mutate(
        repo,
        str(README_RELPATH),
        "docs/RISK_REGISTER.md",
        "docs/SOMEWHERE_ELSE.md",
    )
    errors = run_all_checks(repo)
    assert any("RR-3" in e for e in errors)


def test_code_span_pseudo_link_does_not_satisfy_rr3(repo: Path) -> None:
    # A link inside backticks renders literally; it must not count.
    _mutate(
        repo,
        str(README_RELPATH),
        "[docs/RISK_REGISTER.md](docs/RISK_REGISTER.md)",
        "`[docs/RISK_REGISTER.md](docs/RISK_REGISTER.md)`",
    )
    errors = run_all_checks(repo)
    assert any("RR-3" in e for e in errors)
