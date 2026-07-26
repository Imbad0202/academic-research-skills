# EQUATOR Reporting Guidelines — Research Design and Reporting Guideline Mapping

## Purpose
Quick reference for EQUATOR Network (Enhancing the QUAlity and Transparency Of health Research) reporting guidelines. Assists the research_architect_agent in selecting the appropriate reporting checklist during the methodology design stage, and the report_compiler_agent in ensuring report completeness during the writing stage.

---

## 1. Research Design → Reporting Guideline Mapping Table

| Research Design | Primary Reporting Guideline | Applicable Scenario |
|----------|------------|---------|
| Systematic review / Meta-analysis | **PRISMA** | Literature review integrating multiple studies |
| Randomized controlled trial (RCT) | **CONSORT** | Intervention experiments with random assignment |
| Observational study (cohort, case-control, cross-sectional) | **STROBE** | Non-interventional quantitative observational research |
| Qualitative research | **COREQ** | Interviews, focus groups, observation |
| Quality improvement study | **SQUIRE** | Systematic quality improvement project reports |
| Diagnostic accuracy study | **STARD 2015** | Diagnostic tool evaluation |
| Prediction model study (prognostic or diagnostic) | **TRIPOD+AI** | Prediction model development and validation, regression or machine learning |
| Case report | **CARE** | Single or small number of in-depth case reports |
| Economic evaluation | CHEERS | Cost-effectiveness analysis |
| Mixed methods research | GRAMMS | Mixed qualitative-quantitative designs |
| Animal study | ARRIVE | Animal experiments |
| Network meta-analysis | PRISMA-NMA | Multiple comparison meta-analysis |
| Scoping review | PRISMA-ScR | Scoping review (less stringent than systematic review) |

Guidelines in **bold** have a condensed checklist section in this file (§2-§9). The remainder are pointers only — retrieve the full checklist from the EQUATOR Network. If the study design itself is not yet settled, work through the routing sequence in §10 before using this table.

---

## 2. PRISMA — Systematic Review Condensed Checklist

**Full Name**: Preferred Reporting Items for Systematic Reviews and Meta-Analyses
**Version**: PRISMA 2020 (latest)

### Core Reporting Items

| # | Item | Description | Necessity |
|---|------|------|--------|
| 1 | **Title** | Clearly identify as a systematic review (with or without meta-analysis) | Required |
| 2 | **Abstract** | Structured abstract (background, purpose, methods, results, conclusions) | Required |
| 3 | **Registration** | Registration number and platform (e.g., PROSPERO) | Strongly recommended |
| 4 | **Eligibility criteria** | Inclusion/exclusion criteria in PICOS or PEO format | Required |
| 5 | **Information sources** | Databases searched and dates | Required |
| 6 | **Search strategy** | Complete search strategy for at least one database | Required |
| 7 | **Selection process** | Screening process (number of reviewers, how disagreements were resolved) | Required |
| 8 | **Data extraction** | Data extraction methods | Required |
| 9 | **Risk of bias** | Risk of bias assessment tool and results | Required |
| 10 | **Synthesis methods** | Synthesis method (narrative / meta-analytic) | Required |
| 11 | **PRISMA flow diagram** | Literature screening flow diagram | Required |
| 12 | **Results** | Characteristics of each study, bias assessment, synthesis results | Required |
| 13 | **Discussion** | Certainty of evidence, limitations, relationship to existing knowledge | Required |
| 14 | **Funding** | Funding sources and conflicts of interest | Required |

### PRISMA Flow Diagram Template

```
Records identified (n = )
├── Database searching (n = )
└── Other sources (n = )
         ↓
Duplicates removed (n = )
         ↓
Records screened (n = )
├── Excluded (n = )
         ↓
Reports sought for retrieval (n = )
├── Not retrieved (n = )
         ↓
Reports assessed for eligibility (n = )
├── Excluded, with reasons (n = )
│   ├── Reason 1 (n = )
│   ├── Reason 2 (n = )
│   └── Reason 3 (n = )
         ↓
Studies included in review (n = )
├── In qualitative synthesis (n = )
└── In quantitative synthesis (meta-analysis) (n = )
```

