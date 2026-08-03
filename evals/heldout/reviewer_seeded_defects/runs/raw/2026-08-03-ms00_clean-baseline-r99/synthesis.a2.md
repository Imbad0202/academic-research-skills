# Editorial Decision Package

**Manuscript:** *Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students*
**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · panel_size 5
**Emission note:** this package supersedes `synthesis.a1.md`, which the integrity checker rejected for emitting zero fired-condition lines. All four mechanical audit lines appear exactly once below, in § Sprint Contract Audit.

---

## Sprint Contract Audit (mechanical)

### Step 1 — Role-scoped scoring matrix

Ineligible `not_assessed` values and eligible abstentions are excluded from both numerator and denominator. No dimension is unassessed; no seat was dropped; the panel is intact at 5.

| Dim | Priority | Eligible roles | Assessed eligible seats | Seat scores | Worst assessed | Fatal declared? |
|-----|----------|----------------|-------------------------|-------------|----------------|-----------------|
| D1 | mandatory | methodology | methodology | block (`block_class: repairable`) | block | No |
| D2 | mandatory | domain | domain | warn | warn | No |
| D3 | mandatory | da, methodology | da, methodology | warn, warn | warn | No |
| D4 | high | perspective | perspective | block (no class declared; body states "repairable condition in principle") | block | No |
| D5 | normal | eic | eic | warn | warn | No |
| D6 | mandatory | eic | eic | block (`block_class: repairable`) | block | No |

Audit verdict (worst assessed eligible score across all dimensions): **block**, not `block(fatal)`. No seat declared a fatal block anywhere. This is the single determination that separates F1 from F2, so it is stated explicitly: perspective's D4 block omits `block_class`, and **absence of a fatal declaration is not a fatal declaration** — its review body characterises the condition as repairable in principle. Perspective's "this defect alone, uncorrected, makes acceptance impossible" is a block statement, and its "moves this manuscript out of the revision category" is expressly conditional on a verification outcome not yet obtained. Neither mints fatality on the record as given.

dimension_verdicts: [D1=block, D2=warn, D3=warn, D4=block, D5=warn, D6=block]

### Step 2 — Failure-condition evaluation

| ID | Sev | Cross-reviewer quantifier | Expression | Stage 1 (per-dimension) | Stage 2 (dimension quantifier) | Fired | Action |
|----|-----|---------------------------|------------|--------------------------|-------------------------------|-------|--------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 false, D2 false, D3 false, D6 false — no seat declared fatality | `any` over {D1,D2,D3,D6} → false | **false** | reject |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1 true (methodology=block), D6 true (eic=block); D2 false, D3 false | `any` → true | **true** | major_revision |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 true (n=1, owner methodology=block), D2 true (n=1, owner domain=warn), D3 true (n=2, both seats=warn), D6 true (n=1, owner eic=block) | `two or more` → 4 ≥ 2 → true | **true** | major_revision |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 true (perspective=block) | `any` over {D4} → true | **true** | major_revision |
| F5 | 40 | any | any dimension scores 'warn' or worse | all six true | `any` → true | **true** | minor_revision |
| F0 | 10 | all | every dimension scores 'pass' | no dimension all-pass | `all` → false | **false** | accept |

fired_conditions: [F2, F3, F4, F5]

### Step 3 — Precedence and decision

Among fired conditions the highest `severity` is F2 (90); F3 (70), F4 (60) and F5 (40) are subordinate. No tie-break required.

The Devil's Advocate card's `#### CRITICAL` table contains column headers and **no data rows**; all seven DA findings (M1–M7) are filed under `#### MAJOR`. There are therefore no DA CRITICAL identifiers to adjudicate, and no phantom identifier is minted. (Findings tagged `Severity: Critical` on the EIC, methodology and perspective cards are *not* DA CRITICAL items and are handled through the ordinary consensus and roadmap machinery.)

da_critical_adjudications: []

editorial_decision=major_revision

The `[DA-CRITICAL-VS-ACCEPT]` marker does not apply: the mechanical decision is not `accept`.

### Panel and card-hygiene notes (flagged, not repaired)

- The **perspective card opens with a malformed artefact**: a `## Scoring Plan Dissent` heading with an omitted-placeholder line, followed by an inline self-correction ("Wait — that placeholder is not permitted. Removing it."). No dissent content was recorded, and the card is otherwise complete — `contract_role` present, all six dimensions scored, weaknesses and strengths tagged. I treat the card as usable and score it as written. Per the Phase Boundary I flag this rather than rewrite it; the Phase 1 owner should clean the card header on any re-round.
- **No scoring-plan dissent was declared by any seat.** No fatality was minted during dissent because no dissent exists.
- **Domain seat's self-declared borderline (recorded, not re-scored):** the domain card states that its warn trigger's preamble covers defects that "do not carry a headline conclusion," while the over-generalisation it found *does* touch the abstract — and it resolves the borderline to warn on the reasoning that the defect is unsubstantiation of a claim that is likely true rather than inaccuracy. That score is transported as given. The same card also states that if reference verification fails, D2 moves to block. See the re-round condition in the letter.

---

## Synthesis Working Record — Step 1b sub-claim inventory

Consensus is computed **per `sub_claim_id`** over the **4 non-DA seats** (EIC, R1 = methodology, R2 = domain, R3 = perspective). The denominator is always 4, never "the seats that spoke." `not-mentioned` is silence, never agreement and never opposition. DA positions are recorded for visibility and are excluded from the count.

Severity and confidence are **transported** from the cards' per-finding tags, never re-derived. Every current-format card carries both, so no `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` tag is required anywhere in this inventory.

