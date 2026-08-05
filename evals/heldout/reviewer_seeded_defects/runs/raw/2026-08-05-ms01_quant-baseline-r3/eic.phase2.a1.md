contract_role: eic

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: block
trigger: "a competent reader cannot reliably determine what was done, in what order, or what the reported numbers refer to"

### D6: venue_fit_and_contribution
score: block
block_class: repairable
trigger: "the significance claimed to the readership materially exceeds what the manuscript actually establishes"

## Review Body

I read this submission first as an editor deciding whether it earns space in a learning-analytics research journal, and second as the seat responsible for whether the manuscript is organised and reported well enough for readers to use. On both counts the submission fails its own screen at present, and it fails in ways that a reader can detect without any re-analysis.

The screening problem is that the manuscript's headline claim does not survive contact with its own Results section. The Abstract advertises a correlation of *r* = .42 between dashboard engagement and retention; §4.2 reports *r* = .24. Those are not two framings of one finding, they are two different findings, and the Abstract's version is nearly twice the effect the paper actually reports. The same Abstract describes "a self-report survey collected from 142 students," while §4.1 reports 87 respondents answering the perceived-control item. A reader who takes the Abstract at face value — which is what most readers, and every citation-chasing secondary author, will do — will carry away numbers this paper does not support. Independently of everything else, that alone precludes publication until the authors state which value is the analysis and correct the other.

The second screening problem is scope self-refutation. §1 announces that the authors "are careful throughout to distinguish the pattern in the data from the causal story that might explain it," and §2 approvingly cites a critical audit of causal language in correlational analytics. Four pages later, §5 opens by asserting that "dashboard engagement improved course retention" and that increasing engagement "raises the probability" of completion, and §6 tells "higher education institutions worldwide" that dashboard investment is "a dependable strategy" and "a practical and generalizable lever." A cross-sectional, single-course, volunteer-sample association of *r* ≈ .24 cannot license a causal verb, a worldwide reference class, or the word "dependable." A journal cannot publish a paper whose Conclusion refutes its own Introduction's methodological self-description, and the mismatch is not a stylistic slip: the causal, generalising version *is* the manuscript's contribution claim.

That leads to the contribution question, which is where my mandatory dimension sits. The field already has synthesis-level statements that student-facing dashboard effects on outcomes are small, heterogeneous, and design-dependent. This manuscript cites none of them — the reference list contains no systematic review or meta-analysis of dashboard effects — and so never answers the question an editor must answer: what does one more single-course *r* ≈ .24 add to a literature that already says "small, heterogeneous, design-dependent"? There is a defensible answer available to the authors. The pairing of behavioural engagement with a regulatory self-report in one instrumented course, honestly scoped to that course, is a legitimate if modest brick. But that case has to be built against the syntheses, and the manuscript instead reaches for institutional-deployment prescription. As currently framed, the practitioner-directed prescriptions of §6 outrun the evidence base by a wide margin; the honestly scoped version of this paper is a research contribution of narrow but real interest, whereas the version submitted reads as advocacy that a practitioner outlet would publish and a research journal cannot. I score D6 `block` rather than `fatal` because the topic is squarely in scope and new data are reported: the contribution case needs rebuilding, not abandoning.

On organisation and reporting, the manuscript is conventionally structured and mostly followable at the paragraph level, but its numbers do not reconcile with each other. §4.3 states that all 142 students were classified into engagement groups and reports *t*(140), while Table 2 shows subgroups of 66 and 61 (127). The same paragraph reports *t*(156) for a comparison on an item answered by 87 respondents in a 142-student analytic sample, and reports *t*(140) = 1.31 with *p* = .008 while describing the difference as not reaching a comparable level. I am not the methodology seat and I am not adjudicating which computation is correct, but I will state the editorial consequence plainly rather than filing it as "authors should check their arithmetic": at least one reported degrees-of-freedom value cannot correspond to any sample described in §3, and a *t* of 1.31 cannot yield *p* = .008 on any sample size, so these are not transcription ambiguities to be resolved by preference — some of the reported values are unobtainable from the described data. Likewise, the ten-respondent clarity item reported inline in §4.1 with M = 3.00 and SD = 0.10 cannot arise from ten integer responses on a 1–5 scale, since the smallest non-zero standard deviation available there is an order of magnitude larger. A reader therefore cannot determine what the reported numbers refer to, which is exactly my block condition for this dimension. Two further housekeeping matters compound it: Table 1 reports and §4.3 analyses a final exam score that §3.3 never defines as a measure, and nine of the sixteen listed references are never cited in the text.

