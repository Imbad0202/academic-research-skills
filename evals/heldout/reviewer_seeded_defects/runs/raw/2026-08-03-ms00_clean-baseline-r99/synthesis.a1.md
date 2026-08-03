# Editorial Decision Package

**Contract**: `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size: 5`
**Synthesizer mode**: v3.6.2 Sprint Contract Synthesizer Protocol (arithmetic) + general Synthesis Protocol (letter and roadmap)

---

## Part 0: Contract Audit (mechanical)

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats | Scores | Verdict (worst assessed eligible) |
|-----|----------|----------------|--------------------------|--------|-----------------------------------|
| D1 methodology_rigor | mandatory | methodology | methodology | block (`block_class: repairable`) | **block** |
| D2 domain_accuracy | mandatory | domain | domain | warn | **warn** |
| D3 argumentative_coherence | mandatory | da, methodology | da, methodology | warn, warn | **warn** |
| D4 cross_disciplinary_relevance | high | perspective | perspective | block (no `block_class` field) | **block** |
| D5 writing_and_structure | normal | eic | eic | warn | **warn** |
| D6 venue_fit_and_contribution | mandatory | eic | eic | block (`block_class: repairable`) | **block** |

All `not_assessed` values were excluded from both numerator and denominator. No dimension was left unassessed by its eligible seats, so no `[DIMENSION-UNASSESSED]` marker is emitted. **No seat declared a fatal block** on any dimension; the audit verdict is therefore `block`, not `block(fatal)`.

### Step 2 — Failure-condition evaluation

| ID | Severity | Quantifier | Expression | Per-dimension result | Fired |
|----|----------|------------|------------|----------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 ✗, D2 ✗, D3 ✗, D6 ✗ (no fatality declared anywhere) | **false** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1 ✓, D2 ✗, D3 ✗, D6 ✓ | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 ✓ (n=1, owner), D2 ✓ (n=1, owner), D3 ✓ (n=2, both), D6 ✓ (n=1, owner) → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 ✓ | **true** |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1–D6 all ✓ | **true** |
| F0 | 10 | all | every dimension scores 'pass' | ✗ | **false** |

### Step 3 — Precedence and emission

Highest severity among fired conditions: **F2 (90)**.

```
dimension_verdicts: [D1=block, D2=warn, D3=warn, D4=block, D5=warn, D6=block]
fired_conditions: [F2, F3, F4, F5]
da_critical_adjudications: []
editorial_decision=major_revision
```

`da_critical_adjudications` is `[]` because the Devil's Advocate card's `#### CRITICAL` table contains headers only and no rows. The DA's seven MAJOR findings are adjudicated in Part 1 under Devil's Advocate Findings; they are not CRITICAL IDs and do not enter this line.

### Card-quality flags (not corrected — Phase Boundary)

These are recorded for the caller, not repaired here:

1. **perspective card** opens with a retracted `## Scoring Plan Dissent` placeholder and a self-correction sentence before `contract_role`. Parsing was unaffected — `contract_role` and all six dimension scores are well-formed — but the artifact is in the delivered card.
2. **perspective card** declares `score: block` on D4 with **no `block_class` field**. The body states the condition is "repairable in principle." I treated it as non-fatal: a synthesizer may never mint fatality, and no fatality was declared.
3. **domain card** raises the reference-verifiability issue (W4) as a *conditional* re-score: "If verification fails, my D2 assessment would move from warn to block." This is recorded as a live escalation trigger below; it does **not** alter the matrix, which scores the record as submitted.
4. **domain card** strengths S1–S3 carry no per-finding Confidence tag. Not load-bearing for any roadmap item.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled *"Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students."* Your manuscript has been reviewed by five independent reviewers: a Journal-Fit Reviewer, three Peer Reviewers (methodology, domain, cross-disciplinary), and a Devil's Advocate.

### Decision: Major Revision

The decision follows the contract arithmetic recorded in Part 0: two mandatory dimensions (methodology rigor, venue fit and contribution) scored `block`, firing F2. It is not a rejection. Every reviewer who declared a block classified it as repairable, and no reviewer declared a fatal block. The panel's own remedy set requires no new data collection.

I want to record one thing before the criticisms, because all five reviewers said it independently and it is not a courtesy. **The manuscript's inferential discipline is genuinely good.** The refusal of causal language is sustained from abstract to conclusion, the reverse pathway is stated affirmatively rather than buried, the limitations are mechanism-specific, and the Spearman check is reported rather than hidden. Four of five reviewers listed this as a strength; the Journal-Fit Reviewer asked explicitly that revision not trade it away for stronger claims. It should not be traded away.

What the panel converged on is a different failure: **the paper's restraint about what it claims is being asked to do the work of telling the reader what its number is worth.** Those are separate obligations, and the second is undischarged.

---

### Consensus Analysis

Consensus is computed **per sub-claim** across the **four non-DA reviewers** (Journal-Fit / R1 methodology / R2 domain / R3 cross-disciplinary), denominator always 4. `not-mentioned` is silence, not agreement and not opposition. The Devil's Advocate is tracked separately.

Twenty-eight sub-claims were decomposed from the five cards. The full inventory is in Part 4. Dispositions: **1 CONSENSUS-4**, **2 CONSENSUS-3**, **8 corroborated (2/4)**, **14 single-reviewer**, **3 SPLIT**.

#### Points of Agreement

**[CONSENSUS-4] SC-1 — The manuscript's stated contribution is comparability with prior work, and the comparison is never performed.**
All four non-DA reviewers reached this independently, and the Devil's Advocate reached it a fifth time. No prior effect size appears anywhere in the manuscript. The Journal-Fit Reviewer's formulation is the sharpest: the paper cites Song (2018) for the proposition that any single-site estimate is "one point in a distribution," and then never supplies the distribution. As the domain reviewer notes, this makes "consistent with prior technology-acceptance research" unfalsifiable as constructed — under the paper's own premises about cross-instrument and cross-site variability, almost any positive coefficient would have been declared consistent. This sub-claim alone carries the D6 block. Confidence 5 from both raising seats.

**[CONSENSUS-3] SC-3 — The perceived-usefulness instrument is not reproduced and the adaptation is not documented.**
Raised by R1 (Critical, conf 5) and R3 (Major, conf 5), corroborated by R2 (Minor, conf 4). **Silent reviewer: the Journal-Fit Reviewer**, who explicitly deferred §3.2 measurement detail to the methodology seat and flagged it as a declared blind spot. α = .88 is evidence of inter-item homogeneity only; the source instrument's validation does not transfer to an undescribed modification. Severity band spread (Critical / Major / Minor) is recorded; R2's Minor attaches to the narrower "previously validated" descriptor claim (SC-15) and does not argue against reproduction, so this is not a split.

**[CONSENSUS-3] SC-16 — The foundational technology-acceptance literature is absent and the construct is attributed to secondary sources.**
Raised by R2 (Major, conf 5), corroborated by R3 (Major, conf 4) and the Journal-Fit Reviewer (Minor, conf 3). **Silent reviewer: R1 (methodology).** The manuscript's definition of perceived usefulness is a near-paraphrase of the tradition's founding formulation, credited to a 2019 instrument paper and a 2020 commentary; the originating source, the extension frameworks that added voluntariness as a moderator, and every synthesis of PU–use effects in education are missing, as is anything post-2021. The Journal-Fit Reviewer's lower band comes with explicit deference — "the reference list's completeness is the domain seat's call" — so the band difference is scoped, not contested.

