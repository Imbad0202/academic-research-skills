# Editorial Decision Package

**Contract:** `reviewer/reviewer_full/v2` · **Stage:** `reviewer_full_review` · **Baseline:** v3.20.0 · **Panel size:** 5 (all 5 cards usable; no seat dropped, no `[PANEL-SHRUNK]`)

---

## Part 0: Sprint-Contract Audit (mechanical)

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats | Scores | Verdict |
|-----|----------|----------------|-------------------------|--------|---------|
| D1 methodology_rigor | mandatory | methodology | methodology | `block` + `block_class: fatal` | `block(fatal)` |
| D2 domain_accuracy | mandatory | domain | domain | `block` (repairable) | `block` |
| D3 argumentative_coherence | mandatory | da, methodology | da, methodology | `block` (repairable), `block` (repairable) | `block` |
| D4 cross_disciplinary_relevance | high | perspective | perspective | `block` | `block` |
| D5 writing_and_structure | normal | eic | eic | `block` (no fatal; normal priority carries no fatal escalation) | `block` |
| D6 venue_fit_and_contribution | mandatory | eic | eic | `block` + `block_class: fatal` | `block(fatal)` |

Ineligible `not_assessed` values excluded from every numerator and denominator. No dimension is unassessed by its eligible seats; no `[DIMENSION-UNASSESSED]`. No scoring-plan dissent was declared by any seat (three cards emitted a placeholder dissent heading and withdrew it in-band — see Card-Hygiene Flags), so no fatality was minted from dissent.

`audit_verdict: block(fatal)`

`dimension_verdicts: [D1=block(fatal), D2=block, D3=block, D4=block, D5=block, D6=block(fatal)]`

### Step 2 — Failure-condition evaluation

| Cond | Sev | Cross-reviewer quantifier | Expression | Evaluation | Fired |
|------|-----|---------------------------|------------|------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 fatal (methodology, owner+eligible, mandatory) ✓; D6 fatal (eic, owner+eligible, mandatory) ✓ → `any mandatory` = true | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1, D2, D3, D6 all `block` | true |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 (n=1→owner) ✓, D2 (n=1→owner) ✓, D3 (n=2→both seats block) ✓, D6 (n=1→owner) ✓ → 4 ≥ 2 | true |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 = `block` (perspective) | true |
| F5 | 40 | any | any dimension scores 'warn' or worse | all six | true |
| F0 | 10 | all | every dimension scores 'pass' | none pass | false |

`fired_conditions: [F1, F2, F3, F4, F5]`

### Step 3 — Precedence and emission

Highest severity among fired conditions: **F1 (95)**. No tie.

`da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED, C5=VALIDATED, C6=VALIDATED, C7=VALIDATED]`

`editorial_decision=reject`

No `[DA-CRITICAL-VS-ACCEPT]` marker: the mechanical decision is `reject`, not `accept`. No `C<n>=REJECTED`, so no rejection rationales are due.

**Checker note:** the prior artifact `synthesis.a1.md` emitted zero `fired_conditions` lines (`[SYNTHESIS-PARSE]`). This package emits exactly one line of each of the four required forms, above.

### DA-CRITICAL adjudication basis (visibility, not veto)

| ID | Corroborating non-DA seats | Journal-Fit adjudication basis | Verdict |
|----|---------------------------|-------------------------------|---------|
| C1 causal/prescriptive conclusion from cross-sectional design | EIC W5, R1 (D3 + body), R2 W2, R3 W6 | Manuscript states its own standard (§1, §2 citing Ibarra 2023) and violates it (§5, §6); wholly internal | VALIDATED |
| C2 abstract r = .42 vs Results r = .24 | EIC W4, R1 W1, R2 W6, R3 W8 | Verbatim contradiction; R1's recomputation shows .24 is the internally consistent value | VALIDATED |
| C3 predictor partly determined by outcome (exposure window) | EIC W3 | Follows from the manuscript's own §3.3 definitions; only EIC among non-DA seats states it, and states it as the driver of his fatal D6 block | VALIDATED |
| C4 sample conditioned on the outcome; random vs volunteer contradiction | R1 W4+W10, R2 W7, R3 W5, EIC W7 | §3.2 contains both descriptions; mid-term recruitment structurally excludes pre-recruitment withdrawals | VALIDATED |
| C5 worldwide/dependable-strategy scope claim | EIC W5+W6, R2 W2+W3, R3 W6+W7 | §6 contradicts §5.1's own conceded single-course, single-interface limits | VALIDATED |
| C6 t(156) describes a sample appearing nowhere | R1 W2, EIC W8, R2 W12 | R1's recomputation confirms t = 3.02 at df = 156 yields the reported p, so df was used in an actual computation; neither 87 (df = 85) nor 142 (df = 140) is 156 | VALIDATED |
| C7 no ethics approval; students not informed of trace-data analysis | EIC W1, R1 W5, R2 W11, R3 W1+W2 | §3.2 discloses non-notification; no approval, waiver, or legal basis appears anywhere | VALIDATED |

All seven are validated and independently reinforce F1's action. None operates as an automatic veto; each is recorded with its corroboration and adjudication basis per the DA-visibility rule.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting "Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment." The manuscript was assessed by five reviewers under the `reviewer_full` panel: a Journal-Fit Reviewer, three peer reviewers (methodology; domain; cross-disciplinary/data governance), and a Devil's Advocate.

