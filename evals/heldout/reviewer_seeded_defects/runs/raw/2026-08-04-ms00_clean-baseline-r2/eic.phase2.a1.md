## Dimension Scores

contract_role: eic

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: not_assessed

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: warn
trigger: "inconsistent reporting formats, or deviations from venue conventions"

The manuscript's organisation is genuinely competent — the arc from narrow question to bounded interpretation is legible, and the abstract does not overstate the results. What pushes this to warn rather than pass is a cluster of convention-level omissions that a structural and copy-editing pass would resolve: the shared-variance figure is described qualitatively but never reported numerically while every other statistic is given in full; a scatterplot is asserted to have been inspected but is not shown; no descriptive table or exhibit of any kind appears; the eligible-population denominator and hence the response rate are absent; there is no data availability statement and the six adapted items are not reproduced; and the sole practitioner citation supporting the practice implication is introduced in the Discussion without ever appearing in the Literature Review. None of these prevents review — the numbers a reader needs to follow the argument are all in the running text — so the block threshold ("results reported without the tables or statistics they refer to") is not met.

### D6: venue_fit_and_contribution

score: block
block_class: repairable
trigger: "The contribution is not established as advancing on prior work"

Topically the submission sits inside the journal's remit: LMS engagement among undergraduates is core readership territory, so remit is not the issue. The issue is that this manuscript's entire claimed contribution is relational — it offers itself as "an incremental data point, comparable with prior work" and as one point in the distribution Song (2018) is said to describe — and that relation cannot be established, for two independent reasons. First, the comparison set is unverifiable: all six references carry DOIs under the CrossRef `10.5555` test/reserved prefix, in a sequential block (2050001–2050006), and none of the six outlet titles is a recognisable indexed journal in this field. I cannot confirm that a single cited finding exists, which means the positioning claim ("consistent with prior technology-acceptance research") has no verified referent. Second, even taking the literature review at face value, the manuscript states that prior work already reports positive perceived-usefulness/use associations in higher education; a further single-site bivariate coefficient, with no new construct, instrument, population, or design feature, does not by itself establish an advance on that base. Block, not fatal: my fatal condition is reserved for material categorically outside the remit or with nothing revision could bring into scope, and neither holds — verifiable citations plus recategorisation as a Research Note would let the contribution question be asked properly.

## Review Body

This came to me as a first-pass scope and category triage, and I want to be explicit about the order in which I read it, because the order matters to the verdict. I read the reference list before I read the argument. That is standard practice on this desk for submissions whose stated value is comparability with an existing evidence base, and here it changed the assessment materially.

The reference check does not clear. Every one of the six sources resolves to a DOI under the `10.5555` prefix, which CrossRef reserves for testing rather than for registered content, and the six suffixes run consecutively from 2050001 to 2050006 — a pattern produced by generation, not by six independent registrations across four publishers and four years. The outlet names are near-misses for real venues rather than the venues themselves. I am not asserting as established fact that these citations were fabricated; I am reporting that verification failed on all six, which is the finding an editor must act on. The consequence is not merely bibliographic hygiene. This manuscript's contribution claim is *entirely* comparative — it does not claim to test a model, establish a mechanism, or introduce an instrument, only to add "one point in a distribution." Remove the verified distribution and there is no stated contribution left standing. That is why the D6 block sits where it does rather than being handled as a reference-formatting request. I flag for the panel and the synthesiser that if the other seats reach a comparable conclusion about the evidence base, the escalation grounds are research-integrity grounds that my own dimension card does not enumerate; I have scored strictly within the trigger I committed to in advance, and I have not stretched a scope-and-contribution fatal condition to cover an integrity finding it does not describe.

On category: even with a clean reference list, this is not a research article. One bivariate correlation from one unnamed institution, honestly reported, is a Research Note or a short empirical report. The question I ask on every submission is what the issue-summary line would say, and here the only honest line is: "at one mid-sized university, students who thought the LMS was useful said they used it more (r = .42), consistent with what was already known." No learning technologist, academic developer, or e-learning researcher changes a decision on that. The practice implication the authors do offer — onboarding that demonstrates concrete usefulness may be worth attention — is hedged into non-actionability in the same sentence in which it is raised, and it leans on a practitioner source introduced only in the Discussion and never appraised. The authors' modesty about all of this is accurate, and I want to separate two things that are easy to conflate: the register is correct, and correctness of register is not contribution. A paper that says truthfully that it shows very little has told the truth about a submission that shows very little.

