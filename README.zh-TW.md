# Academic Research Skills for Claude Code

[![Version](https://img.shields.io/badge/version-v3.6.8-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.6.8)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[English](README.md)

一套完整的學術研究 Claude Code 技能包，涵蓋從研究到論文出版的全流程。

> **AI 是你的副駕駛，不是機長。** 這工具不會幫你寫論文。它處理苦工 — 搜文獻、排格式、驗數據、查邏輯一致性 — 讓你專注在真正需要你腦子的事：定義問題、選方法、詮釋數據的意義、寫出「我認為」後面那句話。
>
> 跟 humanizer 不同，這工具不是幫你隱藏用 AI 協作的事實，而是幫你把關文章品質。風格校準從你過去的文章學習你的聲音，寫作品質檢查抓出讓文字讀起來像機器產的模式。目標是品質，不是遮掩。

### 為什麼選「人機協作」而不是「全自動」？

Lu 等人（2026，*Nature* 651:914-919）發表的 **The AI Scientist** 是第一個端到端全自動的 AI 研究系統，其生成的論文通過 ICLR 2025 workshop 的盲審（評分 6.33/10，workshop 平均 4.87）。他們自己的 Limitations 段落也列出了這類系統會遇到的結構性失敗模式：實作錯誤、幻覺實驗結果、取巧特徵依賴、實作錯誤被包裝成「意外發現」、方法論偽造、框架鎖定、引用幻覺。

ARS 建立在這個前提上：**人類研究者 + AI 的組合，比純自動或純人工都更能避開這些失敗模式**。Stage 2.5 與 Stage 4.5 誠信閘門執行 7 類阻斷式檢查清單（見 [`academic-pipeline/references/ai_research_failure_modes.md`](academic-pipeline/references/ai_research_failure_modes.md)），reviewer 也提供 opt-in 的 calibration mode 用使用者自備的 gold set 測量 FNR/FPR。

v3.3 的靈感來自 [**PaperOrchestra**](https://arxiv.org/abs/2604.05018)（Song, Song, Pfister & Yoon, 2026, Google）：Semantic Scholar API 驗證、反洩漏協議、VLM 圖表驗證、分數軌跡追蹤。

---

## 架構與 pipeline

**👉 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — 完整 pipeline 視圖：流程圖、階段 × 維度矩陣、資料存取流、skill 依賴圖、品質閘門、模式清單。

這份架構文件取代了原本散在 README 各處的 pipeline 描述。關於「哪個階段跑什麼」的所有資訊都集中在一個地方。

## 安裝與設定

**Claude Code CLI / IDE 用戶一行裝（v3.7.0+）：**

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

**👉 [docs/SETUP.zh-TW.md](docs/SETUP.zh-TW.md)** — 完整指南：安裝 Claude Code、設定 API key、選用的 Pandoc/tectonic（DOCX/PDF）、跨模型驗證（`ARS_CROSS_MODEL`），以及五種安裝方式（Plugin、專案 skills、全域 skills、claude.ai Project、repo clone）。

## 效能與費用

**👉 [docs/PERFORMANCE.zh-TW.md](docs/PERFORMANCE.zh-TW.md)** — 各模式 token 預算、完整 pipeline 估算（~$4–6 for 一篇 15k 字論文），以及建議的 Claude Code 設定（Skip Permissions；Agent Team 選用）。

## 使用指南與文章

- [學術寫作不該是一個人的事：一套開源 AI 協作工具如何改變研究者的工作流](https://open.substack.com/pub/edwardwu223235/p/ai?r=4dczl&utm_medium=ios) — 完整使用指南（繁體中文）
- [Academic Writing Shouldn't Be a Solo Act](https://open.substack.com/pub/edwardwu223235/p/academic-writing-shouldnt-be-a-solo?r=4dczl&utm_medium=ios) — Full pipeline walkthrough (English)

---

## 功能特色一覽

- **Deep Research** — 13 個 Agent 的研究團隊，支援蘇格拉底引導、PRISMA 系統性回顧、意圖偵測、對話健康度監控、可選跨模型 DA、Semantic Scholar API 驗證。
- **Academic Paper** — 12 個 Agent 的論文撰寫團隊，含風格校準、寫作品質檢查、LaTeX 輸出強化、視覺化、修訂教練、引用格式轉換、反洩漏協議、VLM 圖表驗證。
- **Academic Paper Reviewer** — 7 個 Agent 的多視角同儕審查，0-100 品質量表（主編 + 3 位動態審查者 + 魔鬼代言人），含讓步門檻協議、攻擊強度保持、可選跨模型 DA critique / calibration、R&R 追溯矩陣、唯讀約束。
- **Academic Pipeline** — 10 階段全流程調度器，含自適應 checkpoint、宣稱驗證、素材護照、可選 `repro_lock`、可選跨模型誠信驗證、中途強化機制、分數軌跡追蹤。
- **資料存取層級標註**（v3.3.2+）— 每個 skill 宣告 `data_access_level`（`raw` / `redacted` / `verified_only`），由 `scripts/check_data_access_level.py` 強制執行。設計靈感來自 Anthropic 的 automated-w2s-researcher（2026）。詳見 [`shared/ground_truth_isolation_pattern.md`](shared/ground_truth_isolation_pattern.md)。
- **任務類型標註**（v3.3.2+）— 每個 skill 宣告 `task_type`（`open-ended` 或 `outcome-gradable`）。目前 ARS 所有 skills 皆為 `open-ended`。
- **Benchmark 報告 Schema**（v3.3.5+）— JSON Schema + lint script，要求誠實的 benchmark 比較報告。詳見 [`shared/benchmark_report_pattern.md`](shared/benchmark_report_pattern.md)。
- **Artifact 可重現性 Lockfile**（v3.3.5+）— Material Passport 新增可選 `repro_lock` 子區塊。**是設定文件化，不是重播保證** — LLM 輸出不是位元可重現。詳見 [`shared/artifact_reproducibility_pattern.md`](shared/artifact_reproducibility_pattern.md)。

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
| [同儕審查第一輪](examples/showcase/stage3_review_report.pdf) | 主編 + 3 審查者 + 魔鬼代言人 |
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

#### Deep Research（深度研究，7 種模式）

```
"研究 AI 對高等教育的影響"                    → full mode（完整研究）
"給我一份 X 的快速摘要"                       → quick mode（快速簡報）
"幫我做 X 的系統性文獻回顧，含 PRISMA"        → systematic-review mode
"引導我研究 X"                                → socratic mode（蘇格拉底引導）
"幫我查核這些說法"                            → fact-check mode（事實查核）
"幫我做文獻回顧"                              → lit-review mode（文獻回顧）
"審查這篇論文的研究品質"                      → review mode（論文審查）
```

#### Academic Paper（學術論文撰寫，10 種模式）

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
"審查這篇論文"                                → full mode（主編 + R1/R2/R3 + 魔鬼代言人）
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

### Deep Research (v2.8)

13 個 Agent 的研究團隊。模式：full、quick、review、lit-review、fact-check、socratic、systematic-review。完整 agent 名單與產出物：見 ARCHITECTURE.md §3。

### Academic Paper (v3.0)

12 個 Agent 的論文撰寫 pipeline。模式：full、plan、outline-only、revision、revision-coach、abstract-only、lit-review、format-convert、citation-check、disclosure。輸出：MD + DOCX（Pandoc 可用時）+ LaTeX（APA 7.0 `apa7` class / IEEE / Chicago）→ tectonic 編譯 PDF。完整 agent 名單與各 phase 職責：見 ARCHITECTURE.md §3。

### Academic Paper Reviewer (v1.8)

7 個 Agent 的多視角審查，搭配 **0-100 品質量表**。模式：full、re-review、quick、methodology-focus、guided、calibration。**決策對照：** ≥80 接受、65-79 小修、50-64 大修、<50 退稿。第一輪審查團隊 vs. 精簡再審團隊的分界：見 ARCHITECTURE.md §3 Stage 3 / Stage 3'。

### Academic Pipeline (v3.6)

10 階段調度器，含誠信驗證、兩階段審查、蘇格拉底指導、協作品質評估。Pipeline 保證：每個階段都需使用者確認 checkpoint；誠信驗證（Stage 2.5 + 4.5）不可跳過；R&R 追溯矩陣（Schema 11）獨立驗證作者修訂宣稱。v3.4 新增 Compliance Agent（PRISMA-trAIce + RAISE）於 Stage 2.5 / 4.5。v3.5 新增 **協作深度觀察員**（`collaboration_depth_agent`，僅諮詢性質、永不阻擋流程）於每一次 FULL/SLIM checkpoint 與 pipeline 完成時。MANDATORY 誠信閘門（2.5 / 4.5）明確跳過觀察員，避免稀釋合規檢查。理論基礎：Wang & Zhang (2026), IJETHE 23:11。逐階段矩陣（agent、產出物、閘門）：見 ARCHITECTURE.md §3。

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

**[cloudenochcsis](https://github.com/cloudenochcsis)** — 貢獻者。將 IS 章節從 *Basket of 8* 擴充為完整的 *Senior Scholars' Basket of 11*，補上 *Decision Support Systems*、*Information & Management*、*Information and Organization*（[Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7)、[PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)）。資料來源：[AIS Senior Scholars' List of Premier Journals](https://aisnet.org/page/SeniorScholarListofPremierJournals)。

---

## 更新紀錄

### v3.6.8（2026-05-03）— Generator-Evaluator Contract Gate（v3.6.6 spec ship）

> 命名說明：本次發行交付 **v3.6.6 generator-evaluator contract** spec 與實作。
> v3.6.6 因專案排序晚於 v3.6.7 才落地；design doc 內仍保留 v3.6.6 內部命名作為
> contract gate 版本，suite release 標 v3.6.8 維持 CHANGELOG 單調遞增。

- **Schema 13.1**（`shared/sprint_contract.schema.json`）在 Schema 13 之上加兩個 `mode` enum 值（`writer_full` + `evaluator_full`）、兩個新 optional top-level 欄位（`pre_commitment_artifacts` writer-only、`disagreement_handling` evaluator-only）、12 條 `allOf` branch 強制 reviewer- / writer- / evaluator-conditional gate。既有 reviewer contract 在 Schema 13.1 下 byte-equivalent validate（§3.6 zero-touch promise）。
- **兩個新 shipped contract template**：`shared/contracts/writer/full.json`（D1–D7、F1/F4/F2/F3/F0）+ `shared/contracts/evaluator/full.json`（D1–D5、F1/F2/F3/F6/F4/F5/F0）。Spec branch 上原是 design-time artefact，本次發行 atomically promote 為 live shipped。
- **`academic-paper full` 模式內加入 two-phase orchestration**：Phase 4 拆成 Phase 4a（writer paper-blind 預先承諾）+ Phase 4b（writer paper-visible 撰稿 + 自評）；Phase 6 拆成 Phase 6a（evaluator paper-blind 預先承諾）+ Phase 6b（evaluator paper-visible 評分 + 決策）。phase-numbered `<phase4a_output>` / `<phase6a_output>` data delimiter 沿用 v3.6.2 reviewer pattern。Lint count summary：writer 3+4 / evaluator 5+5 / reviewer 5+6（reviewer 維持 zero-touch）。
- **`academic-paper` SKILL + agent file 新增 `## v3.6.6 Generator-Evaluator Contract Protocol` 區塊**（SKILL.md 101 行 + `draft_writer_agent.md` 47 行 + `peer_reviewer_agent.md` 57 行）。SKILL.md 另加 `## Known limitations` 區塊承載 graceful-degradation + cross-session resume v3.6.7+ forward note。
- **Validator 擴充**：`scripts/check_sprint_contract.py` 做 SC-* mode-gating audit（SC-5 + SC-11 reviewer-only；SC-9 跨三個 mode family 各讀對應欄位）。validator 單元測試從 54 條增加到 71 條（4 positive + 5 schema-branch negative + 2 §3.6 reviewer regression + 6 mode-gating）。
- **Manifest CI lint**：`scripts/check_v3_6_6_ab_manifest.py` 強制 `tests/fixtures/v3.6.6-ab/manifest.yaml` 的 §6.2 manifest schema + §6.5 git-tracked invariant。`.github/workflows/spec-consistency.yml` 把 sprint contract validation loop 擴成同時跑 reviewer + writer + evaluator 三個 template directory，並加入新的 manifest CI lint 步驟。
- **A/B evidence fixture stub**（`tests/fixtures/v3.6.6-ab/`，30 個檔案）：manifest + README + 6 paper-A inputs/baseline + 1 paper-C inputs/baseline + Stage 3 reviewer excerpt + 6 codex-judge baseline placeholder。真實 fixture data 在後續 commit populate。

### v3.6.7（2026-04-30）— 下游 agent pattern protection（Step 1+2）

- **三個下游 agent 收緊 13 / 18 個已知幻覺與漂移 pattern**：`synthesis_agent`（A1–A5 敘事側）、`research_architect_agent` survey-designer 模式（B1–B5 工具側）、`report_compiler_agent` abstract-only 模式（C1–C3 出版側）。三個 agent prompt 各自加上 `PATTERN PROTECTION (v3.6.7)` 區塊。
- **`shared/references/` 增加四份 reference 文件**：`irb_terminology_glossary.md`、`psychometric_terminology_glossary.md`、`protected_hedging_phrases.md`、`word_count_conventions.md`。protection 條款引用這些檔案路徑做為 operational contract。
- **跨模型 audit prompt 模板** 在 `shared/templates/codex_audit_multifile_template.md`，含七個 audit dimension 與 `report_compiler_agent` bundle 必跑的三段式 Section 4(f) 檢查。任一 sub-check 失敗即 P1 finding。
- **靜態 lint + 29 條 mutation 測試**：`scripts/check_v3_6_7_pattern_protection.py` 強制 protection 條款存在性與 obligation phrase 形狀；`scripts/test_check_v3_6_7_pattern_protection.py` 把 codex review 的 mutation 證據封存為 unit test，未來 lint 退化會在 CI 浮上來。兩者都接進 `.github/workflows/spec-consistency.yml`。
- **Codex review 紀錄**：七輪 `gpt-5.5` + `xhigh` 跨模型 review 收斂到 0 P1+P2 finding 才 SHIP。Step 6（orchestrator runtime hook）與 Step 8（合成 eval case）走 follow-up PR。

### v3.6.5（2026-04-27）— Material Passport `literature_corpus[]` Consumer 整合

- **Phase 1 兩個文獻 consumer** 接上：`deep-research/agents/bibliography_agent.md` 與 `academic-paper/agents/literature_strategist_agent.md`。當 passport 帶有非空 `literature_corpus[]` 時，兩者都走相同的五步 **corpus-first、search-fills-gap** 流程，並遵守相同的四條 Iron Rule（Same criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure）。
- **PRE-SCREENED 可重現區塊** 進 Search Strategy 報告：列出已納入／排除／略過的 corpus entry，附 F3 zero-hit 註解與 F4a–F4f provenance 報告（針對 `obtained_via` / `obtained_at` 部分宣告情境）。`final_included = pre_screened_included[] ∪ external_included[]` 維持 neutral — bibliography entry 與 literature matrix row 不掛 provenance 標籤。
- **Consumer 協定參考文件** 在 `academic-pipeline/references/literature_corpus_consumers.md`，包含 PRE-SCREENED 模板、BAD/GOOD 範例、四條 Iron Rule 與 per-consumer 讀取指示。
- **CI lint** `scripts/check_corpus_consumer_protocol.py` 透過 manifest 驅動的 consumer 清單（`scripts/corpus_consumer_manifest.json`）強制九條協定不變式。
- **Schema 9 caveat 退役**：`shared/handoff_schemas.md` 移除 v3.6.4「Consumer-side integration deferred to v3.6.5+」一行，改成指向 consumer 協定的 backpointer。
- 採 presence-based 啟動，不變更 schema、不引入新 env flag。Parse 失敗 fallback 到 external-DB-only flow，並 surface `[CORPUS PARSE FAILURE]`。`citation_compliance_agent` 的 corpus 整合延到 v3.6.6+。
- 無破壞性變更，既有使用者 adapter 不需修改。

### v3.6.4（2026-04-25）— Material Passport `literature_corpus[]` 輸入埠

- **Schema 9 新增 `literature_corpus[]`** 選填欄位作為使用者文獻的輸入埠。每筆 entry 符合 `shared/contracts/passport/literature_corpus_entry.schema.json`（CSL-JSON authors / year / title / source_pointer，加上 PRIVATE 選填的 `abstract` / `user_notes`）。
- **語言中性的 adapter 契約** 放在 `academic-pipeline/references/adapters/overview.md`：任何語言寫的程式都能讀使用者自己的 corpus source 並產出符合契約的 `passport.yaml` + `rejection_log.yaml`。Entry-level 錯誤 fail-soft、adapter-level 錯誤 fail-loud、輸出順序確定。
- **三個 reference Python adapter** 在 `scripts/adapters/`：`folder_scan.py`（檔案系統的 PDF 資料夾）、`zotero.py`（Better BibTeX JSON export）、`obsidian.py`（vault frontmatter）。僅供起點參考；非 reference source 預期使用者自行實作 adapter。
- **Rejection log 契約** 在 `shared/contracts/passport/rejection_log.schema.json`，採用封閉 enum 的 categorical reason 值；永遠輸出（無 rejection 時為空）。
- **CI 把關**：`scripts/check_literature_corpus_schema.py` 驗 schemas + adapter examples；`scripts/sync_adapter_docs.py --check` 防 schema→docs drift；新 `pytest.yml` workflow 在 path-filtered 觸發跑 `scripts/adapters/tests/`。
- **僅輸入埠**：v3.6.4 只定義 schema 與 adapter 契約，consumer 整合到 v3.6.5 才接上 `bibliography_agent` 與 `literature_strategist_agent`。
- 無破壞性變更。

### v3.6.3（2026-04-23）— 選用式 Passport 重置邊界

- **Opt-in passport 重置邊界**（`ARS_PASSPORT_RESET=1`）。把每個 FULL checkpoint 提升為 context 重置邊界。新增 `resume_from_passport=<hash>` 模式，讓使用者在新的 Claude Code session 單憑 Material Passport ledger 就恢復 pipeline，不重播先前對話。`systematic-review` 模式 flag ON 時，每個 FULL checkpoint 一律強制重置；其他模式視重置為 flag 開啟後的強預設。Flag OFF 時 byte-for-byte 維持 pre-v3.6.3 行為。
- Schema 9 新增 append-only `reset_boundary[]` ledger，兩種 entry kind（`kind: boundary` + `kind: resume`）。Hash 用 JSON Canonical Form + SHA-256，搭配 canonical placeholder 處理自我參照問題。選填 `pending_decision` 負責 MANDATORY 分支決策。
- 新 CI lint `scripts/check_passport_reset_contract.py`：任何提到 flag 的檔案都必須指向權威協議文件。
- 協議文件：`academic-pipeline/references/passport_as_reset_boundary.md`。
- `docs/PERFORMANCE.zh-TW.md` 更新 long-running session 指引。
- 無破壞性變更，flag 預設關閉。

### v3.6.2（2026-04-23）— 審稿 Sprint Contract Hard Gate

v3.6.2 引入 Schema 13 sprint contract 與 hard-gate 編排，強制審稿人在閱讀論文前先承諾評分準則。本次只動審稿端（reviewer-only first test case）；writer/evaluator 留到 v3.6.4。詳見 CHANGELOG。

- **Schema 13 sprint contract**：`panel_size`、`acceptance_dimensions`、`failure_conditions`（含 `severity` 優先序 + 隨 panel 變動的 `cross_reviewer_quantifier`）、`measurement_procedure`、選用 `override_ladder`、限定 `agent_amendments`。驗證器：`scripts/check_sprint_contract.py`。
- **兩段 hard gate**：審稿人先在「論文內容盲」Phase 1 預先承諾評分計畫，Phase 2 才看到論文；Phase 1 輸出包在 `<phase1_output>...</phase1_output>` 資料分隔符內，縮窄 self-injection 面。
- **合成者三步機械協議**：建構跨審稿矩陣 → 依 panel-relative quantifier + 認可表達式詞彙評估每條 `failure_condition` → 用 `severity` 決優先。禁止操作清單寫在 `editorial_synthesizer_agent`。
- **出貨兩份審稿模板**：`shared/contracts/reviewer/full.json`（panel 5）與 `shared/contracts/reviewer/methodology_focus.json`（panel 2）。`reviewer_re_review`、`reviewer_calibration`、`reviewer_guided` 三個 mode 在 schema enum 中保留，但 v3.6.2 不出 template，繼續沿用 pre-v3.6.2 行為；`reviewer_quick` 完全排除於 enum 外。
- `academic-paper-reviewer` SKILL 版本：`1.8.1 → 1.9.0`。`academic-pipeline` SKILL 版本：`3.5.1 → 3.6.2`（suite-version invariant）。Suite 版本升至 `3.6.2`。
- 詳見設計稿 [`docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md`](docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md) 與協定 [`academic-paper-reviewer/references/sprint_contract_protocol.md`](academic-paper-reviewer/references/sprint_contract_protocol.md)。

### v3.5.1（2026-04-22）— 選用式 Socratic 誠實探測

v3.5.1 新增 Socratic Mentor 的選用式誠實探測（設定 `ARS_SOCRATIC_READING_PROBE=1` 啟用）。預設關閉。詳見 CHANGELOG。

- **選用式閱讀誠實探測**：設定 `ARS_SOCRATIC_READING_PROBE=1` 後，Socratic Mentor 在目標導向 session 中引用特定論文時，觸發一次性誠實探測，請使用者摘述一段文字。拒絕回答僅記錄，不扣分。探測結果寫入研究計畫摘要，並帶入 Stage 6 AI 自我反思報告。不新增 agent，不變更 schema。
- `deep-research` SKILL 版本：`2.9.0 → 2.9.1`。`academic-pipeline` SKILL 版本：`3.5.0 → 3.5.1`。Suite 版本升至 `3.5.1`。

### v3.5.0（2026-04-21）— 協作深度觀察員（Collaboration Depth Observer）

- **新增 agent**：`academic-pipeline` 新增 `collaboration_depth_agent`（Agent Team 從 3 成長為 4）。每個 FULL/SLIM checkpoint 與 pipeline 完成後（Stage 6 之後）觸發，依 4 維度 rubric 對使用者與 AI 的協作模式評分。**純觀察建議，永不阻擋流程**。MANDATORY checkpoints（Stages 2.5 / 4.5 的完整性檢查）**不**觸發 observer，完整性閘門完全保留。
- **新增 rubric**：[`shared/collaboration_depth_rubric.md`](shared/collaboration_depth_rubric.md) v1.0。四個維度：Delegation Intensity、Cognitive Vigilance、Cognitive Reallocation、Zone Classification（Zone 1 / Zone 2 / Zone 3）。理論依據為 Wang, S., & Zhang, H. (2026). "Pedagogical partnerships with generative AI in higher education: how dual cognitive pathways paradoxically enable transformative learning." *International Journal of Educational Technology in Higher Education*, 23:11. DOI [10.1186/s41239-026-00585-x](https://doi.org/10.1186/s41239-026-00585-x)。
- **Cross-model 分歧顯式標示，不默默平均**：當 `ARS_CROSS_MODEL` 設定時，observer 於兩個模型同時執行；若任一維度分差 > 2 分即標記為 `cross_model_divergence`。另提供 `ARS_CROSS_MODEL_SAMPLE_INTERVAL` 調控成本。
- **Short-stage guard**：stage 內使用者 turn < 5 時注入靜態 `insufficient_evidence` 區塊，不派發全模型 observer call。
- **反諂媚規範**：分數 ≥ 7 必須附具體對話 turn 引用；Zone 3 觸發 re-audit；禁止鼓勵性語言。
- `academic-pipeline` SKILL 版本：`3.3.0 → 3.4.0`。Suite 版本升至 `3.5.0`。新增 lint `scripts/check_collaboration_depth_rubric.py` 加 10 個測試。

### v3.4.0（2026-04-20）— Compliance Agent + Schema 12

- **Compliance Agent（shared）**：單一 mode-aware agent，同時跑 PRISMA-trAIce 17 項（限 SR mode）+ RAISE 四原則 + 8-role matrix。掛載既有 Stage 2.5 / 4.5 Integrity Gate；tier-based block（Mandatory → block、HR → warn、R/O → info）。非 SR 入口只跑原則、warn-only。
- **Schema 12 compliance_report** 附加到 Material Passport 的 `compliance_history[]`（append-only）。
- **三回合 user-override 階梯**，自動注入 `disclosure_addendum` 到 manuscript。無法規避揭露。
- **Calibration 以透明公布取代硬門檻**，與 `task_type: open-ended` 自洽。
- **Upstream freshness CI** 偵測 PRISMA-trAIce 上游漂移（non-blocking）。
- **長時間 session 文件**：Material Passport 作為跨 session 續跑機制。

### v3.3.6 (2026-04-15) — README 精簡 + ARCHITECTURE 文件

- 新增 `docs/ARCHITECTURE.md` 作為 pipeline 結構的單一來源（流程、矩陣、資料存取、依賴圖、品質閘門、模式）。透過 PR #18 合併入 main。
- 新增 `docs/SETUP.md` / `docs/SETUP.zh-TW.md`（前置需求、API key、Pandoc/tectonic、跨模型驗證、四種安裝方式），以及 `docs/PERFORMANCE.md` / `docs/PERFORMANCE.zh-TW.md`（token 預算、建議 Claude Code 設定）。README 以連結取代內嵌。
- 精簡 README：移除 ASCII pipeline 圖與 16 項 key-feature 清單（已被 ARCHITECTURE.md 取代）；Skill 詳細資訊維持版本號錨點，讀者跳到 ARCHITECTURE.md §3 看各 agent 名單。
- 註記：沒有任何 skill 的功能變動，純文件重構。suite version 升級至 `3.3.6`。

### v3.3.5 (2026-04-15)
- 新增 `benchmark_report.schema.json` 與 Material Passport 的 `repro_lock` 可選區塊。兩者都附 pattern 文件、lint、範例。首次引入正式的 Python 開發依賴清單（`requirements-dev.txt`）。

### v3.3.4 (2026-04-15) — README 更新紀錄同步修補

- 同步 `README.md` 與 `README.zh-TW.md` 內嵌的 changelog 區塊，補上原本缺漏的 `v3.3.3` 與 `v3.3.2` 發版摘要。
- 擴充 `scripts/check_spec_consistency.py`，之後 README changelog 若再漂移，CI 會直接 fail。
### v3.3.3 (2026-04-15) — Release Prep + Lint 強化

- 強化 SKILL frontmatter lint：缺少 closing `---` fence 時，現在會明確報錯，不再把整份檔案後半段誤當成合法 YAML。
- frontmatter 若可被 YAML 解析但不是 mapping，現在會回報可讀錯誤，而不是直接 crash。
- 修正中英文 README 中 post-publication audit showcase 連結失效的問題。
- 在 spec consistency check 補上 README 相對連結驗證，之後 dead link 會直接讓 CI fail。
- 將 DOCX 輸出契約在文件中統一：直接產出 `.docx` 依賴 Pandoc，否則回退為 Markdown + 轉換說明。
- 完成 `v3.3.3` 發版準備：suite version bump，`academic-paper` -> v3.0.2，`academic-pipeline` -> v3.2.2。

### v3.3.2 (2026-04-15) — Data Access Level + Task Type Metadata

- 所有頂層 `SKILL.md` 新增 `metadata.data_access_level`，並以 `raw`、`redacted`、`verified_only` 為強制詞彙。
- 所有頂層 `SKILL.md` 新增 `metadata.task_type`，並以 `open-ended`、`outcome-gradable` 為強制詞彙。
- 為兩個 metadata 欄位新增 lint script 與單元測試，並接到 GitHub Actions spec consistency workflow。
- 新增 `shared/ground_truth_isolation_pattern.md`，並在 `shared/handoff_schemas.md` 中補上對新詞彙的說明入口。

### v3.3.1 (2026-04-14) — 規格一致性修補

- 同步 README、`.claude/CLAUDE.md`、`MODE_REGISTRY.md` 與各 `SKILL.md` 的 mode 數量與公開版本標示。
- 修正跨模型敘述：目前已實作的是誠信抽樣查核與獨立 DA critique；同儕審查第六位 reviewer 仍在規劃中。
- 釐清 adaptive checkpoint 語意：SLIM checkpoint 仍然必須等待使用者明確確認。
- 再次明確化 Stage 2.5 與 Stage 4.5 誠信關卡不可跳過。
- 新增輕量 spec consistency 檢查與 GitHub Actions workflow，避免後續再發生文件漂移。

### v3.3 (2026-04-09) — PaperOrchestra 啟發的強化

整合 [PaperOrchestra](https://arxiv.org/abs/2604.05018)（Song, Song, Pfister & Yoon, 2026, Google）的技術。

- **Semantic Scholar API 驗證** — Tier 0 程式化引用存在性查核。Levenshtein >= 0.70 標題比對、DOI 不符偵測、S2 ID 去重。API 不可用時優雅降級。
- **反洩漏協議** — 知識隔離指令優先使用 session 內材料，缺少的內容標記 `[MATERIAL GAP]` 而非用 LLM 記憶填補。降低 Mode 5/6 失敗風險。
- **VLM 圖表驗證**（可選）— 用視覺模型閉環檢查生成圖表。10 項檢核清單，最多 2 輪修正。
- **分數軌跡協議** — 跨修訂輪次的逐維度評分差異追蹤（7 個維度）。偵測退步（delta < -3）觸發強制 checkpoint。
- **Stage 2 並行化** — 視覺化與論證建構可在大綱完成後並行執行。
- 新版本：deep-research v2.8、academic-paper v3.0、academic-pipeline v3.2

### v3.2 (2026-04-09) — Lu 2026 Nature 整合

整合 Lu 等人（2026，*Nature* 651:914-919）的研究洞見——第一個通過盲審的端到端全自動 AI 研究系統。

- **7 類 AI 研究失敗模式檢查清單** — 在 Stage 2.5/4.5 阻斷管線：偵測實作錯誤、幻覺實驗結果、取巧特徵依賴、錯誤包裝為發現、方法偽造、框架鎖定。擴充現有 5 類引用幻覺分類。
- **Reviewer 校準模式**（academic-paper-reviewer v1.8）— opt-in 的 FNR/FPR/balanced accuracy 測量，使用者提供 gold set。5 次集成、跨模型預設開啟、session 內強制附加信心揭露。
- **揭露模式**（academic-paper v2.9）— 針對特定期刊/會議的 AI 使用聲明生成器。v1 涵蓋 ICLR、NeurIPS、Nature、Science、ACL、EMNLP。
- **提前停止機制**（academic-pipeline v3.1）— 收斂檢查 + pipeline 開始時的 token 預算透明化。
- **忠實度-原創性模式光譜** — 按 Lu 2026 Fig 1c 分類所有 3 個 skill 的模式。
- 新版本：academic-paper v2.9、academic-paper-reviewer v1.8、academic-pipeline v3.1

### v3.1.1 (2026-04-09) — 資訊系統 Senior Scholars' Basket of 11

外部貢獻：[@mchesbro1](https://github.com/mchesbro1) 最初提出並撰寫了 IS Basket of 8 期刊清單（[Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)）；[@cloudenochcsis](https://github.com/cloudenochcsis) 將其擴充為完整的 Senior Scholars' Basket of 11（[Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7)、[PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)）。更新 `academic-paper-reviewer/references/top_journals_by_field.md` 第 7 節，補上 *Decision Support Systems*、*Information & Management*、*Information and Organization*。資料來源：[AIS Senior Scholars' List of Premier Journals](https://aisnet.org/page/SeniorScholarListofPremierJournals)。

### v3.1 (2026-04-06) — 抗 Context Rot + 認知框架 + 精簡尺寸

靈感來自 [aspi6246/Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics)。

**Wave 1：抗 Context Rot 錨定**
- 4 個 skill 共 29 條 Anti-Patterns（每個 7-8 條，表格含「為何失敗」+「正確行為」）
- 22 個 IRON RULE 標記，確保長對話中關鍵規則不被遺忘
- 審查者唯讀約束（reviewer 不可修改論文原稿）

**Wave 2：追溯性 + 認知框架 + 中途強化**
- R&R 追溯矩陣（Schema 11）：Re-Review 新增「作者聲稱」+「已驗證？」欄位，獨立核實修訂宣稱
- 3 個認知框架 reference 檔案，教 agent「如何思考」而非只是「做什麼」：
  - 論證與推理框架（Toulmin 模型、Bradford Hill 因果推理、最佳解釋推論、認知狀態分類）
  - 審查品質思維框架（三鏡頭法、常見審查陷阱、校準問題）
  - 寫作判斷力框架（清晰度測試、讀者旅程、學科語態、修訂決策矩陣）
- 中途強化機制：每次 stage 轉換注入對應 IRON RULE + Anti-Pattern 提醒
- FULL checkpoint 前的 5 題自我檢查（引用完整性、諂媚讓步、品質軌跡、範圍紀律、完整性）

**Wave 3：精簡 Skill 尺寸**
- SKILL.md 總大小從 142KB 降至 85KB（-40%），詳細協議移至 `references/` 按需載入
- 新增 ~15 個 reference 檔案（re-review protocol、guided mode、systematic review、process summary 等）
- 所有 IRON RULE 保留在 SKILL.md；詳細內容按需載入
- 新版本：deep-research v2.7、academic-paper v2.8、academic-paper-reviewer v1.7、academic-pipeline v3.0

### v3.0 (2026-04-03) — 反諂媚 + 意圖偵測 + 跨模型驗證 + AI 自我反思
- **魔鬼代言人讓步門檻**（deep-research + academic-paper-reviewer）：反駁必須評分 1-5。≥4 才允許讓步。不允許連續讓步。讓步率追蹤。框架鎖定偵測。
- **攻擊強度保持**（academic-paper-reviewer）：DA 不因被反駁而軟化。反駁評估協議含偏移偵測。
- **意圖偵測層**（deep-research socratic）：偵測探索型 vs. 目標型。探索模式停用自動收束，最大輪數提升至 60。每 5 輪重新評估。
- **對話健康度指標**（deep-research socratic）：每 5 輪靜默自檢，偵測持續同意、迴避衝突、過早收束。偵測到模式時自動注入挑戰性問題。
- **跨模型驗證協議**（shared，可選）：用 GPT-5.4 Pro 或 Gemini 3.1 Pro 做誠信驗證 30% 抽樣跨模型檢查與獨立 DA critique。同儕審查第六位 reviewer 仍在規劃中，尚未實作。設定 `ARS_CROSS_MODEL` 環境變數啟用——未設定時零開銷。完整設定指南見 `shared/cross_model_verification.md`。
- **AI 自我反思報告**（academic-pipeline Stage 6）：Pipeline 結束後 AI 行為自評——DA 讓步率、健康警報、諂媚風險評級（LOW/MEDIUM/HIGH）、框架鎖定事件。
- 來源：四輪辯證實驗中發現 DA 讓步太快、蘇格拉底模式過早收束、整個辯論鎖定在人類設定的框架中。
- 版本：deep-research v2.5、academic-paper-reviewer v1.5、academic-pipeline v2.8

### v2.9.1 (2026-04-03) — Skill Metadata
- 為 4 個 SKILL.md 加入 `status: active` 和 `related_skills` 交叉引用
- 支援 skill 探索工具及跨技能導航

### v2.9 (2026-03-27) — 風格校準 + 寫作品質檢查
- **風格校準**（academic-paper intake Step 10，可選）：提供 3+ 篇過去論文，pipeline 會學習你的寫作風格 — 句子節奏、詞彙偏好、引用整合方式。寫作時作為軟性指引；學科規範永遠優先。優先級系統：學科規範（硬性）> 期刊慣例（強）> 個人風格（軟性）。見 `shared/style_calibration_protocol.md`
- **寫作品質檢查**（`academic-paper/references/writing_quality_check.md`）：寫作品質 checklist，於初稿自我審查時套用。5 大類：AI 高頻詞彙警告（25 個詞）、標點模式控制（em dash ≤3）、開頭廢話偵測、結構模式警告（三項列舉強迫症、均勻段落、同義詞循環）、句子長度變化檢查。這是好寫作規則 — 不是逃避偵測
- **Style Profile** 透過 academic-pipeline Material Passport 攜帶（`shared/handoff_schemas.md` Schema 10）
- **deep-research** report compiler 也可選地消費這兩個功能
- 版本：academic-paper v2.5、deep-research v2.4、academic-pipeline v2.7

### v2.8 (2026-03-22) — SCR Loop Phase 1：State-Challenge-Reflect 反思機制
- **Socratic Mentor Agent**（deep-research + academic-paper）：整合 SCR（表態-挑戰-反思）協議
  - **Commitment Gate**：在每個層級/章節轉換前收集使用者預測，再呈現資料
  - **Certainty-Triggered Contradiction**：偵測高信心語句（「顯然」「毫無疑問」），自動引入反面觀點
  - **Adaptive Intensity**：追蹤 commitment 準確率，動態調整挑戰頻率
  - **Self-Calibration Signal (S5)**：新收斂訊號，追蹤使用者在對話中是否展現自我校準能力
  - **SCR Switch**：使用者可隨時說「跳過預測」關閉 SCR，或「恢復預測」重新開啟，蘇格拉底式提問不受影響
- `deep-research/references/socratic_questioning_framework.md`：新增 SCR Overlay Protocol，對映 SCR 三階段到蘇格拉底功能
- 新增 `CHANGELOG.md`

### v2.7 (2026-03-09) — 誠信驗證 v2.0：反幻覺全面改版
- **integrity_verification_agent v2.0**：Anti-Hallucination Mandate（禁止靠 AI 記憶驗證）、消除灰色地帶分類（僅 VERIFIED/NOT_FOUND/MISMATCH）、強制 WebSearch audit trail、Stage 4.5 獨立全面驗證、Gray-Zone Prevention Rule
- **已知引用幻覺 Pattern**：5 類分類法（TF/PAC/IH/PH/SH，來自 GPTZero × NeurIPS 2025 研究）、5 種複合欺騙模式、實戰案例、文獻統計
- **出版後稽核**：對全部 68 篇引用做 WebSearch 逐一驗證，發現 21 篇有問題（31% 錯誤率），證明外部查證的必要性
- **論文修正**：移除 4 篇捏造引用、修正 6 篇作者錯誤、修正 7 篇書目細節、修正 2 篇格式問題

### v2.6.2 (2026-03-09) — 意圖匹配模式啟動
- **deep-research**：蘇格拉底模式改為**意圖匹配**啟動，取代關鍵字比對。支援任何語言 — 偵測含義（如「使用者想要引導式思考」）而非比對特定字串。
- **academic-paper**：Plan 模式改為**意圖匹配**啟動。偵測意圖信號如「使用者不確定如何開始」「使用者想要逐步引導」，不限語言。
- 兩個模式新增**預設規則**：當意圖模糊時，偏好 `socratic`/`plan` 而非 `full` — 先引導比較安全。
- 雙層架構：Layer 1（skill 啟動）用雙語關鍵字提高匹配信心；Layer 2（mode 路由）用語言無關的意圖信號。

### v2.6.1 (2026-03-09) — 雙語觸發關鍵字
- **deep-research**：新增繁體中文觸發關鍵字，涵蓋一般啟動和蘇格拉底模式。
- **academic-paper**：新增繁體中文觸發關鍵字及 Plan Mode 觸發區塊。
- 兩份 mode selection guide 加入雙語範例及中文專屬誤選情境。

### v2.6 / v2.4 / v1.4 (2026-03-08) — 15+ 項改進
- **deep-research v2.3**：新增系統性文獻回顧 / PRISMA 模式（第 7 模式）；3 個新 agent（risk_of_bias、meta_analysis、monitoring）；PRISMA 協議/報告模板；蘇格拉底收斂準則（4 訊號 + 自動結束）；快速模式選擇指南
- **academic-paper v2.4**：2 個新 agent（visualization、revision_coach）；修訂追蹤模板含 4 種狀態；引用格式轉換（APA↔Chicago↔MLA↔IEEE↔Vancouver）；統計視覺化標準；蘇格拉底收斂準則；修訂復原範例；**LaTeX 輸出強化** — 強制 `apa7` document class、`ragged2e` + `etoolbox` 文字對齊修正、表格欄寬公式、雙語摘要置中、標準字體集（Times New Roman + 思源宋體 VF + Courier New）、僅 tectonic 編譯 PDF
- **academic-paper-reviewer v1.4**：0-100 品質量表含行為指標；決策對照（≥80 接受、65-79 小修、50-64 大修、<50 退稿）；快速模式選擇指南
- **academic-pipeline v2.6**：自適應 checkpoint（FULL/SLIM/MANDATORY）；Phase E 宣稱驗證；素材護照（Material Passport）支援中途進入；跨 skill 模式顧問（14 情境）；團隊協作協議；強化銜接 schema（9 個含驗證規則）；誠信審查失敗復原範例

### v2.4 / v1.3 (2026-03-08)
- **academic-pipeline v2.4**：新增 Stage 6 過程紀錄 — 自動生成結構化論文創建過程紀錄（MD → LaTeX → PDF，中英雙語）；必含最後一章：**協作品質評估**，6 個維度各計 1–100 分（方向設定、智識貢獻、品質把關、迭代紀律、委派效率、後設學習），含誠實回饋與改進建議；pipeline 從 9 階段擴展為 10 階段

### v2.3 / v1.3 (2026-03-08)
- **academic-pipeline v2.3**：Stage 5 定稿階段現在會先詢問格式風格（APA 7.0 / Chicago / IEEE）；PDF 必須從 LaTeX 經 `tectonic` 編譯（禁止 HTML-to-PDF）；APA 7.0 使用 `apa7` document class（`man` 模式）+ XeCJK 支援中英雙語；字體：Times New Roman + 思源宋體 VF + Courier New

### v2.2 / v1.3 (2025-03-05)
- **跨 Agent 品質對齊**：統一定義（同儕審查、時效規則、CRITICAL 嚴重度、來源分級）橫跨所有 agent
- **deep-research v2.2**：synthesis 反模式、蘇格拉底自動結束條件、DOI+WebSearch 驗證、強化倫理誠信審查、模式轉換矩陣
- **academic-paper v2.2**：4 級論證強度評分、抄襲篩查、2 個新失敗路徑（F11 退稿復活、F12 研討會轉期刊）、Plan→Full 模式轉換
- **academic-paper-reviewer v1.3**：DA vs R3 角色邊界、CRITICAL 判定標準、共識分類（4/3/SPLIT/DA-CRITICAL）、信心分數加權、亞洲與區域期刊參考
- **academic-pipeline v2.2**：checkpoint 確認語意、模式切換矩陣、技能失敗降級策略、狀態所有權協議、素材版本控制

### v2.0.1 (2026-03)
- **精簡 4 個 SKILL.md**（-371 行, -16.5%）：移除跨 skill 重複、內嵌模板改為檔案引用、冗餘路由表、重複模式選擇區塊
- 修復 academic-paper 與 academic-pipeline 之間修訂迴圈上限的矛盾

### v2.0 (2026-02)
- **academic-pipeline v2.0**：5→9 階段、強制誠信驗證、兩階段審查、蘇格拉底修訂指導、可重現性保證
- **academic-paper-reviewer v1.1**：+魔鬼代言人審查者（第 7 agent）、+re-review 模式（驗收）、+審後蘇格拉底指導
- 新增 agent：`integrity_verification_agent` — 100% 引用/數據驗證，含稽核軌跡
- 新增 agent：`devils_advocate_reviewer_agent` — 8 維度論點挑戰
- 輸出順序：MD → Pandoc 可用時產出 DOCX（否則提供說明）→ 詢問 LaTeX → 確認 → PDF

### v1.0 (2026-02)
- 初版發布
- deep-research v2.0（10 agents、6 模式含 socratic）
- academic-paper v2.0（10 agents、8 模式含 plan）
- academic-paper-reviewer v1.0（6 agents、4 模式含 guided）
- academic-pipeline v1.0（調度器）
