## Scoring Plan Dissent

*(none required — my Phase 1 plan for D4 held on contact with the manuscript)*

Wait — per protocol I omit that section entirely. Disregard the heading above; the report begins here.

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: warn
trigger: "generalisations stated more broadly than the study design supports"

The core argument is fully recoverable and the Methods section is exemplary in its operational precision, but the outward-facing surfaces (Abstract, Discussion, Conclusion) restate a two-self-report correlation in behavioural vocabulary, the interpretive frame is invoked without ever being named, and the single implication offered to adjacent practice fields is neither substantiated nor explicitly withheld.

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this as a learning-analytics director who runs the LMS event-log infrastructure and the consent-and-linkage governance at an institution structurally identical to the one described here, and who writes the evidence briefs that decide whether onboarding gets funded. My assigned dimension is whether an adjacent-field reader can enter this paper and leave with a correct understanding, and whether the claims it makes outside its home field are substantiated. That framing turns out to matter, because the paper's home-field bookkeeping is genuinely careful while its outward-facing surfaces are not.

Let me state the seat bias first so the panel can discount it. I am predisposed to say "you had the logs, use the logs," and I want to be clear that perceived usefulness is not a behavioural variable and no volume of event-log data substitutes for it. A perception measure is legitimate on its own terms, and this paper's Literature Review says so more precisely than most papers in this genre manage. My objection is not that the authors measured a perception. It is that they also measured a *second* perception — a self-reported approximation of a quantity their own servers record automatically — and then narrated that choice as a constraint imposed from outside. The distinction between "we chose self-report for reason X" and "use was self-reported rather than measured through system logs" is invisible to a domain insider and glaring to a reader from institutional research, learning analytics, or any adjacent field where the behavioural trace is a routine institutional asset. That is a cross-disciplinary legibility problem, not only a methods problem.

Three of my findings (W2, W4, W5) have consequences on mandatory dimensions I do not own. The unused-log question and the recruitment-channel/dependent-variable coupling bear directly on D1 and D3; I report them here because my seat is where they are visible, and I defer the mandatory scoring to the methodology and DA seats rather than importing them into D4.

One referral outside both my dimension and my competence: every reference in the bibliography carries a DOI under the `10.5555` prefix, which is a reserved test prefix rather than a registered publisher prefix. I cannot adjudicate whether these are real works, and I make no finding on it. The domain seat and the editor should verify.

Finally, on severity calibration: I have assigned no Critical. Applying the singleton test honestly, each defect below is repairable either by rewriting or by adding a justification the authors already possess the information to write, and none of them alone invalidates the narrowly stated association the paper actually claims. Several of them together are what makes this a revision rather than an acceptance, but that joint judgement belongs to the dimension score and to synthesis, not to any individual band.

### S1: Construct discipline stated explicitly, in the right place

The Literature Review does the single most important thing a cross-disciplinary reader needs: it names what the measure is and is not, and commits to that reading. This is stronger than the usual hedge because it is stated as an analytic decision rather than as a caveat, and it cites the divergence literature that motivates it (Vasquez, 2020). An adjacent-field reader who reads only §2 will not be misled about the construct.

**Evidence Anchor**: text: §2, "treat our self-report measure as an indicator of perceived use rather than a behavioral count"

### S2: Sensitivity is made legible rather than assumed

A stated minimum detectable effect at a specified power and alpha lets a reader from any quantitative field judge what the study could and could not have found, without reconstructing the power calculation themselves. In my experience reviewing for learning-analytics venues this is present in a minority of single-site survey papers, and its absence is a routine source of misreading by outside readers who assume a null would have been informative.

**Evidence Anchor**: text: §3.4, "greater than .80 power to detect a correlation of r >= .19 at alpha = .05"

### S3: The reverse pathway is named, not gestured at

Rather than the generic "correlation is not causation" formula, the Discussion specifies the competing causal direction and states that it is equally consistent with the data. This is exactly the sentence an adjacent-field reader needs in order to not over-read the finding, and it is attributed to a source that argues the point.

**Evidence Anchor**: text: §5, "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S4: Unusually honest calibration of a single-site estimate

Framing the point estimate as one draw from a between-institution distribution, rather than as a value to be compared against other studies' point estimates, is the correct epistemic posture for a single-site correlation and is rarely stated this plainly. It is also the framing that most protects outside readers from treating *r* = .42 as a parameter.

**Evidence Anchor**: text: §2, "any single-site estimate is best read as one point in a distribution rather than as a fixed value"

### S5: The ordinal-outcome objection is pre-empted

Reporting a Spearman coefficient alongside the Pearson estimate answers the first question a quantitative reader from an adjacent field would raise about correlating a six-item mean with a five-category ordinal item, and the concordance of the two coefficients is reported rather than merely asserted.

