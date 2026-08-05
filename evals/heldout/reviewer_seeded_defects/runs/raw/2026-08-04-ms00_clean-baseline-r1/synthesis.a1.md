# Editorial Decision Package

## Sprint Contract Audit (reviewer/reviewer_full/v2)

```
dimension_verdicts: [D1=block, D2=warn, D3=warn, D4=warn, D5=warn, D6=block]
fired_conditions: [F2, F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision
```

**Matrix construction (role-scoped, Step 1).** D1 ← methodology only (`block`, `block_class: repairable`). D2 ← domain only (`warn`). D3 ← da + methodology (both `warn`; worst = `warn`). D4 ← perspective only (`warn`). D5 ← eic only (`warn`). D6 ← eic only (`block`, `repairable`). All `not_assessed` values on ineligible seats were excluded from both numerator and denominator. Every dimension had at least one assessed eligible seat, so no `[DIMENSION-UNASSESSED]` abort. Audit verdict = `block`; **no seat declared a fatal block**, so no dimension renders as `block(fatal)`.

**Condition evaluation (Step 2).** F1 `false` (no fatal block on any mandatory dimension). F2 `true` (D1 and D6 each have ≥1 assessed eligible seat scoring `block`). F3 `true` (majority-of-eligible-seats predicate holds on D1, D2, D3, D6 → four mandatory dimensions at `warn` or worse; ≥2 satisfied). F4 `false` (D4, the only high-priority dimension, scores `warn`, not `block`). F5 `true`. F0 `false`.

**Precedence (Step 3).** Highest severity among fired conditions = F2 (90) → `editorial_decision=major_revision`. The DA card's CRITICAL table contains headers and zero rows, so the adjudication list is legitimately empty; no phantom IDs were minted.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript "Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students." It was assessed by a five-seat panel: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary), and a Devil's Advocate.

### Decision: Major Revision

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this synthesis received no provenance stamp from the dispatching layer. In `reviewer_full` mode this block is mandatory and its content may only be transcribed from that stamp, never inferred. Accordingly: **no cross-model slot activation is asserted, and no model independence among the five seats is claimed or implied.** The panel matrix below shows which seat produced which score; it does not and cannot show which model family produced each seat. Resolve the stamp before this letter is treated as carrying a provenance disclosure.

### Panel Matrix

| Dimension (priority) | Journal-Fit (eic) | R1 Methodology | R2 Domain | R3 Perspective | Devil's Advocate | Verdict |
|---|---|---|---|---|---|---|
| D1 methodology_rigor (mandatory) | — | **block** (repairable) | — | — | — | block |
| D2 domain_accuracy (mandatory) | — | — | **warn** | — | — | warn |
| D3 argumentative_coherence (mandatory) | — | **warn** | — | — | **warn** | warn |
| D4 cross_disciplinary_relevance (high) | — | — | — | **warn** | — | warn |
| D5 writing_and_structure (normal) | **warn** | — | — | — | — | warn |
| D6 venue_fit_and_contribution (mandatory) | **block** (repairable) | — | — | — | — | block |

`—` = ineligible seat or `not_assessed`; excluded from both numerator and denominator.

### Consensus Analysis

Weaknesses were decomposed into 23 atomic sub-claims before aggregation, so that a bundled objection could not be treated as resolved by partial support. Counting is over the four non-DA seats; **a seat's silence on a sub-claim is silence, not agreement and not opposition.** Sub-claims below the consensus bar are recorded at their true weight, not promoted.

#### Unanimous (CONSENSUS-4)

- **SC-16** — The five use categories are never enumerated and their response distribution is withheld. All four non-DA seats raised this independently (EIC W4, R1 W7, R2 W7, R3 W7); the DA also flags it. This is the only sub-claim on which the full panel converged.

#### Strong majority (CONSENSUS-3)

- **SC-1** — All six DOIs use the reserved `10.5555` test prefix with strictly sequential suffixes, and several journal titles are near-variants of real venues; the reference base cannot be verified from the manuscript. Raised by EIC (Critical, conf 5) and R2 (Major, conf 3); the factual pattern is corroborated by R3, who states the observation and explicitly declines a finding on it. **Silent seat: R1 (methodology).**
- **SC-2** — The canonical technology-acceptance sources (Davis; the UTAUT line) are absent and the interpretive frame is invoked but never named. Raised by EIC and R2; corroborated by R3 from the adjacent-reader side. **Silent seat: R1.**

#### Corroborated findings (two seats, no conflict — below the consensus bar, action-bearing)

- **SC-3** — No quantified prior distribution is supplied, so "consistent with prior technology-acceptance research" is untestable (EIC, R2; DA M6 corroborates).
- **SC-6** — The outcome construct is upgraded to "engagement" in the Abstract, Introduction framing, and Discussion, contradicting the paper's own §3.2 commitment (R2, R3; DA M3 corroborates).
- **SC-9** — Common-method variance is never named as a rival account of the association (R1, R3; DA M2 corroborates at conf 5).
- **SC-12** — The instrument's adaptation is undocumented and its validity is inherited rather than demonstrated (R1 Major, R2 Minor).
- **SC-13** — Log-based measurement was available; the self-report choice is narrated as an external constraint rather than justified (R3; R1 corroborates via the "relabeling does not discharge Vasquez" observation).
- **SC-14** — The onboarding implication presupposes a direction the paper declares undetermined, and delivers nothing a practitioner can act on (EIC reader-interest test, R3; DA M4 corroborates).
- **SC-18** — The power statement is indistinguishable from post-hoc sensitivity (R1; EIC S2 flags the same uncertainty at conf 4).

