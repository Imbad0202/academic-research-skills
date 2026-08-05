# Editorial Decision Package

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size` 5 (5 usable cards received; no `[PANEL-SHRUNK]`)

---

## Sprint Contract Audit (Steps 1–3)

### Step 1 — Role-scoped scoring matrix

Only assessed scores from seats listed in each dimension's `eligible_roles` are counted. Ineligible `not_assessed` values are excluded from both numerator and denominator.

| Dim | Priority | Eligible roles | Assessed eligible seats | Scores | Dimension verdict |
|-----|----------|----------------|-------------------------|--------|-------------------|
| D1 methodology_rigor | mandatory | methodology | methodology | block (`repairable`) | **block** |
| D2 domain_accuracy | mandatory | domain | domain | block (`fatal`) | **block(fatal)** |
| D3 argumentative_coherence | mandatory | da, methodology | da, methodology | warn, warn | **warn** |
| D4 cross_disciplinary_relevance | high | perspective | perspective | warn | **warn** |
| D5 writing_and_structure | normal | eic | eic | warn | **warn** |
| D6 venue_fit_and_contribution | mandatory | eic | eic | block (`repairable`) | **block** |

Every dimension has ≥1 assessed eligible seat; no `[DIMENSION-UNASSESSED]`. Fatal scope on D2 is valid (D2 is mandatory).

**Audit verdict:** `block(fatal)` — worst assessed eligible score is `block`, and one assessed eligible seat (domain, D2) declared a fatal block.

### Step 2 — Failure-condition evaluation

| ID | Sev | Cross-reviewer quantifier | Expression (parsed pattern) | Per-dimension evaluation | Fired |
|----|-----|---------------------------|------------------------------|--------------------------|-------|
| F1 | 95 | any | `any <priority> dimension has a fatal block` (mandatory = D1, D2, D3, D6) | D1 false (repairable), **D2 true**, D3 false, D6 false (repairable) → `any` = true | **true** |
| F2 | 90 | any | `any <priority> dimension scores '<score>'` (block) | **D1 true, D2 true, D6 true**, D3 false → `any` = true | **true** |
| F3 | 70 | majority | `two or more dimensions with priority=<mandatory> score 'warn' or worse` | D1 true (n=1, owner=methodology), D2 true (n=1, owner=domain), D3 true (n=2, both seats warn), D6 true (n=1, owner=eic) → 4 ≥ 2 | **true** |
| F4 | 60 | any | `any <priority>-priority dimension scores 'block'` (high = D4) | D4 = warn, no eligible seat at block → false | false |
| F5 | 40 | any | `any dimension scores '<score>' or worse` (warn) | D1 true → `any` = true | **true** |
| F0 | 10 | all | `every dimension scores 'pass'` | false at D1 | false |

### Step 3 — Precedence and emission

Fired: F1 (95), F2 (90), F3 (70), F5 (40). Highest severity = **F1** → `action: editorial_decision=reject`.

```
dimension_verdicts: [D1=block, D2=block(fatal), D3=warn, D4=warn, D5=warn, D6=block]
fired_conditions: [F1, F2, F3, F5]
da_critical_adjudications: []
editorial_decision=reject
```

`da_critical_adjudications` is `[]` because the Devil's Advocate card's CRITICAL table contains headers only, with an explicit stated rationale for the empty band (singleton test applied; no finding unseats the core claim alone). No phantom IDs minted. No `[DA-CRITICAL-VS-ACCEPT]` marker applies — the mechanical decision is not `accept`.

### Panel input anomalies (flagged, not repaired)

Per the phase boundary I flag incomplete reviewer input rather than augmenting it.

1. **`measurement_procedure` artifacts not forwarded.** The contract requires `contract_paraphrase` and `scoring_plan` output before the paper, with `paraphrase_minimum_dimensions: all`. Neither artifact is present in the five cards **as supplied to synthesis**. Four cards quote their pre-committed triggers verbatim and one refers to "the threshold I committed to before reading," which indicates the plans existed upstream and were not forwarded. I record this as a forwarding gap in the synthesis input, not as reviewer non-compliance, and I did not reconstruct them.
2. **Perspective card format anomaly.** The card opens with a malformed `## Scoring Plan Dissent` heading marked *(none — omitted)* followed by a self-correcting meta-sentence inside the card body. No substantive dissent was recorded. This does not alter eligibility, scoring, or fatality, and no fatality was minted during scoring-plan dissent.
3. **Venue configuration missing for the seat that owns venue fit.** The EIC seat declares that no target-venue statement was supplied in the manuscript and no venue configuration string in the contract, and states it reasoned about venue *class* rather than a named title, declining to invent a recommendation list. **The D6 block therefore rests on a venue-class judgement, not a named-venue judgement.** This is material to routing and is recorded on the face of the decision.
4. **Cross-dimension routing, confirmed non-double-counted.** The EIC recorded the reference-verifiability finding under D5 while stating explicitly that it is not the basis of the D5 warn. The D5 warn rests on missing display material, the qualitative r², missing denominators, and missing declarations. No double count into D5.
5. **No report-level recommendation or confidence score** is present in any card; both are absent from the panel input (see Part 3).
6. `ARS_CROSS_MODEL` is not set and no consent gate was passed. Step 4b was not run; no behavioural change.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript, "Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students." It was assessed by five reviewers, including a Journal-Fit Reviewer and a Devil's Advocate.

