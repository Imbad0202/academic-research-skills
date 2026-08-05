## Dimension Scores

contract_role: domain

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
trigger: "a cited work whose findings are materially misrepresented in support of a key claim"
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

I read this manuscript as a persistence researcher, and the domain problem is not subtle: the paper's dependent variable is called retention, but the persistence literature that defines and theorises retention is entirely absent, and the one place where the paper does lean on a specific empirical source, it appears to have inverted that source.

The inversion is the sharpest domain error. §2 asserts that dashboards "have been shown to reliably improve outcomes for lower-achieving students" and attributes this to Ferro & Nakamura (2021), whose listed title is "When dashboards demotivate: Peer comparison and the lower-achieving student." A title is not a finding, but a paper announcing demotivation of lower-achieving students under peer comparison is not plausibly the warrant for a claim that dashboards reliably improve outcomes for that same subgroup. The manuscript then builds on the misattribution twice: it states the claim "underpins much of the equity-oriented rationale for institutional dashboard deployment," promises to return to it in the Discussion, and in §5 reports that "our finding that engagement tracks retention aligns with the view that externalized progress cues can support persistence." The paper's positioning against the literature therefore rests on a claim its own reference list contradicts. Compounding the oddity, the very next paragraph of §2 correctly reports the demotivation strand via Osei (2020), so the manuscript states both the finding and its opposite within a page without noticing. This is repairable — correct the attribution, and the paragraph becomes a straightforward account of a genuinely contested question — but it is load-bearing as written.

On the construct: the paper measures whether a student remained enrolled and sat one final assessment in one introductory statistics course, in one term. That is course completion, and at best it is course completion in a single gateway setting. The Conclusion converts it into an institution-level, cross-disciplinary, worldwide claim. Those are different variables, and the distinction is not pedantry in this field — course-level completion and institutional persistence dissociate routinely, since students who fail or abandon a gateway course often persist at the institution, and students who complete it often leave for reasons the course never touched. A gateway-attrition study can be valuable precisely because it isolates a course-level mechanism; this one forfeits that value by claiming the institutional outcome it did not measure.

The retention variable also collapses two non-completion pathways that the field treats separately. Formal withdrawal before the final and being enrolled but absent from the final have different antecedents (registrar deadlines, financial and external shocks, and strategic GPA protection on one side; academic disengagement and, frequently, an already-unrecoverable grade on the other) and different institutional remedies (advising and withdrawal-policy design versus early alert and outreach). Merging them into a single dichotomy guarantees that whatever association the study finds cannot be mapped onto any actionable institutional response, which is exactly what §6 promises to deliver. A withdrawal is also arguably a censoring event rather than an outcome failure, and the paper does not engage that choice.

The rival explanation the persistence literature would raise first is never named. Students with higher prior attainment, stronger conscientiousness, and an already-settled intention to persist both click more and finish more; a modest positive correlation between dashboard sessions and completion is the expected signature of that selection, with or without any dashboard effect. The manuscript reports no covariates, no prior-attainment control, and no stratification, and §5.1 does not list confounding among its limitations. Without that account addressed, §5's mediation-flavoured reading — that perceived control is the construct linking use to persistence — has no support whatsoever; a cross-sectional group difference on a single item, measured mid-term among volunteers, is equally consistent with confident students reporting confidence.

This connects to the contribution question. Wexler & Ojo (2020), "Retention modeling with LMS trace data: A cautionary study," is in the reference list and never cited. So is Halloran (2020), a review of gateway-course retention interventions, and Solberg & Whitfield (2018) on institutional deployment. Nine of fifteen listed references are never cited, and the three uncited ones most relevant to the dependent variable are precisely the ones that would have constrained the paper's claims. As it stands I cannot identify what a persistence reader learns here that the cautionary trace-data work did not already establish, and the authors have not attempted the comparison. The paper also cites Ibarra (2023) on causal language outrunning correlational evidence, positions itself in §1 as careful on exactly that point, and then in §5 and §6 asserts that engagement "improved" retention and "raises" completion probability. Misrepresenting one's own relationship to a cited critique is a literature-accuracy failure as much as a coherence one.

Two arithmetic matters bear on domain accuracy without being my lane to score. The abstract reports r = .42 for the engagement–retention association and §4.2 reports r = .24; these are not the same finding, and .42 is the number that will be extracted into future reviews and meta-analyses. Separately, the reported test statistics do not cohere with the stated samples (a perceived-control comparison on df = 156 when 87 respondents answered the item; t(140) = 1.31 paired with p = .008; Table 2 group sizes summing to 127 against a stated 142). I leave the statistical adjudication to the methodology seat, but I note that a reader cannot presently determine which reported quantity is the study's result, and that the direction of the substantive interpretation in §5 ("the exam-performance comparison was weaker still") is not recoverable from the numbers as printed.

