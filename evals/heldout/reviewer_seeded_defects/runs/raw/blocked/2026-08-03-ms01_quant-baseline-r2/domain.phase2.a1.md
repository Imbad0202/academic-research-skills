## Scoring Plan Dissent

*(none — omitted)*

Wait — that placeholder is not permitted. Removing it.

contract_role: domain

## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: block
trigger: "a key cited source materially misrepresented in a way that props up the paper's own argument"
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

I read this manuscript against the state of the student-facing learning analytics literature and against the higher education retention literature it invokes, checking each attributed claim against what the cited source's own title and stated scope indicate, each technical construct against its accepted definition, and each reported quantity against the samples the paper describes.

The decisive problem is a citation reversal. §2's equity paragraph attributes to Ferro & Nakamura (2021) the claim that dashboards "reliably improve outcomes for lower-achieving students," but that reference is titled *When dashboards demotivate: Peer comparison and the lower-achieving student*. The source is cited against its own argument, and the misread is not incidental: the paragraph says "we return to it in the Discussion," and §5's reading that the results "align with the view that externalized progress cues can support persistence" rests on the inverted version. The paper then, two sentences later, cites Osei (2020) for exactly the demotivation finding it has just attributed to the opposite conclusion, so §2 simultaneously asserts and denies the same proposition. The word "reliably" compounds this: the differential-benefit question is one of the most contested in this literature, and the manuscript's own opening sentence of §2 concedes that findings are "far from uniform."

The second domain failure is that the theory does no work. §1 commits to a forethought/performance/reflection cycle and claims the dashboard "supplies the feedback that fuels the reflective phase," but no phase of that cycle is operationalized anywhere in §3. What exists is one cross-sectional single-item perceived-control rating. §5 then upgrades that item to "perceived control as a mediating construct." In this field, mediation is a defined technical claim requiring temporal ordering and an estimated indirect path; none is present, and the cross-sectional design cannot distinguish perceived control as a consequence of dashboard use from perceived control as an antecedent that predisposes students to open the dashboard at all. The reverse ordering is at least as plausible and would invert the paper's entire mechanism story. As written, the self-regulated learning frame constrains no prediction and could be deleted without changing a single analysis.

Third, "retention" is not the construct the higher education literature means when it discusses attrition. The paper measures remaining enrolled and sitting the final assessment in one introductory statistics course, then generalizes to "undergraduate attrition," "the first-year gateway course," and institutional retention "across programs and disciplines." Course non-completion and institutional departure have distinct determinants, and a student who drops one statistics course may persist at the institution without interruption. Nothing in §3 establishes that this is a first-year course or that participants are first-year students, so the gateway framing has no empirical basis in the sample described. This is repairable by rewording plus deletion of §6's institutional claims, but the repair shrinks the stated contribution considerably, which the venue-fit reviewer should weigh.

Fourth, the reference list appears to have been assembled independently of the argument. Six of fifteen entries are cited in text; nine never appear. Meanwhile the claims that most need attribution carry none: the gateway-attrition premise in §1 is unsourced even though Halloran (2020), *Retention in the gateway course*, sits uncited in the list, and the self-regulated learning model is described with no primary-source attribution even though Kessler & Amadou (2019) sits uncited. The paper also does not engage any review of dashboard–outcome studies, which is where a reader would look to learn whether a within-course correlation of this magnitude is news. Every DOI uses the reserved `10.5555/` test prefix, so no reference is independently checkable; I flag this as a verification failure rather than asserting fabrication, but if editorial checking finds the sources do not exist, the correct outcome escalates beyond the block I record here.

I stop short of a fatal block because the empirical core — a modest within-course association between session counts and course completion — could survive correction of the citation record, honest re-labelling of the construct, and removal of the causal and institutional claims. That is substantive rework, not retraction.

On my own limits: I did check the reported degrees of freedom and sample accounting, and several quantities do not reconcile; I record them below but they belong to the methodology reviewer's dimension, as does the non-disclosure of log-data analysis to participants, which I flag rather than adjudicate.

**Strengths**

### S1: Engagement-proxy critique is accurately rendered and applied reflexively

§2's account of click-based proxies matches the field's position and, unusually, is turned on the authors' own measure rather than left as a critique of others.
**Evidence Anchor**: `text: §2 "Most dashboard studies, including the present one, infer engagement from coarse behavioral proxies such as page views or session counts"`
**Confidence**: 5 — I co-authored a systematic review of dashboard–outcome studies and this is the standard measurement caveat.

