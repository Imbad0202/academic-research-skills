## Scoring Plan Dissent

*(omitted — my Phase 2 judgement remains within the Phase 1 plan for D4)*

Wait — that placeholder is not permitted. Removing it.

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: block
trigger: "Central interdisciplinary or generalising claims are asserted without supporting evidence in the manuscript"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

**Verification outcome first.** All six references in this manuscript carry DOIs under the prefix `10.5555`. That prefix is the documented example/test prefix used in DOI and Crossref documentation, not a registered publisher prefix; a live paper's DOI does not sit there. The six journal titles are also near-variants rather than matches of journals I can identify: *Computers & Education Review* against the real *Computers & Education*, *British Journal of Educational Technology Studies* against the real *British Journal of Educational Technology*, and so on. I did not perform live DOI resolution inside this review, so I state the pattern rather than a conclusion of fabrication — but the pattern is sufficient that the editor should establish whether these six works exist before any substantive assessment proceeds. If they do not, that finding supersedes everything else below and moves this manuscript out of the revision category altogether. Interpretation second: the primary scoring home for this defect is domain accuracy (D2) and reproducibility (D1), which are not my seat; I record it here because it is also the load-bearing problem for my own dimension, and I ask the synthesizer to route it.

**Why an unresolvable reference list is a cross-disciplinary problem, not only an integrity one.** This paper imports its central construct from a tradition that is not native to educational research: perceived usefulness comes from technology-acceptance work with roots in information systems. The manuscript never names that tradition, never names its canonical source, and never identifies the discipline it is borrowing from; the phrase "technology-acceptance research" is used as if self-evident. For a reader in psychometrics, human-computer interaction, learning analytics, or higher-education policy, the entire bridge into that literature is the reference list — and the reference list does not carry weight. The manuscript's stated contribution is that it is "comparable with prior work"; comparability is precisely the claim that an outside reader cannot check here, because neither the compared literature nor the compared instrument is reachable. That combination is what took my dimension to `block` rather than `warn`. It is a repairable condition in principle: naming the framework and its origin, citing sources that resolve, and reproducing the instrument would restore the bridge.

**Protocol coherence.** Section 3.3 states that no identifying information was collected and that responses could not be linked back to individual students. Section 3.1 states that five duplicate entries were removed. As written these cannot both hold. Duplicate detection requires *something* persistent — an IP address, a cookie or session token, a device fingerprint, a timestamp-plus-response-pattern match, or a survey-platform response ID. Each of those is a quasi-identifier, and retaining one is a defensible design choice; what is not defensible is a blanket anonymity statement that omits it. This needs a direct answer, not a softening clause, because for readers in adjacent fields the ethics statement is the part they will cite as a template.

**The declined measurement route.** The literature review uses Vasquez (2020) to establish that self-report diverges from behavioral logs, then proceeds with a single self-report item and lists that as a limitation. The university already holds LMS access logs. What blocked access — ethics-approval scope, data-governance policy, technical access, cost, or a decision not to ask? Naming the barrier converts a generic limitation into information other institutions can act on. I raise this at Minor severity because it does not touch the reported association, but it is the single cheapest edit in the manuscript with the highest cross-institutional value.

**Transparency package.** A finding whose entire claimed value is transparency and comparability arrives here with no data-availability statement, no analysis code, no item wording, no preregistration, and no setting descriptors beyond "one mid-sized public university." The correlation as reported cannot be recomputed by anyone. I want to be explicit that these are additions, not re-analyses: the minimum package I would ask for is a de-identified item-level dataset or a correlation matrix with n, the six item stems and the frequency item verbatim, the analysis script, a statement of what "adapted" changed relative to the source instrument, and enough setting description (country or region, LMS platform, data-collection year, disciplinary composition) that a second site can position its own estimate against this one.

**Developmental note.** Excluding the reference question, everything I have raised is fixable without new data collection. The manuscript's inferential discipline is genuinely good and unusually well maintained for a correlational survey report — see the strengths below. The gap is between the transparency standard the paper invokes and the transparency infrastructure it supplies.

### S1: Correlational framing declared up front and held consistently
The paper states its epistemic register in the introduction and does not drift from it in the abstract, discussion, or conclusion. For an adjacent-field reader, this removes the most common source of misreading in survey-based technology research.
**Evidence Anchor**: `text: §1 — "We frame the question descriptively and correlationally."`
**Confidence**: 5 — routine assessment of claim calibration across manuscript sections.

### S2: Reverse causal pathway named explicitly rather than gestured at
Many correlational papers concede non-causality in the abstract and then argue directionally in the discussion. This one states the reverse pathway as equally consistent with the data, which is what lets an outside reader use the number without importing an unstated causal model.
**Evidence Anchor**: `text: §5 — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`
**Confidence**: 5 — direct reading of the discussion's inferential structure.

### S3: Central construct glossed in plain language before it is used
Perceived usefulness is defined conceptually at first substantive use, in ordinary language rather than through a framework acronym. This is the correct move for cross-disciplinary accessibility and it is done early.
**Evidence Anchor**: `text: §2 — "the degree to which a person believes a technology will help them perform better"`
**Confidence**: 4 — assessment of definitional accessibility for non-specialist readers.

### S4: Sensitivity stated in interpretable terms alongside interval estimates
Reporting the detectable-effect floor in plain terms, together with a confidence interval and n, lets a reader outside the subfield judge precision instead of inferring it from a p value. This is better practice than the field's median.
**Evidence Anchor**: `text: §3.4 — "greater than .80 power to detect a correlation of r >= .19 at alpha = .05"`
**Confidence**: 4 — reporting-standards screening, not a statistical adequacy judgement.

