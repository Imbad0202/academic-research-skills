# Editorial Synthesis — Sprint Contract `reviewer/reviewer_full/v2`

## Part 0: Sprint Contract Audit (mechanical)

### Step 1 — Role-scoped scoring matrix

Only seats whose `contract_role` appears in a dimension's `eligible_roles` are counted. Ineligible `not_assessed` values are excluded from both numerator and denominator.

| Dim | Priority | Eligible roles | Assessed eligible seats (score) | Excluded as ineligible | Dimension verdict |
|-----|----------|----------------|----------------------------------|------------------------|-------------------|
| D1 | mandatory | methodology | methodology = `block` (`block_class: fatal`) | eic, domain, perspective, da (all `not_assessed`) | `block(fatal)` |
| D2 | mandatory | domain | domain = `block` (`block_class: fatal`) | eic, methodology, perspective, da | `block(fatal)` |
| D3 | mandatory | da, methodology | da = `block` (repairable); methodology = `block` (repairable) | eic, domain, perspective | `block` |
| D4 | high | perspective | perspective = `block` (no `block_class`; fatal scope invalid on a non-mandatory dimension) | eic, methodology, domain, da | `block` |
| D5 | normal | eic | eic = `warn` | methodology, domain, perspective, da | `warn` |
| D6 | mandatory | eic | eic = `block` (repairable) | methodology, domain, perspective, da | `block` |

Every dimension has ≥1 assessed eligible seat. No `[DIMENSION-UNASSESSED]`. No eligible abstentions.

`audit_verdict: block(fatal)` — worst assessed eligible score, rendered fatal because D1 (methodology) and D2 (domain) each declared a fatal block.

### Step 2 — Failure-condition evaluation

| ID | Sev | Expression (parsed pattern) | Cross-reviewer stage | Dimension stage | Fired |
|----|-----|------------------------------|----------------------|-----------------|-------|
| F1 | 95 | `any <priority> dimension has a fatal block` → mandatory {D1,D2,D3,D6} | `any`: D1 ✓ (methodology fatal), D2 ✓ (domain fatal), D3 ✗ (both seats repairable), D6 ✗ (repairable) | `any` over {T,T,F,F} → **true** | **true** |
| F2 | 90 | `any <priority> dimension scores 'block'` → mandatory {D1,D2,D3,D6} | `any`: all four dimensions have ≥1 eligible seat at `block` | `any` → **true** | **true** |
| F3 | 70 | `two or more <priority> dimensions score 'warn' or worse` → mandatory {D1,D2,D3,D6} | `majority`: D1 n=1 → owner seat (block ✓); D2 n=1 → owner (✓); D3 n=2 → both seats (block, block ✓); D6 n=1 → owner (✓) | `two or more` over 4 true → **true** | **true** |
| F4 | 60 | `any <priority>-priority dimension scores 'block'` → high {D4} | `any`: perspective = block ✓ | `any` → **true** | **true** |
| F5 | 40 | `any dimension scores 'warn' or worse` → all dims | `any`: satisfied at D1–D6 (D5 alone suffices) | `any` → **true** | **true** |
| F0 | 10 | `every dimension scores 'pass'` | `all`: fails at D1 | **false** | false |

### Step 3 — Precedence and emission

Highest-severity fired condition: **F1 (severity 95)** → `action: editorial_decision=reject`.

```
dimension_verdicts: [D1=block(fatal), D2=block(fatal), D3=block, D4=block, D5=warn, D6=block]
fired_conditions: [F1, F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED]
editorial_decision=reject
```

No `[DA-CRITICAL-VS-ACCEPT]` marker: the mechanical decision is `reject`, not `accept`. No `[EXPRESSION-UNRECOGNISED]`, no `[PANEL-SHRUNK]`. All five cards were usable; `panel_size` = 5 as contracted. `ARS_CROSS_MODEL` not set → Step 4b not run, no behavioural change.

### Card-integrity notes (flagged, not fixed)

1. **perspective card** opens with a `## Scoring Plan Dissent` heading containing a placeholder, immediately self-retracted ("Disregarding the line above as a drafting artifact; no dissent section is emitted"). Read as emitting **no dissent**; no fatality is minted from it and no scoring-plan dissent is recorded. Flagged for the caller; not rewritten.
2. **perspective card** strengths S1–S3 carry no per-finding Confidence. Its weaknesses do; only strengths are affected, so no roadmap row depends on the gap.
3. **domain card** flags the §4.4 quantitative reporting in its Review Body without a Severity tag, explicitly deferring the verdict to the methodology seat. Rows sourced from that flag are marked `[SEVERITY-SOURCE: letter-fallback]`.
4. No card emits a report-level overall recommendation (sprint-contract cards score dimensions instead). Part 3 reports assessed dimensions in place of a recommendation.

### Surface-form parity check (#216)

All five cards are in comparable formal register, so no weight in this synthesis was adjusted on phrasing grounds. One re-weighting keys off substance and is stated explicitly: the perspective seat's `Minor` band on the sample-size discrepancy (SC-5) was arbitrated down in favour of `Major`, on the basis of (a) the discrepancy's interaction with the §4.3 exclusion — paper evidence, not wording — and (b) expertise-first deferral to the D1 owner seat on count reconciliation. Opposite-style counterfactual: rewriting that seat's hedge ("I may be over-reading a drafting error") in technical register would **not** change the arbitration, because the arbitration rests on the §4.3 interaction, not on the hedge. No sub-claim gained weight for technical specificity alone.

---

## Part 1: Editorial Decision Letter

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this is `reviewer_full` mode, so this block is mandatory, but the dispatching layer supplied no provenance stamp with the five cards. The stamp's content (cross-model slot active / single-family disclosure / dispatch-failure fallback) **must not be inferred**, and is therefore not stated here. The caller must supply the stamp before this letter is released to the author. No cross-family aggregate or "same-model majority" was computed; per-seat verdicts are visible by inspection in the Part 0 matrix.

---

Dear Author(s),

Thank you for submitting your manuscript "Building Institutional Quality Culture: Administrator Perspectives on Quality Assurance Implementation in Universities". It was assessed by five reviewers — a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary perspective), and a Devil's Advocate — against the venue's six acceptance dimensions. Venue as framed by the Journal-Fit seat: *Quality in Higher Education*.

### Decision: Reject

