# Example: Cross-Disciplinary Paper Review

This example demonstrates how `academic-paper-reviewer` configures reviewer roles and handles inter-disciplinary tensions when faced with a highly cross-disciplinary paper. It simulates the review of a paper titled "Using Machine Learning to Predict University Closure Risk in Taiwan: An Institutional Research Data Approach."

---

## Simulated Paper Abstract

> **Title**: Using Machine Learning to Predict University Closure Risk in Taiwan: An Institutional Research Data Approach
>
> **Abstract**: This study develops a machine learning-based university closure risk prediction system. Using publicly available Ministry of Education data (2010-2023, covering 152 higher education institutions) as the training set, 47 feature variables were included (enrollment rate, financial indicators, faculty structure, industry-academia collaboration, etc.), comparing the predictive performance of four classification models: Random Forest, XGBoost, Logistic Regression, and SVM. The study used 12 institutions that had ceased operations or been designated for special guidance after 2018 as positive cases, employing SMOTE to address class imbalance. Results show XGBoost performed best (AUC = 0.94, F1 = 0.87), with the top five most important features being: freshman enrollment rate, current liability ratio, full-time faculty turnover rate, graduate program enrollment achievement rate, and industry-academia collaboration revenue share. This study provides an empirical basis for early warning tools for education authorities.
>
> **Keywords**: machine learning, university closure, risk prediction, institutional research, Taiwan higher education
>
> **Full text approximately 8,500 words, 52 references cited**

---

## Phase 0: Field Analysis & Persona Configuration

### Field Analysis Report

#### Paper Basic Information
- **Title**: Using Machine Learning to Predict University Closure Risk in Taiwan: An Institutional Research Data Approach
- **Full text length**: Approximately 8,500 words
- **Number of references**: 52

#### Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Higher Education Management + Data Science (dual primary) |
| Secondary Disciplines | Education Policy, Financial Management, Institutional Research (IR) |
| Research Paradigm | Quantitative — Predictive modeling |
| Methodology Type | Statistical Modeling / Machine Learning (Classification) |
| Target Journal Tier | Q2-Q3 — Cross-disciplinary papers may not be "specialized" enough in either field |
| Paper Maturity | Pre-submission — Complete structure, analysis completed |

#### Recommended Target Journals (Top 3)
1. **Studies in Higher Education** — If the higher education theoretical framework is strengthened, targeting educational policy contribution
2. **Education and Information Technologies** — Educational technology oriented, accepts ML application research
3. **Journal of Higher Education Policy and Management** — Policy management oriented, accepts quantitative research

#### Reviewer Configuration Cards

---

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: *Education and Information Technologies* (Springer) Associate Editor, specializing in educational data science and Learning Analytics, has overseen the review of multiple ML-in-education application papers over the past 5 years.
**Review Focus**:
  1. Novelty of ML application in higher education management — Such research is already abundant at the student level (student attrition prediction); is there sufficient new contribution at the institutional level
  2. Paper's actual impact — Can the model really be used by education authorities
  3. Quality of cross-disciplinary integration — Is it just a technology showcase or does it offer educational insight
**Will particularly care about**: "Whether AUC = 0.94 is overly optimistic, especially with only 12 positive cases"
**Possible blind spots**: May focus too much on the technical side, overlooking the complexity of policy application

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 (Methodology — ML Technical Expert)
**Identity Description**: Statistical learning / machine learning methodology researcher, specializing in classification models, class imbalance handling, and model evaluation, with multiple methodology articles in social science ML applications.
**Review Focus**:
  1. Class imbalance handling (12 positive vs 140 negative) — Is SMOTE the best strategy
  2. Overfitting risk — 47 features + small positive count + no visible feature selection strategy
  3. Rigor of model evaluation — Cross-validation strategy, temporal split, out-of-time validation