### Inventory (non-silent positions only)

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | severity | confidence |
|---|---|---|---|---|---|---|
| SC-1 | comparability claim unbenchmarked | EIC | raised | W1 — `text: §2, final ¶ "…an incremental data point, comparable with prior work…"` | Critical | 5 |
| SC-1 | " | R2 | corroborated | W1 — `absence: §2 and §5 — expected a reported comparator effect size…` | Major | 5 |
| SC-1 | " | R3 | corroborated | W2 — `text: Abstract and §5 "consistent with prior technology-acceptance research"` | Major | 4 |
| SC-1 | " | DA | corroborated (non-counting) | M2 — `absence: §2 and §5 — expected numeric effect sizes…` | Major | 4 |
| SC-2 | reference list unverifiable | R3 | raised | W1 — `text: References, all six entries — "…10.5555/2050001" … "…10.5555/2050006"` | Critical | 4 |
| SC-2 | " | R2 | corroborated | W4 — `text: References "https://doi.org/10.5555/2050001" … "…/2050006"` | Major | 3 |
| SC-3 | instrument adaptation undocumented | R1 | raised | W1 — `text: §3.2 "six-item scale adapted from Costa and Wren (2019)" … "α = .88"` | Critical | 5 |
| SC-3 | " | R3 | corroborated | W3 — `absence: §3.2 Measures — expected verbatim wording of the six items…` | Major | 5 |
| SC-3 | " | R2 | corroborated | W6 — `text: Abstract "an adapted, previously validated instrument"` | Minor | 4 |
| SC-3 | " | DA | corroborated (non-counting) | M7 — `text: Abstract "adapted, previously validated"` | Major | 4 |
| SC-4 | abstract claims validity by inheritance | R2 | raised | W6 — `text: Abstract "adapted, previously validated instrument"` | Minor | 4 |
| SC-4 | " | DA | corroborated (non-counting) | M7 | Major | 4 |
| SC-5 | ordinal outcome, parametric estimator made primary | R1 | raised | W2 — `text: §3.2 and §3.4 "…single five-point frequency item…" / "…Spearman…as a robustness check"` | Major | 5 |
| SC-6 | common-method variance unassessed | R1 | raised | W3 — `absence: §3.2 and §5 — expected any assessment of common-method variance…` | Major | 5 |
| SC-6 | " | DA | corroborated (non-counting) | M3 — `absence: §3.4 and §6` | Major | 4 |
| SC-7 | single construct cannot separate PU from platform favourability | R2 | raised | W7 — `absence: §3.2 and §6 — expected acknowledgement…` | Minor | 3 |
| SC-8 | no denominator, no response rate | R1 | raised | W4 — `text: §3.1 "All enrolled undergraduates were eligible" / "…spanned all four year levels"` | Major | 5 |
| SC-8 | " | DA | corroborated (non-counting) | M5 — `text: §1 "among undergraduates at one university…"` | Major | 4 |
| SC-9 | setting descriptors withheld | R3 | raised | W4 — `absence: §3.1 — expected country/region, LMS platform, year, disciplinary composition` | Minor | 5 |
| SC-10 | anonymity vs deduplication contradiction | R3 | raised | W5 — `text: §3.1 with §3.3 "5 duplicate entries were removed" / "could not be linked back…"` | Major | 5 |
| SC-10 | " | R1 | corroborated | W5 — `text: §3.1 and §3.3 "5 duplicate entries were removed" / "No identifying information was collected"` | Major | 4 |
| SC-10 | " | EIC | **disputed** | S3 — `text: §3.1 "A total of 233 responses were received…"`; asserts "Nothing in the recruitment or consent chain requires the editor to ask a follow-up question" | (strength, no severity) | 5 |
| SC-10 | " | DA | corroborated (non-counting) | M6 | Major | 4 |
| SC-11 | distributional reporting too thin to verify assumption checks | R1 | raised | W6 — `text: §3.4 "Scatterplot inspection showed an approximately linear, monotonic association…"` | Major | 5 |
| SC-11 | " | EIC | **disputed** (severity) | W3 — `absence: §3.4 and §4 — expected a scatterplot figure or descriptive table…`; states "Assessment is not obstructed" | Minor | 5 |
| SC-12 | abstract widens construct and population | R1 | raised | W10 — `text: Abstract "perceived usefulness tracks with LMS engagement among undergraduates"` | Minor | 5 |
| SC-12 | " | DA | corroborated (non-counting) | M1 — same anchor | Major | 5 |
| SC-13 | abstract drops CI and robustness check | EIC | raised | W4 — `text: Abstract "…(r = .42, p < .001)"` | Minor | 4 |
| SC-14 | onboarding implication licensed only by an unidentifiable direction | R1 | raised | W11 — `text: §5 "…LMS onboarding which helps students see concrete usefulness"` | Minor | 4 |
| SC-14 | " | DA | corroborated (non-counting) | Review body, "two lesser points" | (below Major band) | — |
| SC-15 | r² characterised verbally, never stated | R1 | raised | W7 — `text: §4 "The proportion of variance shared by the two measures was accordingly modest"` | Minor | 5 |
| SC-15 | " | DA | corroborated (non-counting) | Review body, "two lesser points" | (below Major band) | — |
| SC-16 | sensitivity computed on realised n, framed as design property | R1 | raised | W8 — `text: §3.4 "…greater than .80 power to detect a correlation of r >= .19"` | Minor | 4 |
| SC-16 | " | R2 | corroborated | Review body cross-seat note: "my calculation returns approximately .80, not comfortably above it" | (cross-seat note) | — |
| SC-17 | foundational literature absent; construct attributed to secondary sources | R2 | raised | W3 — `text: §1 ¶1 "a substantial body of work suggests" / §2 ¶1 "the degree to which a person believes…"` | Major | 5 |
| SC-17 | " | R3 | corroborated | W2 — framework never named, home discipline never identified | Major | 4 |
| SC-17 | " | EIC | corroborated | W6 — `text: §2, opening sentence "Research on technology acceptance has long proposed…"` | Minor | 3 |
| SC-18 | estimand mismatch (PU→intention vs PU→use) | R2 | raised | W2 — `text: §1 ¶2 "nor do we test a full acceptance model" / §5 ¶1 "consistent with prior…"` | Major | 5 |
| SC-19 | voluntariness moderator named then unengaged | R2 | raised | W5 — `text: §4 ¶2 "including course requirements and assessment schedules"` | Minor | 4 |
| SC-20 | no data/code/preregistration availability | R3 | raised | W7 — `absence: back matter following §7 — expected data-, code-, preregistration statements` | Major | 5 |
| SC-20 | " | R1 | **disputed** (severity) | W9 — `absence: end matter and Methods §3.4 — expected an availability statement…`; "a reproducibility gap rather than an error" | Minor | 5 |
| SC-21 | recruitment possibly conditioned on the DV (range restriction) | DA | raised (non-counting) | M4 — `text: §3.1 "…distributed through the institution's course-announcement channel…"` | Major | 3 |
| SC-22 | hedging duplicated across five sections | EIC | raised | W5 — `text: §6 "Third, the cross-sectional design precludes any causal or temporal inference."` | Minor | 4 |
| SC-23 | contribution positioned as full-article increment rather than benchmarked replication | EIC | raised | W2 — `text: §1 "It asks a deliberately narrow question…"` | Major | 4 |
| SC-23 | " | R2 | corroborated | Review body: "the field does not need another single-site PU–use correlation reported as a novel association. It can use one reported as a benchmarked replication." | Major | 5 |
| SC-24 | barrier to LMS log data never named | R3 | raised | W6 — `absence: §6 — expected the named barrier…` | Minor | 4 |
| SC-25 | incomplete-case exclusion uncharacterised | R1 | raised | W5 (same parent as SC-10) — `text: §3.1 "14 incomplete submissions…were removed"` | Major | 4 |

**Decomposition discipline check:** every sub-claim above is an atomic component of a claim a listed reviewer actually made. No sub-claim was authored by this synthesis. Two parent weaknesses were split across sub-claims (R1's W5 → SC-10 + SC-25; R3's W2 → SC-1 + SC-17); per the transport rule both children of R1 W5 inherit that parent's Major, and both children of R3 W2 inherit its Major.

### Disposition (precedence: `conflict ≥ 1` → SPLIT first; otherwise by `agree` count over 4)

