## Scoring Plan Dissent

*(none — omitted)*

Wait: per protocol, no dissent section is emitted. Proceeding directly.

contract_role: da

## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: block
trigger: "a causal or effectiveness claim resting on observational association, a predictor and outcome that are definitionally entangled"
block_class: repairable

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

Reconstructed as a chain, the manuscript argues: (P1) dashboard sessions were counted from LMS logs; (P2) session count correlates with completing the final assessment; (P3) high-session students self-report greater perceived control; (C1) therefore dashboards support self-regulation; (C2) therefore increasing dashboard engagement raises retention; (C3) therefore institutions worldwide should deploy dashboards as a dependable retention lever. Granting every datum and disputing only the inferences, the chain fails at P2→C2 and again at C2→C3, and the pillar supporting P3 does not exist in the form the paper reports. D3 is scored block.

The first break is arithmetic, not inferential, but it is load-bearing: the Abstract reports the headline association as r = .42 while §4.2 reports r = .24. These differ by a factor of roughly three in variance explained. One of them is wrong and the manuscript never reconciles them, so a reader cannot state what the paper found. Every downstream claim about effect magnitude — including §5's "modest size" hedge, which is calibrated to .24, and the Abstract's "promising lever" framing, which reads as calibrated to .42 — inherits an unresolved premise.

The second break is the causal escalation the paper explicitly promises to avoid. §1 states the authors "are careful throughout to distinguish the pattern in the data from the causal story that might explain it," and §2 recruits Ibarra (2023) to criticise exactly this failure in others. §5 then opens with "dashboard engagement improved course retention" and asserts that "increasing dashboard engagement therefore raises the probability that a student completes the course"; §6 compounds it with "is associated with, and raises." The design is declared observational and cross-sectional in §3.1. This is not hedge-free phrasing at the margin; it is the manuscript's stated central finding, asserted in a form the design cannot license, and the manuscript's own literature review supplies the standard it violates. Self-awareness in §2 aggravates rather than mitigates: the authors identified the error class and then committed it.

The third break is the most damaging, because it threatens the association itself and the paper never names it. Dashboard engagement is "the number of distinct sessions in which a student opened the dashboard view during the term"; retention is whether the student remained enrolled through the final assessment. A student who withdraws in week 8 has roughly half the opportunity window of a student who completes, so session count is partly constituted by enrollment duration, which is the outcome. The predictor and outcome are mechanically entangled, and an r of .24 is exactly what one would expect from exposure time alone with no dashboard effect whatsoever. The recruitment design deepens this: the sample was assembled from mid-term survey volunteers, so students who withdrew before the recruitment window are structurally absent, and the surviving retention variance is restricted to late withdrawals and final-exam no-shows. Neither exposure-window artifact nor survivorship appears anywhere in §5.1, whose three named limitations (proxy quality, self-report bias, single course) are all comparatively harmless. Reverse causation — persisting students accumulate clicks — is equally unaddressed, as is confounding by prior achievement or conscientiousness, which would predict both dashboard use and completion with no causal path between them.

The perceived-control pillar cannot be evaluated as reported. §4.1 states the item was answered by 87 respondents; §4.3 tests the group difference with t(156) = 3.02, which requires 158 observations — more than the 87 responders and more than the 142-student analytic sample. The test as printed cannot have been run on any sample this paper describes, so the Abstract's claim that high-engagement students "reported higher perceived control" currently has no valid support. §5 then upgrades this to a mediation claim ("perceived control as a mediating construct") on the basis of a two-group mean comparison with no mediation model, no temporal ordering, and cross-sectional data. The secondary exam comparison is internally impossible in a different way: t(140) = 1.31 yields p ≈ .19, not the reported .008, and the surrounding prose ("did not reach a comparable level," "the difference was small") contradicts the significance the printed p asserts. Table 2's group sizes sum to 127 against the 142 the text says were classified and the 142 that t(140) implies.