**Will particularly care about**: "Whether F1 = 0.87 with 12 positive cases is statistically reliable, whether bootstrapped confidence intervals are reported"
**Possible blind spots**: May not be sufficiently sensitive to the substantive meaning of university closure

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 (Domain — Institutional Research Expert)
**Identity Description**: Taiwan institutional research (IR) scholar, specializing in higher education data analysis and indicator system construction, participated in the planning of the Ministry of Education's university closure early warning mechanism.
**Review Focus**:
  1. Selection logic for the 47 feature variables — Whether key indicators are covered, whether there are omissions
  2. Data quality — Accuracy of public data, missing value handling, cross-year consistency
  3. Operational definition of "closure" — Whether the 12 positive cases include all situations (cessation, merger, restructuring)
**Will particularly care about**: "Closure is not just a financial issue; whether governance, geographic location, political factors, and other non-quantifiable indicators are considered"
**Possible blind spots**: May not be sufficiently sensitive to ML methodology details

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 (Cross-disciplinary — Public Policy / AI Ethics)
**Identity Description**: Public policy scholar, specializing in AI application ethics in the public sector, algorithmic decision fairness and transparency, researching AI's role in education policy.
**Review Focus**:
  1. Algorithmic fairness — Could the predictive model produce systematic bias against certain types of institutions (rural, vocational, indigenous colleges)
  2. Ethical considerations of policy application — If the government uses this model, what consequences would institutions labeled "high risk" face
  3. Self-fulfilling prophecy — Could the model predicting a university will close actually accelerate its closure
**Will particularly care about**: "Whether black-box models (XGBoost) are acceptable in public policy, explainability requirements"
**Possible blind spots**: May not understand model technical details well enough

---

## Phase 1: Parallel Multi-Perspective Review (Summary Version)

### Journal-Fit Review Report (Summary)

**Recommendation**: Major Revision | **Confidence**: 4/5

**Core view**: The research direction is innovative — elevating prediction from the student level to the institutional level. However, the paper is imbalanced between technical demonstration and educational insight; currently it reads more like an ML technical paper that happens to use education data, rather than an education study that happens to use ML methods. The "educational implications of feature importance" discussion needs significant strengthening.

**Key Strengths**:
1. Elevates ML prediction from student to institutional level, filling a research gap — **Evidence Anchor**: `text: §1 "predict university closure risk" at the institutional level`
2. Multi-model comparison design is sound — **Evidence Anchor**: `text: abstract "Random Forest, XGBoost, Logistic Regression, and SVM"`
3. Policy implications of the top five important features are insightful — **Evidence Anchor**: `table: Table with top-5 feature importances (enrollment rate, current liability ratio, faculty turnover, graduate enrollment achievement, industry-academia revenue share)`

**Key Weaknesses**:
1. Imbalance between technical and educational insight — Discussion almost exclusively discusses model performance, lacking dialogue with educational theory
   - **Severity**: Major | **Evidence Anchor**: `absence: §6 Discussion — expected dialogue with educational/organizational theory on feature importance; checked §6 Discussion, §7 Conclusion` | **Confidence**: 4 — journal-fit and cross-disciplinary balance within the Journal-Fit Reviewer's core remit
2. Model stability with 12 positive cases is concerning
   - **Severity**: Major | **Evidence Anchor**: `text: abstract "12 institutions that had ceased operations or been designated for special guidance after 2018"` | **Confidence**: 3 — adjacent expertise: general model-stability concern, technical depth deferred to R1
3. Lacks external model validation (e.g., using data from other countries/regions)
   - **Severity**: Minor | **Evidence Anchor**: `absence: §5 Discussion/Limitations — expected external (cross-national) validation; checked §4 Results, §5 Discussion` | **Confidence**: 4 — journal-fit generalizability judgment

---

### Methodology Review Report — R1 (Summary)

**Recommendation**: Major Revision | **Confidence**: 5/5

**Core view**: There are several important technical issues with the ML methodology that need to be resolved. Twelve positive cases are this paper's biggest methodological challenge — not insurmountable, but requiring more careful handling and more conservative claims.

**Key Strengths**:
1. Four-model comparison (RF, XGBoost, LR, SVM) design is sound — **Evidence Anchor**: `text: abstract "comparing the predictive performance of four classification models"`
2. Using SMOTE for class imbalance at least shows the authors are aware of this issue — **Evidence Anchor**: `text: abstract "employing SMOTE to address class imbalance"`
3. Using AUC rather than Accuracy as the primary metric is correct — **Evidence Anchor**: `text: abstract "XGBoost performed best (AUC = 0.94, F1 = 0.87)"`

