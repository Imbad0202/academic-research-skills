contract_role: da

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "an obvious alternative explanation left unmentioned"

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I came to this manuscript expecting to break its spine and could not. That is worth stating plainly before the attack, because it constrains the verdict. The arithmetic is internally consistent: 233 − 14 − 5 = 214; the abstract, Results, and Conclusion all report r = .42 with the same n; the 95% CI [.30, .52] is what a Fisher-z transform on r = .42 with n = 214 actually returns; and the claimed sensitivity to r ≥ .19 at α = .05 is approximately correct at .80 power. The authors state the reverse-causation pathway explicitly rather than burying it, report a Spearman check for an ordinal outcome, and decline to convert a correlation into a mechanism. A cross-sectional correlational claim, stated as a cross-sectional correlational claim, is not incoherent merely for being small. So the central thesis survives, and the score is warn rather than block.

The load-bearing weakness is not in what the paper claims about causation but in what it never names. The two variables in the only reported analysis are both self-descriptions, elicited from the same respondent, in the same instrument, on the same occasion, on adjacent five-point scales. Common-method variance is the first rival explanation any acceptance-research reviewer reaches for, and it is a rival for the *existence and magnitude of the association*, not merely for its direction. The manuscript writes "We take these cautions seriously" and then takes seriously exactly the three cautions it chose to cite — reverse causation (Delgado), context (Ibarra & Poll), and self-report-versus-log fidelity (Vasquez). The Vasquez citation is deployed as a construct-labelling move ("we measure perceived use, not behaviour"), which neutralises a validity objection while leaving the shared-method objection untouched. A four-item Limitations list that omits it is not a complete accounting of alternatives; it is a curated one. This is repairable in revision, but until it is repaired the paper's claim to have dispatched the rivals is broader than its own text supports.

The second structural problem is that the sampling frame is described in a way that quietly contradicts the paper's own account of what an LMS is. Section 1 tells us the LMS hosts "course materials, assessments, announcements, and discussion." Section 3.1 tells us the survey was distributed through "the institution's course-announcement channel." If those two sentences refer to the same system — and the manuscript never says otherwise — then recruitment ran through the outcome variable, and students who rarely or never access the LMS could not have been invited. "All enrolled undergraduates were eligible" then equivocates between eligibility and reachability: the eligible population is all undergraduates, the reachable population is LMS-announcement readers, and the reported r is estimated on a sample selected on the dependent variable. Limitation four gestures at this ("students who engage more with institutional channels may be overrepresented") without drawing the inferential consequence for the estimate itself. Compounding the verification problem, the outcome variable is reported with a median category and nothing else — no mean, no dispersion, no frequency distribution — so a reader cannot check for the floor truncation this recruitment route predicts, and cannot check the §3.4 assertion that "both distributions were approximately symmetric" that warrants the Pearson estimate. I treat that missing-descriptives point as minor rather than major only because the Spearman convergence largely insulates the conclusion from distributional shape.

The one place where the argument actually turns on itself is the practical implication. In §5 the authors state that the reverse pathway "is equally consistent with the data," and then, two sentences later, recommend that onboarding designed to raise perceived usefulness "may be worth institutional attention." If direction is genuinely undetermined, these data supply no support for intervening on perceived usefulness to move use; the recommendation presupposes precisely the arrow the authors have just declared unidentified. The hedge ("suggested by, not proven by") softens the register but does not repair the inference, and the Whitfield (2019) citation propping it up is a practitioner account, not efficacy evidence. This is the paper's only actionable implication and it is self-undercut.

Two further claim–evidence gaps deserve revision. First, the contribution is stated as "an incremental data point, comparable with prior work," and the finding is twice called "consistent with prior technology-acceptance research" — yet no prior coefficient, range, or interval appears anywhere in the manuscript. Since the paper also cites Song (2018) for the proposition that association strengths vary by institution, the consistency claim as written is unfalsifiable: any value would satisfy it. Comparability is the paper's stated warrant for mattering at all, and the comparison is never performed. Second, and more locally: the abstract's "previously validated instrument" transfers the original's validation to a six-item adaptation whose only reported psychometric property in this sample is α = .88, which is internal consistency, not validity. Relatedly, "indicating that the association did not depend on the parametric assumption" overstates what a Pearson–Spearman agreement demonstrates, and ρ = .40 is reported without a CI or p; and the shared variance is described qualitatively as "modest" where every other quantity in the paper is given numerically — r² = .18 should simply be stated.