---

## 3. CONSORT — Randomized Controlled Trial Condensed Checklist

**Full Name**: Consolidated Standards of Reporting Trials
**Version**: CONSORT 2010 + extensions

### Core Reporting Items

| # | Item | Description |
|---|------|------|
| 1 | **Title & Abstract** | Identify as RCT; structured abstract |
| 2 | **Background** | Scientific background and trial rationale |
| 3 | **Objectives** | Specific objectives or hypotheses |
| 4 | **Trial design** | Design type (parallel, crossover, factorial, etc.) and allocation ratio |
| 5 | **Participants** | Eligibility criteria, settings, data collection locations |
| 6 | **Interventions** | Specific description of each group's intervention (including how and when administered) |
| 7 | **Outcomes** | Primary and secondary outcome measures, including definitions and time points |
| 8 | **Sample size** | Sample size calculation method (power analysis) |
| 9 | **Randomisation** | Random sequence generation method, allocation concealment mechanism |
| 10 | **Blinding** | Blinding implementation (who was blinded, how it was implemented) |
| 11 | **Statistical methods** | Statistical analysis methods, ITT/PP analysis |
| 12 | **Flow diagram** | Participant flow diagram (recruitment → allocation → follow-up → analysis) |
| 13 | **Results** | Results per group, effect sizes and precision (CI) |
| 14 | **Harms** | Adverse events or side effects |
| 15 | **Limitations** | Sources of bias, imprecision, multiple comparisons |
| 16 | **Registration** | Trial registration number |

### Higher Education Research Application Notes

RCTs in the education field (e.g., comparing teaching methods) commonly face:
- Inability to fully randomize (cluster randomization is more common)
- Difficulty implementing blinding (teachers/students know their group)
- Recommended to use **CONSORT-SPI** (Social and Psychological Interventions extension)

---

## 4. STROBE — Observational Study Condensed Checklist

**Full Name**: Strengthening the Reporting of Observational Studies in Epidemiology
**Applicable to**: Cohort studies, case-control studies, cross-sectional studies

### Core Reporting Items

| # | Item | Description |
|---|------|------|
| 1 | **Title & Abstract** | Indicate the study design type |
| 2 | **Background** | Scientific background, study rationale |
| 3 | **Objectives** | Specific objectives, pre-specified hypotheses |
| 4 | **Study design** | Clearly state the study design (cohort / case-control / cross-sectional) |
| 5 | **Setting** | Setting, location, relevant dates (recruitment, exposure, follow-up) |
| 6 | **Participants** | Eligibility criteria, data sources, sampling method |
| 7 | **Variables** | Outcome variables, exposure variables, potential confounders, effect modifiers |
| 8 | **Data sources** | Data sources and measurement methods for each variable |
| 9 | **Bias** | Methods for addressing potential sources of bias |
| 10 | **Study size** | How the sample size was determined |
| 11 | **Statistical methods** | Statistical methods (including confounder handling, missing data handling) |
| 12 | **Results** | Descriptive statistics, main results (including effect sizes, CI, p-value) |
| 13 | **Discussion** | Key findings, limitations, generalizability, consistency with other studies |
| 14 | **Funding** | Funding sources |

### Higher Education Research Application Notes

Common observational studies in higher education:
- Student learning outcome cross-sectional survey → cross-sectional STROBE
- Graduate employment tracking → cohort STROBE
- Dropout risk factor analysis → case-control STROBE

---

## 5. COREQ — Qualitative Research Condensed Checklist

**Full Name**: Consolidated Criteria for Reporting Qualitative Research
**Applicable to**: Interviews, focus groups

### Core Reporting Items (32 items, across 3 domains)

#### Domain 1: Research Team and Reflexivity

| # | Item | Description |
|---|------|------|
| 1 | **Interviewer/facilitator** | Who conducted the interviews or facilitated focus groups |
| 2 | **Credentials** | Researcher qualifications |
| 3 | **Occupation** | Researcher's professional identity |
| 4 | **Gender** | Researcher gender |
| 5 | **Experience & training** | Qualitative research experience and training |
| 6 | **Relationship with participants** | Researcher's relationship with participants |
| 7 | **Participant knowledge** | Participants' level of knowledge about the research |

