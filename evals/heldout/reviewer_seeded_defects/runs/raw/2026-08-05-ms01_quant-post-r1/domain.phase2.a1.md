contract_role: domain

## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: block
trigger: "a substantive misrepresentation of cited prior work, such that a specific stated conclusion cannot stand as written without correction to the underlying facts or citations"
block_class: repairable

### D3: argumentative_coherence

score: not_assessed

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

I read this manuscript as a persistence researcher, and my judgement rests on two things a domain reviewer can check without re-running a single analysis: whether the paper uses the field's central construct as the field defines it, and whether the sources it names say what it says they say. On the first, the paper measures one thing and reports another. On the second, it inverts the argument of one cited source and leaves nine of fifteen reference-list entries unused in the body text. Either problem alone would require substantive correction; together they mean the Literature Review and the Conclusion cannot stand as written.

**On the construct.** "Retention" in this manuscript means "remained enrolled and completed the final assessment" of one introductory statistics course in one term. In the persistence tradition the word denotes continued institutional enrolment across terms, and thirty years of work — Tinto's integration model, Bean's attrition model, and the empirical literature that has contested both — establishes that course completion and institutional persistence have overlapping but distinct determinants. A student can fail to sit a final and re-enrol next term; a student can pass every gateway course and depart for financial or family reasons. The paper never marks this distinction, not in the Abstract, not in §3.3 where the outcome is defined, and not in §5.1 where the limitations are enumerated. It then generalises in §6 to "retention across programs and disciplines" for "higher education institutions worldwide" — a claim about a construct the study did not observe. The coding rule compounds this: treating "enrolled but did not sit the final" as *not retained* places still-enrolled students in the same category as withdrawals, which is a measurement decision that inflates the non-retained group with a population whose persistence outlook is entirely different. I want to be precise about what would repair this. Relabelling the outcome as course completion throughout, and confining the Conclusion to that outcome, is achievable by rewriting. It yields a much narrower paper than the one submitted, but it does not require new data — which is why I score this dimension a repairable block rather than a fatal one.

**On source–claim correspondence.** I checked each of the six in-text attributions against its reference-list entry. Five correspond: Calloway (2019) on reflective prompts versus directive nudges, Osei (2020) on relative-standing discouragement, Rutledge and Berange (2022) on the SRL lens, Vandermeer (2023) on click counts, and Ibarra (2023) on causal language. The sixth is inverted. §2 asserts that "Dashboards have been shown to reliably improve outcomes for lower-achieving students" and attributes this to Ferro and Nakamura (2021), an entry titled *When dashboards demotivate: Peer comparison and the lower-achieving student*. The attributed claim is not a loose paraphrase of that title's argument; it is its negation. This matters beyond bookkeeping because the paper explicitly makes the sentence load-bearing — "This position underpins much of the equity-oriented rationale for institutional dashboard deployment, and we return to it in the Discussion" — and §5 duly returns to it, aligning the study's finding with "the view that externalized progress cues can support persistence." A stated conclusion therefore rests on a source that argues the opposite. That the other five attributions are sound is what persuades me this is a discrete error rather than systematic misattribution; it is also what makes it correctable.

**On coverage.** The reference list contains exactly the literature this paper needed and never cites it. Halloran (2020), *Retention in the gateway course: A review of intervention studies*, addresses the paper's own framing premise. Wexler and Ojo (2020), *Retention modeling with LMS trace data: A cautionary study*, addresses its own method. Solberg and Whitfield (2018) addresses its own institutional recommendation. All three are uncited, as are Ainsworth and Devi, Berange (2021), Delacroix and Ohno, Kessler and Amadou, Montez, and Prakash and Tolliver — nine of fifteen entries, sixty percent of the apparatus. Meanwhile §1's premise that "the first-year gateway course is frequently identified as a point of elevated risk" carries no citation at all, and no early-alert evaluation study or persistence model appears anywhere. The effect is a paper that engages the analytics literature with reasonable competence and the retention literature not at all, while claiming retention in its title.

**On the SRL framing.** The forethought/performance/reflection apparatus is invoked in §1 and §2 and measured nowhere. What is measured is a single-item "Overall, I feel in control of my learning in this course." Perceived academic control is a recognised construct, but it is not a forethought measure, not a monitoring measure, and not a reflection measure; the §5 inference that the result is "consistent with a self-regulated learning account in which dashboards scaffold monitoring and adjustment" draws a conclusion about monitoring from an instrument that indexes none. The framing is also internally unstable about which phase is implicated — §1 nominates the reflective phase, §2 the "forethought and self-monitoring phases," and self-monitoring is a process within the performance phase rather than a phase in its own right. §3.3's justification that "single-item overall ratings are common in dashboard studies to limit survey burden" is offered without citation and does not match the field's practice for regulatory constructs, where validated multi-item instruments are the norm.

