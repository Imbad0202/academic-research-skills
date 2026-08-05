# Editorial Decision Package

## Sprint Contract Audit (v3.6.2 arithmetic mode)

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · panel_size 5 · baseline v3.20.0

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats | Excluded (ineligible / not_assessed) | Verdict |
|-----|----------|----------------|--------------------------|--------------------------------------|---------|
| D1 methodology_rigor | mandatory | methodology | methodology = block (repairable) | eic, domain, perspective, da → not_assessed | **block** |
| D2 domain_accuracy | mandatory | domain | domain = block (repairable) | eic, methodology, perspective, da → not_assessed | **block** |
| D3 argumentative_coherence | mandatory | da, methodology | da = block (repairable); methodology = block (repairable) | eic, domain, perspective → not_assessed | **block** |
| D4 cross_disciplinary_relevance | high | perspective | perspective = warn | all others → not_assessed | **warn** |
| D5 writing_and_structure | normal | eic | eic = block | all others → not_assessed | **block** |
| D6 venue_fit_and_contribution | mandatory | eic | eic = block, block_class **fatal** | all others → not_assessed | **block(fatal)** |

`audit_verdict: block(fatal)` — worst assessed eligible score is `block`, and one assessed eligible seat (eic, D6, mandatory) declared a fatal block.

No dimension had two eligible seats disagree on score: D3 is the only multi-eligible dimension and both eligible seats (da, methodology) returned `block` / `repairable`. No abstentions among eligible seats. No dimension was left unassessed by all eligible seats.

### Step 2 — Failure-condition evaluation

| ID | Sev | Cross-reviewer quantifier | Expression | Per-dimension booleans | Fired |
|----|-----|---------------------------|------------|------------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1=F, D2=F, D3=F, **D6=T** (eic declared fatal; D6 mandatory → fatal scope valid) | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1=T, D2=T, D3=T, D6=T | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1=T (n=1→owner), D2=T (n=1→owner), D3=T (n=2→both seats block), D6=T (n=1→owner) → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4=warn ≠ block → F | false |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1=T (and D2, D3, D4, D5, D6) | **true** |
| F0 | 10 | all | every dimension scores 'pass' | no dimension = pass | false |

### Step 3 — Precedence and emission

```
dimension_verdicts: [D1=block, D2=block, D3=block, D4=warn, D5=block, D6=block(fatal)]
fired_conditions: [F1, F2, F3, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED, C5=VALIDATED]
editorial_decision=reject
```

Highest severity among fired conditions is F1 (95) → `action: editorial_decision=reject`. No `[DA-CRITICAL-VS-ACCEPT]` marker applies (mechanical decision is not `accept`). No `C<n>=REJECTED`, so no rejection-rationale lines are required.

**DA CRITICAL adjudication basis** (all five corroborated by at least two non-DA seats on the manuscript's own text):

- **C1 VALIDATED** — N discrepancy corroborated by EIC W6, R1 W1, R3 W8, and R2 (body flag). The DA's narrower insinuation that the missing two *are* the excluded dissenters is explicitly not asserted by the DA and is not validated; the validated claim is that the evidence base is indeterminate and the exclusion unaccounted.
- **C2 VALIDATED** — Delacroix reversal corroborated by EIC W4, R1 W13, R2 W1, R3 W3.
- **C3 VALIDATED** — sector-wide scope violation corroborated by EIC W8, R1 W8, R2 W4, R3 W1.
- **C4 VALIDATED** — self-refuting balance claim and circular exclusion criterion corroborated by EIC W2, R1 W5, R2 W7, R3 W4.
- **C5 VALIDATED** — anonymisation contradiction corroborated by EIC W9, R1 W6, R2 W8 (R3 silent).

### Procedural flags (raised, not repaired)

- `[CARD-METADATA-INCOMPLETE]` The contract's `measurement_procedure.reviewer_must_output_before_paper` requires `contract_paraphrase` and `scoring_plan` for all dimensions. Those artefacts were **not included in the material forwarded to synthesis** (the perspective card references its Phase 1 block condition, implying a plan existed upstream). I cannot verify compliance and did not reconstruct it — flagged for the orchestrator.
- The eic card omits an explicit `block_class` on D5. No fatality classification is possible there in any case (fatal scope is valid only for mandatory dimensions; D5 is `normal`), so the matrix is unaffected.

---

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — No dispatching-layer provenance stamp was supplied with the five reviewer cards. I am not permitted to infer which of the three statements (cross-model slot active / single-family disclosure / dispatch-failure fallback) applies, and I have not selected one. Accordingly: **no claim of cross-family model independence is made for any seat in this panel.** Readers must not treat the five seats as independent model families. The orchestrator should attach the correct stamp before this letter is released.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled "Building Institutional Quality Culture: Administrator Perspectives on Quality Assurance Implementation in Universities." It was assessed by five reviewers: a Journal-Fit Reviewer, three peer reviewers (methodology; quality-assurance domain; cross-disciplinary/organizational sociology), and a Devil's Advocate reviewer.

### Decision: Reject

This decision follows the audit above. A fatal block was recorded on a mandatory acceptance dimension (D6, venue fit and contribution), which under the contract's highest-severity fired condition (F1) yields rejection. The decision is not a judgement that the underlying study is without value — three reviewers independently identified a genuine, publishable finding in §4.3 — and it is not a revision invitation. **Part 2 is supplied as constructive direction for any future resubmission or submission elsewhere, not as a revision cycle on this manuscript.**

The proximate reason is an integrity matter that precedes substantive assessment. All twelve references carry DOIs in the reserved `10.5555` test prefix, allocated as a single sequential block from `1042001` to `1042012`, and several named outlets and the named publisher do not correspond to indexed venues. Because the manuscript's originality claim is constructed entirely as a gap in that literature, an unverifiable reference base removes the premise on which any original claim rests. The corroborating internal signal, noted independently by four reviewers, is that §5 attributes to Delacroix (2018) the exact position that §2 and the reference-list annotation say Delacroix argues against. The required action is verification against Crossref and Scopus. If verification fails, this is an integrity referral rather than a revision request; no revision cycle can make a non-existent source exist.

### Consensus Analysis

Consensus is computed per sub-claim over the four non-Devil's-Advocate reviewers (Journal-Fit, R1 methodology, R2 domain, R3 perspective); the denominator is always 4, and silence is neither agreement nor opposition. Full inventory in Part 2a.

#### Points of Agreement (Consensus)

- **[CONSENSUS-4]** SC-2 — The interview sample size contradicts itself (Abstract: fourteen; §3.2: twelve, with `n=12`). One figure is wrong and nothing in the manuscript reconciles them.
- **[CONSENSUS-4]** SC-3 — §4.3 claims balanced representation capturing the full range of administrator views, and in the next sentence discloses that dissenting participants were excluded. The two claims cannot both stand.
- **[CONSENSUS-4]** SC-4 — The stated exclusion criterion is circular: cases were dropped *because* they fell outside the three-theme structure that the analysis was supposed to produce. The theme structure has therefore never been exposed to the evidence most capable of falsifying it.
- **[CONSENSUS-4]** SC-5 — §5 recruits Delacroix (2018) for the position §2 and the reference annotation say he argues against.
- **[CONSENSUS-4]** SC-7 — §5 generalises from three purposively recruited institutions in one national system to "universities across the sector," "the higher education sector as a whole," and "administrators everywhere," using the verb "demonstrate." The Conclusion's own call for wider testing concedes the point the Discussion overrode.
- **[CONSENSUS-4]** SC-10 — M=3.9 (SD=0.6) is carried into the Abstract with no response-scale range, item wording, item count, instrument provenance, or reliability/validity evidence. A mean without its scale is uninterpretable.
- **[CONSENSUS-4]** SC-23a — §4.1's "structured protocol" contradicts §3.1's "semi-structured interviews."
- **[CONSENSUS-4]** SC-23b — The inference from protocol structure to "the pattern was not an artifact of any single institution's local circumstances" does not follow; ruling out a site artifact would require per-site distribution of themes, which is never reported.
- **[CONSENSUS-3]** SC-13 — The §3.5 anonymisation guarantee is defeated by §4.1's role-plus-institution-type-plus-superlative attributions in a three-site, twelve-person design. (Silent: R3 perspective.)
- **[CONSENSUS-3]** SC-14 — "Quality culture" is never operationally defined and is never distinguished from quality assurance, accreditation compliance, or institutional climate, yet a survey mean is reported as a property of it. (Silent: R1 methodology.)
- **[CONSENSUS-3]** SC-15 — The Conclusion's "first comprehensive account" is refuted by the manuscript's own §2 (Pettersen 2022; Rahman 2020; Silva & Tan 2021). (Silent: R3 perspective.)
- **[CONSENSUS-3]** SC-6 — Correcting the Delacroix attribution empties §5's third implication of its only cited warrant, and Delacroix's actual argument is a live counterargument the study never answers. (Silent: Journal-Fit Reviewer.)

#### Corroborated findings (two reviewers, below the consensus bar)

SC-8 (level-of-analysis slippage: individuals → institutions → field), SC-11 (the §4.4 significance claim is not reportable and cannot license "institutional type as a possible moderator"), SC-12 (28 of 48 survey respondents unaccounted for; no per-institution counts, response rate, or explanation of the private university's absence), SC-19 (the national system and its QA regime are never named, though regime design is the operative variable), SC-20 (the two strands are adjacent, not integrated; §4.4 calls the survey corroborating one sentence before conceding it disconfirmed expectation), SC-22 (the interaction among the three themes — the paper's only real increment — is never developed), SC-24 (no limitations, data-availability, funding or conflict statements; no tables or figures anywhere).

#### Single-reviewer findings (weighted by confidence, no consensus label)

SC-1 reference-apparatus verifiability (Journal-Fit, Critical, confidence 5 — this is nonetheless the fatal-block driver, because D6 is exclusively Journal-Fit-eligible under the contract); SC-9 thematic analysis wholly undocumented (R1, Critical, confidence 5, owner seat for D1); SC-16 no engagement with the foundational quality-culture canon (R2, Major, confidence 5); SC-17 findings reinvent decoupling / institutional logics / identity work without naming them (R3, Major, confidence 5); SC-18 the external body, one of the paper's three named parties, is never characterised (R3, Major, confidence 5); SC-21 the administrator/staff asymmetry is the most operationally useful result and is deferred to future work (R3, Major, confidence 4); SC-25 Brennan & Osei (2020) is placed in the empirical strand though it is a conceptual synthesis (R2, Minor, confidence 4).

#### Points of Disagreement

- **SC-2b — severity of the N reconciliation.** R1 treats it as Major and requires the authors to confirm that no reported prevalence pattern changes under the corrected N; R3 treats it as "trivially fixable" (Minor).
  - **Editor's Resolution**: R1's treatment stands. Rationale: expertise first — sample integrity and prevalence denominators are the methodology seat's domain, and R1's confidence is 5. The DA's C1 additionally shows the discrepancy interacts with an admitted post-hoc exclusion, so the fix is not confined to a numeral. The remedies are compatible (both require stating the true N); only the follow-on obligation differs, and it is required.
- **SC-15b — remedy for the withdrawn priority claim.** R1 holds that "rewording costs the paper nothing" (Minor, confidence 4); R2 and the Journal-Fit Reviewer hold that withdrawing the claim forces a positive restatement of the increment against three cited works and the absent canon (Major, confidence 5 each).
  - **Editor's Resolution**: R2 and the Journal-Fit Reviewer stand. Rationale: expertise first (contribution assessment is the domain and journal-fit seats' remit) and evidence first (both cite the specific prior works the claim must now be positioned against). Deleting the sentence is necessary but not sufficient.