| sub_claim_id | agree | conflict | silent | Disposition |
|---|---|---|---|---|
| SC-1 | 3 (EIC, R2, R3) | 0 | R1 | **[CONSENSUS-3]** — silent seat: R1 (methodology) |
| SC-2 | 2 (R3, R2) | 0 | EIC, R1 | Corroborated finding |
| SC-3 | 3 (R1, R3, R2) | 0 | EIC | **[CONSENSUS-3]** — silent seat: EIC (explicit deferral) |
| SC-4 | 1 (R2) | 0 | EIC, R1, R3 | Single-reviewer finding |
| SC-5 | 1 (R1) | 0 | EIC, R2, R3 | Single-reviewer finding (owner seat, conf 5) |
| SC-6 | 1 (R1) | 0 | EIC, R2, R3 | Single-reviewer finding (owner seat, conf 5) |
| SC-7 | 1 (R2) | 0 | EIC, R1, R3 | Single-reviewer finding (conf 3, standard weight) |
| SC-8 | 1 (R1) | 0 | EIC, R2, R3 | Single-reviewer finding (owner seat, conf 5) |
| SC-9 | 1 (R3) | 0 | EIC, R1, R2 | Single-reviewer finding |
| SC-10 | 2 (R3, R1) | 1 (EIC) | R2 | **[SPLIT]** — arbitrated below |
| SC-11 | 1 (R1) | 1 (EIC) | R2, R3 | **[SPLIT]** — arbitrated below |
| SC-12 | 1 (R1) | 0 | EIC, R2, R3 | Single-reviewer finding |
| SC-13 | 1 (EIC) | 0 | R1, R2, R3 | Single-reviewer finding |
| SC-14 | 1 (R1) | 0 | EIC, R2, R3 | Single-reviewer finding |
| SC-15 | 1 (R1) | 0 | EIC, R2, R3 | Single-reviewer finding |
| SC-16 | 2 (R1, R2) | 0 | EIC, R3 | Corroborated finding |
| SC-17 | 3 (R2, R3, EIC) | 0 | R1 | **[CONSENSUS-3]** — silent seat: R1 |
| SC-18 | 1 (R2) | 0 | EIC, R1, R3 | Single-reviewer finding (owner seat, conf 5) |
| SC-19 | 1 (R2) | 0 | EIC, R1, R3 | Single-reviewer finding |
| SC-20 | 1 (R3) | 1 (R1) | EIC, R2 | **[SPLIT]** — arbitrated below |
| SC-21 | 0 non-DA | 0 | all 4 | DA-only finding (outside consensus count) |
| SC-22 | 1 (EIC) | 0 | R1, R2, R3 | Single-reviewer finding |
| SC-23 | 2 (EIC, R2) | 0 | R1, R3 | Corroborated finding |
| SC-24 | 1 (R3) | 0 | EIC, R1, R2 | Single-reviewer finding |
| SC-25 | 1 (R1) | 0 | EIC, R2, R3 | Single-reviewer finding |

No sub-claim reached CONSENSUS-4. That is a real feature of this panel, not a defect: the seats were configured with deliberately non-overlapping remits, so most findings are owner-seat findings. Under the confidence-weighting rule, several single-reviewer findings at Score 5 from the seat that owns the relevant dimension carry more weight than the raw 1/4 count suggests, and they are prioritised accordingly.

### Step 1c — Surface-form parity check

Three sub-claims were re-examined before their weight was set, because their phrasing differed markedly in register from the surrounding cards:

- **SC-7** (domain, confidence 3) is phrased loosely — "part of r = .42 *may* reflect a general positive orientation." The opposite-style counterfactual: if this were written as a formal discriminant-validity argument with a named nested-model test, would it gain weight? It should not, and it does not. Its weight here comes from its transported confidence of 3 and the seat's own statement that magnitude "is unknowable from the reported data," not from register. It is placed at P2 on that basis.
- **SC-21** (DA, confidence 3) is stated with unusually precise mechanism vocabulary ("sampled conditional on the very behaviour that forms the dependent variable," "range-restricted subpopulation"). The counterfactual runs the other way: does that precision credit the claim? It must not. The claim is explicitly conditional on an unstated fact about the recruitment channel, no non-DA seat corroborated it, and the DA itself rates confidence 3. Technical specificity is not corroboration. It is placed at P2 with an escalation trigger, not at P1.
- **SC-16** (methodology, confidence 4) rests partly on a domain cross-seat aside written informally ("my calculation returns approximately .80, not comfortably above it"). That informality does not reduce its weight; the substance is a checkable arithmetic claim about a reported quantity, and it is recorded as corroboration.

No sub-claim was found unevaluable on ambiguity grounds. Authorship was not used as a weighting input anywhere in this synthesis.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript to this journal. It has been assessed by a five-seat panel: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary/reproducibility), and a Devil's Advocate.

### Decision: Major Revision

