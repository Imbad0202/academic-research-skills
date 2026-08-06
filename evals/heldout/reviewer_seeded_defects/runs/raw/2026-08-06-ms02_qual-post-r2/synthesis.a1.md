# Editorial Synthesis — Sprint Contract `reviewer/reviewer_full/v2`

## Mechanical Audit (v3.6.2 Sprint Contract Synthesizer Protocol)

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats | Ineligible / not_assessed (excluded) | Verdict |
|-----|----------|----------------|--------------------------|--------------------------------------|---------|
| D1 | mandatory | methodology | methodology = `block` (repairable) | eic, domain, perspective, da → `not_assessed` | **block** |
| D2 | mandatory | domain | domain = `block` (repairable) | eic, methodology, perspective, da → `not_assessed` | **block** |
| D3 | mandatory | da, methodology | da = `block` (repairable); methodology = `block` (repairable) | eic, domain, perspective → `not_assessed` | **block** |
| D4 | high | perspective | perspective = `block` | eic, methodology, domain, da → `not_assessed` | **block** |
| D5 | normal | eic | eic = `block` | methodology, domain, perspective, da → `not_assessed` | **block** |
| D6 | mandatory | eic | eic = `block` (repairable) | methodology, domain, perspective, da → `not_assessed` | **block** |

`audit_verdict: block` — worst assessed eligible score across all six dimensions. **No fatality was minted by any seat**: the methodology seat's scoring-plan dissent narrowed its own D1 fatal trigger and scored repairable; the domain seat stated its D2 block "does not bind to `what_triggers_fatal`"; the DA seat considered `fatal` on D3 and rejected it; the EIC seat marked D6 `repairable` and D5 sits on a normal-priority dimension where fatal scope is not valid. Every dimension had ≥1 assessed eligible seat, so no `[DIMENSION-UNASSESSED]` abort.

### Step 2 — Failure-condition evaluation

| Cond | Sev | Cross-reviewer quantifier | Per-dimension result | Dimension quantifier | Fired |
|------|-----|---------------------------|----------------------|----------------------|-------|
| F1 | 95 | any | no fatal block on D1, D2, D3, D6 | any | **false** |
| F2 | 90 | any | D1 ✓, D2 ✓, D3 ✓ (both eligible seats), D6 ✓ | any | **true** |
| F3 | 70 | majority | D1 (n=1 → owner methodology) ✓; D2 (n=1 → owner domain) ✓; D3 (n=2 → both seats) ✓; D6 (n=1 → owner eic) ✓ | two or more | **true** |
| F4 | 60 | any | D4 (high) ✓ | any | **true** |
| F5 | 40 | any | all six dimensions ✓ | any | **true** |
| F0 | 10 | all | no dimension scores `pass` | every | **false** |

### Step 3 — Precedence and emission

Highest severity among fired conditions: **F2 (90)** → `editorial_decision=major_revision`.

```
dimension_verdicts: [D1=block, D2=block, D3=block, D4=block, D5=block, D6=block]
fired_conditions: [F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED, C5=VALIDATED]
editorial_decision=major_revision
```

No `[DA-CRITICAL-VS-ACCEPT]` marker: the mechanical decision is not `accept`. No `C<n>=REJECTED` rows, so no rejection-rationale lines are due. Step 4b (cross-model blind decision check) is not active — `ARS_CROSS_MODEL` was not supplied and no consent gate was passed; no behavioural change.

### Card-hygiene flags (flagged, not fixed — Phase Boundary)

- The `perspective` card's Scoring Plan Dissent slot contains residual meta-text ("Actually, per protocol I omit the section entirely."), and the `da` card's contains "Wait — that placeholder is not permitted. Removing it." Neither affects any score, trigger, or finding; both cards are otherwise complete (contract_role present, all six dimensions dispositioned, per-finding severity and confidence present). Recorded for the reviewer-side owner; not repaired here.
- These cards carry dimension scores rather than an overall recommendation or a report-level Confidence Score. The Step 1a matrix and the Part 3 appendix substitute assessed-dimension verdicts for those template rows; the substitution is noted where it occurs.

---

# Editorial Decision Package

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled "Building Institutional Quality Culture: Administrator Perspectives on Quality Assurance Implementation in Universities" to *Quality in Higher Education* [configured venue taken from the field analysis; not a contract field]. Your manuscript has been assessed by five reviewer seats: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary perspective), and a devil's-advocate reviewer.

### Decision: Major Revision

The decision follows the contract arithmetic above: four mandatory dimensions (D1 methodology rigour, D2 domain accuracy, D3 argumentative coherence, D6 venue fit and contribution), the high-priority D4, and the normal-priority D5 all scored `block`. No seat declared a fatal block, so F1 did not fire and rejection is not the arithmetic outcome; F2 fired at severity 90 and selects major revision.

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — no provenance stamp was supplied by the dispatching layer for this `reviewer_full` round. The block is emitted rather than omitted, and no statement is inferred in its place: I cannot state which model family ran which seat, and I therefore make **no claim of model independence across the five seats**. No cross-family aggregate and no "same-model majority" has been computed. The dispatching layer should supply the stamp before this letter is released to the author.

### Consensus Analysis

Consensus is computed per sub-claim over the four non-DA seats (Journal-Fit Reviewer, R1 methodology, R2 domain, R3 perspective); the denominator is always 4, and silence is neither agreement nor opposition. The full inventory is in Appendix B. **No sub-claim drew a `disputed` position from any seat, so there are zero formal SPLITs and no binding Journal-Fit Reviewer arbitration was triggered.** The severity variations and the one scoping tension are recorded below as arbitration records, not as splits.

#### Points of Agreement (Consensus)

- **[CONSENSUS-4]** (SC-2) The interview sample size is irreconcilable: the abstract reports fourteen administrators, §3.2 reports twelve with an explicit `(n=12)`. All four seats raise it; the DA corroborates (M1).
- **[CONSENSUS-4]** (SC-3) §4.3's claim of "balanced representation… the full range of administrator views" is contradicted two sentences later by the disclosure that dissenting participants were excluded. All four seats; DA C3.
- **[CONSENSUS-4]** (SC-4) §3.5's anonymisation guarantee is defeated by §4.1's attributions to "the quality director of the largest private university in the region" and "the associate dean for quality at the public research university" — singular role-holders in a design with exactly one private and one public research university. All four seats; DA C5.
- **[CONSENSUS-4]** (SC-5) §5 attributes to Delacroix (2018) the inverse of the position §2 and the reference annotation correctly report. All four seats; DA C1.
- **[CONSENSUS-4]** (SC-6) §5's escalation to "universities across the sector," "the higher education sector as a whole," and "administrators everywhere," with the verb "demonstrate," exceeds what three institutions in one unnamed system can license. All four seats; DA C2.
- **[CONSENSUS-4]** (SC-7) §6's "first comprehensive account" priority claim is contradicted by the manuscript's own §2, which calls Pettersen (2022) and Rahman (2020) "closest in spirit to the present study." All four seats; DA M5.
- **[CONSENSUS-3]** (SC-3b) The exclusion is an analytic-validity failure requiring re-analysis, not merely withdrawal of the representativeness claim. R1, R2, R3 agree; **silent: Journal-Fit Reviewer**, who explicitly recorded the contradiction and deferred the analytic consequence.
- **[CONSENSUS-3]** (SC-4b) The consent basis for attributable role-level quotation must be documented and §3.5 re-checked against the reported text. R1, R2, R3 agree; **silent: Journal-Fit Reviewer**, who required redaction but did not raise consent documentation.
- **[CONSENSUS-3]** (SC-12) The survey instrument is undocumented — no range, anchors, item set, provenance, reliability, or dimensionality evidence for a score carried into the abstract. Journal-Fit Reviewer, R1, R2 agree; **silent: R3**.
- **[CONSENSUS-3]** (SC-15) The national system, QA regime, and accreditor are withheld, leaving "external QA requirements" without a referent. Journal-Fit Reviewer, R2, R3 agree; **silent: R1**.
- **[CONSENSUS-3]** (SC-17) §4.1's "structured protocol" contradicts the semi-structured design of §3.1/§3.3 and does not license the inference that the pattern is "not an artifact of any single institution's local circumstances." R1, R2, R3 agree; **silent: Journal-Fit Reviewer**. DA M3.
- **[CONSENSUS-3]** (SC-22b) A participant characteristics table is required for both strands (per-site n, role, tenure, response rate). Journal-Fit Reviewer, R1, R2 agree; **silent: R3**.