#### Domain 2: Study Design

| # | Item | Description |
|---|------|------|
| 8 | **Methodological orientation** | Theoretical framework (e.g., grounded theory, phenomenology) |
| 9 | **Sampling** | Sampling strategy and method |
| 10 | **Method of approach** | How participants were contacted |
| 11 | **Sample size** | Number of participants |
| 12 | **Non-participation** | Number and reasons for refusal to participate |
| 13 | **Setting** | Interview location |
| 14 | **Presence of non-participants** | Whether non-participants were present during interviews |
| 15 | **Description of sample** | Participant demographics |
| 16 | **Interview guide** | Whether an interview guide was used and whether it was pilot-tested |
| 17 | **Repeat interviews** | Whether repeat interviews were conducted |
| 18 | **Audio/visual recording** | Whether audio/video was recorded |
| 19 | **Field notes** | Whether field notes were taken |
| 20 | **Duration** | Interview duration |
| 21 | **Data saturation** | Whether data saturation was discussed |
| 22 | **Transcripts returned** | Whether transcripts were returned to participants for feedback |

#### Domain 3: Analysis and Findings

| # | Item | Description |
|---|------|------|
| 23 | **Data analysis** | Analysis method (e.g., thematic analysis, IPA) |
| 24 | **Software** | Analysis software used |
| 25 | **Participant checking** | Whether participants confirmed the findings |
| 26 | **Quotations** | Whether quotations are presented to support themes |
| 27 | **Data and findings consistency** | Consistency between data and findings |
| 28 | **Clarity of major themes** | Whether major themes are clearly presented |
| 29 | **Clarity of minor themes** | Whether minor themes are clearly presented |

---

## 6. SQUIRE — Quality Improvement Study Condensed Checklist

**Full Name**: Standards for QUality Improvement Reporting Excellence
**Version**: SQUIRE 2.0
**Applicable to**: Quality improvement projects, systematic quality improvement, higher education quality assurance (QA) research

### Core Reporting Items

| # | Item | Description |
|---|------|------|
| 1 | **Title** | Identify as a quality improvement study |
| 2 | **Abstract** | Structured abstract |
| 3 | **Problem description** | Nature and severity of the quality problem |
| 4 | **Available knowledge** | Known relevant evidence |
| 5 | **Rationale** | Theoretical basis for the improvement initiative |
| 6 | **Specific aims** | Specific improvement goals (quantifiable) |
| 7 | **Context** | Environmental context of the improvement |
| 8 | **Intervention(s)** | Specific description of improvement measures |
| 9 | **Study of the intervention(s)** | How the improvement effectiveness was evaluated |
| 10 | **Measures** | Outcome measures, process measures, balancing measures |
| 11 | **Analysis** | Quantitative/qualitative analysis methods |
| 12 | **Ethical considerations** | Ethics review (if applicable) |
| 13 | **Results** | Improvement results (including time series data) |
| 14 | **Discussion** | Key findings, relationship to context, generalizability |
| 15 | **Limitations** | Study limitations |

### Particularly Applicable for Higher Education QA Research

SQUIRE is especially valuable as a reference for the following HE quality assurance research:
- **Teaching quality improvement**: Introduction and evaluation of new teaching strategies
- **Curriculum reform**: Tracking the effects of curriculum redesign
- **Student support service improvement**: Systematic improvement of tutoring, counseling, and learning support
- **HEEACT accreditation self-improvement**: Improvement actions and tracking in response to accreditation findings
- **Institutional research (IR)-driven improvement**: Data-based decision-making and improvement cycles

---

## 7. CARE — Case Report Condensed Checklist

**Full Name**: CAse REport guidelines
**Version**: CARE 2013 checklist (13 topics, 30 checkable items)
**Applicable to**: Reports of the diagnosis and management of one patient; adaptable to a small uncontrolled series
**Source statement**: Gagnier JJ, Kienle G, Altman DG, Moher D, Sox H, Riley D; CARE Group. The CARE guidelines: consensus-based clinical case report guideline development. *J Clin Epidemiol*. 2014;67(1):46-51. doi:10.1016/j.jclinepi.2013.08.003
**Official checklist**: https://www.care-statement.org/checklist

