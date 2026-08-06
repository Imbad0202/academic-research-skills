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
trigger: "asserts interdisciplinary implications in a closing passage without tying them to reported results"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript twice: once as an adjacent-field reader asking whether I could restate the finding without error, and once as the person who runs an LMS data warehouse and would be asked to act on it. The two readings diverge, and that divergence is the substance of my review.

On the first test the paper does well for most of its length. Perceived usefulness is defined in plain terms at first use, the population and setting are named, the design's inferential limits are stated four times in four different places, and the reverse-causal pathway is conceded rather than buried. An adjacent-field reader who reads §1 through §7 can say correctly: among 214 undergraduates at one mid-sized public university, a self-report measure of perceived LMS usefulness correlated moderately with a single self-report frequency item. That is a legitimate, bounded, non-inflated finding, and I want to record that the restraint here is real and unusual.

The test fails at one specific location, and it is the location adjacent-field readers actually read. The abstract's final sentence converts "self-reported use" into "LMS engagement." The manuscript's own literature review cites Vasquez (2020) precisely to forbid that equivalence, and the title and body honour the distinction. An abstract-only reader — which describes almost every institutional reader who will encounter this paper through a database search or a practitioner digest — will carry away the wrong claim. I considered scoring D4 as a block on my export-of-conclusions criterion, and I am not doing so, because the slippage is a single sentence that the body of the paper actively contradicts rather than a scope claim the manuscript sustains. It is correctable in one clause. It should be corrected.

On the second reading, the institutional one, the paper offers less than it appears to. §5's onboarding suggestion is the only actionable content in the manuscript, and it is undetermined in exactly the way that matters for resource allocation. If perceived usefulness drives use, the lever is onboarding communication. If use drives perceived usefulness — the pathway the authors themselves credit to Delgado (2020) as "equally consistent with the data" — then the lever is course design and assessment placement, and onboarding messaging is close to the worst available intervention. The paper states the ambiguity in §5's second paragraph and then makes a recommendation that only survives under one horn of it, without saying so. The hedge does not fix this; it makes the recommendation unfalsifiable rather than defensible. I am aware that a research journal is not obliged to produce a procurement memo, and I have tried not to score the paper against a decision standard it never claimed. But the abstract advertises "implications for LMS onboarding," so the paper does claim this ground, and the claim is not carried.

Third, the part of my brief where I am least willing to be talked out of a finding. This study was conducted inside an institution that owns the LMS and therefore owns the logs that would answer its question better. The manuscript names that gap as Limitation 2 and never says why the gap exists. There is a large interpretive difference between "our data governance committee does not permit linkage of survey responses to log records," "log access was outside the approved IRB protocol," and "we did not pursue logs." The first two are constraints and belong in Limitations exactly where they sit. The third is a design decision and belongs in §3 with a defence. As written, an adjacent-field reader in institutional research or learning analytics cannot tell which they are reading, and therefore cannot tell whether this is the best obtainable evidence on the question or a substitute for evidence that was available down the hall.

Related, and mostly a favour to the authors' own future work: §7 recommends research using behavioral log data, while §3.3 records a consent and anonymity architecture under which no such linkage is possible for this cohort. The recommendation is sound, but the paper is silent on the fact that its own consent design forecloses the extension it proposes, and silent on what consent language would have kept the door open. For readers in my seat, that sentence is worth more than the correlation.

I should name my own bias. I do not think perceived usefulness is merely a degraded proxy for logs; it is a psychological construct with standing of its own, and measuring it with a validated instrument is a defensible thing to do. My objection is not that the paper measured perception. It is that the paper occasionally labels the perception measure "engagement," and that it recommends spending institutional money on the strength of it.

### S1: Construct definition is field-neutral and placed at first use

The operative construct is glossed in ordinary language before any technical use, which is what lets an adjacent-field reader follow §4 and §5 without consulting the technology-acceptance literature.

- **Evidence Anchor**: `text: §2 "the degree to which a person believes a technology will help them perform better"`
- **Confidence**: 5 — routine assessment of construct exposition for mixed-discipline readerships.

### S2: Scope is declared as a scope, not implied

The manuscript states its own narrowness as a design commitment rather than leaving readers to infer it, and then holds to correlational language throughout. This is the main reason the paper is legible across fields despite the abstract's slip.

- **Evidence Anchor**: `text: §1 "It asks a deliberately narrow question"`
- **Confidence**: 5 — direct textual reading.

### S3: Sensitivity is reported in terms an outsider can use

Reporting the detectable effect size rather than only the achieved p value lets a reader from another field judge what the design could and could not have found, without reconstructing a power calculation.

- **Evidence Anchor**: `text: §3.4 "the design was sensitive to small-to-moderate associations"`
- **Confidence**: 4 — familiar with power reporting conventions; the statistical adequacy verdict belongs to D1's owner.

### W1: The abstract restates a self-report finding as a finding about engagement