#### Corroborated findings (2/4 — action-bearing, below the consensus bar)

- **SC-2** — reference list carries the reserved `10.5555` example DOI prefix with sequential suffixes; not independently verifiable. R3 (Critical, conf 4) + R2 (Major, conf 3). *Ranked #1 in Top Blocking Issues despite its 2/4 count — see the note there.*
- **SC-4** — α establishes internal consistency, not dimensionality or construct validity. R1 (Critical, 5) + R2 (Minor, 4).
- **SC-8** — common-method variance never assessed; the paper's restraint addresses direction only. R1 (Major, 5) + R2 (Minor, 3).
- **SC-9** — single coarse ordinal outcome item, no reliability evidence possible, unknown attenuation. R1 (Major, 5) + R2 (unrated cross-seat referral).
- **SC-15** — "previously validated" over-reads what the adapted instrument's evidence establishes. R2 (Minor, 4) + R1 (Critical, 5).
- **SC-7** — setting descriptors (region, LMS platform, collection year, disciplinary composition) withheld. R3 (Minor, 5) + R1 (corroborated within W4).

#### Single-reviewer findings resolved by confidence weighting

Fourteen sub-claims were raised by one reviewer with no conflicting position. Four carry Confidence 5 within the raiser's declared specialty and take full weight: **SC-6** (no population denominator, therefore no response rate and unbounded volunteer skew — R1), **SC-10** (Pearson made primary against the paper's own declared ordinal measurement model — R1), **SC-12** (r² ≈ .18 characterised verbally but never printed — R1), **SC-17** (estimand mismatch: the tradition models PU→intention→use, this paper estimates PU→self-reported use, and never states which link the comparison targets — R2). The remainder are carried at their transported bands in Part 2.

One is flagged for its provenance: **SC-21b** — the domain reviewer's independent recalculation returns power ≈ .80, "not comfortably above it," against the manuscript's "greater than .80." This appears in the domain card's cross-seat notes rather than as a numbered finding, so it carries `[SEVERITY-SOURCE: letter-fallback]` and `[CONFIDENCE-SOURCE: unrated cross-seat referral]`. It is an arithmetic check the author should run regardless of its provenance.

---

### Points of Disagreement

Three sub-claims had `conflict ≥ 1` and were routed to arbitration. All three are resolved; none is left as unresolved dissent.

**SPLIT-1 — SC-5: Is the ethics and sample-accounting section internally consistent?**
- R1 (Major, conf 4) and R3 (Major, conf 5) argue §3.1's "5 duplicate entries were removed" and §3.3's "No identifying information was collected... responses could not be linked back to individual students" cannot both be complete as written.
- The Journal-Fit Reviewer's S3 asserts the opposite in scope: "the arithmetic and the ethics elements are on the page and internally consistent... Nothing in the recruitment or consent chain requires the editor to ask a follow-up question."
- **Editor's Resolution — the contradiction finding is upheld; the Journal-Fit Reviewer's strength is upheld in narrower scope.** Evidence first: duplicate detection requires a persistent marker (IP, session token, device fingerprint, platform response ID, or a pattern heuristic), and each is a quasi-identifier. The two sentences cannot both be complete. The Journal-Fit Reviewer's evidence anchor is the 233 − 14 − 5 = 214 exclusion arithmetic and the enumerated §3.3 elements; that arithmetic *is* clean and that consent chain *is* complete. The Journal-Fit Reviewer did not test the deduplication/anonymity conjunction, and the field-analysis review plan deliberately assigned that specific check to R3 to prevent duplicate flagging. Expertise first: protocol coherence is R3's declared remit and survey operations is R1's. Author must supply a direct answer, not a softening clause. → **R5**.

**SPLIT-2 — SC-11: How severe is the absence of distributional reporting?**
- R1 (Major, conf 5): the linearity, monotonicity, outlier and symmetry assertions in §3.4 are load-bearing for the choice of estimator and cannot be checked; this is inside the D1 block's remedy set.
- Journal-Fit (Minor, conf 5): assessment is not obstructed, since the paper carries few enough numbers that prose reporting suffices; this is why D5 is warn, not block.
- **Editor's Resolution — Major, Priority 1.** The two seats are not disagreeing about the paper; they are scoring different dimensions. The Journal-Fit Reviewer's test was "does this obstruct editorial assessment," and it does not. R1's test was "can the reader verify the assumption checks that license a product-moment coefficient on a five-category ordinal outcome," and it cannot. On expertise, assumption verification for correlational reporting is R1's declared specialty, and the methodology card lists distributional reporting explicitly among the items required to lift the D1 block. The remedies are identical (frequency table, descriptives, scatterplot or cross-tabulation), so upholding the higher band costs the author nothing extra. → **R7**.