#### Single-reviewer findings (one seat, no conflict — weighted by confidence, not promoted)

SC-4 (R2, conf 4: a zero-order *r* is not commensurable with the field's path coefficients, and isolating one path is unjustified) · SC-5 (EIC, conf 5: below the full-article contribution threshold) · SC-7 (R1, conf 5: the single-item ordinal outcome makes .42 a floor of unquantifiable depth) · SC-10 (R1, conf 5: no denominator, so no response rate) · SC-11 (R3, conf 4: recruitment through the outcome's own medium) · SC-15 (R2, conf 4: institutional context unreported) · SC-19, SC-20, SC-21, SC-22, SC-23 (Minor).

Each of these carries full weight under the confidence-weighting rule because each was raised at confidence 4–5 by the seat that owns the relevant dimension. Three of them (SC-7, SC-10, SC-11) are additionally corroborated by the Devil's Advocate, which does not change their count over the four but does raise their standing.

#### Points of Disagreement

**SPLIT 1 — SC-8: is the Spearman coefficient an adequate robustness check for the ordinal outcome?**
R1 (Major, conf 5) argues it is not: with five categories the rank transformation produces massive ties, ρ is near-collinear with *r* (which is why ρ = .40 tracked *r* = .42), and the polyserial correlation is the estimator that speaks to the stated concern. R3 (S5) credits the Spearman report as pre-empting exactly this objection.

- **Editor's Resolution: R1 upheld.** Expertise-first — the psychometrics seat owns coarse-categorization behaviour and holds published work on attenuation under categorical measurement. Evidence-first — R2's independent audit (S1) observes that ρ "sits where a monotone-but-ordinal outcome would put it relative to the Pearson value," which is the mechanism R1 describes, not a refutation of it. R3's credit survives in narrowed form: the authors performed *a* check, which is above the norm for this genre, but that check does not license the manuscript's stated conclusion that the association "did not depend on the parametric assumption." Roadmap item R7.

**SPLIT 2 — SC-17: does the unshown scatterplot matter?**
EIC (W4, Major, conf 4) holds that the §3.4 assumption check is unverifiable because the figure is absent. R3 corroborates at Minor. R1 (S3) treats the same passage as a strength — assumption checking "reported rather than assumed," materially raising confidence that the coefficient is not artifactual.

- **Editor's Resolution: both positions stand and the remedy is additive.** These are not incompatible claims about the same fact: R1 credits the authors for *performing and reporting* the checks; EIC observes that a reader cannot *verify* them. Supplying the scatterplot satisfies EIC and R3 without withdrawing R1's credit. The EIC is a party to this split, so it was arbitrated on the evidence rather than referred back to that seat. Roadmap item R15.

**Overlap explicitly not double-counted.** R1's measurement critique of the dependent variable (SC-7, SC-8) and R3's data-availability critique (SC-13) are one underlying weakness observed from two seats, not two independent objections; they are counted once toward the D1 block. They also converge productively: R3's consented-linkage note (SC-21) is the forward remedy for R1's and the DA's common-method-variance objection (SC-9), and the roadmap presents them on one path.

**Convergence that did *not* occur, and its significance.** The contribution block (D6) is a single-seat judgment. R2 states explicitly that a bounded local estimate has real utility and that smallness is not being scored down; R3 states explicitly that a perception measure is legitimate on its own terms and that no volume of log data substitutes for it; R1 states explicitly that the study's ambition is appropriately small and declines to ask for a larger model. The block therefore is not a pile-on against small-scope work — it is a positioning-and-packaging judgment from the seat that owns venue fit, and that seat's own answer is that a well-positioned Research Note would pass. The panel's shape supports reading this as a venue-and-format problem plus an unmet comparability claim, not a quality verdict on the study's scale.

#### Surface-Form Parity Check (#216)

Run before any sub-claim's weight was set. Two artefacts required attention. First, the domain and perspective cards each open with a self-corrected placeholder fragment ("Wait — that line would constitute a placeholder. Removing it."). This is a card-hygiene defect and it **did not** reduce the weight of any sub-claim in those cards; both cards' substance was assessed against the manuscript. Second, the EIC's SC-1 finding is phrased in highly technical register and R3's corroboration of the same fact is an informal deferral; the finding gained weight because the DOI strings are printed in the manuscript and checkable, not because the phrasing was precise. Opposite-style counterfactual applied to both splits: neither outcome moves if the substance is rewritten in the other register. One confidence-based down-weighting stands and is not a surface-form judgment — R2's SC-1 confidence of 3 is that seat's own declared limit ("I can characterise the DOI prefix but cannot resolve these records from the manuscript alone").

### Devil's Advocate Adjudication

`da_critical_adjudications: []` — the DA card's CRITICAL table is empty. The DA's six MAJOR items were adjudicated in the ordinary channel and all six are carried into the roadmap: M1→R10, M2→R8, M3→R6, M4→R13, M5→S2, M6→R3. No DA item was rejected, so no rejection rationale is required. One DA observation is referred rather than actioned: the DA notes that .80 power for *r* ≥ .19 at *n* = 214 "sits essentially on the boundary" and defers to the methodology seat, which addressed the a-priori/post-hoc question but not the boundary point; the author should treat that as part of S1.

### Decision Rationale

The decision is mechanical under the sprint contract: F2 fired at severity 90 because two mandatory dimensions — methodology rigor and venue fit — each carry a `block` from their eligible seat, and F2's action is `major_revision`. F3 and F5 also fired but rank lower and do not alter the outcome.