**Key Weaknesses**:
1. **Temporal Leakage Risk** (Critical): The paper uses the complete 2010-2023 dataset for k-fold CV, but closure is a time-series event. The correct approach is temporal split (e.g., train on 2010-2019, validate on 2020-2023), otherwise the model may use "future" information
   - **Severity**: Critical | **Evidence Anchor**: `absence: §3 Methods — expected a temporal (out-of-time) split; checked §3 Methods, §4 Results` | **Confidence**: 5 — core expertise: time-series validation design for classification models
2. **SMOTE with Extremely Small Positives** (Critical): 12 positive cases with SMOTE-generated synthetic samples, but SMOTE's effectiveness is very unstable with extremely small samples. Suggest comparing SMOTE vs ADASYN vs cost-sensitive learning
   - **Severity**: Critical | **Evidence Anchor**: `text: abstract "12 institutions... employing SMOTE to address class imbalance"` | **Confidence**: 5 — core expertise: class-imbalance handling for small-N classification
3. **Overfitting** (Major): 47 features + 12 positive cases -> feature count far exceeds positive count, overfitting risk is extremely high. Must report feature selection (e.g., recursive feature elimination) results
   - **Severity**: Major | **Evidence Anchor**: `absence: §3 Methods — expected a feature-selection step reported against 47 features vs. 12 positive cases; checked §3 Methods, §4 Results` | **Confidence**: 5 — core expertise: overfitting risk in high-dimension/small-N classification
4. **Missing Confidence Intervals** (Major): AUC=0.94 but no bootstrapped 95% CI; with 12 positive cases the CI may be extremely wide
   - **Severity**: Major | **Evidence Anchor**: `absence: §4 Results — expected a bootstrapped 95% CI on AUC = 0.94; checked §4 Results, tables` | **Confidence**: 5 — core expertise: model evaluation reporting standards

**Questions for Authors**:
1. Please provide temporal split results. If there are only 12 positive cases and most closures occurred in recent years, temporal split may further reduce the positive count — how would you handle this?
2. Have you considered Leave-One-Out Cross-Validation (LOOCV) as an alternative? It may be more stable with small samples.

---

### Domain Review Report — R2 (Summary)

**Recommendation**: Minor Revision | **Confidence**: 5/5

**Core view**: From an institutional research perspective, the paper's data handling is basically sound, and the 47 features cover the main institutional indicators. However, there are several key data quality and definition issues that need clarification.

**Key Strengths**:
1. 47 feature variables cover enrollment, finance, faculty, research, and industry-academia collaboration — five major dimensions, more comprehensive than most similar studies — **Evidence Anchor**: `text: abstract "47 feature variables were included (enrollment rate, financial indicators, faculty structure, industry-academia collaboration, etc.)"`
2. Using publicly available Ministry of Education data provides high research reproducibility — **Evidence Anchor**: `text: abstract "publicly available Ministry of Education data (2010-2023, covering 152 higher education institutions)"`
3. Top five features are consistent with practical experience in institutional research — **Evidence Anchor**: `table: Table with top-5 feature importances — "freshman enrollment rate, current liability ratio, full-time faculty turnover rate, graduate program enrollment achievement rate, industry-academia collaboration revenue share"`

**Key Weaknesses**:
1. **"Closure" Definition Not Precise Enough** (Major): Do the 12 positive cases include both "cessation" and "merger"? The causes may be completely different — some mergers are strategic (such as successful merger upgrades) and should not be categorized as "closure failure"
   - **Severity**: Major | **Evidence Anchor**: `absence: §3 Methods — expected an operational definition distinguishing cessation from merger among the 12 positive cases; checked §3 Methods, Data section` | **Confidence**: 5 — core expertise: institutional research operational definitions
