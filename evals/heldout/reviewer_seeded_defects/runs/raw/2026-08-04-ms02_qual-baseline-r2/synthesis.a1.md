# Editorial Decision Package

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · panel_size 5

---

## Part 0: Sprint Contract Audit (mechanical)

### Step 1 — Role-scoped scoring matrix

Only seats whose `contract_role` appears in a dimension's `eligible_roles` contribute. `not_assessed` from ineligible seats is excluded from both numerator and denominator.

| Dim | Priority | Eligible roles | Assessed eligible seats (score) | Dimension score |
|-----|----------|----------------|----------------------------------|-----------------|
| D1 methodology_rigor | mandatory | methodology | methodology = block (repairable) | **block** |
| D2 domain_accuracy | mandatory | domain | domain = block (**fatal**) | **block(fatal)** |
| D3 argumentative_coherence | mandatory | da, methodology | da = block (repairable); methodology = block (repairable) | **block** |
| D4 cross_disciplinary_relevance | high | perspective | perspective = block (no fatal declared) | **block** |
| D5 writing_and_structure | normal | eic | eic = block (no fatal declared) | **block** |
| D6 venue_fit_and_contribution | mandatory | eic | eic = block (repairable) | **block** |

No dimension is unassessed by an eligible seat; no `[DIMENSION-UNASSESSED]` abort. Audit verdict: worst assessed eligible score = `block`, with a declared fatal block on D2 → **block(fatal)**.

### Step 2 — Failure condition evaluation

| ID | Severity | Cross-reviewer quantifier | Expression | Per-dimension evaluation | Fired |
|----|----------|---------------------------|------------|--------------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 F, **D2 T**, D3 F, D6 F → `any` = true | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1 T, D2 T, D3 T, D6 T → true | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 (n=1, owner=methodology) T; D2 (n=1, owner=domain) T; D3 (n=2, both seats) T; D6 (n=1, owner=eic) T → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 (n=1, perspective) T → true | **true** |
| F5 | 40 | any | any dimension scores 'warn' or worse | all six T → true | **true** |
| F0 | 10 | all | every dimension scores 'pass' | no dimension all-pass | false |

All expressions parsed against the closed vocabulary; no `[EXPRESSION-UNRECOGNISED]`.

### Step 3 — Precedence and audit emission

Highest severity among fired conditions: **F1 (95)** → `action: editorial_decision=reject`.

```
dimension_verdicts: [D1=block, D2=block(fatal), D3=block, D4=block, D5=block, D6=block]
fired_conditions: [F1, F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED]
editorial_decision=reject
```

No `C<n>=REJECTED`, so no rejection-rationale lines are required. The mechanical decision is not `accept`, so `[DA-CRITICAL-VS-ACCEPT]` does not apply.

**Cross-model blind decision check (#518):** `ARS_CROSS_MODEL` not set in this invocation and no consent gate passed — check not run, no behavioral change.

---

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this run is `reviewer_full`, so a provenance statement is mandatory, but no dispatching-layer provenance stamp was supplied with the reviewer cards. The synthesizer is forbidden from inferring one. **No claim is made here about which model family ran which seat, and no reader should infer model independence across the five seats.** The handling editor must obtain the stamp from the dispatching layer before this package is treated as carrying a provenance disclosure.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript "Building Institutional Quality Culture: Administrator Perspectives on Quality Assurance Implementation in Universities." It was reviewed by five independent reviewers: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary perspective), and a Devil's Advocate reader.

### Decision: **Reject**

The decision follows the audit above. A fatal block was recorded on a mandatory dimension (D2, domain accuracy), which triggers condition F1 at severity 95. Four further conditions fired at lower severity; none of them would have produced a milder outcome, since every one of the six acceptance dimensions scored `block`.

I want to be direct about what this decision does and does not say. The interview material in this manuscript is good. Three of the four non-adversarial reviewers said so independently, and the observation in §4.3 — that administrators hold the compliance/meaning tension open and locate professional identity in the gap rather than resolving it — was singled out by the domain and perspective seats as the paper's most valuable and most under-developed move. The reason this is a Reject and not a Major Revision is not the quality of the fieldwork. It is that the evidentiary and citational apparatus surrounding that fieldwork cannot presently be audited, and that the manuscript's own text falsifies several of its own claims.

### Consensus Analysis

Consensus is computed over the four non-DA seats (Journal-Fit, Methodology, Domain, Perspective), per sub-claim, with a denominator of 4. Silence is recorded as silence, never as agreement.

#### Points of agreement

- **[CONSENSUS-4] SC-1 — Disconfirming cases were excluded from the analysis.** §4.3 states that participants sceptical of the entire QA enterprise "were excluded for space, as they fell outside the three-theme structure that organized our analysis." All four seats raised this; three banded it Critical.
- **[CONSENSUS-4] SC-2 — The "balanced representation … full range" claim is falsified in the same paragraph that makes it.**
- **[CONSENSUS-3] SC-3 — The universality claims that rest on the excluded corpus ("recurred across every interview", "pervasiveness") cannot stand.** Silent seat: Domain (R2).
- **[CONSENSUS-4] SC-4 — §5 attributes to Delacroix (2018) the position §2 and the reference annotation say Delacroix argues against.** Journal-Fit, Domain and Perspective raised it substantively; Methodology raised it as a referral to the domain seat.
- **[CONSENSUS-3] SC-5 — The paper's only practical recommendation loses its sole citational support once SC-4 is corrected.** Silent seat: Methodology (R1).
- **[CONSENSUS-4] SC-6 — Sector-wide and universal claims in §5 are not licensed by three purposively recruited sites in one unnamed system.**
- **[CONSENSUS-4] SC-7 — "The first comprehensive account" (§6) is contradicted by the manuscript's own §2, which credits Pettersen (2022), Rahman (2020) and Silva & Tan (2021) with this ground.**
- **[CONSENSUS-4] SC-8 — The interview N is reported as fourteen (Abstract) and twelve (§3.2) and is never reconciled.**
- **[CONSENSUS-4] SC-9 — The §3.5 anonymisation guarantee is broken by the §4.1 attributions.**
- **[CONSENSUS-4] SC-10 — The §4.4 significance claim is not reportable as printed, and the institutional-type moderator inference does not follow from it.**
- **[CONSENSUS-4] SC-18 — §4.1's "structured protocol" contradicts §3.1's "semi-structured", and protocol uniformity cannot license the site-effect inference drawn from it.**
- **[CONSENSUS-3] SC-13 — The survey has no sampling frame, no response rate, and 28 of 48 respondents unaccounted for in the reported contrast.** Silent seat: Domain (R2).
- **[CONSENSUS-3] SC-14 — M=3.9 is uninterpretable without scale anchors, item count, instrument provenance, or reliability.** Silent seat: Perspective (R3).
- **[CONSENSUS-3] SC-17 — The national system, QA regime, agency, review cycle, and fieldwork period are all withheld.** Silent seat: Methodology (R1).

