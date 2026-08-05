contract_role: domain

## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: block
trigger: "citations to sources that do not support or do not exist as characterised"
block_class: fatal

### D3: argumentative_coherence

score: not_assessed

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

I read this as a learning-technology researcher who has spent time pooling technology-acceptance effect sizes in educational settings, and I want to open by naming my own bias so the panel can discount for it: my instinct on papers like this is to ask for a bigger paper — more constructs, more theory, a fuller model. That instinct is wrong here and I am not acting on it. A single-association, correlationally-worded, single-site study is a legitimate object. The authors' restraint is the best thing about the manuscript, and my blocking concern has nothing to do with scope.

The blocking concern is the reference list. All six entries carry the DOI prefix `10.5555`, with suffixes running consecutively from `2050001` to `2050006`. That pattern is not survivable on its own terms, independent of any judgement about the sources themselves. A DOI prefix is a registrant prefix: it identifies the depositing organisation. Six articles published in six differently-named journals — nominally British, nominally American, across at least four notional publishers — cannot share one registrant prefix, and their suffixes cannot run in an unbroken sequence assigned in reference-list order. Separately, `10.5555` is the prefix that appears in DOI and Crossref documentation as the example/test value; it is not the assigned prefix of any of the publishers implied by these titles. Of the six journal titles, five are one or two words away from real venues in this field — *Computers & Education* appears as "Computers & Education Review", *British Journal of Educational Technology* as "British Journal of Educational Technology Studies", and so on. The sixth, *International Journal of Learning Technology*, does correspond to a real Inderscience journal, but Inderscience deposits under its own prefix (10.1504), not this one. I could not verify a single one of the six records.

This matters far more here than it would in a paper with a broad bibliography, because §2 is *entirely* built from these six items and nothing else. Every domain-level assertion the manuscript makes about the state of the field is sourced only to them: the definition of perceived usefulness (Costa & Wren; Delgado), the caution about cross-sectional inference (Delgado), the claim that association strengths vary by institution (Song), the self-report/log divergence (Vasquez), the practitioner onboarding implication (Whitfield), and the instrument itself (Costa & Wren). Take those six away and there is no literature review, no measurement provenance, and no basis for the paper's only stated contribution — comparability with prior work. That is why I score this dimension as a fatal rather than repairable block: the issue is not a set of malformed DOIs to be corrected in proof, it is that the manuscript's entire factual foundation is currently unverifiable, and the fix is not a revision but a reconstruction of §2 and §3.2 from checkable sources. If the authors can produce verifiable bibliographic records for all six — real DOIs, real volumes, retrievable PDFs — I would revise this judgement immediately and without complaint, and the remaining findings below would stand as a major revision.

Two things reinforce that reading rather than merely coexisting with it. First, the field's canonical lineage is completely absent. The manuscript defines perceived usefulness as "the degree to which a person believes a technology will help them perform better" and attributes this to two sources dated 2019 and 2020. That is Davis's 1989 definition, near-verbatim in substance, and it is the single most-cited definition in this research programme. No UTAUT-generation work appears either. A technology-acceptance manuscript in which no cited source predates 2018 is anomalous on its face; a manuscript that restates a 1989 construct definition as though it originated in 2019 has misattributed the field's central term of art.

Second — and this is where I want to press hardest on the paper's own logic — the manuscript's contribution claim is that it supplies "an incremental data point, comparable with prior work," echoing Song's framing of any single-site estimate as "one point in a distribution rather than as a fixed value." I accept that framing entirely; it is the right way to think about single-site estimates. But it carries an obligation the paper does not discharge. If a distribution exists, the paper must say what it is and where r = .42 sits in it. Pooled meta-analytic estimates for the perceived-usefulness-to-use association in educational technology settings do exist in this literature, and stating a pooled value with its heterogeneity is standard practice for exactly this kind of positioning claim. The manuscript states no comparison quantity anywhere — not a pooled r, not a range, not even the effect sizes of the individual studies it cites. "Effect sizes vary across samples and instruments" is the closest it comes, and that sentence is unfalsifiable as written. As a result the claim "consistent with prior technology-acceptance research," repeated in the abstract, §5, and §7, cannot be evaluated by a reader or by me. The incremental-data-point claim does not survive the test; it collapses into an assertion of consistency with an unspecified benchmark.

On the construct question I flagged going in: I am not persuaded that perceived usefulness and self-reported use are operationally distinct in this design. Six Likert items and one Likert-format frequency item, same instrument, same occasion, same response mode, same latent favourability toward the platform plausibly driving both. The manuscript itself concedes the second measure is a perception — it says it treats self-report "as an indicator of perceived use rather than a behavioral count," which is the honest and correct move — but it never confronts the consequence, which is that r = .42 is then an association between two self-perceptions collected together, and common-method variance is a live rival explanation for a coefficient of exactly this magnitude. No discriminant-validity evidence is offered, no marker variable, no method check. The abstract's closing sentence then quietly reinstates the stronger reading by describing the result as evidence about "LMS engagement," which is not what a single perceived-frequency item measures.