> The wording below is an ARS paraphrase written for orientation, not the official checklist text. CARE is distributed under a non-commercial licence and the item wording is not reproduced here. Download the official checklist before submission and report against that.

### Core Reporting Items

| # | Item | Description |
|---|------|------|
| 1 | **Title** | Name the principal diagnosis or intervention and label the article a case report |
| 2 | **Key words** | Two to five terms naming the diagnoses or interventions, one of them identifying the article as a case report |
| 3a-3d | **Abstract** | What is unusual about the case and what it adds; the leading symptoms and clinical findings; the diagnoses, interventions and outcomes; the take-away lesson |
| 4 | **Introduction** | One or two paragraphs on why this case is worth reporting, with references |
| 5a-5d | **Patient information** | De-identified patient details; the patient's own presenting concerns and symptoms; the history that bears on the case, covering the patient's own illnesses, the family's, the psychosocial picture and any genetics that matter; relevant earlier interventions and how they turned out |
| 6 | **Clinical findings** | The physical examination findings and other clinical findings that matter to the case |
| 7 | **Timeline** | Historical and current events of this episode of care arranged as a dated timeline (figure or table) |
| 8a-8d | **Diagnostic assessment** | Diagnostic methods used (examination, laboratory, imaging, questionnaires); any obstacles to testing, including access, cost or cultural barriers; the diagnosis reached and the alternatives considered; prognostic features where applicable |
| 9a-9c | **Therapeutic intervention** | Type of treatment (drug, surgical, preventive, self-care); how it was given, including dose, strength and duration; any changes made during care and why |
| 10a-10d | **Follow-up and outcomes** | Outcomes as assessed by the clinician and by the patient; follow-up test results; adherence and tolerability, and how these were judged; anything harmful or unforeseen that occurred along the way |
| 11a-11d | **Discussion** | Strengths and limitations of how the case was managed; the relevant literature; the scientific reasoning behind the conclusions, including alternative explanations; the primary take-away lesson |
| 12 | **Patient perspective** | The patient's own account of the care they received, in their own voice where possible |
| 13 | **Informed consent** | Confirmation that the patient (or next of kin) gave informed consent, available on request |

### Clinical Research Application Notes

- Items 12 and 13 are the two least recoverable after the fact. Informed consent for publication has to be obtained from the patient, and the patient perspective has to be collected while contact is still possible — flag both at the design stage, not at submission.
- The timeline (item 7) asks for a structured chronology as a figure or table; a chronology scattered through the narrative does not satisfy it.
- De-identification (item 5a) is a reporting requirement and an ethics requirement at once. Dates, rare-disease combinations and institution names can re-identify a patient even without a name.
- For a small uncontrolled series, CARE can be adapted per patient, but a series with a comparison group is not a case report — re-run the routing sequence in §10.

---

## 8. STARD 2015 — Diagnostic Accuracy Study Condensed Checklist

**Full Name**: Standards for Reporting Diagnostic accuracy studies
**Version**: STARD 2015 (30 items; participant flow diagram required)
**Applicable to**: Studies estimating how well one or more index tests classify participants against a reference standard
**Source statement**: Bossuyt PM, Reitsma JB, Bruns DE, et al. STARD 2015: an updated list of essential items for reporting diagnostic accuracy studies. *BMJ*. 2015;351:h5527. doi:10.1136/bmj.h5527
**Official checklist**: https://www.equator-network.org/reporting-guidelines/stard/

> The wording below is an ARS paraphrase written for orientation, not the official checklist text. Report against the official STARD 2015 checklist.

### Core Reporting Items

