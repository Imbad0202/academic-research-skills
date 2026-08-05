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
score: warn
trigger: "followable but has localised presentation defects"

### D6: venue_fit_and_contribution
score: block
block_class: repairable
trigger: "The contribution is too thin or too derivative to warrant publication here as submitted"

## Review Body

I read this manuscript in the order my desk screen requires: reference base first, then contribution threshold and genre, then the reader-interest test. The first of those checks did not survive, and it changes the character of everything downstream.

**Reference base.** All six references carry DOIs under the `10.5555` prefix with strictly sequential suffixes running `2050001` through `2050006`. `10.5555` is the Crossref test prefix; it is not assigned to any publisher, and DOIs under it do not resolve to content. The sequential suffix pattern — six sources, six consecutive integers, allocated in citation order — is not a pattern that arises from six independent publications in six different journals across four years. The journal titles compound the concern: *British Journal of Educational Technology Studies*, *Computers & Education Review*, and *Journal of Educational Technology Research* are near-misses on real titles rather than real titles. I am not in a position to adjudicate intent from a manuscript alone, and I am not asserting one. I am recording that the entire citational substrate of this paper is unverifiable, and that this is the finding an editor must resolve before any judgement about revision is meaningful. It matters concretely, not just formally: the perceived-usefulness instrument's provenance rests on Costa and Wren (2019), the calibration claim ("consistent with prior technology-acceptance research") rests on that source plus Ibarra and Poll (2021), and the measurement caution the authors properly credit rests on Vasquez (2020). If those sources cannot be resolved, the paper has no validated instrument, no comparison distribution, and no literature. Whether the *representation* of prior work is accurate is D2's jurisdiction and I defer to that seat on substance, but the seat needs this flag in front of it.

**Literature adequacy, separately from authenticity.** Suppose all six sources resolved tomorrow. Six references, none dated later than 2021, still cannot sustain a literature review for a construct with a forty-year research base. There is no Davis, no Venkatesh, no UTAUT, and — most damaging for a paper whose whole claim is calibration against prior findings — no meta-analytic source. The relationship under study has been synthesised repeatedly across hundreds of samples. A manuscript positioning itself as "one point in a distribution" must show the distribution. This one asserts consistency with prior work without ever quantifying what prior work found, which leaves the reader unable to tell whether r = .42 is typical, high, or low.

**Contribution and genre.** One bivariate association, one site, one self-reported ordinal outcome, no model test, no moderator, no comparison. As a full seven-section research article this does not clear the bar at a credible venue, and I would say the same if the references were impeccable. The architecture makes it worse rather than better: seven numbered sections, a standalone Limitations section, and a standalone Conclusion that restates the Abstract, all wrapped around a Results section of two paragraphs containing exactly one inferential test. The frame is doing rhetorical work the content cannot support.

The Research Note reframing deserves a direct answer, because it is the only route I can see. A good note here would be roughly two thousand words: question, sample, measure, the correlation with its interval, and a short positioning paragraph against a *properly built* comparison base — ideally a table placing this estimate alongside published coefficients from named prior samples. It would drop the separate Conclusion, fold Limitations into the Discussion, and add the descriptive table and scatterplot the current Methods section already claims to have inspected. Crucially, it would have to state what the reader gains from one more point estimate, which the present manuscript never does. A weak article is what we have: note-sized content in article-sized packaging.

**Reader-interest test.** For learning technologists and institutional practitioners, I looked for the actionable takeaway and could not find one the authors themselves are willing to stand behind. The single practical implication offered — that onboarding should help students see concrete usefulness — is immediately withdrawn as "suggested by, not proven by, the present correlation," and it is in any case advice the field has been giving for two decades. This is where I want to be precise about something the manuscript does genuinely well and something it does not. The hedging is epistemically correct throughout. It is also, at present, load-bearing in the wrong direction: "offered as an incremental, design-bounded contribution" is unarguable, and unarguable is not the same as publishable. A claim so carefully bounded that no reader could dispute it is also a claim no reader can use. The authors are entitled to refuse to overclaim; they are not thereby relieved of the burden of claiming something.

**Why I did not mark this fatal.** My Phase 1 fatality condition required either total scope mismatch or established knowledge presented as new. Neither holds. LMS engagement is squarely within a learning-technology venue's scope, and the manuscript is conspicuously honest that its finding is not new — that honesty is real and I am not going to convert it into an aggravating factor. A defensible contribution is reachable: reconstruct the reference base from resolvable sources, position the estimate against a quantified prior distribution, and either add substance (log data, second site, a moderator) or shrink the packaging to match the content. That is substantial work but it is within revision scope, so the block is repairable rather than fatal.

**Boundaries.** I have deliberately not scored the psychometrics. Whether a single five-point frequency item can serve as a dependent variable, whether Pearson's r is appropriate for it, and whether the six-item adaptation retains the original instrument's validity are D1 questions and I leave them entirely to the methodology seat — I note only that the answers there could tighten the D6 picture considerably, not loosen it.

**On my own bias.** My standing risk in this seat is punishing well-calibrated small-scope work, which the field needs more of. I have tried to test for it. The reason this manuscript fails my contribution dimension is not that its scope is small; it is that its reference base does not resolve, its comparison distribution is never quantified, and it declines to name a takeaway. A small, honest, well-positioned note would pass. This is small and honest but not positioned.

### S1: Causal discipline is maintained consistently, not just in the Limitations section

The reciprocal-causation problem is raised in the Discussion as a live alternative rather than parked as boilerplate, and the correlational register holds from Abstract through Conclusion without a single slip into causal verbs. This is harder to do than it looks and many submissions at this scope fail it.

**Evidence Anchor**: text: §5 Discussion — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"
**Confidence**: 5 — editorial screening of acceptance-model submissions for causal-language slippage is routine work in this seat.