### Decision: Reject

The decision follows mechanically from the acceptance contract. Two mandatory dimensions carry fatal blocks from their owner seats — methodology rigor (D1) and venue fit and contribution (D6) — which fires F1 at severity 95. Four further conditions fired at lower severity and are subsumed by it.

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this run received no provenance stamp from the dispatching layer. In `reviewer_full` mode this block is mandatory and may not be inferred, so no statement about model family or cross-model slot activity is made here, in either direction. **Readers should not infer model independence across the five seats.** The dispatching layer must supply the stamp (cross-model slot active / single-family disclosure / dispatch-failure fallback) before this letter is released.

### Consensus Analysis

Counted over the four non-DA reviewers (EIC = Journal-Fit; R1 = methodology; R2 = domain; R3 = cross-disciplinary/governance). Denominator is always 4; `not-mentioned` is silence, never agreement and never opposition.

#### Points of agreement

- **[CONSENSUS-4]** The abstract's headline coefficient (r = .42) contradicts the Results (r = .24). *EIC W4, R1 W1, R2 W6, R3 W8.* R1's recomputation establishes .24 as the internally consistent value, so .42 is unsupported and occupies the most-cited surface in the paper.
- **[CONSENSUS-4]** §5 and §6 assert causation and worldwide institutional scope, abandoning the correlational standard set in §1 and the audit cited in §2. *EIC W5, R1 (D3), R2 W2, R3 W6.*
- **[CONSENSUS-4]** No ethics or IRB statement exists, and §3.2 discloses that students were not informed their dashboard activity would be analysed; consent covered the survey only. *EIC W1, R1 W5, R2 W11, R3 W1/W2.* All four treat this as a gate on the log-based analyses rather than a limitation; R2 raises it while explicitly deferring adjudication (confidence 3).
- **[CONSENSUS-4]** §3.2 gives two mutually exclusive sampling descriptions ("random sample" vs. volunteers who "chose to respond"), and no response rate is reported against an enrolment of "several hundred." *EIC W7, R1 W10, R2 W7, R3 W5.*
- **[CONSENSUS-3]** The reported statistics cannot be reconciled with one another: df = 156 against 87 respondents, Table 2's 127 against a stated 142, t(140) = 1.31 paired with p = .008, and two arithmetically unreachable summaries (M = 3.847 at n = 87; SD = 0.10 at n = 10, M = 3.00). *EIC W8/W11/W13/W14, R1 W2/W3/W7/W8/W9, R2 W12/W13.* **Silent seat: R3**, who states he is not recomputing the statistics.
- **[CONSENSUS-3]** §2 attributes to Ferro & Nakamura (2021) the opposite of what that source's own title reports, and the inverted reading is carried forward into §5's equity argument. *EIC W10, R2 W1, R3 W9.* **Silent seat: R1**, consistent with his declared blind spot on literature representation.
- **Corroborated (2/4, no conflict)** — action-bearing but below the consensus bar: all fifteen DOIs use the reserved 10.5555 test prefix and nine of fifteen entries are never cited (*EIC W2, R2 W5/W8*); "retention" as operationalised (one course's final assessment) is not the retention construct invoked in §1 and §6 (*EIC W6, R2 W3* — R3's W6/W7 addresses transport of implications rather than construct identity, so it is not counted here); the SRL frame is not load-bearing and "mediating construct" is asserted with no mediation model (*R1 W15, R2 W4*); the course retention base rate is never reported (*R1 W13, R3 W7*).
- **Single-reviewer findings** (weighted by confidence, not arbitrated): the exposure-window artifact — session counts accrue over the same term whose completion they predict, so withdrawal truncates the accumulation window (*EIC W3, confidence 5; DA C3 corroborates but does not count toward the four*); no covariate-adjusted model, no confidence intervals, no effect size beyond r (*R1 W11/W12, confidence 5, owner seat for D1*); the intervention's plausible harm went unmeasured despite §2's own literature (*R3 W4, confidence 4, owner seat for D4*); the dashboard artefact is never documented (*EIC W9, confidence 5, owner seat for D5*). Each is retained at full weight: the raising seat owns the dimension the finding falls in.

#### Points of disagreement

**[SPLIT-1] Whether a corrected version of *these data* can constitute a contribution.** `agree = 1` (EIC W3: the deficit is the absence of a locatable increment, and "text revision cannot supply it" — scored fatal on D6). `conflict = 2` (R2: the empirical core "could survive correction… substantive rework, not retraction"; R3: a re-scoped version "would be a modest but honest contribution"). `silent = 1` (R1 — D6 outside his remit).

- **Editor's resolution:** EIC's fatal D6 block stands, and the dissent is recorded as substantive rather than overruled. Two grounds. First, expertise/role scoping: D6 is eligible to the `eic` seat alone under this contract, so the venue-contribution judgment is not one R2 and R3 were seated to make, and neither claims otherwise. Second, on inspection the positions are scope-distinct rather than contradictory. R2 and R3 are describing what a *redesigned* study could contribute — R3 enumerates five preconditions including a rebuilt sampling frame, and R2's own remedy "shrinks the stated contribution considerably, which the venue-fit reviewer should weigh." R1's remedy set requires the analysis dataset plus a full-cohort frame. None of the three asserts that an increment is recoverable from the 142 cases as sampled. That is precisely EIC's claim, and it is unopposed at its own scope. The dissent's content — that this research question is worth pursuing on a defensible design — is carried forward into Part 2 as guidance, not as a revision path at this venue.