### Decision: Reject

The decision follows mechanically from the contract's failure conditions: `F1` fired at severity 95 on a fatal block in a mandatory dimension (D2, domain accuracy). Three further conditions also fired — `F2` (90), `F3` (70), `F5` (40) — so the manuscript cannot reach acceptance on any reading of the panel's scores.

### Review Panel Provenance (#540)

No provenance stamp was supplied to this synthesis by the dispatching layer. I therefore cannot state which of the three permitted statements applies (cross-model slot active / single-family disclosure / dispatch-failure fallback), and I will not infer one. **`[PROVENANCE-STAMP-MISSING]` — readers should assume no model independence across the five seats until the dispatching layer supplies the stamp.** I computed no cross-family aggregate and no same-model majority; cross-seat agreement in this letter is agreement between reviewer *cards*, and carries no claim about the models that produced them.

### Consensus Analysis

Consensus is computed per sub-claim over the **four non-DA seats** (Journal-Fit / R1 methodology / R2 domain / R3 perspective), denominator fixed at 4. Silence is neither agreement nor opposition. The DA is tracked separately.

#### Points of Agreement

- **[CONSENSUS-4] The perceived-usefulness instrument is undocumented.** All four seats record that the six items are nowhere reproduced, that the adaptation from the source instrument is undescribed, and that Cronbach's α is the sole psychometric warrant. (SC-2)
- **[CONSENSUS-4] Shared variance is stated qualitatively where a number exists.** All four seats note that "modest" stands in for r² ≈ .18. (SC-15)
- **[CONSENSUS-3] The sampling frame and response rate are absent.** Journal-Fit, R1, and R3 all record that no eligible-population denominator is given, so no response rate exists and the self-selection the paper concedes in §6 cannot be sized. **Silent seat: R2 (domain).** (SC-3)
- **Corroborated (2/4, no conflict): the reference base is unverifiable.** Journal-Fit and R2 independently report that all six DOIs sit on the `10.5555` reserved documentation prefix with unbroken sequential suffixes `2050001`–`2050006`, that six differently-named journals across at least four notional publishers cannot share one registrant prefix, and that five of six titles are one or two words from real venues. (SC-1)
- **Corroborated (2/4): §3.3 anonymity and §3.1 duplicate removal cannot both be literally true.** R1 and R3 each state that deduplication requires a retained identifier or fingerprint, which makes the instrument pseudonymous rather than anonymous. R3 adds that this is a different ethics-approval category on most committees. (SC-5)
- **Corroborated (2/4): common-method variance is never named** as a rival generator of r = .42, despite both variables being self-reports from one respondent in one instrument on one occasion. (SC-6)
- **Corroborated (2/4): recruitment ran through the system being measured**, which is selection on the outcome variable, not the generic voluntary-response caveat §6 offers. (SC-4)

#### Points of Disagreement

- **"LMS engagement" in the abstract's closing sentence (SC-9).** R3 (Major, conf 5), R2 (Major, conf 4) and R1 (Minor, conf 4) all read this as a construct escalation — "engagement" denotes behavioural, emotional and cognitive dimensions, while the measure is one item on weekly access frequency — compounded by the loss of the single-institution bound. The Journal-Fit Reviewer's S2 quotes that same sentence and certifies the abstract as passing concordance screening "without qualification." Under the disposition precedence this is a `[SPLIT]`, not a CONSENSUS-3.

  **Editor's Resolution: the finding is upheld; the Journal-Fit Reviewer's assessment is not overturned.** The SPLIT rule assigns arbitration to the Journal-Fit Reviewer, who is here the disputing party, so I arbitrate directly. On evidence: §2 commits in the paper's own voice to treating the measure as "perceived use rather than a behavioral count," and the abstract's closing sentence contradicts that commitment — a textual, checkable defect. On expertise: R3 owns institutional engagement-metric definitions, R2 owns field construct usage. Reading each side's actual claim precisely, the two positions address different axes: the Journal-Fit Reviewer is right that no *causal or strength* inflation occurs anywhere in the manuscript, and the other three are right that a *construct-term* substitution and a lost population bound occur in the same sentence. Both findings stand; neither is averaged away.

- **Two disagreements the field analysis predicted did not materialise, and I record that explicitly rather than manufacture them.** (a) The anticipated R1/R3 collision over whether self-report is a psychometric defect or a legitimate construct choice is absent: no seat challenges self-report of the *independent* variable, and all three peer seats converge on the *dependent* variable needing behavioural anchoring or an explicit justification. (b) The anticipated scope-creep conflict is absent: R2 explicitly disclaims its own "ask for a bigger paper" instinct, R3 explicitly disclaims "you should have run a different study," and every R1 remedy is disclosure or re-estimation. **No seat requires new data collection.** The remedy set below is therefore deliverable as a revision, not a redesign — the one exception being the article-grade question, which requires either recategorisation (no new data) or a second site / log data (new data).

#### Devil's Advocate