Two boundaries deserve stating plainly. **Not Reject:** F1 did not fire. No seat declared a fatal block, and the Journal-Fit Reviewer set out its reasoning for withholding fatality — the topic is squarely in scope and the manuscript is conspicuously honest that its finding is not new, which is not converted into an aggravating factor. **Not Minor Revision:** two mandatory blocks cannot be cleared by supplementation. The methodology block rests on a stack in which the outcome variable's measurement is undocumented, the robustness check cannot detect the problem it is offered against, the sampling denominator is missing, and a rival account of the association is never raised; repairing it requires new computation, new disclosure, and rewriting of the magnitude interpretation. The contribution block requires either a rebuilt positioning against a quantified prior distribution or a reframing of the article to match its content.

What is genuinely strong is worth recording, because it is what makes revision viable: the correlational discipline holds across every section, the reverse pathway is named rather than gestured at, the sample accounting reconciles, the confidence interval reproduces from the reported *r* and *n*, and the ethics documentation is complete. All four seats credited these independently. The manuscript's problem is upstream of its execution.

**One escalation note that does not alter the decision.** The Journal-Fit Reviewer records that the reference-base finding "requires an editorial integrity check independent of dimension scoring." If the six DOIs cannot be resolved — as distinct from being anonymisation placeholders — that is a research-integrity matter outside this contract's scoring scope, and the editor must escalate rather than wait for a revision cycle. The mechanical decision stands as `major_revision`; roadmap item R1 is a precondition for every other item, because a methods critique of a manuscript with no resolvable evidence base is misdirected effort.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | The entire reference base is unverifiable — reserved `10.5555` test prefix with sequential suffixes — leaving the manuscript with no validated instrument, no comparison distribution, and no literature review | EIC (Critical, conf 5); R2 (Major, conf 3); R3 corroborates the pattern without a finding | text: §References — "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006" | R1 |
| 2 | D1 block — the magnitude of *r* = .42 has no defensible interpretation as submitted: single-item ordinal outcome, a robustness check that cannot detect coarse categorization, and two unquantified biases of opposing sign | R1 (Major, conf 5 across W3/W4/W5) | text: §4 Results — "indicating that the association did not depend on the parametric assumption" | R7 (with R8, R11) |
| 3 | D6 block — one bivariate association from one site, in seven-section article packaging, with no quantified prior distribution to position it against | EIC (Major, conf 5) | text: §7 Conclusion — "offered as an incremental, design-bounded contribution rather than a causal claim" | R5 (with R3) |

### Required Item Details

**R1 — Resolve the reference base.**
Source: EIC W1 (Critical, conf 5); R2 W5 (Major, conf 3); R3 corroborating observation. SC-1.
- **Acceptance criteria**: Every reference resolves to a retrievable record under a registered publisher prefix, or is replaced by a resolvable source; the cover letter states whether the `10.5555` DOIs were anonymisation placeholders or otherwise, and every claim that rested on a replaced source is re-verified against its new source.

**R2 — Rebuild the literature base and name the interpretive frame.**
Source: EIC W3 (Major, conf 5); R2 W1 (Major, conf 5); R3 W6 (Minor, conf 3). SC-2.
- **Acceptance criteria**: The canonical source for perceived usefulness and at least one subsequent framework source are cited, the interpretive frame is named explicitly at first use with its originating work, and the reader can identify which of the frame's constructs are and are not in play.

**R3 — Supply a quantified prior distribution and a falsification condition.**
Source: EIC W3 (Major, conf 5); R2 W1 (Major, conf 5); DA M6 (Major, conf 4). SC-3.
- **Acceptance criteria**: At least one pooled or synthesised estimate (or an explicit table of named prior coefficients) is reported with its range, *r* = .42 is located against it, and the manuscript states what value would have been judged inconsistent.

**R4 — State the commensurability of the compared quantities and justify isolating one path.**
Source: R2 W3 (Major, conf 4). SC-4.
- **Acceptance criteria**: The manuscript states whether the benchmark estimates are zero-order correlations, standardised path coefficients, or PU→intention associations, confirms that like is compared with like, and says in one paragraph what is gained and given up by extracting a single path from a joint framework.

**R5 — Align the packaging with the content, or add substance.**
Source: EIC W2 (Major, conf 5), with EIC W5 (Minor) subsumed. SC-5, SC-23.
- **Acceptance criteria**: Either the manuscript is resubmitted as a Research Note — Limitations folded into the Discussion, the separate Conclusion removed, positioning paragraph and comparison table present — or additional substance (a moderator, a second site, or log-based measurement) is added such that the full-article structure is carried by the content.

**R6 — Hold "self-reported use" throughout.**
Source: R2 W2 (Major, conf 4); R3 W1 (Major, conf 5); DA M3 (Major, conf 4). SC-6.
- **Acceptance criteria**: "Engagement" no longer denotes the measured outcome anywhere in the Abstract, Introduction, Discussion, or Conclusion; the terminal Abstract claim is restated in terms of self-reported access frequency; and the Introduction's opening framing no longer primes a behavioural reading.

**R7 — Report a polyserial estimate and withdraw the magnitude label.**
Source: R1 W3 and W4 (Major, conf 5); SPLIT 1 arbitrated in R1's favour. SC-7, SC-8.
- **Acceptance criteria**: A polyserial correlation is reported alongside *r*; the claim that the association "did not depend on the parametric assumption" is removed or restated to what Spearman's ρ actually establishes; and .42 is presented as a lower bound conditional on the measurement, with the small/moderate/strong label dropped and the unquantifiable single-item component named as such.

