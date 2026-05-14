#!/usr/bin/env python3
"""#108 policy-anchor disclosure renderer — executable spec / referee.

This module is **not** the production renderer. The production renderer is
LLM-prose at runtime when the user invokes `disclosure` mode with
`--policy-anchor=<a>`. This referee codifies the protocol's deterministic
decision logic — §3 G10 7-row precedence table, §4 auto-promotion
forbiddance, and the per-anchor invariant predicates (G2/G5/G7/G8/G9) — so
that:

1. The conformance test suite (`test_policy_anchor_disclosure.py`) can
   exercise every (input × expected output) combination deterministically.
2. The protocol doc and the referee stay in sync — when the protocol's
   §2 table changes, this module must change with it; the test suite
   catches drift.

References:
- Decision Doc §3 (G10 7-row precedence table), §4.3 (8 invariants),
  §4.4 (11 open concerns).
- `academic-paper/references/policy_anchor_disclosure_protocol.md` §§2-7.
- Implementation spec §3 (resolved-paths table).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

CANONICAL_ANCHORS = ("prisma-trAIce", "icmje", "nature", "ieee")
SLR_MODES = ("systematic-review", "slr")
# Includes the exact label the v3.2 policy database uses
# (venue_disclosure_policies.md §"Venue: Nature (Nature Publishing Group)")
# so consistent pair detection works against the canonical entry name.
# Closes codex round-2 P2 #1.
NATURE_VENUE_NAMES = (
    "Nature",
    "Nature Portfolio",
    "Nature (Nature Publishing Group)",
    "Nature Publishing Group",
)
VALID_CATEGORY_STATES = frozenset({"USED", "NOT USED", "UNCERTAIN"})


class TrackGateError(RuntimeError):
    """Raised when --policy-anchor=prisma-trAIce is selected without
    slr_lineage=true / mode=<slr>. G2 invariant."""


class AutoPromotionForbidden(RuntimeError):
    """Raised when caller attempts to render a still-UNCERTAIN category as
    USED. G3/G10 invariant."""


class PairedMandateViolation(RuntimeError):
    """Raised when IEEE render is asked to emit level_of_involvement
    without affected_sections (or vice versa). G8 invariant."""


class VenueAnchorConflict(RuntimeError):
    """Raised when --venue and --policy-anchor map to incompatible
    placement / phrasing requirements. §4.4 #7."""


class InvalidPolicyAnchor(ValueError):
    """Raised when policy_anchor is outside the canonical 4-anchor enum.
    Closes codex round-1 P2 #3."""


class InvalidCategoryState(ValueError):
    """Raised when a category state value is outside {USED, NOT USED,
    UNCERTAIN}. Closes codex round-2 P2 #2."""


@dataclass(frozen=True)
class RendererInput:
    """Flat runtime input — no corpus-entry-level fields per G1 invariant."""

    ai_used: bool | None = None
    categories: dict[str, str] = field(default_factory=dict)
    policy_anchor: str = "icmje"
    venue: str | None = None
    slr_lineage: bool = False
    mode_param: str | None = None
    tool_type: str = "LLM"
    methodological_in_slr: bool = True
    level_of_involvement: str | None = None
    affected_sections: list[str] | None = None


@dataclass(frozen=True)
class DisclosureDecision:
    """Whole-disclosure decision returned by `decide_disclosure_output`."""

    row: int
    kind: str
    track: str
    used_facets: tuple[str, ...] = ()
    uncertain_facets: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# §3 G10 7-row precedence table