Repair is possible without new data collection: correct the Ferro & Nakamura attribution and rewrite the "who benefits" paragraph around the actual contested evidence; retitle and re-describe the outcome as final-assessment completion in a single gateway course; disaggregate withdrawal from non-sitting and report both; situate the study in the persistence and early-alert literatures already sitting in the reference list; add prior-attainment and other available covariates, or explicitly frame the association as confounded; and strike every institutional, worldwide, and cross-disciplinary claim from §6. That is substantial work on the framing and the analysis, but it is revision, not a new study — hence repairable rather than fatal.

### S1: Accurate and correctly attributed treatment of click-based engagement proxies
The manuscript's account of behavioural-proxy limitations is faithful to the source it cites and to the field's current position, and it is carried through consistently into §3.3's operationalisation note and §5.1's first limitation rather than being stated and abandoned.
**Evidence Anchor**: text: §2, "click-based engagement metrics should be treated as rough indicators rather than as faithful measures of the cognitive engagement the theory implicates"
**Confidence**: 5 — I review dashboard trace-measurement claims routinely.

### S2: Correct characterisation of the dashboard evidence base as thin relative to its promotion
The framing that outcome evidence lags adoption and satisfaction reporting is an accurate reading of this literature and is the right entry point for a study of downstream outcomes.
**Evidence Anchor**: text: §1, "an empirical question that has attracted more enthusiasm than evidence"
**Confidence**: 5 — this matches my own reading of the published base.

### S3: Design details relevant to the demotivation literature are reported plainly
Reporting that the dashboard included a peer-comparison band and was universally available without opt-in is exactly the information a persistence reader needs to connect this deployment to the relative-standing feedback strand, and it is reported without spin.
**Evidence Anchor**: text: §3.1, "a peer-comparison band" and "available to all enrolled students from the first week of the term and required no separate opt-in"
**Confidence**: 4 — interface instrumentation detail is not my strongest area.

### W1: Cited source appears inverted, and the inverted claim is load-bearing for the paper's positioning
§2 attributes to Ferro & Nakamura (2021) a claim that dashboards reliably improve outcomes for lower-achieving students, while the listed title of that source announces demotivation of lower-achieving students under peer comparison. The manuscript then makes this claim the equity rationale it "returns to in the Discussion," and §5 reports alignment with it. Either the attribution is wrong or the source's findings are materially misrepresented; in either case the paper's stated relationship to the literature is false, and the misstatement sits directly under a core interpretive claim.
**Severity**: Critical
**Evidence Anchor**: text: §2 vs. References, "Dashboards have been shown to reliably improve outcomes for lower-achieving students" and "When dashboards demotivate: Peer comparison and the lower-achieving student"
**Confidence**: 4 — I know this strand of the dashboard literature well, though I cannot verify the source text itself from the manuscript alone.

### W2: Conclusion claims an institution-level, cross-disciplinary, worldwide outcome the study did not measure
The measured outcome is completion of one final assessment in one introductory statistics course in one term. §6 converts this into a "dependable strategy for improving retention across programs and disciplines" for "higher education institutions worldwide." Course completion and institutional persistence are distinct outcomes that dissociate routinely, and a single-course correlational result licenses neither the level nor the scope nor the dependability claimed. §3.1's appeal to "disciplinary breadth even within one course" describes a mixed-major enrolment, not variation in programme, course design, or dashboard deployment. Uncorrected, the paper's headline implication is false as stated.
**Severity**: Critical
**Evidence Anchor**: text: §6, "For higher education institutions worldwide, the implication is clear" and "is a dependable strategy for improving retention across programs and disciplines"
**Confidence**: 5 — the course-completion/institutional-persistence distinction is my primary research area.

### W3: Withdrawal and enrolled-but-absent are collapsed into a single non-retention category
§3.3 codes formal withdrawal before the final and enrolment without sitting the final as the same outcome. These pathways have different antecedents and different institutional remedies, and withdrawal is arguably a censoring event rather than a failure. Merging them makes the dependent variable uninterpretable for the practical purpose the paper claims, since no dashboard-related recommendation can be aimed at a category that mixes registrar-timed exits with mid-term disengagement. Disaggregating and reporting both, plus base rates, is required.
**Severity**: Major
**Evidence Anchor**: text: §3.3, "Students who withdrew before the final assessment, or who were enrolled but did not sit the final, were coded as not retained."
**Confidence**: 5 — outcome coding of course-level non-completion is squarely my area.

