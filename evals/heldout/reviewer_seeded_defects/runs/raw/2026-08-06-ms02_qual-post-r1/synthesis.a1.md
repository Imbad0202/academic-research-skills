# Editorial Decision Package

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size: 5`
**Protocol applied:** v3.6.2 Sprint Contract Synthesizer Protocol (arithmetic mode). The general sub-claim inventory is used only for roadmap traceability, not for decision derivation.

---

## Mechanical Audit (Sprint Contract, Steps 1–3)

### Step 1 — Role-scoped scoring matrix

Only seats whose `contract_role` appears in a dimension's `eligible_roles` are counted. `not_assessed` from ineligible seats is excluded from numerator and denominator.

| Dim | Priority | Eligible roles | Assessed eligible seats | Scores | Fatal declared? | Verdict |
|-----|----------|----------------|-------------------------|--------|-----------------|---------|
| D1 methodology_rigor | mandatory | methodology | 1/1 (methodology) | block (`repairable`) | no | `block` |
| D2 domain_accuracy | mandatory | domain | 1/1 (domain) | block (`fatal`) | **yes** | `block(fatal)` |
| D3 argumentative_coherence | mandatory | da, methodology | 2/2 (da, methodology) | block (`repairable`), block (`repairable`) | no | `block` |
| D4 cross_disciplinary_relevance | high | perspective | 1/1 (perspective) | block | no | `block` |
| D5 writing_and_structure | normal | eic | 1/1 (eic) | block (no `block_class`) | no | `block` |
| D6 venue_fit_and_contribution | mandatory | eic | 1/1 (eic) | block (`repairable`) | no | `block` |

No dimension is unassessed by its eligible seats; no `[DIMENSION-UNASSESSED]` condition. No abstentions were recorded, so no eligible abstention was excluded. Audit verdict = worst assessed eligible score across the matrix = **`block(fatal)`**.

### Step 2 — Failure condition evaluation

| Condition | Severity | Quantifier | Expression | Per-dimension result | Fired |
|-----------|----------|------------|------------|----------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 F, **D2 T**, D3 F, D6 F → `any` = T | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1 T, D2 T, D3 T, D6 T → `any` = T | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 T (n=1, owner seat), D2 T (n=1), D3 T (n=2, both seats), D6 T (n=1) → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 T → `any` = T | **true** |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1–D6 all T → `any` = T | **true** |
| F0 | 10 | all | every dimension scores 'pass' | D1–D6 all F | false |

Fatal scope was checked as valid: the fatal declaration sits on D2, a `mandatory` dimension. All expressions matched the closed vocabulary; no `[EXPRESSION-UNRECOGNISED]` condition. No reviewer was marked unusable; the panel ran at full `panel_size: 5`, so no `[PANEL-SHRUNK]` condition.

### Step 3 — Precedence and emission

Highest severity among fired conditions: **F1 (95)** → `action: editorial_decision=reject`.

```
dimension_verdicts: [D1=block, D2=block(fatal), D3=block, D4=block, D5=block, D6=block]
fired_conditions: [F1, F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED]
editorial_decision=reject
```

No `C<n>=REJECTED` entries, therefore no rejection rationale lines are owed. The mechanical decision is not `accept`, so no `[DA-CRITICAL-VS-ACCEPT]` marker applies.

**Card hygiene flags (raised, not repaired — Phase 1 is not my territory):**
- `[CARD-HYGIENE: da]` — the DA card opens with a self-cancelling `## Scoring Plan Dissent` stub ("*(omitted…)*" followed by "Actually, per protocol I omit the section entirely"). No dissent is actually declared, so no fatality could be minted during scoring-plan dissent and the arithmetic is unaffected. The stub should be removed at source.
- `[CARD-HYGIENE: eic]` — D5 `block` carries no `block_class`. Absence of a fatal declaration is read as non-fatal; F1 does not fire on D5 (and D5 is `normal`, outside F1's mandatory scope in any case).

### Step 4b — Cross-Model Blind Decision Check

`ARS_CROSS_MODEL` is not set and no consent gate was passed. Check not run; no behavioural change.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting "Building Institutional Quality Culture: Administrator Perspectives on Quality Assurance Implementation in Universities." The manuscript was assessed by a five-seat panel — a Journal-Fit Reviewer and four independent reviewers covering methodology, domain accuracy, cross-disciplinary relevance, and argumentative coherence — against the six acceptance dimensions of the review contract.

### Decision: Reject

The decision follows the contract arithmetic above: a fatal block on a mandatory dimension (D2, domain accuracy) fires F1 at severity 95, which takes precedence over the four lower-severity conditions that also fired. Every one of the six dimensions scored `block`; no dimension reached `pass` or `warn`.

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — no dispatching-layer provenance stamp accompanied this invocation, so none of the three permitted statements (cross-model slot active / single-family disclosure / dispatch-failure fallback) can be filled. This block is present because the mode is `reviewer_full`; its content is withheld rather than inferred. **No claim of model independence across the five seats is made or implied.** The dispatching layer should supply the stamp and refill this block before the letter ships.

### Consensus Analysis

Consensus is counted over the four non-DA seats (Journal-Fit/EiC, R1 Methodology, R2 Domain, R3 Perspective), denominator always 4. Silence is not agreement. The DA's findings are adjudicated separately below.

#### Points of Agreement

- **[CONSENSUS-4] (SC-1)** §5 recruits Delacroix (2018) as recommending stakeholder consultation as the central mechanism for quality culture, which inverts the position §2 and the reference annotation both attribute to that source. Raised by all four seats (EiC W2, R1 W12, R2 W1, R3 W7) and by the DA (C1). The paper's third discussion finding and its practical recommendation rest on the inverted reading.
- **[CONSENSUS-4] (SC-2)** §4.3 claims "balanced representation … the full range of administrator views" in the same paragraph in which it reports excluding dissenting participants because they "fell outside the three-theme structure." Raised by EiC (W3, Critical), R1 (W1, Critical), R3 (W2, Critical), and identified in R2's body before hand-off; DA C3. R1 and the DA converge independently on the same structural point: the exclusion criterion is the finding, which insulates the theme structure from the only evidence capable of testing it.
- **[CONSENSUS-4] (SC-3)** §3.5's unqualified anonymisation guarantee is contradicted by §4.1's attribution of critical quotations to "the quality director of the largest private university in the region" and "the associate dean for quality at the public research university" — unique posts within a three-site design whose site types are stated. EiC W4, R1 W7, R3 W1 (all Critical), noted in R2's body; DA C4.
- **[CONSENSUS-4] (SC-4)** §5–§6 generalise from three institutions in one unnamed system to "universities across the sector," "the higher education sector as a whole," and "administrators everywhere," with no representativeness argument and no operative limitations section. EiC W6, R1 W9, R2 W6, R3 W3; DA C2.
- **[CONSENSUS-3] (SC-5)** "Quality culture" is never operationalised: defined discursively, then scored as a single mean with no instrument behind it, so the construct in the title is not the construct measured. EiC (review body and W7), R1 W4, R2 W3/W5. R3 silent.
- **[CONSENSUS-3] (SC-6)** The quantitative strand is unreportable as given — no instrument, no item count, no scale anchors, no response rate, 20 of 48 respondents accounted for, no test name, statistic, df, or effect size, no table. EiC W7, R1 W4/W5/W6, R2 (records he did not treat the survey as peripheral). R3 silent. R1's four Arithmetic Receipts (AR1–AR4) all return `not_computable` or `not_applicable`, which is independent confirmation that the reported numbers cannot be checked at all rather than merely check poorly.
- **[CONSENSUS-3] (SC-7)** The §6 priority claim ("the first comprehensive account") is contradicted by the paper's own §2, which names Pettersen (2022) and Rahman (2020) as closest in spirit on two of this paper's three themes. EiC W5, R1 W13, R2 W8; DA M5. R3 silent.

#### Corroborated findings (2 of 4 seats, no conflict — below the consensus bar, action-bearing)

- **(SC-8)** The national system, regime type, responsible agency, and cycle position are never stated, so the findings are uninterpretable for a policy reader and untestable by anyone else (R2 W7, R3 W5).
- **(SC-9)** The generic organizational literature the three themes restate — decoupling and ceremonial conformity, institutional logics, identity work, audit culture — is absent, so no higher-education-specific contribution is established (R3 W4, R2 W4).
- **(SC-10)** The inline editorial annotation on the Delacroix reference entry is not a reference-list element in any style this venue uses (EiC W8, R2 W2).

#### Single-reviewer findings (1 of 4, no conflict — weighted by confidence, not by count)

- **(SC-11)** No integration mechanism exists — no joint display, no stated point of interface — so the design is a qualitative study with a survey appended and the "mixed-methods" label is not yet earned (R1 W8, confidence 5, integration is this reviewer's declared teaching and reviewing specialism; full weight).
- **(SC-12)** §4.4 says the survey "corroborated the qualitative picture" and, two sentences later, that the interviews "had led us to anticipate a more skeptical picture" (R1 W10, confidence 5; DA M3). Corroboration and disconfirmation cannot both be claimed of one result.
- **(SC-13)** The three-party negotiation claim is evidenced from one party's testimony; academics appear only as objects of persuasion and external bodies not at all (R3 W6, confidence 4).
- **(SC-14)** The reference apparatus itself cannot be verified: all twelve DOIs sit on the 10.5555 reserved test prefix with suffixes incrementing 1042001–1042012 in alphabetical order of first author (R2 W2, Critical, confidence 4). **This is the sole driver of the fatal designation and therefore of the decision, and I record its provenance plainly:** it is a single-seat finding from the one seat that owns D2, and that seat states its own retraction condition — resolvable DOIs or verifiable bibliographic records for all twelve works. No other seat contradicts it; R3 independently observes that all twelve references are higher-education sources, and the EiC independently flags the anomalous annotation on one entry. The finding stands on the evidence as filed. Recording its falsifiability does not alter the fired condition's action.
- **(SC-15)** "Moderator" language from a two-group cross-sectional contrast with no model and no interaction term (R1 W14); the DA adds (M4) that with one institution per type, type and institution are perfectly confounded, so the design cannot in principle separate them.
- **(SC-16)** The stated subgroup analysis plan (§3.4, "where role categories permitted") does not match the analysis reported (§4.4, by institution) (EiC W9).
- **(SC-17)** The design recommendation names no process, cycle, instrument, or committee, so no quality director could act on it (R3 W9).

#### Points of Disagreement

Four genuine conflicts required arbitration. Three are severity conflicts; one is a direction conflict.

- **[SPLIT] (SC-18) Severity of the interview-count inconsistency** (Abstract: fourteen; §3.2: twelve). EiC W1 and R1 W2 band this Major; R3 W8 bands it Minor. R2 raises it without banding.
  - **Editor's Resolution: Major.** Both Major bandings come from the seats that own reader-reconstruction (D5) and methodological reporting (D1), and R1's rationale is specific: the discrepancy is unresolvable from the text and the natural reading — that the missing two are the excluded dissenters of §4.3 — is available to any reader and nowhere addressed. R3's Minor banding rests on the fix being simple, which is a remedy-cost judgement, not an impact judgement. The remedies are compatible, so this resolves on severity alone.

- **[SPLIT] (SC-19) Severity of the structured/semi-structured contradiction.** EiC W10 and the DA (M2) treat the wording contradiction as minor; R1 W11 bands it Major on a different ground — that §4.1 treats protocol fixity as licence to rule out site-specific artefact.
  - **Editor's Resolution: split the item, both sides upheld.** These are two claims inside one bundle. The description mismatch is a Minor text fix (roadmap S9). The inference — that asking the same questions everywhere controls the local circumstances shaping the answers — is a Major warrant gap on R1's own dimension and is retained at Major (roadmap S5). Neither seat is overruled.

- **[SPLIT] (SC-20) Severity of the priority claim.** EiC W5 bands Major; R1 W13 and R2 W8 band Minor, both on the ground that deleting the sentence costs the paper nothing.
  - **Editor's Resolution: split the item, EiC upheld on the substance.** Deleting "first comprehensive" is indeed a Minor text fix (roadmap S-tier item, P3). But the EiC — the seat that owns D6 — is not banding the sentence; the block is that the manuscript never states its increment over Pettersen, Rahman, and Silva & Tan, and never compares its findings against theirs. That positioning deficit is what blocks D6 and is retained at Major as a required item (R10). Expertise-first arbitration: venue fit and contribution is the EiC's dimension.

- **[SPLIT] (SC-21) Direction conflict: contextual specification versus participant confidentiality.** R2 W7 requires the national system, regime type, agency, and cycle position to be named, without which the domain claims are uncheckable. R3 W1 requires institution-linked descriptors to be stripped because, in a three-site design with one private university, they identify individuals whose attributed quotes disparage their own employers. Each demand pushes on the same object — how much institutional detail the paper discloses.
  - **Editor's Resolution: both, and they are separable — the authors must execute both, not choose.** These demands only look opposed because the manuscript currently uses anonymity to avoid specification while claiming generality. Regime-level context (which national system, accreditation versus audit versus evaluative-state, which agency, where in the cycle) is disclosure about the *system*; institution-linked role descriptors are disclosure about *individuals*. R2 says so explicitly: naming the national system and regime type while withholding institution names is standard practice in this literature. The required outcome is therefore: specify the regulatory regime at system level (R11) **and** strip every institution-linked role descriptor from quote attributions (R2). Where the two genuinely collide — a regime detail that, combined with the stated site typology, re-identifies a post-holder — confidentiality wins and the authors state what was withheld and why. This is not a disagreement to be averaged.

I record one further asymmetry that is not a SPLIT but bears on how this decision should be read. R1, the DA, and the EiC all classify their blocks as `repairable`, and all three describe a defensible paper surviving underneath the defects; R2 alone classifies as `fatal`, on SC-14. Those positions do not conflict — they concern different dimensions and different objects — but the panel's own view is that everything except the reference apparatus is fixable by re-analysis and re-reporting from work already done. The decision is Reject because F1 fired on the fatal block, not because four seats judged the paper unsalvageable.

### Decision Rationale

The manuscript has a real subject and, in three seats' independent judgement, a publishable paper inside it. The EiC finds the administrator-centred angle genuinely under-served and the identity-work theme an analytic advance rather than a restatement; R2 calls the §4.3 identity material "the part of the paper that would be worth publishing if the foundations were sound"; R3 finds the §2 framing legible enough to travel to another regulated sector intact. I do not want that lost in the verdict.

The verdict nonetheless follows without discretion. Every one of the six contract dimensions scored `block`, and the block on domain accuracy is fatal: the twelve-entry reference apparatus carries reserved test-prefix DOIs with sequentially incrementing suffixes in alphabetical order of first author, and §2 — where the paper's entire positioning is built — rests on it. Under F1 that fires Reject at severity 95, ahead of the four other conditions that also fired.

Independently of the arithmetic, three findings would each void a stated contribution on their own. The Delacroix inversion removes source support from the third discussion recommendation, and, worse, dissolves the tension the paper names as its reason for existing. The exclusion of dissenting participants on the ground that they did not fit the theme structure makes the structure both premise and selection criterion, which unsupportably compromises every downstream prevalence claim and falsifies the coverage sentence printed beside it. The sector-wide generalisation is asserted as demonstrated in §5 and conceded as untested in §6. Beside these, the anonymisation guarantee is contradicted on the following page by attributions that identify individual post-holders alongside criticism of their own employers — which, as R1 notes, may require returning to participants rather than editing text.

The path forward is a rebuild, not a revision cycle, and the roadmap below specifies it.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire reference apparatus carries reserved test-prefix DOIs in sequential order and cannot be verified; §2's positioning claims are therefore uncheckable. Fatal block on D2; sole driver of F1 and of the decision. | R2 (Domain) | text: References "https://doi.org/10.5555/1042001" (Aoki 2019) through "https://doi.org/10.5555/1042012" (Silva & Tan 2021) | R1 |
| 2 | Anonymisation guarantee contradicted by re-identifying quote attributions carrying criticism of participants' own employers; consent basis cannot be reconciled with the reporting practice. | EiC, R1, R3 (+DA C4) | text: §3.5 "all data were fully anonymized prior to analysis so that no individual could be identified"; §4.1 "the quality director of the largest private university in the region" | R2 |
| 3 | Disconfirming cases excluded because they did not fit the three-theme structure, while the same paragraph claims full coverage; the central empirical result is insulated from the only evidence that could test it. | EiC, R1, R3 (+DA C3) | text: §4.3 "capturing the full range of administrator views on QA implementation"; "these were excluded for space, as they fell outside the three-theme structure that organized our analysis" | R3 |

### Devil's Advocate Adjudication

All four DA CRITICAL findings are recorded here with their adjudication. Adjudication is visibility, not veto.

| ID | DA argument | Corroborated by | Journal-Fit assessment of validity | Adjudication |
|----|-------------|-----------------|-----------------------------------|--------------|
| C1 | §5 inverts the Delacroix position §2 and the annotation both state; the design recommendation carried into §6 rests on the inversion | EiC W2, R1 W12, R2 W1, R3 W7 (all four non-DA seats) | Valid. The contradiction is internal to the manuscript and verifiable without domain expertise; R2, who owns the accuracy verdict on the source, reaches the same conclusion independently and adds that a consultation-maximising process is precisely what Delacroix identifies as the sophisticated form of ritual | **VALIDATED** |
| C2 | Sector-wide and universal claims asserted as demonstrated on twelve purposively recruited administrators in three institutions in one system, with §6 conceding the generalisation is untested | EiC W6, R1 W9, R2 W6, R3 W3 | Valid. R2 strengthens it: comparative QA scholarship does not merely fail to support cross-system uniformity, it contradicts it, since administrator behaviour varies systematically with regulatory design | **VALIDATED** |
| C3 | Exclusion criterion is the finding; theme structure is both analytic premise and selection criterion, so all prevalence claims are unsupportable as written | EiC W3, R1 W1, R3 W2 (all Critical); named in R2's body | Valid, and the sharpest formulation on the panel. R1 reaches it independently from trustworthiness criteria; the DA reaches it from argument structure alone. R3's observation that a paper critiquing institutions for tidy panel-flattering documentation has produced a tidy thesis-flattering narrative is a credibility point about the whole account, not one theme | **VALIDATED** |
| C4 | Ethics section asserts a property of the data that the findings section disproves; stated consent basis irreconcilable with reporting practice | EiC W4, R1 W7, R3 W1 (all Critical) | Valid. R3, who chairs a research ethics committee and publishes on confidentiality risk in small-N elite interviewing, and R1, on data-handling grounds, both confirm the descriptors are identifications rather than descriptors given the stated site typology | **VALIDATED** |

DA MAJOR findings (M1–M6) are carried into the roadmap and are not adjudicated at CRITICAL level: M1 → R6, M2 → S5/S9, M3 → S2, M4 → R8/S7, M5 → R10 and the P3 deletion, M6 → S6.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the consensus-analysis `SC-n` identifiers above, so decomposed granularity survives to the output boundary. Items with no sub-claim identifier (DA-only or pre-decomposition) use `—`.
>
> **Standing on a Reject decision:** this roadmap is a rebuild specification, not a revision cycle. It is supplied because the panel identified a defensible paper underneath the defects, and because R1's, the DA's, and the EiC's `repairable` classifications mean most of the work is re-analysis and re-reporting from records the study must already hold. Item R1 is logically prior to every other item: if the twelve sources are not real, §2 and all positioning built on it must be rebuilt before the rest is worth doing.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Supply resolvable DOIs or verifiable bibliographic records for all twelve references; where a work does not exist, remove it and rebuild the §2 claim it carried from real sources | SC-14 | Critical | text: References "https://doi.org/10.5555/1042001" (Aoki 2019) through "https://doi.org/10.5555/1042012" (Silva & Tan 2021) | 4 — DOI registration practice verifiable from the manuscript text; the seat could not resolve identifiers from within review | R2 | P1 | 1–6 weeks (hours if the sources are real; a literature-review rebuild if they are not) |
| R2 | Remove every institution-linked role descriptor from quote attributions; state how quote-level disclosure risk was assessed and what consent covered regarding attributed criticism; return to participants if consent did not cover it | SC-3 | Critical | text: §3.5 "all data were fully anonymized prior to analysis so that no individual could be identified"; §4.1 "the quality director of the largest private university in the region" | 5 — EiC, 8 years of QA submissions with institutional-identifiability screening; R3 chairs an ethics committee; R1 confidence 4 (consent wording unavailable) | EiC, R1, R3 (+DA C4) | P1 | 1 week for redaction; 4+ weeks if re-consent is required |
| R3 | Reinstate the excluded dissenting accounts, re-analyse with them included, report what they contest and whether the three-theme structure survives them, and withdraw the balanced-representation and full-range claims | SC-2 | Critical | text: §4.3 "capturing the full range of administrator views on QA implementation"; "these were excluded for space, as they fell outside the three-theme structure that organized our analysis" | 5 — R1 teaches negative-case analysis and trustworthiness criteria in a doctoral mixed-methods seminar | EiC, R1, R3 (+DA C3) | P1 | 3–4 weeks |
| R4 | Resolve the Delacroix reading in one direction, rewrite whichever of §2 or §5 loses, and rebuild the third design recommendation on a source that actually supports it | SC-1 | Critical | text: §5 "who recommends that institutions treat broad stakeholder consultation as the central mechanism for building a healthy quality culture"; §2 "cautions that participatory rhetoric can itself become a compliance ritual" | 5 — contradiction internal to the manuscript, no external verification required | EiC, R1, R2, R3 (+DA C1) | P1 | 1–2 weeks |
| R5 | Withdraw the sector-wide and universal claims; rescope every finding to the three institutions; add an operative limitations section that constrains §5–§6 rather than deferring to future work | SC-4 | Major | text: §5 "these findings demonstrate that universities across the sector treat QA as a negotiated accomplishment rather than a managerial output"; "administrators everywhere face the same fundamental tension" | 5 — evidence-to-claim scope judgement fully contained in the reported design | EiC, R1, R2, R3 (+DA C2) | P1 | 1 week |
| R6 | Reconcile the interview count; state the number interviewed, the number analysed, and the disposition of any difference, including whether the missing two are the §4.3 dissenters | SC-18 | Major (arbitrated — SPLIT resolution above) | text: Abstract "Fourteen administrators were interviewed in depth"; §3.2 "Twelve senior administrators (n=12) with direct QA responsibilities" | 5 — direct textual comparison, no domain judgement required | EiC, R1, R2, R3 (+DA M1) | P1 | 2 days |
| R7 | Report the qualitative analytic procedure at a reconstructable level: named tradition, number of coders, codebook or coding tree, agreement position appropriate to the tradition, audit trail, positionality relative to the QA offices that acted as recruitment gatekeepers, and an evidenced stopping rule in place of "a stable structure was reached" | — | Major | text: §3.4 "Coding proceeded iteratively, moving between transcripts and an emerging set of themes until a stable structure was reached" | 5 — standard reporting bar in the journals this seat reviews for | R1 | P1 | 2 weeks |
| R8 | Supply the survey instrument (item wording, item count, scale anchors, aggregation rule) with reliability or validity evidence; report the population denominator, response rate, and subgroup counts by institution and role summing to 48; then either report the inferential test in full (family, statistic, df, effect size with confidence interval, assumption checks) or reframe the contrast descriptively | SC-5, SC-6 | Major | absence: §3.3 survey instrumentation — expected item wording or appended instrument, item count, response-scale anchors, reliability/validity evidence; checked §3.3, §3.4, §4.4, Abstract, reference list. text: §4.4 "we found a statistically significant difference (p<.05)" | 5 (test reporting); 4 (instrumentation — cannot rule out an instrument existing but unreported) | R1, EiC, R2 (+DA M4) | P1 | 2–3 weeks |
| R9 | Re-specify "quality culture" with its structural-managerial component restored, and separate external QA compliance, internal quality management, and quality culture throughout; re-read all three themes against the re-specified construct | SC-5 | Major | text: §1 "the shared values, practices, and commitments through which an institution takes collective ownership of its own standards"; §4.1 "We produce beautiful evidence portfolios that nobody reads except the panel." | 5 — the dual-construct formulation and the three-way practitioner distinction are standard in this literature | R2, EiC, R1 | P1 | 3–4 weeks |
| R10 | State the specific increment this study adds over Pettersen (2022), Rahman (2020), and Silva & Tan (2021), and compare the findings against theirs; let the identity-work reading carry the originality | SC-7, SC-20 | Major (arbitrated — SPLIT resolution above; EiC upheld on substance) | text: §6 "This paper has offered the first comprehensive account of how university administrators experience and enact QA implementation"; §2 "This latter turn is closest in spirit to the present study." | 5 — venue-level familiarity with the three adjacent published works | EiC (+R1, R2, DA M5) | P1 | 1–2 weeks |
| R11 | Specify the national system, external QA regime type (accreditation, audit, or evaluative-state), responsible agency, and position in the review cycle at system level, coordinating with R2 so that no regime detail combined with the stated site typology re-identifies a post-holder; where detail is withheld for confidentiality, say so and say what is lost | SC-8, SC-21 | Major (arbitrated — both demands upheld, not averaged) | absence: §3.2 Participants and setting — expected identification of the national system, external QA regime type, responsible agency, and position in the review cycle; checked §1, §3.2, §3.3, §4 findings, §5 discussion | 5 (R2 — routine reporting requirement for comparative QA research); 4 (R3 — comparative reader of regulated-sector regimes) | R2, R3 | P1 | 1 week |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | Add an integration mechanism: a joint display mapping the three themes against survey dimensions, plus an explicit statement of sequence, point of interface, and how strand divergence would have been handled — or drop the mixed-methods label from title and abstract | SC-11 | Major | absence: §3.1 and §4.4 mixed-methods integration — expected a stated point of interface with a joint display or narrative weaving linking specific survey results to specific themes; checked §3.1, §3.4, §4.4, §5 | 5 — integration is this seat's declared teaching and reviewing specialism | R1 | P2 | 2 weeks |
| S2 | Resolve the survey's role into one reading — divergent or corroborative, not both — handle divergence as the finding it is, and propagate the resolved reading to the abstract | SC-12 | Major | text: §4.4 "The survey corroborated the qualitative picture"; "the interview accounts had led us to anticipate a more skeptical picture"; §5 "The survey adds a note of complication" | 5 — internal-consistency reading, no external knowledge required | R1 (+DA M3) | P2 | 1 week |
| S3 | Engage the generic organizational literature the three themes restate — decoupling and ceremonial conformity, institutional logics, identity work, audit culture — and state explicitly which mechanisms are field-specific to higher education QA and which travel to any audited profession | SC-9 | Major | absence: §2 and reference list — expected named engagement with institutional decoupling and ceremonial conformity, identity-work, and distributed-leadership theory, plus boundary conditions separating higher education QA from other audited professions; checked §2 three strands, §4 theme labels, §5, §6, all twelve references | 5 — organizational sociologist working on decoupling, institutional logics, and professional identity work | R3, R2 | P2 | 3–4 weeks |
| S4 | Either narrow the negotiation claim to how administrators construe the negotiation, or add academic and external-body accounts | SC-13 | Major | text: §6 "an ongoing negotiation among administrators, academics, and external bodies"; §3.2 "recruited through institutional QA offices" | 4 — standard assessment of evidentiary sufficiency for multi-actor claims | R3 | P2 | 1 week (rescope) or a new data-collection phase |
| S5 | Remove the inference that protocol fixity rules out site-specific artefact; if any cross-institutional claim is retained, support it with analysis reported by site | SC-19 | Major (arbitrated — substance retained at R1's band) | text: §4.1 "These themes emerged systematically from the structured protocol"; "not an artifact of any single institution's local circumstances" | 5 — both the contradiction and the invalid inference are on the page | R1 (+DA M2) | P2 | 1 week |
| S6 | Supply per-theme participant counts or institutional distribution to support "most pervasive," "recurred across every interview," and "administrators consistently described" | — | Major (DA band) | absence: §4.1 to §4.3 and §3.4 — expected per-theme participant counts or institutional distribution supporting "most pervasive" and "recurred across every interview"; checked §3.4, §4.1–§4.3, Abstract theme summary, §5 | 3 — qualitative reporting conventions vary, universal claims still need a basis | DA (M6) | P2 | 1 week |
| S7 | Specify two or three concrete QA design changes the interview data support — to what artefact, at what point in the cycle, replacing what — in place of "processes that create room for meaning-making" | SC-17 | Minor | text: §6 "processes that create room for meaning-making rather than merely demanding documentation" | 4 — works with QA and accreditation practitioners across regulated sectors | R3 | P2 | 1 week |
| S8 | Replace "possible moderator" with a descriptive between-site difference worth examining in future work; do not repair by fitting a moderation model to these cells, and note that with one institution per type, type and institution are perfectly confounded | SC-15 | Minor | text: §4.4 "points to institutional type as a possible moderator of quality culture" | 5 — standard modelling vocabulary | R1 (+DA M4) | P3 | 1 day |
| S9 | Fix the semi-structured/structured description mismatch between §3.1 and §4.1 | SC-19 | Minor (arbitrated — text component of the SPLIT) | text: §3.1 "semi-structured interviews"; §4.1 "These themes emerged systematically from the structured protocol" | 5 — straightforward internal inconsistency in method description | EiC, R1 (+DA M2) | P3 | 1 day |
| S10 | Reconcile the stated subgroup analysis plan with the analysis actually reported | SC-16 | Minor | text: §3.4 "subgroup comparisons were examined where role categories permitted"; §4.4 "Comparing staff at the research university (n=9) with staff at the teaching-focused university (n=11)" | 4 — plan-to-report mismatch is clear; whether it reflects analytic flexibility is not determinable from the text | EiC | P3 | 1 day |
| S11 | Delete "first" and "comprehensive" from §6; the accurate claim is available in the manuscript — the first interview-based account of administrator meaning-making in this setting | SC-7, SC-20 | Minor (arbitrated — text component; the positioning deficit is R10) | text: §6 "This paper has offered the first comprehensive account of how university administrators experience and enact QA implementation" | 4 — the counter-evidence is the manuscript's own §2 | R1, R2 (+EiC, DA M5) | P3 | 1 day |
| S12 | Remove the inline annotation from the Delacroix reference entry; no venue style admits this apparatus | SC-10 | Minor | text: References, the Delacroix (2018) entry carries an inline annotation reading "Delacroix argues against relying on stakeholder consultation as evidence of quality culture" | 5 — venue reference conventions admit no such apparatus | EiC, R2 | P3 | 1 hour |
| S13 | Add numbered tables for the quantitative reporting; the paper currently reports a mean, an SD, and a significance test with no table or figure anywhere | SC-6 | Minor | absence: full manuscript — checked Abstract, §3.3, §3.4, §4.4 and the whole text for any numbered table or figure | 4 — editorial reporting-standards judgement | EiC | P3 | 2 days |

> Every row above carries the driving finding's transported Severity, its typed Evidence Anchor, and its per-finding Confidence, taken from the reviewer cards rather than re-derived. No `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` tags were needed: all five cards carry per-finding Severity and Confidence in current format. Where a SPLIT was arbitrated, the row marks the band as arbitrated and the arbitration is recorded in Part 1 rather than silently applied.

### Required Item Details

**R1 — Verify or rebuild the reference apparatus**
- **Acceptance criteria**: All twelve reference entries resolve to retrievable records, or every non-existent entry is removed and each §2 claim it carried is rebuilt from a verifiable source.

**R2 — Redact re-identifying attributions and document disclosure-risk assessment**
- **Acceptance criteria**: No quote attribution links a role to an institution's type, size, sector, or region, and §3.5 states how quote-level disclosure risk was assessed and what consent covered regarding attributed criticism.

**R3 — Reinstate and re-analyse the dissenting accounts**
- **Acceptance criteria**: The dissenting accounts are analysed and reported, the manuscript states what they contest and whether the theme structure survives them, and the balanced-representation and full-range claims are removed.

**R4 — Resolve the Delacroix reading**
- **Acceptance criteria**: §2 and §5 attribute one and the same position to Delacroix (2018), and the third design recommendation is supported by a source that argues for it.

**R5 — Rescope the generalisation and add operative limitations**
- **Acceptance criteria**: No claim in §5 or §6 extends beyond the three studied institutions, and a limitations section states the scope constraint rather than deferring it to future work.

**R6 — Reconcile the interview count**
- **Acceptance criteria**: One interview count appears throughout, with the number interviewed, the number analysed, and the disposition of any difference stated in §3.2.

**R7 — Report the qualitative analytic procedure**
- **Acceptance criteria**: §3.4 names the analytic tradition, the number of coders, the codebook or coding tree, the agreement position appropriate to that tradition, the audit trail, author positionality relative to the recruiting QA offices, and an evidenced stopping rule.

**R8 — Make the quantitative strand reportable**
- **Acceptance criteria**: The survey instrument, item count, scale anchors, aggregation rule, reliability or validity evidence, population denominator, response rate, and subgroup counts summing to 48 are reported, and the subgroup contrast is either reported in full (family, statistic, df, effect size with confidence interval, assumption checks) or reframed descriptively.

**R9 — Re-specify the construct and separate the three QA objects**
- **Acceptance criteria**: "Quality culture" is defined with both its cultural and structural components, external QA compliance and internal quality management and quality culture are distinguished at every point of use, and all three themes are re-read against the re-specified construct.

**R10 — State the contribution increment**
- **Acceptance criteria**: The manuscript states what it adds beyond Pettersen (2022), Rahman (2020), and Silva & Tan (2021) and compares its findings against theirs.

**R11 — Specify the regulatory context**
- **Acceptance criteria**: The national system, external QA regime type, responsible agency, and position in the review cycle are stated at system level without re-identifying any post-holder, and any detail withheld for confidentiality is named as withheld with its cost stated.

### Revision Checklist

#### Priority 1 — Structural Revisions (Estimated total effort: 12–20 weeks, R1-dependent)
- [ ] R1: Verify or rebuild the reference apparatus (do this first — everything downstream depends on it)
- [ ] R2: Redact re-identifying attributions; document disclosure-risk assessment; re-consent if required
- [ ] R3: Reinstate and re-analyse the dissenting accounts; withdraw the coverage claims
- [ ] R4: Resolve the Delacroix reading in one direction; rebuild the third recommendation
- [ ] R5: Rescope to the three institutions; add an operative limitations section
- [ ] R6: Reconcile the interview count and the disposition of the difference
- [ ] R7: Report the qualitative analytic procedure at a reconstructable level
- [ ] R8: Make the quantitative strand reportable, or reframe it descriptively
- [ ] R9: Re-specify "quality culture"; separate the three QA constructs
- [ ] R10: State the contribution increment over the three adjacent studies
- [ ] R11: Specify the regulatory context, coordinated with R2

#### Priority 2 — Content Supplementation (Estimated total effort: 8–10 weeks)
- [ ] S1: Add an integration mechanism, or drop the mixed-methods label
- [ ] S2: Resolve the survey's corroborative/divergent role into one reading
- [ ] S3: Engage the generic organizational literature; state what is field-specific
- [ ] S4: Narrow the negotiation claim, or add the missing parties' accounts
- [ ] S5: Remove the protocol-fixity inference; report by site if site claims are retained
- [ ] S6: Supply per-theme participant counts or institutional distribution
- [ ] S7: Specify concrete, executable QA design changes

#### Priority 3 — Text and Formatting (Estimated total effort: 1 week)
- [ ] S8: Replace "moderator" with a descriptive between-site difference; note the type/institution confound
- [ ] S9: Fix the semi-structured/structured description mismatch
- [ ] S10: Reconcile the stated subgroup analysis plan with the analysis reported
- [ ] S11: Delete "first" and "comprehensive" from §6
- [ ] S12: Remove the inline annotation from the Delacroix reference entry
- [ ] S13: Add numbered tables for the quantitative reporting

### Revision Deadline

Not applicable. The decision is Reject, so no revision clock runs and no re-review of a revised version is scheduled at this venue. The estimated effort above is a rebuild scale, not a deadline: on the panel's own assessment, Priority 1 is 12–20 weeks of work, dominated by R1's outcome and by whether R2 requires returning to participants.

Three seats identified a defensible thesis surviving underneath — that quality culture in these three institutions is negotiated rather than delivered, held open by administrators as identity work — and R2 named the §4.3 identity material as publishable if the foundations were sound. If the authors complete the Priority 1 work, the reframed study is a legitimate exploratory three-site paper. The field-analysis input recommends *Quality in Higher Education*, *Journal of Higher Education Policy and Management*, and *Higher Education Quarterly* as targets for a rebuilt version, with *Tertiary Education and Management* or a regional practitioner QA outlet as the fallback if the empirical base cannot be strengthened.

### Response Letter Template

If the authors submit a rebuilt version to this or another venue, they should respond to every item above using the format in `templates/revision_response_template.md`, one entry per item identifier (R1–R11, S1–S13), stating the change made and its location, or the reasoned ground for declining. Items R1–R11 carry no "respectfully decline" option: R1–R5 rest on unanimous or near-unanimous panel agreement or on the fatal block, and R6–R11 on arbitrated resolutions recorded in Part 1.

---

## Part 3: Reviewer Report Summary (Appendix)

The panel operated under a sprint contract, so seats emitted dimension scores rather than Accept/Revise/Reject recommendations. Scores are reported on assessed dimensions only.

### Journal-Fit Reviewer (EiC) — dimensions D5, D6
- D5 `block`; D6 `block` (`repairable`) | 10 findings, per-finding confidence 4–5
- Key point: the manuscript is inside the remit and has an identifiable original contribution in the identity-work theme, but it advertises "the first comprehensive account" without positioning against the three adjacent studies its own §2 names, and it cannot be audited by a reader who cannot determine the sample size, the survey scale, or the analytic denominator.

### Peer Reviewer 1 (Methodology) — dimensions D1, D3
- D1 `block` (`repairable`); D3 `block` (`repairable`) | 14 findings, per-finding confidence 4–5; 4 Arithmetic Receipts, all `not_computable` or `not_applicable`
- Key point: excluding participants because their accounts fell outside the structure the analysis was supposed to derive from the accounts inverts the direction of inference and is the paper's most serious defect; the quantitative strand is unrecomputable in principle because no scale, item count, test family, or statistic is reported.

### Peer Reviewer 2 (Domain) — dimension D2
- D2 `block` (`fatal`) | 8 findings, per-finding confidence 4–5
- Key point: all twelve references carry the reserved 10.5555 test prefix with sequential suffixes in alphabetical order and none resolves, so no claim in §2 is checkable; separately, §5 inverts Delacroix and §1 defines "quality culture" with its structural component removed, which manufactures the paper's central culture-versus-management contrast out of its own truncated definition.

### Peer Reviewer 3 (Cross-disciplinary Perspective) — dimension D4
- D4 `block` | 9 findings, per-finding confidence 4–5
- Key point: the three findings are established organizational phenomena renamed without engaging the literature that owns them, so the paper cannot say what is specific to higher education QA; and the sector-wide claims are made from a case whose regime, stakes, and consequence structure are all withheld.

### Devil's Advocate — dimension D3
- D3 `block` (`repairable`) | 4 CRITICAL, 6 MAJOR, per-finding confidence 3–5
- Key point: the argumentative chain breaks in four independent places, and in three of them the manuscript contradicts itself in adjacent text rather than merely overreaching; a defensible thesis survives underneath, but reaching it is a substantial rebuild of §4 and §5, not a rhetorical trim.
