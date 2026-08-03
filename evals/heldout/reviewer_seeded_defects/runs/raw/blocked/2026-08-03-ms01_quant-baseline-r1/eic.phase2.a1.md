contract_role: eic

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: block
trigger: "figures/tables that contradict or are unsupported by the text"

The presentation defect here is not stylistic. Table 2 reports group sizes summing to 127 while the adjacent text asserts that all 142 students were classified into those groups and reports a test with 140 degrees of freedom; the Abstract's headline correlation (.42) is not the correlation in §4.2 (.24); the perceived-control comparison carries more degrees of freedom (156) than the study has participants (142) or item-respondents (87); and one reported *t*/*p* pair (1.31 with p = .008) cannot co-occur. A reader cannot determine from this manuscript what the sample was, how large the reported effect is, or which comparisons were significant. That is reconstruction failure, not copyediting.

### D6: venue_fit_and_contribution
score: block
block_class: repairable
trigger: "reports a single local deployment with no generalisable insight or transferable design lesson"

The topic sits squarely inside this venue's remit; the problem is what the manuscript adds. Stripped of the numbers that contradict each other, the contribution is one association between dashboard session counts and course completion in one section of one course in one term, with no exposure-time adjustment, no described dashboard artifact, and no design lesson a reader at another institution could carry away. The manuscript's own diagnosis of the field — that published work reports "adoption metrics or student satisfaction rather than downstream academic outcomes" — is the category it claims to escape by measuring an outcome; but an outcome association that may be produced mechanically by differential exposure is not evidence about the outcome. I score this repairable rather than fatal because the remedy is a re-analysis of data the authors already hold, not a different study.

## Review Body

I am reviewing this as an editorial-fit and presentation judgement, and I am confining my scores to the two dimensions I own. Study design and statistical practice (D1), the accuracy of the literature characterisation (D2), the argument's internal logic (D3), and adjacent-field accessibility (D4) belong to other seats; where my findings touch their territory I flag the overlap rather than claim the call.

**Triage recommendation.** This manuscript is not revisable at this venue in its present state, and I do not think it is revisable at a lower tier either, because the defect that matters most is not in the writing — it is that the headline association has an untested mechanical explanation. Students who withdrew mid-term had fewer weeks in which to open the dashboard. Session counts and retention would then covary with no behavioural effect whatsoever. Until the authors re-analyse with exposure held constant — a time-at-risk model, or session counts restricted to a window every student survived — there is no finding to place anywhere, at any tier. My routing recommendation is therefore: return to the data first. If the exposure-adjusted association holds, the natural home is a short empirical report making a strictly local, strictly correlational claim, with the dashboard artifact specified well enough to replicate. If it does not hold, the interesting paper is a different one: a measurement-critique piece showing how exposure time inflates dashboard-outcome associations in the deployed literature. That paper would be a genuine contribution to this readership. The present one is not.

**Fit is entangled with claim discipline.** The Introduction promises to "distinguish the pattern in the data from the causal story," §2 cites an audit of causal overreach in correlational learning analytics, and then §5 opens with "dashboard engagement improved course retention" and §6 tells institutions worldwide that dashboards are a "dependable strategy." A venue whose corpus includes the critique cannot publish an unreconstructed instance of it. This is not only a wording problem: the causal and global claims are what make the contribution look large, and once they are withdrawn the manuscript's own scope statement (single course, single term, single interface) is what remains. The DA seat owns the coherence judgement; my point is the editorial one — the contribution that survives honest wording is not the contribution the manuscript is selling.

**On the survey component.** The manuscript describes itself as combining logs and self-report. The self-report is one item on a 1–5 scale, plus a second single item administered to ten students and reported descriptively. That does not constitute a survey component in the sense the framing implies, and it does not license the "regulatory experience" language in §1. I record this as part of the contribution assessment rather than as a separate finding.