2. **Missing Non-Quantifiable but Critical Factors** (Major): Private university closure is often highly correlated with the following factors that are difficult to quantify — board governance quality, campus location (rural), institution type (religious, upgraded from vocational college). The paper needs to clearly indicate this in the limitations discussion
   - **Severity**: Major | **Evidence Anchor**: `absence: §5 Discussion/Limitations — expected acknowledgment of non-quantifiable factors (governance, location, institution type); checked §3 Methods feature list, §5 Discussion` | **Confidence**: 5 — core expertise: Taiwan institutional research indicator systems
3. **Cross-Year Data Consistency** (Minor): Have the indicator definitions changed from 2010-2023 (such as adjustments to Ministry of Education statistical items)? This needs explanation
   - **Severity**: Minor | **Evidence Anchor**: `absence: §3 Methods Data section — expected a cross-year definitional-consistency note for 2010-2023; checked §3 Methods, §5 Discussion/Limitations` | **Confidence**: 4 — adjacent expertise: familiar with the data source, less central than the definitional finding above

---

### Perspective Review Report — R3 (Summary)

**Recommendation**: Major Revision | **Confidence**: 3/5

**Core view**: From the perspective of AI in public policy applications, this paper touches on an important but dangerous territory — using algorithms to "flag" universities that may close. Technically it may be feasible, but ethical and policy considerations are seriously insufficient.

**Key Strengths**:
1. Willingness to explore predictive AI applications in higher education policy, at the research frontier — **Evidence Anchor**: `text: §1 Introduction "machine learning offers a new evidence base for closure-risk policy"`
2. Feature importance analysis provides a preliminary attempt at explainability — **Evidence Anchor**: `table: Table with top-5 feature importances`
3. Clear practical motivation for the research — **Evidence Anchor**: `text: abstract "provides an empirical basis for early warning tools for education authorities"`

**Key Weaknesses**:
1. **Self-Fulfilling Prophecy** (Critical): If the Ministry of Education uses this model, institutions labeled "high risk" may face — more difficult enrollment (parents and students seeing the prediction and avoiding the school), banks refusing loans, top faculty departing. The model's prediction could directly accelerate the school's closure. The paper completely fails to discuss this ethical issue. Suggest adding an "Ethical Implications" section.
   - **Severity**: Critical | **Evidence Anchor**: `absence: §5/§6 Discussion — expected an ethical-implications discussion of prediction-induced closure risk; checked §5 Discussion, §6 Conclusion` | **Confidence**: 4 — core expertise: AI ethics in public-sector policy application
2. **Algorithmic Fairness** (Major): Could the model have systematic bias against certain types of institutions? For example: rural institutions naturally have lower enrollment rates; vocational institutions have different financial structures from regular universities; indigenous colleges are established for purposes other than scale. Without considering these structural differences, the model may "punish" institutions that are already disadvantaged.
   - **Severity**: Major | **Evidence Anchor**: `absence: §3 Methods — expected a fairness/subgroup-bias analysis across institution type; checked §3 Methods, §4 Results` | **Confidence**: 4 — core expertise: algorithmic fairness in public-sector models
3. **Black Box Problem and Policy Acceptability** (Major): XGBoost's explainability is insufficient to support high-stakes policy decisions. At minimum, suggest providing SHAP (SHapley Additive exPlanations) analysis so that each institution's prediction results can be explained. In public policy, "why the model made this judgment" is more important than "whether the model is accurate."
   - **Severity**: Major | **Evidence Anchor**: `absence: §3/§4 Methods/Results — expected case-level explainability (e.g. SHAP) beyond aggregate feature importance; checked §3 Methods, §4 Results` | **Confidence**: 3 — adjacent expertise: policy-acceptability judgment, technical explainability detail deferred to R1

**Cross-Disciplinary Reading Recommendations**:
- O'Neil, C. (2016). *Weapons of Math Destruction*. Crown.
- Selbst, A.D. et al. (2019). Fairness and abstraction in sociotechnical systems. *FAT* Conference*.
- Veale, M. & Binns, R. (2017). Fairer machine learning in the real world. *Big Data & Society*.
- Williamson, B. (2021). Education policy and the digital data state. *British Educational Research Journal*.

**Questions for Authors**:
1. Suppose the Ministry of Education wanted to use your model tomorrow — how would you recommend it be used? Are there any conditions or restrictions?
2. Have you considered giving "predicted" institutions the opportunity to contest the model's results? In AI ethics, this is called the "right to contestation."

