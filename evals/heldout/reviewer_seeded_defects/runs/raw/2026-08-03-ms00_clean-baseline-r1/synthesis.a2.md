# Editorial Decision Package

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · panel_size 5
**Mode:** v3.6.2 Sprint Contract Synthesizer Protocol (arithmetic). The general Step 1b sub-claim inventory does not apply; consensus reporting below is descriptive and does not feed the decision arithmetic.

**Checker remediation:** the prior emission (`synthesis.a1.md`) failed `[SYNTHESIS-PARSE: expected exactly one fired_conditions line, found 0]`. The canonical audit block below emits exactly one line of each of the four required forms.

---

## Audit Emission (canonical)

audit_verdict: block(fatal)

dimension_verdicts: [D1=block, D2=block(fatal), D3=warn, D4=warn, D5=warn, D6=block]

fired_conditions: [F1, F2, F3, F5]

da_critical_adjudications: []

editorial_decision=reject

### Derivation (role-scoped, auditable)

**Step 1 — scoring matrix.** Only eligible seats counted; ineligible `not_assessed` values excluded from numerator and denominator.

| Dim | Priority | Eligible roles | Assessed eligible seats | Verdict |
|-----|----------|----------------|-------------------------|---------|
| D1 | mandatory | methodology | methodology = block (repairable) | block |
| D2 | mandatory | domain | domain = block, block_class fatal | block(fatal) |
| D3 | mandatory | da, methodology | da = warn; methodology = warn | warn |
| D4 | high | perspective | perspective = warn | warn |
| D5 | normal | eic | eic = warn | warn |
| D6 | mandatory | eic | eic = block (repairable) | block |

No dimension is unassessed by its eligible seats; no `[DIMENSION-UNASSESSED]` abort. No scoring-plan dissent was declared by any seat (the `eic` and `perspective` cards contain retracted dissent headings with no dissent content).

**Step 2 — failure conditions.**

| ID | Sev | Quantifier | Expression | Per-dimension result | Fired |
|----|-----|-----------|------------|----------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 F, **D2 T**, D3 F, D6 F | **yes** |
| F2 | 90 | any | any mandatory dimension scores 'block' | **D1 T**, **D2 T**, D3 F, **D6 T** | **yes** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 T (n=1, owner), D2 T (n=1, owner), D3 T (n=2, both seats warn), D6 T (n=1, owner) → 4 ≥ 2 | **yes** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 = warn, not block | no |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1 T | **yes** |
| F0 | 10 | all | every dimension scores 'pass' | D1 block | no |

**Step 3 — precedence.** Highest severity among fired conditions = F1 (95) → `editorial_decision=reject`. The DA's CRITICAL band is empty by the DA's own explicit finding, so `da_critical_adjudications` is `[]`; no `C<n>` rejection rationale is owed, and no `[DA-CRITICAL-VS-ACCEPT]` marker applies (decision is not accept).

**Note on the empty DA CRITICAL band.** The DA states it found no singleton defect capable of invalidating the central claim. That is a finding about the P3→C1 inferential link only. It is not evidence of manuscript soundness and does not offset the D2 fatal block, which the DA did not assess.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript "Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students." It was assessed by five reviewers: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary/practitioner), and a Devil's Advocate.

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this synthesis was invoked in `reviewer_full` mode without a dispatching-layer provenance stamp. The block is mandatory in this mode and may not be inferred, so no statement of cross-model slot status, single-family composition, or dispatch-failure fallback is asserted here. **The dispatching layer must supply the stamp and this block must be completed before the letter is issued to the author.** Readers should not infer model independence, or its absence, from this omission.

### Decision: Reject

This decision is mechanical under the sprint contract: condition F1 fired (a mandatory dimension carries a fatal block), and F1 carries the highest severity among the four fired conditions. Three further conditions fired independently (F2, F3, F5), each of which would have produced Major Revision on its own.

### Consensus Analysis

#### Points of Agreement (Consensus)