# ---------------------------------------------------------------------------
def decide_disclosure_output(ri: RendererInput) -> DisclosureDecision:
    """Return the G10 7-row decision for the given runtime input.

    Implements the protocol's §2 table exactly: rows evaluated top to
    bottom; first match wins. Concern #10 bare-flag gate evaluated before
    row 4 admits the input.
    """
    _check_policy_anchor_enum(ri)
    _check_category_states(ri)
    _check_venue_anchor_conflict(ri)
    _check_track_gate(ri)

    used = {k for k, v in ri.categories.items() if v == "USED"}
    uncertain = {k for k, v in ri.categories.items() if v == "UNCERTAIN"}
    not_used = {k for k, v in ri.categories.items() if v == "NOT USED"}

    track = "prisma-trAIce" if ri.policy_anchor == "prisma-trAIce" else ri.policy_anchor

    # Row 1: ai_used=false AND ≥1 USED (contradiction)
    if ri.ai_used is False and used:
        return DisclosureDecision(row=1, kind="conflict_annotation", track=track)

    # Row 2: ai_used=false AND no USED AND no UNCERTAIN
    if ri.ai_used is False and not used and not uncertain:
        return DisclosureDecision(row=2, kind="no_ai_statement", track=track)

    # Row 3: ai_used=false AND ≥1 UNCERTAIN AND no USED
    if ri.ai_used is False and uncertain and not used:
        return DisclosureDecision(row=3, kind="tension_annotation", track=track)

    # Concern #10 substantive-content gate: bare ai_used=true with no USED
    # category supplied → force v3.2 categorization flow rather than row 4
    if ri.ai_used is True and not used:
        return DisclosureDecision(
            row=4,
            kind="prompt_for_categorization",
            track=track,
            uncertain_facets=tuple(sorted(uncertain)),
        )

    # Row 4: (ai_used=true OR ≥1 USED) AND row 1 didn't match
    if (ri.ai_used is True or used) and not (ri.ai_used is False and used):
        return DisclosureDecision(
            row=4,
            kind="anchor_render",
            track=track,
            used_facets=tuple(sorted(used)),
            uncertain_facets=tuple(sorted(uncertain)),
        )

    # Row 5: ≥1 UNCERTAIN AND no USED AND ai_used unset
    if uncertain and not used and ri.ai_used is None:
        return DisclosureDecision(row=5, kind="not_supplied_annotation", track=track)

    # Row 6: All NOT USED AND no UNCERTAIN AND ai_used unset (silence)
    if not_used and not uncertain and not used and ri.ai_used is None:
        return DisclosureDecision(row=6, kind="silence", track=track)

    # Row 7: empty input across every dimension
    return DisclosureDecision(row=7, kind="not_supplied_annotation", track=track)


def _check_policy_anchor_enum(ri: RendererInput) -> None:
    """Validate policy_anchor membership against the canonical closed enum
    before any other decision logic runs. Closes codex round-1 P2 #3:
    invalid anchor values must not fall through to a render path that has
    no table / protocol entry."""
    if ri.policy_anchor not in CANONICAL_ANCHORS:
        raise InvalidPolicyAnchor(
            f"policy_anchor='{ri.policy_anchor}' is not in the canonical "
            f"closed enum {CANONICAL_ANCHORS}. Selectors are case-sensitive "
            "and must match exactly."
        )


def _check_category_states(ri: RendererInput) -> None:
    """Validate every v3.2 category state against the closed
    {USED, NOT USED, UNCERTAIN} enum. Silent fall-through to row 6/7 on a
    lowercase typo would change the disclosure decision; the protocol
    requires explicit rejection. Closes codex round-2 P2 #2."""
    invalid = {
        k: v for k, v in ri.categories.items() if v not in VALID_CATEGORY_STATES
    }
    if invalid:
        raise InvalidCategoryState(
            f"category states must be in {sorted(VALID_CATEGORY_STATES)}; "
            f"got invalid entries {invalid}"
        )


def _check_venue_anchor_conflict(ri: RendererInput) -> None:
    """Concern #7 resolution: reject conflicting selectors with explicit
    error; the only currently defined consistent pair is Nature venue with
    nature anchor. Every other (venue, anchor) combination raises so silent
    precedence is impossible. Closes codex round-1 P2 #2."""
    if ri.venue is None or ri.policy_anchor is None:
        return
    # Consistent: Nature venue with nature anchor.
    if ri.venue in NATURE_VENUE_NAMES and ri.policy_anchor == "nature":
        return
    # All other combinations where both selectors are supplied are
    # rejected by default. To add a new compatible pair, extend the
    # consistent-pair check above explicitly. Silent precedence is
    # forbidden per §4.4 #7.
    raise VenueAnchorConflict(
        f"venue='{ri.venue}' and --policy-anchor='{ri.policy_anchor}' map to "
        "different (or unmapped) placement / phrasing requirements. The only "
        "currently defined consistent pair is venue ∈ "
        f"{NATURE_VENUE_NAMES!r} with policy_anchor='nature'. Drop one "
        "selector or reconcile."
    )