The conclusion then leaps from one 15-week introductory statistics section at one institution, sampled from mid-term volunteers, to "higher education institutions worldwide," "across programs and disciplines," and a "dependable strategy." This is asserted one section after §5.1 concedes the study "was conducted within a single introductory statistics course" and that interface features may drive the response. The manuscript asserts a restriction and its negation as jointly true, and the negation is what the Conclusion sells to practitioners. I note that §3.1's claim of "disciplinary breadth" within a single required course does no work here — a service course's major mix is not a sampling frame across programs.

Two further items fall outside D3 but bear reporting. §3.2 describes the sample as drawn "using a random sample of students enrolled in the course section" and then, in the next paragraph, describes voluntary response to an LMS announcement with non-responders excluded — these cannot both be true, and no response rate or enrollment denominator is given against the "several hundred" enrolled. §2 cites Ferro and Nakamura (2021) as having shown that dashboards "reliably improve outcomes for lower-achieving students," while the reference list gives that work's title as "When dashboards demotivate: Peer comparison and the lower-achieving student"; the citation appears to be recruited against its own finding, and §2 flags that this claim returns in the Discussion. Separately, the Abstract claims "self-regulated learning behavior" was measured, but §3.3 defines only engagement, retention, and a single perceived-control item; Table 1 also reports a final exam score that §3.3 never defines. Finally, §3.2 states plainly that "Students were not informed that their dashboard activity data would be analyzed for this study," and no ethics-review or IRB statement appears anywhere.

I stop short of fatal deliberately. The logs are timestamped, so engagement restricted to a pre-recruitment window can be re-estimated on a cohort conditioned on mid-term enrollment; the correlation can be reported correctly; the causal and global-generalization claims can be withdrawn; the group tests can be re-run and reported with correct denominators. That is a demanding revision, but it does not strictly require new data collection, so the block is repairable rather than fatal. What it does require is that the authors abandon the thesis as currently stated. Nothing in this manuscript licenses the sentence "dashboard engagement improved course retention."

#### CRITICAL

| # | Issue | Evidence Anchor | Confidence |
|---|---|---|---|
| C1 | The headline association is reported at two irreconcilable magnitudes, so the paper's central quantitative claim cannot be stated. Abstract and Results disagree by a factor of about three in variance explained, and no erratum, rounding, or subsample explanation is offered. | text: Abstract and §4.2, "Dashboard engagement correlated positively with retention (r = .42)" versus "positively associated with course retention (r = .24, p = .004)" | 5 (correlation reporting conventions) |
| C2 | The stated central finding is causal and effectiveness-framed while the design is observational and cross-sectional, so the conclusion is not entailed by the evidence even if every number is granted. The manuscript's own §2 identifies this error class before committing it. | text: §5 and §3.1, "The central finding of this study is that dashboard engagement improved course retention" against "This study used an observational, cross-sectional design" | 5 (causal inference from observational designs) |
| C3 | Predictor and outcome are mechanically entangled: sessions are counted across the whole term, so enrollment duration, which is the outcome, determines the exposure window. Mid-term volunteer recruitment additionally excludes early withdrawers, making the reported association an expected artifact rather than a finding. | text: §3.3 and §3.2, "the number of distinct sessions in which a student opened the dashboard view during the term" and "Midway through the term, an announcement was posted to the course LMS" | 5 (survivorship and exposure-window artifacts) |
| C4 | The perceived-control group comparison reports degrees of freedom implying 158 observations, exceeding both the 87 item responders and the 142-student analytic sample. The Abstract's second pillar claim therefore rests on a test that cannot have been run on any sample described. | text: §4.3 and §4.1, "t(156) = 3.02, p = .003" against "the 87 survey respondents who answered the item" | 5 (t-test degrees-of-freedom arithmetic) |
| C5 | The Conclusion asserts a worldwide, cross-disciplinary policy recommendation and calls dashboard investment dependable, directly contradicting the single-course scope conceded one section earlier. The manuscript asserts a scope restriction and its negation as jointly true, and sells the negation to practitioners. | text: §6 and §5.1, "investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy for improving retention across programs and disciplines" against "the study was conducted within a single introductory statistics course" | 5 (external validity and generalization standards) |
| C6 | Behavioral log data were analyzed without informing participants, whose consent covered only the survey, and no ethics-review or approval statement appears anywhere in the manuscript. Uncorrected, this precludes publication regardless of the empirical findings. | text: §3.2, "Students were not informed that their dashboard activity data would be analyzed for this study" | 5 (research ethics for secondary use of trace data) |