**SPLIT-3 — SC-18: How severe is the absent open-science package?**
- R3 (Major, conf 5): a paper whose entire claimed value is transparency and comparability supplies no dataset, correlation matrix, item wording, analysis script, preregistration, or availability statement; the transparency claim is itself unsubstantiated.
- R1 (Minor, conf 5): "a reproducibility gap rather than an error," though it "sits awkwardly beside the paper's self-description."
- **Editor's Resolution — Major, but Priority 2, and split from the item-reproduction component.** Expertise first: R3 holds the declared data-availability panel seat and R3's own card scopes this correctly — the D4 block is driven by the reference list and the unnamed tradition, *not* by SC-18. So SC-18 is Major (the paper's stated contribution depends on it) but is not itself a block driver. The item-stem and adaptation-statement components are already at Priority 1 under SC-3; the residual package (de-identified dataset or correlation matrix, analysis script, preregistration status, an explicit availability statement) sits at Priority 2. → **S2**.

**Note on a predicted disagreement that did not materialise.** The review plan anticipated a productive tension between R2 and the Journal-Fit Reviewer over whether a single-site increment is publishable at all. It did not occur. Both seats converged on the same disposition — R2: "the field does not need another single-site PU–use correlation reported as a novel association. It can use one reported as a benchmarked replication"; Journal-Fit: option (a), benchmark the increment, "at which point the increment is verifiable and the paper clears the bar." I record this because it means the paper's viability is not actually contested by this panel. Only its execution is.

---

### Devil's Advocate Findings

`da_critical_adjudications: []` — the DA declared **no CRITICAL findings**. Its D3 score is `warn`, matching the methodology seat's independent D3 `warn`. Its seven MAJOR findings are adjudicated here for visibility:

| DA | Corroborated by | Adjudication |
|----|-----------------|--------------|
| M1 abstract shifts outcome construct to behavioural "engagement" | R1 W10 (SC-13a) | **VALIDATED** — §2 explicitly instructs the reader to treat the measure as "perceived rather than actual engagement," and the abstract's closing sentence asserts what §2 disclaims. → S1 |
| M2 "consistent with prior work" has no numeric content and is near-unfalsifiable | EIC, R2, R3, R1 (SC-1) | **VALIDATED** — this is the CONSENSUS-4 finding and the D6 block driver. → R1 |
| M3 common-method variance presupposed negligible | R1 W3, R2 W7 (SC-8) | **VALIDATED** → R8 |
| M4 recruitment may be conditioned on the dependent variable | *none* | **UNRESOLVED — pending author answer.** The DA's own confidence is 3, "conditional on an unstated fact about the recruitment channel." If the course-announcement channel sits inside or is reached via the LMS, the "rarely or never" category is structurally under-sampled and r estimates a range-restricted subpopulation. No other seat raised it. The manuscript does not state where the channel sits, so the panel could not resolve it on evidence and I am not resolving it by fiat in either direction. The author must state it; the answer determines whether anything further is required. → folded into **R6** |
| M5 population-level question, no denominator or response rate | R1 W4 (SC-6) | **VALIDATED** → R6 |
| M6 duplicate removal vs anonymity contradiction | R1 W5, R3 W5 (SC-5) | **VALIDATED** — see SPLIT-1 → R5 |
| M7 validity claimed by inheritance ("previously validated") | R2 W6, R1 W1 (SC-15) | **VALIDATED** → R4, S1 |

The Devil's Advocate raised no unique finding that the panel rejected. M4 is the single DA-only substantive hypothesis and it is recorded as unresolved rather than dismissed.

---

### Decision Rationale

The arithmetic gives Major Revision, and the substance agrees with it.

Two mandatory dimensions blocked, both repairable, and they block for the same underlying reason from opposite ends. D6 blocked because the manuscript nominates itself as a comparable data point and then never performs the comparison — a self-incurred obligation, since it is the paper's own citation of Song (2018) that establishes why the comparison is indispensable. D1 blocked because the coefficient's measurement foundation is undocumented: the six-item adapted scale is not reproduced, the adaptation is unspecified, no dimensionality evidence exists in-sample, the population denominator is absent, and the distributional evidence that licenses a Pearson estimate on a five-category ordinal outcome is withheld. D4 blocked on the cross-disciplinary bridge: a construct imported from information systems, a tradition never named, and a reference list that cannot be resolved.

What is striking is what the panel did *not* find. No reviewer found a domain-false statement. The domain seat confirmed the reported quantities are internally coherent — the Fisher-transform interval is right, the Spearman check is consistent, the case attrition closes, and "moderately" is the correct label. The domain seat also declined to block, reasoning that r = .42 is probably squarely consistent with the field's pooled evidence, and that the defect is unsubstantiation of a claim that is very likely true rather than inaccuracy. Three seats independently declined to penalise the paper for lacking a model it legitimately said it was not testing. That restraint from the panel is why this is a revision and not a rejection.

The revision is substantial but bounded. Nothing in the Priority 1 list requires new respondents. It requires the author to retrieve comparator effect sizes and state where .42 falls; to say which estimand the comparison targets; to print the instrument; to print the distributions; to print the denominator; to resolve the anonymity contradiction; and to establish that the six cited works exist.

### Conditional re-evaluation trigger (recorded, not applied)

Two seats made the reference-verification finding conditionally dispositive in their own cards. R2: "If verification fails, my D2 assessment would move from warn to block." R3: "If they do not, that finding supersedes everything else below and moves this manuscript out of the revision category altogether."

**I have not applied either conditional.** The matrix scores the record as submitted, no seat declared a fatal block, and a synthesizer may not mint fatality. The decision stands at Major Revision.

What follows is a routing note for the editor, not a decision: if verification establishes that the cited works do not exist, the panel's own stated re-scoring changes the matrix inputs, and the appropriate action is to re-run the round on the corrected record rather than to treat this letter as final. That call belongs to the editor and the orchestrator, not to this synthesis.

---

### Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | All six references carry the reserved `10.5555` example DOI prefix with sequential suffixes 2050001–2050006, and the journal titles are near-variants of real journals; existence not established | R3 (Critical, conf 4), R2 (Major, conf 3) | `text: References, all six entries — "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"` | R2 |
| 2 | The paper's self-declared status as a "comparable" data point is never discharged — no prior effect size appears anywhere in the manuscript | EIC (Critical, conf 5), R2 (Major, conf 5), R3 (Major, conf 4), R1 (corroborated), DA M2 | `text: §2 Literature Review, final paragraph — "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model."` | R1 |
| 3 | The sole predictor's measurement content is undocumented — items not reproduced, adaptation unspecified, dimensionality untested in-sample | R1 (Critical, conf 5), R3 (Major, conf 5), R2 (Minor, conf 4), DA M7 | `text: §3.2 — "six-item scale adapted from Costa and Wren (2019)" and "the scale showed good internal consistency (Cronbach's α = .88)"` | R4 |

