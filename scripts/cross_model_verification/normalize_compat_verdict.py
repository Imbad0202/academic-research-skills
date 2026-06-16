"""Normalize an OpenAI-compatible provider's citation-verification response to ONE status.

Compatible providers (MiMo / DeepSeek / self-hosted) expose no hosted web-search tool, so
there is no grounding trace to evidence a positive verdict. The security invariant:

  - a positive `VERIFIED` is downgraded to NOT_SEARCHED (an ungrounded confirmation can
    never count as a grounded agreement);
  - a rejection (NOT_FOUND / MISMATCH) passes through — it is a useful disagreement and
    needs no grounding to be acted on;
  - anything else (self-reported NOT_SEARCHED, unparseable text, empty) fails closed to
    NOT_SEARCHED.

The consumer (agreement counter) must read ONLY the returned `status`. Raw model text is
kept in `context` for humans and is never parsed for a verdict.
"""
from __future__ import annotations

import re

# First explicit verdict token wins; matched case-insensitively at a word boundary.
_VERDICT_RE = re.compile(r"\b(VERIFIED|NOT_FOUND|MISMATCH|NOT_SEARCHED)\b", re.IGNORECASE)

# Rejections survive as-is; a positive is downgraded; everything else fails closed.
_PASS_THROUGH = {"NOT_FOUND", "MISMATCH"}


def normalize_compat_verdict(raw: str) -> dict:
    """Return {"status": <normalized>, "context": <raw>} for a compatible-provider response."""
    raw = raw or ""
    m = _VERDICT_RE.search(raw)
    token = m.group(1).upper() if m else None
    # Only rejections survive; VERIFIED (downgrade), self-reported NOT_SEARCHED, or no
    # recognizable token all fail closed to NOT_SEARCHED.
    status = token if token in _PASS_THROUGH else "NOT_SEARCHED"
    return {"status": status, "context": raw}
