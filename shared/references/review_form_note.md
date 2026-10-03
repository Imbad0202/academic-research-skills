# Review-Form Note (#921)

This file holds the canonical review-form note: a fixed-point reminder that lists the forms a literature review can take and leaves the choice to the author. The block between the markers is copied verbatim into each surface below; `scripts/check_review_form_note_sync.py` keeps every copy byte-identical to this one and checks the note text for a default, a ranking, or a recommendation.

| Surface | Where the block sits |
|---|---|
| `deep-research/SKILL.md` | After the Mode Selection Guide (covers `lit-review` mode and the RQ Brief confirmation in `full` and `socratic` modes) |
| `academic-paper/SKILL.md` | After the Mode Selection Guide (covers `lit-review` mode) |

Why the note exists: whether to run a systematic review is a research-design decision that costs the author months of work and a team. ARS enters `systematic-review` mode only when the user asks for it, so users who do not know the option exists never hear about it. The note closes that gap without letting the model decide: deciding *when* to remind is itself a judgment, so the note is tied to two actions the author takes (selecting `lit-review` mode, confirming the RQ Brief) and never to the content of the question.

Sources for the one-line descriptions:

- Systematic review time and team size: Borah, R., Brown, A. W., Capers, P. L., & Kaiser, K. A. (2017). Analysis of the time and workers needed to conduct systematic reviews of medical interventions using data from the PROSPERO registry. *BMJ Open, 7*(2), e012545. https://doi.org/10.1136/bmjopen-2016-012545 (195 registered, completed reviews: mean 67.3 weeks from registration to publication, mean 5 authors; the same abstract reports means of 42 weeks for funded and 26 weeks for unfunded reviews). The sample is medical-intervention reviews and the means vary by measure, so the note says "months to more than a year", not a figure.
- Scoping review purpose: Tricco, A. C., Lillie, E., Zarin, W., et al. (2018). PRISMA Extension for Scoping Reviews (PRISMA-ScR): Checklist and explanation. *Annals of Internal Medicine, 169*(7), 467–473. https://doi.org/10.7326/M18-0850 ("follow a systematic approach to map evidence on a topic and identify main concepts, theories, sources, and knowledge gaps").
- Rapid review, and two independent screeners for a systematic review: Garritty, C., Gartlehner, G., Nussbaumer-Streit, B., et al. (2021). Cochrane Rapid Reviews Methods Group offers evidence-informed guidance to conduct rapid reviews. *Journal of Clinical Epidemiology, 130*, 13–22. https://doi.org/10.1016/j.jclinepi.2020.10.007 (§3.3.4: "MECIR states that it is desirable to use two screeners working independently"; the guidance applies "when decisions need to be made in a period of weeks to a few months").
- Integrative review: Whittemore, R., & Knafl, K. (2005). The integrative review: Updated methodology. *Journal of Advanced Nursing, 52*(5), 546–553. https://doi.org/10.1111/j.1365-2648.2005.03621.x (the only review approach that "allows for the combination of diverse methodologies"; its stages include searching the literature and evaluating data from primary sources).
- The scoping and narrative lines give no time figure because none of these sources supports one; they say what the work depends on instead.

Other languages: the note has an English and a Traditional Chinese text. Every other language gets the English text, so that no user sees a paraphrase the model wrote on the spot. A community locale pack may propose a reviewed translation as a third fixed text.

Out of scope: any model assessment of whether a question suits a systematic review; the screening skill proposed in #919. Whether sessions show the note at the right points is prompt-level and unmeasured; the routing fixtures in `tests/fixtures/issue_133_routing/` (13–15) are smoke tests, not a rate.

<!-- review-form-note:begin -->
### Review-form note (#921)

The author decides whether to run a systematic review. ARS reminds the author that the choice exists; it does not judge whether a question fits a systematic review, and no review form is ever a default step.

**When to show it.** Show the note at the first of these two points. Both are actions the author takes:

1. The author selects `lit-review` mode (in `deep-research` or `academic-paper`, by slash command or by request).
2. The author confirms the research question: in `deep-research` `full` mode, the author confirms the RQ Brief before Phase 2; in `socratic` mode, the author confirms the Mentor's closing RQ Brief or RQ Summary as their research question. Show the note right after that confirmation. A Socratic ending the author has not confirmed (a turn-cap ending, an ending the author calls unfinished, the stagnation suggestion to switch to `full` mode, or a switch to `full` mode) is not this point; a later confirmation is.

Whether the note appears must not depend on the topic, the wording, or the kind of research question. Do not show it at any other point, and do not show it, or hold it back, because a question looks like an effect question.

**When not to show it.**