- **SC-23 — severity of the "structured protocol" defect.** R1 scores Major because the contradiction is put to work underwriting a confidence claim; the Journal-Fit Reviewer, R2, and R3 score Minor as a terminological inconsistency.
  - **Editor's Resolution**: decomposed rather than arbitrated away. The wording inconsistency (SC-23a) is Minor; the unwarranted artifact inference it supports (SC-23b) is Major. This is not a compromise — the Journal-Fit Reviewer (W11) and R2 (W9) both independently state that the confidence claim must be removed or re-grounded, which is Major treatment of the inference under a Minor label for the wording.
- **Positioning tension (not a dispute): SC-16 vs SC-17.** R2 requires anchoring in the higher-education quality-culture canon; R3 requires anchoring in the organization-studies apparatus that already names all three findings. Neither reviewer disputes the other, and R3 explicitly allows that "the HE field has developed equivalent apparatus in its own terms, in which case the authors should name that apparatus instead."
  - **Editor's Resolution**: this is a positioning decision the authors must make, not two independent required additions. R2's route (field journal + QA canon) is the lower-risk path to publication; R3's route (organization-studies framing + institutional theory) is the higher-ceiling contribution. Pick one and commit; a resubmission that gestures at both will satisfy neither readership. Recorded as S1, Priority 2.

#### Recorded panel-design limitation on the decision

I record this so the reader is not left to infer it. The fatality that produces this decision sits on D6, and under the contract D6 is eligible to the Journal-Fit seat alone; no other reviewer was eligible to corroborate or dissent on it. The reject therefore rests on one eligible seat, at confidence 5, on a check (DOI prefix allocation and index lookup) that is mechanical and independently repeatable rather than interpretive. The other three assessed blocks (D1, D2, D3) were all classified **repairable** by their eligible seats, which is why the substantive path forward in Part 2 is a major-revision roadmap rather than a closed door. The arbitration route for D6 is verification, not re-scoring. I have not softened the fired condition's action on that basis.

### Decision Rationale

Five reviewers, working from different competences, converged on the same picture: a well-written manuscript with one genuinely interesting finding, resting on an evidentiary chain that cannot currently be audited at any of its load-bearing joints. Four independent seats found the same four self-contradictions on the face of the text — fourteen versus twelve interviewees, full-range representation versus excluded dissenters, Delacroix against consultation versus Delacroix for consultation, full anonymisation versus a named single-occupant post. None of these requires domain expertise to detect, and none can be resolved by a reader.

Behind the contradictions sit two absences the methodology seat scored as blocking: the thematic analysis, which produced the paper's entire contribution, is described in three sentences with no named framework, coder count, agreement procedure, saturation criterion, audit trail, or reflexivity statement; and the survey instrument does not exist in the manuscript in any form that makes its headline mean interpretable. The §4.4 significance claim reports a p-value with no test, no statistic, no effect estimate and no assumption check on groups of nine and eleven, with twenty-eight respondents and one of three institutions absent from the comparison.

