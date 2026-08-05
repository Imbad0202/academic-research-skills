# Field Analysis Report

## Paper Basic Information

- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~165 words
- **Full text length**: ~1,850 words excluding references (Methods is the longest section at ~450 words; Results ~200 words)
- **Number of references**: 6
- **Language**: English (review should be conducted in English)

---

## ⚠️ Pre-Configuration Integrity Flag

Before the reviewer cards, one observation that materially shapes how the team should be configured. I am reporting this as a pattern requiring verification, **not** as an established finding:

All six references share the DOI prefix `10.5555` with sequential suffixes (`2050001`–`2050006`). `10.5555` is a reserved test/example prefix, not an allocated publisher prefix. The six journal titles also read as near-misses of real journals (*Computers & Education Review*; *British Journal of Educational Technology Studies*; *Educational Measurement Quarterly*). Additionally, a technology-acceptance paper whose central construct is perceived usefulness cites none of the canonical sources for that construct.

**Implication for configuration**: reference verification cannot be left as an incidental check. I have assigned it explicitly to the Journal-Fit Reviewer (editors own reference screening) and flagged it as a cross-cutting instruction in the Review Strategy section. If verification confirms the pattern, it dominates every other finding and the review's structure changes — so it must be resolved first, not folded into a list of minor points.

---

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| **Primary Discipline** | Educational technology in higher education — specifically learning-platform adoption and student engagement |
| **Secondary Disciplines** | (1) Information systems / technology-acceptance research (TAM–UTAUT lineage); (2) educational measurement and psychometrics (scale adaptation, self-report validity); (3) learning analytics / institutional research (the log-data counterfactual the paper raises but does not use) |
| **Research Paradigm** | Quantitative — descriptive and correlational. Explicitly non-model-testing; the authors decline to fit an acceptance model and frame the study as a single bounded association. |
| **Methodology Type** | Cross-sectional survey, single site, single time point. Analysis is bivariate: Pearson *r* with Spearman robustness check, 95% CI, power statement. No multivariate modelling, no covariates, no subgroup analysis (year level was collected but never used). |
| **Target Journal Tier** | **Reporting discipline reads Q1–Q2; contribution supports Q3–Q4 or a short-report slot.** Rationale: the *reporting* is unusually disciplined for this genre (CI reported, causal language withheld throughout, robustness check performed, limitations pre-empt the obvious objections). But the *substance* is one bivariate correlation, a single-item dependent variable, a single institution, and six references — below the contribution threshold of any Q1 educational-technology journal, which would desk-reject for insufficient novelty. The gap between polish and payload is the paper's defining feature and should shape the whole review. |
| **Paper Maturity** | **Pre-submission in polish, under-developed in scope.** Structure is complete, citation format is internally consistent, prose is clean and hedged. But the content is a research note wearing a full-article structure: seven sections and a two-paragraph Results. Also missing: no instrument appendix, no item wording, no response rate (eligible population size never stated), no description of the LMS platform or how courses used it. |

---

## Recommended Target Journals (Top 3)

1. **Research in Learning Technology** (ALT, open access) — the closest editorial-ethos match. It explicitly welcomes bounded single-institution empirical reports and does not require theoretical novelty as an entry condition. The paper's honest-limitations framing fits its house style. Best odds of the three.

2. **Education and Information Technologies** (Springer) — publishes a very high volume of LMS/TAM survey work, including single-site samples. Plausible on fit and volume, but reviewers there will almost certainly demand either the full construct set or multivariate analysis, because the journal's own back catalogue makes a single-path bivariate estimate look thin by comparison.

3. **Contemporary Educational Technology** or **Journal of Information Technology Education: Research** (Q3) — appropriate homes for an avowedly incremental data point, with review expectations calibrated to that ambition.