Corroborated (2/4) and single-reviewer (1/4) findings are below the consensus bar and are prioritised by transported confidence, not by headcount. They include the entire reference list's non-resolving DOIs (SC-1, Journal-Fit Reviewer alone, Critical, confidence 5), the unauditable thematic-analysis procedure (SC-10, R1 + Journal-Fit Reviewer, Critical/Major, confidence 5/4), the unreportable significance claim (SC-13, R1 alone, Major, confidence 5), the undefined core construct (SC-16, R2 alone, Major, confidence 5), and the unattributed neo-institutional vocabulary (SC-9, R3 alone, Major, confidence 5). Each of these is either the named trigger of a dimension block or carries confidence 5 from the seat that owns the dimension, so each is Required despite the low headcount. Appendix B gives the full disposition.

#### Points of Disagreement

- **Severity of §4.1's "structured protocol" defect (SC-17)**: R1 transports Major; R2 and R3 transport Minor.
  - **Editor's Resolution**: Major stands. Both R2 and R3 explicitly ceded the inferential consequence to the methodology seat ("the methodology seat owns the inferential consequence"; "correctable by rewording without disturbing the findings"). This is deference, not dissent, so the counting rule records no `disputed` position and no SPLIT. Expertise-first arbitration assigns the warrant question to R1.
- **Severity of the mixed-methods integration defect (SC-18)**: R1 transports Major (no stated point of integration, no joint display); R3 transports Minor (framing of §4.4 as corroboration).
  - **Editor's Resolution**: Adopt the union at Major. The two seats address different scopes — absence of integration versus mislabelling of divergence — and R3 deferred statistical adequacy. Priority is P2 under either band, so the resolution is recorded for accuracy rather than to move the item.