- **[CONSENSUS-4] Inferential restraint is genuine and correctly targeted (strength).** All four non-DA reviewers independently credit the same passage: the reverse-causation pathway is stated as an equally supported reading rather than gestured at, and no causal verb enters the substantive claims. The Devil's Advocate confirms the numbers reconcile (Fisher-z on r = .42 at n = 214 reproduces [.30, .52]) and that the causal disclaimer is in the abstract rather than buried. This is not a courtesy finding; it is the manuscript's real asset and should survive any future version.
- **[CONSENSUS-4] The comparability / "incremental data point" claim is not substantiated as written.** All four non-DA reviewers reach this conclusion, by two different routes: the Journal-Fit Reviewer, methodology, and domain seats locate the failure in the absent effect-size benchmark (no prior or pooled estimate appears anywhere, so r = .42 is unlocatable); the perspective seat locates it in the absent site characterisation (the reader cannot tell what kind of site this point came from). The DA adds that as written the claim is unfalsifiable, since any positive coefficient of any magnitude would satisfy it.
- **[CONSENSUS-3] The reference base is below the floor for the submitted article type.** Journal-Fit and domain both find six sources, all 2018–2021, none synthetic or meta-analytic, inadequate for a thirty-year literature; domain adds the absence of foundational acceptance work, UTAUT-family work, post-2021 studies, and learning-analytics work on behavioural LMS measures. Methodology and perspective are silent on this point.
- **Corroborated finding (2/4, no conflict): the instrument adaptation is undocumented.** Methodology and domain converge from different standards — reliability is not structural validity (α = .88 does not establish dimensionality for six adapted items), and adaptation suspends whatever validation the source instrument carried. Both find the Abstract's "previously validated instrument" claim unearned as stated.
- **Corroborated finding (2/4, no conflict): sample accounting is transparently itemised (strength).** Journal-Fit and perspective both credit the received/excluded/analysed breakdown. See the arbitration note below: this credit is in unresolved tension with the deduplication finding.
- **Single-reviewer findings carrying full weight (Confidence 5, factual and checkable):** the anonymity-versus-deduplication contradiction (methodology, corroborated by DA); the missing enrollment denominator and response rate (methodology, corroborated by DA, who sharpens it into possible selection on the dependent variable); the unverifiable citation base (domain).

#### Points of Disagreement

**1. Status of the reference base: repairable shortfall or integrity matter?**
The Journal-Fit Reviewer judges the six references "fixable in revision rather than disqualifying," on the grounds that the works present are "used precisely rather than ornamentally." The domain reviewer, to whom reference verification was assigned, finds the citation base unverifiable and scores it a fatal block: all six DOIs sit on the `10.5555` registration-agency test prefix, a DOI prefix is assigned per registrant so six articles in six differently-named journals cannot legitimately share one, the suffixes run sequentially (2050001–2050006) in reference-list order, and the journal titles read as near-variants of real venues.

> **Editor's Resolution: the domain finding prevails; the manuscript is rejected on this basis.** Arbitrated on evidence first and expertise second. The Journal-Fit Reviewer assessed reference-base *adequacy* and did not perform verification, which was not in that seat's remit; the characterisation "used precisely rather than ornamentally" presupposes that the sources exist, which is exactly what is in question. The domain reviewer supplies internal, checkable evidence at Confidence 5 that does not depend on external lookup. These are not competing readings of the same evidence — one seat evaluated a question the other did not open. **This is recorded as an integrity matter for the editor, not a revision request.** Every substantive domain claim in the manuscript routes through these six entries: the construct definition, the instrument's prior validation, the reverse-causality caution, the self-report caution, the cross-campus variability claim, and the onboarding implication. If they cannot be resolved, the paper's account of the field is not evaluable and its central contribution claim has nothing to attach to.

**2. Ethics reporting: complete, or internally contradictory?**
The Journal-Fit Reviewer credits §3.3 as "crisp and complete." Methodology and the DA find §3.1 and §3.3 mutually exclusive: five submissions were classified as duplicates under a stated procedure in which no identifying information was collected and responses could not be linked to individuals.

> **Editor's Resolution: not a genuine dispute; the contradiction stands.** The Journal-Fit Reviewer explicitly scoped out the methods audit and credited the *completeness of the reporting surface*, not its internal consistency. Methodology owns this territory and its finding is unopposed. Both possible resolutions have consequences: either quasi-identifiers were retained, in which case the anonymity statement made to readers and implicitly to the ethics committee requires correction, or the duplicate rule was heuristic and undisclosed, in which case an exclusion criterion that changed the analysed n is unreported. The five records are immaterial to r = .42; the unresolved contradiction in a compliance statement is not.

**3. Direction of revision: three incompatible expansion demands.**
Methodology asks for measurement apparatus (dimensionality check, attenuation-aware treatment, descriptive breakdown); domain asks for theoretical and literature expansion (foundational sources, UTAUT family, post-2021 work, corrected estimand); perspective asks for data sources and context variables (log validation, platform identity, contextual determinants). The Journal-Fit Reviewer's position implies the opposite move — re-type as a research note, under which most expansion demands become out of scope.