**On research ethics — explicitly not a compliance checkbox.** §3.2 states that "Students were not informed that their dashboard activity data would be analyzed for this study," and no ethics-approval or consent-basis statement appears anywhere in the manuscript. Editorial habit treats this as paperwork to be cleared after acceptance. I do not treat it that way here, and I ask the synthesiser not to let my seat's reporting-level framing (W9) dilute the ethics reviewer's substantive objection. If a colleague on this panel judges the unconsented secondary use of trace data to be independently disqualifying, my repairable classification on D6 should not be read as tension with that judgement — it addresses contribution, not ethics.

**Two matters I am flagging for other seats rather than scoring.** First, §2 attributes to Ferro & Nakamura (2021) the claim that dashboards "reliably improve outcomes for lower-achieving students," while the cited work's title is *When dashboards demotivate: Peer comparison and the lower-achieving student*. If that citation is being used against its own finding, it is a domain-accuracy defect of consequence. Second, a Pearson correlation between a session count and a dichotomous retention outcome is a point-biserial coefficient, and the manuscript neither says so nor reports the corresponding effect-size interpretation; that is the methodology seat's call.

### S1: The literature review supplies the standard by which the paper should be judged
§2 states the field's two central weaknesses plainly — that click-based engagement metrics are rough proxies rather than measures of cognitive engagement, and that causal language in this literature outruns the evidence. This is unusually candid framing for a dashboard submission, it is correctly organised around competing positions rather than a citation parade, and it is the strongest writing in the manuscript.
**Evidence Anchor**: text: §2 "several reviewers have noted that causal language frequently outruns the evidence (Ibarra, 2023)"

### S2: Methods disclose inconvenient design choices instead of burying them
The median split is labelled as a coarse simplification adopted for interpretability rather than efficiency; the sessionisation rule is stated; the cross-sectional restriction is stated twice; and the non-notification of students is disclosed. This candour is what makes the manuscript reviewable at all, and it should be preserved in any revision.
**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure"

### S3: Structural conventions are observed
Numbered IMRaD sectioning, keywords, a dedicated limitations subsection that names real limitations rather than decorative ones, and a consistently formatted reference list with DOIs. The scaffolding a reader needs to navigate the paper is in place; the failures below are in what the scaffolding holds.
**Evidence Anchor**: text: §5.1 "Several limitations qualify these findings."

### W1: Differential exposure time is never eliminated as the explanation for the entire headline association
Retention is coded on completion of the final assessment; dashboard engagement is a count accumulated across the term. Students who withdrew therefore had systematically fewer weeks in which to accumulate sessions. This mechanism alone generates a positive session-count/completion association with no behavioural effect. The manuscript contains no exposure-adjusted model, no restriction of the accumulation window, no time-to-withdrawal analysis, and no mention of the problem in the limitations. Uncorrected, this defect does not weaken the core claim — it removes the basis for it, and with it the contribution on which venue fit rests.
**Severity**: Critical
**Evidence Anchor**: absence: §3.3 Measures and §5.1 Limitations — expected an exposure-adjusted treatment of session counts (time-at-risk model or a pre-withdrawal accumulation window); checked §3.3, §3.4 Analysis, §4.2 Results, §5 Discussion, §5.1 Limitations
**Confidence**: 5 — I have handled roughly 200 dashboard submissions and this is the field's most common artifact-for-finding substitution.

### W2: The Abstract's headline correlation is not the correlation the Results report
The Abstract reports r = .42; §4.2 reports r = .24 with p = .004. The two cannot both describe the same analysis: with N = 142, r = .42 would carry p < .001, so the Abstract's coefficient is inconsistent even with the p-value the manuscript reports. The abstract is the only part of this paper most readers will see, and it currently overstates the study's central quantity by roughly a factor of two. No editor can forward a manuscript whose headline number and result section disagree, and only the authors can say which is true.
**Severity**: Critical
**Evidence Anchor**: text: Abstract "Dashboard engagement correlated positively with retention (r = .42)"
**Confidence**: 5 — direct comparison of two stated values in the same manuscript.