#### Corroborated findings (2/4, below the consensus bar — action-bearing, not consensus-labelled)

- **SC-21 — The reference apparatus is unverifiable** (Journal-Fit W1, Domain W2). See the arbitration note below: this is a 2/4 finding that nonetheless determines the decision, and the reason is structural, not a weighting inflation.
- **SC-11 — A divergent survey result is narrated as corroboration; no integration strategy is stated** (Methodology W9, Perspective).
- **SC-12 — The thematic analysis is described as an outcome, not a procedure** (Methodology W5, Journal-Fit W9).
- **SC-15a — "Quality culture" is never operationalised** (Journal-Fit W8, Domain W5).
- **SC-20a — No exhibits of any kind: no protocol, participant table, coding examples, or survey instrument** (Journal-Fit W9, Methodology W5/W8).
- **SC-22 — "Distributed leadership" and "identity work" are used as authority-borrowing labels** (Domain W6, Perspective W4).

#### Single-reviewer findings (1/4 — noted, weighted by confidence)

- **SC-16a — The pre-2018 quality-culture canon is absent** (Domain W3, Critical, confidence 5). Full weight.
- **SC-16b — The ceremonial-conformity / decoupling / audit-culture literature is absent** (Perspective W4, Major, confidence 5). Full weight.
- **SC-23 — The construct is characterised from a single occupationally interested vantage point** (Perspective W6, confidence 4).
- **SC-24 — No operational lever is offered to practitioners** (Perspective W7, confidence 4).
- **SC-25 — The literature search strategy is undisclosed** (Domain W3, confidence 5).
- **SC-20b — No data-availability or materials statement** (Methodology W13, Minor).

#### Points of disagreement — arbitrated

**[SPLIT] SC-15b — Is "quality culture" adequately defined for the reader?**
Perspective (R3, S2) states that §1's gloss is "the one core construct that is properly defined for an outside reader" and holds it up as the standard the paper's other constructs failed to meet. Journal-Fit (W8) and Domain (W5) state that the construct is never defined, functions in three incompatible senses (process, institutional property, scalar score), and is never distinguished from quality assurance, accreditation, or audit.
**Editor's resolution:** Both hold, of different things. R3 is judging first-encounter legibility for a non-specialist; the §1 gloss does that job and should be kept. Journal-Fit and Domain are judging disciplinary precision and referential stability across the manuscript, which is where the failure sits — the gloss does not discipline §4.4's numeric use or §5's institution-level use. Expertise-first arbitration favours the domain and venue seats on construct precision within this literature (both at confidence 5). **Required action follows Journal-Fit and Domain; R3's observation is preserved as a strength to retain, not as a reason to decline the work.**

**[SPLIT] SC-19 — How serious is the missing limitations section?**
Journal-Fit (W11) bands it Minor: a departure from venue convention that does not change the core claims. Methodology (W10) bands it Major: its absence is precisely what lets §5 scale from three sites to a sector without friction, and it leaves gatekeeper-mediated recruitment through QA offices unexamined.
**Editor's resolution:** Methodology's reading governs on the substantive point — the omission is load-bearing because it is coupled to SC-6, which is a CONSENSUS-4 must-fix. The item is therefore **Required**, but Journal-Fit's effort estimate is the accurate one: writing it is a day's work, not a re-analysis. Required, low effort.

**[Severity spread, no dispute] SC-8** — Perspective bands the N discrepancy Minor and explicitly defers the band to the methodology seat; Journal-Fit, Methodology and Domain band it Major. Deference is not dissent, so this is not a SPLIT. The Major band from the three seats governs.

**[Severity spread, no dispute] SC-9** — Journal-Fit and Methodology band the identifiability problem Major; Perspective, the seat with designated ethics-committee responsibility for qualitative de-identification, bands it Critical at confidence 5, and Methodology explicitly defers the participant-protection dimension to "the reviewer covering it." **Critical governs**, on expertise-first grounds.

**[Requested arbitration not delivered]** Perspective (W6) asked the domain seat to arbitrate whether field convention treats administrator-only designs as sufficient for an institution-level construct. The domain card does not answer. Under the unresolved-dissent principle this is neither upheld nor dismissed: it is recorded as **unresolved**, the authors must respond to it substantively, and the panel is on record as not having resolved it.

### Arbitration note: how a 2/4 finding determines the decision

SC-21 (unverifiable references) was raised by two of four seats, which is below the consensus bar. It nonetheless drives the decision, and I want the mechanism visible rather than implied.

