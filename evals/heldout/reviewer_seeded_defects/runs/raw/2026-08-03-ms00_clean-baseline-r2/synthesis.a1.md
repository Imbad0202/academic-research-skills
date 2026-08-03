# Editorial Decision Package

**Manuscript:** *Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students*
**Contract:** `reviewer/reviewer_full/v2` · baseline `v3.20.0` · panel_size 5

---

## Section 0 — Sprint Contract Mechanical Audit

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats | Worst assessed | Fatal? |
|-----|----------|----------------|--------------------------|----------------|--------|
| D1 methodology_rigor | mandatory | methodology | methodology=warn | **warn** | no |
| D2 domain_accuracy | mandatory | domain | domain=block (repairable) | **block** | no |
| D3 argumentative_coherence | mandatory | da, methodology | da=warn, methodology=warn | **warn** | no |
| D4 cross_disciplinary_relevance | high | perspective | perspective=warn | **warn** | no |
| D5 writing_and_structure | normal | eic | eic=warn | **warn** | no |
| D6 venue_fit_and_contribution | mandatory | eic | eic=block (repairable) | **block** | no |

All `not_assessed` values on ineligible seats excluded from numerator and denominator. Every dimension has ≥1 assessed eligible seat — no `[DIMENSION-UNASSESSED]`. No seat declared a fatal block; both blocks carry `block_class: repairable`. Audit verdict: **block (non-fatal)**.

### Step 2 — Failure-condition evaluation

| ID | Sev | Quantifier | Expression | Per-dimension result | Fired |
|----|-----|-----------|------------|----------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 no, D2 no, D3 no, D6 no | **false** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1 no, **D2 yes**, D3 no, **D6 yes** | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 yes (n=1→owner), D2 yes, D3 yes (n=2→both warn), D6 yes → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 = warn, not block | **false** |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1 yes | **true** |
| F0 | 10 | all | every dimension scores 'pass' | D1 fails | **false** |

### Step 3 — Precedence and emission

Fired: F2 (90), F3 (70), F5 (40). Highest severity = **F2**.

```
dimension_verdicts: [D1=warn, D2=block, D3=warn, D4=warn, D5=warn, D6=block]
fired_conditions: [F2, F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision
```

The DA card's CRITICAL table is empty by the reviewer's own statement ("my CRITICAL band is empty rather than populated for form's sake"), so no `C<n>` IDs exist and the line is `[]`. The DA's seven MAJOR items are adjudicated below for visibility; they carry no machine-line obligation. No `[DA-CRITICAL-VS-ACCEPT]` marker applies — the mechanical decision is not `accept`.

`ARS_CROSS_MODEL` not set; Step 4b blind decision check not run; no behavioural change.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript to *Research in Learning Technology*. It was reviewed by five independent reviewers: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary), and a Devil's Advocate.

### Decision: **Major Revision**

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this package was assembled in `reviewer_full` mode, in which this block is mandatory and must be filled from the dispatching layer's provenance stamp. No stamp was supplied with the reviewer cards. I am not permitted to infer which of the three permitted statements applies (cross-model slot active / single-family disclosure / dispatch-failure fallback), and I have not done so. **The handling editor must obtain the stamp and complete this block before the letter is released.** No claim about model independence across the five seats is made or implied by this package.

---

### Consensus Analysis

#### Step 1a — Reviewer summary matrix

| Dimension | Journal-Fit (EIC) | R1 Methodology | R2 Domain | R3 Perspective | Devil's Advocate |
|---|---|---|---|---|---|
| Overall recommendation | not stated (contract scoring only) | not stated | not stated | not stated | not stated |
| Dimensions assessed | D5, D6 | D1, D3 | D2 | D4 | D3 |
| Scores | D5 warn · D6 **block** (repairable) | D1 warn · D3 warn | D2 **block** (repairable) | D4 warn | D3 warn |
| Report-level confidence | not stated (per-finding only) | not stated | not stated | not stated | not stated |
| Strengths logged | 3 | 5 | 3 | 3 | (narrative) |
| Weaknesses: Critical / Major / Minor | 1 / 2 / 3 | 0 / 5 / 4 | 0 / 4 / 1 | 0 / 3 / 2 | 0 CRITICAL / 7 MAJOR |
| Per-finding confidence range | 4–5 | 4–5 | 3–5 | 4–5 | 3–5 |
| Key weaknesses | → Step 1b | → Step 1b | → Step 1b | → Step 1b | → DA adjudication |

The card format supplies per-finding confidence but no report-level confidence score and no explicit overall recommendation; those cells are marked as absent rather than inferred.

#### Step 1b — Weakness sub-claim inventory