The DA recorded **no CRITICAL findings** and gave its reasoning: applying the singleton test, each defect it found is repairable by rewriting, added argument or added reporting, and none alone unseats the paper's core claim of a bounded, correctly computed bivariate correlation. It states plainly that the standard adversarial openings failed — inflated effect, mismatched interval, smuggled causal verb, headline contradicting the table — and that its arithmetic recomputation reconciled. Its six MAJOR findings are carried into the roadmap and are not discarded: M1 → S3, M2 → S7, M3 → S10, M4 → S4, M5 → S8, M6 → R2.

### Decision Rationale

The decision is arithmetic under the contract, and the arithmetic has a single dominant driver: the domain seat's fatal block on D2, grounded in a reference list none of whose six entries can be located. The pattern is structural rather than typographical — one reserved documentation prefix shared across six nominally independent journals, suffixes running in unbroken reference-list order, five near-miss venue titles, and the one real title (Inderscience's *International Journal of Learning Technology*) deposited under a prefix that is not this one. Section 2 rests exclusively on those six items, and so does §3.2's measurement provenance and the paper's only stated contribution, comparability with prior work. Remove them and no domain-level assertion in the manuscript is checkable.

Two things must be said alongside that. First, **both seats that raised this finding conditioned it on a verification step neither could execute**: the Journal-Fit Reviewer reports confidence 4 and notes that confirmation requires a DOI resolution check unavailable in session; the domain seat states it would revise the fatal judgement "immediately and without complaint" against verifiable records. That contingency belongs to the editor and publisher to settle, and I record it as fact rather than as a modification of the decision — the fired condition's action is not softened. For the author's information only, and clearly labelled as counterfactual: were the references verified, the governing condition would become `F2` at severity 90, whose action is `major_revision`, because D1 and D6 are independently blocked. There is no reading of this panel's scores on which the manuscript is acceptable as submitted.

