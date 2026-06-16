"""Tier-1 behavioral guard for the OpenAI-compatible verdict normalization (#453).

The security invariant: an ungrounded compatible provider can never launder a positive
VERIFIED into a grounded agreement, but a genuine rejection (NOT_FOUND/MISMATCH) is a
useful disagreement and must survive. The consumer (agreement counter) reads ONLY the
returned `status`; raw model text lives in `context` and is never parsed for a verdict.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MOD_PATH = REPO / "scripts" / "cross_model_verification" / "normalize_compat_verdict.py"


def _load():
    spec = importlib.util.spec_from_file_location("normalize_compat_verdict", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _counts_as_grounded_agreement(result) -> bool:
    """Mirror the consumer: a row counts toward grounded agreement iff its status is a
    grounded positive. Compatible never produces one, so this must be False for VERIFIED."""
    return result["status"] == "VERIFIED"


def test_verified_is_downgraded_and_never_agrees():
    mod = _load()
    r = mod.normalize_compat_verdict("VERIFIED — found at https://doi.org/10.1/fake")
    assert r["status"] == "NOT_SEARCHED"
    assert _counts_as_grounded_agreement(r) is False


def test_verified_raw_text_not_in_a_parseable_verdict_slot():
    mod = _load()
    r = mod.normalize_compat_verdict("VERIFIED https://doi.org/10.1/fake")
    # raw text may be retained for humans, but only in `context`, never in `status`.
    assert r["status"] == "NOT_SEARCHED"
    assert "VERIFIED" not in r["status"]
    assert r.get("context", "").startswith("VERIFIED")  # preserved, but consumer ignores it


def test_not_found_passes_through_as_disagreement():
    mod = _load()
    r = mod.normalize_compat_verdict("NOT_FOUND — no matching record exists")
    assert r["status"] == "NOT_FOUND"


def test_mismatch_passes_through_as_disagreement():
    mod = _load()
    r = mod.normalize_compat_verdict("MISMATCH — year is 2021 not 2019")
    assert r["status"] == "MISMATCH"


def test_self_reported_not_searched_stays_not_searched():
    mod = _load()
    assert mod.normalize_compat_verdict("NOT_SEARCHED — could not search")["status"] == "NOT_SEARCHED"


def test_unparseable_text_defaults_closed_to_not_searched():
    mod = _load()
    assert mod.normalize_compat_verdict("the paper looks plausible to me")["status"] == "NOT_SEARCHED"


def test_empty_response_is_not_searched():
    mod = _load()
    assert mod.normalize_compat_verdict("")["status"] == "NOT_SEARCHED"


def test_lowercase_rejection_token_passes_through():
    """The matcher is case-insensitive by design (models may not uppercase). Pin that a
    lowercase rejection token still survives as a disagreement, not silently dropped."""
    mod = _load()
    assert mod.normalize_compat_verdict("not_found — no such record")["status"] == "NOT_FOUND"


def test_none_input_fails_closed():
    """None must not raise (the `raw or ''` guard); it fails closed to NOT_SEARCHED."""
    mod = _load()
    assert mod.normalize_compat_verdict(None)["status"] == "NOT_SEARCHED"


def test_verified_first_then_rejection_fails_closed():
    """SECURITY: a response that LEADS with VERIFIED but later mentions a rejection token
    must fail closed to NOT_SEARCHED (leftmost-of-all-four precedence), never pass through
    as a disagreement. This pins the position-based precedence the security contract needs."""
    mod = _load()
    assert mod.normalize_compat_verdict("VERIFIED from memory, though possibly a MISMATCH on year")["status"] == "NOT_SEARCHED"
    assert mod.normalize_compat_verdict("VERIFIED. NOT_FOUND in my training data.")["status"] == "NOT_SEARCHED"