| # | Item | Description |
|---|------|------|
| 1 | **Identification** | State in the title or abstract that this is a diagnostic accuracy study and name at least one accuracy measure (sensitivity, specificity, predictive values, AUC) |
| 2 | **Abstract** | Structured summary of design, methods, results and conclusions (STARD for Abstracts gives the item list) |
| 3 | **Background** | Set out the science and the clinical problem, and say what the index test is meant to be used for and where it would sit in the care pathway |
| 4 | **Objectives** | What the study set out to establish, and any hypothesis stated in advance |
| 5 | **Study design** | Whether data collection was planned before the tests were performed (prospective) or afterwards (retrospective) |
| 6 | **Eligibility criteria** | Inclusion and exclusion criteria for participants |
| 7 | **Basis of identification** | What made participants potentially eligible — symptoms, results of earlier tests, presence in a registry |
| 8 | **Setting and dates** | The kind of setting and the place in which those people were found, and the calendar period over which this happened |
| 9 | **Sampling** | State whether the series was enrolled consecutively, drawn at random, or assembled out of convenience |
| 10a, 10b | **Test procedures** | The index test and the reference standard each described in enough detail to be replicated |
| 11 | **Reference standard rationale** | Why this reference standard was chosen, where alternatives exist |
| 12a, 12b | **Positivity thresholds** | Definition of and rationale for cut-offs or result categories, for the index test and for the reference standard, marking which were pre-specified and which exploratory |
| 13a, 13b | **Blinding** | Whether index-test readers had the clinical information and reference-standard results, and whether reference-standard assessors had the index-test results |
| 14 | **Accuracy analysis** | Methods used to estimate or compare accuracy measures |
| 15 | **Indeterminate results** | Say what was done with readings that came back neither positive nor negative, on either test |
| 16 | **Missing data** | How missing index-test or reference-standard data were handled |
| 17 | **Variability analyses** | Any analyses of variability in accuracy (for example by subgroup), marking pre-specified versus exploratory |
| 18 | **Sample size** | The intended sample size and how it was arrived at |
| 19 | **Participant flow** | Flow of participants, presented as a diagram — required, not optional |
| 20 | **Baseline characteristics** | Who the participants were, described in demographic and in clinical terms |
| 21a, 21b | **Case mix** | Distribution of disease severity among those with the target condition, and of alternative diagnoses among those without it |
| 22 | **Test interval** | Time interval between index test and reference standard, and any clinical intervention in between |
| 23 | **Cross tabulation** | Index-test results cross-tabulated against reference-standard results (the 2x2 table), or their distribution |
| 24 | **Accuracy estimates** | Accuracy estimates reported with their precision, for example 95% confidence intervals |
| 25 | **Adverse events** | Any adverse events arising from performing either test |
| 26 | **Limitations** | What weakens the study: where bias could have entered, how much statistical uncertainty surrounds the estimates, and how far the findings can be carried to other populations |
| 27 | **Implications** | What the results mean for practice, answered against the use and the clinical role claimed for the index test at the outset |
| 28 | **Registration** | Which registry the study was entered in, and the number it was given there |
| 29 | **Protocol access** | State how a reader can obtain the complete study protocol |
| 30 | **Funding** | Who paid for the study or supported it in other ways, and what part they played in it |

### Clinical Research Application Notes

- Items 23 and 24 are the load-bearing pair: a paper that reports sensitivity and specificity without the underlying cross tabulation, or without confidence intervals, cannot be checked or pooled by anyone else.
- Item 12a is where post-hoc threshold selection hides. A cut-off chosen from the study's own ROC curve is exploratory and must be labelled as such; presenting it as pre-specified inflates the reported accuracy.
- Items 15 and 22 have no counterpart in STROBE and are easy to overlook when adapting an observational-study habit: indeterminate results silently dropped from the denominator, and an unreported delay between index test and reference standard during which the condition could change.
- The flow diagram (item 19) is required here, unlike STROBE's flow-diagram item, which only asks authors to consider one.
- QUADAS-2 is the companion appraisal tool when diagnostic accuracy studies are being synthesised rather than reported.

---

## 9. TRIPOD+AI — Prediction Model Study Condensed Checklist

**Full Name**: Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis, updated for artificial intelligence
**Version**: TRIPOD+AI 2024 (27 items; updates TRIPOD 2015 and covers regression and machine learning models alike)
**Applicable to**: Development, evaluation (validation) or updating of a multivariable model that outputs an individual-level diagnostic or prognostic prediction
**Source statement**: Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ*. 2024;385:e078378. doi:10.1136/bmj-2023-078378
**Official checklist**: https://www.tripod-statement.org/