---

### Devil's Advocate Review Report (Fixed Fifth Seat)

**Editorial Recommendation**: N/A — findings only

**Core Challenge**: Predictive discrimination does not by itself establish decision utility. The paper reports AUC/F1 but does not specify an operating threshold or compare the policy costs of false positives and false negatives, so the claimed early-warning usefulness is not yet supported.

- **Severity**: Major
- **Evidence Anchor**: `absence: §4 Results/§5 Discussion — expected threshold-specific confusion costs or a decision-utility analysis; checked model-evaluation tables and policy-implications discussion`
- **Confidence**: 4 — uncertainty/scope metadata only; predictive-decision stress test
- **Bounded remedy**: Add threshold-specific error trade-offs and limit the policy-use claim to the evaluated decision context.

---

## Phase 2: Editorial Synthesis & Decision (Summary Version)

### Decision: **Major Revision**

### Consensus Analysis

**[CONSENSUS-4 across the 4 non-DA scoring reviewers]**:
1. The research direction is innovative and has practical value
2. 12 positive cases is a major methodological challenge
3. The paper needs more educational/policy-oriented discussion

**[CONSENSUS-3 across the 4 non-DA scoring reviewers]**:
1. Model evaluation needs to be more rigorous (EIC + R1 + R3)
2. Need to add ethical considerations discussion (EIC + R2 + R3)

**Disagreement 1: Technical severity**
- **R1**: Temporal leakage and SMOTE issues are Critical level
- **R2**: Data handling is basically sound (Minor Revision)
- **Resolution**: The temporal-leakage finding is retained because the cited split design directly contaminates out-of-time evaluation under the applicable model-validity criterion. R1's competence basis helps readers understand scope; confidence is uncertainty metadata and does not decide priority or severity.

**Disagreement 2: Weight of ethical issues**
- **R3**: Self-fulfilling prophecy is Critical level
- **R1/R2**: Ethics is important but doesn't affect academic quality judgment
- **Resolution**: The ethics finding is retained because the manuscript proposes a public-policy AI application yet the anchored Discussion/Conclusion lacks analysis of prediction-induced harm. The remedy is bounded to an ethical-implications discussion rather than a model change. Confidence is retained only as uncertainty/scope metadata and never governs arbitration.

### Revision Roadmap

**Priority 1 — Structural Revisions (Estimated effort: 12-16 days)**
- [ ] R1: Execute temporal split validation and report results (Source: R1-W1) — Severity: Critical | Anchor: `absence: §3 Methods — expected a temporal (out-of-time) split; checked §3 Methods, §4 Results` | Confidence: 5
- [ ] R2: Compare SMOTE vs ADASYN vs cost-sensitive learning (Source: R1-W2) — Severity: Critical | Anchor: `text: abstract "12 institutions... employing SMOTE to address class imbalance"` | Confidence: 5
- [ ] R3a: Add "Ethical Implications" section discussing the self-fulfilling prophecy risk (Source: R3-W1) — Severity: Critical | Anchor: `absence: §5/§6 Discussion — expected an ethical-implications discussion of prediction-induced closure risk; checked §5 Discussion, §6 Conclusion` | Confidence: 4
- [ ] R3b: Add a fairness/subgroup-bias analysis across institution types (Source: R3-W2) — Severity: Major | Anchor: `absence: §3 Methods — expected a fairness/subgroup-bias analysis across institution type; checked §3 Methods, §4 Results` | Confidence: 4
- [ ] R3c: Add threshold-specific false-positive/false-negative policy-cost analysis and bound the early-warning claim (Source: DA-W1) — Severity: Major | Anchor: `absence: §4 Results/§5 Discussion — expected threshold-specific confusion costs or a decision-utility analysis; checked model-evaluation tables and policy-implications discussion` | Confidence: 4
- [ ] R4: Add SHAP analysis, providing case-level explainability (Source: R3-W3) — Severity: Major | Anchor: `absence: §3/§4 Methods/Results — expected case-level explainability (e.g. SHAP) beyond aggregate feature importance; checked §3 Methods, §4 Results` | Confidence: 3
- [ ] R5: Execute feature selection, report reduced model performance (Source: R1-W3) — Severity: Major | Anchor: `absence: §3 Methods — expected a feature-selection step reported against 47 features vs. 12 positive cases; checked §3 Methods, §4 Results` | Confidence: 5