**R8 — Add the common-method-variance discussion and the two-sided bias bracket.**
Source: R1 W5 (Major, conf 5); DA M2 (Major, conf 5); R3 W5 corroborating note. SC-9.
- **Acceptance criteria**: The manuscript states that both variables were self-reported in one instrument at one sitting with adjacent items, names shared-method variance as a rival account of the association distinct from the self-report/log fidelity point already made, and states that the true magnitude is bracketed between attenuation and inflation of opposing sign.

**R9 — State the denominator and the response rate.**
Source: R1 W1 (Major, conf 5); DA M1 corroborating. SC-10.
- **Acceptance criteria**: The eligible undergraduate enrolment is reported, a response rate is computed from it, and the voluntary-response limitation is restated in terms bounded by that figure.

**R10 — Correct the recruitment-channel mechanism.**
Source: R3 W4 (Major, conf 4); DA M1 (Major, conf 4). SC-11.
- **Acceptance criteria**: The manuscript states whether the course-announcement channel is an LMS function, and if so identifies the consequence as selection on the dependent variable — capable of biasing the coefficient, not only the sample mean — with the direction stated as indeterminate on the reported evidence; supplying the institutional aggregate use distribution for comparison is the stronger repair and is credited if provided.

**R11 — Document the instrument.**
Source: R1 W2 (Major, conf 5); R2 W6 (Minor, conf 4); DA untabled corroboration. SC-12.
- **Acceptance criteria**: The six items are reproduced in an appendix; what was changed in adaptation is stated item by item; the source instrument's reliability figure is given; and either dimensionality evidence is reported or the "previously validated" claim is softened to internal consistency in the present sample.

**R12 — Give the design rationale for self-report in Methods.**
Source: R3 W2 (Major, conf 5); R1 corroborating observation. SC-13.
- **Acceptance criteria**: Two to three sentences in §3.1 or §3.2 state whether log-based measurement was considered, what stood in the way, and why the self-report proxy was judged adequate — with the Limitations sentence rewritten so that a design choice is no longer phrased as an imposed constraint. This item does not require the log study to be run.

**R13 — Resolve the onboarding implication.**
Source: EIC reader-interest finding (Major, conf 5); R3 W3 (Major, conf 4); DA M4 (Major, conf 4). SC-14.
- **Acceptance criteria**: Either the recommendation is withdrawn as unlicensed by a design the manuscript itself calls directionally symmetric, or it is retained together with an explicit statement of the decision the estimate cannot inform and the design that could — with the hedges replaced by that statement rather than added to.

**R14 — Report the institutional context.**
Source: R2 W4 (Major, conf 4). SC-15.
- **Acceptance criteria**: §3.1 names the LMS platform, states whether use was mandated or optional, and describes assessment integration and whether grades or announcements were available only through the platform, in sufficient detail for another site to be compared against this one.

**R15 — Supply the displays.**
Source: CONSENSUS-4 (EIC W4 Major conf 4; R1 W7, R2 W7, R3 W7 Minor); SPLIT 2 arbitrated as additive. SC-16, SC-17.
- **Acceptance criteria**: All five use-item categories are printed with their numeric codes and response frequencies; a participant-characteristics and descriptives table is provided; and the scatterplot cited in §3.4 as the assumption check is included so that the linearity, monotonicity, and outlier claims are independently checkable.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Items with no sub-claim provenance use `—`; none occur in this roadmap.