**Clarification, not a split (ethics repairability).** EIC W1 and R1 W5 state that an absent authorisation cannot be repaired by revision; R3 W1 agrees the conduct defect is not a limitation, while R3 W2 notes that *if approval already exists*, its non-reporting is a reporting repair. These are compatible conditionals, not competing severities: documentation of pre-existing approval is a reporting fix; retroactive authorisation for an analysis already run is not available. Both readings converge on the same remedy set in R1 below.

### Decision Rationale

Two independent fatal blocks drive this decision, and they are of different kinds.

The methodology block is evidentiary. R1 recomputed every reported statistic and found that some pairs reconcile — r = .24 at n = 142 does give t = 2.93, p = .0040 — while others cannot. Because t = 3.02 at df = 156 *does* yield the reported p = .003, the degrees of freedom were used in an executed computation rather than mistyped, which means the perceived-control test was run on a sample the manuscript never describes. Two further values (M = 3.847 at n = 87 on an integer 1–5 item; SD = 0.10 at n = 10, M = 3.00) are unreachable by any response set, not merely inconsistent. R1 declined to overclaim here: he found three of the discrepancies directional and all three inflating, and explicitly refused to characterise the remainder that way. What survives that discount is still decisive — three independent inflating errors coexisting with two impossible summaries cannot be adjudicated from the manuscript alone, and no data or code availability statement exists through which anyone could adjudicate them. Separately and independently of the arithmetic, mid-term recruitment against an end-of-term outcome conditions the sample on partial survival, which no reanalysis of these 142 cases repairs.

The contribution block is structural. The field already holds systematic reviews establishing that dashboard-outcome evidence is thin, heterogeneous, and correlational — a conclusion §2 itself restates. Once the abstract's coefficient is corrected, the causal verbs of §5–§6 withdrawn, and the exposure-window confound acknowledged, no statement remains that a reader of those reviews could not already make. That is the absence of an increment rather than an oversold one.

Layered on both: the log-based analyses, which carry the headline result, rest on data students were never told would be analysed, with no approval statement anywhere. All four non-DA reviewers treat this as prior to scientific merit.

The panel's dissent is recorded and not softened. R2, R3, and the Devil's Advocate each identify a claim that could be defended — a small positive association between dashboard session counts and course completion, among students still enrolled and volunteering at mid-term, direction and mechanism unresolved. That is worth pursuing. It requires a different study, not a revision of this one.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | No locatable contribution increment over the existing systematic-review consensus; the engagement measure accrues over the same interval whose completion it predicts, so the association is not separable from time-in-course | EIC (fatal, D6); R2 partially corroborates | text: §1 "The present study contributes to this literature by examining the association between dashboard engagement and course retention in a single large undergraduate course" | R9 (with R4) |
| 2 | Reported sample sizes, degrees of freedom, and summary statistics cannot be reconciled with one another or with any described dataset; two values are arithmetically unreachable, and no data or code is available to adjudicate | R1 (fatal, D1); EIC, R2, DA corroborate | absence: manuscript-wide reporting apparatus — expected a data or analysis-code availability statement permitting independent reconciliation of the reported statistics; checked §3.4, §4.1-4.3, Tables 1-2, and the end matter following §6 | R2 |
| 3 | Trace data analysed without notice to participants, with no ethics approval, consent waiver, or data-protection basis stated anywhere | EIC, R1, R3 (Critical); R2 corroborates; DA C7 | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | R1 |

The causal-overreach cluster (D3, blocked repairable by both eligible seats) ranks below these three: all three seats that scored or discussed it agree it is a rewriting job, and it cannot be undertaken until the numbers beneath it are known.

### Card-Hygiene Flags (advisory; flagged, not fixed)

Three cards — methodology, domain, perspective — opened with a `## Scoring Plan Dissent` heading containing a placeholder, then withdrew it in-band ("Correction: per protocol I omit the section entirely"; "Wait — that placeholder is not permitted"; "Actually, per protocol I omit the section entirely"). The protocol requires whole-section omission. No dissent was in fact declared on any dimension, so the audit arithmetic is unaffected and no fatality arises from dissent. Flagged for the Phase 1 owner; not repaired here, per the phase boundary.

---

## Part 2: Requirements for Any Future Version of This Work

> **This is not a revise-and-resubmit invitation at this venue.** The decision is Reject, and two of the blocks are not addressable by revising this manuscript. What follows is the requirement set the panel identified for a defensible study on this question, provided under the constructive-feedback obligation that attaches to a Reject. Items are traced to the reviewer findings that generated them; no requirement originates with the editor.

