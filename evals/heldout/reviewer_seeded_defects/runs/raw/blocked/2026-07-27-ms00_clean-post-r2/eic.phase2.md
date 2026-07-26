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
trigger: "comprehensible but carries fixable craft defects"

The manuscript is well organised and cleanly written; nothing here obstructs comprehension, so the block threshold is not approached. What it carries are craft and convention defects that a copy-editing pass will not fix on its own: no tables or figures anywhere despite descriptive statistics and a diagnostic scatterplot being discussed in the text, a shared-variance quantity narrated in words rather than reported as a number, and a reference apparatus whose formatting cannot be reconciled with live bibliographic records.

### D6: venue_fit_and_contribution

score: block
block_class: repairable
trigger: "The contribution is too slight or too derivative for the venue as submitted"

Topically this sits dead-centre for a learning-technology readership, so venue fit in the narrow sense is satisfied and the fatal threshold is not met. The contribution, as submitted, is not. The manuscript reports one bivariate coefficient for a relationship that has been synthesised repeatedly across e-learning contexts, and its stated warrant for publication is that the coefficient exists and was transparently obtained. That is a description of the paper, not an argument for it. I record this as repairable rather than fatal because a defined path to sufficiency exists within the present dataset, set out in the Review Body.

## Review Body

I write here as handling editor, not as a substitute for the specialist reports. Three questions I could have raised are deliberately left to the panel: the psychometric properties of the instruments as administered, the theoretical lineage of the perceived-usefulness construct, and the choice of self-report over institutional trace data. My remit is narrower and blunter — whether this manuscript, in this form, earns space in this venue, and whether its presentation meets the standard a reader is entitled to expect.

Let me state the central judgement plainly, because the manuscript's own modesty makes it easy to soften. Execution here is above the norm for the tier. The authors avoid causal language, name the reverse pathway themselves, bound their generalisation, and report their statistics with the conventions intact. None of that is contribution. A well-executed study of a settled question is still a study of a settled question, and the manuscript's repeated self-description as "incremental" and "design-bounded" reads to me less as scholarly discipline than as a pre-emptive answer to a question it never actually asks: what does the field know after this paper that it did not know before? On the text as submitted, the answer is nothing.

That is not the end of the matter, and I want to be specific about the alternative rather than dismissing the work wholesale. Venues of this kind do publish bounded single-institution findings, and they do so when the finding is *positioned* — when the reader is told where this estimate falls in the distribution of estimates that already exist, in what institutional context, from what sampling frame, and therefore what it calibrates. The manuscript invokes exactly this logic when it cites Song (2018) on cross-campus variability, then declines to supply the range that would make the logic operative. Everything needed to close that gap is available without new data collection: benchmark r = .42 against the published effect-size distribution, state the response rate against the enrolled denominator, characterise the sample beyond the assertion that it "spanned all four year levels," and report the shared variance as a number. A revised submission doing those four things, at short-communication length, is a defensible paper. The current one is not.

One further note, referred rather than scored: the power statement in §3.4 claims greater than .80 power at r ≥ .19, which on my arithmetic holds only after rounding. It is trivial in practice and belongs to the methodology reviewer; I mention it only so it is not lost between reports.

### S1: Causal restraint is genuine, not decorative

The manuscript does something uncommon at this length: it names the alternative causal direction in its own voice rather than burying it in a limitations list, and it holds correlational language consistently across the abstract, discussion, and conclusion. Reviewers should not spend effort attacking overreach that is not present.

**Evidence Anchor**: text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S2: Statistical reporting conventions are fully observed

The core result is reported with coefficient, interval, exact-threshold p, and n together, accompanied by a rank-order robustness check. This is the reporting standard many submissions at this tier fail, and the authors meet it without prompting.

**Evidence Anchor**: text: §4 "r = .42, 95% CI [.30, .52], p < .001, n = 214"

### S3: Limitations are substantive rather than performative

