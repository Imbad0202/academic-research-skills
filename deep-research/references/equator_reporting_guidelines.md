# EQUATOR Reporting Guidelines — Research Design and Reporting Guideline Mapping

## Purpose
Quick reference for EQUATOR Network (Enhancing the QUAlity and Transparency Of health Research) reporting guidelines. Assists the research_architect_agent in selecting the appropriate reporting checklist during the methodology design stage, and the report_compiler_agent in ensuring report completeness during the writing stage.

---

## 1. Research Design → Reporting Guideline Mapping Table

| Research Design | Primary Reporting Guideline | Applicable Scenario |
|----------|------------|---------|
| Systematic review / Meta-analysis | **PRISMA** | Literature review integrating multiple studies |
| Randomized controlled trial (RCT) | **CONSORT** | Intervention experiments with random assignment |
| Non-randomized intervention study (NRSI) | Scope-specific guideline | Do not default to STROBE; TREND applies specifically to nonrandomized evaluations of behavioral and public-health interventions |
| Observational study (cohort, case-control, cross-sectional) | **STROBE** | Non-interventional quantitative observational research |
| Qualitative research | **COREQ** or **SRQR** | COREQ for interviews/focus groups; SRQR for broader qualitative designs, including observation |
| Quality improvement study | **SQUIRE** | Systematic quality improvement project reports |
| Diagnostic accuracy study | **STARD 2015**; add **STARD-AI** for an AI-based index test | Accuracy of an index test against a reference standard; resolve prediction-model studies first via §10 |
| Prediction model study (prognostic or diagnostic) | **TRIPOD+AI** | Prediction model development, evaluation or updating, using regression or machine learning |
| Clinical practice guideline | RIGHT or AGREE Reporting Checklist | Reporting a health-care practice guideline; AGREE II is an appraisal instrument, not the reporting checklist |
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
**Adapted artifact**: Gagnier JJ, Kienle G, Altman DG, Moher D, Sox H, Riley D; CARE Group. The CARE guidelines: consensus-based clinical case reporting guideline development. *J Med Case Rep*. 2013;7:223. https://doi.org/10.1186/1752-1947-7-223
**Artifact license**: [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) as stated on the Journal of Medical Case Reports version above
**Official checklist**: https://www.care-statement.org/checklist

> **Modification note:** ARS condensed, regrouped and paraphrased the checklist embedded in the licensed Journal of Medical Case Reports artifact. This is an orientation aid, not an official CARE checklist or translation. Download the official checklist before submission and report against that.

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
| 13 | **Informed consent** | Confirmation that the patient, or a legally authorised representative where applicable, gave informed consent for publication, available on request |

### Clinical Research Application Notes

- Items 12 and 13 are the two least recoverable after the fact. Informed consent for publication has to be obtained from the patient or, where applicable, a legally authorised representative, and the patient perspective has to be collected while contact is still possible — flag both at the design stage, not at submission.
- The timeline (item 7) asks for a structured chronology as a figure or table; a chronology scattered through the narrative does not satisfy it.
- De-identification (item 5a) is a reporting requirement and an ethics requirement at once. Dates, rare-disease combinations and institution names can re-identify a patient even without a name.
- For a small uncontrolled series, CARE can be adapted per patient, but a series with a comparison group is not a case report — re-run the routing sequence in §10.

---

## 8. STARD 2015 — Diagnostic Accuracy Study Condensed Checklist

**Full Name**: Standards for Reporting Diagnostic accuracy studies
**Version**: STARD 2015 (30 items; participant flow diagram required)
**Applicable to**: Studies estimating how well one or more index tests classify participants against a reference standard
**AI extension**: [STARD-AI](https://www.equator-network.org/reporting-guidelines/the-stard-ai-reporting-guideline-for-diagnostic-accuracy-studies-using-artificial-intelligence/) adds 18 new or modified items for AI-based index tests; use it with, not instead of, the baseline STARD 2015 checklist
**Adapted artifact**: Bossuyt PM, Reitsma JB, Bruns DE, et al. STARD 2015: an updated list of essential items for reporting diagnostic accuracy studies. EQUATOR-hosted simultaneous-publication version. https://www.equator-network.org/wp-content/uploads/2015/03/STARD-2015-paper.pdf
**Artifact license**: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), stated on the first page of that exact artifact
**Official checklist**: https://www.equator-network.org/wp-content/uploads/2015/03/STARD-2015-checklist.pdf