> **Editor's Resolution: unresolved dissent, recorded rather than averaged.** The panel did not resolve this and the editor does not resolve it here, because it cannot be settled on the present record: the arbitration mechanism the Journal-Fit Reviewer proposes (declare the article type, then scope expansion to it) is itself contingent on a literature base that is currently unverifiable. Each of the three demands is individually reasonable and together they would produce a different and much larger study. **If the citation base is resolved and the work is prepared for submission elsewhere, the authors must first declare the target article type (roadmap item R11) and then justify their scoping decisions against it in the response letter.** No reviewer's expansion demand is dismissed by this letter, and none is endorsed as mandatory beyond the items listed as Required below.

### Decision Rationale

The reject is driven by one fatal block, not by an accumulation of ordinary revision requests. The domain reviewer's verification finding — six references on a registration-agency test prefix, with sequential suffixes in list order and near-miss journal titles — is checkable on the manuscript's face and does not depend on external lookup. Because every substantive claim about the field routes through those six entries, the manuscript's stated contribution ("an incremental data point, comparable with prior work") has no map on which to sit, and its "previously validated" instrument has no traceable validation. A revision round cannot resolve this on the current record; it requires the authors to establish what their sources actually are.

Three further conditions fired independently, and it matters that they did, because the decision does not rest on the citation issue alone. The methodology block rests on three load-bearing elements a reader needs and cannot get: no enrollment denominator (hence no response rate, hence an unbounded nonresponse concern the authors concede only qualitatively), an undocumented instrument adaptation, and a deduplication procedure the stated anonymity conditions appear to preclude. The venue-fit block rests on a contribution that is asserted rather than located: the paper invokes cross-institutional variability to frame its estimate as one point in a distribution, then never describes the distribution.

The panel is clear that this is a competently executed and honestly framed piece of work whose inferential discipline exceeds the median of its class. That assessment is unanimous and is not softened by this decision. But restraint about a claim's strength is not a substitute for stating what the claim adds, and clean reporting of a coefficient does not discharge the obligation to show that the sources it is compared against exist.

### Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire citation base is unverifiable — all six DOIs on the `10.5555` test prefix, sequential suffixes in list order, unrecognisable journal titles; every domain claim routes through these entries (D2 fatal block) | R2 (domain) | `text: §References, first and last entries, "10.5555/2050001" and "10.5555/2050006"` | R1 |
| 2 | Three load-bearing methods elements absent or self-contradictory — no sampling denominator, undocumented instrument adaptation, deduplication incompatible with stated anonymity (D1 block) | R1 (methodology), corroborated by DA | `text: §3.1 and §3.3 "5 duplicate entries were removed" versus "No identifying information was collected, and responses could not be linked back to individual students"` | R2 (with R3, R4) |
| 3 | Contribution claim never benchmarked and reference base below the floor for the submitted article type (D6 block) | EIC, R2 (domain), DA | `absence: §2 Literature Review and §5 Discussion — expected quantitative benchmarking of r = .42 against pooled acceptance-model meta-analytic estimates; checked Abstract, §2, §4, §5, §7, References` | R5 |

### Venue routing (conditional, attributed)

