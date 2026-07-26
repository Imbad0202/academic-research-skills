contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
trigger: "a load-bearing citation is materially misrepresented, such that the paper's substantive contribution as stated cannot stand without the authors correcting the underlying domain content"
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

I read this manuscript as a technology-acceptance specialist checking one thing: whether its substantive claims about the field, its constructs, and its cited prior work are accurate. On the parts of that check concerned with interpretive discipline, the paper performs well above the norm for its tier — I want to say that plainly, because my verdict below is severe and it is not a verdict about the authors' interpretive honesty. The causal-overreach critique that ordinarily dominates reviews of cross-sectional acceptance studies simply does not apply here; the reverse pathway is named in §2, restated in §5, and honoured in the conclusion. I did not find a single instance where the paper claimed more than a correlation licenses.

The failure is elsewhere, and it is structural. This manuscript's stated contribution is not the coefficient — it is the coefficient's *position relative to existing work*. §2 says the study is "intended as an incremental data point, comparable with prior work"; §5 says the result is "consistent with prior technology-acceptance research"; §7 repeats it. That is the whole claim to publishability. And at no point does the paper establish the comparison class against which "incremental" and "consistent" would mean anything. The manuscript's engagement with the domain literature therefore has to bear more weight here than it would in a paper making a stand-alone empirical claim — and it does not bear it.

Three problems compound. First, the construct is used without its origin. "Perceived usefulness" is not a descriptive phrase in this field; it is a defined construct with a specific instrument tradition behind it, and §2's definition is a structural paraphrase of Davis's 1989 formulation while being attributed to two sources dated 2019 and 2020. Davis (1989), Venkatesh and Davis (2000), and the entire UTAUT family are absent. The paper borrows the construct's accumulated authority while citing none of the work that built it. Second, the benchmark that would make "consistent with prior research" a checkable statement is never supplied — not a range, not a meta-analytic estimate, not even the coefficient from any single cited study. Third, and most seriously, I cannot locate the cited literature in the field's corpus at all, for reasons set out in W3.

I want to separate a fourth concern carefully, because it is about domain interpretation rather than design. The paper reads its result as a fact about students. In higher education specifically, LMS access frequency is dominated by course architecture — whether submission, attendance, quizzes, or graded discussion are routed through the platform. §4 concedes this and Ibarra and Poll are cited for it in §2, but the design captures nothing that would let the authors distinguish a perception-driven association from one produced by an uneven distribution of LMS-dependent courses across a self-selected sample. The interpretation offered is therefore stronger, in domain terms, than the collected variables support — not because it overclaims causally, but because it locates the phenomenon in the wrong unit of analysis.

I am explicitly *not* asking for a full acceptance model. The decision to test one association rather than a mediated TAM2/UTAUT structure is defensible and I would not require its reversal. Everything I flag below is fixable without touching the design: correct the attribution, supply the benchmark, resolve the references, collect or at minimum report the course-level context, and either substantiate or withdraw the onboarding recommendation. The empirical finding itself survives all of it. That is why I score D2 `block` rather than `fatal` — but a block it must be, because the contribution as currently stated rests entirely on representations of prior work that I cannot verify and in one case can affirmatively identify as misattributed.

### S1: The reverse-causality pathway is characterised as the field actually holds it

The paper does not merely disclaim causality; it names the specific direction the acceptance literature has documented — that accumulated use raises perceived usefulness — and carries that caution consistently from the literature review into the discussion and limitations. This is the correct domain reading of cross-sectional TAM-lineage data and is more precise than most submissions at this length manage.

- **Evidence Anchor**: text: §2 "students who use a system more may come to perceive it as more useful"

### S2: The dependent variable is reclassified with the field's correct meaning

Having cited the self-report/behavioural-trace divergence, the authors follow through and explicitly reclassify their measure as an indicator of perceived use rather than a behavioural count. This is the technically correct move given the premise, and it is honoured in the abstract, results, and conclusion rather than being stated once and forgotten.

- **Evidence Anchor**: text: §2 "treat our self-report measure as an indicator of perceived use rather than a behavioral count"

### S3: The magnitude is interpreted in domain-appropriate terms

The coefficient is read as moderate, as one factor among several, and with residual variation attributed to curricular structure. This is the correct domain account of what drives LMS access, and it is a marked improvement over the common practice of treating a moderate acceptance correlation as a lever.

- **Evidence Anchor**: text: §4 "reported engagement reflects many influences beyond perceived usefulness"

### W1: The construct's theoretical provenance is misattributed

§2 defines perceived usefulness as the degree to which a person believes a technology will help them perform better and cites Costa and Wren (2019) and Delgado (2020) for it. That definition is a structural paraphrase of Davis's 1989 formulation, which is the source of the construct, its operationalisation, and the item wording that every subsequent instrument in this lineage adapts. Davis (1989), Venkatesh and Davis (2000), and Venkatesh et al.'s UTAUT synthesis are all absent from the reference list. The consequence is not bibliographic tidiness: a reader cannot tell whether the six adapted items measure the TAM construct or something the 2019 source defined independently, and the paper's claim that its instrument is "previously validated" inherits its warrant from a tradition it does not cite. Fix by attributing the definition to its origin, stating explicitly which acceptance-model lineage the adapted instrument descends from, and situating the deliberate decision not to test a full model against that lineage rather than in silence.