**Note on rank 1's placement.** SC-2 is a corroborated 2/4 finding, not a consensus item. It is ranked first anyway, and the basis is transported severity plus stated dispositiveness, not consensus count: it is the only issue in this package that two independent seats declared capable of superseding the rest of the review, and it is a component of R3's D4 block. Its priority does not rest on how many reviewers happened to check the reference list. Both raising seats were explicit that they are reporting a **verification requirement, not a finding of fabrication** — neither performed live DOI resolution. The correct editorial action is to establish the facts, not to assume them in either direction.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Items with a DA-only or pre-decomposition source use `—` with the DA finding id in parentheses. Severity, Evidence Anchor and Confidence are **transported** from the reviewer cards, never re-derived; fallback tags travel with the row.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| R1 | Discharge the comparability claim: retrieve comparator effect sizes for education-sector PU–use associations, state which estimand the comparison targets, assess instrument commensurability, and state explicitly whether .42 falls near, above, or below the prior range | SC-1, SC-17 | Critical (EIC) / Major (R2, R3) | `text: §2 LR final ¶ — "an incremental data point, comparable with prior work"`; `absence: §2 and §5 — expected a reported comparator effect size or pooled PU–use estimate; checked abstract, §1, §2, §4, §5, §7, all six references` | 5 (EIC), 5 (R2), 4 (R3) | EIC W1, R2 W1+W2, R3 W2, DA M2 | P1 | 5–8 days |
| R2 | Establish that each cited work exists and supports the assertion attached to it; correct or replace any that does not, and correct the DOI records | SC-2 | Critical (R3) / Major (R2) | `text: References, all six entries — "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"` | 4 (R3), 3 (R2 — "unresolvable from the manuscript alone; a flag for verification rather than a finding of fact") | R3 W1, R2 W4 | P1 | 1–3 days (unbounded if replacement is required) |
| R3 | Rebuild §2 on identifiable, discipline-attributed sources: name the technology-acceptance tradition and its home discipline, cite the originating definition of perceived usefulness, engage the extension frameworks and the existing syntheses, and add post-2021 work | SC-16 | Major (R2, R3) / Minor (EIC, deferred) | `text: §1 ¶1 — "a substantial body of work suggests"`; `text: §2 ¶1 — "the degree to which a person believes a technology will help them perform better"` | 5 (R2), 4 (R3), 3 (EIC) | R2 W3, R3 W2, EIC W6 | P1 | 4–6 days |
| R4 | Document the instrument: reproduce all six PU item stems and the frequency item verbatim, state what the adaptation changed relative to the source, report dimensionality evidence in this sample, and correct any claim that the adapted scale inherits the original's validation | SC-3, SC-4, SC-15 | Critical (R1) / Major (R3) / Minor (R2) | `text: §3.2 — "six-item scale adapted from Costa and Wren (2019)" and "Cronbach's α = .88"`; `absence: §3.2 Measures — expected verbatim item wording plus a statement of what the adaptation changed; checked §3.2, §3.4, §4, References, absent appendix` | 5 (R1), 5 (R3), 4 (R2) | R1 W1, R3 W3, R2 W6, DA M7 | P1 | 2–3 days |
| R5 | Resolve the anonymity/deduplication contradiction with a direct statement of what persistent marker (if any) was retained and what the approved protocol permitted; and characterise the 14 excluded incomplete cases against their available responses | SC-5, SC-25 | Major (R1, R3) | `text: §3.1 with §3.3 — "5 duplicate entries were removed" and "responses could not be linked back to individual students"` | 4 (R1), 5 (R3) | R1 W5, R3 W5, DA M6 | P1 | 1 day |
| R6 | Report the undergraduate enrolment denominator and the resulting response rate; report year-level, discipline and enrolment-status composition; and state whether the course-announcement channel sits inside or is reached via the LMS | SC-6, — (DA M4) | Major (R1) / Major (DA) | `text: §3.1 — "All enrolled undergraduates were eligible" and "spanned all four year levels"`; `text: §3.1 — "distributed through the institution's course-announcement channel over a three-week window"` | 5 (R1), 3 (DA — conditional on an unstated fact) | R1 W4, DA M4+M5 | P1 | 1–2 days |
| R7 | Supply the distributional evidence that licenses the estimator: a full frequency distribution for the five-category use item, a descriptives table for both measures, and the scatterplot or cross-tabulation §3.4 relies on; state r² numerically | SC-11 *(SPLIT-2, arbitrated to Major)*, SC-12 | Major (R1, arbitrated) / Minor (EIC) | `text: §3.4 — "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers"`; `text: §4 — "The proportion of variance shared by the two measures was accordingly modest"` | 5 (R1), 5 (EIC) | R1 W6+W7, EIC W3 | P1 | 1–2 days |
| R8 | Address same-source measurement as a threat to the coefficient's magnitude, not only to its direction; and reverse the estimator ordering to follow the declared ordinal measurement model, or report a polychoric estimate if a latent-association claim is intended | SC-8, SC-9, SC-10 | Major (R1) / Minor (R2) | `absence: §3.2 and §5 — expected any assessment of common-method variance arising from same-instrument, same-respondent, same-sitting measurement; checked §3.2, §3.3, §3.4, §5, §6`; `text: §3.2 and §3.4 — "a single five-point frequency item" and "we also computed a Spearman correlation as a robustness check"` | 5 (R1), 3 (R2) | R1 W2+W3, R2 W7, DA M3 | P1 | 2–3 days |

### Required Item Details

**R1 — Discharge the comparability claim**
- **Source**: EIC W1 (Critical, conf 5), R2 W1 (Major, conf 5), R2 W2 (Major, conf 5), R3 W2 (Major, conf 4), DA M2
- **Why it blocks**: carries the D6 `block` (`block_class: repairable`). The manuscript asserts comparability in the abstract, §2, §5 and §7 and supplies no comparator value in any of them.
- **Acceptance criteria**: The revised manuscript reports at least one comparator effect size or pooled estimate for education-sector PU–use associations with its source, states which link of the acceptance path (PU→intention vs PU→use, self-reported vs log-validated) the comparison targets, states whether the instruments are commensurable with a six-item adapted PU scale and a single-item frequency measure, and states in text whether r = .42 falls near, above or below that range — or, if commensurability fails, replaces the "comparable with prior work" framing throughout.

**R2 — Establish reference existence**
- **Source**: R3 W1 (Critical, conf 4), R2 W4 (Major, conf 3)
- **Why it blocks**: component of the D4 `block`; both raising seats declared it conditionally dispositive for their own dimensions.
- **Acceptance criteria**: Every reference resolves to a registered DOI at a real publisher prefix, each cited work is independently locatable, and each supports the specific assertion attached to it in text — with any work that fails these tests removed and its dependent assertion re-sourced or withdrawn.

**R3 — Rebuild the literature base**
- **Source**: R2 W3 (Major, conf 5), R3 W2 (Major, conf 4), EIC W6 (Minor, conf 3)
- **Why it blocks**: CONSENSUS-3; component of the D4 `block` and a precondition for R1.
- **Acceptance criteria**: §2 names the technology-acceptance tradition and its originating discipline, attributes the perceived-usefulness construct to its primary source rather than to the 2019/2020 secondary works, cites at least one extension framework covering voluntariness and at least one synthesis of PU–use effects in education, and includes post-2021 literature.

**R4 — Document the instrument**
- **Source**: R1 W1 (Critical, conf 5), R3 W3 (Major, conf 5), R2 W6 (Minor, conf 4), DA M7
- **Why it blocks**: CONSENSUS-3; named by R1 as a required element to lift the D1 `block`.
- **Acceptance criteria**: All six perceived-usefulness item stems and the frequency item appear verbatim in the manuscript or an appendix, the manuscript states which items were changed, dropped, reworded or retranslated relative to the source instrument, in-sample dimensionality evidence is reported alongside α, and the abstract no longer attributes the original's validation to the adapted six-item version.

**R5 — Resolve the anonymity/deduplication contradiction**
- **Source**: R1 W5 (Major, conf 4), R3 W5 (Major, conf 5), DA M6 — arbitrated at SPLIT-1
- **Why it blocks**: named by R1 among the D1 `block`'s internal-inconsistency drivers; a protocol-coherence defect that adjacent-field readers may treat as a template.
- **Acceptance criteria**: §3.1 and §3.3 are mutually consistent as written — the deduplication mechanism is named, any retained quasi-identifier is disclosed with its ethics-approval status, or the anonymity statement is corrected — and the 14 excluded incomplete cases are compared to retained cases on the items they did complete.

**R6 — Report the sampling frame**
- **Source**: R1 W4 (Major, conf 5), DA M5, DA M4 (unresolved)
- **Why it blocks**: named by R1 among the D1 `block` drivers; without a denominator the conceded volunteer skew cannot be bounded at all.
- **Acceptance criteria**: The manuscript reports the eligible undergraduate enrolment, the resulting response rate, the sample's year-level and disciplinary composition, and an explicit statement of whether the course-announcement recruitment channel sits inside or is reached through the LMS.

**R7 — Supply the distributional evidence**
- **Source**: R1 W6 (Major, conf 5), R1 W7 (Minor, conf 5), EIC W3 (Minor, conf 5) — arbitrated at SPLIT-2 to Major
- **Why it blocks**: the §3.4 assumption checks carry the argumentative weight for the choice of estimator while the evidence for them is withheld.
- **Acceptance criteria**: The manuscript includes a full frequency distribution for the five-category use item, a descriptives table for both measures, the scatterplot or a cross-tabulation supporting the linearity and monotonicity claims, and r² stated as a number.