> The wording below is an ARS paraphrase written for orientation, not the official checklist text. Report against the official TRIPOD+AI checklist; a separate TRIPOD+AI for Abstracts list covers item 2.

### Core Reporting Items

| # | Item | Description |
|---|------|------|
| 1 | **Title** | Identify the study as developing or evaluating a multivariable prediction model, and name the target population and the predicted outcome |
| 2 | **Abstract** | Follow the TRIPOD+AI for Abstracts item list |
| 3a-3c | **Background** | Healthcare context (diagnostic or prognostic) and rationale, including existing models; the target population, the intended purpose within the care pathway and the intended users; whatever is already documented about disparities in health outcomes across sociodemographic groups |
| 4 | **Objectives** | Whether the study develops a model, evaluates one, or both |
| 5a, 5b | **Data** | Sources of data given separately for development and evaluation, why they were used and how representative they are; the dates of participant accrual and, if applicable, end of follow-up |
| 6a-6c | **Participants** | Study setting and the number and location of centres; eligibility criteria; any treatments received and how they were handled |
| 7 | **Data preparation** | Pre-processing and quality checking, including whether it was applied similarly across sociodemographic groups |
| 8a-8c | **Outcome** | Definition, time horizon, how and when assessed and why chosen, and whether assessment was consistent across groups; assessor qualifications where interpretation is subjective; any blinding of outcome assessment |
| 9a-9c | **Predictors** | How the initial predictor set was chosen and any pre-selection before model building; definition and measurement of every predictor, including blinding; assessor qualifications where predictor measurement is subjective |
| 10 | **Sample size** | How the study size was arrived at, separately for development and evaluation, and why it is adequate for the question |
| 11 | **Missing data** | How missing data were handled and why any data were omitted |
| 12a-12g | **Analytical methods** | How the data were used and partitioned; how predictors were handled (functional form, rescaling, transformation); model type and rationale, every build step including hyperparameter tuning and the internal validation method; heterogeneity across clusters; **all performance measures and plots used — discrimination, calibration and clinical utility**; any model updating such as recalibration; how predictions were computed at evaluation |
| 13 | **Class imbalance** | If class-imbalance methods were used, why and how, plus any subsequent recalibration of the model or its predictions |
| 14 | **Fairness** | Approaches used to address model fairness, and their rationale |
| 15 | **Model output** | What the model outputs (probability, classification), with rationale for any classification and how thresholds were identified |
| 16 | **Training versus evaluation** | Differences between development and evaluation data in setting, eligibility, outcome and predictors |
| 17 | **Ethical approval** | The approving board or ethics committee, and the consent arrangements or waiver |
| 18a-18f | **Open science** | Funding source and funder role; conflicts of interest; where the protocol can be accessed; registration details; availability of the data; availability of the analytical code |
| 19 | **Patient and public involvement** | Involvement during design, conduct, reporting, interpretation or dissemination — or an explicit statement that there was none |
| 20a-20c | **Participants (results)** | Flow of participants including numbers with and without the outcome and a follow-up summary; characteristics overall and per data source, including key dates, predictors, sample size, event counts and missing data, reported across key demographic groups; for evaluation, comparison against the development data |
| 21 | **Model development** | Number of participants and outcome events in each analysis (development, tuning, evaluation) |
| 22 | **Model specification** | The full model — formula, code, object or API — so that predictions can be reproduced and independently evaluated, with any access or reuse restrictions stated |
| 23a, 23b | **Model performance** | Performance estimates with confidence intervals, including for key subgroups; heterogeneity of performance across clusters if examined |
| 24 | **Model updating** | Results of any updating, including the updated model and its performance |
| 25 | **Interpretation** | Overall interpretation against the objectives and previous studies, including fairness |
| 26 | **Limitations** | Non-representative sampling, sample size, overfitting, missing data, and their effect on bias, statistical uncertainty and generalisability |
| 27a-27c | **Usability in current care** | How poor-quality or unavailable input data should be handled in deployment; what interaction and level of expertise users need; next steps for applicability and generalisability |