> **Sub-claim column:** this synthesis ran in sprint-contract (arithmetic) mode, in which the Step 1b sub-claim inventory does not apply. Traceability is carried instead by the Source column, which names the originating card findings directly.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Establish and document the ethical and legal basis for analysing dashboard logs — approval body, protocol number, consent or waiver scope, data-protection basis, de-identification, retention — or withdraw every log-based analysis | — | Critical | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | 5 — direct editorial responsibility for ethics-statement screening on trace-data submissions | EIC W1; R1 W5; R3 W1/W2; DA C7 | P1 | Not estimable — depends on whether approval pre-exists; withdrawal path immediate |
| R2 | Release the analysis dataset and code, a per-analysis N table, and reconcile every reported statistic against them: r, all df, all p, Table 2's group sizes, the GRIM failure at M = 3.847, and the GRIMMER failure at SD = 0.10 | — | Critical | absence: manuscript-wide reporting apparatus — expected a data or analysis-code availability statement permitting independent reconciliation of the reported statistics; checked §3.4, §4.1-4.3, Tables 1-2, and the end matter following §6 | 4 — pattern-level inference from six verified recomputations | R1 W6 (with W1/W2/W3/W7/W8/W9); EIC W8; R2 W12/W13; DA C6/M2/M3/M4 | P1 | 2–4 weeks if data exist |
| R3 | Rebuild the sampling frame from full-cohort logs including pre-recruitment withdrawals; report eligible enrolment and response rate; delete "random sample" and state the frame as it was ("students still enrolled and volunteering at mid-term") | — | Critical | text: §3.2 "Midway through the term, an announcement was posted to the course LMS inviting students to complete a short survey" | 5 — selection bias in learning-analytics trace samples is R1's primary specialization | R1 W4/W10; R3 W5; EIC W7; R2 W7; DA C4 | P1 | 4–6 weeks (new data extraction) |
| R4 | Correct the exposure-window artifact: normalise session counts to a common pre-outcome window or restrict counting to a fixed observation interval, and report how much of the association survives | — | Critical | text: §1 "The present study contributes to this literature by examining the association between dashboard engagement and course retention in a single large undergraduate course" | 5 — editorial baseline for this submission class | EIC W3; DA C3 | P1 | 1–2 weeks once R2/R3 are done |
| R5 | Replace the point-biserial-as-Pearson analysis and median split with covariate-adjusted logistic regression (prior achievement, credit load, demographics); report the retention base rate, confidence intervals on every estimate, and effect sizes | — | Major | text: §3.4 "Associations between continuous measures were assessed with Pearson correlations." | 5 — standard modelling requirement for binary outcomes in observational educational data | R1 W11/W12/W13; R3 W7 (base rate) | P1 | 2–3 weeks |
| R6 | Correct the Ferro & Nakamura attribution and rebuild the §2 equity paragraph and §5's alignment reading on the source's actual finding; replace all fifteen placeholder 10.5555 DOIs with verifiable citations; cite or remove the nine uncited entries; attribute the gateway-attrition and SRL-model premises | — | Critical | text: §2 and References, "Dashboards have been shown to reliably improve outcomes for lower-achieving students" attributed to "When dashboards demotivate: Peer comparison and the lower-achieving student" | 5 — contradiction is internal to the manuscript and does not depend on retrieving the source | R2 W1/W5/W8; EIC W2/W10; R3 W9; DA M1 | P1 | 1–2 weeks |
| R7 | Rewrite the abstract, §5, and §6 in associational terms bounded to one course and one interface: align the reported coefficient with the analysis of record and state which value that is; remove "improved," "raises the probability," "dependable strategy," "worldwide," "generalizable"; remove the abstract's SRL-behaviour claim or add an actual SRL measure; drop "mediating construct" absent an estimated indirect path | — | Critical | text: §5 "The central finding of this study is that dashboard engagement improved course retention" contradicting §1 "We are careful throughout to distinguish the pattern in the data from the causal story" | 5 — direct within-document comparison, no domain expertise required | DA C1/C2/C5/M5; EIC W4/W5; R1 W1/W15; R2 W2/W4/W6; R3 W6/W8 | P1 | 1–2 weeks, after R2 |
| R8 | Re-label the outcome as within-course completion throughout; remove programme-level, institutional-persistence, attrition, and gateway framing unless year-level and enrolment-continuation data are added | — | Major | text: §3.3 "was coded dichotomously as whether the student remained enrolled and completed the final assessment", §6 "practical and generalizable lever for supporting student success at scale" | 5 — core distinction in the retention literature the paper invokes | R2 W3; EIC W6; DA M7 | P1 | 3–5 days |
| R9 | Identify and state a specific claim the study licenses that a reader of the existing dashboard-outcome systematic reviews could not already make, engaging those reviews directly — or reposition the work | — | Critical | text: §1 "The present study contributes to this literature by examining the association between dashboard engagement and course retention in a single large undergraduate course" | 5 — editorial baseline for this submission class | EIC W3 (fatal D6); R2 W5 (partial) | P1 | Not addressable within this manuscript — see SPLIT-1 |

### Required Item Details

**R1 — Ethical and legal basis for trace-data analysis**
- **Acceptance criteria**: The manuscript states an approval body, protocol identifier, the consent or waiver scope covering secondary analysis of dashboard logs, a data-protection legal basis, a de-identification description, and a retention plan; or every log-derived analysis is removed and the manuscript's claims are rebuilt on the consented survey data alone.

**R2 — Reported-statistics reconciliation against released data**
- **Acceptance criteria**: A data and code availability statement is present, a per-analysis N table accompanies §4, and each of the following resolves against the released data: the focal r, the perceived-control df, the exam-comparison t and p, Table 2's group sizes against the stated 142, the perceived-control mean at its stated n, and the clarity item's SD.

**R3 — Full-cohort sampling frame**
- **Acceptance criteria**: The sampling frame is the full course section including students who withdrew before the recruitment window, eligible enrolment and response rate are both reported as numbers, and the word "random" no longer appears in §3.2 unless a probability sampling procedure is documented.