I also flag the research-ethics disclosure rather than delegating it to a checklist. §3.2 states that consent covered the survey and that "Students were not informed that their dashboard activity data would be analyzed for this study." The manuscript contains no ethics-approval statement, no protocol reference, and no data availability, funding, or conflict-of-interest statements. If approval exists and covers secondary use of log data, this is a disclosure gap the authors can close at revision. If it does not, the analysis of unconsented behavioural traces is not curable by rewriting, and my score on D6 would not be the operative constraint. Authors should also confirm that naming Meridian State University is compatible with the venue's review-anonymity policy.

### S1: Measurement critique is unusually candid and self-implicating
The Literature Review does not shield the study's own operationalisation. It states plainly that click-based proxies conflate distinct behaviours and explicitly includes "the present one" among the studies that infer engagement from coarse proxies. This is the kind of pre-emptive honesty an editor rarely sees, and it gives reviewers a shared vocabulary for the limitation instead of forcing them to introduce it.
**Evidence Anchor**: text: §2 "a student who opens the dashboard once and studies it carefully is scored below one who opens it repeatedly without reflection"

### S2: Operational definitions are specific enough to be repeated
The sessionisation rule, the dichotomous retention coding including the enrolled-but-absent case, and the exact wording of the perceived-control item are all stated. A subsequent team could reproduce these variable constructions on another LMS without contacting the authors, which is more than most dashboard submissions offer.
**Evidence Anchor**: text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"

### S3: Analytic simplifications are named rather than hidden
The median split is labelled as a coarse simplification adopted for interpretability rather than efficiency, and §3.1 states outright that the cross-sectional design confines all measures to a single term. This disclosure discipline in the Methods is genuine, which makes the Discussion's causal turn all the more repairable: the authors clearly know the constraint.
**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure"

### S4: Conventional structure with a locatable limitations section
Sectioning follows standard IMRaD order with numbered subsections, a keyword block, a dedicated limitations subsection, and tables that are captioned and referenced in text. The skeleton the venue expects is present, so the required revisions are to content and reporting rather than to architecture.
**Evidence Anchor**: text: §5.1 "Several limitations qualify these findings."

### W1: Abstract reports a primary effect size the Results contradict
The Abstract states *r* = .42 for the engagement–retention association; §4.2 reports *r* = .24, *p* = .004. No reconciliation, sensitivity analysis, or alternative specification is offered anywhere that would make both values coexist. The Abstract additionally implies survey data from all 142 students, whereas §4.1 reports 87 respondents on the perceived-control item. Because the Abstract is the surface most readers and citing authors consume, publishing it as written would enter an unsupported effect size into the literature; uncorrected, the paper's headline quantitative claim cannot be identified at all, which is sufficient on its own to make acceptance impossible.
**Severity**: Critical
**Evidence Anchor**: text: §Abstract, §4.2 "Dashboard engagement correlated positively with retention (r = .42)" and "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — direct comparison of Abstract and Results text, no inference required

### W2: Conclusion asserts causation and worldwide generalisability that the design and the Introduction both disclaim
§5 states the engagement–retention relation as improvement and as raising completion probability; §6 escalates to a prescription for institutions worldwide, calling dashboard investment "dependable" and "generalizable." The evidence is one term, one course, one dashboard design, a volunteer sample, and a modest correlation. The manuscript's own §1 commits to separating pattern from causal story, and §2 cites a critical audit of exactly this practice, so the Conclusion contradicts the paper's stated methodology as well as its data. Uncorrected, the claim the paper exists to advance is invalid, independent of every reporting error catalogued below.
**Severity**: Critical
**Evidence Anchor**: text: §5, §6 "dashboard engagement improved course retention" and "is associated with, and raises, course retention among undergraduates"
**Confidence**: 5 — the design description and the conclusion are both explicit and mutually exclusive

### W3: No positioning against the existing synthesis literature on student-facing dashboards
The Literature Review engages only individual primary studies and commentary. It cites no systematic review or meta-analysis of dashboard effects on outcomes, so the manuscript never states what its single-course association adds to a synthesis-level baseline that already characterises such effects as small, heterogeneous, and design-dependent. Without that comparison an editor cannot evaluate increment, and the reader cannot tell whether *r* ≈ .24 confirms, refines, or sits below what is already known. The core empirical material survives, but the contribution case requires substantial rewriting and repositioning.
**Severity**: Major
**Evidence Anchor**: absence: §2 Literature Review and References — expected citation of at least one systematic review or meta-analysis of student-facing dashboard effects on academic outcomes; checked §1 Introduction, §2 Literature Review, §5 Discussion, References
**Confidence**: 4 — a decade in this review community plus a full pass over the sixteen listed references

### W4: Table 2 subgroup sizes contradict the sample the text says was analysed
§4.3 states that all 142 students in the primary analytic sample were classified into engagement groups and reports a test with 140 degrees of freedom, but Table 2 lists n = 66 and n = 61, totalling 127. Fifteen students are unaccounted for, with no exclusion rule stated. A reader cannot tell whether the tabled means describe the analysed sample or a subset, so the exam comparison as displayed is not interpretable. Correction may require re-running the comparison, but the retention finding is untouched.
**Severity**: Major
**Evidence Anchor**: table: Table 2 "Final exam comparison by engagement group" — subgroup n values 66 and 61 against the 142 stated in §4.3
**Confidence**: 5 — arithmetic on the table against the text of the same paragraph