Finally, one internal inconsistency in the methods account that the authors must resolve rather than argue away: §3.1 removes "5 duplicate entries," while §3.3 states that no identifying information was collected and that responses could not be linked to individuals. Deduplication requires some linking key. Either a key existed, in which case the anonymity statement needs qualifying, or duplicates were inferred from response patterns, in which case the rule needs stating. As written the two paragraphs cannot both be taken at face value.

None of these defects is singleton-fatal. Each is a rewrite, an added limitation, an added comparison, or a disclosed procedure — not a different study. But there are enough of them, and they cluster tightly enough around the paper's habit of naming the objections it has answers to while passing over the one it does not, that the coherence dimension cannot be scored clean.

#### CRITICAL

| # | Issue | Evidence Anchor | Confidence |
|---|---|---|---|

#### MAJOR

| # | Issue | Evidence Anchor | Confidence |
|---|---|---|---|
| M1 | Practical implication contradicts the authors' own declared indeterminacy of direction: if the reverse pathway is "equally consistent," these data cannot support intervening on perceived usefulness to raise use. The paper's sole actionable recommendation is self-undercut, and the supporting citation is a practitioner account rather than efficacy evidence. | text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data" and "may be worth institutional attention" | 5 — direct internal contradiction between adjacent sentences |
| M2 | Common-method variance is never named as a rival explanation, although both variables are self-descriptions from one respondent in one instrument on one occasion. The paper asserts it takes methodological cautions "seriously" while addressing only the three it selected; the shared-method rival bears on the magnitude of r = .42 itself, not merely its direction. | absence: §6 Limitations — expected an explicit common-method-variance rival explanation for two self-reports collected in one instrument on one occasion; checked Abstract, §2 Literature Review, §3.4 Analysis, §4 Results, §5 Discussion, §6 Limitations | 4 — standard rival for same-source survey correlations |
| M3 | Sampling equivocates eligibility with reachability. §1 lists announcements as an LMS function, so recruitment plausibly ran through the very system whose use is the outcome, conditioning the sample on the dependent variable and truncating the low-use range; the scope claim "among undergraduates" then exceeds what the reachable frame supports. | text: §3.1 "All enrolled undergraduates were eligible" and "The survey was distributed through the institution's course-announcement channel" | 4 — inference from the paper's own definition of LMS functions; channel identity is not disclosed |
| M4 | The claimed contribution rests on a comparison that is never performed: no prior coefficient, range, or interval appears anywhere, so "consistent with prior work" is unfalsifiable as stated, especially given the paper's own citation that association strengths vary by institution. | absence: §2 and §5 — expected a numeric prior effect-size estimate or range against which the reported r = .42 is compared; checked Abstract, §2 Literature Review, §4 Results, §5 Discussion, §7 Conclusion | 5 — exhaustive scan of all reported quantities |
| M5 | Terminological slide from the declared construct: the paper commits to treating the measure as perceived use rather than behaviour, then repeatedly substitutes "engagement" — a behavioural term — in the abstract, results, and discussion, contradicting the commitment its own Vasquez citation is used to justify. | text: Abstract "perceived usefulness tracks with LMS engagement among undergraduates" and §2 "treat our self-report measure as an indicator of perceived use rather than a behavioral count" | 4 — verbatim comparison of stated commitment against downstream usage |
| M6 | Unresolved tension in the data-handling account: five duplicate entries were removed, yet the procedure section states no identifying information was collected and responses could not be linked to individuals. Deduplication requires a linking key or a stated pattern rule; neither is disclosed, so the analytic sample definition and the anonymity claim cannot both be taken at face value. | text: §3.1 "5 duplicate entries were removed" and §3.3 "No identifying information was collected, and responses could not be linked back to individual students" | 4 — logical incompatibility of two procedural statements as written |