**Format recommendation independent of venue**: this manuscript is better positioned as a *Research Note* / *Brief Report* than as a full article. Reframing would convert its main weakness (thin payload behind full-article scaffolding) into a genre fit, and would make the modest claim structurally honest rather than merely verbally hedged. The Journal-Fit Reviewer should evaluate this explicitly.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of *Research in Learning Technology*, previously a desk-screening editor for LMS and technology-acceptance submissions at *Education and Information Technologies*. Has desk-rejected several hundred single-site TAM correlational manuscripts and maintains the journal's reference-integrity screen. Specializes in judging where the line falls between "legitimately incremental" and "insufficient to constitute a contribution."

**Review Focus**:
1. **Reference-base integrity and adequacy — resolve first.** Verify all six references against Crossref/DOI resolution, including the `10.5555` prefix pattern and the sequential suffixes. Separately from authenticity: assess whether six references, none later than 2021, can sustain a literature review for a construct with a forty-year research base. Note the absence of the canonical acceptance literature.
2. **Contribution threshold and genre fit.** Does one bivariate association from one site clear the bar for a full research article at any credible venue? Assess the *Research Note* reframing explicitly: what would the paper need to become a good note versus a weak article, and does the current seven-section structure oversell a two-paragraph Results?
3. **Reader-interest test.** For the configured journal's readership — learning technologists, institutional practitioners, ed-tech researchers — what is the takeaway a reader could act on or cite? If the honest answer is "confirmation of something already meta-analysed," say so plainly.

**Will particularly care about**: Whether the manuscript's careful hedging is functioning as scholarly integrity or as a substitute for contribution. Sentences like "offered as an incremental, design-bounded contribution" are epistemically correct and simultaneously unfalsifiable — being unarguable is not the same as being publishable.

**Possible blind spots**: May over-index on novelty and undervalue genuinely well-calibrated small-scope work — the field arguably needs more papers that refuse to overclaim, and a novelty-first editor can punish exactly that virtue. Will also likely skip the psychometric detail (single-item ordinal DV, adaptation validity), leaving it entirely to Reviewer 1.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative methodologist in educational measurement with a psychometrics doctorate, specializing in self-report measurement validity, single-item versus multi-item indicators, and the treatment of coarse ordinal variables in correlational designs. Regularly serves as statistical reviewer for education journals and has published on attenuation of correlations under categorical measurement.

**Review Focus**:
1. **The single-item ordinal dependent variable.** A five-category self-report item has unknown reliability and no internal-consistency estimate — yet it carries half of the headline correlation. Two consequences must be addressed: (a) coarse categorization attenuates *r* downward, so .42 is a floor not a point estimate; (b) single-item unreliability attenuates it further and in an unquantifiable amount. Also: Spearman is not the right robustness check for a five-category ordinal variable against a continuous mean score — polyserial correlation is. The authors chose a check that cannot detect the problem it purports to address.
2. **Validity of the adapted instrument.** "Adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency" transfers a validity claim from the original to the adaptation without evidence. What was changed in adaptation? α = .88 establishes internal consistency only — no factor analysis, no CFA, no evidence the adaptation preserved the original structure. Items are not reproduced anywhere, so no reader can evaluate them.
3. **Sample inference and the power statement.** Response rate is uncomputable: 233 received and 214 retained, but the eligible undergraduate population is never stated, so nonresponse bias cannot be bounded even descriptively. The power statement ("greater than .80 power to detect *r* ≥ .19") is written as though a priori but is indistinguishable from post-hoc rationalization of the achieved *n*; the manuscript should state whether the target *n* was set before collection.
4. **Common-method variance.** Both variables were measured by self-report, in one instrument, at one sitting, with adjacent items. This inflates the observed association by an unknown amount and pushes in the opposite direction from the attenuation in point 1. The paper discusses neither, so the true magnitude is bracketed by two unquantified biases of opposing sign — which should be stated.

**Will particularly care about**: That *r* = .42 is reported to two decimals with a tight CI as though it were a precise estimate, when coarse measurement and common-method variance make its absolute magnitude non-interpretable. The CI quantifies sampling error only, and the paper's precision presentation implies more than the design delivers.

