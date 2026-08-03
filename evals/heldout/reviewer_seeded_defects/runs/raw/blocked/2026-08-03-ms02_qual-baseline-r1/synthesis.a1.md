# Editorial Decision Package

## Mechanical Contract Emission (v3.6.2 Sprint Contract Synthesizer Protocol)

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · panel_size 5

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | eligible_roles | Assessed eligible seats | Scores | Dimension verdict | Fatal declared |
|-----|----------|----------------|-------------------------|--------|-------------------|----------------|
| D1 | mandatory | methodology | methodology | block (repairable) | block | no |
| D2 | mandatory | domain | domain | block (repairable) | block | no |
| D3 | mandatory | da, methodology | da, methodology | block (repairable), block (repairable) | block | no |
| D4 | high | perspective | perspective | block (no block_class field) | block | no |
| D5 | normal | eic | eic | block (no block_class field; card states no fatality class attaches) | block | no |
| D6 | mandatory | eic | eic | block (repairable) | block | no |

All `not_assessed` values from ineligible seats were excluded from every numerator and denominator. No dimension was unassessed by its eligible seats; no abstentions were recorded.

`audit_verdict: block` (worst assessed eligible score; no fatal block declared by any assessed eligible seat)

### Step 2 — failure_conditions evaluation

| condition_id | severity | expression | Per-dimension evaluation | fired |
|---|---|---|---|---|
| F1 | 95 | any mandatory dimension has a fatal block | D1/D2/D3/D6: no seat declared a fatal block (all declared `repairable`) | false |
| F2 | 90 | any mandatory dimension scores 'block' | `any`: D1 ✓, D2 ✓, D3 ✓, D6 ✓ → `any` over mandatory = true | **true** |
| F3 | 70 | two or more mandatory dimensions score 'warn' or worse | `majority`: D1 (n=1, owner) ✓, D2 (n=1, owner) ✓, D3 (n=2, both) ✓, D6 (n=1, owner) ✓ → 4 ≥ 2 | **true** |
| F4 | 60 | any high-priority dimension scores 'block' | `any`: D4 ✓ | **true** |
| F5 | 40 | any dimension scores 'warn' or worse | `any`: D1–D6 all ✓ | **true** |
| F0 | 10 | every dimension scores 'pass' | `all`: D1 ✗ | false |

### Step 3 — Precedence, decision, audit emission

Highest-severity fired condition: **F2 (severity 90)** → `editorial_decision=major_revision`.

```
dimension_verdicts: [D1=block, D2=block, D3=block, D4=block, D5=block, D6=block]
fired_conditions: [F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED]
editorial_decision=major_revision
```

No `[DA-CRITICAL-VS-ACCEPT]` marker: the mechanical decision is not `accept`. No rejection-rationale lines: no DA CRITICAL was adjudicated REJECTED.

### Panel card integrity notes (flagged, not fixed)