The panel configuration input identified *Research in Learning Technology*, *Journal of Information Technology Education: Research*, and *Education and Information Technologies* as structurally plausible destinations for a bounded single-site correlational note, and explicitly excluded *Computers & Education*, *BJET*, *IJETHE*, and *Online Learning* at current scope. That routing is recorded here for the authors' use, not endorsed as an assessment of this manuscript. **It is conditional on R1: no version of this work should be submitted anywhere until the citation base is established.**

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column is `—` throughout: this synthesis ran in sprint-contract arithmetic mode, in which the Step 1b sub-claim inventory does not apply. Items are keyed to reviewer findings and carry each finding's transported severity, evidence anchor, and confidence.
>
> Because the decision is Reject, these are requirements for any future resubmission, not a revise-and-resubmit invitation. R1 is a precondition on all others: if the cited works cannot be established as existing, items R5, R6, and R7 change in character rather than in degree.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Establish the citation base: supply resolvable DOIs and verifiable bibliographic records for all six sources, or replace them and rebuild every claim that routed through them | — | Critical | `text: §References, first and last entries, "10.5555/2050001" and "10.5555/2050006"` | 5 — reference verification and DOI-prefix administration are routine first-pass work for this seat | R2 (domain) | P1 | Unbounded — days if anonymisation artefact, weeks-to-months if the framing must be rebuilt |
| R2 | Reconcile the deduplication procedure with the anonymity statement; correct whichever of the two is inaccurate | — | Major | `text: §3.1 and §3.3 "5 duplicate entries were removed" versus "No identifying information was collected, and responses could not be linked back to individual students"` | 5 — routine survey data-handling and human-subjects reporting review | R1 (methodology); DA M4 (conf 4) | P1 | 1–2 days, plus any ethics-committee correction |
| R3 | Report total eligible enrollment and the computed response rate; disclose the recruitment channel's relationship to the LMS and address possible selection on the outcome | — | Major | `absence: §3.1 Design and participants — expected total eligible enrollment and a computed response rate; checked §3.1, §3.4, §6, and the abstract` | 5 — teaches survey sampling; response-rate reporting is baseline for eligibility-defined surveys | R1 (methodology); DA M1 (conf 4) | P1 | 2–3 days |
| R4 | Document the instrument adaptation: reproduce administered items, state changes from the source and why, report a dimensionality check on the six items; hedge or earn the Abstract's "previously validated" claim | — | Major | `text: §3.2 Measures "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"` | 5 — psychometrics background; adaptation documentation is standard for a borrowed scale | R1 (methodology W3/W8); R2 (domain W6, conf 4) | P1 | 3–5 days (uses data in hand) |
| R5 | Benchmark r = .42 against stated prior or pooled estimates on matched estimands; state explicitly what the increment is | — | Major | `absence: §2 Literature Review and §5 Discussion — expected quantitative benchmarking of r = .42 against pooled acceptance-model meta-analytic estimates; checked Abstract, §2, §4, §5, §7, References` | 5 — editorial familiarity with the acceptance-model literature stock | EIC W1; R2 (domain W3, conf 4); DA M2 (conf 5) | P1 | 1–2 weeks (literature work, no new data) |
| R6 | Expand and correct the literature base (foundational acceptance work, UTAUT family, post-2021 LMS-use studies, learning-analytics behavioural-measure work); restore correct construct provenance and either justify or drop the perception→use shortcut that omits the intention mediator | — | Major | `text: §2 Literature Review, "perceived usefulness — the degree to which a person believes a technology will help them perform better", "is among the factors associated with adoption and continued use"` | 5 — canonical instrument lineage and mediation structure are this seat's core area | R2 (domain W2/W4, conf 5/4); EIC W2 (conf 5) | P1 | 2–3 weeks |
| R7 | Acknowledge attenuation from the coarse single-item outcome and carry it into interpretation and any comparability claim; correct the framing of the Spearman check, which addresses monotonicity and normality but not coarseness or unreliability | — | Major | `text: §4 Results "indicating that the association did not depend on the parametric assumption"` | 4 — direct specialization in single-item self-report measurement; magnitude unknown without the item distribution | R1 (methodology W4) | P1 | 2–3 days (textual minimum) |
| R8 | Address confounding by a common cause in §5 and §6, and narrow the comparability and cross-site framing to what was observed — either measure the contextual determinants or restrict the claim | — | Major | `text: §4 "including course requirements and assessment schedules"` | 5 — daily operational knowledge of what drives institutional LMS access frequency | R3 (perspective W3); DA M3 (conf 4) | P1 | 3–5 days if reframed; weeks if measured |
| R9 | Substantiate or remove the onboarding implication: state plainly that the correlation neither supports nor tests it, strike it from the Abstract, and reframe it in §5 as a hypothesis requiring a design study | — | Major | `text: §5 "modest support for the intuition that LMS onboarding which helps students see concrete usefulness"` | 4 — designs, budgets, and evaluates the onboarding programmes this recommendation targets | R3 (perspective W2) | P1 | 1 day |
| R10 | State why behavioural log data was not obtained or why a consented validation subsample was infeasible — governance refusal, ethics constraint, anonymity trade-off, or scope decision | — | Major | `absence: §6 Limitations and §3.3 Procedure and ethics — expected a stated reason log data was unavailable or subsample validation infeasible; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §4, §5, §6, §7` | 5 — operates the LMS, owns its clickstream, and processes the required governance and ethics approvals | R3 (perspective W1) | P1 | 1 day |
| R11 | Declare the target article type and argue for it (or re-type as a research note), and replace the recurring modesty framing with an explicit contribution statement | — | Major | `text: Abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates"` | 4 — sufficiency and article-type calls are venue-relative | EIC W3 | P1 | 2–3 days |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | Report the LMS platform identity and where the three-week window fell in the academic term | — | Minor | `absence: §3.1 Design and participants — expected the LMS platform identity and the position of the three-week window in the academic term; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §4, §6` | 4 — routinely assesses whether other institutions' learning-analytics findings transfer | R3 (perspective W4) | P2 | 1 hour |
| S2 | Supply descriptive exhibits: year-level composition, use-item frequency distribution with full response anchors, and the scatterplot the §3.4 assumption check relies on | — | Minor | `absence: §4 Results and §3.4 Analysis — expected at least one table or figure, including the scatterplot cited for the linearity and outlier check; checked Abstract through §7 and all section bodies` | 5 — direct inspection of the submitted text for exhibits and callouts | EIC W4; R1 (methodology W6, conf 4) | P2 | 1–2 days |
| S3 | Report shared variance numerically (≈18%) rather than describing it as "modest" | — | Minor | `text: §4 Results "The proportion of variance shared by the two measures was accordingly modest"` | 4 — reporting-convention check against standard quantitative expectations | EIC W5; DA (e) | P3 | 15 minutes |
| S4 | Reframe the power statement as a post hoc sensitivity bound rather than a design property; state alpha once and consistently; note that ≈215 cases are needed for .80 power at r = .19 | — | Minor | `text: §3.4 Analysis "the study had greater than .80 power to detect a correlation of r >= .19"` | 4 — routine power/sensitivity reporting | R1 (methodology W7); DA (d) | P2 | 2 hours |
| S5 | Add a data and code availability statement and name the analysis software and version | — | Minor | `absence: §3.4 Analysis and §7 Conclusion — expected a data/code availability statement and named analysis software or package versions; checked §3.2, §3.3, §3.4, §7, and the reference list` | 4 — routine venue-reporting expectation; appropriate level depends on target journal policy | R1 (methodology W5) | P3 | 2 hours |
| S6 | Correct the recasting of self-report/log divergence into a "perceived use" construct claim, and address the common-method coupling that follows if the outcome is treated as a perception | — | Minor | `text: §2 Literature Review, "studies relying on self-report capture perceived rather than actual engagement"` | 4 — familiar with how the log-comparison literature states its own findings | R2 (domain W5) | P2 | 3 hours |
| S7 | Fix construct drift: the Abstract's closing "LMS engagement" and §5's "factors bearing on engagement" upgrade the measured variable beyond §2's own commitment to treat it as perceived use | — | Minor `[SEVERITY-SOURCE: letter-fallback]` | `text: Abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates"` | 4 `[CONFIDENCE-SOURCE: report-level]` | DA (a) | P3 | 30 minutes |
| S8 | Merge §6 into §5 or reserve §5 for interpretation; cut the fourfold restatement of r = .42 across Abstract, §4, §5, §7 | — | Minor | `text: §6 Limitations "Third, the cross-sectional design precludes any causal or temporal inference."` | 4 — structural read of section functions and overlap | EIC W6 | P3 | 3 hours |