The missing institutional context compounds this. The LMS is never named, its version is never given, and the institution's usage policy is never described. In LMS research this is not incidental reporting — it is the interpretive frame. If assignment submission, quiz delivery, or grade release runs through the platform, then "how often do you access the LMS in a typical week" is partly an index of compulsion and course workload, not of voluntary engagement, and the meaning of the association changes materially. The manuscript is in fact aware of this mechanism, because §4 attributes residual variance to "course requirements and assessment schedules" — but it measured none of that, and it reports nothing about whether the platform is mandatory. The minimum required here is small and cheap: name the platform, state whether it is the required channel for submission and grades, and state whether any course-level LMS activity was compulsory during the survey window.

Let me be equally clear about what is right. The correlational discipline is real and consistently maintained, including an explicit statement that the reverse pathway is equally consistent with the data — a sentence many published papers in this area still will not write. The Spearman check is the appropriate robustness move for an ordinal outcome and its result is reported rather than merely asserted. The sensitivity statement is framed as a detectable-effect floor rather than as post hoc power, which is the correct form. And the internal arithmetic checks out: the sample reconciliation reconciles, and the reported 95% CI [.30, .52] is what a Fisher-z interval on r = .42 with n = 214 actually returns. Those are not trivial virtues. My recommendation is not that this become a larger paper. It is that a correct small paper needs a verifiable evidence base, a stated benchmark for its comparability claim, and enough context to know what its outcome variable is measuring.

### W1: The entire six-item reference base is unverifiable and bears a test DOI prefix with sequential suffixes

**Severity**: Critical
**Evidence Anchor**: `text: § References — "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006"`
**Confidence**: 5 — direct inspection of the DOI pattern plus routine familiarity with registrant-prefix structure and with the actual venue names in this literature.

Six ostensibly independent articles across six differently-named journals share one DOI prefix and carry suffixes in unbroken reference-list order; the prefix is the documentation/test example value, not any publisher's registrant prefix. Five of the six titles are near-misses of real venues; the one real title (Inderscience's *International Journal of Learning Technology*) does not deposit under this prefix. Because §2, §3.2, §5, and the contribution claim all rest exclusively on these six items, nothing the manuscript says about the field or about its own instrument can currently be checked. This finding alone, uncorrected, makes acceptance impossible: it is not a formatting defect but the absence of a checkable factual foundation.

### W2: Canonical lineage absent and the field's central construct definition misattributed to 2019–2020 sources

**Severity**: Major
**Evidence Anchor**: `absence: §2 Literature Review — expected citation of the canonical perceived-usefulness source and of existing pooled LMS-acceptance estimates; checked §1, §2, §5, §7, and the reference list`
**Confidence**: 5 — this is the lineage I work in; the omission is unambiguous.

The perceived-usefulness definition offered in §2 is substantively Davis's 1989 formulation but is sourced to two 2019–2020 references. No UTAUT-generation work and no existing synthesis of LMS acceptance appears anywhere, and no cited source predates 2018. As written, §2 does not situate the study in its research programme; it paraphrases a founding construct as though it were recent secondary commentary. Repair requires rebuilding the literature review around the actual lineage, which is substantial rewriting, but the reported association itself survives.

### W3: The incrementality claim is asserted without any stated benchmark, making "consistent with prior research" unevaluable

**Severity**: Major
**Evidence Anchor**: `text: §2 and §5 — "effect sizes vary across samples and instruments", "consistent with prior technology-acceptance research"`
**Confidence**: 5 — I have pooled effect sizes in this exact literature; the omission of any comparison quantity is decisive for the claim as stated.

The manuscript's sole contribution claim is that it adds one comparable data point to a distribution. It never states the distribution: no pooled estimate, no range, not even the coefficients of the studies it cites. Consequently "consistent with prior technology-acceptance research" cannot be assessed, and r = .42 cannot be located as high, low, or typical. This is independent of W2 — a paper could cite the canonical lineage and still omit the benchmark — and it directly undercuts the paper's stated reason for existing. Fixing it requires retrieving and reporting pooled values and re-writing the positioning in §2, §5, and §7.

### W4: Perceived usefulness and self-reported use are not shown to be operationally distinct, leaving common-method variance as a live rival explanation

**Severity**: Major
**Evidence Anchor**: `text: Abstract — "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates."`
**Confidence**: 4 — strong basis in acceptance-research measurement practice; I cannot rule the concern out or in without seeing the item wording.