**R4 — Exposure-window correction**
- **Acceptance criteria**: Dashboard engagement is either normalised to time enrolled or counted within a fixed window that closes before any student's withdrawal, and the manuscript reports the association both before and after this correction.

**R5 — Adjusted analytic model with precision estimates**
- **Acceptance criteria**: The binary retention outcome is modelled by logistic regression with at least prior achievement and credit load as covariates, the retention base rate is reported as a count and proportion, and every reported estimate carries a confidence interval.

**R6 — Citation record**
- **Acceptance criteria**: The Ferro & Nakamura claim in §2 matches that source's actual finding and any argument built on the prior reading is rewritten, every reference resolves to a registered DOI, and no reference-list entry is uncited while no in-text claim requiring attribution lacks one.

**R7 — Claim calibration across abstract, Discussion, and Conclusion**
- **Acceptance criteria**: No causal verb, probability-raising claim, dependability claim, or cross-institutional scope claim appears in the abstract, §5, or §6; the abstract's coefficient matches §4.2 and the analysis of record is identified; and no construct is described as measured or mediating unless a corresponding measure or model exists in §3.

**R8 — Outcome construct labelling**
- **Acceptance criteria**: The outcome is named as within-course completion wherever it appears, including the title and abstract, and no implication is drawn about institutional persistence, undergraduate attrition, or gateway-course risk without data supporting it.

**R9 — Contribution statement**
- **Acceptance criteria**: §1 states a specific claim this study licenses that the cited dashboard-outcome review literature does not already support, that literature is engaged by name in §2 and §5, and the claim is one the corrected analyses in R2–R5 actually sustain.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | Document the dashboard artefact: figure or annotated screenshot, framing of the peer-comparison band, display thresholds, any accompanying prompts | — | Major | absence: §3.1 and the §4 exhibit set — expected a figure or annotated screenshot documenting the dashboard interface and its peer-comparison band; checked §1, §3.1, §3.3, §4.1, §4.2, §4.3, Table 1, Table 2, §5.1 | 5 — venue norms for this track require the artefact to be shown | EIC W9 | P2 | 2–3 days |
| S2 | Report whatever harm analyses the data permit — subgroup by prior achievement, goal-orientation moderator, exposure of non-retained students to unfavourable comparisons — and state plainly which harm questions the design cannot answer | — | Major | text: §2 "Being shown one's position relative to peers can discourage struggling students rather than mobilize them" | 4 — algorithmic accountability review of student-facing analytics deployments | R3 W4 | P2 | 1–2 weeks |
| S3 | If any institutional implication is retained, supply the parameters a deployment decision needs: course retention base rate, withdrawal-timing distribution, dose–response across session counts, cost, and comparison against alternative supports | — | Major | absence: §6 institutional recommendation — expected a course retention base rate, a withdrawal timing distribution, dose-response information across session counts, a deployment cost figure, and comparison against alternative retention supports; checked §4.1, §4.2, §4.3, Table 1, Table 2, and §5 | 5 — advised three campuses on whether to fund dashboard rollouts | R3 W7 | P2 | 1–2 weeks (moot if R8 removes the institutional claims) |
| S4 | Justify the thirty-minute sessionization threshold on grounds other than platform default, and report sensitivity of the correlation and group assignment across alternative windows | — | Major | text: §3.3 "following the platform's default sessionization rule" | 4 — definitional gap explicit; magnitude of influence unknowable without the data | R1 W14 | P2 | 3–5 days |
| S5 | Provide reliability or validity evidence for the perceived-control and clarity items, or replace them with multi-item scales | — | Major | text: §3.3 "single-item overall ratings are common in dashboard studies to limit survey burden" | 5 — measurement-validation standards for latent constructs in educational research | R1 W16 | P2 | New instrument required |
| S6 | Operationalise the final-exam outcome in §3.3: scoring, weighting, administration timing, and treatment of non-sitters | — | Minor | absence: §3.3 Measures — expected an operational definition of the final-exam outcome including scoring and administration timing; checked §3.1, §3.2, §3.3, §3.4, §4.1, Table 1, §4.3, Table 2 | 5 — straightforward completeness check of the Measures subsection | EIC W12 | P3 | 1 day |
| S7 | Add a per-measure n column to Table 1, round the perceived-control mean to the precision the ordinal scale supports, and fold the clarity item into a table row or write it as prose rather than raw variable assignments | — | Minor | absence: Table 1 — expected a per-measure n column separating the 142-case log sample from the 87-case item subsample; checked Table 1 header, §3.2 sampling text, and the §4.1 narrative | 5 — the table's columns are visible and contain no n | R1 W17; EIC W13/W14 | P3 | 1 day |
| S8 | Extend §5.1 to cover the consent question and the unmeasured-harm question, and state the sampling frame's exclusion of early withdrawals | — | Minor | text: §5.1 "Several limitations qualify these findings. First, dashboard engagement was operationalized narrowly as session counts" | 4 — limitations-scoping review across analytics deployment appraisals | R3 W3 | P3 | 1 day |
| S9 | Report the distribution of majors and year levels, or delete the disciplinary-breadth claim in §3.1 and the generalisation it supports in §6 | — | Minor | absence: §3.1 sample description — expected a reported distribution of majors or year levels evidencing disciplinary breadth; checked §3.1, §3.2, §4.1, Table 1, and Table 2 | 4 — based on what a reader would need to accept the breadth claim | R2 W9 | P3 | 1 day |
| S10 | Reconcile the SRL phase terminology between §1 (dashboard feedback in the reflective phase) and §2 (forethought and self-monitoring), or acknowledge the shift | — | Minor | text: §2 "dashboards are hypothesized to support the forethought and self-monitoring phases of learning" and §1 "phases of forethought, performance, and reflection" | 4 — standard phase definitions in the SRL tradition | R2 W10 | P3 | Half a day |

