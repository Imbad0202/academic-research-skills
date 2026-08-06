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
trigger: "inconsistent terminology or notation"

The section architecture is sound and the through-line from question to method to result to interpretation is easy to follow. The warn rests on four presentational defects, the load-bearing one being that the dependent variable's response scale is defined only at its endpoints in §3.2 while §4 reports a median category label ("a few times per week") that does not exist anywhere in the Methods. Compounding this: the manuscript contains no numbered table or figure at all, including the scatterplot §3.4 says was inspected; r² is characterised in words but never given as a number; and there is no data availability, funding, or competing-interests statement. None of this obstructs assessment, so the block threshold is not met.

### D6: venue_fit_and_contribution

score: block
block_class: repairable
trigger: "an absent or nominal engagement with prior work such that no increment can be identified"

Topic and register fit the venue squarely, and the short empirical report stream is the correct vehicle. The block is not about scope and not about overclaiming. It is that the manuscript's declared contribution is wholly relational — "an incremental data point, comparable with prior work", "one point in a distribution", "consistent with prior technology-acceptance research" — and neither of the two things that relation requires is on the page. First, not one cited study's effect size appears anywhere, so comparability is asserted and cannot be checked by any reader. Second, all six references carry `10.5555/` DOIs, a documented test prefix that resolves to no indexed publication, so the relata themselves cannot be verified to exist. Either defect alone leaves the increment unidentifiable; together they make the engagement with prior work nominal in the precise sense my Phase 1 block criterion names. The fatal branch does not bind: the paper is not out of scope, does not rest on results it lacks, and makes no novelty claim that could be falsified against the cited record. Repairable.

## Review Body

I read this as the handling editor for the short empirical report stream, and I want to put my central editorial judgement first because it is easy to mistake for something else. The question I set out to answer was whether this paper's declared modesty is legitimate scoping that still clears the contribution bar, or a rhetorical shield in front of a contribution that does not. The answer is neither of the two obvious ones. The modesty is genuine and disciplined: the manuscript does not overclaim anywhere I could find, it names the reverse causal pathway itself rather than waiting to be told, and it keeps correlational language throughout. On the "stated implications and generalisations that the study's design and scope cannot support" branch of my own block criterion, this paper is clean, and I want that on the record because it is rarer than it should be.

The paper nonetheless fails the contribution bar as submitted, for a reason orthogonal to overclaiming: it under-delivers the relational work its own framing makes obligatory. A paper that positions itself as "one point in a distribution" has taken on a burden — the distribution has to be characterised well enough for the point to be locatable in it. Six references cannot do that, and only one of them (Song, 2018) is even multi-site. More concretely, the manuscript never states what any prior study found. The phrase "consistent with prior technology-acceptance research" appears in the abstract and again in §5 with two citations attached and no numbers behind it. A reader cannot tell whether r = .42 sits near the centre of the prior range, at its edge, or outside it. The value the paper offers is comparability, and comparability is the one thing it does not operationalise. This is fixable by rewriting plus additional citation, which is why I score it repairable rather than fatal.

The reference list is the more serious problem and I raise it without accusation as to cause. Every one of the six DOIs uses the `10.5555/` prefix, which is a test prefix, not a registered publisher prefix; none of the six resolves to an indexed publication. Several journal titles are also near-misses on real ones. I cannot verify a single source in this manuscript. For a paper whose entire contribution claim is relational, that is not a copy-editing matter — it removes the anchor the contribution is tied to. Before any recommendation short of rejection can stand, the authors need to supply resolvable identifiers for all six works, and the editorial office should verify them independently rather than accept a resubmitted list at face value.

On my own declared exposure to taking well-presented statistics on trust, I checked rather than assumed. The confidence interval is correct: Fisher-z on r = .42 with n = 214 returns [.30, .52], matching §4 exactly. The power statement is right to rounding — at r = .19 with n = 214 the two-tailed power is approximately .798, so "greater than .80 power to detect r >= .19" is marginally generous but not misleading. The Spearman check at ρ = .40 is consistent with the Pearson estimate. One threat is untreated and I flag it for the methodology seat rather than scoring it here: both variables come from the same self-administered instrument at the same sitting, so common-method variance can inflate the observed association, and neither §5 nor §6 mentions it. That belongs in D1, but an editor should not let it pass unremarked.

On format, my recommendation is unambiguous: this is a short empirical report, not a full article, and the authors should be told so explicitly rather than left to discover it at proof stage. The length is proportionate to a single bivariate association and should not be padded to article dimensions during revision. What should grow is the comparative anchoring in §2 and §5, not the prose elsewhere.

Two smaller things bearing on our practitioner readership. The sole practice implication in §5 is that onboarding which surfaces concrete usefulness "may be worth institutional attention". As written, a learning-technology practitioner cannot act on that: no mechanism, no design guidance, and the direction of effect the recommendation presumes is the same direction the paper elsewhere declines to claim. And the absence of any table means a reader wanting to reuse these descriptives in a synthesis has to mine them out of sentences.

### S1: Inferential reporting is complete to the standard the venue should demand

**Evidence Anchor**: text: §4 Results "r = .42, 95% CI [.30, .52], p < .001, n = 214"

Point estimate, interval, p value, and n appear together in one place, with a Spearman robustness check and an a priori sensitivity statement in §3.4 and Cronbach's α in §3.2. I recomputed the interval and it is correct. This is the reporting profile that makes a single-site estimate reusable, and it is the strongest thing in the manuscript.

### S2: Causal discipline is maintained without prompting

**Evidence Anchor**: text: §5 Discussion "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

The manuscript states the reverse pathway as equally consistent rather than burying it in a limitations list, and the abstract, results, discussion, and conclusion all hold the same correlational register. There is no drift between what the abstract promises and what §4 delivers.