Both variables are Likert self-reports collected in one instrument on one occasion, and the manuscript itself characterises the use item as a perception rather than a behavioural count. No discriminant-validity evidence, marker variable, or method check is reported, so a single undifferentiated favourability toward the platform remains a viable account of r = .42. The abstract then upgrades the finding to evidence about "LMS engagement," which the measure does not support and which contradicts the paper's own framing in §2 and §6. Addressing this needs either a validity check or a behavioural criterion — new analysis or new data — while the descriptive association survives.

### W5: The LMS is never named and the institution's usage policy is never reported, leaving the outcome variable's meaning undetermined

**Severity**: Major
**Evidence Anchor**: `absence: §3.1 and §3.2 — expected the platform identity and version plus the institution's mandatory-use policy for assignment submission and grade release; checked §1, §3, §4, §6`
**Confidence**: 5 — standard reporting expectation in LMS-specific research.

If the platform is the required channel for submission, quizzes, or grade release, the weekly-access item indexes compulsion and course workload as much as engagement, and the association's substantive meaning changes. The manuscript implicitly invokes this mechanism in §4 while reporting none of it. The required disclosure is minimal — platform, version, mandatory-use status, any compulsory LMS activity during the three-week window — but without it the outcome variable cannot be interpreted, so interpretation across §4, §5, and §7 must be revised once supplied.

### W6: "Previously validated" is claimed for an adapted six-item scale on the strength of internal consistency alone

**Severity**: Major
**Evidence Anchor**: `text: §3.2 — "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"`
**Confidence**: 4 — firm on the psychometric point; the provenance question is entangled with W1.

Validity is not transitive across adaptation, population, or platform, and Cronbach's α = .88 evidences internal consistency, not construct validity. No item wording is shown and no account is given of what was adapted or why, so a reader cannot tell whether the field's perceived-usefulness construct was measured at all — which is precisely what W4 turns on. The abstract's description of the measure as "previously validated" therefore overstates the available evidence. This overlaps the methodology seat's remit on reporting completeness; my point is the domain-specific misuse of "validated."

### W7: Residual variance is attributed to specific unmeasured factors

**Severity**: Minor
**Evidence Anchor**: `text: §4 — "consistent with the view that reported engagement reflects many influences beyond perceived usefulness, including course requirements and assessment schedules"`
**Confidence**: 4 — clear on the record; the claim is hedged, which limits its impact.

Course requirements and assessment schedules were not measured, and the only cited support for their relevance is one of the unverifiable references. The sentence is appropriately hedged ("consistent with the view that"), so it does not change any core claim, but naming specific mechanisms the design cannot speak to should either be dropped or explicitly labelled as conjecture.

### W8: The shared-variance statement is qualitative where a number is available

**Severity**: Minor
**Evidence Anchor**: `text: §4 — "The proportion of variance shared by the two measures was accordingly modest"`
**Confidence**: 5 — straightforward reporting point.

With r = .42 the shared variance is approximately 18%, which the manuscript could simply state. Describing it as "modest" without the figure invites the reader to supply their own scale, and in a paper whose contribution is a single reported quantity, the derived quantity should be reported too. Purely a clarity gain; no claim changes.

### S1: Correlational discipline is maintained, including explicit acknowledgement of the reverse pathway

**Evidence Anchor**: `text: §5 — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`

The manuscript does not drift into causal phrasing anywhere, and it states the reverse-causal reading as equally consistent rather than burying it in a limitations list. This is better practice than much of the published acceptance literature and should be preserved verbatim through revision.

### S2: The ordinal robustness check is appropriate and its result is reported

**Evidence Anchor**: `text: §4 — "The Spearman robustness check yielded a comparable coefficient (ρ = .40)"`

Given a five-point frequency outcome, a rank-based check is the right move, and reporting ρ rather than merely asserting robustness lets the reader verify that the parametric assumption is not doing the work.

### S3: Reported quantities are internally consistent and reproduce on inspection

**Evidence Anchor**: `text: §3.1 and §4 — "14 incomplete submissions and 5 duplicate entries were removed, leaving 214 valid responses", "r = .42, 95% CI [.30, .52], p < .001, n = 214"`

The sample accounting reconciles from 233 to 214, and the reported interval is what a Fisher-z transformation on r = .42 at n = 214 returns. Whatever the problems with the evidence base, the manuscript's own arithmetic is trustworthy.

### S4: The self-report measure is correctly characterised as a perception rather than a behavioural count

**Evidence Anchor**: `text: §2 — "treat our self-report measure as an indicator of perceived use rather than a behavioral count"`

This is the correct construal and it is stated in advance of the results rather than retrofitted in the limitations. My objection in W4 is that the abstract does not hold this line, not that the line is wrong.

### S5: Sensitivity is framed as a detectable-effect floor rather than as post hoc power

**Evidence Anchor**: `text: §3.4 — "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05 (two-tailed)"`

Stating the smallest effect the design could detect, rather than computing power on the observed coefficient, is the defensible form of this statement and is worth keeping.