### Clinical Research Application Notes

- Item 12e is where reporting most often stops short: discrimination (a C-statistic or AUC) is given, calibration is not. A model with good discrimination and poor calibration produces systematically wrong individual risks, so treat calibration as a required result rather than an optional plot.
- TRIPOD+AI applies to a nomogram built with ordinary logistic regression exactly as it applies to a gradient-boosted or deep-learning model. "Not an AI study" is not an exemption.
- Item 22 makes the model itself a reportable artefact. A paper that reports performance but never publishes the coefficients, code or an accessible API cannot be validated by anyone else.
- Items 3c, 7, 8a, 14 and 20b together form the equity thread new in the +AI update; they are answered as a set, not as isolated sentences.
- PROBAST (and PROBAST+AI) is the companion appraisal tool when prediction-model studies are being appraised or synthesised rather than reported.

---

## 10. Study Design → Reporting Guideline Routing

The mapping table in §1 assumes the study design is already known. For clinician-authors that assumption is frequently where the error is: the design label in the manuscript is chosen after the analysis, from habit or from the journal's section headings, rather than from what was actually done. Selecting a checklist from a mislabelled design is worse than selecting none, because it produces a confident completeness verdict against the wrong standard.

Work through the questions in order and stop at the first one that determines the answer.

**Q0 — Is this original research?**
If the work synthesises other studies, route to the PRISMA family (PRISMA 2020, PRISMA-ScR for scoping reviews, PRISMA-NMA for network meta-analysis) and stop. Editorials, narrative reviews, clinical guidelines and educational materials have no primary EQUATOR guideline; offer advisory guidance only. Otherwise continue.

**Q1 — Was the intervention assigned by the investigators?**
Assigned as part of the study protocol → Q1a. Chosen by the treating clinician on clinical grounds, even when the resulting groups are compared afterwards → this is observational; go to Q2.

**Q1a — Was the assignment randomised?**
Randomised, with results reported → **CONSORT**, plus the extension matching the design (cluster, non-inferiority/equivalence, pilot and feasibility, social and psychological interventions). Randomised but the manuscript is a protocol with no results → **SPIRIT**. Not randomised (alternate allocation, allocation by admission order, by ward, by clinician preference) → this is a non-randomised intervention study: report with **STROBE**, and expect appraisal with ROBINS-I (TREND is an alternative in behavioural-intervention journals).

**Q2 — Is the unit of reporting one patient, or a handful, followed through diagnosis and management, with no comparison group and no statistical inference?**
One patient → **CARE** (§7). A small uncontrolled series → CARE adapted per patient, stated explicitly as a case series. Anything with a comparison group is not a case report → Q3.

**Q3 — Is the primary estimate the classification performance of a test against a reference standard (sensitivity, specificity, predictive values, AUC)?**
Yes → **STARD 2015** (§8); companion QUADAS-2 when such studies are being synthesised. No → Q4.

**Q4 — Is the deliverable a multivariable model that outputs an individual-level risk or diagnostic probability?**
Yes, whether by regression, nomogram or machine learning → **TRIPOD+AI** (§9); companion PROBAST or PROBAST+AI. No → Q5.

**Q5 — Is this an analytic observational study estimating an exposure-outcome association?**
Yes → **STROBE** (§4), then Q5a for the design branch. A purely descriptive survey or prevalence estimate → STROBE, cross-sectional branch.

**Q5a — What determined who entered the study?**
Enrolment by exposure status, followed forward in time → **cohort**. Enrolment by outcome status, with exposure ascertained backwards → **case-control**. Exposure and outcome measured at the same time point → **cross-sectional**. The branch decides the wording of STROBE items 6, 12, 14 and 15, so it cannot be left open. If the description does not establish the sampling direction, ask.

**Overlays (added to the primary guideline, never replacing it):** routinely collected health data (electronic records, claims, registries) → RECORD extension of STROBE; a qualitative strand alongside → COREQ; an economic outcome → CHEERS; animal experiments → ARRIVE.

