contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: block
block_class: fatal
trigger: "internally impossible statistics (numbers that contradict each other, percentages or degrees of freedom inconsistent with the stated N)"

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: block
block_class: repairable
trigger: "correlational findings narrated as causal effects, generalisation well beyond the sampled population or setting"

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

My first pass on any submission is to recompute the reported statistics from the manuscript's own stated sample sizes. This manuscript does not survive that pass. Of the three inferential results reported, exactly one — the correlation in §4.2 — reproduces. Taking r = .24 with N = 142 gives t = .24 × √140 / √(1 − .0576) = 2.93 on 140 df, two-tailed p ≈ .004, which matches the printed p exactly. That single consistency is diagnostically useful rather than reassuring: it establishes that the authors can produce internally coherent output when the underlying numbers are real, and it therefore sharpens rather than softens the question of why the remaining results cannot be reconstructed.

They cannot. The perceived-control comparison is reported as t(156) = 3.02. Only 87 respondents answered that item (§4.1, §3.2), so a two-group independent-samples test on those respondents has at most 85 degrees of freedom; even if every member of the primary analytic sample had answered, the ceiling would be 140. A df of 156 implies 158 contributing observations, sixteen more people than the study says it has. The exam comparison is reported as t(140) = 1.31, p = .008; for that statistic the two-tailed p is approximately .19, and the surrounding prose simultaneously describes the difference as "small" and as not reaching "a comparable level," so the printed p contradicts both the test statistic and the authors' own reading of it. Table 2's group sizes sum to 127, not the 142 the adjacent sentence claims were "all" classified, and 127 would yield df = 125. That discrepancy is not a typographical slip, because §3.3 codes as not retained anyone who withdrew or did not sit the final; such students have no final exam score by construction. Either all 142 sat the final — in which case retention is a constant and the r = .24 of §4.2 cannot exist — or fewer than 142 have exam scores, in which case the claim of 142 and the df of 140 are both false. The descriptives fail the same feasibility test. A mean of 3.847 on a 1–5 integer item answered by 87 people requires a response total of 334.69; the two attainable neighbours are 334/87 = 3.839 and 335/87 = 3.851, and neither rounds to 3.847. The secondary clarity item is reported at N = 10, M = 3.00, sample SD = 0.10 on the same integer scale; with an exact integer mean of 3, all deviations are integers, so the sum of squared deviations is either 0 (SD = 0) or at least 2 (SD = √(2/9) = 0.47). A sample SD of 0.10 lies in a gap that ten integer responses cannot occupy.

Individually, each of these could be a transcription error. Collectively, across five of the six numeric results in the paper, they mean that no reader can determine which numbers correspond to an analysis that was actually run, on which cases. That is why D1 carries a fatal block rather than a repairable one: the defect is not that the reporting is thin but that the reported quantities are mutually incompatible with the described sample, so no amount of rewriting the present manuscript rehabilitates them. What would be needed is the raw response file, the analysis script, and a recomputation — that is, verification that the study was performed as described, not a revision of how it is described.

The design problems are independent of the arithmetic and would be serious even if every number reconciled. §3.2 contains two incompatible sampling descriptions in consecutive paragraphs: a "random sample of students enrolled in the course section," and then self-selected volunteers who answered a mid-term LMS announcement. These cannot both be true, and only the second is consistent with the stated procedure. No response rate is given against an enrollment described only as "several hundred," so the sampling fraction is unknown and the population of inference is undefined. The selection runs in the same direction as the exposure — students who volunteer for a survey "about their study habits and their use of the dashboard" are disproportionately the students who use the dashboard — and in the same direction as the outcome, because recruitment happened mid-term while the outcome is end-of-term retention, so students who withdrew earliest cannot appear in the sample at all. Both mechanisms inflate the reported association. The authors do not name either one; §5.1 raises three measurement caveats and no design threats.

