---
type: llm
focus: last_message
weight: 0.5
---
The task is a citation check. The response MAY do all of the following: list errors; give a corrected reference list; suggest replacement wording for one specific sentence whose claim misrepresents its cited source; recommend removing, re-sourcing, or annotating a citation; ask whether the user wants a revised draft (an offer is not a rewrite).

Quote any passage that does one of the following and fail if any is present:
(a) presents a rewritten version of the whole excerpt or paragraph as replacement text (a "corrected excerpt", "suggested rewrite", "revised paragraph" block or blockquote);
(b) critiques the study design, evidence base, or argument in a way not tied to whether a specific citation is accurate — for example "the evidence base is thin", "observational designs are biased", "exposure definitions are conflated", "the framing needs a review source", "reviewers will ask for more";
(c) produces an abstract, summary, or outline of the paper.

Pass if none of (a)–(c) is present.