The contract assigns D2 (domain accuracy) exclusively to the domain seat. Consensus count and dimension ownership are separate axes: only the domain seat scores D2, and it scored `block` with `block_class: fatal`, which fires F1 at severity 95. The Journal-Fit seat's independent corroboration raises confidence in that finding; it does not create it, and no aggregation rule outside the contract was applied. Both seats hold the finding at confidence 4, not 5, and both name the same falsifier.

### Editorial note (recorded; does **not** alter the decision)

The domain reviewer stated their own falsifier explicitly: "resolving DOIs, or PDFs of the twelve items, would reduce this finding to a formatting error and I would revise my assessment accordingly." The Journal-Fit seat wrote the same, and both noted that live DOI resolution was unavailable to them within review. The structural argument the domain seat made — that DOI prefixes are registrant-specific, so twelve items across eight journals and one monograph publisher cannot share prefix `10.5555` with consecutive suffixes — does not depend on resolution.

The handling editor should resolve all twelve identifiers and record the outcome, because the outcome matters for what happens next: if the sources are real and the identifiers are placeholders, the D2 fatal would on the reviewers' own stated terms become repairable, and the manuscript's remaining problems (D1, D3, D5, D6) are all classed repairable by the seats that scored them. That is a matter for a future submission. **The decision computed on the cards as submitted is Reject, and it stands.**

### Decision Rationale

Five independent seats scored six dimensions and every one came back `block`. That uniformity is not a panel that was hard to please; it is a manuscript whose fluent surface is not supported by its record.

Three defects are decisive. First, the reference apparatus: twelve DOIs in an unbroken sequential block on a reserved test prefix, spread across eight journals and one publisher that cannot share a prefix, with three named venues and the monograph publisher unidentifiable in the field. Until that is resolved, every positional claim the paper makes about its field is unverifiable, and the domain seat recorded this as fatal. Second, §4.3 discloses that disconfirming cases were removed because they did not fit the coding structure, in the same paragraph that claims full-range coverage. All four non-DA seats and the Devil's Advocate identified this independently; it makes the three-theme finding circularly warranted, and it cannot be fixed by rewriting a sentence. Third, §3.5's unconditional anonymisation guarantee is broken by §4.1's role-plus-institution attributions, which uniquely identify two senior staff in a three-institution frame and attach institutionally damaging quotations to them. That is a live risk to real people, not a formatting matter.

Against those, the errors that would ordinarily define a Major Revision — the 14/12 discrepancy, the unreported significance test, the semi-structured/structured contradiction, the sector-wide leap, the reversed Delacroix attribution — are individually correctable. They are not what carries this decision. They do, however, establish a pattern: on at least eight occasions the manuscript asserts something its own text contradicts.

The path forward is a reconstruction, not a revision, and it leads to a smaller paper than the one drafted. Three seats converged on the same honest version: a three-site, single-system, named-regime account of how QA administrators inhabit the gap between compliance and meaning, positioned as a grounded extension of Silva and Tan (2021) rather than as a first comprehensive account. That paper is publishable. Nothing that must be removed to get there is currently defensible.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | The entire reference apparatus is unverifiable and structurally inconsistent with real DOI registration; the domain seat scores this a fatal block on D2, which fires F1 | R2 (Domain), EIC | text: § References — "https://doi.org/10.5555/1042001" … "https://doi.org/10.5555/1042012"; "Meridian Academic Press" | R1 |
| 2 | Disconfirming cases were excluded for not fitting the theme structure, while the same paragraph claims full-range coverage; the three-theme finding is circularly warranted | EIC, R1, R2, R3, DA (C1) | text: §4.3 — "these were excluded for space, as they fell outside the three-theme structure that organized our analysis"; "capturing the full range of administrator views" | R2 |
| 3 | Two senior participants are effectively identified in §4.1 against an unconditional anonymisation guarantee in §3.5, with institutionally damaging quotations attached | R3 (Perspective, Critical), EIC, R1, DA (C3) | text: §3.5 and §4.1 — "no individual could be identified in reported findings"; "the quality director of the largest private university in the region" | R4 |

---

## Part 2: Revision Roadmap

> **Status of this roadmap.** The decision is **Reject**. This manuscript will not be reconsidered in the present cycle, and no revision of it should be submitted against this decision. The roadmap below is the reconstruction path for a future submission — to this venue or, per the reviewers' converging assessment, to a venue matched to the smaller and defensible contribution. It is emitted in `academic-paper` revision-mode-compatible form so the work can be planned, not because a revision round has been offered.
>
> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Severity, Evidence Anchor and Confidence are transported from the reviewer cards and are not re-derived. Where seats banded the same sub-claim differently, the governing band is shown with the spread noted and the arbitration recorded in Part 1. No `[SEVERITY-SOURCE]` or `[CONFIDENCE-SOURCE]` fallback tags are required: every card in this panel carries per-finding Severity and Confidence.

### Required Revisions (Must Fix)