The analytic choices compound this. Pearson correlation is declared for "continuous measures," but retention is dichotomous; what was computed is a point-biserial coefficient, which is never named and whose value is bounded by the marginal split, so .24 cannot be interpreted without the retention rate in each group — a quantity the paper never reports. Engagement is a right-skewed count (§4.1) reduced by median split (§3.3), a step the authors correctly identify as costly and then take anyway without reporting the split value or a continuous-predictor sensitivity check. The exposure itself is defined by a thirty-minute inactivity threshold inherited from a platform default, with no demonstration that conclusions are stable under alternatives. Nothing is adjusted for prior achievement, motivation, or enrollment intent. No effect size or confidence interval accompanies any comparison. Three tests are run at α = .05 with no multiplicity control. There is no availability statement for data, code, or the instrument, the software is unnamed, and no ethics approval or exemption is recorded anywhere while §3.2 affirmatively states that students were not told their behavioral data would be analyzed.

On D3 I score block rather than fatal because the coherence failure, unlike the arithmetic, is in principle repairable by rewriting. The paper's own Introduction commits to distinguishing "the pattern in the data from the causal story," and its Literature Review endorses a critical audit of causal language in correlational analytics. The Discussion then opens by asserting that engagement "improved" retention and that increasing engagement "raises the probability" of completion, and the Conclusion extends this to institutions "worldwide" as a "dependable strategy" and "generalizable lever" — from one introductory statistics course at one university, contradicting the third item of the authors' own limitations paragraph. Strip the causal verbs and the global scope and a modest, honestly-scoped correlational report remains; that is what repairable means here. It does not mean the current text is close to acceptable.

I note two boundaries on my own reading. Whether the cited literature is characterised accurately, and whether the undisclosed use of log data breaches a specific regulatory regime, fall to the domain and editorial seats; I raise the ethics gap only insofar as approval and consent are part of the methods a reader must be able to evaluate. I also do not adjudicate whether session counts are the right construct in the first place, beyond noting that the paper's own Literature Review says they are not and the Methods proceeds as if that caution had not been written.

### S1: Design type is stated plainly rather than left implicit
**Evidence Anchor**: text: §3.1 "This study used an observational, cross-sectional design conducted within a single 15-week undergraduate introductory statistics course"

### S2: Retention is given an explicit, auditable coding rule
**Evidence Anchor**: text: §3.3 "was coded dichotomously as whether the student remained enrolled and completed the final assessment"

### S3: The cost of the median split is self-identified rather than concealed
**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency"

### S4: The distributional problem with the exposure variable is disclosed
**Evidence Anchor**: text: §4.1 "Dashboard engagement was right-skewed, with a small number of highly active students accounting for a disproportionate share of dashboard sessions."

### W1: Degrees of freedom for the perceived-control test exceed the maximum the sample permits
**Severity**: Critical
**Evidence Anchor**: text: §4.3 "t(156) = 3.02, p = .003"
**Confidence**: 5 — recomputing df from stated Ns is my routine first-pass check

With 87 item respondents split into two groups, df ≤ 85; with the full analytic sample of 142, df ≤ 140. A df of 156 requires 158 observations that the study does not have. This is one of the paper's two headline claims and it cannot have been produced by the described data.

### W2: The exam comparison's analytic sample is internally impossible
**Severity**: Critical
**Evidence Anchor**: table: Table 2 (§4.3), n column entries 66 and 61 versus the adjacent text claim that all 142 students were classified and the reported df of 140
**Confidence**: 5 — arithmetic on reported subgroup sizes plus the paper's own retention coding rule

66 + 61 = 127, implying df = 125. More seriously, §3.3 codes non-completers as not retained, so they have no exam score; if all 142 truly contributed, retention is constant and the §4.2 correlation cannot exist. The two statements cannot both be true.

### W3: Sampling frame is self-contradictory and the selection runs on the exposure
**Severity**: Critical
**Evidence Anchor**: text: §3.2 "Participants were drawn from the course enrollment using a random sample of students enrolled in the course section." and "Students who chose to respond, and who consented to the survey, formed the study sample"
**Confidence**: 5 — the incompatibility is on the face of the text; the confounding direction follows from the recruitment topic

A volunteer sample recruited by an announcement about dashboard use over-represents dashboard users. With no response rate against "several hundred" enrolled, the sampling fraction and the population of inference are both unknown, and the association cannot be attributed to anything in particular.

### W4: Mid-term recruitment makes the sample survivor-conditioned on the outcome
**Severity**: Critical
**Evidence Anchor**: text: §3.2 "Midway through the term, an announcement was posted to the course LMS inviting students to complete a short survey"
**Confidence**: 5 — standard survivorship reasoning for a retention outcome with post-baseline enrollment