**Evidence Anchor**: text: §4, "The Spearman robustness check yielded a comparable coefficient"

### W1: The outward-facing surfaces restate a self-report correlation in behavioural vocabulary

**Severity**: Major
**Evidence Anchor**: text: Abstract final sentence and §5, "perceived usefulness tracks with LMS engagement among undergraduates" and "one of several factors bearing on engagement"
**Confidence**: 5 — direct textual comparison of the Abstract and Discussion against the operational definition the authors themselves set in §2 and §3.2.

The Methods section defines the outcome as "an ordinal indicator of self-reported use." The Abstract's concluding sentence and the Discussion's summary both convert it to "engagement," which in this literature and in every adjacent field that consumes it denotes behaviour. This is not imprecision at the margin; it is an internal inconsistency located in the two surfaces most often read in isolation. An institutional-research reader who encounters the Abstract in a database will code this as a perception-to-behaviour finding, which is not what was measured. The fix is cheap and mechanical — hold "self-reported use" throughout — but it changes what the paper advertises, which is why I score it Major rather than Minor. I would also ask the authors to reconsider the Introduction's opening move ("students engage with the same system very differently"), which is true and is known to be true *from log data*, and which therefore primes precisely the misreading the rest of the paper works to avoid.

### W2: A design choice with an available alternative is narrated as an external constraint

**Severity**: Major
**Evidence Anchor**: text: §6 Limitations, second point, "LMS use was self-reported through a single item rather than measured through system logs"
**Confidence**: 5 — I operate LMS event-log infrastructure and have built consented survey-to-log linkage studies on the same class of system this institution runs.

The institution runs the LMS. Per-student access frequency in a typical week is not a quantity that requires estimation at this institution; it is a quantity the institution records continuously, and the paper's dependent variable is a self-reported proxy for it. The manuscript cites Vasquez (2020) to establish that self-reports diverge from logs, and then relies on self-report anyway — which is a defensible sequence, but only if the reason is given. Nothing in the manuscript establishes that logs were unavailable, that access was denied, or that the ethics protocol prohibited it. The Limitations sentence is constructed in the grammatical register of an imposed limit ("rather than measured through system logs"), and an adjacent-field reader has no way to tell whether they are reading about an institutional obstacle or an authorial preference.

I want to be precise about what I am asking for, because my seat's characteristic failure is to demand a different and better-resourced study. I am *not* asking the authors to run the log study. I am asking for two or three sentences in §3.1 or §3.2 stating that log-based measurement was considered, what stood in the way, and why the self-report proxy was judged adequate for the question asked. If the answer is "we wanted the respondent's own perception of their use pattern as a construct in its own right," that is a good answer and it belongs in Methods as a design rationale, not in Limitations as an apology. The current framing makes the paper's central measurement choice unauditable, which is why this is Major: the repair is rewriting, but it is rewriting the paper's justificatory core.

### W3: The onboarding implication is advertised as a deliverable and delivered as an unusable hedge

**Severity**: Major
**Evidence Anchor**: text: §5 Discussion, "may be worth institutional attention" and "suggested by, not proven by, the present correlation"
**Confidence**: 4 — I sit in the seat that funds onboarding from evidence briefs and judge what a practitioner can act on; the judgement about actionability is professional rather than textual.

The Abstract promises "implications for LMS onboarding," which elevates this from an aside to a stated contribution and puts it squarely inside my dimension. What arrives is triple-hedged: "modest support," "may be worth," "suggested by, not proven by." Each hedge is individually correct — *r* = .42 between two self-reports at one time point cannot support an onboarding allocation in either direction — and I credit the authors for not pretending otherwise. But the result is a recommendation that no practitioner can act on and that no practitioner can rule out, which is the worst of both positions. The paper does not say which it intends.

The productive repair is not more hedging and not less. It is to state the decision the estimate cannot inform and then name the design that could: pre/post log-based engagement around an onboarding intervention, with the log measure available on the institution's own servers, ideally with a comparison cohort. That single addition would convert an ornamental implication into a genuinely cross-disciplinary contribution — it tells the adjacent field what evidence would move it. I note that the supporting citation here (Whitfield, 2019) is a practitioner account, so the engagement with the practice literature is real but thin; the block threshold on my dimension is "no supporting evidence or engagement," and that threshold is not met, which is why D4 lands at warn rather than block.

### W4: The recruitment channel is the dependent variable's own medium, and the paper treats the consequence as a mean-shift rather than an estimate-shift

**Severity**: Major
**Evidence Anchor**: text: §3.1 and §6, "distributed through the institution's course-announcement channel" and "students who engage more with institutional channels may be overrepresented"
**Confidence**: 4 — sampling-frame/outcome coupling is standard territory in log-linked survey work; the direction of the resulting bias is not determinable from what the paper reports.