I also want to state plainly what this manuscript does better than most in its genre, because my seat's characteristic failure mode is to let novelty gatekeeping crowd out that credit. The statistical reporting is close to exemplary for the format: point estimate with a 95% confidence interval, exact-form p, n, a Spearman coefficient as a distributional robustness check, a prospective sensitivity statement giving the detectable effect at conventional power, and an explicit acknowledgement that the reverse causal pathway fits the data equally well. The limitations section names the real constraints rather than decorative ones, including self-report/log divergence and voluntary-response bias. If this work were resubmitted as a Research Note against a verifiable literature, the reporting craft would not be what held it back.

Two matters I am registering rather than scoring, because they belong to other seats. The response rate is absent: 233 responses were received against an eligible population of "all enrolled undergraduates" whose size is never given, so the voluntary-response bias the authors correctly acknowledge cannot be sized by any reader. That is the methodology seat's dimension to score, but it bears on my reader-value assessment, since a site-level point estimate whose representativeness of its own site is unknowable is a weaker data point than the framing implies. Separately, the characterisations of Delgado (2020), Ibarra and Poll (2021), Vasquez (2020), and Song (2018) are internally coherent and appropriately cautionary, but they are unverifiable for the same reason as the DOIs, so the domain seat should treat prior-work representation as unconfirmed rather than as confirmed-correct.

For a revision to be reviewable at this venue, I would need: verifiable citations with resolving DOIs to indexed outlets; recategorisation to Research Note with the framing rewritten to match; the eligible-population denominator and response rate; the shared-variance estimate reported numerically alongside the correlation; the scatterplot and a descriptives table supplied; and the adapted instrument items plus a data availability statement included.

### S1: Complete, unpadded statistical reporting of the primary association

The primary result is reported with everything an assessor needs and nothing inflated: point estimate, interval, exact-form significance, sample size, plus a Spearman coefficient reported as a robustness check against the ordinal-item concern and a prospective statement of the smallest effect the design could detect at conventional power. This is materially better practice than the norm in single-site acceptance surveys.

**Evidence Anchor**: text: §4 Results — "r = .42, 95% CI [.30, .52], p < .001, n = 214"

### S2: Disciplined refusal of causal inference, including the symmetric reverse pathway

Rather than hedging with a boilerplate correlation-is-not-causation sentence, the Discussion states the specific competing pathway and concedes it fits the data equally well. Causal verbs are absent throughout, including in the abstract and conclusion, where they most commonly leak in.

**Evidence Anchor**: text: §5 Discussion — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S3: Scope of the claim declared at the outset and held to consistently

The Introduction commits to a descriptive-correlational frame and a deliberately narrow question, and the abstract, results, discussion, and conclusion all stay inside that commitment. There is no drift between the question asked and the question answered — a structural virtue that is rarer than it should be.

**Evidence Anchor**: text: §1 Introduction — "We frame the question descriptively and correlationally."

### S4: Limitations that name the constraints that actually bind

The limitations enumerate single-site generalisability, single-item self-report against behavioural logs, the cross-sectional bar on temporal inference, and self-selection into a voluntary institutional channel. These are the four constraints a reviewer would raise, stated without euphemism.

**Evidence Anchor**: text: §6 Limitations — "response was voluntary, so students who engage more with institutional channels may be overrepresented"

### W1: Entire evidence base fails verification — six sequential CrossRef test-prefix DOIs and no recognisable outlets