def _check_track_gate(ri: RendererInput) -> None:
    """G2 invariant: --policy-anchor=prisma-trAIce requires SLR lineage."""
    if ri.policy_anchor != "prisma-trAIce":
        return
    if ri.slr_lineage:
        return
    if ri.mode_param and ri.mode_param in SLR_MODES:
        return
    raise TrackGateError(
        "policy_anchor='prisma-trAIce' requires slr_lineage=True (pipeline) "
        "or mode_param='systematic-review' (cold-start). Silent fallback to "
        "general track is forbidden by §4.3 G2 invariant."
    )


# ---------------------------------------------------------------------------
# §4 auto-promotion forbiddance + helpers
# ---------------------------------------------------------------------------
def render_facet_as_used(category_state: str) -> str:
    """Render a single facet at USED strength — raises if input is still
    UNCERTAIN. Encodes the G3/G10 forbiddance as an executable invariant."""
    if category_state == "UNCERTAIN":
        raise AutoPromotionForbidden(
            "category state UNCERTAIN MUST NOT be rendered as USED. "
            "See §4.3 G3/G10 invariant and concern #6 resolution."
        )
    if category_state == "USED":
        return "<full-strength facet render>"
    return "<no render>"


# ---------------------------------------------------------------------------
# G5 invariant — three-gate prompt disclosure predicate
# ---------------------------------------------------------------------------
def prompt_disclosure_required(
    track: str, tool_type: str, methodological_in_slr: bool
) -> bool:
    """True iff all three G5 gates hold."""
    if track != "prisma-trAIce":
        return False
    if tool_type not in {"LLM", "GenAI"}:
        return False
    if not methodological_in_slr:
        return False
    return True


# ---------------------------------------------------------------------------
# G7 invariant — anchor-specific carve-out semantics
# ---------------------------------------------------------------------------
def copyediting_carveout_semantics(anchor: str) -> str:
    """Return the per-anchor copyediting carve-out semantics tag.

    Values: 'eliminate' (Nature) / 'downgrade' (IEEE) / 'out_of_scope'
    (PRISMA-trAIce) / 'not_addressed' (ICMJE).
    """
    return {
        "nature": "eliminate",
        "ieee": "downgrade",
        "prisma-trAIce": "out_of_scope",
        "icmje": "not_addressed",
    }[anchor]


# ---------------------------------------------------------------------------
# G8 invariant — IEEE #5 + #6 paired mandate
# ---------------------------------------------------------------------------
def assert_ieee_pairing_conformant(
    level_of_involvement: str | None, affected_sections: list[str] | None
) -> None:
    """Raise PairedMandateViolation if one is supplied without the other."""
    has_level = bool(level_of_involvement)
    has_sections = bool(affected_sections)
    if has_level != has_sections:
        raise PairedMandateViolation(
            "IEEE #5 (level_of_involvement) and IEEE #6 (affected_sections) "
            "are a paired mandate. Emit both together or neither. See "
            "§4.3 G8 invariant + impl spec concern #4 resolution."
        )


# ---------------------------------------------------------------------------
# G9 invariant — anchor-specific image-rights regimes (distinct, not unified)
# ---------------------------------------------------------------------------
def image_rights_regime(anchor: str) -> str:
    """Return the per-anchor image-rights regime tag."""
    return {
        "prisma-trAIce": "data_handling_adjacency",
        "icmje": "text_attribution_no_ai_primary",
        "nature": "default_deny_with_carveouts",
        "ieee": "acknowledgments_only",
    }[anchor]


# ---------------------------------------------------------------------------
# §4.4 #5 Nature hybrid image outputs
# ---------------------------------------------------------------------------
def nature_image_outputs(images: Iterable[dict]) -> dict[str, list[dict]]:
    """Return the hybrid two-channel output structure for the Nature anchor.

    Channel 1: annotation_block — per-image instructions describing carve-out
    classification and required Nature label text.
    Channel 2: suggested_patch — patch diff against manuscript source figure
    metadata (caption / alt-text / image-field caption).

    The renderer does NOT emit inline_modification — ARS does not modify
    manuscript source autonomously per impl spec concern #5 resolution.
    """
    images = list(images)
    annotation_block = []
    suggested_patch = []
    for img in images:
        if not img.get("ai_generated"):
            continue
        annotation_block.append(
            {"image_id": img["id"], "label": "AI-generated (Nature default-deny carve-out evaluation required)"}
        )
        suggested_patch.append(
            {
                "image_id": img["id"],
                "diff": "<suggested figure-metadata caption patch — apply at author discretion>",
            }
        )
    return {
        "annotation_block": annotation_block,
        "suggested_patch": suggested_patch,
    }
