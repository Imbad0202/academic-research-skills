## Scoring Plan Dissent

*(none required — omitted)*

Correction: per protocol I omit the section entirely rather than emit a placeholder. Disregard the heading above; the report proper begins here.

---

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor

score: block
block_class: fatal
trigger: "internally contradictory sample sizes or degrees of freedom that cannot be reconciled"

The manuscript reports degrees of freedom (156), group sizes (66 + 61 = 127), an analytic sample (142), and an item subsample (87) that cannot be simultaneously true of one dataset, and it reports two summary statistics (M = 3.847 at n = 87 on an integer 1–5 item; sample SD = 0.10 at n = 10, M = 3.00 on an integer 1–5 item) that no achievable response set can produce. Separately, the retention outcome is conditioned on partial survival by construction (mid-term recruitment, end-of-term outcome), and no ethics approval statement exists for trace data the manuscript states students were never told would be analysed.

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: block
block_class: repairable
trigger: "the headline conclusion is stated at a strength the presented evidence cannot sustain"

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

I read this manuscript twice: once as a reader, once with a calculator. The second reading is the one that determines my recommendation, and I want to be explicit about why, because the distinction I am drawing is not between a well-written and a badly written paper but between a paper whose reported numbers are recoverable and a paper whose reported numbers are not.