**Boundaries and routing.** Three matters I noticed fall outside my dimension and I am not scoring them. The arithmetic in §4 does not cohere — t(156) with an analytic sample of 142 and a perceived-control subsample of 87, t(140) = 1.31 reported at p = .008, Table 2 cells summing to 127 against the sentence "All 142 students… were classified into engagement groups," and a secondary-item sample SD of 0.10 that integer 1–5 responses at a mean of exactly 3.00 cannot produce. That is D1's territory and the methodology seat should adjudicate it; I flag it rather than duplicate it. Likewise, the shift from a correlational design to §5's "dashboard engagement improved course retention… therefore raises the probability" and §6's causal restatement is an inference defect belonging to D3, made more striking by the paper's own citation of Ibarra (2023) on precisely that failure. My one numerical finding below concerns a discrepancy between what the paper reports about itself in two places, which is a domain-accuracy matter rather than a statistical one. I also note for the editor that all fifteen references share the DOI prefix 10.5555 with a mechanically progressing suffix pattern; I cannot verify these entries from the manuscript alone, and if verification fails, my repairable assessment would need revisiting.

### S1: Self-critical and correctly attributed treatment of engagement proxies

§2 represents Vandermeer's (2023) argument accurately against its title, and — unusually — applies it to the present study rather than to competitors, conceding that session counts cannot distinguish careful reading from repeated opening. §5.1 carries the concession forward. This is the paper's most disciplined engagement with a source.
- **Evidence Anchor**: `text: §2 "Several authors have therefore cautioned that click-based engagement metrics should be treated as rough indicators"`

### S2: Competent account of the relative-standing and goal-orientation literature

The demotivation paragraph correctly identifies that the direction of peer-comparison effects is conditional on framing and goal orientation, and names the performance-avoidance mechanism specifically rather than gesturing at "individual differences." This is a current and defensible summary of that strand.
- **Evidence Anchor**: `text: §2 "Performance-avoidance oriented students, in particular, may interpret an unfavorable comparison as a threat to be avoided rather than a problem to be solved"`

### S3: Operational transparency about what the dashboard was and how activity was counted

§3.1 discloses the peer-comparison band, universal availability, and absence of opt-in; §3.3 states the sessionization rule and labels the median split as a coarse simplification adopted for interpretability. A domain reader can therefore see exactly what was measured, which is what makes the construct critique above possible.
- **Evidence Anchor**: `text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"`

### W1: §2 attributes to Ferro and Nakamura (2021) the reverse of that source's argument, and the Discussion builds on the inversion

The manuscript states that dashboards "reliably improve outcomes for lower-achieving students" and cites an entry titled *When dashboards demotivate: Peer comparison and the lower-achieving student*. The sentence is declared load-bearing for the equity rationale and is cashed out in §5's claim that the finding "aligns with the view that externalized progress cues can support persistence." Uncorrected, a stated conclusion is supported by a source that argues the opposite, and the Literature Review affirmatively misinforms readers about a contested strand — compounded by §2's own next paragraph (Osei, 2020) asserting the contrary direction without acknowledging the contradiction.
- **Severity**: Critical
- **Evidence Anchor**: `text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students" and References "When dashboards demotivate: Peer comparison and the lower-achieving student"`
- **Confidence**: 5 — direct comparison of in-text claim against the reference-list title, within my citation-verification remit

### W2: "Retention" names institutional persistence but measures single-course final-assessment completion, and the distinction is never drawn

Title, Abstract, and Conclusion all use the field's persistence vocabulary for an outcome defined as completing one course's final assessment in one term. The two constructs have different determinants and different measurement traditions, and the manuscript nowhere acknowledges that it is substituting one for the other — including in §5.1, where the limitation would belong. The Conclusion then extends to "retention across programs and disciplines," a construct no measure in this study addresses. Uncorrected, the paper's headline contribution claim is about something it did not observe.
- **Severity**: Critical
- **Evidence Anchor**: `text: §6 "improving retention across programs and disciplines" and Abstract "end-of-term course retention in a large undergraduate course"`
- **Confidence**: 5 — construct definition is my primary area of empirical work

### W3: Coding a missed final as "not retained" conflates a single missed assessment with withdrawal

§3.3 places students who withdrew and students who "were enrolled but did not sit the final" in the same non-retained category. Still-enrolled students who miss one assessment are not attrition cases by any definition in the persistence literature, and their inclusion changes what the outcome variable means and how its base rate should be read. The outcome requires redefinition and the association re-estimated on the corrected variable.
- **Severity**: Major
- **Evidence Anchor**: `text: §3.3 "Students who withdrew before the final assessment, or who were enrolled but did not sit the final, were coded as not retained"`
- **Confidence**: 5 — standard outcome-coding practice in attrition studies

### W4: Nine of fifteen reference-list entries never appear in the body text