The self-report/behavioural-trace divergence is raised in the literature review and again in §6, and is tied to a named source rather than asserted as a generic caveat. The voluntary-response and single-site bounds are stated in terms of who would be over-represented, not merely that limits exist.

**Evidence Anchor**: text: §6 "self-reports of technology use are known to diverge from behavioral traces"

### W1: The contribution claim is asserted comparability with no comparison supplied

The manuscript rests its case for publication on being "comparable with prior work," but never states what the prior distribution of effect sizes is. Without that anchor, a reader cannot tell whether .42 is typical, high, or low, which means the incremental-data-point rationale does no work: an unlocatable point contributes nothing to a distribution. This is the defect that drives the D6 block. It is repairable with the existing dataset — benchmarking against published synthesis estimates requires reading, not re-sampling — but until it is repaired the paper offers the venue's readership a number without a frame.

**Severity**: Major
**Evidence Anchor**: text: §2 "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model."
**Confidence**: 5 — editorial judgement of contribution positioning against venue expectations is the core of the seat I occupy.

### W2: The entire reference apparatus uses a reserved DOI prefix and near-variant journal titles

All six DOIs share the 10.5555 prefix, which is reserved for test and example records rather than allocated to live registrants; none will resolve. Compounding this, several journal names are close variants of real titles rather than exact matches — *Computers & Education Review* and *British Journal of Educational Technology Studies* among them. I raise this as an editorial verification requirement, not as an accusation: from the manuscript alone I can establish that the identifiers are non-resolvable, not why. But no decision on this submission can be issued until every citation is independently resolved to a live record. If verification fails, this escalates immediately beyond the band assigned here and the submission ends. Note that this is the resolvability question only; the separate matter of whether the reference base is substantively adequate belongs to the domain reviewer.

**Severity**: Major
**Evidence Anchor**: text: References "https://doi.org/10.5555/2050001" and "Computers & Education Review"
**Confidence**: 5 — DOI prefix allocation and journal-title verification are routine editorial-office checks I perform on every handled submission.

### W3: Submitted as a full article, structurally a short communication

At roughly 1,700 words of body text, with six references and no tables or figures, this is a brief report presented against full-article expectations. The mismatch matters because it determines which standard applies: as a short communication the reporting density is close to adequate, whereas as a full article it is materially thin. I flag this as a routing question the authors should answer explicitly in a revised cover letter rather than leaving to the editor to infer, since the redirect itself is administratively cheap and does not by itself require rewriting.

**Severity**: Minor
**Evidence Anchor**: absence: manuscript front matter and structure — expected a declared article type or length matching full-article conventions; checked title, abstract, Sections 1 to 7, and reference list
**Confidence**: 4 — article-type routing is a standard editorial determination, though venue-specific thresholds vary.

### W4: A diagnostic the reader is asked to trust but not permitted to see

Section 3.4 reports conclusions drawn from visual inspection — linearity, monotonicity, absence of bivariate outliers — without supplying the plot. The same section reports no descriptive table, so the two distributions are characterised entirely in prose. This is a presentation defect rather than an analytic one: the checks may well have been performed correctly, but the reader is placed in the position of accepting them on assertion. A single scatterplot and a two-row descriptives table resolve it.

**Severity**: Minor
**Evidence Anchor**: text: §3.4 "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers"
**Confidence**: 4 — presentational adequacy against reporting conventions is squarely within the editorial remit.

### W5: Shared variance is discussed twice in words and reported zero times as a number

The Results section characterises the proportion of shared variance qualitatively, and the Discussion returns to the point, but r² is never given. This is imprecision where precision costs one figure, and it is not a neutral omission: the practical recommendation in §5 rests implicitly on how much of the variation perceived usefulness accounts for, and the reader is left to compute it. Report it.

**Severity**: Minor
**Evidence Anchor**: text: §4 "The proportion of variance shared by the two measures was accordingly modest"
**Confidence**: 5 — a stated quantity omitted from a results section is directly observable in the text.