### S3: Ethics and consent reporting is complete and specific

**Evidence Anchor**: text: §3.3 Procedure and ethics "Participation was voluntary and anonymous, no course credit or payment was offered"

Committee review, consent mechanism, absence of inducement, anonymity, and non-linkability are each stated in a form an editor can check against the venue's requirements. Nothing here needed to be queried back to the authors.

### S4: Limitations are load-bearing rather than ritual

**Evidence Anchor**: text: §6 Limitations "We report the association as a bounded, single-sample descriptive finding to be read alongside these constraints"

The four limitations named — single site, self-report instead of logs, cross-sectional design, voluntary-response bias — are the four that actually bound this estimate, and §7 turns them into a specific research agenda rather than a generic call for more work.

### W1: Every reference carries a test-prefix DOI, so no cited source can be verified

**Severity**: Critical
**Evidence Anchor**: text: References list "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050004", "https://doi.org/10.5555/2050006"
**Confidence**: 5 — routine DOI verification is part of my triage workflow, and `10.5555` is the documented test prefix, not a registered publisher prefix.

All six DOIs sit in the `10.5555` test range and none resolves to an indexed publication; the journal titles are additionally close variants of real ones ("British Journal of Educational Technology Studies", "Computers & Education Review"). Uncorrected, this makes acceptance impossible on its own terms: the paper's contribution is defined entirely by its relation to prior work, and that relation currently points at nothing verifiable. Resolvable identifiers must be supplied for all six and confirmed by the editorial office before the manuscript can be assessed further on substance.

### W2: The comparability and "one point in a distribution" claims are never operationalised

**Severity**: Major
**Evidence Anchor**: absence: §2 Literature Review and §5 Discussion — expected numeric effect sizes from the cited prior studies against which r = .42 is called consistent; checked Abstract, §1, §2, §4, §5, §7, and References
**Confidence**: 4 — this is the standard positioning check I apply to every incremental single-site submission in this stream.

§2 says effect sizes "vary across samples and instruments" and §5 calls the present result "consistent with prior technology-acceptance research", yet no prior coefficient, range, or interval appears anywhere in the manuscript. The framing borrowed from Song (2018) demands more than this: locating a point requires the distribution to be characterised, and six sources, one of them multi-site, cannot characterise it. Whitfield (2019) compounds the pattern by entering only in §5 as support for the practice implication, never having been positioned in §2. Repair requires reporting the comparison coefficients explicitly and broadening the base enough to make the range meaningful, not merely rewording the claim.

### W3: The use measure's scale is undefined at points 2 to 4, and §4 reports a category that Methods never establishes

**Severity**: Major
**Evidence Anchor**: text: §3.2 Measures and §4 Results "rarely or never to 5 = several times daily", "Self-reported LMS use had a median category of"
**Confidence**: 4 — direct comparison of the Methods instrument description against the Results text.

§3.2 anchors only points 1 and 5 of the five-point frequency item and never gives the item's verbatim wording. §4 then reports a median category of "a few times per week", a label absent from the instrument as described, so a reader cannot map the central descriptive result onto any scale point. Because the declared contribution is a reusable, comparable data point, an under-specified dependent variable defeats the reuse the paper is offered for: no one can administer the same item or align it with another study's use measure. The full item wording and all five anchors are needed, ideally with the instrument as an appendix.

### W4: No tables or figures, including the scatterplot the analysis relies on

**Severity**: Minor
**Evidence Anchor**: absence: §3.4 Analysis and §4 Results — expected a descriptive statistics table and the scatterplot the text says was inspected; checked every numbered section, the Abstract, and the reference list for any numbered exhibit
**Confidence**: 5 — verified by reading the manuscript end to end for numbered exhibits.

§3.4 rests the linearity, monotonicity, and outlier judgements on visual inspection of a scatterplot that is never shown, so those judgements cannot be audited. Descriptives for both measures are dispersed across §4 prose rather than tabulated. Neither changes the reported result, but both raise the cost of reuse and of reviewer verification for no benefit.

### W5: No data availability, funding, or competing-interests statements

**Severity**: Minor
**Evidence Anchor**: absence: Front and back matter of the manuscript — expected data availability, funding, and competing interests statements; checked Abstract, keywords, §3.3 Procedure and ethics, §7 Conclusion, and References
**Confidence**: 4 — checked against the declarations the venue requires of every submission in this stream.

The ethics reporting in §3.3 is otherwise exemplary, which makes the missing declarations look like an oversight rather than a substantive problem. A paper arguing for cumulative, comparable single-site estimates has a particular interest in saying whether the anonymised item-level data can be obtained.

### W6: r² is described qualitatively but never reported

**Severity**: Minor
**Evidence Anchor**: text: §4 Results "The proportion of variance shared by the two measures was accordingly modest"
**Confidence**: 5 — the quantity is directly derivable from the reported coefficient.

The sentence gestures at shared variance without giving the number, which for r = .42 is approximately .18. Stating it costs one clause, aids the interpretation §4 is already attempting in plain terms, and is exactly the kind of figure a later synthesis will want to lift.

### W7: The single practice implication is not actionable for this readership

**Severity**: Minor
**Evidence Anchor**: text: §5 Discussion "may be worth institutional attention, a possibility also raised in practitioner accounts of digital-environment onboarding"
**Confidence**: 4 — judged against what the practitioner segment of this venue's readership can operationalise from a short report.

The recommendation names no mechanism, no onboarding design feature, and no way to tell whether it worked, and it presupposes the perception-to-use direction that §5 itself declines to assert two paragraphs earlier. Either ground it in something the data can bear or drop it and let the paper stand on its measurement contribution; as written it invites practitioners to act on a direction of effect the authors have disclaimed.
