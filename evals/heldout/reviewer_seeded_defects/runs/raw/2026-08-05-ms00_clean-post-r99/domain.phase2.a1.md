## Scoring Plan Dissent

*(none — omitted per protocol)*

Wait — that placeholder is itself a protocol violation. Corrected output follows.

contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
block_class: fatal
trigger: "cited sources that do not support anything attributed to them or appear not to exist"

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript as a higher-education educational-technology researcher who works on exactly this association: perceived usefulness and system use, in post-secondary settings, synthesized across studies. My remit is correspondence to the field's evidence base — not elegance, not organisation, not whether the survey was competently run.

The paper is, in its own voice, admirably restrained. It refuses causal language, flags the reverse pathway, flags the self-report/log gap, and offers itself as "an incremental data point, comparable with prior work." That framing is the right one for a single-site correlational survey, and I want to be clear that I am not rejecting the paper for being modest. Modest is fine. Unverifiable is not.

The problem is that every domain claim in this manuscript — the definition of the focal construct, the provenance and validation of the instrument, the measurement caution, the multi-campus distributional claim that licenses the paper's entire contribution framing, and the "consistent with prior research" verdict — rests on six references, all of which carry DOIs under the prefix `10.5555`. That prefix is the DOI Foundation's reserved range for test and example DOIs; no operating journal registers content under it. The six are numbered sequentially, `2050001` through `2050006`, in reference-list order. The journal titles are near-misses for real venues rather than real venues. And no source in the list is one that any competent search of this literature would fail to return: there is no Davis (1989), no Venkatesh et al. (2003) or (2012), no Šumak et al. (2011), no Scherer et al. (2019), no meta-analysis of any kind, and nothing published after 2021 in a literature that has continued to accumulate heavily since. Taken singly, any one of these signals could be an editing artefact. Taken together — reserved test prefix on 6/6, sequential numbering, fictitious-looking venues, and a canonical-omission pattern that no genuine engagement with this literature could produce — the reference base cannot be treated as a factual account of prior work. My Phase 1 fatal trigger named this case explicitly, and I am bound by it.

This matters beyond bibliographic hygiene, and I want to spell out the mechanism rather than assert it. The paper's contribution claim is not "here is an association" but "here is one point in a distribution." A point is only interpretable against the distribution's location. The paper never states one. The single source that supposedly establishes distributional variation (Song, 2018) is unverifiable, and the synthesis literature that could actually supply the benchmark is absent. So r = .42 is not merely a modest finding — it is an unevaluable one. And when I supply the benchmark myself from the literature the paper omits, the comparison turns adverse rather than neutral: pooled TAM estimates place perceived usefulness → behavioural intention substantially higher than perceived usefulness → *actual* use, with the latter commonly in the .2–.3 region and further attenuated when use is measured behaviourally rather than by self-report. A self-reported-use correlation of .42 therefore plausibly sits *at or above* the log-based pooled estimate, which is what common-method variance predicts. That is a finding worth reporting — but the paper reports the opposite reading ("consistent with"), without stating which quantity it is consistent with.

Third, and independent of the citation problem: "how often did you access the LMS in a typical week" is not the construct that this literature calls use. The field distinguishes access frequency, session duration, depth of feature engagement, and assessment-driven compliance use, and these behave differently against perceived usefulness — compliance-driven access is precisely the case where usefulness perceptions decouple from behaviour. The paper's own Results paragraph concedes as much when it attributes residual variance to "course requirements and assessment schedules." A single access-frequency item is therefore not commensurable with whatever "engagement" the compared studies measured, so the Discussion's alignment with Costa & Wren and Ibarra & Poll is not apples-to-apples even on the paper's own terms.

One observation I forward rather than score, because it sits in the methodology seat's remit: the frequency item's response anchors are given only for categories 1 and 5, so the reported median category "a few times per week" cannot be checked against the scale as described.