Second, this is not a weak paper being failed for weakness. Four seats independently credit the same thing: the correlational discipline is real and uniformly maintained, the reverse pathway is volunteered in the paper's own voice rather than buried, the Spearman check is reported rather than asserted, the sensitivity statement takes the defensible detectable-floor form, and the internal arithmetic reproduces — the Fisher-z interval on r = .42 at n = 214 is exactly the reported [.30, .52], and the case flow from 233 to 214 reconciles. The Devil's Advocate notes that most manuscripts of this shape fail at least one of those checks. What blocks the paper is the verifiability of its evidence base, the recoverability of its instrument, the absence of a sampling denominator, and an article-grade claim its content does not fund — not a defect of care.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire six-item reference base is unverifiable; reserved `10.5555` documentation prefix with sequential suffixes; §2, §3.2, §5 and the contribution claim rest exclusively on it (D2 fatal block) | R2 (domain), EIC | `text: § References — "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006"` | R1 |
| 2 | Perceived-usefulness instrument is unrecoverable — items not reproduced, adaptation from source undocumented, no in-sample validity evidence; comparability (the paper's stated contribution) is therefore uninterpretable (D1 block driver) | R1 (methodology), EIC, R2, R3 | `absence: §3.2 Measures and manuscript back matter — expected verbatim wording of the six items, an explicit statement of what was changed from Costa and Wren (2019), and factor-structure evidence in the present sample` | R2 |
| 3 | Contribution below the full-article threshold: one bivariate coefficient on the most replicated association in the literature, from one site, with a single-item outcome (D6 block) | EIC | `text: §7 Conclusion — "offered as an incremental, design-bounded contribution rather than a causal claim"` | R6 |

The D1 block has a **second co-driver** not listed above: the absent eligible-population denominator, which makes the analytic sample unreconcilable against those invited. It is resolved by **R4**.

---

## Part 2: Revision Roadmap

> No revision deadline applies: the decision is Reject. This roadmap is issued as a pre-resubmission checklist for this manuscript at any venue. **R1 should be settled before any resubmission is prepared**, because its outcome determines whether the remaining work is a revision or a reconstruction.
>
> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Severity, Evidence Anchor and Confidence are transported from the reviewer cards, never re-derived; where seats recorded different severities for the same sub-claim the spread is shown with seat attribution rather than collapsed. No card required a `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` tag — all five cards carry per-finding severity and confidence.
>
> **Priority rule applied here** (derived from the priority definitions, stated so it is auditable): **P1** = required to lift a fired block, or to correct a factual/ethical inaccuracy; **P2** = required for interpretability but not block-driving; **P3** = presentation and compliance. Where this rule assigns a priority that diverges from the consensus-label mapping, the divergence is named in the item detail. No card supplied a below-threshold "Minor Issues" channel, so no roadmap item is `source_kind: "editorial"`.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| R1 | Produce verifiable bibliographic records for all six references, or withdraw and rebuild the evidence base from checkable sources | SC-1 | Critical [R2] / Critical [EIC] | `text: § References — "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006"` | 5 [R2] / 4 [EIC — "confirmation requires a resolution check I cannot run here"] | R2, EIC | P1 | 1–2 days if verifiable records exist; 2–3 weeks if §2 and §3.2 must be rebuilt |
| R2 | Reproduce the six perceived-usefulness items verbatim, document every change from the source instrument, and supply in-sample structural evidence | SC-2 | Critical [R1] / Major [R2, R3] / Minor [EIC] | `absence: §3.2 Measures and manuscript back matter — expected verbatim wording of the six items, an explicit statement of what was changed from Costa and Wren (2019), and factor-structure evidence in the present sample` | 5 [R1] / 4 [R2] / 5 [R3] / 5 [EIC] | R1, R2, R3, EIC (+DA M6) | P1 | 2–4 days if a change log exists; longer if the adaptation was undocumented at the time |
| R3 | Disclose the deduplication mechanism and correct whichever of §3.1 / §3.3 is inaccurate | SC-5 | Major [R1] / Major [R3] | `text: §3.3 "No identifying information was collected, and responses could not be linked back to individual students."` | 4 [R1] / 5 [R3] | R1, R3 | P1 | 1 day (disclosure of an existing fact, plus an ethics-approval scope check) |
| R4 | Report the eligible undergraduate enrolment, the computed response rate, and the year-level distribution of the 214 analysed cases | SC-3 | Major [R1] / Major [R3] / Minor [EIC] | `absence: §3.1 Design and participants — expected the enrolled undergraduate population size, a computed response rate, and the year-level distribution of the 214 analyzed cases against institutional benchmarks` | 5 [R1] / 5 [R3] / 5 [EIC] | R1, R3, EIC | P1 | 1–2 days (figures the authors already hold) |
| R5 | Rebuild §2 around the actual research lineage, and stop attributing the 1989 perceived-usefulness definition to 2019–2020 sources | SC-11 | Major [R2] | `absence: §2 Literature Review — expected citation of the canonical perceived-usefulness source and of existing pooled LMS-acceptance estimates; checked §1, §2, §5, §7, and the reference list` | 5 [R2] | R2 | P1 | 1–2 weeks |
| R6 | Recategorise to Brief Report / Research Note and replace the conceded contribution paragraph with an argued gap statement — or retain the article grade by adding a second site or log-based measurement | SC-13, SC-10b | Major [EIC] / Minor [EIC, SC-10b] | `text: §7 Conclusion — "offered as an incremental, design-bounded contribution rather than a causal claim"` | 5 [EIC] / 4 [EIC, SC-10b] | EIC | P1 | 2–3 days for recategorisation and reframing; months if the article grade is retained |

### Required Item Details

**R1 — Verifiable reference base**
This is the fatal-block driver on D2 and, uncorrected, makes acceptance impossible at any venue. Consensus label: corroborated finding (2/4, 0 conflict). **Priority divergence, stated plainly:** the count label maps to P2, and I have assigned P1 on severity grounds — two seats at Critical severity, confidence 5 and 4, no dissent, and it is the sole driver of the only fatal block on the panel. Both seats made their finding contingent on a DOI resolution check neither could execute; that contingency is recorded on the decision but does not alter it.
- **Acceptance criteria**: Every one of the six references resolves to a retrievable record with a registered publisher DOI prefix, correct journal title, volume, issue and page range, or the reference is removed and every claim depending on it is re-sourced and re-verified.

**R2 — Instrument recoverability**
The only [CONSENSUS-4] item at P1. The paper's stated contribution is comparability with prior estimates; comparability requires knowing what was measured, and an undocumented adaptation with no in-sample structural evidence destroys it. α = .88 across six items implies a mean inter-item correlation near .55, equally consistent with a coherent unidimensional scale and with a set of near-paraphrases. R2 adds the domain-specific point that the abstract's "previously validated" overstates the available evidence, since validity is not transitive across adaptation, population or platform. DA M6 records the same premise as undefended.
- **Acceptance criteria**: An appendix reproduces all six item stems verbatim, an explicit change log states what differs from the source instrument and why, in-sample structural evidence (a confirmatory model or at minimum the item-level inter-correlation matrix) is reported, and the abstract's "previously validated" is restated to describe the adapted form.

**R3 — Ethics statement accuracy**
Not a methodological opinion but a factual inconsistency inside the ethics and consent section. Every mechanism supporting deduplication — session token, cookie, IP address, single-use link — is a quasi-identifier or a linkage mechanism; response-pattern matching would be a substantive analytic decision with a non-zero false-positive rate requiring its own disclosure. R3 adds that an instrument supporting duplicate detection is pseudonymous rather than anonymous, which sits in a different approval category on most committees and in several data-protection regimes. Neither seat alleges a governance breach; both state that the manuscript as written misdescribes what the approval covered.
- **Acceptance criteria**: The deduplication mechanism, any retained identifier and its retention period are disclosed, §3.3 describes the anonymity condition accurately, and the stated approval scope matches the mechanism actually used.

**R4 — Sampling denominator and composition**
The second D1 block co-driver. Without the enrolled population there is no response rate, and without a response rate the voluntary-response bias the paper honestly concedes in §6 names a mechanism it cannot bound. R1 notes that recruitment through the institution's course-announcement channel makes selection into the sample plausibly correlated with the outcome variable itself, so this is not an incidental worry. "Spanned all four year levels" is a presence claim, not a distribution.
- **Acceptance criteria**: Eligible enrolment, invitations delivered and computed response rate are reported; the year-level distribution of the 214 analysed cases is given against institutional benchmarks; and where available an early-versus-late responder comparison is reported as a nonresponse proxy.

**R5 — Literature lineage**
Single-reviewer finding (1/4), owner seat for D2, confidence 5, Major. **Priority divergence, stated plainly:** assigned P1 not on count but because its remedy is entailed by R1 — if the references cannot be verified §2 must be rebuilt regardless, and this item specifies what it must be rebuilt around. The §2 definition of perceived usefulness is substantively Davis's 1989 formulation sourced to 2019–2020 references; no UTAUT-generation work and no existing LMS-acceptance synthesis appears; no cited source predates 2018.
- **Acceptance criteria**: §2 cites the canonical origin of the perceived-usefulness construct with correct attribution and date, engages the UTAUT-generation and synthesis literature, and no founding construct definition is attributed to recent secondary commentary.

**R6 — Article category and contribution claim**
Single-reviewer finding (1/4) and the D6 block driver; the owner seat for D6 assigned it, R2 and R3 both declined to speak to the category question (R3 expressly deferring it as the editor's call), so there is no conflict. **The block is scored against a venue *class*, not a named venue**, because no venue configuration reached the seat that owns venue fit — see anomaly 3. The EIC's own position is that the small paper is a legitimate publication object it "would not want the field to lose"; what fails is the article grade, and no amount of rewriting increases the quantity of evidence. SC-10b is folded here: §2 supplies the premise that would justify the paper (single-site estimates matter because association strengths vary by institution) and then never converts it into a claim about what this campus adds.
- **Acceptance criteria**: The submission category is Brief Report or Research Note, and the contribution paragraph states positively what prior work leaves unestablished, what institutional profile is under-represented in the existing distribution of estimates, and what a reader can do with this coefficient — or, if the article grade is retained, a second site or log-based measurement is added.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| S1 | Make an ordinal-appropriate coefficient primary with an interval; retain Pearson and Spearman as sensitivity analyses with intervals; report t and df | SC-7 | Major [R1] | `text: §3.4 "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check."` | 5 [R1] | R1 | P2 | 2–3 days |
| S2 | State that no reliability estimate exists for the outcome and that the CI therefore understates total uncertainty; frame r as a lower bound; report all five category labels and the frequency distribution | SC-8, SC-23 | Major [R1] | `text: §3.2 "We treat this as an ordinal indicator of self-reported use and interpret it accordingly."` | 5 [R1] | R1 (+DA minor obs.) | P2 | 1–2 days |
| S3 | Name common-method variance as a rival explanation for the magnitude of r, and report any procedural remedies used | SC-6 | Major [R1] / Major [R2] | `absence: §5 Discussion — expected common-method or shared-self-report bias named as a rival explanation for the focal correlation; checked Abstract, §2, §3.2, §4, §5, §6` | 5 [R1] / 4 [R2] / 5 [DA M1] | R1, R2 (+DA M1) | P2 | 1 day |
| S4 | State whether the course-announcement channel is LMS-hosted and reclassify the resulting selection as a threat to the coefficient, not only to generalisability | SC-4 | Major [R3] / Major [R1] | `text: §3.1 "The survey was distributed through the institution's course-announcement channel"` | 5 [R3] / 5 [R1] / 4 [DA M4] | R3, R1 (+DA M4) | P2 | 1 day |
| S5 | Name the LMS and its version, and state whether it is the required channel for submission, quizzes and grade release during the survey window | SC-12 | Major [R2] | `absence: §3.1 and §3.2 — expected the platform identity and version plus the institution's mandatory-use policy for assignment submission and grade release; checked §1, §3, §4, §6` | 5 [R2] | R2 | P2 | 1 day |
| S6 | Add a fifth limitation naming unmeasured access and equity confounders, and acknowledge in §5 that part of the association may be structural rather than attitudinal | SC-18 | Major [R3] | `absence: §6 Limitations — expected a named limitation for unmeasured confounders of access frequency (assessment schedules, timetable structure, notification settings, device and broadband access, commuter status, paid-work hours)` | 5 [R3] | R3 | P2 | 1 day |
| S7 | Replace "engagement" with self-reported access frequency wherever frequency is what was measured, and restore the single-institution bound in the abstract's closing sentence | SC-9 | Major [R3] / Major [R2] / Minor [R1] | `text: Abstract "perceived usefulness tracks with LMS engagement among undergraduates"` | 5 [R3] / 4 [R2] / 4 [R1] / 5 [DA M2] | R3, R2, R1 (+DA M2); **arbitrated SPLIT — EIC disputed** | P2 | 1 day |
| S8 | Report a pooled prior estimate or range against which r = .42 is judged consistent, or drop the comparability claim | SC-10a | Major [R2] | `text: §2 and §5 — "effect sizes vary across samples and instruments", "consistent with prior technology-acceptance research"` | 5 [R2] / 5 [DA M5] | R2 (+DA M5) | P2 | 3–5 days (conditional on R1) |
| S9 | State in one sentence why institutional LMS access logs were not used — approval scope, governance route, or feasibility within the three-week window | SC-19 | Minor [R3] | `absence: §3.1 Design and the §6 second limitation — expected a stated reason why institutional LMS access logs were not used or not obtainable` | 4 [R3] | R3 | P2 | <1 day |
| S10 | Delete or reframe the onboarding implication, or supply the argument that makes its directional premise defensible | SC-17 | Minor [R3] / Major [DA M3] | `text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data" / "LMS onboarding which helps students see concrete usefulness"` | 5 [R3] / 4 [DA M3] | R3 (+DA M3) | P2 | 1 day |
| S11 | Add the scatterplot whose inspection §3.4 reports as an analytic step, plus a descriptives table | SC-14 | Major [EIC] / Minor [R1] | `absence: §4 Results and §3.4 Analysis — expected at least one table or figure, including the scatterplot whose inspection is reported; checked §3.4, §4, all section bodies, and the reference list for any table or figure caption` | 5 [EIC] / 5 [R1] | EIC, R1 | P2 | 1–2 days |
| S12 | Report r² = .18 numerically in §4 | SC-15 | Minor [EIC] / Minor [R2] / Minor [R3] / Major [R1, as part of incomplete reporting] | `text: §4 Results — "The proportion of variance shared by the two measures was accordingly modest"` | 4 [EIC] / 5 [R2] / 4 [R3] / 5 [R1] | EIC, R1, R2, R3 — **[CONSENSUS-4]** | P3 | <1 day |
| S13 | Add data-availability, funding and competing-interests declarations; name the statistical software and version; deposit the data or the cross-tabulation | SC-16 | Minor [EIC] / Minor [R1] | `absence: manuscript front and back matter — expected data-availability, funding, and competing-interests declarations required by mainstream educational-technology venues` | 5 [EIC] / 5 [R1] | EIC, R1 | P3 | 1 day |
| S14 | Relabel the §3.4 power statement as a post-hoc sensitivity analysis, state whether any a priori target N existed, and correct "greater than .80" to "approximately .80" at the stated boundary | SC-20 | Minor [R1] | `text: §3.4 "With n = 214, the study had greater than .80 power to detect a correlation of r >= .19"` | 5 [R1] | R1 | P3 | <1 day |
| S15 | Drop the attribution of residual variance to course requirements and assessment schedules, or label it explicitly as conjecture | SC-22 | Minor [R2] | `text: §4 — "consistent with the view that reported engagement reflects many influences beyond perceived usefulness, including course requirements and assessment schedules"` | 4 [R2] | R2 | P3 | <1 day |

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total effort: ~3–5 weeks if references verify; substantially longer if §2 must be rebuilt or the article grade is retained)
- [ ] R1: Produce verifiable bibliographic records for all six references, or rebuild the evidence base from checkable sources
- [ ] R2: Reproduce the six items verbatim, document the adaptation, supply in-sample structural evidence
- [ ] R3: Disclose the deduplication mechanism and correct the §3.1/§3.3 inconsistency
- [ ] R4: Report eligible enrolment, response rate, and year-level distribution
- [ ] R5: Rebuild §2 around the actual lineage and correct the construct-definition attribution
- [ ] R6: Recategorise to Brief Report and argue the contribution, or add a second site / log data

#### Priority 2 — Content Supplementation (estimated total effort: ~2 weeks)
- [ ] S1: Ordinal-appropriate primary estimate with interval; report t and df
- [ ] S2: State the unestimable outcome reliability; frame r as a lower bound; report category labels and distribution
- [ ] S3: Name common-method variance as a rival explanation
- [ ] S4: State whether recruitment ran through the LMS; reclassify the selection threat
- [ ] S5: Name the platform and its mandatory-use policy
- [ ] S6: Add the access and equity confounder limitation
- [ ] S7: Replace "engagement" with access frequency; restore the institutional bound in the abstract
- [ ] S8: Report a prior pooled estimate or drop the comparability claim
- [ ] S9: State why logs were not used
- [ ] S10: Delete, reframe, or argue the onboarding implication
- [ ] S11: Add the scatterplot and a descriptives table

#### Priority 3 — Text and Formatting (estimated total effort: ~2 days)
- [ ] S12: Report r² = .18 numerically
- [ ] S13: Add declarations, name the software, deposit data or cross-tabulation
- [ ] S14: Relabel the power statement and correct the boundary wording
- [ ] S15: Drop or mark as conjecture the residual-variance attribution

### Response Letter Template

Use `templates/revision_response_template.md` and respond to every R and S item individually. The [CONSENSUS-4] items (R2, S12) and the [CONSENSUS-3] item (R4) carry no "respectfully decline" option. R1 must be answered before the rest of the response is meaningful.

### Roadmap — Schema 7 machine form

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "reject",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": ["R2", "EIC"], "source_kind": "finding", "sub_claims": ["SC-1"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: § References — \"https://doi.org/10.5555/2050001\", \"https://doi.org/10.5555/2050006\"", "verification_criteria": "Every one of the six references resolves to a retrievable record with a registered publisher DOI prefix, correct journal title, volume, issue and page range, or the reference is removed and every claim depending on it is re-sourced and re-verified."},
    {"id": "R2", "priority": "must_fix", "reviewer": ["R1", "R2", "R3", "EIC"], "source_kind": "finding", "sub_claims": ["SC-2"], "severity": "critical", "confidence": 5, "evidence_anchor": "absence: §3.2 Measures and manuscript back matter — expected verbatim wording of the six items, an explicit statement of what was changed from Costa and Wren (2019), and factor-structure evidence in the present sample", "verification_criteria": "An appendix reproduces all six item stems verbatim, an explicit change log states what differs from the source instrument and why, in-sample structural evidence is reported, and the abstract's \"previously validated\" is restated to describe the adapted form."},
    {"id": "R3", "priority": "must_fix", "reviewer": ["R1", "R3"], "source_kind": "finding", "sub_claims": ["SC-5"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.3 \"No identifying information was collected, and responses could not be linked back to individual students.\"", "verification_criteria": "The deduplication mechanism, any retained identifier and its retention period are disclosed, §3.3 describes the anonymity condition accurately, and the stated approval scope matches the mechanism actually used."},
    {"id": "R4", "priority": "must_fix", "reviewer": ["R1", "R3", "EIC"], "source_kind": "finding", "sub_claims": ["SC-3"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.1 Design and participants — expected the enrolled undergraduate population size, a computed response rate, and the year-level distribution of the 214 analyzed cases against institutional benchmarks", "verification_criteria": "Eligible enrolment, invitations delivered and computed response rate are reported; the year-level distribution of the 214 analysed cases is given against institutional benchmarks; where available an early-versus-late responder comparison is reported."},
    {"id": "R5", "priority": "must_fix", "reviewer": ["R2"], "source_kind": "finding", "sub_claims": ["SC-11"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §2 Literature Review — expected citation of the canonical perceived-usefulness source and of existing pooled LMS-acceptance estimates; checked §1, §2, §5, §7, and the reference list", "verification_criteria": "§2 cites the canonical origin of the perceived-usefulness construct with correct attribution and date, engages the UTAUT-generation and synthesis literature, and no founding construct definition is attributed to recent secondary commentary."},
    {"id": "R6", "priority": "must_fix", "reviewer": ["EIC"], "source_kind": "finding", "sub_claims": ["SC-13", "SC-10b"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §7 Conclusion — \"offered as an incremental, design-bounded contribution rather than a causal claim\"", "verification_criteria": "The submission category is Brief Report or Research Note, and the contribution paragraph states positively what prior work leaves unestablished, what institutional profile is under-represented in the existing distribution of estimates, and what a reader can do with this coefficient — or the article grade is retained with a second site or log-based measurement added."},
    {"id": "S1", "priority": "should_fix", "reviewer": ["R1"], "source_kind": "finding", "sub_claims": ["SC-7"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.4 \"Because the use item is ordinal, we also computed a Spearman correlation as a robustness check.\"", "verification_criteria": "A polychoric or ordinal-appropriate coefficient is primary with a bootstrap interval; Pearson and Spearman are retained as sensitivity analyses with intervals; t and df accompany the primary p value."},
    {"id": "S2", "priority": "should_fix", "reviewer": ["R1"], "source_kind": "finding", "sub_claims": ["SC-8", "SC-23"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.2 \"We treat this as an ordinal indicator of self-reported use and interpret it accordingly.\"", "verification_criteria": "The manuscript states that no reliability estimate exists for the outcome and that the reported interval understates total uncertainty, frames the coefficient as a lower bound for comparison, and reports all five category labels with the response frequency distribution."},
    {"id": "S3", "priority": "should_fix", "reviewer": ["R1", "R2"], "source_kind": "finding", "sub_claims": ["SC-6"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §5 Discussion — expected common-method or shared-self-report bias named as a rival explanation for the focal correlation; checked Abstract, §2, §3.2, §4, §5, §6", "verification_criteria": "§5 names common-method variance as a rival explanation for the magnitude of the association and reports any procedural remedies used, or states that none were."},
    {"id": "S4", "priority": "should_fix", "reviewer": ["R3", "R1"], "source_kind": "finding", "sub_claims": ["SC-4"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.1 \"The survey was distributed through the institution's course-announcement channel\"", "verification_criteria": "The manuscript states whether the recruitment channel is LMS-hosted and, if so, treats the resulting selection as a threat to the coefficient itself rather than only to generalisability."},
    {"id": "S5", "priority": "should_fix", "reviewer": ["R2"], "source_kind": "finding", "sub_claims": ["SC-12"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.1 and §3.2 — expected the platform identity and version plus the institution's mandatory-use policy for assignment submission and grade release; checked §1, §3, §4, §6", "verification_criteria": "The platform and version are named, mandatory-use status for submission, quizzes and grade release is stated, and any compulsory LMS activity during the survey window is reported."},
    {"id": "S6", "priority": "should_fix", "reviewer": ["R3"], "source_kind": "finding", "sub_claims": ["SC-18"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §6 Limitations — expected a named limitation for unmeasured confounders of access frequency (assessment schedules, timetable structure, notification settings, device and broadband access, commuter status, paid-work hours)", "verification_criteria": "§6 names the unmeasured access and equity confounder class as a limitation and §5 acknowledges that part of the observed association may be structural rather than attitudinal."},
    {"id": "S7", "priority": "should_fix", "reviewer": ["R3", "R2", "R1"], "source_kind": "finding", "sub_claims": ["SC-9"], "severity": "major", "confidence": 5, "evidence_anchor": "text: Abstract \"perceived usefulness tracks with LMS engagement among undergraduates\"", "verification_criteria": "\"Engagement\" is replaced by self-reported access frequency wherever frequency is what was measured (Abstract, §2, §4, §7), or is explicitly defined as reported access frequency only; the abstract's closing sentence carries the single-institution bound.", "arbitration": "split_upheld_by_editor"},
    {"id": "S8", "priority": "should_fix", "reviewer": ["R2"], "source_kind": "finding", "sub_claims": ["SC-10a"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §2 and §5 — \"effect sizes vary across samples and instruments\", \"consistent with prior technology-acceptance research\"", "verification_criteria": "A pooled prior estimate with its heterogeneity, or a numeric range, is reported and r = .42 is located relative to it; otherwise the comparability claim is removed from the Abstract, §5 and §7."},
    {"id": "S9", "priority": "should_fix", "reviewer": ["R3"], "source_kind": "finding", "sub_claims": ["SC-19"], "severity": "minor", "confidence": 4, "evidence_anchor": "absence: §3.1 Design and the §6 second limitation — expected a stated reason why institutional LMS access logs were not used or not obtainable", "verification_criteria": "One sentence states the actual reason logs were not used — approval scope, data-governance route, or feasibility within the survey window."},
    {"id": "S10", "priority": "should_fix", "reviewer": ["R3"], "source_kind": "finding", "sub_claims": ["SC-17"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §5 \"LMS onboarding which helps students see concrete usefulness — rather than merely announcing that a platform exists — may be worth institutional attention\"", "verification_criteria": "The onboarding implication is deleted, reframed to something the design supports, or accompanied by the argument that makes its directional premise defensible given the paper's stated agnosticism about direction."},
    {"id": "S11", "priority": "should_fix", "reviewer": ["EIC", "R1"], "source_kind": "finding", "sub_claims": ["SC-14"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §4 Results and §3.4 Analysis — expected at least one table or figure, including the scatterplot whose inspection is reported; checked §3.4, §4, all section bodies, and the reference list for any table or figure caption", "verification_criteria": "The scatterplot referenced in §3.4 is supplied and a descriptives table reports both measures, including the use-item category distribution."},
    {"id": "S12", "priority": "nice_to_fix", "reviewer": ["EIC", "R1", "R2", "R3"], "source_kind": "finding", "sub_claims": ["SC-15"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §4 Results — \"The proportion of variance shared by the two measures was accordingly modest\"", "verification_criteria": "§4 reports r-squared as a number (approximately .18) rather than as a qualitative characterisation."},
    {"id": "S13", "priority": "nice_to_fix", "reviewer": ["EIC", "R1"], "source_kind": "finding", "sub_claims": ["SC-16"], "severity": "minor", "confidence": 5, "evidence_anchor": "absence: manuscript front and back matter — expected data-availability, funding, and competing-interests declarations required by mainstream educational-technology venues", "verification_criteria": "Data-availability, funding and competing-interests declarations are present; statistical software and version are named; and either the data or the bivariate cross-tabulation is deposited."},
    {"id": "S14", "priority": "nice_to_fix", "reviewer": ["R1"], "source_kind": "finding", "sub_claims": ["SC-20"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §3.4 \"With n = 214, the study had greater than .80 power to detect a correlation of r >= .19\"", "verification_criteria": "The statement is labelled a post-hoc sensitivity analysis, whether any a priori target N existed is stated, and the boundary wording reads \"approximately .80\"."},
    {"id": "S15", "priority": "nice_to_fix", "reviewer": ["R2"], "source_kind": "finding", "sub_claims": ["SC-22"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §4 — \"consistent with the view that reported engagement reflects many influences beyond perceived usefulness, including course requirements and assessment schedules\"", "verification_criteria": "The attribution of residual variance to course requirements and assessment schedules is removed or explicitly labelled as conjecture about unmeasured factors."}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

**Input gap:** no card supplied a report-level overall recommendation or a report-level Confidence Score. I report each seat's assessed dimension verdicts in their place and did not infer the missing fields.

### Journal-Fit Review Report Summary
- Assessed: D5 = warn, D6 = block (`repairable`). No overall recommendation or report-level confidence supplied. Per-finding confidence 4–5.
- Key point: the category question is decided explicitly — this is a Brief Report, not a full article; calibration is real but is doing work that contribution is supposed to do, and the reference apparatus is unresolvable.

### Reviewer 1 (Methodology) Summary
- Assessed: D1 = block (`repairable`), D3 = warn. No overall recommendation or report-level confidence supplied. Per-finding confidence 4–5.
- Key point: the arithmetic reconciles exactly, but the visible apparatus of precision does less inferential work than its presence implies, and the instrument is documented at a level that does not permit knowing what was correlated with what.

### Reviewer 2 (Domain) Summary
- Assessed: D2 = block (`fatal`). No overall recommendation or report-level confidence supplied. Per-finding confidence 4–5.
- Key point: the entire six-item evidence base is unverifiable on a reserved DOI prefix, which is a reconstruction problem rather than a revision problem; the seat states it would revise the fatal judgement immediately against verifiable records.

### Reviewer 3 (Perspective) Summary
- Assessed: D4 = warn. No overall recommendation or report-level confidence supplied. Per-finding confidence 4–5.
- Key point: scope discipline is genuine but lapses at the sentences that travel furthest — "engagement" for weekly access frequency — and the ethics statement cannot be accurate as written.

### Devil's Advocate Summary
- Assessed: D3 = warn. CRITICAL band deliberately empty with stated reasoning; six MAJOR findings.
- Key point: the standard adversarial attacks all failed; the recurring pattern is that a caution is named and then treated as discharged, and common-method variance is never named at all.