- **Is "quality culture" adequately defined?** R3 (S3) records that core constructs are glossed on first use and that accessibility is not the problem; R2 (W4) records that the construct is never defined or operationalised and that the central argument is consequently not falsifiable.
  - **Editor's Resolution**: Not a conflict. R3 assesses accessibility for adjacent-field readers and its own D4 statement separates accessibility from substantiation; R2 assesses operationalisation against the field's typologies and the scalar survey measure. Both hold. The requirement placed on the author is operationalisation (R2's dimension), not further glossing.
- **Where does the contribution live?** R3 argues the three themes are already modelled by neo-institutional decoupling and audit-society theory, so the contribution claim cannot be evaluated until that tradition is engaged; the Journal-Fit Reviewer and R2 argue the administrator-level empirical account is genuinely thin in the QA literature and is the paper's surviving asset.
  - **Editor's Resolution**: Both are correct and neither seat took a `disputed` position, so this is not an arbitrated SPLIT. It is passed to the author as a **scoping decision**, not averaged into "engage more literature": reposition the paper as a contribution to QA studies that engages organisation theory and states what the administrator hinge adds to decoupling accounts — most plausibly the meaning-recovery mechanism in §4.3 — rather than as a general theory claim. R3 itself flags its own pull toward organisation theory as a bias and defers the disciplinary home to the Journal-Fit and domain seats.
- **Non-material severity variation across seats**: SC-2 (Critical R1 / Major three seats), SC-3 and SC-4 (Critical R1, R3 / Major Journal-Fit, R2), SC-5 (Critical R2 / Major three seats).
  - **Editor's Resolution**: No arbitration required. In each case every seat prescribes the same remedy and every transported band sits above the acceptance-blocking threshold, so the difference does not change the item's priority. The roadmap transports both bands with attribution rather than collapsing them to one number.
- **Fatality**: three seats considered fatal scope and declined it (R1 by narrowing its own D1 trigger, the domain seat by declaring non-binding, the DA by explicit rejection).
  - **Editor's Resolution**: Recorded, not overridden. No fatal block exists on the record, F1 did not fire, and I have not minted fatality at the synthesis layer.

### Devil's-Advocate CRITICAL adjudications

Each DA-CRITICAL is adjudicated and visible; none functions as an automatic veto. The mechanical decision is already major revision, so no adjudication changes it.

| ID | DA argument | Corroborated by | Adjudication | Required author response |
|----|-------------|-----------------|--------------|--------------------------|
| C1 | §5's inverted Delacroix is the sole citational support for the paper's only practical recommendation | Journal-Fit W8, R1 W12, R2 W1, R3 W3 | **VALIDATED** — Journal-Fit Reviewer records that "one of these is wrong, and the discussion's central practical recommendation currently rests on the reversal"; the domain seat, who owns D2, blocked on exactly this trigger | Correct the attribution (R7) **and** rebuild the recommendation without the inverted warrant (R8) |
| C2 | Sector-wide generalisation from three institutions, self-refuted by §6's call for future testing across systems | R1 W10, R2 W3, R3 W6; Journal-Fit corroborates in the letter body | **VALIDATED** — the §5/§6 contradiction is verifiable on the page; the Journal-Fit Reviewer flagged the leap while deferring the D3 score to this seat | Delete the sector claim and reduce to the sampling frame (R9); reconcile §5 with §6 |
| C3 | The three-theme structure is both the admission criterion and the finding, so it is immunised against disconfirmation | Journal-Fit W10, R1 W2, R2 W10, R3 W5 | **VALIDATED** — R1's D1 block and D3 block both name the exclusion as a driver | Withdraw the representativeness claim (R5) and reinstate the dissenting accounts for analysis (R6); reconcile the 14/12 gap against the exclusion (R2) |
| C4 | Prospective efficacy claim ("more likely to foster the internalized commitment") with no design variation and no outcome measure | Not raised as a banded finding by any non-DA seat; adjacent support from R3 W8 (recommendation unactionable) | **VALIDATED** — adjudicated on editorial text-check, not on a Journal-Fit position, which is absent from the record: §3 varies no QA process feature and measures no commitment outcome, R1 confirms the survey is a single-time-point perception measure with no documented instrument, and no seat disputes the claim | Delete the efficacy claim in §6 and the abstract's design implications, or supply design variation with outcomes and an identification argument (R11) |
| C5 | The ethics statement asserts non-identifiability while Findings identify unique role-holders | Journal-Fit W5, R1 W4, R2 W9, R3 W1 | **VALIDATED** — R1 and R3 both rate it Critical and both state that publication in this form is not possible | Redact the descriptors (R3) and document the consent basis and ethics-committee scope (R4) |

### Decision Rationale

The arithmetic is unambiguous and the substance behind it is consistent across seats. Four mandatory dimensions blocked, each with a distinct named trigger: the qualitative analysis is not recoverable as a procedure (D1), a load-bearing source is reported in two contradictory senses (D2), the Discussion and Conclusion draw sector-wide and prospective-efficacy claims the design cannot license (D3), and the §6 priority claim is asserted without positioning against work in the manuscript's own bibliography (D6). D4 blocked on unattributed borrowed theory, and D5 on a reference apparatus in which no cited source can be located through the identifier supplied. Every seat that considered fatality declined it, and each block was marked or argued as repairable, so rejection is not on the table: the interview corpus apparently still exists, the excluded accounts can be reinstated, and the correct reading of Delacroix is already present in §2.

What makes this a substantial major revision rather than a long list of corrections is that four defects are integrity-class and three of the four are internal contradictions the manuscript states against itself: two sample sizes for one study, a full-range representation claim beside a disclosed exclusion, an anonymisation guarantee beside identifying descriptors, and a source read correctly in §2 and reversed in §5. Repairing them requires re-analysis and re-reporting, not hedging. One item is procedurally prior to everything else and is not competing for a blocking-issue slot: all twelve DOIs sit on the reserved, non-resolving `10.5555/` prefix with sequential suffixes, so the literature review cannot currently be verified at all. The Journal-Fit Reviewer asks that resolvable identifiers be obtained from the authors before further reviewer time is spent, and I endorse that as a condition on re-review (R1). Ranked fourth on the blocking list, and excluded only by the three-row cap below, is the Delacroix reversal — the named trigger of the D2 mandatory block, addressed by R7 and R8.

I note honestly that much of the required work is addition rather than correction: methods detail, a participant table, per-theme counts, an instrument appendix, an operational definition of the headline construct, canon engagement, and context disclosure. At roughly 1,850 body words with no table or figure, the manuscript is well short of a full research article for this venue, and the author faces a genuine scoping choice at the outset — deepen to full-article depth, or reposition as a research note. That choice materially changes the revision timetable, so it should be made first.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | All twelve references carry non-resolving `10.5555/` placeholder DOIs with sequential suffixes, so no cited source can be located and the literature review cannot be verified | EIC (W1) | text: References, Aoki (2019) and Silva & Tan (2021) "https://doi.org/10.5555/1042001" "https://doi.org/10.5555/1042012" | R1 |
| 2 | §3.5's anonymisation guarantee is defeated by §4.1's attributions to unique role-holders, who are quoted criticising their own institutions | EIC (W5), R1 (W4), R2 (W9), R3 (W1), DA (C5) | text: §3.5 "all data were fully anonymized prior to analysis so that no individual could be identified" and §4.1 "the quality director of the largest private university in the region" | R3, R4 |
| 3 | Dissenting participants were excluded because they "fell outside the three-theme structure," making the primary qualitative finding unfalsifiable as reported and the adjacent full-range claim false | R1 (W2), R3 (W5), EIC (W10), R2 (W10), DA (C3) | text: §4.3 "the study achieved balanced representation of perspectives, capturing the full range of administrator views" and "these were excluded for space, as they fell outside the three-theme structure" | R5, R6 |

### Surface-Form Parity Check (#216)

All five cards are written in formal, technically specific register, so no sub-claim's weight turned on informal or vague phrasing. I ran the opposite-style counterfactual on the two places where phrasing could have moved a weight: (a) the single-reviewer findings at Required priority (SC-1, SC-9, SC-13, SC-16) were weighted on transported confidence 5 from the seat that owns the relevant dimension and on paper-side verifiability, not on how precisely they were worded; (b) the residual meta-text in the perspective and DA cards was excluded from weighting entirely rather than treated as a quality signal against those seats' findings. No sub-claim was marked unevaluable. Authorship was not a weighting input.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Appendix B `sub_claim_id`(s) each item traces to. A DA-CRITICAL item with no sub-claim id uses `—`.
>
> **Priority rule applied here**: P1 = any sub-claim that is either (a) a CONSENSUS-4/CONSENSUS-3 acceptance-blocking issue, or (b) a named trigger of a dimension `block` in the audit matrix above. Rule (b) is why four items below sit at P1 on 1/4 or 2/4 headcount — they are the stated drivers of D1, D2, D4, or D5, so the manuscript cannot clear those dimensions without them. Every such case is labelled.
>
> **Ordinal contract (#576 §5.1)**: the `### Required Item Details` blocks below are numbered `R<n>` in this table's order and form the contiguous sequence R1..R23.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Supply resolvable identifiers for all twelve references before re-review | SC-1 | Critical (EIC) | text: References, Aoki (2019) / Silva & Tan (2021) `10.5555/1042001`–`10.5555/1042012` | 5 — designated handler for this venue's publication-ethics queries | EIC | P1 (D5 block driver; procedural gate) | 1 day |
| R2 | Reconcile the interview N to a single figure and report any withdrawal or exclusion with its reason | SC-2 | Critical (R1) / Major (EIC, R2, R3) | text: Abstract "Fourteen administrators were interviewed in depth"; §3.2 "Twelve senior administrators (n=12)" | 5 (all four seats) | EIC, R1, R2, R3; DA M1 | P1 | 1 day |
| R3 | Redact the deductively identifying participant descriptors in §4.1 | SC-4 | Critical (R1, R3) / Major (EIC, R2) | text: §4.1 "the quality director of the largest private university in the region" | 5 (EIC, R1, R3), 4 (R2) | EIC, R1, R2, R3; DA C5 | P1 | 0.5 day |
| R4 | Document the consent basis for attributable role-level quotation and re-check §3.5 against the reported text | SC-4b | Critical (R1, R3) / Major (R2) | text: §3.5 "all data were fully anonymized prior to analysis so that no individual could be identified" | 5 (R1, R3), 4 (R2) | R1, R2, R3; DA C5 | P1 | 3 days |
| R5 | Withdraw the "balanced representation… full range of administrator views" claim | SC-3 | Critical (R1, R3) / Major (EIC, R2) | text: §4.3 "the study achieved balanced representation of perspectives, capturing the full range of administrator views" | 5 (R1, R2, R3), 4 (EIC) | EIC, R1, R2, R3; DA C3 | P1 | 0.5 day |
| R6 | Reinstate the dissenting accounts and re-analyse, reporting them either integrated or as an explicit negative-case analysis | SC-3b | Critical (R1, R3) / Major (R2) | text: §4.3 "these were excluded for space, as they fell outside the three-theme structure" | 5 (R1, R2, R3) | R1, R2, R3; DA C3 | P1 (D1 + D3 block driver) | 10 days |
| R7 | Correct the Delacroix (2018) attribution in §5 to the position given in §2 and the reference annotation | SC-5 | Critical (R2) / Major (EIC, R1, R3) | text: §5 "who recommends that institutions treat broad stakeholder consultation as the central mechanism for building a healthy quality culture" | 5 (EIC, R2, R3), 4 (R1) | EIC, R1, R2, R3; DA C1 | P1 (D2 block driver) | 0.5 day |
| R8 | Rebuild §5's third finding and its recommendation without the inverted warrant, engaging Delacroix's actual argument as a challenge to it | SC-5b | Critical (R2) / Major (R3) | text: §5 "Consultation, on this reading, is the engine of internalization." | 5 (R2, R3) | R2, R3; DA C1 | P1 (DA C1 VALIDATED; recommendation currently unwarranted) | 3 days |
| R9 | Delete the sector-wide generalisation and the verb "demonstrate"; reduce the claim to the study's sampling frame and reconcile §5 with §6 | SC-6 | Major (R1, R2, R3); `[SEVERITY-SOURCE: letter-fallback]` for EIC | text: §5 "these findings demonstrate that universities across the sector treat QA as a negotiated accomplishment"; "administrators everywhere face the same fundamental tension" | 5 (R1, R2, R3); EIC body-level, no per-finding confidence recorded | EIC (body), R1, R2, R3; DA C2 | P1 (D3 block driver) | 1 day |
| R10 | Withdraw the "first comprehensive account" claim and state the specific increment over Pettersen (2022), Rahman (2020), Silva & Tan (2021) | SC-7 | Major (EIC, R1, R2, R3) | text: §6 "the first comprehensive account"; §2 "This latter turn is closest in spirit to the present study" | 5 (all four seats) | EIC, R1, R2, R3; DA M5 | P1 (D6 block driver) | 1 day |
| R11 | Delete the prospective efficacy claim in §6 and the abstract's design implications, or supply design variation with measured outcomes and an identification argument | — (DA C4) | Critical (DA band) | text: §6 "are more likely to foster the internalized commitment that the language of quality culture promises"; Abstract "implications for how universities design QA processes" | 4 (DA) | DA C4 | P1 (DA C4 VALIDATED; D3 coherence defect) | 1 day |
| R12 | Correct §4.1's "structured protocol" to the actual semi-structured design and delete the non-artifactuality inference it licenses | SC-17 | Major (R1) / Minor (R2, R3) — arbitrated to Major | text: §4.1 "These themes emerged systematically from the structured protocol"; §3.1 "semi-structured interviews" | 5 (R1), 4 (R2, R3) | R1, R2, R3; DA M3 | P1 (D3 block driver) | 0.5 day |
| R13 | Report the thematic analysis as an auditable procedure: tradition, codebook, coder count, disagreement resolution, operational meaning of "stable", saturation, audit trail, member checking, reflexivity | SC-10 | Critical (R1) / Major (EIC) | absence: §3.4 Analysis — expected coding framework, coder count, agreement procedure, saturation evidence, audit trail, reflexivity; checked §3.1, §3.3, §3.4, §4, end matter | 5 (R1), 4 (EIC) | R1, EIC | P1 (D1 block driver) | 4 days |
| R14 | Requantify prevalence claims with per-theme, per-participant, and per-site counts; remove universal and superlative language not supported by them | SC-11 | Major (R1, EIC) | text: §4.2 "This relational, distributed understanding of leadership recurred across every interview" | 5 (R1), 4 (EIC) | R1, EIC; DA M6 | P1 (component of the D3 proportionality repair) | 3 days |
| R15 | Add a participant characteristics table for both strands: per-site n, role, tenure, and response rate | SC-22b | Critical (R1) / Major (EIC, R2) | text: §3.2 "Twelve senior administrators (n=12)… In parallel, 48 mid-level staff (n=48)" | 5 (R1, R2), 4 (EIC) | EIC, R1, R2 | P1 | 2 days |
| R16 | Document the survey instrument: scale range, anchors, item wording or published source, item count, internal consistency, dimensionality evidence | SC-12 | Major (EIC, R1, R2) | absence: §3.3 Data collection — expected scale range and anchors, item wording or source, internal-consistency coefficient, dimensionality evidence; checked §3.1, §3.3, §3.4, §4.4, reference list | 5 (R1, R2), 4 (EIC) | EIC, R1, R2 | P1 (D1 block driver) | 2 days |
| R17 | Either report the subgroup test in full — test name, statistic, df, group means and dispersions, effect size, interval, multiplicity handling, and a justification of the test at n=9 vs n=11 — or delete the inferential language and present a descriptive contrast | SC-13 | Major (R1) | absence: §4.4 — expected test name, statistic, df, effect size, CI, multiplicity correction for the reported p<.05; checked §3.3, §3.4, §4.4, end matter | 5 (R1) | R1; DA M4 | P1 (D1 block driver) | 2 days |
| R18 | Close the survey denominators (48 recruited vs 20 compared; third institution absent) and withdraw the institutional-type moderator claim, which is confounded with site at one institution per type | SC-14, SC-14b | Major (R1, R2) | text: §4.4 "Comparing staff at the research university (n=9) with staff at the teaching-focused university (n=11)"; §4.4 "points to institutional type as a possible moderator" | 5 (R1, R2) | R1, R2; DA M4 | P1 | 2 days |
| R19 | Disclose the national system and QA regime — or state the confidentiality reason and describe regime type, accreditor relationship, and review cycle generically | SC-15 | Major (EIC, R2, R3) | text: §3.2 "three universities in a single national system" | 5 (EIC, R2, R3) | EIC, R2, R3 | P1 (named in the D2 and D6 repair sets) | 1 day |
| R20 | Define and operationalise "quality culture" against established conceptualisations, and state its relation to the survey measure | SC-16 | Major (R2) | text: §4.4 "respondents' overall institutional quality culture score was moderately positive (M=3.9, SD=0.6)" | 5 (R2) | R2 | P1 (named in the D2 owner's repair set) | 4 days |
| R21 | Engage the quality-culture and internal-QA canon and restate the gap claim to what survives that engagement | SC-8 | Major (EIC, R2) | absence: §2 and the reference list — expected ESG 2015 Part 1, Harvey & Green, Harvey & Stensaker, EUA Quality Culture Project, Ehlers, Sursock, Cardoso et al., Loukkola & Zhang; checked §1 gap statement, §2, §5, §6, all 12 entries | 5 (EIC, R2) | EIC, R2 | P1 (D6 and D2 block drivers) | 8 days |
| R22 | Make the scoping decision first: either deepen to full-article evidence depth for this venue or reposition as a research note | SC-22 | Major (EIC) | absence: §3 and §4 — expected a participant table, a coding framework, and a per-theme evidence base proportionate to a full research article; checked §3.4, §4.1–§4.4, and the absence of any numbered table or figure | 4 (EIC) | EIC | P1 (D6 block driver) | 15 days (deepen) / 3 days (reposition) |
| R23 | Attribute the borrowed neo-institutional and audit-society vocabulary, and state what the administrator hinge adds once that tradition is on the table | SC-9 | Major (R3) | absence: §2 and the 12-item reference list — expected at least one citation to the decoupling or audit-society literature that already models ceremonial compliance and reactivity; checked all 12 references, §2 ¶1–4, §5 ¶2 | 5 (R3) | R3 | P1 (D4 block driver) | 6 days |

> Transported metadata appears on every row: severity is copied from each seat's per-finding band (both bands are shown with attribution where seats differ), evidence anchors are copied verbatim from the cards' typed anchors, and confidence is each seat's per-finding score. The one fallback is R9's EIC position, which the EIC card raises in its letter body without a Severity or Confidence tag — marked `[SEVERITY-SOURCE: letter-fallback]`.

### Required Item Details

**R1 — Reference identifiers.** All twelve DOIs sit on the reserved, non-resolving `10.5555/` prefix with sequential suffixes `1042001`–`1042012`, so nothing the manuscript cites can be located. The Journal-Fit Reviewer asks that this be settled before further reviewer time is committed.
- **Acceptance criteria**: every reference entry carries an identifier that resolves to the cited source, and no entry uses the `10.5555/` prefix.

**R2 — Interview N.** The abstract says fourteen, §3.2 says twelve with an explicit `(n=12)`. Both the DA and R1 note that the gap is numerically equal to the "minority" §4.3 says was excluded; if that is the explanation, it must be stated, because it means disconfirming participants were removed from the reported N rather than only from the narrative.
- **Acceptance criteria**: one interview N appears throughout the manuscript, and any difference between recruited and analysed participants is reported with its reason and its relation to the §4.3 exclusion.

**R3 — Redaction.** "The quality director of the largest private university in the region" and "the associate dean for quality at the public research university" are singular office-holders in a sample containing exactly one private and one public research university.
- **Acceptance criteria**: no participant attribution in the manuscript permits identification of a single office-holder when combined with the §3.2 institutional descriptions.

**R4 — Consent basis.** Four seats find §3.5's guarantee incompatible with the reported text, and the quoted material criticises the speakers' own institutions.
- **Acceptance criteria**: the manuscript states whether consent covered attributable role-level quotation, whether participants reviewed and approved their quotes, and what the approving committee was told, and §3.5 describes the protection the reported findings actually deliver.

**R5 — Representativeness claim.** The full-range claim and the disclosed exclusion cannot both stand.
- **Acceptance criteria**: no claim of balanced or full-range representation remains in the manuscript unless it is supported by an analysis that includes the dissenting accounts.

**R6 — Reinstatement and re-analysis.** The stated ground for exclusion was the theme structure itself, which makes the three-theme finding partly a product of the analytic decision.
- **Acceptance criteria**: the dissenting accounts are analysed in the manuscript, either integrated into a revised theme structure or reported as an explicit negative-case analysis, and the reported themes are shown to survive their inclusion.

**R7 — Delacroix attribution.** §2 and the reference annotation report Delacroix as arguing against consultation as evidence of quality culture; §5 recruits him as its principal advocate.
- **Acceptance criteria**: every reference to Delacroix (2018) in the manuscript states the same position, and that position matches the source.

**R8 — Rebuilt recommendation.** Delacroix's actual argument predicts the failure mode the §5 recommendation would produce, so a citation swap is not sufficient.
- **Acceptance criteria**: §5's third finding states its recommendation with a warrant the paper's own evidence or a correctly-read source supplies, and engages Delacroix's objection rather than claiming his support.

**R9 — Scope of the Discussion claim.** §5 escalates to the sector and to "everywhere" while §6 asks for future testing across systems; one of those two sentences must go.
- **Acceptance criteria**: no claim in the manuscript extends beyond three institutions in one national system, the verb "demonstrate" is not used of thematic interview data, and §5 and §6 are mutually consistent about what has been established.

**R10 — Priority claim.** §2 places Pettersen (2022) and Rahman (2020) on the same terrain and calls one "closest in spirit to the present study."
- **Acceptance criteria**: the first-ness and comprehensiveness claims are removed, and §6 states a specific increment over Pettersen, Rahman, and Silva & Tan that §2 supports.

**R11 — Efficacy claim.** Nothing in §3 varies QA process design and nothing measures internalised commitment as an outcome.
- **Acceptance criteria**: no claim that particular QA process designs are more likely to produce internalised commitment remains, unless the manuscript reports design variation with measured outcomes and an explicit identification argument.

**R12 — Design description and the inference from it.** §4.1's "structured protocol" contradicts §3.1 and §3.3, and instrument structure does not warrant a conclusion about how observations distribute across sites.
- **Acceptance criteria**: §4.1 describes the semi-structured design accurately, and no confidence about cross-institutional non-artifactuality is claimed from instrument structure.

**R13 — Auditable analysis.** §3.4's three sentences restate the outcome rather than describing a procedure.
- **Acceptance criteria**: §3.4 reports the analytic tradition, the codebook or coding framework, the number of analysts and how disagreements were resolved, what "stable structure" meant operationally, saturation evidence, the audit trail, any member checking, and a reflexivity statement addressing recruitment through the QA offices.

**R14 — Prevalence.** "Most pervasive" and "recurred across every interview" are quantified claims made without any counts, in a corpus from which cases were removed.
- **Acceptance criteria**: every prevalence or superlative claim about the themes is supported by a reported count or distribution in a theme-by-participant display, and unsupported claims are removed.

**R15 — Participant table.** No per-site n, role, tenure, or response rate is reported for either strand.
- **Acceptance criteria**: a participant characteristics table reports per-site n, role, and tenure for the interview sample and per-site n and response rate for the survey.

**R16 — Instrument documentation.** M=3.9 is carried into the abstract on a metric the reader cannot locate, and the construct is treated as unitary without evidence.
- **Acceptance criteria**: the manuscript reports the scale range and anchors, the item set or its published source, the item count, an internal-consistency coefficient, and dimensionality evidence for the quality-culture score.

**R17 — Inferential claim.** "p<.05" appears with no test, statistic, df, effect size, interval, or multiplicity handling, on n=9 vs n=11; R1's four arithmetic receipts were all non-computable for want of these inputs.
- **Acceptance criteria**: §4.4 either reports the full test with an effect size, an interval, and a justification of the test choice at these group sizes, or contains no inferential language and presents both group means and dispersions descriptively.

**R18 — Denominators and the moderator claim.** Twenty-eight respondents and one entire institution never appear in the results, and institutional type is indistinguishable from site at one institution per type.
- **Acceptance criteria**: the survey results account for all 48 respondents and all three institutions with per-site denominators, and no institutional-type moderator claim is made from a design in which type and site are confounded.

**R19 — Context disclosure.** Anonymising institutions is standard; anonymising the system withholds the referent of "external QA requirements" and blocks any transferability judgement.
- **Acceptance criteria**: §3.2 identifies the national system and QA regime, or states the confidentiality reason and specifies regime type, accreditor relationship, and review cycle in enough detail for a comparative reader to locate the study.

**R20 — Construct definition.** "Quality culture" carries the title, research question, findings, and conclusion, and is nowhere operationalised; as written no observation would count against the central claim.
- **Acceptance criteria**: the manuscript defines quality culture, states its relation to established conceptualisations, specifies what would count as evidence against the central claim, and connects the definition to what the survey measures.

**R21 — Canon engagement.** §1's "under-theorized" claim holds only against the sources the manuscript happens to cite.
- **Acceptance criteria**: §2 engages the established quality-culture and internal-QA literature, and the gap claim in §1 is restated to what survives that engagement — plausibly an empirical gap at the level of administrator practice rather than a theoretical one.

**R22 — Scale and format decision.** Roughly 1,850 body words, three themes carried by one or two quotations each, one descriptive mean, and no table or figure.
- **Acceptance criteria**: the resubmission is either a full article whose evidence depth matches the venue's norm, or a research note whose claims are scaled to its length, and the choice is stated in the response letter.

**R23 — Borrowed theory.** Ritual, theatre, calendar-bound audit cycles, identity work, and the Discussion's own use of "decouple" all come from traditions the manuscript never cites.
- **Acceptance criteria**: the borrowed constructs are attributed to the literature that supplies them, and the manuscript states what the administrator hinge adds to that literature — the meaning-recovery mechanism in §4.3 being the strongest candidate.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | Add a limitations statement covering sample size, single system, gatekeeper recruitment, self-report data, and the non-representative survey subgroups | SC-19 | Major (R1) | absence: §5 and §6 — expected an explicit limitations statement; checked §3, §5, §6, abstract | 5 (R1) | R1 | P2 | 1 day |
| S2 | Report the role composition and attempt role-differentiated analysis, or defend "administrators" as a single analytic category | SC-23 | Major (R2) | text: §3.2 "including quality directors, associate deans, and registry heads" | 4 (R2) | R2 | P2 | 3 days |
| S3 | State the triangulation limitation and the untested self-legitimation reading; reframe the central claim as administrators' accounts rather than an account of quality culture | SC-24 | Major (R3) | absence: §3.2 and §4 — expected at least one academic, student, or external reviewer data source capable of testing administrators' self-accounts; checked §3.2, §3.3, §4.1–§4.4, §5 | 4 (R3) | R3 | P2 | 2 days |
| S4 | State the mixed-methods point of integration, add a joint display, and own the §4.4 divergence instead of labelling it corroboration | SC-18 | Major (R1) / Minor (R3) | text: §4.4 "The survey corroborated the qualitative picture" and "the interview accounts had led us to anticipate a more skeptical picture" | 4 (R1, R3) | R1, R3; DA M2 | P2 | 3 days |
| S5 | Develop the meaning-recovery mechanism: how the conversion works, when it fails, what sustains it | SC-25 | Minor (R3) | absence: §5 treatment of the meaning-recovery mechanism — expected analytic specification of how administrators convert rituals they call theatre into vocational commitment; checked §4.3, §5 ¶2, §6 | 4 (R3) | R3 | P2 | 4 days |
| S6 | Make the practical recommendation actionable: define "genuine" participation against the consultation-as-artifact §4.1 documents | SC-26 | Minor (R3) | text: §5 "processes that maximize genuine participation should be favored" | 4 (R3) | R3 | P2 | 2 days |
| S7 | Append or deposit the interview guide and survey items, and add a data availability statement | SC-20 | Minor (R1) | absence: end matter — expected interview guide, survey item set, data availability statement; checked §3.3, §3.4, §6, reference list | 5 (R1) | R1 | P3 | 1 day |
| S8 | Remove the non-APA "Annotation" from the Delacroix reference entry | SC-21 | Minor (EIC) | text: References, Delacroix (2018) "Annotation: Delacroix argues against relying on stakeholder consultation as evidence of quality culture" | 5 (EIC) | EIC | P3 | 0.1 day |
| S9 | Differentiate accreditation, audit, and evaluation at first use and keep the terms distinct thereafter | SC-27 | Minor (R2) | text: §1 "periodic self-evaluation, external review, and continuous documentation of academic standards" | 5 (R2) | R2 | P3 | 0.5 day |
| S10 | Reconcile §4.1's "region" with §3.2's "single national system" | SC-28 | `[SEVERITY-SOURCE: letter-fallback]` — DA body-level, no band | text: §4.1 "the largest private university in the region"; §3.2 "three universities in a single national system" | DA body-level, no per-finding confidence recorded | DA | P3 | 0.1 day |

No separate aggregated EDITORIAL channel is emitted: none of the five cards carried a Minor Issues section below the finding threshold, so every P3 item above is a transported banded finding rather than an editorial-channel item.

### Revision Checklist (Checkable List)

#### Priority 1 — Structural Revisions (estimated total: 59 days if repositioned as a research note, 71 days if deepened to full-article scope)
- [ ] R1: Obtain resolvable identifiers for all twelve references — this gates re-review
- [ ] R22: Make the scoping decision (deepen vs reposition) before starting the rest
- [ ] R2: Reconcile the interview N and report any exclusion with its reason
- [ ] R3: Redact identifying participant descriptors
- [ ] R4: Document the consent basis and ethics-committee scope
- [ ] R5: Withdraw the full-range representation claim
- [ ] R6: Reinstate the dissenting accounts and re-analyse
- [ ] R7: Correct the Delacroix attribution
- [ ] R8: Rebuild §5's third recommendation
- [ ] R9: Delete the sector-wide generalisation; reconcile §5 with §6
- [ ] R10: Withdraw the priority claim; state the increment
- [ ] R11: Delete or re-evidence the §6 efficacy claim
- [ ] R12: Correct the design description and drop the inference from it
- [ ] R13: Report the thematic analysis as an auditable procedure
- [ ] R14: Requantify the prevalence claims
- [ ] R15: Add the participant characteristics table
- [ ] R16: Document the survey instrument
- [ ] R17: Report the subgroup test in full or delete the inferential language
- [ ] R18: Close the survey denominators; withdraw the moderator claim
- [ ] R19: Disclose the national system and QA regime
- [ ] R20: Define and operationalise "quality culture"
- [ ] R21: Engage the canon; restate the gap claim
- [ ] R23: Attribute the borrowed neo-institutional vocabulary

#### Priority 2 — Content Supplementation (estimated total: 15 days)
- [ ] S1: Add the limitations statement
- [ ] S2: Report role composition; attempt role-differentiated analysis
- [ ] S3: State the triangulation limitation; narrow the interpretive claim
- [ ] S4: State the integration point; own the divergence
- [ ] S5: Develop the meaning-recovery mechanism
- [ ] S6: Make the recommendation actionable

#### Priority 3 — Text and Formatting (estimated total: 2 days)
- [ ] S7: Append the interview guide and survey items; add a data availability statement
- [ ] S8: Remove the reference-list annotation
- [ ] S9: Differentiate the external QA instrument types
- [ ] S10: Reconcile "region" with "single national system"

### Revision Deadline

Twelve weeks, which exceeds the standard 6–8 week major-revision window. The extension is warranted by three items that cannot be compressed: re-analysis with the dissenting cases reinstated (R6), canon engagement and restatement of the gap claim (R21), and ethics-committee correspondence on the consent basis (R4). Two conditions on the timetable: R1 should be returned within one week, since the reference apparatus gates re-review; and the R22 scoping decision should be made in week two, because the "deepen" and "reposition" branches differ by roughly two working weeks. If the manuscript is repositioned as a research note, eight to nine weeks is realistic. Re-review will go to the same panel.

### Response Letter Template

Use the format in `templates/revision_response_template.md` and respond to every numbered item R1–R23 and S1–S10 individually, quoting the revised text and its location. Items R5, R9, R10, and R11 are deletions or withdrawals rather than additions; state explicitly what was removed. For R22, state which branch was taken and why. Declining a Required item is not available: all twelve consensus items and every named dimension-block trigger must be addressed.

---

## Part 3: Reviewer Report Summary (Appendix)

These cards report dimension scores rather than an overall recommendation or a report-level Confidence Score, so the template's Recommendation and Confidence rows are substituted with assessed-dimension verdicts and per-finding confidence range. The substitution is not an inference about a recommendation the seats did not make.

### Appendix A — Seat summaries

**Journal-Fit Reviewer (EIC)** — Assessed: D5 = block, D6 = block (repairable); D1–D4 not_assessed. Per-finding confidence 4–5.
- Key point: neither the reference apparatus nor the priority claim survives inspection — twelve of twelve DOIs are non-resolving placeholders, and §6 claims first-ness while the quality-culture canon is absent and the three themes restate three sources already in the bibliography.

**Peer Reviewer 1 (Methodology)** — Assessed: D1 = block (repairable), D3 = block (repairable); D2, D4, D5, D6 not_assessed. Per-finding confidence 4–5. Filed a scoring-plan dissent narrowing its own D1 fatal trigger; all four arithmetic receipts returned non-computable because the manuscript withholds the required inputs.
- Key point: almost every load-bearing procedural fact is absent, asserted, or contradicted — two sample sizes, an unrecoverable analytic procedure, and disconfirming cases removed to preserve the theme structure they should have tested.

**Peer Reviewer 2 (Domain)** — Assessed: D2 = block (repairable); all others not_assessed. Per-finding confidence 4–5.
- Key point: §5 recruits Delacroix as an advocate for the position he argues against and builds the paper's design recommendation on the inversion, while the headline construct is never defined and the national QA regime is withheld.

**Peer Reviewer 3 (Perspective)** — Assessed: D4 = block; all others not_assessed. Per-finding confidence 4–5.
- Key point: this is a decoupling study that does not cite the decoupling literature it borrows its vocabulary from, and its anonymisation guarantee is defeated on the first page of Findings; accessibility, by contrast, is not the problem.

**Devil's-Advocate Reviewer (DA)** — Assessed: D3 = block (repairable); all others not_assessed. Five CRITICAL, six MAJOR; per-finding confidence 4–5. Considered `fatal` on D3 and rejected it.
- Key point: five independent seams — an inverted load-bearing citation, a scope jump to the sector, an exclusion rule that immunises the findings, a prescriptive efficacy claim with no outcome variable, and an ethics statement the Findings falsify — each with a different repair.

### Appendix B — Sub-Claim Inventory (Step 1b)

Positions: `raised` / `corroborated` / `not-mentioned` (silence, not opposition) / `disputed`. Denominator is always the four non-DA seats. Severity and confidence are transported from each seat's per-finding tags.

| sub_claim_id | parent_weakness | Positions (EIC / R1 / R2 / R3) | agree / conflict / silent | Disposition | Transported severity (by seat) | Confidence (by seat) |
|---|---|---|---|---|---|---|
| SC-1 | Reference apparatus (EIC W1) | raised / — / — / — | 1 / 0 / 3 | single-reviewer finding | Critical (EIC) | 5 |
| SC-2 | Sample count (EIC W7, R1 W1, R2 W8, R3 W9) | raised / raised / corroborated / corroborated | 4 / 0 / 0 | **CONSENSUS-4** | Critical (R1); Major (EIC, R2, R3) | 5 / 5 / 5 / 5 |
| SC-3 | Representativeness claim (EIC W10, R1 W2, R2 W10, R3 W5) | raised / raised / raised / raised | 4 / 0 / 0 | **CONSENSUS-4** | Critical (R1, R3); Major (EIC, R2) | 4 / 5 / 5 / 5 |
| SC-3b | Exclusion as analytic-validity failure (R1 W2, R2 W10, R3 W5) | not-mentioned (deferred) / raised / corroborated / corroborated | 3 / 0 / 1 | **CONSENSUS-3** (silent: EIC) | Critical (R1, R3); Major (R2) | — / 5 / 5 / 5 |
| SC-4 | Identifiability (EIC W5, R1 W4, R2 W9, R3 W1) | raised / raised / raised / raised | 4 / 0 / 0 | **CONSENSUS-4** | Critical (R1, R3); Major (EIC, R2) | 5 / 5 / 4 / 5 |
| SC-4b | Consent documentation (R1 W4, R2 W9, R3 W1) | not-mentioned / raised / corroborated / raised | 3 / 0 / 1 | **CONSENSUS-3** (silent: EIC) | Critical (R1, R3); Major (R2) | — / 5 / 4 / 5 |
| SC-5 | Delacroix reversal (EIC W8, R1 W12, R2 W1, R3 W3) | raised / raised / raised / raised | 4 / 0 / 0 | **CONSENSUS-4** | Critical (R2); Major (EIC, R1, R3) | 5 / 4 / 5 / 5 |
| SC-5b | Recommendation must be rebuilt (R2 W1, R3 W3) | not-mentioned / not-mentioned / raised / corroborated | 2 / 0 / 2 | corroborated finding | Critical (R2); Major (R3) | — / — / 5 / 5 |
| SC-6 | Sector generalisation (EIC body, R1 W10, R2 W3, R3 W6) | corroborated / raised / raised / raised | 4 / 0 / 0 | **CONSENSUS-4** | Major (R1, R2, R3); EIC `[SEVERITY-SOURCE: letter-fallback]` | — / 5 / 5 / 5 |
| SC-7 | Priority claim (EIC W3, R1 W10, R2 W2, R3 W2) | raised / raised / raised / corroborated | 4 / 0 / 0 | **CONSENSUS-4** | Major (all four) | 5 / 5 / 5 / 5 |
| SC-8 | QA/quality-culture canon absent (EIC W3, R2 W5) | raised / not-mentioned / raised / not-mentioned | 2 / 0 / 2 | corroborated finding | Major (EIC, R2) | 5 / — / 5 / — |
| SC-9 | Decoupling literature absent (R3 W2) | — / — / — / raised | 1 / 0 / 3 | single-reviewer finding | Major (R3) | 5 |
| SC-10 | Analysis not auditable (R1 W3, EIC W4) | corroborated / raised / — / — | 2 / 0 / 2 | corroborated finding | Critical (R1); Major (EIC) | 4 / 5 |
| SC-11 | Prevalence unquantified (R1 W9, EIC W4) | corroborated / raised / — / — | 2 / 0 / 2 | corroborated finding | Major (R1, EIC) | 4 / 5 |
| SC-12 | Instrument undocumented (EIC W9, R1 W7, R2 W4) | raised / raised / corroborated / not-mentioned | 3 / 0 / 1 | **CONSENSUS-3** (silent: R3) | Major (all three) | 4 / 5 / 5 |
| SC-13 | Significance claim unreportable (R1 W6) | not-mentioned (deferred) / raised / not-mentioned (deferred) / not-mentioned (deferred) | 1 / 0 / 3 | single-reviewer finding | Major (R1) | 5 |
| SC-14 | Survey denominators (R1 W5, EIC W9) | corroborated / raised / — / — | 2 / 0 / 2 | corroborated finding | Major (R1, EIC) | 4 / 5 |
| SC-14b | Moderator claim unavailable (R1 W5, R2 W6) | — / raised / corroborated / — | 2 / 0 / 2 | corroborated finding | Major (R1, R2) | 5 / 5 |
| SC-15 | Context withheld (EIC W6, R2 W6, R3 W6) | raised / not-mentioned / raised / corroborated | 3 / 0 / 1 | **CONSENSUS-3** (silent: R1) | Major (all three) | 5 / 5 / 5 |
| SC-16 | Construct undefined (R2 W4) | — / — / raised / — | 1 / 0 / 3 | single-reviewer finding | Major (R2) | 5 |
| SC-17 | "Structured protocol" (R1 W8, R2 W11, R3 W10) | not-mentioned / raised / corroborated / corroborated | 3 / 0 / 1 | **CONSENSUS-3** (silent: EIC) | Major (R1); Minor (R2, R3) — arbitrated to Major | — / 5 / 4 / 4 |
| SC-18 | Integration absent (R1 W11, R3 W11) | — / raised / — / corroborated | 2 / 0 / 2 | corroborated finding | Major (R1); Minor (R3) | 4 / 4 |
| SC-19 | No limitations (R1 W13) | — / raised / — / — | 1 / 0 / 3 | single-reviewer finding | Major (R1) | 5 |
| SC-20 | No reproducibility affordances (R1 W14) | — / raised / — / — | 1 / 0 / 3 | single-reviewer finding | Minor (R1) | 5 |
| SC-21 | Reference annotation (EIC W2) | raised / — / — / — | 1 / 0 / 3 | single-reviewer finding | Minor (EIC) | 5 |
| SC-22 | Scale below article norm (EIC W4) | raised / — / — / — | 1 / 0 / 3 | single-reviewer finding | Major (EIC) | 4 |
| SC-22b | Participant table (R1 W1/W5, EIC W4/W9, R2 W7) | corroborated / raised / corroborated / not-mentioned | 3 / 0 / 1 | **CONSENSUS-3** (silent: R3) | Critical (R1); Major (EIC, R2) | 4 / 5 / 4 |
| SC-23 | "Administrators" collapses roles (R2 W7) | — / — / raised / — | 1 / 0 / 3 | single-reviewer finding | Major (R2) | 4 |
| SC-24 | No triangulation (R3 W4) | — / — / — / raised | 1 / 0 / 3 | single-reviewer finding | Major (R3) | 4 |
| SC-25 | Mechanism underdeveloped (R3 W7) | — / — / — / raised | 1 / 0 / 3 | single-reviewer finding | Minor (R3) | 4 |
| SC-26 | Recommendation unactionable (R3 W8) | — / — / — / raised | 1 / 0 / 3 | single-reviewer finding | Minor (R3) | 4 |
| SC-27 | QA vocabulary undifferentiated (R2 W12) | — / — / raised / — | 1 / 0 / 3 | single-reviewer finding | Minor (R2) | 5 |
| SC-28 | "Region" vs national system (DA body) | non-DA seats: none | 0 non-DA | DA-sourced note (outside the consensus count) | `[SEVERITY-SOURCE: letter-fallback]` | — |

Every sub-claim above was decomposed from a claim a seat actually made; no sub-claim originates with this synthesis.

### Appendix C — Roadmap machine form (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "major_revision",
  "items": [
    {"id": "R1", "priority": "must_fix", "verification_criteria": "Every reference entry carries an identifier that resolves to the cited source; no entry uses the 10.5555/ prefix.", "reviewer": "eic", "severity": "critical", "evidence_anchor": "text: References, Aoki (2019) / Silva & Tan (2021) 10.5555/1042001-10.5555/1042012", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-1"]},
    {"id": "R2", "priority": "must_fix", "verification_criteria": "One interview N throughout; any difference between recruited and analysed participants reported with its reason and its relation to the §4.3 exclusion.", "reviewer": "eic,methodology,domain,perspective", "severity": "critical", "evidence_anchor": "text: Abstract 'Fourteen administrators were interviewed in depth'; §3.2 'Twelve senior administrators (n=12)'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-2"]},
    {"id": "R3", "priority": "must_fix", "verification_criteria": "No participant attribution permits identification of a single office-holder when combined with the §3.2 institutional descriptions.", "reviewer": "eic,methodology,domain,perspective", "severity": "critical", "evidence_anchor": "text: §4.1 'the quality director of the largest private university in the region'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-4"]},
    {"id": "R4", "priority": "must_fix", "verification_criteria": "Manuscript states whether consent covered attributable role-level quotation, whether participants approved quotes, and what the committee approved; §3.5 matches the reported text.", "reviewer": "methodology,domain,perspective", "severity": "critical", "evidence_anchor": "text: §3.5 'all data were fully anonymized prior to analysis so that no individual could be identified'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-4b"]},
    {"id": "R5", "priority": "must_fix", "verification_criteria": "No claim of balanced or full-range representation remains unless supported by an analysis including the dissenting accounts.", "reviewer": "eic,methodology,domain,perspective", "severity": "critical", "evidence_anchor": "text: §4.3 'the study achieved balanced representation of perspectives, capturing the full range of administrator views'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-3"]},
    {"id": "R6", "priority": "must_fix", "verification_criteria": "Dissenting accounts analysed in the manuscript, integrated or as explicit negative-case analysis, and reported themes shown to survive their inclusion.", "reviewer": "methodology,domain,perspective", "severity": "critical", "evidence_anchor": "text: §4.3 'these were excluded for space, as they fell outside the three-theme structure'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-3b"]},
    {"id": "R7", "priority": "must_fix", "verification_criteria": "Every reference to Delacroix (2018) states the same position and that position matches the source.", "reviewer": "eic,methodology,domain,perspective", "severity": "critical", "evidence_anchor": "text: §5 'who recommends that institutions treat broad stakeholder consultation as the central mechanism for building a healthy quality culture'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-5"]},
    {"id": "R8", "priority": "must_fix", "verification_criteria": "§5's third finding states its recommendation with a warrant the evidence or a correctly-read source supplies, and engages Delacroix's objection.", "reviewer": "domain,perspective", "severity": "critical", "evidence_anchor": "text: §5 'Consultation, on this reading, is the engine of internalization.'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-5b"]},
    {"id": "R9", "priority": "must_fix", "verification_criteria": "No claim extends beyond three institutions in one national system; 'demonstrate' not used of thematic interview data; §5 and §6 mutually consistent.", "reviewer": "eic,methodology,domain,perspective", "severity": "major", "evidence_anchor": "text: §5 'these findings demonstrate that universities across the sector treat QA as a negotiated accomplishment'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-6"]},
    {"id": "R10", "priority": "must_fix", "verification_criteria": "First-ness and comprehensiveness claims removed; §6 states a specific increment over Pettersen, Rahman, and Silva & Tan that §2 supports.", "reviewer": "eic,methodology,domain,perspective", "severity": "major", "evidence_anchor": "text: §6 'the first comprehensive account'; §2 'This latter turn is closest in spirit to the present study'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-7"]},
    {"id": "R11", "priority": "must_fix", "verification_criteria": "No claim that particular QA process designs are more likely to produce internalised commitment remains, absent design variation with measured outcomes and an identification argument.", "reviewer": "da", "severity": "critical", "evidence_anchor": "text: §6 'are more likely to foster the internalized commitment that the language of quality culture promises'", "confidence": 4, "source_kind": "finding", "sub_claims": []},
    {"id": "R12", "priority": "must_fix", "verification_criteria": "§4.1 describes the semi-structured design accurately; no cross-institutional non-artifactuality claimed from instrument structure.", "reviewer": "methodology,domain,perspective", "severity": "major", "evidence_anchor": "text: §4.1 'These themes emerged systematically from the structured protocol'; §3.1 'semi-structured interviews'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-17"]},
    {"id": "R13", "priority": "must_fix", "verification_criteria": "§3.4 reports tradition, codebook, coder count and disagreement resolution, operational meaning of 'stable', saturation evidence, audit trail, member checking, and reflexivity on gatekeeper recruitment.", "reviewer": "methodology,eic", "severity": "critical", "evidence_anchor": "absence: §3.4 Analysis - expected coding framework, coder count, agreement procedure, saturation evidence, audit trail, reflexivity", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-10"]},
    {"id": "R14", "priority": "must_fix", "verification_criteria": "Every prevalence or superlative theme claim supported by a reported count or distribution in a theme-by-participant display; unsupported claims removed.", "reviewer": "methodology,eic", "severity": "major", "evidence_anchor": "text: §4.2 'This relational, distributed understanding of leadership recurred across every interview'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-11"]},
    {"id": "R15", "priority": "must_fix", "verification_criteria": "Participant characteristics table reports per-site n, role, and tenure for interviews and per-site n plus response rate for the survey.", "reviewer": "methodology,eic,domain", "severity": "critical", "evidence_anchor": "text: §3.2 'Twelve senior administrators (n=12)... In parallel, 48 mid-level staff (n=48)'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-22b"]},
    {"id": "R16", "priority": "must_fix", "verification_criteria": "Scale range and anchors, item set or published source, item count, internal-consistency coefficient, and dimensionality evidence reported for the quality-culture score.", "reviewer": "eic,methodology,domain", "severity": "major", "evidence_anchor": "absence: §3.3 Data collection - expected scale range and anchors, item wording or source, internal-consistency coefficient, dimensionality evidence", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-12"]},
    {"id": "R17", "priority": "must_fix", "verification_criteria": "§4.4 either reports the full test with effect size, interval, and justification of test choice at n=9 vs n=11, or contains no inferential language and reports both group means and dispersions.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "absence: §4.4 - expected test name, statistic, df, effect size, CI, multiplicity correction for the reported p<.05", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-13"]},
    {"id": "R18", "priority": "must_fix", "verification_criteria": "Survey results account for all 48 respondents and all three institutions with per-site denominators; no institutional-type moderator claim where type and site are confounded.", "reviewer": "methodology,domain", "severity": "major", "evidence_anchor": "text: §4.4 'Comparing staff at the research university (n=9) with staff at the teaching-focused university (n=11)'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-14", "SC-14b"]},
    {"id": "R19", "priority": "must_fix", "verification_criteria": "§3.2 identifies the national system and QA regime, or states the confidentiality reason and specifies regime type, accreditor relationship, and review cycle.", "reviewer": "eic,domain,perspective", "severity": "major", "evidence_anchor": "text: §3.2 'three universities in a single national system'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-15"]},
    {"id": "R20", "priority": "must_fix", "verification_criteria": "Quality culture defined, related to established conceptualisations, connected to what the survey measures, with a stated disconfirming observation.", "reviewer": "domain", "severity": "major", "evidence_anchor": "text: §4.4 'respondents' overall institutional quality culture score was moderately positive (M=3.9, SD=0.6)'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-16"]},
    {"id": "R21", "priority": "must_fix", "verification_criteria": "§2 engages the established quality-culture and internal-QA literature; §1's gap claim restated to what survives that engagement.", "reviewer": "eic,domain", "severity": "major", "evidence_anchor": "absence: §2 and the reference list - expected ESG 2015 Part 1, Harvey & Green, Harvey & Stensaker, EUA Quality Culture Project, Ehlers, Sursock, Cardoso et al., Loukkola & Zhang", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-8"]},
    {"id": "R22", "priority": "must_fix", "verification_criteria": "Resubmission is either a full article matching the venue's evidence-depth norm or a research note whose claims are scaled to its length, with the choice stated in the response letter.", "reviewer": "eic", "severity": "major", "evidence_anchor": "absence: §3 and §4 - expected a participant table, a coding framework, and a per-theme evidence base proportionate to a full research article", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-22"]},
    {"id": "R23", "priority": "must_fix", "verification_criteria": "Borrowed constructs attributed to the decoupling and audit-society literature, and the manuscript states what the administrator hinge adds to it.", "reviewer": "perspective", "severity": "major", "evidence_anchor": "absence: §2 and the 12-item reference list - expected at least one citation to the decoupling or audit-society literature", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-9"]},
    {"id": "S1", "priority": "should_fix", "verification_criteria": "Limitations statement names sample size, single national system, gatekeeper recruitment, self-report data, and the non-representative survey subgroups.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "absence: §5 and §6 - expected an explicit limitations statement", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-19"]},
    {"id": "S2", "priority": "should_fix", "verification_criteria": "Role composition reported and either role-differentiated analysis attempted or 'administrators' defended as one analytic category.", "reviewer": "domain", "severity": "major", "evidence_anchor": "text: §3.2 'including quality directors, associate deans, and registry heads'", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-23"]},
    {"id": "S3", "priority": "should_fix", "verification_criteria": "Triangulation limitation and the self-legitimation counter-reading stated; central claim reframed as administrators' accounts.", "reviewer": "perspective", "severity": "major", "evidence_anchor": "absence: §3.2 and §4 - expected at least one academic, student, or external reviewer data source", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-24"]},
    {"id": "S4", "priority": "should_fix", "verification_criteria": "Point of integration stated, joint display presented, and §4.4's divergence reported as divergence rather than corroboration.", "reviewer": "methodology,perspective", "severity": "major", "evidence_anchor": "text: §4.4 'The survey corroborated the qualitative picture' and 'the interview accounts had led us to anticipate a more skeptical picture'", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-18"]},
    {"id": "S5", "priority": "should_fix", "verification_criteria": "Meaning-recovery mechanism specified: how the conversion works, when it fails, what institutional conditions sustain it.", "reviewer": "perspective", "severity": "minor", "evidence_anchor": "absence: §5 treatment of the meaning-recovery mechanism", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-25"]},
    {"id": "S6", "priority": "should_fix", "verification_criteria": "'Genuine participation' operationalised against the consultation-as-artifact §4.1 documents, with an action a QA director could take.", "reviewer": "perspective", "severity": "minor", "evidence_anchor": "text: §5 'processes that maximize genuine participation should be favored'", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-26"]},
    {"id": "S7", "priority": "nice_to_fix", "verification_criteria": "Interview guide and survey item set appended or deposited, and a data availability statement present.", "reviewer": "methodology", "severity": "minor", "evidence_anchor": "absence: end matter - expected interview guide, survey item set, data availability statement", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-20"]},
    {"id": "S8", "priority": "nice_to_fix", "verification_criteria": "Delacroix reference entry contains bibliographic elements only; the 'Annotation' gloss removed.", "reviewer": "eic", "severity": "minor", "evidence_anchor": "text: References, Delacroix (2018) 'Annotation: Delacroix argues against relying on stakeholder consultation as evidence of quality culture'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-21"]},
    {"id": "S9", "priority": "nice_to_fix", "verification_criteria": "Accreditation, audit, and evaluation differentiated at first use and kept distinct thereafter.", "reviewer": "domain", "severity": "minor", "evidence_anchor": "text: §1 'periodic self-evaluation, external review, and continuous documentation of academic standards'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-27"]},
    {"id": "S10", "priority": "nice_to_fix", "verification_criteria": "§4.1's 'region' and §3.2's 'single national system' describe the same sampling frame.", "reviewer": "da", "severity": "unbanded", "evidence_anchor": "text: §4.1 'the largest private university in the region'; §3.2 'three universities in a single national system'", "source_kind": "finding", "sub_claims": ["SC-28"]}
  ]
}
```

---

## Quality Gates

- [x] All five reviewer cards read and cited by seat, weakness id, and transported anchor
- [x] Consensus and disagreement identified and labelled per sub-claim over a denominator of 4; zero formal SPLITs, stated explicitly with the reason
- [x] Every disagreement carries an arbitration result and rationale, including the two severity resolutions, the construct-definition scope distinction, the contribution-scoping directive, and the fatality record
- [x] Decision consistent with the reviewer record and with the contract arithmetic (F2 at severity 90 selects major revision; F1 did not fire because no seat minted fatality)
- [x] Every roadmap item traceable to a named weakness in a named card, with severity, evidence anchor, and confidence transported on every row
- [x] Fallbacks marked where a card lacked a tag (`[SEVERITY-SOURCE: letter-fallback]` on R9's EIC position and S10)
- [x] No self-fabricated issues: every sub-claim decomposes a claim a seat actually made; no sixth-reviewer comment added
- [x] Roadmap format compatible with `academic-paper` revision mode input, plus Schema 7 machine form
- [x] Ordinal contract held: Required Item Details blocks are the contiguous sequence R1..R23 in the Required table's order, each with a single-line Acceptance criteria bullet
- [x] Surface-form parity check run and recorded, with the opposite-style counterfactual applied to the four single-reviewer Required items
- [x] Panel provenance block emitted rather than omitted, with the missing stamp flagged and no independence claim inferred
- [x] Tone professional and impartial; card-hygiene defects flagged, not silently repaired

**Epistemic status**: the audit arithmetic, the consensus counts, and the transported metadata are mechanical and checkable against the cards. The four judgement calls in this letter are (a) adjudicating DA C4 on editorial text-check because no Journal-Fit position on it exists in the record, (b) resolving two severity variances by expertise and explicit deference, (c) admitting four sub-1/2-consensus items to Required priority as named dimension-block triggers, and (d) the twelve-week deadline. Each is stated with its basis so the author and the handling editor can contest it on the evidence.
