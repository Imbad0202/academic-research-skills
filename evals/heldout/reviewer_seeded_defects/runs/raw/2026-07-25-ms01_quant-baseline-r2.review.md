# Isolated-dispatch panel review — alpha-2 (baseline condition, 2026-07-25)

(Phase 1 calls were physically separated: each seat’s pre-commitment was produced by a clean
headless `claude -p` call — claude-opus-5, effort xhigh, thinking enabled — that received only
the contract + title/field/word_count and was forbidden from reading any manuscript. Phase 2,
field analysis, and synthesis were separate paper-visible headless calls with read scope
limited to the named skill files and the neutral-named manuscript copy.)

# PART 1 — FIELD ANALYSIS

# Field Analysis Report

## Paper Basic Information
- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Abstract length**: ~145 words
- **Full text length**: ~2,600 words (main text, excluding references)
- **Number of references**: 15 listed in the reference list; 6 cited in text (Calloway 2019; Ferro & Nakamura 2021; Osei 2020; Rutledge & Berange 2022; Vandermeer 2023; Ibarra 2023) — 9 uncited entries

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Learning analytics / educational technology, situated within higher education studies (student retention and persistence) |
| Secondary Disciplines | Educational psychology (self-regulated learning, goal orientation); educational measurement and quantitative methodology; information systems / HCI (dashboard interface design and log-based behavioral instrumentation) |
| Research Paradigm | Quantitative (observational), with a light mixed-data character — behavioral LMS log data combined with a single self-report item; the paper does not claim mixed-methods integration and no qualitative analysis is present |
| Methodology Type | Cross-sectional observational study using LMS trace/log data + a voluntary-response survey; analysis limited to Pearson correlation, independent-samples t-tests, and a median split on a continuous predictor |
| Target Journal Tier | **Q3 as written; Q2-aspiring.** The framing, literature engagement, and topic would suit a mainstream field journal (Q2), but the analytic execution — bivariate statistics only, no covariate adjustment, no multivariable model of a dichotomous outcome, median-split dichotomization, single-item construct measurement — sits below the current methodological floor of Q1/Q2 learning-analytics venues. Additionally, the reference list is composed entirely of DOIs in the reserved `10.5555` prefix range with no recognizable field-canonical anchors (no Zimmerman, Winne, Tinto, Verbert, Gašević, Jivet, or equivalents), which will read to any specialist editor as an unverifiable or placeholder bibliography and is disqualifying at any tier until resolved. |
| Paper Maturity | **Revised draft.** Structure is complete (IMRaD with tables, keywords, limitations section, formatted references) and the prose is polished at sentence level, which superficially reads as pre-submission. But the manuscript contains internal factual contradictions that a pre-submission draft would not survive: the abstract reports *r* = .42 while §4.2 reports *r* = .24; the analytic sample is stated as *N* = 142 yet §4.3 reports *t*(156) for a subgroup comparison drawn from 87 respondents; Table 2 group sizes (66 + 61 = 127) do not sum to the 142 the same paragraph says were "all classified"; §4.3 reports *t*(140) = 1.31 with *p* = .008, a statistically impossible pairing (that *t* corresponds to *p* ≈ .19); and §2 attributes to Ferro & Nakamura (2021) a claim that dashboards "reliably improve outcomes for lower-achieving students" while that reference's own title reads *When dashboards demotivate: Peer comparison and the lower-achieving student*. These are consistency failures, not polish failures, and they place the manuscript before, not after, a competent internal review. |

## Recommended Target Journals (Top 3)

1. **Journal of Learning Analytics** (SoLAR, open access) — The most precise topical fit: student-facing dashboards, trace-data operationalization, and the field's own ongoing self-critique about correlational designs and causal overreach. JLA reviewers are the exact audience for the Vandermeer/Ibarra-type measurement and inference concerns the paper itself raises. Realistic only after the internal statistical inconsistencies are resolved and the causal language in §5 and §6 is retracted to match the correlational design; JLA reviewers are unusually alert to precisely this failure mode.

2. **British Journal of Educational Technology** — Broad educational-technology readership with strong appetite for LMS-based empirical work and dashboard interventions, and more tolerant than JLA of single-course observational designs when the inferential claims are correspondingly modest. Would require the same claim-strength correction plus, at minimum, a logistic regression of retention on engagement with covariate adjustment; a *r* = .24 bivariate association with a dichotomous outcome is below BJET's current analytic bar on its own.

3. **Internet and Higher Education** — Fits the higher-education-context framing and the retention/persistence outcome, and values theoretically-anchored SRL work. The self-regulated learning framing is the paper's strongest asset for this venue, but the single-item perceived-control measure would need to be replaced or supplemented with a validated SRL instrument (MSLQ subscale or equivalent) before the theoretical claim is defensible here.

*Note on tier:* if the sampling design (voluntary mid-term recruitment, non-respondents excluded) and the single-course scope cannot be strengthened, the realistic landing zone is a regional or practice-oriented venue rather than any of the above, and the paper should be reframed as a descriptive institutional case report rather than as evidence about dashboards in general.

---

## Reviewer Configuration Cards

**Cross-disciplinary coverage note:** This paper is moderately cross-disciplinary (learning analytics + educational psychology + quantitative methodology + HCI). Coverage is allocated as follows: R1 owns the statistical and inferential layer; R2 owns the learning-analytics/higher-education domain layer including literature accuracy; R3 owns the research-ethics and institutional-deployment layer, which no other seat touches and which this manuscript raises unusually sharply. The EIC owns fit and claim-evidence proportionality.

### Reviewer Configuration Card #1

**Role**: EIC
**Identity Description**: Editor-in-Chief of the *Journal of Learning Analytics*, a learning-analytics scholar whose own program of work concerns the translation of trace data into actionable institutional practice; has spent the last five years pushing the field's editorial standards toward explicit separation of association from intervention effect, and personally desk-rejects manuscripts whose abstract and conclusion make claims the design cannot license.
**Review Focus**:
  1. Claim-evidence proportionality across the abstract, Discussion, and Conclusion — specifically whether the manuscript's own §1 promise ("we are careful throughout to distinguish the pattern in the data from the causal story") is kept, given that §5 opens with "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course," and §6 asserts a "dependable strategy" that is "generalizable" and applicable "for higher education institutions worldwide" from a single course at one institution.
  2. Internal consistency as a threshold condition for review — whether the abstract's *r* = .42 and §4.2's *r* = .24 can be reconciled, and which figure (if either) the manuscript's conclusions rest on; whether a manuscript with an unreconciled effect-size discrepancy between abstract and results should proceed to full review at all.
  3. Fit and contribution — whether a single-course, single-term, bivariate correlational study of *N* = 142 adds anything to a literature the manuscript itself characterizes as already saturated with correlational designs and causal overreach (§2, citing Ibarra 2023). What is the marginal contribution beyond one more instance of the pattern the field has already diagnosed?
**Will particularly care about**: Whether the paper's self-aware framing about causal overreach is substantive or decorative — a manuscript that names the field's cardinal error in its Literature Review and then commits it in its Discussion and Conclusion is a more serious editorial problem than one that simply overclaims naively, because it demonstrates the author knows the standard and did not apply it.
**Possible blind spots**: The EIC works at the level of framing and claim strength and may not independently recompute the reported statistics; will likely notice the *r* = .42 / *r* = .24 discrepancy because it spans abstract-to-results, but may not catch the degrees-of-freedom and *p*-value impossibilities inside §4.3, nor the Table 2 arithmetic. May also under-weight the ethics issue in §3.2, which falls outside the typical editorial fit assessment.

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology
**Identity Description**: Quantitative methodologist in educational measurement and applied statistics, specializing in the analysis of dichotomous educational outcomes (persistence, withdrawal, completion) and in selection bias in observational studies of educational technology; teaches a doctoral seminar on why median splits and bivariate correlations produce inflated and unreplicable findings, and serves as a statistical reviewer for two education journals.
**Review Focus**:
  1. **Numerical integrity audit — recompute every reported statistic against every other.** (a) Abstract *r* = .42 vs. §4.2 *r* = .24. (b) §4.3 reports *t*(156) = 3.02 for a comparison of perceived control between engagement groups, but only 87 respondents answered the perceived-control item (§4.1) and the full analytic sample is 142 — *df* = 156 is unreachable from either. (c) §4.3 reports *t*(140) = 1.31, *p* = .008; *t*(140) = 1.31 corresponds to *p* ≈ .19 two-tailed, and the manuscript's own prose calls the difference "small" and "did not reach a comparable level," which contradicts the *p* it reports. (d) Table 2 reports *n* = 66 and *n* = 61 (total 127) for a comparison the text says included "all 142 students." (e) Table 1 reports perceived control to three decimals (3.847) alongside two-decimal SDs, and reports a final-exam variable that appears nowhere in the Measures section (§3.3) — an undeclared measure appearing first in Results.
  2. **Inferential validity of the analysis plan given the outcome type.** Retention is coded dichotomously (§3.3), yet the primary association is reported as a Pearson correlation — a point-biserial correlation reported without covariate adjustment, without a logistic model, and without any confidence interval. Whether an unadjusted bivariate *r* can support any claim about retention when prior achievement, prior LMS engagement, motivation, and course load are unmeasured and uncontrolled; whether the reverse causal path (students on track to persist are the ones who keep opening the dashboard) is not at least as plausible as the one the paper asserts.
  3. **Sampling and selection.** §3.2 contains an internal contradiction: participants were "drawn from the course enrollment using a random sample," yet the immediately following paragraph describes an announcement-based voluntary opt-in with non-respondents excluded. These are incompatible sampling designs and only one can be true. Whether the volunteer sample — recruited mid-term, therefore structurally excluding students who had already disengaged or withdrawn before the recruitment window — can speak to retention at all, given that the students most informative about non-retention are the ones least likely to be in the sample. Also: the median split (§3.3) discards variance the paper already has, and no power analysis or effect-size interval is reported anywhere.
**Will particularly care about**: Whether the numbers in this manuscript are mutually consistent — because they are not, and the pattern (an inflated *r* in the abstract, an unreachable *df*, an impossible *p*, and a table that does not sum) is not attributable to a single typographical slip. Whether the reported results can be reproduced from the described sample at all is a prior question to whether they mean anything.
**Possible blind spots**: May frame the finding as fixable by better modeling (logistic regression with covariates) and under-weight that the mid-term voluntary recruitment makes the retention outcome structurally unrecoverable regardless of model choice — a design defect, not an estimation defect. Also likely to treat the misattributed Ferro & Nakamura claim in §2 as outside statistical scope, and to have little to say about the consent problem in §3.2.

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain
**Identity Description**: Senior learning-analytics researcher in higher education, specializing in student-facing dashboards and self-regulated learning; has published systematic reviews of dashboard-outcome studies and knows the primary literature — Zimmerman's and Winne's SRL models, Jivet and Verbert's dashboard-design critiques, Tinto's and Bean's persistence theory — well enough to notice both what is cited and what is missing.
**Review Focus**:
  1. **Citation accuracy and literature integrity.** §2 states that "dashboards have been shown to reliably improve outcomes for lower-achieving students (Ferro & Nakamura, 2021)," but that reference's listed title is *When dashboards demotivate: Peer comparison and the lower-achieving student* — the source appears to argue the opposite of what it is cited for, and the manuscript builds its "equity-oriented rationale" on that inversion. Separately, of 15 reference-list entries only 6 are cited in text; Ainsworth & Devi, Berange, Delacroix & Ohno, Halloran, Kessler & Amadou, Montez, Prakash & Tolliver, Solberg & Whitfield, and Wexler & Ojo appear nowhere in the body. Wexler & Ojo (2020), *Retention modeling with LMS trace data: A cautionary study*, is directly on point for this manuscript's central design and is left uncited. Every DOI in the list falls in the `10.5555` reserved-for-examples prefix, and no field-canonical source (Zimmerman, Winne, Verbert, Jivet, Gašević, Tinto) appears anywhere — the bibliography must be independently verified before any substantive claim resting on it can be assessed.
  2. **Theoretical framework depth.** The paper invokes self-regulated learning as its mechanism (§1, §2, §5) but operationalizes the entire construct with one general-purpose item ("Overall, I feel in control of my learning in this course," §3.3). Whether a single-item global rating can stand in for a multiphase cyclical construct; whether "perceived control" is even the SRL construct the cited forethought/monitoring framing implies, or a distinct motivational belief (closer to academic control or self-efficacy) being used as a proxy without argument. The claim that "single-item overall ratings are common in dashboard studies to limit survey burden" is asserted without citation.
  3. **Contribution relative to the existing dashboard literature.** The manuscript's own §2 establishes that the field already has an abundance of correlational dashboard studies and an explicit critique of their causal overreach (Ibarra, 2023). What does this study add that its own literature review does not already report? Whether the Discussion's claim that "our finding that engagement tracks retention aligns with the view that externalized progress cues can support persistence" is a contribution or a restatement, and whether the paper engages at all with the competing demotivation account (Osei 2020) that it raises in §2 and then never revisits against its own data.
**Will particularly care about**: Whether the manuscript accurately represents the sources it builds on — the apparent inversion of Ferro & Nakamura is not a citation-style problem but a substantive misrepresentation on which an equity argument is erected, and the two-thirds-uncited reference list raises the question of whether the sources were consulted at all.
**Possible blind spots**: Deep domain familiarity may lead this reviewer to mentally supply the field-standard caveats and correct framing that the manuscript itself does not contain, softening the assessment of the causal language. May accept the *r* values as reported without recomputing, and is unlikely to independently flag the *df* and *p* impossibilities in §4.3 (R1's territory) or the consent issue in §3.2 (R3's territory).

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical
**Identity Description**: Research-ethics and educational-data-governance specialist who chairs a university IRB's education-research panel and advises institutions on the secondary use of LMS trace data under student-privacy regimes (FERPA / GDPR-equivalent); background in information systems, with applied experience in institutional learning-analytics deployment and in the operational reality of what "increase dashboard engagement" means when translated into an institutional mandate.
**Review Focus**:
  1. **Consent, disclosure, and research-ethics reporting.** §3.2 states plainly that "students were not informed that their dashboard activity data would be analyzed for this study," while consent was obtained only for the survey. Whether behavioral log data collected under one purpose (course delivery) may be repurposed for research under a consent that did not cover it; whether this constitutes undisclosed observation of identifiable students. Compounding this: the manuscript contains no IRB or ethics-approval statement, no data-availability statement, no funding or conflict-of-interest declaration, and no description of de-identification or data handling — all of which are mandatory at every venue named above. This is a submission-blocking gap independent of the paper's statistical problems.
  2. **What the intervention implication actually authorizes institutionally.** §6 tells institutions that "investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy." Whether "encouraging engagement" is even the same object as the observed variable — the study measured spontaneous dashboard opening, not induced dashboard opening, and there is no basis for assuming an engagement increase produced by institutional pressure carries the association observed in voluntary use. Whether an institution acting on this recommendation could plausibly convert a benign monitoring tool into a compliance metric, and whether the dashboard's peer-comparison band (§3.1) — the very feature the manuscript's own §2 identifies as a demotivation risk for struggling students (Osei 2020) — is safe to scale on this evidence.
  3. **Deployment context and reproducibility of the artifact under study.** The dashboard is described only in general terms (§3.1: "engagement metrics, assignment progress, and a peer-comparison band") with no screenshot, no version, no vendor or platform identification, and no statement of what students actually saw. §5.1 concedes the interface "differs from those deployed elsewhere" while §6 nonetheless claims generalizability "worldwide." Whether any other institution could identify whether their dashboard is the same class of artifact; whether the sessionization rule (30-minute inactivity, "the platform's default") is a research-defensible operationalization or an inherited platform artifact silently treated as a construct.
**Will particularly care about**: That the manuscript's own Methods section documents an undisclosed secondary use of student behavioral data and then, in the Conclusion, recommends worldwide institutional scale-up of the practice — the ethics gap and the generalization claim compound each other, and neither the statistical reviewer nor the domain reviewer is positioned to name that combination.
**Possible blind spots**: Will not independently audit the statistical reporting and may take the reported associations at face value while critiquing their institutional translation; may under-weight the SRL theoretical framing and the literature-accuracy problems, and could push the review toward a governance conversation at the expense of the more basic question of whether the results are internally reproducible at all.

---

## Review Strategy Recommendations

**Special characteristics requiring particular attention:**

- **This manuscript's defects are verifiable rather than debatable, and the panel should be instructed to state them as findings of fact, not as matters of reviewer judgment.** At least five numerical claims are mutually inconsistent within the manuscript's own text: abstract *r* = .42 vs. §4.2 *r* = .24; *t*(156) from a sample of at most 142 (and a perceived-control subsample of 87); *t*(140) = 1.31 reported with *p* = .008; Table 2's 66 + 61 = 127 against the same paragraph's "all 142 students"; and Table 1's final-exam variable, which is never defined in §3.3 Measures. Reviewers should be directed to check reported statistics against each other rather than assuming a consistent underlying analysis.

- **Style-substance divergence is the central calibration risk.** The prose is fluent, the hedging in §2 and §5.1 is sophisticated, and the manuscript performs methodological self-awareness convincingly ("we are careful throughout to distinguish the pattern in the data from the causal story," §1). This surface competence is likely to induce reviewers to read charitably and assume the numbers are sound. The panel should be primed that fluency here is not evidence of rigor, and that the hedged framing coexists with unhedged causal assertion in §5 ("dashboard engagement improved course retention… therefore raises the probability") and §6 ("a dependable strategy… generalizable… worldwide") — the manuscript states the correct epistemic standard and then violates it.

- **The apparent citation inversion is a high-severity finding and must not be filed as a formatting note.** §2 cites Ferro & Nakamura (2021) as showing dashboards "reliably improve outcomes for lower-achieving students," while the reference list gives that work's title as *When dashboards demotivate*. If the reference list is accurate, the manuscript's equity rationale rests on a reversed source. Combined with 9 of 15 references being uncited in text, all 15 DOIs sitting in the `10.5555` reserved-example range, and the absence of any recognizable field-canonical citation, the bibliography requires independent verification before the panel treats any literature-based claim as supported. R2 owns this; the EIC should be told it may be dispositive on its own.

- **Sampling contradiction is load-bearing, not cosmetic.** §3.2 asserts a "random sample" in one paragraph and an announcement-based voluntary opt-in with non-respondents excluded in the next. Because recruitment occurred mid-term, students who withdrew early are structurally absent from a study whose outcome is retention. R1 should be directed to treat this as a threat to the interpretability of the entire retention analysis rather than as a generalizability caveat, and to say explicitly whether the design can answer the research question at all.

- **The ethics gap is submission-blocking and orthogonal to the statistics.** No IRB statement, no ethics approval, no data-availability or funding/COI statement, plus an explicit acknowledgment that students were not informed their behavioral data would be analyzed. R3 owns this; without it the finding would likely go unstated, because neither a statistician nor a domain specialist typically reads §3.2 for consent scope.

- **Developmental posture is warranted alongside severity.** Despite the density of problems, the structure is complete, the topic is genuinely worth studying, the limitations section shows real awareness, and several defects (claim strength, statistical reporting, citation accuracy, ethics disclosure) are correctable. Reviewers should be instructed to write correctively — for each defect, state what would need to be true for the claim to stand — rather than to adopt a purely gatekeeping register. This does not soften the decision recommendation; it shapes the tone.

**Complementarity and tension between reviewers:**

- **Designed non-overlap.** R1 audits internal numerical consistency and inferential validity; R2 audits literature accuracy and theoretical operationalization; R3 audits research ethics, data governance, and the institutional translation of the recommendation. Each of the manuscript's four defect families (statistical inconsistency, citation misrepresentation, ethics/disclosure absence, causal overclaim) has exactly one primary owner, with causal overclaim owned by the EIC and cross-checked by R1 and R3 from different directions.

