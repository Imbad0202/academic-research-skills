## Dimension Scores

contract_role: perspective

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: not_assessed

### D4: cross_disciplinary_relevance

score: warn
trigger: "Core constructs are used without operational definition, or definitions drift between sections"

The manuscript's scope discipline is genuinely good — causality is disavowed in the abstract, discussion, and conclusion, and the limitations section ties inference back to sample and design. That keeps it well clear of my block threshold, which required unqualified export of findings to unsampled populations, settings, or causal questions. What it does not clear is the warn threshold. The dependent construct is named four different things across the paper ("self-reported frequency of use", "perceived use", "reported engagement", "LMS engagement"), with the widest of those four appearing in the abstract's summative sentence, where an adjacent-field reader is most likely to stop. And the referent of the measured behaviour is never specified: no platform is named, no statement appears about which LMS functions are compulsory, and the three-week collection window is never located in the academic calendar. Inside the technology-acceptance literature "LMS use" is a familiar shorthand that carries these assumptions implicitly. Outside it — for an institutional research office, a learning-analytics group, or anyone from a field that treats access behaviour as a time series — the shorthand does not survive the border crossing, and r = .42 becomes uninterpretable rather than merely modest.

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

I read adoption papers as an operator: my question is whether someone at another institution could interpret this finding, situate it against their own environment, or act on it. On the first two counts the paper is partway there; on the third it is not, and the gap is mostly a translation gap rather than a defect of the underlying analysis.

What the paper does well deserves saying first, because it is unusual. The authors resist the standard inflation of a correlational survey into an acceptance model. They state the question narrowly, keep correlational language throughout, define perceived usefulness in ordinary words rather than by citation alone, report the coefficient with a confidence interval and a rank-order robustness check, and include a prospective power statement rather than a post-hoc one. The limitations section names the self-report/log divergence problem and cites the relevant source rather than burying it. A reader from an adjacent field can tell what kind of claim is on offer and roughly how much weight it bears.

Where the paper stops short is in describing the object of measurement. Three things an outside reader needs are absent. First, which platform, and which of its functions are mandatory. If assignment submission, grade release, or attendance runs exclusively through this system, then a substantial share of reported access frequency is compelled, and perceived usefulness cannot explain that share in the way section 5 implies. This is one paragraph of text, but it changes the reading of the entire correlation, and its absence is not a matter of style. Second, where in the semester the three weeks sat. LMS access is bursty and deadline-driven; a retrospective "typical week" estimate presumes a stationarity that the behaviour does not have, and if collection fell near an assessment cluster then perceived usefulness and reported frequency can move together for structural reasons that have nothing to do with acceptance. The paper actually names "assessment schedules" as an influence on reported use, which makes the failure to locate its own window more conspicuous, not less. Third, what the six adapted items asked. The construct is defined conceptually in section 2 but its operational content is invisible, so a reader in an adjacent field cannot judge whether "usefulness" here means grade-relevant utility, convenience, or something else.

On the log-linkage question I want to be explicit about my own bias. I build trace-data pipelines for a living and I am professionally comfortable with consented linkage in ways students may not be, so I am not asking the authors to have surveilled their sample. Student *perception* of engagement is a legitimate construct on its own terms, and this paper is entitled to measure it. My objection is narrower and is about framing: section 3.3 records a deliberate design choice (no identifiers, no linkage possible) and section 6 records its consequence (self-report cannot be validated against traces) without connecting the two. The limitation reads as circumstance when it is a choice with a stated cost. Naming it as a tradeoff, and briefly sketching the consent pathway that would have permitted linkage, would let a reader at another institution decide the tradeoff differently rather than inherit it silently.

Finally, the onboarding implication. "Onboarding which helps students see concrete usefulness" is hedged appropriately, but it is not a specification anyone can cost or schedule. The study measured usefulness as a single mean, so it cannot say which facet to target, for which student segment, or at what point in the enrolment cycle. Either the recommendation should be narrowed to what the data licenses, or it should be recast as a research agenda rather than a practice suggestion. This is the smallest of my findings, but it is the one that determines whether a practitioner reader gets anything from the paper beyond a comparison point.

### S1: Causal restraint is maintained consistently across abstract, discussion, and conclusion

The reverse-causation pathway is named explicitly and attributed, and no section quietly upgrades the association. For an adjacent-field reader this is the single most important accessibility feature the paper has, because it prevents the most common misreading of a survey correlation.

**Evidence Anchor**: text: Abstract — "should not be read as causal, given the cross-sectional design"

### S2: The central construct is glossed in plain language before technical use

Perceived usefulness is given an ordinary-language definition in the literature review rather than left as a citation-bound term of art, which lets a reader without technology-acceptance training follow the rest of the paper.

**Evidence Anchor**: text: §2 — "the degree to which a person believes a technology will help them perform better"

### S3: Statistical reporting is legible to readers outside the home subfield

The coefficient arrives with an interval, an n, a rank-order robustness check, and a prospective sensitivity statement. An adjacent-field reader can locate this estimate against their own without recomputation.

**Evidence Anchor**: text: §3.4 — "greater than .80 power to detect a correlation of r >= .19 at alpha = .05"

### S4: Generality is bounded explicitly rather than left to the reader to infer

The limitations section states the replication requirement in a form an outside reader can act on, instead of relying on a generic "further research is needed" formula.