Presentation note: the specification records one row per `(sub_claim, reviewer)` position. I have transposed the reviewer positions into a single column per sub-claim. This is information-equivalent (every reviewer's position on every sub-claim is stated) and materially more readable at 32 sub-claims × 4 seats. Positions: `raised` / `corr` (corroborated) / `disp` (disputed) / `—` (not-mentioned, i.e. **silence, not opposition**). DA positions are recorded but do not enter the count.

| SC | Sub-claim (atomic) | Parent | EIC | R1 | R2 | R3 | DA | agree/conflict (of 4) | Disposition | Sev (transported) | Conf |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SC-1 | No prior effect size appears anywhere, so the comparability claim cannot be checked | EIC W2 / R2 W2 | raised | — | corr | — | corr (M1) | 2/0 | corroborated finding | Major (both) | 5, 5 |
| SC-2 | All six DOIs use the reserved 10.5555 test prefix; no journal title resolves to an indexed periodical | EIC W1 | raised | — | — | — | — | 1/0 | single-reviewer | **Critical** | 5 |
| SC-3 | The instrument-validation warrant (Costa & Wren 2019) is itself unverifiable | EIC W1 | raised | — | — | — | — | 1/0 | single-reviewer | Critical | 5 |
| SC-4 | The six adapted PU item stems are not reproduced and the adaptation is undocumented | EIC W5 / R1 W5 / R3 W5 | raised | corr | — | corr | — | 3/0 | **[CONSENSUS-3]** (silent: R2) | Minor / Major / Minor | 4, 5, 4 |
| SC-5 | α establishes consistency, not unidimensionality; no factor evidence for a mean composite | R1 W5 | — | raised | — | — | corr (M7) | 1/0 | single-reviewer | Major | 5 |
| SC-6 | "Previously validated" does not transfer from the parent instrument to the adapted version | R1 W5 / R2 W5 | — | raised | corr | — | corr (M7) | 2/0 | corroborated finding | Major / Minor | 5, 3 |
| SC-7 | Source instrument targets *continuance*; sample mixes acceptance and continuance | R2 W5 | — | — | raised | — | — | 1/0 | single-reviewer | Minor | 3 |
| SC-8 | Common-method variance (same instrument/respondent/occasion/format) is undisclosed | R1 W1 | — | raised | — | — | corr (M3) | 1/0 | single-reviewer | Major | 5 |
| SC-9 | Single coarse ordinal outcome: no estimable reliability, no attenuation bound, no latent-scale estimate | R1 W2 | — | raised | — | — | — | 1/0 | single-reviewer | Major | 5 |
| SC-10 | The Spearman check is over-read as independence from "the parametric assumption" | R1 W9 | — | raised | — | — | — | 1/0 | single-reviewer | Minor | 5 |
| SC-11 | No eligible-population denominator, therefore no participation rate | EIC W3 / R1 W3 | raised | corr | — | — | corr | 2/0 | corroborated finding | Major (both) | 5, 5 |
| SC-12 | Sample composition beyond year level is unreported; year levels themselves unquantified | EIC W3 / R3 W2 | raised | — | — | corr | corr | 2/0 | corroborated finding | Major (both) | 5, 4 |
| SC-13 | Announcement-channel recruitment excludes the low-engagement students the implication targets | R3 W2 | — | — | — | raised | corr (M5) | 1/0 | single-reviewer | Major | 4 |
| SC-14 | The recruitment channel may be the LMS itself (selection on the outcome) | DA M5 | — | — | — | — | raised | 0/0 (DA-only) | DA-only, unresolved | — | 4 |
| SC-15 | The five-category frequency distribution is never reported (median category only) | R1 W6 / EIC W4 | corr | raised | — | — | corr (M5) | 2/0 | corroborated finding | Minor (both) | 5, 4 |
| SC-16 | Assumption checks are asserted from an undisplayed scatterplot | R1 W6 / EIC W4 | corr | raised | — | — | — | 2/0 | corroborated finding | Minor (both) | 5, 4 |
| SC-17 | r² ≈ .18 is described verbally ("modest") rather than reported | EIC W4 | raised | — | — | — | corr | 1/0 | single-reviewer | Minor | 4 |
| SC-18 | The manuscript contains no table or figure of any kind | EIC W4 | raised | — | — | — | — | 1/0 | single-reviewer | Minor | 4 |
| SC-19 | Duplicate removal is logically incompatible with the stated anonymity procedure | R1 W4 | — | raised | — | — | corr (M6) | 1/0 | single-reviewer | Major | 4 |
| SC-20 | Power statement's status (a priori vs post hoc sensitivity) unspecified | R1 W7 | — | raised | — | — | — | 1/0 | single-reviewer | Minor | 4 |
| SC-21 | No data-, code-, or materials-availability statement | R1 W8 | — | raised | — | — | — | 1/0 | single-reviewer | Minor | 5 |
| SC-22 | Construct genealogy absent; canonical PU definition attributed to 2019/2020 secondary sources | R2 W1 | — | — | raised | — | — | 1/0 | single-reviewer | Major | 5 |
| SC-23 | Costa & Wren and Ibarra & Poll are cited in §5 as warrant for a magnitude comparison the manuscript never shows they contain | R2 W2 body | — | — | raised | — | corr (M1) | 1/0 | single-reviewer | Major | 5 |
| SC-24 | Estimand mismatch: PU→use bypasses intention; comparison literature estimates PU→intention | R2 W3 | — | — | raised | — | — | 1/0 | single-reviewer | Major | 5 |
| SC-25 | Mandatory-use boundary conceded in a trailing clause, omitted from Limitations | R2 W4 | — | — | raised | — | — | 1/0 | single-reviewer | Major | 5 |
| SC-26 | "Accessed the LMS" has no defined referent | R3 W1 | — | — | — | raised | — | 1/0 | single-reviewer | Major | 5 |
| SC-27 | The onboarding implication is actionable only under the disclaimed causal direction and names no action, population, or cost | R3 W3 / EIC W2 | corr | — | — | raised | corr (M4) | 2/0 | corroborated finding | Major (both) | 4, 5 |
| SC-28 | The §2 perceived-use boundary is dropped in the Abstract and §5, which say "engagement" | DA M2 | — | **disp** | **disp** | — | raised | 0/2 (DA-vs-panel) | **arbitrated** (below) | — | 5 |
| SC-29 | Compelled use + channel-engaged sample may compress outcome variance at the top | R2 W4 body | — | — | raised | — | — | 1/0 | single-reviewer | Major | 5 |
| SC-30 | Whitfield (2019) appears only at the point of use in §5 | EIC W6 | raised | — | — | — | — | 1/0 | single-reviewer | Minor | 4 |
| SC-31 | Log-access disclosure: the limitation is framed as inherent, not as a choice at an institution that owns the logs | R3 W4 | — | — | — | raised | — | 1/0 | single-reviewer | Minor | 4 |
| SC-32 | Format mismatch: ~1,900 words and one coefficient is a Research Note, not an Original Research article | EIC body | raised | — | — | — | — | 1/0 | single-reviewer | `[SEVERITY-SOURCE: letter-fallback]` | `[CONFIDENCE-SOURCE: not stated in card]` |

**Decomposition discipline:** every sub-claim above is an atomic component of a claim a reviewer actually made. No sub-claim was introduced by this seat.

#### Step 1c — Surface-form parity check (#216)

Applied before any weighting. Two checks bit:

- **R2's W5 (confidence 3, hedged, informal register)** — the acceptance/continuance mismatch is phrased tentatively ("I cannot inspect the six items"). I did **not** reduce its weight for tentative phrasing; it is carried at its stated confidence and its remedy is in the roadmap (S12). The tentativeness reflects a declared evidence limit, not a weak claim.
- **R1's W1 and W2 (dense psychometric vocabulary: attenuation, polyserial, Harman single-factor)** — technical specificity was **not** treated as corroboration. Each was checked against the paper independently: the paper does have both variables in one instrument (§3.2), does have a one-item five-category outcome (§3.2), and does omit both from §6. The weight comes from that check, not from the vocabulary.

Opposite-style counterfactual run on both: neither weight changes if the substance is rewritten in the other register. Authorship was not a weighting input.

#### Points of agreement

- **[CONSENSUS-3]** SC-4 — the six adapted perceived-usefulness items are not reproduced and the adaptation is undocumented. Raised by the Journal-Fit Reviewer, corroborated by R1 and R3; **R2 is silent on this sub-claim** (silence, not dissent). Note the transported severity bands differ (Minor / Major / Minor); see arbitration below.
- **Corroborated findings** (2 of 4, no conflict): SC-1 (no prior effect size), SC-6 (validation attribution), SC-11 (no denominator), SC-12 (sample composition), SC-15 (frequency distribution), SC-16 (assumption checks), SC-27 (onboarding implication).
- **No sub-claim reached [CONSENSUS-4].** With the field-analysis lane assignments in force (reference integrity to the Journal-Fit seat, psychometrics to R1, theory to R2, definition/actionability to R3), the seats largely covered disjoint territory. Low consensus counts here reflect scope separation, not weak support — SC-2 is a 1/4 finding because the other three seats were instructed not to opine on citation integrity, not because they disagreed.

#### Points of disagreement

**1. SC-28 — Is the perceived/behavioural boundary honoured outside §2?**

- **DA (M2, confidence 5):** the §2 commitment ("an indicator of perceived use rather than a behavioral count") is dropped in the Abstract's terminal sentence and §5, both of which say "engagement," a behavioural construct.
- **R1 (S4, confidence 5):** traced the construct label across abstract, methods, results, discussion, limitations and found "no later section quietly upgrades it to behaviour."
- **R2 (S2, confidence 4):** the redefinition "is carried consistently into §3.2, §4, and §6."

**Editor's resolution: DA's claim is validated in bounded form; R1's and R2's are also correct, about a different object.** I checked the manuscript directly rather than adjudicating on seat authority. The *measure* is never redescribed as behavioural — R1 and R2 are right about §3.2, §4, and §6 (§4 says "reported engagement," correctly hedged). But the Abstract's terminal sentence reads "perceived usefulness tracks with **LMS engagement** among undergraduates," unhedged, and §5 says perceived usefulness is "one of several factors bearing on **engagement**," also unhedged. DA's textual observation stands in the two most-read locations. Neither seat has expertise priority here — this is textual consistency, not methodology or domain — so the evidence decides. Verdict: a terminology defect in the summary sections, not construct drift in the analysis. **Repair is one word in each of two sentences** (roadmap R14). R1's and R2's strength findings survive unchanged and are reported to the author as such.

**2. SC-4 — severity band divergence (Minor / Major / Minor)**

R1 bands item non-reproduction Major; the Journal-Fit Reviewer and R3 band it Minor. **Not classified as a SPLIT.** The divergence traces to bundling — R1's W5 combines item wording with factor structure and the validation attribution, and its Major reflects the bundle — while the sub-claim's remedy is identical across all three seats (an appendix with the adapted items). No incompatible remedy, no substantive conflict about the sub-claim. I record the divergence rather than resolving it away; the roadmap carries all three transported bands.

**3. The predicted EIC-vs-R1 disagreement did not materialise.**

The Journal-Fit Reviewer flagged in advance that R1 might treat measurement problems as capping the maximum defensible claim rather than as fixable ("If that is their reading, it should govern; I have not scored around it"). R1 explicitly declined that reading: "I stopped short of `block` on D1 deliberately. Every defect above is either a reporting addition the authors can supply from data in hand or an interpretive qualification they can write." Both seats converge on repairable. Recorded so the author is not asked to guess.

**4. Log data — lane boundary preserved, no double-count.**

R1 explicitly declined to score the absence of log data as a methodological defect ("the paper never trades on behaviour"). R3 asks only that the *reason* logs were not used be disclosed. These are compatible; the roadmap carries one item (S5), not two.

#### Devil's Advocate adjudication

`da_critical_adjudications: []` — the DA declared no CRITICAL findings. The seven MAJOR items are adjudicated here for visibility; they bear on the D3 warn and the author must respond to each.

| DA item | Corroborated by | Journal-Fit assessment | Adjudication | Routed to |
|---|---|---|---|---|
| M1 comparability unfalsifiable | EIC W2, R2 W2 | Independently confirmed against §2, §5, §7 and the reference list | **VALIDATED** | R3, R5 |
| M2 "engagement" slippage | — (R1, R2 dispute) | Arbitrated above; textual claim holds for Abstract + §5 | **VALIDATED (bounded)** | R14 |
| M3 common-method variance | R1 W1 (conf 5, primary research area) | Independently confirmed; §6 lists four limitations, none is CMV | **VALIDATED** | R6 |
| M4 implication vs indeterminacy | R3 W3, EIC W2 | Confirmed: §5 states the reverse pathway is "equally consistent" then recommends intervening on the predictor | **VALIDATED** | R12 |
| M5a channel may be the LMS itself | — | The manuscript genuinely does not say. §1 places announcements on the LMS; §3.1 names "the institution's course-announcement channel." Cannot be resolved from the text | **UNRESOLVED — author query required** | S6 |
| M5b use-category distribution absent | R1 W6, EIC W4 | Confirmed | **VALIDATED** | S3 |
| M6 duplicate/anonymity contradiction | R1 W4 (conf 4) | Confirmed against §3.1 and §3.3 | **VALIDATED** | R9 |
| M7 α alone for a mean composite | R1 W5 | Confirmed; DA's own caveat that some venues accept α alone is noted | **VALIDATED (in part)** | S2 |

M5a is recorded as unresolved rather than resolved in either direction. The panel could not settle it on evidence or expertise, and I have not applied a directional prior; the author must answer it and the answer materially affects how §6's fourth limitation is written.

---

### Decision Rationale

Two mandatory dimensions carry non-fatal blocks and four carry warns, which fires F2 (severity 90) and returns Major Revision. That arithmetic is not the whole reason, so let me state the substance.

This manuscript is better executed than its tier norm and worse positioned than its execution suggests. Four of five reviewers independently credited the same thing: correlational language held throughout, the reverse causal pathway named and attributed, a confidence interval and a sensitivity floor and a rank-order check all reported, and four limitations disclosed pre-emptively. R1 reproduced both numeric claims and found the arithmetic correct. That calibration is real and it is not the problem.

The problem is that calibration is being asked to serve as contribution. The manuscript's only stated contribution is comparability — "one point in a distribution." Two independent seats found that the distribution is never named: no prior effect size appears anywhere. The domain seat found more specifically that two cited sources are made to warrant a magnitude comparison the manuscript never shows they contain, which is what makes D2 a block rather than a warn. The Journal-Fit seat found that every source carries a reserved test DOI prefix, so neither the comparison nor the comparators can be verified — including the instrument on which the study's central measurement warrant rests.

Both blocks are informational, not architectural. The empirical statement about these 214 students survives every reviewer's critique intact. What does not survive is the interpretive claim that carries the paper. That is repairable in revision, which is why this is Major Revision and not Reject.

### Top Blocking Issues

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | Every cited source is unverifiable — all six DOIs use the reserved 10.5555 test prefix and no journal title resolves to an indexed periodical, including the source of the study's measurement warrant | EIC (W1, Critical, conf 5) | text: References and §3.2 — "https://doi.org/10.5555/2050001"; "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency" | R1 |
| 2 | Two named sources are represented in §5 as warranting a quantitative comparability judgement the manuscript gives no evidence they contain | R2 (W2 body, Major, conf 5); DA M1 | text: §5 — "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)" | R2 |
| 3 | The stated contribution is comparability, but no prior effect size appears anywhere, making "consistent with prior work" unfalsifiable | EIC (W2, Major, conf 5); R2 (W2, Major, conf 5); DA M1 | absence: §2 and §5 — expected a named pooled PU–use estimate with its interval and a statement of where r = .42 falls; checked Abstract, §1, §2, §5, §7, References | R3, R5 |

---

### Achievability determination (union of requested changes)

The field analysis flagged the additive-rejection failure mode, and this synthesis is obliged to answer it rather than let arithmetic deliver a verdict no reviewer stated.

**Determination: the union of requested changes is achievable with the existing 214-response dataset, conditional on one gating item.** No reviewer requests new data collection. Specifically:

- R2 opens by declining to request constructs, mediators, or a structural model.
- R1's two heaviest asks (a single-factor diagnostic on the seven items; a polyserial or polychoric estimate) are computable from data in hand.
- R3's concerns are "answerable by definition and disclosure," with sample composition contingent on what was already collected — and R3 states the alternative (report it or withdraw the implication).
- The Journal-Fit Reviewer's five requirements are all reporting, repositioning, or reformatting.

**The gating condition is R1 (reference integrity).** If verifiable sources — including a real provenance for the perceived-usefulness instrument — cannot be supplied, no other repair helps, and the decision must be revisited on that basis alone rather than pursued through the remaining roadmap. This is the Journal-Fit Reviewer's own stated position and I adopt it.

**Remedy class for each disclosed limitation** (reframing vs new data), so the author is not left conflating them:

| §6 limitation | Remedy class |
|---|---|
| 1. Single site | **Reframing** — retier to Research Note, supply the comparison anchor. No new data. |
| 2. Self-report not logs | **Disclosure** — state whether log access was sought and refused. New data only if the authors elect behavioural measurement, which no reviewer requires. |
| 3. Cross-sectional / causality | **Reframing** — condition or demote the implication. No new data. |
| 4. Voluntary response | **Reporting** (denominator, composition already held) + **honest non-closure**. Closing it fully would need new data; the panel asks only for disclosure. |
| *(undisclosed)* Common-method variance | **Reframing + existing-data diagnostic.** |
| *(undisclosed)* Mandatory use | **Reframing.** |

---

### Required Item Details

**R1**
Replace the reference list with sources a reader and the editorial office can locate and resolve, including verifiable provenance for the perceived-usefulness instrument. Every retained claim must be re-checked against the substituted source.
- **Acceptance criteria**: All references resolve to live, locatable records; no DOI uses the reserved 10.5555 range; the instrument source cited in §3.2 is independently checkable and its reported validation evidence is described in the manuscript.

**R2**
Withdraw or substantiate the §5 attribution in which Costa & Wren (2019) and Ibarra & Poll (2021) warrant a quantitative comparability judgement. If those sources report PU–use magnitudes, state them; if they do not, remove them from that sentence.
- **Acceptance criteria**: Every source cited in support of the comparability claim is shown in the text to report a PU–use effect size, or is removed from that claim.

**R3**
Report at least one prior or pooled PU–use estimate from education-sector acceptance research, with its interval, and state explicitly where r = .42 falls relative to it.
- **Acceptance criteria**: §2 and §5 each contain a named prior estimate with an interval and an explicit statement locating r = .42 as inside, above, or below it.

**R4**
State that the modelled path bypasses behavioural intention, say why, and restrict the comparison set to studies estimating the same PU-to-use link rather than PU-to-intention.
- **Acceptance criteria**: The manuscript states the bypassed mediator and confines its comparison set to estimates of the same estimand.

**R5**
State in one sentence what a reader or an institution can now do that they could not before this paper, and ensure that sentence survives contact with a moderate cross-sectional correlation.
- **Acceptance criteria**: §7 contains one explicit, non-circular contribution sentence naming what changes for a reader or institution, and it does not exceed what r = .42 supports.

**R6**
Disclose common-method variance as a rival account of the coefficient's magnitude, and report a single-factor diagnostic computed on the seven items.
- **Acceptance criteria**: §6 names common-method variance from same-instrument, same-respondent, same-occasion measurement as a limitation, and §4 or §3.4 reports a single-factor or equivalent diagnostic.

**R7**
State the two-sided distortion on r = .42 — attenuation from a single coarse ordinal outcome pushing it down, shared method pushing it up — and supply a polyserial or polychoric estimate of the latent association, or an explicit attenuation bound in its place.
- **Acceptance criteria**: The discussion states both directions of distortion, and either a latent-scale estimate or an explicit attenuation bound is reported.

**R8**
Supply the size of the eligible undergraduate population and the resulting participation rate, and state the reach of the distribution channel if known.
- **Acceptance criteria**: §3.1 reports the eligible-population denominator and a participation rate computed from it.

**R9**
Resolve the contradiction between duplicate removal (§3.1) and the anonymity procedure (§3.3): state the detection mechanism, and amend the anonymity and consent statements if quasi-identifiers were captured, or state the pattern criterion and its false-positive risk if duplication was inferred.
- **Acceptance criteria**: The duplicate-detection mechanism is stated and is logically consistent with the §3.3 anonymity claim as written.

**R10**
Define what constitutes an "access" event in the outcome item, or redefine the outcome explicitly as a self-appraisal of engagement intensity, and match the claim language to whichever is chosen.
- **Acceptance criteria**: §3.2 states the intended referent of "accessed the LMS," and every downstream claim uses language consistent with that referent.

**R11**
Add compelled LMS use to §6 as a limitation and take an explicit position on whether compulsion bounds the finding or undermines the theoretical frame, including its interaction with the voluntary-response limitation.
- **Acceptance criteria**: §6 contains a mandatory-use limitation with an explicit bounds-versus-invalidates position and a stated interaction with the existing fourth limitation.

**R12**
Either make the directional assumption an explicit condition of the onboarding recommendation and state what an institution would change, for whom, and at what cost, or demote the paragraph to a stated research agenda.
- **Acceptance criteria**: §5's practical paragraph either names its causal condition and specifies the action, target, and cost, or is rewritten as a research agenda with no implied intervention.

**R13**
Correct the Abstract's "previously validated instrument," which attaches the parent instrument's validation evidence to the adapted version actually fielded.
- **Acceptance criteria**: The Abstract attributes validation to the source instrument and separately describes what was established in this sample.

**R14**
Align the Abstract's terminal sentence and §5 with the boundary set in §2 by qualifying or replacing the unhedged noun "engagement."
- **Acceptance criteria**: No sentence in the Abstract or §5 describes the outcome with an unqualified behavioural noun; the perceived-use framing of §2 holds in both.

**R15**
Reformat and resubmit as a Research Note, with at least one table carrying the descriptive statistics and the outcome's category frequencies.
- **Acceptance criteria**: The manuscript is submitted in the Research Note format and contains at least one table.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. `—` marks an item with no sub-claim id.
> **Priority note:** default consensus→priority mapping is overridden for items that are a stated basis of a `block` score on a mandatory dimension. Those are Priority 1 by the P1 definition itself ("issues that cannot be accepted without fixing"), irrespective of consensus count. Each such override is visible in the Source column.

### Required Revisions (Must Fix)

> **Ordinal contract:** the `### Required Item Details` blocks above are numbered `R1..R15` in this table's order.

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Replace the reference list with verifiable sources, incl. instrument provenance | SC-2, SC-3 | Critical | text: References and §3.2 — "https://doi.org/10.5555/2050001"; "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency" | 5 — routine editorial-office DOI screening; reserved status of 10.5555 is public record | EIC W1 (D6 block basis) | P1 | 2–5 d (conditional) |
| R2 | Withdraw or substantiate the §5 source warrant for the magnitude comparison | SC-23 | Major | text: §5 — "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)" | 5 — meta-analytic synthesis of acceptance research is this seat's area | R2 (D2 block trigger) | P1 | 0.5 d |
| R3 | Report a named prior/pooled PU–use estimate with interval; locate r = .42 | SC-1 | Major | absence: §2 and §5 — expected a named pooled PU–use estimate with its interval; checked Abstract, §1, §2, §5, §7, References | 5, 5 | EIC W2 + R2 W2 (corroborated; both block bases); DA M1 | P1 | 2 d |
| R4 | State the bypassed intention step; restrict the comparison set to PU→use estimates | SC-24 | Major | text: §1 "nor do we test a full acceptance model"; §5 "consistent with prior technology-acceptance research" | 5 — estimand specification is this seat's direct research area | R2 W3 | P1 | 0.5 d |
| R5 | One-sentence statement of what a reader or institution can now do differently | SC-1 | Major | text: §2 "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model." | 5 — contribution screening is this seat's core function | EIC W2 (D6 block basis) | P1 | 0.5 d |
| R6 | Disclose common-method variance; report a single-factor diagnostic on the seven items | SC-8 | Major | absence: §6 Limitations — expected acknowledgement of CMV from same-instrument/respondent/occasion measurement plus a marker or Harman-type check; checked §3.2, §3.3, §3.4, §4, §5, §6 | 5 — CMV in single-instrument technology-use surveys is this seat's primary area | R1 W1; DA M3 | P1 | 1 d |
| R7 | State the two-sided distortion; supply a polyserial/polychoric estimate or attenuation bound | SC-9, SC-10 | Major | absence: §3.4 Analysis — expected a polyserial or polychoric estimate, or an explicit attenuation bound for the one-item five-category outcome; checked §3.2, §3.4, §4, §6 | 5 — attenuation and coarse-categorisation effects are core to this seat's teaching | R1 W2 (+W9) | P1 | 1 d |
| R8 | Supply eligible-population denominator and participation rate | SC-11 | Major | absence: §3.1 — expected an eligible-population denominator and a participation rate; checked §3.1, §3.4, §4, §6, §7 | 5, 5 | EIC W3 + R1 W3 (corroborated) | P1 | 0.5 d |
| R9 | Resolve duplicate removal vs the anonymity procedure | SC-19 | Major | text: §3.1 and §3.3 — "5 duplicate entries were removed" and "responses could not be linked back to individual students" | 4 — inference from the stated procedure | R1 W4; DA M6 | P1 | 0.5 d |
| R10 | Define the referent of "accessed the LMS" or redefine the outcome | SC-26 | Major | text: §3.2 "a single five-point frequency item asking how often the respondent accessed the LMS in a typical week" | 5 — this seat administers and reconciles these access definitions against event logs | R3 W1 | P1 | 0.5 d |
| R11 | Add the mandatory-use boundary to §6 with an explicit bounds-vs-invalidates position | SC-25, SC-29 | Major | text: §4 "including course requirements and assessment schedules" | 5 — mandatory-use boundary conditions are this seat's specific problem | R2 W4 | P1 | 0.5 d |
| R12 | Condition the onboarding implication on its causal assumption, or demote it | SC-27 | Major | text: §5 "modest support for the intuition that LMS onboarding which helps students see concrete usefulness" and "may be worth institutional attention" | 4, 5 | R3 W3 + EIC W2 (corroborated); DA M4 | P1 | 0.5 d |
| R13 | Correct the Abstract's "previously validated instrument" attribution | SC-6 | Major | text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument" | 5, 3 | R1 W5 + R2 W5 (corroborated); DA M7 | P1 | 0.25 d |
| R14 | Align "engagement" in the Abstract and §5 with the §2 perceived-use boundary | SC-28 | `[SEVERITY-SOURCE: DA MAJOR band]` | text: Abstract "perceived usefulness tracks with LMS engagement among undergraduates" vs §2 "an indicator of perceived use rather than a behavioral count" | 5 — direct textual comparison | DA M2, **arbitrated: validated in bounded form** (R1 S4 and R2 S2 dissent recorded) | P1 | 0.25 d |
| R15 | Reformat as a Research Note with at least one table | SC-32, SC-18 | `[SEVERITY-SOURCE: letter-fallback]` | text: EIC review body — "this is a Research Note, not an Original Research article" | `[CONFIDENCE-SOURCE: not stated in card]` | EIC (venue-fit owner seat) | P1 | 1 d |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Reproduce the six adapted PU items in an appendix and document the adaptation. **Escalates to P1 if R1 cannot supply a verifiable instrument source** (EIC W5: "the item text is the only remaining route to knowing what was measured") | SC-4 | Minor / Major / Minor (transported per seat) | absence: §3.2 Measures — expected the six item stems and a statement of how the adapted wording differs from the source; checked §3.2, §3.4, §7, References, appendices | 4, 5, 4 | **[CONSENSUS-3]** EIC W5 + R1 W5 + R3 W5 (silent: R2) | P2 | 0.5 d |
| S2 | Report dimensionality evidence for the six-item mean composite | SC-5 | Major | text: §3.2 "the scale showed good internal consistency (Cronbach's α = .88)" | 5 | R1 W5; DA M7 | P2 | 0.5 d |
| S3 | Report the frequency distribution across the five use categories | SC-15 | Minor | text: §4 "Self-reported LMS use had a median category of 'a few times per week.'" | 5, 4 | R1 W6 + EIC W4 (corroborated); DA M5b | P2 | 0.25 d |
| S4 | Report sample composition beyond year level, or state what was not collected | SC-12, SC-13 | Major | absence: §3.1 — expected composition beyond year level (enrolment status, commuter/residential, first-generation, connectivity); checked Abstract, §3.1, §3.2, §4, §6 | 5, 4 | EIC W3 + R3 W2 (corroborated) | P2 | 0.5 d |
| S5 | State whether LMS log access was sought, refused, or not pursued | SC-31 | Minor | text: §6 "LMS use was self-reported through a single item rather than measured through system logs" | 4 | R3 W4 | P2 | 0.25 d |
| S6 | State whether the course-announcement channel is the LMS under study | SC-14 | `[SEVERITY-SOURCE: DA MAJOR band]` | absence: §3.1 and §4 — expected disclosure of whether the announcement channel is the LMS, plus the use-category distribution; checked §1, §3.1, §3.4, §4, §6 | 4 | DA M5a — **UNRESOLVED, author query**; no non-DA seat raised it | P2 | 0.25 d |
| S7 | Note possible variance compression at the top of the outcome | SC-29 | Major | text: §4 "including course requirements and assessment schedules" | 5 | R2 W4 body | P2 | 0.25 d |
| S8 | Rewrite the robustness sentence to claim monotonic robustness specifically | SC-10 | Minor | text: §4 "indicating that the association did not depend on the parametric assumption" | 5 | R1 W9 | P2 | 0.1 d |
| S9 | Specify whether the power statement is a priori or post hoc sensitivity | SC-20 | Minor | text: §3.4 "so the design was sensitive to small-to-moderate associations" | 4 | R1 W7 | P2 | 0.1 d |
| S10 | Add a data-, code-, and materials-availability statement | SC-21 | Minor | absence: §3.3 and §7 — expected a data-, code-, or materials-availability statement; checked §3.2, §3.3, §3.4, §5, §6, §7, References | 5 | R1 W8 | P2 | 0.25 d |
| S11 | Show or summarise the assumption checks rather than asserting them | SC-16 | Minor | text: §3.4 "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers" | 5, 4 | R1 W6 + EIC W4 (corroborated) | P2 | 0.25 d |
| S12 | Reconcile the instrument's continuance context with the present operationalisation | SC-7 | Minor | text: §3.2 and References — "adapted from Costa and Wren (2019)"; "Perceived usefulness and continued use of learning platforms" | 3 | R2 W5 | P2 | 0.25 d |
| S13 | Add the primary theoretical genealogy and re-attribute the "long proposed" claim | SC-22 | Major | text: §2 "Research on technology acceptance has long proposed" and "the degree to which a person believes a technology will help them perform better" | 5 — this is the lineage this seat works in and publishes on | R2 W1 | P2 | 0.5 d |
| S14 | Report r² = .18 numerically rather than as "modest" | SC-17 | Minor | text: §4 "The proportion of variance shared by the two measures was accordingly modest" | 4 | EIC W4; DA | P3 | 0.1 d |
| S15 | Introduce Whitfield (2019) in §2, or drop the appeal to it in §5 | SC-30 | Minor | text: §5 "a possibility also raised in practitioner accounts of digital-environment onboarding (Whitfield, 2019)" | 4 | EIC W6 | P3 | 0.1 d |

> Transported metadata appears on every row: each item carries the driving sub-claim's transported Severity (with fallback tags where the card supplied none), the finding's typed Evidence Anchor, and its per-finding Confidence. Where a corroborated item has two source seats, both confidences are listed in source order.

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total effort: 10.5–13.5 days)