### S1: Reported quantities are internally consistent and arithmetically correct
The confidence interval is not decorative. For r = .42 with n = 214, the Fisher-z interval is [.303, .525], which rounds exactly to the reported [.30, .52]. The power statement is likewise correct to rounding: n = 214 at α = .05 two-tailed detects r ≈ .19 at 80% power (the exact requirement for r = .19 is n ≈ 215, so "greater than .80" is optimistic by a hair, not wrong). Whatever else is wrong here, the arithmetic of the paper's own data is sound, and that is not universal in submissions of this type.
**Evidence Anchor**: `text: §4 ¶2 "r = .42, 95% CI [.30, .52], p < .001, n = 214"`

### S2: The self-report/behavioural-log caution is a correct statement of the field's position
The claim that self-reported technology use diverges from log traces is accurate domain knowledge, and the paper follows it through consistently — treating the measure as an indicator of *perceived* use in the Literature Review, the Measures section, and the Limitations. The divergence direction and its interpretive consequence are stated as the literature actually has them. The accuracy of this content is independent of whether the attached citation is verifiable.
**Evidence Anchor**: `text: §2 ¶2 "self-reported estimates of technology use diverge, sometimes substantially, from behavioral log data"`

### S3: Claim strength is calibrated to the design throughout
The reverse-causation pathway is named rather than buried, the practical implication is explicitly marked as unproven, and the Conclusion does not upgrade the correlation. In a literature with a long history of cross-sectional acceptance studies drifting into causal phrasing, this discipline is genuine and should survive any revision.
**Evidence Anchor**: `text: §5 ¶2 "though this implication is suggested by, not proven by, the present correlation"`

### S4: The ordinal use item is handled as ordinal
Reporting Spearman alongside Pearson, and stating both coefficients, is the field-appropriate treatment of a five-point single-item indicator, and the near-identity of ρ = .40 and r = .42 is reported without overclaiming what the check establishes.
**Evidence Anchor**: `text: §4 ¶2 "The Spearman robustness check yielded a comparable coefficient (ρ = .40)"`

### W1: The entire reference base is unverifiable and bears the DOI Foundation's reserved test prefix
All six references resolve to `10.5555/205000X`, sequentially numbered in list order. `10.5555` is the reserved prefix for test and example DOIs; it is not assigned to publishers. The venue names are plausible-sounding variants rather than identifiable journals, and no author in the list appears in the canonical corpus of this literature. Because every domain claim in the manuscript — construct definition, instrument provenance and validation, measurement caution, distributional benchmark, and the consistency verdict — is sourced only here, there is no verifiable factual content about prior work anywhere in the paper. This is not repairable by revising text: it requires rebuilding the literature base from scratch and re-establishing what instrument was actually administered, which may in turn invalidate the measure the data were collected with.
**Severity**: Critical
**Evidence Anchor**: `text: §References, first and last entries "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"`
**Confidence**: 5 — the reserved test-prefix range is a matter of public record, and I verify reference lists in this specific literature as routine practice.

### W2: No canonical, meta-analytic, or post-2021 source is engaged in a saturated literature
Perceived usefulness and system use is one of the most heavily synthesized associations in educational technology. Pooled estimates exist, moderator analyses exist, and the intention-versus-use distinction is settled enough to be taught. A manuscript that positions itself against "prior technology-acceptance research" while citing no foundational source, no synthesis, and nothing from the last four years cannot demonstrate that its association is either consistent with or additive to that body of work. The remedy is not "add citations" cosmetically: the omitted sources are the ones that would determine whether this paper has anything to add.
**Severity**: Major
**Evidence Anchor**: `absence: §2 Literature Review and §References — expected at least one foundational acceptance-model source and one meta-analytic or systematic-review source, plus any work published after 2021; checked §1 Introduction, §2 Literature Review, §5 Discussion, §7 Conclusion, §References`
**Confidence**: 5 — this is the literature I synthesize professionally.

### W3: The field's canonical definition of perceived usefulness is attributed to recent secondary sources
The definition offered is, in substance, the standard TAM formulation of perceived usefulness — belief that using a system enhances performance — but it is attached to 2019 and 2020 sources and introduced with a diachronic claim ("has long proposed") that no source in the list is old enough to support. Misplacing the provenance of the focal construct is a domain-accuracy error in its own right, and it compounds W2: a reader cannot tell whether the authors are using the construct as the tradition defines it or as an unverifiable intermediary paraphrased it.
**Severity**: Major
**Evidence Anchor**: `text: §2 ¶1 "the degree to which a person believes a technology will help them perform better"`
**Confidence**: 5 — the definitional wording is close enough to the canonical formulation to identify unambiguously.

