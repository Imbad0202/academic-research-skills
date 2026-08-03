contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
trigger: "Fabricated or non-existent sources, invented or unverifiable domain results presented as established"
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

I took reference verification first, before assessing any substantive claim, because every domain-accuracy judgement about this manuscript is downstream of whether its six sources exist as described. They cannot be confirmed to, and the internal evidence points the other way. All six DOIs sit on the `10.5555` prefix. That prefix is not a publisher prefix at all — it is the registration-agency test prefix used in documentation and sandbox examples. More decisively, and visible without leaving the page: a DOI prefix is assigned per registrant, so six articles in six differently named journals cannot legitimately share one prefix, and the suffixes run sequentially — 2050001 through 2050006 — in reference-list order, one per entry. That is the signature of generated placeholders, not of six independently published papers. The journal names compound the problem: they read as near-misses on real venues (*Computers & Education Review*, *British Journal of Educational Technology Studies*) rather than as indexed titles I can place in the literature, and none of the author–year pairs corresponds to work I recognise in the acceptance tradition, where the relevant instrument-development and multi-campus survey literature is small enough that a reviewer with a decade in this area would expect to.

This is not a citation-hygiene complaint. Every substantive domain assertion in the manuscript routes through these six entries: the definition of perceived usefulness (Costa & Wren, 2019; Delgado, 2020), the provenance and prior validation of the measurement instrument (Costa & Wren, 2019), the reverse-causality caution (Delgado, 2020), the self-report-versus-log caution the limitations section leans on (Vasquez, 2020), the cross-institutional variability claim that licenses the "one point in a distribution" framing (Song, 2018), and the practitioner onboarding implication (Whitfield, 2019). If the citation base is unverifiable, the claim of consistency with prior technology-acceptance research has nothing to be consistent with, the "previously validated" instrument has no traceable validation, and the paper's stated contribution — an incremental, comparable data point — has no map to sit on. I record this as a fatal block under D2 because my Phase 1 fatal condition names fabricated, non-existent, or unverifiable sources presented as established, and because a journal encountering six un-locatable references on a test DOI prefix is facing a research-integrity matter that no revision round resolves on the current record. The empirical work may well be sound; the substantive account built on top of it is not currently trustworthy.

Setting the citation problem aside for the sake of a complete domain reading, the manuscript also has real construct and coverage problems that would need attention even with a clean reference list. The most consequential is an estimand mismatch. In the canonical formulation of this tradition, perceived usefulness predicts behavioural intention, and use sits downstream of intention; the pooled estimates that reviewers in this area carry in their heads are largely perception-to-intention estimates. This paper estimates a direct perception-to-use association and then asserts consistency with that literature without ever naming the collapse or defending it. Under a purely correlational framing the shortcut is defensible as a design choice, but it is not defensible as a *comparability* claim, and comparability is precisely what the contribution rests on. The paper compounds this by asserting consistency without stating any prior estimate at all, so r = .42 is unlocatable — typical, high, or low, the reader cannot tell — a gap made sharper because the manuscript itself invokes Song's cross-campus variability to frame its estimate as one point in a distribution it never describes.

The literature base is also too thin and too narrow to do the work asked of it. Six sources, all 2018–2021, no foundational acceptance-model work, nothing from the UTAUT family, nothing after 2021, and no engagement with learning analytics on behavioural LMS measures — even though the limitations section depends on exactly that literature's central finding. The post-2021 absence is substantive rather than cosmetic: baseline LMS use shifted sharply across 2020–2021, which bears directly on the variance available in a five-point weekly-frequency item and therefore on the magnitude of the correlation this paper reports.

I note two boundary calls. Measurement provenance (W6) touches the methodology seat's territory; I report it as a construct-warrant problem — whether the adapted six items still measure perceived usefulness as this tradition defines it — and leave reproducibility framing to that seat. Whether the theoretical omission also breaks the argument's chain of inference is for the coherence owners; I report only that the domain description is wrong. On my own blind spot: I recognise that the study has practical value for platform administrators, and I am not asking for theoretical elaboration that would break the paper's deliberately narrow frame. My objection is narrower than that. The paper does not need to test a model, but it does need to be able to say what it is consistent with.