### S2: The demotivation and goal-orientation literature is correctly represented

The Osei (2020) paragraph states the framing-dependence of the effect and the performance-avoidance mechanism accurately and with appropriate hedging; this is the one place where the paper's picture of the field is trustworthy.
**Evidence Anchor**: `text: §2 "Performance-avoidance oriented students, in particular, may interpret an unfavorable comparison as a threat to be avoided rather than a problem to be solved"`
**Confidence**: 5 — direct familiarity with the relative-standing feedback literature.

### S3: Candid disclosure of the median split and sessionization rule

§3.3 names the median split as a coarse simplification adopted for interpretability and specifies the thirty-minute sessionization rule, which is more measurement transparency than most deployments report.
**Evidence Anchor**: `text: §3.3 "This median split is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency"`
**Confidence**: 4 — based on routine reading of dashboard deployment methods sections.

### S4: Dashboard-design specificity is correctly identified as a limit on transfer

§5.1 recognizes that interface features condition student response, which is the caveat this literature most often omits.
**Evidence Anchor**: `text: §5.1 "the specific dashboard design used here differs from those deployed elsewhere; the particular interface features may shape how students respond"`
**Confidence**: 4 — consistent with cross-deployment heterogeneity findings in the review literature.

**Weaknesses**

### W1: Ferro & Nakamura (2021) is cited against its own finding, and the misread carries structural weight

The attributed claim is the negation of the cited paper's stated finding, and §2 explicitly forwards it into the Discussion, where it supports the alignment reading in §5. A reader relying on §2 acquires a false belief about the field's position on lower-achieving students. Uncorrected, this cannot be published; correcting it removes §5's equity-oriented interpretation entirely.
**Severity**: Critical
**Evidence Anchor**: `text: §2 and References, "Dashboards have been shown to reliably improve outcomes for lower-achieving students" attributed to "When dashboards demotivate: Peer comparison and the lower-achieving student"`
**Confidence**: 5 — the contradiction is internal to the manuscript and does not depend on retrieving the source.

### W2: A causal effect is asserted as domain fact against the paper's own design and its own cited audit

§5 states that engagement "improved course retention" and that increasing engagement "raises the probability" of completion; §6 calls dashboards "a dependable strategy." Nothing in the field establishes a causal dashboard-to-outcome effect, and §2 cites Ibarra (2023) precisely for auditing this error before committing it. The hedging in §1 and §2 is abandoned exactly where it becomes inconvenient.
**Severity**: Critical
**Evidence Anchor**: `text: §5 "dashboard engagement improved course retention" and §6 "a dependable strategy for improving retention across programs and disciplines"`
**Confidence**: 5 — the design is described as cross-sectional and observational by the authors.

### W3: Course completion is conflated with institutional persistence

The measured construct is within-course completion; the framing and implications are about undergraduate attrition, gateway-course risk, and retention across programs. These are distinct constructs with distinct determinants, and no year-level or enrollment-continuation data are reported that would license the institutional reading.
**Severity**: Major
**Evidence Anchor**: `text: §3.3 "remained enrolled and completed the final assessment" against §1 "the first-year gateway course is frequently identified as a point of elevated risk"`
**Confidence**: 5 — this is a core distinction in the retention literature the paper invokes.

### W4: "Mediating construct" is used without any mediation test, and the SRL cycle is never operationalized

Mediation is a defined technical claim; the paper offers a single cross-sectional item and a median-split t-test. No phase of the forethought/performance/reflection cycle is measured, and the causal ordering the mechanism story requires is untested and reversible.
**Severity**: Major
**Evidence Anchor**: `text: §5 "perceived control as a mediating construct" and §1 "supplies the feedback that fuels the reflective phase"`
**Confidence**: 5 — mediation requirements are standard in this literature.

### W5: Load-bearing domain premises carry no attribution while nine of fifteen references go uncited

The reference list is decoupled from the argument: the motivating attrition premise and the SRL model are unsourced, relevant listed entries are never invoked, and no review of dashboard–outcome studies is engaged, so the reader cannot locate the paper's claims in the field's evidence base.
**Severity**: Major
**Evidence Anchor**: `absence: §1 and §2 motivating claims — expected in-text citations for gateway-course attrition risk and for the forethought/performance/reflection self-regulated learning model; checked §1, §2, §5, §6, and the fifteen-entry reference list`
**Confidence**: 5 — counted directly against the reference list.