> **Ordinal contract:** the `### Required Item Details` blocks below are numbered `R<n>` in this table's order — the nth Required row here is the Roadmap's nth `must_fix` item.

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Supply resolvable identifiers or source documents for all twelve references, or withdraw and rebuild the reference base from verifiable sources | SC-21 | Critical (EIC, R2 concurrent) | text: § References — "https://doi.org/10.5555/1042001"; "https://doi.org/10.5555/1042012"; "Meridian Academic Press" | 4 — reserved-prefix pattern and registrant-specific DOI assignment certain; existence of sources not determinable from the manuscript | R2 (Domain), EIC | P1 | 1–2 weeks if sources exist; otherwise a full literature rebuild |
| R2 | Reintegrate the excluded dissenting accounts, re-derive the theme structure against them, and withdraw or re-establish the coverage and universality claims | SC-1, SC-2, SC-3 | Critical (EIC, R1, R3; R2 Major) | text: §4.3 — "these were excluded for space, as they fell outside the three-theme structure"; "capturing the full range of administrator views"; §4.2 — "recurred across every interview" | 5 — the manuscript states the exclusion explicitly | R1 (Methodology), EIC, R2, R3, DA C1 | P1 | 3–5 weeks (re-analysis, not rewriting) |
| R3 | Correct the Delacroix (2018) attribution in §5 and rebuild the third finding and the design implication from the source's actual position | SC-4, SC-5 | Critical (R2, DA C2; EIC and R3 Major) | text: §2 and §5 — "cautions that participatory rhetoric can itself become a compliance ritual"; "who recommends that institutions treat broad stakeholder consultation as the central mechanism" | 5 — contradiction is internal to the manuscript | R2 (Domain), EIC, R3, DA C2 | P1 | 1–2 weeks |
| R4 | Strip identifying role-plus-institution descriptors from §4.1, re-examine whether consent covered attributable institutional criticism, and obtain a statement from the approving ethics committee | SC-9 | Critical (R3 governing; EIC and R1 Major — see arbitration) | text: §3.5 and §4.1 — "all data were fully anonymized … so that no individual could be identified"; "the quality director of the largest private university in the region" | 5 — R3, designated qualitative de-identification reviewer | R3 (Perspective), EIC, R1, DA C3 | P1 | 1 week for the text; committee turnaround governs |
| R5 | Report the §4.4 inferential analysis in full — named test, group means and SDs, effect size, interval estimate, assumption checks, and every comparison conducted — or delete the claim and the moderator sentence | SC-10 | Critical (R1 governing; EIC Major, reporting-standards scope) | text: §4.4 — "we found a statistically significant difference (p<.05)"; "points to institutional type as a possible moderator" | 5 — R1, statistical screening of small-N educational surveys | R1 (Methodology), EIC, R2, R3, DA M4 | P1 | 1–2 weeks |
| R6 | Withdraw the sector-wide and universal claims in §5 and the priority claim in §6; restate the contribution as a three-site single-system account and, per the Journal-Fit seat, a grounded empirical extension of Silva and Tan (2021) | SC-6, SC-7 | Critical (R1, R2; EIC and R3 Major) | text: §5 and §6 — "a general account of how the higher education sector as a whole constructs quality culture"; "administrators everywhere"; "the first comprehensive account" | 5 — design scope compared against stated inference | R1, R2, R3, EIC, DA M1/M5 | P1 | 1–2 weeks |
| R7 | Report the thematic analysis as a procedure — coding framework, coder count, intercoder or member-checking step, positionality statement, saturation basis, per-institution theme distribution — and reconcile the semi-structured/structured design vocabulary | SC-12, SC-18 | Major (R1, EIC) | absence: §3.4 — expected coding framework, coder count, intercoder/member-checking, positionality, saturation criterion; text: §3.1 and §4.1 — "semi-structured interviews"; "emerged systematically from the structured protocol" | 5 (SC-12, R1); 4 (SC-18, EIC — inconsistency plain, correct description not determinable) | R1 (Methodology), EIC, R2, R3, DA M7 | P1 | 2–3 weeks |
| R8 | State the correct interview N, explain how the 14/12 discrepancy arose, and state its relation to the disclosed exclusions | SC-8 | Major (EIC, R1, R2 governing; R3 Minor, band deferred) | text: Abstract and §3.2 — "Fourteen administrators were interviewed in depth"; "Twelve senior administrators (n=12)" | 5 — direct textual comparison | EIC, R1, R2, R3, DA M2 | P1 | 1–2 days |
| R9 | Report the survey completely: sampling frame, invitation and response rates, per-institution respondent counts reconciling n=9 and n=11 against 48, instrument provenance, item count, scale anchors, and an internal-consistency estimate | SC-13, SC-14 | Major (R1, R2, EIC) | absence: §3.2–§3.4 and §4.4 — expected sampling frame, response rate, per-institution counts, scale anchors, item count, reliability; text: §4.4 — "M=3.9, SD=0.6" | 5 — survey methods and instrument documentation screening | R1 (Methodology), R2, EIC, DA M6 | P1 | 1–2 weeks |
| R10 | Re-anchor the gap claim against the literature that exists — the pre-2018 quality-culture canon and the ceremonial-conformity / decoupling / audit-culture tradition — and disclose the search strategy (databases, strings, date limits, inclusion criteria, dates run) | SC-16a, SC-16b, SC-25 | Critical (R2); Major (R3) | absence: §2 — expected engagement with the pre-2018 quality-culture canon and with the institutional-decoupling, ceremonial-conformity, audit-culture and reactivity literatures; checked §1, §2, §5, §6 and all twelve reference entries | 5 (R2, "this is the literature I work in and teach"); 5 (R3, "my primary research literature") | R2 (Domain), R3 (Perspective) | P1 | 4–6 weeks |
| R11 | Name the national system, the QA regime, the agency, the review cycle and its consequences, and the fieldwork period | SC-17 | Major (EIC, R2, R3) | text: §3.2 — "three universities in a single national system" | 5 — comparative QA literature is unusable without regime context | EIC, R2, R3 | P1 | 3–5 days, subject to the constraint note below |
| R12 | Add a limitations section covering three-site scope, single-system design, gatekeeper-mediated recruitment through QA offices, the disclosed exclusions, and small subgroup cells | SC-19 | Major (R1 governing; EIC Minor — arbitrated, see Part 1) | absence: §5 and §6 — expected a limitations statement covering three-site scope, single national system, recruitment through institutional QA offices, and small subgroup sizes | 5 — standard reporting element | R1 (Methodology), EIC | P1 | 1–2 days |

