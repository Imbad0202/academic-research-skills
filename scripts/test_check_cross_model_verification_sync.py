"""Tests for the cross-model grounding-guard doc-sync lint (#346 / #349).

Mutation-style: confirm the lint PASSES the real tree and FAILS on each violation class it
exists to catch, so it is not vacuously green.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
LINT = REPO / "scripts" / "check_cross_model_verification_sync.py"
DOC = REPO / "shared" / "cross_model_verification.md"

# A re-inline of the (pre-#349 naive) Gemini sources jq, used by the re-inline mutation test.
REINLINE_OLD = 'cites="$(jq -r -f "$GUARD/gemini_sources.jq" <<<"$body")"'
REINLINE_NEW = (
    'cites="$(jq -r \'[ .candidates[0].groundingMetadata.groundingSupports[]?'
    '.groundingChunkIndices[]? ]\' <<<"$body")"'
)


def _load_lint():
    spec = importlib.util.spec_from_file_location("xmv_sync_lint", LINT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _assert_lint_fails_on_mutation(tmp_path, monkeypatch, old: str, new: str):
    """Apply a string mutation to the doc and assert the lint rejects it (returns 1)."""
    mod = _load_lint()
    mutated = DOC.read_text(encoding="utf-8").replace(old, new)
    assert mutated != DOC.read_text(encoding="utf-8"), f"mutation {old!r}→{new!r} was a no-op"
    fake = tmp_path / "cross_model_verification.md"
    fake.write_text(mutated, encoding="utf-8")
    monkeypatch.setattr(mod, "DOC", fake)
    assert mod.main() == 1


def test_lint_passes_real_tree():
    assert _load_lint().main() == 0


def test_required_filters_all_exist_on_disk():
    mod = _load_lint()
    for name in mod.REQUIRED_FILTERS:
        assert (mod.GUARD_DIR / name).is_file(), f"canonical filter absent: {name}"


@pytest.mark.parametrize(
    "old,new",
    [
        # drop a canonical-filter reference (rename it so the doc no longer wires the .jq)
        ("gemini_is_grounded.jq", "gemini_RENAMED.jq"),
        # drop each safety branch
        ("NOT_SEARCHED", "OK_FINE"),
        ("CROSS-MODEL-ERROR", "oops"),
    ],
    ids=["filter-ref-dropped", "not-searched-dropped", "cross-model-error-dropped"],
)
def test_lint_fails_on_doc_mutation(tmp_path, monkeypatch, old, new):
    """Each removal of a wired filter reference or a safety branch must fail the lint."""
    _assert_lint_fails_on_mutation(tmp_path, monkeypatch, old, new)


def test_lint_fails_when_guard_reinlined(tmp_path, monkeypatch):
    """Re-inlining the naive Gemini sources jq must be caught — it bypasses the tested .jq.

    Kept separate from the parametrized cases: this is a distinct mechanism (check 4 — an inline
    jq program referencing a grounding token), not a dropped reference/branch.
    """
    _assert_lint_fails_on_mutation(tmp_path, monkeypatch, REINLINE_OLD, REINLINE_NEW)


def test_lint_fails_when_jq_f_only_in_comment(tmp_path, monkeypatch):
    """A commented-out `jq -f` line (filename surviving only in a comment) must NOT satisfy the
    wiring check — the lint scans executable bash lines, not comments/prose."""
    _assert_lint_fails_on_mutation(
        tmp_path,
        monkeypatch,
        REINLINE_OLD,
        '# ' + REINLINE_OLD + '\n  cites="$(jq -r ".candidates[0].x" <<<"$body")"',
    )


def test_lint_fails_when_jq_f_only_in_trailing_comment(tmp_path, monkeypatch):
    """A `jq -f` filename surviving only in a TRAILING comment on a weak inline line must NOT
    satisfy the wiring check — trailing comments are stripped before the check."""
    _assert_lint_fails_on_mutation(
        tmp_path,
        monkeypatch,
        REINLINE_OLD,
        'cites="$(jq -r ".candidates[0].x" <<<"$body")"  # ' + REINLINE_OLD,
    )


def test_lint_fails_on_double_quoted_inline_grounding_jq(tmp_path, monkeypatch):
    """An inline jq program referencing a grounding token must be caught even when double-quoted
    (the re-inline guard scans both quote styles, not just single quotes)."""
    _assert_lint_fails_on_mutation(
        tmp_path,
        monkeypatch,
        REINLINE_OLD,
        'cites="$(jq -r "[.candidates[0].groundingMetadata.groundingChunks[].web.uri]" <<<"$body")"',
    )


# --- #453 narrowed regression checks (Task 5) ------------------------------------------------

def test_lint_fails_if_compat_drops_not_searched_in_bash(tmp_path, monkeypatch):
    """The compatible block's executable bash must keep a NOT_SEARCHED fail-closed default.
    Mutate the fail-closed branch so the block no longer references NOT_SEARCHED there."""
    _assert_lint_fails_on_mutation(
        tmp_path, monkeypatch,
        'status="NOT_SEARCHED" ;;  # VERIFIED downgrade',
        'status="OK" ;;  # VERIFIED downgrade',
    )


def test_lint_fails_if_openai_base_url_expansion_reintroduced(tmp_path, monkeypatch):
    """A passive OPENAI_BASE_URL expansion in executable bash must fail (the passive-downgrade
    regression). Reintroduce the PR's endpoint line."""
    _assert_lint_fails_on_mutation(
        tmp_path, monkeypatch,
        'endpoint="${ARS_OPENAI_COMPAT_BASE_URL%/}/chat/completions"',
        'endpoint="${OPENAI_BASE_URL:-https://api.openai.com}/v1/chat/completions"',
    )


def test_lint_fails_if_double_v1_reintroduced(tmp_path, monkeypatch):
    """A literal /v1/v1 in executable bash must fail (the double-v1 endpoint bug)."""
    _assert_lint_fails_on_mutation(
        tmp_path, monkeypatch,
        'endpoint="${ARS_OPENAI_COMPAT_BASE_URL%/}/chat/completions"',
        'endpoint="${ARS_OPENAI_COMPAT_BASE_URL%/}/v1/v1/chat/completions"',
    )


def test_lint_fails_if_compat_precedence_becomes_rejection_only(tmp_path, monkeypatch):
    """The compatible normalization must scan the leftmost of ALL FOUR tokens (parity with
    normalize_compat_verdict.py). Mutate the four-token scan into a rejection-only grep and
    the lint must reject it — a VERIFIED-led ramble would otherwise pass through as a
    disagreement instead of failing closed."""
    _assert_lint_fails_on_mutation(
        tmp_path, monkeypatch,
        "grep -oiE '\\b(VERIFIED|NOT_FOUND|MISMATCH|NOT_SEARCHED)\\b'",
        "grep -oiE '\\b(NOT_FOUND|MISMATCH)\\b'",
    )


def test_lint_allows_openai_base_url_in_prose(tmp_path, monkeypatch):
    """A PROSE/comment mention of OPENAI_BASE_URL (explaining we don't read it) must NOT
    false-fail — the check targets executable assignment/expansion only."""
    mod = _load_lint()
    text = DOC.read_text(encoding="utf-8")
    injected = text.replace(
        "## API Call Patterns",
        "We deliberately never read `OPENAI_BASE_URL` here.\n\n## API Call Patterns",
        1,
    )
    assert injected != text
    fake = tmp_path / "cross_model_verification.md"
    fake.write_text(injected, encoding="utf-8")
    monkeypatch.setattr(mod, "DOC", fake)
    assert mod.main() == 0