Sixty percent of the apparatus is uncited, including three entries directly on the paper's own topic. A reference list that large relative to its in-text use cannot be taken as evidence of the literature actually consulted, and the Literature Review's coverage claims cannot be assessed against it. Repair requires either citing these sources where they bear on the argument or removing them, and in the former case revising §2's account accordingly.
- **Severity**: Major
- **Evidence Anchor**: `absence: reference list versus body text — expected at least one in-text citation for nine entries (Ainsworth & Devi, Berange 2021, Delacroix & Ohno, Halloran, Kessler & Amadou, Montez, Prakash & Tolliver, Solberg & Whitfield, Wexler & Ojo); checked Introduction, Literature Review, Methods, Results, Discussion, Conclusion`
- **Confidence**: 5 — exhaustive entry-by-entry check of the submitted text

### W5: The persistence and gateway-course retention literature the paper's claims depend on is never engaged

No persistence model, no early-alert evaluation, and no gateway-course intervention study is cited; §1's elevated-risk premise carries no citation; the Halloran (2020) review of exactly this literature sits uncited in the paper's own list. A study claiming retention effects and recommending institutional deployment cannot situate either claim without this body of work, and doing so would likely change the framing of the association reported in §4.2.
- **Severity**: Major
- **Evidence Anchor**: `absence: §1 and §2 — expected engagement with the student-persistence and gateway-course retention literatures; checked Introduction, Literature Review, Discussion, Conclusion, reference list`
- **Confidence**: 5 — this is the literature I work in

### W6: The self-regulated learning framing is invoked but not measured, and a single "perceived control" item is treated as evidence about SRL phases

Forethought, performance, and reflection are named in §1 and §2; none is measured. §5 nonetheless reads the perceived-control result as consistent with dashboards scaffolding "monitoring and adjustment," which the instrument cannot speak to. The framing is also unstable about which phase is implicated, and treats self-monitoring as a phase. Either the SRL claim is withdrawn or phase-appropriate measures are collected; as submitted, one of the paper's two headline claims lacks a construct-valid measure.
- **Severity**: Major
- **Evidence Anchor**: `text: §5 "consistent with a self-regulated learning account in which dashboards scaffold monitoring and adjustment" and §1 "supplies the feedback that fuels the reflective phase"`
- **Confidence**: 4 — SRL measurement is adjacent to rather than central to my own empirical work

### W7: The Abstract reports an effect size the Results contradict

The Abstract states r = .42; §4.2 reports r = .24. The Abstract's value is roughly three-quarters larger than the analysis it summarises, and abstract-level readers, citing authors, and any subsequent synthesis would ingest the wrong magnitude. Since §5's "modest size" reading is calibrated to the smaller value, the two sections describe materially different findings.
- **Severity**: Major
- **Evidence Anchor**: `text: Abstract "Dashboard engagement correlated positively with retention (r = .42)" and §4.2 "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"`
- **Confidence**: 5 — direct within-manuscript comparison

### W8: The Conclusion characterises the state of the evidence in terms the field's literature does not support

§6 calls dashboard engagement "a dependable strategy" and "a practical and generalizable lever" for institutions worldwide. The dashboard-effects literature is heterogeneous, with null and negative findings among them the very source cited at W1, and §1 concedes the area has "attracted more enthusiasm than evidence." A single-course correlation of r = .24 licenses no dependability claim, and the Conclusion must be rewritten to match both the study's evidence and the field's.
- **Severity**: Major
- **Evidence Anchor**: `text: §6 "For higher education institutions worldwide, the implication is clear" and §1 "has attracted more enthusiasm than evidence"`
- **Confidence**: 4 — judgement about the field's aggregate evidence base, held with appropriate uncertainty

### W9: Reference entries cannot be verified from the manuscript; all fifteen DOIs share a placeholder-range prefix with a mechanical suffix pattern

Every entry resolves through the 10.5555 prefix with sequentially patterned suffixes across otherwise unrelated journals. I cannot determine from the submission whether these are real records with substituted identifiers or unverifiable entries, but the pattern is not what fifteen genuine records from five publishers produce, and the editor should verify before any decision. If verification fails, the literature framing has no evidentiary basis at all and my repairable assessment of this dimension would not survive.
- **Severity**: Major
- **Evidence Anchor**: `text: References "10.5555/1010203" and "10.5555/1516718"`
- **Confidence**: 3 — pattern-level inference; I cannot resolve identifiers from the manuscript alone

### W10: The claim that single-item overall ratings are standard practice in this literature is uncited and does not match field norms

§3.3 justifies the perceived-control measure by asserting that such items are "common in dashboard studies to limit survey burden." No source is given, and for regulatory and control constructs the norm in this literature is validated multi-item instrumentation. The justification should be either supported or dropped in favour of a plain acknowledgement of the measurement compromise.
- **Severity**: Minor
- **Evidence Anchor**: `text: §3.3 "single-item overall ratings are common in dashboard studies to limit survey burden"`
- **Confidence**: 4 — familiarity with instrumentation practice in adjacent survey-based persistence research
