Launched `bibliography_agent` to retrieve, deduplicate, and extract WHY/HOW/WHAT profiles for three peer-reviewed scholarly works on Japan in the Second World War. Waiting for its Phase 2 deliverable before dispatching `source_verification_agent`.
`bibliography_agent` is still actively querying OpenAlex and fetching source metadata; continuing to wait for its completion.
`bibliography_agent` completed retrieval and `abstract_only` WHY/HOW/WHAT extraction for three peer-reviewed articles. Now running `source_verification_agent` for independent citation, venue, author, COI, and evidence-quality verification.
# Three-Way Literature Scan (`three-way-scan`): Japan in the Second World War

**Mode**: `deep-research` → `three-way-scan` (WHY / HOW / WHAT paper comparison)  
**Search Date**: `2026-11-13` | **Corpus Size**: 3 peer-reviewed journal articles (selected from 131 identified records; 116 unique after deduplication)  
**Read Scope**: `abstract_only` + bibliographic/venue API metadata for all 3 works (publisher/OA full-text URLs and `doi.org` returned `HTTP 403` in the sandbox; no bypass attempted).

---

## 1. Per-Paper WHY / HOW / WHAT Profiles

## The promise of role reversal as dream and nightmare: Japan’s occupation of Java in the Second World War as global history
Source: OpenAlex (`W4414498233`), Crossref, Semantic Scholar (`00228705aa0329b569f2a3539cdbdae8ec099137`), WebSearch | Year: 2026 (print; online 2025) | Link: https://doi.org/10.1080/07075332.2025.2563803  
*APA 7.0*: Mark, E. (2026). The promise of role reversal as dream and nightmare: Japan’s occupation of Java in the Second World War as global history. *The International History Review*, *48*(2), 258–273. https://doi.org/10.1080/07075332.2025.2563803  
*Verification & Read Scope*: `S2_VERIFIED` + `VERIFIED` (CR/OA + WebSearch) | `not_retracted` | **Provisional Grade B** (Level VI Humanities; A-eligible pending full text) | Read: `abstract_only`

- **WHY**: Framing Japan's WWII occupations monolithically as nightmares of Asian suffering obscures structural differences between North Asia and Southeast Asia—specifically how prior Western colonial rule in Java shaped local receptivity to Japan's anti-colonial rhetoric and Japanese self-perceptions.
- **HOW**: Global-historical and ideological-comparative analysis of the Japanese occupation of Java (Dutch East Indies), contrasting Japanese occupiers' and Southeast Asian subjects' perceptions of early military victories over Western empires and examining the tension between pan-Asian liberationist claims and imperial rule.
- **WHAT**: Argues that Japan's Southeast Asian occupations were uniquely "revolutionary" among WWII occupations because early victories over Western powers and initial local welcomes fostered a Japanese vision of world-historical "role reversal" (simultaneously new Asian hegemon and putative anti-imperial liberator/model), foreshadowing the postwar global order of decolonizing nation-states. Unresolved at `abstract_only`: granular administrative mechanics in Java and local collaboration/resistance trajectories.
  - **Method weaknesses**: not assessed (read scope: abstract_only)

## Japan’s forgotten Korean forced laborers: The search for hidden wartime graves in Hokkaido
Source: OpenAlex (`W4393444356`), Crossref, Semantic Scholar (`7bb15fa09ce4de600b5bd9fe103762ef822a23f9`), WebSearch | Year: 2024 | Link: https://doi.org/10.1017/s0147547924000048  
*APA 7.0*: Duró, Á., & Palmer, D. (2024). Japan’s forgotten Korean forced laborers: The search for hidden wartime graves in Hokkaido. *International Labor and Working-Class History*, *106*, 311–330. https://doi.org/10.1017/s0147547924000048  
*Verification & Read Scope*: `S2_VERIFIED` + `VERIFIED` (CR/OA + WebSearch) | `not_retracted` | **Provisional Grade B** (Level VI Humanities/Social History; A-eligible pending full text; intellectual/advocacy stance noted) | Read: `abstract_only`

