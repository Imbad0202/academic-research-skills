#!/usr/bin/env python3
"""Reference grammar + routing for the #527 cross-model handoff envelope.

`shared/cross_model_verification.md` § Cross-model handoff envelope (#527)
names this module as the NORMATIVE grammar: the prose describes the contract,
this module decides it. A dispatcher (the main session running a skill, or
`pipeline_orchestrator_agent` in pipeline Mode A) that consumes an owner's
handoff block behaves exactly like `parse_handoff` + `route_result`; the
deterministic owner → dispatcher → owner fixtures in
`scripts/test_cross_model_handoff.py` pin that behavior with a fake
transport (no external API, no manuscript upload).

Design constraints inherited from #523/#518:

- The owner's committed decision travels OUTSIDE the payload; only the
  payload is ever forwarded to the cross-model (blindness).
- Agreement → the dispatcher performs the mechanical fill and does NOT
  re-invoke the owner. Divergence → the dispatcher re-invokes the original
  owner with the minimum return context; it never authors the rebuttal.
- Anything malformed (envelope or result) fails safely to `unavailable` —
  the dispatcher never fabricates a judgment.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field

OPEN_FENCE = "[CROSS-MODEL-HANDOFF v1]"
CLOSE_FENCE = "[/CROSS-MODEL-HANDOFF]"
# Any handoff-shaped opener, any version. A v2 fence must be REJECTED as
# malformed, never silently treated as an ordinary deliverable (fail-closed
# on unknown versions — codex #527 round-1 P1).
_ANY_OPEN_FENCE_RE = re.compile(r"^\[CROSS-MODEL-HANDOFF\b.*\]$")

CHECKPOINT_KINDS = {
    # kind -> (expected_result, decision enum or None)
    "design_freeze": (
        "enum_comparison",
        ("sound", "revise_before_freeze", "fundamental_concern"),
    ),
    "editorial_decision": (
        "enum_comparison",
        ("accept", "minor_revision", "major_revision", "reject"),
    ),
    "da_critique": ("full_return", None),
}
# Closed kind -> owner binding: a design_freeze envelope claiming a different
# owner would route the divergence re-invocation to the wrong agent,
# violating "re-invoke the ORIGINAL owner" (codex #527 round-1 P1).
EXPECTED_OWNERS = {
    "design_freeze": "research_architect_agent",
    "editorial_decision": "editorial_synthesizer_agent",
    "da_critique": "devils_advocate_reviewer_agent",
}
EXPECTED_RESULTS = ("enum_comparison", "full_return")
CONFIDENCE_VALUES = ("low", "medium", "high")
MAX_DRIVERS = 3

# Routing outcomes (the dispatcher's complete decision space).
AGREEMENT_FILL = "agreement_fill_no_reinvoke"
DIVERGENCE_REINVOKE = "divergence_reinvoke_owner"
FULL_RETURN_REINVOKE = "full_return_reinvoke_owner"
UNAVAILABLE = "unavailable"


class HandoffError(ValueError):
    """Malformed envelope or result. Dispatchers map this to
    `[CROSS-MODEL-ERROR: <reason>]` + outcome `unavailable` — never a
    fabricated judgment."""


@dataclass
class Handoff:
    checkpoint_kind: str
    owner_agent: str
    correlation_id: str
    expected_result: str
    payload: str
    decision_enum: tuple[str, ...] | None = None
    owner_decision: dict | None = None


@dataclass
class Routing:
    outcome: str  # one of AGREEMENT_FILL / DIVERGENCE_REINVOKE / FULL_RETURN_REINVOKE / UNAVAILABLE
    error: str | None = None
    # Minimum context the dispatcher MUST return to the owner on
    # re-invocation (empty when no re-invocation happens).
    return_context: dict = field(default_factory=dict)


_HEADER_RE = re.compile(r"^([a-z_]+):[ \t]*(.*)$")
_REQUIRED_HEADERS = ("checkpoint_kind", "owner_agent", "correlation_id", "expected_result")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    """json.loads keeps the LAST duplicate key silently — an object with two
    different `decision` values would be routed by the latter (codex #527
    round-10 P1). Reject ambiguity instead."""
    obj: dict = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key {key!r}")
        obj[key] = value
    return obj


def _reject_constant(name: str):
    # NaN / Infinity / -Infinity are not standard JSON — a "strict" decision
    # object must not smuggle them through (codex #527 round-13 P1).
    raise ValueError(f"non-standard JSON constant {name!r}")


def _loads_strict(raw: str):
    return json.loads(
        raw,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_constant,
    )


def _is_blank(text: str) -> bool:
    """Blank = nothing left after stripping whitespace AND Unicode format
    (Cf) characters — an invisible-only payload or response must not count
    as substance (codex #527 round-11 P1)."""
    return not "".join(
        c for c in text if unicodedata.category(c) != "Cf"
    ).strip()


def _fold_for_detection(line: str) -> str:
    """Strip whitespace AND Unicode format (Cf) characters for fence
    DETECTION only — a zero-width-prefixed fence must be detected (then
    rejected by the raw-equality acceptance check), not skipped as an
    ordinary deliverable (#524 fold-before-compare lesson). Acceptance
    stays raw column-0 equality."""
    return "".join(c for c in line if unicodedata.category(c) != "Cf").strip()


def _is_fence_shaped(line: str) -> bool:
    folded = _fold_for_detection(line)
    return bool(_ANY_OPEN_FENCE_RE.match(folded)) or folded == CLOSE_FENCE


def extract_handoff_block(text: str) -> str | None:
    """Return the first fenced handoff block (fences included), or None.

    Recognition rule: both fences must sit at the start of their own line.
    An output with no block is an ordinary deliverable — the dispatcher
    must not invent a transport for it.
    """
    lines = text.splitlines()
    # Detection is generous (stripped match, any version) so nothing
    # handoff-shaped can pass as an ordinary deliverable; ACCEPTANCE is
    # strict (raw line equality at column 0, exact v1) so an indented or
    # re-versioned fence is malformed, never transported (codex #527
    # round-5 P1: indented fences).
    opens = [i for i, l in enumerate(lines) if _ANY_OPEN_FENCE_RE.match(_fold_for_detection(l))]
    closes = [i for i, l in enumerate(lines) if _fold_for_detection(l) == CLOSE_FENCE]
    if not opens and not closes:
        return None
    if len(opens) > 1 or len(closes) > 1:
        # A fence-shaped line inside the payload (or a second envelope)
        # would silently truncate/confuse extraction — reject the whole
        # output instead of guessing which fence is real (codex #527
        # round-2 P1: closing-fence collision).
        raise HandoffError(
            "malformed_handoff: ambiguous fences — exactly one envelope per "
            "output, and the payload must not contain a fence-shaped line"
        )
    if not opens:
        raise HandoffError("malformed_handoff: closing fence without opening fence")
    start = opens[0]
    if lines[start] != OPEN_FENCE:
        raise HandoffError(
            f"malformed_handoff: fence {lines[start]!r} is not the exact "
            f"column-0 {OPEN_FENCE!r} (indented or unknown-version fences "
            f"are rejected, never transported)"
        )
    if not closes or closes[0] < start:
        raise HandoffError("malformed_handoff: opening fence without closing fence")
    if lines[closes[0]] != CLOSE_FENCE:
        raise HandoffError("malformed_handoff: closing fence must sit at column 0")
    return "\n".join(lines[start : closes[0] + 1])


def parse_handoff(block: str) -> Handoff:
    """Parse one fenced block into a validated Handoff.

    Raises HandoffError on ANY deviation: unknown version fence, missing or
    duplicate header, unknown checkpoint_kind, expected_result mismatch with
    the kind, missing/invalid owner_decision for enum_comparison, missing
    payload. Fail-closed: an envelope the dispatcher cannot fully validate
    is a transport failure, not a best-effort guess.
    """
    lines = block.splitlines()
    if not lines or lines[0] != OPEN_FENCE:
        raise HandoffError("malformed_handoff: missing or unknown version fence")
    if lines[-1] != CLOSE_FENCE:
        raise HandoffError("malformed_handoff: missing closing fence")

    headers: dict[str, str] = {}
    payload_lines: list[str] | None = None
    for raw in lines[1:-1]:
        if _is_fence_shaped(raw):
            # parse_handoff enforces the no-fence-inside rule itself, so a
            # caller that skips extract_handoff_block gets the same
            # rejection (codex #527 round-6 P1).
            raise HandoffError(
                "malformed_handoff: fence-shaped line inside the envelope "
                "(the payload must not contain a fence-shaped line)"
            )
        if payload_lines is not None:
            payload_lines.append(raw)
            continue
        if raw.strip() == "payload:":
            payload_lines = []
            continue
        if not raw.strip():
            continue
        m = _HEADER_RE.match(raw)
        if not m:
            raise HandoffError(f"malformed_handoff: unparseable header line {raw!r}")
        key, value = m.group(1), m.group(2).strip()
        if key in headers:
            raise HandoffError(f"malformed_handoff: duplicate header {key!r}")
        headers[key] = value

    for key in _REQUIRED_HEADERS:
        # A value that is blank after Cf-folding (e.g. a zero-width-only
        # correlation_id) is missing, not a stable token (codex #527
        # round-13 P1).
        if key not in headers or _is_blank(headers[key]):
            raise HandoffError(f"malformed_handoff: missing header {key!r}")
    unknown = set(headers) - set(_REQUIRED_HEADERS) - {"owner_decision"}
    if unknown:
        raise HandoffError(f"malformed_handoff: unknown header(s) {sorted(unknown)}")
    if payload_lines is None or _is_blank("\n".join(payload_lines)):
        raise HandoffError("malformed_handoff: missing payload")

    kind = headers["checkpoint_kind"]
    if kind not in CHECKPOINT_KINDS:
        raise HandoffError(f"malformed_handoff: unknown checkpoint_kind {kind!r}")
    expected, enum = CHECKPOINT_KINDS[kind]
    if headers["expected_result"] != expected:
        raise HandoffError(
            f"malformed_handoff: checkpoint_kind {kind!r} requires "
            f"expected_result {expected!r}, got {headers['expected_result']!r}"
        )
    if headers["owner_agent"] != EXPECTED_OWNERS[kind]:
        raise HandoffError(
            f"malformed_handoff: checkpoint_kind {kind!r} is owned by "
            f"{EXPECTED_OWNERS[kind]!r}, not {headers['owner_agent']!r}"
        )

    owner_decision = None
    if expected == "full_return" and "owner_decision" in headers:
        raise HandoffError(
            "malformed_handoff: owner_decision is REQUIRED iff enum_comparison "
            "— a full_return envelope must not carry one"
        )
    if expected == "enum_comparison":
        raw_decision = headers.get("owner_decision", "")
        if not raw_decision:
            raise HandoffError("malformed_handoff: enum_comparison requires owner_decision")
        try:
            owner_decision = _loads_strict(raw_decision)
        except (json.JSONDecodeError, RecursionError, ValueError) as exc:
            # RecursionError: pathologically nested JSON must fail closed
            # like any other malformed input (codex #527 round-7 P1).
            raise HandoffError(f"malformed_handoff: owner_decision is not JSON ({type(exc).__name__})") from exc
        try:
            _validate_structured_decision(owner_decision, enum, who="owner_decision")
        except HandoffError as exc:
            # Owner-side problems are envelope problems, not result problems.
            raise HandoffError(str(exc).replace("malformed_result", "malformed_handoff", 1)) from exc

    return Handoff(
        checkpoint_kind=kind,
        owner_agent=headers["owner_agent"],
        correlation_id=headers["correlation_id"],
        expected_result=expected,
        payload="\n".join(payload_lines),
        decision_enum=enum,
        owner_decision=owner_decision,
    )


def _validate_structured_decision(obj: object, enum: tuple[str, ...], who: str) -> dict:
    """The full #518 output contract: all three fields are REQUIRED —
    `{"decision": "sound"}` alone must not route to a judgment (codex #527
    round-1 P1)."""
    if not isinstance(obj, dict):
        raise HandoffError(f"malformed_result: {who} is not an object")
    decision = obj.get("decision")
    if decision not in enum:
        raise HandoffError(f"malformed_result: {who} decision {decision!r} not in {enum}")
    drivers = obj.get("drivers")
    if (
        not isinstance(drivers, list)
        or len(drivers) > MAX_DRIVERS
        or not all(isinstance(d, str) for d in drivers)
    ):
        raise HandoffError(
            f"malformed_result: {who} drivers must be a list of <= {MAX_DRIVERS} strings"
        )
    confidence = obj.get("confidence")
    if confidence not in CONFIDENCE_VALUES:
        raise HandoffError(f"malformed_result: {who} confidence {confidence!r} invalid")
    return obj


def route_result(handoff: Handoff, transport_ok: bool, raw_result: str | None) -> Routing:
    """The dispatcher's complete outcome routing.

    - transport failure -> UNAVAILABLE (`[CROSS-MODEL-ERROR]`, single-model).
    - enum_comparison: validated result with equal enums -> AGREEMENT_FILL
      (mechanical fill, NO owner re-invocation); differing enums ->
      DIVERGENCE_REINVOKE with the minimum return context; malformed /
      unknown-enum result -> UNAVAILABLE, never fabricated.
    - full_return: every successful response -> FULL_RETURN_REINVOKE (there
      is no comparison the dispatcher could resolve itself).
    """
    if not transport_ok or raw_result is None or _is_blank(raw_result):
        # A blank body is a failed transport, not a critique to hand back
        # (codex #527 round-10 P1).
        return Routing(UNAVAILABLE, error="transport_failure")

    if handoff.expected_result == "full_return":
        return Routing(
            FULL_RETURN_REINVOKE,
            return_context={
                "correlation_id": handoff.correlation_id,
                "owner_agent": handoff.owner_agent,
                "cross_model_response": raw_result,
            },
        )

    try:
        result = _loads_strict(raw_result)
        _validate_structured_decision(result, handoff.decision_enum or (), who="cross_model_result")
    except (HandoffError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        return Routing(UNAVAILABLE, error=f"malformed_result: {type(exc).__name__}: {exc}")

    assert handoff.owner_decision is not None  # guaranteed by parse_handoff
    if result["decision"] == handoff.owner_decision["decision"]:
        return Routing(AGREEMENT_FILL)
    return Routing(
        DIVERGENCE_REINVOKE,
        return_context={
            "correlation_id": handoff.correlation_id,
            "owner_agent": handoff.owner_agent,
            "owner_decision": handoff.owner_decision,
            "cross_model_decision": result,
            "original_payload": handoff.payload,
        },
    )