### W3: Causal claims are asserted in the same manuscript that promises correlational discipline
§1 undertakes to "distinguish the pattern in the data from the causal story"; §5 then states as its central finding that "dashboard engagement improved course retention" and that increasing engagement "raises the probability" of completion; §6 repeats "is associated with, and raises." The design is observational and cross-sectional by the authors' own §3.1. Repairing this requires rewriting the Discussion, Conclusion, and Abstract around a claim the design supports — substantial rewriting, and one that visibly shrinks the stated contribution. For this venue specifically, publishing an uncorrected instance of the error its own cited corpus audits is not available.
**Severity**: Major
**Evidence Anchor**: text: §5 "dashboard engagement improved course retention"
**Confidence**: 5 — the design statement and the causal claim are both explicit in the manuscript.

### W4: Global, prescriptive generalisation from one course section, contradicting the manuscript's own limitations
§5.1 concedes the single-course setting and that the specific interface may shape responses. §6 then tells "higher education institutions worldwide" that dashboard investment is a "dependable strategy" and a "generalizable lever." One section, one term, one interface, 142 students, and a modest association cannot support a dependability claim at that scope, and the Conclusion contradicts the Limitations two pages earlier. This is the significance-outruns-scope problem in its strongest form and requires the Conclusion to be rewritten from scratch.
**Severity**: Major
**Evidence Anchor**: text: §6 "investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy for improving retention across programs and disciplines"
**Confidence**: 5 — scope of the design and scope of the claim are both stated explicitly.

### W5: The perceived-control comparison reports more degrees of freedom than the study has participants
§4.3 reports t(156) = 3.02 for the high- versus low-engagement comparison on perceived control. Degrees of freedom of 156 imply N = 158. The primary analytic sample is 142, and only 87 respondents answered the perceived-control item, which is the relevant denominator. The reported test cannot have been computed on the described sample. Resolving this requires the authors to return to the analysis, not to amend the text.
**Severity**: Major
**Evidence Anchor**: text: §4.3 "t(156) = 3.02, p = .003"
**Confidence**: 5 — arithmetic comparison against the sample sizes the manuscript states.

### W6: Table 2's group sizes contradict the sample the text says was classified
Table 2 reports n = 66 and n = 61, summing to 127. The immediately preceding sentence states that all 142 students in the primary analytic sample were classified into engagement groups for this comparison, and the reported test carries 140 degrees of freedom, implying N = 142. Fifteen students are unaccounted for, with no exclusion rule given. A reader cannot tell whether Table 2 describes the analysis reported beside it.
**Severity**: Major
**Evidence Anchor**: table: Table 2 rows "High engagement" (n = 66) and "Low engagement" (n = 61)
**Confidence**: 5 — arithmetic comparison of the table against adjacent text.

### W7: The exam comparison's reported statistic, p-value, and verbal interpretation are mutually incompatible
§4.3 reports t(140) = 1.31 with p = .008 and describes the difference as small and as not reaching a comparable level. A t of 1.31 on 140 degrees of freedom corresponds to p ≈ .19, not .008; and p = .008 would be significant at the stated alpha of .05, contradicting the verbal gloss. One of the three — statistic, p-value, or interpretation — is wrong, and the manuscript gives the reader no way to tell which. The Discussion's claim that "the exam-performance comparison was weaker still" rests on this unresolved reporting.
**Severity**: Major
**Evidence Anchor**: text: §4.3 "the difference was small, t(140) = 1.31, p = .008"
**Confidence**: 5 — standard t-distribution reference against the stated alpha.

### W8: The sampling description contradicts itself within a single subsection
§3.2 first states that participants were drawn "using a random sample of students enrolled in the course section," then describes recruitment as a mid-term LMS announcement to which students chose to respond, with non-responders excluded, and concludes that the sample "reflects those who volunteered during the recruitment window." A volunteer sample is not a random sample. As written, a reader cannot determine the sample's provenance, which is the precondition for judging every result in §4. I report this as a reporting contradiction within my remit; its consequences for inference belong to the methodology seat.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "using a random sample of students enrolled in the course section"
**Confidence**: 5 — both descriptions appear in the same subsection.