- **Expected convergence — a strong signal when it occurs.** R1 (from selection bias and reverse causality), R2 (from the field's documented causal-overreach critique, Ibarra 2023), and R3 (from what the recommendation authorizes institutionally) should independently arrive at the §5/§6 causal language. Independent convergence from three unrelated premises is stronger evidence of a Priority-1 defect than any single reviewer's objection, and the synthesizer should record it as convergent rather than collapsing it into one line item.

- **Expected productive tension #1 — severity of the effect size.** R1 will likely treat *r* = .24 (if that is the correct value) as too small and too confounded to support any practical recommendation. R2 may argue that a modest association is unremarkable and even expected in this literature, and that the real problem is the interpretation rather than the magnitude. The synthesizer should not average these: the disagreement is informative, and the resolution depends on which *r* the authors actually obtained — which the manuscript does not currently establish.

- **Expected productive tension #2 — is this fixable?** R2 and the EIC may see a salvageable paper needing reanalysis and claim retraction. R1 is likely to argue the mid-term voluntary sample makes the retention question unanswerable with these data no matter how the analysis is redone. R3 may hold that the consent gap cannot be retrospectively cured at all. This three-way split maps directly onto the major-revision-versus-reject boundary and should be surfaced explicitly in the decision letter rather than smoothed over.

- **Deliberate blind-spot compensation.** The EIC and R2 are the seats most susceptible to being persuaded by the manuscript's polish; R1's mandate to recompute and R3's mandate to read §3.2 for consent scope are the structural corrective. Conversely, R1 and R3 may miss the field-level question of whether this study contributes anything beyond what §2 already reports — that is R2's to raise, and the synthesizer should confirm it was raised.

- **Sequencing note for the synthesizer.** If R1's numerical audit confirms the inconsistencies, the substantive critiques from R2 and R3 apply to a results section whose values cannot currently be relied upon. The decision letter should present the internal-consistency findings first as a threshold matter, then present the design, literature, and ethics findings as issues that persist independently of how the numerical discrepancies are resolved — so the authors cannot treat corrected typography as a full response.

# PART 2 — SEATS

## SEAT — EIC

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** From the editorial chair, this dimension asks whether the study's design, data handling, statistical reporting, and reproducibility affordances would survive scrutiny from the journal's methodological readership. I am not the technical referee — that seat belongs to the methodology reviewer — but I own the question of whether the manuscript's evidentiary machinery is *visible and sound enough* for the journal to stand behind the claims it prints. For a deployment study in learning analytics, this means the observational design must be described well enough that a reader can tell what was measured, on whom, over what period, and with what comparison. At 2487 words, I expect compression; compression is acceptable, but absent method reporting is not the same as brief method reporting, and I will judge which one this is.

**D2 — domain_accuracy (mandatory).** This asks whether the paper's claims sit correctly within the current evidence base of learning analytics and the higher-education retention literature it borrows from, whether prior work is represented as prior authors would recognise it, and whether domain terminology carries its accepted meaning. My editorial concern is reputational and scholarly: a journal that prints a mischaracterisation of the retention literature — or a dashboard-engagement paper that treats a contested construct as settled — damages its standing with the readership that knows the field best. Retention and persistence is a domain with decades of theory and a well-known tendency for engagement proxies to be read as more meaningful than the literature supports, so I will hold this dimension to the field's own standard of representation, not to a generic factual-error check.

**D3 — argumentative_coherence (mandatory).** This is the dimension closest to my seat's native competence: does the manuscript's central thesis hold together from title through abstract, introduction, results, and conclusion, does the evidence presented actually license the claims made, and are there reasoning failures that break the spine of the argument? For this title in particular, the argumentative load-bearing question is what relationship between dashboard engagement and course retention the paper commits to, and whether the evidence it musters supports a claim at that strength. Over-promising in the title or abstract and under-delivering in the discussion is a coherence failure, not merely a stylistic one, and it is precisely the failure an editor is positioned to catch.

**D4 — cross_disciplinary_relevance (high priority, not mandatory).** This asks whether the framing, definitions, and implications are legible to adjacent-field readers, and whether any claims that reach across disciplinary boundaries are substantiated rather than asserted. This paper sits at an intersection by construction — learning analytics and educational technology on one side, higher education studies on the other — so the journal's readership is heterogeneous by default: institutional researchers, retention scholars, instructional technologists, possibly administrators. My editorial question is whether a reader arriving from the higher-education-studies side can follow the analytics apparatus, and whether a reader arriving from the analytics side is given the retention-theory grounding the claims require. Because this is high-priority rather than mandatory, it can trigger a failure condition only at `block` strength.

**D5 — writing_and_structure (normal priority).** This covers organisation, clarity of exposition, quality of figures and tables, and conformity to venue conventions. It is the lightest dimension in the contract — no failure condition in the contract references normal-priority dimensions at all — so my score here is diagnostic and advisory for the synthesiser rather than decision-driving. I will still score it honestly: at 2487 words the manuscript is at short-communication length, and I will assess whether the structure it adopts is a deliberate fit for that length or the residue of a longer paper cut down.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for`: Whether the deployment context is specified (institution type, course or courses, cohort size, term span); whether "dashboard engagement" is given an operational definition traceable to a measurable behaviour rather than left as a construct label; whether "retention" is defined at a stated unit and window (course completion? re-enrolment? within-term persistence?); whether a comparison or counterfactual exists at all (control group, pre/post, matched sample, or an explicit statement that none does); whether reported statistics carry the quantities a reader needs to interpret them (effect estimates, uncertainty, sample sizes, model specification) rather than bare significance markers; whether any data-access, code, or instrument-availability statement appears; whether the paper acknowledges that engagement measures are self-selected and that students who use dashboards may differ systematically from those who do not.
- `what_triggers_block`: A quantitative claim about the engagement-retention relationship is presented with no recoverable method basis — no sample size, no analytic approach, and no definition of either measured variable — such that a competent reader cannot tell what was done; OR the study reports an effect and the described design cannot support that effect (e.g. an outcome asserted for a population the described data never observed); OR a causal claim is stated in the results or conclusion while the design as described is observational and no confounding adjustment or identification argument is offered anywhere. Any of these means the journal would be printing a number no reader can audit.
- `what_triggers_warn`: The method is present and followable but under-specified for the strength of the claims — e.g. sample size and analysis are given but selection into dashboard use is never addressed; OR retention is defined loosely enough that two readers would operationalise it differently; OR reporting omits uncertainty or effect magnitude while relying on significance language; OR no reproducibility affordance of any kind is offered but the design is otherwise legible. These are fixable in revision and do not by themselves make the evidence unauditable.

### D2: domain_accuracy

- `what_to_look_for`: Whether the retention and persistence literature is engaged at all and, if so, whether the named traditions and constructs are used as that literature uses them; whether learning-analytics terminology (engagement, at-risk indicator, early-warning system, learning analytics dashboard) is used in its accepted technical sense rather than a colloquial one; whether prior findings are characterised at the strength their original authors reported, particularly the well-documented mixed and null results for dashboard interventions; whether the paper acknowledges the known distinction between platform activity as a proxy and learning or commitment as the construct of interest; whether cited work is attributed to the right claim.
- `what_triggers_block`: A load-bearing claim contradicts well-established evidence in the retention or learning-analytics literature without acknowledgement or argument — e.g. presenting dashboard-driven retention gains as an established consensus when the intervention literature is demonstrably mixed; OR prior work is materially misrepresented in a way that props up the paper's contribution claim (a cited study reported as finding the opposite or a stronger result than it did); OR a core domain construct is defined incorrectly in a way that invalidates the interpretation of the results. Any of these would be visible to the journal's core readership on first reading.
- `what_triggers_warn`: The domain grounding is thin rather than wrong — the retention literature is invoked by name but not actually engaged with; OR terminology is used loosely at the edges without corrupting the central interpretation; OR the mixed state of prior dashboard-intervention evidence is under-represented but not denied; OR the literature base is narrow enough (single tradition, single geography, dated) that the framing is incomplete for the claims made.

### D3: argumentative_coherence

- `what_to_look_for`: Whether a single research question is stated and whether the conclusion answers that question rather than an adjacent one; the consistency of claim strength across title, abstract, results, and discussion — specifically whether "Evidence from…" in the title is cashed out as associational or causal evidence and whether that commitment holds throughout; whether the discussion's implications follow from the results actually reported or import strength from elsewhere; whether limitations are stated and then honoured in the conclusion rather than stated and then contradicted; whether alternative explanations for an engagement-retention association (prior achievement, motivation, course difficulty, general platform activity) are considered or silently excluded; whether recommendations to practice are proportionate to the evidence.
- `what_triggers_block`: The central thesis is internally inconsistent — the conclusion asserts something the reported results do not support, or asserts it at a strength the paper's own limitations section disavows; OR the paper hedges to association in one section and recommends causal intervention ("institutions should deploy dashboards to improve retention") in another without bridging argument; OR a fallacy carries the main argument (treating correlation as intervention warrant, or generalising from a single deployment to a population claim with no argument for transferability) such that removing the fallacy removes the contribution.
- `what_triggers_warn`: The argument is directionally sound but leaks at the seams — e.g. the abstract is measurably stronger than the discussion; OR plausible alternative explanations go unmentioned though the conclusion does not depend on excluding them; OR the research question is implicit and must be reconstructed by the reader; OR practice recommendations are stated slightly beyond what the evidence licenses but are not the paper's load-bearing claim.

### D4: cross_disciplinary_relevance

- `what_to_look_for`: Whether analytics-side terms are glossed for higher-education-studies readers and retention-theory terms are glossed for analytics readers; whether the deployment is contextualised institutionally (what kind of institution, what student population, what retention problem it faces) so that readers outside the deploying context can judge relevance; whether implications are addressed to identifiable audiences (institutional researchers, instructors, administrators, system designers) rather than left generic; whether any claim that bridges the two fields — that an analytics measure indexes a retention-theoretic construct — is substantiated rather than assumed; whether the single-deployment scope and its boundaries of transfer are stated.
- `what_triggers_block`: The paper is unreadable to one of its two constituent audiences on a load-bearing point — core apparatus or core construct is used throughout with no definition available anywhere in the text, so that an adjacent-field reader cannot evaluate the central claim; OR an explicit interdisciplinary bridging claim (an engagement metric standing in for a retention-theory construct) is asserted as the basis of the contribution with no substantiation anywhere. Because D4 is high-priority, only a `block` here fires a failure condition, so I reserve it for genuine inaccessibility of the central argument, not for uneven exposition.
- `what_triggers_warn`: Framing tilts to one field with the other treated as background — e.g. the analytics is well specified while the retention framing is decorative, or vice versa; OR implications are stated generically without naming who should act on them; OR the institutional context is thin enough that transferability is left to the reader to guess; OR jargon from one side is unglossed in places that are secondary rather than load-bearing.

### D5: writing_and_structure

- `what_to_look_for`: Whether the section structure suits a ~2500-word article and whether each section earns its length; whether the abstract is self-contained and accurately previews the paper; whether figures and tables are legible, captioned so as to stand alone, referenced in text, and interpreted rather than merely displayed; whether numbers in the text agree with numbers in the tables; whether reference formatting and apparatus are internally consistent; whether the prose is clear enough that meaning does not depend on charitable reading; whether the length looks like a deliberate short-form design or a truncation that left dangling references to material no longer present.
- `what_triggers_block`: Presentation failures obstruct evaluation of the substance — e.g. figures or tables central to the results are missing, illegible, or unreferenced; OR numbers in text and in exhibits disagree materially; OR the manuscript's organisation is disordered enough that the reader cannot locate what was done and what was found; OR the abstract describes a different study than the body. (Noting for the record: no contract failure condition references normal-priority dimensions, so a `block` here is diagnostic to the synthesiser and does not itself fire F1, F2, or F3.)
- `what_triggers_warn`: Ordinary craft problems that revision fixes — sections disproportionate to their contribution; an abstract that under-represents or over-claims relative to the body; exhibits that are present and legible but under-interpreted or redundant with the text; inconsistent reference or notation style; passages requiring re-reading; dangling cross-references or venue-convention mismatches.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## EIC Review Report

### Reviewer Identity

Editor-in-Chief of the *Journal of Learning Analytics*; a learning-analytics scholar whose own program of work concerns the translation of trace data into actionable institutional practice. For the last five years I have pushed this journal's editorial standards toward an explicit separation of association from intervention effect, and I desk-reject manuscripts whose abstract and conclusion make claims the design cannot license.

### Overall Recommendation

Reject

### Confidence Score

4

- The claim-strength, fit, and internal-consistency judgments below are squarely within my editorial competence. I have not recomputed the manuscript's statistics from raw data — the degrees-of-freedom and *p*-value arithmetic belongs to the methodology seat — so where I cite a numerical contradiction I cite it as a discrepancy visible on the manuscript's own face, not as a recomputation.

### Summary Assessment

The manuscript reports an observational study of 142 undergraduates in a single introductory statistics course, relating LMS-logged dashboard sessions to end-of-term course retention and to a single self-report item on perceived control. The topic is squarely within this journal's scope, the writing is fluent, and §2 and §5.1 display a real awareness of the field's methodological debates — including, explicitly, the causal-overreach critique (Ibarra, 2023) that this journal has spent years trying to enforce.

That awareness is the manuscript's central problem rather than its defence. §1 promises that the authors "are careful throughout to distinguish the pattern in the data from the causal story." §5 opens by asserting that "dashboard engagement improved course retention" and that "increasing dashboard engagement therefore raises the probability that a student completes the course." §6 tells "higher education institutions worldwide" that dashboard investment is "a dependable strategy… generalizable." A manuscript that names the field's cardinal inferential error in its literature review and then commits it in its discussion and conclusion is a heavier editorial problem than one that overclaims naively: the standard was known and not applied.

Compounding this, the manuscript's own reported numbers do not agree with each other — most visibly, the abstract reports *r* = .42 while §4.2 reports *r* = .24 for what appears to be the same association. An unreconciled effect size spanning abstract and results is a threshold matter: I cannot determine which figure the conclusions rest on, and neither can a reader. The contribution question is also unresolved: a single-course, single-term bivariate correlational study is precisely the design §2 characterises as already abundant.

### Strengths

1. **Genuine topical fit and a live question.** The relationship between student-facing dashboard use and downstream persistence is exactly the question this journal exists to adjudicate, and the manuscript addresses it with real institutional data rather than adoption metrics or satisfaction scores — the substitution §1 rightly criticises. The study is about something worth studying.

2. **A literature review that engages the field's actual disagreements.** §2 does not present dashboards as settled goods. It sets Calloway's (2019) reflective-prompt framing against the demotivation account (Osei, 2020), flags the proxy problem in click-based engagement measures (Vandermeer, 2023), and names the causal-language critique directly (Ibarra, 2023). This is the correct map of the terrain.

3. **Some methodological self-criticism is stated plainly rather than buried.** §3.3 concedes that the median split "is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency." §5.1 concedes narrow operationalisation, self-report bias, and single-course scope. §5's third paragraph — "the modest size of the engagement-retention association counsels against overstatement… dashboards help at the margin" — is a fair reading of a modest correlation.

4. **Legible reporting structure.** IMRaD organisation, keywords, two tables, a limitations subsection, and a formatted reference list mean the manuscript can be evaluated at all. Nothing here has to be reconstructed from fragments.

### Weaknesses

1. **The paper states the correct epistemic standard and then violates it (load-bearing).** §1's promise to "distinguish the pattern in the data from the causal story" is contradicted within the same manuscript by §5's "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course," and by §6's "engagement… is associated with, and raises, course retention." The design in §3.1 is explicitly "observational, cross-sectional." No covariate adjustment, matching, or identification argument appears anywhere. §5's own third paragraph then reverts to associational hedging, so the manuscript disagrees with itself across three consecutive paragraphs. *Improvement direction:* every causal verb must be retracted to associational language, and the reverse path — students already on course to persist are the ones who keep opening the dashboard — must be stated as at least equally consistent with the data. If the authors wish to retain a causal claim, they need a design that licenses it, not softer wording around the same claim.

2. **An unreconciled effect size between abstract and results, within a broader pattern of numerical disagreement (threshold-level).** The abstract reports *r* = .42; §4.2 reports *r* = .24, *p* = .004. Nothing in the manuscript reconciles them, and they carry different practical implications — .42 would be a notable association in this literature, .24 is the "helps at the margin" reading §5 actually defends. Further discrepancies are visible on the face of the text: §4.3 reports *t*(156) for a comparison of perceived control, when the perceived-control item was answered by 87 respondents (§4.1) within an analytic sample of 142 (§3.2); §4.3 reports *t*(140) = 1.31 with *p* = .008 while describing the difference in prose as small and as not reaching a comparable level; Table 2's group sizes (66 + 61 = 127) do not reconcile with the same paragraph's statement that "all 142 students… were classified into engagement groups"; and Table 1 reports a final-exam variable that §3.3 Measures never defines. I flag these as an editor, not as the statistical referee — the methodology seat owns the arithmetic. *Improvement direction:* the authors must supply a single reconciled analysis with every reported statistic traceable to a stated *N*, and state explicitly which value the conclusions rest on. Until then the results section cannot be relied upon by the reviewers assessing everything downstream of it.

3. **The conclusion's scope claim is not connected to anything in the study (load-bearing).** §6 addresses "higher education institutions worldwide," calls dashboard investment "a dependable strategy," and describes the lever as "generalizable" — from one lecture section of one introductory statistics course at one institution in one term, with a dashboard §5.1 concedes "differs from those deployed elsewhere." §5.1 and §6 are in direct contradiction: the limitations section disavows transferability and the conclusion asserts it two paragraphs later. Additionally, the study observed *spontaneous* dashboard opening; §6 recommends *encouraging* engagement, which is a different object with no evidence behind it, and the peer-comparison band (§3.1) is the very feature §2 identifies as a demotivation risk (Osei, 2020) for the students an equity rationale would target. *Improvement direction:* the conclusion must be rewritten to the scope the design supports — one course, one term, one interface — and any institutional recommendation withdrawn or downgraded to a hypothesis for interventional test.

4. **A prior claim is attributed to a source that appears to argue the opposite, and the equity rationale is built on it.** §2 states that "dashboards have been shown to reliably improve outcomes for lower-achieving students… (Ferro & Nakamura, 2021)," and the manuscript builds its "equity-oriented rationale for institutional dashboard deployment" on that sentence. The reference list gives that work's title as *When dashboards demotivate: Peer comparison and the lower-achieving student*. On the manuscript's own evidence the citation appears inverted. Independently, 9 of the 15 listed references are never cited in text — including Wexler & Ojo (2020), *Retention modeling with LMS trace data: A cautionary study*, which is directly on point for this design — and every DOI in the list sits in the `10.5555` prefix range reserved for examples, with no field-canonical anchor anywhere. The domain seat owns the substantive verification; my editorial position is that the bibliography must be independently verified before any literature-based claim in this manuscript is treated as supported. *Improvement direction:* verify and correct every reference, restate what Ferro & Nakamura actually found, and rebuild or withdraw the equity rationale accordingly.

5. **The sampling description contains two incompatible designs, and the recruitment window undercuts the outcome.** §3.2 states participants were "drawn from the course enrollment using a random sample," and the next paragraph describes an LMS announcement inviting volunteers, with non-respondents excluded. Both cannot be true. The consequential half is the second: recruitment occurred "midway through the term," so students who had already disengaged or withdrawn are structurally absent from a study whose outcome is retention. *Improvement direction:* state the actual recruitment procedure, report the response rate and the enrolled-versus-analysed comparison, and address directly whether the sample can speak to non-retention at all. The methodology seat will judge whether this is remediable by reanalysis; my editorial read is that it constrains what any analysis of these data can conclude.

6. **No ethics, data-availability, funding, or conflict-of-interest statement — alongside an acknowledged undisclosed secondary use.** §3.2 states that "students were not informed that their dashboard activity data would be analyzed for this study," while consent covered only the survey. There is no IRB or ethics-approval statement, no de-identification description, and no data-availability, funding, or COI declaration anywhere in the manuscript. These are mandatory at this journal and at every comparable venue. *Improvement direction:* supply the ethics approval and its scope, state the legal and institutional basis for the secondary use of behavioural data, and add the standard declarations. This is a submission-completeness gap independent of everything above; the cross-disciplinary/ethics seat owns its substantive assessment.

### Detailed Comments

#### Journal Fit

Topically this is a good fit: student-facing dashboards, trace-data operationalisation, and retention outcomes are core to this journal's remit, and our readership includes exactly the institutional researchers and learning-analytics practitioners the paper addresses. Fit fails on two other axes, however. First, this journal's readership is the field's most alert to causal overreach in correlational dashboard studies — §5 and §6 would draw that objection from essentially every referee we could assign. Second, the manuscript's analytic execution (bivariate correlation of a dichotomous outcome, median split, no covariate adjustment, no confidence intervals, single-item construct measurement) sits below the current methodological floor here. My honest assessment is that in its present form the paper would land better as a descriptive institutional case report at a practice-oriented venue; with a corrected analysis and retracted claims, a broad educational-technology outlet (BJET) or a persistence-focused venue (*Internet and Higher Education*, if the perceived-control measure is replaced with a validated instrument) would be a more realistic target than this journal.

#### Originality

The manuscript's own §2 establishes that this literature is already saturated with correlational dashboard studies and already carries an explicit audit of their causal overreach. Against that backdrop, I could not identify what this study adds. §5's core interpretive sentence — "our finding that engagement tracks retention aligns with the view that externalized progress cues can support persistence" — is an alignment with an existing view, not a new claim. The combination of behavioural logs with a self-report measure is the strongest originality candidate, but a single global item on perceived control is too thin to constitute a measurement contribution, and the manuscript makes no claim to methodological novelty. The paper does not test the competing demotivation account (Osei, 2020) it raises in §2 against its own data, which is the one place where these data could have said something the literature does not already report.

#### Significance

If the association is real and is approximately *r* = .24, its significance is modest by the manuscript's own reading — dashboards "help at the margin." That is a legitimate and publishable finding, but it does not support the institutional recommendation in §6, and the manuscript's significance claim is currently pitched entirely at that recommendation. Because the effect size is unreconciled between abstract and results, I cannot presently assess significance at all: the two reported values imply materially different conclusions about how much this matters.

#### Structural Coherence

This is where the manuscript fails most clearly at my level of review. Title → abstract → §1 → §5 → §6 do not carry a single consistent commitment. The title says "Evidence from…", which is neutral. The abstract says engagement "correlated positively" (associational) and then that increasing engagement "is a promising lever" (interventional). §1 promises careful separation of pattern from cause. §5 asserts causation outright, then in its third paragraph reverts to marginal-association language. §5.1 disavows transferability. §6 asserts worldwide generalisability and a "dependable strategy." Each hedge in the manuscript is contradicted by an unhedged assertion elsewhere, and the strongest claims sit in the two places — abstract and conclusion — most readers will actually read. This is not a wording problem to be smoothed in copyediting; the manuscript has no single position on what it found.

#### Title & Abstract

The title is appropriately restrained and I would not change it. The abstract is the more serious problem: it reports *r* = .42, a value that appears nowhere in the results, and closes on "increasing dashboard engagement is a promising lever for improving retention" — interventional framing over a correlational design. It also omits the design descriptor (observational, cross-sectional), the single-course scope, and the fact that the perceived-control comparison rests on 87 respondents rather than 142. An abstract carrying an effect size the results section contradicts is, on its own, sufficient reason to return a manuscript before full review.

#### Conclusion

§6 answers a question the study did not ask. The research question in §1 is "whether students who engage more with a learning analytics dashboard are more likely to persist in and complete their course" — an associational question that §4.2 answers, modestly, in the affirmative. §6 instead answers "should institutions invest in dashboards worldwide," and answers it affirmatively with the word "dependable." It also introduces "encouraging students to engage" — induced engagement — which was never observed. The conclusion is the single section most in need of being rewritten from scratch against the evidence actually reported.

### Questions for Authors

1. Which correlation is correct — the *r* = .42 in the abstract or the *r* = .24 in §4.2 — and on which value do the conclusions in §5 and §6 rest? Please provide the full analysis output for the retention association, including *N*, the coefficient with a confidence interval, and the statistic used for a dichotomous outcome.

2. §1 commits to distinguishing pattern from causal story; §5 states that engagement "improved" retention and "therefore raises the probability" of completion. What in the design licenses that verb? If nothing does, will the authors retract the causal language throughout §5 and §6?

3. Was recruitment a random sample of enrolled students (§3.2, first paragraph) or a voluntary response to an LMS announcement with non-respondents excluded (§3.2, second paragraph)? Please report the response rate and any comparison between respondents and the full enrolment.

4. Recruitment occurred midway through the term. How many students had already withdrawn before the recruitment window, and how are they represented in a retention outcome?

5. §2 cites Ferro & Nakamura (2021) as showing dashboards "reliably improve outcomes for lower-achieving students," while the reference list titles that work *When dashboards demotivate: Peer comparison and the lower-achieving student*. What does that source actually report, and does the equity rationale in §2 survive the correction?

6. Please state the ethics-approval body and protocol number, and the basis on which dashboard activity data were analysed for research when §3.2 states that students were not informed of this use. What de-identification was applied?

7. On what evidence does §6 extend to "institutions worldwide" a finding from one section of one course, when §5.1 states the dashboard "differs from those deployed elsewhere"?

8. The study measured spontaneous dashboard opening. What is the basis for the recommendation that institutions *encourage* engagement, and would the observed association be expected to hold under induced use?

9. Given that §2 raises the demotivation account (Osei, 2020) and §3.1 describes a peer-comparison band, why is that competing account never tested against these data — for instance, among lower-performing students?

### Minor Issues

- Table 1 reports a final-exam variable (0–100) that §3.3 Measures never defines; the measure first appears in Results.
- Table 1 mixes precision conventions: perceived control at three decimals (3.847) against two-decimal SDs and one-decimal means elsewhere.
- Table 2's caption and content report only *n*, *M*, and *SD*; the *t* statistic and *p* value appear in text only, and the group *n*s do not reconcile with the accompanying prose.
- §4.2 reports a correlation for a dichotomously coded outcome (§3.3) without naming the coefficient type or reporting an interval.
- The sessionization rule (30 minutes of inactivity) is attributed to "the platform's default"; a platform default adopted as a construct boundary should be justified as a research decision.
- The dashboard artifact is described only in general terms (§3.1) — no platform, version, screenshot, or specification of what students saw — so no other site can determine whether their dashboard is the same class of object.
- The claim that "single-item overall ratings are common in dashboard studies to limit survey burden" (§3.3) carries no citation.
- Nine of fifteen reference entries are never cited in text; all fifteen DOIs fall in the `10.5555` reserved-for-examples prefix range.
- §3.1 states the course "enrolled several hundred students" without a figure, which prevents the reader from computing a participation rate against the 142 analysed.
- No integrity note: the manuscript contains no instruction-like content addressed to reviewers, so no prompt-injection concern arises.

---

contract_role: eic

## Dimension Scores

### D1: methodology_rigor

score: block

My Phase 1 commitment set `block` for, among other patterns, "a causal claim is stated in the results or conclusion while the design as described is observational and no confounding adjustment or identification argument is offered anywhere." That trigger is met exactly: §3.1 declares an observational cross-sectional design, §5 states that "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course," and no adjustment, matching, or identification argument appears anywhere in §3.4 or §4. A second committed `block` trigger — a quantitative claim presented with no recoverable basis — is met in a narrower but real form: the retention association is reported at two irreconcilable magnitudes (abstract *r* = .42 vs. §4.2 *r* = .24), so no reader can determine which quantity the paper is asserting or audit it. The design is otherwise legible enough that I would not have fired on under-specification alone; the causal-claim trigger and the unauditable effect size are what carry this score.

### D2: domain_accuracy

score: block

My Phase 1 `block` trigger included "prior work is materially misrepresented in a way that props up the paper's contribution claim (a cited study reported as finding the opposite or a stronger result than it did)." §2 attributes to Ferro & Nakamura (2021) the finding that dashboards "reliably improve outcomes for lower-achieving students"; the manuscript's own reference list titles that work *When dashboards demotivate: Peer comparison and the lower-achieving student*. On the manuscript's internal evidence the source is cited for the inverse of what it reports, and §2 explicitly erects the "equity-oriented rationale for institutional dashboard deployment" on that sentence — the misrepresentation is load-bearing, not incidental. The same trigger's first clause is independently satisfied by §6, which presents dashboard-driven retention improvement as a "dependable strategy" when §2 itself documents the literature as mixed. I record that the bibliography as a whole (9 of 15 entries uncited, all DOIs in the `10.5555` reserved-example range, no field-canonical anchor) cannot be verified from within the manuscript; that is the domain seat's substantive determination, and my score here does not depend on it.

### D3: argumentative_coherence

score: block

My Phase 1 `block` trigger — "the paper hedges to association in one section and recommends causal intervention in another without bridging argument," and "the conclusion asserts something the reported results do not support, or asserts it at a strength the paper's own limitations section disavows" — is met twice over. §1 promises to distinguish pattern from causal story; §5 asserts causation; §5's own third paragraph reverts to marginal association; §5.1 disavows transferability; §6 asserts worldwide generalisability and a "dependable strategy." The abstract's *r* = .42 and §4.2's *r* = .24 mean the manuscript's evidentiary premise is itself unstable. Removing the causal step removes the contribution as currently framed, which is precisely the condition I committed to treat as `block`.

### D4: cross_disciplinary_relevance

score: warn

My Phase 1 `block` trigger for this dimension was deliberately narrow — genuine inaccessibility of the central argument to one of the two constituent audiences, or an explicit bridging claim asserted with no substantiation anywhere. Neither is met. The analytics apparatus is described in terms a higher-education-studies reader can follow, and the SRL framing is introduced for the analytics reader. The `warn` triggers are met plainly: the retention framing is decorative rather than engaged (no persistence theory is developed and the retention literature is invoked but never analysed against these data); the institutional context is thin (institution type, enrolment figure, and student population are never given, so transferability is left to the reader to guess); the SRL bridging claim — that a single global perceived-control item indexes the regulatory construct the theory implicates — is asserted without argument, though the paper's central retention claim does not rest on it; and §6's implications are addressed to "institutions worldwide" rather than to any identifiable actor. This is uneven exposition and an unsubstantiated secondary bridge, not inaccessibility.

### D5: writing_and_structure

score: warn

Sentence-level prose is clear, the IMRaD structure is complete and proportionate to a short article, and both tables are legible and referenced in text. The `warn` triggers I committed to are met: the abstract over-claims relative to the body and carries a value the body contradicts; exhibits are under-interpreted (Table 2 shows group means but the inferential statistics live only in prose, and Table 1 introduces a variable Methods never defines); precision conventions are inconsistent; and the reference apparatus is internally inconsistent with the text (nine uncited entries). I considered `block` on the ground that numbers in text and exhibits disagree — Table 2's 66 + 61 = 127 against the same paragraph's "all 142 students" is a genuine text-exhibit disagreement. I hold at `warn` because the disagreement is a symptom of the reporting failure already scored at `block` under D1 rather than a presentation defect that independently obstructs evaluation: the organisation is orderly and a reader can locate what was done and what was claimed. Recording for the synthesiser that this dimension is normal-priority and, per the contract, fires no failure condition either way.

## Failure Condition Checks

### F1

fired: true

Predicate: any mandatory dimension scores `block`. D1 (methodology_rigor), D2 (domain_accuracy), and D3 (argumentative_coherence) are all mandatory and all score `block`. Severity 90.

### F2

fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. Three mandatory dimensions (D1, D2, D3) score `block`, which is worse than `warn`. Severity 70. (The `majority` quantifier on this condition is panel-level machinery for the synthesiser; I evaluate the predicate against my own scores only.)

### F3

fired: false

Predicate: any high-priority dimension scores `block`. The only high-priority dimension is D4 (cross_disciplinary_relevance), which scores `warn`, not `block`.

### F0

fired: false

Predicate: every mandatory dimension scores `pass`. D1, D2, and D3 all score `block`.

## Review Body

From the editorial chair, this manuscript presents two distinct problems, and they need to be kept separate because they call for different responses.

The first is a threshold problem. A manuscript whose abstract reports *r* = .42 and whose results report *r* = .24 for the same association has not established what it found. That discrepancy is not a typographical matter I can wave through to referees, because every substantive judgment downstream — is the effect worth reporting, does it support the discussion's marginal-benefit reading, does it support §6's recommendation at all — turns on which number is real. Adjacent discrepancies visible on the manuscript's face compound this: a *t* statistic in §4.3 with degrees of freedom unreachable from any sample the paper describes; a reported *p* whose value contradicts the same sentence's prose characterisation of the difference as small; a table whose group sizes do not sum to the count the accompanying paragraph asserts; and a final-exam variable that appears in Table 1 and in §4.3 without ever being defined in Methods. Individually any one of these is a correction. Together they mean the results section is not currently a reliable object for the rest of the panel to review. I record that determination as an editor; the arithmetic itself is the methodology seat's to certify.

The second problem is the one I own directly, and it is not fixable by correcting numbers. This manuscript states the field's cardinal inferential standard and then breaches it. §1 promises care in distinguishing pattern from causal story. §2 cites Ibarra (2023) on causal language outrunning evidence in correlational learning analytics, and says the study was designed "to be transparent about its correlational scope, while acknowledging that the appetite for actionable findings creates pressure toward stronger claims than the data can bear." Then §5 opens: "dashboard engagement improved course retention… increasing dashboard engagement therefore raises the probability that a student completes the course." Then §6: "associated with, and raises, course retention," "a dependable strategy," "generalizable," "institutions worldwide." The manuscript diagnoses the pressure and then yields to it in the two sections that carry the paper's public claim.

I want to be precise about why this weighs more heavily than ordinary overclaiming. An author who does not know the standard can be taught it in revision. This manuscript demonstrates that the standard is known — it is articulated with some sophistication in §2 and honoured in §5's third paragraph and in §5.1 — and is nonetheless not applied where it would cost the paper its headline. The hedging and the assertion coexist in the same document, which means a revision that only softens verbs would leave the underlying disposition untouched. What is required is a manuscript that decides what it is claiming and lets the design set the ceiling.

Three further matters bear on my decision without belonging primarily to my seat. The apparent inversion of Ferro & Nakamura (2021) is not a citation-style defect: §2 builds an equity rationale on a source whose own title states the opposite finding, and an equity argument resting on a reversed source is worse than no argument. That the bibliography also contains nine uncited entries, no recognisable canonical anchor, and DOIs entirely within a reserved-example prefix means no literature-based claim here can be treated as supported until the references are independently verified. The sampling description contradicts itself between two adjacent paragraphs, and the half that survives — mid-term voluntary recruitment with non-respondents excluded — structurally omits the students most informative about non-retention. And §3.2 states plainly that students were not told their dashboard activity would be analysed, with no ethics approval, de-identification, data-availability, funding, or conflict-of-interest statement anywhere in the manuscript; §6 then recommends worldwide scale-up of the practice. Those three findings belong to the domain, methodology, and cross-disciplinary seats respectively, and I defer to their determinations; I note here only that each is independently sufficient to prevent this manuscript from proceeding in its current form.

On fit and contribution, which are mine: the topic belongs in this journal and the question is worth asking, but §2 itself establishes that the field already holds an abundance of single-site correlational dashboard studies and an explicit audit of their causal overreach. This manuscript adds one more instance of that pattern, and — because it names the pattern first — an instance whose framing invites the objection more sharply than a naive paper would. The genuinely interesting move available in these data is untaken: §2 raises the demotivation account and §3.1 describes a peer-comparison band, yet the competing account is never tested against the data among the students it concerns. That analysis, on a corrected sample with an appropriate model for a dichotomous outcome, would be a contribution. What is here is not.

On the developmental question — is this salvageable — my editorial view is that the claim strength, the citation accuracy, and the reporting apparatus are all correctable, and the authors clearly have the competence to correct them. Whether the data can answer the retention question at all after the sampling problem is properly stated is a harder question that I do not think the manuscript currently permits anyone to answer, and it is the methodology seat's to judge. The reason my recommendation is Reject rather than Major Revision is not any single defect but their conjunction across three mandatory dimensions, plus the ethics disclosure gap which cannot be cured retrospectively by rewriting. A resubmission built on corrected analysis, a documented ethics basis, verified references, and claims held to the design's ceiling would be welcome; it would be a materially different manuscript, and it should be assessed as a new submission rather than as a revision of this one.

To the authors: the topic is worth your effort, your literature review shows you know this field's arguments, and your limitations section shows you can see your own study clearly. The distance between §5.1 and §6 is the whole problem, and it is a distance you already know how to close.

## Editorial Decision

Contract precedence: F1 (severity 90) and F2 (severity 70) both fired against my scores. Highest severity wins; F1 governs.

editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 1 (Methodology)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** As Peer Reviewer 1 this is my primary charge: whether the study's design can actually answer the question it poses, and whether a reader could reconstruct the study from what is written. For a learning-analytics deployment paper of roughly 2,500 words reporting on dashboard engagement and course retention, the operative questions are whether the design supports the inferential claim being made, whether the exposure variable (dashboard engagement) and outcome (retention) are defined and measured in ways that are auditable, whether the analytic model matches the data structure (students nested in courses, time-varying exposure, non-random uptake), and whether the reporting carries the quantities a methodologist needs — sample and attrition accounting, effect sizes with intervals, assumption checks, missing-data handling, and enough procedural detail plus data/code/ethics disclosure for another team to attempt replication. Contract-relevant: this dimension covers both the design layer and the statistical-reporting layer; a defensible design with unreportable statistics fails it just as a clean regression table on an uninterpretable design does.

**D2 — domain_accuracy (mandatory).** Read through my seat's lens, this is not a literature-completeness judgment (Reviewer 2's charge) but a narrower methodological one: whether the paper's use of learning-analytics and retention constructs is technically correct where those constructs carry measurement consequences. Retention, persistence, completion, withdrawal, and pass rate are distinct operationalizations in higher-education studies with distinct denominators; dashboard "engagement" spans logins, sessions, dwell time, and feature use, which are not interchangeable exposures. I assess whether prior findings the paper invokes as methodological warrant (for instance, a cited effect size used to justify a sample, or a prior instrument reused here) are represented accurately enough to bear that weight, and whether reported statistics are internally consistent with each other and with the stated Ns.

**D3 — argumentative_coherence (mandatory).** Under my remit this is the inference chain: whether what the data can support and what the paper concludes are the same claim. For an observational deployment study of a voluntary tool, the load-bearing risk is the slide from association to causation — self-selection into dashboard use by already-persisting students, reverse causation (students who are staying engaged log in more, rather than logging in keeping them enrolled), and survivorship in the analytic sample when withdrawn students stop generating telemetry. I evaluate whether the paper's stated conclusions, abstract, and implications sections are calibrated to its design, and whether any fallacy in my checklist — ecological inference across course-level aggregates, uncorrected multiple comparisons across dashboard features, selective reporting of the significant subset — actually undermines the central argument rather than sitting as a minor blemish.

**D4 — cross_disciplinary_relevance (high priority).** Reviewer 3 owns interdisciplinary impact; my contribution is bounded to methodological legibility. Learning analytics draws readers from education research, institutional research, HCI, and data science, each with different default conventions for what "engagement" and "retention" mean and what counts as adequate causal warrant. I assess whether the methods are described in field-neutral enough terms that an adjacent-field methodologist can evaluate them without insider knowledge of one platform's telemetry schema — whether variables are defined before they are used, whether platform-specific jargon is glossed, and whether any claim that borrows authority from another discipline (a causal-inference estimator, a psychometric property, an economic retention model) is substantiated to that discipline's standard rather than named in passing.

**D5 — writing_and_structure (normal priority).** My scope here is confined to whether the exposition lets the methodology be audited at all. A 2,487-word manuscript is short for an empirical deployment study, so the risk is compression: methods details displaced into prose asides, results reported without the tables that would make them checkable, figures whose axes or denominators are unlabelled, or a structure that separates a procedure from the result it produced. I assess organisation, figure/table adequacy, and venue-convention adherence only insofar as they impede or enable methodological verification; pure style, prose quality, and formatting preferences are outside my seat.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for` — An explicitly named design (observational cohort, quasi-experiment, RCT, pre-post) and stated unit of analysis; operational definitions of dashboard engagement (metric, granularity, aggregation window) and retention (denominator, censoring point, term boundary); sampling frame, N, number of courses/terms, and attrition accounting from enrolled to analytic sample; whether uptake was voluntary and whether any selection adjustment (covariate control, propensity/matching, fixed effects, IV, difference-in-differences) is used; whether the model accounts for clustering of students within courses/instructors and for time-ordering between exposure and outcome; effect sizes with 95% CIs alongside any p-values, not p-values alone; a priori power or precision justification, or a Type II discussion attached to null results; assumption checks appropriate to the model (linearity, independence, multicollinearity/VIF, proportional hazards if survival, separation if logistic); missing/incomplete-telemetry amount, proportion, and handling method; data/code/instrument availability and an IRB or equivalent ethics statement; enough procedural detail (platform, deployment period, what students saw, what triggered logging) for replication.
- `what_triggers_block` — The exposure or outcome is never operationally defined, or the analysis is not identifiable from the text (no named model, or a model whose form cannot be inferred), such that the reported result cannot be reproduced or checked in principle; OR the analytic sample is undocumented (no N, or an N that shifts across sections without reconciliation) with no attrition accounting; OR the design cannot support the estimand the paper reports (e.g., a causal/effect estimate presented with no comparison condition, no adjustment, and no acknowledgement of that gap); OR results are reported with neither effect sizes nor intervals nor test statistics — bare significance labels only; OR analytic decisions appear outcome-contingent (multiple engagement metrics, outcome windows, or subgroups evidently tried with only the significant configuration reported, no correction and no pre-specification).
- `what_triggers_warn` — Design and estimand are coherent but a discrete piece of the rigor package is absent or thin: effect sizes present but no CIs (or CIs with no interpretation); no power/precision justification for a study whose null or small-N results depend on it; clustering acknowledged in prose but not in the model; assumption checks unreported for a model that requires them; missing data mentioned without amounts or handling method; sampling from a single course/term/institution with representativeness left unaddressed; reproducibility affordances partial (methods narratively adequate but no data/code availability statement, or no ethics/IRB record); measurement of engagement defensible but single-indicator with no reliability or sensitivity check across alternative operationalizations.

### D2: domain_accuracy
- `what_to_look_for` — Whether "retention" is pinned to a specific, conventional operationalization (course completion vs. next-term re-enrolment vs. non-withdrawal by census date) and used consistently thereafter, with the denominator stated; whether "engagement" is disaggregated into the specific telemetry it is computed from and not silently swapped between definitions across abstract, methods, and discussion; whether any learning-analytics construct with an established technical meaning (early-alert, at-risk flag, predictive model performance metrics, dashboard nudge) is used in its standard sense; whether cited prior results that carry methodological weight — a benchmark effect size, a reused or adapted instrument, a reported base rate used to size the study — are represented at the right magnitude and from the right design; internal arithmetic consistency of Ns, percentages, degrees of freedom, and subgroup totals against reported statistics.
- `what_triggers_block` — A load-bearing statistic or construct is wrong in a way that invalidates the reported finding: reported numbers are mutually inconsistent and cannot both be true (e.g., subgroup Ns exceed the total, percentages irreconcilable with the stated denominator, test statistic incompatible with the reported df/N); OR the outcome construct changes meaning between where it is defined and where it is concluded upon, so the headline claim is about a different quantity than the one measured; OR a cited prior finding is materially misstated (wrong direction, wrong order of magnitude, or attributed to a design that could not have produced it) and that misstatement is what licenses the paper's method or interpretation.
- `what_triggers_warn` — Terminology is loose but recoverable: retention and persistence used interchangeably without harming the analysis; engagement defined once but described with drifting labels later; a domain metric used correctly but without stating the convention followed, leaving the reader to guess the denominator; a prior result invoked with imprecise characterization that does not change the methodological warrant; minor numeric or unit slips (rounding inconsistency, a percentage that misses by less than a rounding step) that do not alter any conclusion.

### D3: argumentative_coherence
- `what_to_look_for` — Whether the verbs used for the main finding (associated with / predicts / increases / improves / causes) match the design's warrant, checked separately in title, abstract, results, discussion, and any practice implications — abstract-to-discussion escalation is the pattern I will scan for specifically; whether self-selection into voluntary dashboard use is named and addressed, not merely noted as a limitation and then ignored downstream; whether reverse causation (persisting students generate more telemetry) is explicitly considered; whether survivorship is handled — students who withdraw stop producing engagement data, so the exposure is partly a function of the outcome; whether course-level aggregates are used to make student-level claims (ecological inference) or vice versa; whether non-significant and unfavourable results are reported alongside favourable ones; whether the limitations section actually constrains the conclusions drawn elsewhere or is decorative; whether recommendations for practice (deploy this dashboard to improve retention) exceed what an observational association supports.
- `what_triggers_block` — The central claim is causal or prescriptive while the design is observational and unadjusted, and the paper neither adjusts nor qualifies — i.e., the conclusion the abstract and implications assert is one the data cannot support at all; OR a fallacy sits on the inferential main line rather than the margins (exposure defined so that it is mechanically entailed by the outcome, so the reported association is definitional; or student-level conclusions drawn purely from course-level aggregates); OR evidence presentation is internally contradictory — the results section and discussion assert opposite or incompatible readings of the same analysis; OR selective reporting is evident and the surviving argument depends on it.
- `what_triggers_warn` — The claim is calibrated in the results section but overstated in one downstream location (abstract hedge dropped, or a practice implication stated more strongly than the estimate warrants); OR self-selection, reverse causation, or survivorship is acknowledged in limitations but not carried into how the finding is worded; OR a plausible confounder (prior GPA, course difficulty, instructor, credit load, financial-aid status) is unaddressed without argument for why it is ignorable; OR multiple comparisons across engagement metrics or subgroups are present without correction but with the exploratory status stated; OR the argument holds but relies on an unstated premise (that dashboard viewing is the active ingredient rather than a proxy for a general engagement disposition) that is never surfaced.

### D4: cross_disciplinary_relevance
- `what_to_look_for` — Whether every construct is defined at first use in terms an adjacent-field reader (institutional researcher, HCI scholar, applied statistician) can evaluate without platform-insider knowledge; whether platform- or vendor-specific telemetry terms are glossed into generic measurement language; whether the retention outcome is stated in a way that maps onto how higher-education studies conventionally define persistence, so external readers can situate the effect; whether any imported method — a causal-inference estimator, a survival model, a psychometric reliability claim, a machine-learning performance metric — is applied and reported to that source discipline's standard, including its own assumption set; whether interdisciplinary framing claims ("this bridges learning analytics and retention theory") are backed by an actual methodological move rather than asserted.
- `what_triggers_block` — A method borrowed from another discipline is applied in a way that is invalid by that discipline's standards and the paper's conclusion rests on it (e.g., a causal estimator invoked without its identifying assumption stated or plausibly met; a predictive-performance metric reported in a way that misrepresents what the model does); OR the methodology is unevaluable from outside the specific platform — core variables are defined only by proprietary/undocumented telemetry labels with no generic operationalization, so no adjacent-field reviewer could assess or reuse the design.
- `what_triggers_warn` — Constructs are defined but unevenly, with some jargon left unglossed or defined only implicitly by context; the retention definition is internally clear but not related to any standard higher-education convention, making external comparison hard; an interdisciplinary implication is claimed with no methodological substantiation but also with no weight placed on it; the paper is legible to learning-analytics insiders but would require a reader from institutional research or statistics to reconstruct definitions from scattered mentions.

### D5: writing_and_structure
- `what_to_look_for` — Whether a distinct methods section exists and contains the procedures (rather than scattering them across introduction and results); whether results are reported in tables/figures adequate to check the analysis — labelled axes, stated denominators, Ns per cell, units, and a caption that states what was analysed; whether every analysis described in methods has a corresponding reported result and vice versa; whether the sequence lets a reader trace question → design → measure → analysis → result → conclusion without backtracking; whether the manuscript's length is used on the parts that carry the inference or spent on framing at the expense of methods detail; whether venue conventions for statistical reporting (APA 7.0 or equivalent: italicized symbols, correct decimals, leading zeros, p-value formatting) are followed.
- `what_triggers_block` — Structural failure that makes the methodology unauditable regardless of its quality: no identifiable methods section and no equivalent procedural account anywhere; OR results referenced in the text but never presented in any retrievable form (no table, no figure, no in-text numbers); OR figures/tables that are the sole evidence for the main claim are unreadable as presented (no axis labels or denominators, or a caption that contradicts the text).
- `what_triggers_warn` — Methods present but compressed such that at least one procedural element must be inferred; a table or figure missing a label, unit, N, or note that the reader can still work around; an analysis mentioned in methods without a matching result (or a result appearing with no methods antecedent); statistical-reporting format deviations from venue convention that do not obscure the numbers; organisation that requires backtracking to connect a procedure with its result; word budget visibly skewed toward framing with methods detail thinned as a consequence, without any single element rising to unauditable.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Methodology Review Report (Peer Reviewer 1)

### Reviewer Identity

Quantitative methodologist in educational measurement and applied statistics, specializing in the analysis of dichotomous educational outcomes (persistence, withdrawal, completion) and in selection bias in observational studies of educational technology; teaches a doctoral seminar on why median splits and bivariate correlations produce inflated and unreplicable findings; serves as statistical reviewer for two education journals.

### Overall Recommendation

**Reject** (resubmission possible only after redesign and full reanalysis, not after correction of the reported numbers).

### Confidence Score

5

### Summary Assessment

This manuscript cannot be evaluated on the merits of its finding because the reported statistics are not mutually consistent, and it cannot be repaired by correcting them because the sampling design is incompatible with the outcome it studies.

Six independent numerical contradictions are present in the text as submitted. The abstract reports *r* = .42 and §4.2 reports *r* = .24 for the same association. §4.3 reports *t*(156), a degrees-of-freedom value unreachable from a sample of 142 (or the 87 who answered the perceived-control item). §4.3 reports *t*(140) = 1.31 with *p* = .008; that pairing is arithmetically impossible. Table 2's group sizes sum to 127 in a paragraph asserting that all 142 students were classified. Table 2's weighted mean final-exam score (70.66) does not equal Table 1's reported 71.3. And Table 1 reports a final-exam variable that §3.3 Measures never defines. These are findings of fact, not judgments.

Independently of the numbers, the design has two defects that reanalysis cannot reach. Recruitment occurred mid-term by voluntary announcement, so students who disengaged or withdrew before the recruitment window — the students most informative about non-retention — are structurally absent from a study whose outcome is retention. And the exposure window is not censored at withdrawal, so non-retained students mechanically accumulate fewer dashboard sessions than retained students by construction. Both operate in the direction of the reported association.

### Strengths

1. **Explicit, auditable exposure operationalization.** §3.3 states the metric (distinct dashboard-opening sessions), the sessionization rule (30-minute inactivity), and the accumulation window. This is more specification than many trace-data studies provide and makes the exposure at least checkable in principle.

2. **Precise retention coding, including the ambiguous case.** §3.3 states that students enrolled but not sitting the final are coded as not retained, rather than leaving the boundary case implicit. The definition is narrower than the paper's later use of it, but the definition itself is clean.

3. **Author-declared analytic simplification.** §3.3 explicitly labels the median split "a coarse simplification of a continuous measure … adopted for interpretability rather than statistical efficiency." Naming a known-suboptimal choice rather than presenting it as neutral is a real reporting virtue, even though the choice itself is not defensible here.

4. **The results section is arithmetically reconstructible where the abstract is not.** The §4.2 pair (*r* = .24, *p* = .004) is exactly what a point-biserial correlation at *N* = 142 produces (*t*(140) = 2.93). This locates at least one discrepancy — the *r* = .42 — in the abstract rather than in the analysis, which is useful diagnostic information for the authors.

5. **§2 states the correct methodological standard.** The literature review correctly identifies click-based engagement as a rough proxy (Vandermeer, 2023) and correctly names causal overreach as the field's recurring failure (Ibarra, 2023). The author demonstrably knows the standard the manuscript then does not meet.

### Weaknesses

1. **The reported statistics are mutually inconsistent, so no reported result can currently be relied upon.**
   *Problem.* Six contradictions, enumerated in Results Presentation below. *Why it matters.* An unreconciled effect-size discrepancy between abstract and results means the manuscript does not currently state what it found; an impossible *t*/*p* pairing and an unreachable *df* mean the tests as reported were not run on the samples as described. Reviewers cannot assess an inference whose inputs are indeterminate. *Fix.* Re-derive every reported statistic from the analysis file, report *N* per test, and supply a table mapping each test to the exact subsample it used. Do not resubmit with the discrepancies patched in prose; supply the analysis script.

2. **Mid-term voluntary recruitment makes the retention outcome structurally unrecoverable — a design defect, not an estimation defect.**
   *Problem.* §3.2 recruits by LMS announcement "midway through the term" and excludes non-respondents. Students who withdrew before that announcement never had the opportunity to enter the sample. *Why it matters.* This is left-truncation on the outcome. The sample is conditioned on having survived to the recruitment window, so the observed relationship between engagement and retention is estimated inside a population from which the most informative non-retention cases have already been removed. Adding covariates, fitting a logistic model, or matching does not repair this — no estimator recovers cases that were never eligible for sampling. *Fix.* Retention must be studied on the full enrolled cohort with exposure measured prospectively from week 1, with survey participation treated as an auxiliary variable rather than as the sampling frame. With the present data, the retention question should be withdrawn.

3. **The exposure window is not censored at the outcome, so part of the association is mechanical.**
   *Problem.* §3.3 counts dashboard sessions "during the term"; §3.3 codes retention on completion of the final assessment. A student who withdraws in week 6 has six weeks in which to accumulate sessions; a student who completes has fifteen. *Why it matters.* Non-retained students are guaranteed a truncated exposure window by the definition of non-retention. Some unknown fraction of *r* = .24 is therefore arithmetic rather than behavioral, and it acts in the reported direction. *Fix.* Censor exposure at a common landmark that precedes any withdrawal (e.g., sessions in weeks 1–4 only), or model exposure as time-varying in a discrete-time hazard framework with the outcome measured after the exposure window closes. Report the landmark analysis as the primary result.

4. **The sampling section describes two incompatible designs, and neither is documented.**
   *Problem.* §3.2 paragraph 1 states participants were "drawn from the course enrollment using a random sample"; paragraph 2 describes an announcement-based voluntary opt-in with non-respondents excluded. These cannot both be true. Separately, the enrolled population is given only as "several hundred," so no participation rate is computable, and no attrition accounting from enrolled to analytic sample appears anywhere. *Why it matters.* Which design was used determines whether selection is ignorable; without the enrolled *N*, the reader cannot judge how selective 142 is. *Fix.* State the actual recruitment procedure, give the exact enrolled *N*, report the participation rate, and compare respondents to non-respondents on any administrative variable available (prior GPA, credit load, week-of-term activity).

5. **The analysis plan does not match the outcome type, and the reporting package is largely absent.**
   *Problem.* Retention is dichotomous (§3.3) yet the primary association is a Pearson (i.e., point-biserial) correlation, never named as such, with no covariate adjustment, no logistic or hazard model, no confidence interval, no odds ratio or risk difference, and — critically — no reported retention base rate anywhere in the manuscript. A continuous predictor is then dichotomized at its median for the group comparisons. There is no a priori power analysis, no assumption check of any kind, no correction across the three reported tests, and no characterization of the 38.7% item non-response on perceived control (142 → 87) beyond listwise exclusion. *Why it matters.* Without the retention base rate the association is uninterpretable and no institutionally meaningful quantity (risk difference, number needed) can be derived; without a CI the precision is unknown; the median split discards variance the study already has and, at these group sizes, is the least efficient use of the data. *Fix.* Report the retention rate and the 2×2 cross-tabulation; fit logistic regression of retention on continuous landmark-window engagement with prior achievement, prior LMS activity, and credit load as covariates; report OR with 95% CI and the marginal risk difference; retain engagement as continuous throughout; report an a priori or sensitivity power analysis; compare item responders to non-responders.

### Detailed Comments

#### Research Questions & Hypotheses

§1 poses a clear and answerable question ("whether students who engage more with a learning analytics dashboard are more likely to persist in and complete their course") and correctly frames it as associational. No hypotheses are stated formally, which is acceptable for an exploratory observational study, but the absence of pre-specification becomes consequential given that three tests are reported and only the framing of the favourable one is carried into the Discussion.

#### Research Design

The design is named ("observational, cross-sectional," §3.1) and the naming is honest. The problem is the mismatch between that design and the estimand: §5 and §6 report an effect ("dashboard engagement improved course retention," "raises the probability that a student completes the course," "a dependable strategy"). A cross-sectional observational design with no comparison condition, no adjustment, and no identification strategy cannot yield an effect. §1's stated commitment to "distinguish the pattern in the data from the causal story" is not kept.

There is also an internal design contradiction: §3.1 calls the design cross-sectional, but retention is by construction an end-of-term outcome and engagement accumulates across the term. The study is a single-cohort prospective observational design with retrospectively assembled logs and a mid-term cross-sectional survey layer. Calling it cross-sectional obscures the time-ordering problem rather than resolving it.

#### Sampling Strategy

Covered in Weaknesses 2 and 4. Two further points. First, the median split cut point is derived from the 142-student analytic sample, but the perceived-control comparison uses only the 87 item responders; those 87 are therefore not median-split within themselves, and the resulting groups are of unstated size. Second, sampling is from a single course, a single section, a single term, and a single institution, with representativeness never addressed — and §6 nonetheless generalizes to institutions "worldwide."

#### Data Collection

The dashboard artifact is described only as displaying "engagement metrics, assignment progress, and a peer-comparison band" (§3.1) — no version, no screenshot, no statement of what a student actually saw on opening it. Since dashboard *sessions* is the exposure, what a session exposed a student to is a load-bearing measurement fact, and it is absent. The 30-minute sessionization threshold is adopted as "the platform's default": an inherited platform artifact is being treated as a research construct without justification or sensitivity analysis. A supplementary analysis at alternative thresholds (e.g., 15 and 60 minutes) would establish whether the association is robust to this choice.

Perceived control is a single global item asserted, without citation, to be conventional ("single-item overall ratings are common in dashboard studies to limit survey burden," §3.3). No reliability evidence, no validity argument, no distributional check beyond a mean and SD.

#### Analysis Methods

§3.4 is three sentences and names only "Pearson correlations," "independent-samples t-tests," "standard statistical software," and α = .05. The software is not named or versioned. No assumption is tested or reported: not normality, not homogeneity of variance (relevant given Table 2's SDs of 11.1 vs 13.0 at unequal *n*), not the appropriateness of a Pearson coefficient with a dichotomous variable, not the right-skew in dashboard sessions that §4.1 itself reports and then never accommodates. Whether Student's or Welch's *t* was used is unstated. No effect size accompanies either *t*-test. No correction is applied across three tests, and no exploratory status is declared.

#### Results Presentation

The six verifiable contradictions:

1. **Abstract *r* = .42 vs. §4.2 *r* = .24.** These imply 17.6% and 5.8% of variance respectively — a threefold difference. The §4.2 pair (*r* = .24, *p* = .004) is internally coherent at *N* = 142; *r* = .42 at *N* = 142 would yield *p* < .001. The abstract figure is not reconcilable with the results section by any rounding or transcription account.

2. **§4.3, *t*(156) = 3.02.** *df* = 156 requires *n*₁ + *n*₂ = 158. The maximum available is 142; the perceived-control item was answered by 87, implying *df* = 85. 156 is unreachable from either. (The reported *p* = .003 is compatible with *t* = 3.02 at any of these *df*, so *p* does not disambiguate — the *df* itself is the error.)

3. **§4.3, *t*(140) = 1.31, *p* = .008.** *t*(140) = 1.31 corresponds to *p* ≈ .19 two-tailed. The reported *p* also contradicts the manuscript's own prose two sentences earlier ("did not reach a comparable level," "the difference was small"), which describes a null result while reporting a *p* well below the stated α of .05.

4. **Table 2 sums to 127; the text says 142.** §4.3 states "All 142 students in the primary analytic sample were classified into engagement groups for this comparison," and *t*(140) independently implies *N* = 142. Table 2 reports 66 + 61 = 127. Fifteen students are unaccounted for, and *df* consistent with Table 2 would be 125.

5. **Table 2's weighted mean does not equal Table 1's.** (66 × 72.0 + 61 × 69.2) / 127 = 70.66, against Table 1's reported 71.3. The two tables are computed on different samples, and the manuscript never distinguishes them.

6. **Table 1 reports a final-exam variable that §3.3 Measures never defines.** An undeclared measure appears first in Results. Its scale (0–100), range, and provenance are given only in the table.

A seventh issue is logical rather than arithmetic and is the most consequential. §3.3 codes as *not retained* any student who "did not sit the final." Such students therefore have no final-exam score. If retention has any variance in the analytic sample — which it must, or *r* = .24 with retention would be undefined — then some of the 142 have no exam score, and the §4.3 assertion that "all 142 students … were classified into engagement groups for this comparison" cannot be true of a comparison of exam scores. Table 2's 127 is consistent with exactly such a silent exclusion. But conditioning the exam comparison on having sat the exam conditions on the outcome, and *t*(140) is then the wrong test statistic for the sample actually analysed.

Elsewhere: no *N* is given per row in Table 1 (dashboard sessions and perceived control are demonstrably computed on different subsamples — 142 and 87); Table 1 reports perceived control to three decimals (3.847) against two-decimal SDs; Table 2 carries no test statistic, no *p*, no effect size, and no CI. The retention rate — the single most important descriptive quantity in a retention study — is never reported.

Selective-reporting risk is moderate rather than severe: the null exam comparison is reported, which counts in the manuscript's favour, but only the favourable result is carried into the Discussion and Conclusion, and only the favourable result appears (at an inflated magnitude) in the abstract.

#### Reproducibility

Inadequate. No data availability statement, no analysis code, no software identification, no survey instrument beyond the single item's wording, no IRB or ethics-approval record, no funding statement, no conflict-of-interest declaration. §3.2 affirmatively states that "students were not informed that their dashboard activity data would be analyzed for this study," and no ethics review is documented anywhere — I flag the absence of the approval record as a reporting gap within my remit; the substantive consent question belongs to the ethics reviewer. Given the contradictions above, an independent analyst could not reproduce a single reported statistic from what is written.

**Statistical reporting completeness: Unacceptable.** Effect sizes: partial (one *r*; none for either *t*-test). Confidence intervals: absent. Power: absent, including for a null result the Discussion interprets. Assumption testing: absent. Missing data: 38.7% item non-response acknowledged only by implication, handling method inferable but unstated, no responder/non-responder comparison. APA 7.0 format: symbols are italicized and leading zeros are correctly omitted, but decimal precision is inconsistent (3.847 alongside 0.62) and *p*-values are reported without a consistent convention.

**Red flags.** Selective emphasis (favourable result only, in the abstract, at an inflated magnitude); an impossible *t*/*p* pairing; unexplained sample shifts across tests; dichotomization of a continuous predictor; three uncorrected tests. I do not conclude that p-hacking occurred — the pattern is at least as consistent with an analysis file that does not match the manuscript text — but the manuscript as submitted cannot rule it out, and only the analysis script can.

#### Methodological Fallacies Detected

- **Survivorship bias (primary).** Mid-term recruitment excludes pre-window withdrawals from a retention study (Weakness 2).
- **Reverse causation (unaddressed).** Both principal associations are equally readable in the opposite direction: students on track to persist keep opening the dashboard; students who feel in control of their learning are the ones who check their progress. The perceived-control comparison is fully concurrent, with no time ordering at all, yet §5 reads it directionally ("dashboards scaffold monitoring and adjustment").
- **Mechanical/definitional entailment.** Uncensored exposure windows guarantee part of the association (Weakness 3).
- **Endogeneity / omitted variables.** Prior achievement, prior LMS engagement, motivation, credit load, and financial circumstances are all unmeasured; the manuscript offers no argument that any is ignorable. §5.1 does not name confounding at all.
- **Conclusion exceeding data support.** §5 ("improved … therefore raises the probability") and §6 ("dependable strategy," "generalizable," "worldwide") assert causal and prescriptive claims from an unadjusted bivariate association in one course. §5.1's limitations are real but decorative: they constrain nothing stated in §5 or §6, and they omit selection, reverse causation, and causal identification entirely.
- **Uncorrected multiple comparisons.** Three tests, α = .05 throughout, no correction, no declared exploratory status.

One observation outside my remit, recorded for the domain seat rather than scored here: §2 cites Ferro & Nakamura (2021) as showing dashboards "reliably improve outcomes for lower-achieving students," while the reference list gives that work's title as *When dashboards demotivate: Peer comparison and the lower-achieving student*. If the reference list is accurate, the direction is inverted. I flag it because it is checkable; its assessment belongs to Reviewer 2.

I found no instruction-directed content in the manuscript addressed to reviewers or editors.

### Questions for Authors

1. Which correlation is correct, *r* = .42 or *r* = .24, and on what sample was it computed? Please supply the analysis script and the correlation's 95% CI.
2. From what sample does *t*(156) = 3.02 arise? *df* = 156 requires 158 observations; the manuscript reports 142 in the analytic sample and 87 respondents to the perceived-control item.
3. *t*(140) = 1.31 corresponds to *p* ≈ .19, not *p* = .008, and your own prose describes the difference as small and non-comparable. Which value is in error?
4. Table 2 reports 66 + 61 = 127 in a paragraph stating all 142 students were classified. What happened to the other 15, and what is the correct *df* for that test?
5. Students coded as not retained did not sit the final assessment and therefore have no exam score. How were they handled in the Table 2 comparison, and if they were excluded, how is that reconciled with "all 142 students"?
6. What is the final-exam measure, and why does it appear in Table 1 but not in §3.3 Measures? Why does Table 2's weighted mean (70.66) differ from Table 1's (71.3)?
7. Was the sample a random sample of the enrolled section or a voluntary opt-in with non-respondents excluded? §3.2 asserts both. What was the enrolled *N* and the participation rate?
8. What was the retention rate in the analytic sample? Please provide the 2×2 cross-tabulation of engagement group by retention status.
9. Was dashboard exposure censored at withdrawal? If not, how do you distinguish the reported association from the arithmetic fact that withdrawn students had fewer weeks in which to open the dashboard?
10. What is your basis for excluding reverse causation, given that both associations are concurrent and unadjusted?
11. Is there an ethics-approval record for this study, and can the analysis data and code be made available?

### Minor Issues

- §3.4 does not name the statistical software or version.
- Whether Student's or Welch's *t* was used is unstated; Table 2's SD ratio and unequal *n* make the choice consequential.
- Decimal precision is inconsistent within Table 1 (3.847 vs 0.62 vs 14.6).
- Table 1 gives no *N* per row despite rows being computed on different subsamples.
- Table 2 carries no test statistic, *p*, effect size, or CI.
- §3.1 labels the design "cross-sectional" while the outcome is end-of-term and exposure accumulates across the term.
- "Retention," "persistence," and "completion" are used interchangeably across abstract, §3.3, §5, and §6; §3.3 defines a single-course completion outcome, while §6 concludes about retention "across programs and disciplines."
- The claim that single-item overall ratings "are common in dashboard studies" (§3.3) carries no citation.

---

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: block

Multiple committed block triggers fired concurrently. (a) The analytic sample is undocumented and shifts across sections without reconciliation: 142 (§3.2, §4.3), 87 (§4.1), 158 implied by *t*(156), and 127 (Table 2); the enrolled population is given only as "several hundred," so no attrition accounting from enrolled to analytic sample exists. (b) The design cannot support the estimand: §5 and §6 report an effect and a prescription from an unadjusted bivariate association with no comparison condition, no adjustment, no identification strategy, and no acknowledgement of that gap in the Discussion. (c) Results are reported without intervals: no CI accompanies any estimate, and neither *t*-test carries an effect size. Additionally, an undeclared measure (final exam) enters first in Results, and §3.2 states two incompatible sampling designs. Independently of the reporting layer, mid-term voluntary recruitment left-truncates the sample on the outcome, and uncensored exposure windows make part of the association mechanical — defects no reanalysis of these data can reach.

### D2: domain_accuracy
score: block

Committed block trigger fired on internal inconsistency: reported numbers are mutually incompatible and cannot all be true — abstract *r* = .42 vs. §4.2 *r* = .24; *t*(156) unreachable from *n* ≤ 142; *t*(140) = 1.31 paired with *p* = .008 (true value ≈ .19); Table 2's 127 against the same paragraph's 142 and against *t*(140); Table 2's weighted mean 70.66 against Table 1's 71.3. A second committed block trigger also fired: the outcome construct changes meaning between definition and conclusion. §3.3 defines retention as remaining enrolled and completing the final assessment in one course; §6 concludes about "retention across programs and disciplines" for institutions "worldwide" — a different quantity from the one measured. A possible misattribution of Ferro & Nakamura (2021) is recorded above but is Reviewer 2's to assess and is not part of this score's basis.

### D3: argumentative_coherence
score: block

Committed block triggers fired. (a) The central claim is causal and prescriptive while the design is observational and unadjusted, and the paper neither adjusts nor qualifies: §5 states "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course"; §6 calls it "a dependable strategy … generalizable" for institutions "worldwide." §5.1's limitations constrain nothing asserted in §5 or §6 and omit selection, confounding, and reverse causation entirely. (b) Evidence presentation is internally contradictory: §4.3 reports *p* = .008 while the surrounding prose describes the same comparison as small and as not reaching a comparable level. (c) A defect sits on the inferential main line rather than the margins: exposure is accumulated over a window that terminates at the outcome for non-retained students, so the reported association is in part mechanically entailed by how the two variables are constructed.

### D4: cross_disciplinary_relevance
score: warn

Committed warn triggers fired; block triggers did not. Constructs are defined but unevenly. The retention definition is internally clear yet never related to any standard higher-education convention (course completion vs. non-withdrawal by census vs. next-term re-enrolment), so an institutional-research reader cannot situate the estimate — and the Conclusion then slides into the institutional sense of the term. The sessionization rule is inherited from "the platform's default" and treated as a construct without justification or sensitivity check. Perceived control is imported as a self-regulated-learning proxy with no psychometric substantiation (single item, no reliability, no validity argument, uncited convention claim), and no adjacent-field reader could evaluate it as a measure. No causal-inference estimator, survival model, or predictive metric is invoked at all, so the block trigger for an invalidly applied borrowed method does not apply; and the methodology, though thin, is not platform-opaque — the exposure is described in generic enough terms to be reconstructed elsewhere.

### D5: writing_and_structure
score: warn

Committed warn triggers fired; block triggers did not. A distinct Methods section exists and contains the procedures, and every in-text result is retrievable, so the manuscript is not unauditable on structural grounds. But: an undeclared measure (final exam) appears in Table 1 with no Methods antecedent; §3.4 compresses the entire analysis plan into three sentences, so software, test variant, and assumption handling must be inferred; Table 1 omits per-row *N* despite rows drawn from different subsamples; Table 2 omits the test statistic, *p*, effect size, and CI, and its group sizes contradict the adjacent text; and reporting-format conventions drift (inconsistent decimal precision). The word budget is visibly weighted toward framing — §1 and §2 run roughly as long as §3 through §5 combined — with methods detail thinned as a consequence.

## Failure Condition Checks

### F1
fired: true
Predicate: any mandatory dimension scores 'block'. D1 (methodology_rigor), D2 (domain_accuracy), and D3 (argumentative_coherence) are all mandatory and all score block. Severity 90 — highest of the fired conditions.

### F2
fired: true
Predicate: two or more mandatory dimensions score 'warn' or worse. Three mandatory dimensions (D1, D2, D3) score block, which is worse than warn. Severity 70.

### F3
fired: false
Predicate: any high-priority dimension scores 'block'. D4 (cross_disciplinary_relevance) is the sole high-priority dimension and scores warn, not block.

### F0
fired: false
Predicate: every mandatory dimension scores 'pass'. D1, D2, and D3 all score block.

## Review Body

This manuscript fails at a level prior to the assessment of its finding. Its reported statistics are not mutually consistent, and the pattern of inconsistency is not attributable to a single typographical slip: an effect size that differs threefold in variance-explained between abstract and results, a degrees-of-freedom value unreachable from any sample the manuscript describes, a *t*/*p* pairing that is arithmetically impossible and that contradicts the manuscript's own prose characterization of the same comparison, a table whose group sizes contradict the adjacent sentence and the test statistic reported for it, two tables whose final-exam means do not reconcile, and a measure that appears in Results without ever being defined in Methods. Each is checkable from the text alone. Until an analysis script is supplied, no reported value can be treated as evidence, and the substantive critiques from any seat apply to a results section whose contents are indeterminate.

Correcting the numbers would not make the study interpretable, and this distinction matters for the authors' revision planning. Two design features are outside the reach of reanalysis. First, recruitment occurred mid-term by voluntary announcement with non-respondents excluded, so students who disengaged or withdrew before the recruitment window could never enter the sample. In a study whose outcome is retention, the cases carrying the most information about non-retention are structurally absent. No covariate set, no logistic model, no propensity adjustment recovers observations that were never eligible for sampling. Second, dashboard sessions accumulate "during the term" while non-retention is defined by leaving before the final assessment, so withdrawn students have shorter exposure windows by construction. Some portion of the reported association is arithmetic rather than behavioral, and it runs in the direction the paper reports. A landmark design — exposure fixed to weeks 1–4, outcome measured thereafter, on the full enrolled cohort — would address the second problem, but only new data address the first.

The reporting package around the analysis is correspondingly thin. The outcome is dichotomous but the analysis is a point-biserial correlation never named as such, with no covariate adjustment and no logistic or hazard model. The retention rate itself — the base rate on which any institutional interpretation depends — is never reported, nor is the 2×2 cross-tabulation from which it could be recovered. No confidence interval appears anywhere. No assumption is tested. No power analysis supports a null result the Discussion nonetheless interprets. A continuous predictor is dichotomized at its median, discarding variance the study already possesses. Item non-response of 38.7% on the perceived-control measure is handled by exclusion with no responder/non-responder comparison. There is no data-availability statement, no code, no software identification, and no ethics-approval record — the last against a Methods section that affirmatively states students were not informed their behavioral data would be analysed.

What makes the manuscript's position harder rather than easier is that §2 states the correct standard and §5 violates it. The literature review correctly identifies causal overreach as the field's documented failure mode, and §1 promises to "distinguish the pattern in the data from the causal story." §5 then opens with "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course," and §6 recommends dashboards to institutions "worldwide" as "a dependable strategy." §5.1's limitations are genuine but constrain nothing asserted in §5 or §6, and they omit selection, confounding, and reverse causation entirely — the three threats that most directly bear on this design. Both principal associations are equally readable in the opposite direction; the perceived-control comparison is fully concurrent, with no time ordering whatsoever, and is nonetheless read as dashboards producing regulatory perception.

The topic is worth studying, the exposure operationalization is more explicit than the field's norm, the null exam comparison is reported rather than suppressed, and the authors label their own median split as a coarse simplification. Those are real virtues. They do not offset a manuscript whose numbers cannot be reconciled and whose sampling frame excludes the population its outcome is about. For a resubmission to be assessable on the merits, the authors would need the full enrolled cohort with prospectively measured, landmark-censored exposure; a logistic or discrete-time hazard model with prior achievement and course-load covariates; odds ratios and marginal risk differences with intervals; the retention base rate; an analysis script; and claim language in the abstract, Discussion, and Conclusion reduced to what an adjusted association supports. With the present data, the retention question should be withdrawn and the manuscript reframed as a descriptive institutional case report.

## Editorial Decision

Derived mechanically from the contract's `failure_conditions` precedence: F1 and F2 both fired; F1 carries the higher severity (90 > 70) and therefore controls.

editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 2 (Domain)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** Read as a domain reader rather than a methodologist: this dimension asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the bar that learning analytics and higher-education retention research actually enforces. My reading of it from a domain-accuracy seat is narrow by design — Reviewer 1 owns the technical adequacy of the design itself, and I own whether the paper's methodological choices are described in terms the field would recognise and whether they are represented honestly against what the field's own evidence base has established. For a dashboard-engagement/retention deployment study, the field-recognised bar concerns things like whether engagement is operationalised in a way prior deployment studies would accept, whether retention/persistence is defined with the temporal precision the higher-education literature demands, and whether the paper's own account of its design supports the domain claims it later makes. Where a rigor complaint of mine would rest on an assertion about what learning analytics *should* do — data release, preregistration, reporting completeness — I am gated by Step 5 and must ground the norm externally or down-rate to advisory.

**D2 — domain_accuracy.** This is my core dimension. It asks whether the paper's claims align with current evidence in learning analytics and higher-education retention, whether prior work is represented as its authors actually argued it, and whether domain-specific terminology and results are factually correct. In this field that has a very specific shape. Retention, persistence, attrition, completion, and progression are not synonyms in the higher-education studies literature, and the dashboard/engagement side carries its own vocabulary distinctions (dashboard access versus engagement, engagement versus self-regulated learning behaviour, learning analytics as a field versus academic analytics or educational data mining). The literature also has a well-documented body of deployment findings that complicate any simple dashboard-helps story — differential effects by prior attainment, null and negative results in controlled deployments, and long-standing critiques of engagement proxies. Domain accuracy here means the paper's positioning is truthful about that record rather than about a simplified version of it, and that any theoretical framework it invokes (self-regulated learning, feedback theory, or a retention/persistence model) is stated as its originators stated it rather than in a loose paraphrase.

**D3 — argumentative_coherence.** The contract asks whether the central thesis holds together internally, whether the evidence presented actually supports the claims made, and whether any fallacy undermines the core argument. From the domain seat I read this as the accuracy of the *inferential chain*, not the statistics: whether the concepts the paper defines early are the same concepts it reasons about later, whether the causal language it uses is licensed by the kind of study a deployment is, and whether the conclusions it draws about retention follow from the engagement evidence it presents. This dimension is where the field's most familiar reasoning error lives — engagement and retention co-vary because both are downstream of prior attainment, motivation, and enrolment intensity, so a coherent argument in this space must confront the confounding structure rather than route around it. Coherence in my sense fails when the paper's own stated framework or definitions contradict the inferences it later builds on them.

**D4 — cross_disciplinary_relevance.** This dimension asks whether framing, definitions, and implications land for adjacent-field readers and whether interdisciplinary claims are actually substantiated. The paper sits at a real disciplinary junction — learning analytics and educational technology on one side, higher-education studies on student retention and persistence on the other — so I read this as a boundary-accuracy question rather than a general accessibility question, which is Reviewer 3's remit. My concern is whether the paper's use of each tradition is faithful *to that tradition*: whether a retention scholar would recognise the retention constructs and whether a learning analytics researcher would recognise the engagement constructs, and whether claims that cross the boundary (that dashboard engagement bears on institutional persistence outcomes) are supported rather than asserted by juxtaposition. Priority is `high`, not `mandatory`, so a `block` here fires F3 rather than F1 — that difference disciplines how hard I lean on it.

**D5 — writing_and_structure.** Organisation, clarity of exposition, figure and table quality, and adherence to venue conventions. This is `normal` priority and no failure condition in the contract references it, so it cannot move the editorial decision at my seat. I still score it, and I read it through the domain lens available to me: whether the manuscript is structured so a domain reader can locate the constructs, the deployment context, and the evidence chain, and whether the exposition of domain material is precise rather than merely fluent. At 2487 words the manuscript is short for an empirical deployment study in this field, which makes structural economy a live consideration rather than a cosmetic one — but shortness is a fact about the format, not a defect in itself, and I will not treat it as one absent evidence that the compression removed something a domain reader needs.

## Scoring Plan

### D1: methodology_rigor

what_to_look_for: Whether the deployment is described with enough specificity for a domain reader to know what was actually deployed and to whom — dashboard features, who saw them, over what period, in what course context, and whether use was opt-in. Whether "engagement" has a stated operationalisation (logins, sessions, dwell time, feature-level interaction) and whether that operationalisation is one prior deployment studies use or a novel proxy introduced without justification. Whether "retention" is defined with a stated measurement window and unit (within-course completion, next-term re-enrolment, within-programme persistence, degree completion) rather than left as an undefined outcome. Whether the sample is characterised on the covariates the retention literature treats as first-order (prior attainment, enrolment intensity, entry route, standing). Whether reported statistics are complete enough to interpret — effect sizes with dispersion, not bare significance — and whether attrition from the analytic sample is accounted for. Whether reproducibility affordances (data, code, dashboard specification, instrument) are addressed at all, and if invoked as a deficiency, whether the learning analytics venue norm for that release actually exists as a checkable policy rather than my own assumption.

what_triggers_block: A mandatory-dimension `block` requires evidence that the domain claims the paper makes are not supported by any design it describes. Concretely: the outcome construct ("retention") is never operationally defined anywhere in the manuscript, so no reader can determine what was measured; or the engagement measure is never defined and the paper nonetheless reports quantitative associations with it; or the reported results are internally inconsistent in a way that makes the analysis uninterpretable (Ns that do not reconcile across text and tables, a reported statistic that cannot arise from the stated design); or the paper claims an experimental or causal design in its own words while describing a procedure that contains no assignment mechanism, no comparison condition, and no counterfactual — a design-claim misstatement, not merely a weak design. Absence of data or code release alone will NOT trigger `block`: I have no checkable learning analytics venue policy in hand mandating it, so under Step 5 that finding is capped at advisory and labelled `[FIELD-NORM UNVERIFIED]` unless the manuscript itself names a venue whose policy I can verify from session materials.

what_triggers_warn: Engagement or retention is defined, but loosely enough that the definition admits multiple incompatible readings (e.g. "retention" used without a stated window, or shifting window between sections). Sample characterisation omits prior attainment or enrolment intensity, the covariates this literature treats as dominant, so the domain reader cannot judge whether the population is one where the reported association would be expected. Statistical reporting is present but incomplete for domain interpretation — significance without effect size, or effect size without the base rate needed to judge practical magnitude in a retention context. Self-selection into dashboard use is present in the design and either unmentioned or noted without consequence for how results are read. Reproducibility affordances are absent AND the paper makes a claim of deployability or transferability that would require them to be checkable — this fires `warn` on the coupling to the claim, not on the absence alone.

### D2: domain_accuracy

what_to_look_for: Precision in the retention vocabulary — whether retention, persistence, attrition, progression, and completion are used as the higher-education literature distinguishes them, and whether the paper's outcome matches the term it uses for it. Correct attribution of the retention/persistence theoretical tradition if invoked, including whether a named model is presented as its author actually stated it and whether the paper is aware of the substantial critique that tradition has attracted, particularly regarding its applicability across student populations and institutional types. Whether learning analytics terms are used to field convention — dashboard *access* distinguished from *engagement*, engagement distinguished from the self-regulated learning constructs it is often taken to proxy, and the analytics subfield named correctly. Whether the literature base covers the deployment-study record honestly, including the null, mixed, and differential-effect findings that this specific literature is known for, rather than assembling only confirmatory work. Whether prior studies are represented as their authors argued them rather than as convenient support. Whether any factual claim about the sector — retention rates, policy context, institutional arrangements — is correct for the country and period named, or is left unlocated so that no reader can check it.

what_triggers_block: A substantive misrepresentation that the paper's own argument rests on. Specifically: a named theory or model attributed to the wrong originator, or presented with core claims it does not make, where that presentation is load-bearing for the paper's framing. A cited prior study characterised as finding something contrary to what it found, where that characterisation supports the paper's gap or contribution claim. Systematic terminological conflation that changes what is being claimed — most concretely, using "retention" for an outcome that is course completion or grade attainment, thereby claiming an institutional persistence result the study did not produce. A confident empirical claim about the sector (a retention statistic, a policy fact) that is stated as established and is wrong or unlocatable in place and time. Any of these fires `block` because domain accuracy is exactly the property being violated, and it is a mandatory dimension.

what_triggers_warn: The literature base is one-sided — deployment studies cited are confirmatory while the well-documented null and differential-effect findings in dashboard research go unmentioned — without the paper acknowledging the selection. Key domain terms are used consistently but never defined, so the reader must infer which construct is meant. A theoretical framework is named but applied only nominally: invoked in the introduction, absent from the design and the interpretation, and not revisited in the conclusion. Secondhand citation of a foundational claim through a review or a downstream paper where the original is standard and available. Contemporary coverage is thin — a field this active with nothing from the last three to five years, or coverage concentrated in a single research group, venue, or national system without the paper noting that concentration. Contextual claims that are plausible but unlocated (no country, no period, no institutional type), leaving domain accuracy unverifiable rather than wrong.

### D3: argumentative_coherence

what_to_look_for: Whether the construct defined in the front matter is the construct reasoned about in the discussion, or whether it silently widens (dashboard use → engagement → motivation → persistence). Whether the causal vocabulary matches the evidentiary warrant the design provides — a deployment study licenses associational language, and the coherence question is whether the paper's own claims respect that, including in the abstract, the section headings, and the practical recommendations, which are where causal drift most often surfaces after a hedged results section. Whether the confounding structure specific to this literature is confronted: engaged students may be the students who were going to persist anyway, so I look for whether the paper addresses the selection pathway and whether its conclusions are stated in a form that survives the reader granting it. Whether the stated research gap is the gap the study actually fills, and whether the contribution claimed in the conclusion is the contribution the evidence section delivers. Whether limitations, where present, are actually reflected back in how the claims are worded rather than quarantined in a paragraph the conclusions ignore.

what_triggers_block: The central claim is contradicted by the paper's own material — the conclusion asserts a relationship the reported evidence does not show, or the discussion generalises to a population or outcome the study explicitly excluded. Unqualified causal assertion at the level of the paper's headline claim (title, abstract, or conclusion states that dashboard engagement *increases*, *improves*, or *drives* retention) from an observational deployment with no assignment mechanism and no confounding adjustment — this is a fallacy that undermines the central argument, which is precisely what the dimension names, and it is mandatory. A definitional switch where the term carrying the conclusion is not the term that was measured, such that the argument only works because the meaning shifted mid-paper. A stated limitation that, if taken seriously, voids the main claim, while the main claim is left standing unmodified.

what_triggers_warn: Causal language appears in secondary locations — a recommendation, a subheading, a single sentence of the discussion — while the primary claims stay appropriately hedged. Self-selection is acknowledged as a limitation but no adjustment, sensitivity check, or reworded conclusion follows from the acknowledgement. The research gap is asserted rather than argued from the literature reviewed, so the contribution claim rests on an unestablished premise. Practical recommendations outrun the evidence in scope — institution-level or sector-level prescriptions from a single-course deployment — without a transferability caveat. Minor unsupported inferential steps that the argument does not depend on, or an interpretation offered as the explanation where the paper's own data admit at least one equally plausible alternative it does not consider.

### D4: cross_disciplinary_relevance

what_to_look_for: Whether the two traditions the paper joins are each represented in terms their own scholars would accept — that a higher-education retention reader recognises the persistence constructs and the institutional framing, and that a learning analytics reader recognises the engagement and dashboard constructs. Whether the crossing claim itself (that a dashboard-engagement signal bears on institutional retention) is substantiated by evidence or literature, or arrives by adjacency — the two bodies of work placed side by side and the connection left for the reader to supply. Whether terms with different meanings in the two literatures are disambiguated on first use, engagement being the clearest case: a behavioural log-derived measure in learning analytics, a multidimensional construct including affective and cognitive components in the higher-education engagement literature, and the paper needs to say which it means. Whether the implications are stated at a level an adjacent-field reader can act on, and whether the deployment context (institution type, system, discipline, cohort) is given, since transferability across educational contexts is the adjacent reader's first question. Whether any claim of interdisciplinary contribution is backed by engagement with both literatures rather than one plus a gesture.

what_triggers_block: The paper asserts an interdisciplinary contribution — bridging learning analytics and retention scholarship — while one of the two literatures is essentially absent or is represented through a single passing citation, so the bridge claim has no substantiation on one side. Or a construct is imported from the retention tradition and used with a meaning that tradition does not license, in a way that carries the paper's cross-boundary claim. This is a `high`-priority dimension, so a `block` here fires F3 (major revision) rather than F1; I will hold `block` for a substantiation failure at the level of the crossing claim itself, not for uneven depth between the two literatures.

what_triggers_warn: The engagement construct is used without disambiguating which disciplinary sense is meant, leaving an adjacent-field reader to guess. The retention literature is present but thin relative to the analytics literature (or the reverse), so the paper reads as one field's paper with the other's vocabulary borrowed. Implications are stated only in the vocabulary of one field, limiting uptake by the other. The deployment context is under-specified — no institution type, no national system, no disciplinary setting — so an adjacent-field reader cannot assess whether the finding transfers to theirs. Interdisciplinary framing in the introduction that the discussion never returns to.

### D5: writing_and_structure

what_to_look_for: Whether a domain reader can locate, without hunting, the four things this kind of paper must supply — the deployment description, the construct definitions, the analytic evidence, and the claims derived from it. Whether definitions appear before the terms are used in argument rather than after. Whether figures and tables carry enough labelling to stand alone (defined variables, stated units, stated N, stated time window) and whether the caption's interpretation follows from what the display actually shows. Whether the section structure serves the argument or merely fills a conventional template. Whether the 2487-word length reflects a deliberate short-format submission with proportionate scope, or compression that has silently dropped material a domain reader needs — the difference matters, and I look for which one the manuscript's own scope claims imply. Whether citation practice is consistent and whether terminology is stable across sections rather than drifting between synonyms.

what_triggers_warn: Domain-critical content is genuinely hard to locate — construct definitions absent from where the argument uses them, or the deployment described only in fragments spread across sections. A figure or table that cannot be read on its own terms (unlabelled axes, undefined variables, missing N or time window) or whose caption states an interpretation the display does not support. Terminology that drifts between synonyms across sections such that the reader must reconstruct whether the same construct is meant. Structural omission of a section the argument depends on — for instance, no limitations discussion in an observational deployment study. Note: this dimension is `normal` priority and appears in no `failure_conditions` predicate, so a `warn` here does not by itself move my editorial decision.

what_triggers_block: Reserved for exposition that makes the domain content unassessable — for example, the paper's structure or presentation is so disordered that I cannot determine what was measured or what is being claimed even after a full read, so no domain judgment is recoverable from the text. Ordinary weaknesses of organisation, clarity, formatting, or venue-convention adherence resolve at `warn` or `pass`. I record here, as a pre-commitment, that I will not escalate a `normal`-priority presentation complaint to `block` in order to move the editorial decision by a route the contract's failure conditions do not provide — F1 and F2 read mandatory dimensions only and F3 reads high-priority dimensions only, so D5 has no decision path, and manufacturing one would be a protocol violation rather than a severity judgment.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Domain Review Report (Peer Reviewer 2)

### Reviewer Identity

Senior learning-analytics researcher in higher education, specialising in student-facing dashboards and self-regulated learning; publishes systematic reviews of dashboard-outcome studies and works close enough to the primary SRL, dashboard-design, and persistence literatures to notice both what is cited and what is absent.

### Overall Recommendation

Reject — with a path back. The domain defects are correctable in principle, but the manuscript in its present state cannot be assessed on its literature claims at all, because the source it builds its equity rationale on appears in its own reference list under a title that argues the opposite.

### Confidence Score

4

I am confident about the findings below because every one of them is verifiable inside the manuscript's own text — I am not asserting external facts about sources I cannot reach. I withhold the fifth point because I could not independently resolve a single reference: all fifteen DOIs share one prefix, so the literature base itself is unverifiable from my seat, and a portion of my assessment is therefore conditional on what an independent bibliographic check returns.

### Summary Assessment

This is a manuscript whose literature review is better than its use of literature. Section 2 is organised around the four fault lines that genuinely divide this field — benefit heterogeneity, demotivation risk, proxy-measurement validity, and causal overreach — and it applies the measurement critique reflexively to the present study, which is uncommon and creditable. That structural competence makes what follows harder to excuse rather than easier.

Three domain problems are decisive. First, §2 cites Ferro & Nakamura (2021) as having shown that dashboards "reliably improve outcomes for lower-achieving students," while the manuscript's own reference list gives that work's title as *When dashboards demotivate: Peer comparison and the lower-achieving student*. The paper's equity-oriented rationale rests on that sentence. Second, the bibliography cannot presently support any literature-based claim: nine of fifteen entries are never cited, no work from the retention and persistence tradition is cited anywhere in the text despite retention being the outcome, and the one directly on-point reference the author already holds — Wexler & Ojo (2020), *Retention modeling with LMS trace data: A cautionary study* — is left unused. Third, §1 states the correct epistemic standard for this field and §§5–6 abandon it, concluding that engagement "raises" retention and that dashboards are a "dependable" and "generalisable" lever for institutions "worldwide."

The self-regulated learning framing is named rather than applied: no SRL model is attributed to any originator, the construct is operationalised as one perceived-control item, and no conclusion returns to the theory.

### Strengths

1. **Literature review with real critical architecture**: §2 is organised thematically around four contested questions rather than as a citation list, and each theme corresponds to an actual division in the dashboard literature. The transition from benefit-heterogeneity to demotivation to measurement to causal critique is a defensible map of the field's current state.
2. **Reflexive application of the measurement critique**: §2 writes that "most dashboard studies, including the present one, infer engagement from coarse behavioral proxies," and §5.1 repeats the concession. Turning the field's critique on one's own instrument is the correct move and is rarer in this literature than it should be.
3. **Operationally stated constructs**: both focal constructs are defined in §3.3 rather than left implicit — engagement as distinct dashboard sessions under a stated sessionisation rule, retention as remaining enrolled through the final assessment. The title's scope ("course retention") matches that operationalisation, which many papers in this space fail to do.
4. **Honest naming of the median split as a compromise**: §3.3 states the split "is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency." The choice is still weak, but the manuscript does not disguise it.
5. **Limitations that identify the right three risks**: §5.1 names proxy narrowness, self-report bias, and single-course/single-interface scope. These are the correct three; the failure is that §6 proceeds as if none had been written.

### Weaknesses

1. **Source inversion carrying the equity rationale**: §2 states that "dashboards have been shown to reliably improve outcomes for lower-achieving students, who are said to gain the most from externalized progress cues (Ferro & Nakamura, 2021)," and adds that "this position underpins much of the equity-oriented rationale for institutional dashboard deployment." The reference list entry for that citation reads *When dashboards demotivate: Peer comparison and the lower-achieving student* (Journal of Educational Data Practice, 9(1), 44–62). The in-text characterisation and the manuscript's own bibliographic record of the source point in opposite directions for the same population. This is not a citation-style matter: it is the sentence the equity argument stands on, and it also means the demotivation account in the very next paragraph (Osei, 2020) is set up as a minority counterpoint to a consensus that the manuscript's own list does not evidence. *Severity basis: an internal contradiction between §2's prose and the manuscript's own reference list — not an external claim about a source I cannot access.* **Required for the claim to stand:** either quote the passage in Ferro & Nakamura that supports the "reliably improve" reading, or correct the sentence and rebuild the equity rationale on a source that argues it.
2. **A bibliography that cannot currently support any literature-based claim**: nine of fifteen entries (Ainsworth & Devi; Berange; Delacroix & Ohno; Halloran; Kessler & Amadou; Montez; Prakash & Tolliver; Solberg & Whitfield; Wexler & Ojo) appear nowhere in the body. Several are directly relevant to passages that instead cite something else or nothing — Berange (2021) on goal orientation and dashboard response sits unused beside §2's goal-orientation paragraph; Kessler & Amadou (2019) on SRL in digital environments sits unused beside the SRL framing; Wexler & Ojo (2020) on retention modelling with LMS trace data is the closest analogue to this study's own design and is never engaged. Separately, all fifteen DOIs share the `10.5555` prefix across five different journals. If that prefix is the reserved example range rather than a registered prefix, none of these references resolves and the entire literature base requires reconstruction; I flag the prefix observation as a pattern in the text and mark the inference about what the prefix means as requiring independent verification. **Required for the claim to stand:** an independent resolution check on all fifteen entries, and either citation or removal of the nine unused ones.
3. **Causal conclusions the manuscript's own standard forbids**: §1 promises "we are careful throughout to distinguish the pattern in the data from the causal story that might explain it, a distinction that the dashboard literature has not always maintained." §5 then opens with "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course"; §6 states engagement "is associated with, and raises, course retention." Nothing in §§3–4 supplies an assignment mechanism, a comparison condition, or any covariate adjustment. The manuscript cites Ibarra (2023) on exactly this failure mode and then instantiates it. A reviewer can forgive naive overclaiming more readily than overclaiming by an author who has documented the standard in their own §2. **Required for the claim to stand:** retract to associational language in the abstract, §5, and §6, and confront the reverse pathway — students already on track to complete are plausibly the ones who keep opening the dashboard.
4. **Self-regulated learning invoked but neither attributed nor applied**: §1 describes learners cycling "through phases of forethought, performance, and reflection" without attributing this to any originator; the only SRL citation is Rutledge & Berange (2022), a secondhand route to a framework whose primary statements are standard and available. The construct is then operationalised with one item — "Overall, I feel in control of my learning in this course" — and §4.3 reads a group difference on it as evidence that "dashboard use and self-regulatory perception travel together." Perceived control is not the SRL monitoring construct the forethought/reflection framing implies; it sits closer to academic control or self-efficacy, and the substitution is made without argument. The manuscript's defence that "single-item overall ratings are common in dashboard studies to limit survey burden" is itself an uncited claim about field practice. No conclusion returns to SRL to extend, revise, or challenge it. *I do not assert here what instrument the field requires: I could not ground that norm in an external checkable source, so I report the gap and decline to attach a severity to the instrument choice as such* `[FIELD-NORM UNVERIFIED]`. *The attributional gap, the construct substitution, and the author's own uncited field-practice claim are independent of that norm and are not down-rated.* **Required for the claim to stand:** attribute the phase model to its source, argue why perceived control indexes the SRL phases the mechanism story needs, and cite the "common practice" assertion or drop it.
5. **Retention construct widens between Methods and Conclusion**: §3.3 defines retention at the course level — remaining enrolled and completing the final assessment. §6 concludes that dashboards are a lever "for improving retention across programs and disciplines" and for "supporting student success at scale," addressed to "higher education institutions worldwide." Course completion and programme persistence are distinct outcomes in the higher-education literature with distinct predictors; the manuscript measures the first and prescribes on the second. The title is correctly bounded; the conclusion is not. **Required for the claim to stand:** keep §6's claims at the course level, or supply evidence linking within-course completion to programme persistence in this setting.

### Detailed Comments

#### Literature Review

- **Coverage**: The learning analytics side is adequately represented for a short-format paper. The retention and persistence side is absent from the body — zero of the six in-text citations come from that tradition, while three unused reference-list entries (Halloran; Solberg & Whitfield; Wexler & Ojo) do. §1's opening claims that "undergraduate attrition remains a persistent concern" and that "the first-year gateway course is frequently identified as a point of elevated risk" are stated as established and carry no citation, with Halloran (2020), *Retention in the gateway course*, sitting uncited in the author's own list. No foundational SRL, dashboard-design, or persistence source is cited anywhere.
- **Integration quality**: Genuinely synthetic within its four themes, not enumerative. §2's paragraphs build on one another and each names a real tension. This is the manuscript's strongest section as writing; the problem is that one of its load-bearing citations appears inverted and two-thirds of the assembled sources never enter it.
- **Research gap argument**: Weak, and undermined by the manuscript's own framing. §2 establishes that the field is already saturated with correlational designs and already carries an explicit audit of their causal overreach (Ibarra, 2023). A single-course bivariate correlational study is another instance of the pattern §2 diagnoses. §1 asserts that outcome-facing evidence is thin, but the review that follows does not demonstrate the specific gap this design fills.

#### Theoretical Framework

- **Appropriateness**: SRL is a defensible choice for a dashboard-feedback mechanism, and the forethought/monitoring framing matches what dashboards plausibly afford. The framework is not the problem.
- **Application depth**: Superficial. The framework appears in §1, §2, and §5 as language and never as a constraint on design or interpretation. No SRL phase is measured; the sole SRL-adjacent measure is a global control rating; the discussion draws no theoretical consequence. §5's inference that engagement and "self-regulatory perception travel together" is the framework's only appearance in the results interpretation, and it rests on the construct substitution described in W4.
- **Alternative frameworks**: If perceived control is what the study can actually measure, the honest framing may be an academic-control or self-efficacy account rather than an SRL one, which would make the single item defensible on its own terms instead of a weak proxy for something else. Alternatively, if the mechanism of interest is peer comparison — which is what §3.1's dashboard actually displays — a social-comparison or goal-orientation framing would fit the artefact more closely, and the manuscript already holds an unused reference on precisely that (Berange, 2021).

#### Academic Argument Quality

- **Factual accuracy**: The Ferro & Nakamura characterisation contradicts the manuscript's own record of that source (W1). Two contextual claims in §1 about attrition and gateway-course risk are unlocated in country, period, or institutional type, so a domain reader cannot check them. The setting is named ("Meridian State University") without institution type, system, or sector context, which leaves the deployment unlocatable for transferability purposes.
- **Argument logic**: The chain from §1 to §6 does not hold. §1 commits to distinguishing pattern from cause; §5 asserts cause; §6 asserts cause plus worldwide generalisability, over a §5.1 limitation that explicitly concedes the interface "differs from those deployed elsewhere." The manuscript raises the demotivation account (Osei, 2020) in §2, says it will return to the benefit-heterogeneity question "in the Discussion," and never tests either against its own data — no subgroup analysis by prior attainment appears, despite a peer-comparison band being the very feature §2 flags as a demotivation risk. Self-selection is not addressed anywhere: §3.2 states that participation depended on students volunteering mid-term, which structurally removes from a retention study the students most informative about non-retention, and no conclusion is reworded in light of it.
- **Terminology precision**: Retention drifts from course completion (§3.3) to programme-and-discipline retention (§6). Dashboard *access* is treated throughout as dashboard *engagement*, which §2 itself warns against and §5 then relies on. "Perceived control" is used interchangeably with self-regulation. Separately, §4.2's association is reported as a Pearson correlation against a dichotomous outcome; I flag the mismatch as a domain-reader interpretability issue and leave the statistical adjudication to Reviewer 1.

#### Contribution to the Field

- **Incremental contribution**: Presently unassessable, and thin on the most favourable reading. If the association is real, it is one more correlational single-course finding of the exact type §2 documents the field as already having in abundance. §5's statement that "our finding that engagement tracks retention aligns with the view that externalized progress cues can support persistence" is a restatement of the prior, not an advance on it. The study's one distinctive affordance — pairing behavioural traces with a subjective regulatory measure — is not exploited, because the subjective measure is a single global item analysed only as a group difference.
- **Positioning**: The manuscript positions itself as more epistemically careful than the field (§1, §2) and then does what it criticises. That is a worse position than naive overclaiming, because it demonstrates the standard was known and not applied.
- **Overclaiming**: Severe and concentrated in §6, which converts a modest within-course association into a "dependable strategy" that is "practical and generalizable" for institutions "worldwide." Three separate escalations occur in two sentences: association to causation, course to programme, one interface at one institution to global practice.

#### Missing Key References

**Already in the author's own reference list and uncited — these should be engaged or removed:**

- Wexler & Ojo (2020), *Retention modeling with LMS trace data: A cautionary study*. The closest published analogue to this design. A study of this shape cannot leave a cautionary paper on its own method unaddressed.
- Halloran (2020), *Retention in the gateway course: A review of intervention studies*. Would ground §1's uncited gateway-course claim and locate this study among prior retention interventions.
- Berange (2021), *Goal orientation and dashboard response in introductory courses*. Directly serves §2's goal-orientation passage and would support the subgroup analysis §2 promises and §4 never delivers.
- Kessler & Amadou (2019), *Self-regulated learning in digital environments: A synthesis*. The SRL framing currently rests on one downstream citation; this is the author's own available synthesis.
- Solberg & Whitfield (2018), *Institutional deployment of learning analytics: Lessons from three campuses*. Required if §6 intends to keep any institutional-deployment recommendation.
- Prakash & Tolliver (2021), *Dashboard adoption patterns across disciplines*, and Delacroix & Ohno (2022), *Behavioral logging and its discontents in higher education analytics*: relevant to §5.1's transferability caveat and to the engagement-proxy defence respectively.

**Search leads for the missing canonical layer** — no work from any of the following traditions appears anywhere in the manuscript. I can attest to none of the metadata below from session materials, so each is a search lead rather than a citation:

- `[UNVERIFIED]` The primary statement of the cyclical-phase SRL model — work by Zimmerman on forethought/performance/self-reflection phases, and the Winne & Hadwin account of studying as self-regulated learning. §1 paraphrases this model without attributing it to anyone.
- `[UNVERIFIED]` The dashboard-design and dashboard-evaluation critique literature — work by Jivet and colleagues on whether student-facing dashboards are grounded in learning theory, and by Verbert and colleagues on dashboard applications; also the systematic-review layer on student-facing dashboard outcomes (the Bodily & Verbert review is the standard entry point).
- `[UNVERIFIED]` The field's own corrective on trace data and learning — Gašević, Dawson & Siemens on learning analytics being about learning rather than about logs, which is the canonical statement of the proxy-validity problem §2 raises via Vandermeer alone.
- `[UNVERIFIED]` The student-departure and persistence tradition — Tinto's interactionalist model and Bean's alternative, plus the substantial critique of their applicability across student populations and institution types. A paper whose outcome is retention and whose conclusion addresses institutions cannot leave this tradition entirely unrepresented.

### Questions for Authors

1. Please quote the passage in Ferro & Nakamura (2021) that supports "dashboards have been shown to reliably improve outcomes for lower-achieving students," and reconcile it with the title recorded in your own reference list. If the reference-list entry is the error, which source does §2's claim actually come from?
2. Which correlation is the study's result — the abstract's *r* = .42 or §4.2's *r* = .24? A domain reader's judgment of whether this finding is notable or unremarkable within the dashboard literature turns entirely on which figure is real.
3. Which self-regulated learning model does §1's forethought/performance/reflection description come from, and on what basis does a single global perceived-control rating index the phases that model specifies?
4. §2 raises the demotivation account (Osei, 2020) and the benefit-heterogeneity question, and says you will return to them in the Discussion. The peer-comparison band in your dashboard (§3.1) is the exact feature at issue. Why is there no analysis by prior attainment, and what would your data say if there were?
5. §3.3 defines retention as course-level completion. On what evidence does §6 extend that to retention "across programs and disciplines" for institutions "worldwide"?
6. §3.2 states that participants were "drawn from the course enrollment using a random sample" and, in the next paragraph, that students who did not respond to a mid-term announcement were excluded. Which describes what happened? Given that students who withdrew before the recruitment window cannot appear in a sample whose outcome is retention, how should a reader interpret the retention association?

### Minor Issues

- The manuscript contains no instruction-directed content addressed to reviewers; there is no injection attempt to report.
- Table 1 reports perceived control to three decimals (3.847) beside two-decimal statistics, and carries a final-exam variable that is never defined in §3.3 Measures — it first appears in Results.
- Neither table reports its N; Table 2's group sizes and the accompanying text's "all 142 students" describe different samples.
- The institution is named but not characterised (type, system, sector), so an adjacent-field reader cannot judge transferability; the dashboard is described only in three general phrases, with no version, vendor, or specification.
- The thirty-minute sessionisation rule is adopted as "the platform's default." An inherited platform setting is being used as a construct boundary; this should be stated as a limitation rather than as a definition.
- "Learning analytics" is used throughout without distinguishing it from academic analytics or educational data mining; for a paper positioned within the field, one line of definitional work would help adjacent readers.

---

contract_role: domain

## Dimension Scores

### D1: methodology_rigor

Trigger applied (Phase 1, `what_triggers_block`): "the reported results are internally inconsistent in a way that makes the analysis uninterpretable (Ns that do not reconcile across text and tables, a reported statistic that cannot arise from the stated design)."
Basis: the abstract reports *r* = .42 and §4.2 reports *r* = .24 for the same association; §4.3 reports *t*(156) for a perceived-control comparison drawn from 87 respondents within an analytic sample of 142; Table 2 reports 66 + 61 = 127 in the same paragraph that states "all 142 students… were classified"; Table 1 reports a final-exam measure that §3.3 never defines. §3.2 additionally states two incompatible sampling designs one paragraph apart. From the domain seat the consequence is that no reported quantity can be positioned against the field's existing effect-size record. The full numerical audit and the inferential-validity question belong to Reviewer 1; I score only the domain-interpretability consequence. Neither construct definition is absent, and I did not down-rate for reproducibility-artefact absence, per my Phase 1 cap.
score: block

### D2: domain_accuracy

Trigger applied (Phase 1, `what_triggers_block`): "a cited prior study characterised as finding something contrary to what it found, where that characterisation supports the paper's gap or contribution claim."
Basis: §2's characterisation of Ferro & Nakamura (2021) contradicts the title the manuscript's own reference list gives that work, and the manuscript states that this position "underpins much of the equity-oriented rationale for institutional dashboard deployment." Compounding, at `warn` level within the same dimension: the retention/persistence tradition is uncited throughout while retention is the outcome; the SRL phase model is unattributed and reached only through a downstream citation; nine of fifteen references are unused; the "single-item ratings are common in dashboard studies" field-practice claim is uncited; and §1's sector claims are unlocated in country, period, or institution type. The terminological widening from course completion to programme retention is scored here and under D3.
score: block

### D3: argumentative_coherence

Trigger applied (Phase 1, `what_triggers_block`): "unqualified causal assertion at the level of the paper's headline claim… from an observational deployment with no assignment mechanism and no confounding adjustment," and, independently, "a stated limitation that, if taken seriously, voids the main claim, while the main claim is left standing unmodified."
Basis: §5 states "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course"; §6 states engagement "is associated with, and raises, course retention." §1 commits to the opposite standard and §2 cites Ibarra (2023) documenting this exact failure mode. §5.1 concedes single-course scope and interface idiosyncrasy; §6 claims worldwide generalisability over that concession unmodified. The self-selection pathway created by mid-term voluntary recruitment is never addressed, and the term carrying the conclusion (programme-level retention) is not the term that was measured (course completion).
score: block

### D4: cross_disciplinary_relevance

Trigger applied (Phase 1, `what_triggers_block`): "the paper asserts an interdisciplinary contribution… while one of the two literatures is essentially absent or is represented through a single passing citation, so the bridge claim has no substantiation on one side."
Basis: the crossing claim is the paper's outcome and its entire prescription — dashboard engagement bearing on retention, with §6 addressing "higher education institutions worldwide" about retention "across programs and disciplines." Zero of the six in-text citations come from the retention or persistence literature; §1's retention premises are uncited; the three retention-side entries the author holds are all unused. This is substantiation absence on the crossing claim itself, not uneven depth between two represented literatures, which is the distinction I committed to in Phase 1. The engagement construct is also never disambiguated between its log-behavioural and multidimensional senses, and the deployment context is under-specified for any adjacent reader assessing transfer.
score: block

### D5: writing_and_structure

Trigger applied (Phase 1, `what_triggers_warn`): "a figure or table that cannot be read on its own terms (unlabelled axes, undefined variables, missing N or time window)," and "terminology that drifts between synonyms across sections."
Basis: neither table reports N; Table 1 carries an undefined final-exam variable and inconsistent decimal precision; Table 2 does not reconcile with its own paragraph; retention/persistence/completion and access/engagement drift across sections. The prose is otherwise clear, the IMRaD structure is complete, and a limitations section is present — the `block` threshold I reserved (exposition that makes the domain content unassessable) is not met, and I recorded in Phase 1 that I would not escalate a `normal`-priority presentation complaint to `block` to reach a decision route the contract does not provide.
score: warn

## Failure Condition Checks

### F1

Predicate: any mandatory dimension scores `block`. D1, D2, and D3 are all mandatory and all score `block`.
fired: true

### F2

Predicate: two or more mandatory dimensions score `warn` or worse. Three mandatory dimensions (D1, D2, D3) score `block`, which is worse than `warn`.
fired: true

### F3

Predicate: any high-priority dimension scores `block`. D4 is `high` priority and scores `block`.
fired: true

### F0

Predicate: every mandatory dimension scores `pass`. None does.
fired: false

## Review Body

From the domain seat, this manuscript fails on the property my dimension is named for, and it fails on a fact internal to its own pages rather than on a judgment call. Section 2 tells the reader that dashboards "have been shown to reliably improve outcomes for lower-achieving students" and attributes that to Ferro & Nakamura (2021); the reference list records that work as *When dashboards demotivate: Peer comparison and the lower-achieving student*. The manuscript then states that this position underpins the equity-oriented rationale for institutional deployment. Whichever of the two records is wrong, the sentence carrying the equity argument is presently unsupported by the manuscript's own materials, and the demotivation account it introduces immediately afterwards is framed as dissent from a consensus the paper has not evidenced.

That finding does not stand alone. Nine of fifteen references are never cited, and the unused portion contains exactly the works the argument needs: a cautionary study of retention modelling with LMS trace data, a review of gateway-course retention interventions, a goal-orientation study of dashboard response, and an SRL synthesis. Meanwhile no work from the persistence tradition is cited anywhere in the body, though retention is the outcome, the title, and the conclusion's entire prescription. Every DOI in the list shares one prefix across five journals. A domain reviewer cannot treat any literature-based claim in this paper as supported until the bibliography is independently resolved, and I have therefore made my confidence conditional on that check rather than assuming the sources behind it.

The theoretical layer is named rather than used. The forethought/performance/reflection cycle appears in §1 with no originator attached; the single SRL citation is a downstream one; the construct is measured by one global item about feeling "in control," which is not the monitoring construct the mechanism story requires; and no conclusion returns to the theory to extend or revise it. The substitution of perceived control for self-regulation is made silently, and §4.3 then reads a group difference on that item as evidence about self-regulatory perception. I record separately that I could not ground, in any external checkable source, a field norm about what instrument SRL requires in dashboard studies, so I decline to attach severity to the instrument choice as such and mark that portion `[FIELD-NORM UNVERIFIED]`. The attributional gap and the construct substitution do not depend on any such norm, and I have not down-rated them.

What makes the causal drift more serious than ordinary overclaiming is that §1 states the correct standard and §2 cites an audit of the field for violating it. §5 then asserts that engagement "improved" retention and "raises the probability" of completion; §6 asserts it "raises" retention and calls dashboards a "dependable" and "generalizable" lever for institutions "worldwide" — over a §5.1 limitation conceding that this interface differs from those deployed elsewhere. Along the way the outcome quietly widens from the course-level completion defined in §3.3 to programme-and-discipline retention. Three escalations happen in the space of §6's two sentences: association to cause, course to programme, one interface to global practice.

I note, and do not soften, what the paper does well. Section 2 is a genuinely critical review with a defensible map of the field's fault lines, it applies the proxy-validity critique to its own instrument, and §3.3 defines both focal constructs operationally with a title that matches the narrower one. Those are the parts a revision can build on. What a revision cannot do is preserve the current conclusions: the causal language must go, the outcome must stay at the course level, the equity rationale must be rebuilt on a source that argues it, and the bibliography must be verified end to end before any claim resting on it is reviewable. Whether the design can answer the retention question at all after the mid-term volunteer recruitment is Reviewer 1's determination, and I defer to it; the domain defects I have named persist regardless of how that determination goes.

No instruction-directed content was found inside the manuscript; there is no injection attempt to report as an integrity weakness.

## Editorial Decision

Derived mechanically from the contract's `failure_conditions` precedence: F1 (severity 90), F2 (70), and F3 (60) all fired against my own dimension scores; the highest severity wins.

editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 3 (Perspective)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** As the outsider seat, I read this dimension not as a statistics audit (that belongs to Reviewer 1) but as a question of whether the study's design decisions are legible and defensible to someone standing outside learning analytics. A paper reporting a dashboard deployment in an undergraduate setting is making a claim about a real intervention in a real institution, so the design's rigor is inseparable from what the design *can* say about causal or associational structure. My paraphrase: the design, data handling, and reproducibility affordances must be transparent enough that a reader from an adjacent discipline — a program evaluator, an HCI researcher, an institutional-research analyst — can tell what the study measured, on whom, over what window, and what class of inference the design licenses. Where the field's conventional design (observational log-data study of a voluntary tool) carries known interpretive limits, rigor here means those limits are named rather than absorbed into the framing.

**D2 — domain_accuracy.** Learning analytics sits at an intersection: it borrows constructs from higher-education retention scholarship, from educational psychology, and from data science. From my seat, domain accuracy is therefore a *multi-domain* obligation. Constructs the paper imports from the retention and persistence literature (retention, persistence, attrition, stop-out, engagement) carry specific technical meanings in higher education studies, and a learning-analytics paper that redefines or flattens them is inaccurate even if every number is right. My paraphrase: claims must be faithful to the current evidence base in *each* discipline the paper draws on, prior work must be represented as its own field would recognize it, and imported terminology must be used with its home-discipline meaning or explicitly redefined. This is not a literature-coverage audit (Reviewer 2's job) — it is whether what *is* cited and asserted is correctly characterized.

**D3 — argumentative_coherence.** I do not run fallacy detection or internal-consistency checks (that is the Devil's Advocate's role). My reading of this dimension is upstream of formal logic: whether the paper's central thesis survives contact with the assumptions it rests on. A study linking dashboard engagement to course retention is built on premises that its own discipline rarely interrogates — that engagement with an analytics tool is a meaningful behavioral signal rather than a proxy for prior motivation, that visibility of one's data changes behavior in the intended direction, that retention is the right outcome to optimize. My paraphrase: the core argument must hold once its implicit and paradigmatic assumptions are surfaced, and the strength of the conclusion must not exceed what the stated design and framing can carry.

**D4 — cross_disciplinary_relevance.** This is my primary dimension and the contract marks it high-priority. The paper is explicitly positioned at a junction — learning analytics and educational technology on one side, higher education studies on retention and persistence on the other — so accessibility to adjacent-field readers is not a courtesy, it is a load-bearing requirement of the paper's own positioning. My paraphrase: framing, operational definitions, and stated implications must be intelligible and usable to readers who do not share the authors' methodological training; and any claim that reaches across a disciplinary boundary — invoking retention theory, behavioral change, student motivation, institutional policy — must be substantiated on the *receiving* field's terms, not asserted from the home field's assumptions. It also covers whether the paper considers the stakeholders and practical conditions an adjacent reader would immediately think of: students as subjects rather than data sources, instructors, advisors, institutions with unequal infrastructure, and students with unequal digital access.

**D5 — writing_and_structure.** From the outsider seat, organisation and exposition matter because they determine whether a non-specialist can reconstruct what was done. At roughly 2,500 words this is a short-format manuscript, which makes structural discipline more consequential, not less: at that length every section must earn its place, and compression is the most likely source of an unreadable methods account or an implications section that asserts rather than argues. My paraphrase: the manuscript's organisation, clarity, and figure/table quality must let an adjacent-field reader follow the chain from data to claim without reconstructing missing steps. I treat this as the contract's normal-priority dimension and will not inflate presentational complaints into substantive ones.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for`: Whether the design is described concretely enough for an outside reader to identify what was compared and against what — sample frame, institution type and count, course level and discipline mix, observation window, and whether dashboard access was voluntary, assigned, or universal. Whether the paper states what the engagement measure actually is (logins, dwell time, feature interactions) and whether that operationalization is defended rather than assumed. Whether self-selection into dashboard use is acknowledged as a structural feature of the deployment. Whether there is any account of what happened to students who never engaged. Whether reproducibility affordances exist in a form an external evaluator could act on — instrument description, variable definitions, data-availability or code statement, or an explicit statement of why none is possible.
- `what_triggers_block`: The design as described cannot support the inference the paper draws, and the mismatch is not disclosed — for example, a voluntary-use observational deployment whose write-up treats dashboard engagement as an intervention that produced retention, with no acknowledgement that users self-selected. Also blocking: the study's basic parameters (who, how many, over what period, what counted as engagement) are absent to the point that an adjacent-field reader cannot determine what was studied, so no independent assessment of the design is possible.
- `what_triggers_warn`: Design parameters are present but thin in ways that limit external assessment — engagement operationalized without justification, single-institution or single-course scope not flagged as a boundary condition, attrition from the analytic sample unexplained, or no reproducibility affordance offered and no reason given. Also warning: limitations are listed but generically, in a form that names the concern without letting the reader gauge its size or direction.

### D2: domain_accuracy

- `what_to_look_for`: Whether retention is defined at all, and if so at which unit — course completion, term-to-term persistence, or degree completion — since the title says *course* retention while the field's retention literature predominantly theorizes institutional persistence. Whether the paper's use of "engagement" is consistent with its meaning in higher education studies (a multidimensional behavioral/emotional/cognitive construct) or silently narrowed to tool-usage frequency without saying so. Whether cited retention and persistence scholarship is characterized as that literature would recognize it, rather than reduced to a citation of convenience. Whether learning-analytics claims about early-warning or intervention effectiveness are stated at the strength the current evidence in that area actually supports.
- `what_triggers_block`: A construct imported from higher education studies is used with a meaning its home field would reject, and a substantive claim rests on that misuse — for example, course-level completion findings presented as evidence about student persistence or attrition in the institutional sense, or a body of prior work characterized as having established something it did not. Also blocking: a factual misstatement about the state of evidence in learning analytics or retention research that the paper's conclusion depends on.
- `what_triggers_warn`: Cross-field terminology is used loosely but not misleadingly — "retention," "engagement," "at-risk," or "persistence" deployed without definition where the two contributing fields would read them differently, or prior work described in terms broad enough to blur what it actually found. Also warning: claims stated more confidently than the cited evidence base warrants, without a hedge, where the overreach does not carry the central conclusion.

### D3: argumentative_coherence

- `what_to_look_for`: The implicit premises the argument needs but may never state — that dashboard engagement indexes something other than pre-existing motivation or conscientiousness; that seeing one's own analytics changes behavior in the intended direction rather than discouraging struggling students; that retention is an unambiguous good for every student regardless of fit; that a deployment-scale association would hold under the counterfactual. Whether the paper's own framing acknowledges the reverse or common-cause reading of the engagement-retention link. Whether the conclusion and any practice or policy recommendation are pitched at the strength the argument can carry, or escalate between abstract, results, and discussion.
- `what_triggers_block`: The central thesis depends on an unexamined assumption that, once surfaced, plausibly reverses or dissolves the finding — most concretely, an engagement-retention association presented as grounds for deploying or expanding dashboards when the same pattern is at least equally consistent with already-persisting students being the ones who check dashboards, and the paper neither raises nor rules out that reading. Also blocking: recommendations whose warrant exceeds the paper's own stated design by a wide margin, such that a practitioner acting on them would be acting on a claim the study never made.
- `what_triggers_warn`: An alternative interpretation is acknowledged but only in passing, without following through on what it would mean for the conclusion. Claim strength drifts across sections — hedged in the results, unhedged in the abstract or implications. A paradigmatic assumption (that more data visibility produces better student decisions; that behavioral signals capture engagement) is left implicit where naming it would materially change how a reader from an adjacent field weighs the finding.

### D4: cross_disciplinary_relevance

- `what_to_look_for`: Whether an adjacent-field reader — a higher education scholar, an institutional researcher, a student-affairs practitioner — can extract from the framing what the study means for them without already sharing learning-analytics assumptions. Whether operational definitions are given for terms that travel across the two named fields. Whether the paper substantiates its interdisciplinary claims on the receiving field's terms when it invokes retention theory, behavior change, or institutional policy. Whether the stakeholder map extends past the institution and the instructor to students themselves — their experience of being measured, the possibility that seeing an unfavorable dashboard demotivates, differential digital access, and privacy or data-governance interests. Whether implementation conditions are stated concretely enough that an institution unlike the study site could judge transferability — infrastructure, staffing, advisor capacity, LMS integration. Whether the single-context nature of the deployment is flagged as a limit on generalization across institution types and national systems.
- `what_triggers_block`: The paper makes a substantive interdisciplinary claim — that its findings bear on student persistence theory, that dashboards should be adopted as a retention strategy, or that the results generalize across institutions — with no substantiation on the receiving discipline's terms and no acknowledgement that the claim crosses a boundary. Also blocking: recommendations addressed to practice or policy while students, the population most directly affected, appear only as data sources with no consideration of their experience, their unequal access, or the ethical and privacy dimensions of behavioral monitoring — such that acting on the paper's recommendation would carry unexamined equity or harm risk.
- `what_triggers_warn`: The framing is comprehensible to adjacent readers but assumes field-specific vocabulary or platform conventions without gloss. Implications are stated at a level of generality that gives an outside practitioner nothing actionable ("institutions should consider learning analytics"). One significant stakeholder or contextual condition — student workload and affect, advisor capacity, infrastructure prerequisites, cross-institutional or cross-national transferability — is unaddressed where an adjacent-field reader would expect it. Ethical or privacy dimensions of behavioral tracking are mentioned once and not developed. Cross-context validity is asserted rather than argued.

### D5: writing_and_structure

- `what_to_look_for`: Whether the ~2,500-word budget is allocated so the methods and the basis for the central claim are recoverable, rather than spent on framing at the expense of the empirical account. Whether section organisation lets a reader trace data → measure → analysis → claim without reconstructing omitted steps. Whether figures and tables carry self-sufficient captions with defined units, sample sizes, and axes, and whether the text's interpretation of a figure follows from what the figure shows. Whether terminology is used consistently across sections. Whether the abstract's characterization of the findings matches the body.
- `what_triggers_block`: The exposition is disordered or compressed to the point that the central claim's basis cannot be reconstructed at all — key results reported without the analysis that produced them, or figures/tables that cannot be read because units, denominators, or axes are undefined and the text does not supply them. I hold this bar high: as the normal-priority dimension, `block` is reserved for presentation failures that defeat comprehension, not for style.
- `what_triggers_warn`: Structural imbalance that costs the reader — a methods account too compressed to follow on one pass, an implications section longer than the evidence supporting it, or a results narrative that requires flipping back to reconstruct definitions. Figure or table captions that are not self-sufficient. Inconsistent terminology for the same construct across sections. Abstract emphasis that does not match the body's actual findings. Venue-convention lapses that an editor would return.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity

Research-ethics and educational-data-governance specialist; chair of a university IRB education-research panel; adviser to institutions on secondary use of LMS trace data under student-privacy regimes (FERPA / GDPR-equivalent). Background in information systems, with applied experience in institutional learning-analytics deployment and in what "increase dashboard engagement" becomes once an institution operationalizes it. I am an outsider to learning analytics as a research field: I read this manuscript as someone who would have to approve the study, or advise a provost acting on it.

### Overall Recommendation

Reject (resubmission possible after redesign of consent and disclosure, and retraction of the causal and generalization claims)

### Confidence Score

4

### Summary Assessment

The manuscript's Methods section documents, in its own words, that "students were not informed that their dashboard activity data would be analyzed for this study" (§3.2), while consent was obtained only for the survey. There is no ethics-approval statement, no de-identification account, no data-availability statement, and no funding or conflict-of-interest declaration. On its own that is a submission-blocking gap at every venue this work could plausibly target, and it is not curable by rewriting: consent for the behavioral half of the dataset cannot be obtained retrospectively.

That gap then compounds with the Conclusion. §6 tells "higher education institutions worldwide" that dashboards plus "encouraging students to engage with them" is a "dependable strategy," on the basis of one course at one institution where the observed variable was *spontaneous* dashboard opening. The paper recommends worldwide scale-up of a practice whose own study did not disclose itself to its subjects, and whose central artifact — including the peer-comparison band that §2 identifies as a demotivation risk (Osei, 2020) — is never described concretely enough for another institution to know whether they have the same thing.

The topic is worth studying, the limitations section shows genuine awareness, and the SRL framing is a real asset. But the paper as written asks institutions to act, and from where I sit an institution acting on it would be taking on unexamined equity, consent, and governance risk.

### Strengths

1. **The research question matters to practice, not only to the literature.** Institutions are buying dashboards now, largely on vendor claims. A study that asks whether dashboard use tracks course completion is asking the question a provost actually has. That practical grounding is real and I want to see the paper survive to answer it.

2. **§2 names the field's own failure modes.** The demotivation account (Osei, 2020), the click-proxy measurement critique (Vandermeer, 2023), and the causal-overreach audit (Ibarra, 2023) are all raised. An outsider reading §2 alone would conclude the authors know exactly what the traps are. That knowledge is an asset the rest of the manuscript should be made to use.

3. **§5.1 admits the artifact is idiosyncratic.** "The specific dashboard design used here differs from those deployed elsewhere; the particular interface features may shape how students respond" is precisely the right instinct about transferability, and it is stated without defensiveness.

4. **The median-split disclosure is honest.** §3.3 flags its own dichotomization as "a coarse simplification of a continuous measure … adopted for interpretability rather than statistical efficiency." Whether the choice is defensible is R1's call; the disclosure itself is the behavior a reviewer should reward.

5. **The measurement construct is not oversold in the Measures section.** §3.3 states plainly that engagement is a count of dashboard-opening sessions. The problem is not concealment at the point of definition — it is what happens to that definition by §6.

### Weaknesses

1. **W1 — Undisclosed secondary use of identifiable behavioral data, with no ethics-governance apparatus reported.** §3.2 states that students were not told their dashboard activity would be analyzed; consent covered the survey only. Behavioral logs were collected for course delivery, then repurposed for research under a consent that did not reach them, and the log data were linked at the individual level to survey responses and to retention outcomes — so this is not aggregate institutional reporting, it is individually-identifiable observation. Compounding: no IRB or ethics-approval statement, no waiver-of-consent justification, no de-identification or data-handling description, no data-availability statement, no funding or COI declaration. *Why it matters:* every venue named as a plausible target requires an ethics statement; more importantly, the disclosure gap is the exact practice the paper recommends scaling. *What would need to be true for the claim to stand:* either (a) an approved protocol with a documented consent waiver or an institution-wide research-use notice in effect during the study term, reported with the approving body and protocol identifier; or (b) if no such approval exists, the behavioral-log analysis cannot be published in this form, and the honest path is a retrospective disclosure to the ethics body before resubmission. Add the four missing statements regardless of which path applies.

2. **W2 — "Encouraging engagement" is not the variable that was measured.** §6 recommends "encouraging students to engage with" dashboards. The study observed spontaneous opening in a setting where the dashboard "required no separate opt-in" (§3.1). There is no basis for assuming that engagement produced by institutional prompting — nudge emails, advisor follow-up, participation credit — carries the association observed in voluntary use. *Why it matters:* an institution reading §6 literally will build precisely the induced-engagement program the study did not study, and the most likely operational endpoint is that dashboard-opening becomes a compliance metric monitored by advisors, converting a self-monitoring aid into surveillance. *Suggestion:* restrict §6 to what was observed, and state explicitly that whether induced engagement carries the same association is an open question requiring a randomized encouragement design. That reframing costs the paper nothing it legitimately has.

3. **W3 — The peer-comparison band is recommended for scale-up while the paper's own §2 flags it as a hazard, and the paper never returns to it.** §3.1 tells us the dashboard displays "a peer-comparison band." §2 tells us relative-standing feedback can discourage struggling students, with the effect depending on goal orientation (Osei, 2020). §5 and §6 then recommend the artifact as a whole with the hazard unmentioned. *Why it matters:* the students most likely to be harmed by relative-standing feedback are the ones least likely to appear in a mid-term volunteer sample, so this study's design is structurally blind to its own most plausible adverse effect. *Suggestion:* either revisit Osei (2020) against your own data — do low-engagement students who *did* look show lower perceived control, and what happened to students whose sessions dropped to zero after early use? — or state in §5.1 that the design cannot detect demotivation and therefore cannot support recommending the peer-comparison feature.

4. **W4 — Students appear only as data sources, never as stakeholders.** The paper considers instructional designers and institutions (abstract, §6). It does not consider what it is like to be measured: whether students knew the dashboard was logging them (§3.2 says they did not know it was being analyzed), whether an unfavorable band demotivates, whether students with constrained device or connectivity access can generate dashboard sessions at all, or whether students have any interest in how their behavioral data are governed. *Why it matters:* dashboard sessions are partly a measure of access. A commuting student on a phone with a data cap opens the dashboard less than a residential student with a laptop, and that student also faces higher attrition risk for reasons unrelated to dashboards. An engagement-retention association can therefore be partly an access-retention association wearing a dashboard's clothes — and a recommendation to "encourage engagement" would then load an additional compliance demand onto the students with the least capacity to meet it. *Suggestion:* add a stakeholder paragraph to §5 covering student experience, differential access, and data governance, and — if the platform records it — report device/access mix descriptively.

5. **W5 — The artifact under study is not identifiable, so transferability cannot be judged, yet §6 claims worldwide generality.** The dashboard is described in nine words of features (§3.1); there is no screenshot, no vendor or platform name, no version, no statement of what students actually saw or how often the display refreshed. The sessionization rule (30-minute inactivity) is adopted as "the platform's default" — a vendor artifact treated as a construct boundary without argument. *Why it matters:* an institutional reader cannot determine whether their dashboard is the same class of object, which makes "generalizable lever" unactionable at best and misleading at worst; §5.1 concedes idiosyncrasy and §6 contradicts the concession. *Suggestion:* add a figure or annotated description of the interface, name the platform and version, and state whether the sessionization rule was validated against any behavioral criterion or simply inherited. Then let §6 claim only what §5.1 concedes.

### Detailed Comments

#### Assumption Audit

**Explicit assumptions.** The paper states its theoretical premise plainly: "visibility supports self-regulation" (§1), operationalized as dashboards supplying "the feedback that fuels the reflective phase." Under outside scrutiny this premise is conditional in a way §1 does not carry. §2 itself supplies the condition — dashboards support monitoring "only when learners possess the regulatory strategies to act on what they see" (Rutledge & Berange, 2022) — and then §5 proceeds as though the condition were satisfied. The second explicit assumption is that course retention is the appropriate outcome. From a governance seat this is not self-evident: retention is an institutional interest, and for an individual student a well-timed withdrawal from a gateway statistics course can be the correct decision. A paper that recommends institutions optimize for completion should say once that student interest and institutional interest are not identical here.

**Implicit assumptions.** Three premises the manuscript needs but never states.

The first: that dashboard-opening is a behavioral signal rather than a trait proxy. Nothing in the design distinguishes "checking the dashboard" from "being the kind of student who checks things," and the students who check things were going to finish the course. The paper's own §2 anticipates this ("engagement without adjustment") and §5 does not use it.

The second, and the one I have not seen named anywhere in the manuscript: that dashboard access is uniformly available. Sessions require a device, connectivity, and discretionary time. Table 1 shows a minimum of 0 sessions — some students in the analytic sample never opened it at all — and the manuscript never asks who those students were. Treating that count as a pure motivation index assumes away material inequality, and it is the assumption that turns an equity-framed recommendation into a potentially regressive one.

The third: that "engagement" is a quantity an institution can increase without changing what it is. §6's recommendation depends on this; §3.3's definition (session counts) does not support it. Encouraged opening and spontaneous opening are different behaviors that produce identical log rows, which is exactly why the log cannot tell them apart.

**Paradigmatic assumptions.** The manuscript operates inside a more-visibility-is-better paradigm, and inside a linear-causality frame in which an association observed in a voluntary deployment is treated as a lever to be pulled ("increasing dashboard engagement therefore raises the probability that a student completes the course," §5). From an information-systems seat this is a familiar pattern with a familiar failure mode: instrumenting a behavior changes the behavior's meaning. Once opening the dashboard is encouraged, monitored, or credited, it stops indexing self-regulation and starts indexing compliance — and the association that motivated the intervention is the first thing the intervention destroys. This paradigm is standard in learning analytics and I do not ask the authors to abandon it, only to name it as a boundary condition on §6.

#### Cross-Disciplinary Connections

**Parallel research.** Research-ethics and data-governance scholarship on the secondary use of administrative and trace data has worked through this exact problem — data collected for service delivery, later analyzed for research — and has settled on institution-wide research-use notices at enrollment plus documented waiver criteria as the standard remedy. Adopting that vocabulary in §3.2 would let the authors say what governance was in place instead of leaving a bare "students were not informed." Separately, the information-systems literature on measurement dysfunction (what happens when a proxy becomes a target) speaks directly to W2 and would give §5 a principled reason to distinguish observed from induced engagement.

**Borrowing opportunities.** Three concepts would materially strengthen the paper at low cost. *Purpose limitation* (data-protection law) names precisely the gap in §3.2 and turns an admission into an analyzable design fact. *Contextual integrity* (privacy theory) explains why students may be untroubled by an instructor seeing their activity and troubled by its analysis for research, which is the distinction §3.2 straddles. *Proxy-target degradation* (measurement/management theory) is the sharpest available statement of why §6's recommendation may not inherit §4.2's association.

**Methodological borrowing.** For the ethics-and-governance layer, a documented consent architecture — what notice existed, what the waiver criteria were, how log and survey data were linked and de-identified — would be a short subsection with a large payoff, and every named target venue expects it. Substantively, the design question W2 raises is answerable: a randomized encouragement design (some students prompted, some not) estimates the effect of *inducing* engagement, which is the quantity §6 needs and the current design does not provide. If the authors also collected any qualitative material — even open-text survey responses — a brief account of how students describe seeing the peer-comparison band would engage the Osei (2020) demotivation account against this deployment rather than leaving it hanging from §2. I recognize the analytic-strength questions here belong to Reviewer 1; I raise the designs only because they are what the ethics and translation problems require.

#### Practical Impact

**Real-world application.** Read as written, §6 authorizes a budget line and a student-communications campaign. A director of student success could take this paper to a cabinet meeting tomorrow. What the paper actually supports is far narrower: in one introductory statistics course at one institution, students who opened a dashboard more often were somewhat more likely to complete the course, among students who volunteered for a survey partway through the term. Those two sentences describe different objects. The gap between them is the paper's central practical problem, and it is fixable by editing §5 and §6 rather than by collecting new data.

**Implementation feasibility.** An institution acting on §6 faces conditions the paper does not mention: an LMS with dashboard capability and a data pipeline behind it; someone to maintain the peer-comparison logic; advisor capacity if dashboard signals are meant to trigger outreach; and a governance decision about whether student-level engagement data may be viewed by staff and for what purposes. The most likely unintended consequence is the one I have described — engagement becomes a monitored metric and the display becomes something students manage rather than use. A second, specific to the peer-comparison band, is that scaling a feature the paper's own literature review flags as demotivating for struggling students distributes the harm to precisely the population the equity rationale in §2 claims to serve.

**Stakeholders.** Students are absent as stakeholders (W4). Instructors are absent entirely: no account of whether the instructor saw dashboard data, whether that shaped grading or outreach, or whether instructor behavior during the term co-varied with student dashboard use. Advisors appear nowhere, though they are who an institution would task with acting on engagement signals. Power asymmetry is undiscussed: the students in §3.2 were enrolled in a required course, recruited by an announcement from the platform that was already logging them, and not told about the analysis. That is not a neutral consent setting, and it deserves a sentence.

#### Broader Implications

**Ethical dimensions.** The core issue is W1 and I will not restate it. Two additions. First, the linkage: connecting behavioral logs to survey responses and to retention outcomes at the individual level produces a record materially more sensitive than either source alone, and nothing in §3.2 or §3.3 describes how that linkage was performed, held, or de-identified. Second, the recursive problem: this paper recommends worldwide adoption of student-facing behavioral monitoring while itself demonstrating that such monitoring can be analyzed without telling the students. If dashboards scale on this evidence base, undisclosed secondary use scales with them. That connection is the finding I most want the authors to sit with, because it is visible only from outside the field.

**Social impact.** The differential-access mechanism in W4 is the main risk, and it inverts the paper's own equity framing: a recommendation that institutions encourage dashboard engagement, applied to a population with unequal device and connectivity access, adds a demand that falls hardest on the students who can least absorb it while flattering the institution that it has acted on retention. The peer-comparison band adds a second inversion for performance-avoidance-oriented students — §2 says so and §6 forgets it. A third consideration the paper's "worldwide" reach makes unavoidable: institutional contexts differ in whether opting out of behavioral logging is even possible, and a recommendation pitched globally cannot be silent on that.

**Future directions.** Ranked by what I would fund. (1) A randomized encouragement design, which answers the question §6 wants answered and is the only design that licenses its language. (2) A study of the demotivation pathway specifically — recruit before the term rather than mid-term, retain students who withdraw, and measure affect after peer-comparison exposure; this is the missing half of the evidence base and the current design cannot supply it. (3) A governance study of what institutions actually do with student-level engagement data once they have it, which is the question a provost has and which no dashboard-outcome study currently answers. (4) An access-stratified reanalysis: whether the engagement-retention association survives conditioning on device and connectivity access.

### Cross-Disciplinary Reading Recommendations

- **Wexler, T., & Ojo, A. (2020).** *Retention modeling with LMS trace data: A cautionary study.* Present in this manuscript's own reference list (p. 132) but uncited in the body. On the title alone it addresses this manuscript's exact design, and the authors should engage it in §2 and §5 rather than list it.
- **Osei, K. (2020)** and **Ferro & Nakamura (2021)**, both already in the reference list, need to be brought into contact with the peer-comparison band in §3.1 and with §6's recommendation. This is a use-what-you-cited request, not a new-reading request. I note without pursuing it — it is Reviewer 2's territory — that the Ferro & Nakamura title as listed ("When dashboards demotivate") appears to point the opposite way from the claim §2 attributes to it, which matters here because §2's equity rationale is what makes §6's recommendation sound safe.
- **[UNVERIFIED] Search lead — purpose limitation and secondary use of educational administrative data.** I can attest the concept and its standard remedies from IRB practice, not to a specific citation from session materials. Search terms: "secondary use" + "learning analytics" + consent waiver; "purpose limitation" + student data.
- **[UNVERIFIED] Search lead — contextual integrity as a privacy framework.** Widely used in privacy scholarship to explain why the same data flow is acceptable in one context and not another; directly applicable to §3.2's course-delivery-to-research shift. Search terms: contextual integrity + educational data.
- **[UNVERIFIED] Search lead — proxy-target degradation / measurement dysfunction.** The literature on what happens when a measured proxy becomes a management target; the sharpest available frame for W2. Search terms: measurement dysfunction; surrogation; gaming of performance metrics.

I have deliberately recommended no field-canonical learning-analytics or SRL sources: that is Reviewer 2's coverage assignment, and I am not positioned to audit it.

### Questions for Authors

1. What ethics review covered the behavioral-log component of this study? Please name the approving body and protocol identifier, and if consent was waived, state the waiver criteria that were applied. If there was no review of the log component, please say so plainly.
2. §3.2 says students were not informed their dashboard activity would be analyzed. Was there any institution-wide notice at enrollment that LMS activity data may be used for research? If yes, quote it. If no, on what basis was the log analysis conducted?
3. How were behavioral logs linked to survey responses at the individual level, who held the linkage key, and what de-identification was applied before analysis?
4. §6 recommends "encouraging students to engage." What is your basis for expecting institutionally-induced engagement to carry the same association as the spontaneous engagement you observed? If you have none, would you restrict §6 accordingly?
5. Your dashboard includes a peer-comparison band, and your §2 identifies relative-standing feedback as a demotivation risk for struggling students. Do you recommend scaling that specific feature, and what in your data speaks to its safety?
6. Table 1 shows a minimum of 0 dashboard sessions. Who are those students, what happened to them, and what would you say to the possibility that dashboard sessions partly measure device and connectivity access rather than motivation?
7. Which dashboard is this — platform, version, and what did students see? Was the 30-minute sessionization rule validated against any behavioral criterion, or inherited from the platform?
8. Would you accept that §5.1's concession ("differs from those deployed elsewhere") and §6's claim ("generalizable… worldwide") cannot both stand, and which one do you want to keep?

### Minor Issues

- No data-availability statement; none of the named target venues would waive it for LMS trace data.
- No funding or conflict-of-interest declaration. Given that the study evaluates a platform feature, whether any vendor relationship exists is material and should be stated even if the answer is none.
- §3.1 says the dashboard "required no separate opt-in" and §3.2 says participation "depended on students electing to answer the announcement." Both may be true of different things (tool access vs. study participation), but as written a reader has to work that out. One clause would fix it.
- §3.2's "random sample" and the following paragraph's volunteer-opt-in recruitment describe different sampling designs. I flag this only because it changes who the ethics analysis applies to; the design implications belong to Reviewer 1.
- "Meridian State University" is named while nothing else about the deployment is identifiable. If the institution consented to being named, fine; if this is meant as a pseudonym, say so.
- §1's promise to "distinguish the pattern in the data from the causal story" is a commitment §5's opening sentence does not keep. An outside reader notices this immediately, and it costs the paper credibility it does not need to spend.
- No prompt-injection or reviewer-directed instruction content was found in the manuscript; nothing to report on the integrity class.

---

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor

score: warn

Assessed against my Phase 1 plan from the outsider seat, not as a statistics audit. The `block` trigger required either an undisclosed design-inference mismatch or absent basic parameters. Neither is met on my reading: §3.1 and §3.2 do disclose that the deployment was universal-access and that recruitment was voluntary and mid-term, §3.3 states what engagement is, and §5.1 names the single-course boundary and the click-proxy limit. The `warn` triggers fire on several counts — engagement is operationalized without justification, the sessionization rule is inherited from a vendor default rather than defended, students with zero sessions are never accounted for, no reproducibility affordance is offered and no reason is given, and the artifact under study is not identifiable enough for external assessment. My W1 ethics-reporting gap also sits partly here as a data-handling and reproducibility failure (no de-identification account, no linkage description, no data-availability statement). Warn rather than block: the parameters are present and the disclosures, though thin, exist. I note that whether the *reported statistics* are internally consistent is Reviewer 1's determination and I have not scored it.

### D2: domain_accuracy

score: warn

Retention is defined operationally (§3.3, completion of the final assessment) but the manuscript never distinguishes course-level completion from institutional persistence, while §1 opens on "undergraduate attrition" and §6 reaches for retention "across programs and disciplines" — a boundary a higher-education reader would expect marked. "Engagement" is silently narrowed from the multidimensional construct the SRL framing invokes to a session count, and §2's own citation of Vandermeer (2023) shows the authors know it. §6's "dependable strategy" overstates what the cited evidence base supports on the manuscript's own account of that base (§2, Ibarra 2023). These are the `warn` patterns I committed to: cross-field terminology used loosely, and claim strength exceeding the cited evidence. I did not reach `block`, which required a substantive claim resting on a construct its home field would reject. I note that the apparent inversion of Ferro & Nakamura (2021) — §2's stated claim runs against that work's listed title — would be a `block`-class misrepresentation if confirmed, and that the equity rationale my W3 depends on is built on it; adjudicating source fidelity is Reviewer 2's assignment and I defer the scoring of it there rather than double-count it.

### D3: argumentative_coherence

score: block

Both of my committed `block` triggers fire, independently.

First trigger: the central thesis depends on an unexamined assumption that, once surfaced, plausibly dissolves the finding. §5 asserts "dashboard engagement improved course retention" and that "increasing dashboard engagement therefore raises the probability that a student completes the course." The same association is at least equally consistent with already-persisting, already-organized students being the ones who open dashboards, and with dashboard sessions partly indexing device and connectivity access. §2 supplies both readings in the authors' own words — "engagement without adjustment," and the click-proxy caveat — and §5 uses neither against its own claim. The reverse and common-cause readings are never raised where they matter.

Second trigger: the recommendation's warrant exceeds the stated design by a wide margin. §6 tells institutions worldwide that dashboards plus encouragement are "a dependable strategy… generalizable" for retention "across programs and disciplines," from one course, one term, one institution, and a volunteer sample recruited mid-term. A practitioner acting on §6 would be acting on a claim this study never made — and, per my W2, on a different variable (induced engagement) than the one observed. §5.1's concession that the interface "differs from those deployed elsewhere" contradicts §6 directly, which sharpens rather than mitigates the finding: the authors possess the correct boundary statement and did not apply it.

I score this `block` in full awareness that it lies close to Reviewer 1's inferential territory and the Devil's Advocate's consistency territory. My warrant is the one my seat owns: what the argument authorizes an institution to do. I have not evaluated fallacy structure or recomputed any statistic.

### D4: cross_disciplinary_relevance

score: block

My committed second `block` trigger fires squarely: the manuscript addresses recommendations to practice and policy — "for higher education institutions worldwide, the implication is clear" (§6) — while students, the population most directly affected, appear only as data sources. There is no consideration of their experience of being measured, no treatment of unequal digital access despite dashboard sessions requiring a device and connectivity, and no engagement with the privacy or governance dimensions of behavioral monitoring, in a manuscript whose own §3.2 states that students were not informed their behavioral data would be analyzed. Acting on §6 therefore carries exactly the unexamined equity and harm risk my Phase 1 plan named: a demand that falls hardest on the least-resourced students, and a scale-up of the peer-comparison feature the manuscript's own §2 flags as demotivating for struggling learners.

The first `block` trigger also fires: §6's generalization claim crosses into higher-education practice with no substantiation on that field's terms and no acknowledgement that a boundary is being crossed — while §5.1 concedes the artifact is idiosyncratic. Ethics is not a stakeholder oversight here; it is a documented absence (no ethics approval, no waiver justification, no de-identification account, no data-availability, no funding/COI statement) in a paper recommending the practice globally. This is the contract's high-priority dimension and my primary assignment, and the evidence is in the manuscript's own text rather than in my inference.

### D5: writing_and_structure

score: warn

I hold `block` here for presentation failures that defeat comprehension, and that bar is not met: the IMRaD structure is complete, the prose is clear at sentence level, and an outside reader can follow §3 to §4 on one pass. The `warn` triggers do fire. Table 1 reports a final-exam variable that §3.3 Measures never defines, so a reader meets a measure for the first time in Results. Table 2's caption is not self-sufficient — no note on why its group sizes differ from the sample the same paragraph describes, and no units or denominator statement. §3.1 and §3.2 read inconsistently on what "opt-in" refers to. §6 is pitched at a rhetorical level the evidence sections do not reach, which is a structural imbalance rather than a stylistic one. And the abstract's characterization of the association does not sit comfortably with §4.2's, though establishing which value the manuscript stands behind is Reviewer 1's determination, not mine — I score only the reader-facing consequence, which is that the abstract and body do not currently support each other.

## Failure Condition Checks

### F1

fired: true

Predicate: any mandatory dimension scores `block`. Mandatory dimensions in this contract are D1, D2, D3. D3 (argumentative_coherence) scores `block`. Condition fires. Severity 90.

### F2

fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. D1 `warn`, D2 `warn`, D3 `block` — three of three. Condition fires. Severity 70. (The `majority` quantifier on this entry is panel-level machinery for the synthesizer; I evaluate only the predicate against my own scores.)

### F3

fired: true

Predicate: any high-priority dimension scores `block`. D4 (cross_disciplinary_relevance, priority `high`) scores `block`. Condition fires. Severity 60.

### F0

fired: false

Predicate: every mandatory dimension scores `pass`. D1 `warn`, D2 `warn`, D3 `block`. Condition does not fire.

## Review Body

I write as an outsider to learning analytics — a research-ethics and data-governance specialist who would sit on the panel reviewing this protocol, and who advises institutions that would act on this paper's Conclusion. Three findings belong to my seat and to no other.

The first is documented in the manuscript's own Methods. §3.2 states that students were not informed their dashboard activity data would be analyzed for this study; consent covered the survey only. Behavioral logs gathered for course delivery were repurposed for research and linked at the individual level to survey responses and retention outcomes. There is no ethics-approval statement, no waiver justification, no de-identification or linkage account, no data-availability statement, and no funding or conflict-of-interest declaration. Four of those five are recoverable by writing them; the consent gap for the log component is not recoverable retrospectively, and it needs to be brought to the ethics body before this component is published in any form.

The second is that §6 recommends something the study did not observe. The measured variable is spontaneous dashboard opening in a setting where the tool required no opt-in. §6 recommends "encouraging students to engage," which is induced opening — a different behavior producing identical log rows. There is no basis in these data for expecting the association to survive the substitution, and the most likely institutional endpoint is that dashboard-opening becomes a monitored compliance metric, at which point it stops indexing self-regulation altogether. The paper should restrict its recommendation to what it observed and name the randomized encouragement design that would license the stronger claim.

The third is the equity inversion. §3.1 tells us the dashboard displays a peer-comparison band. §2 tells us, citing Osei (2020), that relative-standing feedback can discourage struggling students depending on goal orientation. §5 and §6 recommend the artifact without returning to that hazard — and because recruitment happened mid-term and non-respondents were dropped, the students most likely to have been discouraged are structurally absent from the sample. Meanwhile dashboard sessions require a device, connectivity, and discretionary time; Table 1's minimum of zero sessions is never examined. A recommendation that institutions push engagement, applied to a population with unequal access, adds a demand that falls hardest on the students least able to absorb it, while the institution records that it has acted on retention. The equity rationale in §2 and the recommendation in §6 point in opposite directions, and only the outside seat is positioned to say so.

These three compound into the recursive problem I would put to the authors above all others: this manuscript recommends worldwide adoption of student-facing behavioral monitoring, and in doing so demonstrates that such monitoring can be analyzed without telling the students. If dashboards scale on this evidence base, undisclosed secondary use scales with them.

What I am not saying: I have not recomputed a single statistic, have not audited literature coverage, and have not checked whether the manuscript's reported numbers agree with one another. Reviewer 1 and Reviewer 2 own those questions, and where my findings touch theirs — the sampling contradiction in §3.2, the apparent inversion of Ferro & Nakamura in §2 — I have flagged the boundary and deferred the scoring rather than double-count it.

What would make this publishable, in order: document the ethics governance or withdraw the log analysis; add the four missing declarations; identify the artifact (platform, version, what students saw, whether the sessionization rule was validated); retract §5's causal sentence and §6's "dependable… generalizable… worldwide" to match §5.1's own concession; add a stakeholder section covering student experience, differential access, and data governance; and either engage Osei (2020) against your own data or state that the design cannot detect demotivation and therefore cannot support recommending the peer-comparison feature. The question is worth answering and the authors clearly know the traps — §2 lists them. The manuscript's problem is that it does not use what it knows.

## Editorial Decision

Precedence resolution: three of my four conditions fired — F1 (severity 90), F2 (severity 70), F3 (severity 60). Highest severity wins; F1 at severity 90 is decisive with no tie to break. F0 did not fire.

editorial_decision=reject_or_major_revision

---

## SEAT — Devil’s Advocate

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** The contract asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the field's peer-review bar. Read adversarially, this is not a checklist of whether methods sections exist — it is the question of whether the inferential machinery could survive a hostile re-analysis. For a retention study of this shape, the adversarial reading is: whatever design the authors chose, the burden is on them to show that the design can carry the weight the conclusions place on it, and that a reader could tell from the manuscript alone what was actually done, in what order, to whom, and with what analytic choices fixed in advance versus chosen after seeing data. My job is not to score the elegance of the method but to ask what the method *cannot* rule out, and whether the paper acknowledges that. Note the DA boundary: I do not adjudicate statistical design or power analysis as R1 does — I challenge whether the reported methodological record supports the argument built on top of it, and whether analytic latitude was left unbounded.

**D2 — domain_accuracy (mandatory).** The contract asks whether claims align with current domain evidence, whether prior work is represented correctly, and whether domain terminology and reported results are factually right. Adversarially, my interest is not coverage completeness (that is R2's territory) but *directional* accuracy: whether the literature is invoked as a supporting chorus rather than a genuine evidentiary landscape, whether contradicting findings that a competent domain reader would expect to see are absent, and whether terms of art are used in a sense the field would not recognize. Learning analytics and retention research both carry well-known contested findings and well-known definitional slippage; a paper that reports only concordant prior work, or that uses a contested construct as if it were settled, is exhibiting evidence-selection bias even if every individual citation is real and correctly quoted. This is my cherry-picking and confirmation-bias lens, not a bibliography audit.

**D3 — argumentative_coherence (mandatory).** The contract asks whether the core thesis is internally consistent, whether evidence supports the claims made, and whether any fallacy undermines the central argument. This is my home dimension and the one on which I am hardest. The relevant questions are: does the conclusion follow from what was actually shown, even granting the evidence; are there hidden premises the paper never states and never defends; is there a simpler rival explanation that fits the same evidence at least as well; and does the paper's own framing quietly convert an association into a mechanism. A title of the form "X and Y: Evidence from a deployment" is a claim about what the evidence licenses, and I will hold the conclusion to exactly the strength the design can bear — no more, and equally, no less, since over-demanding is itself a calibration failure.

**D4 — cross_disciplinary_relevance (high, not mandatory).** The contract asks whether framing, definitions, and implications are accessible to adjacent-field readers and whether interdisciplinary claims are substantiated. This paper sits at a genuine three-way junction — learning analytics, educational technology, and higher-education retention studies — and each of those brings its own construct definitions and its own accepted evidence standards. Adversarially, the failure mode I hunt is a claim that borrows authority across the boundary without paying the price: importing "retention" or "persistence" from the higher-education literature (where it carries specific operational and theoretical baggage) while measuring it in a way only the analytics side would accept, or generalizing a technology-deployment finding into an institutional-policy implication that the deployment cannot support. I also note explicitly which stakeholder voices are structurally absent, without elaborating on what they would say — that elaboration is R3's role, not mine.

**D5 — writing_and_structure (normal).** The contract asks about organization, clarity of exposition, figure and table quality, and adherence to venue conventions. Adversarially, I care about this only where it is load-bearing: where imprecise structure or a caption hides an inferential gap, where a figure's visual framing implies a relationship the data do not carry, or where the reported numbers in text and table diverge. Pure presentation defects are MINOR by definition under my severity rules, and — per the surface-form parity gate — I must not let polished prose buy credibility for a weak claim, nor let rough prose discount a sound one. At 2,487 words this is a short manuscript, which cuts both ways: brevity is a legitimate venue choice, not a defect, but brevity also cannot be used as an excuse for absent methodological record. That distinction is the substance of my scoring here.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for`: Whether the manuscript states, unambiguously and in one place, what was actually done — unit of analysis, who was included and who was excluded, over what period, and how the retention outcome was operationalized (re-enrollment? course completion? non-withdrawal? at what census point?). Whether "dashboard engagement" is defined as a measured quantity with a stated derivation (logins? sessions? a composite index? thresholded into groups?) rather than referred to as if self-evident. Whether the analysis is described in enough detail to be re-run in principle: model form, what was adjusted for, how missing data and non-users were handled. Whether analytic choices (cutpoints, group definitions, covariate sets, outcome windows) are presented as pre-specified or acknowledged as chosen after inspecting data. Whether attrition from the analytic sample is reconciled, and whether the denominator is stable across reported figures. Whether the deployment context imposes a structural constraint the design cannot escape — non-random exposure, self-selection into dashboard use, staggered rollout, concurrent institutional interventions — and whether the paper names that constraint rather than letting the reader discover it. Whether reproducibility affordances are addressed at a level the *learning analytics* community actually practices (institutional data governance routinely bars raw-data release; the checkable expectation is a described derivation and stated restriction, not an open dataset).
- `what_triggers_block`: The manuscript's central quantitative claim cannot be located to a described procedure — i.e., a headline result is reported for which the outcome definition, the exposure definition, or the analytic sample is not recoverable from the text, so no reader could tell what was compared to what. Equivalently: reported numbers are mutually inconsistent across text/table in a way that cannot be reconciled (different N for the same group, a stated effect that does not follow from the reported cells), or the design as described cannot in principle produce the quantity the paper reports. A single unrecoverable-but-load-bearing procedure is sufficient; this is the "foundation collapse" trigger, and it fires on absence of the *record*, not on absence of my preferred design.
- `what_triggers_warn`: The procedure is recoverable but leaves material analytic latitude undeclared — engagement thresholds or group cutpoints introduced without justification or sensitivity check, covariate selection unexplained, missing/non-user cases silently dropped, or an outcome window whose choice is unstated. Also fires when a known structural confound of this deployment shape (self-selection into dashboard use; students already on track being the ones who check dashboards) is unaddressed anywhere in the manuscript, or when reproducibility is not discussed at all — not merely restricted. Multiple such gaps that individually warn do not automatically compound to block; block requires unrecoverability, per the trigger above.

### D2: domain_accuracy

- `what_to_look_for`: The directional balance of the evidence base — whether cited prior work runs uniformly in the direction of the paper's thesis, and whether the well-known null, mixed, or adverse findings in learning-analytics dashboard research are represented at all. Whether contested constructs are treated as settled: "engagement," "at-risk," "retention" versus "persistence" versus "progression" each carry distinct operational meanings in higher-education studies, and conflating them silently is a domain error, not a style choice. Whether cited work is characterized in a way its authors would accept — a study reported as showing an effect it did not claim, a correlational finding cited as causal support, a pilot cited as an established result. Whether reported statistics are internally coherent with the described design (effect direction, plausible magnitude, degrees of freedom implied by the stated sample). Whether the paper's own institutional context is generalized into a domain-level claim without the qualifier the field would require.
- `what_triggers_block`: A load-bearing factual misrepresentation — a cited source characterized as supporting a claim it does not support, a domain term used in a sense that inverts its accepted meaning where the argument depends on that meaning, or a reported result that is arithmetically or logically impossible given the stated design. The test is that correcting the error would change what the paper is entitled to conclude. Per the field-norm gate: if my severity here rests on "the field should cite X," I must be able to name the field's actual accepted-practice boundary from a checkable source; if I cannot, this down-rates to advisory rather than block.
- `what_triggers_warn`: Systematically one-directional citation — supporting findings present, the field's known contradicting or null findings absent, with no acknowledgment that the evidence base is mixed. Also fires on definitional slippage that does not invert meaning but blurs it (using retention and persistence interchangeably; treating a proxy for engagement as engagement itself), on prior work summarized more strongly than its own abstract would license, and on unqualified generalization from this single deployment to "learning analytics dashboards" as a class.

### D3: argumentative_coherence

- `what_to_look_for`: The exact logical distance between what was measured and what is concluded — specifically whether an observed association between dashboard engagement and retention is at any point spoken of as if the dashboard *produced* the retention, through word choice ("improved," "led to," "impact," "effect of") or through implication in the abstract, discussion, or recommendations even where the results section is careful. Hidden premises: that engagement is exogenous rather than a symptom of the same underlying student characteristics that drive retention; that the intervention is the dashboard rather than everything bundled with its rollout; that non-engagers are a valid counterfactual for engagers. Internal contradictions between sections — a limitation conceded on one page and then contradicted by a recommendation on the next. Whether the reverse-causation and common-cause explanations are named and confronted, or merely gestured at in a limitations paragraph and then ignored in the conclusion. Whether a more parsimonious rival account (selection: conscientious students both check dashboards and persist) fits the reported pattern at least as well as the paper's account. Whether the conclusion would survive if the single strongest alternative explanation were true.
- `what_triggers_block`: The paper's headline conclusion does not follow from its own evidence — a causal or quasi-causal claim (in title, abstract, discussion, or recommendation) resting on an observational association without a design feature or argument that rules out reverse causation and common-cause selection, and without the conclusion being restated at association strength. Also fires on a demonstrated internal contradiction where the paper's own reported data or stated limitation defeats its stated conclusion, or where a strictly more parsimonious rival explanation fits the presented data at least as well and is neither addressed nor excluded. This is the Logic Chain Break / Stronger Counter-Narrative trigger, and on this dimension I will fire it: a mismatch between design-licensed strength and claimed strength is the archetypal failure of this paper's genre, and hedging language in a limitations section does not repair a conclusion that is stated without hedge where it counts.
- `what_triggers_warn`: The causal step is not taken outright, but the paper leans on it — associational results narrated with directional verbs, an abstract stronger than the results section, or policy/practice recommendations that only make sense if the causal reading holds while the text nominally disclaims it. Also fires when rival explanations are acknowledged only as a boilerplate limitation with no analytic engagement, when an unstated premise is doing real work but is defensible if made explicit, or when the "so what" is thin — the incremental contribution over what is already established is not articulated, though the reasoning itself is sound.

### D4: cross_disciplinary_relevance

- `what_to_look_for`: Whether the paper's core constructs are defined in a form an adjacent-field reader could evaluate rather than assumed from within one subfield's house style — a higher-education retention scholar should be able to tell exactly which retention measure was used and how it relates to the institutional definitions they know; a learning-analytics reader should be able to tell exactly what telemetry constitutes "engagement." Whether claims that borrow authority across the boundary pay for it: invoking retention theory to explain a log-data pattern, or invoking analytics precision to make a claim about student persistence, each requires the substantiation the *receiving* field expects. Whether implications are pitched at a level the evidence supports — an undergraduate deployment at one institution generating institution-level or sector-level policy prescriptions is scope inflation. Which stakeholder positions are structurally absent from the framing (students as data subjects, instructors, advising staff, institutional data governance) — I name the absence only; what those stakeholders would say is R3's deliverable, not mine.
- `what_triggers_block`: An interdisciplinary claim is load-bearing and unsubstantiated in the receiving field's terms — e.g., the argument's validity depends on a retention-theoretic mechanism that is asserted rather than evidenced, or on an analytics measurement claim that the higher-education framing cannot check, such that an adjacent-field reader cannot evaluate the paper's central contribution at all. Because D4 is `high` rather than `mandatory`, a block here fires contract condition F3 rather than F1; that lower blast radius does not lower my bar — I fire it only on genuine unevaluability, not on stylistic parochialism.
- `what_triggers_warn`: Constructs are defined loosely enough that adjacent-field readers would operationalize them differently (retention undefined against any institutional census point; engagement described only qualitatively), implications overreach the deployment's scope without a stated boundary condition, or a cross-boundary claim is stated with confidence but supported only from one side of the boundary. Also fires on structurally absent stakeholder framing where the paper's recommendations directly affect the absent group — recording the absence, not arguing their case.

### D5: writing_and_structure

- `what_to_look_for`: Whether the organization lets a reader trace claim → evidence → source without hunting, or whether load-bearing detail is dispersed such that no single place states what was done. Whether tables and figures are self-describing (defined units, stated N, labeled axes) and whether their visual framing matches the data's actual strength — a truncated axis, an unbounded trend line, or a caption that interprets rather than describes is an inferential problem wearing presentational clothes. Whether numbers agree across abstract, text, and tables. Whether the abstract accurately represents the body's strength of claim. Whether length is used honestly: at 2,487 words, whether brevity reflects a legitimately compact short-format contribution or whether the method record has been compressed out of existence. Whether venue conventions (structured sections, reporting expectations, limitation placement) are met at the level the format implies.
- `what_triggers_block`: Presentation defeats evaluability — the manuscript's exposition or its figures/tables actively misstate the evidence (a figure implying a relationship the reported statistics do not support, a caption asserting an interpretation the data do not carry, or figures/text disagreeing on the primary result), so a reader following the presentation reaches a conclusion the underlying data do not license. Pure disorganization, formatting inconsistency, or venue-convention deviation never blocks here — per my severity rules those are MINOR by construction. This trigger fires only where the presentation is the vehicle of a false impression, which makes it a coherence failure surfacing at D5.
- `what_triggers_warn`: Claim-to-evidence tracing requires reconstruction across sections; a figure or table lacks the information needed to read it independently (missing N, undefined units, unlabeled grouping); the abstract states the finding more strongly than the body; internal cross-references or numeric agreement are sloppy without being contradictory; or the compressed length has left a materially thin methods record that is still recoverable in outline. I will not warn on prose register, informality, or non-native phrasing — per the surface-form parity gate, style is not a defect and polish is not evidence.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Devil's Advocate Review

**Manuscript:** *Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment*

**Strengths (for fairness, per Review Discipline #5):** The literature review is genuinely two-sided in construction — it raises the demotivation account (§2, Osei 2020), the measurement-proxy critique (§2, Vandermeer 2023), and the field's own causal-overreach audit (§2, Ibarra 2023) — and §3.3 is candid that the median split is "a coarse simplification… adopted for interpretability rather than statistical efficiency." A manuscript that names its own weak points is doing something many do not.

### Strongest Counter-Argument

The paper's association may be a measurement artifact of its own outcome variable, in which case there is nothing to explain. Dashboard engagement is "the number of distinct sessions… during the term" (§3.3). Non-retention is defined as withdrawing before the final assessment (§3.3). A student who withdraws in week 6 has roughly six weeks in which to accrue sessions; a student who sits the final has fifteen. The exposure variable is therefore mechanically truncated by the outcome. Retention does not merely correlate with session count — it partly *determines* it. Under this account no psychological mechanism is required, no self-regulation is scaffolded, and the dashboard need have no effect whatsoever.

This rival is strictly more parsimonious and fits the reported data at least as well as the authors'. It predicts a modest positive association (observed). It predicts the near-null exam comparison (§4.3: 72.0 vs 69.2) — if regulation were genuinely improving, some performance transfer should appear, and essentially none does. It even predicts the perceived-control difference, via the same third variable: students who are coping stay enrolled, keep clicking, and report feeling in control.

The manuscript never states this possibility, never tests it (a person-time-normalized rate, or engagement censored at a fixed pre-withdrawal window, would begin to), and does not list it among its limitations (§5.1). Until it is excluded, §5's claim that "dashboard engagement improved course retention" has no evidentiary standing at all — not weak standing, none.

### Issue List

#### CRITICAL

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| C1 | 1, 4 (Stronger Counter-Narrative) | Exposure-window truncation: session counts accrue "during the term," while non-retention terminates the accrual window. The predictor is partly an arithmetic consequence of the outcome. A more parsimonious rival account fits all three reported results (modest *r*, null exam difference, perceived-control gap) with no dashboard effect. Not raised, not tested, not listed in §5.1. | §3.3, §4.2, §5.1 | — | — |
| C2 | 4 (Logic Chain Break) | Unhedged causal and interventional claims from a cross-sectional correlation: "dashboard engagement **improved** course retention"; "increasing dashboard engagement **therefore raises the probability** that a student completes the course" (§5); "associated with, **and raises**" (§6). This directly violates the manuscript's own §1 commitment ("we are careful throughout to distinguish the pattern in the data from the causal story") and the standard it endorses in §2 via Ibarra (2023). Stating the correct epistemic rule and then breaking it is worse than naive overclaim, because it removes the excuse of not knowing. | Abstract; §5 ¶1; §6 | — | — |
| C3 | 4 (Data-Conclusion Mismatch) | The primary effect size is reported twice with two different values: Abstract *r* = .42, §4.2 *r* = .24. These differ by roughly threefold in shared variance (17.6% vs 5.8%). No reader can determine what the study found, and the abstract — the part most readers will read alone — carries the larger figure. | Abstract; §4.2 | — | — |
| C4 | 1, 4 (Data-Conclusion Mismatch) | The secondary statistics are internally impossible. (a) *t*(156) = 3.02 for the perceived-control comparison, drawn from 87 item respondents (§4.1) within a 142-student sample — *df* = 156 requires *N* = 158 and is unreachable from either. (b) *t*(140) = 1.31 reported with *p* = .008; that *t* corresponds to *p* ≈ .19. (c) The same paragraph states "all 142 students… were classified," reports *t*(140) implying *N* = 142, and points to Table 2, whose groups sum to 127. Three mutually exclusive sample sizes for one comparison. (d) The prose calls that difference "small" and says it "did not reach a comparable level" — the correct reading — while the reported *p* = .008 is significant under the paper's own α = .05 (§3.4). Text and statistic were evidently written without reference to each other. | §4.3; Table 2 | — | — |
| C5 | 2, 3 (Foundation Collapse) | §2 asserts "Dashboards have been shown to reliably improve outcomes for lower-achieving students… (Ferro & Nakamura, 2021)," and states this "underpins much of the equity-oriented rationale for institutional dashboard deployment." The manuscript's own reference list gives that work's title as *When dashboards demotivate: Peer comparison and the lower-achieving student* (p. Refs). The in-text characterization and the manuscript's own bibliography point in opposite directions. Which is in error cannot be determined from the manuscript — but either way the equity rationale, as written, rests on an unsupported inversion, and the word "reliably" is a strength claim the manuscript has no basis to make. | §2 ¶2; References (Ferro & Nakamura, 2021) | Not applicable — severity rests on an internal contradiction between the manuscript's body and its own reference list, both checkable within the submitted document, not on any claim about field practice. | — |
| C6 | 1, 4 (Foundation Collapse) | §3.2 describes two incompatible sampling designs one paragraph apart: "Participants were drawn from the course enrollment using a random sample," then "Students who chose to respond… formed the study sample; those who did not respond were excluded." Only one can be true, and they carry opposite implications for what the sample represents. Compounding this, recruitment occurred "midway through the term" — so students who disengaged or withdrew before the announcement could not enter the sample at all. In a study whose outcome is retention, the cases most informative about non-retention are structurally absent, and the outcome's variance is conditioned on survival to the recruitment window. Neither the contradiction nor the survivorship is acknowledged anywhere. | §3.2 | — | — |

#### MAJOR

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| M1 | 3, 4 | The Limitations section is decorative. It lists three genuine but peripheral caveats (narrow operationalization, self-report bias, single-course context) and omits every threat that could defeat the conclusion: self-selection into dashboard use, reverse causation, exposure truncation (C1), the mid-term volunteer sample (C6), and the absence of any covariate adjustment. Hedging that systematically avoids the load-bearing threats is not hedging. | §5.1 | — | — |
| M2 | 2 (Cherry-Picking) | Evidence selection runs one direction at the point of interpretation. §2 raises Osei's (2020) demotivation account and Berange-style goal-orientation moderation, then §5 never revisits either against the study's own data — despite the manuscript holding a low-engagement group whose outcomes could have been examined for exactly that pattern. Separately, Wexler & Ojo (2020), *Retention modeling with LMS trace data: A cautionary study* — the single listed source most directly on point for this design — appears in the reference list and is never engaged in the body. The concordant sources are discussed; the cautionary ones are shelved. | §2; §5; References | Not applicable — the omitted counter-evidence is present in the manuscript's own reference list, so this is an internal-engagement failure, not a coverage demand imported from field practice (coverage is R2's). | — |
| M3 | 5 (Overgeneralization) | "Retention" slips between two constructs. §3.3 operationalizes it as within-course completion (remained enrolled and sat the final). The Abstract, §1's framing against "undergraduate attrition" and "the first-year gateway course," and §6's "improving retention across programs and disciplines" all trade on the institutional sense — re-enrollment and persistence across terms. Nothing in this design speaks to whether a single student remained at Meridian State. | Abstract; §1 ¶1; §3.3; §6 | — | — |
| M4 | 4, 6 | The §6 recommendation is about a different variable than the one measured. The study observed *spontaneous* dashboard opening; §6 recommends "encouraging students to engage with them." Engagement induced by institutional pressure is not the same object as engagement freely chosen, and any association attaching to the latter cannot be assumed to transfer. Even granting C2's causal reading in full, the recommendation still does not follow. | §6 | — | — |
| M5 | 8 ("So What?") | The manuscript's own §2 establishes that the field is saturated with correlational dashboard studies and has published an explicit audit of their causal overreach (Ibarra, 2023). The paper then contributes one more correlational dashboard study that commits that error. §5's contribution statement — "our finding that engagement tracks retention aligns with the view that externalized progress cues can support persistence" — restates the prior rather than testing it. The incremental contribution is never articulated, and the literature review argues against it. | §2 ¶5; §5 ¶2 | — | — |
| M6 | 1 | Table 1 reports a "Final exam score (0-100)" variable that appears nowhere in §3.3 Measures. An undeclared measure first surfaces in Results and then carries an inferential test (§4.3) and a table of its own (Table 2). A reader cannot tell how it was obtained, for whom, or with what missingness. | §3.3; Table 1; §4.3 | — | — |

#### MINOR

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| m1 | 1 | §3.1 reports "several hundred students" enrolled; the analytic sample is 142. The participation rate is never stated, so the reader cannot gauge how selective the volunteer sample is. | §3.1, §3.2 |
| m2 | 1 | 55 of 142 respondents (39%) skipped a single item on a "short survey," with no explanation and no comparison of skippers to answerers. | §3.2, §4.1 |
| m3 | 1 | The 30-minute sessionization rule is adopted because it is "the platform's default" (§3.3). An inherited platform artifact is being treated as a construct decision without argument. | §3.3 |
| m4 | 5 | The dashboard is described in one clause — "engagement metrics, assignment progress, and a peer-comparison band" (§3.1) — with no version, vendor, or depiction, while §6 claims worldwide generalizability. §5.1 concedes the interface "differs from those deployed elsewhere," which §6 then contradicts. | §3.1; §5.1; §6 |
| m5 | 5 | Table 1 reports *M* = 3.847 to three decimals alongside *SD* = 0.62 to two. Spurious precision on a 1–5 integer item. | Table 1 |
| m6 | 2 | 9 of 15 reference-list entries are never cited in the body. Noted as an evidence-base integrity signal only; bibliographic coverage is R2's dimension, not mine. | References |

#### Advisory — severity down-rated under Field-Norm Gating (Challenge Dimension 9 / #215)

| # | Issue | Location | Status |
|---|-------|----------|--------|
| A1 | The entire self-regulated learning mechanism (§1, §2, §5) is operationalized by one general-purpose item, "Overall, I feel in control of my learning in this course," defended only by the uncited assertion that "single-item overall ratings are common in dashboard studies to limit survey burden" (§3.3). I judge this construct-validity gap to be real and load-bearing for §5's explanatory account. But grading it CRITICAL or MAJOR would rest on a claim about what educational-psychology measurement practice *requires*, and I cannot name that boundary from a checkable external source within my read scope. Down-rated to advisory. | §3.3; §5 ¶1 | **[FIELD-NORM UNVERIFIED]** |
| A2 | The manuscript carries no ethics-approval, data-availability, funding, or conflict-of-interest statement, and no description of de-identification. I report the absence as a fact. Grading it as a submission-blocking defect would rest on a venue-policy norm I cannot verify from a checkable source here. Down-rated to advisory. The related *internal* fact — §3.2's own statement that "Students were not informed that their dashboard activity data would be analyzed for this study" — is recorded below as a structural stakeholder absence; its adjudication belongs to R3. | §3.2; whole manuscript | **[FIELD-NORM UNVERIFIED]** |

### Ignored Alternative Explanations/Paths

1. **Exposure-window truncation (C1).** Session counts are bounded by weeks enrolled; withdrawal ends accrual. The predictor is partly a consequence of the outcome. Strictly more parsimonious than the SRL account and fits all three reported results.
2. **Common-cause selection.** A stable student characteristic — prior achievement, conscientiousness, course load, or simply not being in crisis — plausibly drives dashboard checking, perceived control, and persistence simultaneously. None of these was measured, so none can be ruled out. This account explains the perceived-control difference (§4.3) without granting the dashboard any role.
3. **Reverse causation.** Students already on track to complete are the ones who keep opening a progress display; students heading for withdrawal stop looking. The paper's own theory supplies this reading as readily as its preferred one, and §5 never confronts it.
4. **Survivorship in the sample (C6).** Mid-term recruitment conditions the sample on having survived to the announcement. Whatever pattern remains among survivors need not hold in the population the retention question is about.
5. **Unconsidered policy alternatives.** §6 recommends dashboard investment without weighing cheaper or more mature levers — instructor early-alert, direct advising outreach, targeted tutoring — against it, and without asking whether the peer-comparison band (§3.1) should be *removed* rather than scaled, given that §2 identifies precisely that feature as the demotivation risk. The paper compares its intervention to nothing.

### Missing Stakeholder Perspectives

*Named only; elaboration of what these parties would say belongs to R3.*

- Students as data subjects — §3.2 states they were not informed their dashboard activity would be analyzed.
- Students who withdrew before the mid-term recruitment window — structurally excluded from a study about withdrawal.
- Instructors and advising staff, who would operate any "encouraging engagement" recommendation (§6).
- Institutional data governance and research-ethics review, absent from a manuscript recommending worldwide deployment.
- Low-engagement and performance-avoidance-oriented students, whom §2 identifies as at risk from the very peer-comparison feature deployed here (§3.1) and whom §5 never returns to.

### Unexamined Premise (Frame-Lock Detection)

**The paper assumes throughout that retention is unambiguously good for the student.** Every framing depends on it: attrition is a "concern" (§1), retention is what dashboards should "improve" (§6), and completion is treated as the terminal good. But a student who withdraws from a required introductory statistics course may be making a correct decision — reallocating effort, avoiding a failing grade, changing direction. The manuscript never distinguishes the institution's interest in retention from the student's interest in a good outcome, and the conflation is what licenses §6's leap from a within-course association to institutional strategy. Once the two are separated, "a dependable strategy for improving retention" becomes a claim about institutional metrics, not about student welfare — and the paper offers no evidence about the latter at all. None of the eight challenge dimensions surfaces this, because it sits underneath all of them.

### Observations (Non-Defects)

- The prose is fluent and the §2 hedging is sophisticated. Per the surface-form parity gate, I have given this no credit: the polish coexists with C2's unhedged causal assertion and C3/C4's impossible statistics, and fluency is not evidence. Symmetrically, none of the findings above turns on wording — each rests on a proposition checkable against the manuscript's own text and tables.
- The manuscript contains no instruction-injection attempt. No imperative addressed to reviewers, no embedded scoring directive, no plea. Reported as clean under the integrity class.
- §3.3's own admission that the median split is "a coarse simplification… adopted for interpretability rather than statistical efficiency" is a genuine, non-defensive disclosure. It is also the model for what §5.1 should have done with the threats in C1, C6, and M1 and did not.
- Several defects here are correctable in principle — claim strength (C2), statistical reporting (C3, C4), citation accuracy (C5), disclosure (A2). C1 and C6 are not: they are properties of how the data were generated, and no reanalysis of this dataset repairs them.

---

contract_role: da

## Dimension Scores

### D1: methodology_rigor
score: block

My Phase 1 block trigger for D1 was unrecoverability of the record, not the absence of my preferred design — specifically, "reported numbers are mutually inconsistent across text/table in a way that cannot be reconciled (different N for the same group…)" or a load-bearing procedure the reader cannot recover. Both fire. Three mutually exclusive sample sizes attach to one comparison in §4.3 (140 from the *df*, 142 from the prose, 127 from Table 2); *t*(156) is unreachable from any stated sample; the primary *r* appears as two different values; and §3.2 states two incompatible sampling designs one paragraph apart, so the analytic sample itself is not recoverable. I am deliberately not scoring the choice of Pearson over a covariate-adjusted model of a dichotomous outcome — that is R1's adjudication. I am scoring whether a reader can tell what was compared to what. They cannot.

### D2: domain_accuracy
score: block

My Phase 1 block trigger was "a cited source characterized as supporting a claim it does not support… the test is that correcting the error would change what the paper is entitled to conclude." §2's characterization of Ferro & Nakamura (2021) as showing dashboards "reliably improve outcomes for lower-achieving students" is contradicted by the manuscript's own reference list, which titles that work *When dashboards demotivate: Peer comparison and the lower-achieving student*. The manuscript itself states the claim "underpins much of the equity-oriented rationale," making it load-bearing. Correcting it removes the equity rationale entirely. Per my Phase 1 field-norm gate, I note this severity does not depend on any claim about what the field should cite — it rests on an internal contradiction inside the submitted document. Definitional slippage between course completion and institutional retention (M3) and the one-directional engagement with the paper's own cautionary sources (M2) independently satisfy the warn trigger.

### D3: argumentative_coherence
score: block

My Phase 1 commitment was explicit that I would fire here on "a causal or quasi-causal claim… resting on an observational association without a design feature or argument that rules out reverse causation and common-cause selection," and on "a strictly more parsimonious rival explanation [that] fits the presented data at least as well and is neither addressed nor excluded." Both fire. §5 states the causal claim without hedge and then adds an interventional one; §6 escalates to a "dependable strategy" that is "generalizable" "worldwide." The exposure-truncation account (C1) is more parsimonious, fits all three reported results including the exam null, and is never named. And the paper's own §1 and §2 commitments make this a demonstrated internal contradiction, not merely an overreach.

### D4: cross_disciplinary_relevance
score: warn

I considered block and am declining it, which I want on the record. My Phase 1 block trigger required genuine unevaluability — an adjacent-field reader unable to assess the central contribution at all. That bar is not met: §3.3 does define retention operationally, so a higher-education reader can recover what was measured even while the Abstract and §6 use the word in the institutional sense (M3). The other candidate leg for a block — that the SRL mechanism is asserted rather than evidenced, resting on one unvalidated item — depends on a measurement norm I cannot ground from a checkable external source within my read scope, so under Challenge Dimension 9 it is down-rated to advisory (A1) and cannot carry a block. What remains is exactly my committed warn pattern: constructs adjacent fields would operationalize differently, implications overreaching the deployment without a stated boundary condition, and a cross-boundary claim (§6's institutional policy prescription) supported from only one side. Scoring warn also costs nothing in the decision, since F3 is subordinate to F1 — I note this so the synthesizer can see the restraint was not free-riding on an already-fired condition.

### D5: writing_and_structure
score: block

My Phase 1 block trigger was narrow and deliberately so: presentation defeats evaluability, where "figures/text disagree on the primary result" or a caption or prose asserts an interpretation the data do not carry. Both fire literally. The Abstract and §4.2 disagree on the primary result (*r* = .42 vs .24), and a reader who reads only the Abstract — most readers — takes away an association three times larger in shared variance. Table 2's group sizes contradict the same paragraph's stated *N*. Table 1 introduces a measure absent from §3.3. §4.3's prose interpretation and its reported *p* contradict each other. This is not disorganization or venue-convention deviation, which my Phase 1 plan classifies as MINOR by construction, and I have warned on no matter of prose register, informality, or style. D5 is `normal` priority, so this block fires no failure condition — I record it because it is true, not because it moves the decision.

## Failure Condition Checks

*Evaluated against my own dimension scores only. The `cross_reviewer_quantifier` field is panel-level machinery for the synthesizer and is not applied here.*

### F1
fired: true

Predicate: any mandatory dimension scores `block`. D1, D2, and D3 are all mandatory and all score `block`. Severity 90.

### F2
fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. Three mandatory dimensions score `block`, which is worse than `warn`. Severity 70; subordinate to F1.

### F3
fired: false

Predicate: any high-priority dimension scores `block`. D4 is the only `high`-priority dimension and scores `warn`, not `block`. Severity 60; would have been subordinate to F1 in any case.

### F0
fired: false

Predicate: every mandatory dimension scores `pass`. None does.

## Review Body

The manuscript fails at a level prior to the question of whether its finding is interesting. Before a reader can ask what dashboard engagement means for retention, they must be able to determine what the study reported — and this manuscript reports its primary result twice with two different values (Abstract *r* = .42, §4.2 *r* = .24), reports a *t* statistic whose degrees of freedom exceed any sample the paper describes (*t*(156) from at most 142 students and 87 item respondents), pairs *t*(140) = 1.31 with *p* = .008 when that pairing is arithmetically impossible, and attaches three mutually exclusive sample sizes to a single comparison in §4.3. These are not typographical slips distributed at random; they cluster on the load-bearing quantities, and the abstract's discrepancy runs in the direction that flatters the conclusion. The sampling description compounds it: §3.2 asserts a random sample and then, one paragraph later, describes voluntary opt-in with non-respondents excluded. Only one can be true, and the reader is given no way to tell which. That is what drives D1 to block — not a preference for logistic regression over Pearson correlation, which is R1's call and which I have deliberately left alone, but the plain unrecoverability of what was compared to what.

Grant the numbers anyway, for argument's sake, and the inference still does not stand. The exposure variable is counted "during the term," and the outcome is defined by whether the student was still there at the end of it. A student who withdraws in week six cannot accrue the sessions a completer accrues; retention partly manufactures the predictor. This account is strictly more parsimonious than the paper's — it needs no self-regulation, no monitoring, no reflective phase — and it fits every reported result, including the one the paper treats as a puzzle: the essentially null exam comparison. If dashboards were scaffolding regulation, some performance signal should appear; 72.0 against 69.2 is what a selection story predicts, not what a mechanism story predicts. Neither this account, nor reverse causation, nor common-cause selection appears anywhere in the manuscript, including in a Limitations section that finds room for three peripheral caveats while omitting all three fatal ones.

Against that background, §5's language is the central problem rather than an incidental one. "Dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course" are a causal claim and an interventional claim respectively, both stated without hedge, both from a cross-sectional correlation, and both in a paper whose §1 promises the opposite discipline and whose §2 cites Ibarra (2023) as an audit of exactly this failure. §6 then compounds it — "a dependable strategy," "generalizable," "institutions worldwide" — from one course at one university, and recommends *encouraging* engagement when the study observed only spontaneous engagement, a different variable with no established transfer. A manuscript that articulates the field's cardinal error and then commits it is a harder case than one that overclaims naively, because the standard was demonstrably available to the author. That is D3's block.

D2 blocks on a separate axis. §2 tells the reader that dashboards "reliably improve outcomes for lower-achieving students," attributes it to Ferro & Nakamura (2021), and says the claim "underpins much of the equity-oriented rationale" for deployment. The manuscript's own reference list titles that source *When dashboards demotivate: Peer comparison and the lower-achieving student*. I cannot determine from the manuscript which of the two is wrong. I do not need to: as submitted, the equity rationale rests on a characterization the document contradicts on its own pages, and correcting the error in either direction changes what the paper may conclude. Alongside it sits a quieter pattern — Osei (2020) is raised in §2 and never brought into contact with data that could have addressed it, and Wexler & Ojo's *Retention modeling with LMS trace data: A cautionary study* sits in the reference list and is never engaged. The concordant sources are discussed; the cautionary ones are listed.

Two things I have declined to do. D4 scores warn, not block: the retention construct is operationally defined in §3.3, so an adjacent-field reader can recover it even while the Abstract and §6 trade on the institutional sense, and the stronger cross-boundary charge — that a single ungrounded item cannot carry the SRL mechanism — depends on a measurement norm I cannot verify from an external checkable source and is therefore down-rated to advisory and marked `[FIELD-NORM UNVERIFIED]`. The same gate applies to the missing ethics, data-availability, and conflict-of-interest statements: I record their absence as fact and record §3.2's own statement that students were not informed their activity data would be analyzed, but I do not grade either against a venue policy I cannot check, and the adjudication belongs to R3. Neither restraint changes the outcome, which is the point of noting it.

On calibration: I have given the manuscript's fluency no credit. The prose is good, the §2 hedging is sophisticated, and §3.3's admission about the median split is genuinely candid — and none of that bears on whether *t*(140) = 1.31 can yield *p* = .008. Running the opposite-style counterfactual on my own findings: every finding above would read identically if the manuscript were written in rougher prose, because each rests on a proposition checkable against the text and tables rather than on how the text sounds. Finally, the developmental note the severity should not obscure: the question is worth asking, the structure is complete, and claim strength, statistical reporting, citation accuracy, and disclosure are all correctable. The exposure truncation and the mid-term volunteer sample are not — those are properties of how the data came into existence, and no reanalysis of this dataset repairs them. If the authors cannot obtain a sample that includes early withdrawers and an engagement measure not bounded by the outcome window, the honest move is to reframe this as a descriptive institutional case report and drop the retention claim entirely.

## Editorial Decision

Derived mechanically from the contract's `failure_conditions` precedence: F1 fired at severity 90, F2 fired at severity 70, F3 and F0 did not fire. Highest severity wins; F1's action follows.

editorial_decision=reject_or_major_revision

# PART 3 — EDITORIAL SYNTHESIS

# Editorial Decision Package
## Manuscript: *Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment*

---

# Part 0: Sprint-Contract Mechanical Synthesis

> Contract `reviewer/reviewer_full/v1`, baseline v3.6.2, `generated_at=2026-07-25T08:00:00Z`, `panel_size = 5`.
> This section is arithmetic, not interpretive. Steps 1–3 execute the v3.6.2 Sprint Contract Synthesizer Protocol exactly as specified; nothing below it may alter the result.

## Step 1 — Scoring Matrix

Dimensions resolved by `id`. Seats in fixed panel order: EIC, R1 (methodology), R2 (domain), R3 (perspective), DA.

| Dimension | Priority | EIC | R1 | R2 | R3 | DA |
|-----------|----------|-----|----|----|----|----|
| D1 `methodology_rigor` | mandatory | block | block | block | warn | block |
| D2 `domain_accuracy` | mandatory | block | block | block | warn | block |
| D3 `argumentative_coherence` | mandatory | block | block | block | block | block |
| D4 `cross_disciplinary_relevance` | high | warn | warn | block | block | warn |
| D5 `writing_and_structure` | normal | warn | warn | warn | warn | block |

All five Phase 2 outputs are usable: each carries `## Dimension Scores` with one subsection per contract dimension, `## Failure Condition Checks` with one subsection per `failure_conditions[]` entry, `## Review Body`, and exactly one `## Editorial Decision` line. `len(usable_phase2_outputs) == panel_size == 5`; the §6 panel-cardinality invariant holds and no `[PANEL-SHRUNK]` condition arises.

## Step 2 — Per-Condition Evaluation

Panel-relative thresholds for N = 5: `any` → ≥ 1; `majority` → ≥ ⌊5/2⌋ + 1 = 3; `all` → 5.

### F1 — severity 90, quantifier `any`
Expression: `any mandatory dimension scores 'block'` (§9 pattern 1, priority-scoped single-match; recognised).
Predicate per seat, over mandatory {D1, D2, D3}:

| Seat | Mandatory blocks | Predicate |
|------|------------------|-----------|
| EIC | D1, D2, D3 | true |
| R1 | D1, D2, D3 | true |
| R2 | D1, D2, D3 | true |
| R3 | D3 | true |
| DA | D1, D2, D3 | true |

Holds for 5 of 5 ≥ 1. **fired: true.**

### F2 — severity 70, quantifier `majority`
Expression: `two or more mandatory dimensions score 'warn' or worse` (§9 pattern 2, priority-scoped count-based; ordering `pass` < `warn` < `block`; recognised).

| Seat | Mandatory dims at warn-or-worse | Count | Predicate |
|------|--------------------------------|-------|-----------|
| EIC | D1, D2, D3 | 3 | true |
| R1 | D1, D2, D3 | 3 | true |
| R2 | D1, D2, D3 | 3 | true |
| R3 | D1, D2, D3 | 3 | true |
| DA | D1, D2, D3 | 3 | true |

Holds for 5 of 5 ≥ 3 (majority threshold). **fired: true.**

### F3 — severity 60, quantifier `any`
Expression: `any high-priority dimension scores 'block'` (§9 pattern 1, `high-priority` variant; recognised). Sole high-priority dimension is D4.

| Seat | D4 | Predicate |
|------|----|-----------|
| EIC | warn | false |
| R1 | warn | false |
| R2 | block | true |
| R3 | block | true |
| DA | warn | false |

Holds for 2 of 5 ≥ 1. **fired: true.**

### F0 — severity 10, quantifier `all`
Expression: `every mandatory dimension scores 'pass'` (§9 pattern 3, universal over priority; recognised). No seat has any mandatory dimension at `pass`; predicate holds for 0 of 5, below the `all` threshold of 5. **fired: false.**

## Step 3 — Precedence and Decision

Fired: F1 (90), F2 (70), F3 (60). Highest severity governs with no tie to break: **F1**. Its `action` is emitted verbatim below.

fired_conditions: [F1, F2, F3]

editorial_decision=reject_or_major_revision

*Note on the two seat-level score divergences visible in the matrix (D4: R2/R3 `block` against EIC/R1/DA `warn`; D5: DA `block` against four `warn`): under the contract these are neither averaged nor vote-aggregated. F3 already fires on `any` and is recorded above; D5 is `normal` priority and fires no condition either way. Both divergences are carried into Part 1's Points of Disagreement as documented reviewer disagreement, not as an aggregation input.*

*Cross-model blind decision check (Step 4b, #518) was not run: `ARS_CROSS_MODEL` is not set for this invocation and no consent gate was passed. No behavioural change; no `[CROSS-MODEL-CHECKPOINT]` or `[CROSS-MODEL-ERROR]` line is emitted.*

---

# Part 0b: General Synthesis Working Record

## Step 1a — Reviewer Summary Matrix

| Dimension | EIC | R1 (Methodology) | R2 (Domain) | R3 (Perspective) | DA |
|-----------|-----|------------------|-------------|------------------|-----|
| Overall Recommendation | Reject | Reject | Reject (with a path back) | Reject | (no overall-recommendation field; contract decision only) |
| Confidence Score | 4 | 5 | 4 (conditional on independent bibliographic check) | 4 | (none emitted) |
| Key Strengths | Topical fit; critical §2; plain self-criticism; legible structure | Explicit exposure operationalisation; precise retention coding; declared median-split simplification; §4.2 arithmetically reconstructible; §2 states the right standard | Critical review architecture; reflexive proxy critique; operational constructs; honest median-split naming; correct three limitations | Practically-grounded question; §2 names the field's traps; §5.1 admits artifact idiosyncrasy; honest median-split disclosure; Measures section not oversold | §2 genuinely two-sided; §3.3 candid on median split |
| Key Weaknesses | (→ Step 1b) | (→ Step 1b) | (→ Step 1b) | (→ Step 1b) | (→ Step 1b) |
| # of Questions | 9 | 11 | 6 | 8 | (issue list in lieu of questions) |
| # of Minor Issues | 10 | 8 | 6 | 7 | 6 minor + 2 advisory |

Confidence weighting inputs: R1 = 5 (full weight, methodology its primary domain); EIC / R2 / R3 = 4 (full weight). No seat scored ≤ 2, so no finding is reduced or footnoted on confidence grounds. R2's confidence is explicitly conditional on an external bibliographic resolution check; that conditionality is carried onto SC-27 only, not onto R2's other findings.

## Step 1b — Weakness Sub-Claim Inventory

Denominator is the 4 non-DA reviewers throughout. Rows are emitted for positions in {raised, corroborated, disputed}; `not-mentioned` positions are silence and are named in the disposition table rather than listed here. DA positions are tracked separately (Part 1 § Devil's Advocate).

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | confidence |
|--------------|-----------------|-------------|----------|------------------|------------|
| SC-1 | Unreconciled effect size | EIC | raised | W2 "abstract reports *r* = .42; §4.2 reports *r* = .24" | 4 |
| SC-1 | Unreconciled effect size | R1 | raised | Results Presentation #1; "not reconcilable by any rounding account" | 5 |
| SC-1 | Unreconciled effect size | R2 | corroborated | Q2; D1 score basis | 4 |
| SC-1 | Unreconciled effect size | R3 | corroborated | D5 "abstract and body do not currently support each other" | 4 |
| SC-2 | Impossible *df* | EIC | raised | W2 "*t*(156) … unreachable from any sample" | 4 |
| SC-2 | Impossible *df* | R1 | raised | Results Presentation #2 | 5 |
| SC-2 | Impossible *df* | R2 | corroborated | D1 score basis | 4 |
| SC-3 | Impossible *t*/*p* pairing | EIC | raised | W2 "*t*(140) = 1.31 with *p* = .008" | 4 |
| SC-3 | Impossible *t*/*p* pairing | R1 | raised | Results Presentation #3; "*p* ≈ .19 two-tailed" | 5 |
| SC-4 | Table 2 group sizes | EIC | raised | W2 "66 + 61 = 127 … against 'all 142'" | 4 |
| SC-4 | Table 2 group sizes | R1 | raised | Results Presentation #4 | 5 |
| SC-4 | Table 2 group sizes | R2 | raised | D1 score basis | 4 |
| SC-4 | Table 2 group sizes | R3 | raised | D5 "no note on why its group sizes differ" | 4 |
| SC-5 | Undeclared final-exam measure | EIC | raised | Minor Issues #1 | 4 |
| SC-5 | Undeclared final-exam measure | R1 | raised | Results Presentation #6 | 5 |
| SC-5 | Undeclared final-exam measure | R2 | raised | Minor Issues | 4 |
| SC-5 | Undeclared final-exam measure | R3 | raised | D5 score basis | 4 |
| SC-6 | Table 1 / Table 2 mean mismatch | R1 | raised | Results Presentation #5 (70.66 vs 71.3) | 5 |
| SC-7 | Exhibit reporting completeness | EIC | raised | Minor Issues #2–#3 | 4 |
| SC-7 | Exhibit reporting completeness | R1 | raised | Minor Issues; "no *N* per row … no CI" | 5 |
| SC-7 | Exhibit reporting completeness | R2 | raised | Minor Issues "Neither table reports its N" | 4 |
| SC-7 | Exhibit reporting completeness | R3 | raised | D5 "caption is not self-sufficient" | 4 |
| SC-8 | Contradictory sampling designs | EIC | raised | W5 | 4 |
| SC-8 | Contradictory sampling designs | R1 | raised | W4 "These cannot both be true" | 5 |
| SC-8 | Contradictory sampling designs | R2 | raised | Q6 | 4 |
| SC-8 | Contradictory sampling designs | R3 | raised | Minor Issues (flagged for ethics scope) | 4 |
| SC-9 | Mid-term recruitment / survivorship | EIC | raised | W5 "structurally absent" | 4 |
| SC-9 | Mid-term recruitment / survivorship | R1 | raised | W2 "left-truncation on the outcome" | 5 |
| SC-9 | Mid-term recruitment / survivorship | R2 | raised | Argument logic; Q6 | 4 |
| SC-9 | Mid-term recruitment / survivorship | R3 | raised | W3; Review Body ¶4 | 4 |
| SC-10 | Uncensored exposure window | R1 | raised | W3 "part of the association is mechanical" | 5 |
| SC-11 | Reverse causation / common cause | EIC | raised | W1 improvement direction | 4 |
| SC-11 | Reverse causation / common cause | R1 | raised | Methodological Fallacies Detected | 5 |
| SC-11 | Reverse causation / common cause | R2 | raised | W3 "confront the reverse pathway" | 4 |
| SC-11 | Reverse causation / common cause | R3 | raised | D3 first block trigger | 4 |
| SC-12 | Analysis mismatched to outcome type | EIC | raised | Journal Fit; Minor Issues #4 | 4 |
| SC-12 | Analysis mismatched to outcome type | R1 | raised | W5 | 5 |
| SC-12 | Analysis mismatched to outcome type | R2 | corroborated | Terminology precision (defers adjudication to R1) | 4 |
| SC-13 | Retention base rate never reported | R1 | raised | W5 "critically — no reported retention base rate" | 5 |
| SC-14 | Median split of continuous predictor | EIC | raised | Journal Fit | 4 |
| SC-14 | Median split of continuous predictor | R1 | raised | W5 "least efficient use of the data" | 5 |
| SC-14 | Median split of continuous predictor | R2 | corroborated | Strength 4 "the choice is still weak" | 4 |
| SC-15 | Missing analysis apparatus | EIC | raised | Journal Fit "no confidence intervals" | 4 |
| SC-15 | Missing analysis apparatus | R1 | raised | Analysis Methods; Reproducibility | 5 |
| SC-16 | 38.7% item non-response unhandled | EIC | corroborated | Title & Abstract (87 vs 142) | 4 |
| SC-16 | 38.7% item non-response unhandled | R1 | raised | W5; Statistical reporting completeness | 5 |
| SC-17 | Enrolled *N* / participation rate absent | EIC | raised | Minor Issues #9 | 4 |
| SC-17 | Enrolled *N* / participation rate absent | R1 | raised | W4 | 5 |
| SC-18 | Causal verbs in §5 | EIC | raised | W1 | 4 |
| SC-18 | Causal verbs in §5 | R1 | raised | Research Design; D3 basis | 5 |
| SC-18 | Causal verbs in §5 | R2 | raised | W3 | 4 |
| SC-18 | Causal verbs in §5 | R3 | raised | D3 second block trigger | 4 |
| SC-19 | §6 worldwide claim vs §5.1 | EIC | raised | W3 "direct contradiction" | 4 |
| SC-19 | §6 worldwide claim vs §5.1 | R1 | raised | D3 basis; Fallacies | 5 |
| SC-19 | §6 worldwide claim vs §5.1 | R2 | raised | Overclaiming | 4 |
| SC-19 | §6 worldwide claim vs §5.1 | R3 | raised | Q8; D4 first block trigger | 4 |
| SC-20 | Retention construct widens | R1 | raised | Minor Issues; D2 second block trigger | 5 |
| SC-20 | Retention construct widens | R2 | raised | W5 | 4 |
| SC-20 | Retention construct widens | R3 | raised | D2 score basis | 4 |
| SC-21 | Induced ≠ observed engagement | EIC | raised | W3 "a different object" | 4 |
| SC-21 | Induced ≠ observed engagement | R3 | raised | W2; Q4 | 4 |
| SC-22 | §5.1 omits load-bearing threats | R1 | raised | Fallacies "limitations are real but decorative" | 5 |
| SC-22 | §5.1 omits load-bearing threats | R2 | raised | Strength 5; D3 second block trigger | 4 |
| SC-22 | §5.1 omits load-bearing threats | R3 | corroborated | W3 "state in §5.1 that the design cannot detect demotivation" | 4 |
| SC-23 | Contribution unestablished | EIC | raised | Originality; Significance | 4 |
| SC-23 | Contribution unestablished | R2 | raised | Contribution to the Field | 4 |
| SC-24 | Abstract omits design/scope/basis | EIC | raised | Title & Abstract | 4 |
| SC-25 | Ferro & Nakamura inversion | EIC | raised | W4 | 4 |
| SC-25 | Ferro & Nakamura inversion | R1 | corroborated | "outside my remit … I flag it because it is checkable" | 5 |
| SC-25 | Ferro & Nakamura inversion | R2 | raised | W1 | 4 |
| SC-25 | Ferro & Nakamura inversion | R3 | corroborated | Reading Recommendations (defers scoring to R2) | 4 |
| SC-26 | Nine of fifteen references uncited | EIC | raised | W4; Minor Issues #8 | 4 |
| SC-26 | Nine of fifteen references uncited | R2 | raised | W2 | 4 |
| SC-26 | Nine of fifteen references uncited | R3 | corroborated | Reading Recommendations "use-what-you-cited" | 4 |
| SC-27 | All DOIs in reserved-example prefix | EIC | raised | W4; Minor Issues #8 | 4 |
| SC-27 | All DOIs in reserved-example prefix | R2 | raised | W2 (marked as requiring independent verification) | 4 |
| SC-28 | Persistence literature/theory absent | EIC | raised | D4 warn basis "retention framing is decorative" | 4 |
| SC-28 | Persistence literature/theory absent | R1 | raised | D4 warn basis | 5 |
| SC-28 | Persistence literature/theory absent | R2 | raised | Literature Review Coverage; D4 block basis | 4 |
| SC-29 | SRL unattributed / substitution / uncited practice claim | EIC | corroborated | Minor Issues #7; Originality | 4 |
| SC-29 | SRL unattributed / substitution / uncited practice claim | R1 | corroborated | Data Collection; Minor Issues | 5 |
| SC-29 | SRL unattributed / substitution / uncited practice claim | R2 | raised | W4 | 4 |
| SC-30 | Single-item instrument as severity-bearing defect | EIC | raised | Originality "too thin to constitute a measurement contribution" | 4 |
| SC-30 | Single-item instrument as severity-bearing defect | R1 | raised | Data Collection "no reliability … no validity argument" | 5 |
| SC-30 | Single-item instrument as severity-bearing defect | R2 | disputed | W4 `[FIELD-NORM UNVERIFIED]`; "decline to attach a severity to the instrument choice as such" | 4 |
| SC-31 | Demotivation account never tested | EIC | raised | W3; Q9 | 4 |
| SC-31 | Demotivation account never tested | R2 | raised | Argument logic; Q4 | 4 |
| SC-31 | Demotivation account never tested | R3 | raised | W3 | 4 |
| SC-32 | No ethics-approval record | EIC | raised | W6 | 4 |
| SC-32 | No ethics-approval record | R1 | raised | Reproducibility (scoped to reporting gap) | 5 |
| SC-32 | No ethics-approval record | R3 | raised | W1; Q1 | 4 |
| SC-33 | Undisclosed secondary use; no de-identification/linkage account | EIC | raised | W6 | 4 |
| SC-33 | Undisclosed secondary use; no de-identification/linkage account | R1 | corroborated | Reproducibility (defers substance to R3) | 5 |
| SC-33 | Undisclosed secondary use; no de-identification/linkage account | R3 | raised | W1; Broader Implications; Q2–Q3 | 4 |
| SC-34 | No DAS / funding / COI / code / software | EIC | raised | W6 | 4 |
| SC-34 | No DAS / funding / COI / code / software | R1 | raised | Reproducibility; Minor Issues | 5 |
| SC-34 | No DAS / funding / COI / code / software | R3 | raised | Minor Issues #1–#2 | 4 |
| SC-35 | Students absent as stakeholders; access inequality unexamined | R3 | raised | W4; Q6; D4 second block trigger | 4 |
| SC-36 | Dashboard artifact unidentifiable | EIC | raised | Minor Issues #6 | 4 |
| SC-36 | Dashboard artifact unidentifiable | R1 | raised | Data Collection | 5 |
| SC-36 | Dashboard artifact unidentifiable | R2 | raised | Minor Issues | 4 |
| SC-36 | Dashboard artifact unidentifiable | R3 | raised | W5; Q7 | 4 |
| SC-37 | Sessionization rule inherited from vendor default | EIC | raised | Minor Issues #5 | 4 |
| SC-37 | Sessionization rule inherited from vendor default | R1 | raised | Data Collection | 5 |
| SC-37 | Sessionization rule inherited from vendor default | R2 | raised | Minor Issues | 4 |
| SC-37 | Sessionization rule inherited from vendor default | R3 | raised | W5; Q7 | 4 |
| SC-38 | Institution named but not characterised | EIC | raised | D4 warn basis "institutional context is thin" | 4 |
| SC-38 | Institution named but not characterised | R2 | raised | Factual accuracy | 4 |
| SC-38 | Institution named but not characterised | R3 | raised | Minor Issues #5 | 4 |

**Decomposition discipline check.** Every sub-claim above traces to a claim a named reviewer actually made; no sub-claim was authored by this synthesis. Two bundles were split rather than aggregated, because their sub-claims carry different reviewer sets and different dispositions: the bibliography bundle splits into SC-26 (uncited entries) and SC-27 (DOI prefix), and the measurement bundle splits into SC-29 (attribution / substitution / uncited practice claim — no field norm required) and SC-30 (the instrument choice itself — norm-dependent, and the one genuine conflict on the panel).

## Step 1c — Surface-Form Parity Check (#216)

Run before any weighting. Three places where phrasing could have driven weight, and what was done:

- **R3's register is narrative and non-statistical relative to R1's.** SC-35 (stakeholders, device and connectivity access, the zero-session students in Table 1) arrives with no statistical apparatus at all. Opposite-style counterfactual: rewritten as "engagement count is confounded with access covariates that were not measured," the substance is identical and the weight would not change. Weight held on substance; SC-35 is a full-weight single-reviewer finding, not a soft one.
- **DA's C4 arrives in maximally precise arithmetic form.** Precision was not treated as corroboration. C4 gains weight only because R1 independently derived the same arithmetic from the same paper text, and EIC and R2 independently observed subsets of it — paper evidence, not phrasing.
- **R2's and DA's `[FIELD-NORM UNVERIFIED]` markers are epistemic restraint, not vagueness.** Under Special Situation 4 a "vague" criticism may be down-weighted; that rule was not applied here, because these markers state precisely what is claimed and precisely what is withheld. The sub-claims they carry (SC-29) are fully evaluable and are weighted at full strength.

No sub-claim was marked unevaluable. Authorship was not a weighting input at any point.

## Step 2 — Consensus Dispositions

Precedence applied top-down: `conflict ≥ 1` → SPLIT first; otherwise by `agree` count over 4.

| ID | Short label | agree | conflict | silent | Disposition |
|----|-------------|-------|----------|--------|-------------|
| SC-1 | Abstract *r* = .42 vs §4.2 *r* = .24 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-4 | Table 2 sums to 127 against "all 142" | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-5 | Final-exam measure undefined in Methods | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-7 | Exhibits omit *N*, test statistic, *p*, ES, CI | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-8 | Two incompatible sampling designs in §3.2 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-9 | Mid-term volunteer recruitment / survivorship | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-11 | Reverse causation and common cause unconfronted | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-18 | Causal verbs in §5 unlicensed by the design | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-19 | §6 worldwide generalisability contradicts §5.1 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-25 | Ferro & Nakamura (2021) characterisation inverted | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-36 | Dashboard artifact unidentifiable | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-37 | 30-minute sessionization inherited as a construct | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-2 | *t*(156) unreachable from any stated sample | 3 | 0 | R3 | **[CONSENSUS-3]** |
| SC-12 | Point-biserial correlation for a dichotomous outcome | 3 | 0 | R3 | **[CONSENSUS-3]** |
| SC-14 | Median split of a continuous predictor | 3 | 0 | R3 | **[CONSENSUS-3]** |
| SC-20 | Retention widens from course to programme | 3 | 0 | EIC | **[CONSENSUS-3]** |
| SC-22 | §5.1 omits the load-bearing threats | 3 | 0 | EIC | **[CONSENSUS-3]** |
| SC-26 | Nine of fifteen references never cited | 3 | 0 | R1 | **[CONSENSUS-3]** |
| SC-28 | Persistence literature and theory absent from body | 3 | 0 | R3 | **[CONSENSUS-3]** |
| SC-29 | SRL unattributed; substitution and practice claim uncited | 3 | 0 | R3 | **[CONSENSUS-3]** |
| SC-31 | Demotivation account never tested against the data | 3 | 0 | R1 | **[CONSENSUS-3]** |
| SC-32 | No ethics-approval record | 3 | 0 | R2 | **[CONSENSUS-3]** |
| SC-33 | Undisclosed secondary use; no linkage/de-identification account | 3 | 0 | R2 | **[CONSENSUS-3]** |
| SC-34 | No data-availability, funding, COI, code, software | 3 | 0 | R2 | **[CONSENSUS-3]** |
| SC-38 | Institution named but not characterised | 3 | 0 | R1 | **[CONSENSUS-3]** |
| SC-3 | *t*(140) = 1.31 paired with *p* = .008 | 2 | 0 | R2, R3 | corroborated finding |
| SC-15 | No power analysis, assumption checks, or corrections | 2 | 0 | R2, R3 | corroborated finding |
| SC-16 | 38.7% item non-response unhandled | 2 | 0 | R2, R3 | corroborated finding |
| SC-17 | Enrolled *N* and participation rate absent | 2 | 0 | R2, R3 | corroborated finding |
| SC-21 | §6 recommends induced engagement, never observed | 2 | 0 | R1, R2 | corroborated finding |
| SC-23 | Incremental contribution unestablished | 2 | 0 | R1, R3 | corroborated finding |
| SC-27 | All fifteen DOIs in the reserved-example prefix | 2 | 0 | R1, R3 | corroborated finding |
| SC-6 | Table 2 weighted mean 70.66 ≠ Table 1's 71.3 | 1 | 0 | EIC, R2, R3 | single-reviewer finding (R1, conf 5) |
| SC-10 | Exposure window uncensored at withdrawal | 1 | 0 | EIC, R2, R3 | single-reviewer finding (R1, conf 5) + DA-CRITICAL C1 |
| SC-13 | Retention base rate / 2×2 never reported | 1 | 0 | EIC, R2, R3 | single-reviewer finding (R1, conf 5) |
| SC-24 | Abstract omits design descriptor, scope, 87-basis | 1 | 0 | R1, R2, R3 | single-reviewer finding (EIC, conf 4) |
| SC-35 | Students absent as stakeholders; access unexamined | 1 | 0 | EIC, R1, R2 | single-reviewer finding (R3, conf 4) |
| SC-30 | Single-item instrument as a severity-bearing defect | 2 | 1 (R2) | R3 | **[SPLIT]** → arbitration |

Silence is recorded as silence throughout. Seven of the eleven single-reviewer or corroborated dispositions above arise because the seat that owned the question deliberately deferred to another seat (R1 → R2 on citation fidelity; R2 and DA → R1 on statistics; R3 → R1 on design and R2 on coverage; DA → R3 on ethics). Those deferrals were not promoted into agreement, and they were not read as dissent.

---

# Part 1: Editorial Decision Letter

## Manuscript Information

- **Title**: *Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment*
- **Manuscript ID**: not supplied
- **Submission Date**: not supplied
- **Decision Date**: 2026-07-25
- **Review Round**: 1
- **Journal**: *Journal of Learning Analytics*
- **Panel**: 5 reviewers (Editor-in-Chief, Reviewer 1 Methodology, Reviewer 2 Domain, Reviewer 3 Perspective, Devil's Advocate)

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — This is a `reviewer_full` letter, so this block is mandatory and must carry exactly one of the three published statements (cross-model slot active / single-family disclosure / dispatch-failure fallback). The dispatching layer did not supply a provenance stamp with this invocation, and the statement may not be inferred. **The letter must not ship until the dispatching layer fills this block.** No cross-family aggregate was computed and none is permitted; cross-family splits, if any exist, are visible by inspection in the Part 0 panel matrix.

---

## Decision

### Reject

**Subtype**: Fundamental Flaw — Resubmit Encouraged (a resubmission would be assessed as a new submission, not as a revision of this manuscript).

The sprint contract's governing condition F1 carries the action `reject_or_major_revision`. Within that band the decision resolves to Reject rather than Major Revision, on the following basis: all four non-DA reviewers independently recommended Reject; two defects (SC-9 mid-term recruitment, SC-10 uncensored exposure) are properties of how the data came into existence and are not reachable by any reanalysis of this dataset; and the ethics-governance gap (SC-32, SC-33) cannot be cured retrospectively by rewriting. This is a resolution *within* the fired condition's action, not a softening of it.

---

## Top Blocking Issues (ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | The reported statistical record is mutually inconsistent, so no reported quantity can currently be treated as the study's finding | EIC, R1, R2, R3, DA | Abstract *r* = .42 vs §4.2 *r* = .24; §4.3 *t*(156) from ≤ 142; §4.3 *t*(140) = 1.31 with *p* = .008; Table 2 66 + 61 = 127 against "all 142 students" | R1 |
| 2 | Causal and interventional claims from an unadjusted observational association, contradicting the manuscript's own §1 commitment and §5.1 concession | EIC, R1, R2, R3, DA | §5 "dashboard engagement improved course retention … therefore raises the probability"; §6 "a dependable strategy … generalizable … institutions worldwide" against §5.1 "differs from those deployed elsewhere" | R4, R5 |
| 3 | Two design defects no reanalysis of these data can reach: mid-term volunteer recruitment left-truncates the sample on the outcome, and exposure accrual is not censored at withdrawal | EIC, R1, R2, R3, DA | §3.2 recruitment "midway through the term," non-respondents excluded; §3.3 sessions counted "during the term" against retention defined by sitting the final | R3 |

A fourth issue of blocking severity — the ethics-governance gap (§3.2: "students were not informed that their dashboard activity data would be analyzed for this study," with no approval record, waiver justification, de-identification account, or declarations anywhere) — is excluded from this table only by its three-row cap. It is roadmap item **R2**, it is a co-driver of the decision, and unlike ranks 1–2 it cannot be cured by rewriting.

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence |
|----------|------|---------------|------------|
| EIC | Editor-in-Chief, *Journal of Learning Analytics*; learning analytics translation to institutional practice | Reject | 4 |
| Reviewer 1 | Quantitative methodologist; dichotomous educational outcomes and selection bias in edtech observational studies | Reject | 5 |
| Reviewer 2 | Senior learning-analytics researcher; student-facing dashboards and self-regulated learning | Reject (with a path back) | 4 |
| Reviewer 3 | Research-ethics and educational-data-governance specialist; IRB panel chair, institutional analytics adviser | Reject | 4 |
| Devil's Advocate | Adversarial challenge seat | (no overall-recommendation field emitted) | (none emitted) |

---

## Consensus Analysis

### Points of Agreement (Consensus)

**[CONSENSUS-4]** — all four non-DA reviewers agree on the sub-claim and on the required action:

1. **[SC-1] The primary effect size is reported at two irreconcilable magnitudes.** EIC: "an unreconciled effect size spanning abstract and results is a threshold matter." R1: "*r* = .42 at *N* = 142 would yield *p* < .001 … not reconcilable … by any rounding or transcription account." R2 makes the interpretive consequence explicit: whether this finding is notable or unremarkable within the dashboard literature "turns entirely on which figure is real." R3 scores only the reader-facing consequence and defers the value determination to R1.
2. **[SC-4] Table 2's group sizes (66 + 61 = 127) contradict the same paragraph's "all 142 students."** R1 adds that *t*(140) independently implies *N* = 142, giving three mutually exclusive sample sizes for one comparison.
3. **[SC-5] Table 1 reports a final-exam variable that §3.3 Measures never defines**, which then carries an inferential test and a table of its own.
4. **[SC-7] Neither exhibit is self-sufficient**: no per-row *N* despite rows drawn from different subsamples, no test statistic, *p*, effect size, or interval in Table 2, and inconsistent decimal precision.
5. **[SC-8] §3.2 states two incompatible sampling designs one paragraph apart** — a random sample of the enrolment, and a voluntary response to an LMS announcement with non-respondents excluded.
6. **[SC-9] Recruitment occurred mid-term, so students who disengaged or withdrew beforehand could never enter a study whose outcome is retention.** R1 names the mechanism: left-truncation on the outcome.
7. **[SC-11] Reverse causation and common-cause selection are never confronted.** Both principal associations are concurrent and unadjusted; §5 nonetheless reads the perceived-control comparison directionally.
8. **[SC-18] §5 asserts causation** ("dashboard engagement improved course retention"; "therefore raises the probability that a student completes the course") from a design §3.1 calls observational and cross-sectional, with no adjustment, matching, or identification argument anywhere.
9. **[SC-19] §6 asserts worldwide generalisability and a "dependable strategy"** over §5.1's own concession that the interface "differs from those deployed elsewhere." The two sections contradict each other directly.
10. **[SC-25] §2 attributes to Ferro & Nakamura (2021) a finding the manuscript's own reference list titles in the opposite direction** (*When dashboards demotivate: Peer comparison and the lower-achieving student*), and §2 states that this position "underpins much of the equity-oriented rationale for institutional dashboard deployment." R1 and R3 both flagged this as checkable and deferred the substantive determination to R2, who owns it; R2 confirms it as an internal contradiction between body and bibliography.
11. **[SC-36] The dashboard artifact is described in one clause** — no platform, version, screenshot, or account of what a student saw — while it is the object the exposure variable measures and the object §6 recommends scaling.
12. **[SC-37] The 30-minute sessionization rule is adopted as "the platform's default"**: a vendor artifact used as a construct boundary with no justification and no sensitivity analysis.

**[CONSENSUS-3]** — three agree, the fourth silent (silent reviewer named):

13. **[SC-2] §4.3's *t*(156) is unreachable** from the 142-student analytic sample or the 87 item respondents (EIC, R1, R2; **R3 silent**).
14. **[SC-12] A point-biserial correlation, never named as such, is used for a dichotomous outcome** with no covariate adjustment, logistic or hazard model, or interval (EIC, R1, R2; **R3 silent** — R3 explicitly assigns this to R1).
15. **[SC-14] The median split discards variance the study already possesses** (EIC, R1, R2; **R3 silent**).
16. **[SC-20] "Retention" widens from the course-level completion defined in §3.3** to "retention across programs and disciplines" in §6 (R1, R2, R3; **EIC silent**).
17. **[SC-22] §5.1's limitations omit every threat that could defeat the conclusion** — selection, confounding, reverse causation, exposure truncation (R1, R2, R3; **EIC silent**).
18. **[SC-26] Nine of fifteen reference entries are never cited in the body**, including Wexler & Ojo (2020), the listed source closest to this design (EIC, R2, R3; **R1 silent**).
19. **[SC-28] No work from the retention or persistence tradition is cited anywhere in the body**, though retention is the outcome, the title, and the conclusion's prescription (EIC, R1, R2; **R3 silent**).
20. **[SC-29] The forethought/performance/reflection model is attributed to no originator, perceived control is substituted for self-regulation without argument, and the "single-item ratings are common in dashboard studies" claim is uncited** (EIC, R1, R2; **R3 silent**).
21. **[SC-31] The demotivation account (Osei, 2020) and the peer-comparison band are raised in §2 and §3.1 and never brought into contact with the data** (EIC, R2, R3; **R1 silent**).
22. **[SC-32] No ethics-approval record appears anywhere** (EIC, R1, R3; **R2 silent**).
23. **[SC-33] §3.2 states that students were not informed their dashboard activity would be analysed**, consent covered the survey only, logs were linked to survey responses and outcomes at the individual level, and no de-identification or linkage account is given (EIC, R1, R3; **R2 silent**).
24. **[SC-34] No data-availability, funding, or conflict-of-interest statement; no analysis code; software unnamed** (EIC, R1, R3; **R2 silent**).
25. **[SC-38] The institution is named but not characterised** by type, system, or sector, so transferability cannot be judged (EIC, R2, R3; **R1 silent**).

**Corroborated findings** (two reviewers, no conflict — action-bearing, below the consensus label): SC-3 (*t*(140) = 1.31 with *p* = .008, arithmetically impossible and contradicting the same paragraph's prose — EIC, R1); SC-15 (no power analysis, no assumption checks, no correction across three tests, no effect sizes for either *t*-test — EIC, R1); SC-16 (38.7% item non-response handled by exclusion with no responder comparison — EIC, R1); SC-17 (enrolled population given only as "several hundred," so no participation rate is computable — EIC, R1); SC-21 (§6 recommends *encouraging* engagement, while the study observed only spontaneous opening — EIC, R3); SC-23 (the incremental contribution is never articulated, and §2's own account of the field argues against it — EIC, R2); SC-27 (all fifteen DOIs sit in the `10.5555` reserved-example prefix — EIC, R2, the latter marking the inference as requiring independent verification).

**Single-reviewer findings** (weighted by confidence, not by count): SC-6, SC-10, SC-13 (R1, confidence 5 each — Table 2's weighted exam mean does not reconcile with Table 1's; the exposure window is not censored at withdrawal; the retention base rate is never reported); SC-24 (EIC, confidence 4 — the abstract omits the design descriptor, the single-course scope, and the 87-respondent basis); SC-35 (R3, confidence 4 — students appear only as data sources, differential device and connectivity access is never considered, and Table 1's zero-session students are never examined).

### Points of Disagreement

**Disagreement 1 — [SC-30] Severity of the single-item perceived-control measure**

- **EIC and R1 view**: a substantive construct-validity defect. R1: "No reliability evidence, no validity argument, no distributional check beyond a mean and SD." EIC: "a single global item on perceived control is too thin to constitute a measurement contribution."
- **R2 view**: the gap is real and load-bearing for §5's explanatory account, but severity cannot be attached to the instrument choice as such, because doing so would rest on a claim about what educational-psychology measurement practice *requires* that R2 could not ground in a checkable external source. Marked `[FIELD-NORM UNVERIFIED]`; R2 scores the attribution, substitution, and uncited-practice components (SC-29) at full severity and withholds only on the instrument.
- **R3**: silent (not-mentioned).
- **Disagreement type**: severity disagreement.
- **Editor's Resolution**: **The reporting-adequacy claim stands at full weight; the field-norm claim does not, and is not carried into the roadmap as a requirement.** R2's restraint is correct about what an unverifiable field norm can support, and this synthesis does not import one. But R1's objection does not depend on any norm: a measure reported with no reliability estimate, no validity argument, and no distributional check is under-reported on its own terms, whatever a given field conventionally accepts. Under arbitration principle 3b.2 (expertise first), measurement adequacy sits with R1, whose confidence on this point is 5. The author is therefore required to supply psychometric evidence for the item **or** reframe the construct to what a single global control rating can carry — not to adopt any particular instrument. Roadmap item **S1**; conservative principle applies, so a response is required either way. Recorded per surface-form parity: R2's `[FIELD-NORM UNVERIFIED]` marker was read as precision about the limit of its own warrant, not as vagueness, and carried no weight penalty.

**Disagreement 2 — Panel divergence on D4 (`cross_disciplinary_relevance`)**

- **R2 and R3 view**: `block`. R2's warrant is substantiation absence on the crossing claim itself — the paper's outcome and its entire prescription cross into higher education, and zero of the six in-text citations come from the retention or persistence tradition. R3's warrant is that §6 addresses recommendations to practice while students, the population most affected, appear only as data sources, with no treatment of unequal digital access or data governance.
- **EIC, R1, and DA view**: `warn`. All three set a narrower block trigger — genuine inaccessibility of the central argument to an adjacent-field reader, or an explicit bridging claim with no substantiation anywhere — and each judged that bar unmet, because §3.3 does define retention operationally and the analytics apparatus is legible to a higher-education reader.
- **Disagreement type**: perspective difference (each seat applied its own pre-committed Phase 1 trigger).
- **Editor's Resolution**: **not aggregated, and both block-side findings are carried into the roadmap.** The contract forbids averaging or vote-aggregating scores within a dimension, so the divergence is displayed in the Part 0 matrix rather than resolved into a single value; F3 fires on `any` and is recorded as fired. The divergence does not change the outcome, since F1 governs at severity 90. On substance, the two sides are not in conflict about the paper: the warn-side reviewers judged a narrower trigger unmet, and none of them disputes R2's or R3's underlying observation. D4 is R3's primary assignment and the literature-coverage half is R2's; both findings enter the roadmap (SC-28 at S1, SC-35 at S4).

**Disagreement 3 — DA's field-norm down-rating of the ethics gap against R3's block-level finding**

- **DA view**: records the absence of ethics-approval, data-availability, funding, and COI statements as fact, and records §3.2's own statement that students were not informed — but down-rates both to advisory (`A2`, `[FIELD-NORM UNVERIFIED]`) rather than grading them against a venue policy DA could not verify, explicitly assigning adjudication to R3.
- **R3 view**: submission-blocking at every plausible venue, and the consent gap for the log component is not recoverable retrospectively.
- **Editor's Resolution**: **no conflict to arbitrate — DA deferred, it did not dissent.** R3 owns this determination and holds it at confidence 4; EIC and R1 independently corroborate the reporting-gap half (SC-32, SC-34) at confidence 4 and 5. DA's restraint is noted and endorsed as correct practice for a seat outside its warrant. The finding stands at full severity as roadmap item **R2**.

### Devil's Advocate Findings

DA is not one of the four counted reviewers; its findings are tracked independently and each must be answered by the author regardless of corroboration.

| DA issue | Argument | Corroborated by | Editor's assessment | Required author response |
|----------|----------|-----------------|---------------------|--------------------------|
| **C1** Exposure-window truncation | Session counts accrue "during the term" while non-retention terminates the accrual window, so retention partly *determines* the predictor. A rival account requiring no dashboard effect fits all three reported results, including the near-null exam comparison | R1 (SC-10, independently, confidence 5) | **Valid and load-bearing.** Reached independently from the methodology seat by a different route. Neither the manuscript's Discussion nor §5.1 raises it | Address directly, or report a landmark analysis with exposure fixed to a window closing before any withdrawal |
| **C2** Unhedged causal and interventional claims | §5 and §6 assert cause and prescribe intervention from a cross-sectional correlation, in a paper whose §1 promises the opposite and whose §2 cites an audit of exactly this failure | All four (SC-18, SC-19) — CONSENSUS-4 | **Valid.** The panel is unanimous | Retract per roadmap R4/R5 |
| **C3** Two effect sizes for one association | Abstract *r* = .42 vs §4.2 *r* = .24; threefold difference in shared variance, with the larger figure in the section most readers read alone | All four (SC-1) — CONSENSUS-4 | **Valid.** The panel is unanimous | Reconcile per roadmap R1 |
| **C4** Impossible secondary statistics | *t*(156) unreachable; *t*(140) = 1.31 with *p* = .008 impossible; three mutually exclusive sample sizes for one comparison; prose and reported *p* contradict each other | R1 (all parts, confidence 5); EIC (SC-2, SC-3, SC-4); R2 (SC-2, SC-4) | **Valid.** Credited on R1's independent derivation from the paper text, not on the precision of DA's phrasing | Answer per roadmap R1 |
| **C5** Ferro & Nakamura foundation collapse | §2's characterisation and the manuscript's own reference-list title point in opposite directions; correcting the error in either direction removes the equity rationale | All four (SC-25) — CONSENSUS-4 | **Valid.** DA correctly grounds severity in an internal contradiction rather than an external claim about the source | Answer per roadmap R6 |
| **C6** Two sampling designs plus survivorship | §3.2 asserts a random sample and, one paragraph later, voluntary opt-in with exclusions; mid-term recruitment conditions the sample on surviving to the announcement | All four (SC-8, SC-9) — CONSENSUS-4 | **Valid.** The panel is unanimous | Answer per roadmap R3 |

**DA frame-lock finding (not CRITICAL, recorded for response).** DA identifies an unexamined premise beneath all eight of its challenge dimensions: that retention is unambiguously good for the student, so that the institution's interest and the student's interest are treated as identical. R3 reaches the same premise independently from the governance seat ("for an individual student a well-timed withdrawal from a gateway statistics course can be the correct decision"). No other reviewer raises it. The editor's assessment is that this is a legitimate framing observation rather than a defect in the analysis, and the author should state once, in §5 or §6, that the two interests are not identical here. Roadmap item **S4**.

**DA advisory items down-rated under its own field-norm gate** (`A1` single-item construct validity, `A2` missing ethics and declaration statements) are not treated as DA findings of reduced severity; both are carried at full severity through the corresponding reviewer sub-claims (SC-30 via arbitration, SC-32/33/34 via CONSENSUS-3).

---

## Decision Rationale

The decision rests on the conjunction of three independent failures, not on any single defect.

First, the manuscript does not currently state what it found. Six numerical contradictions are checkable from the text alone, and they cluster on the load-bearing quantities: an effect size reported at two magnitudes with the larger one in the abstract, a degrees-of-freedom value unreachable from any described sample, an arithmetically impossible *t*/*p* pairing that also contradicts its own paragraph's prose, and three mutually exclusive sample sizes for one comparison. Every downstream judgment — whether the effect is notable, whether it supports §5's marginal-benefit reading, whether it supports §6 at all — turns on values the panel cannot recover. R1 (confidence 5) establishes this on the arithmetic; EIC, R2, R3, and DA reach it independently.

Second, the paper states the field's cardinal inferential standard and then breaches it. §1 promises to separate pattern from causal story and §2 cites an audit of the field for failing to; §5 asserts that engagement "improved" retention and §6 calls dashboards a "dependable" and "generalizable" strategy for institutions "worldwide," over §5.1's own concession that the interface differs from those deployed elsewhere. All five seats scored D3 `block`. Because the standard is demonstrably known to the author, softened verbs would not reach the underlying problem.

Third, and decisive for Reject over Major Revision: two defects lie outside the reach of reanalysis. Mid-term volunteer recruitment structurally excludes the students most informative about non-retention, and uncensored exposure accrual makes part of the association arithmetic rather than behavioural. Both act in the reported direction. Separately, the consent gap for the behavioural-log component (§3.2) cannot be cured retrospectively by rewriting.

The topic is worth studying and the panel says so. A resubmission built on prospective, landmark-censored exposure over the full enrolled cohort, a documented ethics basis, verified references, and claims held to the design's ceiling would be welcome — as a new submission.

---

# Part 2: Revision Roadmap

> Requirements for a resubmission, which will be assessed as a new submission rather than as a revision of this manuscript. The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to.

## Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Source | Severity | Section | Estimated Effort |
|---|---------------|--------------|--------|----------|---------|------------------|
| R1 | Re-derive every reported statistic from the analysis file; state which value the conclusions rest on; supply per-test *N* and the analysis script | SC-1, SC-2, SC-3, SC-4, SC-5, SC-6, SC-7, SC-16 | EIC, R1, R2, R3, DA | Critical | Abstract, §4, Tables 1–2 | 3–5 days |
| R2 | Document the ethics governance of the behavioural-log component (approving body, protocol identifier, waiver criteria, institution-wide research-use notice) or withdraw that analysis; describe linkage and de-identification; add ethics, data-availability, funding, and COI statements | SC-32, SC-33, SC-34 | EIC, R1, R3 | Critical | §3.2, front/back matter | 2–6 weeks (institution-dependent; not author-controlled) |
| R3 | Resolve the sampling account and address the two design defects reanalysis cannot reach: state the actual recruitment procedure, the enrolled *N*, and the participation rate; report the enrolled-vs-analysed comparison; censor exposure at a common landmark preceding any withdrawal — or withdraw the retention question with the present data | SC-8, SC-9, SC-10, SC-17 | EIC, R1, R2, R3, DA | Critical | §3.2, §3.3, §4 | New data collection (one term) if the retention question is retained |
| R4 | Retract every causal and interventional verb in the Abstract, §5, and §6 to associational language; state the reverse and common-cause readings as at least equally consistent with the data; rewrite §5.1 to carry selection, confounding, reverse causation, and exposure truncation | SC-11, SC-18, SC-22 | EIC, R1, R2, R3, DA | Critical | Abstract, §5, §5.1, §6 | 3–5 days |
| R5 | Rewrite §6 to the scope the design supports — one course, one term, one interface; restore the course-level retention construct throughout; withdraw the institutional recommendation and the induced-engagement recommendation, or downgrade both to hypotheses for interventional test | SC-19, SC-20, SC-21 | EIC, R1, R2, R3, DA | Critical | §6, Abstract, §1 | 2–3 days |
| R6 | Correct the Ferro & Nakamura (2021) characterisation and rebuild or withdraw the equity rationale on a source that argues it; independently resolve all fifteen references and the `10.5555` DOI prefix; cite or remove the nine unused entries | SC-25, SC-26, SC-27 | EIC, R1, R2, R3, DA | Critical | §2, References | 1 week |
| R7 | Refit the analysis to the outcome type: logistic (or discrete-time hazard) regression of retention on continuous, landmark-censored engagement with prior achievement, prior LMS activity, and credit load as covariates; report the retention base rate and 2×2 cross-tabulation, odds ratio with 95% CI, and marginal risk difference; drop the median split; report assumption checks, power, and treatment of the three tests | SC-12, SC-13, SC-14, SC-15 | EIC, R1, R2 | Critical | §3.4, §4 | 1–2 weeks |

### Required Item Details

**R1: Reconcile the statistical record**
- **Problem**: Six mutually incompatible reported values, spanning abstract, results text, and both tables.
- **Source**: R1 Results Presentation #1–#6 (confidence 5); EIC W2; R2 D1 basis; R3 D5 basis; DA C3, C4.
- **Requirement**: Re-derive every statistic from the analysis file rather than patching the prose. Supply a table mapping each reported test to the exact subsample it used, with *N* per row in both exhibits. State explicitly which correlation the conclusions rest on and report it with a confidence interval. Define the final-exam measure in §3.3 Measures, and explain how students coded as not retained — who by definition did not sit the final — were handled in the Table 2 comparison.
- **Acceptance criteria**: An independent analyst reproduces every reported value from the supplied script and data description, and no two reported figures conflict.

**R2: Document the ethics basis or withdraw the log analysis**
- **Problem**: §3.2 states students were not informed their dashboard activity would be analysed; consent covered the survey only; logs were linked to survey responses and retention outcomes at the individual level. No approval record, waiver justification, de-identification account, or declarations appear.
- **Source**: R3 W1 and Q1–Q3 (owning seat, confidence 4); EIC W6; R1 Reproducibility (confidence 5, scoped to the reporting gap).
- **Requirement**: Name the approving body and protocol identifier and state the waiver criteria applied; or, if an institution-wide research-use notice was in effect during the study term, quote it. If no review covered the log component, say so plainly and bring the matter to the ethics body before resubmission. Describe how logs and survey responses were linked, who held the key, and what de-identification was applied. Add ethics, data-availability, funding, and conflict-of-interest statements — the last is material given that the study evaluates a platform feature.
- **Acceptance criteria**: A reader can determine the legal and institutional basis on which the behavioural data were analysed, and all four declarations are present.

**R3: Resolve sampling and the two irrecoverable design defects**
- **Problem**: §3.2 asserts a random sample and, one paragraph later, voluntary opt-in with non-respondents excluded. The surviving half left-truncates the sample on the outcome. Separately, exposure accrues across a window that terminates at withdrawal for non-retained students.
- **Source**: R1 W2 and W3 (confidence 5); EIC W5; R2 Q6; R3 W3; DA C1 and C6.
- **Requirement**: State what actually happened, give the exact enrolled *N* and participation rate, and compare respondents to non-respondents on any available administrative variable. Study retention on the full enrolled cohort with exposure measured prospectively from week 1 and survey participation treated as an auxiliary variable, not as the sampling frame. Censor exposure at a landmark preceding any withdrawal and report the landmark analysis as primary. If neither is possible with these data, withdraw the retention question and reframe the work as a descriptive institutional case report.
- **Acceptance criteria**: The analytic sample is not conditioned on surviving to a recruitment window, and no portion of the reported association is entailed by how the exposure window and the outcome are jointly constructed.

**R4: Hold the claims to the design's ceiling**
- **Problem**: §1 commits to distinguishing pattern from cause; §5 asserts cause and then, three paragraphs later, reverts to marginal association; §5.1's limitations constrain nothing asserted in §5 or §6.
- **Source**: CONSENSUS-4 (SC-18, SC-11); CONSENSUS-3 (SC-22, EIC silent); DA C2.
- **Requirement**: Remove every causal and interventional verb from the Abstract, §5, and §6. State the reverse pathway and the common-cause pathway as at least equally consistent with the data. Rewrite §5.1 to name selection, confounding, reverse causation, and exposure truncation, and to say what each would do to the conclusion.
- **Acceptance criteria**: No sentence in the manuscript claims more than an adjusted association, and the limitations section constrains the claims the manuscript actually makes.

**R5: Rewrite §6 to what was studied**
- **Problem**: §6 addresses "institutions worldwide," calls dashboard investment "dependable" and "generalizable," extends the outcome to "retention across programs and disciplines," and recommends *encouraging* engagement — none of which the study observed.
- **Source**: CONSENSUS-4 (SC-19); CONSENSUS-3 (SC-20, EIC silent); corroborated (SC-21, EIC and R3); DA M3, M4.
- **Requirement**: Keep every claim at the course level and at this site, this term, this interface. State explicitly that whether institutionally induced engagement carries the association observed in voluntary use is an open question requiring a randomized encouragement design.
- **Acceptance criteria**: §5.1 and §6 no longer contradict each other, and the conclusion answers the question §1 asked.

**R6: Verify the literature base and rebuild the equity rationale**
- **Problem**: §2 attributes to Ferro & Nakamura (2021) a finding contradicted by the manuscript's own reference-list title, and builds the equity rationale on it; nine of fifteen entries are uncited; all fifteen DOIs sit in a reserved-example prefix.
- **Source**: CONSENSUS-4 (SC-25, R2 owning); CONSENSUS-3 (SC-26, R1 silent); corroborated (SC-27, EIC and R2).
- **Requirement**: Quote the passage supporting §2's reading or correct the sentence and rebuild the equity rationale on a source that argues it. Resolve every reference independently and correct the DOIs. Cite the nine unused entries where they belong — Wexler & Ojo (2020) in particular, as the closest published analogue to this design — or remove them.
- **Acceptance criteria**: Every reference resolves, every entry is cited, and no in-text characterisation contradicts its own bibliographic record.

**R7: Match the analysis to the outcome**
- **Problem**: A dichotomous outcome analysed by an unnamed point-biserial correlation, with a median-split predictor, no adjustment, no interval, and no retention base rate.
- **Source**: CONSENSUS-3 (SC-12, SC-14, R3 silent); single-reviewer at confidence 5 (SC-13); corroborated (SC-15).
- **Requirement**: Fit logistic or discrete-time hazard regression on continuous landmark-censored engagement with covariates; report the base rate, the 2×2 table, odds ratio with 95% CI, and the marginal risk difference; name the software and version and the *t*-test variant; report assumption checks and the treatment of multiple tests.
- **Acceptance criteria**: The reported quantity is one an institution could act on, with its precision stated.

## Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Source | Priority | Section | Expected Improvement |
|---|---------------|--------------|--------|----------|---------|----------------------|
| S1 | Engage the retention and persistence tradition in the body; attribute the SRL phase model to its originator; argue why perceived control indexes the SRL phases the mechanism story needs, **or** reframe the construct as academic control / self-efficacy; supply psychometric evidence for the item or state what a single global rating can carry; cite the "single-item ratings are common" claim or drop it | SC-28, SC-29, SC-30 | EIC, R1, R2 (SC-30 arbitrated) | P2 | §1, §2, §3.3, §5 | Situates the outcome for a higher-education reader; makes the measure evaluable on its own terms |
| S2 | Test the demotivation account (Osei, 2020) against these data by prior attainment, **or** state in §5.1 that the design cannot detect demotivation and therefore cannot support recommending the peer-comparison band | SC-31 | EIC, R2, R3 | P2 | §4, §5.1, §6 | Delivers the analysis §2 promises; removes an unexamined equity hazard from the recommendation |
| S3 | Identify the dashboard artifact — platform, version, refresh behaviour, and what students saw (figure or annotated description); justify or sensitivity-test the 30-minute sessionization rule at alternative thresholds | SC-36, SC-37 | EIC, R1, R2, R3 | P2 | §3.1, §3.3 | Lets another site determine whether its dashboard is the same class of object |
| S4 | Add a stakeholder passage covering student experience of being measured, differential device and connectivity access, and data governance; account for the students with zero sessions; state once that institutional and student interests in retention are not identical | SC-35, DA frame-lock | R3, DA | P2 | §5, §5.1 | Closes the equity inversion R3 identifies; surfaces the premise beneath the whole framing |
| S5 | Characterise the institution (type, system, sector, student population) and give the enrolled *N* | SC-17, SC-38 | EIC, R1, R2, R3 | P2 | §3.1, §3.2 | Makes transferability judgeable rather than guessable |
| S6 | Articulate the incremental contribution against the saturation §2 itself documents, or reframe the paper as a descriptive institutional case report | SC-23 | EIC, R2 | P2 | §1, §5 | Answers the "so what" the current framing argues against |
| S7 | Rewrite the abstract to carry the design descriptor (observational, cross-sectional), the single-course scope, the reconciled effect size, and the 87-respondent basis of the perceived-control comparison | SC-24, SC-1 | EIC | P2 | Abstract | The section most readers read alone stops contradicting the body |
| S8 | Exhibit and format cleanup: per-row *N* in Table 1; test statistic, *p*, effect size, and CI in Table 2; consistent decimal precision; final-exam measure defined in §3.3; software and *t*-test variant named; "retention" / "persistence" / "completion" and "access" / "engagement" used consistently | SC-5, SC-7, SC-15, SC-20 | EIC, R1, R2, R3 | P3 | §3.3, §3.4, Tables 1–2 | Exhibits become readable on their own terms |

## Revision Checklist

### Priority 1 — Structural Revisions (estimated total effort: 6–10 weeks of author work, plus one full term if the retention question is retained)
- [ ] R1: Re-derive and reconcile every reported statistic; supply per-test *N* and the analysis script
- [ ] R2: Document the ethics basis for the log analysis or withdraw it; add the four missing declarations and the linkage/de-identification account
- [ ] R3: State the actual recruitment procedure with enrolled *N* and participation rate; collect or reconstruct a cohort not conditioned on mid-term survival; censor exposure at a pre-withdrawal landmark
- [ ] R4: Retract all causal and interventional language; confront reverse causation and common cause; rewrite §5.1 to the load-bearing threats
- [ ] R5: Rewrite §6 to course-level, single-site scope; withdraw the worldwide and induced-engagement recommendations
- [ ] R6: Correct the Ferro & Nakamura characterisation; rebuild or withdraw the equity rationale; verify all fifteen references and the DOIs; cite or remove the nine unused entries
- [ ] R7: Refit with a model appropriate to a dichotomous outcome; report base rate, 2×2, OR with CI, and risk difference; drop the median split

### Priority 2 — Content Supplementation (estimated total effort: 8–12 days)
- [ ] S1: Engage the persistence literature; attribute the SRL model; justify or reframe the perceived-control construct
- [ ] S2: Test the demotivation account by prior attainment, or state that the design cannot detect it
- [ ] S3: Identify the dashboard artifact; justify or sensitivity-test the sessionization rule
- [ ] S4: Add the stakeholder, access, and governance passage; account for zero-session students; separate institutional from student interest
- [ ] S5: Characterise the institution and give the enrolled *N*
- [ ] S6: Articulate the incremental contribution, or reframe as a case report
- [ ] S7: Rewrite the abstract to the design, scope, and reconciled values

### Priority 3 — Text and Formatting (estimated total effort: 1–2 days)
- [ ] S8: Per-row *N* in Table 1; full inferential reporting in Table 2; consistent decimal precision (3.847 against 0.62 against 14.6)
- [ ] S8: Define the final-exam measure in §3.3 Measures before it appears in Results
- [ ] S8: Name the statistical software and version, and whether Student's or Welch's *t* was used
- [ ] S8: Fix terminology drift — "retention" / "persistence" / "completion"; "access" / "engagement"; "perceived control" / "self-regulation"
- [ ] S8: State whether "Meridian State University" is the institution's name or a pseudonym
- [ ] S8: Disambiguate §3.1's "no separate opt-in" (tool access) from §3.2's opt-in (study participation)
- [ ] S8: Define "learning analytics" against academic analytics and educational data mining in one line

### Total Estimated Effort
- **As a resubmission**: 6–10 weeks of author work for R1, R2, R4–R7 and all P2/P3 items, **plus** a new data-collection cycle (one term minimum) if R3's retention question is retained rather than withdrawn.

## Revision Deadline

Not applicable — this decision is Reject. No revision deadline is set and no re-review of this manuscript is scheduled. A resubmission may be made at any time and will enter as a new submission with a fresh review round.

## Response Letter Instructions

Should the authors resubmit, please use the format in `templates/revision_response_template.md` to respond to every item above point by point.

**Must include:**
1. A response and change description for each Required Revision (R1–R7)
2. A response for each Suggested Revision (S1–S8), stating adoption or the reason for non-adoption
3. A response to each of the six Devil's Advocate CRITICAL issues (C1–C6) and to the frame-lock premise, including those the panel already corroborates
4. Change markup in the resubmitted manuscript
5. A cross-reference table mapping each response to its new page and paragraph

---

## Closing

After careful consideration, and with the unanimous recommendation of all four independent reviewers, we are unable to accept your manuscript for publication in the *Journal of Learning Analytics*.

We want to be direct about why, because the reasons are not evenly distributed. Your literature review is a genuinely critical map of this field's disagreements, your Methods define both focal constructs operationally, and your limitations section identifies the right risks. Every reviewer said so independently, and several said the question is worth answering. The manuscript does not fail for want of competence.

It fails on three things at once. The reported numbers do not agree with each other, so the panel could not determine what you found. The claims in §5 and §6 go past what an unadjusted observational association can license — and past what your own §1 and §5.1 say. And two features of how the data came into existence, mid-term volunteer recruitment and an exposure window that closes at the outcome, are not reachable by reanalysis. The ethics gap in §3.2 is a fourth matter that rewriting cannot cure and that should go to your ethics body regardless of what you do with this manuscript.

The distance between §5.1 and §6 is the whole problem, and it is a distance you already know how to close. A study built on the full enrolled cohort with prospectively measured, landmark-censored exposure, a documented ethics basis, verified references, and claims held to the design's ceiling would be welcome here. If the retention question cannot be answered with these data, the honest and publishable alternative is a descriptive institutional case report at a practice-oriented venue; with a corrected analysis and retracted claims, *BJET* or *Internet and Higher Education* would be realistic targets for the present dataset.

We appreciate the effort behind this work and hope the reviewers' comments are useful to it.

---

# Part 3: Reviewer Report Summary (Appendix)

### EIC Report Summary
- **Recommendation**: Reject | **Confidence**: 4
- **Key Point**: The manuscript names the field's cardinal inferential error in §2 and commits it in §5 and §6; combined with an effect size the abstract and results do not agree on, and an ethics gap that rewriting cannot cure, the conjunction across three mandatory dimensions makes this a Reject rather than a Major Revision.

### Reviewer 1 (Methodology) Summary
- **Recommendation**: Reject | **Confidence**: 5
- **Key Point**: Six mutually inconsistent reported statistics mean no reported value can be treated as evidence; independently, mid-term recruitment left-truncates the sample on the outcome and uncensored exposure makes part of the association mechanical — two defects no reanalysis of this dataset can reach.

### Reviewer 2 (Domain) Summary
- **Recommendation**: Reject, with a path back | **Confidence**: 4 (conditional on an independent bibliographic resolution check)
- **Key Point**: §2's characterisation of Ferro & Nakamura (2021) contradicts the manuscript's own reference list and carries the equity rationale; with nine of fifteen entries uncited and the persistence tradition absent from the body, no literature-based claim here is reviewable until the bibliography is verified.

### Reviewer 3 (Perspective) Summary
- **Recommendation**: Reject | **Confidence**: 4
- **Key Point**: §3.2 documents undisclosed secondary use of individually-linked behavioural data with no ethics apparatus reported, while §6 recommends worldwide scale-up of a practice whose measured variable (spontaneous opening) is not the one it prescribes (induced engagement) — and whose peer-comparison band the paper's own §2 flags as a hazard to the students an equity rationale would target.

### Devil's Advocate Summary
- **Recommendation**: (no overall-recommendation field emitted) | **Confidence**: (none emitted)
- **Key Point**: A strictly more parsimonious rival — exposure-window truncation, in which retention partly manufactures the predictor — fits all three reported results including the near-null exam comparison with no dashboard effect required, and is neither raised nor tested nor listed among the limitations.

*Full reviewer reports are attached for the authors' reference.*