This decision is the mechanical output of the review contract's failure conditions applied to the panel's dimension scores. Two mandatory dimensions (methodology rigour, venue fit and contribution) and one high-priority dimension (cross-disciplinary relevance) were scored `block`; the remaining three were scored `warn`. No seat declared any block unrepairable, which is why the decision is a revision rather than a rejection. Every block on the record is repairable without new data collection.

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-ABSENT: no dispatching-layer provenance stamp was supplied with this synthesis input. This block is required in reviewer_full mode and may not be inferred, so it is emitted unfilled rather than populated with an assumed statement. The dispatching layer should supply the stamp — cross-model slot active, single-family disclosure, or dispatch-failure fallback — and this block should be completed before the letter is sent to the author. No cross-family aggregate or "same-model majority" figure has been computed; per-seat scores are visible by inspection in the audit matrix above.]`

*(Blind cross-model decision check, Step 4b: `ARS_CROSS_MODEL` is not indicated in this invocation and no consent gate has been passed. No cross-model comparison was run; no behavioural change.)*

### Consensus Analysis

#### Points of Agreement (Consensus)

- **[CONSENSUS-3]** *(SC-1; silent seat: methodology)* — The manuscript's stated contribution is comparability with prior work, and that comparability is never demonstrated. No prior effect size appears anywhere in the paper. The Journal-Fit Reviewer, the domain reviewer and the cross-disciplinary reviewer independently reached this, and the Devil's Advocate adds the sharpest form of it: given the manuscript's own premises that effect sizes vary "across samples and instruments" (§2) and that association strengths "varied by institution" (Song), almost any positive coefficient would have been declared consistent. The consistency claim as constructed is close to unfalsifiable. This is the finding that carries the venue-fit block, and it is an obligation the manuscript incurred itself — having cited Song for the proposition that a single-site estimate is "one point in a distribution," the paper owes its reader the distribution.
- **[CONSENSUS-3]** *(SC-3; silent seat: Journal-Fit Reviewer, by explicit deferral)* — The perceived-usefulness scale is described only as "adapted" from a prior instrument. No item is reproduced, the adaptation is never specified, and no dimensionality evidence exists for this sample. Cronbach's α = .88 establishes inter-item homogeneity and nothing about construct validity or structure; an adapted scale is a new scale until shown otherwise. Since the entire contribution is one coefficient, the content of the measure on one side of that coefficient is the contribution's foundation.
- **[CONSENSUS-3]** *(SC-17; silent seat: methodology)* — The literature base is six references, none canonical, none post-2021. The construct's definition is a near-paraphrase of the technology-acceptance tradition's founding formulation but is credited to two secondary sources; the tradition is never named, its home discipline is never identified, its extension frameworks are absent, and every existing synthesis of PU–use effects in education is absent. The introduction's "substantial body of work" rests on a single citation.

#### Corroborated findings below the consensus bar (2/4, no conflict)

- **SC-2 — reference-list verifiability (potentially dispositive; see re-round condition).** Two seats independently observed that all six references carry DOIs under the `10.5555` prefix with sequential suffixes 2050001–2050006, and that several journal titles are near-variants of established titles rather than matches. Both seats report this as a **verification requirement, not a finding of fabrication** — neither performed live DOI resolution, and both note that a de-identification or production step could in principle explain the pattern. The editorial office must establish whether each cited work exists and supports the assertion attached to it before the revision is re-reviewed.
- **SC-16** — the sensitivity statement's arithmetic and its framing.
- **SC-23** — the contribution should be repositioned as a benchmarked replication rather than a novel single-site association.

#### Single-reviewer findings carried at full weight (confidence-weighted)

Several of the most consequential findings were raised by one seat only, because the panel's remits were configured not to overlap. Under the confidence-weighting rule, a Score-5 finding from the seat that owns the dimension carries full weight regardless of how many other seats spoke to it. These include SC-5 (ordinal outcome with a parametric estimator made primary), SC-6 (common-method variance never assessed), SC-8 (no population denominator, therefore no response rate), and SC-18 (estimand mismatch between PU→use and the PU→intention paths of the tradition invoked). Each is at P1 in the roadmap on that basis, not on a headcount.

#### Points of Disagreement

**1. SC-10 — Is the anonymity/deduplication contradiction a live problem?** *(2 raised, 1 disputed, 1 silent)*

- **R3 (cross-disciplinary) and R1 (methodology) argue** the two statements cannot both hold as written: §3.1 reports removing five duplicate entries, §3.3 asserts that no identifying information was collected and responses could not be linked to individuals. Duplicate detection requires a persistent marker (IP address, session token, device fingerprint, platform response ID) or a heuristic rule; each is a quasi-identifier, and retaining one is defensible, but a blanket anonymity statement that omits it is not.
- **The Journal-Fit Reviewer's S3 disputes this implicitly**, certifying that "nothing in the recruitment or consent chain requires the editor to ask a follow-up question" and praising the ethics reporting as internally consistent.
- **Editor's Resolution: the finding stands; the Journal-Fit Reviewer's strength is narrowed rather than withdrawn.** Arbitration is on evidence and expertise. On evidence, the tension is textual and direct — two sentences in the submitted manuscript that cannot both be complete as written. On expertise, protocol coherence and ethics-reporting scrutiny were the cross-disciplinary seat's assigned remit, and the methodology seat corroborates from routine survey-operations reasoning; the Journal-Fit Reviewer's S3 addresses the *consent chain* — approval body, voluntariness, absence of incentive, landing-page consent — which remains sound and is not contradicted. The disputed element is *data-handling disclosure*, which the Journal-Fit Reviewer did not examine and did not list among its self-identified blind spots. Both readings survive on their own subject matter. **Roadmap item R8, Priority 1.** A direct answer is required, not a softening clause.

**2. SC-11 — Is the absence of distributional reporting a presentation defect or a rigour defect?** *(1 raised at Major, 1 disputed at Minor)*

- **R1 (methodology) argues Major**: §3.4 asserts approximate linearity, monotonicity, absence of extreme bivariate outliers and approximate symmetry of both distributions. For a five-category ordinal outcome, "approximately symmetric" is a claim about a frequency table that is never shown. These are precisely the checks that decide whether a product-moment coefficient is the right summary, so the assertion carries the argumentative weight while the evidence for it is withheld.
- **The Journal-Fit Reviewer argues Minor**: the paper carries roughly six quantities in total, all reported in text with adequate precision, so assessment is not obstructed; this is a presentation defect, and it is expressly why D5 was scored warn rather than block.
- **Editor's Resolution: upheld at Major.** Expertise-first: assumption verification for correlational reporting sits in D1, whose sole eligible seat is methodology, and the Journal-Fit Reviewer explicitly states it is relying on the methodology seat for measurement detail. Both seats are correct about different objects — as a matter of *editorial presentation* the paper is readable without a table, and as a matter of *estimator justification* the frequency distribution is load-bearing. The higher severity governs because the second object is the one that decides whether r = .42 is the right summary at all. **Roadmap item R5, Priority 1.** This resolution does not disturb the D5 warn score, which was scored on presentation grounds and is transported unchanged.

**3. SC-20 — Is the missing availability package Major or Minor?** *(1 raised at Major, 1 disputed at Minor)*

- **R3 (cross-disciplinary) argues Major**: the contribution is framed as a transparently reported association, yet nothing in the manuscript permits independent recomputation — no dataset, no correlation matrix, no script, no preregistration, no availability statement of any kind. The claim that the reporting is transparent is therefore itself unsubstantiated.
- **R1 (methodology) argues Minor**: "a reproducibility gap rather than an error."
- **Editor's Resolution: upheld at Major, on the disputing seat's own reasoning.** R1's card states that for an anonymous survey with two variables and n = 214 "the barrier to sharing is close to zero, and sharing would resolve part of W1 and all of W6 at a stroke" — that is, the availability package discharges part of two other Priority 1 items at near-zero cost. Expertise also favours R3, whose configured remit is open-science infrastructure and who serves on a data-availability screening panel. The item is placed at P1 not because it is the gravest defect but because it is the cheapest resolution of several graver ones. **Roadmap item R11, Priority 1.**

**4. The tension the panel design predicted did not materialise — and that is worth stating.** The reviewer configuration anticipated a genuine dispute between the domain reviewer ("the increment is not worth publishing without more") and the Journal-Fit Reviewer ("publishable as a short report if properly positioned"), and flagged it as the paper's real decision point. It did not occur. Both seats converged on the same remedy: benchmark the estimate against the pooled distribution and reposition the contribution as replication-with-known-limits, after which the paper clears its bar. The domain seat states explicitly that "the paper's stated ambition is defensible at the lower ceiling if the benchmarking is actually done." There is nothing to arbitrate here, and the author should read the absence of dispute as a clear signal: the required work is benchmarking, not new data.

#### Devil's Advocate findings

The Devil's Advocate recorded no CRITICAL findings; all seven of its findings sit at Major and are folded into the roadmap alongside the seats that corroborate them (M1→S2, M2→R2, M3→R9, M5→R7, M6→R8, M7→R4/S2). M4 (SC-21) is DA-only and is addressed at S10 with an escalation trigger. The DA's D3 warn is the panel's assessment that the *central* correlational claim survives adversarial pressure — the failures are in the layer of claims built on top of it, not in the coefficient itself.

### Decision Rationale

The panel's judgement is unusually coherent for a manuscript with three blocked dimensions, and the coherence points at one thing. Every seat, without exception, credited the paper's inferential discipline: causal language is refused from abstract to conclusion, the reverse pathway is named affirmatively rather than buried, the use item is treated as an indicator of perceived rather than actual engagement, and the limitations name the four threats that actually bear on this design without mitigation rhetoric. That restraint is genuine and should be protected in revision. No reviewer asked for stronger claims.

What every seat also found is that the restraint was allowed to stand in for work it does not do. Declining to say what your number *causes* is not the same as telling the reader what your number is *worth*. The manuscript nominates itself as an incremental data point comparable with prior work, and then supplies no comparator — no effect size from any cited study, no pooled estimate, no statement of whether .42 sits inside or outside the field's range. Since comparability is the sole claimed contribution, the contribution cannot be evaluated by anyone. That carries the venue-fit block. Independently, the measurement foundation of the single reported coefficient cannot be reconstructed: the predictor's items are not reproduced and its adaptation is not described, the outcome is a coarse single ordinal item whose distribution is never shown, no population denominator exists so the conceded volunteer skew cannot be bounded, and the deduplication account contradicts the anonymity statement. That carries the methodology block. And the bridge into the borrowed tradition — the reference list — is not currently checkable, which is what took cross-disciplinary relevance to block.

Rejection would be the wrong call, and no seat asked for it. Every block on the record was declared or described as repairable, and none of the required work needs new data collection: it needs literature retrieval, disclosure of material the authors plainly hold, one reordering of estimators, and a repositioning of the contribution claim. The manuscript is a clean draft that needs substance, not a rough draft that needs cleaning. Whether the substance can be supplied depends first on the reference-verification outcome, and that determination belongs to the editorial office before re-review begins.

### Re-round condition (recorded, not applied)

Two seats condition their scores on an outcome not yet obtained. The domain seat states that if reference verification fails, its D2 score moves from warn to block under its fabricated-evidence trigger; the cross-disciplinary seat states that such a finding "supersedes everything else" and "moves this manuscript out of the revision category altogether." **This synthesis has not applied either contingency**, because the arithmetic runs on the scores as submitted and the verification has not been performed. If the editorial office establishes that the cited works do not exist, that is new evidence requiring a fresh scoring round on a re-scored panel — not a re-derivation by this synthesis, and not a discretionary downgrade of the present decision.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | All six references carry the reserved `10.5555` example DOI prefix with sequential suffixes and near-variant journal titles; the manuscript's entire bridge into the tradition it claims to increment is currently uncheckable. Reported as a verification requirement, not a finding of fabrication. | R3 (raised, Critical, conf 4); R2 (corroborated, Major, conf 3) | `text: References, all six entries — "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"` | R1 |
| 2 | The paper's sole claimed contribution — comparability with prior work — is asserted four times and never demonstrated; no prior effect size appears anywhere, and the paper's own premises about cross-instrument and cross-site variability make the consistency claim near-unfalsifiable as framed. | EIC (raised, Critical, conf 5); R2 (Major, conf 5); R3 (Major, conf 4); DA M2 | `text: §2 Literature Review, final paragraph "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model."` | R2 |
| 3 | The measurement foundation of the single reported coefficient cannot be reconstructed: the six PU items are not reproduced, the adaptation is unspecified, no dimensionality evidence exists in this sample, and α = .88 licenses none of it. | R1 (raised, Critical, conf 5); R3 (Major, conf 5); R2 (Minor, conf 4); DA M7 | `text: §3.2 — "six-item scale adapted from Costa and Wren (2019)" and "the scale showed good internal consistency (Cronbach's α = .88)"` | R4 |

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b identifiers each item traces to. `Severity` and `Confidence` are transported from the cards' per-finding tags and were not re-derived; where seats tagged the same sub-claim at different severities, all transported values are shown with attribution and the arbitrated priority is stated in the letter above. No fallback tags were required.

### Required Revisions (Must Fix)

> **Ordinal contract:** the `### Required Item Details` blocks below are numbered `R1..R12` in exactly this table's order; the *n*th Required row here is the *n*th must-fix item.

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Establish that all six cited works exist and support the assertions attached to them; supply resolvable DOIs or replace the citations. | SC-2 | Critical (R3) / Major (R2) | `text: References, all six entries — "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"` | 4 (R3, DOI-prefix screening, no live resolution) / 3 (R2, unresolvable from manuscript) | R3, R2 | P1 | 1–3 days (+ editorial verification gate) |
| R2 | Benchmark r = .42 against reported comparator effect sizes and the pooled PU–use distribution; state explicitly whether it falls near, above or below; assess instrument commensurability; if commensurability fails, change the "comparable" framing materially. | SC-1 | Critical (EIC) / Major (R2, R3) | `text: §2 Literature Review, final paragraph "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model."` | 5 (EIC) / 5 (R2, meta-analysis co-author) / 4 (R3) | EIC, R2, R3, DA M2 | P1 | 5–10 days |
| R3 | State which estimand the comparison targets (PU→intention vs PU→use vs log-validated use) and adjust the comparator set accordingly. | SC-18 | Major | `text: §1 ¶2 "nor do we test a full acceptance model" and §5 ¶1 "consistent with prior technology-acceptance research"` | 5 | R2 | P1 | 1–2 days |
| R4 | Reproduce the six PU item stems and the frequency item verbatim; state exactly what the adaptation changed relative to the source instrument; report a dimensionality check in this sample. | SC-3 | Critical (R1) / Major (R3) / Minor (R2) | `text: §3.2 — "six-item scale adapted from Costa and Wren (2019)" and "the scale showed good internal consistency (Cronbach's α = .88)"` | 5 (R1) / 5 (R3) / 4 (R2) | R1, R3, R2, DA M7 | P1 | 2–4 days |
| R5 | Report the full frequency distribution of the use item and a descriptives table, and show the scatterplot or cross-tabulation that supports the linearity, monotonicity and symmetry claims. | SC-11 | Major (R1) — arbitrated over Minor (EIC) | `text: §3.4 — "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers" and "and both distributions were approximately symmetric"` | 5 (R1) / 5 (EIC) | R1, EIC | P1 | 2–3 days |
| R6 | Make the rank-based (or polychoric) estimate primary in line with the ordinal measurement model declared in §3.2, or justify parametric primacy explicitly; state the attenuation argument that licenses the word "moderately." | SC-5 | Major | `text: §3.2 and §3.4 — "captured with a single five-point frequency item asking how often the respondent accessed the LMS" and "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check"` | 5 | R1 | P1 | 2–3 days |
| R7 | Report the undergraduate enrolment denominator and the response rate; describe sample composition beyond "spanned all four year levels." | SC-8 | Major | `text: §3.1 — "All enrolled undergraduates were eligible" and "The analyzed sample of 214 students spanned all four year levels"` | 5 | R1, DA M5 | P1 | 1–2 days |
| R8 | Repair the data-handling disclosure: state the deduplication rule and what persistent marker (if any) was retained, reconcile it with §3.3, and characterise the 14 incomplete-case exclusions. | SC-10, SC-25 | Major | `text: §3.1 with §3.3 — "5 duplicate entries were removed" and "responses could not be linked back to individual students"` | 5 (R3) / 4 (R1) | R3, R1, DA M6 | P1 | 2–4 days (may require confirming the approved protocol) |
| R9 | Add explicit treatment of common-method variance as a threat to the *magnitude* of r, not only to causal direction, in Methods, Discussion and Limitations. | SC-6 | Major | `absence: Methods §3.2 and Discussion §5 — expected any assessment of common-method variance arising from same-instrument, same-respondent, same-sitting measurement of both variables; checked §3.2 Measures, §3.3 Procedure and ethics, §3.4 Analysis, §5 Discussion, §6 Limitations` | 5 | R1, DA M3 | P1 | 3–5 days |
| R10 | Rework §2: name the tradition and its home discipline, anchor the perceived-usefulness construct in its originating literature, engage the extension frameworks and post-2021 syntheses. | SC-17 | Major (R2, R3) / Minor (EIC) | `text: §1 ¶1 "a substantial body of work suggests" and §2 ¶1 "the degree to which a person believes a technology will help them perform better"` | 5 (R2) / 4 (R3) / 3 (EIC, defers to domain seat) | R2, R3, EIC | P1 | 7–10 days |
| R11 | Add a data-, code- and materials-availability statement: de-identified item-level dataset or correlation matrix with n, the analysis script, and preregistration status or its explicit absence. | SC-20 | Major (R3) — arbitrated over Minor (R1) | `absence: back matter following §7 — expected data-availability, code-availability, and preregistration statements; checked Abstract, §3.3, §3.4, §6, §7, and References` | 5 (R3) / 5 (R1) | R3, R1 | P1 | 1–2 days |
| R12 | Reposition the contribution as a benchmarked replication and/or re-categorise the submission as a brief report or short paper; drop the full-article framing if the benchmarking cannot be completed. | SC-23 | Major | `text: §1 Introduction "It asks a deliberately narrow question: among undergraduates at one university, is perceived usefulness of the LMS associated with self-reported frequency of use?"` | 4 (EIC) / 5 (R2) | EIC, R2 | P1 | 2–3 days |

