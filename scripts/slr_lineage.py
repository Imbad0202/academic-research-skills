#!/usr/bin/env python3
"""#111 slr_lineage resolver — pure function over state_tracker.stages.

Pipeline plumbing helper for the `deep-research systematic-review →
academic-paper full → disclosure --policy-anchor=prisma-trAIce` auto-
dispatch path. The orchestrator persists the resolved value on the
Schema 9 Material Passport at the Stage 1 → Stage 2 handoff; the
disclosure renderer reads it back as `RendererInput.slr_lineage`.

Design: docs/design/2026-05-15-issue-111-slr-lineage-emission-design.md
Contract: policy_anchor_disclosure_protocol.md §3.1 (G2 invariant)
"""
from __future__ import annotations

from typing import Mapping

from policy_anchor_disclosure_referee import SLR_MODES


def resolve_from_stages(stages: Mapping[str, Mapping]) -> bool:
    """Return True iff any stage was produced by deep-research in SLR mode.

    Run-level provenance: the contract is bound to deep-research lineage
    specifically, mirroring the §4.3 G2 invariant track gate. A
    non-deep-research stage with mode='systematic-review' does NOT
    trigger SLR lineage — only the documented producer counts.
    """
    return any(
        (stage.get("skill") == "deep-research")
        and (stage.get("mode") in SLR_MODES)
        for stage in stages.values()
    )