**Achievability, stated up front because the panel's asks are not the same size.** Every Required item is achievable within one revision cycle **without new data collection**, on two conditions: that R5 is answered by the Research Note route rather than the add-substance route, and that R10 is answered by the minimum repair (correct the mechanism) rather than the strong repair (institutional use distribution). The methodology seat's items require new computation and disclosure from information already in hand. The domain seat's items require substantial rewriting. The cross-disciplinary seat's items require justification the authors already possess the information to write — that seat states explicitly that it is *not* asking for the log-linked study. No item on this list is a request to re-run data collection.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Resolve the reference base; every DOI must resolve to a retrievable record, and every claim resting on a replaced source must be re-verified | SC-1 | Critical | text: §References — "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006" | 5 — EIC's standing reference-integrity screen; the prefix pattern is unambiguous | EIC (+R2 conf 3, R3 corroborates pattern) | P1 | 0.5 day if clerical; 4–6 days if the base must be rebuilt |
| R2 | Cite the canonical construct and framework sources; name the interpretive frame at first use | SC-2 | Major | absence: §2 Literature Review — expected canonical technology-acceptance and meta-analytic sources; checked §1, §2, §5, §7 and the reference list | 5 — desk-screen judgement of literature adequacy against construct volume | EIC, R2 (+R3 conf 3) | P1 | 2–3 days |
| R3 | Supply a quantified prior distribution and state what value would have been inconsistent | SC-3 | Major | text: §5 Discussion — "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)" | 5 — a decade on the TAM→UTAUT lineage and its meta-analytic evidence | R2, EIC (+DA M6) | P1 | 2–3 days |
| R4 | State which quantity is compared to which, and justify isolating one path from the framework | SC-4 | Major | text: §2 Literature Review — "an incremental data point, comparable with prior work, rather than as a test of a theoretical model" | 4 — based on how estimates are conventionally reported and pooled | R2 | P1 | 0.5 day |
| R5 | Reframe as a Research Note (or add substance) so the packaging matches the content | SC-5, SC-23 | Major | text: §7 Conclusion — "offered as an incremental, design-bounded contribution rather than a causal claim" | 5 — core desk-screening competence of the venue-fit seat | EIC | P1 | 3–4 days (Note route) |
| R6 | Hold "self-reported use" throughout; remove "engagement" from Abstract, Introduction, Discussion | SC-6 | Major | text: Abstract — "perceived usefulness tracks with LMS engagement among undergraduates" | 5 (R3) / 4 (R2) — direct textual comparison against the authors' own §2 and §3.2 commitment | R3, R2 (+DA M3) | P1 | 0.5 day |
| R7 | Report a polyserial correlation; present .42 as a floor; withdraw the magnitude label and the parametric-assumption claim | SC-7, SC-8 | Major | text: §4 Results — "indicating that the association did not depend on the parametric assumption" | 5 — published work on correlation attenuation under categorical measurement | R1 (SPLIT 1 vs R3 S5, arbitrated for R1) | P1 | 1 day |
| R8 | Add the common-method-variance discussion and state the two-sided bias bracket | SC-9 | Major | absence: §5 and §6 — expected acknowledgement that both variables were self-reported in one instrument at one sitting; checked §3.2, §3.4, §5, §6, §7 | 5 — standard survey-methods threat, verified absent across all interpretive sections | R1, R3 (+DA M2 conf 5) | P1 | 0.5 day |
| R9 | State the eligible-enrolment denominator and compute the response rate | SC-10 | Major | absence: §3.1 — expected the eligible undergraduate enrolment denominator and a computed response rate; checked §3.1, §3.4, §4, §6, Abstract | 5 — routine survey-reporting standard, verified by reading every section | R1 (+DA M1) | P1 | <0.5 day |
| R10 | Restate the recruitment-channel consequence as selection on the dependent variable, with direction indeterminate | SC-11 | Major | text: §3.1 and §6 — "distributed through the institution's course-announcement channel" / "students who engage more with institutional channels may be overrepresented" | 4 — sampling-frame/outcome coupling is standard in log-linked survey work; direction not determinable from the reported data | R3 (+DA M1) | P1 | 0.5 day (minimum repair) |
| R11 | Document the adaptation, supply the six items in an appendix, and either report dimensionality evidence or soften the validity claim | SC-12 | Major | text: §3.2 — "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency" | 5 — direct specialization in self-report instrument adaptation and validity evidence | R1 (Major), R2 (Minor) | P1 | 1–2 days |
| R12 | Give the design rationale for self-report over available logs in Methods, not as a Limitations apology | SC-13 | Major | text: §6 Limitations — "LMS use was self-reported through a single item rather than measured through system logs" | 5 — operates LMS event-log infrastructure and consent-linkage governance | R3 (+R1 corroborates) | P1 | 0.5 day |
| R13 | Resolve the onboarding implication: withdraw it, or name the design that would license it | SC-14 | Major | text: §5 Discussion — "may be worth institutional attention" / "suggested by, not proven by, the present correlation" | 4 (R3) / 5 (EIC) — practitioner-actionability judgement plus the reader-interest test | R3, EIC (+DA M4) | P1 | 0.5 day |
| R14 | Report the LMS platform, mandated-versus-optional status, and assessment integration | SC-15 | Major | absence: §3.1 — expected named LMS platform, mandated-versus-optional use status, and assessment integration; checked §3.1, §3.2, §4, §5, §6 | 4 — comparative reading of single-site LMS studies where these moderators drive between-site variation | R2 | P1 | 0.5 day |
| R15 | Supply the five-category frequency distribution with labels, a descriptives table, and the scatterplot | SC-16, SC-17 | Major (EIC) / Minor (R1, R2, R3) | absence: §4 Results and §3.4 Analysis — expected a descriptive table, participant-characteristics breakdown, and the scatterplot cited as an assumption check; checked §3.1, §3.4, §4 and all captions | 4–5 across four seats — absence directly verifiable | EIC, R1, R2, R3 (CONSENSUS-4 on the distribution; SPLIT 2 on the scatterplot, arbitrated as additive) | P1 | 1 day |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | State whether a target *n* was set before collection; otherwise label the calculation a sensitivity analysis, and address the DA's boundary observation | SC-18 | Minor | text: §3.4 — "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05" | 4 — arithmetic verified; the a-priori/post-hoc question is unresolvable from the text | R1, EIC (+DA referral) | P2 | <0.5 day |
| S2 | Name the deduplication mechanism and reconcile it with the anonymity assurance; characterise how the 14 incomplete cases differed | SC-19 | Minor (R1) / Major (DA M5) | text: §3.3 — "No identifying information was collected, and responses could not be linked back to individual students" | 4 — the tension is plainly visible; benign explanations exist but none is stated | R1 (+DA M5, which bands it higher) | P2 | 0.5 day |
| S3 | Add a data, instrument, and analysis-code availability statement, and name the software with version | SC-20 | Minor | absence: §3.4 and end matter — expected a data, instrument, or analysis-code availability statement and named software with version; checked §3.2, §3.3, §3.4, §7 and the reference list | 5 — checked every section and the reference list | R1 | P2 | 0.5 day |
| S4 | State whether consented survey-to-log linkage was considered and on what grounds it was rejected | SC-21 | Minor | absence: §3.3 — expected a statement of whether consented survey-to-log linkage was considered and why rejected; checked §3.1, §3.3, §3.4, §6, §7 | 5 — consent-and-linkage governance is that seat's direct operational responsibility | R3 | P2 | <0.5 day |
| S5 | Report *r*² numerically instead of "accordingly modest"; carry the confidence interval into the Abstract | SC-22 | Minor | text: §4 Results — "The proportion of variance shared by the two measures was accordingly modest" | 5 — directly observable on the page | EIC (+DA untabled) | P2 | <0.5 day |
| S6 | Fold Limitations into the Discussion and remove the Conclusion's restatement of the Abstract | SC-23 | Minor | text: §4 Results — "The 214 respondents reported a mean perceived-usefulness score of 3.6 (SD = 0.8) on the five-point scale." | 4 — section-to-content proportionality is a presentational judgement, not a bright line | EIC | P3 | 0.5 day — subsumed by R5 if the Research Note route is taken |