**The reported-statistics audit.** I recomputed every test statistic, *p*-value, and mean in the manuscript. Some pairs check out. The correlation in §4.2 is internally coherent: *r* = .24 at *n* = 142 gives *t* = 2.93 on 140 *df*, two-tailed *p* = .0040, exactly as reported. The perceived-control *t*/*p* pair in §4.3 is also coherent on its own terms: *t* = 3.02 at 156 *df* does yield *p* = .003. That internal coherence is diagnostically important, because it means these *p*-values were computed from real inputs rather than guessed — which in turn means the *df* of 156 was not a typographic ornament but reflects an *n* of 158 that appears nowhere in the manuscript. The perceived-control comparison can only have been run on the 87 students who answered the item (*df* = 85) or, if imputed somehow, on 142 (*df* = 140). Neither is 156. This is the single finding that most sharply separates "transcription slip" from "the analytic sample is not what §3.2 describes."

Three further checks fail outright. The abstract's *r* = .42 is not the *r* = .24 of §4.2; the abstract figure is the one readers and citers will carry away, and it is nearly double. The exam comparison reports *t*(140) = 1.31 with *p* = .008, but *t* = 1.31 at 140 *df* gives two-tailed *p* ≈ .19, and the surrounding prose simultaneously calls the difference "small" and says it "did not reach a comparable level" — so the *t*, the *p*, and the verbal gloss form a three-way contradiction in which no two members agree. Table 2's group sizes sum to 127 while the same paragraph asserts that "all 142 students" were classified and the *df* of 140 independently implies 142; fifteen cases are unaccounted for. A median split of 142 should also produce roughly 71/71, and ties at the median do not generate a 15-case shortfall.

Two reported values are not merely inconsistent but arithmetically unreachable. On an integer 1–5 item, 87 responses must sum to an integer; 334/87 = 3.839 and 335/87 = 3.851, so no achievable sum rounds to 3.847 (a GRIM failure). For the secondary clarity item, 10 integer responses with a mean of exactly 3.00 sum to 30, so the sum of squared deviations is a non-negative integer: zero (all threes, SD = 0) or at minimum two (one 2 and one 4), giving SD = √(2/9) ≈ 0.471. A sample SD of 0.10 lies in a gap that no response set occupies.

I also ran the cross-table reconciliation. Table 2's weighted group mean is (66 × 72.0 + 61 × 69.2)/127 = 70.66, against Table 1's full-sample 71.3. These can be reconciled arithmetically only if the fifteen unaccounted students averaged (142 × 71.3 − 8973.2)/15 ≈ 76.8 — above both reported groups and within the stated 32–98 range. So the gap is not impossible; it is informative. It tells us the missing cases are not a random slice, and it therefore contradicts the claim that all 142 were classified into engagement groups. I state this precisely because overclaiming here would be the wrong kind of rigor.

**On the direction of the errors.** My prior expectation was that every discrepancy would favour the hypothesis. On inspection that is true of three of them and not of the others, and I will not inflate the claim. The three directional errors — *r* .42 over .24, *p* .008 over .19, *df* 156 over 85 — all move in the direction of a stronger, larger, or better-powered finding, and none is explicable as the same slip twice. The GRIM failure and the 66/61 asymmetry are directionless; the abstract's .42 is, in isolation, consistent with a digit transposition of .24. What survives that discount is still decisive: a set in which three independent inflating errors coexist with two arithmetically impossible summaries cannot be adjudicated as careless transcription from the manuscript alone. It requires the underlying data, and the manuscript provides no data or code availability statement through which anyone could adjudicate it.

**Design.** Independent of the arithmetic, one design feature is fatal to the estimand as claimed. Recruitment occurred midway through the term; retention was measured at end of term. Students who had already withdrawn were structurally unable to enter the sample. The outcome variable is therefore conditioned on partial survival, the retention variable is truncated from below, and the engagement–retention association is distorted in a direction that cannot be signed without the full-cohort frame. No reanalysis of these 142 cases repairs this. Compounding it, §3.2 describes the sample as "a random sample of students enrolled in the course section" and then, two sentences later, as students who "chose to respond." These are not two descriptions of one procedure; they are two mutually exclusive procedures, and the recruitment narrative makes clear which one occurred. The response rate is never given against an enrollment of "several hundred," so the selection intensity is unmeasurable.

**Measurement and model.** A dichotomous retention outcome analysed by Pearson correlation with no covariates is below the field's minimum: logistic regression with prior achievement, credit load, and basic demographics is the floor, and without it the reported association is uninterpretable as anything other than a marginal contrast. The exposure variable is a platform-default 30-minute sessionization rule adopted without justification and conceded in §2 to conflate distinct engagement types, with no sensitivity analysis across alternative windows. A median split is applied to a distribution the paper itself calls right-skewed. Both focal constructs are single items with no reliability or validity evidence. Not one confidence interval appears anywhere, no effect size beyond *r* is reported, and the retention base rate is never stated — which matters concretely, because the ceiling on a point-biserial correlation depends on the outcome's marginal split. Finally, the abstract asserts that "self-regulated learning behavior" was measured; §3.3 contains no such measure, only one perceived-control rating.

**Ethics.** §3.2 states plainly that "Students were not informed that their dashboard activity data would be analyzed for this study," and the manuscript contains no IRB or ethics-committee approval statement, no waiver of consent, and no data-governance description. Consent is described only for the survey. I flag this as a gate rather than a limitation. It is not within a reviewer's remit to decide whether an approval exists; it is within a reviewer's remit to decline to certify a human-subjects analysis in which the disclosed consent does not cover the analysed data.

**Inferential warrant (D3).** The manuscript states its own standard and then fails it. §1 promises to "distinguish the pattern in the data from the causal story," §2 cites the audit literature on causal language outrunning correlational designs, and §3.1 concedes the cross-sectional constraint. §5 then opens with "dashboard engagement improved course retention" and asserts that "increasing dashboard engagement therefore raises the probability that a student completes the course"; §6 says engagement "is associated with, and raises," retention and calls institutional dashboard investment "a dependable strategy" and "generalizable" — from one section of one introductory statistics course, on a survivorship-conditioned sample, with no covariates. Two further coherence defects are local but load-bearing: a *p* = .008 result is narrated as not reaching a comparable level, and the perceived-control result is offered as evidence of a mediating construct when nothing mediational was estimated. I score this a block rather than a fatal because a correlational, single-site, hypothesis-generating paper is a coherent position the authors could actually defend; the defect is that they wrote a different paper in §§5–6 than the one their methods licence. Repairing it is a rewriting job, not a redesign — but it cannot be done until the numbers underneath it are known.

**What would change my assessment.** The analysis dataset and code, a per-analysis *n* table, the retention base rate, a full-cohort sampling frame that includes pre-recruitment withdrawals, a logistic model with covariates, intervals on every estimate, and documentation of ethics approval covering the log data. Short of the first and last of those, I do not think the reported results can be evaluated at all.

### S1: Operational definitions are specific enough to audit

The outcome coding resolves the ambiguous case explicitly rather than leaving it implicit, and the exposure definition names its sessionization rule. This precision is the reason an external reviewer can reconstruct the intended analysis and locate the inconsistencies at all; a vaguer Methods section would have concealed them.

**Evidence Anchor**: `text: §3.3 "Students who withdrew before the final assessment, or who were enrolled but did not sit the final, were coded as not retained."`

### S2: The manuscript names its own analytic compromises

§3.3 volunteers that the median split is a coarse simplification chosen for interpretability rather than efficiency, and §3.1 states the cross-sectional limit on inference. Self-disclosure of a known-suboptimal choice, in the Methods rather than buried in Limitations, is the correct practice and is credited here.

**Evidence Anchor**: `text: §3.3 "This median split is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency."`

### S3: The literature review contains the correct methodological self-critique

§2 anticipates both of the critiques that most threaten this design — that click-based proxies do not measure cognitive engagement, and that causal language in this literature outruns correlational evidence. The framework for a properly hedged paper is already present in the manuscript's own words.

**Evidence Anchor**: `text: §2 "click-based engagement metrics should be treated as rough indicators rather than as faithful measures of the cognitive engagement the theory implicates"`

### W1: The abstract's headline correlation is nearly double the value reported in Results

The abstract reports *r* = .42; §4.2 reports *r* = .24, *p* = .004. Only the second is internally consistent (*t* = 2.93, *df* = 140, *p* = .0040), so .42 is the unsupported figure and it occupies the most-read location in the paper. Taken alone this is consistent with a digit transposition, but a transposition in the abstract that doubles the effect is not a cosmetic error: it is the number that will be cited, and the Discussion's "modest size" framing cannot be evaluated until the authors state which value the analysis produced.

**Severity**: Critical
**Evidence Anchor**: `text: Abstract "Dashboard engagement correlated positively with retention (r = .42)" vs §4.2 "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"`
**Confidence**: 5 — direct recomputation of the correlation-to-*t* transform at the stated *n*.

### W2: The perceived-control *t*-test's degrees of freedom match no sample described in the manuscript

Only 87 students answered the perceived-control item, implying *df* = 85 for a two-group comparison; the full analytic sample of 142 would imply *df* = 140. The reported *df* = 156 implies *n* = 158, a figure that appears nowhere. Because *t* = 3.02 at *df* = 156 does yield exactly the reported *p* = .003, the *df* was used in an actual computation rather than mistyped in isolation, which means the sample this test was run on is not the sample §3.2 describes. One of the paper's two headline results rests on a test whose analytic sample cannot be identified.

**Severity**: Critical
**Evidence Anchor**: `text: §4.3 "t(156) = 3.02, p = .003"`
**Confidence**: 5 — statcheck-style recomputation plus arithmetic on the two candidate sample sizes.

### W3: The reported perceived-control mean is unreachable on the stated scale and sample (GRIM failure)

For an integer 1–5 item answered by 87 respondents, the response total must be an integer, so the mean must be a multiple of 1/87. The two nearest achievable values are 334/87 = 3.8391 and 335/87 = 3.8506; neither rounds to 3.847. The reported mean therefore cannot have been computed from 87 integer responses. Either the *n*, the scale, or the mean is misreported, and nothing in the manuscript allows a reader to determine which — this requires the underlying data, not a rewording. Three-decimal precision on a single-item ordinal measure is separately unjustified and is what made the inconsistency detectable.

**Severity**: Critical
**Evidence Anchor**: `table: Table 1, perceived-control row (M = 3.847, SD = 0.62), with n = 87 per §4.1`
**Confidence**: 5 — GRIM test is deterministic given an integer scale and a known *n*.

### W4: The retention outcome is conditioned on partial survival by design

Recruitment occurred midway through the term and the outcome was measured at term end, so students who withdrew before the recruitment window were structurally excluded from the sample. The analytic sample is thus a set of partial survivors, the retention variable is truncated from below, and the engagement–retention association is biased by an amount and in a direction that cannot be recovered from these data. This is not a limitation to be acknowledged; it means the reported estimand is not the one the paper claims to estimate, and no reanalysis of the 142 cases repairs it. A full-cohort frame including pre-recruitment withdrawals is required.

**Severity**: Critical
**Evidence Anchor**: `text: §3.2 "Midway through the term, an announcement was posted to the course LMS inviting students to complete a short survey"`
**Confidence**: 5 — selection-bias mechanism in learning-analytics trace samples is my primary specialization.

### W5: Trace data were analysed without notice to participants and with no ethics approval statement

The manuscript states that students were not informed their dashboard activity would be analysed, and describes consent only for the survey instrument. No IRB or ethics-committee approval, no consent waiver, and no data-governance provision appears anywhere. The analysed data are therefore human-subjects data whose disclosed consent does not cover the use made of them. I raise this at the highest band because it is a publication gate independent of the statistical findings: no amount of revision to the analysis resolves an absent authorisation, and a reviewer cannot certify the study without documentation that it existed.

**Severity**: Critical
**Evidence Anchor**: `text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."`
**Confidence**: 4 — the disclosure gap is explicit in the text; whether approval exists undocumented is outside my knowledge.

### W6: The set of discrepancies cannot be adjudicated as transcription error, and nothing is provided that would allow adjudication

Three of the discrepancies are directional and all three favour the hypothesis (*r* .42 over .24; *p* .008 over .19; *df* 156 over 85), and none is a repetition of a single slip. Two further reported values are arithmetically impossible rather than merely inconsistent. This combination is the signature that distinguishes careless proofreading from a reporting layer that does not correspond to an executed analysis. Deciding between those two accounts requires the analysis dataset, the per-analysis case counts, and the code — none of which the manuscript offers, and for which no availability statement or withholding rationale is given. I file this as a finding in its own right because its remedy differs from the individual corrections: the appropriate editorial action is a data request, not a list of errata.

**Severity**: Critical
**Evidence Anchor**: `absence: manuscript-wide reporting apparatus — expected a data or analysis-code availability statement permitting independent reconciliation of the reported statistics; checked §3.4, §4.1-4.3, Tables 1-2, and the end matter following §6`
**Confidence**: 4 — pattern-level inference from six verified recomputations; alternative benign explanations cannot be excluded without the data, which is precisely the point.

### W7: The exam comparison's *t*, *p*, and verbal interpretation are mutually incompatible

At *df* = 140, *t* = 1.31 gives two-tailed *p* ≈ .19, not the reported .008. The surrounding prose compounds this by describing the same result as "small" and as one that "did not reach a comparable level" while reporting a *p*-value well below the stated alpha of .05. No two of the three reported elements agree. Correcting to *p* ≈ .19 yields a null result, which is compatible with the verbal gloss but not with a *p* of .008 having been computed from this test.

**Severity**: Major
**Evidence Anchor**: `text: §4.3 "the difference was small, t(140) = 1.31, p = .008" and "did not reach a comparable level"`
**Confidence**: 5 — direct *p*-value recomputation at the reported *t* and *df*.

### W8: Table 2's group sizes contradict the stated analytic sample, the degrees of freedom, and median-split arithmetic

Table 2 reports 66 + 61 = 127 cases, while the same paragraph states that all 142 students were classified into engagement groups and the reported *df* = 140 independently implies *n* = 142. Fifteen cases are unaccounted for. A median split of 142 should also yield roughly 71/71; tie handling at the median cannot produce a 15-case shortfall. The cross-table check is informative rather than merely inconsistent: Table 2's weighted mean is 70.66 against Table 1's 71.3, which reconciles only if the fifteen missing students averaged ≈76.8, above both reported groups. That is arithmetically possible but implies the excluded cases are systematically higher-scoring, which directly contradicts the claim that all 142 were classified. The analytic sample for this comparison must be re-derived from the data.

**Severity**: Major
**Evidence Anchor**: `table: Table 2, group n column (66 and 61, summing to 127)`
**Confidence**: 5 — arithmetic on reported cell values and the reported *df*.

### W9: The secondary clarity item's reported SD is arithmetically impossible

With 10 integer responses on a 1–5 scale and a mean of exactly 3.00, the response total is 30 and the sum of squared deviations from 3 is a non-negative integer. Zero gives SD = 0 (all threes); the smallest nonzero value is 2 (one 2 and one 4), giving sample SD = √(2/9) ≈ 0.471. A sample SD of 0.10 falls in a gap no response set occupies, and the population-SD reading fails for the same reason. As with W3, the discrepancy cannot be repaired by editing because it is a statement about which datasets exist, and no inference in the paper rests on this item — which makes the error harder, not easier, to explain away as motivated.

**Severity**: Major
**Evidence Anchor**: `text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"`
**Confidence**: 5 — GRIMMER-style deterministic check on integer response sets.

### W10: The sampling description is self-contradictory and the response rate is never reported

§3.2 first describes the participants as drawn "using a random sample of students enrolled in the course section" and then, two sentences later, as those who "chose to respond," with non-responders excluded. These are incompatible procedures, not two descriptions of one; the recruitment narrative establishes that the study is a voluntary-response convenience sample, and the word "random" should be removed. Because enrollment is given only as "several hundred," the response rate — and therefore the strength of the volunteer selection — cannot be estimated by a reader. Every generalisation in §§5–6 depends on which of these two descriptions is true.

**Severity**: Major
**Evidence Anchor**: `text: §3.2 "a random sample of students enrolled in the course section" and "Students who chose to respond, and who consented to the survey, formed the study sample"`
**Confidence**: 5 — the contradiction is on the surface of the text.

### W11: A dichotomous outcome is analysed by correlation with no covariates and no adjusted model

§3.4 states that associations were assessed with Pearson correlations "between continuous measures," but retention is explicitly dichotomous, so the headline analysis is a point-biserial contrast presented as a product-moment correlation. More consequentially, no covariates appear anywhere: no prior achievement, no credit load, no demographics. Logistic regression with those adjustments is the minimum defensible specification for a binary persistence outcome in observational LMS data, and without it the reported association carries no discriminating information about engagement as distinct from general academic propensity. The median split compounds this by discarding variance from a distribution the paper itself describes as right-skewed.

**Severity**: Major
**Evidence Anchor**: `text: §3.4 "Associations between continuous measures were assessed with Pearson correlations."`
**Confidence**: 5 — standard modelling requirement for binary outcomes in observational educational data.

### W12: No confidence intervals or effect sizes appear anywhere in the manuscript

Every result is reported as a point estimate with a *p*-value. There is no interval on the focal correlation, no standardised mean difference for either group comparison, and no precision statement of any kind. For *r* = .24 at *n* = 142 the 95% interval runs roughly .08 to .39, which spans effects the Discussion would have to characterise very differently. Because the Discussion's central hedge is explicitly about magnitude ("the modest size of the engagement-retention association"), the absence of any precision estimate leaves the paper's own calibration claim unverifiable.

**Severity**: Major
**Evidence Anchor**: `absence: §4.2-4.3 with §3.4 — expected confidence intervals and at least one effect size beyond r for the correlation and both t-tests; checked §3.4 analysis plan, §4.1 descriptives, §4.2, §4.3, and Tables 1 and 2`
**Confidence**: 5 — exhaustive reading of the Results and analysis sections.

### W13: The retention base rate is never reported

Retention is the study's outcome, yet neither the count nor the proportion of retained students appears anywhere. This is not a completeness quibble: the attainable magnitude of a point-biserial correlation is bounded by the outcome's marginal split, so *r* = .24 cannot be interpreted, benchmarked, or compared with the literature without it. The base rate is also the quantity a reader needs to judge whether the survivorship conditioning in W4 has already truncated most of the outcome variance.

**Severity**: Major
**Evidence Anchor**: `absence: §4 Results — expected the retention base rate as counts and proportion for the 142-case analytic sample; checked §3.3 outcome definition, §4.1 descriptives, Table 1, and the §4.2 correlation report`
**Confidence**: 5 — the quantity is definitionally required to interpret the reported statistic.

### W14: The exposure variable rests on an unjustified platform default with no sensitivity analysis

Dashboard sessions are defined by a 30-minute inactivity threshold adopted because it is the platform's default. No rationale connects that window to any theory of dashboard consultation, and no sensitivity analysis shows whether the correlation, the median split, or the group assignment survive alternative windows. §2 concedes that such counts conflate a student who opens the dashboard once and studies it with one who opens it repeatedly without reflection. Since this measure is the independent variable in the paper's core claim and the basis of every group assignment, its robustness is not optional.

**Severity**: Major
**Evidence Anchor**: `text: §3.3 "following the platform's default sessionization rule"`
**Confidence**: 4 — the definitional gap is explicit; the magnitude of its influence is unknowable without the data.

### W15: The abstract claims a self-regulated learning behavioural measure that the Methods do not contain

The abstract states that dashboard engagement, "self-regulated learning behavior," and course persistence were measured. §3.3 lists three instruments: a session count, a dichotomous retention code, and one perceived-control rating. No behavioural SRL measure exists — no strategy inventory, no help-seeking or planning trace, nothing operationalising the forethought/monitoring cycle the Introduction builds on. A single perceived-control item is a subjective appraisal, not a behavioural measure of regulation, and the SRL framing carries much of the paper's theoretical contribution.

**Severity**: Major
**Evidence Anchor**: `absence: §3.3 Measures — expected an operational self-regulated learning behavioural measure matching the abstract's claim; checked §3.3 measure list, §3.4 analysis plan, Table 1 rows, and §4.1-4.3`
**Confidence**: 5 — direct comparison of abstract claims against the enumerated measures.

### W16: Both focal constructs are single items with no reliability or validity evidence

Perceived control and interface clarity are each measured by one item, and the justification offered is prevalence and survey burden rather than psychometric adequacy. Internal consistency is undefined for a single item, and no convergent, discriminant, or criterion evidence is offered from this sample or any other. One of the two claims in the abstract rests entirely on such an item, so its measurement properties are load-bearing: without validity evidence, the group difference in §4.3 cannot be attributed to perceived control rather than to acquiescence, item interpretation, or mood at the time of the survey.

**Severity**: Major
**Evidence Anchor**: `text: §3.3 "single-item overall ratings are common in dashboard studies to limit survey burden"`
**Confidence**: 5 — measurement-validation standards for latent constructs in educational research.

### W17: Table 1 mixes subsamples without reporting per-measure *n*

Table 1 is titled as descriptives for the primary measures and lists session counts, perceived control, and final exam score in one block with no *n* column, although perceived control comes from 87 respondents and the other two from 142. A reader cannot tell from the table which rows describe which sample, which is exactly the ambiguity that makes W2, W3, and W8 hard to diagnose. Reporting *n* per row, and reducing the perceived-control mean to a precision the ordinal scale supports, would cost nothing and prevent the confusion.

**Severity**: Minor
**Evidence Anchor**: `absence: Table 1 — expected a per-measure n column separating the 142-case log sample from the 87-case item subsample; checked Table 1 header, §3.2 sampling text, and the §4.1 narrative`
**Confidence**: 5 — the table's columns are visible and contain no *n*.