All six references carry `10.5555` DOIs, the prefix CrossRef reserves for testing rather than registered content, with suffixes running consecutively 2050001–2050006 across four ostensibly different publishers and four publication years. None of the six journal titles is a recognisable indexed outlet in educational technology or measurement. Consequently no cited claim can be checked, the "consistent with prior technology-acceptance research" positioning has no confirmable referent, and the manuscript's sole stated contribution — comparability with prior work — is unsupported at its foundation. Uncorrected, this makes acceptance impossible on its own, independent of every other finding in this report.

**Severity**: Critical
**Evidence Anchor**: text: References — "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"
**Confidence**: 5 — maintain this journal's reference-verification checklist and screen DOI prefixes on every submission.

### W2: Contribution is below the research-article bar and is self-declared as incremental

The manuscript offers one bivariate correlation from one site, with no new instrument, construct, population, design feature, or synthesis, and states that prior work already reports the same association in higher education. Its own framing concedes the point. That is a Research Note, not a research article, and the framing, length, and claim structure would all need rewriting to that category. The core finding itself survives — it is honestly reported — but the article-level claim around it does not.

**Severity**: Major
**Evidence Anchor**: text: §2 Literature Review — "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model."
**Confidence**: 5 — first-pass category triage on LMS-adoption survey submissions is my standing editorial function.

### W3: No response rate or eligible-population denominator, so the site estimate's representativeness is unknowable

Eligibility is defined as all enrolled undergraduates, but that population is never sized, so 214 valid responses could represent a small or a substantial fraction of the institution. Because the manuscript's only claimed value is as a site-level data point to be compared against multi-campus distributions, and because it correctly flags voluntary-response bias, the missing denominator removes the reader's ability to size the very bias the authors concede. Supplying it requires new reporting and a rewritten interpretation of how much weight the site estimate can bear. Scoring consequence belongs to the methodology seat; I register it here for its effect on reader value.

**Severity**: Major
**Evidence Anchor**: absence: §3.1 Design and participants — expected response rate against an eligible-population denominator; checked §3.1, §3.4, §4, §6, and Abstract
**Confidence**: 4 — routine editorial completeness check on survey submissions, though the methods seat owns the design judgement.

### W4: The one practice implication is hedged to non-actionability and rests on an unappraised late-entry source

The onboarding implication is introduced, attributed to a practitioner account that appears nowhere in the Literature Review, and withdrawn within the same sentence. The result is that the editorial takeaway line for an issue summary cannot be written from the paper's own claims, which weakens its case for readership interest without changing the empirical core.

**Severity**: Minor
**Evidence Anchor**: text: §5 Discussion — "though this implication is suggested by, not proven by, the present correlation"
**Confidence**: 4 — judging actionability for learning technologists and academic developers is this seat's standing test.

### W5: Shared variance described qualitatively but never reported numerically

Given that the correlation, its interval, p, n, and a Spearman check are all reported precisely, describing the shared-variance proportion only as "modest" is an inconsistent reporting standard within a single paragraph. The figure is trivially derivable and should be stated.

**Severity**: Minor
**Evidence Anchor**: text: §4 Results — "The proportion of variance shared by the two measures was accordingly modest"
**Confidence**: 5 — a reporting-consistency check within venue conventions.

### W6: No exhibits at all, including the scatterplot the analysis says was inspected

The analysis section relies on a scatterplot inspection to justify the linearity and outlier assumptions, but the plot is not presented, and no descriptive table of either measure appears. Readers must accept the assumption checks on assertion. This is a presentation gap rather than an analytic one.

**Severity**: Minor
**Evidence Anchor**: absence: §4 Results — expected the inspected scatterplot and a descriptive table of both measures; checked §4, §3.4, and all section bodies for figure or table captions
**Confidence**: 5 — checked every section body for exhibit captions and cross-references.

### W7: Missing data availability statement and instrument items

The six adapted perceived-usefulness items are not reproduced, and there is no data availability statement, so neither the measure nor the dataset is inspectable at the level this journal's conventions expect. Both are additions to back matter rather than changes to the study.

**Severity**: Minor
**Evidence Anchor**: absence: back matter — expected a data availability statement and the six adapted scale items; checked §3.2, §3.3, §3.4, References, and all post-reference content
**Confidence**: 5 — standard venue-convention completeness check at submission triage.