### Required Item Details

**R1 — Reference verifiability**
- **Acceptance criteria**: Every reference resolves to a registered publisher DOI, the journal title matches an identifiable venue, and the editorial office confirms that each cited work supports the assertion attached to it; any citation that fails is replaced or removed and the dependent text revised.

**R2 — Benchmark the estimate**
- **Acceptance criteria**: At least one pooled or comparator effect size for education-sector PU–use associations is reported with its source, instrument commensurability with a six-item adapted PU scale and a single-item frequency measure is assessed explicitly, and the manuscript states in text whether r = .42 falls near, above or below that range.

**R3 — Specify the estimand**
- **Acceptance criteria**: The manuscript states which path of the acceptance tradition its coefficient corresponds to and restricts every comparability claim to comparators estimating that same path.

**R4 — Document the instrument**
- **Acceptance criteria**: All six PU item stems and the frequency item appear verbatim in the manuscript or a cited appendix, the adaptation from the source instrument is described item by item, and a dimensionality check on this sample is reported alongside α.

**R5 — Distributional reporting and assumption evidence**
- **Acceptance criteria**: A descriptives table and the full five-category frequency distribution of the use item are reported, and the linearity, monotonicity, outlier and symmetry claims in §3.4 are each supported by a shown exhibit rather than by assertion.

