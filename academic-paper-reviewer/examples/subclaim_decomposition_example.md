# Example: Sub-Claim Decomposition in Editorial Synthesis (§F.3.2 partial-evidence trap)

This example shows the editorial synthesizer's Step 1 → Step 2 → Step 5 flow on a **compound weakness** — the case the §F.3.2 partial-evidence trap exists to catch — and contrasts the old bundle-level aggregation (which buries a minority sub-claim) with the sub-claim decomposition introduced for [#214](https://github.com/Imbad0202/academic-research-skills/issues/214). A later section shows a single-reviewer finding that a DA issue row also reports ([#1098](https://github.com/Imbad0202/academic-research-skills/issues/1098)); it stops at Step 2.

It is a focused illustration of one weakness bundle, not a full Phase 0–2 walkthrough (see `hei_paper_review_example.md` for that).

In the machine-shaped excerpts below, the stable serialized reviewer ID `EIC` maps to the public display role **Journal-Fit Reviewer**.

---

## The input: what the 4 reviewers said about one weakness area

The paper reports a multi-site mixed-effects analysis. Three reviewers raised concerns that **look like "one statistics weakness"** but are actually two distinct claims:

- **R1 (Methodology), Severity: Major, Confidence 5** (anchors: `absence: §3 Methods — expected the random-effects grouping factor; checked §3 Methods, §4 Results` / `table: Table 3 standardized betas vs Table 4 raw coefficients, no key`; competence: core expertise — multi-site mixed-effects design): "Two problems. First, the statistical reporting is inconsistent — Table 3 gives standardized betas, Table 4 raw coefficients, with no key. Second, the mixed-model random-effects grouping is never specified: are sites or participants the grouping factor?"
- **R2 (Domain), Severity: Major, Confidence 4** (anchor: `absence: §3 Methods — expected the grouping variable; checked §3 Methods`; competence: core expertise — quantitative methods in the domain): "I agree the random-effects structure is unclear — the paper doesn't say what the grouping variable is."
- **R3 (Cross-disciplinary), Severity: Major, Confidence 3** (anchor: `table: Tables 3–4 — units shift between tables, no key`; competence: adjacent — reporting clarity, not mixed-model design): "The reporting tables were hard to follow; the units shift between tables."
- **EIC, Confidence 4:** Did not comment on the statistics specifically.

