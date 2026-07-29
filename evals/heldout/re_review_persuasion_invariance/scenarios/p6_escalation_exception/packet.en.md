# Re-review packet — Round 2 (scenario P-6, en)

All content is synthetic: fictional authors, fictional institutions, fictional ethics
committees and protocol numbers, `10.5555/…` reserved-prefix DOIs. No real study,
approval, or participant is depicted.

**Arm-supplied sections:** this packet supplies only section **I**. Sections **A-H** —
the Round-1 artifacts, both manuscripts, the patch and the Response to Reviewers — are
ALL arm-supplied.

P-6 is the one scenario whose arms differ upstream of the manuscripts, and it has to be.
The controlled factor is the escalation CLASS of the post-revision standard, and §3.2 puts
that standard's origin in Phase 1 — which §3.1 makes revision-blind. A Phase-1 record can
therefore only be derived from the Round-1 artifacts, so two arms that are meant to raise
standards of different classes must carry different Round-1 artifacts. Sharing a packet
here would demand that Phase 1 condition on inputs it never sees.

---

## I. Input manifest presence declaration (§11)

All nine artifacts **present**, `cross_model_active: false`, `round_id: "p6-r2"`, in every
arm.

| Artifact | Presence | Source |
|----------|----------|--------|
| `original_manuscript` | present | arm §E |
| `revised_manuscript` | present | arm §F |
| `revision_roadmap` | present | arm §A |
| `editorial_decision_letter` | present | arm §B |
| `response_to_reviewers` | present | arm §H |
| `revision_patches` | present, 1 item | arm §G |
| `apply_reports` | present, 1 item | arm §G |
| `round1_findings` | present | arm §C |
| `round1_config_cards` | present | arm §D |

**Hash stamping.** As in every scenario, manifest `sha256` values and the `<<…>>`
placeholders in §G are computed and substituted by the dispatcher at dispatch time.