- **WHY**: While nearly 800,000 Koreans were forcibly mobilized to at least 1,589 worksites in Japan (381 in Hokkaido) during 1940–1945 and over 10% across the empire are estimated to have died or disappeared, the exact wartime death toll inside Japan and individual victims' identities and causes of death remain unknown—compounded by pre-1989 immediate cremation practices.
- **HOW**: Empirical historical and civil-society case documentation tracing the first comprehensive post-1989 effort by Korean and Japanese activists and academics in Hokkaido to locate and exhume Korean forced laborers' graves without immediate cremation.
- **WHAT**: Shows that the Hokkaido exhumation initiative recovered a neglected chapter of wartime forced labor and supported bereaved Korean families, yet reveals severe evidentiary gaps: operating in a difficult political climate and neglecting forensic science protocols during mass excavations prevented definitive identification of victims' names and causes of death required for state/corporate accountability. Unresolved: exact mortality inside Japan and forensic identification of remaining victims.
  - **Method weaknesses**: not assessed (read scope: abstract_only)

## Measuring the time‐varying market efficiency in the prewar and wartime Japanese stock market, 1924–1943
Source: OpenAlex (`W4401550022`), Crossref, Semantic Scholar (`a55b180906507503a6c109fcfbbe4356906a75ac`), WebSearch | Year: 2025 (print; online 2024; S2 merges 2019 `arXiv:1911.04059`) | Link: https://doi.org/10.1111/aehr.12297  
*APA 7.0*: Hirayama, K., & Noda, A. (2025). Measuring the time‐varying market efficiency in the prewar and wartime Japanese stock market, 1924–1943. *Asia‐Pacific Economic History Review*, *65*(1), 131–159. https://doi.org/10.1111/aehr.12297  
*Verification & Read Scope*: `S2_VERIFIED` + `VERIFIED` (CR/OA + WebSearch) | `not_retracted` | **Provisional Grade B** (Level IV Economic History; A-eligible pending full text; JST/JSPS funding disclosed; first author's corporate financial affiliation noted) | Read: `abstract_only`

- **WHY**: Tests how Japan's prewar and wartime mobilization and escalating state controls altered capital market efficiency between 1924 and 1943, and whether earlier studies were distorted by using non-capitalization-weighted stock indices.
- **HOW**: Quantitative historical econometrics applying Andrew Lo's Adaptive Market Hypothesis (AMH) to a newly constructed market-capitalization-weighted stock price index for the prewar and wartime Japanese stock market (1924–1943).
- **WHAT**: Finds that (1) Japanese stock market efficiency varied substantially over time alongside major historical events (supporting AMH); (2) this time-varying trajectory diverges notably from prior studies; and (3) efficiency declined while war risk premiums rose as government market intervention intensified in the 1930s and the Pacific War became inevitable. Unresolved at `abstract_only`: exact econometric breakpoints, part-paid stock adjustments, and post-1943 wartime market closure dynamics.
  - **Method weaknesses**: not assessed (read scope: abstract_only)

---

## 2. Cross-Paper Synthesis

- **Common `WHY`**: All three works challenge oversimplified, static narratives of Imperial Japan in WWII by re-examining neglected structural mechanisms—ideological contradictions in occupied Southeast Asia (Mark, 2026), unrecorded human costs and evidentiary gaps in domestic forced labor (Duró & Palmer, 2024), and the dynamic erosion of market pricing under wartime state control (Hirayama & Noda, 2025).
- **Divergent `HOW`**: The shortlist spans three distinct disciplinary paradigms and evidence bases:
  1. *Transnational/global intellectual history* comparing imperial and subject perceptions in occupied Java (Mark, 2026);
  2. *Grassroots/archival social history* documenting post-1989 exhumations and civil-society mobilization in Hokkaido (Duró & Palmer, 2024);
  3. *Cliometric time-series econometrics* constructing a capitalization-weighted index (1924–1943) under the Adaptive Market Hypothesis (Hirayama & Noda, 2025).
- **Strongest `WHAT` (Provisional at `abstract_only`)**: Because full texts were inaccessible (`HTTP 403`), comparative empirical strength cannot be adjudicated at full-text depth. At the abstract/metadata level, **Hirayama & Noda (2025)** offers the most sharply bounded, falsifiable empirical finding (demonstrating that capitalization-weighting overturns prior efficiency estimates and quantifying declining efficiency alongside rising war risk premiums up to 1943), whereas **Duró & Palmer (2024)** contributes an unusually candid internal critique of evidentiary failure (showing how non-forensic excavations undermined legal accountability), and **Mark (2026)** provides the broadest historiographical reframing linking Japanese occupation ideology to postwar decolonization.
- **Unresolved Global Gap**:
  1. *Domain gap*: None of the three works bridges Japan's **internal economic/labor mobilization** (home islands + colonial Korea) with its **external occupation governance** (Southeast Asia) in an integrated imperial-system framework, and English-language selection excludes Japanese- and Korean-language primary historiography.
  2. *Verification gap*: All three works require full-text reading outside the proxy-restricted sandbox to audit primary archival citations, quantitative estimates (e.g., Korean forced labor counts), and econometric specifications.

---

## 3. Search Strategy, Triangulation & Escalation

- **Search & Deduplication Summary**: Queried OpenAlex (100 records from 1,586 title-search hits), Crossref (25), WebSearch (6), and Semantic Scholar (`/paper/search` hit `HTTP 429` rate limit; degraded gracefully). Removed 15 duplicates via DOI/S2 ID/title match; screened 116 unique records; assessed 14 candidates at Pass 2; selected 3 recent (2024–2026) peer-reviewed articles across distinct publishers (Taylor & Francis, Cambridge University Press, Wiley).
- **Distributional Skew Advisory (Step 4.6)**: Time distribution `2020s = 3/3 (100%)` (intentional recency filter); Venue tier `peer-reviewed hybrid OA journal articles = 3/3 (100%)` (user requested three scholarly works).
- **Citation & Existence Verification Summary**: All 3 works verified (`HTTP 200`) across Semantic Scholar (`DOI:{doi}`), Crossref, OpenAlex, and `search_web`; `0` retractions (`is_retracted=false`, no Crossref update notices); all 3 journals confirmed indexed and peer-reviewed with `0` predatory flags.
- **Next Step / Escalation**: To expand into a broader thematic evidence matrix, escalate from `three-way-scan` to `lit-review` mode (or retrieve the three open-access/institutional full texts outside the sandbox proxy for full methodological appraisal). Escalate to `systematic-review` only if you explicitly choose a formal systematic review.

---

## 4. AI-Use & Platform Disclosure

- **Platform & Model**: Antigravity running **Gemini 4 Hydrogen (High)**.
- **Subagent Dispatch (Rule 4)**: `bibliography_agent` and `source_verification_agent` ran as separate, isolated subagents (`invoke_subagent`) using their complete ARS agent prompts and the session model (Claude `model:` hints do not apply on Antigravity). The compact `three-way-scan` cross-paper synthesis above was assembled inline by the orchestrator (consistent with `deep-research/SKILL.md`, which assigns `Biblio + Verification` to `three-way-scan`).
- **Verification & Read-Scope Degradation (Rule 5)**: Every citation was verified against Semantic Scholar (`DOI:{doi}`), Crossref, OpenAlex, and `search_web`. However, Semantic Scholar `/paper/search` returned `HTTP 429` during broad discovery, and `https://doi.org/{doi}` as well as publisher/repository full-text URLs returned `HTTP 403` under sandbox network restrictions. Accordingly, all 3 works are reported at `read scope: abstract_only` (full text not opened), `Method weaknesses` are marked `not assessed (read scope: abstract_only)`, and underlying full-text claims remain unverified beyond abstract/metadata checks.
- **Write-Scope Enforcement (Rule 7)**: Antigravity does not run the ARS `PreToolUse` write-scope hook; Phase 2 boundaries were enforced at the prompt/orchestrator level, and no files were modified under `<ARS_ROOT>`.