### Required Item Details

**R1 — Establish the citation base.**
- **Acceptance criteria**: Every reference resolves to a verifiable published record (working DOI on a live registrant prefix, or an equivalent locator), or is replaced; and every claim in §1, §2, §3.2, §5, and §6 that cited a removed source is either re-grounded in a verified source or withdrawn.

**R2 — Reconcile deduplication with anonymity.**
- **Acceptance criteria**: §3.1 states the mechanism by which duplicates were identified, and §3.3 accurately describes what data that mechanism required, with any resulting correction to the ethics statement disclosed to the editor.

**R3 — Report the denominator, response rate, and recruitment channel.**
- **Acceptance criteria**: §3.1 reports total eligible undergraduate enrollment for the survey window and the computed response rate, states whether the course-announcement channel was delivered through or driven by the LMS, and §6 discusses selection on the outcome rather than generic volunteer bias alone.

**R4 — Document the instrument adaptation.**
- **Acceptance criteria**: The six administered items appear in the paper or a supplement, the changes from the source instrument and their rationale are stated, a dimensionality check on the six items is reported, and the Abstract's validation language matches what §3.2 establishes.

**R5 — Benchmark the coefficient.**
- **Acceptance criteria**: At least one prior or pooled effect-size estimate is stated with its estimand and source, r = .42 is located relative to it, and the paper states in one sentence what a reader knows after this study that they did not know before.

**R6 — Expand the literature base and correct the construct account.**
- **Acceptance criteria**: §2 cites foundational acceptance-model work, UTAUT-family work, post-2021 LMS-use work, and learning-analytics work on behavioural measures; the perceived-usefulness definition is attributed to its origin; and the omission of the intention mediator is either named and justified or the comparison target is restated.

**R7 — Carry attenuation into the interpretation.**
- **Acceptance criteria**: §3.2 or §4 states that the five-category outcome and its unmodeled unreliability attenuate the observable coefficient, §4 no longer presents the Spearman check as addressing the measurement-level concern, and any comparability claim in §5 is qualified for estimand and metric.

