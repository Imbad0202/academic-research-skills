## Scoring Plan Dissent

*(none — omitted)*

Wait: per protocol I must not emit an empty dissent section. Disregarding that heading, my report begins below.

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

Owned by the methodology seat under this contract.

### D2: domain_accuracy
score: not_assessed

Owned by the domain seat under this contract.

### D3: argumentative_coherence
score: not_assessed

Owned by the discourse-analysis seat under this contract.

### D4: cross_disciplinary_relevance
score: warn
trigger: "some field-specific terms or measures go unexplained, or a few implication statements are broader than the presented evidence"

The manuscript's scope statements are unusually disciplined for its genre, and its measured construct (perceived usefulness) is defined in plain language an adjacent-field reader can use. Two things keep it from a pass. First, the paper's outward-facing claim sentences swap in "engagement" — a term of art in learning analytics and educational psychology denoting behavioural, emotional, and cognitive dimensions — for a single self-reported weekly access-frequency item that is never characterised as anything but frequency. Second, the six-item instrument is never reproduced in any form, so no reader outside the technology-acceptance tradition can verify what the construct covers or what the "adaptation" changed. Neither defect is a block: the operational definition of the measured variable is present, the abstract and §6 bound the claim honestly, and the main correlational finding remains recoverable to an outside reader.

### D5: writing_and_structure
score: not_assessed

Owned by the editor-in-chief seat under this contract.

### D6: venue_fit_and_contribution
score: not_assessed

Owned by the editor-in-chief seat under this contract.

## Review Body

I read this manuscript from an institutional-operations seat: I run a university's LMS telemetry pipeline and institutional-research function, co-chair the data-ethics committee that approves student-trace-data use, and sign the budget lines for student onboarding programmes. My scoring remit here is cross-disciplinary relevance, and I have kept the score to that. But the panel should hear the operational reading as well, because the audiences this paper reaches beyond its own subfield — institutional researchers, LMS administrators, ethics committees, and the people who fund onboarding — are precisely the readers most likely to be misled by the two or three places where its language runs ahead of its measurement.

The paper's central virtue is scope discipline. It states a narrow question, uses correlational language consistently, reports the coefficient with a confidence interval, sample size, a Spearman robustness check, and a prospective sensitivity statement, and closes with four honest limitations. Section 2 does something I rarely see and genuinely value across disciplinary lines: it teaches the outside reader the interpretive norm for a single-site estimate before presenting one. A reader from health-services research or public administration could pick this paper up and know how much weight to put on it. That is not a small achievement, and it is why my score is warn rather than block.

The problem is that this discipline lapses at exactly the sentences that travel furthest. The abstract's closing claim and the results discussion both say "engagement," while everything actually measured is a single five-point item about how often a student accessed the system in a typical week. In my operational experience, weekly access frequency tracks assessment deadlines, timetable density, and notification defaults far more tightly than it tracks any perception of usefulness; the paper itself concedes as much in a Results parenthetical, then drops the point. Inside a technology-acceptance readership, "engagement" may pass as loose shorthand. One field over, it is a false friend: it will be read as the multidimensional construct, and the paper will be cited for something it did not measure. This is repairable with word-level honesty rather than new data, which is why it is Major and not Critical.

The second cross-disciplinary barrier is that the instrument is invisible. "Six items adapted from Costa and Wren (2019)" with an alpha of .88 tells me the items hang together; it tells me nothing about what they ask. An adjacent-field specialist cannot assess construct coverage, and no institution could reuse the instrument, without the item stems. Internal consistency is not content validity, and "adapted" is doing undisclosed work.

Third, and this is where the practitioner reading bites hardest: the manuscript names the self-report/log divergence problem, cites Vasquez (2020) for it, discloses it in §6, and then never explains why log data was not used. Every institution operating an LMS already holds per-student access logs; the study's own site does. There are entirely legitimate reasons not to use them — the ethics approval may not have covered trace data, the data-governance route may take longer than a three-week survey window, the analytics team may not release row-level extracts to student researchers. Any of those, stated in one sentence, would convert a disclosed limitation into a handled one and would tell readers whether self-report was a constraint or a convenience. I want to be explicit that I am not asking for a different study. I am asking for the rationale behind the one that was run. As written, the limitation is acknowledged rather than addressed, and outside readers cannot calibrate how much the acknowledgment costs.