**R8 — Treat same-source measurement and fix the estimator ordering**
- **Source**: R1 W2 (Major, conf 5), R1 W3 (Major, conf 5), R2 W7 (Minor, conf 3), DA M3
- **Why it blocks**: named by R1 as a required element to lift the D1 `block`; the manuscript's hedging addresses causal direction only, leaving the magnitude claim unbounded in both directions.
- **Acceptance criteria**: The manuscript explicitly addresses common-method variance as a threat to the coefficient's magnitude (procedural or statistical, or a reasoned argument for negligibility), and either makes the rank-based coefficient primary in §3.4 consistent with §3.2's ordinal declaration or reports a polychoric estimate, with the change of ordering stated rather than silent.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| S1 | Correct the abstract: restore "self-reported use" in place of "engagement", restore the single-site and volunteer boundaries in place of unqualified "undergraduates", restore the 95% CI and the Spearman check, and correct "previously validated" | SC-13a, SC-13b, SC-14 | Minor (R1, EIC) / Major (DA M1, M7) | `text: Abstract — "perceived usefulness tracks with LMS engagement among undergraduates"`; `text: Abstract — "r = .42, p < .001"` | 5 (R1), 4 (EIC), 5 (DA M1) | R1 W10, EIC W4, DA M1+M7 | P2 | 0.5 day |
| S2 | Supply the residual open-science package: de-identified item-level dataset or correlation matrix with n, analysis script, preregistration status, and an explicit availability statement | SC-18 *(SPLIT-3, arbitrated to Major)* | Major (R3, arbitrated) / Minor (R1) | `absence: back matter following §7 — expected data-availability, code-availability and preregistration statements; checked Abstract, §3.3, §3.4, §6, §7, References` | 5 (R3), 5 (R1) | R3 W7, R1 W9 | P2 | 1–2 days |
| S3 | Add setting descriptors: country or region, LMS platform, data-collection year, disciplinary composition | SC-7 | Minor (R3) | `absence: §3.1 — expected country or region, LMS platform, data-collection year and disciplinary composition; checked Abstract, §3.1, §3.3, §5, §6` | 5 (R3) | R3 W4, R1 W4 | P2 | 0.5 day |
| S4 | Name the barrier that prevented access to institutional LMS log data — ethics scope, data-governance policy, technical access, cost, or a decision not to ask | SC-24 | Minor (R3) | `absence: §6 — expected the named barrier that prevented access to institutional LMS log data; checked §2, §3.3, §3.4, §5, §6` | 4 (R3) | R3 W6 | P2 | 0.25 day |
| S5 | Engage the voluntariness/mandatoriness moderator: state that the estimate comes from a context where LMS use is partly compelled, and cite what the field knows about how that changes the association's magnitude and meaning | SC-23 | Minor (R2) | `text: §4 ¶2 — "including course requirements and assessment schedules"` | 4 (R2) | R2 W5 | P2 | 1 day (folds into R3) |
| S6 | Reword the sensitivity statement to state its planning status honestly (a priori vs post hoc on the realised n), and re-verify the ">.80" claim against the domain seat's recalculation of ≈.80 | SC-21, SC-21b | Minor (R1); `[SEVERITY-SOURCE: letter-fallback]` for SC-21b | `text: §3.4 — "greater than .80 power to detect a correlation of r >= .19" and "so the design was sensitive to small-to-moderate associations"` | 4 (R1); `[CONFIDENCE-SOURCE: unrated cross-seat referral]` for SC-21b | R1 W8, R2 cross-seat note | P2 | 0.5 day |
| S7 | Reframe the §5 onboarding implication as explicitly conditional on a direction the design cannot identify, or restate it as a hypothesis for a design that could distinguish the two pathways | SC-20 | Minor (R1) | `text: §5 — "offers modest support for the intuition that LMS onboarding which helps students see concrete usefulness"` | 4 (R1) | R1 W11, DA (body) | P2 | 0.25 day |
| S8 | Decide the article category with the editor: full research article with the R1 benchmarking in place, or resubmission to the short-paper / replication track with explicit replication framing and a benchmark table | SC-19 | Major (EIC) | `text: §1 — "It asks a deliberately narrow question"` | 4 (EIC) | EIC W2 | P2 | Decision, not effort |
| S9 | Acknowledge in Measures or Limitations that a single-construct self-report cannot separate perceived usefulness from generalised platform favourability (discriminant validity untested here) | SC-26 | Minor (R2) | `absence: §3.2 and §6 — expected acknowledgement that a single-construct self-report cannot separate perceived usefulness from generalised platform favourability; checked §2, §3.2, §4, §5, §6` | 3 (R2) | R2 W7 | P3 | 0.25 day |
| S10 | Consolidate the duplicated hedging (the non-causality caution appears in the abstract, §2, §5, §6 and §7; the self-report/logs caution in §2, §5 and §6) — prune the restatements, keep §6, and reinvest the space in the R1 benchmarking. Do not weaken the cautions themselves | SC-22 | Minor (EIC) | `text: §6 — "Third, the cross-sectional design precludes any causal or temporal inference."` | 4 (EIC) | EIC W5 | P3 | 0.5 day |

> Transported metadata appears on every row above, not only on the Top Blocking rows. Where two seats transported different bands for the same sub-claim, both are shown with attribution; no band was re-derived by this synthesis. Two rows carry provenance fallback tags (S6). The Priority 3 rows (S9, S10) are substantive minor findings from reviewer cards, not aggregated editorial polish; `source_kind: "reviewer"` applies to all rows in this package. No `source_kind: "editorial"` items were generated — the panel raised no sub-threshold Minor Issues outside the finding channel.

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total: 17–28 days, R2 unbounded if replacement is required)
- [ ] R1: Retrieve comparator effect sizes, state the estimand, assess commensurability, locate .42 in the distribution
- [ ] R2: Verify every reference exists and supports its attached assertion; correct the DOI records
- [ ] R3: Rebuild §2 on named, discipline-attributed, canonical and post-2021 sources
- [ ] R4: Print the six item stems and the frequency item; document the adaptation; report in-sample dimensionality; fix "previously validated"
- [ ] R5: Resolve the anonymity/deduplication contradiction with a direct answer; characterise the 14 excluded cases
- [ ] R6: Report enrolment denominator, response rate, sample composition; state where the recruitment channel sits
- [ ] R7: Add the frequency distribution, descriptives table and scatterplot; print r²
- [ ] R8: Address common-method variance as a magnitude threat; reverse the estimator ordering or report polychoric

#### Priority 2 — Content Supplementation (estimated total: 4–6 days)
- [ ] S1: Correct the abstract's construct, population, interval and validation claims
- [ ] S2: Supply the residual open-science package
- [ ] S3: Add setting descriptors
- [ ] S4: Name the log-data access barrier
- [ ] S5: Engage the voluntariness moderator literature
- [ ] S6: Fix the sensitivity statement's planning status and re-verify the ≈.80 boundary
- [ ] S7: Make the onboarding implication direction-conditional
- [ ] S8: Settle the article category with the editor

#### Priority 3 — Text and Structure (estimated total: 1 day)
- [ ] S9: Add the discriminant-validity caveat
- [ ] S10: Consolidate duplicated hedging without weakening it

### Revision Deadline