### S1: Correlational discipline is maintained consistently, including explicit statement of the reverse pathway

The manuscript does not drift into causal language anywhere, and it names the reverse-causality alternative in its own voice rather than parking it in a limitations list. In a literature where perception–use correlations are routinely narrated as adoption drivers, this restraint is both unusual and correct.

**Evidence Anchor**: text: §5 Discussion, "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"
**Confidence**: 5 — a decade reading acceptance-model discussion sections for exactly this slippage.

### S2: The self-report-versus-behavioural-log limitation is stated plainly rather than buried

The correct domain caution for any self-reported LMS use measure is named in the limitations section without hedging, and the paper does not claim its item is a behavioural count. This is the right posture for a study of this design.

**Evidence Anchor**: text: §6 Limitations, "self-reports of technology use are known to diverge from behavioral traces"
**Confidence**: 4 — familiar with the log-versus-self-report divergence literature and how often it is omitted.

### S3: Single-site estimates are correctly framed as points in a distribution rather than fixed values

The framing of a one-institution correlation as a draw from a between-institution distribution is the appropriate domain move, and it is the framing that makes the study's modest scope coherent rather than apologetic.

**Evidence Anchor**: text: §2 Literature Review, "any single-site estimate is best read as one point in a distribution rather than as a fixed value"
**Confidence**: 4 — prior involvement in meta-analytic synthesis where between-study heterogeneity is the central quantity.

### W1: Entire citation base is unverifiable; all six DOIs sit on a test prefix with sequential suffixes

All six references carry `10.5555` DOIs, which is the registration-agency test prefix rather than any publisher's, and the suffixes increment sequentially in reference-list order. A DOI prefix is assigned per registrant, so six articles in six distinct journals cannot share one legitimately. The journal titles read as near-variants of real venues rather than indexed titles, and no author–year pair maps to work I can place in this literature. Because every domain claim in the manuscript — the construct definition, the instrument's prior validation, the reverse-causality caution, the self-report caution, the cross-campus variability claim, and the onboarding implication — routes through these entries, the paper's substantive account of the field cannot be evaluated as written. This defect alone makes acceptance impossible and is an integrity matter for the editor, not a revision request.

**Severity**: Critical
**Evidence Anchor**: text: §References, first and last entries, "10.5555/2050001" and "10.5555/2050006"
**Confidence**: 5 — reference verification and DOI-prefix administration are routine first-pass work for me.

### W2: Perceived usefulness is defined and positioned as the tradition does not, and the intention step is dropped without acknowledgement

The manuscript gives a paraphrase of the canonical perceived-usefulness definition and attributes it to two recent sources rather than to the foundational work where it originates, then places perceived usefulness as a direct correlate of use. In the canonical formulation, perceived usefulness predicts behavioural intention and use is downstream; the prior estimates a reader would benchmark against are largely perception-to-intention estimates. Estimating a perception-to-use association is a legitimate design choice under a correlational frame, but the paper never names the omitted mediator or defends the shortcut, and it simultaneously claims consistency with the tradition whose estimand it has changed. The comparability plank of the contribution therefore rests on a mis-specified equivalence. Repair requires rewriting the theoretical framing, restoring the correct provenance of the construct, and either justifying the direct path or restating the comparison target.

**Severity**: Major
**Evidence Anchor**: text: §2 Literature Review, "perceived usefulness — the degree to which a person believes a technology will help them perform better", "is among the factors associated with adoption and continued use"
**Confidence**: 5 — the canonical instrument lineage and its mediation structure are my core area.

### W3: The consistency claim is asserted without any stated prior estimate, leaving r = .42 unlocatable