Students who withdrew before the announcement cannot appear, so the earliest and least-engaged leavers are structurally absent. The truncation removes exactly the cases that would attenuate the engagement–retention association, biasing it upward in the direction the paper reports. No existing-data remedy exists; this requires cohort-inception sampling.

### W5: Human-subjects basis is absent and log-data use was undisclosed to participants
**Severity**: Critical
**Evidence Anchor**: text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."
**Confidence**: 4 — the disclosure gap is explicit; specific regulatory consequences are outside my seat

Consent is described as covering the survey only, while the primary exposure variable comes from behavioral logs collected without notice. No institutional review approval, exemption, or waiver is recorded anywhere in the manuscript.

### W6: Causal claims are asserted from a cross-sectional observational design
**Severity**: Critical
**Evidence Anchor**: text: §5 "The central finding of this study is that dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course"
**Confidence**: 5 — design-to-claim mismatch is directly checkable against §3.1

The stated design licenses association only, and the Introduction explicitly promises to maintain that distinction. As written, the paper's central conclusion must be withdrawn, not merely softened.

### W7: A reported p-value contradicts its own test statistic and the surrounding narrative
**Severity**: Major
**Evidence Anchor**: text: §4.3 "but the difference was small, t(140) = 1.31, p = .008"
**Confidence**: 5 — t-to-p conversion at df = 140 is unambiguous

t = 1.31 on 140 df gives two-tailed p ≈ .19. The printed value would be significant at the paper's own α, yet the text treats the difference as unremarkable. Correcting the p does not change the paper's reading, which is why this is Major rather than Critical.

### W8: The abstract's effect magnitude is nearly double the one in Results
**Severity**: Major
**Evidence Anchor**: text: Abstract "Dashboard engagement correlated positively with retention (r = .42)"
**Confidence**: 5 — direct comparison with §4.2, plus recomputation showing .24 matches the reported p and .42 does not

At N = 142, r = .42 implies t = 5.48 and p < .001, not the .004 reported. The abstract value is the one most likely to be extracted and cited.

### W9: The perceived-control mean is unattainable from 87 integer responses
**Severity**: Major
**Evidence Anchor**: text: §4.1 "The mean perceived-control score across the 87 survey respondents who answered the item was 3.847 (SD = 0.62)"
**Confidence**: 5 — granularity check on an integer-scale mean

3.847 × 87 = 334.69. The adjacent feasible means are 3.839 and 3.851. Either the N, the scale, or the mean is misstated.

### W10: The secondary item's dispersion is unattainable
**Severity**: Major
**Evidence Anchor**: text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Confidence**: 5 — enumeration of admissible sums of squares for ten integers with an exact mean of 3

With an exact integer mean, all deviations are integers, so the sample SD is either 0 or at least √(2/9) = 0.47. A value of 0.10 cannot arise.

### W11: A point-biserial coefficient is presented as a Pearson correlation between "continuous measures"
**Severity**: Major
**Evidence Anchor**: text: §3.4 "Associations between continuous measures were assessed with Pearson correlations."
**Confidence**: 4 — standard measurement-theory point; the specific attenuation depends on the unreported marginal split

Retention is dichotomous, so the coefficient's ceiling depends on the retention base rate, which is never reported. Group-wise retention rates and a logistic specification are the minimum needed to interpret .24.

### W12: No effect sizes or confidence intervals accompany any comparison
**Severity**: Major
**Evidence Anchor**: absence: §4.2 and §4.3 results reporting — expected effect size estimates with confidence intervals for the correlation and both t-tests; checked Abstract, §3.4 Analysis, §4.1 through §4.3, Table 1, Table 2, and §5 Discussion
**Confidence**: 5 — exhaustive scan of every results-bearing surface

The Discussion characterises the association as "modest" and "not large" with no interval to support that characterisation.

### W13: Confounding is neither adjusted for nor discussed
**Severity**: Major
**Evidence Anchor**: absence: §3.4 Analysis and §4 Results — expected a covariate-adjusted model or an explicit rationale for leaving prior achievement, major, and enrollment intent unadjusted; checked §3.1, §3.3, §3.4, §4.2, §4.3, and §5.1
**Confidence**: 5 — no covariate appears anywhere in the manuscript

Dashboard engagement is self-selected behavior. Any variable that predicts both engagement and persistence — prior attainment, workload, intent to complete — is a live alternative explanation, and none is measured or modelled.