Two mandatory dimensions carry a **fatal** block from their owning reviewer: methodology rigour (D1) and domain accuracy (D2). Under this journal's decision contract, a fatal block on any mandatory dimension is a reject, and that is the decision recorded. The remaining dimensions are also blocked (D3 argumentative coherence, D4 cross-disciplinary relevance, D6 venue fit and contribution) or warned (D5 writing and structure), but they are not what drives the outcome.

I want to be plain about what this decision is and is not. It is not a judgement that the underlying study is worthless. Four of the five reviewers independently identified the same publishable insight — §4.3's finding that administrators hold the compliance/meaning tension open and locate professional identity in the gap. It is a judgement that the manuscript, as submitted, cannot be assessed on its substance, because its bibliography cannot be verified and its reported evidence base was reduced by removing the cases that would have tested its findings. Neither of those is repaired by revision of the text.

### Consensus Analysis

Consensus is counted over the four non-Devil's-Advocate seats, with the denominator fixed at 4. Silence is silence: a sub-claim that only one seat raised is a 1/4 finding, never a consensus. Weaknesses were decomposed into atomic sub-claims before counting, because several cards bundled two or more distinct claims into one weakness entry.

#### Points of Agreement

| SC | Sub-claim | EIC | METH | DOM | PERSP | DA | Count (agree/conflict/silent) | Disposition | Severity (transported) |
|----|-----------|-----|------|-----|-------|----|-------------------------------|-------------|------------------------|
| SC-1 | Reference set unverifiable: all 12 DOIs in the reserved `10.5555` test range, publisher prefixes contradicted, 3 journal titles unidentifiable | — | — | R | — | — | 1/0/3 | single-reviewer finding (D2 owner) | Critical (conf 5) |
| SC-2 | §5 attributes to Delacroix (2018) the reverse of the position §2 and the reference annotation give him | R | C | R | C | C1 | 4/0/0 | **CONSENSUS-4** | Critical (domain, D2 owner) / Major (EIC, METH, PERSP) |
| SC-3 | Dissenting participants excluded because they did not fit the three-theme structure, alongside a full-range coverage claim | R | R | R | R | C3 | 4/0/0 | **CONSENSUS-4** | Critical (METH, PERSP) / Major (EIC, DOM) |
| SC-4 | §3.5 anonymity guarantee falsified by role-plus-institution attributions in §4.1 | R | R | R | R | C4 | 4/0/0 | **CONSENSUS-4** | Major (all four) / Critical (DA) |
| SC-5 | Interview N reported as 14 (Abstract) and 12 (§3.2) | R | R | R | **D** | M1 | 3/1/0 | **[SPLIT]** — arbitrated below | Major (EIC, METH, DOM) vs Minor (PERSP) |
| SC-6 | Sector-wide and universal claims ("across the sector", "the sector as a whole", "administrators everywhere") from three sites in one system | R | R | R | R | C2 | 4/0/0 | **CONSENSUS-4** | Major (all four) |
| SC-7 | "First comprehensive account" priority claim, contradicted by the paper's own literature review | R | **D** | C | — | M5 | 2/1/1 | **[SPLIT]** — arbitrated below | Major (EIC, DOM) vs Minor (METH) |
| SC-8 | The contribution increment over Okonkwo (2018), Pettersen (2022), Rahman (2020), Silva & Tan (2021) is never argued | R | — | C | — | — | 2/0/2 | corroborated finding | Major (conf 5) |
| SC-9 | Survey instrument wholly unreported: no items, scale range/anchors, reliability, validity, sampling frame, response rate | C | R | R | C | M4 | 4/0/0 | **CONSENSUS-4** | Major (all four) |
| SC-10 | §4.4 subgroup significance claim unsupported: no named test, no means/dispersion, no effect size, no correction, institution collinear with group | C | R | C | C | M3 | 4/0/0 | **CONSENSUS-4** | Major (METH conf 5); DOM row `[SEVERITY-SOURCE: letter-fallback]` |
| SC-11 | 28 of 48 respondents unallocated; the private university has no reported subgroup | C | C | C | R | M4 | 4/0/0 | **CONSENSUS-4** | Minor (PERSP, the only atomic rating); band divergence is bundling-driven, not a severity conflict |
| SC-12 | §4.4 labels a divergent survey result "corroborat[ion]" in the same paragraph that reports the opposite expectation | — | R | — | — | M2 | 1/0/3 | single-reviewer finding (+DA) | Major (conf 5) |
| SC-13 | Thematic analysis non-reconstructable: no tradition, no stability criterion, no coder process, no trustworthiness check, no reflexivity | — | R | — | — | — | 1/0/3 | single-reviewer finding (D1 owner; EIC and DOM explicitly defer) | Major (conf 5) |
| SC-14a | Design described inconsistently: "semi-structured interviews" (§3.1) vs "the structured protocol" (§4.1) | R | R | R | R | M7 | 4/0/0 | **CONSENSUS-4** | Minor (EIC, DOM, PERSP); Major inside METH W7 bundle |
| SC-14b | §4.1's non-artifactuality warrant does not follow from protocol structure | C | R | — | C | M7 | 3/0/1 | **CONSENSUS-3** (silent: DOM) | Major (METH, D1/D3 owner) |
| SC-15 | Gatekeeper recruitment through the QA offices under study is never named as a selection pressure; no sampling logic reported | — | R | — | R | M8 | 2/0/2 | corroborated finding | Major (conf 5 both) |
| SC-16 | The national system, its regulatory model, funding/licensure linkage and review cycle are never identified | R | — | — | R | — | 2/0/2 | corroborated finding (drives both the D6 and D4 blocks) | Major (conf 5 both) |
| SC-17 | "Quality culture" never defined or operationalised; "QA" attaches to three different referents without acknowledgement | R | — | C | C | — | 3/0/1 | **CONSENSUS-3** (silent: METH) | Major (conf 5 / 4) |
| SC-18 | The §1 definition drops the structural/managerial component, making §5's "not a management output" conclusion partly definitional | — | — | R | — | — | 1/0/3 | single-reviewer finding (D2 owner) | Major (conf 5) |
| SC-19 | No theoretical framework declared, though the stated gap is a theorizing gap; adjacent-field vocabulary used without its source literatures | — | — | R | R | — | 2/0/2 | corroborated finding | Major (conf 4 / 5) |
| SC-20 | No source predates 2018; established field knowledge (decoupling, audit society, ritualism among quality staff) presented as emergent | — | — | R | C | — | 2/0/2 | corroborated finding | Major (conf 5) |
| SC-21 | Practical implications non-operational; documentation burden never quantified | — | — | — | R | — | 1/0/3 | single-reviewer finding | Major (conf 5) |
| SC-22 | No academic or student data, yet §6 prescribes QA processes for them | — | — | — | R | — | 1/0/3 | single-reviewer finding | Major (conf 5) |
| SC-24 | No reproducibility affordances: no protocol, codebook, instrument appendix, or data-availability statement | — | R | — | — | — | 1/0/3 | single-reviewer finding | Minor (conf 5) |
| SC-25 | Reference-list entry for Delacroix carries an editorial annotation | R | — | — | — | — | 1/0/3 | single-reviewer finding | Minor (conf 5) |
| SC-26 | Quantitative results delivered entirely in prose; the manuscript contains no tables or figures | R | — | — | — | — | 1/0/3 | single-reviewer finding (D5 warn driver) | Major (conf 4) |