What determines the decision rather than the priority is the reference apparatus. Twelve sequential DOIs in a reserved test prefix, several unindexed outlets, and a Discussion that reverses a source the same manuscript summarised correctly two sections earlier, together mean that no literature-based claim here can be traced and the paper's stated gap cannot be confirmed to exist. That is a pre-review integrity matter. Verification must precede any further substantive assessment.

The study's merits, as the cards found them: §4.3's observation that administrators hold the compliance/meaning tension open and locate their professional identity in the gap was named by three reviewers as a real, non-obvious contribution; §2's staging of the participation-versus-performance debate is precise and correctly attributed; and the maximum-variation site design would have supported the institutional-type contrast §4.4 attempts, had that contrast been reported properly.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire reference list carries reserved `10.5555` test-prefix DOIs in one sequential block, with unindexed outlets; no cited claim is traceable, and the paper's originality premise is a gap in that untraceable literature | EIC | text: References list, "https://doi.org/10.5555/1042001" through "https://doi.org/10.5555/1042012", and "Journal of Higher Education Governance, 14" | R1 |
| 2 | Disconfirming cases excluded for not fitting the theme structure the analysis was meant to produce, while the same paragraph claims full-range representation — the three themes have never faced falsifying evidence | R1, EIC, R3, R2, DA (C4) | text: §4.3 "the study achieved balanced representation of perspectives, capturing the full range of administrator views" and "these were excluded for space, as they fell outside the three-theme structure" | R3 |
| 3 | §5's third implication is warranted by a source the manuscript itself reports as arguing the opposite; correcting it leaves the paper's only actionable recommendation without support | R2, R3, EIC, R1, DA (C2) | text: §5 "our findings align with Delacroix (2018), who recommends that institutions treat broad stakeholder consultation as the central mechanism" vs §2 "cautions that participatory rhetoric can itself become a compliance ritual" | R4 |

---

## Part 2a: Sub-Claim Inventory (Step 1b)

Rows are recorded for stated positions (`raised`, `corroborated`, `disputed`) only; `not-mentioned` reviewers are named in the disposition table's `silent` column rather than given empty rows, so silence remains visible to the count without a 100-row table. Severity and confidence are **transported** from the cards, never re-derived.

| sub_claim_id | parent_weakness | reviewer | position | evidence_pointer | severity | confidence |
|---|---|---|---|---|---|---|
| SC-1 | reference apparatus unverifiable | EIC | raised | EIC W1 | Critical | 5 |
| SC-2 | interview N contradictory | EIC | raised | EIC W6 | Major | 5 |
| SC-2 | " | R1 | corroborated | R1 W1 | Major | 5 |
| SC-2 | " | R2 | corroborated | R2 body, "flag without scoring" | `[SEVERITY-SOURCE: letter-fallback]` Major-equivalent | `[CONFIDENCE-SOURCE: report-level]` n/a — no per-finding or report-level score on this card |
| SC-2 | " | R3 | corroborated | R3 W8 | Minor | 5 |
| SC-2b | severity/follow-on of N fix | R1 | raised | R1 W1 "confirm that no reported pattern changes" | Major | 5 |
| SC-2b | " | R3 | disputed | R3 W8 "Trivially fixable" | Minor | 5 |
| SC-3 | balance claim vs exclusion | EIC | raised | EIC W2 | Critical | 5 |
| SC-3 | " | R1 | corroborated | R1 W5 | Critical | 5 |
| SC-3 | " | R2 | corroborated | R2 W7 | Major | 4 |
| SC-3 | " | R3 | corroborated | R3 W4 | Critical | 4 |
| SC-4 | circular exclusion criterion | R1 | raised | R1 W5 | Critical | 5 |
| SC-4 | " | EIC | corroborated | EIC W2 | Critical | 5 |
| SC-4 | " | R2 | corroborated | R2 W7 | Major | 4 |
| SC-4 | " | R3 | corroborated | R3 W4 | Critical | 4 |
| SC-5 | Delacroix reversal | R2 | raised | R2 W1 | Critical | 5 |
| SC-5 | " | EIC | corroborated | EIC W4 | Major | 5 |
| SC-5 | " | R1 | corroborated | R1 W13 | Major | 4 |
| SC-5 | " | R3 | corroborated | R3 W3 | Critical | 4 |
| SC-6 | correction empties the recommendation | R2 | raised | R2 W1 body | Critical | 5 |
| SC-6 | " | R3 | corroborated | R3 W3 | Critical | 4 |
| SC-6 | " | R1 | corroborated | R1 W13 "loses its stated warrant entirely" | Major | 4 |
| SC-7 | sector-wide overgeneralisation | R1 | raised | R1 W8 | Critical | 5 |
| SC-7 | " | EIC | corroborated | EIC W8 | Major | 5 |
| SC-7 | " | R2 | corroborated | R2 W4 | Major | 5 |
| SC-7 | " | R3 | corroborated | R3 W1 | Major | 5 |
| SC-8 | level-of-analysis slippage | R3 | raised | R3 W1 | Major | 5 |
| SC-8 | " | R1 | corroborated | R1 W8 | Critical | 5 |
| SC-9 | thematic analysis undocumented | R1 | raised | R1 W4 | Critical | 5 |
| SC-10 | survey instrument absent | R1 | raised | R1 W3 | Major | 5 |
| SC-10 | " | EIC | corroborated | EIC W7 | Major | 4 |
| SC-10 | " | R2 | corroborated | R2 W3 | Major | 5 |
| SC-10 | " | R3 | corroborated | R3 W7 | Major | 4 |
| SC-11 | §4.4 significance unreportable | R1 | raised | R1 W2 | Critical | 5 |
| SC-11 | " | EIC | corroborated | EIC W7 | Major | 4 |
| SC-12 | survey denominators unreconciled | R1 | raised | R1 W10 | Major | 5 |
| SC-12 | " | EIC | corroborated | EIC W7 | Major | 4 |
| SC-13 | anonymisation defeated | EIC | raised | EIC W9 | Critical | 5 |
| SC-13 | " | R1 | corroborated | R1 W6 | Major | 5 |
| SC-13 | " | R2 | corroborated | R2 W8 | Major | 4 |
| SC-14 | "quality culture" not operationalised | EIC | raised | EIC W5 | Major | 5 |
| SC-14 | " | R2 | corroborated | R2 W3 | Major | 5 |
| SC-14 | " | R3 | corroborated | R3 W7 | Major | 4 |
| SC-15 | priority claim refuted by own §2 | EIC | raised | EIC W3 | Major | 5 |
| SC-15 | " | R2 | corroborated | R2 W6 | Major | 5 |
| SC-15 | " | R1 | corroborated | R1 W12 | Minor | 4 |
| SC-15b | remedy for priority claim | R2 | raised | R2 W6 "a rewriting of the contribution argument, not a deletion" | Major | 5 |
| SC-15b | " | EIC | corroborated | EIC W3 "must be rebuilt against those three works" | Major | 5 |
| SC-15b | " | R1 | disputed | R1 W12 "Rewording costs the paper nothing" | Minor | 4 |
| SC-16 | QA canon absent | R2 | raised | R2 W2 | Major | 5 |
| SC-17 | org-studies concepts unnamed | R3 | raised | R3 W5 | Major | 5 |
| SC-18 | external body never opened | R3 | raised | R3 W2 | Major | 5 |
| SC-19 | national system / regime unnamed | R2 | raised | R2 W5 | Major | 5 |
| SC-19 | " | R3 | corroborated | R3 W2 | Major | 5 |
| SC-20 | strands adjacent, not mixed | R1 | raised | R1 W7 | Major | 5 |
| SC-20 | " | R3 | corroborated | R3 W6 | Major | 4 |
| SC-21 | administrator/staff asymmetry deferred | R3 | raised | R3 W6 | Major | 4 |
| SC-22 | theme interaction undeveloped | EIC | raised | EIC W12 | Major | 4 |
| SC-22 | " | R3 | corroborated | R3 W5 body, "no theoretical apparatus with which to develop §4.3 beyond description" | Major | 5 |
| SC-23a | structured vs semi-structured | EIC | raised | EIC W11 | Minor | 4 |
| SC-23a | " | R1 | corroborated | R1 W9 | Major | 4 |
| SC-23a | " | R2 | corroborated | R2 W9 | Minor | 4 |
| SC-23a | " | R3 | corroborated | R3 W9 | Minor | 3 |
| SC-23b | artifact-confidence inference unwarranted | R1 | raised | R1 W9 | Major | 4 |
| SC-23b | " | EIC | corroborated | EIC W11 | Minor | 4 |
| SC-23b | " | R2 | corroborated | R2 W9 | Minor | 4 |
| SC-23b | " | R3 | corroborated | R3 W9 | Minor | 3 |
| SC-24 | venue apparatus / reproducibility absent | EIC | raised | EIC W10 | Minor | 5 |
| SC-24 | " | R1 | corroborated | R1 W11 | Minor | 4 |
| SC-25 | Brennan & Osei misplaced | R2 | raised | R2 W10 | Minor | 4 |