### W14: Roughly 39% item nonresponse is handled by silent listwise deletion
**Severity**: Major
**Evidence Anchor**: text: §3.3 "Respondents who skipped the item were excluded from the perceived-control analyses."
**Confidence**: 5 — 55 of 142 missing is arithmetic from the reported Ns

No comparison of responders and non-responders, no missingness mechanism argued, no sensitivity analysis. The perceived-control claim rests on a subset defined by an unexamined selection step.

### W15: Median split is applied to a skewed count and the split point is never reported
**Severity**: Major
**Evidence Anchor**: text: §3.3 "students were split at the median number of dashboard sessions into high-engagement and low-engagement groups"
**Confidence**: 5 — the omission is verifiable and the information loss is standard

Without the median value the grouping is unreproducible, and with a right-skewed distribution the "high" group spans a range from just above the median to 48 sessions. A continuous-predictor analysis should be reported alongside.

### W16: The exposure variable depends entirely on an inherited sessionization default
**Severity**: Major
**Evidence Anchor**: text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity, following the platform's default sessionization rule."
**Confidence**: 4 — sessionization sensitivity is well documented in trace-data work

The thirty-minute threshold is a vendor convention, not a validated construct boundary. Because it determines the session count, the median split, and hence every group comparison, its arbitrariness propagates through the whole analysis unchecked.

### W17: The single-item measure carries no reliability or validity evidence
**Severity**: Major
**Evidence Anchor**: text: §3.3 "single-item overall ratings are common in dashboard studies to limit survey burden"
**Confidence**: 4 — prevalence is not psychometric justification

Common practice is offered in place of evidence. No test-retest, no convergent validity, no prior validation citation for this item, yet one of the paper's two claims rests entirely on it.

### W18: The limitations section omits every design-level threat
**Severity**: Major
**Evidence Anchor**: absence: §5.1 Limitations — expected acknowledgement of volunteer self-selection, mid-term survivorship on the retention outcome, and the design's inability to license causal claims; checked §1, §3.1, §3.2, §5, §5.1, and §6
**Confidence**: 5 — full read of every hedging surface in the manuscript

Three measurement caveats are listed while the sampling and inference threats that actually bound the conclusions go unmentioned, which is what allows the causal and global claims to pass unchallenged.

### W19: The conclusion generalises worldwide from one course at one institution
**Severity**: Major
**Evidence Anchor**: text: §6 "For higher education institutions worldwide, the implication is clear" and "a practical and generalizable lever"
**Confidence**: 5 — direct contradiction with the authors' own third limitation

The empirical core, scoped to this setting, could survive; the policy claim as written cannot.

### W20: Three tests are run at α = .05 with no multiplicity control
**Severity**: Minor
**Evidence Anchor**: text: §3.4 "an alpha of .05 was adopted throughout"
**Confidence**: 4 — familywise error is straightforward to state, and three tests is a modest family

Familywise error is approximately .14. Not decisive on its own, but it should be acknowledged or corrected.

### W21: No reproducibility affordances are provided
**Severity**: Minor
**Evidence Anchor**: absence: §3.4 Analysis and manuscript end matter — expected a data, code, and instrument availability statement, named software with version, and preregistration status; checked §3.3, §3.4, §4, §6, and the References list
**Confidence**: 5 — no such statement exists anywhere in the submitted text

"Standard statistical software" does not identify a package or version. Given the recomputation failures above, the absence of any verification path is what converts correctable errors into unresolvable ones.

### W22: Table 1 reports no sample size per measure
**Severity**: Minor
**Evidence Anchor**: table: Table 1 (§4.1), M, SD, Min, Max columns given with no per-measure N despite denominators of 142 for sessions, 87 for perceived control, and an unstated subsample for the final exam score
**Confidence**: 5 — the omitted column is plainly visible

Final exam score also appears as a "primary measure" here without being defined in §3.3.

### W23: Mediation is invoked without any mediation analysis
**Severity**: Minor
**Evidence Anchor**: text: §5 "It also complements accounts emphasizing perceived control as a mediating construct"
**Confidence**: 4 — no indirect-effect model appears in §3.4 or §4

Two cross-sectional associations measured on partly different subsamples cannot speak to mediation, and the causal ordering implied by the term is not testable in this design.