> Transported metadata appears on every row: severity is copied from the seat's per-finding **Severity** tag, evidence anchors are copied verbatim from the cards' typed anchors, and confidence is the per-finding value with its stated basis. No severity was re-derived and no fallback tag was required — every card in this panel carried per-finding severity and confidence. Where two seats banded the same sub-claim differently (R11 Major/Minor, R15 Major/Minor, S2 Minor/Major), both bands are shown and the owning seat's band governs the priority.

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated 14–18 days on the Research Note route; add 4–6 days if the reference base must be rebuilt)
- [ ] R1: Resolve every DOI; re-verify each claim that rested on a replaced source
- [ ] R2: Cite the canonical construct and framework sources; name the frame at first use
- [ ] R3: Supply the quantified prior distribution and the falsification condition
- [ ] R4: State the commensurability of the compared quantities; justify the single-path design
- [ ] R5: Reframe as a Research Note (or add substance)
- [ ] R6: Remove "engagement" as the outcome's name throughout
- [ ] R7: Compute and report the polyserial correlation; withdraw the magnitude label
- [ ] R8: Add the common-method-variance discussion and the bias bracket
- [ ] R9: Report the enrolment denominator and response rate
- [ ] R10: Restate the recruitment mechanism as selection on the outcome
- [ ] R11: Document the adaptation; append the six items; resolve the validity claim
- [ ] R12: Move the self-report justification into Methods as a design rationale
- [ ] R13: Withdraw or re-license the onboarding implication
- [ ] R14: Report the institutional context descriptors
- [ ] R15: Add the frequency distribution, descriptives table, and scatterplot

#### Priority 2 — Content Supplementation (estimated 2 days)
- [ ] S1: Clarify a-priori versus post-hoc sensitivity
- [ ] S2: Reconcile deduplication with the anonymity assurance
- [ ] S3: Add availability statements and software version
- [ ] S4: State whether consented linkage was considered
- [ ] S5: Report *r*² and carry the CI into the Abstract

#### Priority 3 — Text and Structure (estimated 0.5 day)
- [ ] S6: Fold Limitations into the Discussion; remove the redundant Conclusion
- [ ] EDITORIAL channel: no separate Minor-Issues lists were supplied in these sprint-contract cards, so this channel is otherwise empty. This is a card-format observation, not an inference that no such issues exist.

### Revision Deadline

Recommended 6–8 weeks (Major Revision). R1 should be answered within the first week regardless, since every other item is conditional on it.

### Response Letter Template

Use `templates/revision_response_template.md` and respond to every numbered item — R1–R15 and S1–S6 — individually. Items R1–R15 are not eligible for a "respectfully decline" response; SC-16 in particular carries unanimous panel support. For the two arbitrated splits (R7, R15), respond to the editor's resolution rather than to the individual reviewer positions.

---