- `[CARD-INCOMPLETE: eic W4 — per-finding Confidence absent]`. No report-level Confidence Score exists on the eic card either, so no fallback value is available; the SC-11 row is marked `[CONFIDENCE-SOURCE: unavailable]`.
- `[CARD-FORMAT-GAP: eic D5, perspective D4 — no block_class field]`. Neither card declares a fatal block; both were therefore scored non-fatal, which is the reading the eic card states in prose. Recorded so the field's absence is visible rather than silently normalised.
- `[PHASE1-PREREQ-NOT-VISIBLE]`: `measurement_procedure.reviewer_must_output_before_paper` requires `contract_paraphrase` and `scoring_plan` from each seat. Those sections are not present in the material supplied to me (only the two "Scoring Plan Dissent — omitted" placeholders are). I cannot tell whether they were emitted in Phase 1 and truncated from my input, or never emitted. Flagging, not fixing.
- Optional cross-model blind decision check (#518) was not triggered: no `ARS_CROSS_MODEL` signal and no consent-gate pass in the invocation.

---

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this is `reviewer_full` mode, so this block is mandatory and must carry exactly one of the three permitted statements (cross-model slot active / single-family disclosure / dispatch-failure fallback). The dispatching layer supplied no provenance stamp with the five reviewer cards. I will not infer which model family ran which seat, and I will not imply model independence that may not have existed. **This letter must not ship until the dispatching layer fills this block.**

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript "Building Institutional Quality Culture: Administrator Perspectives on Quality Assurance Implementation in Universities." It was assessed by five reviewers: a Journal-Fit Reviewer, three peer reviewers (methodology, higher-education/QA domain, cross-disciplinary organizational sociology), and a Devil's Advocate seat.

### Decision: Major Revision

### Consensus Analysis

The panel is unusually convergent. Every reviewer scored a block on the dimension they own, no reviewer declared a fatal block, and all five identified an overlapping set of defects. There is no reviewer in this panel who thinks the manuscript is close to publishable, and none who thinks the underlying study is unsalvageable.

#### Sub-claim inventory (Step 1b, compressed)

Weakness bundles were decomposed into atomic sub-claims before consensus was computed, so that a compound weakness whose parts reached different support levels produces separately prioritised roadmap items. Positions are recorded per (sub-claim, reviewer); the four non-DA seats are the denominator throughout. Format: `seat position (transported Severity / per-finding Confidence)`. `—` = not-mentioned (silence, not opposition).

| ID | Parent weakness | Positions (EIC / R1 methodology / R2 domain / R3 perspective) | DA | Agree/Conflict | Disposition |
|----|-----------------|---------------------------------------------------------------|----|----------------|-------------|
| SC-1a | 10.5555 DOI prefix | EIC raised (Critical/5) · R1 — · R2 corroborated (Minor/3) · R3 — | — | 2/0 | corroborated finding |
| SC-1b | Verification as pre-decision gate | EIC raised (Critical/5) · R1 — · R2 **disputed** (Minor/3) · R3 — | — | 1/1 | **[SPLIT]** |
| SC-2 | Anonymity vs identifying attribution | EIC raised (Critical/5) · R1 corroborated (Critical/5) · R2 corroborated (Minor/4, self-declared deference to R1's banding) · R3 corroborated (Critical/5) | C3 | 4/0 | **[CONSENSUS-4]** |
| SC-3 | Disconfirming cases excluded by the structure they should test | EIC raised (Critical/4) · R1 raised (Critical/5) · R2 corroborated (Major/4) · R3 corroborated (Critical/4) | C2 | 4/0 | **[CONSENSUS-4]** |
| SC-4 | "Balanced representation / full range" claim is false on the paper's own account | EIC raised (Critical/4) · R1 raised (Critical/5) · R2 corroborated (Major/4) · R3 corroborated (Critical/4) | C2 | 4/0 | **[CONSENSUS-4]** |
| SC-5 | Required remedy for the exclusion | EIC corroborated (Critical/4) · R1 raised (Critical/5) · R2 **disputed** (Major/4) · R3 corroborated (Critical/4) | C2 | 3/1 | **[SPLIT]** |
| SC-6 | §5 inverts Delacroix (2018) | EIC raised (Major/5) · R1 corroborated (Major/5) · R2 raised (Critical/5) · R3 corroborated (Major/4) | C1 | 4/0 | **[CONSENSUS-4]** |
| SC-7 | Correct reading undercuts the recommendation; must be re-derived, not re-cited | EIC corroborated (Major/5) · R1 corroborated (Major/5) · R2 raised (Critical/5) · R3 corroborated (Major/4) | C1 | 4/0 | **[CONSENSUS-4]** |
| SC-8 | Sector-wide generalisation from 3 sites / 1 system | EIC raised (Major/5) · R1 raised (Major/5) · R2 corroborated (Major/4) · R3 raised (Major/5) | M2 | 4/0 | **[CONSENSUS-4]** |
| SC-9 | §5's generalisation is internally retracted by §6 | EIC raised (Major/5) · R1 — · R2 corroborated (Major/4) · R3 — | — | 2/0 | corroborated finding |
| SC-10 | Claim rescoping alone is insufficient; new analytic work required | EIC raised (Major/4) · R1 corroborated (Critical/5) · R2 corroborated (Major/5) · R3 corroborated (Major/5) | — | 4/0 | **[CONSENSUS-4]** |
| SC-11 | "Quality culture" never operationally defined | EIC raised (Major/`[CONFIDENCE-SOURCE: unavailable]`) · R1 — · R2 raised (Major/4) · R3 raised (Major/4) | — | 3/0 | **[CONSENSUS-3]** (silent: R1) |
| SC-12 | M=3.9 uninterpretable — no instrument, scale, anchors, reliability | EIC corroborated (Minor/5) · R1 raised (Major/5) · R2 corroborated (Major/4) · R3 raised (Major/4) | M9 | 4/0 | **[CONSENSUS-4]** |
| SC-13 | Unidimensional score incommensurable with the field's constructs | EIC — · R1 — · R2 raised (Major/4) · R3 — | — | 1/0 | single-reviewer finding |
| SC-14 | p<.05 with no test, statistic, effect size, CI; n=9 vs n=11 | EIC corroborated (Minor/5) · R1 raised (Major/5) · R2 corroborated (Minor/—, routed to R1) · R3 corroborated (Major/4) | M5 | 4/0 | **[CONSENSUS-4]** |
| SC-15 | Survey sample unreconstructable; 28 of 48 unaccounted | EIC corroborated (Minor/5) · R1 raised (Major/4) · R2 corroborated (routed to R1) · R3 corroborated (Major/4) | M5 | 4/0 | **[CONSENSUS-4]** |
| SC-16 | Abstract 14 vs §3.2 12 | EIC raised (Major/5) · R1 raised (Major/5) · R2 corroborated (Minor/5) · R3 corroborated (Minor/5) | M1 | 4/0 | **[CONSENSUS-4]** |
| SC-17 | §4.1 "structured protocol" contradicts §3.1/§3.3 | EIC raised (Major/4) · R1 raised (Major/5) · R2 — · R3 corroborated (Minor/4) | M4 | 3/0 | **[CONSENSUS-3]** (silent: R2) |
| SC-18 | Protocol uniformity would manufacture convergence, not exclude artifact | EIC — · R1 — · R2 — · R3 raised (Minor/4) | M4 | 1/0 | single-reviewer finding |
| SC-19 | Qualitative analytic procedure unreportable (no codebook, coder count, trustworthiness) | EIC — (explicit deference) · R1 raised (Critical/5) · R2 — · R3 — | — | 1/0 | single-reviewer finding — **D1 block-trigger driver** |
| SC-20 | Prevalence/saturation language uncalibrated | EIC — · R1 raised (Minor/4) · R2 — · R3 — | M7 | 1/0 | single-reviewer finding |
| SC-21 | No reproducibility affordances | EIC — · R1 raised (Minor/5) · R2 — · R3 — | — | 1/0 | single-reviewer finding |
| SC-22 | Constitutive QA/quality-culture literature absent; "still emergent" misdescribes the field | EIC raised (Major/4) · R1 — · R2 raised (Major/5) · R3 — | — | 2/0 | corroborated finding — **D2/D6 block-trigger driver** |
| SC-23 | "First comprehensive account" contradicted by the paper's own bibliography | EIC raised (Major/4) · R1 corroborated (Major/5) · R2 raised (Major/4) · R3 corroborated (Minor/4) | M2 | 4/0 | **[CONSENSUS-4]** |
| SC-24 | Defensible contribution is narrower: identity-in-the-gap + level divergence | EIC raised (—) · R1 — · R2 raised (—) · R3 raised (—) | — | 3/0 | **[CONSENSUS-3]** (silent: R1) |
| SC-25 | Central mechanism (decoupling / ceremonial conformity) never named or theorised | EIC — · R1 — · R2 corroborated (audit-culture canon, Major/5) · R3 raised (Major/5) | — | 2/0 | corroborated finding — **D4 block-trigger driver** |
| SC-26 | "Distributed leadership" / "identity work" used as labels only | EIC — · R1 — · R2 — · R3 raised (Major/5) | — | 1/0 | single-reviewer finding |
| SC-28 | Three-party negotiation claim rests on one party's data | EIC — · R1 — · R2 — · R3 raised (Major/5) | — | 1/0 | single-reviewer finding — **D4 block-trigger driver** |
| SC-29 | Administrator/staff divergence deferred rather than analysed | EIC — · R1 corroborated (Major/5) · R2 — · R3 raised (Major/4) | — | 2/0 | corroborated finding |
| SC-30 | Divergence mislabelled as corroboration; no integration procedure | EIC — · R1 raised (Major/5) · R2 — · R3 raised (Major/4) | M3 | 2/0 | corroborated finding |
| SC-31 | No numbered table or figure anywhere | EIC raised (Minor/5) · R1 — · R2 — · R3 — | — | 1/0 | single-reviewer finding |
| SC-32 | National QA regime never identified | EIC — · R1 — · R2 raised (Minor/3) · R3 — | — | 1/0 | single-reviewer finding |
| SC-33 | ~2,400 words against venue norm | EIC raised (Major/4) · R1 — · R2 — · R3 — | — | 1/0 | single-reviewer finding — **D6 block-trigger driver** |
| SC-34 | "Coping resource" inferred from self-presentational talk alone | (no non-DA seat) | M8 | 0/0 | DA-only MAJOR |
| SC-35 | Pettersen/Rahman cited in §2, never engaged in §4–§5 | EIC — · R1 — · R2 corroborated (Major/4) · R3 — | M6 | 1/0 | single-reviewer + DA |

Decomposition discipline: every sub-claim above traces to a weakness a reviewer actually raised. No sub-claim was authored by this desk. Severity and confidence are transported from the cards, not re-derived.

Surface-form parity check (#216) applied at arbitration: no sub-claim's weight was adjusted for the formality, technicality, or vagueness of its phrasing. I ran the opposite-style counterfactual on the two SPLITs and on the single-reviewer findings promoted to Priority 1; in each case the weight tracks paper evidence and dimension ownership, not wording. R2's deliberately restrained banding of the ethics and DOI issues was not read as weak evidence, and R3's more theoretically-loaded phrasing was not read as corroboration.

#### Points of Agreement (Consensus)

- **[CONSENSUS-4]** SC-2 — §3.5's anonymisation guarantee is falsified by §4.1/§4.2 attributions that identify individual post-holders by role plus institution, attached to professionally damaging speech.
- **[CONSENSUS-4]** SC-3, SC-4 — dissenting participants were removed because they fell outside the three-theme structure, in the same paragraph that claims full-range coverage. The exclusion criterion is the analytic outcome; the coverage claim is refuted by its own next sentence.
- **[CONSENSUS-4]** SC-6, SC-7 — §5 attributes to Delacroix (2018) the opposite of what §2 and the reference annotation attribute to him, and the reversed reading carries the paper's only practical recommendation. Three seats add that the paper's own ritual-compliance finding is evidence *for* Delacroix's actual argument.
- **[CONSENSUS-4]** SC-8, SC-23 — the sector-level generalisation and the "first comprehensive account" priority claim exceed a three-site, single-system, twelve-interview design; the priority claim is undercut by the paper's own §2.
- **[CONSENSUS-4]** SC-10 — claim rescoping alone will not repair the manuscript; substantive new analytic work is required. This is worth stating plainly, because the anticipated EIC↔R1 disagreement on this point did not materialise: R1 explicitly abandoned the "missing procedure is a write-up problem" reading after §4.3, and both seats land on repairable-but-substantial.
- **[CONSENSUS-4]** SC-12, SC-14, SC-15, SC-16 — the survey cannot be interpreted as printed (no instrument, scale, anchors, reliability), the inferential subgroup claim has no supporting apparatus, the survey sample cannot be reconstructed (20 of 48 accounted for), and the interview N contradicts itself between abstract and Methods.
- **[CONSENSUS-3]** SC-11 (silent: R1) — "quality culture" is never operationally defined and circulates as a near-synonym of quality assurance, institutional culture, and compliance behaviour.
- **[CONSENSUS-3]** SC-17 (silent: R2) — §4.1's "structured protocol" contradicts the semi-structured design, and it is the only place the paper argues its themes travel across sites.
- **[CONSENSUS-3]** SC-24 (silent: R1) — the defensible contribution is narrower and more interesting than the one claimed: administrators holding the compliance/meaning gap open, plus the administrator/staff perceptual divergence.

#### Points of Disagreement

**[SPLIT] SC-1b — Does reference verification gate this decision letter?**

- **Journal-Fit Reviewer**: all twelve DOIs sit on the reserved `10.5555/` test prefix, numbered consecutively in first-author alphabetical order across eleven journals and one monograph publisher. No cited source can be verified; therefore no recommendation, *including* a revise recommendation, should issue until resolvable identifiers are supplied (Critical, confidence 5). This drives the D5 block.
- **R2 (Domain)**: the prefix status is a matter of fact and is treated as a production or anonymisation artifact; R2 explicitly declines to infer fabrication and bands it Minor (confidence 3), with the remedy being supply of resolvable identifiers during revision.
- Disagreement type: severity plus procedure. Both seats agree on the observable fact and both explicitly decline the fabrication inference.
- **Editor's Resolution — partly resolved, partly unresolved, and I am separating the two halves.**
  - *Gating question — resolved:* this letter issues now. The `major_revision` action follows from F2, fired by blocks on D1, D2, D3, and D6 whose drivers are all internal contradictions in the submitted text — the §4.3 exclusion, the §5-versus-§2 Delacroix reversal, the unreportable analytic procedure, the contribution increment. Not one of them depends on external source verification. Withholding the letter would delay repairs every seat requires without changing what those repairs are. R2's expertise governs here in a narrow sense: the two seats' *actions* are compatible, and only the banding differs.
  - *Integrity question — unresolved, and recorded as such.* Neither seat could verify the references, and neither claims to have established fabrication. Under the unresolved-dissent principle I neither dismiss the Journal-Fit Reviewer's concern nor convert it into a finding of misconduct. It is escalated to the editorial office as a research-integrity check, and it becomes a hard precondition on re-review: **R10 must be satisfied before the panel's source-fidelity findings (R3, R6) can be treated as final.** Until then, every fidelity finding in this letter is provisional, and the authors should understand that correcting §5's Delacroix reading may not be the end of that matter.

**[SPLIT] SC-5 — What remedy does the §4.3 exclusion require?**

- **R1 (Methodology, D1 owner)**: reinstate the negative cases and re-analyse; report their bearing on each theme; do this *before* addressing the reporting gaps, because restoring the cases may change what the themes are (Critical, confidence 5).
- **R3 (Perspective)**: no reanalysis of the reported themes can proceed until the excluded material is reinstated and reported (Critical, confidence 4).
- **Journal-Fit Reviewer**: the evidence base itself must be reconstituted; this is part of why rescoping the claims cannot repair the contribution (Critical, confidence 4).
- **R2 (Domain)**: offers an alternative — *either* report the dissenting accounts as a fourth position, *or* state plainly that the analysis characterises a subset and revise the interpretive claims accordingly (Major, confidence 4).
- Disagreement type: direction of remedy. R2's second option is materially weaker than reinstatement.
- **Editor's Resolution — R1's position binds, with R2's reporting form adopted.** The reinstatement requirement stands, and the "characterises a subset" option is declined. The rationale is not seat authority but R2's own text: R2 states that removing the dissenting accounts makes the meaning-recovery finding "partly an artifact of case selection at the analytic stage." A disclosure that the analysis covers a subset does not remove that artifact — it discloses it while leaving the three-theme structure validated against a corpus pruned to produce it. On evidence, therefore, R2's stronger option is the only one of the two that reaches the defect R2 identifies. R2's "fourth position" formulation is adopted as the reporting form for the reinstated cases, since resistance to the QA enterprise is a constitutive category in the field's quality-culture typologies rather than residual noise. Expertise is a secondary consideration and points the same way: D1 is R1's dimension, and R2 twice states that analytic and sampling adequacy are R1's judgement.

**Complementarity, not conflict — R2 ↔ R3 on which literature is missing (editorial sizing direction).** R2 requires the field's constitutive QA literature (EUA Quality Culture Project's structural/cultural distinction, Harvey & Green, Harvey & Stensaker's typology, Newton, the audit-culture canon). R3 requires the organizational-theory vocabulary that names the mechanism the findings describe (means-ends decoupling, ceremonial conformity, audit society, reactivity, recoupling). Neither disputes the other; both absences are real and they are not substitutes. R3 volunteered a self-limit and asked that the prescription be scaled to the venue rather than to zero. I adopt that: for a QA-practitioner readership, R2's literature carries the depth (positioning, definition, typology), and R3's is applied at the volume R3 named — roughly two paragraphs in §2 plus a reframing of §5's second finding from a population claim to a mechanism claim with stated scope conditions. Both are folded into R6. This is arbitration of the panel's existing recommendations, not a new requirement.

**Preserved against the weight of criticism.** Four critical reviews can bury a real signal. The panel is unanimous that two things here are worth building on. First, the gap statement: administrators as the hinge between external requirement and internal practice is a specific structural position rather than a topic gesture, it names its nearest prior treatment honestly (Silva & Tan 2021), and it is the reason the Journal-Fit Reviewer scored D6 repairable rather than fatal. Second, §4.3's observation that administrators do not resolve the compliance/meaning tension but inhabit it — three seats independently identify this as the paper's best analytic move and the one finding not already covered by the paper's own cited literature, and R3 notes it is also the finding that travels furthest beyond higher education. R1 additionally credits the declared strand priority, the maximum-variation site logic, and the candour of reporting a survey result that ran against expectation. Build the revised paper around the identity-in-the-gap reading and the level divergence; do not respond to this letter by pruning the paper down to what survives.

### Decision Rationale

Major Revision follows mechanically from the contract: blocks on all four mandatory dimensions fired F2 at severity 90, and F3, F4, and F5 fired beneath it. No seat declared a fatal block, so F1 did not fire and rejection is not the contract's action. That arithmetic matches the panel's substantive reading. The study's object is well chosen, the interview material is vivid, one analytic move is genuinely original, and every seat judged the defects repairable without new fieldwork.

What makes this more than a heavy revision is that three of the defects are not omissions but assertions the manuscript's own text contradicts. §4.3 claims full-range coverage in the sentence after declaring that non-conforming cases were removed. §5 recruits Delacroix for the position §2 correctly reports him attacking, and builds the paper's only practical recommendation on the reversal. §3.5 guarantees that no individual could be identified, and §4.1 identifies one. These are not softenable by rewording; each requires work that may change what the paper reports. The three Devil's Advocate CRITICAL challenges name exactly these three, all three were independently corroborated by every non-DA seat, and all three are adjudicated VALIDATED.

Two further blocks are not in the top three but are equally unresolved and equally required: the qualitative analytic procedure is unreportable from §3.4 (D1's stated trigger), and the contribution increment, read against the paper's own bibliography, is three replicated themes plus one undeveloped paragraph (D6). The authors should not read a three-row blocking table as the full set of conditions.

Re-review will be required, minimally by the methodology and domain seats.

### Top Blocking Issues (0–3, ranked)

Ordering basis: potential for harm to identifiable third parties first, then defects that void the paper's core empirical claim, then defects that void its stated practical contribution.

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | The stated anonymisation guarantee is falsified by role-plus-institution attributions of career-relevant speech; consent was obtained on the guarantee's terms | EIC, R1, R2, R3, DA (C3) | text: §3.5 / §4.1 "all data were fully anonymized prior to analysis so that no individual could be identified" vs "the quality director of the largest private university in the region" | R2 |
| 2 | The three-theme structure was validated against a corpus from which non-conforming cases were removed, while the paper claims full-range coverage | R1, EIC, R2, R3, DA (C2) | text: §4.3 "these were excluded for space, as they fell outside the three-theme structure that organized our analysis" alongside "capturing the full range of administrator views" | R1 |
| 3 | The sole practical recommendation rests on a 180-degree inversion of Delacroix (2018), whose actual argument the paper's own findings support | R2, EIC, R1, R3, DA (C1) | text: §5 "who recommends that institutions treat broad stakeholder consultation as the central mechanism" vs §2 "argues *against* treating stakeholder consultation as sufficient evidence of a healthy quality culture" | R3 |

### Devil's Advocate CRITICAL adjudications

| ID | DA challenge | Corroborated by | Journal-Fit / editorial assessment | Required author response |
|----|--------------|-----------------|------------------------------------|--------------------------|
| C1 | Central design recommendation attributed to a source the paper reports as arguing the opposite; the correct reading problematises the recommendation | All four non-DA seats (EIC W7, R1 W10, R2 W1, R3 W7) | **VALIDATED.** The contradiction is internal to the manuscript and verifiable without external checking; R2, who owns D2, independently identifies the same reversal and reaches the stronger conclusion that the paper's data currently argue against its own recommendation | R3 — re-derive the design implication from Delacroix's actual argument; do not merely re-cite |
| C2 | Comprehensiveness claimed in the same paragraph that declares selection on the analytic outcome | All four non-DA seats (EIC W3, R1 W1, R2 W6, R3 W6) | **VALIDATED.** Stated by the authors in adjacent sentences; R1 (D1 owner) bands it Critical at confidence 5 and identifies it as the reason the manuscript is not repairable by fuller reporting alone | R1 — reinstate and analyse the excluded cases; withdraw the coverage claim |
| C3 | Methods anonymisation guarantee contradicted by uniquely identifying Findings attributions | All four non-DA seats (EIC W2, R1 W3, R2 W9, R3 W5) | **VALIDATED.** R3 assessed this as a former research-ethics committee member reviewing exactly this problem class; R1 and EIC concur at confidence 5. R2's Minor banding is explicit deference on ethics, not dissent | R2 — revise attribution conventions or document consent scope; correct §3.5 |

No DA CRITICAL was rejected. This adjudication is visibility and arbitration, not a veto: the three validated challenges did not change the mechanical decision, which F2 had already set.

### Required Item Details

**R1 — Reinstate the excluded cases and re-derive the thematic structure.**
Reinstate every dissenting or sceptical participant excluded at §4.3, report their bearing on each of the three themes, revise or replace the theme structure as the reinstated corpus requires, and delete the "balanced representation … full range of administrator views" claim. Report the dissenting accounts as a distinct position rather than as residual material. Do this first, because it may change what the themes are.
- **Acceptance criteria**: All previously excluded cases are analysed and reported; each theme states how the dissenting cases bear on it; no coverage or representativeness claim remains that the reported corpus does not support.

**R2 — Resolve the anonymity conflict.**
Remove superlative and role-plus-institution descriptors throughout §4 (including "the quality director of the largest private university in the region," "the associate dean for quality at the public research university," and "one registry head" where institution is inferable), or state explicitly what the consent covered regarding attributed quotation. Restate §3.5 to what the reporting actually achieves.
- **Acceptance criteria**: No quotation is attributable to an identifiable individual by role, institution, or superlative descriptor, and §3.5's wording matches the reporting practice.

**R3 — Correct the Delacroix reading and re-derive the design implication.**
Restore Delacroix's actual position in §5, and rebuild the third discussion finding from it rather than against it. Carry the §2 cultivation-versus-performativity tension through §4 and §5 instead of announcing it and dropping it. Test the participation recommendation against the paper's own ritual-compliance finding, which R2 identifies as evidence for Delacroix. Address what a practitioner needs: how to distinguish a participation ritual from genuine participation when both look identical in an evidence portfolio.
- **Acceptance criteria**: Delacroix's position is stated consistently in §2 and §5, and the design implication is derived from it with the performativity objection addressed using the interview material.

**R4 — Report the qualitative analytic procedure to a reproducible standard.**
Supply the coding framework or codebook, state whether coding was inductive or template-based, give the number of coders and the reconciliation procedure, and name the trustworthiness strategies used (member checking, audit trail, negative-case analysis, peer debriefing). "Coding proceeded iteratively until a stable structure was reached" is not a reportable procedure.
- **Acceptance criteria**: Another analyst could follow or contest the stated procedure, and every element listed above appears in §3.4 or an appendix.

**R5 — Retract the sector-level and priority claims; bound the conclusions to the design.**
Withdraw "universities across the sector," "the higher education sector as a whole," "administrators everywhere," and "the first comprehensive account." Replace the population claim with a mechanism claim carrying stated scope conditions, add a bounded transferability statement naming the regime studied, and either rescope the §6 three-party negotiation claim to administrators or acknowledge that academics and external bodies were not sampled.
- **Acceptance criteria**: No claim exceeds three institutions in one national system, no priority claim remains, and §5 and §6 no longer contradict §6's own call for cross-system testing.

**R6 — Rebuild the contribution, the construct definition, and the positioning.**
Supply an operational definition of quality culture tied to a named framework that distinguishes it from quality assurance, institutional culture, and compliance behaviour. Engage the field's constitutive literature (EUA Quality Culture Project's structural/cultural distinction, Harvey & Green, Harvey & Stensaker's typology, Newton, and the audit-culture canon invoked through Harlow 2019) as positioning rather than as an appended list, and correct the §2 characterisation of the quality-culture strand as "still emergent." Name the mechanism the ritual-compliance finding describes, at approximately two paragraphs in §2 plus a reframing of §5's second finding. Develop the identity-in-the-gap / hinge-actor argument as the paper's centre rather than as its third theme, and bring the manuscript to this venue's normal length for an empirical article.
- **Acceptance criteria**: Quality culture is operationally defined against a named framework, the pre-2018 constitutive literature and the named mechanism both appear in §2 and do analytic work in §5, and the contribution claim states what the data add beyond Iversen, Okonkwo, Pettersen, Rahman, and Silva & Tan.

**R7 — Document the survey and repair or withdraw the inferential claim.**
Report instrument provenance, item wording, scale range and anchors, dimensional structure, and an internal-consistency estimate; report the sampling frame, recruitment route, eligibility definition, response rate, and per-institution breakdown reconciling n=9 and n=11 against the stated total of 48. Then either supply the full inferential analysis for the subgroup contrast (named test, test statistic, degrees of freedom, effect size, confidence interval, and the number of comparisons examined) or present the contrast descriptively with no inferential verdict and withdraw the moderator suggestion.
- **Acceptance criteria**: M=3.9 (SD=0.6) is interpretable against a described instrument and scale, the 48 respondents are fully accounted for, and no "statistically significant" claim appears without its complete supporting apparatus.

**R8 — Reconcile the interview sample size.**
State authoritatively whether twelve or fourteen administrators were interviewed, correct the abstract or §3.2 accordingly, say what happened to any excluded cases and where, and re-check every count-dependent statement in §4. If the discrepancy reflects post-hoc removal of participants, that disposition belongs in R1's report of the reinstated cases.
- **Acceptance criteria**: One N appears throughout the manuscript, its relationship to R1's reinstated corpus is stated, and no prevalence claim rests on the superseded figure.

**R9 — Correct the protocol description and the cross-site warrant.**
Bring §4.1 into line with the semi-structured design declared in §3.1 and §3.3, or supply the protocol and correct the design description. Then withdraw or re-warrant the inference that cross-institution recurrence shows the pattern is not a local artifact, addressing R3's point that a common instrument and a shared national regulatory system are both candidate manufacturers of that convergence.
- **Acceptance criteria**: §4.1's instrument description matches §3, and the robustness claim is either supported by a stated warrant or removed.

**R10 — Supply resolvable identifiers for all twelve references.**
Replace the `10.5555/` test-prefix DOIs (`1042001`–`1042012`) with resolvable identifiers, or explain their presence if it is a production or anonymisation artifact. This is a precondition on re-review, not merely a formatting fix: the panel's source-fidelity findings under R3 and R6 remain provisional until the cited works can be retrieved and checked.
- **Acceptance criteria**: Every reference carries a resolvable identifier or a stated explanation, and the sources characterised in §2 and §5 can be independently verified against the manuscript's descriptions.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. A DA-only or pre-decomposition item uses `—`.
>
> **Priority note (stated for transparency).** Priority 1 default follows the consensus taxonomy (CONSENSUS-4 and CONSENSUS-3 serious issues). Four items are promoted to Priority 1 below that default because they are the stated trigger-driver of a reviewer's dimension block, which makes them decision-bearing under the contract: **R4** (SC-19, single-reviewer, drives D1's block trigger), **R6** (SC-22 corroborated and SC-25 corroborated, driving D2/D6 and D4 respectively; SC-28/SC-33 single-reviewer, driving D4/D6), and **R10** (SC-1a corroborated, driving D5's block trigger and arbitrated as a re-review precondition). This is roadmap ordering, not an aggregation rule applied to the scoring matrix; the mechanical emission above is untouched by it.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Reinstate the excluded dissenting cases, re-analyse, and re-derive or withdraw the three-theme structure; delete the full-range coverage claim | SC-3, SC-4, SC-5 | Critical (transported: R1 Critical, EIC Critical, R3 Critical; R2 Major) | text: §4.3 "these were excluded for space, as they fell outside the three-theme structure that organized our analysis" alongside "capturing the full range of administrator views" | 5 — R1, negative-case analysis and reflexive TA taught at doctoral level | R1 (owner), EIC, R2, R3, DA C2 | P1 | 3–4 weeks |
| R2 | Resolve the anonymity conflict: redact identifying descriptors throughout §4 or document consent scope; correct §3.5 | SC-2 | Critical (transported: EIC, R1, R3 Critical; R2 Minor with declared deference) | text: §3.5 / §4.1 "no individual could be identified" vs "the quality director of the largest private university in the region" | 5 — R3, prior research-ethics committee review of this exact problem class | EIC, R1, R2, R3, DA C3 | P1 | 3–5 days |
| R3 | Correct the Delacroix reading and re-derive the design implication from his actual argument; carry the §2 tension through §4–§5 | SC-6, SC-7 | Critical (transported: R2 Critical; EIC, R1 Major/5, R3 Major/4) | text: §5 "the central mechanism for building a healthy quality culture" vs §2 "argues *against* treating stakeholder consultation as sufficient evidence" | 5 — R2, internal comparison plus familiarity with the cultivation/performativity debate | R2 (owner), EIC, R1, R3, DA C1 | P1 | 1–2 weeks |
| R4 | Report the qualitative analytic procedure: codebook, inductive vs template, coder count and reconciliation, trustworthiness strategies | SC-19 | Critical (transported: R1 Critical) | absence: §3.4 Analysis — expected codebook or coding framework, inductive versus template statement, coder count and reconciliation, named trustworthiness strategies | 5 — R1, standard reporting expectations for thematic analysis | R1 (single-reviewer; D1 block-trigger driver) | P1 | 1–2 weeks (concurrent with R1) |
| R5 | Retract the sector-level generalisation and priority claim; bound conclusions to the design; rescope or acknowledge the three-party negotiation claim | SC-8, SC-9, SC-23, SC-28 | Major (transported: EIC, R1, R2, R3 Major; R3 Minor on SC-23) | text: §5 "these findings demonstrate that universities across the sector treat QA as a negotiated accomplishment" and §6 "the first comprehensive account" | 5 — R1 and EIC, direct comparison of claim scope against the stated sampling frame | EIC, R1, R2, R3, DA M2 | P1 | 1 week |
| R6 | Rebuild contribution, construct definition, positioning literature, and named mechanism; develop the hinge-actor argument; bring to venue length | SC-10, SC-11, SC-22, SC-24, SC-25, SC-26, SC-33 | Major (transported: EIC Major, R2 Major/5, R3 Major/5; R1 Critical on the re-analysis dependency) | absence: §2 and references — expected the field's constitutive quality-culture literature and the organizational-theory vocabulary naming the described mechanism; plus `[CONFIDENCE-SOURCE: unavailable]` on EIC's SC-11 row | 5 — R2 and R3, each on their primary research literature | EIC (D6 owner), R2, R3, R1 | P1 | 4–5 weeks |
| R7 | Document the survey instrument and sample; supply or withdraw the inferential subgroup claim | SC-12, SC-14, SC-15 | Major (transported: R1 Major/5, R3 Major/4, R2 Major/4; EIC Minor) | text: §4.4 "we found a statistically significant difference (p<.05)"; absence: §3.3 and §3.2 — instrument provenance, items, scale anchors, reliability, sampling frame, response rate, per-institution breakdown | 5 — R1, published on significance-testing misuse in small-n institutional survey work | R1 (owner), R3, R2, EIC, DA M5/M9 | P1 | 1–2 weeks |
| R8 | Reconcile the 14-versus-12 interview N and re-check every count-dependent claim | SC-16 | Major (transported: R1 Major/5, EIC Major/5; R2 and R3 Minor/5) | text: Abstract "Fourteen administrators were interviewed in depth" vs §3.2 "Twelve senior administrators (n=12)" | 5 — direct textual comparison, four seats concurring | EIC, R1, R2, R3, DA M1 | P1 | 1–2 days |
| R9 | Correct §4.1's "structured protocol" description and withdraw or re-warrant the cross-site robustness inference | SC-17, SC-18 | Major (transported: R1 Major/5, EIC Major/4; R3 Minor/4) | text: §4.1 "These themes emerged systematically from the structured protocol" and "giving us confidence that the pattern was not an artifact" vs §3.1 "semi-structured interviews" | 5 — R1, direct comparison of §4.1 against §3.1 and §3.3 | EIC, R1, R3, DA M4 | P1 | 2–3 days |
| R10 | Supply resolvable identifiers for all twelve references (re-review precondition; see SPLIT SC-1b) | SC-1a, SC-1b | Critical per EIC / Minor per R2 — **arbitrated SPLIT, both bands recorded** | text: References, Aoki (2019) through Silva & Tan (2021) "https://doi.org/10.5555/1042001" … "10.5555/1042012" | 5 (EIC — routine editorial-office DOI verification) / 3 (R2 — prefix status factual, reason for its use not determinable) | EIC (D5 block driver), R2 | P1 | 1–3 days |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | Report quality culture as dimensions against the named framework rather than a single scalar | SC-13 | Major (transported: R2) | text: §4.4 "respondents' overall institutional quality culture score was moderately positive (M=3.9, SD=0.6)" | 4 — R2; psychometric adequacy routed to R1 | R2 | P2 | 3–5 days (with R7) |
| S2 | Name and analyse the administrator/staff divergence as a level-of-analysis finding using the existing data | SC-29 | Major (transported: R1 Major/5, R3 Major/4) | text: §5 "a divergence worth pursuing in future work" | 5 — R1, integration is R1's specific review focus | R1, R3 | P2 | 1 week |
| S3 | Re-describe the survey as divergent rather than corroborative and state the integration procedure | SC-30 | Major (transported: R1 Major/5, R3 Major/4) | text: §4.4 "The survey corroborated the qualitative picture" then "had led us to anticipate a more skeptical picture" | 5 — R1 | R1, R3, DA M3 | P2 | 3–5 days |
| S4 | Connect the "distributed leadership" and "identity work" labels to their theoretical traditions at venue-appropriate depth | SC-26 | Major (transported: R3) | absence: §2 and §5 — expected contact with the leadership-studies and identity-work literatures the theme labels invoke | 5 — R3, primary research literature | R3 | P2 | 3–5 days (with R6) |
| S5 | Identify the national QA regime at regime and review-framework level | SC-32 | Minor (transported: R2) | absence: §3.2 setting description — expected identification of the national QA regime and its review framework | 3 — R2; how much anonymity the venue permits to be relaxed is editorial | R2 | P2 | 1 day |
| S6 | Report per-case prevalence or calibrate the universal prevalence language (dependent on R1's outcome) | SC-20 | Minor (transported: R1) | text: §4.2 "This relational, distributed understanding of leadership recurred across every interview" | 4 — R1, claim-calibration judgement | R1, DA M7 | P2 | 2–3 days |
| S7 | Add a data, protocol, and codebook availability statement plus appendices | SC-21 | Minor (transported: R1) | absence: whole manuscript — expected an availability statement and appendices supporting independent checking | 5 — R1, exhaustive check of the submitted text | R1 | P2 | 1–2 days |
| S8 | Qualify the "coping resource" inference or supply data distinguishing it from sincere commitment and interviewer performance | SC-34 | Major (transported: DA MAJOR band) | text: §4.3 "This vocational framing appeared to function as a coping resource" | 4 — DA, inference-type mismatch between interview talk and psychological function | DA M8 (no non-DA corroboration; recorded as DA-sourced) | P2 | 2–3 days |
| S9 | Engage Pettersen (2022) and Rahman (2020) in the Findings and Discussion, not only §2 | SC-35 | Major (transported: R2 Major/4) | text: §2 "This latter turn is closest in spirit to the present study" | 4 — R2 and DA, internal comparison of the gap claim against cited prior work | R2, DA M6 | P2 | 2–3 days (with R6) |
| S10 | Add a numbered, captioned table for the survey results | SC-31 | Minor (transported: EIC) | absence: whole manuscript — expected a numbered table reporting instrument, items, scale, response rate, subgroup means and the test statistic | 5 — EIC, directly observable | EIC | P3 | 1 day |
| S11 | Replace demonstrative verbs ("demonstrate," "confirms," "systematically") with verbs available to interpretive thematic work | — (editorial channel; `source_kind: editorial`) | Editorial (below finding threshold; no transported metadata) | text: §5 "these findings demonstrate" and "confirms long-standing concerns" | — | Aggregated: EIC, R1, R2, R3, DA M2 | P3 | 1 day |

> Transported metadata appears on every row above, not only on the three Top Blocking rows. Where a card lacked a per-finding value, the row carries its provenance tag (`[CONFIDENCE-SOURCE: unavailable]` on EIC's SC-11 contribution to R6). No severity on this roadmap was re-derived by this desk.

### Revision Checklist (Checkable List)

#### Priority 1 — Structural Revisions (estimated total effort: ~9–11 weeks, partly parallel)
- [ ] R1: Reinstate and analyse the excluded dissenting cases; re-derive or withdraw the three themes; delete the coverage claim — **do this first**
- [ ] R2: Redact identifying descriptors throughout §4 or document consent scope; correct §3.5
- [ ] R3: Correct the Delacroix reading; re-derive the design implication; carry the §2 tension through §4–§5
- [ ] R4: Report codebook, coding approach, coder count and reconciliation, trustworthiness strategies
- [ ] R5: Retract sector-level and priority claims; bound the conclusions; rescope the three-party claim
- [ ] R6: Rebuild construct definition, positioning literature, named mechanism, hinge-actor argument, length
- [ ] R7: Document the survey instrument and sample; supply or withdraw the inferential claim
- [ ] R8: Reconcile the 14-versus-12 N and re-check count-dependent claims
- [ ] R9: Correct §4.1's protocol description; withdraw or re-warrant the cross-site inference
- [ ] R10: Supply resolvable reference identifiers (re-review precondition)

#### Priority 2 — Content Supplementation (estimated total effort: ~3 weeks, overlapping P1)
- [ ] S1: Report quality culture dimensionally rather than as one scalar
- [ ] S2: Analyse the administrator/staff divergence with existing data
- [ ] S3: Re-describe the survey as divergent; state the integration procedure
- [ ] S4: Ground the leadership and identity-work labels in their traditions
- [ ] S5: Identify the national QA regime at framework level
- [ ] S6: Calibrate or evidence the prevalence language
- [ ] S7: Add availability statement and appendices
- [ ] S8: Qualify or evidence the "coping resource" inference
- [ ] S9: Engage Pettersen and Rahman in §4–§5

#### Priority 3 — Text and Formatting (estimated total effort: ~2 days)
- [ ] S10: Add a numbered, captioned survey table
- [ ] S11: Replace demonstrative verbs with verbs the design supports

**Sequencing note.** R1 precedes R4, R6, R8, S2, S3, and S6, because restoring the excluded cases may change what the themes are and therefore what is being reported, positioned, and counted. R10 precedes final assessment of R3 and R6. S2 and S3 are Priority 2 by consensus count but are coupled to R5 and R6: the Discussion cannot be rewritten without them, so they belong in the same revision pass.

### Revision Deadline

**10–12 weeks.** This exceeds the usual 6–8 weeks for a major revision, deliberately. Two Priority 1 items — R1 (re-analysis with the negative cases restored) and R6 (construct definition, positioning literature, mechanism, and development to venue length) — are new analytic and scholarly work rather than editing, and the panel is unanimous on that point. Requesting them inside eight weeks would invite a superficial response.

**Re-review.** Required. The revision returns minimally to the methodology seat (R1, R4, R7, R8, R9) and the domain seat (R3, R6, S1, S9), and the Journal-Fit Reviewer will re-assess D6 once R6 is complete. Source-fidelity findings re-open on satisfaction of R10.

### Response Letter Template

Please use `templates/revision_response_template.md` and respond point-by-point to every item R1–R10 and S1–S11, quoting the revised text and its location. Two items need explicit handling beyond the standard format:

- **R1**: state how many cases were excluded, what they said, and how each of the three themes changed or survived once they were reinstated. "Space" is not an acceptable account of an analytic exclusion.
- **R10**: if the `10.5555/` identifiers are a production or anonymisation artifact, say so directly; if they are not, the editorial office will treat the matter as a research-integrity question, and it is better addressed in your response letter than after it.

The three Devil's Advocate CRITICAL challenges (C1–C3) must each receive a direct response even where you disagree with the framing.

---

## Part 3: Reviewer Report Summary (Appendix)

Reviewers under this contract score dimensions rather than issue an overall Accept/Revise/Reject recommendation, and the cards carry no report-level Confidence Score. The matrix below therefore reports dimension verdicts and per-finding confidence ranges rather than fabricating fields the cards do not contain.

| Dimension | Journal-Fit Reviewer (EIC) | R1 (Methodology) | R2 (Domain) | R3 (Cross-disciplinary) | DA |
|-----------|---------------------------|------------------|-------------|-------------------------|----|
| Overall recommendation | not stated in card (contract-scored) | not stated | not stated | not stated | not stated |
| Dimensions scored | D5 block, D6 block (repairable) | D1 block (repairable), D3 block (repairable) | D2 block (repairable) | D4 block | D3 block (repairable) |
| Fatal declared | no | no | no | no | no |
| Per-finding confidence | 4–5 (one row absent) | 4–5 | 3–5 | 4–5 | 4–5 |
| Strengths logged | 3 | 5 | 3 | 3 | — |
| Weaknesses logged | 11 (3 Critical, 7 Major, 1 Minor) | 13 (3 Critical, 8 Major, 2 Minor) | 10 (1 Critical, 5 Major, 4 Minor) | 12 (2 Critical, 7 Major, 3 Minor) | 12 (3 CRITICAL, 9 MAJOR) |
| Key weaknesses | → Step 1b inventory | → Step 1b inventory | → Step 1b inventory | → Step 1b inventory | → C1–C3 adjudication table |

**Journal-Fit Reviewer (EIC) summary.** D5 block, D6 block (repairable). Key point: the manuscript fails three submission-readiness gates — unverifiable references, self-contradicting sample size, ethics statement contradicted by its own findings text — and the contribution increment, read against the paper's own bibliography, cannot be repaired by rescoping the claims.

**R1 (Methodology) summary.** D1 block (repairable), D3 block (repairable). Key point: the qualitative analysis is not reportable from the text, and §4.3's exclusion of disconfirming cases is an analytic decision rather than a reporting omission, so the fix is re-analysis with the negative cases restored, not a longer Methods paragraph.

**R2 (Domain) summary.** D2 block (repairable). Key point: §5 inverts Delacroix at exactly the point where the paper builds its practical recommendation, and the paper's own ritual-compliance finding supports Delacroix's actual argument; separately, the paper's conceptual scaffolding and novelty claim were assembled without the field's constitutive literature, which must be rebuilt rather than appended to.

**R3 (Cross-disciplinary) summary.** D4 block. Key point: the paper describes ceremonial conformity and means-ends decoupling without naming the mechanism, and substitutes a claim about scope ("the sector as a whole") for the claim about mechanism its data could actually support; the anonymity conflict makes publication untenable as written.

**Devil's Advocate summary.** D3 block (repairable). Key point: the chain from evidence to conclusion breaks at three load-bearing points, and at each break the paper asserts the opposite of what its own text records; the repairs are achievable without new fieldwork but require rewriting the Discussion and Conclusion rather than softening them.

---

## Roadmap — Schema 7 machine form

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "stage": "reviewer_full_review",
  "editorial_decision": "major_revision",
  "provenance_block_status": "PROVENANCE-STAMP-MISSING",
  "items": [
    {
      "id": "R1",
      "priority": "must_fix",
      "verification_criteria": "All previously excluded cases are analysed and reported; each theme states how the dissenting cases bear on it; no coverage or representativeness claim remains that the reported corpus does not support.",
      "reviewer": ["R1", "EIC", "R2", "R3", "DA"],
      "severity": "critical",
      "evidence_anchor": "text: §4.3 \"these were excluded for space, as they fell outside the three-theme structure that organized our analysis\"",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-3", "SC-4", "SC-5"],
      "consensus": "CONSENSUS-4 (SC-3, SC-4); SPLIT arbitrated (SC-5)",
      "da_ref": "C2"
    },
    {
      "id": "R2",
      "priority": "must_fix",
      "verification_criteria": "No quotation is attributable to an identifiable individual by role, institution, or superlative descriptor, and §3.5's wording matches the reporting practice.",
      "reviewer": ["EIC", "R1", "R2", "R3", "DA"],
      "severity": "critical",
      "evidence_anchor": "text: §3.5 / §4.1 \"no individual could be identified\" vs \"the quality director of the largest private university in the region\"",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-2"],
      "consensus": "CONSENSUS-4",
      "da_ref": "C3"
    },
    {
      "id": "R3",
      "priority": "must_fix",
      "verification_criteria": "Delacroix's position is stated consistently in §2 and §5, and the design implication is derived from it with the performativity objection addressed using the interview material.",
      "reviewer": ["R2", "EIC", "R1", "R3", "DA"],
      "severity": "critical",
      "evidence_anchor": "text: §5 \"the central mechanism for building a healthy quality culture\" vs §2 \"argues against treating stakeholder consultation as sufficient evidence\"",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-6", "SC-7"],
      "consensus": "CONSENSUS-4",
      "da_ref": "C1",
      "blocked_by": ["R10"]
    },
    {
      "id": "R4",
      "priority": "must_fix",
      "verification_criteria": "Another analyst could follow or contest the stated procedure, and codebook, coding approach, coder count, reconciliation, and named trustworthiness strategies all appear in §3.4 or an appendix.",
      "reviewer": ["R1"],
      "severity": "critical",
      "evidence_anchor": "absence: §3.4 Analysis — expected codebook or coding framework, inductive versus template statement, coder count and reconciliation, named trustworthiness strategies",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-19"],
      "consensus": "single-reviewer; promoted to must_fix as D1 block-trigger driver",
      "blocked_by": ["R1"]
    },
    {
      "id": "R5",
      "priority": "must_fix",
      "verification_criteria": "No claim exceeds three institutions in one national system, no priority claim remains, and §5 and §6 no longer contradict §6's own call for cross-system testing.",
      "reviewer": ["EIC", "R1", "R2", "R3", "DA"],
      "severity": "major",
      "evidence_anchor": "text: §5 \"these findings demonstrate that universities across the sector treat QA as a negotiated accomplishment\" and §6 \"the first comprehensive account\"",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-8", "SC-9", "SC-23", "SC-28"],
      "consensus": "CONSENSUS-4 (SC-8, SC-23); corroborated (SC-9); single-reviewer (SC-28)"
    },
    {
      "id": "R6",
      "priority": "must_fix",
      "verification_criteria": "Quality culture is operationally defined against a named framework, the pre-2018 constitutive literature and the named mechanism both appear in §2 and do analytic work in §5, and the contribution claim states what the data add beyond Iversen, Okonkwo, Pettersen, Rahman, and Silva & Tan.",
      "reviewer": ["EIC", "R2", "R3", "R1"],
      "severity": "major",
      "evidence_anchor": "absence: §2 and references — expected the field's constitutive quality-culture literature and the organizational-theory vocabulary naming the described mechanism",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-10", "SC-11", "SC-22", "SC-24", "SC-25", "SC-26", "SC-33"],
      "consensus": "CONSENSUS-4 (SC-10); CONSENSUS-3 (SC-11, SC-24); corroborated (SC-22, SC-25); single-reviewer (SC-26, SC-33)",
      "notes": "SC-11 carries [CONFIDENCE-SOURCE: unavailable] for the EIC row (card gap). Theory volume arbitrated to ~2 paragraphs in §2 plus reframing of §5's second finding.",
      "blocked_by": ["R1", "R10"]
    },
    {
      "id": "R7",
      "priority": "must_fix",
      "verification_criteria": "M=3.9 (SD=0.6) is interpretable against a described instrument and scale, the 48 respondents are fully accounted for, and no \"statistically significant\" claim appears without named test, statistic, degrees of freedom, effect size, confidence interval, and number of comparisons.",
      "reviewer": ["R1", "R3", "R2", "EIC", "DA"],
      "severity": "major",
      "evidence_anchor": "text: §4.4 \"we found a statistically significant difference (p<.05)\"; absence: §3.3 and §3.2 — instrument provenance, items, scale anchors, reliability, sampling frame, response rate, per-institution breakdown",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-12", "SC-14", "SC-15"],
      "consensus": "CONSENSUS-4"
    },
    {
      "id": "R8",
      "priority": "must_fix",
      "verification_criteria": "One N appears throughout the manuscript, its relationship to R1's reinstated corpus is stated, and no prevalence claim rests on the superseded figure.",
      "reviewer": ["EIC", "R1", "R2", "R3", "DA"],
      "severity": "major",
      "evidence_anchor": "text: Abstract \"Fourteen administrators were interviewed in depth\" vs §3.2 \"Twelve senior administrators (n=12)\"",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-16"],
      "consensus": "CONSENSUS-4",
      "blocked_by": ["R1"]
    },
    {
      "id": "R9",
      "priority": "must_fix",
      "verification_criteria": "§4.1's instrument description matches §3, and the cross-site robustness claim is either supported by a stated warrant or removed.",
      "reviewer": ["EIC", "R1", "R3", "DA"],
      "severity": "major",
      "evidence_anchor": "text: §4.1 \"These themes emerged systematically from the structured protocol\" vs §3.1 \"semi-structured interviews\"",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-17", "SC-18"],
      "consensus": "CONSENSUS-3 (SC-17, silent: R2); single-reviewer (SC-18)"
    },
    {
      "id": "R10",
      "priority": "must_fix",
      "verification_criteria": "Every reference carries a resolvable identifier or a stated explanation, and the sources characterised in §2 and §5 can be independently verified against the manuscript's descriptions.",
      "reviewer": ["EIC", "R2"],
      "severity": "critical|minor",
      "evidence_anchor": "text: References, Aoki (2019) through Silva & Tan (2021) \"https://doi.org/10.5555/1042001\" … \"10.5555/1042012\"",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-1a", "SC-1b"],
      "consensus": "corroborated (SC-1a); SPLIT arbitrated (SC-1b) — gating question resolved, integrity question recorded UNRESOLVED and escalated",
      "notes": "Severity band unresolved between seats: EIC critical / R2 minor. Both recorded; neither re-derived. Re-review precondition for R3 and R6."
    },
    {
      "id": "S1",
      "priority": "should_fix",
      "verification_criteria": "The quality culture measure is reported by dimension against the named framework rather than as a single aggregate.",
      "reviewer": ["R2"],
      "severity": "major",
      "evidence_anchor": "text: §4.4 \"respondents' overall institutional quality culture score was moderately positive (M=3.9, SD=0.6)\"",
      "confidence": 4,
      "source_kind": "finding",
      "sub_claims": ["SC-13"],
      "consensus": "single-reviewer finding"
    },
    {
      "id": "S2",
      "priority": "should_fix",
      "verification_criteria": "The administrator/staff divergence is analysed as a level-of-analysis finding using the collected data rather than deferred to future work.",
      "reviewer": ["R1", "R3"],
      "severity": "major",
      "evidence_anchor": "text: §5 \"a divergence worth pursuing in future work\"",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-29"],
      "consensus": "corroborated finding",
      "notes": "Coupled to R5 and R6; complete in the same pass."
    },
    {
      "id": "S3",
      "priority": "should_fix",
      "verification_criteria": "§4.4 describes the survey result as divergent from expectation and states the integration procedure joining the two strands.",
      "reviewer": ["R1", "R3", "DA"],
      "severity": "major",
      "evidence_anchor": "text: §4.4 \"The survey corroborated the qualitative picture\" then \"had led us to anticipate a more skeptical picture\"",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-30"],
      "consensus": "corroborated finding",
      "notes": "Coupled to R5 and R6; complete in the same pass."
    },
    {
      "id": "S4",
      "priority": "should_fix",
      "verification_criteria": "The distributed-leadership and identity-work labels are connected to their theoretical traditions at a depth proportionate to the venue.",
      "reviewer": ["R3"],
      "severity": "major",
      "evidence_anchor": "absence: §2 and §5 — expected contact with the leadership-studies and identity-work literatures the theme labels invoke",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-26"],
      "consensus": "single-reviewer finding"
    },
    {
      "id": "S5",
      "priority": "should_fix",
      "verification_criteria": "The national QA regime and its review framework are identified at regime-type level.",
      "reviewer": ["R2"],
      "severity": "minor",
      "evidence_anchor": "absence: §3.2 setting description — expected identification of the national QA regime and its review framework",
      "confidence": 3,
      "source_kind": "finding",
      "sub_claims": ["SC-32"],
      "consensus": "single-reviewer finding"
    },
    {
      "id": "S6",
      "priority": "should_fix",
      "verification_criteria": "Prevalence claims are either supported by reported per-case counts or softened to what the corpus shows.",
      "reviewer": ["R1", "DA"],
      "severity": "minor",
      "evidence_anchor": "text: §4.2 \"This relational, distributed understanding of leadership recurred across every interview\"",
      "confidence": 4,
      "source_kind": "finding",
      "sub_claims": ["SC-20"],
      "consensus": "single-reviewer finding",
      "blocked_by": ["R1"]
    },
    {
      "id": "S7",
      "priority": "should_fix",
      "verification_criteria": "A data, protocol, and codebook availability statement appears, with shareable materials appended.",
      "reviewer": ["R1"],
      "severity": "minor",
      "evidence_anchor": "absence: whole manuscript — expected an availability statement and appendices supporting independent checking",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-21"],
      "consensus": "single-reviewer finding"
    },
    {
      "id": "S8",
      "priority": "should_fix",
      "verification_criteria": "The coping-resource inference is either evidenced against competing readings or restated as a possible interpretation.",
      "reviewer": ["DA"],
      "severity": "major",
      "evidence_anchor": "text: §4.3 \"This vocational framing appeared to function as a coping resource\"",
      "confidence": 4,
      "source_kind": "finding",
      "sub_claims": ["SC-34"],
      "consensus": "DA-only MAJOR; no non-DA corroboration"
    },
    {
      "id": "S9",
      "priority": "should_fix",
      "verification_criteria": "Pettersen (2022) and Rahman (2020) are engaged in the Findings and Discussion, positioning each theme against its nearest baseline.",
      "reviewer": ["R2", "DA"],
      "severity": "major",
      "evidence_anchor": "text: §2 \"This latter turn is closest in spirit to the present study\"",
      "confidence": 4,
      "source_kind": "finding",
      "sub_claims": ["SC-35"],
      "consensus": "single-reviewer + DA"
    },
    {
      "id": "S10",
      "priority": "nice_to_fix",
      "verification_criteria": "A numbered, captioned table reports the survey instrument, scale, response rate, subgroup means, and test statistic.",
      "reviewer": ["EIC"],
      "severity": "minor",
      "evidence_anchor": "absence: whole manuscript — expected a numbered table or figure supporting the §4.4 reporting",
      "confidence": 5,
      "source_kind": "finding",
      "sub_claims": ["SC-31"],
      "consensus": "single-reviewer finding"
    },
    {
      "id": "S11",
      "priority": "nice_to_fix",
      "verification_criteria": "Demonstrative verbs are replaced throughout with verbs the design licenses.",
      "reviewer": ["EIC", "R1", "R2", "R3", "DA"],
      "source_kind": "editorial",
      "sub_claims": [],
      "consensus": "aggregated editorial channel; below finding threshold, no transported metadata"
    }
  ]
}
```

---

**Quality gate self-check.** All five cards read and cited; consensus and disagreement labelled per sub-claim over the four non-DA seats with silence counted as silence; both SPLITs arbitrated with rationale grounded in reviewer text; decision consistent with the panel (all five scored a block; none declared fatal; F2's action emitted unaltered); every roadmap item traceable to a named reviewer finding; severity and confidence transported with provenance tags where cards were incomplete; no issue introduced by this desk; roadmap emitted in both `academic-paper` revision-mode format and Schema 7. One outstanding blocker on the package itself: the `reviewer_full` provenance block cannot be filled without the dispatching layer's stamp, and the letter should not ship until it is.