The closing sentence of the abstract drops the "self-reported" qualifier that the title, §3.2, §4, and §6 all maintain, and substitutes "LMS engagement." The manuscript's own citation of Vasquez (2020) establishes that these are not interchangeable. Because abstracts circulate independently, this is the single highest-traffic sentence in the paper and the one most likely to be quoted into a practitioner or cross-field argument. The fix is a clause; the reason it is not cosmetic is that the corrected sentence narrows the paper's advertised contribution to what it actually measured.

- **Severity**: Major
- **Evidence Anchor**: `text: Abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates."`
- **Confidence**: 5 — published work on survey/log divergence; the distinction is my direct area.

### W2: The onboarding implication is not determinate enough to inform any allocation, and its hedge conceals rather than resolves that

§5 concedes that the reverse pathway is equally consistent with the data, then recommends onboarding attention, which is the lever implied by only one of the two pathways. Under the reverse pathway the indicated lever is assessment and course-design placement inside the LMS, not onboarding messaging. The manuscript never tells the reader that its recommendation is conditional on a direction it has explicitly declined to establish. The hedge ("suggested by, not proven by") makes the sentence unfalsifiable but leaves an institutional reader with a recommendation they cannot evaluate, and a careless one with a recommendation they may act on. Repair requires either deriving the implication under both directions or withdrawing it and letting the correlation stand alone, which also means amending the abstract's promise of onboarding implications.

- **Severity**: Major
- **Evidence Anchor**: `text: §5 "may be worth institutional attention" and "suggested by, not proven by"`
- **Confidence**: 5 — direct experience translating correlational LMS findings into onboarding and course-design decisions.

### W3: The reason log data was not used is never stated, so readers cannot tell whether Limitation 2 is a constraint or a choice

The study sits inside the institution that holds the behavioral records the research question implicates. The manuscript cites the self-report/log divergence literature in §2, lists the absence of logs in §6, and recommends log-based work in §7, without anywhere stating why logs were not used here. Governance restriction, IRB scope, and absence of a linkage key under anonymity are all legitimate constraints that would settle the matter in one sentence. Non-pursuit is a design decision that requires a defence. Left unstated, an adjacent-field reader cannot assign the study its evidential position: best-available evidence under a real constraint, or a weaker instrument chosen where a stronger one was institutionally at hand. That is not a clarity issue; it changes the weight the finding should receive. The methodological adequacy verdict here belongs to D1's owner, but the reader-facing indeterminacy is mine.

- **Severity**: Major
- **Evidence Anchor**: `absence: Methods §3.3 and Limitations §6 — expected an explicit statement of whether LMS log data was governance-restricted, outside IRB scope, or simply not pursued; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §6, §7`
- **Confidence**: 5 — I chair a student-data governance committee and review exactly these linkage requests.

### W4: The consent architecture forecloses the future work the paper recommends, and the paper does not say so

§3.3 records that no identifying information was collected and that responses cannot be linked to individual students. That design is defensible on its own terms, and it is also the reason the §7 recommendation cannot be executed on this cohort. Authors recommending log-linked follow-up should state what consent and linkage architecture such a study needs — a linkage key held under separate governance, or consent language explicitly covering administrative and log-data linkage — since the readers most able to act on the recommendation are the ones who must clear it with a governance body first. As written, the recommendation is addressed to a community whose binding constraint it does not engage.

- **Severity**: Minor
- **Evidence Anchor**: `text: §3.3 "No identifying information was collected, and responses could not be linked back to individual students."`
- **Confidence**: 4 — governance practice varies by jurisdiction and institution, so the specific remedy may differ.

### W5: Deduplication is reported without explaining what made duplicates detectable under stated anonymity

Five duplicate entries were identified and removed in a survey described as collecting no identifying information. Something distinguished them: a session token, an IP or device fingerprint, a response-timestamp heuristic, or a platform-level duplicate flag. Each has a different disclosure implication, and some are quasi-identifiers whose collection a reader would want reconciled with §3.3's anonymity statement. For adjacent-field readers assessing whether their own governance regime would have approved this protocol, the gap matters more than its size suggests.

- **Severity**: Minor
- **Evidence Anchor**: `text: §3.1 "14 incomplete submissions and 5 duplicate entries were removed"`
- **Confidence**: 4 — standard survey-platform deduplication mechanics; the actual method here is undisclosed.

### W6: Frequency-scale anchors are incompletely reported, so the reported central tendency is not interpretable outside the paper

§3.2 gives only the endpoint labels of the five-point use item, while §4 reports a median category of "a few times per week" that corresponds to an unlabelled interior point. An outside reader cannot tell whether that median is the third or fourth scale position, nor how the intermediate categories were worded, which blocks comparison against Song (2018) or against any institution's own usage bands. The six adapted perceived-usefulness items are likewise not reproduced, so the adaptation cannot be inspected. Both are supplement-level fixes.

- **Severity**: Minor
- **Evidence Anchor**: `text: §3.2 "1 = rarely or never to 5 = several times daily"`
- **Confidence**: 5 — instrument reporting conventions for survey replication.