Every row above carries the driving finding's transported Severity, typed Evidence Anchor, and per-finding Confidence, copied from the reviewer cards and not re-derived. No `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` tags are required: all five cards carry per-finding severity and confidence in the current format.

### Roadmap (Schema 7 machine form)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "reject",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": "eic", "source_kind": "reviewer", "severity": "critical", "confidence": 5, "evidence_anchor": "text: §3.2 \"Students were not informed that their dashboard activity data would be analyzed for this study.\"", "verification_criteria": "Approval body, protocol identifier, consent or waiver scope covering secondary log analysis, data-protection basis, de-identification, and retention plan are all stated; or all log-based analyses are removed."},
    {"id": "R2", "priority": "must_fix", "reviewer": "methodology", "source_kind": "reviewer", "severity": "critical", "confidence": 4, "evidence_anchor": "absence: manuscript-wide reporting apparatus — expected a data or analysis-code availability statement permitting independent reconciliation of the reported statistics; checked §3.4, §4.1-4.3, Tables 1-2, and the end matter following §6", "verification_criteria": "Data and code availability statement present, per-analysis N table accompanies §4, and the focal r, perceived-control df, exam t/p, Table 2 group sizes, perceived-control mean, and clarity-item SD each reconcile against the released data."},
    {"id": "R3", "priority": "must_fix", "reviewer": "methodology", "source_kind": "reviewer", "severity": "critical", "confidence": 5, "evidence_anchor": "text: §3.2 \"Midway through the term, an announcement was posted to the course LMS inviting students to complete a short survey\"", "verification_criteria": "Sampling frame covers the full section including pre-recruitment withdrawals; eligible enrolment and response rate reported numerically; \"random\" removed unless a probability procedure is documented."},
    {"id": "R4", "priority": "must_fix", "reviewer": "eic", "source_kind": "reviewer", "severity": "critical", "confidence": 5, "evidence_anchor": "text: §1 \"The present study contributes to this literature by examining the association between dashboard engagement and course retention in a single large undergraduate course\"", "verification_criteria": "Engagement is normalised to time enrolled or counted in a window closing before any withdrawal, and the association is reported both before and after correction."},
    {"id": "R5", "priority": "must_fix", "reviewer": "methodology", "source_kind": "reviewer", "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.4 \"Associations between continuous measures were assessed with Pearson correlations.\"", "verification_criteria": "Binary retention modelled by logistic regression with prior achievement and credit load as covariates; retention base rate reported as count and proportion; every estimate carries a confidence interval."},
    {"id": "R6", "priority": "must_fix", "reviewer": "domain", "source_kind": "reviewer", "severity": "critical", "confidence": 5, "evidence_anchor": "text: §2 and References, \"Dashboards have been shown to reliably improve outcomes for lower-achieving students\" attributed to \"When dashboards demotivate: Peer comparison and the lower-achieving student\"", "verification_criteria": "Ferro & Nakamura claim matches the source's finding and dependent arguments are rewritten; every reference resolves to a registered DOI; no uncited entries and no unattributed load-bearing claims remain."},
    {"id": "R7", "priority": "must_fix", "reviewer": "da", "source_kind": "reviewer", "severity": "critical", "confidence": 5, "evidence_anchor": "text: §5 \"The central finding of this study is that dashboard engagement improved course retention\" contradicting §1 \"We are careful throughout to distinguish the pattern in the data from the causal story\"", "verification_criteria": "No causal verb, probability-raising claim, dependability claim, or cross-institutional scope claim in abstract, §5, or §6; abstract coefficient matches §4.2 with the analysis of record identified; no construct described as measured or mediating without a corresponding measure or model."},
    {"id": "R8", "priority": "must_fix", "reviewer": "domain", "source_kind": "reviewer", "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.3 \"was coded dichotomously as whether the student remained enrolled and completed the final assessment\", §6 \"practical and generalizable lever for supporting student success at scale\"", "verification_criteria": "Outcome named as within-course completion throughout including title and abstract; no institutional-persistence, attrition, or gateway implications without supporting data."},
    {"id": "R9", "priority": "must_fix", "reviewer": "eic", "source_kind": "reviewer", "severity": "critical", "confidence": 5, "evidence_anchor": "text: §1 \"The present study contributes to this literature by examining the association between dashboard engagement and course retention in a single large undergraduate course\"", "verification_criteria": "§1 states a specific claim the study licenses that the cited dashboard-outcome review literature does not already support; that literature is engaged by name in §2 and §5; the claim is sustained by the corrected analyses."},
    {"id": "S1", "priority": "should_fix", "reviewer": "eic", "source_kind": "reviewer", "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.1 and the §4 exhibit set — expected a figure or annotated screenshot documenting the dashboard interface and its peer-comparison band; checked §1, §3.1, §3.3, §4.1, §4.2, §4.3, Table 1, Table 2, §5.1", "verification_criteria": "A figure or annotated screenshot documents the interface, the comparison-band framing, display thresholds, and any accompanying prompts."},
    {"id": "S2", "priority": "should_fix", "reviewer": "perspective", "source_kind": "reviewer", "severity": "major", "confidence": 4, "evidence_anchor": "text: §2 \"Being shown one's position relative to peers can discourage struggling students rather than mobilize them\"", "verification_criteria": "Subgroup analysis by prior achievement, a goal-orientation moderator where data permit, and an exposure analysis for non-retained students are reported, with unanswerable harm questions stated explicitly."},
    {"id": "S3", "priority": "should_fix", "reviewer": "perspective", "source_kind": "reviewer", "severity": "major", "confidence": 5, "evidence_anchor": "absence: §6 institutional recommendation — expected a course retention base rate, a withdrawal timing distribution, dose-response information across session counts, a deployment cost figure, and comparison against alternative retention supports; checked §4.1, §4.2, §4.3, Table 1, Table 2, and §5", "verification_criteria": "Any retained institutional implication is accompanied by base rate, withdrawal-timing distribution, dose-response, cost, and comparison against alternatives; otherwise the implication is removed."},
    {"id": "S4", "priority": "should_fix", "reviewer": "methodology", "source_kind": "reviewer", "severity": "major", "confidence": 4, "evidence_anchor": "text: §3.3 \"following the platform's default sessionization rule\"", "verification_criteria": "The sessionization threshold is justified on substantive grounds and sensitivity of the correlation and group assignment across alternative windows is reported."},
    {"id": "S5", "priority": "should_fix", "reviewer": "methodology", "source_kind": "reviewer", "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.3 \"single-item overall ratings are common in dashboard studies to limit survey burden\"", "verification_criteria": "Reliability or validity evidence is reported for each focal construct, or single items are replaced by multi-item scales."},
    {"id": "S6", "priority": "nice_to_fix", "reviewer": "eic", "source_kind": "reviewer", "severity": "minor", "confidence": 5, "evidence_anchor": "absence: §3.3 Measures — expected an operational definition of the final-exam outcome including scoring and administration timing; checked §3.1, §3.2, §3.3, §3.4, §4.1, Table 1, §4.3, Table 2", "verification_criteria": "§3.3 defines the final-exam outcome's scoring, weighting, administration timing, and treatment of non-sitters."},
    {"id": "S7", "priority": "nice_to_fix", "reviewer": "methodology", "source_kind": "reviewer", "severity": "minor", "confidence": 5, "evidence_anchor": "absence: Table 1 — expected a per-measure n column separating the 142-case log sample from the 87-case item subsample; checked Table 1 header, §3.2 sampling text, and the §4.1 narrative", "verification_criteria": "Table 1 carries a per-measure n column, the perceived-control mean uses scale-appropriate precision, and the clarity item appears as a table row or prose rather than raw variable assignments."},
    {"id": "S8", "priority": "nice_to_fix", "reviewer": "perspective", "source_kind": "reviewer", "severity": "minor", "confidence": 4, "evidence_anchor": "text: §5.1 \"Several limitations qualify these findings. First, dashboard engagement was operationalized narrowly as session counts\"", "verification_criteria": "§5.1 names the consent question, the unmeasured-harm question, and the frame's exclusion of early withdrawals."},
    {"id": "S9", "priority": "nice_to_fix", "reviewer": "domain", "source_kind": "reviewer", "severity": "minor", "confidence": 4, "evidence_anchor": "absence: §3.1 sample description — expected a reported distribution of majors or year levels evidencing disciplinary breadth; checked §3.1, §3.2, §4.1, Table 1, and Table 2", "verification_criteria": "A distribution of majors and year levels is reported, or the disciplinary-breadth claim and the generalisation resting on it are deleted."},
    {"id": "S10", "priority": "nice_to_fix", "reviewer": "domain", "source_kind": "reviewer", "severity": "minor", "confidence": 4, "evidence_anchor": "text: §2 \"dashboards are hypothesized to support the forethought and self-monitoring phases of learning\" and §1 \"phases of forethought, performance, and reflection\"", "verification_criteria": "§1 and §2 locate the dashboard mechanism in the same SRL phase, or the shift is explicitly acknowledged."}
  ]
}
```

### Revision Checklist

#### Priority 1 — Structural (not completable within this manuscript; R1–R4 and R9 require new data or a new study)
- [ ] R1: Document the ethical and legal basis for log analysis, or withdraw the log-based analyses
- [ ] R2: Release data and code; reconcile every reported statistic
- [ ] R3: Rebuild the sampling frame from full-cohort logs; report response rate; delete "random"
- [ ] R4: Normalise or window-restrict the engagement measure against exposure time
- [ ] R5: Fit a covariate-adjusted logistic model; report base rate, CIs, effect sizes
- [ ] R6: Correct the Ferro & Nakamura attribution; supply verifiable citations; fix the uncited/unattributed asymmetry
- [ ] R7: Strip causal and global-scope language; align the abstract's coefficient; remove unmeasured-construct claims
- [ ] R8: Re-label the outcome as within-course completion; drop institutional implications
- [ ] R9: Identify a contribution the existing review literature does not already supply, or reposition

#### Priority 2 — Content supplementation (estimated 4–6 weeks, conditional on P1)
- [ ] S1: Document the dashboard artefact
- [ ] S2: Report the harm analyses the data permit; state what the design cannot answer
- [ ] S3: Supply deployment-decision parameters if any institutional claim is retained
- [ ] S4: Justify sessionization; report window sensitivity
- [ ] S5: Provide measurement validity evidence or multi-item scales

#### Priority 3 — Text and formatting (estimated 4–5 days)
- [ ] S6: Operationalise the final-exam outcome
- [ ] S7: Table 1 per-measure n, precision, clarity-item formatting
- [ ] S8: Extend the limitations to consent, harm, and the frame's exclusions
- [ ] S9: Report the major/year-level distribution or drop the breadth claim
- [ ] S10: Reconcile SRL phase terminology

### Deadline

Not applicable — this is a Reject, not a revision invitation. R1 through R4 and R9 cannot be discharged on the present dataset; a resubmission anywhere would be a new study rather than a revised manuscript.

### Forward guidance (per the constructive-feedback obligation on a Reject)

Three seats independently converged on the same defensible claim, and the panel records it as genuine rather than consolation: *in one introductory statistics course, among students still enrolled and volunteering at mid-term, dashboard session count showed a small positive association with course completion, with direction and mechanism unresolved.* Reaching that claim honestly requires the full-cohort frame (R3), exposure correction (R4), an adjusted model (R5), and reconciled statistics (R2), on a documented ethical basis (R1). The panel also credits real strengths that should survive into any future version: §2's engagement-proxy critique is accurate and turned reflexively on the authors' own measure, §3.3's operational definitions are specific enough that external reviewers could locate the inconsistencies at all, and §2's demotivation and goal-orientation account is the one place four reviewers found the field correctly represented.

### Response letter

If the authors pursue a resubmission elsewhere, `templates/revision_response_template.md` provides the point-by-point format; every R and S item above should receive an explicit response.

---

## Part 3: Reviewer Report Summary (Appendix)

### Step 1a — Panel matrix

| Dimension | Journal-Fit (EIC) | R1 (Methodology) | R2 (Domain) | R3 (Cross-disciplinary) | DA |
|-----------|-------------------|------------------|-------------|-------------------------|-----|
| Dimensions scored | D5 `block`, D6 `block(fatal)` | D1 `block(fatal)`, D3 `block` | D2 `block` | D4 `block` | D3 `block` |
| Confidence range on findings | 4–5 | 4–5 | 3–5 | 3–5 | 4–5 |
| Critical findings | 3 (W1, W2, W3) | 6 (W1–W6) | 2 (W1, W2) | 2 (W1, W6) | 7 (C1–C7) |
| Major findings | 8 | 10 | 10 | 5 | 8 |
| Minor findings | 3 | 1 | 2 | 1 | 0 (untabled, disclosed in body) |
| Key weaknesses | → Consensus Analysis | → Consensus Analysis | → Consensus Analysis | → Consensus Analysis | → DA adjudication table |

### Journal-Fit Reviewer (EIC)
- Dimensions: D5 `block`, D6 `block` + `fatal` | Confidence on the fatal: 5
- Key point: topic fit is not in question; the failure is the absence of a locatable increment over the existing systematic-review consensus, compounded by an exposure-window confound that no text revision reaches — plus two gates prior to scientific merit (ethics disclosure, unverifiable references).

### Peer Reviewer 1 — Methodology
- Dimensions: D1 `block` + `fatal`, D3 `block` (repairable) | Confidence on the fatal: 5
- Key point: six recomputations show three directional inflating errors and two arithmetically unreachable summaries; because t = 3.02 at df = 156 yields the reported p, the sample this test ran on is not the sample §3.2 describes, and the manuscript supplies nothing through which anyone could adjudicate it. He explicitly declined to claim all discrepancies were directional.

### Peer Reviewer 2 — Domain
- Dimensions: D2 `block` (repairable) | Confidence on the driving finding: 5
- Key point: Ferro & Nakamura (2021) is cited against its own finding, and the inversion does structural work in §2 and §5; the SRL frame constrains no prediction and "mediating construct" is asserted with no mediation; the reference list is decoupled from the argument. He stops short of fatal because the empirical core could survive substantive rework.

### Peer Reviewer 3 — Cross-disciplinary / Data Governance
- Dimensions: D4 `block` | Confidence on the driving findings: 4–5
- Key point: accessibility is broadly satisfied but export is not earned — §6's procurement recommendation to institutions worldwide rests on r = .24 in one course, on a mid-term volunteer sample that structurally excludes the students most likely to have been harmed by the unmeasured peer-comparison band, with no ethics, legal-basis, anonymisation, retention, or data-availability statement anywhere.

### Devil's Advocate
- Dimensions: D3 `block` (repairable) | 7 CRITICAL, 8 MAJOR
- Key point: a concede-and-proceed pattern — every concession is made where it costs nothing and withdrawn where it would cost something; §2 cites the audit of causal overreach and then commits the audited error. All 7 CRITICAL items validated on adjudication.

---

*Editorial scope note: this synthesis arbitrated the five Phase 1 cards and produced the decision and roadmap. It introduced no findings of its own; every roadmap item names its originating card finding. Revision-side work is not in scope for this phase. One input defect is outstanding and blocks release of this letter: the `reviewer_full` provenance stamp was not supplied by the dispatching layer.*
