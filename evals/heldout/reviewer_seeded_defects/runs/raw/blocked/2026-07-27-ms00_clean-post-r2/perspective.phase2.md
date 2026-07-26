## Scoring Plan Dissent

*(omitted — Phase 1 plan holds)*

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
score: warn
trigger: "specific constructs, instruments, or technical vocabulary go undefined at first use, or outward-facing implications are stated with insufficient hedging and only partial linkage to the reported evidence"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript from a learning analytics and institutional data governance position — that is, as the kind of reader who sits one field over from technology-acceptance research and who would be a plausible secondary consumer of this finding. My question is not whether the correlation is correctly estimated (another seat owns that) but whether an adjacent-field reader can tell what was actually measured, what the finding licenses outside the room it was produced in, and what about the setting bounds its transfer.

The paper's discipline is real and I want to credit it precisely rather than generically. Its scope conditions are not decorative; they are specific, repeated, and placed where a reader will actually meet them. The reverse-causality pathway is named in the body, not deferred to a limitations paragraph. The construct at the centre of the study is glossed in plain language at first use. The self-report-versus-trace-data gap is surfaced in the literature review rather than smuggled in at the end. Taken together, these make the paper unusually legible for an outsider, and they mean the standard cross-field failure mode — an insider result quietly inflated into a general claim — is largely absent.

What remains, and what my score turns on, is a narrower and more stubborn problem: the paper's outward-facing vocabulary does not match its measurement. The measured dependent variable is a single self-reported weekly access-frequency item. The vocabulary carried in the title's vicinity, the abstract's opening and closing sentences, and the framing of §1 is *engagement*. In the field I work in, "engagement" is not a loose synonym for login count — the last decade of learning analytics has been substantially devoted to establishing that raw access frequency is a poor proxy for it, because a student who opens the LMS six times to check whether a grade posted is not more engaged than one who opens it twice and works for an hour. A reader arriving from learning analytics, institutional research, or student-success work will read "LMS engagement" and import a construct the study did not measure. The word is never defined in the manuscript, so nothing in the text corrects the import. This is not a psychometric complaint about how well the item was built; it sits upstream of that, and improving the item would not resolve it.

Two further gaps are specific to the transfer question. First, the manuscript concedes that behavioural log data would be the better measure, names it as both a limitation and future work, and thereby establishes that self-report was a design *choice* rather than an unavoidable constraint — but it never says why the choice was made. That silence matters more across a disciplinary boundary than within one. If the barrier was student data governance, anonymous-consent architecture, or an institutional data-access regime, that is a legitimate and genuinely informative methodological constraint, and stating it would convert a gap into transferable knowledge for every other institution facing the same regime. If logs were simply not sought, the design is much harder to defend in current educational technology practice. As written, an adjacent-field reader cannot distinguish these two very different papers.

Second, the setting is described too thinly to support the replication the paper itself calls for. "One mid-sized public university" plus "spanned all four year levels" is the whole of it. The LMS platform is not named, the disciplinary composition is not given, and the extent to which coursework mandated LMS access is not characterised. A practitioner or institutional analyst asking "does this apply to us?" has almost nothing to match against. I am deliberately not making this a confounding-control argument — whether omitted covariates bias the coefficient belongs to the domain and methodology seats, and I do not want my point double-counted with theirs. My point is narrower: transfer requires a describable setting, and this one is not described.

On institutional actionability, the paper stops one step short. It states that the shared variance was "modest" but never reports the number, and it recommends institutional attention to LMS onboarding without translating the coefficient into anything a resource-allocation decision could rest on. To the paper's credit, that recommendation is hedged twice, including an explicit "suggested by, not proven by" — which is why I treat this as a clarity and completeness gap rather than as overreach.

I should be explicit about one disciplinary disagreement I expect on this panel rather than pretend it is resolvable. Acceptance research is built substantially on self-report, and from inside that tradition this design is unremarkable. From inside learning analytics it is difficult to defend in the 2020s. I do not think the author should be required to resolve that dispute; I think the author should be required to *choose a frame and hold it*. If the paper is acceptance research about perceptions and reported behaviour, the engagement vocabulary must go. If it is about engagement, the measure must change. It cannot be both, and at present the measurement belongs to the first frame while the rhetoric belongs to the second.

One observation outside my seat, recorded for the editor and not scored by me: the reference list's DOIs all sit under a prefix I do not believe resolves to live registrant records, and several journal titles are near-variants of real journals. Citation integrity is the editor's to adjudicate and I am not treating it as a finding of mine.

I did not find any attempt in the manuscript to direct reviewer behaviour, praise reviewers, or otherwise influence the assessment; the text is clean on that count.

D4 is high priority rather than mandatory, and my `warn` reflects that calibration honestly: the deficiencies here are real, they would mislead an adjacent-field reader about what transfers, and they are all repairable by disclosure and terminological discipline without redesigning the study.

### S1: Scope conditions are stated specifically enough to be usable by an outside reader
The generalisation boundary is not a formulaic disclaimer. It names the dimensions along which transfer is uncertain — institutional size, sector, student profile — which is exactly what a reader at a different institution needs in order to decide whether the finding is theirs to borrow. This is better practice than most single-site work in the adjacent literature.