### S2: Inferential reporting for the single test is complete

The coefficient is reported with its 95% interval, p value, and n; a Spearman coefficient is given as a robustness check against the parametric assumption; and an a priori sensitivity statement establishes what the design could detect. Many manuscripts of this size report r and p alone.

**Evidence Anchor**: text: §3.4 Analysis — "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05"
**Confidence**: 4 — the reporting completeness is directly checkable; whether the sensitivity calculation was genuinely a priori is not.

### S3: Sample attrition is accounted for transparently

The path from responses received to responses analysed is given with the exclusion reasons and counts stated separately, so a reader can reconstruct the analytic sample. This is a small courtesy that a surprising number of survey submissions omit.

**Evidence Anchor**: text: §3.1 Design and participants — "14 incomplete submissions and 5 duplicate entries were removed, leaving 214 valid responses"
**Confidence**: 5 — arithmetic and completeness are verifiable on the page.

### S4: The Limitations section names threats that actually threaten the finding

Voluntary-response bias, single-site scope, self-report divergence from behavioural traces, and cross-sectional inference are each stated in terms of what they would do to this result, rather than as a generic disclaimer list.

**Evidence Anchor**: text: §6 Limitations — "students who engage more with institutional channels may be overrepresented"
**Confidence**: 4 — the section's content is on the page; my judgement about which threats are material is field-standard but contestable.

### W1: The entire reference base is unverifiable — test-prefix DOIs with sequential suffixes

All six DOIs use the `10.5555` Crossref test prefix, which resolves to no publisher content, and the suffixes run consecutively from `2050001` to `2050006` in citation order. Several journal titles are near-variants of real titles rather than real titles. Uncorrected, this leaves the manuscript with no validated instrument (the perceived-usefulness scale is "adapted from Costa and Wren, 2019"), no comparison distribution for its central calibration claim, and no literature review — acceptance is impossible at any venue in this state, and the finding requires an editorial integrity check independent of dimension scoring.

**Severity**: Critical
**Evidence Anchor**: text: §References — "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006"
**Confidence**: 5 — maintaining this journal's reference-integrity screen is a standing responsibility of this seat and the `10.5555` prefix pattern is unambiguous.

### W2: One bivariate association from one site does not meet the research-article threshold

The manuscript reports a single correlation between two self-report measures at one unnamed institution, tests no model, examines no moderator, and offers no comparison condition. Its own framing concedes the finding replicates existing work. As a full research article this is below the contribution bar; the core estimate itself survives, so the defect is addressable by reframing to a Research Note plus quantified positioning against prior estimates, but that is substantial rewriting rather than polish.

**Severity**: Major
**Evidence Anchor**: text: §7 Conclusion — "offered as an incremental, design-bounded contribution rather than a causal claim"
**Confidence**: 5 — desk-screening single-site acceptance correlational submissions against the article threshold is the core competence of this seat.

### W3: Six pre-2021 sources cannot sustain a review of a forty-year construct

Even setting authenticity aside, the literature base omits the canonical technology-acceptance sources and, more damagingly for this paper's argument, any meta-analytic synthesis. The manuscript's positioning claim depends on knowing what prior work found; without a quantified prior distribution the reader cannot judge whether r = .42 is typical, elevated, or low, so the paper's stated purpose — comparability with prior work — is unmet.

**Severity**: Major
**Evidence Anchor**: absence: §2 Literature Review — expected canonical technology-acceptance and meta-analytic sources for a construct with a forty-year research base; checked §1, §2, §5, §7, and the reference list
**Confidence**: 5 — adequacy of a literature base relative to a construct's research volume is a routine desk-screen judgement.

### W4: No tables or figures, including the scatterplot the Methods section claims to have inspected

The manuscript contains no displays of any kind. Section 3.4 reports that "scatterplot inspection" established linearity, monotonicity, and absence of bivariate outliers, but the scatterplot is not provided, so that assumption check is unverifiable. There is also no descriptive table and no participant-characteristics breakdown: the sample is said to span all four year levels with no counts, and the two measures' distributions are given in prose fragments. Fixing this requires new display material, and until it exists a reader cannot independently assess the reported checks.

**Severity**: Major
**Evidence Anchor**: absence: §4 Results and §3.4 Analysis — expected a descriptive table, a participant-characteristics breakdown, and the scatterplot cited as an assumption check; checked §3.1, §3.4, §4, and all figure and table captions
**Confidence**: 4 — the absence is verifiable; whether this venue would require all three displays or only the figure is an editorial call.

### W5: Seven-section article architecture is disproportionate to a two-paragraph Results

The submission deploys full IMRaD-plus scaffolding — separate Literature Review, Limitations, and Conclusion sections — around one inferential test. The Conclusion restates the Abstract almost claim-for-claim, and the Limitations material would sit more naturally inside the Discussion at this scale. No claim changes if this is restructured; the gain is that the packaging stops signalling more content than exists.

**Severity**: Minor
**Evidence Anchor**: text: §4 Results — "The 214 respondents reported a mean perceived-usefulness score of 3.6 (SD = 0.8) on the five-point scale."
**Confidence**: 4 — section-to-content proportionality is a presentational judgement, well within seat competence but not a bright line.

### W6: Computable quantities are described qualitatively rather than reported

The Results section characterises shared variance as "accordingly modest" instead of reporting the value, and the Abstract omits the confidence interval that Section 3.4 promises to report. In a paper whose entire empirical content is one coefficient, every derivable quantity should appear as a number. This is a clarity fix that changes no claim.

**Severity**: Minor
**Evidence Anchor**: text: §4 Results — "The proportion of variance shared by the two measures was accordingly modest"
**Confidence**: 5 — directly observable on the page.