*Work package A — evidence base (gating; complete R1 before B–D)*
- [ ] R1: Replace all six references with verifiable sources, including instrument provenance
- [ ] R2: Withdraw or substantiate the §5 source warrant

*Work package B — the comparability claim*
- [ ] R3: Report a named prior/pooled estimate with interval; locate r = .42
- [ ] R4: State the bypassed intention step; restrict the comparison set
- [ ] R5: One sentence on what changes for a reader or institution

*Work package C — what the coefficient can mean*
- [ ] R6: Disclose common-method variance; run the single-factor diagnostic
- [ ] R7: State the two-sided distortion; supply a latent-scale estimate or attenuation bound

*Work package D — sample and procedure*
- [ ] R8: Denominator and participation rate
- [ ] R9: Duplicate-removal mechanism vs anonymity

*Work package E — claim discipline*
- [ ] R10: Define the referent of "accessed the LMS"
- [ ] R11: Mandatory-use boundary in §6 with an explicit position
- [ ] R12: Condition or demote the onboarding implication
- [ ] R13: Correct the Abstract's validation attribution
- [ ] R14: Align "engagement" wording in Abstract and §5

*Work package F — format*
- [ ] R15: Reformat as a Research Note with at least one table

#### Priority 2 — Content Supplementation (estimated total effort: 4–5 days)
- [ ] S1: Appendix with the six adapted items + adaptation description *(escalates to P1 if R1 fails)*
- [ ] S2: Dimensionality evidence for the composite
- [ ] S3: Use-category frequency distribution
- [ ] S4: Sample composition, or a statement of what was not collected
- [ ] S5: Log-access disclosure
- [ ] S6: Whether the announcement channel is the LMS *(author query — unresolved DA item)*
- [ ] S7: Variance-compression note
- [ ] S8: Monotonic-robustness rewrite
- [ ] S9: A priori vs post hoc sensitivity
- [ ] S10: Availability statement
- [ ] S11: Show the assumption checks
- [ ] S12: Continuance-vs-acceptance reconciliation
- [ ] S13: Primary theoretical genealogy