**R6 — Estimator ordering**
- **Acceptance criteria**: The reported primary coefficient is consistent with the ordinal measurement model declared in §3.2, or the parametric primacy is defended in text, and the magnitude descriptor "moderately" is accompanied by a stated attenuation argument.

**R7 — Denominator and response rate**
- **Acceptance criteria**: The eligible undergraduate enrolment figure and the resulting response rate are reported, and sample composition is described in enough detail to compare against the institutional profile.

**R8 — Data-handling disclosure**
- **Acceptance criteria**: §3.1 and §3.3 are mutually consistent as written, the deduplication procedure and any retained quasi-identifier are stated, and the 14 excluded incomplete cases are compared to retained cases on their completed PU items or complete-case analysis is defended.

**R9 — Common-method variance**
- **Acceptance criteria**: The manuscript identifies same-instrument, same-respondent, same-sitting measurement as a threat to the magnitude of the coefficient distinct from the causal-direction question, and either reports a diagnostic or states the unbounded inflation explicitly in Limitations.

**R10 — Literature base**
- **Acceptance criteria**: §2 names the technology-acceptance tradition and its originating discipline, cites the construct's primary source for its definition, engages the extension frameworks and at least one post-2021 synthesis, and no framework claim rests on a secondary source alone.

**R11 — Availability package**
- **Acceptance criteria**: The manuscript carries data-, code- and materials-availability statements, and a reader can recompute the reported correlation from the deposited material or from a reported correlation matrix with n.

**R12 — Reposition the contribution**
- **Acceptance criteria**: The abstract, §2 and §7 describe the study as a benchmarked replication with a stated comparator, or the submission is re-categorised to the brief-report track with the full-article framing removed.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | State r² numerically (≈ .18) rather than describing shared variance as "accordingly modest." | SC-15 | Minor | `text: §4 — "The proportion of variance shared by the two measures was accordingly modest"` | 5 | R1, DA | P2 | 0.5 day |
| S2 | Correct the abstract's closing sentence: "engagement" is a behavioural construct the paper disclaims in §2, and unqualified "undergraduates" drops the single-site and volunteer boundaries §6 honours. | SC-12 | Minor (R1) / Major (DA M1) | `text: Abstract — "perceived usefulness tracks with LMS engagement among undergraduates"` | 5 (R1) / 5 (DA) | R1, DA M1 | P2 | 0.5 day |
| S3 | Restore the confidence interval and the Spearman robustness check to the abstract; [.30, .52] is precisely what a reader scanning for comparable estimates needs. | SC-13 | Minor | `text: Abstract "Perceived usefulness was positively and moderately associated with self-reported LMS use (r = .42, p < .001)."` | 4 | EIC | P2 | 0.5 day |
| S4 | Reframe the onboarding implication as explicitly conditional on a direction the design cannot identify, or as a hypothesis for a design that could. | SC-14 | Minor | `text: §5 — "offers modest support for the intuition that LMS onboarding which helps students see concrete usefulness"` | 4 | R1, DA | P2 | 0.5 day |
| S5 | State whether the sensitivity calculation was a priori or computed post hoc on the realised post-exclusion n, and whether the Pearson-primary ordering was fixed in advance; note that the domain seat's recalculation returns ≈ .80 rather than comfortably above it. | SC-16 | Minor | `text: §3.4 — "the study had greater than .80 power to detect a correlation of r >= .19" and "so the design was sensitive to small-to-moderate associations"` | 4 (R1) / — (R2 cross-seat note) | R1, R2 | P2 | 1 day |
| S6 | Name the barrier that prevented use of institutional LMS log data — ethics scope, data-governance policy, technical access, cost, or a decision not to ask. | SC-24 | Minor | `absence: §6 Limitations — expected the named barrier that prevented access to institutional LMS log data, such as ethics scope, data-governance policy, technical access, or cost; checked §2, §3.3, §3.4, §5, and §6` | 4 | R3 | P2 | 0.5 day |
| S7 | Add setting descriptors: country or region, LMS platform, data-collection year, disciplinary composition of respondents. | SC-9 | Minor | `absence: §3.1 Design and participants — expected country or region, LMS platform, data-collection year, and disciplinary composition of respondents; checked Abstract, §3.1, §3.3, §5, and §6` | 5 | R3 | P2 | 1 day |
| S8 | State that the estimate comes from a context where LMS use is partly compelled by course requirements, and cite what the field knows about voluntariness as a moderator of PU–use associations. | SC-19 | Minor | `text: §4 ¶2 "including course requirements and assessment schedules"` | 4 | R2 | P2 | 1–2 days |
| S9 | Add a caveat that a single-construct self-report cannot separate perceived usefulness from generalised platform favourability; discriminant validity is untested here. | SC-7 | Minor | `absence: §3.2 Measures and §6 Limitations — expected acknowledgement that a single-construct self-report cannot separate perceived usefulness from generalised platform favourability; checked §2, §3.2, §4, §5, §6` | 3 | R2 | P2 | 0.5 day |
| S10 | State whether the course-announcement channel sits inside the LMS or is reached through it. **Escalation trigger:** if it does, the low end of the use scale is structurally under-sampled and the range-restriction consequence must be worked through in Limitations, which would raise this to P1 on re-review. | SC-21 | Major (DA) | `text: §3.1 "The survey was distributed through the institution's course-announcement channel over a three-week window."` | 3 — DA states the finding is conditional on an unstated fact; no non-DA seat corroborated | DA M4 | P2 | 1 day |
| S11 | Consolidate the duplicated non-causality and self-report cautions (currently repeated across the abstract, §2, §5, §6 and §7) into §6, freeing space for the benchmarking work R2 requires without lengthening the manuscript. Consolidate the cautions; do not weaken them. | SC-22 | Minor | `text: §6 Limitations "Third, the cross-sectional design precludes any causal or temporal inference."` | 4 | EIC | P3 | 1 day |