**Priority 2 — Content Supplementation (Estimated effort: 6-8 days)**
- [ ] S1: Report bootstrapped 95% CI (Source: R1-W4) — Severity: Major | Anchor: `absence: §4 Results — expected a bootstrapped 95% CI on AUC = 0.94; checked §4 Results, tables` | Confidence: 5
- [ ] S2: Precisely define "closure," distinguishing cessation from merger (Source: R2-W1) — Severity: Major | Anchor: `absence: §3 Methods — expected an operational definition distinguishing cessation from merger among the 12 positive cases; checked §3 Methods, Data section` | Confidence: 5
- [ ] S3: Strengthen educational theory dialogue on feature importance in the discussion (Source: EIC-W1) — Severity: Major | Anchor: `absence: §6 Discussion — expected dialogue with educational/organizational theory on feature importance; checked §6 Discussion, §7 Conclusion` | Confidence: 4
- [ ] S4: Discuss the absence of non-quantifiable factors in limitations (Source: R2-W2) — Severity: Major | Anchor: `absence: §5 Discussion/Limitations — expected acknowledgment of non-quantifiable factors (governance, location, institution type); checked §3 Methods feature list, §5 Discussion` | Confidence: 5
- [ ] S5: Discuss cross-year data consistency handling (Source: R2-W3) — Severity: Minor | Anchor: `absence: §3 Methods Data section — expected a cross-year definitional-consistency note for 2010-2023; checked §3 Methods, §5 Discussion/Limitations` | Confidence: 4

**Priority 3 — Text and Formatting (Estimated effort: 2 days)**
- [ ] Adjust title to highlight the predictive model's policy implications
- [ ] Add external model validation as a future research suggestion
- [ ] Standardize citation format

**Revision Deadline**: Recommended 8 weeks

---

## Pedagogical Value of This Example

### 1. Challenges of Cross-Disciplinary Reviewer Configuration

This paper involves ML technology + higher education management + public policy across three fields. The `field_analyst_agent`'s configuration strategy was:
- **R1 (Methodology)**: ML technical expert — because technical rigor is the foundation for this type of paper
- **R2 (Domain)**: Institutional research expert — because domain knowledge of the data is crucial
- **R3 (Cross-disciplinary)**: AI ethics/public policy — because this is the aspect most likely to be overlooked by the authors

If all three reviewers were higher education scholars, technical issues would be missed; if all were ML scholars, policy ethics would be overlooked.

### 2. Unique Value of Reviewer 3

In this example, R3 (AI ethics scholar) raised issues that no other reviewer mentioned:
- Self-fulfilling prophecy
- Algorithmic fairness
- Acceptability of black-box policy decisions

This is precisely the design value of `perspective_reviewer_agent` — it represents an academic community the author may not have engaged with.

### 3. Disagreement Handling Example

R1 considers the technical issues Critical, while R2 considers them Minor. The `editorial_synthesizer_agent` resolves the disagreement from the applicable criterion and evidence:
- The described split leaks later-period information into model evaluation.
- That contamination directly threatens the validity of the reported performance estimate.
- The anchored defect therefore remains Critical; reviewer confidence is transported only as uncertainty/scope metadata.

R3's ethics finding is handled the same way: its applicability follows from the proposed public-policy use, and its absence anchor shows that the manuscript does not address the resulting harm pathway. The bounded remedy is an ethical-implications discussion. Confidence neither strengthens nor softens that conclusion.

### 4. Difference from Student-Level ML Research

This paper's unique challenge is "extremely few positive cases" (only 12 closed institutions). This is fundamentally different from student-level ML research (which typically has hundreds to thousands of positive cases). R1's review therefore specifically focuses on model stability issues with small samples, rather than the "model selection" or "hyperparameter tuning" issues common in standard ML papers.