#### Priority 3 — Text and Formatting (estimated total effort: 0.5 day)
- [ ] S14: Report r² = .18 numerically
- [ ] S15: Introduce or drop Whitfield (2019)

### Revision Deadline

**8 weeks.** Total estimated effort ≈ 15–19 working days across 15 Required and 15 Suggested items, with the reference rebuild (R1) on the critical path and work packages B–E dependent on its outcome.

### Response Letter Template

Use `templates/revision_response_template.md`. Respond to every item R1–R15 and S1–S15 individually. Two items require a direct answer rather than a revision: **S6** (is the course-announcement channel the LMS under study?) and **R9** (by what mechanism were duplicates detected?). The panel could not resolve either from the text.

### Machine-form Roadmap (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "major_revision",
  "items": [
    {"id":"R1","priority":"must_fix","verification_criteria":"All references resolve to live, locatable records; no DOI uses the reserved 10.5555 range; the instrument source cited in §3.2 is independently checkable and its reported validation evidence is described in the manuscript.","reviewer":"eic","severity":"critical","evidence_anchor":"text: References and §3.2 — 'https://doi.org/10.5555/2050001'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-2","SC-3"],"gating":true},
    {"id":"R2","priority":"must_fix","verification_criteria":"Every source cited in support of the comparability claim is shown in the text to report a PU-use effect size, or is removed from that claim.","reviewer":"domain","severity":"major","evidence_anchor":"text: §5 — 'consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-23"]},
    {"id":"R3","priority":"must_fix","verification_criteria":"§2 and §5 each contain a named prior estimate with an interval and an explicit statement locating r = .42 as inside, above, or below it.","reviewer":"eic+domain","severity":"major","evidence_anchor":"absence: §2 and §5 — expected a named pooled PU-use estimate with its interval; checked Abstract, §1, §2, §5, §7, References","confidence":5,"source_kind":"reviewer","sub_claims":["SC-1"]},
    {"id":"R4","priority":"must_fix","verification_criteria":"The manuscript states the bypassed mediator and confines its comparison set to estimates of the same estimand.","reviewer":"domain","severity":"major","evidence_anchor":"text: §1 'nor do we test a full acceptance model'; §5 'consistent with prior technology-acceptance research'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-24"]},
    {"id":"R5","priority":"must_fix","verification_criteria":"§7 contains one explicit, non-circular contribution sentence naming what changes for a reader or institution, and it does not exceed what r = .42 supports.","reviewer":"eic","severity":"major","evidence_anchor":"text: §2 'It is intended as an incremental data point, comparable with prior work'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-1"]},
    {"id":"R6","priority":"must_fix","verification_criteria":"§6 names common-method variance from same-instrument, same-respondent, same-occasion measurement as a limitation, and §4 or §3.4 reports a single-factor or equivalent diagnostic.","reviewer":"methodology","severity":"major","evidence_anchor":"absence: §6 Limitations — expected acknowledgement of common-method variance plus a marker or Harman-type check; checked §3.2, §3.3, §3.4, §4, §5, §6","confidence":5,"source_kind":"reviewer","sub_claims":["SC-8"]},
    {"id":"R7","priority":"must_fix","verification_criteria":"The discussion states both directions of distortion, and either a latent-scale estimate or an explicit attenuation bound is reported.","reviewer":"methodology","severity":"major","evidence_anchor":"absence: §3.4 Analysis — expected a polyserial or polychoric estimate, or an explicit attenuation bound; checked §3.2, §3.4, §4, §6","confidence":5,"source_kind":"reviewer","sub_claims":["SC-9","SC-10"]},
    {"id":"R8","priority":"must_fix","verification_criteria":"§3.1 reports the eligible-population denominator and a participation rate computed from it.","reviewer":"eic+methodology","severity":"major","evidence_anchor":"absence: §3.1 — expected an eligible-population denominator and a participation rate; checked §3.1, §3.4, §4, §6, §7","confidence":5,"source_kind":"reviewer","sub_claims":["SC-11"]},
    {"id":"R9","priority":"must_fix","verification_criteria":"The duplicate-detection mechanism is stated and is logically consistent with the §3.3 anonymity claim as written.","reviewer":"methodology","severity":"major","evidence_anchor":"text: §3.1 and §3.3 — '5 duplicate entries were removed' and 'responses could not be linked back to individual students'","confidence":4,"source_kind":"reviewer","sub_claims":["SC-19"]},
    {"id":"R10","priority":"must_fix","verification_criteria":"§3.2 states the intended referent of 'accessed the LMS', and every downstream claim uses language consistent with that referent.","reviewer":"perspective","severity":"major","evidence_anchor":"text: §3.2 'a single five-point frequency item asking how often the respondent accessed the LMS in a typical week'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-26"]},
    {"id":"R11","priority":"must_fix","verification_criteria":"§6 contains a mandatory-use limitation with an explicit bounds-versus-invalidates position and a stated interaction with the existing fourth limitation.","reviewer":"domain","severity":"major","evidence_anchor":"text: §4 'including course requirements and assessment schedules'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-25","SC-29"]},
    {"id":"R12","priority":"must_fix","verification_criteria":"§5's practical paragraph either names its causal condition and specifies the action, target, and cost, or is rewritten as a research agenda with no implied intervention.","reviewer":"perspective+eic","severity":"major","evidence_anchor":"text: §5 'may be worth institutional attention'","confidence":4,"source_kind":"reviewer","sub_claims":["SC-27"]},
    {"id":"R13","priority":"must_fix","verification_criteria":"The Abstract attributes validation to the source instrument and separately describes what was established in this sample.","reviewer":"methodology+domain","severity":"major","evidence_anchor":"text: Abstract 'Perceived usefulness was measured with an adapted, previously validated instrument'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-6"]},
    {"id":"R14","priority":"must_fix","verification_criteria":"No sentence in the Abstract or §5 describes the outcome with an unqualified behavioural noun; the perceived-use framing of §2 holds in both.","reviewer":"da","severity":"major","evidence_anchor":"text: Abstract 'perceived usefulness tracks with LMS engagement among undergraduates' vs §2 'an indicator of perceived use rather than a behavioral count'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-28"],"arbitration":"validated_bounded"},
    {"id":"R15","priority":"must_fix","verification_criteria":"The manuscript is submitted in the Research Note format and contains at least one table.","reviewer":"eic","severity":"letter_fallback","evidence_anchor":"text: EIC review body — 'this is a Research Note, not an Original Research article'","confidence":null,"source_kind":"editorial","sub_claims":["SC-32","SC-18"]},
    {"id":"S1","priority":"should_fix","verification_criteria":"An appendix reproduces the six adapted perceived-usefulness items and states how the wording differs from the source instrument.","reviewer":"eic+methodology+perspective","severity":"minor|major|minor","evidence_anchor":"absence: §3.2 Measures — expected the six item stems and a statement of adaptation; checked §3.2, §3.4, §7, References, appendices","confidence":4,"source_kind":"reviewer","sub_claims":["SC-4"],"consensus":"CONSENSUS-3","escalates_to_must_fix_if":"R1 cannot supply a verifiable instrument source"},
    {"id":"S2","priority":"should_fix","verification_criteria":"Dimensionality evidence (factor analysis or item-total statistics) is reported for the six-item mean composite.","reviewer":"methodology","severity":"major","evidence_anchor":"text: §3.2 'the scale showed good internal consistency (Cronbach's alpha = .88)'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-5"]},
    {"id":"S3","priority":"should_fix","verification_criteria":"§4 reports the frequency of each of the five use categories.","reviewer":"methodology+eic","severity":"minor","evidence_anchor":"text: §4 'Self-reported LMS use had a median category of a few times per week'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-15"]},
    {"id":"S4","priority":"should_fix","verification_criteria":"§3.1 reports sample composition beyond year level, or states explicitly which composition variables were not collected.","reviewer":"eic+perspective","severity":"major","evidence_anchor":"absence: §3.1 — expected composition beyond year level; checked Abstract, §3.1, §3.2, §4, §6","confidence":5,"source_kind":"reviewer","sub_claims":["SC-12","SC-13"]},
    {"id":"S5","priority":"should_fix","verification_criteria":"§6 states whether LMS log access was sought and refused, precluded by the ethics approval, or not pursued.","reviewer":"perspective","severity":"minor","evidence_anchor":"text: §6 'LMS use was self-reported through a single item rather than measured through system logs'","confidence":4,"source_kind":"reviewer","sub_claims":["SC-31"]},
    {"id":"S6","priority":"should_fix","verification_criteria":"§3.1 states whether the course-announcement channel is the LMS under study.","reviewer":"da","severity":"da_major_band","evidence_anchor":"absence: §3.1 and §4 — expected disclosure of whether the announcement channel is the LMS; checked §1, §3.1, §3.4, §4, §6","confidence":4,"source_kind":"reviewer","sub_claims":["SC-14"],"arbitration":"unresolved_author_query"},
    {"id":"S7","priority":"should_fix","verification_criteria":"§6 notes possible compression of outcome variance arising from compelled use and channel-based recruitment.","reviewer":"domain","severity":"major","evidence_anchor":"text: §4 'including course requirements and assessment schedules'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-29"]},
    {"id":"S8","priority":"should_fix","verification_criteria":"§4 claims monotonic robustness specifically rather than independence from the parametric assumption.","reviewer":"methodology","severity":"minor","evidence_anchor":"text: §4 'indicating that the association did not depend on the parametric assumption'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-10"]},
    {"id":"S9","priority":"should_fix","verification_criteria":"§3.4 states whether the power calculation is a priori or post hoc sensitivity, with the assumed effect size if a priori.","reviewer":"methodology","severity":"minor","evidence_anchor":"text: §3.4 'so the design was sensitive to small-to-moderate associations'","confidence":4,"source_kind":"reviewer","sub_claims":["SC-20"]},
    {"id":"S10","priority":"should_fix","verification_criteria":"The manuscript contains a data-, code-, and materials-availability statement.","reviewer":"methodology","severity":"minor","evidence_anchor":"absence: §3.3 and §7 — expected an availability statement; checked §3.2, §3.3, §3.4, §5, §6, §7, References","confidence":5,"source_kind":"reviewer","sub_claims":["SC-21"]},
    {"id":"S11","priority":"should_fix","verification_criteria":"The assumption checks are supported by a displayed plot or reported descriptive detail rather than asserted.","reviewer":"methodology+eic","severity":"minor","evidence_anchor":"text: §3.4 'Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-16"]},
    {"id":"S12","priority":"should_fix","verification_criteria":"A paragraph reconciles the source instrument's continuance context with the present acceptance/continuance-mixed operationalisation.","reviewer":"domain","severity":"minor","evidence_anchor":"text: §3.2 and References — 'Perceived usefulness and continued use of learning platforms'","confidence":3,"source_kind":"reviewer","sub_claims":["SC-7"]},
    {"id":"S13","priority":"should_fix","verification_criteria":"§2 cites the construct's primary definition, re-attributes the 'long proposed' claim to its origin, and states which formulation the six items descend from.","reviewer":"domain","severity":"major","evidence_anchor":"text: §2 'Research on technology acceptance has long proposed'","confidence":5,"source_kind":"reviewer","sub_claims":["SC-22"]},
    {"id":"S14","priority":"nice_to_fix","verification_criteria":"§4 reports r-squared numerically.","reviewer":"eic","severity":"minor","evidence_anchor":"text: §4 'The proportion of variance shared by the two measures was accordingly modest'","confidence":4,"source_kind":"reviewer","sub_claims":["SC-17"]},
    {"id":"S15","priority":"nice_to_fix","verification_criteria":"Whitfield (2019) is introduced in §2 or removed from §5.","reviewer":"eic","severity":"minor","evidence_anchor":"text: §5 'a possibility also raised in practitioner accounts of digital-environment onboarding (Whitfield, 2019)'","confidence":4,"source_kind":"reviewer","sub_claims":["SC-30"]}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review (EIC) — D5 warn, D6 block (repairable)