### W9: No ethics-approval statement or consent basis for the trace-data analysis, alongside disclosed non-notification
The manuscript states that students were not informed their dashboard activity would be analysed for this study, and nowhere reports ethics or IRB approval, an approval identifier, a waiver, or the LMS terms under which secondary use of trace data was permissible. Survey consent is mentioned; log-data consent is not. At a venue in this community, that absence must be resolved before review can proceed, and the disclosed non-notification suggests the underlying issue is not merely an unwritten paragraph. I band this from my seat's reporting perspective; the ethics reviewer's substantive assessment may well be more severe, and should not be reduced to my framing.
**Severity**: Major
**Evidence Anchor**: absence: manuscript-wide — expected an ethics-approval/IRB statement and a stated consent basis for secondary use of dashboard trace data; checked §3.1, §3.2, §3.4, §5.1, and the front matter
**Confidence**: 4 — I can verify the absence in the manuscript, but not whether approval exists off-page.

### W10: A reported secondary-item standard deviation is arithmetically impossible for the described instrument
§4.1 reports N = 10, M = 3.00, SD = 0.10 on an integer 1–5 scale. Ten integer responses averaging exactly 3.00 either are all 3s, giving SD = 0, or contain at least one deviation of 1, giving SD of roughly 0.32 or more. SD = 0.10 cannot arise. Either the response scale, the sample size, or the statistic is misreported. The item bears no analytic weight, but the impossibility cannot be fixed by deleting it: it indicates reported values were not checked against source data, and verifying it requires returning to that data.
**Severity**: Major
**Evidence Anchor**: text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Confidence**: 4 — arithmetic bound on integer-scale dispersion; assumes the stated scale and N are as written.

### W11: Table 1 omits the outcome variable, includes an undefined measure, and mixes reporting precision
Table 1 is titled "Descriptive statistics for primary measures" but does not report course retention, the study's dependent variable, and does report final exam score, which §3.3 never defines as a measure or explains how it was obtained. Perceived control is given to three decimals (3.847) while its SD is given to two (0.62), and the same three-decimal value recurs in §4.1. Corrected, this changes no claim; uncorrected, the table does not do the job its caption assigns it.
**Severity**: Minor
**Evidence Anchor**: table: Table 1 rows "Perceived control (1-5)" and "Final exam score (0-100)"
**Confidence**: 5 — direct inspection of the table against §3.3.

### W12: The dashboard itself is never specified, so no transferable design lesson is available
The intervention artifact is described in one clause: engagement metrics, assignment progress, and a peer-comparison band. There is no figure or screenshot, no account of what the peer band displayed or how it was computed, no statement of update frequency or default landing view, and no notification or prompting regime. §5.1 concedes that interface features may shape responses, which makes the omission decisive: a reader at another institution cannot tell what was deployed, cannot replicate it, and cannot extract a design implication despite §6 promising implications for instructional design. For a dashboard venue, this alone leaves the contribution non-transferable.
**Severity**: Major
**Evidence Anchor**: text: §3.1 "a student-facing learning analytics dashboard displaying engagement metrics, assignment progress, and a peer-comparison band"
**Confidence**: 5 — the quoted clause is the manuscript's complete description of the artifact.

### W13: Nine of fifteen reference-list entries are never cited in the text
Ainsworth & Devi (2018), Berange (2021), Delacroix & Ohno (2022), Halloran (2020), Kessler & Amadou (2019), Montez (2022), Prakash & Tolliver (2021), Solberg & Whitfield (2018), and Wexler & Ojo (2020) appear in the references but nowhere in the body. Several of them are directly relevant — a cautionary study on retention modelling with LMS trace data goes uncited in a manuscript that models retention with LMS trace data. This is a conventions defect that copyediting can resolve, but it also leaves the positioning against nearest prior work thinner than the reference list implies.
**Severity**: Minor
**Evidence Anchor**: absence: §§1–6 body text — expected in-text citations for the nine reference-list entries that appear only in the References; checked §1, §2, §3, §4, §5, §6
**Confidence**: 5 — full text search of all body sections against the reference list.