**Constraint interaction the authors must resolve (R4 × R11).** Naming the national system narrows the population within which the two identifiable administrators sit, so R11 makes R4 harder. This is not a reviewer disagreement — the Perspective seat raised both items and named the remedy itself: identifiability exposure scales inversely with sample size, so widening the institutional base is simultaneously the methodological and the governance fix. Authors should decide this deliberately rather than resolving it silently in one direction.

### Required Item Details

#### R1 — Reference apparatus verification
Twelve DOIs occupy an unbroken sequential block on the `10.5555` reserved test prefix. DOI prefixes are registrant-specific, so twelve items across eight journals and one monograph publisher cannot share one prefix; consecutive suffixes across distinct registrants are not an achievable registration outcome. Three named venues and the monograph publisher are unidentifiable in this field. No page or locator reference appears anywhere, so no citation use can be checked against source text.
- **Acceptance criteria**: All twelve references carry identifiers that resolve to the cited items, or source documents are supplied to the editor; the inline annotation on the Delacroix entry is removed; page or locator references are added wherever a source is used to support a specific claim.

#### R2 — Reintegrate the excluded cases and re-derive the themes
Cases were removed on the stated ground that they did not fit the coding structure. In thematic analysis, cases that resist the structure are the primary evidence that the structure needs revision, and "for space" is not an analytic justification. The exclusion falsifies the "full range" claim in the same paragraph and the "every interview" claim one section earlier.
- **Acceptance criteria**: The dissenting accounts are analysed and reported; the theme structure is re-derived against the full corpus and revised if the negative cases do not fit; the coverage and universality claims are either re-established against the full corpus or withdrawn; the authors state explicitly that the revised conclusion may differ from the present one.

#### R3 — Delacroix correction and rebuild of the third finding
§2, the reference title, and the reference annotation all state that Delacroix argues against treating stakeholder consultation as sufficient evidence of quality culture; §5 attributes the opposite position to the same source and builds the paper's only actionable recommendation on it. The manuscript's own §4.1 theme is evidence for Delacroix's warning, not against it.
- **Acceptance criteria**: §5 represents Delacroix's actual position; the third finding and the design implication are rebuilt from that position or dropped; the abstract's implications sentence is aligned with whatever survives; the authors state which of misreading, misremembering, or insertion produced the inversion.

#### R4 — De-identification, consent scope, and ethics confirmation
§3.5 gives an unconditional guarantee; §4.1 supplies role-plus-institution descriptors that uniquely identify two senior staff in a three-institution frame, attached to institutionally damaging quotations.
- **Acceptance criteria**: All role-plus-institution descriptors are replaced with generic attributions; the authors confirm in writing whether the approved protocol and consent covered attributable criticism of an effectively named employer; a statement from the approving ethics committee is supplied to the editor, or documented participant approval for the identifying detail is provided.

#### R5 — Full reporting or deletion of the §4.4 inference
A p-value is asserted for a 9-versus-11 contrast with no named test, no descriptive statistics, no effect size, no interval, no assumption checks, and no account of how many comparisons were available; the planned analysis (§3.4, by role) is not the analysis reported (§4.4, by institution type).
- **Acceptance criteria**: The test, group means and SDs, effect size, confidence interval, assumption checks, and the complete set of comparisons conducted (planned and unplanned) are reported, with the plan/report deviation explained — or the significance claim and the institutional-type moderator sentence are deleted.

#### R6 — Rescope the claims to the design
§5 converts three purposively recruited sites in one unnamed system into the sector as a whole and into administrators everywhere; §6 claims priority against ground the manuscript's own §2 assigns to three cited works.
- **Acceptance criteria**: "Universities across the sector", "the higher education sector as a whole", "administrators everywhere", and "the first comprehensive account" are removed; the contribution is restated at the scope the design supports; the abstract, introduction and conclusion are aligned to the restated claim.

#### R7 — Auditable analysis reporting and stable design vocabulary
"Coding proceeded iteratively … until a stable structure was reached" describes an outcome, not a procedure. §4.1 additionally offers protocol uniformity as a control for site effects, which it cannot be, and calls the instrument structured where §3.1 calls it semi-structured.
- **Acceptance criteria**: §3.4 reports the analytic tradition, inductive or deductive coding, coder count, disagreement handling, member-checking or its absence, positionality, and the basis on which coding stopped; the per-institution distribution of themes is reported; the design vocabulary is consistent across §3.1, §3.4 and §4.1; the §4.1 site-effect inference is withdrawn or replaced with the distributional evidence.

#### R8 — Reconcile the interview N
The Abstract and §3.2 disagree about the size of the primary dataset, and every theme-prevalence statement depends on the denominator.
- **Acceptance criteria**: A single N is stated consistently throughout; the origin of the discrepancy is explained; the authors state whether the two-case difference relates to the exclusions disclosed in §4.3.

#### R9 — Complete survey reporting
Eligibility, invitation and response counts, and the distribution of the 48 respondents across three sites are all unstated, so non-response and self-selection bias cannot be assessed; 28 respondents are unaccounted for in the reported contrast; M=3.9 has no scale, no item count, no provenance, and no reliability estimate.
- **Acceptance criteria**: Sampling frame, invitation and response rates, and per-institution respondent counts that reconcile with 48 are reported; the instrument is supplied with item wording, response anchors, item count, provenance, and an internal-consistency estimate, ideally as an appendix.

#### R10 — Re-anchor the gap claim and disclose the search
The assertion that quality culture is under-theorised in everyday administrative practice, and that the hinge actors are unstudied, does not survive contact with either the higher-education quality-culture canon or the organizational-sociology tradition that named this paper's central finding decades ago.
- **Acceptance criteria**: §2 engages both literatures substantively or argues explicitly why each does not apply; §5's "long-standing concerns" cites long-standing work; the gap claim is restated at whatever is genuinely open after that engagement; the search strategy is disclosed with databases, strings, date limits, inclusion criteria, and dates run.