### W4: No engagement with retention or persistence theory despite retention being the dependent variable
The paper theorises only self-regulated learning and cites nothing from the persistence, integration, institutional-commitment, or early-alert literatures. §1 asserts gateway-course risk without citation. Three listed references bearing directly on the outcome — a gateway-retention intervention review, an institutional-deployment study, and a cautionary trace-data retention-modelling study — are never cited, as are six others. The consequence is not decorative: without that literature the paper cannot say what mechanism it expects, what baseline attrition looks like, or what the observed association would need to survive to be informative.
**Severity**: Major
**Evidence Anchor**: absence: §1-§2 and reference list - expected substantive engagement with student-persistence theory and gateway-course retention evidence, including the listed but uncited Halloran (2020) and Wexler & Ojo (2020); checked Introduction, Literature Review, Discussion, Limitations, and every in-text citation against the 15-item reference list
**Confidence**: 5 — I can enumerate what a retention-outcome paper is expected to engage.

### W5: Leading rival explanation never named, tested, or adjusted for
That already-persisting, higher-prior-attainment, more conscientious students both click more and complete more is the default account of a modest positive engagement–completion correlation, and it is the account the cited-but-unused cautionary trace-data literature exists to press. The manuscript reports no covariates, no prior-attainment adjustment, and no stratification, and §5.1 omits confounding entirely. Consequently §5's reading of perceived control as a mediating construct is unsupported: a cross-sectional single-item group difference among volunteers is equally consistent with pre-existing confidence. Either adjust with available administrative covariates or drop the mediation framing.
**Severity**: Major
**Evidence Anchor**: absence: §3.4 and §5 - expected identification of the prior-attainment and conscientiousness selection account with covariate adjustment or stratification reported; checked Design, Participants, Measures, Analysis, Results, Discussion, and Limitations for any named alternative explanation
**Confidence**: 5 — selection into trace-data engagement measures is a standing concern in this literature.

### W6: Two different values reported for the study's headline association
The Abstract reports r = .42 and §4.2 reports r = .24 for the same engagement–retention association. These carry materially different interpretations, and the larger figure is the one that will be extracted by readers and downstream reviews. Whichever is correct, the manuscript currently enters an unresolved discrepancy into the domain record, and §5's "modest" characterisation is consistent with only one of them.
**Severity**: Major
**Evidence Anchor**: text: Abstract and §4.2, "Dashboard engagement correlated positively with retention (r = .42)" and "positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — the discrepancy is directly readable from the manuscript.

### W7: Goal-orientation moderation attributed to the wrong listed source
§2 attributes the framing- and goal-orientation-dependence of dashboard effects, plus the performance-avoidance mechanism, to Osei (2020), whose listed title concerns discouragement effects of relative-standing feedback. Berange (2021), listed as "Goal orientation and dashboard response in introductory courses," is never cited. The substantive point survives, but the attribution is imprecise and the apparently correct source goes unused.
**Severity**: Minor
**Evidence Anchor**: text: §2 vs. References, "the direction of the effect appears to depend on framing and on individual differences in goal orientation (Osei, 2020)" and "Goal orientation and dashboard response in introductory courses"
**Confidence**: 4 — inference from listed titles rather than source texts.

### W8: Uncited normative claim used to justify a measurement choice
§3.3 defends the single-item perceived-control measure by asserting that such items are common in dashboard studies to limit survey burden. No source is given, and the claim about field practice is doing justificatory work. Either cite it or defend the choice on its own terms.
**Severity**: Minor
**Evidence Anchor**: text: §3.3, "single-item overall ratings are common in dashboard studies to limit survey burden"
**Confidence**: 3 — single-item measurement psychometrics is not my specialism.

### W9: Paper positions itself against causal overreach and then commits it
§1 promises to distinguish pattern from causal story, and §2 cites an audit of causal language in correlational learning analytics. §5 then reports that engagement "improved" retention and that increasing engagement "raises" completion probability, and §6 repeats the causal reading. This misrepresents the paper's own stated relationship to the critique it cites and, in a field where that critique is well established, converts a cited caution into an illustration of the problem. The Discussion and Conclusion require rewriting to associational language throughout.
**Severity**: Major
**Evidence Anchor**: text: §1 and §5, "We are careful throughout to distinguish the pattern in the data from the causal story that might explain it" and "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course"
**Confidence**: 5 — the internal mismatch is directly readable and the cited critique is well known to me.
