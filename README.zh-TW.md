# Academic Research Skills for Claude Code

[![Version](https://img.shields.io/badge/version-v4.1.0-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v4.1.0)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[English](README.md)

一套完整的學術研究 Claude Code 技能包，涵蓋從研究到論文出版的全流程。

---

## 功能特色

- **Deep Research** — 13 個 Agent 組成的研究團隊，支援蘇格拉底引導 + 系統性文獻回顧 / PRISMA
- **Academic Paper** — 12 個 Agent 的論文撰寫團隊，含 LaTeX 輸出強化、視覺化、修訂教練、引用格式轉換
- **Academic Paper Reviewer** — 多視角同儕審查，0-100 品質量表（主編 + 3 位動態審查者 + 魔鬼代言人）
- **Academic Pipeline** — 10 階段全流程調度器，含自適應 checkpoint、宣稱驗證、素材護照

### 完整 Pipeline

```
研究 → 撰寫 → 誠信審查 → 審稿（5人）→ 蘇格拉底指導
  → 修訂 → 再審 → 再修訂 → 最終誠信審查 → 定稿
```

**核心特點：**
1. 自適應 checkpoint（FULL / SLIM / MANDATORY）
2. 審稿前誠信驗證 — 100% 引用、數據、宣稱驗證（Phase A-E）
3. 兩階段審查，含魔鬼代言人 + 0-100 品質量表
4. 審稿與修訂之間的蘇格拉底修訂指導
5. 出版前最終誠信驗證
6. 輸出格式：MD + DOCX + LaTeX（APA 7.0 `apa7` class / IEEE / Chicago）→ tectonic 編譯 PDF
7. Pipeline 完成後自動產出協作品質評估（6 維度 1-100 分）
8. 素材護照（Material Passport）支援中途進入流程的來源追蹤
9. 跨 skill 模式顧問（14 種情境 + 使用者典型）

---

## 實際產出展示

查看完整 10 階段 pipeline 的實際產出 — 包含**同儕審查報告、誠信驗證報告、完稿論文**：

**[瀏覽所有 pipeline 產出 →](examples/showcase/)**

| 產出物 | 說明 |
|--------|------|
| [完稿論文（英文）](examples/showcase/full_paper_apa7.pdf) | APA 7.0 格式，LaTeX 編譯 |
| [完稿論文（中文）](examples/showcase/full_paper_zh_apa7.pdf) | 中文版，APA 7.0 |
| [誠信報告 — 審稿前](examples/showcase/integrity_report_stage2.5.pdf) | Stage 2.5：抓出 15 個虛構引用 + 3 個統計錯誤 |
| [誠信報告 — 最終](examples/showcase/integrity_report_stage4.5.pdf) | Stage 4.5：確認零回歸 |
| [同儕審查第一輪](examples/showcase/stage3_review_report.pdf) | 主編 + 3 審查者 + 魔鬼代言人 |
| [複審](examples/showcase/stage3prime_rereview_report.pdf) | 修訂後驗證審查 |
| [同儕審查第二輪](examples/showcase/stage3_review_report_r2.pdf) | 追蹤審查 |
| [回覆審查意見](examples/showcase/response_to_reviewers_r2.pdf) | 逐點回覆 |
| [出版後稽核報告](examples/showcase/post_publication_audit_2026-03-09.md) | 獨立全引用稽核：發現 21/68 篇問題，通過了 3 輪誠信審查仍漏網 |

---

## 效能說明

> **建議模型：Claude Opus 4.6**，搭配 **Max plan**（或同等的延伸思考設定）。
>
> 完整學術 pipeline（10 階段）會消耗**大量 token** — 單次完整執行可能超過 200K 輸入 + 100K 輸出 token，視論文長度和修訂輪數而定。請依預算斟酌使用。
>
> 單獨使用個別 skill（如只用 `deep-research` 或 `academic-paper-reviewer`）的消耗明顯較少。

### 建議設定

為獲得最佳使用體驗，建議啟用以下 Claude Code 功能：

| 設定 | 功能說明 | 啟用方式 | 官方文件 |
|------|---------|---------|---------|
| **Agent Team** | 產生子代理（subagent）平行執行研究、撰寫、審查 — 多 Agent pipeline 的核心機制 | 設定 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`（研究預覽） | [Agent Teams](https://code.claude.com/docs/en/agent-teams) |
| **Ralph Loop** | 在長時間 pipeline 階段保持 session 持續運作，讓 Claude 能自主執行而不會逾時中斷 | 使用 `/ralph-loop` 啟動 | [Ralph Loop](https://claude.com/plugins/ralph-loop) |
| **Skip Permissions** | 跳過每次工具使用的確認提示，實現全 pipeline 不中斷的自主執行 | 啟動時加上 `claude --dangerously-skip-permissions` | [Permissions](https://docs.anthropic.com/en/docs/claude-code/cli-reference) · [Advanced Usage](https://docs.anthropic.com/en/docs/claude-code/advanced) |

> **⚠️ Skip Permissions 注意事項**：此旗標會停用所有工具使用的確認對話框。請自行斟酌使用 — 在可信任的長時間 pipeline 中非常方便，但會移除手動審核的安全機制。僅在你確定接受 Claude 自動執行檔案讀寫、shell 指令等操作時才啟用。

---

## 前置需求

### 安裝 Claude Code

**建議：原生安裝程式**（不需要 Node.js，自動更新）：

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash

# Windows（PowerShell）
irm https://claude.ai/install.ps1 | iex
```

<details>
<summary>替代方案：npm 安裝（已棄用）</summary>

需要 Node.js 18+。

```bash
npm install -g @anthropic-ai/claude-code
```

</details>

### 設定 API Key

你需要一個 Anthropic API key，請至 https://console.anthropic.com/ 取得。

```bash
# Claude Code 首次執行時會提示輸入 API key
claude
```

或設定環境變數：

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

---

## 安裝方式

### 方法一：作為專案 Skills（推薦）

將此 repo clone 到專案的 `.claude/skills/` 目錄：

```bash
# 切換到你的專案根目錄
cd /path/to/your/project

# 建立 skills 目錄（若不存在）
mkdir -p .claude/skills

# Clone skills
git clone https://github.com/Imbad0202/academic-research-skills.git .claude/skills/academic-research-skills
```

接著將 `.claude/CLAUDE.md` 的內容複製到你專案的 `.claude/CLAUDE.md`（若已有則合併）。

> **全域安裝：** 若希望所有專案都能使用這些 skills，可安裝到 `~/.claude/skills/`：
> ```bash
> mkdir -p ~/.claude/skills
> git clone https://github.com/Imbad0202/academic-research-skills.git ~/.claude/skills/academic-research-skills
> ```

### 方法二：作為獨立專案

```bash
# Clone repo
git clone https://github.com/Imbad0202/academic-research-skills.git

# 進入專案
cd academic-research-skills

# 啟動 Claude Code
claude
```

<details>
<summary><strong>沒有安裝 Git？</strong>直接下載 ZIP</summary>

1. 前往 https://github.com/Imbad0202/academic-research-skills
2. 點擊綠色 **Code** 按鈕 → **Download ZIP**
3. 解壓縮到你想要的位置
4. 方法一：將解壓後的資料夾移動到你專案內的 `.claude/skills/academic-research-skills`
5. 獨立使用：在解壓後的資料夾中開啟終端機，執行 `claude`

</details>

### 方法三：Claude Cowork（桌面版）

在 [Claude Cowork](https://claude.com/product/cowork) 中使用這些 skills — Claude Desktop 的 AI 自主工作區。

**選項 A：資料夾存取（最快）**

1. 將此 repo clone 到本機：
   ```bash
   git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
   ```
2. 開啟 Claude Desktop → 點擊上方 **Cowork** 分頁
3. 選擇 clone 下來的 `academic-research-skills` 資料夾作為工作目錄
4. Claude 會自動從 `SKILL.md` 偵測並載入 skills

**選項 B：作為專案 Skills**

若你已有 Cowork 專案資料夾：
```bash
cd /path/to/your/project
mkdir -p .claude/skills
git clone https://github.com/Imbad0202/academic-research-skills.git .claude/skills/academic-research-skills
```

Skills 會在對話相關時自動載入 — 例如說「幫我寫論文」會觸發 `academic-paper`。

**需求：**
- Claude Desktop（最新版本）且已啟用 Cowork
- 付費方案（Pro、Max、Team 或 Enterprise）

### 方法四：上傳至 claude.ai

claude.ai 的 Project 功能可以載入這些 skills，不需要安裝 Claude Code。

**步驟：**

1. 從這個 repo 下載所有 `SKILL.md` 檔案（共 4 個）：
   - `deep-research/SKILL.md`
   - `academic-paper/SKILL.md`
   - `academic-paper-reviewer/SKILL.md`
   - `academic-pipeline/SKILL.md`

2. 登入 [claude.ai](https://claude.ai)

3. 建立新 Project：
   - 點擊左側欄 **Projects** → **Create Project**
   - 命名為「Academic Research」（或任意名稱）

4. 上傳 SKILL.md 檔案：
   - 進入 Project → 點擊 **Project Knowledge**（右側面板）
   - 點擊 **Add Content** → **Upload Files**
   - 上傳 4 個 `SKILL.md` 檔案

5. （選用）上傳 reference 和 template 檔案以獲得更好效果：
   - `deep-research/references/` 下的檔案（APA 指南、方法論模板等）
   - `academic-paper/references/` 下的檔案（引用格式、寫作風格等）
   - `academic-paper/templates/` 下的檔案（論文結構模板）

6. 開始對話：在 Project 中開啟新對話，直接說「引導我研究 X」或「幫我寫論文」

**claude.ai 限制：**
- Project Knowledge 檔案大小上限為每個檔案 200KB
- SKILL.md 的 YAML frontmatter 中 `version` 和 `last_updated` 必須在 `metadata:` 下，否則上傳會失敗
- claude.ai 不支援多 agent 平行執行，效果不如 Claude Code 完整
- 建議至少上傳 4 個 SKILL.md + 核心 references，以獲得最佳效果

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
"幫我做 X 的系統性文獻回顧，含 PRISMA"        → systematic-review mode（新增）
"引導我研究 X"                                → socratic mode（蘇格拉底引導）
"幫我查核這些說法"                            → fact-check mode（事實查核）
"幫我做文獻回顧"                              → lit-review mode（文獻回顧）
"審查這篇論文的研究品質"                      → review mode（論文審查）
```

#### Academic Paper（學術論文撰寫，9 種模式）
```
"幫我寫一篇論文"                              → full mode（完整撰寫）
"引導我寫論文"                                → plan mode（引導規劃）
"我有初稿，這是審稿意見"                      → revision mode（修訂）
"幫我整理這些審稿意見成修訂路線圖"            → revision-coach mode（新增）
"轉換成 LaTeX" / "引用格式轉 IEEE"            → format-convert mode（格式轉換）
"檢查引用格式"                                → citation-check mode（引用檢查）
"寫一份中英雙語摘要"                          → bilingual-abstract mode（雙語摘要）
"潤飾我的寫作風格"                            → writing-polish mode（寫作潤飾）
"自動完成整篇論文"                            → full-auto mode（全自動撰寫）
```

#### Academic Paper Reviewer（論文審查，5 種模式）
```
"審查這篇論文"                                → full mode（主編 + R1/R2/R3 + 魔鬼代言人）
"快速評估這篇論文"                            → quick mode（快速評估）
"引導我改進這篇論文"                          → guided mode（引導改進）
"檢查研究方法"                                → methodology-focus mode（方法論聚焦）
"驗收修訂"                                    → re-review mode（再審驗收）
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

### Deep Research (v2.3)

13 個 Agent 的嚴謹學術研究 pipeline：

| Agent | 角色 |
|-------|------|
| Research Question Agent | FINER 評分的研究問題制定 |
| Research Architect | 研究方法設計 |
| Bibliography Agent | 系統性文獻搜尋 |
| Source Verification Agent | 證據分級、掠奪性期刊偵測 |
| Synthesis Agent | 跨來源整合 |
| Report Compiler | APA 7.0 報告撰寫 |
| Editor-in-Chief | Q1 期刊主編審查 |
| Devil's Advocate | 假設挑戰（3 個檢查點） |
| Ethics Review Agent | AI 揭露、引用誠信 |
| Socratic Mentor | 蘇格拉底引導式研究對話，含收斂準則 |
| Risk of Bias Agent | RoB 2 + ROBINS-I 偏誤風險評估 |
| Meta-Analysis Agent | 效果量、異質性、森林圖、GRADE |
| Monitoring Agent | Pipeline 完成後的文獻監測警報 |

**模式：** full、quick、paper-review、lit-review、fact-check、socratic、**systematic-review**（新增）

### Academic Paper (v2.4)

12 個 Agent 的學術論文撰寫 pipeline：

| Agent | 角色 |
|-------|------|
| Intake Agent | 組態訪談 + 上游銜接偵測 |
| Literature Strategist | 搜尋策略 + 注釋書目 |
| Structure Architect | 論文大綱 + 字數分配 |
| Argument Builder | 論點 + 主張-證據鏈 |
| Draft Writer | 逐章撰寫 |
| Citation Compliance | 多格式引用審核 + APA↔Chicago↔MLA↔IEEE↔Vancouver 轉換 |
| Abstract Bilingual | 中英雙語摘要 |
| Peer Reviewer | 5 維度審查（最多 2 輪） |
| Formatter | LaTeX/DOCX/PDF 輸出 — 強制 `apa7` class、XeCJK 雙語、`ragged2e` 對齊修正、tectonic 編譯 |
| Socratic Mentor | 逐章引導規劃，含收斂準則 |
| Visualization Agent | 9 種圖表類型、matplotlib/ggplot2、APA 7.0 標準 |
| Revision Coach Agent | 解析非結構化審稿意見 → 修訂路線圖 |

**模式：** full、plan、revision、citation-check、format-convert、bilingual-abstract、writing-polish、full-auto、**revision-coach**（新增）

### Academic Paper Reviewer (v1.4)

7 個 Agent 的多視角審查，搭配 **0-100 品質量表**：

| Agent | 角色 |
|-------|------|
| Field Analyst | 辨識領域、配置審查者 persona |
| Editor-in-Chief | 期刊適配性、新穎性、重要性 |
| Methodology Reviewer | 研究設計、統計、可重現性 |
| Domain Reviewer | 文獻涵蓋率、理論框架 |
| Perspective Reviewer | 跨領域觀點、實務影響 |
| Devil's Advocate Reviewer | 核心論點挑戰、邏輯謬誤偵測、最強反論 |
| Editorial Synthesizer | 共識分析、修訂路線圖、**量表評分** |

**模式：** full、re-review（驗收）、quick、methodology-focus、guided

**決策對照：** ≥80 接受、65-79 小修、50-64 大修、<50 退稿

### Academic Pipeline (v2.6)

10 階段調度器，含誠信驗證、兩階段審查、蘇格拉底指導、協作品質評估：

| 階段 | Skill | 目的 |
|------|-------|------|
| 1. 研究 | deep-research | 釐清研究問題、搜尋文獻 |
| 2. 撰寫 | academic-paper | 撰寫論文初稿 |
| **2.5. 誠信審查** | **integrity_verification_agent** | **100% 引用與數據驗證（v2.0：反幻覺強制令）** |
| 3. 審稿 | academic-paper-reviewer | 5 人審查（主編 + R1/R2/R3 + 魔鬼代言人） |
| → | *蘇格拉底修訂指導* | *引導使用者理解審稿意見* |
| 4. 修訂 | academic-paper | 回應審稿意見 |
| 3'. 再審 | academic-paper-reviewer | 驗收修訂內容 |
| → | *蘇格拉底殘餘指導* | *引導處理剩餘問題（若為 Major）* |
| 4'. 再修訂 | academic-paper | 最終修訂（若需要） |
| **4.5. 最終誠信審查** | **integrity_verification_agent** | **100% 最終驗證（零問題要求）** |
| 5. 定稿 | academic-paper | 詢問格式風格 → MD + DOCX + LaTeX → tectonic → PDF |
| **6. 過程紀錄** | **pipeline** | **論文創建過程紀錄 + 協作品質評估（1–100 分）** |

**Pipeline 保證：**
- 每個階段都需使用者確認 checkpoint
- 誠信驗證（Stage 2.5 + 4.5）不可跳過
- 可重現 — 標準化流程，含完整稽核軌跡
- Pipeline 完成後自動產出協作品質評估，含 6 維度誠實評分

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

## 作者

**吳政宜** (Cheng-I Wu)

---

## 更新紀錄

### v4.1.0 (2026-03-22) — SCR Loop Phase 1：State-Challenge-Reflect 反思機制
- **Socratic Mentor Agent**（deep-research + academic-paper）：整合 SCR（表態-挑戰-反思）協議
  - **Commitment Gate**：在每個層級/章節轉換前收集使用者預測，再呈現資料
  - **Certainty-Triggered Contradiction**：偵測高信心語句（「顯然」「毫無疑問」），自動引入反面觀點
  - **Adaptive Intensity**：追蹤 commitment 準確率，動態調整挑戰頻率
  - **Self-Calibration Signal (S5)**：新收斂訊號，追蹤使用者在對話中是否展現自我校準能力
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
- 輸出順序：MD + DOCX → 詢問 LaTeX → 確認 → PDF

### v1.0 (2026-02)
- 初版發布
- deep-research v2.0（10 agents、6 模式含 socratic）
- academic-paper v2.0（10 agents、8 模式含 plan）
- academic-paper-reviewer v1.0（6 agents、4 模式含 guided）
- academic-pipeline v1.0（調度器）