Key point: the manuscript's calibration is above tier norm and is explicitly not the problem; the problem is that calibration is being asked to serve as contribution, and neither the comparison nor the comparators can be verified. Three strengths logged (statistical reporting completeness, no claim drift across sections, accurate abstract/title). Recommends reclassification as a Research Note and states that if reference integrity cannot be repaired, no other work makes the manuscript publishable.

### Peer Reviewer 1 (Methodology) — D1 warn, D3 warn
Key point: the arithmetic is correct and was independently reproduced (CI and sensitivity floor both verified), but the two variables being correlated are under-discussed — common-method variance is undisclosed and the coarse one-item outcome has no latent-scale estimate, making r = .42 simultaneously a lower bound on the latent association and a plausible upper bound on the method-free one. Five strengths logged. Explicitly declined to score the absence of log data as a defect and explicitly stopped short of `block`.

### Peer Reviewer 2 (Domain) — D2 block (repairable)
Key point: the paper's restraint is its central virtue and no constructs, mediators, or structural model are being requested; the failure is that two named sources are made to warrant a magnitude comparison the manuscript never shows they contain, with no theoretical genealogy, no named comparison distribution, an unstated estimand, and a mandatory-use boundary condition omitted from Limitations. Three strengths logged. Every requested repair is citation, framing, or interpretation — none requires new data.