Fourth, the omission that most affects how I would interpret the association is not in §6 at all. Device ownership and quality, broadband reliability, commuter versus residential status, and paid-work hours all shape how often a student can access an LMS, and they are correlated with how useful the platform can be to that student in the first place. A student sharing a phone on a weak connection while working twenty hours a week will report both lower access frequency and lower usefulness, for reasons that have nothing to do with acceptance psychology. That is an unmeasured common cause sitting directly under the reported correlation, and §6 does not name it. Adjacent-field readers who lack higher-education operational context will read the four listed limitations as exhaustive and take the association as cleaner than it is. Naming this class of confounder costs the authors nothing and materially improves the honesty of the interpretation.

Fifth, on recruitment: the survey was distributed through the institution's course-announcement channel, which lives inside the very system whose use is the outcome variable. Students who rarely open the LMS were the least likely to see the invitation. That is not generic voluntary-response bias; it is a selection loop specific to this design that truncates the low end of the dependent variable, and its likely direction on a correlation is not obvious enough to hand-wave. The manuscript also never reports the eligible-population denominator, so no reader can tell whether 214 responses represent two per cent of undergraduates or twenty. Both are one-sentence fixes, and both change how much the association can bear.

Sixth, on ethics and governance, which is my committee remit. Section 3.1 reports the removal of five duplicate entries. Section 3.3 states that no identifying information was collected and that responses could not be linked back to individual students. Both cannot be true as written: duplicate detection requires some retained identifier or fingerprint — a session token, IP address, device hash, or single-use link — and the presence of any of those makes the instrument pseudonymous rather than anonymous, which in several jurisdictions and on most committees is a materially different approval category. I am not accusing the authors of a governance breach; I suspect duplicates were caught by an entirely benign mechanism. But the manuscript as written misdescribes what the ethics approval covered, and any committee reading it would ask the same question I am asking. The fix is factual disclosure, not rewording.

Finally, the practical implication. Section 5 recommends onboarding that helps students see concrete usefulness rather than merely announcing that a platform exists. I sit on the side of the desk where that sentence would have to become a budget line, and it cannot. Onboarding was never measured, no onboarding variable was manipulated or observed, and the recommendation is the correlation restated as advice with a hedge attached. To move a budget line, I would need something the current design cannot produce and the manuscript should therefore not gesture at: a comparison of access trajectories between cohorts who received usefulness-framed versus availability-framed onboarding, or at minimum a perceived-usefulness item set disaggregated by which specific LMS functions students found useful, so a programme designer knows what to demonstrate in week one. The hedging in §5 keeps this from misleading anyone who reads carefully, which is why I rate it Minor rather than Major. But the honest version of this paper says plainly that no institutional action follows from a single moderate cross-sectional correlation, and that would be a stronger contribution than a hedged implication. Whether the resulting contribution clears the venue's bar is the editor-in-chief's call, not mine.

### S1: Scope discipline is stated once and then actually honoured

The manuscript commits in §2 to correlational language and to treating its measure as perceived rather than behavioural use, and it holds that line through Results, Discussion, and Conclusion without a single causal slip in verb choice. For an outside reader deciding how much weight to place on a single-site finding, this consistency is what makes the paper safely borrowable.

**Evidence Anchor**: `text: §2 "We take these cautions seriously, restrict ourselves to correlational language throughout"`
**Confidence**: 5 — I routinely audit correlational survey reports for causal-language drift before they reach institutional committees.

### S2: The paper teaches the outside reader how to read a single-site estimate

Section 2 uses Song (2018) not as decoration but to install an interpretive norm before presenting the result. This is exactly the scaffolding an adjacent-field specialist needs and rarely receives, and it pre-empts the most common misuse of a lone campus correlation.

**Evidence Anchor**: `text: §2 "any single-site estimate is best read as one point in a distribution"`
**Confidence**: 4 — based on repeated experience of single-site education-technology findings being over-generalised in institutional decision memos.

### S3: Robustness and sensitivity are reported in a form outsiders can check

