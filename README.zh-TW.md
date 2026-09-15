# Academic Research Skills for Claude Code

[![Version](https://img.shields.io/badge/version-v3.21.2-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.21.2)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20696614-blue)](https://doi.org/10.5281/zenodo.20696614)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[English](README.md) | [简体中文版](README.zh-CN.md) | [日本語版](README.ja-JP.md) | [한국어](README.ko-KR.md) | [Español](README.es-ES.md)

一套完整的學術研究 Claude Code 技能包，涵蓋從研究到論文出版的全流程。

**30 秒安裝**（Claude Code CLI / VS Code / JetBrains，v3.7.0+）：

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

裝完跑 `/ars-plan`，ARS 會用蘇格拉底對話幫你規劃章節結構。需要前置條件或傳統 symlink 安裝請看 [快速安裝](#快速安裝)。

> **AI 是你的副駕駛，不是機長。** 這工具不會幫你寫論文。它處理苦工 — 搜文獻、排格式、驗數據、查邏輯一致性 — 讓你專注在真正需要你腦子的事：定義問題、選方法、詮釋數據的意義、寫出「我認為」後面那句話。
>
> 跟 humanizer 不同，這工具不是幫你隱藏用 AI 協作的事實，而是幫你把關文章品質。風格校準從你過去的文章學習你的聲音，寫作品質檢查抓出讓文字讀起來像機器產的模式。目標是品質，不是遮掩。

### 為什麼選「人機協作」而不是「全自動」？

Lu 等人（2026，*Nature* 651:914-919）發表的 **The AI Scientist** 是第一個端到端全自動的 AI 研究系統，其生成的論文通過 ICLR 2025 workshop 的盲審（評分 6.33/10，workshop 平均 4.87）。他們自己的 Limitations 段落也列出了這類系統會遇到的結構性失敗模式：實作錯誤、幻覺實驗結果、取巧特徵依賴、實作錯誤被包裝成「意外發現」、方法論偽造、框架鎖定、引用幻覺。

ARS 建立在這個前提上：**人類研究者 + AI 的組合，比純自動或純人工都更能避開這些失敗模式**。Stage 2.5 與 Stage 4.5 誠信閘門執行 7 類阻斷式檢查清單（見 [`academic-pipeline/references/ai_research_failure_modes.md`](academic-pipeline/references/ai_research_failure_modes.md)），reviewer 也提供 opt-in 的 calibration mode 用使用者自備的 gold set 測量 FNR/FPR。

[**Zhao 等人**](https://arxiv.org/abs/2605.07723)（2026-05）盤點了 arXiv、bioRxiv、SSRN、PMC 上 250 萬篇論文裡的 1.11 億筆引用，保守估計 2025 年單年就有 146,932 筆幻覺引用，並觀察到 2024 年中是上升的拐點；bioRxiv-to-PMC 這條配對的「預印本進到正式發表」幻覺存活率達 85.3%。他們把「真實引用被用來支撐被引文獻其實沒有提出的主張」描述為當前未解的問題。ARS v3.7.1 為來源 provenance 加上 trust-chain frontmatter，v3.7.3 為未來的 claim-level 稽核鋪上 locator 基礎建設（三層引用 anchor），並在引用時段帶出 advisory 風險訊號（ARS 內部把這條 claim-faithfulness 缺口標記為「L3」，此為 ARS 的用詞，不是論文的用詞）。v3.7.x 的設計動機來自 Zhao 等人的 corpus-scale 發現；ARS 本身的 corpus-scale 評估仍是未來工作。

v3.8 補上 L3 缺口的另一半。v3.7.3 讓每一筆引用都帶 locator anchor，v3.8 在這個基礎上加一道 opt-in 稽核（`ARS_CLAIM_AUDIT=1`）：抓回每一個 anchor 指向的原始文本，判斷論文裡的 claim 是否真有被該引用支撐。五類新的 HIGH-WARN annotation（claim-not-supported、negative-constraint-violation、fabricated-reference、anchorless、constraint-violation-uncited）會在 formatter terminal hard gate 直接攔下輸出。Calibration 隨 release 出 20 筆 gold set，採 FNR<0.15、FPR<0.10 雙閾值；正式放大投入前要先有 calibration 證據（v3.8 spec §5）。

[**Ren 等人**](https://arxiv.org/abs/2607.13104)（2026，*Self-Improvements in Modern Agentic Systems: A Survey*）補上第三個、survey 層級的錨點。其科學發現章節的綜合結論（§7.4）指出：發現型 agent 難以自行驗證 novelty、正確性與可重現性，反而可能鑽弱代理指標的漏洞；證據管理必須跨異質工具與文獻維持；並帶有治理疑慮——「證據薄弱時，科學寫作也會放大錯誤資訊」。其生成迴圈章節（§5.1–§5.2）把人工稽核與保留人類標註列為自生成評估迴圈的實務防護；歷史章節（§2.2）則記下同一課題最早的版本：Lenat 的 EURISKO 的實務成功高度依賴使用者充當外部評估訊號、修剪無效的 heuristic 漂移——survey 明言此限制延續到現代 agentic 系統。ARS 引用這篇 survey 作為 human-in-the-loop 立場的設計依據，而非「人機協作必然勝過全自動」的實證證明；survey 對 ARS 可落地的增量記錄在 #539–#541 與 #547–#550。

[**Gartenberg 等人**](https://doi.org/10.1287/orsc.2026.ed.v37.n3)（2026，*Organization Science* 37(3):795-812，*More versus better*）補上第四個錨點，也是第一個來自期刊端的錨點。*Organization Science* 的 AI 工作小組用商用 AI 寫作分類器與標準可讀性指標，量了該刊 2021 年 1 月到 2026 年 2 月收到的全部首次投稿（6,957 篇）與文字型審查意見（10,389 份）。被判為大量由 AI 撰寫的稿件在這些指標上更難讀、也更常被 desk reject；AI 味較重的審查意見偏向理論、遠離資料；編輯群的結論是，現行 AI 工具加上「不發表就出局」的誘因，「看來正把系統推向『更多而非更好』的均衡」。其 §5 把「認知投降」（cognitive surrender，該文引 Shaw & Nave, 2026）與「人先行」的用法對比，並要求作者揭露稿件如何產出。這些證據是觀察性、總體層次、且只來自一本期刊，分類器也是專有工具。ARS 引用這篇社論作為「產量不是目標」（見 `POSITIONING.md`）、Collaboration Depth Observer 與 claim-strength ladder 的設計依據，不是關於 ARS 產出的證據；可落地的增量記錄在 #829–#833。

[**Wang、Li 等人**](https://arxiv.org/abs/2609.07713)（2026-09，*The Emerging AI Paper-Review Arms Race: Adversarial Co-Evolution in Scholarly Publishing*，整理 230 份文獻的 survey）補上第五個錨點，也是第一個把研究產出與同儕審查當成同一個耦合系統來看的錨點。其評估權限階梯（§4.1）從作者端回饋、審稿人輔助、正式 AI 審查，一路到評分與決策支援，並指出某一階的能力不能自動證成下一階的使用；ARS 的模擬 panel 依設計位於最低那一階（見 `POSITIONING.md`）。其中兩項發現形塑了 reviewer 的路線圖。第一，依該 survey 對 Dycke & Gurevych（2026，§4.5）的整理，391 個破壞論文科學支撐關係的改動，相較於 540 個不影響 soundness 的對照改動，在受測自動審稿者的評估面向、情緒與分數上都沒有統計顯著差異，而科學內容固定、只改呈現的改寫卻能移動 AI 審查分數（§5.2）；survey 在 §9.2 的結論是，一旦作者能觀察並適應 AI 審稿者，靜態評估可能高估其可靠度。ARS 把對應的第一輪配對控制記在 #871、作者身分線索的控制（§7.2）記在 #872；兩者都是量測，不是新機制。第二，其 §9.1 引用 Brodeur 等人（2026，*PNAS* 123(22):e2524747123）的隨機實驗：288 位研究者分成 103 隊，在三種條件下重現已發表的量化社會科學結果：純人類、AI 輔助（以 ChatGPT 為協作工具）、AI 主導（ChatGPT 在最少人工監督下運作）。純人類隊與 AI 輔助隊的重現率分別為 94% 與 91%，AI 主導隊為 37%，且 AI 輔助隊抓到的重大程式錯誤比純人類隊少。在該研究中，AI 輔助的驗證並沒有比人單獨做更好，AI 主導的驗證則差很多；ARS 把這讀成「每個檢查點的驗證都要由人主導」的理由，不是 ARS 自己的檢查點或 integrity gate 有效的證據。這篇 survey 是綜合而非實驗，結構化檢索止於 2026-07-01、之後的定向更新沒有重跑每一條檢索式（§10），部署證據集中在少數 AI／CS 會議、OpenReview 場域與特定期刊，「軍備競賽」是分析視角而非發現；ARS 引用它作為設計依據，不是關於 ARS 產出的證據。

v3.3 的靈感來自 [**PaperOrchestra**](https://arxiv.org/abs/2604.05018)（Song, Song, Pfister & Yoon, 2026, Google）：Semantic Scholar API 驗證、反洩漏協議、VLM 圖表驗證、修訂軌跡追蹤。ARS 目前以分類式、證據錨定的準則軌跡實作最後一項，不計算分數差。

---

## 架構與 pipeline

**👉 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — 完整 pipeline 視圖：流程圖、階段 × 維度矩陣、資料存取流、skill 依賴圖、品質閘門、模式清單。

這份架構文件取代了原本散在 README 各處的 pipeline 描述。關於「哪個階段跑什麼」的所有資訊都集中在一個地方。

## 快速安裝

**前置條件**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/setup)（建議最新版；plugin packaging 需要近期版本）
- 已 export `ANTHROPIC_API_KEY`，或第一次跑 `claude` 時設定
- *選用：* Pandoc 用於 DOCX 輸出，tectonic + 思源宋體 TC 用於 APA 7.0 PDF（純 Markdown 輸出兩個都不需要）

**Plugin 安裝（v3.7.0+，推薦）：**

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

**驗證可用：** 跑 `/ars-plan` 並描述你正在寫的論文，ARS 會用蘇格拉底對話幫你規劃章節結構。想要單次測試的話改跑 `/ars-lit-review "你的主題"`。

**👉 [docs/SETUP.zh-TW.md](docs/SETUP.zh-TW.md)** — 完整指南：安裝 Claude Code、設定 API key、選用的 Pandoc/tectonic（DOCX/PDF）、跨模型驗證（`ARS_CROSS_MODEL`），以及六種安裝方式（Plugin、專案 skills、全域 skills、claude.ai Project、repo clone、Claude Science 匯入）。

> **你的安裝管道實際啟用哪些控制機制？** 可用性依安裝管道而異，請查逐管道對照表：[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)（英文）。

**👉 [docs/DATA_FLOWS.md](docs/DATA_FLOWS.md)** — 哪些資料會離開你的電腦（書目 resolver、選用且需明確同意的跨模型呼叫、更新檢查）、本機快取存什麼與存多久、每條路徑怎麼關閉。（英文）

**使用 Claude Science？** 四個 skill 可直接匯入：**Skills → Import from GitHub**，貼上 `https://github.com/Imbad0202/academic-research-skills`，按 **Preview**，再按 **Import 4 skills**（需本 repo v3.14.0+——匯入器讀取 marketplace manifest 中明列的 skill 路徑）。匯入是單次快照：ARS 更新後需重新匯入。匯入的 skill 承載 ARS 方法論（研究／寫作／審查協定）；Claude Code 專屬機制——slash commands、hooks、subagent 編排——不會轉移。細節見 [docs/SETUP.zh-TW.md](docs/SETUP.zh-TW.md) 方法五。

**使用 Pi？** 執行 `pi install git:github.com/Imbad0202/academic-research-skills` 安裝 repo 內的社群維護 wrapper。它持續以原始 ARS 內容為準，並記錄 Pi 在編排與 hooks 方面的限制。詳見 [`pi/README.md`](pi/README.md)。

**用 Codex CLI？** 請改裝姊妹版：[`Imbad0202/academic-research-skills-codex`](https://github.com/Imbad0202/academic-research-skills-codex)。同一套 workflow 內容，Codex 原生包裝為單一 `$academic-research-suite` skill，提供 `ars-*` 別名。

## 效能與費用

**👉 [docs/PERFORMANCE.zh-TW.md](docs/PERFORMANCE.zh-TW.md)** — 各模式 token 預算、完整 pipeline 估算（一篇 15k 字論文約 ~$4–6），以及建議的 Claude Code 設定（Auto 模式；Agent Team 選用）。

## 使用指南與文章

- [學術寫作不該是一個人的事：一套開源 AI 協作工具如何改變研究者的工作流](https://open.substack.com/pub/edwardwu223235/p/ai?r=4dczl&utm_medium=ios) — 完整使用指南（繁體中文）
- [Academic Writing Shouldn't Be a Solo Act](https://open.substack.com/pub/edwardwu223235/p/academic-writing-shouldnt-be-a-solo?r=4dczl&utm_medium=ios) — Full pipeline walkthrough (English)

---

## 功能特色一覽

- **Deep Research** — 13 個 Agent 的研究團隊，支援蘇格拉底引導、PRISMA 系統性回顧、意圖偵測、對話健康度監控、可選跨模型 DA、Semantic Scholar API 驗證。
- **Academic Paper** — 12 個 Agent 的論文撰寫團隊，含風格校準、寫作品質檢查、LaTeX 輸出強化、視覺化、修訂教練、引用格式轉換、反洩漏協議、VLM 圖表驗證。
- **Academic Paper Reviewer** — 7 個 Agent 的多視角同儕審查，採逐準則、證據錨定的敘事判斷（Journal-Fit Reviewer + 3 位動態審查者 + 魔鬼代言人），含讓步門檻協議、攻擊強度保持、可選跨模型 DA critique / calibration、R&R 追溯矩陣、唯讀約束。目前 live review 一律為 `NOT_CALIBRATED`；完整 calibration 只產生有界候選 profile，尚未接上 live review。
- **Academic Pipeline** — 10 階段全流程調度器，含自適應 checkpoint、宣稱驗證、素材護照、可選 `repro_lock`、可選跨模型誠信驗證、中途強化機制，以及逐項準則的敘事退步檢查（typed trajectory 尚未實作）。
- **資料存取層級標註**（v3.3.2+）— 每個 skill 宣告 `data_access_level`（`raw` / `redacted` / `verified_only`），由 `scripts/check_data_access_level.py` 強制執行。設計靈感來自 Anthropic 的 automated-w2s-researcher（2026）。詳見 [`shared/ground_truth_isolation_pattern.md`](shared/ground_truth_isolation_pattern.md)。
- **任務類型標註**（v3.3.2+）— 每個 skill 宣告 `task_type`（`open-ended` 或 `outcome-gradable`）。目前 ARS 所有 skills 皆為 `open-ended`。
- **Benchmark 報告 Schema**（v3.3.5+）— JSON Schema + lint script，要求誠實的 benchmark 比較報告。詳見 [`shared/benchmark_report_pattern.md`](shared/benchmark_report_pattern.md)。
- **Artifact 可重現性 Lockfile**（v3.3.5+）— Material Passport 新增可選 `repro_lock` 子區塊。**是設定文件化，不是重播保證** — LLM 輸出不是位元可重現。詳見 [`shared/artifact_reproducibility_pattern.md`](shared/artifact_reproducibility_pattern.md)。
- **實驗來源憑證登錄**（#260）— Material Passport 可選的 `experiment_provenance[]` 記錄研究者在**外部**跑過的實驗（ARS 從不執行實驗），論文宣稱透過 `claim_intent_manifest.planned_experiment_ids[]` 與之 join。誠信 gate（Stage 2.5/4.5）逐條比對實驗支撐型宣稱與登錄憑證 — `ALIGNED` / `OVERSTATED` / `NOT_SUPPORTED_BY_PROVENANCE` / `PROVENANCE_INSUFFICIENT` — **但不判定實驗本身是否正確**。fail-closed 的 `experiment_intake_declaration` 讓「有沒有跑實驗」成為 Stage 1 明確決定。詳見 [`shared/handoff_schemas.md`](shared/handoff_schemas.md)。

**誠信與驗證邊界：**ARS 檢查的是論文與被報告的研究過程，包括引用是否存在、宣稱與來源是否一致、所述方法、已登錄實驗結果與論文宣稱的一致性、圖表忠實度，以及報告／流程／提交包的一致性；部分檢查採抽樣或由 LLM 判斷。ARS **不能**證明程序確實執行、原始資料真實，或結果可重現；若捏造內容被前後一致地報告，仍可能通過這些檢查。詳見 [POSITIONING.md〈Integrity checks and the empirical-work boundary〉](POSITIONING.md#integrity-checks-and-the-empirical-work-boundary)。

---

## 實際產出展示

查看完整 10 階段 pipeline 的實際產出 — 包含**同儕審查報告、誠信驗證報告、完稿論文**：

**[瀏覽所有 pipeline 產出 →](examples/showcase/)**

| 產出物 | 說明 |
|---|---|
| [完稿論文（英文）](examples/showcase/full_paper_apa7.pdf) | APA 7.0 格式，LaTeX 編譯 |
| [完稿論文（中文）](examples/showcase/full_paper_zh_apa7.pdf) | 中文版，APA 7.0 |
| [誠信報告 — 審稿前](examples/showcase/integrity_report_stage2.5.pdf) | Stage 2.5：抓出 15 個虛構引用 + 3 個統計錯誤 |
| [誠信報告 — 最終](examples/showcase/integrity_report_stage4.5.pdf) | Stage 4.5：確認零回歸 |
| [同儕審查第一輪](examples/showcase/stage3_review_report.pdf) | Journal-Fit Reviewer + 3 審查者 + 魔鬼代言人 |
| [複審](examples/showcase/stage3prime_rereview_report.pdf) | 修訂後驗證審查 |
| [同儕審查第二輪](examples/showcase/stage3_review_report_r2.pdf) | 追蹤審查 |
| [回覆審查意見](examples/showcase/response_to_reviewers_r2.pdf) | 逐點回覆 |
| [出版後稽核報告](examples/showcase/post_publication_audit_2026-03-09.pdf) | 獨立全引用稽核：發現 21/68 篇問題，通過了 3 輪誠信審查仍漏網 |

---

## 搭配工具：Experiment Agent

如果你的研究需要在寫作前跑實驗（程式碼或人工研究），[Experiment Agent](https://github.com/Imbad0202/experiment-agent) 技能填補 ARS Stage 1（研究）和 Stage 2（寫作）之間的空缺。

```
ARS Stage 1 研究      →  RQ Brief + Methodology Blueprint
        ↓
  experiment-agent     →  執行/管理實驗 → 驗證結果
        ↓
ARS Stage 2 寫作      →  用驗證過的實驗結果撰寫論文
```

**功能**：執行程式碼實驗（Python、R 等）並即時監控、管理人工研究 protocol 與 IRB 倫理審查、11 種統計謬誤偵測、重現性驗證。

**搭配使用方式**：ARS pipeline 跑完 Stage 1 後暫停，在另一個 experiment-agent session 中跑實驗，完成後將結果（含 Material Passport）帶回 ARS Stage 2。ARS 不需要任何修改。詳見 [experiment-agent README](https://github.com/Imbad0202/experiment-agent)。

---

## 使用方式

### 快速開始

```
# 啟動完整研究 pipeline
你: "我想做一篇關於 AI 對高教品保影響的研究論文"

# 蘇格拉底引導模式
你: "引導我研究 AI 在教育評鑑中的應用"

# 引導式論文撰寫
你: "引導我寫一篇關於少子化影響的論文"

# 審查現有論文
你: "幫我審查這篇論文"（接著提供論文）

# 查看 pipeline 進度
你: "進度" 或 "status"
```

### 個別 Skill 使用

#### Deep Research（深度研究，8 種模式）

```
"研究 AI 對高等教育的影響"                    → full mode（完整研究）
"給我一份 X 的快速摘要"                       → quick mode（快速簡報）
"幫我做 X 的系統性文獻回顧，含 PRISMA"        → systematic-review mode
"引導我研究 X"                                → socratic mode（蘇格拉底引導）
"幫我查核這些說法"                            → fact-check mode（事實查核）
"幫我做文獻回顧"                              → lit-review mode（文獻回顧）
"審查這篇論文的研究品質"                      → review mode（論文審查）
```

#### Academic Paper（學術論文撰寫，11 種模式）

```
"幫我寫一篇論文"                              → full mode（完整撰寫）
"引導我寫論文"                                → plan mode（引導規劃）
"先幫我搭論文大綱"                            → outline-only mode（只做大綱）
"我有初稿，這是審稿意見"                      → revision mode（修訂）
"幫我整理這些審稿意見成修訂路線圖"            → revision-coach mode
"幫我寫這篇的摘要"                            → abstract-only mode（摘要）
"把這批資料寫成文獻回顧論文"                  → lit-review mode（文獻回顧論文）
"轉換成 LaTeX" / "引用格式轉 IEEE"            → format-convert mode（格式轉換）
"檢查引用格式"                                → citation-check mode（引用檢查）
"幫我生成 NeurIPS 的 AI 使用揭露"             → disclosure mode（AI 揭露）
```

#### Academic Paper Reviewer（論文審查，6 種模式）

```
"審查這篇論文"                                → full mode（Journal-Fit Reviewer + R1/R2/R3 + 魔鬼代言人）
"快速評估這篇論文"                            → quick mode（快速評估）
"引導我改進這篇論文"                          → guided mode（引導改進）
"檢查研究方法"                                → methodology-focus mode（方法論聚焦）
"驗收修訂"                                    → re-review mode（再審驗收）
"用我的 gold set 校準 reviewer"               → calibration mode（校準）
```

#### Academic Pipeline（全流程調度器）

```
"我想做一篇完整的研究論文"                    → 從 Stage 1 開始完整 pipeline
"我已經有論文，幫我審查"                      → 從 Stage 2.5 進入（先做誠信審查）
"我收到審稿意見了"                            → 從 Stage 4 進入
```

> Pipeline 結束時自動產出 **Stage 6：過程紀錄** — 含論文創建過程紀錄與 6 維度協作品質評估（1–100 分）。

### 支援語言

- **繁體中文** — 使用者以中文對話時預設使用
- **English** — 使用者以英文對話時預設使用
- 學術論文自動產出雙語摘要（中文 + English）

> **使用其他語言？** 蘇格拉底模式（deep-research）和 Plan 模式（academic-paper）採用**意圖匹配**啟動 — 偵測你的請求含義，而非比對特定關鍵字。這代表它們**支援任何語言**，無需額外設定。
>
> 不過，一般的 `Trigger Keywords` 區塊（決定 skill 是否被啟動）仍以英文和繁體中文為主。如果你發現 skill 在你的語言下觸發不穩定，可以在各 `SKILL.md` 的 `### Trigger Keywords` 區塊中加入你的語言的關鍵字，提高匹配信心。

### 支援引用格式

- APA 7.0（預設，含中文引用規則）
- Chicago（Notes & Author-Date）
- MLA
- IEEE
- Vancouver

### 支援論文結構

- IMRaD（實證研究）
- 主題式文獻回顧
- 理論分析
- 個案研究
- 政策簡報
- 研討會論文

---

## Skill 詳細資訊

各 agent 的職責與各階段產出物現已移至 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)。版本號保留在此以維持 release metadata 集中管理。

### Deep Research (v2.12.1)

13 個 Agent 的研究團隊。模式：full、quick、review、lit-review、three-way-scan、fact-check、socratic、systematic-review。完整 agent 名單與產出物：見 ARCHITECTURE.md §3。

### Academic Paper (v3.3.1)

12 個 Agent 的論文撰寫 pipeline。模式：full、plan、outline-only、revision、revision-coach、abstract-only、lit-review、format-convert、citation-check、disclosure、rebuttal-audit。輸出：MD + DOCX（Pandoc 可用時）+ LaTeX（APA 7.0 `apa7` class / IEEE / Chicago）→ tectonic 編譯 PDF。完整 agent 名單與各 phase 職責：見 ARCHITECTURE.md §3。

### Academic Paper Reviewer (v1.11.1)

7 個 Agent 的多視角審查，採 **逐準則、證據錨定的敘事判斷**。模式：full、re-review、quick、methodology-focus、guided、calibration。目前 live review 與 Schema 6 package 一律為 `NOT_CALIBRATED`；完整 calibration 可產生有界候選 profile，但尚未接上 live review。不得以固定總分對照接受、小修、大修或退稿。第一輪審查面板 vs. 契約治理再審派送的分界：見 ARCHITECTURE.md §3 Stage 3 / Stage 3'。

### Academic Pipeline (v3.21.2)

10 階段調度器，含誠信驗證、兩階段審查、蘇格拉底指導、協作品質評估。Pipeline 保證：每個階段都需使用者確認 checkpoint；誠信驗證（Stage 2.5 + 4.5）為 MANDATORY 且沒有不留紀錄的繞過路徑（所有覆寫都須記錄使用者理由、供 Stage 6 使用）；R&R 追溯矩陣（Schema 11）獨立驗證作者修訂宣稱。v3.4 新增 Compliance Agent（PRISMA-trAIce + RAISE）於 Stage 2.5 / 4.5。v3.5 新增 **協作深度觀察員**（`collaboration_depth_agent`，僅諮詢性質、永不阻擋流程）於每一次 FULL/SLIM checkpoint 與 pipeline 完成時。MANDATORY 誠信閘門（2.5 / 4.5）明確跳過觀察員，避免稀釋合規檢查。理論基礎：Wang & Zhang (2026), IJETHE 23:11。逐階段矩陣（agent、產出物、閘門）：見 ARCHITECTURE.md §3。

---

## v3.0 優化：我們發現了 AI 的哪些結構性限制

在使用 ARS 撰寫一篇關於 AI 與高教的反思文章時，我們遇到了三個結構性問題：

1. **框架鎖定**：AI 在給定框架內越來越精緻，但無法質疑框架本身
2. **諂媚傾向**：每次挑戰魔鬼代言人的攻擊，它都讓步得太快
3. **意圖偵測錯誤**：蘇格拉底模式在使用者仍在探索時就急著收束

### 改了什麼

- **魔鬼代言人讓步門檻**：反駁必須評分 1-5，≥4 才允許讓步。不允許連續讓步。框架鎖定偵測。
- **蘇格拉底意圖偵測**：偵測使用者是「探索型」還是「目標型」。探索型模式停用自動收束。
- **對話健康度指標**：每 5 輪靜默自檢，偵測持續同意、迴避衝突、過早收束。
- **跨模型驗證**：設定 `ARS_CROSS_MODEL` 啟用第二 AI 模型獨立審查。詳見 [docs/SETUP.zh-TW.md](docs/SETUP.zh-TW.md)。
- **AI 自我反思報告**：Pipeline 結束後自動產出 AI 行為自評。

這些優化不能完全解決 AI 的結構性限制——它們讓限制變得可見、可追蹤、可被人類介入。

---

## 授權條款

本作品採用 [CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 授權。

**你可以自由：**
- 分享 — 複製及散布本作品
- 改作 — 重混、轉換、以本作品為基礎進行創作

**惟須遵守以下條件：**
- **姓名標示** — 你必須給予適當的標示
- **非商業性** — 你不得將本作品用於商業目的

**標示格式：**
```
Based on Academic Research Skills by Cheng-I Wu
https://github.com/Imbad0202/academic-research-skills
```

---

## 貢獻者

**吳政宜** (Cheng-I Wu) — 作者與維護者

**[aspi6246](https://github.com/aspi6246)** — 貢獻者。v3.1 優化靈感來自 [Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics)：唯讀約束模式、Anti-Pattern 作為一等公民設計、認知框架方法（教「如何思考」而非只有步驟）、精簡 skill 尺寸哲學。

**[mchesbro1](https://github.com/mchesbro1)** — 貢獻者。最初提出並撰寫了 IS Basket of 8 期刊清單（[Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)）。

**[cloudenochcsis](https://github.com/cloudenochcsis)** — 貢獻者。將 IS 章節從 *Basket of 8* 擴充為完整的 *Senior Scholars' Basket of 11*，補上 *Decision Support Systems*、*Information & Management*、*Information and Organization*（[Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7)、[PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)）。資料來源：[AIS Senior Scholars' List of Premier Journals](https://aisnet.org/research/seniorscholarsbasket/)。

**[eltociear](https://github.com/eltociear)**（Ikko Eltociear Ashimine）— 貢獻者。翻譯了日文版 README（[`README.ja-JP.md`](README.ja-JP.md)）（[PR #161](https://github.com/Imbad0202/academic-research-skills/pull/161)）。

**[xpfo-go](https://github.com/xpfo-go)**（xpfo）— 貢獻者。翻譯了簡體中文版 README（[`README.zh-CN.md`](README.zh-CN.md)）（[PR #181](https://github.com/Imbad0202/academic-research-skills/pull/181)）。

**[ktao732084-arch](https://github.com/ktao732084-arch)** — 貢獻者。擴充了 `academic-paper` 揭露系統，新增九個醫學出版政策目標、依目標收集必要事實的流程，以及 fail-closed 的獨立揭露渲染（[Issue #596](https://github.com/Imbad0202/academic-research-skills/issues/596)、[PR #599](https://github.com/Imbad0202/academic-research-skills/pull/599)）；擴充 EQUATOR 臨床報告參考，加入 CARE、STARD 與 TRIPOD+AI 的精簡指引，以及 fail-closed 的研究設計路由流程（[Issue #594](https://github.com/Imbad0202/academic-research-skills/issues/594)、[PR #601](https://github.com/Imbad0202/academic-research-skills/pull/601)）；並設計及貢獻獨立的中文文獻解析器、API 協定與合成傳輸 fixture 測試套件（[Issue #595](https://github.com/Imbad0202/academic-research-skills/issues/595)、[PR #600](https://github.com/Imbad0202/academic-research-skills/pull/600)）。

---

## 更新紀錄

這裡只列最近三個版本。完整更新紀錄在英文版 [CHANGELOG.md](CHANGELOG.md)。到 v3.21.2 為止的繁體中文版本摘要已凍結存放於 [docs/changelog-archive/zh-TW.md](docs/changelog-archive/zh-TW.md)，之後不再更新。

### v3.21.2（2026-09-06）— 模型現況對齊（Fable 5.1 / GPT-6 Astra）、檢查點決策來源與 CJK 標題比對修復

> **對齊現況與決策來源，不是新能力：**v3.21.2 依兩份 2026 年 9 月的廠商 system card 對齊套件。`gpt-6-astra` 以 provisional 身分進入跨模型表（兩條傳輸皆然），並依世代現況政策成為建議的 OpenAI 驗證模型；`gpt-5.6-sol` 保留其在 ChatGPT 訂閱引用傳輸上的 validated 身分，本版不宣稱任何新的 bakeoff 結果。受限的 Codex 傳輸 reasoning-effort 集合新增 `ultra`。新增兩道 guardrail，皆為 prompt 層、由廠商文件而非 ARS 量測所驅動：檢查點決策來源（只有使用者回合算決策；決策逐字轉交子代理；風險 R11），以及供應商端監控或安全介入一律視為傳輸失敗、永遠不是判定。針對兩份卡片的 harness 汰除審計沒有汰除任何東西（0 條 prompt 文字汰除；8 條 keep-as-debt 項目補上卡片引註）。修復：CJK 標題不再在四個索引解析器的精確標題閘失敗（#798），外層引號只在構成單一平衡單位時才剝除（#800）；autolink round-trip 測試明示其相依套件（#801）；`check_surface_form_parity` 改為指名壞掉的環境而非 manifest；新增 skill 清單一致性 lint（#809）；R10 殘餘缺口去過時化（#813）；修正一行 MLA 規則（#805）。套件／pipeline → v3.21.2；deep-research → v2.12.1；academic-paper → v3.3.1；academic-paper-reviewer → v1.11.1。

### v3.21.1（2026-08-24）— 有界工作流程基礎、封存式 bakeoff 與傳輸強化

> **有明示量測才視為量測，其餘維持有界：**v3.21.1 修復 codex-cli 0.147.0 下受限的 ChatGPT 訂閱引用傳輸，並記錄第一次 Promotion Bakeoff：`gpt-5.6-sol` 僅在該訂閱傳輸上取得 validated，first-party API 路徑仍為 provisional；往後的 bakeoff 則必須採用封存式預註冊。本版也新增 default-off 的研究工作流程 profile 基礎（只有離線、確定性的 conformance；沒有 pipeline hook，也未提供特定研究家族的成品 profile）、opt-in 的 inquiry-ledger alpha（`ARS_INQUIRY_LEDGER=1`），以及尚未實作、僅凍結設計的 alternative register。其行為證據維持 `NOT_RUN`，不宣稱可用性、復原、創新性、正確性或研究成果效益。審查準則 registry 新增一組有來源支持、僅供示範的 MSR 2027 exact-profile proving set；這不代表投稿期刊／會議與學科覆蓋、真實作者 attest，亦非 constructive-review 證據，所需的獨立人類評估仍未完成。其他變更包含對齊 `data_access_level`、整併 markdown lint 文法、登錄 guard launcher 的降級路徑，以及在不背書的前提下把 OrcaRouter 列為社群整合。套件／pipeline → v3.21.1；deep-research → v2.12.1；academic-paper → v3.3.1；academic-paper-reviewer → v1.11.1。

### v3.21.0（2026-08-18）— ISO/IEC 42001 精神軌：透明、可驗證、可行

> **可被檢驗的透明：**v3.21.0 完成 ISO/IEC 42001 精神稽核軌（#753–#760）。對外宣稱對齊證據紀錄，並新增四份常設文件回答使用者真正想問的問題：你的安裝管道有哪些控制實際運作（`docs/CONTROL_AVAILABILITY.md`）、哪些資料離開你的機器與存放多久（`docs/DATA_FLOWS.md`）、每個 CI workflow 實際的強制力等級（`docs/ARCHITECTURE.md` §7.1）、每個機制對應哪個風險與其證據狀態、殘餘缺口（`docs/RISK_REGISTER.md`），每份都由專屬 CI lint 防漂移。`GOVERNANCE.md` 言明決策權限、cross-model 審查提供與不提供什麼（error-detection control、非組織獨立性）與 end-of-life 姿態；`SECURITY.md` 新增一人可運轉的分級 triage 程序。這些是附 ISO/IEC 42001 資訊性錨點的操作原則、不是驗證宣稱，本版也不新增任何成效數字。套件／pipeline → v3.21.0；deep-research → v2.12.1；academic-paper → v3.3.1；academic-paper-reviewer → v1.11.1。