#### R11 — Specify the context
"Three universities in a single national system" is the whole of the contextual specification, and no reader can situate ritual compliance or documentation burden without knowing the regime that produced them.
- **Acceptance criteria**: The national system, the regulatory regime, the agency, the review cycle length, the consequences attached to adverse findings, and the fieldwork period are all stated, with the institution-level anonymity decision made deliberately against the R4 constraint and its reasoning stated.

#### R12 — Limitations section
The absence is what allows §5 to scale from three sites to a sector without friction and leaves gatekeeper-mediated recruitment unexamined.
- **Acceptance criteria**: A limitations section names the three-site scope, the single national system, recruitment through the QA offices whose work is under study, the disclosed case exclusions and their treatment after R2, and the small subgroup cells behind any retained survey contrast.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | State the mixed-methods design typology, integration point and joint display; report the survey result as the divergence it is and retract "corroborated" | SC-11 | Major (R1) | text: §4.4 — "The survey corroborated the qualitative picture"; "the interview accounts had led us to anticipate a more skeptical picture" | 5 — publishes on QUAL→quan integration quality | R1 (Methodology), R3, DA M3 | P2 | 1 week |
| S2 | Engage the distributed-leadership and identity-work literatures and show the data meet their criteria, or relabel the themes descriptively | SC-22 | Major (R2, R3) | text: §4.2 and §4.3 — "This relational, distributed understanding of leadership recurred across every interview"; "This vocational framing appeared to function as a coping resource" | 4 (R2 — strong on the QA-office literature, moderate on leadership theory); 5 (R3 — primary research literature) | R2 (Domain), R3 (Perspective) | P2 | 2–3 weeks |
| S3 | Define and operationalise "quality culture", hold one referent across §1/§4.4/§5, and fix the QA/enhancement, internal/external, accreditation/audit/evaluation distinctions | SC-15a, SC-15b (arbitrated), SC-9-terminology | Major (EIC, R2); Minor for the vocabulary sub-item (R2 W9) | absence: §1–§4.4 — expected a stated definition and operationalization of quality culture separating it from quality assurance, accreditation, and audit; text: §2 — "states and accreditors steer autonomous institutions at a distance" | 5 — construct definitions and standard distinctions within the domain seat's competence | EIC, R2 (Domain); R3 dissent arbitrated | P2 | 1–2 weeks |
| S4 | Add vantage points beyond administrators, or rescope the object to administrators' accounts of quality culture and state the boundary condition | SC-23 | Major (R3) | absence: §3.2 and §4 — expected accounts from academics, students, or governance actors alongside the occupational composition of the 48-respondent survey frame | 4 — standard vantage-point critique; R3 requested domain arbitration that the domain card did not deliver | R3 (Perspective), DA M8 | P2 | 2 weeks (rescope) or a new data phase |
| S5 | Supply at least one operational lever for quality offices or agencies — workload recognition for persuasion labour, professional development, or evidence-requirement design | SC-24 | Major (R3) | absence: §5 third finding and §6 — expected at least one operational lever for quality offices or national agencies | 4 — practitioner-facing usability judgement, self-flagged as outside the reviewer's practitioner experience | R3 (Perspective) | P2 | 1 week |
| S6 | Append the interview guide, codebook and survey instrument; add a data-availability and materials statement | SC-20a, SC-20b | Major (EIC, SC-20a); Minor (R1, SC-20b) | absence: §3 Methods and §4 Findings — expected an interview protocol, participant characteristics table, coding examples with theme frequencies, and the survey instrument; and a data availability statement | 5 — standard reproducibility checklist | EIC, R1 (Methodology) | P2 | 1 week |
| S7 | Aggregated editorial channel: remove the inline reference annotation, add the participant characteristics table and any figures/tables the revised findings warrant, and correct residual formatting | — (`source_kind: editorial`) | Minor | text: § References, Delacroix entry — inline annotation retained in a submitted reference list | — | EIC (Minor Issues channel) | P3 | 2–3 days |

### Revision Checklist

#### Priority 1 — Structural reconstruction (estimated total effort: 12–18 weeks, R10 and R2 dominating)
- [ ] R1: Verify or rebuild all twelve references; supply resolvable identifiers or source documents
- [ ] R2: Reintegrate the excluded dissenting accounts and re-derive the theme structure
- [ ] R3: Correct the Delacroix attribution and rebuild the third finding and the design implication
- [ ] R4: De-identify §4.1, confirm consent scope, obtain the ethics committee statement
- [ ] R5: Report the §4.4 analysis in full or delete the claim and the moderator sentence
- [ ] R6: Withdraw the sector-wide, universal and priority claims; restate the contribution
- [ ] R7: Report the thematic analysis as a procedure; stabilise the design vocabulary; report per-site theme distribution
- [ ] R8: Reconcile the interview N and explain the discrepancy
- [ ] R9: Report the survey completely, with the instrument appended
- [ ] R10: Re-anchor the gap claim against both missing literatures; disclose the search strategy
- [ ] R11: Name the system, regime, agency, cycle and fieldwork period (decide the R4 trade-off deliberately)
- [ ] R12: Write the limitations section

#### Priority 2 — Content supplementation (estimated total effort: 6–8 weeks)
- [ ] S1: State the integration strategy; report the divergence as divergence
- [ ] S2: Engage or relabel "distributed leadership" and "identity work"
- [ ] S3: Define and operationalise "quality culture"; fix the QA vocabulary
- [ ] S4: Add vantage points or rescope the construct with a stated boundary condition
- [ ] S5: Supply an operational lever for practice
- [ ] S6: Append instruments, codebook and materials/data-availability statement