The Spearman check addresses the ordinal outcome directly, and the prospective power statement tells a reader what the design could and could not have detected rather than post-hoc rationalising the observed effect. Both let a non-specialist evaluate the estimate without trusting the authors' adjectives.

**Evidence Anchor**: `text: §4 "The Spearman robustness check yielded a comparable coefficient (ρ = .40)"; §3.4 "the study had greater than .80 power to detect a correlation of r >= .19"`
**Confidence**: 4 — standard reporting-quality assessment in my institutional-research role.

### W1: "Engagement" substitutes for weekly access frequency in the paper's most portable claims

**Severity**: Major
The abstract's closing sentence and the Results discussion both use "engagement," a construct that in learning analytics and educational psychology denotes behavioural, emotional, and cognitive dimensions. What was measured is one self-reported item about weekly access frequency. Inside the technology-acceptance tradition this shorthand may pass; one field over it will be read as the richer construct, and the paper will be cited for a finding about engagement it did not produce. Access frequency is additionally a weak proxy on operational grounds, since it tracks assessment deadlines, timetable structure, and notification defaults. The repair is terminological consistency in the abstract, §4, and §7: say self-reported access frequency wherever frequency is what was measured, and if "engagement" is retained anywhere, state explicitly that it is being used to mean reported access frequency only.
**Evidence Anchor**: `text: Abstract "perceived usefulness tracks with LMS engagement among undergraduates"; §4 "reported engagement reflects many influences beyond perceived usefulness"`
**Confidence**: 5 — I manage the telemetry pipeline that produces institutional engagement metrics and the definitional disputes around them.

### W2: The perceived-usefulness instrument is never reproduced, so its construct coverage cannot be assessed

**Severity**: Major
Section 3.2 reports six items adapted from Costa and Wren (2019) with Cronbach's α = .88, but no item stems appear anywhere in the manuscript and there is no appendix or supplementary-materials statement. Internal consistency establishes that the items covary, not what they ask. Nor is the adaptation documented: an adjacent-field reader cannot tell whether wording was localised, whether items were dropped, or whether the adapted scale still measures what the validated original measured, which weakens the paper's reliance on "previously validated." Reproducing the six stems, and stating what changed from the source instrument, costs half a page and is the single highest-value addition for readers and for any institution wanting to reuse the measure.
**Evidence Anchor**: `absence: §3.2 Measures and manuscript end matter — expected the six adapted perceived-usefulness item stems or an appendix reproducing the instrument; checked §3.2, §3.4, §7, the reference list, and the lack of any appendix or supplementary-materials statement`
**Confidence**: 5 — instrument review is a standing requirement in the survey approvals I sign off.

### W3: §6 omits the unmeasured access and equity confounders that plausibly drive both variables

**Severity**: Major
Device ownership and quality, broadband reliability, commuter versus residential status, and paid-work hours all constrain how often a student can access an LMS, and they co-vary with how useful the platform can be to that student. None is measured, and none is named in the four limitations. Section 4 gestures at course requirements and assessment schedules in a single parenthetical and then drops the issue. Because §6 reads as an exhaustive list, adjacent-field readers without higher-education operational context will treat the association as cleaner than it is. A fifth limitation naming this class of common cause, and a sentence in §5 acknowledging that part of the observed association may be structural rather than attitudinal, would resolve it without new data.
**Evidence Anchor**: `absence: §6 Limitations — expected a named limitation for unmeasured confounders of access frequency (assessment schedules, timetable structure, notification settings, device and broadband access, commuter status, paid-work hours); checked §6 items one through four, §5 Discussion, the §4 Results parenthetical on course requirements, and §3.2 Measures`
**Confidence**: 5 — this confounder set is what my office controls for whenever it models LMS access rates.

### W4: The onboarding implication invokes a lever the study never measured and cannot guide institutional action