### Disposition table

| sub_claim | agree | conflict | silent (named) | Disposition |
|---|---|---|---|---|
| SC-1 | 1 | 0 | R1, R2, R3 | single-reviewer finding (conf 5) |
| SC-2 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-2b | 1 | 1 | EIC, R2 | **[SPLIT]** → arbitrated (R1 stands) |
| SC-3 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-4 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-5 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-6 | 3 | 0 | EIC | **[CONSENSUS-3]** |
| SC-7 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-8 | 2 | 0 | EIC, R2 | corroborated finding |
| SC-9 | 1 | 0 | EIC, R2, R3 | single-reviewer finding (conf 5, D1 owner seat) |
| SC-10 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-11 | 2 | 0 | R2, R3 | corroborated finding |
| SC-12 | 2 | 0 | R2, R3 | corroborated finding |
| SC-13 | 3 | 0 | R3 | **[CONSENSUS-3]** |
| SC-14 | 3 | 0 | R1 | **[CONSENSUS-3]** |
| SC-15 | 3 | 0 | R3 | **[CONSENSUS-3]** |
| SC-15b | 2 | 1 | R3 | **[SPLIT]** → arbitrated (R2/EIC stand) |
| SC-16 | 1 | 0 | EIC, R1, R3 | single-reviewer finding (conf 5) |
| SC-17 | 1 | 0 | EIC, R1, R2 | single-reviewer finding (conf 5) |
| SC-18 | 1 | 0 | EIC, R1, R2 | single-reviewer finding (conf 5) |
| SC-19 | 2 | 0 | EIC, R1 | corroborated finding |
| SC-20 | 2 | 0 | EIC, R2 | corroborated finding |
| SC-21 | 1 | 0 | EIC, R1, R2 | single-reviewer finding (conf 4) |
| SC-22 | 2 | 0 | R1, R2 | corroborated finding |
| SC-23a | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-23b | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-24 | 2 | 0 | R2, R3 | corroborated finding |
| SC-25 | 1 | 0 | EIC, R1, R3 | single-reviewer finding (conf 4) |