*No separate aggregated editorial channel is emitted: none of the five cards supplied a Minor Issues list below the finding threshold, so every roadmap item above carries transported per-finding metadata and none is `source_kind: "editorial"`.*

### Roadmap — machine form (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "decision": "major_revision",
  "items": [
    {"id": "R1", "priority": "P1", "verification_criteria": "Every reference resolves to a registered publisher DOI, each journal title matches an identifiable venue, and the editorial office confirms each cited work supports its attached assertion; failures replaced and dependent text revised.", "reviewer": ["perspective", "domain"], "severity": "critical", "evidence_anchor": "text: References, all six entries — \"https://doi.org/10.5555/2050001\" and \"https://doi.org/10.5555/2050006\"", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-2"]},
    {"id": "R2", "priority": "P1", "verification_criteria": "At least one pooled or comparator PU-use effect size reported with source, instrument commensurability assessed, and r = .42 located as near/above/below that range in text.", "reviewer": ["eic", "domain", "perspective", "da"], "severity": "critical", "evidence_anchor": "text: §2 Literature Review, final paragraph \"It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model.\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-1"]},
    {"id": "R3", "priority": "P1", "verification_criteria": "Manuscript states which acceptance-tradition path its coefficient estimates and restricts comparability claims to comparators estimating the same path.", "reviewer": ["domain"], "severity": "major", "evidence_anchor": "text: §1 ¶2 \"nor do we test a full acceptance model\" and §5 ¶1 \"consistent with prior technology-acceptance research\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-18"]},
    {"id": "R4", "priority": "P1", "verification_criteria": "All six PU item stems and the frequency item appear verbatim, the adaptation is described item by item, and a dimensionality check on this sample is reported alongside alpha.", "reviewer": ["methodology", "perspective", "domain", "da"], "severity": "critical", "evidence_anchor": "text: §3.2 — \"six-item scale adapted from Costa and Wren (2019)\" and \"the scale showed good internal consistency (Cronbach's α = .88)\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-3"]},
    {"id": "R5", "priority": "P1", "verification_criteria": "Descriptives table and full five-category frequency distribution reported; linearity, monotonicity, outlier and symmetry claims each supported by a shown exhibit.", "reviewer": ["methodology", "eic"], "severity": "major", "evidence_anchor": "text: §3.4 — \"Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers\" and \"and both distributions were approximately symmetric\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-11"], "arbitration": "split_upheld_at_major"},
    {"id": "R6", "priority": "P1", "verification_criteria": "Primary coefficient consistent with the declared ordinal measurement model or parametric primacy defended in text; \"moderately\" accompanied by a stated attenuation argument.", "reviewer": ["methodology"], "severity": "major", "evidence_anchor": "text: §3.2 and §3.4 — \"captured with a single five-point frequency item asking how often the respondent accessed the LMS\" and \"Because the use item is ordinal, we also computed a Spearman correlation as a robustness check\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-5"]},
    {"id": "R7", "priority": "P1", "verification_criteria": "Eligible enrolment figure and response rate reported; sample composition described sufficiently to compare against the institutional profile.", "reviewer": ["methodology", "da"], "severity": "major", "evidence_anchor": "text: §3.1 — \"All enrolled undergraduates were eligible\" and \"The analyzed sample of 214 students spanned all four year levels\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-8"]},
    {"id": "R8", "priority": "P1", "verification_criteria": "§3.1 and §3.3 mutually consistent; deduplication procedure and any retained quasi-identifier stated; 14 excluded incomplete cases compared to retained cases or complete-case analysis defended.", "reviewer": ["perspective", "methodology", "da"], "severity": "major", "evidence_anchor": "text: §3.1 with §3.3 — \"5 duplicate entries were removed\" and \"responses could not be linked back to individual students\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-10", "SC-25"], "arbitration": "split_upheld"},
    {"id": "R9", "priority": "P1", "verification_criteria": "Same-instrument/same-respondent/same-sitting measurement identified as a magnitude threat distinct from causal direction, with a diagnostic reported or the unbounded inflation stated in Limitations.", "reviewer": ["methodology", "da"], "severity": "major", "evidence_anchor": "absence: Methods §3.2 and Discussion §5 — expected any assessment of common-method variance arising from same-instrument, same-respondent, same-sitting measurement of both variables; checked §3.2 Measures, §3.3 Procedure and ethics, §3.4 Analysis, §5 Discussion, §6 Limitations", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-6"]},
    {"id": "R10", "priority": "P1", "verification_criteria": "§2 names the tradition and its home discipline, cites the construct's primary source, engages extension frameworks and at least one post-2021 synthesis; no framework claim rests on a secondary source alone.", "reviewer": ["domain", "perspective", "eic"], "severity": "major", "evidence_anchor": "text: §1 ¶1 \"a substantial body of work suggests\" and §2 ¶1 \"the degree to which a person believes a technology will help them perform better\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-17"]},
    {"id": "R11", "priority": "P1", "verification_criteria": "Data-, code- and materials-availability statements present; a reader can recompute the reported correlation from deposited material or a reported correlation matrix with n.", "reviewer": ["perspective", "methodology"], "severity": "major", "evidence_anchor": "absence: back matter following §7 — expected data-availability, code-availability, and preregistration statements; checked Abstract, §3.3, §3.4, §6, §7, and References", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-20"], "arbitration": "split_upheld_at_major"},
    {"id": "R12", "priority": "P1", "verification_criteria": "Abstract, §2 and §7 describe the study as a benchmarked replication with a stated comparator, or the submission is re-categorised to the brief-report track with full-article framing removed.", "reviewer": ["eic", "domain"], "severity": "major", "evidence_anchor": "text: §1 Introduction \"It asks a deliberately narrow question: among undergraduates at one university, is perceived usefulness of the LMS associated with self-reported frequency of use?\"", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-23"]},
    {"id": "S1", "priority": "P2", "verification_criteria": "r-squared reported numerically in §4.", "reviewer": ["methodology", "da"], "severity": "minor", "evidence_anchor": "text: §4 — \"The proportion of variance shared by the two measures was accordingly modest\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-15"]},
    {"id": "S2", "priority": "P2", "verification_criteria": "Abstract's closing sentence uses the measured outcome (self-reported use) and the bounded population (volunteer respondents at one institution).", "reviewer": ["methodology", "da"], "severity": "minor", "evidence_anchor": "text: Abstract — \"perceived usefulness tracks with LMS engagement among undergraduates\"", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-12"]},
    {"id": "S3", "priority": "P2", "verification_criteria": "Abstract reports the 95% CI and the Spearman robustness check alongside r and p.", "reviewer": ["eic"], "severity": "minor", "evidence_anchor": "text: Abstract \"Perceived usefulness was positively and moderately associated with self-reported LMS use (r = .42, p < .001).\"", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-13"]},
    {"id": "S4", "priority": "P2", "verification_criteria": "The onboarding implication is stated as conditional on a direction the design cannot identify, or reframed as a hypothesis for a design that could.", "reviewer": ["methodology", "da"], "severity": "minor", "evidence_anchor": "text: §5 — \"offers modest support for the intuition that LMS onboarding which helps students see concrete usefulness\"", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-14"]},
    {"id": "S5", "priority": "P2", "verification_criteria": "Planning status of the sensitivity calculation and of the estimator ordering stated explicitly; the boundary nature of the .80 figure acknowledged.", "reviewer": ["methodology", "domain"], "severity": "minor", "evidence_anchor": "text: §3.4 — \"the study had greater than .80 power to detect a correlation of r >= .19\" and \"so the design was sensitive to small-to-moderate associations\"", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-16"]},
    {"id": "S6", "priority": "P2", "verification_criteria": "The specific barrier to LMS log-data access is named in §6.", "reviewer": ["perspective"], "severity": "minor", "evidence_anchor": "absence: §6 Limitations — expected the named barrier that prevented access to institutional LMS log data, such as ethics scope, data-governance policy, technical access, or cost; checked §2, §3.3, §3.4, §5, and §6", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-24"]},
    {"id": "S7", "priority": "P2", "verification_criteria": "Country or region, LMS platform, data-collection year and disciplinary composition reported in §3.1.", "reviewer": ["perspective"], "severity": "minor", "evidence_anchor": "absence: §3.1 Design and participants — expected country or region, LMS platform, data-collection year, and disciplinary composition of respondents; checked Abstract, §3.1, §3.3, §5, and §6", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-9"]},
    {"id": "S8", "priority": "P2", "verification_criteria": "Partly-compelled use context stated and the voluntariness-moderator literature cited.", "reviewer": ["domain"], "severity": "minor", "evidence_anchor": "text: §4 ¶2 \"including course requirements and assessment schedules\"", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-19"]},
    {"id": "S9", "priority": "P2", "verification_criteria": "Limitations or Measures acknowledges that discriminant validity against generalised platform favourability is untested.", "reviewer": ["domain"], "severity": "minor", "evidence_anchor": "absence: §3.2 Measures and §6 Limitations — expected acknowledgement that a single-construct self-report cannot separate perceived usefulness from generalised platform favourability; checked §2, §3.2, §4, §5, §6", "confidence": 3, "source_kind": "finding", "sub_claims": ["SC-7"]},
    {"id": "S10", "priority": "P2", "verification_criteria": "§3.1 states whether the course-announcement channel sits inside or is reached via the LMS; if it does, range restriction is worked through in Limitations.", "reviewer": ["da"], "severity": "major", "evidence_anchor": "text: §3.1 \"The survey was distributed through the institution's course-announcement channel over a three-week window.\"", "confidence": 3, "source_kind": "finding", "sub_claims": ["SC-21"], "escalation": "raises_to_P1_if_channel_is_inside_lms"},
    {"id": "S11", "priority": "P3", "verification_criteria": "Non-causality and self-report cautions consolidated into §6 without weakening their content; §5 and §7 restatements pruned.", "reviewer": ["eic"], "severity": "minor", "evidence_anchor": "text: §6 Limitations \"Third, the cross-sectional design precludes any causal or temporal inference.\"", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-22"]}
  ]
}
```

### Revision Checklist

#### Priority 1 — Structural revisions (estimated 29–51 person-days; R2, R3 and R10 share one literature-retrieval block, so the realistic combined figure is nearer 25–40)
- [ ] R1: Verify or replace all six references — editorial gate before re-review begins
- [ ] R2: Benchmark r = .42 against reported comparator and pooled estimates
- [ ] R3: Specify the estimand and align the comparator set to it
- [ ] R4: Reproduce the items, document the adaptation, test dimensionality
- [ ] R5: Report the frequency distribution, descriptives table and assumption exhibits
- [ ] R6: Reorder the estimators to match the declared measurement model
- [ ] R7: Report the enrolment denominator and response rate
- [ ] R8: Repair the deduplication/anonymity disclosure and characterise the incomplete-case exclusions
- [ ] R9: Treat common-method variance as a magnitude threat
- [ ] R10: Rework §2 around the tradition's primary and cumulative literature
- [ ] R11: Add the data, code and materials availability package
- [ ] R12: Reposition as a benchmarked replication or re-categorise as a brief report

#### Priority 2 — Content supplementation (estimated 7–9 person-days)
- [ ] S1: State r² numerically
- [ ] S2: Correct the abstract's construct and population widening
- [ ] S3: Restore the CI and robustness check to the abstract
- [ ] S4: Make the onboarding implication explicitly conditional
- [ ] S5: State the planning status of the sensitivity calculation and estimator ordering
- [ ] S6: Name the log-data access barrier
- [ ] S7: Add setting descriptors
- [ ] S8: Address voluntariness as a moderator
- [ ] S9: Add the discriminant-validity caveat
- [ ] S10: State where the recruitment channel sits (escalates if inside the LMS)

#### Priority 3 — Text and structure (estimated 1 person-day)
- [ ] S11: Consolidate the duplicated cautions into §6 without weakening them

### Revision Deadline

**8 weeks** (Major Revision). Re-review will be required. Note that the R1 verification gate should be resolved by the editorial office at the front of that window, since its outcome determines whether the remaining roadmap is the right roadmap.

### Response Letter Template

Please respond to every numbered item (R1–R12, S1–S11) using the format in `templates/revision_response_template.md`, quoting the item ID, the change made, and the manuscript location. Items R1–R12 are must-fix and may not be declined. For S-items you may decline with a stated reason. Two specific requests: **R8 requires a direct factual answer about the deduplication procedure, not an additional hedging clause**, and the panel asks that the manuscript's existing inferential restraint — the refusal of causal language, the explicit naming of the reverse pathway, and the mechanism-specific limitations — be preserved rather than traded away in revision. Every seat identified that restraint as the manuscript's strongest asset, and no seat asked for stronger claims.

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary
- Scored: D5 warn, D6 block (repairable). Highest-confidence finding: Critical, confidence 5.
- Key point: the paper nominates itself as a comparable increment and then never performs the comparison; its modesty is genuine calibration on the inferential axis and a substitute for missing work on the contribution axis, and the revision must not collapse the two.

### Reviewer 1 (Methodology) Summary
- Scored: D1 block (repairable), D3 warn. Eleven weaknesses, one Critical, five Major.
- Key point: direction and magnitude are independent problems and the manuscript addresses only the first — the coefficient's measurement foundation (undocumented instrument, coarse single-item outcome, no denominator, unshown distributions, unassessed common-method variance) cannot be reconstructed as submitted.

### Reviewer 2 (Domain) Summary
- Scored: D2 warn (with a self-declared borderline against block, and an explicit contingency to block if reference verification fails). Seven weaknesses, four Major.
- Key point: nothing here is domain-false and the coefficient is probably squarely consistent with the field's pooled evidence — which is the irony of a paper that never goes to that evidence, cites no canonical source, and never states which path of the tradition its estimate is comparable to.

### Reviewer 3 (Cross-disciplinary / reproducibility) Summary
- Scored: D4 block. Seven weaknesses, one Critical, four Major. Card carries a malformed opening artefact, flagged above and not repaired here.
- Key point: verification first — all six references sit on a reserved example DOI prefix, so the bridge into a borrowed tradition is currently uncheckable; and a manuscript whose entire claimed value is transparency arrives with no instrument, no data, no code, no preregistration and no setting descriptors.

### Devil's Advocate Summary
- Scored: D3 warn. Zero CRITICAL findings; seven MAJOR (M1–M7).
- Key point: the central correlational claim survives adversarial pressure and is not blocked; what fails is the layer built on top of it — an abstract that asserts behavioural engagement the paper disclaims, a consistency claim that the paper's own premises render near-unfalsifiable, and an unstated assumption that two self-reports from one respondent in one sitting are independent measurements.
