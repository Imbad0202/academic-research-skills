# Editorial Decision Package

**Manuscript**: *Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students*
**Contract**: `reviewer/reviewer_full/v2` · baseline v3.20.0 · panel_size 5
**Prior checker diagnostic addressed**: `[SYNTHESIS-PARSE: synthesis.a1.md: expected exactly one fired_conditions line, found 0]` — the four mechanical audit lines are emitted once each, below.

---

## Part 0: Sprint Contract Audit (v3.6.2 mechanical)

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats | Scores | Dimension verdict |
|-----|----------|----------------|-------------------------|--------|-------------------|
| D1 methodology_rigor | mandatory | methodology | 1 (methodology) | warn | **warn** |
| D2 domain_accuracy | mandatory | domain | 1 (domain) | block (repairable) | **block** |
| D3 argumentative_coherence | mandatory | da, methodology | 2 (da, methodology) | warn, warn | **warn** |
| D4 cross_disciplinary_relevance | high | perspective | 1 (perspective) | warn | **warn** |
| D5 writing_and_structure | normal | eic | 1 (eic) | warn | **warn** |
| D6 venue_fit_and_contribution | mandatory | eic | 1 (eic) | block (repairable) | **block** |

All ineligible `not_assessed` values excluded from numerator and denominator. No dimension is unassessed. No assessed eligible seat declared a fatal block — both blocks carry `block_class: repairable`.

**Audit verdict**: `block` (not fatal).

dimension_verdicts: [D1=warn, D2=block, D3=warn, D4=warn, D5=warn, D6=block]

### Step 2 — Failure-condition evaluation

| ID | Sev | Quantifier | Expression | Per-dimension evaluation | Fired |
|----|-----|-----------|------------|--------------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 F, D2 F (repairable), D3 F, D6 F (repairable) → any = false | **false** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1 F, **D2 T**, D3 F, **D6 T** → any = true | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 T (n=1, owner), D2 T (n=1, owner), D3 T (n=2, both), D6 T (n=1, owner) → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 = warn → false | **false** |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1–D6 all true → any = true | **true** |
| F0 | 10 | all | every dimension scores 'pass' | D1 false (warn) → false | **false** |

### Step 3 — Precedence and emission

Fired conditions ranked by severity: F2 (90) > F3 (70) > F5 (40). Highest severity selects F2 → `editorial_decision=major_revision`.

The Devil's Advocate card's CRITICAL table is empty (headers only, zero rows), so there are no DA CRITICAL IDs to adjudicate.

fired_conditions: [F2, F3, F5]

da_critical_adjudications: []

editorial_decision=major_revision

---

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — no provenance stamp was supplied by the dispatching layer with this invocation. The **dispatch-failure fallback** therefore applies: no cross-model reviewer slot can be confirmed for any of the five seats, and this synthesis makes **no claim of model independence** across the panel. All five reviewer cards must be read as potentially originating from a single model family. Any apparent agreement between seats is correspondingly weaker evidence than independent agreement would be, and the synthesis below does not treat cross-seat convergence as independent confirmation. No cross-family aggregate and no "same-model majority" has been computed.