- **Severity**: Major
- **Evidence Anchor**: text: §2 "the degree to which a person believes a technology will help them perform better"
- **Confidence**: 5 — I have published comparative work on TAM, TAM2, and UTAUT applications in e-learning and know this construct's provenance directly.

### W2: "Consistent with prior research" is asserted without any effect-size benchmark

The manuscript's contribution rationale is comparability, yet the comparison class is never specified. No prior coefficient, no range, and no meta-analytic estimate for the perceived-usefulness/use relationship in e-learning contexts appears anywhere. A reader cannot determine whether r = .42 is typical, high, or low, which makes "consistent with prior technology-acceptance research" unfalsifiable as written. The problem is sharpened by the paper's own citation practice: §2 invokes Song (2018) for the finding that association strengths vary by institution, without reporting that variation's range — and if the range is wide, a single uncharacterised site is precisely *not* comparable to anything, which undercuts rather than supports the "one point in a distribution" framing. The repair is a short paragraph reporting the published distribution of effect sizes and locating .42 within it, plus Song's actual reported range.

- **Severity**: Major
- **Evidence Anchor**: text: §5 "consistent with prior technology-acceptance research", §2 "association strengths varied by institution"
- **Confidence**: 5 — I have contributed to meta-analytic syntheses of acceptance predictors and know this benchmark literature is both available and standard to cite.

### W3: The cited literature does not correspond to identifiable work in this field

All six references carry DOIs under the `10.5555` prefix, which is a reserved test and example range rather than a live registrant allocation; six of six under that prefix is not a plausible coincidence. Independently, five of the six journal titles are near-miss variants of real titles in this literature rather than the titles themselves — *Journal of Educational Technology Research*, *Computers & Education Review*, *British Journal of Educational Technology Studies*, *Educational Measurement Quarterly*, *Higher Education Practice*. As a specialist who reviews for and publishes in this area, I do not recognise these as journals in the technology-acceptance or educational-technology corpus, and I cannot place any of the six author–year pairs. Because every domain claim the manuscript makes about prior work — the construct definition, the reverse-causality caution, the self-report/log divergence, the cross-campus variability, the instrument's prior validation, and the onboarding recommendation — is sourced exclusively to these six items, none of the paper's representations of the literature can currently be checked. Uncorrected, this alone forecloses acceptance regardless of the study's other properties. I flag it at maximum severity while noting what would resolve it in either direction: independent resolution of all six DOIs and titles against live bibliographic records. If they resolve as real work with transcription errors, this reduces to a correctable citation-accuracy defect; if they do not resolve, the manuscript's entire domain foundation is invented.

- **Severity**: Critical
- **Evidence Anchor**: text: References "10.5555/2050001", "British Journal of Educational Technology Studies"
- **Confidence**: 4 — high familiarity with this field's journal set and with reserved DOI prefixes; short of 5 only because I could not execute live DOI resolution.

### W4: The finding is interpreted as a fact about students when the domain's dominant driver is course architecture

In higher education, how often a student opens the LMS in a typical week is largely determined by whether their enrolled courses route assessment submission, attendance, quizzing, or graded discussion through the platform. The manuscript acknowledges this in §4 and cites Ibarra and Poll (2021) for it in §2, then proceeds to interpret the association as a perception-to-behaviour relationship at the student level. No course-level information was collected: not discipline, not the degree of course-mandated LMS dependence, and not even the year-level breakdown, despite §3.1 asserting that the sample spanned all four year levels. If LMS-dependent courses are unevenly distributed across a self-selected sample — which in a voluntary institutional-channel recruitment is likely — part of the observed association is curricular structure rather than student perception. The interpretation should either be qualified to that effect explicitly, or the covariates collected and reported so the reader can judge.

- **Severity**: Major
- **Evidence Anchor**: absence: Methods §3.2 Measures — expected course-level covariates such as discipline, year level, and course-mandated LMS dependence; checked §3.1 participants, §3.2 measures, §3.4 analysis, §4 results, §6 limitations
- **Confidence**: 4 — direct research experience with LMS adoption in post-secondary institutions, where curricular mandate routinely dominates perception effects on access frequency.

### W5: The onboarding recommendation is not grounded in the implementation literature

§5 suggests that LMS onboarding emphasising concrete usefulness may warrant institutional attention, supported by a single practitioner-facing reference. The higher-education literature on orientation and onboarding interventions — including work reporting null or short-lived effects — is not engaged at all, so the recommendation is not positioned against what is already known about whether such interventions move usage. The hedging in the sentence is appropriate and I am not asking for it to be strengthened; I am asking for the recommendation to be either connected to intervention evidence or dropped, since as written it is the only forward-looking claim in the paper resting on the thinnest citation in the reference list.

- **Severity**: Minor
- **Evidence Anchor**: text: §5 "a possibility also raised in practitioner accounts of digital-environment onboarding"
- **Confidence**: 4 — familiar with the HE implementation and orientation-intervention literature, though it is adjacent to rather than central to my own work.