### W4: "Consistent with prior technology-acceptance research" is asserted without any benchmark, and conflates two different pooled associations
No comparison value, interval, or range is given anywhere in the paper, so consistency is unevaluable as written. Worse, the claim does not distinguish perceived usefulness → behavioural intention from perceived usefulness → use, which differ materially in the synthesis literature, nor self-reported use from log-measured use, which differ again. Supplying the missing benchmark reverses the direction of the inference: r = .42 against a self-reported access measure plausibly sits at or above log-based pooled estimates, which is a common-method-variance story, not a corroboration story. The paper's central comparative claim therefore may be not merely unsupported but backwards.
**Severity**: Major
**Evidence Anchor**: `text: §5 ¶1 "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)"`
**Confidence**: 4 — pooled magnitudes are recalled as ranges rather than exact values, but the intention/use and self-report/log orderings are robust.

### W5: The "use" construct is not the construct the comparison studies measure
Weekly access frequency captures neither depth of feature use, nor session duration, nor the assessment-compliance pathway that dominates LMS access in many course designs. Since the paper's contribution is explicitly comparative ("comparable with prior work"), construct commensurability is load-bearing, not incidental. The Results paragraph already attributes residual variance to course requirements and assessment schedules, which is a description of exactly the confound that makes access frequency a poor proxy for engagement. Either the construct claim must be narrowed to access frequency specifically, with comparisons restricted to studies using that operationalisation, or a richer use measure is required.
**Severity**: Major
**Evidence Anchor**: `text: §3.2 "how often the respondent accessed the LMS in a typical week"`
**Confidence**: 5 — the use-construct taxonomy and its consequences for effect magnitude are standard in this literature.

### W6: "Previously validated instrument" inherits validation across adaptation and substitutes reliability for validity
The Abstract's warrant for construct measurement is that the instrument was previously validated; the Methods reveal that it was *adapted*, and the only psychometric evidence offered in-sample is Cronbach's α = .88. Internal consistency is not validity, and validation does not transfer intact across adaptation — particularly when neither the item wording nor the nature of the adaptation is reported. With the source instrument itself unverifiable (W1), the paper has no established warrant that the six items measure perceived usefulness as the field defines it. Either item-level content and factorial evidence must be supplied, or the "validated" claim must be withdrawn, which leaves the construct-measurement warrant open.
**Severity**: Major
**Evidence Anchor**: `text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument"`
**Confidence**: 4 — the reliability/validity distinction is unambiguous; my uncertainty concerns only how much undisclosed validity evidence might exist.

### W7: The paper claims the "technology acceptance" label without naming or engaging any acceptance model
The keywords, Literature Review, and Discussion all invoke technology acceptance as the paper's home literature, while the Introduction disclaims testing "a full acceptance model" and no model is ever named. Using the field's terminology as a positioning label without identifying which framework is meant is loose usage that will mislead readers about what tradition the .42 belongs to. Repairable in place by naming the framework the perceived-usefulness construct is drawn from and stating explicitly which of its paths this study does and does not address.
**Severity**: Minor
**Evidence Anchor**: `text: §1 ¶2 "nor do we test a full acceptance model"`
**Confidence**: 5 — terminological, directly checkable against the text.

### W8: Shared variance is described verbally rather than reported as r²
Field convention for a correlational contribution of this kind is to report r² explicitly so readers can place the result without recomputing. The paper instead offers a qualitative characterisation ("modest"), twice. The value is trivially derivable — roughly 18% — but leaving it implicit while making comparative claims about magnitude is a reporting shortfall that also makes the unbenchmarked consistency claim in W4 harder for a reader to interrogate.
**Severity**: Minor
**Evidence Anchor**: `text: §4 ¶2 "The proportion of variance shared by the two measures was accordingly modest"`
**Confidence**: 5 — reporting convention, directly checkable.