**Cross-model blind decision check (#518)**: not triggered — `ARS_CROSS_MODEL` is not set and the consent gate has not been passed. No behavioural change.

---

## Card-Quality Flags (flagged, not repaired)

Per the phase boundary, defects in reviewer cards are surfaced, not silently fixed:

- `[CARD-FORMAT-ANOMALY: perspective]` — the card opens with a malformed "Scoring Plan Dissent" placeholder and then self-corrects in-band ("*Wait — that placeholder is not permitted. Correcting below.*"). All six dimension scores are present and parseable; `contract_role: perspective` is declared. The seat is **usable** and was scored normally. Per the forbidden-operations list, a scoring-plan anomaly does not mint fatality.
- `[FINDING-METADATA-GAP: domain]` — the domain card's D2 block trigger ("a cited source represented as supporting a conclusion it does not support") is argued in the review body but is **not** carried as a numbered weakness block, so it has no per-finding Severity or Confidence tag. Roadmap item R3 therefore carries fallback provenance tags.
- `[NO-REPORT-LEVEL-CONFIDENCE]` — under this contract's card format no seat emits a report-level Confidence Score. Per-finding confidence is present on all numbered weaknesses and has been transported directly. Where a finding has neither (R3, R18), the row is tagged `[CONFIDENCE-SOURCE: letter-fallback]`.
- `[FIELD-ANALYSIS ITEM UNCLAIMED]` — the field analysis flagged the abstract's omission of the confidence interval. No reviewer seat raised it. It is recorded here as a panel-coverage observation only and is **not** a roadmap item; the synthesizer does not author findings.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript to *Research in Learning Technology*. It has been assessed by five reviewers: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary), and a Devil's Advocate reader.

### Decision: Major Revision

### Step 1a — Reviewer Summary Matrix

| Dimension | Journal-Fit (EIC) | R1 Methodology | R2 Domain | R3 Cross-disciplinary | DA |
|-----------|-------------------|----------------|-----------|------------------------|-----|
| Overall recommendation | *not a card field under this contract*; worst score **block** (D6) | worst **warn** (D1, D3) | worst **block** (D2) | worst **warn** (D4) | worst **warn** (D3) |
| Confidence | per-finding 4–5 | per-finding 4–5 | per-finding 3–5 | per-finding 4–5 | per-finding 3–5 |
| Key strengths | reporting completeness; claim strength stable across sections; honest abstract | uncertainty reporting verifiable; sensitivity stated as detectable effect; ethics complete; construct narrowing held; reverse pathway named | reverse-causation caution used consequentially; self-report caution acted on; quantities mutually coherent | directional agnosticism in the paper's own voice; reporting reusable for pooling; adjacent-literature caution imported | opening paragraph: no causal laundering, no circular thesis, limitations anticipated |
| Key weaknesses | → Step 1b (SC-1, SC-2, SC-3, SC-4, SC-5, SC-6, SC-7a/b, SC-8, SC-9) | → Step 1b (SC-10, SC-11, SC-5, SC-12, SC-8, SC-13, SC-14, SC-7b, SC-15, SC-16, SC-17) | → Step 1b (SC-18, SC-3, SC-19, SC-20, SC-21, SC-14, SC-22) | → Step 1b (SC-23, SC-24, SC-6, SC-25, SC-26, SC-8) | → Step 1b (SC-3, SC-27, SC-10, SC-25, SC-28, SC-7b, SC-12, SC-13, SC-14) |
| # weakness blocks | 6 | 9 | 5 | 5 | 7 MAJOR, 0 CRITICAL |
| # strength blocks | 3 | 5 | 3 | 3 | in-body |

### Step 1b — Weakness Sub-Claim Inventory (positions across the 4 non-DA seats; DA tracked separately)

| ID | Sub-claim | EIC | R1 | R2 | R3 | DA | agree/conflict (of 4) | Disposition |
|----|-----------|-----|----|----|----|----|----------------------|-------------|
| SC-1 | Reference list is editorially unverifiable (reserved 10.5555 DOI prefix; no indexed journal titles) | raised | — | — | — | — | 1 / 0 | single-reviewer |
| SC-2 | The instrument's validation warrant rests on an uncheckable source | raised | — | corroborated | — | — | 2 / 0 | corroborated |
| SC-3 | No prior effect size anywhere; the comparability contribution has no named distribution | raised | — | raised | — | corrob. (M1) | 2 / 0 | corroborated |
| SC-4 | No statement of what a reader or institution can now do differently | raised | — | — | corroborated | — | 2 / 0 | corroborated |
| SC-5 | No eligible-population denominator, therefore no response rate | raised | raised | — | — | corrob. | 2 / 0 | corroborated |
| SC-6 | No sample composition beyond year level; year-level distribution unquantified | raised | — | — | raised | — | 2 / 0 | corroborated |
| SC-7a | r² described as an adjective rather than reported (≈ .18) | raised | — | — | — | corrob. | 1 / 0 | single-reviewer |
| SC-7b | No marginal frequency distribution for the 5-category outcome; no table or figure | raised | raised | — | — | corrob. (M5) | 2 / 0 | corroborated |
| SC-8 | Adapted items not reproduced; adaptation undocumented | raised | raised | corroborated | raised | — | **4 / 0** | **[CONSENSUS-4]** |
| SC-9 | Whitfield (2019) appears only at the point where it is used | raised | — | — | — | — | 1 / 0 | single-reviewer |
| SC-10 | Common-method variance undisclosed; rival account of the *magnitude* | — | raised | — | — | corrob. (M3) | 1 / 0 | single-reviewer (owner seat, conf 5) |
| SC-11 | Coarse single-item outcome; no latent-scale estimate, no attenuation discussion | — | raised | — | — | — | 1 / 0 | single-reviewer (owner seat, conf 5) |
| SC-12 | Duplicate removal logically incompatible with the anonymity/consent claim | — | raised | — | — | corrob. (M6) | 1 / 0 | single-reviewer |
| SC-13 | α does not establish the unidimensionality the mean composite presupposes | — | raised | — | — | corrob. (M7) | 1 / 0 | single-reviewer |
| SC-14 | "Previously validated" attaches parent-instrument validation to the fielded adaptation | — | raised | raised | — | corrob. (M7) | 2 / 0 | corroborated |
| SC-15 | Power statement's status (a priori vs post hoc sensitivity) unspecified | — | raised | — | — | — | 1 / 0 | single-reviewer |
| SC-16 | No data, code, or materials availability statement | — | raised | — | — | — | 1 / 0 | single-reviewer |
| SC-17 | Robustness claim over-reads what a rank check establishes | — | raised | — | — | — | 1 / 0 | single-reviewer |
| SC-18 | Construct genealogy absent; primary definition attributed to secondary sources | — | — | raised | — | — | 1 / 0 | single-reviewer (owner seat, conf 5) |
| SC-19 | Estimand mismatch: PU→use compared against a PU→intention literature | — | — | raised | — | — | 1 / 0 | single-reviewer (owner seat, conf 5) |
| SC-20 | Mandatory-use boundary condition in a trailing clause; absent from Limitations | — | — | raised | — | — | 1 / 0 | single-reviewer (owner seat, conf 5) |
| SC-21 | Instrument's acceptance/continuance validation context unreconciled with present use | — | — | raised | — | — | 1 / 0 | single-reviewer |
| SC-22 | §5 cites two sources as warrant for a magnitude judgement they are not shown to report | — | — | raised | — | corrob. (M1) | 1 / 0 | single-reviewer (**D2 block trigger**) |
| SC-23 | "Accessed the LMS" has no recoverable referent | — | — | — | raised | — | 1 / 0 | single-reviewer (owner seat, conf 5) |
| SC-24 | The recruitment channel structurally excludes the population the implication targets | — | — | — | raised | — | 1 / 0 | single-reviewer |
| SC-25 | The practical implication is actionable only under the direction the paper disclaims | — | — | — | raised | corrob. (M4) | 1 / 0 | single-reviewer |
| SC-26 | Log absence framed as inherent rather than as a disclosed choice | — | — | — | raised | — | 1 / 0 | single-reviewer |
| SC-27 | §2's "perceived use" boundary dropped for "engagement" in Abstract and Discussion | — | **disputed** | — | — | **raised (M2)** | 0 / 1 among the 4 | **DA-origin, disputed by R1 → arbitrated** |
| SC-28 | The recruitment channel may be the LMS itself: selection on the dependent variable | — | — | — | — | **raised (M5)** | 0 / 0 among the 4 | DA-origin |

**Counting note**: the denominator is always the four non-DA seats. `not-mentioned` is silence, not agreement and not opposition. DA positions are tracked but never counted toward CONSENSUS-4/3 or SPLIT.

### Step 1c — Surface-Form Parity Check (#216)

No sub-claim's weight in this synthesis was set by phrasing. Two candidate exposures were checked explicitly:

1. **The domain card's D2 block trigger (SC-22)** is argued in flowing prose rather than in a tagged weakness block, and is the least "technical-looking" of the block drivers. Opposite-style counterfactual: written up as a numbered finding with a formal anchor, its substance is unchanged — §5 attributes a magnitude-comparability judgement to two sources the manuscript itself characterises as an instrument-development study and a moderator study. It holds against the paper text regardless of packaging. **Weight unchanged.**
2. **The perspective card's opening self-correction** is the panel's most informal moment. Under Special Situation 4 the temptation is to discount the seat. Counterfactual: the seat's four substantive findings (SC-23, SC-24, SC-25, SC-26) each carry a specific paper locator and an evaluable claim; none becomes unevaluable because of the header anomaly. **Weight unchanged; no discount applied.**

No sub-claim was credited for technical specificity in the absence of paper evidence, and no sub-claim was down-rated for informal wording. Authorship was not a weighting input.

*Epistemic status: this is a prompt-surface parity check. It records that the standard was applied; it is not evidence that the underlying model is free of a surface-form prior.*

### Points of Agreement (Consensus)

**On weaknesses:**

- **[CONSENSUS-4] SC-8** — All four non-DA reviewers require the six adapted perceived-usefulness items to be reproduced and the adaptation documented. The Journal-Fit Reviewer bands it Minor as a reproducibility gap, R1 bands it Major as an instrument-reporting failure, R2 needs it to check whether the items operationalise the field's construct, and R3 needs it to know whether "usefulness" means academic benefit, convenience, or instructor compliance. This is the panel's only unanimous weakness and it is not optional.
- **Corroborated (2 of 4, no conflict)**: SC-2, SC-3, SC-4, SC-5, SC-6, SC-7b, SC-14.

**On strengths — unanimous across all five seats, and load-bearing for this decision:**

- **Reporting completeness is above the tier norm.** The coefficient arrives with a 95% CI, an exact n, a rank-order robustness check, a detectable-effect sensitivity statement, and a complete ethics paragraph. R1 independently recomputed both numeric claims (the Fisher-z interval for r = .42 at n = 214, and r ≈ .19 as the effect detectable at .80 power) and found the arithmetic correct.
- **Causal discipline is held throughout.** Every seat, including the Devil's Advocate, records that the reverse pathway is named rather than buried and that correlational language does not drift between Results and Conclusion. The Devil's Advocate states plainly that it searched for a causal-laundering or circular-thesis failure and did not find one, which is why its CRITICAL band is empty rather than populated for form.
- **The construct was narrowed honestly and in advance.** The outcome is declared an indicator of *perceived* use before results appear.

**Do not revise these away.** Several of the changes requested below (particularly R7, R8, R14, R16) risk being over-corrected into stronger claims. The calibration is the manuscript's best property.

### Points of Disagreement

**D-1. Is the §2 "perceived use" boundary dropped in the Abstract and Discussion? (SC-27)**
*DA (M2, conf 5)*: the Abstract's terminal sentence and §5 revert to "engagement", a behavioural construct, contradicting §2's commitment. *R1 (S4, conf 5)*: the construct narrowing "is held consistently… no later section quietly upgrades it to behaviour."
**Editor's resolution — DA's fact upheld, DA's severity reduced; both seats are partly right.** Type: severity disagreement, not existence disagreement. On evidence: the Abstract does read "perceived usefulness tracks with LMS engagement," and §5 reads "factors bearing on engagement" — DA's textual observation is verified against the paper. On expertise: neither seat has priority; both are reading the same sentences. But R1's narrower claim is also verified — the *measure* is never relabelled as a behavioural count, and §3.2 and §6 hold the line. The residue is a loose noun in the two most-read sections, not claim drift. **Ruling: required as a wording repair (S4), not as a claim-integrity defect. It does not escalate any dimension score.**

**D-2. Does the measurement problem cap the maximum defensible claim, or is it fixable in revision?**
The Journal-Fit Reviewer pre-registered this as an anticipated conflict and deferred in advance: "the methodology seat may reasonably conclude that the measurement problem caps the maximum defensible claim… If that is their reading, it should govern; I have not scored around it."
**Editor's resolution — the anticipated conflict did not materialise.** R1 scored D1 `warn` and stated the reason explicitly: every defect is "either a reporting addition the authors can supply from data in hand or an interpretive qualification they can write," and none makes the result non-verifiable or the sign doubtful. The deferral is recorded because it was made in good faith and because it constrains any future re-review: if a revision reveals that the polyserial estimate or the method-variance diagnostic cannot be produced, D1's reading is the one that governs.

**D-3. Weight of the reference-integrity finding, which only one seat raised (SC-1).**
By count SC-1 is a 1-of-4 finding. Three seats are silent.
**Editor's resolution — full weight; the silence carries no evidential force against it.** Two grounds. First, `not-mentioned` is silence, never opposition. Second, the panel's review strategy assigned source verification exclusively to the Journal-Fit Reviewer and instructed the other three seats not to reach a substantive verdict on the literature base — the non-corroboration is procedurally induced, not independent. The finding carries Confidence 5 on a matter of public record (the 10.5555 range is Crossref's reserved test/demonstration prefix, not an assigned registrant), and it is the stated basis of the D6 block. Note the dependency the strategy flagged: R2's Confidence-3 caveat on W5 ("I cannot inspect the six items or the source instrument's validation evidence") and its remark that pooled estimates "do exist" are both downstream of source verifiability, not independent confirmations of it.

**D-4. Lane overlap between R1 and R3 on self-report versus logs.**
**Editor's resolution — no double-counting occurred, and none has been introduced.** R1 owns the psychometric consequence (SC-10 method variance, SC-11 coarseness and attenuation). R3 owns data availability and construct definition (SC-23 referent, SC-26 log-access disclosure). These are four distinct sub-claims with four distinct remedies; the roadmap does not merge them and does not inflate their combined severity. A single rewrite of §3.2 and §6 can nonetheless serve all four.

**D-5. Predicted scope creep did not occur.**
R2 opened by disavowing it: "I am **not** asking the authors to add constructs, mediators, or a structural model… Every repair I ask for below is a citation, framing, or interpretation repair — no new data, no new constructs." R3 likewise disavowed penalising the paper for being incremental. Recorded because it materially changes the achievability verdict below.

**Zero SPLITs.** No sub-claim drew a `disputed` position from any of the four non-DA seats. The only conflict in the panel is D-1, which is DA-versus-R1.

### Decision Rationale

The contract arithmetic returns `major_revision` via F2 (a mandatory dimension scores `block`), with F3 and F5 also firing beneath it. Two mandatory dimensions block — domain accuracy and venue fit — and both blocking seats classified the block as *repairable* rather than fatal, which is why F1 did not fire and why this is not a rejection.

The substantive picture behind that arithmetic is unusual and worth stating precisely, because it should govern how you read the length of the roadmap. The panel converged on almost nothing at the level of individual findings — one unanimous weakness, seven corroborated pairs, and twenty single-seat findings — yet every seat independently identified the same *class* of defect. The study appears to have been executed carefully and reported honestly; what it fails to do is anchor and disclose. It claims comparability without naming a single prior coefficient. It measures with an adapted instrument whose items nobody outside the author team can see and whose source cannot be located. It reports a correlation between two self-reports elicited in one sitting without saying so. It reports 233 responses without a denominator. It recommends an onboarding intervention to a population its recruitment channel structurally excluded.

None of that is a design failure and none of it requires new data. It is the gap between what the authors know and what the manuscript says — which is exactly the gap a major revision exists to close.

Two things must survive the revision unchanged: the calibration and the causal restraint. Every seat praised them, and several of the requested changes could easily be over-corrected into the claim inflation this manuscript has so far avoided.

### Achievability of the Union (explicit, per synthesis protocol)

Four seats requesting major work on four non-overlapping axes can sum to a de facto rejection nobody stated. The editor is required to rule on this rather than let arithmetic deliver it.

**Ruling: the union of requested changes is achievable with the existing 214-response dataset, with one contingency.** Sixteen of the eighteen Required items are literature work, disclosure, rewriting, or re-analysis computable from data already in hand (the Harman-type diagnostic on seven items, the polyserial estimate, the factor structure, the enrolment denominator). One item (R9's sample-composition component) may be limited by what was actually collected — report what exists and state what does not. One item is **not** a data problem and is the genuine contingency: **R1, reference integrity.** If the six cited works cannot be replaced with sources a reader can locate — including a verifiable provenance for the perceived-usefulness instrument — no amount of work on the other seventeen items makes the manuscript publishable, and the decision must be revisited on that basis alone. This is the Journal-Fit Reviewer's position and the editor adopts it.

No reviewer asked for a second site, a second wave, log-linked data, an added construct, or a structural model. This is a major revision, not a disguised rejection.

### Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Every cited source is unverifiable (reserved 10.5555 DOI prefix; no indexed journal titles), including the source carrying the study's measurement warrant | EIC (W1, Critical, conf 5) | `text: References and §3.2 "https://doi.org/10.5555/2050001" and "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"` | R1 |
| 2 | §5 attributes a quantitative comparability judgement to two sources the manuscript itself describes as an instrument-development study and a moderator study — neither is anywhere shown to report a PU–use magnitude | Domain (D2 block trigger); DA M1 corroborates | `text: §5 Discussion "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)"` | R3 |
| 3 | The stated contribution is comparability, but no prior effect size appears anywhere in the manuscript, so the claim is unfalsifiable and the contribution is undelivered | EIC (W2, Major, conf 5); Domain (W2, Major, conf 5); DA M1 | `absence: §2 and §5 comparability claim — expected a named pooled PU-use estimate from education-sector acceptance meta-analyses with its interval, and an explicit statement of where r = .42 falls relative to that interval; checked Abstract, §1, §2, §5, §7, and the six-entry reference list` | R2 |

### Required Item Details

*(Numbering follows the Required Revisions table in Part 2; R1–R18 contiguous.)*

**R1 — Replace the reference list with locatable sources, including verifiable instrument provenance.** All six DOIs use Crossref's reserved test range and no journal title resolves to an indexed periodical; the study's central methodological warrant depends on one of them.
- **Acceptance criteria**: every reference resolves to a live DOI or an equivalent locatable record, and the perceived-usefulness instrument's validation source is independently checkable by a reader.

**R2 — Name the distribution the paper claims to be one point in.** The comparability framing is the stated contribution and no prior coefficient appears anywhere.
- **Acceptance criteria**: §2 and §5 each report at least one pooled or prior PU–use estimate with its interval, and state explicitly where r = .42 falls relative to it.

**R3 — Correct the §5 attribution of the comparability judgement.** Costa & Wren (2019) and Ibarra & Poll (2021) are cited as warrant for a magnitude claim the manuscript never shows them to contain.
- **Acceptance criteria**: the "consistent with prior technology-acceptance research" claim is either supported by cited sources whose reported magnitudes are stated, or the attribution is removed.

**R4 — Supply the construct's primary theoretical sources.** §2 reproduces the field's canonical definition of perceived usefulness and attributes it, plus the "long proposed" claim, to sources dated 2019 and 2020.
- **Acceptance criteria**: the primary definitional source is cited, the "long proposed" claim is re-attributed to its origin, and the lineage the six items descend from is named.

**R5 — Restrict the comparison set to the estimand actually estimated.** The modelled path bypasses behavioural intention, which the parent theory specifies as mediator; PU→intention and PU→use estimates do not share a magnitude range.
- **Acceptance criteria**: one paragraph states why the intention step is bypassed and confines the comparison set to studies estimating the same PU-to-use link.

**R6 — Add the mandatory-use boundary condition to Limitations.** §4 concedes assessment-driven use in a trailing clause; §6 lists four limitations and omits compulsion entirely.
- **Acceptance criteria**: §6 takes an explicit position on whether compulsion bounds the finding or undermines the theoretical frame, and states the interaction with the voluntary-response limitation already listed.

**R7 — Disclose common-method variance and state the two-sided distortion.** Predictor and outcome share instrument, respondent, occasion, and response format; the threat is absent from all four limitations.
- **Acceptance criteria**: §6 acknowledges same-instrument method variance, a single-factor or marker-based diagnostic on the seven items is reported, and §5 states that .42 is an upper-bound-inclusive estimate.

**R8 — Report a latent-scale estimate and discuss attenuation.** A one-item five-category outcome has unknowable reliability and truncates the observable association; the Spearman check addresses monotonicity, not coarseness.
- **Acceptance criteria**: a polyserial or polychoric estimate is reported alongside r, and the discussion states both directions of distortion rather than treating the rank check as settling the measurement question.

**R9 — Report the denominator, the response rate, and the sample composition.** "All enrolled undergraduates were eligible" supplies a frame without a size, so 233 responses cannot be converted to a participation rate, and "spanned all four year levels" is unquantified.
- **Acceptance criteria**: the eligible-population size, the participation rate, and a year-level distribution are reported, plus whatever further composition data was collected — with an explicit statement of what was not collected.

**R10 — Reconcile duplicate removal with the anonymity and consent claims.** §3.1 removes five duplicates while §3.3 states no identifying information was collected and responses could not be linked to individuals.
- **Acceptance criteria**: the duplicate-detection mechanism is stated, and either the anonymity and consent language is amended to match it or the pattern-based criterion is specified with its false-positive risk acknowledged.

**R11 — Reproduce the adapted items and document the adaptation.** *(Unanimous — all four non-DA reviewers.)* The scale is described as adapted, but no item stems appear and the nature and extent of the adaptation are unstated.
- **Acceptance criteria**: all six item stems appear in an appendix or supplement, with an explicit statement of how the adapted wording differs from the source instrument.

**R12 — Report dimensionality evidence for the six-item composite.** α = .88 evidences internal consistency, not the unidimensionality a simple item mean presupposes, and the scale was adapted rather than administered intact.
- **Acceptance criteria**: a factor structure or item-total statistics for this sample are reported and shown to justify collapsing the six items into a single mean.

**R13 — Split the "previously validated" attribution.** The Abstract attaches the parent instrument's validation evidence to the version actually fielded.
- **Acceptance criteria**: the Abstract and §3.2 distinguish validation evidence belonging to the source instrument from evidence established in this sample.

**R14 — Define the referent of "accessed the LMS".** Background app sync, a notification tap, an email deep link, a proctored quiz window, and a study session are all "accessing the LMS"; respondents counted different subsets.
- **Acceptance criteria**: §3.2 states the intended referent — either a specified behaviour or a self-appraisal of engagement intensity — and the claim language throughout is aligned to whichever is chosen.

**R15 — State what a reader or an institution can now do differently.** "An incremental data point" describes the paper's size, not what it gives anyone.
- **Acceptance criteria**: one sentence states what changes because of this paper, and that sentence remains defensible against a moderate cross-sectional correlation.

**R16 — Repair or demote the §5 onboarding implication.** The paragraph recommends intervening on the predictor two sentences after conceding the reverse pathway is equally consistent with the data.
- **Acceptance criteria**: the directional assumption is made explicit as a stated condition of the recommendation, or the paragraph is demoted to a research agenda; the generic "suggested by, not proven by" hedge alone does not satisfy this.

**R17 — Disclose the recruitment channel's identity and address selection on the outcome.** If the course-announcement channel is the LMS under study, recruitment was conditioned on the dependent variable; and the students the onboarding implication targets are the students that channel excludes.
- **Acceptance criteria**: the manuscript states whether the announcement channel is the LMS under study, and §6 addresses coverage of the low-usefulness tail as a selection problem rather than only as an overrepresentation of levels.

**R18 — Reformat as a Research Note with one table.** Roughly 1,900 words carrying a single bivariate coefficient with no tables or figures is poorly matched to the full-article format currently occupied.
- **Acceptance criteria**: the manuscript is resubmitted in the journal's Research Note format with at least one table carrying the descriptive statistics.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. `—` marks an item with no sub-claim id (editorial directive).
>
> **Priority rule applied (stated for auditability):** P1 = any sub-claim that drives a `block` or `warn` verdict on a mandatory dimension, plus every CONSENSUS-4 item, plus any Major/Critical finding from a dimension's owner seat at confidence ≥ 4. This deviates from the default correspondence ("P1 = CONSENSUS-4/3 only") because this panel produced almost no cross-seat overlap; applying the default would have demoted the block drivers themselves to P2. The Confidence Score Weighting rule (quality of expertise over quantity of opinions) governs.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Replace the reference list with locatable sources, including verifiable instrument provenance | SC-1, SC-2 | Critical | `text: References and §3.2 "https://doi.org/10.5555/2050001" and "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"` | 5 — DOI verification is routine editorial screening; the reserved status of 10.5555 is public record | EIC | P1 | 2–5 days (or blocking) |
| R2 | Name the prior distribution and locate r = .42 within it | SC-3 | Major | `absence: §2 and §5 comparability claim — expected a named pooled PU-use estimate from education-sector acceptance meta-analyses with its interval, and an explicit statement of where r = .42 falls relative to that interval; checked Abstract, §1, §2, §5, §7, and the six-entry reference list` | 5 — reviewer has conducted meta-analytic syntheses of acceptance research | R2, EIC (+DA M1) | P1 | 2 days |
| R3 | Correct the §5 attribution of the comparability warrant | SC-22 | Major `[SEVERITY-SOURCE: letter-fallback]` | `text: §5 Discussion "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)"` | 5 `[CONFIDENCE-SOURCE: letter-fallback]` | R2 (D2 block trigger) (+DA M1) | P1 | 0.5 day |
| R4 | Supply primary theoretical sources for perceived usefulness | SC-18 | Major | `text: §2 Literature Review "Research on technology acceptance has long proposed" and "the degree to which a person believes a technology will help them perform better"` | 5 — reviewer's publishing lineage | R2 | P1 | 1 day |
| R5 | Restrict the comparison set to the PU→use estimand; justify bypassing intention | SC-19 | Major | `text: §1 Introduction "nor do we test a full acceptance model" and §5 Discussion "consistent with prior technology-acceptance research"` | 5 — estimand specification is reviewer's direct research area | R2 | P1 | 0.5 day |
| R6 | Add the mandatory-use boundary condition to Limitations | SC-20 | Major | `text: §4 Results "including course requirements and assessment schedules"` | 5 — mandatory-use boundary conditions are reviewer's specific problem | R2 | P1 | 0.5 day |
| R7 | Disclose common-method variance; state the two-sided distortion | SC-10 | Major | `absence: §6 Limitations — expected an acknowledgement of common-method variance from same-instrument, same-respondent, same-occasion measurement, plus a marker variable or Harman-type check; checked §3.2, §3.3, §3.4, §4, §5, §6` | 5 — CMV in single-instrument technology-use surveys is reviewer's primary area | R1 (+DA M3) | P1 | 1 day |
| R8 | Add a latent-scale estimate and an attenuation discussion | SC-11 | Major | `absence: §3.4 Analysis — expected a polyserial or polychoric estimate of the latent association, or an explicit attenuation bound for the one-item five-category outcome; checked §3.2, §3.4, §4, §6` | 5 — attenuation and coarse-categorisation effects are core to reviewer's teaching | R1 | P1 | 1 day |
| R9 | Report the denominator, response rate, and sample composition | SC-5, SC-6 | Major | `absence: §3.1 Design and participants — expected an eligible-population denominator and a participation or response rate; checked §3.1, §3.4, §4, §6, §7` (corroborating: `absence: §3.1 participant description — expected sample composition beyond year level; checked abstract, §3.1, §3.2, §4, §6`) | 5 (R1), 5 (EIC), 4 (R3) | R1, EIC, R3 (+DA) | P1 | 1 day |
| R10 | Reconcile duplicate removal with the anonymity and consent claims | SC-12 | Major | `text: §3.1 and §3.3 "5 duplicate entries were removed" and "responses could not be linked back to individual students"` | 4 — inference from stated procedure; a mechanism may reconcile it | R1 (+DA M6) | P1 | 0.5 day |
| R11 | **[CONSENSUS-4]** Reproduce the adapted items and document the adaptation | SC-8 | Major (R1) / Minor (EIC, R2, R3) | `absence: §3.2 Measures — expected the six perceived-usefulness item stems and a statement of how the adapted wording differs from the source instrument; checked §3.2, §3.4, §7, the reference list, and any appendix or supplementary-materials statement` | 5 (R1), 4 (EIC), 4 (R3), 3 (R2) | All four non-DA seats | P1 | 0.5 day |
| R12 | Report dimensionality evidence for the six-item composite | SC-13 | Major | `absence: §3.2 Measures — expected dimensionality evidence for the six-item adapted scale such as factor analysis or item-total statistics justifying a single mean composite; checked §3.2, §3.4, §4, and the abstract's validation claim` *(anchor transported from corroborating DA M7; raising seat is R1)* | 5 (R1), 3 (DA) | R1 (+DA M7) | P1 | 1 day |
| R13 | Split the "previously validated" attribution between source and fielded version | SC-14 | Major (R1) / Minor (R2) | `text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument"` | 5 (R1), 3 (R2) | R1, R2 (+DA M7) | P1 | 0.25 day |
| R14 | Define the referent of "accessed the LMS" and align claim language | SC-23 | Major | `text: §3.2 "a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"` | 5 — reviewer administers and reconciles these access definitions against event-log data | R3 | P1 | 0.25 day |
| R15 | State what a reader or institution can now do differently | SC-4 | Major | `text: §2 "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model."` | 5 (EIC), 4 (R3) | EIC, R3 | P1 | 0.25 day |
| R16 | Repair or demote the §5 onboarding implication | SC-25 | Major | `text: §5 "modest support for the intuition that LMS onboarding which helps students see concrete usefulness" and "may be worth institutional attention"` | 4 (R3), 3 (DA) | R3 (+DA M4) | P1 | 0.5 day |
| R17 | Disclose the recruitment channel and address selection on the outcome | SC-24, SC-28 | Major | `absence: §3.1 Design and participants and §4 Results — expected disclosure of whether the course-announcement channel is the LMS under study plus the frequency distribution across the five use categories; checked §1, §3.1, §3.4, §4, §6 limitation four` | 4 (R3), 4 (DA M5) | R3, DA | P1 | 0.5 day |
| R18 | Reformat as a Research Note with one table | — | Major `[SEVERITY-SOURCE: letter-fallback]` | `text: EIC review body — "this is a Research Note, not an Original Research article"` | 5 `[CONFIDENCE-SOURCE: letter-fallback]` | EIC (editorial directive) | P1 | 1 day |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | Report the marginal frequency distribution of the five-category use item, plus a compact descriptives table | SC-7b | Minor | `text: §3.4 "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers"` | 5 (R1), 4 (EIC) | R1, EIC (+DA M5) | P2 | 0.5 day |
| S2 | Reconcile the instrument's acceptance-versus-continuance validation context with the present operationalisation | SC-21 | Minor | `text: §3.2 Measures "adapted from Costa and Wren (2019)…" and References "Perceived usefulness and continued use of learning platforms: Instrument development and validation"` | 3 — reviewer cannot inspect the six items or the source's validation evidence | R2 | P2 | 0.5 day |
| S3 | Rewrite the robustness sentence to claim monotonic robustness specifically | SC-17 | Minor | `text: §4 "indicating that the association did not depend on the parametric assumption"` | 5 — the rank-vs-scale distinction is unambiguous | R1 | P2 | 0.25 day |
| S4 | Replace "engagement" in the Abstract and Discussion with the construct actually measured *(arbitrated — see D-1)* | SC-27 | Major (DA), arbitrated to wording repair | `text: Abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates" vs §2 "treat our self-report measure as an indicator of perceived use rather than a behavioral count"` | 5 (DA); disputed on significance by R1 (conf 5) | DA M2 (R1 dissenting) | P2 | 0.25 day |
| S5 | Disclose whether LMS log access was sought, refused, or not pursued | SC-26 | Minor | `text: §6 "LMS use was self-reported through a single item rather than measured through system logs"` | 4 — direct familiarity with LMS log-access governance | R3 | P2 | 0.25 day |
| S6 | Report r² numerically (≈ .18) rather than as an adjective | SC-7a | Minor | `text: §4 "The proportion of variance shared by the two measures was accordingly modest"` | 4 (EIC) | EIC (+DA) | P3 | 0.1 day |
| S7 | Introduce Whitfield (2019) in §2 or drop the appeal to it | SC-9 | Minor | `text: §5 "a possibility also raised in practitioner accounts of digital-environment onboarding (Whitfield, 2019)"` | 4 — structural consistency of the citation apparatus is directly observable | EIC | P3 | 0.1 day |
| S8 | State whether the power calculation is a priori or post hoc sensitivity | SC-15 | Minor | `text: §3.4 "so the design was sensitive to small-to-moderate associations"` | 4 — reporting-convention judgement | R1 | P3 | 0.1 day |
| S9 | Add a data-, code-, and materials-availability statement | SC-16 | Minor | `absence: §3.3 and §7 — expected a data-availability, code-availability, or materials-availability statement; checked §3.2, §3.3, §3.4, §5, §6, §7, References` | 5 — presence or absence is directly checkable | R1 | P3 | 0.25 day |

> Transported metadata appears on every row. Two rows (R3, R18) carry `[SEVERITY-SOURCE: letter-fallback]` and `[CONFIDENCE-SOURCE: letter-fallback]` because their findings live in a card's dimension trigger or review body rather than in a tagged weakness block; the non-standard `letter-fallback` confidence tag is used because no card under this contract emits a report-level Confidence Score to fall back to. See Card-Quality Flags.

### Revision Checklist (grouped by manuscript section)

#### Priority 1 — Structural Revisions (estimated total effort: 14–17 working days)

*References and sources — contingent gate*
- [ ] R1: Replace all six references with locatable sources; establish verifiable provenance for the perceived-usefulness instrument
- [ ] R4: Cite the primary theoretical source for perceived usefulness; re-attribute the "long proposed" claim

*§2 Literature Review and §5 Discussion — the anchoring pass*
- [ ] R2: Report at least one prior/pooled PU–use estimate with its interval; state where .42 falls
- [ ] R3: Fix or remove the attribution of the comparability judgement to Costa & Wren and Ibarra & Poll
- [ ] R5: State why behavioural intention is bypassed; confine comparisons to PU→use studies
- [ ] R15: Write the one sentence stating what changes because of this paper
- [ ] R16: Repair or demote the onboarding implication

*§3 Methods — the disclosure pass*
- [ ] R9: Report eligible-population size, participation rate, and year-level distribution (plus any further composition data; state what was not collected)
- [ ] R10: State the duplicate-detection mechanism and reconcile it with §3.3
- [ ] R11: Reproduce all six adapted item stems and document the adaptation
- [ ] R13: Distinguish source-instrument validation from evidence established in this sample
- [ ] R14: Define what counts as "accessing the LMS"
- [ ] R17: State whether the announcement channel is the LMS under study

*§3.4 / §4 / §6 — the re-analysis pass (all computable from data in hand)*
- [ ] R7: Run and report a single-factor or marker-based method-variance diagnostic; add the CMV limitation
- [ ] R8: Compute and report the polyserial/polychoric estimate; discuss attenuation in both directions
- [ ] R12: Report the factor structure or item-total statistics justifying the mean composite
- [ ] R6: Add the mandatory-use boundary condition to §6 with a bounds-vs-invalidates position

*Format*
- [ ] R18: Reformat as a Research Note with at least one descriptive table

#### Priority 2 — Content Supplementation (estimated total effort: 2 working days)
- [ ] S1: Report the use-item frequency distribution and a descriptives table
- [ ] S2: Reconcile acceptance versus continuance validation context
- [ ] S3: Restate the robustness claim as monotonic robustness only
- [ ] S4: Replace "engagement" with the measured construct in the Abstract and Discussion
- [ ] S5: Disclose the log-access position

#### Priority 3 — Text and Reporting Hygiene (estimated total effort: 0.5 working days)
- [ ] S6: Report r² numerically
- [ ] S7: Introduce or drop Whitfield (2019)
- [ ] S8: Label the power statement a priori or post hoc
- [ ] S9: Add an availability statement

### Do Not Change

- [ ] Preserve the confidence interval, exact n, sensitivity statement, and rank-order check in Results
- [ ] Preserve the explicit refusal of causal language and the named reverse pathway in §5
- [ ] Preserve the declaration that the outcome is *perceived* use (S4 corrects the noun, not the commitment)
- [ ] Do not add constructs, mediators, or a structural model — no reviewer requested one, and R2 explicitly disavowed it

### Revision Deadline

**6–8 weeks** (Major Revision). Total assessed effort is approximately 3–4 weeks of working time. Re-review by the Journal-Fit, methodology, and domain seats will follow.

**If R1 cannot be met**, contact the editorial office before beginning the other seventeen items. The remaining work is not worth doing on an unverifiable evidence base, and the decision will be revisited on that ground alone.

### Response Letter Template

Please use `templates/revision_response_template.md`. Respond to every numbered item R1–R18 and S1–S9 individually, quoting the item, stating the change made, and giving the revised location. For any item you decline, state your reasoning against the item's acceptance criterion. **R11 is unanimous across all four reviewers and is not open to declining.** S4 records a genuine disagreement between two reviewers and its arbitration; you may argue against the arbitration on evidence.

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary
- Scored: D5 warn, D6 **block** (repairable) | Per-finding confidence 4–5
- Key point: the craft is above tier and the calibration is not the problem — but correct calibration is being asked to function as a contribution, and neither the comparison nor the comparators can be established as submitted. Recommends reclassification as a Research Note.

### Reviewer 1 (Methodology) Summary
- Scored: D1 warn, D3 warn | Per-finding confidence 4–5
- Key point: nothing in the reported arithmetic is wrong (both numeric claims independently recomputed); the rigor problem is entirely in what is left undiscussed about the two variables being correlated — undisclosed method variance pushing the estimate up, unquantified attenuation pushing it down.

### Reviewer 2 (Domain) Summary
- Scored: D2 **block** (repairable) | Per-finding confidence 3–5
- Key point: the dataset and analysis survive intact; the interpretive claim that carries the paper does not. Needs primary-source grounding, a named comparison distribution, an estimand caveat, and an honest voluntariness limitation — all citation and framing repairs, no new data.

### Reviewer 3 (Cross-disciplinary) Summary
- Scored: D4 warn | Per-finding confidence 4–5
- Key point: the paper does not overclaim in kind, it underspecifies in degree, at exactly the two points an institutional reader needs — the outcome has no recoverable referent, and the population the implication targets is the population the recruitment channel excludes.

### Devil's Advocate Summary
- Scored: D3 warn | 0 CRITICAL, 7 MAJOR | Per-finding confidence 3–5
- Key point: searched for the failure modes that would justify a block or fatal reading — a headline claim contradicted by the paper's own numbers, a smuggled mechanistic inference, a circular thesis — and did not find them. The CRITICAL band is empty by finding, not by omission. Strongest available objection is that both variables are self-reports elicited in one sitting and the paper never asks whether common method inflates the coefficient.

---

## Schema 7 — Machine-Form Roadmap

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "major_revision",
  "selected_condition": "F2",
  "items": [
    {"id": "R1", "priority": "P1", "bucket": "must_fix", "verification_criteria": "Every reference resolves to a live DOI or equivalent locatable record, and the perceived-usefulness instrument's validation source is independently checkable by a reader.", "reviewer": ["eic"], "sub_claims": ["SC-1", "SC-2"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: References and §3.2 \"https://doi.org/10.5555/2050001\" and \"a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": "D6", "contingency": true},
    {"id": "R2", "priority": "P1", "bucket": "must_fix", "verification_criteria": "§2 and §5 each report at least one pooled or prior PU-use estimate with its interval, and state explicitly where r = .42 falls relative to it.", "reviewer": ["domain", "eic"], "sub_claims": ["SC-3"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §2 and §5 comparability claim - expected a named pooled PU-use estimate from education-sector acceptance meta-analyses with its interval, and an explicit statement of where r = .42 falls relative to that interval; checked Abstract, §1, §2, §5, §7, and the six-entry reference list", "source_kind": "reviewer_finding", "consensus": "corroborated", "blocking_dimension": ["D2", "D6"]},
    {"id": "R3", "priority": "P1", "bucket": "must_fix", "verification_criteria": "The \"consistent with prior technology-acceptance research\" claim is either supported by cited sources whose reported magnitudes are stated, or the attribution is removed.", "reviewer": ["domain"], "sub_claims": ["SC-22"], "severity": "major", "severity_source": "letter-fallback", "confidence": 5, "confidence_source": "letter-fallback", "evidence_anchor": "text: §5 Discussion \"consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": "D2"},
    {"id": "R4", "priority": "P1", "bucket": "must_fix", "verification_criteria": "The primary definitional source is cited, the \"long proposed\" claim is re-attributed to its origin, and the lineage the six items descend from is named.", "reviewer": ["domain"], "sub_claims": ["SC-18"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §2 Literature Review \"Research on technology acceptance has long proposed\" and \"the degree to which a person believes a technology will help them perform better\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": "D2"},
    {"id": "R5", "priority": "P1", "bucket": "must_fix", "verification_criteria": "One paragraph states why the intention step is bypassed and confines the comparison set to studies estimating the same PU-to-use link.", "reviewer": ["domain"], "sub_claims": ["SC-19"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §1 Introduction \"nor do we test a full acceptance model\" and §5 Discussion \"consistent with prior technology-acceptance research\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": "D2"},
    {"id": "R6", "priority": "P1", "bucket": "must_fix", "verification_criteria": "§6 takes an explicit position on whether compulsion bounds the finding or undermines the theoretical frame, and states the interaction with the voluntary-response limitation already listed.", "reviewer": ["domain"], "sub_claims": ["SC-20"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §4 Results \"including course requirements and assessment schedules\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": "D2"},
    {"id": "R7", "priority": "P1", "bucket": "must_fix", "verification_criteria": "§6 acknowledges same-instrument method variance, a single-factor or marker-based diagnostic on the seven items is reported, and §5 states that .42 is an upper-bound-inclusive estimate.", "reviewer": ["methodology", "da"], "sub_claims": ["SC-10"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §6 Limitations - expected an acknowledgement of common-method variance from same-instrument, same-respondent, same-occasion measurement, plus a marker variable or Harman-type check; checked §3.2, §3.3, §3.4, §4, §5, §6", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": ["D1", "D3"]},
    {"id": "R8", "priority": "P1", "bucket": "must_fix", "verification_criteria": "A polyserial or polychoric estimate is reported alongside r, and the discussion states both directions of distortion rather than treating the rank check as settling the measurement question.", "reviewer": ["methodology"], "sub_claims": ["SC-11"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.4 Analysis - expected a polyserial or polychoric estimate of the latent association, or an explicit attenuation bound for the one-item five-category outcome; checked §3.2, §3.4, §4, §6", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": "D1"},
    {"id": "R9", "priority": "P1", "bucket": "must_fix", "verification_criteria": "The eligible-population size, the participation rate, and a year-level distribution are reported, plus whatever further composition data was collected, with an explicit statement of what was not collected.", "reviewer": ["methodology", "eic", "perspective"], "sub_claims": ["SC-5", "SC-6"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.1 Design and participants - expected an eligible-population denominator and a participation or response rate; checked §3.1, §3.4, §4, §6, §7", "source_kind": "reviewer_finding", "consensus": "corroborated", "blocking_dimension": ["D1", "D6"]},
    {"id": "R10", "priority": "P1", "bucket": "must_fix", "verification_criteria": "The duplicate-detection mechanism is stated, and either the anonymity and consent language is amended to match it or the pattern-based criterion is specified with its false-positive risk acknowledged.", "reviewer": ["methodology", "da"], "sub_claims": ["SC-12"], "severity": "major", "confidence": 4, "evidence_anchor": "text: §3.1 and §3.3 \"5 duplicate entries were removed\" and \"responses could not be linked back to individual students\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": "D1"},
    {"id": "R11", "priority": "P1", "bucket": "must_fix", "verification_criteria": "All six item stems appear in an appendix or supplement, with an explicit statement of how the adapted wording differs from the source instrument.", "reviewer": ["eic", "methodology", "domain", "perspective"], "sub_claims": ["SC-8"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.2 Measures - expected the six perceived-usefulness item stems and a statement of how the adapted wording differs from the source instrument; checked §3.2, §3.4, §7, the reference list, and any appendix or supplementary-materials statement", "source_kind": "reviewer_finding", "consensus": "CONSENSUS-4", "blocking_dimension": "D1"},
    {"id": "R12", "priority": "P1", "bucket": "must_fix", "verification_criteria": "A factor structure or item-total statistics for this sample are reported and shown to justify collapsing the six items into a single mean.", "reviewer": ["methodology", "da"], "sub_claims": ["SC-13"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.2 Measures - expected dimensionality evidence for the six-item adapted scale such as factor analysis or item-total statistics justifying a single mean composite; checked §3.2, §3.4, §4, and the abstract's validation claim", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": "D1"},
    {"id": "R13", "priority": "P1", "bucket": "must_fix", "verification_criteria": "The Abstract and §3.2 distinguish validation evidence belonging to the source instrument from evidence established in this sample.", "reviewer": ["methodology", "domain", "da"], "sub_claims": ["SC-14"], "severity": "major", "confidence": 5, "evidence_anchor": "text: Abstract \"Perceived usefulness was measured with an adapted, previously validated instrument\"", "source_kind": "reviewer_finding", "consensus": "corroborated", "blocking_dimension": "D1"},
    {"id": "R14", "priority": "P1", "bucket": "must_fix", "verification_criteria": "§3.2 states the intended referent - either a specified behaviour or a self-appraisal of engagement intensity - and the claim language throughout is aligned to whichever is chosen.", "reviewer": ["perspective"], "sub_claims": ["SC-23"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.2 \"a single five-point frequency item asking how often the respondent accessed the LMS in a typical week\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": "D4"},
    {"id": "R15", "priority": "P1", "bucket": "must_fix", "verification_criteria": "One sentence states what changes because of this paper, and that sentence remains defensible against a moderate cross-sectional correlation.", "reviewer": ["eic", "perspective"], "sub_claims": ["SC-4"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §2 \"It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model.\"", "source_kind": "reviewer_finding", "consensus": "corroborated", "blocking_dimension": "D6"},
    {"id": "R16", "priority": "P1", "bucket": "must_fix", "verification_criteria": "The directional assumption is made explicit as a stated condition of the recommendation, or the paragraph is demoted to a research agenda; the generic hedge alone does not satisfy this.", "reviewer": ["perspective", "da"], "sub_claims": ["SC-25"], "severity": "major", "confidence": 4, "evidence_anchor": "text: §5 \"modest support for the intuition that LMS onboarding which helps students see concrete usefulness\" and \"may be worth institutional attention\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": ["D3", "D4"]},
    {"id": "R17", "priority": "P1", "bucket": "must_fix", "verification_criteria": "The manuscript states whether the announcement channel is the LMS under study, and §6 addresses coverage of the low-usefulness tail as a selection problem rather than only as an overrepresentation of levels.", "reviewer": ["perspective", "da"], "sub_claims": ["SC-24", "SC-28"], "severity": "major", "confidence": 4, "evidence_anchor": "absence: §3.1 Design and participants and §4 Results - expected disclosure of whether the course-announcement channel is the LMS under study plus the frequency distribution across the five use categories; checked §1, §3.1, §3.4, §4, §6 limitation four", "source_kind": "reviewer_finding", "consensus": "single-reviewer", "blocking_dimension": ["D3", "D4"]},
    {"id": "R18", "priority": "P1", "bucket": "must_fix", "verification_criteria": "The manuscript is resubmitted in the journal's Research Note format with at least one table carrying the descriptive statistics.", "reviewer": ["eic"], "sub_claims": [], "severity": "major", "severity_source": "letter-fallback", "confidence": 5, "confidence_source": "letter-fallback", "evidence_anchor": "text: EIC review body - \"this is a Research Note, not an Original Research article\"", "source_kind": "editorial", "consensus": "n/a", "blocking_dimension": ["D5", "D6"]},
    {"id": "S1", "priority": "P2", "bucket": "should_fix", "verification_criteria": "A category-frequency table for the five-point use item and a compact descriptives table are present.", "reviewer": ["methodology", "eic", "da"], "sub_claims": ["SC-7b"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §3.4 \"Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers\"", "source_kind": "reviewer_finding", "consensus": "corroborated"},
    {"id": "S2", "priority": "P2", "bucket": "should_fix", "verification_criteria": "A short paragraph reconciles the source instrument's continuance-validation context with the present acceptance-mixed sample and operationalisation.", "reviewer": ["domain"], "sub_claims": ["SC-21"], "severity": "minor", "confidence": 3, "evidence_anchor": "text: §3.2 Measures \"adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency\" and References \"Perceived usefulness and continued use of learning platforms: Instrument development and validation\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer"},
    {"id": "S3", "priority": "P2", "bucket": "should_fix", "verification_criteria": "The Results sentence claims monotonic robustness specifically and no longer claims independence from the parametric assumption in general.", "reviewer": ["methodology"], "sub_claims": ["SC-17"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §4 \"indicating that the association did not depend on the parametric assumption\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer"},
    {"id": "S4", "priority": "P2", "bucket": "should_fix", "verification_criteria": "The Abstract's terminal sentence and §5 name the construct actually measured rather than \"engagement\".", "reviewer": ["da"], "sub_claims": ["SC-27"], "severity": "major", "confidence": 5, "evidence_anchor": "text: Abstract \"The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates\" vs §2 \"treat our self-report measure as an indicator of perceived use rather than a behavioral count\"", "source_kind": "reviewer_finding", "consensus": "arbitrated-disagreement", "arbitration": "D-1: DA fact upheld, severity reduced to wording repair; R1 dissent recorded"},
    {"id": "S5", "priority": "P2", "bucket": "should_fix", "verification_criteria": "One sentence states whether log access was sought and refused, precluded by the ethics approval, or not pursued.", "reviewer": ["perspective"], "sub_claims": ["SC-26"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §6 \"LMS use was self-reported through a single item rather than measured through system logs\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer"},
    {"id": "S6", "priority": "P3", "bucket": "nice_to_fix", "verification_criteria": "§4 reports the numeric proportion of shared variance instead of the adjective.", "reviewer": ["eic", "da"], "sub_claims": ["SC-7a"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §4 \"The proportion of variance shared by the two measures was accordingly modest\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer"},
    {"id": "S7", "priority": "P3", "bucket": "nice_to_fix", "verification_criteria": "Whitfield (2019) is introduced in §2 or the appeal to it in §5 is removed.", "reviewer": ["eic"], "sub_claims": ["SC-9"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §5 \"a possibility also raised in practitioner accounts of digital-environment onboarding (Whitfield, 2019)\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer"},
    {"id": "S8", "priority": "P3", "bucket": "nice_to_fix", "verification_criteria": "§3.4 states whether the calculation is a priori or post hoc sensitivity, giving the assumed effect size if a target n was set in advance.", "reviewer": ["methodology"], "sub_claims": ["SC-15"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §3.4 \"so the design was sensitive to small-to-moderate associations\"", "source_kind": "reviewer_finding", "consensus": "single-reviewer"},
    {"id": "S9", "priority": "P3", "bucket": "nice_to_fix", "verification_criteria": "A data-, code-, and materials-availability statement is present.", "reviewer": ["methodology"], "sub_claims": ["SC-16"], "severity": "minor", "confidence": 5, "evidence_anchor": "absence: §3.3 and §7 - expected a data-availability, code-availability, or materials-availability statement; checked §3.2, §3.3, §3.4, §5, §6, §7, References", "source_kind": "reviewer_finding", "consensus": "single-reviewer"}
  ]
}
```

---

## Quality Gates

- [x] All five reviewer cards fully read and cited
- [x] Consensus and disagreement identified and labelled per sub-claim (one CONSENSUS-4, seven corroborated pairs, twenty single-reviewer, zero SPLITs, one arbitrated DA-vs-R1 conflict)
- [x] Every disagreement carries an arbitration result and rationale (D-1 through D-5)
- [x] Decision consistent with reviewer scores and derived mechanically from the contract
- [x] Every roadmap item traceable to a specific reviewer finding; no synthesizer-authored findings
- [x] Severity and confidence transported from cards, with fallback tags where the card lacked them
- [x] Roadmap compatible with `academic-paper` revision-mode input; Schema 7 machine-form emitted
- [x] Ordinal contract satisfied: R1–R18 contiguous, one acceptance-criteria bullet per block, order matches the Required table
- [x] Achievability of the union ruled on explicitly rather than left to arithmetic
- [x] Panel provenance stated without implying independence that was not established