> **Modification note:** ARS condensed, regrouped and paraphrased the licensed STARD 2015 artifact. This is an orientation aid, not an official STARD checklist or translation. Report against the official checklist.

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
| 13a, 13b | **Blinding** | Whether index-test readers had clinical information and reference-standard results, and whether reference-standard assessors had clinical information and index-test results |
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
- For an AI-based index test, apply STARD-AI together with STARD 2015. A multivariable diagnostic prediction model remains a TRIPOD+AI study instead; settle that distinction at Q3 before reaching the index-test branch at Q5.
- QUADAS-3 is the current companion appraisal tool when diagnostic accuracy studies are being synthesised rather than reported; it updates QUADAS-2. Appraisal-tool findings do not replace STARD reporting requirements.

---

## 9. TRIPOD+AI — Prediction Model Study Condensed Checklist

**Full Name**: Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis, updated for artificial intelligence
**Version**: TRIPOD+AI 2024 (27 items; updates TRIPOD 2015 and covers regression and machine learning models alike)
**Applicable to**: Development, evaluation (validation) or updating of a multivariable diagnostic or prognostic prediction model, including score, probability, risk-group and classification outputs
**Adapted artifact**: Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ*. 2024;385:e078378. https://doi.org/10.1136/bmj-2023-078378
**Artifact license**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) for the BMJ statement artifact
**Official checklist**: [TRIPOD+AI statement, Table 2](https://www.bmj.com/content/385/bmj-2023-078378#T2) (the fillable checklist is Supplementary Table 2 on that article)

> **Modification note:** ARS condensed, regrouped and paraphrased the licensed statement checklist, while retaining the official development/evaluation applicability markers. This is an orientation aid, not an official TRIPOD+AI checklist or translation. Report against the official checklist; a separate TRIPOD+AI for Abstracts list covers item 2.

In the `Applies to` column, **D** means model development and **E** means model evaluation; `D;E` applies to both.

### Core Reporting Items

| # | Applies to | Item | Description |
|---|------------|------|-------------|
| 1 | D;E | **Title** | Identify the study as developing or evaluating a multivariable prediction model, and name the target population and predicted outcome |
| 2 | D;E | **Abstract** | Follow the TRIPOD+AI for Abstracts item list |
| 3a-3c | D;E | **Background** | Healthcare context and rationale, including existing models; target population, intended purpose, care-pathway position and users; known health inequalities across sociodemographic groups |
| 4 | D;E | **Objectives** | Whether the study develops a model, evaluates one, or both |
| 5a, 5b | D;E | **Data** | Sources given separately for development and evaluation, their rationale and representativeness; accrual dates and, where applicable, end of follow-up |
| 6a-6c | D;E | **Participants** | Setting and centres; eligibility criteria; treatments received and how they were handled |
| 7 | D;E | **Data preparation** | Pre-processing and quality checking, including whether these were similar across sociodemographic groups |
| 8a-8c | D;E | **Outcome** | Definition, time horizon, assessment and rationale, including consistency across groups; assessor qualifications and demographics where interpretation is subjective; any blinding |
| 9a | D | **Initial predictors** | How the initial predictor set was chosen and any pre-selection before model building |
| 9b, 9c | D;E | **Predictor measurement** | Definition and measurement of every predictor, including blinding; assessor qualifications and demographics where interpretation is subjective |
| 10 | D;E | **Sample size** | How the study size was arrived at, separately for development and evaluation, and why it is adequate |
| 11 | D;E | **Missing data** | How missing data were handled and why any data were omitted |
| 12a-12c | D | **Development methods** | How data were used or partitioned; predictor handling; model type and rationale; all building, tuning and internal-validation steps |
| 12d, 12e | D;E | **Performance methods** | Handling of heterogeneity across clusters; all measures and plots chosen to evaluate discrimination, calibration and clinical utility, with rationale |
| 12f, 12g | E | **Evaluation and updating methods** | Any updating after evaluation, including for sociodemographic groups or settings; how evaluated predictions were calculated |
| 13 | D;E | **Class imbalance** | If class-imbalance methods were used, why and how, plus any subsequent recalibration |
| 14 | D;E | **Fairness** | Approaches used to address model fairness and their rationale |
| 15 | D | **Model output** | What the model outputs (for example a score, probability, risk group or classification), why that output was chosen, and how any thresholds were identified |
| 16 | D;E | **Development versus evaluation** | Differences between development and evaluation data in setting, eligibility, outcome and predictors |
| 17 | D;E | **Ethical approval** | The approving board or ethics committee, and the consent arrangements or waiver |
| 18a, 18b | D;E | **Funding and conflicts** | Funding source and funder role; conflicts of interest and financial disclosures |
| 18c, 18d | D;E | **Protocol and registration** | Where the protocol can be accessed, or state that no protocol was prepared; registration details, or state that the study was not registered |
| 18e, 18f | D;E | **Data and code sharing** | Availability of study data and analytical code |
| 19 | D;E | **Patient and public involvement** | Involvement during design, conduct, reporting, interpretation or dissemination — or an explicit statement that there was none |
| 20a, 20b | D;E | **Participants (results)** | Participant flow and follow-up; characteristics overall and by data source, including dates, predictors, sample size, events and missingness, with differences across key demographic groups |
| 20c | E | **Evaluation sample comparison** | Compare important predictors and outcomes in the evaluation data with the development data |
| 21 | D;E | **Analysis numbers** | Number of participants and outcome events in each development, tuning or evaluation analysis |
| 22 | D | **Model specification** | The full model — formula, code, object or API — so predictions can be reproduced and independently evaluated, with access or reuse restrictions stated |
| 23a, 23b | D;E | **Model performance** | Performance estimates with confidence intervals, including key subgroups and appropriate plots; heterogeneity across clusters if examined |
| 24 | E | **Model updating** | Results of any updating, including the updated model and its subsequent performance |
| 25 | D;E | **Interpretation** | Overall interpretation against the objectives and previous studies, including fairness |
| 26 | D;E | **Limitations** | Non-representative sampling, sample size, overfitting, missing data, and their effect on bias, statistical uncertainty and generalisability |
| 27a, 27b | D | **Use in current care** | Handling poor-quality or unavailable inputs, required user interaction and the expertise users need |
| 27c | D;E | **Next steps** | Future research needed for applicability and generalisability |

### Clinical Research Application Notes

- Item 12e specifies, in the methods, which performance measures and plots will be used and why. Item 23a is the corresponding results obligation: report the measures and plots actually used, with estimates and confidence intervals where applicable. When calibration is part of the stated performance assessment, an AUC alone does not discharge that obligation.
- TRIPOD+AI applies to a nomogram built with ordinary logistic regression exactly as it applies to a gradient-boosted or deep-learning model. "Not an AI study" is not an exemption.
- Item 22 makes the model itself a reportable artefact. A paper that reports performance but never publishes the coefficients, code or an accessible API cannot be validated by anyone else.
- Equity and fairness recur across items 3c, 5a, 7, 8a, 8b, 9c, 12f, 14, 20b, 23a, 25 and 26. Treat that cross-cutting thread as a connected account, not as a single fairness sentence.
- PROBAST+AI is the current companion appraisal tool when prediction-model studies are being appraised or synthesised rather than reported; it replaces PROBAST-2019. Appraisal does not replace TRIPOD+AI reporting.

---

## 10. Study Design → Reporting Guideline Routing

The mapping table in §1 assumes the study design is already known. For clinician-authors that assumption is frequently where the error is: the design label in the manuscript is chosen after the analysis, from habit or from the journal's section headings, rather than from what was actually done. Selecting a checklist from a mislabelled design is worse than selecting none, because it produces a confident completeness verdict against the wrong standard.

Current scope/version anchors for the branches added here: [RIGHT](https://www.equator-network.org/reporting-guidelines/right-statement/), [TREND](https://www.equator-network.org/reporting-guidelines/improving-the-reporting-quality-of-nonrandomized-evaluations-of-behavioral-and-public-health-interventions-the-trend-statement/), [STARD-AI](https://www.equator-network.org/reporting-guidelines/the-stard-ai-reporting-guideline-for-diagnostic-accuracy-studies-using-artificial-intelligence/), [QUADAS-3](https://doi.org/10.7326/ANNALS-25-02104) and [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505).

Work through the questions in order. Stop when the report's primary purpose and design establish a reporting guideline. Tools for risk-of-bias or quality appraisal are labelled separately and never repair or replace the reporting route.

**Q0 — Is the deliverable a synthesis or a clinical practice guideline?**
A systematic review or meta-analysis → the **PRISMA** family (PRISMA 2020, PRISMA-ScR for scoping reviews, PRISMA-NMA for network meta-analysis). A clinical practice guideline → **RIGHT** or the **AGREE Reporting Checklist**, selecting any applicable extension; **AGREE II** is an appraisal instrument, not the reporting guideline. Editorials, narrative reviews and educational materials have no single default EQUATOR guideline; search for a deliverable-specific guideline rather than forcing one of the study routes below. Otherwise continue.

**Q1 — Is one of these standalone research families the primary deliverable?**
Qualitative research → **COREQ** for interviews or focus groups, or **SRQR** where its broader qualitative scope fits. Quality-improvement research → **SQUIRE**. Economic evaluation → **CHEERS**. In vivo research involving live animals → **ARRIVE**. Other preclinical research without live animals does not automatically fall under ARRIVE; search EQUATOR and the target venue for an applicable guideline rather than forcing this route. Mixed-methods research → **GRAMMS**, plus the reporting guideline for each substantive component where applicable. If none applies, continue.

**Q2 — Is the unit of reporting one patient, or a handful, followed through diagnosis and management, with no comparison group and no statistical inference?**
One patient → **CARE** (§7). A small uncontrolled series → CARE adapted per patient, stated explicitly as a case series. Anything with a comparison group is not a case report → Q3.

**Q3 — Is the deliverable a multivariable prediction model study?**
Development, evaluation or updating of a diagnostic or prognostic model that outputs an individual score, probability, risk group or classification → **TRIPOD+AI** (§9), whether the method is regression, a nomogram or machine learning. **PROBAST+AI** is the separate current appraisal tool. Otherwise continue to Q4.

**Q4 — Is the primary study question an estimate of an intervention's effects or harms?**
Yes → Q4a, regardless of whether allocation was controlled by investigators, clinicians, policy, availability or participant choice. No — the study is not evaluating an intervention effect → Q5.

**Q4a — Was assignment randomised?**
Randomised, with results reported → **CONSORT**, plus the extension matching the design. Randomised but the manuscript is a protocol with no results → **SPIRIT**. Not randomised (for example alternate allocation, admission order, ward or clinician preference, routine-care policy, availability or participant choice) → this is a **non-randomised intervention study (NRSI)**. An NRSI may use an observational design, but do not default to STROBE merely because allocation was not random: STROBE can describe an applicable underlying observational design but does not cover intervention-specific reporting. **TREND** is a reporting option only for nonrandomized evaluations of behavioral and public-health interventions. For other NRSI, select a design- and domain-specific reporting guideline from EQUATOR or the target venue; if none is established, leave the route unresolved and ask rather than treating STROBE as a complete intervention-reporting answer. **ROBINS-I** is an appraisal tool for NRSI and is not a reporting guideline.

**Q5 — Is the primary estimate the accuracy of an index test against a reference standard?**
Yes → **STARD 2015** (§8); for an AI-based index test, use STARD 2015 together with the **STARD-AI** extension (or an integrated checklist containing both the baseline and the 18 new or modified AI items). **QUADAS-3** is the separate current appraisal tool when such studies are assessed or synthesised. No → Q6.

**Q6 — Is this a non-interventional cohort, case-control or cross-sectional study?**
This includes reports of exposure-outcome associations, incidence or natural history, and cross-sectional prevalence. Yes → **STROBE** (§4), then Q6a. No → search EQUATOR for the actual study type; do not force a nearest-looking guideline.

**Q6a — What determined who entered the study?**
A defined population selected independently of outcome status, with outcome occurrence or risk ascertained over time → **cohort**, whether exposures are compared or incidence alone is described, and whether the data were collected prospectively or reconstructed retrospectively from existing records. Entry or sampling determined by outcome/case status, with prior exposure compared between cases and controls → **case-control**. Exposure and outcome assessed for a sampled population at a defined time or interval, without longitudinal ascertainment of new outcome occurrence → **cross-sectional**. The branch decides the wording of STROBE items 6, 12, 14 and 15, so it cannot be left open. If the description does not establish the sampling basis and time structure, ask.

**Extensions and secondary components:** routinely collected health data in a STROBE-routed study may add RECORD; a substantive qualitative or economic component may additionally require COREQ/SRQR or CHEERS. These additions do not turn a standalone qualitative, economic, quality-improvement or animal study into an overlay on an unrelated guideline.

### Output

The sequence returns a primary reporting guideline and separately labelled companion appraisal tools, if any. Record which question settled the routing and which sentence in the scholar's description was decisive, so the scholar can see the reasoning and correct it if the description was inaccurate.

### Ambiguity rule

**If the description does not settle the current question, ask the scholar. Never infer a study design from keywords.** A guideline chosen from vocabulary rather than from what was done yields a completeness verdict that is confidently wrong. Routing remains undetermined until the scholar supplies the design fact that distinguishes the branches.

### Phrasings that do not settle the question

The following are typical of clinical manuscript descriptions and are compatible with more than one design. Treat each as a prompt for a specific follow-up question, never as a routing decision.

- *"randomly divided into two groups"* (隨機分為兩組) — may describe genuine randomisation or alternation, admission-order or clinician-preference allocation. Ask how the allocation sequence was generated and whether it was concealed before accepting CONSORT.
- *"retrospective analysis of cases treated in our department"* (回顧性分析我科病例) — compatible with a retrospective cohort, an uncontrolled case series and a cross-sectional study. Ask whether there is a comparison group and whether participants were followed over time.
- *"observation of clinical efficacy"*, *"comparison of group A and group B"* (臨床療效觀察) — usually a non-randomised intervention study rather than a trial. Ask who decided which patients received which treatment.
- *"diagnostic value of X for Y"*, *"area under the ROC curve"* — does not distinguish a prediction-model study from an index-test accuracy study. Ask whether the deliverable is a multivariable model and whether an index test is compared with a reference standard; Q3 must be resolved before Q5.
- *"a prediction model was established"*, *"nomogram"* (預測模型、列線圖) — TRIPOD+AI, even when the analysis is ordinary logistic regression.
- *"analysis of risk factors"* (危險因素分析) — cohort or case-control; the sampling direction in Q6a decides, not the phrase.

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

Use the canonical sequence in §10. Higher-education topic labels do not change its decisions: an intervention is not CONSORT-routed until random assignment is established, and “retrospective comparison” does not establish cohort versus case-control sampling. The ranking above describes frequency of use in higher-education research; it is not a second routing system.

---

## Quick Reference: 3 Steps to Choosing a Reporting Guideline

1. **Identify your research design**: What type of research design is your study? If the design is not already settled, work through the routing sequence in §10 rather than matching on vocabulary
2. **Check the mapping table**: Find the corresponding reporting guideline
3. **Download the checklist**: Go to [EQUATOR Network](https://www.equator-network.org/) and download the full checklist — the condensed sections in this file are orientation, not a substitute for the official item wording

> Reminder: Reporting guidelines represent the minimum standard, not the quality ceiling. Meeting the checklist doesn't guarantee high research quality, but failing to meet the checklist typically indicates deficiencies in reporting quality.
