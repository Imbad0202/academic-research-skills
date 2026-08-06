# Field Analysis Report

## Paper Basic Information

- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~155 words
- **Full text length**: ~1,700 words (main text, Sections 1–7, excluding abstract and references) — approximate count
- **Number of references**: 6
- **Language**: English (review to be conducted in English)

---

## Field Analysis

| Dimension | Analysis Result |
|---|---|
| **Primary Discipline** | Educational technology in higher education — specifically LMS adoption and student engagement with institutional platforms |
| **Secondary Disciplines** | (1) Information systems / technology acceptance research (TAM lineage); (2) Survey methodology and educational measurement; (3) Higher education institutional practice (digital education service delivery) |
| **Research Paradigm** | Quantitative — explicitly descriptive/correlational, not model-testing |
| **Methodology Type** | Single-site cross-sectional survey; bivariate correlational analysis (Pearson with Spearman robustness check). No multivariate modelling, no experimental or longitudinal component |
| **Target Journal Tier** | **Q3**, with Q2 reachable only after substantial expansion. Rationale: the reporting quality is above its weight class (95% CI, a priori-style power statement, robustness check, explicit non-causal framing, ethics detail), but the contribution is a single bivariate coefficient from one institution supported by a 6-item reference base. Q1 outlets in this space (*Computers & Education*, *BJET*, *IJETHE*, *Internet and Higher Education*) would desk-reject on incremental contribution, not on execution |
| **Paper Maturity** | **Pre-submission** — structurally complete, internally consistent, language-polished, reporting conventions largely observed. Two substantive gaps prevent it from being submission-ready: (a) no response rate is derivable, and (b) the literature base is far too thin to establish where this data point sits in the distribution it claims to join |

### Verification notes carried into review

These are flagged for reviewer attention, not adjudicated here:

- **Arithmetic checks out**: 233 − 14 − 5 = 214. Consistent throughout.
- **CI checks out**: Fisher-z transformation of r = .42 at n = 214 yields approximately [.30, .52]. As reported.
- **Power claim checks out**: minimum detectable r at 80% power, α = .05 two-tailed, n = 214 is approximately .19. As reported.
- **Reference DOIs require verification**: all six references carry the `10.5555/` prefix, which is a reserved test/sandbox prefix, not a live registrant prefix. None of the six journal titles is readily identifiable as an indexed outlet. This may be an anonymisation artefact of the review copy, but it must be resolved before any editorial recommendation is issued.
- **Unaddressed threat**: both variables were collected from the same respondents, in the same instrument, at the same moment. Common method variance is a live inflation risk for the headline r and is absent from both the Limitations section and the Analysis section.

---

## Recommended Target Journals (Top 3)

1. **Research in Learning Technology** (ALT, open access) — Best fit. Publishes bounded single-site empirical work and explicitly values transparent, appropriately hedged reporting. The paper's epistemic discipline is a match for this readership. Requires expanding the literature base and reporting a response rate.

2. **Journal of Applied Research in Higher Education** (Emerald) — Realistic fallback. Tolerant of single-institution survey work and oriented to institutional practice, which suits the onboarding implication in Section 5. Would expect the practice implication to be developed further than one hedged sentence.

3. **Australasian Journal of Educational Technology** — Stretch target. Reachable only if the authors add a second institution or link a log-data subsample; as currently scoped the contribution is below AJET's novelty threshold.

**Not recommended at current scope**: *Computers & Education*, *British Journal of Educational Technology*, *International Journal of Educational Technology in Higher Education*. The gap is contribution size, not craft.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of *Research in Learning Technology*, learning-technology evaluation specialist in UK higher education; handles the journal's short empirical report stream and has chaired an ALT conference research strand. Routinely triages single-site survey submissions and has published editorially on when incremental replication earns journal space.

**Review Focus**:
1. Whether a single bivariate correlation from one institution constitutes a publishable unit for this journal's readership, and if so, whether the short-report format rather than full article is the correct vehicle.
2. Whether the 6-reference base is sufficient to establish the paper's claim that it is "one point in a distribution" — a claim that logically requires the distribution to be characterised, which six sources cannot do.
3. Verification of the reference list: whether the six cited works exist as indexed publications, given the `10.5555/` test-prefix DOIs and unfamiliar journal titles.

