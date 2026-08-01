# AI-Usage Disclosure Policy Database — v2

**Snapshot date**: 2026-04-09 (original v1 database build; individual rows carry their own "access date" recording when each was last re-verified)
**Scope**: v1 (2026-04) covered 6 ML/NLP-focused venues (ICLR, NeurIPS, Nature, Science, ACL, EMNLP). v2 (2026-07, #596) adds 9 medical-publishing policy targets: the ICMJE umbrella recommendations, four ICMJE member journals (BMJ, JAMA, The Lancet, NEJM), PLOS, Frontiers, and the database's first two Chinese-language policy targets (one publisher-wide entry, Chinese Nursing Journals Publishing House 中华护理杂志社; one journal, International Eye Science 国际眼科杂志). Education/QA journals remain deferred.
**Maintenance**: policies drift. Before submission, the user should verify against the venue's current page. The "source URL" and "access date" below record when ARS last verified each policy.
**Ordering note**: all entries are kept in one global alphabetical order by canonical English label (per step 5 of "Adding a new venue" below).

---

## Evidence-layer contract

This file is the venue track's policy-evidence layer consumed by `disclosure_mode_protocol.md`. It contains source provenance, policy wording, prohibited uses, and placement evidence; it contains no executable renderer directives. Selector aliases, applicability predicates, required/conditional fact mappings, halt outcomes, advisories, and rendering behavior exist only in the protocol. The two surfaces require coordinated maintenance when a target changes. This evidence file is not a standalone disclosure template.

Unknown-venue handling is defined exclusively in `disclosure_mode_protocol.md`;
free policy prose, whether pasted or recorded here, is not an executable
category-to-field mapping.

---

## Venue: ACL (Association for Computational Linguistics)

| Field | Value |
|---|---|
| Source URL | https://www.aclweb.org/adminwiki/index.php/ACL_Policy_on_Publication_Ethics#Guidelines_for_Generative_Assistance_in_Authorship |
| Access date | 2026-06-07 |
| Policy summary | Use of generative AI to create content must be fully disclosed in the **Acknowledgements** section (the policy's own example: "Section 3 was written with inputs from ChatGPT"). Disclosure is graduated by use type: language-only assistance (paraphrasing/polishing) and short-form input assistance (predictive keyboards) do **not** require disclosure; low-novelty text generation and AI-suggested new ideas **do**. AI literature-search tools require no special disclosure but the usual citation-accuracy and thoroughness requirements still apply. Authors are fully responsible for all submitted content. |
| Required phrasing elements | Name the tool and the specific content it produced (the policy example states the section and the tool). For low-novelty generated text, also affirm the output was checked for accuracy and carries appropriate citations for both the source text and the source idea(s). |
| Preferred disclosure location | The **Acknowledgements** section (per the ACL Admin Wiki current guidance). The 2023-era separate "Use of AI Assistance" subsection is no longer the canonical location. |
| Prohibited uses | Listing a generative AI tool as an author. Using automated tools that rephrase existing work as one's own without attribution (treated as plagiarism). Generated text that copies existing work is subject to the plagiarism policy. |
| Authorship rule | AI tools cannot be listed as authors; ACL does not consider a generative model an entity that can fulfill co-authorship requirements |
| Notes | Source is the org-wide ACL Admin Wiki policy (ACL Exec-approved, current through 2025), which ARR / EMNLP 2026 link to for current paper-integrity guidance. Supersedes the 2023 ACL conference blog URL (still live but stale: it pointed disclosure at a dedicated subsection rather than Acknowledgements). |

---

## Venue: BMJ (The BMJ / BMJ Publishing Group)

| Field | Value |
|---|---|
| Source URL | https://authors.bmj.com/policies/ai-use/ |
| Access date | 2026-07-31 |
| Policy summary | BMJ considers content produced with AI; its "approach is one of transparency". The policy applies to all content formats (text, audio, video, images, data) and is explicitly WAME/COPE-aligned. BMJ expects adequate declaration and says authors should declare AI use; inadequate declaration can lead to rejection or, post-publication, to corrective action. |
| Required phrasing elements | Declare what AI technology was used, why it was used, and how it was used. Authors should consider providing a **summary of the input, output, and the way the authors reviewed the AI output** as supplementary files or additional information for editorial review. |
| Preferred disclosure location | **Contributor section** (acknowledgement of AI use); research-related AI use additionally requires a fuller description in **Methods**. |
| Prohibited uses | Listing AI as an author. Inadequate declaration of AI use (grounds for rejection or post-publication action). Peer reviewers putting unpublished manuscripts into publicly available AI tools. |
| Authorship rule | "AI technologies will not be accepted as an author(s) of any content submitted to BMJ for publication." |
| Notes | BMJ is an ICMJE member journal. The ICMJE umbrella recommendations and BMJ's own AI-use page are simultaneously relevant sources; neither source states that it silently replaces the other. |

---

## Venue: Chinese Nursing Journals Publishing House (中华护理杂志社)

| Field | Value |
|---|---|
| Source URL | https://www.zhhlzzs.com/CN/news/news795.shtml |
| Access date | 2026-08-01 |
| Policy summary | 《中华护理杂志社关于使用生成式人工智能技术的有关规定》 (Regulations on the Use of Generative AI Technology; dated 2024-06-20, posted on the official site 2024-12-16). GenAI-assisted work is permitted only with mandatory description of the use and full author responsibility; the regulation itself provides a model disclosure statement. GenAI may not write the whole paper or its important parts; methods, results, and result interpretation are introduced with “如” as examples, followed by the broader rule that all content constituting scientific contribution or intellectual labour must be completed by the authors. GenAI may not generate research figures (data plots, radiology images, photographs, forest plots, surgical audio/video), and unverified GenAI-generated references must not be used. Content by another author that is already labelled as AI-generated generally should not be cited as an original source; when citation is genuinely necessary, the author should explain it. |
| Required phrasing elements | Model statement (verbatim, Chinese): “生成式人工智能技术应用声明：本文在准备和撰写过程中，作者使用了[GenAI具体工具/服务名称]来[使用目的：如文献调研/数据分析/图表制作等]。使用此工具/服务后，作者根据需要对内容进行了审查和编辑，并对出版物的内容承担全部责任。” The policy also states: “应在论文的‘材料与方法’（或类似部分）中进行描述，同时在正文后、参考文献前，公开、透明、详细地说明GenAI技术的使用和审查情况。” (English paraphrase: name the specific tool/service and purpose, state that authors reviewed and edited the content as needed and take full responsibility; describe the use in Materials and Methods or similar, AND give a detailed use-and-review statement after the main text and before the references.) The policy separately says authors should cooperate with the editorial office in submitting and archiving AI-assisted text / figures / code as supplementary material; its wording is an editorial-cooperation clause rather than an unconditional first-submission attachment requirement. |
| Preferred disclosure location | **“材料与方法” (Materials and Methods)** AND a statement **after the main text, before the references** (both locations required). |
| Prohibited uses | GenAI as author; writing the whole paper or its important parts; generating data plots, radiology images, photographs, forest plots, or surgical audio/video; **altering or manipulating original research data, the research process, or results**; using unverified GenAI references; uploading manuscripts to public GenAI platforms during peer review; editors using public GenAI for screening or copyediting. Penalty (verbatim, Chinese): “将直接退稿或撤稿……情节严重者，将列入作者学术失信名单，2年内禁止该作者向中华护理杂志社系列期刊投稿；若该作者是期刊审稿人，同时将禁止其参与审稿工作。” (English paraphrase: direct rejection or retraction; serious cases are added to the academic-dishonesty list with a 2-year submission ban across the publisher's journal series; reviewer-authors are additionally barred from reviewing.) |
| Authorship rule | GenAI cannot be listed as an author |
| Notes | One of the database's first two Chinese-language policy targets (with International Eye Science); this entry is publisher-wide rather than a single journal. The regulation references the ICMJE framework. Verbatim policy language is kept in the original Chinese with English paraphrase. The qualified rule about citing another author's AI-labelled content is an advisory/conditional-explanation rule, not the same hard prohibition as directly using an unverified GenAI-generated reference. |

---

## Venue: EMNLP (Empirical Methods in Natural Language Processing)

| Field | Value |
|---|---|
| Source URL | https://2026.emnlp.org/paper-integrity-policy/ (refers authors to ACL's generative-authorship guidelines; canonical text at the ACL Admin Wiki — see ACL row) |
| Access date | 2026-06-07 |
| Policy summary | For AI-assistance disclosure, EMNLP refers authors to ACL's generative-authorship guidelines. Same requirements apply. See ACL row. |
| Required phrasing elements | Same as ACL |
| Preferred disclosure location | Same as ACL: the **Acknowledgements** section |
| Prohibited uses | Same as ACL |
| Authorship rule | Same as ACL |
| Notes | EMNLP 2026 maintains its own Paper Integrity Policy page that refers authors to ACL's generative-authorship guidelines for this issue (and carries additional EMNLP/ARR-specific integrity policies beyond AI disclosure). The canonical source for the AI-disclosure rules below is the ACL Admin Wiki (see ACL row). |

---

## Venue: Frontiers (Frontiers journals)

| Field | Value |
|---|---|
| Source URL | https://www.frontiersin.org/guidelines/policies-and-publication-ethics |
| Access date | 2026-08-01 |
| Policy summary | Section "Artificial intelligence: fair use and disclosure policy". Generative AI (LLMs; text-to-image generators) may be used in writing/editing and in figure production, subject to disclosure. Authors remain responsible for checking factual accuracy of applicable GenAI-created content, including quotes, citations, and references; checking GenAI-produced or GenAI-edited written and visual content is plagiarism-free; and checking a figure accurately reflects the data when it represents manuscript data. These quality checks are pre-submission actions rather than disclosure-rendering fields. |
| Required phrasing elements | Identify the tool's "name, version, model, and source" for AI-produced or AI-edited content. Prompts and outputs are encouraged as supplementary files. |
| Preferred disclosure location | **Acknowledgments** (AI-generated main text); AI-produced or AI-edited written or visual content → Acknowledgments AND **Methods** if applicable. |
| Prohibited uses | Listing generative AI as author or co-author. Editors/reviewers uploading manuscript content to external generative AI tools. |
| Authorship rule | "Authors should not list a generative AI technology as a co-author or author of any submitted manuscript." |
| Notes | Explicitly permits GenAI-assisted figure production subject to verification and disclosure — broader than most medical venues in this database. The factual-accuracy, plagiarism-free, and conditionally applicable accuracy-to-data checks are carried as a labelled Phase-5 pre-submission checklist. An unknown or false check remains outstanding and must not be rendered as confirmed; it is not a disclosure `UNKNOWN` halt or a categorical prohibition. |

---

## Venue: ICLR (International Conference on Learning Representations)

| Field | Value |
|---|---|
| Source URL | https://iclr.cc/public/AuthorGuide |
| Access date | 2026-04-09 |
| Policy summary | Authors may use LLMs and AI assistants for writing and code. Authors must disclose AI use and are fully responsible for all content. AI cannot be listed as an author. |
| Required phrasing elements | Must state specific tool(s) used and specific tasks assisted. Must include "the authors take full responsibility for the content." |
| Preferred disclosure location | Paper body — a dedicated paragraph in the paper, typically at the end of the Introduction or in Acknowledgements |
| Prohibited uses | None explicitly prohibited, but fabricated citations or results would violate general scientific integrity policies |
| Authorship rule | AI tools cannot be listed as authors |

---

## Venue: ICMJE (International Committee of Medical Journal Editors — umbrella recommendations)

| Field | Value |
|---|---|
| Source URL | https://www.icmje.org/recommendations/browse/roles-and-responsibilities/defining-the-role-of-authors-and-contributors.html (§II.A.4); https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-authors.html (Section V.A) |
| Access date | 2026-08-01 |
| Policy summary | ICMJE Recommendations §II.A.4 "Artificial Intelligence (AI)-Assisted Technology" plus the standalone chapter Section V "Use of Artificial Intelligence in Publishing" (V.A Use of AI by Authors; V.B Use of AI by Reviewers; V.C Editors' Role in Ensuring Responsible Use of AI) — the umbrella policy layer used alongside the instructions of participating journals, including NEJM, The Lancet, JAMA, and BMJ. Authors should disclose AI-assisted technology use at submission; AI cannot be an author or be cited as an author; humans remain responsible for all submitted material. Section V.A advises authors to carefully review and edit AI-generated content and requires appropriate attribution and full citations for quoted material; "Referencing AI-generated material as the primary source is not acceptable"; nondisclosure of AI use "may require corrective action and may be construed as misconduct in some circumstances". |
| Required phrasing elements | Disclose whether and how AI-assisted technologies were used, both in the cover letter and in the submitted work itself. |
| Preferred disclosure location | **Cover letter AND in the work**: writing assistance → **Acknowledgments**; AI use in data collection / analysis / figure generation → **Methods**. |
| Prohibited uses | Listing AI as author or co-author; citing AI as an author; referencing AI-generated material as the primary source. The recommendation that authors carefully review and edit AI output is recorded in the summary as advice, not converted here into a separate prohibited-use condition. |
| Authorship rule | "Chatbots (such as ChatGPT) should not be listed as authors because they cannot be responsible for the accuracy, integrity, and originality of the work, and these responsibilities are required for authorship" |
| Notes | Umbrella recommendations, not a journal: the source says authors should use these recommendations **alongside** the target journal's instructions. The NEJM / The Lancet / JAMA / BMJ rows record both the ICMJE relationship and each journal's own clauses. The standalone Section V spans the full publishing workflow — AI use by authors (V.A), by peer reviewers (V.B), and the editors' role in ensuring responsible AI use (V.C); only the author-side clauses are summarized in this row. The #108 anchor track separately carries an `icmje` policy anchor (16-field matrix). |

---

## Venue: International Eye Science (国际眼科杂志)

| Field | Value |
|---|---|
| Source URL | Official submission guide: https://gjyk.ijournals.cn/gjykcn/site/menu/20120104163914001 ; GenAI notice: https://gjyk.ijournals.cn/uploadfile/gjykcn/20260423/%E7%94%9F%E6%88%90%E5%BC%8F%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%B7%A5%E5%85%B7%E5%90%AF%E4%BA%8B.pdf ; Data Management Policy: https://gjyk.ijournals.cn/uploadfile/gjykcn/20260423/%E3%80%8A%E5%9B%BD%E9%99%85%E7%9C%BC%E7%A7%91%E6%9D%82%E5%BF%97%E3%80%8B%E6%95%B0%E6%8D%AE%E7%AE%A1%E7%90%86%E6%94%BF%E7%AD%96.pdf |
| Access date | 2026-08-01 |
| Policy summary | The live submission guide directs authors to both 《关于规范使用生成式人工智能工具的启事》 (Notice on Regulating the Use of Generative AI Tools; editorial office, dated 2025-11-22) and 《国际眼科杂志》数据管理政策 (Data Management Policy; same date). The notice limits AIGC tools to non-core research steps: “生成式人工智能工具的应用，仅限于语言润色、文献检索、数据整理等非核心研究环节” (English paraphrase: language polishing, literature search, data organization, and comparable non-core steps). Section 4 of the companion data policy permits only auxiliary data organization, chart annotation, and preliminary literature retrieval subject to author checking, and separately governs AIGC data disclosure, privacy, ethics, and fabrication. Nondisclosure is treated as concealment and leads to rejection or retraction; the editorial office reserves long-term post-publication audit rights. |
| Required phrasing elements | Tool name and version, purpose of use, scope of use, and the proportion of generated content; whenever the use involves data (including data organization or chart annotation), additionally the data types and their verification status; when clinical/case data are involved, also disclose the de-identification measures. |
| Preferred disclosure location | **Timing: at submission.** Neither the notice nor the companion data policy identifies a manuscript section or submission-system field; “at submission” is timing rather than a named location. |
| Prohibited uses | Full or core generation of main text, research conclusions, experimental analysis, academic viewpoints, or innovation claims; fabricating experimental plans, technical routes, or citations; replacing the author in experimental design or data validation; fabricating experimental data, inventing research results, or tampering with experimental conclusions; using AIGC to generate/tamper with data or replace core analysis; uploading unde-identified data or data lacking required ethics review to AIGC; fabricating related data/ethics proof; rewriting plagiarized work with AI to evade detection; generating peer-review responses, grant statements, contribution statements, or integrity pledges; listing AIGC as an author; using overseas AIGC tools without lawful Chinese qualification (verbatim: "严禁使用未取得合法合规资质的境外AIGC工具"); uploading secret research data or unpublished experimental results to public AI platforms. |
| Authorship rule | AIGC tools cannot be listed as authors |
| Notes | One of the database's first two Chinese-language policy targets (with the publisher-wide Chinese Nursing Journals Publishing House entry); this one is a journal. The required "proportion of generated content" is a reporting element only — the policy publishes no acceptance threshold, and none is recorded here. The GenAI notice cites the AI-content-labelling standard as `GB 45221-2025`; the official national-standard record identifies 《网络安全技术 人工智能生成合成内容标识方法》 as `GB 45438-2025` (https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=F32EA2A561F1886CD8D606513512D547&refer=outter). The source wording is preserved here with this upstream-error caveat. The venue's own "AI-rewriting to evade detection" prohibition parallels ARS's no-detection-evasion principle. |

---

## Venue: JAMA (JAMA Network)

| Field | Value |
|---|---|
| Source URL | Official: https://jamanetwork.com/journals/jama/pages/instructions-for-authors ; exact stable snapshot: https://web.archive.org/web/20260701223416/https://jamanetwork.com/journals/jama/pages/instructions-for-authors |
| Access date | 2026-08-01 (live official page verified in a browser; the cited exact official-URL snapshot is from 2026-07-01 and is not a complete capture of the current manuscript-class prohibitions) |
| Policy summary | "Instructions for Authors", AI sections ("Use of AI in Publication and Research" plus the authorship clauses). The policy is restrictive-by-default: submission and publication of AI-created content "is discouraged, unless part of formal research design or methods, and is not permitted without clear description of the content that was created" plus identification of the model or tool (name, version and extension numbers, manufacturer). Authors must review and confirm the accuracy of AI-generated content and remain accountable for it. Where AI assisted with content creation, revision, or formatting, the use must be reported in the Acknowledgment section. For any AI used in a scientific study, authors must address AI-specific rights conditions and describe the specific research use; only studies using LLMs trigger the platform/tool/version/manufacturer/date and prompt-sequence/revision details. The guidance does not apply to basic tools for checking grammar or spelling. It says AI should not be used to generate or format references and recommends standard reference managers; this is retained as guidance rather than restated as an explicit "not permitted" rule. |
| Required phrasing elements | For manuscript-preparation AI: platform/program/tool name, model or tool version **and extension number(s) when applicable**, manufacturer, date(s) of use, a description of how AI was used and on which portions of the manuscript/content, confirmation that the authors reviewed and confirmed the accuracy of generated content, and confirmation that they take responsibility for its integrity. For any scientific-study AI use, describe the specific research use. The policy separately addresses two conditional rights cases. If copyright-protected content was entered into the model/tool, **include a copy** of the copyright-holder permission/license with the submission **and separately describe** that permission/license in Methods. If AI-generated text, images, or multimedia are included in the submitted work, state the rights or permission to publish **as determined by the AI service or owner** in Methods or the relevant legend. Only for a study using an LLM: also report platform/program/tool name, version, manufacturer, date(s), prompt(s), their sequence, and any prompt revisions made in response to initial outputs. |
| Preferred disclosure location | **Acknowledgment section** (manuscript-preparation AI); **Methods** (research AI and the description of any triggered copyright-input permission/license); publication-rights information for included AI-generated content → **Methods or the relevant figure legend**, as applicable. The required permission/license copy is a separate submission-package item; the policy does not designate it as text to paste into Methods. |
| Prohibited uses | Using AI/LLMs/chatbots to draft **Opinion manuscripts, Letters to the Editor, Online Comments, A Piece of My Mind, or Poetry**; submitting AI-created content without a clear description and identification of the model/tool; submitting clinical images or clinical illustrations created or manipulated by these technologies unless they are part of a formal research design or method that is fully disclosed. |
| Authorship rule | "Nonhuman artificial intelligence, language models, machine learning, or similar technologies do not qualify for authorship." |
| Notes | JAMA is an ICMJE member journal; the ICMJE umbrella recommendations and JAMA's Instructions for Authors are simultaneously relevant sources. These AI-specific clauses are not a complete JAMA Methods/reporting checklist; current study-design, reporting-guideline, ethics, data-sharing, and other applicable rights/licensing instructions remain separately applicable. The reference sentence uses “should not” for AI/LLM/chatbot generation or formatting of references, rather than JAMA's stronger “not permitted” wording for the manuscript classes and clinical-image cases listed above. A Piece of My Mind and Poetry drafting clauses were verified on the live official page on 2026-08-01 and are absent from the cited 2026-07-01 snapshot. No later exact official-URL snapshot was available when checked, so the runtime prohibition is retained with this evidence gap stated explicitly. |

---

## Venue: Nature (Nature Publishing Group)

**Policy-source dedup pointer:** Nature's substantive AI policy text is co-cited by the #108 policy-anchor renderer (`policy_anchor_table.md` Nature section, verbatim quotes per 16 fields). Both consumers reference the canonical source pointer `shared/policy_data/nature_policy.md` so a future single-source-of-truth refactor can extract Nature's policy text without breaking either consumer's substantive content. Dedup invariant lint: `verify_nature_dedup_with_venue` in `scripts/check_policy_anchor_table.py`.

**Derivation note (#108 scope limitation):** the venue-track summary fields below (Policy summary / Required phrasing elements / Preferred disclosure location / Prohibited uses / Authorship rule) **are derived** from `shared/policy_data/nature_policy.md` but are **not auto-generated from it** — the v3.2 venue path predates the canonical source and continues to drive runtime rendering off these summary rows. If Nature's source policy drifts, **the canonical source file MUST be updated first** (per the G4 invariant) and these summary rows **MUST be reviewed and updated in the same change**. A future refactor (out of #108 scope) can replace these summary rows with an extract from the canonical source so the dedup contract is auto-enforced; until then this section is a derived view that requires manual sync.

| Field | Value |
|---|---|
| Source URL | https://www.nature.com/nature/editorial-policies/ai |
| Access date | 2026-04-09 |
| Policy summary | Authors who use AI tools — including LLMs — in the writing of a manuscript, production of images, or other elements of the research must document this use transparently in the Methods or Acknowledgements section. LLMs cannot be listed as authors. Authors are responsible for the accuracy of AI-generated content. |
| Required phrasing elements | Must name the tool and describe how it was used. Must state authors verified and take responsibility for all content. Nature encourages detailed descriptions. |
| Preferred disclosure location | **Methods section** (recommended by Nature) or Acknowledgements. Also mention in the cover letter. |
| Prohibited uses | AI-generated text or images cannot be presented as original human work without disclosure. Fabrication of references or data is prohibited under general integrity policy. |
| Authorship rule | AI tools cannot meet authorship criteria (accountability requirement) and must not be listed as authors |
| Notes | Lu et al. (2026, Nature 651:914-919) provides a worked example: their AI Scientist paper includes full disclosure in Methods and Ethics Statement, with explicit IRB-style approval for the human reviewer participation. |

---

## Venue: NEJM (The New England Journal of Medicine)

| Field | Value |
|---|---|
| Source URL | Official: https://www.nejm.org/about-nejm/editorial-policies ; exact current snapshot: https://web.archive.org/web/20260731132825/https://www.nejm.org/about-nejm/editorial-policies |
| Access date | 2026-07-31 (live official URL is bot-walled to non-browser clients; the exact official-URL snapshot above was captured and re-verified against the current page) |
| Policy summary | "Editorial Policies", section "Author Use of AI-Assisted Technologies". Authors must disclose at submission whether AI-assisted technologies were used (ICMJE-aligned). The current policy says authors **must carefully review and edit all materials produced with AI**; they must be able to assert that AI-produced text/images contain no plagiarism and must properly attribute quoted material with full citations. These are current obligations, not advice inherited from the older 2025 snapshot. |
| Required phrasing elements | Describe at submission which AI-assisted technologies were used and what the technology produced; confirm that the authors carefully reviewed and edited the AI-produced material and can assert that it contains no plagiarism; include attribution and full citations for quoted material. |
| Preferred disclosure location | At submission, in **both the cover letter and the submitted work**. |
| Prohibited uses | Listing AI as an author; plagiarism in AI-produced text or images; "Citation of AI-generated material as a primary source is not acceptable." |
| Authorship rule | "Because the authors of a manuscript are responsible for the accuracy, integrity, and originality of the work, chatbots or other AI-assisted technologies cannot be listed as authors." |
| Notes | NEJM is an ICMJE member journal. The ICMJE umbrella recommendations and NEJM's own Editorial Policies are simultaneously relevant sources; neither source states that it silently replaces the other. |

---

## Venue: NeurIPS (Conference on Neural Information Processing Systems)

| Field | Value |
|---|---|
| Source URL | https://neurips.cc/public/EthicsGuidelines |
| Access date | 2026-04-09 |
| Policy summary | Authors must disclose any use of generative AI or LLMs during manuscript preparation, including writing, coding, and data analysis. Full responsibility lies with the human authors. |
| Required phrasing elements | Must specify tool name, version if known, and specific tasks. Must state authors reviewed all AI-generated content. |
| Preferred disclosure location | Acknowledgements section or a separate "Use of AI Tools" subsection before References |
| Prohibited uses | Cannot use AI to fabricate or falsify data. Cannot list AI as author. |
| Authorship rule | AI tools cannot be listed as authors |

---

## Venue: PLOS (PLOS journals)

| Field | Value |
|---|---|
| Source URL | https://journals.plos.org/plosone/s/ethical-publishing-practice |
| Access date | 2026-08-01 |
| Policy summary | "Ethical Publishing Practice", section "Artificial Intelligence Tools and Technologies". Contributions by AI tools / LLMs to a submission must be clearly reported; authors must ensure the accuracy and validity of AI-assisted content, cite original sources, and ensure that hypotheses, interpretations, and conclusions remain the authors' own. |
| Required phrasing elements | Tool name(s), how the tool was used, how its outputs were validated, and which parts of the work were AI-affected. |
| Preferred disclosure location | A dedicated part of **Methods** (or Acknowledgements if the article type has no Methods section). |
| Prohibited uses | Using AI to fabricate or misrepresent primary research data — "The use of AI tools and technologies to fabricate or otherwise misrepresent primary research data is unacceptable." Reviewers/editors uploading submissions to generative AI platforms. Noncompliance leads to rejection, retraction, or a published notice. |
| Authorship rule | No explicit AI-authorship prohibition on this policy page as of 2026-08-01. The policy expects that articles "report the listed authors' own work and ideas" and that "Contributions by artificial intelligence (AI) tools and technologies to a study or to an article's contents must be clearly reported" — AI contributions are handled via disclosure, not authorship. |

---

## Venue: Science (AAAS)

| Field | Value |
|---|---|
| Source URL | https://www.science.org/content/page/science-journals-editorial-policies |
| Access date | 2026-04-09 |
| Policy summary | Authors must disclose any use of AI-generated text, figures, or data in the manuscript. The use of AI writing tools must be documented in the Acknowledgements section or in Materials and Methods. AI tools are not authors. |
| Required phrasing elements | Must identify the AI tool by name. Must indicate which parts of the manuscript were aided by the tool. Must affirm that authors verified the accuracy of all AI-generated content. |
| Preferred disclosure location | **Acknowledgements** (preferred) or **Materials and Methods** |
| Prohibited uses | AI-generated text submitted without disclosure violates editorial policy. Fabricated figures or data are prohibited. |
| Authorship rule | AI tools cannot be listed as authors; all listed authors must meet ICMJE criteria |

---

## Venue: The Lancet

| Field | Value |
|---|---|
| Source URL | The Lancet Information for Authors: https://www.thelancet.com/pb/assets/raw/Lancet//authors/lancet-information-for-authors.pdf ; exact official-URL snapshot of that original URL: https://web.archive.org/web/20250713081908/https://www.thelancet.com/pb/assets/raw/Lancet//authors/lancet-information-for-authors.pdf ; current Elsevier journal policy: https://www.elsevier.com/en-gb/about/policies-and-standards/generative-ai-policies-for-journals |
| Access date | 2026-08-01 (the exact Lancet PDF capture is reproducible; Elsevier's policy was live-verified) |
| Policy summary | The Lancet author-information PDF served at its current official URL identifies the journal as an ICMJE signatory; its publisher's current journal policy governs generative-AI use. For manuscript preparation, authors should disclose AI-tool use in a separate declaration; basic spelling, grammar, and punctuation checks do not require declaration, while substantive changes do. Specialist assistive technology used solely for accessibility is also outside the declaration requirement. AI used in the research process must be described in detail in Methods. Elsevier now distinguishes explanatory images, data visualizations, primary research images, research-method images, graphical abstracts, and cover art instead of applying the superseded blanket image rule. General-purpose generative-AI image tools must not create graphical abstracts; dedicated scientific illustration or other professional illustration tools are the permitted path, with the tool named in the image caption and with publication rights checked. AI-generated cover art is conditionally permitted only after prior permission from both the journal editor and publisher. Authors remain responsible for image accuracy, originality, rights, and attribution. |
| Required phrasing elements | Manuscript-preparation declaration: tool/service name, purpose/reason, extent of human oversight, confirmation that authors reviewed and edited the content as needed, and confirmation of full author responsibility. Research-process use: reproducible Methods detail. For every otherwise permitted submitted visual, verify accuracy and originality and, when based on existing artwork/graphics, record attribution and rights-holder permission. Explanatory-image use: disclose the tool, version, and how it was used in each image caption and in the general declaration. Data-visualization use: model/tool name, version, and developer/manufacturer in Methods. Research-method-image use: name, version, and developer/manufacturer when applicable. Permitted AI-assisted graphical-abstract use: name the dedicated scientific or professional illustration tool in the graphical-abstract image caption and confirm that its terms provide the necessary publication rights. AI-generated cover art: prior editor and publisher permission, permissions for any third-party material used, and appropriate content attribution. |
| Preferred disclosure location | Manuscript preparation → a separate **"Declaration of generative AI and AI-assisted technologies in the manuscript preparation process" immediately before the references**. Research-process use, AI-generated data visualizations, and permitted research-method-image use → **Methods**. Explanatory images → **each image caption AND the general declaration**. Permitted AI-assisted graphical-abstract illustration-tool use → **the graphical-abstract image caption**. Cover-art approval and rights evidence are pre-submission permission actions, not a manuscript disclosure location. |
| Prohibited uses | Listing or citing an AI tool as an author; fabricating or altering research data, results, or references; using AI to create or alter primary research images representing observed/experimental data that were not directly obtained in the research (formal AI-assisted research-design/method use remains the reproducibly disclosed exception); using general-purpose generative AI for graphical abstracts; generating images that duplicate or refer to existing copyrighted images, real people, others' identifiable products/brands, or any likeness of an individual's voice. AI use may not replace the authors' intellectual contribution. |
| Authorship rule | AI tools must not be listed as authors or co-authors, nor cited as authors; accountable human authors approve and take responsibility for the final work. |
| Notes | The superseded February-2025 `tl-info-for-authors.pdf` is deliberately not used. The reproducible Lancet author-information PDF identifies the journal's ICMJE relationship but is dated May 2019 and contains no generative-AI clause; it is not presented as the source of the current AI rules. Those rules come from Elsevier's current journal policy. The ICMJE recommendations and Lancet/Elsevier instructions are simultaneously relevant sources; neither source states that it silently overrides the other. |

---

## Adding a new venue (v2 and beyond)

To add a venue to this database:

1. Find the venue's current AI-usage policy page (not a third-party summary).
2. Copy the structured fields above.
3. Fill in each field with verbatim or closely-paraphrased policy text.
4. Record the source URL and date accessed.
5. Add the venue entry to this file in alphabetical order.
6. Add explicit selector aliases, applicability predicates, and required/conditional facts to `disclosure_mode_protocol.md`; do not rely on the policy prose to create a second implicit mapping.
7. Update the "Scope" line and the user-facing selector/count surfaces.

For venues without a published AI policy: record "No explicit AI-usage policy found as of {date}" for database maintenance, but do not add the target to the runnable selector set. Runtime behavior for unknown/no-policy targets is defined only in `disclosure_mode_protocol.md`.

**Education/QA journals** still targeted for a future revision (deferred at v2, which added medical venues instead): Higher Education, Quality in Higher Education, Studies in Higher Education, Assessment & Evaluation in Higher Education, Journal of Higher Education Policy and Management. These will require separate research as their policies are less standardized than ML/NLP venues.