**Possible blind spots**: May demand SEM or multivariate modelling that 214 cases and two constructs cannot support — the fix for a thin design is not always a bigger model. Will not judge whether the study is worth doing at all, only whether it is executed correctly.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior higher-education researcher specializing in LMS adoption and student engagement, with a decade of work on the TAM→UTAUT lineage and its critics. Familiar with the existing meta-analytic evidence on LMS acceptance and with the standing critique that TAM's explanatory value in educational settings has plateaued.

**Review Focus**:
1. **Absent canonical literature and missing meta-analytic benchmark.** The foundational sources for perceived usefulness and for LMS acceptance specifically are entirely absent. This matters beyond citation etiquette: pooled estimates for precisely this association already exist. Without positioning *r* = .42 against that distribution, the claim "consistent with prior technology-acceptance research" is untestable — the paper never states what value would have been *inconsistent*.
2. **Theoretical positioning of a deliberately atheoretical study.** The paper declines to test a model while adopting that model's central construct. This is a defensible choice but is never justified: is this a partial replication, a benchmarking exercise, or atheoretical description? What is gained by isolating one path from a framework whose value lies in the joint structure of its constructs?
3. **The self-undercutting contribution claim.** The literature review cites Song (2018) to argue that any single-site estimate is "one point in a distribution rather than a fixed value" — then the paper delivers a single-site estimate without supplying the distribution to place it in. The manuscript states the reason its own contribution is limited and does not resolve it. This is the sharpest internal tension in the paper and the authors should be asked to answer it directly.
4. **Missing institutional context.** No description of which LMS, how courses used it, whether use was mandated, or how assessment was integrated. The paper itself invokes Ibarra and Poll (2021) to argue that course design, instructor expectations, and assessment structure shape both perception and use — and then reports neither. Without it, the finding cannot be compared to any other site, which is the only thing an incremental data point is for.

**Will particularly care about**: Whether the field learns anything it did not already know. And whether the limitations framing has become argumentatively load-bearing — pre-emptively naming a weakness is not the same as addressing it, and this manuscript names nearly every weakness it has without fixing any of them.

**Possible blind spots**: May be reflexively dismissive of small incremental work per se, which would be a category error rather than a judgement. Likely to undervalue the local, practice-side utility of a bounded finding for the institution that produced it.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Director of Learning Analytics at a research university, jointly appointed in institutional research, with responsibility for LMS event-log infrastructure, consent-and-linkage data governance, and the evidence briefs that inform platform procurement and onboarding budgets. Reviews for learning-analytics venues and has built consented survey–log linkage studies on the same infrastructure this paper's institution would have.

**Review Focus**:
1. **The log data existed and was not used.** The institution runs the LMS; per-student access events are on its own servers and the paper's own dependent variable ("how often did you access the LMS in a typical week") is a direct self-report proxy for a metric already recorded automatically. The paper cites Vasquez (2020) to establish that self-reports diverge from logs, and then relies on self-report anyway. This should be treated as a **design decision requiring justification, not a limitation requiring apology.** The Limitations section presents it as an external constraint ("use was self-reported... rather than measured through system logs") when the manuscript gives no evidence that logs were unavailable.
2. **Anonymity as a chosen trade-off with a governance alternative.** Full anonymity precluded linkage — that was a defensible ethics posture, but consented-linkage designs (respondent opts in to have survey responses joined to their own log record under an ethics protocol) are standard practice and would have converted this study from a correlation between two self-reports into a correlation between perception and behaviour. The authors should state whether this was considered and why it was rejected. This also non-trivially strengthens the paper's response to Reviewer 1's common-method-variance objection.
3. **Decision-usability of the practice recommendation.** The Discussion suggests onboarding that helps students "see concrete usefulness" may warrant institutional attention. From the seat that funds onboarding: *r* = .42 between two self-reports at one time point cannot support that allocation, in either direction. Reviewers should press on what evidence *would* — minimally, pre/post log-based engagement around an onboarding intervention. The recommendation is triple-hedged ("modest support," "may be worth," "suggested by, not proven by"), which is honest, and also leaves nothing a practitioner can act on. Say which it is.
4. **Nonresponse and the recruitment channel.** Recruitment ran through the institution's course-announcement channel — which is itself inside or adjacent to the LMS. Students who rarely open the LMS were structurally less likely to see the invitation. This is not generic voluntary-response bias (which Limitations does note); it is a **sampling mechanism correlated with the dependent variable**, which can bias the correlation itself, not merely the mean. The paper misses this specific mechanism.