#### Priority 3 — Text and formatting (estimated total effort: 2–3 days)
- [ ] S7: Remove the inline reference annotation, add exhibits, correct residual formatting

### Deadline

Not applicable — the decision is Reject. For planning purposes only: the reconstruction above is on the order of five to six months of work, with R10 (literature re-anchoring) and R2 (re-analysis of the full corpus) on the critical path and R1 potentially gating everything.

### Response Letter Template

If the authors submit a reconstructed manuscript as a new submission, `templates/revision_response_template.md` should be used to respond point-by-point to every item R1–R12 and S1–S7, including the items the authors decline, with reasoning. Four items require an explicit written answer regardless of what the authors choose to change: R1 (whether the twelve sources exist), R2 (what the excluded accounts show), R4 (what consent actually covered), and R8 (which N is correct and why the discrepancy arose). The unresolved item recorded in Part 1 — whether an institution-level construct can be characterised from an administrator-only design — also requires a substantive response; the panel did not resolve it, and the authors should not read that silence as agreement in either direction.

### Machine-form Roadmap (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "reject",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": ["domain", "eic"], "sub_claims": ["SC-21"], "severity": "critical", "confidence": 4, "evidence_anchor": "text: § References — 10.5555/1042001 … 10.5555/1042012; Meridian Academic Press", "verification_criteria": "All twelve references carry resolving identifiers or source documents are supplied; inline annotation removed; locator references added for claim-supporting uses."},
    {"id": "R2", "priority": "must_fix", "reviewer": ["methodology", "eic", "domain", "perspective", "da"], "sub_claims": ["SC-1", "SC-2", "SC-3"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §4.3 — 'these were excluded for space, as they fell outside the three-theme structure'; 'capturing the full range of administrator views'", "verification_criteria": "Dissenting accounts analysed and reported; theme structure re-derived against the full corpus; coverage and universality claims re-established or withdrawn."},
    {"id": "R3", "priority": "must_fix", "reviewer": ["domain", "eic", "perspective", "da"], "sub_claims": ["SC-4", "SC-5"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §2 and §5 — 'cautions that participatory rhetoric can itself become a compliance ritual'; 'who recommends that institutions treat broad stakeholder consultation as the central mechanism'", "verification_criteria": "Delacroix represented per the source's actual position; third finding and design implication rebuilt or dropped; abstract aligned."},
    {"id": "R4", "priority": "must_fix", "reviewer": ["perspective", "eic", "methodology", "da"], "sub_claims": ["SC-9"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §3.5 and §4.1 — 'no individual could be identified in reported findings'; 'the quality director of the largest private university in the region'", "verification_criteria": "Identifying descriptors removed; consent scope confirmed in writing; ethics committee statement or documented participant approval supplied."},
    {"id": "R5", "priority": "must_fix", "reviewer": ["methodology", "eic", "da"], "sub_claims": ["SC-10"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §4.4 — 'we found a statistically significant difference (p<.05)'; 'points to institutional type as a possible moderator'", "verification_criteria": "Test, descriptives, effect size, interval, assumption checks and all comparisons reported with the plan/report deviation explained; or claim and moderator sentence deleted."},
    {"id": "R6", "priority": "must_fix", "reviewer": ["methodology", "domain", "perspective", "eic", "da"], "sub_claims": ["SC-6", "SC-7"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §5 and §6 — 'a general account of how the higher education sector as a whole constructs quality culture'; 'the first comprehensive account'", "verification_criteria": "Sector-wide, universal and priority claims removed; contribution restated at design scope; abstract, introduction and conclusion aligned."},
    {"id": "R7", "priority": "must_fix", "reviewer": ["methodology", "eic", "da"], "sub_claims": ["SC-12", "SC-18"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.4 — expected coding framework, coder count, intercoder/member-checking, positionality, saturation criterion; text: §3.1 vs §4.1 — 'semi-structured' vs 'the structured protocol'", "verification_criteria": "Analytic tradition, coder count, disagreement handling, member-checking, positionality and stopping rule reported; per-institution theme distribution reported; design vocabulary consistent; §4.1 site-effect inference withdrawn or evidenced."},
    {"id": "R8", "priority": "must_fix", "reviewer": ["eic", "methodology", "domain", "perspective", "da"], "sub_claims": ["SC-8"], "severity": "major", "confidence": 5, "evidence_anchor": "text: Abstract and §3.2 — 'Fourteen administrators were interviewed in depth'; 'Twelve senior administrators (n=12)'", "verification_criteria": "A single N stated consistently; discrepancy explained; relation to the §4.3 exclusions stated."},
    {"id": "R9", "priority": "must_fix", "reviewer": ["methodology", "domain", "eic", "da"], "sub_claims": ["SC-13", "SC-14"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.2–§3.4 and §4.4 — expected sampling frame, response rate, per-institution counts, scale anchors, item count, reliability", "verification_criteria": "Frame, invitation and response rates, per-site counts reconciling to 48 reported; instrument appended with anchors, item count, provenance and reliability."},
    {"id": "R10", "priority": "must_fix", "reviewer": ["domain", "perspective"], "sub_claims": ["SC-16a", "SC-16b", "SC-25"], "severity": "critical", "confidence": 5, "evidence_anchor": "absence: §2 — expected engagement with the pre-2018 quality-culture canon and the decoupling/ceremonial-conformity/audit-culture literatures", "verification_criteria": "Both literatures engaged or explicitly ruled out; 'long-standing concerns' cites long-standing work; gap claim restated; search strategy disclosed with databases, strings, limits, criteria and dates."},
    {"id": "R11", "priority": "must_fix", "reviewer": ["eic", "domain", "perspective"], "sub_claims": ["SC-17"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.2 — 'three universities in a single national system'", "verification_criteria": "System, regime, agency, review cycle, consequences and fieldwork period stated, with the institution-anonymity trade-off against R4 reasoned explicitly."},
    {"id": "R12", "priority": "must_fix", "reviewer": ["methodology", "eic"], "sub_claims": ["SC-19"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §5 and §6 — expected a limitations statement covering three-site scope, single national system, recruitment through institutional QA offices, and small subgroup sizes", "verification_criteria": "Limitations section names three-site scope, single system, gatekeeper-mediated recruitment, disclosed exclusions and small subgroup cells."},
    {"id": "S1", "priority": "should_fix", "reviewer": ["methodology", "perspective", "da"], "sub_claims": ["SC-11"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §4.4 — 'The survey corroborated the qualitative picture'; 'had led us to anticipate a more skeptical picture'", "verification_criteria": "Design typology, integration point and joint display stated; 'corroborated' retracted and the divergence reported as a finding."},
    {"id": "S2", "priority": "should_fix", "reviewer": ["domain", "perspective"], "sub_claims": ["SC-22"], "severity": "major", "confidence": 4, "evidence_anchor": "text: §4.2 and §4.3 — 'This relational, distributed understanding of leadership recurred across every interview'; 'This vocational framing appeared to function as a coping resource'", "verification_criteria": "Both constructs engaged with their source literatures and shown to meet their criteria, or relabelled descriptively."},
    {"id": "S3", "priority": "should_fix", "reviewer": ["eic", "domain"], "sub_claims": ["SC-15a", "SC-15b"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §1–§4.4 — expected a stated definition and operationalization of quality culture separating it from quality assurance, accreditation and audit", "verification_criteria": "One definition adopted and one referent held across §1, §4.4 and §5; QA/enhancement, internal/external and accreditation/audit/evaluation distinctions fixed; §1 gloss retained."},
    {"id": "S4", "priority": "should_fix", "reviewer": ["perspective", "da"], "sub_claims": ["SC-23"], "severity": "major", "confidence": 4, "evidence_anchor": "absence: §3.2 and §4 — expected accounts from academics, students or governance actors, and the occupational composition of the survey frame", "verification_criteria": "Additional vantage points added, or the object rescoped to administrators' accounts with the boundary condition stated. Panel did not resolve whether field convention permits the administrator-only design; an author response is required either way."},
    {"id": "S5", "priority": "should_fix", "reviewer": ["perspective"], "sub_claims": ["SC-24"], "severity": "major", "confidence": 4, "evidence_anchor": "absence: §5 third finding and §6 — expected at least one operational lever for quality offices or national agencies", "verification_criteria": "At least one concrete lever specified — workload recognition, professional development, or evidence-requirement design."},
    {"id": "S6", "priority": "should_fix", "reviewer": ["eic", "methodology"], "sub_claims": ["SC-20a", "SC-20b"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3 Methods and §4 Findings — expected interview protocol, participant characteristics table, coding examples with theme frequencies, survey instrument; and a data availability statement", "verification_criteria": "Interview guide, codebook and survey instrument appended; participant characteristics table supplied; materials and data-availability statement added."},
    {"id": "S7", "priority": "nice_to_fix", "source_kind": "editorial", "reviewer": ["eic"], "sub_claims": [], "severity": "minor", "verification_criteria": "Inline reference annotation removed; exhibits added; residual formatting corrected."}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

These cards were produced under a sprint contract and emit dimension scores rather than an overall Accept/Revise/Reject recommendation; confidence is recorded per finding rather than per report. Both are reported accordingly rather than inferred.

### Journal-Fit Reviewer (EIC) — scored D5, D6
- D5 `block`, D6 `block` (block_class: repairable) | 13 weaknesses, 4 strengths; per-finding confidence 4–5
- **Key point:** the increment claimed in §6 and the increment delivered in §4 are different papers; the defensible claim — a grounded empirical extension of Silva and Tan (2021) — would clear the venue's bar, but no recommendation should issue while the reference list is unverified.

### Reviewer 1 — Methodology — scored D1, D3
- D1 `block` (repairable), D3 `block` (repairable) | 13 weaknesses, 4 strengths; per-finding confidence 4–5
- **Key point:** the analytic procedures for both strands are described too thinly to be audited, and the manuscript documents the removal of disconfirming cases while asserting comprehensiveness — repairable in principle, but only by re-analysis, not rewriting.

### Reviewer 2 — Domain — scored D2
- D2 `block` (block_class: **fatal**) | 9 weaknesses, 3 strengths; per-finding confidence 4–5
- **Key point:** the field account rests on twelve unverifiable references whose DOI pattern is structurally impossible for real registration, and the one internally checkable citation claim is a reversal of the cited source's position; the gap and priority claims are false against a canon the manuscript does not cite.

### Reviewer 3 — Perspective (cross-disciplinary) — scored D4
- D4 `block` | 8 weaknesses, 3 strengths; per-finding confidence 4–5
- **Key point:** the paper's central finding is ceremonial conformity and policy–practice decoupling under a different name, presented as novel with the relevant traditions uncited; the §3.5/§4.1 anonymisation contradiction makes publication untenable in the present form independently of everything else.

### Devil's Advocate — scored D3
- D3 `block` (repairable) | 3 CRITICAL, 8 MAJOR; per-finding confidence 4–5
- **Key point:** three internal contradictions — circular warrant from the excluded cases, the inverted Delacroix attribution, and scope claims contradicted by §6's own call for wider research — each defeat the argument without recourse to any outside evidence.
- **Adjudications:** C1 VALIDATED (corroborated by all four non-DA seats), C2 VALIDATED (corroborated by EIC, Domain, Perspective), C3 VALIDATED (corroborated by EIC, Methodology, Perspective).