`R` = raised, `C` = corroborated, `D` = disputed, `—` = not mentioned (silence, not opposition). Devil's-Advocate positions are recorded for visibility and are **not** in the count. Two DA-only findings are additionally carried into the roadmap: **SC-23** (§6's forward-looking causal claim about internalized commitment, from a study with no outcome measure; DA M6, Major, conf 5) and **SC-27** (§4.2's "recurred across every interview" universal, unsustainable over a corpus from which non-conforming cases were removed; DA M9, Major, conf 5). All rows carry per-finding severity and confidence transported from the cards; none was re-derived.

#### Points of Disagreement

**SC-5 — severity of the 14-vs-12 discrepancy.** The Journal-Fit, methodology and domain seats rate it Major; the perspective seat rates it Minor and self-flags possible over-reading of a drafting error (conf 4).
**Editor's resolution: Major.** Evidence-first: the two-participant gap is the same order of magnitude as the dissenting group §4.3 reports excluding, so the discrepancy is not severable from SC-3 and cannot be treated as a typographical matter until the exclusion is resolved. Expertise-first: count reconciliation sits with the D1 owner (conf 5). The perspective seat's own basis for the Minor band — uncertainty about cause — is precisely what the resolution of SC-3 will settle.

**SC-7 — is deleting the priority claim sufficient?** The methodology seat holds that "deleting the claim costs the paper nothing" (Minor). The Journal-Fit seat (D6 owner) and the domain seat hold that the claim is symptomatic of an unargued contribution requiring repositioning of §1, §2, §5 and §6 (Major).
**Editor's resolution: Major; both remedies required, in sequence.** The methodology seat is correct that the sentence itself is costless to strike, and it is confining itself properly to internal consistency, its own remit. But striking it leaves SC-8 — the increment over the paper's own cited work — unaddressed, and SC-8 is the stated driver of the D6 block. Expertise-first defers the contribution question to the D6 owner. Delete the claim **and** argue the increment (roadmap R13).

**SC-3 — remedy scope (recorded as deference, not conflict).** The methodology seat treats restoration of the excluded cases as requiring re-analysis whose outcome could change the theme structure, and grades the resulting D1 block fatal. The Journal-Fit and domain seats offer a disjunctive remedy ("restore the accounts **or** withdraw the representativeness claim"), which is a lighter reading — but both explicitly defer the analytic consequences to the methodology seat. That is deference, not dissent, so this is recorded as CONSENSUS-4 with the remedy resolved to the owner seat's stricter reading: withdrawing the claim without re-analysis is not sufficient, because §4.1's pervasiveness claim and §4.2's universal claim also rest on the reduced corpus.

**SC-12 — apparent contradiction between seats, resolved as locus-specific.** The methodology seat and the Devil's Advocate report that the manuscript mislabels divergence as corroboration; the domain and perspective seats each record, as a *strength*, that the manuscript reports the divergence honestly rather than smoothing it. Both are correct about different sentences: §4.4 opens "The survey corroborated the qualitative picture"; §5 calls the same result "a divergence worth pursuing". This is not a disputed position and was not counted as a SPLIT. Remedy: bring §4.4 into line with §5's framing (roadmap S5).

**SC-19 — which literature (a genuine choice, deliberately not averaged).** The domain seat routes the missing framework through the field's own canon (institutional decoupling, audit society, quality-culture typologies); the perspective seat routes it through the organizational sociology of professional work (street-level bureaucracy, institutional work, professional identity and coping). These are compatible on the requirement and different on the source, and they lead to different papers with different target venues. The choice belongs to the authors and must be made explicitly, not blended into a general instruction to engage more literature.

#### Devil's Advocate CRITICAL adjudications

All four DA CRITICAL findings are independently corroborated by the Journal-Fit seat's own weaknesses, and none was disputed by any seat. Adjudications are mine as arbitrator, on the on-page evidence; the Journal-Fit card was written in parallel and does not itself adjudicate the DA.

| ID | DA argument | Corroborated by | Assessment | Adjudication | Required author response |
|----|-------------|-----------------|------------|--------------|--------------------------|
| C1 | The Discussion's sole design recommendation is warranted by Delacroix (2018) with the source's thesis reversed | EIC W2, METH W12, DOM W2, PERSP W4 (4/4) | The manuscript states both readings; the reversed one carries §5's third implication and the paper's only prescription | **VALIDATED** | Resolve at R3; state which reading is correct and rebuild or withdraw the implication |
| C2 | Generalisation from 12 administrators at 3 sites to the whole sector, while §6 treats that generality as untested | EIC W8, METH W11, DOM W7, PERSP W1 (4/4) | Quantifiers ("demonstrate", "as a whole", "everywhere") compared against the stated sampling frame; the internal contradiction with §6 is on the page | **VALIDATED** | Rescope at R6; §6's forward-looking causal claim (DA M6) withdrawn with it |
| C3 | Disconfirming cases removed for non-fit with the finding, then completeness claimed on the reduced corpus | EIC W6, METH W1, DOM W9, PERSP W5 (4/4) | The stated exclusion criterion makes the theme structure unfalsifiable by the study's own data; §4.1's pervasiveness and §4.2's universal inherit the defect | **VALIDATED** — also the binding basis of the D1 fatal block | Re-analyse at R2; no completeness claim may survive without it |
| C4 | Role-plus-institution attributions identify individuals, contradicting the §3.5 anonymity guarantee | EIC W7, METH W8, DOM W10, PERSP W9 (4/4) | With one private and one public research university in the sample, singular office titles resolve to identifiable post-holders | **VALIDATED** | Remediate at R4 and correct §3.5 to describe what was actually done; this is a hard publication bar independent of every other item |

No DA CRITICAL was rejected, so no rejection rationale is required. The four DA MAJOR items not otherwise duplicated (M2→SC-12, M6→SC-23, M8→SC-15, M9→SC-27) are carried into the roadmap.

### Decision Rationale

The decision is Reject because two mandatory dimensions carry fatal blocks from the reviewers who own them, and both blocks concern the evidentiary foundation rather than its presentation.

The domain seat could not verify a single one of the twelve cited sources. All twelve DOIs sit in the reserved `10.5555` test range with sequential suffixes; for the eight entries naming real journals, the registered publisher prefixes are public record and differ; three journal titles are unidentifiable in the field. Because the paper's contribution is entirely literature-relative, the dimension could not be assessed on substance at all — not scored badly, but unassessable. The one internal check available worsened it: §5 attributes to Delacroix the reverse of what §2 and the paper's own reference annotation say he argued, and that reversal carries the paper's only design prescription.

The methodology seat's fatal block rests on §4.3. Participants with dissenting views were removed from the analysis *because* they fell outside the three-theme structure, and the adjacent sentence claims the study captured the full range of administrator views. A structure preserved by deleting the cases that would test it is not a finding about the data, and the disconfirming material has been excised from the analysis the Findings report. That cannot be repaired by adding description; the evidence would have to be regenerated.

Beyond these, the panel converged unanimously on four further contradictions internal to the manuscript — the sample size, the corroboration/divergence mislabelling, the anonymity guarantee, and the sector-wide generalisation — each visible on the page, each requiring one of two stated claims to be withdrawn. The prose quality and the §4.3 insight are real, and four seats named them. They do not change what the evidence base can currently support.

### Top Blocking Issues

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire reference set unverifiable — reserved `10.5555` DOI prefix, publisher prefixes contradicted, three unidentifiable journal titles; D2 cannot be assessed on substance (fatal) | DOM (W1, Critical, conf 5) | text: References, Ferreira & Lund (2022) and Okonkwo (2018) entries "https://doi.org/10.5555/1042004" "https://doi.org/10.5555/1042009" | R1 |
| 2 | Disconfirming cases excluded for non-fit with the three-theme structure while full-range coverage is claimed; the reported themes are an artefact of the exclusion (fatal) | METH (W1, Critical, conf 5); corroborated EIC W6, DOM W9, PERSP W5; DA C3 | text: §4.3 "balanced representation of perspectives, capturing the full range of administrator views"; "these were excluded for space, as they fell outside the three-theme structure" | R2 |
| 3 | §5 credits Delacroix (2018) with the opposite of the position the manuscript itself attributes to him; the paper's sole design recommendation rests on the inversion | DOM (W2, Critical, conf 5); corroborated EIC W2, METH W12, PERSP W4; DA C1 | text: §5 ¶4 "who recommends that institutions treat broad stakeholder consultation as the central mechanism for building a healthy quality culture" | R3 |

Note on the cap: the anonymity breach (R4) is also an absolute publication bar in the Journal-Fit, methodology, domain and perspective seats' judgement, and is ranked outside the top three only because it does not drive a dimension verdict.

### Required Item Details

These are the roadmap's `must_fix` items, numbered `R1..R14` in the order of the Required Revisions table in Part 2.

**R1 — Establish reference-set verifiability.** Every cited source must resolve to a real bibliographic record, or leave the manuscript together with the claims it supports.
- **Acceptance criteria**: every one of the 12 references resolves to a verifiable bibliographic record under a registered publisher DOI, or the unverifiable source is removed together with every claim that depends on it.

**R2 — Restore the excluded accounts and re-derive the theme structure.** The exclusion criterion (non-fit with the finding) is what makes this fatal rather than reparable by disclosure.
- **Acceptance criteria**: the dissenting accounts are analysed within the reported corpus and the theme structure is re-derived over the full corpus, or the study is reported with the exclusion stated as a bounded limitation and every completeness claim withdrawn (§4.3 full range, §4.1 pervasiveness, §4.2 "every interview").

**R3 — Resolve the Delacroix reversal and rebuild §5's third implication.**
- **Acceptance criteria**: §5's third implication no longer cites Delacroix (2018) as recommending consultation, and is either rebuilt on sources that support it or reframed as an explicit disagreement with Delacroix.

**R4 — Remove identifying attributions and correct the ethics statement.**
- **Acceptance criteria**: no attribution combines a singular office title with an institutional descriptor, and §3.5 describes the de-identification actually performed.

**R5 — Fix the interview N and re-verify every count.**
- **Acceptance criteria**: one interview N governs throughout, and every count in the Abstract, Methods, Findings and survey subgroups is re-verified against it.

**R6 — Rescope all sector-wide and forward-looking claims.** Covers SC-6 and the DA's M6.
- **Acceptance criteria**: no claim in §5 or §6 extends beyond the three studied institutions in the one studied system, and §6's claim that meaning-making processes "are more likely to foster internalized commitment" is withdrawn or supported by outcome evidence.

**R7 — Report the survey instrument in full, or remove the survey.**
- **Acceptance criteria**: item wording, response-scale range and anchors, reliability and validity evidence, sampling frame, invitation base and response rate are reported and all 48 respondents are accounted for by institution, or every survey-derived statement including the Abstract's M=3.9 is removed.

**R8 — Withdraw or reconstruct the inferential subgroup claim.**
- **Acceptance criteria**: the §4.4 subgroup contrast is presented descriptively without a p-value, or is reported with named test, group means and dispersion, degrees of freedom, effect size and explicit treatment of institutional clustering; the institutional-type moderator nomination is withdrawn unless so supported.

**R9 — Report the thematic analysis to a reconstructable standard.**
- **Acceptance criteria**: §3.4 names the analytic tradition, the criterion for thematic stability, the coder or team process, at least one trustworthiness check and a reflexivity/positionality statement, sufficient for a reader to reconstruct how the three themes were reached.

**R10 — Reconcile the design description and strike the §4.1 warrant.**
- **Acceptance criteria**: the interview instrument is described consistently across §3.1, §3.3, §3.4 and §4.1, and the sentence deriving confidence in non-artifactuality from protocol structure is struck or replaced by a reported site-level comparison.

**R11 — Name and characterise the national system.**
- **Acceptance criteria**: the national system is identified and characterised by regulatory model, funding or licensure linkage, review-cycle stage during fieldwork, and documentation language.

**R12 — Define and operationalise "quality culture"; disaggregate the QA referents.**
- **Acceptance criteria**: quality culture is defined operationally including the structural/managerial component alongside the cultural one, is distinguished from external accreditation compliance, external review and internal QA, and the three themes' distinct referents are stated where they diverge.

**R13 — Withdraw the priority claim and argue the actual increment.**
- **Acceptance criteria**: the "first comprehensive account" claim is deleted, and §1, §2 and §6 state what this study adds specifically to Okonkwo (2018), Pettersen (2022), Rahman (2020) and Silva and Tan (2021).

**R14 — Declare and apply a framework; reconstruct §2 to its foundations.** The panel offers two routes (field-canonical vs organizational sociology of professional work); choose one explicitly rather than gesturing at both.
- **Acceptance criteria**: a theoretical or conceptual framework is declared and applied to the three themes, and §2 engages the pre-2018 foundational literature that framework is drawn from.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Transported Severity, Evidence Anchor and Confidence appear on every row, from the driving sub-claim's card entry.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Supply verifiable bibliographic records for all 12 sources or withdraw the unverifiable ones with their dependent claims | SC-1 | Critical | text: References, Ferreira & Lund (2022) / Okonkwo (2018) — "https://doi.org/10.5555/1042004" "https://doi.org/10.5555/1042009" | 5 — DOI prefix registration and named-journal publishers are public record | DOM (W1) | P1 | 2–4 days if records exist; otherwise blocks resubmission |
| R2 | Restore the excluded dissenting accounts and re-derive the theme structure over the full corpus; withdraw all completeness claims that do not survive | SC-3, SC-27 | Critical | text: §4.3 "capturing the full range of administrator views"; "these were excluded for space, as they fell outside the three-theme structure" | 5 — negative-case handling is core reflexive TA practice | METH (W1); EIC W6, DOM W9, PERSP W5; DA C3, M9 | P1 | 3–4 weeks (re-analysis; outcome may change the themes) |
| R3 | Correct the Delacroix (2018) attribution and rebuild or withdraw §5's third implication | SC-2 | Critical | text: §5 ¶4 "who recommends that institutions treat broad stakeholder consultation as the central mechanism for building a healthy quality culture" | 5 — internal to the manuscript, no external verification needed | DOM (W2); EIC W2, METH W12, PERSP W4; DA C1 | P1 | 2 days (plus dependency on R1/R14 for replacement sources) |
| R4 | Replace identifying role-plus-institution attributions with generic role labels; correct §3.5 to describe the de-identification actually performed | SC-4 | Major (DA band: Critical) | text: §3.5 and §4.1 "no individual could be identified" vs "the quality director of the largest private university in the region" | 5 — sample composition in §3.2 makes the descriptors uniquely identifying | EIC (W7); METH W8, DOM W10, PERSP W9; DA C4 | P1 | 1 day |
| R5 | Establish the governing interview N and re-verify every count in the manuscript | SC-5 | Major (arbitrated; PERSP rated Minor) | text: Abstract "Fourteen administrators were interviewed in depth" vs §3.2 "Twelve senior administrators (n=12)" | 5 — direct arithmetic inconsistency on the page | METH (W4); EIC W3, DOM W8, PERSP W10; DA M1 | P1 | 1 day (after R2 resolves whether the gap is the excluded group) |
| R6 | Rescope §5 and §6 to three institutions in one system; withdraw §6's forward-looking causal claim | SC-6, SC-23 | Major | text: §5 "administrators everywhere face the same fundamental tension between external requirement and internal meaning" | 5 — scope-of-inference judgement against the stated sampling frame | METH (W11); EIC W8, DOM W7, PERSP W1; DA C2, M6 | P1 | 3 days |
| R7 | Report the survey instrument, administration and respondent allocation in full, or remove every survey-derived claim including the Abstract's mean | SC-9, SC-11 | Major | absence: §3.3 and §4.4 — expected item wording, response-scale range and anchors, reliability or validity evidence, sampling frame and response rate; checked §3.1–§3.5, §4.4, Abstract, References | 5 — instrument reporting is a minimum survey-methods standard | METH (W2); EIC W9, DOM W6, PERSP W8/W11; DA M4 | P1 | 1 week if the instrument exists; 1 day to remove |
| R8 | Withdraw the p<.05 subgroup claim or report it to standard, and withdraw the institutional-type moderator nomination unless supported | SC-10 | Major | text: §4.4 "we found a statistically significant difference (p<.05) in perceived quality culture, with the teaching-focused institution scoring higher" | 5 — elementary inferential reporting requirements | METH (W3); EIC W9, DOM (body flag, `[SEVERITY-SOURCE: letter-fallback]`), PERSP W8; DA M3 | P1 | 2 days |
| R9 | Report the thematic analysis procedure, reflexivity/positionality and at least one trustworthiness check | SC-13 | Major | absence: §3.4 — expected named analytic approach, reflexivity or positionality statement, stated stability criterion, coder or team process, and a trustworthiness check; checked §3.1–§3.5, §4.1–§4.3, Abstract | 5 — reflexive TA reporting standards | METH (W6) | P1 | 1 week |
| R10 | Reconcile the design description across §3.1/§3.3/§3.4/§4.1 and strike the protocol-based confidence warrant | SC-14a, SC-14b | Major (METH, warrant) / Minor (EIC, DOM, PERSP, terminology) | text: §3.1 and §4.1 "semi-structured interviews"; "These themes emerged systematically from the structured protocol, giving us confidence that the pattern was not an artifact" | 5 — internal inconsistency between declared design and findings warrant | METH (W7); EIC W10, DOM W11, PERSP W12; DA M7 | P1 | 1 day |
| R11 | Identify and characterise the national QA system and its conditions | SC-16 | Major | absence: §3.2 and §6 — expected identification of the national QA system with regulatory, funding and documentation-language conditions; checked Abstract, §1, §2, §3.2, §5, §6, References | 5 — standard expectation for comparative QA scholarship | EIC (W4); PERSP W2 | P1 | 2 days |
| R12 | Define and operationalise quality culture including its structural component; disaggregate the three themes' QA referents | SC-17, SC-18 | Major | absence: §1 and §3.4 — expected an operational definition distinguishing quality culture from external accreditation compliance, external review and internal QA, with instrument items and scale range; checked Abstract, §1, §2, §3.3, §3.4, §4.4, §5 | 5 — conceptual distinctions are foundational in this subfield | EIC (W5); DOM W4/W6, PERSP W8 | P1 | 1–2 weeks |
| R13 | Delete the priority claim and argue the contribution increment against the four closest cited works | SC-7, SC-8 | Major (arbitrated; METH rated the sentence Minor) | text: §6 "This paper has offered the first comprehensive account of how university administrators experience and enact QA implementation" | 5 — direct comparison against the works the paper itself cites | EIC (W1); DOM W3, METH W13; DA M5 | P1 | 1 week |
| R14 | Declare and apply a theoretical framework and reconstruct §2 to include its foundational literature; state which of the two routes was chosen | SC-19, SC-20 | Major | absence: §2 and reference list — expected the field's foundational quality-culture and audit-culture sources predating 2018, including institutional decoupling, audit society and quality-culture typologies; checked all 12 references, §1, §2, §5, §6 | 5 (DOM W3) / 4 (DOM W5) / 5 (PERSP W7) | DOM (W3, W5); PERSP W7 | P1 | 3–4 weeks |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | Name gatekeeper recruitment as a selection pressure and report the sampling logic, approach and decline numbers | SC-15 | Major | text: §3.2 "were recruited through institutional QA offices" | 5 — routine appraisal of gatekeeper-mediated access | METH (W9); PERSP (body); DA M8 | P2 | 3 days |
| S2 | Make the practical implications operational and quantify the documentation burden the paper diagnoses | SC-21 | Major | text: §5 and §6 "processes that maximize genuine participation should be favored"; "create room for meaning-making rather than merely demanding documentation" | 5 — the reviewer is the audience these recommendations address | PERSP (W3) | P2 | 1 week |
| S3 | Acknowledge that the prescriptions rest on administrator self-report alone, or confine them to administrative experience | SC-22 | Major | absence: §3.2 and §4 — expected accounts from academics or students on whom QA acts, given the institution-wide prescriptions in §6; checked §3.2–§3.3, §4.1–§4.4, §5, §6 | 5 — the population claimed about must appear in the evidence base | PERSP (W6) | P2 | 2 days |
| S4 | Supply reproducibility materials: interview protocol, codebook, survey instrument, data-availability statement | SC-24 | Minor | absence: Methods and back matter — expected interview protocol, coding frame or codebook, and a data-availability or materials statement; checked §3.1–§3.5, §4, §6, References | 5 — direct check of the manuscript's surfaces | METH (W10) | P2 | 2 days |
| S5 | Relabel §4.4's divergence as divergence, aligning it with §5's own framing, and treat it as a finding | SC-12 | Major | text: §4.4 "The survey corroborated the qualitative picture"; "the interview accounts had led us to anticipate a more skeptical picture" | 5 — direction of evidence contradicted within one paragraph | METH (W5); DA M2 | P2 | 1 day |
| S6 | Present the survey results in a table rather than running prose | SC-26 | Major (EIC band; presentational) | absence: §4.4 — expected a table reporting group means, standard deviations, test performed, degrees of freedom and effect size; checked §3.3, §3.4, §4.4 and the whole manuscript for any figure or table callout | 4 — familiar with QA survey reporting norms, not a statistician | EIC (W9) | P3 | 1 day (dependent on R7/R8) |
| S7 | Remove the editorial annotation from the Delacroix reference entry or move it into the body | SC-25 | Minor | text: References "Delacroix argues against relying on stakeholder consultation as evidence of quality culture" | 5 — venue reference conventions | EIC (W11) | P3 | <1 hour |
| S8 | Copyedit and rebalance: section proportions (§4.4 carries the whole quantitative contribution in one paragraph), terms undefined on first use | — (`source_kind: editorial`, aggregated from the D5 warn) | — (below finding threshold) | — | — | EIC (D5) | P3 | 2 days |

### Revision Checklist

#### Priority 1 — Structural (estimated total: 10–12 weeks, R2/R12/R14 partly parallelisable)
- [ ] R1: Verify or withdraw all 12 references
- [ ] R2: Restore excluded accounts; re-derive themes; withdraw unsupported completeness claims
- [ ] R3: Correct Delacroix; rebuild or withdraw §5's third implication
- [ ] R4: De-identify attributions; correct §3.5
- [ ] R5: Fix the interview N; re-verify all counts
- [ ] R6: Rescope §5/§6; withdraw the outcome claim
- [ ] R7: Report the survey instrument fully, or remove the survey
- [ ] R8: Withdraw or reconstruct the subgroup inference
- [ ] R9: Report the analysis procedure, reflexivity and a trustworthiness check
- [ ] R10: Reconcile the design description; strike the §4.1 warrant
- [ ] R11: Name and characterise the national system
- [ ] R12: Define and operationalise quality culture; disaggregate referents
- [ ] R13: Delete the priority claim; argue the increment
- [ ] R14: Declare a framework; reconstruct §2 to its foundations

#### Priority 2 — Content supplementation (estimated total: 2–3 weeks)
- [ ] S1: Name gatekeeper selection; report sampling logic
- [ ] S2: Operationalise implications; quantify the burden
- [ ] S3: Confine prescriptions to the evidence base
- [ ] S4: Supply reproducibility materials
- [ ] S5: Relabel §4.4 divergence honestly

#### Priority 3 — Text and presentation (estimated total: 3 days)
- [ ] S6: Survey results in a table
- [ ] S7: Remove the reference annotation
- [ ] S8: Copyedit and rebalance sections

### Deadline

No revision deadline applies: the decision is Reject, and this journal does not hold rejected manuscripts open for return. The roadmap above is a resubmission roadmap for a new submission here or elsewhere. Estimated total effort to a defensible submission: **12–16 weeks**, gated on R1 — if verifiable records cannot be produced for the cited sources, no subsequent item is worth attempting.

The domain seat named the one condition that would overturn its own fatal judgement: resolvable DOIs and verifiable bibliographic records for all twelve sources, supplied by the authors. That is stated for your guidance about a future submission; it does not alter this decision.

Two constructive notes, since a reject still owes you a direction. Four of five reviewers independently identified §4.3 — administrators holding the compliance/meaning tension open and locating professional identity in the gap — as a genuine, publishable insight that exceeds Rahman's (2020) account of vocation. A study rebuilt around that observation, honestly scoped to three institutions in a named system, theorised through either the field's decoupling/audit-culture canon or the organizational sociology of professional work, and with the survey either fully reported or removed, is a viable paper. On venue: if the survey cannot be strengthened, the panel's material supports reframing as an exploratory qualitative study of intermediary work, which suits *Journal of Higher Education Policy and Management* or *Tertiary Education and Management* better than this journal's comparative readership.

### Response Letter

For any future submission arising from this roadmap, respond to every R and S item individually using `templates/revision_response_template.md`. Items R2, R3, R5, R7 and R10 each require you to state which of two conflicting sentences in the current manuscript you are withdrawing.

### Machine-form Roadmap (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "reject",
  "items": [
    {"id": "R1", "priority": "must_fix", "verification_criteria": "Every one of the 12 references resolves to a verifiable bibliographic record under a registered publisher DOI, or the unverifiable source is removed together with every claim that depends on it.", "reviewer": "domain", "severity": "critical", "evidence_anchor": "text: References, Ferreira & Lund (2022) and Okonkwo (2018) entries \"https://doi.org/10.5555/1042004\" \"https://doi.org/10.5555/1042009\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-1"]},
    {"id": "R2", "priority": "must_fix", "verification_criteria": "The dissenting accounts are analysed within the reported corpus and the theme structure is re-derived over the full corpus, or the study is reported with the exclusion stated as a bounded limitation and every completeness claim withdrawn (§4.3 full range, §4.1 pervasiveness, §4.2 \"every interview\").", "reviewer": "methodology", "severity": "critical", "evidence_anchor": "text: §4.3 \"balanced representation of perspectives, capturing the full range of administrator views\"; \"these were excluded for space, as they fell outside the three-theme structure\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-3", "SC-27"]},
    {"id": "R3", "priority": "must_fix", "verification_criteria": "§5's third implication no longer cites Delacroix (2018) as recommending consultation, and is either rebuilt on sources that support it or reframed as an explicit disagreement with Delacroix.", "reviewer": "domain", "severity": "critical", "evidence_anchor": "text: §5 ¶4 \"who recommends that institutions treat broad stakeholder consultation as the central mechanism for building a healthy quality culture\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-2"]},
    {"id": "R4", "priority": "must_fix", "verification_criteria": "No attribution combines a singular office title with an institutional descriptor, and §3.5 describes the de-identification actually performed.", "reviewer": "eic", "severity": "major", "evidence_anchor": "text: §3.5 and §4.1 \"no individual could be identified in reported findings\"; \"the quality director of the largest private university in the region\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-4"]},
    {"id": "R5", "priority": "must_fix", "verification_criteria": "One interview N governs throughout, and every count in the Abstract, Methods, Findings and survey subgroups is re-verified against it.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "text: Abstract and §3.2 \"Fourteen administrators were interviewed in depth\"; \"Twelve senior administrators (n=12)\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-5"]},
    {"id": "R6", "priority": "must_fix", "verification_criteria": "No claim in §5 or §6 extends beyond the three studied institutions in the one studied system, and §6's claim that meaning-making processes are more likely to foster internalized commitment is withdrawn or supported by outcome evidence.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "text: §5 \"administrators everywhere face the same fundamental tension between external requirement and internal meaning\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-6", "SC-23"]},
    {"id": "R7", "priority": "must_fix", "verification_criteria": "Item wording, response-scale range and anchors, reliability and validity evidence, sampling frame, invitation base and response rate are reported and all 48 respondents are accounted for by institution, or every survey-derived statement including the Abstract's M=3.9 is removed.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "absence: §3.3 and §4.4 survey reporting — expected item wording, response-scale range and anchors, reliability or validity evidence, sampling frame, and response rate; checked §3.1–§3.5, §4.4, the Abstract, and the reference list", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-9", "SC-11"]},
    {"id": "R8", "priority": "must_fix", "verification_criteria": "The §4.4 subgroup contrast is presented descriptively without a p-value, or is reported with named test, group means and dispersion, degrees of freedom, effect size and explicit treatment of institutional clustering; the institutional-type moderator nomination is withdrawn unless so supported.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "text: §4.4 \"we found a statistically significant difference (p<.05) in perceived quality culture, with the teaching-focused institution scoring higher\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-10"]},
    {"id": "R9", "priority": "must_fix", "verification_criteria": "§3.4 names the analytic tradition, the criterion for thematic stability, the coder or team process, at least one trustworthiness check and a reflexivity/positionality statement, sufficient for a reader to reconstruct how the three themes were reached.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "absence: §3.4 analysis reporting — expected a named analytic approach, reflexivity or positionality statement, stated criterion for thematic stability, coder or team process, and at least one trustworthiness check; checked §3.1–§3.5, §4.1–§4.3, and the Abstract", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-13"]},
    {"id": "R10", "priority": "must_fix", "verification_criteria": "The interview instrument is described consistently across §3.1, §3.3, §3.4 and §4.1, and the sentence deriving confidence in non-artifactuality from protocol structure is struck or replaced by a reported site-level comparison.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "text: §3.1 and §4.1 \"semi-structured interviews\"; \"These themes emerged systematically from the structured protocol, giving us confidence that the pattern was not an artifact\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-14a", "SC-14b"]},
    {"id": "R11", "priority": "must_fix", "verification_criteria": "The national system is identified and characterised by regulatory model, funding or licensure linkage, review-cycle stage during fieldwork, and documentation language.", "reviewer": "eic", "severity": "major", "evidence_anchor": "absence: Methods §3.2 and Introduction — expected identification of the national QA system, its regulatory model, and the review-cycle stage during fieldwork; checked Abstract, §1, §3.2, §3.3, §4, §5", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-16"]},
    {"id": "R12", "priority": "must_fix", "verification_criteria": "Quality culture is defined operationally including the structural/managerial component alongside the cultural one, is distinguished from external accreditation compliance, external review and internal QA, and the three themes' distinct referents are stated where they diverge.", "reviewer": "eic", "severity": "major", "evidence_anchor": "absence: §1 Introduction and §3.4 Analysis — expected an operational definition of quality culture distinguishing it from external accreditation compliance, external review, and internal quality assurance, together with the survey instrument items and scale range; checked Abstract, §1, §2, §3.3, §3.4, §4.4, §5", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-17", "SC-18"]},
    {"id": "R13", "priority": "must_fix", "verification_criteria": "The \"first comprehensive account\" claim is deleted, and §1, §2 and §6 state what this study adds specifically to Okonkwo (2018), Pettersen (2022), Rahman (2020) and Silva and Tan (2021).", "reviewer": "eic", "severity": "major", "evidence_anchor": "text: §6 \"This paper has offered the first comprehensive account of how university administrators experience and enact QA implementation.\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-7", "SC-8"]},
    {"id": "R14", "priority": "must_fix", "verification_criteria": "A theoretical or conceptual framework is declared and applied to the three themes, and §2 engages the pre-2018 foundational literature that framework is drawn from.", "reviewer": "domain", "severity": "major", "evidence_anchor": "absence: §2 and reference list — expected the field's foundational quality-culture and audit-culture sources predating 2018, including institutional decoupling, audit society, and quality-culture typologies; checked all 12 references, §1 framing, §2 three strands, §5 Discussion, §6 Conclusion", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-19", "SC-20"]},
    {"id": "S1", "priority": "should_fix", "verification_criteria": "Gatekeeper recruitment is named as a selection pressure and its consequences discussed, with the number approached, the number declining, and the sampling or information-power logic reported.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "text: §3.2 \"were recruited through institutional QA offices\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-15"]},
    {"id": "S2", "priority": "should_fix", "verification_criteria": "Each practical implication states what a quality office would stop doing, at what cost in staff time, what a regulator would have to relax, and how a panel would distinguish a meaningful process from a well-documented one; the documentation burden is quantified.", "reviewer": "perspective", "severity": "major", "evidence_anchor": "text: §5 and §6 \"processes that maximize genuine participation should be favored\"; \"create room for meaning-making rather than merely demanding documentation\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-21"]},
    {"id": "S3", "priority": "should_fix", "verification_criteria": "Either the design acknowledges that all prescriptions rest on administrator self-report alone, or the claims are confined to administrative experience.", "reviewer": "perspective", "severity": "major", "evidence_anchor": "absence: §3.2 and §4 — expected accounts from academics or students on whom QA acts, given the institution-wide prescriptions issued in §6; checked §3.2, §3.3, §4.1–§4.4, §5, §6", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-22"]},
    {"id": "S4", "priority": "should_fix", "verification_criteria": "Interview protocol, coding frame or codebook, survey instrument, and a data-availability or materials statement are supplied.", "reviewer": "methodology", "severity": "minor", "evidence_anchor": "absence: Methods and back matter — expected interview protocol, coding frame or codebook, and a data-availability or materials statement; checked §3.1–§3.5, §4, §6, the reference list, and any supplementary-materials note", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-24"]},
    {"id": "S5", "priority": "should_fix", "verification_criteria": "§4.4 describes the survey result as diverging from the interview-based expectation and explains the divergence, consistent with §5's own framing; no sentence describes it as corroboration.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "text: §4.4 \"The survey corroborated the qualitative picture\"; \"This is notable because the interview accounts had led us to anticipate a more skeptical picture\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-12"]},
    {"id": "S6", "priority": "nice_to_fix", "verification_criteria": "Survey results appear in a table with group means, standard deviations and, if retained, the test performed, degrees of freedom and effect size.", "reviewer": "eic", "severity": "major", "evidence_anchor": "absence: §4.4 Survey findings — expected a table reporting group means, standard deviations, the test performed, degrees of freedom, and an effect size, plus reconciliation of the subgroup counts with the 48 respondents; checked §3.3, §3.4, §4.4, and the whole manuscript for any figure or table callout", "confidence": 4, "source_kind": "finding", "sub_claim_ids": ["SC-26"]},
    {"id": "S7", "priority": "nice_to_fix", "verification_criteria": "The Delacroix reference entry carries no editorial annotation; any needed characterisation of the source appears in the body.", "reviewer": "eic", "severity": "minor", "evidence_anchor": "text: References \"Delacroix argues against relying on stakeholder consultation as evidence of quality culture\"", "confidence": 5, "source_kind": "finding", "sub_claim_ids": ["SC-25"]},
    {"id": "S8", "priority": "nice_to_fix", "verification_criteria": "Section proportions are rebalanced so no single paragraph carries an entire strand of the contribution, and every term is defined on first use.", "reviewer": "eic", "source_kind": "editorial", "sub_claim_ids": []}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

Sprint-contract cards score dimensions rather than issuing an overall recommendation, so assessed dimensions replace the recommendation field.

### Journal-Fit Reviewer (`eic`) — owner of D5, D6
- Assessed: D5 `warn`, D6 `block` (repairable). D1–D4 correctly `not_assessed` (ineligible).
- Confidence: 4–5 across 11 weaknesses; 3 strengths.
- Key point: the manuscript belongs at this venue on topic and method, but its three themes map one-to-one onto Okonkwo (2018), Pettersen (2022) and Rahman (2020), and the increment is never argued — so the "first comprehensive account" claim is contradicted by the paper's own bibliography.

### Peer Reviewer 1 (`methodology`) — owner of D1, eligible on D3
- Assessed: D1 `block` (**fatal**), D3 `block` (repairable). Others `not_assessed`.
- Confidence: 4–5 across 13 weaknesses; 3 strengths.
- Key point: the described procedure could not have produced the reported results, because §4.3 removes disconfirming cases *because* they disconfirm and then claims full-range coverage; the evidence would have to be regenerated, not documented.

### Peer Reviewer 2 (`domain`) — owner of D2
- Assessed: D2 `block` (**fatal**). Others `not_assessed`.
- Confidence: 4–5 across 11 weaknesses; 3 strengths.
- Key point: all 12 DOIs sit in the reserved `10.5555` test range and contradict the named journals' registered publisher prefixes, so no claim about prior work can be verified — and the one internally checkable citation (Delacroix) is reversed in §5.

### Peer Reviewer 3 (`perspective`) — owner of D4
- Assessed: D4 `block` (no `block_class`; fatal scope invalid on a high-priority dimension). Others `not_assessed`. `[Scoring-plan dissent: none emitted — see card-integrity note 1]`
- Confidence: 4–5 across 12 weaknesses; 3 strengths (no per-finding confidence on strengths).
- Key point: an unnamed system plus an undescribed instrument plus sector-wide claims leaves an adjacent-field reader unable to judge transfer at all, and the paper's silences — academics, students, dissenting administrators, the regulator — reproduce a managerial account while presenting itself as a critique of one.

### Devil's Advocate (`da`) — owner of D3
- Assessed: D3 `block` (repairable). Others `not_assessed`.
- 4 CRITICAL (all VALIDATED), 9 MAJOR; confidence 4–5.
- Key point: the shortest hostile route needs no external knowledge — the reversed Delacroix warrant, the sector-wide quantifiers, and the exclusion-plus-completeness pair are all visible on the page, and the reversed version is the one doing the argumentative work.

---

**Deliverable complete.** Per the Phase 2 boundary, no revision of the manuscript, no reviewer-card edits, and no new review comments were produced; the caller must re-invoke the appropriate revision-side phase separately, and must supply the missing `#540` provenance stamp before this letter is released.