**Severity**: Minor
Section 5 recommends onboarding that helps students see concrete usefulness. No onboarding variable was observed or manipulated, so the recommendation is the correlation restated as advice. From a budget-holder's seat there is nothing here to act on: it does not identify which LMS functions students found useful, does not compare framings, and does not estimate any change in use attributable to onboarding. The hedge ("suggested by, not proven by") keeps a careful reader from being misled, which holds this below Major, but the manuscript would be stronger if it either stated plainly that no institutional action follows from a single cross-sectional correlation, or reported perceived-usefulness responses at the item level so a programme designer knows what to demonstrate.
**Evidence Anchor**: `text: §5 "LMS onboarding which helps students see concrete usefulness — rather than merely announcing that a platform exists — may be worth institutional attention"`
**Confidence**: 5 — I hold the onboarding budget line this implication would have to move.

### W5: The anonymity claim in §3.3 is incompatible with the duplicate removal reported in §3.1

**Severity**: Major
Removing five duplicate entries requires some retained identifier or fingerprint: a session token, IP address, device hash, or single-use link. Section 3.3 nonetheless states that no identifying information was collected and that responses could not be linked back to individuals. On most ethics committees, and in several data-protection regimes, an instrument supporting duplicate detection is pseudonymous rather than anonymous, and the two sit in different approval categories. I do not assume a governance breach; I assume a benign detection mechanism that the manuscript has described inaccurately. But resolving this requires the authors to supply a fact the paper does not contain — the actual deduplication mechanism, whether any identifier was retained and for how long, and what the approval covered — rather than a rewording. As written, the ethics statement cannot be accurate, and cross-jurisdictional readers will misread the study's data-protection posture.
**Evidence Anchor**: `text: §3.1 "5 duplicate entries were removed"; §3.3 "No identifying information was collected, and responses could not be linked back to individual students"`
**Confidence**: 5 — I co-chair the committee that reviews exactly this class of student-data claim.

### W6: The shared-variance statement is qualitative where a number is available

**Severity**: Minor
Section 4 says the proportion of variance shared by the two measures was "accordingly modest" without stating it, and "moderate" carries different conventional thresholds across fields. Giving the value explicitly (roughly eighteen per cent) lets readers in disciplines with different effect-size norms judge the magnitude for themselves rather than accepting the authors' adjective, and it strengthens rather than weakens the paper's own modesty claim.
**Evidence Anchor**: `text: §4 "The proportion of variance shared by the two measures was accordingly modest"`
**Confidence**: 4 — routine effect-size reporting judgment in cross-field comparisons of institutional findings.

### W7: Recruitment ran through the system being measured, and the eligible-population denominator is missing

**Severity**: Major
The survey was distributed via the institution's course-announcement channel, which sits inside the LMS whose use is the outcome. Students who rarely open the LMS were least likely to see the invitation, which truncates the low end of the dependent variable. This is a design-specific selection loop, not the generic voluntary-response caveat §6 offers, and its effect on a correlation is not self-evidently conservative. Compounding this, no enrolled-undergraduate denominator is reported, so no reader can compute a participation rate or bound the self-selection risk. Both are one-sentence disclosures the authors already possess, and together they change how much interpretive weight the association can carry.
**Evidence Anchor**: `text: §3.1 "The survey was distributed through the institution's course-announcement channel"; §6 "students who engage more with institutional channels may be overrepresented"`
**Confidence**: 5 — I administer institutional survey distribution and hold the enrolment figures such studies omit.

### W8: The choice of self-report over available log data is disclosed but never justified

**Severity**: Minor
The manuscript cites Vasquez (2020) for the divergence between self-reported and logged technology use, lists the reliance on self-report as its second limitation, and recommends log-based work in §7, yet never says why logs were not used here. Every institution running an LMS holds per-student access logs, so outside readers will assume they were available and cannot tell whether self-report was a governance constraint, an approval-scope constraint, a feasibility constraint within a three-week window, or a convenience. One sentence stating the actual reason would convert a disclosed limitation into a handled one. I am not asking for a redesign; I am asking for the rationale behind the design that was run, which is what lets a practitioner reader calibrate what the "design-bounded" framing costs.
**Evidence Anchor**: `absence: §3.1 Design and the §6 second limitation — expected a stated reason why institutional LMS access logs were not used or not obtainable (approval scope, data-governance route, feasibility within the survey window); checked §3.1, §3.2, §3.3, §6, and the §7 future-research sentence`
**Confidence**: 4 — based on operating the governance process that grants or denies exactly this kind of log access.