**Will particularly care about**: That the paper's central weakness was a choice with an available alternative, and is narrated as a constraint. Institutions collect behavioural data continuously; a study that measures self-reported approximations of data the institution already holds should explain why.

**Possible blind spots**: Will underweight what a perception measure legitimately captures on its own terms — perceived usefulness is not a behavioural variable and log data cannot substitute for it. May tilt the review toward "conduct a different, better-resourced study," which is not always actionable reviewer guidance.

---

## Review Strategy Recommendations

**Cross-cutting instruction — verify references before drafting substantive comments.** The `10.5555` prefix pattern must be resolved first by the Journal-Fit Reviewer. If confirmed as placeholder or fabricated, that finding dominates the review and every other comment becomes conditional; a methods critique of a manuscript with a non-existent evidence base is misdirected effort. Report as verified or unverified — do not assume either outcome.

**The paper's defining characteristic: polish–payload mismatch.** This manuscript is not badly executed; it is thinly conceived and impeccably presented. Reviewers should be briefed that the usual heuristics will mislead here. There is no overclaiming to catch (the hedging is genuinely careful and correct), no sloppy writing, no missing limitations section. The problem is upstream, in what was designed and measured. Reviewers accustomed to catching overreach may find nothing to object to and default to accept-with-minor-revisions, which would be the wrong verdict for the wrong reason.

**Register**: developmental in wording, evidence-based in verdict. Given the paper's evident methodological literacy, feedback should be pitched as design guidance to a competent author rather than remediation. This changes tone only — the recommendation must follow from the criteria, and the register must not soften it.

**Anticipated tension the synthesizer must resolve — the asks are not the same size.**
- Reviewer 1 identifies problems that are largely *fixable in revision* (polyserial correlation, instrument appendix, response-rate denominator, common-method-variance discussion, softened precision claims).
- Reviewer 2 identifies problems requiring *substantial rewriting but not new data* (canonical literature, meta-analytic benchmark, institutional context, resolution of the Song self-contradiction).
- Reviewer 3 identifies a problem requiring *a different study* (log-linked design).

The synthesizer must not stack these into one undifferentiated revision list. Doing so produces an incoherent verdict — "major revisions" that silently includes a request to re-run data collection. Sort by whether each item is achievable within a revision cycle and say so.

**Anticipated overlap the synthesizer must not double-count.** Reviewers 1 and 3 both attack the dependent variable, from opposite directions: R1 from measurement theory (single item, coarse categories, unquantified reliability), R3 from data availability (logs existed and were not used). These are one underlying weakness viewed twice, not two independent objections. Counting them separately would artificially inflate the case against the paper. Conversely, they converge productively: R3's consented-linkage proposal is the concrete remedy for R1's measurement critique, and the synthesis should present them as one problem with one solution path.

**Coverage note on secondary disciplines.** Information-systems/TAM coverage sits with Reviewer 2; measurement/psychometrics with Reviewer 1; learning analytics and institutional research with Reviewer 3. No secondary discipline is unassigned, and no two reviewers share primary responsibility for the same one.

**One asymmetry to guard against.** Three of four reviewers will converge on "insufficient contribution." That convergence is plausibly correct, but it can also be an artefact of configuring three reviewers who all specialize in finding weaknesses in small studies. The synthesizer should ask directly whether a well-executed, honestly reported, single-site incremental finding has a legitimate home in the literature — and if the answer is yes, the verdict is a venue-and-format problem rather than a quality problem. That distinction changes the recommendation substantially and neither the Journal-Fit Reviewer nor Reviewer 2 is well positioned to raise it against their own priors.