**R8 — Address confounding and narrow the transfer claim.**
- **Acceptance criteria**: §5 or §6 names confounding by a common cause as an unaddressable limitation of a two-variable design, the Results attribution to course requirements and assessment schedules is relocated or marked as unmeasured, and the cross-site comparability framing is narrowed to what the reported site characteristics support.

**R9 — Substantiate or remove the onboarding implication.**
- **Acceptance criteria**: The onboarding recommendation no longer appears in the Abstract, and §5 states explicitly that the reported correlation neither supports nor tests it and presents it as a hypothesis for a design study.

**R10 — Explain the absence of log validation.**
- **Acceptance criteria**: §3 or §6 states the specific reason behavioural log data was not obtained and why a consented validation subsample was infeasible, or records that it was a scope decision.

**R11 — Declare and argue the article type.**
- **Acceptance criteria**: The manuscript names its target article type and gives a one-paragraph justification tied to its evidentiary mass, and the recurring "modest / incremental / design-bounded" phrasing is replaced by an explicit statement of the contribution's size.

### Revision Checklist

#### Priority 1 — Structural (estimated total effort: 6–10 weeks, excluding R1, which is unbounded)
- [ ] R1: Establish or replace the entire citation base *(precondition on R5, R6, R7)*
- [ ] R2: Reconcile deduplication with the anonymity statement
- [ ] R3: Report enrollment denominator, response rate, and recruitment channel
- [ ] R4: Document the instrument adaptation and dimensionality
- [ ] R5: Benchmark r = .42 against stated prior estimates
- [ ] R6: Expand the literature base; correct construct provenance and the estimand
- [ ] R7: Acknowledge and carry through outcome attenuation
- [ ] R8: Address confounding; narrow the comparability framing
- [ ] R9: Substantiate or remove the onboarding implication
- [ ] R10: State why log validation was not performed
- [ ] R11: Declare and argue the article type

#### Priority 2 — Content supplementation (estimated total effort: 2–3 days)
- [ ] S1: Report platform identity and term position
- [ ] S2: Supply descriptive tables and the scatterplot
- [ ] S4: Reframe the power statement as post hoc sensitivity
- [ ] S6: Correct the self-report construct recasting; address common-method coupling

#### Priority 3 — Text and formatting (estimated total effort: 1 day)
- [ ] S3: Report shared variance numerically
- [ ] S5: Add data/code availability and named software
- [ ] S7: Fix "engagement" construct drift
- [ ] S8: Merge Limitations into Discussion; cut restatement

### Revision Deadline

Not applicable — this is a Reject, not a revise-and-resubmit. R1 must be resolved before any resubmission is prepared for this or any other venue. If R1 resolves favourably, the P1 set is a 6–10 week programme.

### Response Letter Template

If the work is resubmitted elsewhere, use `templates/revision_response_template.md` and respond to every item R1–R11 and S1–S8 individually. The response to R11 must also address the unresolved expansion dissent recorded above: state the chosen article type and justify, against it, which of the methodology, domain, and perspective expansion demands were adopted and which were scoped out.

---

