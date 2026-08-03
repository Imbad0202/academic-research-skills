# Editorial Decision Package

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size: 5`
**Synthesis mode:** v3.6.2 Sprint Contract Synthesizer Protocol (arithmetic). All 5 reviewer cards present and usable; no `[PANEL-SHRUNK]`.

---

## Part 0: Contract Audit (mechanical)

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats | Excluded (ineligible `not_assessed`) | Verdict |
|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | methodology | methodology = `block` (repairable) | eic, domain, perspective, da | block |
| D2 domain_accuracy | mandatory | domain | domain = `block` (repairable) | eic, methodology, perspective, da | block |
| D3 argumentative_coherence | mandatory | da, methodology | da = `block` (repairable); methodology = `block` (repairable) | eic, domain, perspective | block |
| D4 cross_disciplinary_relevance | high | perspective | perspective = `block` (no `block_class`) | eic, methodology, domain, da | block |
| D5 writing_and_structure | normal | eic | eic = `block` (no `block_class`; card states no fatality class attaches) | methodology, domain, perspective, da | block |
| D6 venue_fit_and_contribution | mandatory | eic | eic = `block` (repairable) | methodology, domain, perspective, da | block |

Every dimension has ≥1 assessed eligible seat — no `[DIMENSION-UNASSESSED]`. No abstentions among eligible seats. No seat declared a **fatal** block on any dimension.

`audit_verdict: block`

### Step 2 — Failure-condition evaluation

| ID | Sev | Cross-reviewer quantifier | Expression (recognised pattern) | Per-dimension booleans | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | `any mandatory dimension has a fatal block` (pattern: fatal, mandatory scope — valid) | D1 F, D2 F, D3 F, D6 F | **false** |
| F2 | 90 | any | `any mandatory dimension scores 'block'` | D1 T, D2 T, D3 T (≥1 of {da, methodology}), D6 T | **true** |
| F3 | 70 | majority | `two or more mandatory dimensions score 'warn' or worse` | D1 T (n=1 → owner seat), D2 T (n=1), D3 T (n=2 → both seats block), D6 T (n=1) → 4 ≥ 2 | **true** |
| F4 | 60 | any | `any high-priority dimension scores 'block'` | D4 T | **true** |
| F5 | 40 | any | `any dimension scores 'warn' or worse` | D1–D6 all T | **true** |
| F0 | 10 | all | `every dimension scores 'pass'` | none T | **false** |

### Step 3 — Precedence, decision, audit emission

Fired set = {F2, F3, F4, F5}. Highest `severity` = **F2 (90)** → `action: editorial_decision=major_revision`. No tie-break required.

```
dimension_verdicts: [D1=block, D2=block, D3=block, D4=block, D5=block, D6=block]
fired_conditions: [F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED]
editorial_decision=major_revision
```

Mechanical decision is not `accept`, so no `[DA-CRITICAL-VS-ACCEPT]` marker applies.

`ARS_CROSS_MODEL` not set → Step 4b cross-model blind decision check not run; no behavioral change.

**Card-completeness flags (surfaced, not fixed — Phase Boundary forbids me augmenting reviewer cards):**
`[CARD-INCOMPLETE: eic — D5 block has no block_class line; W4 has no per-finding Confidence line]`
`[CARD-INCOMPLETE: perspective — D4 block has no block_class line]`
Neither gap affects the arithmetic: F1 requires a *declared* fatal block, and an absent `block_class` is not a fatal declaration. The missing eic W4 confidence is carried into the roadmap as `[CONFIDENCE-SOURCE: absent-in-card]` (the card supplies no report-level Confidence Score either, so the standard `report-level` fallback is unavailable).

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript "Building Institutional Quality Culture: Administrator Perspectives on Quality Assurance Implementation in Universities." It was assessed by five reviewers: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary perspective), and a Devil's Advocate.

### Decision: Major Revision

All six contract dimensions returned `block`. No reviewer declared any block fatal, and four of the five explicitly recorded their block as repairable. The panel's collective position is that the study's empirical material and its central question are worth publishing, and that the manuscript as submitted cannot be assessed on its merits because several of its load-bearing claims are contradicted by its own text.

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-ABSENT]` No provenance stamp was supplied with this dispatch. I therefore make **no** statement that a cross-model slot was active, and **no** assertion of model independence across the five seats. Readers should assume, absent a stamp, that cross-family independence has not been established for this panel. This block is required in `reviewer_full` mode and is not omitted; its content is limited to what the dispatch actually recorded.

### Consensus Analysis

Consensus is computed over the **4 non-DA reviewers** (Journal-Fit / EIC, R1 methodology, R2 domain, R3 perspective), per sub-claim, denominator always 4. Silence (`not-mentioned`) is not agreement. Devil's Advocate findings are adjudicated separately and do not enter the count.

#### Points of agreement

**[CONSENSUS-4]**