### Peer Reviewer 3 (Cross-disciplinary) — D4 warn
Key point: the paper does not overclaim in kind, it underspecifies in degree, at exactly the two points an institutional reader needs — the outcome has no defined referent, and the recruitment channel structurally excludes the low-perceived-usefulness students the onboarding implication targets. Three strengths logged. Explicitly declines to penalise the paper for being incremental.

### Devil's Advocate — D3 warn
Key point: no CRITICAL findings; the manuscript is unusually well-defended against the objections this seat normally reaches for first, and the failure modes that would justify a block reading were looked for and not found. Seven MAJOR objections, of which six are validated or partly validated by the panel and one (whether the announcement channel is the LMS) is unresolved and routed to an author query.

---

## Audit Flags

- `[PROVENANCE-STAMP-MISSING]` — the mandatory `reviewer_full` Review Panel Provenance block could not be filled. No stamp was supplied; no statement was inferred. **Blocks release of the letter until the handling editor supplies it.**
- `[CARD-ANOMALY: perspective]` — the R3 card opens with a self-corrected placeholder under a "Scoring Plan Dissent" heading ("Wait — that placeholder is not permitted. Correcting below."). Flagged, not repaired. The card is substantively complete below the artifact: `contract_role`, all six dimension scores, three strengths, and five weaknesses with typed anchors and per-finding confidence are present, and the D4 score is usable. No scoring consequence.
- `[PRE-PAPER-OUTPUTS-UNVERIFIABLE]` — `measurement_procedure.reviewer_must_output_before_paper` requires `contract_paraphrase` and `scoring_plan` from each seat. Neither was forwarded with the cards supplied to this phase. I cannot verify compliance from the material in hand and have not assumed either outcome. Verification is the dispatching layer's.
- `[FIELD-ANALYSIS-ITEM-NOT-CONVERTED]` — the field analysis flagged that the Abstract reports r and p but omits the confidence interval the body supplies, and assigned it to "the synthesiser's editorial pass." No reviewer card carries this finding. The Phase 2 boundary forbids this seat from authoring review comments, so it has **not** been converted into a roadmap item. Recorded here for the handling editor's discretion.
- No `[EXPRESSION-UNRECOGNISED]`, no `[DIMENSION-UNASSESSED]`, no `[PANEL-SHRUNK]`. All five cards usable; panel_size 5 intact.