### S5: Limitations tied to specific design features, including selection into the sample
The limitations are mechanism-specific rather than boilerplate, and the voluntary-response point identifies the actual selection channel. An adjacent-field reader can act on these.
**Evidence Anchor**: `text: §6 — "response was voluntary, so students who engage more with institutional channels may be overrepresented"`
**Confidence**: 4 — evaluation of limitation specificity against reporting norms.

### W1: All six references carry a reserved example DOI prefix and none is independently locatable
Every reference resolves nominally to a `10.5555` DOI, the documented example/test prefix rather than a registered publisher prefix, and the journal titles are near-variants of real journals rather than matches. This pattern must be resolved by the editor before substantive review. If the sources do not exist, the manuscript has no literature base, its comparability claim has no referent, its instrument has no provenance, and its measurement caution (Vasquez) has no support. This defect alone, uncorrected, makes acceptance impossible.
**Severity**: Critical
**Evidence Anchor**: `text: References, all six entries — "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"`
**Confidence**: 4 — DOI-prefix and journal-title screening on a reproducibility panel; live resolution not performed within this review.

### W2: The borrowed theoretical tradition is never named or attributed to a home discipline
The claim of consistency with prior technology-acceptance research appears in the abstract, discussion, and conclusion, and is the manuscript's stated route to comparability. Yet the framework is never named, its originating discipline is never identified, and no canonical source is cited. Even if the six references were verified, a reader from an adjacent field would still be unable to locate the tradition being invoked or to judge whether r = .42 sits inside or outside its reported range. Substantiating this requires rewriting the literature review around identifiable, discipline-attributed sources.
**Severity**: Major
**Evidence Anchor**: `text: Abstract and §5 — "consistent with prior technology-acceptance research"`
**Confidence**: 4 — assessment of interdisciplinary provenance and citation adequacy.

### W3: The adapted instrument is not reproduced and the adaptation is not described
Perceived usefulness is reported as a six-item adapted scale with α = .88, but no item wording is supplied and the word adapted is never unpacked: no indication of which items were changed, dropped, reworded, or retranslated relative to the source. A reader in another field cannot determine what construct was actually measured, and no second site can reuse the instrument for the comparison the paper invites. This requires new material, not editing.
**Severity**: Major
**Evidence Anchor**: `absence: §3.2 Measures — expected verbatim wording of the six perceived-usefulness items and the frequency item plus a statement of what the adaptation changed; checked §3.2, §3.4, §4, References, and the absent appendix or supplementary-materials list`
**Confidence**: 5 — standard materials-availability screening.

### W4: Setting descriptors needed for transfer judgements are withheld
The paper positions itself as one comparable point in a distribution, but supplies no country or region, no LMS platform, no data-collection year, and no disciplinary composition of respondents. Its own limitation about generalising across "size, sector, or student profile" is therefore not actionable, since a reader cannot tell which profile this site represents. The fix is a disclosure paragraph; the core association is unaffected.
**Severity**: Minor
**Evidence Anchor**: `absence: §3.1 Design and participants — expected country or region, LMS platform, data-collection year, and disciplinary composition of respondents; checked Abstract, §3.1, §3.3, §5, and §6`
**Confidence**: 5 — routine assessment of setting reporting for comparability.

### W5: The anonymity statement and the duplicate-removal step are mutually inconsistent as written
Section 3.3 asserts that no identifying information was collected and that responses could not be linked to individual students; Section 3.1 reports removal of five duplicate entries. Duplicate identification requires a retained persistent marker, which is a quasi-identifier. Either the anonymity statement is overstated or the deduplication rule is unreported, and adjacent-field readers treating this ethics paragraph as a model would be misled. This requires a corrected ethics and data-handling description, and possibly confirmation of what the approved protocol permitted.
**Severity**: Major
**Evidence Anchor**: `text: §3.1 with §3.3 — "5 duplicate entries were removed" and "responses could not be linked back to individual students"`
**Confidence**: 5 — protocol-coherence and ethics-reporting review experience.

### W6: The barrier that prevented use of LMS log data is never named
Vasquez (2020) is used to establish that self-report diverges from logs, after which the paper proceeds on self-report and lists it as a limitation without stating what blocked the institutional route: ethics scope, data-governance policy, technical access, cost, or choice. Named, the constraint becomes reusable information for other institutions; unnamed, the limitation is decorative. The reported finding is unaffected.
**Severity**: Minor
**Evidence Anchor**: `absence: §6 Limitations — expected the named barrier that prevented access to institutional LMS log data, such as ethics scope, data-governance policy, technical access, or cost; checked §2, §3.3, §3.4, §5, and §6`
**Confidence**: 4 — practical experience negotiating LMS log-data access approvals.

### W7: No data-, code-, or preregistration availability for a manuscript whose claimed value is transparency
The contribution is framed as a transparently reported association, yet nothing in the manuscript permits independent recomputation: no de-identified dataset, no correlation matrix, no analysis script, no preregistration, and no availability statement of any kind. The claim that the reporting is transparent is therefore itself unsubstantiated, and the finding cannot function as the verifiable comparison point the paper offers it as. Meeting this requires new deliverables.
**Severity**: Major
**Evidence Anchor**: `absence: back matter following §7 — expected data-availability, code-availability, and preregistration statements; checked Abstract, §3.3, §3.4, §6, §7, and References`
**Confidence**: 5 — service on a journal data-availability screening panel.