### Output

The sequence returns a primary guideline plus companion tools. Record which question settled the routing and which sentence in the scholar's description was decisive, so the scholar can see the reasoning and correct it if the description was inaccurate.

### Ambiguity rule

**If the description does not settle the current question, ask the scholar. Never infer a study design from keywords.** A guideline chosen from vocabulary rather than from what was done yields a completeness verdict that is confidently wrong, and the scholar has no way to see that the wrong standard was applied. Asking one question costs a turn; guessing costs the validity of the whole check. This rule outranks any preference for producing an answer in a single pass.

### Phrasings that do not settle the question

The following are typical of clinical manuscript descriptions and are compatible with more than one design. Treat each as a prompt for a specific follow-up question, never as a routing decision.

- *"randomly divided into two groups"* (隨機分為兩組) — may describe genuine randomisation or alternation, admission-order or clinician-preference allocation. Ask how the allocation sequence was generated and whether it was concealed before accepting CONSORT.
- *"retrospective analysis of cases treated in our department"* (回顧性分析我科病例) — compatible with a retrospective cohort, an uncontrolled case series and a cross-sectional study. Ask whether there is a comparison group and whether participants were followed over time.
- *"observation of clinical efficacy"*, *"comparison of group A and group B"* (臨床療效觀察) — usually a non-randomised intervention study rather than a trial. Ask who decided which patients received which treatment.
- *"diagnostic value of X for Y"*, *"area under the ROC curve"* — points towards STARD, but only if there is a reference standard the index test is measured against. Without one this is an association study and STROBE applies.
- *"a prediction model was established"*, *"nomogram"* (預測模型、列線圖) — TRIPOD+AI, even when the analysis is ordinary logistic regression.
- *"analysis of risk factors"* (危險因素分析) — cohort or case-control; the sampling direction in Q5a decides, not the phrase.

---

## 11. Higher Education Research Context Recommendations

### Commonly Used Guidelines Ranking

| Rank | Guideline | Common HE Usage Scenario |
|------|------|----------------|
| 1 | **PRISMA** | Systematic review of education policy, teaching strategy meta-analysis |
| 2 | **COREQ** | Teacher/student experience interviews, focus groups |
| 3 | **STROBE** | Student surveys, institutional data analysis |
| 4 | **SQUIRE** | Teaching quality improvement, QA accreditation |
| 5 | **CONSORT** | Teaching intervention experiments (less common but high impact) |

### Research Design Quick Selection

```
What is your research type?
│
├── Integrating existing research → PRISMA
│   ├── Systematic review → PRISMA 2020
│   ├── Scoping review → PRISMA-ScR
│   └── Meta-analysis → PRISMA + MOOSE
│
├── Intervention experiment → CONSORT
│   ├── Individual randomization → CONSORT 2010
│   ├── Class/school randomization → CONSORT-Cluster
│   └── Social/psychological intervention → CONSORT-SPI
│
├── Observational survey → STROBE
│   ├── Cross-sectional survey → STROBE-CS
│   ├── Follow-up study → STROBE-Cohort
│   └── Retrospective comparison → STROBE-CC
│
├── Qualitative research → COREQ
│   ├── Interviews → COREQ
│   ├── Focus groups → COREQ
│   └── Ethnography → SRQR (alternative)
│
└── Quality improvement → SQUIRE
    ├── PDSA cycle → SQUIRE 2.0
    └── QA/accreditation improvement → SQUIRE 2.0
```

---

## Quick Reference: 3 Steps to Choosing a Reporting Guideline

1. **Identify your research design**: What type of research design is your study? If the design is not already settled, work through the routing sequence in §10 rather than matching on vocabulary
2. **Check the mapping table**: Find the corresponding reporting guideline
3. **Download the checklist**: Go to [EQUATOR Network](https://www.equator-network.org/) and download the full checklist — the condensed sections in this file are orientation, not a substitute for the official item wording

> Reminder: Reporting guidelines represent the minimum standard, not the quality ceiling. Meeting the checklist doesn't guarantee high research quality, but failing to meet the checklist typically indicates deficiencies in reporting quality.