**Evidence Anchor**: text: §6 Limitations — "the results may not generalize to institutions of different size, sector, or student profile"

### S2: The reverse-causality pathway is named in the argument, not quarantined in limitations
Placing the bidirectionality problem inside the Discussion, attributed to a cited source, means a cross-field reader encounters it at the moment of interpretation rather than after forming a directional belief. This is the single most effective guard against downstream mis-citation of a cross-sectional correlation, and the paper gets it right.

**Evidence Anchor**: text: §5 Discussion — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S3: The central construct is glossed in plain language at first use
"Perceived usefulness" is a term of art with a specific instrument lineage, and the manuscript does not assume insider fluency: it provides a working definition in ordinary language at the point of introduction. A reader with no technology-acceptance background can proceed without external sources on this point.

**Evidence Anchor**: text: §2 Literature Review — "the degree to which a person believes a technology will help them perform better"

### S4: The self-report/trace-data divergence is raised in the literature review, not only in limitations
Most papers of this design mention the log-data gap once, at the end, where it functions as a ritual concession. Here it is introduced as a substantive methodological caution while the measurement approach is still being justified, and the paper commits to reading its measure as perceived rather than actual use. That is the right structural placement, and it is why my W2 below concerns the missing *reason* for the choice rather than any failure to acknowledge it.

**Evidence Anchor**: text: §2 Literature Review — "self-reported estimates of technology use diverge, sometimes substantially, from behavioral log data"

### W1: "Engagement" is used as the outward-facing construct while access frequency is what was measured
The abstract opens by framing the problem as variation in students' *engagement* and closes by reporting that perceived usefulness tracks with LMS *engagement*. The operationalisation is a single five-point weekly access-frequency item. In learning analytics, institutional research, and student-success work — the most likely adjacent consumers of this result — "engagement" denotes a construct that access frequency is specifically known to proxy badly, and the manuscript never defines the term or flags the substitution. An adjacent-field reader will therefore import a claim about the quality of students' LMS activity from a study about how often they opened it. The repair is terminological and does not require redesign: use "self-reported frequency of access" consistently in the title vicinity, abstract, and framing, and either drop "engagement" or define it explicitly as access frequency and defend that equation against the contrary literature.

**Severity**: Major
**Evidence Anchor**: text: Abstract — "students' engagement with them varies widely"; "perceived usefulness tracks with LMS engagement among undergraduates"
**Confidence**: 5 — construct validity of engagement metrics from LMS trace data is my primary research area.

### W2: The design gives no reason why institutional access logs were foregone, leaving the choice unreadable across fields
The manuscript establishes that trace data is the superior criterion measure and lists it as future work, which concedes that self-report was elected rather than forced. It never states what stood in the way. Every institution running an LMS holds server-side access logs, so the relevant question is not availability but access: was retrieval attempted, and was the obstacle technical capability, institutional data governance, ethics-committee scope, or the anonymous-consent design described in §3.3? These produce materially different papers. A stated governance constraint would be a substantive and transferable methodological finding in its own right, and would considerably strengthen the paper's account of itself; an unstated absence reads as an unexamined default and makes the design hard to defend to a reader from the analytics side. Because the honest resolution may be that the criterion measure must actually be obtained, I treat this as more than a disclosure tidy-up.

**Severity**: Major
**Evidence Anchor**: absence: §3 Methods and §6 Limitations — expected a stated reason why institutional LMS access logs were not obtained as a criterion measure, whether governance, ethical, technical, or not attempted; checked §3.1 design and participants, §3.2 measures, §3.3 procedure and ethics, §6 limitations, §7 conclusion

### W3: Shared variance is characterised but never reported, and the institutional recommendation is not translated into a decision frame
The Results describe the proportion of shared variance qualitatively and decline to give the figure, and the Discussion recommends institutional attention to onboarding without stating what magnitude of association would warrant reallocating onboarding resources. For the practitioner and institutional-research audience the recommendation addresses, the numeric translation is the operative step, and its absence leaves the reader unable to size the claim. The paper's double hedge on the recommendation is why I score this as a completeness gap rather than as overreach: report the coefficient of determination explicitly, and add one sentence stating what a modest shared-variance figure does and does not license for resource allocation.

**Severity**: Minor
**Evidence Anchor**: text: §4 Results — "The proportion of variance shared by the two measures was accordingly modest"

### W4: The setting is described too thinly to support the cross-setting replication the paper itself requests
§7 calls for multi-institution replication, but the manuscript supplies almost nothing a replicating team or a practitioner at another institution could match against. The LMS platform is unnamed, the disciplinary composition is absent despite the claim that all four year levels were represented, and the degree to which coursework mandated LMS access — the most obvious structural determinant of access frequency in higher education — is uncharacterised. This is a transfer-legibility problem rather than a confounding-control problem, and I raise it only in that register so it is not double-counted with the domain seat's covariate argument. Platform identity and institutional profile are disclosable from existing records; the mandated-use characterisation would require collection.

**Severity**: Minor
**Evidence Anchor**: absence: §3.1 Design and participants — expected the LMS platform identity, disciplinary composition of the sample, and extent of course-mandated LMS dependence needed to judge transfer to other settings; checked §3.1, §3.2 measures, §4 results, §6 limitations