> **Atomicity note (#574 A2/A3):** R1's card bundles two sub-claims into ONE weakness — a fully-conformant current-format card would have emitted them as two separate atomic weaknesses, each with its own single `evidence_anchor` object (Schema 6). Step 1b decomposition is the synthesizer's guard for bundles that still arrive; the two parenthetical anchors above are the bundle's internal evidence, and the transport rows below carry each sub-claim's own anchor.

---

## ❌ Old behavior — bundle-level aggregation (the trap)

The Step 1 inventory collapses this into a single `Key Weaknesses` cell ("statistics problems"), and Step 2 reaches **one** consensus verdict on the bundle:

> **[CONSENSUS-3] Statistics problems** — R1, R2, R3 agree; EIC silent. Author must fix.

What went wrong: the bundle holds **two** sub-claims with **different** support levels, and the verdict averages them into one. "Random-effects grouping unspecified" was raised by R1 *and* corroborated by R2 — a genuine 2-reviewer consensus. "Inconsistent reporting units" was raised by R1 and R3 but is a different defect. Folding both into one "[CONSENSUS-3]" item produces a single roadmap line that lets the author treat the whole thing as one fix, and the precise grouping-factor defect can be lost inside a vague "clean up the statistics" instruction. Partial support read as full resolution.

---

## ✅ New behavior — Step 1b sub-claim inventory, then per-sub-claim consensus

### Step 1b — Weakness Sub-Claim Inventory

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | severity | confidence |
|--------------|-----------------|-------------|----------|------------------|----------|------------|
| SC-1 | Statistics | R1 | raised | `absence: §3 Methods — expected the random-effects grouping factor; checked §3, §4` | major | 5 |
| SC-1 | Statistics | R2 | corroborated | `absence: §3 Methods — expected the grouping variable; checked §3 Methods` | major | 4 |
| SC-1 | Statistics | R3 | not-mentioned | — | — | — |
| SC-1 | Statistics | EIC | not-mentioned | — | — | — |
| SC-2 | Statistics | R1 | raised | `table: Table 3 standardized betas vs Table 4 raw coefficients, no key` | major | 5 |
| SC-2 | Statistics | R3 | corroborated | `table: Tables 3–4 — units shift between tables, no key` | major | 3 |
| SC-2 | Statistics | R2 | not-mentioned | — | — | — |
| SC-2 | Statistics | EIC | not-mentioned | — | — | — |

Two atomic sub-claims fall out of the one "statistics" bundle. `not-mentioned` is recorded as silence, not opposition. Note the severity column: both R1 rows carry the SAME transported severity — they decompose from R1's one "Statistics" weakness, whose single per-finding Severity is inherited by every sub-claim split from it (#574 A3); a severity difference between sub-claims requires different parent weaknesses, never re-rating.

### Step 2 — consensus per sub_claim (denominator = 4 non-DA reviewers)

- **SC-1 (random-effects grouping unspecified):** `agree = 2` (R1 raised, R2 corroborated), `conflict = 0`, `silent = 2` (R3, EIC). Two agree, none conflict → a **corroborated finding** (below the CONSENSUS-3 bar of 3/4), action-bearing because two anchored reviewer rows identify the same major methods defect. Confidence remains uncertainty/scope metadata and does not prioritize the finding. **Not a CONSENSUS-3/4 label; not a SPLIT.**
- **SC-2 (inconsistent reporting units):** `agree = 2` (R1 raised, R3 corroborated), `conflict = 0`, `silent = 2` (R2, EIC) → a **corroborated finding** because two exact table anchors identify the same reporting defect. Confidence remains uncertainty/scope metadata and does not prioritize the finding. **Not a SPLIT.**

Note the threshold discipline: even though every reviewer who *spoke* agreed, neither sub-claim is promoted to CONSENSUS-4 — the consensus denominator is the four non-DA scoring reviewers, not the 2 who spoke, so 2/4 is a corroborated finding, not unanimity. This is exactly the mislabel the absolute-count rule prevents.

Neither sub-claim triggers Journal-Fit Reviewer arbitration — there is no `disputed` position anywhere, so finer granularity did **not** manufacture arbitration load. (Had R2 instead written "the grouping is clearly by site, this is a non-issue," SC-1 would carry a `disputed` position against R1's `raised`, and *then* it would be a genuine SPLIT requiring Journal-Fit Reviewer arbitration.)

### Step 5 — Revision Roadmap (sub-claim-keyed)

Instead of one blurred "fix the statistics" line, two separate, traceable items, kept in source order (Step 5 never orders items by severity, obligation, or cost):

> - **[SC-1]** `obligation_class: must_fix`, `consensus_level: CORROBORATED` — Specify the mixed-model random-effects grouping factor (sites vs participants) and re-state the model. *Severity: major (transported) | Anchor: `absence: §3 Methods — expected the random-effects grouping factor; checked §3 Methods, §4 Results` (transported) | Raised R1 (conf 5), corroborated R2 (conf 4).*
> - **[SC-2]** `obligation_class: should_fix`, `consensus_level: CORROBORATED` — Standardize coefficient reporting across Tables 3–4 (one convention + a key). *Severity: major (transported) | Anchor: `table: Table 3 standardized betas vs Table 4 raw coefficients, no key` (transported) | Raised R1 (conf 5), corroborated R3 (conf 3).*

Each item carries its `sub_claim_id`, traces back to the Step 1b inventory, and flows forward into `academic-paper` revision mode unchanged in format. The minority-risk sub-claim (the grouping factor) is now its own `must_fix` item rather than buried in a bundle. The obligation class is an editorial gate, not a work rank.

---

## A third sub-claim: one seat plus a DA issue row (#1098)

The same paper ends with a funding recommendation built on the pooled model. R3 and the DA speak to a premise of that recommendation:

- **R3 (Cross-disciplinary), Severity: Minor, Confidence 2** (anchor: `absence: §6 Implications — expected who bears the cost of the funding rule; checked §5 Discussion, §6 Implications`; competence: adjacent — policy implications, not funding design): "The recommendation assumes every site gains from the pooled rule. Small sites, which the pooled model underweights, may lose funding, and the paper does not discuss them."
- **DA, MAJOR row, Confidence 4** (competence: core — adversarial challenge of the argument's premises; Dimension: 7 Stakeholder Blind Spots; anchor: `absence: §6 Implications — expected the effect of the rule on small sites; checked §4 Results, §6 Implications`): the recommendation depends on the assumption that all sites benefit, and the paper gives no evidence for it.

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | severity | confidence |
|--------------|-----------------|-------------|----------|------------------|----------|------------|
| SC-3 | Funding premise | R3 | raised | `absence: §6 Implications — expected who bears the cost of the funding rule; checked §5 Discussion, §6 Implications` | minor | 2 |
| SC-3 | Funding premise | R1 | not-mentioned | — | — | — |
| SC-3 | Funding premise | R2 | not-mentioned | — | — | — |
| SC-3 | Funding premise | EIC | not-mentioned | — | — | — |
| SC-3 | Funding premise | DA | raised | `absence: §6 Implications — expected the effect of the rule on small sites; checked §4 Results, §6 Implications` | major | 4 |

- **SC-3 (funding premise unsupported):** `agree = 1` (R3 raised), `conflict = 0`, `silent = 3` (R1, R2, EIC) → a **single-reviewer finding, DA-corroborated**. The DA row is not a vote, so `agree` stays 1 and the denominator stays 4. The finding is evaluated against its criterion and the anchors of both rows. R3's minor and the DA's major are shown side by side; the gap is not a `disputed` position, because the DA is not one of the 4.
- The label shows that the DA also raised the sub-claim. It does not show independent judgement: the seats can share one model, and peer-output blinding does not prove independent errors.
- In the roadmap, the SC-3 item has `consensus_level: SINGLE-REVIEWER`, and the DA row goes into `corroborating_sources[]` with `reviewer: DA`, its major severity, its anchor, and confidence 4 (#1100). The DA row does not change `consensus_level` or `obligation_class`. The decision letter lists SC-3 under Below the Consensus Bar with the DA-corroborated note.

---

## What this example demonstrates (acceptance for #214 and #1098)

- **Step 1b inventory** with `sub_claim` as the primary key, alongside the retained Step 1a summary matrix.
- **Per-sub-claim consensus** in Step 2, with `not-mentioned` correctly excluded from both consensus and SPLIT counting.
- **SPLIT bound respected** — no arbitration is triggered absent an explicit conflicting position (the parenthetical shows what *would* trigger one).
- **Revision Roadmap at sub-claim granularity** — the compound weakness yields two separate, traceable items, each with its own obligation class, instead of one.
- **DA-corroborated label (#1098)** — a single-reviewer finding that a DA issue row also reports keeps `agree = 1` and the denominator of 4, and shows both rows and both severities.
- DA-CRITICAL flow and the v3.6.2 sprint-contract arithmetic path are untouched (neither appears in this general-protocol example).