- **SC-2** — The §3.5 anonymisation guarantee is contradicted by role-plus-institution descriptors in §4.1/§4.2 that identify single post-holders. (R2 bands this Minor but explicitly defers to the methodology seat's higher banding; that is deference, not dissent.)
- **SC-3** — Dissenting participants were excluded because they fell outside the theme structure the analysis was meant to produce. The structure was validated against a corpus from which non-conforming cases had been removed.
- **SC-4** — The adjacent claim of "balanced representation… capturing the full range of administrator views" is falsified by that exclusion, on the manuscript's own account.
- **SC-5** — §5 attributes to Delacroix (2018) the position that consultation is "the central mechanism" for quality culture, while §2 and the reference annotation both record him as arguing against exactly that.
- **SC-7** — §5/§6 generalise from three institutions in one national system to "universities across the sector," "the sector as a whole," and "administrators everywhere," and §6 then concedes the generalisation has not been earned.
- **SC-8** — §6's "first comprehensive account" priority claim is contradicted by the manuscript's own literature review.
- **SC-13** — The p<.05 subgroup claim names no test and reports no statistic, effect size, or interval, on n=9 vs n=11.
- **SC-15** — The survey instrument is undocumented (no provenance, items, scale range, anchors, or reliability), so M=3.9 cannot be interpreted.
- **SC-23** — Abstract reports fourteen interviews; §3.2 reports twelve, twice, once numerically.

**[CONSENSUS-3]** (the fourth reviewer is silent, not opposed — named)

- **SC-6** — Correcting Delacroix runs *against* §5's recommendation, because the paper's own ritual-compliance theme is evidence for his warning. Raised by EIC, R2, R3; **R1 silent** on this specific consequence.
- **SC-9** — Each of the three themes maps onto a source the paper itself cites (Iversen/Okonkwo, Pettersen, Rahman); the genuinely novel increment occupies roughly a paragraph. Raised by EIC, R2, R3; **R1 silent**.
- **SC-11** — §4.1's "structured protocol" warrant contradicts the semi-structured design declared in §3.1/§3.3. Raised by EIC, R1, R3; **R2 silent**.
- **SC-14** — The survey sample cannot be reconstructed: 9 + 11 = 20 of 48, with no frame, response rate, or per-site breakdown. Raised by R1, R3, EIC; **R2 silent**.
- **SC-16** — "Quality culture" is never operationally defined and slides between quality culture, QA, compliance behaviour, and institutional culture. Raised by EIC, R2, R3; **R1 silent**.

**Corroborated findings (2/4, no conflict — action-bearing, below the consensus bar)**

- **SC-18** — The field's constitutive pre-2018 literature is absent and §2 misdescribes the quality-culture strand as "still emergent" (R2, conf 5 — dimension owner; EIC, conf 4).
- **SC-20** — §4.4 labels a disconfirming survey result "corroboration" and performs no integration (R1 conf 5; R3 conf 4).
- **SC-21** — The administrator/staff cross-level divergence, the only cross-level evidence collected, is deferred rather than analysed (R3 conf 4; R1 conf 5 corroborating).

**Single-reviewer findings (1/4, no conflict — weighted by confidence, not arbitrated)**

SC-10 qualitative procedure unreportable (R1, conf 5, D1 owner — full weight); SC-19 the mechanism is described but never named or theorised (R3, conf 5, D4 owner — full weight); SC-22 the three-party negotiation claim rests on one party's data (R3, conf 5 — full weight); SC-29 the sole practical recommendation is non-actionable (EIC, conf 5 — full weight); SC-17 quality culture reported as a single scalar (R2, conf 4); SC-12 shared-regulatory-environment confound (R3, conf 4); SC-24 uncalibrated prevalence language (R1, conf 4); SC-25 no reproducibility affordances (R1, conf 5); SC-26 national QA regime unnamed (R2, conf 3 — standard weight); SC-27 no numbered table or figure (EIC, conf 5); SC-28 word count far below venue norm (EIC, conf 4).

#### Points of disagreement

One genuine SPLIT was found. Every other sub-claim had `conflict = 0`.

- **SC-1 — status of the unverifiable references.** EIC (conf 5) records that all twelve DOIs sit on the reserved `10.5555/` test prefix, numbered `1042001`–`1042012` in alphabetical order of first author, bands it **Critical**, and holds that no recommendation — including a revise recommendation — should issue until resolvable identifiers are supplied. R2 (conf 3) accepts the prefix status as fact, bands it **Minor**, treats it as a production or anonymisation artifact, and explicitly declines to infer fabrication.

  **Editor's Resolution (Journal-Fit arbitration).** Evidence first: the two seats do not disagree about any verifiable proposition. EIC's confidence 5 attaches to the checkable observation (reserved prefix, sequential numbering), and EIC expressly leaves the fabrication inference to the editorial office; R2's confidence 3 attaches only to the *reason* for the prefix. The disagreement is therefore a severity-band conflict, not an existence conflict. I sustain **both** positions on the grounds each seat actually states: the panel finds that **no cited source can be verified by any reviewer**, and the panel makes **no finding that the references are fabricated**. I carry EIC's Critical band, because the ground EIC states — traceability of claims — is independently sufficient and unaffected by the unresolved question of cause. Consequence recorded for the author: the D2 source-fidelity assessment, including the Delacroix finding, currently rests on internal comparison within the manuscript alone. Required action is identical under both readings, so it becomes roadmap item R1 and is a prerequisite to verifying R4, R17, and R20.

  This resolution does not average the two positions and does not soften F2's action.

### Devil's Advocate CRITICAL adjudication

| ID | DA argument | Corroborated by | Journal-Fit assessment | Required author response |
|---|---|---|---|---|
| **C1** | §5's design recommendation is attributed to a source the paper reports as arguing the opposite; the reversal is load-bearing for the third of three stated contributions. | EIC W7, R1 W10, R2 W1, R3 W7 — all four non-DA reviewers | **VALIDATED.** The contradiction is internal to the manuscript and requires no external checking. R2, the dimension owner, additionally establishes that the correct reading points against the recommendation. | Address in full: R4 and R5. |
| **C2** | Comprehensiveness is claimed in the same paragraph that declares disconfirming cases were removed for failing to fit the theme structure the analysis produced. | EIC W3, R1 W1, R2 W6, R3 W6 — all four | **VALIDATED.** Stated by the authors in adjacent sentences; R1 (D1 owner, conf 5) treats it as an analytic defect, not a reporting omission. | Address in full: R2 and R3. |
| **C3** | The Methods anonymisation guarantee is contradicted by Findings attributions that uniquely identify speakers by role plus institution. | EIC W2, R1 W3, R2 W9, R3 W5 — all four; R3 assessed it as a former research-ethics committee member | **VALIDATED.** Not a stylistic matter: consent was obtained on the §3.5 basis. | Address in full: R6. |

No DA CRITICAL was rejected, so no rejection rationale is required. DA MAJOR findings M1–M9 are recorded in the roadmap where they add a claim not already carried by a non-DA reviewer (see S7, S10); the remainder duplicate consensus items above.

### Decision Rationale

The decision is `major_revision` under F2: four mandatory dimensions carry a `block` from their eligible seats. F3, F4, and F5 also fired; F2's severity of 90 governs.

The pattern the panel converges on is not a set of isolated errors but a manuscript that asserts, at three load-bearing points, the opposite of what its own text records. §4.3 claims full-range coverage in the sentence after disclosing that dissenting cases were removed for not fitting the themes. §5 recruits Delacroix in support of a recommendation §2 records him as opposing. §5 generalises to the sector and §6 retracts the generalisation two sentences later. Each is repairable, and none requires new fieldwork — but repair means rewriting the Findings, Discussion and Conclusion, restoring and re-analysing the excluded cases, and building the positioning literature. That is new analytic work, which is why the Journal-Fit seat found that rescoping the claims alone cannot deliver a publishable contribution.

Two seat-level tensions the panel flagged in advance were resolved rather than averaged. On R1-versus-EIC: R1 came to the manuscript inclined to read missing procedure as a write-up failure and abandoned that reading at §4.3, which describes an analytic decision rather than an omitted description. I adopt R1's revised position, so the required repair is re-analysis, not a longer Methods paragraph. On R2-versus-R3: both literature absences are real and neither displaces the other. R2's field-specific positioning (R17) carries the greater depth for a quality-assurance readership; R3's mechanism naming (R18) is scoped to roughly two paragraphs in §2 plus a reframing of §5's second finding, which is what R3 themselves asked for.

What must not be lost in revision: the gap statement in §2 is precisely drawn and honestly attributed; §4.3's reading of the compliance/meaning gap as the site where administrative identity is located is the one finding not already covered by the paper's own citations, and three seats independently named it the paper's best contribution; and the administrator/staff perceptual divergence in §4.4 is a genuinely informative result that the paper currently discards. Build the revised paper around those three.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | Disconfirming cases were excluded by the theme structure they should have tested, and the paper simultaneously claims full-range coverage. The three-theme finding — the core empirical claim — cannot be credited as reported. | R1 (Critical, conf 5), R3 (Critical, conf 4), EIC (Critical, conf 4), R2 (Major, conf 4), DA C2 | text: §4.3 "the study achieved balanced representation of perspectives, capturing the full range of administrator views" alongside "these were excluded for space, as they fell outside the three-theme structure" | R2 |
| 2 | The sole practical recommendation rests on a 180-degree inversion of Delacroix (2018); the correct reading is supported by the paper's own ritual-compliance theme and points against the recommendation. Sole trigger of the D2 block. | R2 (Critical, conf 5), EIC (Major, conf 5), R1 (Major, conf 5), R3 (Major, conf 4), DA C1 | text: §5 "who recommends that institutions treat broad stakeholder consultation as the central mechanism" vs §2 "argues *against* treating stakeholder consultation as sufficient evidence of a healthy quality culture" | R4 |
| 3 | The §3.5 anonymisation guarantee is falsified by uniquely identifying descriptors attached to professionally damaging quotations, in a study of twelve elite post-holders across three type-labelled institutions. Consent was obtained on the §3.5 basis. | EIC (Critical, conf 5), R1 (Critical, conf 5), R3 (Critical, conf 5), R2 (Minor, conf 4, deferring), DA C3 | text: §3.5 "all data were fully anonymized prior to analysis so that no individual could be identified" vs §4.1 "the quality director of the largest private university in the region" | R6 |

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. A DA-only item with no sub-claim id uses `—`.
>
> **Severity, Evidence Anchor and Confidence are transported from the reviewer cards, never re-derived.** Where seats banded a sub-claim differently, all transported bands are shown; where the SPLIT arbitration selected a band, that is marked `arb.`
>
> **Priority assignment.** Priority follows whether the item gates clearing a blocked contract dimension, with the consensus level recorded per row. Two rows depart from the default consensus→priority correspondence and say so: **R17** (SC-18, a 2/4 corroborated finding) is P1 because R8 and R16 cannot be completed without it, and **R18** / **R19** / **R20** carry single-reviewer findings at P1 because each is a stated driver of a scored block on a mandatory or high-priority dimension by that dimension's owner seat at confidence 5.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Est. Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Supply resolvable identifiers for all twelve references; prerequisite to verifying R4, R17, R20 | SC-1 | Critical (EIC) / Minor (R2) — **arb. Critical** | text: References, Aoki (2019) & Silva & Tan (2021) "https://doi.org/10.5555/1042001", "…/1042012" | 5 (EIC, prefix check) / 3 (R2, cause) | EIC, R2 — **SPLIT arbitrated** | P1 | 1–2 d |
| R2 | Reinstate the excluded dissenting cases and re-derive the theme structure against them | SC-3 | Critical (R1, R3, EIC) / Major (R2) | text: §4.3 "these were excluded for space, as they fell outside the three-theme structure" | 5 (R1) / 4 (R3, EIC, R2) | R1, R3, EIC, R2, DA C2 | P1 | 10–15 d |
| R3 | Retract the balanced-representation / full-range claim, or make it true against the reinstated corpus | SC-4 | Critical (R1, R3, EIC) / Major (R2) | text: §4.3 "the study achieved balanced representation of perspectives, capturing the full range of administrator views" | 5 (R1) / 4 (R3, EIC, R2) | R1, R3, EIC, R2, DA C2 | P1 | 1 d |
| R4 | Correct §5's Delacroix attribution to the position stated in §2 and the reference annotation | SC-5 | Critical (R2) / Major (EIC, R1, R3) | text: §5 "who recommends that institutions treat broad stakeholder consultation as the central mechanism" | 5 (R2, EIC, R1) / 4 (R3) | R2, EIC, R1, R3, DA C1 | P1 | 1 d |
| R5 | Re-derive §5's third finding from Delacroix's actual argument, using the paper's own ritual-compliance theme | SC-6 | Critical (R2) / Major (EIC, R3) | text: §2 "an institution can hold elaborate consultations and still lack any genuine ownership of standards" | 5 (R2, EIC) / 4 (R3) | R2, EIC, R3 (**R1 silent**), DA C1 | P1 | 4–6 d |
| R6 | Redact role-plus-institution descriptors throughout §4; restate §3.5 to what anonymisation achieved; state consent scope for attributed quotation | SC-2 | Critical (EIC, R1, R3) / Minor (R2, deferring) | text: §4.1 "the quality director of the largest private university in the region" | 5 (EIC, R1, R3) / 4 (R2) | EIC, R1, R3, R2, DA C3 | P1 | 2–3 d |
| R7 | Retract the sector-wide generalisation; rescope §5/§6 with a bounded transferability statement naming the regime | SC-7 | Major (EIC, R1, R2, R3) | text: §5 "these findings demonstrate that universities across the sector treat QA as a negotiated accomplishment" and "administrators everywhere face the same fundamental tension" | 5 (EIC, R1, R3) / 4 (R2) | EIC, R1, R2, R3, DA M2 | P1 | 2–3 d |
| R8 | Delete or qualify the "first comprehensive account" priority claim | SC-8 | Major (EIC, R2) / Minor (R3, deferring) | text: §6 "This paper has offered the first comprehensive account of how university administrators experience and enact QA implementation" | 4 (EIC, R2, R3) | EIC, R2, R3, R1 | P1 | 1 d |
| R9 | Report the qualitative analytic procedure in full: coding approach, codebook, coder count and reconciliation, trustworthiness strategies | SC-10 | Critical (R1) | absence: §3.4 Analysis — expected a codebook or coding framework, inductive vs template statement, number of coders and reconciliation procedure, named trustworthiness strategies; checked §3.4, §3.1, §4.1–§4.3, absent appendices | 5 (R1, D1 owner) | R1 | P1 | 4–6 d |
| R10 | Reconcile the fourteen/twelve participant count; re-check every count-dependent statement | SC-23 | Major (EIC, R1) / Minor (R2, R3) | text: Abstract "Fourteen administrators were interviewed in depth" vs §3.2 "Twelve senior administrators (n=12)" | 5 (all four) | EIC, R1, R2, R3, DA M1 | P1 | 0.5 d |
| R11 | Supply the interview protocol and correct §3.1/§3.3, or withdraw §4.1's "structured protocol" robustness warrant | SC-11 | Major (EIC, R1) / Minor (R3) | text: §4.1 "These themes emerged systematically from the structured protocol" vs §3.1 "semi-structured" | 5 (R1) / 4 (EIC, R3) | R1, EIC, R3 (**R2 silent**), DA M4 | P1 | 1–2 d |
| R12 | Document the survey instrument (provenance, items, scale range and anchors, reliability) so M=3.9 is interpretable | SC-15 | Major (R1, R2, R3, EIC) / Minor (EIC W11) | absence: §3.3 Data collection — expected instrument provenance, item wording, response scale range and anchors, internal consistency estimate; checked §3.3, §3.4, §4.4, abstract, reference list | 5 (R1, EIC) / 4 (R2, R3) | R1, R2, R3, EIC, DA M9 | P1 | 2–3 d |
| R13 | Supply the full inferential apparatus for the p<.05 subgroup claim, or present the contrast descriptively | SC-13 | Major (R1, R3) / Minor (EIC) | text: §4.4 "we found a statistically significant difference (p<.05) in perceived quality culture" | 5 (R1, EIC) / 4 (R3, R2) | R1, R3, EIC, R2, DA M5 | P1 | 1–2 d |
| R14 | Reconstruct the survey sample: frame, recruitment, eligibility, response rate, per-institution breakdown reconciling 9+11 against 48 | SC-14 | Major (R1, R3) / Minor (EIC) | absence: §3.2 Participants and setting — expected survey sampling frame, recruitment route, response rate, per-institution breakdown reconciling 9 and 11 against 48; checked §3.2, §3.3, §4.4, abstract | 4 (R1, R3) / 5 (EIC) | R1, R3, EIC (**R2 silent**) | P1 | 2–3 d |
| R15 | Reframe §4.4 and §5 as strand divergence, not corroboration, and state an integration procedure | SC-20 | Major (R1, R3) | text: §4.4 "The survey corroborated the qualitative picture" then "the interview accounts had led us to anticipate a more skeptical picture" | 5 (R1) / 4 (R3) | R1, R3, DA M3 | P1 | 3–4 d |
| R16 | State an operational definition of quality culture distinguishing it from QA, compliance behaviour, and institutional culture | SC-16 | Major (EIC, R2, R3) | absence: Abstract, §1, §2, §3, §4.4 — expected a stated operational definition of quality culture distinguishing it from quality assurance, institutional culture, and compliance behaviour | `[CONFIDENCE-SOURCE: absent-in-card]` (EIC W4) / 4 (R2, R3) | EIC, R2, R3 (**R1 silent**) | P1 | 3–4 d |
| R17 | Rebuild §2's positioning in the field's constitutive pre-2018 literature; correct the "still emergent" characterisation | SC-18 | Major (R2, EIC) | absence: §2 quality-culture strand and reference list — expected engagement with EUA Quality Culture Project; Harvey & Green 1993; Harvey & Stensaker 2008; Newton 2000, 2002; the audit-culture tradition; checked all 12 references, §1, §2 ¶1–3, §5 | 5 (R2, D2 owner) / 4 (EIC) | R2, EIC — corroborated 2/4, P1 by dependency (gates R8, R16) | P1 | 10–15 d |
| R18 | Name and theorise the mechanism the ritual-compliance theme describes; state its scope conditions | SC-19 | Major (R3) | absence: §2 Literature Review and §5 Discussion — expected citation of neo-institutional decoupling, ceremonial conformity, and audit-society scholarship naming the mechanism the findings describe; checked all three strands of §2, first two findings in §5, 12-item reference list | 5 (R3, D4 owner) | R3 — single-reviewer, P1 as stated D4 block driver | P1 | 4–6 d |
| R19 | Rescope §6's three-party negotiation claim to the party actually sampled, or sample the missing parties | SC-22 | Major (R3) | text: §6 "an ongoing negotiation among administrators, academics, and external bodies" | 5 (R3, D4 owner) | R3 — single-reviewer, P1 as stated D4 block driver | P1 | 2–3 d |
| R20 | Reformulate the contribution around the defensible increment and make the practical implication actionable | SC-9, SC-29 | Major (EIC, R2) / Minor (R3) | text: §2 ¶3 "Pettersen (2022) and Rahman (2020), meanwhile, turn attention toward the quality office itself, examining how distributed leadership and professional identity shape the work" | 4 (EIC, R2, R3) / 5 (EIC on SC-29) | EIC (D6 owner), R2, R3 (**R1 silent**), DA M6 | P1 | 6–8 d |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Est. Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Analyse the administrator/staff cross-level divergence with the data already collected | SC-21 | Major (R3, R1) | text: §5 "a divergence worth pursuing in future work" | 4 (R3) / 5 (R1) | R3, R1 — corroborated 2/4 | P2 | 4–6 d |
| S2 | Report quality culture dimensionally rather than as a single scalar | SC-17 | Major (R2) | text: §4.4 "respondents' overall institutional quality culture score was moderately positive (M=3.9, SD=0.6)" | 4 (R2) | R2 | P2 | 2–3 d |
| S3 | Calibrate prevalence and saturation language to reported evidence, or soften it | SC-24 | Minor (R1) | text: §4.2 "This relational, distributed understanding of leadership recurred across every interview" | 4 (R1) | R1, DA M7 | P2 | 1 d |
| S4 | Add a data/protocol/codebook availability statement and appendices for shareable materials | SC-25 | Minor (R1) | absence: whole manuscript — expected a data, protocol, or codebook availability statement and any appendix supporting independent replication; checked §3 in full, §4.4, §6, and the position where appendices would appear | 5 (R1) | R1 | P2 | 1 d |
| S5 | Identify the national QA regime at regime-type level so the described machinery can be checked | SC-26 | Minor (R2) | absence: §3.2 setting description — expected identification of the national QA regime and its review framework at regime-type level; checked §1, §2, §3.1–§3.3, §5, §6 | 3 (R2) | R2 | P2 | 0.5 d |
| S6 | Soften the cross-site recurrence inference; address the shared-regulatory-environment confound | SC-12 | Minor (R3) | text: §4.1 "giving us confidence that the pattern was not an artifact of any single institution's local circumstances" | 4 (R3) | R3, DA M4 | P2 | 1 d |
| S7 | Distinguish coping resource from sincere vocational commitment or interviewer-directed performance, or soften the inference | — | Major band (DA) | text: §4.3 "This vocational framing appeared to function as a coping resource" | 4 (DA M8) | DA (M8, non-CRITICAL) | P2 | 1–2 d |
| S8 | Expand the manuscript toward the venue's normal length for an empirical article | SC-28 | Major (EIC) | absence: References list and §2 — expected engagement with pre-2018 foundational QA and quality-culture literature; checked all twelve reference entries, §1, §2, §5 | 4 (EIC) | EIC | P2 | absorbed by R2, R9, R17 |
| S9 | Add numbered, captioned tables/figures for all quantitative reporting | SC-27 | Minor (EIC) | absence: §3.3, §3.4, §4.4 — expected a numbered table reporting survey instrument, items, scale, response rate, subgroup means and the test statistic behind the reported p-value; checked abstract, §3.3, §3.4, §4.4, and full manuscript for any numbered table or figure | 5 (EIC) | EIC | P3 | 1 d |
| S10 | Replace demonstrative verbs ("demonstrate," "confirms") with verbs available to interpretive thematic work | — | Major band (DA) | text: §5 "these findings demonstrate" and "confirms long-standing concerns" | 5 (DA M2) | DA (M2 part), R2 (review body) | P3 | 0.5 d |

No item on this roadmap was built from an aggregated Minor-Issues editorial channel; every row transports a named reviewer finding, so no row carries `source_kind: "editorial"`.

### Required Item Details

**R1 — Resolvable reference identifiers**
- **Acceptance criteria**: All twelve references carry identifiers that resolve to a deposited record, and any reference that cannot be resolved is removed with every claim resting on it re-sourced or withdrawn.

**R2 — Reinstate and re-analyse the excluded dissenting cases**
- **Acceptance criteria**: The dissenting accounts are reinstated in the analysed corpus and reported as data, and each of the three themes is restated to account for them, with any theme that does not survive revised or dropped.

**R3 — Withdraw or substantiate the representativeness claim**
- **Acceptance criteria**: No sentence in §4 claims balanced representation or full-range coverage unless the reinstated corpus supports it; otherwise the analysis is described as characterising a subset.

**R4 — Correct the Delacroix attribution**
- **Acceptance criteria**: §5 states Delacroix's position as §2 and the reference annotation state it, with no residual sentence presenting him as recommending consultation as the central mechanism.

**R5 — Re-derive the participation recommendation**
- **Acceptance criteria**: §5's third finding is derived from Delacroix's actual argument and names at least one observable feature distinguishing genuine participation from participation ritual, tested against the interview material.

**R6 — Participant protection and anonymisation**
- **Acceptance criteria**: No quotation in §4 is attributed by a descriptor combining role with institution or institutional superlative, §3.5 states what anonymisation actually achieved, and the consent scope for attributed quotation is stated.

**R7 — Rescope the generalisation**
- **Acceptance criteria**: No claim in §5 or §6 extends beyond three institutions in one national system, and a bounded transferability statement names the regime studied.

**R8 — Withdraw the priority claim**
- **Acceptance criteria**: The "first comprehensive account" claim is deleted or replaced by a contribution claim the paper's own literature review supports.

**R9 — Report the qualitative analytic procedure**
- **Acceptance criteria**: §3.4 reports the coding approach (inductive or template-based), the codebook or coding framework, the number of coders and their reconciliation procedure, and at least one named trustworthiness strategy.

**R10 — Reconcile the participant count**
- **Acceptance criteria**: The abstract and §3.2 report the same participant count, every count-dependent statement in §4 is re-checked against it, and any excluded cases are stated with their disposition.

**R11 — Resolve the protocol contradiction**
- **Acceptance criteria**: Either the interview protocol is supplied and §3.1/§3.3 corrected, or §4.1's "structured protocol" warrant is withdrawn and the robustness claim rewritten.

**R12 — Document the survey instrument**
- **Acceptance criteria**: §3.3 or an appendix reports the instrument's provenance, item wording, response-scale range and anchors, and an internal-consistency estimate, and §4.4 reports M=3.9 against the stated scale.

**R13 — Supply or withdraw the inferential claim**
- **Acceptance criteria**: §4.4 either names the test and reports the test statistic, degrees of freedom, effect size, interval and number of comparisons run, or presents the contrast descriptively with no inferential verdict.

**R14 — Reconstruct the survey sample**
- **Acceptance criteria**: §3.2 or §3.3 reports the survey sampling frame, recruitment route, eligibility definition, response rate, and per-institution breakdown, and the subgroup Ns reconcile against the stated total of 48.

**R15 — Reframe the strand relationship as divergence**
- **Acceptance criteria**: §4.4 and §5 describe the survey result as divergent from the interview-derived expectation, and a stated integration procedure joins the two strands.

**R16 — Operationally define quality culture**
- **Acceptance criteria**: A single operational definition of quality culture appears before §4, distinguishes it from quality assurance, compliance behaviour and institutional culture, and is used consistently thereafter.

**R17 — Rebuild the field positioning**
- **Acceptance criteria**: §2 engages the field's constitutive pre-2018 quality-assurance and quality-culture literature, and no sentence characterises the quality-culture strand as still emergent.

**R18 — Name and theorise the mechanism**
- **Acceptance criteria**: §2 and §5 name the mechanism the ritual-compliance theme describes, cite its literature, and state the scope conditions under which it is expected to form.

**R19 — Rescope the negotiation claim**
- **Acceptance criteria**: §6's negotiation claim names only parties represented in the collected data, or the missing parties are sampled.

**R20 — Reformulate the contribution and the practical implication**
- **Acceptance criteria**: The contribution claim identifies what the data add beyond Iversen, Okonkwo, Pettersen, Rahman and Silva & Tan, and §5's practical implication names at least one process feature a quality office could change.

### Revision Checklist

#### Priority 1 — Structural revisions (estimated 60–85 working days)
- [ ] R1: Supply resolvable reference identifiers — do this first; R4, R17 and R20 depend on it
- [ ] R2: Reinstate and re-analyse the excluded dissenting cases — do this before R3, R9, R11, R20; the themes may change
- [ ] R3: Withdraw or substantiate the full-range representation claim
- [ ] R4: Correct the §5 Delacroix attribution
- [ ] R5: Re-derive §5's third finding from Delacroix's actual argument
- [ ] R6: Redact identifying descriptors; restate §3.5; state consent scope
- [ ] R7: Rescope §5/§6 to three sites in one national system
- [ ] R8: Withdraw or qualify the "first comprehensive account" claim
- [ ] R9: Report the full qualitative analytic procedure
- [ ] R10: Reconcile fourteen/twelve and re-check count-dependent statements
- [ ] R11: Supply the protocol or withdraw the §4.1 robustness warrant
- [ ] R12: Document the survey instrument
- [ ] R13: Supply the inferential apparatus or go descriptive
- [ ] R14: Reconstruct and reconcile the survey sample
- [ ] R15: Reframe §4.4/§5 as divergence with a stated integration procedure
- [ ] R16: State an operational definition of quality culture
- [ ] R17: Rebuild §2's positioning in the pre-2018 literature
- [ ] R18: Name and theorise the mechanism; state scope conditions
- [ ] R19: Rescope the three-party negotiation claim
- [ ] R20: Reformulate the contribution; make the practical implication actionable

#### Priority 2 — Content supplementation (estimated 10–15 working days)
- [ ] S1: Analyse the administrator/staff cross-level divergence — highest-value P2 item
- [ ] S2: Report quality culture dimensionally
- [ ] S3: Calibrate prevalence and saturation language
- [ ] S4: Add availability statement and appendices
- [ ] S5: Identify the national QA regime at regime-type level
- [ ] S6: Address the shared-regulatory-environment confound
- [ ] S7: Distinguish coping resource from sincere commitment or interviewer-directed performance
- [ ] S8: Bring length to venue norm (largely absorbed by R2, R9, R17)

#### Priority 3 — Text and formatting (estimated 1–2 working days)
- [ ] S9: Add numbered, captioned tables/figures for quantitative reporting
- [ ] S10: Replace demonstrative verbs with verbs available to interpretive thematic work

### Sequencing note

R1, R10, R4 and R6 are cheap and unblock verification, so do them first. R2 must precede R3, R9, R11 and R20, because restoring the negative cases may change what the themes are — the methodology seat was explicit that reporting repairs should not be attempted before the re-analysis. R17 gates R8 and R16.

### Revision deadline

**8 weeks** (Major Revision, upper end of the recommended band). Re-review after revision is required, and the panel expects to re-examine R2, R4, R6, R9 and R17 directly.

### Response letter

Use `templates/revision_response_template.md`. Respond to every numbered item R1–R20 and S1–S10 individually, quoting the revised text and its location. Items R2, R4 and R6 correspond to Devil's Advocate CRITICAL findings C2, C1 and C3, all three adjudicated VALIDATED; each requires an explicit response.

---

## Part 3: Reviewer Report Summary (Appendix)

These cards are sprint-contract cards: they carry dimension scores and per-finding severity/confidence rather than an overall recommendation or a single report-level confidence score. The summary reflects what the cards state.

**Journal-Fit Reviewer (EIC)** — D5 `block`, D6 `block` (repairable); D1–D4 `not_assessed`. Key point: the topic and the hinge-actor hook are genuinely in scope, but the manuscript fails three submission-readiness gates before any substantive question arises, and cutting the claims to the evidence would leave three replicated themes at 2,400 words — the contribution needs new analytic work, not rescoping.

**Peer Reviewer 1 (Methodology)** — D1 `block` (repairable), D3 `block` (repairable); D2, D4–D6 `not_assessed`. Key point: §4.3 describes an analytic decision, not a reporting omission, so the three-theme structure was validated against a pruned corpus and the required repair is re-analysis; the survey strand as reported cannot carry any inferential weight.

**Peer Reviewer 2 (Domain)** — D2 `block` (repairable); all others `not_assessed`. Key point: the Delacroix inversion sits at the exact point where the paper builds its recommendation, and Delacroix's actual argument is supported by the paper's own ritual-compliance finding; separately, the argument was not built from the field's constitutive literature, which is why quality culture is never defined and the novelty claim is not sustainable.

**Peer Reviewer 3 (Cross-disciplinary perspective)** — D4 `block`; all others `not_assessed`. Key point: the paper describes ceremonial conformity and means–ends decoupling without naming the mechanism, then substitutes a claim about scope for the claim about mechanism its data could support; the administrator/staff divergence is the paper's most informative result and is exactly what decoupling predicts.

**Devil's Advocate** — D3 `block` (repairable); all others `not_assessed`. Key point: the chain from evidence to conclusion breaks at three load-bearing points, and at each break the paper asserts the opposite of what its own text records; all repairs are achievable without new fieldwork but require rewriting the Discussion and Conclusion rather than softening them.

---

## Schema 7 — Machine-form Roadmap

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "stage": "reviewer_full_review",
  "decision": "major_revision",
  "panel_size": 5,
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": ["eic", "domain"], "sub_claims": ["SC-1"], "severity": "critical", "severity_note": "arbitrated to eic band; domain banded minor", "evidence_anchor": "text: References, Aoki (2019) and Silva & Tan (2021) https://doi.org/10.5555/1042001, .../1042012", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "All twelve references carry identifiers that resolve to a deposited record, and any reference that cannot be resolved is removed with every claim resting on it re-sourced or withdrawn."},
    {"id": "R2", "priority": "must_fix", "reviewer": ["methodology", "perspective", "eic", "domain", "da"], "sub_claims": ["SC-3"], "severity": "critical", "evidence_anchor": "text: §4.3 'these were excluded for space, as they fell outside the three-theme structure'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "The dissenting accounts are reinstated in the analysed corpus and reported as data, and each of the three themes is restated to account for them, with any theme that does not survive revised or dropped."},
    {"id": "R3", "priority": "must_fix", "reviewer": ["methodology", "perspective", "eic", "domain", "da"], "sub_claims": ["SC-4"], "severity": "critical", "evidence_anchor": "text: §4.3 'the study achieved balanced representation of perspectives, capturing the full range of administrator views'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "No sentence in §4 claims balanced representation or full-range coverage unless the reinstated corpus supports it; otherwise the analysis is described as characterising a subset."},
    {"id": "R4", "priority": "must_fix", "reviewer": ["domain", "eic", "methodology", "perspective", "da"], "sub_claims": ["SC-5"], "severity": "critical", "evidence_anchor": "text: §5 'who recommends that institutions treat broad stakeholder consultation as the central mechanism'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "§5 states Delacroix's position as §2 and the reference annotation state it, with no residual sentence presenting him as recommending consultation as the central mechanism."},
    {"id": "R5", "priority": "must_fix", "reviewer": ["domain", "eic", "perspective", "da"], "sub_claims": ["SC-6"], "severity": "critical", "evidence_anchor": "text: §2 'an institution can hold elaborate consultations and still lack any genuine ownership of standards'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "§5's third finding is derived from Delacroix's actual argument and names at least one observable feature distinguishing genuine participation from participation ritual, tested against the interview material."},
    {"id": "R6", "priority": "must_fix", "reviewer": ["eic", "methodology", "perspective", "domain", "da"], "sub_claims": ["SC-2"], "severity": "critical", "evidence_anchor": "text: §4.1 'the quality director of the largest private university in the region'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "No quotation in §4 is attributed by a descriptor combining role with institution or institutional superlative, §3.5 states what anonymisation actually achieved, and the consent scope for attributed quotation is stated."},
    {"id": "R7", "priority": "must_fix", "reviewer": ["eic", "methodology", "domain", "perspective", "da"], "sub_claims": ["SC-7"], "severity": "major", "evidence_anchor": "text: §5 'these findings demonstrate that universities across the sector treat QA as a negotiated accomplishment' and 'administrators everywhere face the same fundamental tension'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "No claim in §5 or §6 extends beyond three institutions in one national system, and a bounded transferability statement names the regime studied."},
    {"id": "R8", "priority": "must_fix", "reviewer": ["eic", "domain", "perspective", "methodology"], "sub_claims": ["SC-8"], "severity": "major", "evidence_anchor": "text: §6 'This paper has offered the first comprehensive account of how university administrators experience and enact QA implementation'", "confidence": 4, "source_kind": "reviewer_finding", "verification_criteria": "The 'first comprehensive account' claim is deleted or replaced by a contribution claim the paper's own literature review supports."},
    {"id": "R9", "priority": "must_fix", "reviewer": ["methodology"], "sub_claims": ["SC-10"], "severity": "critical", "evidence_anchor": "absence: §3.4 Analysis - expected codebook or coding framework, inductive vs template statement, number of coders and reconciliation procedure, named trustworthiness strategies", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "§3.4 reports the coding approach (inductive or template-based), the codebook or coding framework, the number of coders and their reconciliation procedure, and at least one named trustworthiness strategy."},
    {"id": "R10", "priority": "must_fix", "reviewer": ["eic", "methodology", "domain", "perspective", "da"], "sub_claims": ["SC-23"], "severity": "major", "evidence_anchor": "text: Abstract 'Fourteen administrators were interviewed in depth' vs §3.2 'Twelve senior administrators (n=12)'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "The abstract and §3.2 report the same participant count, every count-dependent statement in §4 is re-checked against it, and any excluded cases are stated with their disposition."},
    {"id": "R11", "priority": "must_fix", "reviewer": ["methodology", "eic", "perspective", "da"], "sub_claims": ["SC-11"], "severity": "major", "evidence_anchor": "text: §4.1 'These themes emerged systematically from the structured protocol' vs §3.1 'semi-structured'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "Either the interview protocol is supplied and §3.1/§3.3 corrected, or §4.1's 'structured protocol' warrant is withdrawn and the robustness claim rewritten."},
    {"id": "R12", "priority": "must_fix", "reviewer": ["methodology", "domain", "perspective", "eic", "da"], "sub_claims": ["SC-15"], "severity": "major", "evidence_anchor": "absence: §3.3 Data collection - expected instrument provenance, item wording, response scale range and anchors, internal consistency estimate", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "§3.3 or an appendix reports the instrument's provenance, item wording, response-scale range and anchors, and an internal-consistency estimate, and §4.4 reports M=3.9 against the stated scale."},
    {"id": "R13", "priority": "must_fix", "reviewer": ["methodology", "perspective", "eic", "domain", "da"], "sub_claims": ["SC-13"], "severity": "major", "evidence_anchor": "text: §4.4 'we found a statistically significant difference (p<.05) in perceived quality culture'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "§4.4 either names the test and reports the test statistic, degrees of freedom, effect size, interval and number of comparisons run, or presents the contrast descriptively with no inferential verdict."},
    {"id": "R14", "priority": "must_fix", "reviewer": ["methodology", "perspective", "eic"], "sub_claims": ["SC-14"], "severity": "major", "evidence_anchor": "absence: §3.2 Participants and setting - expected survey sampling frame, recruitment route, response rate, per-institution breakdown reconciling 9 and 11 against 48", "confidence": 4, "source_kind": "reviewer_finding", "verification_criteria": "§3.2 or §3.3 reports the survey sampling frame, recruitment route, eligibility definition, response rate, and per-institution breakdown, and the subgroup Ns reconcile against the stated total of 48."},
    {"id": "R15", "priority": "must_fix", "reviewer": ["methodology", "perspective", "da"], "sub_claims": ["SC-20"], "severity": "major", "evidence_anchor": "text: §4.4 'The survey corroborated the qualitative picture' then 'the interview accounts had led us to anticipate a more skeptical picture'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "§4.4 and §5 describe the survey result as divergent from the interview-derived expectation, and a stated integration procedure joins the two strands."},
    {"id": "R16", "priority": "must_fix", "reviewer": ["eic", "domain", "perspective"], "sub_claims": ["SC-16"], "severity": "major", "evidence_anchor": "absence: Abstract, §1, §2, §3, §4.4 - expected a stated operational definition of quality culture distinguishing it from quality assurance, institutional culture, and compliance behaviour", "confidence": null, "confidence_note": "CONFIDENCE-SOURCE: absent-in-card (eic W4); domain and perspective transported 4", "source_kind": "reviewer_finding", "verification_criteria": "A single operational definition of quality culture appears before §4, distinguishes it from quality assurance, compliance behaviour and institutional culture, and is used consistently thereafter."},
    {"id": "R17", "priority": "must_fix", "reviewer": ["domain", "eic"], "sub_claims": ["SC-18"], "severity": "major", "evidence_anchor": "absence: §2 quality-culture strand and reference list - expected engagement with EUA Quality Culture Project, Harvey & Green 1993, Harvey & Stensaker 2008, Newton 2000 and 2002, the audit-culture tradition", "confidence": 5, "source_kind": "reviewer_finding", "priority_note": "corroborated 2/4; assigned must_fix by dependency - gates R8 and R16", "verification_criteria": "§2 engages the field's constitutive pre-2018 quality-assurance and quality-culture literature, and no sentence characterises the quality-culture strand as still emergent."},
    {"id": "R18", "priority": "must_fix", "reviewer": ["perspective"], "sub_claims": ["SC-19"], "severity": "major", "evidence_anchor": "absence: §2 Literature Review and §5 Discussion - expected citation of neo-institutional decoupling, ceremonial conformity, and audit-society scholarship naming the mechanism the findings describe", "confidence": 5, "source_kind": "reviewer_finding", "priority_note": "single-reviewer; assigned must_fix as stated D4 block driver by the D4 owner seat", "verification_criteria": "§2 and §5 name the mechanism the ritual-compliance theme describes, cite its literature, and state the scope conditions under which it is expected to form."},
    {"id": "R19", "priority": "must_fix", "reviewer": ["perspective"], "sub_claims": ["SC-22"], "severity": "major", "evidence_anchor": "text: §6 'an ongoing negotiation among administrators, academics, and external bodies'", "confidence": 5, "source_kind": "reviewer_finding", "priority_note": "single-reviewer; assigned must_fix as stated D4 block driver by the D4 owner seat", "verification_criteria": "§6's negotiation claim names only parties represented in the collected data, or the missing parties are sampled."},
    {"id": "R20", "priority": "must_fix", "reviewer": ["eic", "domain", "perspective", "da"], "sub_claims": ["SC-9", "SC-29"], "severity": "major", "evidence_anchor": "text: §2 ¶3 'Pettersen (2022) and Rahman (2020), meanwhile, turn attention toward the quality office itself, examining how distributed leadership and professional identity shape the work'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "The contribution claim identifies what the data add beyond Iversen, Okonkwo, Pettersen, Rahman and Silva & Tan, and §5's practical implication names at least one process feature a quality office could change."},
    {"id": "S1", "priority": "should_fix", "reviewer": ["perspective", "methodology"], "sub_claims": ["SC-21"], "severity": "major", "evidence_anchor": "text: §5 'a divergence worth pursuing in future work'", "confidence": 4, "source_kind": "reviewer_finding", "verification_criteria": "§5 analyses the administrator/staff divergence using the collected data and states a candidate explanation with its testable implication, rather than deferring it to future work."},
    {"id": "S2", "priority": "should_fix", "reviewer": ["domain"], "sub_claims": ["SC-17"], "severity": "major", "evidence_anchor": "text: §4.4 'respondents' overall institutional quality culture score was moderately positive (M=3.9, SD=0.6)'", "confidence": 4, "source_kind": "reviewer_finding", "verification_criteria": "§4.4 reports the quality-culture measure by dimension against a named framework rather than as a single aggregate."},
    {"id": "S3", "priority": "should_fix", "reviewer": ["methodology", "da"], "sub_claims": ["SC-24"], "severity": "minor", "evidence_anchor": "text: §4.2 'This relational, distributed understanding of leadership recurred across every interview'", "confidence": 4, "source_kind": "reviewer_finding", "verification_criteria": "Every prevalence claim in §4 is either supported by reported per-theme case counts or softened to non-universal wording."},
    {"id": "S4", "priority": "should_fix", "reviewer": ["methodology"], "sub_claims": ["SC-25"], "severity": "minor", "evidence_anchor": "absence: whole manuscript - expected a data, protocol, or codebook availability statement and any appendix supporting independent replication", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "The manuscript carries an availability statement covering the interview guide, coding framework and survey instrument, with appendices or a named repository."},
    {"id": "S5", "priority": "should_fix", "reviewer": ["domain"], "sub_claims": ["SC-26"], "severity": "minor", "evidence_anchor": "absence: §3.2 setting description - expected identification of the national QA regime and its review framework at regime-type level", "confidence": 3, "source_kind": "reviewer_finding", "verification_criteria": "§3.2 identifies the national QA regime type and its review framework at a level sufficient to check the described machinery."},
    {"id": "S6", "priority": "should_fix", "reviewer": ["perspective", "da"], "sub_claims": ["SC-12"], "severity": "minor", "evidence_anchor": "text: §4.1 'giving us confidence that the pattern was not an artifact of any single institution's local circumstances'", "confidence": 4, "source_kind": "reviewer_finding", "verification_criteria": "§4.1 acknowledges that a shared national regulatory environment and a common instrument can both produce cross-site convergence, and the artifact inference is softened accordingly."},
    {"id": "S7", "priority": "should_fix", "reviewer": ["da"], "sub_claims": [], "severity": "major", "evidence_anchor": "text: §4.3 'This vocational framing appeared to function as a coping resource'", "confidence": 4, "source_kind": "reviewer_finding", "verification_criteria": "§4.3 either states the evidence distinguishing a coping resource from sincere vocational commitment or interviewer-directed performance, or softens the inference to a description of the talk."},
    {"id": "S8", "priority": "should_fix", "reviewer": ["eic"], "sub_claims": ["SC-28"], "severity": "major", "evidence_anchor": "absence: References list and §2 - expected engagement with pre-2018 foundational quality-assurance and quality-culture literature", "confidence": 4, "source_kind": "reviewer_finding", "verification_criteria": "The revised manuscript reaches the venue's normal length for an empirical article, with the added length carrying analytic content from R2, R9 and R17 rather than expansion of existing prose."},
    {"id": "S9", "priority": "nice_to_fix", "reviewer": ["eic"], "sub_claims": ["SC-27"], "severity": "minor", "evidence_anchor": "absence: §3.3, §3.4, §4.4 - expected a numbered table reporting survey instrument, items, scale, response rate, subgroup means and the test statistic behind the reported p-value", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "All quantitative reporting appears in numbered, captioned tables or figures referenced from the text."},
    {"id": "S10", "priority": "nice_to_fix", "reviewer": ["da", "domain"], "sub_claims": [], "severity": "major", "evidence_anchor": "text: §5 'these findings demonstrate' and 'confirms long-standing concerns'", "confidence": 5, "source_kind": "reviewer_finding", "verification_criteria": "No verb in §5 or §6 asserts demonstration or confirmation of a claim that interpretive thematic analysis cannot establish."}
  ]
}
```