**Surface-form parity check (#216).** No sub-claim's weight in the arbitrations above turns on phrasing. SC-2b and SC-15b were arbitrated on seat expertise and cited evidence, not on which reviewer wrote more technically; R3's "trivially fixable" and R1's "Rewording costs the paper nothing" are both informal, and neither was down-weighted for informality — R1's SC-15b position lost on expertise scope, not on style. The opposite-style counterfactual was run on both: rewriting either position in the other's register does not change the outcome. No sub-claim was credited for naming a technical concept absent paper evidence; SC-17's organization-studies vocabulary earns its weight from R3's identification of specific manuscript passages, not from the vocabulary itself. No sub-claim was marked unevaluable.

---

## Part 2: Revision Roadmap

> Supplied as constructive direction for a future submission, not as a revision invitation on this manuscript (see Decision). The `Sub-Claim(s)` column carries Step 1b ids; DA-only items use `—`. Item R1 is a gate: nothing below it is meaningful until it clears.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Verify every reference against Crossref/Scopus; replace the `10.5555` test-prefix DOIs with resolvable identifiers or withdraw the entries | SC-1 | Critical | text: References list, "https://doi.org/10.5555/1042001" through "https://doi.org/10.5555/1042012" | 5 — routine editorial screening | EIC | P1 | 1–2 days (verification); unbounded if sources do not exist |
| R2 | State the true interview N, explain the discrepancy, and confirm no prevalence claim changes under the corrected N | SC-2, SC-2b | Major (EIC/R1; R3 recorded Minor — arbitrated to Major) | text: Abstract vs §3.2, "Fourteen administrators were interviewed in depth" / "Twelve senior administrators (n=12)" | 5 | EIC, R1, R2 `[SEVERITY-SOURCE: letter-fallback]`, R3 | P1 | 1 day |
| R3 | Reinstate the dissenting cases as negative cases, re-derive the theme structure against them, and delete the balanced-representation claim regardless of outcome | SC-3, SC-4 | Critical (EIC, R1, R3; R2 recorded Major) | text: §4.3 "capturing the full range of administrator views" and "these were excluded for space, as they fell outside the three-theme structure" | 5 | R1, EIC, R2, R3, DA C4 | P1 | 3–4 weeks |
| R4 | Correct the Delacroix attribution in §5, and rebuild the third implication either on evidence the paper holds or by engaging Delacroix as an unresolved counterargument | SC-5, SC-6 | Critical (R2, R3; EIC/R1 recorded Major) | text: §5 "who recommends that institutions treat broad stakeholder consultation as the central mechanism" vs §2 "cautions that participatory rhetoric can itself become a compliance ritual" | 5 | R2, EIC, R1, R3, DA C2 | P1 | 1–2 weeks |
| R5 | Rescope every sector-level and cross-national claim to three institutions in one system; fix the unit of analysis and replace "demonstrate" | SC-7, SC-8 | Critical (R1; EIC/R2/R3 recorded Major) | text: §5 "these findings demonstrate that universities across the sector treat QA as a negotiated accomplishment rather than a managerial output" | 5 | R1, EIC, R2, R3, DA C3 | P1 | 3–5 days |
| R6 | Rewrite §3.4: name the analytic tradition, report coder count and agreement/consensus procedure, state a saturation criterion, describe the audit trail, add a positionality statement, and append the codebook | SC-9 | Critical | absence: §3.4 — expected named analytic framework, coder count, agreement procedure, saturation criterion, audit trail, reflexivity; checked §3.1, §3.4, §3.5, §4.1, §4.2, §4.3 | 5 | R1 | P1 | 2–3 weeks |
| R7 | Report the §4.4 comparison in full (test, statistic, df, effect size, CI, assumption check) and confine the language to a descriptive difference within these subsamples — or remove the claim; drop "institutional type as a possible moderator" | SC-11 | Critical | text: §4.4 "we found a statistically significant difference (p<.05) in perceived quality culture" | 5 | R1, EIC, DA M4 | P1 | 3–5 days |
| R8 | Supply the survey instrument: scale range and anchors, item wording and count, provenance, and reliability/validity evidence — or withdraw the construct-level reading of M=3.9 | SC-10 | Major | text/absence: §4.4 "(M=3.9, SD=0.6)"; §3.3 and §4.4 — expected scale range, item wording, item count, provenance, reliability; checked §3.1–§3.4, §4.4, Abstract, References | 5 | R1, EIC, R2, R3, DA M6 | P1 | 1–2 weeks |
| R9 | Reduce §4.1 attributions to non-identifying descriptors, correct §3.5 to describe what was actually done, and confirm whether participants reviewed their quotations as attributed | SC-13 | Critical (EIC; R1/R2 recorded Major) | text: §3.5 and §4.1, "fully anonymized prior to analysis so that no individual could be identified" and "the quality director of the largest private university in the region" | 5 | EIC, R1, R2, DA C5 | P1 | 2–4 days plus any consent re-contact |
| R10 | Give "quality culture" an operational definition the study can test, and mark its boundaries against quality assurance, accreditation compliance, and institutional climate | SC-14 | Major | absence: Abstract and §§1–4.4 — expected an operational definition distinguishing quality culture from QA compliance and institutional climate; checked Abstract, §1, §2, §3.3, §4.4 | 5 | EIC, R2, R3 | P1 | 1–2 weeks |
| R11 | Withdraw "first comprehensive account" and state positively what the study adds relative to Pettersen (2022), Rahman (2020), and Silva & Tan (2021) | SC-15, SC-15b | Major (EIC/R2; R1 recorded Minor — arbitrated to Major) | text: §6 "the first comprehensive account" and §2 "Pettersen (2022) and Rahman (2020), meanwhile, turn attention toward the quality office itself" | 5 | EIC, R2, R1 | P1 | 3–5 days |
| R12 | Reconcile the survey denominators: per-institution respondent counts summing to 48, response rate, eligibility and recruitment, and why the private university is absent from the type comparison | SC-12 | Major | absence: §3.2, §3.3, §4.4 — expected sampling frame, response rate, and per-institution counts reconciling n=48 with n=9 and n=11; checked §3.2, §3.3, §4.4, Abstract | 5 | R1, EIC | P1 | 2–4 days |
| R13 | Reconcile "structured protocol" (§4.1) with "semi-structured interviews" (§3.1), and delete the artifact-confidence claim or ground it in reported per-site theme distribution | SC-23a, SC-23b | Major for the inference (R1); Minor for the wording (EIC, R2, R3) | text: §4.1 and §3.1, "These themes emerged systematically from the structured protocol, giving us confidence that the pattern was not an artifact" vs "semi-structured interviews" | 4 | R1, EIC, R2, R3, DA M3 | P1 | 2–3 days |
| R14 | Name the national system and describe its QA regime: voluntary or mandatory, programme- or institution-level, and what consequences attach to outcomes | SC-19 | Major | absence: §3.2 — expected identification of the national system and its QA regime design; checked §1, §2, §3.1–§3.5, §4, §5, §6 | 5 | R2, R3 | P1 | 2–4 days |
| R15 | Rewrite the §4.4 framing sentence so it states the relation the data show; the survey disconfirmed what the interviews led the authors to expect, and the paper cannot call that corroboration | SC-20 | Major | text: §4.4, "The survey corroborated the qualitative picture" and "the interview accounts had led us to anticipate a more skeptical picture" | 5 | R1, R3, DA M2 | P1 | 1 day |

### Required Item Details

**R1 — Reference verification (gate)**
Twelve sequential DOIs in the reserved `10.5555` range, with several outlets and the publisher unfindable in Crossref or Scopus. Masking real identifiers does not produce sequential test-prefix strings. Nothing below this item can be assessed until it clears; failure is an integrity referral, not a revision item.
- **Acceptance criteria**: every reference resolves to an indexed record verifiable in Crossref or Scopus, or is removed together with every claim it supported.

**R2 — Interview N**
Fourteen in the Abstract, twelve in §3.2 with `n=12`. No attrition, withdrawn consent, excluded transcript, or pilot is mentioned. The corrected N is the denominator for every prevalence claim in §4.
- **Acceptance criteria**: one N appears throughout, the discrepancy is explained in the Methods, and each prevalence statement in §4 is restated against the corrected denominator.

**R3 — Negative cases**
The dissenting participants were removed *because* they did not fit the three themes, so the theme structure has never been tested against the evidence capable of falsifying it. Re-analysis may not return three themes, which is the point.
- **Acceptance criteria**: the dissenting accounts are reported and analysed, the theme structure is re-derived with the misfits shown, and no claim of balanced or full-range representation remains.

**R4 — Delacroix**
§2 and the reference annotation report Delacroix as arguing against consultation-as-evidence; §5 recruits him for the opposite. Correcting the attribution removes the only cited warrant for the paper's single actionable recommendation.
- **Acceptance criteria**: §5 represents Delacroix consistently with §2, and the third implication is either supported by the study's own evidence or reframed as an open question against Delacroix's argument.

**R5 — Scope and unit of analysis**
Three purposively recruited sites in one system, recruited through institutional QA offices, cannot demonstrate anything about "universities across the sector" or "administrators everywhere." Twelve individuals cannot characterise three organisations, and three organisations cannot characterise a field.
- **Acceptance criteria**: every claim is scoped to the three studied institutions with the unit of analysis stated explicitly, and sector-level applicability appears only as a hypothesis for future testing.

**R6 — Thematic analysis documentation**
"Analyzed thematically" and "until a stable structure was reached" name no tradition and state no saturation criterion. Reflexive TA, codebook TA, framework analysis and IPA impose different and partly incompatible obligations.
- **Acceptance criteria**: the named analytic tradition, coder count, agreement or consensus procedure, saturation criterion, audit trail, and positionality statement are all reported, and a codebook or coding frame is appended.

**R7 — §4.4 inferential claim**
A p-value with no named test on groups of nine and eleven, where the parametric/rank-based choice is consequential and normality is untestable in practice. Institutional type is confounded with institution at one case per type, so the moderator inference is not identifiable even if fully reported.
- **Acceptance criteria**: the analysis is either reported in full with the language reduced to a descriptive difference between these two subsamples, or removed, and no moderator claim remains.

**R8 — Survey instrument**
M=3.9 on a five-point scale and on a seven-point scale support opposite conclusions. "Moderately positive institutional quality culture" is an interpretation the manuscript cannot currently license.
- **Acceptance criteria**: the instrument, scale range and anchors, item count, provenance, and internal-consistency evidence are reported and the instrument is appended, or the construct-level interpretation of the mean is withdrawn.

**R9 — Participant protection**
Role plus institution type plus a superlative descriptor identifies a single post-holder among three individuated institutions, and the quoted content is professionally damaging. The §3.5 statement as written is inaccurate, which is a distinct problem from the disclosure risk.
- **Acceptance criteria**: no attribution combines role with institution type or a superlative descriptor, §3.5 accurately describes the de-identification actually performed, and the authors state whether participants approved their quotations as attributed.

**R10 — Construct definition**
The title construct is invoked as shared values, as internalisation, as favourable sentiment, and as the absence of ritualism, and is nowhere separated from quality assurance, accreditation compliance, or institutional climate.
- **Acceptance criteria**: a single operational definition appears before first analytic use, its boundaries against QA, compliance, and climate are stated, and every measurement claim is tied to that definition.

**R11 — Contribution claim**
Priority is refuted by the manuscript's own §2. §2's own observation that Silva & Tan is conceptual rather than grounded supports a narrower and defensible claim about administrators' own accounts.
- **Acceptance criteria**: the priority and comprehensiveness claims are gone, and the Conclusion states the increment positively against the three cited works and the literature added under S1.

**R12 — Survey denominators**
Forty-eight respondents, twenty analysed, twenty-eight unexplained, no response rate, no per-institution counts, and the private university absent from a comparison whose variable is institutional type.
- **Acceptance criteria**: per-institution counts reconcile to 48, a response rate and eligibility description are reported, and the private university's absence from the type contrast is explained.

**R13 — Protocol description and artifact claim**
Protocol standardisation controls interviewer variation, not site effects; a common instrument across sites makes convergence more likely as an instrumentation artefact, not less.
- **Acceptance criteria**: the protocol is described consistently across §3 and §4, and the artifact-confidence sentence is either deleted or replaced with reported per-site theme distribution.

**R14 — Regime specification**
The argument is about how external requirement becomes internal meaning, which makes regime design the operative variable rather than background.
- **Acceptance criteria**: §3.2 names the national system and states whether external review is voluntary or mandatory, programme- or institution-level, and what consequences attach.

**R15 — §4.4 framing sentence**
Corroboration and surprise are different epistemic relations, asserted one sentence apart. The second sentence is the honest one.
- **Acceptance criteria**: the framing sentence states the disconfirmation the data show, and no sentence in §4.4 or §5 describes the survey as corroborating the interviews.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Make a positioning decision and anchor the paper in one canon: the quality-culture literature (Harvey & Green; Harvey & Stensaker; Newton; EUA Quality Culture Project; ESG 2015 or a named national framework) **or** the organization-studies apparatus (means–ends vs policy–practice decoupling; institutional and identity work; competing logics / sustained hybridity) | SC-16, SC-17 | Major | absence: §2 and References — expected engagement with foundational quality-culture scholarship (R2) / with the decoupling and institutional-logics literatures (R3); checked all three strands of §2, §4.1, §4.3, §5, §6, and all twelve reference entries | 5 (both seats) | R2, R3 | P2 | 3–4 weeks |
| S2 | Build a genuine integration procedure with a joint display and stated meta-inference logic, or stop describing the study as mixed methods; address that the survey and interview samples are different populations with no linking design | SC-20 | Major | text: §3.1 "The qualitative component was primary; the survey served to contextualize" with §4.4 | 5 | R1, R3, DA M2 | P2 | 1–2 weeks |
| S3 | Develop the interaction among the three themes — ritualism perceived, persuasion substituted for documentation, identity located in the unresolved gap — rather than presenting them in parallel | SC-22 | Major | absence: §4.3 and §5 — expected analysis of how the three themes interact; checked §4.1, §4.2, §4.3, §5, §6 | 4 (EIC), 5 (R3) | EIC, R3 | P2 | 2–3 weeks |
| S4 | Characterise the external body: its standards, review methodology, what evidence it accepts, what sanctions attach, and how reviewers behave — or rescope the thesis to a two-party account | SC-18 | Major | absence: §2 and §3.2 — expected description of the agency's standards, methodology, sanctions, or reviewer conduct; checked §1, §2 strand one, §3.2, §4.1, §6 | 5 | R3 | P2 | 2–3 weeks |
| S5 | Develop the administrator/staff asymmetry as a finding: does the QA burden concentrate in the quality office, and is that a protective buffer or a decoupled quality function? | SC-21 | Major | text: §4.4 and §5, "The survey corroborated the qualitative picture." and "a divergence worth pursuing in future work" | 4 | R3 | P2 | 1–2 weeks |
| S6 | Replace universal frequency claims with participant counts or coding tallies, and reconcile them with the acknowledged existence of dissenting participants | — (DA M7) | Major (DA section band) | text: §4.2 "This relational, distributed understanding of leadership recurred across every interview" | 4 | DA M7 | P2 | 2–3 days |
| S7 | Remove or re-ground the prospective claim in §6; no outcome data on internalised commitment were collected | — (DA M5) | Major (DA section band) | text: §6 "are more likely to foster the internalized commitment that the language of quality culture promises" | 4 | DA M5 | P2 | 1 day |
| S8 | Respond on the record to the reframing question: is ritual compliance a pathology, or a rational organisational response to an instrument whose only accepted evidence of quality is documentation? | SC-17 | Major | text: §4.1 "It's theater, and everyone knows it's theater." | 5 | R3 | P2 | 3–5 days (author judgment; either answer is acceptable if argued) |
| S9 | Add a limitations section, a data/materials availability statement, and funding and conflict declarations; present the quantitative results in at least one table | SC-24 | Minor | absence: end matter and §§5–6 — expected limitations, data availability, funding and conflict declarations, protocol or instrument, and tables; checked §3.3, §3.4, §5, §6, References | 5 (EIC), 4 (R1) | EIC, R1 | P3 | 2–3 days |
| S10 | Move Brennan & Osei (2020) out of the empirical strand in §2; a conceptual synthesis cannot document perceptions, which leaves Montero (2021) alone supporting that strand | SC-25 | Minor | text: §2 "documenting how academics often perceive it as burdensome... (Montero, 2021; Brennan & Osei, 2020)" | 4 | R2 | P3 | 1 hour |

> Transported metadata appears on every row above: each item carries the driving sub-claim's transported Severity (with fallback tags where a card lacked the field), the finding's typed Evidence Anchor, and its per-finding Confidence. Where seats transported different severities for the same sub-claim, the highest transported value is used and the divergence is named in-cell; no severity was re-derived.

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total effort: 10–13 weeks, sequential after R1)
- [ ] R1: Verify all twelve references against Crossref/Scopus (gate — do nothing else until this clears)
- [ ] R2: Fix and explain the interview N; restate prevalence claims against it
- [ ] R3: Reinstate and analyse the dissenting cases; re-derive the themes; delete the balance claim
- [ ] R4: Correct the Delacroix attribution; rebuild §5's third implication
- [ ] R5: Rescope all sector and cross-national claims; fix the unit of analysis
- [ ] R6: Rewrite §3.4 in full; append the codebook
- [ ] R7: Report or remove the §4.4 inferential claim; drop the moderator inference
- [ ] R8: Supply the survey instrument or withdraw the construct-level reading of M=3.9
- [ ] R9: De-identify §4.1 attributions; correct §3.5; confirm quotation approval
- [ ] R10: Define "quality culture" operationally and mark its boundaries
- [ ] R11: Withdraw the priority claim; state the increment positively
- [ ] R12: Reconcile the survey denominators; explain the missing institution
- [ ] R13: Fix the protocol description; delete or ground the artifact-confidence claim
- [ ] R14: Name the national system and its QA regime design
- [ ] R15: Rewrite the §4.4 "corroborated" sentence