- The note was already answered or skipped in this project or run. In a run with a passport file, look for a `checkpoint_closed` entry with `checkpoint_id: review-form-note` in what `python3 scripts/run_ledger.py show --passport-path <passport>` prints; without one, look in this conversation. Across separate sessions without a passport file the note can appear again; this is accepted. If the ledger holds a `checkpoint_opened` entry for `review-form-note` and no closing entry, the note is still awaiting its answer: show it again, append no second opening entry, and append the closing entry after the reply.
- The author already named a review form in their own words or actions: entered `systematic-review` mode, asked for a systematic, scoping, rapid, narrative, or integrative review, or said they want no formal review. This test reads what the author said, not the content of the research question.

**How to show it.**

- Show the note text below verbatim: the English text in English conversations, the Traditional Chinese text in Traditional Chinese conversations, and the English text in every other language. Do not shorten, reorder, paraphrase, or add to it. Add no recommendation, default, or comment on which form fits the question, before or after it.
- Then stop and wait for the author's reply. Do not start the literature search, the review, or Phase 2 before the author replies.
- The note does not reopen the choice of workflow. If the author skips it, the mode the author asked for continues unchanged.
- If the author asks which form fits their question, say that the choice is theirs. On request, describe any form in more detail, without a comparison that favours one form for their question.

**After the reply.**

- Skip, or a reply that keeps the current work: continue in the current mode. Skipping is a decision.
- Systematic review: offer `deep-research` `systematic-review` mode, and enter it only when the author confirms.
- Scoping review or rapid review: continue in the current mode, and say once that ARS has no separate mode for this form, so its protocol and reporting checklist (PRISMA-ScR for a scoping review) stay with the author.
- Narrative or integrative review, or no formal review: continue in the current mode.
- In a run with a passport file, record the note through `scripts/run_ledger.py append`: before waiting, unless the ledger already holds one, a `checkpoint_opened` entry (`checkpoint_id: review-form-note`, `stage`: the current stage or mode, `checkpoint_type: SLIM`, `question`: the note as shown, `options`: the five forms and `skip`); after the reply, a `checkpoint_closed` entry with `answer`: the form chosen or `skip`, and the author's exact words in `user_words`.
- No path enters `systematic-review` mode on ARS's initiative. Only the author's explicit choice does.

**Note text (English):**

> **Before the review starts: which form of literature review?**
> ARS does not choose this for you. There is no default and no recommendation, and the order below is not a ranking.
>
> - **Systematic review**: answers a focused question with a search and screening plan fixed in advance, with two people screening independently where possible. Months to more than a year for a team of several people, often with a registered protocol. In ARS: `systematic-review` mode.
> - **Scoping review**: maps what has been studied on a topic, the main concepts, and the gaps, using a systematic approach. The work grows with the breadth of the topic. ARS has no separate mode for it.
> - **Narrative or integrative review**: builds an argument or a framework from the literature. In a narrative review the author chooses the sources; an integrative review documents its search and evaluation and can combine different study designs. The work depends on the scope the author sets. In ARS: `lit-review` mode.
> - **Rapid review**: a systematic review with some steps shortened or left out to deliver sooner, typically within weeks to a few months. ARS has no separate mode for it.
> - **No formal review**: background from the sources at hand, for example for an introduction. It does not claim to cover the literature.
>
> Reply with the form you want, or reply "skip" to continue as you are. Either reply is your decision, and this note will not appear again in this project.

**Note text (Traditional Chinese):**

> **開始回顧之前：要做哪一種文獻回顧？**
> 這件事由你決定，ARS 不替你選。下列選項沒有預設、沒有推薦，排列順序也不代表高下。
>
> - **系統性回顧（systematic review）**：回答一個聚焦的問題，檢索與篩選方式事先訂好，盡可能由兩人各自獨立篩選。一個數人團隊需要數個月到一年以上，通常有已登錄的研究計畫書。ARS 對應：`systematic-review` 模式。
> - **範疇回顧（scoping review）**：用系統化的做法盤點一個主題已經研究了什麼、有哪些主要概念、缺口在哪裡。工作量隨主題的廣度增加。ARS 沒有專屬模式。
> - **敘事或整合性回顧（narrative / integrative review）**：從文獻建立論證或架構。敘事回顧由作者選擇文獻；整合性回顧會記錄檢索與評估過程，並可合併不同研究設計。工作量取決於作者設定的範圍。ARS 對應：`lit-review` 模式。
> - **快速回顧（rapid review）**：為了早點交出結果而縮短或省略部分步驟的系統性回顧，通常在數週到數個月內完成。ARS 沒有專屬模式。
> - **不做正式回顧**：用手邊的文獻寫背景，例如論文的緒論。不宣稱涵蓋整體文獻。
>
> 請回覆你要的形式，或回覆「跳過」照目前的做法繼續。兩種回覆都算你的決定，這個專案裡不會再出現這則提醒。
<!-- review-form-note:end -->