## Part 2b: Roadmap — Machine Form (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "major_revision",
  "items": [
    {"id": "R1", "priority": "must_fix", "verification_criteria": "Every reference resolves to a retrievable record under a registered publisher prefix, or is replaced by a resolvable source; the cover letter states whether the 10.5555 DOIs were anonymisation placeholders; every claim that rested on a replaced source is re-verified.", "reviewer": "eic", "severity": "critical", "evidence_anchor": "text: §References — https://doi.org/10.5555/2050001, https://doi.org/10.5555/2050006", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-1"], "consensus": "CONSENSUS-3"},
    {"id": "R2", "priority": "must_fix", "verification_criteria": "Canonical construct source and at least one subsequent framework source cited; interpretive frame named at first use with its originating work; in-play constructs identified.", "reviewer": "eic", "severity": "major", "evidence_anchor": "absence: §2 Literature Review — expected canonical technology-acceptance and meta-analytic sources; checked §1, §2, §5, §7 and reference list", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-2"], "consensus": "CONSENSUS-3"},
    {"id": "R3", "priority": "must_fix", "verification_criteria": "At least one pooled or synthesised estimate reported with its range; r = .42 located against it; the value that would have been inconsistent is stated.", "reviewer": "domain", "severity": "major", "evidence_anchor": "text: §5 Discussion — consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-3"], "consensus": "corroborated"},
    {"id": "R4", "priority": "must_fix", "verification_criteria": "The benchmark estimand is identified (zero-order r vs standardised path coefficient vs PU-to-intention); like-with-like comparison confirmed; a paragraph states what is gained and given up by isolating one path.", "reviewer": "domain", "severity": "major", "evidence_anchor": "text: §2 Literature Review — an incremental data point, comparable with prior work, rather than as a test of a theoretical model", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-4"], "consensus": "single_reviewer"},
    {"id": "R5", "priority": "must_fix", "verification_criteria": "Either resubmitted as a Research Note with Limitations folded into the Discussion, the separate Conclusion removed, and a positioning paragraph plus comparison table present; or additional substance added such that the full-article structure is carried by the content.", "reviewer": "eic", "severity": "major", "evidence_anchor": "text: §7 Conclusion — offered as an incremental, design-bounded contribution rather than a causal claim", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-5", "SC-23"], "consensus": "single_reviewer"},
    {"id": "R6", "priority": "must_fix", "verification_criteria": "'Engagement' no longer denotes the measured outcome in Abstract, Introduction, Discussion, or Conclusion; terminal Abstract claim restated as self-reported access frequency; Introduction opening no longer primes a behavioural reading.", "reviewer": "perspective", "severity": "major", "evidence_anchor": "text: Abstract — perceived usefulness tracks with LMS engagement among undergraduates", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-6"], "consensus": "corroborated"},
    {"id": "R7", "priority": "must_fix", "verification_criteria": "Polyserial correlation reported alongside r; the parametric-assumption claim removed or restated to what Spearman's rho establishes; .42 presented as a lower bound conditional on measurement with the small/moderate/strong label dropped and the unquantifiable single-item component named.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "text: §4 Results — indicating that the association did not depend on the parametric assumption", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-7", "SC-8"], "consensus": "SPLIT_arbitrated"},
    {"id": "R8", "priority": "must_fix", "verification_criteria": "Manuscript states both variables were self-reported in one instrument at one sitting with adjacent items; names shared-method variance as a rival account distinct from the self-report/log fidelity point; states the magnitude is bracketed between biases of opposing sign.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "absence: §5 and §6 — expected acknowledgement that both variables were self-reported in one instrument at one sitting; checked §3.2, §3.4, §5, §6, §7", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-9"], "consensus": "corroborated"},
    {"id": "R9", "priority": "must_fix", "verification_criteria": "Eligible undergraduate enrolment reported; response rate computed from it; voluntary-response limitation restated in terms bounded by that figure.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "absence: §3.1 — expected the eligible undergraduate enrolment denominator and a computed response rate; checked §3.1, §3.4, §4, §6, Abstract", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-10"], "consensus": "single_reviewer"},
    {"id": "R10", "priority": "must_fix", "verification_criteria": "Manuscript states whether the course-announcement channel is an LMS function and, if so, identifies the consequence as selection on the dependent variable capable of biasing the coefficient, with direction stated as indeterminate; institutional aggregate use distribution credited if supplied.", "reviewer": "perspective", "severity": "major", "evidence_anchor": "text: §3.1 and §6 — distributed through the institution's course-announcement channel / students who engage more with institutional channels may be overrepresented", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-11"], "consensus": "single_reviewer"},
    {"id": "R11", "priority": "must_fix", "verification_criteria": "Six items reproduced in an appendix; adaptation changes stated item by item; source instrument's reliability figure given; dimensionality evidence reported or the 'previously validated' claim softened to internal consistency in the present sample.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "text: §3.2 — adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-12"], "consensus": "corroborated"},
    {"id": "R12", "priority": "must_fix", "verification_criteria": "Two to three sentences in §3.1 or §3.2 state whether log-based measurement was considered, what stood in the way, and why the self-report proxy was adequate; the Limitations sentence no longer phrases a design choice as an imposed constraint. Does not require the log study.", "reviewer": "perspective", "severity": "major", "evidence_anchor": "text: §6 Limitations — LMS use was self-reported through a single item rather than measured through system logs", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-13"], "consensus": "corroborated"},
    {"id": "R13", "priority": "must_fix", "verification_criteria": "Recommendation either withdrawn as unlicensed by a directionally symmetric design, or retained with an explicit statement of the decision the estimate cannot inform and the design that could, with hedges replaced by that statement rather than added to.", "reviewer": "perspective", "severity": "major", "evidence_anchor": "text: §5 Discussion — may be worth institutional attention / suggested by, not proven by, the present correlation", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-14"], "consensus": "corroborated"},
    {"id": "R14", "priority": "must_fix", "verification_criteria": "§3.1 names the LMS platform, states whether use was mandated or optional, and describes assessment integration and exclusive-channel status in detail sufficient for cross-site comparison.", "reviewer": "domain", "severity": "major", "evidence_anchor": "absence: §3.1 — expected named LMS platform, mandated-versus-optional use status, and assessment integration; checked §3.1, §3.2, §4, §5, §6", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-15"], "consensus": "single_reviewer"},
    {"id": "R15", "priority": "must_fix", "verification_criteria": "All five use-item categories printed with numeric codes and response frequencies; participant-characteristics and descriptives table provided; the §3.4 scatterplot included so linearity, monotonicity, and outlier claims are independently checkable.", "reviewer": "eic", "severity": "major", "evidence_anchor": "absence: §4 Results and §3.4 Analysis — expected a descriptive table, a participant-characteristics breakdown, and the scatterplot cited as an assumption check; checked §3.1, §3.4, §4, and all captions", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-16", "SC-17"], "consensus": "CONSENSUS-4"},
    {"id": "S1", "priority": "should_fix", "verification_criteria": "Manuscript states whether a target n was set before collection, or labels the calculation a sensitivity analysis, and addresses the boundary observation on .80 power at r >= .19.", "reviewer": "methodology", "severity": "minor", "evidence_anchor": "text: §3.4 — the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-18"], "consensus": "corroborated"},
    {"id": "S2", "priority": "should_fix", "verification_criteria": "Deduplication mechanism named and reconciled with the anonymity assurance; the 14 incomplete cases characterised relative to retained cases.", "reviewer": "methodology", "severity": "minor", "evidence_anchor": "text: §3.3 — No identifying information was collected, and responses could not be linked back to individual students", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-19"], "consensus": "single_reviewer"},
    {"id": "S3", "priority": "should_fix", "verification_criteria": "Data, instrument, and analysis-code availability statement present; analysis software and version named.", "reviewer": "methodology", "severity": "minor", "evidence_anchor": "absence: §3.4 and end matter — expected a data, instrument, or analysis-code availability statement and named software with version; checked §3.2, §3.3, §3.4, §7 and the reference list", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-20"], "consensus": "single_reviewer"},
    {"id": "S4", "priority": "should_fix", "verification_criteria": "Manuscript states whether consented survey-to-log linkage was considered and on what grounds it was rejected.", "reviewer": "perspective", "severity": "minor", "evidence_anchor": "absence: §3.3 — expected a statement of whether consented survey-to-log linkage was considered and why it was rejected; checked §3.1, §3.3, §3.4, §6, §7", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-21"], "consensus": "single_reviewer"},
    {"id": "S5", "priority": "should_fix", "verification_criteria": "r-squared reported numerically in Results; the 95% confidence interval carried into the Abstract.", "reviewer": "eic", "severity": "minor", "evidence_anchor": "text: §4 Results — The proportion of variance shared by the two measures was accordingly modest", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-22"], "consensus": "single_reviewer"},
    {"id": "S6", "priority": "nice_to_fix", "verification_criteria": "Limitations folded into the Discussion and the Conclusion's restatement of the Abstract removed; subsumed if R5 is answered by the Research Note route.", "reviewer": "eic", "severity": "minor", "evidence_anchor": "text: §4 Results — The 214 respondents reported a mean perceived-usefulness score of 3.6 (SD = 0.8) on the five-point scale.", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-23"], "consensus": "single_reviewer"}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

These cards were produced under a sprint contract, which specifies per-dimension scores rather than a report-level recommendation and confidence score. Those two fields are therefore **not provided** in any of the five cards; they are recorded as absent rather than inferred from the dimension verdicts.

### Journal-Fit Reviewer (eic)
- Recommendation: `[not provided — sprint-contract card format]` | Confidence: `[not provided; per-finding confidence 4–5]`
- Dimensions scored: D5 `warn`, D6 `block` (repairable). Fatality explicitly considered and withheld.
- Key point: The reference base does not resolve, the comparison distribution is never quantified, and the paper declines to name a takeaway — a small, honest, well-positioned note would pass, and this is small and honest but not positioned.

### Reviewer 1 — Methodology (methodology)
- Recommendation: `[not provided]` | Confidence: `[not provided; per-finding confidence 4–5]`
- Dimensions scored: D1 `block` (repairable), D3 `warn`.
- Key point: The one number the paper exists to report has no defensible interpretation of magnitude as submitted, because it sits between attenuation from coarse single-item measurement and inflation from shared method, neither of which the manuscript addresses. Explicitly does not ask for a larger model.

### Reviewer 2 — Domain (domain)
- Recommendation: `[not provided]` | Confidence: `[not provided; per-finding confidence 3–5]`
- Dimensions scored: D2 `warn`, declared conditional on the good-faith reading of the reference list.
- Key point: Nothing the paper says is false and the statistics reconcile, but the one claim it makes about the field is stated in a form that cannot be checked, and the construct arrives without its provenance. Explicitly declines to score the study down for being small or single-site.

### Reviewer 3 — Cross-disciplinary (perspective)
- Recommendation: `[not provided]` | Confidence: `[not provided; per-finding confidence 3–5]`
- Dimensions scored: D4 `warn`. Assigned no Critical, with the singleton test stated.
- Key point: The home-field bookkeeping is careful while the outward-facing surfaces are not, and the paper's central measurement choice is narrated as an imposed constraint when nothing establishes that it was one. Explicitly not asking for the log-linked study.

### Devil's Advocate (da)
- Recommendation: `[not provided]` | Confidence: `[not provided; per-finding confidence 4–5]`
- Dimensions scored: D3 `warn`. CRITICAL table empty (0 items); six MAJOR items, all carried into the roadmap.
- Key point: The paper's modesty is applied almost exclusively to the direction of the association, while the identity of the outcome construct, the composition of the sample, and the comparative claim that supplies the entire stated contribution travel unpoliced.

### Card-Quality Flags (raised, not repaired)

Per the phase boundary these are reported for the orchestrator, not fixed here:

1. **Domain card** opens with a self-corrected placeholder artefact (`## Scoring Plan Dissent` followed by "Wait — that line would constitute a placeholder. Removing it.") that was left in the emitted card. The `contract_role: domain` line and all dimension scores parse correctly; no score was affected.
2. **Perspective card** carries the same class of artefact ("Wait — per protocol I omit that section entirely. Disregard the heading above"). Same assessment: parseable, scores unaffected.
3. Neither artefact reduced the weight of any sub-claim from those cards, per the surface-form parity check above.
4. No reviewer was dropped and no substitute score was synthesised; `panel_size` = 5 held throughout, so no `[PANEL-SHRUNK]` condition arose.

---

**Handoff.** Revision-side work is out of scope for this phase. The revised draft is a separate `academic-paper` Phase 6 re-invocation of `draft_writer_agent`; the revised manuscript is Phase 7 `formatter_agent`. Control returns to the caller, with one item flagged for editorial action ahead of any revision cycle: the reference-base integrity check recorded at R1.