The abstract, discussion, and conclusion all describe the finding as consistent with prior technology-acceptance research, but no prior coefficient, pooled estimate, or plausible range appears anywhere in the manuscript. A reader therefore cannot tell whether .42 is typical, high, or low for this construct pairing in this population, which means "incremental data point" is an assertion rather than a demonstrated location. The gap is sharper because the paper invokes cross-institutional variability to justify reading its estimate as one point in a distribution, then declines to characterise that distribution. Correcting this requires substantive synthesis work: state the prior benchmark, state its estimand, and compare on like terms.

**Severity**: Major
**Evidence Anchor**: absence: §5 Discussion consistency claim — expected a stated prior or pooled effect-size benchmark against which r = .42 is compared; checked Abstract, §2 Literature Review, §4 Results, §5 Discussion, §7 Conclusion, References
**Confidence**: 4 — prior meta-analytic work on acceptance-model predictors gives me the benchmark expectation.

### W4: Literature base omits foundational, UTAUT-family, post-2021, and learning-analytics work the argument depends on

Six sources spanning 2018–2021 carry the entire framing. There is no foundational acceptance literature, nothing from the UTAUT family, nothing published after 2021, and no learning-analytics work on behavioural LMS measures despite the limitations section resting on that literature's central finding via a single citation. The post-2021 omission is substantive: baseline LMS use shifted sharply across 2020–2021, which affects the variance available in a five-point weekly-frequency item and therefore the magnitude of the reported correlation, yet the manuscript neither reports the use-item distribution in enough detail to assess ceiling effects nor discusses the shift. The stated aim of situating the finding against prior findings cannot be met from this base; §2, §5, and §6 need substantial rewriting.

**Severity**: Major
**Evidence Anchor**: absence: §References and §2 Literature Review — expected foundational acceptance-model sources, UTAUT-family work, post-2021 LMS-use studies, and learning-analytics work on behavioral LMS measures; checked all six reference entries, §1 Introduction, §2 Literature Review, §6 Limitations
**Confidence**: 4 — I track this literature's currency and the post-2021 baseline shift directly.

### W5: The cited self-report finding is recast from measurement error into a construct claim

The manuscript converts a reported divergence between self-report and behavioural logs into the claim that self-report studies capture perceived rather than actual engagement. Those are different statements. Divergence means self-report is an error-laden and typically over-estimating proxy for behaviour; it does not establish that self-report validly measures a separate "perceived use" construct. The recasting turns a validity limitation into a definitional move, and it sits inconsistently with the rest of the paper, which describes the item as self-reported use in the abstract and as an ordinal indicator of self-reported use in §3.2. It also leaves an unaddressed consequence: if the outcome is a perception, then pairing it with a perception predictor raises common-method coupling that the paper never discusses. The fix is sentence-level plus a caveat, and it does not change the headline estimate.

**Severity**: Minor
**Evidence Anchor**: text: §2 Literature Review, "studies relying on self-report capture perceived rather than actual engagement"
**Confidence**: 4 — familiar with how the log-comparison literature states its own findings.

### W6: "Previously validated" instrument claim is supported only by an internal-consistency figure, and the adapted items are not reproduced

The abstract asserts a previously validated instrument; §3.2 supports this by noting that the original reported strong internal consistency. Internal consistency is a reliability property, not validity evidence, and in the acceptance-instrument lineage the psychometric warrant for a perceived-usefulness scale rests on established factor structure and convergent–discriminant evidence, not on alpha. Adaptation further suspends whatever validation the original carried until it is re-established in the new context, and no item wording, adaptation rationale, or factor analysis is provided. A domain reader consequently cannot confirm that the six items measure perceived usefulness as the tradition defines it rather than adjacent constructs such as satisfaction or perceived ease of use — which matters because the interpretation of r = .42 depends entirely on what the predictor is. The authors must either publish the items and re-establish measurement or drop the validated-measure claim, which is itself named as part of the contribution in §2.

**Severity**: Major
**Evidence Anchor**: text: Abstract and §3.2, "measured with an adapted, previously validated instrument", "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"
**Confidence**: 4 — construct-validity standards for acceptance instruments are within my direct expertise; reproducibility framing belongs to the methodology seat.