#### MAJOR

| # | Issue | Evidence Anchor | Confidence |
|---|---|---|---|
| M1 | The exam comparison reports a p-value inconsistent with its own test statistic (t = 1.31 at df = 140 gives p of roughly .19), and the surrounding prose describes the result as small and non-comparable while the printed p would be significant at the stated alpha. Numeric and verbal claims contradict each other. | text: §4.3, "the difference was small, t(140) = 1.31, p = .008" alongside "did not reach a comparable level" | 5 (t-distribution p-value arithmetic) |
| M2 | Group sizes in the exam comparison do not reconcile with the text or with the reported degrees of freedom, leaving the denominators of the secondary analysis undetermined. | table: Table 2, Final exam comparison by engagement group, n column values 66 and 61 summing to 127 against the 142 classified in §4.3 and the 142 implied by df = 140 | 5 (sample accounting) |
| M3 | The sampling description is self-contradictory: the section claims a random sample of enrolled students and then describes voluntary response to an LMS announcement with non-responders excluded. No response rate or enrollment denominator is reported against the several hundred enrolled, so every generalization rests on an unspecified self-selected subset. | text: §3.2, "using a random sample of students enrolled in the course section" versus "Students who chose to respond, and who consented to the survey, formed the study sample" | 5 (sampling frame and self-selection) |
| M4 | The limitations section names only proxy quality, self-report bias, and single-course scope, omitting the rival explanations that would actually dissolve the finding: confounding by prior achievement or conscientiousness, reverse causation, and selection on mid-term persistence. The argument never confronts its strongest opposition. | absence: §5.1 Limitations — expected treatment of confounding, reverse causation, and prior-achievement selection; checked §5.1 limitations list, §5 discussion, §3.4 analysis | 5 (rival-explanation adequacy) |
| M5 | A mediation claim is asserted from a two-group mean comparison, with no mediation model, no path estimates, and no temporal ordering available in a cross-sectional design. The claim's strength exceeds anything the analysis section attempted. | text: §5, "It also complements accounts emphasizing perceived control as a mediating construct" | 4 (mediation analysis requirements) |
| M6 | A cited source is recruited as supporting a claim that its own title indicates it contests, and §2 flags this claim as returning in the Discussion to underwrite the equity framing. If the citation is reversed, the discussion's alignment argument loses its stated warrant. | text: §2 and References, "Dashboards have been shown to reliably improve outcomes for lower-achieving students" against the listed title "When dashboards demotivate: Peer comparison and the lower-achieving student" | 4 (citation-to-source correspondence) |
| M7 | The Abstract claims self-regulated learning behavior was measured, but the Measures section defines only session counts, dichotomous retention, and a single perceived-control item. The construct named in the theoretical framing is never operationalized, so the SRL account in the Discussion is asserted rather than tested. | absence: §3.3 Measures — expected a self-regulated learning behavior instrument matching the Abstract's claim; checked §3.3 measure definitions, §3.4 analysis, Table 1, §4 results | 5 (construct operationalization) |
| M8 | The secondary clarity item's reported dispersion is impossible for the stated data: ten integer responses on a 1-5 scale with a mean of exactly 3.00 admit either SD = 0 or SD of at least about 0.47, never 0.10. The same section reports a single-item mean to three decimals, implying precision the instrument cannot carry. | text: §4.1, "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5" | 5 (variance arithmetic on bounded integer scales) |