The survey was distributed through the course-announcement channel, which at every institution I know of is inside or immediately adjacent to the LMS. Students who rarely open the LMS were therefore structurally less likely to see the invitation. Limitations point four does gesture at this and deserves credit for naming institutional-channel overrepresentation — but it frames the consequence as a representativeness problem, i.e. a caveat about the sample mean. That is not the operative risk. When the probability of being sampled is a function of the dependent variable, the low-use tail is thinned and the *correlation itself* can be biased, not merely the marginal distribution. This is a different mechanism from generic voluntary-response bias and it bears directly on the paper's only quantitative deliverable.

I cannot tell the panel which way it cuts. Range restriction on the outcome would ordinarily attenuate *r*, implying the population value is larger; but if the same mechanism compresses the perceived-usefulness distribution — plausible, since low-use students are likely also low-perceived-usefulness students — the net effect on the coefficient is not sign-determinate. That indeterminacy is the finding. The paper invites comparison of *r* = .42 against prior estimates (via the Song, 2018 distribution framing in §2), and that comparison is unsound until the mechanism is addressed. The strong repair requires the institutional aggregate use distribution — again, data the institution holds — to show how the respondent sample's use profile compares to the eligible population's. The minimum repair is to state the mechanism correctly and to stop treating it as a note about generalisability.

### W5: Consented linkage is never mentioned as a considered and rejected option

**Severity**: Minor
**Evidence Anchor**: absence: §3.3 Procedure and ethics — expected a statement of whether consented survey-to-log linkage was considered and why it was rejected; checked §3.1, §3.3, §3.4, §6, and §7

**Confidence**: 5 — consent-and-linkage data governance is my direct operational responsibility.

Full anonymity is a defensible ethics posture and I do not want it read as an error. But §3.3 presents anonymity as settled fact ("responses could not be linked back to individual students") without registering that a consented-linkage design — respondent opts in to have their survey responses joined to their own log record under an approved protocol — is standard practice, routinely approved, and would have converted this study from a correlation between two self-reports into a correlation between a perception and a behaviour. I am scoring this Minor because what I am asking for is transparency, not a redesign: one or two sentences stating whether the option was considered and on what grounds it was rejected. I flag its secondary value explicitly, because it is easy to miss — that sentence is also the paper's strongest available answer to any common-method-variance objection raised elsewhere on this panel, since it would establish that the shared-method problem was recognised at design time rather than discovered at review.

### W6: The interpretive frame is invoked throughout and never named

**Severity**: Minor
**Evidence Anchor**: text: §1 and §5, "nor do we test a full acceptance model" and "consistent with prior technology-acceptance research"
**Confidence**: 3 — I read the technology-acceptance literature as a consumer of its instruments rather than as a specialist in its historiography.

The paper leans on "technology-acceptance research" and "a full acceptance model" as load-bearing interpretive scaffolding, and never names the model, its originating work, or which of its constructs are and are not in play here. For a domain insider this is harmless shorthand. For the adjacent-field reader my dimension is about, it is a closed door: they cannot determine whether the "perceived usefulness" measured here is the canonical construct comparable across a large literature or an instrument-specific quantity from Costa and Wren (2019). That matters more than usual because the paper's *only* stated contribution is comparability — "an incremental data point, comparable with prior work" — and comparability is unverifiable by an outsider who cannot identify the construct's lineage. I keep this Minor because a diligent reader can chase the instrument through the cited validation study, and because the fix is a named frame plus a foundational citation. Whether the definition offered in §2 is correctly attributed is a domain-accuracy question I leave to that seat.

### W7: No table or figure anywhere, including the distribution needed to audit the headline estimate

**Severity**: Minor
**Evidence Anchor**: absence: §4 Results — expected a frequency table for the five-category self-reported use item plus the bivariate scatterplot referenced in §3.4; checked Abstract, §3.4, §4, §5, and §7

**Confidence**: 4 — routine reporting expectation for an ordinal outcome in this literature.

§3.4 reports that a scatterplot was inspected and that the association was approximately linear and monotonic with no extreme bivariate outliers. The scatterplot is not shown, and the outcome variable's marginal distribution is given only as a median category. An adjacent-field reader is therefore asked to accept the distributional claims on assertion, and — more consequentially — cannot independently assess W4, because the thinness or otherwise of the low-use cells is exactly what a five-row frequency table would reveal. The fix costs the authors nothing: the numbers are already in hand. I score this Minor because document-level figure and table quality belongs to the editor's dimension and because no editor would reject over it; I raise it here only because its cross-disciplinary cost is specific — it removes the outside reader's ability to check the paper's most contestable claim.