#### Priority 2 — Content Supplementation (estimated total effort: 6–9 weeks, partly parallel)
- [ ] S1: Choose one canon and anchor the paper in it
- [ ] S2: Build genuine integration or drop the mixed-methods framing
- [ ] S3: Develop the interaction among the three themes
- [ ] S4: Characterise the external body, or rescope the thesis
- [ ] S5: Develop the administrator/staff asymmetry
- [ ] S6: Replace universal frequency claims with counts
- [ ] S7: Remove or re-ground the §6 prospective claim
- [ ] S8: Answer the ritualism-as-rational-adaptation question on the record

#### Priority 3 — Text and Formatting (estimated total effort: 2–3 days)
- [ ] S9: Add limitations, data availability, funding and conflict statements; add a results table
- [ ] S10: Recategorise Brennan & Osei (2020) in §2

### Deadline

Not applicable — this is a Reject, and no revision window is open on this manuscript. Were R1 to clear on verification and the work resubmitted, the P1 and P2 sets together represent roughly **10–14 weeks**, with R3 and R6 on the critical path because re-analysis may change the theme structure and therefore the paper's argument.

### Where to take this next

Should the reference apparatus verify, the honest positioning options are: *Quality in Higher Education* (natural disciplinary home, but that readership will require S1's QA-canon route and will notice its absence immediately), *Journal of Higher Education Policy and Management* (more tolerant of a modest sample where the practical contribution is sharpened — which requires R4 first, since the only concrete recommendation currently rests on the reversed citation), or *Tertiary Education and Management* (the most realistic target given the present sample and analytic depth). An organization-studies venue becomes viable only on S1's second route, and would raise the ceiling at the cost of a longer rewrite.

### Response Letter

Any resubmission should respond to every item above using the `templates/revision_response_template.md` format, with one response per item id.

---

## Part 2b: Roadmap — Schema 7 machine form

```json
{
  "schema": "roadmap/7",
  "decision": "reject",
  "contract_id": "reviewer/reviewer_full/v2",
  "note": "Emitted as constructive direction; no revision window is open. Item R1 is a gate.",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": "eic", "sub_claims": ["SC-1"], "severity": "critical", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: References list, https://doi.org/10.5555/1042001 through https://doi.org/10.5555/1042012", "verification_criteria": "Every reference resolves to an indexed record verifiable in Crossref or Scopus, or is removed together with every claim it supported."},
    {"id": "R2", "priority": "must_fix", "reviewer": ["eic", "methodology", "domain", "perspective"], "sub_claims": ["SC-2", "SC-2b"], "severity": "major", "severity_source_note": "domain row: letter-fallback; perspective transported minor, arbitrated to major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: Abstract vs §3.2, 'Fourteen administrators were interviewed in depth' / 'Twelve senior administrators (n=12)'", "verification_criteria": "One N appears throughout, the discrepancy is explained in Methods, and each §4 prevalence statement is restated against the corrected denominator."},
    {"id": "R3", "priority": "must_fix", "reviewer": ["methodology", "eic", "domain", "perspective", "da"], "sub_claims": ["SC-3", "SC-4"], "severity": "critical", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: §4.3 'capturing the full range of administrator views' and 'these were excluded for space, as they fell outside the three-theme structure'", "verification_criteria": "Dissenting accounts are reported and analysed, the theme structure is re-derived with misfits shown, and no claim of balanced or full-range representation remains."},
    {"id": "R4", "priority": "must_fix", "reviewer": ["domain", "eic", "methodology", "perspective", "da"], "sub_claims": ["SC-5", "SC-6"], "severity": "critical", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: §5 'who recommends that institutions treat broad stakeholder consultation as the central mechanism' vs §2 'cautions that participatory rhetoric can itself become a compliance ritual'", "verification_criteria": "§5 represents Delacroix consistently with §2, and the third implication is supported by the study's own evidence or reframed as an open question against Delacroix's argument."},
    {"id": "R5", "priority": "must_fix", "reviewer": ["methodology", "eic", "domain", "perspective", "da"], "sub_claims": ["SC-7", "SC-8"], "severity": "critical", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: §5 'these findings demonstrate that universities across the sector treat QA as a negotiated accomplishment rather than a managerial output'", "verification_criteria": "Every claim is scoped to the three studied institutions with the unit of analysis stated explicitly, and sector-level applicability appears only as a hypothesis."},
    {"id": "R6", "priority": "must_fix", "reviewer": "methodology", "sub_claims": ["SC-9"], "severity": "critical", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "absence: §3.4 - expected named analytic framework, coder count, agreement procedure, saturation criterion, audit trail, reflexivity; checked §3.1, §3.4, §3.5, §4.1, §4.2, §4.3", "verification_criteria": "Named analytic tradition, coder count, agreement or consensus procedure, saturation criterion, audit trail, and positionality statement are all reported, and a codebook is appended."},
    {"id": "R7", "priority": "must_fix", "reviewer": ["methodology", "eic", "da"], "sub_claims": ["SC-11"], "severity": "critical", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: §4.4 'we found a statistically significant difference (p<.05) in perceived quality culture'", "verification_criteria": "The analysis is reported in full with language reduced to a descriptive difference between these two subsamples, or removed, and no moderator claim remains."},
    {"id": "R8", "priority": "must_fix", "reviewer": ["methodology", "eic", "domain", "perspective", "da"], "sub_claims": ["SC-10"], "severity": "major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "absence: §3.3 and §4.4 - expected scale range, item wording, item count, provenance, reliability; checked §3.1-§3.4, §4.4, Abstract, References", "verification_criteria": "Instrument, scale range and anchors, item count, provenance, and internal-consistency evidence are reported and the instrument appended, or the construct-level interpretation of the mean is withdrawn."},
    {"id": "R9", "priority": "must_fix", "reviewer": ["eic", "methodology", "domain", "da"], "sub_claims": ["SC-13"], "severity": "critical", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: §3.5 and §4.1, 'fully anonymized prior to analysis so that no individual could be identified' and 'the quality director of the largest private university in the region'", "verification_criteria": "No attribution combines role with institution type or a superlative descriptor, §3.5 accurately describes the de-identification performed, and quotation approval status is stated."},
    {"id": "R10", "priority": "must_fix", "reviewer": ["eic", "domain", "perspective"], "sub_claims": ["SC-14"], "severity": "major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "absence: Abstract and §§1-4.4 - expected an operational definition distinguishing quality culture from QA compliance and institutional climate; checked Abstract, §1, §2, §3.3, §4.4", "verification_criteria": "A single operational definition appears before first analytic use, boundaries against QA, compliance, and climate are stated, and every measurement claim is tied to that definition."},
    {"id": "R11", "priority": "must_fix", "reviewer": ["eic", "domain", "methodology"], "sub_claims": ["SC-15", "SC-15b"], "severity": "major", "severity_source_note": "methodology transported minor, arbitrated to major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: §6 'the first comprehensive account' and §2 'Pettersen (2022) and Rahman (2020), meanwhile, turn attention toward the quality office itself'", "verification_criteria": "Priority and comprehensiveness claims are removed, and the Conclusion states the increment positively against Pettersen (2022), Rahman (2020), Silva and Tan (2021), and the literature added under S1."},
    {"id": "R12", "priority": "must_fix", "reviewer": ["methodology", "eic"], "sub_claims": ["SC-12"], "severity": "major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "absence: §3.2, §3.3, §4.4 - expected sampling frame, response rate, per-institution counts reconciling n=48 with n=9 and n=11; checked §3.2, §3.3, §4.4, Abstract", "verification_criteria": "Per-institution counts reconcile to 48, a response rate and eligibility description are reported, and the private university's absence from the type contrast is explained."},
    {"id": "R13", "priority": "must_fix", "reviewer": ["methodology", "eic", "domain", "perspective", "da"], "sub_claims": ["SC-23a", "SC-23b"], "severity": "major", "severity_source_note": "major for the inference (methodology); minor for the wording (eic, domain, perspective)", "confidence": 4, "source_kind": "reviewer", "evidence_anchor": "text: §4.1 and §3.1, 'These themes emerged systematically from the structured protocol, giving us confidence that the pattern was not an artifact' vs 'semi-structured interviews'", "verification_criteria": "The protocol is described consistently across §3 and §4, and the artifact-confidence sentence is deleted or replaced with reported per-site theme distribution."},
    {"id": "R14", "priority": "must_fix", "reviewer": ["domain", "perspective"], "sub_claims": ["SC-19"], "severity": "major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "absence: §3.2 - expected identification of the national system and its QA regime design; checked §1, §2, §3.1-§3.5, §4, §5, §6", "verification_criteria": "§3.2 names the national system and states whether external review is voluntary or mandatory, programme- or institution-level, and what consequences attach."},
    {"id": "R15", "priority": "must_fix", "reviewer": ["methodology", "perspective", "da"], "sub_claims": ["SC-20"], "severity": "major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: §4.4, 'The survey corroborated the qualitative picture' and 'the interview accounts had led us to anticipate a more skeptical picture'", "verification_criteria": "The framing sentence states the disconfirmation the data show, and no sentence in §4.4 or §5 describes the survey as corroborating the interviews."},
    {"id": "S1", "priority": "should_fix", "reviewer": ["domain", "perspective"], "sub_claims": ["SC-16", "SC-17"], "severity": "major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "absence: §2 and References - expected engagement with foundational quality-culture scholarship (domain) or with the decoupling and institutional-logics literatures (perspective); checked all three strands of §2, §4.1, §4.3, §5, §6, all twelve reference entries", "verification_criteria": "The paper commits to one canon and engages it substantively; the alternative literature is either integrated or explicitly set aside with a stated reason."},
    {"id": "S2", "priority": "should_fix", "reviewer": ["methodology", "perspective", "da"], "sub_claims": ["SC-20"], "severity": "major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: §3.1 'The qualitative component was primary; the survey served to contextualize' with §4.4", "verification_criteria": "A joint display and stated integration procedure with meta-inference logic are present and the different sample populations are addressed, or the mixed-methods self-description is removed."},
    {"id": "S3", "priority": "should_fix", "reviewer": ["eic", "perspective"], "sub_claims": ["SC-22"], "severity": "major", "confidence": 4, "source_kind": "reviewer", "evidence_anchor": "absence: §4.3 and §5 - expected analysis of how ritual compliance, distributed leadership, and identity work interact; checked §4.1, §4.2, §4.3, §5, §6", "verification_criteria": "The manuscript analyses how the three themes sustain one another rather than presenting them in parallel."},
    {"id": "S4", "priority": "should_fix", "reviewer": "perspective", "sub_claims": ["SC-18"], "severity": "major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "absence: §2 and §3.2 - expected description of the external agency's standards, review methodology, sanctions, or reviewer conduct; checked §1, §2 strand one, §3.2, §4.1, §6", "verification_criteria": "The external body's standards, methodology, accepted evidence, and consequences are described, or the three-party thesis is rescoped to two parties."},
    {"id": "S5", "priority": "should_fix", "reviewer": "perspective", "sub_claims": ["SC-21"], "severity": "major", "confidence": 4, "source_kind": "reviewer", "evidence_anchor": "text: §4.4 and §5, 'The survey corroborated the qualitative picture.' and 'a divergence worth pursuing in future work'", "verification_criteria": "The administrator/staff asymmetry is analysed as a finding with a stated interpretation, not deferred to future work."},
    {"id": "S6", "priority": "should_fix", "reviewer": "da", "sub_claims": [], "severity": "major", "confidence": 4, "source_kind": "reviewer", "evidence_anchor": "text: §4.2 'This relational, distributed understanding of leadership recurred across every interview'", "verification_criteria": "Frequency claims report participant counts or coding tallies and are consistent with the disclosed dissenting participants."},
    {"id": "S7", "priority": "should_fix", "reviewer": "da", "sub_claims": [], "severity": "major", "confidence": 4, "source_kind": "reviewer", "evidence_anchor": "text: §6 'are more likely to foster the internalized commitment that the language of quality culture promises'", "verification_criteria": "The prospective claim is removed or restated as a hypothesis, with no implication that outcome data on internalised commitment were collected."},
    {"id": "S8", "priority": "should_fix", "reviewer": "perspective", "sub_claims": ["SC-17"], "severity": "major", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "text: §4.1 'It's theater, and everyone knows it's theater.'", "verification_criteria": "The manuscript states and argues a position on whether ritual compliance is a pathology or a rational response to the review instrument."},
    {"id": "S9", "priority": "nice_to_fix", "reviewer": ["eic", "methodology"], "sub_claims": ["SC-24"], "severity": "minor", "confidence": 5, "source_kind": "reviewer", "evidence_anchor": "absence: end matter and §§5-6 - expected limitations, data availability, funding and conflict declarations, protocol or instrument, and tables; checked §3.3, §3.4, §5, §6, References", "verification_criteria": "Limitations, data or materials availability, funding, and conflict statements are present, and quantitative results appear in at least one table."},
    {"id": "S10", "priority": "nice_to_fix", "reviewer": "domain", "sub_claims": ["SC-25"], "severity": "minor", "confidence": 4, "source_kind": "reviewer", "evidence_anchor": "text: §2 'documenting how academics often perceive it as burdensome, distrust-laden, and disconnected from their disciplinary values (Montero, 2021; Brennan & Osei, 2020)'", "verification_criteria": "Brennan and Osei (2020) is described as a conceptual synthesis and is not cited as empirical documentation of academic perceptions."}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary
- Dimension scores: D5 = block; D6 = block (fatal). D1–D4 not assessed.
- Key point: the reference apparatus cannot be verified, which removes the premise for any originality claim; the paper's real increment — the interaction among its three themes — is one sentence long.

### Reviewer 1 (Methodology) Summary
- Dimension scores: D1 = block (repairable); D3 = block (repairable). D2, D4–D6 not assessed.
- Key point: a reader cannot reconstruct how twelve (or fourteen) transcripts became three themes, and the themes were never tested against the cases that would falsify them; every defect is in principle repairable, and re-analysis may not return the same three themes.

### Reviewer 2 (Domain) Summary
- Dimension scores: D2 = block (repairable). All others not assessed.
- Key point: §5 recruits Delacroix for the position his paper exists to refute, and correcting it leaves the third implication with no warrant while raising the counterargument the study never answers; the quality-culture canon is entirely absent, so §4.1 cannot be distinguished from a rediscovery.

### Reviewer 3 (Cross-disciplinary / organizational sociology) Summary
- Dimension scores: D4 = warn (block considered and declined on its own stated conditions). All others not assessed.
- Key point: the paper is legible to adjacent-field readers and simultaneously invisible to them, because all three findings already have names in organization studies and it uses none of them; the external body — one of its three named parties — is never opened.

### Devil's Advocate Summary
- Dimension score: D3 = block (repairable). All others not assessed.
- Key point: five critical coherence failures, all internal to the manuscript, including a circular exclusion criterion under which the theme structure determines its own inputs; the core thesis survives all of them, which is why the block was classified repairable.