**Will particularly care about**: Whether the paper's declared modesty is a legitimate scoping decision that still clears the contribution bar, or a rhetorical shield placed in front of a contribution that does not clear it. These are different papers and must be distinguished before any recommendation.

**Possible blind spots**: May accept the statistical reporting at face value because it is unusually well presented, without independently checking the CI, power, or the untreated common-method-variance threat. May also over-weight fit and under-weight whether the practice implication in Section 5 is actionable for the journal's practitioner readership.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Survey methodologist with a psychometrics background, based in an institutional research and educational measurement unit; specialises in measurement error in self-report instruments, nonresponse bias in web-administered institutional surveys, and the validity limits of single-item measures. Has published on common method variance in acceptance research.

**Review Focus**:
1. **Response rate and nonresponse.** "All enrolled undergraduates were eligible" establishes a population but never states its size, so no response rate is derivable and the voluntary-response limitation in Section 6 cannot be assessed for magnitude. Also: how were the 5 duplicates identified in an anonymous survey, and does that detection mechanism conflict with the claim that no identifying information was collected?
2. **Common method variance.** Predictor and outcome share source, instrument, and occasion. This is a standard inflation mechanism for the reported r and is not mentioned anywhere in the paper. Was any procedural or statistical remedy (item separation, marker variable, Harman's test) considered?
3. **Measurement adequacy.** The adapted six-item scale is supported only by α = .88, which evidences internal consistency but not unidimensionality or structural validity in this sample. What did the adaptation change from Costa and Wren's original, and was any factor structure examined? Separately, the single-item ordinal outcome carries unknown reliability, and the Spearman check addresses distributional form but not reliability attenuation.

**Will particularly care about**: Whether the reported r = .42 is defensible as an estimate of anything beyond shared self-report method, and whether the honest limitations section covers the threats that actually matter here or only the visible ones.

**Possible blind spots**: May push for redesign the paper explicitly disclaims (log linkage, longitudinal waves, multi-site sampling), converting a scoping decision into a rejection ground. May also disengage from whether the field literature is adequately covered, treating that as outside methodological remit.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior scholar in higher-education learning technology, thirty years in the field, with sustained work on LMS engagement and the migration of acceptance research from information systems into education. Has written on replication norms in educational technology and serves on two editorial boards in the area.

**Review Focus**:
1. **Literature coverage.** Six references cannot situate a technology-acceptance study. The foundational acceptance literature (Davis; Venkatesh and colleagues on UTAUT) is entirely absent, as is the last decade of LMS engagement and learning-analytics work. Without these, the paper cannot substantiate its central positioning claim of being "comparable with prior work."
2. **Contribution framing.** The paper positions itself as an incremental data point. Fair — but the field has explicit norms for what a contributory replication must supply: an identified target estimate, a stated comparison, and a statement of whether the result converges or diverges. The paper supplies none of these. Which prior estimate is r = .42 being compared against, and does it agree?
3. **Theoretical stance.** The paper invokes perceived usefulness as a construct while declining to test any model. That is a legitimate position, but it needs defending rather than assuming: what is gained by measuring a TAM construct outside TAM, and what does the resulting coefficient mean absent the nomological network the construct was built inside?

**Will particularly care about**: Whether "incremental contribution" is being used with its technical meaning — a result that measurably tightens or challenges an existing estimate — or as a general disclaimer. Only the first earns publication.

**Possible blind spots**: May demand full TAM/UTAUT model testing, which would inflate scope well past the paper's declared narrow question and past what a bivariate dataset can support. May accept the statistics uninspected as the methodologist's territory.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Director of Digital Education at a large public university; learning technologist by training, with a scholarship-of-teaching-and-learning publication record and standing membership on LMS procurement and renewal committees. Spends professional time deciding whether findings like this one should change institutional spend, and has run the onboarding interventions the paper's Discussion recommends.

**Review Focus**:
1. **Actionability of the practice claim.** Section 5 proposes that onboarding demonstrating "concrete usefulness" may warrant institutional attention. From a decision-maker's chair, r = .42 between two self-reports supports no resourcing decision at all. What specifically would an institution do differently, and what would count as evidence that it worked?
2. **The design self-contradiction.** The paper's own recommendation for future work is behavioural log data. Every institution running an LMS already holds those logs. The anonymity design deliberately foreclosed linkage to them. Was that trade-off examined and justified, or defaulted into? Consent-based opt-in linkage is standard practice and would have converted this into a substantially stronger study at marginal cost.
3. **Missing institutional context.** LMS use is heavily determined by whether instructors mandate it, whether assessment submission runs through it, and whether attendance or grades are posted there. Section 4 gestures at this ("course requirements and assessment schedules") but no institutional policy context is reported. Without it, a reader cannot judge whether this site's r = .42 would transfer to their own campus — which is exactly what the generalisation limitation claims to be about.

**Will particularly care about**: Whether a finding offered as useful to practice has been tested against what practice actually needs, or whether "implications for practice" is functioning as a section heading rather than a claim.

**Possible blind spots**: May undervalue the legitimate scholarly function of a well-bounded descriptive estimate, treating immediate actionability as the sole criterion. May also press for institution-identifying policy detail that conflicts with the site anonymity the paper maintains.

---

## Review Strategy Recommendations

**1. Primary calibration hazard: humility is not a contribution.**
This manuscript is unusually self-limiting. It pre-empts nearly every standard criticism — causality, generalisability, self-report validity, effect size — in its own Limitations and Discussion. The risk is that reviewers reward the epistemic discipline and stop there. Each reviewer should be held to a separate question: *after all disclaimers are granted, what is left, and does it clear the bar?* The disclaimers are correct. Whether the residue is publishable is a distinct judgement and must be made explicitly.

**2. Deliberate non-overlap of the four angles.**
The four reviewers converge on the same manuscript from four non-intersecting directions: fit and contribution size (Journal-Fit); measurement and inferential validity (R1); field literature and replication norms (R2); institutional decision-usefulness (R3). No two share a primary focus. The one adjacent pair is R1's common-method-variance concern and R3's log-linkage concern — these look similar but are not: R1 asks whether the coefficient is contaminated, R3 asks why an available and superior data source was designed out. Keep both.

**3. Convergence to expect, and what it means.**
R1's response-rate gap, R2's six-reference gap, and R3's missing institutional context are three independent routes to the same underlying deficiency: *the paper cannot support its own generalisability framing.* It repeatedly describes itself as one point in a distribution, but never characterises the distribution (R2), never establishes what population its point represents (R1), and never describes the local conditions that would let a reader judge transfer (R3). If all three raise this independently, the synthesiser should treat it as the paper's single load-bearing defect rather than three separate minor revisions.

**4. Tension to expect between R2 and the Journal-Fit Reviewer.**
R2 will likely push toward model testing and a substantially expanded theoretical apparatus. The Journal-Fit Reviewer, configured against a journal that accepts short empirical reports, will resist scope inflation. This tension is productive and should be preserved, not resolved prematurely. The synthesiser should distinguish *literature coverage sufficient to position the finding* (necessary, and currently absent) from *theoretical model testing* (not necessary given the declared scope).

**5. Reference verification must be resolved before any recommendation is finalised.**
All six DOIs use a reserved test prefix and none of the cited journals is readily identifiable. This may well be an artefact of the anonymised review copy. But no reviewer can assess literature adequacy against sources that cannot be located, and the Journal-Fit Reviewer cannot recommend acceptance of a paper whose evidentiary base is unverifiable. Assign this to the Journal-Fit Reviewer as a gating item and have the synthesiser confirm it was addressed rather than skipped.

**6. Register.**
Pre-submission maturity with sound craft. Standard peer-review register is appropriate — no developmental scaffolding needed. The authors demonstrably understand inferential limits; feedback should engage them at that level rather than restating cautions they have already internalised. Tone stays collegial; the verdict follows the evidence regardless of tone.