### Roadmap — machine form (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "reject",
  "items": [
    {"id": "R1", "priority": "must_fix", "verification_criteria": "Every reference resolves to a verifiable published record or is replaced; every claim citing a removed source is re-grounded or withdrawn.", "reviewer": ["domain"], "severity": "critical", "evidence_anchor": "text: §References, first and last entries, \"10.5555/2050001\" and \"10.5555/2050006\"", "confidence": 5, "source_kind": "reviewer_finding"},
    {"id": "R2", "priority": "must_fix", "verification_criteria": "§3.1 states the duplicate-identification mechanism; §3.3 accurately describes the data it required; any ethics-statement correction is disclosed.", "reviewer": ["methodology", "da"], "severity": "major", "evidence_anchor": "text: §3.1 and §3.3 \"5 duplicate entries were removed\" versus \"No identifying information was collected, and responses could not be linked back to individual students\"", "confidence": 5, "source_kind": "reviewer_finding"},
    {"id": "R3", "priority": "must_fix", "verification_criteria": "§3.1 reports total eligible enrollment and response rate and the channel's relationship to the LMS; §6 addresses selection on the outcome.", "reviewer": ["methodology", "da"], "severity": "major", "evidence_anchor": "absence: §3.1 Design and participants — expected total eligible enrollment and a computed response rate; checked §3.1, §3.4, §6, and the abstract", "confidence": 5, "source_kind": "reviewer_finding"},
    {"id": "R4", "priority": "must_fix", "verification_criteria": "Administered items published; adaptation changes and rationale stated; dimensionality check reported; Abstract validation language matches §3.2.", "reviewer": ["methodology", "domain"], "severity": "major", "evidence_anchor": "text: §3.2 Measures \"a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency\"", "confidence": 5, "source_kind": "reviewer_finding"},
    {"id": "R5", "priority": "must_fix", "verification_criteria": "At least one prior/pooled estimate stated with estimand and source; r = .42 located relative to it; increment stated in one sentence.", "reviewer": ["eic", "domain", "da"], "severity": "major", "evidence_anchor": "absence: §2 Literature Review and §5 Discussion — expected quantitative benchmarking of r = .42 against pooled acceptance-model meta-analytic estimates; checked Abstract, §2, §4, §5, §7, References", "confidence": 5, "source_kind": "reviewer_finding"},
    {"id": "R6", "priority": "must_fix", "verification_criteria": "§2 cites foundational, UTAUT-family, post-2021, and learning-analytics work; construct attributed to origin; intention-mediator omission named and justified or comparison target restated.", "reviewer": ["domain", "eic"], "severity": "major", "evidence_anchor": "text: §2 Literature Review, \"perceived usefulness — the degree to which a person believes a technology will help them perform better\", \"is among the factors associated with adoption and continued use\"", "confidence": 5, "source_kind": "reviewer_finding"},
    {"id": "R7", "priority": "must_fix", "verification_criteria": "Attenuation stated in §3.2 or §4; Spearman check no longer presented as addressing measurement level; §5 comparability qualified for estimand and metric.", "reviewer": ["methodology"], "severity": "major", "evidence_anchor": "text: §4 Results \"indicating that the association did not depend on the parametric assumption\"", "confidence": 4, "source_kind": "reviewer_finding"},
    {"id": "R8", "priority": "must_fix", "verification_criteria": "Common-cause confounding named as unaddressable in §5/§6; Results attribution relocated or marked unmeasured; cross-site framing narrowed to reported site characteristics.", "reviewer": ["perspective", "da"], "severity": "major", "evidence_anchor": "text: §4 \"including course requirements and assessment schedules\"", "confidence": 5, "source_kind": "reviewer_finding"},
    {"id": "R9", "priority": "must_fix", "verification_criteria": "Onboarding recommendation removed from Abstract; §5 states the correlation neither supports nor tests it and reframes it as a hypothesis.", "reviewer": ["perspective"], "severity": "major", "evidence_anchor": "text: §5 \"modest support for the intuition that LMS onboarding which helps students see concrete usefulness\"", "confidence": 4, "source_kind": "reviewer_finding"},
    {"id": "R10", "priority": "must_fix", "verification_criteria": "§3 or §6 states the specific reason log data was unobtainable and why a consented validation subsample was infeasible, or records it as a scope decision.", "reviewer": ["perspective"], "severity": "major", "evidence_anchor": "absence: §6 Limitations and §3.3 Procedure and ethics — expected a stated reason log data was unavailable or subsample validation infeasible; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §4, §5, §6, §7", "confidence": 5, "source_kind": "reviewer_finding"},
    {"id": "R11", "priority": "must_fix", "verification_criteria": "Target article type named with a justification tied to evidentiary mass; modesty phrasing replaced by an explicit contribution statement.", "reviewer": ["eic"], "severity": "major", "evidence_anchor": "text: Abstract \"The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates\"", "confidence": 4, "source_kind": "reviewer_finding"},
    {"id": "S1", "priority": "should_fix", "verification_criteria": "§3.1 names the LMS platform and the position of the three-week window in the academic term.", "reviewer": ["perspective"], "severity": "minor", "evidence_anchor": "absence: §3.1 Design and participants — expected the LMS platform identity and the position of the three-week window in the academic term; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §4, §6", "confidence": 4, "source_kind": "reviewer_finding"},
    {"id": "S2", "priority": "should_fix", "verification_criteria": "At least one descriptive table (year-level composition, use-item distribution with full anchors) and the scatterplot cited in §3.4 appear in the manuscript.", "reviewer": ["eic", "methodology"], "severity": "minor", "evidence_anchor": "absence: §4 Results and §3.4 Analysis — expected at least one table or figure, including the scatterplot cited for the linearity and outlier check; checked Abstract through §7 and all section bodies", "confidence": 5, "source_kind": "reviewer_finding"},
    {"id": "S3", "priority": "nice_to_fix", "verification_criteria": "§4 reports shared variance as a number rather than as a verbal characterisation.", "reviewer": ["eic", "da"], "severity": "minor", "evidence_anchor": "text: §4 Results \"The proportion of variance shared by the two measures was accordingly modest\"", "confidence": 4, "source_kind": "reviewer_finding"},
    {"id": "S4", "priority": "should_fix", "verification_criteria": "§3.4 frames the computation as post hoc sensitivity, states alpha once consistently, and corrects the .80-power threshold statement.", "reviewer": ["methodology", "da"], "severity": "minor", "evidence_anchor": "text: §3.4 Analysis \"the study had greater than .80 power to detect a correlation of r >= .19\"", "confidence": 4, "source_kind": "reviewer_finding"},
    {"id": "S5", "priority": "nice_to_fix", "verification_criteria": "A data/code availability statement and named analysis software with version appear in the manuscript.", "reviewer": ["methodology"], "severity": "minor", "evidence_anchor": "absence: §3.4 Analysis and §7 Conclusion — expected a data/code availability statement and named analysis software or package versions; checked §3.2, §3.3, §3.4, §7, and the reference list", "confidence": 4, "source_kind": "reviewer_finding"},
    {"id": "S6", "priority": "should_fix", "verification_criteria": "§2 states the log-comparison finding as measurement divergence rather than as a separate construct, and common-method coupling is addressed where the outcome is treated as a perception.", "reviewer": ["domain"], "severity": "minor", "evidence_anchor": "text: §2 Literature Review, \"studies relying on self-report capture perceived rather than actual engagement\"", "confidence": 4, "source_kind": "reviewer_finding"},
    {"id": "S7", "priority": "nice_to_fix", "verification_criteria": "Abstract and §5 no longer use \"engagement\" for the measured variable where §2 committed to \"perceived use\".", "reviewer": ["da"], "severity": "minor", "severity_source": "letter-fallback", "evidence_anchor": "text: Abstract \"The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates\"", "confidence": 4, "confidence_source": "report-level", "source_kind": "reviewer_finding"},
    {"id": "S8", "priority": "nice_to_fix", "verification_criteria": "The three cautions appear once rather than in both §5 and §6, and r = .42 is not restated in four separate sections.", "reviewer": ["eic"], "severity": "minor", "evidence_anchor": "text: §6 Limitations \"Third, the cross-sectional design precludes any causal or temporal inference.\"", "confidence": 4, "source_kind": "reviewer_finding"}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary
- Scored: D5 = warn, D6 = block (repairable). Other dimensions not assessed (out of seat scope).
- Key point: fit yes, sufficiency no — the manuscript is a research note submitted in full-article format, and its "incremental data point" claim is never quantified against the pooled record it claims comparability with. Explicitly scoped out the measurement audit and stated that a favourable journal-fit path would not discharge it.

### Peer Reviewer 1 (Methodology) Summary
- Scored: D1 = block (repairable), D3 = warn. Others not assessed.
- Key point: the analysis is the right analysis and the numbers reconcile; the block is documentary — no sampling denominator, no instrument documentation, and a deduplication statement that cannot coexist with the anonymity statement. Explicitly flagged its own disposition to over-request measurement machinery.

### Peer Reviewer 2 (Domain) Summary
- Scored: D2 = block, block_class fatal. Others not assessed.
- Key point: reference verification taken first because every domain judgement is downstream of it — all six DOIs sit on the `10.5555` test prefix with sequential suffixes across six differently-named journals, which cannot be legitimate. Secondary findings (estimand collapse, absent benchmark, literature currency) would require attention even with a clean reference list.

### Peer Reviewer 3 (Cross-disciplinary / practitioner) Summary
- Scored: D4 = warn. Others not assessed.
- Key point: legible and honestly hedged, but the onboarding implication is invariant to the result and is nonetheless carried into the Abstract; log data existed on the same server for the same population and window with no stated reason for its non-use; platform and term position are absent, which makes the single-site limitation unremediable rather than merely acknowledged.

### Devil's Advocate Summary
- Scored: D3 = warn. Others not assessed. CRITICAL band empty by finding; four MAJOR items.
- Key point: link P3→C1 holds and the arithmetic reconciles, but the recruitment channel may have selected on the dependent variable, the consistency claim is unfalsifiable as written, confounding by common cause is raised in §2 and then dropped from both §5 and §6, and §3.1 and §3.3 cannot both be true.

---

*Synthesis complete. This is the Phase 2 deliverable. Revision-side work (any redrafting) is a separate `academic-paper` Phase 6 invocation and is not performed here. Two items require action by the caller before this letter issues: (1) supply the `#540` provenance stamp, and (2) route the R1 citation-verification finding to the editor as an integrity matter rather than as a revision request.*