**Evidence Anchor**: text: §6 — "replication across settings would be needed before treating the association as general"

### W1: The dependent construct drifts from "self-reported access frequency" to "LMS engagement" at the abstract's summary sentence

Section 2 commits carefully to treating the measure as perceived rather than behavioural, and the methods operationalise it as a single access-frequency item. The abstract's closing sentence then reports the finding in terms of "engagement", a construct that in education research and learning analytics spans behavioural, cognitive, and affective components. Design scope and site scope are qualified in that same abstract; construct scope is not. An adjacent-field reader who reads only the abstract will import the wider construct, and the paper's own careful framing does not reach them.

**Severity**: Major
**Evidence Anchor**: text: Abstract — "perceived usefulness tracks with LMS engagement among undergraduates"; §2 — "an indicator of perceived use rather than a behavioral count"
**Confidence**: 5 — I work daily with the behavioural/cognitive/affective engagement distinction in institutional reporting, and the mismatch here is textual rather than interpretive.

### W2: Neither the platform nor the compulsory status of any LMS function is stated, so compelled use cannot be distinguished from chosen use

Reported access frequency in a system that exclusively hosts assignment submission, grade release, or attendance is partly a workflow artefact. Whether that is the case here is unknowable from the manuscript. The paper's Results section gestures at "course requirements" as residual variance, but a compulsory-function disclosure is a different matter: it determines whether a share of the dependent variable is structurally fixed rather than perception-sensitive. Without it, a reader at another institution cannot tell whether this correlation is comparable to their own environment, and the discussion's acceptance-flavoured reading of the association is not checkable.

**Severity**: Major
**Evidence Anchor**: absence: §3.1 and §3.2 — expected identification of the LMS platform and a statement of which platform functions are compulsory for undergraduates; checked Abstract, §1 Introduction, §3.1 Design and participants, §3.2 Measures, §5 Discussion, §6 Limitations
**Confidence**: 5 — I have run a campus-wide LMS onboarding redesign and this is the first question any operator asks of a use-frequency figure.

### W3: The collection window is never located in the semester, and a "typical week" estimate presumes stationarity that LMS access does not have

Access behaviour spikes at assessment deadlines and troughs mid-term. A retrospective single-item estimate of a "typical week", gathered in an unlocated three-week window, is a weak summary statistic for a cyclical process, and if the window overlapped an assessment cluster then perceived usefulness and reported frequency plausibly shift together for reasons exogenous to acceptance. Fixing this requires no new data — only disclosure of the window's position and a paragraph acknowledging the non-stationarity assumption — but until that appears, readers from any field that treats access as a time series cannot judge what the estimate summarises.

**Severity**: Major
**Evidence Anchor**: text: §3.1 — "distributed through the institution's course-announcement channel over a three-week window"; §3.2 — "how often the respondent accessed the LMS in a typical week"
**Confidence**: 4 — strong on the burstiness of LMS traces from pipeline work; the magnitude of the resulting bias here is plausible but unquantified from the text alone.

### W4: The six adapted items are not reproduced and the nature of the adaptation is unreported

An adjacent-field reader can see the conceptual definition of perceived usefulness but not its operational content, and cannot tell what "adapted" changed relative to the source instrument. The reported alpha establishes internal consistency but not what the items are about. This does not affect the paper's core claim, and the conceptual gloss in section 2 partly compensates, but reproducing the stems in an appendix would let readers outside technology acceptance judge construct content for themselves.

**Severity**: Minor
**Evidence Anchor**: absence: §3.2 Measures — expected the six adapted item stems plus a description of what the adaptation changed from Costa and Wren (2019); checked §3.2, §3.4, §4, and the reference list
**Confidence**: 4 — routine expectation for instrument reuse in cross-field reading; I am not assessing psychometric adequacy, which is another reviewer's remit.

### W5: The onboarding implication is not specifiable at the resolution an institution could act on

The recommendation names no usefulness facet, no student segment, and no point in the enrolment cycle, and the study's single-mean measurement of usefulness cannot supply any of those. The hedging is honest, but hedged unactionability is still unactionable. Either narrow the claim to what the data licenses, or reframe it as a design question for future work.

**Severity**: Minor
**Evidence Anchor**: text: §5 — "LMS onboarding which helps students see concrete usefulness"
**Confidence**: 5 — this is exactly the specification level at which institutional interventions are costed and scheduled.

### W6: A deliberate anonymity choice is reported as a design fact and its measurement consequence as an unavoidable limitation, with the tradeoff never connected

The paper records that no identifiers were collected and separately records that self-report cannot be checked against behavioural traces. Both statements are correct, but the causal link between them is left for the reader to assemble, which makes the limitation read as circumstance rather than as the price of a defensible choice. I am not arguing the choice was wrong — consented linkage carries real surveillance costs, and perceived use is a legitimate construct. I am arguing that stating the tradeoff, including the consent pathway that would have permitted linkage, lets readers at other institutions weigh it themselves rather than inherit it.

**Severity**: Minor
**Evidence Anchor**: text: §3.3 — "No identifying information was collected, and responses could not be linked back to individual students"
**Confidence**: 4 — I co-chair an institutional data-ethics working group and have written both sides of this tradeoff; the disciplinary bias toward linkage is mine and I have flagged it.