### W5: Reported test statistics cannot be produced by the described samples
The perceived-control comparison is reported as *t*(156) = 3.02 although the analytic sample is 142 and only 87 respondents answered the item; no sample in the manuscript yields 156 degrees of freedom. The exam comparison is reported as *t*(140) = 1.31, *p* = .008 and simultaneously described as not reaching a comparable level, yet that *t* value corresponds to *p* ≈ .19 at those degrees of freedom while *p* = .008 would be significant at the stated alpha. At least one number in each pair is wrong, and the second-of-two headline claims — that engaged students perceive more control — rests on the first pair. The methodology seat should determine which values are recoverable; editorially, the reported statistics cannot stand as printed.
**Severity**: Major
**Evidence Anchor**: text: §4.3 "t(156) = 3.02, p = .003" and "t(140) = 1.31, p = .008"
**Confidence**: 4 — routine editorial screening of degrees of freedom and *p*-value plausibility, not a re-analysis of the data

### W6: Behavioural log data analysed without participant notice, with no ethics approval statement
§3.2 states that consent was obtained for the survey and that students were not informed their dashboard activity data would be analysed for the study. The manuscript contains no ethics-approval or protocol statement anywhere, so a reader cannot establish that secondary analysis of identifiable LMS traces was reviewed or permitted. This is not a formatting omission: if approval covering log analysis exists, disclosure closes the gap at revision; if it does not, no rewriting makes the analysis publishable. I record it as Major on the assumption that documentation exists and was simply omitted, and flag explicitly that the finding escalates if it does not.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."
**Confidence**: 4 — clear on what the manuscript discloses, uncertain only about documentation held off-page

### W7: Nine of sixteen references are never cited in the text
Ainsworth & Devi (2018), Berange (2021), Delacroix & Ohno (2022), Halloran (2020), Kessler & Amadou (2019), Montez (2022), Prakash & Tolliver (2021), Solberg & Whitfield (2018), and Wexler & Ojo (2020) appear only in the reference list. Uncited entries inflate the apparent depth of engagement with the literature and violate standard referencing convention. Fixing this changes no claim, but it must be fixed before typesetting, and several of these entries look like the material that should have supported the positioning missing in W3.
**Severity**: Minor
**Evidence Anchor**: absence: References list checked against in-text citation strings — expected an in-text citation for each listed reference; checked §1 Introduction, §2 Literature Review, §3 Methods, §4 Results, §5 Discussion, §6 Conclusion
**Confidence**: 5 — enumerated the reference list against every in-text citation

### W8: Final exam score is analysed and tabled but never defined as a measure
§3.3 defines dashboard engagement, retention, perceived control, and the clarity item, but not final exam score, which nonetheless appears in Table 1 and carries the whole of §4.3. A reader cannot tell whether it is the same instrument as the "final assessment" used to code retention, how it was scaled beyond the 0–100 label, or whether non-retained students contribute scores. This limits interpretation of a secondary analysis without disturbing the primary claim.
**Severity**: Minor
**Evidence Anchor**: absence: §3.3 Measures — expected an operational definition of the final exam score variable reported in Table 1; checked §3.1 Design and Setting, §3.3 Measures, §3.4 Analysis, Table 1
**Confidence**: 4 — full read of the Methods section for any definition of the variable

### W9: Secondary clarity item is presented as inline raw output with impossible dispersion
§4.1 reports the ten-student clarity item as an inline semicolon-delimited string rather than as prose or a table, states no purpose for the item, and never revisits it. The reported SD of 0.10 is unobtainable from ten integer responses on a 1–5 scale, where the smallest non-zero standard deviation is roughly 0.33. Precision is also inconsistent across the section, with perceived control given to three decimals against a two-decimal SD. No core claim depends on this item, but it reads as unedited output and warrants either proper reporting or removal.
**Severity**: Minor
**Evidence Anchor**: text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Confidence**: 4 — inspection of the reported values against the stated integer response scale

### W10: Venue-required declarations are absent
The manuscript carries no data availability statement, no funding declaration, and no conflict-of-interest statement. Research journals in this field require all three at submission, and the data availability statement matters more than usual here because the reported statistics cannot currently be reconciled with the described samples. These are administrative additions that change no claim.
**Severity**: Minor
**Evidence Anchor**: absence: Front and back matter of the submission — expected data availability, funding, and conflict-of-interest declarations; checked Abstract, §3 Methods, §5.1 Limitations, §6 Conclusion, References
**Confidence**: 5 — checked every section for the standard declaration block