### W6: The abstract misreports the study's own headline effect

The abstract gives r = .42; §4.2 gives r = .24. The abstract's figure implies roughly three times the shared variance, and abstracts are what secondary reviewers and meta-analysts extract.
**Severity**: Major
**Evidence Anchor**: `text: Abstract "Dashboard engagement correlated positively with retention (r = .42)" and §4.2 "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"`
**Confidence**: 5 — direct textual comparison.

### W7: A self-selected volunteer sample is labelled a random sample

§3.2 claims a random sample and then describes an opt-in announcement with non-respondents excluded. "Random sample" is a defined term whose misuse licenses inferential claims the recruitment cannot support, and the volunteer route plausibly enriches the sample for engaged, persisting students, biasing the focal association.
**Severity**: Major
**Evidence Anchor**: `text: §3.2 "using a random sample of students enrolled in the course section" and "the resulting sample reflects those who volunteered during the recruitment window"`
**Confidence**: 5 — the two descriptions are mutually exclusive on their face.

### W8: No reference is verifiable because every DOI uses the reserved test prefix

All fifteen entries resolve to the `10.5555/` test namespace, so the citation record cannot be checked by a reader or an editor. I treat this as a verification failure requiring editorial confirmation; if the sources do not exist, the integrity problem is of a different and more serious kind.
**Severity**: Major
**Evidence Anchor**: `text: References, "https://doi.org/10.5555/1010203" and "https://doi.org/10.5555/1516718"`
**Confidence**: 4 — the prefix is reserved for testing; I cannot rule out placeholder typesetting.

### W9: "Disciplinary breadth" is asserted with no distribution reported

§3.1 uses breadth within a single course to soften the single-site limitation, and §6 leans on it for generalization across programs, but no distribution of majors or year levels appears anywhere.
**Severity**: Minor
**Evidence Anchor**: `absence: §3.1 sample description — expected a reported distribution of majors or year levels evidencing disciplinary breadth; checked §3.1, §3.2, §4.1, Table 1, and Table 2`
**Confidence**: 4 — based on what a reader would need to accept the breadth claim.

### W10: SRL phase terminology drifts between sections

§1 names a three-phase cycle and locates dashboard feedback in the reflective phase; §2 relocates the mechanism to "forethought and self-monitoring." Self-monitoring is conventionally situated in the performance phase, so the two passages describe different mechanisms without acknowledging the shift.
**Severity**: Minor
**Evidence Anchor**: `text: §2 "dashboards are hypothesized to support the forethought and self-monitoring phases of learning" and §1 "phases of forethought, performance, and reflection"`
**Confidence**: 4 — standard phase definitions in the SRL tradition.

### W11: Participants were not informed their dashboard log data would be analyzed

I note this rather than adjudicate it; consent scope belongs to the methodology reviewer's dimension, but an editor will need a disclosure and approval statement before this can proceed.
**Severity**: Major
**Evidence Anchor**: `text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study"`
**Confidence**: 3 — I read consent scope as an editorial and ethics-review matter rather than my area of expertise.

### W12: Reported sample sizes and test statistics cannot be reconciled with the described samples

Table 2's groups sum to 127 while §4.3 states all 142 students were classified; the perceived-control comparison reports t(156) although only 87 respondents answered the item; and the exam comparison reports t(140) = 1.31 with p = .008 while describing the difference as not reaching a comparable level. Referred to the methodology reviewer.
**Severity**: Major
**Evidence Anchor**: `table: Table 2 engagement-group n column (66 + 61 = 127) versus §4.3's classification of all 142 students`
**Confidence**: 4 — arithmetic and distributional checks, not a re-analysis of raw data.

### W13: The secondary clarity statistic is impossible for the described response scale

With ten integer responses on a 1–5 scale and a mean of exactly 3.00, the smallest attainable non-zero sample SD is about 0.47; SD = 0.10 cannot arise from any such response pattern. The item is descriptive only, but an impossible statistic must be resolved before publication. Referred to the methodology reviewer.
**Severity**: Major
**Evidence Anchor**: `text: §4.1 "N=10; M=3.00; sample SD=0.10; integer scale=1-5"`
**Confidence**: 4 — direct calculation over integer response patterns.
