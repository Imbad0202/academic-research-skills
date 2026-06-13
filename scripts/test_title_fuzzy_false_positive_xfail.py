#!/usr/bin/env python3
"""Anti-false-closure pin for #250 (DELIBERATELY xfail).

#250 records that the citation-extraction gold set cannot catch a regression
where a resolver's title fallback *accidentally* accepts a wrong record as
`matched`. The reason is architectural: the gold set feeds STATIC
`resolver_outcomes` to the pure reducer (`run_evals.py`), so the match/no-match
decision has already been made before a tuple's data begins. The decision lives
one layer below — in the client `title_search` similarity threshold and
`_resolve_doi_then_title` — which the gold set never executes. (See the #250
finding comment for the full trace.)

This file is the resolver-client-layer test that issue asked for, and it
surfaces a REAL defect, not just a coverage gap: the current title match
criterion is `difflib.SequenceMatcher.ratio() >= 0.70` over punctuation-stripped
titles (`scripts/_text_similarity.py`). Character-level ratio scores distinct
works far above 0.70 when their titles share long substrings:

    "Deep Residual Learning for Image Recognition"
    "Deep Residual Learning for Image Recognition on Embedded Devices"  -> 0.815
    "Attention Is All You Need" vs "Attention Is Not All You Need"       -> 0.926
    "A Survey of Reinforcement Learning in Healthcare" vs
    "A Survey of Deep Reinforcement Learning in Robotics"               -> 0.808

So a real-but-unindexed citation whose title search surfaces a *different* paper
with a near-identical title is collapsed to `matched` (false positive), and
`_resolve_doi_then_title` runs the title fallback with NO year/author re-check to
catch it. That is exactly the regression #250 names.

The same 0.70 SequenceMatcher criterion is shared (via `_text_similarity`) by the
Crossref / OpenAlex / Semantic Scholar clients, so this defect is not
Crossref-specific; CrossrefClient is the representative under test because its
`title_search` is the most direct.

The tests are marked `xfail(strict=True)`: they assert the CORRECT behavior (a
distinct work is rejected), which fails today by construction, so CI stays green.
DO NOT delete them to make CI "cleaner." When the match criterion is hardened
(the defect follow-up issue — token-set / length-penalty / negation-aware
scoring), these flip to xpass and strict-xfail FAILS the build, forcing removal
of the marker and conversion to a real passing assertion.

Run:
    PYTHONPATH=. python -m pytest scripts/test_title_fuzzy_false_positive_xfail.py -v
"""
from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch

import pytest


def _mock_response(payload: dict) -> MagicMock:
    """Build a urlopen() context-manager mock returning `payload` as JSON.

    Mirrors the mock shape in test_crossref_client.py so this pin exercises the
    real client HTTP path, not a stub.
    """
    resp = MagicMock()
    resp.read.return_value = json.dumps(payload).encode("utf-8")
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)
    return resp


@pytest.mark.xfail(
    reason="#250 title-fuzzy false positive: the 0.70 SequenceMatcher criterion "
           "accepts a distinct work whose title is a superstring of the cited "
           "title (0.815). No year/author re-check catches it. Remove this xfail "
           "only when the match criterion is hardened (the #250 defect follow-up).",
    strict=True,
)
def test_superstring_title_is_rejected_as_distinct_work():
    """A cited work's title search surfaces a DIFFERENT paper whose title merely
    contains the cited title as a prefix. The correct verdict is "no match" (the
    cited work is genuinely unindexed); today the threshold accepts it."""
    from crossref_client import CrossrefClient

    cited_title = "Deep Residual Learning for Image Recognition"
    # The only candidate the index returns is a real but DIFFERENT paper.
    surfaced_distinct_work = {
        "title": ["Deep Residual Learning for Image Recognition on Embedded Devices"],
        "DOI": "10.0000/not-the-cited-work",
    }
    payload = {"message": {"items": [surfaced_distinct_work]}}

    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        client = CrossrefClient()
        result = client.title_search(cited_title)

    assert result is None, (
        "title_search accepted a distinct work (superstring title) as a match — "
        "false positive. The cited work is unindexed; the resolver surfaced a "
        "different paper."
    )


@pytest.mark.xfail(
    reason="#250 title-fuzzy false positive: the 0.70 SequenceMatcher criterion "
           "scores a negated title (semantic opposite) at 0.926, accepting it as "
           "a match. Remove this xfail only when the match criterion is hardened "
           "(the #250 defect follow-up).",
    strict=True,
)
def test_negated_title_is_rejected_as_distinct_work():
    """A negation ("Not") flips a title's meaning but barely moves the
    character-level ratio. The correct verdict is "no match"; today it passes."""
    from crossref_client import CrossrefClient

    cited_title = "Attention Is All You Need"
    surfaced_distinct_work = {
        "title": ["Attention Is Not All You Need"],
        "DOI": "10.0000/different-negated-work",
    }
    payload = {"message": {"items": [surfaced_distinct_work]}}

    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        client = CrossrefClient()
        result = client.title_search(cited_title)

    assert result is None, (
        "title_search accepted a semantically negated title as a match — "
        "false positive on a distinct work."
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