**6–8 weeks.** No item requires new data collection. R2's timeline is the one genuine unknown: if references require replacement rather than correction, R1 and R3 both depend on it and the schedule should be renegotiated rather than compressed.

### What not to change

The panel was unanimous that the manuscript's correlational discipline is a strength — five of five cards recorded it. Do not respond to this decision by strengthening the claims. The Journal-Fit Reviewer stated it directly: "I would resist any revision that traded it for stronger claims." The problem is not that the paper claims too little; it is that it never tells the reader what its number is worth.

### Response Letter

Use `templates/revision_response_template.md` and respond to every item R1–R8 and S1–S10 individually, including items you decline. Two items require an authored answer rather than a hedge: **R5** (the deduplication mechanism) and **R6**'s recruitment-channel component (DA M4, recorded as unresolved). A softening clause will not close either.

### Roadmap — machine form (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "major_revision",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": ["eic", "domain", "perspective", "methodology"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §2 Literature Review, final paragraph — \"It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model.\"", "source_kind": "reviewer", "sub_claims": ["SC-1", "SC-17"], "verification_criteria": "At least one comparator effect size or pooled PU-use estimate is reported with its source; the targeted estimand (PU-intention vs PU-use; self-report vs log-validated) is stated; instrument commensurability is assessed; r=.42 is located near/above/below the prior range, or the comparability framing is replaced."},
    {"id": "R2", "priority": "must_fix", "reviewer": ["perspective", "domain"], "severity": "critical", "confidence": 4, "evidence_anchor": "text: References, all six entries — \"https://doi.org/10.5555/2050001\" and \"https://doi.org/10.5555/2050006\"", "source_kind": "reviewer", "sub_claims": ["SC-2"], "verification_criteria": "Every reference resolves to a registered publisher DOI, is independently locatable, and supports the specific assertion attached to it; any failing work is removed and its dependent assertion re-sourced or withdrawn."},
    {"id": "R3", "priority": "must_fix", "reviewer": ["domain", "perspective", "eic"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §2 ¶1 — \"the degree to which a person believes a technology will help them perform better\"", "source_kind": "reviewer", "sub_claims": ["SC-16"], "verification_criteria": "§2 names the acceptance tradition and its home discipline, cites the originating definition of perceived usefulness, cites at least one voluntariness-moderator framework and at least one education-sector PU-use synthesis, and includes post-2021 literature."},
    {"id": "R4", "priority": "must_fix", "reviewer": ["methodology", "perspective", "domain"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §3.2 — \"six-item scale adapted from Costa and Wren (2019)\" and \"the scale showed good internal consistency (Cronbach's α = .88)\"", "source_kind": "reviewer", "sub_claims": ["SC-3", "SC-4", "SC-15"], "verification_criteria": "All six PU item stems and the frequency item appear verbatim; the adaptation's changes relative to the source are stated; in-sample dimensionality evidence is reported alongside alpha; the abstract no longer attributes the original's validation to the adapted scale."},
    {"id": "R5", "priority": "must_fix", "reviewer": ["methodology", "perspective"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.1 with §3.3 — \"5 duplicate entries were removed\" and \"responses could not be linked back to individual students\"", "source_kind": "reviewer", "sub_claims": ["SC-5", "SC-25"], "verification_criteria": "§3.1 and §3.3 are mutually consistent: the deduplication mechanism is named and any retained quasi-identifier disclosed with its approval status, or the anonymity statement is corrected; and the 14 excluded incomplete cases are compared to retained cases on completed items."},
    {"id": "R6", "priority": "must_fix", "reviewer": ["methodology", "da"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.1 — \"All enrolled undergraduates were eligible\" and \"The analyzed sample of 214 students spanned all four year levels\"", "source_kind": "reviewer", "sub_claims": ["SC-6"], "verification_criteria": "Eligible undergraduate enrolment, response rate, and year-level plus disciplinary composition are reported; and the manuscript states whether the course-announcement recruitment channel sits inside or is reached through the LMS."},
    {"id": "R7", "priority": "must_fix", "reviewer": ["methodology", "eic"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.4 — \"Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers\"", "source_kind": "reviewer", "sub_claims": ["SC-11", "SC-12"], "verification_criteria": "A full frequency distribution for the five-category use item, a descriptives table for both measures, and the supporting scatterplot or cross-tabulation are included; r-squared is stated numerically."},
    {"id": "R8", "priority": "must_fix", "reviewer": ["methodology", "domain", "da"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.2 Measures and §5 Discussion — expected any assessment of common-method variance arising from same-instrument, same-respondent, same-sitting measurement of both variables; checked §3.2, §3.3, §3.4, §5, §6", "source_kind": "reviewer", "sub_claims": ["SC-8", "SC-9", "SC-10"], "verification_criteria": "Common-method variance is explicitly addressed as a threat to the coefficient's magnitude; and the rank-based coefficient is made primary consistent with §3.2's ordinal declaration, or a polychoric estimate is reported, with the change stated."},
    {"id": "S1", "priority": "should_fix", "reviewer": ["methodology", "eic", "da"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: Abstract — \"perceived usefulness tracks with LMS engagement among undergraduates\"", "source_kind": "reviewer", "sub_claims": ["SC-13a", "SC-13b", "SC-14"], "verification_criteria": "The abstract reports self-reported use rather than engagement, retains the single-site and volunteer boundaries, reports the 95% CI and the Spearman check, and no longer calls the adapted instrument previously validated."},
    {"id": "S2", "priority": "should_fix", "reviewer": ["perspective", "methodology"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: back matter following §7 — expected data-availability, code-availability, and preregistration statements; checked Abstract, §3.3, §3.4, §6, §7, and References", "source_kind": "reviewer", "sub_claims": ["SC-18"], "verification_criteria": "A de-identified item-level dataset or correlation matrix with n, the analysis script, preregistration status, and an explicit availability statement are provided."},
    {"id": "S3", "priority": "should_fix", "reviewer": ["perspective", "methodology"], "severity": "minor", "confidence": 5, "evidence_anchor": "absence: §3.1 Design and participants — expected country or region, LMS platform, data-collection year, and disciplinary composition of respondents; checked Abstract, §3.1, §3.3, §5, and §6", "source_kind": "reviewer", "sub_claims": ["SC-7"], "verification_criteria": "Country or region, LMS platform, data-collection year, and disciplinary composition are reported."},
    {"id": "S4", "priority": "should_fix", "reviewer": ["perspective"], "severity": "minor", "confidence": 4, "evidence_anchor": "absence: §6 Limitations — expected the named barrier that prevented access to institutional LMS log data, such as ethics scope, data-governance policy, technical access, or cost; checked §2, §3.3, §3.4, §5, and §6", "source_kind": "reviewer", "sub_claims": ["SC-24"], "verification_criteria": "§6 names the specific barrier that prevented use of institutional LMS log data."},
    {"id": "S5", "priority": "should_fix", "reviewer": ["domain"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §4 ¶2 — \"including course requirements and assessment schedules\"", "source_kind": "reviewer", "sub_claims": ["SC-23"], "verification_criteria": "The manuscript states that the estimate comes from a partly-compelled use context and cites the moderator literature on how voluntariness changes the association's magnitude and meaning."},
    {"id": "S6", "priority": "should_fix", "reviewer": ["methodology", "domain"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §3.4 — \"the study had greater than .80 power to detect a correlation of r >= .19\" and \"so the design was sensitive to small-to-moderate associations\"", "source_kind": "reviewer", "sub_claims": ["SC-21", "SC-21b"], "provenance_flags": ["SEVERITY-SOURCE: letter-fallback (SC-21b)", "CONFIDENCE-SOURCE: unrated cross-seat referral (SC-21b)"], "verification_criteria": "The sensitivity statement declares whether it was specified a priori or computed post hoc on the realised n, and the >.80 figure is re-verified against the boundary recalculation of approximately .80."},
    {"id": "S7", "priority": "should_fix", "reviewer": ["methodology", "da"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §5 — \"offers modest support for the intuition that LMS onboarding which helps students see concrete usefulness\"", "source_kind": "reviewer", "sub_claims": ["SC-20"], "verification_criteria": "The onboarding implication is stated as explicitly conditional on the perception-to-use direction, or reframed as a hypothesis for a design that could distinguish the two pathways."},
    {"id": "S8", "priority": "should_fix", "reviewer": ["eic"], "severity": "major", "confidence": 4, "evidence_anchor": "text: §1 Introduction — \"It asks a deliberately narrow question\"", "source_kind": "reviewer", "sub_claims": ["SC-19"], "verification_criteria": "The article category is settled with the editor: full research article with R1 benchmarking in place, or short-paper/replication track with explicit replication framing and a benchmark table."},
    {"id": "S9", "priority": "nice_to_fix", "reviewer": ["domain"], "severity": "minor", "confidence": 3, "evidence_anchor": "absence: §3.2 Measures and §6 Limitations — expected acknowledgement that a single-construct self-report cannot separate perceived usefulness from generalised platform favourability; checked §2, §3.2, §4, §5, §6", "source_kind": "reviewer", "sub_claims": ["SC-26"], "verification_criteria": "Measures or Limitations acknowledges that discriminant validity between perceived usefulness and generalised platform favourability is untested in this design."},
    {"id": "S10", "priority": "nice_to_fix", "reviewer": ["eic"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §6 Limitations — \"Third, the cross-sectional design precludes any causal or temporal inference.\"", "source_kind": "reviewer", "sub_claims": ["SC-22"], "verification_criteria": "The non-causality and self-report cautions are consolidated (retained in §6, pruned from §5 and §7) without any caution being weakened or removed."}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

The sprint-contract card format carries **dimension scores and per-finding confidence**, not an overall recommendation or a report-level confidence score. Those two fields are recorded as absent rather than inferred.

| Dimension | Journal-Fit (eic) | R1 Methodology | R2 Domain | R3 Cross-disciplinary | DA |
|-----------|-------------------|----------------|-----------|-----------------------|-----|
| Overall recommendation | *(absent — not in sprint card format)* | *(absent)* | *(absent)* | *(absent)* | *(absent)* |
| Report-level confidence | *(absent — per-finding confidence supplied instead)* | *(absent)* | *(absent)* | *(absent)* | *(absent)* |
| Dimensions assessed | D5 warn, D6 block | D1 block, D3 warn | D2 warn | D4 block | D3 warn |
| Weaknesses / findings | 6 (1 Critical, 1 Major, 4 Minor) | 11 (1 Critical, 5 Major, 5 Minor) | 7 (4 Major, 3 Minor) | 7 (1 Critical, 4 Major, 2 Minor) | 7 Major, 0 Critical |
| Strengths | 4 | 5 | 3 | 5 | recorded in body |
| Key weaknesses | → Part 4 inventory | → Part 4 | → Part 4 | → Part 4 | → DA table, Part 1 |
| Per-finding confidence range | 3–5 | 4–5 | 3–5 | 4–5 | 3–5 |

**Journal-Fit Reviewer (eic)** — D5 warn, D6 block (repairable). Key point: the paper self-nominates as a comparable increment and never performs the comparison; the modesty is genuine calibration on the inferential axis and a substitute for missing work on the contribution axis, and those must not be collapsed in revision.

**Peer Reviewer 1 — Methodology** — D1 block (repairable), D3 warn. Key point: direction and magnitude are independent problems and the manuscript addresses only the first; the coefficient's defensibility as an *estimate* is untested because the instrument, the denominator, the distributions and the same-source threat are all undocumented.

**Peer Reviewer 2 — Domain** — D2 warn. Key point: nothing here is domain-false and r = .42 is probably squarely consistent with the field's pooled evidence — which is precisely why the paper's failure to demonstrate it is the defect; the honest framing available to the authors was stronger than the one they chose.

**Peer Reviewer 3 — Cross-disciplinary** — D4 block. Key point: the paper imports a construct from a tradition it never names, and the reference list that would carry an outside reader into that tradition does not resolve; a manuscript whose claimed value is transparency supplies no transparency infrastructure.

**Devil's Advocate** — D3 warn, 0 CRITICAL. Key point: the central correlational claim survives adversarial pressure; the surrounding layer of claims — the abstract's construct shift, the near-unfalsifiable consistency claim, and the unargued independence of two same-instrument self-reports — does not.

---

## Part 4: Sub-Claim Inventory (Step 1b)

Twenty-eight sub-claims, one row per `(sub_claim, reviewer)` position. Denominator is always the four non-DA reviewers. `agree` = raised + corroborated; `conflict` = disputed; `silent` = not-mentioned.

| SC | Parent weakness | eic | R1 | R2 | R3 | agree / conflict | Disposition |
|----|-----------------|-----|----|----|----|------------------|-------------|
| SC-1 | Comparability never discharged | raised (Critical, 5) | corroborated (within W3, Major, 5) | raised (Major, 5) | corroborated (Major, 4) | 4 / 0 | **CONSENSUS-4** |
| SC-2 | Reference verifiability | not-mentioned | not-mentioned | raised (Major, 3) | raised (Critical, 4) | 2 / 0 | corroborated |
| SC-3 | Instrument not reproduced / adaptation undocumented | not-mentioned *(explicit deferral)* | raised (Critical, 5) | corroborated (Minor, 4) | raised (Major, 5) | 3 / 0 | **CONSENSUS-3** (silent: eic) |
| SC-4 | α ≠ dimensionality / construct validity | not-mentioned | raised (Critical, 5) | corroborated (Minor, 4) | not-mentioned | 2 / 0 | corroborated |
| SC-5 | Anonymity vs deduplication | **disputed** (S3, 5) | raised (Major, 4) | not-mentioned | raised (Major, 5) | 2 / 1 | **SPLIT-1** |
| SC-6 | No population denominator / response rate | not-mentioned | raised (Major, 5) | not-mentioned | not-mentioned | 1 / 0 | single-reviewer (conf 5, full weight) |
| SC-7 | Setting descriptors withheld | not-mentioned | corroborated (within W4, Major, 5) | not-mentioned | raised (Minor, 5) | 2 / 0 | corroborated |
| SC-8 | Common-method variance unassessed | not-mentioned | raised (Major, 5) | corroborated (Minor, 3) | not-mentioned | 2 / 0 | corroborated |
| SC-9 | Single coarse ordinal outcome item | not-mentioned | raised (Major, 5) | corroborated (cross-seat referral, unrated) | not-mentioned | 2 / 0 | corroborated |
| SC-10 | Pearson-primary contradicts declared ordinal model | not-mentioned | raised (Major, 5) | not-mentioned | not-mentioned | 1 / 0 | single-reviewer (conf 5, full weight) |
| SC-11 | Distributional reporting too thin to verify assumptions | **disputed** (Minor, 5) | raised (Major, 5) | not-mentioned | not-mentioned | 1 / 1 | **SPLIT-2** |
| SC-12 | r² never printed | not-mentioned | raised (Minor, 5) | not-mentioned *(computed r²≈.18 independently; endorsed the label's accuracy — compatible remedy, not a dispute)* | not-mentioned | 1 / 0 | single-reviewer (conf 5, full weight) |
| SC-13a | Abstract widens outcome to "engagement" | not-mentioned | raised (Minor, 5) | not-mentioned | not-mentioned | 1 / 0 | single-reviewer |
| SC-13b | Abstract drops single-site / volunteer boundaries | not-mentioned | raised (Minor, 5) | not-mentioned | not-mentioned | 1 / 0 | single-reviewer |
| SC-14 | Abstract drops CI and robustness check | raised (Minor, 4) | not-mentioned | not-mentioned | not-mentioned | 1 / 0 | single-reviewer |
| SC-15 | "Previously validated" over-reads the adaptation | not-mentioned | corroborated (Critical, 5) | raised (Minor, 4) | not-mentioned | 2 / 0 | corroborated |
| SC-16 | Canonical literature absent / secondary attribution | corroborated (Minor, 3, *explicit deferral*) | not-mentioned | raised (Major, 5) | corroborated (Major, 4) | 3 / 0 | **CONSENSUS-3** (silent: R1) |
| SC-17 | Estimand mismatch (PU→intention vs PU→use) | not-mentioned | not-mentioned | raised (Major, 5) | not-mentioned | 1 / 0 | single-reviewer (conf 5, full weight) |
| SC-18 | No data / code / preregistration availability | not-mentioned | **disputed** (Minor, 5) | not-mentioned | raised (Major, 5) | 1 / 1 | **SPLIT-3** |
| SC-19 | Brief-report content in a full-article submission | raised (Major, 4) | not-mentioned | not-mentioned | not-mentioned | 1 / 0 | single-reviewer |
| SC-20 | Practical implication licensed only by the unidentifiable direction | not-mentioned | raised (Minor, 4) | not-mentioned | not-mentioned | 1 / 0 | single-reviewer |
| SC-21 | Sensitivity statement post hoc, framed as design property | not-mentioned *(S2, deferred)* | raised (Minor, 4) | not-mentioned | not-mentioned *(S4, deferred)* | 1 / 0 | single-reviewer |
| SC-21b | Power ≈ .80, not "greater than .80" | not-mentioned | not-mentioned | raised (cross-seat note) `[SEVERITY-SOURCE: letter-fallback]` `[CONFIDENCE-SOURCE: unrated cross-seat referral]` | not-mentioned | 1 / 0 | single-reviewer |
| SC-22 | Hedging duplicated across five sections | raised (Minor, 4) | not-mentioned | not-mentioned | not-mentioned | 1 / 0 | single-reviewer |
| SC-23 | Voluntariness moderator named then unengaged | not-mentioned | not-mentioned | raised (Minor, 4) | not-mentioned | 1 / 0 | single-reviewer |
| SC-24 | Log-data barrier never named | not-mentioned | not-mentioned | not-mentioned | raised (Minor, 4) | 1 / 0 | single-reviewer |
| SC-25 | Incomplete-case exclusion uncharacterised | not-mentioned | raised (Major, 4) | not-mentioned | not-mentioned | 1 / 0 | single-reviewer |
| SC-26 | Single construct cannot separate PU from platform favourability | not-mentioned | not-mentioned | raised (Minor, 3) | not-mentioned | 1 / 0 | single-reviewer (conf 3, standard weight) |

**Decomposition discipline note.** Every sub-claim above traces to a claim a reviewer actually made. No sub-claim was introduced by this synthesis. Where a reviewer's numbered weakness bundled several atomic claims (R1 W1 → SC-3 + SC-4 + SC-15; R1 W4 → SC-6 + SC-7; R1 W5 → SC-5 + SC-25; R1 W10 → SC-13a + SC-13b; R2 W1 → SC-1; R2 W6 → SC-15), the bundle was split so that a minority sub-claim could not be buried inside a majority one.

**Surface-form parity check (Step 1c).** Two weighting decisions in this synthesis turned on evidence quality, and I ran the opposite-style counterfactual on both. SC-2's raising cards differ sharply in register — R3's is procedurally specific ("documented example/test prefix"), R2's is hedged ("to my knowledge," conf 3). The item's rank-1 placement rests on the observable pattern in the reference list and on both seats' stated dispositiveness, not on R3's more technical phrasing; rewritten in R2's hedged register, it would rank identically. SC-21b arrives as an informal aside in a cross-seat note with no severity or confidence tag, and it is carried into the roadmap at full action-bearing weight anyway, because an arithmetic recalculation is either right or wrong regardless of where it was written. No sub-claim was down-weighted for informal phrasing, and none was credited for technical specificity absent paper evidence. No sub-claim was marked unevaluable.

---

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — This synthesis was invoked in `reviewer_full` mode, which requires a provenance statement, but **no provenance stamp was supplied by the dispatching layer**. I therefore cannot state which model family executed which reviewer seat.

Because the stamp is absent, no claim of cross-family model independence is made here, and none should be inferred from this package. The five cards may have been produced by five instances of the same model family; nothing in the material available to me establishes otherwise. Provenance was not inferred from card style, phrasing, or content — that inference is not available and would not be sound if attempted.

No cross-family aggregate and no "same-model majority" figure has been computed; both are outside this role's permitted operations. Where reviewers split, the split is visible by inspection in the Part 4 inventory and the Part 0 matrix.

**Cross-model blind decision check (#518):** not invoked. `ARS_CROSS_MODEL` was not set in this invocation and no consent gate was passed, so the editorial decision above is single-model.

---

## Quality Gate Record

- [x] All five reviewer cards read in full and cited by finding id
- [x] Consensus and disagreement identified per sub-claim, labelled with explicit counts over the fixed denominator of 4
- [x] All three SPLITs arbitrated with recorded rationale; one DA finding (M4) recorded as unresolved rather than auto-kept or auto-dismissed
- [x] Decision derived mechanically from the contract; no aggregation rule introduced beyond `cross_reviewer_quantifier` + `severity`; no fired condition's action softened
- [x] Every roadmap item traceable to a specific reviewer finding; no synthesizer-authored issues
- [x] Severity, evidence anchor and confidence transported on every row; two provenance fallback tags applied where card metadata was absent
- [x] Roadmap emitted in both narrative and Schema 7 machine form; Required blocks R1–R8 contiguous and ordered to the Required table
- [x] No fatality minted; both declared blocks carried as repairable; the conditional escalation trigger recorded without being applied
- [x] Card-quality gaps flagged, not silently repaired

**Deliverable complete.** Revision work belongs to a separate `academic-paper` Phase 6 re-invocation of `draft_writer_agent`; control returns to the caller.
